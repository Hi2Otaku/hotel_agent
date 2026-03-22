# Phase 12: Migrate from pip to uv — Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace pip with uv as the Python package manager across all 4 backend services (auth, room, booking, gateway). Migrate from requirements.txt to pyproject.toml per service with uv.lock for reproducible installs. Update Dockerfiles, CI/CD pipeline, and local dev workflow. Does NOT change any application code — only dependency management and build tooling.

</domain>

<decisions>
## Implementation Decisions

### Dependency format
- Each service gets its own `pyproject.toml` with `[project.dependencies]`
- Each service gets its own `uv.lock` for reproducible installs
- The `shared/` package is referenced as a path dependency: `hotelbook-shared = {path = "../../shared"}`
- Old `requirements.txt` files kept temporarily with a deprecation comment (deleted in a future cleanup)
- Root `requirements-dev.txt` migrated to dev dependencies in root or per-service pyproject.toml

### Docker build strategy
- Install uv via `COPY --from=ghcr.io/astral-sh/uv` (multi-stage copy from official image)
- No pip needed in final images
- Use `uv sync --frozen` from lockfile for exact reproducible installs
- Dockerfiles updated to copy pyproject.toml + uv.lock before source code (layer caching)

### Local dev workflow
- Local venvs + Docker: developers can run services directly from per-service `.venv` OR via Docker
- Each service gets a `.venv` created by `uv sync` in its directory
- Root `pyproject.toml` pytest config moves to per-service pyproject.toml — tests run from within each service directory
- Add a `Makefile` with common targets: `sync-all`, `test-auth`, `test-booking`, `test-room`, `test-gateway`, `lint`, etc.
- `.gitignore` updated to ignore `.venv/` in service directories

### CI/CD impact
- CI installs uv, then runs `uv sync --frozen` in each service directory
- Cache uv store (`~/.cache/uv`) between CI runs for speed
- Linting and testing jobs updated to use uv-based dependency installation
- Old requirements.txt files kept with deprecation comment during transition

### Claude's Discretion
- Exact uv version to pin in CI and Dockerfiles
- Makefile target naming conventions
- Whether to use `uv run` for commands or activate venvs explicitly
- Layer caching optimization details in Dockerfiles
- How to structure the per-service pytest configuration

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current dependency files
- `services/auth/requirements.txt` — Current auth service dependencies
- `services/room/requirements.txt` — Current room service dependencies
- `services/booking/requirements.txt` — Current booking service dependencies
- `services/gateway/requirements.txt` — Current gateway service dependencies
- `requirements-dev.txt` — Current dev dependencies (linting, testing)
- `shared/pyproject.toml` — Shared package definition (keep as-is, it's already pyproject.toml)
- `pyproject.toml` — Root project config with pytest settings (to be split per-service)

### Dockerfiles
- `services/auth/Dockerfile` — Current pip-based Docker build
- `services/room/Dockerfile` — Current pip-based Docker build
- `services/booking/Dockerfile` — Current pip-based Docker build
- `services/gateway/Dockerfile` — Current pip-based Docker build

### CI/CD
- `.github/workflows/ci.yml` — Current pipeline using pip install

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/pyproject.toml`: Already in pyproject.toml format — no migration needed for shared package
- `scripts/generate_keys.sh`: Not affected by this migration

### Established Patterns
- All 4 Dockerfiles follow identical pattern: `FROM python:3.12-slim`, `pip install /app/shared`, `pip install -r requirements.txt`
- CI pipeline installs deps with `pip install -r requirements.txt` then runs pytest
- Root `pyproject.toml` has `pythonpath = ["services/auth", "services/room", "services/booking", "shared"]` for test discovery

### Integration Points
- Dockerfiles: pip install → uv sync --frozen
- CI pipeline: pip install → uv sync --frozen
- docker-compose.yml: no changes needed (volumes and env vars stay the same)
- shared package: referenced as path dep instead of `pip install /app/shared`

</code_context>

<specifics>
## Specific Ideas

- The Makefile should make it trivial for a new developer to get set up: `make setup` installs uv + syncs all services
- Per-service test isolation means `cd services/auth && uv run pytest` should work standalone

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 12-migrate-from-pip-to-uv-and-set-up-per-service-virtual-environments*
*Context gathered: 2026-03-23*
