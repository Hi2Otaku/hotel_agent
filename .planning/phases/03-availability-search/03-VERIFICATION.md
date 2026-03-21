---
phase: 03-availability-search
verified: 2026-03-21T07:30:00Z
status: passed
score: 9/9 must-haves verified
re_verification: false
---

# Phase 03: Availability Search Verification Report

**Phase Goal:** Guests can search for available rooms by dates and filters, view room details, and see per-night pricing -- backed by a correctness-guaranteed availability engine
**Verified:** 2026-03-21
**Status:** PASSED
**Re-verification:** No -- initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Reservation projection table exists with all required columns | VERIFIED | `ReservationProjection` model in `services/room/app/models/reservation.py` with booking_id (unique), room_type_id, room_id (nullable), check_in, check_out, status (String(20)), guest_count |
| 2 | RoomType model has overbooking_pct column | VERIFIED | `overbooking_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), ...)` in `services/room/app/models/room_type.py` line 30 |
| 3 | RabbitMQ consumer listens on booking.events and upserts projections | VERIFIED | `BOOKING_EXCHANGE = "booking.events"`, `handle_booking_event` with upsert logic in `services/room/app/services/event_consumer.py` |
| 4 | Availability service uses half-open interval overlap detection | VERIFIED | Lines 77-78 in `availability.py`: `ReservationProjection.check_in < check_out` AND `ReservationProjection.check_out > check_in` |
| 5 | Only blocking statuses (pending, confirmed, checked_in) reduce availability | VERIFIED | `BLOCKING_STATUSES = ["pending", "confirmed", "checked_in"]` in `availability.py`; cancelled and checked_out excluded |
| 6 | Guest can search by dates/guests and only available rooms are returned | VERIFIED | `GET /api/v1/search/availability` endpoint wired to `search_available_room_types`; rooms with available==0 are skipped |
| 7 | Guest can filter by room type, price range, and amenities | VERIFIED | Filter logic in `search_available_room_types`: `room_type_id`, `min_price`/`max_price` against `price_per_night`, amenity key set check |
| 8 | Guest can view room type details with photos, amenities, bed_config, and per-night pricing | VERIFIED | `GET /api/v1/search/room-types/{id}` returns `RoomTypeDetail` with `photo_urls`, `amenities`, `bed_config`, `nightly_rates`, `price_per_night`, `total_price` |
| 9 | Guest can see pricing calendar with per-night rates and availability for 6 months | VERIFIED | `GET /api/v1/search/calendar` batch-loads rates, generates days via `timedelta`, returns `CalendarResponse` with green/yellow/red indicators |

