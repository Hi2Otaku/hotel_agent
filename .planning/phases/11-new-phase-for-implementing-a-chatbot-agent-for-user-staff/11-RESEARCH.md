# Phase 11: Chatbot Agent for User & Staff - Research

**Researched:** 2026-03-22
**Domain:** AI Chatbot (LLM integration, SSE streaming, tool-use, MCP server)
**Confidence:** HIGH

## Summary

This phase adds an AI-powered chatbot to the existing HotelBook microservices architecture. The backend is a new FastAPI chat service (port 8010) with its own PostgreSQL database, pluggable LLM provider abstraction (Anthropic + OpenAI SDKs), SSE streaming to the frontend, function-calling tool use for hotel operations, and a separate MCP server for external AI clients. The frontend adds a ChatGPT-style chat interface to both guest and staff applications with conversation management, markdown rendering, inline tool status cards, and rich room cards.

The project already uses FastAPI >= 0.135.0 which has **native SSE support** via `fastapi.sse.EventSourceResponse` and `ServerSentEvent` -- no third-party SSE library needed. Both the Anthropic SDK (0.86.0) and OpenAI SDK (2.29.0) support async streaming with tool use. The MCP Python SDK (1.26.0) provides `FastMCP` for building tool servers with minimal boilerplate.

**Primary recommendation:** Build a thin LLM provider abstraction layer that normalizes Anthropic and OpenAI streaming APIs into a common async generator interface, then pipe that through FastAPI's native SSE to the frontend. Use the existing microservice patterns (database-per-service, RabbitMQ events, gateway proxy, JWT auth) exactly as established in phases 1-10.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Pluggable LLM provider behind an abstract interface -- both Anthropic SDK (Claude) and OpenAI SDK implementations from day one
- Default model: Claude Sonnet 4.6, configurable via `CHAT_LLM_MODEL` env var
- Provider and API key configured via environment variables (`CHAT_LLM_PROVIDER`, `CHAT_LLM_API_KEY`)
- New chat microservice on port 8010 with its own PostgreSQL database (`chat_db`) and Docker container
- SSE (Server-Sent Events) for streaming responses -- user messages sent via regular POST
- Dynamic system prompt built at runtime from actual hotel data (room types, rates, policies from DB)
- Tool-use (function calling) enabled -- bot calls internal APIs as tools
- Write actions (create booking, cancel, modify) require user confirmation before executing
- Read-only actions (search, status check) execute immediately
- Retry once with backoff on LLM API failure, then show graceful fallback message
- Per-user rate limiting on chat messages (e.g., 20 messages/minute)
- Conversation history persisted in chat_db -- users can return to past conversations
- Soft limit ~50 messages per conversation before suggesting a new one
- Token usage and estimated cost tracked per message for analytics
- Publish chat events to RabbitMQ (`chat.events` exchange) for integration with other services
- Separate MCP server process exposing read-only tools (search, status, reports) for external AI clients
- Guest capabilities: search rooms, create bookings (multi-turn), manage bookings, hotel FAQs, rich inline room cards, starter chips, auto-detect language, auth required
- Staff capabilities: all guest plus check-in/out, room status updates, reports/metrics, guest lookup, RBAC-based tool access
- ChatGPT-style layout: conversation sidebar (280px) + active chat area
- Mobile: sidebar as Sheet drawer
- Separate bots with distinct names (HotelBook Assistant / HB Ops) and personalities
- Chat components copied into each frontend with styling adjustments (no shared package)
- Chat accessible via nav link (guest Navbar) / sidebar item (staff Sidebar)
- Dedicated `/chat` page with full-height layout, no footer

### Claude's Discretion
- Exact message bubble styling and spacing
- Loading skeleton design for chat page
- Scroll behavior and auto-scroll logic
- Error state UI for failed messages
- Exact rate limit numbers
- MCP server port and transport details
- RabbitMQ routing key naming for chat events

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

## Standard Stack

