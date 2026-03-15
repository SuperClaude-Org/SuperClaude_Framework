# Diff Analysis -- execution_mode Annotation Value Set (Q7)

## Variants Under Analysis

Seven proposed values for the `execution_mode` annotation field on tasklist phases/tasks.

### Variant Group A: Core Values (Low Controversy)

| Value | Semantics | Current Evidence |
|---|---|---|
| `claude` | Phase executed via Claude subprocess (current default behavior) | All phases today run this way via `ClaudeProcess` |
| `skip` | Phase not executed; used for conditional gates | Phase 5 in v2.24.5 skipped when Phase 1 = WORKING |

### Variant Group B: Automation Values (Moderate Controversy)

| Value | Semantics | Current Evidence |
|---|---|---|
| `python` | Extract shell commands from task steps, run via `subprocess.run()`, capture output | Phase 1 tasks are pure shell commands (e.g., `claude --print -p "hello" --max-turns 1`) |
| `python-gate` | Like `python` but results determine subsequent phase activation | Phase 1 is exactly this pattern: shell commands whose output gates Phase 5 |

### Variant Group C: Advanced Values (High Controversy)

| Value | Semantics | Current Evidence |
|---|---|---|
| `hybrid` | Mix of python and claude tasks within a single phase | No current use case in v2.24.5 |
| `dry-run` | Execute in python but do not write artifacts | No current use case; meta/testing concern |
| `manual` | Sprint pauses for human intervention | No current use case in v2.24.5 |

## Structural Differences

### 1. Executor Dispatch Complexity

- **claude**: Already implemented. Zero new code.
- **skip**: Trivially implementable. `if mode == "skip": return PhaseResult(status=SKIPPED)`.
- **python**: Requires a shell command extractor (parse step markdown for shell blocks), subprocess runner, output capture, and evidence artifact writer. Medium implementation.
- **python-gate**: Everything in `python` PLUS a result-to-gate-decision mapper. Must define how results propagate to downstream phase activation. Medium-high implementation.
- **hybrid**: Requires per-task annotation support (currently annotations are per-phase). Requires the executor to switch dispatch strategies mid-phase. High implementation.
- **dry-run**: Requires duplicating python execution with artifact-write suppression. Low-medium implementation but unclear value.
- **manual**: Requires a pause/resume mechanism in the sprint runner, user input collection, and state persistence across the pause. High implementation.

### 2. Annotation Granularity

- `claude`, `python`, `skip`, `dry-run`, `manual`: Phase-level annotation only.
- `python-gate`: Phase-level annotation with cross-phase side effects.
- `hybrid`: Requires task-level annotation (breaks current per-phase model).

### 3. Composability with Existing Fields

| Value | Interacts with Tier? | Interacts with Dependencies? | Interacts with Verification? |
|---|---|---|---|
| `claude` | Yes (tier drives verification) | Yes (normal) | Yes (normal) |
| `skip` | No (tier irrelevant) | Yes (skipped phases may gate others) | No |
| `python` | Partial (EXEMPT tasks only make sense) | Yes (normal) | No (python output IS the verification) |
| `python-gate` | Partial (EXEMPT) | Yes (creates implicit dependencies) | No |
| `hybrid` | Complex (different per task) | Complex | Complex |
| `dry-run` | No | No | No |
| `manual` | No | Yes (blocks downstream) | N/A |

## Contradictions Identified

1. **python vs python-gate overlap**: `python-gate` is a strict superset of `python`. If you have `python-gate`, you can always ignore the gate result, making it equivalent to `python`. Having both creates ambiguity about which to use for non-gating shell phases.

2. **hybrid breaks the annotation model**: The current tasklist format has annotations at the phase level. `hybrid` requires per-task annotations, which is a structural change to the format, not just a new value.

3. **dry-run is meta-circular**: `dry-run` tests the annotation system itself. This is a development/testing concern that should be handled by the sprint runner's existing `--dry-run` flag, not by an annotation value.

4. **skip vs conditional dependency**: `skip` can be modeled as a dependency that evaluates to false. The v2.24.5 tasklist already uses prose-level conditionality ("Activates only if Phase 1 result is BROKEN") rather than a formal annotation.

## Unique Contributions per Value

| Value | Unique Capability Not Covered by Others |
|---|---|
| `claude` | Full LLM execution with tool access |
| `skip` | Zero-cost phase deactivation |
| `python` | Deterministic shell execution without LLM cost |
| `python-gate` | Conditional flow control based on empirical results |
| `hybrid` | None (composition of `python` + `claude` at task level) |
| `dry-run` | None (covered by `--dry-run` CLI flag) |
| `manual` | Human-in-the-loop pause capability |
