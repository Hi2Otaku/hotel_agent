# Phase 12: Migrate from pip to uv - Research

**Researched:** 2026-03-23
**Domain:** Python dependency management, Docker builds, CI/CD
**Confidence:** HIGH

## Summary

This phase replaces pip with uv across 4 Python microservices (auth, room, booking, gateway). uv is an extremely fast Python package manager by Astral (written in Rust) that supports pyproject.toml, lockfiles, and virtual environments natively. The migration involves: (1) creating per-service pyproject.toml files with uv.lock, (2) updating Dockerfiles to use `COPY --from=ghcr.io/astral-sh/uv`, (3) updating CI to use `astral-sh/setup-uv`, and (4) adding a Makefile for developer experience.

The user chose independent projects with path dependencies (NOT uv workspaces). This means each service has its own pyproject.toml, uv.lock, and .venv -- they are NOT workspace members sharing a single lockfile. The shared/ package is referenced as a path dependency via `[tool.uv.sources]`.

**Primary recommendation:** Use uv 0.10.x with independent per-service projects, `--frozen` for Docker/CI installs, and `astral-sh/setup-uv@v7` with built-in caching in GitHub Actions.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Each service gets its own `pyproject.toml` with `[project.dependencies]`
- Each service gets its own `uv.lock` for reproducible installs
- The `shared/` package is referenced as a path dependency: `hotelbook-shared = {path = "../../shared"}`
- Old `requirements.txt` files kept temporarily with a deprecation comment (deleted in a future cleanup)
- Root `requirements-dev.txt` migrated to dev dependencies in root or per-service pyproject.toml
- Install uv via `COPY --from=ghcr.io/astral-sh/uv` (multi-stage copy from official image)
- No pip needed in final images
- Use `uv sync --frozen` from lockfile for exact reproducible installs
- Dockerfiles updated to copy pyproject.toml + uv.lock before source code (layer caching)
- Local venvs + Docker: developers can run services directly from per-service `.venv` OR via Docker
- Each service gets a `.venv` created by `uv sync` in its directory
- Root `pyproject.toml` pytest config moves to per-service pyproject.toml -- tests run from within each service directory
- Add a `Makefile` with common targets: `sync-all`, `test-auth`, `test-booking`, `test-room`, `test-gateway`, `lint`, etc.
- `.gitignore` updated to ignore `.venv/` in service directories
- CI installs uv, then runs `uv sync --frozen` in each service directory
- Cache uv store (`~/.cache/uv`) between CI runs for speed

### Claude's Discretion
- Exact uv version to pin in CI and Dockerfiles
- Makefile target naming conventions
- Whether to use `uv run` for commands or activate venvs explicitly
- Layer caching optimization details in Dockerfiles
- How to structure the per-service pytest configuration

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| uv | 0.10.x (pin to 0.10.9+) | Python package/project manager | 10-100x faster than pip, lockfile support, official Astral tool |
| astral-sh/setup-uv | v7 | GitHub Actions uv installer | Official action with built-in caching |

### Supporting
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| ghcr.io/astral-sh/uv | 0.10.x | Docker uv binary source | COPY --from in Dockerfiles |
| make | system | Developer workflow automation | Makefile for common commands |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Independent projects | uv workspaces | Workspaces share one lockfile + venv -- bad for isolated microservices with different deps |
| `--frozen` | `--locked` | `--locked` validates lockfile freshness but FAILS if path deps aren't present in Docker layer -- `--frozen` is correct for Docker |
| `uv run pytest` | activating venv then running pytest | `uv run` is simpler and auto-discovers the project venv |

**Version pinning:** Pin uv to a specific version (e.g., `0.10.9`) in both Dockerfiles and CI for reproducible builds. Use the same version everywhere.

## Architecture Patterns

### Recommended Project Structure
```
services/
  auth/
    pyproject.toml        # service deps + pytest config
    uv.lock               # reproducible lockfile
    .venv/                # local dev venv (gitignored)
    .python-version       # optional: pin Python version
    Dockerfile
    app/
    ...
  room/
    pyproject.toml
    uv.lock
    .venv/
    Dockerfile
    app/
    ...
  booking/
    pyproject.toml
    uv.lock
    .venv/
    Dockerfile
    app/
    ...
  gateway/
    pyproject.toml
    uv.lock
    .venv/
    Dockerfile
    app/
    ...
shared/
  pyproject.toml          # already exists, keep as-is
  ...
Makefile                  # root-level for DX
pyproject.toml            # root (stripped to minimal or removed)
```

### Pattern 1: Per-Service pyproject.toml with Path Dependency

