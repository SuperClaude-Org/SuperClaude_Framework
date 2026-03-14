---
title: "v2.25 Long-Term Amendments Tasklist"
source: approved-longterm.md
target: v2.25-spec-merged.md
compliance: strict
issues_addressed:
  - "ISSUE 1 (W-ADV-2 extended, MAJOR): roadmap.md content hash for stale-detection"
  - "ISSUE 2 (W-ADV-4, MAJOR): Non-integer remediation_attempts crashes budget check"
  - "ISSUE 3 (W-ADV-3, MAJOR): Deviation ID format unconstrained — comma corrupts routing"
  - "ISSUE 4 (N-2 extended, MAJOR): Two retry counters with no coordination spec"
executor: sc:task-unified
---

# v2.25 Long-Term Amendments — Implementation Tasklist

All tasks operate on:
- **Target file**: `.dev/releases/backlog/2.25-roadmap-v5/v2.25-spec-merged.md`
- **Source of truth**: `.dev/releases/backlog/2.25-roadmap-v5/approved-longterm.md`

## Critical Prerequisite

**This tasklist MUST be executed AFTER `tasklist-immediate-amendments.md` completes.**

Specific dependencies:
- TASK A-1 from immediate tasklist must have renumbered §3.1–3.5 → §3.2–3.6, which shifts §3.5 Gate Definition to §3.6. The longterm tasklist inserts into what is now **§3.6** (formerly §3.5).
- TASK E-1 from immediate tasklist will have created **§8.7** ("Spec-Patch Auto-Resume Cycle: Retirement"). Longterm ISSUE 4 inserts a **§8.8** table (not §8.7 — see TASK G-1 note below).
- TASK G-2 from immediate tasklist will have created **§14.7** ("Spec-Patch Auto-Resume Retirement"). Longterm ISSUE 4 inserts **§14.8** ("Spec-Patch Cycle Dormancy in v5") — see TASK G-2 note below.

> **Section numbering resolution**: Because the immediate amendments already occupy §8.7 and §14.7,
> all longterm §8.7/§14.7 draft labels from `approved-longterm.md` become §8.8/§14.9 in the final spec.
> This tasklist uses the **final** section numbers throughout.

---

## GROUP A — §3 Gate Definition Update (depends on immediate A-1 completing)

### TASK A-1: Add `roadmap_hash` to `ANNOTATE_DEVIATIONS_GATE` required fields (§3.6)

**Issue**: ISSUE 1 (W-ADV-2)
**Priority**: MAJOR — correctness; prevents silent stale-annotation on `--resume`
**FR/NFR**: FR-070
**Compliance**: strict
**Depends on**: immediate tasklist TASK A-1 (§3 renumbered; §3.5 → §3.6)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 3.6 Gate Definition` (formerly §3.5, renumbered by immediate TASK A-1). Find `**FR-013**` — the last existing FR in that section. After the FR-013 block, insert verbatim:

```
**FR-070**: The `ANNOTATE_DEVIATIONS_GATE` required frontmatter fields SHALL
include `roadmap_hash`. A missing or empty `roadmap_hash` field SHALL cause
the STANDARD gate to fail on structural completeness grounds (existing
frontmatter field check behavior).
```

**Acceptance criteria**:
- `grep "FR-070" v2.25-spec-merged.md` returns exactly one match in the §3.6 gate section
- `grep "roadmap_hash" v2.25-spec-merged.md` returns matches in §3.6 (gate field requirement) and §3.3 (injection spec — added by TASK B-1 below)

---

## GROUP B — §3.3 Step Construction Update (depends on immediate A-1)

### TASK B-1: Add `roadmap_hash` injection spec to §3.3 (formerly §3.2)

**Issue**: ISSUE 1 (W-ADV-2)
**Priority**: MAJOR
**FR/NFR**: FR-055
**Compliance**: strict
**Depends on**: immediate tasklist TASK A-1 (§3 renumbered; §3.2 → §3.3)

**What to do**:
In `v2.25-spec-merged.md`, locate `### 3.3 Step Construction in \`_build_steps()\`` (formerly §3.2). Find `**FR-004**` — the existing step insertion FR in that section. After the FR-004 block (and its associated code listing), insert verbatim from `approved-longterm.md` ISSUE 1 Draft Spec Language, the FR-055 block:

