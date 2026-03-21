# Phase 6: Staff Dashboard - Research

**Researched:** 2026-03-21
**Domain:** React SPA (admin dashboard) + Backend staff API endpoints
**Confidence:** HIGH

## Summary

Phase 6 builds a separate React frontend (`frontend-staff/`) for hotel staff daily operations. The frontend replicates the same tech stack as the guest frontend (Vite + React + Tailwind CSS 4 + shadcn/ui + TanStack Query + Zustand) but with a darker admin visual identity and sidebar navigation layout.

A critical finding is that **the backend currently lacks staff-specific booking endpoints**. The existing booking API (`services/booking/app/api/v1/bookings.py`) only supports guest-facing operations filtered by `user_id`. Phase 6 must add new staff endpoints for: listing ALL bookings with search/filter, check-in (assign room + transition status), and check-out (transition status + room cleanup). The gateway proxy already routes `/api/v1/bookings` to the booking service, so new endpoints under that prefix will automatically proxy.

The existing guest frontend (`frontend/`) provides battle-tested patterns to replicate: Axios client with JWT interceptor, Zustand auth store, TanStack Query hooks, shadcn/ui components, and Vitest configuration. These should be copied and adapted, not imported across app boundaries.

**Primary recommendation:** Build backend staff endpoints first (new router file `services/booking/app/api/v1/staff.py`), then scaffold the `frontend-staff/` React app replicating guest frontend patterns with dark admin theme customization.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Separate React app in `frontend-staff/` directory -- independent build from guest frontend
- Same tech stack: Vite + React + Tailwind CSS 4 + shadcn/ui
- Reuse shared patterns from guest frontend (API client structure, Zustand stores, query hooks)
- Staff auth required on all routes -- role-based access using JWT claims
- Darker admin visual feel -- distinct from the clean/white guest site
- Sidebar navigation (collapsible on mobile): Reservations, Check-in/out, Room Status, Guest Profiles, (Reports placeholder for Phase 7)
- Home page: today's overview -- today's check-ins, check-outs, current occupancy, room status summary
- Same design system (shadcn/ui) but with darker color scheme
- Room assignment: auto-assign from available rooms of booked type, staff can override
- Confirmation: dialog confirmation before check-in/check-out actions
- Check-in updates booking status (CONFIRMED -> CHECKED_IN) and room status (Available -> Occupied)
- Check-out updates booking status (CHECKED_IN -> CHECKED_OUT) and room status (Occupied -> Cleaning, auto)
- Room status changes happen via existing Room service API + RabbitMQ events
- Card grid display for reservations with quick actions
- Search by guest name, date range, status filter, confirmation number
- Pagination with 12 cards per page
- Status-based quick action visibility
- Read-only guest profiles with booking history

