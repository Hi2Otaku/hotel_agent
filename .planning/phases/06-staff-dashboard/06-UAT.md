---
status: complete
phase: 06-staff-dashboard
source: 06-01-SUMMARY.md, 06-02-SUMMARY.md, 06-03-SUMMARY.md, 06-04-SUMMARY.md
started: 2026-03-21T10:30:00Z
updated: 2026-03-21T11:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Staff frontend dev server starts on port 5174. npm run build succeeds.
result: pass

### 2. Staff Login API
expected: POST /api/v1/auth/login with admin@hotel.local/admin123 returns JWT with role=admin
result: pass

### 3. Staff BFF Overview
expected: GET /api/v1/staff/overview returns arrivals_count, departures_count, occupancy_percent, rooms_to_clean
result: pass

### 4. Staff Bookings List
expected: GET /api/v1/bookings/staff/ returns paginated bookings list
result: pass

### 5. Today's Arrivals/Departures
expected: GET /api/v1/bookings/staff/today returns arrivals and departures arrays
result: pass

### 6. Room Status Board
expected: GET /api/v1/rooms/board returns floors with rooms grouped by floor, each with status
result: pass

### 7. Room Status Transition
expected: POST /api/v1/rooms/{id}/status with new_status changes room status and returns updated room
result: pass

### 8. Guest Search
expected: GET /api/v1/staff/guests/search?q=guest returns matching users
result: pass

### 9. Guest Search via Auth
expected: GET /api/v1/users/search?q=admin returns matching users with role info
result: pass

### 10. RBAC - Staff Endpoints Protected
expected: Staff endpoints return 401/403 without valid staff token
result: pass

### 11. Staff Frontend Build
expected: npm run build in frontend-staff/ succeeds
result: pass

### 12. Staff Frontend Pages Exist
expected: OverviewPage, ReservationsPage, CheckInOutPage, RoomStatusPage, GuestProfilePage, LoginPage all exist
result: pass

### 13. Check-In Flow (API)
expected: POST /api/v1/staff/check-in/{booking_id} assigns room and updates booking status to checked_in
result: skipped
reason: No bookings exist — blocked by Phase 4 booking creation bug (FOR UPDATE + count)

### 14. Check-Out Flow (API)
expected: POST /api/v1/staff/check-out/{booking_id} updates booking and room status
result: skipped
reason: No bookings exist — blocked by Phase 4 booking creation bug

### 15. Guest Profile with Booking History
expected: GET /api/v1/staff/guests/{user_id}/profile returns guest info with booking history
result: skipped
reason: No bookings exist — booking history would be empty, meaningful test blocked by Phase 4

## Summary

total: 15
passed: 12
issues: 0
pending: 0
skipped: 3

## Gaps

[none — skipped tests are blocked by Phase 4 booking creation bug, not Phase 6 issues]
