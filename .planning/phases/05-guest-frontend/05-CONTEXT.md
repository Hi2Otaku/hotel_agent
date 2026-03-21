# Phase 5: Guest Frontend - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

React SPA for the complete guest booking journey: landing page with search, room search results with filters, booking wizard (4-step with state persistence), guest account (register, login, password reset), booking management (view, cancel, modify), and pricing calendar. Fully responsive, mobile-first design. Consumes the gateway BFF API.

</domain>

<decisions>
## Implementation Decisions

### Visual Style & Layout
- Clean & modern aesthetic: white space, subtle shadows, minimal borders (Airbnb/Booking.com style)
- Landing page: split layout — left: search card form, right: rotating resort photos
- Top navbar: fixed, with logo, search link, pricing calendar, My Bookings, Login/Profile
- Simple footer: contact info, quick links, "Powered by HotelBook"
- Color palette and typography: Claude's discretion (something befitting a clean beach resort)

### Booking Wizard UX
- Sidebar steps: steps listed in left sidebar, content on right — 1. Room → 2. Details → 3. Payment → 4. Confirmed
- Free back navigation: guests can go back to any previous step, data preserved
- Booking summary: collapsible panel (top on mobile), showing room type, dates, nights, price breakdown
- Browser refresh resilience: booking ID saved to URL/localStorage — guest resumes where they left off
- State persistence across steps: wizard maintains all data without loss

### Search & Results Display
- Search form: card-style with stacked inputs (check-in, check-out, guests, search button)
- Filters: slide-out drawer triggered by filter icon — mobile-friendly
- Result cards: large photo cards with room type name, price, amenity tags, book button (Airbnb style)
- Date picker: Claude's discretion (calendar popup, whatever works best with shadcn/ui)
- Pricing calendar: integrated page with room type filter and click-to-search dates

### Account & Auth Pages
- Login/register: dedicated pages (/login, /register) — standard, SEO-friendly
- My Bookings: card list — each booking as a card with dates, room type, status badge, action buttons
- Booking detail page shows:
  - Full summary: confirmation number, dates, room type photo, price breakdown, guest info
  - Status timeline: visual progression (Booked → Confirmed → Checked In → Checked Out)
  - Action buttons: Cancel and Modify (disabled when not applicable based on status)
  - Cancellation policy: whether free cancellation is still available

### Loading & Error States
- Loading: skeleton loaders for content areas (Claude's discretion on exact implementation)
- Errors: toast notifications for API errors, inline validation for forms
- Empty states: friendly messages with actionable CTAs (e.g., "No bookings yet — find your room")

### Claude's Discretion
- Color palette and typography choices
- Date picker component choice (shadcn/ui DatePicker or custom)
- Exact responsive breakpoints and mobile adaptations
- Animation/transition style
- Loading skeleton design
- Toast notification library choice
- How the pricing calendar integrates with search
- Room photo gallery/carousel implementation

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project research (stack)
- `.planning/research/STACK.md` — React 19, Vite 8, Tailwind CSS 4, shadcn/ui, TanStack Query, Zustand, React Router v7

### Gateway BFF API (consumed by frontend)
- `services/gateway/app/api/search.py` — Search BFF endpoints: /search/availability, /search/room-types/{id}, /search/calendar
- `services/gateway/app/api/booking.py` — Booking BFF endpoints: enrichment/aggregation
- `services/gateway/app/api/proxy.py` — Auth proxy: /api/v1/auth/* (register, login, me, password-reset)
- `services/gateway/app/main.py` — All BFF routes registered before catch-all proxy

### Auth API
- `services/auth/app/api/v1/auth.py` — Register, login (returns JWT), password reset
- `services/auth/app/schemas/auth.py` — Request/response schemas for auth endpoints

### Booking API
- `services/booking/app/api/v1/bookings.py` — Full booking CRUD: create, guest details, payment, list, cancel, modify
- `services/booking/app/schemas/booking.py` — BookingCreate, GuestDetailsSubmit, BookingResponse, BookingModifyRequest
- `services/booking/app/schemas/payment.py` — PaymentSubmit, PaymentResponse

### Search API
- `services/room/app/schemas/availability.py` — SearchResult, SearchResponse, RoomTypeDetail, CalendarDay, CalendarResponse

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No frontend code exists yet — greenfield React app
- Gateway BFF provides all API endpoints the frontend needs
- All API schemas are defined in Pydantic and can inform TypeScript types

### Established Patterns
- Gateway is the single entry point for all frontend API calls
- JWT stored client-side for authenticated requests (24-hour hard expiry)
- On expired token: redirect to login, return to original URL after re-login (from Phase 1 context)
- Search endpoints are public (no auth), booking/account endpoints require JWT

### Integration Points
- Frontend served separately (Vite dev server or static build)
- All API calls go to gateway: `http://localhost:8000/api/v1/*`
- Docker Compose can add a frontend container or serve via gateway
- CORS configuration needed on gateway for frontend dev server

</code_context>

<specifics>
## Specific Ideas

- Split layout landing page with card search form — clean modern approach
- Sidebar booking wizard with left steps + right content — spacious, clear progression
- Photo cards for search results — showcases the beach resort Unsplash images
- Status timeline on booking detail — visually compelling, demonstrates CSS/component skills
- Slide-out filter drawer — mobile-first, modern pattern

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-guest-frontend*
*Context gathered: 2026-03-21*
