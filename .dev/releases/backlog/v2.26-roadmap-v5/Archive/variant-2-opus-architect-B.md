---
title: "v2.25 Roadmap v5 Spec -- Variant B: Structural Refactor with LoopStep"
version: "2.25.0-B"
status: draft
scope: single-phase
design_philosophy: structural_refactor
replaces_steps: ["spec-fidelity"]
new_primitives: ["LoopStep"]
new_steps: ["classify-and-validate"]
modified_steps: ["remediate", "certify"]
modified_models: ["Finding", "Step (via LoopStep)"]
affected_files: 8
estimated_loc: 450
---

# v2.25 Roadmap v5 Specification -- Variant B

## Structural Refactor: Unified Classify-and-Validate with LoopStep Primitive

---

## 1. Problem Statement

### 1.1 Triggering Incident

The v2.24-cli-portify-cli-v4 roadmap pipeline failed at the `spec-fidelity`
gate after 2 attempts (retry_limit=1, meaning 2 total runs). The gate enforces
`high_severity_count == 0` in the fidelity report frontmatter. With 3 HIGH
severity deviations in the report, the gate blocked and the pipeline halted.

**Pipeline state at failure**:
- Completed (PASS): `generate-opus-architect`, `generate-haiku-architect`,
  `diff`, `debate`, `score`, `merge`, `test-strategy`
- Failed (attempt 2/2): `spec-fidelity`
- Never reached: `remediate`, `certify`
- Skipped: `extract` (resume from prior run)

### 1.2 Fidelity Report: The 3 HIGH Deviations

| ID | Deviation | True Classification |
|----|-----------|---------------------|
| DEV-001 | File structure mismatch: `steps/` subdirectory with renamed modules | MIXED: `steps/` layout was debate-resolved (D-02, R2); module renames were SLIPs |
| DEV-002 | Missing data models: 3 of 6 spec-defined models absent | SLIP: never discussed in debate |
| DEV-003 | Missing semantic check implementations: 8 functions referenced abstractly | SLIP: never discussed in debate |

### 1.3 Root Cause Analysis

Six systemic failures caused the pipeline halt:

1. **Information loss in extraction**: The extraction step loses module names,
   data model definitions, and function signatures. Generate agents work from
   the extraction, not the spec, so they never see what they are dropping.

2. **No spec context in debate**: Debate agents receive the diff and two
   variants but never the original spec. They cannot flag spec departures.

3. **No deviation annotation at merge**: The merge agent produces `roadmap.md`
   with no companion metadata marking where the output departs from the spec.

4. **Fidelity agent works from scratch**: Must rediscover all context by
   re-reading debate artifacts to understand which deviations were intentional
   versus accidental. This is unreliable.

5. **Retry is futile**: Same prompt + same inputs = same output. The retry
   mechanism reruns spec-fidelity against the unchanged roadmap, producing the
   identical failure.

6. **No remediation path for classified deviations**: Even when deviations are
   correctly identified, there is no automated flow to distinguish "fix this
   SLIP in the roadmap" from "this intentional deviation is acceptable."

### 1.4 Why the Current Architecture Cannot Self-Heal

The v4 pipeline treats spec-fidelity as a terminal quality gate. When
deviations exist -- even intentional ones resolved during debate -- the gate
blocks unconditionally. There is no classification layer, no remediation loop,
and no distinction between intentional design decisions and generation errors.

The pipeline can only succeed if the generation phase produces zero deviations
from the spec, which is architecturally infeasible given that the debate step
is explicitly designed to improve upon the spec where appropriate.

---

## 2. Design Philosophy: Variant B -- Structural Refactor

This variant proposes a structural refactor rather than an incremental addition
of steps. The core changes are:

1. **Replace `spec-fidelity` with `classify-and-validate`**: A single unified
   step that combines deviation annotation, fidelity checking, and deviation
   classification into one pass. This eliminates the three-step pipeline
   (annotate -> fidelity -> classify) proposed in the brainstorm's two-scope
   architecture, collapsing them into a single, more efficient step.

2. **Add `LoopStep` primitive to the pipeline executor**: A new executor
   primitive that wraps a body of steps in a bounded retry loop with an exit
   condition derived from gate evaluation. This enables the remediate-certify
   cycle without requiring `--resume` invocations.

3. **Inline certify as post-remediation re-check**: Rather than a separate
   pipeline step, certify becomes the exit condition of the remediate loop.
   If the loop body (remediate) produces output that passes certification
   checks, the loop exits. Otherwise it retries up to `max_iterations`.

4. **Deviation-to-Finding conversion built into the unified step**: The
   `classify-and-validate` step output includes structured Finding objects
   directly, eliminating a separate conversion function.

5. **Single-phase implementation**: No Scope 1 / Scope 2 sequencing. All
   changes land in one release.

### 2.1 Pipeline Comparison

**v4 (current)**:
```
extract -> [gen-A, gen-B] -> diff -> debate -> score -> merge
  -> test-strategy -> spec-fidelity(STRICT, blocks on HIGH>0)
  -> remediate -> certify
```

**v5-B (proposed)**:
```
extract -> [gen-A, gen-B] -> diff -> debate -> score -> merge
  -> test-strategy -> classify-and-validate(STRICT, blocks on AMBIGUOUS>0)
  -> LoopStep(body=[remediate], exit=certify_gate, max_iterations=2)
```

### 2.2 Key Architectural Difference from Variant A

Variant A (incremental) adds two new steps (`annotate-deviations`,
`deviation-analysis`) between existing steps, preserving `spec-fidelity` in
downgraded form. This creates a 12-step pipeline.

Variant B (this spec) replaces `spec-fidelity` entirely with a single unified
step that does annotation + fidelity + classification in one LLM invocation.
It then adds a `LoopStep` primitive to the executor, enabling the
remediate-certify cycle to be expressed declaratively rather than through
manual `--resume` invocations. The result is a 10-step pipeline (with the
loop counting as one composite step).

---

## 3. v5-B Pipeline Flow