**Score:** 9/9 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `services/room/app/models/reservation.py` | ReservationProjection SQLAlchemy model | VERIFIED | Contains `class ReservationProjection(Base):`, `__tablename__ = "reservation_projections"`, all required columns including `booking_id` unique, `room_id` nullable |
| `services/room/alembic/versions/002_reservation_projection.py` | Migration for reservation_projections and overbooking_pct | VERIFIED | `revision = "002"`, `down_revision = "001"`, creates table with all columns, indexes `ix_reservation_proj_availability` and `ix_reservation_proj_room_dates`, adds `overbooking_pct` to room_types |
| `services/room/app/services/event_consumer.py` | RabbitMQ consumer for booking events | VERIFIED | Contains `handle_booking_event`, `start_event_consumer`, `BOOKING_EXCHANGE = "booking.events"`, `ROOM_QUEUE = "room.booking_projections"`, `message.process()` auto-ack pattern |
| `services/room/app/services/availability.py` | Availability query logic | VERIFIED | Exports `get_available_count`, `search_available_room_types`, `effective_capacity`, `compute_sort_score` -- all substantive, full implementation |
| `tests/room/test_event_consumer.py` | Unit tests for event consumer | VERIFIED | 4 tests: `test_handle_booking_event_insert`, `test_handle_booking_event_update`, `test_handle_booking_event_idempotent`, `test_handle_booking_event_sets_room_id` |
| `services/room/app/schemas/availability.py` | Pydantic schemas for search/detail/calendar | VERIFIED | Contains `SearchResult`, `SearchResponse`, `RoomTypeDetail`, `CalendarDay`, `CalendarResponse`, `NightlyRate`, `BedConfigItem`; all monetary fields use `Decimal` |
| `services/room/app/api/v1/search.py` | Public search/detail/calendar endpoints | VERIFIED | 3 endpoints (`search_availability`, `room_type_detail`, `pricing_calendar`); prefix `/api/v1/search`; no `get_current_user` dependency; only `get_db` |
| `tests/room/test_search.py` | Integration tests for search and room detail | VERIFIED | 5 tests: `test_search_by_dates_and_guests`, `test_search_filters`, `test_search_no_results`, `test_search_validation`, `test_room_type_detail` |
| `tests/room/test_availability.py` | Availability logic tests | VERIFIED | 5 tests: `test_overlap_exclusion`, `test_pending_blocks`, `test_cancelled_does_not_block`, `test_back_to_back`, `test_overbooking_buffer` |
| `tests/room/test_calendar.py` | Pricing calendar tests | VERIFIED | 2 tests: `test_pricing_calendar_6_months`, `test_calendar_room_type_filter` |
| `services/gateway/app/api/search.py` | Gateway BFF search aggregation endpoints | VERIFIED | 3 public endpoints forwarding to `ROOM_SERVICE_URL`; no auth dependency; explicit timeouts (30s, 30s, 60s) |
| `tests/gateway/test_search_bff.py` | Gateway BFF integration tests | VERIFIED | 5 tests: `test_bff_search_availability`, `test_bff_room_type_detail`, `test_bff_pricing_calendar`, `test_bff_forwards_query_params`, `test_bff_error_passthrough` |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `services/room/app/services/event_consumer.py` | `services/room/app/models/reservation.py` | upsert ReservationProjection on booking event | WIRED | `ReservationProjection` imported and instantiated in `handle_booking_event`; both insert and update paths present |
| `services/room/app/services/availability.py` | `services/room/app/models/reservation.py` | query reservation_projections for overlap detection | WIRED | `ReservationProjection.check_in < check_out` and `ReservationProjection.check_out > check_in` used in `get_available_count` query |
| `services/room/app/main.py` | `services/room/app/services/event_consumer.py` | asyncio.create_task in lifespan | WIRED | `from app.services.event_consumer import start_event_consumer`; `consumer_task = asyncio.create_task(start_event_consumer())` in lifespan with graceful shutdown |
| `services/room/app/api/v1/search.py` | `services/room/app/services/availability.py` | search endpoint calls search_available_room_types | WIRED | `from app.services.availability import get_available_count, search_available_room_types`; both called in endpoint functions |
| `services/room/app/api/v1/search.py` | `services/room/app/services/rate.py` | detail/calendar endpoints call calculate_stay_price | WIRED | `from app.services.rate import TWO_PLACES, calculate_stay_price, get_base_rate_for_occupancy, get_base_rates, get_seasonal_rates, get_weekend_surcharges`; all used in endpoint functions |
| `services/room/app/main.py` | `services/room/app/api/v1/search.py` | app.include_router(search_router) | WIRED | `from app.api.v1.search import router as search_router`; `app.include_router(search_router)` present |
| `services/gateway/app/api/search.py` | Room service (`/api/v1/search/*`) | httpx.AsyncClient calling ROOM_SERVICE_URL | WIRED | `settings.ROOM_SERVICE_URL` referenced in all 3 BFF endpoints via `httpx.AsyncClient` |
| `services/gateway/app/main.py` | `services/gateway/app/api/search.py` | app.include_router(search_router) before proxy_router | WIRED | `search_router` registered before `proxy_router` on lines 19-20 of `main.py`; correct route precedence confirmed |

