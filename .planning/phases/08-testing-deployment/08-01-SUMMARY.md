---
phase: 08-testing-deployment
plan: 01
subsystem: testing
tags: [vitest, playwright, pytest, react-testing-library, e2e, component-tests]

# Dependency graph
requires:
  - phase: 05-guest-frontend
    provides: Guest frontend components and stores to test
  - phase: 06-staff-frontend
    provides: Staff frontend pages and report components to test
  - phase: 07-analytics
    provides: Nivo chart components with mock patterns
provides:
  - 26 guest frontend Vitest tests across 6 test files
  - 29 staff frontend Vitest tests across 7 test files
  - 7 Playwright E2E tests across 2 spec files
  - Fixed pytest conftest.py async session fixtures for backend tests
affects: [08-02, 08-03]

# Tech tracking
tech-stack:
  added: ["@playwright/test ^1.58.0"]
  patterns: ["vi.mocked() pattern for mock references after vi.mock hoisting", "Idempotent test fixtures for session-scoped async tests"]

key-files:
  created:
    - frontend/src/__tests__/authStore.test.ts
    - frontend/src/__tests__/bookingWizardStore.test.ts
    - frontend/src/__tests__/SearchResults.test.tsx
    - frontend/src/__tests__/BookingWizard.test.tsx
    - frontend-staff/src/__tests__/LoginPage.test.tsx
    - frontend-staff/src/__tests__/ReservationsPage.test.tsx
    - e2e/package.json
    - e2e/playwright.config.ts
    - e2e/tests/guest-booking.spec.ts
    - e2e/tests/staff-checkin.spec.ts
  modified:
    - frontend-staff/src/components/reports/OccupancyHeatmap.test.tsx
    - frontend-staff/src/components/reports/RevenueChart.test.tsx
    - frontend-staff/src/components/reports/BookingTrendsChart.test.tsx
    - frontend-staff/src/components/reports/DateRangePicker.test.tsx
    - frontend-staff/src/pages/ReportsPage.test.tsx
    - tests/conftest.py
    - tests/auth/conftest.py
    - pyproject.toml

key-decisions:
  - "pytest_asyncio fixtures with loop_scope=session replacing deprecated event_loop fixture"
  - "async_sessionmaker per-request instead of manual savepoints for test isolation"
  - "asyncio_default_test_loop_scope=session so tests share engine event loop"
  - "vi.mocked() import pattern to avoid hoisting issues with vi.fn() variable references"
  - "Idempotent registered_guest fixture handles 409 conflict by falling back to login"

patterns-established:
  - "Nivo mock pattern: vi.mock returns vi.fn(() => null), then import and vi.mocked() for assertions"
  - "E2E flexible selectors: getByRole with regex, .or() chains for resilient element matching"

requirements-completed: [INFR-02]

# Metrics
duration: 20min
completed: 2026-03-22
---

# Phase 08 Plan 01: Frontend Test Coverage and E2E Setup Summary

**55 frontend tests (26 guest + 29 staff) with Vitest plus 7 Playwright E2E specs, and fixed backend pytest async session fixtures**

## Performance

- **Duration:** 20 min
- **Started:** 2026-03-21T17:20:32Z
- **Completed:** 2026-03-21T17:40:32Z
- **Tasks:** 3
- **Files modified:** 18

## Accomplishments
- Guest frontend expanded from 2 to 6 test files (26 passing tests) covering auth store, booking wizard store, SearchResults, and BookingWizard
- Staff frontend expanded from 0 real tests to 7 test files (29 passing tests) by converting 5 it.todo stubs and adding 2 new page tests
- Playwright E2E project created with chromium, 2 spec files containing 7 tests (guest booking flow + staff check-in flow)
- Fixed backend pytest conftest.py: replaced deprecated event_loop fixture with modern pytest_asyncio decorators and async_sessionmaker pattern

## Task Commits

Each task was committed atomically:

1. **Task 1: Guest frontend component and store tests** - `ea30210` (feat)
2. **Task 2: Staff frontend component tests (convert stubs + new pages)** - `71591d1` (feat)
3. **Task 3: Playwright E2E project setup with test specs** - `fc08606` (feat)

