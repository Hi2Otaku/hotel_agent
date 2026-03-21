"""Gateway BFF search aggregation endpoints.

Forwards guest search requests to the Room service. All endpoints are public
(no auth required) -- guests search without logging in.
"""

import uuid
from datetime import date
from decimal import Decimal

import httpx
from fastapi import APIRouter, Query, Response

from app.core.config import settings

router = APIRouter(tags=["search"])


@router.get("/api/v1/search/availability")
async def search_availability(
    check_in: date = Query(...),
    check_out: date = Query(...),
    guests: int = Query(..., ge=1),
    room_type_id: uuid.UUID | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    amenities: str | None = None,
    sort: str = "recommended",
):
    """Search available rooms. Public, no auth required. Forwards to Room service."""
    params: dict = {
        "check_in": str(check_in),
        "check_out": str(check_out),
        "guests": guests,
        "sort": sort,
    }
    if room_type_id:
        params["room_type_id"] = str(room_type_id)
    if min_price is not None:
        params["min_price"] = str(min_price)
    if max_price is not None:
        params["max_price"] = str(max_price)
    if amenities:
        params["amenities"] = amenities
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{settings.ROOM_SERVICE_URL}/api/v1/search/availability",
            params=params,
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
    )


@router.get("/api/v1/search/room-types/{room_type_id}")
async def room_type_detail(
    room_type_id: uuid.UUID,
    check_in: date = Query(...),
    check_out: date = Query(...),
    guests: int = Query(2, ge=1),
):
    """Get room type details with pricing. Public, no auth required."""
    params: dict = {
        "check_in": str(check_in),
        "check_out": str(check_out),
        "guests": guests,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{settings.ROOM_SERVICE_URL}/api/v1/search/room-types/{room_type_id}",
            params=params,
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
    )


@router.get("/api/v1/search/calendar")
async def pricing_calendar(
    room_type_id: uuid.UUID | None = None,
    guests: int = Query(2, ge=1),
    months: int = Query(6, ge=1, le=12),
):
    """Get pricing calendar. Public, no auth required."""
    params: dict = {"guests": guests, "months": months}
    if room_type_id:
        params["room_type_id"] = str(room_type_id)
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(
            f"{settings.ROOM_SERVICE_URL}/api/v1/search/calendar",
            params=params,
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
    )
