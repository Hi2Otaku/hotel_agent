# Phase 1: Foundation & Authentication - Research

**Researched:** 2026-03-20
**Domain:** Microservice scaffolding, Docker Compose orchestration, async PostgreSQL, JWT authentication, RBAC
**Confidence:** HIGH

## Summary

Phase 1 establishes the entire project infrastructure: a monorepo with four FastAPI microservices (Auth, Room, Booking, Gateway/BFF), Docker Compose orchestration with database-per-service (three separate PostgreSQL instances), RabbitMQ for inter-service messaging, and Mailpit for email simulation. The Auth service is the primary deliverable, implementing JWT authentication for guests and staff with role-based access control (admin, manager, front desk), staff invite links, first-admin seeding from environment variables, and a full password reset flow with 15-minute token expiry via Mailpit.

The key architectural decision is using RS256 (asymmetric) JWT signing so the Auth service holds the private key while other services only need the public key to verify tokens. This avoids sharing secrets across services. RabbitMQ is recommended over Redis Streams as the message queue because it provides guaranteed delivery, acknowledgments, and dead-letter exchanges out of the box -- critical for a hotel system where lost messages mean lost bookings.

**Primary recommendation:** Build a monorepo with service directories, each with its own Dockerfile, Alembic config, and async SQLAlchemy setup. Use RS256 JWT with public key distribution. Use RabbitMQ with aio-pika. Start with the Auth service fully functional before scaffolding the other three services as stubs.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- JWT tokens with 24-hour hard expiry (no sliding refresh)
- Same token duration for guests and staff
- On expired token: redirect to login page, return to original URL after re-login
- Access token + refresh token pattern not needed -- hard expiry is sufficient
- Three roles: admin, manager, front desk
- Admin: full access (system settings, user management, all operations)
- Manager: room/rate management, reports, bookings -- no user management
- Front desk: bookings and check-in/out only -- no room/rate CRUD, no reports, no user management, no rate overrides
- Staff accounts created via invite link from admin
- First admin account created via environment variable / config at deployment
- No staff self-registration
- Full realistic password reset flow: request form -> token email -> reset link -> new password form
- Reset tokens valid for 15 minutes
- Email delivery via Mailpit (local SMTP trap with web UI)
- Four services: Auth, Room, Booking, Gateway/BFF
- Domain module organization within each service
- Docker Compose for local development -- each service in its own container
- Database per service: separate PostgreSQL databases for auth, rooms, bookings
- Inter-service communication via message queue

### Claude's Discretion
- Message queue choice (RabbitMQ vs Redis Streams)
- Whether to use monorepo with service directories or separate repos (considering portfolio reviewability)
- Exact Docker Compose configuration
- Database migration tooling per service (Alembic)
- Shared library/package strategy across services
- JWT signing key distribution across services

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | Guest can create account with email and password | Auth service with pwdlib/Argon2 hashing, async SQLAlchemy user model, registration endpoint |
| AUTH-02 | Guest can log in and stay logged in across sessions (JWT) | PyJWT RS256 token creation, 24h hard expiry, OAuth2PasswordBearer dependency |
| AUTH-03 | Guest can reset password via email link (simulated) | fastapi-mail + Mailpit SMTP, secure token generation, 15-min expiry, full flow |
| AUTH-04 | Staff can log in with role-based access (admin, manager, front desk) | Role enum in user model, role-checking dependencies, first-admin seeding, invite link system |
</phase_requirements>

## Standard Stack

