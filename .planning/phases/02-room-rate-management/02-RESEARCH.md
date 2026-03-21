# Phase 2: Room & Rate Management - Research

**Researched:** 2026-03-21
**Domain:** Room inventory management, rate/pricing engine, file storage (MinIO), room status lifecycle
**Confidence:** HIGH

## Summary

Phase 2 builds the Room service from its current stub (`services/room/app/main.py` with only a health endpoint) into a full CRUD service for room types, individual rooms, rates, seasonal pricing, and room status lifecycle. The service follows the exact same three-layer architecture established in Phase 1's auth service: `api/v1/*.py` (routes) -> `services/*.py` (business logic) -> `models/*.py` (ORM). It gets its own PostgreSQL database (`room_db` on port 5434, already in docker-compose.yml) and needs MinIO added for photo uploads.

Key technical domains: SQLAlchemy models with JSON columns for amenities/bed config, PostgreSQL ENUM types for room status, Decimal-based pricing with multiplicative rate stacking, MinIO S3-compatible file uploads via the `minio` Python SDK, Alembic async migrations, and a seed data script for 50-60 beach resort rooms. The room service authenticates requests by verifying JWTs with the shared public key (same pattern as `shared/shared/jwt.py`).

**Primary recommendation:** Follow auth service patterns exactly for project structure, config, database setup, deps, and migration. Use `sa.Numeric(10, 2)` for all monetary columns. Model amenities and bed config as PostgreSQL JSONB columns. Use the `minio` Python SDK (synchronous, wrapped in `run_in_executor` for the few upload endpoints) rather than adding a full async dependency.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- 3-4 room types for a beach resort: Ocean View, Garden Room, Junior Suite, Villa (or similar)
- Amenities modeled as categorized groups (Comfort: AC/Heating, Tech: WiFi/TV, Bathroom: Tub/Shower, etc.)
- Photos handled via file upload to MinIO (S3-compatible) -- add MinIO container to Docker Compose
- Capacity is detailed: max adults + max children + structured bed configuration [{type: "king", count: 1}]
- 7 statuses: Available, Occupied, Cleaning, Inspected, Maintenance, Out of Order, Reserved
- Role-based transitions with specific role assignments per transition type
- Automatic transitions: Checkout -> Cleaning, Inspection complete -> Available, Booking confirmed + assigned -> Reserved
- Manual override always available for managers/admins
- Status board: grid layout grouped by floor, color-coded by status
- Status change history logged with who/when timestamps
- Base rates per room type with occupancy tiers (1-2 guests = base, 3+ = higher rate)
- Seasonal pricing: date-range overrides with multiplier (e.g., "Summer Peak: Jun 1 - Aug 31, 1.3x")
- Weekend surcharges: per room type, as a multiplier (e.g., Suite: 1.2x on Fri-Sat)
- Stacking: multiplicative (summer 1.3x x weekend 1.15x = 1.495x)
- No minimum stay rules in this phase
- Currency: configurable by admin (stored as ISO 4217 code)
- Full demo data: 50-60 rooms, Unsplash URLs, sample seasonal rates
- Seed runs on first boot or via management command

### Claude's Discretion
- Exact room type names and descriptions for the beach resort theme
- Amenity category names and which amenities go in each
- MinIO bucket naming and upload path conventions
- Status transition validation logic implementation
- Exact seed data quantities and pricing numbers
- Status board color scheme for each status

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RMGT-01 | Staff can create/edit/delete room types (with photos, amenities, capacity) | SQLAlchemy models with JSONB for amenities/bed config, MinIO for photo uploads, CRUD service pattern from auth |
| RMGT-02 | Staff can manage individual rooms (number, floor, status) | Room model with FK to RoomType, status ENUM, floor/number columns, unique constraint on room_number |
| RMGT-03 | Staff can view room status board (occupied, vacant, cleaning, maintenance) | Query rooms grouped by floor, return status for color-coding, filter/aggregate endpoint |
| RMGT-04 | Housekeeping status tracking (auto-mark dirty on checkout, clean/inspected toggle) | Status transition state machine with role-based validation, status_change_log table for audit |
| RATE-01 | Staff can set base rates per room type | BaseRate model with room_type_id, occupancy_tier, amount (Numeric 10,2), currency ISO 4217 |
| RATE-02 | Staff can create seasonal pricing rules (date-range overrides, weekend surcharges) | SeasonalRate model with date ranges + multiplier, WeekendSurcharge model, multiplicative stacking logic |
</phase_requirements>

