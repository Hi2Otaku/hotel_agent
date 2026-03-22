"""RabbitMQ event publishing for chat service events.

Publishes events to the chat.events exchange. Follows the same pattern
as the booking service event publisher -- errors are logged but never
propagated to avoid disrupting the chat flow.
"""

import json
import logging

from aio_pika import DeliveryMode, Message

from shared.messaging import get_rabbitmq_connection, get_channel, declare_exchange
from app.core.config import settings

logger = logging.getLogger(__name__)

CHAT_EXCHANGE = "chat.events"


async def publish_chat_event(event_type: str, payload: dict) -> None:
    """Publish a chat event to RabbitMQ.

    Routing keys:
      - chat.message.sent
      - chat.conversation.created
      - chat.tool.executed

    Args:
        event_type: The routing key / event type string.
        payload: The event payload dict.
    """
    connection = None
    try:
        body = {
            "event_type": event_type,
            **payload,
        }

        connection = await get_rabbitmq_connection(settings.RABBITMQ_URL)
        channel = await get_channel(connection)
        exchange = await declare_exchange(channel, CHAT_EXCHANGE)

        message = Message(
            body=json.dumps(body, default=str).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=event_type)

        logger.info("Published %s event", event_type)
    except Exception:
        logger.exception("Failed to publish %s event", event_type)
    finally:
        if connection is not None:
            try:
                await connection.close()
            except Exception:
                pass
