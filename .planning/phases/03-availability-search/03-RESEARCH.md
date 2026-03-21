# Phase 3: Availability & Search - Research

**Researched:** 2026-03-21
**Domain:** Room availability queries, search API, pricing calendar, RabbitMQ event consumption, Gateway BFF aggregation
**Confidence:** HIGH

## Summary

Phase 3 builds the guest-facing search and availability system on top of the existing Room service (Phase 2). The core challenge is threefold: (1) creating a reservations projection table in the Room service that tracks bookings via RabbitMQ events, (2) building efficient availability queries that check individual room overlaps using half-open date intervals, and (3) extending the Gateway with BFF aggregation endpoints that combine room type data with availability counts and pricing.

The existing codebase provides strong foundations: `calculate_nightly_rate()` and `calculate_stay_price()` already handle multiplicative pricing with per-night granularity. The Room model tracks individual rooms with `room_type_id` FK and `status` enum. RabbitMQ infrastructure (aio-pika) is configured in docker-compose and shared messaging helpers exist. The Gateway has a working reverse proxy that needs BFF endpoints added alongside (not replacing) the existing proxy route.

All endpoints in this phase are public (no auth required). This is a departure from Phase 2's staff-only endpoints and requires new routes without the `get_current_user` dependency. The search must be read-only with no locking -- pessimistic locking happens only at booking time (Phase 4).

**Primary recommendation:** Build the reservations projection table and RabbitMQ consumer first, then layer search/availability/calendar endpoints on top, then add Gateway BFF aggregation last.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Search filters: check-in/check-out dates, guest count, room type filter, price range (min/max), amenity filter
- Results grouped by room type (e.g., "Ocean View from $X/night, 3 available") -- not individual rooms
- Default sort: recommended (best value/match) -- Claude determines ranking algorithm
- Each result shows: photo, room type name, price/night, total stay price, capacity, availability count, top 3-5 amenity highlights, bed configuration
- No auth required for search -- public endpoints, login only at booking
- No results: simple "No rooms available for these dates" message
- Track availability at individual room level -- check each room's reservation overlap for the requested date range
- Half-open date intervals: [check_in, check_out) -- check-in included, check-out excluded
- Configurable overbooking buffer per room type (e.g., allow 10% overbooking)
- Pessimistic locking (SELECT ... FOR UPDATE) at booking time only -- search is read-only, no locks
- Room service maintains a local reservations projection table, fed by booking events via RabbitMQ
- Pricing calendar: 6 months ahead, per-night rates + availability indicators, filterable by room type
- Click-to-search: clicking a date auto-fills the search form with that check-in date
- Gateway aggregation (BFF pattern) -- gateway combines data from Room + Booking services
- All guest requests go through gateway only -- services are internal
- Eventually consistent: slight delay between booking confirmation and availability update is acceptable

### Claude's Discretion
- Recommended sort algorithm (price weight, availability, capacity match)
- Reservations projection table schema in Room service
- RabbitMQ consumer implementation details
- Gateway aggregation endpoint implementation
- Overbooking buffer default value
- Availability indicator thresholds (what % triggers yellow vs red)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ROOM-01 | Guest can search rooms by check-in/check-out dates and guest count | Search endpoint with date range + guest count + filters; availability service queries reservations projection table; results grouped by room type |
| ROOM-02 | Guest sees only available rooms for selected dates (real-time availability) | Reservations projection table fed by RabbitMQ; overlap detection query using half-open intervals; overbooking buffer per room type |
| ROOM-03 | Guest can view room details (photos, amenities, capacity, per-night price) | Room type detail endpoint reusing existing RoomType model (photo_urls, amenities JSONB, bed_config, max_adults/max_children); price via existing `calculate_stay_price()` |
| ROOM-04 | Guest can see pricing calendar showing per-night rates and availability | Calendar endpoint generating 6 months of per-night rates using existing pricing engine; availability indicators from projection table counts |
</phase_requirements>

## Standard Stack

