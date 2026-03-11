# CLI Portify — Release Guide

This guide covers the `sc:cli-portify` workflow-to-CLI pipeline compiler, including:
- what each component does,
- when to use it,
- how to run it,
- practical examples with all options,
- the 4-phase protocol architecture,
- gate criteria and validation,
- and how it fits into the **skill → spec → roadmap → tasklist → implementation** workflow.

---

## 1) Release Summary (What is included)

### Core command surface
The `sc:cli-portify` command provides a single entry point:
- `/sc:cli-portify` — Analyze an inference-based workflow and produce a reviewed release specification for programmatic CLI conversion

### Architecture overview
The cli-portify system uses a **two-layer architecture**:
1. **Command shim** (`cli-portify.md`) — Thin entry point that validates inputs and delegates to the protocol skill
2. **Protocol skill** (`sc-cli-portify-protocol/SKILL.md`) — Full 4-phase portification protocol with embedded brainstorm and spec-panel review

The protocol transforms inference-based SuperClaude workflows (commands + skills + agents) into formal release specifications that describe deterministic CLI pipelines with:
- Programmatic control flow (Python decides what runs when)
- Formal artifact validation (gates check output quality)
- Resume/retry capability (failed steps resume without re-running everything)
- Live monitoring (TUI with stall detection and diagnostics)
- Budget economics (turn ledger tracks consumption)

### Module structure
```
src/superclaude/
├── commands/
│   └── cli-portify.md                        # Command shim (input validation + protocol invocation)
└── skills/
    └── sc-cli-portify-protocol/
        ├── __init__.py                        # Package marker
        ├── SKILL.md                           # Full 4-phase protocol (~560 lines)
        ├── decisions.yaml                     # 15 architectural decision records
        └── refs/
            ├── analysis-protocol.md           # Phase 1 discovery checklist and output template
            ├── pipeline-spec.md               # Phase 2 code patterns and design primitives
            └── code-templates.md              # INACTIVE — historical reference only (pre-v2.23)
```

### Shared infrastructure dependency
The cli-portify protocol produces specifications that describe pipelines built on the shared `pipeline/` and `sprint/` modules:
- `pipeline/models.py` — `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`, `GateMode`, `SemanticCheck`
- `pipeline/executor.py` — Generic step sequencer with retry, gates, parallel dispatch
- `pipeline/process.py` — `ClaudeProcess` subprocess management
- `pipeline/gates.py` — `gate_passed()` evaluation logic
- `sprint/models.py` — `TurnLedger` for budget tracking

### Key design decisions
- **Spec-driven output**: Phases 3-4 produce a reviewed release specification, NOT generated code. Code generation was removed in v2.23 in favor of feeding the spec into `sc:roadmap` → `sc:tasklist` → `sc:implement`
- **Embedded behavioral patterns**: Brainstorm and spec-panel patterns are embedded inline (no inter-skill command invocation) to keep the pipeline non-interactive and automatable (ADR-C01)
- **Additive-only incorporation**: All spec modifications during Phase 4 review append/extend only — never rewrite existing content (ADR-C02)
- **Convergent review loop**: Phase 4 uses a state machine with max 3 iterations to guarantee termination while ensuring quality (ADR-SM01)
- **Downstream-ready gate**: `overall >= 7.0` required before the spec can feed downstream planning tools (ADR-C08)

---

## 2) Command Reference — When and How to Use

## `/sc:cli-portify`

### What it does
Analyzes an inference-based SuperClaude workflow (skill/command/agent), decomposes it into a structured pipeline specification, synthesizes a release spec from a template, runs multi-persona brainstorm gap analysis, and performs convergent expert panel review — producing a downstream-ready specification for `sc:roadmap`.

### Use when
- You have an existing SuperClaude skill that needs deterministic, repeatable execution
- You want formal artifact validation and resume capability for a multi-step workflow
- You want to move orchestration out of inference and into Python control flow
- You need a reviewed specification before committing to implementation

