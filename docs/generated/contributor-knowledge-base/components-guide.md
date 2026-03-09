# Components Guide

## Component map

This guide summarizes the most important contributor-relevant components in the current repository.

```text
src/superclaude/
├── cli/             # Click CLI + workflow subsystems
├── pytest_plugin.py # Pytest integration entry point
├── pm_agent/        # Confidence, self-check, reflexion, token budget
├── execution/       # Parallel/reflection/self-correction helpers
├── commands/        # Markdown command assets
├── skills/          # Skill packages and protocol bundles
└── agents/          # Agent definition source assets
```

## CLI subsystem

### Primary file
- `src/superclaude/cli/main.py`

### Top-level commands observed
- `main`
- `install`
- `mcp`
- `update`
- `install_skill`
- `doctor`
- `version`

### Important CLI subpackages

#### `src/superclaude/cli/sprint/`
Contains sprint-oriented operational code such as:
- config
- models
- commands
- executor
- monitor
- diagnostics
- tui
- tmux integration
- KPI/logging helpers

#### `src/superclaude/cli/roadmap/`
Contains roadmap-related models, prompts, executors, commands, and validation helpers.

#### `src/superclaude/cli/cleanup_audit/`
Contains audit-oriented command, executor, model, prompt, diagnostics, process, and TUI support.

#### `src/superclaude/cli/pipeline/`
Contains pipeline analysis and verification modules such as:
- models
- executor
- process
- guard/dataflow/invariant passes
- conflict detection/review
- verification emission
- trailing gate logic

#### `src/superclaude/cli/audit/`
Contains granular audit support modules such as:
- classification
- validation
- duplication
- dead code
- dependency graph
- checkpoint/resume
- report depth/completeness
- artifact emission
- orchestration helpers

### Contributor insight
The CLI subtree is a major implementation surface. If you are touching workflow orchestration, validation, or analysis capabilities, this is likely where the real code changes belong.

## Pytest plugin subsystem

### Primary file
- `src/superclaude/pytest_plugin.py`

### Observed responsibilities
- pytest configuration
- runtime setup hooks
- report hooks
- collection behavior
- exposure of PM-agent fixtures

### Observed fixtures/helpers
- `confidence_checker`
- `self_check_protocol`
- `reflexion_pattern`
- `token_budget`
- `pm_context`

### Contributor insight
If a change should affect test-time behavior, markers, or framework fixtures, inspect the pytest plugin before assuming the change belongs somewhere else.

## PM-agent subsystem

### Files
- `src/superclaude/pm_agent/confidence.py`
- `src/superclaude/pm_agent/self_check.py`
- `src/superclaude/pm_agent/reflexion.py`
- `src/superclaude/pm_agent/token_budget.py`

### Conceptual role
This subsystem embodies the repo’s documented operating principles:
- confidence before implementation
- evidence-based validation after implementation
- learning from failures and patterns
- token-aware execution limits

### Contributor insight
When adding behavior that changes decision quality, validation, or reflective workflows, start by checking whether the PM-agent layer already models part of the problem.

## Execution subsystem

### Files
- `src/superclaude/execution/parallel.py`
- `src/superclaude/execution/reflection.py`
- `src/superclaude/execution/self_correction.py`

### Conceptual role
These modules appear to capture reusable execution patterns and iterative correction mechanisms.

### Contributor insight
If a feature is framed around “how work should be executed” rather than “what command exists,” the execution package is a likely home.

## Commands asset subsystem

### Location
- `src/superclaude/commands/`

### Representative files
- `implement.md`
- `analyze.md`
- `build.md`
- `document.md`
- `task.md`
- `task-unified.md`
- `research.md`
- `cleanup-audit.md`
- `roadmap.md`
- `index.md`
- `index-repo.md`
- `recommend.md`
- `pm.md`

### Contributor insight
These are part of the framework surface shipped to users. If you are changing command semantics, prompts, or workflow guidance, changes may need to happen here as well as in any Python code that supports them.

## Skills subsystem

### Location
- `src/superclaude/skills/`

### Notable skill families observed
- confidence check
- roadmap protocol
- task-unified protocol
- cli-portify protocol
- cleanup-audit protocol
- adversarial protocol
- review-translation protocol
- validate-tests protocol

### Package structure patterns observed
A skill package may include:
- `SKILL.md`
- `__init__.py`
- `refs/`
- `rules/`
- `templates/`
- `scripts/`
- structured config files like YAML

### Contributor insight
Protocol-oriented skills appear to be a significant architectural pattern in the current repo. If a behavior is mostly instruction/process-oriented, check whether it belongs as a skill artifact rather than as Python-only logic.

## Docs subsystem

### Major groups inside `docs/`
- `getting-started/`
- `user-guide/`
- `developer-guide/`
- `reference/`
- `architecture/`
- `research/`
- `generated/`

### Contributor insight
The docs tree already contains both hand-maintained and generated material. New generated orientation artifacts should stay inside `docs/generated/`, while durable curated docs may belong elsewhere when explicitly requested.

## Component relationship diagram

```text
                    ┌───────────────────────┐
                    │   docs / README /     │
                    │   contributor context  │
                    └───────────┬───────────┘
                                │
                                v
┌────────────────────────────────────────────────────────────┐
│                    src/superclaude/                        │
├──────────────┬───────────────┬──────────────┬──────────────┤
│ cli/         │ pytest plugin │ pm_agent/    │ execution/   │
├──────────────┼───────────────┼──────────────┼──────────────┤
│ commands/    │ skills/       │ agents/      │ install flow │
└──────────────┴───────────────┴──────────────┴──────────────┘
                                │
                                v
                      .claude/ dev mirror assets
```

## Where to look by task type

- CLI command behavior change → `src/superclaude/cli/`
- installation or sync issue → `src/superclaude/cli/` + `Makefile` + `pyproject.toml`
- pytest integration issue → `src/superclaude/pytest_plugin.py`
- confidence/self-check/reflexion issue → `src/superclaude/pm_agent/`
- workflow execution pattern issue → `src/superclaude/execution/`
- slash command content change → `src/superclaude/commands/`
- skill behavior/protocol change → `src/superclaude/skills/`
- contributor understanding or doc navigation issue → `docs/` and generated docs
