---
name: sc-cli-portify-protocol
description: "Full behavioral protocol for sc:cli-portify — port inference-based SuperClaude workflows into programmatic CLI pipelines with sprint-style supervised execution."
category: development
complexity: high
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
mcp-servers: [sequential, serena, context7, auggie-mcp]
personas: [architect, analyzer, backend]
argument-hint: "--workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>] [--dry-run]"
---

# sc:cli-portify — Workflow-to-CLI Pipeline Compiler

Convert inference-based SuperClaude workflows into programmatic CLI pipelines that ensure 100% completion and consistency between runs.

## Purpose

SuperClaude workflows implemented as commands + skills + agents + refs rely entirely on Claude's reasoning for orchestration. This works well for flexible, one-off tasks but breaks down for repeatable multi-step pipelines where you need:

- **Deterministic control flow** — Python decides what runs when, not inference
- **Formal artifact validation** — Gates check output quality programmatically
- **Resume/retry** — Failed steps resume without re-running everything
- **Live monitoring** — TUI shows progress, stall detection, diagnostics
- **Budget economics** — Turn ledger tracks consumption across subprocesses
- **Consistent behavior** — Same inputs produce structurally identical outputs every run

The existing `pipeline/` and `sprint/` modules already solve these problems. This skill bridges the gap by analyzing a workflow and generating a new CLI module that uses these proven patterns.

## What Gets Generated

A CLI subcommand package under `src/superclaude/cli/<name>/`:

| File | Purpose | When Generated |
|------|---------|----------------|
| `models.py` | Domain types extending `PipelineConfig`, `Step`, `StepResult` | Always |
| `gates.py` | `GateCriteria` + semantic check functions returning `tuple[bool, str]` | Always |
| `prompts.py` | LLM contract builders per Claude-assisted step | Always |
| `config.py` | CLI arg resolution, file discovery, config construction | Always |
| `executor.py` | Synchronous supervisor loop with `ThreadPoolExecutor` for parallelism | Always |
| `monitor.py` | NDJSON incremental output parser with domain signals | Always |
| `process.py` | `ClaudeProcess` subclass with domain-specific prompt building | Always |
| `tui.py` | Rich live dashboard with gate state machine | Always |
| `logging_.py` | Dual JSONL + Markdown execution logging | Always |
| `diagnostics.py` | `DiagnosticCollector`, `FailureClassifier`, `ReportGenerator` | Always |
| `commands.py` | Click CLI group and subcommands | Always |
| `__init__.py` | Package exports | Always |
| `inventory.py` | Pure-programmatic file discovery/classification | If workflow has discovery steps |
| `filtering.py` | Pure-programmatic inter-step data filtering | If workflow has filtering between steps |

These file definitions inform the pipeline specification produced in Phase 2.

## Required Input

