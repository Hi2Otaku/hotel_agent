# Phase 10: Deploy to Online Test Server - Research

**Researched:** 2026-03-22
**Domain:** AWS EC2 deployment, Docker Compose production, GitHub Actions CI/CD, seed data
**Confidence:** HIGH

## Summary

Phase 10 deploys the existing HotelBook Docker Compose stack to an AWS EC2 t3.small instance in us-east-1. The infrastructure is largely in place: `docker-compose.prod.yml` provides the production overlay, nginx is configured for HTTP on port 80, the CI/CD pipeline has a deploy job using `appleboy/ssh-action@v1`, and both room and booking services already seed data on startup. The primary work involves: (1) creating a server setup script that installs Docker and configures swap on a fresh EC2 instance, (2) creating a deploy-time `.env` file from GitHub Secrets for production credentials, (3) extending the seed data to include guest user accounts, (4) updating the CI deploy job to write secrets to disk and handle the `.env` file, and (5) removing the 443 port from the prod overlay since we are HTTP-only.

The existing codebase handles most deployment concerns already. Room seed data (55 rooms, 4 types, rates) runs via `SEED_ON_STARTUP=true`. Booking seed data (800-1200 historical bookings) runs automatically in the booking service lifespan. The main gap is demo guest accounts in the auth service -- currently only the admin account is seeded on startup.

**Primary recommendation:** Use Ubuntu 22.04 LTS AMI, create a bash setup script for instance provisioning (Docker, swap, git clone), a deploy-time env/secrets script triggered from CI, and add guest account seeding to the auth service startup.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- AWS EC2, t3.small instance (2 vCPU, 2GB RAM, ~$15/mo)
- Region: us-east-1 (N. Virginia)
- User already has an AWS account, needs instance provisioning
- Add swap file to help with memory pressure from 11+ containers
- Security group: open ports 80 (HTTP) and 22 (SSH)
- EC2 public IP only -- no custom domain for now
- HTTP only -- no SSL needed for test server
- Nginx config: remove/comment SSL blocks, listen on port 80 only
- Publicly accessible -- anyone with the URL can access
- Extended seed data: add fake guest accounts and sample bookings so staff dashboard has data to show immediately
- Seed should include: 5-10 guest accounts, 20-30 bookings across various statuses (confirmed, checked-in, checked-out, cancelled)
- Admin credentials set via environment variable (ADMIN_EMAIL, ADMIN_PASSWORD on the server)
- JWT keys: stored as GitHub Secrets, deploy script writes them to disk on the server
- Database passwords: all stored as GitHub Secrets, deploy script creates .env file
- GitHub secrets needed: EC2_HOST, EC2_USER, EC2_SSH_KEY, JWT_PRIVATE_KEY, JWT_PUBLIC_KEY, AUTH_DB_PASSWORD, ROOM_DB_PASSWORD, BOOKING_DB_PASSWORD, RABBITMQ_PASS, ADMIN_EMAIL, ADMIN_PASSWORD
- Dev keys in repo remain for local development -- production keys never touch the repo

### Claude's Discretion
- Exact swap file size (1-2GB recommended)
- EC2 AMI choice (Amazon Linux 2023 or Ubuntu)
- Docker installation method
- Seed data content (room types, guest names, booking dates)
- Deploy script structure

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DEPLOY-01 | EC2 server provisioned with Docker, swap, and reproducible setup script | Server setup script with Docker CE install, 2GB swap, firewall, git clone -- see Architecture Patterns |
| DEPLOY-02 | Production secrets (JWT keys, DB passwords) managed via GitHub Secrets, never in repo | CI deploy job writes .env from secrets, writes JWT keys to keys/ dir -- see Secrets Management pattern |
| DEPLOY-03 | Extended demo data: guest accounts and historical bookings seeded on startup | Auth service needs guest seed function; booking seed already exists (800-1200 bookings); need 5-10 guest accounts -- see Seed Data pattern |
| DEPLOY-04 | Full stack accessible at EC2 public IP over HTTP with automated health checks | Nginx on port 80, CI health check after deploy, docker-compose.prod.yml adjustments -- see Health Check pattern |
</phase_requirements>

## Standard Stack

### Core (Already in Project)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Docker CE | Latest stable | Container runtime | Official install script for Ubuntu |
| Docker Compose | v2 (plugin) | Multi-container orchestration | Bundled with Docker CE install |
| nginx | stable-alpine | Reverse proxy, static serving | Already in docker-compose.prod.yml |
| appleboy/ssh-action | v1 | CI/CD SSH deploy | Already in ci.yml deploy job |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| Ubuntu 22.04 LTS AMI | EC2 base OS | Wider Docker/community support than Amazon Linux 2023 |
| ufw (Uncomplicated Firewall) | Port management | Already on Ubuntu, simpler than iptables |
| systemd | Docker auto-start | Ensure containers restart on reboot |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Ubuntu 22.04 | Amazon Linux 2023 | AL2023 uses dnf, smaller community for Docker troubleshooting |
| ufw | AWS Security Group only | Security group is primary; ufw is defense-in-depth |
| appleboy/ssh-action | Self-hosted runner | SSH action already works, simpler for single server |

## Architecture Patterns

### Recommended File Structure
```
scripts/
  setup-server.sh       # One-time EC2 provisioning (Docker, swap, clone)
  deploy.sh             # Called by CI: write secrets, compose up, health check
  generate_keys.sh      # Existing: RSA key pair generation
services/
  auth/app/services/
    seed_guests.py       # NEW: Demo guest account seeding
```

### Pattern 1: Server Setup Script (One-Time Provisioning)
**What:** Idempotent bash script that provisions a fresh Ubuntu EC2 instance.
**When to use:** First-time setup or reprovisioning.
**Key steps:**
1. System update and essential packages
2. Docker CE installation (official apt repository method)
3. Add ec2 user to docker group
4. Enable Docker systemd service
5. Create 2GB swap file
6. Clone repository to /opt/hotelbook
7. Create keys/ directory with correct permissions

```bash
#!/bin/bash
set -euo pipefail

# Update system
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl git

# Install Docker CE (official method)
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Enable Docker on boot
sudo systemctl enable docker

# Create 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Clone repo
sudo mkdir -p /opt/hotelbook
sudo chown $USER:$USER /opt/hotelbook
git clone https://github.com/OWNER/REPO.git /opt/hotelbook

# Create keys directory
mkdir -p /opt/hotelbook/keys
chmod 700 /opt/hotelbook/keys
```

### Pattern 2: Secrets Management via CI Deploy
**What:** CI deploy job writes GitHub Secrets to server files before docker compose up.
**When to use:** Every deployment.
**Critical detail:** The docker-compose.yml hardcodes dev passwords inline (e.g., `POSTGRES_PASSWORD: auth_pass`). For production, a `.env` file is needed to override these via `docker-compose.prod.yml` environment variable interpolation.

The current `docker-compose.prod.yml` only overrides `ADMIN_EMAIL` and `ADMIN_PASSWORD` via `${VAR:-default}` syntax. A new `docker-compose.deploy.yml` overlay is needed to parameterize ALL credentials:

```yaml
# docker-compose.deploy.yml -- production credential overrides
services:
  auth_db:
    environment:
      POSTGRES_PASSWORD: ${AUTH_DB_PASSWORD}
  room_db:
    environment:
      POSTGRES_PASSWORD: ${ROOM_DB_PASSWORD}
  booking_db:
    environment:
      POSTGRES_PASSWORD: ${BOOKING_DB_PASSWORD}
  rabbitmq:
    environment:
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASS}
  auth:
    environment:
      DATABASE_URL: postgresql+asyncpg://auth_user:${AUTH_DB_PASSWORD}@auth_db:5432/auth
      RABBITMQ_URL: amqp://hotel:${RABBITMQ_PASS}@rabbitmq:5672/
  room:
    environment:
      DATABASE_URL: postgresql+asyncpg://room_user:${ROOM_DB_PASSWORD}@room_db:5432/rooms
      RABBITMQ_URL: amqp://hotel:${RABBITMQ_PASS}@rabbitmq:5672/
  booking:
    environment:
      DATABASE_URL: postgresql+asyncpg://booking_user:${BOOKING_DB_PASSWORD}@booking_db:5432/bookings
      RABBITMQ_URL: amqp://hotel:${RABBITMQ_PASS}@rabbitmq:5672/
  nginx:
    ports:
      - "80:80"
    # Remove 443 port (HTTP only)
```