## Standard Stack

### Core (Room Service)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.135.x | API framework | Already in room service requirements.txt |
| SQLAlchemy | 2.0.48+ | ORM with async | Already in room service requirements.txt, JSONB column support built-in |
| asyncpg | latest | PostgreSQL async driver | Already in room service requirements.txt |
| Alembic | 1.18.x | Database migrations | Must be added to room requirements.txt (currently missing) |
| Pydantic | 2.12.x | Request/response schemas | Ships with FastAPI |
| pydantic-settings | 2.x | Environment config | Already in room service requirements.txt |
| PyJWT[crypto] | 2.x | JWT verification (public key only) | Must be added for token verification |
| minio | 7.2.x | S3-compatible file uploads | New dependency for photo uploads |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-multipart | (bundled with FastAPI) | File upload parsing | Required for UploadFile endpoints |
| Pillow | latest | Image validation/thumbnails | Optional -- validate uploaded files are actual images |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| minio SDK | boto3 | boto3 is larger (full AWS SDK), minio SDK is purpose-built and lighter. Both work with MinIO. Use minio SDK for simplicity. |
| minio SDK (sync) | miniopy-async | miniopy-async is a community fork, smaller ecosystem. The sync minio SDK works fine for file uploads (few endpoints, use run_in_executor). |
| JSONB for amenities | Separate amenities table (M2M) | M2M is more normalized but adds complexity for what is essentially a read-heavy display list. JSONB is simpler for categorized amenity lists. |

### New Dependencies for requirements.txt

```
# Add to services/room/requirements.txt
alembic>=1.18.0
PyJWT[crypto]>=2.12.0
minio>=7.2.0
python-multipart
```

## Architecture Patterns

### Room Service Project Structure

```
services/room/
├── alembic/
│   ├── versions/
│   │   └── 001_initial_room_models.py
│   └── env.py
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, lifespan for seed data
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings (DB, MinIO, JWT)
│   │   ├── database.py          # Engine/session from shared lib
│   │   └── storage.py           # MinIO client singleton
│   ├── models/
│   │   ├── __init__.py
│   │   ├── room_type.py         # RoomType model
│   │   ├── room.py              # Room model + RoomStatus enum
│   │   ├── rate.py              # BaseRate, SeasonalRate, WeekendSurcharge
│   │   └── status_log.py        # RoomStatusChange audit log
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── room_type.py         # RoomType CRUD schemas
│   │   ├── room.py              # Room CRUD + status board schemas
│   │   └── rate.py              # Rate CRUD schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # get_db, get_current_user, require_role (replicate auth pattern)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── room_types.py    # Room type CRUD + photo upload
│   │       ├── rooms.py         # Room CRUD + status transitions + status board
│   │       └── rates.py         # Base rate + seasonal + weekend surcharge CRUD
│   └── services/
│       ├── __init__.py
│       ├── room_type.py         # Room type business logic
│       ├── room.py              # Room CRUD + status machine
│       ├── rate.py              # Rate management + price calculation
│       ├── storage.py           # MinIO upload/delete operations
│       └── seed.py              # Seed data for beach resort
├── entrypoint.sh                # Run migrations + start uvicorn
├── Dockerfile
└── requirements.txt
```

### Pattern 1: Room Status State Machine

**What:** Explicit allowed transitions dictionary with role-based validation.
**When to use:** Every status change on a room.

```python
from enum import Enum as PyEnum

class RoomStatus(str, PyEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    INSPECTED = "inspected"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"
    RESERVED = "reserved"

# role -> set of (from_status, to_status) tuples
ROLE_TRANSITIONS = {
    "front_desk": {
        (RoomStatus.AVAILABLE, RoomStatus.OCCUPIED),
        (RoomStatus.OCCUPIED, RoomStatus.AVAILABLE),
        (RoomStatus.RESERVED, RoomStatus.OCCUPIED),  # check-in
    },
    "housekeeping": {
        (RoomStatus.CLEANING, RoomStatus.INSPECTED),
    },
    "manager": None,  # None = all transitions allowed
    "admin": None,     # None = all transitions allowed
}

AUTO_TRANSITIONS = {
    # trigger_event -> (from_status, to_status)
    "checkout": (RoomStatus.OCCUPIED, RoomStatus.CLEANING),
    "inspection_complete": (RoomStatus.INSPECTED, RoomStatus.AVAILABLE),
    "booking_assigned": (RoomStatus.AVAILABLE, RoomStatus.RESERVED),
}
```

