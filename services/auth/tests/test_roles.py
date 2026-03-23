"""Integration tests for role-based access control (AUTH-04)."""

import pytest


class TestRoles:
    """Test suite for RBAC enforcement on protected endpoints."""

    async def test_admin_login(self, client, admin_token):
        """Admin login returns a JWT with role=admin in /me response."""
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    async def test_admin_can_list_users(self, client, admin_token):
        """Admin can access the user list endpoint."""
        resp = await client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "users" in resp.json()

    async def test_guest_cannot_list_users(self, client, registered_guest):
        """Guest users get 403 when trying to list users."""
        _, token = registered_guest
        resp = await client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    async def test_unauthenticated_cannot_list_users(self, client):
        """Unauthenticated requests to user list get 401."""
        resp = await client.get("/api/v1/users/")
        assert resp.status_code == 401

    async def test_jwt_contains_role(self, client, admin_token):
        """Admin JWT payload contains role, sub, email, and exp claims."""
        import jwt

        payload = jwt.decode(admin_token, options={"verify_signature": False})
        assert payload["role"] == "admin"
        assert "sub" in payload
        assert "email" in payload
        assert "exp" in payload