The CI deploy job writes a `.env` file on the server, then runs:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.deploy.yml up -d --build
```

### Pattern 3: Guest Account Seeding
**What:** Auth service seeds demo guest accounts on startup.
**When to use:** Demo/test deployments.
**Design:** Follow the existing pattern in room service (`seed_data` function, idempotent, check-if-exists-first). The seed function creates 5-10 guest accounts with known credentials via the same `register_user` path or direct DB insertion matching the existing User model.

Important: The seed_bookings.py generates random `user_id` UUIDs that don't correspond to real auth accounts. For the demo to be fully functional (guests can log in and see "their" bookings), the guest seed should either:
- Option A: Create guest accounts with known emails, but bookings remain with random user_ids (simpler, dashboard still looks good)
- Option B: Wire guest account UUIDs into the booking seed (complex cross-service coordination)

**Recommendation:** Option A -- create standalone guest accounts for login demonstration. The booking seed data already makes the staff dashboard impressive. Guest accounts let someone log in and navigate the guest UI. Their "My Bookings" page will be empty, which is fine for a demo (they can create new bookings).

### Pattern 4: Health Check After Deploy
**What:** CI deploy job verifies the stack is healthy after deployment.
**Gateway already has:** `GET /health` returning `{"status": "ok", "service": "gateway"}`
**Nginx already proxies:** `/health` to gateway.

The deploy script should poll the health endpoint after `docker compose up`:
```bash
echo "Waiting for stack to be healthy..."
for i in $(seq 1 30); do
  if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "Stack is healthy!"
    exit 0
  fi
  sleep 10
done
echo "Health check failed after 5 minutes"
exit 1
```

### Anti-Patterns to Avoid
- **Storing production secrets in git:** Never commit .env with real passwords. The .env is written by CI at deploy time.
- **Using docker compose without --remove-orphans:** Leftover containers from removed services cause port conflicts.
- **Hardcoding server IP in code:** Use relative API URLs (already done -- both frontends default VITE_API_URL to empty string).
- **Running docker compose as root:** Add ec2 user to docker group instead.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Docker installation | Manual apt install | Docker's official convenience script or apt repo | GPG keys, repos change; official method stays current |
| SSH deployment | Custom SSH scripts | appleboy/ssh-action@v1 | Already working in CI, handles key management |
| Process management | Custom restart scripts | Docker Compose restart: always + systemd docker.service | Survives reboots, handles crashes |
| Reverse proxy | Custom routing | nginx (already configured) | Already handles /api/, /staff/, / routing |
| SSL/TLS | Anything | SKIP for now | Explicit user decision: HTTP only |

## Common Pitfalls

### Pitfall 1: Memory Pressure on t3.small
**What goes wrong:** 2GB RAM with 11+ containers (3 Postgres, RabbitMQ, Minio, 4 app services, 2 frontends, nginx) causes OOM kills.
**Why it happens:** PostgreSQL alone can consume 100-200MB per instance. Docker build phase is especially memory-hungry.
**How to avoid:** Create 2GB swap file BEFORE first docker compose build. Set `--build` only when needed. Consider `docker system prune -f` after builds.
**Warning signs:** Containers restarting in loops, `dmesg | grep oom`.

### Pitfall 2: Docker Compose File Ordering
**What goes wrong:** Environment variables in base compose override those in overlay files.
**Why it happens:** Docker Compose merges environment blocks; later files override earlier ones. But `POSTGRES_PASSWORD: auth_pass` in base compose is a literal, not a variable. The deploy overlay MUST re-declare environment vars to override.
**How to avoid:** The deploy overlay must explicitly set `POSTGRES_PASSWORD: ${AUTH_DB_PASSWORD}` to override the hardcoded `auth_pass` in base.

### Pitfall 3: JWT Key Newlines in GitHub Secrets
**What goes wrong:** RSA keys pasted into GitHub Secrets lose their newline formatting, causing "could not deserialize key data" errors.
**Why it happens:** GitHub Secrets UI may strip trailing newlines or add extra whitespace.
**How to avoid:** Base64-encode keys before storing in GitHub Secrets. Deploy script decodes:
```bash
echo "$JWT_PRIVATE_KEY" | base64 -d > /opt/hotelbook/keys/jwt_private_key
echo "$JWT_PUBLIC_KEY" | base64 -d > /opt/hotelbook/keys/jwt_public_key
chmod 600 /opt/hotelbook/keys/jwt_private_key
```

### Pitfall 4: Booking Seed Depends on Room Service
**What goes wrong:** Booking seed runs but room service isn't ready yet, so seed fails silently.
**Why it happens:** `seed_historical_bookings` fetches room types from room service API. If room service is still starting, the HTTP call fails.
**How to avoid:** The existing code already handles this gracefully (try/except with warning log). The booking service `restart: always` in prod means it will restart and retry. The room seed runs synchronously on startup and is fast, so typically room service is ready before booking service starts seeding.

### Pitfall 5: Port 443 in docker-compose.prod.yml
**What goes wrong:** Nginx tries to listen on 443 but there's no SSL cert, causing startup failure.
**Why it happens:** The prod overlay currently maps both 80 and 443.
**How to avoid:** The deploy overlay should override nginx ports to only expose 80. Or remove 443 from the prod overlay.

### Pitfall 6: First Deploy Requires Manual git clone
**What goes wrong:** CI deploy job runs `cd /opt/hotelbook && git pull` but directory doesn't exist yet.
**Why it happens:** Setup script must run first to clone the repo.
**How to avoid:** Document the one-time setup process clearly. Setup script creates /opt/hotelbook with git clone.

## Code Examples

### Existing CI Deploy Job (current state)
```yaml
# Source: .github/workflows/ci.yml lines 174-190
deploy:
  runs-on: ubuntu-latest
  needs: build
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  steps:
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v1
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ${{ secrets.EC2_USER }}
        key: ${{ secrets.EC2_SSH_KEY }}
        script: |
          cd /opt/hotelbook
          git pull origin main
          docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --remove-orphans
          docker system prune -f
