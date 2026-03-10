# Contributor Workflow Guide

## Core workflow rule

For this repository, prefer these sources when deciding how to work:
1. `CLAUDE.md`
2. `pyproject.toml`
3. `Makefile`
4. current code under `src/superclaude/`

These give the most concrete, current guidance for contributor activity.

## Python environment rule

The repository-specific instructions say to use `uv` for Python operations.

Examples from repo guidance:

```bash
uv run pytest
uv run pytest tests/pm_agent/ -v
uv pip install package
uv run python script.py
```

## Everyday developer commands

### Setup and verification
```bash
make dev
make verify
```

### Testing
```bash
make test
uv run pytest tests/pm_agent/ -v
uv run pytest tests/test_file.py -v
uv run pytest -m confidence_check
uv run pytest --cov=superclaude
```

### Quality
```bash
make lint
make format
make doctor
```

### Sync
```bash
make sync-dev
make verify-sync
```

### Plugin packaging
```bash
make build-plugin
make sync-plugin-repo
```

## Contributor workflow diagram

```text
Read context
  README.md + CLAUDE.md + pyproject.toml + Makefile
        ↓
Find real implementation surface
  src/superclaude/... or docs/... depending on task
        ↓
Make focused changes
        ↓
Run relevant validation
  tests / lint / verify-sync / doctor
        ↓
Check generated-vs-source relationships
        ↓
Prepare commit or follow-up changes
```

## Working with source-of-truth vs dev mirrors

### Source-of-truth
Use `src/superclaude/` for distributable components.

### Dev mirrors
Use `.claude/` only with awareness that it is a local-development-facing mirror for Claude Code.

### Practical rule
If you edit framework components in `.claude/` during local iteration, the repository guidance says those changes should be copied back to `src/superclaude/` and then verified for sync.

## How to choose where to edit

### If the change is about package behavior
Start in:
- `src/superclaude/cli/`
- `src/superclaude/pytest_plugin.py`
- `src/superclaude/pm_agent/`
- `src/superclaude/execution/`

### If the change is about framework content/prompt behavior
Start in:
- `src/superclaude/commands/`
- `src/superclaude/skills/`
- agent source assets in `src/superclaude/agents/`

### If the change is about contributor understanding
Start in:
- `README.md`
- `docs/`
- generated docs under `docs/generated/` when the task explicitly calls for generated artifacts

## Validation strategy

Use the smallest validation set that directly proves the changed surface is correct.

Examples:
- changed pytest integration → run relevant `uv run pytest ...`
- changed package/CLI behavior → run relevant tests and `make doctor` or `make verify`
- changed distributable content mirrors → run `make verify-sync`
- changed docs only → verify links, claims, and referenced paths against the repo

## Important contributor cautions

### 1. Avoid assuming older docs are fully current
Some developer docs in the repository reflect earlier architectural framing. When there is tension between older prose and the actual current tree, prefer the current source code and active repo instructions.

### 2. Keep generated docs in generated locations
For generated documentation work in this repo, output belongs under `docs/generated/`.

### 3. Prefer evidence over inference
Before documenting a subsystem:
- inspect the actual path
- inspect package metadata or symbols where relevant
- align terminology with what the repo currently contains

## Suggested onboarding path for new contributors

### Day 1: basic orientation
- read `README.md`
- read `CLAUDE.md`
- skim `pyproject.toml`
- skim `Makefile`

### Day 2: implementation surfaces
- inspect `src/superclaude/cli/main.py`
- inspect `src/superclaude/pytest_plugin.py`
- inspect `src/superclaude/pm_agent/`
- inspect `src/superclaude/commands/` and `src/superclaude/skills/`

### Day 3: process and deeper context
- browse `docs/developer-guide/`
- browse `docs/reference/`
- browse `docs/research/` only as needed for historical context

## Contributor checklist

Before marking work complete, ask:
- Did I edit the correct source-of-truth location?
- If I touched mirrored assets, did I account for sync?
- Did I validate the exact changed surface?
- Did I keep generated output under `docs/generated/` when required?
- Are my documentation claims grounded in current repository structure?
