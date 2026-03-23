"""Unit tests for the RabbitMQ event consumer's handle_booking_event function.

Uses lazy imports to avoid module-level resolution issues with the
multi-service pythonpath configuration.
"""

import json
import uuid
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select


def _make_message(data: dict) -> MagicMock:
    """Create a mock IncomingMessage with JSON body and async process() context manager."""
    message = MagicMock()
    message.body = json.dumps(data).encode()

    @asynccontextmanager
    async def mock_process():
        yield

    message.process = mock_process
    return message


def _booking_event(
    booking_id: str | None = None,
    room_type_id: str | None = None,
    room_id: str | None = None,
    check_in: str = "2026-04-01",
    check_out: str = "2026-04-03",
    status: str = "pending",
    guest_count: int = 2,
    event_type: str = "booking.created",
) -> dict:
    """Build a booking event payload."""
    return {
        "event_type": event_type,
        "booking_id": booking_id or str(uuid.uuid4()),
        "room_type_id": room_type_id or str(uuid.uuid4()),
        "room_id": room_id,
        "check_in": check_in,
        "check_out": check_out,
        "status": status,
        "guest_count": guest_count,
    }


@pytest.mark.asyncio
async def test_handle_booking_event_insert(room_db_session):
    """A new booking event creates a ReservationProjection row."""
    from app.models.reservation import ReservationProjection
    from app.services.event_consumer import handle_booking_event

    booking_id = str(uuid.uuid4())
    room_type_id = str(uuid.uuid4())
    event = _booking_event(booking_id=booking_id, room_type_id=room_type_id)
    message = _make_message(event)

    @asynccontextmanager
    async def mock_session_factory():
        yield room_db_session

    with patch(
        "app.services.event_consumer.async_session_factory",
        mock_session_factory,
    ):
        await handle_booking_event(message)

    # Verify the row was created
    result = await room_db_session.execute(
        select(ReservationProjection).where(
            ReservationProjection.booking_id == uuid.UUID(booking_id)
        )
    )
    projection = result.scalar_one_or_none()
    assert projection is not None
    assert str(projection.room_type_id) == room_type_id
    assert projection.status == "pending"
    assert projection.guest_count == 2
    assert str(projection.check_in) == "2026-04-01"
    assert str(projection.check_out) == "2026-04-03"
    assert projection.room_id is None


@pytest.mark.asyncio
async def test_handle_booking_event_update(room_db_session):
    """An event with an existing booking_id updates the status."""
    from app.models.reservation import ReservationProjection
    from app.services.event_consumer import handle_booking_event

    booking_id = uuid.uuid4()
    room_type_id = uuid.uuid4()

    # Insert existing projection
    projection = ReservationProjection(
        booking_id=booking_id,
        room_type_id=room_type_id,
        check_in="2026-04-01",
        check_out="2026-04-03",
        status="pending",
        guest_count=1,
    )
    room_db_session.add(projection)
    await room_db_session.commit()

    # Send update event with status=cancelled
    event = _booking_event(
        booking_id=str(booking_id),
        room_type_id=str(room_type_id),
        status="cancelled",
        event_type="booking.cancelled",
    )
    message = _make_message(event)

    @asynccontextmanager
    async def mock_session_factory():
        yield room_db_session

    with patch(
        "app.services.event_consumer.async_session_factory",
        mock_session_factory,
    ):
        await handle_booking_event(message)

    # Refresh and verify
    await room_db_session.refresh(projection)
    assert projection.status == "cancelled"


@pytest.mark.asyncio
async def test_handle_booking_event_idempotent(room_db_session):
    """Sending the same event twice results in only one row (upsert, not duplicate)."""
    from app.models.reservation import ReservationProjection
    from app.services.event_consumer import handle_booking_event

    booking_id = str(uuid.uuid4())
    room_type_id = str(uuid.uuid4())
    event = _booking_event(booking_id=booking_id, room_type_id=room_type_id)

    @asynccontextmanager
    async def mock_session_factory():
        yield room_db_session

    with patch(
        "app.services.event_consumer.async_session_factory",
        mock_session_factory,
    ):
        # Process same event twice
        await handle_booking_event(_make_message(event))
        await handle_booking_event(_make_message(event))

    # Verify only one row
    result = await room_db_session.execute(
        select(ReservationProjection).where(
            ReservationProjection.booking_id == uuid.UUID(booking_id)
        )
    )
    rows = list(result.scalars().all())
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_handle_booking_event_sets_room_id(room_db_session):
    """An update event with room_id set updates the projection's room_id."""
    from app.models.reservation import ReservationProjection
    from app.services.event_consumer import handle_booking_event

    booking_id = uuid.uuid4()
    room_type_id = uuid.uuid4()
    room_id = uuid.uuid4()

    # Insert existing projection without room_id
    projection = ReservationProjection(
        booking_id=booking_id,
        room_type_id=room_type_id,
        check_in="2026-04-01",
        check_out="2026-04-03",
        status="confirmed",
        guest_count=1,
    )
    room_db_session.add(projection)
    await room_db_session.commit()

    # Send event with room_id
    event = _booking_event(
        booking_id=str(booking_id),
        room_type_id=str(room_type_id),
        room_id=str(room_id),
        status="checked_in",
        event_type="booking.checked_in",
    )
    message = _make_message(event)

    @asynccontextmanager
    async def mock_session_factory():
        yield room_db_session

    with patch(
        "app.services.event_consumer.async_session_factory",
        mock_session_factory,
    ):
        await handle_booking_event(message)

    # Refresh and verify room_id was set
    await room_db_session.refresh(projection)
    assert projection.room_id == room_id
    assert projection.status == "checked_in"
