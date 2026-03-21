"""Rate management endpoints: base rates, seasonal rates, weekend surcharges, price calculation."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin, require_manager_or_above, require_staff
from app.schemas.rate import (
    BaseRateCreate,
    BaseRateResponse,
    BaseRateUpdate,
    PriceCalculationRequest,
    PriceCalculationResponse,
    SeasonalRateCreate,
    SeasonalRateResponse,
    SeasonalRateUpdate,
    WeekendSurchargeCreate,
    WeekendSurchargeResponse,
    WeekendSurchargeUpdate,
)
from app.services.rate import (
    calculate_stay_price,
    create_base_rate,
    create_seasonal_rate,
    create_weekend_surcharge,
    delete_base_rate,
    delete_seasonal_rate,
    delete_weekend_surcharge,
    get_base_rates,
    get_seasonal_rates,
    get_weekend_surcharges,
    update_base_rate,
    update_seasonal_rate,
    update_weekend_surcharge,
)

router = APIRouter(prefix="/api/v1/rooms/rates", tags=["rates"])

# ---------------------------------------------------------------------------
# Base Rate endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/base",
    response_model=BaseRateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_base_rate_endpoint(
    data: BaseRateCreate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_manager_or_above),
):
    """Create a base rate for a room type."""
    return await create_base_rate(db, data)


@router.get("/base/{room_type_id}", response_model=list[BaseRateResponse])
async def list_base_rates_endpoint(
    room_type_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_staff),
):
    """List base rates for a room type."""
    return await get_base_rates(db, room_type_id)


@router.patch("/base/{rate_id}", response_model=BaseRateResponse)
async def update_base_rate_endpoint(
    rate_id: uuid.UUID,
    data: BaseRateUpdate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_manager_or_above),
):
    """Update a base rate."""
    return await update_base_rate(db, rate_id, data)


@router.delete("/base/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_base_rate_endpoint(
    rate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_admin),
):
    """Delete a base rate."""
    await delete_base_rate(db, rate_id)


# ---------------------------------------------------------------------------
# Seasonal Rate endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/seasonal",
    response_model=SeasonalRateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_seasonal_rate_endpoint(
    data: SeasonalRateCreate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_manager_or_above),
):
    """Create a seasonal rate for a room type."""
    return await create_seasonal_rate(db, data)


@router.get("/seasonal/{room_type_id}", response_model=list[SeasonalRateResponse])
async def list_seasonal_rates_endpoint(
    room_type_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_staff),
):
    """List active seasonal rates for a room type."""
    return await get_seasonal_rates(db, room_type_id)


@router.patch("/seasonal/{rate_id}", response_model=SeasonalRateResponse)
async def update_seasonal_rate_endpoint(
    rate_id: uuid.UUID,
    data: SeasonalRateUpdate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_manager_or_above),
):
    """Update a seasonal rate."""
    return await update_seasonal_rate(db, rate_id, data)


@router.delete("/seasonal/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seasonal_rate_endpoint(
    rate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_admin),
):
    """Delete a seasonal rate."""
    await delete_seasonal_rate(db, rate_id)


# ---------------------------------------------------------------------------
# Weekend Surcharge endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/weekend",
    response_model=WeekendSurchargeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_weekend_surcharge_endpoint(
    data: WeekendSurchargeCreate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_manager_or_above),
):
    """Create a weekend surcharge for a room type."""
    return await create_weekend_surcharge(db, data)


@router.get("/weekend/{room_type_id}", response_model=list[WeekendSurchargeResponse])
async def list_weekend_surcharges_endpoint(
    room_type_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_staff),
):
    """List active weekend surcharges for a room type."""
    return await get_weekend_surcharges(db, room_type_id)


@router.patch("/weekend/{rate_id}", response_model=WeekendSurchargeResponse)
async def update_weekend_surcharge_endpoint(
    rate_id: uuid.UUID,
    data: WeekendSurchargeUpdate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_manager_or_above),
):
    """Update a weekend surcharge."""
    return await update_weekend_surcharge(db, rate_id, data)


@router.delete("/weekend/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weekend_surcharge_endpoint(
    rate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_admin),
):
    """Delete a weekend surcharge."""
    await delete_weekend_surcharge(db, rate_id)


# ---------------------------------------------------------------------------
# Price Calculation endpoint
# ---------------------------------------------------------------------------


@router.post("/calculate", response_model=PriceCalculationResponse)
async def calculate_price_endpoint(
    data: PriceCalculationRequest,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_staff),
):
    """Calculate stay price with multiplicative stacking."""
    result = await calculate_stay_price(
        db,
        room_type_id=data.room_type_id,
        check_in=data.check_in,
        check_out=data.check_out,
        occupancy=data.occupancy,
    )
    return PriceCalculationResponse(
        room_type_id=data.room_type_id,
        check_in=data.check_in,
        check_out=data.check_out,
        occupancy=data.occupancy,
        currency=result["currency"],
        nightly_rates=result["nightly_rates"],
        total=result["total"],
    )
