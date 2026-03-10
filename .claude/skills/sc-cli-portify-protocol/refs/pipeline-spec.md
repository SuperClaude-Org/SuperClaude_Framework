# Pipeline Specification Reference

Loaded during Phase 2 of portification. This ref provides the detailed specification patterns for converting a workflow analysis into concrete code designs.

## Phase 2→3 Bridge

Phase 2 outputs (`portify-spec.md` and optional `portify-prompts.md`) flow into Phase 3 (Release Spec Synthesis), NOT into code generation. The bridge works as follows:

1. **Phase 2 produces**: Step graph, model designs, gate definitions, executor patterns, pure-programmatic implementations, and integration plan — all as specification documents.
2. **Phase 3 consumes**: Phase 2 outputs are mapped into a release specification template. Each Phase 2 step becomes a functional requirement (FR). Model designs populate the data models section. Gate definitions populate the gate criteria section.
3. **Phase 3→4 gate**: The synthesized spec must have zero remaining `{{SC_PLACEHOLDER:*}}` sentinels and a brainstorm gap analysis section before entering Phase 4 (Spec Panel Review).

Phase 2 does NOT produce runnable code. It produces code-ready specifications that inform the release spec, which is then reviewed by the panel in Phase 4 and ultimately consumed by `sc:roadmap` and `sc:tasklist` for implementation planning.

## Step Graph Design

### Step Definition Pattern

Every workflow operation that produces an artifact maps to a `Step`:

```python
Step(
    id="step-id",              # kebab-case, unique within pipeline
    prompt=build_X_prompt(),   # Function from prompts.py
    output_file="artifact.md", # Relative to work_dir
    gate=STEP_GATE,            # From gates.py
    gate_mode=GateMode.BLOCKING,  # BLOCKING (default) or TRAILING
    timeout_seconds=600,       # Per-step timeout
    inputs=["dep1.md"],        # Files this step reads
    retry_limit=1,             # How many retries on gate failure
    model=None,                # None = use default from config
)
```

### Gate Mode Selection

Choose `GateMode` based on step criticality:
- `BLOCKING` (default): Pipeline halts if gate fails. Use for steps whose output is consumed by downstream steps.
- `TRAILING`: Gate evaluates asynchronously; pipeline continues. Use for quality checks that don't affect downstream data flow.

Rule of thumb from `resolve_gate_mode()`:
- Release scope → always BLOCKING
- Milestone scope → configurable
- Task scope → TRAILING when `grace_period > 0`

### Parallel Group Pattern

Steps that can run concurrently are wrapped in a list:

```python
steps = [
    single_step_1,
    [parallel_step_a, parallel_step_b],  # Run concurrently
    single_step_2,                        # Waits for parallel group
]
```

The generic `execute_pipeline()` handles thread coordination. If using sprint-style custom executor, implement your own parallel dispatch.

### Dependency Rules

- Steps consume outputs of prior steps via `inputs` list
- A step can only reference outputs from steps that precede it in the graph
- Parallel steps within a group must not depend on each other
- Resume logic skips steps whose output already passes their gate

## Model Design Patterns

### Config Model

Always extend `PipelineConfig`:

```python
@dataclass
class MyConfig(PipelineConfig):
    """Pipeline-specific configuration."""
    # Required: identify the input
    source_path: Path

    # Optional: control behavior
    depth: str = "standard"       # quick|standard|deep

    # Computed paths
    @property
    def results_dir(self) -> Path:
        return self.work_dir / "results"

    @property
    def output_file(self, step_id: str) -> Path:
        return self.work_dir / f"{step_id}-output.md"
```

### Status Enum

Sprint-style pipelines need richer status than generic `StepStatus`:

```python
class StepPhaseStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"    # Completed but no structured report
    PASS_NO_REPORT = "pass_no_report"    # Output exists but no result file
    INCOMPLETE = "incomplete"             # Budget exhausted
    HALT = "halt"                         # Step recommends stopping
    TIMEOUT = "timeout"                   # Hard timeout exceeded
    ERROR = "error"                       # Process crash
    SKIPPED = "skipped"                   # Skipped by config
```

### Result Model

Extend `StepResult` with domain telemetry:

```python
@dataclass
class MyStepResult(StepResult):
    exit_code: int | None = None
    started_at: float | None = None
    finished_at: float | None = None
    output_bytes: int = 0
    error_bytes: int = 0
    # Domain-specific fields:
    artifacts_produced: list[str] = field(default_factory=list)
    gate_details: dict = field(default_factory=dict)
```

### Monitor State

Domain-specific signals extracted from NDJSON output:

```python
@dataclass
class MyMonitorState:
    output_bytes: int = 0
    last_growth_time: float = 0.0
    events_received: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    # Domain-specific signals:
    last_step_id: str | None = None
    current_artifact: str | None = None
    files_changed: set = field(default_factory=set)
```

## Gate Design Patterns

### Gate Criteria Tiers

```python
# Exempt: always passes (for optional/informational steps)
EXEMPT_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="EXEMPT",
)

# Light: file exists and non-empty
LIGHT_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="LIGHT",
)

# Standard: structural validation
STANDARD_GATE = GateCriteria(
    required_frontmatter_fields=["title", "status"],
    min_lines=50,
    enforcement_tier="STANDARD",
)

# Strict: structural + semantic validation
STRICT_GATE = GateCriteria(
    required_frontmatter_fields=["title", "status", "convergence_score"],
    min_lines=100,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="no_heading_gaps",
            check_fn=_no_heading_gaps,
            failure_message="Heading hierarchy has gaps (e.g. H1→H3 without H2)",
        ),
        SemanticCheck(
            name="refs_resolve",
            check_fn=_cross_refs_resolve,
            failure_message="Cross-references do not resolve to valid targets",
        ),
    ],
)
```

### Semantic Check Functions

Semantic checks are pure functions matching the `Callable[[str], bool]` signature — they take file content and return a boolean:

```python
def _no_heading_gaps(content: str) -> bool:
    """Verify heading hierarchy has no gaps (H1->H3 without H2)."""
    # ... implementation ...
    return True  # or False on failure

def _has_required_sections(content: str) -> bool:
    """Verify all required sections are present."""
    required = {"## Summary", "## Findings", "## Recommendations"}
    present = {line.strip() for line in content.splitlines() if line.startswith("## ")}
    missing = required - present
    return len(missing) == 0
```

### Frontmatter Validation

The shared `gate_passed()` function handles YAML frontmatter checks. Steps that produce markdown with frontmatter get automatic validation:

```yaml
---
title: Diff Analysis
status: complete
diff_points: 12
convergence_ready: true
---
```

## Prompt Design Patterns

### Prompt Builder Structure

Each step's prompt is a function that takes inputs and returns a complete prompt string:

```python
def build_analysis_prompt(source_path: Path, config: MyConfig) -> str:
    return f"""Read the source file and produce a structured analysis.

Source: {source_path}
Depth: {config.depth}

## Required Output Format

Write your analysis to the output file with this structure:

```yaml
---
title: Analysis Report
status: complete
finding_count: <integer>
---
```

## Sections Required

### Summary
Brief overview of findings.

### Findings
Numbered list of findings with evidence.

### Recommendations
Actionable next steps.

## Machine-Readable Markers

At the end of your output, include:
```
EXIT_RECOMMENDATION: CONTINUE
```
or
```
EXIT_RECOMMENDATION: HALT
```
"""
```

### Key Prompt Rules

1. **Specify output file format** — Tell Claude exactly what frontmatter fields to include
2. **Require machine-readable markers** — `EXIT_RECOMMENDATION: CONTINUE|HALT` for status determination
3. **Embed input content when small** — Under ~50KB, embed directly in prompt; otherwise use `--file` args
4. **Be explicit about sections** — Name every required section; don't leave structure to inference
5. **Include depth/focus constraints** — If the step has configurable depth, encode it in the prompt

### Input Embedding Pattern

```python
def _embed_inputs(prompt: str, inputs: list[Path], config: MyConfig) -> tuple[str, list[str]]:
    """Embed small input files directly into prompt, return file args for large ones."""
    file_args = []
    for input_path in inputs:
        full_path = config.work_dir / input_path
        if full_path.stat().st_size < 50_000:
            content = full_path.read_text()
            prompt += f"\n\n---\n## Input: {input_path}\n\n{content}"
        else:
            file_args.append(str(full_path))
    return prompt, file_args
```

## Executor Design Patterns

