"""Integration tests for pricing calendar endpoint (ROOM-04).

Tests calendar generation with per-day rates and availability indicators.
"""

import uuid
from decimal import Decimal

import pytest

from .conftest import seed_room_data


@pytest.mark.asyncio
async def test_pricing_calendar_6_months(public_client, room_db_session):
    """GET calendar returns ~180 days of rates with availability indicators."""
    data = await seed_room_data(room_db_session)

    resp = await public_client.get(
        "/api/v1/search/calendar",
        params={
            "room_type_id": str(data["deluxe_id"]),
            "guests": 2,
            "months": 6,
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["room_type_id"] == str(data["deluxe_id"])
    assert body["room_type_name"] == "Deluxe King"

    # Should have ~180 days
    assert len(body["days"]) >= 170
    assert len(body["days"]) <= 190

    for day in body["days"]:
        assert Decimal(str(day["rate"])) > 0
        assert day["availability_indicator"] in ["green", "yellow", "red"]
        assert "base_amount" in day
        assert "seasonal_multiplier" in day
        assert "weekend_multiplier" in day
        assert "available_count" in day
        assert "total_rooms" in day


@pytest.mark.asyncio
async def test_calendar_room_type_filter(public_client, room_db_session):
    """GET calendar with room_type_id returns data for that specific type."""
    data = await seed_room_data(room_db_session)

    # Request for Standard Twin
    resp = await public_client.get(
        "/api/v1/search/calendar",
        params={
            "room_type_id": str(data["standard_id"]),
            "guests": 2,
            "months": 1,
        },
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["room_type_id"] == str(data["standard_id"])
    assert body["room_type_name"] == "Standard Twin"
    assert len(body["days"]) >= 28
    assert len(body["days"]) <= 32

    # All days should have rates matching the Standard base rate ($120)
    for day in body["days"]:
        rate = Decimal(str(day["rate"]))
        assert rate >= Decimal("120.00")  # base or with multipliers