**What:** Each service declares its own dependencies and references shared/ as a path dependency.
**When to use:** Always -- this is the decided approach.

```toml
# services/auth/pyproject.toml
[project]
name = "hotelbook-auth"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.135.0",
    "uvicorn[standard]",
    "sqlalchemy[asyncio]>=2.0.48",
    "asyncpg",
    "alembic>=1.18.0",
    "pydantic-settings>=2.0",
    "httpx",
    "pwdlib[argon2]>=0.3.0",
    "PyJWT[crypto]>=2.12.0",
    "fastapi-mail>=1.6.0",
    "aio-pika>=9.6.0",
    "hotelbook-shared",
]

[tool.uv.sources]
hotelbook-shared = { path = "../../shared" }

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.23.0",
    "httpx",
    "aiosqlite",
    "ruff",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
testpaths = ["tests"]
pythonpath = ["."]
filterwarnings = ["ignore::DeprecationWarning"]
```

**Important:** The path `"../../shared"` is relative to the service directory. In Docker, the shared/ package gets copied into the build context at a different path, so the Dockerfile must handle this.

### Pattern 2: Dockerfile with uv and Layer Caching

**What:** Multi-layer Docker build using uv for dependency installation.
**When to use:** All 4 service Dockerfiles.

```dockerfile
FROM python:3.12-slim

# Install uv (pinned version)
COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

# Configure uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Layer 1: Install shared package first (changes rarely)
COPY shared/ /app/shared/

# Layer 2: Copy dependency manifests (changes rarely)
COPY services/auth/pyproject.toml services/auth/uv.lock ./

# Layer 3: Install dependencies only (cached when deps unchanged)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Layer 4: Copy service code (changes frequently)
COPY services/auth/ .

# Layer 5: Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Make entrypoint executable
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
```

**Critical Docker path dependency issue:** The pyproject.toml references `../../shared` but in Docker the shared/ is at `/app/shared/`. Two approaches:

1. **Override via environment variable at build time** -- not directly supported by uv sources
2. **Adjust Docker WORKDIR** -- set WORKDIR so that relative path resolves correctly
3. **Copy shared/ to the right relative location** -- ensure the directory structure matches

**Recommended approach:** Since Docker builds from repository root context, copy shared/ to a location that matches the relative path. Structure the Dockerfile WORKDIR and COPY commands so that `../../shared` resolves from the service's working directory:

```dockerfile
WORKDIR /build/services/auth
COPY shared/ /build/shared/
COPY services/auth/pyproject.toml services/auth/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project
COPY services/auth/ .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
ENV PATH="/build/services/auth/.venv/bin:$PATH"
```

This way `../../shared` from `/build/services/auth/` resolves to `/build/shared/` which is correct.

### Pattern 3: GitHub Actions with setup-uv

**What:** CI pipeline using astral-sh/setup-uv with caching.
**When to use:** All CI jobs that need Python dependencies.

```yaml
- uses: astral-sh/setup-uv@v7
  with:
    version: "0.10.9"
    enable-cache: true

- name: Install auth dependencies
  run: cd services/auth && uv sync --frozen

- name: Run auth tests
  run: cd services/auth && uv run pytest tests/ -x --tb=short
```

### Pattern 4: Makefile for Developer Experience

**What:** Root Makefile with common targets.
**When to use:** Developer workflow.

```makefile
.PHONY: setup sync-all test lint test-auth test-room test-booking test-gateway

SERVICES := auth room booking gateway

setup:
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	@$(MAKE) sync-all

sync-all:
	@for svc in $(SERVICES); do \
		echo "Syncing $$svc..."; \
		cd services/$$svc && uv sync && cd ../..; \
	done

test-auth:
	cd services/auth && uv run pytest tests/ -x --tb=short

test-room:
	cd services/room && uv run pytest tests/ -x --tb=short

test-booking:
	cd services/booking && uv run pytest tests/ -x --tb=short

test-gateway:
	cd services/gateway && uv run pytest tests/ -x --tb=short

test: test-auth test-room test-booking test-gateway

lint:
	uv run ruff check services/ shared/
```

### Anti-Patterns to Avoid
- **Using uv workspaces when services need isolation:** Workspaces share a single lockfile and venv. Microservices with different deps should be independent projects.
- **Using `--locked` in Docker without all source files present:** `--locked` validates the lockfile by re-resolving, which fails if path dependencies aren't accessible. Use `--frozen` in Docker.
- **Installing uv via pip or apt in Docker:** Use `COPY --from=ghcr.io/astral-sh/uv:version` for speed and simplicity.
- **Forgetting UV_COMPILE_BYTECODE in production:** Without bytecode compilation, first import is slower.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Lockfile generation | Custom lock scripts | `uv lock` | Handles dependency resolution, platform markers, hashes |
| CI uv installation | curl scripts | `astral-sh/setup-uv@v7` | Handles caching, version resolution, PATH setup |
| Virtual env management | Manual venv creation | `uv sync` (auto-creates .venv) | uv creates and populates .venv automatically |
| Docker uv install | apt/pip install | `COPY --from=ghcr.io/astral-sh/uv` | Single layer, no package manager overhead |

