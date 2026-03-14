---
title: "Portification of sc-cli-portify-protocol into Programmatic CLI Pipeline"
version: "1.0.0"
status: draft
feature_id: FR-PORTIFY-CLI
parent_feature: null
spec_type: portification
complexity_score: 0.85
complexity_class: high
target_release: v2.24
authors: [user, claude]
created: 2026-03-10
quality_scores:
  clarity: 8.5
  completeness: 8.0
  testability: 8.5
  consistency: 8.0
  overall: 8.25
---

## 1. Problem Statement

The `sc-cli-portify-protocol` workflow currently relies entirely on Claude's inference for orchestration across 4 phases and 12 logical steps. This produces inconsistent results between runs: phase boundaries are implicit, gate validation depends on Claude self-reporting, there is no stall detection or budget tracking, and failures require full re-execution from the beginning. For a workflow whose purpose is to produce repeatable CLI pipelines from other workflows, the lack of its own programmatic control flow is both a practical limitation and a credibility gap.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| No resume capability on failure — full re-execution required | SKILL.md behavioral flow (no checkpoint mechanism) | 30-60 min wasted on partial failures |
| Gate validation is inference-based — Claude decides if its own output passes | SKILL.md Phase 3→4 gate description | Quality gates are advisory, not enforced |
| No budget tracking across phases — token consumption is unbounded | SKILL.md (no TurnLedger integration) | Unpredictable costs for multi-phase execution |
| Phase timing is self-reported, not instrumented | SKILL.md return contract (phase_timing fields) | Timing data unreliable for optimization |
| Inconsistent output structure between runs | Observed behavior across multiple portification runs | Downstream consumers (sc:roadmap, sc:tasklist) receive varying input quality |

### 1.2 Scope Boundary

**In scope**: Portification of the sc-cli-portify-protocol workflow into a programmatic CLI pipeline under `src/superclaude/cli/cli_portify/`, producing 13 new Python modules plus 1 modified file (`main.py`), with full gate validation, TurnLedger budget tracking, convergence loop management, resume support, and Rich TUI monitoring.

**Out of scope**: Modifying the source skill/command/agent files; executing the generated pipeline; changes to the `pipeline/` or `sprint/` base modules; UI/frontend work; new MCP server integrations.

## 2. Solution Overview

A new CLI subcommand package `superclaude cli-portify` that wraps the existing 4-phase portification protocol in a sprint-style supervised executor. Python controls all flow decisions (what runs when, convergence checks, budget guards). Claude subprocesses handle content generation, invoking existing skills (`/sc:brainstorm`, `/sc:spec-panel`) rather than reimplementing their behavioral patterns.

The pipeline consolidates 12 logical workflow steps into 7 pipeline steps: 2 pure-programmatic (config validation, component discovery) and 5 Claude-assisted (workflow analysis, pipeline design, spec synthesis, brainstorm gaps, panel review with convergence).

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Step consolidation | 12 logical → 7 pipeline steps | 1:1 mapping (12 steps), aggressive merge (4 steps) | Balances subprocess overhead reduction with gate coverage at critical boundaries |
| Skill reuse | Invoke `/sc:brainstorm` and `/sc:spec-panel` in subprocesses | Reimplement behavioral patterns in prompts | Existing skills have tested multi-persona, MCP, and expert panel logic; avoid duplication |
| File passing | `@path` references in prompts (subprocess reads via Read tool) | `--file` CLI args, inline embedding | Matches sprint `ClaudeProcess` pattern; `--file` flag is for remote IDs not local files |
| Execution model | Synchronous threading + `time.sleep()` polling | `async/await`, multiprocessing | Consistent with sprint/pipeline architecture; simpler debugging |
| Convergence control | Executor manages iteration loop, Claude runs one pass per subprocess | Claude manages own convergence in single session | Python-controlled convergence ensures deterministic iteration count and budget tracking |

### 2.2 Workflow / Data Flow

```
[CLI args: --workflow, --name, --output, --dry-run]
    |
    v
Step 1: validate-config [PROGRAMMATIC]
    |  Output: validate-config-result.json
    v
Step 2: discover-components [PROGRAMMATIC]
    |  Output: component-inventory.md
    v
Step 3: analyze-workflow [CLAUDE]
    |  Reads: component-inventory.md, SKILL.md, refs/*
    |  Output: portify-analysis.md
    |  Gate: STRICT (required sections, data flow diagram)
    v
Step 4: design-pipeline [CLAUDE]
    |  Reads: portify-analysis.md, refs/pipeline-spec.md
    |  Output: portify-spec.md
    |  Gate: STRICT (step mappings, gate definitions)
    |  ** USER REVIEW ** (--dry-run stops here)
    v
Step 5: synthesize-spec [CLAUDE]
    |  Reads: @portify-analysis.md, @portify-spec.md, template (inline)
    |  Output: portify-release-spec.md
    |  Gate: STRICT (zero SC_PLACEHOLDER sentinels)
    v
Step 6: brainstorm-gaps [CLAUDE via /sc:brainstorm]
    |  Reads: portify-release-spec.md
    |  Output: portify-release-spec.md (+ Section 12)
    |  Gate: STANDARD (Section 12 present)
    v
Step 7: panel-review [CLAUDE via /sc:spec-panel, convergence loop]
    |  Reads: portify-release-spec.md
    |  Output: portify-release-spec.md (final), panel-report.md
    |  Gate: STRICT (quality scores valid, overall is mean)
    |  Convergence: max 3 iterations, halts on 0 unaddressed CRITICALs
    |  ** USER REVIEW **
    v
[RETURN CONTRACT: contract_version 2.0, quality_scores, downstream_ready]
```

## 3. Functional Requirements

### FR-PORTIFY-CLI.1: Config Validation (Step: validate-config)

**Description**: Pure-programmatic step that validates all CLI inputs before any Claude subprocess is launched. Resolves workflow path to a directory containing `SKILL.md`, derives CLI name (strip `sc-` prefix and `-protocol` suffix, convert to kebab/snake case), validates output directory writability, and checks for name collisions with non-portified CLI modules.

**Consolidates**: Logical Step 0 (input validation)

**Acceptance Criteria**:
- [ ] Resolves `--workflow` to a directory containing `SKILL.md`, or emits `INVALID_PATH` error
- [ ] Derives CLI name from workflow when `--name` not provided, or emits `DERIVATION_FAILED`
- [ ] Validates output directory parent exists and is writable, or emits `OUTPUT_NOT_WRITABLE`
- [ ] Detects collision with existing non-portified modules, or emits `NAME_COLLISION`
- [ ] Writes `validate-config-result.json` with resolved paths on success
- [ ] Completes in <1s (no Claude subprocess)

**Dependencies**: None

### FR-PORTIFY-CLI.2: Component Discovery (Step: discover-components)

**Description**: Pure-programmatic step that inventories all components of the target workflow. Uses `Path.rglob()` to find SKILL.md, refs/, rules/, templates/, scripts/, and matching command files. Counts lines per component. Produces a structured markdown inventory table with YAML frontmatter.

**Consolidates**: Logical Step 1 (component discovery)

**Acceptance Criteria**:
- [ ] Finds SKILL.md in workflow directory
- [ ] Discovers all files in refs/, rules/, templates/, scripts/ subdirectories
- [ ] Locates matching command file in `src/superclaude/commands/` or `.claude/commands/sc/`
- [ ] Counts lines accurately for each component
- [ ] Produces `component-inventory.md` with YAML frontmatter (`source_skill`, `component_count`)
- [ ] Completes in <5s (no Claude subprocess)

**Dependencies**: FR-PORTIFY-CLI.1

### FR-PORTIFY-CLI.3: Workflow Analysis (Step: analyze-workflow)

**Description**: Claude-assisted step that reads all discovered components and produces a complete portification analysis document. Extracts the behavioral flow, identifies step boundaries, classifies each step on the programmatic spectrum (pure-programmatic, claude-assisted, hybrid), maps dependencies and parallel groups, extracts gate requirements, and produces a data flow diagram.

**Consolidates**: Logical Steps 2 (protocol mapping), 3 (step identification/classification), 4 (gate extraction), 5 (analysis assembly)

**Acceptance Criteria**:
- [ ] Produces `portify-analysis.md` with YAML frontmatter (`source_skill`, `step_count`, `parallel_groups`, `gate_count`, `complexity`)
- [ ] Contains all required sections: Source Components, Step Graph, Gates Summary, Data Flow Diagram, Classification Summary
- [ ] Every identified step has a classification (pure-programmatic, claude-assisted, or hybrid)
- [ ] Data flow diagram is present with arrow notation
- [ ] Analysis is under 400 lines per output guidance
- [ ] Gate passes STRICT tier validation

**Dependencies**: FR-PORTIFY-CLI.2

### FR-PORTIFY-CLI.4: Pipeline Design (Step: design-pipeline)

**Description**: Claude-assisted step that converts the workflow analysis into a concrete, code-ready pipeline specification. Designs the Step graph, defines domain models (Config, Status, Result, MonitorState), writes prompt builder specifications, defines gate criteria with semantic checks, implements pure-programmatic steps as runnable Python code, designs the executor loop, and plans Click CLI integration.

**Consolidates**: Logical Step 6 (pipeline specification)

**Acceptance Criteria**:
- [ ] Produces `portify-spec.md` with YAML frontmatter (`step_mapping_count`, `model_count`, `gate_definition_count`)
- [ ] Contains step mapping entries for every pipeline step
- [ ] All steps have corresponding gate definitions
- [ ] Pure-programmatic steps include actual Python implementation code
- [ ] Prompt builders for Claude-assisted steps specify required output format and machine-readable markers
- [ ] Executor design uses synchronous threading (not async/await)
- [ ] Gate passes STRICT tier validation
- [ ] User review gate after this step; `--dry-run` halts pipeline here

