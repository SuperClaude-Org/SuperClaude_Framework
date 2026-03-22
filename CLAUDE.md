# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🐍 Python Environment Rules

**CRITICAL**: This project uses **UV** for all Python operations. Never use `python -m`, `pip install`, or `python script.py` directly.

### Required Commands

```bash
# All Python operations must use UV
uv run pytest                    # Run tests
uv run pytest tests/pm_agent/   # Run specific tests
uv pip install package           # Install dependencies
uv run python script.py          # Execute scripts
```

## 📂 Project Structure

**Current v4.3.0 Architecture**: Python package with 30 commands, 20 agents, 7 modes

```
# Claude Code Configuration (v4.3.0)
# Installed via `superclaude install` to user's home directory
~/.claude/
├── settings.json
├── commands/sc/         # 30 slash commands (/sc:research, /sc:implement, etc.)
│   ├── pm.md
│   ├── research.md
│   ├── implement.md
│   └── ... (30 total)
├── agents/              # 20 domain-specialist agents (@pm-agent, @system-architect, etc.)
│   ├── pm-agent.md
│   ├── system-architect.md
│   └── ... (20 total)
└── skills/              # Skills (confidence-check, etc.)

# Python Package
src/superclaude/
├── __init__.py          # Public API: ConfidenceChecker, SelfCheckProtocol, ReflexionPattern
├── pytest_plugin.py     # Auto-loaded pytest integration (5 fixtures, 9 markers)
├── pm_agent/            # confidence.py, self_check.py, reflexion.py, token_budget.py
├── execution/           # parallel.py, reflection.py, self_correction.py
├── cli/                 # main.py, doctor.py, install_commands.py, install_mcp.py, install_skill.py
├── commands/            # 30 slash command definitions (.md files)
├── agents/              # 20 agent definitions (.md files)
├── modes/               # 7 behavioral modes (.md files)
├── skills/              # Installable skills (confidence-check, etc.)
├── hooks/               # Claude Code hook definitions
├── mcp/                 # MCP server configurations (10 servers)
└── core/                # Core utilities

# Project Files
tests/                   # Python test suite (136 tests)
├── unit/                # Unit tests (auto-marked @pytest.mark.unit)
└── integration/         # Integration tests (auto-marked @pytest.mark.integration)
docs/                    # Documentation
scripts/                 # Analysis tools (workflow metrics, A/B testing)
plugins/                 # Exported plugin artefacts for distribution
PLANNING.md              # Architecture, absolute rules
TASK.md                  # Current tasks
KNOWLEDGE.md             # Accumulated insights
```

### Claude Code Integration Points

SuperClaude integrates with Claude Code through these mechanisms:
- **Slash Commands**: 30 commands installed to `~/.claude/commands/sc/` (e.g., `/sc:pm`, `/sc:research`)
- **Agents**: 20 agents installed to `~/.claude/agents/` (e.g., `@pm-agent`, `@system-architect`)
- **Skills**: Installed to `~/.claude/skills/` (e.g., confidence-check)
- **Hooks**: Session lifecycle hooks in `src/superclaude/hooks/`
- **Settings**: Project settings in `.claude/settings.json`
- **Pytest Plugin**: Auto-loaded via entry point, provides fixtures and markers
- **MCP Servers**: 8+ servers configurable via `superclaude mcp`

## 🔧 Development Workflow

### Essential Commands

```bash
# Setup
make dev              # Install in editable mode with dev dependencies
make verify           # Verify installation (package, plugin, health)

# Testing
make test             # Run full test suite
uv run pytest tests/pm_agent/ -v              # Run specific directory
uv run pytest tests/test_file.py -v           # Run specific file
uv run pytest -m confidence_check             # Run by marker
uv run pytest --cov=superclaude               # With coverage

# Code Quality
make lint             # Run ruff linter
make format           # Format code with ruff
make doctor           # Health check diagnostics

# MCP Servers
superclaude mcp                              # Interactive install (gateway default)
superclaude mcp --list                       # List available servers
superclaude mcp --servers airis-mcp-gateway  # Install AIRIS Gateway (recommended)
superclaude mcp --servers tavily context7    # Install individual servers

# Plugin Packaging
make build-plugin            # Build plugin artefacts into dist/
make sync-plugin-repo        # Sync artefacts into ../SuperClaude_Plugin

# Maintenance
make clean            # Remove build artifacts
```

