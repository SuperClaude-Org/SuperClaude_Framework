# Workflow Plan: Release Spec Merge Refactoring

**Target file**: `portify-release-spec.md` (560 lines → ~1,550 lines)
**Source file**: `portify-spec.md` (1,288 lines — content extracted, file unchanged)
**Edits**: 4 independent edits, executable in parallel

---

## Edit 1: Expand Section 4.5 (Data Models)

**Current state**: Lines 288-321 — 30-line summary with abbreviated class stubs (no properties, no methods, no field defaults, PortifyStepResult and PortifyMonitorState entirely absent)

**Target state**: Full dataclass definitions with all fields, `@property` methods, `field(default_factory=...)` values, and helper methods — matching portify-spec.md §2 exactly

**Anchor**: Replace the entire content between `### 4.5 Data Models` (line 288) and `### 4.6 Implementation Order` (line 323). The fenced code block on lines 290-321 is what gets replaced.

### Sub-task 1a: PortifyConfig — full definition with derived path properties

**Replace** the 10-line stub (lines 291-301):
```python
# PortifyConfig extends PipelineConfig
@dataclass
class PortifyConfig(PipelineConfig):
    workflow_path: Path                    # Path to skill directory
    cli_name: str = ""                     # kebab-case CLI name
    module_name: str = ""                  # snake_case Python module name
    output_dir: Path = Path(".")           # Target output directory
    skip_review: bool = False              # Skip user review gates
    max_convergence: int = 3              # Max panel review iterations
    stall_timeout: int = 120              # Seconds before stall detection
    stall_action: str = "kill"            # Stall response: kill | warn
```

**With** the full 44-line definition (portify-spec.md:106-150):
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
```

**Why**: The stub lacks `field(default_factory=...)` for Path fields (which would fail at runtime without it), omits `max_turns`, and has no derived path properties — properties the executor, prompts, and process modules all depend on (`config.analysis_file`, `config.release_spec_file`, etc.).

### Sub-task 1b: PortifyStatus — full Enum with values and comments

**Replace** the 4-line compressed one-liner (lines 303-307):
```python
# PortifyStatus extends generic status with domain states
class PortifyStatus(Enum):
    PENDING | RUNNING | PASS | PASS_NO_SIGNAL | PASS_NO_REPORT |
    INCOMPLETE | HALT | TIMEOUT | ERROR | SKIPPED |
    VALIDATION_FAIL | USER_REJECTED | CONVERGENCE_EXHAUSTED
