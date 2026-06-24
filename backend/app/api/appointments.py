"""Appointment API routes."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.api.schemas import (
    AppointmentCreateRequest,
    AppointmentCreateResponse,
    AppointmentResponse,
)
from app.services.appointment_service import AppointmentService

router = APIRouter(tags=["Appointments"])


@router.post("/appointments", response_model=AppointmentCreateResponse)
async def create_appointment(
    request: AppointmentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new appointment directly via API."""
    service = AppointmentService(db)
    appointment = await service.create_appointment(
        patient_name=request.patient_name,
        department=request.department,
        visit_date=request.visit_date,
        summary=request.summary,
    )

    return AppointmentCreateResponse(
        appointment_id=str(appointment.id),
    )


@router.get("/appointments", response_model=list[AppointmentResponse])
async def list_appointments(
    conversation_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all appointments, optionally filtered by conversation."""
    service = AppointmentService(db)

    conv_uuid = None
    if conversation_id:
        try:
            conv_uuid = uuid.UUID(conversation_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid conversation_id format")

    appointments = await service.list_appointments(conv_uuid)

    return [
        AppointmentResponse(
            appointment_id=str(apt.id),
            patient_name=apt.patient_name,
            department=apt.department,
            visit_date=str(apt.visit_date),
            summary=apt.summary,
        )
        for apt in appointments
    ]
