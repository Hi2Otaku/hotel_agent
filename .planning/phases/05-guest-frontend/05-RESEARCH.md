# Phase 5: Guest Frontend - Research

**Researched:** 2026-03-21
**Domain:** React SPA — guest booking journey (search, booking wizard, account, booking management)
**Confidence:** HIGH

## Summary

Phase 5 is a greenfield React SPA that consumes the existing gateway BFF API. The backend is fully built (phases 1-4 complete) with search, booking, auth, and room management endpoints all proxied through the gateway at `localhost:8000`. The frontend needs to implement: landing page with search, room search results with filters, a 4-step booking wizard with state persistence, guest auth pages, My Bookings list, booking detail with status timeline, and a pricing calendar. All API contracts are well-defined via Pydantic schemas.

The stack is locked: React 19 + Vite 8 + Tailwind CSS 4 + shadcn/ui + TanStack Query + Zustand + React Hook Form + Zod. The UI-SPEC provides complete visual and interaction contracts including colors, typography, spacing, breakpoints, component states, and copywriting. This is primarily an execution phase -- the design and API contracts are already defined.

**Primary recommendation:** Structure the app around React Router v7 with route-level code splitting, use TanStack Query for all API calls with a centralized Axios instance, Zustand for booking wizard state with localStorage persistence, and React Hook Form + Zod for all forms. Install shadcn/ui components incrementally as needed.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Clean & modern aesthetic: white space, subtle shadows, minimal borders (Airbnb/Booking.com style)
- Landing page: split layout -- left: search card form, right: rotating resort photos
- Top navbar: fixed, with logo, search link, pricing calendar, My Bookings, Login/Profile
- Simple footer: contact info, quick links, "Powered by HotelBook"
- Sidebar steps booking wizard: steps listed in left sidebar, content on right -- 1. Room > 2. Details > 3. Payment > 4. Confirmed
- Free back navigation: guests can go back to any previous step, data preserved
- Booking summary: collapsible panel (top on mobile), showing room type, dates, nights, price breakdown
- Browser refresh resilience: booking ID saved to URL/localStorage -- guest resumes where they left off
- Search form: card-style with stacked inputs (check-in, check-out, guests, search button)
- Filters: slide-out drawer triggered by filter icon -- mobile-friendly
- Result cards: large photo cards with room type name, price, amenity tags, book button
- Login/register: dedicated pages (/login, /register)
- My Bookings: card list with dates, room type, status badge, action buttons
- Booking detail: confirmation number, dates, room photo, price breakdown, guest info, status timeline, action buttons, cancellation policy
- Loading: skeleton loaders for content areas
- Errors: toast notifications for API errors, inline validation for forms
- Empty states: friendly messages with actionable CTAs

### Claude's Discretion
- Color palette and typography choices (decided in UI-SPEC: Teal-700 accent, Inter font)
- Date picker component choice (shadcn/ui Calendar + Popover)
- Exact responsive breakpoints and mobile adaptations (decided in UI-SPEC: 640/1024)
- Animation/transition style (decided in UI-SPEC: minimal, no route transitions)
- Loading skeleton design (decided in UI-SPEC: animate-pulse slate-200)
- Toast notification library choice (decided in UI-SPEC: sonner)
- How the pricing calendar integrates with search (click date to pre-fill search)
- Room photo gallery/carousel implementation (decided in UI-SPEC: embla-carousel-react)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFR-01 | Responsive design for guest-facing site (mobile-first) | UI-SPEC defines 3 breakpoints (mobile <640, tablet 640-1023, desktop >=1024). Tailwind CSS 4 utility classes handle responsive design natively. shadcn/ui Sheet component for mobile navigation and filter drawers. |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | 19.2.4 | UI framework | Locked in STACK.md and CONTEXT.md |
| Vite | 8.0.1 | Build tool / dev server | Rolldown bundler, fast HMR |
| Tailwind CSS | 4.2.2 | Utility-first styling | Zero-config in v4, pairs with shadcn/ui |
| shadcn/ui | latest | Component library (source code) | Radix UI + Tailwind, full control |
| React Router | 7.13.1 | Client-side routing | SPA routing with data loading |
| TanStack Query | 5.91.3 | Server state management | Caching, background refetch, mutations |
| Zustand | 5.0.12 | Client state management | Booking wizard step/data, UI state |
| React Hook Form | 7.71.2 | Form handling | Multi-step forms, uncontrolled perf |
| Zod | 4.3.6 | Schema validation | Form validation + API response parsing |
| Axios | 1.13.6 | HTTP client | Interceptors for JWT injection |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| date-fns | 4.1.0 | Date manipulation | Date formatting, range calc, calendar logic |
| sonner | 2.0.7 | Toast notifications | API errors, success messages |
| embla-carousel-react | 8.6.0 | Photo carousel | Room type photo galleries |
| lucide-react | 0.577.0 | Icon library | All UI icons |
| @hookform/resolvers | 5.2.2 | Form + Zod bridge | Connect Zod schemas to React Hook Form |