## 📦 Core Architecture

### Pytest Plugin (Auto-loaded)

Registered via `pyproject.toml` entry point, automatically available after installation.

**Fixtures**: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`

**Auto-markers**:
- Tests in `/unit/` → `@pytest.mark.unit`
- Tests in `/integration/` → `@pytest.mark.integration`

**Custom markers**: `@pytest.mark.confidence_check`, `@pytest.mark.self_check`, `@pytest.mark.reflexion`

### PM Agent - Three Core Patterns

**1. ConfidenceChecker** (src/superclaude/pm_agent/confidence.py)
- Pre-execution confidence assessment: ≥90% required, 70-89% present alternatives, <70% ask questions
- Prevents wrong-direction work, ROI: 25-250x token savings

**2. SelfCheckProtocol** (src/superclaude/pm_agent/self_check.py)
- Post-implementation evidence-based validation
- No speculation - verify with tests/docs

**3. ReflexionPattern** (src/superclaude/pm_agent/reflexion.py)
- Error learning and prevention
- Cross-session pattern matching

### Parallel Execution

**Wave → Checkpoint → Wave pattern** (src/superclaude/execution/parallel.py):
- 3.5x faster than sequential execution
- Automatic dependency analysis
- Example: [Read files in parallel] → Analyze → [Edit files in parallel]

### Slash Commands, Agents & Modes (v4.3.0)

- Install via: `pipx install superclaude && superclaude install`
- **30 Commands** installed to `~/.claude/commands/sc/` (e.g., `/sc:pm`, `/sc:research`, `/sc:implement`)
- **20 Agents** installed to `~/.claude/agents/` (e.g., `@pm-agent`, `@system-architect`, `@deep-research`)
- **7 Behavioral Modes**: Brainstorming, Business Panel, Deep Research, Introspection, Orchestration, Task Management, Token Efficiency
- **Skills**: Installable to `~/.claude/skills/` (e.g., confidence-check)

> **Note**: TypeScript plugin system planned for v5.0 ([#419](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/419))

## 🧪 Testing with PM Agent

### Example Test with Markers

```python
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    """Pre-execution confidence check - skips if < 70%"""
    context = {"test_name": "test_feature", "has_official_docs": True}
    assert confidence_checker.assess(context) >= 0.7

@pytest.mark.self_check
def test_implementation(self_check_protocol):
    """Post-implementation validation with evidence"""
    implementation = {"code": "...", "tests": [...]}
    passed, issues = self_check_protocol.validate(implementation)
    assert passed, f"Validation failed: {issues}"

@pytest.mark.reflexion
def test_error_learning(reflexion_pattern):
    """If test fails, reflexion records for future prevention"""
    pass

@pytest.mark.complexity("medium")  # simple: 200, medium: 1000, complex: 2500
def test_with_budget(token_budget):
    """Token budget allocation"""
    assert token_budget.limit == 1000
