---
title: "v2.25 Immediate Amendments Tasklist"
source: approved-immediate.md
target: v2.25-spec-merged.md
compliance: strict
issues_addressed:
  - "ISSUE 1 (W-1, CRITICAL): Spec-patch cycle retirement"
  - "ISSUE 2 (W-ADV-1, CRITICAL): Empty routing_fix_roadmap silently drops SLIPs"
  - "ISSUE 3 (W-3, MAJOR): Artifact boundary undefined"
  - "ISSUE 4 (W-2, MAJOR): §11 compatibility surface missing"
  - "ISSUE 5 (W-4+W-5, MAJOR/MINOR): NFR-006 incomplete"
executor: sc:task-unified
---

# v2.25 Immediate Amendments — Implementation Tasklist

All tasks operate on:
- **Target file**: `.dev/releases/backlog/2.25-roadmap-v5/v2.25-spec-merged.md`
- **Source of truth**: `.dev/releases/backlog/2.25-roadmap-v5/approved-immediate.md`

Tasks are ordered by dependency. Tasks within the same group may be parallelized.
CRITICAL issues (1 and 2) must complete before implementation of `executor.py` and `gates.py` begins.

---

## GROUP A — Structural Setup (prerequisite for all other tasks)

### TASK A-1: Renumber §3 subsections 3.1–3.5 → 3.2–3.6

**Issue**: ISSUE 3 (W-3)
**Priority**: MAJOR — must happen before A-2 inserts new §3.1
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, rename the following section headings (headers and all cross-references to them throughout the document):

| Old heading | New heading |
|-------------|-------------|
| `### 3.1 Step Definition` | `### 3.2 Step Definition` |
| `### 3.2 Step Construction in \`_build_steps()\`` | `### 3.3 Step Construction in \`_build_steps()\`` |
| `### 3.3 Prompt Design: \`build_annotate_deviations_prompt()\`` | `### 3.4 Prompt Design: \`build_annotate_deviations_prompt()\`` |
| `### 3.4 Output Format: \`spec-deviations.md\`` | `### 3.5 Output Format: \`spec-deviations.md\`` |
| `### 3.5 Gate Definition` | `### 3.6 Gate Definition` |

Also update any cross-references in the document body (e.g., "§3.1", "§3.2", "(§3.5)") to reflect the new numbers. Search for all occurrences of `§3.1`, `§3.2`, `§3.3`, `§3.4`, `§3.5` and update each to its new number.

**Acceptance criteria**:
- `grep "### 3\." v2.25-spec-merged.md` shows headings 3.1 through 3.6 with 3.1 being the new taxonomy table
- No remaining references to old §3.1 (Step Definition) with the old number
- `grep "### 3.1" v2.25-spec-merged.md` returns only the new Artifact Taxonomy heading

---

## GROUP B — New §3.1 Insertion (depends on A-1)

### TASK B-1: Insert §3.1 Artifact Taxonomy table

**Issue**: ISSUE 3 (W-3)
**Priority**: MAJOR
**FR/NFR**: no new FR number — structural addition
**Compliance**: strict

**What to do**:
After the `## 3. New Step: \`annotate-deviations\` (Scope 2 -- Prevention)` heading and its brief introductory sentence (if any), and BEFORE the (now-renumbered) `### 3.2 Step Definition` heading, insert the following new subsection verbatim from `approved-immediate.md` ISSUE 3 Draft Spec Language:

```
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
```

**Acceptance criteria**:
- `grep -n "### 3.1" v2.25-spec-merged.md` returns exactly one match: "Artifact Taxonomy: Deviation-Related Files"
- The table with "Glob pattern", "Writer", "Readers" columns is present
- The critical implementation note is present

---

## GROUP C — §5.5 Gate Updates (CRITICAL — depends on no prior task)

### TASK C-1: Add `_routing_consistent_with_slip_count()` function to §5.5

