"""LLM service wrapping OpenAI SDK with tool calling support."""

import json
import time
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionToolParam

from app.config import get_settings
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.metrics_service import RequestMetrics, metrics_service
from app.utils.logger import logger, log_with_data
import logging


# Tool definitions for OpenAI function calling
TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": (
                "Book a medical appointment for the patient. "
                "Use this when you have collected sufficient symptom information, "
                "the patient's name, and their preferred visit date."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {
                        "type": "string",
                        "description": "The full name of the patient.",
                    },
                    "department": {
                        "type": "string",
                        "description": "The recommended medical department.",
                        "enum": [
                            "ENT",
                            "Neurology",
                            "Orthopedics",
                            "Cardiology",
                            "Dermatology",
                            "General Medicine",
                        ],
                    },
                    "visit_date": {
                        "type": "string",
                        "description": "The preferred visit date in YYYY-MM-DD format.",
                    },
                    "summary": {
                        "type": "string",
                        "description": (
                            "A concise, doctor-facing clinical summary of the patient's "
                            "symptoms, duration, severity, and relevant details."
                        ),
                    },
                },
                "required": ["patient_name", "department", "visit_date", "summary"],
                "additionalProperties": False,
            },
        },
    }
]


class LLMService:
    """Manages interactions with the Gemini API."""

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.gemini_api_key or not self.settings.gemini_api_key.strip():
            raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY in your .env file.")
        self.client = AsyncOpenAI(
            api_key=self.settings.gemini_api_key,
            base_url=self.settings.gemini_api_base,
        )
        self.model = self.settings.gemini_model

    async def chat_completion(
        self,
        messages: list[dict],
        include_tools: bool = True,
    ) -> dict:
        """
        Send a chat completion request to Gemini.
        
        Args:
            messages: List of message dicts (role, content).
            include_tools: Whether to include tool definitions.
            
        Returns:
            Dict with response content, tool_calls, and metrics.
        """
        # Prepend system prompt
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages

        # Build request kwargs
        kwargs = {
            "model": self.model,
            "messages": full_messages,
            "temperature": self.settings.gemini_temperature,
            "max_tokens": self.settings.gemini_max_tokens,
        }

        if include_tools:
            kwargs["tools"] = TOOLS
            kwargs["tool_choice"] = "auto"

        # Track timing
        start_time = time.time()
        ttft = 0.0

        log_with_data(
            logger, logging.DEBUG,
            "Sending LLM request",
            model=self.model,
            message_count=len(full_messages),
        )

        try:
            response = await self.client.chat.completions.create(**kwargs)
            ttft = (time.time() - start_time) * 1000  # ms
            latency = ttft  # For non-streaming, TTFT ≈ latency

            # Extract response data
            choice = response.choices[0]
            message = choice.message

            # Extract usage metrics
            usage = response.usage
            request_metrics = RequestMetrics(
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                cached_tokens=getattr(usage, "prompt_tokens_details", {}).get("cached_tokens", 0) if usage and hasattr(usage, "prompt_tokens_details") and usage.prompt_tokens_details else 0,
                total_tokens=usage.total_tokens if usage else 0,
                ttft_ms=round(ttft, 2),
                latency_ms=round(latency, 2),
                model=response.model,
            )

            # Record metrics
            metrics_service.record_request(request_metrics)

            log_with_data(
                logger, logging.INFO,
                "LLM response received",
                model=response.model,
                input_tokens=request_metrics.input_tokens,
                output_tokens=request_metrics.output_tokens,
                latency_ms=request_metrics.latency_ms,
            )

            # Build result
            result = {
                "content": message.content,
                "tool_calls": [],
                "metrics": request_metrics,
                "finish_reason": choice.finish_reason,
            }

            # Process tool calls if present
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments),
                    })

            return result

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            log_with_data(
                logger, logging.ERROR,
                "LLM request failed",
                error=str(e),
                latency_ms=round(latency, 2),
            )
            raise

    async def generate_summary(self, prompt: str) -> str:
        """Generate a summary using the LLM (no tools)."""
        messages = [{"role": "user", "content": prompt}]
        result = await self.chat_completion(messages, include_tools=False)
        return result["content"] or ""

    async def continue_with_tool_result(
        self,
        messages: list[dict],
        tool_call_id: str,
        tool_result: str,
    ) -> dict:
        """
        Continue a conversation after a tool call with the tool's result.
        
        Args:
            messages: Full conversation messages including the assistant's tool call.
            tool_call_id: The ID of the tool call being responded to.
            tool_result: The result of the tool execution as a string.
            
        Returns:
            Dict with the assistant's follow-up response.
        """
        # Add the tool result message
        messages_with_result = messages + [
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result,
            }
        ]

        return await self.chat_completion(messages_with_result, include_tools=True)