### Core (already in project)
| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| FastAPI | 0.135.x | API framework for new search endpoints | Existing |
| SQLAlchemy | 2.0.48 | ORM for reservations projection + availability queries | Existing |
| asyncpg | latest | PostgreSQL async driver | Existing |
| Pydantic | 2.12.x | Request/response schemas for search | Existing |
| aio-pika | latest | RabbitMQ consumer for booking events | Existing in shared/shared/messaging.py |
| httpx | latest | Gateway-to-service HTTP calls for BFF | Existing in gateway proxy |

### No New Dependencies Required
This phase uses only existing libraries. No new pip installs needed. The RabbitMQ consumer uses `aio-pika` (already in shared). The Gateway BFF uses `httpx` (already a gateway dependency). All database work uses existing SQLAlchemy + asyncpg.

## Architecture Patterns

### Recommended Project Structure (New Files)
```
services/room/app/
  models/
    reservation.py          # NEW: Reservations projection table model
  schemas/
    availability.py         # NEW: Search request/response, calendar schemas
  services/
    availability.py         # NEW: Availability queries, search logic
    event_consumer.py       # NEW: RabbitMQ consumer for booking events
  api/v1/
    search.py               # NEW: Public search/availability/calendar endpoints

services/gateway/app/
  api/
    search.py               # NEW: BFF aggregation endpoints for search
  services/
    aggregation.py          # NEW: Multi-service data combination logic

services/room/alembic/versions/
    002_reservations_projection.py  # NEW: Migration for projection table
```

### Pattern 1: Reservations Projection Table
**What:** A local table in the Room service database that mirrors relevant booking data, fed by RabbitMQ events from the Booking service. This enables the Room service to answer availability queries without runtime calls to the Booking service.
**When to use:** When a service needs data owned by another service for read-heavy queries.
**Schema design:**

```python
class ReservationProjection(Base):
    """Local projection of bookings for availability queries.

    Fed by RabbitMQ events from Booking service.
    """
    __tablename__ = "reservation_projections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    room_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("room_types.id"), nullable=False
    )
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=True
    )
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    guest_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

**Key indexes:**
```sql
-- Composite index for availability queries
CREATE INDEX ix_reservation_proj_availability
ON reservation_projections (room_type_id, check_in, check_out, status);

-- Index for room-level overlap checks
CREATE INDEX ix_reservation_proj_room_dates
ON reservation_projections (room_id, check_in, check_out)
WHERE room_id IS NOT NULL;
```

**Design rationale:**
- `booking_id` is unique -- each booking maps to one projection row
- `room_id` is nullable because at search/booking time, a specific room may not yet be assigned (assigned at check-in)
- `status` tracks booking state (pending, confirmed, cancelled, checked_out) so cancelled bookings can be excluded from availability
- Statuses that BLOCK availability: `pending`, `confirmed`, `checked_in`
- Statuses that DO NOT block: `cancelled`, `checked_out`

### Pattern 2: Overbooking Buffer Configuration
**What:** Each room type can allow a configurable percentage of overbooking.
**Implementation:** Add an `overbooking_pct` column to `room_types` table (Decimal, default 0.00, meaning no overbooking). When checking availability, effective capacity = `physical_room_count * (1 + overbooking_pct / 100)`, rounded down.

```python
# In availability service
def effective_capacity(physical_count: int, overbooking_pct: Decimal) -> int:
    """Calculate effective room count with overbooking buffer."""
    return int(physical_count * (1 + overbooking_pct / Decimal("100")))
