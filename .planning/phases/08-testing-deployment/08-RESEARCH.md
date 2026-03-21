# Phase 8: Testing & Deployment - Research

**Researched:** 2026-03-22
**Domain:** Testing (pytest, Vitest, Playwright), CI/CD (GitHub Actions), Deployment (AWS EC2 + Docker Compose + Nginx)
**Confidence:** HIGH

## Summary

Phase 8 production-hardens HotelBook with comprehensive tests across all layers (126 backend tests already exist, ~7 frontend tests, 0 E2E tests), a GitHub Actions CI/CD pipeline, AWS EC2 deployment with Docker Compose and Nginx reverse proxy, and developer documentation. The project already has a solid test infrastructure: pytest-asyncio with real PostgreSQL via Docker Compose, Vitest with jsdom and React Testing Library for both frontends, and per-service conftest patterns. The main work is: (1) filling test gaps in booking/room/gateway/frontend services, (2) implementing Playwright E2E tests, (3) creating GitHub Actions workflow with Docker Compose for CI, (4) creating production Docker Compose override and Nginx config, (5) setting up EC2 auto-deploy, and (6) writing developer README.

The existing 126 backend tests span auth (25), booking (34), room (42), and gateway (8) services. Frontend has 7 existing tests (2 guest, 5 staff report stubs as `it.todo`). The target of 100+ tests is already met on the backend but frontend and E2E need significant work.

**Primary recommendation:** Focus on filling critical test gaps (frontend component tests, E2E user journeys), then build CI/CD pipeline using Docker Compose in GitHub Actions (not service containers -- the app already uses compose), and deploy with SSH-based auto-deploy to EC2.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Comprehensive coverage** -- 100+ tests across all services and frontends
- Backend: unit + integration tests for auth, booking, room, gateway services covering all critical paths and edge cases
- Frontend: Vitest + React Testing Library component tests for key components
- **E2E: Playwright** for full user journeys (guest booking flow, staff check-in/out, reports)
- Fix existing broken `tests/conftest.py` async session fixture (already partially fixed this session)
- Each service has its own test suite running against real PostgreSQL (Docker Compose test environment)
- **Full pipeline**: Lint -> Test (backend + frontend) -> Build Docker images -> Deploy
- **GitHub Actions** with Docker Compose for test environment in CI
- Separate jobs: lint, backend-tests, frontend-tests, e2e-tests, build, deploy
- Tests run on every push and PR
- Auto-deploy to production on merge to main
- **AWS EC2 + Docker Compose** -- single instance running the full stack as-is
- Docker Compose production config (separate from dev -- no hot-reload, proper env vars)
- **Auto-deploy via GitHub Actions** -- SSH into EC2, pull latest, docker compose up
- Nginx reverse proxy for SSL termination and routing (guest frontend, staff frontend, API gateway)
- SSL via Let's Encrypt / Certbot
- **Developer-focused README** -- setup instructions, environment variables, how to run tests, API endpoints list
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

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFR-02 | Unit and integration tests with CI/CD pipeline (GitHub Actions) | Backend tests (pytest-asyncio), frontend tests (Vitest + RTL), E2E tests (Playwright), GitHub Actions workflow with Docker Compose |
| INFR-03 | Deployed with live demo URL and documentation | AWS EC2 + Docker Compose prod config, Nginx reverse proxy with SSL, developer README with architecture overview |
</phase_requirements>

## Standard Stack

### Core - Testing

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.x | Backend test framework | Already in use, asyncio_mode=auto configured |
| pytest-asyncio | 1.x | Async test support | Already configured in pyproject.toml |
| httpx | 0.28.x | Async HTTP client for FastAPI testing | Already used in conftest.py with ASGITransport |
| Vitest | 4.x | Frontend unit/component testing | Already configured in both frontends |
| @testing-library/react | 16.x | React component testing | Already installed in both frontends |
| @playwright/test | 1.58.x | E2E browser testing | User-chosen; industry standard for E2E |

### Core - CI/CD & Deployment

