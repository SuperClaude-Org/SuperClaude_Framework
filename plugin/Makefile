.PHONY: dev install test test-plugin doctor verify clean clean-superclaude lint format install-plugin install-plugin-minimal install-plugin-dev uninstall-plugin reinstall-plugin reinstall-plugin-minimal reinstall-plugin-dev help

# Development installation (local source, editable) - FOR PYTHON PACKAGE ONLY
dev:
	@echo "🔧 Installing Airiscode Python package (development mode)..."
	@echo "⚠️  NOTE: This installs the Python package (pytest plugin + CLI) only."
	@echo "⚠️  For Claude Code plugin, use project-local or 'make install-plugin-dev'"
	@echo ""
	uv pip install -e ".[dev]"
	@echo ""
	@echo "✅ Python package installation complete!"
	@echo "   Run 'make verify' to check installation"

# Alias for backward compatibility
install: dev

# Run tests (accepts ARGS for specific tests)
# Usage:
#   make test                              # Run all tests
#   make test ARGS="tests/pm_agent/ -v"    # Run specific directory
#   make test ARGS="tests/test.py::name"   # Run specific test
#   make test ARGS="-m confidence_check"   # Run by marker
test:
	@echo "Running tests..."
	uv run pytest $(ARGS)

# Test pytest plugin loading
test-plugin:
	@echo "Testing pytest plugin auto-discovery..."
	@uv run python -m pytest --trace-config 2>&1 | grep -A2 "registered third-party plugins:" | grep airiscode && echo "✅ Plugin loaded successfully" || echo "❌ Plugin not loaded"

# Run doctor command
doctor:
	@echo "Running Airiscode health check..."
	@uv run airiscode doctor

# Verify installation (Python package + Claude Code plugin)
verify:
	@echo "🔍 Airiscode Installation Verification"
	@echo "======================================"
	@echo ""
	@echo "1. Python package location:"
	@uv run python -c "import airiscode; print(f'   {airiscode.__file__}')" 2>&1 || echo "   ❌ Not installed (run 'make dev' first)"
	@echo ""
	@echo "2. Package version:"
	@uv run airiscode --version 2>&1 | sed 's/^/   /' || echo "   ❌ CLI not available"
	@echo ""
	@echo "3. Pytest plugin:"
	@uv run python -m pytest --trace-config 2>&1 | grep "registered third-party plugins:" -A2 | grep airiscode | sed 's/^/   /' && echo "   ✅ Plugin loaded" || echo "   ❌ Plugin not loaded"
	@echo ""
	@echo "4. Health check:"
	@uv run airiscode doctor 2>&1 | grep -i "healthy" > /dev/null && echo "   ✅ All checks passed" || echo "   ❌ Some checks failed"
	@echo ""
	@echo "5. Claude Code plugin:"
	@[ -f .claude-plugin/plugin.json ] && echo "   ✅ plugin.json found" || echo "   ❌ plugin.json missing"
	@[ -f .claude/settings.json ] && echo "   ✅ settings.json found" || echo "   ❌ settings.json missing"
	@echo ""
	@echo "======================================"
	@echo "✅ Verification complete"
	@echo ""
	@echo "To use Claude Code plugin:"
	@echo "  - Project-local: 'cd $(PWD) && claude'"
	@echo "  - Global: 'make install-plugin-dev'"

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