```

**Default overbooking buffer: 0% (no overbooking).** This is the safe default. Staff can configure per room type via the existing room type update endpoint (add `overbooking_pct` field).

### Pattern 3: Half-Open Interval Overlap Detection
**What:** Availability queries use `[check_in, check_out)` intervals where check_out is exclusive. This means a guest checking out on March 12 does NOT conflict with a guest checking in on March 12.
**SQL pattern:**

```sql
-- Find rooms of a given type that are NOT reserved for the requested range
-- Half-open overlap: [a.check_in, a.check_out) overlaps [b.check_in, b.check_out)
-- when a.check_in < b.check_out AND a.check_out > b.check_in
SELECT r.id FROM rooms r
WHERE r.room_type_id = :type_id
  AND r.is_active = true
  AND r.id NOT IN (
    SELECT rp.room_id FROM reservation_projections rp
    WHERE rp.room_type_id = :type_id
      AND rp.status IN ('pending', 'confirmed', 'checked_in')
      AND rp.check_in < :requested_check_out
      AND rp.check_out > :requested_check_in
      AND rp.room_id IS NOT NULL
  )
```

**Important:** Since `room_id` may be NULL on projections (no room assigned yet), we need a two-level check:
1. Count active rooms of the type
2. Count blocking reservations for the type (regardless of room_id)
3. Available = effective_capacity - blocking_reservation_count

This is simpler and correct -- we do not need individual room assignment at search time.

### Pattern 4: RabbitMQ Event Consumer
**What:** Room service starts a background consumer on startup that listens for booking events.
**Exchange:** `booking.events` (topic exchange, durable)
**Routing keys:**
- `booking.created` -- new reservation, insert projection
- `booking.confirmed` -- update status
- `booking.cancelled` -- update status (no longer blocks availability)
- `booking.checked_in` -- update status + assign room_id
- `booking.checked_out` -- update status (no longer blocks availability)

**Implementation in lifespan:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Existing startup (MinIO, seed)...

    # Start RabbitMQ consumer
    consumer_task = asyncio.create_task(start_event_consumer())

    yield

    # Graceful shutdown
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
```

**Message format (expected from Booking service in Phase 4):**
```json
{
    "event_type": "booking.created",
    "booking_id": "uuid",
    "room_type_id": "uuid",
    "room_id": null,
    "check_in": "2026-04-10",
    "check_out": "2026-04-13",
    "status": "pending",
    "guest_count": 2,
    "timestamp": "2026-03-21T10:00:00Z"
}
```

**Idempotency:** Use `booking_id` UNIQUE constraint. On duplicate, UPDATE instead of INSERT (upsert pattern).

### Pattern 5: Gateway BFF Aggregation
**What:** The Gateway exposes dedicated search endpoints that aggregate data from the Room service, rather than having the client make multiple requests.
**Key difference from proxy:** Proxy forwards requests 1:1. BFF endpoints call Room service internally and may combine/transform data before returning to the client.

```python
# Gateway BFF endpoint
@router.get("/api/v1/search/availability")
async def search_availability(
    check_in: date, check_out: date, guests: int,
    room_type_id: UUID | None = None,
    min_price: Decimal | None = None, max_price: Decimal | None = None,
    amenities: str | None = None,  # comma-separated
):
    # Call Room service search endpoint
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{ROOM_SERVICE_URL}/api/v1/search/availability",
            params={...}
        )
    return resp.json()
```

**For Phase 3, the Gateway BFF can be a thin pass-through** to the Room service search endpoints, since Room service has all the data it needs locally (room types, rates, reservation projections). The BFF pattern becomes more valuable in Phase 4 when combining booking data.

**Gateway routing:** Add BFF routes BEFORE the catch-all proxy route so they take precedence.

### Pattern 6: Recommended Sort Algorithm
**What:** Default sort for search results balances value, availability, and capacity match.
**Algorithm:**

```python
def compute_sort_score(
    price_per_night: Decimal,
    max_price_in_results: Decimal,
    available_count: int,
    total_count: int,
    capacity_match: float,  # 0-1, how well guest count fits room capacity
) -> float:
    """Higher score = better recommendation."""
    # Normalize price (lower is better value)
    price_score = 1.0 - float(price_per_night / max_price_in_results) if max_price_in_results > 0 else 0.5

    # Availability score (more available = less urgency, but still good)
    avail_score = min(available_count / max(total_count, 1), 1.0)

    # Capacity match (1.0 = perfect fit, lower if room is much bigger than needed)
    cap_score = capacity_match

    # Weighted combination
    return (price_score * 0.4) + (avail_score * 0.3) + (cap_score * 0.3)
```

