"""Unit/integration tests for pricing calculation engine (RATE-02).

Verifies multiplicative stacking with exact Decimal precision.
Uses concrete dates that fall on known weekdays.
"""

import uuid
from datetime import date
from decimal import Decimal

import pytest


async def _setup_room_type_with_rates(client, base_amount="100.00"):
    """Create room type with base rate, seasonal rate (Jun-Aug 1.30x), weekend surcharge (Fri-Sat 1.20x).

    Returns room_type_id.
    """
    # Create room type
    rt_resp = await client.post(
        "/api/v1/rooms/types",
        json={
            "name": f"Price Test {uuid.uuid4().hex[:6]}",
            "slug": f"price-test-{uuid.uuid4().hex[:6]}",
            "description": "For pricing tests",
            "max_adults": 4,
            "max_children": 2,
            "bed_config": [{"type": "king", "count": 1}],
            "amenities": {},
        },
    )
    assert rt_resp.status_code == 201, f"Failed to create room type: {rt_resp.text}"
    room_type_id = rt_resp.json()["id"]

    # Base rate: 1-2 guests
    await client.post(
        "/api/v1/rooms/rates/base",
        json={
            "room_type_id": room_type_id,
            "min_occupancy": 1,
            "max_occupancy": 2,
            "amount": base_amount,
        },
    )

    # Seasonal rate: Summer Peak Jun-Aug = 1.30x
    await client.post(
        "/api/v1/rooms/rates/seasonal",
        json={
            "room_type_id": room_type_id,
            "name": "Summer Peak",
            "start_date": "2026-06-01",
            "end_date": "2026-08-31",
            "multiplier": "1.30",
        },
    )

    # Weekend surcharge: Fri-Sat = 1.20x
    await client.post(
        "/api/v1/rooms/rates/weekend",
        json={
            "room_type_id": room_type_id,
            "multiplier": "1.20",
            "days": [4, 5],
        },
    )

    return room_type_id


