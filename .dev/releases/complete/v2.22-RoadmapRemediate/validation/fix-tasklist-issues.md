# Fix Tasklist Issues — v2.22 RoadmapRemediate
# Workflow generated from parallel validation of 7 phase tasklist files vs roadmap

## Metadata

| Field | Value |
|---|---|
| Source | Validation report: 7 parallel quality-engineer agents |
| Scope | phase-1-tasklist.md through phase-7-tasklist.md |
| Total Issues | 0 Critical, 2 Major, 14 Minor |
| Total Fix Tasks | 16 |
| Files Modified | phase-2-tasklist.md, phase-4-tasklist.md, phase-5-tasklist.md, phase-6-tasklist.md, phase-7-tasklist.md, phase-1-tasklist.md |

---

## Dependency Order

```
FIX-01 (P5/T05.05 - CERTIFY_GATE field)   — no deps, highest priority
FIX-02 (P4/T04.05 - stray FR-018)         — no deps
FIX-03 (P4 - NFR-008 ownership)           — no deps
FIX-04 (P6/T06.02 - hash acceptance)      — no deps
FIX-05 (P4/T04.09 - backup mechanism)     — no deps
FIX-06 (P4/T04.08 - SKIPPED criterion)    — no deps
FIX-07 (P2/T02.03 - parser AC)            — no deps
FIX-08 (P7 checkpoint sequencing)         — no deps
FIX-09 (P7/T07.05 - delegation level)     — no deps
FIX-10 (P1/T01.02 - confidence note)      — no deps
FIX-11 (P1/T01.02 - risk drivers)         — no deps
FIX-12 (P1 checkpoint - M0 label)         — no deps
FIX-13 (P2/T02.03 - risk rating)          — no deps
FIX-14 (P2/T02.05 - coverage threshold)   — no deps
FIX-15 (P4/T04.10 - tier note)            — no deps
FIX-16 (P7/T07.09 - artifact naming)      — no deps
```

All fixes are independent edits to different files/sections. They may be executed in any order or in parallel batches.

---

## Fix Tasks

---

### FIX-01 — Add `certification_date` to CERTIFY_GATE required fields [PRIORITY 1]

| Field | Value |
|---|---|
| Phase File | `phase-5-tasklist.md` |
| Task | T05.05 |
| Issue Severity | MINOR (highest priority — latent validation gap) |
| Issue | CERTIFY_GATE.required_frontmatter_fields lists only 4 fields; `certification_date` is missing. T05.03 generates the field but the gate won't enforce it. |
| Roadmap Ref | R-036, FR-028 |

**What to change in phase-5-tasklist.md, task T05.05:**

1. Find the `CERTIFY_GATE` deliverable definition in T05.05 (the `required_frontmatter_fields` list).
2. Add `certification_date` as the 5th required field alongside: `findings_verified`, `findings_passed`, `findings_failed`, `certified`.
3. In the `Why` field metadata row, update the gate field enumeration to list all 5 fields.
4. In the Acceptance Criteria block, update the criterion that references required fields to enumerate all 5 explicitly.

**Verification:** After edit, grep T05.05 for `certification_date` — must appear in at least 3 locations: required_frontmatter_fields list, Why enumeration, and Acceptance Criteria.

---

### FIX-02 — Replace stray `FR-018` reference in T04.05 [PRIORITY 2]

| Field | Value |
|---|---|
| Phase File | `phase-4-tasklist.md` |
| Task | T04.05 |
| Issue Severity | MAJOR |
| Issue | Acceptance criteria cite `FR-018` which does not exist in Phase 4's roadmap item set. R-018 (file grouping) is a different item already owned by T04.02. Creates naming collision and implementer confusion. |
| Roadmap Ref | R-023, FR-012, FR-019 |

**What to change in phase-4-tasklist.md, task T04.05:**

