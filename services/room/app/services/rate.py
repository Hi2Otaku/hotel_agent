"""Rate CRUD operations and multiplicative price calculation engine.

All monetary calculations use Decimal, never float.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rate import BaseRate, SeasonalRate, WeekendSurcharge
from app.models.room_type import RoomType
from app.schemas.rate import (
    BaseRateCreate,
    BaseRateUpdate,
    SeasonalRateCreate,
    SeasonalRateUpdate,
    WeekendSurchargeCreate,
    WeekendSurchargeUpdate,
)

TWO_PLACES = Decimal("0.01")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _validate_room_type_exists(db: AsyncSession, room_type_id: uuid.UUID) -> None:
    """Raise 404 if room_type_id does not exist."""
    result = await db.execute(
        select(RoomType.id).where(RoomType.id == room_type_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room type not found",
        )


# ---------------------------------------------------------------------------
# BaseRate CRUD
# ---------------------------------------------------------------------------


async def create_base_rate(db: AsyncSession, data: BaseRateCreate) -> BaseRate:
    """Create a base rate. Validates room type exists and no overlapping occupancy."""
    await _validate_room_type_exists(db, data.room_type_id)

    # Check overlapping occupancy range for same room type
    overlap_q = select(BaseRate).where(
        BaseRate.room_type_id == data.room_type_id,
        BaseRate.min_occupancy <= data.max_occupancy,
        BaseRate.max_occupancy >= data.min_occupancy,
    )
    result = await db.execute(overlap_q)
    if result.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Overlapping occupancy range for this room type",
        )

    rate = BaseRate(
        room_type_id=data.room_type_id,
        min_occupancy=data.min_occupancy,
        max_occupancy=data.max_occupancy,
        amount=data.amount,
        currency=data.currency,
    )
    db.add(rate)
    await db.commit()
    await db.refresh(rate)
    return rate


async def get_base_rates(
    db: AsyncSession, room_type_id: uuid.UUID
) -> list[BaseRate]:
    """List all base rates for a room type, ordered by min_occupancy."""
    result = await db.execute(
        select(BaseRate)
        .where(BaseRate.room_type_id == room_type_id)
        .order_by(BaseRate.min_occupancy)
    )
    return list(result.scalars().all())


async def update_base_rate(
    db: AsyncSession, rate_id: uuid.UUID, data: BaseRateUpdate
) -> BaseRate:
    """Update non-None fields on a base rate."""
    result = await db.execute(select(BaseRate).where(BaseRate.id == rate_id))
    rate = result.scalar_one_or_none()
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Base rate not found"
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rate, field, value)
    await db.commit()
    await db.refresh(rate)
    return rate


async def delete_base_rate(db: AsyncSession, rate_id: uuid.UUID) -> None:
    """Hard delete a base rate."""
    result = await db.execute(select(BaseRate).where(BaseRate.id == rate_id))
    rate = result.scalar_one_or_none()
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Base rate not found"
        )
    await db.delete(rate)
    await db.commit()


# ---------------------------------------------------------------------------
# SeasonalRate CRUD
# ---------------------------------------------------------------------------


async def create_seasonal_rate(
    db: AsyncSession, data: SeasonalRateCreate
) -> SeasonalRate:
    """Create a seasonal rate. Validates dates and room type."""
    if data.end_date <= data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date",
        )
    await _validate_room_type_exists(db, data.room_type_id)

    rate = SeasonalRate(
        room_type_id=data.room_type_id,
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        multiplier=data.multiplier,
    )
    db.add(rate)
    await db.commit()
    await db.refresh(rate)
    return rate


async def get_seasonal_rates(
    db: AsyncSession, room_type_id: uuid.UUID
) -> list[SeasonalRate]:
    """List active seasonal rates for a room type."""
    result = await db.execute(
        select(SeasonalRate).where(
            SeasonalRate.room_type_id == room_type_id,
            SeasonalRate.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def update_seasonal_rate(
    db: AsyncSession, rate_id: uuid.UUID, data: SeasonalRateUpdate
) -> SeasonalRate:
    """Update non-None fields on a seasonal rate."""
    result = await db.execute(
        select(SeasonalRate).where(SeasonalRate.id == rate_id)
    )
    rate = result.scalar_one_or_none()
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seasonal rate not found",
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rate, field, value)
    await db.commit()
    await db.refresh(rate)
    return rate


async def delete_seasonal_rate(db: AsyncSession, rate_id: uuid.UUID) -> None:
    """Hard delete a seasonal rate."""
    result = await db.execute(
        select(SeasonalRate).where(SeasonalRate.id == rate_id)
    )
    rate = result.scalar_one_or_none()
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seasonal rate not found",
        )
    await db.delete(rate)
    await db.commit()


# ---------------------------------------------------------------------------
# WeekendSurcharge CRUD
# ---------------------------------------------------------------------------


async def create_weekend_surcharge(
    db: AsyncSession, data: WeekendSurchargeCreate
) -> WeekendSurcharge:
    """Create a weekend surcharge."""
    await _validate_room_type_exists(db, data.room_type_id)

    surcharge = WeekendSurcharge(
        room_type_id=data.room_type_id,
        multiplier=data.multiplier,
        days=data.days,
    )
    db.add(surcharge)
    await db.commit()
    await db.refresh(surcharge)
    return surcharge


async def get_weekend_surcharges(
    db: AsyncSession, room_type_id: uuid.UUID
) -> list[WeekendSurcharge]:
    """List active weekend surcharges for a room type."""
    result = await db.execute(
        select(WeekendSurcharge).where(
            WeekendSurcharge.room_type_id == room_type_id,
            WeekendSurcharge.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def update_weekend_surcharge(
    db: AsyncSession, rate_id: uuid.UUID, data: WeekendSurchargeUpdate
) -> WeekendSurcharge:
    """Update non-None fields on a weekend surcharge."""
    result = await db.execute(
        select(WeekendSurcharge).where(WeekendSurcharge.id == rate_id)
    )
    surcharge = result.scalar_one_or_none()
    if surcharge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekend surcharge not found",
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(surcharge, field, value)
    await db.commit()
    await db.refresh(surcharge)
    return surcharge


async def delete_weekend_surcharge(
    db: AsyncSession, rate_id: uuid.UUID
) -> None:
    """Hard delete a weekend surcharge."""
    result = await db.execute(
        select(WeekendSurcharge).where(WeekendSurcharge.id == rate_id)
    )
    surcharge = result.scalar_one_or_none()
    if surcharge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekend surcharge not found",
        )
    await db.delete(surcharge)
    await db.commit()


# ---------------------------------------------------------------------------
# Price Calculation Engine
# ---------------------------------------------------------------------------


async def get_base_rate_for_occupancy(
    db: AsyncSession, room_type_id: uuid.UUID, occupancy: int
) -> Decimal:
    """Find the base rate tier that covers this occupancy count.

    Raises 404 if no matching tier.
    """
    result = await db.execute(
        select(BaseRate).where(
            BaseRate.room_type_id == room_type_id,
            BaseRate.min_occupancy <= occupancy,
            BaseRate.max_occupancy >= occupancy,
        )
    )
    rate = result.scalar_one_or_none()
    if rate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No base rate found for occupancy {occupancy}",
        )
    return Decimal(str(rate.amount))


async def get_seasonal_multiplier(
    db: AsyncSession, room_type_id: uuid.UUID, target_date: date
) -> Decimal:
    """Find active seasonal rate covering target_date.

    Returns multiplier if found, Decimal("1.00") if no seasonal rate applies.
    """
    result = await db.execute(
        select(SeasonalRate).where(
            SeasonalRate.room_type_id == room_type_id,
            SeasonalRate.is_active.is_(True),
            SeasonalRate.start_date <= target_date,
            SeasonalRate.end_date >= target_date,
        )
        .order_by(SeasonalRate.start_date.desc())
        .limit(1)
    )
    seasonal = result.scalar_one_or_none()
    if seasonal is None:
        return Decimal("1.00")
    return Decimal(str(seasonal.multiplier))


async def get_weekend_multiplier(
    db: AsyncSession, room_type_id: uuid.UUID, target_date: date
) -> Decimal:
    """Check if target_date.weekday() is in any active weekend surcharge's days list.

    Returns multiplier if found, Decimal("1.00") if not.
    """
    result = await db.execute(
        select(WeekendSurcharge).where(
            WeekendSurcharge.room_type_id == room_type_id,
            WeekendSurcharge.is_active.is_(True),
        )
    )
    surcharges = result.scalars().all()
    weekday = target_date.weekday()
    for surcharge in surcharges:
        if weekday in surcharge.days:
            return Decimal(str(surcharge.multiplier))
    return Decimal("1.00")


async def calculate_nightly_rate(
    db: AsyncSession,
    room_type_id: uuid.UUID,
    target_date: date,
    occupancy: int,
) -> dict:
    """Calculate rate for one night with full breakdown.

    Returns {"base_amount", "seasonal_multiplier", "weekend_multiplier", "final_amount"}
    using multiplicative stacking: final = base * seasonal * weekend.
    """
    base_amount = await get_base_rate_for_occupancy(db, room_type_id, occupancy)
    seasonal_multiplier = await get_seasonal_multiplier(db, room_type_id, target_date)
    weekend_multiplier = await get_weekend_multiplier(db, room_type_id, target_date)

    final_amount = (base_amount * seasonal_multiplier * weekend_multiplier).quantize(
        TWO_PLACES
    )

    return {
        "base_amount": base_amount,
        "seasonal_multiplier": seasonal_multiplier,
        "weekend_multiplier": weekend_multiplier,
        "final_amount": final_amount,
    }


async def calculate_stay_price(
    db: AsyncSession,
    room_type_id: uuid.UUID,
    check_in: date,
    check_out: date,
    occupancy: int,
) -> dict:
    """Calculate total price for a date range.

    Iterates each night from check_in to check_out-1 (check_out is departure day).
    Returns {"currency", "nightly_rates", "total"}.
    """
    nightly_rates = []
    total = Decimal("0.00")

    current = check_in
    while current < check_out:
        night = await calculate_nightly_rate(db, room_type_id, current, occupancy)
        nightly_rates.append(
            {
                "date": current,
                "base_amount": night["base_amount"],
                "seasonal_multiplier": night["seasonal_multiplier"],
                "weekend_multiplier": night["weekend_multiplier"],
                "final_amount": night["final_amount"],
            }
        )
        total += night["final_amount"]
        current += timedelta(days=1)

    # Get currency from base rate
    result = await db.execute(
        select(BaseRate.currency).where(BaseRate.room_type_id == room_type_id).limit(1)
    )
    currency = result.scalar_one_or_none() or "USD"

    return {
        "currency": currency,
        "nightly_rates": nightly_rates,
        "total": total.quantize(TWO_PLACES),
    }
