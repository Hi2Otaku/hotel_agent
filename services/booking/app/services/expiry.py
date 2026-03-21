"""Background task for expiring stale PENDING bookings.

Runs as an asyncio task within the FastAPI lifespan, periodically
checking for PENDING bookings past their expires_at timestamp.
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.booking import Booking, BookingStatus
from app.services.booking import transition_booking

logger = logging.getLogger(__name__)


async def expire_pending_bookings() -> None:
    """Continuously check for and cancel expired PENDING bookings.

    Runs in an infinite loop, sleeping for EXPIRY_CHECK_INTERVAL_SECONDS
    between checks. Each iteration queries all PENDING bookings with
    expires_at < now(UTC) and transitions them to CANCELLED with
    reason="expired".

    The loop body is wrapped in try/except to prevent the background
    task from dying on transient errors.
    """
    while True:
        await asyncio.sleep(settings.EXPIRY_CHECK_INTERVAL_SECONDS)
        try:
            async with async_session_factory() as db:
                now = datetime.now(timezone.utc)
                query = select(Booking).where(
                    Booking.status == BookingStatus.PENDING,
                    Booking.expires_at < now,
                )
                result = await db.execute(query)
                expired_bookings = result.scalars().all()

                count = 0
                for booking in expired_bookings:
                    try:
                        await transition_booking(db, booking, "cancelled", reason="expired")
                        count += 1
                    except Exception:
                        logger.exception(
                            "Failed to expire booking %s", booking.id
                        )

                if count > 0:
                    logger.info("Expired %d pending booking(s)", count)
        except Exception:
            logger.exception("Error in expiry check loop")
