# CLAUDE.md

Project-specific instructions for Claude Code when working with SuperClaude Framework.

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

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_cli_smoke.py -v

# With coverage
uv run pytest --cov=superclaude --cov-report=html
```

### Code Quality

```bash
# Linting (if configured)
uv run ruff check .

# Type checking (if configured)
uv run mypy superclaude/

# Formatting (if configured)
uv run ruff format .
```

## 📦 Component Architecture

SuperClaude uses **Responsibility-Driven Design**. Each component has a single, clear responsibility:

- **knowledge_base**: Framework knowledge initialization
- **behavior_modes**: Execution mode definitions
- **agent_personas**: AI agent personality definitions
- **slash_commands**: CLI command registration
- **mcp_integration**: External tool integration

## 🚀 Contributing

When making changes:

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes with tests: `uv run pytest`
3. Commit with conventional commits: `git commit -m "feat: description"`
4. Push and create PR: Small, reviewable PRs preferred

## 📝 Documentation

- Root documents: `PLANNING.md`, `KNOWLEDGE.md`, `TASK.md`
- User guides: `docs/user-guide/`
- Development docs: `docs/Development/`
- Research reports: `docs/research/`

## 🔗 Related

- Global rules: `~/.claude/CLAUDE.md` (workspace-level)
- MCP servers: Unified gateway via `airis-mcp-gateway`
- Framework docs: Auto-installed to `~/.claude/superclaude/`
