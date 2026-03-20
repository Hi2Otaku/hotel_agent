"""Integration tests for login and /me endpoint (AUTH-02)."""

import pytest


class TestLogin:
    """Test suite for POST /api/v1/auth/login and GET /api/v1/auth/me."""

    async def test_login_success(self, client, registered_guest):
        """Logging in with valid credentials returns 200 and a JWT token."""
        user_data, _ = registered_guest
        resp = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client, registered_guest):
        """Logging in with wrong password returns 401."""
        user_data, _ = registered_guest
        resp = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": "wrongpassword",
            },
        )
        assert resp.status_code == 401
        assert "invalid credentials" in resp.json()["detail"].lower()

    async def test_login_nonexistent_email(self, client):
        """Logging in with a non-existent email returns 401."""
        resp = await client.post(
            "/api/v1/auth/login",
            data={"username": "nobody@test.com", "password": "anypassword"},
        )
        assert resp.status_code == 401

    async def test_me_with_token(self, client, registered_guest):
        """GET /me with a valid JWT returns the user profile."""
        _, token = registered_guest
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "guest@test.com"
        assert data["role"] == "guest"

    async def test_me_without_token(self, client):
        """GET /me without a JWT returns 401."""
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401
