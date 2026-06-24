"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


# ── Chat Schemas ──────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    message: str = Field(..., min_length=1, max_length=5000, description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID to continue")
    patient_name: Optional[str] = Field(None, description="Patient's full name")


class MetricsResponse(BaseModel):
    """LLM metrics for a single request."""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    ttft_ms: float = 0.0
    latency_ms: float = 0.0
    model: str = ""


class AppointmentCreated(BaseModel):
    """Appointment data returned when created via chat."""
    appointment_id: str
    patient_name: str
    department: str
    visit_date: str
    summary: str


class ChatResponse(BaseModel):
    """Response body for the chat endpoint."""
    conversation_id: str
    response: str
    appointments_created: list[AppointmentCreated] = []
    pii_warning: Optional[str] = None
    metrics: Optional[MetricsResponse] = None


# ── Appointment Schemas ───────────────────────────────────────────────

class AppointmentCreateRequest(BaseModel):
    """Request body for creating an appointment directly."""
    patient_name: str = Field(..., min_length=1, max_length=255)
    department: str = Field(..., min_length=1, max_length=100)
    visit_date: date
    summary: str = Field("", max_length=5000)


class AppointmentResponse(BaseModel):
    """Response body for a single appointment."""
    appointment_id: str
    patient_name: str
    department: str
    visit_date: str
    summary: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentCreateResponse(BaseModel):
    """Response body after creating an appointment."""
    appointment_id: str


# ── Metrics Schemas ───────────────────────────────────────────────────

class AggregateMetricsResponse(BaseModel):
    """Response body for the metrics endpoint."""
    total_requests: int = 0
    total_appointments: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cached_tokens: int = 0
    total_tokens: int = 0
    avg_latency_ms: float = 0.0
    avg_ttft_ms: float = 0.0
    total_cost_usd: float = 0.0