### Core -- Backend (Chat Service)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi[standard] | >=0.135.0 | HTTP framework with native SSE | Already in project; 0.135+ has built-in `EventSourceResponse` |
| uvicorn[standard] | latest | ASGI server | Project standard |
| sqlalchemy[asyncio] | >=2.0.48 | Async ORM for chat_db | Project standard |
| asyncpg | latest | PostgreSQL async driver | Project standard |
| alembic | >=1.18.0 | Database migrations | Project standard |
| pydantic-settings | >=2.0 | Configuration from env vars | Project standard |
| anthropic | >=0.86.0 | Claude API with streaming + tool use | Locked decision -- Anthropic provider |
| openai | >=2.29.0 | OpenAI API with streaming + tool use | Locked decision -- OpenAI provider |
| httpx | latest | Internal service-to-service HTTP calls | Project standard (tools call booking/room/auth APIs) |
| aio-pika | >=9.6.0 | RabbitMQ event publishing | Project standard |
| PyJWT[crypto] | >=2.12.0 | JWT verification (claims-based auth) | Project standard |

### Core -- Backend (MCP Server)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| mcp | >=1.26.0 | MCP Python SDK with FastMCP | Official MCP SDK; `FastMCP` provides decorator-based tool registration |
| httpx | latest | Calls internal APIs for tool execution | Same as chat service |
| uvicorn[standard] | latest | Runs MCP server HTTP transport | Consistent with project |

### Core -- Frontend (both apps)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-markdown | 10.1.0 | Render markdown in bot messages | UI-SPEC specifies markdown rendering in bubbles |
| remark-gfm | 4.0.1 | GitHub Flavored Markdown support | Tables, strikethrough, task lists in bot responses |
| eventsource-parser | 3.0.6 | Parse SSE streams from chat API | Handles chunked SSE parsing for token-by-token streaming |

### Already Available (no new install)

| Library | Purpose | Notes |
|---------|---------|-------|
| zustand | Chat state management (messages, conversations, UI) | Already in both frontends |
| @tanstack/react-query | Conversation list, message history fetching | Already in both frontends |
| axios | Chat API calls (POST message, GET conversations) | Already in both frontends |
| lucide-react | Icons (Send, MessageSquare, Loader2, ChevronDown) | Already in both frontends |
| radix-ui (shadcn) | ScrollArea, Sheet, Dialog, DropdownMenu, Skeleton | Already in both frontends |
| date-fns | Conversation timestamps formatting | Already in both frontends |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Native fastapi.sse | sse-starlette | FastAPI 0.135+ has first-class SSE; no external dep needed |
| eventsource-parser | Native EventSource API | EventSource API only supports GET; chat needs POST for messages, so manual SSE parsing required |
| anthropic + openai SDKs | litellm | litellm abstracts providers but adds a heavy dependency; direct SDKs give full control over streaming + tool use |
| mcp SDK FastMCP | Custom REST API | MCP is the standard protocol for LLM tool servers; provides client interop for free |

**Installation (chat service):**
```bash
pip install "fastapi[standard]" "uvicorn[standard]" "sqlalchemy[asyncio]" asyncpg alembic pydantic-settings anthropic openai httpx "aio-pika>=9.6.0" "PyJWT[crypto]>=2.12.0"
```

**Installation (MCP server):**
```bash
pip install "mcp[cli]>=1.26.0" httpx uvicorn
```

**Installation (guest frontend):**
```bash
npm install react-markdown remark-gfm eventsource-parser
npx shadcn@latest add scroll-area
```

**Installation (staff frontend):**
```bash
npm install react-markdown remark-gfm eventsource-parser
```

## Architecture Patterns

### Recommended Project Structure -- Chat Service

```
services/chat/
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, lifespan, CORS, routers
│   ├── core/
│   │   ├── config.py              # Settings (DB, LLM provider, API keys, RabbitMQ)
│   │   ├── database.py            # Engine, session factory (shared pattern)
│   │   └── security.py            # JWT verification (claims-based, public key only)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py        # Conversation model (id, user_id, title, created_at, updated_at)
│   │   └── message.py             # Message model (id, conversation_id, role, content, tool_calls, token_usage, cost_estimate)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py                # SendMessage, MessageResponse, ConversationResponse
│   │   └── sse_events.py          # SSE event types (text_delta, tool_start, tool_result, done, error)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # get_db, get_current_user (JWT claims), rate_limiter
│   │   └── v1/
│   │       ├── chat.py            # POST /send (SSE), GET /conversations, GET /conversations/:id/messages
│   │       └── conversations.py   # PATCH /conversations/:id (rename), DELETE /conversations/:id
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_engine.py         # Orchestrates: build prompt -> call LLM -> handle tool use -> stream response
│   │   ├── prompt_builder.py      # Builds dynamic system prompt from hotel data
│   │   ├── tool_registry.py       # Registers available tools per bot type (guest vs staff)
│   │   ├── tool_executor.py       # Executes tool calls via internal HTTP APIs
│   │   ├── event_publisher.py     # Publishes chat events to RabbitMQ
│   │   └── title_generator.py     # LLM-generated conversation title after first exchange
│   └── llm/
│       ├── __init__.py
│       ├── base.py                # Abstract LLMProvider interface
│       ├── anthropic_provider.py  # Anthropic SDK implementation
│       └── openai_provider.py     # OpenAI SDK implementation
```

