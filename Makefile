# Makefile for FastAPI + Vue (Vite) project

.DEFAULT_GOAL := help

.PHONY: help sync format lint check test run run-backend run-frontend ci clean

# -----------------------
# General help
# -----------------------
help:
	@echo "Available targets:"
	@echo "  sync             Install/sync dependencies"
	@echo "  format           Auto-format Python code with ruff"
	@echo "  lint             Lint and auto-fix Python code with ruff"
	@echo "  check            Run format + lint (Python only)"
	@echo "  test             Run Python unit tests with coverage"	
	@echo "  run-backend      Run FastAPI app only"
	@echo "  run-frontend     Run Vue (Vite) frontend only"
	@echo "  ci               Full CI pipeline"
	@echo "  clean            Remove cache files"

# -----------------------
# Python dev commands
# -----------------------
sync:
	uv -V
	uv sync --all-groups

format:
	uv run ruff format .

lint:
	uv run ruff check --fix

check: format lint

test:
	uv run coverage run -m pytest -v -s
	uv run coverage html
	uv run coverage report -m

cli:
	uv run python -m app.cli

run-backend:
	@echo "Running FastAPI app on http://127.0.0.1:8000"
	uv run uvicorn app.api:app --reload

# -----------------------
# Frontend commands
# -----------------------
run-frontend:
	@echo "Running Vite dev server on http://localhost:5173"
	cd frontend && npm install && npm run dev


# -----------------------
# CI
# -----------------------
ci: sync check test

# -----------------------
# Clean caches
# -----------------------
clean:
	rm -rf .ruff_cache .pytest_cache __pycache__ htmlcov .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete