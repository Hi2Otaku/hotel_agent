"""Tests for the tool executor with mocked httpx calls."""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.services.tool_executor import ToolExecutor


@pytest.fixture
def executor():
    return ToolExecutor(auth_token="test-jwt-token")


@pytest.mark.asyncio
async def test_search_rooms_calls_room_service(executor):
    """search_rooms should call room service availability endpoint."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{"name": "Deluxe", "available": 3}]
    mock_response.raise_for_status = MagicMock()

    with patch("app.services.tool_executor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await executor.execute("search_rooms", {
            "check_in": "2026-04-01",
            "check_out": "2026-04-03",
            "guests": 2,
        })

    assert result["success"] is True
    assert result["data"] == [{"name": "Deluxe", "available": 3}]


@pytest.mark.asyncio
async def test_create_booking_forwards_auth_token(executor):
    """create_booking should forward the JWT in Authorization header."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "123", "status": "confirmed"}
    mock_response.raise_for_status = MagicMock()

    with patch("app.services.tool_executor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await executor.execute("create_booking", {
            "room_type_id": "rt-1",
            "check_in": "2026-04-01",
            "check_out": "2026-04-03",
            "guests": 2,
            "guest_name": "Test Guest",
            "guest_email": "test@example.com",
        })

    assert result["success"] is True
    # Verify auth header was set in constructor
    assert executor._headers["Authorization"] == "Bearer test-jwt-token"


@pytest.mark.asyncio
async def test_timeout_returns_error(executor):
    """Timeout should return a structured error, not crash."""
    import httpx as httpx_mod

    with patch("app.services.tool_executor.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx_mod.TimeoutException("timed out"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await executor.execute("search_rooms", {
            "check_in": "2026-04-01",
            "check_out": "2026-04-03",
            "guests": 2,
        })

    assert result["success"] is False
    assert "timed out" in result["error"].lower() or "timeout" in result["error"].lower()


@pytest.mark.asyncio
async def test_unknown_tool_returns_error(executor):
    """Unknown tool names should return an error, not crash."""
    result = await executor.execute("nonexistent_tool", {})
    assert result["success"] is False
    assert "Unknown tool" in result["error"]
