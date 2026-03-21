---
phase: 03-availability-search
plan: 01
subsystem: database, api
tags: [sqlalchemy, rabbitmq, aio-pika, availability, projection, cqrs]

# Dependency graph
requires:
  - phase: 02-room-management
    provides: "Room, RoomType, BaseRate models and rate calculation engine"
provides:
  - "ReservationProjection SQLAlchemy model for booking event projections"
  - "Alembic migration 002 with reservation_projections table and indexes"
  - "RabbitMQ event consumer for booking.events exchange"
  - "Availability service with overlap detection and search queries"
  - "overbooking_pct column on RoomType model"
affects: [03-availability-search, 04-booking-flow]

# Tech tracking
tech-stack:
  added: [aio-pika (existing shared dep)]
  patterns: [CQRS projection via event consumer, half-open interval overlap detection, upsert-by-business-key pattern]

key-files:
  created:
    - services/room/app/models/reservation.py
    - services/room/app/services/event_consumer.py
    - services/room/app/services/availability.py
    - services/room/alembic/versions/002_reservation_projection.py
    - tests/room/test_event_consumer.py
  modified:
    - services/room/app/models/room_type.py
    - services/room/app/models/__init__.py
    - services/room/app/core/config.py
    - services/room/app/main.py

key-decisions:
  - "Upsert by booking_id for idempotent event processing (query then insert/update, not ON CONFLICT)"
  - "Half-open interval overlap: check_in < requested_check_out AND check_out > requested_check_in"
  - "Search result dict keys use photo_url (singular) and amenity_highlights to match Plan 02 SearchResult schema"
  - "Lazy imports in event consumer tests to handle multi-service pythonpath namespace collision"

patterns-established:
  - "CQRS projection pattern: events from booking service upserted into room service's reservation_projections table"
  - "message.process() async context manager for automatic ack/nack in aio-pika consumers"
  - "Availability overlap detection using BLOCKING_STATUSES set (pending, confirmed, checked_in)"
  - "effective_capacity formula: physical_count * (1 + overbooking_pct / 100)"

requirements-completed: [ROOM-02]

# Metrics
duration: 7min
completed: 2026-03-21
---

# Phase 03 Plan 01: Reservation Projection & Availability Summary

**ReservationProjection CQRS model with RabbitMQ event consumer, half-open interval availability queries, and overbooking support**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-21T05:27:23Z
- **Completed:** 2026-03-21T05:34:44Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- ReservationProjection model with booking_id (unique), room_type_id, room_id (nullable), dates, status, and guest_count
- Alembic migration 002 with composite availability index and partial room-dates index
- RabbitMQ event consumer with idempotent upsert processing and auto-ack/nack via message.process()
- Availability service with get_available_count (overlap detection), search_available_room_types (filtering/sorting/pricing), effective_capacity, and compute_sort_score
- overbooking_pct Decimal column on RoomType for capacity buffer calculation
- 4 unit tests for event consumer (insert, update, idempotent, room_id assignment)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ReservationProjection model, overbooking_pct on RoomType, and Alembic migration** - `fe7a1a8` (feat)
2. **Task 2: Create RabbitMQ event consumer, availability query service, and event consumer tests** - `90fce94` (feat)

## Files Created/Modified
- `services/room/app/models/reservation.py` - ReservationProjection SQLAlchemy model with composite and partial indexes
- `services/room/app/services/event_consumer.py` - RabbitMQ consumer: handle_booking_event (upsert), start_event_consumer (exchange/queue setup)
- `services/room/app/services/availability.py` - Availability queries: get_available_count, search_available_room_types, effective_capacity, compute_sort_score
- `services/room/alembic/versions/002_reservation_projection.py` - Migration creating reservation_projections table, indexes, and overbooking_pct column
- `tests/room/test_event_consumer.py` - 4 unit tests for event consumer with mock message processing
- `services/room/app/models/room_type.py` - Added overbooking_pct Mapped[Decimal] column with Numeric(5,2)
- `services/room/app/models/__init__.py` - Added ReservationProjection re-export for Alembic metadata discovery
- `services/room/app/core/config.py` - Added RABBITMQ_URL to Settings class
- `services/room/app/main.py` - Added consumer_task in lifespan with graceful shutdown

## Decisions Made
- Used query-then-upsert pattern (SELECT by booking_id, then INSERT or UPDATE) rather than PostgreSQL ON CONFLICT for clearer logic and ORM compatibility
- Half-open interval overlap detection: `check_in < check_out AND check_out > check_in` correctly handles adjacent bookings (checkout day = next checkin day)
- Search result dicts use `photo_url` (singular, first element) and `amenity_highlights` (top 5 keys) to match Plan 02's SearchResult Pydantic schema for direct `SearchResult(**r)` unpacking
- Event consumer tests use lazy imports with sys.path manipulation to handle the multi-service pythonpath namespace collision (services/auth and services/room both expose `app` package)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Lazy imports for event consumer tests**
- **Found during:** Task 2 (test creation)
- **Issue:** `from app.models.reservation import ReservationProjection` at module level in test file failed because pytest's pythonpath lists `services/auth` before `services/room`, causing `app` to resolve to auth service's package which has no `reservation` module
- **Fix:** Moved all `app.models.reservation` and `app.services.event_consumer` imports inside test functions, added `_ensure_room_imports()` helper that inserts `services/room` at front of sys.path
- **Files modified:** tests/room/test_event_consumer.py
- **Verification:** All 4 tests collect successfully (`pytest --co` passes); runtime requires PostgreSQL which is expected
- **Committed in:** 90fce94 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Auto-fix was necessary to make tests importable under the existing multi-service pythonpath configuration. No scope creep.

## Issues Encountered
- Test collection failure due to multi-service `app` namespace collision in pythonpath -- resolved with lazy imports (see deviation above)
- Tests require PostgreSQL for runtime execution (expected -- same as all other room service tests)

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ReservationProjection and availability service ready for Plan 02 (search/availability endpoints) and Plan 03 (calendar endpoint)
- Event consumer will sync bookings once booking service publishes to `booking.events` exchange
- overbooking_pct column ready for admin configuration via existing room type CRUD endpoints

---
*Phase: 03-availability-search*
*Completed: 2026-03-21*

## Self-Check: PASSED

All 5 created files verified present. Both task commits (fe7a1a8, 90fce94) verified in git log.
