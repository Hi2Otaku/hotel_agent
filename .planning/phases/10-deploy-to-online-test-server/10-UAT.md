---
status: complete
phase: 10-deploy-to-online-test-server
source: 10-01-SUMMARY.md, 10-02-SUMMARY.md
started: 2026-03-22T17:00:00Z
updated: 2026-03-22T17:15:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Server Setup Script Exists and Is Executable
expected: `scripts/setup-server.sh` exists with Docker install, 2GB swap creation, repo clone to /opt/hotelbook, and keys directory. `bash -n scripts/setup-server.sh` passes with no syntax errors.
result: pass

### 2. Production Environment Template
expected: `.env.production.template` exists and documents all required secrets: AUTH_DB_PASSWORD, ROOM_DB_PASSWORD, BOOKING_DB_PASSWORD, RABBITMQ_PASS, ADMIN_EMAIL, ADMIN_PASSWORD, JWT_PRIVATE_KEY, JWT_PUBLIC_KEY. Each has a CHANGE_ME placeholder.
result: issue
reported: "No JWT keys in template, has MINIO instead"
severity: major

### 3. CI/CD Deploy Job Injects Secrets
expected: `.github/workflows/ci.yml` deploy job uses `appleboy/ssh-action` with `envs:` parameter listing at least 8 secret variables. The script writes an .env file and JWT key files from those env vars before running `docker compose up`.
result: pass

### 4. Demo Guest Accounts Seed on Startup
expected: `services/auth/app/services/seed_guests.py` creates 8 demo guest accounts with `@demo.hotelbook.com` emails. `services/auth/app/main.py` lifespan calls the seed function. Seeding is idempotent (won't duplicate on restart).
result: pass

### 5. Demo Guests Endpoint for Inter-Service Lookup
expected: `services/auth/app/api/v1/users.py` has a `/demo-guests` GET endpoint that returns demo account IDs. The endpoint is unauthenticated (no JWT required) since it only returns non-sensitive data.
result: pass

### 6. Booking Seed Links to Real Guest Accounts
expected: `services/booking/app/services/seed_bookings.py` calls the auth service `/demo-guests` endpoint to fetch real guest IDs before creating bookings. Falls back to random UUIDs if auth service unavailable. `services/booking/app/core/config.py` has AUTH_SERVICE_URL setting.
result: pass

### 7. Production Compose Overrides Passwords from Env Vars
expected: `docker-compose.prod.yml` overrides auth_db, room_db, booking_db, and rabbitmq passwords using `${VAR:-default}` pattern. Port 443 and letsencrypt volume are removed (HTTP-only).
result: pass

### 8. Dev Compose Still Works with Defaults
expected: Running `docker compose config` (dev compose only) completes without errors. All services have their default dev passwords inline.
result: pass

### 9. Production Compose Config Merges Correctly
expected: Running `docker compose -f docker-compose.yml -f docker-compose.prod.yml config` completes without errors and shows the merged configuration with env-var substitution patterns.
result: pass

### 10. Post-Deploy Health Check in CI
expected: `.github/workflows/ci.yml` has a health check step after the deploy that curls `/health` on the deployed server to verify it's running.
result: pass

## Summary

total: 10
passed: 9
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: ".env.production.template documents JWT_PRIVATE_KEY and JWT_PUBLIC_KEY"
  status: failed
  reason: "User reported: No JWT keys in template, has MINIO instead"
  severity: major
  test: 2
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""
