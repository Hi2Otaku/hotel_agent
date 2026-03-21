"""Pricing integration with Room service.

Fetches live pricing and room counts from the Room service API
via inter-service HTTP calls.
"""

import logging
import time
from decimal import Decimal
from datetime import date
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

# Simple in-memory cache for room counts (room_type_id -> (count, timestamp))
_room_count_cache: dict[str, tuple[int, float]] = {}
_CACHE_TTL_SECONDS = 60.0


async def get_pricing_from_room_service(
    room_type_id: UUID, check_in: date, check_out: date, guests: int
) -> dict:
    """Fetch pricing for a room type and date range from Room service.

    Args:
        room_type_id: The UUID of the room type.
        check_in: Check-in date.
        check_out: Check-out date.
        guests: Number of guests.

    Returns:
        Dict with total_price (Decimal), price_per_night (Decimal),
        currency (str), nightly_breakdown (list), room_type_name (str).

    Raises:
        HTTPException(502): If Room service is unreachable or returns an error.
    """
    url = (
        f"{settings.ROOM_SERVICE_URL}/api/v1/search/room-types/{room_type_id}"
        f"?check_in={check_in}&check_out={check_out}&guests={guests}"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        return {
            "total_price": Decimal(str(data["total_price"])),
            "price_per_night": Decimal(str(data["price_per_night"])),
            "currency": data["currency"],
            "nightly_breakdown": data.get("nightly_rates", []),
            "room_type_name": data.get("name", "Room"),
        }
    except httpx.HTTPError as exc:
        logger.exception("Failed to fetch pricing from Room service: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch pricing from Room service",
        )


async def get_room_count_for_type(room_type_id: UUID) -> int:
    """Get the total number of rooms for a room type.

    Results are cached for 60 seconds to reduce inter-service calls.

    Args:
        room_type_id: The UUID of the room type.

    Returns:
        The total number of rooms of this type.

    Raises:
        HTTPException(502): If Room service is unreachable.
    """
    cache_key = str(room_type_id)
    now = time.monotonic()

    # Check cache
    if cache_key in _room_count_cache:
        count, cached_at = _room_count_cache[cache_key]
        if now - cached_at < _CACHE_TTL_SECONDS:
            return count

    url = f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/types/{room_type_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        room_count = data.get("room_count", data.get("total_rooms", 1))
        _room_count_cache[cache_key] = (room_count, now)
        return room_count
    except httpx.HTTPError as exc:
        logger.exception("Failed to fetch room count from Room service: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch room information from Room service",
        )
