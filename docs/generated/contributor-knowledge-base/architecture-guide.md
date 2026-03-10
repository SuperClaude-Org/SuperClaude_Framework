# Architecture Guide

This guide explains the current repository architecture of `SuperClaude_Framework` from a contributor perspective.

It is grounded in the current repository state, especially:
- `src/superclaude/`
- `pyproject.toml`
- `Makefile`
- `CLAUDE.md`
- generated contributor docs in `docs/generated/contributor-knowledge-base/`

If older prose conflicts with the current tree, prefer the current code and current repo instructions.

## Table of contents

- [Architecture in one view](#architecture-in-one-view)
- [Source-of-truth model](#source-of-truth-model)
- [Core architectural layers](#core-architectural-layers)
- [Runtime-facing package architecture](#runtime-facing-package-architecture)
- [Framework asset architecture](#framework-asset-architecture)
- [CLI-centered architecture](#cli-centered-architecture)
- [Execution and validation architecture](#execution-and-validation-architecture)
- [Contributor implications](#contributor-implications)
- [Mermaid readability notes](#mermaid-readability-notes)

## Architecture in one view

At a practical level, contributors can think about the repository as four connected layers:

```mermaid
flowchart TD
    A[Contributor guidance<br/>README.md, CLAUDE.md, docs/] --> B[Canonical package and assets<br/>src/superclaude/]
    B --> C[Runtime implementation<br/>CLI, pytest plugin, PM-agent, execution]
    B --> D[Framework assets<br/>commands, skills, agents, core, mcp, modes]
    C --> E[Packaging and validation<br/>pyproject.toml, Makefile, tests/]
    D --> E
    E --> F[Installed outputs and mirrors<br/>.claude/ and ~/.claude/]
```

## Source-of-truth model

The most important structural rule documented in the repository is:
- `src/superclaude/` is the canonical source for distributable components
- `.claude/` contains repo-local development copies consumed directly by Claude Code during local iteration

That means contributor edits should generally start in `src/superclaude/` and only flow into `.claude/` through the documented sync path.

```mermaid
flowchart LR
    subgraph SourceOfTruth[Canonical source]
        A[src/superclaude/commands]
        B[src/superclaude/agents]
        C[src/superclaude/skills]
        D[src/superclaude Python code]
    end

    subgraph RepoMirror[Repo-local mirror]
        E[.claude/commands/sc]
        F[.claude/agents]
        G[.claude/skills]
    end

    subgraph UserInstall[User install targets]
        H[~/.claude/commands/sc]
        I[~/.claude/agents]
        J[~/.claude/skills]
        K[~/.claude core files]
    end

    A -->|make sync-dev| E
    B -->|make sync-dev| F
    C -->|make sync-dev| G

    A -->|CLI install flow| H
    B -->|CLI install flow| I
    C -->|CLI install flow| J
    D -->|install_core / package runtime| K

    L[make verify-sync] -. checks drift .-> E
    L -. checks drift .-> F
    L -. checks drift .-> G
```

## Core architectural layers

### 1. Contributor and process layer
This layer includes:
- `README.md`
- `CLAUDE.md`
- curated docs under `docs/`
- process and release materials under `.dev/`

Its job is to explain how the repository should be used and changed.

### 2. Canonical package and asset layer
This is `src/superclaude/`, which contains both:
- executable Python package code
- shipped framework assets like commands, skills, and agents

### 3. Runtime and integration layer
This includes the Python implementation surfaces contributors most often touch:
- CLI package
- pytest plugin
- PM-agent modules
- execution helpers

### 4. Packaging, sync, and validation layer
This includes:
- `pyproject.toml`
- `Makefile`
- `tests/`
- installer modules in `src/superclaude/cli/`

## Runtime-facing package architecture

The runtime-facing part of the package is broader than some older docs suggest.

```mermaid
flowchart TB
    ROOT[src/superclaude/]
    ROOT --> CLI[cli/]
    ROOT --> PYTEST[pytest_plugin.py]
    ROOT --> PM[pm_agent/]
    ROOT --> EXEC[execution/]
    ROOT --> ASSETS[commands / skills / agents]
    ROOT --> CONTENT[core / mcp / modes]

    CLI --> CLI_SUBS[installer commands + workflow groups]
    PYTEST --> PYTEST_SUBS[fixtures + hooks + collection/report logic]
    PM --> PM_SUBS[confidence + self-check + reflexion + token budget]
    EXEC --> EXEC_SUBS[parallel + reflection + self-correction]
```

### CLI layer
Observed in `src/superclaude/cli/`.

Current top-level command functions exported from `main.py` include:
- `main`
- `install`
- `mcp`
- `update`
- `install_skill`
- `doctor`
- `version`

The CLI tree also contains larger workflow subsystems:
- `sprint/`
- `roadmap/`
- `cleanup_audit/`
- `pipeline/`
- `audit/`

### Pytest plugin layer
Observed in `src/superclaude/pytest_plugin.py`.

Observed functions include:
- `pytest_configure`
- `confidence_checker`
- `self_check_protocol`
- `reflexion_pattern`
- `token_budget`
- `pm_context`
- `pytest_runtest_setup`
- `pytest_runtest_makereport`
- `pytest_report_header`
- `pytest_collection_modifyitems`

This makes the pytest plugin a first-class integration surface, not just a test helper.

### PM-agent layer
Observed in `src/superclaude/pm_agent/`.

Key modules:
- `confidence.py`
- `self_check.py`
- `reflexion.py`
- `token_budget.py`

These match the repository’s documented operating model of confidence-first work, evidence-based validation, learning/reflection, and token budgeting.

### Execution support layer
Observed in `src/superclaude/execution/`.

Key modules:
- `parallel.py`
- `reflection.py`
- `self_correction.py`

This layer appears to capture reusable execution and iteration patterns.

## Framework asset architecture

The repository ships framework assets alongside Python code.

```mermaid
flowchart LR
    A[src/superclaude/] --> B[commands/]
    A --> C[skills/]
    A --> D[agents/]
    A --> E[core/]
    A --> F[mcp/]
    A --> G[modes/]

    B --> B1[slash-command markdown assets]
    C --> C1[skill packages with SKILL.md]
    C --> C2[rules / refs / templates / scripts]
    D --> D1[agent definition source files]
    E --> E1[framework core content]
    F --> F1[MCP-related framework content]
    G --> G1[mode-related framework content]
```

### Commands
Observed in `src/superclaude/commands/`.

This tree contains a large set of markdown-defined commands, including:
- `implement.md`
- `analyze.md`
- `build.md`
- `document.md`
- `research.md`
- `task-unified.md`
- `cleanup-audit.md`
- `index.md`
- `index-repo.md`
- `roadmap.md`
- and many others

### Skills
Observed in `src/superclaude/skills/`.

The repo includes both user-facing and protocol-style skills, for example:
- `confidence-check/`
- `sc-task-unified-protocol/`
- `sc-cli-portify-protocol/`
- `sc-roadmap-protocol/`
- `sc-cleanup-audit-protocol/`
- `sc-adversarial-protocol/`
- `sc-review-translation-protocol/`

Many skill packages include a mix of:
- `SKILL.md`
- `__init__.py`
- `rules/`
- `templates/`
- `refs/`
- `scripts/`
- YAML configuration artifacts

### Agents
The source tree and docs indicate agent assets are also part of the distributable framework model, even though the current codebase is broader than an agents-only framing.

## CLI-centered architecture

The CLI is the main console-runtime surface of the package.

```mermaid
flowchart TD
    A[pyproject.toml] --> B[[project.scripts]]
    A --> C[[project.entry-points.pytest11]]

    B --> D[superclaude = superclaude.cli.main:main]
    D --> E[Console CLI]
    E --> F[src/superclaude/cli/main.py]

    C --> G[superclaude = superclaude.pytest_plugin]
    G --> H[Pytest plugin runtime]

    F --> I[install]
    F --> J[mcp]
    F --> K[update]
    F --> L[install-skill]
    F --> M[doctor]
    F --> N[version]
    F --> O[sprint group]
    F --> P[roadmap group]
    F --> Q[cleanup-audit group]
```

A second useful view is the CLI subsystem structure:

```mermaid
flowchart TB
    CLI[src/superclaude/cli/]
    CLI --> MAIN[main.py]
    CLI --> DOCTOR[doctor.py]
    CLI --> INSTALLERS[install_*.py]
    CLI --> SPRINT[sprint/]
    CLI --> ROADMAP[roadmap/]
    CLI --> CLEANUP[cleanup_audit/]
    CLI --> PIPELINE[pipeline/]
    CLI --> AUDIT[audit/]

    SPRINT --> SPRINT_PARTS[commands / executor / config / models / tmux / tui]
    ROADMAP --> ROADMAP_PARTS[commands / executor / validate_executor / gates / prompts / models]
    CLEANUP --> CLEANUP_PARTS[commands / executor / config / models / prompts / gates / tui]
    PIPELINE --> PIPELINE_PARTS[shared runners / gates / passes / process / diagnostics]
    AUDIT --> AUDIT_PARTS[classification / validation / duplication / reports / orchestration]
```

## Execution and validation architecture

Contributors should think of execution and validation as a connected support layer rather than as isolated files.

```mermaid
flowchart LR
    A[CLI workflows] --> B[pipeline/ shared execution foundation]
    A --> C[audit/ specialized audit support]
    D[pytest plugin] --> E[test-time validation hooks]
    F[pm_agent/] --> G[confidence and self-check patterns]
    H[execution/] --> I[parallel / reflection / self-correction helpers]

    B --> J[workflow execution]
    C --> K[reporting and structural analysis]
    E --> L[test collection / setup / report integration]
    G --> M[quality and readiness checks]
    I --> N[execution pattern reuse]
```

A validation-oriented contributor reading is:
- package behavior often flows through CLI + tests + plugin hooks
- framework-asset changes often require sync/verification via `make sync-dev` and `make verify-sync`
- generated-doc changes require path/link/claim validation against the live tree

## Contributor implications

When changing the system:
- packaging concerns often flow through `pyproject.toml` and `src/superclaude/cli/`
- test/plugin concerns often flow through `src/superclaude/pytest_plugin.py` and `tests/`
- framework content changes often flow through `src/superclaude/commands/`, `src/superclaude/skills/`, and agent assets
- local Claude Code development behavior may require corresponding `.claude/` sync validation

A useful decision shortcut is:

```mermaid
flowchart TD
    A[Need to change behavior] --> B{What kind of behavior?}
    B -->|Console / install / runner behavior| C[src/superclaude/cli/]
    B -->|Pytest / fixtures / hooks| D[src/superclaude/pytest_plugin.py]
    B -->|Confidence / self-check / reflection| E[src/superclaude/pm_agent/]
    B -->|Execution pattern reuse| F[src/superclaude/execution/]
    B -->|Command UX or workflow contract| G[src/superclaude/commands/]
    B -->|Protocol-heavy skill behavior| H[src/superclaude/skills/]
    B -->|Generated contributor docs| I[docs/generated/]
```

## Mermaid readability notes

When reading these diagrams in GitHub markdown:
- prefer zooming the page instead of copying diagrams into external renderers first
- follow left-to-right or top-to-bottom flow one section at a time
- use the section heading and nearby bullets as the legend for each diagram
- when a diagram feels dense, jump to the linked detailed doc instead of treating the diagram as a full specification

Authoring guidance used in this generated bundle:
- one diagram per architectural question
- avoid overloading a single graph with every subsystem
- keep labels tied to real repo paths and current entry points
- prefer current code over older prose when diagramming relationships
