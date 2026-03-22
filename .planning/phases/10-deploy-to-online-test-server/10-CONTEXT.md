# Phase 10: Deploy to Online Test Server - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Get the HotelBook application running on a publicly accessible EC2 instance for demo and testing purposes. This includes instance provisioning, security configuration, secrets management, extended seed data, and CI/CD integration. Does NOT include custom domain setup, SSL certificates, or production hardening beyond what's needed for a test server.

</domain>

<decisions>
## Implementation Decisions

### Hosting provider
- AWS EC2, t3.small instance (2 vCPU, 2GB RAM, ~$15/mo)
- Region: us-east-1 (N. Virginia)
- User already has an AWS account, needs instance provisioning
- Add swap file to help with memory pressure from 11+ containers
- Security group: open ports 80 (HTTP) and 22 (SSH)

### Domain & SSL
- EC2 public IP only — no custom domain for now
- HTTP only — no SSL needed for test server
- Nginx config: remove/comment SSL blocks, listen on port 80 only
- Can add domain and Let's Encrypt later if needed

### Demo data & access
- Publicly accessible — anyone with the URL can access
- Extended seed data: add fake guest accounts and sample bookings so staff dashboard has data to show immediately
- Seed should include: 5-10 guest accounts, 20-30 bookings across various statuses (confirmed, checked-in, checked-out, cancelled)
- Admin credentials set via environment variable (ADMIN_EMAIL, ADMIN_PASSWORD on the server)

### Secrets & security
- JWT keys: stored as GitHub Secrets, deploy script writes them to disk on the server
- Database passwords: all stored as GitHub Secrets, deploy script creates .env file
- GitHub secrets needed: EC2_HOST, EC2_USER, EC2_SSH_KEY, JWT_PRIVATE_KEY, JWT_PUBLIC_KEY, AUTH_DB_PASSWORD, ROOM_DB_PASSWORD, BOOKING_DB_PASSWORD, RABBITMQ_PASS, ADMIN_EMAIL, ADMIN_PASSWORD
- Dev keys in repo remain for local development — production keys never touch the repo

### Claude's Discretion
- Exact swap file size (1-2GB recommended)
- EC2 AMI choice (Amazon Linux 2023 or Ubuntu)
- Docker installation method
- Seed data content (room types, guest names, booking dates)
- Deploy script structure

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Deployment infrastructure
- `docker-compose.yml` — Dev compose with all services, ports, and DB configs
- `docker-compose.prod.yml` — Prod overlay adding frontends, nginx, restart policies
- `nginx/conf.d/default.conf` — Reverse proxy routing rules (API, staff, guest)
- `.github/workflows/ci.yml` — CI/CD pipeline with SSH deploy job
- `.env.example` — Required environment variables documentation

### Frontend builds
- `frontend/Dockerfile` — Guest frontend multi-stage build
- `frontend-staff/Dockerfile` — Staff frontend multi-stage build
- `frontend/nginx.conf` — Guest SPA serving config
- `frontend-staff/nginx.conf` — Staff SPA serving config

### Key management
- `scripts/generate_keys.sh` — RSA key pair generation script

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docker-compose.prod.yml`: Production overlay ready — adds frontends, nginx, restart policies
- `nginx/conf.d/default.conf`: Full reverse proxy config — routes /api/, /staff/, / correctly
- `.github/workflows/ci.yml`: Deploy job already targets EC2 via SSH (`appleboy/ssh-action@v1`)
- `scripts/generate_keys.sh`: Key generation script exists
- Room service `SEED_ON_STARTUP=true`: Auto-seeds room types and rooms

### Established Patterns
- Docker Compose overlay: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`
- Gateway hides behind nginx in prod (ports removed)
- Frontend builds: Node build stage → nginx serve stage
- Dev credentials inline in compose, prod overrides from env vars

### Integration Points
- CI deploy job needs GitHub secrets configured
- `.env` file on server feeds docker-compose env vars
- JWT keys mounted read-only at `/run/secrets/` in backend containers
- Nginx expects `frontend-guest:80` and `frontend-staff:80` as upstream services

</code_context>

<specifics>
## Specific Ideas

- Extended seed should make the staff dashboard immediately impressive — occupancy data, check-ins/outs for today, revenue for reports
- The deploy should be reproducible — anyone with the right AWS/GitHub access should be able to redeploy

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 10-deploy-to-online-test-server*
*Context gathered: 2026-03-22*