### Pattern 2: JSONB for Amenities and Bed Config

**What:** Store structured but schema-flexible data as PostgreSQL JSONB.
**When to use:** Amenities (categorized list) and bed configuration (array of {type, count}).

```python
from sqlalchemy import String, Integer, ARRAY
from sqlalchemy.dialects.postgresql import JSONB

class RoomType(Base):
    __tablename__ = "room_types"

    # ... id, name, description columns ...

    # JSONB for categorized amenities:
    # {"Comfort": ["AC", "Heating", "Mini Bar"], "Tech": ["WiFi", "Smart TV"], ...}
    amenities: Mapped[dict] = mapped_column(JSONB, default=dict)

    # JSONB for bed configuration:
    # [{"type": "king", "count": 1}, {"type": "twin", "count": 2}]
    bed_config: Mapped[list] = mapped_column(JSONB, default=list)

    max_adults: Mapped[int] = mapped_column(Integer, nullable=False)
    max_children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
```

### Pattern 3: Multiplicative Rate Stacking

**What:** Calculate final nightly rate by applying base rate, then multiplying by seasonal and weekend multipliers.
**When to use:** Any rate calculation for a given room type on a given date.

```python
from decimal import Decimal

async def calculate_nightly_rate(
    db: AsyncSession,
    room_type_id: uuid.UUID,
    date: date,
    occupancy: int,
) -> Decimal:
    """Calculate the rate for one night, applying all applicable multipliers."""
    # 1. Get base rate for occupancy tier
    base = await get_base_rate(db, room_type_id, occupancy)

    # 2. Check for seasonal multiplier
    seasonal = await get_seasonal_multiplier(db, room_type_id, date)

    # 3. Check for weekend surcharge
    weekend = await get_weekend_multiplier(db, room_type_id, date)

    # Multiplicative stacking
    return (base * seasonal * weekend).quantize(Decimal("0.01"))
```

### Pattern 4: MinIO File Upload

**What:** Upload room photos to MinIO S3-compatible storage, return public URL.
**When to use:** Room type photo management endpoints.

```python
from minio import Minio
import uuid

# In core/storage.py - singleton client
def get_minio_client(settings) -> Minio:
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,      # "minio:9000"
        access_key=settings.MINIO_ACCESS_KEY,   # "minioadmin"
        secret_key=settings.MINIO_SECRET_KEY,   # "minioadmin"
        secure=False,                            # HTTP in dev
    )

# In services/storage.py - upload logic
async def upload_photo(
    client: Minio,
    bucket: str,
    file: UploadFile,
) -> str:
    """Upload a file to MinIO, return the object path."""
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    object_name = f"room-photos/{uuid.uuid4()}.{ext}"

    # minio SDK is sync -- use run_in_executor for async context
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: client.put_object(
            bucket,
            object_name,
            file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        ),
    )
    return object_name
```

### Pattern 5: JWT Verification in Non-Auth Service

**What:** Room service verifies JWTs using only the public key, replicating auth service's deps.py pattern.
**When to use:** Every authenticated endpoint in the room service.

```python
# Room service api/deps.py -- adapted from auth service
import jwt
from shared.jwt import verify_token

async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> dict:
    """Verify JWT and return payload. No DB lookup needed -- trust the token claims."""
    try:
        payload = verify_token(token, public_key)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
    return payload  # {"sub": uuid, "role": "admin", "email": "..."}

def require_role(*roles: str):
    async def checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return checker
```

**Key difference from auth service:** The room service does NOT have a User table. It trusts JWT claims directly (sub, role, email) without a DB lookup. This is the correct microservice pattern -- each service owns its own data.

### Anti-Patterns to Avoid

- **Using Float for pricing:** Float arithmetic causes rounding errors. Use `Decimal` in Python and `Numeric(10, 2)` in PostgreSQL for all monetary values.
- **Storing photo files in the database:** Use MinIO/S3 for binary storage, store only the object path/URL in the DB.
- **Direct status updates without validation:** Every status change MUST go through the state machine validation function. No direct `room.status = new_status` outside the service layer.
- **Hardcoding room types in code:** Room types are database records, not code constants. The seed script creates them, but staff can add/edit/delete them.
- **Accepting rate amounts from untrusted input without Decimal conversion:** Always parse incoming rate values through Pydantic with `Decimal` type to prevent floating point contamination.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| S3-compatible file storage | Custom file upload to disk | MinIO + minio SDK | S3 API is an industry standard; MinIO provides it locally in Docker |
| UUID generation | Custom ID schemes | `uuid.uuid4()` + PostgreSQL UUID type | Standard, collision-resistant, already established in auth models |
| JSON column validation | Custom JSON parsing/validation | Pydantic models for JSONB validation in schemas | Pydantic validates the JSON structure at the API layer before it hits the DB |
| Date range overlap checking | Manual date comparison logic | PostgreSQL `daterange` + `&&` operator | Database-level overlap detection is atomic and correct |
| Decimal rounding for currency | Manual rounding | `Decimal.quantize(Decimal("0.01"))` | Python's Decimal module handles banker's rounding correctly |