1. Find the Acceptance Criteria line containing `FR-018, FR-019` (the ClaudeProcess agent-spawning criterion).
2. Replace `FR-018` with `FR-012` (the correct functional requirement for parallel agent execution).
3. Result should read: `Agents spawned via ClaudeProcess matching validate_executor.py pattern (FR-012, FR-019)`.
4. Search entire T04.05 for any other occurrences of `FR-018` and apply the same replacement.

**Verification:** After edit, `grep "FR-018" phase-4-tasklist.md` must return 0 matches.

---

### FIX-03 — Assign NFR-008 wall-clock measurement ownership in Phase 4 [PRIORITY 3]

| Field | Value |
|---|---|
| Phase File | `phase-4-tasklist.md` |
| Task | T04.10 (step addition) |
| Issue Severity | MINOR |
| Issue | End-of-phase checkpoint requires `<=30% wall-clock overhead (NFR-008)` but no task owns measuring it. The exit criterion is unverifiable without a measurement step. |
| Roadmap Ref | NFR-008, SC-006 |

**What to change in phase-4-tasklist.md, task T04.10:**

1. Add a new `[VERIFICATION]` step at the end of the Steps list in T04.10:
   ```
   [VERIFICATION] Capture wall-clock timing of steps 10-11 execution and assert <=30% overhead vs steps 1-9 baseline (NFR-008). Record timing in D-0023/spec.md under "Performance Notes" section.
   ```
2. Add `NFR-008` to the Why field reference list for T04.10.
3. Add an Acceptance Criterion: `Steps 10-11 wall-clock overhead is <=30% vs steps 1-9 baseline per NFR-008 (timing recorded in D-0023/spec.md)`.

**Verification:** After edit, `grep "NFR-008" phase-4-tasklist.md` must return matches inside T04.10 (not only in the checkpoint section).

---

### FIX-04 — Strengthen T06.02 acceptance criterion to include hash-based check [PRIORITY 4]

| Field | Value |
|---|---|
| Phase File | `phase-6-tasklist.md` |
| Task | T06.02 |
| Issue Severity | MINOR |
| Issue | T06.02 Acceptance Criteria say "gate-based" but the roadmap exit criterion requires "gate- and hash-based, not timestamp-only". The hash check exists in the implementation steps but is absent from the formal acceptance criterion, creating a verifiability gap. |
| Roadmap Ref | FR-030, Phase 5 exit criteria |

**What to change in phase-6-tasklist.md, task T06.02:**

1. Find the Acceptance Criteria line that reads "Resume decisions are gate-based" (or similar).
2. Expand it to: `Resume decisions are gate- and hash-based, not timestamp-only (gate check passes AND source_report_hash matches current report)`.
3. Ensure the hash verification is listed as a separate bullet if the criterion was a single item.

**Verification:** After edit, T06.02 Acceptance Criteria must contain both "gate" and "hash" in the same criterion, plus the phrase "not timestamp-only".

---

### FIX-05 — Define tasklist rollback mechanism in T04.09 [PRIORITY 5]

| Field | Value |
|---|---|
| Phase File | `phase-4-tasklist.md` |
| Task | T04.09 |
| Issue Severity | MINOR |
| Issue | T04.09 rollback section references a "pre-update backup" of remediation-tasklist.md but no Phase 4 task defines how this backup is created. The mechanism is implicit and untestable as written. |
| Roadmap Ref | R-027 |

**What to change in phase-4-tasklist.md, task T04.09:**

1. Find the rollback/failure handling section of T04.09 that mentions "pre-update backup".
2. Replace the reference with an explicit mechanism: `Rollback: Restore remediation-tasklist.md from in-memory original content captured before write (not a file backup — use atomic tmp + os.replace() so failure leaves original intact per NFR-005)`.
3. Alternatively if a file backup is intended, add a step: `[EXECUTION] Before writing outcomes, copy remediation-tasklist.md to remediation-tasklist.md.pre-outcomes as rollback target`.
4. Add an Acceptance Criterion: `If outcome write fails, remediation-tasklist.md is either unchanged (atomic write via tmp+os.replace) or restored from .pre-outcomes backup`.

