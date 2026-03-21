# Phase 4: Booking Engine - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Full booking lifecycle in the Booking service: three-step creation flow (reserve → guest details → payment), mock payment with Stripe-like test cards, confirmation with email via Mailpit, guest booking management (view/cancel/modify with price recalculation), booking state machine with automatic PENDING expiry. Publishes booking events via RabbitMQ for Room service availability updates.

</domain>

<decisions>
## Implementation Decisions

### Booking Flow Steps
- Three-step API flow:
  1. **Reserve**: Guest selects room type + dates → creates PENDING booking, room is held (reserved)
  2. **Guest Details**: Submit guest info (name, email, phone, address, special requests, ID/passport)
  3. **Payment**: Submit mock payment → booking becomes CONFIRMED, confirmation email sent
- Room held at step 1 (PENDING state) — prevents others from booking the same room
- Pessimistic locking (SELECT ... FOR UPDATE) at reservation step to prevent double-booking
- Confirmation number format: Claude's discretion (something professional like HB-XXXXXX)

### Mock Payment
- Standard card fields: card number, expiry (MM/YY), CVC, cardholder name, billing address
- Simulated 2-3 second processing delay for realism
- Stripe-like test cards: specific card numbers trigger specific outcomes
  - 4242424242424242 → success
  - 4000000000000002 → decline
  - 4111111111111111 → insufficient funds
- Payment generates a transaction record: transaction ID, amount, last 4 digits, timestamp, status
- Card data is NOT stored — only last 4 digits and transaction metadata

### Cancellation & Modification
- Cancellation policy: free cancellation up to N days before check-in (N is admin-configurable)
- Late cancellation penalty: first night's charge
- Policy displayed during booking flow (BOOK-05)
- Guests can modify: dates, room type, guest count, guest details
- Date/room type changes subject to availability check
- Price automatically recalculated on modification — show old vs new price
- Cannot modify after check-in

### PENDING Expiry
- PENDING bookings auto-cancel after 15 minutes
- Cleanup: both background task (every 5 min) AND on-demand check when booking is accessed
- Expired bookings transition to CANCELLED with reason "expired"
- Room availability updates via RabbitMQ event on expiry

### Booking State Machine
- States: PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT
- Additional transitions: PENDING → CANCELLED (manual or expired), CONFIRMED → CANCELLED (guest cancels)
- BookingStatus enum already defined in Phase 1 auth migration
- State transitions must be validated — no skipping states

### Cross-Service Integration
- Booking service publishes events via RabbitMQ on every state change (matches contract from Phase 3)
- Room service consumes events to update reservation projections
- Booking service calls Room service (or uses shared pricing engine) for price calculations
- Gateway needs booking endpoints added to BFF
- Mock email confirmation sent via Mailpit (same pattern as Phase 1 password reset)

### Claude's Discretion
- Confirmation number format
- Transaction ID format
- Exact test card number mappings beyond the 3 specified
- Background task implementation (asyncio periodic vs dedicated worker)
- How Booking service gets pricing data (call Room service API vs replicate pricing logic)
- Cancellation policy default days value
- Gateway BFF endpoint design for booking operations

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project research (internal)
- `.planning/research/STACK.md` — Technology stack with versions
- `.planning/research/ARCHITECTURE.md` — Booking state machine, pessimistic locking
- `.planning/research/PITFALLS.md` — Double-booking, date range logic, pricing inconsistencies, state machine design

### Phase 3 event contract
- `services/room/app/services/event_consumer.py` — RabbitMQ consumer defining the booking event schema Booking service must publish to
- `services/room/app/models/reservation.py` — ReservationProjection model that consumes booking events

### Phase 1 patterns
- `services/auth/app/services/email.py` — Email service pattern for Mailpit (reuse for booking confirmation)
- `services/auth/app/models/user.py` — SQLAlchemy model pattern with UUID PKs
- `services/auth/app/core/security.py` — JWT creation for booking service auth
- `shared/shared/messaging.py` — RabbitMQ publish helpers
- `shared/shared/database.py` — Async engine/session factory

### Phase 2 pricing
- `services/room/app/services/rate.py` — Pricing engine (calculate_nightly_rate, calculate_stay_price)

### Infrastructure
- `docker-compose.yml` — Container orchestration (booking_db already configured)
- `services/booking/app/main.py` — Booking service stub to extend

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/shared/messaging.py`: RabbitMQ helpers — Booking service publishes events using these
- `shared/shared/database.py`: Async engine factory — Booking service uses same pattern for booking_db
- `shared/shared/jwt.py`: JWT verification — Booking service validates guest tokens
- `services/auth/app/services/email.py`: Email service via Mailpit — pattern to replicate for booking confirmations
- `services/room/app/services/rate.py`: `calculate_stay_price()` — Booking service needs pricing data

### Established Patterns
- Three-layer: `api/v1/*.py` → `services/*.py` → `models/*.py`
- Claims-based JWT auth (Room service pattern) — Booking service needs guest auth
- Alembic async migrations per service
- All monetary values as Decimal
- RabbitMQ event publishing to match Phase 3 consumer contract

### Integration Points
- Booking service publishes to RabbitMQ exchange that Room service consumes
- Event schema must match what `event_consumer.py` expects (booking_id, room_type_id, room_id, check_in, check_out, status, guest_count)
- Gateway needs booking BFF endpoints
- Booking service needs to verify guest JWT tokens (but not staff — guests only for this phase)
- Pricing: Booking service calls Room service API or replicates pricing logic

</code_context>

<specifics>
## Specific Ideas

- Stripe-like test card system demonstrates API design sophistication — shows understanding of payment integration patterns
- Three-step flow mirrors real hotel booking UX — each step is a separate API call with state persistence
- 15-minute PENDING expiry with dual cleanup (background + on-demand) shows production-grade reliability thinking
- Configurable cancellation policy demonstrates admin-driven business rules

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-booking-engine*
*Context gathered: 2026-03-21*