### Core (Phase 1 Specific)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.135.x | API framework for all services | Async-first, Pydantic-native, auto OpenAPI docs |
| SQLAlchemy | 2.0.48 | Async ORM with asyncpg | Industry standard, v2.0 async support, type-safe queries |
| asyncpg | latest | PostgreSQL async driver | 5x faster than psycopg3, purpose-built for asyncio |
| Alembic | 1.18.x | Database migrations per service | Only serious migration tool for SQLAlchemy; use `--async` flag |
| Pydantic | 2.12.x | Request/response validation | Ships with FastAPI, v2 is dramatically faster |
| pydantic-settings | 2.x | Environment variable loading | .env file support, clean config separation |
| PyJWT | 2.12.1 | JWT token creation/verification | Lightweight, actively maintained. Use with `cryptography` for RS256 |
| pwdlib[argon2] | 0.3.0 | Password hashing | Modern passlib replacement, Argon2 per OWASP. FastAPI docs recommend this. |
| fastapi-mail | 1.6.2 | Async email sending | Jinja2 templates, async SMTP, works with Mailpit |
| aio-pika | 9.6.1 | RabbitMQ async client | Wrapper around aiormq for asyncio, auto-reconnect, publisher confirms |
| httpx | latest | HTTP client for gateway proxying and tests | Async client, ships with FastAPI, used for inter-service calls and testing |
| uvicorn | latest | ASGI server | Standard production server for FastAPI |
| cryptography | latest | RSA key support for PyJWT | Required for RS256 algorithm |

### Infrastructure

| Component | Image/Version | Purpose |
|-----------|---------------|---------|
| PostgreSQL | 16-alpine | Three instances: auth_db, room_db, booking_db |
| RabbitMQ | 3-management-alpine | Message queue with management UI on port 15672 |
| Mailpit | axllent/mailpit:latest | SMTP trap (port 1025) + Web UI (port 8025) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| RabbitMQ (aio-pika) | Redis Streams | Redis is simpler but lacks guaranteed delivery, dead-letter exchanges, and native message acknowledgment. RabbitMQ is purpose-built for message brokering. For a hotel system, message reliability matters. |
| RS256 (asymmetric JWT) | HS256 (symmetric) | HS256 requires sharing the same secret across all services. RS256 lets Auth hold the private key and distribute only the public key. Better security posture for microservices. |
| Monorepo with service dirs | Separate repositories | Monorepo is better for portfolio: single clone, shared CI, easier review. Separate repos add complexity without benefit for a single-developer project. |
| fastapi-mail | aiosmtplib (raw) | fastapi-mail provides Jinja2 templates, background task integration, and ConnectionConfig out of the box. Raw SMTP is unnecessary complexity. |

**Installation (per service):**
```bash
# Common to all services
pip install fastapi[standard] uvicorn[standard]
pip install sqlalchemy[asyncio] asyncpg alembic
pip install pydantic-settings
pip install httpx

# Auth service specific
pip install "pwdlib[argon2]" "PyJWT[crypto]"
pip install fastapi-mail
pip install aio-pika

# Dev dependencies (all services)
pip install pytest pytest-asyncio pytest-cov
pip install ruff
```

## Architecture Patterns

### Recommended Project Structure (Monorepo)

```
hotelbook/
├── docker-compose.yml           # All services, DBs, RabbitMQ, Mailpit
├── .env.example                 # Template for env vars
├── shared/                      # Shared Python package
│   ├── pyproject.toml           # Installable package
│   └── shared/
│       ├── __init__.py
│       ├── schemas/             # Shared Pydantic schemas (user info in JWT, etc.)
│       ├── jwt.py               # JWT verification (public key only)
│       ├── messaging.py         # RabbitMQ connection helpers
│       └── database.py          # Common async engine/session factory
├── services/
│   ├── auth/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic/             # Auth-specific migrations
│   │   ├── alembic.ini
│   │   └── app/
│   │       ├── main.py          # FastAPI app, CORS, lifespan
│   │       ├── core/
│   │       │   ├── config.py    # Settings (DB URL, JWT keys, SMTP)
│   │       │   ├── security.py  # Password hashing, JWT creation (private key)
│   │       │   └── database.py  # Auth DB engine + session
│   │       ├── models/
│   │       │   ├── user.py      # User model (guests + staff)
│   │       │   └── token.py     # Password reset tokens, invite tokens
│   │       ├── schemas/
│   │       │   ├── auth.py      # Login, register, token response
│   │       │   └── user.py      # User create/read/update
│   │       ├── api/
│   │       │   ├── deps.py      # get_db, get_current_user, require_role
│   │       │   └── v1/
│   │       │       ├── auth.py  # Login, register, refresh, password reset
│   │       │       ├── users.py # User management (admin only)
│   │       │       └── invite.py # Staff invite link endpoints
│   │       └── services/
│   │           ├── auth.py      # Auth business logic
│   │           ├── user.py      # User CRUD
│   │           ├── email.py     # Email sending via fastapi-mail
│   │           └── invite.py    # Invite link generation/validation
│   ├── room/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic/
│   │   ├── alembic.ini
│   │   └── app/
│   │       └── main.py          # Stub for Phase 1
│   ├── booking/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic/
│   │   ├── alembic.ini
│   │   └── app/
│   │       └── main.py          # Stub for Phase 1
│   └── gateway/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app/
│           ├── main.py          # Gateway app with proxy routes
│           ├── core/
│           │   └── config.py    # Service URLs, JWT public key
│           └── api/
│               └── proxy.py     # Reverse proxy to services
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── auth/
│   │   ├── test_registration.py
│   │   ├── test_login.py
│   │   ├── test_password_reset.py
│   │   └── test_roles.py
│   └── gateway/
│       └── test_proxy.py
└── scripts/
    ├── generate_keys.sh         # Generate RSA key pair for JWT
    └── seed_admin.py            # First admin creation script
```

