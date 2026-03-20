# Project Research Summary

**Project:** HotelBook — Hotel Reservation Application
**Domain:** Single-property hotel reservation system (guest booking + staff dashboard)
**Researched:** 2026-03-20
**Confidence:** HIGH

## Executive Summary

HotelBook is a full-stack web application with two distinct user surfaces: a guest-facing booking site and a staff management dashboard backed by a shared FastAPI + PostgreSQL API. Research across all four domains converges on the same conclusion: this is a well-understood problem domain with clearly documented patterns, but it contains several non-obvious correctness traps that cannot be retrofitted later. The recommended approach is a React 19 SPA (Vite 8 + Tailwind 4 + shadcn/ui) consuming a FastAPI 0.135 backend with SQLAlchemy 2.0 async + PostgreSQL 16, deployed on Railway or Render. Every layer of the stack has a clear best practice in 2026, and the version choices are specific — notably, passlib/python-jose are dead and must not be used.

The most important architectural insight from research is that correctness must be designed in from day one, not added later. Three problems — double-booking via race conditions, date range off-by-one errors, and broken booking state machines — are impossible to fix cheaply after the data model is in place. The booking system must use pessimistic locking (`SELECT ... FOR UPDATE`) on availability checks, half-open date intervals (`[check_in, check_out)`) enforced by database constraints, and an explicit state machine enum with a single validated transition function. These are not optimizations; they are correctness requirements.

Feature scope is deliberately constrained to a single property, which is the right call. The research shows that multi-property support, real payment processing, and third-party OTA integrations all introduce architectural changes that would double complexity without proportionate portfolio value. The MVP delivers a complete booking loop (search, book, pay mock, confirm, manage) plus a staff dashboard (reservations, check-in/out, room/rate CRUD). Features like reporting, visual availability calendars, and analytics charts are high-value differentiators that belong in v1.x after the core loop is solid.

## Key Findings

### Recommended Stack

The stack is modern async Python on the backend and TypeScript React on the frontend, with a clear separation of concerns between server state (TanStack Query) and client UI state (Zustand). FastAPI with SQLAlchemy 2.0 async is the correct choice for demonstrating modern Python patterns; Django would obscure the async architecture. On the frontend, Vite 8 (Rolldown-based, 10-30x faster builds) replaces CRA entirely, and shadcn/ui provides accessible, customizable components without locking the project into a heavy design system dependency. Two library choices require specific attention: use `pwdlib[argon2]` (not passlib, which is dead) and `PyJWT` (not python-jose, which is unmaintained). Python 3.12 is the safe version — 3.13 has edge-case issues with C extensions.

**Core technologies:**
- Python 3.12 + FastAPI 0.135: Backend API — async-first, Pydantic-native, automatic OpenAPI docs
- SQLAlchemy 2.0 + asyncpg + Alembic: Data layer — async ORM, 5x faster than psycopg3, versioned migrations
- PostgreSQL 16: Persistence — ACID transactions, row locking (`FOR UPDATE`), native daterange type, GiST indexes
- React 19.2 + Vite 8 + TypeScript: Frontend — industry standard SPA with Rolldown-speed builds
- TanStack Query 5 + Zustand 5: State management — server state cached and refetched automatically; client UI state minimal and hook-based
- React Hook Form 7.71 + Zod 4: Form handling — minimal re-renders, shared schema validation between forms and API parsing
- Tailwind CSS 4 + shadcn/ui: Styling — utility-first, full code ownership of components, accessible by default
- pwdlib[argon2] + PyJWT: Auth security — replaces deprecated passlib and python-jose

### Expected Features

Research identifies a hard line between what guests and staff take for granted (table stakes) and what separates this from a basic CRUD app (differentiators). The full feature dependency graph is documented in FEATURES.md; the key insight is that Room Management CRUD must be seeded before any guest-facing search works, so staff tooling is a prerequisite for guest tooling.