```
/sc:cli-portify --workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `--workflow` | Yes | Skill directory path or `sc-*` name to portify |
| `--name` | No | CLI subcommand name (default: derived from workflow) |
| `--output` | No | Output directory (default: `src/superclaude/cli/<name>/`) |
| `--dry-run` | No | Execute Phases 0-2 only — emit Phase 0-2 contracts only. No spec synthesis (Phase 3) or panel review (Phase 4) artifacts are produced. |

**STOP** if `--workflow` is not provided or the path doesn't resolve to a valid skill.

## Behavioral Flow

Four phases, each producing artifacts that feed the next. Present output to user for review after Phases 1 and 2 before continuing.

### Phase 1: Workflow Analysis

Load `refs/analysis-protocol.md` before this phase. It contains the discovery checklist, step decomposition algorithm, classification rubric, and output format template.

**Goal**: Decompose the target workflow into a structured pipeline specification.

1. **Discover components** — Find the command `.md`, skill `SKILL.md`, all `refs/` and `rules/`, all `templates/`, all `scripts/`, and all referenced agents. Build a component inventory table with paths, line counts, and purposes.

2. **Map the protocol** — Extract the step-by-step behavioral flow. Pay attention to:
   - Wave/phase boundaries in the skill
   - Agent delegation patterns (which agent, parallel vs sequential)
   - Conditional execution paths (flags that skip steps)
   - Implicit inter-step data flow (what one step produces that another consumes)

3. **Identify steps** — A new Step boundary exists when:
   - A new artifact is produced
   - A different agent takes over
   - Execution mode changes (sequential → parallel)
   - A quality gate must be evaluated
   - Operation type changes (analysis → generation → validation)

4. **Classify each step** on the programmatic spectrum:
   - **Pure programmatic**: Runs as a Python function, no Claude subprocess. Examples: file inventory via `git ls-files`, config construction, file filtering between passes, scoring formulas, structural validation, batch assignment. If the logic is deterministic and the input/output formats are well-defined, it should be programmatic.
   - **Claude-assisted**: Runs as a Claude subprocess with a prompt contract and gate. Examples: content analysis, writing reports, rubric-based assessment, creative synthesis, debate.
   - **Hybrid**: Programmatic setup → Claude subprocess → programmatic validation. Examples: steps that need Claude for content but have strict structural validation on the output.

5. **Map dependencies and parallel groups** — Draw the data flow: which steps produce artifacts consumed by downstream steps? Which steps are independent and can run concurrently? For batched workflows, identify where batch parallelism applies.

6. **Extract gates** — For each step output, identify what validation the original workflow expects. Map these to gate tiers: EXEMPT (informational), LIGHT (exists + non-empty), STANDARD (structural checks), STRICT (structural + semantic).

7. **Assign gate modes** — `GateMode.BLOCKING` for steps whose output feeds downstream steps. `GateMode.TRAILING` for quality-only checks that don't affect data flow.

**Output**: `portify-analysis.md` — Complete decomposition following the template in `refs/analysis-protocol.md`. Must include: component inventory, step graph with classifications, parallel groups, gates summary, data flow diagram, and recommendations.

**Present to user for review before Phase 2.**

### Phase 2: Pipeline Specification

Load `refs/pipeline-spec.md` before this phase. It contains Step definition patterns, model design patterns, gate patterns, executor patterns, and the new unified-audit-gating patterns (TurnLedger, gate modes, subprocess isolation, context injection, resume semantics).

**Goal**: Convert the analysis into concrete, code-ready specifications.

1. **Design the Step graph** — Map each workflow step to `Step` objects. Batched parallel steps are `list[Step]` groups. Dynamic step counts (e.g., batch count determined at runtime) require a `build_steps()` function.

2. **Define models** — Design domain-specific dataclasses:
   - Config extending `PipelineConfig` with workflow-specific fields (source paths, pass selection, batch sizes, stall/timeout policies)
   - Status enum with domain-specific states (e.g., `VALIDATION_FAIL`, `CRITICAL_FAIL` for audit workflows)
   - Result extending `StepResult` with execution telemetry
   - Aggregate result with `resume_command()` and `suggested_resume_budget`
   - Monitor state with domain-specific NDJSON signals
   - `TurnLedger` integration for budget tracking

3. **Design prompts** — For each Claude-assisted step, write the prompt builder. Each prompt must specify:
   - What input files/context to embed (inline for <50KB, `--file` args for larger)
   - Required output sections and frontmatter fields
   - Machine-readable markers: `EXIT_RECOMMENDATION: CONTINUE|HALT`
   - Any structural requirements the gate will check

   If prompts collectively exceed ~300 lines, put them in a separate `portify-prompts.md`.

4. **Design gates** — For each output artifact, define:
   - `GateCriteria` with tier, required frontmatter, min lines, semantic checks
   - `GateMode` (BLOCKING or TRAILING)
   - All semantic check functions returning `tuple[bool, str]`

5. **Implement pure-programmatic steps** — Write actual runnable Python code for steps classified as "pure programmatic". These run as direct function calls in the executor, bypassing `ClaudeProcess`. Include: file discovery, domain classification, batch assignment, inter-pass filtering, config construction.

6. **Design the executor** — Sprint-style synchronous supervisor:
   - `ThreadPoolExecutor` for batch parallelism (NOT async/await)
   - `time.sleep()` polling loops for monitoring
   - Per-step/batch monitoring with stall detection
   - `TurnLedger` budget guards before each launch
   - Runner-authored truth: reports from observed data, not Claude self-reporting
   - Subprocess isolation (4-layer model) for child Claude sessions
   - Context injection: prior results compressed into subsequent prompts
   - Signal-aware shutdown with `SignalHandler`

7. **Plan integration** — Click command group, main.py import, file generation order.

**Output**: `portify-spec.md` (+ optional `portify-prompts.md`) — Complete code spec with models, gates, executor design, pure-programmatic implementations, and integration plan.

**Present to user for approval before Phase 3.**

### Phase 3: Release Spec Synthesis

**Phase 2→3 Entry Gate**: Before beginning Phase 3, verify ALL of the following:
- Phase 2 contract `status: completed`
- All blocking checks passed (no unresolved BLOCKING gate failures)
- Phase 2 `step_mapping` contains ≥1 entry

**STOP** if any entry gate condition fails. Report which condition failed and emit the return contract with `failure_phase: 3, failure_type: prerequisite_failed`.

**Goal**: Generate a complete, reviewed release specification from Phase 1 and Phase 2 outputs. Record the wall clock start time for `phase_3_seconds` timing instrumentation.

**Timing**: Record `phase_3_start = current_time()` at the beginning of this phase. NFR-001 advisory target: Phase 3 should complete within 10 minutes wall clock (non-blocking; exceeding this target emits a warning but does not halt the pipeline).

#### Step 3a: Template Instantiation

1. Load the release spec template from `src/superclaude/examples/release-spec-template.md`
2. Create a working copy at `{work_dir}/portify-release-spec.md`
3. Verify the working copy was created successfully and contains the template content

#### Step 3b: Content Population

Fill template sections from Phase 1 (workflow analysis) and Phase 2 (pipeline specification) outputs using the following mapping table. For each template section, replace `{{SC_PLACEHOLDER:*}}` sentinels with content derived from the specified source:

| # | Template Section | Source |
|---|-----------------|--------|
| 1 | Problem Statement | Derive from source workflow's purpose + why portification is needed |
| 2 | Solution Overview | Phase 2 pipeline architecture (step graph, executor design) |
| 2.2 | Workflow / Data Flow | Phase 1 data flow diagram, adapted for the target pipeline |
| 3 | Functional Requirements | One FR per generated pipeline step from Phase 2 `step_mapping` — every `step_mapping` entry MUST produce a corresponding FR (SC-004) |
| 4 | Architecture | Phase 2 `module_plan` (new files), Phase 0 prerequisites (modified files) |
| 4.5 | Data Models | Phase 2 model designs (Config, Status, Result, MonitorState) |
| 4.6 | Implementation Order | Phase 2 module dependency order |
| 5.2 | Gate Criteria | Phase 2 `gate_definitions` |
| 5.3 | Phase Contracts | Phase 1+2 contract schemas |
| 6 | NFRs | Standard portification NFRs (sync execution, gate signatures, runner-authored truth) |
| 7 | Risk Assessment | Derived from Phase 1 classification confidence scores + unsupported patterns |
| 8 | Test Plan | Structural test plan from Phase 2 pattern coverage matrix |
| 10 | Downstream Inputs | Themes for sc:roadmap, tasks for sc:tasklist |

After populating all sections, run SC-003 self-validation: verify zero remaining `{{SC_PLACEHOLDER:*}}` sentinels in the working copy. If any remain, resolve them before proceeding.

#### Step 3c: Automated Brainstorm Pass

Apply embedded brainstorm behavioral patterns as a non-interactive automated pass against the draft spec. This is NOT an invocation of the `sc:brainstorm` command (which is interactive/Socratic); instead, cycle through each of three personas to analyze the draft spec for gaps:

**Persona perspectives** (apply each in sequence):

1. **Architect persona**: Analyze for structural gaps — missing dependencies, incomplete module boundaries, scaling concerns, cross-module interaction gaps, missing error handling paths
2. **Analyzer persona**: Analyze for logical gaps — uncovered edge cases, ambiguous requirements, missing acceptance criteria, inconsistent cross-references, untestable requirements
3. **Backend persona**: Analyze for implementation gaps — missing data models, incomplete API contracts, undefined error states, missing retry/timeout specifications, resource lifecycle gaps

**Structured output format**: Each finding uses the schema:
```
{gap_id, description, severity(high|medium|low), affected_section, persona}
```

Example:
```
{GAP-001, "No retry policy defined for failed gate checks", medium, "5.2 Gate Criteria", architect}
```

**Zero-gap handling**: If no gaps are identified across all three personas, produce an explicit summary:
> "No gaps identified by architect, analyzer, and backend personas. Spec coverage assessed as complete."

Set `gaps_identified: 0` in the return contract. Zero gaps is a valid outcome — it does not block the pipeline.

**Output**: Append a `## Brainstorm Gap Analysis` section (Section 12) to the draft spec containing all findings in the structured format, or the zero-gap summary.

