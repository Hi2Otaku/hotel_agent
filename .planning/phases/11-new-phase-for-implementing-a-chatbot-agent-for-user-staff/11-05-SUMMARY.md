---
phase: 11-chatbot-agent
plan: 05
subsystem: ui
tags: [react, zustand, sse, react-markdown, tailwindcss, dark-theme, chat-ui, staff]

# Dependency graph
requires:
  - phase: 11-chatbot-agent-01
    provides: Chat service Docker infra, DB models, LLM provider abstraction
  - phase: 11-chatbot-agent-02
    provides: Chat engine, SSE streaming endpoint, conversation CRUD, tool registry
provides:
  - Staff chat UI at /chat with dark theme within AppLayout
  - Staff-specific welcome message (HB Ops) and operations starter chips
  - SSE streaming hook with bot_type="staff"
  - Check-in/check-out confirmation card labels
  - Sidebar nav item with MessageSquare icon
affects: [deployment, e2e-tests]

# Tech tracking
tech-stack:
  added: [react-markdown, remark-gfm, eventsource-parser]
  patterns: [SSE streaming with eventsource-parser in staff frontend, dark-theme chat components using CSS variables]

key-files:
  created:
    - frontend-staff/src/features/chat/ChatPage.tsx
    - frontend-staff/src/features/chat/ChatLayout.tsx
    - frontend-staff/src/features/chat/types/chat.ts
    - frontend-staff/src/features/chat/api/chatApi.ts
    - frontend-staff/src/features/chat/stores/chatStore.ts
    - frontend-staff/src/features/chat/hooks/useChat.ts
    - frontend-staff/src/features/chat/hooks/useConversations.ts
    - frontend-staff/src/features/chat/hooks/useAutoScroll.ts
    - frontend-staff/src/features/chat/components/WelcomeMessage.tsx
    - frontend-staff/src/features/chat/components/StarterChips.tsx
    - frontend-staff/src/features/chat/components/MessageBubble.tsx
    - frontend-staff/src/features/chat/components/MessageInput.tsx
    - frontend-staff/src/features/chat/components/MessageList.tsx
    - frontend-staff/src/features/chat/components/ConversationSidebar.tsx
    - frontend-staff/src/features/chat/components/ConversationList.tsx
    - frontend-staff/src/features/chat/components/ChatArea.tsx
    - frontend-staff/src/features/chat/components/ToolStatusCard.tsx
    - frontend-staff/src/features/chat/components/ConfirmationCard.tsx
    - frontend-staff/src/features/chat/components/TypingIndicator.tsx
    - frontend-staff/src/features/chat/components/ScrollToBottom.tsx
    - frontend-staff/src/components/ui/scroll-area.tsx
    - frontend-staff/src/features/chat/__tests__/ChatPage.test.tsx
  modified:
    - frontend-staff/src/App.tsx
    - frontend-staff/src/components/layout/Sidebar.tsx
    - frontend-staff/src/components/layout/AppLayout.tsx
    - frontend-staff/package.json

key-decisions:
  - "Staff chat uses same SSE streaming pattern as guest but with bot_type='staff'"
  - "Dark theme uses semantic CSS variable classes (bg-background, bg-card, text-primary) for consistency"
  - "Bot bubble uses hsl(217.2,32.6%,17.5%) with hsl(217.2,32.6%,29.4%) border matching UI-SPEC"
  - "Check-in/check-out confirmation labels per copywriting contract: Confirm Check-in/Don't Check In"

patterns-established:
  - "Staff chat feature mirrors guest chat structure for consistency and maintainability"
  - "Dark theme chat bubbles use explicit HSL values for staff-specific colors not in CSS variables"

requirements-completed: [CHAT-UI-STAFF]

# Metrics
duration: 6min
completed: 2026-03-23
---

# Phase 11 Plan 05: Staff Chat UI Summary

**Dark-themed staff chat interface with HB Ops welcome, operations starter chips, SSE streaming, check-in/out confirmation cards, and Sidebar integration at /chat**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-22T17:40:28Z
- **Completed:** 2026-03-22T17:46:09Z
- **Tasks:** 2
- **Files modified:** 27

