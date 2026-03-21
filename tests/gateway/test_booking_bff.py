"""Tests for Gateway BFF booking aggregation endpoints.

Verifies that BFF endpoints enrich booking data with room type details
from the Room service.
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from .conftest import mock_httpx_response

pytestmark = pytest.mark.asyncio

MOCK_BOOKING = {
    "id": "00000000-0000-0000-0000-000000000010",
    "confirmation_number": "HB-A3K7X2",
    "user_id": "00000000-0000-0000-0000-000000000099",
    "room_type_id": "00000000-0000-0000-0000-000000000001",
    "room_id": None,
    "check_in": "2026-04-01",
    "check_out": "2026-04-03",
    "guest_count": 2,
    "status": "confirmed",
    "total_price": "400.00",
    "price_per_night": "200.00",
    "currency": "USD",
    "nightly_breakdown": [],
    "guest_first_name": "Jane",
    "guest_last_name": "Doe",
    "guest_email": "jane@example.com",
    "guest_phone": "+1234567890",
    "special_requests": None,
    "expires_at": None,
    "cancelled_at": None,
    "cancellation_reason": None,
    "cancellation_fee": None,
    "created_at": "2026-03-20T10:00:00Z",
    "updated_at": "2026-03-20T10:00:00Z",
}

MOCK_ROOM_TYPE = {
    "id": "00000000-0000-0000-0000-000000000001",
    "name": "Deluxe King",
    "description": "A spacious king room",
    "photo_urls": ["/photos/deluxe1.jpg", "/photos/deluxe2.jpg"],
    "amenities": ["wifi", "minibar", "room_service"],
}

MOCK_BOOKING_LIST = {
    "items": [MOCK_BOOKING],
    "total": 1,
}


async def test_booking_details_enriched(gateway_client):
    """GET /api/v1/bookings/{id}/details returns booking + room type info."""
    mock_client_instance = AsyncMock()

    async def mock_get(url, **kwargs):
        if "/rooms/types/" in url:
            return mock_httpx_response(200, MOCK_ROOM_TYPE)
        return mock_httpx_response(200, MOCK_BOOKING)

    mock_client_instance.get = AsyncMock(side_effect=mock_get)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("app.api.booking.httpx.AsyncClient", return_value=mock_client_instance):
        resp = await gateway_client.get(
            "/api/v1/bookings/00000000-0000-0000-0000-000000000010/details",
            headers={"authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    data = resp.json()
    # Original booking fields
    assert data["confirmation_number"] == "HB-A3K7X2"
    assert data["status"] == "confirmed"
    # Enriched room type fields
    assert data["room_type_name"] == "Deluxe King"
    assert data["room_type_description"] == "A spacious king room"
    assert len(data["room_type_photos"]) == 2
    assert "wifi" in data["room_type_amenities"]


async def test_booking_summary_enriched(gateway_client):
    """GET /api/v1/bookings/summary returns bookings with room type names."""
    mock_client_instance = AsyncMock()

    async def mock_get(url, **kwargs):
        if "/rooms/types/" in url:
            return mock_httpx_response(200, MOCK_ROOM_TYPE)
        return mock_httpx_response(200, MOCK_BOOKING_LIST)

    mock_client_instance.get = AsyncMock(side_effect=mock_get)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("app.api.booking.httpx.AsyncClient", return_value=mock_client_instance):
        resp = await gateway_client.get(
            "/api/v1/bookings/summary",
            headers={"authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["room_type_name"] == "Deluxe King"


async def test_booking_details_without_room_service(gateway_client):
    """BFF gracefully degrades if Room service is unavailable."""
    mock_client_instance = AsyncMock()

    async def mock_get(url, **kwargs):
        if "/rooms/types/" in url:
            raise httpx.HTTPError("Connection refused")
        return mock_httpx_response(200, MOCK_BOOKING)

    mock_client_instance.get = AsyncMock(side_effect=mock_get)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("app.api.booking.httpx.AsyncClient", return_value=mock_client_instance):
        resp = await gateway_client.get(
            "/api/v1/bookings/00000000-0000-0000-0000-000000000010/details",
            headers={"authorization": "Bearer test-token"},
        )

    assert resp.status_code == 200
    data = resp.json()
    # Booking data should still be present
    assert data["confirmation_number"] == "HB-A3K7X2"
    # Room details should be absent (graceful degradation)
    assert "room_type_name" not in data
