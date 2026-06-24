"""PII detection utilities using regex patterns."""

import re
from dataclasses import dataclass


@dataclass
class PIIDetection:
    """Result of PII detection scan."""
    has_pii: bool
    pii_types: list[str]
    details: list[str]


# Regex patterns for PII detection
EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
)

PHONE_PATTERN = re.compile(
    r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'
)

SSN_PATTERN = re.compile(
    r'\b\d{3}-\d{2}-\d{4}\b'
)


def detect_pii(text: str) -> PIIDetection:
    """
    Scan text for PII patterns (email, phone, SSN).
    
    Returns a PIIDetection object with results.
    """
    pii_types = []
    details = []

    # Check for emails
    emails = EMAIL_PATTERN.findall(text)
    if emails:
        pii_types.append("email")
        details.extend([f"Email detected: {e}" for e in emails])

    # Check for phone numbers
    phones = PHONE_PATTERN.findall(text)
    if phones:
        # Filter out short numbers that are likely not phone numbers (e.g., ages, doses)
        valid_phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10]
        if valid_phones:
            pii_types.append("phone")
            details.extend([f"Phone number detected: {p}" for p in valid_phones])

    # Check for SSN
    ssns = SSN_PATTERN.findall(text)
    if ssns:
        pii_types.append("ssn")
        details.extend([f"SSN detected: {s}" for s in ssns])

    return PIIDetection(
        has_pii=len(pii_types) > 0,
        pii_types=pii_types,
        details=details,
    )
