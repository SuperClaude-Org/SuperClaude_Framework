---
status: completed
step_count: 12
step_mapping:
  step-0: input-validation
  step-1: component-discovery
  step-2: protocol-mapping
  step-3: analysis-synthesis
  step-4: user-review-p1
  step-5: step-graph-design
  step-6: models-gates-design
  step-7: prompts-executor-design
  step-8: pipeline-spec-assembly
  step-9: user-review-p2
  step-10: release-spec-synthesis
  step-11: spec-panel-review
module_plan:
  - models.py
  - gates.py
  - prompts.py
  - config.py
  - inventory.py
  - executor.py
  - monitor.py
  - process.py
  - tui.py
  - logging_.py
  - diagnostics.py
  - commands.py
  - __init__.py
gate_definitions:
  G-000: STANDARD (config validation)
  G-001: STANDARD (component inventory)
  G-002: STRICT (protocol map)
  G-003: STRICT (analysis report)
  G-004: STANDARD (user review P1)
  G-005: STRICT (step graph)
  G-006: STRICT (models/gates spec)
  G-007: STRICT (prompts/executor spec)
  G-008: STRICT (pipeline spec)
  G-009: STANDARD (user review P2)
  G-010: STRICT (release spec)
  G-011: STRICT (panel review)
---

# Pipeline Specification: cli-portify

## 1. Step Graph

### Step Definitions

All steps are sequential. No parallel groups.

#### Step 0: `input-validation` (Pure Programmatic)

```python
Step(
    id="input-validation",
    prompt="",  # Pure programmatic — no Claude subprocess
    output_file=Path("portify-config.yaml"),
    gate=GATE_G000,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=30,
    inputs=[],
    retry_limit=0,
)
```

**Implementation**: Python function `validate_and_build_config()` in `config.py`.
- Resolve `--workflow` to skill directory (glob `src/superclaude/skills/`)
- Verify `SKILL.md` exists in resolved path
- Derive CLI name: strip `sc-` prefix, strip `-protocol` suffix, kebab-case
- Check name collision against existing `src/superclaude/cli/` modules
- Check output directory parent is writable
- Emit `portify-config.yaml` with resolved paths

#### Step 1: `component-discovery` (Pure Programmatic)

```python
Step(
    id="component-discovery",
    prompt="",  # Pure programmatic
    output_file=Path("component-inventory.yaml"),
    gate=GATE_G001,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=60,
    inputs=[Path("portify-config.yaml")],
    retry_limit=0,
)
```

**Implementation**: Python function `discover_components()` in `inventory.py`.
- Glob for command `.md` matching workflow name in `src/superclaude/commands/` and `.claude/commands/sc/`
- Read SKILL.md from workflow path
- Glob `refs/`, `rules/`, `templates/`, `scripts/` subdirectories
- Find agent `.md` files referenced in skill frontmatter
- Count lines per file with `wc -l` equivalent
- Emit YAML inventory: `{path, lines, purpose, type}` per component

#### Step 2: `protocol-mapping` (Claude-Assisted)

```python
Step(
    id="protocol-mapping",
    prompt=build_protocol_mapping_prompt(config),
    output_file=Path("protocol-map.md"),
    gate=GATE_G002,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=600,
    inputs=[Path("component-inventory.yaml")],
    retry_limit=1,
)
```

Claude reads all source files from inventory and extracts:
- Step-by-step behavioral flow with phase/wave boundaries
- Step boundary identification (artifact, agent, mode, gate, operation changes)
- Classification per step (pure-programmatic / claude-assisted / hybrid)
- Dependency mapping and parallel group identification
- Gate extraction with tier assignment and mode assignment

#### Step 3: `analysis-synthesis` (Claude-Assisted)

```python
Step(
    id="analysis-synthesis",
    prompt=build_analysis_synthesis_prompt(config),
    output_file=Path("portify-analysis-report.md"),
    gate=GATE_G003,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=600,
    inputs=[Path("protocol-map.md"), Path("component-inventory.yaml")],
    retry_limit=1,
)
```

Claude synthesizes protocol map + inventory into the structured analysis format (refs/analysis-protocol.md template). This is the Phase 1 deliverable.

#### Step 4: `user-review-p1` (Pure Programmatic — Pipeline Pause)

```python
Step(
    id="user-review-p1",
    prompt="",  # Pure programmatic — checkpoint/pause
    output_file=Path("phase1-approval.yaml"),
    gate=GATE_G004,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=0,  # No timeout — user interaction
    inputs=[Path("portify-analysis-report.md")],
    retry_limit=0,
)
```

**Implementation**: `emit_review_checkpoint()` in `executor.py`.
- Write `phase1-approval.yaml` with `status: pending`
- Print analysis report path to console
- Exit pipeline with resume information
- On `--resume`, check `phase1-approval.yaml` has `status: approved`

#### Step 5: `step-graph-design` (Claude-Assisted)

```python
Step(
    id="step-graph-design",
    prompt=build_step_graph_prompt(config),
    output_file=Path("step-graph-spec.md"),
    gate=GATE_G005,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=600,
    inputs=[Path("portify-analysis-report.md")],
    retry_limit=1,
)
```

Claude maps each workflow step to pipeline `Step` objects, designs batched parallel groups, defines `build_steps()` function signature.

#### Step 6: `models-gates-design` (Claude-Assisted)