```
**FR-055**: After the `annotate-deviations` subprocess completes and
`_sanitize_output()` runs, the executor SHALL inject a `roadmap_hash` field
into `spec-deviations.md` frontmatter containing the SHA-256 hex digest of
`roadmap.md` at the time of injection (same atomic-write pattern as
`_inject_pipeline_diagnostics()`).

Implementation:
```python
# In roadmap_run_step(), after _sanitize_output():
if step.id == "annotate-deviations" and step.output_file.exists():
    _inject_roadmap_hash(step.output_file, config.output_dir / "roadmap.md")
```

`_inject_roadmap_hash(output_file, roadmap_path)` reads the current
frontmatter, adds or overwrites `roadmap_hash: <sha256>`, and writes
atomically via `.tmp` + `os.replace()`.
```

**Acceptance criteria**:
- `grep "FR-055" v2.25-spec-merged.md` returns exactly one match in §3.3
- `grep "_inject_roadmap_hash" v2.25-spec-merged.md` returns a match
- `grep "roadmap_hash" v2.25-spec-merged.md` returns matches in both §3.3 and §3.6

---

## GROUP C — §5.4 Deviation ID Format Constraint (no dependency on other tasks)

### TASK C-1: Add `DEV-\d+` ID format constraint to §5.4

**Issue**: ISSUE 3 (W-ADV-3)
**Priority**: MAJOR — prevents silent routing corruption from comma-in-ID
**FR/NFR**: FR-073
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.4 Output Format: \`deviation-analysis.md\``. Find `**FR-024**` — the last existing output format FR in that section. After the FR-024 block, insert verbatim from `approved-longterm.md` ISSUE 3 Draft Spec Language, the FR-073 block:

```
**FR-073**: Deviation IDs in `deviation-analysis.md` SHALL match the pattern
`DEV-\d+` (e.g., DEV-001, DEV-042). The prompt for `deviation-analysis`
SHALL instruct the agent to use only deviation IDs as they appear in
`spec-fidelity.md`, which generates IDs in the `DEV-NNN` format.
```

**Acceptance criteria**:
- `grep "FR-073" v2.25-spec-merged.md` returns exactly one match in §5.4
- `grep "DEV-\\\\d+" v2.25-spec-merged.md` returns a match (the regex pattern)

---

## GROUP D — §5.5 Gate Updates: `_routing_ids_valid` (depends on C-1 for logical consistency, may run parallel)

### TASK D-1: Add `_routing_ids_valid()` semantic check function to §5.5

**Issue**: ISSUE 3 (W-ADV-3)
**Priority**: MAJOR — STRICT gate blocks malformed routing IDs from reaching `deviations_to_findings()`
**FR/NFR**: FR-074
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.5 Gate Definition`. Find `**FR-026**` — the existing gate definition FR. After the FR-026 block (and any existing semantic check definitions), insert verbatim from `approved-longterm.md` ISSUE 3 Draft Spec Language, the FR-074 block:

```
**FR-074**: A `_routing_ids_valid(content: str) -> bool` semantic check
function SHALL be added to `gates.py`. The function SHALL:
1. Parse the frontmatter of `deviation-analysis.md`
2. For each of the four routing fields (`routing_fix_roadmap`,
   `routing_update_spec`, `routing_no_action`, `routing_human_review`),
   split the value on commas and validate each non-empty token against
   `re.compile(r'^DEV-\d+$')`
3. Return `False` if any token fails validation; return `True` if all tokens
   are valid or all routing fields are empty

