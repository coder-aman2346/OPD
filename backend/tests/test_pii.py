"""Tests for PII detection utilities."""

import pytest
from app.utils.pii import detect_pii


class TestPIIDetection:
    """Test suite for PII detection."""

    def test_detects_email(self):
        result = detect_pii("My email is john@example.com")
        assert result.has_pii is True
        assert "email" in result.pii_types

    def test_detects_multiple_emails(self):
        result = detect_pii("Contact me at john@example.com or jane@test.org")
        assert result.has_pii is True
        assert "email" in result.pii_types
        assert len([d for d in result.details if "Email" in d]) == 2

    def test_detects_phone_number(self):
        result = detect_pii("Call me at 1234567890")
        assert result.has_pii is True
        assert "phone" in result.pii_types

    def test_detects_phone_with_dashes(self):
        result = detect_pii("My number is 123-456-7890")
        assert result.has_pii is True
        assert "phone" in result.pii_types

    def test_detects_phone_with_country_code(self):
        result = detect_pii("Reach me at +1-234-567-8901")
        assert result.has_pii is True
        assert "phone" in result.pii_types

    def test_detects_ssn(self):
        result = detect_pii("My SSN is 123-45-6789")
        assert result.has_pii is True
        assert "ssn" in result.pii_types

    def test_no_pii_in_normal_text(self):
        result = detect_pii("I have a headache that started 3 days ago")
        assert result.has_pii is False
        assert len(result.pii_types) == 0

    def test_no_pii_in_medical_text(self):
        result = detect_pii("The pain is about 7 out of 10 severity")
        assert result.has_pii is False

    def test_detects_multiple_pii_types(self):
        result = detect_pii("Email me at john@test.com, my phone is 1234567890")
        assert result.has_pii is True
        assert "email" in result.pii_types
        assert "phone" in result.pii_types

    def test_empty_string(self):
        result = detect_pii("")
        assert result.has_pii is False