### Recommended Project Structure -- MCP Server

```
services/mcp-server/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── server.py                  # FastMCP instance with @mcp.tool() decorators
│   └── tools/
│       ├── search.py              # Room search tools
│       ├── booking.py             # Booking status lookup
│       └── reports.py             # Occupancy, revenue read-only reports
```

### Recommended Frontend Structure (copied per app)

```
frontend/src/features/chat/
├── ChatPage.tsx                   # /chat route, full-height layout
├── ChatLayout.tsx                 # Sidebar + ChatArea flex container
├── components/
│   ├── ConversationSidebar.tsx    # 280px sidebar, conversation list, new chat button
│   ├── ConversationList.tsx       # Sorted conversations with context menu
│   ├── ChatArea.tsx               # Messages + input bar container
│   ├── MessageList.tsx            # Scrollable message container (role="log")
│   ├── MessageBubble.tsx          # Bot (left) / User (right) bubble with markdown
│   ├── ToolStatusCard.tsx         # Inline tool action status (search, booking, etc.)
│   ├── RoomCard.tsx               # Inline rich room card (photo, price, amenities, "Book this")
│   ├── ConfirmationCard.tsx       # Write action confirmation prompt
│   ├── WelcomeMessage.tsx         # Avatar + greeting + starter chips
│   ├── StarterChips.tsx           # Prompt suggestion chips
│   ├── MessageInput.tsx           # Auto-grow textarea + send button
│   ├── TypingIndicator.tsx        # Animated dots + status text
│   └── ScrollToBottom.tsx         # Floating scroll-to-bottom button
├── hooks/
│   ├── useChat.ts                 # Main chat hook: send message, SSE streaming, tool handling
│   ├── useConversations.ts        # React Query for conversation CRUD
│   └── useAutoScroll.ts           # Auto-scroll logic with pause-on-scroll-up
├── stores/
│   └── chatStore.ts               # Zustand: current conversation, messages, streaming state
├── api/
│   └── chatApi.ts                 # API functions (sendMessage, getConversations, etc.)
└── types/
    └── chat.ts                    # TypeScript types for messages, conversations, SSE events
```

### Pattern 1: LLM Provider Abstraction

**What:** Abstract interface for LLM providers with streaming + tool use
**When to use:** All LLM interactions go through this layer

```python
# app/llm/base.py
from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass

@dataclass
class StreamChunk:
    """Normalized streaming chunk from any LLM provider."""
    type: str  # "text_delta" | "tool_use_start" | "tool_use_input" | "tool_use_end" | "done" | "error"
    text: str | None = None
    tool_name: str | None = None
    tool_id: str | None = None
    tool_input: dict | None = None

@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int

class LLMProvider(ABC):
    @abstractmethod
    async def stream_message(
        self,
        messages: list[dict],
        system: str,
        tools: list[dict],
        max_tokens: int = 4096,
    ) -> AsyncIterator[StreamChunk]:
        """Stream a message with tool definitions. Yields normalized chunks."""
        ...

    @abstractmethod
    async def get_usage(self) -> TokenUsage:
        """Return token usage from the last call."""
        ...
```

### Pattern 2: Anthropic Streaming with Tool Use

**What:** Anthropic SDK streaming that handles both text and tool_use content blocks
**When to use:** When `CHAT_LLM_PROVIDER=anthropic`

