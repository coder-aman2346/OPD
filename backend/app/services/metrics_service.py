"""Metrics service for tracking LLM usage and application metrics."""

import time
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RequestMetrics:
    """Metrics for a single LLM request."""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    ttft_ms: float = 0.0  # Time to first token
    latency_ms: float = 0.0  # Total request latency
    model: str = ""


@dataclass
class AggregateMetrics:
    """Aggregated application metrics."""
    total_requests: int = 0
    total_appointments: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cached_tokens: int = 0
    total_tokens: int = 0
    avg_latency_ms: float = 0.0
    avg_ttft_ms: float = 0.0
    total_cost_usd: float = 0.0


class MetricsService:
    """Singleton service for tracking application metrics."""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._requests: list[RequestMetrics] = []
        self._appointment_count: int = 0
        self._lock = Lock()

    def record_request(self, metrics: RequestMetrics):
        """Record metrics for a single LLM request."""
        with self._lock:
            self._requests.append(metrics)

    def record_appointment(self):
        """Increment appointment counter."""
        with self._lock:
            self._appointment_count += 1

    def get_aggregate(self) -> AggregateMetrics:
        """Get aggregated metrics across all requests."""
        with self._lock:
            if not self._requests:
                return AggregateMetrics(
                    total_appointments=self._appointment_count
                )

            total_input = sum(r.input_tokens for r in self._requests)
            total_output = sum(r.output_tokens for r in self._requests)
            total_cached = sum(r.cached_tokens for r in self._requests)
            total_tokens = sum(r.total_tokens for r in self._requests)
            avg_latency = sum(r.latency_ms for r in self._requests) / len(self._requests)
            avg_ttft = sum(r.ttft_ms for r in self._requests) / len(self._requests)

            # Cost estimation based on Gemini Flash pricing:
            # Input: $0.075 / 1M tokens, Output: $0.30 / 1M tokens
            cost = (total_input * 0.075 / 1_000_000) + (total_output * 0.30 / 1_000_000)

            return AggregateMetrics(
                total_requests=len(self._requests),
                total_appointments=self._appointment_count,
                total_input_tokens=total_input,
                total_output_tokens=total_output,
                total_cached_tokens=total_cached,
                total_tokens=total_tokens,
                avg_latency_ms=round(avg_latency, 2),
                avg_ttft_ms=round(avg_ttft, 2),
                total_cost_usd=round(cost, 6),
            )

    def get_last_request_metrics(self) -> RequestMetrics | None:
        """Get metrics for the most recent request."""
        with self._lock:
            return self._requests[-1] if self._requests else None

    def reset(self):
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._requests.clear()
            self._appointment_count = 0


# Global singleton instance
metrics_service = MetricsService()