```python
Step(
    id="models-gates-design",
    prompt=build_models_gates_prompt(config),
    output_file=Path("models-gates-spec.md"),
    gate=GATE_G006,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=600,
    inputs=[Path("step-graph-spec.md"), Path("portify-analysis-report.md")],
    retry_limit=1,
)
```

Claude designs domain dataclasses (Config, Status, Result, MonitorState) extending pipeline base types. Designs GateCriteria per step with semantic check function specs.

#### Step 7: `prompts-executor-design` (Claude-Assisted)

```python
Step(
    id="prompts-executor-design",
    prompt=build_prompts_executor_prompt(config),
    output_file=Path("prompts-executor-spec.md"),
    gate=GATE_G007,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=600,
    inputs=[Path("step-graph-spec.md"), Path("models-gates-spec.md")],
    retry_limit=1,
)
```

Claude writes prompt builders for each Claude-assisted step. Designs sprint-style synchronous supervisor executor. Writes pure-programmatic step implementations. Plans Click command group and main.py integration.

#### Step 8: `pipeline-spec-assembly` (Hybrid)

```python
Step(
    id="pipeline-spec-assembly",
    prompt=build_assembly_prompt(config),
    output_file=Path("portify-spec.md"),
    gate=GATE_G008,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=600,
    inputs=[
        Path("step-graph-spec.md"),
        Path("models-gates-spec.md"),
        Path("prompts-executor-spec.md"),
    ],
    retry_limit=1,
)
```

Merges three Phase 2 sub-specs into consolidated pipeline specification. Programmatic pre-assembly (concatenation, deduplication) followed by Claude synthesis for coherent narrative.

#### Step 9: `user-review-p2` (Pure Programmatic — Pipeline Pause)

```python
Step(
    id="user-review-p2",
    prompt="",  # Pure programmatic — checkpoint/pause
    output_file=Path("phase2-approval.yaml"),
    gate=GATE_G009,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=0,
    inputs=[Path("portify-spec.md")],
    retry_limit=0,
)
```

**Implementation**: Same pattern as step 4. Phase 2→3 entry gate verifies:
- `portify-spec.md` status: completed
- All blocking checks passed
- `step_mapping` contains ≥1 entry

#### Step 10: `release-spec-synthesis` (Claude-Assisted)

```python
Step(
    id="release-spec-synthesis",
    prompt=build_release_spec_prompt(config),
    output_file=Path("portify-release-spec.md"),
    gate=GATE_G010,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=900,
    inputs=[
        Path("portify-analysis-report.md"),
        Path("portify-spec.md"),
    ],
    retry_limit=1,
)
```

Sub-steps within single Claude call:
1. **3a**: Load template from `src/superclaude/examples/release-spec-template.md`, create working copy
2. **3b**: Populate 13 template sections from Phase 1+2 outputs (see mapping table in SKILL.md)
3. **3c**: Automated brainstorm pass — 3 persona perspectives (architect, analyzer, backend) producing `{gap_id, description, severity, affected_section, persona}` findings
4. **3d**: Gap incorporation — actionable findings into spec body, unresolvable to Section 11

Gate validates: zero `{{SC_PLACEHOLDER:*}}` sentinels remaining, Section 12 brainstorm present.

#### Step 11: `spec-panel-review` (Claude-Assisted — Convergence Loop)

```python
Step(
    id="spec-panel-review",
    prompt=build_panel_review_prompt(config),
    output_file=Path("portify-release-spec.md"),  # Updated in place
    gate=GATE_G011,
    gate_mode=GateMode.BLOCKING,
    timeout_seconds=1200,
    inputs=[Path("portify-release-spec.md")],
    retry_limit=0,  # Convergence loop handles retries internally
)
```

**Convergence loop** (max 3 iterations):

States: `REVIEWING → INCORPORATING → SCORING → CONVERGED|ESCALATED`

Per iteration:
1. **4a Focus pass**: 4 experts (Fowler, Nygard, Whittaker, Crispin) with `--focus correctness,architecture`
2. **4b Focus incorporation**: CRITICAL must be addressed, MAJOR incorporated, MINOR to Section 11
3. **4c Critique pass**: Full expert panel in critique mode, produces quality scores
4. **4d Scoring**: Compute `overall = mean(clarity, completeness, testability, consistency)`, check convergence

**Terminal conditions**:
- CONVERGED: zero unaddressed CRITICALs → `status: success`
- ESCALATED: 3 iterations exhausted → `status: partial`, escalate to user

**Downstream ready gate**: `if overall >= 7.0 then downstream_ready = true`

Additional output: `panel-report.md` with all findings, scores, convergence status.

## 2. Models

### `PortifyPhaseType` Enum

```python
class PortifyPhaseType(Enum):
    """Semantic phase classification for portify steps."""
    PREREQUISITES = "prerequisites"      # Steps 0-1
    ANALYSIS = "analysis"                # Steps 2-3
    USER_REVIEW = "user_review"          # Steps 4, 9
    SPECIFICATION = "specification"      # Steps 5-8
    SYNTHESIS = "synthesis"              # Step 10
    PANEL_REVIEW = "panel_review"        # Step 11
```

### `PortifyStatus` Enum

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
    AWAITING_REVIEW = "awaiting_review"  # Domain-specific: user review gates