```python
# app/llm/anthropic_provider.py
import anthropic
from app.llm.base import LLMProvider, StreamChunk, TokenUsage

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self._usage: TokenUsage | None = None

    async def stream_message(self, messages, system, tools, max_tokens=4096):
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            tools=tools,
        ) as stream:
            async for event in stream:
                if event.type == "text":
                    yield StreamChunk(type="text_delta", text=event.text)
                elif event.type == "content_block_start":
                    if hasattr(event.content_block, "name"):
                        yield StreamChunk(
                            type="tool_use_start",
                            tool_name=event.content_block.name,
                            tool_id=event.content_block.id,
                        )
                elif event.type == "input_json":
                    yield StreamChunk(type="tool_use_input", text=event.partial_json)
                elif event.type == "content_block_stop":
                    if hasattr(event.content_block, "input"):
                        yield StreamChunk(
                            type="tool_use_end",
                            tool_id=event.content_block.id,
                            tool_input=event.content_block.input,
                        )

            final = await stream.get_final_message()
            self._usage = TokenUsage(
                input_tokens=final.usage.input_tokens,
                output_tokens=final.usage.output_tokens,
            )
            yield StreamChunk(type="done")
```

### Pattern 3: FastAPI Native SSE Endpoint

**What:** POST endpoint that returns SSE stream using FastAPI's built-in `EventSourceResponse`
**When to use:** Chat message send endpoint

```python
# app/api/v1/chat.py
from collections.abc import AsyncIterable
from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent
from app.schemas.chat import SendMessageRequest
from app.api.deps import get_current_user, get_db, rate_limiter

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/send", response_class=EventSourceResponse)
async def send_message(
    request: SendMessageRequest,
    user=Depends(get_current_user),
    db=Depends(get_db),
    _=Depends(rate_limiter),
) -> AsyncIterable[ServerSentEvent]:
    engine = ChatEngine(db=db, user=user)
    async for chunk in engine.process_message(request):
        yield ServerSentEvent(
            data=chunk.model_dump_json(),
            event=chunk.type,
        )
```

### Pattern 4: Frontend SSE Consumer with eventsource-parser

**What:** Manual SSE parsing from POST response using eventsource-parser
**When to use:** Frontend `useChat` hook for streaming messages

```typescript
// features/chat/hooks/useChat.ts
import { createParser, type EventSourceMessage } from 'eventsource-parser';

async function streamMessage(conversationId: string, content: string, token: string) {
  const response = await fetch('/api/v1/chat/send', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ conversation_id: conversationId, content }),
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  const parser = createParser({
    onEvent(event: EventSourceMessage) {
      const data = JSON.parse(event.data);
      switch (event.event) {
        case 'text_delta':
          // Append text to current message
          break;
        case 'tool_start':
          // Show tool status card
          break;
        case 'tool_result':
          // Update tool card with result
          break;
        case 'done':
          // Finalize message
          break;
        case 'error':
          // Show error state
          break;
      }
    },
  });

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    parser.feed(decoder.decode(value, { stream: true }));
  }
}
```

### Pattern 5: Tool-Use Loop with Confirmation

**What:** Chat engine orchestrates multi-turn tool use, pausing for write action confirmation
**When to use:** Core chat processing logic

```python
# app/services/chat_engine.py (simplified)
class ChatEngine:
    async def process_message(self, request):
        messages = await self._load_conversation_history(request.conversation_id)
        messages.append({"role": "user", "content": request.content})
        system = await self._build_system_prompt(request.bot_type)
        tools = self.tool_registry.get_tools(request.bot_type, user_role=self.user.role)

        while True:
            async for chunk in self.llm.stream_message(messages, system, tools):
                if chunk.type == "tool_use_end":
                    tool_def = self.tool_registry.get(chunk.tool_name)
                    if tool_def.requires_confirmation:
                        # Yield confirmation request to frontend, pause
                        yield SSEEvent(type="confirmation_required", data={...})
                        return  # Frontend will re-POST with confirmation
                    else:
                        result = await self.tool_executor.execute(chunk.tool_name, chunk.tool_input)
                        yield SSEEvent(type="tool_result", data=result)
                        messages.append({"role": "assistant", "content": [tool_use_block]})
                        messages.append({"role": "user", "content": [tool_result_block]})
                        continue  # Re-enter LLM loop with tool result
                else:
                    yield SSEEvent.from_chunk(chunk)
            break  # No more tool calls, done
```

### Pattern 6: MCP Server with FastMCP

**What:** Standalone MCP server exposing hotel read-only tools
**When to use:** MCP server container

```python
# services/mcp-server/app/server.py
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("hotelbook")

ROOM_SERVICE = "http://room:8000"
BOOKING_SERVICE = "http://booking:8000"

@mcp.tool()
async def search_rooms(check_in: str, check_out: str, guests: int) -> str:
    """Search available hotel rooms for given dates and guest count."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{ROOM_SERVICE}/api/v1/search/availability",
            params={"check_in": check_in, "check_out": check_out, "guests": guests},
        )
        return resp.text

@mcp.tool()
async def get_occupancy_report(date_from: str, date_to: str) -> str:
    """Get hotel occupancy report for a date range."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BOOKING_SERVICE}/api/v1/reports/occupancy",
            params={"date_from": date_from, "date_to": date_to},
        )
        return resp.text
```

