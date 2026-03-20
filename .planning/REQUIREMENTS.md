# Requirements: HotelBook

**Defined:** 2026-03-20
**Core Value:** Guests can seamlessly search, book, and manage room reservations with a polished experience that demonstrates real-world full-stack competency.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [ ] **AUTH-01**: Guest can create account with email and password
- [ ] **AUTH-02**: Guest can log in and stay logged in across sessions (JWT)
- [ ] **AUTH-03**: Guest can reset password via email link (simulated)
- [ ] **AUTH-04**: Staff can log in with role-based access (admin, manager, front desk)

### Room Search & Availability

- [ ] **ROOM-01**: Guest can search rooms by check-in/check-out dates and guest count
- [ ] **ROOM-02**: Guest sees only available rooms for selected dates (real-time availability)
- [ ] **ROOM-03**: Guest can view room details (photos, amenities, capacity, per-night price)
- [ ] **ROOM-04**: Guest can see pricing calendar showing per-night rates and availability

### Booking Flow

- [ ] **BOOK-01**: Guest can complete multi-step booking (select room → guest details → payment → confirmation)
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

- [ ] **RMGT-01**: Staff can create/edit/delete room types (with photos, amenities, capacity)
- [ ] **RMGT-02**: Staff can manage individual rooms (number, floor, status)
- [ ] **RMGT-03**: Staff can view room status board (occupied, vacant, cleaning, maintenance)
- [ ] **RMGT-04**: Housekeeping status tracking (auto-mark dirty on checkout, clean/inspected toggle)

### Rate Management

- [ ] **RATE-01**: Staff can set base rates per room type
- [ ] **RATE-02**: Staff can create seasonal pricing rules (date-range overrides, weekend surcharges)

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
| Real payment processing | Mock payments only — avoids PCI complexity while demonstrating integration pattern |
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
| AUTH-01 | — | Pending |
| AUTH-02 | — | Pending |
| AUTH-03 | — | Pending |
| AUTH-04 | — | Pending |
| ROOM-01 | — | Pending |
| ROOM-02 | — | Pending |
| ROOM-03 | — | Pending |
| ROOM-04 | — | Pending |
| BOOK-01 | — | Pending |
| BOOK-02 | — | Pending |
| BOOK-03 | — | Pending |
| BOOK-04 | — | Pending |
| BOOK-05 | — | Pending |
| MGMT-01 | — | Pending |
| MGMT-02 | — | Pending |
| MGMT-03 | — | Pending |
| STAF-01 | — | Pending |
| STAF-02 | — | Pending |
| STAF-03 | — | Pending |
| STAF-04 | — | Pending |
| RMGT-01 | — | Pending |
| RMGT-02 | — | Pending |
| RMGT-03 | — | Pending |
| RMGT-04 | — | Pending |
| RATE-01 | — | Pending |
| RATE-02 | — | Pending |
| REPT-01 | — | Pending |
| REPT-02 | — | Pending |
| REPT-03 | — | Pending |
| INFR-01 | — | Pending |
| INFR-02 | — | Pending |
| INFR-03 | — | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 0
- Unmapped: 32 ⚠️

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-20 after initial definition*
