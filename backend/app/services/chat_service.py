"""Chat service — main orchestrator for conversation flow."""

import json
import uuid
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.appointment_service import AppointmentService
from app.services.guardrail_service import run_guardrails
from app.services.metrics_service import metrics_service
from app.prompts.summary_prompt import SUMMARY_PROMPT
from app.utils.logger import logger, log_with_data, conversation_id_var
import logging


class ChatService:
    """Orchestrates the conversation flow between user, LLM, and tools."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()
        self.memory = MemoryService(db)
        self.appointments = AppointmentService(db)

    async def process_message(
        self,
        message: str,
        conversation_id: str | None = None,
        patient_name: str | None = None,
    ) -> dict:
        """
        Process a user message through the full conversation pipeline.
        
        Args:
            message: The user's message text.
            conversation_id: Optional existing conversation ID.
            patient_name: Optional patient name.
            
        Returns:
            Dict with conversation_id, response, appointments_created, 
            pii_warning, and metrics.
        """
        # 1. Run guardrails on input
        guardrail_result = run_guardrails(message)

        if not guardrail_result.is_safe:
            # Return block message without calling LLM
            # Still create/get conversation for tracking
            conversation = await self.memory.get_or_create_conversation(
                conversation_id, patient_name
            )
            conversation_id_var.set(str(conversation.id))

            # Save the blocked message and response
            await self.memory.save_message(conversation.id, "user", message)
            await self.memory.save_message(
                conversation.id, "assistant", guardrail_result.block_message
            )

            log_with_data(
                logger, logging.WARNING,
                "Message blocked by guardrails",
                conversation_id=str(conversation.id),
                injection_detected=guardrail_result.injection_detected,
            )

            return {
                "conversation_id": str(conversation.id),
                "response": guardrail_result.block_message,
                "appointments_created": [],
                "pii_warning": None,
                "metrics": None,
            }

        # 2. Get or create conversation
        conversation = await self.memory.get_or_create_conversation(
            conversation_id, patient_name
        )
        conversation_id_var.set(str(conversation.id))

        log_with_data(
            logger, logging.INFO,
            "Processing message",
            conversation_id=str(conversation.id),
            message_length=len(message),
        )

        # 3. Save user message
        await self.memory.save_message(conversation.id, "user", message)

        # 4. Check if summarization is needed
        if await self.memory.should_summarize(conversation.id):
            await self._summarize_conversation(conversation.id)

        # 5. Load context messages
        context_messages = await self.memory.get_context_messages(conversation.id)

        # 6. Call LLM
        llm_result = await self.llm.chat_completion(context_messages)

        # 7. Handle tool calls (appointment booking)
        appointments_created = []
        assistant_content = llm_result["content"]

        if llm_result["tool_calls"]:
            appointments_created, assistant_content = await self._handle_tool_calls(
                conversation.id, context_messages, llm_result
            )

        # 8. Save assistant response
        if assistant_content:
            await self.memory.save_message(
                conversation.id, "assistant", assistant_content
            )

        # Update patient name on conversation if learned from the conversation
        if patient_name and not conversation.patient_name:
            conversation.patient_name = patient_name
            await self.db.flush()

        # 9. Build response
        metrics = llm_result.get("metrics")
        metrics_dict = None
        if metrics:
            metrics_dict = {
                "input_tokens": metrics.input_tokens,
                "output_tokens": metrics.output_tokens,
                "cached_tokens": metrics.cached_tokens,
                "total_tokens": metrics.total_tokens,
                "ttft_ms": metrics.ttft_ms,
                "latency_ms": metrics.latency_ms,
                "model": metrics.model,
            }

        return {
            "conversation_id": str(conversation.id),
            "response": assistant_content or "I'm sorry, I couldn't process that. Could you try again?",
            "appointments_created": appointments_created,
            "pii_warning": guardrail_result.warning_message,
            "metrics": metrics_dict,
        }

    async def _handle_tool_calls(
        self,
        conversation_id: uuid.UUID,
        context_messages: list[dict],
        llm_result: dict,
    ) -> tuple[list[dict], str]:
        """
        Handle tool calls from the LLM response.
        
        Returns:
            Tuple of (appointments_created, final_assistant_content)
        """
        appointments_created = []
        
        # Build the assistant message with tool calls for the continuation
        assistant_tool_message = {
            "role": "assistant",
            "content": llm_result["content"],
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"]),
                    },
                }
                for tc in llm_result["tool_calls"]
            ],
        }

        messages_for_continuation = context_messages + [assistant_tool_message]

        # Process each tool call
        for tool_call in llm_result["tool_calls"]:
            if tool_call["name"] == "book_appointment":
                args = tool_call["arguments"]

                try:
                    visit_date = date.fromisoformat(args["visit_date"])
                except (ValueError, KeyError):
                    visit_date = date.today()

                # Create the appointment
                appointment = await self.appointments.create_appointment(
                    patient_name=args["patient_name"],
                    department=args["department"],
                    visit_date=visit_date,
                    summary=args.get("summary", ""),
                    conversation_id=conversation_id,
                )

                appointment_data = {
                    "appointment_id": str(appointment.id),
                    "patient_name": appointment.patient_name,
                    "department": appointment.department,
                    "visit_date": str(appointment.visit_date),
                    "summary": appointment.summary,
                }
                appointments_created.append(appointment_data)

                # Add tool result for continuation
                tool_result = json.dumps({
                    "status": "success",
                    "appointment_id": str(appointment.id),
                    "message": f"Appointment booked successfully for {args['patient_name']} "
                               f"in {args['department']} on {args['visit_date']}.",
                })

                messages_for_continuation.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result,
                })

                log_with_data(
                    logger, logging.INFO,
                    "Appointment booked via tool call",
                    conversation_id=str(conversation_id),
                    department=args["department"],
                    appointment_id=str(appointment.id),
                )

        # Get final response after tool execution
        final_result = await self.llm.chat_completion(
            messages_for_continuation, include_tools=True
        )

        return appointments_created, final_result["content"]

    async def _summarize_conversation(self, conversation_id: uuid.UUID):
        """Generate and save a conversation summary, then compact messages."""
        try:
            conversation_text = await self.memory.get_full_conversation_text(
                conversation_id
            )
            prompt = SUMMARY_PROMPT.format(conversation=conversation_text)
            summary = await self.llm.generate_summary(prompt)

            await self.memory.save_summary(conversation_id, summary)
            await self.memory.compact_messages(conversation_id)

            log_with_data(
                logger, logging.INFO,
                "Conversation summarized and compacted",
                conversation_id=str(conversation_id),
            )
        except Exception as e:
            log_with_data(
                logger, logging.ERROR,
                "Failed to summarize conversation",
                conversation_id=str(conversation_id),
                error=str(e),
            )
