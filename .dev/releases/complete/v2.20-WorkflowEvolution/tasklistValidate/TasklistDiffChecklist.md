  File-by-file edit checklist                                                                            
                                                                                                         
  - phase-1-tasklist.md                                                                                  
    - Remove or reframe unimplemented stakeholder sign-off language in phase intro                       
    - Normalize OQ-006 schema references to include FR-051.4
    - Clarify renumbered phase wording in T01.09
  - phase-2-tasklist.md
    - Add explicit pre-change regression baseline
    - Strengthen T02.01 named-test traceability
    - Fix checkpoint filename mismatch
    - Expand end-of-phase checkpoint to match roadmap exit criteria
  - phase-3-tasklist.md
    - Fix fallback wording to match roadmap dependency model
    - Normalize T03.03 verification/test selector wording
    - Clarify regression wording after renumbering
  - phase-4-tasklist.md
    - Clarify checkpoint regression scope
    - Explicitly anchor SC-005 E2E validation in T04.05
    - Replace T04.04 rollback TBD
    - Expand T04.05 deliverable summary to mention layering guard
  - phase-5-tasklist.md
    - Add rollback-plan testing/drill to T05.09
    - Add rollback test evidence expectations
    - Update phase-end checkpoint to require “documented and tested”
    - Optional: rename T05.14 for renumbering clarity
  - phase-6-tasklist.md
    - Replace final full-suite command with uv run pytest
    - Reword T06.03 evidence aggregation to cover all prior phases
    - Strengthen phase-end checkpoint to explicitly require all 14 SCs + no regressions
  - Cross-file consistency sweep
    - Standardize “output Phase X” wording where needed
    - Align checkpoint wording with roadmap exit criteria
    - Align deliverable summaries with actual acceptance criteria

  ---
  Precise diff plan

  1) phase-1-tasklist.md

  Section/heading to change

  - Phase intro / opening summary
  - T01.03 — OQ-006 deviation schema task
  - T01.09 — consolidated decision log task

  Planned edits

  A. Phase intro

  Current issue: Intro claims each decision includes stakeholder sign-off, but tasks do not model
  sign-off.

  Change:
  - Replace sign-off claim with documentation-focused wording.

  Diff intent:
  - Change from something like:
    - “each decision must include rationale, impact, and stakeholder sign-off”
  - To:
    - “each decision must include rationale, impact, and explicit downstream implications”
    - or
    - “each decision must be documented with rationale and implementation implications before
  implementation begins”

  Reason: Aligns intro with actual task structure unless you want to add real sign-off workflow.

  ---
  B. T01.03

  Current issue: OQ-006 references drift between FR-051.4, FR-021, and FR-026.

  Change:
  - In completion/acceptance/traceability wording, explicitly preserve FR-051.4 as primary schema anchor.
  - Keep FR-026 if used for deviation reference finalization.

  Diff intent:
  - Ensure wording says:
    - “7-column schema aligned to FR-051.4, with finalization consistency against FR-026”
  - Avoid wording that implies only FR-021/FR-026 and drops FR-051.4.

  ---
  C. T01.09

  Current issue: “Cross-reference decision log with Phase 2 exit criteria” is ambiguous after
  renumbering.

  Change:
  - Replace “Phase 2 exit criteria” with:
    - “next output phase exit criteria”
    - or
    - “output Phase 2 / roadmap Phase 1 implementation entry criteria”

  Preferred wording:
  - “Cross-reference decision log with the next output phase’s implementation entry/exit criteria.”

  ---
  2) phase-2-tasklist.md

  Section/heading to change

  - T02.01 — REFLECT_GATE tier promotion
  - Mid-phase checkpoint block
  - End of Phase 2 checkpoint / phase-end summary

  Planned edits

  A. T02.01

  Current issue: No explicit pre-change regression baseline; named-test traceability is too generic.

  Change 1: add baseline step
  Insert a first execution step such as:
  - “Run pre-change regression baseline against existing roadmap tests and record results before
  modifying gate enforcement.”

  Validation text to add:
  - uv run pytest tests/roadmap/ -v or the exact suite intended as baseline
  - evidence path for baseline report

  Change 2: strengthen named test traceability
  Add roadmap-named tests explicitly:
  - test_reflect_gate_is_strict
  - test_reflect_gate_semantic_checks_execute

  Diff intent in acceptance criteria:
  - “Named roadmap tests for REFLECT strictness and semantic execution pass.”

  ---
  B. Mid-phase checkpoint block

  Current issue: checkpoint filename mismatch.

  Change:
  - Rename checkpoint artifact reference from:
    - CP-P02-T01-T05.md
  - To a T02-aligned name, e.g.:
    - CP-P02-T02-01-T02-05.md
    - or whatever local convention matches the surrounding files

  Goal: Make scope and filename align.

  ---
  C. End of Phase 2 checkpoint

  Current issue: Summary is weaker than roadmap exit criteria.

  Change:
  Expand end-of-phase checkpoint bullets to explicitly include:
  - all existing tests pass
  - _cross_refs_resolve() rejects dangling references
  - semantic checks have 100% branch coverage
  - deviation format reference doc exists
  - OQ-002 and OQ-003 are documented
  - no new executor/process framework introduced

  Diff intent:
  Convert checkpoint from a short completion summary into a roadmap-exit-criteria mirror.

  ---
  3) phase-3-tasklist.md

  Section/heading to change

  - Task metadata blocks for T03.01–T03.06
  - T03.03 — pipeline step integration
  - T03.06 — phase test / checkpoint wording

  Planned edits

  A. Task metadata blocks

  Current issue: blanket Fallback Allowed | Yes conflicts with roadmap statement that Claude API
  dependency has no fallback.

  Change:
  Replace blanket fallback wording with something like:
  - “External dependency fallback: No”
  - “Operational degraded reporting: Yes, after attempted execution”
  - or
  - “No alternate dependency fallback; degraded pipeline behavior applies after failure”

  Goal: distinguish dependency fallback from degraded report behavior.

  ---
  B. T03.03

  Current issue: inconsistent validation selectors.

  Change:
  Normalize Steps / Acceptance Criteria / Validation so they all reference the same targeted test scope.

  Diff intent:
  - Pick one wording and use it everywhere, e.g.:
    - “Run targeted pipeline/spec-fidelity integration tests”
    - with one exact selector/command
  - Ensure it directly supports roadmap tests:
    - test_spec_fidelity_blocks_on_high_deviation
    - test_spec_fidelity_passes_clean_roadmap
    - test_pipeline_includes_spec_fidelity_step

  ---
  C. T03.06

  Current issue: regression wording is slightly ambiguous after renumbering.

  Change:
  Replace “All Phase 1-2 tests still pass” with one of:
  - “All prior output phases still pass”
  - “All prior implementation-phase tests still pass”
  - “Output Phases 1–2 remain green”

  ---
  4) phase-4-tasklist.md

  Section/heading to change

  - T04.04 — performance measurement
  - T04.05 — phase tests / exit verification
  - Phase-end checkpoint

  Planned edits

  A. T04.04

  Current issue: rollback is TBD.

  Change:
  Replace TBD with a concrete rollback statement.

  Preferred rollback wording:
  - “Rollback: remove benchmark-only notes/artifacts and revert measurement-specific tasklist changes if
  thresholds or framing prove incorrect.”
  - Or, if no artifact rollback is needed:
    - “Rollback: no code-path change; remove/replace invalid measurement evidence only.”

  ---
  B. T04.05

  Current issue 1: SC-005 is not explicit enough in acceptance/validation.
  Change:
  Add explicit acceptance/validation mention of:
  - fabricated traceability E2E validation against v2.19 artifacts
  - validation layering guard test

  Diff intent:
  Acceptance criteria should mention all of:
  - SC-005
  - SC-009
  - SC-013
  - validation layering guard

  Current issue 2: deliverable summary under-describes layering guard.
  Change:
  Update deliverable summary to mention:
  - “phase test results including SC criteria, fabricated traceability detection, and layering-guard
  verification”

  ---
  C. Phase-end checkpoint

  Current issue: regression scope wording ambiguous.

  Change:
  Replace wording like:
  - “All Phase 1-3 tests still pass”
  With:
  - “All prior output phases (Phases 1–3) still pass”
  or
  - “All prior roadmap-equivalent phase validations remain passing”

  ---
  5) phase-5-tasklist.md

  Section/heading to change

  - T05.09 — monitoring metrics / rollback plan
  - T05.14 — phase validation task
  - Phase-end checkpoint

  Planned edits

  A. T05.09

  Current issue: roadmap requires rollback plan to be documented and tested, but task only documents it.

  Change:
  Expand T05.09 into two-part output within the same task:
  1. monitoring metrics definition
  2. rollback drill/simulation and evidence capture

  Add execution steps:
  - define rollback trigger thresholds
  - execute rollback drill or dry-run simulation
  - record expected vs observed results
  - store rollback evidence artifact

  Acceptance criteria to add:
  - rollback procedure exercised in drill/simulation
  - result documented
  - evidence path recorded
  - failure conditions and recovery expectations captured

  Deliverable summary update:
  - from “Monitoring metrics definition document” / “Rollback plan document”
  - to “Monitoring metrics definition + rollback drill evidence” or split if task structure allows

  ---
  B. T05.14

  Optional clarity edit
  Current issue: title may be ambiguous because output Phase 5 corresponds to roadmap Phase 4.

  Change:
  Rename from something like:
  - “Execute Phase 5 Test Suite”
  To:
  - “Execute Output Phase 5 Validation Suite”
  or
  - “Execute roadmap-Phase-4 hardening validation suite”

  Optional, but improves operator clarity.

  ---
  C. Phase-end checkpoint

  Current issue: roadmap wording says rollback plan must be documented and tested.

  Change:
  Explicitly add a checkpoint bullet:
  - “Rollback plan documented and tested”
  Also preserve:
  - SC-006, SC-010, SC-012 verified
  - historical replay completed
  - monitoring metrics defined
  - team can distinguish pass/fail/skipped/degraded

  ---
  6) phase-6-tasklist.md

  Section/heading to change

  - T06.03 — release sign-off checklist
  - T06.04 — final test suite / validation
  - Phase-end checkpoint

  Planned edits

  A. T06.03

  Current issue: wording implies 14 success criteria are compiled only from Phase 5.

  Change:
  Reword evidence aggregation to explicitly span all prior phases.

  Preferred wording:
  - “Compile and cross-reference evidence for all 14 success criteria from prior output-phase artifacts
  and validation outputs.”
  - Avoid: “from Phase 5”

  ---
  B. T06.04

  Current issue: final full-suite command is narrower than roadmap.

  Change:
  Replace any final-suite validation command:
  - from uv run pytest tests/ -v
  - to uv run pytest

  Acceptance criteria update:
  - explicitly state this is the roadmap-defined full suite
  - retain E2E/full-gate validation if already present

  ---
  C. Phase-end checkpoint

  Current issue: checkpoint does not fully mirror roadmap exit criteria.

  Change:
  Explicitly add:
  - all 14 success criteria passing
  - no regressions across entire suite
  - all artifacts archived in .dev/releases/
  - sign-off documented with evidence for each criterion

  Goal: make final checkpoint a near-verbatim mirror of roadmap Phase 5 exit criteria.

  ---
  7) Cross-file consistency sweep

  Sections/headings to change

  - Any task or checkpoint that references another phase by number
  - Any deliverable summary that under-describes acceptance criteria
  - Any metadata block with ambiguous fallback or rollback wording

  Planned edits

  A. Phase-reference normalization

  Use one consistent convention:
  - output Phase X inside tasklists
  - optionally mention roadmap phase only when needed for traceability

  B. Checkpoint wording normalization

  Ensure each end-of-phase checkpoint reads like a compressed mirror of roadmap exit criteria rather than
   a looser completion summary.

  C. Deliverable summary normalization

  Where acceptance criteria mention specific SCs/tests/guards, ensure the short deliverable label does
  not omit the most important ones.

  ---
  Suggested execution order

  1. phase-5-tasklist.md
  2. phase-6-tasklist.md
  3. phase-2-tasklist.md
  4. phase-1-tasklist.md
  5. phase-4-tasklist.md
  6. phase-3-tasklist.md
  7. cross-file consistency sweep

  Validation checklist after patching

  - Phase 1 no longer claims unsupported sign-off workflow
  - Phase 2 has explicit pre-change regression baseline
  - Phase 2 end checkpoint mirrors roadmap exit criteria
  - Phase 3 fallback wording no longer implies unsupported dependency fallback
  - Phase 4 explicitly names SC-005 and layering guard validation
  - Phase 4 rollback text is no longer TBD
  - Phase 5 includes rollback testing evidence
  - Phase 5 end checkpoint says rollback documented and tested
  - Phase 6 final suite uses uv run pytest
  - Phase 6 sign-off aggregates evidence from all prior phases
  - Phase 6 final checkpoint explicitly requires all 14 SCs and no regressions
  - Cross-phase references consistently use output-phase wording