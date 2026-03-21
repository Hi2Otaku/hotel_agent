"""Staff-specific booking service functions.

Provides operations that bypass user ownership checks, allowing staff
to manage all bookings: list, search, filter, check-in, check-out, cancel.
"""

import logging
from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.services.booking import transition_booking

logger = logging.getLogger(__name__)


async def list_all_bookings(
    db: AsyncSession,
    search: str | None = None,
    status_filter: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 12,
) -> tuple[list[Booking], int]:
    """List ALL bookings with optional search, status filter, and date range.

    No user_id filter -- staff can see everything.

    Args:
        db: Async database session.
        search: Optional search term matched against guest name and confirmation number.
        status_filter: Optional booking status to filter by.
        date_from: Optional earliest check-in date.
        date_to: Optional latest check-in date.
        skip: Pagination offset.
        limit: Pagination limit.

    Returns:
        Tuple of (list of Booking instances, total count).
    """
    filters = []

    if search:
        search_term = f"%{search}%"
        filters.append(
            or_(
                Booking.guest_first_name.ilike(search_term),
                Booking.guest_last_name.ilike(search_term),
                Booking.confirmation_number.ilike(search_term),
            )
        )

    if status_filter:
        filters.append(Booking.status == status_filter)

    if date_from:
        filters.append(Booking.check_in >= date_from)

    if date_to:
        filters.append(Booking.check_in <= date_to)

    # Count query
    count_query = select(func.count()).select_from(Booking)
    if filters:
        count_query = count_query.where(*filters)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Data query
    query = select(Booking).order_by(Booking.created_at.desc()).offset(skip).limit(limit)
    if filters:
        query = query.where(*filters)
    result = await db.execute(query)
    bookings = list(result.scalars().all())

    return bookings, total


async def get_today_bookings(db: AsyncSession) -> dict:
    """Get today's arrivals and departures.

    Args:
        db: Async database session.

    Returns:
        Dict with 'arrivals' (confirmed bookings checking in today)
        and 'departures' (checked-in bookings checking out today).
    """
    today = date.today()

    # Arrivals: confirmed bookings with check_in = today
    arrivals_query = select(Booking).where(
        Booking.status == BookingStatus.CONFIRMED,
        Booking.check_in == today,
    )
    arrivals_result = await db.execute(arrivals_query)
    arrivals = list(arrivals_result.scalars().all())

    # Departures: checked-in bookings with check_out = today
    departures_query = select(Booking).where(
        Booking.status == BookingStatus.CHECKED_IN,
        Booking.check_out == today,
    )
    departures_result = await db.execute(departures_query)
    departures = list(departures_result.scalars().all())

    return {"arrivals": arrivals, "departures": departures}


async def check_in_guest(
    db: AsyncSession, booking_id: UUID, room_id: UUID
) -> Booking:
    """Check in a guest by assigning a room and transitioning to checked_in.

    Args:
        db: Async database session.
        booking_id: The booking UUID.
        room_id: The physical room UUID to assign.

    Returns:
        The updated Booking.

    Raises:
        HTTPException(404): Booking not found.
        HTTPException(400): Invalid state transition.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.room_id = room_id
    booking = await transition_booking(db, booking, "checked_in")
    return booking


async def check_out_guest(db: AsyncSession, booking_id: UUID) -> Booking:
    """Check out a guest by transitioning to checked_out.

    Args:
        db: Async database session.
        booking_id: The booking UUID.

    Returns:
        The updated Booking.

    Raises:
        HTTPException(404): Booking not found.
        HTTPException(400): Invalid state transition.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking = await transition_booking(db, booking, "checked_out")
    return booking


async def staff_cancel_booking(db: AsyncSession, booking_id: UUID) -> Booking:
    """Cancel a booking as staff.

    Args:
        db: Async database session.
        booking_id: The booking UUID.

    Returns:
        The cancelled Booking.

    Raises:
        HTTPException(404): Booking not found.
        HTTPException(400): Invalid state transition.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking = await transition_booking(db, booking, "cancelled", reason="staff_cancelled")
    return booking


async def get_bookings_by_user(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Booking], int]:
    """List bookings for a specific user (staff access, no ownership check).

    Args:
        db: Async database session.
        user_id: The user UUID to filter by.
        skip: Pagination offset.
        limit: Pagination limit.

    Returns:
        Tuple of (list of Booking instances, total count).
    """
    base_filter = [Booking.user_id == user_id]

    count_query = select(func.count()).select_from(Booking).where(*base_filter)
    total = (await db.execute(count_query)).scalar()

    query = (
        select(Booking)
        .where(*base_filter)
        .order_by(Booking.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    bookings = list(result.scalars().all())

    return bookings, total
