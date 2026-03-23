"""Integration tests for booking list/management endpoints.

Covers: listing bookings, status filtering, pagination, and ownership enforcement.
"""

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

pytestmark = pytest.mark.asyncio


async def _create_booking(client):
    """Helper to create a booking and return its response data."""
    resp = await client.post("/api/v1/bookings/", json=BOOKING_DATA)
    assert resp.status_code == 201
    return resp.json()


async def test_list_bookings_empty(client):
    """GET /api/v1/bookings/ returns empty list when no bookings exist."""
    resp = await client.get("/api/v1/bookings/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


async def test_list_bookings_returns_guest_bookings(client):
    """GET /api/v1/bookings/ returns all bookings for the authenticated guest."""
    await _create_booking(client)
    await _create_booking(client)

    resp = await client.get("/api/v1/bookings/")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) >= 2
    assert body["total"] >= 2


async def test_list_bookings_filtered_by_status(client):
    """GET /api/v1/bookings/?status=pending returns only pending bookings."""
    await _create_booking(client)

    resp = await client.get("/api/v1/bookings/", params={"status": "pending"})
    assert resp.status_code == 200
    body = resp.json()
    for item in body["items"]:
        assert item["status"] == "pending"

    # Filter for a status with no bookings
    resp2 = await client.get("/api/v1/bookings/", params={"status": "checked_in"})
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["total"] == 0


async def test_list_bookings_pagination(client):
    """GET /api/v1/bookings/ supports skip and limit for pagination."""
    # Create 3 bookings
    for _ in range(3):
        await _create_booking(client)

    # Get first page (limit=2)
    resp1 = await client.get("/api/v1/bookings/", params={"limit": 2, "skip": 0})
    assert resp1.status_code == 200
    body1 = resp1.json()
    assert len(body1["items"]) == 2
    assert body1["total"] >= 3

    # Get second page
    resp2 = await client.get("/api/v1/bookings/", params={"limit": 2, "skip": 2})
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert len(body2["items"]) >= 1


async def test_list_bookings_only_own(client, other_user_client):
    """A guest can only see their own bookings, not other guests' bookings."""
    # Create a booking as the primary guest
    booking = await _create_booking(client)

    # List as other user -- should not see the primary guest's booking
    resp = await other_user_client.get("/api/v1/bookings/")
    assert resp.status_code == 200
    body = resp.json()
    ids = [item["id"] for item in body["items"]]
    assert booking["id"] not in ids