### Anti-Patterns to Avoid

- **Coupling LLM SDK types to API layer:** Never expose Anthropic/OpenAI SDK types in SSE events or schemas. Always normalize through the `StreamChunk` / SSE event layer.
- **Blocking on tool execution during stream:** Tool execution should be async, and intermediate status updates should be streamed while waiting.
- **Storing raw LLM responses in DB:** Store normalized message content and tool call data, not provider-specific response objects.
- **Shared mutable state for conversations:** Each request should load conversation history from DB, not from in-memory cache. Conversations are per-user and must be isolated.
- **Using browser EventSource API:** The `EventSource` API only supports GET requests. Chat requires POST to send message content. Use `fetch()` with manual SSE parsing via `eventsource-parser`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSE streaming | Custom chunked response formatting | `fastapi.sse.EventSourceResponse` + `ServerSentEvent` | Handles keep-alive pings, cache-control headers, nginx buffering headers automatically |
| SSE parsing (frontend) | Manual text splitting on `data:` lines | `eventsource-parser` | Handles edge cases: multi-line data, comments, retry fields, partial chunks |
| Markdown rendering | Custom regex-based parsing | `react-markdown` + `remark-gfm` | Markdown is deceptively complex; handles code blocks, nested lists, links, XSS sanitization |
| LLM streaming | Custom HTTP chunk reading | Anthropic/OpenAI SDK `.stream()` methods | SDKs handle reconnection, accumulation, event normalization, error handling |
| MCP server | Custom JSON-RPC implementation | `mcp` SDK with `FastMCP` | Handles protocol negotiation, capability advertisement, transport management |
| Rate limiting | Custom middleware from scratch | Sliding window counter in DB or Redis | In-memory counters break with multiple workers; use DB-backed per-user counter |
| JWT verification | Custom token parsing | `PyJWT` with public key (project pattern) | Claims-based auth already established; chat service just verifies, never signs |

**Key insight:** This phase integrates multiple complex protocols (LLM APIs, SSE, MCP, tool use). Each has well-tested SDK/library support. Hand-rolling any of them risks subtle protocol compliance bugs that are hard to debug in production.

## Common Pitfalls

### Pitfall 1: SSE Connection Dropped by Reverse Proxy
**What goes wrong:** Nginx or cloud load balancers close idle SSE connections after 60s, killing long-running LLM responses.
**Why it happens:** Default proxy timeouts are too short for LLM inference that can take 30-60s with tool use.
**How to avoid:** FastAPI's native SSE sends keep-alive pings every 15s automatically. Nginx config needs `proxy_buffering off;` and `proxy_read_timeout 300;` for the chat endpoint. The `X-Accel-Buffering: no` header is set automatically by FastAPI SSE.
**Warning signs:** Responses cut off mid-stream; works in dev but fails behind nginx.

### Pitfall 2: Tool Use Loop Becomes Infinite
**What goes wrong:** LLM keeps calling tools in a loop without converging to a text response.
**Why it happens:** Ambiguous system prompt or tool definitions cause the model to endlessly re-query.
**How to avoid:** Cap tool call iterations (e.g., max 5 per message). After the cap, inject a message like "Please summarize what you've found so far." Also make tool descriptions precise about when to use each tool.
**Warning signs:** Chat responses never complete; high token usage per message.

### Pitfall 3: Confirmation Flow State Management
**What goes wrong:** User confirms a write action but the context (tool call arguments) is lost between the confirmation POST and execution.
**Why it happens:** SSE is stateless; the confirmation UI and the execution are separate HTTP requests.
**How to avoid:** When a tool requires confirmation, persist the pending tool call (tool name, arguments, tool_id) in the message record in chat_db. The confirmation POST references the message ID, and the server retrieves the pending tool call from DB to execute.
**Warning signs:** Confirmation succeeds but wrong action is performed; actions silently fail.

