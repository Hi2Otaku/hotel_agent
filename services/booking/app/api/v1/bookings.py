"""Three-step booking API endpoints.

Step 1: POST /           -- create PENDING booking
Step 2: PUT /{id}/guest-details -- submit guest information
Step 3: POST /{id}/payment     -- pay and confirm

Plus: GET /{id} and GET /{id}/cancellation-policy.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.schemas.booking import (
    BookingCreate,
    BookingListResponse,
    BookingModifyRequest,
    BookingResponse,
    CancellationPolicyResponse,
    GuestDetailsSubmit,
)
from app.schemas.payment import PaymentResponse, PaymentSubmit
from app.services.booking import (
    cancel_booking,
    create_booking,
    get_booking,
    get_cancellation_policy,
    list_bookings,
    modify_booking,
    process_booking_payment,
    submit_guest_details,
)

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])


@router.get("/", response_model=BookingListResponse)
async def list_bookings_endpoint(
    status: str | None = None,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List the authenticated guest's bookings with optional status filter."""
    user_id = UUID(current_user["sub"])
    bookings, total = await list_bookings(db, user_id, status_filter=status, skip=skip, limit=limit)
    return BookingListResponse(
        items=[BookingResponse.model_validate(b) for b in bookings],
        total=total,
    )


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


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking_endpoint(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cancel a booking with policy-based cancellation fee."""
    user_id = UUID(current_user["sub"])
    booking = await cancel_booking(db, booking_id, user_id)
    return booking


@router.put("/{booking_id}/modify")
async def modify_booking_endpoint(
    booking_id: UUID,
    data: BookingModifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Modify a confirmed booking with availability re-check and price recalculation."""
    user_id = UUID(current_user["sub"])
    result = await modify_booking(db, booking_id, user_id, data)
    booking_resp = BookingResponse.model_validate(result["booking"])
    return {
        "booking": booking_resp.model_dump(mode="json"),
        "old_total": str(result["old_total"]),
        "new_total": str(result["new_total"]),
        "price_difference": str(result["price_difference"]),
        "currency": result["booking"].currency,
    }
