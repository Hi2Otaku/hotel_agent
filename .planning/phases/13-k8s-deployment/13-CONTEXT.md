# Phase 13: k8s deployment - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Migrate HotelBook's production deployment from Docker Compose on EC2 to Kubernetes (k3s) on the same EC2 instance. Create Helm charts for all services, update CI/CD to deploy via kubectl/helm, and replace nginx with Traefik IngressRoute routing. Docker Compose remains available for local development.

</domain>

<decisions>
## Implementation Decisions

### Cluster target
- k3s on the existing EC2 t3.medium (4GB RAM) instance
- k8s runs alongside Docker Compose — Compose stays for local dev, k8s is the production deployment
- CI/CD (GitHub Actions) updated to deploy to k8s instead of Docker Compose
- Resource constraints are tight at 4GB — resource limits/requests must be set on all pods

### Manifest approach
- Helm charts — single umbrella chart (hotelbook/) with all services as templates
- Separate values files: values.yaml (defaults), values-dev.yaml, values-prod.yaml
- Container images pushed to GitHub Container Registry (ghcr.io)
- CI builds images, pushes to ghcr.io, then deploys to k3s via helm upgrade

### Database & stateful services
- Consolidate 4 Postgres instances into 1 Postgres StatefulSet with 4 databases inside (auth, rooms, bookings, chat)
- Services keep separate database names and credentials — logical isolation, shared instance
- RabbitMQ as single-replica StatefulSet with PVC
- MinIO as single-replica StatefulSet with PVC
- Mailpit included in dev values only, not deployed in prod

### Ingress & networking
- Traefik (k3s built-in) as ingress controller — no separate nginx container
- Traefik IngressRoute CRDs for path-based routing: / → guest frontend, /staff/ → staff frontend, /api/ → gateway
- IP-based access (no domain, no TLS) — matches current EC2 setup
- K8s Secrets created/updated by CI/CD via kubectl (source of truth remains GitHub Secrets)

### Claude's Discretion
- Exact resource limits/requests per pod (within 4GB total constraint)
- k3s installation method and version
- Helm chart directory structure and template organization
- Health check / readiness probe configuration
- Namespace strategy (single namespace vs per-concern)
- Rolling update strategy configuration
- Init container patterns for database migrations

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current infrastructure
- `docker-compose.yml` — Dev compose with all services, databases, and infrastructure
- `docker-compose.prod.yml` — Production overlay with env var secrets, nginx, frontend containers
- `.github/workflows/ci.yml` — Current CI/CD pipeline (lint, test, build, deploy via SSH)

### Service Dockerfiles
- `services/auth/Dockerfile` — Auth service container
- `services/room/Dockerfile` — Room service container
- `services/booking/Dockerfile` — Booking service container
- `services/gateway/Dockerfile` — Gateway service container
- `services/chat/Dockerfile` — Chat service container
- `services/mcp-server/Dockerfile` — MCP server container
- `frontend/Dockerfile` — Guest frontend container
- `frontend-staff/Dockerfile` — Staff frontend container

### Nginx config (to be replaced by Traefik)
- `frontend/nginx.conf` — Guest frontend nginx config
- `frontend-staff/nginx.conf` — Staff frontend nginx config

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- All 8 Dockerfiles already build production-ready containers — no changes needed to app code
- `docker-compose.prod.yml` overlay pattern documents all production environment variables needed
- JWT keys mounted as volume secrets (`./keys:/run/secrets:ro`) — maps to k8s Secret volumes
- `shared/` package mounted as read-only volume — needs to be baked into images (already done in Dockerfiles)

### Established Patterns
- Database-per-service with separate credentials (auth_user/room_user/booking_user/chat_user)
- Service discovery via DNS names (auth, room, booking, gateway, chat) — maps directly to k8s Service names
- Health checks defined in compose — translate to k8s liveness/readiness probes
- Environment-based configuration (DATABASE_URL, JWT paths, service URLs) — maps to k8s ConfigMaps/Secrets

### Integration Points
- CI/CD pipeline (.github/workflows/ci.yml) — deploy job needs rewrite from SSH+compose to kubectl/helm
- Service-to-service URLs (http://auth:8000, etc.) — k8s Service DNS follows same pattern
- Frontend nginx configs handle SPA routing (try_files) — Traefik or frontend container must preserve this

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 13-k8s-deployment*
*Context gathered: 2026-03-23*