```

### `PortifyOutcome` Enum

```python
class PortifyOutcome(Enum):
    SUCCESS = "success"
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"
    DRY_RUN = "dry_run"
    AWAITING_REVIEW = "awaiting_review"
```

### `ConvergenceState` Enum

```python
class ConvergenceState(Enum):
    NOT_STARTED = "NOT_STARTED"
    REVIEWING = "REVIEWING"
    INCORPORATING = "INCORPORATING"
    SCORING = "SCORING"
    CONVERGED = "CONVERGED"
    ESCALATED = "ESCALATED"
```

### `PortifyConfig(PipelineConfig)`

```python
@dataclass
class PortifyConfig(PipelineConfig):
    # --- Required inputs ---
    workflow_path: Path = Path(".")
    cli_name: str = ""
    output_dir: Path = Path(".")

    # --- Behavioral flags ---
    stall_timeout: int = 300
    stall_action: str = "kill"
    resume_from: str | None = None   # Step ID to resume from

    # --- Derived paths ---
    @property
    def module_name(self) -> str:
        return self.cli_name.replace("-", "_")

    @property
    def results_dir(self) -> Path:
        return self.work_dir / "results"

    @property
    def artifacts_dir(self) -> Path:
        return self.work_dir / "artifacts"

    @property
    def execution_log_jsonl(self) -> Path:
        return self.work_dir / "execution-log.jsonl"

    @property
    def execution_log_md(self) -> Path:
        return self.work_dir / "execution-log.md"

    @property
    def skill_md_path(self) -> Path:
        return self.workflow_path / "SKILL.md"

    @property
    def template_path(self) -> Path:
        return Path("src/superclaude/examples/release-spec-template.md")
```

### `PortifyStep(Step)`

```python
@dataclass
class PortifyStep(Step):
    phase_type: PortifyPhaseType = PortifyPhaseType.PREREQUISITES
    is_programmatic: bool = False
    convergence_max_iterations: int = 0  # 0 = no convergence loop; 3 for step 11
```

### `PortifyStepResult(StepResult)`

```python
@dataclass
class PortifyStepResult(StepResult):
    status: PortifyStatus = PortifyStatus.PENDING
    exit_code: int | None = None
    started_at: float | None = None
    finished_at: float | None = None
    output_bytes: int = 0
    error_bytes: int = 0
    # Domain-specific:
    artifacts_produced: list[str] = field(default_factory=list)
    gate_details: dict = field(default_factory=dict)
    convergence_iterations: int = 0
    quality_scores: dict[str, float] = field(default_factory=dict)
```

### `PortifyResult`

```python
@dataclass
class PortifyResult:
    config: PortifyConfig
    step_results: list[PortifyStepResult] = field(default_factory=list)
    outcome: PortifyOutcome = PortifyOutcome.SUCCESS
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    halt_step: str | None = None
    convergence_state: ConvergenceState = ConvergenceState.NOT_STARTED
    quality_scores: dict[str, float] = field(default_factory=dict)
    phase_timing: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at or time.time()
        return end - self.started_at

    @property
    def steps_passed(self) -> int:
        return sum(1 for r in self.step_results
                   if r.status in (PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL))

    @property
    def downstream_ready(self) -> bool:
        overall = self.quality_scores.get("overall", 0.0)
        return overall >= 7.0

    def resume_command(self) -> str | None:
        if self.halt_step:
            return (
                f"superclaude cli-portify run "
                f"--workflow {self.config.workflow_path} "
                f"--name {self.config.cli_name} "
                f"--resume {self.halt_step} "
                f"--max-turns {self.suggested_resume_budget}"
            )
        return None

    @property
    def suggested_resume_budget(self) -> int:
        remaining = sum(1 for r in self.step_results
                        if r.status in (PortifyStatus.PENDING, PortifyStatus.INCOMPLETE))
        return remaining * 25
```

### `PortifyMonitorState`

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
    # Domain-specific:
    last_phase: str | None = None
    current_artifact: str | None = None
    convergence_iteration: int = 0
    findings_count: int = 0
    placeholders_remaining: int = 0
```

## 3. Gates

### Semantic Check Functions

```python
def has_valid_yaml_config(content: str) -> bool:
    """Verify content is valid YAML with required config fields."""

def has_component_inventory(content: str) -> bool:
    """Verify inventory lists at least one component with SKILL.md."""

def has_step_classifications(content: str) -> bool:
    """Verify all steps have type classification (pure-programmatic/claude-assisted/hybrid)."""

def has_required_analysis_sections(content: str) -> bool:
    """Verify required sections: Source Components, Step Graph, Parallel Groups, Gates Summary, Data Flow, Classifications, Recommendations."""

def has_step_definitions(content: str) -> bool:
    """Verify each step has id, prompt/programmatic marker, output_file, gate, timeout."""

def has_gate_signatures(content: str) -> bool:
    """Verify gate check functions specify tuple[bool, str] return pattern."""

def has_exit_recommendation_markers(content: str) -> bool:
    """Verify prompts specify EXIT_RECOMMENDATION: CONTINUE|HALT markers."""

def has_step_count_consistency(content: str) -> bool:
    """Verify step_mapping count matches declared step_count in frontmatter."""

def has_zero_placeholders(content: str) -> bool:
    """Verify zero remaining {{SC_PLACEHOLDER:*}} sentinels."""

def has_brainstorm_section(content: str) -> bool:
    """Verify Section 12 Brainstorm Gap Analysis is present."""

def has_quality_scores(content: str) -> bool:
    """Verify quality_scores with clarity, completeness, testability, consistency, overall."""

def has_criticals_addressed(content: str) -> bool:
    """Verify all CRITICAL findings are marked [INCORPORATED] or [DISMISSED]."""

def has_exit_recommendation(content: str) -> bool:
    """Verify EXIT_RECOMMENDATION marker present."""

def has_approval_status(content: str) -> bool:
    """Verify approval status field is present (approved/rejected/pending)."""
```

