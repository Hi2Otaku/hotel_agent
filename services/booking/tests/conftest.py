"""Booking service test fixtures with mocked dependencies.

Isolates the booking service app module, mocks external dependencies
(RabbitMQ, email, Room service pricing), and provides test clients.

Merged from root tests/conftest.py (DB engine, session) and
tests/booking/conftest.py (booking-specific fixtures).
"""

import os
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_current_user, get_db
from app.core.database import Base
from app.main import app
from app.services import booking as _booking_service_module

BOOKING_TEST_DB_URL = os.getenv(
    "BOOKING_TEST_DATABASE_URL",
    "postgresql+asyncpg://booking_user:booking_pass@localhost:5436/bookings",
)


# ---------------------------------------------------------------------------
# Mock users
# ---------------------------------------------------------------------------

GUEST_USER_ID = str(uuid.uuid4())


@pytest.fixture
def guest_user():
    """JWT claims dict for a guest user."""
    return {"sub": GUEST_USER_ID, "role": "guest", "email": "guest@test.com"}


@pytest.fixture
def guest_token(guest_user):
    """Alias -- returns the guest claims dict."""
    return guest_user


@pytest.fixture
def other_user():
    """JWT claims dict for a different guest user."""
    return {"sub": str(uuid.uuid4()), "role": "guest", "email": "other@test.com"}


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
async def booking_test_engine():
    """Create test database engine, set up and tear down tables."""
    engine = create_async_engine(BOOKING_TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def booking_db_session(booking_test_engine):
    """Provide a transactional database session for each test."""
    sf = async_sessionmaker(booking_test_engine, expire_on_commit=False)
    async with sf() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# Mock external dependencies
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_publish_event():
    """Mock RabbitMQ event publishing to prevent real connections."""
    with patch.object(
        _booking_service_module, "publish_booking_event", new_callable=AsyncMock
    ) as m:
        yield m


@pytest.fixture(autouse=True)
def mock_send_email():
    """Mock email sending to prevent real SMTP connections."""
    with patch.object(
        _booking_service_module,
        "send_booking_confirmation_email",
        new_callable=AsyncMock,
    ) as m:
        yield m


@pytest.fixture(autouse=True)
def mock_pricing():
    """Mock Room service pricing call."""
    pricing_data = {
        "total_price": Decimal("300.00"),
        "price_per_night": Decimal("100.00"),
        "currency": "USD",
        "nightly_breakdown": [],
        "room_type_name": "Deluxe Room",
    }
    with patch.object(
        _booking_service_module,
        "get_pricing_from_room_service",
        new_callable=AsyncMock,
        return_value=pricing_data,
    ) as m:
        yield m


@pytest.fixture(autouse=True)
def mock_room_count():
    """Mock Room service room count call."""
    with patch.object(
        _booking_service_module,
        "get_room_count_for_type",
        new_callable=AsyncMock,
        return_value=5,
    ) as m:
        yield m


# ---------------------------------------------------------------------------
# Test clients
# ---------------------------------------------------------------------------

@pytest.fixture
async def client(booking_test_engine, guest_user):
    """Booking service test client with authenticated guest user."""
    sf = async_sessionmaker(booking_test_engine, expire_on_commit=False)

    async def override_get_db():
        async with sf() as session:
            yield session

    async def override_get_current_user():
        return guest_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def other_user_client(booking_test_engine, other_user):
    """Booking service test client with a different user."""
    sf = async_sessionmaker(booking_test_engine, expire_on_commit=False)

    async def override_get_db():
        async with sf() as session:
            yield session

    async def override_get_current_user():
        return other_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def unauth_client(booking_test_engine):
    """Booking service test client with NO auth override (triggers 401)."""
    sf = async_sessionmaker(booking_test_engine, expire_on_commit=False)

    async def override_get_db():
        async with sf() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    # Do NOT override get_current_user -- will require real token
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