## Common Pitfalls

### Pitfall 1: MinIO Container Not Ready on First Boot
**What goes wrong:** The room service starts before MinIO is healthy, fails to create bucket, seed photos fail.
**Why it happens:** Docker Compose `depends_on` only waits for container start, not readiness.
**How to avoid:** Add a healthcheck to the MinIO container. Use `depends_on: minio: condition: service_healthy`. In the lifespan startup, retry bucket creation with backoff.
**Warning signs:** "Connection refused" errors on first `docker compose up`.

### Pitfall 2: Forgetting to Add Room Routes to Gateway SERVICE_MAP
**What goes wrong:** Room service works on direct port (8002) but not through gateway (8000).
**Why it happens:** Gateway `SERVICE_MAP` currently has `"/api/v1/rooms": settings.ROOM_SERVICE_URL` but does not have entries for rate endpoints or room type endpoints if they use different prefixes.
**How to avoid:** Use `/api/v1/rooms` as the prefix for ALL room service endpoints (room types, rooms, rates). The gateway already matches by prefix, so `/api/v1/rooms/types`, `/api/v1/rooms/123/status`, `/api/v1/rooms/rates` all route correctly through the existing `/api/v1/rooms` prefix mapping.
**Warning signs:** 404 from gateway, 200 from direct service URL.

### Pitfall 3: JSONB Column Migration Issues
**What goes wrong:** Alembic autogenerate does not detect changes to JSONB column default values or structure.
**Why it happens:** JSONB is schemaless -- Alembic cannot diff JSON structures, only column type changes.
**How to avoid:** Write explicit migration steps for JSONB columns. Validate JSON structure in Pydantic schemas (API layer), not in the database.
**Warning signs:** Schema changes to amenity structure are not caught by `alembic revision --autogenerate`.

### Pitfall 4: Decimal vs Float Contamination in Rate Calculations
**What goes wrong:** A float multiplier (e.g., `1.3`) infects Decimal arithmetic, producing incorrect totals.
**Why it happens:** Pydantic may deserialize JSON numbers as float by default. Multiplying Decimal by float produces float.
**How to avoid:** Define all rate/multiplier schema fields as `Decimal` type in Pydantic. Use `Decimal("1.3")` not `1.3` in seed data. Test that `calculate_nightly_rate` returns exact Decimal values.
**Warning signs:** Price of `149.99000000000001` instead of `149.99`.

### Pitfall 5: Missing Alembic in Room Service
**What goes wrong:** Room service has no migration infrastructure -- models exist but tables are never created.
**Why it happens:** The room service stub was created in Phase 1 without Alembic. It needs to be initialized.
**How to avoid:** Run `alembic init -t async alembic` inside `services/room/`, configure `alembic.ini` with the room_db URL, set up `env.py` to import room models.
**Warning signs:** "relation does not exist" errors when room service starts.

### Pitfall 6: Seed Data Idempotency
**What goes wrong:** Seed script runs on every boot and creates duplicate rooms/rates.
**Why it happens:** Seed script uses INSERT without checking for existing data.
**How to avoid:** Check if data exists before seeding (e.g., `SELECT COUNT(*) FROM room_types`). Only seed if tables are empty. Log "Seed data already exists, skipping."
**Warning signs:** Room count grows every time Docker restarts.

## Code Examples

### Database Model: RoomType with JSONB

```python
# Source: Established pattern from services/auth/app/models/user.py + JSONB extension
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RoomType(Base):
    __tablename__ = "room_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    max_adults: Mapped[int] = mapped_column(Integer, nullable=False)
    max_children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bed_config: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    amenities: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    photo_urls: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    rooms = relationship("Room", back_populates="room_type")
    base_rates = relationship("BaseRate", back_populates="room_type")
```

### Database Model: Room with Status Enum