This check SHALL be registered as a STRICT semantic check on
`DEVIATION_ANALYSIS_GATE`.
```

> **Note**: If the immediate amendments tasklist has already updated `DEVIATION_ANALYSIS_GATE`
> (adding the `routing_consistent_with_slip_count` third check), this `_routing_ids_valid` check
> becomes a **fourth** semantic check. The `DEVIATION_ANALYSIS_GATE` GateCriteria block must be
> updated again to include it. Update the code block to add:
> ```python
> SemanticCheck(
>     name="routing_ids_valid",
>     check_fn=_routing_ids_valid,
>     failure_message=(
>         "One or more routing field tokens do not match the DEV-\\d+ pattern. "
>         "Deviation IDs must use the format DEV-NNN as generated by spec-fidelity. "
>         "Re-run the deviation-analysis step."
>     ),
> ),
> ```
> as the fourth entry in the `semantic_checks` list.

**Acceptance criteria**:
- `grep "FR-074" v2.25-spec-merged.md` returns exactly one match in §5.5
- `grep "_routing_ids_valid" v2.25-spec-merged.md` returns at least 2 matches (function spec + gate registration)
- `grep "routing_ids_valid" v2.25-spec-merged.md` returns a match inside the `DEVIATION_ANALYSIS_GATE` `semantic_checks` list

---

## GROUP E — §7.2 Token Validation in `_parse_routing_list()` (no blocking dependency)

### TASK E-1: Add `DEV-\d+` token validation and cross-check to `_parse_routing_list()` in §7.2

**Issue**: ISSUE 3 (W-ADV-3)
**Priority**: MAJOR — defense-in-depth: filters non-conforming tokens even if gate is bypassed
**FR/NFR**: FR-075
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 7.2 Deviation-to-Finding Conversion`. Find the section describing `_parse_routing_list()` (this function is called within `deviations_to_findings()`). After the existing `_parse_routing_list()` prose or the `deviations_to_findings()` code stub (wherever `_parse_routing_list()` is last mentioned in spec language), insert verbatim from `approved-longterm.md` ISSUE 3 Draft Spec Language, the FR-075 block:

```
**FR-075**: `_parse_routing_list()` SHALL validate each token against
`re.compile(r'^DEV-\d+$')`. Non-conforming tokens SHALL be logged as
WARNING and excluded from the returned list. An empty string token (from
trailing comma or empty field) SHALL be silently skipped without logging.

Additionally, `_parse_routing_list()` SHALL cross-check `len(returned_tokens)`
against the `total_analyzed` frontmatter field. If `len(returned_tokens) >
total_analyzed`, a WARNING SHALL be logged (routing more IDs than were analyzed
suggests a parse error or duplicate IDs).
```

> **Note**: If the short-term amendments tasklist has already added FR-061 to §7.2a
> (specifying `_parse_routing_list()` edge cases), FR-075 is additive — it strengthens
> the token validation spec. Both FRs apply to the same function. FR-075 adds the regex
> constraint and cross-check to whatever FR-061 already specified.

**Acceptance criteria**:
- `grep "FR-075" v2.25-spec-merged.md` returns exactly one match in §7.2 or §7.2a
- `grep "total_analyzed" v2.25-spec-merged.md` returns a match in the `_parse_routing_list()` context (cross-check warning)
- `grep "Non-conforming tokens" v2.25-spec-merged.md` returns a match

---

## GROUP F — §8.2 Resume Freshness Check (no blocking dependency)

### TASK F-1: Add `_check_annotate_deviations_freshness()` spec to §8.2

**Issue**: ISSUE 1 (W-ADV-2)
**Priority**: MAJOR
**FR/NFR**: FR-071, NFR-016
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 8.2 Impact of v5 Changes on Resume`. Find `**FR-038**` — the existing resume impact FR. After the FR-038 block, insert verbatim from `approved-longterm.md` ISSUE 1 Draft Spec Language, the FR-071 + NFR-016 block:

```
**FR-071**: `_apply_resume()` SHALL call
`_check_annotate_deviations_freshness(config, deviations_file)` before
deciding to skip the `annotate-deviations` step. If the function returns
`False` (meaning `roadmap_hash` in `spec-deviations.md` does not match the
current SHA-256 of `roadmap.md`), the step SHALL be re-added to the execution
queue regardless of whether the STANDARD gate would otherwise pass.

```python
def _check_annotate_deviations_freshness(
    config: RoadmapConfig,
    deviations_file: Path,
) -> bool:
    """Returns True if spec-deviations.md is fresh for current roadmap.md.

    Returns False if:
    - spec-deviations.md does not exist
    - roadmap_hash field is missing or empty
    - roadmap.md does not exist
    - SHA-256 of roadmap.md does not match stored roadmap_hash
    """
    if not deviations_file.exists():
        return False
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

**NFR-016**: `_check_annotate_deviations_freshness()` SHALL be fail-closed:
any missing file, missing field, or read error SHALL cause it to return
`False` (force re-run), not skip. It SHALL NOT raise exceptions.
```

