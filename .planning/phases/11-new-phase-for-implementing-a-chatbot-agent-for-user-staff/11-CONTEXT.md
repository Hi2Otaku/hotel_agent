# Phase 11: Chatbot Agent for User & Staff - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement an AI-powered chatbot for both guest and staff users. Guests get a conversational assistant for searching rooms, booking, managing reservations, and hotel FAQs. Staff get an operations assistant for check-in/out, room status, reports, and guest lookup. Each bot has its own personality, tool set, and system prompt. The backend is a new chat microservice with pluggable LLM providers, SSE streaming, and a separate MCP server for external AI clients.

</domain>

<decisions>
## Implementation Decisions

### AI/LLM Backend
- Pluggable LLM provider behind an abstract interface — both Anthropic SDK (Claude) and OpenAI SDK implementations from day one
- Default model: Claude Sonnet 4.6, configurable via `CHAT_LLM_MODEL` env var
- Provider and API key configured via environment variables (`CHAT_LLM_PROVIDER`, `CHAT_LLM_API_KEY`)
- New chat microservice on port 8010 with its own PostgreSQL database (`chat_db`) and Docker container
- SSE (Server-Sent Events) for streaming responses — user messages sent via regular POST
- Dynamic system prompt built at runtime from actual hotel data (room types, rates, policies from DB)
- Tool-use (function calling) enabled — bot calls internal APIs as tools
- Write actions (create booking, cancel, modify) require user confirmation before executing
- Read-only actions (search, status check) execute immediately
- Retry once with backoff on LLM API failure, then show graceful fallback message
- Per-user rate limiting on chat messages (e.g., 20 messages/minute)
- Conversation history persisted in chat_db — users can return to past conversations
- Soft limit ~50 messages per conversation before suggesting a new one
- Token usage and estimated cost tracked per message for analytics
- Publish chat events to RabbitMQ (`chat.events` exchange) for integration with other services
- Separate MCP server process exposing read-only tools (search, status, reports) for external AI clients

### Chatbot Capabilities — Guest
- Search rooms by dates, guest count, and filters
- Create bookings via conversational multi-turn flow (dates → guest count → room → confirm)
- Manage existing bookings (check status, cancel, modify)
- Answer hotel FAQs from dynamic system prompt (policies, amenities, check-in times, etc.)
- Chat-initiated actions trigger the same side effects as manual flow (email confirmation, events)
- Rich inline room cards in responses (photo thumbnail, price, amenities, "Book this" button)
- Starter prompt chips on new conversation: Search rooms, Check my booking, Hotel info, etc.
- Auto-detect user language and respond accordingly
- Authentication required — chat only available to logged-in guests

### Chatbot Capabilities — Staff
- All guest capabilities plus:
- Check-in and check-out guests by name or confirmation number
- Update room status (cleaning, maintenance, available)
- View reports and metrics (occupancy, revenue, booking trends)
- Guest profile and booking history lookup
- Operations-focused starter chips: Today's check-ins, Room status, Find guest, Occupancy report
- Respect RBAC — tools available match the staff member's role (admin/manager/front_desk)

### Conversation UX
- Chat accessible via nav link in Navbar (guest) / Sidebar nav item (staff)
- Dedicated `/chat` page with its own layout — no footer, full-height
- ChatGPT-style layout: conversation sidebar on left + active chat area on right
- Mobile: conversation sidebar as Sheet drawer (consistent with existing mobile patterns)
- Message bubbles with rendered markdown (bold, lists, code blocks, links)
- Timestamps shown on hover/tap (not always visible)
- Welcome message + starter prompt chips when starting a new conversation
- Animated dots + status text while bot processes ("Thinking...", "Searching rooms...")
- Inline status cards for tool actions ("Searching rooms for Mar 25-28..." → results)
- Conversations: delete + rename via right-click/swipe
- LLM-generated conversation titles after first exchange

### Staff vs Guest Split
- Separate bots with distinct names and personalities (e.g., "HotelBook Assistant" for guests, "HB Ops" for staff)
- Different system prompts, tool sets, and tone
- No cross-access — staff and guest chats completely isolated
- Chat components copied into each frontend with styling adjustments (light theme guest, dark theme staff)
- No shared component package between frontends

### Claude's Discretion
- Exact message bubble styling and spacing
- Loading skeleton design for chat page
- Scroll behavior and auto-scroll logic
- Error state UI for failed messages
- Exact rate limit numbers
- MCP server port and transport details
- RabbitMQ routing key naming for chat events

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs — requirements are fully captured in decisions above.

### Architecture patterns
- `services/gateway/app/api/proxy.py` — Gateway proxy pattern for routing to services
- `services/room/app/services/event_consumer.py` — RabbitMQ consumer pattern
- `services/booking/app/services/event_publisher.py` — RabbitMQ publisher pattern
- `shared/shared/messaging.py` — Shared messaging utilities
- `shared/shared/database.py` — Database engine and session factory pattern

### Auth patterns
- `services/auth/app/core/security.py` — RS256 JWT signing/verification
- `services/auth/app/api/deps.py` — `get_current_user()` and `require_role()` dependency injection

### Frontend layout patterns
- `frontend/src/components/layout/PageLayout.tsx` — Guest page layout (Navbar + Footer)
- `frontend/src/components/layout/Navbar.tsx` — Guest navbar with nav links and auth
- `frontend-staff/src/components/layout/AppLayout.tsx` — Staff layout (Sidebar + TopBar + Outlet)
- `frontend-staff/src/components/layout/Sidebar.tsx` — Staff sidebar nav with collapse

### Frontend infrastructure
- `frontend/src/api/client.ts` — Axios client with JWT interceptor
- `frontend/src/stores/authStore.ts` — Guest auth Zustand store
- `frontend-staff/src/stores/authStore.ts` — Staff auth Zustand store

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- shadcn/ui components (Button, Card, Dialog, Sheet, Input, Avatar, Badge, Skeleton) — available in both frontends
- Zustand stores pattern — use for chat state (messages, conversations, UI state)
- React Query — use for conversation list fetching, message history
- Axios client with JWT interceptor — reuse for chat API calls
- Sheet component — reuse for mobile conversation sidebar
- Sonner (toast) — reuse for chat error notifications

### Established Patterns
- Microservice with FastAPI, async SQLAlchemy, Alembic migrations
- Database-per-service with PostgreSQL in Docker Compose
- RabbitMQ topic exchange for event publishing/consuming
- Gateway BFF for cross-service orchestration
- RS256 JWT with role-based access control
- React.lazy for code splitting on page components
- Feature-based component folder structure

### Integration Points
- Gateway `SERVICE_MAP` needs new entry for chat service routing
- Guest Navbar needs "Chat" nav link (after "Pricing", before auth section)
- Staff Sidebar `navItems` array needs "Chat" entry with MessageSquare icon
- Guest App.tsx needs `/chat` route with dedicated ChatLayout (no footer)
- Staff App.tsx needs `/chat` route within the AppLayout
- Docker Compose needs chat_db, chat service, and MCP server containers
- Nginx config needs `/chat-api/` proxy rule for production

</code_context>

<specifics>
## Specific Ideas

- Layout inspired by ChatGPT: conversation sidebar + chat area, full-height below navbar
- Guest bot persona: friendly hotel concierge ("HotelBook Assistant")
- Staff bot persona: professional operations assistant ("HB Ops")
- Tool actions visible in chat as inline status cards that update (not hidden)
- Room search results as rich cards directly in chat with photo, price, and "Book this" action

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-new-phase-for-implementing-a-chatbot-agent-for-user-staff*
*Context gathered: 2026-03-22*
