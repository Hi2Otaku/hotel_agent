"""Auth-specific test fixtures."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tests.conftest import TEST_DB_URL


@pytest.fixture
async def registered_guest(client):
    """Register a guest user and return (user_data, token)."""
    payload = {
        "email": "guest@test.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "Guest",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return payload, token


@pytest.fixture
async def admin_token(client):
    """Create an admin user and return their JWT token.

    Seeds the admin via the service layer, then logs in to get a token.
    """
    from app.services.user import get_or_create_admin

    # Create admin directly via service layer using a separate session
    engine = create_async_engine(TEST_DB_URL, echo=False)
    sf = async_sessionmaker(engine, expire_on_commit=False)
    async with sf() as session:
        await get_or_create_admin(session, "admin@hotel.local", "admin123")
    await engine.dispose()

    # Login as admin
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@hotel.local", "password": "admin123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]