### Syntax
```
/sc:cli-portify --workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>] [--dry-run]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--workflow` | Yes | — | Skill directory path or `sc-*` name to portify. Must resolve to a directory containing `SKILL.md`. |
| `--name` | No | Derived from workflow | CLI subcommand name (kebab-case). Derivation strips `sc-` prefix and `-protocol` suffix. |
| `--output` | No | `src/superclaude/cli/<derived-name>/` | Output directory for all pipeline artifacts. |
| `--dry-run` | No | false | Execute Phases 1-2 only — emit analysis and specification contracts. No spec synthesis (Phase 3) or panel review (Phase 4). |

### Input validation

Six validation checks run before protocol invocation:

| Check | Error Code | Condition |
|-------|-----------|-----------|
| Workflow argument present | `MISSING_WORKFLOW` | `--workflow` not provided |
| Workflow path resolves | `INVALID_PATH` | Path doesn't exist or has no `SKILL.md` |
| Workflow path unambiguous | `AMBIGUOUS_PATH` | Multiple candidates match the name |
| Output directory writable | `OUTPUT_NOT_WRITABLE` | Parent directory doesn't exist or isn't writable |
| No name collision | `NAME_COLLISION` | Derived name collides with existing non-portified CLI module |
| Name derivation succeeds | `DERIVATION_FAILED` | Cannot derive valid identifier from workflow name |

### Name derivation rules
When `--name` is not provided:
1. Strip `sc-` prefix if present
2. Strip `-protocol` suffix if present
3. Convert to kebab-case for CLI, snake_case for Python modules

Example: `sc-cleanup-audit-protocol` → CLI name: `cleanup-audit`, Python module: `cleanup_audit`

### Examples

```bash
# Basic: portify a skill by directory path
/sc:cli-portify --workflow src/superclaude/skills/sc-cleanup-audit-protocol/

# Portify by skill name (auto-resolved to directory)
/sc:cli-portify --workflow sc-cleanup-audit

# With explicit CLI name
/sc:cli-portify --workflow sc-cleanup-audit --name cleanup-audit

# Dry run — analysis and specification only, no synthesis or review
/sc:cli-portify --workflow sc-adversarial --dry-run

# Full invocation with all options
/sc:cli-portify --workflow src/superclaude/skills/sc-tasklist-protocol/ \
  --name tasklist \
  --output src/superclaude/cli/tasklist/

# Portify the roadmap skill (already portified — would trigger NAME_COLLISION)
/sc:cli-portify --workflow sc-roadmap-protocol
# → error_code: NAME_COLLISION
# → message: "CLI module 'roadmap' already exists at 'src/superclaude/cli/roadmap/' ..."
```

---

## 3) The 4-Phase Protocol Architecture

The portification protocol decomposes a workflow through progressive refinement. Each phase produces artifacts that feed the next.

### Pipeline overview

```
Phase 1: Workflow Analysis ───────────────────┐
    → portify-analysis.md                      │
                                               │ (user review)
                                               ↓
Phase 2: Pipeline Specification ──────────────┐
    → portify-spec.md (+ portify-prompts.md)   │
                                               │ (user approval)
                                               ↓
Phase 3: Release Spec Synthesis ──────────────┐
    ├─ 3a: Template instantiation              │
    ├─ 3b: Content population from P1 + P2     │
    ├─ 3c: Automated brainstorm (3 personas)   │
    └─ 3d: Gap incorporation                   │
    → portify-release-spec.md (draft)          │
                                               │ (automatic gate)
                                               ↓
Phase 4: Spec Panel Review ───────────────────┐
    ├─ 4a: Focus pass (4 experts)              │
    ├─ 4b: Focus incorporation                 │
    ├─ 4c: Critique pass (4 experts)           │
    └─ 4d: Critique incorporation + scoring    │
    → portify-release-spec.md (final)          │
    → panel-report.md                          │
                                               │ (user approval)
                                               ↓
               Downstream: sc:roadmap → sc:tasklist → sc:implement
```

### Phase details

| Phase | Name | Ref Loaded | User Gate | Dry-Run |
|-------|------|------------|-----------|---------|
| 1 | Workflow Analysis | `refs/analysis-protocol.md` | Review before Phase 2 | Executed |
| 2 | Pipeline Specification | `refs/pipeline-spec.md` | Approval before Phase 3 | Executed |
| 3 | Release Spec Synthesis | Template from `src/superclaude/examples/` | Automatic (zero placeholders + brainstorm section) | Skipped |
| 4 | Spec Panel Review | None (embedded patterns) | Approval before delivery | Skipped |

