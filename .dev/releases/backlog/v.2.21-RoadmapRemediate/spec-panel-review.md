---
review_type: spec-panel
target: spec-roadmap-remediate.md
date: 2026-03-09
panel: [wiegers, adzic, fowler, nygard, whittaker, crispin]
certification: CONDITIONAL_PASS
critical_count: 3
major_count: 7
minor_count: 8
---

# Spec Panel Review: v2.21 Roadmap Remediation Loop

## Certification Decision

**CONDITIONAL PASS** — Spec is well-structured, evidence-based, and demonstrates
deep understanding of the existing pipeline. Ready for roadmap/tasklist generation
**after** the 3 CRITICAL items are resolved. The 7 MAJOR items should be addressed
before tasklist generation but are not blockers for roadmap planning.

---

## CRITICAL Findings (must resolve before proceeding)

### C-01 [Fowler] Architectural Mismatch: Remediate Step vs. Step Model

The remediate step doesn't fit the existing `Step`/`execute_pipeline` model.
Each `Step` has one prompt, one output_file, and one gate. The remediate step
spawns N dynamic agents in parallel (one per file), each with a different
prompt, determined at runtime after parsing the validation report.

The existing parallel step mechanism (`list[Step]` groups in `_build_steps()`)
requires fixed step definitions at build time, not runtime-dynamic agents.

**Resolution options**:
- **(a) Internal dispatch** (recommended): `remediate_executor` runs its own
  parallel dispatch internally and presents as a single Step to the outer
  pipeline. Consistent with `validate_executor.py` which already has its own
  internal orchestration. The Step's `output_file` is `remediation-tasklist.md`,
  and the gate checks that file.
- (b) Pre-step parsing: A parse step runs first, constructs Step list dynamically.
- (c) Pipeline executor extension: Add `DynamicStepGroup` concept.

**Spec amendment needed**: State which option is chosen and how remediate
presents to `execute_pipeline()`.

### C-02 [Nygard] Partial Failure Semantics Undefined

When remediation agents run in parallel per-file and one agent fails while
others succeed:

- Are successful agents' changes kept? (Artifacts may be inconsistent)
- Cross-file findings (F-05) could be half-applied — one side fixed, other not
- The artifacts could be in a WORSE state than before remediation

**Example**: F-05 requires moving a test between roadmap.md and test-strategy.md.
Agent 1 (roadmap.md) adds the test to Phase 1. Agent 2 (test-strategy.md) fails.
Now roadmap.md claims a test exists in Phase 1 that test-strategy.md still lists
in Phase 2. This is a new consistency bug that didn't exist before remediation.

**Spec amendment needed**: Define partial failure behavior. Recommendation:
if any agent fails, revert all agents' changes for that remediation run
(or more simply: treat parallel agent group like existing pipeline parallel
groups — any failure halts all).

### C-03 [Whittaker] Zero-Actionable-Findings Path Undefined

**Attack**: User selects [3] All, but all 14 findings are marked
NO_ACTION_REQUIRED. After filtering, 0 actionable findings remain.

Current spec doesn't define:
- What does remediate emit for 0 findings? (Empty tasklist?)
- What does certify verify with 0 findings? (Vacuously true?)
- Does `per_finding_table_present` gate pass on an empty table?

**Spec amendment needed**: If 0 actionable findings after filtering, skip
remediate and certify, set state to "certified" directly. Add explicit guard:
`if len(actionable_findings) == 0: skip_to_certified()`.

---

## MAJOR Findings (address before tasklist generation)

### M-01 [Wiegers] SC-002 Measurement Ambiguity

