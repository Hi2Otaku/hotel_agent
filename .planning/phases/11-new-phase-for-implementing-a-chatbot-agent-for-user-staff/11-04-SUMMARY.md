---
phase: 11-chatbot-agent
plan: 04
subsystem: ui
tags: [react, zustand, sse, eventsource-parser, react-markdown, remark-gfm, chat-ui, streaming]

requires:
  - phase: 11-01
    provides: Chat service with SSE streaming endpoints
  - phase: 11-02
    provides: Chat engine core with tool orchestration and confirmation flow
provides:
  - Guest chat page at /chat with full ChatGPT-style layout
  - SSE streaming hook with eventsource-parser for real-time bot responses
  - Zustand chat store for message, tool status, and confirmation state
  - React Query hooks for conversation CRUD (list, rename, delete)
  - Markdown rendering in bot messages via react-markdown + remark-gfm
  - Inline tool status cards, room cards with Book button, confirmation cards
  - Mobile-responsive sidebar via Sheet component
affects: [11-05-staff-chat-ui, frontend-testing, deployment]

tech-stack:
  added: [react-markdown, remark-gfm, eventsource-parser, shadcn-scroll-area]
  patterns: [SSE streaming via native fetch + eventsource-parser, Zustand store for chat state, lazy-loaded route with own layout (no Footer)]

key-files:
  created:
    - frontend/src/features/chat/types/chat.ts
    - frontend/src/features/chat/api/chatApi.ts
    - frontend/src/features/chat/stores/chatStore.ts
    - frontend/src/features/chat/hooks/useChat.ts
    - frontend/src/features/chat/hooks/useConversations.ts
    - frontend/src/features/chat/hooks/useAutoScroll.ts
    - frontend/src/features/chat/ChatPage.tsx
    - frontend/src/features/chat/ChatLayout.tsx
    - frontend/src/features/chat/components/ConversationSidebar.tsx
    - frontend/src/features/chat/components/ConversationList.tsx
    - frontend/src/features/chat/components/ChatArea.tsx
    - frontend/src/features/chat/components/MessageList.tsx
    - frontend/src/features/chat/components/MessageBubble.tsx
    - frontend/src/features/chat/components/ToolStatusCard.tsx
    - frontend/src/features/chat/components/RoomCard.tsx
    - frontend/src/features/chat/components/ConfirmationCard.tsx
    - frontend/src/features/chat/components/WelcomeMessage.tsx
    - frontend/src/features/chat/components/StarterChips.tsx
    - frontend/src/features/chat/components/MessageInput.tsx
    - frontend/src/features/chat/components/TypingIndicator.tsx
    - frontend/src/features/chat/components/ScrollToBottom.tsx
    - frontend/src/features/chat/__tests__/ChatPage.test.tsx
    - frontend/src/features/chat/__tests__/MessageBubble.test.tsx
  modified:
    - frontend/src/App.tsx
    - frontend/src/components/layout/Navbar.tsx
    - frontend/package.json

key-decisions:
  - "ChatPage uses own layout (Navbar + no Footer) via separate Route in App.tsx"
  - "SSE streaming uses native fetch + eventsource-parser (not axios) for ReadableStream support"
  - "Chat feature organized in features/chat/ directory with types, api, stores, hooks, components"
  - "Lazy-loaded ChatPage for code splitting (188KB separate chunk)"

patterns-established:
  - "Feature directory pattern: features/chat/ with types/, api/, stores/, hooks/, components/, __tests__/"
  - "SSE client pattern: native fetch POST -> ReadableStream reader -> eventsource-parser -> Zustand store updates"
  - "Custom layout routes: separate Route in App.tsx for pages needing different layout (no Footer)"

requirements-completed: [CHAT-UI-GUEST]

duration: 5min
completed: 2026-03-22
---

# Phase 11 Plan 04: Guest Chat UI Summary

**ChatGPT-style guest chat interface at /chat with SSE streaming, markdown rendering, tool status cards, room cards, confirmation flow, conversation sidebar, and mobile-responsive design**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-22T17:40:20Z
- **Completed:** 2026-03-22T17:45:42Z
- **Tasks:** 2
- **Files modified:** 28

## Accomplishments
- Full guest chat interface at /chat with welcome message, starter chips, and ChatGPT-style layout
- SSE streaming data layer with eventsource-parser processing text_delta, tool_start, tool_result, confirmation_required, done, and error events
- 15 React components covering message bubbles (markdown + timestamps), tool status cards, room cards with Book button, confirmation cards, typing indicator, scroll-to-bottom, and auto-growing message input
- Conversation sidebar with CRUD (list, rename with inline edit, delete with confirmation dialog) via React Query
- Mobile-responsive design with Sheet-based sidebar drawer
- Navbar updated with Chat link, App.tsx with protected /chat route (lazy-loaded, code-split)

