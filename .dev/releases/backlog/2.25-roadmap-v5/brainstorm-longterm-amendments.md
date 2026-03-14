---
title: "v2.25 Spec Amendment Brainstorm: Long-Term Quality & Robustness Issues"
version: "2.25.0-longterm-amendments"
status: draft
scope: "4 long-term quality/robustness issues identified by spec panel review"
author: claude-sonnet-4-6
created: 2026-03-14
issues_addressed:
  - "W-ADV-2 extended: roadmap.md content hash for stale detection"
  - "W-ADV-4: Non-integer remediation_attempts crashes budget check"
  - "W-ADV-3: Deviation ID format not constrained — comma in ID corrupts routing"
  - "N-2 extended: Two independent retry counters with no coordination spec"
---

# v2.25 Spec Amendment Brainstorm: Long-Term Quality & Robustness Issues

This document is a detailed specification amendment brainstorm for 4 long-term
quality and robustness issues identified by the spec panel review of the
v2.25 merged spec (`v2.25-spec-merged.md`). Each issue is analyzed with
multiple approaches, exact draft FR/NFR text, and a v2.25 vs. v2.26 deferral
assessment.

This is not a summary. Every approach is fully specified with implementation
mechanics, tradeoffs, and exact spec language ready to insert.

---

## ISSUE 1 (W-ADV-2 extended, MAJOR): `roadmap.md` content hash in `spec-deviations.md` for stale-detection

### Problem Restatement

The `annotate-deviations` step writes `spec-deviations.md` and its STANDARD
gate validates only structural completeness (frontmatter fields present,
minimum line count). When a user edits `roadmap.md` after a successful
`annotate-deviations` run and then invokes `--resume`, `_apply_resume()`
evaluates the STANDARD gate against the existing `spec-deviations.md`. The
gate passes because frontmatter fields are present and the file is long enough.
The stale artifact is therefore silently reused. Downstream, `spec-fidelity`
and `deviation-analysis` receive classification data that does not correspond
to the current `roadmap.md`, producing potentially incorrect INTENTIONAL vs.
SLIP routing.

The existing `_apply_resume()` already performs a `spec_hash` check for the
spec file itself (lines 1286-1297 of executor.py), detecting changes and
forcing re-extraction. No analogous check exists for `roadmap.md` as an input
to `annotate-deviations`.

---

### Approaches Considered

#### Approach A: `roadmap_hash` frontmatter field + SemanticCheck closure

**Mechanical Description**

The `annotate-deviations` step prompt instructs the LLM to include a
`roadmap_hash` field in the YAML frontmatter of `spec-deviations.md`. The
executor (post-subprocess) injects the actual SHA-256 of `roadmap.md` into
the frontmatter using the same pattern as `_inject_pipeline_diagnostics()` for
the extract step — the LLM writes a placeholder, the executor overwrites it.
Alternatively, the executor computes the hash and appends it via a new
`_inject_roadmap_hash()` helper called in `roadmap_run_step()` immediately
after `_sanitize_output()` for the `annotate-deviations` step.

For gate-time detection, a `SemanticCheck` is registered on
`ANNOTATE_DEVIATIONS_GATE` that re-reads `roadmap.md` and compares its
current SHA-256 against the stored `roadmap_hash`. The core problem is that
`SemanticCheck` functions have the fixed signature `(content: str) -> bool`
and receive only the file content — they have no access to external file
paths.

Three sub-approaches resolve this constraint:

**Sub-approach A1: Closure over path at gate-construction time**

```python
# In executor.py, _build_steps():
def _make_roadmap_hash_check(roadmap_path: Path) -> SemanticCheck:
    """Factory: returns a SemanticCheck that validates roadmap_hash
    against the current SHA-256 of roadmap_path."""

    def _check(content: str) -> bool:
        fm = _parse_frontmatter(content)
        if fm is None:
            return False
        stored_hash = fm.get("roadmap_hash", "")
        if not stored_hash:
            return False
        current_hash = hashlib.sha256(roadmap_path.read_bytes()).hexdigest()
        return stored_hash == current_hash

    return SemanticCheck(
        name="roadmap_hash_current",
        check_fn=_check,
        failure_message=(
            "roadmap.md has changed since spec-deviations.md was written. "
            "Re-run annotate-deviations."
        ),
    )

# Gate construction (cannot be module-level constant any more):
ANNOTATE_DEVIATIONS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_annotated",
        "intentional_improvement_count",
        "intentional_preference_count",
        "scope_addition_count",
        "not_discussed_count",
        "roadmap_hash",      # NEW required field
    ],
    min_lines=15,
    enforcement_tier="STANDARD",
    semantic_checks=[_make_roadmap_hash_check(merge_file)],  # closure
)
```

This sub-approach requires `ANNOTATE_DEVIATIONS_GATE` to be constructed
dynamically inside `_build_steps()` rather than as a module-level constant in
`gates.py`. It violates the current architecture principle in `gates.py` that
"Gate criteria are pure data -- no logic, no imports from pipeline/gates.py
enforcement code (NFR-005)." The gate is no longer pure data because the
check function closes over a `Path` and calls `hashlib.sha256()`.

Impact on `GateCriteria` architecture: minor. `GateCriteria` already accepts
`semantic_checks: list[SemanticCheck] | None`, so the dataclass itself does
not change. The change is entirely in how the gate is constructed — from a
module-level constant to a per-invocation factory call. The `ALL_GATES` list
in `gates.py` cannot include this gate at module load time; it would need to
be updated dynamically or excluded from the list.

**Sub-approach A2: Add `context: dict` parameter to `SemanticCheck`**

Modify the `SemanticCheck` dataclass in `pipeline/models.py` to carry an
optional `context` dict, and change the enforcement engine in
`pipeline/gates.py` to call `check_fn(content, context=check.context)` when
`check.context` is non-empty.

```python
@dataclass
class SemanticCheck:
    name: str
    check_fn: Callable[..., bool]   # was Callable[[str], bool]
    failure_message: str
    context: dict = field(default_factory=dict)

# In gates.py enforcement:
for check in gate.semantic_checks:
    if check.context:
        passed = check.check_fn(content, context=check.context)
    else:
        passed = check.check_fn(content)
```

The `_roadmap_hash_current(content: str, context: dict) -> bool` function in
`gates.py` reads `context["roadmap_path"]` and computes the hash. Gate
construction in `_build_steps()` passes the path in the `context` dict.

