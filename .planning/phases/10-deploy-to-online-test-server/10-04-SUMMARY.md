---
phase: 10-deploy-to-online-test-server
plan: 04
subsystem: infra
tags: [env-template, secrets, gap-closure]
gap_closure: true

requires:
  - phase: 10-deploy-to-online-test-server
    provides: Original env template from plan 01
provides:
  - Corrected production environment template with JWT keys and no MinIO
affects: [10-deploy-to-online-test-server]

key-files:
  modified:
    - .env.production.template

requirements-completed: [DEPLOY-02]

duration: 1min
completed: 2026-03-22
---

# Phase 10 Plan 04: Fix Production Environment Template (Gap Closure)

**Added JWT_PRIVATE_KEY and JWT_PUBLIC_KEY to .env.production.template, removed dev-only MinIO variables**

## Performance

- **Duration:** 1 min
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added JWT_PRIVATE_KEY and JWT_PUBLIC_KEY entries with CHANGE_ME placeholders and PEM format documentation
- Removed MINIO_ROOT_USER and MINIO_ROOT_PASSWORD (dev-only, not in prod compose)
- Template now documents all 8 production secrets matching CI/CD envs parameter

## Task Commits

1. **Task 1: Fix production environment template** - `4d2f05b` (fix)

## Gap Closed
- UAT Test 2: ".env.production.template documents JWT_PRIVATE_KEY and JWT_PUBLIC_KEY" — now passes

## Deviations from Plan
None.

## Issues Encountered
None.

---
*Phase: 10-deploy-to-online-test-server*
*Completed: 2026-03-22*
