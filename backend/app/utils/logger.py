"""Structured JSON logger with request tracing support."""

import logging
import json
import sys
from datetime import datetime, timezone
from contextvars import ContextVar

# Context variables for request tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="no-request")
conversation_id_var: ContextVar[str] = ContextVar("conversation_id", default="no-conversation")


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get("no-request"),
            "conversation_id": conversation_id_var.get("no-conversation"),
        }

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logger(name: str = "healthcare") -> logging.Logger:
    """Create and configure a structured JSON logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger


def log_with_data(logger: logging.Logger, level: int, message: str, **kwargs):
    """Log a message with additional structured data."""
    record = logger.makeRecord(
        logger.name, level, "(unknown)", 0, message, (), None
    )
    record.extra_data = kwargs
    logger.handle(record)


# Default application logger
logger = setup_logger()
