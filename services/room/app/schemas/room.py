"""Pydantic v2 schemas for room request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.room_type import RoomTypeResponse


class RoomCreate(BaseModel):
    """Schema for creating a new room."""

    room_number: str = Field(..., min_length=1, max_length=10)
    floor: int = Field(..., ge=0, le=100)
    room_type_id: uuid.UUID
    notes: str | None = None


class RoomUpdate(BaseModel):
    """Schema for partially updating a room."""

    room_number: str | None = Field(None, min_length=1, max_length=10)
    floor: int | None = Field(None, ge=0, le=100)
    room_type_id: uuid.UUID | None = None
    notes: str | None = None
    is_active: bool | None = None


class StatusTransitionRequest(BaseModel):
    """Schema for requesting a room status change."""

    new_status: str  # one of RoomStatus values
    reason: str | None = None


class RoomResponse(BaseModel):
    """Schema for room API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_number: str
    floor: int
    room_type_id: uuid.UUID
    status: str
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoomDetailResponse(RoomResponse):
    """Room response with joined room type details."""

    room_type: RoomTypeResponse | None = None


class RoomListResponse(BaseModel):
    """Paginated list of rooms."""

    items: list[RoomResponse]
    total: int


class StatusBoardRoom(BaseModel):
    """Single room entry on the status board."""

    id: uuid.UUID
    room_number: str
    status: str
    room_type_name: str


class StatusBoardFloor(BaseModel):
    """Floor grouping for the status board."""

    floor: int
    rooms: list[StatusBoardRoom]


class StatusBoardResponse(BaseModel):
    """Full status board: rooms grouped by floor with summary counts."""

    floors: list[StatusBoardFloor]
    summary: dict[str, int]  # status -> count


class StatusChangeResponse(BaseModel):
    """Schema for room status change log entries."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_id: uuid.UUID
    from_status: str
    to_status: str
    changed_by: uuid.UUID | None
    reason: str | None
    changed_at: datetime
