"""Chat API route."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.utils.logger import logger, log_with_data, request_id_var
import logging
import uuid

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI Healthcare Assistant.
    
    The assistant will:
    - Collect symptoms and ask follow-up questions
    - Recommend a medical department
    - Book appointments when ready
    - Generate doctor-facing summaries
    """
    # Set request ID for tracing
    req_id = str(uuid.uuid4())[:8]
    request_id_var.set(req_id)

    log_with_data(
        logger, logging.INFO,
        "Chat request received",
        request_id=req_id,
        conversation_id=request.conversation_id,
        message_preview=request.message[:50],
    )

    chat_service = ChatService(db)
    result = await chat_service.process_message(
        message=request.message,
        conversation_id=request.conversation_id,
        patient_name=request.patient_name,
    )

    return ChatResponse(**result)