### shadcn/ui Components to Install
button, card, input, label, select, dialog, sheet, skeleton, separator, badge, calendar, popover, dropdown-menu, avatar, form, tabs, navigation-menu, sonner (toast)

**Installation:**
```bash
# Create Vite project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Core dependencies
npm install react-router @tanstack/react-query zustand axios date-fns
npm install react-hook-form @hookform/resolvers zod
npm install embla-carousel-react sonner lucide-react

# Tailwind CSS v4
npm install tailwindcss @tailwindcss/vite

# Dev dependencies
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom

# Initialize shadcn/ui (after Tailwind configured)
npx shadcn@latest init

# Install shadcn components
npx shadcn@latest add button card input label select dialog sheet skeleton separator badge calendar popover dropdown-menu avatar form tabs navigation-menu sonner
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/
├── src/
│   ├── api/                # API client layer
│   │   ├── client.ts       # Axios instance with interceptors
│   │   ├── auth.ts         # Auth API functions
│   │   ├── search.ts       # Search API functions
│   │   ├── booking.ts      # Booking API functions
│   │   └── types.ts        # TypeScript types matching backend schemas
│   ├── components/         # Shared components
│   │   ├── ui/             # shadcn/ui components (auto-generated)
│   │   ├── layout/         # Navbar, Footer, PageLayout
│   │   ├── booking/        # Booking-specific components
│   │   ├── search/         # Search-specific components
│   │   └── common/         # LoadingSpinner, EmptyState, ErrorBoundary
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.ts      # Auth state + token management
│   │   ├── useBookingWizard.ts  # Wizard state management
│   │   └── queries/        # TanStack Query hooks
│   │       ├── useSearch.ts
│   │       ├── useBookings.ts
│   │       └── useAuth.ts
│   ├── pages/              # Route-level page components
│   │   ├── Landing.tsx
│   │   ├── SearchResults.tsx
│   │   ├── BookingWizard.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── PasswordReset.tsx
│   │   ├── MyBookings.tsx
│   │   ├── BookingDetail.tsx
│   │   └── PricingCalendar.tsx
│   ├── stores/             # Zustand stores
│   │   ├── authStore.ts    # JWT token, user info
│   │   └── bookingWizardStore.ts  # Wizard step, form data
│   ├── lib/                # Utility functions
│   │   ├── utils.ts        # cn() helper (shadcn), formatters
│   │   └── validators.ts   # Zod schemas
│   ├── App.tsx             # Router setup + providers
│   ├── main.tsx            # Entry point
│   └── index.css           # Tailwind + custom CSS vars
├── components.json         # shadcn/ui config
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### Pattern 1: API Client with JWT Interceptor
**What:** Centralized Axios instance that auto-attaches JWT and handles 401 redirects
**When to use:** All API calls go through this client
**Example:**
```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Pattern 2: TanStack Query Hooks
**What:** Encapsulate API calls + caching in custom hooks
**When to use:** Every data-fetching component
**Example:**
```typescript
// src/hooks/queries/useSearch.ts
import { useQuery } from '@tanstack/react-query';
import { searchAvailability } from '@/api/search';

export function useSearchAvailability(params: SearchParams) {
  return useQuery({
    queryKey: ['search', params],
    queryFn: () => searchAvailability(params),
    enabled: !!params.checkIn && !!params.checkOut,
    staleTime: 30_000, // 30s -- availability changes
  });
}
```

