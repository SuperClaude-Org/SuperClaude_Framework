---
## ISSUE 1 (W-1, CRITICAL): Spec-Patch Cycle Silently Broken by STANDARD Downgrade

### Recommended Approach

**Approach A: Retire the spec-patch cycle.**

The fundamental justification: the spec-patch cycle existed to handle a world where spec-fidelity
STRICT was the only recovery mechanism and it was permanently blocked. v2.25 eliminates that world.
The deviation-analysis STRICT gate + bounded `--resume` remediation cycle is the new recovery path.
There is no scenario in v2.25 where the spec-patch auto-resume adds value that the new mechanisms
do not already provide. Retiring it removes ~130 lines of code, eliminates a subtle "two resume
mechanisms" mental model for implementors, and makes the spec internally consistent.

The `roadmap accept-spec-change` CLI command (`prompt_accept_spec_change()` in `spec_patch.py`)
is NOT retired — it remains useful as a manual operator tool for updating the spec hash after a
deliberate spec modification. Only the auto-triggering from within `execute_roadmap()` is retired.

### Draft Spec Language

**Insert as new §8.7 in §8 (Resume Logic Modifications)**:

---

#### 8.7 Spec-Patch Auto-Resume Cycle: Retirement

**FR-059**: As of v2.25, the spec-patch auto-resume cycle introduced in v2.24.2
(`_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, `initial_spec_hash`,
`_spec_patch_cycle_count`) SHALL be retired from `executor.py`. The trigger check in
`execute_roadmap()` — which fired when `spec_fidelity_failed == True` — SHALL be removed.

**Rationale**: The spec-patch cycle was designed for a pipeline where `SPEC_FIDELITY_GATE` was
STRICT and a permanent halt on fidelity failure could only be recovered by patching the spec and
resuming. v2.25 eliminates this failure mode: `SPEC_FIDELITY_GATE` is now STANDARD (never
semantically blocks), and the `DEVIATION_ANALYSIS_GATE` (STRICT) is the new blocking gate, with
recovery via bounded `--resume` remediation cycles (§8.4–8.6). The auto-resume scenario the
spec-patch cycle handled — "subprocess patched spec, wrote `dev-*-accepted-deviation.md`, pipeline
should resume from spec-fidelity" — no longer arises in the v2.25 pipeline because spec-fidelity
no longer blocks.

**Scope of retirement** (code to be deleted from `executor.py`):
- The `_spec_patch_cycle_count = 0` local variable in `execute_roadmap()`
- The `initial_spec_hash = hashlib.sha256(...)` capture in `execute_roadmap()`
- The `spec_fidelity_failed` boolean and the `if spec_fidelity_failed:` block in `execute_roadmap()`
- The `_apply_resume_after_spec_patch()` function definition (~90 lines)
- The `_find_qualifying_deviation_files()` function definition (~45 lines)
- The `auto_accept` parameter from `execute_roadmap()` signature

**Not retired**: `spec_patch.py` and its `prompt_accept_spec_change()` function remain unchanged.
The `roadmap accept-spec-change` CLI command continues to function as a manual operator tool for
updating `spec_hash` in `.roadmap-state.json` after deliberate spec modifications. The
`scan_accepted_deviation_records()` function and the `DeviationRecord` dataclass remain in
`spec_patch.py` unchanged. Only the executor's automatic triggering is removed.

**Insert as new subsection §14.7 in §14 (Backward Compatibility)**:

---

#### 14.7 Spec-Patch Auto-Resume Retirement

**NFR-011**: The `_apply_resume_after_spec_patch()` auto-resume cycle SHALL NOT be present in
v2.25 executor.py. Operators who relied on automatic spec-patch auto-resume in v2.24.x SHALL
use explicit `--resume` invocations after any spec modification.

The v2.24.2 spec-patch auto-resume cycle triggered when three conditions were simultaneously true:

1. `spec-fidelity` step failed its STRICT gate (`spec_fidelity_failed == True`)
2. Qualifying `dev-*-accepted-deviation.md` files existed with mtime > fidelity started_at
3. The spec file SHA-256 hash changed since `execute_roadmap()` entry

In v2.25, Condition 1 never occurs in normal operation because `SPEC_FIDELITY_GATE` is STANDARD
(no semantic checks). The recovery mechanism that replaced the spec-patch cycle is:

- `DEVIATION_ANALYSIS_GATE` (STRICT) blocks on `ambiguous_count > 0` (human review required)
- Bounded `--resume` remediation cycle (max 2 attempts) for SLIP remediation failure
- Manual `roadmap accept-spec-change` for deliberate spec modifications followed by `--resume`

Existing `.roadmap-state.json` files containing `spec_hash` entries remain valid. The
`accept-spec-change` CLI command continues to update `spec_hash` for manual use.

---

## ISSUE 2 (W-ADV-1, CRITICAL): Empty `routing_fix_roadmap` Silently Drops All SLIPs

### Recommended Approach

**Approach A: Add semantic check to DEVIATION_ANALYSIS_GATE**, combined with the `ValueError`
guard from Approach B as a secondary defense.

The gate is the correct place to enforce structural invariants of the `deviation-analysis.md`
artifact before it is consumed downstream. Adding `_routing_consistent_with_slip_count()` to
`DEVIATION_ANALYSIS_GATE` catches the empty-routing case immediately, with a clear failure message
pointing at the deviation-analysis step as the source. The `ValueError` guard in
`deviations_to_findings()` provides secondary defense against future gate relaxation or direct
function calls in tests.

### Draft Spec Language

**Add to §5.5 (Gate Definition) after the existing `DEVIATION_ANALYSIS_GATE` definition**:

---

**FR-056**: A `_routing_consistent_with_slip_count()` semantic check function SHALL be added to
`gates.py`. The check SHALL return `False` if `slip_count > 0` AND `routing_fix_roadmap` is empty,
null, or whitespace-only. It SHALL return `True` if `slip_count == 0` (empty routing is correct
when there are no SLIPs). It SHALL fail-closed: if `slip_count` is absent or unparseable, it
returns `False`.

```python
def _routing_consistent_with_slip_count(content: str) -> bool:
    """Validate routing_fix_roadmap is non-empty when slip_count > 0.

    Invariant (FR-022): SLIPs are always routed to fix_roadmap. Therefore,
    slip_count > 0 implies routing_fix_roadmap must contain at least one ID.

    Fails closed: missing or unparseable slip_count returns False.
    """
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    slip_val = fm.get("slip_count")
    if slip_val is None:
        return False
    try:
        slip_count = int(slip_val)
    except (ValueError, TypeError):
        return False

    if slip_count == 0:
        return True  # No SLIPs; empty routing is correct

    routing_val = fm.get("routing_fix_roadmap", "")
    if routing_val is None:
        return False
    return len(str(routing_val).strip()) > 0
```

**FR-057**: The `DEVIATION_ANALYSIS_GATE` SHALL include `_routing_consistent_with_slip_count`
as a third semantic check, appended after `no_ambiguous_deviations` and
`validation_complete_true`. The failure message SHALL be:

```
"slip_count > 0 but routing_fix_roadmap is empty. Every SLIP must appear in
routing_fix_roadmap (FR-022). Verify deviation-analysis agent output is complete
and re-run the deviation-analysis step."
```

**Updated DEVIATION_ANALYSIS_GATE** (replaces the definition in §5.5):

```python
DEVIATION_ANALYSIS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "total_analyzed",
        "pre_approved_count",
        "intentional_count",
        "slip_count",
        "ambiguous_count",
        "adjusted_high_severity_count",
        "validation_complete",
        "routing_fix_roadmap",
        "routing_update_spec",
        "routing_no_action",
        "routing_human_review",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="no_ambiguous_deviations",
            check_fn=_no_ambiguous_deviations,
            failure_message=(
                "All deviations must be fully classified. "
                "ambiguous_count must be 0 before remediation can proceed."
            ),
        ),
        SemanticCheck(
            name="validation_complete_true",
            check_fn=_validation_complete_true,
            failure_message="validation_complete must be true before remediation can proceed",
        ),
        SemanticCheck(
            name="routing_consistent_with_slip_count",
            check_fn=_routing_consistent_with_slip_count,
            failure_message=(
                "slip_count > 0 but routing_fix_roadmap is empty. "
                "Every SLIP must appear in routing_fix_roadmap (FR-022). "
                "Verify deviation-analysis agent output is complete and "
                "re-run the deviation-analysis step."
            ),
        ),
    ],
)
```

**FR-058**: The `deviations_to_findings()` function SHALL include a secondary guard: if
`_parse_routing_list()` returns an empty list AND frontmatter `slip_count > 0`, the function
SHALL raise `ValueError` with a message indicating the artifact is inconsistent. This guard is
defense-in-depth against gate bypass and direct function calls in test harnesses.

**Add to §7.2 (Deviation-to-Finding Conversion), immediately after the `if not fix_ids: return []`
block in the `deviations_to_findings()` code listing**:

```python
    if not fix_ids:
        # Secondary guard (defense-in-depth against gate bypass):
        # If the gate passed but routing is empty, check slip_count.
        # This should never fire in production if DEVIATION_ANALYSIS_GATE is enforced.
        slip_count = int(da_fm.get("slip_count", 0)) if da_fm else 0
        if slip_count > 0:
            raise ValueError(
                f"deviation-analysis.md reports slip_count={slip_count} but "
                f"routing_fix_roadmap is empty. Artifact is inconsistent. "
                f"Re-run deviation-analysis or fix the routing table manually."
            )
        return []
