# HotelBook

## What This Is

A full-stack hotel reservation application for a single property, featuring a guest-facing React booking site and a staff management dashboard. Guests can search availability, book rooms, complete mock payments, and manage their reservations. Hotel staff get a comprehensive dashboard for bookings, room/rate management, reports, and guest history. Built as a portfolio piece showcasing production-grade full-stack development.

## Core Value

Guests can seamlessly search, book, and manage room reservations with a polished experience that demonstrates real-world full-stack competency.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Guest account creation and login — Phase 1
- ✓ Staff authentication and role-based access — Phase 1
- ✓ Room management (types, rates, availability, status) — Phase 2
- ✓ Rate management (seasonal pricing, discounts) — Phase 2
- ✓ Guest room search by date and filters — Phase 3
- ✓ Room availability calendar — Phase 3
- ✓ Full booking flow (select room → guest details → mock payment → confirmation) — Phase 4
- ✓ Guest booking management (view, modify, cancel) — Phase 4
- ✓ Email confirmation (mock/simulated) — Phase 4

### Active

<!-- Current scope. Building toward these. -->
- [ ] Staff booking management (view all, check-in, check-out)
- [ ] Guest history and profiles (staff view)
- [ ] Reporting dashboard (occupancy, revenue, booking trends)
- [ ] Mock payment integration (simulated Stripe-like flow)
- [ ] Responsive design for guest-facing site
- [ ] Tests and CI/CD pipeline
- [ ] Deployment-ready with documentation

### Out of Scope

- Real payment processing — mock payments only, no actual charges
- Multi-property support — single hotel only
- Mobile native app — web responsive is sufficient
- Real-time chat/messaging — not needed for reservation flow
- Third-party OTA integration (Booking.com, Expedia) — complexity not justified for portfolio

## Context

- Portfolio project aimed at showcasing full-stack skills with a realistic domain
- Target audience: potential employers and collaborators reviewing the codebase and live demo
- Should demonstrate clean architecture, testing practices, and deployment competency
- Single hotel property simplifies data model while still covering core reservation patterns

## Constraints

- **Tech stack**: Python/FastAPI backend, React frontend, PostgreSQL database
- **Payments**: Mock only — simulated payment flow that looks real but processes no charges
- **Deployment**: Must be deployable with live demo URL
- **Quality**: Tests and CI/CD required — this is a portfolio piece that needs to demonstrate engineering rigor

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI over Django | Async-first, modern Python, better API design showcase | — Pending |
| React SPA over Next.js | Clearer separation of concerns, simpler deployment model | — Pending |
| PostgreSQL over SQLite | Production-grade credibility for portfolio | — Pending |
| Mock payments over Stripe | Avoids real payment complexity while demonstrating the integration pattern | — Pending |
| Single property | Keeps data model focused; multi-property adds complexity without portfolio value | — Pending |

---
*Last updated: 2026-03-21 after Phase 4 completion*
