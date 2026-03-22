---
phase: 11-chatbot-agent
plan: 01
subsystem: infra
tags: [fastapi, postgresql, sqlalchemy, alembic, anthropic, openai, llm, docker, jwt, sse]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: RS256 JWT signing, shared database utilities, RabbitMQ messaging
provides:
  - Chat service Docker container with chat_db PostgreSQL
  - Conversation and Message SQLAlchemy models with JSONB fields
  - LLM provider abstraction (Anthropic + OpenAI) with streaming
  - JWT verification for chat service
  - SSE event schemas for streaming responses
affects: [11-02, 11-03, 11-04, 11-05, gateway]

# Tech tracking
tech-stack:
  added: [anthropic, openai, PyJWT]
  patterns: [LLM provider abstraction, StreamChunk dataclass, async streaming iterator]

key-files:
  created:
    - services/chat/Dockerfile
    - services/chat/app/core/config.py
    - services/chat/app/core/database.py
    - services/chat/app/core/security.py
    - services/chat/app/models/conversation.py
    - services/chat/app/models/message.py
    - services/chat/app/schemas/chat.py
    - services/chat/app/schemas/sse_events.py
    - services/chat/app/llm/base.py
    - services/chat/app/llm/anthropic_provider.py
    - services/chat/app/llm/openai_provider.py
    - services/chat/app/api/deps.py
    - services/chat/alembic/versions/001_initial_chat_models.py
  modified:
    - docker-compose.yml

key-decisions:
  - "LLM provider abstraction with factory function for runtime provider selection"
  - "StreamChunk dataclass as unified streaming format across Anthropic and OpenAI"
  - "JWT verification only (no signing) in chat service, consistent with booking service pattern"
  - "JSONB columns for tool_calls, tool_results, pending_confirmation on Message model"

patterns-established:
  - "LLMProvider ABC: stream_message yields StreamChunk, get_usage returns TokenUsage"
  - "Chat service follows same Dockerfile/entrypoint/config/database pattern as booking service"
  - "SSE event models as Pydantic BaseModel subclasses for type-safe streaming"

requirements-completed: [CHAT-INFRA, CHAT-LLM]

# Metrics
duration: 5min
completed: 2026-03-22
---

# Phase 11 Plan 01: Chat Service Scaffolding Summary

**Chat microservice with Docker infra, PostgreSQL models, Alembic migrations, and dual LLM provider abstraction (Anthropic + OpenAI) with streaming**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-22T17:22:48Z
- **Completed:** 2026-03-22T17:28:13Z
- **Tasks:** 2
- **Files modified:** 30

## Accomplishments
- Chat service Docker container builds and starts with chat_db PostgreSQL on port 5436
- Conversation and Message models with JSONB tool_calls, pending_confirmation, and token tracking
- LLM provider abstraction with AnthropicProvider and OpenAIProvider streaming implementations
- Factory function selects provider by string name, MockLLMProvider for testing
- 8 passing tests covering factory selection, mock streaming, and model instantiation

## Task Commits

Each task was committed atomically:

1. **Task 1: Chat service scaffolding, Docker infra, DB models, migrations** - `792f550` (feat)
2. **Task 2: LLM provider abstraction layer with Anthropic + OpenAI and test stubs** - `0787826` (feat)

## Files Created/Modified
- `services/chat/Dockerfile` - Python 3.12-slim container with shared lib and service deps
- `services/chat/entrypoint.sh` - Alembic upgrade then uvicorn startup
- `services/chat/requirements.txt` - FastAPI, SQLAlchemy, anthropic, openai, PyJWT, pytest
- `services/chat/app/core/config.py` - Settings with LLM provider, model, API key, DB, RabbitMQ
- `services/chat/app/core/database.py` - Async engine and session factory using shared lib
- `services/chat/app/core/security.py` - RS256 JWT verification (public key only)
- `services/chat/app/api/deps.py` - get_db, get_current_user, rate_limiter placeholder
- `services/chat/app/models/conversation.py` - Conversation model with user_id, bot_type, title
- `services/chat/app/models/message.py` - Message model with JSONB tool_calls, pending_confirmation, token tracking
- `services/chat/app/schemas/chat.py` - SendMessageRequest, ConversationResponse, MessageResponse
- `services/chat/app/schemas/sse_events.py` - TextDelta, ToolStart, ToolResult, ConfirmationRequired, Done, Error events
- `services/chat/app/llm/base.py` - LLMProvider ABC, StreamChunk, TokenUsage dataclasses
- `services/chat/app/llm/anthropic_provider.py` - AnthropicProvider with messages.stream
- `services/chat/app/llm/openai_provider.py` - OpenAIProvider with function calling format conversion
- `services/chat/app/llm/__init__.py` - get_llm_provider factory function
- `services/chat/alembic/versions/001_initial_chat_models.py` - Create conversations + messages tables
- `services/chat/tests/conftest.py` - MockLLMProvider, test_user_claims fixtures
- `services/chat/tests/test_models.py` - Model instantiation tests
- `services/chat/tests/test_llm_providers.py` - Factory and streaming tests
- `docker-compose.yml` - Added chat_db (port 5436) and chat service (port 8010)

## Decisions Made
- LLM provider abstraction with factory function for runtime provider selection by string name
- StreamChunk dataclass as unified streaming format across both Anthropic and OpenAI providers
- JWT verification only (no signing) in chat service, consistent with booking service pattern
- JSONB columns for tool_calls, tool_results, pending_confirmation on Message model for flexible schema
- Added pytest/pytest-asyncio to requirements for in-container test execution

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added pytest/pytest-asyncio to requirements.txt**
- **Found during:** Task 2 (test execution)
- **Issue:** pytest not available in container for running tests
- **Fix:** Added pytest>=8.0 and pytest-asyncio>=0.24.0 to requirements.txt
- **Files modified:** services/chat/requirements.txt
- **Verification:** All 8 tests pass in container
- **Committed in:** 0787826 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for test execution. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Chat service infrastructure ready for Plan 02 (chat endpoints and conversation API)
- LLM provider abstraction ready for tool-use integration in Plan 03
- SSE event models ready for streaming endpoint implementation

---
*Phase: 11-chatbot-agent*
*Completed: 2026-03-22*