```

---

## ISSUE 3 (W-3, MAJOR): Artifact Boundary Between `dev-*-accepted-deviation.md` and `spec-deviations.md` Undefined

### Recommended Approach

**Approach A as primary, with a §14 cross-reference** (elements of Approach B).

Insert §3.1 "Artifact Taxonomy" immediately before the step definition (renaming current §3.1
to §3.2). Add a cross-reference note in §14. This ensures the taxonomy is discovered on first
encounter with `spec-deviations.md` in §3, while §14 provides a compat-oriented summary for
upgrade-path readers.

### Draft Spec Language

**Insert as new §3.1 in §3 (renumber current §3.1–§3.5 to §3.2–§3.6)**:

---

### 3.1 Artifact Taxonomy: Deviation-Related Files

v2.25 introduces `spec-deviations.md` as a new pipeline artifact. It coexists in the output
directory with `dev-*-accepted-deviation.md` files from v2.24.2. These artifacts are distinct
in purpose, writer, reader, and lifecycle. They MUST NOT be confused or treated as substitutes.

| Property | `spec-deviations.md` | `dev-*-accepted-deviation.md` |
|----------|---------------------|-------------------------------|
| **Glob pattern** | `spec-deviations.md` (exact filename) | `dev-*-accepted-deviation.md` (glob, zero or more) |
| **Writer** | `annotate-deviations` pipeline step (Step 7, FR-003) | Subprocess agent invocations during roadmap generation (v2.24.2); written outside the pipeline orchestration loop |
| **Readers** | `spec-fidelity` step (as additional input, FR-018); `deviation-analysis` step (as classification context, FR-019) | `scan_accepted_deviation_records()` in `spec_patch.py` (for the `roadmap accept-spec-change` CLI command) |
| **Lifecycle** | Regenerated on each pipeline run. Skipped on `--resume` only if its `ANNOTATE_DEVIATIONS_GATE` already passes. Never incrementally updated. | Written by subprocesses during agent execution. Persists across pipeline runs. Accumulates over time. |
| **Format** | YAML frontmatter (`total_annotated`, count fields) + deviation annotation table + evidence sections | YAML frontmatter (`disposition: ACCEPTED`, `spec_update_required: true/false`, `affects_spec_sections`, `acceptance_rationale`) + markdown body |
| **Classification scheme** | `INTENTIONAL_IMPROVEMENT` / `INTENTIONAL_PREFERENCE` / `SCOPE_ADDITION` / `NOT_DISCUSSED` | Binary: `disposition: ACCEPTED` or `REJECTED` |
| **Purpose** | Pre-compute deviation classification for fidelity agent and deviation-analysis step (Scope 2: prevention) | Record operator or subprocess acceptance of a specific deviation, enabling spec-hash update via `accept-spec-change` command |
| **Pipeline role in v2.25** | Active: consumed by steps 9 (spec-fidelity) and 10 (deviation-analysis) | Passive: read only by manual CLI command (`roadmap accept-spec-change`). Not read by any pipeline step in v2.25. |
| **Substitution** | Does NOT substitute for `dev-*-accepted-deviation.md` | Does NOT substitute for `spec-deviations.md` |

**Critical implementation note**: The `annotate-deviations` step SHALL write only `spec-deviations.md`
and SHALL NOT write `dev-*-accepted-deviation.md` files. The two formats are not interchangeable.
An `annotate-deviations` agent that writes `dev-*-accepted-deviation.md` is producing the wrong
artifact and will cause the deviation-analysis step to receive an empty or absent
`spec-deviations.md` input.

**Add cross-reference to §14 as new §14.8**:

---

#### 14.8 Deviation Artifact Taxonomy (Cross-Reference)

See §3.1 for the full artifact taxonomy table. In summary: `spec-deviations.md` (new in v2.25,
written by `annotate-deviations` step, consumed by `spec-fidelity` and `deviation-analysis`) and
`dev-*-accepted-deviation.md` (v2.24.2, written by subprocess agents, consumed only by the
`roadmap accept-spec-change` CLI command in v2.25) serve completely different purposes and MUST
NOT be confused.

**NFR-012**: No pipeline step introduced or modified in v2.25 SHALL read `dev-*-accepted-deviation.md`
files as part of its normal execution. The `dev-*-accepted-deviation.md` artifact format is
consumed exclusively by `spec_patch.py` / the `roadmap accept-spec-change` CLI command.

---

## ISSUE 4 (W-2, MAJOR): §11 Affected-Files Summary Omits All v2.24.2 Functions

### Recommended Approach

**Approach C: Add §11.5 "v2.24.2 → v2.25 Compatibility Surface" table.**

Approach C provides the most complete reference with the least ambiguity. It serves both
implementors (complete checklist of changes) and reviewers (can verify executor.py diff against
the table). Approach A is a subset of C. Approach B's inline annotation is harder to read.

The table below is the exact content to insert, reflecting the retirement decision from Issue 1
(Approach A). If Issue 1 is resolved differently, only the RETIRED rows change.

### Draft Spec Language

**Insert as new §11.5 after the existing §11 tables**:

---

### 11.5 v2.24.2 → v2.25 Compatibility Surface: `executor.py`

The following table maps every v2.24.2 symbol in `executor.py` to its v2.25 disposition. This
table is authoritative for implementors performing the v2.24.2 → v2.25 migration. Symbols marked
RETIRED are deleted in v2.25. Symbols marked UNCHANGED are intentionally left alone. Symbols
marked MODIFIED or NEW are covered by the FR references.

| v2.24.2 Symbol in `executor.py` | v2.25 Disposition | FR Reference |
|----------------------------------|-------------------|--------------|
| `execute_roadmap(config, resume, no_validate, auto_accept)` — function signature | MODIFIED: `auto_accept` parameter removed | FR-059 |
| `_spec_patch_cycle_count = 0` — local variable in `execute_roadmap()` | RETIRED | FR-059 |
| `initial_spec_hash = hashlib.sha256(...)` — local variable in `execute_roadmap()` | RETIRED | FR-059 |
| `spec_fidelity_failed = any(...)` — boolean + conditional block in `execute_roadmap()` | RETIRED | FR-059 |
| `_find_qualifying_deviation_files(config, results)` — function | RETIRED | FR-059 |
| `_apply_resume_after_spec_patch(config, results, auto_accept, initial_spec_hash, cycle_count)` — function | RETIRED | FR-059 |
| `_apply_resume(steps, config, gate_passed)` | UNCHANGED | — |
| `_build_steps(config)` | MODIFIED: `annotate-deviations` (FR-004) and `deviation-analysis` (FR-020) steps added; spec-fidelity step updated to include `deviations_file` input (FR-018) | FR-004, FR-018, FR-020 |
| `_get_all_step_ids(config)` | MODIFIED: `annotate-deviations` and `deviation-analysis` IDs added in correct pipeline positions | FR-038 |
| `_save_state(config, results)` | MODIFIED: `remediation_attempts` counter logic added | FR-039 |
| `_check_remediation_budget(config, max_attempts)` | NEW | FR-040 |
| `_print_terminal_halt(config, state)` | NEW | FR-042 |
| `_auto_invoke_validate(config)` | UNCHANGED | — |
| `_save_validation_status(config, status)` | UNCHANGED | — |
| `_format_halt_output(results, config)` | UNCHANGED | — |
| `_dry_run_output(steps)` | UNCHANGED | — |
| `_print_step_start(step)` | UNCHANGED | — |
| `_print_step_complete(result)` | UNCHANGED | — |

**Implementation note**: The six symbols marked RETIRED (FR-059) constitute approximately 130
lines of code. Their deletion is a v2.25 correctness requirement, not a cleanup optimization.
Leaving them in place with v2.25 code will result in dead code with incorrect implicit semantics
(the `spec_fidelity_failed` trigger block would reference a STANDARD gate that almost never
fails, and `_apply_resume_after_spec_patch()` would shadow the new --resume mechanism).

---

## ISSUE 5 (W-4+W-5, MAJOR/MINOR): NFR-006 Incomplete + No FR for Spec-Patch Trigger Update

### Draft Spec Language

**Updated NFR-006 (replaces existing §14.2 text)**:

---

#### 14.2 Spec-Fidelity Gate Downgrade: Relaxation and Behavioral Consequences

**NFR-006**: The downgrade of `SPEC_FIDELITY_GATE` from STRICT to STANDARD enforcement tier
(FR-014, FR-015) is a relaxation with the following behavioral consequences:

**(a) Forward compatibility**: Any pipeline run that passed the STRICT gate (i.e., produced a
`spec-fidelity.md` with `high_severity_count == 0` and passing semantic checks) will also pass
the STANDARD gate. Existing `.roadmap-state.json` files with `spec-fidelity: PASS` remain valid
and will be correctly skipped by `--resume`. No migration of existing state files is required.

**(b) Behavioral flip for previously-failing runs**: Pipeline runs that previously FAILED at the
STRICT `spec-fidelity` gate (because `high_severity_count > 0`) will now PASS the STANDARD gate.
This is the intended behavior: the blocking responsibility has moved from spec-fidelity to the new
`DEVIATION_ANALYSIS_GATE` (STRICT, §5.5). A STANDARD pass at spec-fidelity does NOT mean
deviations were fixed — it means the pipeline proceeds to `deviation-analysis`, which classifies
the deviations and routes them to remediation. Operators whose pipelines previously blocked at
spec-fidelity will observe the pipeline proceeding through spec-fidelity and halting (or passing)
at `deviation-analysis` instead. This is correct v2.25 behavior.

**(c) Spec-patch auto-resume dormancy**: With spec-fidelity STANDARD, the `spec_fidelity_failed`
boolean in `execute_roadmap()` is almost never True. The v2.24.2 spec-patch auto-resume cycle
(`_apply_resume_after_spec_patch()`) is therefore effectively dormant. This cycle is formally
retired in v2.25 per FR-059. See §8.7 for the retirement specification and §14.7 for the
backward-compat summary.

**(d) Existing state file compatibility**: `.roadmap-state.json` files written by v2.24.2 pipelines
that contain `spec-fidelity: FAIL` are valid inputs to v2.25 `--resume`. The STANDARD gate will
pass the existing output file on resume (since it checks only frontmatter presence), allowing
the resume to proceed to `deviation-analysis`. This is the intended `--resume` behavior.

---

**FR-059 (new, §8.7)**:

The full FR-055 text was drafted in Issue 1 above. For cross-reference, its assignment is confirmed:

- **FR-059 location**: §8.7 (new subsection "Spec-Patch Auto-Resume Cycle: Retirement")
- **FR-059 scope**: Retirement of `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`,
  `initial_spec_hash`, `_spec_patch_cycle_count`, and `auto_accept` parameter from `execute_roadmap()`
- **FR-059 rationale**: SPEC_FIDELITY_GATE downgraded to STANDARD means `spec_fidelity_failed`
  is almost never True; the spec-patch auto-resume cycle is dormant and misleading; retirement
  removes ~130 lines of dead code and eliminates the "two resume mechanisms" confusion

**Note on FR numbering**: FR-055 is already assigned in the current spec to the `ALL_GATES`
registry update (§3.5: "The `ALL_GATES` registry in `gates.py` SHALL be updated to include
entries for both `annotate-deviations` and `deviation-analysis` gates"). The spec-patch
retirement FR must therefore be assigned FR-059 (next available after FR-058, the secondary
guard FR drafted in Issue 2). Confirm assignment during spec merge.

**Revised FR numbering recommendation for Issue 5**:

- FR-055: ALL_GATES registry update (existing, keep as-is per §3.5 FR-054 / §3.5 FR-055 text)
- FR-056: `_routing_consistent_with_slip_count()` semantic check (Issue 2 Approach A)
- FR-057: `DEVIATION_ANALYSIS_GATE` third semantic check (Issue 2 Approach A)
- FR-058: `deviations_to_findings()` secondary guard (Issue 2 defense-in-depth)
- FR-059: Spec-patch auto-resume cycle retirement (Issue 1 Approach A — was labeled FR-055 in
  this document's §8.7 draft; corrected here to FR-059 to avoid collision)

**Corrected §8.7 header** (replacing "FR-055" with "FR-059" throughout the §8.7 draft above):

All instances of "FR-055" in the Issue 1 §8.7 draft language and the §14.7 draft language should
read "FR-059." The §11.5 table (Issue 4) should also reference FR-059, not FR-055.

## Consolidated FR/NFR List

The following table lists every new FR and NFR drafted in this brainstorm document. All are
additive to the existing v2.25 spec. Section references indicate where the language should be
inserted.

| Number | Type | Title | Insert Location | Issue |
|--------|------|--------|-----------------|-------|
| FR-056 | FR | `_routing_consistent_with_slip_count()` semantic check function | §5.5, after DEVIATION_ANALYSIS_GATE definition | W-ADV-1 |
| FR-057 | FR | DEVIATION_ANALYSIS_GATE gains third semantic check (`routing_consistent_with_slip_count`) | §5.5, replaces DEVIATION_ANALYSIS_GATE definition | W-ADV-1 |
| FR-058 | FR | `deviations_to_findings()` secondary guard: raise ValueError if fix_ids empty and slip_count > 0 | §7.2, inside deviations_to_findings() listing | W-ADV-1 |
| FR-059 | FR | Spec-patch auto-resume cycle retirement: delete `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, local vars, `auto_accept` param | New §8.7 | W-1 |
| NFR-006 | NFR | Spec-fidelity downgrade: forward compat, behavioral flip, spec-patch dormancy, state file compat (full replacement) | §14.2 (replaces existing text) | W-4+W-5 |
| NFR-011 | NFR | Spec-patch auto-resume cycle not present in v2.25; operators use explicit --resume | New §14.7 | W-1 |
| NFR-012 | NFR | No v2.25 pipeline step reads dev-*-accepted-deviation.md; format consumed only by accept-spec-change CLI | New §14.8 | W-3 |

Additionally, the following spec locations require structural additions (no new FR/NFR numbers):

| Location | Type | Content | Issue |
|----------|------|---------|-------|
| §3.1 (new subsection; renumber 3.1–3.5 → 3.2–3.6) | Taxonomy table | Deviation artifact taxonomy: spec-deviations.md vs dev-*-accepted-deviation.md | W-3 |
| §11.5 (new subsection) | Compatibility table | v2.24.2 → v2.25 executor.py symbol disposition map (RETIRED / UNCHANGED / MODIFIED / NEW) | W-2 |
| §14.7 (new subsection) | Backward-compat note | Spec-patch auto-resume retirement summary and operator migration guidance | W-1 |
| §14.8 (new subsection) | Backward-compat note | Deviation artifact taxonomy cross-reference; NFR-012 | W-3 |

### FR Number Collision Note

The existing spec assigns **FR-054** (§3.5) as the ALL_GATES registry update, and **FR-055**
appears in some spec drafts as a second ALL_GATES-related entry. Before inserting FR-056 through
FR-059 from this brainstorm, the implementor MUST verify the highest existing FR number in the
merged spec and assign the new FRs sequentially from that point. The numbers FR-056 through
FR-059 in this document are provisional and assume FR-054 is the current maximum. If FR-055 is
also used, the new FRs shift to FR-057 through FR-060.

