# Phase 4: Booking Engine - Research

**Researched:** 2026-03-21
**Domain:** Booking lifecycle, payment simulation, state machine, event-driven cross-service integration
**Confidence:** HIGH

## Summary

Phase 4 builds the full booking lifecycle in the Booking service: a three-step creation flow (reserve with pessimistic locking, guest details submission, mock payment confirmation), booking management (view, cancel, modify with price recalculation), a state machine with 15-minute PENDING expiry, confirmation emails via Mailpit, and RabbitMQ event publishing that matches the Room service consumer contract established in Phase 3.

The Booking service is currently a stub (`services/booking/app/main.py` with only a health endpoint). It has a database container (`booking_db` on port 5435) already configured in `docker-compose.yml`, but no Alembic setup, no models, no routes, no services. Everything must be built from scratch, following the patterns established in the Auth (Phase 1) and Room (Phase 2-3) services.

**Primary recommendation:** Build in layers: (1) Alembic + models + config, (2) booking service with state machine + pessimistic locking + event publishing, (3) three-step booking API endpoints, (4) payment service + confirmation email, (5) booking management endpoints (view/cancel/modify), (6) background expiry task, (7) gateway BFF endpoints and integration tests.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Three-step API flow: Reserve (PENDING + room hold) -> Guest Details -> Payment (CONFIRMED + email)
- Pessimistic locking (SELECT ... FOR UPDATE) at reservation step
- Standard card fields: card number, expiry (MM/YY), CVC, cardholder name, billing address
- Simulated 2-3 second processing delay for realism
- Test cards: 4242424242424242=success, 4000000000000002=decline, 4111111111111111=insufficient funds
- Payment generates transaction record: transaction ID, amount, last 4 digits, timestamp, status
- Card data NOT stored -- only last 4 digits and transaction metadata
- Free cancellation up to N days before check-in (N is admin-configurable), late cancellation = first night charge
- Guests can modify: dates, room type, guest count, guest details (with price recalc, availability check)
- Cannot modify after check-in
- 15-minute PENDING expiry with dual cleanup: background task (every 5 min) AND on-demand check when booking is accessed
- States: PENDING -> CONFIRMED -> CHECKED_IN -> CHECKED_OUT; plus PENDING -> CANCELLED, CONFIRMED -> CANCELLED
- BookingStatus enum already defined in Phase 1 auth migration (includes NO_SHOW)
- Events published via RabbitMQ on every state change, matching Room service consumer contract
- Booking service calls Room service for pricing or replicates pricing logic (Claude's discretion)
- Gateway needs booking endpoints added to BFF

### Claude's Discretion
- Confirmation number format
- Transaction ID format
- Exact test card number mappings beyond the 3 specified
- Background task implementation (asyncio periodic vs dedicated worker)
- How Booking service gets pricing data (call Room service API vs replicate pricing logic)
- Cancellation policy default days value
- Gateway BFF endpoint design for booking operations

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BOOK-01 | Guest can complete multi-step booking (select room -> guest details -> payment -> confirmation) | Three-step API flow with state machine; pessimistic locking pattern from Architecture research; Room service pricing engine for rate calculation |
| BOOK-02 | Guest completes mock payment with Stripe-like card form | Mock payment service with test card logic, transaction record model, asyncio.sleep for processing delay |
| BOOK-03 | Guest receives booking confirmation page with confirmation number | Confirmation number generation (HB-XXXXXX format); booking response schema with full details |
| BOOK-04 | Guest receives mock email confirmation | fastapi-mail + Mailpit pattern from Auth service email.py; Jinja2 HTML template |
| BOOK-05 | Cancellation policy displayed during booking flow | Admin-configurable cancellation_policy_days setting; policy calculation logic in booking service |
| MGMT-01 | Guest can view upcoming and past bookings with status | List endpoint with status filtering; ownership enforcement (user_id from JWT) |
| MGMT-02 | Guest can cancel a booking (with policy enforcement) | State machine transition CONFIRMED->CANCELLED; cancellation fee calculation; availability release via RabbitMQ event |
| MGMT-03 | Guest can modify booking dates/room with automatic price recalculation | Availability re-check with locking; Room service pricing call; old-vs-new price comparison |
</phase_requirements>

## Standard Stack

### Core (already in project)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.135.x | API framework | Project standard, all services use it |
| SQLAlchemy | 2.0.48+ | ORM with async | Project standard, async with asyncpg |
| asyncpg | latest | PostgreSQL async driver | Project standard |
| Alembic | 1.18.x | Database migrations | Project standard, async env pattern from Room service |
| Pydantic | 2.12.x | Request/response schemas | Ships with FastAPI |
| pydantic-settings | 2.x | Config from env vars | Project standard |
| aio-pika | latest | RabbitMQ client | Already used in shared/messaging.py and Room service |
| fastapi-mail | latest | Email via Mailpit | Already used in Auth service for password reset/invite |
| httpx | latest | HTTP client + testing | Project standard |
| PyJWT | 2.x | JWT verification | Via shared/jwt.py |

### New Dependencies for Booking Service

| Library | Purpose | Notes |
|---------|---------|-------|
| alembic | Migrations | Needs alembic init + alembic.ini in services/booking/ |
| fastapi-mail | Confirmation emails | Same pattern as auth service; add to booking requirements.txt |
| jinja2 | Email templates | Dependency of fastapi-mail, already available |

**Installation (add to `services/booking/requirements.txt`):**
```
fastapi[standard]>=0.135.0
uvicorn[standard]
sqlalchemy[asyncio]>=2.0.48
asyncpg
pydantic-settings>=2.0
httpx
alembic>=1.18.0
aio-pika>=9.0
fastapi-mail
```

## Architecture Patterns

### Booking Service Structure (mirrors Room service)
```
services/booking/
  alembic/
    versions/
      001_initial_booking_models.py
    env.py
  alembic.ini
  app/
    __init__.py
    main.py                    # Lifespan: event publisher init + background expiry task
    core/
      __init__.py
      config.py                # Settings: DB, JWT, RabbitMQ, Mail, cancellation policy
      database.py              # Async engine + session factory (mirrors room service)
    models/
      __init__.py
      booking.py               # Booking model with status enum
      guest_details.py         # GuestDetails model (name, email, phone, address, etc.)
      payment.py               # PaymentTransaction model
    schemas/
      __init__.py
      booking.py               # Create/Response/List schemas
      guest_details.py         # Guest details submission schema
      payment.py               # Payment request/response schemas
    api/
      __init__.py
      deps.py                  # get_db, get_current_user (claims-based, mirrors Room)
      v1/
        __init__.py
        bookings.py            # Booking CRUD + flow endpoints
    services/
      __init__.py
      booking.py               # Core booking logic, state machine, availability
      payment.py               # Mock payment processing
      email.py                 # Booking confirmation email
      pricing.py               # Pricing via Room service API call
      event_publisher.py       # RabbitMQ event publishing
      expiry.py                # Background PENDING expiry task
    templates/
      email/
        booking_confirmation.html
  Dockerfile
  requirements.txt
```

### Pattern 1: Three-Step Booking Flow
**What:** Three separate API endpoints that progress a booking through creation:
1. `POST /api/v1/bookings` -- Reserve: creates PENDING booking with pessimistic lock
2. `PUT /api/v1/bookings/{id}/guest-details` -- Submit guest info
3. `POST /api/v1/bookings/{id}/payment` -- Submit payment, transition to CONFIRMED

**When to use:** Always for this booking flow.
**Example:**
```python
# POST /api/v1/bookings -- Step 1: Reserve
async def create_booking(db: AsyncSession, user_id: uuid.UUID, data: BookingCreate) -> Booking:
    """Create a PENDING booking with pessimistic locking."""
    # Lock rooms of this type to prevent double-booking
    rooms = await db.execute(
        select(Room)  # This would be against a local or remote check
        .with_for_update()
        .where(...)
    )
    # Verify availability count
    # Create booking with status=PENDING, expires_at=now+15min
    # Publish booking.created event
    # Return booking with confirmation_number
```

### Pattern 2: Pessimistic Locking for Availability
**What:** The Booking service must ensure no double-booking. Since availability data lives in the Room service (via ReservationProjection), the Booking service needs its own mechanism.

**Recommended approach:** The Booking service maintains its own bookings table. At reservation time:
1. Use `SELECT ... FOR UPDATE` on existing bookings for the same room_type + overlapping dates
2. Count blocking bookings (PENDING + CONFIRMED + CHECKED_IN)
3. Call Room service API to get total room count for the room type
4. If blocking_count >= total_rooms, reject
5. Insert new booking within same transaction
6. Publish event so Room service updates its projection

```python
async def check_and_reserve(
    db: AsyncSession, room_type_id: uuid.UUID, check_in: date, check_out: date
) -> bool:
    """Atomically check availability and create reservation."""
    # Lock all overlapping bookings for this room type
    result = await db.execute(
        select(func.count())
        .select_from(Booking)
        .where(
            Booking.room_type_id == room_type_id,
            Booking.status.in_(["pending", "confirmed", "checked_in"]),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
        .with_for_update()
    )
    blocking_count = result.scalar() or 0

    # Get total room count from Room service (cached or API call)
    total_rooms = await get_room_count(room_type_id)

    if blocking_count >= total_rooms:
        raise HTTPException(409, "No availability for selected dates")
```

### Pattern 3: State Machine Transitions
**What:** A single `transition_status` function validates and executes all booking state changes.

```python
VALID_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"checked_in", "cancelled"},
    "checked_in": {"checked_out"},
    "checked_out": set(),
    "cancelled": set(),
    "no_show": set(),
}

async def transition_booking(
    db: AsyncSession, booking: Booking, new_status: str, reason: str | None = None
) -> Booking:
    allowed = VALID_TRANSITIONS.get(booking.status, set())
    if new_status not in allowed:
        raise HTTPException(400, f"Cannot transition from {booking.status} to {new_status}")
    booking.status = new_status
    if new_status == "cancelled":
        booking.cancelled_at = datetime.now(timezone.utc)
        booking.cancellation_reason = reason
    # Publish state change event
    await publish_booking_event(booking, f"booking.{new_status}")
    await db.commit()
    return booking
```

### Pattern 4: RabbitMQ Event Publishing (must match Room service consumer)
**What:** Publish events to `booking.events` exchange with routing key `booking.*`.

The Room service consumer (`event_consumer.py`) expects this exact JSON payload:
```python
{
    "event_type": "booking.created",  # or booking.confirmed, booking.cancelled, etc.
    "booking_id": str(booking.id),    # UUID as string
    "room_type_id": str(booking.room_type_id),  # UUID as string
    "room_id": str(booking.room_id) if booking.room_id else None,  # UUID or null
    "check_in": booking.check_in.isoformat(),   # date as ISO string
    "check_out": booking.check_out.isoformat(),  # date as ISO string
    "status": booking.status,          # string: pending, confirmed, cancelled, etc.
    "guest_count": booking.guest_count  # integer, defaults to 1
}
```

**Critical:** The exchange name is `booking.events`, queue is `room.booking_projections`, routing key pattern is `booking.*`. The consumer uses `message.process()` for auto ack/nack.

### Pattern 5: Pricing Strategy
**Recommendation:** Call Room service API for pricing rather than replicating logic.

The Room service already has `calculate_stay_price(db, room_type_id, check_in, check_out, occupancy)` at endpoint `GET /api/v1/search/room-types/{id}?check_in=...&check_out=...&guests=...`. The Booking service should call this via httpx to get pricing, then snapshot the result into the booking record.

```python
async def get_pricing_from_room_service(
    room_type_id: uuid.UUID, check_in: date, check_out: date, guests: int
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{settings.ROOM_SERVICE_URL}/api/v1/search/room-types/{room_type_id}",
            params={"check_in": str(check_in), "check_out": str(check_out), "guests": guests},
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "total_price": Decimal(str(data["total_price"])),
            "price_per_night": Decimal(str(data["price_per_night"])),
            "currency": data["currency"],
            "nightly_breakdown": data.get("nightly_rates", []),
        }
```

### Pattern 6: Dual Expiry Cleanup
**What:** PENDING bookings auto-expire after 15 minutes via two mechanisms:
1. **Background task:** asyncio periodic task (every 5 min) queries and cancels expired bookings
2. **On-demand:** When any booking is accessed (GET), check if PENDING and expired, transition to CANCELLED

```python
# Background task in lifespan
async def expire_pending_bookings():
    while True:
        await asyncio.sleep(300)  # 5 minutes
        async with async_session_factory() as db:
            expired = await db.execute(
                select(Booking).where(
                    Booking.status == "pending",
                    Booking.expires_at < datetime.now(timezone.utc),
                )
            )
            for booking in expired.scalars():
                await transition_booking(db, booking, "cancelled", reason="expired")

# On-demand check in service layer
async def get_booking(db: AsyncSession, booking_id: uuid.UUID) -> Booking:
    booking = await db.get(Booking, booking_id)
    if booking and booking.status == "pending" and booking.expires_at < datetime.now(timezone.utc):
        await transition_booking(db, booking, "cancelled", reason="expired")
    return booking
```

### Anti-Patterns to Avoid
- **Direct status updates:** Never `booking.status = "confirmed"` outside the transition function
- **Price from client:** Never accept price in booking request body -- always compute server-side
- **Missing ownership check:** Every guest endpoint must verify `booking.user_id == current_user.sub`
- **Sync sleep for payment delay:** Use `await asyncio.sleep(2.5)` not `time.sleep()`
- **Forgetting to publish events:** Every state transition must publish a RabbitMQ event

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Email sending | SMTP client | fastapi-mail + ConnectionConfig.model_construct | Auth service pattern already handles Mailpit .local domain bypass |
| JWT verification | Token parsing | shared/jwt.py verify_token | Shared library, all services use it |
| RabbitMQ connections | Raw pika | shared/messaging.py helpers | Shared library with robust connections |
| Pricing calculation | Replicate rate engine | Call Room service API via httpx | Single source of truth; avoids drift |
| UUID generation | Custom ID schemes | uuid.uuid4() | Project standard, all models use UUID PKs |
| Password hashing | N/A for booking service | N/A | Booking service only verifies JWT, never handles passwords |

**Key insight:** The shared library and existing service patterns handle all infrastructure concerns. The Booking service's unique logic is the state machine, three-step flow, mock payment, and cancellation policy.

## Common Pitfalls

### Pitfall 1: Double-Booking Race Condition
**What goes wrong:** Two concurrent reservations for the last room both succeed.
**Why it happens:** Availability check and booking insert are separate non-locked operations.
**How to avoid:** SELECT ... FOR UPDATE on existing bookings within the same transaction as the insert. The Booking service counts its own blocking bookings against the Room service's room count.
**Warning signs:** No `with_for_update()` in the reservation path; tests only test sequential bookings.

### Pitfall 2: Event Schema Mismatch with Room Service
**What goes wrong:** Room service consumer crashes or silently drops events because the published event JSON does not match what `handle_booking_event` in `event_consumer.py` expects.
**Why it happens:** The event payload format is implicit -- there is no shared schema definition.
**How to avoid:** The event MUST contain exactly: `event_type` (str), `booking_id` (UUID str), `room_type_id` (UUID str), `room_id` (UUID str or null), `check_in` (ISO date str), `check_out` (ISO date str), `status` (str), `guest_count` (int). Test with the actual Room service consumer.
**Warning signs:** Missing `room_id` field (can be null but must be present); dates as datetime instead of date strings.

### Pitfall 3: BookingStatus Enum in Wrong Database
**What goes wrong:** The booking_status PostgreSQL ENUM type was created in the auth database migration, not the booking database. The Booking service's Alembic migration needs to create its own ENUM type in the booking_db.
**Why it happens:** Phase 1 created the ENUM in auth_db for "cross-service availability" but each service has its own database.
**How to avoid:** Define the BookingStatus enum as a Python enum in the Booking service models. Create the PostgreSQL ENUM type in the booking_db migration. Do NOT try to reference the auth_db enum.
**Warning signs:** Migration error "type booking_status does not exist" in booking_db.

### Pitfall 4: Pricing Snapshot Not Stored
**What goes wrong:** A rate change retroactively alters the price of a confirmed booking.
**Why it happens:** Price is recalculated from live rates instead of stored at confirmation time.
**How to avoid:** Store `total_price`, `price_per_night`, `currency`, and optionally a nightly breakdown JSON on the booking record at confirmation time. Modifications recalculate and update the snapshot.

### Pitfall 5: Expiry Race with Payment
**What goes wrong:** Background expiry task cancels a booking at the exact moment the guest submits payment.
**Why it happens:** No locking on the booking row during payment processing.
**How to avoid:** The payment endpoint must SELECT ... FOR UPDATE the booking row, verify it is still PENDING, then transition to CONFIRMED. If it was already cancelled (expired), return an error to the guest.

### Pitfall 6: Missing MAIL_SERVER Config in Booking Service
**What goes wrong:** Booking service cannot send confirmation emails because mail settings are not configured.
**Why it happens:** Mail settings exist in auth service config but not in booking service config.
**How to avoid:** Add all MAIL_* settings to booking service Settings class. Add MAIL_SERVER=mailpit and MAIL_PORT=1025 to docker-compose.yml booking service environment.

### Pitfall 7: Gateway Proxy Already Routes /api/v1/bookings
**What goes wrong:** Nothing breaks, but the gateway proxy already has `"/api/v1/bookings": settings.BOOKING_SERVICE_URL` in SERVICE_MAP.
**Why it's good:** The proxy catch-all already forwards booking requests. For BFF endpoints that aggregate data (e.g., booking + room details), add specific routes to a new `booking.py` BFF router BEFORE the catch-all proxy (same pattern as search.py).

## Code Examples

### Booking Model
```python
# services/booking/app/models/booking.py
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, Integer, Numeric, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class BookingStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    confirmation_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    room_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    room_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    guest_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(
        Enum(BookingStatus, name="booking_status", create_constraint=True),
        default=BookingStatus.PENDING,
        nullable=False,
    )
    # Price snapshot (set at confirmation)
    total_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_per_night: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    nightly_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Guest details (set at step 2)
    guest_first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guest_last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guest_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    guest_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    special_requests: Mapped[str | None] = mapped_column(Text, nullable=True)
    id_document: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Timing
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cancellation_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Payment Transaction Model
```python
# services/booking/app/models/payment.py
class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    transaction_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    card_last_four: Mapped[str] = mapped_column(String(4), nullable=False)
    card_brand: Mapped[str] = mapped_column(String(20), nullable=False)  # visa, mastercard
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # succeeded, declined, failed
    decline_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### Mock Payment Service
```python
# services/booking/app/services/payment.py
import asyncio
import uuid
from decimal import Decimal

TEST_CARDS = {
    "4242424242424242": {"status": "succeeded", "brand": "visa"},
    "4000000000000002": {"status": "declined", "brand": "visa", "reason": "card_declined"},
    "4111111111111111": {"status": "declined", "brand": "visa", "reason": "insufficient_funds"},
}

async def process_payment(
    card_number: str, amount: Decimal, currency: str = "USD"
) -> dict:
    """Simulate payment processing with 2-3s delay."""
    await asyncio.sleep(2.5)  # Simulated processing delay

    card_info = TEST_CARDS.get(card_number, {"status": "succeeded", "brand": "visa"})
    transaction_id = f"txn_{uuid.uuid4().hex[:16]}"

    return {
        "transaction_id": transaction_id,
        "status": card_info["status"],
        "brand": card_info["brand"],
        "last_four": card_number[-4:],
        "amount": amount,
        "currency": currency,
        "decline_reason": card_info.get("reason"),
    }
```

### Event Publisher
```python
# services/booking/app/services/event_publisher.py
import json
from aio_pika import Message, DeliveryMode
from shared.messaging import get_rabbitmq_connection, get_channel, declare_exchange

BOOKING_EXCHANGE = "booking.events"

async def publish_booking_event(booking, event_type: str, rabbitmq_url: str) -> None:
    """Publish a booking state change event to RabbitMQ."""
    payload = {
        "event_type": event_type,
        "booking_id": str(booking.id),
        "room_type_id": str(booking.room_type_id),
        "room_id": str(booking.room_id) if booking.room_id else None,
        "check_in": booking.check_in.isoformat(),
        "check_out": booking.check_out.isoformat(),
        "status": booking.status if isinstance(booking.status, str) else booking.status.value,
        "guest_count": booking.guest_count,
    }
    connection = await get_rabbitmq_connection(rabbitmq_url)
    try:
        channel = await get_channel(connection)
        exchange = await declare_exchange(channel, BOOKING_EXCHANGE)
        message = Message(
            body=json.dumps(payload).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=event_type)
    finally:
        await connection.close()
```

### Confirmation Number Generation
```python
import secrets
def generate_confirmation_number() -> str:
    """Generate a professional confirmation number like HB-A3X9K2."""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # No 0/O/1/I ambiguity
    code = "".join(secrets.choice(chars) for _ in range(6))
    return f"HB-{code}"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Store booking_status as string | PostgreSQL ENUM type with Python Enum | SQLAlchemy 2.0+ | Type safety, invalid states impossible at DB level |
| Sync background tasks | asyncio.create_task in lifespan | FastAPI lifespan pattern | No Celery dependency needed for simple periodic tasks |
| Blocking payment calls | await asyncio.sleep for mock delays | Always for async apps | Never use time.sleep in async context |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.x + pytest-asyncio |
| Config file | pyproject.toml (asyncio_mode = "auto") |
| Quick run command | `python -m pytest tests/booking/ -x -q` |
| Full suite command | `python -m pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BOOK-01 | Three-step booking flow (reserve -> details -> payment) | integration | `python -m pytest tests/booking/test_booking_flow.py -x` | Wave 0 |
| BOOK-02 | Mock payment with test cards (success + decline) | unit + integration | `python -m pytest tests/booking/test_payment.py -x` | Wave 0 |
| BOOK-03 | Confirmation number in booking response | integration | `python -m pytest tests/booking/test_booking_flow.py::test_confirmation_number -x` | Wave 0 |
| BOOK-04 | Confirmation email sent via Mailpit | unit | `python -m pytest tests/booking/test_email.py -x` | Wave 0 |
| BOOK-05 | Cancellation policy in booking response | integration | `python -m pytest tests/booking/test_cancellation.py::test_policy_displayed -x` | Wave 0 |
| MGMT-01 | List guest bookings with status filter | integration | `python -m pytest tests/booking/test_management.py::test_list_bookings -x` | Wave 0 |
| MGMT-02 | Cancel booking with policy enforcement | integration | `python -m pytest tests/booking/test_cancellation.py -x` | Wave 0 |
| MGMT-03 | Modify booking with price recalculation | integration | `python -m pytest tests/booking/test_modification.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/booking/ -x -q`
- **Per wave merge:** `python -m pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/booking/__init__.py` -- package init
- [ ] `tests/booking/conftest.py` -- booking service test fixtures (db session, mock user, mock room service)
- [ ] `tests/booking/test_booking_flow.py` -- covers BOOK-01, BOOK-03
- [ ] `tests/booking/test_payment.py` -- covers BOOK-02
- [ ] `tests/booking/test_email.py` -- covers BOOK-04
- [ ] `tests/booking/test_cancellation.py` -- covers BOOK-05, MGMT-02
- [ ] `tests/booking/test_management.py` -- covers MGMT-01
- [ ] `tests/booking/test_modification.py` -- covers MGMT-03
- [ ] `pyproject.toml` update: add `"services/booking"` to pythonpath
- [ ] Framework install: `pip install aio-pika fastapi-mail` in booking requirements.txt

## Open Questions

1. **Room count for availability check**
   - What we know: Booking service needs total room count per room_type_id to compare against blocking booking count
   - What's unclear: Whether to call Room service API at reservation time or cache/replicate room counts
   - Recommendation: Call Room service API (`GET /api/v1/rooms/types/{id}`) at reservation time. Cache with short TTL (60s) using a simple dict. Room counts rarely change.

2. **room_id field in booking events**
   - What we know: Room service consumer expects `room_id` (nullable). Individual room assignment happens at check-in (Phase 6).
   - What's unclear: Should room_id always be null in Phase 4 events?
   - Recommendation: Set `room_id = None` for all Phase 4 bookings. Room service consumer already handles null room_id. Staff will assign rooms in Phase 6.

3. **Cancellation fee payment**
   - What we know: Late cancellation incurs first-night charge. Transaction record stores fee amount.
   - What's unclear: Does the cancellation fee trigger a new mock payment charge?
   - Recommendation: Record the fee in `booking.cancellation_fee` and create a PaymentTransaction with type "cancellation_fee". No actual payment processing needed for the mock.

## Sources

### Primary (HIGH confidence)
- `services/room/app/services/event_consumer.py` -- Exact event schema the Booking service must publish
- `services/room/app/models/reservation.py` -- ReservationProjection model showing required fields
- `services/room/app/services/rate.py` -- Pricing engine (calculate_stay_price, calculate_nightly_rate)
- `services/room/app/services/availability.py` -- Availability logic showing BLOCKING_STATUSES and overlap detection
- `services/auth/app/services/email.py` -- Email pattern with model_construct bypass for .local domains
- `services/auth/app/models/user.py` -- BookingStatus enum definition (PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED, NO_SHOW)
- `shared/shared/messaging.py` -- RabbitMQ connection helpers
- `shared/shared/jwt.py` -- JWT verification function
- `shared/shared/database.py` -- Async engine + session factory
- `services/room/app/api/deps.py` -- Claims-based JWT auth pattern to replicate
- `services/room/app/core/database.py` -- Database setup pattern to replicate
- `services/room/app/core/config.py` -- Settings pattern to replicate
- `services/gateway/app/api/proxy.py` -- Gateway already routes /api/v1/bookings to booking service
- `docker-compose.yml` -- booking_db on port 5435, BOOKING_SERVICE_URL configured in gateway

### Secondary (MEDIUM confidence)
- `.planning/research/ARCHITECTURE.md` -- State machine pattern, pessimistic locking approach
- `.planning/research/PITFALLS.md` -- Double-booking prevention, date range logic, pricing consistency

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already used in other services
- Architecture: HIGH -- follows established service patterns, event contract is explicitly defined
- Pitfalls: HIGH -- all pitfalls verified against actual codebase behavior
- Event integration: HIGH -- exact schema visible in Room service consumer code

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable -- patterns established, no external dependencies)

---
*Phase 4: Booking Engine research for HotelBook*
*Researched: 2026-03-21*
