# Release Guide — v2.24: CLI Portify Python Pipeline (`superclaude cli-portify`)

**Release**: v2.24
**Branch**: `v.24-cli-portify-cli-v4`
**Sprint outcome**: All 8 phases passed — 1h 12m total execution
**Sprint exit code**: 0 (success)
**Date**: 2026-03-13

---

## 1. What Was Delivered

v2.24 ports the inference-based `sc:cli-portify` skill into a fully programmatic Python CLI pipeline. The new command `superclaude cli-portify run <WORKFLOW_PATH>` replaces the skill's manual 4-phase protocol with a deterministic 7-step Python orchestrator that runs Claude subprocesses under explicit programmatic control.

### Before v2.24

The `sc:cli-portify` skill ran inside a Claude Code session. Claude decided when to move between phases, what to validate, and whether gates passed. This produced inconsistent results between runs, had no stall detection, no budget tracking, and required full re-execution on failure.

### After v2.24

The same workflow now runs as a CLI subprocess pipeline:

```bash
superclaude cli-portify run /path/to/skill-directory
```

Python controls sequencing. Claude only fills content. Gates enforce quality programmatically. Budget is tracked. Failures generate resume commands.

---

## 2. Module Structure

The release adds 24 Python modules under `src/superclaude/cli/cli_portify/`:

```
src/superclaude/cli/cli_portify/
├── __init__.py                   # Exports cli_portify_group
├── cli.py                        # Click CLI: cli-portify group + run subcommand
├── config.py                     # PortifyConfig loader and validator
├── models.py                     # Domain types: PortifyConfig, PortifyStepResult, ComponentInventory, PortifyMonitorState
├── contract.py                   # Return contract emission for all exit paths
├── convergence.py                # ConvergenceState enum + engine + budget guard
├── resume.py                     # Resumability matrix, entry requirements, resume command builder
├── gates.py                      # Gate registry: 5 named GateCriteria with semantic check functions
├── prompts.py                    # Prompt builder framework for Steps 3-7
├── process.py                    # PortifyProcess (extends ClaudeProcess): @path refs, --add-dir
├── monitor.py                    # Event logger, timing capture, failure classifier, diagnostic report
├── tui.py                        # Rich TUI live dashboard with gate state machine
├── review.py                     # User review gate: pause TUI, stderr prompt, y/n, --skip-review
├── failures.py                   # 7 failure type handlers and FailureClassification
├── utils.py                      # Frontmatter parsing, section hashing, file checks, signal constants
└── steps/
    ├── __init__.py
    ├── validate_config.py        # Step 1: config validation (pure-programmatic, EXEMPT gate)
    ├── discover_components.py    # Step 2: component inventory (pure-programmatic, EXEMPT gate)
    ├── analyze_workflow.py       # Step 3: Claude-assisted analysis (STRICT gate)
    ├── design_pipeline.py        # Step 4: Claude-assisted design (STRICT gate + dry-run halt)
    ├── synthesize_spec.py        # Step 5: Claude-assisted spec synthesis (STRICT gate)
    ├── brainstorm_gaps.py        # Step 6: Claude-assisted gap analysis (STANDARD gate)
    └── panel_review.py           # Step 7: Claude-assisted panel review with convergence loop (STRICT gate)
```

This architecture was selected via a two-round adversarial debate between Opus-Architect and Haiku-Architect (convergence score 0.72, Opus selected 81 vs 74). The key design decisions over the original spec are documented in `dev-001-accepted-deviation.md`.

---

## 3. CLI Reference

### Command Group

```
superclaude cli-portify [COMMAND]
```

Subcommands:
- `run WORKFLOW_PATH` — Execute the portification pipeline

### `run` Options