### Pitfall 4: Anthropic vs OpenAI Tool Schema Differences
**What goes wrong:** Tools work with one provider but fail with the other.
**Why it happens:** Anthropic uses `input_schema` with JSON Schema; OpenAI uses `parameters` in a function-calling wrapper. Event shapes and tool result formats differ.
**How to avoid:** Define tools in a provider-agnostic format (e.g., JSON Schema). Each provider adapter translates to its native format. The `LLMProvider` abstraction handles this in `stream_message()`.
**Warning signs:** Tool calls work with Claude but fail with GPT-4, or vice versa.

### Pitfall 5: Streaming + Database Writes Race Condition
**What goes wrong:** Message is saved to DB before streaming completes, or not saved at all on error.
**Why it happens:** SSE streams asynchronously; DB writes need to happen after the full response is accumulated.
**How to avoid:** Buffer the complete assistant response during streaming. After the stream ends (or on error), save the complete message to DB with token usage. Use a `try/finally` block around the streaming generator.
**Warning signs:** Conversation history is incomplete; messages appear then vanish on page refresh.

### Pitfall 6: Frontend Memory Leak from Unclosed SSE Streams
**What goes wrong:** Browser memory grows unbounded after many messages.
**Why it happens:** `ReadableStream` reader is not properly closed when user navigates away or starts a new message.
**How to avoid:** Use `AbortController` with `fetch()`. Abort the controller on component unmount and when starting a new message. Always call `reader.cancel()` in cleanup.
**Warning signs:** Tab gets slow after extended chat sessions; DevTools shows growing number of connections.

### Pitfall 7: Dynamic System Prompt Staleness
**What goes wrong:** Bot gives incorrect information about room types, rates, or policies.
**Why it happens:** System prompt is built once and cached, but hotel data changes (new rooms, rate updates).
**How to avoid:** Build the system prompt per-conversation-start (not per-message -- too expensive). Include a timestamp. For rate-sensitive queries, the search tool returns live data anyway. Rebuild prompt if conversation is resumed after >1 hour.
**Warning signs:** Bot quotes outdated prices; new room types not mentioned.

## Code Examples

### Database Models (chat_db)

```python
# app/models/conversation.py
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)  # From JWT claims
    bot_type: Mapped[str] = mapped_column(String(10))  # "guest" or "staff"
    title: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", order_by="Message.created_at")
```

```python
# app/models/message.py
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # "user", "assistant", "tool_result"
    content: Mapped[str | None] = mapped_column(Text)
    tool_calls: Mapped[dict | None] = mapped_column(JSONB)  # Normalized tool call data
    tool_results: Mapped[dict | None] = mapped_column(JSONB)  # Tool execution results
    pending_confirmation: Mapped[dict | None] = mapped_column(JSONB)  # Pending write action
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric(10, 6))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
```

### Rate Limiter Dependency

```python
# app/api/deps.py (rate limiting portion)
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func
from app.models.message import Message

RATE_LIMIT_MESSAGES = 20
RATE_LIMIT_WINDOW = timedelta(minutes=1)

async def rate_limiter(user=Depends(get_current_user), db=Depends(get_db)):
    """Enforce per-user rate limit on chat messages."""
    since = datetime.utcnow() - RATE_LIMIT_WINDOW
    count = await db.scalar(
        select(func.count(Message.id))
        .where(Message.conversation_id.in_(
            select(Conversation.id).where(Conversation.user_id == user.id)
        ))
        .where(Message.role == "user")
        .where(Message.created_at >= since)
    )
    if count and count >= RATE_LIMIT_MESSAGES:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before sending more messages.",
        )
```

### SSE Event Types (shared schema)

```python
# app/schemas/sse_events.py
from pydantic import BaseModel

class TextDeltaEvent(BaseModel):
    type: str = "text_delta"
    text: str

class ToolStartEvent(BaseModel):
    type: str = "tool_start"
    tool_name: str
    tool_id: str
    description: str  # Human-readable: "Searching rooms for Mar 25-28..."

class ToolResultEvent(BaseModel):
    type: str = "tool_result"
    tool_id: str
    success: bool
    data: dict  # Tool-specific result data

class ConfirmationRequiredEvent(BaseModel):
    type: str = "confirmation_required"
    message_id: str  # Reference for confirmation POST
    action: str  # "book", "cancel", "modify", "check_in", "check_out"
    description: str  # Human-readable action description
    details: dict  # Action-specific details for UI rendering

class DoneEvent(BaseModel):
    type: str = "done"
    message_id: str
    input_tokens: int
    output_tokens: int

class ErrorEvent(BaseModel):
    type: str = "error"
    message: str
    retryable: bool = False
```