```

### Enhanced CI Deploy Job (needed)
```yaml
deploy:
  runs-on: ubuntu-latest
  needs: build
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  steps:
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v1
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ${{ secrets.EC2_USER }}
        key: ${{ secrets.EC2_SSH_KEY }}
        envs: JWT_PRIVATE_KEY,JWT_PUBLIC_KEY,AUTH_DB_PASSWORD,ROOM_DB_PASSWORD,BOOKING_DB_PASSWORD,RABBITMQ_PASS,ADMIN_EMAIL,ADMIN_PASSWORD
        script: |
          cd /opt/hotelbook
          git pull origin main

          # Write JWT keys (base64 decoded)
          echo "$JWT_PRIVATE_KEY" | base64 -d > keys/jwt_private_key
          echo "$JWT_PUBLIC_KEY" | base64 -d > keys/jwt_public_key
          chmod 600 keys/jwt_private_key
          chmod 644 keys/jwt_public_key

          # Write .env for docker compose interpolation
          cat > .env << ENVEOF
          AUTH_DB_PASSWORD=$AUTH_DB_PASSWORD
          ROOM_DB_PASSWORD=$ROOM_DB_PASSWORD
          BOOKING_DB_PASSWORD=$BOOKING_DB_PASSWORD
          RABBITMQ_PASS=$RABBITMQ_PASS
          ADMIN_EMAIL=$ADMIN_EMAIL
          ADMIN_PASSWORD=$ADMIN_PASSWORD
          ENVEOF

          # Deploy
          docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.deploy.yml up -d --build --remove-orphans
          docker system prune -f

          # Health check
          for i in $(seq 1 30); do
            if curl -sf http://localhost/health; then
              echo "Healthy!"
              exit 0
            fi
            sleep 10
          done
          echo "Health check failed"
          exit 1