**Issue**: ISSUE 2 (W-ADV-1, CRITICAL)
**Priority**: CRITICAL — blocks gates.py implementation
**FR/NFR**: FR-056
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 5.5 Gate Definition` and find the existing `DEVIATION_ANALYSIS_GATE` definition block. After the closing `}` of that definition (and before any subsequent content in §5.5), insert the following new FR block verbatim from `approved-immediate.md` ISSUE 2 Draft Spec Language:

```
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
```

**Acceptance criteria**:
- `grep "FR-056" v2.25-spec-merged.md` returns a match in §5.5
- `grep "_routing_consistent_with_slip_count" v2.25-spec-merged.md` returns the function definition

---

### TASK C-2: Replace `DEVIATION_ANALYSIS_GATE` definition with updated version (adds third semantic check)

**Issue**: ISSUE 2 (W-ADV-1, CRITICAL)
**Priority**: CRITICAL — blocks gates.py implementation
**FR/NFR**: FR-057
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md` `### 5.5 Gate Definition`, replace the existing `DEVIATION_ANALYSIS_GATE = GateCriteria(...)` Python block with the updated version from `approved-immediate.md` ISSUE 2 Draft Spec Language. The updated gate adds a third `SemanticCheck` for `routing_consistent_with_slip_count`.

Precede the replacement block with this FR label:

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
```

Then the full `DEVIATION_ANALYSIS_GATE = GateCriteria(...)` block from approved-immediate.md (lines 152–194).

**Acceptance criteria**:
- `grep "FR-057" v2.25-spec-merged.md` returns a match in §5.5
- `grep "routing_consistent_with_slip_count" v2.25-spec-merged.md` returns at least 3 matches (function def, gate field, SemanticCheck name)
- The `DEVIATION_ANALYSIS_GATE` block in §5.5 contains exactly 3 `SemanticCheck` entries

---

## GROUP D — §7.2 Secondary Guard (CRITICAL — may run parallel to GROUP C)

### TASK D-1: Add `ValueError` secondary guard to `deviations_to_findings()` in §7.2

**Issue**: ISSUE 2 (W-ADV-1, CRITICAL)
**Priority**: CRITICAL — blocks executor.py implementation
**FR/NFR**: FR-058
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md` `### 7.2 Deviation-to-Finding Conversion`, locate the `deviations_to_findings()` code listing. Find the block that contains `if not fix_ids: return []`. Replace that block with the expanded version from `approved-immediate.md` ISSUE 2 Draft Spec Language (FR-058), which adds the secondary guard check for `slip_count > 0`.

Precede the updated code block with:

```
**FR-058**: The `deviations_to_findings()` function SHALL include a secondary guard: if
`_parse_routing_list()` returns an empty list AND frontmatter `slip_count > 0`, the function
SHALL raise `ValueError` with a message indicating the artifact is inconsistent. This guard is
defense-in-depth against gate bypass and direct function calls in test harnesses.

**Add to §7.2 (Deviation-to-Finding Conversion), immediately after the `if not fix_ids: return []`
block in the `deviations_to_findings()` code listing**:
```

Then insert the full code block from approved-immediate.md (the `if not fix_ids:` block with the ValueError raise).

**Acceptance criteria**:
- `grep "FR-058" v2.25-spec-merged.md` returns a match in §7.2
- `grep "ValueError" v2.25-spec-merged.md` returns a match in §7.2
- `grep "slip_count > 0" v2.25-spec-merged.md` returns a match in the deviations_to_findings context

---

## GROUP E — §8.7 New Section (CRITICAL — depends on no prior task)

### TASK E-1: Insert new §8.7 "Spec-Patch Auto-Resume Cycle: Retirement"

**Issue**: ISSUE 1 (W-1, CRITICAL)
**Priority**: CRITICAL — blocks executor.py implementation
**FR/NFR**: FR-059
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 8.6 Resume Flow: Post-Pipeline Remediate-Certify` (the last subsection of §8). After its content ends (before `## 9.`), insert the following new subsection verbatim from `approved-immediate.md` ISSUE 1 Draft Spec Language:

```
### 8.7 Spec-Patch Auto-Resume Cycle: Retirement

**FR-059**: As of v2.25, the spec-patch auto-resume cycle introduced in v2.24.2
(`_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, `initial_spec_hash`,
`_spec_patch_cycle_count`) SHALL be retired from `executor.py`. The trigger check in
`execute_roadmap()` — which fired when `spec_fidelity_failed == True` — SHALL be removed.