```
                    +--------------------------------------------------+
                    |           GENERATION PHASE (unchanged)            |
                    +--------------------------------------------------+
                    |  extract --+-- gen-A (opus)  --+                  |
                    |            +-- gen-B (haiku) --+                  |
                    |                    |                              |
                    |               diff-analysis                      |
                    |                    |                              |
                    |                 debate                            |
                    |                    |                              |
                    |                  score                            |
                    |                    |                              |
                    |                  merge ----------> roadmap.md     |
                    +--------------------+-----------------------------+
                                         |
                    +--------------------v-----------------------------+
                    |           VALIDATION PHASE (modified)            |
                    +--------------------------------------------------+
                    |  test-strategy (unchanged)                        |
                    |                    |                              |
                    |  classify-and-validate (NEW, replaces fidelity)   |
                    |    reads: spec + roadmap + debate + diff          |
                    |    produces: classify-and-validate.md             |
                    |    gate: STRICT (no AMBIGUOUS deviations)         |
                    |    output: deviation table + Finding objects      |
                    +--------------------+-----------------------------+
                                         |
                    +--------------------v-----------------------------+
                    |     REMEDIATION PHASE (LoopStep primitive)       |
                    +--------------------------------------------------+
                    |  LoopStep(max_iterations=2):                      |
                    |    |                                              |
                    |    +-- remediate (body step)                      |
                    |    |     reads: classify-and-validate.md          |
                    |    |     fixes SLIPs in roadmap.md                |
                    |    |     produces: remediation-tasklist.md        |
                    |    |                                              |
                    |    +-- [inline certify gate evaluation]           |
                    |          reads: roadmap.md + remediation-tasklist |
                    |          exit condition: certified == true        |
                    |          |                                        |
                    |          +-- PASS -> exit loop, pipeline done     |
                    |          +-- FAIL -> retry body (if iterations    |
                    |                      remain), else HALT           |
                    +--------------------------------------------------+
```

---

## 4. The `classify-and-validate` Unified Step

### 4.1 Purpose

This step replaces the three-step sequence proposed in the brainstorm
(annotate-deviations -> spec-fidelity -> deviation-analysis) with a single
LLM invocation that performs all three functions:

1. **Annotation**: For each deviation found, search the debate transcript for
   discussion citations. Classify as `INTENTIONAL` (with citation) or
   `NOT_DISCUSSED`.

2. **Fidelity check**: Compare the merged roadmap against the original spec,
   identifying structural deviations in modules, data models, function
   signatures, and architectural decisions.

3. **Classification**: Assign each deviation a final class:
   - `INTENTIONAL`: Debated and resolved with consensus. No fix needed.
   - `SLIP`: Not discussed in debate. Must be fixed by remediate.
   - `AMBIGUOUS`: Partially discussed, no clear consensus. Blocks pipeline.

4. **Finding generation**: For each `SLIP` deviation, produce a structured
   Finding object (in the output format) that the remediate step can consume
   directly.

### 4.2 Step Definition

| Property | Value |
|----------|-------|
| Step ID | `classify-and-validate` |
| Position | After `test-strategy`, before `LoopStep` |
| Inputs | `spec_file`, `roadmap.md`, `debate-transcript.md`, `diff-analysis.md` |
| Output | `classify-and-validate.md` |
| Gate | `CLASSIFY_AND_VALIDATE_GATE` -- STRICT tier |
| Timeout | 600s |
| Retry | 1 |

### 4.3 Prompt Design: `build_classify_and_validate_prompt()`

**New function in `src/superclaude/cli/roadmap/prompts.py`**.

The prompt instructs a fresh Claude subprocess to:

1. Read the spec file in full (not the extraction -- avoids information loss).
2. Read the merged roadmap (`roadmap.md`).
3. Read the debate transcript (`debate-transcript.md`).
4. Read the diff analysis (`diff-analysis.md`).
5. For every element in the spec (modules, data models, functions, gates,
   architectural decisions), check whether the roadmap faithfully represents it.
6. For each deviation found:
   a. Search the debate transcript for explicit discussion (cite D-XX, round).
   b. If discussed with consensus: classify as `INTENTIONAL`.
   c. If not discussed at all: classify as `SLIP`.
   d. If partially discussed without resolution: classify as `AMBIGUOUS`.
7. For each `SLIP`, produce a structured Finding block with:
   - `id`: `DEV-NNN`
   - `severity`: `BLOCKING` (was HIGH) or `WARNING` (was MEDIUM)
   - `dimension`: `spec-fidelity`
   - `description`: What the spec requires vs. what the roadmap has
   - `location`: Section/module in roadmap.md
   - `evidence`: Spec reference and roadmap reference
   - `fix_guidance`: Specific instructions for remediation
   - `deviation_class`: `SLIP`
8. Produce YAML frontmatter with counts and routing metadata.

**Prompt skeleton** (abbreviated):

```
You are a spec-fidelity analyst. You have four input documents:
1. The SPECIFICATION (ground truth)
2. The MERGED ROADMAP (output being validated)
3. The DEBATE TRANSCRIPT (records of design decisions)
4. The DIFF ANALYSIS (structural differences between variants)

## Task

For every element in the specification, verify it appears in the roadmap.
For every deviation, classify it using the debate transcript.

## Classification Rules

- INTENTIONAL: The debate transcript explicitly discusses this deviation
  with a consensus decision. You MUST cite the specific D-XX identifier
  and round number. Without a valid citation, you cannot classify as
  INTENTIONAL.
- SLIP: The deviation is not discussed anywhere in the debate transcript.
  This is a generation error that must be fixed.
- AMBIGUOUS: The deviation is partially discussed but no clear consensus
  was reached. This blocks the pipeline for human review.

## Anti-Laundering Rules

1. Every INTENTIONAL classification MUST include a direct quote from the
   debate transcript proving the decision was made.
2. "Implied" or "consistent with the spirit of" is NOT sufficient for
   INTENTIONAL. The deviation must be explicitly discussed.
3. If you are uncertain, classify as AMBIGUOUS. Never default to INTENTIONAL.

## Output Format

YAML frontmatter followed by structured markdown body.
```

### 4.4 Output Format: `classify-and-validate.md`

```yaml
---
total_deviations: 5
intentional_count: 2
slip_count: 2
ambiguous_count: 1
high_severity_slips: 2
medium_severity_slips: 0
low_severity_slips: 0
validation_complete: true
findings_generated: 2
---
```

Body contains three sections:

**Section 1: Deviation Table**