```python
from enum import Enum as PyEnum

class RoomStatus(str, PyEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    INSPECTED = "inspected"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"
    RESERVED = "reserved"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    room_number: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("room_types.id"), nullable=False
    )
    status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus, name="room_status", create_constraint=True),
        default=RoomStatus.AVAILABLE,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    room_type = relationship("RoomType", back_populates="rooms")
    status_history = relationship("RoomStatusChange", back_populates="room")
```

### Database Model: Rate Tables

```python
class BaseRate(Base):
    """Base rate per room type per occupancy tier."""
    __tablename__ = "base_rates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("room_types.id"), nullable=False)
    min_occupancy: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_occupancy: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")  # ISO 4217

    room_type = relationship("RoomType", back_populates="base_rates")


class SeasonalRate(Base):
    """Date-range multiplier override for seasonal pricing."""
    __tablename__ = "seasonal_rates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("room_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # "Summer Peak"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    multiplier: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)  # e.g., 1.30
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class WeekendSurcharge(Base):
    """Weekend multiplier per room type."""
    __tablename__ = "weekend_surcharges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("room_types.id"), nullable=False)
    multiplier: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)  # e.g., 1.15
    # Friday=4, Saturday=5 in Python's weekday()
    days: Mapped[list] = mapped_column(JSONB, nullable=False, default=lambda: [4, 5])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

### Status Change Audit Log

```python
class RoomStatusChange(Base):
    """Audit log for room status transitions."""
    __tablename__ = "room_status_changes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    from_status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus, name="room_status", create_constraint=False), nullable=False
    )
    to_status: Mapped[RoomStatus] = mapped_column(
        Enum(RoomStatus, name="room_status", create_constraint=False), nullable=False
    )
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)  # user UUID from JWT
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    room = relationship("Room", back_populates="status_history")
```

### MinIO Docker Compose Addition

```yaml
# Add to docker-compose.yml services section
minio:
  image: minio/minio:RELEASE.2025-09-07T16-13-09Z
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
  volumes:
    - minio_data:/data
  ports:
    - "9000:9000"    # API
    - "9001:9001"    # Console UI
  healthcheck:
    test: ["CMD", "mc", "ready", "local"]
    interval: 5s
    timeout: 3s
    retries: 5

# Add to volumes section
minio_data:
```

**Note on MinIO Docker image availability:** The MinIO GitHub repository was archived in February 2026 and new Docker Hub images stopped in October 2025. The `RELEASE.2025-09-07T16-13-09Z` tag is the latest available on Docker Hub. For a portfolio project this is perfectly fine -- the image works and MinIO is S3-compatible. If Docker Hub pulls fail in the future, alternatives include `pgsty/minio` (community fork) or `cgr.dev/chainguard/minio:latest`.

### Room Service Environment Variables

```python
# services/room/app/core/config.py
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://room_user:room_pass@room_db:5432/rooms"
    JWT_PUBLIC_KEY_PATH: str = "/run/secrets/jwt_public_key"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "hotelbook"
    MINIO_SECURE: bool = False

    # Seed data
    SEED_ON_STARTUP: bool = True

    DEBUG: bool = False
    model_config = {"env_file": ".env"}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Store images in PostgreSQL BYTEA | S3-compatible object storage (MinIO) | Industry standard for years | Keeps DB small, enables CDN, scales independently |
| Float for money | Decimal/Numeric | Always was best practice | Prevents rounding errors in pricing |
| Separate amenities table (M2M) | JSONB for semi-structured data | PostgreSQL 9.4+ (2014) | Simpler queries for read-heavy display data |
| MinIO `minio/minio:latest` on Docker Hub | Pin specific release tag | Oct 2025 (Docker Hub publishing stopped) | Must use specific release tag, not `latest` |

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.x + pytest-asyncio |
| Config file | `pyproject.toml` (root level, existing) |
| Quick run command | `pytest tests/room/ -x -q` |
| Full suite command | `pytest tests/ -x -q` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RMGT-01 | CRUD room types with photos, amenities, capacity | integration | `pytest tests/room/test_room_types.py -x` | Wave 0 |
| RMGT-02 | Manage rooms (number, floor, status) | integration | `pytest tests/room/test_rooms.py -x` | Wave 0 |
| RMGT-03 | View room status board | integration | `pytest tests/room/test_status_board.py -x` | Wave 0 |
| RMGT-04 | Housekeeping status tracking + auto transitions | integration | `pytest tests/room/test_status_transitions.py -x` | Wave 0 |
| RATE-01 | Set base rates per room type | integration | `pytest tests/room/test_rates.py -x` | Wave 0 |
| RATE-02 | Seasonal pricing + weekend surcharges + stacking | unit + integration | `pytest tests/room/test_pricing.py -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/room/ -x -q`
- **Per wave merge:** `pytest tests/ -x -q`
- **Phase gate:** Full suite green before verify

