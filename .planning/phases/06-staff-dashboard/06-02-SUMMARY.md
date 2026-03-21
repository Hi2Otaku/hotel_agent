---
phase: 06-staff-dashboard
plan: 02
subsystem: ui
tags: [react, vite, tailwindcss, shadcn, zustand, tanstack-query, axios, dark-theme]

requires:
  - phase: 06-01
    provides: BFF endpoints for staff overview, check-in/out, guest search

provides:
  - Staff frontend React project (frontend-staff/) with dark admin theme
  - API client using staff_access_token with JWT interceptor
  - Zustand auth store with STAFF_ROLES validation
  - Sidebar navigation with 6 items (Reports disabled)
  - Login page with staff role validation
  - TanStack Query hooks for bookings, rooms, guests
  - StatusBadge with dark theme colors
  - Protected route infrastructure

affects: [06-03, 06-04]

tech-stack:
  added: [react, react-router, zustand, tanstack-react-query, axios, tailwindcss, shadcn-ui, sonner, lucide-react, zod, react-hook-form, vite]
  patterns: [dark-only theme via CSS variables, staff_access_token localStorage key, BFF API pattern, sidebar + topbar layout]

key-files:
  created:
    - frontend-staff/package.json
    - frontend-staff/vite.config.ts
    - frontend-staff/src/index.css
    - frontend-staff/src/api/client.ts
    - frontend-staff/src/api/types.ts
    - frontend-staff/src/api/bookings.ts
    - frontend-staff/src/api/rooms.ts
    - frontend-staff/src/api/guests.ts
    - frontend-staff/src/stores/authStore.ts
    - frontend-staff/src/stores/sidebarStore.ts
    - frontend-staff/src/hooks/queries/useStaffBookings.ts
    - frontend-staff/src/hooks/queries/useRooms.ts
    - frontend-staff/src/hooks/queries/useGuests.ts
    - frontend-staff/src/components/layout/Sidebar.tsx
    - frontend-staff/src/components/layout/TopBar.tsx
    - frontend-staff/src/components/layout/AppLayout.tsx
    - frontend-staff/src/components/common/StatusBadge.tsx
    - frontend-staff/src/components/common/LoadingSpinner.tsx
    - frontend-staff/src/components/common/EmptyState.tsx
    - frontend-staff/src/pages/LoginPage.tsx
    - frontend-staff/src/App.tsx
  modified: []

key-decisions:
  - "staff_access_token localStorage key separates staff auth from guest auth"
  - "Always-dark theme via CSS variables in :root (no .dark class toggle needed)"
  - "Staff frontend on port 5174 to avoid conflict with guest frontend on 5173"
  - "shadcn sonner simplified to remove next-themes dependency (always dark)"
  - "JWT payload decoded client-side to check role before storing token"

patterns-established:
  - "Dark admin theme: CSS variables define dark colors as defaults, no light mode"
  - "Staff auth flow: OAuth2 login -> JWT decode -> STAFF_ROLES check -> store or reject"
  - "Collapsible sidebar: NavItem interface with disabled flag, tooltip on collapse/disabled"
  - "AppLayout: sidebar + topbar wrapper with skip-to-content and Outlet for pages"

requirements-completed: [STAF-01, STAF-02, STAF-03, STAF-04]

duration: 7min
completed: 2026-03-21
---

# Phase 6 Plan 02: Staff Frontend Scaffold Summary

**Complete frontend-staff React app with dark admin theme, sidebar navigation, API layer, auth store with role validation, and login page**

## What Was Built

### Task 1: Project scaffold with dependencies, dark theme, and API layer
- Created Vite + React + TypeScript project (`frontend-staff/`) on port 5174
- Installed 20 shadcn/ui components (button, card, sidebar, dialog, table, etc.)
- Dark admin theme CSS variables: slate-900 background, teal accent (#0F766E)
- API client using `staff_access_token` key with 401 redirect interceptor
- API modules for bookings (staff CRUD, BFF check-in/out), rooms (board, status), guests (search, profile)
- Zustand auth store with `STAFF_ROLES` array and `isStaff()` validation
- Zustand sidebar store with collapse and mobile state
- TanStack Query hooks with cache invalidation (check-in/out invalidates bookings + rooms + overview)
- Vitest configured with jsdom and Node 25 localStorage polyfill

### Task 2: Layout components, login page, and router
- Collapsible sidebar with logo, 6 nav items (Reports disabled with tooltip), staff avatar/role, logout
- TopBar with page title, mobile hamburger, notification bell placeholder, avatar dropdown
- AppLayout with skip-to-content link and responsive sidebar/content layout
- LoginPage with email/password form, OAuth2 submission, JWT role validation
- StatusBadge with dark theme rgba colors per booking status
- LoadingSpinner and EmptyState common components
- Protected routes redirecting unauthenticated users to /login
- Placeholder pages for all 6 routes

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created use-mobile hook for shadcn sidebar dependency**
- Found during: Task 1
- Issue: shadcn sidebar component imports `@/hooks/use-mobile` which wasn't in the plan
- Fix: Created the hook replicating guest frontend pattern
- Files modified: frontend-staff/src/hooks/use-mobile.ts

**2. [Rule 3 - Blocking] Fixed shadcn sonner circular import and next-themes dependency**
- Found during: Task 1
- Issue: shadcn sonner component had circular self-import and used next-themes (not needed for always-dark app)
- Fix: Rewrote sonner to import directly from 'sonner' package with hardcoded dark theme
- Files modified: frontend-staff/src/components/ui/sonner.tsx

**3. [Rule 3 - Blocking] Fixed shadcn component installation path**
- Found during: Task 1
- Issue: shadcn CLI installed components to `frontend-staff/@/components/ui/` instead of `frontend-staff/src/components/ui/`
- Fix: Moved files to correct location and removed the `@/` directory
- Files modified: frontend-staff/src/components/ui/*.tsx

## Verification

- `npm run build` succeeds (288ms build time)
- API client uses `staff_access_token` key throughout
- Auth store includes `STAFF_ROLES` validation
- StatusBadge uses dark theme rgba colors from UI-SPEC
- All 6 routes defined with placeholder pages
- Sidebar has all nav items with Reports disabled

## Self-Check: PASSED

All key files exist. Commits 85622e7 and d8f4c8f verified.