```
Usage: superclaude cli-portify run [OPTIONS] WORKFLOW_PATH

  Execute the cli-portify pipeline on WORKFLOW_PATH.

  WORKFLOW_PATH is the directory containing a SKILL.md file to portify.

Options:
  --output PATH           Output directory for generated artifacts
  --cli-name TEXT         Override derived CLI command name
  --dry-run               Validate and plan without executing Claude steps (halts after Step 2)
  --skip-review           Skip interactive review gates
  --start TEXT            Resume from a specific step (e.g. 'synthesize-spec')
  --max-convergence INT   Maximum convergence iterations for panel review (default: 3)
  --iteration-timeout INT Per-iteration timeout in seconds (default: 300)
  --max-turns INT         Maximum turns per Claude subprocess (default: 100)
  --model TEXT            Claude model to use
  --debug                 Enable debug logging
```

### Quick Usage

```bash
# Full pipeline run
superclaude cli-portify run .claude/skills/sc-brainstorm-protocol

# Dry run — validate config and discover components, then stop
superclaude cli-portify run .claude/skills/sc-brainstorm-protocol --dry-run

# Skip interactive review gates (CI/CD usage)
superclaude cli-portify run .claude/skills/sc-brainstorm-protocol --skip-review

# Resume from a specific step after failure
superclaude cli-portify run .claude/skills/sc-brainstorm-protocol --start synthesize-spec

# Custom output directory
superclaude cli-portify run .claude/skills/sc-brainstorm-protocol --output ./my-portify-output

# Custom model and conservative turn budget
superclaude cli-portify run .claude/skills/sc-brainstorm-protocol --model claude-opus-4-6 --max-turns 50
```

---

## 4. Pipeline Steps

The pipeline runs 7 steps in sequence across two categories:

### Pure-Programmatic Steps (Steps 1-2)

No Claude subprocess is invoked. These complete in <5s and provide fast failure detection.

| Step | Name | Gate Tier | Output Artifact |
|------|------|-----------|----------------|
| 1 | `validate-config` | EXEMPT (<1s, 4 error paths) | `validate-config-result.json` |
| 2 | `discover-components` | EXEMPT (<5s, accurate inventory) | `component-inventory.md` |

**Step 1** validates:
- Workflow path resolves to a directory containing `SKILL.md`
- CLI name derivation succeeds (strips `sc-`/`-protocol`, normalizes case)
- Output directory is writable
- No collision with existing non-portified CLI modules

**Step 2** inventories:
- `SKILL.md`, `refs/`, `rules/`, `templates/`, `scripts/`, matching command files
- Line counts per component (with 1MB cap warning)
- YAML frontmatter with `source_skill` and `component_count`

### Claude-Assisted Steps (Steps 3-7)

Each step spawns a Claude subprocess via `PortifyProcess`, injects `@path` references to prior artifacts, and validates the output through a gate function before proceeding.

| Step | Name | Gate Tier | Output Artifact |
|------|------|-----------|----------------|
| 3 | `analyze-workflow` | STRICT | `portify-analysis.md` (<400 lines) |
| 4 | `design-pipeline` | STRICT + dry-run halt | `portify-spec.md` |
| 5 | `synthesize-spec` | STRICT + sentinel scan | Populated release spec |
| 6 | `brainstorm-gaps` | STANDARD | Augmented spec with Section 12 |
| 7 | `panel-review` | STRICT + convergence loop | `panel-report.md` |

**Step 3** requires 5 sections, a data flow diagram, and 5 YAML frontmatter fields.

**Step 4** is the `--dry-run` halt point. If `--dry-run` is set, the pipeline stops here and emits a `dry_run` contract with phases 3-4 marked `skipped`. A user review gate pauses at this step unless `--skip-review` is set.

**Step 5** requires zero remaining `{{SC_PLACEHOLDER:*}}` sentinels. On gate failure, the retry prompt includes the specific placeholder names that remain.

**Step 6** requires Section 12 to contain either a findings table (with Gap ID column) or the literal zero-gap summary text. Heading-only content fails the gate. Falls back to inline multi-persona prompt if `/sc:brainstorm` is unavailable.

**Step 7** runs a convergence loop (up to `--max-convergence` iterations, default 3). Each iteration has an independent per-iteration timeout (default 300s). Quality is scored across 4 dimensions (clarity, completeness, testability, consistency). Overall = mean of 4 dimensions. Downstream readiness gate: `overall >= 7.0` (7.0 → ready, 6.9 → not ready). Converges when zero unaddressed CRITICALs are found. Falls back to inline fallback prompt if `/sc:spec-panel` is unavailable.