### Sprint-Style Supervisor Loop

The sprint executor pattern provides supervised execution with monitoring. IMPORTANT: Sprint uses synchronous execution with `threading` for parallelism, NOT `async/await`. Use `time.sleep()` polling loops and `concurrent.futures.ThreadPoolExecutor` for batch dispatch.

```python
def execute_pipeline(config: MyConfig) -> MyResult:
    # 1. Pre-flight checks
    verify_claude_binary()

    # 2. Setup infrastructure
    signal_handler = SignalHandler()
    logger = MyLogger(config)
    tui = MyTUI(config)
    monitor = OutputMonitor()
    result = MyResult(config=config)
    ledger = TurnLedger(initial_budget=config.max_turns)

    # 3. Start TUI
    tui.start()

    try:
        for step in config.steps:
            if signal_handler.shutdown_requested:
                break

            # 4. Reset monitor for this step
            monitor.reset(config.output_file(step))
            monitor.start()

            # 5. Launch Claude subprocess
            process = ClaudeProcess(config, step)
            process.start()

            # 6. Supervision loop
            while process.is_running():
                if signal_handler.shutdown_requested:
                    process.stop()
                    break

                state = monitor.get_state()

                # Stall detection
                if state.stall_seconds > config.stall_timeout:
                    process.stop()
                    break

                # TUI update
                tui.update(step, state)
                time.sleep(0.5)

            # 7. Classify result
            monitor.stop()
            status = determine_status(process.exit_code, step, config)

            # 8. Record and decide
            step_result = build_result(step, status, monitor.state)
            result.add(step_result)
            logger.write_step_result(step_result)

            if status not in (PASS, PASS_NO_SIGNAL):
                # Collect diagnostics and halt
                diagnostics = collect_diagnostics(step_result, monitor.state)
                write_diagnostic_report(diagnostics, config)
                result.outcome = HALTED
                break

    finally:
        tui.stop()
        monitor.stop()
        signal_handler.restore()

    return result
```

### Status Classification

Map every possible exit condition to a deterministic status:

```python
def determine_status(exit_code, step, config):
    # 1. Hard failures
    if exit_code == 124:
        return TIMEOUT
    if exit_code != 0:
        return ERROR

    # 2. Check for structured result file
    result_path = config.result_file(step)
    if result_path.exists():
        content = result_path.read_text()
        if "EXIT_RECOMMENDATION: HALT" in content:
            return HALT
        if "EXIT_RECOMMENDATION: CONTINUE" in content:
            return PASS
        return PASS_NO_SIGNAL

    # 3. Check for output without result
    output_path = config.output_file(step)
    if output_path.exists():
        if detect_error_max_turns(output_path):
            return INCOMPLETE
        return PASS_NO_REPORT

    # 4. No output at all
    return ERROR
```

## Integration Patterns

### main.py Registration

```python
# In src/superclaude/cli/main.py
from superclaude.cli.my_pipeline import my_pipeline_group
app.add_command(my_pipeline_group)
```

### Click Command Group

```python
@click.group("my-pipeline")
def my_pipeline_group():
    """My pipeline description."""
    pass

@my_pipeline_group.command("run")
@click.argument("source")
@click.option("--depth", default="standard", type=click.Choice(["quick", "standard", "deep"]))
@click.option("--dry-run", is_flag=True)
@click.option("--max-turns", default=25, type=int)
@click.option("--model", default=None)
@click.option("--debug", is_flag=True)
def run(source, depth, dry_run, max_turns, model, debug):
    """Execute the pipeline."""
    config = load_config(source, depth=depth, dry_run=dry_run, ...)
    result = execute_pipeline(config)
    sys.exit(0 if result.success else 1)
```

## Turn Budget Economics (from unified-audit-gating)

For pipelines with multiple Claude subprocesses, use `TurnLedger` to manage budget:

```python
from superclaude.cli.sprint.models import TurnLedger

@dataclass
class MyConfig(PipelineConfig):
    max_turns: int = 200
    min_launch_allocation: int = 10
    min_remediation_budget: int = 5

# In executor:
ledger = TurnLedger(
    initial_budget=config.max_turns,
    minimum_allocation=config.min_launch_allocation,
    minimum_remediation_budget=config.min_remediation_budget,
)

# Before launching a step:
if not ledger.can_launch():
    result.outcome = HALTED
    result.halt_reason = "Budget exhausted"
    break

# After step completes, count actual turns used:
actual_turns = count_turns_from_output(output_path)
ledger.debit(actual_turns)

# If step used fewer turns than allocated, credit back:
if actual_turns < allocated:
    ledger.credit(allocated - actual_turns)
```