Weights: 40% price value, 30% availability, 30% capacity fit. Sort descending.

### Anti-Patterns to Avoid
- **N+1 pricing queries:** Do NOT call `calculate_nightly_rate()` per-night per-room-type in a loop for search results. Batch-load all rates for the requested room types, then compute in memory.
- **Locking during search:** Search MUST be read-only. No `FOR UPDATE`, no write transactions. Locking is Phase 4's concern.
- **Client-side availability filtering:** All availability filtering happens server-side in SQL. Never return all rooms and let the frontend filter.
- **Separate calendar API calls per day:** The pricing calendar endpoint must return all 180 days in a single response, not require the client to make 180 requests.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Date overlap detection | Custom Python date comparison loops | SQL with `check_in < :end AND check_out > :start` | SQL is atomic, indexed, and handles edge cases correctly |
| Message queue consumer | Raw socket connection to RabbitMQ | aio-pika `consume()` with ack/nack | Handles reconnection, message acknowledgment, prefetch |
| Decimal arithmetic | Float math for prices | Python `Decimal` with `quantize(TWO_PLACES)` | Already established in codebase -- float would introduce rounding errors |
| HTTP client for BFF | `urllib` or raw sockets | `httpx.AsyncClient` | Already used in gateway proxy; handles async, timeouts, connection pooling |

## Common Pitfalls

### Pitfall 1: Counting Availability by Room Instead of by Reservation
**What goes wrong:** You try to count available rooms by checking each individual room's schedule. With 55 rooms and multi-day stays, this becomes complex and slow.
**Why it happens:** Thinking "which specific rooms are free" instead of "how many rooms of this type have overlapping reservations."
**How to avoid:** Count blocking reservations per room type, subtract from total room count (with overbooking buffer). Individual room assignment is a Phase 4/6 concern (check-in).
**Warning signs:** Queries join rooms table with reservations and GROUP BY room.id instead of room_type_id.

### Pitfall 2: Forgetting Pending Reservations Block Availability
**What goes wrong:** Only counting `confirmed` and `checked_in` reservations as blocking. Two users both see 1 room available, both submit bookings, one gets double-booked.
**Why it happens:** Misunderstanding that `pending` reservations (payment in progress) also consume capacity.
**How to avoid:** Blocking statuses: `pending`, `confirmed`, `checked_in`. Non-blocking: `cancelled`, `checked_out`.

### Pitfall 3: RabbitMQ Consumer Crash Losing Events
**What goes wrong:** Consumer processes a message, updates the database, but crashes before acknowledging. Or acknowledges before processing, then crashes and loses the event.
**Why it happens:** Incorrect ack timing.
**How to avoid:** Process message first, then ack. Use `aio_pika`'s manual ack mode. On failure, nack with requeue. Use `connect_robust` for auto-reconnection (already in shared helpers).

### Pitfall 4: Pricing Calendar Performance
**What goes wrong:** Generating 180 days of pricing for 4 room types requires 720 calls to `calculate_nightly_rate()`, each doing 3 DB queries (base rate, seasonal, weekend) = 2160 queries.
**Why it happens:** Calling the existing per-night function in a loop without optimization.
**How to avoid:** Batch-load all rates for the requested room types upfront (1 query for base rates, 1 for seasonal, 1 for weekend surcharges), then compute pricing in-memory. Create a `calculate_calendar_rates()` function that pre-fetches data.

### Pitfall 5: Gateway BFF Creating Circular Dependencies
**What goes wrong:** Gateway calls Room service, which calls Booking service, which calls Room service for rate information.
**Why it happens:** Unclear service boundaries.
**How to avoid:** Room service is self-contained for search (it has its own reservation projection). Gateway only calls Room service for search. No service-to-service calls for search queries.

