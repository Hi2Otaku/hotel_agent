# Phase 2: Room & Rate Management - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Staff CRUD for room types, individual rooms, base rates, seasonal pricing, room status lifecycle, and housekeeping tracking — all through API endpoints in the Room service. Includes seed data for a beach resort demo. This phase builds the data foundation that guest search (Phase 3) and booking (Phase 4) consume.

</domain>

<decisions>
## Implementation Decisions

### Room Type Modeling
- 3-4 room types for a beach resort: Ocean View, Garden Room, Junior Suite, Villa (or similar)
- Amenities modeled as categorized groups (Comfort: AC/Heating, Tech: WiFi/TV, Bathroom: Tub/Shower, etc.)
- Photos handled via file upload to MinIO (S3-compatible) — add MinIO container to Docker Compose
- Capacity is detailed: max adults + max children + structured bed configuration [{type: "king", count: 1}]

### Room Status Lifecycle
- 7 statuses: Available, Occupied, Cleaning, Inspected, Maintenance, Out of Order, Reserved
- Role-based transitions:
  - Front desk: Available ↔ Occupied, Reserved → Occupied (check-in)
  - Housekeeping (any staff): Cleaning → Inspected
  - Manager/Admin: Maintenance, Out of Order toggles
- Automatic transitions:
  - Checkout → room auto-moves to Cleaning
  - Inspection complete → room auto-moves to Available
  - Booking confirmed + room assigned → room auto-moves to Reserved
- Manual override always available for managers/admins
- Status board: grid layout grouped by floor, color-coded by status
- Status change history logged with who/when timestamps

### Pricing Structure
- Base rates per room type with occupancy tiers (1-2 guests = base, 3+ = higher rate)
- Seasonal pricing: date-range overrides with multiplier (e.g., "Summer Peak: Jun 1 - Aug 31, 1.3x")
- Weekend surcharges: per room type, as a multiplier (e.g., Suite: 1.2x on Fri-Sat)
- Stacking: multiplicative (summer 1.3x × weekend 1.15x = 1.495x)
- No minimum stay rules in this phase — keep pricing focused on rates
- Currency: configurable by admin (stored as ISO 4217 code — USD, EUR, THB, etc.)

### Seed Data
- Full demo data: beach resort theme, 50-60 rooms across 3-4 types
- Unsplash URLs for room photos in seed data
- Include sample seasonal rates (summer peak, holiday, off-season) and weekend surcharges
- Seed runs on first boot or via management command

### Claude's Discretion
- Exact room type names and descriptions for the beach resort theme
- Amenity category names and which amenities go in each
- MinIO bucket naming and upload path conventions
- Status transition validation logic implementation
- Exact seed data quantities and pricing numbers
- Status board color scheme for each status

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project research (internal)
- `.planning/research/STACK.md` — Technology stack with versions
- `.planning/research/ARCHITECTURE.md` — Three-layer backend, database-per-service pattern
- `.planning/research/PITFALLS.md` — Date handling, pricing inconsistencies, async/sync mismatch

### Phase 1 established patterns
- `services/auth/app/models/user.py` — SQLAlchemy model pattern with UUID PKs
- `services/auth/app/api/v1/auth.py` — Route pattern with dependency injection
- `services/auth/app/services/auth.py` — Service layer pattern
- `services/auth/app/api/deps.py` — RBAC dependency chain (require_role)
- `shared/shared/database.py` — Async engine/session factory
- `shared/shared/jwt.py` — RS256 JWT verification for non-auth services
- `docker-compose.yml` — Existing container orchestration to extend

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/shared/database.py`: Async engine factory, session management — Room service uses same pattern
- `shared/shared/jwt.py`: JWT verification — Room service validates tokens with public key
- `services/auth/app/api/deps.py`: RBAC require_role dependency — pattern to replicate in Room service
- `services/auth/app/models/user.py`: User model with UUID PK and Enum — pattern for Room models

### Established Patterns
- Three-layer: `api/v1/*.py` (routes) → `services/*.py` (business logic) → `models/*.py` (ORM)
- Pydantic schemas in `schemas/*.py` for request/response validation
- Alembic async migrations with `alembic init -t async`
- Docker Compose with separate DB per service

### Integration Points
- Room service gets its own PostgreSQL container (room_db) — already stubbed in docker-compose.yml
- Room service Dockerfile follows auth service pattern
- Gateway proxy needs Room service routes added
- MinIO container needs to be added to docker-compose.yml

</code_context>

<specifics>
## Specific Ideas

- Beach resort theme for seed data — tropical vibe with Ocean View rooms, garden rooms, villas
- MinIO for photo storage demonstrates S3-compatible cloud storage pattern — portfolio-impressive
- Floor-grouped status board with color coding creates a visually compelling staff tool
- Status change logging creates an audit trail that demonstrates operational awareness

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-room-rate-management*
*Context gathered: 2026-03-21*
