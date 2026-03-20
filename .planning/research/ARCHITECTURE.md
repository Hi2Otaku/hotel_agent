# Architecture Research

**Domain:** Hotel reservation system (single property, guest booking + staff dashboard)
**Researched:** 2026-03-20
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  ┌──────────────────────┐     ┌──────────────────────┐              │
│  │  Guest Booking SPA   │     │  Staff Dashboard SPA │              │
│  │  (React + Vite)      │     │  (React + Vite)      │              │
│  └──────────┬───────────┘     └──────────┬───────────┘              │
│             │                            │                          │
├─────────────┴────────────────────────────┴──────────────────────────┤
│                        API LAYER (FastAPI)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Auth    │  │ Booking  │  │  Room    │  │ Reporting │            │
│  │  Router  │  │  Router  │  │  Router  │  │  Router   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │              │              │              │                 │
├───────┴──────────────┴──────────────┴──────────────┴────────────────┤
│                        SERVICE LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Auth    │  │ Booking  │  │  Room    │  │ Reporting │            │
│  │  Service │  │  Service │  │  Service │  │  Service  │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
│       │              │              │              │                 │
├───────┴──────────────┴──────────────┴──────────────┴────────────────┤
│                        DATA LAYER                                   │
│  ┌──────────────────────────────────────────────────┐               │
│  │          SQLAlchemy ORM + Alembic Migrations      │               │
│  └──────────────────────┬────────────────────────────┘               │
│                         │                                           │
│  ┌──────────────────────┴────────────────────────────┐               │
│  │               PostgreSQL Database                  │               │
│  └────────────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Guest Booking SPA | Room search, booking flow, guest account management | React + React Router, date pickers, form wizards |
| Staff Dashboard SPA | Booking management, room/rate CRUD, reports, guest profiles | React + React Router, data tables, charts |
| Auth Router | Login, registration, token refresh, role verification | FastAPI router + JWT tokens (python-jose or PyJWT) |
| Booking Router | Create/read/update/cancel reservations, check-in/out | FastAPI router, Pydantic schemas for validation |
| Room Router | Room types, availability queries, rate management | FastAPI router, date-range availability queries |
| Reporting Router | Occupancy stats, revenue reports, booking trends | FastAPI router, aggregation queries |
| Auth Service | Password hashing, JWT creation, role-based access | passlib + bcrypt, role enum (guest/staff/admin) |
| Booking Service | Availability validation, reservation state machine, overbooking prevention | Core business logic, DB transaction management |
| Room Service | Room inventory, rate calculations, seasonal pricing | Pricing engine, availability calendar logic |
| Reporting Service | Data aggregation, metric calculation | SQL aggregation queries, date-range filtering |
| SQLAlchemy ORM | Object-relational mapping, query building | Async SQLAlchemy 2.0 with asyncpg driver |
| Alembic | Schema versioning, database migrations | Migration scripts, auto-generation from models |
| PostgreSQL | Persistent storage, ACID transactions, row locking | Primary datastore, handles concurrency |

## Recommended Project Structure

### Backend (FastAPI)

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic configuration
├── app/
│   ├── main.py                 # FastAPI app creation, middleware, startup
│   ├── core/
│   │   ├── config.py           # Pydantic BaseSettings (env vars)
│   │   ├── security.py         # JWT creation, password hashing
│   │   └── database.py         # Engine, session factory, Base
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py             # Guest and Staff models
│   │   ├── room.py             # Room, RoomType models
│   │   ├── booking.py          # Booking model with state machine
│   │   ├── payment.py          # Payment record model
│   │   └── rate.py             # Rate and seasonal pricing models
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── booking.py
│   │   └── payment.py
│   ├── api/
│   │   ├── deps.py             # Shared dependencies (get_db, get_current_user)
│   │   └── v1/
│   │       ├── auth.py         # Auth endpoints
│   │       ├── bookings.py     # Booking endpoints
│   │       ├── rooms.py        # Room/availability endpoints
│   │       ├── rates.py        # Rate management endpoints
│   │       ├── guests.py       # Guest profile endpoints (staff)
│   │       └── reports.py      # Reporting endpoints (staff)
│   └── services/               # Business logic layer
│       ├── auth.py
│       ├── booking.py
│       ├── room.py
│       ├── payment.py
│       └── reporting.py
├── tests/
│   ├── conftest.py             # Fixtures, test DB setup
│   ├── test_auth.py
│   ├── test_bookings.py
│   └── test_rooms.py
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

