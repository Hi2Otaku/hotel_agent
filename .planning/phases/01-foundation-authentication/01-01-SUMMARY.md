---
phase: 01-foundation-authentication
plan: 01
subsystem: infra, auth
tags: [docker-compose, fastapi, sqlalchemy, asyncpg, alembic, jwt, rs256, argon2, rabbitmq, mailpit, pydantic]

# Dependency graph
requires:
  - phase: none
    provides: greenfield project
provides:
  - Docker Compose orchestration for all 9 containers (3 DBs, RabbitMQ, Mailpit, 4 services)
  - Shared library with JWT verification, database helpers, messaging helpers
  - Auth service models (User with 4 roles, PasswordResetToken, StaffInviteToken)
  - Auth service security module (Argon2 hashing, RS256 JWT creation/verification)
  - FastAPI RBAC dependency chain (get_current_user, require_role)
  - Pydantic schemas for all auth request/response contracts
  - Alembic async migration configuration with initial migration
  - RSA key generation script
  - Stub services for Room, Booking, Gateway
affects: [01-02-PLAN, 01-03-PLAN, 02-room-management, 03-booking-engine, 04-gateway-integration]

# Tech tracking
tech-stack:
  added: [fastapi, sqlalchemy, asyncpg, alembic, pydantic-settings, pwdlib, PyJWT, aio-pika, fastapi-mail, uvicorn, httpx]
  patterns: [database-per-service, RS256 JWT with key distribution, async SQLAlchemy, Docker Compose healthchecks, Alembic async migrations, RBAC dependency chain]

key-files:
  created:
    - docker-compose.yml
    - shared/shared/jwt.py
    - shared/shared/database.py
    - shared/shared/messaging.py
    - services/auth/app/models/user.py
    - services/auth/app/models/token.py
    - services/auth/app/core/security.py
    - services/auth/app/core/config.py
    - services/auth/app/core/database.py
    - services/auth/app/api/deps.py
    - services/auth/app/schemas/auth.py
    - services/auth/app/schemas/user.py
    - services/auth/alembic/versions/001_initial_auth_models.py
    - scripts/generate_keys.sh
  modified: []

key-decisions:
  - "RS256 asymmetric JWT: Auth service signs with private key, other services verify with public key only"
  - "Database-per-service: 3 separate PostgreSQL containers for isolation"
  - "RabbitMQ for inter-service messaging with aio-pika async client"
  - "Mailpit for email simulation in development"
  - "BookingStatus enum defined in auth migration for cross-service availability"
  - "Manual Alembic migration file created (no live DB for autogenerate at scaffold time)"

patterns-established:
  - "Shared library pattern: shared/ package installed in each service Dockerfile"
  - "Config pattern: pydantic-settings BaseSettings with env_file support"
  - "Database pattern: shared create_db_engine/create_session_factory, per-service get_session"
  - "RBAC pattern: OAuth2PasswordBearer -> get_current_user -> require_role(*roles)"
  - "Docker entrypoint: alembic upgrade head before uvicorn start"
  - "JWT key distribution: keys/ dir mounted as /run/secrets volume"

requirements-completed: [AUTH-01, AUTH-02, AUTH-04]

# Metrics
duration: 5min
completed: 2026-03-20
---

# Phase 01 Plan 01: Infrastructure & Auth Foundation Summary

**Monorepo scaffold with Docker Compose (9 containers), shared JWT/DB library, Auth service models with Argon2/RS256 security and RBAC dependency chain, Alembic async migrations**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-20T15:43:45Z
- **Completed:** 2026-03-20T15:49:14Z
- **Tasks:** 2
- **Files modified:** 45

## Accomplishments
- Full monorepo with Docker Compose orchestrating 3 Postgres DBs, RabbitMQ, Mailpit, and 4 service containers
- Shared library providing JWT verification (RS256), async database helpers, and RabbitMQ messaging helpers
- Auth service with User model (4 roles), PasswordResetToken, StaffInviteToken, Argon2 hashing, RS256 JWT, and RBAC dependency chain
- Alembic async migration creating users, password_reset_tokens, and staff_invite_tokens tables plus user_role and bookingstatus enums
- Room, Booking, and Gateway stub services with health endpoints

## Task Commits

Each task was committed atomically:

1. **Task 1: Create monorepo structure, Docker Compose, shared library, and all service scaffolds** - `267b4a7` (feat)
2. **Task 2: Create Auth service models, schemas, security module, RBAC dependencies, and Alembic migrations** - `d6d6f99` (feat)

## Files Created/Modified
- `docker-compose.yml` - Full orchestration of 9 services with healthchecks and volumes
- `.env.example` - Template for all environment variables
- `.gitignore` - Excludes keys, Python artifacts, env files
- `scripts/generate_keys.sh` - RSA 2048-bit key pair generation
- `shared/shared/jwt.py` - JWT verification with RS256 public key
- `shared/shared/database.py` - Async engine, session factory, DeclarativeBase
- `shared/shared/messaging.py` - RabbitMQ connection, channel, exchange, queue helpers
- `shared/shared/schemas/user.py` - TokenPayload Pydantic model
- `services/auth/Dockerfile` - Auth service container with shared lib and migrations
- `services/auth/requirements.txt` - All auth service dependencies
- `services/auth/entrypoint.sh` - Alembic migrate then uvicorn start
- `services/auth/app/main.py` - FastAPI app with admin seeding lifespan
- `services/auth/app/core/config.py` - Settings with DB, JWT, mail, RabbitMQ config
- `services/auth/app/core/database.py` - Auth DB engine and session factory
- `services/auth/app/core/security.py` - Argon2 hashing and RS256 JWT
- `services/auth/app/models/user.py` - User model with UserRole and BookingStatus enums
- `services/auth/app/models/token.py` - PasswordResetToken and StaffInviteToken models
- `services/auth/app/schemas/auth.py` - Register, login, token, reset, invite schemas
- `services/auth/app/schemas/user.py` - UserResponse and UserListResponse schemas
- `services/auth/app/api/deps.py` - get_current_user, require_role, require_admin, require_staff
- `services/auth/alembic.ini` - Alembic config with async PostgreSQL URL
- `services/auth/alembic/env.py` - Async migration environment with model imports
- `services/auth/alembic/versions/001_initial_auth_models.py` - Initial migration
- `services/room/app/main.py` - Room service stub with health endpoint
- `services/booking/app/main.py` - Booking service stub with health endpoint
- `services/gateway/app/main.py` - Gateway service stub with health endpoint

## Decisions Made
- RS256 asymmetric JWT chosen so auth service holds private key while other services only need public key -- better security posture for microservices
- Separate PostgreSQL containers per service for true isolation (not shared instance with multiple databases)
- RabbitMQ over Redis Streams for guaranteed message delivery with acknowledgments
- BookingStatus enum placed in auth migration to ensure it exists as a PostgreSQL type early
- Manual Alembic migration created since autogenerate requires a live database connection
- Monorepo structure with shared/ package for cross-service code reuse

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Infrastructure ready: Docker Compose can bring up all containers
- Auth service models and security layer complete, ready for endpoint implementation in Plan 02
- RBAC dependencies ready for route consumption
- Shared library installed and importable by all services
- RSA keys can be generated with `bash scripts/generate_keys.sh`

## Self-Check: PASSED

All key files verified present. Both task commits (267b4a7, d6d6f99) confirmed in git log.

---
*Phase: 01-foundation-authentication*
*Completed: 2026-03-20*