### Pattern 1: RS256 JWT with Key Distribution

**What:** Auth service signs tokens with RSA private key. All other services verify with the public key only.
**When to use:** Any microservice architecture where multiple services need to verify tokens.

```python
# Auth service: JWT creation (has private key)
# services/auth/app/core/security.py
import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path

PRIVATE_KEY = Path("/run/secrets/jwt_private_key").read_text()
PUBLIC_KEY = Path("/run/secrets/jwt_public_key").read_text()
ALGORITHM = "RS256"
TOKEN_EXPIRE_HOURS = 24

def create_access_token(user_id: str, role: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
```

```python
# Shared library: JWT verification (public key only)
# shared/shared/jwt.py
import jwt

def verify_token(token: str, public_key: str) -> dict:
    """Any service can verify tokens with only the public key."""
    return jwt.decode(token, public_key, algorithms=["RS256"])
```

### Pattern 2: FastAPI Dependency Chain for RBAC

**What:** Composable dependencies for authentication and role checking.
**When to use:** Every protected endpoint.

```python
# services/auth/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_token
from app.core.database import get_session
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = verify_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

def require_role(*roles: UserRole):
    """Dependency factory for role-based access control."""
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return check_role

# Usage in routes:
# @router.get("/admin-only")
# async def admin_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
#     ...
```

### Pattern 3: Async Database Setup Per Service

**What:** Each service has its own async engine and session factory pointing to its own PostgreSQL database.
**When to use:** Every service.

```python
# services/auth/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,  # postgresql+asyncpg://user:pass@auth_db:5432/auth
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
```

### Pattern 4: Docker Compose with Database-per-Service

**What:** Separate PostgreSQL containers for each service.