#### Step 3d: Gap Incorporation

Review each brainstorm finding and route it:

- **Actionable findings** (findings that can be directly addressed): Incorporate into the relevant spec body section identified by `affected_section`. Mark the finding as `[INCORPORATED]` in the gap analysis table.
- **Unresolvable items** (findings that require external input, are out of scope, or cannot be resolved within the spec): Route to Section 11 (Open Items) with the gap ID, question, impact, and resolution target. Mark the finding as `[OPEN]` in the gap analysis table.

After incorporation, update the gap analysis summary with counts: `{total_gaps, incorporated, open, severity_distribution}`.

**Timing**: Record `phase_3_end = current_time()`. Compute `phase_3_seconds = phase_3_end - phase_3_start`. Populate `phase_timing.phase_3_seconds` in the return contract. If `phase_3_seconds > 600`, emit warning: "Phase 3 exceeded 10-minute advisory target (NFR-001)".

**Output**: `{work_dir}/portify-release-spec.md` — Complete draft spec with brainstorm gap analysis section and incorporated findings.

**Phase 3→4 automatic gate**: Draft spec populated (no `{{SC_PLACEHOLDER:*}}` values remain) AND brainstorm section (Section 12) present in draft spec.

### Phase 4: Spec Panel Review

Embed `sc:spec-panel` behavioral patterns in a convergent review loop. Like Phase 3's brainstorm, this embeds spec-panel behavioral patterns directly rather than invoking the `sc:spec-panel` command (Constraint 1: no inter-skill command invocation).

