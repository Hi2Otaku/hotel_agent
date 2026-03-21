# Phase 3: Availability & Search - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Guest-facing search and availability API endpoints. Guests can search available rooms by dates/guest count with filters, view room type details with per-night pricing, and browse a pricing calendar showing rates and availability 6 months ahead. Backed by a correctness-guaranteed availability engine with pessimistic locking at booking time. This phase builds the search APIs that the guest frontend (Phase 5) will consume and that the booking engine (Phase 4) depends on for availability checks.

</domain>

<decisions>
## Implementation Decisions

### Search Behavior
- Search filters: check-in/check-out dates, guest count, room type filter, price range (min/max), amenity filter
- Results grouped by room type (e.g., "Ocean View from $X/night, 3 available") — not individual rooms
- Default sort: recommended (best value/match) — Claude determines ranking algorithm
- Each result shows: photo, room type name, price/night, total stay price, capacity, availability count, top 3-5 amenity highlights, bed configuration
- No auth required for search — public endpoints, login only at booking
- No results: simple "No rooms available for these dates" message — guest adjusts manually

### Availability Logic
- Track availability at individual room level — check each room's reservation overlap for the requested date range
- Half-open date intervals: [check_in, check_out) — check-in included, check-out excluded
- Configurable overbooking buffer per room type (e.g., allow 10% overbooking)
- Pessimistic locking (SELECT ... FOR UPDATE) at booking time only — search is read-only, no locks
- Room service maintains a local reservations projection table, fed by booking events via RabbitMQ

### Pricing Calendar
- Shows 6 months ahead from current date
- Each day shows: lowest available rate, availability indicator (green/yellow/red), room type breakdown
- Filterable by room type — guest can select a type to see its specific pricing/availability
- Click-to-search: clicking a date auto-fills the search form with that check-in date
- Pricing uses the existing multiplicative engine: base × seasonal × weekend (all Decimal)

### Cross-Service Architecture
- Gateway aggregation (BFF pattern) — gateway combines data from Room + Booking services
- All guest requests go through gateway only — services are internal
- Room service consumes booking events via RabbitMQ and maintains a local reservations projection table
- This enables Room service to answer availability queries without calling Booking service at runtime
- Eventually consistent: slight delay between booking confirmation and availability update is acceptable

### Claude's Discretion
- Recommended sort algorithm (price weight, availability, capacity match)
- Reservations projection table schema in Room service
- RabbitMQ consumer implementation details
- Gateway aggregation endpoint implementation
- Overbooking buffer default value
- Availability indicator thresholds (what % triggers yellow vs red)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project research (internal)
- `.planning/research/STACK.md` — Technology stack with versions
- `.planning/research/ARCHITECTURE.md` — Room inventory pattern, pessimistic locking, data flow
- `.planning/research/PITFALLS.md` — Date range pitfalls, double-booking prevention, pricing inconsistencies

### Phase 2 established patterns (Room service)
- `services/room/app/models/room.py` — Room model with status enum and room_type_id FK
- `services/room/app/models/room_type.py` — RoomType model with amenities JSONB, bed_config, photo_urls
- `services/room/app/models/rate.py` — BaseRate, SeasonalRate, WeekendSurcharge models
- `services/room/app/services/rate.py` — Pricing engine with `calculate_nightly_rate()` — multiplicative stacking
- `services/room/app/api/deps.py` — Claims-based JWT auth + RBAC dependency chain
- `services/room/app/core/config.py` — Room service settings
- `services/room/app/core/database.py` — Async engine/session for room_db
- `docker-compose.yml` — Container orchestration (RabbitMQ already configured)

### Phase 1 shared infrastructure
- `shared/shared/messaging.py` — RabbitMQ connection helpers (aio-pika)
- `shared/shared/jwt.py` — JWT verification for non-auth services
- `services/gateway/app/api/proxy.py` — Gateway reverse proxy (to extend with BFF endpoints)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `services/room/app/services/rate.py`: `calculate_nightly_rate()` — already computes per-night price with seasonal + weekend multipliers. Search results can call this directly.
- `services/room/app/models/room.py`: Room model with `status` enum and `room_type_id` FK — availability queries filter by status + date overlap.
- `shared/shared/messaging.py`: RabbitMQ helpers — Room service can use these to consume booking events.
- `services/gateway/app/api/proxy.py`: Gateway proxy — needs BFF aggregation endpoints added for search.

### Established Patterns
- Three-layer: `api/v1/*.py` → `services/*.py` → `models/*.py`
- Claims-based JWT auth (no DB lookup) in Room service
- All monetary values as Decimal with `quantize(Decimal("0.01"))`
- Alembic async migrations per service

### Integration Points
- Room service needs a new `reservations` projection table (consumed from RabbitMQ)
- Room service needs new public endpoints (no auth): search, room details, pricing calendar
- Gateway needs BFF aggregation endpoints that combine Room + availability data
- RabbitMQ consumer in Room service to listen for booking events from Booking service

</code_context>

<specifics>
## Specific Ideas

- Booking events via RabbitMQ for eventually-consistent availability — demonstrates proper microservice event sourcing
- Gateway BFF pattern for search aggregation — shows architectural sophistication beyond simple proxy
- Configurable overbooking buffer demonstrates real hotel industry practice
- Pricing calendar with room type filtering and click-to-search interaction

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-availability-search*
*Context gathered: 2026-03-21*
