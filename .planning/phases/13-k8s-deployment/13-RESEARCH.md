# Phase 13: k8s Deployment - Research

**Researched:** 2026-03-23
**Domain:** Kubernetes (k3s), Helm charts, Traefik IngressRoute, CI/CD with GHCR
**Confidence:** HIGH

## Summary

This phase migrates HotelBook's production deployment from Docker Compose on EC2 to Kubernetes via k3s on the same EC2 t3.medium (4 GB RAM). The approach uses Helm umbrella charts for manifest management, Traefik (bundled with k3s) for ingress routing, and GitHub Container Registry (ghcr.io) for image storage. The CI/CD pipeline shifts from SSH-based `docker compose up` to building/pushing images to GHCR and deploying via `helm upgrade` over SSH.

The tightest constraint is the 4 GB RAM budget. k3s itself consumes approximately 500-600 MB at idle (server mode with embedded SQLite). Traefik adds ~30-50 MB. That leaves roughly 3.0-3.4 GB for application workloads. Consolidating 4 Postgres instances into 1 is critical for staying within budget.

**Primary recommendation:** Use k3s with embedded SQLite (not etcd) to minimize memory overhead, a single Helm umbrella chart with per-service templates, Traefik IngressRoute CRDs for path routing, and a single namespace for simplicity on a single-node cluster.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- k3s on the existing EC2 t3.medium (4GB RAM) instance
- k8s runs alongside Docker Compose -- Compose stays for local dev, k8s is the production deployment
- CI/CD (GitHub Actions) updated to deploy to k8s instead of Docker Compose
- Resource constraints are tight at 4GB -- resource limits/requests must be set on all pods
- Helm charts -- single umbrella chart (hotelbook/) with all services as templates
- Separate values files: values.yaml (defaults), values-dev.yaml, values-prod.yaml
- Container images pushed to GitHub Container Registry (ghcr.io)
- CI builds images, pushes to ghcr.io, then deploys to k3s via helm upgrade
- Consolidate 4 Postgres instances into 1 Postgres StatefulSet with 4 databases inside (auth, rooms, bookings, chat)
- Services keep separate database names and credentials -- logical isolation, shared instance
- RabbitMQ as single-replica StatefulSet with PVC
- MinIO as single-replica StatefulSet with PVC
- Mailpit included in dev values only, not deployed in prod
- Traefik (k3s built-in) as ingress controller -- no separate nginx container
- Traefik IngressRoute CRDs for path-based routing: / -> guest frontend, /staff/ -> staff frontend, /api/ -> gateway
- IP-based access (no domain, no TLS) -- matches current EC2 setup
- K8s Secrets created/updated by CI/CD via kubectl (source of truth remains GitHub Secrets)

### Claude's Discretion
- Exact resource limits/requests per pod (within 4GB total constraint)
- k3s installation method and version
- Helm chart directory structure and template organization
- Health check / readiness probe configuration
- Namespace strategy (single namespace vs per-concern)
- Rolling update strategy configuration
- Init container patterns for database migrations

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

## Standard Stack

### Core
| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| k3s | v1.32.x (stable channel) | Lightweight Kubernetes distribution | Ships with Traefik v3, SQLite default datastore, minimal memory overhead (~500 MB) |
| Helm | v3.x (latest) | Kubernetes package manager | Standard for templated manifests; umbrella chart pattern well-supported |
| Traefik | v3.3.x (bundled with k3s v1.32) | Ingress controller | Built into k3s, IngressRoute CRD for path-based routing, no extra install |
| GHCR (ghcr.io) | N/A | Container image registry | Free for public repos, integrated with GitHub Actions auth via GITHUB_TOKEN |

### Supporting
| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| docker/login-action | v3 | GHCR authentication in CI | Every CI build that pushes images |
| docker/build-push-action | v6 | Build and push Docker images | Every CI build step |
| kubectl | Matches k3s version | Direct cluster commands | Secret creation, debugging, one-off operations |
| postgres:16-alpine | 16.x | Database (single instance, 4 DBs) | StatefulSet with init script for multi-DB setup |
| rabbitmq:3-management-alpine | 3.x | Message queue | StatefulSet with PVC |
| minio/minio | RELEASE.2025-09-07 | Object storage | StatefulSet with PVC |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| k3s SQLite | k3s etcd | etcd uses ~200 MB more RAM; unnecessary for single-node |
| Helm umbrella | Kustomize | Kustomize is simpler but lacks values-file overrides and dependency management |
| Traefik IngressRoute CRD | Standard k8s Ingress | IngressRoute is more expressive (SSE support, middleware chains); already bundled |
| Single namespace | Multi-namespace | Multi-namespace adds RBAC complexity with no benefit on single-node |

### Installation

k3s on EC2:
```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL=stable sh -
```

Helm on EC2:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Kubeconfig:
```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
# Or copy to ~/.kube/config with correct permissions
```

## Architecture Patterns

### Recommended Helm Chart Structure
```
helm/hotelbook/
├── Chart.yaml                  # Umbrella chart metadata
├── values.yaml                 # Default values (shared)
├── values-dev.yaml             # Dev overrides (mailpit enabled, lower resources)
├── values-prod.yaml            # Prod overrides (real passwords, higher resources)
├── templates/
│   ├── _helpers.tpl            # Shared template helpers (labels, names)
│   ├── namespace.yaml          # Namespace definition
│   ├── NOTES.txt               # Post-install instructions
│   │
│   ├── # --- Stateful infrastructure ---
│   ├── postgres-statefulset.yaml
│   ├── postgres-service.yaml
│   ├── postgres-configmap.yaml # Init SQL for creating 4 databases + users
│   ├── postgres-pvc.yaml
│   ├── rabbitmq-statefulset.yaml
│   ├── rabbitmq-service.yaml
│   ├── rabbitmq-pvc.yaml
│   ├── minio-statefulset.yaml
│   ├── minio-service.yaml
│   ├── minio-pvc.yaml
│   │
│   ├── # --- Application services ---
│   ├── auth-deployment.yaml
│   ├── auth-service.yaml
│   ├── room-deployment.yaml
│   ├── room-service.yaml
│   ├── booking-deployment.yaml
│   ├── booking-service.yaml
│   ├── chat-deployment.yaml
│   ├── chat-service.yaml
│   ├── mcp-server-deployment.yaml
│   ├── mcp-server-service.yaml
│   ├── gateway-deployment.yaml
│   ├── gateway-service.yaml
│   │
│   ├── # --- Frontend ---
│   ├── frontend-guest-deployment.yaml
│   ├── frontend-guest-service.yaml
│   ├── frontend-staff-deployment.yaml
│   ├── frontend-staff-service.yaml
│   │
│   ├── # --- Ingress ---
│   ├── ingressroute.yaml       # Traefik IngressRoute CRD
│   │
│   ├── # --- Secrets & Config ---
│   ├── secrets.yaml            # Placeholder (actual values from CI/CD kubectl)
│   ├── configmap.yaml          # Non-sensitive config
│   │
│   └── # --- Optional ---
│   └── mailpit-deployment.yaml # Conditional on .Values.mailpit.enabled
```

### Pattern 1: Postgres Multi-Database Init Container
**What:** Single Postgres StatefulSet with an init SQL script that creates all 4 databases and users.
**When to use:** Consolidating multiple Postgres instances into one (saves ~300 MB RAM per eliminated instance).
**Example:**
```yaml
# postgres-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-init
data:
  init-databases.sql: |
    -- Create additional databases (default DB created by POSTGRES_DB env)
    CREATE DATABASE rooms;
    CREATE DATABASE bookings;
    CREATE DATABASE chat;

    -- Create users with passwords (set via env/secrets)
    CREATE USER room_user WITH PASSWORD '${ROOM_DB_PASSWORD}';
    CREATE USER booking_user WITH PASSWORD '${BOOKING_DB_PASSWORD}';
    CREATE USER chat_user WITH PASSWORD '${CHAT_DB_PASSWORD}';

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE auth TO auth_user;
    GRANT ALL PRIVILEGES ON DATABASE rooms TO room_user;
    GRANT ALL PRIVILEGES ON DATABASE bookings TO booking_user;
    GRANT ALL PRIVILEGES ON DATABASE chat TO chat_user;
```

Note: The postgres:16-alpine image runs `.sql` files from `/docker-entrypoint-initdb.d/` on first start. Mount the ConfigMap there. For password templating, use a shell init script (`.sh`) instead that reads from environment variables.

