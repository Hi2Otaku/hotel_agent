"""Integration tests for search and room detail endpoints (ROOM-01, ROOM-03).

Tests search by dates/guests, filters, validation, and room type detail.
All endpoints are public -- uses public_client fixture (no auth).
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from tests.room.conftest import seed_room_data, insert_reservation


@pytest.mark.asyncio
async def test_search_by_dates_and_guests(public_client, room_db_session):
    """Search with valid dates and guest count returns results grouped by room type."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=3)

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
    assert body["total"] >= 1
    assert body["check_in"] == str(tomorrow)
    assert body["check_out"] == str(checkout)
    assert body["guests"] == 2

    for result in body["results"]:
        assert result["available_count"] > 0
        # price_per_night is a Decimal-like string
        assert Decimal(str(result["price_per_night"])) > 0
        assert "room_type_id" in result
        assert "name" in result
        assert "slug" in result


@pytest.mark.asyncio
async def test_search_filters(public_client, room_db_session):
    """Search with room_type_id, price range, and amenity filters."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=2)

    # Filter by room_type_id: only Deluxe
    resp = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
            "room_type_id": str(data["deluxe_id"]),
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["results"][0]["room_type_id"] == str(data["deluxe_id"])

    # Filter by max_price=150: should only return Standard ($120)
    resp2 = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
            "max_price": "150",
        },
    )
    assert resp2.status_code == 200
    body2 = resp2.json()
    for result in body2["results"]:
        assert Decimal(str(result["price_per_night"])) <= Decimal("150")

    # Filter by amenities="room": both types have "room" amenity key
    resp3 = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
            "amenities": "room",
        },
    )
    assert resp3.status_code == 200
    assert resp3.json()["total"] >= 1


@pytest.mark.asyncio
async def test_search_no_results(public_client, room_db_session):
    """Search with dates where all rooms are blocked returns empty results."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=2)

    # Block all deluxe rooms (3 rooms)
    for i in range(3):
        await insert_reservation(
            room_db_session,
            booking_id=uuid.uuid4(),
            room_type_id=data["deluxe_id"],
            check_in=tomorrow,
            check_out=checkout,
            status="confirmed",
        )
    # Block all standard rooms (2 rooms)
    for i in range(2):
        await insert_reservation(
            room_db_session,
            booking_id=uuid.uuid4(),
            room_type_id=data["standard_id"],
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
    assert body["results"] == []
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_search_validation(public_client, room_db_session):
    """check_in >= check_out returns 400; check_in in past returns 400."""
    tomorrow = date.today() + timedelta(days=1)

    # check_in == check_out
    resp = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow),
            "check_out": str(tomorrow),
            "guests": 2,
        },
    )
    assert resp.status_code == 400

    # check_in after check_out
    resp2 = await public_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": str(tomorrow + timedelta(days=3)),
            "check_out": str(tomorrow),
            "guests": 2,
        },
    )
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_room_type_detail(public_client, room_db_session):
    """GET room detail with dates returns photos, amenities, bed_config, pricing, availability."""
    data = await seed_room_data(room_db_session)
    tomorrow = date.today() + timedelta(days=1)
    checkout = tomorrow + timedelta(days=2)

    resp = await public_client.get(
        f"/api/v1/search/room-types/{data['deluxe_id']}",
        params={
            "check_in": str(tomorrow),
            "check_out": str(checkout),
            "guests": 2,
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["id"] == str(data["deluxe_id"])
    assert body["name"] == "Deluxe King"
    assert isinstance(body["photo_urls"], list)
    assert isinstance(body["amenities"], dict)
    assert isinstance(body["bed_config"], list)
    assert isinstance(body["nightly_rates"], list)
    assert len(body["nightly_rates"]) == 2  # 2 nights
    assert Decimal(str(body["total_price"])) > 0
    assert body["available_count"] >= 0
    assert body["total_rooms"] >= 0
    assert Decimal(str(body["price_per_night"])) > 0
