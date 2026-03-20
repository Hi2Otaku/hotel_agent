# Phase 1: Foundation & Authentication - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Project scaffolding for a microservice architecture, database schema with async engine, and JWT authentication for guests and staff with role-based access (admin, manager, front desk). This phase delivers the auth service, API gateway skeleton, and shared infrastructure (Docker Compose, message queue setup, database-per-service).

</domain>

<decisions>
## Implementation Decisions

### Session Handling
- JWT tokens with 24-hour hard expiry (no sliding refresh)
- Same token duration for guests and staff
- On expired token: redirect to login page, return to original URL after re-login
- Access token + refresh token pattern not needed — hard expiry is sufficient

### Staff Roles & Permissions
- Three roles: admin, manager, front desk
- Admin: full access (system settings, user management, all operations)
- Manager: room/rate management, reports, bookings — no user management
- Front desk: bookings and check-in/out only — no room/rate CRUD, no reports, no user management, no rate overrides
- Staff accounts created via invite link from admin
- First admin account created via environment variable / config at deployment
- No staff self-registration

### Password Reset
- Full realistic flow: request form → token email → reset link → new password form
- Reset tokens valid for 15 minutes
- Email delivery via Mailpit (local SMTP trap with web UI)
- This sets the pattern for all simulated emails (booking confirmations, etc.)

### Project Structure — Microservices
- Four services: Auth, Room, Booking, Gateway/BFF
- Each service is its own repo (or directory for portfolio convenience — Claude's discretion on repo vs monorepo-with-services)
- Domain module organization within each service: app/auth/, app/rooms/, etc. with models, routes, services per module
- Docker Compose for local development — each service in its own container
- Database per service: separate PostgreSQL databases for auth, rooms, bookings
- Inter-service communication via message queue (RabbitMQ or Redis — Claude's discretion)
- Gateway/BFF handles routing to services and serves the frontend

### Claude's Discretion
- Message queue choice (RabbitMQ vs Redis Streams)
- Whether to use monorepo with service directories or separate repos (considering portfolio reviewability)
- Exact Docker Compose configuration
- Database migration tooling per service (Alembic)
- Shared library/package strategy across services
- JWT signing key distribution across services

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements fully captured in decisions above.

### Project research (internal)
- `.planning/research/STACK.md` — Technology stack with versions (FastAPI 0.135, SQLAlchemy 2.0, asyncpg, pwdlib)
- `.planning/research/ARCHITECTURE.md` — System architecture patterns, three-layer backend design
- `.planning/research/PITFALLS.md` — FastAPI async/sync mismatch warning, pessimistic locking patterns

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project, no existing code

### Established Patterns
- None — this phase establishes all patterns

### Integration Points
- Auth service provides JWT verification that all other services will consume
- Message queue setup is shared infrastructure for service communication
- Docker Compose defines the local development environment for all phases

</code_context>

<specifics>
## Specific Ideas

- Mailpit for email simulation — provides a web UI to view sent emails, more portfolio-impressive than console logging
- Microservice architecture with message queue demonstrates distributed systems knowledge
- Database-per-service pattern shows proper service isolation
- Invite link for staff creation demonstrates a real-world onboarding pattern

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-authentication*
*Context gathered: 2026-03-20*