### Pattern 2: Traefik IngressRoute for Path-Based Routing
**What:** Replace nginx reverse proxy with Traefik IngressRoute CRDs for path routing.
**When to use:** All ingress routing in k3s.
**Example:**
```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: hotelbook
spec:
  entryPoints:
    - web        # Port 80 (Traefik default)
  routes:
    # SSE endpoint for chat streaming (highest priority - longest match)
    - match: PathPrefix(`/api/v1/chat/send`)
      kind: Rule
      services:
        - name: gateway
          port: 8000
      middlewares:
        - name: sse-headers

    # API routes
    - match: PathPrefix(`/api`) || PathPrefix(`/docs`) || PathPrefix(`/openapi.json`) || PathPrefix(`/health`)
      kind: Rule
      services:
        - name: gateway
          port: 8000

    # Staff frontend (must match before guest catch-all)
    - match: PathPrefix(`/staff`)
      kind: Rule
      services:
        - name: frontend-staff
          port: 80
      middlewares:
        - name: strip-staff-prefix

    # Guest frontend (catch-all)
    - match: PathPrefix(`/`)
      kind: Rule
      services:
        - name: frontend-guest
          port: 80
```

### Pattern 3: StripPrefix Middleware for Staff Frontend
**What:** Strip `/staff` prefix so the staff frontend container receives requests at `/`.
**When to use:** The staff frontend nginx container expects requests at `/`, but Traefik routes `/staff/*` to it.
**Example:**
```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: strip-staff-prefix
spec:
  stripPrefix:
    prefixes:
      - /staff
```

**Important:** The frontend containers already have their own nginx with `try_files $uri $uri/ /index.html` for SPA routing. Traefik only needs to proxy to them -- it does not need to replicate try_files behavior.

### Pattern 4: SSE Middleware for Chat Streaming
**What:** Disable buffering for Server-Sent Events endpoints.
**When to use:** The chat streaming endpoint at `/api/v1/chat/send`.
**Example:**
```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: sse-headers
spec:
  headers:
    customResponseHeaders:
      X-Accel-Buffering: "no"
```

Note: Traefik v3 handles SSE passthrough well by default, but explicitly disabling buffering via middleware ensures no proxy-layer buffering interferes with streaming.

### Pattern 5: Service-to-Service DNS
**What:** k8s Service names match existing Docker Compose service names for seamless migration.
**When to use:** All inter-service communication.
**Example:**
```yaml
# Service names must match what services expect in their environment variables
apiVersion: v1
kind: Service
metadata:
  name: auth       # Matches http://auth:8000 in compose
spec:
  selector:
    app: auth
  ports:
    - port: 8000
      targetPort: 8000
```

Current compose service URLs (`http://auth:8000`, `http://room:8000`, etc.) map directly to k8s Service DNS (`auth.default.svc.cluster.local:8000`). No application code changes needed.

### Pattern 6: Init Container for Database Migrations
**What:** Run Alembic migrations before the main container starts.
**When to use:** Services with database migrations (auth, room, booking, chat).
**Example:**
```yaml
initContainers:
  - name: migrate
    image: "{{ .Values.images.auth.repository }}:{{ .Values.images.auth.tag }}"
    command: ["alembic", "upgrade", "head"]
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: db-credentials
            key: auth-database-url
```

### Anti-Patterns to Avoid
- **Separate namespace per service:** Adds unnecessary RBAC complexity on a single-node cluster. Use a single `hotelbook` namespace.
- **HPA (Horizontal Pod Autoscaler):** On a 4 GB node, autoscaling will just cause OOM kills. Fix replicas to 1 for all pods.
- **emptyDir for database storage:** Data loss on pod restart. Always use PersistentVolumeClaims with k3s local-path provisioner.
- **Latest tag for images:** Use Git SHA tags for traceability. `ghcr.io/owner/hotelbook-auth:sha-abc1234`.
- **Storing secrets in values files:** Secrets must come from CI/CD via `kubectl create secret`. Values files should reference secret names, not contain secret values.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Ingress routing | Custom nginx k8s configs | Traefik IngressRoute CRD (bundled) | Already installed, native CRD, SSE support |
| Secret management | Templated secret values | kubectl create secret from CI/CD | Source of truth stays in GitHub Secrets |
| Storage provisioning | Manual PV creation | k3s local-path provisioner (bundled) | Automatic PV provisioning from PVC claims |
| Service discovery | Custom DNS/hosts | k8s Service DNS | Built-in, zero config, matches compose names |
| Container registry | Self-hosted registry | ghcr.io | Free, integrated with GitHub Actions GITHUB_TOKEN |
| Process supervision | systemd units for services | k8s Deployments with restart policy | Automatic restart, health checks, rolling updates |
| Load balancing | iptables rules | k3s ServiceLB (bundled) | Handles port 80/443 binding on node |

