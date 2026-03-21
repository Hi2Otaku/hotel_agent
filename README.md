# HotelBook

Full-stack hotel reservation system with microservice architecture, demonstrating real-world booking workflows, staff operations, and analytics.

## Live Demo

- **Guest App:** [https://YOUR_DOMAIN](https://YOUR_DOMAIN)
- **Staff Dashboard:** [https://YOUR_DOMAIN/staff/](https://YOUR_DOMAIN/staff/)
- **API Docs (Swagger):** [https://YOUR_DOMAIN/docs](https://YOUR_DOMAIN/docs)

**Demo Credentials:**
- Guest: Register with any email address
- Staff: `admin@hotel.local` / `admin123`

## Features

- **Guest Booking:** Room search with date-based availability, multi-step booking wizard, mock payment processing, booking management (view, modify, cancel)
- **Staff Operations:** Reservation management with check-in/check-out, room status board, guest profiles and history
- **Analytics Dashboard:** Occupancy heatmap, revenue charts, booking trend analysis with drill-down and CSV/PDF export
- **Infrastructure:** JWT authentication (RS256 asymmetric), role-based access control, event-driven architecture via RabbitMQ, email notifications via Mailpit

## Architecture

```
                          +------------------+
                          |     Nginx        |
                          |  (reverse proxy) |
                          +--------+---------+
                                   |
                 +-----------------+------------------+
                 |                 |                   |
          +------+------+  +------+------+   +--------+--------+
          | Guest SPA   |  | Staff SPA   |   | API Gateway     |
          | (React/Vite)|  | (React/Vite)|   | :8000           |
          | :5173 (dev) |  | :5174 (dev) |   +--------+--------+
          +-------------+  +-------------+            |
                                            +---------+---------+
                                            |         |         |
                                      +-----+--+ +---+----+ +--+-------+
                                      |  Auth  | |  Room  | | Booking  |
                                      | :8001  | | :8002  | | :8003    |
                                      +---+----+ +---+----+ +----+-----+
                                          |         |             |
                                      +---+----+ +--+-----+ +----+-----+
                                      |auth_db | |room_db | |booking_db|
                                      | :5433  | | :5434  | | :5435    |
                                      +--------+ +--------+ +----------+

              +------------+    +-----------+    +-----------+
              |  RabbitMQ  |    |   MinIO   |    |  Mailpit  |
              |  (events)  |    |  (photos) |    |  (email)  |
              |  :5672     |    |  :9000    |    |  :1025    |
              +------------+    +-----------+    +-----------+
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **Gateway** | 8000 | API gateway and BFF (Backend-for-Frontend) endpoints |
| **Auth** | 8001 | Authentication, user management, RBAC |
| **Room** | 8002 | Room types, rooms, rates, availability, photos |
| **Booking** | 8003 | Booking lifecycle, payments, email notifications |

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Pydantic v2 |
| Frontend | React 19, TypeScript, Vite, TailwindCSS, shadcn/ui |
| Databases | PostgreSQL 16 (3 separate instances, one per service) |
| Messaging | RabbitMQ (inter-service events) |
| Storage | MinIO (S3-compatible object storage for room photos) |
| Email | Mailpit (development email capture) |
| Proxy | Nginx (production reverse proxy, SSL termination) |
| CI/CD | GitHub Actions (lint, test, build, deploy) |
| Deployment | Docker Compose on AWS EC2 |

## Getting Started

### Prerequisites

- Docker and Docker Compose v2
- Node.js 20+
- Python 3.12+

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/hotelbook.git
   cd hotelbook
   ```

2. **Generate JWT keys:**
   ```bash
   mkdir -p keys
   openssl genrsa -out keys/jwt-private.pem 2048
   openssl rsa -in keys/jwt-private.pem -pubout -out keys/jwt-public.pem
   ```

3. **Start all services:**
   ```bash
   docker compose up -d --build
   ```

4. **Wait for services to be healthy:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Access the application:**
   - Guest app: http://localhost:5173
   - Staff dashboard: http://localhost:5174
   - API docs: http://localhost:8000/docs

## Running Tests

### Backend Tests
Requires Docker Compose database containers running:
```bash
pytest tests/ -x --tb=short
```

Run a specific service:
```bash
pytest tests/auth -x --tb=short
pytest tests/booking -x --tb=short
pytest tests/room -x --tb=short
pytest tests/gateway -x --tb=short
```

### Guest Frontend Tests
```bash
cd frontend && npm test
```

### Staff Frontend Tests
```bash
cd frontend-staff && npm test
```

### E2E Tests
Requires the full stack running via Docker Compose:
```bash
cd e2e && npx playwright test
```

### CI
Push to `main` or open a pull request -- GitHub Actions runs all tests automatically (lint, backend tests, frontend tests, E2E tests, build verification).

## Project Structure

```
services/
  auth/              # Authentication & user management
  room/              # Room types, rooms, rates, availability
  booking/           # Booking lifecycle & payments
  gateway/           # API gateway & BFF endpoints
shared/              # Shared library (JWT, DB helpers, messaging)
frontend/            # Guest-facing React SPA
frontend-staff/      # Staff dashboard React SPA
e2e/                 # Playwright E2E tests
tests/               # Backend integration tests
nginx/               # Production reverse proxy config
keys/                # JWT RSA keys (generated, not committed)
.github/workflows/   # CI/CD pipeline
```

## Deployment

### Production (Docker Compose)
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### CI/CD Pipeline
GitHub Actions automatically deploys to EC2 on merge to `main`:
1. **Lint** -- ruff (backend) + eslint (frontends)
2. **Backend Tests** -- pytest against real PostgreSQL containers
3. **Frontend Tests** -- Vitest for both guest and staff apps
4. **E2E Tests** -- Playwright against full Docker stack
5. **Build** -- validates all Docker images compile
6. **Deploy** -- SSH to EC2, pull latest, rebuild containers

### SSL Setup
On EC2, install Certbot for Let's Encrypt SSL:
```bash
sudo certbot certonly --standalone -d YOUR_DOMAIN
```
Then uncomment the SSL server block in `nginx/conf.d/default.conf`.

## Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `AUTH_DATABASE_URL` | Auth | PostgreSQL connection for auth database |
| `ROOM_DATABASE_URL` | Room | PostgreSQL connection for room database |
| `BOOKING_DATABASE_URL` | Booking | PostgreSQL connection for booking database |
| `JWT_PRIVATE_KEY_PATH` | Auth | Path to RSA private key for signing tokens |
| `JWT_PUBLIC_KEY_PATH` | All services | Path to RSA public key for verifying tokens |
| `RABBITMQ_URL` | Auth, Room, Booking | AMQP connection URL for event messaging |
| `MAIL_SERVER` | Auth, Booking | SMTP server hostname |
| `MAIL_PORT` | Auth, Booking | SMTP server port |
| `MINIO_ENDPOINT` | Room | MinIO S3-compatible endpoint |
| `MINIO_ACCESS_KEY` | Room | MinIO access key |
| `MINIO_SECRET_KEY` | Room | MinIO secret key |
| `MINIO_BUCKET` | Room | MinIO bucket name for photos |
| `MINIO_SECURE` | Room | Use HTTPS for MinIO (`true`/`false`) |
| `ROOM_SERVICE_URL` | Booking, Gateway | Internal URL for room service |
| `AUTH_SERVICE_URL` | Gateway | Internal URL for auth service |
| `BOOKING_SERVICE_URL` | Gateway | Internal URL for booking service |

## API Endpoints

Full interactive API documentation is available at `/docs` (Swagger UI) on each service.

| Group | Method | Endpoint | Description |
|-------|--------|----------|-------------|
| **Auth** | POST | `/api/v1/auth/register` | Register a new guest account |
| | POST | `/api/v1/auth/login` | Login and receive JWT tokens |
| | GET | `/api/v1/auth/me` | Get current user profile |
| **Rooms** | GET | `/api/v1/rooms` | List all rooms |
| | GET | `/api/v1/rooms/types` | List room types |
| | GET | `/api/v1/rooms/search` | Search available rooms by date/filters |
| **Bookings** | POST | `/api/v1/bookings` | Create a new booking |
| | GET | `/api/v1/bookings` | List user bookings |
| | PATCH | `/api/v1/bookings/{id}` | Modify or cancel a booking |
| **Staff** | GET | `/api/v1/staff/bookings` | List all bookings (staff only) |
| | POST | `/api/v1/staff/bookings/{id}/check-in` | Check in a guest |
| | POST | `/api/v1/staff/bookings/{id}/check-out` | Check out a guest |

## License

This is a portfolio project demonstrating full-stack development skills. MIT License.