| ID | Spec Element | Deviation | Debate Ref | Round | Class | Severity |
|----|-------------|-----------|------------|-------|-------|----------|
| DEV-001 | steps/ layout | Subdirectory added | D-02 | R2 | INTENTIONAL | -- |
| DEV-002 | PortifyStatus model | Missing from roadmap | -- | -- | SLIP | HIGH |
| DEV-003 | _all_gates_defined() | Not implemented | -- | -- | SLIP | HIGH |
| DEV-004 | executor.py module | Explicit module | D-04 | R2 | INTENTIONAL | -- |
| DEV-005 | cli.py rename | Partial discussion | D-02? | R2 | AMBIGUOUS | MEDIUM |

**Section 2: Evidence per Deviation**

Per-deviation evidence blocks with debate quotes, spec references, and
architectural assessment.

**Section 3: Generated Findings (for SLIPs)**

```markdown
## Generated Findings

### F-001 (DEV-002)
- **severity**: BLOCKING
- **dimension**: spec-fidelity
- **description**: Spec requires PortifyStatus, PortifyOutcome, PortifyStepResult
  models. Roadmap defines only 3 of 6 required models.
- **location**: roadmap.md Section 4.2
- **evidence**: Spec Section 3.1 defines 6 models; roadmap Section 4.2 has 3
- **fix_guidance**: Add missing PortifyStatus, PortifyOutcome, PortifyStepResult
  model definitions to Section 4.2 of the roadmap.
- **deviation_class**: SLIP
- **files_affected**: ["roadmap.md"]
```

### 4.5 Gate Definition

```python
def _no_ambiguous_deviations(content: str) -> bool:
    """Validate that ambiguous_count equals zero.

    Returns True only if frontmatter contains ambiguous_count with
    integer value 0. AMBIGUOUS deviations block the pipeline because
    they require human review before remediation can proceed.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    value = fm.get("ambiguous_count")
    if value is None:
        return False

    try:
        count = int(value)
    except (ValueError, TypeError):
        return False

    return count == 0


def _validation_complete_true(content: str) -> bool:
    """Validate that validation_complete is true."""
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    value = fm.get("validation_complete")
    if value is None:
        return False

    return value.lower() == "true"


CLASSIFY_AND_VALIDATE_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_deviations",
        "intentional_count",
        "slip_count",
        "ambiguous_count",
        "validation_complete",
        "findings_generated",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="no_ambiguous_deviations",
            check_fn=_no_ambiguous_deviations,
            failure_message=(
                "All deviations must be classified as INTENTIONAL or SLIP. "
                "AMBIGUOUS deviations require human review."
            ),
        ),
        SemanticCheck(
            name="validation_complete_true",
            check_fn=_validation_complete_true,
            failure_message="validation_complete must be true",
        ),
    ],
)
```

**Critical design decision**: The gate blocks on **unresolved ambiguity**,
NOT on SLIP count. SLIPs are expected -- they flow into the remediate loop.
Blocking on SLIP count would prevent remediation from ever running, which
was the exact v4 failure mode.

### 4.6 Anti-Laundering Safeguards

1. **Separate subprocess**: The classify-and-validate step runs as a fresh
   Claude process with no shared state from generation or merge agents.

2. **Citation requirement**: Every `INTENTIONAL` classification must cite
   a specific D-XX identifier and round number with quoted text.

3. **Strict classification hierarchy**: Only explicit debate consensus
   qualifies as INTENTIONAL. "Spirit of the discussion" does not count.

4. **AMBIGUOUS as safety valve**: If the LLM cannot definitively classify
   a deviation, AMBIGUOUS blocks the pipeline for human review rather than
   silently approving a false INTENTIONAL.

---

## 5. The `LoopStep` Primitive

### 5.1 Motivation

The current pipeline executor (`src/superclaude/cli/pipeline/executor.py`)
processes `list[Step | list[Step]]` -- sequential steps or parallel groups.
There is no mechanism for bounded iteration.

The remediate-certify cycle requires exactly this: run remediate, check if
the fixes pass certification, and if not, retry remediate with feedback
about what failed. Without a loop primitive, this requires manual
`--resume` invocations, which is the same futile-retry problem that caused
the v2.24 failure.

### 5.2 Data Model

```python
@dataclass
class LoopStep:
    """A bounded iteration primitive for the pipeline executor.

    Wraps a sequence of body steps in a retry loop. After each iteration,
    the exit_gate is evaluated against exit_output_file. If the gate passes,
    the loop exits successfully. If it fails and iterations remain, the body
    runs again. If max_iterations is exhausted, the loop halts with FAIL.

    Attributes:
        id: Unique identifier for the loop (e.g., "remediate-certify-loop").
        body: Ordered list of steps to execute per iteration. Each step is
              a standard Step with its own gate (evaluated normally).
        exit_gate: GateCriteria evaluated after all body steps complete.
              This is the "certification" check -- does the output meet
              the final quality bar?
        exit_output_file: Path to the file evaluated by exit_gate.
        max_iterations: Upper bound on loop iterations. Default 2.
              Safety bound to prevent infinite loops.
        exit_prompt: Optional prompt for generating the exit gate's input
              file. If provided, a Claude subprocess runs this prompt and
              writes to exit_output_file before gate evaluation.
        exit_timeout_seconds: Timeout for the exit prompt subprocess.
    """

    id: str
    body: list[Step]
    exit_gate: GateCriteria
    exit_output_file: Path
    max_iterations: int = 2
    exit_prompt: str = ""
    exit_timeout_seconds: int = 300
```

**Design decision**: `LoopStep` is a separate dataclass, NOT a subclass of
`Step`. This preserves the `Step` contract (single execution unit) while
giving the executor a new compound type to dispatch on. The `execute_pipeline`
type signature changes from `list[Step | list[Step]]` to
`list[Step | list[Step] | LoopStep]`.

### 5.3 Executor Integration

The `execute_pipeline()` function in `src/superclaude/cli/pipeline/executor.py`
gains a new dispatch branch for `LoopStep`:

```python
def execute_pipeline(
    steps: list[Step | list[Step] | LoopStep],
    config: PipelineConfig,
    run_step: StepRunner,
    on_step_start: Callable[[Step], None] = lambda s: None,
    on_step_complete: Callable[[Step, StepResult], None] = lambda s, r: None,
    on_state_update: Callable[[dict], None] = lambda state: None,
    cancel_check: Callable[[], bool] = lambda: False,
    trailing_runner: TrailingGateRunner | None = None,
) -> list[StepResult]:
    """Generic pipeline executor.

    Processes steps in order. Each element in ``steps`` is either:
    - A single Step (executed sequentially)
    - A list[Step] (all steps in the list executed in parallel)
    - A LoopStep (bounded iteration over body steps)
    """
    all_results: list[StepResult] = []
    # ... existing setup ...

    for entry in steps:
        if cancel_check():
            break

        if isinstance(entry, LoopStep):
            # Bounded iteration
            loop_results = _execute_loop_step(
                entry, config, run_step, cancel_check,
                on_step_start, on_step_complete,
                trailing_runner=_trailing,
            )
            all_results.extend(loop_results)
            on_state_update(_build_state(all_results))

            # If loop did not exit successfully, halt
            if loop_results and loop_results[-1].status != StepStatus.PASS:
                break

        elif isinstance(entry, list):
            # ... existing parallel group logic ...
        else:
            # ... existing sequential step logic ...

    # ... existing trailing gate sync ...
    return all_results
```

### 5.4 Loop Execution Logic

```python
def _execute_loop_step(
    loop: LoopStep,
    config: PipelineConfig,
    run_step: StepRunner,
    cancel_check: Callable[[], bool],
    on_step_start: Callable[[Step], None] = lambda s: None,
    on_step_complete: Callable[[Step, StepResult], None] = lambda s, r: None,
    trailing_runner: TrailingGateRunner | None = None,
) -> list[StepResult]:
    """Execute a bounded loop: body steps -> exit gate -> repeat or exit.

    For each iteration (1..max_iterations):
    1. Execute all body steps sequentially. If any body step fails, halt.
    2. If exit_prompt is set, run a subprocess to produce exit_output_file.
    3. Evaluate exit_gate against exit_output_file.
    4. If gate passes: return all results with final PASS.
    5. If gate fails and iterations remain: log, continue to next iteration.
    6. If gate fails and max_iterations exhausted: return with FAIL.

    Each iteration's body step IDs are suffixed with the iteration number
    for state tracking: "remediate" -> "remediate.1", "remediate.2".
    """
    all_results: list[StepResult] = []

    for iteration in range(1, loop.max_iterations + 1):
        if cancel_check():
            break

        _log.info(
            "Loop '%s': iteration %d/%d",
            loop.id, iteration, loop.max_iterations,
        )

        # Execute body steps
        body_failed = False
        for body_step in loop.body:
            # Create iteration-scoped step ID
            iter_step = Step(
                id=f"{body_step.id}.{iteration}",
                prompt=body_step.prompt,
                output_file=body_step.output_file,
                gate=body_step.gate,
                timeout_seconds=body_step.timeout_seconds,
                inputs=body_step.inputs,
                retry_limit=body_step.retry_limit,
                model=body_step.model,
                gate_mode=body_step.gate_mode,
            )

            result = _execute_single_step(
                iter_step, config, run_step, cancel_check,
                on_step_start, on_step_complete,
                trailing_runner=trailing_runner,
            )
            all_results.append(result)

            if result.status != StepStatus.PASS:
                body_failed = True
                break

        if body_failed:
            break

        # Run exit prompt if provided (inline certify)
        if loop.exit_prompt:
            certify_step = Step(
                id=f"{loop.id}.certify.{iteration}",
                prompt=loop.exit_prompt,
                output_file=loop.exit_output_file,
                gate=None,  # Gate checked manually below
                timeout_seconds=loop.exit_timeout_seconds,
                inputs=[s.output_file for s in loop.body],
            )
            on_step_start(certify_step)
            certify_result = run_step(certify_step, config, cancel_check)
            all_results.append(certify_result)
            on_step_complete(certify_step, certify_result)

            if certify_result.status != StepStatus.PASS:
                break

        # Evaluate exit gate
        passed, reason = gate_passed(loop.exit_output_file, loop.exit_gate)
        if passed:
            _log.info("Loop '%s': exit gate passed on iteration %d", loop.id, iteration)
            # Create a synthetic PASS result for the loop
            now = datetime.now(timezone.utc)
            all_results.append(StepResult(
                step=Step(
                    id=loop.id,
                    prompt="",
                    output_file=loop.exit_output_file,
                    gate=loop.exit_gate,
                    timeout_seconds=0,
                ),
                status=StepStatus.PASS,
                attempt=iteration,
                started_at=now,
                finished_at=now,
            ))
            return all_results

        # Gate failed
        _log.info(
            "Loop '%s': exit gate failed on iteration %d/%d: %s",
            loop.id, iteration, loop.max_iterations, reason,
        )

        if iteration == loop.max_iterations:
            # Exhausted iterations -- terminal failure
            now = datetime.now(timezone.utc)
            all_results.append(StepResult(
                step=Step(
                    id=loop.id,
                    prompt="",
                    output_file=loop.exit_output_file,
                    gate=loop.exit_gate,
                    timeout_seconds=0,
                ),
                status=StepStatus.FAIL,
                attempt=iteration,
                gate_failure_reason=(
                    f"Loop '{loop.id}' exhausted {loop.max_iterations} iterations. "
                    f"Last gate failure: {reason}"
                ),
                started_at=now,
                finished_at=now,
            ))

    return all_results
```

### 5.5 Interaction with Resume

The `_apply_resume()` function in `src/superclaude/cli/roadmap/executor.py`
must handle `LoopStep` entries. The resume logic checks whether the loop's
`exit_output_file` passes `exit_gate`. If it does, the entire loop is skipped.
If not, the loop runs from scratch (iteration 1).

```python
# In _apply_resume(), add LoopStep handling:
elif isinstance(entry, LoopStep):
    if entry.exit_gate:
        passed, _reason = gate_fn(entry.exit_output_file, entry.exit_gate)
        if passed:
            skipped += 1
            print(f"[roadmap] Skipping loop {entry.id} (exit gate passes)")
            continue
    found_failure = True
    result.append(entry)
```

### 5.6 State Tracking

Each loop iteration produces step results with iteration-scoped IDs
(e.g., `remediate.1`, `remediate-certify-loop.certify.1`). The state file
records all iterations, enabling post-hoc analysis of convergence behavior.

The loop's synthetic result uses the `loop.id` as step ID, providing a
single entry point for resume logic.

---

