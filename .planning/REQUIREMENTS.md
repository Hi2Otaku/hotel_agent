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

- [ ] **BOOK-01**: Guest can complete multi-step booking (select room -> guest details -> payment -> confirmation)
- [ ] **BOOK-02**: Guest completes mock payment with Stripe-like card form
- [ ] **BOOK-03**: Guest receives booking confirmation page with confirmation number
- [ ] **BOOK-04**: Guest receives mock email confirmation
- [ ] **BOOK-05**: Cancellation policy displayed during booking flow

### Booking Management

- [ ] **MGMT-01**: Guest can view upcoming and past bookings with status
- [ ] **MGMT-02**: Guest can cancel a booking (with policy enforcement)
- [ ] **MGMT-03**: Guest can modify booking dates/room with automatic price recalculation

### Staff Reservations

- [ ] **STAF-01**: Staff can view all reservations with search/filter (name, date, status, confirmation #)
- [ ] **STAF-02**: Staff can check in guests (assign specific room)
- [ ] **STAF-03**: Staff can check out guests
- [ ] **STAF-04**: Staff can view guest profile with booking history

### Room Management

- [x] **RMGT-01**: Staff can create/edit/delete room types (with photos, amenities, capacity)
- [x] **RMGT-02**: Staff can manage individual rooms (number, floor, status)
- [x] **RMGT-03**: Staff can view room status board (occupied, vacant, cleaning, maintenance)
- [x] **RMGT-04**: Housekeeping status tracking (auto-mark dirty on checkout, clean/inspected toggle)

### Rate Management

- [x] **RATE-01**: Staff can set base rates per room type
- [x] **RATE-02**: Staff can create seasonal pricing rules (date-range overrides, weekend surcharges)

### Reporting

- [ ] **REPT-01**: Staff dashboard shows occupancy rate by date range
- [ ] **REPT-02**: Staff dashboard shows revenue summary
- [ ] **REPT-03**: Staff dashboard shows booking trend charts (interactive)

### Infrastructure

- [ ] **INFR-01**: Responsive design for guest-facing site (mobile-first)
- [ ] **INFR-02**: Unit and integration tests with CI/CD pipeline (GitHub Actions)
- [ ] **INFR-03**: Deployed with live demo URL and documentation

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
| BOOK-01 | Phase 4 | Pending |
| BOOK-02 | Phase 4 | Pending |
| BOOK-03 | Phase 4 | Pending |
| BOOK-04 | Phase 4 | Pending |
| BOOK-05 | Phase 4 | Pending |
| MGMT-01 | Phase 4 | Pending |
| MGMT-02 | Phase 4 | Pending |
| MGMT-03 | Phase 4 | Pending |
| INFR-01 | Phase 5 | Pending |
| STAF-01 | Phase 6 | Pending |
| STAF-02 | Phase 6 | Pending |
| STAF-03 | Phase 6 | Pending |
| STAF-04 | Phase 6 | Pending |
| REPT-01 | Phase 7 | Pending |
| REPT-02 | Phase 7 | Pending |
| REPT-03 | Phase 7 | Pending |
| INFR-02 | Phase 8 | Pending |
| INFR-03 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-20 after roadmap creation*
