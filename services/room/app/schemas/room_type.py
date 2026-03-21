"""Pydantic v2 schemas for room type request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BedConfig(BaseModel):
    """Single bed configuration entry."""

    type: str = Field(..., examples=["king", "queen", "twin", "sofa"])
    count: int = Field(..., ge=1)


class RoomTypeCreate(BaseModel):
    """Schema for creating a new room type."""

    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str = ""
    max_adults: int = Field(..., ge=1, le=10)
    max_children: int = Field(0, ge=0, le=10)
    bed_config: list[BedConfig] = []
    amenities: dict[str, list[str]] = {}


class RoomTypeUpdate(BaseModel):
    """Schema for partially updating a room type."""

    name: str | None = Field(None, min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    max_adults: int | None = Field(None, ge=1, le=10)
    max_children: int | None = Field(None, ge=0, le=10)
    bed_config: list[BedConfig] | None = None
    amenities: dict[str, list[str]] | None = None
    is_active: bool | None = None


class RoomTypeResponse(BaseModel):
    """Schema for room type API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str
    max_adults: int
    max_children: int
    bed_config: list[BedConfig]
    amenities: dict[str, list[str]]
    photo_urls: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoomTypeListResponse(BaseModel):
    """Paginated list of room types."""

    items: list[RoomTypeResponse]
    total: int
