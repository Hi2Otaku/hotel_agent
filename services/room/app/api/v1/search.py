"""Public search, room detail, and pricing calendar endpoints.

All endpoints are public (no auth required) -- only get_db dependency.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.room_type import RoomType
from app.schemas.availability import (
    CalendarDay,
    CalendarResponse,
    NightlyRate,
    RoomTypeDetail,
    SearchResponse,
    SearchResult,
)
from app.services.availability import get_available_count, search_available_room_types
from app.services.rate import (
    TWO_PLACES,
    calculate_stay_price,
    get_base_rate_for_occupancy,
    get_base_rates,
    get_seasonal_rates,
    get_weekend_surcharges,
)

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/availability", response_model=SearchResponse)
async def search_availability(
    check_in: date = Query(...),
    check_out: date = Query(...),
    guests: int = Query(..., ge=1),
    room_type_id: uuid.UUID | None = Query(None),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    amenities: str | None = Query(None),
    sort: str = Query("recommended"),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """Search for available room types by dates, guest count, and optional filters.

    Public endpoint -- no authentication required.
    """
    today = date.today()
    if check_in < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_in cannot be in the past",
        )
    if check_in >= check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_in must be before check_out",
        )

    amenities_list = (
        [a.strip() for a in amenities.split(",") if a.strip()] if amenities else None
    )

    results = await search_available_room_types(
        db,
        check_in,
        check_out,
        guests,
        room_type_id,
        min_price,
        max_price,
        amenities_list,
    )

    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        total=len(results),
        check_in=check_in,
        check_out=check_out,
        guests=guests,
    )


@router.get("/room-types/{room_type_id}", response_model=RoomTypeDetail)
async def room_type_detail(
    room_type_id: uuid.UUID,
    check_in: date = Query(...),
    check_out: date = Query(...),
    guests: int = Query(2, ge=1),
    db: AsyncSession = Depends(get_db),
) -> RoomTypeDetail:
    """Get full room type detail with pricing for selected dates.

    Public endpoint -- no authentication required.
    """
    if check_in >= check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="check_in must be before check_out",
        )

    # Fetch room type
    result = await db.execute(
        select(RoomType).where(
            RoomType.id == room_type_id,
            RoomType.is_active.is_(True),
        )
    )
    rt = result.scalar_one_or_none()
    if rt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )

    # Availability
    available_count, total_rooms = await get_available_count(
        db, room_type_id, check_in, check_out
    )

    # Pricing
    price_per_night = await get_base_rate_for_occupancy(db, room_type_id, guests)
    stay_price = await calculate_stay_price(db, room_type_id, check_in, check_out, guests)

    nightly_rates = [
        NightlyRate(
            date=nr["date"],
            base_amount=nr["base_amount"],
            seasonal_multiplier=nr["seasonal_multiplier"],
            weekend_multiplier=nr["weekend_multiplier"],
            final_amount=nr["final_amount"],
        )
        for nr in stay_price["nightly_rates"]
    ]

    return RoomTypeDetail(
        id=rt.id,
        name=rt.name,
        slug=rt.slug,
        description=rt.description,
        max_adults=rt.max_adults,
        max_children=rt.max_children,
        bed_config=rt.bed_config,
        amenities=rt.amenities,
        photo_urls=rt.photo_urls,
        available_count=available_count,
        total_rooms=total_rooms,
        price_per_night=price_per_night,
        total_price=stay_price["total"],
        currency=stay_price["currency"],
        nightly_rates=nightly_rates,
    )


@router.get("/calendar", response_model=CalendarResponse)
async def pricing_calendar(
    room_type_id: uuid.UUID | None = Query(None),
    guests: int = Query(2, ge=1),
    months: int = Query(6, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
) -> CalendarResponse:
    """Get a pricing calendar showing per-night rates and availability.

    If room_type_id is not provided, uses the cheapest active room type.
    Public endpoint -- no authentication required.
    """
    rt = None

    if room_type_id is not None:
        result = await db.execute(
            select(RoomType).where(
                RoomType.id == room_type_id,
                RoomType.is_active.is_(True),
            )
        )
        rt = result.scalar_one_or_none()
        if rt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room type not found",
            )
    else:
        # Find cheapest active room type by lowest base rate
        from app.models.rate import BaseRate

        result = await db.execute(
            select(RoomType)
            .join(BaseRate, BaseRate.room_type_id == RoomType.id)
            .where(RoomType.is_active.is_(True))
            .order_by(BaseRate.amount)
            .limit(1)
        )
        rt = result.scalar_one_or_none()
        if rt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active room types with rates found",
            )

    rt_id = rt.id
    rt_name = rt.name

    # Batch-load rate data (3 queries total, not per-day)
    base_rates = await get_base_rates(db, rt_id)
    seasonal_rates = await get_seasonal_rates(db, rt_id)
    weekend_surcharges = await get_weekend_surcharges(db, rt_id)

    # Find base rate for the requested occupancy
    base_amount = Decimal("0.00")
    for br in base_rates:
        if br.min_occupancy <= guests <= br.max_occupancy:
            base_amount = Decimal(str(br.amount))
            break
    else:
        # Fallback: use lowest base rate if no occupancy match
        if base_rates:
            base_amount = Decimal(str(base_rates[0].amount))

    # Generate calendar days
    today = date.today()
    end_date = today + timedelta(days=months * 30)
    days: list[CalendarDay] = []

    current = today
    while current < end_date:
        # Seasonal multiplier for this day
        seasonal_mult = Decimal("1.00")
        for sr in seasonal_rates:
            if sr.start_date <= current <= sr.end_date:
                seasonal_mult = Decimal(str(sr.multiplier))
                break

        # Weekend multiplier for this day
        weekend_mult = Decimal("1.00")
        weekday = current.weekday()
        for ws in weekend_surcharges:
            if weekday in ws.days:
                weekend_mult = Decimal(str(ws.multiplier))
                break

        final_rate = (base_amount * seasonal_mult * weekend_mult).quantize(TWO_PLACES)

        # Single-day availability
        avail_count, total_rooms = await get_available_count(
            db, rt_id, current, current + timedelta(days=1)
        )

        # Availability indicator
        if avail_count == 0 or total_rooms == 0:
            indicator = "red"
        elif avail_count / total_rooms >= 0.5:
            indicator = "green"
        elif avail_count / total_rooms >= 0.2:
            indicator = "yellow"
        else:
            indicator = "red"

        days.append(
            CalendarDay(
                date=current,
                rate=final_rate,
                base_amount=base_amount,
                seasonal_multiplier=seasonal_mult,
                weekend_multiplier=weekend_mult,
                available_count=avail_count,
                total_rooms=total_rooms,
                availability_indicator=indicator,
            )
        )

        current += timedelta(days=1)

    return CalendarResponse(
        room_type_id=rt_id,
        room_type_name=rt_name,
        start_date=today,
        end_date=end_date,
        days=days,
    )
