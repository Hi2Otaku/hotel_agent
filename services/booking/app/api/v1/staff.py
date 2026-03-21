"""Staff-only booking API endpoints.

Provides endpoints for staff to manage all bookings: list, search,
today's arrivals/departures, check-in, check-out, cancel, and by-user lookup.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.schemas.booking import BookingListResponse, BookingResponse
from app.services.staff import (
    check_in_guest,
    check_out_guest,
    get_bookings_by_user,
    get_today_bookings,
    list_all_bookings,
    staff_cancel_booking,
)

router = APIRouter(prefix="/api/v1/bookings/staff", tags=["staff-bookings"])

require_staff = require_role("admin", "manager", "front_desk")


class CheckInRequest(BaseModel):
    """Request body for check-in with room assignment."""

    room_id: uuid.UUID


@router.get("/", response_model=BookingListResponse)
async def list_all_bookings_endpoint(
    search: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = Query(default=12, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """List all bookings with optional search, status filter, and date range."""
    bookings, total = await list_all_bookings(
        db,
        search=search,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return BookingListResponse(
        items=[BookingResponse.model_validate(b) for b in bookings],
        total=total,
    )


@router.get("/today")
async def today_bookings_endpoint(
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Get today's arrivals and departures."""
    data = await get_today_bookings(db)
    return {
        "arrivals": [BookingResponse.model_validate(b).model_dump(mode="json") for b in data["arrivals"]],
        "departures": [BookingResponse.model_validate(b).model_dump(mode="json") for b in data["departures"]],
    }


@router.post("/{booking_id}/check-in", response_model=BookingResponse)
async def check_in_endpoint(
    booking_id: uuid.UUID,
    data: CheckInRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Check in a guest with room assignment."""
    booking = await check_in_guest(db, booking_id, data.room_id)
    return booking


@router.post("/{booking_id}/check-out", response_model=BookingResponse)
async def check_out_endpoint(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Check out a guest."""
    booking = await check_out_guest(db, booking_id)
    return booking


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_endpoint(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Cancel a booking as staff."""
    booking = await staff_cancel_booking(db, booking_id)
    return booking


@router.get("/by-user/{user_id}", response_model=BookingListResponse)
async def bookings_by_user_endpoint(
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(require_staff),
):
    """Get all bookings for a specific user."""
    bookings, total = await get_bookings_by_user(db, user_id, skip=skip, limit=limit)
    return BookingListResponse(
        items=[BookingResponse.model_validate(b) for b in bookings],
        total=total,
    )