### Frontend (React)

```
frontend/
├── src/
│   ├── main.tsx                # Entry point
│   ├── App.tsx                 # Root component, routing setup
│   ├── api/                    # API client layer
│   │   ├── client.ts           # Axios/fetch wrapper, auth interceptor
│   │   ├── bookings.ts         # Booking API calls
│   │   ├── rooms.ts            # Room/availability API calls
│   │   └── auth.ts             # Auth API calls
│   ├── components/             # Shared/reusable components
│   │   ├── ui/                 # Buttons, inputs, modals, cards
│   │   ├── layout/             # Header, footer, sidebar, page shells
│   │   └── booking/            # Booking-specific shared components
│   ├── pages/                  # Route-level page components
│   │   ├── guest/              # Guest-facing pages
│   │   │   ├── HomePage.tsx
│   │   │   ├── SearchPage.tsx
│   │   │   ├── RoomDetailPage.tsx
│   │   │   ├── BookingFlowPage.tsx
│   │   │   ├── ConfirmationPage.tsx
│   │   │   └── MyBookingsPage.tsx
│   │   └── staff/              # Staff dashboard pages
│   │       ├── DashboardPage.tsx
│   │       ├── BookingsPage.tsx
│   │       ├── RoomsPage.tsx
│   │       ├── RatesPage.tsx
│   │       ├── GuestsPage.tsx
│   │       └── ReportsPage.tsx
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useBooking.ts
│   │   └── useAvailability.ts
│   ├── context/                # React Context providers
│   │   ├── AuthContext.tsx
│   │   └── BookingContext.tsx
│   ├── types/                  # TypeScript interfaces
│   │   └── index.ts
│   └── utils/                  # Helpers (date formatting, price calc)
│       └── index.ts
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

### Structure Rationale

- **backend/app/api/v1/:** API versioning from the start. Routers grouped by domain resource, not by HTTP method.
- **backend/app/services/:** Business logic separated from HTTP layer. Routers call services; services call the ORM. This keeps routers thin and testable.
- **backend/app/models/ vs schemas/:** SQLAlchemy models (DB shape) are separate from Pydantic schemas (API shape). They diverge as the project grows.
- **frontend/src/api/:** Centralized API client with auth token injection. Pages never call fetch directly.
- **frontend/src/pages/guest/ vs staff/:** Clear separation between two user experiences. They share components but have distinct page structures and navigation.

## Architectural Patterns

### Pattern 1: Three-Layer Backend (Router -> Service -> ORM)

**What:** Routers handle HTTP concerns (request parsing, response codes). Services contain business logic. ORM models handle persistence. No layer skips another.
**When to use:** Always -- this is the default for any non-trivial FastAPI app.
**Trade-offs:** Slightly more files than putting logic in routers. Massively easier to test and refactor.

**Example:**
```python
# api/v1/bookings.py (Router - thin, HTTP only)
@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.create_booking(db, current_user.id, data)

# services/booking.py (Service - business logic)
async def create_booking(
    db: AsyncSession, user_id: int, data: BookingCreate
) -> Booking:
    await _validate_availability(db, data.room_type_id, data.check_in, data.check_out)
    booking = Booking(user_id=user_id, status=BookingStatus.PENDING, **data.dict())
    db.add(booking)
    await db.commit()
    return booking
```

### Pattern 2: Booking State Machine

**What:** Reservations transition through explicit states: PENDING -> CONFIRMED -> CHECKED_IN -> CHECKED_OUT (or CANCELLED from PENDING/CONFIRMED). Each transition has validation rules.
**When to use:** Always for booking/reservation systems. Ad-hoc status strings cause bugs.
**Trade-offs:** More upfront design, but prevents invalid state transitions that cause data corruption.

**Example:**
```python
# models/booking.py
class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