**Rationale**: [full rationale paragraph from approved-immediate.md]

**Scope of retirement** (code to be deleted from `executor.py`):
- The `_spec_patch_cycle_count = 0` local variable in `execute_roadmap()`
- The `initial_spec_hash = hashlib.sha256(...)` capture in `execute_roadmap()`
- The `spec_fidelity_failed` boolean and the `if spec_fidelity_failed:` block in `execute_roadmap()`
- The `_apply_resume_after_spec_patch()` function definition (~90 lines)
- The `_find_qualifying_deviation_files()` function definition (~45 lines)
- The `auto_accept` parameter from `execute_roadmap()` signature

**Not retired**: [full "Not retired" paragraph from approved-immediate.md]
```

Copy exact text from `approved-immediate.md` ISSUE 1 `### Draft Spec Language` → `#### 8.7 Spec-Patch Auto-Resume Cycle: Retirement` block (lines 25–53).

**Acceptance criteria**:
- `grep "### 8.7" v2.25-spec-merged.md` returns exactly one match
- `grep "FR-059" v2.25-spec-merged.md` returns matches in §8.7
- `grep "_apply_resume_after_spec_patch" v2.25-spec-merged.md` returns at least one match in §8.7 scope-of-retirement list

---

## GROUP F — §11.5 New Section (depends on no prior task, may run parallel)

### TASK F-1: Insert new §11.5 "v2.24.2 → v2.25 Compatibility Surface: executor.py"

**Issue**: ISSUE 4 (W-2, MAJOR)
**Priority**: MAJOR — documentation, no implementation blocker
**FR/NFR**: no new FR — structural addition
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `## 11. Affected Files Summary`. After the last existing table or content in §11 (before `## 12.`), insert the full §11.5 block verbatim from `approved-immediate.md` ISSUE 4 Draft Spec Language:

```
### 11.5 v2.24.2 → v2.25 Compatibility Surface: `executor.py`

The following table maps every v2.24.2 symbol in `executor.py` to its v2.25 disposition. [...]

| v2.24.2 Symbol in `executor.py` | v2.25 Disposition | FR Reference |
|----------------------------------|-------------------|--------------|
| `execute_roadmap(config, resume, no_validate, auto_accept)` — function signature | MODIFIED: `auto_accept` parameter removed | FR-059 |
| `_spec_patch_cycle_count = 0` ... | RETIRED | FR-059 |
[... all 18 rows from approved-immediate.md ...]

**Implementation note**: The six symbols marked RETIRED (FR-059) constitute approximately 130
lines of code. [...]
```

Copy exact content from `approved-immediate.md` ISSUE 4 `### Draft Spec Language` → `### 11.5` block (lines 299–331).

**Acceptance criteria**:
- `grep "### 11.5" v2.25-spec-merged.md` returns exactly one match
- `grep "RETIRED" v2.25-spec-merged.md` returns 5+ matches in §11.5 (the 5 RETIRED rows)
- `grep "auto_accept" v2.25-spec-merged.md` returns at least one match in §11.5

---

## GROUP G — §14 Updates (may run parallel to other groups)

### TASK G-1: Replace §14.2 content with updated NFR-006

**Issue**: ISSUE 5 (W-4+W-5, MAJOR/MINOR)
**Priority**: MAJOR — documentation
**FR/NFR**: NFR-006 (full replacement)
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 14.2 Spec-Fidelity Gate`. Replace the entire content of that subsection (everything between `### 14.2` and the next `### 14.3`) with the updated text from `approved-immediate.md` ISSUE 5 Draft Spec Language → `#### 14.2 Spec-Fidelity Gate Downgrade: Relaxation and Behavioral Consequences`.

The replacement heading should become:
```
### 14.2 Spec-Fidelity Gate Downgrade: Relaxation and Behavioral Consequences
```

Then insert the full NFR-006 block with all four clauses (a) through (d) verbatim from `approved-immediate.md` lines 343–372.

**Acceptance criteria**:
- `grep "NFR-006" v2.25-spec-merged.md` returns a match in §14.2
- `grep "Forward compatibility" v2.25-spec-merged.md` returns a match in §14.2 context
- `grep "Behavioral flip" v2.25-spec-merged.md` returns a match
- `grep "spec-patch auto-resume dormancy" v2.25-spec-merged.md` returns a match
- `grep "Existing state file compatibility" v2.25-spec-merged.md` returns a match

