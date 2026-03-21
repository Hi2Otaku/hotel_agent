"""RabbitMQ event consumer for booking service events.

Listens on the booking.events exchange and upserts ReservationProjection
rows to keep the room service's availability data in sync.
"""

import asyncio
import json
import logging
import uuid
from datetime import date

from aio_pika import IncomingMessage
from sqlalchemy import select

from shared.messaging import (
    get_rabbitmq_connection,
    get_channel,
    declare_exchange,
    declare_queue,
)
from app.core.database import async_session_factory
from app.core.config import settings
from app.models.reservation import ReservationProjection

logger = logging.getLogger(__name__)

BOOKING_EXCHANGE = "booking.events"
ROOM_QUEUE = "room.booking_projections"
BLOCKING_STATUSES = {"pending", "confirmed", "checked_in"}


async def handle_booking_event(message: IncomingMessage) -> None:
    """Process a single booking event message.

    Upserts a ReservationProjection row based on booking_id.
    Uses message.process() for automatic ack on success / nack on exception.
    """
    async with message.process():
        data = json.loads(message.body.decode())

        event_type = data.get("event_type", "unknown")
        booking_id = uuid.UUID(data["booking_id"])
        room_type_id = uuid.UUID(data["room_type_id"])
        room_id = uuid.UUID(data["room_id"]) if data.get("room_id") else None
        check_in = date.fromisoformat(data["check_in"])
        check_out = date.fromisoformat(data["check_out"])
        status = data["status"]
        guest_count = data.get("guest_count", 1)

        async with async_session_factory() as db:
            # Look up existing projection by booking_id
            result = await db.execute(
                select(ReservationProjection).where(
                    ReservationProjection.booking_id == booking_id
                )
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                # INSERT new projection
                projection = ReservationProjection(
                    booking_id=booking_id,
                    room_type_id=room_type_id,
                    room_id=room_id,
                    check_in=check_in,
                    check_out=check_out,
                    status=status,
                    guest_count=guest_count,
                )
                db.add(projection)
            else:
                # UPDATE existing projection
                existing.status = status
                if room_id is not None:
                    existing.room_id = room_id

            await db.commit()

        logger.info(f"Processed {event_type} for booking {booking_id}")


async def start_event_consumer() -> None:
    """Start the RabbitMQ consumer for booking events.

    Connects to RabbitMQ, declares exchange and queue, binds with
    routing key 'booking.*', and consumes messages indefinitely.
    """
    connection = await get_rabbitmq_connection(settings.RABBITMQ_URL)
    try:
        channel = await get_channel(connection)
        exchange = await declare_exchange(channel, BOOKING_EXCHANGE)
        queue = await declare_queue(channel, ROOM_QUEUE)
        await queue.bind(exchange, routing_key="booking.*")
        await queue.consume(handle_booking_event)
        logger.info("RabbitMQ consumer started on queue %s", ROOM_QUEUE)
        # Keep consumer running until cancelled
        await asyncio.Future()
    finally:
        await connection.close()