## 6. Inline Certify as Post-Remediation Re-Check

### 6.1 Concept

Rather than certify being a standalone pipeline step, it becomes the exit
condition of the remediate loop. The `LoopStep` runs a certify prompt after
each remediate iteration and evaluates the certify gate to determine whether
to exit or retry.

### 6.2 Certify Gate Fix (Pre-existing Bug)

The current `CERTIFY_GATE` lacks a `_certified_is_true` semantic check.
This is a known gap (see brainstorm reference Section 6.1, Gap 1). This
spec requires fixing it:

```python
def _certified_is_true(content: str) -> bool:
    """Validate that certified field is true in certification report.

    Returns True only if frontmatter contains certified with value 'true'.
    A certification report with certified=false or certified missing MUST
    fail the gate, even if all other structural checks pass.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    value = fm.get("certified")
    if value is None:
        return False

    return value.lower() == "true"


# Updated CERTIFY_GATE:
CERTIFY_GATE = GateCriteria(
    required_frontmatter_fields=[
        "findings_verified",
        "findings_passed",
        "findings_failed",
        "certified",
        "certification_date",
    ],
    min_lines=15,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="One or more required frontmatter fields have empty values",
        ),
        SemanticCheck(
            name="per_finding_table_present",
            check_fn=_has_per_finding_table,
            failure_message="Certification report missing per-finding results table",
        ),
        SemanticCheck(
            name="certified_true",
            check_fn=_certified_is_true,
            failure_message="Certification failed -- not all findings verified as FIXED",
        ),
    ],
)
```

### 6.3 Certify Prompt Modification

The certification prompt receives SLIP findings from the
`classify-and-validate.md` output. For each SLIP:

1. Check that `roadmap.md` now contains the missing element.
2. Verify the fix matches the spec (not just "something changed").
3. Produce per-finding PASS/FAIL with justification.
4. Set `certified: true` only if ALL SLIP fixes verified.

### 6.4 Terminal Halt with Manual-Fix Instructions

When the loop exhausts `max_iterations` (default 2), the pipeline halts
with specific guidance:

```
ERROR: Remediation loop exhausted 2 iterations for loop 'remediate-certify-loop'
  Last gate failure: certified must be true

  Unfixed findings:
    DEV-003: _all_gates_defined() still missing from Phase 2 gate deliverables

  Manual intervention required:
    1. Edit roadmap.md to fix the unfixed findings
    2. Run: superclaude roadmap run <spec-file> --resume
```

This addresses brainstorm Gap 4 (no terminal state with manual-fix
instructions).

---

## 7. `Finding.deviation_class` Field Addition

### 7.1 Model Change

The `Finding` dataclass in `src/superclaude/cli/roadmap/models.py` gains
a new field:

```python
VALID_DEVIATION_CLASSES = frozenset({
    "SLIP", "INTENTIONAL", "AMBIGUOUS", "UNCLASSIFIED",
})

VALID_FINDING_STATUSES = frozenset({"PENDING", "FIXED", "FAILED", "SKIPPED"})


@dataclass
class Finding:
    """A single validation finding extracted from a report.

    Fields align with spec 2.3.1. Status lifecycle defined in D-0003:
    PENDING -> FIXED | FAILED | SKIPPED (all terminal).

    The deviation_class field (v2.25) indicates the origin classification:
    - SLIP: Generation error, not discussed in debate. Must be fixed.
    - INTENTIONAL: Debate-resolved design decision. No fix needed.
    - AMBIGUOUS: Partially discussed, no consensus. Blocks pipeline.
    - UNCLASSIFIED: Legacy findings or findings from non-roadmap pipelines.
    """

    id: str
    severity: str
    dimension: str
    description: str
    location: str
    evidence: str
    fix_guidance: str
    files_affected: list[str] = field(default_factory=list)
    status: str = "PENDING"
    agreement_category: str = ""
    deviation_class: str = "UNCLASSIFIED"

    def __post_init__(self) -> None:
        if self.status not in VALID_FINDING_STATUSES:
            raise ValueError(
                f"Invalid Finding status {self.status!r}. "
                f"Must be one of: {', '.join(sorted(VALID_FINDING_STATUSES))}"
            )
        if self.deviation_class not in VALID_DEVIATION_CLASSES:
            raise ValueError(
                f"Invalid deviation_class {self.deviation_class!r}. "
                f"Must be one of: {', '.join(sorted(VALID_DEVIATION_CLASSES))}"
            )
```

### 7.2 Backward Compatibility

The default value `"UNCLASSIFIED"` ensures backward compatibility:
- Existing code that constructs `Finding` objects without `deviation_class`
  gets `"UNCLASSIFIED"` automatically.
- Non-roadmap pipelines (e.g., sprint) are unaffected.
- Existing serialized Findings (in tasklist files) that lack the field
  will deserialize with the default.

### 7.3 Remediate Integration

The remediate step uses `deviation_class` to filter its work:

- `SLIP`: Fix the roadmap to match the spec.
- `INTENTIONAL`: Skip -- no action needed.
- `AMBIGUOUS`: Should never reach remediate (blocked by classify-and-validate
  gate), but if encountered, treat as error.
- `UNCLASSIFIED`: Legacy behavior -- treat as actionable.

---

## 8. Deviation-to-Finding Conversion

### 8.1 Built into Unified Step Output

Unlike the brainstorm's proposal for a separate `deviations_to_findings()`
function, Variant B builds Finding generation directly into the
`classify-and-validate` prompt. The LLM produces Finding blocks as part
of its output, which are then parsed by the remediate step.

### 8.2 Severity Mapping

| Fidelity Severity | Finding Severity | Rationale |
|-------------------|-----------------|-----------|
| HIGH | BLOCKING | Must fix before pipeline can complete |
| MEDIUM | WARNING | Should fix, but non-blocking for certification |
| LOW | INFO | Cosmetic, not required for certification |

### 8.3 Parser Function

A parser function in `remediate.py` extracts Finding objects from the
classify-and-validate output:

```python
def parse_findings_from_classify_output(
    classify_output_path: Path,
) -> list[Finding]:
    """Parse Finding objects from classify-and-validate.md output.

    Extracts structured Finding blocks from the '## Generated Findings'
    section. Each Finding block has YAML-like key-value pairs.

    Only returns findings with deviation_class == 'SLIP'. INTENTIONAL
    deviations are not actionable and are excluded.
    """
    content = classify_output_path.read_text(encoding="utf-8")

    findings: list[Finding] = []
    # Parse the Generated Findings section
    # ... (implementation detail: regex or structured parsing)

    return [f for f in findings if f.deviation_class == "SLIP"]
```

