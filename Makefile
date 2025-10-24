.PHONY: dev install test test-plugin doctor verify clean lint format install-plugin install-plugin-minimal install-plugin-dev uninstall-plugin reinstall-plugin reinstall-plugin-minimal reinstall-plugin-dev help

# Development installation (local source, editable) - RECOMMENDED
dev:
	@echo "🔧 Installing SuperClaude Framework (development mode)..."
	uv pip install -e ".[dev]"
	@echo ""
	@echo "✅ Installation complete!"
	@echo "   Run 'make verify' to check installation"

# Alias for backward compatibility
install: dev

# Run tests
test:
	@echo "Running tests..."
	uv run pytest

# Test pytest plugin loading
test-plugin:
	@echo "Testing pytest plugin auto-discovery..."
	@uv run python -m pytest --trace-config 2>&1 | grep -A2 "registered third-party plugins:" | grep superclaude && echo "✅ Plugin loaded successfully" || echo "❌ Plugin not loaded"

# Run doctor command
doctor:
	@echo "Running SuperClaude health check..."
	@uv run superclaude doctor

# Verify Phase 1 installation
verify:
	@echo "🔍 Phase 1 Installation Verification"
	@echo "======================================"
	@echo ""
	@echo "1. Package location:"
	@uv run python -c "import superclaude; print(f'   {superclaude.__file__}')"
	@echo ""
	@echo "2. Package version:"
	@uv run superclaude --version | sed 's/^/   /'
	@echo ""
	@echo "3. Pytest plugin:"
	@uv run python -m pytest --trace-config 2>&1 | grep "registered third-party plugins:" -A2 | grep superclaude | sed 's/^/   /' && echo "   ✅ Plugin loaded" || echo "   ❌ Plugin not loaded"
	@echo ""
	@echo "4. Health check:"
	@uv run superclaude doctor | grep "SuperClaude is healthy" > /dev/null && echo "   ✅ All checks passed" || echo "   ❌ Some checks failed"
	@echo ""
	@echo "======================================"
	@echo "✅ Phase 1 verification complete"

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

# Install Claude Code plugin - MINIMAL (manifest only, for baseline performance)
install-plugin-minimal:
	@echo "🔌 Installing SuperClaude plugin (MINIMAL) to Claude Code..."
	@if [ -d ~/.claude/plugins/superclaude ]; then \
		echo "⚠️  Plugin already exists at ~/.claude/plugins/superclaude"; \
		echo "   Run 'make reinstall-plugin-minimal' to update"; \
		exit 1; \
	fi
	@mkdir -p ~/.claude/plugins/superclaude
	@cp .claude-plugin/plugin.json ~/.claude/plugins/superclaude/
	@cp .claude-plugin/marketplace.json ~/.claude/plugins/superclaude/
	@echo ""
	@echo "✅ Plugin installed (MINIMAL configuration)"
	@echo "   Only manifest files copied - for baseline performance testing"
	@echo ""
	@echo "🔄 Restart Claude Code to activate plugins"

# Install Claude Code plugin - DEV (full, for development)
install-plugin-dev:
	@echo "🔌 Installing SuperClaude plugin (DEV) to Claude Code..."
	@if [ -d ~/.claude/plugins/superclaude ]; then \
		echo "⚠️  Plugin already exists at ~/.claude/plugins/superclaude"; \
		echo "   Run 'make reinstall-plugin-dev' to update"; \
		exit 1; \
	fi
	@mkdir -p ~/.claude/plugins/superclaude
	@cp -r .claude-plugin/* ~/.claude/plugins/superclaude/
	@cp -r commands ~/.claude/plugins/superclaude/
	@cp -r hooks ~/.claude/plugins/superclaude/
	@echo ""
	@echo "✅ Plugin installed (DEV configuration)"
	@echo ""
	@echo "📋 Installed components:"
	@echo "   - /pm: PM Agent orchestrator (SessionStart hook)"
	@echo "   - /research: Deep web search with adaptive planning"
	@echo "   - /index-repo: Repository indexing (94%% token reduction)"
	@echo ""
	@echo "🔄 Restart Claude Code to activate plugins"

# Default install (dev configuration for backward compatibility)
install-plugin: install-plugin-dev

# Uninstall Claude Code plugin
uninstall-plugin:
	@echo "🗑️  Uninstalling SuperClaude plugin..."
	@if [ ! -d ~/.claude/plugins/superclaude ]; then \
		echo "❌ Plugin not found at ~/.claude/plugins/superclaude"; \
		exit 1; \
	fi
	@rm -rf ~/.claude/plugins/superclaude
	@echo "✅ Plugin uninstalled successfully"

# Reinstall plugin - MINIMAL
reinstall-plugin-minimal:
	@echo "🔄 Reinstalling SuperClaude plugin (MINIMAL)..."
	@rm -rf ~/.claude/plugins/superclaude 2>/dev/null || true
	@mkdir -p ~/.claude/plugins/superclaude
	@cp .claude-plugin/plugin.json ~/.claude/plugins/superclaude/
	@cp .claude-plugin/marketplace.json ~/.claude/plugins/superclaude/
	@echo "✅ Plugin reinstalled (MINIMAL configuration)"
	@echo "🔄 Restart Claude Code to apply changes"

# Reinstall plugin - DEV
reinstall-plugin-dev:
	@echo "🔄 Reinstalling SuperClaude plugin (DEV)..."
	@rm -rf ~/.claude/plugins/superclaude 2>/dev/null || true
	@mkdir -p ~/.claude/plugins/superclaude
	@cp -r .claude-plugin/* ~/.claude/plugins/superclaude/
	@cp -r agents ~/.claude/plugins/superclaude/
	@cp -r commands ~/.claude/plugins/superclaude/
	@cp -r skills ~/.claude/plugins/superclaude/
	@cp -r hooks ~/.claude/plugins/superclaude/
	@cp -r pm ~/.claude/plugins/superclaude/
	@cp -r research ~/.claude/plugins/superclaude/
	@cp -r index ~/.claude/plugins/superclaude/
	@echo "✅ Plugin reinstalled (DEV configuration)"
	@echo "   - Commands: /pm, /research, /index-repo"
	@echo "   - Agents: self-review, deep-research, repo-index"
	@echo "   - Skills: confidence-check"
	@echo "   - TypeScript: pm/, research/, index/"
	@echo "🔄 Restart Claude Code to apply changes"

# Default reinstall (dev configuration for backward compatibility)
reinstall-plugin: reinstall-plugin-dev

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
	@echo "🚀 Quick Start:"
	@echo "  make dev             - Install in development mode (RECOMMENDED)"
	@echo "  make verify          - Verify installation is working"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make test            - Run test suite"
	@echo "  make test-plugin     - Test pytest plugin auto-discovery"
	@echo "  make doctor          - Run health check"
	@echo "  make lint            - Run linter (ruff check)"
	@echo "  make format          - Format code (ruff format)"
	@echo "  make clean           - Clean build artifacts"
	@echo ""
	@echo "🔌 Plugin Management:"
	@echo "  make install-plugin  - Install plugin to Claude Code (~/.claude/plugins/)"
	@echo "  make uninstall-plugin - Remove plugin from Claude Code"
	@echo "  make reinstall-plugin - Update existing plugin installation"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  make translate       - Translate README to Chinese and Japanese"
	@echo "  make help            - Show this help message"
	@echo ""
	@echo "💡 Legacy (backward compatibility):"
	@echo "  make install         - Alias for 'make dev'"