```

### Existing docker-compose.prod.yml nginx section
```yaml
# Source: docker-compose.prod.yml
nginx:
  image: nginx:stable-alpine
  ports:
    - "80:80"
    - "443:443"   # MUST be removed for HTTP-only
  volumes:
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
    - letsencrypt_data:/etc/letsencrypt:ro  # MUST be removed
```

### Frontend API URL Configuration
```typescript
// Source: frontend/src/api/client.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  // Defaults to '' which means relative URLs -- works with nginx proxy
});
```
No build-time configuration needed. Nginx handles routing.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Docker Compose v1 standalone | Docker Compose v2 plugin | 2023 | Use `docker compose` not `docker-compose` |
| Docker install.sh convenience script | Official apt repository method | 2024 | More reliable, supports pinning versions |
| Manual SSH deploy | appleboy/ssh-action with envs parameter | Already in CI | Passes env vars to remote script securely |

## Open Questions

1. **GitHub repository URL for git clone**
   - What we know: Setup script needs to clone the repo
   - What's unclear: The exact GitHub repo URL (OWNER/REPO)
   - Recommendation: Use a placeholder in setup script, document that user must fill it in

2. **EC2 instance creation method**
   - What we know: User has AWS account, wants t3.small in us-east-1
   - What's unclear: Whether to script EC2 creation (AWS CLI/Terraform) or document manual console steps
   - Recommendation: Document manual AWS Console steps (simpler for single instance), provide setup script for post-launch provisioning

3. **MinIO in production**
   - What we know: MinIO is used for photo storage in dev
   - What's unclear: Whether MinIO should run in production or if photos use external URLs
   - Recommendation: Keep MinIO -- the room seed uses Unsplash URLs directly in photo_urls, MinIO is only for staff uploads. Include it in prod stack.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual + CI health check |
| Config file | .github/workflows/ci.yml |
| Quick run command | `curl -sf http://EC2_IP/health` |
| Full suite command | `curl -sf http://EC2_IP/health && curl -sf http://EC2_IP/ && curl -sf http://EC2_IP/staff/ && curl -sf http://EC2_IP/api/v1/rooms/types/` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DEPLOY-01 | EC2 with Docker, swap, setup script | manual | `ssh EC2 "docker --version && swapon --show"` | N/A -- manual verification |
| DEPLOY-02 | Secrets from GitHub, not in repo | manual + CI | `grep -r "AUTH_DB_PASSWORD" .env` should not exist in repo | N/A |
| DEPLOY-03 | Demo guest accounts and bookings seeded | smoke | `curl http://EC2_IP/api/v1/rooms/types/` returns room types | Wave 0 |
| DEPLOY-04 | Full stack on HTTP with health check | smoke | `curl -sf http://EC2_IP/health` | Added to CI deploy job |

### Sampling Rate
- **Per task commit:** Verify scripts have correct syntax with `bash -n script.sh`
- **Per wave merge:** Full CI pipeline passes
- **Phase gate:** Stack accessible at EC2 IP, all routes return 200

### Wave 0 Gaps
- [ ] Health check verification in CI deploy job -- needs adding to deploy step
- [ ] Guest account seed function -- `services/auth/app/services/seed_guests.py` does not exist yet
- [ ] `docker-compose.deploy.yml` -- production credential override layer does not exist yet

## Sources

### Primary (HIGH confidence)
- Project codebase: docker-compose.yml, docker-compose.prod.yml, ci.yml, nginx config, seed scripts -- direct inspection
- Docker Compose file merge behavior -- well-established Docker documentation

### Secondary (MEDIUM confidence)
- Ubuntu 22.04 Docker CE installation -- official Docker docs method (stable, widely documented)
- appleboy/ssh-action envs parameter -- used in existing CI, GitHub Actions marketplace

### Tertiary (LOW confidence)
- t3.small memory behavior with 11+ containers -- based on general AWS experience, actual memory pressure depends on workload

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all tools already in project, just needs production configuration
- Architecture: HIGH -- existing infrastructure covers 80% of needs, gaps clearly identified
- Pitfalls: HIGH -- common deployment issues well-documented, verified against actual codebase
- Seed data: HIGH -- existing seed patterns inspected, gap (guest accounts) clearly scoped

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable infrastructure, no fast-moving dependencies)