**Must have (table stakes — v1):**
- Date-based room search with real-time availability — the core interaction; missing it means no product
- Room listing with photos, amenities, and pricing — guests cannot choose without this
- Complete multi-step booking flow (select, details, mock payment, confirmation) — end-to-end guest journey
- Guest auth (register, login, JWT) — required for booking management
- Guest booking management (view, cancel) — proves the system works end-to-end
- Mock payment flow (Stripe-like UI, simulated processing) — visually identical to real checkout
- Responsive/mobile-first design — majority of hotel booking traffic is mobile
- Staff auth with role-based access control (admin / manager / front desk) — security foundation
- Staff reservation list with search, filter, and status management — core daily operation
- Check-in / check-out workflow — the primary front desk task
- Room management CRUD (room types, individual rooms, base rates) — prerequisite for everything else
- Booking confirmation with cancellation policy display — users need proof and policy before committing

**Should have (differentiators — v1.x):**
- Rate management with seasonal/dynamic pricing — demonstrates business logic depth
- Room status board with housekeeping tracking — operational dashboard showcase
- Booking modification with price recalculation — real-world complexity
- Mock email notification system with viewable log — shows integration pattern knowledge
- Basic reporting dashboard (occupancy rate, revenue summary, booking trends) — data visualization showcase
- Guest profile view for staff — aggregates booking history

**Defer (v2+):**
- Visual availability calendar (Gantt-style timeline) — high complexity, high wow-factor, needs data volume
- Interactive analytics charts — requires meaningful reservation data to look good
- Guest-facing pricing calendar widget — polish, not core functionality
- Audit log for staff actions — security feature, low urgency
- PWA support — enhancement over responsive web

### Architecture Approach

The system follows a clean three-layer backend (Router -> Service -> ORM) with no layer skipping, a single PostgreSQL database, and two React SPAs sharing the same FastAPI backend via role-based routing. The guest app and staff app can be the same React build with role-based route trees, which is simpler than two separate builds. Business logic lives exclusively in the service layer — routers are thin HTTP adapters. The database schema uses a `room_inventory` table (room_type_id + date -> available_count) rather than tracking every physical room for availability, which is the correct tradeoff for a single property. Individual room assignment only matters at check-in.

**Major components:**
1. Guest Booking SPA — room search, multi-step booking wizard (BookingContext), guest account management
2. Staff Dashboard SPA — reservations table, check-in/out, room/rate CRUD, reporting charts
3. FastAPI API layer — four domain routers (Auth, Booking, Room, Reporting), versioned under `/api/v1/`
4. Service layer — all business logic: availability validation, booking state machine, pricing engine, reporting aggregations
5. SQLAlchemy 2.0 + PostgreSQL — async ORM with pessimistic locking on availability writes, Alembic migrations
6. Mock services — payment (Stripe-like interface) and email (background task queue) built to be swappable

### Critical Pitfalls

1. **Double-booking via race conditions** — Use `SELECT ... FOR UPDATE` within a transaction for every availability check + reservation insert. This must be in the initial booking implementation, not retrofitted. An atomic `UPDATE inventory SET available_count = available_count - 1 WHERE available_count > 0` is an acceptable simpler alternative.

2. **Broken date range logic (night vs. day)** — Model all date ranges as half-open intervals `[check_in, check_out)`. Enforce `check_out > check_in` as a database CHECK constraint. Use PostgreSQL's `daterange` type with `&&` for overlap queries. Write explicit tests for back-to-back bookings (checkout day = next check-in day, must NOT conflict).

3. **Missing booking state machine** — Use a PostgreSQL ENUM for status; define valid transitions in a dictionary; create a single `transition_booking_state()` function that validates before applying. Direct `UPDATE booking SET status = X` outside this function must never happen. PENDING bookings must expire via a background task (abandoned cart protection).

4. **Pricing calculation inconsistencies** — Single `calculate_price()` function used everywhere, no exceptions. Snapshot the price breakdown into the reservation at confirmation time. Never recalculate a confirmed booking's price from current rates. Seasonal pricing iterates over each night individually.

5. **Sync/async mismatch in FastAPI + SQLAlchemy** — Use `AsyncSession` and `create_async_engine` with `asyncpg` throughout from day one. A sync `Session` inside an `async def` endpoint blocks the event loop and causes hangs under any concurrent load. This must be set up correctly in the foundation phase — it cannot be retrofitted without rewriting every database interaction.

