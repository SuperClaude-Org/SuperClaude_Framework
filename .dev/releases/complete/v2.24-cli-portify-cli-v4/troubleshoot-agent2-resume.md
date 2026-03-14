# Resume Logic Investigation Report
# Agent 2 - Root Cause Analyst
# Date: 2026-03-13

## Summary

The `--resume` flag is implemented in `src/superclaude/cli/roadmap/executor.py`. It reads
the state file BEFORE deciding to run stages, evaluates each step's gate condition against
on-disk output files (not the state file's recorded status), and uses a "first-failure
cascades" model: skip all steps until the first gate failure, then run that step and all
subsequent steps unconditionally.

The current run state at `.dev/releases/current/v2.24-cli-portify-cli-v4/.roadmap-state.json`
shows `spec-fidelity` failed on attempt 2. A `--resume` invocation on this directory
will re-evaluate gates from the first step and skip everything through `test-strategy`
(all passing), then stop at `spec-fidelity` and re-run it.

---

## Source Files

- Main entry: `src/superclaude/cli/roadmap/executor.py`
- Pipeline executor: `src/superclaude/cli/pipeline/executor.py`
- Gate logic: `src/superclaude/cli/pipeline/gates.py`
- Roadmap-specific gate criteria: `src/superclaude/cli/roadmap/gates.py`
- Data models: `src/superclaude/cli/pipeline/models.py`
- CLI commands: `src/superclaude/cli/roadmap/commands.py`
- Tests (core): `tests/roadmap/test_resume.py`
- Tests (post-pipeline states): `tests/roadmap/test_resume_pipeline_states.py`

---

## 1. Entry Point: How --resume is Wired In

File: `src/superclaude/cli/roadmap/commands.py`, lines 55-61, 149

```python
@click.option(
    "--resume",
    is_flag=True,
    help=(
        "Skip steps whose outputs already pass their gates. "
        "Re-run from the first failing step."
    ),
)
...
execute_roadmap(config, resume=resume, no_validate=no_validate)
```

The `resume` bool propagates into `execute_roadmap()`.

---

## 2. execute_roadmap: Top-Level Resume Control

File: `src/superclaude/cli/roadmap/executor.py`, lines 822-890

```python
def execute_roadmap(config: RoadmapConfig, resume: bool = False, no_validate: bool = False) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    steps = _build_steps(config)

    if config.dry_run:
        _dry_run_output(steps)
        return

    # --resume: check which steps already pass their gates
    if resume:
        from ..pipeline.gates import gate_passed
        steps = _apply_resume(steps, config, gate_passed)

    results = execute_pipeline(
        steps=steps,
        config=config,
        run_step=roadmap_run_step,
        ...
    )

    _save_state(config, results)

    failures = [r for r in results if r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)]
    if failures:
        halt_msg = _format_halt_output(results, config)
        print(halt_msg, file=sys.stderr)
        sys.exit(1)

    # After successful pipeline, check if validation already ran (--resume path)
    if resume:
        state_file = config.output_dir / ".roadmap-state.json"
        state = read_state(state_file)
        if state and "validation" in state:
            saved = state["validation"]
            if saved.get("status") in ("pass", "fail"):
                print(f"[roadmap] Validation already completed ({saved['status']}), skipping")
                return

    _auto_invoke_validate(config)
```

Key observation: `_apply_resume()` is called BEFORE `execute_pipeline()`. The modified
`steps` list is what actually gets executed. The state file is only consulted for the
stale-spec check and the post-pipeline validation skip guard.

---

## 3. _apply_resume: The Core Skip/Re-Run Logic

File: `src/superclaude/cli/roadmap/executor.py`, lines 1055-1131 (full function)

### Pseudocode

```
_apply_resume(steps, config, gate_fn):
    state = read_state(".roadmap-state.json")   # may be None

    # Stale spec detection
    if state exists:
        saved_hash = state["spec_hash"]
        current_hash = sha256(spec_file)
        if saved_hash != current_hash:
            print WARNING to stderr
            force_extract = True

    skipped = 0
    result = []           # steps to actually run
    found_failure = False

    for each entry in steps:

        if found_failure:
            # Once we found any failing step, include ALL remaining steps
            result.append(entry)
            continue

        if entry is a parallel group (list[Step]):
            all_pass = True
            for each step in group:
                if step has gate:
                    passed, reason = gate_fn(step.output_file, step.gate)
                    if not passed:
                        all_pass = False; break
                else:
                    all_pass = False; break

            if all_pass:
                skipped += len(group)
                print "[roadmap] Skipping <ids> (gates pass)"
            else:
                found_failure = True
                result.append(entry)     # run the whole group

        else:  # sequential step
            # Force extract re-run on stale spec
            if force_extract and entry.id == "extract":
                found_failure = True
                result.append(entry)
                continue

            if entry has gate:
                passed, reason = gate_fn(entry.output_file, entry.gate)
                if passed:
                    skipped += 1
                    print "[roadmap] Skipping <id> (gate passes)"
                    continue

            # gate failed (or step has no gate)
            found_failure = True
            result.append(entry)

    if skipped > 0:
        print "[roadmap] Skipped N steps (gates pass)"

    if not result:
        print "[roadmap] All steps already pass gates. Nothing to do."

    return result
```

### Actual Code

Lines 1055-1131 of `src/superclaude/cli/roadmap/executor.py`:

```python
def _apply_resume(
    steps: list[Step | list[Step]],
    config: RoadmapConfig,
    gate_fn: Callable,
) -> list[Step | list[Step]]:
    state_file = config.output_dir / ".roadmap-state.json"
    state = read_state(state_file)
    force_extract = False
    if state is not None:
        saved_hash = state.get("spec_hash", "")
        current_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
        if saved_hash and saved_hash != current_hash:
            print(
                f"WARNING: spec-file has changed since last run.\n"
                f"  Last hash: {saved_hash[:12]}...\n"
                f"  Current:   {current_hash[:12]}...\n"
                f"Forcing re-run of extract step.",
                file=sys.stderr,
                flush=True,
            )
            force_extract = True

    skipped = 0
    result: list[Step | list[Step]] = []
    found_failure = False

    for entry in steps:
        if found_failure:
            result.append(entry)
            continue

        if isinstance(entry, list):
            all_pass = True
            for s in entry:
                if s.gate:
                    passed, _reason = gate_fn(s.output_file, s.gate)
                    if not passed:
                        all_pass = False
                        break
                else:
                    all_pass = False
                    break
            if all_pass:
                skipped += len(entry)
                print(f"[roadmap] Skipping {', '.join(s.id for s in entry)} (gates pass)", flush=True)
            else:
                found_failure = True
                result.append(entry)
        else:
            if force_extract and entry.id == "extract":
                found_failure = True
                result.append(entry)
                continue

            if entry.gate:
                passed, _reason = gate_fn(entry.output_file, entry.gate)
                if passed:
                    skipped += 1
                    print(f"[roadmap] Skipping {entry.id} (gate passes)", flush=True)
                    continue
            found_failure = True
            result.append(entry)

    if skipped > 0:
        print(f"[roadmap] Skipped {skipped} steps (gates pass)", flush=True)

    if not result:
        print("[roadmap] All steps already pass gates. Nothing to do.", flush=True)

    return result
```

---

## 4. How State Is Read and What It Is Used For

### State file schema (from actual `.roadmap-state.json`)

```json
{
  "schema_version": 1,
  "spec_file": "<absolute path>",
  "spec_hash": "<sha256 hex>",
  "agents": [...],
  "depth": "standard",
  "last_run": "<ISO timestamp>",
  "steps": {
    "extract":          { "status": "PASS", "attempt": 1, ... },
    "generate-opus-architect": { "status": "PASS", ... },
    "generate-haiku-architect": { "status": "PASS", ... },
    "diff":             { "status": "PASS", ... },
    "debate":           { "status": "PASS", ... },
    "score":            { "status": "PASS", ... },
    "merge":            { "status": "PASS", ... },
    "test-strategy":    { "status": "PASS", ... },
    "spec-fidelity":    { "status": "FAIL", "attempt": 2, ... }
  },
  "fidelity_status": "fail"
}
```

### Critical finding: state file step statuses are NOT consulted during resume

The `_apply_resume` function reads the state file ONLY for the `spec_hash` comparison
(line 1068). It does NOT read the `steps` dictionary in the state file to determine
what to skip or re-run.

Instead, it calls `gate_fn(step.output_file, step.gate)` for every step in order. This
evaluates the actual on-disk output file against the gate criteria defined per-step.

This is a design decision: the gate re-evaluation is the single source of truth for
resume decisions. The state file's recorded `status` values are purely informational
(used for human diagnostics, `derive_pipeline_status()`, and post-pipeline validation
check). They do not drive the skip/run logic.

---

## 5. Gate Evaluation: What Determines Skip vs Re-Run

File: `src/superclaude/cli/pipeline/gates.py`, lines 20-69

The `gate_passed(output_file, criteria)` function checks the following in order,
based on the enforcement tier:

| Tier     | Condition checked |
|----------|------------------------------------------------|
| EXEMPT   | Always passes (returns True, None) |
| LIGHT    | File exists AND file is non-empty |
| STANDARD | File exists + non-empty + min_lines met + required frontmatter fields present |
| STRICT   | All STANDARD checks + semantic check functions pass |

**Skip condition (line 1118-1121):**
```python
if entry.gate:
    passed, _reason = gate_fn(entry.output_file, entry.gate)
    if passed:
        skipped += 1
        continue   # SKIP this step
```
A step is skipped if and only if its output file currently satisfies all gate criteria.

**Re-run condition (lines 1122-1123):**
```python
found_failure = True
result.append(entry)
```
A step is re-run (included in the returned list) if:
- It has no gate at all, OR
- Its gate evaluation returns False (file missing, empty, below min_lines, frontmatter absent, or semantic check fails)

**Cascade behavior (lines 1086-1089):**
```python
if found_failure:
    result.append(entry)
    continue
```
Once `found_failure` is set True by any step, ALL remaining steps are included in the
result list unconditionally, without re-evaluating their gates. This ensures the pipeline
is sequential and consistent: you cannot skip a step if a prior step is re-running.

---

## 6. Current Run State and What --resume Would Do

The current state file at `.dev/releases/current/v2.24-cli-portify-cli-v4/.roadmap-state.json`
records all 9 steps, with `spec-fidelity` as `FAIL` (attempt 2).

The spec hash in the state file is:
`3d1a6d1581bd8352ace0f80faf845b1131b8df36b3fe7e458e299a7647dfbaa9`

**If `--resume` is invoked without modifying the spec file:**

1. `read_state()` loads the state file
2. `sha256(spec_file)` is computed; if it matches the stored hash, `force_extract = False`
3. Gate evaluation proceeds in order:
   - `extract`: `extraction.md` exists and passes gate -> SKIP
   - `generate-opus-architect` + `generate-haiku-architect` (parallel): both output files exist and pass -> SKIP group
   - `diff`: `diff-analysis.md` exists and passes -> SKIP
   - `debate`: `debate-transcript.md` exists and passes -> SKIP
   - `score`: `base-selection.md` exists and passes -> SKIP
   - `merge`: `roadmap.md` exists and passes -> SKIP
   - `test-strategy`: `test-strategy.md` exists and passes -> SKIP
   - `spec-fidelity`: `spec-fidelity.md` exists but the SPEC_FIDELITY_GATE evaluation is the key question (see section 7)
4. If `spec-fidelity` gate fails: `found_failure = True`, step is included for re-run
5. All remaining steps after `spec-fidelity` (none in the 9-step list) are included

The spec-fidelity output file currently contains valid frontmatter with `tasklist_ready: false`
and was written on a failed attempt. The gate behavior on a prior-failed step's output
depends entirely on what SPEC_FIDELITY_GATE requires.

---

## 7. SPEC_FIDELITY_GATE: Does It Pass or Fail the Existing Output?

File: `src/superclaude/cli/roadmap/gates.py` (first 60 lines read)

The gate uses GateCriteria with required frontmatter fields. The existing `spec-fidelity.md`
starts with:

```
---
high_severity_count: 3
medium_severity_count: 8
low_severity_count: 5
total_deviations: 16
validation_complete: true
tasklist_ready: false
---
```

If SPEC_FIDELITY_GATE requires `tasklist_ready: true` as a semantic check, or if the
step failed its gate during the original run due to a subprocess non-zero exit (not a gate
check), the on-disk file may or may not satisfy the gate on resume.

The state file records `"status": "FAIL"` and `"attempt": 2`, meaning two subprocess
runs were made. The `.err` file for spec-fidelity is empty (1 line, blank), suggesting
the subprocess exited non-zero but produced no stderr content. However, the output file
`spec-fidelity.md` IS present and well-formed with frontmatter.

**This is a potential gap (see section 9):** the state file records FAIL but the output
file on disk may now satisfy the gate, depending on gate tier and semantic checks. If it
does satisfy the gate, `--resume` will skip `spec-fidelity` and report "All steps pass."
If it does not satisfy the gate, `spec-fidelity` will be re-run correctly.

---

## 8. Post-Pipeline Validation Skip Logic

File: `src/superclaude/cli/roadmap/executor.py`, lines 877-888

After the pipeline completes successfully (all included steps pass), there is a separate
guard for the post-pipeline `validate` step:

```python
if resume:
    state_file = config.output_dir / ".roadmap-state.json"
    state = read_state(state_file)
    if state and "validation" in state:
        saved = state["validation"]
        if saved.get("status") in ("pass", "fail"):
            print(f"[roadmap] Validation already completed ({saved['status']}), skipping")
            return
```

Here the state file IS used directly. If a prior validation completed with `pass` or
`fail`, it is not re-run on resume. The current state file has no `validation` key,
so validation will be re-invoked after a successful `--resume` run.

---

## 9. Bugs and Gaps Identified

### Gap 1: State file step statuses ignored during gate evaluation

The state file records per-step `status` values (PASS, FAIL) but `_apply_resume()` does
NOT use them. It re-evaluates the gate from the actual output file on disk.

**Consequence:** If a step previously FAILed but happened to write a valid output file
before failing (e.g., subprocess exited 1 after writing output), the gate check on the
on-disk file may PASS, causing `--resume` to skip the step even though it was recorded
as FAIL. Whether this is a bug or a feature depends on intent.

The current `spec-fidelity` situation is an example: the step is `FAIL` in state, but
`spec-fidelity.md` exists on disk with well-formed frontmatter. If the gate passes the
existing file, `--resume` will skip re-running spec-fidelity and proceed. This may be
undesirable if the intent was to re-run the failing step regardless.

### Gap 2: No guard for "step failed its gate, output file is invalid but present"

If a step writes a partial or gate-failing output file and then exits non-zero, the output
file exists on disk but fails its gate. `--resume` will correctly identify this as a
failure and re-run the step. However, the previous partial output file is NOT deleted
before re-running. This is consistent with the existing behavior (no cleanup), but means
the step must overwrite the file correctly or the gate check on the new run may be
confused by leftover content.

### Gap 3: Parallel group cascade is conservative

For a parallel group, if any single step's gate fails, the ENTIRE group is included for
re-run, even if the other step in the group passes its gate. This is correct for
consistency but means a single generate step failure causes both generate steps to re-run.

Lines 1091-1108:
```python
if isinstance(entry, list):
    all_pass = True
    for s in entry:
        if s.gate:
            passed, _reason = gate_fn(s.output_file, s.gate)
            if not passed:
                all_pass = False
                break
        else:
            all_pass = False
            break
    if all_pass:
        skipped += len(entry)
    else:
        found_failure = True
        result.append(entry)   # whole group re-runs
```

### Gap 4: Steps with no gate are always re-run

Lines 1116-1123:
```python
if entry.gate:
    passed, _reason = gate_fn(entry.output_file, entry.gate)
    if passed:
        skipped += 1
        continue
found_failure = True
result.append(entry)
```

If a step has `gate = None`, it always triggers `found_failure = True` and includes
itself and all subsequent steps. In the current 9-step pipeline, all steps have gates,
so this path is not reached. But it is a latent risk if a gateless step is ever added.

### Gap 5: Validation skip guard reads state AFTER _save_state() overwrites it

Lines 859-888:
```python
_save_state(config, results)       # writes new state from THIS run's results
...
if resume:
    state = read_state(state_file)  # reads the file just written
    if state and "validation" in state:
        ...
```

`_save_state()` preserves the existing `validation` key (lines 609-610):
```python
if existing_validation is not None:
    state["validation"] = existing_validation
```

So the validation skip guard correctly reads the preserved validation key. This is not
a bug, but the two-step write-then-read pattern is worth noting.

---

## 10. State Transitions and Resume Scenarios

### Scenario A: All prior steps PASS, spec-fidelity FAIL (current state)

```
--resume invoked
  spec_hash check: PASS (no warning if spec unchanged)
  extract:       gate_passed(extraction.md) -> True  -> SKIP
  generate-*:    gate_passed(roadmap-*.md)  -> True  -> SKIP group
  diff:          gate_passed(diff-analysis.md) -> True -> SKIP
  debate:        gate_passed(debate-transcript.md) -> True -> SKIP
  score:         gate_passed(base-selection.md) -> True -> SKIP
  merge:         gate_passed(roadmap.md) -> True -> SKIP
  test-strategy: gate_passed(test-strategy.md) -> True -> SKIP
  spec-fidelity: gate_passed(spec-fidelity.md) -> ??? (see Gap 1)

If spec-fidelity gate FAILS existing file:
  -> spec-fidelity included for re-run
  -> execute_pipeline runs only [spec-fidelity]
  -> CORRECT behavior

If spec-fidelity gate PASSES existing file:
  -> result = []
  -> "All steps already pass gates. Nothing to do."
  -> Pipeline considered complete
  -> _auto_invoke_validate runs
  -> POTENTIALLY WRONG if intent was to re-run spec-fidelity
```

### Scenario B: No state file (first resume or state file deleted)

```
--resume invoked
  read_state -> None
  force_extract = False (no hash to compare against)
  All gate checks proceed from the first step
  First step whose output file fails gate -> that step and all subsequent run
```

### Scenario C: Stale spec (spec file changed since last run)

```
--resume invoked
  spec_hash check: MISMATCH
  WARNING printed to stderr
  force_extract = True
  extract: forced to found_failure=True -> included for re-run
  All steps after extract: included for re-run (cascade)
```

### Scenario D: All steps pass (clean resume)

```
--resume invoked
  All gate checks return True
  result = []
  "All steps already pass gates. Nothing to do."
  Pipeline skipped
  If no validation in state: _auto_invoke_validate runs
```

---

## 11. Remediate and Certify Resume (Post-Pipeline Phases)

These are separate check functions called from outside `execute_roadmap()`, used by the
`remediate` and `certify` sub-commands.

`check_remediate_resume()` (lines 959-990): Returns True (skip) when:
1. `remediation-tasklist.md` exists
2. Passes REMEDIATE_GATE
3. `source_report_hash` in tasklist frontmatter matches SHA-256 of current validation report

`check_certify_resume()` (lines 993-1012): Returns True (skip) when:
1. `certification-report.md` exists
2. Passes CERTIFY_GATE

These functions use gate evaluation + hash checks (not the state file's `remediate`/`certify`
keys) to determine skip/re-run. They return a bool consumed by the caller to decide whether
to run the step.

---

## 12. Files and Line References Summary

| Component | File | Key Lines |
|-----------|------|-----------|
| CLI flag definition | `src/superclaude/cli/roadmap/commands.py` | 55-61 |
| CLI flag pass-through | `src/superclaude/cli/roadmap/commands.py` | 149 |
| execute_roadmap entry | `src/superclaude/cli/roadmap/executor.py` | 822-890 |
| _apply_resume (full) | `src/superclaude/cli/roadmap/executor.py` | 1055-1131 |
| Stale spec detection | `src/superclaude/cli/roadmap/executor.py` | 1067-1079 |
| Skip condition | `src/superclaude/cli/roadmap/executor.py` | 1116-1121 |
| Re-run condition | `src/superclaude/cli/roadmap/executor.py` | 1122-1123 |
| Cascade condition | `src/superclaude/cli/roadmap/executor.py` | 1086-1089 |
| Parallel group check | `src/superclaude/cli/roadmap/executor.py` | 1091-1108 |
| Validation skip guard | `src/superclaude/cli/roadmap/executor.py` | 877-888 |
| read_state | `src/superclaude/cli/roadmap/executor.py` | 794-804 |
| write_state | `src/superclaude/cli/roadmap/executor.py` | 784-791 |
| _save_state | `src/superclaude/cli/roadmap/executor.py` | 567-634 |
| gate_passed | `src/superclaude/cli/pipeline/gates.py` | 20-69 |
| StepStatus enum | `src/superclaude/cli/pipeline/models.py` | 17-43 |
| execute_pipeline | `src/superclaude/cli/pipeline/executor.py` | 46-133 |
| check_remediate_resume | `src/superclaude/cli/roadmap/executor.py` | 959-990 |
| check_certify_resume | `src/superclaude/cli/roadmap/executor.py` | 993-1012 |
| Core resume tests | `tests/roadmap/test_resume.py` | all |
| Post-pipeline tests | `tests/roadmap/test_resume_pipeline_states.py` | all |

---

## 13. Conclusion

The `--resume` logic is evidence-based and gate-driven. It does NOT read the `steps`
dictionary from the state file to determine skip/re-run. Instead it re-evaluates the
actual gate condition against on-disk output files at the time of the `--resume` invocation.

The single most important design decision: **the first step whose output file fails its
gate triggers a cascade** - that step and all subsequent steps are re-run, regardless
of whether their output files pass their own gates. This is intentional (ensures
sequential dependency correctness) but means a failing step earlier in the pipeline
forces re-execution of all downstream steps even if their outputs are valid.

For the current run (`spec-fidelity` FAIL, all others PASS): the behavior of `--resume`
depends entirely on whether the existing `spec-fidelity.md` satisfies SPEC_FIDELITY_GATE.
If the gate check passes the existing file (it has valid frontmatter), `--resume` will
report nothing to do and skip re-running spec-fidelity. If the gate check fails the
existing file, spec-fidelity will be correctly re-run.