### Wave 0 Gaps

- [ ] `tests/room/__init__.py` -- test package init
- [ ] `tests/room/conftest.py` -- room service fixtures (db session, client, auth tokens, MinIO mock)
- [ ] `tests/room/test_room_types.py` -- covers RMGT-01
- [ ] `tests/room/test_rooms.py` -- covers RMGT-02
- [ ] `tests/room/test_status_board.py` -- covers RMGT-03
- [ ] `tests/room/test_status_transitions.py` -- covers RMGT-04
- [ ] `tests/room/test_rates.py` -- covers RATE-01
- [ ] `tests/room/test_pricing.py` -- covers RATE-02 (unit tests for rate calculation)
- [ ] Update `pyproject.toml` pythonpath to include `services/room`

### Test Infrastructure Notes

The existing test setup in `pyproject.toml` sets `pythonpath = ["services/auth", "shared"]`. For Phase 2, this must be extended to include `services/room`. The `tests/room/conftest.py` needs:
1. A `TEST_DATABASE_URL` pointing to room_db (`localhost:5434`)
2. Table creation using room service models
3. An async client fixture using the room service app
4. Mock JWT tokens (no need for actual auth service -- generate tokens with test keys)
5. MinIO mock or test bucket for photo upload tests

## Open Questions

1. **MinIO healthcheck command**
   - What we know: `mc ready local` is documented as the healthcheck for MinIO
   - What's unclear: Whether this command is available in older MinIO images
   - Recommendation: Test the healthcheck; fallback to `curl -f http://localhost:9000/minio/health/live`

2. **Photo URL format: presigned vs public**
   - What we know: MinIO supports both presigned URLs (time-limited) and public bucket policies
   - What's unclear: For a portfolio project, which is simpler?
   - Recommendation: Use public bucket policy for the `hotelbook` bucket. Simpler for demo purposes -- photos are not sensitive data.

3. **Gateway multipart forwarding**
   - What we know: The gateway proxy forwards request body as raw bytes
   - What's unclear: Whether multipart file uploads proxy correctly through the gateway
   - Recommendation: Test this explicitly. The current `proxy_request` reads `await request.body()` which should work for multipart, but verify content-type header forwarding.

## Sources

### Primary (HIGH confidence)
- `services/auth/` -- Established patterns for models, routes, services, deps, config, database, migrations
- `docker-compose.yml` -- Existing infrastructure including room_db on port 5434
- `shared/shared/database.py` -- Engine/session factory pattern
- `shared/shared/jwt.py` -- JWT verification for non-auth services
- `services/gateway/app/api/proxy.py` -- Gateway routing with SERVICE_MAP

### Secondary (MEDIUM confidence)
- [MinIO Python SDK (PyPI)](https://pypi.org/project/minio/) -- v7.2.20, Python 3.9+
- [MinIO Docker Setup](https://github.com/minio/minio/blob/master/docs/docker/README.md) -- Docker Compose patterns
- [FastAPI MinIO Integration (Medium)](https://medium.com/@mojimich2015/fastapi-minio-integration-31b35076afcb) -- Upload patterns
- [SQLAlchemy 2.0 Numeric/Decimal](https://docs.sqlalchemy.org/en/20/core/type_basics.html) -- Decimal column types
- [MinIO Docker Hub Tags](https://hub.docker.com/r/minio/minio/tags) -- Available image versions

### Tertiary (LOW confidence)
- MinIO Docker Hub availability long-term -- repo archived Feb 2026, images may become unavailable. Pinned tag `RELEASE.2025-09-07T16-13-09Z` works today.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries are established, versions verified, patterns from Phase 1 apply directly
- Architecture: HIGH -- direct extension of auth service patterns, well-understood CRUD domain
- Pitfalls: HIGH -- pricing pitfalls from project research apply, MinIO integration is well-documented
- MinIO availability: MEDIUM -- Docker image exists but repo is archived; pinned tag is the safe approach

**Research date:** 2026-03-21
**Valid until:** 2026-04-21 (stable domain, pinned versions)

---
*Phase 2 research for: HotelBook - Room & Rate Management*
*Researched: 2026-03-21*
