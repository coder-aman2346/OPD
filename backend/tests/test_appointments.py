"""Tests for appointment API endpoints."""

import pytest
import pytest_asyncio


@pytest.mark.asyncio
async def test_create_appointment(client):
    """Test creating an appointment via API."""
    response = await client.post("/appointments", json={
        "patient_name": "John Doe",
        "department": "ENT",
        "visit_date": "2026-07-01",
        "summary": "Patient reports ringing in ears for 3 days.",
    })

    assert response.status_code == 200
    data = response.json()
    assert "appointment_id" in data
    assert len(data["appointment_id"]) > 0


@pytest.mark.asyncio
async def test_list_appointments_empty(client):
    """Test listing appointments when none exist."""
    response = await client.get("/appointments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_appointments_after_create(client):
    """Test listing appointments after creating one."""
    # Create
    create_resp = await client.post("/appointments", json={
        "patient_name": "Jane Smith",
        "department": "Neurology",
        "visit_date": "2026-07-15",
        "summary": "Recurring headaches for 2 weeks.",
    })
    assert create_resp.status_code == 200

    # List
    list_resp = await client.get("/appointments")
    assert list_resp.status_code == 200
    appointments = list_resp.json()
    assert len(appointments) >= 1

    # Verify data
    found = any(a["patient_name"] == "Jane Smith" for a in appointments)
    assert found is True


@pytest.mark.asyncio
async def test_create_appointment_validation(client):
    """Test appointment creation with missing fields."""
    response = await client.post("/appointments", json={
        "patient_name": "Test",
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_appointment_invalid_date(client):
    """Test appointment creation with invalid date."""
    response = await client.post("/appointments", json={
        "patient_name": "Test User",
        "department": "ENT",
        "visit_date": "not-a-date",
        "summary": "Test",
    })
    assert response.status_code == 422
