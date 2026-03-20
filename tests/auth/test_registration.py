"""Integration tests for user registration (AUTH-01)."""

import pytest


class TestRegistration:
    """Test suite for the POST /api/v1/auth/register endpoint."""

    async def test_register_success(self, client):
        """Registering with valid data returns 201 and a JWT token."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@test.com",
                "password": "securepass123",
                "first_name": "New",
                "last_name": "User",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client):
        """Registering with an already-used email returns 409."""
        payload = {
            "email": "dup@test.com",
            "password": "securepass123",
            "first_name": "Dup",
            "last_name": "User",
        }
        await client.post("/api/v1/auth/register", json=payload)
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"].lower()

    async def test_register_short_password(self, client):
        """Registering with a password under 8 chars returns 422."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@test.com",
                "password": "short",
                "first_name": "S",
                "last_name": "P",
            },
        )
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client):
        """Registering with an invalid email format returns 422."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "securepass123",
                "first_name": "Bad",
                "last_name": "Email",
            },
        )
        assert resp.status_code == 422