Copy exact text from `approved-longterm.md` lines 49–87.

**Acceptance criteria**:
- `grep "FR-071" v2.25-spec-merged.md` returns exactly one match in §8.2
- `grep "NFR-016" v2.25-spec-merged.md` returns exactly one match in §8.2
- `grep "_check_annotate_deviations_freshness" v2.25-spec-merged.md` returns at least 2 matches (prose + function def)
- `grep "fail-closed" v2.25-spec-merged.md` returns a match in §8.2 context

---

## GROUP G — §8.4 Remediation Budget Hardening (no blocking dependency)

### TASK G-1: Add `int()` coercion spec to `_check_remediation_budget()` and `_save_state()` in §8.4

**Issue**: ISSUE 2 (W-ADV-4)
**Priority**: MAJOR — crash defect; uncaught TypeError crashes pipeline on corrupt state
**FR/NFR**: FR-072, NFR-017
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 8.4 Remediation Cycle Bounding`. Find `**FR-041**` — the last existing FR in that section. After the FR-041 block, insert verbatim from `approved-longterm.md` ISSUE 2 Draft Spec Language, the FR-072 + NFR-017 block:

```
**FR-072**: `_check_remediation_budget()` SHALL coerce `remediation_attempts`
to `int` before comparison. If the coercion raises `ValueError` or
`TypeError`, the function SHALL log a WARNING and treat `remediation_attempts`
as `0` (fresh budget), allowing the current attempt to proceed.

```python
raw = remediate.get("remediation_attempts", 0)
try:
    attempts = int(raw)
except (ValueError, TypeError):
    _log.warning(
        "remediation_attempts value %r is not a valid integer in "
        ".roadmap-state.json; treating as 0. State file may be corrupt.",
        raw,
    )
    attempts = 0
```

**Rationale**: External tampering or filesystem corruption may produce
non-integer values. An uncaught TypeError crashing the pipeline is a worse
outcome than allowing one more attempt. The WARNING log provides observability.

**NFR-017**: `_save_state()` SHALL coerce `existing_attempts` to `int`
before incrementing, using `try: int(...) except (ValueError, TypeError): 0`.
This ensures that `remediation_attempts` is always written as a Python `int`
to `.roadmap-state.json`, preventing corruption propagation across write
cycles.
```

Copy exact text from `approved-longterm.md` lines 107–133.

**Acceptance criteria**:
- `grep "FR-072" v2.25-spec-merged.md` returns exactly one match in §8.4
- `grep "NFR-017" v2.25-spec-merged.md` returns exactly one match in §8.4
- `grep "ValueError, TypeError" v2.25-spec-merged.md` returns a match in §8.4 context
- `grep "State file may be corrupt" v2.25-spec-merged.md` returns a match

---

## GROUP H — §8.8 Retry Budget Summary (depends on immediate TASK E-1 creating §8.7)

### TASK H-1: Insert new §8.8 "Retry Budget Summary and Counter Interaction"

**Issue**: ISSUE 4 (N-2 extended)
**Priority**: MAJOR — documentation-only; prevents implementor confusion about retry architecture
**FR/NFR**: FR-076, FR-077, NFR-018
**Compliance**: strict
**Depends on**: immediate tasklist TASK E-1 (which creates §8.7)

> **Section number note**: `approved-longterm.md` labels this "§8.7". Because the immediate
> amendments tasklist has already inserted §8.7 ("Spec-Patch Auto-Resume Cycle: Retirement"),
> this section becomes **§8.8** in the merged spec.

**What to do**:
In `v2.25-spec-merged.md`, locate `### 8.7 Spec-Patch Auto-Resume Cycle: Retirement` (inserted by immediate TASK E-1). After its content ends (and before `## 9.`), insert verbatim from `approved-longterm.md` ISSUE 4 Draft Spec Language, the §8.7 block — but with the heading changed to `### 8.8`:

```
### 8.8 Retry Budget Summary and Counter Interaction

The v5 pipeline contains two independent retry mechanisms. They operate on
different triggers, different storage, and different failure modes.

| Counter | Type | Max | Storage | Trigger | Effective in v5 |
|---------|------|-----|---------|---------|-----------------|
| `_spec_patch_cycle_count` | in-memory | 1 per invocation | local var in `execute_roadmap()` | spec-fidelity STANDARD FAIL + deviation files + spec hash change | Rarely (STANDARD gate failures are structural only) |
| `remediation_attempts` | persisted | 2 | `.roadmap-state.json` | certify FAIL on `--resume` | Yes (primary recovery mechanism) |

**FR-076**: The spec-patch cycle (`_spec_patch_cycle_count`) and the
remediation budget (`remediation_attempts`) SHALL remain independent in v5.
No global recovery budget counter is introduced.

**FR-077**: If the spec-patch cycle completes (cycle_count reaches 1) and
remediation subsequently exhausts its budget (remediation_attempts reaches 2),
`_print_terminal_halt()` SHALL be called with the standard remediation-
exhausted message. The message SHALL include a sentence noting that the
pipeline attempted both automatic recovery mechanisms. The exact wording is:

```
Note: A spec-patch auto-resume cycle also occurred before remediation began.
Both recovery mechanisms are now exhausted. Manual intervention is required.
```

Implementation of the "also occurred" note requires `_print_terminal_halt()`
to receive information about spec-patch cycle history. The state file
mechanism for this is deferred to v2.26 (see §14.9). For v2.25, this note
is a specification-only requirement pending implementation.

**NFR-018**: The combined maximum automatic recovery attempts in a single
pipeline lifetime SHALL NOT exceed 3 (1 spec-patch + 2 remediation). This
bound is enforced by the independent caps on each counter and requires no
additional global counter.
```

Copy exact text from `approved-longterm.md` lines 211–244, substituting `### 8.8` for `### 8.7` and updating the cross-reference `§14.7` → `§14.9`.

**Acceptance criteria**:
- `grep "### 8.8" v2.25-spec-merged.md` returns exactly one match
- `grep "FR-076" v2.25-spec-merged.md` returns a match in §8.8
- `grep "FR-077" v2.25-spec-merged.md` returns a match in §8.8
- `grep "NFR-018" v2.25-spec-merged.md` returns a match in §8.8
- `grep "Both recovery mechanisms are now exhausted" v2.25-spec-merged.md` returns a match
- The counter comparison table (with `_spec_patch_cycle_count` and `remediation_attempts` rows) is present

---

## GROUP I — §14.9 Dormancy Note (depends on immediate G-2 and G-3 creating §14.7 and §14.8)

### TASK I-1: Insert new §14.9 "Spec-Patch Cycle Dormancy in v5"

**Issue**: ISSUE 4 (N-2 extended)
**Priority**: MAJOR — documentation-only
**FR/NFR**: NFR-019
**Compliance**: strict
**Depends on**: immediate tasklist TASK G-2 (creates §14.7) and TASK G-3 (creates §14.8)

> **Section number note**: `approved-longterm.md` labels this "§14.7". Because the immediate
> amendments tasklist has already inserted §14.7 ("Spec-Patch Auto-Resume Retirement") and
> §14.8 ("Deviation Artifact Taxonomy Cross-Reference"), this section becomes **§14.9**.

**What to do**:
In `v2.25-spec-merged.md`, locate `### 14.8 Deviation Artifact Taxonomy (Cross-Reference)` (inserted by immediate TASK G-3). After its content ends (and before `## 15.`), insert verbatim from `approved-longterm.md` ISSUE 4 Draft Spec Language, the §14.7 block — but with the heading changed to `### 14.9`:

```
### 14.9 Spec-Patch Cycle Dormancy in v5

**NFR-019**: The `_apply_resume_after_spec_patch()` function and
`_spec_patch_cycle_count` counter SHALL be retained unchanged in v5. They
are not removed and not modified.

With spec-fidelity downgraded to STANDARD in v5 (FR-014), the spec-patch
cycle's trigger condition fires only when the STANDARD gate fails (missing
frontmatter or insufficient line count at the spec-fidelity step). HIGH
deviation count no longer triggers gate failure and therefore no longer
triggers the spec-patch cycle. The mechanism is functionally dormant in the
common pipeline path.

The mechanism is retained because:
1. It imposes no runtime cost when inactive
2. It provides a backstop for unforeseen STANDARD gate failures
3. Removing it would require coordinated changes with v2.24.2 deployments

Consumers of v2.25 who observe unexpected spec-patch cycle activation should
investigate whether `spec-fidelity.md` is missing required frontmatter or
whether `roadmap.md` is being modified by an external process during pipeline
execution.
```

