---
status: complete
phase: 04-booking-engine
source: 04-01-SUMMARY.md, 04-02-SUMMARY.md, 04-03-SUMMARY.md
started: 2026-03-21T11:20:00Z
updated: 2026-03-21T11:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Create booking
expected: POST /api/v1/bookings/ with room_type_id, dates, guest_count returns 201 with booking and confirmation number
result: issue
reported: "HTTP 500: FOR UPDATE is not allowed with aggregate functions. The availability check query uses SELECT count(*) ... FOR UPDATE which PostgreSQL forbids. Booking creation fails for all room types."
severity: blocker

### 2. Confirmation number format
expected: Confirmation number starts with HB- and is 9 chars (HB-XXXXXX)
result: issue
reported: "Cannot verify — booking creation fails (blocked by test 1)"
severity: blocker

### 3. Mock payment
expected: POST /api/v1/bookings/{id}/payment with card details confirms booking
result: issue
reported: "Cannot verify — no booking to pay (blocked by test 1)"
severity: blocker

### 4. List my bookings
expected: GET /api/v1/bookings/ with guest token returns 200
result: pass

### 5. Modify booking
expected: PUT /api/v1/bookings/{id}/modify with new dates returns 200
result: issue
reported: "Cannot verify — no confirmed booking to modify (blocked by test 1)"
severity: blocker

### 6. Cancel booking
expected: POST /api/v1/bookings/{id}/cancel returns 200, status changes to cancelled
result: issue
reported: "Cannot verify — no confirmed booking to cancel (blocked by test 1)"
severity: blocker

### 7. Cancellation policy
expected: GET /api/v1/bookings/{id}/cancellation-policy returns 200
result: issue
reported: "Cannot verify — no booking exists (blocked by test 1)"
severity: blocker

## Summary

total: 7
passed: 1
issues: 6
pending: 0
skipped: 0

## Gaps

- truth: "Guest can create a booking by selecting room type and dates"
  status: failed
  reason: "HTTP 500: FOR UPDATE is not allowed with aggregate functions in availability check query"
  severity: blocker
  test: 1
  root_cause: "Booking service availability check uses SELECT count(*) FROM bookings WHERE ... FOR UPDATE. PostgreSQL does not allow FOR UPDATE with aggregate functions. The FOR UPDATE lock must be on the row-level SELECT, not on a count query."
  artifacts:
    - path: "services/booking/app/services/booking.py"
      issue: "Availability check query combines count() with FOR UPDATE"
  missing:
    - "Remove FOR UPDATE from count query, or restructure to lock individual rows then count in application code"

- truth: "Mock payment, modify, cancel, cancellation policy all work"
  status: failed
  reason: "All blocked by booking creation failure — cascade failure"
  severity: blocker
  test: 3
  root_cause: "Same as test 1 — booking creation fails so no bookings exist to test downstream flows"
  artifacts: []
  missing:
    - "Fix booking creation first, then all downstream tests should pass"
