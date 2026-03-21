---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: unknown
stopped_at: Phase 8 context gathered
last_updated: "2026-03-21T16:58:22.160Z"
progress:
  total_phases: 8
  completed_phases: 7
  total_plans: 26
  completed_plans: 26
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-20)

**Core value:** Guests can seamlessly search, book, and manage room reservations with a polished experience that demonstrates real-world full-stack competency.
**Current focus:** Phase 07 — reporting-dashboard

## Current Position

Phase: 07 (reporting-dashboard) — EXECUTING
Plan: 4 of 4

## Performance Metrics

**Velocity:**

- Total plans completed: 7
- Average duration: 4min
- Total execution time: 0.47 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 3 | 13min | 4min |
| 02 | 3 | 15min | 5min |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 02 P02 | 6min | 3 tasks | 12 files |
| Phase 02 P03 | 6min | 2 tasks | 7 files |
| Phase 03 P01 | 7min | 2 tasks | 9 files |
| Phase 03 P03 | 3min | 2 tasks | 6 files |
| Phase 03 P02 | 5min | 2 tasks | 7 files |
| Phase 04 P01 | 5min | 2 tasks | 21 files |
| Phase 04 P02 | 13min | 2 tasks | 13 files |
| Phase 04 P03 | 6min | 2 tasks | 10 files |
| Phase 05 P00 | 1min | 2 tasks | 5 files |
| Phase 05 P01 | 8min | 2 tasks | 48 files |
| Phase 05 P03 | 3min | 2 tasks | 5 files |
| Phase 05 P02 | 5min | 2 tasks | 12 files |
| Phase 05 P04 | 6min | 2 tasks | 8 files |
| Phase 05 P05 | 5min | 2 tasks | 6 files |
| Phase 06 P01 | 3min | 2 tasks | 7 files |
| Phase 06 P02 | 7min | 2 tasks | 46 files |
| Phase 06 P03 | 5min | 2 tasks | 8 files |
| Phase 06 P04 | 7min | 2 tasks | 14 files |
| Phase 07 P00 | 2min | 1 tasks | 5 files |
| Phase 07 P01 | 3min | 2 tasks | 8 files |
| Phase 07 P02 | 3min | 2 tasks | 14 files |
| Phase 07 P03 | 2min | 2 tasks | 7 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Backend-first build order (phases 1-4 API, then phases 5-6 frontend) per research recommendation
- [Roadmap]: Fine granularity (8 phases) to maintain natural delivery boundaries
- [01-01]: RS256 asymmetric JWT -- Auth signs with private key, services verify with public key only
- [01-01]: Database-per-service with 3 separate PostgreSQL containers
- [01-01]: RabbitMQ for inter-service messaging (guaranteed delivery over Redis Streams)
- [01-01]: BookingStatus enum defined in auth migration for cross-service availability
- [Phase 01]: Service layer pattern: business logic in services/, routes in api/v1/ for testability
- [Phase 01]: OAuth2PasswordRequestForm for login endpoint enables Swagger UI testing
- [01-03]: Lazy ConnectionConfig via model_construct to bypass pydantic .local domain validation
- [01-03]: Gateway SERVICE_MAP prefix routing for /api/v1/* to backend services
- [01-03]: Tests mock email sending to decouple from Mailpit availability
- [02-01]: Claims-based JWT auth: room service trusts JWT payload without DB user lookup
- [02-01]: JSONB columns for bed_config, amenities, photo_urls -- flexible schema within PostgreSQL
- [02-01]: Decimal type enforced in all monetary Pydantic schemas (never float)
- [02-02]: ROLE_TRANSITIONS dict pattern: None means all transitions allowed (manager/admin), set means restricted
- [02-02]: JSONB list mutation via new list creation to trigger SQLAlchemy change detection
- [02-02]: Route prefix /api/v1/rooms/types mounted before /api/v1/rooms for path precedence
- [02-02]: Added housekeeping role to require_staff dependency for status transition access
- [Phase 02-02]: ROLE_TRANSITIONS dict pattern: None means all transitions allowed (manager/admin), set means restricted
- [03-01]: Upsert by booking_id for idempotent event processing (query then insert/update)
- [03-01]: Half-open interval overlap detection for availability: check_in < check_out AND check_out > check_in
- [03-01]: Search result dicts use photo_url (singular) and amenity_highlights to match SearchResult schema
- [03-01]: Lazy imports in event consumer tests to handle multi-service app namespace collision
- [Phase 03]: sys.path manipulation in gateway conftest to isolate app module from room/auth services
- [Phase 03]: BFF endpoints return raw httpx Response (pass-through) rather than parsing/re-serializing
- [Phase 03]: Public endpoints use get_db only, no get_current_user dependency
- [Phase 03]: Calendar batch-loads rates (3 queries) then computes per-day in-memory
- [Phase 03]: Availability indicator thresholds: green >= 50%, yellow >= 20%, red < 20%
- [Phase 04-01]: BookingStatus enum with 6 states and VALID_TRANSITIONS dict for state machine enforcement
- [Phase 04-01]: Confirmation number format HB-XXXXXX using unambiguous characters (no 0/O/1/I)
- [Phase 04-01]: All monetary fields use Numeric(10,2) in models and Decimal in schemas (never float)
- [Phase 04]: patch.object on imported module reference to avoid multi-service app namespace collision in tests
- [Phase 04]: Email and event errors caught silently -- booking flow must never crash due to side-effect failures
- [Phase 04-03]: GET / list route placed before GET /{id} to avoid FastAPI UUID parsing conflict
- [Phase 04-03]: Modify availability re-check excludes current booking from blocking count (self-exclusion)
- [Phase 04-03]: BFF booking endpoints gracefully degrade if Room service is unavailable
- [Phase 04-03]: Late cancellation fee = price_per_night (first night charge)
- [Phase 05-00]: Vitest with jsdom for React component testing (consistent with Vite toolchain)
- [Phase 05-00]: Todo stubs (.todo) for tests before components exist -- Plans 01-05 convert to real tests
- [Phase 05-01]: Node 25 localStorage polyfill in test setup for Zustand store compatibility
- [Phase 05-01]: AppRoutes exported separately from App for test wrapping with MemoryRouter
- [Phase 05]: AxiosError instanceof check for 409/400 status differentiation in auth error handling
- [Phase 05-03]: Centered card auth layout pattern: max-w-400px, F8FAFC background, HotelBook logo, accent CTAs
- [Phase 05]: Filter state persisted in URL search params for shareable/bookmarkable search URLs
- [Phase 05]: PricingCalendar groups days by month with weekday alignment padding
- [Phase 05]: Responsive filter pattern: desktop sidebar (w-64) + mobile Sheet trigger
- [Phase 05]: Lazy-load wizard step components via React.lazy for code splitting
- [Phase 05]: String-based Zod schema for payment expiry fields to avoid z.coerce incompatibility with react-hook-form
- [Phase 05]: StatusBadge uses custom className overrides on shadcn Badge for precise color control per status
- [Phase 05]: StatusTimeline renders cancelled/no_show as all-muted dots with red label instead of partial progress
- [Phase 05]: ModifyDialog uses modifyBooking response shape (old_total, new_total, price_difference) for price diff toast
- [Phase 06]: Staff router registered before guest router in booking service for path precedence
- [Phase 06]: Gateway BFF check-in/out orchestrates booking + room services with graceful degradation
- [Phase 06]: Auth /search endpoint placed before /{user_id} for path precedence
- [Phase 06]: staff_access_token localStorage key separates staff auth from guest auth
- [Phase 06]: Always-dark theme via CSS variables in :root (no .dark class toggle needed)
- [Phase 06]: Staff frontend on port 5174 to avoid conflict with guest frontend on 5173
- [Phase 06-03]: Lazy-load OverviewPage and ReservationsPage for code splitting
- [Phase 06-03]: Debounce search 300ms, immediate emit for dropdown/date filter changes
- [Phase 06-03]: Windowed pagination showing max 5 page numbers centered on current page
- [Phase 06]: Auto-assign room: sort by floor ASC then room_number ASC, pick first
- [Phase 06]: Dialog reuse pattern: CheckInDialog/CheckOutDialog shared across 3 pages
- [Phase 06]: Room status transitions via popover with STATUS_ACTIONS map for valid transitions
- [Phase 07]: Nivo mock pattern: vi.mock returns vi.fn(() => null) for each chart component
- [Phase 07]: Auto-compute group_by from date range: day (<30d), week (30-90d), month (>90d)
- [Phase 07]: Occupancy uses reservation_projections table to avoid cross-service calls
- [Phase 07]: Gateway BFF reports uses 30s timeout for aggregation queries
- [Phase 07]: Seed script fetches room type UUIDs from room service API for referential integrity
- [Phase 07]: react-day-picker installed for shadcn Calendar range selection support
- [Phase 07]: Nivo chart components wrapped in role=img with aria-labels for accessibility
- [Phase 07]: DrillDownPanel uses shadcn Sheet with side=right for slide-out interaction
- [Phase 07]: getDrillDownBookings reuses existing staff bookings endpoint with date_from/date_to params
- [Phase 07]: PDF export captures dashboardRef div (KPIs + charts) excluding date picker header

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-03-21T16:58:22.156Z
Stopped at: Phase 8 context gathered
Resume file: .planning/phases/08-testing-deployment/08-CONTEXT.md