Copy exact text from `approved-longterm.md` lines 248–269, substituting `### 14.9` for `### 14.7`.

**Acceptance criteria**:
- `grep "### 14.9" v2.25-spec-merged.md` returns exactly one match
- `grep "NFR-019" v2.25-spec-merged.md` returns a match in §14.9
- `grep "functionally dormant" v2.25-spec-merged.md` returns a match
- `grep "retained because" v2.25-spec-merged.md` returns a match

---

## GROUP J — Final Validation (depends on all prior tasks)

### TASK J-1: Full spec consistency verification

**Priority**: CRITICAL gate — do not mark longterm amendments complete until all checks pass
**Compliance**: strict

Run each of the following checks against the modified `v2.25-spec-merged.md`:

**Section structure checks**:
```bash
grep "^### 3\." v2.25-spec-merged.md
# Expected: 3.1 Artifact Taxonomy, 3.2 Step Definition (etc.), 3.6 Gate Definition

grep "^### 5\." v2.25-spec-merged.md
# Expected: 5.4 and 5.5 present and in order

grep "^### 8\." v2.25-spec-merged.md
# Expected: 8.1 through 8.8 present (8.7 = retirement, 8.8 = retry budget)

grep "^### 14\." v2.25-spec-merged.md
# Expected: 14.1 through 14.9 present
```

**FR/NFR presence checks**:
```bash
grep -c "FR-055" v2.25-spec-merged.md   # exactly 1 (§3.3 roadmap_hash injection)
grep -c "FR-070" v2.25-spec-merged.md   # exactly 1 (§3.6 gate field)
grep -c "FR-071" v2.25-spec-merged.md   # exactly 1 (§8.2 freshness check call)
grep -c "FR-072" v2.25-spec-merged.md   # exactly 1 (§8.4 int coercion)
grep -c "FR-073" v2.25-spec-merged.md   # exactly 1 (§5.4 ID format)
grep -c "FR-074" v2.25-spec-merged.md   # exactly 1 (§5.5 routing_ids_valid)
grep -c "FR-075" v2.25-spec-merged.md   # exactly 1 (§7.2 parse_routing_list)
grep -c "FR-076" v2.25-spec-merged.md   # exactly 1 (§8.8 independent counters)
grep -c "FR-077" v2.25-spec-merged.md   # exactly 1 (§8.8 dual-mechanism note)
grep -c "NFR-016" v2.25-spec-merged.md  # exactly 1 (§8.2 fail-closed)
grep -c "NFR-017" v2.25-spec-merged.md  # exactly 1 (§8.4 save_state coercion)
grep -c "NFR-018" v2.25-spec-merged.md  # exactly 1 (§8.8 max 3 attempts)
grep -c "NFR-019" v2.25-spec-merged.md  # exactly 1 (§14.9 dormancy)
```

**Content integrity spot-checks**:
```bash
grep "_inject_roadmap_hash" v2.25-spec-merged.md          # 1+ results in §3.3
grep "_check_annotate_deviations_freshness" v2.25-spec-merged.md  # 2+ results in §8.2
grep "_routing_ids_valid" v2.25-spec-merged.md            # 2+ results (fn spec + gate)
grep "DEV-\\\\d+" v2.25-spec-merged.md                   # 1+ results in §5.4 and §5.5
grep "State file may be corrupt" v2.25-spec-merged.md     # 1 result in §8.4
grep "Both recovery mechanisms are now exhausted" v2.25-spec-merged.md  # 1 result
grep "functionally dormant" v2.25-spec-merged.md          # 1 result in §14.9
```