**Verification:** After edit, T04.09 rollback description must not reference an undefined mechanism.

---

### FIX-06 — Add SKIPPED findings acceptance criterion to T04.08 [PRIORITY 6]

| Field | Value |
|---|---|
| Phase File | `phase-4-tasklist.md` |
| Task | T04.08 |
| Issue Severity | MINOR |
| Issue | T04.08 success handler acceptance criteria only cover agent-targeted findings (set to FIXED). SKIPPED findings (allowlist-rejected) are not mentioned — an implementer could inadvertently overwrite SKIPPED status. |
| Roadmap Ref | R-026 |

**What to change in phase-4-tasklist.md, task T04.08:**

1. Find the Acceptance Criteria block in T04.08.
2. Add a new criterion: `SKIPPED findings (those rejected by allowlist enforcement in T04.04) remain in SKIPPED status and are not modified by the success handler`.
3. Optionally add a corresponding step: `[VERIFICATION] Confirm SKIPPED findings are untouched by inspecting finding status list before/after success handler execution`.

**Verification:** After edit, T04.08 Acceptance Criteria must contain the word "SKIPPED".

---

### FIX-07 — Add `merged-validation-report.md` to T02.03 acceptance criteria [PRIORITY 7]

| Field | Value |
|---|---|
| Phase File | `phase-2-tasklist.md` |
| Task | T02.03 |
| Issue Severity | MINOR |
| Issue | T02.03 acceptance criteria validates the parser against `reflect-merged.md` only. `merged-validation-report.md` (the second required target per R-007/FR-001) is named in the Why/Steps but absent from formal acceptance criteria. The parser could pass verification without being tested against the second format. |
| Roadmap Ref | R-007, FR-001 |

**What to change in phase-2-tasklist.md, task T02.03:**

1. Find the Acceptance Criteria block in T02.03.
2. Locate the criterion that validates parser extraction from `reflect-merged.md` format.
3. Add a parallel criterion: `Parser correctly extracts all Finding fields from merged-validation-report.md format (distinct structure from reflect-merged.md)`.
4. Update the Validation block to include: `uv run pytest tests/roadmap/test_remediate_parser.py -k "merged_validation_report"` or similar scoped test invocation.

**Verification:** After edit, T02.03 Acceptance Criteria must reference both `reflect-merged.md` and `merged-validation-report.md`.

---

### FIX-08 — Move regression exit criterion to end-of-phase checkpoint in Phase 7 [PRIORITY 8]

| Field | Value |
|---|---|
| Phase File | `phase-7-tasklist.md` |
| Task | Mid-phase checkpoint CP-P07-T01-T05 |
| Issue Severity | MINOR |
| Issue | Mid-phase checkpoint (covering T07.01-T07.05) lists "No regressions in existing pipeline steps 1-9" as an exit criterion, but T07.08 (the regression test task) executes after this checkpoint. The criterion cannot be verified at that point. |
| Roadmap Ref | R-053 |

**What to change in phase-7-tasklist.md, mid-phase checkpoint section:**

1. Find the checkpoint CP-P07-T01-T05 (or equivalent mid-phase checkpoint covering T07.01-T07.05).
2. Remove the exit criterion "No regressions in existing pipeline steps 1-9" from the mid-phase checkpoint.
3. Verify this criterion already exists in the end-of-phase checkpoint CP-P07-END (it should — add it if missing).
4. Optionally add a note to the mid-phase checkpoint: `Regression testing deferred to T07.08 (end-of-phase)`.

**Verification:** After edit, the mid-phase checkpoint must not claim regression coverage; the end-of-phase checkpoint must include it.

---

### FIX-09 — Change T07.05 Sub-Agent Delegation from "Recommended" to "Required" [PRIORITY 9]

