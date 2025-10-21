# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🐍 Python Environment Rules

**CRITICAL**: This project uses **UV** for all Python operations.

### Required Commands

```bash
# ❌ WRONG - Never use these
python -m pytest
pip install package
python script.py

# ✅ CORRECT - Always use UV
uv run pytest
uv pip install package
uv run python script.py
```

### Why UV?

- **Fast**: 10-100x faster than pip
- **Reliable**: Lock file ensures reproducibility
- **Clean**: No system Python pollution
- **Standard**: Project convention for consistency

### Common Operations

```bash
# Run tests
uv run pytest tests/ -v

# Install dependencies
uv pip install -r requirements.txt

# Run specific script
uv run python scripts/analyze_workflow_metrics.py

# Create virtual environment (if needed)
uv venv
```

### Integration with Docker

When using Docker for development:
```bash
# Inside Docker container
docker compose exec workspace uv run pytest
```

## 📂 Project Structure

```
SuperClaude_Framework/
├── superclaude/           # Framework source
│   ├── commands/          # Slash commands
│   ├── agents/            # Agent personas
│   ├── modes/             # Behavior modes
│   ├── framework/         # Core principles/rules/flags
│   ├── business/          # Business analysis patterns
│   └── research/          # Research configurations
├── setup/                 # Installation system
│   ├── components/        # Installable components
│   │   ├── knowledge_base.py       # Framework knowledge
│   │   ├── behavior_modes.py       # Mode definitions
│   │   ├── agent_personas.py       # Agent definitions
│   │   ├── slash_commands.py       # Command registration
│   │   └── mcp_integration.py      # External tool integration
│   └── core/              # Installation logic
└── tests/                 # Test suite
```

## 🔧 Development Workflow

### Makefile Commands (Recommended)

```bash
# Development setup
make dev              # Install in editable mode with [dev] dependencies (RECOMMENDED)
make verify           # Verify installation health (package, version, plugin, doctor)

# Testing
make test             # Run full test suite with pytest
make test-plugin      # Verify pytest plugin auto-discovery

# Code quality
make lint             # Run ruff linter
make format           # Format code with ruff

# Maintenance
make doctor           # Run health check diagnostics
make clean            # Remove build artifacts and caches
make translate        # Translate README to zh/ja (requires neural-cli)
```

### Running Tests Directly

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/pm_agent/test_confidence_check.py -v

# By directory
uv run pytest tests/pm_agent/ -v

# By marker
uv run pytest -m confidence_check
uv run pytest -m "unit and not integration"

