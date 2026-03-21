---
phase: 08-testing-deployment
plan: 03
subsystem: ci-cd-docs
tags: [github-actions, ci-cd, deployment, readme, documentation, docker]

# Dependency graph
requires:
  - phase: 08-testing-deployment
    plan: 01
    provides: Test commands for CI pipeline (pytest, vitest, playwright)
  - phase: 08-testing-deployment
    plan: 02
    provides: Docker Compose prod override and Nginx config for deploy job
provides:
  - CI/CD pipeline with 6-job dependency chain
  - Developer documentation for project onboarding
affects:
  - .github/workflows/ci.yml
  - README.md

# Tech stack
added: [github-actions, appleboy/ssh-action]
patterns: [ci-cd-pipeline, docker-compose-in-ci, ssh-deploy]

# Key files
created:
  - .github/workflows/ci.yml
  - README.md

# Decisions
key-decisions:
  - "Docker Compose in CI over GHA service containers for production parity"
  - "SSH-based deploy to EC2 via appleboy/ssh-action for simplicity"
  - "6-job pipeline: lint -> backend-tests + frontend-tests -> e2e-tests -> build -> deploy"
  - "Build job validates Docker images compile before deploy (no registry push)"

# Metrics
duration: 2min
completed: "2026-03-21T17:45:30Z"
---

# Phase 08 Plan 03: CI/CD Pipeline & Developer README Summary

GitHub Actions 6-job CI/CD pipeline (lint, backend-tests, frontend-tests, e2e-tests, build, deploy) with SSH auto-deploy to EC2 on merge to main, plus comprehensive developer README covering architecture, setup, testing, deployment, and API reference.

## What Was Built

### Task 1: GitHub Actions CI/CD Pipeline
Created `.github/workflows/ci.yml` with 6 jobs in a dependency chain:

1. **lint** -- ruff for backend Python, eslint for both React frontends
2. **backend-tests** (needs: lint) -- Docker Compose starts infrastructure containers, pytest runs against real PostgreSQL with RSA key generation
3. **frontend-tests** (needs: lint) -- Vitest for guest and staff frontends with npm caching
4. **e2e-tests** (needs: backend-tests, frontend-tests) -- Full Docker stack build, Playwright chromium with artifact upload on failure
5. **build** (needs: e2e-tests) -- Docker Compose prod build to validate all images compile
6. **deploy** (needs: build, only on push to main) -- SSH to EC2 via appleboy/ssh-action, git pull + docker compose up

Triggers on push to `main` and pull requests to `main`. Includes pip and npm caching for faster CI runs.

### Task 2: Developer README
Created `README.md` with 10+ sections:
- ASCII architecture diagram showing service topology
- Service and tech stack reference tables
- Quick start guide (JWT keys, Docker Compose, health check)
- Test commands for all layers (backend, frontend, E2E)
- Project structure directory tree
- Deployment guide with CI/CD pipeline overview and SSL setup
- Environment variables reference (17 variables)
- API endpoints summary table
- Live demo URL placeholders and demo credentials

## Verification Results

- `.github/workflows/ci.yml` validates as valid YAML
- Contains all 6 jobs with correct dependency chain
- Pipeline triggers on push/PR to main
- Deploy job uses `appleboy/ssh-action` with `secrets.EC2_HOST`
- README has 22 sections covering all required topics
- README includes architecture, setup, testing, deployment, env vars, API endpoints

## Deviations from Plan

None -- plan executed exactly as written.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | b55669d | feat(08-03): add GitHub Actions CI/CD pipeline with 6 jobs |
| 2 | 653af10 | feat(08-03): add developer README with architecture and setup docs |