## Accomplishments
- Complete staff chat feature at /chat within AppLayout with dark theme matching existing staff dashboard
- HB Ops welcome message with operations-focused starter chips (Today's check-ins, Room status, Find guest, Occupancy report)
- Full data layer: types, API with staff auth token, Zustand store, SSE streaming hook (bot_type="staff"), React Query conversation hooks
- 14 UI components: ChatPage, ChatLayout, ConversationSidebar, ConversationList, ChatArea, MessageList, MessageBubble, ToolStatusCard, ConfirmationCard, WelcomeMessage, StarterChips, MessageInput, TypingIndicator, ScrollToBottom
- Sidebar nav item with MessageSquare icon, App.tsx lazy-loaded /chat route
- 5 passing tests verifying welcome message, starter chips, input, and button rendering

## Task Commits

Each task was committed atomically:

1. **Task 1: Staff chat data layer (types, API, store, hooks)** - `f82805c` (feat)
2. **Task 2: Staff chat UI components with dark theme, routing, Sidebar integration** - `d01f3df` (feat)

## Files Created/Modified
- `frontend-staff/src/features/chat/types/chat.ts` - TypeScript types for conversations, messages, SSE events
- `frontend-staff/src/features/chat/api/chatApi.ts` - API functions using staff auth token (staff_access_token)
- `frontend-staff/src/features/chat/stores/chatStore.ts` - Zustand store for chat state
- `frontend-staff/src/features/chat/hooks/useChat.ts` - SSE streaming hook with bot_type="staff"
- `frontend-staff/src/features/chat/hooks/useConversations.ts` - React Query hooks for conversation CRUD
- `frontend-staff/src/features/chat/hooks/useAutoScroll.ts` - Auto-scroll hook for message list
- `frontend-staff/src/features/chat/ChatPage.tsx` - Page component with full viewport height
- `frontend-staff/src/features/chat/ChatLayout.tsx` - Flex layout with sidebar + chat area
- `frontend-staff/src/features/chat/components/WelcomeMessage.tsx` - HB Ops welcome with operations copy
- `frontend-staff/src/features/chat/components/StarterChips.tsx` - Staff-specific operations chips
- `frontend-staff/src/features/chat/components/MessageBubble.tsx` - Dark-themed bubbles with react-markdown
- `frontend-staff/src/features/chat/components/MessageInput.tsx` - Staff placeholder, Enter-to-send
- `frontend-staff/src/features/chat/components/MessageList.tsx` - Message container with auto-scroll
- `frontend-staff/src/features/chat/components/ConversationSidebar.tsx` - 280px sidebar with New Chat button
- `frontend-staff/src/features/chat/components/ConversationList.tsx` - Conversation items with rename/delete
- `frontend-staff/src/features/chat/components/ChatArea.tsx` - Orchestrates welcome vs messages view
- `frontend-staff/src/features/chat/components/ToolStatusCard.tsx` - Dark green-900/20 tool status cards
- `frontend-staff/src/features/chat/components/ConfirmationCard.tsx` - Amber-900/20 with check-in/out labels
- `frontend-staff/src/features/chat/components/TypingIndicator.tsx` - Bounce animation with reduced-motion
- `frontend-staff/src/features/chat/components/ScrollToBottom.tsx` - Floating button with card bg
- `frontend-staff/src/components/ui/scroll-area.tsx` - shadcn scroll-area component
- `frontend-staff/src/App.tsx` - Added lazy-loaded /chat route
- `frontend-staff/src/components/layout/Sidebar.tsx` - Added Chat nav item with MessageSquare icon
- `frontend-staff/src/components/layout/AppLayout.tsx` - Added Chat page title mapping
- `frontend-staff/src/features/chat/__tests__/ChatPage.test.tsx` - 5 tests for page rendering

## Decisions Made
- Staff chat uses same SSE streaming pattern as guest but with bot_type="staff" for backend role filtering
- Dark theme uses semantic CSS variable classes (bg-background, bg-card, text-primary) where possible
- Bot bubble uses explicit hsl(217.2,32.6%,17.5%) with border hsl(217.2,32.6%,29.4%) per UI-SPEC
- Check-in/check-out confirmation labels follow copywriting contract exactly

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created scroll-area component manually**
- **Found during:** Task 1
- **Issue:** `npx shadcn@latest add scroll-area` installed to wrong directory due to monorepo config
- **Fix:** Created scroll-area.tsx manually using radix-ui ScrollArea primitives matching shadcn new-york preset
- **Files modified:** frontend-staff/src/components/ui/scroll-area.tsx
- **Verification:** TypeScript compiles, component renders in ConversationSidebar
- **Committed in:** f82805c (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for scroll-area component. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Staff chat UI complete, ready for end-to-end testing with running chat service
- All 14 components follow dark theme palette from UI-SPEC
- SSE streaming ready to connect to gateway /api/v1/chat/send endpoint

## Self-Check: PASSED

All 15 key files verified present. Both task commits (f82805c, d01f3df) confirmed in git log.

---
*Phase: 11-chatbot-agent*
*Completed: 2026-03-23*
