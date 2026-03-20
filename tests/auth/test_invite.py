"""Integration tests for staff invite flow (AUTH-04)."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.token import PasswordResetToken, StaffInviteToken
from app.models.user import UserRole


class TestStaffInvite:
    """Staff invite creation and acceptance tests."""

    async def test_admin_can_create_invite(self, client, admin_token):
        """Admin can create a staff invite."""
        resp = await client.post(
            "/api/v1/invite/create",
            json={"target_role": "manager"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body["message"].lower() or "invite" in body["message"].lower()

    async def test_guest_cannot_create_invite(self, client, registered_guest):
        """Guest user is forbidden from creating invites."""
        _, token = registered_guest
        resp = await client.post(
            "/api/v1/invite/create",
            json={"target_role": "manager"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    async def test_accept_invite_creates_staff(self, client, admin_token):
        """Accepting invite creates user with correct role and returns JWT."""
        # Create invite
        resp = await client.post(
            "/api/v1/invite/create",
            json={"target_role": "front_desk"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        message = resp.json()["message"]
        invite_token = message.split("Token: ")[-1] if "Token: " in message else None
        assert invite_token is not None

        # Accept invite
        resp = await client.post(
            "/api/v1/invite/accept",
            json={
                "token": invite_token,
                "email": "frontdesk@hotel.local",
                "password": "staffpass123",
                "first_name": "Front",
                "last_name": "Desk",
            },
        )
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]

        # Verify role
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "front_desk"

    async def test_accept_expired_invite(self, client, db_session, admin_token):
        """Expired invite is rejected."""
        # Get admin user id
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        admin_id = resp.json()["id"]

        raw_token = secrets.token_urlsafe(32)
        invite = StaffInviteToken(
            token_hash=PasswordResetToken.hash_token(raw_token),
            target_role=UserRole.MANAGER,
            created_by=uuid.UUID(admin_id),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),  # expired
        )
        db_session.add(invite)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/invite/accept",
            json={
                "token": raw_token,
                "email": "expired@hotel.local",
                "password": "staffpass123",
                "first_name": "Expired",
                "last_name": "Invite",
            },
        )
        assert resp.status_code == 400

    async def test_accept_used_invite(self, client, admin_token):
        """Already-used invite is rejected on second acceptance."""
        # Create and accept invite
        resp = await client.post(
            "/api/v1/invite/create",
            json={"target_role": "manager"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        message = resp.json()["message"]
        invite_token = message.split("Token: ")[-1]

        # First accept
        await client.post(
            "/api/v1/invite/accept",
            json={
                "token": invite_token,
                "email": "first@hotel.local",
                "password": "staffpass123",
                "first_name": "First",
                "last_name": "Accept",
            },
        )

        # Second accept with same token
        resp = await client.post(
            "/api/v1/invite/accept",
            json={
                "token": invite_token,
                "email": "second@hotel.local",
                "password": "staffpass123",
                "first_name": "Second",
                "last_name": "Accept",
            },
        )
        assert resp.status_code == 400

    async def test_invalid_target_role(self, client, admin_token):
        """Invalid target role is rejected."""
        resp = await client.post(
            "/api/v1/invite/create",
            json={"target_role": "superadmin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 400 or resp.status_code == 422
