"""Guardrail service for input safety checks."""

import re
from dataclasses import dataclass

from app.utils.pii import detect_pii, PIIDetection
from app.utils.logger import logger, log_with_data
import logging


@dataclass
class GuardrailResult:
    """Result of guardrail checks."""
    is_safe: bool
    pii_detected: PIIDetection | None = None
    injection_detected: bool = False
    warning_message: str | None = None
    block_message: str | None = None


# Prompt injection patterns
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?above\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?system\s+prompt", re.IGNORECASE),
    re.compile(r"show\s+(me\s+)?(your\s+)?system\s+prompt", re.IGNORECASE),
    re.compile(r"what\s+(is|are)\s+your\s+(system\s+)?instructions", re.IGNORECASE),
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"DAN\s+mode", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+are\s+not\s+an?\s+AI", re.IGNORECASE),
    re.compile(r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions", re.IGNORECASE),
    re.compile(r"bypass\s+(your\s+)?(safety|content)\s+(filter|guidelines)", re.IGNORECASE),
    re.compile(r"override\s+(your\s+)?instructions", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(your\s+)?rules", re.IGNORECASE),
]


def check_prompt_injection(text: str) -> bool:
    """Check if the text contains prompt injection attempts."""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def run_guardrails(text: str) -> GuardrailResult:
    """
    Run all guardrail checks on input text.
    
    Returns:
        GuardrailResult with safety status, warnings, and block messages.
    """
    # 1. Check for prompt injection (blocks the message)
    if check_prompt_injection(text):
        log_with_data(
            logger, logging.WARNING,
            "Prompt injection detected",
            input_text=text[:100],
        )
        return GuardrailResult(
            is_safe=False,
            injection_detected=True,
            block_message=(
                "I'm sorry, but I can't process that request. "
                "I'm here to help you with healthcare-related questions "
                "and appointment booking. How can I assist you with your health concerns?"
            ),
        )

    # 2. Check for PII (warns but does not block)
    pii_result = detect_pii(text)
    warning_message = None

    if pii_result.has_pii:
        log_with_data(
            logger, logging.WARNING,
            "PII detected in user input",
            pii_types=pii_result.pii_types,
        )
        pii_type_str = ", ".join(pii_result.pii_types)
        warning_message = (
            f"⚠️ I noticed your message may contain personal information ({pii_type_str}). "
            f"For your privacy, please avoid sharing sensitive personal details like "
            f"email addresses, phone numbers, or social security numbers in this chat."
        )

    return GuardrailResult(
        is_safe=True,
        pii_detected=pii_result,
        warning_message=warning_message,
    )
