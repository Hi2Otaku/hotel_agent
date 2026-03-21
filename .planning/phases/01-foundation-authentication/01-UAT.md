---
status: complete
phase: 01-foundation-authentication
source: 01-01-SUMMARY.md, 01-02-SUMMARY.md, 01-03-SUMMARY.md
started: 2026-03-21T10:45:00Z
updated: 2026-03-21T11:15:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Run `docker compose up -d --build`. All containers should start healthy. Auth service seeds admin on startup.
result: issue (fixed)
reported: "auth, room, and booking service containers fail to start. Three issues: (1) PYTHONPATH=/app missing in Dockerfiles causing Alembic ModuleNotFoundError, (2) SQLAlchemy Enum columns missing values_callable sending uppercase names instead of lowercase values, (3) sa.Enum in migrations auto-creating types during create_table causing DuplicateObjectError. Fixed all three, all 10 containers now running."
severity: blocker

### 2. Guest Registration
expected: POST to gateway `/api/v1/auth/register` returns 201 with access_token JWT.
result: pass

### 3. Guest Login
expected: POST to gateway `/api/v1/auth/login` with OAuth2 form returns 200 with access_token JWT.
result: pass

### 4. Authenticated Profile Access
expected: GET `/api/v1/auth/me` with Bearer token returns 200 with user profile. Without token returns 401.
result: pass

### 5. RBAC - Guest Cannot Access Admin Endpoints
expected: GET `/api/v1/users/` with guest token returns 403. Admin token returns 200 with user list.
result: pass

### 6. Password Reset Request
expected: POST `/api/v1/auth/password-reset/request` returns 200. Mailpit receives reset email.
result: pass

### 7. Password Reset Confirm
expected: POST `/api/v1/auth/password-reset/confirm` with token resets password. Token is single-use.
result: pass

### 8. Staff Invite Creation
expected: POST `/api/v1/invite/create` with admin token returns 200 with invite token. Guest token returns 403.
result: pass

### 9. Staff Invite Acceptance
expected: POST `/api/v1/invite/accept` creates staff account with assigned role. /me shows role="front_desk".
result: pass

### 10. Gateway Proxy Routing
expected: Gateway routes /api/v1/* to correct services. All 4 health endpoints respond 200.
result: pass

### 11. Integration Tests Pass
expected: Run `pytest tests/auth/ -v`. All 25 tests should pass.
result: issue
reported: "Only 4 of 25 tests pass. Most tests fail with asyncpg InterfaceError: cannot perform operation: another operation is in progress. Root cause: test conftest.py async session fixture shares a connection that gets into a bad state when multiple operations overlap. The API endpoints themselves all work correctly (verified via curl)."
severity: major

## Summary

total: 11
passed: 9
issues: 2
pending: 0
skipped: 0

## Gaps

- truth: "All containers start healthy, auth service seeds admin on startup"
  status: fixed
  reason: "Three issues found and fixed inline: (1) PYTHONPATH=/app missing in Dockerfiles, (2) SQLAlchemy Enum values_callable missing, (3) sa.Enum auto-creating types in migrations. All fixed, all containers running."
  severity: blocker
  test: 1
  root_cause: "Multiple infrastructure issues in Dockerfiles, model Enum columns, and migration scripts"
  artifacts:
    - path: "services/auth/Dockerfile"
      issue: "Added ENV PYTHONPATH=/app"
    - path: "services/room/Dockerfile"
      issue: "Added ENV PYTHONPATH=/app"
    - path: "services/booking/Dockerfile"
      issue: "Added ENV PYTHONPATH=/app"
    - path: "services/auth/app/models/user.py"
      issue: "Added values_callable to Enum columns"
    - path: "services/auth/app/models/token.py"
      issue: "Added values_callable to Enum columns"
    - path: "services/room/app/models/room.py"
      issue: "Added values_callable to Enum columns"
    - path: "services/room/app/models/status_log.py"
      issue: "Added values_callable to Enum columns"
    - path: "services/booking/app/models/booking.py"
      issue: "Added values_callable to Enum columns"
    - path: "services/room/alembic/versions/001_initial_room_models.py"
      issue: "Switched sa.Enum to postgresql.ENUM with create_type=False"
    - path: "services/booking/alembic/versions/001_initial_booking_models.py"
      issue: "Switched sa.Enum to postgresql.ENUM with create_type=False"
  missing: []

- truth: "All 25 integration tests pass"
  status: failed
  reason: "User reported: Only 4 of 25 tests pass. Most tests fail with asyncpg InterfaceError: cannot perform operation: another operation is in progress."
  severity: major
  test: 11
  root_cause: "Test conftest.py async session fixture uses a shared async connection that gets into a bad state. The get_db dependency override and async session setup don't properly isolate concurrent operations on the asyncpg connection."
  artifacts:
    - path: "tests/conftest.py"
      issue: "Async session fixture connection sharing causes InterfaceError"
    - path: "tests/auth/conftest.py"
      issue: "admin_token fixture triggers overlapping operations on shared connection"
  missing:
    - "Fix async session isolation in test conftest — each test needs its own connection or proper transaction rollback"
