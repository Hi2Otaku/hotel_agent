# Phase 6: Staff Dashboard - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Separate React frontend for hotel staff daily operations: reservation management with search/filter, check-in/check-out workflow with auto room assignment, guest profile views with booking history, and room status board. Staff dashboard has its own visual identity (darker admin feel) and sidebar navigation. Consumes staff-only gateway BFF endpoints.

</domain>

<decisions>
## Implementation Decisions

### Architecture
- Separate React app in `frontend-staff/` directory — independent build from guest frontend
- Same tech stack: Vite + React + Tailwind CSS 4 + shadcn/ui
- Reuse shared patterns from guest frontend (API client structure, Zustand stores, query hooks)
- Staff auth required on all routes — role-based access using JWT claims

### Dashboard Layout
- Darker admin visual feel — distinct from the clean/white guest site
- Sidebar navigation (collapsible on mobile): Reservations, Check-in/out, Room Status, Guest Profiles, (Reports placeholder for Phase 7)
- Home page: today's overview — today's check-ins, check-outs, current occupancy, room status summary
- Same design system (shadcn/ui) but with darker color scheme

### Check-in/out Workflow
- Room assignment: auto-assign from available rooms of booked type, staff can override
- Confirmation: dialog confirmation ("Check in John Doe to Room 305?") before action
- Check-in updates booking status (CONFIRMED → CHECKED_IN) and room status (Available → Occupied)
- Check-out updates booking status (CHECKED_IN → CHECKED_OUT) and room status (Occupied → Cleaning, auto)
- Room status changes happen via existing Room service API + RabbitMQ events

### Reservation List UX
- Card grid display — reservation cards with guest name, dates, room type, status badge, confirmation #
- Quick actions on each card: Check-in button, Check-out button, View detail link, Cancel button
- Search by guest name, date range, status filter, confirmation number
- Pagination with realistic data volumes
- Status-based quick action visibility (check-in only for confirmed, check-out only for checked-in)

### Guest Profile
- View guest contact info, booking history (all bookings for this guest), and special requests
- Read-only aggregation — no edit capability for guest profiles in this phase

### Claude's Discretion
- Exact dark theme color palette (darker background, lighter cards)
- Today's overview layout and metric cards
- Card grid column count and responsive breakpoints
- Auto-assign algorithm (random vs lowest floor first vs sequential)
- Pagination style (numbered pages vs infinite scroll)
- How sidebar collapses on mobile (hamburger vs bottom nav)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 5 established frontend patterns
- `frontend/src/api/client.ts` — Axios client with JWT interceptor (replicate for staff)
- `frontend/src/api/types.ts` — TypeScript interfaces (share or replicate)
- `frontend/src/stores/authStore.ts` — Zustand auth store pattern
- `frontend/src/components/layout/Navbar.tsx` — Responsive nav pattern (adapt for sidebar)
- `frontend/src/hooks/queries/useBookings.ts` — TanStack Query hooks pattern
- `frontend/src/components/booking/StatusBadge.tsx` — Status badge component (reusable)
- `frontend/vite.config.ts` — Vite config with proxy (replicate for staff port)

### Backend APIs (consumed by staff dashboard)
- `services/booking/app/api/v1/bookings.py` — Booking endpoints (list, detail, cancel, modify + check-in/out)
- `services/room/app/api/v1/rooms.py` — Room management endpoints (status board, status transitions)
- `services/room/app/api/v1/room_types.py` — Room type CRUD
- `services/auth/app/api/v1/users.py` — User/guest management (admin only)
- `services/gateway/app/api/proxy.py` — Gateway proxy for all services

### Phase 2 room management
- `services/room/app/services/room.py` — Room service with ROLE_TRANSITIONS and status board
- `services/room/app/models/room.py` — Room model with 7-state status enum

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/api/client.ts`: Axios instance with JWT interceptor — replicate for staff app
- `frontend/src/api/types.ts`: TypeScript interfaces for all backend schemas — can be shared
- `frontend/src/components/booking/StatusBadge.tsx`: Color-coded booking status badge — reuse directly
- `frontend/src/stores/authStore.ts`: Zustand auth store — replicate with role-based logic
- `frontend/vitest.config.ts`: Vitest config — replicate for staff app testing

### Established Patterns
- TanStack Query for API state + Zustand for UI state
- React Hook Form + Zod for form validation
- shadcn/ui components with Tailwind CSS
- API proxy via Vite dev server to gateway

### Integration Points
- Staff dashboard calls gateway (same as guest frontend, different port for dev)
- Check-in/out triggers Booking service state transition + Room service status change
- Room status board endpoint already exists in Room service
- Guest profile needs Booking service list (filter by guest) + Auth service user detail

</code_context>

<specifics>
## Specific Ideas

- Darker admin feel creates clear visual distinction from the guest-facing site
- Today's overview as home page gives staff immediate situational awareness
- Auto-assign rooms speeds up busy check-in times
- Card grid with inline quick actions minimizes clicks for common operations

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-staff-dashboard*
*Context gathered: 2026-03-21*