**Dependencies**: FR-PORTIFY-CLI.3

### FR-PORTIFY-CLI.5: Spec Synthesis (Step: synthesize-spec)

**Description**: Claude-assisted step that instantiates the release spec template and populates all sections from Phase 1 and Phase 2 outputs. Template (9KB) is embedded inline in the prompt. Analysis and spec are referenced by `@path` for subprocess Read tool access. Includes the step consolidation mapping table to ensure each FR maps to a pipeline step. Runs SC-003 self-validation to verify zero remaining `{{SC_PLACEHOLDER:*}}` sentinels.

**Consolidates**: Logical Steps 7 (template instantiation), 8 (content population)

**Acceptance Criteria**:
- [ ] Produces `portify-release-spec.md` with complete YAML frontmatter
- [ ] Zero remaining `{{SC_PLACEHOLDER:*}}` sentinels (SC-003)
- [ ] Contains 7 functional requirements (one per pipeline step)
- [ ] FR consolidation mapping is explicit (which logical steps each FR covers)
- [ ] All conditional sections appropriate for portification type are included (Sections 4.3, 4.5, 5, 8.3, 9)
- [ ] Gate passes STRICT tier validation
- [ ] On gate failure (remaining placeholders), retry prompt includes the specific placeholder names that remain, enabling targeted fix rather than blind re-run [F-005]

### FR-PORTIFY-CLI.6: Brainstorm Gap Analysis (Step: brainstorm-gaps)

**Description**: Claude-assisted step that invokes the existing `/sc:brainstorm` skill against the draft release spec. The subprocess runs `/sc:brainstorm --strategy systematic --depth deep --no-codebase`, leveraging its built-in multi-persona orchestration (architect, analyzer, backend), MCP integrations, and structured output. Post-processing formats findings and incorporates actionable gaps into spec body sections. Unresolvable items route to Section 11 (Open Items).

**Consolidates**: Logical Step 9 (automated brainstorm pass)

**Acceptance Criteria**:
- [ ] Subprocess invokes `/sc:brainstorm` skill (not reimplemented behavioral patterns)
- [ ] Section 12 (Brainstorm Gap Analysis) is appended to the spec
- [ ] Findings use structured format: `{gap_id, description, severity, affected_section, persona}`
- [ ] Actionable findings are incorporated into relevant spec sections and marked `[INCORPORATED]`
- [ ] Unresolvable items are routed to Section 11 and marked `[OPEN]`
- [ ] Summary includes `{total_gaps, incorporated, open, severity_distribution}`
- [ ] Zero-gap outcome is valid and does not block the pipeline
- [ ] Gate passes STANDARD tier validation
- [ ] Section 12 gate includes structural validation: must contain either a findings table (with Gap ID column) or the literal zero-gap summary text — heading alone is insufficient [F-007]
- [ ] Pre-flight check: verify `/sc:brainstorm` skill is available in subprocess environment; if unavailable, fall back to inline multi-persona prompt with warning [GAP-001]

**Dependencies**: FR-PORTIFY-CLI.5

### FR-PORTIFY-CLI.7: Panel Review with Convergence (Step: panel-review)

**Description**: Claude-assisted step with executor-managed convergence loop. Each iteration launches a Claude subprocess that invokes the existing `/sc:spec-panel` skill with `--focus correctness,architecture`. The executor (Python) checks the convergence predicate after each iteration: zero unaddressed CRITICALs transitions to CONVERGED; otherwise iterates up to `max_convergence` (default 3). Produces quality scores (clarity, completeness, testability, consistency, overall) and a panel report. Downstream readiness gate: `overall >= 7.0`.

**Consolidates**: Logical Steps 10 (focus pass), 11 (critique/scoring/convergence)

**Acceptance Criteria**:
- [ ] Each iteration invokes `/sc:spec-panel` skill (not reimplemented expert patterns)
- [ ] Executor manages convergence loop with iteration counter and hard cap (max 3)
- [ ] Convergence predicate: zero findings with `severity: CRITICAL` and status not `[INCORPORATED]` or `[DISMISSED]`
- [ ] Quality scores in spec frontmatter: clarity, completeness, testability, consistency (all 0-10 float)
- [ ] Overall = mean(clarity, completeness, testability, consistency) (SC-010)
- [ ] `panel-report.md` produced with all findings, scores, and convergence status
- [ ] Machine-readable convergence block: `CONVERGENCE_STATUS`, `UNADDRESSED_CRITICALS`, `QUALITY_OVERALL`
- [ ] Terminal state: CONVERGED (success) or ESCALATED (partial, with user escalation)
- [ ] Downstream ready gate: `overall >= 7.0` (boundary: 7.0 true, 6.9 false) (SC-012)
- [ ] Gate passes STRICT tier validation
- [ ] User review gate at end
- [ ] Pre-flight check: verify `/sc:spec-panel` skill is available in subprocess environment; if unavailable, fall back to inline expert panel prompt with warning [GAP-001]
- [ ] Each iteration runs both focus pass (discussion mode) and critique pass (critique mode) within a single subprocess — mode is NOT mapped across iterations [GAP-006]
- [ ] Each convergence iteration has its own independent timeout (default 300s), not a division of the total step timeout. TurnLedger guards budget before each iteration launch. [F-004]

**Dependencies**: FR-PORTIFY-CLI.6

## 4. Architecture

### 4.1 New Files

> **Architecture Note (DEV-001 accepted, 2026-03-13)**: The file layout below reflects the
> accepted roadmap architecture produced through adversarial debate (D-02, D-04, D-11, D-12,
> D-14). It replaces the original 13-file flat layout with an 18-module structure using a
> `steps/` subdirectory for step implementations. See `dev-001-accepted-deviation.md` for
> the full acceptance record and debate evidence.

| File | Purpose | Dependencies | Debate Basis |
|------|---------|-------------|--------------|
| `src/superclaude/cli/cli_portify/__init__.py` | Package exports (`cli_portify_group`) | cli.py | (unchanged) |
| `src/superclaude/cli/cli_portify/cli.py` | Click CLI group (`cli-portify`) and `run` subcommand; registers with `main.py` via `app.add_command()` | executor.py | Naming convention alignment (function over framework) |
| `src/superclaude/cli/cli_portify/executor.py` | Step orchestration loop: convergence iteration, budget management, resume state serialization, review-gate pauses, dry-run termination | all step modules, convergence.py, resume.py, contract.py, monitor.py | D-04 consensus |
| `src/superclaude/cli/cli_portify/models.py` | PortifyConfig, PortifyStatus, PortifyOutcome, PortifyStepResult, PortifyResult, PortifyMonitorState | pipeline.models | (unchanged) |
| `src/superclaude/cli/cli_portify/contract.py` | Return contract emission: `to_contract()` producing Phase Contracts schema YAML on all exit paths (success, partial, failed, dry_run) | models.py | Opus original (unchallenged) |
| `src/superclaude/cli/cli_portify/resume.py` | Resume decision table: per-step resumability classification, prior-context injection rules, partial-artifact preservation policy | models.py | D-12 consensus |
| `src/superclaude/cli/cli_portify/convergence.py` | ConvergenceState enum (READY, ITERATING, CONVERGED, ESCALATED, FAILED) with valid-transition dictionary and transition assertion | models.py | D-11 consensus |
| `src/superclaude/cli/cli_portify/gates.py` | 7 GateCriteria objects with SemanticCheck compositions, tiered enforcement (EXEMPT/STANDARD/STRICT), 8 semantic check functions | pipeline.models, models.py | (unchanged) |
| `src/superclaude/cli/cli_portify/process.py` | PortifyProcess extending pipeline.ClaudeProcess; `--add-dir` for work_dir and workflow_path; centralized `@path`, timeout, model propagation rules | models.py, pipeline.process | (unchanged) |
| `src/superclaude/cli/cli_portify/prompts.py` | 5 prompt builders (analyze, pipeline, synthesize, brainstorm, panel); resume-context-aware for Steps 5-7 | models.py | (unchanged) |
| `src/superclaude/cli/cli_portify/monitor.py` | Unified monitoring: Rich TUI live dashboard, JSONL + Markdown execution logging, 5 signal types; contains DiagnosticCollector, FailureClassifier, ReportGenerator as internal components | models.py | D-14 / coherence (replaces tui.py + logging_.py + diagnostics.py) |
| `src/superclaude/cli/cli_portify/steps/validate_config.py` | Step 1: config validation, name derivation, output-dir writability, collision detection; emits `validate-config-result.json` | models.py | D-02 consensus |
| `src/superclaude/cli/cli_portify/steps/discover_components.py` | Step 2: component discovery via Path.rglob(), line counting (1MB cap with warning), emits `component-inventory.md` | models.py | D-02 consensus |
| `src/superclaude/cli/cli_portify/steps/analyze_workflow.py` | Step 3: Claude-assisted workflow analysis; STRICT gate | models.py, gates.py, process.py, prompts.py | D-02 consensus |
| `src/superclaude/cli/cli_portify/steps/design_pipeline.py` | Step 4: Claude-assisted pipeline design; STRICT gate; dry-run halts after this step | models.py, gates.py, process.py, prompts.py | D-02 consensus |
| `src/superclaude/cli/cli_portify/steps/synthesize_spec.py` | Step 5: Claude-assisted spec synthesis from release-spec-template.md; zero-placeholder STRICT gate | models.py, gates.py, process.py, prompts.py | D-02 consensus |
| `src/superclaude/cli/cli_portify/steps/brainstorm_gaps.py` | Step 6: Claude-assisted gap analysis via /sc:brainstorm; STANDARD gate; appends Section 12 | models.py, gates.py, process.py, prompts.py | D-02 consensus |
| `src/superclaude/cli/cli_portify/steps/panel_review.py` | Step 7: Claude-assisted panel review with convergence loop; section hashing for additive-only enforcement; STRICT gate | models.py, gates.py, process.py, prompts.py, convergence.py | D-02 + D-14 consensus |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/cli/main.py` | Add `from superclaude.cli.cli_portify import cli_portify_group` and `app.add_command(cli_portify_group)` | Register new CLI subcommand |

### 4.3 Removed Files

| File/Section | Reason | Migration |
|-------------|--------|-----------|
| (none) | Portification adds a new CLI module; no files are removed | N/A |

### 4.4 Module Dependency Graph

> **Architecture Note (DEV-001 accepted, 2026-03-13)**: Graph reflects the accepted
> executor-centered architecture with `steps/` subdirectory. Replaces the original flat
> dependency graph. See `dev-001-accepted-deviation.md` Amendment B.

```
External dependencies:
  pipeline.models ──────────────────────────────────────────────┐
  pipeline.gates ───────────────────────────────────────────────┤
  pipeline.process ─────────────────────────────────────────────┤
  sprint.models (TurnLedger) ───────────────────────────────────┤
                                                                │