This approach modifies `pipeline/models.py` (the generic pipeline layer),
violating NFR-010 ("Neither `pipeline/executor.py` nor `pipeline/models.py`
SHALL be modified"). It would open a precedent for all future semantic checks
to receive arbitrary context, increasing the interface surface area.

**Sub-approach A3: Pre-gate validation hook outside the gate system**

A new function `_check_annotate_deviations_freshness(config, gate_fn)` is
called in `_apply_resume()` before the standard gate check for
`annotate-deviations`. If the function detects staleness (roadmap hash
mismatch), it marks the step as needing re-run by excluding it from the skip
list — regardless of whether the gate would otherwise pass.

```python
# In executor.py, _apply_resume():
def _check_annotate_deviations_freshness(
    config: RoadmapConfig,
    deviations_file: Path,
) -> bool:
    """Returns True if spec-deviations.md is fresh (roadmap_hash matches).
    Returns False if stale or if roadmap_hash field is missing."""
    if not deviations_file.exists():
        return False
    from .gates import _parse_frontmatter
    content = deviations_file.read_text(encoding="utf-8")
    fm = _parse_frontmatter(content)
    if fm is None:
        return False
    stored_hash = fm.get("roadmap_hash", "")
    if not stored_hash:
        return False
    merge_file = config.output_dir / "roadmap.md"
    if not merge_file.exists():
        return False
    current_hash = hashlib.sha256(merge_file.read_bytes()).hexdigest()
    return stored_hash == current_hash
```

`_apply_resume()` calls this function when it would otherwise skip the
`annotate-deviations` step. If it returns `False`, the step is re-added to
the run queue. This is a pre-gate hook, not a gate change. The gate itself
remains a module-level constant in `gates.py` with no closures.

Impact on `GateCriteria` architecture: zero. The gate dataclass and
enforcement engine are not modified. The freshness logic lives entirely in
`executor.py`'s resume path.

**Tradeoffs**

| | A1 (closure) | A2 (context dict) | A3 (pre-gate hook) |
|-|---|---|---|
| NFR-010 compliance | Yes | No (modifies models.py) | Yes |
| gates.py purity | Violated (gate no longer module-level constant) | Maintained | Maintained |
| ALL_GATES registry | Broken (gate is dynamic) | Maintained | Maintained |
| Architectural precedent | Moderate risk | High risk | Low risk |
| Test surface | Gate factory unit tests needed | Check fn unit tests needed | Hook unit tests needed |
| Detection at resume vs. gate check | Gate check (correct) | Gate check (correct) | Resume path only |
| False negatives | None (hash always current at gate check) | None | None |

**Implementation complexity estimate**

- A1: ~40 lines new code, 1 new helper, gates.py structural change, ALL_GATES update
- A2: ~30 lines new code + ~10 lines model change + pipeline/gates.py enforcement change
- A3: ~35 lines new code, executor.py only, no gate system changes

**v2.25 vs. v2.26 recommendation**

A3 is recommended for v2.25. A1 violates the module-level-constant architecture
of gates.py. A2 violates NFR-010. A3 achieves the same detection outcome
through the resume path at zero architectural cost.

---

#### Approach B: Spec prohibition + mtime warning

**Mechanical Description**

Add a behavioral rule to §8.2 of the spec: "Manual edits to `roadmap.md`
after the `annotate-deviations` step completes invalidate `spec-deviations.md`.
Users who edit `roadmap.md` after annotation SHOULD perform a full re-run, not
`--resume`." Separately, in `_apply_resume()`, add an mtime check: if
`mtime(roadmap.md) > mtime(spec-deviations.md)`, emit a WARNING to stderr
before proceeding.

```python
# In _apply_resume(), before the step-skip loop:
merge_file = config.output_dir / "roadmap.md"
deviations_file = config.output_dir / "spec-deviations.md"
if merge_file.exists() and deviations_file.exists():
    if merge_file.stat().st_mtime > deviations_file.stat().st_mtime:
        print(
            "WARNING: roadmap.md is newer than spec-deviations.md. "
            "spec-deviations.md may be stale. Consider a full re-run.",
            file=sys.stderr,
            flush=True,
        )
```

**Tradeoffs**

Pros:
- Zero implementation complexity beyond the warning
- No changes to gate system, models, or resume logic
- Catches the most common case (user edits file, immediately resumes)

Cons:
- Warning is advisory only. Users can ignore it and get silently incorrect results
- mtime comparison is unreliable on filesystems with coarse timestamp resolution
  (1-second on HFS+, some NFS mounts). A file written in the same second as
  the step completed would not trigger the warning
- mtime can be spoofed by `touch` or restored by `rsync`
- Does not protect against programmatic edits that preserve mtime

Risk: HIGH. The failure mode is silent incorrect routing. A warning that can
be ignored provides false assurance.

**Implementation complexity estimate**

~8 lines new code in executor.py + 2-3 sentences in §8.2.

**v2.25 vs. v2.26 recommendation**

Defer to v2.26 as a fallback if Approach A3 is rejected. Do not use as the
primary mitigation because the failure mode is silent.

---

#### Approach C: Input hash tracking for all step inputs

**Mechanical Description**

Extend the executor pattern: after every step completes, the executor injects
an `input_hash` frontmatter field into the output file. The `input_hash` is
the SHA-256 of the concatenation (or XOR-combine) of all input file hashes.
During `_apply_resume()`, before skipping any step, the executor recomputes
the input hashes and compares against the stored `input_hash`. If the hashes
differ, the step is re-run.

For `annotate-deviations`, inputs are: `spec_file`, `roadmap.md`,
`debate-transcript.md`, `diff-analysis.md`. The `input_hash` would be
`sha256(sha256(spec_file) + sha256(roadmap.md) + sha256(debate.md) + sha256(diff.md))`.

```python
def _compute_input_hash(input_paths: list[Path]) -> str:
    """Compute combined SHA-256 of all step inputs."""
    combined = hashlib.sha256()
    for p in sorted(str(p) for p in input_paths):  # sort for determinism
        if Path(p).exists():
            combined.update(hashlib.sha256(Path(p).read_bytes()).digest())
    return combined.hexdigest()

def _inject_input_hash(output_file: Path, input_paths: list[Path]) -> None:
    """Inject input_hash into output frontmatter post-subprocess."""
    ...  # same pattern as _inject_pipeline_diagnostics
```

During `_apply_resume()`:
```python
for step in steps_that_would_be_skipped:
    stored_hash = _read_input_hash(step.output_file)
    current_hash = _compute_input_hash(step.inputs)
    if stored_hash != current_hash:
        # Re-queue step
        pass
```

**Scope question**

If applied only to `annotate-deviations`, this is ~60 lines of targeted code.
If applied to all steps, this becomes a generic mechanism requiring modification
of `roadmap_run_step()`, `_apply_resume()`, and potentially the `Step` dataclass
to carry `inputs` in a way that `_apply_resume()` can access. The Step dataclass
already has an `inputs` field, so the data is available.

Applied to all 10+ steps, the implementation cost is ~120 lines and the runtime
cost is O(N * avg_file_size) additional hashing on every `--resume` invocation.
For a pipeline with 200KB input files per step, this is negligible.

The deeper concern is correctness: for parallel steps (generate-A, generate-B),
both steps share the same inputs (extraction). If extraction changes, both
parallel steps would correctly be re-queued. The logic handles this correctly
because each step's `input_hash` is independent.

**Tradeoffs**

Pros:
- Comprehensive: catches all stale-input scenarios, not just roadmap.md
- Generalizes cleanly across the pipeline
- No changes to gate system or models

Cons:
- Higher implementation scope than targeted fix
- `_inject_input_hash()` must be called in `roadmap_run_step()` after
  `_sanitize_output()`, adding a new post-subprocess hook to an already
  growing function
- If the LLM-generated output already contains an `input_hash` field (unlikely
  but possible if the prompt leaks), the injection silently overwrites it
- Requires `Step.inputs` to be populated accurately for all steps; current
  `_build_steps()` code is correct but any future step that omits `inputs`
  would silently skip the check

**Implementation complexity estimate**

Targeted (annotate-deviations only): ~60 lines, executor.py only
Generic (all steps): ~120 lines, executor.py + potential Step model review

**v2.25 vs. v2.26 recommendation**

Targeted version for `annotate-deviations` only: acceptable for v2.25 but
overlaps with Approach A3. Generic version: defer to v2.26 as a pipeline-wide
robustness initiative.

---

### Recommended Approach

**Approach A, Sub-approach A3** (pre-gate validation hook in `_apply_resume()`).

Rationale:
1. Achieves the detection goal: if roadmap.md changed since annotate-deviations
   ran, the step is re-queued on `--resume`
2. Zero impact on gate architecture, NFR-010 compliance maintained
3. Executor-local change — one new helper function, ~35 lines
4. Requires `roadmap_hash` to be written into `spec-deviations.md` frontmatter
   by the executor (not the LLM), which is safe and precise

The `roadmap_hash` injection uses the same executor-writes-hash pattern already
established for `spec_hash` in `_save_state()`.

---

### Draft Spec Language

**Insert into §3.2 (Step Construction in `_build_steps()`) after existing FR-004:**

> **FR-055**: After the `annotate-deviations` subprocess completes and
> `_sanitize_output()` runs, the executor SHALL inject a `roadmap_hash` field
> into `spec-deviations.md` frontmatter containing the SHA-256 hex digest of
> `roadmap.md` at the time of injection (same atomic-write pattern as
> `_inject_pipeline_diagnostics()`).
>
> Implementation:
> ```python
> # In roadmap_run_step(), after _sanitize_output():
> if step.id == "annotate-deviations" and step.output_file.exists():
>     _inject_roadmap_hash(step.output_file, config.output_dir / "roadmap.md")
> ```
>
> `_inject_roadmap_hash(output_file, roadmap_path)` reads the current
> frontmatter, adds or overwrites `roadmap_hash: <sha256>`, and writes
> atomically via `.tmp` + `os.replace()`.

**Insert into §3.5 (Gate Definition) after existing FR-013:**

> **FR-056**: The `ANNOTATE_DEVIATIONS_GATE` required frontmatter fields SHALL
> include `roadmap_hash`. A missing or empty `roadmap_hash` field SHALL cause
> the STANDARD gate to fail on structural completeness grounds (existing
> frontmatter field check behavior).

**Insert into §8.2 (Impact of v5 Changes on Resume) after existing FR-038 prose:**

> **FR-057**: `_apply_resume()` SHALL call
> `_check_annotate_deviations_freshness(config, deviations_file)` before
> deciding to skip the `annotate-deviations` step. If the function returns
> `False` (meaning `roadmap_hash` in `spec-deviations.md` does not match the
> current SHA-256 of `roadmap.md`), the step SHALL be re-added to the execution
> queue regardless of whether the STANDARD gate would otherwise pass.
>
> ```python
> def _check_annotate_deviations_freshness(
>     config: RoadmapConfig,
>     deviations_file: Path,
> ) -> bool:
>     """Returns True if spec-deviations.md is fresh for current roadmap.md.
>
>     Returns False if:
>     - spec-deviations.md does not exist
>     - roadmap_hash field is missing or empty
>     - roadmap.md does not exist
>     - SHA-256 of roadmap.md does not match stored roadmap_hash
>     """
>     if not deviations_file.exists():
>         return False
>     content = deviations_file.read_text(encoding="utf-8")
>     fm = _parse_frontmatter(content)
>     if fm is None:
>         return False
>     stored_hash = fm.get("roadmap_hash", "")
>     if not stored_hash:
>         return False
>     merge_file = config.output_dir / "roadmap.md"
>     if not merge_file.exists():
>         return False
>     current_hash = hashlib.sha256(merge_file.read_bytes()).hexdigest()
>     return stored_hash == current_hash
> ```
>
> **NFR-011**: `_check_annotate_deviations_freshness()` SHALL be fail-closed:
> any missing file, missing field, or read error SHALL cause it to return
> `False` (force re-run), not skip. It SHALL NOT raise exceptions.

---

## ISSUE 2 (W-ADV-4, MAJOR): Non-integer `remediation_attempts` crashes `_check_remediation_budget()`

### Problem Restatement

`_check_remediation_budget()` reads `remediation_attempts` from
`.roadmap-state.json` via `remediate.get("remediation_attempts", 0)` and
then compares the result with `>=`. If `.roadmap-state.json` contains
`"remediation_attempts": "two"` (a string), `"remediation_attempts": null`
(JSON null, Python `None`), or any non-integer value, the expression
`attempts >= max_attempts` raises `TypeError: '>=' not supported between
instances of 'str' and 'int'`. This exception is not caught anywhere in the
call stack visible in `executor.py`. The pipeline crashes with an uncaught
exception rather than a controlled halt, losing the diagnostic halt message
and the `sys.exit(1)` contract.

The state file is normally written by `_save_state()` which sets
`remediate_metadata["remediation_attempts"] = existing_attempts + 1` where
`existing_attempts` comes from `existing_remediate.get("remediation_attempts", 0)`.
If `existing_attempts` is already corrupt, this addition also raises TypeError.
External tampering (manual edit, concurrent process, filesystem corruption) is
the most likely cause.

---

### Approaches Considered

#### Approach A: `int()` coercion with fallback in `_check_remediation_budget()`

**Mechanical Description**

Add a defensive coercion at the point of use:

```python
def _check_remediation_budget(config: RoadmapConfig, max_attempts: int = 2) -> bool:
    state_file = config.output_dir / ".roadmap-state.json"
    state = read_state(state_file)
    if state is None:
        return True

    remediate = state.get("remediate")
    if remediate is None:
        return True

    raw = remediate.get("remediation_attempts", 0)
    try:
        attempts = int(raw)
    except (ValueError, TypeError):
        _log.warning(
            "remediation_attempts value %r is not a valid integer; "
            "treating as 0 (fresh budget). State file may be corrupt.",
            raw,
        )
        attempts = 0

    if attempts >= max_attempts:
        _print_terminal_halt(config, state)
        return False

    return True
```

The spec question is: should treating corruption as `attempts = 0` (fresh
budget, allowing another attempt) be the correct behavior? The alternative is
treating it as `attempts = max_attempts` (block immediately on corruption).

Arguments for `attempts = 0` (fresh budget):
- Corruption is almost certainly external; the legitimate pipeline did not
  make `max_attempts` attempts
- Crashing on corruption is worse than allowing one more attempt
- The subsequent write by `_save_state()` will restore a valid integer

Arguments for `attempts = max_attempts` (block on corruption):
- Fail-closed is safer: if the state is corrupt, we cannot trust any of it
- Resetting to 0 on corruption could theoretically allow infinite retries
  if an external process keeps corrupting the field

The `attempts = 0` behavior is more operationally forgiving and is correct
for the common case. The `attempts = max_attempts` behavior is safer against
adversarial state manipulation but unnecessarily punishes users whose files
were corrupted by filesystem issues.

Recommendation: `attempts = 0` with a WARNING log. The warning gives operators
visibility without crashing the pipeline.

**Tradeoffs**

Pros:
- Minimal change (~8 lines), contained to one function
- No spec schema changes needed
- Logging provides observability for the corruption
- Correct for the common case (filesystem error, manual edit typo)

Cons:
- Does not prevent corruption in `_save_state()` itself if `existing_attempts`
  is already corrupt when the addition happens
- Does not validate the state file schema holistically

**Implementation complexity estimate**

~8 lines in executor.py. 1 new FR.

**v2.25 recommendation**: Include in v2.25. This is a one-line behavioral
defect with a clean targeted fix.

---

#### Approach B: Validation in `_save_state()` — enforce integer on write

**Mechanical Description**

`_save_state()` already controls what it writes to `remediation_attempts`:

```python
# Current code in _save_state():
existing_attempts = existing_remediate.get("remediation_attempts", 0)
remediate_metadata["remediation_attempts"] = existing_attempts + 1
```

Add a defensive cast here as well:

```python
try:
    existing_attempts = int(existing_remediate.get("remediation_attempts", 0))
except (ValueError, TypeError):
    _log.warning(
        "Corrupt remediation_attempts in state; resetting to 0 before increment."
    )
    existing_attempts = 0
remediate_metadata["remediation_attempts"] = existing_attempts + 1
```

Since `_save_state()` always writes Python `int` values (the result of
`existing_attempts + 1`), the resulting JSON will always have a valid integer.
Corruption can therefore only arise from external tampering between writes.

Is Approach B alone sufficient? No. `_save_state()` protects the write path,
but if `.roadmap-state.json` is externally modified between the write and the
next `_check_remediation_budget()` read, corruption still reaches the budget
check. Approach B is defense-in-depth on the write path; Approach A is defense
on the read path. Both together are correct.

**Tradeoffs**

Pros:
- Prevents corruption propagation from one write to the next
- Keeps `_save_state()` self-consistent

Cons:
- Does not protect the read path in `_check_remediation_budget()`
- Concurrent processes can still corrupt the file between writes

**Implementation complexity estimate**

~6 lines in `_save_state()`. 1 new NFR.

**v2.25 recommendation**: Include in v2.25 as complement to Approach A.

---

#### Approach C: JSON schema validation for `.roadmap-state.json`

**Mechanical Description**

Define a JSON schema for the state file and validate on every read in
`read_state()`:

```python
_STATE_SCHEMA = {
    "type": "object",
    "properties": {
        "schema_version": {"type": "integer"},
        "spec_hash": {"type": "string"},
        "remediate": {
            "type": "object",
            "properties": {
                "remediation_attempts": {"type": "integer", "minimum": 0},
            },
        },
    },
}

def read_state(path: Path) -> dict | None:
    ...
    state = json.loads(text)
    try:
        import jsonschema
        jsonschema.validate(state, _STATE_SCHEMA)
    except jsonschema.ValidationError as exc:
        _log.warning("State file schema validation failed: %s", exc.message)
        # Repair: reset remediation_attempts if invalid
        if "remediate" in state:
            raw = state["remediate"].get("remediation_attempts")
            if not isinstance(raw, int):
                state["remediate"]["remediation_attempts"] = 0
    return state
```

This adds `jsonschema` as a runtime dependency or requires Python's
`jsonschema`-free validation. The `jsonschema` library is not currently a
dependency of `superclaude` (`pyproject.toml` lists only `pytest`, `click`,
`rich`). Adding it solely for state file validation is disproportionate.

An alternative is inline type validation without the library:

```python
def _validate_state(state: dict) -> dict:
    """Repair known-invalid fields in state dict. Returns repaired state."""
    remediate = state.get("remediate")
    if remediate is not None:
        raw = remediate.get("remediation_attempts")
        if raw is not None and not isinstance(raw, int):
            _log.warning(
                "remediation_attempts is %r (not int), resetting to 0", raw
            )
            remediate["remediation_attempts"] = 0
    return state
```

Called from `read_state()` after parsing. This is effectively Approach A+B
done at the read layer with explicit type checking.

**Tradeoffs**

Pros:
- Comprehensive: catches any schema violation, not just `remediation_attempts`
- Creates a clear maintenance target (the schema definition)

Cons:
- If using `jsonschema` library: new dependency, pip install required, version
  pinning maintenance overhead
- If inline validation: equivalent to Approach A at the `read_state()` layer,
  not meaningfully different
- Schema maintenance: every new state field requires schema update or the
  schema becomes a maintenance liability
- The state file is not a public API; over-specifying its schema reduces future
  flexibility

**Implementation complexity estimate**

With `jsonschema`: ~30 lines + new dependency
Inline validation: ~20 lines in executor.py, 1 new NFR

**v2.25 recommendation**: Defer full schema validation to v2.26. The inline
repair approach (without `jsonschema`) is acceptable for v2.25 but duplicates
Approach A. Use Approach A + B for v2.25 and defer formal schema definition.

---

### Recommended Approach

**Combined Approach A + B** for v2.25.

- Approach A: defensive `int()` coercion + warning log in `_check_remediation_budget()`
- Approach B: defensive `int()` coercion in `_save_state()` read path

Together these cover both the read and write paths. Implementation cost is
~14 lines total. No new dependencies. No schema changes.

---

### Draft Spec Language

**Insert into §8.4 (Remediation Cycle Bounding) after existing FR-041:**

> **FR-058**: `_check_remediation_budget()` SHALL coerce `remediation_attempts`
> to `int` before comparison. If the coercion raises `ValueError` or
> `TypeError`, the function SHALL log a WARNING and treat `remediation_attempts`
> as `0` (fresh budget), allowing the current attempt to proceed.
>
> ```python
> raw = remediate.get("remediation_attempts", 0)
> try:
>     attempts = int(raw)
> except (ValueError, TypeError):
>     _log.warning(
>         "remediation_attempts value %r is not a valid integer in "
>         ".roadmap-state.json; treating as 0. State file may be corrupt.",
>         raw,
>     )
>     attempts = 0
> ```
>
> **Rationale**: External tampering or filesystem corruption may produce
> non-integer values. An uncaught TypeError crashing the pipeline is a worse
> outcome than allowing one more attempt. The WARNING log provides observability.

> **NFR-012**: `_save_state()` SHALL coerce `existing_attempts` to `int`
> before incrementing, using `try: int(...) except (ValueError, TypeError): 0`.
> This ensures that `remediation_attempts` is always written as a Python `int`
> to `.roadmap-state.json`, preventing corruption propagation across write
> cycles.

---

## ISSUE 3 (W-ADV-3, MAJOR): Deviation ID format not constrained — comma in ID corrupts routing

### Problem Restatement

The v5 spec mandates comma-separated routing fields in `deviation-analysis.md`
frontmatter (FR-045): `routing_fix_roadmap: DEV-002,DEV-003`. The
`deviations_to_findings()` function parses this field via `_parse_routing_list()`
which splits on commas. If an LLM-generated deviation ID contains a comma —
e.g., `DEV-002,alt` or `"module X, function Y"` used as an ID — the split
produces `["DEV-002", "alt"]` or `["\"module X", " function Y\""]`. The
non-conforming tokens are silently looked up in `fidelity_deviations.get(token)`,
return `None`, and are skipped with `continue`. The actual deviation
`DEV-002,alt` is never routed to remediation. This is silent data loss, not an
error.

The spec currently has no constraint on what constitutes a valid deviation ID.
`spec-fidelity.md` generates IDs like `DEV-001`, `DEV-002` etc., but nothing
in the spec or gate system enforces this format.

---

### Approaches Considered

#### Approach A: Constrain deviation ID format with regex validation in `_parse_routing_list()`

**Mechanical Description**

Add a formal FR constraining deviation IDs to the pattern `DEV-\d+` (e.g.,
DEV-001, DEV-042). This pattern is already used in existing examples throughout
the spec. Validation is enforced at parse time in `_parse_routing_list()`:

```python
import re
_DEVIATION_ID_PATTERN = re.compile(r'^DEV-\d+$')

def _parse_routing_list(content: str, field_name: str) -> list[str]:
    """Parse a comma-separated routing field from deviation-analysis.md frontmatter.

    Returns only tokens that match DEV-\\d+. Non-conforming tokens are
    logged as warnings and excluded.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return []
    raw = fm.get(field_name, "")
    if not raw.strip():
        return []

    tokens = [t.strip() for t in raw.split(",")]
    valid: list[str] = []
    for token in tokens:
        if not token:
            continue
        if _DEVIATION_ID_PATTERN.match(token):
            valid.append(token)
        else:
            _log.warning(
                "Routing field '%s' contains non-conforming token %r "
                "(expected DEV-\\d+); excluding from routing.",
                field_name,
                token,
            )
    return valid
```

**Gate-level enforcement**

The `DEVIATION_ANALYSIS_GATE` could additionally verify that all IDs in
routing fields are valid. This requires a new semantic check function that
parses the routing fields and validates each token. The function signature
`(content: str) -> bool` is compatible without closures because the field
names are known constants.

```python
def _routing_ids_valid(content: str) -> bool:
    """All deviation IDs in routing fields match DEV-\\d+."""
    import re
    fm = _parse_frontmatter(content)
    if fm is None:
        return False
    pattern = re.compile(r'^DEV-\d+$')
    routing_fields = [
        "routing_fix_roadmap", "routing_update_spec",
        "routing_no_action", "routing_human_review",
    ]
    for field in routing_fields:
        raw = fm.get(field, "")
        if not raw.strip():
            continue
        for token in raw.split(","):
            token = token.strip()
            if token and not pattern.match(token):
                return False
    return True
```

Registered on `DEVIATION_ANALYSIS_GATE` as a new semantic check.

**Tradeoffs**

Pros:
- Both prevents and detects the problem: validation in the gate blocks
  malformed output; defensive parsing in `_parse_routing_list()` is defense
  in depth for any future gate bypass
- Pure functions, no closure needed, fits existing gates.py architecture
- Zero breaking change to existing valid outputs (all existing examples use
  `DEV-NNN` format)

Cons:
- If the spec-fidelity LLM generates non-conforming IDs (e.g., `F-001`,
  `DEV-001a`), the STRICT gate blocks and the user must manually re-run. This
  is arguably correct behavior
- The regex `^DEV-\d+$` does not allow zero-padded variants like DEV-1 vs
  DEV-001; both are valid matches but they are distinct strings

**Implementation complexity estimate**

~25 lines in executor.py (`_parse_routing_list()` modification) + ~20 lines in
gates.py (`_routing_ids_valid()` + gate registration). 2 new FRs.

**v2.25 recommendation**: Include in v2.25.

---

#### Approach B: Change separator from comma to semicolon

**Mechanical Description**

All routing frontmatter fields use semicolons instead of commas:
`routing_fix_roadmap: DEV-002;DEV-003`. Semicolons are far less likely to
appear naturally in any LLM-generated ID, name, or description.

Breaking change assessment: yes, this is a breaking change to the spec examples.
Every location where the comma-separated format is specified must be updated:

- §5.4 output format example: `routing_fix_roadmap: DEV-002,DEV-003` (line
  in the merged spec with this exact value)
- FR-045: "flat frontmatter fields ... comma-separated deviation IDs"
- FR-046: gate fields description (text mentions the format)
- `deviations_to_findings()` code example: `_parse_routing_list(da_content, "routing_fix_roadmap")`
- Appendix B gate definitions table

`_parse_frontmatter()` does not need changes: it splits on the first `:` per
line, returning the rest as a string. The caller (`_parse_routing_list()`)
then splits on the separator. Only `_parse_routing_list()` needs a change from
`raw.split(",")` to `raw.split(";")`.

**Tradeoffs**

Pros:
- Eliminates the comma-in-ID risk at the format level, not the validation level
- Semicolons are not special characters in YAML values (unlike commas, which
  are also harmless in YAML string values but look natural in text)
- One-line change to `_parse_routing_list()`

Cons:
- Breaking change to all spec examples (7-10 locations)
- If LLM-generated IDs ever contain semicolons (unlikely but possible in
  free-text IDs), the problem recurs
- Does not actually constrain what constitutes a valid deviation ID — the root
  cause is unconstrained IDs, not the separator choice
- Changes examples in a way that makes spec text harder to read (semicolons
  look unusual in frontmatter context)

**Implementation complexity estimate**

~1 line in `_parse_routing_list()` + updates to ~8 spec locations. 1 modified FR.

**v2.25 recommendation**: Do not adopt as primary fix. The separator is
cosmetic; Approach A addresses the root cause. Could be combined with Approach
A as an additional defense.

---

#### Approach C: Space-separated format

**Mechanical Description**

`routing_fix_roadmap: DEV-002 DEV-003`. Parsing uses `str.split()` (no
argument), which splits on any whitespace and strips leading/trailing
whitespace automatically.

```python
# In _parse_routing_list():
tokens = raw.split()   # was raw.split(",")
```

`str.split()` behavior vs `split(',')`:
- `"DEV-002 DEV-003".split()` → `["DEV-002", "DEV-003"]` (correct)
- `"DEV-002  DEV-003".split()` → `["DEV-002", "DEV-003"]` (handles extra spaces)
- `"DEV-002, DEV-003".split(",")` → `["DEV-002", " DEV-003"]` (requires strip)
- `"".split()` → `[]` (correct empty case)

Current `_parse_frontmatter()` does `value.strip()` after splitting on `:`,
so leading/trailing whitespace in the value is already removed. Internal
whitespace within the value is preserved, so `DEV-002 DEV-003` would be
returned as the string `"DEV-002 DEV-003"` from `_parse_frontmatter()` —
correct for space-splitting.

Structural IDs `DEV-NNN` cannot contain spaces (they are machine-generated
from a pattern). The space separator is therefore the safest possible choice:
no valid ID can corrupt the separator.

**Tradeoffs**

Pros:
- Cleanest parsing: `str.split()` is idiomatic and handles edge cases correctly
- No valid DEV-NNN ID can contain a space
- One-line change to `_parse_routing_list()`

Cons:
- Same breaking-change issue as Approach B (all spec examples must be updated)
- YAML frontmatter with space-separated values looks unusual: `routing_fix_roadmap: DEV-002 DEV-003`
  could be misread as a tag or multi-value
- Still does not constrain ID format at the spec level

**Implementation complexity estimate**

~1 line in `_parse_routing_list()` + updates to ~8 spec locations. 1 modified FR.

**v2.25 recommendation**: Do not adopt as primary fix. Approach A is more
principled.

---

#### Approach D: Validation in `_parse_routing_list()` with slip_count cross-check

**Mechanical Description**

After parsing and filtering tokens, cross-check the `fix_roadmap` list length
against the `slip_count` frontmatter field. If `len(fix_ids) != slip_count`,
emit a warning (not a hard error — `fix_roadmap` may legitimately include both
SLIPs and INTENTIONAL-preference deviations, which would exceed `slip_count`).
The more precise cross-check is `len(fix_ids) <= total_analyzed` (cannot route
more IDs than were analyzed).

```python
def _parse_routing_list(content: str, field_name: str) -> list[str]:
    # ... parse and validate tokens against DEV-\d+ pattern ...
    valid = [t for t in tokens if _DEVIATION_ID_PATTERN.match(t)]

    # Cross-check against total_analyzed
    fm = _parse_frontmatter(content)
    if fm is not None:
        try:
            total = int(fm.get("total_analyzed", 0))
            if len(valid) > total:
                _log.warning(
                    "routing field '%s' has %d IDs but total_analyzed=%d; "
                    "possible duplication or parse error.",
                    field_name, len(valid), total,
                )
        except (ValueError, TypeError):
            pass

    return valid
```

The `slip_count` cross-check specifically: `len(fix_ids) == slip_count` is
NOT a valid invariant because `fix_roadmap` also receives
INTENTIONAL-preference deviations (FR-022). Only `slip_count + intentional_preference_count`
would equal `len(fix_ids)`. The spec does not require frontmatter to separately
count INTENTIONAL-preference items. Therefore the cross-check against
`total_analyzed` is the only safe bound.

**Tradeoffs**

Pros:
- Detects obvious parse errors (more IDs than were analyzed)
- Complementary to regex validation; adds a numeric sanity check

Cons:
- Warning only — does not block incorrect routing
- `slip_count` cross-check is not a valid invariant (as analyzed above)
- Adds complexity to what should be a simple parse function

**Implementation complexity estimate**

~20 lines in executor.py (within `_parse_routing_list()`). 1 new NFR.

**v2.25 recommendation**: Include as complement to Approach A, implemented
as the warning-only cross-check against `total_analyzed`.

---

### Recommended Approach

**Approach A** (constrained ID format + validation in `_parse_routing_list()`
+ `_routing_ids_valid()` semantic check on `DEVIATION_ANALYSIS_GATE`), with the
`total_analyzed` cross-check from Approach D as a warning.

This is the only approach that addresses the root cause (unconstrained ID
format) rather than the symptom (comma as separator). Routing corruption is
prevented at two layers: the STRICT gate blocks non-conforming output from
reaching `deviations_to_findings()`, and `_parse_routing_list()` defensively
filters any tokens that bypass the gate.

---

### Draft Spec Language

**Insert into §5.4 (Output Format: `deviation-analysis.md`) after existing FR-024:**

> **FR-059**: Deviation IDs in `deviation-analysis.md` SHALL match the pattern
> `DEV-\d+` (e.g., DEV-001, DEV-042). The prompt for `deviation-analysis`
> SHALL instruct the agent to use only deviation IDs as they appear in
> `spec-fidelity.md`, which generates IDs in the `DEV-NNN` format.

**Insert into §5.5 (Gate Definition) after existing FR-026:**

> **FR-060**: A `_routing_ids_valid(content: str) -> bool` semantic check
> function SHALL be added to `gates.py`. The function SHALL:
> 1. Parse the frontmatter of `deviation-analysis.md`
> 2. For each of the four routing fields (`routing_fix_roadmap`,
>    `routing_update_spec`, `routing_no_action`, `routing_human_review`),
>    split the value on commas and validate each non-empty token against
>    `re.compile(r'^DEV-\d+$')`
> 3. Return `False` if any token fails validation; return `True` if all tokens
>    are valid or all routing fields are empty
>
> This check SHALL be registered as a STRICT semantic check on
> `DEVIATION_ANALYSIS_GATE`.

**Modify §7.2 (`deviations_to_findings()`) to add after the `_parse_routing_list()` call:**

> **FR-061**: `_parse_routing_list()` SHALL validate each token against
> `re.compile(r'^DEV-\d+$')`. Non-conforming tokens SHALL be logged as
> WARNING and excluded from the returned list. An empty string token (from
> trailing comma or empty field) SHALL be silently skipped without logging.
>
> Additionally, `_parse_routing_list()` SHALL cross-check `len(returned_tokens)`
> against the `total_analyzed` frontmatter field. If `len(returned_tokens) >
> total_analyzed`, a WARNING SHALL be logged (routing more IDs than were analyzed
> suggests a parse error or duplicate IDs).

---

## ISSUE 4 (N-2 extended, MAJOR): Two independent retry counters with no coordination spec

### Problem Restatement

The v5 pipeline contains two distinct retry mechanisms:

1. `_spec_patch_cycle_count` — a local variable in `execute_roadmap()`,
   per-invocation, maximum 1 cycle. Triggers when spec-fidelity fails STRICT
   AND qualifying deviation files exist with mtime > fidelity started_at AND
   the spec file hash changed since run started.

2. `remediation_attempts` — persisted in `.roadmap-state.json`, maximum 2
   attempts. Triggers on certify FAIL and is checked by
   `_check_remediation_budget()` on each `--resume`.

These mechanisms are completely independent. If both fire in the same pipeline
lifetime, the total recovery attempts can reach 3 (1 spec-patch + 2 remediation).
The spec documents each counter in isolation but does not specify:
- What happens if spec-patch fires and the resumed pipeline then exhausts
  remediation budget
- Whether `_print_terminal_halt()` should differentiate "remediation exhausted"
  from "spec-patch cycle + remediation exhausted"
- Whether there is a global cap on total recovery attempts

Furthermore, with spec-fidelity downgraded to STANDARD in v5, the
`_spec_patch_cycle_count` mechanism is effectively dormant: it triggers only
on STRICT gate failures at the spec-fidelity step, but spec-fidelity is now
STANDARD. The trigger condition `spec_fidelity_failed` in `execute_roadmap()`
checks `r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)` — a STANDARD gate
failure would still register as FAIL and could in principle trigger the
spec-patch cycle. This creates an ambiguity: is the spec-patch cycle intended
to be active in v5?

---

### Approaches Considered

#### Approach A: §8.7 "Retry Budget Summary" documentation only

**Mechanical Description**

Add a new §8.7 to the spec with a comprehensive table of all retry mechanisms
and prose explaining their independence. No code changes.

Proposed §8.7 content:

> ### 8.7 Retry Budget Summary
>
> The v5 pipeline contains two independent retry mechanisms. They operate on
> different triggers, different storage, and different failure modes. This
> section documents their combined behavior.
>
> | Counter | Type | Max | Storage | Trigger Condition | Trigger Gate |
> |---------|------|-----|---------|-------------------|--------------|
> | `_spec_patch_cycle_count` | in-memory | 1 per invocation | local variable in `execute_roadmap()` | spec-fidelity FAIL AND qualifying deviation files AND spec hash change | STANDARD (v5) |
> | `remediation_attempts` | persisted | 2 | `.roadmap-state.json` → `remediate.remediation_attempts` | certify FAIL on `--resume` | STRICT (`CERTIFY_GATE`) |
>
> **Combined behavior**: If both mechanisms fire within the same pipeline
> lifetime, the total automatic recovery attempts may reach 3. This is by
> design: spec-patch addresses a different failure mode (spec changed mid-run)
> than remediation (SLIP fixes failed certification).
>
> **Dormancy in v5**: The spec-patch cycle (`_spec_patch_cycle_count`) was
> designed for a STRICT spec-fidelity gate. With spec-fidelity downgraded to
> STANDARD in v5 (FR-014), the cycle's trigger condition (spec-fidelity FAIL)
> can still fire on STANDARD gate failure. In practice, STANDARD failures are
> rare (they require missing frontmatter, not high deviation counts). The
> spec-patch cycle is retained for backward compatibility with v2.24.x
> deployments that may still encounter STANDARD failures.
>
> **Independence**: These counters do not communicate. If the spec-patch cycle
> completes (cycle_count reaches 1) and remediation subsequently exhausts its
> budget (remediation_attempts reaches 2), `_print_terminal_halt()` fires with
> the remediation-exhausted message. The terminal halt message does not
> currently indicate whether a spec-patch cycle also occurred.

**Tradeoffs**

Pros:
- Zero implementation cost
- Correct documentation of existing behavior
- Prevents future implementers from misunderstanding the interaction

Cons:
- Does not change behavior, only documents it
- If the combined behavior is actually wrong (e.g., allowing 3 attempts is too
  many), documentation alone does not fix it
- The dormancy note may create confusion: "why document a mechanism that
  barely fires?"

**Implementation complexity estimate**

~300 words of spec text, zero code changes.

**v2.25 recommendation**: Include in v2.25. Documentation alone is sufficient
for a low-risk interaction that is unlikely to fire in practice.

---

#### Approach B: Global pipeline retry budget — `total_recovery_attempts` counter

**Mechanical Description**

Add a `total_recovery_attempts` field to `.roadmap-state.json`. Every recovery
attempt (spec-patch or remediation) increments it. A global cap (e.g., 3)
triggers `_print_terminal_halt()` regardless of which counter reached it first.

```python
# In .roadmap-state.json schema:
{
  "total_recovery_attempts": 0,   # NEW: incremented on any recovery
  "remediate": {
    "remediation_attempts": 1,    # existing
    ...
  }
}

# In execute_roadmap(), when spec-patch cycle fires:
_save_total_recovery_attempts(config, increment=1)

# In _check_remediation_budget():
total = state.get("total_recovery_attempts", 0)
if total >= GLOBAL_MAX_RECOVERY:
    _print_terminal_halt(config, state, reason="global_budget_exhausted")
    return False
```

Questions:
- What is the global max? 3 seems reasonable (1 spec-patch + 2 remediation).
  But if spec-patch does not fire, remediation gets 2 attempts — correct. If
  spec-patch fires, remediation gets 2 attempts — correct. The global cap of 3
  does not actually prevent any case that the independent caps would not already
  prevent.
- What happens if `.roadmap-state.json` is reset between invocations? The
  counter resets to 0, allowing another full cycle. This could happen if the
  user deletes the state file (intentional) or if the state file is corrupted.
  In both cases, reset is the correct behavior.
- Is this over-engineering? Yes. The existing independent caps already bound
  the total to at most 3 attempts. A global cap that is equal to the sum of
  independent caps adds no additional protection.

**Tradeoffs**

Pros:
- Provides explicit global budget enforcement
- Makes the "at most 3 attempts total" invariant testable

Cons:
- Over-engineering: the global cap is numerically equal to the sum of
  independent caps, providing no additional constraint
- Adds state schema complexity
- `total_recovery_attempts` incrementing from the spec-patch path requires
  `execute_roadmap()` to call `_save_state()` mid-execution, which currently
  only happens at the end of each pipeline run — this is a structural change
- If the global cap is set lower than the sum of independent caps (e.g., 2),
  it artificially restricts the spec-patch + remediation combined scenario in
  a non-obvious way

**Implementation complexity estimate**

~50 lines across executor.py + state schema update + 2 new FRs.

**v2.25 recommendation**: Defer to v2.26. The global budget adds complexity
without meaningful additional protection given independent caps already exist.

---

#### Approach C: Explicit interaction rules in spec

**Mechanical Description**

Add to §8.4 (or a new §8.7): explicit prose describing what `_print_terminal_halt()`
outputs when both mechanisms have fired.

Modification to `_print_terminal_halt()`: check whether `_spec_patch_cycle_count`
was ever incremented. Since `_spec_patch_cycle_count` is a local variable in
`execute_roadmap()` and `_print_terminal_halt()` receives only `config` and
`state`, this information must be stored in the state file to be accessible.
Add a `spec_patch_attempted: bool` field to `.roadmap-state.json`:

```python
# After spec-patch cycle completes in execute_roadmap():
_flag_spec_patch_in_state(config)  # sets state["spec_patch_attempted"] = True

# In _print_terminal_halt():
spec_patch_attempted = state.get("spec_patch_attempted", False)
if spec_patch_attempted:
    lines.append(
        "  Note: A spec-patch auto-resume cycle also occurred during this run."
    )
    lines.append(
        "  Both the spec-patch cycle and the remediation budget are exhausted."
    )
```

This is a minimal enhancement: one boolean field in state, one additional
`print` statement in `_print_terminal_halt()`.

**Tradeoffs**

Pros:
- Improves diagnostic output when both mechanisms fire
- Targeted: one boolean field, 2-3 lines of terminal output
- No behavioral change, only improved observability

Cons:
- Requires state schema change (`spec_patch_attempted` field)
- `_flag_spec_patch_in_state()` must write to disk mid-execution (new write path)
- The scenario (both spec-patch AND remediation exhaust) is vanishingly rare in
  practice; the diagnostic value may not justify the implementation cost

**Implementation complexity estimate**

~30 lines in executor.py + 1 new state field. 1 new FR.

**v2.25 recommendation**: Include the spec text from Approach A (§8.7 table)
plus the interaction rule prose from Approach C, but defer the state schema
change and `_flag_spec_patch_in_state()` implementation to v2.26.

---

#### Approach D: Retire `_spec_patch_cycle_count` in v2.25 — document dormancy

**Mechanical Description**

With spec-fidelity downgraded to STANDARD, the spec-patch cycle's trigger
condition fires only on STANDARD gate failures (missing frontmatter, insufficient
line count). STANDARD failures at spec-fidelity are expected to be extremely
rare in a well-functioning pipeline. The cycle was designed for the STRICT gate
era (v2.24.x). In v5, deviation-analysis STRICT is the relevant blocking gate.

Add to §14 (Backward Compatibility) a note explicitly documenting the
spec-patch cycle's dormant status:

> ### 14.7 Spec-Patch Cycle Dormancy
>
> The `_apply_resume_after_spec_patch()` mechanism and `_spec_patch_cycle_count`
> counter were introduced in v2.24.2 to handle the case where a subprocess
> patched the spec file during a STRICT spec-fidelity failure. With
> spec-fidelity downgraded to STANDARD in v5 (FR-014), HIGH deviation counts
> no longer trigger a gate failure and the spec-patch cycle's trigger condition
> fires only on structural failures (missing frontmatter, insufficient content).
>
> The spec-patch cycle code is RETAINED but functionally dormant in v5. It is
> not removed because:
> 1. It imposes no runtime cost when inactive
> 2. It provides a backstop for unforeseen STANDARD gate failures at spec-fidelity
> 3. Removing it would break backward compatibility for v2.24.2 users on
>    `--resume` cycles already in progress
>
> Users who encounter unexpected spec-patch cycle activation in v5 should
> investigate whether `roadmap.md` is being modified by an external process
> during pipeline execution.

Retirement (removing the code) is explicitly NOT recommended. The mechanism is
harmless when dormant and provides a safety net.

Questions on retirement vs. keeping:
- Can we retire without breaking v2.24.2 users? Only if we also remove the
  trigger condition check in `execute_roadmap()`. Users with `.roadmap-state.json`
  from v2.24.2 runs that have `remediation_attempts` present would not be
  affected by removing the spec-patch cycle — that mechanism is separate.
- Is the trigger condition consistent with v5? The trigger fires on
  `spec_fidelity_failed = any(r.step.id == "spec-fidelity" and r.status in
  (FAIL, TIMEOUT))`. This condition is still reachable in v5 via STANDARD
  gate failure (frontmatter missing). Keeping the code is correct.

**Tradeoffs**

Pros:
- Prevents confusion in v2.25: clearly documents why the mechanism exists but
  rarely fires
- No code changes required
- Accurate spec that reflects actual runtime behavior

Cons:
- Does not resolve the underlying interaction question — just declares it
  "dormant" and moves on
- If the dormancy note is wrong (i.e., STANDARD failures at spec-fidelity do
  occur), it creates false confidence

**Implementation complexity estimate**

~200 words of spec text, zero code changes.

**v2.25 recommendation**: Include the dormancy note in §14. This is the most
honest description of the mechanism's v5 status.

---

### Recommended Approach

**Approach A** (§8.7 documentation table) **+ Approach D** (§14.7 dormancy note),
with the specific interaction rule from Approach C added to §8.7 prose without
implementing the state schema change.

Rationale:
- The interaction between the two counters is a documentation gap, not a
  behavioral defect: the independent caps already bound total attempts correctly
- A §8.7 table gives implementers and reviewers a clear reference
- The §14.7 dormancy note honestly documents the spec-patch cycle's reduced
  relevance in v5
- The Approach C interaction rule (what `_print_terminal_halt()` says when
  both fire) can be specified in the spec text without implementing the state
  change — making it a v2.26 implementation requirement

---

### Draft Spec Language

**New §8.7 to insert after §8.6:**

> ### 8.7 Retry Budget Summary and Counter Interaction
>
> The v5 pipeline contains two independent retry mechanisms. They operate on
> different triggers, different storage, and different failure modes.
>
> | Counter | Type | Max | Storage | Trigger | Effective in v5 |
> |---------|------|-----|---------|---------|-----------------|
> | `_spec_patch_cycle_count` | in-memory | 1 per invocation | local var in `execute_roadmap()` | spec-fidelity STANDARD FAIL + deviation files + spec hash change | Rarely (STANDARD gate failures are structural only) |
> | `remediation_attempts` | persisted | 2 | `.roadmap-state.json` | certify FAIL on `--resume` | Yes (primary recovery mechanism) |
>
> **FR-062**: The spec-patch cycle (`_spec_patch_cycle_count`) and the
> remediation budget (`remediation_attempts`) SHALL remain independent in v5.
> No global recovery budget counter is introduced.
>
> **FR-063**: If the spec-patch cycle completes (cycle_count reaches 1) and
> remediation subsequently exhausts its budget (remediation_attempts reaches 2),
> `_print_terminal_halt()` SHALL be called with the standard remediation-
> exhausted message. The message SHALL include a sentence noting that the
> pipeline attempted both automatic recovery mechanisms. The exact wording is:
>
> ```
> Note: A spec-patch auto-resume cycle also occurred before remediation began.
> Both recovery mechanisms are now exhausted. Manual intervention is required.
> ```
>
> Implementation of the "also occurred" note requires `_print_terminal_halt()`
> to receive information about spec-patch cycle history. The state file
> mechanism for this is deferred to v2.26 (see §14.7). For v2.25, this note
> is a specification-only requirement pending implementation.
>
> **NFR-013**: The combined maximum automatic recovery attempts in a single
> pipeline lifetime SHALL NOT exceed 3 (1 spec-patch + 2 remediation). This
> bound is enforced by the independent caps on each counter and requires no
> additional global counter.

**New §14.7 to insert after §14.6:**

> ### 14.7 Spec-Patch Cycle Dormancy in v5
>
> **NFR-014**: The `_apply_resume_after_spec_patch()` function and
> `_spec_patch_cycle_count` counter SHALL be retained unchanged in v5. They
> are not removed and not modified.
>
> With spec-fidelity downgraded to STANDARD in v5 (FR-014), the spec-patch
> cycle's trigger condition fires only when the STANDARD gate fails (missing
> frontmatter or insufficient line count at the spec-fidelity step). HIGH
> deviation count no longer triggers gate failure and therefore no longer
> triggers the spec-patch cycle. The mechanism is functionally dormant in the
> common pipeline path.
>
> The mechanism is retained because:
> 1. It imposes no runtime cost when inactive
> 2. It provides a backstop for unforeseen STANDARD gate failures
> 3. Removing it would require coordinated changes with v2.24.2 deployments
>
> Consumers of v2.25 who observe unexpected spec-patch cycle activation should
> investigate whether `spec-fidelity.md` is missing required frontmatter or
> whether `roadmap.md` is being modified by an external process during pipeline
> execution.

