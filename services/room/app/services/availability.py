"""Availability query service -- overlap detection and search logic.

Core functions:
- effective_capacity: physical rooms + overbooking buffer
- get_available_count: count available rooms for a room type and date range
- search_available_room_types: full search with filtering and scoring
- compute_sort_score: recommended sort scoring formula
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import ReservationProjection
from app.models.room import Room
from app.models.room_type import RoomType
from app.models.rate import BaseRate
from app.services.rate import get_base_rate_for_occupancy, calculate_stay_price

BLOCKING_STATUSES = ["pending", "confirmed", "checked_in"]


def effective_capacity(physical_count: int, overbooking_pct: Decimal) -> int:
    """Calculate effective room capacity including overbooking buffer.

    Args:
        physical_count: Number of physical rooms of this type.
        overbooking_pct: Overbooking percentage (e.g. 10.00 means 10%).

    Returns:
        Effective capacity (integer, rounded down).
    """
    return int(physical_count * (1 + overbooking_pct / Decimal("100")))


async def get_available_count(
    db: AsyncSession,
    room_type_id: uuid.UUID,
    check_in: date,
    check_out: date,
) -> tuple[int, int]:
    """Count available rooms for a room type in a date range.

    Uses half-open interval overlap detection:
    A reservation overlaps if its check_in < requested check_out
    AND its check_out > requested check_in.

    Args:
        db: Database session.
        room_type_id: Room type to check.
        check_in: Requested check-in date.
        check_out: Requested check-out date.

    Returns:
        Tuple of (available_count, total_physical_rooms).
    """
    # Count active physical rooms of this type
    total_result = await db.execute(
        select(func.count()).select_from(Room).where(
            and_(
                Room.room_type_id == room_type_id,
                Room.is_active.is_(True),
            )
        )
    )
    total = total_result.scalar() or 0

    # Count blocking reservations that overlap the requested dates
    blocking_result = await db.execute(
        select(func.count()).select_from(ReservationProjection).where(
            and_(
                ReservationProjection.room_type_id == room_type_id,
                ReservationProjection.status.in_(BLOCKING_STATUSES),
                ReservationProjection.check_in < check_out,
                ReservationProjection.check_out > check_in,
            )
        )
    )
    blocking = blocking_result.scalar() or 0

    # Get overbooking percentage
    ob_result = await db.execute(
        select(RoomType.overbooking_pct).where(RoomType.id == room_type_id)
    )
    overbooking_pct = ob_result.scalar() or Decimal("0.00")

    capacity = effective_capacity(total, overbooking_pct)
    available = max(capacity - blocking, 0)

    return (available, total)


def compute_sort_score(
    price_per_night: Decimal,
    max_price_in_results: Decimal,
    available_count: int,
    total_count: int,
    capacity_match: float,
) -> float:
    """Compute a recommended sort score for search results.

    Weights: price 40%, availability 30%, capacity match 30%.
    Lower price and higher availability score better.

    Args:
        price_per_night: Nightly rate for this room type.
        max_price_in_results: Highest price across all results (for normalization).
        available_count: Number of available rooms.
        total_count: Total physical rooms.
        capacity_match: Guest-to-capacity ratio (0.0 to 1.0).

    Returns:
        Score as float (higher = better match).
    """
    price_score = (
        1.0 - float(price_per_night / max_price_in_results)
        if max_price_in_results > 0
        else 0.5
    )
    avail_score = min(available_count / max(total_count, 1), 1.0)
    cap_score = capacity_match
    return (price_score * 0.4) + (avail_score * 0.3) + (cap_score * 0.3)


async def search_available_room_types(
    db: AsyncSession,
    check_in: date,
    check_out: date,
    guests: int,
    room_type_id: uuid.UUID | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    amenities: list[str] | None = None,
) -> list[dict]:
    """Search for available room types matching criteria.

    Args:
        db: Database session.
        check_in: Requested check-in date.
        check_out: Requested check-out date (must be after check_in).
        guests: Number of guests.
        room_type_id: Optional filter for a specific room type.
        min_price: Optional minimum price per night filter.
        max_price: Optional maximum price per night filter.
        amenities: Optional list of required amenity keys.

    Returns:
        List of result dicts with keys matching SearchResult schema:
        room_type_id, name, slug, description, photo_url, price_per_night,
        total_price, currency, max_adults, max_children, bed_config,
        amenity_highlights, available_count, total_rooms.
    """
    if check_in >= check_out:
        raise ValueError("check_in must be before check_out")
    if guests < 1:
        raise ValueError("guests must be at least 1")

    # Query active room types that can hold the guest count
    query = select(RoomType).where(
        and_(
            RoomType.is_active.is_(True),
            (RoomType.max_adults + RoomType.max_children) >= guests,
        )
    )
    if room_type_id is not None:
        query = query.where(RoomType.id == room_type_id)

    result = await db.execute(query)
    room_types = list(result.scalars().all())

    # Build raw results with availability and pricing
    raw_results = []
    for rt in room_types:
        available, total = await get_available_count(db, rt.id, check_in, check_out)
        if available == 0:
            continue

        # Get pricing
        try:
            price_per_night = await get_base_rate_for_occupancy(db, rt.id, guests)
        except Exception:
            # No rate configured for this occupancy -- skip
            continue

        try:
            stay_price = await calculate_stay_price(
                db, rt.id, check_in, check_out, guests
            )
            total_price = stay_price["total"]
            currency = stay_price["currency"]
        except Exception:
            total_price = price_per_night * (check_out - check_in).days
            currency = "USD"

        # Apply price filters
        if min_price is not None and price_per_night < min_price:
            continue
        if max_price is not None and price_per_night > max_price:
            continue

        # Apply amenity filter
        if amenities:
            rt_amenity_keys = set()
            if isinstance(rt.amenities, dict):
                rt_amenity_keys = set(rt.amenities.keys())
            if not all(a in rt_amenity_keys for a in amenities):
                continue

        # Extract photo_url (singular, first element or None)
        photo_url = rt.photo_urls[0] if rt.photo_urls else None

        # Extract amenity_highlights (top 5 amenity keys)
        amenity_highlights = list(rt.amenities.keys())[:5] if isinstance(rt.amenities, dict) else []

        # Capacity match score
        capacity_match = min(guests / max(rt.max_adults, 1), 1.0)

        raw_results.append({
            "room_type_id": rt.id,
            "name": rt.name,
            "slug": rt.slug,
            "description": rt.description,
            "photo_url": photo_url,
            "price_per_night": price_per_night,
            "total_price": total_price,
            "currency": currency,
            "max_adults": rt.max_adults,
            "max_children": rt.max_children,
            "bed_config": rt.bed_config,
            "amenity_highlights": amenity_highlights,
            "available_count": available,
            "total_rooms": total,
            "_capacity_match": capacity_match,
        })

    if not raw_results:
        return []

    # Compute sort scores
    max_price_in_results = max(r["price_per_night"] for r in raw_results)
    for r in raw_results:
        r["_score"] = compute_sort_score(
            r["price_per_night"],
            max_price_in_results,
            r["available_count"],
            r["total_rooms"],
            r["_capacity_match"],
        )

    # Sort by score descending
    raw_results.sort(key=lambda r: r["_score"], reverse=True)

    # Remove internal keys before returning
    for r in raw_results:
        del r["_score"]
        del r["_capacity_match"]

    return raw_results