```yaml
# docker-compose.yml
services:
  # --- Databases ---
  auth_db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: auth
      POSTGRES_USER: auth_user
      POSTGRES_PASSWORD: auth_pass
    volumes:
      - auth_db_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U auth_user -d auth"]
      interval: 5s
      timeout: 3s
      retries: 5

  room_db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: rooms
      POSTGRES_USER: room_user
      POSTGRES_PASSWORD: room_pass
    volumes:
      - room_db_data:/var/lib/postgresql/data
    ports:
      - "5434:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U room_user -d rooms"]
      interval: 5s
      timeout: 3s
      retries: 5

  booking_db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: bookings
      POSTGRES_USER: booking_user
      POSTGRES_PASSWORD: booking_pass
    volumes:
      - booking_db_data:/var/lib/postgresql/data
    ports:
      - "5435:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U booking_user -d bookings"]
      interval: 5s
      timeout: 3s
      retries: 5

  # --- Message Queue ---
  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: hotel
      RABBITMQ_DEFAULT_PASS: hotel_pass
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 10s
      timeout: 5s
      retries: 5

  # --- Email ---
  mailpit:
    image: axllent/mailpit:latest
    ports:
      - "8025:8025"    # Web UI
      - "1025:1025"    # SMTP
    environment:
      MP_MAX_MESSAGES: 500

  # --- Services ---
  auth:
    build:
      context: .
      dockerfile: services/auth/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://auth_user:auth_pass@auth_db:5432/auth
      JWT_PRIVATE_KEY_PATH: /run/secrets/jwt_private_key
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key
      MAIL_SERVER: mailpit
      MAIL_PORT: 1025
      RABBITMQ_URL: amqp://hotel:hotel_pass@rabbitmq:5672/
      FIRST_ADMIN_EMAIL: admin@hotel.local
      FIRST_ADMIN_PASSWORD: admin123
    depends_on:
      auth_db:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    ports:
      - "8001:8000"

  gateway:
    build:
      context: .
      dockerfile: services/gateway/Dockerfile
    environment:
      AUTH_SERVICE_URL: http://auth:8000
      ROOM_SERVICE_URL: http://room:8000
      BOOKING_SERVICE_URL: http://booking:8000
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key
    depends_on:
      - auth
    ports:
      - "8000:8000"

  room:
    build:
      context: .
      dockerfile: services/room/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://room_user:room_pass@room_db:5432/rooms
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key
      RABBITMQ_URL: amqp://hotel:hotel_pass@rabbitmq:5672/
    depends_on:
      room_db:
        condition: service_healthy
    ports:
      - "8002:8000"

  booking:
    build:
      context: .
      dockerfile: services/booking/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://booking_user:booking_pass@booking_db:5432/bookings
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key
      RABBITMQ_URL: amqp://hotel:hotel_pass@rabbitmq:5672/
    depends_on:
      booking_db:
        condition: service_healthy
    ports:
      - "8003:8000"

volumes:
  auth_db_data:
  room_db_data:
  booking_db_data:
```

### Pattern 5: Mailpit Email Integration

**What:** fastapi-mail configured to send to Mailpit's SMTP server.

```python
# services/auth/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... other settings
    MAIL_SERVER: str = "mailpit"
    MAIL_PORT: int = 1025
    MAIL_FROM: str = "noreply@hotelbook.local"
    MAIL_FROM_NAME: str = "HotelBook"
    # Mailpit doesn't need credentials
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = False
    MAIL_VALIDATE_CERTS: bool = False
```

```python
# services/auth/app/services/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
    TEMPLATE_FOLDER="app/templates/email",
)

async def send_password_reset_email(email: str, reset_token: str, reset_url: str):
    message = MessageSchema(
        subject="Reset Your Password - HotelBook",
        recipients=[email],
        template_body={"reset_url": reset_url, "token": reset_token},
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message, template_name="password_reset.html")
```

### Pattern 6: First Admin Seeding via Lifespan

**What:** Create the first admin account on startup from environment variables.

```python
# services/auth/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine, async_session_factory
from app.services.user import get_or_create_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed first admin
    async with async_session_factory() as session:
        await get_or_create_admin(
            session,
            email=settings.FIRST_ADMIN_EMAIL,
            password=settings.FIRST_ADMIN_PASSWORD,
        )
    yield
    # Shutdown: close engine
    await engine.dispose()

app = FastAPI(title="Auth Service", lifespan=lifespan)
```

### Anti-Patterns to Avoid