| Field | Value |
|---|---|
| Phase File | `phase-7-tasklist.md` |
| Task | T07.05 |
| Issue Severity | MINOR |
| Issue | T07.05 is STRICT tier (same as T07.01) and the deliverable registry classifies D-0039 as Sub-agent verification, but T07.05 metadata says "Recommended" while T07.01 says "Required". Inconsistent across same-tier tasks. |
| Roadmap Ref | R-050, D-0039 |

**What to change in phase-7-tasklist.md, task T07.05:**

1. Find the metadata table row `Sub-Agent Delegation | Recommended` in T07.05.
2. Change the value to `Required`.
3. If T07.05 has a delegation note elsewhere (e.g., in steps), ensure it is consistent.

**Verification:** After edit, T07.05 `Sub-Agent Delegation` field must read `Required`.

---

### FIX-10 — Add uncertainty rationale to T01.02 confidence score [PRIORITY 10]

| Field | Value |
|---|---|
| Phase File | `phase-1-tasklist.md` |
| Task | T01.02 |
| Issue Severity | MINOR |
| Issue | T01.02 confidence is 72% — atypically low for an EXEMPT read-only confirmation task where all three open questions are pre-resolved in the roadmap. Low confidence without explanation may cause unnecessary hesitation or re-investigation. |
| Roadmap Ref | R-003 |

**What to change in phase-1-tasklist.md, task T01.02:**

1. Find the Notes field (or add one) in T01.02's metadata table.
2. Add or expand the note: `72% confidence reflects genuine uncertainty in ClaudeProcess SIGINT/signal-forwarding behavior — subprocess cleanup behavior may differ from documented behavior. All other OQs (hash algorithm, step wiring) have pre-determined answers per roadmap §7. Confidence would be higher if ClaudeProcess behavior were pre-validated.`

**Verification:** After edit, T01.02 must have a Notes entry explaining the confidence score.

---

### FIX-11 — Fix T01.02 Risk Drivers field (inconsistent with Risk level) [PRIORITY 11]

| Field | Value |
|---|---|
| Phase File | `phase-1-tasklist.md` |
| Task | T01.02 |
| Issue Severity | MINOR |
| Issue | T01.02 Risk is "Low" but Risk Drivers is "None" — internally inconsistent. Low risk implies at least one driver exists. |
| Roadmap Ref | R-003 |

**What to change in phase-1-tasklist.md, task T01.02:**

1. Find the metadata table row `Risk Drivers | None` in T01.02.
2. Replace `None` with `subprocess signal behavior (ClaudeProcess SIGINT handling uncertain)`.

**Verification:** After edit, T01.02 `Risk Drivers` field must not be "None" when Risk is "Low".

---

### FIX-12 — Add M0 milestone label to Phase 1 checkpoint [PRIORITY 12]

| Field | Value |
|---|---|
| Phase File | `phase-1-tasklist.md` |
| Task | End-of-Phase 1 checkpoint section |
| Issue Severity | MINOR |
| Issue | Phase 1 checkpoint does not reference the roadmap milestone M0 — Architecture decisions locked. Missing label weakens traceability from checkpoint reports back to the roadmap. |
| Roadmap Ref | Roadmap Phase 0 exit criteria |

**What to change in phase-1-tasklist.md, checkpoint section:**

1. Find the end-of-Phase 1 checkpoint header.
2. Add `**Milestone:** M0 — Architecture decisions locked` as the first line of the checkpoint body (before Exit Criteria or Scope).

**Verification:** After edit, the Phase 1 checkpoint section must contain the string "M0".

---

### FIX-13 — Raise T02.03 risk rating from Low to Medium [PRIORITY 13]

| Field | Value |
|---|---|
| Phase File | `phase-2-tasklist.md` |
| Task | T02.03 |
| Issue Severity | MINOR |
| Issue | The primary parser (T02.03) is the critical dependency for every downstream phase. A "Low / None" risk classification is inconsistent with its architectural role, risking under-investment in defensive implementation. |
| Roadmap Ref | R-007, Roadmap Phase 1 Analyzer Priority note |