**Timing**: Record `phase_4_start = current_time()` at the beginning of this phase. NFR-002 advisory target: Phase 4 should complete within 15 minutes wall clock (non-blocking; exceeding this target emits a warning but does not halt the pipeline).

#### Step 4a: Focus Pass

Apply spec-panel behavioral patterns with `--focus correctness,architecture` against `portify-release-spec.md`. This pass embeds four expert analysis patterns inline:

**Expert analysis patterns** (apply each in sequence, building on prior context):

1. **Fowler (Architecture)**: Analyze interface design quality, bounded context boundaries, module coupling/cohesion, dependency direction, and design pattern appropriateness. Annotate data flows with count divergence analysis — for each transformation, document input count, output count, and whether the spec accounts for count differences.

2. **Nygard (Reliability/Failure Modes)**: Analyze failure mode coverage, circuit breaker patterns, timeout specifications, retry policies, and recovery mechanisms. Extend guard boundary analysis to include zero/empty cases — for every guard condition, verify the spec defines behavior for zero, empty, null, and negative inputs.

3. **Whittaker (Adversarial)**: Apply five attack methodologies (Zero/Empty, Divergence, Sentinel Collision, Sequence, Accumulation) against each identified invariant. Produce concrete attack scenarios with state traces demonstrating specification gaps.

4. **Crispin (Testing)**: Analyze testing strategy coverage, acceptance criteria quality, edge case identification, and quality attribute specifications. Generate boundary value test cases for every guard condition and state variable covering: below minimum, at minimum, typical, at maximum, above maximum, and degenerate (zero/empty/null).

