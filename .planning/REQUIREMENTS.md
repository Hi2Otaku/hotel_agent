# Requirements: HotelBook

**Defined:** 2026-03-20
**Core Value:** Guests can seamlessly search, book, and manage room reservations with a polished experience that demonstrates real-world full-stack competency.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [x] **AUTH-01**: Guest can create account with email and password
- [x] **AUTH-02**: Guest can log in and stay logged in across sessions (JWT)
- [x] **AUTH-03**: Guest can reset password via email link (simulated)
- [x] **AUTH-04**: Staff can log in with role-based access (admin, manager, front desk)

### Room Search & Availability

- [x] **ROOM-01**: Guest can search rooms by check-in/check-out dates and guest count
- [x] **ROOM-02**: Guest sees only available rooms for selected dates (real-time availability)
- [x] **ROOM-03**: Guest can view room details (photos, amenities, capacity, per-night price)
- [x] **ROOM-04**: Guest can see pricing calendar showing per-night rates and availability

### Booking Flow

- [x] **BOOK-01**: Guest can complete multi-step booking (select room -> guest details -> payment -> confirmation)
- [x] **BOOK-02**: Guest completes mock payment with Stripe-like card form
- [x] **BOOK-03**: Guest receives booking confirmation page with confirmation number
- [x] **BOOK-04**: Guest receives mock email confirmation
- [x] **BOOK-05**: Cancellation policy displayed during booking flow

### Booking Management

- [x] **MGMT-01**: Guest can view upcoming and past bookings with status
- [x] **MGMT-02**: Guest can cancel a booking (with policy enforcement)
- [x] **MGMT-03**: Guest can modify booking dates/room with automatic price recalculation

### Staff Reservations

