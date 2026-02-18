# Makefile for running tests and FastAPI app

.DEFAULT_GOAL := help


.PHONY: help sync format lint check test run run-fast clean

help:
	@echo "Available targets:"
	@echo "  sync       Install/sync dependencies"
	@echo "  format     Auto-format code with ruff"
	@echo "  lint       Lint and auto-fix with ruff"
	@echo "  check      Run format + lint (no tests)"
	@echo "  test       Run unit tests"
	@echo "  run        Run app"	
	@echo "  ci         Full CI pipeline"
	@echo "  clean      Remove cache files"

sync:
	uv -V         
	uv sync --all-groups

format:
	uv run ruff format .

lint:
	uv run ruff check --fix

check: format lint

# Run unittests
test:	
	uv run coverage run -m pytest -v -s
	uv run coverage html
	uv run coverage report -m
	
cli:
	uv run python -m app.cli

run-fast:
	@echo "Running FastAPI app on http://127.0.0.1:8000"
	uv run uvicorn app.api:app --reload

run: run-fast

ci: sync check test

clean:
	rm -rf .ruff_cache .pytest_cache __pycache__ htmlcov .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
