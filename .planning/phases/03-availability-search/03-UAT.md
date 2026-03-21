---
status: complete
phase: 03-availability-search
source: 03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-03-SUMMARY.md
started: 2026-03-21T11:20:00Z
updated: 2026-03-21T11:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Search available rooms
expected: GET /api/v1/search/availability?check_in=...&check_out=...&guests=2 returns 200 with results
result: pass

### 2. Room type detail with pricing
expected: GET /api/v1/search/room-types/{id}?check_in=...&check_out=... returns 200 with pricing
result: issue
reported: "HTTP 500: MultipleResultsFound in get_seasonal_multiplier — scalar_one_or_none fails when overlapping seasonal rates exist for the same room type and date. Query returns multiple rows but code expects 0 or 1."
severity: major

### 3. Pricing calendar
expected: GET /api/v1/search/calendar?room_type_id=...&start_date=...&end_date=... returns 200
result: pass

## Summary

total: 3
passed: 2
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "Room type detail endpoint returns pricing for selected dates"
  status: failed
  reason: "User reported: HTTP 500 - MultipleResultsFound in get_seasonal_multiplier when overlapping seasonal rates exist"
  severity: major
  test: 2
  root_cause: "get_seasonal_multiplier in services/room/app/services/rate.py uses scalar_one_or_none() but query can return multiple overlapping seasonal rates for the same room_type_id and date. Need to use .first() or add ordering and limit."
  artifacts:
    - path: "services/room/app/services/rate.py"
      issue: "get_seasonal_multiplier query returns multiple rows when seasonal rates overlap"
  missing:
    - "Use .first() with ordering (e.g., latest created) instead of scalar_one_or_none() in get_seasonal_multiplier"
