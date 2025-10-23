# Architecture Overview

This document clarifies the **dual-component architecture** of Airiscode.

## 🏗️ Two Separate Components

Airiscode consists of **two independent components**:

### 1. Claude Code Plugin (Primary)

**Purpose**: Extend Claude Code with PM Agent capabilities

**Location**: Project root
```
.claude-plugin/    # Plugin manifest
pm/                # TypeScript source
research/
index/
commands/
hooks/
```

**Installation**:
```bash
# Project-local (recommended)
cd airiscode
claude             # Auto-detects .claude-plugin/

# Global (advanced)
make install-plugin-dev
```

**Usage**:
```bash
/pm                # PM Agent orchestration
/research "query"  # Deep web research
/index-repo        # Repository indexing
```

**Distribution**: Via Claude Code marketplace (future) or project-local detection

---

### 2. Python Package (Optional)

**Purpose**: Testing utilities and CLI tools for contributors

**Location**: `src/airiscode/`
```
src/airiscode/
├── pytest_plugin.py    # Pytest plugin (auto-loaded)
├── pm_agent/           # confidence.py, self_check.py, reflexion.py
├── execution/          # parallel.py, reflection.py
└── cli/                # main.py, doctor.py
```

**Installation**:
```bash
uv venv
source .venv/bin/activate
make dev               # uv pip install -e ".[dev]"
```

**Usage**:
```bash
uv run pytest          # Run tests
airiscode doctor       # Health check CLI
```

**Distribution**: Via PyPI (future) or local editable install

---

## ❌ Common Misconception

**WRONG**: "`make dev` installs the Claude Code plugin"

**CORRECT**: "`make dev` only installs the Python package (pytest plugin + CLI)"

### Clarification

| Component | Installation | Purpose |
|-----------|-------------|---------|
| **Claude Code Plugin** | `cd airiscode && claude` | Use PM Agent in Claude Code |
| **Python Package** | `make dev` | Run tests, contribute code |

They are **completely independent**:
- You can use the Claude Code plugin **without** installing the Python package
- The Python package is **only** for contributors who want to run tests or use CLI tools

## 📦 Package Relationships

```
┌─────────────────────────────────────────┐
│ Claude Code Plugin (TypeScript)         │
│ ├── .claude-plugin/plugin.json          │
│ ├── pm/index.ts                         │
│ ├── research/index.ts                   │
│ └── index/index.ts                      │
│                                          │
│ Installation: cd airiscode && claude    │
│ Usage: /pm, /research, /index-repo      │
└─────────────────────────────────────────┘

                  ↕ (separate)

┌─────────────────────────────────────────┐
│ Python Package (pytest + CLI)           │
│ ├── src/airiscode/pytest_plugin.py      │
│ ├── src/airiscode/pm_agent/             │
│ └── src/airiscode/cli/                  │
│                                          │
│ Installation: make dev                  │
│ Usage: uv run pytest, airiscode doctor  │
└─────────────────────────────────────────┘
```

## 🎯 When to Use What

### End Users (Use PM Agent)
→ **Claude Code Plugin only**
```bash
git clone https://github.com/agiletec-inc/airiscode.git
cd airiscode
claude
```

### Contributors (Develop/Test)
→ **Both components**
```bash
# 1. Use Claude Code plugin for development
cd airiscode
claude

# 2. Install Python package for testing
uv venv
source .venv/bin/activate
make dev
uv run pytest
```

## 📚 Official Documentation References

Based on Claude Code official documentation:

1. **Plugin Distribution** ([docs](https://docs.claude.com/ja/docs/claude-code/plugins))
   - Marketplace distribution (recommended)
   - Project-local detection (`.claude-plugin/`)
   - Manual global installation

2. **No Python Package Distribution Method**
   - Official docs do NOT mention distributing plugins as Python packages
   - Python packaging is our custom addition for development/testing

## 🚀 Future Plans

### Claude Code Plugin
- [ ] Submit to Claude Code marketplace
- [ ] Enable marketplace auto-updates
- [ ] Add more commands

### Python Package (Maybe)
- [ ] Publish to PyPI (if there's demand)
- [ ] Add more CLI tools
- [ ] Improve test coverage

But the **primary product is the Claude Code plugin**, not the Python package.
