"""Pydantic v2 schemas for search, room detail, and pricing calendar.

All monetary fields use Decimal, never float.
"""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    """Query params for search -- used for documentation, actual parsing via Query()."""

    check_in: date
    check_out: date
    guests: int = Field(..., ge=1)
    room_type_id: uuid.UUID | None = None
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    amenities: str | None = None  # comma-separated
    sort: str = "recommended"


class BedConfigItem(BaseModel):
    """Single bed configuration entry in search results."""

    type: str
    count: int


class SearchResult(BaseModel):
    """Single room type result in search response."""

    room_type_id: uuid.UUID
    name: str
    slug: str
    description: str
    photo_url: str | None = None  # first photo as thumbnail
    price_per_night: Decimal
    total_price: Decimal
    currency: str = "USD"
    max_adults: int
    max_children: int
    bed_config: list[BedConfigItem]
    amenity_highlights: list[str]  # top 5 amenity keys
    available_count: int
    total_rooms: int


class SearchResponse(BaseModel):
    """Search results wrapper."""

    results: list[SearchResult]
    total: int
    check_in: date
    check_out: date
    guests: int


class NightlyRate(BaseModel):
    """Per-night rate breakdown."""

    date: date
    base_amount: Decimal
    seasonal_multiplier: Decimal
    weekend_multiplier: Decimal
    final_amount: Decimal


class RoomTypeDetail(BaseModel):
    """Full room type detail with pricing for selected dates."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str
    max_adults: int
    max_children: int
    bed_config: list[BedConfigItem]
    amenities: dict[str, list[str]]
    photo_urls: list[str]
    available_count: int
    total_rooms: int
    price_per_night: Decimal
    total_price: Decimal
    currency: str
    nightly_rates: list[NightlyRate]


class CalendarDay(BaseModel):
    """Single day in pricing calendar."""

    date: date
    rate: Decimal
    base_amount: Decimal
    seasonal_multiplier: Decimal
    weekend_multiplier: Decimal
    available_count: int
    total_rooms: int
    availability_indicator: str  # "green", "yellow", "red"


class CalendarResponse(BaseModel):
    """Pricing calendar response."""

    room_type_id: uuid.UUID | None
    room_type_name: str | None
    start_date: date
    end_date: date
    days: list[CalendarDay]
