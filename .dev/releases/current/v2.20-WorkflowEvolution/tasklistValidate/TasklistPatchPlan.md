Patch plan for updating the phase tasklists

  Patch set 1 — Highest-value corrections

  These directly close the meaningful roadmap drift.

  A. Patch phase-5-tasklist.md

  Target: T05.09 and end-of-phase checkpoint
  Changes:
  - Expand T05.09 from “define monitoring metrics + rollback plan” to:
    - define metrics
    - document rollback plan
    - execute or simulate rollback procedure
    - capture rollback evidence
  - Add acceptance criteria:
    - rollback steps executed in drill/simulation
    - observed result documented
    - rollback evidence path recorded
  - Update phase-end checkpoint to say:
    - rollback plan documented and tested

  B. Patch phase-6-tasklist.md

  Target: T06.04 and checkpoint wording
  Changes:
  - Replace final full-suite validation command with uv run pytest
  - Reword T06.03 to say success-criteria evidence is aggregated from all prior phase artifacts, not just
   “from Phase 5”
  - Strengthen phase-end checkpoint with explicit:
    - all 14 success criteria passing
    - no regressions across entire suite

  C. Patch phase-2-tasklist.md

  Target: T02.01 or add early checkpoint/baseline step
  Changes:
  - Add explicit pre-change regression baseline command/evidence
  - Update end-of-phase checkpoint to include roadmap Phase 1 exit criteria verbatim or near-verbatim:
    - all existing tests pass
    - dangling refs rejected
    - 100% branch coverage on semantic checks
    - deviation doc exists
    - OQ-002 and OQ-003 documented
    - no new executor/process framework introduced

  D. Patch phase-1-tasklist.md

  Target: phase intro + T01.09
  Changes:
  - Preferred: remove “stakeholder sign-off” from intro if approval is not actually modeled
  - Clarify T01.09 wording:
    - replace “Phase 2 exit criteria” with “next output phase exit criteria” or similar
  - Normalize OQ-006 references to consistently include FR-051.4

  ---
  Patch set 2 — Fidelity/traceability tightening

  E. Patch phase-3-tasklist.md

  Changes:
  - Update fallback wording so it does not imply a true external fallback for the Claude API dependency
  - Normalize T03.03 validation/test selector wording
  - Clarify regression wording to avoid renumbering ambiguity

  F. Patch phase-4-tasklist.md

  Changes:
  - Clarify checkpoint regression scope:
    - “all prior output phases still pass”
  - Explicitly name SC-005 / fabricated traceability E2E validation in acceptance/validation text
  - Replace T04.04 rollback TBD with concrete rollback statement
  - Expand T04.05 deliverable summary to mention layering guard verification

  ---
  Patch set 3 — Small consistency cleanup

  G. Phase-wide wording normalization

  Apply across all six phase files:
  - Use “output Phase X” when referring to renumbered tasklist phases
  - Prefer “prior phases” if phase number is not necessary
  - Keep roadmap-vs-output naming explicit where cross-reference could be ambiguous

  H. Metadata cleanup

  - Fix checkpoint filename inconsistency in Phase 2
  - Align short deliverable summaries with actual acceptance criteria
  - Normalize FR/SC references where slightly drifted

  ---
  Suggested edit order

  1. phase-5-tasklist.md
  2. phase-6-tasklist.md
  3. phase-2-tasklist.md
  4. phase-1-tasklist.md
  5. phase-4-tasklist.md
  6. phase-3-tasklist.md
  7. quick consistency sweep across all phase files