---

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|---------------|-------------|--------|---------|
| ROOM-01 | 03-02, 03-03 | Guest can search rooms by check-in/check-out dates and guest count | SATISFIED | `GET /api/v1/search/availability` accepts `check_in`, `check_out`, `guests` query params; returns `SearchResponse` with results grouped by room type; validated by `test_search_by_dates_and_guests` |
| ROOM-02 | 03-01, 03-03 | Guest sees only available rooms for selected dates (real-time availability) | SATISFIED | Availability service uses half-open interval overlap with BLOCKING_STATUSES; rooms with available==0 excluded from results; RabbitMQ consumer syncs reservation projections; validated by `test_overlap_exclusion`, `test_pending_blocks`, `test_cancelled_does_not_block`, `test_back_to_back` |
| ROOM-03 | 03-02, 03-03 | Guest can view room details (photos, amenities, capacity, per-night price) | SATISFIED | `GET /api/v1/search/room-types/{id}` returns `RoomTypeDetail` with `photo_urls`, `amenities` (dict), `bed_config`, `nightly_rates` breakdown, `price_per_night`, `total_price`; validated by `test_room_type_detail` |
| ROOM-04 | 03-02, 03-03 | Guest can see pricing calendar showing per-night rates and availability | SATISFIED | `GET /api/v1/search/calendar` generates up to 12 months of `CalendarDay` entries with rate, `availability_indicator` (green/yellow/red), per-day availability counts; validated by `test_pricing_calendar_6_months` |

All 4 requirements (ROOM-01 through ROOM-04) are satisfied. No orphaned requirements detected -- all appear in plan frontmatter and are covered by implementation.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `services/room/app/services/availability.py` | 240 | `return []` | Info | Legitimate early-exit guard when no active room types have availability -- not a stub. Correctly placed after the raw_results loop. |

No blocking or warning anti-patterns found. The single `return []` instance is a valid business-logic guard (`if not raw_results: return []`), not a placeholder.

---

### Human Verification Required

#### 1. Calendar Per-Day DB Query Performance

**Test:** Run `GET /api/v1/search/calendar?months=6` against a live instance and observe response time.
**Expected:** The calendar batch-loads 3 queries for rates but calls `get_available_count` once per day (up to 180 individual DB queries). This may cause latency under load.
**Why human:** Cannot measure actual query performance with static code analysis; requires a running database.

#### 2. Gateway BFF Route Precedence Under Real Traffic

**Test:** Deploy gateway with both `search_router` and `proxy_router` active and issue a real `GET /api/v1/search/availability` request.
**Expected:** Request hits the BFF handler (`search_availability`), not the catch-all proxy, and receives a Room-service JSON response.
**Why human:** Route precedence is verified structurally (BFF registered first in `main.py`), but runtime behavior under FastAPI's route matching requires a live environment to confirm.

---

### Gaps Summary

No gaps found. All must-have truths are verified, all artifacts are substantive and wired, all key links are confirmed, and all 4 requirements (ROOM-01, ROOM-02, ROOM-03, ROOM-04) are satisfied.

**Git commits verified:** All 6 phase commits exist in history -- `fe7a1a8`, `90fce94` (Plan 01), `e874d47`, `c833b4d` (Plan 02), `7f1b514`, `65d7a44` (Plan 03).

**Notable implementation details confirmed correct:**
- Half-open interval overlap: `check_in < check_out AND check_out > check_in` (back-to-back bookings never conflict)
- `effective_capacity = int(physical * (1 + overbooking_pct / 100))`
- `photo_url` (singular, first element) and `amenity_highlights` (top 5 keys) in search result dicts match `SearchResult(**r)` unpacking
- BFF registered before catch-all proxy for correct route precedence
- All search endpoints have no `get_current_user` dependency (public access confirmed)
- `message.process()` async context manager ensures auto-ack on success / nack on exception

---

_Verified: 2026-03-21T07:30:00Z_
_Verifier: Claude (gsd-verifier)_
