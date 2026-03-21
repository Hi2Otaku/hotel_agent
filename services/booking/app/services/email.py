"""Booking confirmation email service via fastapi-mail and Mailpit.

Mirrors the auth service email.py pattern: lazy ConnectionConfig via
model_construct to bypass pydantic .local domain validation.
"""

import logging
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings

logger = logging.getLogger(__name__)

_conf: ConnectionConfig | None = None

TEMPLATE_FOLDER = Path(__file__).parent.parent / "templates" / "email"


def _get_mail_config() -> ConnectionConfig:
    """Lazily build the mail configuration.

    Uses model_construct to bypass pydantic email validation on MAIL_FROM,
    which rejects .local domains used in development with Mailpit.
    """
    global _conf
    if _conf is not None:
        return _conf

    _conf = ConnectionConfig.model_construct(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
        VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
        TEMPLATE_FOLDER=TEMPLATE_FOLDER,
        SUPPRESS_SEND=0,
    )
    return _conf


async def send_booking_confirmation_email(
    email: str,
    confirmation_number: str,
    guest_name: str,
    check_in: date,
    check_out: date,
    room_type_name: str,
    total_price: Decimal,
    currency: str,
    cancellation_policy: str,
) -> None:
    """Send a booking confirmation email to the guest.

    Errors are logged but never propagated -- a failed email must not
    prevent a successful booking from being committed.

    Args:
        email: The guest's email address.
        confirmation_number: The booking confirmation number (HB-XXXXXX).
        guest_name: The guest's full name.
        check_in: Check-in date.
        check_out: Check-out date.
        room_type_name: Display name of the room type.
        total_price: Total booking price.
        currency: ISO 4217 currency code.
        cancellation_policy: Human-readable cancellation policy text.
    """
    try:
        message = MessageSchema(
            subject="Booking Confirmed - HotelBook",
            recipients=[email],
            template_body={
                "confirmation_number": confirmation_number,
                "guest_name": guest_name,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "room_type_name": room_type_name,
                "total_price": str(total_price),
                "currency": currency,
                "cancellation_policy": cancellation_policy,
            },
            subtype=MessageType.html,
        )
        fm = FastMail(_get_mail_config())
        await fm.send_message(message, template_name="booking_confirmation.html")
        logger.info("Confirmation email sent to %s for %s", email, confirmation_number)
    except Exception:
        logger.exception(
            "Failed to send confirmation email to %s for %s",
            email,
            confirmation_number,
        )
