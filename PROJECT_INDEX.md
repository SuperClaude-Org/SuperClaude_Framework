# Project Index: SuperClaude Framework

**Generated**: 2025-10-29
**Version**: 0.4.0
**Description**: AI-enhanced development framework for Claude Code - pytest plugin with specialized commands

---

## 📁 Project Structure

```
SuperClaude_Framework/
├── src/superclaude/          # Python package (3,002 LOC)
│   ├── cli/                  # CLI commands (main.py, doctor.py, install_skill.py)
│   ├── pm_agent/             # PM Agent core (confidence.py, self_check.py, reflexion.py, token_budget.py)
│   ├── execution/            # Execution patterns (parallel.py, reflection.py, self_correction.py)
│   ├── pytest_plugin.py      # Auto-loaded pytest integration
│   └── skills/               # TypeScript skills (confidence-check)
├── tests/                    # Test suite (7 files)
│   ├── pm_agent/             # PM Agent tests (confidence, self_check, reflexion)
│   └── conftest.py           # Shared fixtures
├── docs/                     # Documentation (90+ files)
│   ├── user-guide/           # User guides (en, ja, kr, zh)
│   ├── developer-guide/      # Developer documentation
│   ├── reference/            # API reference & examples
│   ├── architecture/         # Architecture decisions
│   └── research/             # Research findings
├── scripts/                  # Analysis tools (workflow metrics, A/B testing)
├── setup/                    # Setup components & utilities
├── skills/                   # Claude Code skills
│   └── confidence-check/     # Confidence check skill (SKILL.md, confidence.ts)
├── .claude/                  # Claude Code configuration
│   ├── settings.json         # Plugin settings
│   └── skills/               # Installed skills
└── .github/                  # GitHub workflows & templates
```

---

## 🚀 Entry Points

### CLI
- **Command**: `superclaude` (installed via pip/uv)
- **Source**: `src/superclaude/cli/main.py:main`
- **Purpose**: CLI interface for SuperClaude operations

### Pytest Plugin
- **Auto-loaded**: Yes (via `pyproject.toml` entry point)
- **Source**: `src/superclaude/pytest_plugin.py`
- **Purpose**: PM Agent fixtures and test automation

### Skills
- **Confidence Check**: `.claude/skills/confidence-check/confidence.ts`
- **Purpose**: Pre-implementation confidence assessment

---

## 📦 Core Modules

### PM Agent (src/superclaude/pm_agent/)
Core patterns for AI-enhanced development:

#### ConfidenceChecker (`confidence.py`)
- **Purpose**: Pre-execution confidence assessment
- **Threshold**: ≥90% required, 70-89% present alternatives, <70% ask questions
- **ROI**: 25-250x token savings
- **Checks**: No duplication, architecture compliance, official docs, OSS references, root cause identification

#### SelfCheckProtocol (`self_check.py`)
- **Purpose**: Post-implementation evidence-based validation
- **Approach**: No speculation - verify with tests/docs
- **Pattern**: Assert → Verify → Report

#### ReflexionPattern (`reflexion.py`)
- **Purpose**: Error learning and prevention
- **Features**: Cross-session pattern matching, failure analysis
- **Storage**: Session-persistent learning

#### TokenBudgetManager (`token_budget.py`)
- **Purpose**: Token allocation and tracking
- **Levels**: Simple (200), Medium (1,000), Complex (2,500)
- **Enforcement**: Budget-aware execution

### Execution Patterns (src/superclaude/execution/)

#### Parallel Execution (`parallel.py`)
- **Pattern**: Wave → Checkpoint → Wave
- **Performance**: 3.5x faster than sequential
- **Features**: Automatic dependency analysis, concurrent tool calls
- **Example**: [Read files in parallel] → Analyze → [Edit files in parallel]

#### Reflection (`reflection.py`)
- **Purpose**: Post-execution analysis and improvement
- **Integration**: Works with ReflexionPattern

#### Self-Correction (`self_correction.py`)
- **Purpose**: Automated error detection and correction
- **Strategy**: Iterative refinement

### CLI Commands (src/superclaude/cli/)

#### main.py
- **Exports**: `main()` - CLI entry point
- **Framework**: Click-based CLI
- **Commands**: install-skill, doctor (health check)

#### doctor.py
- **Purpose**: Health check diagnostics
- **Checks**: Package installation, pytest plugin, skills availability

#### install_skill.py
- **Purpose**: Install SuperClaude skills to Claude Code
- **Target**: `~/.claude/skills/`

---

## 🔧 Configuration

### Python Package
- **File**: `pyproject.toml`
- **Build**: hatchling (PEP 517)
- **Python**: ≥3.10
- **Dependencies**: pytest ≥7.0.0, click ≥8.0.0, rich ≥13.0.0

### NPM Wrapper
- **File**: `package.json`
- **Package**: `@bifrost_inc/superclaude`
- **Version**: 4.1.5
- **Purpose**: Cross-platform installation wrapper

### Claude Code
- **File**: `.claude/settings.json`
- **Purpose**: Plugin and marketplace settings

---

## 📚 Documentation

### Key Files
- **CLAUDE.md**: Instructions for Claude Code integration
- **README.md**: Project overview and quick start
- **CONTRIBUTING.md**: Contribution guidelines
- **CHANGELOG.md**: Version history
- **AGENTS.md**: Agent architecture documentation

