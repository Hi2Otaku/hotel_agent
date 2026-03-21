# Roadmap: HotelBook

## Overview

HotelBook delivers a full-stack hotel reservation application in 8 phases, moving from backend data contracts through guest and staff frontends to production deployment. The first four phases establish the API layer (auth, room management, availability, booking engine) because every frontend feature depends on stable, correctness-guaranteed backend services. Phases 5-6 build the two user-facing applications (guest SPA, staff dashboard) as vertical slices consuming those APIs. Phase 7 adds reporting analytics, and Phase 8 hardens everything for portfolio presentation with tests, CI/CD, and live deployment.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation & Authentication** - Project scaffolding, database schema, async setup, JWT auth for guests and staff
- [x] **Phase 2: Room & Rate Management** - Staff CRUD for room types, individual rooms, rates, and room status (completed 2026-03-21)
- [x] **Phase 3: Availability & Search** - Guest-facing room search with real-time availability engine and pricing calendar (completed 2026-03-21)
- [ ] **Phase 4: Booking Engine** - Complete booking lifecycle: creation, mock payment, confirmation, cancellation, modification
- [ ] **Phase 5: Guest Frontend** - React SPA for guest journey: search, booking wizard, account management, responsive design
- [ ] **Phase 6: Staff Dashboard** - Staff reservation management, check-in/out workflow, guest profiles
- [ ] **Phase 7: Reporting Dashboard** - Occupancy, revenue, and booking trend analytics for staff
- [ ] **Phase 8: Testing & Deployment** - Test suite, CI/CD pipeline, production deployment with live demo URL

## Phase Details

### Phase 1: Foundation & Authentication
**Goal**: Users can register, log in, and access role-appropriate parts of the application with sessions that persist across browser refreshes
**Depends on**: Nothing (first phase)
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04
**Success Criteria** (what must be TRUE):
  1. Guest can create an account with email and password, then log in and remain authenticated across browser sessions
  2. Guest can request a password reset and receive a simulated email link that allows setting a new password
  3. Staff member can log in and the system correctly identifies their role (admin, manager, or front desk)
  4. API rejects unauthenticated requests to protected endpoints and returns appropriate error responses
  5. Database schema is deployed via migrations, async engine is configured, and the booking state machine enum exists in the schema
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Monorepo scaffolding, Docker Compose, shared library, Auth models/migrations
- [ ] 01-02-PLAN.md — Auth service endpoints (register, login, RBAC) and integration tests
- [ ] 01-03-PLAN.md — Password reset flow, staff invite system, gateway proxy, remaining tests

### Phase 2: Room & Rate Management
**Goal**: Staff can fully manage the hotel's room inventory, room types, pricing, and room status through API endpoints
**Depends on**: Phase 1
**Requirements**: RMGT-01, RMGT-02, RMGT-03, RMGT-04, RATE-01, RATE-02
**Success Criteria** (what must be TRUE):
  1. Staff can create, edit, and delete room types with photos, amenities, and capacity details
  2. Staff can manage individual rooms (assign numbers, floors, and toggle status between available, occupied, cleaning, maintenance)
  3. Staff can view a room status board showing current state of all rooms
  4. Housekeeping status automatically marks rooms dirty on checkout and staff can toggle clean/inspected
  5. Staff can set base rates per room type and create seasonal pricing rules with date-range overrides and weekend surcharges
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md — Room service scaffolding, models, migrations, schemas, MinIO, Docker infrastructure
- [ ] 02-02-PLAN.md — Room type CRUD with photos, room management with status state machine, integration tests
- [ ] 02-03-PLAN.md — Rate management, pricing engine with multiplicative stacking, seed data, tests

### Phase 3: Availability & Search
**Goal**: Guests can search for available rooms by dates and filters, view room details, and see per-night pricing -- backed by a correctness-guaranteed availability engine
**Depends on**: Phase 2
**Requirements**: ROOM-01, ROOM-02, ROOM-03, ROOM-04
**Success Criteria** (what must be TRUE):
  1. Guest can search rooms by check-in date, check-out date, and guest count, and only available rooms are returned
  2. Guest can view room details including photos, amenities, capacity, and per-night price for their selected dates
  3. Guest can see a pricing calendar showing per-night rates and availability across a date range
  4. Availability queries use pessimistic locking (FOR UPDATE) to prevent double-booking at the database level
**Plans**: 3 plans

Plans:
- [ ] 03-01-PLAN.md — Reservation projection model, migration, RabbitMQ event consumer, availability query service
- [ ] 03-02-PLAN.md — Public search/detail/calendar endpoints, Pydantic schemas, integration tests
- [ ] 03-03-PLAN.md — Gateway BFF search aggregation endpoints, gateway test infrastructure

