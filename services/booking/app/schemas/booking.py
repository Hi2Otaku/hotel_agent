"""Pydantic v2 schemas for booking request/response contracts."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr


class BookingCreate(BaseModel):
    """Step 1: Hold a room type for given dates."""

    room_type_id: uuid.UUID
    check_in: date
    check_out: date
    guest_count: int = 1


class GuestDetailsSubmit(BaseModel):
    """Step 2: Submit guest personal details."""

    guest_first_name: str
    guest_last_name: str
    guest_email: EmailStr
    guest_phone: str
    guest_address: str | None = None
    special_requests: str | None = None
    id_document: str | None = None


class BookingResponse(BaseModel):
    """Full booking representation returned by API."""

    id: uuid.UUID
    confirmation_number: str
    user_id: uuid.UUID
    room_type_id: uuid.UUID
    room_id: uuid.UUID | None
    check_in: date
    check_out: date
    guest_count: int
    status: str
    total_price: Decimal | None
    price_per_night: Decimal | None
    currency: str
    nightly_breakdown: list | None
    guest_first_name: str | None
    guest_last_name: str | None
    guest_email: str | None
    guest_phone: str | None
    special_requests: str | None
    expires_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    cancellation_fee: Decimal | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    """Paginated list of bookings."""

    items: list[BookingResponse]
    total: int


class BookingModifyRequest(BaseModel):
    """Modify an existing booking (all fields optional)."""

    check_in: date | None = None
    check_out: date | None = None
    room_type_id: uuid.UUID | None = None
    guest_count: int | None = None
    guest_first_name: str | None = None
    guest_last_name: str | None = None
    guest_phone: str | None = None
    guest_address: str | None = None
    special_requests: str | None = None


class ModifyPricePreview(BaseModel):
    """Price comparison when modifying a booking."""

    old_total: Decimal
    new_total: Decimal
    price_difference: Decimal
    currency: str
    nightly_breakdown: list


class CancellationPolicyResponse(BaseModel):
    """Cancellation policy details for a booking."""

    free_cancellation_before: date | None
    cancellation_fee: Decimal | None
    policy_text: str
