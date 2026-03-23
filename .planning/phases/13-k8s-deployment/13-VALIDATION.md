---
phase: 13
slug: k8s-deployment
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | kubectl + helm CLI validation (infrastructure phase) |
| **Config file** | k8s/hotelbook/Chart.yaml (Helm chart) |
| **Quick run command** | `helm template hotelbook k8s/hotelbook/ --values k8s/hotelbook/values-dev.yaml \| kubectl apply --dry-run=client -f -` |
| **Full suite command** | `helm template hotelbook k8s/hotelbook/ --values k8s/hotelbook/values-prod.yaml \| kubectl apply --dry-run=client -f -` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `helm template hotelbook k8s/hotelbook/ | kubectl apply --dry-run=client -f -`
- **After every plan wave:** Run full suite with prod values
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | K8S-CHART | template | `helm template hotelbook k8s/hotelbook/` | ❌ W0 | ⬜ pending |
| 13-01-02 | 01 | 1 | K8S-DB | template | `helm template hotelbook k8s/hotelbook/ \| grep StatefulSet` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 2 | K8S-DEPLOY | template | `helm template hotelbook k8s/hotelbook/ \| grep Deployment` | ❌ W0 | ⬜ pending |
| 13-02-02 | 02 | 2 | K8S-INGRESS | template | `helm template hotelbook k8s/hotelbook/ \| grep IngressRoute` | ❌ W0 | ⬜ pending |
| 13-03-01 | 03 | 3 | K8S-CICD | lint | `yamllint .github/workflows/ci.yml` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `k8s/hotelbook/Chart.yaml` — Helm chart definition
- [ ] `k8s/hotelbook/values.yaml` — Default values file
- [ ] Helm CLI available on dev machine for template validation

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| k3s cluster accessible | K8S-CLUSTER | Requires SSH to EC2 | SSH to EC2, run `kubectl get nodes` |
| Services respond via Traefik | K8S-INGRESS | Requires live cluster | curl EC2_IP:80/, /staff/, /api/health |
| CI/CD deploys successfully | K8S-CICD | Requires GitHub Actions run | Push to main, verify workflow passes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