- [x] **STAF-01**: Staff can view all reservations with search/filter (name, date, status, confirmation #)
- [x] **STAF-02**: Staff can check in guests (assign specific room)
- [x] **STAF-03**: Staff can check out guests
- [x] **STAF-04**: Staff can view guest profile with booking history

### Room Management

- [x] **RMGT-01**: Staff can create/edit/delete room types (with photos, amenities, capacity)
- [x] **RMGT-02**: Staff can manage individual rooms (number, floor, status)
- [x] **RMGT-03**: Staff can view room status board (occupied, vacant, cleaning, maintenance)
- [x] **RMGT-04**: Housekeeping status tracking (auto-mark dirty on checkout, clean/inspected toggle)

### Rate Management

- [x] **RATE-01**: Staff can set base rates per room type
- [x] **RATE-02**: Staff can create seasonal pricing rules (date-range overrides, weekend surcharges)

### Reporting

- [x] **REPT-01**: Staff dashboard shows occupancy rate by date range
- [x] **REPT-02**: Staff dashboard shows revenue summary
- [x] **REPT-03**: Staff dashboard shows booking trend charts (interactive)

### Infrastructure

- [x] **INFR-01**: Responsive design for guest-facing site (mobile-first)
- [x] **INFR-02**: Unit and integration tests with CI/CD pipeline (GitHub Actions)
- [x] **INFR-03**: Deployed with live demo URL and documentation

### Deployment (Phase 10)

- [x] **DEPLOY-01**: EC2 server provisioned with Docker, swap, and reproducible setup script
- [x] **DEPLOY-02**: Production secrets (JWT keys, DB passwords) managed via GitHub Secrets, never in repo
- [x] **DEPLOY-03**: Extended demo data: guest accounts and historical bookings seeded on startup
- [x] **DEPLOY-04**: Full stack accessible at EC2 public IP over HTTP with automated health checks

### Dependency Management (Phase 12)

- [x] **UV-01**: Each backend service has its own pyproject.toml with uv.lock for reproducible installs
- [x] **UV-02**: Shared package referenced as path dependency in all services
- [x] **UV-03**: Tests relocated into per-service directories and runnable via `uv run pytest`
- [x] **UV-04**: Old requirements.txt files deprecated with migration comment
- [x] **UV-05**: Dockerfiles use uv (COPY --from=ghcr.io/astral-sh/uv) with no pip commands
- [x] **UV-06**: CI pipeline uses astral-sh/setup-uv with caching for all Python jobs
- [x] **UV-07**: Root Makefile provides setup, sync, test, and lint targets for developer workflow

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Visual Tools

- **VCAL-01**: Visual availability calendar (timeline/Gantt-style view for staff)
- **VCAL-02**: Guest-facing pricing calendar widget on landing page

### Audit & Compliance

- **AUDT-01**: Audit log for all staff actions (booking changes, rate changes, check-in/out)
- **AUDT-02**: Admin can view audit log with filters

### Email Notifications

- **EMAL-01**: Simulated email notification system with viewable log
- **EMAL-02**: Email templates for confirmation, cancellation, reminder

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real payment processing | Mock payments only -- avoids PCI complexity while demonstrating integration pattern |
| Multi-property support | Single hotel keeps data model focused; multi-property doubles complexity |
| OTA integration (Booking.com, Expedia) | Requires API partnerships and complex inventory sync |
| Real-time chat/messaging | Orthogonal to reservation domain; high complexity, low portfolio value |
| Mobile native app | Responsive web sufficient; native doubles codebase |
| AI-powered pricing | Rule-based pricing demonstrates same business logic without AI overhead |
| Loyalty/rewards program | Significant feature surface for single-property project |
| Multi-language/i18n | Build i18n-ready patterns but ship English-only |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1 | Complete |
| AUTH-02 | Phase 1 | Complete |
| AUTH-03 | Phase 1 | Complete |
| AUTH-04 | Phase 1 | Complete |
| RMGT-01 | Phase 2 | Complete |
| RMGT-02 | Phase 2 | Complete |
| RMGT-03 | Phase 2 | Complete |
| RMGT-04 | Phase 2 | Complete |
| RATE-01 | Phase 2 | Complete |
| RATE-02 | Phase 2 | Complete |
| ROOM-01 | Phase 3 | Complete |
| ROOM-02 | Phase 3 | Complete |
| ROOM-03 | Phase 3 | Complete |
| ROOM-04 | Phase 3 | Complete |
| BOOK-01 | Phase 4 | Complete |
| BOOK-02 | Phase 4 | Complete |
| BOOK-03 | Phase 4 | Complete |
| BOOK-04 | Phase 4 | Complete |
| BOOK-05 | Phase 4 | Complete |
| MGMT-01 | Phase 4 | Complete |
| MGMT-02 | Phase 4 | Complete |
| MGMT-03 | Phase 4 | Complete |
| INFR-01 | Phase 5 | Complete |
| STAF-01 | Phase 6 | Complete |
| STAF-02 | Phase 6 | Complete |
| STAF-03 | Phase 6 | Complete |
| STAF-04 | Phase 6 | Complete |
| REPT-01 | Phase 7 | Complete |
| REPT-02 | Phase 7 | Complete |
| REPT-03 | Phase 7 | Complete |
| INFR-02 | Phase 8 | Complete |
| INFR-03 | Phase 8 | Complete |
| DEPLOY-01 | Phase 10 | Planned |
| DEPLOY-02 | Phase 10 | Planned |
| DEPLOY-03 | Phase 10 | Planned |
| DEPLOY-04 | Phase 10 | Planned |
| UV-01 | Phase 12 | Planned |
| UV-02 | Phase 12 | Planned |
| UV-03 | Phase 12 | Planned |
| UV-04 | Phase 12 | Planned |
| UV-05 | Phase 12 | Planned |
| UV-06 | Phase 12 | Planned |
| UV-07 | Phase 12 | Planned |

**Coverage:**
- v1 requirements: 32 total (complete)
- Phase 10 requirements: 4 total (planned)
- Phase 12 requirements: 7 total (planned)
- Mapped to phases: 43
- Unmapped: 0

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-23 after Phase 12 planning*
