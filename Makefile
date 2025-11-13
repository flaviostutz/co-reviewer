.PHONY: setup install build test lint run deploy undeploy all clean

setup:
	@echo "Setting up development environment..."
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@echo "Setup complete!"

install:
	@echo "Installing dependencies..."
	uv sync --all-extras
	@echo "Dependencies installed!"

build:
	@echo "Building package..."
	uv build
	@echo "Build complete!"

test:
	@echo "Running tests..."
	uv run pytest -v
	@echo "Tests complete!"

lint:
	@echo "Running linters..."
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy co_reviewer
	@echo "Linting complete!"

lint-fix:
	@echo "Fixing linting issues..."
	uv run ruff check --fix .
	uv run ruff format .
	@echo "Linting fixes applied!"

run:
	@echo "Running co-reviewer..."
	uv run python -m co_reviewer.cli

run-server:
	@echo "Starting API server..."
	uv run uvicorn co_reviewer.api:app --reload

all: lint test build
	@echo "All checks passed!"

clean:
	@echo "Cleaning up..."
	rm -rf dist/ build/ *.egg-info htmlcov/ .coverage .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"