# Clean SuperClaude legacy configuration from ~/.claude/
clean-superclaude:
	@echo "🧹 Cleaning SuperClaude legacy configuration from ~/.claude/..."
	@echo ""
	@echo "⚠️  This will remove:"
	@echo "   - ~/.claude/hooks/ (SuperClaude-specific hooks)"
	@echo "   - Old plugin references in ~/.claude/settings.json"
	@echo "   - ~/.claude/plugins/pm-agent/ (if exists)"
	@echo ""
	@if [ -d ~/.claude/hooks ] && grep -q "SuperClaude Framework" ~/.claude/hooks/*.sh 2>/dev/null; then \
		echo "🗑️  Removing ~/.claude/hooks/ (SuperClaude-specific)..."; \
		rm -rf ~/.claude/hooks/; \
		echo "   ✅ Removed"; \
	else \
		echo "   ℹ️  ~/.claude/hooks/ not found or not SuperClaude-specific (skipped)"; \
	fi
	@echo ""
	@if [ -f ~/.claude/settings.json ]; then \
		echo "🔧 Cleaning ~/.claude/settings.json..."; \
		if grep -q "pm-agent@superclaude-local\|airiscode@superclaude-local" ~/.claude/settings.json 2>/dev/null; then \
			cp ~/.claude/settings.json ~/.claude/settings.json.bak; \
			sed -E '/"pm-agent@superclaude-local"|"airiscode@superclaude-local"/d' ~/.claude/settings.json | \
			sed -E '/^[[:space:]]*"enabledPlugins"[[:space:]]*:[[:space:]]*\{[[:space:]]*\}[[:space:]]*,?$$/d' > ~/.claude/settings.json.tmp; \
			mv ~/.claude/settings.json.tmp ~/.claude/settings.json; \
			echo "   ✅ Removed old plugin references (backup: settings.json.bak)"; \
		else \
			echo "   ℹ️  No SuperClaude plugin references found"; \
		fi; \
	else \
		echo "   ℹ️  ~/.claude/settings.json not found"; \
	fi
	@echo ""
	@if [ -d ~/.claude/plugins/pm-agent ]; then \
		echo "🗑️  Removing ~/.claude/plugins/pm-agent/..."; \
		rm -rf ~/.claude/plugins/pm-agent/; \
		echo "   ✅ Removed"; \
	else \
		echo "   ℹ️  ~/.claude/plugins/pm-agent/ not found"; \
	fi
	@echo ""
	@echo "✅ SuperClaude legacy cleanup complete!"
	@echo ""
	@echo "💡 Next steps:"
	@echo "   1. Use project-local: 'cd $(PWD) && claude'"
	@echo "   2. Or install globally: 'make install-plugin-dev'"

# Install Claude Code plugin - MINIMAL (manifest only, for baseline performance)
install-plugin-minimal:
	@echo "🔌 Installing Airiscode plugin (MINIMAL) to Claude Code..."
	@if [ -d ~/.claude/plugins/airiscode ]; then \
		echo "⚠️  Plugin already exists at ~/.claude/plugins/airiscode"; \
		echo "   Run 'make reinstall-plugin-minimal' to update"; \
		exit 1; \
	fi
	@mkdir -p ~/.claude/plugins/airiscode
	@cp .claude-plugin/plugin.json ~/.claude/plugins/airiscode/
	@cp .claude-plugin/marketplace.json ~/.claude/plugins/airiscode/
	@echo ""
	@echo "✅ Plugin installed (MINIMAL configuration)"
	@echo "   Only manifest files copied - for baseline performance testing"
	@echo ""
	@echo "🔄 Restart Claude Code to activate plugins"

# Install Claude Code plugin - DEV (full, for development)
install-plugin-dev:
	@echo "🔌 Installing Airiscode plugin (DEV) to Claude Code..."
	@if [ -d ~/.claude/plugins/airiscode ]; then \
		echo "⚠️  Plugin already exists at ~/.claude/plugins/airiscode"; \
		echo "   Run 'make reinstall-plugin-dev' to update"; \
		exit 1; \
	fi
	@mkdir -p ~/.claude/plugins/airiscode
	@cp -r .claude-plugin/* ~/.claude/plugins/airiscode/
	@cp -r commands ~/.claude/plugins/airiscode/
	@cp -r agents ~/.claude/plugins/airiscode/
	@cp -r skills ~/.claude/plugins/airiscode/
	@cp -r hooks ~/.claude/plugins/airiscode/
	@echo ""
	@echo "✅ Plugin installed (DEV configuration)"
	@echo ""
	@echo "📋 Installed components:"
	@echo "   - /pm: PM Agent orchestrator (SessionStart hook)"
	@echo "   - @deep-research: Delegated web + MCP investigations"
	@echo "   - @repo-index: Repository indexing (94%% token reduction)"
	@echo "   - @self-review: Post-implementation validation"
	@echo ""
	@echo "🔄 Restart Claude Code to activate plugins"

# Default install (dev configuration for backward compatibility)
install-plugin: install-plugin-dev

# Uninstall Claude Code plugin
uninstall-plugin:
	@echo "🗑️  Uninstalling SuperClaude plugin..."
	@if [ ! -d ~/.claude/plugins/airiscode ]; then \
		echo "❌ Plugin not found at ~/.claude/plugins/airiscode"; \
		exit 1; \
	fi
	@rm -rf ~/.claude/plugins/airiscode
	@echo "✅ Plugin uninstalled successfully"

# Reinstall plugin - MINIMAL
reinstall-plugin-minimal:
	@echo "🔄 Reinstalling SuperClaude plugin (MINIMAL)..."
	@rm -rf ~/.claude/plugins/airiscode 2>/dev/null || true
	@mkdir -p ~/.claude/plugins/airiscode
	@cp .claude-plugin/plugin.json ~/.claude/plugins/airiscode/
	@cp .claude-plugin/marketplace.json ~/.claude/plugins/airiscode/
	@echo "✅ Plugin reinstalled (MINIMAL configuration)"
	@echo "🔄 Restart Claude Code to apply changes"

# Reinstall plugin - DEV
reinstall-plugin-dev:
	@echo "🔄 Reinstalling SuperClaude plugin (DEV)..."
	@rm -rf ~/.claude/plugins/airiscode 2>/dev/null || true
	@mkdir -p ~/.claude/plugins/airiscode
	@cp -r .claude-plugin/* ~/.claude/plugins/airiscode/
	@cp -r commands ~/.claude/plugins/airiscode/
	@cp -r agents ~/.claude/plugins/airiscode/
	@cp -r skills ~/.claude/plugins/airiscode/
	@cp -r hooks ~/.claude/plugins/airiscode/
	@echo "✅ Plugin reinstalled (DEV configuration)"
	@echo "   - Commands: /pm, /research, /index-repo"
	@echo "   - Agents: @deep-research, @repo-index, @self-review"
	@echo "   - Skills: confidence-check"
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
	@echo "Airiscode - Available commands:"
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
	@echo "  make clean-superclaude - Clean SuperClaude legacy config from ~/.claude/"
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
