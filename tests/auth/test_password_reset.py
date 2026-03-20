"""RED phase: Password reset import and basic behavior tests.

These tests verify that the password reset module exists and exports
the expected functions. They will FAIL until the implementation is created.
"""

import pytest


class TestPasswordResetImports:
    """Verify password reset module exports exist."""

    def test_password_reset_imports(self):
        from app.services.password_reset import (
            request_password_reset,
            confirm_password_reset,
        )
        assert callable(request_password_reset)
        assert callable(confirm_password_reset)

    def test_email_service_imports(self):
        from app.services.email import (
            send_password_reset_email,
            send_invite_email,
        )
        assert callable(send_password_reset_email)
        assert callable(send_invite_email)

    def test_invite_service_imports(self):
        from app.services.invite import create_invite, accept_invite
        assert callable(create_invite)
        assert callable(accept_invite)

    def test_invite_router_imports(self):
        from app.api.v1.invite import router
        assert router is not None
