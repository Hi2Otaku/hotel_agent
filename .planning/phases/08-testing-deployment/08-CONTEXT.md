# Phase 8: Testing & Deployment - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Production-harden HotelBook with comprehensive tests (backend + frontend + E2E), a GitHub Actions CI/CD pipeline with auto-deploy, AWS EC2 hosting with Docker Compose, and developer-focused documentation. This is the final phase — after this, the project is a complete portfolio piece with a live demo URL.

</domain>

<decisions>
## Implementation Decisions

### Test Strategy & Coverage
- **Comprehensive coverage** — 100+ tests across all services and frontends
- Backend: unit + integration tests for auth, booking, room, gateway services covering all critical paths and edge cases
- Frontend: Vitest + React Testing Library component tests for key components
- **E2E: Playwright** for full user journeys (guest booking flow, staff check-in/out, reports)
- Fix existing broken `tests/conftest.py` async session fixture (already partially fixed this session)
- Each service has its own test suite running against real PostgreSQL (Docker Compose test environment)

### CI/CD Pipeline
- **Full pipeline**: Lint → Test (backend + frontend) → Build Docker images → Deploy
- **GitHub Actions** with Docker Compose for test environment in CI
- Separate jobs: lint, backend-tests, frontend-tests, e2e-tests, build, deploy
- Tests run on every push and PR
- Auto-deploy to production on merge to main

### Deployment
- **AWS EC2 + Docker Compose** — single instance running the full stack as-is
- Docker Compose production config (separate from dev — no hot-reload, proper env vars)
- **Auto-deploy via GitHub Actions** — SSH into EC2, pull latest, docker compose up
- Nginx reverse proxy for SSL termination and routing (guest frontend, staff frontend, API gateway)
- SSL via Let's Encrypt / Certbot

### Documentation
- **Developer-focused README** — setup instructions, environment variables, how to run tests, API endpoints list
- Architecture overview section explaining microservice structure
- How to run locally (Docker Compose), how to run tests, how to deploy
- Live demo link prominently displayed
- FastAPI auto-generated Swagger docs already exist at /docs on each service

### Claude's Discretion
- Exact GitHub Actions job structure and caching strategy
- Nginx configuration details
- Docker Compose production overrides
- Test fixture patterns and data seeding approach
- EC2 instance type and security group config
- Playwright test structure and page object patterns

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements are fully captured in decisions above and REQUIREMENTS.md.

### Requirements
- `.planning/REQUIREMENTS.md` — INFR-02 (tests + CI/CD), INFR-03 (deployment + docs)

### Existing Test Infrastructure
- `tests/conftest.py` — Core test fixtures (recently rewritten with connection-scoped transactions)
- `tests/auth/conftest.py` — Auth-specific fixtures (admin_token, registered_guest)
- `pyproject.toml` — pytest configuration (asyncio_mode, testpaths, pythonpath)
- `frontend-staff/src/components/reports/*.test.tsx` — Phase 7 test stubs (Vitest + it.todo)

### Deployment Infrastructure
- `docker-compose.yml` — Full local orchestration (10 containers)
- `services/*/Dockerfile` — Per-service Docker builds
- `services/*/entrypoint.sh` — Migration + server startup scripts

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/conftest.py` — Async session fixture with savepoint pattern (recently fixed)
- `tests/auth/` — 25 existing tests (registration, login, RBAC, password reset, invites)
- `tests/booking/`, `tests/room/`, `tests/gateway/` — Test directories exist but mostly empty
- `frontend-staff/src/components/reports/*.test.tsx` — 5 Vitest stubs with it.todo()

### Established Patterns
- pytest-asyncio with real PostgreSQL (not SQLite) via Docker Compose
- FastAPI dependency_overrides for test session isolation
- Each service has Alembic migrations run at container startup
- Vitest configured in frontend-staff with jsdom + Node 25 localStorage polyfill

### Integration Points
- `.github/workflows/` — Does not exist yet (create CI/CD workflows here)
- `docker-compose.yml` — Needs production override file (`docker-compose.prod.yml`)
- `nginx/` — New directory for reverse proxy config
- Root `README.md` — Does not exist in project root

</code_context>

<specifics>
## Specific Ideas

- Portfolio piece — CI/CD and deployment should demonstrate engineering rigor
- Tests should run in Docker Compose in CI, matching production environment
- Live demo URL should show both guest and staff interfaces

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-testing-deployment*
*Context gathered: 2026-03-21*
