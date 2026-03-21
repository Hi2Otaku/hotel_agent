"""Integration tests for booking modification with price recalculation.

Covers: date changes, room type changes, guest detail updates, invalid states,
price difference display, and no-availability failures.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.services import booking as _booking_service_module

ROOM_TYPE_ID = str(uuid.uuid4())
OTHER_ROOM_TYPE_ID = str(uuid.uuid4())
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
}

SUCCESS_CARD = {
    "card_number": "4242424242424242",
    "expiry_month": 12,
    "expiry_year": 2028,
    "cvc": "123",
    "cardholder_name": "Jane Doe",
}

pytestmark = pytest.mark.asyncio


async def _create_and_confirm(client):
    """Create a booking, add guest details, pay, and return the confirmed booking."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    assert resp.status_code == 201
    booking = resp.json()
    bid = booking["id"]

    await client.put(f"/api/v1/bookings/{bid}/guest-details", json=GUEST_DETAILS)

    pay_resp = await client.post(f"/api/v1/bookings/{bid}/payment", json=SUCCESS_CARD)
    assert pay_resp.status_code == 200
    return pay_resp.json()["booking"]


async def test_modify_dates(client):
    """Modifying check-in/check-out on a CONFIRMED booking recalculates price."""
    booking = await _create_and_confirm(client)

    new_check_in = (date.today() + timedelta(days=40)).isoformat()
    new_check_out = (date.today() + timedelta(days=44)).isoformat()

    # Mock returns different pricing for new dates (4 nights instead of 3)
    new_pricing = {
        "total_price": Decimal("400.00"),
        "price_per_night": Decimal("100.00"),
        "currency": "USD",
        "nightly_breakdown": [],
        "room_type_name": "Deluxe Room",
    }
    with patch.object(
        _booking_service_module,
        "get_pricing_from_room_service",
        new_callable=AsyncMock,
        return_value=new_pricing,
    ):
        resp = await client.put(
            f"/api/v1/bookings/{booking['id']}/modify",
            json={"check_in": new_check_in, "check_out": new_check_out},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["booking"]["check_in"] == new_check_in
    assert body["booking"]["check_out"] == new_check_out


async def test_modify_room_type(client):
    """Changing room_type_id re-checks availability and updates pricing."""
    booking = await _create_and_confirm(client)

    new_pricing = {
        "total_price": Decimal("600.00"),
        "price_per_night": Decimal("200.00"),
        "currency": "USD",
        "nightly_breakdown": [],
        "room_type_name": "Suite",
    }
    with patch.object(
        _booking_service_module,
        "get_pricing_from_room_service",
        new_callable=AsyncMock,
        return_value=new_pricing,
    ):
        resp = await client.put(
            f"/api/v1/bookings/{booking['id']}/modify",
            json={"room_type_id": OTHER_ROOM_TYPE_ID},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["booking"]["room_type_id"] == OTHER_ROOM_TYPE_ID


async def test_modify_guest_details(client):
    """Modifying only guest details does not trigger price recalculation."""
    booking = await _create_and_confirm(client)

    resp = await client.put(
        f"/api/v1/bookings/{booking['id']}/modify",
        json={"guest_first_name": "Updated"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["booking"]["guest_first_name"] == "Updated"
    # Price should remain unchanged
    assert body["old_total"] == body["new_total"]
    assert body["price_difference"] == "0"


async def test_modify_pending_fails(client):
    """Cannot modify a PENDING booking."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    booking = resp.json()

    modify_resp = await client.put(
        f"/api/v1/bookings/{booking['id']}/modify",
        json={"guest_first_name": "New"},
    )
    assert modify_resp.status_code == 400
    assert "confirmed" in modify_resp.json()["detail"].lower()


async def test_modify_checked_in_fails(client):
    """Cannot modify a booking after check-in."""
    booking = await _create_and_confirm(client)

    # Transition to checked_in
    from app.services.booking import get_booking, transition_booking
    from app.core.database import async_session_factory

    async with async_session_factory() as db:
        b = await get_booking(db, uuid.UUID(booking["id"]))
        await transition_booking(db, b, "checked_in")

    modify_resp = await client.put(
        f"/api/v1/bookings/{booking['id']}/modify",
        json={"guest_first_name": "New"},
    )
    assert modify_resp.status_code == 400


async def test_modify_shows_price_difference(client):
    """Modify response includes old_total, new_total, and price_difference."""
    booking = await _create_and_confirm(client)

    new_pricing = {
        "total_price": Decimal("500.00"),
        "price_per_night": Decimal("100.00"),
        "currency": "USD",
        "nightly_breakdown": [],
        "room_type_name": "Deluxe Room",
    }
    new_check_in = (date.today() + timedelta(days=40)).isoformat()
    new_check_out = (date.today() + timedelta(days=45)).isoformat()

    with patch.object(
        _booking_service_module,
        "get_pricing_from_room_service",
        new_callable=AsyncMock,
        return_value=new_pricing,
    ):
        resp = await client.put(
            f"/api/v1/bookings/{booking['id']}/modify",
            json={"check_in": new_check_in, "check_out": new_check_out},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "old_total" in body
    assert "new_total" in body
    assert "price_difference" in body
    assert "currency" in body


async def test_modify_no_availability_fails(client):
    """Modifying dates when no rooms available returns 409."""
    booking = await _create_and_confirm(client)

    new_check_in = (date.today() + timedelta(days=50)).isoformat()
    new_check_out = (date.today() + timedelta(days=53)).isoformat()

    # Mock room count to 0 so availability check fails
    with patch.object(
        _booking_service_module,
        "get_room_count_for_type",
        new_callable=AsyncMock,
        return_value=0,
    ):
        resp = await client.put(
            f"/api/v1/bookings/{booking['id']}/modify",
            json={"check_in": new_check_in, "check_out": new_check_out},
        )

    assert resp.status_code == 409
    assert "available" in resp.json()["detail"].lower()