cli_portify/models.py ◄───────────────────────────────────────┘
    (foundation — imported by all other modules)

CLI entry and orchestration layer:
  cli_portify/cli.py ──────────────────────────────────────────> main.py (app.add_command())
  cli_portify/cli.py ──> cli_portify/executor.py
  cli_portify/executor.py ──> cli_portify/convergence.py   (ConvergenceState enum + valid-transition dict)
  cli_portify/executor.py ──> cli_portify/resume.py        (resume decision table, per-step resumability)
  cli_portify/executor.py ──> cli_portify/contract.py      (return contract emission on all exit paths)
  cli_portify/executor.py ──> cli_portify/monitor.py       (Rich TUI + JSONL logging + signals)

Step implementations (executor.py imports each):
  cli_portify/executor.py ──> cli_portify/steps/validate_config.py
  cli_portify/executor.py ──> cli_portify/steps/discover_components.py
  cli_portify/executor.py ──> cli_portify/steps/analyze_workflow.py
  cli_portify/executor.py ──> cli_portify/steps/design_pipeline.py
  cli_portify/executor.py ──> cli_portify/steps/synthesize_spec.py
  cli_portify/executor.py ──> cli_portify/steps/brainstorm_gaps.py
  cli_portify/executor.py ──> cli_portify/steps/panel_review.py
  cli_portify/steps/panel_review.py ──> cli_portify/convergence.py  (direct import for section hashing)

Shared infrastructure (imported by step modules and executor):
  cli_portify/models.py   ──> (all step modules, executor, contract, resume, convergence)
  cli_portify/gates.py    ──> (all step modules)
  cli_portify/process.py  ──> (steps 3-7: analyze, design, synthesize, brainstorm, panel)
  cli_portify/prompts.py  ──> (steps 3-7)

cli_portify/__init__.py ◄── cli_portify/cli.py
main.py ◄── cli_portify/__init__.py
```

### 4.5 Data Models

```python
@dataclass
class PortifyConfig(PipelineConfig):
    """cli-portify pipeline configuration."""
    # Required: identify the workflow to portify
    workflow_path: Path = field(default_factory=lambda: Path("."))
    cli_name: str = ""
    module_name: str = ""
    output_dir: Path = field(default_factory=lambda: Path("."))

    # Behavioral controls
    skip_review: bool = False       # Skip user review gates
    max_convergence: int = 3        # Max panel review iterations

    # Budget
    max_turns: int = 200
    stall_timeout: int = 120        # Seconds before stall detection
    stall_action: str = "kill"

    # Derived paths
    @property
    def analysis_file(self) -> Path:
        return self.work_dir / "portify-analysis.md"

    @property
    def spec_file(self) -> Path:
        return self.work_dir / "portify-spec.md"

    @property
    def prompts_file(self) -> Path:
        return self.work_dir / "portify-prompts.md"

    @property
    def release_spec_file(self) -> Path:
        return self.work_dir / "portify-release-spec.md"

    @property
    def panel_report_file(self) -> Path:
        return self.work_dir / "panel-report.md"

    @property
    def template_path(self) -> Path:
        """Path to the release spec template."""
        return Path("src/superclaude/examples/release-spec-template.md")


class PortifyStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"
    PASS_NO_REPORT = "pass_no_report"
    INCOMPLETE = "incomplete"
    HALT = "halt"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"
    # Domain-specific
    VALIDATION_FAIL = "validation_fail"     # Step 0 config validation failed
    USER_REJECTED = "user_rejected"         # User rejected at review gate
    CONVERGENCE_EXHAUSTED = "convergence_exhausted"  # 3 iterations without resolution