---

## 5. Gate System

Gates enforce quality programmatically. All gate functions return `tuple[bool, str]` — a pass/fail bool and a diagnostic message.

### Gate Tiers

| Tier | Verification | MCP Required | Fallback |
|------|-------------|--------------|---------|
| STRICT | Sub-agent quality review | Sequential + Serena | No |
| STANDARD | Direct test execution | Sequential + Context7 preferred | Yes |
| EXEMPT | Skip verification | None | Yes |

### Semantic Check Functions

The gate registry in `gates.py` provides:

- `_check_section_count(content, min_sections)` — verifies minimum required sections
- `_check_no_placeholders(content)` — zero `{{SC_PLACEHOLDER:*}}` remaining
- `_check_convergence_terminal(content)` — convergence terminal state reached
- `_check_data_flow_diagram(content)` — data flow diagram with arrow notation present

Named gate criteria:

| Constant | Step | Tier | Semantic Checks |
|----------|------|------|----------------|
| `ANALYZE_WORKFLOW_GATE` | 3 | STRICT | section_count(5), data_flow_diagram, frontmatter(5 fields) |
| `DESIGN_PIPELINE_GATE` | 4 | STRICT | step_mapping_count, model_count, gate_definition_count |
| `SYNTHESIZE_SPEC_GATE` | 5 | STRICT | no_placeholders, 7 FRs with consolidation mapping |
| `BRAINSTORM_GAPS_GATE` | 6 | STANDARD | has_section_12 (findings table OR zero-gap text) |
| `PANEL_REVIEW_GATE` | 7 | STRICT | convergence_terminal, quality_scores_populated, downstream_readiness |

---

## 6. Convergence Engine

`convergence.py` implements a standalone, testable convergence controller separate from the executor.

### ConvergenceState Enum

```python
class ConvergenceState(Enum):
    READY      # Not yet started
    ITERATING  # In active iteration loop
    CONVERGED  # Zero unaddressed CRITICALs — success terminal state
    ESCALATED  # Budget/user-triggered — partial terminal state
    FAILED     # Error terminal state
```

All transitions are validated via a dictionary. Invalid transitions raise `AssertionError`.

### ConvergenceEngine

```python
engine = ConvergenceEngine(max_iterations=3, budget_guard=SimpleBudgetGuard(budget))

while not engine.is_done:
    result = run_one_iteration()       # Claude subprocess
    engine.submit(result)              # records + evaluates convergence predicate
    if engine.state == ConvergenceState.CONVERGED:
        break

final = engine.result()  # ConvergenceResult
```

### BudgetGuard

`SimpleBudgetGuard` implements pre-launch budget checking. `has_budget()` is called before each iteration. If the budget is exhausted, `escalate_budget()` transitions the engine to `ESCALATED`.

### Quality Scoring (SC-008, SC-009)

- `overall = mean(clarity, completeness, testability, consistency)` (±0.01 precision)
- Downstream readiness: `overall >= 7.0` → ready (7.0 = True, 6.9 = False)

---

## 7. Subprocess Integration

### PortifyProcess

Extends `pipeline.ClaudeProcess` with:

- **Dual `--add-dir` scoping**: Both `work_dir` (output artifacts) and `workflow_path` (source skill files) are added so Claude can read from both locations
- **`@path` reference injection**: Prior artifact paths are prepended to the prompt as `@<path>` references
- **Exit code 124 → timeout detection**: Follows bash timeout convention
- **Result capture**: `ProcessResult` captures exit_code, stdout_text, stderr_text, timed_out, duration_seconds

### Prompt Builder Framework

Each Claude-assisted step has a dedicated prompt builder in `prompts.py`:

- `AnalyzeWorkflowPrompt` — references component inventory via `@path`
- `DesignPipelinePrompt` — references analysis output via `@path`
- `SynthesizeSpecPrompt` — references all prior artifacts; includes template population contract
- `BrainstormGapsPrompt` — includes multi-persona analysis instructions; fallback variant
- `PanelReviewPrompt` — includes focus pass + critique pass combined; convergence iteration state

All builders accept resume context injection for Steps 5-7 when `--start` is used.

---

## 8. Return Contracts

Every exit path emits a populated `PortifyContract` (never a partial or empty object). `contract.py` provides four builders:

| Builder | Status | When |
|---------|--------|------|
| `build_success_contract()` | `SUCCESS` | All 7 steps pass |
| `build_partial_contract()` | `PARTIAL` | Some steps complete, pipeline stops |
| `build_failed_contract()` | `FAILED` | Unrecoverable failure |
| `build_dry_run_contract()` | `DRY_RUN` | `--dry-run` flag used |

Contracts include:
- Step results and timing for each completed step
- Phase status (completed/skipped/failed)
- Resume command (when applicable)
- Quality scores (for panel review completions)
- Downstream readiness assessment

---

## 9. Resume Semantics

`resume.py` owns the resumability matrix and resume command generation.

### Resumability Matrix

| Step | Resumable | Preserved Context |
|------|-----------|-------------------|
| validate-config (1) | No | — |
| discover-components (2) | No | — |
| analyze-workflow (3) | Yes | component-inventory.md |
| design-pipeline (4) | Yes | portify-analysis.md |
| synthesize-spec (5) | Yes | portify-spec.md, prior analysis |
| brainstorm-gaps (6) | Yes | synthesized spec |
| panel-review (7) | Yes | focus-findings.md from prior iterations |

**Policy**: Prefer re-running `synthesize-spec` over trusting partially gated output. Steps with partial artifacts are flagged for re-run rather than resume.

### Resume Command Generation

When a resumable step fails, the contract includes:

```bash
superclaude cli-portify run <workflow_path> --start <step_name> [--max-turns <suggested_budget>]
```

---

## 10. Failure Handling

`failures.py` classifies 7 failure types with explicit handling paths:

| Type | Detection | Handling |
|------|-----------|---------|
| Missing template | `release-spec-template.md` absent at startup | Fail-fast with remediation path |
| Missing skills | `/sc:brainstorm` or `/sc:spec-panel` unavailable | Graceful fallback with warning |
| Malformed artifact | Frontmatter parse error or gate failure | Diagnostic classification + targeted retry |
| Timeout | Exit code 124 per-iteration | Per-iteration independent timeout; ESCALATED state |
| Partial artifact | Step produced output but gate failed | Re-run policy (prefer re-run over trust) |
| Non-writable output | Output directory not writable | Early detection in Step 1 |
| Exhausted budget | TurnLedger depleted | ESCALATED terminal state with resume guidance |

---

## 11. Live Dashboard (TUI)

`tui.py` provides a Rich-based live dashboard using `rich.live.Live`.

### Dashboard State Machine

```
pending → running → complete | failed
                  ↓
           review_pause (when gate requires user review)
                  ↓
              resume
```

### Display Components

- **Step table**: Each of 7 steps with status, timing, gate tier
- **Current iteration**: Active convergence iteration count (Step 7)
- **Review pause**: Banner prompting user to continue or abort
- **Warnings**: Advisory messages from stall detection or fallback activation
- **Elapsed timer**: Running total pipeline duration

Falls back gracefully when `rich` is not installed (plain text output via `_fallback_status`).

---

## 12. User Review Gates

`review.py` implements interactive pause points at Steps 4 and 7 (after panel review).

Behavior:
- TUI is paused (live rendering stops)
- Prompt written to stderr: `"Review complete. Continue? [y/N]"`
- `y` → continue pipeline
- `n` → pipeline halts with `USER_REJECTED` status; resume command is generated
- `--skip-review` bypasses all review gates (suitable for CI/CD)

---

## 13. Monitoring and Diagnostics

`monitor.py` unifies three concerns (previously `tui.py`, `logging_.py`, `diagnostics.py` in spec):

### EventLogger

Emits NDJSON events to `execution-log.jsonl`. Signal vocabulary constants (from `utils.py`):