### Gate Definitions

```python
GATE_G000 = GateCriteria(
    required_frontmatter_fields=["workflow_path", "cli_name", "output_dir"],
    min_lines=0,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck("valid_yaml_config", has_valid_yaml_config, "Config YAML is invalid or missing required fields"),
    ],
)

GATE_G001 = GateCriteria(
    required_frontmatter_fields=["component_count"],
    min_lines=0,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck("component_inventory", has_component_inventory, "Inventory must list at least one component with SKILL.md"),
    ],
)

GATE_G002 = GateCriteria(
    required_frontmatter_fields=["status", "step_count", "parallel_groups"],
    min_lines=50,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("step_classifications", has_step_classifications, "All steps must have type classification"),
        SemanticCheck("exit_recommendation", has_exit_recommendation, "EXIT_RECOMMENDATION marker missing"),
    ],
)

GATE_G003 = GateCriteria(
    required_frontmatter_fields=["source_skill", "step_count", "gate_count"],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("required_sections", has_required_analysis_sections, "Missing required analysis sections"),
        SemanticCheck("exit_recommendation", has_exit_recommendation, "EXIT_RECOMMENDATION marker missing"),
    ],
)

GATE_G004 = GateCriteria(
    required_frontmatter_fields=["status"],
    min_lines=0,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck("approval_status", has_approval_status, "Approval status must be present"),
    ],
)

GATE_G005 = GateCriteria(
    required_frontmatter_fields=["step_count", "step_mapping"],
    min_lines=50,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("step_definitions", has_step_definitions, "Steps must have id, prompt, output_file, gate, timeout"),
        SemanticCheck("exit_recommendation", has_exit_recommendation, "EXIT_RECOMMENDATION marker missing"),
    ],
)

GATE_G006 = GateCriteria(
    required_frontmatter_fields=["model_count", "gate_count"],
    min_lines=80,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("gate_signatures", has_gate_signatures, "Gate checks must specify tuple[bool, str] return"),
        SemanticCheck("exit_recommendation", has_exit_recommendation, "EXIT_RECOMMENDATION marker missing"),
    ],
)

GATE_G007 = GateCriteria(
    required_frontmatter_fields=["prompt_count", "executor_style"],
    min_lines=80,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("exit_markers", has_exit_recommendation_markers, "Prompts must specify EXIT_RECOMMENDATION markers"),
        SemanticCheck("exit_recommendation", has_exit_recommendation, "EXIT_RECOMMENDATION marker missing"),
    ],
)

GATE_G008 = GateCriteria(
    required_frontmatter_fields=["status", "step_mapping", "module_plan"],
    min_lines=200,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("step_count_consistency", has_step_count_consistency, "step_mapping count must match step_count"),
        SemanticCheck("exit_recommendation", has_exit_recommendation, "EXIT_RECOMMENDATION marker missing"),
    ],
)

GATE_G009 = GateCriteria(
    required_frontmatter_fields=["status"],
    min_lines=0,
    enforcement_tier="STANDARD",
    semantic_checks=[
        SemanticCheck("approval_status", has_approval_status, "Approval status must be present"),
    ],
)

GATE_G010 = GateCriteria(
    required_frontmatter_fields=["title", "status", "quality_scores"],
    min_lines=300,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("zero_placeholders", has_zero_placeholders, "{{SC_PLACEHOLDER:*}} sentinels remain in spec"),
        SemanticCheck("brainstorm_section", has_brainstorm_section, "Section 12 Brainstorm Gap Analysis missing"),
        SemanticCheck("exit_recommendation", has_exit_recommendation, "EXIT_RECOMMENDATION marker missing"),
    ],
)

GATE_G011 = GateCriteria(
    required_frontmatter_fields=["quality_scores"],
    min_lines=0,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck("quality_scores", has_quality_scores, "Quality scores must include clarity, completeness, testability, consistency, overall"),
        SemanticCheck("criticals_addressed", has_criticals_addressed, "All CRITICAL findings must be [INCORPORATED] or [DISMISSED]"),
    ],
)

ALL_GATES = {
    "G-000": GATE_G000,
    "G-001": GATE_G001,
    "G-002": GATE_G002,
    "G-003": GATE_G003,
    "G-004": GATE_G004,
    "G-005": GATE_G005,
    "G-006": GATE_G006,
    "G-007": GATE_G007,
    "G-008": GATE_G008,
    "G-009": GATE_G009,
    "G-010": GATE_G010,
    "G-011": GATE_G011,
}
```

## 4. Prompts

### Prompt Builders

One builder per Claude-assisted step. All follow the cleanup_audit pattern:

```python
def build_protocol_mapping_prompt(config: PortifyConfig) -> str:
    """Step 2: Read all source files and extract structured protocol map."""
    # Opens with /sc:task-unified framing
    # Embeds component-inventory.yaml content
    # Requires: step boundaries, classifications, dependencies, gates
    # Output: protocol-map.md with frontmatter {status, step_count, parallel_groups}
    # Sections: Step Graph, Data Flow, Classifications
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT

def build_analysis_synthesis_prompt(config: PortifyConfig) -> str:
    """Step 3: Synthesize protocol map + inventory into analysis report."""
    # Embeds protocol-map.md and component-inventory.yaml
    # Follows refs/analysis-protocol.md output format
    # Output: portify-analysis-report.md with frontmatter {source_skill, step_count, gate_count}
    # Sections: Source Components, Step Graph, Parallel Groups, Gates Summary, Data Flow Diagram, Classification Summary, Recommendations
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT

def build_step_graph_prompt(config: PortifyConfig) -> str:
    """Step 5: Map workflow steps to pipeline Step objects."""
    # Embeds portify-analysis-report.md
    # References refs/pipeline-spec.md patterns
    # Output: step-graph-spec.md with frontmatter {step_count, step_mapping}
    # Sections: Step Definitions, Parallel Groups, Dependencies
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT

def build_models_gates_prompt(config: PortifyConfig) -> str:
    """Step 6: Design domain dataclasses and gate criteria."""
    # Embeds step-graph-spec.md and portify-analysis-report.md
    # Output: models-gates-spec.md with frontmatter {model_count, gate_count}
    # Sections: Config Model, Status Enum, Result Model, Monitor State, Gate Criteria, Semantic Checks
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT

def build_prompts_executor_prompt(config: PortifyConfig) -> str:
    """Step 7: Write prompt builders and executor design."""
    # Embeds step-graph-spec.md and models-gates-spec.md
    # Output: prompts-executor-spec.md with frontmatter {prompt_count, executor_style}
    # Sections: Prompt Builders, Executor Design, Pure-Programmatic Implementations, Integration Plan
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT

def build_assembly_prompt(config: PortifyConfig) -> str:
    """Step 8: Merge sub-specs into consolidated pipeline specification."""
    # Embeds step-graph-spec.md, models-gates-spec.md, prompts-executor-spec.md
    # Output: portify-spec.md with frontmatter {status, step_mapping, module_plan, gate_definitions}
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT

def build_release_spec_prompt(config: PortifyConfig) -> str:
    """Step 10: Synthesize release spec from Phase 1+2 outputs."""
    # Embeds portify-analysis-report.md, portify-spec.md
    # References release-spec-template.md (loads via --file arg if >50KB)
    # Sub-steps: 3a template instantiation, 3b content population, 3c brainstorm (3 personas), 3d gap incorporation
    # Output: portify-release-spec.md with frontmatter {title, status, quality_scores}
    # Validates: zero {{SC_PLACEHOLDER:*}} sentinels, Section 12 present
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT

def build_panel_review_prompt(config: PortifyConfig) -> str:
    """Step 11: Run spec panel review with convergence loop."""
    # Embeds portify-release-spec.md
    # 4a: Focus pass (Fowler, Nygard, Whittaker, Crispin) with --focus correctness,architecture
    # 4b: Focus incorporation (CRITICAL/MAJOR/MINOR routing)
    # 4c: Critique pass (full expert panel, quality scores)
    # 4d: Scoring and convergence check
    # Convergence: max 3 iterations, zero unaddressed CRITICALs → CONVERGED
    # Output: updated portify-release-spec.md + panel-report.md
    # Terminal: EXIT_RECOMMENDATION: CONTINUE|HALT
```

If prompts exceed 300 lines collectively, split into `portify-prompts.md`.

## 5. Pure-Programmatic Step Implementations

### Step 0: `validate_and_build_config()`

```python
def validate_and_build_config(
    workflow: str,
    name: str | None,
    output: str | None,
    dry_run: bool,
    max_turns: int,
    model: str,
) -> PortifyConfig:
    """Validate CLI inputs and construct pipeline config."""
    # 1. Resolve workflow path
    workflow_path = _resolve_workflow_path(workflow)

    # 2. Derive or validate CLI name
    cli_name = name or _derive_cli_name(workflow_path.name)

    # 3. Resolve output directory
    output_dir = Path(output) if output else Path(f"src/superclaude/cli/{cli_name.replace('-', '_')}/")

    # 4. Check name collision
    if output_dir.exists() and not _is_portified_module(output_dir):
        raise PortifyValidationError("NAME_COLLISION", f"CLI module '{cli_name}' already exists")

    # 5. Check output parent writable
    if not output_dir.parent.exists():
        raise PortifyValidationError("OUTPUT_NOT_WRITABLE", f"Parent '{output_dir.parent}' does not exist")

    # 6. Build config
    work_dir = Path(f".dev/portify-workdir/{cli_name}/")
    work_dir.mkdir(parents=True, exist_ok=True)

    config = PortifyConfig(
        workflow_path=workflow_path,
        cli_name=cli_name,
        output_dir=output_dir,
        work_dir=work_dir,
        dry_run=dry_run,
        max_turns=max_turns,
        model=model,
    )

    # 7. Emit config YAML
    _write_config_yaml(config, work_dir / "portify-config.yaml")
    return config


def _resolve_workflow_path(workflow: str) -> Path:
    """Resolve workflow name or path to skill directory."""
    path = Path(workflow)
    if path.is_dir() and (path / "SKILL.md").exists():
        return path

    # Try name-based resolution
    candidates = list(Path("src/superclaude/skills/").glob(f"*{workflow}*/SKILL.md"))
    if len(candidates) == 0:
        raise PortifyValidationError("INVALID_PATH", f"No skill found for '{workflow}'")
    if len(candidates) > 1:
        dirs = [str(c.parent) for c in candidates]
        raise PortifyValidationError("AMBIGUOUS_PATH", f"Multiple candidates: {dirs}")

    return candidates[0].parent


def _derive_cli_name(skill_dir_name: str) -> str:
    """Derive CLI name from skill directory name."""
    name = skill_dir_name
    if name.startswith("sc-"):
        name = name[3:]
    if name.endswith("-protocol"):
        name = name[:-9]
    if not name or not name.replace("-", "").isalnum():
        raise PortifyValidationError("DERIVATION_FAILED", f"Cannot derive name from '{skill_dir_name}'")
    return name


def _is_portified_module(path: Path) -> bool:
    """Check if existing module was generated by portification."""
    init = path / "__init__.py"
    if init.exists():
        content = init.read_text()
        return "Generated by" in content or "Portified from" in content
    return False
```

