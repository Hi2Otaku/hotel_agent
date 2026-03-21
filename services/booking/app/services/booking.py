"""Core booking service with 3-step flow, state machine, and pessimistic locking.

Implements the complete booking lifecycle:
  Step 1: create_booking   -- reserve room type for dates (PENDING)
  Step 2: submit_guest_details -- fill in guest information
  Step 3: process_booking_payment -- pay and confirm
"""

import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.booking import Booking, BookingStatus, VALID_TRANSITIONS, generate_confirmation_number
from app.models.payment import PaymentTransaction
from app.schemas.booking import BookingCreate, CancellationPolicyResponse, GuestDetailsSubmit
from app.schemas.payment import PaymentSubmit
from app.services.event_publisher import publish_booking_event
from app.services.email import send_booking_confirmation_email
from app.services.payment import process_payment
from app.services.pricing import get_pricing_from_room_service, get_room_count_for_type

logger = logging.getLogger(__name__)


async def create_booking(
    db: AsyncSession, user_id: UUID, data: BookingCreate
) -> Booking:
    """Step 1: Create a PENDING booking with pessimistic locking to prevent double-booking.

    Validates dates, checks availability using SELECT ... FOR UPDATE,
    fetches pricing from Room service, and creates the booking record.

    Args:
        db: Async database session.
        user_id: The authenticated user's UUID.
        data: BookingCreate schema with room_type_id, check_in, check_out, guest_count.

    Returns:
        The created Booking with status PENDING.

    Raises:
        HTTPException(400): Invalid dates.
        HTTPException(409): No rooms available.
        HTTPException(502): Room service unreachable.
    """
    # Validate dates
    if data.check_in >= data.check_out:
        raise HTTPException(status_code=400, detail="Check-in must be before check-out")
    if data.check_in < date.today():
        raise HTTPException(status_code=400, detail="Check-in cannot be in the past")

    # Pessimistic locking: count overlapping blocking bookings FOR UPDATE
    blocking_query = (
        select(func.count())
        .select_from(Booking)
        .where(
            Booking.room_type_id == data.room_type_id,
            Booking.status.in_([
                BookingStatus.PENDING,
                BookingStatus.CONFIRMED,
                BookingStatus.CHECKED_IN,
            ]),
            Booking.check_in < data.check_out,
            Booking.check_out > data.check_in,
        )
        .with_for_update()
    )
    result = await db.execute(blocking_query)
    blocking_count = result.scalar_one()

    # Check against available room count
    total_rooms = await get_room_count_for_type(data.room_type_id)
    if blocking_count >= total_rooms:
        raise HTTPException(status_code=409, detail="No rooms available for selected dates")

    # Fetch pricing from Room service
    pricing = await get_pricing_from_room_service(
        data.room_type_id, data.check_in, data.check_out, data.guest_count
    )

    # Create booking
    booking = Booking(
        confirmation_number=generate_confirmation_number(),
        user_id=user_id,
        room_type_id=data.room_type_id,
        check_in=data.check_in,
        check_out=data.check_out,
        guest_count=data.guest_count,
        status=BookingStatus.PENDING,
        total_price=pricing["total_price"],
        price_per_night=pricing["price_per_night"],
        currency=pricing["currency"],
        nightly_breakdown=pricing["nightly_breakdown"],
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.PENDING_EXPIRY_MINUTES),
    )
    db.add(booking)
    await db.flush()

    # Publish event (non-blocking)
    try:
        await publish_booking_event(booking, "booking.created")
    except Exception:
        logger.exception("Failed to publish booking.created event")

    await db.commit()
    await db.refresh(booking)
    return booking


async def submit_guest_details(
    db: AsyncSession, booking_id: UUID, user_id: UUID, data: GuestDetailsSubmit
) -> Booking:
    """Step 2: Submit guest personal details for a PENDING booking.

    Verifies ownership, checks on-demand expiry, and updates guest fields.

    Args:
        db: Async database session.
        booking_id: The booking UUID.
        user_id: The authenticated user's UUID.
        data: GuestDetailsSubmit schema with guest info.

    Returns:
        The updated Booking.

    Raises:
        HTTPException(404): Booking not found.
        HTTPException(403): Not the booking owner.
        HTTPException(400): Booking not in PENDING status or expired.
    """
    booking = await _get_booking_with_ownership(db, booking_id, user_id)

    # On-demand expiry check
    booking = await _check_expiry(db, booking)

    if booking.status != BookingStatus.PENDING and booking.status != "pending":
        raise HTTPException(status_code=400, detail="Booking is not in pending status")

    booking.guest_first_name = data.guest_first_name
    booking.guest_last_name = data.guest_last_name
    booking.guest_email = data.guest_email
    booking.guest_phone = data.guest_phone
    booking.guest_address = data.guest_address
    booking.special_requests = data.special_requests
    booking.id_document = data.id_document

    await db.commit()
    await db.refresh(booking)
    return booking


