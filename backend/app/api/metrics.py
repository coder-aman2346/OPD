"""Metrics API route."""

from fastapi import APIRouter

from app.api.schemas import AggregateMetricsResponse
from app.services.metrics_service import metrics_service

router = APIRouter(tags=["Metrics"])


@router.get("/metrics", response_model=AggregateMetricsResponse)
async def get_metrics():
    """
    Get aggregated application metrics.
    
    Returns total requests, token usage, latency, appointment count,
    and estimated cost.
    """
    aggregate = metrics_service.get_aggregate()

    return AggregateMetricsResponse(
        total_requests=aggregate.total_requests,
        total_appointments=aggregate.total_appointments,
        total_input_tokens=aggregate.total_input_tokens,
        total_output_tokens=aggregate.total_output_tokens,
        total_cached_tokens=aggregate.total_cached_tokens,
        total_tokens=aggregate.total_tokens,
        avg_latency_ms=aggregate.avg_latency_ms,
        avg_ttft_ms=aggregate.avg_ttft_ms,
        total_cost_usd=aggregate.total_cost_usd,
    )
