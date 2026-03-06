.DEFAULT_GOAL := help

.PHONY: help sync backend-sync frontend-sync format format-check lint lint-frontend format-frontend check test run-backend run-frontend ci clean cli

# -----------------------
# Help
# -----------------------
help:
	@echo "Available targets:"
	@echo "  sync     Install dependencies"
	@echo "  backend-sync     Install Python dependencies"
	@echo "  frontend-sync    Install Node dependencies"
	@echo "  format           Format Python code"
	@echo "  format-check     Check formatting (CI)"
	@echo "  lint             Lint Python code"
	@echo "  lint-frontend    Lint frontend"
	@echo "  format-frontend  Format frontend"
	@echo "  check            Run all format + lint"
	@echo "  test             Run Python tests"
	@echo "  run-backend      Run FastAPI backend"
	@echo "  run-frontend     Run Vue frontend"	
	@echo "  ci               CI pipeline"
	@echo "  clean            Clean cache files"

# -----------------------
# Dependencies
# -----------------------
sync: backend-sync frontend-sync

backend-sync:
	uv -V
	uv sync --all-groups

frontend-sync:
	cd frontend && npm ci

build-frontend:
	cd frontend && npm run build

# -----------------------
# Python formatting
# -----------------------
format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

# -----------------------
# Frontend
# -----------------------
format-frontend:
	cd frontend && npm run format

lint-frontend:
	cd frontend && npm run lint

# -----------------------
# Checks
# -----------------------
check: format lint format-frontend lint-frontend

# -----------------------
# Tests
# -----------------------
test:
	uv run coverage run -m pytest -v
	uv run coverage html
	uv run coverage report -m

# -----------------------
# CLI
# -----------------------
cli:
	uv run python -m app.cli

# -----------------------
# Run
# -----------------------
BACKEND_PORT ?= 8000
VITE_PORT ?= 3000

run-backend:
	@echo "Running FastAPI on http://127.0.0.1:$(BACKEND_PORT)"
	uv run uvicorn app.api:app \
		--reload \
		--port $(BACKEND_PORT)
		

run-frontend:
	@echo "Running Vite dev server on port $(VITE_PORT)"
	cd frontend && npm run dev  -- --port $(VITE_PORT)

# -----------------------
# CI
# -----------------------
ci: backend-sync frontend-sync format-check lint lint-frontend test

# -----------------------
# Clean
# -----------------------
clean:
	rm -rf .ruff_cache .pytest_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete