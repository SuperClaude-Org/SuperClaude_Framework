.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync lint-architecture uninstall-legacy help

# Installation (local source, editable) - RECOMMENDED
install:
	@echo "🔧 Installing SuperClaude Framework (development mode)..."
	uv pip install -e ".[dev]"
	@echo ""
	@echo "✅ Installation complete!"
	@echo "   Run 'make verify' to check installation"

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

PLUGIN_DIST := dist/plugins/superclaude
PLUGIN_REPO ?= ../SuperClaude_Plugin

.PHONY: build-plugin
build-plugin: ## Build SuperClaude plugin artefacts into dist/
	@echo "🛠️  Building SuperClaude plugin from unified sources..."
	@uv run python scripts/build_superclaude_plugin.py

.PHONY: sync-plugin-repo
sync-plugin-repo: build-plugin ## Sync built plugin artefacts into ../SuperClaude_Plugin
	@if [ ! -d "$(PLUGIN_REPO)" ]; then \
		echo "❌ Target plugin repository not found at $(PLUGIN_REPO)"; \
		echo "   Set PLUGIN_REPO=/path/to/SuperClaude_Plugin when running make."; \
		exit 1; \
	fi
	@echo "📦 Syncing artefacts to $(PLUGIN_REPO)..."
	@rsync -a --delete $(PLUGIN_DIST)/agents/ $(PLUGIN_REPO)/agents/
	@rsync -a --delete $(PLUGIN_DIST)/commands/ $(PLUGIN_REPO)/commands/
	@rsync -a --delete $(PLUGIN_DIST)/hooks/ $(PLUGIN_REPO)/hooks/
	@rsync -a --delete $(PLUGIN_DIST)/scripts/ $(PLUGIN_REPO)/scripts/
	@rsync -a --delete $(PLUGIN_DIST)/skills/ $(PLUGIN_REPO)/skills/
	@rsync -a --delete $(PLUGIN_DIST)/.claude-plugin/ $(PLUGIN_REPO)/.claude-plugin/
	@echo "✅ Sync complete."

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

# Sync src/superclaude/{skills,agents} → .claude/{skills,agents} for local dev
sync-dev:
	@echo "🔄 Syncing src/superclaude/ → .claude/ for local development..."
	@mkdir -p .claude/skills .claude/agents
	@for skill_dir in src/superclaude/skills/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		case "$$skill_name" in __*) continue;; esac; \
		if [ -f "$$skill_dir/SKILL.md" ] || [ -f "$$skill_dir/skill.md" ]; then \
			mkdir -p ".claude/skills/$$skill_name"; \
			find "$$skill_dir" -type f ! -name '__init__.py' ! -path '*/__pycache__/*' -exec sh -c ' \
				src="$$1"; skill_dir="$$2"; target_base="$$3"; \
				rel=$${src#$$skill_dir}; \
				target_dir="$$target_base/$$(dirname "$$rel")"; \
				mkdir -p "$$target_dir"; \
				cp "$$src" "$$target_dir/" \
			' _ {} "$$skill_dir" ".claude/skills/$$skill_name" \; ; \
		fi; \
	done
	@for agent in src/superclaude/agents/*.md; do \
		name=$$(basename "$$agent"); \
		case "$$name" in README.md) continue;; esac; \
		cp "$$agent" ".claude/agents/$$name"; \
	done
	@mkdir -p .claude/commands/sc
	@for cmd in src/superclaude/commands/*.md; do \
		name=$$(basename "$$cmd"); \
		case "$$name" in README.md|__init__.py) continue;; esac; \
		cp "$$cmd" ".claude/commands/sc/$$name"; \
	done
	@echo "✅ Sync complete."
	@echo "   Skills:   $$(ls -d .claude/skills/*/ 2>/dev/null | wc -l | tr -d ' ') directories"
	@echo "   Agents:   $$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "   Commands: $$(ls .claude/commands/sc/*.md 2>/dev/null | wc -l | tr -d ' ') files"

# Verify src/superclaude/ and .claude/ are in sync (CI-friendly, exits 1 on drift)
verify-sync:
	@echo "🔍 Verifying src/superclaude/ ↔ .claude/ sync..."
	@drift=0; \
	echo ""; \
	echo "=== Skills ==="; \
	for skill_dir in src/superclaude/skills/*/; do \
		name=$$(basename "$$skill_dir"); \
		case "$$name" in __*) continue;; esac; \
		if [ ! -d ".claude/skills/$$name" ]; then \
			echo "  ❌ MISSING in .claude/skills/: $$name"; \
			drift=1; \
		else \
			changes=$$(diff -rq --exclude='__init__.py' --exclude='__pycache__' "$$skill_dir" ".claude/skills/$$name" 2>/dev/null); \
			if [ -n "$$changes" ]; then \
				echo "  ⚠️  DIFFERS: $$name"; \
				echo "$$changes" | sed 's/^/      /'; \
				drift=1; \
			else \
				echo "  ✅ $$name"; \
			fi; \
		fi; \
	done; \
	for skill_dir in .claude/skills/*/; do \
		name=$$(basename "$$skill_dir"); \
		case "$$name" in __*) continue;; esac; \
		if [ ! -d "src/superclaude/skills/$$name" ]; then \
			echo "  ❌ MISSING in src/superclaude/skills/: $$name (not distributable!)"; \
			drift=1; \
		fi; \
	done; \
	echo ""; \
	echo "=== Agents ==="; \
	for agent in src/superclaude/agents/*.md; do \
		name=$$(basename "$$agent"); \
		case "$$name" in README.md) continue;; esac; \
		if [ ! -f ".claude/agents/$$name" ]; then \
			echo "  ❌ MISSING in .claude/agents/: $$name"; \
			drift=1; \
		else \
			if ! diff -q "$$agent" ".claude/agents/$$name" > /dev/null 2>&1; then \
				echo "  ⚠️  DIFFERS: $$name"; \
				drift=1; \
			else \
				echo "  ✅ $$name"; \
			fi; \
		fi; \
	done; \
	for agent in .claude/agents/*.md; do \
		[ -f "$$agent" ] || continue; \
		name=$$(basename "$$agent"); \
		case "$$name" in README.md) continue;; esac; \
		if [ ! -f "src/superclaude/agents/$$name" ]; then \
			echo "  ❌ MISSING in src/superclaude/agents/: $$name (not distributable!)"; \
			drift=1; \
		fi; \
	done; \
	echo ""; \
	echo "=== Commands ==="; \
	for cmd in src/superclaude/commands/*.md; do \
		name=$$(basename "$$cmd"); \
		case "$$name" in README.md) continue;; esac; \
		if [ ! -f ".claude/commands/sc/$$name" ]; then \
			echo "  ❌ MISSING in .claude/commands/sc/: $$name"; \
			drift=1; \
		else \
			if ! diff -q "$$cmd" ".claude/commands/sc/$$name" > /dev/null 2>&1; then \
				echo "  ⚠️  DIFFERS: $$name"; \
				drift=1; \
			else \
				echo "  ✅ $$name"; \
			fi; \
		fi; \
	done; \
	for cmd in .claude/commands/sc/*.md; do \
		[ -f "$$cmd" ] || continue; \
		name=$$(basename "$$cmd"); \
		case "$$name" in README.md) continue;; esac; \
		if [ ! -f "src/superclaude/commands/$$name" ]; then \
			echo "  ❌ MISSING in src/superclaude/commands/: $$name (not distributable!)"; \
			drift=1; \
		fi; \
	done; \
	echo ""; \
	if [ "$$drift" -eq 0 ]; then \
		echo "✅ All components in sync."; \
	else \
		echo "❌ Drift detected! Run 'make sync-dev' to fix, or copy .claude/ changes to src/."; \
		exit 1; \
	fi

# Enforce architecture policy: commands, skills, naming conventions
lint-architecture:
	@echo "🔍 Checking architecture policy compliance..."
	@errors=0; \
	warnings=0; \
	\
	echo ""; \
	echo "=== Check 1/2: Bidirectional Command ↔ Skill Links ==="; \
	for f in src/superclaude/commands/*.md; do \
		name=$$(basename "$$f" .md); \
		case "$$name" in README) continue;; esac; \
		if grep -q "## Activation" "$$f"; then \
			skill_name="sc-$$name-protocol"; \
			if [ ! -d "src/superclaude/skills/$$skill_name" ]; then \
				echo "  ❌ ERROR [Check 1]: $$f has ## Activation but no matching skill directory: $$skill_name"; \
				errors=$$((errors+1)); \
			else \
				echo "  ✅ [Check 1]: $$name → $$skill_name"; \
			fi; \
		fi; \
	done; \
	for d in src/superclaude/skills/sc-*-protocol/; do \
		skill_base=$$(basename "$$d"); \
		cmd_name=$$(echo "$$skill_base" | sed 's/^sc-//' | sed 's/-protocol$$//'); \
		cmd_file="src/superclaude/commands/$$cmd_name.md"; \
		if [ ! -f "$$cmd_file" ]; then \
			echo "  ❌ ERROR [Check 2]: Skill $$skill_base has no matching command: $$cmd_file"; \
			errors=$$((errors+1)); \
		else \
			echo "  ✅ [Check 2]: $$skill_base ← $$cmd_name.md"; \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Check 3/4: Command Size Limits ==="; \
	for f in src/superclaude/commands/*.md; do \
		name=$$(basename "$$f"); \
		case "$$name" in README.md) continue;; esac; \
		lines=$$(wc -l < "$$f"); \
		if [ "$$lines" -gt 500 ]; then \
			echo "  ❌ ERROR [Check 4]: $$name ($$lines lines, hard limit 500)"; \
			errors=$$((errors+1)); \
		elif [ "$$lines" -gt 350 ] && grep -q "## Activation" "$$f"; then \
			echo "  ❌ ERROR [Check 4]: $$name ($$lines lines, max ≤350 for paired commands)"; \
			errors=$$((errors+1)); \
		elif [ "$$lines" -gt 200 ]; then \
			echo "  ⚠️  WARN [Check 3]: $$name ($$lines lines, warn threshold 200)"; \
			warnings=$$((warnings+1)); \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Check 6: Activation Section Present (for paired commands) ==="; \
	for d in src/superclaude/skills/sc-*-protocol/; do \
		skill_base=$$(basename "$$d"); \
		cmd_name=$$(echo "$$skill_base" | sed 's/^sc-//' | sed 's/-protocol$$//'); \
		cmd_file="src/superclaude/commands/$$cmd_name.md"; \
		if [ -f "$$cmd_file" ]; then \
			if grep -q "## Activation" "$$cmd_file"; then \
				echo "  ✅ [Check 6]: $$cmd_name.md has ## Activation"; \
			else \
				echo "  ❌ ERROR [Check 6]: $$cmd_name.md missing ## Activation (paired with $$skill_base)"; \
				errors=$$((errors+1)); \
			fi; \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Check 8: Skill Frontmatter Completeness ==="; \
	for skill_md in src/superclaude/skills/sc-*-protocol/SKILL.md; do \
		for field in "name:" "description:" "allowed-tools:"; do \
			if ! grep -q "^$$field" "$$skill_md"; then \
				echo "  ❌ ERROR [Check 8]: $$skill_md missing frontmatter field: $$field"; \
				errors=$$((errors+1)); \
			fi; \
		done; \
		echo "  ✅ [Check 8]: $$(dirname $$skill_md | xargs basename) frontmatter complete"; \
	done; \
	\
	echo ""; \
	echo "=== Check 9: Protocol Naming Consistency ==="; \
	for skill_md in src/superclaude/skills/sc-*-protocol/SKILL.md; do \
		name_field=$$(grep "^name:" "$$skill_md" | head -1 | sed 's/^name:[[:space:]]*//' | tr -d ' "'); \
		if echo "$$name_field" | grep -q ".*-protocol$$"; then \
			echo "  ✅ [Check 9]: $$name_field ends in -protocol"; \
		else \
			echo "  ❌ ERROR [Check 9]: $$(dirname $$skill_md | xargs basename) SKILL.md name field '$$name_field' does not end in -protocol"; \
			errors=$$((errors+1)); \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Checks 5/7: NEEDS DESIGN (skipped) ==="; \
	echo "  ℹ️  Check 5 (inline protocol detection) — pending design"; \
	echo "  ℹ️  Check 7 (activation references correct skill) — pending design"; \
	\
	echo ""; \
	echo "=== Summary ==="; \
	echo "  Errors:   $$errors"; \
	echo "  Warnings: $$warnings"; \
	if [ "$$errors" -gt 0 ]; then \
		echo "  ❌ FAIL — $$errors error(s) found. Fix before proceeding."; \
		exit 1; \
	else \
		echo "  ✅ PASS — architecture policy compliant ($$warnings warning(s))"; \
		exit 0; \
	fi

# Show help
help:
	@echo "SuperClaude Framework - Available commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make install         - Install in development mode (RECOMMENDED)"
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
	@echo "🔄 Component Sync:"
	@echo "  make sync-dev        - Sync src/ → .claude/ for local development"
	@echo "  make verify-sync     - Check src/ and .claude/ are in sync (CI-friendly)"
	@echo "  make lint-architecture - Enforce architecture policy (6 of 10 checks)"
	@echo ""
	@echo "🔌 Plugin Packaging:"
	@echo "  make build-plugin    - Build SuperClaude plugin artefacts into dist/"
	@echo "  make sync-plugin-repo - Sync artefacts into ../SuperClaude_Plugin"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  make translate       - Translate README to Chinese and Japanese"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make uninstall-legacy - Remove old SuperClaude files from ~/.claude"
	@echo "  make help            - Show this help message"

# Remove legacy SuperClaude files from ~/.claude directory
uninstall-legacy:
	@echo "🧹 Cleaning up legacy SuperClaude files..."
	@bash scripts/uninstall_legacy.sh
	@echo ""