**Key insight:** k3s bundles Traefik, ServiceLB, local-path provisioner, and CoreDNS. Leveraging these bundled components avoids installing additional software and keeps memory usage low.

## Common Pitfalls

### Pitfall 1: Memory Exhaustion on 4 GB Node
**What goes wrong:** k3s + all application pods exceed 4 GB, triggering OOM killer which takes down random pods (including k3s components).
**Why it happens:** No resource limits set, or limits set too generously.
**How to avoid:** Set explicit resource requests AND limits on every pod. Budget:
- k3s system: ~600 MB reserved
- Postgres: ~512 MB limit
- RabbitMQ: ~256 MB limit
- MinIO: ~256 MB limit
- Each backend service (auth, room, booking, chat, mcp-server, gateway): ~128 MB limit each = 768 MB
- Each frontend (guest, staff): ~64 MB limit each = 128 MB
- Traefik: ~64 MB (managed by k3s)
- Total estimated: ~2,584 MB, leaving ~1,400 MB headroom for spikes
**Warning signs:** Pods in `OOMKilled` status, `kubectl top nodes` showing >85% memory usage.

### Pitfall 2: Postgres Init Script Only Runs on Fresh Volume
**What goes wrong:** The `/docker-entrypoint-initdb.d/` scripts only execute when the data directory is empty (first startup). If you change the init SQL, it won't re-run.
**Why it happens:** Standard Postgres Docker image behavior.
**How to avoid:** For changes after initial setup, use Alembic migrations or manual `kubectl exec` into the Postgres pod. Keep init script idempotent with `CREATE DATABASE IF NOT EXISTS` (or use `\gexec` pattern since Postgres doesn't support IF NOT EXISTS for CREATE DATABASE directly).
**Warning signs:** New databases/users not appearing after pod restart.

### Pitfall 3: Staff Frontend Path Routing
**What goes wrong:** Staff frontend SPA routing breaks -- deep links like `/staff/reservations` return 404.
**Why it happens:** Traefik strips `/staff` prefix and forwards to the frontend container, but the frontend nginx `try_files` correctly falls back to `index.html`. However, the React app's router must be configured with `basename="/staff"` so it recognizes routes correctly.
**How to avoid:** Two changes needed: (1) Traefik StripPrefix middleware removes `/staff`, (2) Staff frontend Vite build uses `base: '/staff/'` in vite.config.ts, and React Router uses `basename="/staff"`. The nginx in the frontend container handles the SPA fallback.
**Warning signs:** Staff frontend loads but navigation shows blank pages or 404s.

### Pitfall 4: Image Pull Authentication
**What goes wrong:** k3s cannot pull images from ghcr.io because it lacks authentication credentials.
**Why it happens:** GHCR images for private repos require authentication. Even public repos may have rate limits.
**How to avoid:** Create an imagePullSecret in the namespace using a GitHub Personal Access Token (or GITHUB_TOKEN for public repos). Reference it in pod specs or attach to the default service account.
**Warning signs:** Pods stuck in `ImagePullBackOff` with "unauthorized" errors.

### Pitfall 5: PVC Storage with local-path Provisioner
**What goes wrong:** Data lost when node is replaced (not just rebooted).
**Why it happens:** local-path provisioner stores data on the node's filesystem, not on EBS.
**How to avoid:** For this project (single EC2, not HA), local-path is acceptable. If durability matters, use an EBS-backed StorageClass instead. Document that this is a conscious tradeoff.
**Warning signs:** After node termination, StatefulSet pods start with empty databases.

### Pitfall 6: Traefik SSE Buffering
**What goes wrong:** Chat streaming responses arrive in chunks instead of streaming, or hang entirely.
**Why it happens:** Traefik may buffer responses by default.
**How to avoid:** Add explicit middleware to disable buffering for the SSE endpoint. Use `X-Accel-Buffering: no` header. Also ensure the IngressRoute for `/api/v1/chat/send` is a separate, higher-priority rule.
**Warning signs:** Chat responses appear all at once after a delay instead of streaming token-by-token.

### Pitfall 7: CI/CD Kubeconfig Security
**What goes wrong:** Kubeconfig with cluster-admin credentials leaks or is stored insecurely.
**Why it happens:** k3s kubeconfig at `/etc/rancher/k3s/k3s.yaml` has full admin access.
**How to avoid:** Store kubeconfig as a GitHub Secret (base64 encoded). In CI, decode and write to a temp file. Use `kubectl --kubeconfig` or set KUBECONFIG env var. Alternatively, continue SSH-based deployment (SSH into EC2 and run helm upgrade locally).
**Warning signs:** Anyone with the secret can control the entire cluster.

## Code Examples

### GitHub Actions: Build and Push to GHCR
```yaml
# .github/workflows/ci.yml (build job)
build-and-push:
  runs-on: ubuntu-latest
  needs: e2e-tests
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  permissions:
    packages: write
    contents: read
  strategy:
    matrix:
      service:
        - { name: auth, context: ".", dockerfile: services/auth/Dockerfile }
        - { name: room, context: ".", dockerfile: services/room/Dockerfile }
        - { name: booking, context: ".", dockerfile: services/booking/Dockerfile }
        - { name: chat, context: ".", dockerfile: services/chat/Dockerfile }
        - { name: mcp-server, context: ".", dockerfile: services/mcp-server/Dockerfile }
        - { name: gateway, context: ".", dockerfile: services/gateway/Dockerfile }
        - { name: frontend-guest, context: ./frontend, dockerfile: frontend/Dockerfile }
        - { name: frontend-staff, context: ./frontend-staff, dockerfile: frontend-staff/Dockerfile }
  steps:
    - uses: actions/checkout@v4

    - uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - uses: docker/build-push-action@v6
      with:
        context: ${{ matrix.service.context }}
        file: ${{ matrix.service.dockerfile }}
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/hotelbook-${{ matrix.service.name }}:${{ github.sha }}
          ghcr.io/${{ github.repository_owner }}/hotelbook-${{ matrix.service.name }}:latest
```

### GitHub Actions: Deploy via SSH + Helm
```yaml
deploy:
  runs-on: ubuntu-latest
  needs: build-and-push
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  steps:
    - uses: actions/checkout@v4

    - name: Deploy to k3s
      uses: appleboy/ssh-action@v1
      env:
        IMAGE_TAG: ${{ github.sha }}
        AUTH_DB_PASSWORD: ${{ secrets.AUTH_DB_PASSWORD }}
        ROOM_DB_PASSWORD: ${{ secrets.ROOM_DB_PASSWORD }}
        BOOKING_DB_PASSWORD: ${{ secrets.BOOKING_DB_PASSWORD }}
        RABBITMQ_PASS: ${{ secrets.RABBITMQ_PASS }}
        ADMIN_EMAIL: ${{ secrets.ADMIN_EMAIL }}
        ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
        JWT_PRIVATE_KEY: ${{ secrets.JWT_PRIVATE_KEY }}
        JWT_PUBLIC_KEY: ${{ secrets.JWT_PUBLIC_KEY }}
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ${{ secrets.EC2_USER }}
        key: ${{ secrets.EC2_SSH_KEY }}
        envs: IMAGE_TAG,AUTH_DB_PASSWORD,ROOM_DB_PASSWORD,BOOKING_DB_PASSWORD,RABBITMQ_PASS,ADMIN_EMAIL,ADMIN_PASSWORD,JWT_PRIVATE_KEY,JWT_PUBLIC_KEY
        script: |
          cd /opt/hotelbook
          git pull origin main

          # Create/update k8s secrets
          kubectl create secret generic db-credentials \
            --from-literal=auth-db-password="$AUTH_DB_PASSWORD" \
            --from-literal=room-db-password="$ROOM_DB_PASSWORD" \
            --from-literal=booking-db-password="$BOOKING_DB_PASSWORD" \
            --from-literal=rabbitmq-password="$RABBITMQ_PASS" \
            --from-literal=admin-email="$ADMIN_EMAIL" \
            --from-literal=admin-password="$ADMIN_PASSWORD" \
            --dry-run=client -o yaml | kubectl apply -f -

          # Create/update JWT key secrets
          kubectl create secret generic jwt-keys \
            --from-literal=private-key="$JWT_PRIVATE_KEY" \
            --from-literal=public-key="$JWT_PUBLIC_KEY" \
            --dry-run=client -o yaml | kubectl apply -f -

          # Deploy with Helm
          helm upgrade --install hotelbook ./helm/hotelbook \
            -f ./helm/hotelbook/values-prod.yaml \
            --set global.imageTag="$IMAGE_TAG"
```

### Postgres StatefulSet with Multi-DB Init
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: auth
            - name: POSTGRES_USER
              value: auth_user
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: auth-db-password
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
            - name: init-scripts
              mountPath: /docker-entrypoint-initdb.d
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            exec:
              command: ["pg_isready", "-U", "auth_user", "-d", "auth"]
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "auth_user", "-d", "auth"]
            initialDelaySeconds: 5
            periodSeconds: 5
      volumes:
        - name: init-scripts
          configMap:
            name: postgres-init
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 5Gi
```

### Backend Service Deployment Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.auth.name | default "auth" }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: auth
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  template:
    metadata:
      labels:
        app: auth
    spec:
      initContainers:
        - name: migrate
          image: "ghcr.io/{{ .Values.global.owner }}/hotelbook-auth:{{ .Values.global.imageTag }}"
          command: ["alembic", "upgrade", "head"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: auth-database-url
      containers:
        - name: auth
          image: "ghcr.io/{{ .Values.global.owner }}/hotelbook-auth:{{ .Values.global.imageTag }}"
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              value: "postgresql+asyncpg://auth_user:$(AUTH_DB_PASSWORD)@postgres:5432/auth"
            - name: JWT_PRIVATE_KEY_PATH
              value: /run/secrets/jwt_private_key
            - name: JWT_PUBLIC_KEY_PATH
              value: /run/secrets/jwt_public_key
            - name: RABBITMQ_URL
              value: "amqp://hotel:$(RABBITMQ_PASS)@rabbitmq:5672/"
          volumeMounts:
            - name: jwt-keys
              mountPath: /run/secrets
              readOnly: true
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "128Mi"
              cpu: "250m"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
      volumes:
        - name: jwt-keys
          secret:
            secretName: jwt-keys
```

