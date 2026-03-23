---
phase: 12-migrate-from-pip-to-uv
plan: 02
subsystem: infra
tags: [uv, docker, ci-cd, makefile, dependency-management]

# Dependency graph
requires:
  - phase: 12-01
    provides: "Per-service pyproject.toml and uv.lock files"
provides:
  - "5 Dockerfiles using uv instead of pip with layer caching"
  - "CI pipeline using astral-sh/setup-uv@v7 with per-service test execution"
  - "Root Makefile with setup, sync-all, test, lint, lock-all, clean targets"
affects: [deploy, docker-compose, ci-cd]

# Tech tracking
tech-stack:
  added: [astral-sh/setup-uv, ghcr.io/astral-sh/uv]
  patterns: [uv-dockerfile-two-phase-sync, per-service-ci-test-loop, makefile-developer-workflow]

key-files:
  created:
    - Makefile
  modified:
    - services/auth/Dockerfile
    - services/room/Dockerfile
    - services/booking/Dockerfile
    - services/gateway/Dockerfile
    - services/chat/Dockerfile
    - .github/workflows/ci.yml

key-decisions:
  - "uv pinned to 0.10.9 in both Dockerfiles and CI for reproducibility"
  - "Two-phase uv sync in Dockerfiles: deps-only layer then project install for Docker cache optimization"
  - "WORKDIR /build/services/{svc} preserves ../../shared path resolution for uv path dependencies"

patterns-established:
  - "Dockerfile pattern: COPY --from=ghcr.io/astral-sh/uv:0.10.9 + two-phase uv sync --frozen"
  - "CI pattern: astral-sh/setup-uv@v7 with enable-cache for GitHub Actions"
  - "Makefile pattern: per-service targets (test-{svc}) and aggregate targets (sync-all, test)"

requirements-completed: [UV-05, UV-06, UV-07]

# Metrics
duration: 2min
completed: 2026-03-23
---

# Phase 12 Plan 02: Docker and CI Migration to uv Summary

**5 Dockerfiles migrated to uv with two-phase layer caching, CI pipeline using astral-sh/setup-uv@v7, and root Makefile for developer workflow**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-23T02:21:31Z
- **Completed:** 2026-03-23T02:23:30Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- All 5 service Dockerfiles use COPY --from=ghcr.io/astral-sh/uv:0.10.9 with two-phase uv sync for optimal layer caching
- CI pipeline fully migrated: astral-sh/setup-uv@v7 replaces actions/setup-python, uvx ruff replaces pip install ruff, per-service uv run pytest replaces monolithic pytest
- Makefile provides single-command developer setup (make setup) and testing (make test) with per-service granularity

## Task Commits

Each task was committed atomically:

1. **Task 1: Update all 5 Dockerfiles to use uv with layer caching** - `6213a12` (feat)
2. **Task 2: Update CI pipeline and create Makefile** - `bf99859` (feat)

## Files Created/Modified
- `services/auth/Dockerfile` - uv-based Docker build with two-phase sync and /build/services/auth WORKDIR
- `services/room/Dockerfile` - uv-based Docker build for room service
- `services/booking/Dockerfile` - uv-based Docker build for booking service
- `services/gateway/Dockerfile` - uv-based Docker build for gateway (no entrypoint.sh, direct uvicorn CMD)
- `services/chat/Dockerfile` - uv-based Docker build for chat service
- `.github/workflows/ci.yml` - CI pipeline using astral-sh/setup-uv@v7 with per-service test loop
- `Makefile` - Developer workflow targets: setup, sync-all, test, lint, lock-all, clean

## Decisions Made
- uv pinned to 0.10.9 consistently across all Dockerfiles and CI for reproducibility
- Two-phase uv sync in Dockerfiles: first --no-install-project (deps only, cached), then full sync (after source copy)
- WORKDIR set to /build/services/{svc} so ../../shared path dependency resolves correctly in Docker context
- CI uses uvx ruff check (no install step needed) for linting

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All infrastructure fully migrated to uv -- no pip commands remain in Dockerfiles or CI
- Docker builds will use uv sync --frozen with the lockfiles created in Plan 01
- Developer workflow simplified: `make setup` for initial setup, `make test` for all tests
- Phase 12 migration complete

## Self-Check: PASSED

All 7 modified/created files verified present. Both task commits (6213a12, bf99859) verified in git log.

---
*Phase: 12-migrate-from-pip-to-uv*
*Completed: 2026-03-23*