## Subprocess Isolation Pattern

For pipelines spawning child Claude sessions, use the 4-layer isolation model:

```python
def setup_isolation(work_dir: Path) -> dict[str, str]:
    """Create isolated environment for child Claude subprocess."""
    env = os.environ.copy()

    # Layer 1: Scoped work directory
    env["CLAUDE_WORK_DIR"] = str(work_dir)

    # Layer 2: Git ceiling (prevent escaping work_dir)
    env["GIT_CEILING_DIRECTORIES"] = str(work_dir.parent)

    # Layer 3: Isolated plugin directory
    plugin_dir = work_dir / ".claude-plugins"
    plugin_dir.mkdir(exist_ok=True)
    env["CLAUDE_PLUGIN_DIR"] = str(plugin_dir)

    # Layer 4: Isolated settings
    settings_dir = work_dir / ".claude-settings"
    settings_dir.mkdir(exist_ok=True)
    env["CLAUDE_SETTINGS_DIR"] = str(settings_dir)

    return env
```

## Context Injection Pattern

Prior step results feed into subsequent prompts as compressed context:

```python
def build_step_prompt_with_context(step, prior_results: list[StepResult]) -> str:
    """Build prompt with prior step context injected."""
    base_prompt = step.prompt

    if not prior_results:
        return base_prompt

    context_block = "## Prior Step Context\n\n"
    for result in prior_results[-3:]:  # Keep recent, compress older
        context_block += result.to_context_summary(verbose=(result == prior_results[-1]))
        context_block += "\n\n"

    return f"{base_prompt}\n\n{context_block}"
```

## Resume-First Failure Output Pattern

On halt, generate actionable resume information:

```python
@dataclass
class MyResult:
    # ... other fields ...

    def resume_command(self) -> str | None:
        """Generate CLI command to resume from failure point."""
        if not self.halt_step:
            return None
        remaining = [r.step.id for r in self.step_results
                     if r.status == MyStatus.PENDING]
        return (
            f"superclaude {CLI_NAME} run "
            f"--resume --start {self.halt_step} "
            f"--max-turns {self.suggested_resume_budget}"
        )

    @property
    def suggested_resume_budget(self) -> int:
        """Estimate turns needed to complete remaining work."""
        remaining_steps = sum(1 for r in self.step_results
                              if r.status in (MyStatus.PENDING, MyStatus.INCOMPLETE))
        return remaining_steps * 25  # Default allocation per step
```

## Pure-Programmatic Step Execution

Not all steps need Claude. Pure-programmatic steps run as direct Python function calls:

```python
def execute_step(step, config):
    """Route step to appropriate executor."""
    if step.prompt == "":
        # Pure programmatic — run directly
        return run_programmatic_step(step, config)
    else:
        # Claude-assisted — launch subprocess
        return run_claude_step(step, config)

def run_programmatic_step(step, config) -> StepResult:
    """Execute a pure-programmatic step without Claude."""
    started = time.time()
    try:
        # Call the step's implementation function
        PROGRAMMATIC_RUNNERS[step.id](config)
        return StepResult(step=step, status=StepStatus.PASS,
                         started_at=started, finished_at=time.time())
    except Exception as e:
        return StepResult(step=step, status=StepStatus.FAIL,
                         gate_failure_reason=str(e),
                         started_at=started, finished_at=time.time())
```

## Gate Display State Machine (for TUI)

Model gate states as explicit transitions for richer UX:

```python
class GateDisplayState(Enum):
    NONE = "none"
    CHECKING = "checking"
    PASS = "pass"
    FAIL_DEFERRED = "fail_deferred"
    REMEDIATING = "remediating"
    REMEDIATED = "remediated"
    HALT = "halt"

    @property
    def icon(self) -> str:
        return {
            "none": " ", "checking": "...",
            "pass": "ok", "fail_deferred": "!",
            "remediating": "~", "remediated": "ok",
            "halt": "X",
        }[self.value]
```