## Resource Budget (4 GB = 4096 MB)

| Component | Requests | Limits | Notes |
|-----------|----------|--------|-------|
| k3s system (reserved) | ~600 MB | -- | Server + Traefik + CoreDNS + ServiceLB |
| Postgres | 256 MB | 512 MB | Single instance, 4 databases |
| RabbitMQ | 128 MB | 256 MB | Single replica |
| MinIO | 128 MB | 256 MB | Single replica |
| Auth service | 64 MB | 128 MB | FastAPI + uvicorn |
| Room service | 64 MB | 128 MB | FastAPI + uvicorn |
| Booking service | 64 MB | 128 MB | FastAPI + uvicorn |
| Chat service | 64 MB | 128 MB | FastAPI + uvicorn |
| MCP server | 64 MB | 128 MB | FastAPI + uvicorn |
| Gateway | 64 MB | 128 MB | FastAPI + uvicorn |
| Frontend guest | 32 MB | 64 MB | nginx serving static files |
| Frontend staff | 32 MB | 64 MB | nginx serving static files |
| **Total requests** | **~1,560 MB** | | |
| **Total limits** | **~2,520 MB** | | |
| **Available headroom** | **~1,576 MB** | | For burst usage |

This budget is conservative. The key principle: requests should be what the pod normally uses, limits should be the maximum before OOM kill.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Traefik v2 IngressRoute | Traefik v3 IngressRoute | k3s v1.32 (2025) | API group changed from `traefik.containo.us/v1alpha1` to `traefik.io/v1alpha1` |
| docker/build-push-action v5 | docker/build-push-action v6 | 2025 | Improved caching, provenance attestation |
| GHCR classic PAT auth | GITHUB_TOKEN with packages:write | 2024 | No PAT needed for CI; use permissions block in workflow |

**Critical:** Use `traefik.io/v1alpha1` API group (not `traefik.containo.us/v1alpha1`) for IngressRoute CRDs on k3s v1.32+ with Traefik v3.

## Open Questions

1. **Frontend base path for staff frontend**
   - What we know: Staff frontend currently serves from `/staff/` via nginx proxy_pass with path stripping. Vite `base` config and React Router `basename` must match.
   - What's unclear: Whether the staff frontend already has `base: '/staff/'` configured in vite.config.ts, or if this is a new change needed for k8s.
   - Recommendation: Check vite.config.ts during implementation. If not set, add `base: '/staff/'` and rebuild.

2. **Entrypoint scripts and migrations**
   - What we know: Backend services use `entrypoint.sh` which likely runs migrations before starting uvicorn.
   - What's unclear: Whether to use init containers for migrations (k8s pattern) or keep existing entrypoint.sh behavior.
   - Recommendation: Keep existing entrypoint.sh as-is initially. Init containers are a refinement that can be added later if migration ordering matters.

3. **GHCR visibility (public vs private)**
   - What we know: Public GHCR packages don't need imagePullSecrets. Private ones do.
   - What's unclear: Whether the repo is public or private.
   - Recommendation: Plan for both -- include imagePullSecret creation in CI/CD, conditionally referenced in deployments.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual infrastructure validation (no unit tests for k8s manifests) |
