"""Room service test fixtures with mock JWT and role overrides."""

import asyncio
import os
import uuid
from datetime import date
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import room service app and deps
from app.api.deps import get_db, get_current_user
from app.core.database import Base
from app.main import app

ROOM_TEST_DB_URL = os.getenv(
    "ROOM_TEST_DATABASE_URL",
    "postgresql+asyncpg://room_user:room_pass@localhost:5434/rooms",
)


@pytest.fixture(scope="session")
async def room_test_engine():
    """Create test database engine, set up and tear down tables."""
    engine = create_async_engine(ROOM_TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def room_db_session(room_test_engine):
    """Provide a transactional database session for each test."""
    sf = async_sessionmaker(room_test_engine, expire_on_commit=False)
    async with sf() as session:
        yield session
        await session.rollback()


def make_mock_user(role: str = "admin", user_id: str | None = None) -> dict:
    """Create a mock JWT payload for testing."""
    return {
        "sub": user_id or str(uuid.uuid4()),
        "role": role,
        "email": f"{role}@test.com",
    }


@pytest.fixture
def admin_user():
    return make_mock_user("admin")


@pytest.fixture
def manager_user():
    return make_mock_user("manager")


@pytest.fixture
def front_desk_user():
    return make_mock_user("front_desk")


@pytest.fixture
def housekeeping_user():
    return make_mock_user("housekeeping")


@pytest.fixture
async def client(room_test_engine, admin_user):
    """Room service client with admin user by default."""
    sf = async_sessionmaker(room_test_engine, expire_on_commit=False)

    async def override_get_db():
        async with sf() as session:
            yield session

    async def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def public_client(room_test_engine):
    """Room service client with no auth -- for public search endpoints."""
    sf = async_sessionmaker(room_test_engine, expire_on_commit=False)

    async def override_get_db():
        async with sf() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    # Do NOT override get_current_user -- search endpoints don't use it
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def front_desk_client(room_test_engine, front_desk_user):
    """Room service client with front_desk user role."""
    sf = async_sessionmaker(room_test_engine, expire_on_commit=False)

    async def override_get_db():
        async with sf() as session:
            yield session

    async def override_get_current_user():
        return front_desk_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seed data helpers (used by search/availability/calendar tests)
# ---------------------------------------------------------------------------


async def seed_room_data(db: AsyncSession) -> dict:
    """Seed two room types with rooms and base rates for testing.

    Creates:
    - Deluxe King: max_adults=2, 3 rooms, $200/night (occ 1-2)
    - Standard Twin: max_adults=3, 2 rooms, $120/night (occ 1-3)

    Returns dict with deluxe_id, standard_id, and room IDs.
    """
    from app.models.room_type import RoomType
    from app.models.room import Room
    from app.models.rate import BaseRate

    # Deluxe King
    deluxe = RoomType(
        name="Deluxe King",
        slug="deluxe-king",
        description="A premium room with king bed",
        max_adults=2,
        max_children=1,
        bed_config=[{"type": "king", "count": 1}],
        amenities={"room": ["wifi", "minibar", "tv"]},
        photo_urls=["https://example.com/deluxe1.jpg"],
        overbooking_pct=Decimal("0.00"),
    )
    db.add(deluxe)
    await db.flush()

    # Standard Twin
    standard = RoomType(
        name="Standard Twin",
        slug="standard-twin",
        description="A comfortable twin room",
        max_adults=3,
        max_children=1,
        bed_config=[{"type": "twin", "count": 2}],
        amenities={"room": ["wifi", "tv"]},
        photo_urls=[],
        overbooking_pct=Decimal("0.00"),
    )
    db.add(standard)
    await db.flush()

    # 3 rooms for Deluxe
    deluxe_rooms = []
    for i in range(3):
        room = Room(
            room_number=f"D{100 + i}",
            floor=1,
            room_type_id=deluxe.id,
            is_active=True,
        )
        db.add(room)
        deluxe_rooms.append(room)

    # 2 rooms for Standard
    standard_rooms = []
    for i in range(2):
        room = Room(
            room_number=f"S{200 + i}",
            floor=2,
            room_type_id=standard.id,
            is_active=True,
        )
        db.add(room)
        standard_rooms.append(room)

    await db.flush()

    # Base rates
    deluxe_rate = BaseRate(
        room_type_id=deluxe.id,
        min_occupancy=1,
        max_occupancy=2,
        amount=Decimal("200.00"),
        currency="USD",
    )
    db.add(deluxe_rate)

    standard_rate = BaseRate(
        room_type_id=standard.id,
        min_occupancy=1,
        max_occupancy=3,
        amount=Decimal("120.00"),
        currency="USD",
    )
    db.add(standard_rate)

    await db.commit()

    return {
        "deluxe_id": deluxe.id,
        "standard_id": standard.id,
        "deluxe_room_ids": [r.id for r in deluxe_rooms],
        "standard_room_ids": [r.id for r in standard_rooms],
    }


async def insert_reservation(
    db: AsyncSession,
    booking_id: uuid.UUID,
    room_type_id: uuid.UUID,
    check_in: date,
    check_out: date,
    status: str = "confirmed",
    guest_count: int = 2,
):
    """Insert a ReservationProjection directly for testing."""
    from app.models.reservation import ReservationProjection

    rp = ReservationProjection(
        booking_id=booking_id,
        room_type_id=room_type_id,
        check_in=check_in,
        check_out=check_out,
        status=status,
        guest_count=guest_count,
    )
    db.add(rp)
    await db.commit()
    return rp
