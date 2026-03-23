"""Gateway service test fixtures with httpx mocking for backend services."""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def mock_httpx_response(status_code=200, json_data=None):
    """Create a mock httpx.Response object."""
    content = json.dumps(json_data).encode() if json_data is not None else b""
    return httpx.Response(
        status_code=status_code,
        content=content,
        request=httpx.Request("GET", "http://mock"),
    )


MOCK_SEARCH_RESPONSE = {
    "results": [
        {
            "room_type_id": "00000000-0000-0000-0000-000000000001",
            "name": "Deluxe King",
            "slug": "deluxe-king",
            "description": "A deluxe king room",
            "base_price": "200.00",
            "price_per_night": "200.00",
            "available_count": 3,
            "max_guests": 2,
            "photo_url": "/photos/deluxe.jpg",
            "amenity_highlights": ["wifi", "minibar"],
        }
    ],
    "total": 1,
    "check_in": "2026-04-01",
    "check_out": "2026-04-03",
    "guests": 2,
}

MOCK_DETAIL_RESPONSE = {
    "room_type_id": "00000000-0000-0000-0000-000000000001",
    "name": "Deluxe King",
    "slug": "deluxe-king",
    "description": "A deluxe king room",
    "base_price": "200.00",
    "price_per_night": "200.00",
    "total_price": "400.00",
    "nights": 2,
    "available_count": 3,
    "max_guests": 2,
    "amenities": ["wifi", "minibar"],
    "photos": ["/photos/deluxe.jpg"],
    "bed_config": {"king": 1},
}

MOCK_CALENDAR_RESPONSE = {
    "room_type_id": "00000000-0000-0000-0000-000000000001",
    "months": [
        {
            "year": 2026,
            "month": 4,
            "days": [
                {"date": "2026-04-01", "price": "200.00", "available": True, "min_stay": 1}
            ],
        }
    ],
}


@pytest.fixture
async def gateway_client():
    """Gateway test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_room_service():
    """Mock httpx.AsyncClient to intercept calls to Room service.

    Yields a mock that can be configured with custom responses.
    The mock intercepts the context manager and .get() calls.
    """
    mock_response = mock_httpx_response(200, MOCK_SEARCH_RESPONSE)

    mock_client_instance = AsyncMock()
    mock_client_instance.get = AsyncMock(return_value=mock_response)
    mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("app.api.search.httpx.AsyncClient", return_value=mock_client_instance) as mock_cls:
        mock_cls._instance = mock_client_instance
        yield mock_cls
