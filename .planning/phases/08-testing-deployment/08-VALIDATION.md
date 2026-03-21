# Phase 8: Testing & Deployment - Validation

**Generated:** 2026-03-22
**Source:** 08-RESEARCH.md Validation Architecture section

## Test Framework

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

## Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFR-02 | Backend tests pass | unit+integration | `pytest tests/ -x --tb=short` | Partial (126 tests exist, gaps in some services) |
| INFR-02 | Frontend tests pass | unit | `cd frontend && npm test && cd ../frontend-staff && npm test` | Partial (7 tests, 5 are stubs) |
| INFR-02 | E2E tests pass | e2e | `cd e2e && npx playwright test` | No (new) |
| INFR-02 | CI pipeline green | integration | Push to PR branch and check GHA status | No (new) |
| INFR-03 | Docker Compose prod starts | smoke | `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d && curl -f http://localhost:8000/health` | No (new) |
| INFR-03 | Deploy succeeds | e2e | Manual -- verify live URL responds | No (new) |

## Sampling Rate

- **Per task commit:** Relevant test subset (e.g., `pytest tests/booking -x` for booking tests)
- **Per wave merge:** Full backend + frontend suite
- **Phase gate:** Full suite green including E2E, CI pipeline green on a PR

## Wave 0 Gaps

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