```

**With** the full 15-line definition (portify-spec.md:154-170):
```python
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
```

**Why**: The pipe-delimited stub is not valid Python syntax. Roadmap/tasklist generators need actual enum values to estimate serialization and contract mapping work.

### Sub-task 1c: PortifyOutcome — add missing enum

**Insert after** the PortifyStatus block. Currently absent from release spec.

**Add** (portify-spec.md:174-182):
```python
class PortifyOutcome(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"       # Escalated from convergence
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"
    DRY_RUN = "dry_run"
```

**Why**: The release spec's PortifyResult references `PortifyOutcome` by name but never defines it. Downstream tools see an undefined type.

### Sub-task 1d: PortifyStepResult — add missing dataclass

**Insert after** PortifyOutcome. Currently absent from release spec.

**Add** (portify-spec.md:186-205):
```python
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
```

**Why**: PortifyResult.step_results is `list[PortifyStepResult]` but the type is undefined. The executor, diagnostics, and logging modules all construct and inspect PortifyStepResult instances.

### Sub-task 1e: PortifyResult — replace stub with full implementation

**Replace** the 11-line stub (lines 309-321):
```python
# PortifyResult aggregate with return contract
@dataclass
class PortifyResult:
    config: PortifyConfig
    step_results: list[PortifyStepResult]
    outcome: PortifyOutcome
    convergence_state: str
    convergence_iterations: int
    quality_scores: dict
    phase_timing: dict
    warnings: list[str]
    # Methods: resume_command(), to_contract(), downstream_ready (property)
```

**With** the full 150-line definition (portify-spec.md:209-358) including:
- All fields with `field(default_factory=...)` for mutable defaults
- `downstream_ready` property (boundary: overall >= 7.0)
- `source_step_count` property
- `spec_fr_count` property (reads release spec file, counts `### FR-` headings)
- `resume_command()` method (generates CLI resume string)
- `suggested_resume_budget` property (counts PENDING steps × 30)
- `to_contract()` method (full return contract dict with 20+ fields)
- `_phase_contracts()` helper (step-to-phase status mapping)
- `_failure_phase()` helper (maps halt_step to phase number)
- `_failure_type()` helper (classifies failure: convergence_exhausted, user_rejected, template_failed, etc.)
- `_resume_phase()` helper (maps halt_step to resumable phase)
- `_resume_substep()` helper (maps halt_step to substep label)

**Why**: The stub hides 140 lines of implementation that defines the entire return contract, failure classification, and resume logic. Without this, a roadmap generator cannot assess the complexity of the contract or the resume system.

### Sub-task 1f: PortifyMonitorState — add missing dataclass

**Insert after** PortifyResult, before the closing ``` of the code block. Currently absent from release spec.

**Add** (portify-spec.md:361-392):
```python
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

**Why**: The monitor.py and tui.py modules depend on this state model for stall detection and TUI rendering. Omitting it hides the domain-specific signal fields (persona tracking, placeholder countdown, convergence iteration) that inform monitor complexity.

### Edit 1 Net Change: ~30 lines → ~260 lines (+230)

---

## Edit 2: Add Section 5.2.1 (Semantic Check Implementations)

**Current state**: Section 5.2 (lines 361-371) is a summary table listing gate criteria by step. The semantic check function names appear in the table (`has_required_analysis_sections`, `zero_placeholders`, etc.) but their implementations are absent.

**Target state**: Table unchanged. New subsection `### 5.2.1 Semantic Check Implementations` inserted between the table (line 371) and `### 5.3 Phase Contracts` (line 373), containing all 7 semantic check function implementations plus all 7 GateCriteria object definitions.

**Anchor**: Insert new content after line 371 (`| panel-review | STRICT | ...`) and before line 373 (`### 5.3 Phase Contracts`).

### Sub-task 2a: Insert heading

**Add** after the gate criteria table:
```markdown
### 5.2.1 Semantic Check Implementations
```

### Sub-task 2b: _has_required_analysis_sections()

**Add** (portify-spec.md:723-730):
```python
def _has_required_analysis_sections(content: str) -> bool:
    """Verify portify-analysis.md has all required sections."""
    required = {
        "## Source Components", "## Step Graph", "## Gates Summary",
        "## Data Flow Diagram", "## Classification Summary",
    }
    present = {line.strip() for line in content.splitlines() if line.startswith("## ")}
    return required.issubset(present)
```

**Why**: STRICT gate for analyze-workflow step. Validates 5 mandatory section headings are present.

### Sub-task 2c: _has_data_flow_diagram()

**Add** (portify-spec.md:732-734):
```python
def _has_data_flow_diagram(content: str) -> bool:
    """Verify data flow diagram is present (contains arrow notation)."""
    return "-->" in content or "--->" in content
```

**Why**: STRICT gate for analyze-workflow step. Ensures data flow diagram exists via arrow-notation heuristic.

### Sub-task 2d: _has_step_mappings()

**Add** (portify-spec.md:736-738):
```python
def _has_step_mappings(content: str) -> bool:
    """Verify pipeline spec contains step mapping entries."""
    return "Step(" in content or "step-" in content.lower()
```

**Why**: STRICT gate for design-pipeline step. Validates step definitions are present.

### Sub-task 2e: _all_gates_defined()

**Add** (portify-spec.md:740-747):
```python
def _all_gates_defined(content: str) -> bool:
    """Verify every step has a gate definition."""
    import re
    steps = re.findall(r'id="([^"]+)"', content)
    for step_id in steps:
        if step_id not in content.split("Gate Definitions")[1] if "Gate Definitions" in content else "":
            return False
    return True
```

**Why**: Design-pipeline gate. Cross-references step IDs against gate definitions section. Note: referenced in portify-spec.md but not currently wired into any GateCriteria — candidate for future gate enhancement.

### Sub-task 2f: _zero_placeholders()

**Add** (portify-spec.md:749-751):
```python
def _zero_placeholders(content: str) -> bool:
    """SC-003: Verify zero remaining {{SC_PLACEHOLDER:*}} sentinels."""
    return "{{SC_PLACEHOLDER:" not in content
```

**Why**: STRICT gate for synthesize-spec step. The most critical gate — ensures template is fully populated.

### Sub-task 2g: _has_section_12()

**Add** (portify-spec.md:753-755):
```python
def _has_section_12(content: str) -> bool:
    """Verify Section 12 (Brainstorm Gap Analysis) is present."""
    return "## 12." in content or "## Brainstorm Gap Analysis" in content
```

**Why**: STANDARD gate for brainstorm-gaps step. Note: per F-007 panel finding, this should also validate structural content (findings table or zero-gap summary), not just the heading. That enhancement is tracked in the panel report.

### Sub-task 2h: _quality_scores_valid() and _overall_is_mean()

**Add** (portify-spec.md:757-784):
```python
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

**Why**: Two STRICT gates for panel-review step. `_quality_scores_valid` ensures all 5 score fields exist. `_overall_is_mean` (SC-010) verifies the arithmetic mean invariant with < 0.01 tolerance.

### Sub-task 2i: GateCriteria object definitions

**Add** after the semantic check functions (portify-spec.md:789-857):

All 7 GateCriteria objects:
- `VALIDATE_CONFIG_GATE` — EXEMPT tier, no frontmatter/lines/checks
- `DISCOVER_COMPONENTS_GATE` — STANDARD tier, frontmatter: source_skill, component_count, min 5 lines
- `ANALYZE_WORKFLOW_GATE` — STRICT tier, 5 frontmatter fields, min 100 lines, 2 semantic checks
- `DESIGN_PIPELINE_GATE` — STRICT tier, 3 frontmatter fields, min 200 lines, 1 semantic check
- `SYNTHESIZE_SPEC_GATE` — STRICT tier, 3 frontmatter fields, min 150 lines, 1 semantic check
- `BRAINSTORM_GAPS_GATE` — STANDARD tier, no frontmatter, 1 semantic check
- `PANEL_REVIEW_GATE` — STRICT tier, no frontmatter, 2 semantic checks

**Why**: The Section 5.2 table describes gates in human-readable form. These objects are the machine-readable equivalents — the actual Python code the gates.py module will contain. Having both the table (for quick reference) and the objects (for implementation precision) in the same spec section makes them cross-verifiable.

### Edit 2 Net Change: +0 existing lines modified, +140 lines added

---

## Edit 3: Add Appendix C (Prompt Specifications)

**Current state**: No Appendix C exists. Appendix B (Reference Documents) ends the file.

**Target state**: New `## Appendix C: Prompt Specifications` section inserted after Appendix B, containing the design principle preamble and all 5 prompt builder functions with their full prompt template strings.

**Anchor**: Insert after the last row of the Appendix B table (line ~560) and before the end of the file.

### Sub-task 3a: Heading + design principle preamble

**Add** (portify-spec.md:394-406):

```markdown
## Appendix C: Prompt Specifications

### Design Principle: Reuse Existing Skills

**CRITICAL**: Claude subprocess prompts MUST invoke existing `/sc:*` commands and skills whenever equivalent functionality exists. The programmatic pipeline controls **flow** (what runs when, convergence checks, gate validation, budget tracking); Claude subprocesses execute **content** (analysis, review, synthesis) using the project's existing skill library.

This means:
- **brainstorm-gaps** invokes `/sc:brainstorm` — not a manual reimplementation of multi-persona analysis
- **panel-review** invokes `/sc:spec-panel` — not a manual reimplementation of Fowler/Nygard/Whittaker/Crispin
- **analyze-workflow** and **design-pipeline** use custom prompts because no existing skill matches their specific task
- **synthesize-spec** uses a custom prompt because template instantiation is unique to portification

The "Constraint 1: no inter-skill command invocation" from the inference-based SKILL.md does NOT apply in the programmatic pipeline context. Each Claude subprocess is an independent session that can invoke any available command.
```

**Why**: This is the most important architectural constraint for prompt design. Without it, an implementer might reimplement brainstorm/panel logic in custom prompts, defeating the skill reuse design decision (Section 2.1, row 2).

### Sub-task 3b: build_analyze_prompt

**Add** (portify-spec.md:408-477) — full function with:
- Reads `component-inventory.md` from work_dir
- Points to SKILL.md and refs/*.md files
- Task instructions: protocol mapping, step identification, classification, dependency mapping, gate extraction
- Required output format with YAML frontmatter schema
- Machine-readable `EXIT_RECOMMENDATION: CONTINUE` marker

**Why**: Custom prompt (no existing skill). ~70 lines. The prompt template defines the analysis structure that all downstream steps depend on.

### Sub-task 3c: build_pipeline_prompt

**Add** (portify-spec.md:479-528) — full function with:
- Reads portify-analysis.md content inline
- References pipeline-spec.md ref document
- 7-point task breakdown: step graph, models, prompts, gates, pure-programmatic, executor, integration
- Critical constraints section (synchronous, tuple[bool,str] gates, runner-authored truth, deterministic flow)
- Required output format with YAML frontmatter schema

**Why**: Custom prompt (no existing skill). ~50 lines. Defines the pipeline spec structure that gets synthesized into the release spec.

### Sub-task 3d: build_synthesize_prompt

**Add** (portify-spec.md:530-603) — full function with:
- Design note: template inline (9KB), analysis/spec via @path references
- Step consolidation mapping table (12 logical → 7 pipeline)
- Section-to-source mapping table (13 rows)
- SC-003 self-validation instruction
- `EXIT_RECOMMENDATION: CONTINUE` marker

**Why**: Custom prompt. ~75 lines. The most complex prompt — it must map 13 template sections to their data sources and enforce the zero-placeholder invariant.

### Sub-task 3e: build_brainstorm_prompt

**Add** (portify-spec.md:605-652) — full function with:
- Design note: invokes `/sc:brainstorm` skill, does NOT reimplement
- Command: `/sc:brainstorm @{spec_path} --strategy systematic --depth deep --no-codebase`
- Post-processing instructions: format findings, incorporate actionable gaps, route to Section 11, write Section 12 summary
- Zero-gap handling instruction

**Why**: Skill reuse prompt. ~50 lines. The post-processing instructions are critical — they define how brainstorm output gets structured into the gap analysis table format.

### Sub-task 3f: build_panel_prompt

**Add** (portify-spec.md:654-716) — full function with:
- Design note: invokes `/sc:spec-panel` skill, executor manages convergence
- `iteration` parameter controlling mode (`discussion` for iter 1, `critique` for iter 2+)
- NOTE: Per GAP-006/F-004 findings, the mode mapping needs revision (both focus+critique within each iteration). Add a comment noting this.
- Command: `/sc:spec-panel @{spec_path} --mode {mode} --focus correctness,architecture --iterations 1 --format structured`
- Prior iteration context injection for iter > 1
- Post-processing: incorporate by severity, update frontmatter scores, write panel-report.md with machine-readable convergence block
- Machine-readable markers: `CONVERGENCE_STATUS`, `UNADDRESSED_CRITICALS`, `QUALITY_OVERALL`

**Why**: Skill reuse prompt. ~60 lines. The convergence block format is what the executor parses to check the convergence predicate.

### Edit 3 Net Change: +~320 lines added

---

## Edit 4: Add Appendix D (Implementation Reference)

**Current state**: No Appendix D exists.

**Target state**: New `## Appendix D: Implementation Reference` section appended after Appendix C, containing pure-programmatic step code, executor pseudocode, convergence loop handler, and Click CLI integration.

**Anchor**: Append after Appendix C (which itself follows Appendix B).

### Sub-task 4a: Heading

**Add**:
```markdown
## Appendix D: Implementation Reference

> Pseudocode and reference implementations for key modules. These define the expected structure and logic for the executor, pure-programmatic steps, and CLI integration. Implementation may refine details but must preserve the contracts and behavioral invariants described here.
```

### Sub-task 4b: D.1 Pure-Programmatic Steps — run_validate_config

**Add** under `### D.1 Pure-Programmatic Step Implementations` (portify-spec.md:861-908):

`run_validate_config(config)` — 44 lines:
- Checks SKILL.md existence → `INVALID_PATH`
- Checks module_name is valid identifier → `DERIVATION_FAILED`
- Checks output_dir parent exists → `OUTPUT_NOT_WRITABLE`
- Checks no name collision with non-portified modules → `NAME_COLLISION`
- Writes `validate-config-result.json` on success

**Why**: This is actual Python that goes into `inventory.py`. Having it in the spec means the implementer copies, not reinvents.

### Sub-task 4c: D.1 continued — run_discover_components

**Add** (portify-spec.md:910-983):

`run_discover_components(config)` — 73 lines:
- Scans SKILL.md, refs/, rules/, templates/, scripts/
- Finds matching command file in two candidate paths
- Writes `component-inventory.md` with YAML frontmatter and markdown table

**Why**: Same rationale. Pure Python, directly implementable.

### Sub-task 4d: D.2 Executor Design — execute_cli_portify main loop

**Add** under `### D.2 Executor Design` (portify-spec.md:987-1111):

`execute_cli_portify(config)` — 125 lines:
- Pre-flight: verify `claude` binary
- Setup: SignalHandler, PortifyLogger, PortifyTUI, OutputMonitor, PortifyResult, TurnLedger
- Main loop: iterate steps, check shutdown, handle dry-run gate, phase timing instrumentation
- Step routing: `prompt == ""` → programmatic, `step.id == "panel-review"` → convergence, else → Claude
- Budget guard before Claude steps
- Gate checking after step completion
- Failure handling with DiagnosticCollector, FailureClassifier, ReportGenerator
- Phase timing warnings (NFR-001, NFR-002)
- Quality score extraction from panel report
- Cleanup in finally block

**Why**: This is the central orchestration logic. It defines every control flow branch, every timing hook, every failure path. A roadmap that doesn't see this will underestimate executor.py by 3-5x.

### Sub-task 4e: D.2 continued — _run_convergence_step

**Add** (portify-spec.md:1113-1162):

`_run_convergence_step(step, config, ledger, monitor, tui, handler)` — 50 lines:
- Iteration loop: 1 to max_convergence
- Shutdown and budget guards per iteration
- Builds iteration-specific Step with `build_panel_prompt(config, iteration)`
- Timeout per iteration: `step.timeout_seconds // config.max_convergence`
  - NOTE: Per F-004, this should be independent per-iteration timeout. Add comment.
- Convergence check: parse panel-report.md for `CONVERGENCE_STATUS: CONVERGED` or `UNADDRESSED_CRITICALS: 0`
- Returns aggregate PortifyStepResult

**Why**: The convergence loop is the most novel piece of the executor. Its timeout strategy, convergence predicate parsing, and budget management are all implementation-critical.

### Sub-task 4f: D.2 continued — _run_programmatic_step

**Add** (portify-spec.md:1164-1191):

`_run_programmatic_step(step, config)` — 28 lines:
- `PROGRAMMATIC_RUNNERS` dict mapping step IDs to functions
- Try/except wrapper returning PortifyStepResult with PASS or HALT status
- Timing instrumentation

**Why**: Simple but defines the routing contract between the executor and inventory.py.

### Sub-task 4g: D.3 Click CLI Integration — command group + run command

**Add** under `### D.3 Click CLI Integration` (portify-spec.md:1221-1264):

Click CLI definition — 44 lines:
- `@click.group("cli-portify")` group
- `@cli_portify_group.command("run")` with all options:
  - `workflow` (PATH argument, required)
  - `--name`, `--output`, `--dry-run`, `--max-turns`, `--skip-review`, `--model`, `--debug`
- Calls `load_cli_portify_config()` → `execute_cli_portify()` → `result.to_contract()`
- Writes return-contract.yaml
- Prints summary (downstream_ready or resume_command)
- Exit code: 0 for success/dry_run, 1 otherwise

**Why**: Defines the exact CLI surface that users interact with. Cross-references Section 5.1 CLI Surface table.

### Sub-task 4h: D.3 continued — main.py registration

**Add** (portify-spec.md:1213-1219):
```python
# In src/superclaude/cli/main.py
from superclaude.cli.cli_portify import cli_portify_group
app.add_command(cli_portify_group)
```

**Why**: The only modification to an existing file. 2 lines. Cross-references Section 4.2 Modified Files.

### Edit 4 Net Change: +~300 lines added

---

## Summary

| Edit | Section | Current Lines | After Lines | Delta |
|------|---------|--------------|-------------|-------|
| 1 | 4.5 Data Models | ~30 | ~260 | +230 |
| 2 | 5.2.1 Semantic Checks + Gate Objects | 0 | ~140 | +140 |
| 3 | Appendix C: Prompt Specifications | 0 | ~320 | +320 |
| 4 | Appendix D: Implementation Reference | 0 | ~300 | +300 |
| **Total** | | **~560** | **~1,550** | **+990** |

## Execution Plan

All 4 edits are **independent** — they modify non-overlapping line ranges:
- Edit 1: lines 288-321 (replace in-place)
- Edit 2: insert between lines 371-373
- Edit 3: append after ~line 560
- Edit 4: append after Edit 3

**Recommended order** (bottom-up to avoid offset drift):
1. **Edit 4** (Appendix D) — append at end of file
2. **Edit 3** (Appendix C) — append after Appendix B
3. **Edit 2** (Section 5.2.1) — insert between 5.2 and 5.3
4. **Edit 1** (Section 4.5) — in-place replacement

## Post-Merge Validation

After all 4 edits:
1. `grep -c '{{SC_PLACEHOLDER:' portify-release-spec.md` → must return 0
2. `grep -c '## Appendix' portify-release-spec.md` → must return 4 (A, B, C, D)
3. `grep -c 'def ' portify-release-spec.md` → should be ~20+ (7 semantic checks + 5 prompt builders + 5 executor functions + 2 programmatic steps + 1 CLI)
4. `wc -l portify-release-spec.md` → should be ~1,550 ± 50
5. All 7 FR cross-references to gate criteria should match between Section 3 (FRs), Section 5.2 (table), and Section 5.2.1 (objects)

## What Gets Deleted

**Nothing.** portify-spec.md remains unchanged as the canonical Phase 2 artifact. The release spec becomes self-contained by incorporating its content. Both documents coexist — Appendix B already references portify-spec.md.
