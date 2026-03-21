---
phase: 02
slug: room-rate-management
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-21
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.x + pytest-asyncio |
| **Config file** | `pyproject.toml` (root level, existing — extend pythonpath) |
| **Quick run command** | `pytest tests/room/ -x -q` |
| **Full suite command** | `pytest tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/room/ -x -q`
- **After every plan wave:** Run `pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-XX | 01 | 1 | RMGT-01 | integration | `pytest tests/room/test_room_types.py -x` | ❌ W0 | ⬜ pending |
| 02-01-XX | 01 | 1 | RMGT-02 | integration | `pytest tests/room/test_rooms.py -x` | ❌ W0 | ⬜ pending |
| 02-02-XX | 02 | 2 | RMGT-03 | integration | `pytest tests/room/test_status_board.py -x` | ❌ W0 | ⬜ pending |
| 02-02-XX | 02 | 2 | RMGT-04 | integration | `pytest tests/room/test_status_transitions.py -x` | ❌ W0 | ⬜ pending |
| 02-03-XX | 03 | 3 | RATE-01 | integration | `pytest tests/room/test_rates.py -x` | ❌ W0 | ⬜ pending |
| 02-03-XX | 03 | 3 | RATE-02 | unit+integration | `pytest tests/room/test_pricing.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/room/__init__.py` — test package init
- [ ] `tests/room/conftest.py` — room service fixtures (db session, client, auth tokens, MinIO mock)
- [ ] `tests/room/test_room_types.py` — stubs for RMGT-01
- [ ] `tests/room/test_rooms.py` — stubs for RMGT-02
- [ ] `tests/room/test_status_board.py` — stubs for RMGT-03
- [ ] `tests/room/test_status_transitions.py` — stubs for RMGT-04
- [ ] `tests/room/test_rates.py` — stubs for RATE-01
- [ ] `tests/room/test_pricing.py` — stubs for RATE-02
- [ ] Update `pyproject.toml` pythonpath to include `services/room`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MinIO photo upload via browser | RMGT-01 | Requires running MinIO container and multipart form | 1. Start Docker Compose 2. Upload photo via API 3. Check MinIO console at localhost:9001 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
