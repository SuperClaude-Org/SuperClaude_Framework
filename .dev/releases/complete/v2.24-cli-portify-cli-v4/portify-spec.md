---
source_skill: sc-cli-portify-protocol
cli_name: cli-portify
module_name: cli_portify
prefix: Portify
step_mapping_count: 7
model_count: 6
gate_definition_count: 7
status: completed
---

# Pipeline Specification: cli-portify

## 1. Step Graph Design

Consolidated from 12 logical steps to 7 pipeline steps per analysis recommendations.

### Step Graph

```python
steps = [
    Step(id="validate-config",    prompt="", ...),          # Pure programmatic
    Step(id="discover-components", prompt="", ...),          # Pure programmatic
    Step(id="analyze-workflow",   prompt=build_analyze_prompt, ...),  # Claude
    Step(id="design-pipeline",   prompt=build_pipeline_prompt, ...),  # Claude
    Step(id="synthesize-spec",   prompt=build_synthesize_prompt, ...),# Claude
    Step(id="brainstorm-gaps",   prompt=build_brainstorm_prompt, ...), # Claude
    Step(id="panel-review",      prompt=build_panel_prompt, ...),     # Claude (convergence)
]
```

### Step Definitions

#### Step 1: validate-config (Pure Programmatic)
- **Prompt**: `""` (no Claude subprocess)
- **Output**: `validate-config-result.json`
- **Gate**: EXEMPT
- **Gate Mode**: BLOCKING
- **Timeout**: 10s
- **Inputs**: CLI args
- **Implementation**: `run_validate_config(config)` — resolves workflow path, validates name derivation, checks output directory writability, checks name collision. Emits structured JSON with resolved paths.

#### Step 2: discover-components (Pure Programmatic)
- **Prompt**: `""` (no Claude subprocess)
- **Output**: `component-inventory.md`
- **Gate**: STANDARD (frontmatter: `source_skill`, `component_count`; min_lines: 5)
- **Gate Mode**: BLOCKING
- **Timeout**: 30s
- **Inputs**: [workflow path from config]
- **Implementation**: `run_discover_components(config)` — uses `Path.rglob()` to find SKILL.md, refs/, rules/, templates/, scripts/; counts lines with `len(path.read_text().splitlines())`; generates markdown inventory table. Looks up matching command file in `src/superclaude/commands/` and `.claude/commands/sc/`.

#### Step 3: analyze-workflow (Claude-Assisted)
- **Prompt**: `build_analyze_prompt(config)`
- **Output**: `portify-analysis.md`
- **Gate**: STRICT
- **Gate Mode**: BLOCKING
- **Timeout**: 600s
- **Inputs**: [component-inventory.md, SKILL.md, all refs/]
- **Retry**: 1
- **Notes**: Consolidates logical steps 2-5 from analysis. Claude reads all components and produces the complete analysis document following the `refs/analysis-protocol.md` template. Includes protocol mapping, step identification/classification, gate extraction, dependency mapping, and data flow diagram.

#### Step 4: design-pipeline (Claude-Assisted)
- **Prompt**: `build_pipeline_prompt(config)`
- **Output**: `portify-spec.md` (+ optional `portify-prompts.md`)
- **Gate**: STRICT
- **Gate Mode**: BLOCKING
- **Timeout**: 600s
- **Inputs**: [portify-analysis.md, refs/pipeline-spec.md]
- **Retry**: 1
- **Notes**: Converts analysis into code-ready pipeline specification. USER REVIEW after this step. If `--dry-run`, pipeline halts here.

#### Step 5: synthesize-spec (Claude-Assisted)
- **Prompt**: `build_synthesize_prompt(config)` — returns `str` (template inline, prior artifacts via `@path` references)
- **Output**: `portify-release-spec.md`
- **Gate**: STRICT
- **Gate Mode**: BLOCKING
- **Timeout**: 600s
- **Inputs**: [release-spec-template.md (inline), portify-analysis.md (@path ref), portify-spec.md (@path ref)]
- **Retry**: 1
- **Notes**: Template (9KB) embedded inline as scaffold. Analysis and spec referenced by `@path` for subprocess Read tool access, matching sprint `ClaudeProcess` pattern. Gate checks zero remaining `{{SC_PLACEHOLDER:*}}` sentinels. Includes explicit consolidation mapping (12 logical steps -> 7 pipeline steps) for FR generation.