### Step 1: `discover_components()`

```python
def discover_components(config: PortifyConfig) -> dict:
    """Discover all source components for the workflow."""
    inventory = {"components": [], "total_lines": 0}
    skill_dir = config.workflow_path

    # SKILL.md
    _add_component(inventory, skill_dir / "SKILL.md", "skill", "Full portification protocol")

    # Command file
    for cmd_dir in [Path("src/superclaude/commands/"), Path(".claude/commands/sc/")]:
        for md in cmd_dir.glob(f"*{config.cli_name}*.md"):
            _add_component(inventory, md, "command", "CLI command definition")

    # Refs
    refs_dir = skill_dir / "refs"
    if refs_dir.is_dir():
        for ref in refs_dir.glob("*.md"):
            _add_component(inventory, ref, "ref", f"Reference: {ref.stem}")

    # Rules, templates, scripts
    for subdir, comp_type in [("rules", "rule"), ("templates", "template"), ("scripts", "script")]:
        sub = skill_dir / subdir
        if sub.is_dir():
            for f in sub.iterdir():
                if f.is_file():
                    _add_component(inventory, f, comp_type, f"{comp_type.title()}: {f.stem}")

    # Decisions
    decisions = skill_dir / "decisions.yaml"
    if decisions.exists():
        _add_component(inventory, decisions, "decisions", "Architectural decisions")

    # Agents (from skill frontmatter)
    agents_dir = Path("src/superclaude/agents/")
    # Agent resolution is best-effort; not all persona names map to agent files

    # Write inventory YAML
    output_path = config.work_dir / "component-inventory.yaml"
    _write_yaml(inventory, output_path)
    return inventory


def _add_component(inventory: dict, path: Path, comp_type: str, purpose: str):
    """Add a component to the inventory with line count."""
    if path.exists():
        lines = len(path.read_text().splitlines())
        inventory["components"].append({
            "path": str(path),
            "type": comp_type,
            "lines": lines,
            "purpose": purpose,
        })
        inventory["total_lines"] += lines
```

### Step 4 & 9: `emit_review_checkpoint()`

```python
def emit_review_checkpoint(step_id: str, artifact_path: Path, config: PortifyConfig) -> PortifyStepResult:
    """Emit review checkpoint and pause pipeline."""
    phase_num = "1" if step_id == "user-review-p1" else "2"
    approval_file = config.work_dir / f"phase{phase_num}-approval.yaml"

    approval = {
        "status": "pending",
        "artifact": str(artifact_path),
        "timestamp": time.time(),
        "phase": int(phase_num),
    }
    _write_yaml(approval, approval_file)

    return PortifyStepResult(
        step=None,
        status=PortifyStatus.AWAITING_REVIEW,
        started_at=time.time(),
        finished_at=time.time(),
        artifacts_produced=[str(approval_file)],
    )


def check_review_approval(step_id: str, config: PortifyConfig) -> bool:
    """Check if user has approved the review checkpoint."""
    phase_num = "1" if step_id == "user-review-p1" else "2"
    approval_file = config.work_dir / f"phase{phase_num}-approval.yaml"
    if not approval_file.exists():
        return False
    content = approval_file.read_text()
    return "status: approved" in content
```

## 6. Executor Design

### Sprint-Style Synchronous Supervisor