### Output artifacts

| Artifact | Source Phase | Description |
|----------|------------|-------------|
| `portify-analysis.md` | Phase 1 | Component inventory, step graph, gates, data flow diagram |
| `portify-spec.md` | Phase 2 | Models, gates, executor design, pure-programmatic implementations |
| `portify-prompts.md` | Phase 2 | Prompt builders (optional, if prompts exceed ~300 lines) |
| `portify-release-spec.md` | Phase 3+4 | Complete reviewed release specification |
| `panel-report.md` | Phase 4 | Focus findings, critique scores, convergence status |

---

## 4) Phase 1: Workflow Analysis

### Purpose
Decompose the target workflow into a structured pipeline specification.

### Process
1. **Discover components** — Find command `.md`, skill `SKILL.md`, all `refs/`, `rules/`, `templates/`, `scripts/`, and referenced agents. Build component inventory table.
2. **Map the protocol** — Extract step-by-step behavioral flow, noting wave/phase boundaries, agent delegation patterns, conditional paths, and inter-step data flow.
3. **Identify steps** — Apply step boundary algorithm: new artifact produced, different agent, execution mode change, quality gate, or operation type change.
4. **Classify each step** on the programmatic spectrum:
   - **Pure programmatic** — Deterministic Python function (e.g., file inventory, batch assignment)
   - **Claude-assisted** — Claude subprocess with prompt contract and gate (e.g., content analysis)
   - **Hybrid** — Programmatic setup → Claude → programmatic validation
5. **Map dependencies and parallel groups** — Draw data flow, identify concurrent opportunities.
6. **Extract gates** — Map to tiers: EXEMPT, LIGHT, STANDARD, STRICT.
7. **Assign gate modes** — BLOCKING for data-flow steps, TRAILING for quality-only checks.

### Classification decision framework

| Operation | Classification | Rationale |
|-----------|---------------|-----------|
| Enumerate repo files | Pure programmatic | `git ls-files` + patterns — deterministic |
| Classify file domains | Pure programmatic | Extension/path rules, no judgment |
| Assign files to batches | Pure programmatic | Math: divide by batch_size |
| Filter between passes | Pure programmatic | Parse markdown, extract, filter |
| Analyze file for issues | Claude-assisted | Requires reading code, understanding context |
| Score variant quality | Hybrid | Formulas programmatic, rubric evaluation Claude |
| Validate structural integrity | Pure programmatic | Regex, section presence, field counts |
| Merge batch reports | Claude-assisted | Synthesis, deduplication, pattern extraction |
| Generate executive summary | Claude-assisted | Narrative synthesis |

**Rule of thumb**: If you can write a Python function with clear input→output types and no ambiguity, make it programmatic.

### Output format
`portify-analysis.md` with YAML frontmatter (`source_skill`, `step_count`, `parallel_groups`, `gate_count`, `complexity`) and sections: Source Components, Step Graph, Parallel Groups, Gates Summary, Agent Delegation Map, Data Flow Diagram, Classification Summary, Recommendations.

---

## 5) Phase 2: Pipeline Specification

### Purpose
Convert the Phase 1 analysis into concrete, code-ready specifications.

### Process
1. **Design Step graph** — Map steps to `Step` objects. Dynamic counts use `build_steps()`.
2. **Define models** — Config (extends `PipelineConfig`), Status enum, Result, MonitorState, TurnLedger integration.
3. **Design prompts** — Prompt builders specifying input embedding, output format, machine-readable markers (`EXIT_RECOMMENDATION: CONTINUE|HALT`), and structural requirements.
4. **Design gates** — `GateCriteria` with tier, frontmatter, min lines, semantic checks. All checks return `tuple[bool, str]`.
5. **Implement pure-programmatic steps** — Full runnable Python code (not descriptions).
6. **Design executor** — Sprint-style synchronous supervisor with `ThreadPoolExecutor`, stall detection, TurnLedger guards, signal-aware shutdown.
7. **Plan integration** — Click command group, main.py import, file generation order.