---

## Consolidated FR/NFR List

| Number | Type | Section | Summary | v2.25 or v2.26 |
|--------|------|---------|---------|----------------|
| FR-055 | FR | §3.2 | Executor injects `roadmap_hash` into `spec-deviations.md` frontmatter after subprocess completes | v2.25 |
| FR-056 | FR | §3.5 | `ANNOTATE_DEVIATIONS_GATE` required fields include `roadmap_hash` | v2.25 |
| FR-057 | FR | §8.2 | `_apply_resume()` calls `_check_annotate_deviations_freshness()` before skipping `annotate-deviations`; fail-closed | v2.25 |
| NFR-011 | NFR | §8.2 | `_check_annotate_deviations_freshness()` is fail-closed; missing file/field/error returns False (force re-run), never raises | v2.25 |
| FR-058 | FR | §8.4 | `_check_remediation_budget()` coerces `remediation_attempts` to `int`; logs WARNING on corrupt value; treats corruption as 0 | v2.25 |
| NFR-012 | NFR | §8.4 | `_save_state()` coerces `existing_attempts` to `int` before incrementing; `remediation_attempts` is always written as Python `int` | v2.25 |
| FR-059 | FR | §5.4 | Deviation IDs SHALL match `DEV-\d+`; prompt instructs agent to use only IDs as they appear in `spec-fidelity.md` | v2.25 |
| FR-060 | FR | §5.5 | `_routing_ids_valid(content: str) -> bool` added to `gates.py`; validates all routing field tokens against `^DEV-\d+$`; registered as STRICT check on `DEVIATION_ANALYSIS_GATE` | v2.25 |
| FR-061 | FR | §7.2 | `_parse_routing_list()` validates each token against `^DEV-\d+$`; warns and excludes non-conforming; cross-checks `len(returned_tokens) <= total_analyzed` | v2.25 |
| FR-062 | FR | §8.7 (new) | Spec-patch cycle and remediation budget remain independent; no global budget counter introduced | v2.25 (doc) |
| FR-063 | FR | §8.7 (new) | `_print_terminal_halt()` SHALL include spec-patch-also-fired note when both mechanisms are exhausted; state mechanism deferred to v2.26 | v2.26 (impl) |
| NFR-013 | NFR | §8.7 (new) | Combined max recovery attempts SHALL NOT exceed 3; enforced by independent caps | v2.25 (doc) |
| NFR-014 | NFR | §14.7 (new) | `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` SHALL be retained unchanged in v5; not removed | v2.25 (doc) |