### Claude's Discretion
- Exact dark theme color palette (darker background, lighter cards) -- UI-SPEC provides full palette
- Today's overview layout and metric cards -- UI-SPEC defines 4-card layout
- Card grid column count and responsive breakpoints -- UI-SPEC: 3/2/1 columns
- Auto-assign algorithm -- UI-SPEC: lowest floor first, then lowest room number
- Pagination style -- UI-SPEC: numbered pages
- How sidebar collapses on mobile -- UI-SPEC: hamburger + Sheet slide-out

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| STAF-01 | Staff can view all reservations with search/filter (name, date, status, confirmation #) | Requires new staff booking list endpoint (no user_id filter). Frontend: reservation list page with card grid, search/filter bar, pagination. Existing `BookingListResponse` schema works. |
| STAF-02 | Staff can check in guests (assign specific room) | Requires new check-in endpoint that transitions CONFIRMED->CHECKED_IN + assigns room_id. Auto-assign algorithm: query available rooms of booked type, sort by floor ASC then room_number ASC. Frontend: check-in dialog with room assignment. |
| STAF-03 | Staff can check out guests | Requires new check-out endpoint that transitions CHECKED_IN->CHECKED_OUT + triggers room status to CLEANING. Frontend: check-out dialog with stay summary. |
| STAF-04 | Staff can view guest profile with booking history | Requires gateway BFF endpoint that combines Auth service user detail + Booking service list filtered by user_id. Frontend: guest search + profile page with booking history table. |
</phase_requirements>

## Standard Stack

### Core (replicate from guest frontend)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | ^19.2.4 | UI framework | Same as guest frontend, locked |
| Vite | ^8.0.1 | Build tool | Same as guest frontend |
| Tailwind CSS | ^4.2.2 | Styling | Same as guest frontend, dark theme via CSS variables |
| shadcn/ui | latest (New York style) | UI components | Same preset as guest frontend for component consistency |
| TanStack Query | ^5.91.3 | Server state | Same as guest frontend |
| Zustand | ^5.0.12 | Client state | Sidebar collapse state, filter state |
| React Router | ^7.13.1 | Routing | Same as guest frontend |
| Axios | ^1.13.6 | HTTP client | Same interceptor pattern |
| React Hook Form | ^7.71.2 | Forms | Search/filter forms |
| Zod | ^4.3.6 | Validation | Schema validation |
| date-fns | ^4.1.0 | Date formatting | Reservation dates, today's overview |
| lucide-react | ^0.577.0 | Icons | Sidebar nav icons, metric cards |
| sonner | ^2.0.7 | Toast notifications | Check-in/out success/error toasts |

### Supporting (from guest frontend)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @hookform/resolvers | ^5.2.2 | Form+Zod bridge | If search forms need Zod validation |
| class-variance-authority | ^0.7.1 | Component variants | StatusBadge variants, button variants |
| clsx + tailwind-merge | ^2.1.1 / ^3.5.0 | Class merging | Conditional dark theme classes |
| radix-ui | ^1.4.3 | Primitives | Via shadcn/ui components |

### Dev Dependencies
| Library | Version | Purpose |
|---------|---------|---------|
| Vitest | ^4.1.0 | Test runner |
| @testing-library/react | ^16.3.2 | Component testing |
| @testing-library/jest-dom | ^6.9.1 | DOM matchers |
| @testing-library/user-event | ^14.6.1 | User interaction simulation |
| jsdom | ^29.0.1 | Test DOM environment |
| TypeScript | ~5.9.3 | Type checking |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Separate app | Monorepo shared code | Separate apps are simpler, avoid coupling. Decision is locked. |
| Copy patterns | npm workspace shared package | Over-engineering for two apps in a portfolio project |

**Installation (frontend-staff/):**
```bash
# Create project
npm create vite@latest frontend-staff -- --template react-ts
cd frontend-staff

# Same dependencies as guest frontend
npm install react-router @tanstack/react-query zustand axios react-hook-form @hookform/resolvers zod date-fns lucide-react sonner
npm install tailwindcss @tailwindcss/vite class-variance-authority clsx tailwind-merge radix-ui

# Dev dependencies
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @types/node @vitejs/plugin-react eslint typescript typescript-eslint

# Initialize shadcn/ui (New York style, slate base)
npx shadcn@latest init

# Install shadcn components
npx shadcn@latest add button card input label select dialog skeleton separator badge dropdown-menu avatar form table pagination sheet tabs sonner popover sidebar tooltip
```

## Architecture Patterns

### Recommended Project Structure
```
frontend-staff/
├── src/
│   ├── api/
│   │   ├── client.ts          # Axios with JWT interceptor (replicated from guest)
│   │   ├── types.ts           # Staff-specific TS interfaces
│   │   ├── bookings.ts        # Staff booking API calls
│   │   ├── rooms.ts           # Room status API calls
│   │   └── guests.ts          # Guest profile API calls
│   ├── components/
│   │   ├── ui/                # shadcn/ui generated components
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx    # Collapsible sidebar navigation
│   │   │   ├── TopBar.tsx     # Sticky top bar with page title
│   │   │   └── AppLayout.tsx  # Main layout wrapper
│   │   ├── dashboard/
│   │   │   ├── MetricCard.tsx # Overview metric card
│   │   │   ├── ArrivalsList.tsx
│   │   │   └── DeparturesList.tsx
│   │   ├── reservations/
│   │   │   ├── ReservationCard.tsx
│   │   │   ├── SearchFilters.tsx
│   │   │   └── StatusBadge.tsx # Dark-themed status badge
│   │   ├── checkin/
│   │   │   ├── CheckInDialog.tsx
│   │   │   └── CheckOutDialog.tsx
│   │   ├── rooms/
│   │   │   ├── RoomCard.tsx
│   │   │   └── RoomStatusBoard.tsx
│   │   └── guests/
│   │       ├── GuestSearch.tsx
│   │       └── GuestProfile.tsx
│   ├── hooks/
│   │   └── queries/
│   │       ├── useStaffBookings.ts  # Staff booking query hooks
│   │       ├── useRooms.ts          # Room status query hooks
│   │       └── useGuests.ts         # Guest profile query hooks
│   ├── stores/
│   │   ├── authStore.ts       # Replicated with staff role check
│   │   └── sidebarStore.ts    # Sidebar collapse state
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── OverviewPage.tsx
│   │   ├── ReservationsPage.tsx
│   │   ├── CheckInOutPage.tsx
│   │   ├── RoomStatusPage.tsx
│   │   └── GuestProfilePage.tsx
│   ├── lib/
│   │   └── utils.ts           # cn() helper from shadcn
│   ├── test/
│   │   └── setup.ts           # Vitest setup (replicated from guest)
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css              # Tailwind + dark theme CSS variables
├── components.json            # shadcn/ui config
├── vite.config.ts
├── vitest.config.ts
├── tsconfig.json
├── tsconfig.app.json
└── package.json
```

### Pattern 1: API Client with Staff Auth Redirect
**What:** Replicate guest frontend Axios client but redirect to `/staff/login` on 401.
**When to use:** All API calls from staff dashboard.
**Example:**
```typescript
// Source: frontend/src/api/client.ts (adapted)
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('staff_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('staff_access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export { apiClient };
```

### Pattern 2: Staff Auth Store with Role Validation
**What:** Zustand auth store that validates staff role on login.
**When to use:** Login flow, route guards.
**Example:**
```typescript
// Source: frontend/src/stores/authStore.ts (adapted)
import { create } from 'zustand';
import type { UserResponse } from '@/api/types';

const STAFF_ROLES = ['admin', 'manager', 'front_desk', 'housekeeping'];

interface StaffAuthState {
  token: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  setUser: (user: UserResponse) => void;
  isStaff: () => boolean;
}

export const useStaffAuthStore = create<StaffAuthState>((set, get) => ({
  token: localStorage.getItem('staff_access_token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('staff_access_token'),
  login: (token: string) => {
    localStorage.setItem('staff_access_token', token);
    set({ token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('staff_access_token');
    set({ token: null, user: null, isAuthenticated: false });
  },
  setUser: (user: UserResponse) => set({ user }),
  isStaff: () => {
    const user = get().user;
    return !!user && STAFF_ROLES.includes(user.role);
  },
}));
```

### Pattern 3: TanStack Query Hooks for Staff Operations
**What:** Query hooks with mutation + cache invalidation for check-in/check-out.
**When to use:** All staff data fetching and mutations.
**Example:**
```typescript
// Source: frontend/src/hooks/queries/useBookings.ts (adapted)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useStaffBookings(params?: {
  search?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['staff-bookings', params],
    queryFn: () => getStaffBookings(params),
  });
}

export function useCheckIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ bookingId, roomId }: { bookingId: string; roomId: string }) =>
      checkInGuest(bookingId, roomId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['room-status'] });
      queryClient.invalidateQueries({ queryKey: ['overview'] });
    },
  });
}
```

### Pattern 4: Dark Theme via CSS Variables
**What:** Override shadcn CSS variables for dark admin theme in `index.css`.
**When to use:** Global theme definition.
**Example:**
```css
/* Staff dark theme -- override shadcn CSS variables */
@layer base {
  :root {
    --background: 222.2 47.4% 11.2%;    /* slate-900 #0F172A */
    --foreground: 210 40% 96.1%;          /* slate-100 #F1F5F9 */
    --card: 222.2 47.4% 16.5%;           /* slate-800 #1E293B */
    --card-foreground: 210 40% 96.1%;
    --primary: 173.4 80.4% 25.9%;        /* teal-700 #0F766E */
    --primary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;          /* slate-800 */
    --muted-foreground: 215 20.2% 65.1%; /* slate-400 */
    --border: 217.2 32.6% 29.4%;         /* slate-700 #334155 */
    --input: 222.2 47.4% 16.5%;          /* slate-800 */
    --destructive: 0 72.2% 50.6%;        /* red-600 */
    --ring: 173.4 80.4% 25.9%;           /* teal-700 */
  }
}
```

### Anti-Patterns to Avoid
- **Importing from guest frontend:** Do NOT import code from `frontend/src/`. Copy and adapt patterns. The apps must be independently buildable.
- **Using `user_id` filter for staff booking list:** Staff endpoints must list ALL bookings, not filter by authenticated user. This is the key difference from guest endpoints.
- **Single localStorage key for both apps:** Use `staff_access_token` (not `access_token`) to avoid conflicts if both apps are open in the same browser.
- **Polling without staleTime:** Set appropriate `staleTime` on TanStack Query (e.g., 30s for overview, 60s for reservation list) to avoid unnecessary API calls.
- **Hand-rolling sidebar:** Use shadcn/ui's `sidebar` component which handles collapse, mobile sheet, and keyboard nav.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sidebar navigation | Custom sidebar with collapse logic | shadcn/ui `sidebar` component | Handles responsive collapse, Sheet on mobile, keyboard nav, tooltips on collapsed items |
| Status badges | Custom styled spans | Replicate `StatusBadge.tsx` from guest frontend with dark theme colors from UI-SPEC | Consistent status representation |
| Pagination | Custom page calculation | shadcn/ui `pagination` component | Handles numbered pages, prev/next, edge cases |
| Confirmation dialogs | Custom modal implementation | shadcn/ui `dialog` component | Focus trapping, escape to close, accessible |
| Toast notifications | Custom notification system | `sonner` (already in stack) | Auto-dismiss, stacking, animations |
| Data tables | Custom table rendering | shadcn/ui `table` component | Sticky headers, row hover, accessible markup |
| Date range inputs | Custom date pickers | `react-day-picker` (already in guest frontend deps) with shadcn popover | Date range selection for filter |
| Room auto-assignment | Complex assignment algorithm | Simple SQL query: `SELECT * FROM rooms WHERE room_type_id = ? AND status = 'available' ORDER BY floor ASC, room_number ASC LIMIT 1` | Predictable, matches housekeeping workflows |

**Key insight:** The staff dashboard is UI-heavy but logic-light. Most complexity is in layout, data display, and state transitions -- all well-served by shadcn/ui components and TanStack Query patterns already proven in the guest frontend.

## Common Pitfalls

### Pitfall 1: Missing Staff Backend Endpoints
**What goes wrong:** The staff dashboard cannot function without backend endpoints that list ALL bookings (not per-user) and handle check-in/check-out with room assignment.
**Why it happens:** The existing booking service was built for guest-facing operations only, with `user_id` filtering on every query.
**How to avoid:** Build new staff endpoints FIRST before building frontend pages. Add `services/booking/app/api/v1/staff.py` with `require_role("admin", "manager", "front_desk")` dependency.
**Warning signs:** Frontend returning empty lists or 403 errors.

### Pitfall 2: Check-in/Check-out Cross-Service Coordination
**What goes wrong:** Check-in must update BOTH booking status (Booking service) AND room status (Room service). If done as two separate API calls from frontend, partial failures leave inconsistent state.
**Why it happens:** Microservice architecture means the two updates cross service boundaries.
**How to avoid:** Implement check-in/check-out as a single gateway BFF endpoint that coordinates both calls. If room status update fails, roll back booking status change (or at least return an error indicating partial success).
**Warning signs:** Room shown as "Available" but booking shows "Checked In".

### Pitfall 3: Vite Dev Server Port Collision
**What goes wrong:** Both guest frontend and staff frontend try to use port 5173.
**Why it happens:** Vite defaults to port 5173.
**How to avoid:** Configure `frontend-staff/vite.config.ts` with `server.port: 5174` and proxy to gateway at `localhost:8000`.
**Warning signs:** "Port 5173 already in use" error.

### Pitfall 4: shadcn/ui Dark Theme CSS Variable Conflicts
**What goes wrong:** shadcn components look wrong because CSS variables assume light theme defaults.
**Why it happens:** shadcn/ui initializes with light theme CSS variables. Staff dashboard needs ALL variables overridden for dark.
**How to avoid:** Define the dark palette as the `:root` default (not inside a `.dark` class). The staff app is ALWAYS dark -- no light/dark toggle needed.
**Warning signs:** White backgrounds on shadcn components, invisible text.

### Pitfall 5: Booking List Endpoint Without Search
**What goes wrong:** Staff cannot find bookings efficiently because the existing list endpoint only supports status filter, not guest name or confirmation number search.
**Why it happens:** Guest-facing list only needs per-user filtering.
**How to avoid:** Add `search` query parameter to staff booking list endpoint that matches against `guest_first_name`, `guest_last_name`, and `confirmation_number` using SQL `ILIKE`.
**Warning signs:** Staff must scroll through all bookings to find a specific guest.

### Pitfall 6: Room Assignment Race Condition
**What goes wrong:** Two staff members check in different guests and both get assigned the same room.
**Why it happens:** No locking on room assignment.
**How to avoid:** Use `SELECT ... FOR UPDATE` when querying available rooms during check-in, within the same transaction that updates room status.
**Warning signs:** Two bookings with the same `room_id`.

## Code Examples

### Backend: Staff Booking List Endpoint
```python
# services/booking/app/api/v1/staff.py
# Requires new router for staff-only booking operations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.models.booking import Booking

router = APIRouter(prefix="/api/v1/bookings/staff", tags=["staff-bookings"])

require_staff = require_role("admin", "manager", "front_desk")

@router.get("/", response_model=BookingListResponse)
async def list_all_bookings(
    search: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = Query(default=12, le=100),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """List ALL bookings with search/filter for staff."""
    # No user_id filter -- staff sees all bookings
    filters = []
    if status:
        filters.append(Booking.status == status)
    if date_from:
        filters.append(Booking.check_in >= date_from)
    if date_to:
        filters.append(Booking.check_in <= date_to)
    if search:
        search_term = f"%{search}%"
        filters.append(or_(
            Booking.guest_first_name.ilike(search_term),
            Booking.guest_last_name.ilike(search_term),
            Booking.confirmation_number.ilike(search_term),
        ))
    # ... paginated query
```

### Backend: Check-in Endpoint
```python
# services/booking/app/api/v1/staff.py (continued)

@router.post("/{booking_id}/check-in", response_model=BookingResponse)
async def check_in_guest(
    booking_id: UUID,
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_staff),
):
    """Check in a guest: assign room + transition to CHECKED_IN.

    Room status transition (Available -> Occupied) is handled
    by the gateway BFF which calls Room service after booking update.
    """
    booking = await get_booking(db, booking_id)  # No user_id ownership check
    booking.room_id = room_id
    booking = await transition_booking(db, booking, "checked_in")
    return booking
```

### Backend: Gateway BFF Check-in Orchestration
```python
# services/gateway/app/api/staff.py
# BFF endpoint that coordinates check-in across Booking + Room services

@router.post("/api/v1/staff/check-in/{booking_id}")
async def staff_check_in(booking_id: str, request: Request):
    """Orchestrate check-in: update booking + transition room status."""
    body = await request.json()
    room_id = body["room_id"]
    auth_header = request.headers.get("authorization", "")
    headers = {"authorization": auth_header}

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: Check in on booking service
        booking_resp = await client.post(
            f"{settings.BOOKING_SERVICE_URL}/api/v1/bookings/staff/{booking_id}/check-in",
            json={"room_id": room_id},
            headers=headers,
        )
        if booking_resp.status_code != 200:
            return Response(content=booking_resp.content, status_code=booking_resp.status_code)

        # Step 2: Transition room to Occupied
        room_resp = await client.post(
            f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/{room_id}/status",
            json={"new_status": "occupied"},
            headers=headers,
        )
        # Graceful degradation if room service fails

    return Response(content=booking_resp.content, status_code=200)
```

### Frontend: Vite Config for Staff App
```typescript
// frontend-staff/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5174,  // Different from guest frontend (5173)
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Same gateway
        changeOrigin: true,
      },
    },
  },
})
```

### Frontend: Staff Check-in Mutation with Cache Invalidation
```typescript
// frontend-staff/src/hooks/queries/useStaffBookings.ts
export function useCheckIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ bookingId, roomId }: { bookingId: string; roomId: string }) =>
      apiClient.post(`/api/v1/staff/check-in/${bookingId}`, { room_id: roomId }),
    onSuccess: () => {
      // Invalidate all related caches
      queryClient.invalidateQueries({ queryKey: ['staff-bookings'] });
      queryClient.invalidateQueries({ queryKey: ['room-status'] });
      queryClient.invalidateQueries({ queryKey: ['today-overview'] });
    },
  });
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CSS dark mode toggle | Always-dark admin theme via CSS variables at `:root` | N/A | No `.dark` class needed; all shadcn variables set for dark |
| Custom sidebar component | shadcn/ui `sidebar` component | shadcn added sidebar component | Handles collapse, Sheet, tooltip, keyboard nav out of the box |
| Manual pagination | shadcn/ui `pagination` component | shadcn added pagination | Consistent numbered pagination with accessible markup |

## Backend Endpoints Needed (New)

### Booking Service (`services/booking/app/api/v1/staff.py`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/v1/bookings/staff/` | List ALL bookings with search/filter/pagination | require_staff |
| GET | `/api/v1/bookings/staff/today` | Today's check-ins and check-outs | require_staff |
| POST | `/api/v1/bookings/staff/{id}/check-in` | Assign room + transition to CHECKED_IN | require_staff |
| POST | `/api/v1/bookings/staff/{id}/check-out` | Transition to CHECKED_OUT | require_staff |
| POST | `/api/v1/bookings/staff/{id}/cancel` | Staff-initiated cancellation | require_staff |
| GET | `/api/v1/bookings/staff/by-user/{user_id}` | List bookings for a specific guest | require_staff |

### Gateway BFF (`services/gateway/app/api/staff.py`)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/staff/check-in/{id}` | Orchestrate check-in: booking + room status |
| POST | `/api/v1/staff/check-out/{id}` | Orchestrate check-out: booking + room status -> cleaning |
| GET | `/api/v1/staff/overview` | Aggregate: today's counts + occupancy + rooms to clean |
| GET | `/api/v1/staff/guests/search` | Search guests by name/email from Auth service |
| GET | `/api/v1/staff/guests/{id}/profile` | Guest detail + booking history aggregation |

### Room Service (existing, no changes needed)

| Method | Path | Already Exists |
|--------|------|---------------|
| GET | `/api/v1/rooms/board` | Yes -- status board grouped by floor |
| GET | `/api/v1/rooms/list` | Yes -- list rooms with filters |
| POST | `/api/v1/rooms/{id}/status` | Yes -- transition room status |
| GET | `/api/v1/rooms/{id}` | Yes -- get room detail |

### Gateway Proxy Update
Add to `SERVICE_MAP` in `services/gateway/app/api/proxy.py`:
```python
"/api/v1/bookings/staff": settings.BOOKING_SERVICE_URL,
```
Note: This prefix already matches under `/api/v1/bookings` so no change needed -- existing gateway proxy will forward these.

## Available Rooms Query for Auto-Assignment

The Room service list endpoint (`GET /api/v1/rooms/list`) already supports filtering by `room_type_id` and `room_status`. For auto-assignment during check-in:

```
GET /api/v1/rooms/list?room_type_id={booked_type}&room_status=available&limit=1
```

However, the endpoint does not support `ORDER BY floor ASC, room_number ASC` -- it returns rooms in default order. Two options:
1. **Frontend sorts:** Fetch all available rooms of that type, sort client-side, pick first.
2. **Backend adds sort param:** Add `sort_by` query param to rooms list endpoint.

**Recommendation:** Option 1 (frontend sorts) since the number of rooms per type is small (< 50). The sort is trivial and avoids backend changes to the Room service.

## Open Questions

1. **Gateway prefix routing for `/api/v1/bookings/staff`**
   - What we know: The gateway proxy matches on longest prefix. `/api/v1/bookings` already maps to the booking service.
   - What's unclear: Whether `/api/v1/bookings/staff/` will be caught by the existing `/api/v1/bookings` prefix match.
   - Recommendation: It WILL match -- the proxy iterates `SERVICE_MAP` and uses `startswith()`. `/api/v1/bookings/staff/...` starts with `/api/v1/bookings`. No gateway change needed for staff booking endpoints. Gateway BFF endpoints at `/api/v1/staff/` DO need a new `SERVICE_MAP` entry or a new BFF router.

2. **Guest search across Auth service**
   - What we know: Auth service has `GET /api/v1/users/` (admin only) and `GET /api/v1/users/{id}` (staff). But no search-by-name endpoint.
   - What's unclear: Whether to add search to Auth service or do it at gateway BFF level.
   - Recommendation: Add a search endpoint to Auth service (`GET /api/v1/users/search?q=name`) since text search belongs at the data layer. Alternatively, the gateway BFF can fetch all users and filter -- acceptable for small datasets but not scalable.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest 4.1.0 + React Testing Library 16.3.2 |
| Config file | `frontend-staff/vitest.config.ts` (Wave 0 -- create) |
| Quick run command | `cd frontend-staff && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend-staff && npx vitest run --reporter=verbose` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| STAF-01 | Reservation list renders with cards, search filters, pagination | unit | `cd frontend-staff && npx vitest run src/pages/ReservationsPage.test.tsx -x` | Wave 0 |
| STAF-01 | Staff booking API returns all bookings (not user-filtered) | integration | `cd services/booking && python -m pytest tests/test_staff_bookings.py -x` | Wave 0 |
| STAF-02 | Check-in dialog opens, shows auto-assigned room, confirms | unit | `cd frontend-staff && npx vitest run src/components/checkin/CheckInDialog.test.tsx -x` | Wave 0 |
| STAF-02 | Check-in endpoint assigns room + transitions status | integration | `cd services/booking && python -m pytest tests/test_staff_checkin.py -x` | Wave 0 |
| STAF-03 | Check-out dialog opens, shows summary, confirms | unit | `cd frontend-staff && npx vitest run src/components/checkin/CheckOutDialog.test.tsx -x` | Wave 0 |
| STAF-03 | Check-out endpoint transitions booking + room status | integration | `cd services/booking && python -m pytest tests/test_staff_checkout.py -x` | Wave 0 |
| STAF-04 | Guest profile shows contact info + booking history table | unit | `cd frontend-staff && npx vitest run src/pages/GuestProfilePage.test.tsx -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend-staff && npx vitest run --reporter=verbose`
- **Per wave merge:** Full frontend + backend test suites
- **Phase gate:** All tests green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend-staff/vitest.config.ts` -- Vitest configuration (replicate from guest frontend)
- [ ] `frontend-staff/src/test/setup.ts` -- Test setup with localStorage polyfill
- [ ] `services/booking/tests/test_staff_bookings.py` -- Staff booking list endpoint tests
- [ ] `services/booking/tests/test_staff_checkin.py` -- Check-in endpoint tests
- [ ] `services/booking/tests/test_staff_checkout.py` -- Check-out endpoint tests
- [ ] Framework install: `cd frontend-staff && npm install` -- entire project scaffold needed

## Sources

### Primary (HIGH confidence)
- `frontend/src/api/client.ts` -- Established Axios + JWT interceptor pattern
- `frontend/src/stores/authStore.ts` -- Zustand auth store pattern
- `frontend/src/hooks/queries/useBookings.ts` -- TanStack Query hooks pattern
- `frontend/vite.config.ts` -- Vite proxy configuration pattern
- `frontend/vitest.config.ts` -- Vitest jsdom configuration
- `frontend/package.json` -- Exact dependency versions to replicate
- `services/booking/app/api/v1/bookings.py` -- Existing booking endpoints (guest-only)
- `services/booking/app/models/booking.py` -- BookingStatus enum and VALID_TRANSITIONS
- `services/booking/app/api/deps.py` -- `require_role()` dependency factory
- `services/room/app/api/v1/rooms.py` -- Room CRUD + status board endpoints
- `services/room/app/services/room.py` -- ROLE_TRANSITIONS for room status
- `services/gateway/app/api/proxy.py` -- SERVICE_MAP gateway routing
- `06-UI-SPEC.md` -- Complete visual and interaction contract

### Secondary (MEDIUM confidence)
- `services/auth/app/api/v1/users.py` -- User list/detail endpoints (may need search addition)

### Tertiary (LOW confidence)
- shadcn/ui `sidebar` component documentation -- assumed available based on shadcn registry, should verify during implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- exact versions replicated from existing guest frontend `package.json`
- Architecture: HIGH -- patterns proven in Phase 5 guest frontend, replicated with minor adaptations
- Backend endpoints: HIGH -- clear gap analysis from reading existing code; VALID_TRANSITIONS already supports checked_in/checked_out
- Pitfalls: HIGH -- identified from reading actual code patterns and cross-service architecture
- UI-SPEC compliance: HIGH -- detailed UI-SPEC provides all visual specifications

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable patterns, no fast-moving dependencies)
