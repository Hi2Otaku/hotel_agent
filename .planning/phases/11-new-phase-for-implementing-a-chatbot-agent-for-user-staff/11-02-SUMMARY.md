---
phase: 11-chatbot-agent
plan: 02
subsystem: api
tags: [fastapi, sse, llm, tool-use, httpx, rabbitmq, rate-limiting, chat-engine]

# Dependency graph
requires:
  - phase: 11-chatbot-agent-01
    provides: Chat service Docker infra, DB models, LLM provider abstraction, SSE event schemas
provides:
  - Chat engine orchestrator with tool-use loop and confirmation flow
  - Prompt builder with dynamic hotel data and guest/staff personas
  - Tool registry with 6 guest + 6 staff-only tools and RBAC filtering
  - Tool executor routing 12 tools to internal service APIs
  - SSE streaming endpoint POST /api/v1/chat/send
  - Conversation CRUD endpoints (list, rename, delete)
  - Rate limiter (20 msg/min per user)
  - Event publisher for RabbitMQ chat.events exchange
  - Title generator for LLM-based conversation titles
affects: [11-03, 11-04, 11-05, gateway]

# Tech tracking
tech-stack:
  added: [sse-starlette]
  patterns: [tool-use loop with confirmation flow, provider-agnostic tool registry with RBAC, SSE streaming via EventSourceResponse]

key-files:
  created:
    - services/chat/app/services/prompt_builder.py
    - services/chat/app/services/tool_registry.py
    - services/chat/app/services/tool_executor.py
    - services/chat/app/services/chat_engine.py
    - services/chat/app/services/event_publisher.py
    - services/chat/app/services/title_generator.py
    - services/chat/app/api/v1/chat.py
    - services/chat/app/api/v1/conversations.py
    - services/chat/tests/test_tool_registry.py
    - services/chat/tests/test_tool_executor.py
    - services/chat/tests/test_prompt_builder.py
    - services/chat/tests/test_chat_api.py
    - services/chat/tests/test_rate_limiter.py
  modified:
    - services/chat/app/api/deps.py
    - services/chat/app/main.py
    - services/chat/requirements.txt

key-decisions:
  - "Tool registry stores provider-agnostic format; each LLM provider converts internally"
  - "ChatEngine uses max 5 tool-use loop iterations to prevent runaway chains"
  - "Soft limit at 50 messages appends note to system prompt for natural suggestion"
  - "sse-starlette for EventSourceResponse SSE streaming"
  - "Rate limiter queries DB for user messages in rolling 1-minute window"

patterns-established:
  - "ChatEngine: async generator yielding SSE event dicts for streaming"
  - "ToolExecutor: dynamic dispatch via getattr to _execute_{tool_name} methods"
  - "PromptBuilder: 1-hour cache per bot_type for system prompts with live hotel data"
  - "Confirmation flow: write tools save pending_confirmation, frontend re-POSTs with confirmed_message_id"

requirements-completed: [CHAT-API, CHAT-TOOLS, CHAT-ENGINE]

# Metrics
duration: 6min
completed: 2026-03-22
---

# Phase 11 Plan 02: Chat Engine Core Summary

**Chat engine with tool-use loop, SSE streaming, 12-tool registry with RBAC, confirmation flow for write actions, and 20 msg/min rate limiter**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-22T17:31:08Z
- **Completed:** 2026-03-22T17:37:10Z
- **Tasks:** 2
- **Files modified:** 18

## Accomplishments
- ChatEngine orchestrates full message flow: history load, LLM call, tool-use loop (max 5 iterations), write-action confirmation pause, and SSE streaming
- ToolRegistry defines 6 guest tools + 6 staff-only tools with RBAC role filtering and provider format conversion
- ToolExecutor routes all 12 tools to correct internal service APIs (room, booking, auth) with JWT forwarding
- PromptBuilder fetches live room types and builds dynamic system prompts with hotel info and bot personality
- Rate limiter enforces 20 messages per minute per user via DB query
- Conversation CRUD (list, rename, delete) and message history with cursor pagination

## Task Commits

Each task was committed atomically:

1. **Task 1: Prompt builder, tool registry, tool executor, event publisher, title generator** - `8b13878` (feat)
2. **Task 2: Chat engine, SSE endpoint, conversation CRUD, rate limiter** - `07606a6` (feat)

## Files Created/Modified
- `services/chat/app/services/prompt_builder.py` - Dynamic system prompt builder with hotel data and 1h cache
- `services/chat/app/services/tool_registry.py` - 12-tool registry with RBAC filtering and format converters
- `services/chat/app/services/tool_executor.py` - Routes tool calls to room/booking/auth services via httpx
- `services/chat/app/services/chat_engine.py` - Core orchestrator with tool-use loop and confirmation flow
- `services/chat/app/services/event_publisher.py` - RabbitMQ publisher for chat.events exchange
- `services/chat/app/services/title_generator.py` - LLM-based conversation title generation
- `services/chat/app/api/v1/chat.py` - POST /send SSE endpoint and GET /messages with pagination
- `services/chat/app/api/v1/conversations.py` - Conversation list, rename, delete endpoints
- `services/chat/app/api/deps.py` - Updated with rate limiter (20 msg/min, DB-based)
- `services/chat/app/main.py` - Updated with chat and conversations routers, engine dispose
- `services/chat/requirements.txt` - Added sse-starlette dependency
- `services/chat/tests/test_tool_registry.py` - 8 tests for RBAC, format, confirmation
- `services/chat/tests/test_tool_executor.py` - 4 tests for routing, auth, timeout, unknown
- `services/chat/tests/test_prompt_builder.py` - 5 tests for content, language, caching
- `services/chat/tests/test_chat_api.py` - 5 tests for routes, constants, auth
- `services/chat/tests/test_rate_limiter.py` - 5 tests for config, threshold, window

## Decisions Made
- Tool registry uses provider-agnostic format; to_anthropic_format/to_openai_format are utility helpers, not used by ChatEngine (providers convert internally)
- ChatEngine limits tool-use loop to 5 iterations to prevent runaway chains
- Soft limit at 50 messages appends system prompt note for LLM to naturally suggest new conversation
- sse-starlette chosen for EventSourceResponse (standard FastAPI SSE library)
- Rate limiter queries DB message count in rolling 1-minute window rather than in-memory counter

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added sse-starlette dependency**
- **Found during:** Task 2 (SSE endpoint)
- **Issue:** Plan referenced `from fastapi.sse import EventSourceResponse` which does not exist in FastAPI; sse-starlette is the standard library
- **Fix:** Installed sse-starlette and added to requirements.txt; used `from sse_starlette.sse import EventSourceResponse, ServerSentEvent`
- **Files modified:** services/chat/requirements.txt
- **Verification:** Import succeeds, router creates successfully
- **Committed in:** 07606a6 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for SSE support. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Chat engine core complete, ready for Plan 03 (gateway integration and frontend chat UI)
- All 12 tools registered and routed to internal APIs
- SSE streaming endpoint ready for frontend consumption
- Conversation CRUD endpoints ready for chat sidebar

---
*Phase: 11-chatbot-agent*
*Completed: 2026-03-22*
