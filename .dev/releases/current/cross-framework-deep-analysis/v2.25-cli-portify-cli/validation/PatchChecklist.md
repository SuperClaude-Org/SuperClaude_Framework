# Patch Checklist
Generated: 2026-03-15
Total edits: 22 across 9 files

## File-by-file edit checklist

- phase-2-tasklist.md
  - [ ] H1: Add DERIVATION_FAILED error raising to T02.02 acceptance criteria and steps

- phase-3-tasklist.md
  - [ ] H2: Add convergence_iteration, findings_count, placeholder_count to T03.11 OutputMonitor fields
  - [ ] H3: Fix Phase 3 end checkpoint dependency reference ("Phase 5" → clarify roadmap/tasklist numbering)
  - [ ] M2: Add "must not use static turn count" to T03.10 acceptance criteria
  - [ ] M3: Change T03.12 "before Phase 5" to clarify roadmap Phase 4 dependency

- phase-4-tasklist.md
  - [ ] H4: Add PASS_NO_SIGNAL vs PASS_NO_REPORT retry distinction to T04.01 acceptance criteria
  - [ ] M4: Clarify Phase 4 end checkpoint super-milestone A reference with roadmap numbering

- phase-5-tasklist.md
  - [ ] H5: Add SC-007 step-skipping integration test to T05.06 verification step

- phase-7-tasklist.md
  - [ ] H6: Change T07.02 severity routing from "CRITICAL/MAJOR" to "actionable vs unresolvable"
  - [ ] H7: Add BrainstormFinding model deliverable to T07.02

- phase-8-tasklist.md
  - [ ] H8: Add G-011 gate validation to T08.05 acceptance criteria

- phase-9-tasklist.md
  - [ ] M6: Clarify T09.01 "Phase 3" reference with "(roadmap Phase 2)"
  - [ ] M7: Clarify T09.02 "Phase 3" reference with "(roadmap Phase 2)"

- phase-10-tasklist.md
  - [ ] H9: Add SC-013 exit code mapping acceptance criterion to T10.01
  - [ ] M8: Add workflow path positional argument to T10.01 acceptance criteria

- phase-11-tasklist.md
  - [ ] H10: Add TurnLedger and exit code mapping to T11.01 acceptance criteria
  - [ ] H11: Add gate retry acceptance criterion to T11.02
  - [ ] M9: Add ESCALATED and >50KB edge cases to T11.03 acceptance criteria
  - [ ] M10: Add interrupted and escalation scenarios to T11.06 acceptance criteria
  - [ ] L1: Clarify T11.07 milestone C phase numbering

- phase-1-tasklist.md
  - [ ] M1: Add implementation checklist production step to T01.04

## Cross-file consistency sweep
- [ ] All super-milestone references include both roadmap and tasklist phase numbering
- [ ] All phase dependency references clarify roadmap vs tasklist numbering where they differ

---

## Precise diff plan

### 1) phase-2-tasklist.md

#### Section: T02.02 Acceptance Criteria
**A. Add DERIVATION_FAILED error raising (H1)**
Current issue: T02.02 describes name derivation but never mentions raising DERIVATION_FAILED on failure
Change: Add acceptance criterion and step
Diff intent: After "Kebab-case normalization produces lowercase-hyphenated output..." add: "DERIVATION_FAILED error raised when automatic name derivation produces an empty or invalid result (no --name override and derivation yields no usable name)" and add step between steps 4 and 5: "[EXECUTION] Handle derivation failure: if stripping prefix/suffix yields empty string, raise DERIVATION_FAILED with diagnostic message"

### 2) phase-3-tasklist.md

#### Section: T03.11 Acceptance Criteria and Steps
**A. Add 3 missing OutputMonitor fields (H2)**
Current issue: Missing convergence_iteration, findings_count, placeholder_count
Change: Extend field lists in steps 1, 3 and acceptance criteria
Diff intent: Change "output_bytes, growth_rate_bps, stall_seconds, events, line_count" to "output_bytes, growth_rate_bps, stall_seconds, events, line_count, convergence_iteration, findings_count, placeholder_count" in all occurrences

#### Section: End of Phase 3 Checkpoint
**B. Fix dependency reference (H3)**
Current issue: "Phase 5 dependency met: observability baseline ready for Claude-assisted step debugging"
Change: Clarify numbering
Diff intent: Change to "Observability baseline dependency met for Claude-assisted phases (roadmap Phase 4 / tasklist Phase 5)"

#### Section: T03.10 Acceptance Criteria
**C. Add static turn count prohibition (M2)**
Current issue: Missing constraint from roadmap line 143
Change: Add acceptance criterion
Diff intent: After "suggested_resume_budget calculated as remaining * 25..." add: "suggested_resume_budget is dynamically calculated from remaining step count — must not use a static/hardcoded turn count"

#### Section: T03.12 Why field
**D. Clarify Phase dependency (M3)**
Current issue: Says "before Phase 5"
Change: Clarify roadmap dependency
Diff intent: Change "before Phase 5 when long-running steps need progress visibility" to "before Claude-assisted phases begin (roadmap Phase 4 / tasklist Phase 5) when long-running steps need progress visibility"

### 3) phase-4-tasklist.md

#### Section: T04.01 Acceptance Criteria
**A. Add retry distinction (H4)**
Current issue: No mention of PASS_NO_SIGNAL vs PASS_NO_REPORT
Change: Add acceptance criterion
Diff intent: Add after last AC bullet: "Gate retry logic correctly distinguishes PASS_NO_SIGNAL (triggers retry — result file present, no EXIT_RECOMMENDATION) from PASS_NO_REPORT (no retry — treated as passing outcome) per roadmap retry semantics note"