---

## 9. Updated `_build_steps()` for v5-B

### 9.1 Step Builder Changes

```python
def _build_steps(config: RoadmapConfig) -> list[Step | list[Step] | LoopStep]:
    """Build the v5-B pipeline with classify-and-validate + remediate loop.

    Returns a list where each element is either:
    - A single Step (sequential)
    - A list[Step] (parallel group)
    - A LoopStep (bounded iteration)
    """
    out = config.output_dir
    agent_a = config.agents[0]
    agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]

    # Output paths
    extraction = out / "extraction.md"
    roadmap_a = out / f"roadmap-{agent_a.id}.md"
    roadmap_b = out / f"roadmap-{agent_b.id}.md"
    diff_file = out / "diff-analysis.md"
    debate_file = out / "debate-transcript.md"
    score_file = out / "base-selection.md"
    merge_file = out / "roadmap.md"
    test_strat = out / "test-strategy.md"
    classify_file = out / "classify-and-validate.md"
    tasklist_file = out / "remediation-tasklist.md"
    certify_file = out / "certification-report.md"

    steps: list[Step | list[Step] | LoopStep] = [
        # Steps 1-7: unchanged (extract through test-strategy)
        # ... (identical to current _build_steps) ...

        # Step 8: Classify-and-Validate (replaces spec-fidelity)
        Step(
            id="classify-and-validate",
            prompt=build_classify_and_validate_prompt(
                config.spec_file, merge_file, debate_file, diff_file,
            ),
            output_file=classify_file,
            gate=CLASSIFY_AND_VALIDATE_GATE,
            timeout_seconds=600,
            inputs=[config.spec_file, merge_file, debate_file, diff_file],
            retry_limit=1,
        ),

        # Step 9: Remediate-Certify Loop
        LoopStep(
            id="remediate-certify-loop",
            body=[
                Step(
                    id="remediate",
                    prompt=build_remediate_prompt(classify_file, merge_file),
                    output_file=tasklist_file,
                    gate=REMEDIATE_GATE,
                    timeout_seconds=600,
                    inputs=[classify_file, merge_file],
                    retry_limit=1,
                ),
            ],
            exit_gate=CERTIFY_GATE,
            exit_output_file=certify_file,
            max_iterations=2,
            exit_prompt=build_certification_prompt_from_classify(
                classify_file, merge_file, tasklist_file,
            ),
            exit_timeout_seconds=300,
        ),
    ]

    return steps
```

### 9.2 Updated Step ID List

```python
def _get_all_step_ids(config: RoadmapConfig) -> list[str]:
    """Get all step IDs in pipeline order."""
    agent_a = config.agents[0]
    agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]
    return [
        "extract",
        f"generate-{agent_a.id}",
        f"generate-{agent_b.id}",
        "diff",
        "debate",
        "score",
        "merge",
        "test-strategy",
        "classify-and-validate",
        "remediate-certify-loop",
    ]
```

---

## 10. Implementation Plan (Single Phase)

All changes land in a single release. No Scope 1 / Scope 2 sequencing.

### 10.1 Deliverables

| # | Deliverable | File(s) | Est. LOC |
|---|------------|---------|----------|
| 1 | `LoopStep` dataclass | `src/superclaude/cli/pipeline/models.py` | 30 |
| 2 | `_execute_loop_step()` function | `src/superclaude/cli/pipeline/executor.py` | 90 |
| 3 | `execute_pipeline()` dispatch update | `src/superclaude/cli/pipeline/executor.py` | 15 |
| 4 | `build_classify_and_validate_prompt()` | `src/superclaude/cli/roadmap/prompts.py` | 60 |
| 5 | `CLASSIFY_AND_VALIDATE_GATE` + semantic checks | `src/superclaude/cli/roadmap/gates.py` | 50 |
| 6 | Remove `SPEC_FIDELITY_GATE` from pipeline | `src/superclaude/cli/roadmap/gates.py` | -5 |
| 7 | `_certified_is_true` semantic check | `src/superclaude/cli/roadmap/gates.py` | 15 |
| 8 | `Finding.deviation_class` field + validation | `src/superclaude/cli/roadmap/models.py` | 20 |
| 9 | Updated `_build_steps()` | `src/superclaude/cli/roadmap/executor.py` | 40 |
| 10 | Updated `_get_all_step_ids()` | `src/superclaude/cli/roadmap/executor.py` | 5 |
| 11 | `_apply_resume()` LoopStep handling | `src/superclaude/cli/roadmap/executor.py` | 15 |
| 12 | `parse_findings_from_classify_output()` | `src/superclaude/cli/roadmap/remediate.py` | 40 |
| 13 | Terminal halt formatting for loops | `src/superclaude/cli/roadmap/executor.py` | 25 |
| 14 | `build_certification_prompt_from_classify()` | `src/superclaude/cli/roadmap/certify_prompts.py` | 30 |
| 15 | Tests: LoopStep model | `tests/pipeline/test_models.py` | 25 |
| 16 | Tests: loop execution | `tests/pipeline/test_loop_executor.py` | 80 |
| 17 | Tests: classify-and-validate gate | `tests/roadmap/test_gates_data.py` | 30 |
| 18 | Tests: Finding.deviation_class | `tests/roadmap/test_models.py` | 15 |
| 19 | Tests: findings parser | `tests/roadmap/test_remediate.py` | 25 |
| 20 | Update `ALL_GATES` registry | `src/superclaude/cli/roadmap/gates.py` | 5 |
| | **Total** | | **~615** |

### 10.2 Implementation Order

The deliverables have the following dependency chain:

```
[1] LoopStep model ──────────────────────────┐
[2,3] Executor loop dispatch ────────────────┤
                                              ├── [9] _build_steps()
[4] classify-and-validate prompt ────────────┤
[5,6] Gate definitions ──────────────────────┤
[7] _certified_is_true ─────────────────────┤
[8] Finding.deviation_class ─────────────────┤
[12] Findings parser ────────────────────────┤
[14] Certify prompt update ──────────────────┘
                                              │
[10,11,13] Executor updates ─────────────────┘
[15-19] Tests (parallel, after code) ────────
[20] ALL_GATES registry cleanup ─────────────
```