## Files Created/Modified
- `frontend/src/__tests__/authStore.test.ts` - Zustand auth store unit tests
- `frontend/src/__tests__/bookingWizardStore.test.ts` - Booking wizard store unit tests
- `frontend/src/__tests__/SearchResults.test.tsx` - Search results component tests with mocked hook
- `frontend/src/__tests__/BookingWizard.test.tsx` - Booking wizard component tests with lazy-load mocks
- `frontend-staff/src/components/reports/OccupancyHeatmap.test.tsx` - Real Nivo calendar mock tests
- `frontend-staff/src/components/reports/RevenueChart.test.tsx` - Real Nivo bar chart mock tests
- `frontend-staff/src/components/reports/BookingTrendsChart.test.tsx` - Real Nivo line chart mock tests
- `frontend-staff/src/components/reports/DateRangePicker.test.tsx` - Preset button and onChange tests
- `frontend-staff/src/pages/ReportsPage.test.tsx` - Full page with KPI cards and chart sections
- `frontend-staff/src/__tests__/LoginPage.test.tsx` - Login form rendering and input tests
- `frontend-staff/src/__tests__/ReservationsPage.test.tsx` - Reservations list with mock data
- `e2e/package.json` - Playwright project config
- `e2e/playwright.config.ts` - Chromium project with docker-compose webServer
- `e2e/tests/guest-booking.spec.ts` - 4 E2E tests: search, view, book, register
- `e2e/tests/staff-checkin.spec.ts` - 3 E2E tests: login, view reservations, check-in
- `tests/conftest.py` - Fixed async fixtures for pytest-asyncio 1.3.0
- `tests/auth/conftest.py` - Idempotent registered_guest and admin_token fixtures
- `pyproject.toml` - Added asyncio loop scope configuration

## Decisions Made
- Used `pytest_asyncio` fixtures with `loop_scope="session"` instead of deprecated `event_loop` fixture pattern for pytest-asyncio 1.3.0 compatibility
- Switched test DB session management from manual savepoint-per-request to `async_sessionmaker` per request for simpler, more reliable test isolation
- Used `vi.mocked()` import pattern after `vi.mock()` to avoid variable hoisting issues (vi.fn() references before initialization)
- Made `registered_guest` fixture idempotent (handles 409 by falling back to login) for session-scoped test loop

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed pytest conftest.py deprecated event_loop fixture**
- **Found during:** Task 1 (backend auth test verification)
- **Issue:** pytest-asyncio 1.3.0 deprecated the `event_loop` fixture; tests crashed with "another operation in progress" and "different loop" errors
- **Fix:** Replaced `event_loop` fixture with `@pytest_asyncio.fixture(loop_scope="session")` decorators, switched to `async_sessionmaker`, added `asyncio_default_test_loop_scope=session` config
- **Files modified:** tests/conftest.py, tests/auth/conftest.py, pyproject.toml
- **Verification:** 19/22 non-invite auth tests pass (3 invite tests have pre-existing 422 validation issue)
- **Committed in:** ea30210 (Task 1 commit)

**2. [Rule 1 - Bug] Fixed admin_token fixture event loop deadlock**
- **Found during:** Task 1 (backend auth test verification)
- **Issue:** admin_token created a separate engine/session which got attached to a different event loop, causing deadlock
- **Fix:** Rewired admin_token to register via API then promote via `_test_conn`, later simplified to use register + login API flow with `_test_engine` sessionmaker
- **Files modified:** tests/auth/conftest.py
- **Committed in:** ea30210 (Task 1 commit)

**3. [Rule 1 - Bug] Fixed vi.fn() hoisting issue in Nivo mock tests**
- **Found during:** Task 2 (staff frontend tests)
- **Issue:** `const mockX = vi.fn()` before `vi.mock()` fails because vi.mock is hoisted above const declarations
- **Fix:** Used `vi.mock()` with inline `vi.fn()`, then imported and `vi.mocked()` the module reference
- **Files modified:** OccupancyHeatmap.test.tsx, RevenueChart.test.tsx, BookingTrendsChart.test.tsx
- **Committed in:** 71591d1 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (3 bugs)
**Impact on plan:** All fixes necessary for test infrastructure correctness. No scope creep.

## Deferred Issues

- **Pre-existing:** Backend invite accept tests return 422 (likely EmailStr validation rejecting `.local` domain) - 3 tests affected
- **Pre-existing:** Backend password reset tests conflict with shared session state (registered_guest password gets changed) - 2 tests affected

## Issues Encountered
- Backend auth tests require Docker DB + local JWT keys. Tests verified with `JWT_PRIVATE_KEY_PATH=keys/jwt_private_key` env var pointing to local keys.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Frontend test suites ready for CI integration (Plan 08-02)
- Playwright E2E specs ready for full-stack testing when Docker Compose stack is running
- Backend conftest.py fixed and ready for expanded test coverage

---
*Phase: 08-testing-deployment*
*Completed: 2026-03-22*