#### Section: End of Phase 4 Checkpoint
**B. Clarify milestone reference (M4)**
Current issue: "Super-milestone A (Foundations) complete: Phases 1-4 done"
Change: Add roadmap numbering
Diff intent: Change to "Super-milestone A (Foundations) complete: roadmap Phases 0-3 / tasklist Phases 1-4 done"

### 4) phase-5-tasklist.md

#### Section: T05.06 Steps
**A. Add SC-007 integration test (H5)**
Current issue: No task tests step-skipping behavior
Change: Add verification step
Diff intent: Change verification step to: "[VERIFICATION] Run full Phase 1 integration test including resume with completed step skipping: mark protocol-mapping and analysis-synthesis as completed, resume pipeline, verify skipped (SC-007)"

### 5) phase-7-tasklist.md

#### Section: T07.02 Steps and Acceptance Criteria
**A. Fix severity routing language (H6)**
Current issue: Uses "CRITICAL/MAJOR findings" instead of "actionable findings"
Change: Align with roadmap Phase 6 language
Diff intent: Change step 5 from "incorporate CRITICAL/MAJOR findings into body sections; route unresolvable findings to Section 11" to "incorporate actionable findings into body; route unresolvable findings to Section 11 (FR-027)". Change corresponding AC bullet similarly.

**B. Add BrainstormFinding model deliverable (H7)**
Current issue: Missing formal model class as deliverable
Change: Add deliverable and acceptance criterion
Diff intent: Add to deliverables: "BrainstormFinding dataclass in models.py with fields: gap_id, description, severity, affected_section, persona". Add AC: "BrainstormFinding dataclass defined in models.py with all 5 required fields per roadmap brainstorm finding model deliverable"

### 6) phase-8-tasklist.md

#### Section: T08.05 Acceptance Criteria
**A. Add G-011 gate validation (H8)**
Current issue: No reference to G-011 checks
Change: Add acceptance criterion
Diff intent: Add: "Panel report output satisfies G-011 gate checks: has_quality_scores (clarity, completeness, testability, consistency, overall) and has_criticals_addressed (all CRITICAL findings marked [INCORPORATED] or [DISMISSED])"

### 7) phase-9-tasklist.md

#### Section: T09.01 and T09.02 descriptions
**A. Clarify Phase references (M6, M7)**
Current issue: "from Phase 3" is technically correct (tasklist numbering) but confusing
Change: Add roadmap reference
Diff intent: Change "from Phase 3" to "from tasklist Phase 3 (roadmap Phase 2)" in both tasks

### 8) phase-10-tasklist.md

#### Section: T10.01 Acceptance Criteria
**A. Add SC-013 exit code mapping (H9)**
Current issue: No exit code mapping implementation
Change: Add acceptance criterion
Diff intent: Add: "CLI run subcommand returns correct exit codes mapped from PortifyOutcome values: 0 for success, non-zero for failure/halted/interrupted (SC-013)"

**B. Add workflow path positional argument (M8)**
Current issue: Missing required positional argument
Change: Add acceptance criterion
Diff intent: Add: "run subcommand accepts a required positional argument for the workflow path (skill directory to portify)"

### 9) phase-11-tasklist.md

#### Section: T11.01 Acceptance Criteria
**A. Add TurnLedger and exit code tests (H10)**
Current issue: Two test categories omitted from AC
Change: Add two acceptance criteria
Diff intent: Add: "TurnLedger budget tracking and exhaustion tested: can_launch() returns false at exhaustion, HALTED outcome set" and "Exit code mapping tested: each PortifyOutcome maps to correct CLI exit code"

#### Section: T11.02 Acceptance Criteria
**B. Add gate retry test (H11)**
Current issue: Gate retry validation omitted from AC
Change: Add acceptance criterion
Diff intent: Add: "Gate retry integration test verifies missing EXIT_RECOMMENDATION triggers retry mechanism (PASS_NO_SIGNAL status → retry)"

#### Section: T11.03 Acceptance Criteria
**C. Add 2 missing edge cases (M9)**
Current issue: ESCALATED and >50KB omitted from AC
Change: Add two acceptance criteria
Diff intent: Add: "Convergence ESCALATED test verifies status: partial with panel-report.md and downstream_ready=false" and "Template >50KB test verifies --file argument passed to Claude subprocess"

#### Section: T11.06 Acceptance Criteria
**D. Add 2 missing scenarios (M10)**
Current issue: Interrupted and escalation omitted from AC
Change: Add two acceptance criteria
Diff intent: Add: "Interrupted execution produces INTERRUPTED outcome with return-contract.yaml emitted" and "Escalation case produces ESCALATED status with panel-report.md and downstream_ready=false"

#### Section: T11.07 End Checkpoint
**E. Clarify milestone C reference (L1)**
Current issue: "Phases 8-11" without roadmap reference
Change: Add roadmap numbering
Diff intent: Change "Phases 8-11 done" to "roadmap Phases 7-10 / tasklist Phases 8-11 done"

### 10) phase-1-tasklist.md

#### Section: T01.04 Steps
**A. Add implementation checklist step (M1)**
Current issue: No step produces/updates the implementation checklist
Change: Add execution step
Diff intent: Add step between existing steps 5 and 6: "[EXECUTION] Update implementation checklist reflecting Phase 0 decisions, resolved OQs, and confirmed architecture assumptions"