class PortifyOutcome(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"       # Escalated from convergence
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"
    DRY_RUN = "dry_run"


@dataclass
class PortifyStepResult(StepResult):
    status: PortifyStatus = PortifyStatus.PENDING
    exit_code: int | None = None
    started_at: float | None = None
    finished_at: float | None = None
    output_bytes: int = 0
    error_bytes: int = 0
    # Domain-specific
    convergence_iteration: int | None = None    # For panel-review step
    quality_scores: dict | None = None          # For panel-review step
    gate_details: dict = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return 0.0


@dataclass
class PortifyResult:
    config: PortifyConfig
    step_results: list[PortifyStepResult] = field(default_factory=list)
    outcome: PortifyOutcome = PortifyOutcome.SUCCESS
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    halt_step: str | None = None

    # Return contract fields
    convergence_state: str = "NOT_STARTED"
    convergence_iterations: int = 0
    quality_scores: dict = field(default_factory=lambda: {
        "clarity": 0.0, "completeness": 0.0,
        "testability": 0.0, "consistency": 0.0, "overall": 0.0
    })
    phase_timing: dict = field(default_factory=lambda: {
        "phase_3_seconds": 0.0, "phase_4_seconds": 0.0
    })
    warnings: list[str] = field(default_factory=list)

    @property
    def downstream_ready(self) -> bool:
        return self.quality_scores.get("overall", 0.0) >= 7.0

    @property
    def source_step_count(self) -> int:
        return len(self.step_results)

    @property
    def spec_fr_count(self) -> int:
        """Count FR sections in the release spec."""
        spec_path = self.config.release_spec_file
        if not spec_path.exists():
            return 0
        content = spec_path.read_text()
        return content.count("### FR-")

    def resume_command(self) -> str | None:
        if not self.halt_step:
            return None
        return (
            f"superclaude cli-portify run "
            f"--workflow {self.config.workflow_path} "
            f"--name {self.config.cli_name} "
            f"--resume --start {self.halt_step} "
            f"--max-turns {self.suggested_resume_budget}"
        )

    @property
    def suggested_resume_budget(self) -> int:
        remaining = sum(1 for r in self.step_results
                       if r.status == PortifyStatus.PENDING)
        return remaining * 30

    def to_contract(self) -> dict:
        """Emit the return contract per SKILL.md schema."""
        import hashlib
        spec_hash = ""
        if self.config.spec_file.exists():
            spec_hash = hashlib.sha256(
                self.config.spec_file.read_bytes()
            ).hexdigest()

        return {
            "contract_version": "2.0",
            "spec_file": str(self.config.release_spec_file) if self.config.release_spec_file.exists() else "",
            "panel_report": str(self.config.panel_report_file) if self.config.panel_report_file.exists() else "",
            "output_directory": str(self.config.work_dir),
            "quality_scores": self.quality_scores,
            "convergence_iterations": self.convergence_iterations,
            "convergence_state": self.convergence_state,
            "phase_timing": self.phase_timing,
            "source_step_count": self.source_step_count,
            "spec_fr_count": self.spec_fr_count,
            "api_snapshot_hash": spec_hash,
            "downstream_ready": self.downstream_ready,
            "phase_contracts": self._phase_contracts(),
            "warnings": self.warnings,
            "status": self.outcome.value,
            "failure_phase": self._failure_phase(),
            "failure_type": self._failure_type(),
            "resume_phase": self._resume_phase(),
            "resume_substep": self._resume_substep(),
            "resume_command": self.resume_command(),
        }

    def _phase_contracts(self) -> dict:
        """Map step results to phase contract statuses."""
        phase_map = {
            "validate-config": "phase_0",
            "discover-components": "phase_0",
            "analyze-workflow": "phase_1",
            "design-pipeline": "phase_2",
            "synthesize-spec": "phase_3",
            "brainstorm-gaps": "phase_3",
            "panel-review": "phase_4",
        }
        contracts = {f"phase_{i}": "failed" for i in range(5)}
        for r in self.step_results:
            if r.step and r.step.id in phase_map:
                phase = phase_map[r.step.id]
                if r.status in (PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL):
                    contracts[phase] = "completed"
                elif r.status == PortifyStatus.SKIPPED:
                    contracts[phase] = "skipped"
        if self.outcome == PortifyOutcome.DRY_RUN:
            contracts["phase_3"] = "skipped"
            contracts["phase_4"] = "skipped"
        return contracts

    def _failure_phase(self) -> int | None:
        if self.outcome in (PortifyOutcome.SUCCESS, PortifyOutcome.DRY_RUN):
            return None
        phase_map = {
            "validate-config": 0, "discover-components": 0,
            "analyze-workflow": 1, "design-pipeline": 2,
            "synthesize-spec": 3, "brainstorm-gaps": 3,
            "panel-review": 4,
        }
        return phase_map.get(self.halt_step or "", None)

    def _failure_type(self) -> str | None:
        if self.outcome in (PortifyOutcome.SUCCESS, PortifyOutcome.DRY_RUN):
            return None
        if self.convergence_state == "ESCALATED":
            return "convergence_exhausted"
        last_failed = next(
            (r for r in reversed(self.step_results)
             if r.status not in (PortifyStatus.PASS, PortifyStatus.PENDING, PortifyStatus.SKIPPED)),
            None
        )
        if last_failed and last_failed.status == PortifyStatus.USER_REJECTED:
            return "user_rejected"
        if self.halt_step == "synthesize-spec":
            return "template_failed"
        if self.halt_step == "brainstorm-gaps":
            return "brainstorm_failed"
        if self.halt_step == "panel-review":
            return "focus_failed"
        return None

    def _resume_phase(self) -> int | None:
        resumable = {"brainstorm-gaps": 3, "panel-review": 4}
        return resumable.get(self.halt_step or "", None)

    def _resume_substep(self) -> str | None:
        resumable = {"brainstorm-gaps": "3c", "panel-review": "4a"}
        return resumable.get(self.halt_step or "", None)


@dataclass
class PortifyMonitorState:
    output_bytes: int = 0
    output_bytes_prev: int = 0
    last_growth_time: float = 0.0
    last_event_time: float = 0.0
    step_started_at: float = 0.0
    events_received: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    # Domain-specific
    current_phase: str = ""
    current_persona: str = ""          # For brainstorm: architect|analyzer|backend
    convergence_iteration: int = 0     # For panel-review
    placeholders_remaining: int = -1   # For synthesize-spec (-1 = unknown)
    sections_populated: int = 0

    @property
    def stall_status(self) -> str:
        if self.events_received == 0:
            elapsed = time.time() - self.step_started_at if self.step_started_at else 0
            return "waiting..." if elapsed < 30 else "STALLED"
        if self.stall_seconds > 120:
            return "STALLED"
        if self.stall_seconds > 30:
            return "thinking..."
        return "active"
```

> **Architecture Note (DEV-001 accepted, 2026-03-13)**: The `to_contract()` method defined
> on `PortifyResult` above, together with its 5 helper methods (`_phase_contracts()`,
> `_failure_phase()`, `_failure_type()`, `_resume_phase()`, `_resume_substep()`), are
> extracted to a dedicated `contract.py` module in the implemented architecture. `PortifyResult`
> retains all data fields; contract emission is handled by `contract.py` which receives the
> result object as a parameter. Similarly, the resume methods (`resume_command()`,
> `suggested_resume_budget`, `_resume_phase()`, `_resume_substep()`) are extracted to
> `resume.py`, which owns the resume decision table as a Phase 2 deliverable (D-12 consensus).
> The field-level definitions and method signatures in this section remain authoritative for
> implementation; only their module boundary has changed. See `dev-001-accepted-deviation.md`
> Amendment C for full rationale.

### 4.6 Implementation Order

> **Architecture Note (DEV-001 accepted, 2026-03-13)**: Implementation order updated to
> reflect the accepted 18-module structure with `steps/` subdirectory and unified `monitor.py`.
> Replaces the original 13-file flat layout order.

```
1. models.py                          -- No internal deps; defines all types
2. convergence.py                     -- [parallel] Imports from models; ConvergenceState enum + transitions
   resume.py                          -- [parallel] Imports from models; resume decision table
   contract.py                        -- [parallel] Imports from models; return contract emission
3. gates.py                           -- Imports from models; 7 semantic checks + 7 gate definitions
   prompts.py                         -- [parallel with gates.py] Imports from models; 5 prompt builders
4. process.py                         -- Imports from models, pipeline.process; PortifyProcess
   monitor.py                         -- [parallel with process.py] Imports from models; unified TUI + logging + diagnostics
5. steps/validate_config.py           -- Imports from models; Step 1 pure-programmatic
   steps/discover_components.py       -- [parallel] Imports from models; Step 2 pure-programmatic
6. steps/analyze_workflow.py          -- Imports from models, gates, process, prompts; Step 3 Claude-assisted
   steps/design_pipeline.py           -- [parallel] Imports from models, gates, process, prompts; Step 4
   steps/synthesize_spec.py           -- [parallel] Imports from models, gates, process, prompts; Step 5
7. steps/brainstorm_gaps.py           -- Imports from models, gates, process, prompts; Step 6
   steps/panel_review.py              -- [parallel] Imports from models, gates, process, prompts, convergence; Step 7
8. executor.py                        -- Imports from all step modules, convergence, resume, contract, monitor
9. cli.py                             -- Imports from executor; Click CLI group
10. __init__.py                       -- Re-exports cli_portify_group
11. main.py (patch)                   -- Add import + app.add_command()
```

## 5. Interface Contracts

### 5.1 CLI Surface

```
superclaude cli-portify run <WORKFLOW> [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `WORKFLOW` | PATH (argument) | required | Path to skill directory to portify |
| `--name` | STRING | derived | CLI subcommand name (kebab-case) |
| `--output` | PATH | `src/superclaude/cli/<name>/` | Output directory |
| `--dry-run` | FLAG | false | Stop after Phase 2, emit dry_run contract |
| `--max-turns` | INT | 200 | Turn budget across all subprocesses |
| `--skip-review` | FLAG | false | Skip user review gates |
| `--model` | STRING | (default) | Claude model override |
| `--debug` | FLAG | false | Enable debug logging |

### 5.2 Gate Criteria

| Step | Gate Tier | Frontmatter | Min Lines | Semantic Checks |
|------|-----------|-------------|-----------|-----------------|
| validate-config | EXEMPT | -- | -- | -- |
| discover-components | STANDARD | source_skill, component_count | 5 | -- |
| analyze-workflow | STRICT | source_skill, step_count, parallel_groups, gate_count, complexity | 100 | has_required_analysis_sections, has_data_flow_diagram |
| design-pipeline | STRICT | step_mapping_count, model_count, gate_definition_count | 200 | has_step_mappings |
| synthesize-spec | STRICT | title, spec_type, complexity_class | 150 | zero_placeholders |
| brainstorm-gaps | STANDARD | -- | -- | has_section_12 |
| panel-review | STRICT | -- | -- | quality_scores_valid, overall_is_mean |

### 5.2.1 Semantic Check Implementations

```python
def _has_required_analysis_sections(content: str) -> bool:
    """Verify portify-analysis.md has all required sections."""
    required = {
        "## Source Components", "## Step Graph", "## Gates Summary",
        "## Data Flow Diagram", "## Classification Summary",
    }
    present = {line.strip() for line in content.splitlines() if line.startswith("## ")}
    return required.issubset(present)

def _has_data_flow_diagram(content: str) -> bool:
    """Verify data flow diagram is present (contains arrow notation)."""
    return "-->" in content or "--->" in content

def _has_step_mappings(content: str) -> bool:
    """Verify pipeline spec contains step mapping entries."""
    return "Step(" in content or "step-" in content.lower()

def _all_gates_defined(content: str) -> bool:
    """Verify every step has a gate definition."""
    import re
    steps = re.findall(r'id="([^"]+)"', content)
    for step_id in steps:
        if step_id not in content.split("Gate Definitions")[1] if "Gate Definitions" in content else "":
            return False
    return True

def _zero_placeholders(content: str) -> bool:
    """SC-003: Verify zero remaining {{SC_PLACEHOLDER:*}} sentinels."""
    return "{{SC_PLACEHOLDER:" not in content

def _has_section_12(content: str) -> bool:
    """Verify Section 12 (Brainstorm Gap Analysis) is present."""
    return "## 12." in content or "## Brainstorm Gap Analysis" in content

def _quality_scores_valid(content: str) -> bool:
    """Verify quality_scores frontmatter has all 4 dimensions + overall."""
    import re
    fm_match = re.search(r"---\n(.*?)---", content, re.DOTALL)
    if not fm_match:
        return False
    fm = fm_match.group(1)
    required = ["clarity:", "completeness:", "testability:", "consistency:", "overall:"]
    return all(field in fm for field in required)

def _overall_is_mean(content: str) -> bool:
    """SC-010: Verify overall = mean(clarity, completeness, testability, consistency)."""
    import re, yaml
    fm_match = re.search(r"---\n(.*?)---", content, re.DOTALL)
    if not fm_match:
        return False
    try:
        fm = yaml.safe_load(fm_match.group(1))
        qs = fm.get("quality_scores", {})
        if not qs:
            return False
        dims = [qs.get("clarity", 0), qs.get("completeness", 0),
                qs.get("testability", 0), qs.get("consistency", 0)]
        expected = sum(dims) / 4
        actual = qs.get("overall", -1)
        return abs(actual - expected) < 0.01
    except Exception:
        return False
```

### 5.2.2 Gate Criteria Objects

```python
VALIDATE_CONFIG_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="EXEMPT",
)

DISCOVER_COMPONENTS_GATE = GateCriteria(
    required_frontmatter_fields=["source_skill", "component_count"],
    min_lines=5,
    enforcement_tier="STANDARD",
)

ANALYZE_WORKFLOW_GATE = GateCriteria(
    required_frontmatter_fields=["source_skill", "step_count", "parallel_groups",
                                  "gate_count", "complexity"],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("has_required_sections", _has_required_analysis_sections,
                     "Missing required analysis sections"),
        SemanticCheck("has_data_flow", _has_data_flow_diagram,
                     "Data flow diagram not found"),
    ],
)

DESIGN_PIPELINE_GATE = GateCriteria(
    required_frontmatter_fields=["step_mapping_count", "model_count",
                                  "gate_definition_count"],
    min_lines=200,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("has_step_mappings", _has_step_mappings,
                     "No step mapping entries found"),
    ],
)

SYNTHESIZE_SPEC_GATE = GateCriteria(
    required_frontmatter_fields=["title", "spec_type", "complexity_class"],
    min_lines=150,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("zero_placeholders", _zero_placeholders,
                     "Remaining {{SC_PLACEHOLDER:*}} sentinels found"),
    ],
)

BRAINSTORM_GAPS_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck("has_section_12", _has_section_12,
                     "Section 12 (Brainstorm Gap Analysis) not found"),
    ],
)

PANEL_REVIEW_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("quality_scores_valid", _quality_scores_valid,
                     "Quality scores frontmatter missing or incomplete"),
        SemanticCheck("overall_is_mean", _overall_is_mean,
                     "Overall score is not the arithmetic mean of 4 dimensions"),
    ],
)
```

### 5.3 Phase Contracts

```yaml
# Return contract emitted on every invocation (success, partial, failed, dry_run)
contract_version: "2.0"
spec_file: "<path>"
panel_report: "<path>"
output_directory: "<path>"
quality_scores:
  clarity: <float>          # 0.0-10.0
  completeness: <float>
  testability: <float>
  consistency: <float>
  overall: <float>          # mean of above 4
convergence_iterations: <int>
convergence_state: "CONVERGED|ESCALATED|NOT_STARTED"
phase_timing:
  phase_3_seconds: <float>
  phase_4_seconds: <float>
source_step_count: <int>
spec_fr_count: <int>
api_snapshot_hash: "<sha256>"
downstream_ready: <bool>    # true if overall >= 7.0
phase_contracts:
  phase_0: "completed|skipped|failed"
  phase_1: "completed|skipped|failed"
  phase_2: "completed|skipped|failed"
  phase_3: "completed|skipped|failed"
  phase_4: "completed|skipped|failed"
warnings: []
status: "success|partial|failed|dry_run"
failure_phase: <int|null>
failure_type: "<type|null>"
resume_phase: <int|null>
resume_substep: "<substep|null>"
resume_command: "<command|null>"
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-001 | Phase 3 wall clock time | < 10 minutes | `phase_timing.phase_3_seconds`; advisory warning if exceeded |
| NFR-002 | Phase 4 wall clock time | < 15 minutes | `phase_timing.phase_4_seconds`; advisory warning if exceeded |
| NFR-003 | Synchronous execution | No async/await | Code review: zero `async def` or `await` in cli_portify/ |
| NFR-004 | Gate function signatures | All return `tuple[bool, str]` | Type checking + unit tests |
| NFR-005 | Runner-authored truth | Reports from observed data only | No Claude self-reporting in status determination |
| NFR-006 | Deterministic flow control | Python controls all sequencing | No step uses Claude to decide "what's next" |
| NFR-007 | No pipeline/sprint modification | Zero changes to base modules | `git diff` shows no changes in pipeline/ or sprint/ |
| NFR-008 | Additive-only spec modifications | Panel review never rewrites existing content | Append/extend only in Steps 4b, 4d |
| NFR-009 | Failure path defaults | All contract fields populated on failure | Unit test: verify default contract on each failure type |
| NFR-010 | Skill reuse | brainstorm-gaps invokes /sc:brainstorm; panel-review invokes /sc:spec-panel | Prompt content inspection + integration test |
| NFR-011 | User review gates | When not `--skip-review`, executor pauses TUI and prompts on stderr; user enters `y` to continue or `n` to halt with USER_REJECTED status [GAP-003] | Manual test |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Large context windows in Steps 5-7 may cause Claude to truncate output | Medium | High | Use `@path` references instead of inline embedding; set generous `max_turns` |
| Convergence loop may exhaust budget before completing 3 iterations | Medium | Medium | TurnLedger pre-launch guards; budget estimation per iteration; ESCALATED terminal state |
| `/sc:brainstorm` and `/sc:spec-panel` may not produce machine-readable convergence markers | Medium | High | Post-processing in executor parses output; fallback to structural checks if markers missing |
| Sequential execution (no parallelism) results in long wall-clock time | High | Low | Inherent to data flow dependencies; 7 steps vs 12 reduces overhead; timing is advisory not blocking |
| Self-portification circularity: changes to cli-portify code affect the workflow being portified | Low | Medium | Source skill files are read-only during portification; generated code is in separate directory |
| Subprocess skill invocation may fail if commands not installed | Low | High | Pre-flight check in executor verifies `claude` binary; config validation checks skill availability |
| Subprocess cannot read `@path` files outside its working directory scope | Medium | High | PortifyProcess passes `--add-dir` for work directory and workflow path via `extra_args` [GAP-002] |
| User review gates have no programmatic interaction mechanism | Medium | Medium | `--skip-review` flag bypasses; otherwise executor pauses TUI and prompts on stderr [GAP-003] |
| Panel review convergence prompt uses wrong mode mapping across iterations | High | High | Fix: each iteration runs focus (discussion) then critique within a single subprocess, not mode-per-iteration [GAP-006] |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| test_validate_config_valid | tests/cli_portify/test_inventory.py | Config validation passes for valid inputs |
| test_validate_config_invalid_path | tests/cli_portify/test_inventory.py | INVALID_PATH error for missing SKILL.md |
| test_validate_config_name_collision | tests/cli_portify/test_inventory.py | NAME_COLLISION error for existing non-portified module |
| test_discover_components | tests/cli_portify/test_inventory.py | Component inventory produced with correct counts |
| test_gate_zero_placeholders | tests/cli_portify/test_gates.py | Detects remaining SC_PLACEHOLDER sentinels |
| test_gate_has_section_12 | tests/cli_portify/test_gates.py | Detects presence/absence of Section 12 |
| test_gate_quality_scores_valid | tests/cli_portify/test_gates.py | Validates quality score frontmatter structure |
| test_gate_overall_is_mean | tests/cli_portify/test_gates.py | Verifies overall = mean of 4 dimensions |
| test_result_to_contract | tests/cli_portify/test_models.py | Return contract has all required fields |
| test_result_failure_defaults | tests/cli_portify/test_models.py | NFR-009: all fields populated with defaults on failure |
| test_result_resume_command | tests/cli_portify/test_models.py | Resume command generated for resumable failures |
| test_result_downstream_ready | tests/cli_portify/test_models.py | SC-012: boundary test at 7.0 and 6.9 |
| test_config_load | tests/cli_portify/test_config.py | Config loads with defaults and overrides |
| test_name_derivation | tests/cli_portify/test_config.py | Strips sc- prefix, -protocol suffix, converts case |
| test_convergence_converges | tests/cli_portify/test_executor.py | Convergence loop terminates on 0 unaddressed CRITICALs [F-009] |
| test_convergence_escalates | tests/cli_portify/test_executor.py | Convergence loop escalates after max iterations [F-009] |
| test_convergence_budget_guard | tests/cli_portify/test_executor.py | TurnLedger prevents iteration launch when budget exhausted [F-009] |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| test_programmatic_steps_e2e | Steps 1-2 run without Claude subprocess and produce valid artifacts |
| test_dry_run_halts_after_phase2 | --dry-run stops after design-pipeline, emits dry_run contract |
| test_gate_enforcement | STRICT gate failure halts pipeline with diagnostic report |
| test_convergence_loop | Executor iterates panel-review up to max, checks convergence predicate |
| test_return_contract_schema | Contract YAML matches schema on success, failure, and dry-run paths |

### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Full portification of sc-cleanup-audit | `superclaude cli-portify run src/superclaude/skills/sc-cleanup-audit/` | Pipeline completes, release spec produced, downstream_ready assessed |
| Dry run of sc-adversarial | `superclaude cli-portify run src/superclaude/skills/sc-adversarial-protocol/ --dry-run` | Phases 0-2 complete, Phases 3-4 skipped, dry_run contract emitted |
| Resume after brainstorm failure | Kill process during brainstorm step, run resume command | Resumes from Step 6, preserves Phase 1-2 artifacts |
| Self-portification | `superclaude cli-portify run src/superclaude/skills/sc-cli-portify-protocol/ --name cli-portify` | Meta-test: portify the portifier itself |

## 9. Migration & Rollout

- **Breaking changes**: None. This adds a new CLI subcommand; no existing commands or modules are modified (except `main.py` registration).
- **Backwards compatibility**: The existing skill-based `/sc:cli-portify` workflow continues to work unchanged. The new CLI pipeline is an alternative execution path.
- **Rollback plan**: Remove the `cli_portify/` directory and revert the `main.py` import. One commit.

## 10. Downstream Inputs

### For sc:roadmap

**Theme**: CLI Pipeline Infrastructure
- Milestone 1: Core models, gates, and pure-programmatic steps (FR-1, FR-2)
- Milestone 2: Claude-assisted steps with prompt builders (FR-3, FR-4, FR-5)
- Milestone 3: Brainstorm and panel integration with skill reuse (FR-6, FR-7)
- Milestone 4: Executor, TUI, logging, diagnostics, and CLI registration

### For sc:tasklist

**Task breakdown guidance**:
- Phase 1 (models.py, gates.py, config.py, prompts.py): ~4 tasks, parallelizable
- Phase 2 (inventory.py, monitor.py, process.py): ~3 tasks, partially parallel
- Phase 3 (tui.py, logging_.py, diagnostics.py): ~3 tasks, fully parallel
- Phase 4 (executor.py, commands.py, __init__.py, main.py patch): ~4 tasks, sequential
- Phase 5 (unit tests, integration tests): ~3 tasks
- Estimated total: 14-17 tasks across 5 phases

## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| GAP-005 | Resume from Phase 3 failure: if synthesize-spec partially wrote the spec file, does the gate pass on resume? Need to define whether resume re-runs synthesize-spec or only brainstorm. | Medium — resume may fail silently | Implementation phase: define resume entry points precisely |
| GAP-008 | NDJSON signal patterns for monitor.py: what domain-specific signals does the monitor extract from Claude subprocess output? | Medium — affects TUI accuracy | Implementation phase: define signal vocabulary during monitor.py development |
| F-006 | Resume from Phase 4: specify that prior focus-findings.md is preserved as context injection into the first iteration's prompt, but convergence counter resets to 1 | Medium — affects resume correctness | Implementation phase |

## 12. Brainstorm Gap Analysis

| Gap ID | Description | Severity | Affected Section | Persona | Status |
|--------|-------------|----------|-----------------|---------|--------|
| GAP-001 | No error handling when /sc:brainstorm or /sc:spec-panel skills unavailable in subprocess | high | FR-6, FR-7 | architect | [INCORPORATED] — added fallback + pre-flight check to FR-6, FR-7 acceptance criteria |
| GAP-002 | PortifyProcess needs --add-dir for work_dir so subprocess can read @path files | medium | 4.4, FR-5 | architect | [INCORPORATED] — added to process.py description in Section 4.1 and Risk Assessment |
| GAP-003 | No specification for user review gate interaction mechanism | medium | FR-4, FR-7 | architect | [INCORPORATED] — added NFR-011 defining stderr prompt behavior with --skip-review flag |
| GAP-004 | Overall score rounding tolerance (< 0.01) vs display precision not specified | low | 5.2, NFR-004 | analyzer | [OPEN] — minor, routed to implementation |
| GAP-005 | Resume from Phase 3: partial synthesize-spec output may not pass gate on resume | medium | 5.3 | analyzer | [OPEN] — routed to Section 11 |
| GAP-006 | Panel prompt mode mapping incorrect: should run both focus+critique within each iteration | high | FR-7, prompts | analyzer | [INCORPORATED] — added acceptance criterion to FR-7; risk assessment updated |
| GAP-007 | to_contract() uses inline imports (hashlib, yaml) instead of module-level | low | 4.5 | backend | [OPEN] — minor, fix during implementation |
| GAP-008 | No NDJSON signal vocabulary defined for monitor.py | medium | FR-3 to FR-7 | backend | [OPEN] — routed to Section 11 |
| GAP-009 | run_discover_components reads full file content to count lines | low | FR-2 | backend | [OPEN] — acceptable cost for typical skill directories (<20 files) |

**Summary**: {total_gaps: 9, incorporated: 4, open: 5, severity_distribution: {high: 2, medium: 4, low: 3}}

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Portification | Converting an inference-based SuperClaude workflow into a programmatic CLI pipeline |
| Gate | Programmatic validation check applied to step output before pipeline continues |
| Convergence | Panel review loop termination condition: zero unaddressed CRITICAL findings |
| Runner-authored truth | Reports derived from observed data (exit codes, artifacts, gates), not Claude self-reporting |
| TurnLedger | Budget tracking mechanism for multi-subprocess pipelines |
| Sprint-style executor | Synchronous supervisor loop with threading for parallelism and time.sleep() polling |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | Source workflow being portified |
| `src/superclaude/skills/sc-cli-portify-protocol/refs/analysis-protocol.md` | Phase 1 discovery checklist and classification rubric |
| `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md` | Phase 2 step/model/gate/executor design patterns |
| `src/superclaude/cli/pipeline/models.py` | Base types: PipelineConfig, Step, StepResult, GateCriteria, GateMode |
| `src/superclaude/cli/pipeline/gates.py` | gate_passed() validation engine |
| `src/superclaude/cli/pipeline/process.py` | Base ClaudeProcess with extra_args support |
| `src/superclaude/cli/sprint/models.py` | TurnLedger, GateDisplayState |
| `src/superclaude/cli/sprint/process.py` | Sprint ClaudeProcess pattern (build_prompt with @path), SignalHandler |
| `docs/generated/cli-portify/portify-analysis.md` | Phase 1 output |
| `docs/generated/cli-portify/portify-spec.md` | Phase 2 output |

## Appendix C: Prompt Specifications

### Design Principle: Reuse Existing Skills

**CRITICAL**: Claude subprocess prompts MUST invoke existing `/sc:*` commands and skills whenever equivalent functionality exists. The programmatic pipeline controls **flow** (what runs when, convergence checks, gate validation, budget tracking); Claude subprocesses execute **content** (analysis, review, synthesis) using the project's existing skill library.

This means:
- **brainstorm-gaps** invokes `/sc:brainstorm` — not a manual reimplementation of multi-persona analysis
- **panel-review** invokes `/sc:spec-panel` — not a manual reimplementation of Fowler/Nygard/Whittaker/Crispin
- **analyze-workflow** and **design-pipeline** use custom prompts because no existing skill matches their specific task
- **synthesize-spec** uses a custom prompt because template instantiation is unique to portification

The "Constraint 1: no inter-skill command invocation" from the inference-based SKILL.md does NOT apply in the programmatic pipeline context. Each Claude subprocess is an independent session that can invoke any available command.

### build_analyze_prompt

```python
def build_analyze_prompt(config: PortifyConfig) -> str:
    """Build the workflow analysis prompt (consolidates Phase 1 steps 2-5)."""
    inventory = (config.work_dir / "component-inventory.md").read_text()
    skill_content = config.workflow_path / "SKILL.md"
    refs = list((config.workflow_path / "refs").rglob("*.md")) if (config.workflow_path / "refs").exists() else []

    return f"""You are analyzing a SuperClaude workflow for portification into a programmatic CLI pipeline.

## Input: Component Inventory
{inventory}

## Input: Source Skill
Read the SKILL.md file at: {skill_content}

## Input: Reference Files
{chr(10).join(f'Read: {r}' for r in refs)}

## Task
Produce a complete portification analysis document following this structure:

1. **Protocol Mapping**: Extract the step-by-step behavioral flow. Identify:
   - Phase/wave boundaries
   - Conditional execution paths (flags that skip steps)
   - Implicit inter-step data flow

2. **Step Identification**: Identify step boundaries where:
   - A new artifact is produced
   - Execution mode changes
   - A quality gate must be evaluated
   - Operation type changes

3. **Classification**: Classify each step as:
   - Pure programmatic (deterministic, formula-based)
   - Claude-assisted (content generation, judgment)
   - Hybrid (programmatic setup + Claude + programmatic validation)

4. **Dependency Mapping**: Draw data flow showing which steps produce artifacts consumed by others.

5. **Gate Extraction**: For each step output, define:
   - Gate tier: EXEMPT | LIGHT | STANDARD | STRICT
   - Required frontmatter fields
   - Semantic checks needed
   - Gate mode: BLOCKING | TRAILING

## Required Output Format

Write your analysis to the output file with this frontmatter:

```yaml
---
source_skill: {config.cli_name}
step_count: <integer>
parallel_groups: <integer>
gate_count: <integer>
complexity: <simple|moderate|high>
status: complete
---
```

Include these sections: Source Components, Step Graph, Parallel Groups, Gates Summary,
Data Flow Diagram, Classification Summary, Recommendations.

## Machine-Readable Markers

EXIT_RECOMMENDATION: CONTINUE
"""
```

### build_pipeline_prompt

```python
def build_pipeline_prompt(config: PortifyConfig) -> str:
    """Build the pipeline specification prompt (Phase 2)."""
    analysis = config.analysis_file.read_text()

    return f"""You are designing a programmatic CLI pipeline specification based on workflow analysis.

## Input: Portification Analysis
{analysis}

## Reference: Pipeline Design Patterns
Read: src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md

## Task
Convert the analysis into concrete, code-ready specifications:

1. **Step Graph**: Map each step to Step objects with id, prompt, output_file, gate, timeout.
2. **Models**: Design dataclasses extending PipelineConfig, StepResult.
3. **Prompts**: Write prompt builder function signatures and key content for each Claude step.
4. **Gates**: Define GateCriteria with tier, frontmatter, min_lines, semantic checks.
5. **Pure-Programmatic Steps**: Write actual Python implementation code.
6. **Executor Design**: Sprint-style synchronous supervisor with ThreadPoolExecutor.
7. **Integration Plan**: Click command group, main.py import, file generation order.

## Critical Constraints
- Synchronous execution (threading + time.sleep, NOT async/await)
- Gate functions return tuple[bool, str]
- Runner-authored truth (reports from observed data)
- Deterministic flow control (Python decides, not Claude)
- Reuse pipeline/ primitives (PipelineConfig, Step, StepResult, GateCriteria, etc.)

## Required Output Format

```yaml
---
step_mapping_count: <integer>
model_count: <integer>
gate_definition_count: <integer>
status: complete
---
```

Include: Step Graph, Model Definitions, Prompt Builders, Gate Definitions,
Pure-Programmatic Implementations, Executor Design, Integration Plan.

EXIT_RECOMMENDATION: CONTINUE
"""
```

### build_synthesize_prompt

**Design**: Template (9KB) is embedded inline since the subprocess needs it as a starting scaffold. Analysis and spec are referenced by `@path` — the Claude subprocess reads them via its Read tool, matching the sprint pattern (see `sprint/process.py:122` which uses `@{phase_file}`). This avoids embedding 63KB of prior artifacts in the prompt string while keeping the subprocess self-contained.

```python
def build_synthesize_prompt(config: PortifyConfig) -> str:
    """Build the release spec synthesis prompt (Phase 3 steps a-b).

    Template is embedded inline (9KB). Analysis (16KB) and spec (47KB) are
    referenced by @path for the subprocess to read, matching the sprint
    ClaudeProcess pattern. This keeps the prompt under 15KB while giving
    the subprocess access to all inputs.
    """
    template = config.template_path.read_text()

    return f"""You are synthesizing a release specification from workflow analysis and pipeline spec.

## Input: Release Spec Template (inline — use as starting scaffold)
{template}

## Input: Portification Analysis (Phase 1)
Read this file: @{config.analysis_file}

## Input: Pipeline Specification (Phase 2)
Read this file: @{config.spec_file}

## Step Consolidation Mapping
The analysis identifies 12 logical steps; the pipeline spec consolidates to 7.
Each FR must map to a pipeline step, with notes on which logical steps it consolidates:

| Pipeline Step | FR | Consolidates Logical Steps |
|--------------|-----|---------------------------|
| validate-config | FR-1 | Step 0 (input validation) |
| discover-components | FR-2 | Step 1 (component discovery) |
| analyze-workflow | FR-3 | Steps 2-5 (protocol mapping, step ID, gate extraction, analysis assembly) |
| design-pipeline | FR-4 | Step 6 (pipeline specification) |
| synthesize-spec | FR-5 | Steps 7-8 (template instantiation, content population) |
| brainstorm-gaps | FR-6 | Step 9 (automated brainstorm pass) |
| panel-review | FR-7 | Steps 10-11 (focus pass, critique/scoring/convergence) |

## Task
Fill ALL {{{{SC_PLACEHOLDER:*}}}} sentinels in the template using the analysis and spec.

Mapping:
| Template Section | Source |
|-----------------|--------|
| 1. Problem Statement | Source workflow purpose + why portification needed |
| 2. Solution Overview | Phase 2 pipeline architecture |
| 2.2 Workflow/Data Flow | Phase 1 data flow diagram |
| 3. Functional Requirements | One FR per pipeline step (7 FRs), using consolidation mapping above |
| 4. Architecture | Phase 2 module_plan (new files) |
| 4.5 Data Models | Phase 2 model designs |
| 4.6 Implementation Order | Phase 2 module dependency order |
| 5.2 Gate Criteria | Phase 2 gate_definitions |
| 5.3 Phase Contracts | Phase 1+2 contract schemas |
| 6. NFRs | Standard portification NFRs |
| 7. Risk Assessment | Phase 1 classification confidence + unsupported patterns |
| 8. Test Plan | Phase 2 pattern coverage matrix |
| 10. Downstream Inputs | Themes for roadmap, tasks for tasklist |

Set spec_type to "portification". Set created to today's date.
Leave quality_scores as 0.0 (populated by panel review).
Leave Section 12 empty (populated by brainstorm pass).

## CRITICAL: Self-Validation
After populating, verify ZERO remaining {{{{SC_PLACEHOLDER:*}}}} sentinels.
If any remain, resolve them before finishing.

## Required Output
Write the complete populated spec to the output file.

EXIT_RECOMMENDATION: CONTINUE
"""
```

### build_brainstorm_prompt

**Design**: Invoke the existing `/sc:brainstorm` skill in the Claude subprocess rather than reimplementing brainstorm behavioral patterns. The subprocess receives the draft spec as context and runs the real brainstorm command, which already has multi-persona orchestration, MCP integration, and structured output.

```python
def build_brainstorm_prompt(config: PortifyConfig) -> str:
    """Build prompt that invokes /sc:brainstorm against the draft spec.

    Leverages the existing sc:brainstorm skill which provides:
    - Multi-persona orchestration (architect, analyzer, backend, etc.)
    - Auggie MCP codebase awareness
    - Sequential MCP for structured reasoning
    - Systematic gap identification
    """
    spec_path = config.release_spec_file

    return f"""Execute the following command against the draft release specification:

/sc:brainstorm @{spec_path} --strategy systematic --depth deep --no-codebase

## Context
This is an automated brainstorm pass as part of the cli-portify pipeline.
The spec is a release specification for portifying the sc-cli-portify-protocol
workflow into a programmatic CLI pipeline.

## Required Post-Processing
After the brainstorm completes, perform these steps:

1. Format each finding as:
   {{gap_id, description, severity(high|medium|low), affected_section, persona}}

2. Incorporate actionable findings into the relevant spec body sections.
   Mark as [INCORPORATED] in the gap analysis table.

3. Route unresolvable items to Section 11 (Open Items).
   Mark as [OPEN] in the gap analysis table.

4. Append Section 12 (Brainstorm Gap Analysis) to the spec with the
   findings table and summary: {{total_gaps, incorporated, open, severity_distribution}}

5. Write the COMPLETE updated spec to the output file.

If no gaps are identified: write "No gaps identified by architect, analyzer,
and backend personas. Spec coverage assessed as complete." in Section 12.

EXIT_RECOMMENDATION: CONTINUE
"""
```

### build_panel_prompt

**Design**: Invoke the existing `/sc:spec-panel` skill in the Claude subprocess rather than reimplementing the expert panel behavioral patterns. The subprocess runs the real spec-panel command, which already provides Fowler, Nygard, Whittaker, Crispin expert analysis, quality scoring, and structured finding output.

The convergence loop is handled by the **executor**, not the prompt. Each iteration launches a new Claude subprocess with `/sc:spec-panel`, collects the output, checks convergence, and decides whether to iterate.

> **NOTE [GAP-006]**: The mode parameter below uses `discussion` for iteration 1 and `critique` for subsequent iterations. Per the GAP-006 finding, each iteration should ideally run both focus (discussion) AND critique within a single subprocess. Adjust during implementation to invoke both `--mode discussion` and `--mode critique` in sequence within each iteration's prompt.

```python
def build_panel_prompt(config: PortifyConfig, iteration: int) -> str:
    """Build prompt that invokes /sc:spec-panel for one review iteration.

    Leverages the existing sc:spec-panel skill which provides:
    - Fowler (Architecture), Nygard (Reliability), Whittaker (Adversarial), Crispin (Testing)
    - Structured finding format with severity levels
    - Quality dimension scoring (clarity, completeness, testability, consistency)
    - Sequential MCP for deep analysis
    - Context7 MCP for pattern reference
    """
    spec_path = config.release_spec_file

    mode = "critique" if iteration > 1 else "discussion"

    return f"""Execute the following command against the release specification:

/sc:spec-panel @{spec_path} --mode {mode} --focus correctness,architecture --iterations 1 --format structured

## Context
This is iteration {iteration}/3 of the panel review convergence loop in the
cli-portify pipeline. The spec is a release specification for portifying the
sc-cli-portify-protocol workflow into a programmatic CLI pipeline.

{"## Prior Iteration Context" + chr(10) + "Previous iterations found unaddressed CRITICAL findings. Focus on resolving those." if iteration > 1 else ""}

## Required Post-Processing
After the spec-panel review completes:

1. Incorporate findings by severity:
   - CRITICAL: MUST address (incorporate fix or justify dismissal)
   - MAJOR: Incorporate into spec body (additive-only modifications)
   - MINOR: Append to Section 11 (Open Items)

2. Update the spec frontmatter with quality_scores:
   ```yaml
   quality_scores:
     clarity: <float>
     completeness: <float>
     testability: <float>
     consistency: <float>
     overall: <float>   # mean of above 4
   ```

3. Write the COMPLETE updated spec to: {spec_path}

4. Write panel-report.md to: {config.panel_report_file}
   Include this machine-readable convergence block:
   ```
   CONVERGENCE_STATUS: CONVERGED|NOT_CONVERGED
   UNADDRESSED_CRITICALS: <count>
   QUALITY_OVERALL: <float>
   ```

EXIT_RECOMMENDATION: CONTINUE
"""
```

## Appendix D: Implementation Reference

> Pseudocode and reference implementations for key modules. These define the expected structure and logic for the executor, pure-programmatic steps, and CLI integration. Implementation may refine details but must preserve the contracts and behavioral invariants described here.

### D.1 Pure-Programmatic Step Implementations

#### run_validate_config

```python
def run_validate_config(config: PortifyConfig) -> None:
    """Validate pipeline configuration. Raises ValueError on failure."""
    # Check workflow path resolves
    skill_md = config.workflow_path / "SKILL.md"
    if not skill_md.exists():
        raise ValueError(
            f"INVALID_PATH: '{config.workflow_path}' does not contain SKILL.md"
        )

    # Check name is valid Python identifier
    if not config.module_name.isidentifier():
        raise ValueError(
            f"DERIVATION_FAILED: '{config.module_name}' is not a valid Python identifier"
        )

    # Check output dir parent exists
    output_parent = config.output_dir.parent
    if not output_parent.exists():
        raise ValueError(
            f"OUTPUT_NOT_WRITABLE: Parent '{output_parent}' does not exist"
        )

    # Check no name collision
    if config.output_dir.exists():
        init_file = config.output_dir / "__init__.py"
        if init_file.exists():
            content = init_file.read_text()
            if "Portified from:" not in content and "sc-cli-portify" not in content:
                raise ValueError(
                    f"NAME_COLLISION: '{config.output_dir}' exists and was not "
                    f"generated by portification"
                )

    # Write result
    import json
    result = {
        "workflow_path": str(config.workflow_path),
        "cli_name": config.cli_name,
        "module_name": config.module_name,
        "output_dir": str(config.output_dir),
        "status": "validated",
    }
    result_path = config.work_dir / "validate-config-result.json"
    result_path.write_text(json.dumps(result, indent=2))
```

#### run_discover_components

```python
def run_discover_components(config: PortifyConfig) -> None:
    """Discover and inventory all workflow components. Pure Python."""
    workflow = config.workflow_path
    components = []

    # SKILL.md
    skill_md = workflow / "SKILL.md"
    if skill_md.exists():
        lines = len(skill_md.read_text().splitlines())
        components.append(("Skill", str(skill_md), lines, "Full protocol"))

    # refs/
    refs_dir = workflow / "refs"
    if refs_dir.exists():
        for ref in sorted(refs_dir.rglob("*.md")):
            lines = len(ref.read_text().splitlines())
            components.append((f"Ref: {ref.stem}", str(ref), lines, "Reference"))

    # rules/
    rules_dir = workflow / "rules"
    if rules_dir.exists():
        for rule in sorted(rules_dir.rglob("*")):
            if rule.is_file():
                lines = len(rule.read_text().splitlines())
                components.append((f"Rule: {rule.stem}", str(rule), lines, "Rule"))

    # templates/
    templates_dir = workflow / "templates"
    if templates_dir.exists():
        for tmpl in sorted(templates_dir.rglob("*")):
            if tmpl.is_file():
                lines = len(tmpl.read_text().splitlines())
                components.append((f"Template: {tmpl.stem}", str(tmpl), lines, "Template"))

    # scripts/
    scripts_dir = workflow / "scripts"
    if scripts_dir.exists():
        for script in sorted(scripts_dir.rglob("*")):
            if script.is_file():
                lines = len(script.read_text().splitlines())
                components.append((f"Script: {script.stem}", str(script), lines, "Script"))

    # Find matching command
    cmd_candidates = [
        Path("src/superclaude/commands") / f"{config.cli_name}.md",
        Path(".claude/commands/sc") / f"{config.cli_name}.md",
    ]
    for cmd_path in cmd_candidates:
        if cmd_path.exists():
            lines = len(cmd_path.read_text().splitlines())
            components.append(("Command", str(cmd_path), lines, "CLI command"))
            break

    # Write inventory
    output = config.work_dir / "component-inventory.md"
    lines_out = [
        "---",
        f"source_skill: {config.cli_name}",
        f"component_count: {len(components)}",
        "---",
        "",
        "# Component Inventory",
        "",
        "| Component | Path | Lines | Purpose |",
        "|-----------|------|-------|---------|",
    ]
    for comp_type, path, line_count, purpose in components:
        lines_out.append(f"| {comp_type} | `{path}` | {line_count} | {purpose} |")

    output.write_text("\n".join(lines_out) + "\n")
```

### D.2 Executor Design

#### execute_cli_portify (Main Execution Loop)

```python
def execute_cli_portify(config: PortifyConfig) -> PortifyResult:
    """Execute the cli-portify pipeline with supervised monitoring."""

    # Pre-flight
    if not shutil.which("claude"):
        print("Error: 'claude' binary not found in PATH", file=sys.stderr)
        sys.exit(1)

    # Setup
    handler = SignalHandler()
    handler.install()
    logger = PortifyLogger(config)
    tui = PortifyTUI(config)
    monitor = OutputMonitor()
    result = PortifyResult(config=config)
    ledger = TurnLedger(
        initial_budget=config.max_turns,
        minimum_allocation=10,
        minimum_remediation_budget=5,
    )

    logger.write_header()
    tui.start()

    phase_3_start = None
    phase_4_start = None

    try:
        steps = _build_steps(config)

        for step in steps:
            if handler.shutdown_requested:
                result.outcome = PortifyOutcome.INTERRUPTED
                break

            # Dry-run gate: stop after design-pipeline
            if config.dry_run and step.id == "synthesize-spec":
                result.outcome = PortifyOutcome.DRY_RUN
                for remaining in steps[steps.index(step):]:
                    result.step_results.append(PortifyStepResult(
                        step=remaining, status=PortifyStatus.SKIPPED))
                break

            # Phase timing instrumentation
            if step.id == "synthesize-spec":
                phase_3_start = time.time()
            if step.id == "panel-review":
                if phase_3_start:
                    result.phase_timing["phase_3_seconds"] = time.time() - phase_3_start
                phase_4_start = time.time()

            # Route: programmatic vs Claude
            if step.prompt == "":
                step_result = _run_programmatic_step(step, config)
            elif step.id == "panel-review":
                step_result = _run_convergence_step(step, config, ledger, monitor, tui, handler)
            else:
                # Budget guard
                if not ledger.can_launch():
                    result.outcome = PortifyOutcome.HALTED
                    result.halt_step = step.id
                    break
                step_result = _run_claude_step(step, config, ledger, monitor, tui, handler)

            result.step_results.append(step_result)
            logger.write_step_result(step_result)

            # Gate check
            if step_result.status in (PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL):
                if step.gate and step.gate.enforcement_tier != "EXEMPT":
                    output_path = config.work_dir / step.output_file
                    if output_path.exists():
                        passed, reason = gate_passed(output_path, step.gate)
                        if not passed:
                            step_result.status = PortifyStatus.HALT
                            step_result.gate_failure_reason = reason

            # Handle failure
            if step_result.status not in (
                PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL,
                PortifyStatus.PASS_NO_REPORT, PortifyStatus.SKIPPED
            ):
                result.outcome = PortifyOutcome.HALTED
                result.halt_step = step.id
                # Diagnostics
                collector = DiagnosticCollector()
                bundle = collector.collect(step_result, monitor.state, config)
                classifier = FailureClassifier()
                category = classifier.classify(bundle)
                reporter = ReportGenerator()
                reporter.write_report(bundle, category, config)
                break

        # Phase 4 timing
        if phase_4_start:
            elapsed = time.time() - phase_4_start
            result.phase_timing["phase_4_seconds"] = elapsed
            if elapsed > 900:
                result.warnings.append(
                    "Phase 4 exceeded 15-minute advisory target (NFR-002)"
                )

        # Phase 3 timing warning
        if result.phase_timing["phase_3_seconds"] > 600:
            result.warnings.append(
                "Phase 3 exceeded 10-minute advisory target (NFR-001)"
            )

        # Extract quality scores from panel report if exists
        if config.panel_report_file.exists():
            _extract_convergence_data(result, config)

        result.finished_at = time.time()
        logger.write_summary(result)

    finally:
        tui.stop()
        monitor.stop()
        handler.restore()

    return result
```

#### _run_convergence_step (Convergence Loop Handler)

> **NOTE [F-004]**: The timeout calculation below divides total timeout by max_convergence. Per finding F-004, each iteration should have its own independent timeout (default 300s). Adjust during implementation.

```python
def _run_convergence_step(
    step: Step, config: PortifyConfig, ledger: TurnLedger,
    monitor: OutputMonitor, tui: PortifyTUI, handler: SignalHandler,
) -> PortifyStepResult:
    """Execute the panel-review step with convergence loop."""
    overall_start = time.time()
    last_result = None

    for iteration in range(1, config.max_convergence + 1):
        if handler.shutdown_requested:
            break
        if not ledger.can_launch():
            break

        # Build iteration-specific prompt
        iter_step = Step(
            id=f"panel-review-iter-{iteration}",
            prompt=build_panel_prompt(config, iteration),
            output_file=step.output_file,
            gate=step.gate,
            timeout_seconds=step.timeout_seconds // config.max_convergence,
            inputs=step.inputs,
            gate_mode=step.gate_mode,
        )

        last_result = _run_claude_step(iter_step, config, ledger, monitor, tui, handler)
        last_result.convergence_iteration = iteration

        # Check convergence: parse panel-report.md for machine-readable block
        if config.panel_report_file.exists():
            report = config.panel_report_file.read_text()
            if "CONVERGENCE_STATUS: CONVERGED" in report:
                break
            if "UNADDRESSED_CRITICALS: 0" in report:
                break

    # Build aggregate result
    result = PortifyStepResult(
        step=step,
        status=last_result.status if last_result else PortifyStatus.ERROR,
        started_at=overall_start,
        finished_at=time.time(),
        convergence_iteration=iteration if last_result else 0,
    )

    return result
```

#### _run_programmatic_step (Pure-Programmatic Step Runner)

```python
PROGRAMMATIC_RUNNERS = {
    "validate-config": run_validate_config,
    "discover-components": run_discover_components,
}

def _run_programmatic_step(step: Step, config: PortifyConfig) -> PortifyStepResult:
    """Execute a pure-programmatic step without Claude subprocess."""
    started = time.time()
    try:
        PROGRAMMATIC_RUNNERS[step.id](config)
        return PortifyStepResult(
            step=step,
            status=PortifyStatus.PASS,
            started_at=started,
            finished_at=time.time(),
        )
    except Exception as e:
        return PortifyStepResult(
            step=step,
            status=PortifyStatus.HALT,
            gate_failure_reason=str(e),
            started_at=started,
            finished_at=time.time(),
        )
```

### D.3 Click CLI Integration

#### main.py Registration

```python
# In src/superclaude/cli/main.py
from superclaude.cli.cli_portify import cli_portify_group
app.add_command(cli_portify_group)
```

#### Click Command Group

```python
@click.group("cli-portify")
def cli_portify_group():
    """Portify SuperClaude workflows into programmatic CLI pipelines."""
    pass

@cli_portify_group.command("run")
@click.argument("workflow", type=click.Path(exists=True))
@click.option("--name", default=None, help="CLI subcommand name (kebab-case)")
@click.option("--output", default=None, type=click.Path(), help="Output directory")
@click.option("--dry-run", is_flag=True, help="Analysis only, no spec synthesis")
@click.option("--max-turns", default=200, type=int, help="Turn budget")
@click.option("--skip-review", is_flag=True, help="Skip user review gates")
@click.option("--model", default=None, help="Claude model override")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def run(workflow, name, output, dry_run, max_turns, skip_review, model, debug):
    """Execute the cli-portify pipeline."""
    config = load_cli_portify_config(
        workflow=workflow, name=name, output=output,
        dry_run=dry_run, max_turns=max_turns,
        skip_review=skip_review, model=model, debug=debug,
    )

    if dry_run:
        _print_dry_run(config)

    result = execute_cli_portify(config)

    # Emit return contract
    import json, yaml
    contract = result.to_contract()
    contract_path = config.work_dir / "return-contract.yaml"
    contract_path.write_text(yaml.dump(contract, default_flow_style=False))

    # Print summary
    if result.downstream_ready:
        print(f"\nSpec ready for downstream: {config.release_spec_file}")
    elif result.resume_command():
        print(f"\nResume with: {result.resume_command()}")

    sys.exit(0 if result.outcome.value in ("success", "dry_run") else 1)
```
