---
phase: 01
slug: foundation-authentication
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-20
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.x + pytest-asyncio |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/auth/ -x -q` |
| **Full suite command** | `pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/auth/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-XX | 01 | 1 | AUTH-01 | integration | `pytest tests/auth/test_registration.py -x` | ❌ W0 | ⬜ pending |
| 01-01-XX | 01 | 1 | AUTH-02 | integration | `pytest tests/auth/test_login.py -x` | ❌ W0 | ⬜ pending |
| 01-02-XX | 02 | 1 | AUTH-03 | integration | `pytest tests/auth/test_password_reset.py -x` | ❌ W0 | ⬜ pending |
| 01-02-XX | 02 | 1 | AUTH-04 | integration | `pytest tests/auth/test_roles.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — async test fixtures, test database setup, test client factory
- [ ] `tests/auth/conftest.py` — auth-specific fixtures (test user, admin user, tokens)
- [ ] `tests/auth/test_registration.py` — stubs for AUTH-01
- [ ] `tests/auth/test_login.py` — stubs for AUTH-02
- [ ] `tests/auth/test_password_reset.py` — stubs for AUTH-03
- [ ] `tests/auth/test_roles.py` — stubs for AUTH-04
- [ ] `pytest.ini` or `pyproject.toml` with pytest config (asyncio_mode = "auto")
- [ ] Framework install: `pip install pytest pytest-asyncio httpx`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Mailpit receives password reset email | AUTH-03 | Requires running Mailpit container and checking web UI | 1. Trigger password reset 2. Open localhost:8025 3. Verify email content |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