**Focus dimensions**: `correctness` and `architecture` — findings must address both dimensions (SC-006).

**Output format**: Each finding uses the structured schema:
```
{finding_id, severity(CRITICAL|MAJOR|MINOR), expert, location, issue, recommendation}
```

Where:
- `finding_id`: Unique identifier (e.g., `F-001`, `F-002`)
- `severity`: One of `CRITICAL` (spec provably wrong), `MAJOR` (spec ambiguous/incomplete), `MINOR` (spec could be clearer)
- `expert`: One of `Fowler`, `Nygard`, `Whittaker`, `Crispin`
- `location`: Section/requirement reference in the spec
- `issue`: Description of the identified problem
- `recommendation`: Specific actionable fix

Additionally produce, if applicable:
- Guard Condition Boundary Table (Nygard leads, Crispin validates, Whittaker attacks)
- Pipeline Quantity Flow Diagram (Fowler leads, if pipeline stages detected)
- State Variable Registry (if 3+ mutable state variables identified)

#### Step 4b: Focus Incorporation

Review focus findings from step 4a. Route each finding by severity level. All modifications MUST be additive-only — append or extend spec sections only, do not rewrite existing content (Constraint 2, NFR-008).

**Severity routing**:

- **CRITICAL findings**: MUST be addressed. Either:
  - Incorporate the fix into the relevant spec body section identified by `location`, OR
  - Document a written justification for dismissal in the panel report (Constraint 7). Dismissal justification must include: `finding_id`, reason for dismissal, and assessment of downstream impact.
- **MAJOR findings**: Incorporate into the corresponding spec body section identified by `location`. Modifications use append/extend only.
- **MINOR findings**: Append to Section 11 (Open Items) with the `finding_id`, issue summary, and recommended resolution target.

All modifications are traceable by `finding_id` from step 4a output. Mark each finding as `[INCORPORATED]`, `[DISMISSED]`, or `[OPEN]` in the focus findings table.

#### Step 4c: Critique Pass

Apply spec-panel behavioral patterns with `--mode critique` against the updated spec (after step 4b incorporation). Run the full expert panel in critique review sequence:

1. Fowler — Architecture and interface design
2. Nygard — Reliability and failure mode analysis
3. Whittaker — Adversarial attack-based specification probing
4. Crispin — Testing strategy and acceptance criteria

Each expert produces quality dimension scores and prioritized improvement recommendations.

**Quality score output** (SC-007):
```
{clarity: float, completeness: float, testability: float, consistency: float}
```

Where each dimension is a float in the 0-10 range:
- `clarity` (0.0-10.0): Language precision, unambiguous requirements, clear behavioral definitions
- `completeness` (0.0-10.0): Coverage of essential elements, no missing requirements, all edge cases addressed
- `testability` (0.0-10.0): Measurable acceptance criteria, verifiable requirements, concrete test scenarios
- `consistency` (0.0-10.0): Internal coherence, no contradictions, aligned cross-references

Each expert also produces prioritized improvement recommendations as new findings using the same structured schema from step 4a.

#### Step 4d: Critique Incorporation and Scoring

1. **Record quality scores**: Write all 4 quality dimension scores from step 4c into the spec frontmatter:
   ```yaml
   quality_scores:
     clarity: <float>
     completeness: <float>
     testability: <float>
     consistency: <float>
     overall: <float>
   ```

2. **Compute overall score**: `overall = mean(clarity, completeness, testability, consistency)` — that is, `overall = (clarity + completeness + testability + consistency) / 4` (Constraint 6, SC-010).

3. **Append panel report**: Generate `panel-report.md` in the working directory containing:
   - All focus findings from step 4a with incorporation status
   - All critique findings from step 4c with scores
   - Guard Condition Boundary Table (if produced)
   - Quality dimension scores and overall score
   - Convergence status

#### Convergence Loop

Steps 4a through 4d execute within a bounded convergence loop using state machine semantics.

