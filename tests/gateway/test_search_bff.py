"""Tests for Gateway BFF search aggregation endpoints."""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from .conftest import (
    MOCK_CALENDAR_RESPONSE,
    MOCK_DETAIL_RESPONSE,
    MOCK_SEARCH_RESPONSE,
    mock_httpx_response,
)

pytestmark = pytest.mark.asyncio


async def test_bff_search_availability(gateway_client, mock_room_service):
    """BFF forwards availability search to Room service and returns response."""
    mock_instance = mock_room_service._instance
    mock_instance.get = AsyncMock(
        return_value=mock_httpx_response(200, MOCK_SEARCH_RESPONSE)
    )

    resp = await gateway_client.get(
        "/api/v1/search/availability",
        params={"check_in": "2026-04-01", "check_out": "2026-04-03", "guests": 2},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["results"][0]["name"] == "Deluxe King"
    mock_instance.get.assert_called_once()


async def test_bff_room_type_detail(gateway_client, mock_room_service):
    """BFF forwards room type detail request to Room service."""
    mock_instance = mock_room_service._instance
    mock_instance.get = AsyncMock(
        return_value=mock_httpx_response(200, MOCK_DETAIL_RESPONSE)
    )

    room_type_id = "00000000-0000-0000-0000-000000000001"
    resp = await gateway_client.get(
        f"/api/v1/search/room-types/{room_type_id}",
        params={"check_in": "2026-04-01", "check_out": "2026-04-03"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Deluxe King"
    assert data["nights"] == 2
    mock_instance.get.assert_called_once()


async def test_bff_pricing_calendar(gateway_client, mock_room_service):
    """BFF forwards pricing calendar request to Room service."""
    mock_instance = mock_room_service._instance
    mock_instance.get = AsyncMock(
        return_value=mock_httpx_response(200, MOCK_CALENDAR_RESPONSE)
    )

    resp = await gateway_client.get(
        "/api/v1/search/calendar",
        params={"guests": 2},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "months" in data
    mock_instance.get.assert_called_once()


async def test_bff_forwards_query_params(gateway_client, mock_room_service):
    """BFF forwards all query parameters to Room service."""
    mock_instance = mock_room_service._instance
    mock_instance.get = AsyncMock(
        return_value=mock_httpx_response(200, MOCK_SEARCH_RESPONSE)
    )

    resp = await gateway_client.get(
        "/api/v1/search/availability",
        params={
            "check_in": "2026-04-01",
            "check_out": "2026-04-03",
            "guests": 2,
            "min_price": "100",
            "max_price": "500",
            "amenities": "wifi,pool",
            "sort": "price_asc",
        },
    )

    assert resp.status_code == 200

    # Verify the mock was called with correct params forwarded
    call_args = mock_instance.get.call_args
    called_params = call_args.kwargs.get("params", {}) or (call_args[1].get("params", {}) if len(call_args) > 1 else {})
    assert called_params["check_in"] == "2026-04-01"
    assert called_params["check_out"] == "2026-04-03"
    assert called_params["guests"] == 2
    assert called_params["min_price"] == "100"
    assert called_params["max_price"] == "500"
    assert called_params["amenities"] == "wifi,pool"
    assert called_params["sort"] == "price_asc"


async def test_bff_error_passthrough(gateway_client, mock_room_service):
    """BFF passes through error responses from Room service."""
    error_body = {"detail": "Invalid date range: check_out must be after check_in"}
    mock_instance = mock_room_service._instance
    mock_instance.get = AsyncMock(
        return_value=mock_httpx_response(400, error_body)
    )

    resp = await gateway_client.get(
        "/api/v1/search/availability",
        params={"check_in": "2026-04-03", "check_out": "2026-04-01", "guests": 2},
    )

    assert resp.status_code == 400
    data = resp.json()
    assert "Invalid date range" in data["detail"]