**Key insight:** uv handles venv creation, dependency resolution, locking, and installation in a single tool. Don't mix pip and uv in the same project.

## Common Pitfalls

### Pitfall 1: Path Dependency Resolution in Docker
**What goes wrong:** `uv sync --frozen` fails because path dependency (`../../shared`) doesn't exist at the expected relative path in Docker.
**Why it happens:** Docker WORKDIR changes relative path resolution.
**How to avoid:** Structure Docker COPY and WORKDIR so that the relative path in pyproject.toml resolves correctly. Use `/build/services/auth/` as WORKDIR with shared/ at `/build/shared/`.
**Warning signs:** "No such file or directory" errors during `uv sync` in Docker build.

### Pitfall 2: --locked vs --frozen in Docker
**What goes wrong:** `uv sync --locked` fails in Docker layer caching setup because it needs all source files to verify the lockfile.
**Why it happens:** `--locked` re-resolves dependencies to verify freshness. With path deps, it needs the path dep's pyproject.toml accessible.
**How to avoid:** Use `--frozen` in Docker (already decided). Use `--locked` in local dev if you want freshness checks.
**Warning signs:** "workspace member not found" or resolution errors during Docker build.

### Pitfall 3: Forgetting to Generate uv.lock Before First Docker Build
**What goes wrong:** Docker build fails because uv.lock doesn't exist.
**Why it happens:** uv.lock is generated by `uv lock` or `uv sync` locally, not automatically.
**How to avoid:** Run `uv lock` in each service directory and commit the uv.lock files. Makefile `sync-all` target handles this.
**Warning signs:** "No lockfile found" errors.

### Pitfall 4: Shared Package Not Importable After uv sync
**What goes wrong:** `from shared.xxx import yyy` fails at runtime.
**Why it happens:** The shared package needs to be properly installed (not just on PYTHONPATH). With uv, it's installed as a path dependency.
**How to avoid:** Ensure `hotelbook-shared` is in `[project.dependencies]` and `[tool.uv.sources]` points to the correct path. uv installs it into the venv.
**Warning signs:** `ModuleNotFoundError: No module named 'shared'`.

### Pitfall 5: Test pythonpath Mismatch After Migration
**What goes wrong:** Tests that relied on root pyproject.toml pythonpath setting fail.
**Why it happens:** Root pyproject.toml had `pythonpath = ["services/auth", "services/room", ...]`. Per-service pyproject.toml only needs `pythonpath = ["."]` since tests run from within the service directory.
**How to avoid:** Each service's pytest config uses `pythonpath = ["."]`. Tests import from `app.*` which resolves to the service's own `app/` directory.
**Warning signs:** Import errors in tests after migration.

### Pitfall 6: CI Cache Key Must Include All Service Lockfiles
**What goes wrong:** CI cache doesn't invalidate when one service's deps change.
**Why it happens:** Cache key only hashes one lockfile.
**How to avoid:** Use `hashFiles('services/*/uv.lock')` in cache key or rely on setup-uv's built-in caching which handles this.
**Warning signs:** CI uses stale dependencies after a lockfile update.

## Code Examples

### Per-Service pyproject.toml (Auth - Complete)
```toml
# Source: Derived from services/auth/requirements.txt
[project]
name = "hotelbook-auth"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.135.0",
    "uvicorn[standard]",
    "sqlalchemy[asyncio]>=2.0.48",
    "asyncpg",
    "alembic>=1.18.0",
    "pydantic-settings>=2.0",
    "httpx",
    "pwdlib[argon2]>=0.3.0",
    "PyJWT[crypto]>=2.12.0",
    "fastapi-mail>=1.6.0",
    "aio-pika>=9.6.0",
    "hotelbook-shared",
]

[tool.uv.sources]
hotelbook-shared = { path = "../../shared" }

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.23.0",
    "httpx",
    "aiosqlite",
    "ruff",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
testpaths = ["tests"]
pythonpath = ["."]
filterwarnings = ["ignore::DeprecationWarning"]
```