## Implications for Roadmap

Research strongly supports a build-order-driven phase structure where each phase delivers a testable vertical slice. The architecture's own build order (models -> auth -> rooms -> booking -> payment -> guest frontend -> staff API -> staff frontend -> polish) maps cleanly to phases. Critically, several correctness guarantees (locking, state machine, date convention, async setup) must be established in early phases — they are not polish.

### Phase 1: Foundation — Data Layer + Auth
**Rationale:** Everything in the system depends on the database schema and authentication. These cannot be changed cheaply after later phases build on them. The async database setup, UUID identifiers, date range convention, and booking state machine enum must be established here.
**Delivers:** PostgreSQL schema with migrations, AsyncSession configuration, JWT auth (register/login), role-based access control dependencies, booking state machine enum and transition validator
**Addresses:** Staff auth with roles (table stakes prerequisite), all guest auth requirements
**Avoids:** Sync/async mismatch (Pitfall 6), date range convention debt (Pitfall 2), sequential integer ID exposure (security mistake), booking status as free-form string (anti-pattern 3)

### Phase 2: Room Inventory + Availability API
**Rationale:** Guest booking depends on room search. Staff room management CRUD must exist before guest search can return results. Availability queries are the correctness-critical queries — the locking and indexing strategy must be established here, not in Phase 3.
**Delivers:** Room types CRUD, individual room management, room inventory table, date-range availability query with `FOR UPDATE` locking, GiST index on daterange, base rate management
**Addresses:** Room management CRUD (table stakes), room listing with details (table stakes), real-time availability display (table stakes)
**Avoids:** Availability calculation that does not block PENDING rooms (Pitfall 5), N+1 queries in room listing (performance trap)

### Phase 3: Core Booking Flow
**Rationale:** The central transaction of the entire system. The state machine, pricing snapshot, and overbooking prevention from Phases 1 and 2 are consumed here. This is the highest-risk phase from a correctness standpoint and should be built before any frontend work obscures the backend logic.
**Delivers:** Booking creation (PENDING), mock payment endpoint (PENDING -> CONFIRMED), booking state transitions, price snapshot on confirmation, PENDING expiration background task, idempotency key handling, mock email trigger
**Addresses:** Complete booking flow (table stakes), mock payment flow (table stakes), booking confirmation (table stakes), cancellation flow
**Avoids:** Double-booking race conditions (Pitfall 1), pricing inconsistencies (Pitfall 4), duplicate submission (UX pitfall), missing PENDING expiration (technical debt)

### Phase 4: Guest Frontend
**Rationale:** All backend APIs for the guest journey are now available. Build the complete React guest experience consuming the stable API. BookingContext for wizard state, TanStack Query for server data, React Hook Form + Zod for forms.
**Delivers:** Home page + search UI, room listing and detail pages, multi-step booking wizard (BookingContext), mock payment form (Stripe-like UI), confirmation page, guest auth pages (register/login), My Bookings page (view + cancel)
**Addresses:** Date-based room search (table stakes), responsive/mobile design (table stakes), multi-step booking flow UX (table stakes), guest booking management (table stakes)
**Avoids:** Prop drilling through booking wizard (anti-pattern 4), one giant component per page (anti-pattern 5), JavaScript Date objects in API calls (integration gotcha), requiring login before showing availability (UX pitfall)

### Phase 5: Staff Dashboard
**Rationale:** Staff features build on the booking data created in Phase 3. Check-in/out are state machine transitions already implemented in Phase 3 — the staff frontend just calls them. Reporting aggregations can be built now that booking data exists.
**Delivers:** Staff reservation list (search, filter, sort, pagination), check-in / check-out workflow, room status board, housekeeping status tracking, guest profile view, basic reporting (occupancy rate, revenue summary)
**Addresses:** Reservation list with search/filter (table stakes), check-in/out workflow (table stakes), room status board (table stakes), basic reporting (table stakes), guest profile view (table stakes)
**Avoids:** No pagination on reservation listing (performance trap), staff role escalation via API (security mistake), loading full objects when only counts needed (performance trap)

