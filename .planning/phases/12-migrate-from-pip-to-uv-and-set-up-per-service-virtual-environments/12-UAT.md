---
status: complete
phase: 12-migrate-from-pip-to-uv-and-set-up-per-service-virtual-environments
source: 12-01-SUMMARY.md, 12-02-SUMMARY.md
started: 2026-03-23T03:00:00Z
updated: 2026-03-23T03:05:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Per-Service pyproject.toml Exists with Correct Dependencies
expected: Each of the 5 services has a `pyproject.toml` with correct dependencies and `[tool.uv.sources]` referencing `hotelbook-shared` as path dependency `../../shared`.
result: pass

### 2. Per-Service uv.lock Files Generated
expected: Each of the 5 services has a `uv.lock` file.
result: pass

### 3. Shared Package Importable from Service Venvs
expected: Running `cd services/gateway && uv run python -c "import shared"` succeeds without import errors.
result: pass

### 4. Gateway Tests Pass via uv
expected: Running `cd services/gateway && uv run pytest tests/ -x --tb=short` passes all gateway tests (8/8).
result: pass

### 5. Per-Service Test Directories Exist with Conftest
expected: Each of auth, room, booking, gateway has `services/{svc}/tests/conftest.py` with `from app` imports (no sys.path hacks).
result: pass

### 6. Old requirements.txt Files Have Deprecation Header
expected: Each service's `requirements.txt` and the root `requirements-dev.txt` start with a deprecation comment.
result: pass

### 7. Root pyproject.toml Stripped of Pytest Config
expected: Root `pyproject.toml` no longer has `[tool.pytest.ini_options]` section.
result: pass

### 8. Dockerfiles Use uv Instead of pip
expected: All 5 Dockerfiles contain `COPY --from=ghcr.io/astral-sh/uv` and `uv sync --frozen`. No `pip install` commands remain.
result: pass

### 9. CI Pipeline Uses setup-uv
expected: `.github/workflows/ci.yml` uses `astral-sh/setup-uv@v7`, `uv sync --frozen`, `uv run pytest`. No `pip install` or `actions/setup-python` remain.
result: pass

### 10. Makefile Has All Required Targets
expected: Root `Makefile` exists with targets: setup, sync-all, test, test-auth, test-room, test-booking, test-gateway, test-chat, lint, lock-all, clean.
result: pass

### 11. .gitignore Updated for Service Venvs
expected: `.gitignore` contains a pattern covering service `.venv/` directories.
result: pass

### 12. Docker Compose Config Still Merges
expected: `docker compose -f docker-compose.yml -f docker-compose.prod.yml config` completes without errors.
result: pass

## Summary

total: 12
passed: 12
issues: 0
pending: 0
skipped: 0

## Gaps

[none]