| Library/Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| GitHub Actions | N/A | CI/CD pipeline | User-chosen; native to GitHub |
| Docker Compose | v2 | Container orchestration (CI + prod) | Already used for local dev |
| Nginx | stable-alpine | Reverse proxy + SSL termination | Industry standard for this pattern |
| Certbot | latest | Let's Encrypt SSL certificates | User-chosen; free SSL |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| appleboy/ssh-action | v1 | GitHub Action for SSH deploy | Auto-deploy step to EC2 |
| docker/setup-buildx-action | v3 | Docker buildx in CI | Building multi-platform images |
| actions/cache | v4 | Caching pip/npm/Docker layers | Speed up CI runs |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Docker Compose in CI | GHA service containers | Service containers lack volume mounts and compose networking; our app already has compose, so reuse it |
| appleboy/ssh-action | AWS CodeDeploy | CodeDeploy adds complexity; SSH is simpler for single-instance |
| Nginx on host | Traefik in compose | Traefik auto-discovers containers but Nginx is simpler for static config |

**Installation (E2E only -- new dependency):**
```bash
cd e2e && npm init -y && npm install -D @playwright/test
npx playwright install --with-deps chromium
```

## Architecture Patterns

### Recommended Project Structure (new files)

```
.github/
  workflows/
    ci.yml                    # Main CI/CD pipeline
docker-compose.prod.yml       # Production overrides
docker-compose.test.yml       # Test environment overrides (optional)
nginx/
  nginx.conf                  # Reverse proxy config
  conf.d/
    default.conf              # Server blocks for guest, staff, API
e2e/
  package.json                # Playwright dependencies
  playwright.config.ts        # Playwright configuration
  tests/
    guest-booking.spec.ts     # Guest booking flow E2E
    staff-checkin.spec.ts     # Staff check-in/out E2E
    staff-reports.spec.ts     # Staff reports E2E
README.md                     # Developer documentation
```

### Pattern 1: GitHub Actions with Docker Compose

**What:** Run the full Docker Compose stack in CI for integration/E2E tests
**When to use:** When your app already uses Docker Compose and you want CI to mirror production

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: pip install ruff
      - run: ruff check services/ tests/
      - run: cd frontend && npm ci && npm run lint
      - run: cd frontend-staff && npm ci && npm run lint

  backend-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Start databases
        run: docker compose up -d auth_db room_db booking_db rabbitmq mailpit minio
      - name: Wait for health
        run: |
          for svc in auth_db room_db booking_db; do
            docker compose exec $svc pg_isready -U $(docker compose config --format json | jq -r ".services.${svc}.environment.POSTGRES_USER") || true
          done
          sleep 10
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install deps
        run: |
          pip install -r services/auth/requirements.txt
          pip install -r services/room/requirements.txt
          pip install -r services/booking/requirements.txt
          pip install -r services/gateway/requirements.txt
          pip install pytest pytest-asyncio
          pip install shared/
      - name: Run tests
        run: pytest tests/ -x --tb=short
      - name: Teardown
        if: always()
        run: docker compose down -v

  frontend-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm ci && npm test
      - run: cd frontend-staff && npm ci && npm test

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v4
      - name: Start full stack
        run: docker compose up -d --build
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd e2e && npm ci && npx playwright install --with-deps chromium
      - name: Wait for services
        run: |
          timeout 120 bash -c 'until curl -f http://localhost:8000/health 2>/dev/null; do sleep 2; done'
      - run: cd e2e && npx playwright test
      - name: Teardown
        if: always()
        run: docker compose down -v

  deploy:
    runs-on: ubuntu-latest
    needs: e2e-tests
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /opt/hotelbook
            git pull origin main
            docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --remove-orphans
```

### Pattern 2: Docker Compose Production Override

**What:** Layer production config over the dev compose file
**When to use:** Same compose base, different env for prod

```yaml
# docker-compose.prod.yml
services:
  auth:
    restart: always
    environment:
      FIRST_ADMIN_EMAIL: ${ADMIN_EMAIL}
      FIRST_ADMIN_PASSWORD: ${ADMIN_PASSWORD}

  room:
    restart: always
    environment:
      SEED_ON_STARTUP: "false"

  gateway:
    restart: always

  booking:
    restart: always

  nginx:
    image: nginx:stable-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - gateway
    restart: always

  # Override frontend builds for production
  frontend-guest:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always

  frontend-staff:
    build:
      context: ./frontend-staff
      dockerfile: Dockerfile
    restart: always