VALID_TRANSITIONS = {
    BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
    BookingStatus.CONFIRMED: [BookingStatus.CHECKED_IN, BookingStatus.CANCELLED],
    BookingStatus.CHECKED_IN: [BookingStatus.CHECKED_OUT],
    BookingStatus.CHECKED_OUT: [],
    BookingStatus.CANCELLED: [],
}
```

### Pattern 3: Pessimistic Locking for Availability

**What:** Use PostgreSQL `SELECT ... FOR UPDATE` when checking and reserving room availability within a single transaction. This prevents two concurrent requests from double-booking the same room.
**When to use:** Any write path that checks availability then creates a reservation.
**Trade-offs:** Slightly slower under contention (requests queue up for locked rows). For a single-property hotel, contention is negligible. Correctness is non-negotiable.

**Example:**
```python
# services/booking.py
async def _validate_availability(
    db: AsyncSession, room_type_id: int, check_in: date, check_out: date
):
    """Check availability with row locking to prevent double-booking."""
    result = await db.execute(
        select(RoomInventory)
        .where(
            RoomInventory.room_type_id == room_type_id,
            RoomInventory.date >= check_in,
            RoomInventory.date < check_out,
        )
        .with_for_update()  # Lock rows until transaction completes
    )
    inventory_rows = result.scalars().all()
    for row in inventory_rows:
        if row.available_count <= 0:
            raise HTTPException(409, f"No availability on {row.date}")
        row.available_count -= 1  # Decrement within locked transaction
```

### Pattern 4: Dependency Injection via FastAPI Depends

**What:** Use FastAPI's `Depends()` for database sessions, current user extraction, and role checking. Compose dependencies for clean, declarative endpoint signatures.
**When to use:** Every endpoint that needs DB access, authentication, or authorization.
**Trade-offs:** None -- this is FastAPI's core design pattern. Use it everywhere.

**Example:**
```python
# api/deps.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_jwt(token)
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(401, "Invalid token")
    return user