### Phase 4: Booking Engine
**Goal**: Guests can complete the full booking lifecycle -- from room selection through mock payment to confirmation -- and manage existing bookings (view, cancel, modify)
**Depends on**: Phase 3
**Requirements**: BOOK-01, BOOK-02, BOOK-03, BOOK-04, BOOK-05, MGMT-01, MGMT-02, MGMT-03
**Success Criteria** (what must be TRUE):
  1. Guest can complete a multi-step booking (select room, enter details, submit mock payment, receive confirmation with confirmation number)
  2. Guest completes a Stripe-like mock payment form that simulates card processing without real charges
  3. Guest receives a mock email confirmation after booking and sees the cancellation policy during the booking flow
  4. Guest can view upcoming and past bookings with status, cancel a booking (with policy enforcement), and modify dates/room with automatic price recalculation
  5. Booking state machine enforces valid transitions (PENDING -> CONFIRMED -> CHECKED_IN -> CHECKED_OUT, PENDING -> CANCELLED, etc.) and expired PENDING bookings are automatically cleaned up
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md — Booking service scaffolding, models, migrations, schemas, config, deps, email template
- [ ] 04-02-PLAN.md — Core 3-step booking flow, mock payment, event publisher, confirmation email, integration tests
- [ ] 04-03-PLAN.md — Booking management (list, cancel, modify), expiry background task, gateway BFF

### Phase 5: Guest Frontend
**Goal**: Guests have a polished, responsive React application for the complete booking journey -- from searching rooms to managing reservations
**Depends on**: Phase 4
**Requirements**: INFR-01
**Success Criteria** (what must be TRUE):
  1. Guest can use the search, booking, and account management flows through a cohesive React UI (not just raw API calls)
  2. The multi-step booking wizard maintains state across steps (room selection, guest details, payment, confirmation) without data loss
  3. Guest-facing site is fully responsive and usable on mobile devices (mobile-first design)
  4. Loading states, error messages, and empty states are handled gracefully throughout the application
**Plans**: 6 plans

Plans:
- [ ] 05-00-PLAN.md — Vitest test infrastructure setup, responsive and Navbar behavioral test stubs
- [ ] 05-01-PLAN.md — Vite + React + Tailwind v4 + shadcn/ui scaffolding, API client layer, stores, layout shell (Navbar/Footer), router
- [ ] 05-02-PLAN.md — Landing page with search form, search results with filter drawer, room detail with photo gallery, pricing calendar
- [ ] 05-03-PLAN.md — Login, Register, Password Reset pages with form validation and auth hooks
- [ ] 05-04-PLAN.md — 4-step booking wizard with sidebar navigation, summary panel, state persistence
- [ ] 05-05-PLAN.md — My Bookings list, Booking Detail with status timeline, cancel/modify dialogs

### Phase 6: Staff Dashboard
**Goal**: Hotel staff can manage daily operations -- viewing reservations, checking guests in and out, and reviewing guest history -- through a dedicated dashboard
**Depends on**: Phase 5
**Requirements**: STAF-01, STAF-02, STAF-03, STAF-04
**Success Criteria** (what must be TRUE):
  1. Staff can view all reservations with search and filter by guest name, date range, status, and confirmation number
  2. Staff can check in a guest (assigning a specific room) and check out a guest, with room status updating automatically
  3. Staff can view a guest profile showing their complete booking history
  4. Dashboard is paginated and performs well with realistic data volumes
**Plans**: 4 plans

Plans:
- [ ] 06-01-PLAN.md — Backend staff booking endpoints, gateway BFF orchestration, auth user search
- [ ] 06-02-PLAN.md — Frontend-staff scaffolding: Vite project, dark theme, API layer, sidebar layout, login
- [ ] 06-03-PLAN.md — Overview dashboard with metric cards, reservations list with search/filter/pagination
- [ ] 06-04-PLAN.md — Check-in/out dialogs with room assignment, room status board, guest profiles

### Phase 7: Reporting Dashboard
**Goal**: Staff can view actionable business analytics -- occupancy rates, revenue summaries, and booking trends -- through interactive charts
**Depends on**: Phase 6
**Requirements**: REPT-01, REPT-02, REPT-03
**Success Criteria** (what must be TRUE):
  1. Staff dashboard shows occupancy rate visualization filterable by date range
  2. Staff dashboard shows revenue summary for selected periods
  3. Staff dashboard shows interactive booking trend charts that respond to user interaction (hover, filter, zoom)
**Plans**: TBD

Plans:
- [ ] 07-01: TBD

### Phase 8: Testing & Deployment
**Goal**: The application is production-hardened with comprehensive tests, automated CI/CD, and a live demo URL that showcases the portfolio piece
**Depends on**: Phase 7
**Requirements**: INFR-02, INFR-03
**Success Criteria** (what must be TRUE):
  1. Unit and integration tests cover critical paths (auth, availability, booking, payment) and pass in CI
  2. GitHub Actions pipeline runs lint, test, and build on every push and pull request
  3. Application is deployed and accessible at a live URL with both guest and staff interfaces functional
  4. Project includes documentation sufficient for a reviewer to understand the architecture and run it locally
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Authentication | 0/3 | Planning complete | - |
| 2. Room & Rate Management | 3/3 | Complete   | 2026-03-21 |
| 3. Availability & Search | 3/3 | Complete   | 2026-03-21 |
| 4. Booking Engine | 2/3 | In Progress|  |
| 5. Guest Frontend | 5/6 | In Progress|  |
| 6. Staff Dashboard | 1/4 | In Progress|  |
| 7. Reporting Dashboard | 0/1 | Not started | - |
| 8. Testing & Deployment | 0/2 | Not started | - |