**States**:
- `REVIEWING` — Executing focus pass (4a) or critique pass (4c)
- `INCORPORATING` — Executing incorporation (4b or 4d)
- `SCORING` — Evaluating convergence after scoring (4d)
- `CONVERGED` — Terminal state: zero unaddressed CRITICALs, `status: success`
- `ESCALATED` — Terminal state: 3 iterations exhausted, `status: partial`

**Transitions**:
```
REVIEWING → INCORPORATING (findings produced)
INCORPORATING → SCORING (incorporation complete, scores computed)
SCORING → CONVERGED (zero unaddressed CRITICALs remaining)
SCORING → REVIEWING (unaddressed CRITICALs remain, iteration < 3)
SCORING → ESCALATED (unaddressed CRITICALs remain, iteration >= 3)
```

**Iteration counter**: Initialize `iteration = 1` before first pass. Increment after each SCORING → REVIEWING transition. Hard cap: `max_iterations = 3` (SC-008).

**Convergence predicate**: After SCORING, check if any findings with `severity: CRITICAL` have status other than `[INCORPORATED]` or `[DISMISSED]`. If zero unaddressed CRITICALs → transition to CONVERGED. Otherwise → check iteration counter.

**Terminal states**:
- **CONVERGED**: `status: success` — all CRITICALs addressed, spec is review-complete
- **ESCALATED**: `status: partial` — 3 iterations exhausted with unaddressed CRITICALs remaining. Escalate to user with: remaining CRITICAL findings, iteration history, and recommendation for manual resolution.

#### Downstream Ready Gate

After convergence loop terminates (either CONVERGED or ESCALATED):

1. Evaluate `downstream_ready` gate: `if overall >= 7.0 then downstream_ready = true else downstream_ready = false` (Constraint 8, SC-012).
   - Boundary: `overall = 7.0` → `downstream_ready: true`
   - Boundary: `overall = 6.9` → `downstream_ready: false`

2. **Timing**: Record `phase_4_end = current_time()`. Compute `phase_4_seconds = phase_4_end - phase_4_start`. Populate `phase_timing.phase_4_seconds` in the return contract (SC-013). If `phase_4_seconds > 900`, emit warning: "Phase 4 exceeded 15-minute advisory target (NFR-002)".

3. Populate the return contract with:
   - `convergence_state`: `CONVERGED` or `ESCALATED`
   - `convergence_iterations`: number of iterations completed
   - `quality_scores`: all 4 dimensions + overall
   - `downstream_ready`: boolean
   - `phase_timing.phase_4_seconds`: elapsed seconds

**Present final spec to user for approval before delivering.**

## Decision Framework: What Becomes Programmatic

The value of portification is moving orchestration out of inference. Here are concrete examples from tested workflows:

| Operation | Classification | Why |
|-----------|---------------|-----|
| Enumerate repo files | Pure programmatic | `git ls-files` + pattern matching is deterministic |
| Classify file domains | Pure programmatic | Extension/path pattern rules, no judgment needed |
| Assign files to batches | Pure programmatic | Math: divide files by batch_size, assign to agents |
| Filter Pass 1 results for Pass 2 | Pure programmatic | Parse markdown, extract classifications, filter list |
| Analyze file for issues | Claude-assisted | Requires reading code, understanding context |
| Score variant quality | Hybrid | Formulas are programmatic, rubric evaluation is Claude |
| Validate structural integrity | Pure programmatic | Regex checks, section presence, field counts |
| Spot-check verification | Claude-assisted | Re-reads files, re-evaluates claims independently |
| Merge batch reports | Claude-assisted | Requires synthesis, deduplication, pattern extraction |
| Compute convergence score | Pure programmatic | `agreed / total` — arithmetic |
| Generate executive summary | Claude-assisted | Requires narrative synthesis |

### Rule of Thumb
If you can write a Python function for it with clear input→output types and no ambiguity, make it programmatic. If it requires reading natural language, making judgments, or synthesizing information, use Claude with a gate to verify the output.

## Pipeline Design Principles