- **HS256 shared secret across services:** Share a public key instead. HS256 means every service that can verify can also forge tokens.
- **Sync SQLAlchemy in async endpoints:** Always use `AsyncSession` and `create_async_engine`. Mixing sync blocks the event loop.
- **Password reset tokens in JWT:** Use opaque random tokens stored in the database with expiry. JWTs for password reset are harder to invalidate.
- **Direct service-to-service HTTP for everything:** Use the message queue for async operations (event notifications). Use HTTP only for synchronous request-response (via gateway).
- **Single PostgreSQL instance with multiple databases:** Use separate containers for true isolation. A single instance with multiple DBs shares connection pools and resources.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom hash function or raw hashlib | pwdlib[argon2] | Argon2 tuning, salt management, timing-safe comparison are easy to get wrong |
| JWT creation/verification | Manual base64 + HMAC | PyJWT with cryptography | RFC 7519 compliance, algorithm validation, expiry checking |
| Email sending | Raw SMTP with smtplib | fastapi-mail | Async support, template rendering, connection pooling, retry logic |
| RabbitMQ integration | Raw amqplib/socket | aio-pika | Connection recovery, channel management, consumer groups, publisher confirms |
| Environment config | os.environ parsing | pydantic-settings | Type validation, .env file support, nested config, defaults |
| Database migrations | Manual SQL scripts | Alembic | Auto-generation from model diffs, version history, upgrade/downgrade |
| CORS handling | Custom middleware | FastAPI CORSMiddleware | Proper header handling, preflight support, origin validation |

**Key insight:** Every "simple" thing above has subtle edge cases (timing attacks in password comparison, algorithm confusion in JWT, connection recovery in AMQP) that libraries handle and hand-rolled code misses.

## Common Pitfalls

### Pitfall 1: Sync/Async Mismatch with SQLAlchemy

**What goes wrong:** Endpoints defined as `async def` but using synchronous `Session` instead of `AsyncSession`. Application works in dev (single user) but freezes under any concurrent load.
**Why it happens:** Many SQLAlchemy tutorials still show sync patterns.
**How to avoid:** Use `create_async_engine`, `async_sessionmaker`, and `AsyncSession` exclusively. Never import from `sqlalchemy.orm.Session` in an async codebase. Use `asyncpg` driver, not `psycopg2`.
**Warning signs:** `psycopg2` in requirements.txt, `Session` import instead of `AsyncSession`.

### Pitfall 2: JWT Algorithm Confusion

**What goes wrong:** Token created with RS256 but verified with HS256, or vice versa. This can be a security vulnerability (attacker sends HS256 token using the public key as the "secret").
**Why it happens:** PyJWT's `decode()` accepts an `algorithms` parameter (list) but developers sometimes omit it.
**How to avoid:** Always explicitly specify `algorithms=["RS256"]` in `jwt.decode()`. Never accept algorithm from the token header.
**Warning signs:** `jwt.decode(token, key)` without `algorithms` parameter.

### Pitfall 3: Password Reset Token Leakage

**What goes wrong:** Password reset tokens are predictable, reusable, or exposed in URLs that get logged.
**Why it happens:** Using sequential IDs or short tokens, not invalidating after use, or logging full URLs.
**How to avoid:** Use `secrets.token_urlsafe(32)` for token generation. Store hashed token in DB (hash with SHA-256, not Argon2 -- reset tokens are not passwords). Invalidate immediately after use. Set 15-minute expiry in the database row.
**Warning signs:** Token is a short numeric code, token can be used multiple times, no expiry check.

### Pitfall 4: Alembic Migrations Not Running on Startup

**What goes wrong:** Service starts but database has no tables. Migrations were generated but never applied in the Docker container.
**Why it happens:** Developers run `alembic upgrade head` manually during development but forget to include it in the Docker entrypoint.
**How to avoid:** Add `alembic upgrade head` to the Docker entrypoint script before starting uvicorn. Or use a startup event/lifespan to run migrations programmatically.
**Warning signs:** Service crashes with "relation does not exist" on first container startup.

### Pitfall 5: Docker Compose Service Startup Order

**What goes wrong:** Auth service starts before PostgreSQL is ready, crashes with connection refused.
**Why it happens:** `depends_on` only waits for container start, not service readiness.
**How to avoid:** Use `depends_on` with `condition: service_healthy` and define `healthcheck` on database containers. PostgreSQL healthcheck: `pg_isready -U user -d dbname`.
**Warning signs:** Intermittent startup failures, service works on retry but not on first `docker compose up`.

### Pitfall 6: Invite Link Security