Recommended implementation sequence:
1. Model changes first: `LoopStep`, `Finding.deviation_class` (deliverables 1, 8)
2. Executor changes: loop dispatch, loop execution (deliverables 2, 3)
3. Gate definitions and semantic checks (deliverables 5, 6, 7, 20)
4. Prompt builders (deliverables 4, 14)
5. Roadmap executor integration (deliverables 9, 10, 11, 12, 13)
6. Tests (deliverables 15-19)

---

## 11. Affected Files

### 11.1 Files Modified

| File | Changes |
|------|---------|
| `src/superclaude/cli/pipeline/models.py` | Add `LoopStep` dataclass |
| `src/superclaude/cli/pipeline/executor.py` | Add `_execute_loop_step()`, update `execute_pipeline()` type signature and dispatch, import `LoopStep` |
| `src/superclaude/cli/roadmap/gates.py` | Add `CLASSIFY_AND_VALIDATE_GATE`, `_no_ambiguous_deviations()`, `_validation_complete_true()`, `_certified_is_true()`; update `CERTIFY_GATE`; update `ALL_GATES`; optionally remove or deprecate `SPEC_FIDELITY_GATE` |
| `src/superclaude/cli/roadmap/models.py` | Add `deviation_class` field and `VALID_DEVIATION_CLASSES` to `Finding` |
| `src/superclaude/cli/roadmap/executor.py` | Update `_build_steps()`, `_get_all_step_ids()`, `_apply_resume()`, `_format_halt_output()`; add loop-aware halt formatting |
| `src/superclaude/cli/roadmap/prompts.py` | Add `build_classify_and_validate_prompt()` |
| `src/superclaude/cli/roadmap/certify_prompts.py` | Add `build_certification_prompt_from_classify()` |
| `src/superclaude/cli/roadmap/remediate.py` | Add `parse_findings_from_classify_output()` |

### 11.2 Files Not Modified (but Considered)

| File | Why Not |
|------|---------|
| `src/superclaude/cli/pipeline/gates.py` | Gate evaluation logic (`gate_passed()`) is generic and already handles `GateCriteria` -- no changes needed |
| `src/superclaude/cli/pipeline/trailing_gate.py` | Trailing gates not used by LoopStep |
| `src/superclaude/cli/roadmap/fidelity.py` | The `FidelityDeviation` model is consumed by `spec-fidelity`, which is being replaced. Left in place for backward compatibility but not extended. |

### 11.3 New Test Files

| File | Coverage |
|------|----------|
| `tests/pipeline/test_loop_executor.py` | LoopStep execution, iteration bounds, gate evaluation, cancellation |
| (existing) `tests/pipeline/test_models.py` | LoopStep construction, validation |
| (existing) `tests/roadmap/test_gates_data.py` | New gate definitions, semantic checks |
| (existing) `tests/roadmap/test_models.py` | Finding.deviation_class validation |
| (existing) `tests/roadmap/test_remediate.py` | Findings parser |

---

## 12. Risk Assessment

### 12.1 Risk Matrix

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **LoopStep primitive adds complexity to a generic module** | HIGH | MEDIUM | LoopStep is self-contained. Existing pipelines never see it unless they construct one. Type union is additive, not breaking. |
| **Single unified step is too complex for one LLM pass** | HIGH | MEDIUM | The prompt asks for annotation + fidelity + classification, which is substantial but comparable to the merge step (also 4 inputs). Context window budget is ~600s timeout. If quality degrades, the step can be split in v2.26 without changing the LoopStep primitive. |
| **Anti-laundering safeguards insufficient** | MEDIUM | LOW | Same mitigations as Variant A: separate subprocess, citation requirement, AMBIGUOUS safety valve. Additionally, the unified step has no prior state to be biased by. |
| **LoopStep interaction with trailing gates** | LOW | LOW | LoopStep does not use trailing gates. Body steps within the loop use BLOCKING mode exclusively. |
| **Remediate prompt confusion from deviation_class** | MEDIUM | LOW | The remediate prompt only receives SLIP findings. INTENTIONAL findings are filtered out by the parser. |
| **Resume logic for LoopStep** | MEDIUM | MEDIUM | Simple: check exit_gate on exit_output_file. If passes, skip entire loop. If fails, re-run from iteration 1. No partial-loop resume. |
| **Backward compatibility of Finding model** | LOW | LOW | Default `deviation_class="UNCLASSIFIED"` preserves all existing behavior. Validation in `__post_init__` uses a known set. |
| **State file schema change** | LOW | LOW | Loop iterations produce new step IDs (e.g., `remediate.1`). Existing state consumers that iterate over step IDs are unaffected since they look up specific known IDs. |

### 12.2 Specific Risks of the Structural Refactor Approach

**Risk: All-or-nothing delivery.**
Unlike Variant A's two-scope sequencing, this variant has no intermediate
deliverable. The entire pipeline change must work end-to-end. If the
classify-and-validate step fails in production, there is no partial fallback
to the old spec-fidelity step.

**Mitigation**: The old `SPEC_FIDELITY_GATE` is not deleted, only removed
from `_build_steps()`. A `--legacy-fidelity` flag could be added to fall
back to the v4 pipeline shape if needed. This is not in scope for v2.25 but
is a trivial addition.

**Risk: LoopStep primitive is over-engineered for one use case.**
Currently only the remediate-certify cycle uses LoopStep. If no other
pipeline needs it, it is unnecessary abstraction in the generic executor.

**Mitigation**: LoopStep is ~30 lines of model + ~90 lines of executor logic.
The cost is low. The sprint pipeline's future test-fix cycle is a natural
second consumer. The abstraction pays for itself if used even twice.

---

## 13. Backward Compatibility

### 13.1 Pipeline Executor (`pipeline/executor.py`)

The type signature change from `list[Step | list[Step]]` to
`list[Step | list[Step] | LoopStep]` is backward compatible:

- Existing callers that pass `list[Step | list[Step]]` are valid inputs
  to the new signature (a subtype of the union).
- The `isinstance` dispatch in the for-loop adds a new branch but does not
  alter existing branches.
- No existing behavior changes for pipelines that do not use `LoopStep`.