### Pattern 3: Zustand Store with localStorage Persistence
**What:** Wizard state that survives browser refresh
**When to use:** Booking wizard step tracking and form data
**Example:**
```typescript
// src/stores/bookingWizardStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WizardState {
  step: number;
  bookingId: string | null;
  roomTypeId: string | null;
  checkIn: string | null;
  checkOut: string | null;
  guestDetails: GuestDetails | null;
  setStep: (step: number) => void;
  setBookingId: (id: string) => void;
  reset: () => void;
}

export const useBookingWizardStore = create<WizardState>()(
  persist(
    (set) => ({
      step: 1,
      bookingId: null,
      roomTypeId: null,
      checkIn: null,
      checkOut: null,
      guestDetails: null,
      setStep: (step) => set({ step }),
      setBookingId: (id) => set({ bookingId: id }),
      reset: () => set({ step: 1, bookingId: null, roomTypeId: null,
                         checkIn: null, checkOut: null, guestDetails: null }),
    }),
    { name: 'booking-wizard' }
  )
);
```

### Pattern 4: Auth Store with Token Management
**What:** JWT stored in localStorage, user info fetched via /auth/me
**When to use:** Auth state across the app
**Example:**
```typescript
// src/stores/authStore.ts
import { create } from 'zustand';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('access_token'),
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  login: (token) => {
    localStorage.setItem('access_token', token);
    set({ token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('access_token');
    set({ token: null, user: null, isAuthenticated: false });
  },
  setUser: (user) => set({ user }),
}));
```

### Pattern 5: Protected Route Component
**What:** Route wrapper that redirects unauthenticated users to login
**When to use:** My Bookings, Booking Detail, Booking Wizard (steps 2+)
**Example:**
```typescript
// src/components/common/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router';
import { useAuthStore } from '@/stores/authStore';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return <>{children}</>;
}
```

### Anti-Patterns to Avoid
- **Storing server data in Zustand:** Use TanStack Query for API data. Zustand is only for UI state (wizard step, filter toggles).
- **Fetching in useEffect:** Use TanStack Query's useQuery/useMutation. Never manage loading/error states manually.
- **Prop drilling:** Use Zustand stores or TanStack Query hooks at the component that needs the data.
- **Giant page components:** Extract reusable pieces (RoomCard, BookingSummary, StatusTimeline) into components/.
- **Hardcoded API URLs:** Use environment variable `VITE_API_URL` with a fallback.

## API Surface Reference

### Auth Endpoints (via gateway proxy)
| Method | Path | Auth | Request | Response |
|--------|------|------|---------|----------|
| POST | /api/v1/auth/register | No | `{ email, password, first_name, last_name }` | `{ access_token, token_type }` |
| POST | /api/v1/auth/login | No | Form: `username` (email), `password` | `{ access_token, token_type }` |
| GET | /api/v1/auth/me | JWT | - | `{ id, email, first_name, last_name, role, is_active, created_at }` |
| POST | /api/v1/auth/password-reset/request | No | `{ email }` | `{ message }` |
| POST | /api/v1/auth/password-reset/confirm | No | `{ token, new_password }` | `{ message }` |

**CRITICAL -- Login uses form-data (OAuth2PasswordRequestForm):** The login endpoint expects `application/x-www-form-urlencoded` with `username` and `password` fields, NOT JSON. The `username` field contains the email address. Axios must be configured with `Content-Type: application/x-www-form-urlencoded` for this endpoint.

