# Legacy Tests Directory

**These tests have been superseded by per-service test suites.**

Tests are now located inside each service directory:

- `services/auth/tests/` -- Auth service tests
- `services/room/tests/` -- Room service tests
- `services/booking/tests/` -- Booking service tests
- `services/gateway/tests/` -- Gateway service tests
- `services/chat/tests/` -- Chat service tests

To run tests for a specific service:

```bash
cd services/{service}
uv run pytest tests/ -x
```

This directory will be removed in a future cleanup.