---

## v2.25 vs. v2.26 Deferral Assessment

### Do in v2.25

**FR-055, FR-056, FR-057, NFR-011 (Issue 1 — roadmap hash stale detection)**

Rationale: The failure mode (stale `spec-deviations.md` silently feeds incorrect
routing to downstream steps) is a correctness defect with no workaround. If a
user edits `roadmap.md` and resumes, the pipeline produces wrong results without
warning. The implementation is ~35 lines in executor.py, one new helper function,
one new required frontmatter field. This is firmly within v2.25 scope alongside
the `annotate-deviations` step implementation.

Cost: low. Risk: very low. Value: high (prevents silent data corruption).

**FR-058, NFR-012 (Issue 2 — non-integer remediation_attempts)**

Rationale: This is a one-step crash defect with a targeted 14-line fix. It
crashes the pipeline with an uncaught exception rather than a controlled halt,
breaking the `sys.exit(1)` contract and losing diagnostic output. Fixing it
requires no architectural changes, no new dependencies, and no spec ambiguity.
This must be in v2.25.

Cost: minimal. Risk: zero. Value: high (correctness).

**FR-059, FR-060, FR-061 (Issue 3 — deviation ID format)**

Rationale: Comma in a deviation ID silently corrupts routing, causing SLIPs to
be skipped in remediation. The STRICT gate check (`FR-060`) prevents malformed
output from reaching `deviations_to_findings()`. The defensive parse filter
(`FR-061`) is defense in depth. Both are pure-function additions to `gates.py`
and executor.py. The `DEVIATION_ANALYSIS_GATE` is new in v2.25 and adding a
new semantic check during initial definition has zero migration cost.

