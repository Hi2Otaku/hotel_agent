---
phase: 05
slug: guest-frontend
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest 4.x + @testing-library/react |
| **Config file** | `frontend/vitest.config.ts` (Wave 0) |
| **Quick run command** | `cd frontend && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd frontend && npx vitest run --coverage` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npx vitest run --reporter=verbose`
- **After every plan wave:** Run `cd frontend && npx vitest run --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-XX | 01 | 1 | INFR-01 | unit | `cd frontend && npx vitest run --reporter=verbose` | ❌ W0 | ⬜ pending |
| 05-02-XX | 02 | 2 | INFR-01 | integration | `cd frontend && npx vitest run --reporter=verbose` | ❌ W0 | ⬜ pending |
| 05-03-XX | 03 | 3 | INFR-01 | integration | `cd frontend && npx vitest run --reporter=verbose` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend/vitest.config.ts` — Vitest configuration
- [ ] `frontend/src/test/setup.ts` — Testing library setup (jsdom, cleanup)
- [ ] `frontend/src/__tests__/` — Test directory structure
- [ ] Framework install: `npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual responsive at 375px/768px/1280px | INFR-01 | Requires browser rendering | 1. Open in Chrome DevTools 2. Toggle device toolbar 3. Check all breakpoints |
| Booking wizard state survives refresh | INFR-01 | Requires browser with localStorage | 1. Start booking 2. Refresh at step 2 3. Verify state preserved |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