These inform Phase 2 pipeline specification and align with the unified-audit-gating architecture in `pipeline/`.

### Critical Constraints
1. **Synchronous execution** — Sprint uses `threading` + `time.sleep()` polling. Use `concurrent.futures.ThreadPoolExecutor` for batch parallelism. Do NOT use async/await.
2. **Gate function signatures** — All semantic checks return `tuple[bool, str]`. The reason string feeds diagnostics and retry decisions.
3. **Runner-authored truth** — Reports derive from runner-observed data (exit codes, artifacts, gates, monitor signals), not Claude's self-reported status.
4. **Deterministic flow control** — Python makes all decisions about what runs next. Claude never decides "what's next".

### Shared Pipeline Patterns
5. **Reuse `pipeline/` primitives** — `PipelineConfig`, `Step`, `StepResult`, `GateMode`, `GateCriteria`, `SemanticCheck`, `gate_passed()`, `ClaudeProcess`
6. **Gate modes** — `BLOCKING` (default) stops pipeline on failure. `TRAILING` defers evaluation. Use trailing only for quality checks that don't affect downstream data flow.
7. **Turn budget** — `TurnLedger` with debit/credit/guard for multi-subprocess pipelines. Pre-launch guards prevent launching when budget too low.
8. **Subprocess isolation** — 4-layer model: scoped work dir, git ceiling, isolated plugin dir, isolated settings dir.
9. **Context injection** — Prior results serialized into subsequent prompts. Compress older, preserve recent.
10. **Resume-first failures** — On halt: exact resume command, remaining work, diagnostic path, budget suggestion.
11. **Diagnostic chain** — Runner-side failure analysis that doesn't consume turn budget.

### Output Guidance
- `portify-analysis.md`: Under 400 lines. Step graph, gates, data flow.
- `portify-spec.md`: Split prompts to separate file if spec exceeds 800 lines.
- Pure-programmatic steps: Full implementation code, not descriptions.

## Boundaries

### Will Do
- Analyze any SuperClaude skill/command/agent workflow
- Decompose into structured pipeline specification
- Generate a complete release specification via template instantiation and brainstorm pass
- Run spec panel review for quality validation
- Produce a downstream-ready spec for sc:roadmap and sc:tasklist

### Will Not Do
- Generate code files directly (use the release spec with sc:implement instead)
- Execute the generated pipeline
- Modify original skill/command/agent files
- Create new skills or agents
- Make architectural decisions about the workflow's logic

## Return Contract Schema

The return contract is emitted on **every invocation** including success, partial completion, failure, and dry-run (SC-009). All fields are always present; default values apply on failure paths.

### Contract Fields

```yaml
# --- Identity ---
contract_version: "2.0"            # Schema version for downstream compatibility
spec_file: "<path>"                 # Path to generated release spec (empty string on failure)
panel_report: "<path>"              # Path to panel-report.md (empty string if not produced)
output_directory: "<path>"          # Working directory for all artifacts

# --- Quality Scores (SC-007, SC-010) ---
quality_scores:
  clarity: <float>                  # 0.0-10.0 — Language precision, unambiguous requirements
  completeness: <float>             # 0.0-10.0 — Coverage of essential elements
  testability: <float>              # 0.0-10.0 — Measurable acceptance criteria
  consistency: <float>              # 0.0-10.0 — Internal coherence, no contradictions
  overall: <float>                  # mean(clarity, completeness, testability, consistency) (SC-010)

# --- Convergence ---
convergence_iterations: <int>       # Number of review loop iterations completed (0 on failure)
convergence_state: "<state>"        # CONVERGED | ESCALATED | NOT_STARTED

# --- Timing (SC-013) ---
phase_timing:
  phase_3_seconds: <float>          # Wall clock seconds for Phase 3 (0.0 if not reached)
  phase_4_seconds: <float>          # Wall clock seconds for Phase 4 (0.0 if not reached)

# --- Pipeline Metadata ---
source_step_count: <int>            # Number of steps identified in Phase 1 analysis
spec_fr_count: <int>                # Number of functional requirements in generated spec
api_snapshot_hash: "<hash>"         # SHA-256 of the pipeline-spec.md at time of spec generation

# --- Downstream Readiness (SC-012) ---
downstream_ready: <bool>            # true if overall >= 7.0, false otherwise
                                    # Boundary: overall = 7.0 → true; overall = 6.9 → false

# --- Phase Contracts ---
phase_contracts:
  phase_0: "<status>"               # completed | skipped | failed
  phase_1: "<status>"               # completed | skipped | failed
  phase_2: "<status>"               # completed | skipped | failed
  phase_3: "<status>"               # completed | skipped | failed
  phase_4: "<status>"               # completed | skipped | failed

# --- Warnings ---
warnings: []                        # List of advisory messages (e.g., timing threshold exceeded)

# --- Failure Information ---
status: "<status>"                  # success | partial | failed | dry_run
failure_phase: <int|null>           # Phase number where failure occurred (null on success)
failure_type: "<type|null>"         # Failure type enumeration value (null on success)

# --- Resume Support ---
resume_phase: <int|null>            # Phase to resume from (null if not resumable)
resume_substep: "<substep|null>"    # Substep within phase to resume from (null if not resumable)
resume_command: "<command|null>"    # Full CLI command to resume execution (null if not resumable)
```

