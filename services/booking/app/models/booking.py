"""Booking model with status enum, valid transitions, and confirmation number generator."""

import random
import string
import uuid
from datetime import datetime
from decimal import Decimal

from enum import Enum as PyEnum

from sqlalchemy import Date, DateTime, Enum, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# Characters that avoid ambiguity (no 0/O, 1/I)
_CONFIRMATION_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class BookingStatus(str, PyEnum):
    """Allowed booking lifecycle states."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


VALID_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"checked_in", "cancelled"},
    "checked_in": {"checked_out"},
    "checked_out": set(),
    "cancelled": set(),
    "no_show": set(),
}


def generate_confirmation_number() -> str:
    """Generate a human-friendly confirmation number like HB-A3K7X2."""
    code = "".join(random.choices(_CONFIRMATION_CHARS, k=6))
    return f"HB-{code}"


class Booking(Base):
    """A guest room booking with full lifecycle tracking."""

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    confirmation_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    room_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Stay details
    check_in: Mapped[datetime] = mapped_column(Date, nullable=False)
    check_out: Mapped[datetime] = mapped_column(Date, nullable=False)
    guest_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Status
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status", create_constraint=True),
        default=BookingStatus.PENDING,
    )

    # Pricing (Decimal, never float)
    total_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_per_night: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    nightly_breakdown: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Guest details
    guest_first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guest_last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guest_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    guest_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    special_requests: Mapped[str | None] = mapped_column(Text, nullable=True)
    id_document: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Lifecycle timestamps
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancellation_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cancellation_fee: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
