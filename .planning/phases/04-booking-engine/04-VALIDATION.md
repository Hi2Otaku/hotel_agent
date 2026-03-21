---
phase: 04
slug: booking-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.x + pytest-asyncio |
| **Config file** | `pyproject.toml` (root level, existing — extend pythonpath) |
| **Quick run command** | `pytest tests/booking/ -x -q` |
| **Full suite command** | `pytest tests/ -x -q` |
| **Estimated runtime** | ~25 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/booking/ -x -q`
- **After every plan wave:** Run `pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 25 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-XX | 01 | 1 | BOOK-01 | integration | `pytest tests/booking/test_booking_flow.py -x` | ❌ W0 | ⬜ pending |
| 04-01-XX | 01 | 1 | BOOK-02 | unit+integration | `pytest tests/booking/test_payment.py -x` | ❌ W0 | ⬜ pending |
| 04-01-XX | 01 | 1 | BOOK-03 | integration | `pytest tests/booking/test_booking_flow.py -x` | ❌ W0 | ⬜ pending |
| 04-02-XX | 02 | 2 | BOOK-04 | unit | `pytest tests/booking/test_email.py -x` | ❌ W0 | ⬜ pending |
| 04-02-XX | 02 | 2 | BOOK-05 | integration | `pytest tests/booking/test_cancellation.py -x` | ❌ W0 | ⬜ pending |
| 04-02-XX | 02 | 2 | MGMT-01 | integration | `pytest tests/booking/test_management.py -x` | ❌ W0 | ⬜ pending |
| 04-02-XX | 02 | 2 | MGMT-02 | integration | `pytest tests/booking/test_cancellation.py -x` | ❌ W0 | ⬜ pending |
| 04-03-XX | 03 | 3 | MGMT-03 | integration | `pytest tests/booking/test_modification.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/booking/__init__.py` — package init
- [ ] `tests/booking/conftest.py` — booking service fixtures (db session, mock user, mock room service)
- [ ] `tests/booking/test_booking_flow.py` — stubs for BOOK-01, BOOK-03
- [ ] `tests/booking/test_payment.py` — stubs for BOOK-02
- [ ] `tests/booking/test_email.py` — stubs for BOOK-04
- [ ] `tests/booking/test_cancellation.py` — stubs for BOOK-05, MGMT-02
- [ ] `tests/booking/test_management.py` — stubs for MGMT-01
- [ ] `tests/booking/test_modification.py` — stubs for MGMT-03
- [ ] Update `pyproject.toml` pythonpath to include `services/booking`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Mailpit receives confirmation email | BOOK-04 | Requires running Mailpit container | 1. Complete booking flow 2. Check localhost:8025 for email |
| RabbitMQ events received by Room service | N/A | Requires full Docker Compose stack | 1. Create booking 2. Check Room service reservation_projections table |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 25s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