| Config file | N/A |
| Quick run command | `helm template ./helm/hotelbook -f ./helm/hotelbook/values-prod.yaml` (dry-run render) |
| Full suite command | `helm upgrade --install hotelbook ./helm/hotelbook --dry-run --debug` (cluster dry-run) |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| K8S-01 | k3s cluster running | smoke | `kubectl get nodes` | N/A - infra |
| K8S-02 | All pods healthy | smoke | `kubectl get pods -n hotelbook` | N/A - infra |
| K8S-03 | Ingress routes working | smoke | `curl http://<EC2_IP>/health` | N/A - infra |
| K8S-04 | CI/CD deploys to k8s | integration | Push to main and observe | N/A - CI |
| K8S-05 | Data persists across restarts | smoke | `kubectl delete pod postgres-0 && kubectl exec ... psql` | N/A - infra |
| K8S-06 | Helm template renders | unit | `helm template ./helm/hotelbook` | Wave 0 |

### Sampling Rate
- **Per task commit:** `helm template ./helm/hotelbook` (validate YAML renders)
- **Per wave merge:** `helm upgrade --install --dry-run --debug` (validate against cluster)
- **Phase gate:** All pods Running, health endpoints responding, CI/CD successful deploy

### Wave 0 Gaps
- [ ] `helm/hotelbook/Chart.yaml` -- umbrella chart definition
- [ ] `helm/hotelbook/values.yaml` -- default values
- [ ] Helm installation on EC2 -- prerequisite for all validation

## Sources

### Primary (HIGH confidence)
- [K3s Requirements](https://docs.k3s.io/installation/requirements) -- Minimum hardware specs (2 CPU, 2 GB RAM for server)
- [K3s Resource Profiling](https://docs.k3s.io/reference/resource-profiling) -- Baseline ~600 MB idle, ~1.6 GB with standard workload
- [K3s Quick Start](https://docs.k3s.io/quick-start) -- Installation via `curl -sfL https://get.k3s.io | sh -`
- [Traefik IngressRoute CRD](https://doc.traefik.io/traefik/reference/routing-configuration/kubernetes/crd/http/ingressroute/) -- IngressRoute spec and path matching
- [Traefik StripPrefix Middleware](https://doc.traefik.io/traefik/middlewares/http/stripprefix/) -- Path prefix stripping for subpath routing
- [K3s Traefik v3 discussion](https://github.com/k3s-io/k3s/discussions/10679) -- k3s v1.32+ ships Traefik v3 (API group `traefik.io/v1alpha1`)

### Secondary (MEDIUM confidence)
- [Helm Umbrella Charts](https://oneuptime.com/blog/post/2026-01-17-helm-umbrella-charts-multi-service/view) -- Umbrella chart patterns for microservices
- [GitHub Actions Kubernetes Deploy](https://spacelift.io/blog/github-actions-kubernetes) -- CI/CD pipeline patterns with Helm + GHCR
- [K3s idle memory ~535 MB](https://github.com/k3s-io/k3s/discussions/3558) -- Community observation of idle memory consumption

### Tertiary (LOW confidence)
- Resource budget estimates -- Based on typical FastAPI/uvicorn memory footprint and Postgres defaults. Should be validated with actual `kubectl top` measurements after deployment.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - k3s, Helm, Traefik are well-documented; versions confirmed from official sources
- Architecture: HIGH - Helm umbrella chart pattern is well-established; IngressRoute CRD is official Traefik approach
- Pitfalls: HIGH - Memory constraints, init script behavior, and SPA routing issues are well-known k8s deployment challenges
- Resource budget: MEDIUM - Based on typical values, needs validation with real workload

**Research date:** 2026-03-23
**Valid until:** 2026-04-23 (stable infrastructure, 30-day validity)
