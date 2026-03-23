"""Integration tests for the 3-step booking flow.

Covers: create booking, submit guest details, process payment,
ownership checks, confirmation number format, and cancellation policy.
"""

import re
import uuid
from datetime import date, timedelta

import pytest


ROOM_TYPE_ID = str(uuid.uuid4())
FUTURE_CHECK_IN = (date.today() + timedelta(days=30)).isoformat()
FUTURE_CHECK_OUT = (date.today() + timedelta(days=33)).isoformat()

BOOKING_DATA = {
    "room_type_id": ROOM_TYPE_ID,
    "check_in": FUTURE_CHECK_IN,
    "check_out": FUTURE_CHECK_OUT,
    "guest_count": 2,
}

GUEST_DETAILS = {
    "guest_first_name": "Jane",
    "guest_last_name": "Doe",
    "guest_email": "jane@example.com",
    "guest_phone": "+1234567890",
    "guest_address": "123 Main St",
    "special_requests": "Late check-in",
}

SUCCESS_CARD = {
    "card_number": "4242424242424242",
    "expiry_month": 12,
    "expiry_year": 2028,
    "cvc": "123",
    "cardholder_name": "Jane Doe",
}

DECLINE_CARD = {
    "card_number": "4000000000000002",
    "expiry_month": 12,
    "expiry_year": 2028,
    "cvc": "123",
    "cardholder_name": "Jane Doe",
}


@pytest.mark.asyncio
async def test_create_booking_returns_pending(client):
    """POST /api/v1/bookings creates a PENDING booking with confirmation number."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["confirmation_number"].startswith("HB-")
    assert body["expires_at"] is not None
    assert body["total_price"] == "300.00"


@pytest.mark.asyncio
async def test_create_booking_requires_auth(unauth_client):
    """POST /api/v1/bookings without a token returns 401."""
    resp = await unauth_client.post("/api/v1/bookings/", json=BOOKING_DATA)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_submit_guest_details(client):
    """PUT /{id}/guest-details saves guest information."""
    # Step 1: Create booking
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking_id = resp.json()["id"]

    # Step 2: Submit guest details
    resp = await client.put(
        f"/api/v1/bookings/{booking_id}/guest-details", json=GUEST_DETAILS
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["guest_first_name"] == "Jane"
    assert body["guest_last_name"] == "Doe"
    assert body["guest_email"] == "jane@example.com"


@pytest.mark.asyncio
async def test_submit_guest_details_wrong_user(client, other_user_client):
    """PUT with a different user returns 403."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking_id = resp.json()["id"]

    resp = await other_user_client.put(
        f"/api/v1/bookings/{booking_id}/guest-details", json=GUEST_DETAILS
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_payment_success(client):
    """POST /{id}/payment with success card confirms the booking."""
    # Step 1
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking_id = resp.json()["id"]

    # Step 2
    await client.put(f"/api/v1/bookings/{booking_id}/guest-details", json=GUEST_DETAILS)

    # Step 3
    resp = await client.post(f"/api/v1/bookings/{booking_id}/payment", json=SUCCESS_CARD)
    assert resp.status_code == 200
    body = resp.json()
    assert body["booking"]["status"] == "confirmed"
    assert body["payment"]["status"] == "succeeded"
    assert body["payment"]["transaction_id"].startswith("txn_")


@pytest.mark.asyncio
async def test_payment_decline(client):
    """POST /{id}/payment with decline card returns 402."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking_id = resp.json()["id"]
    await client.put(f"/api/v1/bookings/{booking_id}/guest-details", json=GUEST_DETAILS)

    resp = await client.post(f"/api/v1/bookings/{booking_id}/payment", json=DECLINE_CARD)
    assert resp.status_code == 402
    body = resp.json()
    assert "declined" in str(body["detail"]["payment"]["status"])


@pytest.mark.asyncio
async def test_full_three_step_flow(client):
    """Complete lifecycle: create -> guest details -> payment -> confirmed."""
    # Step 1: Create
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    assert resp.status_code == 201
    booking_id = resp.json()["id"]
    assert resp.json()["status"] == "pending"

    # Step 2: Guest details
    resp = await client.put(
        f"/api/v1/bookings/{booking_id}/guest-details", json=GUEST_DETAILS
    )
    assert resp.status_code == 200

    # Step 3: Payment
    resp = await client.post(f"/api/v1/bookings/{booking_id}/payment", json=SUCCESS_CARD)
    assert resp.status_code == 200
    assert resp.json()["booking"]["status"] == "confirmed"

    # Verify via GET
    resp = await client.get(f"/api/v1/bookings/{booking_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


@pytest.mark.asyncio
async def test_confirmation_number_in_response(client):
    """Confirmation number matches HB-[A-Z0-9]{6} pattern."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    confirmation = resp.json()["confirmation_number"]
    assert re.match(r"^HB-[A-Z2-9]{6}$", confirmation), f"Unexpected format: {confirmation}"


@pytest.mark.asyncio
async def test_cancellation_policy_endpoint(client):
    """GET /{id}/cancellation-policy returns policy text."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/bookings/{booking_id}/cancellation-policy")
    assert resp.status_code == 200
    body = resp.json()
    assert "policy_text" in body
    assert body["free_cancellation_before"] is not None