"Remediation fixes ≥90% of BLOCKING findings on first pass" — measured how?
Agent exit code? Certification verification? If certification is the
measurement, SC-002 is redundant with SC-003 ("certification correctly
identifies unfixed findings").

**Fix**: Define measurement: "≥90% of BLOCKING findings receive PASS verdict
in the certification report (§2.4.3)."

### M-02 [Wiegers] SC-006 Baseline Undefined

"Pipeline time increase ≤30%" — 30% of what? Current pipeline runs 15-60min
depending on model and network. The baseline must be specified.

**Fix**: "Pipeline wall-clock time for steps 1-9 serves as baseline. Steps
10-11 add ≤30% to that wall-clock time."

### M-03 [Adzic] Cross-File Finding Prompt Splitting Unspecified

F-05 spans roadmap.md + test-strategy.md. The spec says both agents get it
"with guidance on which file each agent should edit" — but no example shows
how the prompt is split.

**Fix**: Add a concrete example showing the roadmap.md agent prompt fragment
and the test-strategy.md agent prompt fragment for the same cross-file finding.

### M-04 [Adzic] Fallback Deduplication Semantics Undefined

OQ-003 says "deduplicated by location + description similarity." What counts
as "similar"? Same file + overlapping line range? Fuzzy text match?

**Fix**: Define deduplication rule concretely. Recommendation: "Two findings
are duplicates if they reference the same file AND their location ranges
overlap (or are within 5 lines). On collision, take the higher severity."

### M-05 [Fowler] Interactive Prompt Breaks Pipeline Flow Model

`execute_pipeline()` is non-interactive. The user prompt between validate
and remediate either goes inside the executor (violating its contract) or
requires splitting the pipeline into two `execute_pipeline()` calls.

**Fix**: State that `execute_roadmap()` runs steps 1-9 via `execute_pipeline()`,
then handles the user prompt in its own logic (like `_auto_invoke_validate`
already does), then runs steps 10-11 via a second executor call or internal
dispatch.

### M-06 [Nygard] No Timeout or Retry for Remediation Agents

Existing steps specify `timeout_seconds` (300-900) and `retry_limit` (1).
Remediation agents have neither specified.

**Fix**: Add timeout (300s recommended — agents have scoped edits, not
generation) and retry_limit (1, consistent with other steps).

### M-07 [Whittaker] Resume Stale-Detection Missing

Resume checks "remediation-tasklist.md shows all FIXED" but doesn't verify
the tasklist matches the CURRENT validation report. A stale tasklist from
a prior run could cause resume to skip remediation for a completely different
set of findings.

**Fix**: Include `source_report_hash` in remediation-tasklist.md frontmatter.
Resume verifies hash matches current validation report before skipping.

---

## MINOR Findings (defer to implementation)

### m-01 [Wiegers] Finding.status Lifecycle

No definition of what triggers FAILED status or who sets it. Clarify: agent
exit non-zero → FAILED; agent exit 0 but certify says FAIL → status remains
FIXED (certification is a separate check).

### m-02 [Wiegers] NO_ACTION_REQUIRED Detection

The parser must detect NO_ACTION_REQUIRED from the validation report, but
this status isn't always present (it was manually added in reflect-merged.md).
Parser should handle reports with and without this column.

### m-03 [Wiegers] INFO-Only Prompt Behavior

Spec says skip prompt if 0 BLOCKING + 0 WARNING + 0 INFO. Consider: skip
prompt if 0 BLOCKING + 0 WARNING (regardless of INFO count), since INFO-only
remediation is low value and the prompt forces a decision.

### m-04 [Adzic] Relevant-Section Extraction Size

OQ-002 says "relevant sections" but doesn't define extraction radius. Suggest:
±30 lines around the finding location, or the entire markdown section (##/###)
containing the location.

### m-05 [Adzic] FAILED Entry Format

No example of a FAILED remediation-tasklist entry. Add:
`- [ ] F-03 | extraction.md | FAILED — agent exited with code 1`

### m-06 [Fowler] schema_version Bump

State JSON shows schema_version: 2, but spec claims backward-compatible additive
fields. Either keep version 1 (since changes are additive) or document what
consumers should do when they see version 2.

### m-07 [Nygard] validated-with-issues Reason

State should capture whether "validated-with-issues" means "user declined
remediation" vs. "pipeline error." Affects resume behavior.

### m-08 [Crispin] In-Place Edit Gate Checking

Remediation agents edit existing files (roadmap.md) rather than writing new
output files. How does gate checking work? The Step model expects an
output_file — is this remediation-tasklist.md (the status record) or the
edited artifact itself? (Connects to C-01 resolution.)

---

## Expert Consensus

All six experts agree:

1. The spec is **well above average** for a draft architecture document. Problem
   statement is evidence-based, constraints are explicit, existing patterns are
   respected, and the design is appropriately scoped.

2. The **core design is sound**: validate → user-prompt → remediate → certify
   is the right decomposition. Batch-by-file, no-loop, and user-controlled
   scope are good decisions.

3. The **three critical gaps** (architectural fit, partial failure, zero-findings
   path) must be resolved because they affect fundamental control flow. Without
   resolution, an implementer would have to make undocumented architectural
   decisions.

4. The spec is **ready for roadmap generation** once the 3 CRITICALs are
   amended as one-paragraph additions. The MAJORs can be resolved during
   roadmap-to-tasklist conversion.