```

### Pattern 3: Nginx Reverse Proxy Config

**What:** Route traffic to guest frontend, staff frontend, and API gateway
**When to use:** Single EC2 serving multiple services on one domain

```nginx
# nginx/conf.d/default.conf
server {
    listen 80;
    server_name hotelbook.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name hotelbook.example.com;

    ssl_certificate /etc/letsencrypt/live/hotelbook.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hotelbook.example.com/privkey.pem;

    # API Gateway
    location /api/ {
        proxy_pass http://gateway:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_for_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Staff frontend
    location /staff/ {
        proxy_pass http://frontend-staff:80/;
        proxy_set_header Host $host;
    }

    # Guest frontend (default)
    location / {
        proxy_pass http://frontend-guest:80/;
        proxy_set_header Host $host;
    }
}
```

### Pattern 4: Playwright E2E with Page Objects

**What:** E2E tests using page object pattern against running Docker Compose stack
**When to use:** Testing full user journeys through the browser

```typescript
// e2e/playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  retries: 1,
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
  ],
  webServer: [
    {
      command: 'docker compose up -d',
      url: 'http://localhost:8000/health',
      reuseExistingServer: true,
      timeout: 120_000,
    },
  ],
});
```

```typescript
// e2e/tests/guest-booking.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Guest Booking Flow', () => {
  test('complete booking from search to confirmation', async ({ page }) => {
    await page.goto('/');
    // Search for rooms
    await page.fill('[data-testid="checkin-date"]', '2026-05-01');
    await page.fill('[data-testid="checkout-date"]', '2026-05-03');
    await page.click('[data-testid="search-button"]');
    // Select a room
    await page.click('[data-testid="room-card"]:first-child [data-testid="book-now"]');
    // Fill guest details, payment, confirm...
    await expect(page.locator('[data-testid="confirmation-number"]')).toBeVisible();
  });
});
```

### Anti-Patterns to Avoid
- **Testing against SQLite instead of PostgreSQL:** The project uses PostgreSQL-specific features (JSONB, async). Always test against real Postgres.
- **Flaky E2E tests without proper waits:** Use Playwright's auto-waiting and locators, never `page.waitForTimeout()`.
- **Skipping Docker layer caching in CI:** Without caching, Docker builds add 5-10 minutes per run.
- **Hardcoding secrets in workflow files:** Always use GitHub repository secrets for SSH keys, passwords, etc.
- **Running all backend tests in one pytest invocation without service isolation:** Each service imports its own `app.main:app`. The existing conftest pattern handles this with per-service conftest.py files and pythonpath config.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSH deployment | Custom SSH scripts | appleboy/ssh-action@v1 | Handles key management, timeouts, error reporting |
| SSL certificates | Manual cert management | Certbot with auto-renewal cron | Let's Encrypt is free, Certbot handles renewal |
| Docker layer caching in CI | Manual cache management | actions/cache with Docker buildx | Proven patterns, 50-70% build time reduction |
| Health check polling | Custom bash loops | docker compose healthcheck + timeout | Compose healthchecks are declarative and reliable |
| Frontend static serving in prod | Custom Node server | Nginx serving built static files | Nginx is 10x more efficient for static files |

**Key insight:** The deployment stack (Nginx, Certbot, Docker Compose overrides) is entirely infrastructure configuration, not application code. Use proven config patterns rather than inventing bespoke solutions.

## Common Pitfalls

### Pitfall 1: Docker Compose Networking in GitHub Actions
**What goes wrong:** Service containers can't reach each other by hostname in CI
**Why it happens:** GitHub Actions runners use a different Docker network than `docker compose up`
**How to avoid:** Use `docker compose up` for the full stack (not GHA service containers). All services connect via compose's default network.
**Warning signs:** "Connection refused" errors in CI but not locally

### Pitfall 2: pytest Multi-Service App Import Collision
**What goes wrong:** `from app.main import app` resolves to wrong service
**Why it happens:** All services use `app/` as their package name; pythonpath includes all of them
**How to avoid:** The existing pattern uses per-service conftest.py with sys.path manipulation. Run tests per-service or use the existing pythonpath config carefully.
**Warning signs:** Wrong models/routes loaded, import errors about missing tables

### Pitfall 3: Playwright in CI Without Display Server
**What goes wrong:** Browser fails to launch in headless CI
**Why it happens:** Missing system dependencies for Chromium
**How to avoid:** Use `npx playwright install --with-deps chromium` which installs all system deps. Always run in headless mode (default).
**Warning signs:** "Failed to launch browser" errors

### Pitfall 4: Docker Compose Port Conflicts in CI
**What goes wrong:** E2E tests can't reach services on expected ports
**Why it happens:** Port mapping in compose exposes on host, but in CI the runner IS the host
**How to avoid:** The existing docker-compose.yml port mappings (8000, 8001-8003, 5433-5435) work on GHA Ubuntu runners. Just ensure no port conflicts.
**Warning signs:** "Address already in use" in CI logs

### Pitfall 5: Frontend Static Build for Production
**What goes wrong:** Frontend builds reference localhost API URLs
**Why it happens:** Vite inlines env vars at build time; dev proxy config doesn't apply in production
**How to avoid:** Use relative API paths (`/api/...`) in frontend code (already done via Vite proxy). In production, Nginx handles routing. Build frontends with `VITE_API_URL=/api` or rely on relative paths.
**Warning signs:** CORS errors or "connection refused" from browser in production

### Pitfall 6: EC2 Disk Space Exhaustion
**What goes wrong:** Docker images and layers accumulate, filling disk
**Why it happens:** Each deploy pulls/builds new images without cleanup
**How to avoid:** Add `docker system prune -af --volumes` (for unused) before or after deploy. Or use `--remove-orphans` flag.
**Warning signs:** "No space left on device" after several deploys

## Code Examples

### Backend Test Pattern (existing, verified from codebase)
```python
# tests/conftest.py -- savepoint pattern for test isolation
@pytest.fixture
async def client(test_engine):
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        async def override_get_db():
            nested = await conn.begin_nested()
            session = AsyncSession(bind=conn, expire_on_commit=False)
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
        app.dependency_overrides.clear()
        await trans.rollback()