### Search Endpoints (public, via gateway BFF)
| Method | Path | Auth | Params | Response |
|--------|------|------|--------|----------|
| GET | /api/v1/search/availability | No | check_in, check_out, guests, room_type_id?, min_price?, max_price?, amenities?, sort? | `{ results: SearchResult[], total, check_in, check_out, guests }` |
| GET | /api/v1/search/room-types/{id} | No | check_in, check_out, guests? | `RoomTypeDetail` |
| GET | /api/v1/search/calendar | No | room_type_id?, guests?, months? | `{ room_type_id, room_type_name, start_date, end_date, days: CalendarDay[] }` |

### Booking Endpoints (all require JWT, via gateway proxy)
| Method | Path | Auth | Request | Response |
|--------|------|------|---------|----------|
| POST | /api/v1/bookings/ | JWT | `{ room_type_id, check_in, check_out, guest_count }` | `BookingResponse` (status 201) |
| PUT | /api/v1/bookings/{id}/guest-details | JWT | `{ guest_first_name, guest_last_name, guest_email, guest_phone, special_requests? }` | `BookingResponse` |
| POST | /api/v1/bookings/{id}/payment | JWT | `{ card_number, expiry_month, expiry_year, cvc, cardholder_name }` | `{ booking, payment }` |
| GET | /api/v1/bookings/ | JWT | status?, skip?, limit? | `{ items: BookingResponse[], total }` |
| GET | /api/v1/bookings/{id} | JWT | - | `BookingResponse` |
| GET | /api/v1/bookings/{id}/cancellation-policy | JWT | - | `{ free_cancellation_before, cancellation_fee, policy_text }` |
| POST | /api/v1/bookings/{id}/cancel | JWT | - | `BookingResponse` |
| PUT | /api/v1/bookings/{id}/modify | JWT | `BookingModifyRequest` (all optional) | `{ booking, old_total, new_total, price_difference, currency }` |

### BFF Enriched Endpoints (via gateway BFF)
| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | /api/v1/bookings/{id}/details | JWT | BookingResponse + room_type_name, room_type_description, room_type_photos, room_type_amenities |
| GET | /api/v1/bookings/summary | JWT | BookingListResponse with room_type_name added to each item |

## Route Map

