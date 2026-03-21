---
phase: 06
slug: staff-dashboard
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest 4.x + @testing-library/react (frontend-staff) + pytest (backend) |
| **Config file** | `frontend-staff/vitest.config.ts` (Wave 0) |
| **Quick run command** | `cd frontend-staff && npx vitest run --reporter=verbose` |
| **Full suite command** | `cd frontend-staff && npx vitest run --reporter=verbose && python -m pytest tests/booking/ -x -q` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend-staff && npx vitest run --reporter=verbose`
- **After every plan wave:** Run full suite (frontend + backend tests)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-XX | 01 | 1 | STAF-01 | integration | `python -m pytest tests/booking/test_staff_bookings.py -x` | ❌ W0 | ⬜ pending |
| 06-01-XX | 01 | 1 | STAF-02 | integration | `python -m pytest tests/booking/test_staff_checkin.py -x` | ❌ W0 | ⬜ pending |
| 06-02-XX | 02 | 2 | STAF-01 | unit | `cd frontend-staff && npx vitest run --reporter=verbose` | ❌ W0 | ⬜ pending |
| 06-02-XX | 02 | 2 | STAF-02 | unit | `cd frontend-staff && npx vitest run --reporter=verbose` | ❌ W0 | ⬜ pending |
| 06-02-XX | 02 | 2 | STAF-03 | unit | `cd frontend-staff && npx vitest run --reporter=verbose` | ❌ W0 | ⬜ pending |
| 06-02-XX | 02 | 2 | STAF-04 | unit | `cd frontend-staff && npx vitest run --reporter=verbose` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend-staff/vitest.config.ts` — Vitest configuration
- [ ] `frontend-staff/src/test/setup.ts` — Test setup with localStorage polyfill
- [ ] Backend staff booking tests (created in plan tasks)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dark theme renders correctly | N/A | Visual | 1. Open frontend-staff in browser 2. Verify dark backgrounds |
| Check-in room auto-assignment | STAF-02 | Requires live API | 1. Check in guest 2. Verify room assigned |
| Sidebar collapse on mobile | N/A | Responsive | 1. Open DevTools 2. Toggle mobile view |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