### Summary: Pre-Implementation Actions Required

Before v2.25 implementation begins, the following spec amendments must be merged into
`v2.25-spec-merged.md`:

1. **W-1 (CRITICAL)**: Insert §8.7 (FR-059 retirement) and §14.7 (NFR-011 compat note). Update
   §14.2 (NFR-006 full replacement). Update §11.5 RETIRED rows (FR-059 reference).

2. **W-ADV-1 (CRITICAL)**: Insert `_routing_consistent_with_slip_count()` function (FR-056) and
   update `DEVIATION_ANALYSIS_GATE` definition (FR-057) in §5.5. Add secondary guard to
   `deviations_to_findings()` (FR-058) in §7.2.

3. **W-3 (MAJOR)**: Insert §3.1 taxonomy table (renumber 3.1–3.5 to 3.2–3.6). Insert §14.8
   cross-reference (NFR-012).

4. **W-2 (MAJOR)**: Insert §11.5 compatibility surface table.

5. **W-4+W-5 (MAJOR/MINOR)**: Replace §14.2 with updated NFR-006 text. Confirm FR-059 number
   (spec-patch retirement).

Issues 1 and 2 are CRITICAL and block implementation of executor.py and gates.py respectively.
Issues 3, 4, and 5 are documentation amendments that should be merged before implementation review.