```python
STEP_START   = "step_start"
STEP_COMPLETE = "step_complete"
STEP_ERROR   = "step_error"
STEP_TIMEOUT  = "step_timeout"
GATE_PASS    = "gate_pass"
GATE_FAIL    = "gate_fail"
```

### TimingCapture

Records per-step and per-phase timings with `start_step()`/`end_step()` boundaries. Accessible via `step_timings` and `phase_timings` properties for contract population.

### DiagnosticReport

`generate_diagnostic_report()` produces a Markdown report from all events in the event log, including failure classification, timing summary, and gate results.

---

## 14. Registration

`cli_portify_group` is registered in `src/superclaude/cli/main.py`:

```python
from superclaude.cli.cli_portify import cli_portify_group
main.add_command(cli_portify_group, name="cli-portify")
```

This makes `superclaude cli-portify` available as a top-level subcommand alongside `sprint`, `roadmap`, `cleanup-audit`, and `tasklist`.

---

## 15. Test Coverage

The test suite in `tests/cli_portify/` covers all major components:

### Unit Tests

| Test File | Coverage |
|-----------|---------|
| `test_config.py` | PortifyConfig loading, CLI name derivation, path validation |
| `test_contracts.py` | Contract builders for all 4 exit path states |
| `test_validate_config.py` | Step 1: 4 failure paths, SKILL.md detection |
| `test_discover_components.py` | Step 2: line counting, frontmatter generation, 1MB cap |
| `test_gates.py` | Gate tier enforcement, `tuple[bool, str]` signatures |
| `test_portify_gates.py` | Semantic check functions; 7.0/6.9 boundary cases |
| `test_convergence.py` | ConvergenceState transitions, BudgetGuard, engine lifecycle |
| `test_section_hashing.py` | Additive-only enforcement, hash comparison |
| `test_resume.py` | Resumability matrix, resume command generation |
| `test_failures.py` | All 7 failure type handlers |
| `test_review.py` | Review gate pause/continue/reject behavior |
| `test_tui.py` | Dashboard state machine, Rich fallback |
| `test_monitor.py` | EventLogger, TimingCapture, NDJSON emission |

### Subprocess/Integration Tests

| Test File | Coverage |
|-----------|---------|
| `test_process.py` | PortifyProcess: `--add-dir`, `@path` injection, exit code capture |
| `test_prompts.py` | Per-step prompt builder output format |
| `test_mock_harness.py` | Mock harness returns known-good outputs per step type |
| `test_analyze_workflow.py` | Step 3 STRICT gate with known-good analysis |
| `test_design_pipeline.py` | Step 4: dry-run halt, review gate, STRICT gate |
| `test_synthesize_spec.py` | Step 5: zero placeholder sentinel, retry prompt |
| `test_brainstorm_gaps.py` | Step 6: Section 12 validation, fallback activation |
| `test_panel_review.py` | Step 7: convergence loop, quality scoring, downstream readiness |
| `test_panel_report.py` | panel-report.md structure, convergence block |
| `integration/test_orchestration.py` | Full happy path, dry-run, review rejection, convergence bounds |

### Compliance Checks (SC-012, SC-013)

```bash
# Zero async def / await in cli_portify/
grep -r "async def\|await" src/superclaude/cli/cli_portify/   # expect: no output

# Zero changes to pipeline/ and sprint/ base modules
git diff --name-only HEAD main | grep -E "pipeline/|sprint/"  # expect: no output
```

---

## 16. Architectural Invariants

These constraints are enforced by compliance checks and must not be violated in future modifications:

1. **Synchronous-only**: No `async def` or `await` anywhere in `cli_portify/`. Use `threading` and `ThreadPoolExecutor` for parallelism.

2. **Zero base-module modifications**: `pipeline/` and `sprint/` directories are read-only from `cli_portify/`'s perspective. All extension is via subclassing and composition.

3. **Runner-authored truth**: Python controls sequencing. Claude never decides which step runs next or whether a gate passes.

4. **All exit paths emit contracts**: Every code path — success, partial, failed, dry_run, user-rejected — calls a contract builder before returning.