```

## 🌿 Git Workflow

**Branch structure**: `master` (production) ← `integration` (testing) ← `feature/*`, `fix/*`, `docs/*`

**Standard workflow**:
1. Create branch from `integration`: `git checkout -b feature/your-feature`
2. Develop with tests: `uv run pytest`
3. Commit: `git commit -m "feat: description"` (conventional commits)
4. Merge to `integration` → validate → merge to `master`

**Current branch**: See git status in session start output

### Parallel Development with Git Worktrees

**CRITICAL**: When running multiple Claude Code sessions in parallel, use `git worktree` to avoid conflicts.

```bash
# Create worktree for integration branch
cd ~/github/SuperClaude_Framework
git worktree add ../SuperClaude_Framework-integration integration

# Create worktree for feature branch
git worktree add ../SuperClaude_Framework-feature feature/pm-agent
```

**Benefits**:
- Run Claude Code sessions on different branches simultaneously
- No branch switching conflicts
- Independent working directories
- Parallel development without state corruption

**Usage**:
- Session A: Open `~/github/SuperClaude_Framework/` (current branch)
- Session B: Open `~/github/SuperClaude_Framework-integration/` (integration)
- Session C: Open `~/github/SuperClaude_Framework-feature/` (feature branch)

**Cleanup**:
```bash
git worktree remove ../SuperClaude_Framework-integration
```

## 📝 Key Documentation Files

**PLANNING.md** - Architecture, design principles, absolute rules
**TASK.md** - Current tasks and priorities
**KNOWLEDGE.md** - Accumulated insights and troubleshooting

Additional docs in `docs/user-guide/`, `docs/developer-guide/`, `docs/reference/`

## 💡 Core Development Principles

### 1. Evidence-Based Development
**Never guess** - verify with official docs (Context7 MCP, WebFetch, WebSearch) before implementation.

### 2. Confidence-First Implementation
Check confidence BEFORE starting: ≥90% proceed, 70-89% present alternatives, <70% ask questions.

### 3. Parallel-First Execution
Use **Wave → Checkpoint → Wave** pattern (3.5x faster). Example: `[Read files in parallel]` → Analyze → `[Edit files in parallel]`

### 4. Token Efficiency
- Simple (typo): 200 tokens
- Medium (bug fix): 1,000 tokens
- Complex (feature): 2,500 tokens
- Confidence check ROI: spend 100-200 to save 5,000-50,000

## 🔧 MCP Server Integration

**Recommended**: Use **airis-mcp-gateway** for unified MCP management.

```bash
superclaude mcp  # Interactive install, gateway is default (requires Docker)
```

**Gateway Benefits**: 60+ tools, 98% token reduction, single SSE endpoint, Web UI

**High Priority Servers** (included in gateway):
- **Tavily**: Web search (Deep Research)
- **Context7**: Official documentation (prevent hallucination)
- **Sequential**: Token-efficient reasoning (30-50% reduction)
- **Serena**: Session persistence
- **Mindbase**: Cross-session learning

**Optional**: Playwright (browser automation), Magic (UI components), Chrome DevTools (performance)

**Usage**: TypeScript plugins and Python pytest plugin can call MCP servers. Always prefer MCP tools over speculation for documentation/research.

## 🚀 Development & Installation

### Current Installation Method (v4.3.0)

**Standard Installation**:
```bash
# Option 1: pipx (recommended)
pipx install superclaude
superclaude install

# Option 2: Direct from repo
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework
./install.sh
```

**Development Mode**:
```bash
# Install in editable mode
make dev

# Run tests
make test

# Verify installation
make verify
```

### Plugin System (v5.0 - Not Yet Available)

The TypeScript plugin system (`.claude-plugin/`, marketplace) is planned for v5.0.
See `docs/plugin-reorg.md` for details.

## 📊 Package Information

**Package name**: `superclaude`
**Version**: 4.3.0
**Python**: >=3.10
**Build system**: hatchling (PEP 517)

**Entry points**:
- CLI: `superclaude` command
- Pytest plugin: Auto-loaded as `superclaude`

**Dependencies**:
- pytest>=7.0.0
- click>=8.0.0
- rich>=13.0.0

## 🔌 Claude Code Native Features (for developers)

SuperClaude extends Claude Code through its native extension points. When developing SuperClaude features, use these Claude Code capabilities:

### Extension Points We Use
- **Custom Commands** (`~/.claude/commands/sc/*.md`): 30 `/sc:*` commands
- **Custom Agents** (`~/.claude/agents/*.md`): 20 domain-specialist agents
- **Skills** (`~/.claude/skills/`): confidence-check skill
- **Settings** (`.claude/settings.json`): Permission rules, hooks
- **MCP Servers**: 8 pre-configured + AIRIS gateway
- **Pytest Plugin**: Auto-loaded via entry point

### Extension Points We Should Use More
- **Hooks** (28 events): `SessionStart`, `Stop`, `PostToolUse`, `TaskCompleted` — ideal for PM Agent auto-restore, self-check validation, and reflexion triggers
- **Skills System**: Commands should migrate to proper skills with YAML frontmatter for auto-triggering, tool restrictions, and effort overrides
- **Plan Mode**: Could integrate with confidence checks (block implementation when < 70%)
- **Settings Profiles**: Could provide recommended permission/hook configs per workflow
- **Native Session Persistence**: `--continue`/`--resume` instead of custom memory files

See `docs/user-guide/claude-code-integration.md` for the full gap analysis.
