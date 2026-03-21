"""Three-step booking API endpoints.

Step 1: POST /           -- create PENDING booking
Step 2: PUT /{id}/guest-details -- submit guest information
Step 3: POST /{id}/payment     -- pay and confirm

Plus: GET /{id} and GET /{id}/cancellation-policy.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    CancellationPolicyResponse,
    GuestDetailsSubmit,
)
from app.schemas.payment import PaymentResponse, PaymentSubmit
from app.services.booking import (
    create_booking,
    get_booking,
    get_cancellation_policy,
    process_booking_payment,
    submit_guest_details,
)

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking_endpoint(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Step 1: Create a PENDING booking for the authenticated user."""
    user_id = UUID(current_user["sub"])
    booking = await create_booking(db, user_id, data)
    return booking


@router.put("/{booking_id}/guest-details", response_model=BookingResponse)
async def submit_guest_details_endpoint(
    booking_id: UUID,
    data: GuestDetailsSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Step 2: Submit guest personal details for a PENDING booking."""
    user_id = UUID(current_user["sub"])
    booking = await submit_guest_details(db, booking_id, user_id, data)
    return booking


@router.post("/{booking_id}/payment")
async def process_payment_endpoint(
    booking_id: UUID,
    data: PaymentSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Step 3: Process payment to confirm the booking.

    Returns 200 on success, 402 if payment is declined.
    """
    user_id = UUID(current_user["sub"])
    booking, transaction = await process_booking_payment(db, booking_id, user_id, data)

    booking_resp = BookingResponse.model_validate(booking)
    payment_resp = PaymentResponse.model_validate(transaction)

    if transaction.status == "declined":
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Payment declined",
                "booking": booking_resp.model_dump(mode="json"),
                "payment": payment_resp.model_dump(mode="json"),
            },
        )

    return {
        "booking": booking_resp.model_dump(mode="json"),
        "payment": payment_resp.model_dump(mode="json"),
    }


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking_endpoint(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a booking by ID (ownership verified)."""
    user_id = UUID(current_user["sub"])
    booking = await get_booking(db, booking_id, user_id)
    return booking


@router.get("/{booking_id}/cancellation-policy", response_model=CancellationPolicyResponse)
async def get_cancellation_policy_endpoint(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get the cancellation policy for a booking."""
    user_id = UUID(current_user["sub"])
    booking = await get_booking(db, booking_id, user_id)
    return get_cancellation_policy(booking, settings.CANCELLATION_POLICY_DAYS)