5. **Gate signatures**: All gate functions return `tuple[bool, str]`. Functions returning `bool` alone are not compliant.

6. **Per-iteration independent timeout**: Each convergence iteration in Step 7 gets its own independent `iteration_timeout`, not a share of a total divided by `max_convergence`.

---

## 17. How to Run Tests

```bash
# Full test suite
uv run pytest tests/cli_portify/ -v

# Unit tests only
uv run pytest tests/cli_portify/ -v -k "not integration"

# Integration tests only
uv run pytest tests/cli_portify/integration/ -v

# Specific component
uv run pytest tests/cli_portify/test_convergence.py -v
uv run pytest tests/cli_portify/test_gates.py -v

# Boundary tests for scoring
uv run pytest tests/cli_portify/test_portify_gates.py -v -k "boundary"
```

---

## 18. Known Deviations from Original Spec

The implementation differs from the original `portify-release-spec.md` in several accepted ways documented in `dev-001-accepted-deviation.md`:

| Deviation | Resolution |
|-----------|-----------|
| `steps/` subdirectory vs. flat layout | `steps/` adopted — better navigability, step-level test isolation |
| `cli.py` vs. `commands.py` | `cli.py` adopted — names file by function, not framework abstraction |
| `contract.py` not in original spec | Added — separates contract emission from result data model (SRP) |
| `resume.py` not in original spec | Added — cross-cutting resume policy owns decision table |
| `convergence.py` scope expanded | Includes predicate checking + budget guards, not just enum + transitions |
| `monitor.py` merges `tui.py` + `logging_.py` + `diagnostics.py` | Merged — shared event stream, same lifecycle, avoids circular deps |
| `executor.py` as first-class module | Separated from `cli.py` — owns orchestration, budget, resume, review |

All deviations were validated through a two-round adversarial debate (documented in `debate-transcript.md` and `base-selection.md`).

---

## 19. Release Process Used

This release was built using the SuperClaude Sprint CLI runner:

| Phase | Name | Duration |
|-------|------|---------|
| 1 | Architecture Confirmation (Decision Records) | 4m 49s |
| 2 | Foundation and CLI Skeleton | 8m 18s |
| 3 | Fast Deterministic Steps | 7m 24s |
| 4 | Subprocess Orchestration Core | 10m 35s |
| 5 | Core Content Generation | 7m 14s |
| 6 | Quality Amplification | 9m 11s |
| 7 | UX and Operational Hardening | 15m 17s |
| 8 | Validation and Release | 10m 1s |
| **Total** | | **1h 12m** |

The tasklist (37 tasks, 52 deliverables) was generated from the roadmap by the `sc:tasklist` command. Spec fidelity was validated (16 deviations found, 3 HIGH resolved). Tasklist validation found 7 findings (2 HIGH, 3 MEDIUM, 2 LOW — all resolved before execution).

---

## 20. Related Files

| File | Purpose |
|------|---------|
| `.dev/releases/current/v2.24-cli-portify-cli-v4/roadmap.md` | Full implementation roadmap (8 phases) |
| `.dev/releases/current/v2.24-cli-portify-cli-v4/portify-release-spec.md` | Original feature specification |
| `.dev/releases/current/v2.24-cli-portify-cli-v4/spec-fidelity.md` | 16-deviation fidelity report |
| `.dev/releases/current/v2.24-cli-portify-cli-v4/dev-001-accepted-deviation.md` | DEV-001 architectural acceptance record |
| `.dev/releases/current/v2.24-cli-portify-cli-v4/validation/ValidationReport.md` | Tasklist validation findings |
| `.dev/releases/current/v2.24-cli-portify-cli-v4/debate-transcript.md` | Adversarial debate transcript |
| `.dev/releases/current/v2.24-cli-portify-cli-v4/base-selection.md` | Variant scoring and selection |
| `.dev/releases/current/v2.24-cli-portify-cli-v4/execution-log.md` | Sprint phase execution log |
| `docs/generated/cli-portify-release-guide.md` | Skill-layer guide (sc:cli-portify command) |