### Docker Compose Additions

```yaml
# New entries for docker-compose.yml
  chat_db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: chat
      POSTGRES_USER: chat_user
      POSTGRES_PASSWORD: chat_pass
    volumes:
      - chat_db_data:/var/lib/postgresql/data
    ports:
      - "5436:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chat_user -d chat"]
      interval: 5s
      timeout: 3s
      retries: 5

  chat:
    build:
      context: .
      dockerfile: services/chat/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://chat_user:chat_pass@chat_db:5432/chat
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key
      RABBITMQ_URL: amqp://hotel:hotel_pass@rabbitmq:5672/
      CHAT_LLM_PROVIDER: anthropic
      CHAT_LLM_MODEL: claude-sonnet-4-6-20250514
      CHAT_LLM_API_KEY: ${ANTHROPIC_API_KEY:-sk-placeholder}
      AUTH_SERVICE_URL: http://auth:8000
      ROOM_SERVICE_URL: http://room:8000
      BOOKING_SERVICE_URL: http://booking:8000
    depends_on:
      chat_db:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    ports:
      - "8010:8000"
    volumes:
      - ./keys:/run/secrets:ro
      - ./shared:/app/shared:ro

  mcp-server:
    build:
      context: .
      dockerfile: services/mcp-server/Dockerfile
    environment:
      ROOM_SERVICE_URL: http://room:8000
      BOOKING_SERVICE_URL: http://booking:8000
      AUTH_SERVICE_URL: http://auth:8000
    depends_on:
      - room
      - booking
    ports:
      - "8011:8000"

# volumes section:
  chat_db_data:
```

### Gateway SERVICE_MAP Update

