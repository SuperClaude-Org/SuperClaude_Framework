# Patch Checklist
Generated: 2026-03-14
Scope: Phase 8 and Phase 9 only (full regeneration approach — files rewritten from scratch)
Total edits: 10 patches across 2 files

## Execution approach

Both `phase-8-tasklist.md` and `phase-9-tasklist.md` were **regenerated from scratch** (full file rewrite) rather than applying incremental edits. This eliminates the risk of partial-patch drift. All 10 patches are embedded directly into the regenerated files.

## File-by-file edit checklist

- `phase-8-tasklist.md`
  - [x] M11: Replace "AC-010 schema" with "schema expectations from the /sc:roadmap command definition" in T08.01 steps and AC (from finding M11)
  - [x] M12: Add AC criterion to T08.01: "D-0030 findings are referenced in validation-report.md (D-0033) per Gate Criteria requirement" (from finding M12)
  - [x] L12: Expand T08.02 AC gate scope to explicitly state "formal architecture review, not a formatting pass or compliance scan" (from finding L12)
  - [x] H10: Change T08.03 Dimension 4 step from "Phase 2 components" to "Phase 1 components" in step text and AC (from finding H10)
  - [x] H11: Add four Disqualifying Conditions to T08.03 step 9 and AC: (1) evidence unverifiable, (2) copied mass in adoption, (3) broken cross-artifact lineage, (4) implementation-scope drift — any triggered = Fail-Rework (from finding H11)
  - [x] M13: Change T08.04 AC from "list of reworked items with corrections" to "failed items listed with Fail classification and Disqualifying Condition reference for T08.05 consumption" (from finding M13)
  - [x] H12: Add T08.05 step 5 for Auggie MCP file path verification; add AC criterion: "All file paths in final-improve-plan.md are verified via Auggie MCP (Gate Criteria SC-007)" (from finding H12)
  - [x] M14: Add T08.05 AC criterion: "final-improve-plan.md is confirmed schema-compliant with /sc:roadmap expectations established in D-0030, satisfying Gate Criteria pre-validation requirement" (from finding M14)

- `phase-9-tasklist.md`
  - [x] H13: Replace T09.02 failure branch AC with unconditional block: sprint completion blocked; test MUST be re-executed and pass before T09.03/T09.04 proceed; remove language allowing sprint completion with documented failure (from finding H13)
  - [x] L13: Add T09.04 step 2 preference statement: "the script is the strongly preferred path (low effort relative to manual review of 35+ artifacts per roadmap); only fall back to manual protocol if script cannot be produced and document explicitly why" (from finding L13)

## Cross-file consistency sweep
- [x] Phase 8 end-of-phase checkpoint updated to reflect all four Disqualifying Conditions, Auggie MCP file path verification, and schema compliance confirmation
- [x] Phase 9 end-of-phase checkpoint updated to reflect unconditional resume test gate and script-preferred OQ-005 resolution
- [x] tasklist-index.md Generation Notes updated with Patch Regeneration section documenting all 10 applied patches

## Findings deferred (Phases 1-7, not in scope for this regeneration)

The following findings from the original ValidationReport affect phases 1-7 and are explicitly out of scope for this patch cycle. They remain open and require a separate phase-1-7 patch pass:

| Finding | Phase | Task | Status |
|---------|-------|------|--------|
| H1 | Phase 1 | T01.07 | Open — deferred |
| H2 | Phase 1 | T01.04 | Open — deferred |
| H3 | Phase 1 | T01.03 | Open — deferred |
| H4 | Phase 2 | T02.04 | Open — deferred |
| H5 | Phase 3 | T03.01 | Open — deferred |
| H6 | Phase 3 | T03.02 | Open — deferred |
| H7 | Phase 5 | T05.03 | Open — deferred |
| H8 | Phase 6 | T06.01 | Open — deferred |
| H9 | Phase 7 | T07.01 | Open — deferred |
| M1 | Phase 1 | T01.01 | Open — deferred |
| M2 | Phase 1 | T01.03 | Open — deferred |
| M3 | Phase 1 | T01.05 | Open — deferred |
| M4 | Phase 1 | T01.06 | Open — deferred |
| M5 | Phase 2 | T02.02 | Open — deferred |
| M6 | Phase 3 | T03.01 | Open — deferred |
| M7 | Phase 4 | T04.02 | Open — deferred |
| M8 | Phase 4 | T04.03 | Open — deferred |
| M9 | Phase 6 | T06.02 | Open — deferred |
| M10 | Phase 6 | T06.03 | Open — deferred |
| L1 | Phase 1 | T01.02 | Open — deferred |
| L2 | Phase 1 | T01.01 | Open — deferred |
| L3 | Phase 1 | T01.06 | Open — deferred |
| L4 | Phase 2 | T02.01 | Open — deferred |
| L5 | Phase 3 | T03.01 | Open — deferred |
| L6 | Phase 3 | T03.03 | Open — deferred |
| L7 | Phase 5 | T05.01 | Open — deferred |
| L8 | Phase 5 | T05.04 | Open — deferred |
| L9 | Phase 6 | T06.02 | Open — deferred |
| L10 | Phase 7 | T07.02 | Open — deferred |
| L11 | Phase 7 | T07.03 | Open — deferred |