### Phase 6: Business Logic Depth (v1.x)
**Rationale:** Core loop is solid. Add the differentiators that elevate this from a CRUD demo to a production-quality system. Seasonal pricing builds on the base rate structure from Phase 2. Booking modification requires the pricing function from Phase 3. Analytics charts require the data volume from Phases 3-5.
**Delivers:** Seasonal / dynamic rate management, booking modification with price recalculation, mock email notification log (viewable queue), reporting dashboard with 3-4 charts (Recharts or Chart.js), audit log for staff actions
**Addresses:** Rate management with seasonal pricing (differentiator), booking modification (differentiator), email notification system (differentiator), dashboard analytics (differentiator)
**Avoids:** Pricing recalculation inconsistencies on modification (Pitfall 4), rate changes retroactively affecting confirmed bookings (snapshot already in place from Phase 3)

### Phase 7: Polish + Deployment
**Rationale:** Final hardening for portfolio presentation. CI/CD, error handling, loading states, CORS lockdown, and deployment to Railway or Render.
**Delivers:** GitHub Actions CI (lint, test, build), Docker Compose dev environment, deployment to Railway/Render, comprehensive error handling and loading states, CORS configuration with explicit allowed origins, pre-commit hooks (Ruff, ESLint)
**Addresses:** Responsive design final pass, E2E tests with Playwright, concurrent booking stress test
**Avoids:** CORS misconfiguration (integration gotcha), missing loading states causing duplicate submissions (UX pitfall)

### Phase Ordering Rationale

- Phases 1-3 are backend-only and must be done in order because each creates the data contracts consumed by the next. No frontend work until the API is stable.
- Phase 4 (guest frontend) precedes Phase 5 (staff dashboard) because the guest booking loop generates the reservation data the staff dashboard needs to look meaningful during development.
- Phase 6 requires Phases 1-5 to be complete because seasonal pricing modifies the availability and pricing functions established earlier, and booking modification requires the state machine and price snapshot from Phase 3.
- Reporting (Phase 5/6) is explicitly deferred until booking data exists — charts with empty data communicate nothing.
- The PENDING expiration background task is in Phase 3, not Phase 7, because it is a correctness requirement, not a polish feature.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 6 (reporting/analytics):** Charting library selection (Recharts vs. Chart.js vs. Victory) and specific chart types for occupancy/ADR/RevPAR metrics may benefit from a focused research pass. SQL aggregation query patterns for hotel KPIs are non-obvious.
- **Phase 3 (PENDING expiration):** FastAPI BackgroundTasks vs. a dedicated task queue (Celery, ARQ) for the expiration job. For portfolio scale, BackgroundTasks is sufficient, but the tradeoff should be documented in the phase plan.

Phases with standard patterns (skip research-phase):
- **Phase 1 (foundation):** FastAPI + SQLAlchemy 2.0 async setup is thoroughly documented with official sources. Patterns are established.
- **Phase 2 (room inventory):** CRUD patterns with FastAPI routers and service layer are standard. The availability query pattern is documented in ARCHITECTURE.md with specific SQL.
- **Phase 4 (guest frontend):** React Hook Form + TanStack Query + Zustand patterns are well-documented. BookingContext wizard pattern is standard.
- **Phase 7 (deployment):** Railway/Render deployment with GitHub Actions is well-documented for this stack.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All version numbers verified against official release notes, npm, and PyPI. Specific deprecation warnings (passlib, python-jose, CRA) confirmed from official sources. |
| Features | HIGH | Cross-referenced against multiple hotel PMS and booking engine guides (Cloudbeds, AltexSoft, HotelMinder, SiteMinder). Feature boundaries are consistent across sources. |
| Architecture | HIGH | Patterns sourced from FastAPI official docs, well-maintained community best practices (zhanymkanov), and hotel-specific system design references (ByteByteGo, SystemDesignHandbook). |
| Pitfalls | HIGH | Concurrency and double-booking pitfalls verified across multiple independent sources including database-level implementation guides. Date range convention and state machine pitfalls are well-documented in production system post-mortems. |