---

### TASK G-2: Insert new §14.7 "Spec-Patch Auto-Resume Retirement"

**Issue**: ISSUE 1 (W-1, CRITICAL)
**Priority**: CRITICAL (backward-compat documentation for the retirement)
**FR/NFR**: NFR-011
**Compliance**: strict

**What to do**:
In `v2.25-spec-merged.md`, locate `### 14.6 Pipeline Executor` (the last subsection of §14). After its content ends (before `## 15.`), insert the new §14.7 block verbatim from `approved-immediate.md` ISSUE 1 Draft Spec Language → `#### 14.7 Spec-Patch Auto-Resume Retirement`:

```
### 14.7 Spec-Patch Auto-Resume Retirement

**NFR-011**: The `_apply_resume_after_spec_patch()` auto-resume cycle SHALL NOT be present in
v2.25 executor.py. Operators who relied on automatic spec-patch auto-resume in v2.24.x SHALL
use explicit `--resume` invocations after any spec modification.

[full three-condition list]

In v2.25, Condition 1 never occurs in normal operation because `SPEC_FIDELITY_GATE` is STANDARD
(no semantic checks). The recovery mechanism that replaced the spec-patch cycle is:

[bullet list]

Existing `.roadmap-state.json` files containing `spec_hash` entries remain valid. The
`accept-spec-change` CLI command continues to update `spec_hash` for manual use.
```

Copy exact text from `approved-immediate.md` lines 59–79.

**Acceptance criteria**:
- `grep "### 14.7" v2.25-spec-merged.md` returns exactly one match
- `grep "NFR-011" v2.25-spec-merged.md` returns a match in §14.7
- `grep "explicit.*--resume" v2.25-spec-merged.md` returns a match in §14.7 context

---

### TASK G-3: Insert new §14.8 "Deviation Artifact Taxonomy (Cross-Reference)"

**Issue**: ISSUE 3 (W-3, MAJOR)
**Priority**: MAJOR
**FR/NFR**: NFR-012
**Compliance**: strict
**Depends on**: G-2 (insert after §14.7)

**What to do**:
After the §14.7 block inserted by G-2, insert the new §14.8 block verbatim from `approved-immediate.md` ISSUE 3 Draft Spec Language → `#### 14.8 Deviation Artifact Taxonomy (Cross-Reference)`:

```
### 14.8 Deviation Artifact Taxonomy (Cross-Reference)

See §3.1 for the full artifact taxonomy table. In summary: `spec-deviations.md` (new in v2.25,
written by `annotate-deviations` step, consumed by `spec-fidelity` and `deviation-analysis`) and
`dev-*-accepted-deviation.md` (v2.24.2, written by subprocess agents, consumed only by the
`roadmap accept-spec-change` CLI command in v2.25) serve completely different purposes and MUST
NOT be confused.

**NFR-012**: No pipeline step introduced or modified in v2.25 SHALL read `dev-*-accepted-deviation.md`
files as part of its normal execution. The `dev-*-accepted-deviation.md` artifact format is
consumed exclusively by `spec_patch.py` / the `roadmap accept-spec-change` CLI command.
```

Copy exact text from `approved-immediate.md` lines 266–276.

**Acceptance criteria**:
- `grep "### 14.8" v2.25-spec-merged.md` returns exactly one match
- `grep "NFR-012" v2.25-spec-merged.md` returns a match in §14.8
- `grep "Cross-Reference" v2.25-spec-merged.md` returns a match in §14 context

---

## GROUP H — Final Validation (depends on all prior tasks)

### TASK H-1: Full spec consistency verification

**Priority**: CRITICAL gate
**Compliance**: strict

Run each of the following checks against the modified `v2.25-spec-merged.md`:

