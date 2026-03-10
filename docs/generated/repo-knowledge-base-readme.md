# SuperClaude Framework Repository Knowledge Base

## What this repository is

SuperClaude Framework is a Python-packaged framework for Claude Code that combines:
- a CLI entry point (`superclaude`)
- an auto-loaded pytest plugin
- distributable slash commands, agents, and skills
- project documentation and research artifacts

The package metadata defines the project as `superclaude` version `4.2.0` with Python `>=3.10` in `pyproject.toml`.

## Primary entry points

### CLI
- Entry point: `superclaude`
- Defined in: `pyproject.toml`
- Implementation: `src/superclaude/cli/main.py`

The CLI handles installation, updates, doctor/health checks, skill installation, and MCP-related workflows.

### Pytest plugin
- Entry point group: `pytest11`
- Registered as: `superclaude`
- Implementation: `src/superclaude/pytest_plugin.py`

The plugin exposes PM-agent-oriented fixtures and markers used by the test suite.

## Repository layout

```text
SuperClaude_Framework/
├── src/superclaude/         # Source of truth for distributable framework components
├── .claude/                 # Development copies used directly by Claude Code in this repo
├── tests/                   # Pytest suite
├── docs/                    # User, developer, reference, architecture, research, and generated docs
├── scripts/                 # Build, analysis, and maintenance scripts
├── plugins/                 # Plugin-related assets included in packaging
├── .vendor/                 # Vendored external content, including skill-related assets
├── .dev/                    # Release/process artifacts and internal workflow materials
└── root *.md files          # High-signal project guidance and contributor context
```

## Core source areas

### `src/superclaude/`
Canonical source tree for packaged and installable framework assets.

Important subareas:
- `src/superclaude/cli/` — Click-based CLI commands and installers
- `src/superclaude/pm_agent/` — Confidence, self-check, reflexion, and related PM-agent patterns
- `src/superclaude/execution/` — Execution support such as parallel/reflection workflows
- `src/superclaude/agents/` — Agent definition source files
- `src/superclaude/skills/` — Skill packages and supporting content
- `src/superclaude/commands/` — Slash command source files
- `src/superclaude/pytest_plugin.py` — pytest integration

### `.claude/`
Local development copy of Claude Code-facing assets.

The repository guidance states:
- `src/superclaude/` is the source of truth
- `.claude/skills/` and `.claude/agents/` are convenience copies for development
- changes should ultimately be kept in sync between `src/superclaude/` and `.claude/`

## Key architectural concepts

### 1. Context-oriented framework
The project documentation describes SuperClaude as a framework that enhances Claude Code through behavioral/context files, commands, agents, skills, and MCP integrations.

### 2. PM Agent patterns
The repository guidance highlights three core PM-agent patterns:
- `ConfidenceChecker`
- `SelfCheckProtocol`
- `ReflexionPattern`

These live under `src/superclaude/pm_agent/` and are central to the repo’s evidence-first workflow.

### 3. Parallel-first execution
The repo guidance also emphasizes a “Wave → Checkpoint → Wave” execution pattern, with related code under `src/superclaude/execution/`.

## Development workflow

The project-specific guidance in `CLAUDE.md` says Python operations should use `uv`.

Common commands:

```bash
# setup
make dev
make verify

# testing
make test
uv run pytest tests/pm_agent/ -v
uv run pytest tests/test_file.py -v
uv run pytest -m confidence_check
uv run pytest --cov=superclaude

# quality
make lint
make format
make doctor

# sync development copies
make sync-dev
make verify-sync

# plugin packaging
make build-plugin
make sync-plugin-repo
```

## Documentation map

The `docs/` tree is broad and already contains multiple documentation layers:
- `docs/getting-started/` — onboarding and installation
- `docs/user-guide/` — commands, modes, agents, flags, MCP usage
- `docs/developer-guide/` — architecture, testing, contribution guidance
- `docs/reference/` — examples, troubleshooting, reference material
- `docs/architecture/` — architecture decisions and phase docs
- `docs/research/` — research and investigation outputs
- `docs/generated/` — generated documentation artifacts
- localized user guides under `docs/user-guide-zh/`, `docs/user-guide-jp/`, and `docs/user-guide-kr/`

## Important root-level files

High-value files for orientation:
- `README.md` — public project overview and installation guidance
- `CLAUDE.md` — repository-specific instructions for Claude Code work in this repo
- `PLANNING.md` — architecture and design guidance
- `KNOWLEDGE.md` — accumulated project insights
- `CONTRIBUTING.md` — contributor workflow
- `CHANGELOG.md` — release history
- `PROJECT_INDEX.md` / `PROJECT_INDEX.json` — prior indexing artifacts
- `Makefile` — primary developer workflow commands
- `pyproject.toml` — package metadata, dependencies, pytest config, entry points

## Tests and quality

The Python test suite lives under `tests/` and uses pytest configuration from `pyproject.toml`.

Observed pytest markers include:
- `unit`
- `integration`
- `confidence_check`
- `self_check`
- `reflexion`
- several diagnostic and performance-oriented markers

Code quality tooling configured in the repository includes:
- Ruff
- mypy
- Black configuration
- coverage settings

## Installation model

Current stable packaging is Python-based:
- `pipx install superclaude`
- `superclaude install`

The repository README also documents direct Git-based installation via `./install.sh`.

## Documentation constraints for this task

Per the active repository/user instructions, generated documentation should be written under `docs/generated/`. This file follows that rule.

## Suggested reading order for maintainers

1. `README.md`
2. `CLAUDE.md`
3. `pyproject.toml`
4. `Makefile`
5. `src/superclaude/cli/main.py`
6. `src/superclaude/pytest_plugin.py`
7. `src/superclaude/pm_agent/`
8. `docs/developer-guide/` and `docs/reference/`

## Summary

If you need to understand this repository quickly:
- start with `README.md` for the public product story
- use `CLAUDE.md` for repo-specific workflow rules
- treat `src/superclaude/` as the canonical implementation and distribution source
- treat `.claude/` as the repo-local development mirror for Claude Code assets
- use `docs/` for deeper architecture, reference, and research context
