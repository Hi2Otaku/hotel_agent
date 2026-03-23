---
phase: 12-migrate-from-pip-to-uv
plan: 01
subsystem: infra
tags: [uv, pyproject-toml, dependency-management, pytest, monorepo]

# Dependency graph
requires:
  - phase: 01-03
    provides: "Service directory structure with requirements.txt"
  - phase: 11
    provides: "Chat service with its own requirements.txt"
provides:
  - "5 per-service pyproject.toml files with uv.lock"
  - "Per-service test suites with merged conftest fixtures"
  - "Shared package importable via [tool.uv.sources] path dependency"
  - "Deprecated requirements.txt files with migration notice"
affects: [12-02, ci-cd, docker]

# Tech tracking
tech-stack:
  added: [uv]
  patterns: [per-service-pyproject, uv-lock, path-dependency-shared-package, per-service-pytest-config]

key-files:
  created:
    - services/auth/pyproject.toml
    - services/room/pyproject.toml
    - services/booking/pyproject.toml
    - services/gateway/pyproject.toml
    - services/chat/pyproject.toml
    - services/auth/uv.lock
    - services/room/uv.lock
    - services/booking/uv.lock
    - services/gateway/uv.lock
    - services/chat/uv.lock
    - services/auth/tests/conftest.py
    - services/room/tests/conftest.py
    - services/booking/tests/conftest.py
    - services/gateway/tests/conftest.py
    - tests/README.md
  modified:
    - services/auth/requirements.txt
    - services/room/requirements.txt
    - services/booking/requirements.txt
    - services/gateway/requirements.txt
    - services/chat/requirements.txt
    - requirements-dev.txt
    - pyproject.toml
    - .gitignore

key-decisions:
  - "Per-service pyproject.toml with [tool.uv.sources] path dependency on shared package"
  - "Booking conftest removes sys.path hack and shared Base.metadata.clear() -- clean imports via pythonpath=['.']"
  - "Gateway gets no aiosqlite dev dep (no DB); auth/room/booking get aiosqlite for SQLite test overrides"

patterns-established:
  - "Per-service test isolation: cd services/{svc} && uv run pytest tests/ -x"
  - "Shared package referenced as hotelbook-shared = { path = '../../shared' } in [tool.uv.sources]"
  - "Merged conftest pattern: root DB fixtures + service-specific fixtures in single conftest.py"

requirements-completed: [UV-01, UV-02, UV-03, UV-04]

# Metrics
duration: 8min
completed: 2026-03-23
---

# Phase 12 Plan 01: Per-Service uv Projects and Test Relocation Summary

**5 backend services converted to standalone uv projects with pyproject.toml, uv.lock, and per-service test suites replacing root-level tests**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-23T02:16:36Z
- **Completed:** 2026-03-23T02:24:00Z
- **Tasks:** 3
- **Files modified:** 56

## Accomplishments
- All 5 services (auth, room, booking, gateway, chat) have pyproject.toml with correct dependencies and uv.lock
- Shared package importable from all service venvs via [tool.uv.sources] path dependency
- Gateway tests pass via `cd services/gateway && uv run pytest tests/ -x` (8/8 passed)
- Tests relocated from root tests/ into per-service directories with merged conftest files
- All sys.path hacks removed from conftest files

## Task Commits

Each task was committed atomically:

1. **Task 1: Create per-service pyproject.toml files and generate uv.lock** - `051f809` (feat)
2. **Task 2: Relocate gateway tests into service directory** - `ff6918f` (feat)
3. **Task 3: Relocate auth, room, and booking tests into service directories** - `3b0ad2f` (feat)

## Files Created/Modified
- `services/auth/pyproject.toml` - Auth service uv project config with all deps + shared path dep
- `services/room/pyproject.toml` - Room service uv project config with minio, python-multipart
- `services/booking/pyproject.toml` - Booking service uv project config with aio-pika, fastapi-mail
- `services/gateway/pyproject.toml` - Gateway service lightweight config (no DB deps)
- `services/chat/pyproject.toml` - Chat service config with anthropic, openai, sse-starlette
- `services/*/uv.lock` - Lockfiles for reproducible installs
- `services/gateway/tests/conftest.py` - Gateway test fixtures without sys.path hack
- `services/auth/tests/conftest.py` - Auth test fixtures merged from root + auth-specific
- `services/room/tests/conftest.py` - Room test fixtures with seed_room_data and insert_reservation helpers
- `services/booking/tests/conftest.py` - Booking test fixtures with mock dependencies (no sys.path hack)
- `services/booking/tests/test_*.py` - 6 booking test files relocated
- `tests/README.md` - Note that old tests/ is superseded
- `pyproject.toml` - Stripped of pytest config (moved per-service)
- `.gitignore` - Added services/*/.venv/ pattern
- `requirements-dev.txt` - Deprecation header added

## Decisions Made
- Per-service pyproject.toml with [tool.uv.sources] path dependency on shared package for clean resolution
- Booking conftest rewritten to remove sys.path manipulation and shared Base.metadata.clear() hack -- clean imports via pythonpath=["."] in pyproject.toml
- Gateway dev dependencies exclude aiosqlite (no database) while auth/room/booking include it for SQLite test overrides
- Old tests/ directory retained with README noting supersession (cleanup deferred)

## Deviations from Plan

None - plan executed exactly as written. Tasks 1 and 2 were completed in a prior session and found already committed.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All services ready for Docker/CI migration (Plan 12-02)
- Dockerfiles can switch from `pip install -r requirements.txt` to `uv sync --frozen`
- CI pipeline can switch to `uv sync --frozen` per service
- Per-service test isolation verified for gateway; auth/room/booking require DB containers for full test runs

---
*Phase: 12-migrate-from-pip-to-uv*
*Completed: 2026-03-23*