```
/                          Landing page (public)
/search                    Search results (public)
/rooms/:roomTypeId         Room type detail (public)
/book                      Booking wizard (auth required for steps 2+)
/pricing                   Pricing calendar (public)
/login                     Login page (public)
/register                  Register page (public)
/password-reset            Password reset request (public)
/password-reset/confirm    Password reset with token (public)
/my-bookings               Booking list (auth required)
/my-bookings/:bookingId    Booking detail (auth required)
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Date picker | Custom calendar input | shadcn/ui Calendar + Popover | Date range selection edge cases, keyboard nav, locale handling |
| Toast system | Custom notification stack | sonner (via shadcn/ui) | Animation, stacking, auto-dismiss, accessibility |
| Form validation | Manual onChange handlers | React Hook Form + Zod + @hookform/resolvers | Multi-step form state, field-level validation, uncontrolled perf |
| Modal/Dialog | Custom overlay | shadcn/ui Dialog | Focus trap, escape key, backdrop click, portal rendering |
| Mobile drawer | Custom slide panel | shadcn/ui Sheet | Touch gestures, animation, backdrop, scroll lock |
| Photo carousel | Custom slider with CSS | embla-carousel-react | Touch/swipe, loop, responsive, lazy loading |
| Loading skeletons | Manual placeholder divs | shadcn/ui Skeleton | Consistent pulse animation, composable |
| Dropdown menu | Custom JS menu | shadcn/ui DropdownMenu | Keyboard nav, focus management, portal positioning |

**Key insight:** shadcn/ui provides almost every interactive component needed. The only additional UI library is embla-carousel-react for photo galleries. All other interactions are covered by Radix UI primitives via shadcn.

## Common Pitfalls

### Pitfall 1: Login Endpoint Uses Form-Data, Not JSON
**What goes wrong:** Sending JSON to /auth/login returns 422 validation error
**Why it happens:** FastAPI's `OAuth2PasswordRequestForm` expects `application/x-www-form-urlencoded`
**How to avoid:** Use `URLSearchParams` or `qs.stringify` for login POST, with `Content-Type: application/x-www-form-urlencoded`
**Warning signs:** 422 error on login, "field required" validation errors

### Pitfall 2: Login Uses "username" Field for Email
**What goes wrong:** Sending `{ email: "..." }` to login fails
**Why it happens:** OAuth2PasswordRequestForm requires field name `username`
**How to avoid:** Map email to `username` field in the login API function
**Warning signs:** Login always returns 422 even with correct credentials

### Pitfall 3: Vite Proxy for Dev Environment
**What goes wrong:** CORS errors when frontend (port 5173) calls gateway (port 8000)
**Why it happens:** Browser enforces same-origin policy in development
**How to avoid:** Configure Vite dev proxy in vite.config.ts to forward /api/* to gateway. Gateway already has CORS allow_origins=["*"] but the proxy is cleaner.
**Warning signs:** CORS errors in browser console

### Pitfall 4: Tailwind CSS v4 Configuration
**What goes wrong:** Styles not applying, purge removing needed classes
**Why it happens:** Tailwind v4 uses CSS-first config, not tailwind.config.js
**How to avoid:** Use `@import "tailwindcss"` in CSS and `@tailwindcss/vite` plugin. No config file needed for basics. Custom theme values go in CSS with `@theme`.
**Warning signs:** Missing utilities, classes not being generated

### Pitfall 5: Booking Wizard State Loss on Refresh
**What goes wrong:** User refreshes page during booking and loses progress
**Why it happens:** React state is ephemeral
**How to avoid:** Persist booking wizard state to localStorage via Zustand `persist` middleware. Store bookingId in URL params. On refresh, restore from localStorage and refetch booking state from API.
**Warning signs:** User complaints about lost form data

### Pitfall 6: Date Serialization Mismatch
**What goes wrong:** API returns dates as "2026-03-21" strings but frontend treats them as Date objects
**Why it happens:** JSON has no native date type. Axios does not auto-parse dates.
**How to avoid:** Keep dates as ISO strings (`YYYY-MM-DD`) throughout. Only convert to Date objects at the display layer using date-fns `parseISO` and `format`. Zod schemas should use `z.string()` for dates, not `z.date()`.
**Warning signs:** "Invalid Date" display, NaN in date calculations, timezone shifts

### Pitfall 7: shadcn/ui + Tailwind v4 Init Issues
**What goes wrong:** `npx shadcn@latest init` fails or produces wrong config
**Why it happens:** shadcn/ui has specific expectations for Tailwind v4 CSS structure
**How to avoid:** Follow this order: (1) Set up Vite + React, (2) Install Tailwind v4 with @tailwindcss/vite plugin, (3) Add `@import "tailwindcss"` to CSS, (4) Run `npx shadcn@latest init` which detects v4 automatically
**Warning signs:** Component styles not rendering, CSS variable conflicts

### Pitfall 8: Decimal/Money Display
**What goes wrong:** Prices show as "123.4" instead of "$123.40"
**Why it happens:** API returns Decimal as string/number, no auto-formatting
**How to avoid:** Create a `formatCurrency(amount: string | number)` utility using `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`. Apply everywhere prices appear.
**Warning signs:** Inconsistent price formatting, missing decimals

## Code Examples

### Vite Dev Proxy Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### Tailwind CSS v4 Entry Point
```css
/* src/index.css */
@import "tailwindcss";

/* Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, sans-serif;
  --color-accent: #0F766E;
  --color-accent-hover: #0D6660;
  --color-destructive: #DC2626;
  --color-success: #16A34A;
  --color-warning: #D97706;
  --color-muted: #64748B;
  --color-border: #E2E8F0;
  --color-surface: #F8FAFC;
}
```

### Login API Function (Form-Data)
```typescript
// src/api/auth.ts
import { apiClient } from './client';

export async function loginUser(email: string, password: string) {
  const params = new URLSearchParams();
  params.append('username', email); // OAuth2 form uses "username"
  params.append('password', password);

  const { data } = await apiClient.post('/api/v1/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data; // { access_token, token_type }
}
```

### TypeScript Types from Backend Schemas
```typescript
// src/api/types.ts
export interface SearchResult {
  room_type_id: string;
  name: string;
  slug: string;
  description: string;
  photo_url: string | null;
  price_per_night: string; // Decimal as string
  total_price: string;
  currency: string;
  max_adults: number;
  max_children: number;
  bed_config: { type: string; count: number }[];
  amenity_highlights: string[];
  available_count: number;
  total_rooms: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  check_in: string;
  check_out: string;
  guests: number;
}

export interface BookingResponse {
  id: string;
  confirmation_number: string;
  user_id: string;
  room_type_id: string;
  room_id: string | null;
  check_in: string;
  check_out: string;
  guest_count: number;
  status: string; // "pending" | "confirmed" | "checked_in" | "checked_out" | "cancelled" | "no_show"
  total_price: string | null;
  price_per_night: string | null;
  currency: string;
  nightly_breakdown: NightlyRate[] | null;
  guest_first_name: string | null;
  guest_last_name: string | null;
  guest_email: string | null;
  guest_phone: string | null;
  special_requests: string | null;
  expires_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  cancellation_fee: string | null;
  created_at: string;
  updated_at: string;
  // BFF enrichment fields (from /bookings/{id}/details)
  room_type_name?: string;
  room_type_description?: string;
  room_type_photos?: string[];
  room_type_amenities?: string[];
}

export interface CalendarDay {
  date: string;
  rate: string;
  base_amount: string;
  seasonal_multiplier: string;
  weekend_multiplier: string;
  available_count: number;
  total_rooms: number;
  availability_indicator: 'green' | 'yellow' | 'red';
}

export interface UserResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}
```

### Booking Wizard Step Flow
```typescript
// Wizard flow maps to API endpoints:
// Step 1 (Select Room): POST /api/v1/bookings/ -> creates PENDING booking, returns bookingId
// Step 2 (Guest Details): PUT /api/v1/bookings/{id}/guest-details
// Step 3 (Payment): POST /api/v1/bookings/{id}/payment -> confirms booking
// Step 4 (Confirmation): Display only, no API call -- show confirmation number

// On browser refresh:
// 1. Read bookingId from Zustand persist (localStorage)
// 2. GET /api/v1/bookings/{bookingId} to check current status
// 3. Determine step from status:
//    - "pending" + no guest details -> step 2
//    - "pending" + has guest details -> step 3
//    - "confirmed" -> step 4
// 4. Resume wizard at correct step
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| tailwind.config.js | CSS-first @theme config | Tailwind v4 (2025) | No JS config file needed |
| react-router-dom package | react-router package (unified) | React Router v7 (2025) | Single package import |
| Custom fetch wrappers | TanStack Query v5 | 2024 | Automatic cache, refetch, mutations |
| Redux for all state | Zustand (UI) + TanStack Query (server) | 2024-2025 | Clear separation, less boilerplate |
| Zod v3 z.string().email() | Zod v4 z.email() | Zod v4 (2025) | Simplified validators, new API |
| CRA / Webpack | Vite 8 with Rolldown | 2025-2026 | 10-30x faster builds |

**Deprecated/outdated:**
- `tailwind.config.js` -- Tailwind v4 uses CSS `@theme` directive
- `react-router-dom` as separate package -- v7 unified into `react-router`
- `Zod z.object().shape` -- v4 may have API changes, verify resolver compatibility

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest 4.x + @testing-library/react |
| Config file | `frontend/vitest.config.ts` (to be created in Wave 0) |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend && npx vitest run --coverage` |

### Phase Requirements Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFR-01 | Responsive layout renders at mobile/tablet/desktop widths | integration | `cd frontend && npx vitest run src/__tests__/responsive.test.tsx -x` | No - Wave 0 |
| INFR-01 | Navbar shows hamburger on mobile, full nav on desktop | unit | `cd frontend && npx vitest run src/components/layout/__tests__/Navbar.test.tsx -x` | No - Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend && npx vitest run --coverage`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend/vitest.config.ts` -- Vitest configuration
- [ ] `frontend/src/test/setup.ts` -- Testing library setup (jsdom, cleanup)
- [ ] `frontend/src/__tests__/` -- Test directory structure
- [ ] Framework install: `npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom`

## Docker Integration

The frontend can be developed standalone with Vite dev server (port 5173) proxying API calls to gateway (port 8000). For production builds:

```yaml
# Add to docker-compose.yml (later, not this phase)
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "3000:80"
```

For development, just run `npm run dev` in the frontend directory with Vite proxy configured. Backend services must be running via `docker compose up`.

## Open Questions

1. **Zod v4 + @hookform/resolvers compatibility**
   - What we know: @hookform/resolvers 5.2.2 is current. Zod 4.3.6 has API changes from v3.
   - What's unclear: Whether resolvers fully supports Zod v4's new API
   - Recommendation: Test early. If issues arise, pin `@hookform/resolvers/zod` and check their changelog. Fallback: use Zod v3 if v4 causes resolver issues.

2. **shadcn/ui + Tailwind v4 maturity**
   - What we know: shadcn/ui officially supports Tailwind v4.
   - What's unclear: Edge cases with v4 CSS variable naming conventions
   - Recommendation: Run `npx shadcn@latest init` first, verify component rendering before building pages.

3. **Photo URLs source**
   - What we know: Room types have `photo_urls` array stored in the database. MinIO is used for object storage.
   - What's unclear: Whether photo URLs are absolute (pointing to MinIO) or relative
   - Recommendation: Inspect a seeded room type response from the API to determine URL format. May need to construct full MinIO URL on the frontend.

## Sources

### Primary (HIGH confidence)
- Backend schemas: `services/*/app/schemas/*.py` -- exact API contracts
- Gateway endpoints: `services/gateway/app/api/*.py` -- exact BFF surface
- Booking API: `services/booking/app/api/v1/bookings.py` -- exact endpoint signatures
- Auth API: `services/auth/app/api/v1/auth.py` -- exact auth flow
- STACK.md: `.planning/research/STACK.md` -- verified stack decisions
- UI-SPEC: `.planning/phases/05-guest-frontend/05-UI-SPEC.md` -- complete visual contract
- npm registry: All package versions verified via `npm view` on 2026-03-21

### Secondary (MEDIUM confidence)
- Tailwind v4 CSS-first configuration pattern (based on official v4 announcement)
- React Router v7 unified package pattern (based on official changelog)
- Zod v4 API changes (verified version, API details from training data)

### Tertiary (LOW confidence)
- Exact Zod v4 + @hookform/resolvers compatibility (needs runtime verification)
- shadcn/ui init behavior with Tailwind v4 (needs runtime verification)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all versions verified via npm, locked in CONTEXT.md and STACK.md
- Architecture: HIGH -- patterns are standard React + TanStack Query + Zustand, well-established
- API surface: HIGH -- directly read from backend source code
- Pitfalls: HIGH -- identified from actual backend code (form-data login, date types, decimal handling)
- Validation: MEDIUM -- Vitest setup is straightforward but responsive testing approach needs verification

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (30 days -- stable ecosystem)
