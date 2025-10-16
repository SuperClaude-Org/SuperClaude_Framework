.PHONY: install dev test clean lint format uninstall update help

# Full installation (dependencies + SuperClaude components)
install:
	@echo "Installing SuperClaude Framework..."
	uv pip install -e ".[dev]"
	uv run superclaude install

# Install dependencies and SuperClaude (for development)
dev:
	@echo "Installing development dependencies..."
	uv pip install -e ".[dev]"
	@echo "Installing SuperClaude components..."
	uv run superclaude install

# Run tests
test:
	@echo "Running tests..."
	uv run pytest

# Linting
lint:
	@echo "Running linter..."
	uv run ruff check .

# Format code
format:
	@echo "Formatting code..."
	uv run ruff format .

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

# Uninstall SuperClaude components
uninstall:
	@echo "Uninstalling SuperClaude components..."
	uv run superclaude uninstall

# Update SuperClaude components
update:
	@echo "Updating SuperClaude components..."
	uv run superclaude update

# Show help
help:
	@echo "SuperClaude Framework - Available commands:"
	@echo ""
	@echo "  make install    - Full installation (dependencies + components)"
	@echo "  make dev        - Install development dependencies only"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make uninstall  - Uninstall SuperClaude components"
	@echo "  make update     - Update SuperClaude components"
	@echo "  make help       - Show this help message"
