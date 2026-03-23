FROM python:3.12-slim

# Install uv (pinned version)
COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

# Configure uv for production
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Use WORKDIR that preserves relative path to shared/
WORKDIR /build/services/gateway

# Layer 1: Copy shared package (changes rarely)
COPY shared/ /build/shared/

# Layer 2: Copy dependency manifests only (cached when deps unchanged)
COPY services/gateway/pyproject.toml services/gateway/uv.lock ./

# Layer 3: Install dependencies only (no project install yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Layer 4: Copy service source code (changes frequently)
COPY services/gateway/ .

# Layer 5: Install the project itself (picks up source)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Activate the virtual environment and set PYTHONPATH
ENV PATH="/build/services/gateway/.venv/bin:$PATH" \
    PYTHONPATH="/build/services/gateway"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
