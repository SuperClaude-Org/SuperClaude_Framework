# Repository Overview

## What this repository is

SuperClaude Framework is a Python-packaged Claude Code framework repository with several overlapping roles:
- package source tree
- CLI implementation
- pytest plugin implementation
- source definitions for commands, agents, and skills
- development mirrors for Claude Code consumption
- documentation, research, and release/process artifacts

The package metadata in `pyproject.toml` identifies:
- package name: `superclaude`
- version: `4.2.0`
- Python: `>=3.10`

## High-level repository layout

```text
SuperClaude_Framework/
├── src/                      # Canonical Python/package source
│   └── superclaude/
├── .claude/                  # Local development-facing Claude Code assets
├── tests/                    # Pytest suite
├── docs/                     # Documentation, research, generated docs
├── scripts/                  # Build and analysis scripts
├── plugins/                  # Plugin/package-related assets
├── .vendor/                  # Vendored dependencies/content
├── .dev/                     # Release/process artifacts
└── root-level project files  # README, CLAUDE.md, Makefile, pyproject.toml, etc.
```

## Top-level directories and why they matter

### `src/superclaude/`
This is the main implementation and distribution source.

Important subareas observed in the repository:
- `cli/` — CLI entry point and subcommands
- `pm_agent/` — confidence, self-check, reflexion, token budget
- `execution/` — parallel execution, reflection, self-correction support
- `commands/` — command definition markdown files
- `skills/` — skill packages and related assets
- `agents/` — agent definition source files

### `.claude/`
Project-local Claude Code assets used during development.

The repository instructions explicitly say:
- `src/superclaude/` is the source of truth
- `.claude/skills/` and `.claude/agents/` are convenience copies
- contributors should keep them in sync when working on installed-facing assets

### `tests/`
Pytest-based validation for the Python package and PM-agent patterns.

### `docs/`
A large documentation tree that already includes:
- onboarding docs
- user guides
- developer guides
- reference docs
- research notes
- generated docs
- localized user-guide variants

### `scripts/`
Operational/build/analysis utilities used by the repository.

### `.dev/`
Internal release and process artifacts. Useful for understanding recent workstreams, but not usually the first stop for code changes.

## Root-level files worth reading first

- `README.md` — public-facing project overview
- `CLAUDE.md` — repo-specific workflow rules for this repository
- `pyproject.toml` — packaging, entry points, dependencies, pytest config
- `Makefile` — main developer commands
- `CONTRIBUTING.md` — contribution guidance
- `PLANNING.md` — planning and architecture context
- `KNOWLEDGE.md` — accumulated repo insights
- `PROJECT_INDEX.md` / `PROJECT_INDEX.json` — prior generated index artifacts

## Entry points

### CLI entry point
`pyproject.toml` defines:
- console script: `superclaude = superclaude.cli.main:main`

### Pytest plugin entry point
`pyproject.toml` also defines:
- pytest11 entry point: `superclaude = superclaude.pytest_plugin`

This makes the CLI and plugin the two most important executable package entry points.

## Repository identity in one diagram

```text
                         SuperClaude_Framework
                                  |
        ---------------------------------------------------------
        |                       |                  |             |
        v                       v                  v             v
  Python package          Claude Code assets     Docs       Release/process
  src/superclaude/            .claude/           docs/         .dev/
        |
        +--> CLI
        +--> pytest plugin
        +--> PM agent patterns
        +--> commands
        +--> skills
        +--> agents
```

## Contributor takeaway

If you are unsure where to start:
- implementation truth usually lives in `src/superclaude/`
- developer workflow truth usually lives in `CLAUDE.md`, `Makefile`, and `pyproject.toml`
- higher-level context usually lives in `README.md` and `docs/`
