"""Room model with RoomStatus enum (7 statuses)."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RoomStatus(str, PyEnum):
    """Room housekeeping / availability status."""

    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    INSPECTED = "inspected"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"
    RESERVED = "reserved"


class Room(Base):
    """Individual room within the hotel."""

    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    room_number: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("room_types.id"),
        nullable=False,
    )
    status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus, name="room_status", create_constraint=True),
        default=RoomStatus.AVAILABLE,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    room_type = relationship("RoomType", back_populates="rooms")
    status_history = relationship("RoomStatusChange", back_populates="room")