async def process_booking_payment(
    db: AsyncSession, booking_id: UUID, user_id: UUID, payment_data: PaymentSubmit
) -> tuple[Booking, PaymentTransaction]:
    """Step 3: Process payment and confirm the booking.

    Uses SELECT ... FOR UPDATE to prevent expiry race conditions.
    On success, transitions booking to CONFIRMED and sends confirmation email.

    Args:
        db: Async database session.
        booking_id: The booking UUID.
        user_id: The authenticated user's UUID.
        payment_data: PaymentSubmit schema with card details.

    Returns:
        Tuple of (Booking, PaymentTransaction).

    Raises:
        HTTPException(404): Booking not found.
        HTTPException(403): Not the booking owner.
        HTTPException(400): Booking not in PENDING status, expired, or guest details missing.
    """
    # Lock the booking row to prevent expiry race
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Verify ownership
    if str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not your booking")

    # On-demand expiry check
    booking = await _check_expiry(db, booking)

    if booking.status != BookingStatus.PENDING and booking.status != "pending":
        raise HTTPException(status_code=400, detail="Booking is not in pending status")

    # Verify guest details are filled
    if booking.guest_first_name is None:
        raise HTTPException(
            status_code=400,
            detail="Guest details must be submitted before payment",
        )

    # Process payment
    payment_result = await process_payment(
        payment_data.card_number,
        Decimal(str(booking.total_price)),
        booking.currency,
    )

    # Create payment transaction record
    transaction = PaymentTransaction(
        booking_id=booking.id,
        transaction_id=payment_result["transaction_id"],
        amount=payment_result["amount"],
        currency=payment_result["currency"],
        card_last_four=payment_result["last_four"],
        card_brand=payment_result["brand"],
        status=payment_result["status"],
        decline_reason=payment_result.get("decline_reason"),
    )
    db.add(transaction)

    if payment_result["status"] == "succeeded":
        booking = await transition_booking(db, booking, "confirmed")

        # Send confirmation email (non-blocking)
        try:
            policy = get_cancellation_policy(booking, settings.CANCELLATION_POLICY_DAYS)
            guest_name = f"{booking.guest_first_name} {booking.guest_last_name}"
            await send_booking_confirmation_email(
                email=booking.guest_email,
                confirmation_number=booking.confirmation_number,
                guest_name=guest_name,
                check_in=booking.check_in,
                check_out=booking.check_out,
                room_type_name="Room",  # Pricing info not stored separately
                total_price=Decimal(str(booking.total_price)),
                currency=booking.currency,
                cancellation_policy=policy.policy_text,
            )
        except Exception:
            logger.exception("Failed to send confirmation email for booking %s", booking.id)
    else:
        await db.commit()

    return booking, transaction


async def transition_booking(
    db: AsyncSession, booking: Booking, new_status: str, reason: str | None = None
) -> Booking:
    """Transition a booking to a new status using the state machine.

    Validates the transition against VALID_TRANSITIONS, updates status,
    and publishes the corresponding event.

    Args:
        db: Async database session.
        booking: The Booking ORM instance.
        new_status: The target status string.
        reason: Optional reason (used for cancellations).

    Returns:
        The updated Booking.

    Raises:
        HTTPException(400): Invalid state transition.
    """
    current = booking.status if isinstance(booking.status, str) else booking.status.value
    allowed = VALID_TRANSITIONS.get(current, set())

    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current} to {new_status}",
        )

    booking.status = new_status

    if new_status == "cancelled":
        booking.cancelled_at = datetime.now(timezone.utc)
        booking.cancellation_reason = reason

    # Publish event
    try:
        await publish_booking_event(booking, f"booking.{new_status}")
    except Exception:
        logger.exception("Failed to publish booking.%s event", new_status)

    await db.commit()
    await db.refresh(booking)
    return booking


async def get_booking(
    db: AsyncSession, booking_id: UUID, user_id: UUID | None = None
) -> Booking:
    """Fetch a booking by ID with optional ownership check and on-demand expiry.

    Args:
        db: Async database session.
        booking_id: The booking UUID.
        user_id: If provided, verify the booking belongs to this user.

    Returns:
        The Booking instance.

    Raises:
        HTTPException(404): Booking not found.
        HTTPException(403): Not the booking owner.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    if user_id is not None and str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not your booking")

    # On-demand expiry check
    booking = await _check_expiry(db, booking)

    return booking


def get_cancellation_policy(
    booking: Booking, cancellation_policy_days: int
) -> CancellationPolicyResponse:
    """Calculate the cancellation policy for a booking.

    Args:
        booking: The Booking instance.
        cancellation_policy_days: Number of days before check-in for free cancellation.

    Returns:
        CancellationPolicyResponse with policy details.
    """
    check_in_date = booking.check_in if isinstance(booking.check_in, date) else booking.check_in.date()
    free_before = check_in_date - timedelta(days=cancellation_policy_days)

    if date.today() < free_before:
        return CancellationPolicyResponse(
            free_cancellation_before=free_before,
            cancellation_fee=None,
            policy_text=f"Free cancellation before {free_before}",
        )
    else:
        fee = Decimal(str(booking.price_per_night)) if booking.price_per_night else None
        currency = booking.currency or "USD"
        return CancellationPolicyResponse(
            free_cancellation_before=free_before,
            cancellation_fee=fee,
            policy_text=f"Late cancellation: {fee} {currency} fee applies",
        )


async def _get_booking_with_ownership(
    db: AsyncSession, booking_id: UUID, user_id: UUID
) -> Booking:
    """Fetch a booking and verify ownership."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not your booking")

    return booking


async def _check_expiry(db: AsyncSession, booking: Booking) -> Booking:
    """On-demand expiry check: cancel PENDING bookings past their expires_at."""
    current_status = booking.status if isinstance(booking.status, str) else booking.status.value
    if current_status == "pending" and booking.expires_at is not None:
        now = datetime.now(timezone.utc)
        expires = booking.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if now > expires:
            booking = await transition_booking(db, booking, "cancelled", reason="expired")
    return booking