```

### Frontend Test Pattern (existing, verified from codebase)
```typescript
// frontend/src/test/setup.ts -- localStorage polyfill for Node 25
if (typeof globalThis.localStorage === 'undefined' ||
    typeof globalThis.localStorage.getItem !== 'function') {
  const store: Record<string, string> = {};
  Object.defineProperty(globalThis, 'localStorage', {
    value: {
      getItem: (key: string) => store[key] ?? null,
      setItem: (key: string, value: string) => { store[key] = String(value); },
      removeItem: (key: string) => { delete store[key]; },
      clear: () => { for (const k of Object.keys(store)) delete store[k]; },
      get length() { return Object.keys(store).length; },
      key: (index: number) => Object.keys(store)[index] ?? null,
    },
    writable: true,
    configurable: true,
  });
}
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';
afterEach(() => { cleanup(); localStorage.clear(); });
```

### Frontend Dockerfile for Production
```dockerfile
# frontend/Dockerfile (new)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| GHA service containers for DB | Docker Compose up in CI | 2024+ | Better parity with prod, supports full stack |
| Cypress for E2E | Playwright | 2023+ | Faster, better auto-waiting, multi-browser |
| Manual EC2 deploy | SSH-action auto-deploy | 2024+ | Zero-touch deployment on merge |
| Self-managed SSL | Let's Encrypt + Certbot | Mature | Free, auto-renewing SSL |

## Open Questions

1. **Domain name for live demo**
   - What we know: Need a domain for SSL and live demo URL
   - What's unclear: Whether user has a domain or will use EC2 public IP with nip.io
   - Recommendation: Plan for domain-based config but make it configurable via env var

2. **Frontend build for production serving**
   - What we know: Guest frontend on /, staff frontend on /staff/
   - What's unclear: Whether to build frontends into Docker images or serve from Nginx directly
   - Recommendation: Build each frontend into its own Nginx Docker image, then reverse-proxy from the main Nginx

