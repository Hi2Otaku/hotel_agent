"""RoomType model with JSONB amenities, bed_config, and photo_urls."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RoomType(Base):
    """Room type definition (e.g. Deluxe King, Standard Twin)."""

    __tablename__ = "room_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    max_adults: Mapped[int] = mapped_column(Integer, nullable=False)
    max_children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bed_config: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    amenities: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    photo_urls: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    rooms = relationship("Room", back_populates="room_type")
    base_rates = relationship("BaseRate", back_populates="room_type")