**No orphaned section references** — verify cross-references to §8.7 and §14.7 from longterm content were updated to §8.8 and §14.9:
```bash
grep "§8\.7" v2.25-spec-merged.md
# Should return ONLY the "Spec-Patch Auto-Resume Cycle: Retirement" header and
# any references to the retirement section. FR-077's cross-reference should say §14.9.

grep "§14\.7" v2.25-spec-merged.md
# Should return ONLY the "Spec-Patch Auto-Resume Retirement" header (immediate §14.7)
# and NFR-011's reference to it. FR-076/§8.8 should reference §14.9, not §14.7.
```

**Acceptance criteria**: All checks pass. Report any failures as blockers before marking J-1 complete.

---

## v2.26 Deferred Items (do NOT implement in v2.25)

The following FR is spec-only in v2.25 — the **implementation** is deferred to v2.26:

| FR | Reason for deferral |
|----|---------------------|
| **FR-077 implementation** | Requires adding `spec_patch_attempted` boolean to `.roadmap-state.json` and a new write call in `execute_roadmap()`. Scenario (spec-patch fires AND remediation exhausts) is extremely unlikely. Spec text inserted; state schema extension deferred. |

When implementing in v2.26, add to backlog:
> "Implement state schema extension for `spec_patch_attempted` tracking to support FR-077 dual-mechanism halt message."

---

## Execution Order Summary

```
[After all immediate amendments complete]

B-1 (FR-055 §3.3 injection spec)      ─┐
A-1 (FR-070 §3.6 gate field)          ─┤
C-1 (FR-073 §5.4 ID format)           ─┤ all parallel
D-1 (FR-074 §5.5 routing_ids_valid)   ─┤
E-1 (FR-075 §7.2 parse_routing_list)  ─┤
F-1 (FR-071+NFR-016 §8.2 freshness)   ─┤
G-1 (FR-072+NFR-017 §8.4 int coerce)  ─┘

H-1 (§8.8 retry budget table)          ← depends on immediate §8.7 existing
I-1 (§14.9 dormancy note)              ← depends on immediate §14.8 existing

J-1 (full validation)                  ← depends on all above
```

Groups A–G have no mutual dependency among themselves and may be executed fully in parallel.
H-1 and I-1 require the immediate amendments to have run first but are independent of each other.
J-1 must be last.

---

## Reference: FR/NFR Canonical Numbers for This Tasklist

| Number | Type | Spec Section | v2.25/v2.26 | Summary |
|--------|------|-------------|-------------|---------|
| FR-055 | FR | §3.3 | v2.25 | Executor injects `roadmap_hash` into `spec-deviations.md` after `annotate-deviations` completes |
| FR-070 | FR | §3.6 | v2.25 | `ANNOTATE_DEVIATIONS_GATE` required fields include `roadmap_hash` |
| FR-071 | FR | §8.2 | v2.25 | `_apply_resume()` calls `_check_annotate_deviations_freshness()` before skipping `annotate-deviations` |
| NFR-016 | NFR | §8.2 | v2.25 | `_check_annotate_deviations_freshness()` is fail-closed; returns False on any error |
| FR-072 | FR | §8.4 | v2.25 | `_check_remediation_budget()` coerces `remediation_attempts` to int; warns on corrupt value |
| NFR-017 | NFR | §8.4 | v2.25 | `_save_state()` always writes `remediation_attempts` as Python int |
| FR-073 | FR | §5.4 | v2.25 | Deviation IDs SHALL match `DEV-\d+` pattern |
| FR-074 | FR | §5.5 | v2.25 | `_routing_ids_valid()` STRICT semantic check on `DEVIATION_ANALYSIS_GATE` |
| FR-075 | FR | §7.2 | v2.25 | `_parse_routing_list()` validates tokens against `^DEV-\d+$`; cross-checks vs `total_analyzed` |
| FR-076 | FR | §8.8 | v2.25 (doc) | Spec-patch and remediation counters remain independent; no global counter |
| FR-077 | FR | §8.8 | v2.26 (impl) | `_print_terminal_halt()` dual-mechanism exhaustion note |
| NFR-018 | NFR | §8.8 | v2.25 (doc) | Combined max 3 automatic recovery attempts |
| NFR-019 | NFR | §14.9 | v2.25 (doc) | `_apply_resume_after_spec_patch()` retained unchanged in v5 |