**What to change in phase-2-tasklist.md, task T02.03:**

1. Find the metadata table rows `Risk | Low` and `Risk Drivers | None` in T02.03.
2. Change `Risk` to `Medium`.
3. Change `Risk Drivers` to `format-variance (report format fragility is explicitly called out as high-priority risk in roadmap Phase 1 Analyzer Priority note and Risk R-002)`.

**Verification:** After edit, T02.03 `Risk` must be `Medium` and `Risk Drivers` must be non-empty.

---

### FIX-14 — Add 100% coverage enforcement to T02.05 acceptance criteria [PRIORITY 14]

| Field | Value |
|---|---|
| Phase File | `phase-2-tasklist.md` |
| Task | T02.05 |
| Issue Severity | MINOR |
| Issue | The roadmap Phase 1 exit criterion requires "100% unit test coverage on parser and data model." T02.05 requires 3+ format variants and passing tests, but the coverage threshold is only enforced at the checkpoint level — not within the task's own acceptance criteria. |
| Roadmap Ref | R-009, Roadmap Phase 1 exit criteria |

**What to change in phase-2-tasklist.md, task T02.05:**

1. Find the Acceptance Criteria block in T02.05.
2. Add a criterion: `Unit test coverage for remediate_parser.py and Finding dataclass reaches 100% (measured via uv run pytest tests/roadmap/test_remediate_parser.py --cov=superclaude --cov-report=term-missing)`.
3. Add the coverage command to the Validation block.

**Verification:** After edit, T02.05 Acceptance Criteria must reference 100% coverage and include a coverage measurement command.

---

### FIX-15 — Add integration-test note to T04.10 (executor.py modification scope) [PRIORITY 15]

| Field | Value |
|---|---|
| Phase File | `phase-4-tasklist.md` |
| Task | T04.10 |
| Issue Severity | MINOR |
| Issue | T04.10 modifies executor.py (shared pipeline infrastructure) but is classified STANDARD (direct test execution only, no sub-agent review). This may under-validate a high blast-radius change. The deliverable registry specifies STANDARD so tier cannot be changed here, but a note is warranted. |
| Roadmap Ref | R-028, architectural constraints |

**What to change in phase-4-tasklist.md, task T04.10:**

1. Find the Notes field (or add one) in T04.10's metadata table.
2. Add: `IMPORTANT: This task modifies executor.py (shared pipeline infrastructure). Direct test execution covers unit correctness, but executor.py changes must also be validated by the Phase 7 E2E integration test (T07.01). Do not mark this task complete until T07.01 confirms no pipeline regressions.`
3. Add an Acceptance Criterion: `executor.py step registration does not break existing steps 1-9 (validated by T07.01 E2E test, not unit tests alone)`.

**Verification:** After edit, T04.10 must reference T07.01 validation dependency.

---

### FIX-16 — Add naming convention note to T07.09 artifact path [PRIORITY 16]

| Field | Value |
|---|---|
| Phase File | `phase-7-tasklist.md` |
| Task | T07.09 |
| Issue Severity | MINOR |
| Issue | T07.09 uses artifact path `D-0043/notes.md` while all other Phase 7 deliverables use `evidence.md`. The Validation field calls the file "Evidence" while naming it "notes.md". Cosmetic but may break pattern-based tooling. |
| Roadmap Ref | R-054, D-0043 |

**What to change in phase-7-tasklist.md, task T07.09:**

Option A (preferred — preserve notes.md, add explanation):
1. Find the Validation block in T07.09.
2. Update the phrasing from `Evidence: linkable artifact produced at D-0043/notes.md` to `Review artifact produced at D-0043/notes.md (notes.md naming is intentional for EXEMPT review-type deliverables; all test-type deliverables use evidence.md)`.

Option B (align naming):
1. Change `D-0043/notes.md` to `D-0043/evidence.md` in both the Artifacts section and Validation block.
2. Update the deliverable registry entry in `tasklist-index.md` accordingly.