### Critical constraints
1. **Synchronous execution** — `threading` + `time.sleep()` polling. No `async/await`.
2. **Gate function signatures** — `tuple[bool, str]` return type.
3. **Runner-authored truth** — Reports from observed data, not Claude self-reporting.
4. **Deterministic flow control** — Python makes all "what's next" decisions.

### Shared pipeline primitives
Reuse from `superclaude.cli.pipeline`:
- `PipelineConfig`, `Step`, `StepResult`, `GateMode`, `GateCriteria`, `SemanticCheck`, `gate_passed()`, `ClaudeProcess`

From `superclaude.cli.sprint`:
- `TurnLedger` (budget tracking)

### Output format
`portify-spec.md` (under 800 lines; split prompts to `portify-prompts.md` if exceeded).

---

## 6) Phase 3: Release Spec Synthesis

### Purpose
Generate a complete release specification from Phase 1 and Phase 2 outputs.

### Entry gate
- Phase 2 contract `status: completed`
- All blocking checks passed
- Phase 2 `step_mapping` contains >= 1 entry

### Steps

#### 3a: Template Instantiation
Load the release spec template from `src/superclaude/examples/release-spec-template.md` and create a working copy at `{work_dir}/portify-release-spec.md`.

#### 3b: Content Population
Fill template sections by replacing `{{SC_PLACEHOLDER:*}}` sentinels with content from Phase 1 and Phase 2:

| Template Section | Source |
|-----------------|--------|
| Problem Statement | Source workflow purpose + portification rationale |
| Solution Overview | Phase 2 pipeline architecture |
| Workflow / Data Flow | Phase 1 data flow diagram |
| Functional Requirements | One FR per Phase 2 step (every step MUST produce an FR) |
| Architecture | Phase 2 module plan |
| Data Models | Phase 2 model designs |
| Gate Criteria | Phase 2 gate definitions |
| NFRs | Standard portification NFRs (sync execution, gate signatures, runner-authored truth) |
| Risk Assessment | Phase 1 classification confidence + unsupported patterns |
| Test Plan | Phase 2 pattern coverage matrix |
| Downstream Inputs | Themes for sc:roadmap, tasks for sc:tasklist |

After population, run self-validation: verify zero remaining `{{SC_PLACEHOLDER:*}}` sentinels.

#### 3c: Automated Brainstorm Pass
Apply three persona perspectives (non-interactive, NOT a `sc:brainstorm` invocation):

1. **Architect**: Structural gaps — missing dependencies, incomplete module boundaries, scaling concerns
2. **Analyzer**: Logical gaps — uncovered edge cases, ambiguous requirements, missing acceptance criteria
3. **Backend**: Implementation gaps — missing data models, incomplete API contracts, undefined error states

Each finding: `{gap_id, description, severity(high|medium|low), affected_section, persona}`

Zero gaps is a valid outcome.

#### 3d: Gap Incorporation
- **Actionable findings** → Incorporate into relevant spec section, mark `[INCORPORATED]`
- **Unresolvable items** → Route to Section 11 (Open Items), mark `[OPEN]`

### Timing
Advisory target: 10 minutes wall clock (NFR-001). Exceeding emits warning but does not halt.

### Exit gate
Draft spec populated (zero `{{SC_PLACEHOLDER:*}}` sentinels) AND brainstorm section (Section 12) present.

---

## 7) Phase 4: Spec Panel Review

### Purpose
Convergent expert review ensuring specification quality before downstream consumption.

### Expert Analysis Patterns

#### Focus Pass (Step 4a)
Four expert patterns applied in sequence:

| Expert | Focus | Key Analysis |
|--------|-------|-------------|
| **Fowler** (Architecture) | Interface design, bounded contexts, coupling/cohesion | Count divergence analysis on data flows |
| **Nygard** (Reliability) | Failure modes, circuit breakers, timeouts, retries | Zero/empty case guard analysis |
| **Whittaker** (Adversarial) | Zero/Empty, Divergence, Sentinel Collision, Sequence, Accumulation attacks | Concrete attack scenarios with state traces |
| **Crispin** (Testing) | Coverage, acceptance criteria, edge cases | Boundary value test cases for all guards |

