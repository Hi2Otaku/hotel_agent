"""RabbitMQ messaging helpers using aio-pika.

Provides connection management and channel/exchange/queue helpers
for inter-service communication.
"""

import aio_pika
from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection, AbstractChannel


async def get_rabbitmq_connection(url: str) -> AbstractRobustConnection:
    """Create a robust connection to RabbitMQ.

    Args:
        url: AMQP connection URL (e.g., amqp://user:pass@host:5672/).

    Returns:
        A robust connection that auto-reconnects.
    """
    return await connect_robust(url)


async def get_channel(connection: AbstractRobustConnection) -> AbstractChannel:
    """Create a channel from an existing connection.

    Args:
        connection: An active RabbitMQ connection.

    Returns:
        A new channel on the connection.
    """
    return await connection.channel()


async def declare_exchange(
    channel: AbstractChannel,
    name: str,
    exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.TOPIC,
    durable: bool = True,
) -> aio_pika.abc.AbstractExchange:
    """Declare an exchange on the given channel.

    Args:
        channel: The channel to declare the exchange on.
        name: Exchange name.
        exchange_type: Type of exchange (default: TOPIC).
        durable: Whether the exchange survives broker restart.

    Returns:
        The declared exchange.
    """
    return await channel.declare_exchange(name, exchange_type, durable=durable)


async def declare_queue(
    channel: AbstractChannel,
    name: str,
    durable: bool = True,
) -> aio_pika.abc.AbstractQueue:
    """Declare a queue on the given channel.

    Args:
        channel: The channel to declare the queue on.
        name: Queue name.
        durable: Whether the queue survives broker restart.

    Returns:
        The declared queue.
    """
    return await channel.declare_queue(name, durable=durable)


__all__ = [
    "get_rabbitmq_connection",
    "get_channel",
    "declare_exchange",
    "declare_queue",
]
