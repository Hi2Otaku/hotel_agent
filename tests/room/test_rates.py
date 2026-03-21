"""Integration tests for rate management endpoints (RATE-01).

Tests base rate, seasonal rate, and weekend surcharge CRUD with RBAC.
"""

import uuid

import pytest


async def _create_room_type(client) -> str:
    """Helper: create a room type and return its ID."""
    payload = {
        "name": f"Rate Test Type {uuid.uuid4().hex[:6]}",
        "slug": f"rate-test-{uuid.uuid4().hex[:6]}",
        "description": "For rate testing",
        "max_adults": 2,
        "max_children": 1,
        "bed_config": [{"type": "queen", "count": 1}],
        "amenities": {},
    }
    resp = await client.post("/api/v1/rooms/types", json=payload)
    assert resp.status_code == 201, f"Failed to create room type: {resp.text}"
    return resp.json()["id"]


class TestBaseRates:
    """Tests for base rate CRUD endpoints."""

    async def test_create_base_rate(self, client):
        """POST /api/v1/rooms/rates/base with valid data returns 201."""
        room_type_id = await _create_room_type(client)
        resp = await client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": room_type_id,
                "min_occupancy": 1,
                "max_occupancy": 2,
                "amount": "149.99",
                "currency": "USD",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"] == "149.99"
        assert data["currency"] == "USD"
        assert data["min_occupancy"] == 1
        assert data["max_occupancy"] == 2

    async def test_create_base_rate_invalid_room_type(self, client):
        """POST with nonexistent room_type_id returns 404."""
        resp = await client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": str(uuid.uuid4()),
                "min_occupancy": 1,
                "max_occupancy": 2,
                "amount": "100.00",
                "currency": "USD",
            },
        )
        assert resp.status_code == 404

    async def test_list_base_rates(self, client):
        """GET returns list of rates for room type."""
        room_type_id = await _create_room_type(client)
        # Create 2 base rates (different occupancy tiers)
        await client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": room_type_id,
                "min_occupancy": 1,
                "max_occupancy": 2,
                "amount": "100.00",
            },
        )
        await client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": room_type_id,
                "min_occupancy": 3,
                "max_occupancy": 4,
                "amount": "150.00",
            },
        )
        resp = await client.get(f"/api/v1/rooms/rates/base/{room_type_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2

    async def test_update_base_rate(self, client):
        """PATCH updates amount successfully."""
        room_type_id = await _create_room_type(client)
        create_resp = await client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": room_type_id,
                "min_occupancy": 1,
                "max_occupancy": 2,
                "amount": "100.00",
            },
        )
        rate_id = create_resp.json()["id"]
        resp = await client.patch(
            f"/api/v1/rooms/rates/base/{rate_id}",
            json={"amount": "120.00"},
        )
        assert resp.status_code == 200
        assert resp.json()["amount"] == "120.00"

    async def test_delete_base_rate(self, client):
        """DELETE returns 204 and rate is removed from list."""
        room_type_id = await _create_room_type(client)
        create_resp = await client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": room_type_id,
                "min_occupancy": 1,
                "max_occupancy": 2,
                "amount": "100.00",
            },
        )
        rate_id = create_resp.json()["id"]
        del_resp = await client.delete(f"/api/v1/rooms/rates/base/{rate_id}")
        assert del_resp.status_code == 204

        list_resp = await client.get(f"/api/v1/rooms/rates/base/{room_type_id}")
        rate_ids = [r["id"] for r in list_resp.json()]
        assert rate_id not in rate_ids


class TestSeasonalRates:
    """Tests for seasonal rate CRUD endpoints."""

    async def test_create_seasonal_rate(self, client):
        """POST with name, dates, multiplier returns 201."""
        room_type_id = await _create_room_type(client)
        resp = await client.post(
            "/api/v1/rooms/rates/seasonal",
            json={
                "room_type_id": room_type_id,
                "name": "Summer Peak",
                "start_date": "2026-06-01",
                "end_date": "2026-08-31",
                "multiplier": "1.30",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Summer Peak"
        assert data["multiplier"] == "1.30"

    async def test_create_seasonal_rate_invalid_dates(self, client):
        """POST with end_date before start_date returns 400."""
        room_type_id = await _create_room_type(client)
        resp = await client.post(
            "/api/v1/rooms/rates/seasonal",
            json={
                "room_type_id": room_type_id,
                "name": "Bad Dates",
                "start_date": "2026-08-31",
                "end_date": "2026-06-01",
                "multiplier": "1.20",
            },
        )
        assert resp.status_code == 400


class TestWeekendSurcharges:
    """Tests for weekend surcharge CRUD endpoints."""

    async def test_create_weekend_surcharge(self, client):
        """POST with multiplier and days returns 201."""
        room_type_id = await _create_room_type(client)
        resp = await client.post(
            "/api/v1/rooms/rates/weekend",
            json={
                "room_type_id": room_type_id,
                "multiplier": "1.15",
                "days": [4, 5],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["multiplier"] == "1.15"
        assert data["days"] == [4, 5]


class TestRatePermissions:
    """Tests for RBAC on rate endpoints."""

    async def test_create_base_rate_requires_manager(self, front_desk_client):
        """Front desk user cannot create base rates (403)."""
        resp = await front_desk_client.post(
            "/api/v1/rooms/rates/base",
            json={
                "room_type_id": str(uuid.uuid4()),
                "min_occupancy": 1,
                "max_occupancy": 2,
                "amount": "100.00",
            },
        )
        assert resp.status_code == 403