Finding format: `{finding_id, severity(CRITICAL|MAJOR|MINOR), expert, location, issue, recommendation}`

#### Focus Incorporation (Step 4b)
- **CRITICAL** → Must incorporate OR document dismissal justification
- **MAJOR** → Incorporate into spec body (additive-only)
- **MINOR** → Append to Open Items

#### Critique Pass (Step 4c)
Full expert panel produces quality dimension scores:
- `clarity` (0-10): Language precision, unambiguous requirements
- `completeness` (0-10): Coverage, no missing requirements
- `testability` (0-10): Measurable acceptance criteria
- `consistency` (0-10): Internal coherence, no contradictions

#### Scoring (Step 4d)
`overall = mean(clarity, completeness, testability, consistency)` — simple arithmetic mean, no weighting.

### Convergence Loop

State machine with bounded iterations:

```
REVIEWING → INCORPORATING → SCORING → CONVERGED (zero unaddressed CRITICALs)
                                    → REVIEWING (CRITICALs remain, iteration < 3)
                                    → ESCALATED (CRITICALs remain, iteration >= 3)
```

**Max iterations**: 3 (hard cap).

**Terminal states**:
- **CONVERGED** — `status: success`, all CRITICALs addressed
- **ESCALATED** — `status: partial`, unaddressed CRITICALs escalated to user

### Downstream Ready Gate
After convergence: `if overall >= 7.0 then downstream_ready = true else false`
- Boundary: `7.0` → true; `6.9` → false

### Timing
Advisory target: 15 minutes wall clock (NFR-002).

---

## 8) Return Contract Schema

The return contract is emitted on **every invocation** (success, partial, failure, dry-run).

### Contract fields

```yaml
# Identity
contract_version: "2.0"
spec_file: "<path>"
panel_report: "<path>"
output_directory: "<path>"

# Quality Scores
quality_scores:
  clarity: <float>          # 0.0-10.0
  completeness: <float>     # 0.0-10.0
  testability: <float>      # 0.0-10.0
  consistency: <float>      # 0.0-10.0
  overall: <float>          # mean of above

# Convergence
convergence_iterations: <int>
convergence_state: "CONVERGED|ESCALATED|NOT_STARTED"

# Timing
phase_timing:
  phase_3_seconds: <float>
  phase_4_seconds: <float>

# Pipeline Metadata
source_step_count: <int>
spec_fr_count: <int>
api_snapshot_hash: "<hash>"

# Downstream Readiness
downstream_ready: <bool>    # true if overall >= 7.0

# Phase Contracts
phase_contracts:
  phase_0: "completed|skipped|failed"
  phase_1: "completed|skipped|failed"
  phase_2: "completed|skipped|failed"
  phase_3: "completed|skipped|failed"
  phase_4: "completed|skipped|failed"

# Warnings
warnings: []

# Failure Information
status: "success|partial|failed|dry_run"
failure_phase: <int|null>
failure_type: "<type|null>"

# Resume Support
resume_phase: <int|null>
resume_substep: "<substep|null>"
resume_command: "<command|null>"
```

### Failure type enumeration

| Value | Description | Resumable | Resume Point |
|-------|-------------|-----------|--------------|
| `template_failed` | Release spec template could not be loaded | No | — |
| `brainstorm_failed` | Brainstorm pass failed to produce findings | Yes | `3c` |
| `brainstorm_timeout` | Brainstorm exceeded time budget | Yes | `3c` |
| `focus_failed` | Panel focus pass failed | Yes | `4a` |
| `critique_failed` | Panel critique pass failed | Yes | `4a` |
| `convergence_exhausted` | Max 3 iterations with unresolved CRITICALs | No | — |
| `user_rejected` | User rejected spec at approval gate | No | — |
| `prerequisite_failed` | Phase entry gate condition not met | No | — |

### Failure path defaults
- All `quality_scores` → `0.0` (not null)
- `downstream_ready` → `false`
- `convergence_state` → `NOT_STARTED`
- `spec_file`, `panel_report` → `""` (empty string)

