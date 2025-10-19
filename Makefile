.PHONY: install install-release dev test clean lint format uninstall update translate help

# Development installation (local source, editable)
install:
	@echo "Installing SuperClaude Framework (development mode)..."
	uv pip install -e ".[dev]"
	uv run superclaude install

# Production installation (from PyPI, recommended for users)
install-release:
	@echo "Installing SuperClaude Framework (production mode)..."
	@echo "Using pipx for isolated environment..."
	pipx install SuperClaude
	pipx upgrade SuperClaude
	superclaude install

# Alias for development installation
dev: install

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

# Translate README to multiple languages using Neural CLI
translate:
	@echo "🌐 Translating README using Neural CLI (Ollama + qwen2.5:3b)..."
	@if [ ! -f ~/.local/bin/neural-cli ]; then \
		echo "📦 Installing neural-cli..."; \
		mkdir -p ~/.local/bin; \
		ln -sf ~/github/neural/src-tauri/target/release/neural-cli ~/.local/bin/neural-cli; \
		echo "✅ neural-cli installed to ~/.local/bin/"; \
	fi
	@echo ""
	@echo "🇨🇳 Translating to Simplified Chinese..."
	@~/.local/bin/neural-cli translate README.md --from English --to "Simplified Chinese" --output README-zh.md
	@echo ""
	@echo "🇯🇵 Translating to Japanese..."
	@~/.local/bin/neural-cli translate README.md --from English --to Japanese --output README-ja.md
	@echo ""
	@echo "✅ Translation complete!"
	@echo "📝 Files updated: README-zh.md, README-ja.md"

# Show help
help:
	@echo "SuperClaude Framework - Available commands:"
	@echo ""
	@echo "Installation:"
	@echo "  make install         - Development installation (local source, editable with uv)"
	@echo "  make install-release - Production installation (from PyPI with pipx)"
	@echo "  make dev             - Alias for 'make install'"
	@echo ""
	@echo "Development:"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linter"
	@echo "  make format          - Format code"
	@echo "  make clean           - Clean build artifacts"
	@echo ""
	@echo "Maintenance:"
	@echo "  make uninstall       - Uninstall SuperClaude components"
	@echo "  make update          - Update SuperClaude components"
	@echo ""
	@echo "Documentation:"
	@echo "  make translate       - Translate README to Chinese and Japanese (requires Ollama)"
	@echo "  make help            - Show this help message"