## Code Examples

### Availability Count Query (SQLAlchemy)
```python
# Source: Derived from existing codebase patterns
from sqlalchemy import select, func, and_
from app.models.reservation import ReservationProjection
from app.models.room import Room

async def get_available_count(
    db: AsyncSession,
    room_type_id: uuid.UUID,
    check_in: date,
    check_out: date,
) -> tuple[int, int]:
    """Return (available_count, total_count) for a room type in date range.

    Uses half-open interval [check_in, check_out).
    """
    # Count total active rooms of this type
    total_q = select(func.count()).select_from(Room).where(
        Room.room_type_id == room_type_id,
        Room.is_active == True,
    )
    total = (await db.execute(total_q)).scalar() or 0

    # Count blocking reservations
    blocking_q = select(func.count()).select_from(ReservationProjection).where(
        ReservationProjection.room_type_id == room_type_id,
        ReservationProjection.status.in_(["pending", "confirmed", "checked_in"]),
        ReservationProjection.check_in < check_out,   # half-open
        ReservationProjection.check_out > check_in,    # half-open
    )
    blocking = (await db.execute(blocking_q)).scalar() or 0

    return max(total - blocking, 0), total
```

### Batch Calendar Pricing
```python
# Source: Extending existing rate.py patterns
from datetime import date, timedelta
from decimal import Decimal

TWO_PLACES = Decimal("0.01")

async def calculate_calendar_rates(
    db: AsyncSession,
    room_type_id: uuid.UUID,
    start_date: date,
    months: int = 6,
    occupancy: int = 2,
) -> list[dict]:
    """Generate per-day pricing for calendar display.

    Pre-fetches all rate data to avoid N+1 queries.
    """
    from dateutil.relativedelta import relativedelta
    end_date = start_date + relativedelta(months=months)

    # Pre-fetch all rates (3 queries total, not 3 * num_days)
    base_rates = await get_base_rates(db, room_type_id)
    seasonal_rates = await get_seasonal_rates(db, room_type_id)
    weekend_surcharges = await get_weekend_surcharges(db, room_type_id)

    # Find matching base rate for occupancy
    base_amount = Decimal("0")
    for br in base_rates:
        if br.min_occupancy <= occupancy <= br.max_occupancy:
            base_amount = Decimal(str(br.amount))
            break

    results = []
    current = start_date
    while current < end_date:
        seasonal_mult = Decimal("1.00")
        for sr in seasonal_rates:
            if sr.start_date <= current <= sr.end_date:
                seasonal_mult = Decimal(str(sr.multiplier))
                break

        weekend_mult = Decimal("1.00")
        weekday = current.weekday()
        for ws in weekend_surcharges:
            if weekday in ws.days:
                weekend_mult = Decimal(str(ws.multiplier))
                break

        final = (base_amount * seasonal_mult * weekend_mult).quantize(TWO_PLACES)

        results.append({
            "date": current,
            "rate": final,
            "base_amount": base_amount,
            "seasonal_multiplier": seasonal_mult,
            "weekend_multiplier": weekend_mult,
        })
        current += timedelta(days=1)

    return results
```

