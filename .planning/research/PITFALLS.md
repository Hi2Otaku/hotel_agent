# Pitfalls Research

**Domain:** Hotel Reservation System (single-property, FastAPI + React + PostgreSQL)
**Researched:** 2026-03-20
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Double-Booking via Race Conditions

**What goes wrong:**
Two guests simultaneously request the same room for overlapping dates. Both read that the room is available, both proceed to book, and both get confirmations. The second booking overwrites or conflicts with the first. This is the single most damaging bug a reservation system can have.

**Why it happens:**
Developers check availability with a SELECT query, then INSERT the reservation in a separate step without any locking or atomic guarantees. In FastAPI's async environment, concurrent requests are the norm, not the exception -- this race condition will happen, not might happen.

**How to avoid:**
Use one of two PostgreSQL locking strategies:

1. **Pessimistic locking (recommended for this project's scale):** Use `SELECT ... FOR UPDATE` within a transaction to lock the room rows being checked. Other transactions wait until the lock is released.
   ```sql
   BEGIN;
   SELECT id FROM rooms WHERE id = 123 FOR UPDATE;
   -- Check availability for date range
   -- Insert reservation if available
   COMMIT;
   ```

2. **Optimistic locking (alternative):** Add a `version` column to the room/inventory table. Read the version, attempt the update with `WHERE version = <read_version>`. If zero rows affected, another transaction won. Retry or fail gracefully.

3. **Atomic conditional update (simplest):** For inventory-count based models, use `UPDATE inventory SET available_count = available_count - 1 WHERE room_type_id = X AND date = Y AND available_count > 0`. The WHERE clause makes it atomic -- only the first concurrent request succeeds.

For a single-property portfolio project, pessimistic locking is the right choice: simpler to reason about, sufficient at this scale, and demonstrates understanding of the problem.

**Warning signs:**
- Availability check and reservation insert are in separate, non-transactional database calls
- No `FOR UPDATE` or version checks anywhere in the booking code
- Tests only test sequential bookings, never concurrent ones
- Using SQLAlchemy sessions without explicit transaction boundaries

**Phase to address:**
Core booking flow phase. This must be designed correctly from the start -- retrofitting concurrency control onto a naive implementation requires rewriting the entire booking path.

---

### Pitfall 2: Broken Date Range Logic ("Night vs. Day" Problem)

**What goes wrong:**
The system confuses check-in dates, check-out dates, and "nights stayed." A guest books March 10-12, expecting 2 nights (nights of the 10th and 11th). But the system either: (a) counts 3 days and charges for 3 nights, (b) marks March 12 as occupied when it should be available for new check-ins, or (c) creates off-by-one errors in availability calculations that cascade into phantom unavailability or double-bookings.

**Why it happens:**
Hotel dates use a "night" model: check-in date is inclusive, check-out date is exclusive. A reservation for March 10-12 means the guest occupies the room on nights of March 10 and March 11 and checks out on March 12 morning. This is a half-open interval `[check_in, check_out)`. Developers who use inclusive ranges `[check_in, check_out]` or who think in "days" instead of "nights" get this wrong.

**How to avoid:**
- Model all date ranges as half-open intervals: `[check_in, check_out)` where check_in is inclusive and check_out is exclusive
- Use PostgreSQL's `daterange` type with the `&&` (overlaps) operator for availability queries:
  ```sql
  SELECT COUNT(*) FROM reservations
  WHERE room_id = X
  AND daterange(check_in, check_out) && daterange('2026-03-10', '2026-03-12');
  ```
- Enforce `check_out > check_in` as a database constraint (CHECK constraint)
- Calculate nights as `check_out - check_in` (simple date subtraction)
- Never store "number of nights" as a separate field -- derive it from the dates
- Write explicit tests: a checkout on March 12 and a check-in on March 12 must NOT conflict

**Warning signs:**
- Availability queries use `BETWEEN` with inclusive endpoints
- Code calculates nights by adding 1 to date differences
- Tests do not cover back-to-back bookings (checkout day = next check-in day)
- Frontend and backend disagree on what the date range means

**Phase to address:**
Database schema and data model phase. The date range convention must be established before any availability or pricing logic is built. Document the convention in code comments and enforce it with database constraints.

---

### Pitfall 3: Booking State Machine with Missing or Invalid Transitions

**What goes wrong:**
Reservations get stuck in limbo states, or reach states they should not be in. Examples: a "pending" reservation never expires and blocks the room forever. A "cancelled" reservation somehow gets checked in. A "checked-out" reservation gets cancelled and triggers a refund. The booking lifecycle becomes a source of data corruption.

**Why it happens:**
Developers implement booking status as a simple string field and scatter transition logic across multiple endpoints. Without an explicit state machine, there is no single source of truth for which transitions are legal. Edge cases (payment timeout, partial cancellation, no-show) are handled ad-hoc.

**How to avoid:**
Define an explicit state machine with these states and transitions:

```
PENDING --> CONFIRMED    (payment succeeds)
PENDING --> CANCELLED    (payment fails, timeout, or user cancels)
CONFIRMED --> CHECKED_IN (staff marks guest arrival)
CONFIRMED --> CANCELLED  (user cancels before check-in, may trigger refund)
CHECKED_IN --> COMPLETED (staff marks checkout)
CONFIRMED --> NO_SHOW    (guest never arrives after check-in date)
```

Implementation:
- Use a PostgreSQL ENUM type for status
- Create a single `transition_booking_state(booking_id, new_state)` function that validates the transition is legal before applying it
- Add a `status_history` table that logs every transition with timestamp and actor (guest, staff, system)
- PENDING reservations must have an expiration timestamp. A background task or database trigger releases them after 15-30 minutes if payment is not completed
- Never allow direct status updates via raw SQL or ORM -- always go through the transition function

**Warning signs:**
- Booking status is updated with direct `UPDATE booking SET status = 'X'` without validation
- No expiration mechanism for pending bookings
- No audit trail for state changes
- Edge cases like no-show and payment timeout are not handled

**Phase to address:**
Core booking flow phase, refined during staff dashboard phase (which adds check-in/check-out transitions). The state machine should be the first thing built in the booking domain.

---

### Pitfall 4: Pricing Calculation Inconsistencies (Quote vs. Charge Mismatch)

**What goes wrong:**
The price shown during search does not match the price charged at booking confirmation. Or worse: modifying a reservation recalculates the price differently than the original booking because a seasonal rate changed between booking time and modification time.

**Why it happens:**
Price calculation is duplicated in multiple places (search results, booking summary, confirmation email, admin dashboard) and the implementations drift. Seasonal rates are looked up at calculation time rather than snapshotted at booking time. Taxes or fees are added inconsistently.

**How to avoid:**
- Create a single `calculate_price(room_type, check_in, check_out)` function used everywhere. No exceptions. No inline price math.
- The function should return a detailed breakdown: per-night rates, any discounts, taxes, and total
- When a booking is confirmed, snapshot the price breakdown into the reservation record. Never recalculate a confirmed booking's price from current rates -- use the stored snapshot.
- Store per-night rate on the reservation (a `reservation_nights` table with `date, rate` rows) so the math is auditable
- For seasonal pricing: rates are looked up by date, so each night in a stay can have a different rate. The price function must iterate over each night, not multiply a single rate by number of nights.

**Warning signs:**
- Price calculation logic appears in more than one file or function
- No price snapshot stored on confirmed bookings
- Seasonal rate changes retroactively affect existing reservations
- Tests do not cover stays that span rate boundaries (e.g., 2 nights at regular rate + 1 night at holiday rate)

**Phase to address:**
Rate management phase. The pricing function should be built and thoroughly tested before the booking flow consumes it. The snapshot mechanism must be in place when the booking flow is built.

---

### Pitfall 5: Availability Calculation That Does Not Scale or Is Wrong

**What goes wrong:**
Availability queries either return incorrect results (showing rooms as available when they are booked, or vice versa) or become painfully slow as reservation data grows. A common mistake is calculating availability by loading all reservations into application memory and filtering in Python.

**Why it happens:**
Developers think of availability as "find all bookings, check if any overlap." This works for 10 reservations but degrades with thousands. Another mistake: the availability query does not account for all blocking states (e.g., it checks for CONFIRMED reservations but forgets PENDING ones, leading to double-booking during the payment window).

**How to avoid:**
- Availability must be a single SQL query, not Python-side filtering:
  ```sql
  SELECT r.id FROM rooms r
  WHERE r.room_type_id = :type_id
  AND r.id NOT IN (
    SELECT room_id FROM reservations
    WHERE status IN ('PENDING', 'CONFIRMED', 'CHECKED_IN')
    AND daterange(check_in, check_out) && daterange(:requested_start, :requested_end)
  )
  LIMIT 1;
  ```
- PENDING reservations MUST block availability (otherwise two guests can pay for the same room simultaneously)
- Add a composite index on `(room_id, check_in, check_out)` or use a GiST index on a daterange column for the overlap query
- For room type availability counts (search results), use a COUNT query, not individual room checks
- Test with: adjacent bookings, single-night stays, month-long stays, fully-booked periods

**Warning signs:**
- Availability logic fetches all reservations and filters in Python
- PENDING reservations are not included in availability blocking
- No database index on reservation date columns
- Search becomes slow after seeding a few hundred reservations

**Phase to address:**
Database schema phase (indexes, daterange types) and search/availability phase (query implementation). Must be correct before the booking flow is built.

---

### Pitfall 6: Mixing Sync and Async in FastAPI with SQLAlchemy

**What goes wrong:**
The FastAPI application uses `async def` endpoints but calls synchronous SQLAlchemy operations, which blocks the event loop. Under concurrent load (even modest -- 10 simultaneous users), the entire application freezes because a single synchronous database call blocks all other async operations waiting in the event loop.

**Why it happens:**
SQLAlchemy's traditional (1.x style) API is synchronous. Developers define endpoints as `async def` (because FastAPI documentation encourages it) but use `Session` instead of `AsyncSession`. FastAPI does not warn about this mismatch at startup -- it only manifests under load.

**How to avoid:**
- Use SQLAlchemy 2.0 with `create_async_engine` and `AsyncSession` throughout. Do not mix sync and async sessions.
- Use `asyncpg` as the PostgreSQL driver (not `psycopg2` which is synchronous)
- If you must use synchronous code (e.g., a library without async support), use `def` (not `async def`) for that endpoint -- FastAPI will run it in a thread pool automatically
- Never call `session.execute()` from a sync Session inside an `async def` endpoint
- Set up a proper async session dependency:
  ```python
  async def get_db():
      async with async_session_maker() as session:
          yield session
  ```

**Warning signs:**
- Import of `Session` instead of `AsyncSession` in an async codebase
- `psycopg2` in requirements instead of `asyncpg`
- Application works fine in development (single user) but hangs under any concurrent load
- Database connection pool exhaustion errors in logs

**Phase to address:**
Project setup / foundation phase. The async database configuration must be correct from day one. Retrofitting async onto a sync SQLAlchemy setup requires rewriting every database interaction.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Storing availability as a boolean on the room table instead of computing from reservations | Simple queries | Cannot handle date-range queries; must be kept in sync manually; breaks for any multi-day booking | Never -- use reservation-based availability from the start |
| Hardcoding tax rates and fees in the pricing function | Ship faster | Every rate change requires a code deploy; no audit trail | MVP only, but extract to config/database in the next phase |
| Skipping the reservation expiration mechanism for PENDING bookings | Avoids background task complexity | Rooms get permanently locked by abandoned carts | Never -- even a simple cron job is better than nothing |
| Using SQLite for local development instead of PostgreSQL | No setup required | Daterange types, FOR UPDATE, and GiST indexes are PostgreSQL-specific; behavior differences will hide bugs | Never for this project -- use PostgreSQL from the start via Docker |
| No booking status history table | One less table to manage | Cannot debug state issues, no audit trail, impossible to answer "who cancelled this and when?" | MVP only, add before staff dashboard is built |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Mock payment (simulated Stripe) | Making the mock always succeed, so error paths are never tested | Mock should simulate failures (card declined, timeout, insufficient funds) with configurable failure rates. Test the PENDING-to-CANCELLED path. |
| Email confirmation (mock) | Sending emails synchronously in the booking endpoint, causing slow response times | Queue email sends as background tasks (`BackgroundTasks` in FastAPI or a simple task queue). Even mock emails should be async. |
| Frontend date picker | Using JavaScript Date objects which include time zones, causing off-by-one date errors when the browser timezone differs from the server | Use date-only strings (YYYY-MM-DD) in API requests. Never pass JavaScript Date objects directly. Use a date library (date-fns) that handles date-only operations. |
| CORS configuration | Allowing all origins in development, forgetting to restrict in production | Configure CORS properly from the start with explicit allowed origins. Use environment variables to switch between dev and prod origins. |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| N+1 queries in room listing (loading each room's amenities, images, rates separately) | Search page takes 2-5 seconds; database shows hundreds of queries per page load | Use SQLAlchemy `selectinload` or `joinedload` for related data. Profile with SQLAlchemy echo mode. | 20+ rooms with 5+ related tables |
| No pagination on reservation listing (staff dashboard) | Dashboard loads slowly or times out as bookings accumulate | Add LIMIT/OFFSET or cursor-based pagination from the start. Never return unbounded result sets. | 500+ reservations |
| Recalculating availability for every room on every search | Search takes 1+ seconds; database CPU spikes during peak hours | Use efficient SQL with proper indexes. For a single property (maybe 50-200 rooms), a well-indexed query is fast enough without caching. | 1000+ reservations with no indexes |
| Loading full reservation objects when only counts are needed | Excessive memory usage, slow availability checks | Use COUNT queries and projections. Only load full objects when displaying details. | 100+ concurrent searches |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing reservation IDs as sequential integers in URLs | Guests can enumerate other guests' reservations by incrementing the ID | Use UUIDs for public-facing reservation identifiers. Keep integer IDs for internal database foreign keys. |
| No authorization check on reservation endpoints (only authentication) | Authenticated guest A can view/modify/cancel guest B's reservation | Every reservation endpoint must verify that the requesting user owns the reservation (or is staff). Middleware is not enough -- check ownership in the query itself: `WHERE id = :booking_id AND guest_id = :current_user_id`. |
| Accepting check-in/check-out dates from the frontend without server-side validation | Guests can book rooms with past dates, checkout before checkin, or zero-night stays | Validate all dates server-side: check_in >= today, check_out > check_in, stay length within allowed bounds. Frontend validation is UX only, not security. |
| Staff role escalation via API manipulation | A guest account could access staff endpoints if role checks are only on the frontend | Implement role-based access control as FastAPI dependencies. Staff endpoints must verify the user's role server-side. |
| Price manipulation by sending price in the booking request | Guest sends a lower price, system accepts it | Never accept price from the client. Always recalculate server-side using the same pricing function. The client only sends room type + dates. |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing "no rooms available" without explanation | Guest has no idea if the hotel is fully booked, or if they should try different dates | Show a message like "No rooms available for these dates. Try adjusting your dates or room type." Suggest nearby available dates if possible. |
| Calendar does not visually distinguish past dates, booked dates, and available dates | Guest wastes time selecting dates that are not bookable, leading to frustration | Disable past dates. Show booked dates as greyed out or with a visual indicator. Highlight available date ranges. |
| Requiring account creation before showing prices or availability | High bounce rate -- guests leave before seeing if the hotel meets their needs | Allow anonymous search and availability checks. Only require login/registration at the booking confirmation step. |
| Confirmation page does not clearly show cancellation policy | Guests book without understanding the cancellation terms, leading to disputes | Display cancellation policy prominently on the booking confirmation page and in the confirmation email. |
| No loading state during booking submission | Guest clicks "Book" multiple times thinking nothing happened, potentially creating duplicate reservations | Show a loading spinner immediately. Disable the submit button after first click. Implement idempotency on the backend (idempotency key in the request). |

## "Looks Done But Isn't" Checklist

- [ ] **Availability search:** Does it block rooms in PENDING state (payment in progress)? If not, two guests can pay for the same room simultaneously.
- [ ] **Booking confirmation:** Does it store a price snapshot, or will a rate change alter the confirmed booking's price?
- [ ] **Date handling:** Can a guest check in on the same day another checks out for the same room? (They must be able to.)
- [ ] **Cancellation:** Does cancelling a reservation actually release the room back to available inventory?
- [ ] **Pending expiration:** Do abandoned bookings (started but never paid) eventually expire and release the room?
- [ ] **Concurrent booking test:** Have you tested two simultaneous booking attempts for the last available room? (Manual testing is not sufficient -- write an automated concurrent test.)
- [ ] **Multi-night pricing:** Does a 3-night stay spanning a rate change correctly apply different rates to different nights?
- [ ] **Timezone consistency:** Are dates stored as date-only (no timezone) in PostgreSQL? Mixing timestamps with dates causes off-by-one errors.
- [ ] **Staff operations:** Can staff check in a guest whose reservation is in CANCELLED state? (They must not be able to.)
- [ ] **Idempotency:** Does double-clicking "Confirm Booking" create two reservations?

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Double-booking discovered in production | HIGH | Requires manual guest notification and rebooking. Add database constraint (`EXCLUDE USING gist`) to prevent recurrence. Audit all existing reservations for conflicts. |
| Wrong date range convention (inclusive vs exclusive) | HIGH | Requires auditing every query, every test, and potentially migrating existing data. Prevention is dramatically cheaper than fixing. |
| Missing state machine (ad-hoc status updates) | MEDIUM | Introduce transition function, audit existing data for invalid states, backfill status history. Can be done incrementally. |
| Sync/async mismatch in FastAPI | MEDIUM | Replace `Session` with `AsyncSession` and `psycopg2` with `asyncpg` throughout. Every database interaction must be updated. Easier if caught early. |
| No price snapshots on bookings | MEDIUM | Add snapshot columns/table, backfill existing bookings with current rates (best effort -- historical accuracy is lost). |
| Sequential integer IDs exposed publicly | LOW | Add UUID column, update API routes, keep integer IDs internally. Migration is straightforward but touches every endpoint. |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Double-booking race conditions | Core booking flow | Automated concurrent booking test passes; database locks visible in code review |
| Broken date range logic | Database schema / data model | Back-to-back booking test passes; CHECK constraint on check_out > check_in exists |
| Missing state machine | Core booking flow | Transition function exists; no direct status UPDATE outside it; status history table populated |
| Pricing inconsistencies | Rate management | Single pricing function; snapshot stored on booking; multi-rate stay test passes |
| Availability calculation errors | Search / availability | PENDING blocks availability; SQL-based (not Python-side); index exists on date columns |
| Sync/async mismatch | Project foundation / setup | AsyncSession and asyncpg in use; no sync Session imports; load test with 10 concurrent users passes |
| Price manipulation via API | Core booking flow | No price field accepted in booking request body; server recalculates |
| Reservation ID enumeration | Database schema / API design | UUIDs used in all public-facing URLs |
| Duplicate submission (no idempotency) | Core booking flow | Idempotency key in booking request; double-click test passes |
| Pending reservation never expires | Core booking flow | Background task or scheduled job releases PENDING bookings after timeout; test verifies expiration |

## Sources

- [How to Solve Race Conditions in a Booking System - HackerNoon](https://hackernoon.com/how-to-solve-race-conditions-in-a-booking-system)
- [Design Hotel Booking System: A Step-by-Step Guide - System Design Handbook](https://www.systemdesignhandbook.com/guides/design-hotel-booking-system/)
- [Solving Double Booking at Scale: System Design Patterns - ITNext](https://itnext.io/solving-double-booking-at-scale-system-design-patterns-from-top-tech-companies-4c5a3311d8ea)
- [SQLAlchemy Database Locks Using FastAPI - Medium](https://medium.com/@mojimich2015/sqlalchemy-database-locks-using-fastapi-a-simple-guide-3e7dcd552d87)
- [The Concurrency Trap in FastAPI - DataSci Ocean](https://datasciocean.com/en/other/fastapi-race-condition/)
- [Hotel Reservation Schema Design (PostgreSQL) - DEV Community](https://dev.to/chandra179/hotel-reservation-schema-design-postgresql-3i9j)
- [ByteByteGo Hotel Reservation System Design](https://bytebytego.com/courses/system-design-interview/hotel-reservation-system)
- [Locking mechanisms for data integrity - FastAPI/SQLModel GitHub Issue](https://github.com/fastapi/sqlmodel/issues/307)

---
*Pitfalls research for: HotelBook - Hotel Reservation System*
*Researched: 2026-03-20*
