# Airiscode - PM Agent for Claude Code

**Confidence-driven development framework for Claude Code**

Transform Claude Code into a structured development platform through PM Agent orchestration, deep research, and repository indexing.

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/agiletec-inc/airiscode.git
cd airiscode

# Start Claude Code (auto-detected)
claude
```

That's it! PM Agent activates automatically via SessionStart hook.

## ✨ Features

### 🔍 Confidence-Driven Workflow
- **Pre-implementation confidence check**: ≥90% required before execution
- **Alternative exploration**: 70-89% confidence triggers alternative discovery
- **Clarification requests**: <70% confidence asks questions first
- **ROI**: Spend 100-200 tokens to save 5,000-50,000 tokens

### 🌐 Deep Research
- **Adaptive planning**: 3 strategies (planning-only, intent-planning, unified)
- **Multi-hop reasoning**: Up to 5 iterative searches
- **Quality scoring**: Confidence-based validation (target: 0.8)
- **Case-based learning**: Cross-session intelligence

### 📊 Repository Indexing
- **94% token reduction**: 58K → 3K tokens
- **Fast exploration**: Glob patterns, keyword search
- **Structural understanding**: Codebase architecture analysis

### ⚡ Parallel Execution
- **Wave → Checkpoint → Wave pattern**: 3.5x faster than sequential
- **Automatic dependency analysis**: Smart task orchestration
- **Example**: [Read files] → Analyze → [Edit files]

## 📦 Installation

### Recommended: Marketplace Installation (Coming Soon)

**Future**: Install via Claude Code marketplace for automatic updates and easy management.

```bash
# In Claude Code
/plugin install @airiscode/airiscode
```

### Option 1: Project-Local (For Development)

Best for plugin development and contributing to airiscode.

```bash
# Clone and start - that's it!
git clone https://github.com/agiletec-inc/airiscode.git
cd airiscode
claude
```

**Auto-configuration**:
- `.claude/settings.json` defines local marketplace
- `.claude-plugin/plugin.json` detected automatically
- PM Agent activates via SessionStart hook

**Benefits**:
- ✅ Zero install - auto-detected by Claude Code
- ✅ Hot reload - edit TypeScript, save, instant reflection
- ✅ Auto-activation - PM Agent starts on session
- ✅ Safe development - isolated from global Claude Code

### Option 2: Global Manual Installation (Advanced)

For using airiscode across all projects without cloning.

```bash
cd airiscode
make install-plugin-dev    # Install to ~/.claude/plugins/pm-agent/
# Restart Claude Code
```

**Note**: Manual updates required when new versions are released.

### Python Package (Optional - For Contributors)

**Note**: The Python package (pytest plugin + CLI) is **separate** from the Claude Code plugin.

**Only needed if**:
- Contributing to airiscode development
- Running test suite
- Using CLI tools (`airiscode doctor`)

```bash
cd airiscode

# Create virtual environment
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install Python package
make dev                   # Install in editable mode with dev dependencies

# Verify Python package (not Claude Code plugin!)
make verify                # Check package installation
uv run pytest              # Run test suite
```

**Important**: `make dev` does **NOT** install the Claude Code plugin. Use project-local or global installation for that.

### Installation Comparison

| Method | Use Case | Auto-Update | Hot Reload | Scope |
|--------|----------|-------------|------------|-------|
| **Marketplace** (future) | End users | ✅ Yes | ❌ No | Global |
| **Project-Local** | Development | ❌ No (git pull) | ✅ Yes | Project |
| **Global Manual** | Advanced users | ❌ No (manual) | ❌ No | Global |

## 🎯 Usage

### Three Plugin Commands

```bash
# 1. PM Agent - Confidence-driven orchestration
/pm

# 2. Deep Research - Autonomous web research
/research "latest AI developments 2024"

# 3. Repository Indexing - 94% token reduction
/index-repo
```

### Automatic PM Agent Activation

PM Agent activates automatically on session start via SessionStart hook:

```
✅ PM Agent ready to accept tasks

Core Capabilities:
- 🔍 Pre-implementation confidence check (≥90% required)
- ⚡ Parallel investigation and execution
- 📊 Token-budget-aware operations

Usage: Assign tasks directly - PM Agent will orchestrate
```

## 🏗️ Architecture

### Dual-Language Design

```
TypeScript Plugins          Python Package
├── pm/                    ├── pm_agent/
│   ├── index.ts           │   ├── confidence.py
│   └── confidence.ts      │   ├── self_check.py
├── research/              │   └── reflexion.py
│   └── index.ts           ├── execution/
├── index/                 │   ├── parallel.py
│   └── index.ts           │   └── reflection.py
└── commands/              └── cli/
    ├── pm.md                  ├── main.py
    ├── research.md            └── doctor.py
    └── index-repo.md
```

### Core Patterns

**1. ConfidenceChecker** - Pre-execution assessment
```python
@pytest.mark.confidence_check
def test_feature(confidence_checker):
    context = {"test_name": "test_feature", "has_official_docs": True}
    assert confidence_checker.assess(context) >= 0.7
```

**2. SelfCheckProtocol** - Post-implementation validation
```python
@pytest.mark.self_check
def test_implementation(self_check_protocol):
    passed, issues = self_check_protocol.validate(implementation)
    assert passed
```

**3. ReflexionPattern** - Error learning
```python
@pytest.mark.reflexion
def test_error_learning(reflexion_pattern):
    # If test fails, reflexion records for future prevention
    pass
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific tests
uv run pytest tests/pm_agent/ -v
uv run pytest -m confidence_check

# With coverage
uv run pytest --cov=airiscode
```

## 🔧 Development

```bash
# Setup
make dev              # Install in editable mode
make verify           # Verify installation

# Code quality
make lint             # Run ruff linter
make format           # Format code
make doctor           # Health check

# Plugin development
vim pm/index.ts       # Edit plugin (hot reload enabled)
make reinstall-plugin-dev  # Update global installation
```

## 🌐 MCP Server Integration

Airiscode integrates with multiple MCP servers via **airis-mcp-gateway**:

- **Tavily**: Web search (Deep Research)
- **Context7**: Official documentation (prevent hallucination)
- **Sequential**: Token-efficient reasoning (30-50% reduction)
- **Serena**: Session persistence
- **Mindbase**: Cross-session learning

## 📚 Documentation

- **CLAUDE.md**: Developer guide for Claude Code
- **pyproject.toml**: Package configuration
- **Makefile**: Development commands

## 🤝 Contributing

Contributions welcome! This project follows:
- Conventional commits (`feat:`, `fix:`, `docs:`)
- Branch structure: `main` ← `develop` ← `feature/*`
- UV for Python operations

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Credits

Based on [SuperClaude Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) by SuperClaude Team.

## 📊 Stats

| Metric | Value |
|--------|-------|
| **Token Reduction** | 94% (58K → 3K) |
| **Confidence Threshold** | ≥90% |
| **Speed Improvement** | 3.5x (parallel vs sequential) |
| **ROI** | 25-250x token savings |

## 🔗 Links

- **Homepage**: https://github.com/agiletec-inc/airiscode
- **Upstream**: https://github.com/SuperClaude-Org/SuperClaude_Framework
- **Issues**: https://github.com/agiletec-inc/airiscode/issues

---

**Built by Agiletec Inc.** | Powered by Claude Code
