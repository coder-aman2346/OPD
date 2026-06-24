"""Memory service for conversation history management."""

import uuid
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Message, ConversationSummary
from app.config import get_settings
from app.utils.logger import logger, log_with_data
import logging


class MemoryService:
    """Manages conversation memory with summarization for long conversations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def get_or_create_conversation(
        self, conversation_id: str | None = None, patient_name: str | None = None
    ) -> Conversation:
        """Get an existing conversation or create a new one."""
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == uuid.UUID(conversation_id)
                )
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                # Update patient name if provided and not already set
                if patient_name and not conversation.patient_name:
                    conversation.patient_name = patient_name
                    await self.db.flush()
                return conversation

        # Create new conversation
        conversation = Conversation(
            patient_name=patient_name,
        )
        self.db.add(conversation)
        await self.db.flush()

        log_with_data(
            logger, logging.INFO,
            "New conversation created",
            conversation_id=str(conversation.id),
        )

        return conversation

    async def load_messages(self, conversation_id: uuid.UUID) -> list[dict]:
        """Load conversation messages as OpenAI-format dicts."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def save_message(
        self, conversation_id: uuid.UUID, role: str, content: str
    ) -> Message:
        """Save a message to the database."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def get_context_messages(self, conversation_id: uuid.UUID) -> list[dict]:
        """
        Get messages for LLM context.
        
        If a conversation summary exists, prepend it as a system message
        and only include recent messages.
        """
        messages = []

        # Check for existing summary
        result = await self.db.execute(
            select(ConversationSummary).where(
                ConversationSummary.conversation_id == conversation_id
            )
        )
        summary = result.scalar_one_or_none()

        if summary:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary:\n{summary.summary}",
            })

        # Load all messages
        all_messages = await self.load_messages(conversation_id)

        # If we have a summary, only include the most recent messages
        if summary and len(all_messages) > 10:
            messages.extend(all_messages[-10:])
        else:
            messages.extend(all_messages)

        return messages

    async def get_message_count(self, conversation_id: uuid.UUID) -> int:
        """Get the total number of messages in a conversation."""
        result = await self.db.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        return len(result.scalars().all())

    async def save_summary(self, conversation_id: uuid.UUID, summary_text: str):
        """Save or update the conversation summary."""
        result = await self.db.execute(
            select(ConversationSummary).where(
                ConversationSummary.conversation_id == conversation_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.summary = summary_text
            existing.updated_at = datetime.utcnow()
        else:
            summary = ConversationSummary(
                conversation_id=conversation_id,
                summary=summary_text,
            )
            self.db.add(summary)

        await self.db.flush()

        log_with_data(
            logger, logging.INFO,
            "Conversation summary saved",
            conversation_id=str(conversation_id),
        )

    async def should_summarize(self, conversation_id: uuid.UUID) -> bool:
        """Check if the conversation should be summarized."""
        count = await self.get_message_count(conversation_id)
        return count >= self.settings.max_messages_before_summary

    async def get_full_conversation_text(self, conversation_id: uuid.UUID) -> str:
        """Get full conversation as text for summarization."""
        messages = await self.load_messages(conversation_id)
        lines = []
        for msg in messages:
            role = msg["role"].capitalize()
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    async def compact_messages(self, conversation_id: uuid.UUID):
        """Delete older messages after summarization, keeping the most recent ones."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        all_messages = result.scalars().all()

        if len(all_messages) <= 10:
            return

        # Delete all but the last 10 messages
        messages_to_delete = all_messages[:-10]
        for msg in messages_to_delete:
            await self.db.delete(msg)

        await self.db.flush()

        log_with_data(
            logger, logging.INFO,
            "Compacted conversation messages",
            conversation_id=str(conversation_id),
            deleted_count=len(messages_to_delete),
        )
