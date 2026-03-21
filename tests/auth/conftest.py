"""Auth-specific test fixtures."""

import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker


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
