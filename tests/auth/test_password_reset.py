"""Integration tests for password reset flow (AUTH-03)."""

import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.models.token import PasswordResetToken
from app.services.user import get_user_by_email


class TestPasswordReset:
    """Password reset request and confirm tests."""

    async def test_request_reset_registered_email(self, client, registered_guest):
        """Requesting reset for registered email returns 200 and sends email."""
        user_data, _ = registered_guest
        with patch(
            "app.services.password_reset.send_password_reset_email",
            new_callable=AsyncMock,
        ) as mock_email:
            resp = await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": user_data["email"]},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert "sent" in body["message"].lower() or "reset" in body["message"].lower()
            mock_email.assert_called_once()

    async def test_request_reset_unknown_email(self, client):
        """Requesting reset for unknown email returns 200 (no info leakage)."""
        with patch(
            "app.services.password_reset.send_password_reset_email",
            new_callable=AsyncMock,
        ) as mock_email:
            resp = await client.post(
                "/api/v1/auth/password-reset/request",
                json={"email": "nobody@nowhere.com"},
            )
            assert resp.status_code == 200
            mock_email.assert_not_called()

    async def test_confirm_reset_valid_token(
        self, client, registered_guest, db_session
    ):
        """Valid reset token allows password change."""
        user_data, _ = registered_guest

        user = await get_user_by_email(db_session, user_data["email"])
        raw_token = secrets.token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=user.id,
            token_hash=PasswordResetToken.hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        db_session.add(reset)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": raw_token, "new_password": "newpassword123"},
        )
        assert resp.status_code == 200

        # Verify new password works
        resp = await client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": "newpassword123"},
        )
        assert resp.status_code == 200

    async def test_confirm_reset_expired_token(
        self, client, registered_guest, db_session
    ):
        """Expired token is rejected."""
        user_data, _ = registered_guest

        user = await get_user_by_email(db_session, user_data["email"])
        raw_token = secrets.token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=user.id,
            token_hash=PasswordResetToken.hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),  # expired
        )
        db_session.add(reset)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": raw_token, "new_password": "newpassword123"},
        )
        assert resp.status_code == 400

    async def test_confirm_reset_used_token(
        self, client, registered_guest, db_session
    ):
        """Already-used token is rejected."""
        user_data, _ = registered_guest

        user = await get_user_by_email(db_session, user_data["email"])
        raw_token = secrets.token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=user.id,
            token_hash=PasswordResetToken.hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            used=True,  # already used
        )
        db_session.add(reset)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": raw_token, "new_password": "newpassword123"},
        )
        assert resp.status_code == 400