**Section structure checks**:
```bash
grep "^### 3\." v2.25-spec-merged.md
# Expected: 3.1 Artifact Taxonomy, 3.2 Step Definition, 3.3 Prompt Design, 3.4 Output Format, 3.5 Gate Definition, 3.6 Gate Definition
# NOTE: 3.5 is annotate-deviations gate, 3.6 does not exist — adjust based on actual renumbering result

grep "^### 8\." v2.25-spec-merged.md
# Expected: 8.1 through 8.7 present

grep "^### 11\." v2.25-spec-merged.md
# Expected: 11.5 present (alongside existing 11.x subsections if any)

grep "^### 14\." v2.25-spec-merged.md
# Expected: 14.1 through 14.8 present
```

**FR/NFR presence checks**:
```bash
grep -c "FR-056" v2.25-spec-merged.md   # ≥1
grep -c "FR-057" v2.25-spec-merged.md   # ≥1
grep -c "FR-058" v2.25-spec-merged.md   # ≥1
grep -c "FR-059" v2.25-spec-merged.md   # ≥1 (in §8.7 and §11.5 and §14.7)
grep -c "NFR-006" v2.25-spec-merged.md  # ≥1 (in §14.2)
grep -c "NFR-011" v2.25-spec-merged.md  # ≥1 (in §14.7)
grep -c "NFR-012" v2.25-spec-merged.md  # ≥1 (in §14.8)
```

**No stale FR-055 retirement references** (FR-055 should only refer to ALL_GATES if present):
```bash
grep "FR-055" v2.25-spec-merged.md
# Verify: any remaining FR-055 references should ONLY be in the context of ALL_GATES (FR-054 row
# or its own entry). There should be NO "FR-055: spec-patch retirement" language remaining.
```

**Content integrity spot-checks**:
```bash
grep "_routing_consistent_with_slip_count" v2.25-spec-merged.md | wc -l   # ≥3
grep "DEVIATION_ANALYSIS_GATE" v2.25-spec-merged.md | wc -l               # ≥2
grep "Artifact Taxonomy" v2.25-spec-merged.md                              # 1 result
grep "Compatibility Surface" v2.25-spec-merged.md                          # 1 result
grep "NFR-011" v2.25-spec-merged.md                                        # 1+ results
```

**Acceptance criteria**: All checks pass. Report any failures as blockers before marking H-1 complete.

---

## Execution Order Summary

```
A-1 (renumber §3 subsections)
  └─► B-1 (insert §3.1 taxonomy)

C-1 (add _routing_consistent_with_slip_count fn) ─┐
C-2 (update DEVIATION_ANALYSIS_GATE)              ─┤ parallel
D-1 (add ValueError guard to §7.2)               ─┤
E-1 (insert §8.7 retirement)                     ─┤
F-1 (insert §11.5 compat table)                  ─┤
G-1 (replace §14.2 NFR-006)                      ─┘

G-2 (insert §14.7)
  └─► G-3 (insert §14.8)

H-1 (full validation) ← depends on all above
```

**Groups C, D, E, F, G-1** have no mutual dependency and may be executed in parallel.
**Group A → B** must be sequential.
**G-2 → G-3** must be sequential.
**H-1** must be last.

---

## Reference: FR/NFR Canonical Numbers for This Tasklist

| Number | Type | Section | Summary |
|--------|------|---------|---------|
| FR-056 | FR | §5.5 | `_routing_consistent_with_slip_count()` function in `gates.py` |
| FR-057 | FR | §5.5 | `DEVIATION_ANALYSIS_GATE` third semantic check |
| FR-058 | FR | §7.2 | `deviations_to_findings()` secondary ValueError guard |
| FR-059 | FR | §8.7 | Spec-patch auto-resume cycle retirement |
| NFR-006 | NFR | §14.2 | Spec-fidelity gate downgrade behavioral consequences (full replacement) |
| NFR-011 | NFR | §14.7 | Auto-resume not in v2.25; use explicit --resume |
| NFR-012 | NFR | §14.8 | No pipeline step reads dev-*-accepted-deviation.md |

Structural insertions (no FR number):
- §3.1 Artifact Taxonomy (new subsection)
- §11.5 v2.24.2 → v2.25 Compatibility Surface (new subsection)
- §14.7 Spec-Patch Auto-Resume Retirement (new subsection)
- §14.8 Deviation Artifact Taxonomy Cross-Reference (new subsection)
