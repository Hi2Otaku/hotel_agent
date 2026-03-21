"""RabbitMQ event publishing for booking lifecycle events.

Publishes events to the booking.events exchange, matching the
Room service consumer contract for reservation projections.
"""

import json
import logging

from aio_pika import DeliveryMode, Message

from shared.messaging import get_rabbitmq_connection, get_channel, declare_exchange
from app.core.config import settings

logger = logging.getLogger(__name__)

BOOKING_EXCHANGE = "booking.events"


async def publish_booking_event(booking, event_type: str) -> None:
    """Publish a booking lifecycle event to RabbitMQ.

    Builds a payload matching the Room service consumer contract exactly.
    Errors are logged but never propagated -- booking flow must not crash
    because of a messaging failure.

    Args:
        booking: The Booking ORM instance.
        event_type: The event routing key (e.g., "booking.created", "booking.confirmed").
    """
    connection = None
    try:
        payload = {
            "event_type": event_type,
            "booking_id": str(booking.id),
            "room_type_id": str(booking.room_type_id),
            "room_id": str(booking.room_id) if booking.room_id else None,
            "check_in": booking.check_in.isoformat(),
            "check_out": booking.check_out.isoformat(),
            "status": booking.status if isinstance(booking.status, str) else booking.status.value,
            "guest_count": booking.guest_count,
        }

        connection = await get_rabbitmq_connection(settings.RABBITMQ_URL)
        channel = await get_channel(connection)
        exchange = await declare_exchange(channel, BOOKING_EXCHANGE)

        message = Message(
            body=json.dumps(payload).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=event_type)

        logger.info("Published %s for booking %s", event_type, booking.id)
    except Exception:
        logger.exception("Failed to publish %s for booking %s", event_type, booking.id)
    finally:
        if connection is not None:
            try:
                await connection.close()
            except Exception:
                pass