class TestPriceCalculation:
    """Tests for the price calculation endpoint with multiplicative stacking."""

    async def test_calculate_price_base_only(self, client):
        """Wednesday in March: no seasonal, no weekend. Returns base rate only."""
        room_type_id = await _setup_room_type_with_rates(client)
        # date(2026, 3, 18) = Wednesday
        resp = await client.post(
            "/api/v1/rooms/rates/calculate",
            json={
                "room_type_id": room_type_id,
                "check_in": "2026-03-18",
                "check_out": "2026-03-19",
                "occupancy": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nightly_rates"]) == 1
        night = data["nightly_rates"][0]
        assert Decimal(night["final_amount"]) == Decimal("100.00")
        assert Decimal(night["seasonal_multiplier"]) == Decimal("1.00")
        assert Decimal(night["weekend_multiplier"]) == Decimal("1.00")
        assert Decimal(data["total"]) == Decimal("100.00")

    async def test_calculate_price_with_seasonal(self, client):
        """Wednesday in July: seasonal applies. 100.00 * 1.30 = 130.00."""
        room_type_id = await _setup_room_type_with_rates(client)
        # date(2026, 7, 15) = Wednesday
        resp = await client.post(
            "/api/v1/rooms/rates/calculate",
            json={
                "room_type_id": room_type_id,
                "check_in": "2026-07-15",
                "check_out": "2026-07-16",
                "occupancy": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        night = data["nightly_rates"][0]
        assert Decimal(night["final_amount"]) == Decimal("130.00")
        assert Decimal(night["seasonal_multiplier"]) == Decimal("1.30")

    async def test_calculate_price_with_weekend(self, client):
        """Friday in March: weekend applies. 100.00 * 1.20 = 120.00."""
        room_type_id = await _setup_room_type_with_rates(client)
        # date(2026, 3, 20) = Friday
        resp = await client.post(
            "/api/v1/rooms/rates/calculate",
            json={
                "room_type_id": room_type_id,
                "check_in": "2026-03-20",
                "check_out": "2026-03-21",
                "occupancy": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        night = data["nightly_rates"][0]
        assert Decimal(night["final_amount"]) == Decimal("120.00")
        assert Decimal(night["weekend_multiplier"]) == Decimal("1.20")

    async def test_multiplicative_stacking(self, client):
        """Friday in July: seasonal + weekend. 100.00 * 1.30 * 1.20 = 156.00."""
        room_type_id = await _setup_room_type_with_rates(client)
        # date(2026, 7, 17) = Friday
        resp = await client.post(
            "/api/v1/rooms/rates/calculate",
            json={
                "room_type_id": room_type_id,
                "check_in": "2026-07-17",
                "check_out": "2026-07-18",
                "occupancy": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        night = data["nightly_rates"][0]
        assert Decimal(night["final_amount"]) == Decimal("156.00")
        assert Decimal(night["seasonal_multiplier"]) == Decimal("1.30")
        assert Decimal(night["weekend_multiplier"]) == Decimal("1.20")

    async def test_no_float_contamination(self, client):
        """Verify total is a clean Decimal string with no floating point artifacts."""
        room_type_id = await _setup_room_type_with_rates(client)
        # date(2026, 7, 17) = Friday (seasonal + weekend)
        resp = await client.post(
            "/api/v1/rooms/rates/calculate",
            json={
                "room_type_id": room_type_id,
                "check_in": "2026-07-17",
                "check_out": "2026-07-18",
                "occupancy": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        total_str = str(data["total"])
        # Should be "156.00" not "156.00000000000001" or similar
        assert total_str == "156.00", f"Float contamination detected: {total_str}"
        # Verify it parses cleanly to Decimal
        total_decimal = Decimal(total_str)
        assert total_decimal == Decimal("156.00")

    async def test_multi_night_mixed_rates(self, client):
        """Thu-Sun in July: Thu weekday(130), Fri weekend(156), Sat weekend(156). Total: 442.00."""
        room_type_id = await _setup_room_type_with_rates(client)
        # date(2026, 7, 16) = Thursday, checkout date(2026, 7, 19) = Sunday
        resp = await client.post(
            "/api/v1/rooms/rates/calculate",
            json={
                "room_type_id": room_type_id,
                "check_in": "2026-07-16",
                "check_out": "2026-07-19",
                "occupancy": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nightly_rates"]) == 3

        # Thursday: seasonal only (100 * 1.30 = 130.00)
        assert Decimal(data["nightly_rates"][0]["final_amount"]) == Decimal("130.00")
        # Friday: seasonal + weekend (100 * 1.30 * 1.20 = 156.00)
        assert Decimal(data["nightly_rates"][1]["final_amount"]) == Decimal("156.00")
        # Saturday: seasonal + weekend (100 * 1.30 * 1.20 = 156.00)
        assert Decimal(data["nightly_rates"][2]["final_amount"]) == Decimal("156.00")

        assert Decimal(data["total"]) == Decimal("442.00")

    async def test_higher_occupancy_tier(self, client):
        """Higher occupancy tier uses the correct base rate."""
        room_type_id = await _setup_room_type_with_rates(client)
        # Add a higher occupancy tier
        await client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": room_type_id,
                "min_occupancy": 3,
                "max_occupancy": 4,
                "amount": "150.00",
            },
        )
        # Calculate for 3 guests on Wednesday in March (no seasonal, no weekend)
        # date(2026, 3, 18) = Wednesday
        resp = await client.post(
            "/api/v1/rooms/rates/calculate",
            json={
                "room_type_id": room_type_id,
                "check_in": "2026-03-18",
                "check_out": "2026-03-19",
                "occupancy": 3,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert Decimal(data["nightly_rates"][0]["base_amount"]) == Decimal("150.00")
        assert Decimal(data["total"]) == Decimal("150.00")
