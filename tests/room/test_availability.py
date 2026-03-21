"""Integration tests for availability logic (ROOM-02).

Tests overlap exclusion, pending blocking, cancelled non-blocking,
back-to-back half-open intervals, and overbooking buffer.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from tests.room.conftest import seed_room_data, insert_reservation


@pytest.mark.asyncio
async def test_overlap_exclusion(public_client, room_db_session):
    """Reservation overlapping search dates reduces available count by 1."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=3)

    # Insert 1 confirmed reservation for Deluxe overlapping search dates
    await insert_reservation(
        room_db_session,
        booking_id=uuid.uuid4(),
        room_type_id=data["deluxe_id"],
        check_in=tomorrow,
        check_out=checkout,
        status="confirmed",
    )

    resp = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    # Find deluxe in results
    deluxe_results = [r for r in body["results"] if r["room_type_id"] == str(data["deluxe_id"])]
    assert len(deluxe_results) == 1
    # Should be total_rooms - 1 (3 rooms - 1 blocked = 2 available)
    assert deluxe_results[0]["available_count"] == 2


@pytest.mark.asyncio
async def test_pending_blocks(public_client, room_db_session):
    """Pending status reservation blocks availability same as confirmed."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=2)

    await insert_reservation(
        room_db_session,
        booking_id=uuid.uuid4(),
        room_type_id=data["deluxe_id"],
        check_in=tomorrow,
        check_out=checkout,
        status="pending",
    )

    resp = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
        },
    )
    assert resp.status_code == 200
    deluxe_results = [r for r in resp.json()["results"] if r["room_type_id"] == str(data["deluxe_id"])]
    assert len(deluxe_results) == 1
    assert deluxe_results[0]["available_count"] == 2  # 3 - 1 = 2


@pytest.mark.asyncio
async def test_cancelled_does_not_block(public_client, room_db_session):
    """Cancelled reservation does not reduce available count."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=2)

    await insert_reservation(
        room_db_session,
        booking_id=uuid.uuid4(),
        room_type_id=data["deluxe_id"],
        check_in=tomorrow,
        check_out=checkout,
        status="cancelled",
    )

    resp = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
        },
    )
    assert resp.status_code == 200
    deluxe_results = [r for r in resp.json()["results"] if r["room_type_id"] == str(data["deluxe_id"])]
    assert len(deluxe_results) == 1
    assert deluxe_results[0]["available_count"] == 3  # All rooms still available


@pytest.mark.asyncio
async def test_back_to_back(public_client, room_db_session):
    """Reservation check_out == search check_in: NO conflict (half-open intervals)."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    day_after = tomorrow + timedelta(days=1)
    checkout = day_after + timedelta(days=2)

    # Reservation checks out exactly when our search starts
    await insert_reservation(
        room_db_session,
        booking_id=uuid.uuid4(),
        room_type_id=data["deluxe_id"],
        check_in=tomorrow - timedelta(days=2),
        check_out=tomorrow,  # checks out on our check-in day
        status="confirmed",
    )

    resp = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
        },
    )
    assert resp.status_code == 200
    deluxe_results = [r for r in resp.json()["results"] if r["room_type_id"] == str(data["deluxe_id"])]
    assert len(deluxe_results) == 1
    # All rooms still available -- no conflict
    assert deluxe_results[0]["available_count"] == 3


@pytest.mark.asyncio
async def test_overbooking_buffer(public_client, room_db_session):
    """Room type with overbooking_pct=10 and 10 rooms shows 11 effective capacity."""
    from app.services.availability import effective_capacity

    # Test the function directly
    result = effective_capacity(10, Decimal("10.00"))
    assert result == 11

    # Also test via API: use seed data (3 Deluxe rooms with default 0% overbooking)
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=2)

    # Set overbooking to 50% on Deluxe (3 rooms -> 4 effective capacity)
    from app.models.room_type import RoomType
    from sqlalchemy import select

    result = await room_db_session.execute(
        select(RoomType).where(RoomType.id == data["deluxe_id"])
    )
    rt = result.scalar_one()
    rt.overbooking_pct = Decimal("50.00")
    await room_db_session.commit()

    # Block all 3 physical rooms
    for i in range(3):
        await insert_reservation(
            room_db_session,
            booking_id=uuid.uuid4(),
            room_type_id=data["deluxe_id"],
            check_in=tomorrow,
            check_out=checkout,
            status="confirmed",
        )

    resp = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
        },
    )
    assert resp.status_code == 200
    deluxe_results = [r for r in resp.json()["results"] if r["room_type_id"] == str(data["deluxe_id"])]
    assert len(deluxe_results) == 1
    # effective_capacity(3, 50%) = int(3 * 1.5) = 4, minus 3 blocked = 1 available
    assert deluxe_results[0]["available_count"] == 1