def require_role(role: UserRole):
    async def checker(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return checker
```

## Data Flow

### Guest Booking Flow (Primary Happy Path)

```
Guest Browser                    FastAPI Backend                  PostgreSQL
     │                                │                              │
     │  GET /rooms/availability       │                              │
     │  ?check_in=...&check_out=...   │                              │
     │ ─────────────────────────────> │                              │
     │                                │  SELECT room_types + counts  │
     │                                │ ────────────────────────────> │
     │                                │ <──────────────────────────── │
     │ <───────────────────────────── │                              │
     │  [Available room types + rates]│                              │
     │                                │                              │
     │  POST /bookings               │                              │
     │  {room_type, dates, guest}     │                              │
     │ ─────────────────────────────> │                              │
     │                                │  BEGIN TRANSACTION           │
     │                                │  SELECT ... FOR UPDATE       │
     │                                │  (lock inventory rows)       │
     │                                │ ────────────────────────────> │
     │                                │  INSERT booking (PENDING)    │
     │                                │  Decrement available_count   │
     │                                │  COMMIT                      │
     │                                │ ────────────────────────────> │
     │ <───────────────────────────── │                              │
     │  [Booking: PENDING, id=123]    │                              │
     │                                │                              │
     │  POST /bookings/123/payment    │                              │
     │  {mock_card_details}           │                              │
     │ ─────────────────────────────> │                              │
     │                                │  Validate mock payment       │
     │                                │  INSERT payment record       │
     │                                │  UPDATE booking -> CONFIRMED │
     │                                │ ────────────────────────────> │
     │ <───────────────────────────── │                              │
     │  [Booking: CONFIRMED]          │                              │
     │  [Mock email triggered]        │                              │
```

### Staff Check-in Flow

```
Staff Browser                    FastAPI Backend                  PostgreSQL
     │                                │                              │
     │  GET /staff/bookings           │                              │
     │  ?status=confirmed&date=today  │                              │
     │ ─────────────────────────────> │                              │
     │                                │  SELECT bookings             │
     │                                │  WHERE check_in = today      │
     │                                │  AND status = CONFIRMED      │
     │                                │ ────────────────────────────> │
     │ <───────────────────────────── │                              │
     │  [Today's arriving guests]     │                              │
     │                                │                              │
     │  PATCH /staff/bookings/123     │                              │
     │  {status: "checked_in"}        │                              │
     │ ─────────────────────────────> │                              │
     │                                │  Validate state transition   │
     │                                │  UPDATE booking status       │
     │                                │  UPDATE room -> OCCUPIED     │
     │                                │ ────────────────────────────> │
     │ <───────────────────────────── │                              │
     │  [Booking: CHECKED_IN]         │                              │
```

### Frontend State Management

```
AuthContext (global)
    │
    ├── JWT token storage
    ├── Current user info + role
    └── Login/logout actions
         │
         ├── Guest Routes ──── BookingContext (booking flow only)
         │                        │
         │                        ├── Selected dates
         │                        ├── Selected room type
         │                        ├── Guest details form state
         │                        └── Payment step state
         │
         └── Staff Routes ──── React Query / TanStack Query
                                  │
                                  ├── Server state caching
                                  ├── Automatic refetching
                                  └── Optimistic updates
```

Use React Context sparingly: AuthContext for global auth state, BookingContext for the multi-step booking wizard. For server data (room lists, booking tables, reports), use TanStack Query -- it handles caching, loading states, and refetching better than manual state management.

### Key Data Flows

1. **Availability Search:** Guest selects dates -> API aggregates room inventory for date range -> returns available room types with lowest rate per type -> frontend renders cards with pricing.
2. **Booking Creation:** Multi-step form collects room + dates + guest details + payment -> single POST creates booking in PENDING state -> mock payment endpoint confirms it -> status transitions to CONFIRMED.
3. **Staff Dashboard:** Polling or manual refresh fetches today's arrivals, current occupancy, pending checkouts -> staff actions trigger state transitions via PATCH endpoints.
4. **Reporting:** Staff selects date range -> API runs aggregation queries (occupancy %, revenue, ADR) -> returns computed metrics -> frontend renders charts.

## Database Schema (Core Entities)

```
┌──────────────┐     ┌───────────────┐     ┌──────────────────┐
│    users     │     │  room_types   │     │  room_inventory  │
├──────────────┤     ├───────────────┤     ├──────────────────┤
│ id (PK)      │     │ id (PK)       │     │ id (PK)          │
│ email        │     │ name          │     │ room_type_id (FK)│
│ password_hash│     │ description   │     │ date             │
│ first_name   │     │ base_rate     │     │ total_count      │
│ last_name    │     │ max_occupancy │     │ available_count  │
│ phone        │     │ amenities     │     │ rate_override    │
│ role (enum)  │     │ image_urls    │     └──────────────────┘
│ created_at   │     │ is_active     │
└──────┬───────┘     └───────┬───────┘
       │                     │
       │    ┌────────────────┘
       │    │
┌──────┴────┴──┐     ┌──────────────┐
│   bookings   │     │   payments   │
├──────────────┤     ├──────────────┤
│ id (PK)      │     │ id (PK)      │
│ user_id (FK) │     │ booking_id   │
│ room_type_id │     │ amount       │
│ check_in     │     │ method       │
│ check_out    │     │ status       │
│ num_guests   │     │ mock_txn_id  │
│ total_price  │     │ created_at   │
│ status (enum)│     └──────────────┘
│ special_reqs │
│ created_at   │
│ updated_at   │
└──────────────┘
```

**Key design decision:** Use a `room_inventory` table (room_type_id + date -> available_count) rather than tracking individual room assignments. For a single property, this is simpler and sufficient. Individual room numbers only matter at check-in, where staff can assign a specific room. This avoids the complexity of modeling every physical room as a DB row for availability purposes.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Portfolio demo (10-50 users) | Monolith is perfect. Single FastAPI process, single PostgreSQL instance. No caching needed. |
| Small hotel in production (100-500 concurrent) | Add Redis for session caching and rate limiting. Consider background task queue (Celery or FastAPI BackgroundTasks) for email sending. |
| Multi-property expansion (1k+) | Would need tenant isolation, search service (Elasticsearch), CDN for images, separate read replicas. Out of scope for this project. |

### Scaling Priorities (if this were production)

1. **First bottleneck:** Database connections under concurrent booking load. Fix with connection pooling (asyncpg pool, already built into SQLAlchemy async).
2. **Second bottleneck:** Availability search queries on large date ranges. Fix with materialized views or caching layer. Not relevant at portfolio scale.

## Anti-Patterns

### Anti-Pattern 1: Business Logic in Routers

**What people do:** Put availability checks, price calculations, and state transitions directly in FastAPI route handlers.
**Why it's wrong:** Routers become untestable monoliths. You cannot unit test business logic without spinning up HTTP. Duplicate logic across similar endpoints.
**Do this instead:** Routers parse requests and return responses. Services contain all logic. Test services directly with a DB session fixture.

### Anti-Pattern 2: Checking Availability Without Locking

**What people do:** Query available count, then in a separate statement create the booking. Two concurrent requests both see "1 available" and both book it.
**Why it's wrong:** Race condition causes overbooking. The single most critical correctness bug in any reservation system.
**Do this instead:** `SELECT ... FOR UPDATE` within a transaction. Check and decrement atomically. PostgreSQL handles the serialization.

### Anti-Pattern 3: Storing Booking Status as Free-Form String

**What people do:** Use `status = "confirmed"` as a plain string column, set it to whatever value wherever.
**Why it's wrong:** Typos create invisible bugs. No validation of transitions. "Confrimed" and "confirmed" are different values. Impossible to reason about valid states.
**Do this instead:** Use a Python Enum mapped to a PostgreSQL ENUM type. Define valid transitions in a dictionary. Validate every transition in the service layer.

### Anti-Pattern 4: Prop Drilling Through Booking Wizard

**What people do:** Pass booking state (dates, room, guest info, payment) through 4-5 levels of React components via props.
**Why it's wrong:** Fragile, verbose, hard to modify. Adding a field means touching every intermediate component.
**Do this instead:** Use a BookingContext provider that wraps the booking flow pages. Each step reads/writes context directly.

### Anti-Pattern 5: One Giant React Component Per Page

**What people do:** Build SearchPage as a single 500-line component with inline API calls, state, and rendering.
**Why it's wrong:** Impossible to reuse, test, or maintain. Violates component composition -- React's core strength.
**Do this instead:** Decompose into container (data-fetching) and presentational (rendering) components. Extract hooks for reusable logic.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Mock Payment Provider | Service layer simulates Stripe-like request/response cycle | Return mock transaction IDs, simulate success/failure states. Build the interface as if calling a real API so swapping in Stripe later is trivial. |
| Mock Email Service | FastAPI BackgroundTasks or simple async function | Log email content to console/DB in dev. Structure as a service so replacing with SendGrid/SES later requires changing one module. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| React SPA <-> FastAPI | REST API over HTTPS, JWT Bearer tokens | API client module centralizes all HTTP calls. Never scatter fetch() calls across components. |
| FastAPI Routers <-> Services | Direct Python function calls | Services receive DB session and typed data. Never HTTP between layers. |
| Services <-> Database | SQLAlchemy async ORM | Services use ORM models for writes, may use raw SQL for complex reporting queries. |
| Guest app <-> Staff app | Shared API, separate frontend route trees | Same FastAPI backend. Role-based access controls which endpoints each role can reach. Could be same React app with role-based routing, or two separate builds. Single app with role routing is simpler. |

## Build Order (Dependencies)

This ordering reflects technical dependencies -- each phase requires the previous one to be functional.

1. **Database models + migrations first** -- Everything depends on the data layer. Define models, set up Alembic, seed sample data.
2. **Auth system second** -- Every subsequent endpoint needs authentication. JWT issuance, password hashing, role checking.
3. **Room/availability API third** -- Booking depends on being able to query what is available. Room types, inventory, rate queries.
4. **Booking API fourth** -- Core transaction: create reservation, state machine, overbooking prevention. Depends on rooms + auth.
5. **Mock payment fifth** -- Confirms bookings. Depends on booking existing in PENDING state.
6. **Guest frontend sixth** -- Consumes the API built in steps 2-5. Search, book, manage reservations.
7. **Staff API endpoints seventh** -- CRUD for rooms/rates, booking management, guest profiles, reporting queries.
8. **Staff dashboard eighth** -- Consumes staff API. Tables, forms, charts.
9. **Polish ninth** -- Email mocks, responsive design, error handling, loading states, CI/CD, deployment.

## Sources

- [FastAPI Best Practices (zhanymkanov)](https://github.com/zhanymkanov/fastapi-best-practices) -- project structure conventions
- [FastAPI Official Docs: Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) -- router organization
- [FastAPI Official Docs: SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) -- SQLAlchemy integration patterns
- [Design Hotel Booking System (System Design Handbook)](https://www.systemdesignhandbook.com/guides/design-hotel-booking-system/) -- system components and data flow
- [Hotel Reservation Schema Design (PostgreSQL)](https://dev.to/chandra179/hotel-reservation-schema-design-postgresql-3i9j) -- schema patterns
- [Data Model for Hotel Management System (Red Gate)](https://www.red-gate.com/blog/data-model-for-hotel-management-system/) -- entity relationships
- [How to Solve Race Conditions in a Booking System (HackerNoon)](https://hackernoon.com/how-to-solve-race-conditions-in-a-booking-system) -- pessimistic locking patterns
- [Handling the Double-Booking Problem in Databases](https://adamdjellouli.com/articles/databases_notes/07_concurrency_control/04_double_booking_problem) -- concurrency control
- [Setting up FastAPI with Async SQLAlchemy 2.0](https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308) -- async patterns

---
*Architecture research for: HotelBook - single property hotel reservation system*
*Researched: 2026-03-20*