### Per-Service pyproject.toml (Gateway - Lighter)
```toml
# Source: Derived from services/gateway/requirements.txt
[project]
name = "hotelbook-gateway"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.135.0",
    "uvicorn[standard]",
    "pydantic-settings>=2.0",
    "httpx",
    "hotelbook-shared",
]

[tool.uv.sources]
hotelbook-shared = { path = "../../shared" }

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.23.0",
    "httpx",
    "ruff",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
testpaths = ["tests"]
pythonpath = ["."]
filterwarnings = ["ignore::DeprecationWarning"]
```

### Deprecation Comment for Old requirements.txt
```
# DEPRECATED: This file is kept for reference during the uv migration.
# Dependencies are now managed via pyproject.toml + uv.lock.
# This file will be removed in a future cleanup.
#
# To install dependencies, use: uv sync
# See pyproject.toml for the current dependency list.
```

### Updated CI Pipeline (Backend Tests Job)
```yaml
backend-tests:
  runs-on: ubuntu-latest
  needs: lint
  steps:
    - uses: actions/checkout@v4

    - name: Start infrastructure containers
      run: docker compose up -d auth_db room_db booking_db rabbitmq mailpit minio

    - name: Wait for databases
      run: |
        for i in $(seq 1 30); do
          ALL_READY=true
          for svc in auth_db room_db booking_db; do
            if ! docker compose exec $svc pg_isready -q 2>/dev/null; then
              ALL_READY=false
            fi
          done
          if [ "$ALL_READY" = true ]; then break; fi
          sleep 5
        done
        sleep 5

    - uses: astral-sh/setup-uv@v7
      with:
        version: "0.10.9"
        enable-cache: true

    - name: Install service dependencies
      run: |
        for svc in auth room booking gateway; do
          cd services/$svc && uv sync --frozen && cd ../..
        done

    - name: Generate RSA keys for JWT
      run: |
        mkdir -p keys
        openssl genrsa -out keys/jwt-private.pem 2048
        openssl rsa -in keys/jwt-private.pem -pubout -out keys/jwt-public.pem

    - name: Run backend tests
      env:
        AUTH_DATABASE_URL: postgresql+asyncpg://auth_user:auth_pass@localhost:5433/auth
        ROOM_DATABASE_URL: postgresql+asyncpg://room_user:room_pass@localhost:5434/rooms
        BOOKING_DATABASE_URL: postgresql+asyncpg://booking_user:booking_pass@localhost:5435/bookings
        JWT_PRIVATE_KEY_PATH: keys/jwt-private.pem
        JWT_PUBLIC_KEY_PATH: keys/jwt-public.pem
        RABBITMQ_URL: amqp://hotel:hotel_pass@localhost:5672/
        MAIL_SERVER: localhost
        MAIL_PORT: "1025"
        MINIO_ENDPOINT: localhost:9000
        MINIO_ACCESS_KEY: minioadmin
        MINIO_SECRET_KEY: minioadmin
        MINIO_BUCKET: hotelbook
        MINIO_SECURE: "false"
        ROOM_SERVICE_URL: http://localhost:8002
      run: |
        for svc in auth room booking gateway; do
          echo "Testing $svc..."
          cd services/$svc && uv run pytest tests/ -x --tb=short && cd ../..
        done

    - name: Teardown
      if: always()
      run: docker compose down -v
```

