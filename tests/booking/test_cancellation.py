"""Integration tests for booking cancellation with policy enforcement.

Covers: free cancellation, late cancellation with fee, invalid state transitions,
cancellation policy display (BOOK-05), and ownership checks.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

ROOM_TYPE_ID = str(uuid.uuid4())
FUTURE_CHECK_IN = (date.today() + timedelta(days=30)).isoformat()
FUTURE_CHECK_OUT = (date.today() + timedelta(days=33)).isoformat()
# Check-in within cancellation policy window (1 day away)
SOON_CHECK_IN = (date.today() + timedelta(days=1)).isoformat()
SOON_CHECK_OUT = (date.today() + timedelta(days=3)).isoformat()

BOOKING_DATA = {
    "room_type_id": ROOM_TYPE_ID,
    "check_in": FUTURE_CHECK_IN,
    "check_out": FUTURE_CHECK_OUT,
    "guest_count": 2,
}

SOON_BOOKING_DATA = {
    "room_type_id": ROOM_TYPE_ID,
    "check_in": SOON_CHECK_IN,
    "check_out": SOON_CHECK_OUT,
    "guest_count": 1,
}

GUEST_DETAILS = {
    "guest_first_name": "Jane",
    "guest_last_name": "Doe",
    "guest_email": "jane@example.com",
    "guest_phone": "+1234567890",
}

SUCCESS_CARD = {
    "card_number": "4242424242424242",
    "expiry_month": 12,
    "expiry_year": 2028,
    "cvc": "123",
    "cardholder_name": "Jane Doe",
}

pytestmark = pytest.mark.asyncio


async def _create_and_confirm(client, booking_data=None):
    """Create a booking, add guest details, pay, and return the confirmed booking."""
    data = booking_data or BOOKING_DATA
    resp = await client.post("/api/v1/bookings/", json=data)
    assert resp.status_code == 201
    booking = resp.json()
    bid = booking["id"]

    # Submit guest details
    await client.put(f"/api/v1/bookings/{bid}/guest-details", json=GUEST_DETAILS)

    # Process payment
    pay_resp = await client.post(f"/api/v1/bookings/{bid}/payment", json=SUCCESS_CARD)
    assert pay_resp.status_code == 200
    return pay_resp.json()["booking"]


async def test_cancel_pending_booking(client):
    """Cancelling a PENDING booking succeeds with no fee."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking = resp.json()

    cancel_resp = await client.post(f"/api/v1/bookings/{booking['id']}/cancel")
    assert cancel_resp.status_code == 200
    body = cancel_resp.json()
    assert body["status"] == "cancelled"
    assert body["cancellation_reason"] == "guest_cancelled"
    assert body["cancellation_fee"] is None


async def test_cancel_confirmed_free(client):
    """Cancelling a CONFIRMED booking well before check-in incurs no fee."""
    booking = await _create_and_confirm(client)

    cancel_resp = await client.post(f"/api/v1/bookings/{booking['id']}/cancel")
    assert cancel_resp.status_code == 200
    body = cancel_resp.json()
    assert body["status"] == "cancelled"
    assert body["cancellation_reason"] == "guest_cancelled"
    # Check-in is 30 days away, well beyond the 3-day policy window
    assert body["cancellation_fee"] is None


async def test_cancel_confirmed_late(client):
    """Cancelling a CONFIRMED booking within policy window charges first night fee."""
    booking = await _create_and_confirm(client, SOON_BOOKING_DATA)

    cancel_resp = await client.post(f"/api/v1/bookings/{booking['id']}/cancel")
    assert cancel_resp.status_code == 200
    body = cancel_resp.json()
    assert body["status"] == "cancelled"
    assert body["cancellation_fee"] is not None
    # Fee should equal price_per_night
    assert Decimal(body["cancellation_fee"]) == Decimal(body.get("price_per_night", "100.00"))


async def test_cancel_checked_in_fails(client):
    """Cannot cancel a booking that is already checked in."""
    booking = await _create_and_confirm(client)

    # Manually transition to checked_in via the service layer
    from app.services.booking import get_booking, transition_booking
    from app.core.database import async_session_factory

    async with async_session_factory() as db:
        b = await get_booking(db, uuid.UUID(booking["id"]))
        await transition_booking(db, b, "checked_in")

    cancel_resp = await client.post(f"/api/v1/bookings/{booking['id']}/cancel")
    assert cancel_resp.status_code == 400


async def test_cancel_already_cancelled_fails(client):
    """Cannot cancel a booking that is already cancelled."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking = resp.json()

    # Cancel once
    await client.post(f"/api/v1/bookings/{booking['id']}/cancel")

    # Try to cancel again
    cancel_resp = await client.post(f"/api/v1/bookings/{booking['id']}/cancel")
    assert cancel_resp.status_code == 400


async def test_cancellation_policy_displayed(client):
    """GET /api/v1/bookings/{id}/cancellation-policy returns policy details (BOOK-05)."""
    booking = await _create_and_confirm(client)

    resp = await client.get(f"/api/v1/bookings/{booking['id']}/cancellation-policy")
    assert resp.status_code == 200
    body = resp.json()
    assert "policy_text" in body
    assert "free_cancellation_before" in body
    assert "Free cancellation" in body["policy_text"]


async def test_cancel_wrong_user(client, other_user_client):
    """Cancelling another user's booking returns 403."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking = resp.json()

    cancel_resp = await other_user_client.post(f"/api/v1/bookings/{booking['id']}/cancel")
    assert cancel_resp.status_code == 403
