 Deduplicated issue list

  1. Missing rollback-plan testing

  Severity: Medium
  Affects: phase-5-tasklist.md
  Problem: The roadmap requires the rollback plan to be documented and tested, but the tasklist only
  covers documentation.
  Evidence:
  - roadmap.md:284-293 especially roadmap.md:291
  - phase-5-tasklist.md:412-458
  - phase-5-tasklist.md:720-734

  Exact fix:
  - Update T05.09 to explicitly include a rollback drill/simulation/test.
  - Add acceptance criteria and validation steps requiring evidence that the rollback procedure was
  exercised.
  - Update the end-of-phase checkpoint text to say “rollback plan documented and tested”.

  ---
  2. Final full-suite test command drift

  Severity: Medium
  Affects: phase-6-tasklist.md
  Problem: The roadmap requires the full test suite via uv run pytest, but the tasklist narrows this to
  uv run pytest tests/ -v.
  Evidence:
  - roadmap.md:320-324
  - phase-6-tasklist.md:178-191
  - phase-6-tasklist.md:205

  Exact fix:
  - Replace uv run pytest tests/ -v with uv run pytest everywhere this task is framed as the final
  full-suite validation.
  - If the narrower command is intentionally equivalent, add explicit justification; otherwise align
  exactly to roadmap wording.

  ---
  3. Missing explicit pre-change regression baseline

  Severity: Medium
  Affects: phase-2-tasklist.md
  Problem: The roadmap treats the existing suite as a before/after regression baseline, but the tasklist
  only clearly schedules post-change validation.
  Evidence:
  - roadmap.md:376-377
  - phase-2-tasklist.md:3
  - phase-2-tasklist.md:484-500

  Exact fix:
  - Add an explicit pre-change baseline run near the start of Phase 2.
  - Best options:
    - add a first step to T02.01, or
    - add a dedicated task/checkpoint item before implementation tasks begin.
  - Record the baseline artifact/result so the later regression comparison has concrete evidence.

  ---
  4. Introduced sign-off requirement not implemented

  Severity: Medium
  Affects: phase-1-tasklist.md
  Problem: The phase intro says decisions require stakeholder sign-off, but no Phase 1 tasks actually
  capture sign-off and all show Requires Confirmation | No.
  Evidence:
  - phase-1-tasklist.md:3
  - phase-1-tasklist.md:16
  - phase-1-tasklist.md:65
  - phase-1-tasklist.md:418
  - roadmap.md:433-436

  Exact fix:
  Choose one path and apply consistently:
  1. Add sign-off handling to T01.01–T01.09:
    - acceptance criterion for stakeholder approval
    - evidence location for approval/sign-off
    - Requires Confirmation | Yes where appropriate
  or
  2. Remove/soften the sign-off claim in the phase intro so it only promises documented decisions, not
  explicit approval.

  Recommended: if these are planning artifacts only, remove the sign-off claim unless you truly want
  approval workflow embedded.

  ---
  5. End-of-phase checkpoints weaker than roadmap exit criteria

  Severity: Medium
  Affects: phase-2-tasklist.md, phase-4-tasklist.md, phase-6-tasklist.md
  Problem: Several end-of-phase checkpoint sections summarize completion, but do not mirror the roadmap’s
   exit criteria precisely enough.
  Evidence:
  - Phase 2:
    - roadmap.md:109-116
    - phase-2-tasklist.md:507-520
  - Phase 4:
    - roadmap.md:204-210
    - phase-4-tasklist.md:257-259
  - Phase 6:
    - roadmap.md:326-331
    - phase-6-tasklist.md:204-212

  Exact fix:
  - Strengthen checkpoint/phase-end criteria so they explicitly restate roadmap requirements.
  - Specifically:
    - Phase 2: include dangling cross-ref rejection, 100% branch coverage for semantic checks, deviation
  doc existence, no new executor/process framework.
    - Phase 4: clarify regression requirement and preserve SC verification language.
    - Phase 6: explicitly include all 14 success criteria passing and no regressions across the entire
  suite.

  ---
  6. Ambiguous regression-scope wording after renumbering

  Severity: Low
  Affects: phase-3-tasklist.md, phase-4-tasklist.md, phase-6-tasklist.md, some Phase 1 wording
  Problem: Several places use wording like “All Phase 1-2 tests still pass” or “Phase 2 exit criteria”
  without clarifying whether they mean roadmap phases or output phases.
  Evidence:
  - tasklist-index.md:57-58
  - phase-3-tasklist.md:285-289
  - phase-4-tasklist.md:257-259
  - phase-6-tasklist.md:127-133
  - phase-1-tasklist.md:434-440

  Exact fix:
  - Standardize all cross-phase references to one of:
    - “output Phase X”
    - “roadmap Phase X”
    - or “prior phases” if exact numbering is unnecessary
  - Recommended style: use “output Phase” inside tasklists since they are already renumbered outputs.

  ---
  7. Test traceability is sometimes too generic

  Severity: Low
  Affects: phase-2-tasklist.md, phase-3-tasklist.md, phase-4-tasklist.md
  Problem: Some tasks reference generic selectors or broad suite commands instead of the roadmap’s named
  tests / phase-specific verifications.
  Evidence:
  - roadmap.md:103-107 vs phase-2-tasklist.md:38-49
  - roadmap.md:157-159 vs phase-3-tasklist.md:134,138,144
  - roadmap.md:199-202 vs phase-4-tasklist.md:227-244

  Exact fix:
  - Where the roadmap names important tests, preserve them explicitly in acceptance/validation text.
  - In particular:
    - Phase 2: explicitly name REFLECT/cross-ref tests
    - Phase 3: normalize T03.03 selectors
    - Phase 4: explicitly anchor SC-005 E2E fabricated-traceability validation

  ---
  8. Minor metadata / wording / completeness drift

  Severity: Low
  Affects: multiple files
  Problem: Small inconsistencies that do not break roadmap fidelity but weaken clarity.
  Examples:
  - phase-2-tasklist.md:252 checkpoint filename doesn’t match T02 scope
  - phase-4-tasklist.md:197-198 rollback marked TBD
  - phase-4-tasklist.md:224-240 deliverable summary under-describes layering guard verification
  - phase-1-tasklist.md:127-139 OQ-006 references are slightly inconsistent
  - phase-5-tasklist.md:671 title mildly ambiguous due to renumbering

  Exact fix:
  - Clean these up while applying the main fixes:
    - rename inconsistent checkpoint filename
    - replace TBD rollback text with concrete rollback note
    - align deliverable summaries with actual acceptance criteria
    - normalize FR references and phase wording