**Recommendation:** Option A — preserves semantic distinction between test evidence and review notes.

**Verification:** After edit, T07.09 must not use the word "Evidence" to describe a file named "notes.md" without explanation.

---

## Execution Plan

### Batch A — High-Impact Fixes (execute first, independently)
- FIX-01: phase-5-tasklist.md / T05.05 (CERTIFY_GATE field gap)
- FIX-02: phase-4-tasklist.md / T04.05 (stray FR-018)
- FIX-04: phase-6-tasklist.md / T06.02 (hash acceptance criterion)
- FIX-07: phase-2-tasklist.md / T02.03 (parser AC gap)

### Batch B — Medium-Impact Fixes
- FIX-03: phase-4-tasklist.md / T04.10 (NFR-008 ownership)
- FIX-05: phase-4-tasklist.md / T04.09 (rollback mechanism)
- FIX-06: phase-4-tasklist.md / T04.08 (SKIPPED criterion)
- FIX-08: phase-7-tasklist.md / checkpoint (regression sequencing)
- FIX-09: phase-7-tasklist.md / T07.05 (delegation level)
- FIX-15: phase-4-tasklist.md / T04.10 (executor.py note)

### Batch C — Cosmetic/Calibration Fixes
- FIX-10: phase-1-tasklist.md / T01.02 (confidence rationale)
- FIX-11: phase-1-tasklist.md / T01.02 (risk drivers)
- FIX-12: phase-1-tasklist.md / checkpoint (M0 label)
- FIX-13: phase-2-tasklist.md / T02.03 (risk rating)
- FIX-14: phase-2-tasklist.md / T02.05 (coverage criterion)
- FIX-16: phase-7-tasklist.md / T07.09 (artifact naming note)

---

## Verification Checklist

After all fixes are applied, run these checks to confirm no new issues were introduced:

```bash
# Check FR-018 is gone from phase-4
grep -n "FR-018" .dev/releases/current/v2.22-RoadmapRemediate/phase-4-tasklist.md
# Expected: 0 matches

# Check certification_date is in T05.05
grep -n "certification_date" .dev/releases/current/v2.22-RoadmapRemediate/phase-5-tasklist.md
# Expected: >=3 matches (required_fields, Why, Acceptance Criteria)

# Check hash-based in T06.02
grep -n "hash-based\|not timestamp" .dev/releases/current/v2.22-RoadmapRemediate/phase-6-tasklist.md
# Expected: >=1 match in T06.02 acceptance criteria

# Check merged-validation-report in T02.03 AC
grep -n "merged-validation-report" .dev/releases/current/v2.22-RoadmapRemediate/phase-2-tasklist.md
# Expected: >=2 matches (one in steps/why, one in acceptance criteria)

# Check NFR-008 in T04.10 body (not just checkpoint)
grep -n "NFR-008" .dev/releases/current/v2.22-RoadmapRemediate/phase-4-tasklist.md
# Expected: matches both inside T04.10 task AND in checkpoint section

# Check T07.05 delegation
grep -n "Sub-Agent Delegation" .dev/releases/current/v2.22-RoadmapRemediate/phase-7-tasklist.md
# Expected: T07.01 and T07.05 both show "Required"
```

---

## Files Modified Summary

| File | Fix IDs | Change Count |
|---|---|---|
| `phase-1-tasklist.md` | FIX-10, FIX-11, FIX-12 | 3 edits |
| `phase-2-tasklist.md` | FIX-07, FIX-13, FIX-14 | 3 edits |
| `phase-4-tasklist.md` | FIX-02, FIX-03, FIX-05, FIX-06, FIX-15 | 5 edits |
| `phase-5-tasklist.md` | FIX-01 | 1 edit |
| `phase-6-tasklist.md` | FIX-04 | 1 edit |
| `phase-7-tasklist.md` | FIX-08, FIX-09, FIX-16 | 3 edits |