## Task Commits

Each task was committed atomically:

1. **Task 1: Types, API layer, stores, hooks (data layer)** - `90b2509` (feat)
2. **Task 2: Chat UI components, routing, and Navbar integration** - `10b3361` (feat)

## Files Created/Modified
- `frontend/src/features/chat/types/chat.ts` - TypeScript types for Conversation, ChatMessage, SSE events, ToolStatus, RoomCard
- `frontend/src/features/chat/api/chatApi.ts` - API layer with axios CRUD + native fetch SSE streaming
- `frontend/src/features/chat/stores/chatStore.ts` - Zustand store for chat state (messages, streaming, tools, confirmation)
- `frontend/src/features/chat/hooks/useChat.ts` - Main hook with SSE stream processing via eventsource-parser
- `frontend/src/features/chat/hooks/useConversations.ts` - React Query hooks for conversation CRUD
- `frontend/src/features/chat/hooks/useAutoScroll.ts` - Auto-scroll with bottom detection
- `frontend/src/features/chat/ChatPage.tsx` - Full-height route component
- `frontend/src/features/chat/ChatLayout.tsx` - Flex row with sidebar + chat area
- `frontend/src/features/chat/components/ConversationSidebar.tsx` - 280px sidebar with new chat + conversation list
- `frontend/src/features/chat/components/ConversationList.tsx` - Conversation items with rename/delete
- `frontend/src/features/chat/components/ChatArea.tsx` - Welcome or messages + input
- `frontend/src/features/chat/components/MessageList.tsx` - Message list with role=log, aria-live
- `frontend/src/features/chat/components/MessageBubble.tsx` - User (teal) and bot (light) bubbles with markdown
- `frontend/src/features/chat/components/ToolStatusCard.tsx` - Green card with spinner/check/error icons
- `frontend/src/features/chat/components/RoomCard.tsx` - Room photo, price, amenities, Book button
- `frontend/src/features/chat/components/ConfirmationCard.tsx` - Amber card with confirm/cancel
- `frontend/src/features/chat/components/WelcomeMessage.tsx` - Bot avatar + greeting + starter chips
- `frontend/src/features/chat/components/StarterChips.tsx` - 4 guest starter chip buttons
- `frontend/src/features/chat/components/MessageInput.tsx` - Auto-grow textarea with Enter-to-send
- `frontend/src/features/chat/components/TypingIndicator.tsx` - Bouncing dots with reduced-motion support
- `frontend/src/features/chat/components/ScrollToBottom.tsx` - Floating scroll button
- `frontend/src/App.tsx` - Added /chat route with ProtectedRoute, lazy-loaded ChatPage
- `frontend/src/components/layout/Navbar.tsx` - Added Chat link with MessageSquare icon

## Decisions Made
- ChatPage uses own layout wrapper (Navbar + Toaster, no Footer) to maximize chat vertical space
- SSE streaming uses native fetch (not axios) for ReadableStream body access with eventsource-parser
- Chat feature placed in features/chat/ directory following feature-based organization
- ChatPage lazy-loaded with React.lazy for code splitting (produces 188KB separate chunk)
- App.tsx restructured with nested Routes: /chat gets custom layout, /* gets PageLayout with Footer

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] shadcn CLI wrote scroll-area to wrong directory**
- **Found during:** Task 1
- **Issue:** `npx shadcn@latest add scroll-area` created file at `frontend/@/components/ui/` instead of `frontend/src/components/ui/`
- **Fix:** Manually copied file to correct location and removed erroneous directory
- **Files modified:** frontend/src/components/ui/scroll-area.tsx
- **Verification:** TypeScript compilation passes
- **Committed in:** 90b2509 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Minor path fix for shadcn CLI. No scope creep.

## Issues Encountered
None beyond the shadcn path issue documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Guest chat UI complete and ready for integration testing with chat backend
- Staff chat UI (11-05) can reuse shared types, hooks, and components from this plan
- Build passes, tests pass (5/5), code-split chunk properly isolated

## Self-Check: PASSED

All 21 created files verified present. Both task commits (90b2509, 10b3361) verified in git log.

---
*Phase: 11-chatbot-agent, Plan: 04*
*Completed: 2026-03-22*