### Dry-run contract
- `status: dry_run`
- Phases 1-2 contracts populated; Phases 3-4 marked `skipped`
- All quality scores `0.0`, `downstream_ready: false`

---

## 9) Architectural Decision Records

The `decisions.yaml` file tracks 15 decisions across two generations:

### Blocking Implementation Decisions (OQ series — v2.18)

| ID | Title | Resolution |
|----|-------|-----------|
| OQ-002 | TurnLedger location | Import from `sprint.models`, not `pipeline.models` |
| OQ-003 | Dry-run behavior | Phases 0-2 only, emit contracts |
| OQ-004 | Integration schema | 8-field `portify-integration.yaml` |
| OQ-007 | Approval gate mechanism | TodoWrite checkpoint pattern |
| OQ-008 | Default output path | `src/superclaude/cli/<derived_name>/` |
| OQ-010 | Step boundary algorithm | Documented in `refs/analysis-protocol.md` |

### Architectural Decisions (ADR series — v2.23)

| ID | Title | Resolution |
|----|-------|-----------|
| ADR-C01 | Inline behavioral embedding | No inter-skill invocation; embed patterns inline |
| ADR-C02 | Additive-only incorporation | Append/extend only, never rewrite |
| ADR-C04 | Template location | `src/superclaude/examples/release-spec-template.md` |
| ADR-C05 | Placeholder sentinel | `{{SC_PLACEHOLDER:name}}` format |
| ADR-C06 | Quality score formula | `overall = mean(4 dimensions)`, no weighting |
| ADR-C07 | CRITICAL finding disposition | Incorporate OR justify-dismiss (both "addressed") |
| ADR-C08 | Downstream-ready threshold | `overall >= 7.0` |
| ADR-C09 | Implementation order | Fully sequential phase dependency chain |
| ADR-C10 | Component sync | `make sync-dev` + `make verify-sync` |
| ADR-SM01 | State machine convergence | REVIEWING → INCORPORATING → SCORING → CONVERGED\|ESCALATED |

---

## 10) What Gets Generated (Target Pipeline Structure)

When the reviewed spec is eventually implemented via `sc:roadmap` → `sc:tasklist` → `sc:implement`, the target output is a CLI subcommand package:

```
src/superclaude/cli/<name>/
├── __init__.py         # Package exports
├── models.py           # Domain types extending PipelineConfig, Step, StepResult
├── gates.py            # GateCriteria + semantic check functions
├── prompts.py          # LLM contract builders per Claude-assisted step
├── config.py           # CLI arg resolution, file discovery, config construction
├── executor.py         # Synchronous supervisor with ThreadPoolExecutor
├── monitor.py          # NDJSON incremental output parser
├── process.py          # ClaudeProcess subclass with domain-specific prompts
├── tui.py              # Rich live dashboard with gate state machine
├── logging_.py         # Dual JSONL + Markdown execution logging
├── diagnostics.py      # DiagnosticCollector, FailureClassifier, ReportGenerator
├── commands.py         # Click CLI group and subcommands
├── inventory.py        # Pure-programmatic file discovery (if applicable)
└── filtering.py        # Pure-programmatic inter-step filtering (if applicable)
```

---

## 11) End-to-End Workflow: Skill → Spec → Roadmap → Tasklist → Implementation

### Stage A: Identify workflow to portify
Select an inference-based SuperClaude skill that needs deterministic execution.

### Stage B: Portification analysis and specification (this tool)
```bash
/sc:cli-portify --workflow sc-cleanup-audit-protocol
```
Produces `portify-release-spec.md` (reviewed) + `panel-report.md`.

### Stage C: Roadmap generation
```bash
superclaude roadmap run portify-release-spec.md --depth standard
```
Produces adversarially validated `roadmap.md` + `test-strategy.md`.

### Stage D: Tasklist generation
```bash
# Use /sc:tasklist to generate Sprint CLI-compatible phase files
```
Produces `tasklist-index.md` + phase files.

### Stage E: Sprint execution
```bash
superclaude sprint run tasklist-index.md
```
Executes phases with supervised Claude sessions.

### Stage F: Resume on halt
```bash
# Sprint level
superclaude sprint run tasklist-index.md --start <halt_phase>
```

---

