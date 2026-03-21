---
phase: 03
slug: availability-search
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.x + pytest-asyncio |
| **Config file** | `pyproject.toml` (root level, existing) |
| **Quick run command** | `pytest tests/room/test_search.py tests/room/test_availability.py tests/room/test_calendar.py -x -q` |
| **Full suite command** | `pytest tests/ -x -q` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/room/test_search.py tests/room/test_availability.py tests/room/test_calendar.py -x -q`
- **After every plan wave:** Run `pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-XX | 01 | 1 | ROOM-01 | integration | `pytest tests/room/test_search.py -x` | ❌ W0 | ⬜ pending |
| 03-01-XX | 01 | 1 | ROOM-02 | integration | `pytest tests/room/test_availability.py -x` | ❌ W0 | ⬜ pending |
| 03-01-XX | 01 | 1 | ROOM-03 | integration | `pytest tests/room/test_search.py -x` | ❌ W0 | ⬜ pending |
| 03-02-XX | 02 | 2 | ROOM-04 | integration | `pytest tests/room/test_calendar.py -x` | ❌ W0 | ⬜ pending |
| 03-02-XX | 02 | 2 | N/A | unit | `pytest tests/room/test_event_consumer.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/room/test_search.py` — stubs for ROOM-01, ROOM-03
- [ ] `tests/room/test_availability.py` — stubs for ROOM-02
- [ ] `tests/room/test_calendar.py` — stubs for ROOM-04
- [ ] `tests/room/test_event_consumer.py` — stubs for RabbitMQ consumer
- [ ] Update `pyproject.toml` pythonpath if needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| RabbitMQ event consumption end-to-end | N/A | Requires running RabbitMQ + Booking service (Phase 4) | 1. Start Docker Compose 2. Publish test booking event 3. Verify projection table updated |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
