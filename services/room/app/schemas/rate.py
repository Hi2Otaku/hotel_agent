"""Pydantic v2 schemas for rate request/response validation.

All monetary fields use Decimal, never float.
"""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- BaseRate ---


class BaseRateCreate(BaseModel):
    """Schema for creating a base rate."""

    room_type_id: uuid.UUID
    min_occupancy: int = Field(1, ge=1)
    max_occupancy: int = Field(..., ge=1, le=10)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field("USD", min_length=3, max_length=3)


class BaseRateUpdate(BaseModel):
    """Schema for partially updating a base rate."""

    min_occupancy: int | None = Field(None, ge=1)
    max_occupancy: int | None = Field(None, ge=1, le=10)
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    currency: str | None = Field(None, min_length=3, max_length=3)


class BaseRateResponse(BaseModel):
    """Schema for base rate API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_type_id: uuid.UUID
    min_occupancy: int
    max_occupancy: int
    amount: Decimal
    currency: str


# --- SeasonalRate ---


class SeasonalRateCreate(BaseModel):
    """Schema for creating a seasonal rate."""

    room_type_id: uuid.UUID
    name: str = Field(..., min_length=2, max_length=100)
    start_date: date
    end_date: date
    multiplier: Decimal = Field(..., gt=0, decimal_places=2)


class SeasonalRateUpdate(BaseModel):
    """Schema for partially updating a seasonal rate."""

    name: str | None = Field(None, min_length=2, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    multiplier: Decimal | None = Field(None, gt=0, decimal_places=2)
    is_active: bool | None = None


class SeasonalRateResponse(BaseModel):
    """Schema for seasonal rate API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_type_id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    multiplier: Decimal
    is_active: bool


# --- WeekendSurcharge ---


class WeekendSurchargeCreate(BaseModel):
    """Schema for creating a weekend surcharge."""

    room_type_id: uuid.UUID
    multiplier: Decimal = Field(..., gt=0, decimal_places=2)
    days: list[int] = Field(
        default=[4, 5],
        description="Weekday numbers (0=Mon, 4=Fri, 5=Sat)",
    )


class WeekendSurchargeUpdate(BaseModel):
    """Schema for partially updating a weekend surcharge."""

    multiplier: Decimal | None = Field(None, gt=0, decimal_places=2)
    days: list[int] | None = None
    is_active: bool | None = None


class WeekendSurchargeResponse(BaseModel):
    """Schema for weekend surcharge API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_type_id: uuid.UUID
    multiplier: Decimal
    days: list[int]
    is_active: bool


# --- Price Calculation ---


class PriceCalculationRequest(BaseModel):
    """Schema for requesting a price calculation."""

    room_type_id: uuid.UUID
    check_in: date
    check_out: date
    occupancy: int = Field(..., ge=1)


class NightlyRate(BaseModel):
    """Breakdown of a single night's pricing."""

    date: date
    base_amount: Decimal
    seasonal_multiplier: Decimal
    weekend_multiplier: Decimal
    final_amount: Decimal


class PriceCalculationResponse(BaseModel):
    """Full price calculation result with nightly breakdown."""

    room_type_id: uuid.UUID
    check_in: date
    check_out: date
    occupancy: int
    currency: str
    nightly_rates: list[NightlyRate]
    total: Decimal