```python
def execute_cli_portify(config: PortifyConfig) -> PortifyResult:
    """Execute the cli-portify pipeline with supervised monitoring."""

    # Pre-flight
    if not shutil.which("claude"):
        print("Error: 'claude' binary not found in PATH", file=sys.stderr)
        sys.exit(1)

    # Infrastructure
    handler = SignalHandler()
    logger = PortifyLogger(config)
    tui = PortifyTUI(config)
    monitor = OutputMonitor()
    result = PortifyResult(config=config)
    ledger = TurnLedger(initial_budget=config.max_turns)

    handler.install()
    logger.write_header()
    tui.start()

    try:
        steps = _build_steps(config)

        # Dry-run exits after Phase 2 (step 9)
        if config.dry_run:
            steps = [s for s in steps if s.phase_type in (
                PortifyPhaseType.PREREQUISITES,
                PortifyPhaseType.ANALYSIS,
                PortifyPhaseType.USER_REVIEW,
                PortifyPhaseType.SPECIFICATION,
            )]

        for step in steps:
            if handler.shutdown_requested:
                result.outcome = PortifyOutcome.INTERRUPTED
                break

            # Resume support: skip completed steps
            if config.resume_from and not _reached_resume_point(step, config):
                continue

            # Route: programmatic vs Claude
            if step.is_programmatic:
                step_result = _run_programmatic_step(step, config)
            elif step.phase_type == PortifyPhaseType.USER_REVIEW:
                step_result = _run_review_gate(step, config, result)
                if step_result.status == PortifyStatus.AWAITING_REVIEW:
                    result.outcome = PortifyOutcome.AWAITING_REVIEW
                    result.step_results.append(step_result)
                    break
            else:
                # Budget check
                if not ledger.can_launch():
                    result.outcome = PortifyOutcome.HALTED
                    result.halt_step = step.id
                    break

                step_result = _run_claude_step(step, config, handler, monitor, tui, ledger)

            result.step_results.append(step_result)
            logger.write_step_result(step_result)

            # Failure handling
            if step_result.status not in (
                PortifyStatus.PASS, PortifyStatus.PASS_NO_SIGNAL,
                PortifyStatus.PASS_NO_REPORT, PortifyStatus.SKIPPED
            ):
                _collect_and_report_diagnostics(step_result, monitor, config)
                result.outcome = PortifyOutcome.HALTED
                result.halt_step = step.id
                break

        # Finalize
        if config.dry_run:
            result.outcome = PortifyOutcome.DRY_RUN
        result.finished_at = time.time()
        logger.write_summary(result)

    finally:
        tui.stop()
        monitor.stop()
        handler.uninstall()

    return result
```

### Step Builder

```python
PROGRAMMATIC_RUNNERS = {
    "input-validation": run_input_validation,
    "component-discovery": run_component_discovery,
}

REVIEW_STEPS = {"user-review-p1", "user-review-p2"}

def _build_steps(config: PortifyConfig) -> list[PortifyStep]:
    """Build the complete step graph."""
    return [
        PortifyStep(
            id="input-validation",
            prompt="",
            output_file=Path("portify-config.yaml"),
            gate=GATE_G000,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=30,
            phase_type=PortifyPhaseType.PREREQUISITES,
            is_programmatic=True,
        ),
        PortifyStep(
            id="component-discovery",
            prompt="",
            output_file=Path("component-inventory.yaml"),
            gate=GATE_G001,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=60,
            inputs=[Path("portify-config.yaml")],
            phase_type=PortifyPhaseType.PREREQUISITES,
            is_programmatic=True,
        ),
        PortifyStep(
            id="protocol-mapping",
            prompt=build_protocol_mapping_prompt(config),
            output_file=Path("protocol-map.md"),
            gate=GATE_G002,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=600,
            inputs=[Path("component-inventory.yaml")],
            phase_type=PortifyPhaseType.ANALYSIS,
        ),
        PortifyStep(
            id="analysis-synthesis",
            prompt=build_analysis_synthesis_prompt(config),
            output_file=Path("portify-analysis-report.md"),
            gate=GATE_G003,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=600,
            inputs=[Path("protocol-map.md"), Path("component-inventory.yaml")],
            phase_type=PortifyPhaseType.ANALYSIS,
        ),
        PortifyStep(
            id="user-review-p1",
            prompt="",
            output_file=Path("phase1-approval.yaml"),
            gate=GATE_G004,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=0,
            inputs=[Path("portify-analysis-report.md")],
            phase_type=PortifyPhaseType.USER_REVIEW,
            is_programmatic=True,
        ),
        PortifyStep(
            id="step-graph-design",
            prompt=build_step_graph_prompt(config),
            output_file=Path("step-graph-spec.md"),
            gate=GATE_G005,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=600,
            inputs=[Path("portify-analysis-report.md")],
            phase_type=PortifyPhaseType.SPECIFICATION,
        ),
        PortifyStep(
            id="models-gates-design",
            prompt=build_models_gates_prompt(config),
            output_file=Path("models-gates-spec.md"),
            gate=GATE_G006,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=600,
            inputs=[Path("step-graph-spec.md"), Path("portify-analysis-report.md")],
            phase_type=PortifyPhaseType.SPECIFICATION,
        ),
        PortifyStep(
            id="prompts-executor-design",
            prompt=build_prompts_executor_prompt(config),
            output_file=Path("prompts-executor-spec.md"),
            gate=GATE_G007,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=600,
            inputs=[Path("step-graph-spec.md"), Path("models-gates-spec.md")],
            phase_type=PortifyPhaseType.SPECIFICATION,
        ),
        PortifyStep(
            id="pipeline-spec-assembly",
            prompt=build_assembly_prompt(config),
            output_file=Path("portify-spec.md"),
            gate=GATE_G008,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=600,
            inputs=[
                Path("step-graph-spec.md"),
                Path("models-gates-spec.md"),
                Path("prompts-executor-spec.md"),
            ],
            phase_type=PortifyPhaseType.SPECIFICATION,
        ),
        PortifyStep(
            id="user-review-p2",
            prompt="",
            output_file=Path("phase2-approval.yaml"),
            gate=GATE_G009,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=0,
            inputs=[Path("portify-spec.md")],
            phase_type=PortifyPhaseType.USER_REVIEW,
            is_programmatic=True,
        ),
        PortifyStep(
            id="release-spec-synthesis",
            prompt=build_release_spec_prompt(config),
            output_file=Path("portify-release-spec.md"),
            gate=GATE_G010,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=900,
            inputs=[Path("portify-analysis-report.md"), Path("portify-spec.md")],
            phase_type=PortifyPhaseType.SYNTHESIS,
        ),
        PortifyStep(
            id="spec-panel-review",
            prompt=build_panel_review_prompt(config),
            output_file=Path("portify-release-spec.md"),
            gate=GATE_G011,
            gate_mode=GateMode.BLOCKING,
            timeout_seconds=1200,
            inputs=[Path("portify-release-spec.md")],
            phase_type=PortifyPhaseType.PANEL_REVIEW,
            convergence_max_iterations=3,
        ),
    ]
```

