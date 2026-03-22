"""Tests for the prompt builder with mocked room service data."""

from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.services.prompt_builder import PromptBuilder


@pytest.fixture
def builder():
    return PromptBuilder()


def _mock_room_types_response():
    """Create a mock httpx response with room type data."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {
            "name": "Standard",
            "price_per_night": 100,
            "max_guests": 2,
            "amenities": ["WiFi", "TV", "Mini-bar"],
        },
        {
            "name": "Deluxe Suite",
            "price_per_night": 250,
            "max_guests": 4,
            "amenities": ["WiFi", "TV", "Mini-bar", "Balcony", "Jacuzzi"],
        },
    ]
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@pytest.mark.asyncio
async def test_guest_prompt_contains_hotel_info(builder):
    """Guest prompt should contain HotelBook hotel info."""
    with patch("app.services.prompt_builder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=_mock_room_types_response())
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        prompt = await builder.build_system_prompt("guest")

    assert "HotelBook Assistant" in prompt
    assert "HotelBook" in prompt
    assert "3:00 PM" in prompt
    assert "11:00 AM" in prompt


@pytest.mark.asyncio
async def test_staff_prompt_contains_ops_language(builder):
    """Staff prompt should use HB Ops persona."""
    with patch("app.services.prompt_builder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=_mock_room_types_response())
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        prompt = await builder.build_system_prompt("staff")

    assert "HB Ops" in prompt
    assert "operations" in prompt.lower()


@pytest.mark.asyncio
async def test_prompt_includes_room_types(builder):
    """Prompt should include room type names and prices from service."""
    with patch("app.services.prompt_builder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=_mock_room_types_response())
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        prompt = await builder.build_system_prompt("guest")

    assert "Standard" in prompt
    assert "Deluxe Suite" in prompt
    assert "$100" in prompt
    assert "$250" in prompt


@pytest.mark.asyncio
async def test_prompt_contains_language_instruction(builder):
    """Prompt must instruct the bot to respond in the same language the user writes in."""
    with patch("app.services.prompt_builder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=_mock_room_types_response())
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        guest_prompt = await builder.build_system_prompt("guest")

    # Clear cache to test staff too
    builder._cache.clear()

    with patch("app.services.prompt_builder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=_mock_room_types_response())
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        staff_prompt = await builder.build_system_prompt("staff")

    assert "same language the user writes in" in guest_prompt
    assert "same language the user writes in" in staff_prompt


@pytest.mark.asyncio
async def test_prompt_caching(builder):
    """Second call should use cached prompt without calling room service."""
    with patch("app.services.prompt_builder.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=_mock_room_types_response())
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        prompt1 = await builder.build_system_prompt("guest")
        prompt2 = await builder.build_system_prompt("guest")

    assert prompt1 == prompt2
    # httpx.AsyncClient should only be called once due to caching
    assert mock_cls.call_count == 1
