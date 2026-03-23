.PHONY: setup sync-all test lint test-auth test-room test-booking test-gateway test-chat lock-all clean

SERVICES := auth room booking gateway chat

## Setup: Install uv and sync all services
setup:
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@$(MAKE) sync-all

## Sync all service dependencies
sync-all:
	@for svc in $(SERVICES); do \
		echo "Syncing $$svc..."; \
		(cd services/$$svc && uv sync); \
	done
	@echo "All services synced."

## Run all backend tests
test: test-auth test-room test-booking test-gateway test-chat

## Run auth service tests
test-auth:
	cd services/auth && uv run pytest tests/ -x --tb=short

## Run room service tests
test-room:
	cd services/room && uv run pytest tests/ -x --tb=short

## Run booking service tests
test-booking:
	cd services/booking && uv run pytest tests/ -x --tb=short

## Run gateway service tests
test-gateway:
	cd services/gateway && uv run pytest tests/ -x --tb=short

## Run chat service tests
test-chat:
	cd services/chat && uv run pytest tests/ -x --tb=short

## Lint all Python code
lint:
	uvx ruff check services/ shared/

## Lock all services (regenerate uv.lock files)
lock-all:
	@for svc in $(SERVICES); do \
		echo "Locking $$svc..."; \
		(cd services/$$svc && uv lock); \
	done
	@echo "All services locked."

## Clean virtual environments
clean:
	@for svc in $(SERVICES); do \
		rm -rf services/$$svc/.venv; \
	done
	@echo "All .venv directories removed."
