"""Core test fixtures for the HotelBook test suite.

Uses a real PostgreSQL database (from Docker Compose) with FastAPI
dependency overrides for session management. Each test runs in a
nested savepoint that rolls back after the test.
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