### Failure Type Enumeration

The `failure_type` field uses the following enumeration to classify failures:

| Value | Description | Resumable | Resume Point |
|-------|-------------|-----------|--------------|
| `template_failed` | Release spec template could not be loaded or instantiated | No | — |
| `brainstorm_failed` | Automated brainstorm pass failed to produce findings | Yes | `3c` |
| `brainstorm_timeout` | Brainstorm pass exceeded time budget | Yes | `3c` |
| `focus_failed` | Spec panel focus pass failed to produce findings | Yes | `4a` |
| `critique_failed` | Spec panel critique pass failed to produce scores | Yes | `4a` |
| `convergence_exhausted` | Maximum convergence iterations (3) reached with unresolved CRITICALs | No | — |
| `user_rejected` | User rejected spec at an approval gate | No | — |
| `prerequisite_failed` | Phase entry gate condition not met | No | — |

### Failure Path Defaults (NFR-009)

On any failure path, the contract is emitted with these defaults:
- All `quality_scores` fields default to `0.0` (NOT null)
- `downstream_ready` defaults to `false`
- `convergence_iterations` defaults to `0`
- `convergence_state` defaults to `NOT_STARTED`
- `spec_file` and `panel_report` default to `""` (empty string)
- `resume_substep` is populated for resumable failure types; null otherwise
- All `phase_contracts` entries for incomplete phases default to `failed`
- `phase_timing` entries default to `0.0` for phases not reached

### Resume Behavior Semantics

**Phase 3 Resume** (`resume_substep=3c`):
- Preserves the populated spec from Step 3b (template instantiation + content population)
- Brainstorm pass (Step 3c) re-runs from scratch against the preserved draft
- Gap incorporation (Step 3d) re-runs after brainstorm completes
- All Phase 1 and Phase 2 artifacts are preserved unchanged

**Phase 4 Resume** (`resume_substep=4a`):
- Preserves the complete draft spec from Phase 3 (including brainstorm findings)
- Focus pass (Step 4a) re-runs from scratch against the preserved spec
- All subsequent steps (4b, 4c, 4d) re-run in sequence
- Convergence loop resets iteration counter to 1
- All Phase 1, Phase 2, and Phase 3 artifacts are preserved unchanged

### Contract Emission on Dry Run

When `--dry-run` is active, the contract is emitted with:
- `status: dry_run`
- Phases 0-2 contracts populated; Phases 3-4 marked as `skipped`
- All quality scores set to `0.0`
- `downstream_ready: false`
- `convergence_state: NOT_STARTED`
- No spec synthesis or panel review artifacts produced

## Related Commands

- `/sc:implement` — General feature implementation
- `/sc:design` — System architecture design
- `/sc:analyze` — Code analysis for understanding workflows
- `/sc:build` — Build and compile after generating
