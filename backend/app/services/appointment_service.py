"""Appointment service for CRUD operations."""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Appointment
from app.services.metrics_service import metrics_service
from app.utils.logger import logger, log_with_data
import logging


class AppointmentService:
    """Manages appointment creation and retrieval."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_appointment(
        self,
        patient_name: str,
        department: str,
        visit_date: date,
        summary: str,
        conversation_id: uuid.UUID | None = None,
    ) -> Appointment:
        """Create a new appointment."""
        appointment = Appointment(
            patient_name=patient_name,
            department=department,
            visit_date=visit_date,
            summary=summary,
            conversation_id=conversation_id,
        )
        self.db.add(appointment)
        await self.db.flush()

        # Track metrics
        metrics_service.record_appointment()

        log_with_data(
            logger, logging.INFO,
            "Appointment created",
            appointment_id=str(appointment.id),
            patient_name=patient_name,
            department=department,
            visit_date=str(visit_date),
        )

        return appointment

    async def list_appointments(
        self, conversation_id: uuid.UUID | None = None
    ) -> list[Appointment]:
        """List appointments, optionally filtered by conversation."""
        query = select(Appointment).order_by(Appointment.created_at.desc())

        if conversation_id:
            query = query.where(
                Appointment.conversation_id == conversation_id
            )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_appointment(self, appointment_id: uuid.UUID) -> Appointment | None:
        """Get a single appointment by ID."""
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()