#### Step 6: brainstorm-gaps (Claude-Assisted via /sc:brainstorm)
- **Prompt**: `build_brainstorm_prompt(config)` — invokes `/sc:brainstorm` skill
- **Output**: `portify-release-spec.md` (updated with Section 12)
- **Gate**: STANDARD
- **Gate Mode**: BLOCKING
- **Timeout**: 600s
- **Inputs**: [portify-release-spec.md]
- **Retry**: 1
- **Notes**: Subprocess invokes the existing `/sc:brainstorm` skill with `--strategy systematic --depth deep`. Leverages its multi-persona orchestration, MCP integrations, and structured output. Post-processing formats findings and incorporates gaps.

#### Step 7: panel-review (Claude-Assisted via /sc:spec-panel, Convergence)
- **Prompt**: `build_panel_prompt(config, iteration)` — invokes `/sc:spec-panel` skill
- **Output**: `portify-release-spec.md` (final), `panel-report.md`
- **Gate**: STRICT
- **Gate Mode**: BLOCKING
- **Timeout**: 900s (covers up to 3 iterations)
- **Inputs**: [portify-release-spec.md]
- **Retry**: 0 (convergence is internal)
- **Notes**: Convergence loop step. Each iteration launches a Claude subprocess that invokes `/sc:spec-panel --focus correctness,architecture`. Leverages the existing expert panel (Fowler, Nygard, Whittaker, Crispin), quality scoring, and structured finding output. Executor handles iteration logic: checks convergence predicate (zero unaddressed CRITICALs) after each iteration. Max 3 iterations. USER REVIEW at end.

## 2. Model Definitions

### PortifyConfig

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

### PortifyStatus

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

### PortifyOutcome

```python
class PortifyOutcome(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"       # Escalated from convergence
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"
    DRY_RUN = "dry_run"
```

### PortifyStepResult

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

### PortifyResult (Aggregate)

```python
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
```

### PortifyMonitorState

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

## 3. Prompt Designs

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

## 4. Gate Definitions

### Semantic Check Functions

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

### Gate Criteria

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

## 5. Pure-Programmatic Step Implementations

### run_validate_config

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

### run_discover_components

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

## 6. Executor Design

### Main Execution Loop

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

### Convergence Loop Handler

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

### Pure-Programmatic Step Runner

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

## 7. Integration Plan

### File Generation Order (respects dependencies)

```
1. models.py          -- No internal deps
2. gates.py           -- Imports from models
3. prompts.py         -- Imports from models
4. config.py          -- Imports from models
5. inventory.py       -- Imports from models (pure-programmatic discovery)
6. monitor.py         -- Imports from models
7. process.py         -- Imports from models, config; extends pipeline.process
8. executor.py        -- Imports from all above
9. tui.py             -- Imports from models
10. logging_.py       -- Imports from models
11. diagnostics.py    -- Imports from models
12. commands.py       -- Imports from config, executor
13. __init__.py       -- Re-exports commands group
```

### main.py Registration

```python
# In src/superclaude/cli/main.py
from superclaude.cli.cli_portify import cli_portify_group
app.add_command(cli_portify_group)
```

### Click Command Group

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

### Module Plan (New Files)

| File | Path | Purpose |
|------|------|---------|
| `__init__.py` | `src/superclaude/cli/cli_portify/__init__.py` | Package exports |
| `models.py` | `src/superclaude/cli/cli_portify/models.py` | PortifyConfig, PortifyStatus, PortifyResult, PortifyMonitorState |
| `gates.py` | `src/superclaude/cli/cli_portify/gates.py` | 7 gate definitions + 7 semantic check functions |
| `prompts.py` | `src/superclaude/cli/cli_portify/prompts.py` | 5 prompt builders |
| `config.py` | `src/superclaude/cli/cli_portify/config.py` | load_cli_portify_config(), name derivation |
| `inventory.py` | `src/superclaude/cli/cli_portify/inventory.py` | run_validate_config(), run_discover_components() |
| `monitor.py` | `src/superclaude/cli/cli_portify/monitor.py` | OutputMonitor with domain signals |
| `process.py` | `src/superclaude/cli/cli_portify/process.py` | PortifyProcess extending ClaudeProcess |
| `executor.py` | `src/superclaude/cli/cli_portify/executor.py` | execute_cli_portify(), convergence loop |
| `tui.py` | `src/superclaude/cli/cli_portify/tui.py` | Rich live dashboard |
| `logging_.py` | `src/superclaude/cli/cli_portify/logging_.py` | Dual JSONL + Markdown logging |
| `diagnostics.py` | `src/superclaude/cli/cli_portify/diagnostics.py` | Failure classification and reporting |
| `commands.py` | `src/superclaude/cli/cli_portify/commands.py` | Click CLI group and subcommands |

### Modified Files

| File | Change |
|------|--------|
| `src/superclaude/cli/main.py` | Add import and `app.add_command(cli_portify_group)` |