### RabbitMQ Event Consumer
```python
# Source: Extending shared/shared/messaging.py patterns
import json
import logging
from aio_pika import IncomingMessage
from shared.messaging import get_rabbitmq_connection, get_channel, declare_exchange, declare_queue

logger = logging.getLogger(__name__)

BOOKING_EXCHANGE = "booking.events"
ROOM_QUEUE = "room.booking_projections"
BLOCKING_STATUSES = {"pending", "confirmed", "checked_in"}

async def handle_booking_event(message: IncomingMessage):
    """Process a booking event and upsert reservation projection."""
    async with message.process():  # auto-ack on success, nack on exception
        data = json.loads(message.body.decode())
        event_type = data.get("event_type")
        booking_id = data.get("booking_id")

        logger.info(f"Processing {event_type} for booking {booking_id}")

        # Get DB session
        async with async_session_factory() as db:
            existing = await db.execute(
                select(ReservationProjection).where(
                    ReservationProjection.booking_id == uuid.UUID(booking_id)
                )
            )
            projection = existing.scalar_one_or_none()

            if projection is None:
                # Insert new projection
                projection = ReservationProjection(
                    booking_id=uuid.UUID(booking_id),
                    room_type_id=uuid.UUID(data["room_type_id"]),
                    check_in=date.fromisoformat(data["check_in"]),
                    check_out=date.fromisoformat(data["check_out"]),
                    status=data["status"],
                    guest_count=data.get("guest_count", 1),
                )
                db.add(projection)
            else:
                # Update existing projection
                projection.status = data["status"]
                if data.get("room_id"):
                    projection.room_id = uuid.UUID(data["room_id"])

            await db.commit()

async def start_event_consumer():
    """Start consuming booking events from RabbitMQ."""
    from app.core.config import settings

    connection = await get_rabbitmq_connection(settings.RABBITMQ_URL)
    channel = await get_channel(connection)

    exchange = await declare_exchange(channel, BOOKING_EXCHANGE)
    queue = await declare_queue(channel, ROOM_QUEUE)

    # Bind to all booking events
    await queue.bind(exchange, routing_key="booking.*")

    await queue.consume(handle_booking_event)

    # Keep consumer running
    try:
        await asyncio.Future()  # run forever
    finally:
        await connection.close()
```

### Public Search Endpoint (No Auth)
```python
# Source: Follows existing room service patterns but WITHOUT auth dependency
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db  # DB dep only, no auth

router = APIRouter(prefix="/api/v1/search", tags=["search"])

@router.get("/availability")
async def search_availability(
    check_in: date = Query(...),
    check_out: date = Query(...),
    guests: int = Query(..., ge=1),
    room_type_id: uuid.UUID | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    amenities: str | None = None,
    sort: str = "recommended",
    db: AsyncSession = Depends(get_db),
    # NOTE: No auth dependency -- public endpoint
):
    """Search available rooms. Public, no authentication required."""
    ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Room inventory table (pre-computed per-day counts) | Reservation overlap queries against projection table | N/A -- project decision | Simpler to maintain; no daily batch job needed |
| Monolithic availability check (single service) | Event-driven projection (Booking publishes, Room consumes) | Microservices pattern | Room service is self-sufficient for reads |
| REST polling for availability | Still REST for this project (WebSocket would be overkill) | N/A | Appropriate for portfolio project scale |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.x + pytest-asyncio |
| Config file | `tests/room/conftest.py` (existing) |
| Quick run command | `cd services/room && python -m pytest tests/room/ -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ROOM-01 | Search by dates + guest count returns grouped results | integration | `python -m pytest tests/room/test_search.py::test_search_by_dates_and_guests -x` | Wave 0 |
| ROOM-01 | Search filters (room type, price range, amenities) | integration | `python -m pytest tests/room/test_search.py::test_search_filters -x` | Wave 0 |
| ROOM-02 | Available rooms exclude overlapping reservations | integration | `python -m pytest tests/room/test_availability.py::test_overlap_exclusion -x` | Wave 0 |
| ROOM-02 | Pending reservations block availability | integration | `python -m pytest tests/room/test_availability.py::test_pending_blocks -x` | Wave 0 |
| ROOM-02 | Back-to-back bookings (checkout=checkin) do not conflict | integration | `python -m pytest tests/room/test_availability.py::test_back_to_back -x` | Wave 0 |
| ROOM-02 | Overbooking buffer allows extra capacity | unit | `python -m pytest tests/room/test_availability.py::test_overbooking_buffer -x` | Wave 0 |
| ROOM-03 | Room type detail returns photos, amenities, price | integration | `python -m pytest tests/room/test_search.py::test_room_type_detail -x` | Wave 0 |
| ROOM-04 | Pricing calendar returns 6 months of rates | integration | `python -m pytest tests/room/test_calendar.py::test_pricing_calendar_6_months -x` | Wave 0 |
| ROOM-04 | Calendar filterable by room type | integration | `python -m pytest tests/room/test_calendar.py::test_calendar_room_type_filter -x` | Wave 0 |
| N/A | RabbitMQ consumer upserts projection | unit | `python -m pytest tests/room/test_event_consumer.py -x` | Wave 0 |
| N/A | Gateway BFF search endpoint | integration | `python -m pytest tests/gateway/test_search_bff.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/room/test_search.py tests/room/test_availability.py tests/room/test_calendar.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/room/test_search.py` -- covers ROOM-01, ROOM-03
- [ ] `tests/room/test_availability.py` -- covers ROOM-02
- [ ] `tests/room/test_calendar.py` -- covers ROOM-04
- [ ] `tests/room/test_event_consumer.py` -- covers RabbitMQ consumer logic
- [ ] `tests/gateway/` directory and `tests/gateway/conftest.py` -- gateway test infrastructure
- [ ] `tests/gateway/test_search_bff.py` -- covers Gateway BFF endpoints

