"""Auth service test fixtures.

Merged from root tests/conftest.py (DB engine, session, client) and
tests/auth/conftest.py (registered_guest, admin_token).
"""

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_db
from app.core.database import Base
from app.main import app

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://auth_user:auth_pass@localhost:5433/auth",
)


# ---------------------------------------------------------------------------
# Root fixtures (DB engine, session, client)
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine():
    """Create a test database engine and set up/tear down tables."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(test_engine):
    """Provide a database session for each test."""
    _session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    async with _session_maker() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="session")
async def client(test_engine):
    """Provide an async HTTP client with database dependency override.

    Each request gets its own connection + transaction that is rolled back
    after the request completes, keeping tests isolated.

    The client object has a ``_test_engine`` attribute for direct SQL access.
    """
    _session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_db():
        async with _session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac._test_engine = test_engine  # type: ignore[attr-defined]
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Auth-specific fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(loop_scope="session")
async def registered_guest(client):
    """Register a guest user and return (user_data, token).

    Idempotent: if the user already exists (409), logs in instead.
    """
    payload = {
        "email": "guest@test.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "Guest",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    if resp.status_code == 201:
        token = resp.json()["access_token"]
    elif resp.status_code == 409:
        # Already registered, just login
        login_resp = await client.post(
            "/api/v1/auth/login",
            data={"username": payload["email"], "password": payload["password"]},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
    else:
        raise AssertionError(f"Unexpected status {resp.status_code}: {resp.text}")
    return payload, token


@pytest_asyncio.fixture(loop_scope="session")
async def admin_token(client):
    """Create an admin user and return their JWT token.

    Seeds admin via the service layer using a dedicated session,
    then logs in through the API to get a proper JWT.
    """
    from app.services.user import get_or_create_admin

    engine = client._test_engine  # type: ignore[attr-defined]
    sf = async_sessionmaker(engine, expire_on_commit=False)
    async with sf() as session:
        await get_or_create_admin(session, "admin@hotel.local", "admin123")

    # Login as admin
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@hotel.local", "password": "admin123"},
    )
    assert resp.status_code == 200, f"Login failed {resp.status_code}: {resp.text}"
    return resp.json()["access_token"]
