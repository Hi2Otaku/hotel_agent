---
phase: 10-deploy-to-online-test-server
plan: 02
subsystem: infra
tags: [docker, seeding, inter-service, demo-data, compose]

# Dependency graph
requires:
  - phase: 08-containerize-and-ci
    provides: Docker Compose base config and production overlay
  - phase: 04-booking-management
    provides: Booking model and seed_bookings infrastructure
provides:
  - Demo guest account seeding in auth service
  - Booking seed linked to real guest accounts via inter-service lookup
  - Production compose with env-var secrets for EC2 deployment
affects: [10-deploy-to-online-test-server]

# Tech tracking
tech-stack:
  added: []
  patterns: [inter-service demo data lookup, idempotent seed with cross-service dependency]

key-files:
  created:
    - services/auth/app/services/seed_guests.py
  modified:
    - services/auth/app/main.py
    - services/auth/app/api/v1/users.py
    - services/booking/app/services/seed_bookings.py
    - services/booking/app/core/config.py
    - docker-compose.prod.yml
    - docker-compose.yml

key-decisions:
  - "Unauthenticated /demo-guests endpoint for inter-service booking seed lookup (only returns demo account IDs, not sensitive data)"
  - "Booking seed gracefully falls back to random UUIDs when auth service unavailable"
  - "Single hash_password call shared across all 8 demo guests (same password)"

patterns-established:
  - "Inter-service seed lookup: booking service calls auth /demo-guests to get real user IDs for seeded bookings"
  - "Env-var secret override: ${VAR:-default} pattern in prod compose with dev-matching defaults"

requirements-completed: [DEPLOY-03, DEPLOY-04]

# Metrics
duration: 3min
completed: 2026-03-22
---

# Phase 10 Plan 02: Demo Data Seeding and Production Compose Hardening Summary

**8 demo guest accounts seeded on auth startup, booking seed linked to real guest IDs via inter-service lookup, production compose hardened with env-var secrets**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T16:24:53Z
- **Completed:** 2026-03-22T16:27:33Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Auth service seeds 8 demo guest accounts (@demo.hotelbook.com) on startup with idempotency
- Booking seed fetches real demo guest IDs from auth service and links historical bookings to actual accounts
- Production compose overrides all DB and RabbitMQ passwords via env vars, removes SSL artifacts for HTTP-only test server

## Task Commits

Each task was committed atomically:

1. **Task 1: Create demo guest account seeding for auth service** - `dd940ad` (feat)
2. **Task 2: Harden production compose with env-var secrets and HTTP-only config** - `b2bfb57` (feat)
3. **Task 3: Link historical booking seed to real demo guest accounts** - `df84e60` (feat)

## Files Created/Modified
- `services/auth/app/services/seed_guests.py` - Demo guest seeding module (8 accounts, idempotent)
- `services/auth/app/main.py` - Lifespan calls seed_demo_guests after admin seed
- `services/auth/app/api/v1/users.py` - /demo-guests endpoint for inter-service lookup
- `services/booking/app/services/seed_bookings.py` - _fetch_demo_guest_ids + linked booking creation
- `services/booking/app/core/config.py` - AUTH_SERVICE_URL for inter-service communication
- `docker-compose.prod.yml` - Env-var secrets, HTTP-only, no letsencrypt
- `docker-compose.yml` - AUTH_SERVICE_URL added to booking service

## Decisions Made
- Used unauthenticated /demo-guests endpoint placed before /{user_id} route to avoid path conflict
- Booking seed falls back to random UUIDs if auth service unavailable (graceful degradation)
- Added AUTH_SERVICE_URL to both dev and prod compose for consistency

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added AUTH_SERVICE_URL to docker-compose.yml and docker-compose.prod.yml**
- **Found during:** Task 3
- **Issue:** Plan specified adding AUTH_SERVICE_URL to booking config.py but didn't mention adding it to Docker Compose environment variables, which is required for the config to actually receive the value
- **Fix:** Added AUTH_SERVICE_URL: http://auth:8000 to booking service in both compose files
- **Files modified:** docker-compose.yml, docker-compose.prod.yml
- **Verification:** grep confirms AUTH_SERVICE_URL present in both files
- **Committed in:** df84e60 (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Essential for booking-to-auth inter-service communication to work. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Demo data pipeline complete: auth seeds guests, booking seeds linked historical data
- Production compose ready for EC2 deployment with real secrets via .env
- Next plan (10-03) can proceed with actual deployment

---
*Phase: 10-deploy-to-online-test-server*
*Completed: 2026-03-22*