## 12) Practical Use Cases

### Use case 1: Standard portification
```bash
/sc:cli-portify --workflow src/superclaude/skills/sc-cleanup-audit-protocol/
```
Full 4-phase protocol: analysis → specification → spec synthesis → panel review. Artifacts in the skill's output directory.

### Use case 2: Dry-run analysis only
```bash
/sc:cli-portify --workflow sc-adversarial --dry-run
```
Phases 1-2 only. Produces `portify-analysis.md` and `portify-spec.md`. No spec synthesis or panel review. Use this to evaluate portification feasibility before committing to full execution.

### Use case 3: Custom output directory
```bash
/sc:cli-portify --workflow sc-tasklist-protocol \
  --name tasklist \
  --output src/superclaude/cli/tasklist/
```
Explicit name and output path for the target CLI module.

### Use case 4: Already-portified workflow (collision detection)
```bash
/sc:cli-portify --workflow sc-roadmap-protocol
```
Triggers `NAME_COLLISION` error because `src/superclaude/cli/roadmap/` already exists. Use `--name` to specify an alternative.

---

## 13) Version History

| Version | Release | Key Changes |
|---------|---------|-------------|
| v1.0 (v2.15) | Initial | 5-phase protocol with code generation (Phases 3-4 produce Python files) |
| v2.0 (v2.18) | Refactor | Command/protocol split, phase contracts, `refs/` reference architecture |
| v3.0 (v2.23) | Evolution | Replace code generation with spec synthesis + panel review; embedded brainstorm/spec-panel; convergent review loop; return contract schema v2.0 |

---

## 14) Troubleshooting Checklist

### Before running
- [ ] Workflow path resolves to a directory with `SKILL.md`
- [ ] Output directory parent is writable
- [ ] Derived CLI name doesn't collide with existing modules
- [ ] Release spec template exists at `src/superclaude/examples/release-spec-template.md`

### After a failure
- [ ] Check the return contract `failure_type` for classification
- [ ] For `brainstorm_failed`/`brainstorm_timeout`: Review draft spec quality, consider simplifying the source workflow
- [ ] For `focus_failed`/`critique_failed`: Check if Phase 2 spec has sufficient detail for expert analysis
- [ ] For `convergence_exhausted`: Review remaining CRITICAL findings in `panel-report.md` — manual resolution required
- [ ] For `prerequisite_failed`: Verify Phase 2 contract status and step_mapping
- [ ] Use resume support from contract to restart from the failure substep

### Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `MISSING_WORKFLOW` error | `--workflow` not provided | Add `--workflow <path>` argument |
| `INVALID_PATH` error | Path doesn't contain `SKILL.md` | Verify path; use full directory path |
| `NAME_COLLISION` error | Target CLI module already exists | Use `--name <alternative>` to avoid collision |
| Phase 3 entry gate fails | Phase 2 incomplete or no step mappings | Complete Phase 2 with user approval first |
| Convergence loop escalates | Persistent CRITICAL findings | Review panel-report.md; resolve manually |
| Quality score below 7.0 | Spec needs improvement | Address MAJOR findings; re-run Phase 4 |
| `{{SC_PLACEHOLDER:*}}` remains | Template population incomplete | Check Phase 2 outputs for missing data |

---

## 15) Notes for Workflow Operators

- The cli-portify protocol is a **planning** tool. It produces specifications, not code. Implementation follows via the standard `sc:roadmap` → `sc:tasklist` → `sc:implement` pipeline.
- Use `--dry-run` to evaluate portification feasibility before investing in full synthesis and review.
- The quality scoring threshold (`overall >= 7.0`) is a gate, not a guarantee. Specs at 7.0 are minimally acceptable; higher scores indicate better specification quality.
- The convergence loop (max 3 iterations) balances thoroughness against token cost. Most well-specified workflows converge in 1-2 iterations.
- `code-templates.md` in `refs/` is preserved as a historical reference only. It is NOT loaded by any current workflow phase.
- All 15 architectural decisions in `decisions.yaml` are documented with evidence and impact. Consult these before proposing changes to the protocol.
- The command shim validates inputs before any protocol work begins. Invalid inputs fail fast with actionable error messages.