### User Guides (docs/user-guide/)
- **commands.md**: Available commands
- **agents.md**: Agent usage patterns
- **flags.md**: CLI flags and options
- **modes.md**: Operation modes
- **session-management.md**: Session persistence
- **mcp-servers.md**: MCP server integration

### Developer Guides (docs/developer-guide/)
- **contributing-code.md**: Code contribution workflow
- **technical-architecture.md**: Architecture overview
- **testing-debugging.md**: Testing strategies

### Reference (docs/reference/)
- **basic-examples.md**: Usage examples
- **advanced-patterns.md**: Advanced implementation patterns
- **troubleshooting.md**: Common issues and solutions
- **diagnostic-reference.md**: Health check diagnostics

### Architecture (docs/architecture/)
- **MIGRATION_TO_CLEAN_ARCHITECTURE.md**: Architecture evolution
- **PHASE_1_COMPLETE.md**: Phase 1 migration results
- **PM_AGENT_COMPARISON.md**: PM Agent vs alternatives
- **CONTEXT_WINDOW_ANALYSIS.md**: Token efficiency analysis

### Research (docs/research/)
- **llm-agent-token-efficiency-2025.md**: Token optimization research
- **reflexion-integration-2025.md**: Reflexion pattern integration
- **parallel-execution-complete-findings.md**: Parallel execution results
- **pm_agent_roi_analysis_2025-10-21.md**: ROI analysis

---

## 🧪 Test Coverage

### Structure
- **Unit tests**: 7 files in `tests/pm_agent/`
- **Test framework**: pytest ≥7.0.0
- **Coverage tool**: pytest-cov ≥4.0.0
- **Markers**: confidence_check, self_check, reflexion, unit, integration

### Test Files
1. `test_confidence_check.py` - ConfidenceChecker tests
2. `test_self_check_protocol.py` - SelfCheckProtocol tests
3. `test_reflexion_pattern.py` - ReflexionPattern tests
4. `test_pytest_plugin.py` - Pytest plugin tests
5. `conftest.py` - Shared fixtures

### Running Tests
```bash
# All tests
uv run pytest

# Specific directory
uv run pytest tests/pm_agent/ -v

# By marker
uv run pytest -m confidence_check

# With coverage
uv run pytest --cov=superclaude
```

---

## 🔗 Key Dependencies

### Core Dependencies (pyproject.toml)
- **pytest** ≥7.0.0 - Testing framework
- **click** ≥8.0.0 - CLI framework
- **rich** ≥13.0.0 - Terminal formatting

### Dev Dependencies
- **pytest-cov** ≥4.0.0 - Coverage reporting
- **pytest-benchmark** ≥4.0.0 - Performance testing
- **scipy** ≥1.10.0 - A/B testing (statistical analysis)
- **ruff** ≥0.1.0 - Linting and formatting
- **mypy** ≥1.0 - Type checking

---

## 📝 Quick Start

### Installation
```bash
# Install with UV (recommended)
uv pip install superclaude

# Or with pip
pip install superclaude

# Development mode
make install
```

### Usage
```bash
# CLI commands
superclaude --version
superclaude install-skill confidence-check

# Health check
make doctor

# Run tests
make test

# Format and lint
make format
make lint
```

### Pytest Integration
```python
# Automatically available after installation
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    context = {"has_official_docs": True}
    assert confidence_checker.assess(context) >= 0.9
```

---

## 🌿 Git Workflow

**Branch structure**: `master` (production) ← `integration` (testing) ← `feature/*`, `fix/*`, `docs/*`

**Current branch**: `next`

---

## 🎯 Token Efficiency

### Index Performance
- **Before**: 58,000 tokens (reading all files every session)
- **After**: 3,000 tokens (reading this index)
- **Reduction**: 94% (55,000 tokens saved per session)

### PM Agent ROI
- **Confidence check**: 100-200 tokens → saves 5,000-50,000 tokens
- **ROI**: 25-250x token savings
- **Break-even**: 1 failed implementation prevented

---

## 📊 Project Stats

- **Python source**: 3,002 lines of code
- **Test files**: 7 files
- **Documentation**: 90+ markdown files
- **Supported Python**: 3.10, 3.11, 3.12
- **License**: MIT
- **Contributors**: 3 core maintainers

---

## 🔌 MCP Server Integration

Integrates with multiple MCP servers via **airis-mcp-gateway**:

- **Tavily**: Web search (Deep Research)
- **Context7**: Official documentation (prevent hallucination)
- **Sequential**: Token-efficient reasoning (30-50% reduction)
- **Serena**: Session persistence
- **Mindbase**: Cross-session learning

---

## 🎨 Project Principles

1. **Evidence-Based Development** - Never guess, verify with official docs
2. **Confidence-First Implementation** - Check confidence BEFORE starting
3. **Parallel-First Execution** - Use Wave → Checkpoint → Wave (3.5x faster)
4. **Token Efficiency** - Optimize for minimal token usage
5. **Test-Driven Development** - Tests first, implementation second

---

**For detailed documentation**: See `docs/` directory or visit [GitHub repository](https://github.com/SuperClaude-Org/SuperClaude_Framework)