**What goes wrong:** Invite links are predictable or don't expire, allowing unauthorized staff account creation.
**Why it happens:** Using sequential or short tokens for invite links.
**How to avoid:** Use `secrets.token_urlsafe(32)`. Store invite tokens in DB with: target role, created_by (admin ID), expiry (e.g., 48 hours), used_at (null until consumed). Single-use only.
**Warning signs:** Invite token is a short string, no expiry, can create multiple accounts from one link.

## Code Examples

### User Model with Role Enum

```python
# services/auth/app/models/user.py
import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class UserRole(str, PyEnum):
    GUEST = "guest"
    ADMIN = "admin"
    MANAGER = "manager"
    FRONT_DESK = "front_desk"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True),
        default=UserRole.GUEST,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

### Password Reset Token Model

```python
# services/auth/app/models/token.py
import uuid
import hashlib
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash token with SHA-256 for storage. Reset tokens are not passwords."""
        return hashlib.sha256(token.encode()).hexdigest()
```

### Staff Invite Token Model

```python
# services/auth/app/models/token.py (continued)
class StaffInviteToken(Base):
    __tablename__ = "staff_invite_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True), nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
```

### Password Hashing with pwdlib

```python
# services/auth/app/core/security.py
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

password_hash = PasswordHash((Argon2Hasher(),))

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
```

### Alembic Async Setup (per service)

```bash
# Initialize alembic with async template
cd services/auth
alembic init -t async alembic
```

```python
# services/auth/alembic/env.py (key modification)
from app.core.database import Base
from app.models.user import User  # noqa: F401 - import to register models
from app.models.token import PasswordResetToken, StaffInviteToken  # noqa: F401

target_metadata = Base.metadata
```

### Docker Entrypoint with Migrations

```bash
#!/bin/bash
# services/auth/entrypoint.sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting auth service..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| passlib + bcrypt | pwdlib + Argon2 | 2024 | passlib is dead, breaks on Python 3.13+. FastAPI docs updated. |
| python-jose for JWT | PyJWT | 2024 | python-jose unmaintained. PyJWT is actively maintained. |
| Sync SQLAlchemy + psycopg2 | Async SQLAlchemy 2.0 + asyncpg | 2023-2024 | Required for FastAPI async performance. Old approach blocks event loop. |
| MailHog for email testing | Mailpit | 2023 | MailHog is unmaintained. Mailpit is the active fork/replacement. |
| pika (sync RabbitMQ) | aio-pika (async) | 2023+ | pika blocks the event loop in async FastAPI apps. |

**Deprecated/outdated:**
- passlib: unmaintained, breaks on Python 3.13+
- python-jose: unmaintained, security risk
- MailHog: unmaintained, replaced by Mailpit
- pika (for async apps): use aio-pika instead

## Open Questions

1. **RSA Key Management in Docker Compose**
   - What we know: Docker secrets require Swarm mode. For local Compose, we can mount key files as volumes or use environment variables.
   - What is unclear: Best practice for managing RSA key pair in local Docker Compose without Swarm.
   - Recommendation: Generate keys with a script, store in `keys/` directory (gitignored), mount as volumes. Provide `scripts/generate_keys.sh` for setup. For CI/CD, use environment variables with base64-encoded keys.

2. **Gateway Pattern: Reverse Proxy vs. BFF**
   - What we know: Gateway can either be a dumb reverse proxy (forwards requests) or a BFF that aggregates/transforms responses.
   - What is unclear: How much logic the Gateway should have in Phase 1.
   - Recommendation: Start as a thin reverse proxy with JWT verification in Phase 1. Add BFF aggregation logic in later phases as needed.

3. **Shared Package Distribution**
   - What we know: Services need shared code (JWT verification, Pydantic schemas, message queue helpers).
   - What is unclear: Best way to share Python packages across service containers.
   - Recommendation: Use a `shared/` directory at monorepo root with `pyproject.toml`. Install via `pip install -e ../shared` in each service's Dockerfile (or copy and install during build).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.x + pytest-asyncio |
| Config file | None -- Wave 0 must create `pytest.ini` or `pyproject.toml` [tool.pytest] |
| Quick run command | `pytest tests/auth/ -x -q` |
| Full suite command | `pytest tests/ -v --tb=short` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | Guest registration with email/password | integration | `pytest tests/auth/test_registration.py -x` | No -- Wave 0 |
| AUTH-02 | Guest login returns JWT, token validates across requests | integration | `pytest tests/auth/test_login.py -x` | No -- Wave 0 |
| AUTH-03 | Password reset: request, email sent, token valid 15min, reset works | integration | `pytest tests/auth/test_password_reset.py -x` | No -- Wave 0 |
| AUTH-04 | Staff login with role, role-restricted endpoints reject wrong roles | integration | `pytest tests/auth/test_roles.py -x` | No -- Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/auth/ -x -q`
- **Per wave merge:** `pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/conftest.py` -- async test fixtures, test database setup, test client factory
- [ ] `tests/auth/conftest.py` -- auth-specific fixtures (test user, admin user, tokens)
- [ ] `tests/auth/test_registration.py` -- covers AUTH-01
- [ ] `tests/auth/test_login.py` -- covers AUTH-02
- [ ] `tests/auth/test_password_reset.py` -- covers AUTH-03
- [ ] `tests/auth/test_roles.py` -- covers AUTH-04
- [ ] `pytest.ini` or `pyproject.toml` with pytest config (asyncio_mode = "auto")
- [ ] Framework install: `pip install pytest pytest-asyncio httpx` -- none detected (greenfield)

## Sources

### Primary (HIGH confidence)
- [PyJWT 2.12.1 Official Docs](https://pyjwt.readthedocs.io/en/latest/usage.html) -- JWT creation/verification patterns, RS256 examples
- [pwdlib Official Guide](https://frankie567.github.io/pwdlib/guide/) -- Password hashing API, Argon2 configuration
- [FastAPI Official: OAuth2 JWT Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) -- PyJWT + pwdlib recommended pattern
- [Alembic 1.18.4 Official Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) -- Async init, multi-database patterns
- [Mailpit Official Docker Docs](https://mailpit.axllent.org/docs/install/docker/) -- Container config, SMTP settings
- [fastapi-mail Official Docs](https://sabuhish.github.io/fastapi-mail/) -- ConnectionConfig, async send, Jinja2 templates
- [aio-pika Official Docs](https://docs.aio-pika.com/) -- Async RabbitMQ client, connection patterns

### Secondary (MEDIUM confidence)
- [FastAPI Microservices Authentication with JWT - Python in Plain English](https://python.plainenglish.io/fastapi-microservices-authentication-with-jwt-central-auth-api-gateway-rbac-guide-7d049f9cea8c) -- Gateway + Auth service pattern
- [Alembic Multiple Databases in Monorepo - DEV Community](https://dev.to/fadi-bck/managing-database-migrations-for-multiple-services-in-a-monorepo-with-alembic-3p5l) -- Per-service Alembic config
- [AWS: RabbitMQ vs Redis](https://aws.amazon.com/compare/the-difference-between-rabbitmq-and-redis/) -- Message queue comparison
- [FastAPI + aio-pika RabbitMQ - Medium](https://medium.com/@ar.aldhafeeri11/how-to-use-rabbitmq-with-fastapi-asynchronous-message-publishing-and-consuming-c094da1c47a6) -- Integration pattern

### Tertiary (LOW confidence)
- None -- all findings verified with primary or secondary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries verified on PyPI with current versions, official docs consulted
- Architecture: HIGH -- microservice patterns well-documented, Docker Compose patterns verified
- Pitfalls: HIGH -- drawn from project-level pitfalls research plus phase-specific investigation
- Validation: MEDIUM -- test structure is standard but no existing infrastructure to verify against

**Research date:** 2026-03-20
**Valid until:** 2026-04-20 (30 days -- stable domain, no fast-moving dependencies)

---
*Phase 1 research for: HotelBook - Foundation & Authentication*
*Researched: 2026-03-20*