```python
# Add to services/gateway/app/api/proxy.py SERVICE_MAP
"/api/v1/chat": settings.CHAT_SERVICE_URL,
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| sse-starlette third-party lib | FastAPI native `fastapi.sse` | FastAPI 0.135.0 (Jan 2025) | No external SSE dependency needed |
| OpenAI Chat Completions for tool calling | OpenAI Responses API | OpenAI SDK 2.0 (2025) | New API design, but Chat Completions still supported and simpler for compatibility |
| Custom JSON-RPC for tool servers | MCP (Model Context Protocol) | 2024-2025 | Standard protocol; interoperable with Claude Desktop, Cursor, etc. |
| REST-only LLM integrations | Streaming + tool use as standard | 2024-2025 | Users expect real-time token streaming; tool use enables agentic workflows |

**Deprecated/outdated:**
- `sse-starlette`: Still works, but unnecessary with FastAPI 0.135+
- OpenAI `functions` parameter: Replaced by `tools` parameter in Chat Completions API
- MCP stdio-only transport: SSE and Streamable HTTP transports now available

## Open Questions

1. **OpenAI Responses API vs Chat Completions**
   - What we know: OpenAI SDK 2.x introduced the Responses API which is more streaming-native. Chat Completions still works and is more widely compatible.
   - What's unclear: Whether to use Responses API or Chat Completions for the OpenAI provider.
   - Recommendation: Use Chat Completions API for the OpenAI provider -- it's more stable, better documented, and compatible with OpenAI-compatible providers (local models, Azure, etc.).

2. **MCP Transport Selection**
   - What we know: MCP supports stdio, SSE, and Streamable HTTP transports. The server will run as a Docker container.
   - What's unclear: Whether to use SSE or Streamable HTTP transport for the containerized MCP server.
   - Recommendation: Use Streamable HTTP transport (the latest MCP standard). It runs as a regular HTTP server, works well in Docker, and is the direction MCP is moving. Fall back to SSE transport if Streamable HTTP has issues in mcp 1.26.

3. **Token Cost Estimation Accuracy**
   - What we know: Both Anthropic and OpenAI return actual token counts in responses. Cost per token varies by model.
   - What's unclear: How to keep cost-per-token mapping current as pricing changes.
   - Recommendation: Store a simple JSON config mapping model names to input/output costs. Update manually when pricing changes. Good enough for analytics.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework (backend) | pytest + pytest-asyncio (project standard) |
| Framework (frontend) | vitest 4.1.0 + @testing-library/react (project standard) |
| Config file (backend) | `services/chat/pytest.ini` (Wave 0) |
| Config file (frontend) | `frontend/vitest.config.ts` / `frontend-staff/vitest.config.ts` (existing) |
| Quick run command (backend) | `cd services/chat && python -m pytest tests/ -x --timeout=30` |
| Quick run command (frontend) | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `docker compose exec chat python -m pytest && cd frontend && npx vitest run && cd ../frontend-staff && npx vitest run` |

### Phase Requirements -> Test Map

Since no specific requirement IDs were provided, tests map to the key capabilities defined in CONTEXT.md:

| Capability | Behavior | Test Type | Automated Command | File Exists? |
|-----------|----------|-----------|-------------------|-------------|
| LLM abstraction | Provider selection + streaming | unit | `pytest tests/test_llm_providers.py -x` | Wave 0 |
| Tool registry | Guest/staff tool sets, RBAC filtering | unit | `pytest tests/test_tool_registry.py -x` | Wave 0 |
| Tool executor | Internal API calls for each tool | unit | `pytest tests/test_tool_executor.py -x` | Wave 0 |
| Chat engine | Message processing, tool loop, confirmation | integration | `pytest tests/test_chat_engine.py -x` | Wave 0 |
| SSE endpoint | Streaming response format | integration | `pytest tests/test_chat_api.py -x` | Wave 0 |
| Rate limiter | Per-user message rate enforcement | unit | `pytest tests/test_rate_limiter.py -x` | Wave 0 |
| Prompt builder | Dynamic system prompt from hotel data | unit | `pytest tests/test_prompt_builder.py -x` | Wave 0 |
| Conversation CRUD | Create, list, rename, delete conversations | integration | `pytest tests/test_conversations.py -x` | Wave 0 |
| Chat UI (guest) | Message bubbles, input, sidebar rendering | unit | `cd frontend && npx vitest run src/features/chat` | Wave 0 |
| Chat UI (staff) | Staff chat with dark theme | unit | `cd frontend-staff && npx vitest run src/features/chat` | Wave 0 |

### Sampling Rate
- **Per task commit:** Quick run command for affected service/frontend
- **Per wave merge:** Full suite across chat service + both frontends
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `services/chat/pytest.ini` -- pytest configuration
- [ ] `services/chat/conftest.py` -- async DB fixtures, test client
- [ ] `services/chat/tests/` -- test directory structure
- [ ] Framework install: `pip install pytest pytest-asyncio httpx` in chat service dev deps
- [ ] Mock LLM provider for tests (returns canned streaming responses)
- [ ] Frontend test stubs for chat feature components

## Sources

### Primary (HIGH confidence)
- [FastAPI SSE Documentation](https://fastapi.tiangolo.com/tutorial/server-sent-events/) - Native SSE support since 0.135.0, code examples verified
- [Anthropic SDK GitHub](https://github.com/anthropics/anthropic-sdk-python) - v0.86.0, streaming helpers with `.stream()` and event types
- [MCP Build Server Guide](https://modelcontextprotocol.io/docs/develop/build-server) - FastMCP decorator pattern, transport options
- PyPI verified versions: anthropic 0.86.0, openai 2.29.0, mcp 1.26.0, sse-starlette 3.3.3
- npm verified versions: react-markdown 10.1.0, remark-gfm 4.0.1, eventsource-parser 3.0.6
- Project codebase: existing microservice patterns, Docker Compose, gateway proxy, JWT auth

### Secondary (MEDIUM confidence)
- [Anthropic Streaming Messages API](https://docs.anthropic.com/en/api/messages-streaming) - SSE event types and tool_use streaming format
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) - Tool schema format and streaming behavior
- [Anthropic SDK helpers.md](https://github.com/anthropics/anthropic-sdk-python/blob/main/helpers.md) - MessageStream events (text, input_json, content_block_stop)

### Tertiary (LOW confidence)
- OpenAI Responses API vs Chat Completions comparison -- based on web search, needs validation against official migration guide

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all packages verified on PyPI/npm, versions confirmed, project patterns established
- Architecture: HIGH - follows existing microservice patterns exactly; LLM provider abstraction is a well-known pattern
- Pitfalls: HIGH - SSE proxy issues, tool use loops, and confirmation state are well-documented challenges
- MCP server: MEDIUM - FastMCP pattern is documented but transport selection for Docker needs validation
- LLM streaming with tool use: MEDIUM - SDK streaming APIs verified, but multi-turn tool loop orchestration is custom logic

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (30 days -- LLM SDKs move fast but core patterns stable)
