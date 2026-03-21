"""Rate models: BaseRate, SeasonalRate, WeekendSurcharge."""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BaseRate(Base):
    """Base nightly rate for a room type by occupancy."""

    __tablename__ = "base_rates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    room_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("room_types.id"),
        nullable=False,
    )
    min_occupancy: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_occupancy: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Relationships
    room_type = relationship("RoomType", back_populates="base_rates")


class SeasonalRate(Base):
    """Seasonal pricing multiplier for a room type."""

    __tablename__ = "seasonal_rates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    room_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("room_types.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    multiplier: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class WeekendSurcharge(Base):
    """Weekend surcharge multiplier for a room type."""

    __tablename__ = "weekend_surcharges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    room_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("room_types.id"),
        nullable=False,
    )
    multiplier: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    days: Mapped[list] = mapped_column(JSONB, nullable=False, default=[4, 5])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