## Open Questions

1. **Booking service event format**
   - What we know: Room service consumes events; we define the expected message schema
   - What's unclear: Booking service (Phase 4) does not exist yet, so we define the contract now
   - Recommendation: Define the event schema in Phase 3 as a contract. Phase 4 must publish events matching this schema. Document the schema in a shared location or in the Room service consumer code.

2. **python-dateutil dependency for relativedelta**
   - What we know: `calculate_calendar_rates()` needs to add 6 months to a date. `timedelta` cannot add months.
   - What's unclear: Whether `python-dateutil` is already installed
   - Recommendation: Check if installed. If not, add it. Alternatively, compute end date as `date(year, month + 6, day)` with manual month overflow handling, or just use `start_date + timedelta(days=180)` as a simpler approximation.

3. **RabbitMQ consumer testability**
   - What we know: Testing the full consumer requires a running RabbitMQ instance
   - What's unclear: Whether integration tests should require RabbitMQ
   - Recommendation: Test the event handler function (`handle_booking_event`) independently by calling it with mock messages. Test the consumer wiring separately (or skip for unit tests). Insert test reservation projections directly in the DB for search/availability tests.

## Sources

### Primary (HIGH confidence)
- `services/room/app/services/rate.py` -- Existing pricing engine with `calculate_nightly_rate()` and `calculate_stay_price()`
- `services/room/app/models/room.py` -- Room model with UUID PK, room_type_id FK, RoomStatus enum
- `services/room/app/models/room_type.py` -- RoomType with JSONB amenities, bed_config, photo_urls
- `shared/shared/messaging.py` -- aio-pika helpers: `get_rabbitmq_connection`, `get_channel`, `declare_exchange`, `declare_queue`
- `services/gateway/app/api/proxy.py` -- Gateway reverse proxy with SERVICE_MAP routing
- `services/room/app/services/seed.py` -- 4 room types, 55 rooms, full rate configuration
- `docker-compose.yml` -- RabbitMQ already configured at `amqp://hotel:hotel_pass@rabbitmq:5672/`

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md` -- Pessimistic locking pattern, three-layer architecture
- `.planning/research/PITFALLS.md` -- Half-open intervals, availability query patterns, N+1 performance

### Tertiary (LOW confidence)
- Sort algorithm weights (0.4/0.3/0.3) -- reasonable defaults but may need tuning based on UX feedback
- Overbooking buffer default (0%) -- conservative but may want 5-10% for realism

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already in use, no new dependencies
- Architecture: HIGH -- patterns derived from existing codebase conventions and CONTEXT.md decisions
- Pitfalls: HIGH -- well-documented in project research and verified against codebase
- Event consumer: MEDIUM -- contract defined ahead of Booking service (Phase 4)
- Gateway BFF: MEDIUM -- simple pass-through for now, becomes more complex in Phase 4

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (30 days -- stable domain, no fast-moving dependencies)