### 13.2 Pipeline Models (`pipeline/models.py`)

The `LoopStep` dataclass is a new addition. No existing dataclass is
modified. The `Step` dataclass is unchanged.

### 13.3 Finding Model (`roadmap/models.py`)

The `deviation_class` field defaults to `"UNCLASSIFIED"`, preserving
existing construction patterns. The `__post_init__` validation is additive
(validates a new field) and does not alter existing validation behavior.

**Serialization compatibility**: Existing serialized Findings (in YAML
frontmatter or JSON state files) that lack `deviation_class` will
deserialize correctly via the default value, provided the deserialization
uses keyword arguments or `dataclasses.fields()` with defaults.

### 13.4 Gate Registry

`SPEC_FIDELITY_GATE` remains defined in `gates.py` but is removed from
`ALL_GATES` and from `_build_steps()`. Any external code that references
`SPEC_FIDELITY_GATE` directly will continue to work (the constant still
exists). It is marked with a deprecation comment.

### 13.5 Sprint Pipeline

The sprint pipeline (`src/superclaude/cli/sprint/`) does not use
`spec-fidelity`, `remediate`, or `certify` steps. It is completely
unaffected by all changes in this spec. The only shared code path that
changes is `execute_pipeline()`, which gains a new dispatch branch that
sprint pipelines never trigger (they never construct `LoopStep` objects).

---

## 14. What v2.24 Would Have Looked Like With v5-B

1. **classify-and-validate** reads spec + roadmap + debate + diff in one pass.
   Classifies `steps/` layout (D-02, R2) as INTENTIONAL. Classifies missing
   models (DEV-002) and missing functions (DEV-003) as SLIPs. Module rename
   portion of DEV-001 is SLIP (not discussed). No AMBIGUOUS deviations.
   Gate passes.

2. **LoopStep iteration 1**: Remediate receives 2 SLIP findings with specific
   fix_guidance. Fixes roadmap.md to add missing models and functions.
   Inline certify runs, checks fixes against spec. Certify gate passes.
   Loop exits.

3. **Pipeline completes** in one run without manual intervention.

Total pipeline steps: 10 (vs. v4's 8 that halted, or brainstorm's 12).

---

## 15. Open Questions Resolved

| # | Question | Resolution |
|---|----------|------------|
| 1 | Should deviation-analysis accept AMBIGUOUS at lower severity? | No. AMBIGUOUS blocks unconditionally. Use `--accept-ambiguous` flag if needed (deferred). |
| 2 | How does `--resume` interact with new steps? | LoopStep resume checks exit_gate on exit_output_file. Simple pass/fail. |
| 3 | Remediation cycle bound? | `max_iterations=2` on LoopStep. Configurable per construction. |
| 4 | Certify semantic check gap? | Fixed: `_certified_is_true` added to `CERTIFY_GATE`. |
| 5 | Should annotate step receive extraction? | N/A -- unified step reads spec directly. |
| 6 | Blast radius depth? | Deferred to v2.26. Classify-and-validate does not perform blast radius analysis. |
| 7 | spec-deviations.md as living artifact? | N/A -- classify-and-validate.md is regenerated on each run. |
| 8 | Spec update recommendations? | Deferred. INTENTIONAL deviations are logged but no spec-update step is proposed. |
| 9 | Finding.status lifecycle addition? | Deferred. No VERIFICATION_FAILED status in v2.25. Certify updates Finding status to FAILED on check failure. |
| 10 | Skill protocol alignment? | classify-and-validate maps to Wave 3 sub-step. LoopStep maps to Wave 4. |

---

## 16. Success Criteria

1. The v2.24 spec, when run through the v5-B pipeline, completes without
   manual intervention.
2. INTENTIONAL deviations (D-02, D-04) are classified correctly and do not
   trigger remediation.
3. SLIP deviations (DEV-002, DEV-003) are classified, remediated, and
   certified in a single pipeline run.
4. The LoopStep primitive works generically -- a unit test demonstrates a
   non-roadmap LoopStep executing correctly.
5. Existing sprint pipeline tests pass without modification.
6. Finding objects with `deviation_class="UNCLASSIFIED"` (legacy) pass
   validation without errors.

---

## Appendix A: Type Signature Summary

```python
# Before (v4):
def execute_pipeline(
    steps: list[Step | list[Step]],
    ...
) -> list[StepResult]: ...

# After (v5-B):
def execute_pipeline(
    steps: list[Step | list[Step] | LoopStep],
    ...
) -> list[StepResult]: ...

# New in pipeline/models.py:
@dataclass
class LoopStep:
    id: str
    body: list[Step]
    exit_gate: GateCriteria
    exit_output_file: Path
    max_iterations: int = 2
    exit_prompt: str = ""
    exit_timeout_seconds: int = 300

# Modified in roadmap/models.py:
@dataclass
class Finding:
    # ... existing fields ...
    deviation_class: str = "UNCLASSIFIED"  # NEW
```

## Appendix B: Gate Definitions Summary

| Gate | Tier | Semantic Checks | Blocks On |
|------|------|-----------------|-----------|
| `CLASSIFY_AND_VALIDATE_GATE` | STRICT | `no_ambiguous_deviations`, `validation_complete_true` | Any AMBIGUOUS deviation |
| `CERTIFY_GATE` (updated) | STRICT | `frontmatter_values_non_empty`, `per_finding_table_present`, `certified_true` | `certified != true` |
| `SPEC_FIDELITY_GATE` (deprecated) | STRICT | (unchanged) | Retained for backward compat, removed from pipeline |

## Appendix C: Code References

- Pipeline executor: `src/superclaude/cli/pipeline/executor.py`
- Pipeline models: `src/superclaude/cli/pipeline/models.py`
- Roadmap step builder: `src/superclaude/cli/roadmap/executor.py:_build_steps()`
- Gate definitions: `src/superclaude/cli/roadmap/gates.py`
- Prompt builders: `src/superclaude/cli/roadmap/prompts.py`
- Finding model: `src/superclaude/cli/roadmap/models.py:Finding`
- Certify prompts: `src/superclaude/cli/roadmap/certify_prompts.py`
- Remediate module: `src/superclaude/cli/roadmap/remediate.py`
- Brainstorm reference: `.dev/releases/backlog/2.25-roadmap-v5/brainstorm-reference.md`