**Overall confidence:** HIGH

### Gaps to Address

- **Image storage for room photos:** Research did not cover how room photos are stored and served. For portfolio scale, options include committing static images to the repo, using a public CDN URL, or integrating a simple file upload to a cloud storage bucket (S3/R2). This should be decided in Phase 2 planning.
- **Refresh token rotation strategy:** STACK.md recommends httpOnly cookie storage with refresh token rotation, but the exact rotation implementation (database-stored refresh tokens vs. stateless signed tokens with short TTL) was not fully specified. Decide during Phase 1 detailed planning.
- **Concurrent booking stress test tooling:** PITFALLS.md notes that manual testing is insufficient for validating the double-booking prevention. A specific tool (e.g., `asyncio.gather` in pytest, locust, or k6) for the concurrent test should be specified in Phase 3 planning.
- **Charting library:** Both Recharts and Chart.js are mentioned in FEATURES.md. A decision should be made in Phase 6 planning based on TypeScript support and bundle size tradeoffs.

## Sources

### Primary (HIGH confidence)
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/) — FastAPI 0.135.x, pwdlib/PyJWT recommendation
- [FastAPI Official Docs: Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) — router organization
- [FastAPI Official Docs: SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) — SQLAlchemy async integration
- [SQLAlchemy Download](https://www.sqlalchemy.org/download.html) — SQLAlchemy 2.0.48 confirmed
- [Alembic Documentation](https://alembic.sqlalchemy.org/) — 1.18.4 confirmed
- [React Versions](https://react.dev/versions) — React 19.2.x confirmed
- [Vite 8.0 Announcement](https://vite.dev/blog/announcing-vite8) — Vite 8 with Rolldown bundler
- [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4) — v4.0 confirmed
- [TanStack Query](https://tanstack.com/query/latest) — v5.91.x for React
- [React Router Changelog](https://reactrouter.com/changelog) — v7.13.x confirmed
- [Zod npm](https://www.npmjs.com/package/zod) — v4.3.6 confirmed
- [Vitest](https://vitest.dev/) — v4.1.0 confirmed

### Secondary (MEDIUM confidence)
- [FastAPI Best Practices (zhanymkanov)](https://github.com/zhanymkanov/fastapi-best-practices) — project structure conventions
- [Design Hotel Booking System (System Design Handbook)](https://www.systemdesignhandbook.com/guides/design-hotel-booking-system/) — system components and data flow
- [ByteByteGo Hotel Reservation System Design](https://bytebytego.com/courses/system-design-interview/hotel-reservation-system) — schema and concurrency patterns
- [How to Solve Race Conditions in a Booking System (HackerNoon)](https://hackernoon.com/how-to-solve-race-conditions-in-a-booking-system) — pessimistic locking patterns
- [Handling the Double-Booking Problem in Databases](https://adamdjellouli.com/articles/databases_notes/07_concurrency_control/04_double_booking_problem) — concurrency control
- [Setting up FastAPI with Async SQLAlchemy 2.0](https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308) — async patterns
- [Psycopg 3 vs Asyncpg benchmark](https://fernandoarteaga.dev/blog/psycopg-vs-asyncpg/) — asyncpg 5x faster confirmed
- [Cloudbeds - Hotel Reservation System Guide](https://www.cloudbeds.com/articles/hotel-reservation-system/) — feature landscape
- [AltexSoft - Hotel PMS Products and Features](https://www.altexsoft.com/blog/hotel-property-management-systems-products-and-features/) — feature scope
- [Baymard Institute - Travel Site UX Best Practices](https://baymard.com/blog/travel-site-ux-best-practices) — UX pitfalls
- [Hotel Reservation Schema Design (PostgreSQL)](https://dev.to/chandra179/hotel-reservation-schema-design-postgresql-3i9j) — schema patterns
- [Red Gate - Data Model for Hotel Management System](https://www.red-gate.com/blog/data-model-for-hotel-management-system/) — entity relationships

---
*Research completed: 2026-03-20*
*Ready for roadmap: yes*
