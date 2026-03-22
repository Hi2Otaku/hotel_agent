---
phase: 11
slug: new-phase-for-implementing-a-chatbot-agent-for-user-staff
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend), vitest 3.x (frontend) |
| **Config file** | `tests/conftest.py` (backend), `frontend/vitest.config.ts` / `frontend-staff/vitest.config.ts` (frontend) |
| **Quick run command** | `pytest tests/chat/ -x -q` / `cd frontend && npx vitest run src/components/chat/` |
| **Full suite command** | `pytest tests/chat/ -v` / `cd frontend && npx vitest run` / `cd frontend-staff && npx vitest run` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/chat/ -x -q`
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | CHAT-INFRA | unit | `pytest tests/chat/test_models.py -x` | ❌ W0 | ⬜ pending |
| 11-01-02 | 01 | 1 | CHAT-LLM | unit | `pytest tests/chat/test_providers.py -x` | ❌ W0 | ⬜ pending |
| 11-02-01 | 02 | 1 | CHAT-API | integration | `pytest tests/chat/test_endpoints.py -x` | ❌ W0 | ⬜ pending |
| 11-02-02 | 02 | 1 | CHAT-TOOLS | integration | `pytest tests/chat/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 11-03-01 | 03 | 2 | CHAT-UI-GUEST | component | `cd frontend && npx vitest run src/components/chat/` | ❌ W0 | ⬜ pending |
| 11-03-02 | 03 | 2 | CHAT-UI-STAFF | component | `cd frontend-staff && npx vitest run src/components/chat/` | ❌ W0 | ⬜ pending |
| 11-04-01 | 04 | 3 | CHAT-MCP | integration | `pytest tests/chat/test_mcp.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/chat/conftest.py` — shared fixtures for chat service tests
- [ ] `tests/chat/test_models.py` — stubs for conversation/message model tests
- [ ] `tests/chat/test_providers.py` — stubs for LLM provider abstraction tests
- [ ] `tests/chat/test_endpoints.py` — stubs for chat API endpoint tests
- [ ] `tests/chat/test_tools.py` — stubs for tool-use tests
- [ ] `tests/chat/test_mcp.py` — stubs for MCP server tests
- [ ] `frontend/src/components/chat/__tests__/` — stubs for guest chat component tests
- [ ] `frontend-staff/src/components/chat/__tests__/` — stubs for staff chat component tests

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SSE streaming renders progressively | CHAT-STREAM | Real-time rendering requires visual confirmation | Open chat, send message, verify tokens appear progressively |
| Rich room cards display correctly | CHAT-CARDS | Visual layout verification | Bot returns room search results, verify card layout with photo/price/button |
| Tool confirmation flow UX | CHAT-CONFIRM | Multi-step user interaction | Ask bot to book room, verify confirmation prompt appears before action executes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