# With coverage
uv run pytest --cov=superclaude --cov-report=html
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking (if configured)
uv run mypy superclaude/
```

## 📦 Core Architecture

### Pytest Plugin System (Auto-loaded)

SuperClaude includes an **auto-loaded pytest plugin** registered via entry points in pyproject.toml:66-67:

```toml
[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"
```

**Provides:**
- Custom fixtures: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`
- Auto-markers: Tests in `/unit/` → `@pytest.mark.unit`, `/integration/` → `@pytest.mark.integration`
- Custom markers: `@pytest.mark.confidence_check`, `@pytest.mark.self_check`, `@pytest.mark.reflexion`
- PM Agent integration for test lifecycle hooks

### PM Agent - Three Core Patterns

Located in `src/superclaude/pm_agent/`:

**1. ConfidenceChecker (Pre-execution)**
- Prevents wrong-direction execution by assessing confidence BEFORE starting
- Token budget: 100-200 tokens
- ROI: 25-250x token savings when stopping wrong implementations
- Confidence levels:
  - High (≥90%): Proceed immediately
  - Medium (70-89%): Present alternatives
  - Low (<70%): STOP → Ask specific questions

**2. SelfCheckProtocol (Post-implementation)**
- Evidence-based validation after implementation
- No speculation allowed - verify with actual tests/docs
- Ensures implementation matches requirements

**3. ReflexionPattern (Error learning)**
- Records failures for future prevention
- Pattern matching for similar errors
- Cross-session learning and improvement

### Module Structure

```
src/superclaude/
├── __init__.py              # Exports: ConfidenceChecker, SelfCheckProtocol, ReflexionPattern
├── pytest_plugin.py         # Auto-loaded pytest integration (fixtures, hooks, markers)
├── pm_agent/                # PM Agent core (confidence, self-check, reflexion)
├── cli/                     # CLI commands (main, doctor, install_skill)
└── execution/               # Execution patterns (parallel, reflection, self_correction)
```

### Parallel Execution Engine

Located in `src/superclaude/execution/parallel.py`:

- **Automatic parallelization**: Analyzes task dependencies and executes independent operations concurrently
- **Wave → Checkpoint → Wave pattern**: 3.5x faster than sequential execution
- **Dependency graph**: Topological sort for optimal grouping
- **ThreadPoolExecutor**: Concurrent execution with result aggregation

Example pattern:
```python
# Wave 1: Read files in parallel
tasks = [read_file1, read_file2, read_file3]

# Checkpoint: Analyze results

# Wave 2: Edit files in parallel based on analysis
tasks = [edit_file1, edit_file2, edit_file3]
```

### Component Responsibility

- **knowledge_base**: Framework knowledge initialization
- **behavior_modes**: Execution mode definitions
- **agent_personas**: AI agent personality definitions
- **slash_commands**: CLI command registration
- **mcp_integration**: External tool integration

## 🧪 Testing with PM Agent Markers

### Custom Pytest Markers

```python
# Pre-execution confidence check (skips if confidence < 70%)
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    context = {"test_name": "test_feature", "has_official_docs": True}
    assert confidence_checker.assess(context) >= 0.7

# Post-implementation validation with evidence requirement
@pytest.mark.self_check
def test_implementation(self_check_protocol):
    implementation = {"code": "...", "tests": [...]}
    passed, issues = self_check_protocol.validate(implementation)
    assert passed, f"Validation failed: {issues}"

# Error learning and prevention
@pytest.mark.reflexion
def test_error_prone_feature(reflexion_pattern):
    # If this test fails, reflexion records the error for future prevention
    pass

# Token budget allocation (simple: 200, medium: 1000, complex: 2500)
@pytest.mark.complexity("medium")
def test_with_budget(token_budget):
    assert token_budget.limit == 1000
```

### Available Fixtures

From `src/superclaude/pytest_plugin.py`:

- `confidence_checker` - Pre-execution confidence assessment
- `self_check_protocol` - Post-implementation validation
- `reflexion_pattern` - Error learning pattern
- `token_budget` - Token allocation management
- `pm_context` - PM Agent context (memory directory structure)

## 🌿 Git Workflow

### Branch Strategy

```
master          # Production-ready releases
├── integration # Integration testing branch (current)
    ├── feature/*       # Feature development
    ├── fix/*           # Bug fixes
    └── docs/*          # Documentation updates
```

**Workflow:**
1. Create feature branch from `integration`: `git checkout -b feature/your-feature`
2. Develop with tests: `uv run pytest`
3. Commit with conventional commits: `git commit -m "feat: description"`
4. Merge to `integration` for integration testing
5. After validation: `integration` → `master`

**Current branch:** `integration` (see gitStatus above)

## 🚀 Contributing

When making changes:

1. Create feature branch from `integration`
2. Make changes with tests (maintain coverage)
3. Commit with conventional commits (feat:, fix:, docs:, refactor:, test:)
4. Merge to `integration` for integration testing
5. Small, reviewable PRs preferred

## 📝 Essential Documentation

**Read these files IN ORDER at session start:**

1. **PLANNING.md** - Architecture, design principles, absolute rules
2. **TASK.md** - Current tasks and priorities
3. **KNOWLEDGE.md** - Accumulated insights and troubleshooting

These documents are the **source of truth** for development standards.

**Additional Resources:**
- User guides: `docs/user-guide/`
- Development docs: `docs/Development/`
- Research reports: `docs/research/`

## 💡 Core Development Principles

From KNOWLEDGE.md and PLANNING.md:

### 1. Evidence-Based Development
- **Never guess** - verify with official docs (Context7 MCP, WebFetch, WebSearch)
- Example: Don't assume port configuration - check official documentation first
- Prevents wrong-direction implementations

### 2. Token Efficiency
- Every operation has a token budget:
  - Simple (typo fix): 200 tokens
  - Medium (bug fix): 1,000 tokens
  - Complex (feature): 2,500 tokens
- Confidence check ROI: Spend 100-200 to save 5,000-50,000

### 3. Parallel-First Execution
- **Wave → Checkpoint → Wave** pattern (3.5x faster)
- Good: `[Read file1, Read file2, Read file3]` → Analyze → `[Edit file1, Edit file2, Edit file3]`
- Bad: Sequential reads then sequential edits

### 4. Confidence-First Implementation
- Check confidence BEFORE implementation, not after
- ≥90%: Proceed immediately
- 70-89%: Present alternatives
- <70%: STOP → Ask specific questions

## 🔧 MCP Server Integration

This framework integrates with multiple MCP servers:

**Priority Servers:**
- **Context7**: Official documentation (prevent hallucination)
- **Sequential**: Complex analysis and multi-step reasoning
- **Tavily**: Web search for Deep Research

**Optional Servers:**
- **Serena**: Session persistence and memory
- **Playwright**: Browser automation testing
- **Magic**: UI component generation

**Always prefer MCP tools over speculation** when documentation or research is needed.

## 🔗 Related

- Global rules: `~/.claude/CLAUDE.md` (workspace-level)
- MCP servers: Unified gateway via `airis-mcp-gateway`
- Framework docs: Auto-installed to `~/.claude/superclaude/`