### Lint Job Update
```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - uses: astral-sh/setup-uv@v7
      with:
        version: "0.10.9"
        enable-cache: true

    - name: Lint backend
      run: uv run ruff check services/ tests/

    - uses: actions/setup-node@v4
      with:
        node-version: "20"

    - name: Lint guest frontend
      run: cd frontend && npm ci && npm run lint

    - name: Lint staff frontend
      run: cd frontend-staff && npm ci && npm run lint
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| pip + requirements.txt | uv + pyproject.toml + uv.lock | 2024 (uv 0.1) | 10-100x faster installs, lockfiles, reproducibility |
| pip freeze for lockfiles | uv lock (cross-platform resolver) | 2024 | Platform-aware resolution, hash verification |
| venv + pip install | uv sync (creates venv automatically) | 2024 | Single command for venv creation + install |
| setup.py / setup.cfg | pyproject.toml (PEP 621) | 2022-2024 | Standardized metadata, tool config in one file |
| pip install in Docker | COPY --from=ghcr.io/astral-sh/uv | 2024 | No pip needed, faster builds |

**Deprecated/outdated:**
- `pip-tools` / `pip-compile`: Superseded by uv's built-in lockfile support
- `poetry`: uv is faster, PEP-compliant, simpler for non-library projects
- `setup.py` / `setup.cfg`: pyproject.toml is the standard

## Open Questions

1. **Test directory location after migration**
   - What we know: Currently tests are in `tests/` at repo root with subdirectories per service. Per-service pytest config means tests run from within each service.
   - What's unclear: Do the test files need to move into `services/auth/tests/`, `services/room/tests/`, etc., or can they stay at root?
   - Recommendation: The existing `tests/auth/`, `tests/room/` etc. directories should be referenced by each service's pytest config. Alternatively, if the conftest.py imports `from app.xxx`, they need to run from within the service directory where `app/` is the service's app. Moving tests into service directories is cleaner. **This is a planner decision** -- but the conftest.py currently imports `from app.api.deps import get_db` which only works if pythonpath includes the service directory.

2. **Root pyproject.toml fate**
   - What we know: Root pyproject.toml currently has pytest config with cross-service pythonpath.
   - What's unclear: Should it be removed entirely or kept as a minimal shell?
   - Recommendation: Strip it to minimal (project name/version only) or keep it for root-level tooling (ruff config). Remove the pytest section since tests move per-service.

3. **Ruff installation in CI**
   - What we know: Currently `pip install ruff` in lint job. With uv, ruff could be a dev dependency or installed via `uv tool install ruff`.
   - Recommendation: Use `uvx ruff check` (runs ruff without installing to any venv) or include ruff as a dev dependency in each service.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.x + pytest-asyncio 0.23.x |
| Config file | Per-service `pyproject.toml` (to be created) |
| Quick run command | `cd services/auth && uv run pytest tests/ -x --tb=short` |
| Full suite command | `make test` (runs all 4 services) |

### Phase Requirements -> Test Map

This phase has no formal requirement IDs in REQUIREMENTS.md (it's a tooling migration). Validation is behavioral:

| Behavior | Test Type | Automated Command | Exists? |
|----------|-----------|-------------------|---------|
| uv sync creates .venv in each service | smoke | `cd services/auth && uv sync --frozen && test -d .venv` | Wave 0 |
| Docker build succeeds with uv | smoke | `docker compose build auth` | Wave 0 |
| Existing pytest tests pass with uv | integration | `cd services/auth && uv run pytest tests/ -x` | Existing tests |
| CI pipeline passes | integration | Push to branch, check GHA | Existing CI |
| Makefile targets work | smoke | `make sync-all && make test` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd services/auth && uv run pytest tests/ -x --tb=short`
- **Per wave merge:** `make test` (all services) + `docker compose build`
- **Phase gate:** Full CI pipeline green (lint + backend-tests + frontend-tests + e2e)

### Wave 0 Gaps
- [ ] `services/auth/pyproject.toml` -- uv project config (to be created)
- [ ] `services/room/pyproject.toml` -- uv project config (to be created)
- [ ] `services/booking/pyproject.toml` -- uv project config (to be created)
- [ ] `services/gateway/pyproject.toml` -- uv project config (to be created)
- [ ] `services/*/uv.lock` -- lockfiles (generated by `uv lock`)
- [ ] `Makefile` -- developer workflow automation (to be created)

## Sources

### Primary (HIGH confidence)
- [uv Docker guide](https://docs.astral.sh/uv/guides/integration/docker/) - COPY --from pattern, layer caching, --frozen vs --locked, env vars
- [uv GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/) - setup-uv@v7, caching, uv sync in CI
- [uv workspaces docs](https://docs.astral.sh/uv/concepts/projects/workspaces/) - workspace vs independent projects, path dependencies
- [uv dependencies docs](https://docs.astral.sh/uv/concepts/projects/dependencies/) - path dependency syntax, tool.uv.sources

### Secondary (MEDIUM confidence)
- [hynek.me - Production Docker with uv](https://hynek.me/articles/docker-uv/) - UV_COMPILE_BYTECODE, UV_LINK_MODE, --locked vs --frozen rationale
- [GitHub issue #16200](https://github.com/astral-sh/uv/issues/16200) - --frozen required in Docker when path deps aren't all present
- [astral-sh/setup-uv releases](https://github.com/astral-sh/setup-uv/releases) - v7 is current

### Tertiary (LOW confidence)
- uv version 0.10.12 reported as latest (March 2026) -- verify with `uv --version` or check releases before pinning

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official Astral docs, well-documented tool
- Architecture: HIGH - Patterns directly from official Docker/CI guides
- Pitfalls: HIGH - Multiple sources confirm path dep Docker issues, --frozen vs --locked
- Test migration: MEDIUM - Test directory restructuring depends on current test imports

**Research date:** 2026-03-23
**Valid until:** 2026-04-23 (uv is fast-moving but core patterns are stable)