3. **EC2 instance sizing**
   - What we know: 10+ containers (3 DBs, RabbitMQ, MinIO, 4 services, 2 frontends, Nginx)
   - What's unclear: Memory requirements for all containers
   - Recommendation: t3.medium (2 vCPU, 4GB RAM) minimum; t3.large (8GB) for safety

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Backend Framework | pytest 9.x + pytest-asyncio 1.x |
| Frontend Framework | Vitest 4.x + @testing-library/react 16.x |
| E2E Framework | @playwright/test 1.58.x |
| Backend config | pyproject.toml (asyncio_mode=auto, testpaths=tests) |
| Frontend config | frontend/vitest.config.ts, frontend-staff/vitest.config.ts |
| Backend quick run | `pytest tests/auth -x --tb=short` |
| Frontend quick run | `cd frontend && npm test` |
| E2E quick run | `cd e2e && npx playwright test --project=chromium` |
| Full suite | `pytest tests/ -x && cd frontend && npm test && cd ../frontend-staff && npm test && cd ../e2e && npx playwright test` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFR-02 | Backend tests pass | unit+integration | `pytest tests/ -x --tb=short` | Partial (126 tests exist, gaps in some services) |
| INFR-02 | Frontend tests pass | unit | `cd frontend && npm test && cd ../frontend-staff && npm test` | Partial (7 tests, 5 are stubs) |
| INFR-02 | E2E tests pass | e2e | `cd e2e && npx playwright test` | No (new) |
| INFR-02 | CI pipeline green | integration | Push to PR branch and check GHA status | No (new) |
| INFR-03 | Docker Compose prod starts | smoke | `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d && curl -f http://localhost:8000/health` | No (new) |
| INFR-03 | Deploy succeeds | e2e | Manual -- verify live URL responds | No (new) |

### Sampling Rate
- **Per task commit:** Relevant test subset (e.g., `pytest tests/booking -x` for booking tests)
- **Per wave merge:** Full backend + frontend suite
- **Phase gate:** Full suite green including E2E, CI pipeline green on a PR

### Wave 0 Gaps
- [ ] `e2e/` directory -- Playwright project setup, config, and initial test files
- [ ] `e2e/package.json` -- Playwright dependency
- [ ] `e2e/playwright.config.ts` -- Playwright configuration
- [ ] `.github/workflows/ci.yml` -- GitHub Actions CI/CD workflow
- [ ] `docker-compose.prod.yml` -- Production overrides
- [ ] `nginx/` -- Nginx reverse proxy config directory
- [ ] `frontend/Dockerfile` -- Guest frontend production build
- [ ] `frontend-staff/Dockerfile` -- Staff frontend production build
- [ ] Convert `frontend-staff/src/components/reports/*.test.tsx` stubs from `it.todo` to real tests
- [ ] Fill test gaps in `tests/booking/`, `tests/room/`, `tests/gateway/`

## Existing Test Inventory

For planning awareness -- what already exists:

| Service | Test Files | Test Count | Coverage Notes |
|---------|-----------|------------|----------------|
| Auth | 5 files | 25 tests | Registration, login, RBAC, password reset, invites -- solid |
| Booking | 6 files | 34 tests | Booking flow, cancellation, email, management, modification, payment |
| Room | 10 files | 42 tests | Availability, calendar, pricing, rates, rooms, types, status, events |
| Gateway | 2 files | 8 tests | Booking BFF, search BFF |
| Guest Frontend | 2 files | ~2 tests | Navbar, responsive -- minimal |
| Staff Frontend | 5 files | 0 real (stubs) | Reports components -- all it.todo |
| E2E | 0 files | 0 tests | Does not exist yet |
| **Total** | **30 files** | **~111 tests** | Backend strong, frontend/E2E gaps |

## Sources

### Primary (HIGH confidence)
- Project codebase direct inspection -- pyproject.toml, docker-compose.yml, tests/, frontend configs
- [GitHub Docs - Service Containers](https://docs.github.com/en/actions/using-containerized-services/creating-postgresql-service-containers) -- CI patterns

### Secondary (MEDIUM confidence)
- [Docker Compose SSH Deployment](https://github.com/marketplace/actions/docker-compose-ssh-deployment) -- Deploy pattern
- [appleboy/ssh-action](https://github.com/marketplace/actions/docker-compose-deployment-ssh) -- SSH deploy action
- [Playwright E2E Testing Guide 2026](https://www.deviqa.com/blog/guide-to-playwright-end-to-end-testing-in-2025/) -- Playwright patterns
- [BrowserStack Playwright Docker Guide](https://www.browserstack.com/guide/playwright-docker) -- Playwright in Docker

### Tertiary (LOW confidence)
- EC2 instance sizing recommendation (t3.medium/large) -- based on general Docker memory patterns, not measured for this specific stack

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all tools already in use or well-established (pytest, Vitest, Playwright, GitHub Actions, Nginx)
- Architecture: HIGH -- patterns are standard and well-documented; project already has Docker Compose and test infrastructure
- Pitfalls: HIGH -- based on direct codebase inspection (multi-service app imports, port conflicts, frontend build URLs)
- Deployment: MEDIUM -- EC2 sizing and exact Nginx config depend on production domain and traffic

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable tools, 30-day validity)
