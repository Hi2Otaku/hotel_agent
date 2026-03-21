"""Room service test fixtures with mock JWT and role overrides."""

import asyncio
import os
import uuid

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
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
