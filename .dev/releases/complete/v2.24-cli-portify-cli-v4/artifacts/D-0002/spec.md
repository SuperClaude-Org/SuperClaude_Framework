---
deliverable_id: D-0002
task_id: T01.02
roadmap_item: R-002
phase: 1
type: module-map
status: FINAL
depends_on: D-0001
---

# D-0002: Frozen 18-Module Architecture with Ownership Boundaries

## Purpose

Define the authoritative module map for `src/superclaude/cli/cli_portify/` with all 18 modules assigned to ownership boundaries. This map is frozen for the duration of v2.24 implementation.

## Module Layout Authority

Per D-0001 Resolution 4 and DEV-001 accepted deviation, the 18-module structure from the roadmap is authoritative. The spec's original 13-file flat layout is superseded.

---

## Module Map (18 modules)

### Ownership Boundary 1: Config/Model Layer (2 modules)

| # | Module | Path | Purpose |
|---|--------|------|---------|
| 1 | `config.py` | `cli_portify/config.py` | Config validation step: workflow path resolution, CLI name derivation, output-dir writability, collision detection |
| 2 | `models.py` | `cli_portify/models.py` | Domain data models: `PortifyConfig` (extends `PipelineConfig`), `ComponentInventory`, `PortifyResult`, `PortifyStepResult` (extends `StepResult`), `PortifyStatus`, `PortifyOutcome`, `PortifyMonitorState` |

### Ownership Boundary 2: Step Implementations (7 modules)

| # | Module | Path | Purpose |
|---|--------|------|---------|
| 3 | `validate_config.py` | `cli_portify/steps/validate_config.py` | Step 1: config validation, name derivation, output-dir writability, collision detection |
| 4 | `discover_components.py` | `cli_portify/steps/discover_components.py` | Step 2: component discovery, line counting (1MB cap with warning), `ComponentInventory` construction |
| 5 | `analyze_workflow.py` | `cli_portify/steps/analyze_workflow.py` | Step 3: Claude-assisted workflow analysis producing `portify-analysis.md` |
| 6 | `design_pipeline.py` | `cli_portify/steps/design_pipeline.py` | Step 4: Claude-assisted pipeline design producing `portify-spec.md`; `--dry-run` halt point |
| 7 | `synthesize_spec.py` | `cli_portify/steps/synthesize_spec.py` | Step 5: Claude-assisted spec synthesis; template validation; placeholder sentinel scan |
| 8 | `brainstorm_gaps.py` | `cli_portify/steps/brainstorm_gaps.py` | Step 6: Claude-assisted gap analysis via `/sc:brainstorm`; inline fallback if skill unavailable |
| 9 | `panel_review.py` | `cli_portify/steps/panel_review.py` | Step 7: Claude-assisted panel review with convergence loop; section hashing for additive-only enforcement |

### Ownership Boundary 3: Process Wrapper (1 module)

| # | Module | Path | Purpose |
|---|--------|------|---------|
| 10 | `process.py` | `cli_portify/process.py` | `PortifyProcess` extending `pipeline.ClaudeProcess`: `@path` references, `--add-dir`, timeout, model propagation, exit code/stdout/stderr capture |

### Ownership Boundary 4: Monitor/Logging (1 module)

| # | Module | Path | Purpose |
|---|--------|------|---------|
| 11 | `monitor.py` | `cli_portify/monitor.py` | Unified monitoring: Rich TUI live dashboard, JSONL + Markdown execution logging, 5+ signal types; contains `DiagnosticCollector`, `FailureClassifier`, `ReportGenerator` as internal components |

### Ownership Boundary 5: Contract Emission (3 modules)

| # | Module | Path | Purpose |
|---|--------|------|---------|
| 12 | `contract.py` | `cli_portify/contract.py` | Return contract emission: `to_contract()` producing Phase Contracts schema YAML on all exit paths (success/partial/failed/dry_run) |
| 13 | `resume.py` | `cli_portify/resume.py` | Resume decision table: per-step resumability classification, prior-context injection rules, partial-artifact preservation policy, resume command generation |
| 14 | `convergence.py` | `cli_portify/convergence.py` | Convergence controller: `ConvergenceState` enum (`READY`, `ITERATING`, `CONVERGED`, `ESCALATED`, `FAILED`) with valid-transition dictionary and transition assertion |

### Ownership Boundary 6: CLI Integration (4 modules)

| # | Module | Path | Purpose |
|---|--------|------|---------|
| 15 | `cli.py` | `cli_portify/cli.py` | Click CLI group and `run` subcommand; registers command with `main.py` via `app.add_command()` |
| 16 | `executor.py` | `cli_portify/executor.py` | Step orchestration loop: convergence iteration, budget management, resume state, review-gate pauses, dry-run termination |
| 17 | `gates.py` | `cli_portify/gates.py` | Gate criteria registry: 7 `GateCriteria` objects with `SemanticCheck` compositions, tiered enforcement (EXEMPT/STANDARD/STRICT) |
| 18 | `prompts.py` | `cli_portify/prompts.py` | Prompt builder functions for Steps 3-7; resume-context-aware for Steps 5-7; retry augmentation for targeted failures |

---

## Ownership Boundary Coverage Verification

| Boundary | Module Count | Modules |
|----------|-------------|---------|
| Config/Model Layer | 2 | config.py, models.py |
| Step Implementations | 7 | validate_config.py, discover_components.py, analyze_workflow.py, design_pipeline.py, synthesize_spec.py, brainstorm_gaps.py, panel_review.py |
| Process Wrapper | 1 | process.py |
| Monitor/Logging | 1 | monitor.py |
| Contract Emission | 3 | contract.py, resume.py, convergence.py |
| CLI Integration | 4 | cli.py, executor.py, gates.py, prompts.py |
| **Total** | **18** | |

All 6 ownership categories have at least one module. Total module count = 18 (excluding `__init__.py` and `steps/__init__.py`).

---

## File Tree (Complete)

```
src/superclaude/cli/cli_portify/
├── __init__.py
├── cli.py                          # CLI Integration
├── config.py                       # Config/Model Layer
├── contract.py                     # Contract Emission
├── convergence.py                  # Contract Emission
├── executor.py                     # CLI Integration
├── gates.py                        # CLI Integration
├── models.py                       # Config/Model Layer
├── monitor.py                      # Monitor/Logging
├── process.py                      # Process Wrapper
├── prompts.py                      # CLI Integration
├── resume.py                       # Contract Emission
└── steps/
    ├── __init__.py
    ├── validate_config.py           # Step Implementations
    ├── discover_components.py       # Step Implementations
    ├── analyze_workflow.py          # Step Implementations
    ├── design_pipeline.py           # Step Implementations
    ├── synthesize_spec.py           # Step Implementations
    ├── brainstorm_gaps.py           # Step Implementations
    └── panel_review.py              # Step Implementations
```

---

## Consistency Check

- Module count: 18 (matches roadmap Section 4.1 per DEV-001 Amendment A)
- Ownership categories: 6 (all represented)
- Consistent with roadmap Phase 0, Work Item 2
- Consistent with DEV-001 Section 6 (Spec Amendment Table)
- Consistent with D-0001 Resolution 4