### Status Classification

```python
def _determine_status(exit_code: int | None, step: PortifyStep, config: PortifyConfig) -> PortifyStatus:
    """Classify step outcome from exit code and output artifacts."""
    if exit_code == 124:
        return PortifyStatus.TIMEOUT
    if exit_code and exit_code != 0:
        return PortifyStatus.ERROR

    result_path = config.work_dir / f"{step.id}-result.md"
    output_path = config.work_dir / step.output_file

    if result_path.exists():
        content = result_path.read_text()
        if "EXIT_RECOMMENDATION: HALT" in content:
            return PortifyStatus.HALT
        if "EXIT_RECOMMENDATION: CONTINUE" in content:
            return PortifyStatus.PASS
        return PortifyStatus.PASS_NO_SIGNAL

    if output_path.exists():
        if detect_error_max_turns(output_path):
            return PortifyStatus.INCOMPLETE
        return PortifyStatus.PASS_NO_REPORT

    return PortifyStatus.ERROR
```

## 7. Integration Plan

### File Generation Order (dependency chain)

1. `models.py` — No internal deps
2. `gates.py` — Imports from models
3. `prompts.py` — Imports from models
4. `config.py` — Imports from models
5. `inventory.py` — Imports from models, config
6. `monitor.py` — Imports from models
7. `process.py` — Imports from models, config; extends pipeline.process
8. `executor.py` — Imports from everything above
9. `tui.py` — Imports from models
10. `logging_.py` — Imports from models
11. `diagnostics.py` — Imports from models
12. `commands.py` — Imports from config, executor
13. `__init__.py` — Re-exports

### main.py Registration

```python
# Add to src/superclaude/cli/main.py
from superclaude.cli.cli_portify import cli_portify_group
main.add_command(cli_portify_group)
```

### Click Command Group

```python
@click.group("cli-portify")
def cli_portify_group():
    """Port inference-based workflows into programmatic CLI pipelines."""
    pass

@cli_portify_group.command("run")
@click.argument("workflow")
@click.option("--name", default=None, help="CLI subcommand name (kebab-case)")
@click.option("--output", default=None, help="Output directory for generated module")
@click.option("--max-turns", default=200, type=int, help="Max turns budget")
@click.option("--model", default="", help="Claude model to use")
@click.option("--dry-run", is_flag=True, help="Execute Phases 0-2 only")
@click.option("--resume", default=None, help="Resume from step ID")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def run(workflow, name, output, max_turns, model, dry_run, resume, debug):
    """Execute the portification pipeline."""
    config = validate_and_build_config(
        workflow=workflow, name=name, output=output,
        dry_run=dry_run, max_turns=max_turns, model=model,
    )
    if resume:
        config.resume_from = resume

    result = execute_cli_portify(config)

    # Emit return contract
    _emit_return_contract(result, config)

    sys.exit(0 if result.outcome.value in ("success", "dry_run") else 1)
```

## 8. Return Contract Emission

The executor emits the return contract (per SKILL.md schema) on every invocation:

```python
def _emit_return_contract(result: PortifyResult, config: PortifyConfig) -> dict:
    """Emit the return contract YAML per SKILL.md schema."""
    contract = {
        "contract_version": "2.0",
        "spec_file": str(config.work_dir / "portify-release-spec.md") if result.outcome == PortifyOutcome.SUCCESS else "",
        "panel_report": str(config.work_dir / "panel-report.md") if _has_panel_report(result) else "",
        "output_directory": str(config.work_dir),
        "quality_scores": result.quality_scores or {
            "clarity": 0.0, "completeness": 0.0, "testability": 0.0, "consistency": 0.0, "overall": 0.0,
        },
        "convergence_iterations": _get_convergence_iterations(result),
        "convergence_state": result.convergence_state.value,
        "phase_timing": result.phase_timing or {"phase_3_seconds": 0.0, "phase_4_seconds": 0.0},
        "source_step_count": _count_source_steps(result),
        "spec_fr_count": _count_frs(result),
        "api_snapshot_hash": _compute_spec_hash(result, config),
        "downstream_ready": result.downstream_ready,
        "phase_contracts": _build_phase_contracts(result),
        "warnings": result.warnings,
        "status": result.outcome.value,
        "failure_phase": _get_failure_phase(result),
        "failure_type": _get_failure_type(result),
        "resume_phase": _get_resume_phase(result),
        "resume_substep": _get_resume_substep(result),
        "resume_command": result.resume_command(),
    }

    contract_path = config.work_dir / "return-contract.yaml"
    _write_yaml(contract, contract_path)
    return contract
```