Cost: low (~45 lines). Risk: very low. Value: high (prevents silent data loss).

**FR-062, NFR-013, NFR-014 (Issue 4 — counter interaction documentation)**

Rationale: The §8.7 table and §14.7 dormancy note are documentation-only
changes that cost minutes to add and prevent future implementers from
misunderstanding the retry architecture. Including them in v2.25 alongside the
counter implementation is the natural time to document them.

Cost: documentation only. Risk: zero. Value: medium (long-term maintainability).

### Defer to v2.26

**FR-063 implementation (Issue 4 — `_print_terminal_halt()` dual-mechanism note)**

Rationale: Implementing the "both mechanisms exhausted" note in
`_print_terminal_halt()` requires adding a `spec_patch_attempted` boolean to
`.roadmap-state.json` and a new write call mid-execution in `execute_roadmap()`.
This is disproportionate to the diagnostic value. The scenario (spec-patch fires
AND remediation exhausts) is extremely unlikely in a functioning v5 pipeline.
The spec text (FR-063) is included in v2.25 as a forward requirement; the
implementation is deferred.

Defer to v2.26 with the note "implement state schema extension for
`spec_patch_attempted` tracking."

**Approach C (Issue 1) — Generic input hash tracking for all steps**

Rationale: A pipeline-wide `input_hash` mechanism would provide comprehensive
staleness detection across all steps. For v2.25, the targeted `roadmap_hash`
approach (FR-055/FR-057) is sufficient and correct for the identified failure
mode. The generic mechanism is a v2.26 enhancement that would eliminate the
entire class of stale-artifact problems.

**Formal JSON schema for `.roadmap-state.json` (Issue 2, Approach C)**

Rationale: Schema validation with a library like `jsonschema` adds a runtime
dependency not currently in `pyproject.toml`. The inline coercions in
FR-058 and NFR-012 address the immediate defect without the dependency cost.
A formal schema definition would be appropriate in v2.26 when the state file
has stabilized and all fields from v2.25 are confirmed.

**Separator change (Issue 3, Approaches B/C)**

Rationale: Changing comma to semicolon or space is a cosmetic mitigation that
does not address the root cause (unconstrained ID format). FR-059's regex
constraint eliminates the root cause. The separator change adds a breaking
spec change (8+ locations to update) for no additional protection over Approach A.
Not recommended for any version unless Approach A proves insufficient.
