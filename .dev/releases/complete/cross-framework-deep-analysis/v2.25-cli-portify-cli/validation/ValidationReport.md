# Validation Report
Generated: 2026-03-15
Roadmap: .dev/releases/backlog/portify-cli-portify/roadmap.md
Phases validated: 11
Agents spawned: 4 (batched coverage of all 11 phases)
Total findings: 22 (High: 11, Medium: 10, Low: 1)

## Findings

### High Severity

#### H1. T02.02 — DERIVATION_FAILED error code not wired to name derivation logic
- **Severity**: High
- **Affects**: phase-2-tasklist.md / T02.02
- **Problem**: `DERIVATION_FAILED` is defined in T02.07 as one of 5 error codes but T02.02 (CLI name derivation) never references raising it on derivation failure.
- **Roadmap evidence**: Line 89 "Implement CLI name derivation" + line 102 error code `DERIVATION_FAILED` defined
- **Tasklist evidence**: T02.02 acceptance criteria describe derivation behavior but never mention raising DERIVATION_FAILED
- **Exact fix**: Add to T02.02 acceptance criteria: "DERIVATION_FAILED error raised when automatic name derivation produces an empty or invalid result (no --name override and derivation yields no usable name)." Add step: "Handle derivation failure: if stripping prefix/suffix yields empty string, raise DERIVATION_FAILED."

#### H2. T03.11 — OutputMonitor missing 3 fields from roadmap specification
- **Severity**: High
- **Affects**: phase-3-tasklist.md / T03.11
- **Problem**: OutputMonitor field list omits convergence_iteration, findings_count, and placeholder_count which are explicitly required by roadmap NFR-009.
- **Roadmap evidence**: Line 147: "output bytes, growth rate, stall seconds, events, line count, convergence iteration, findings count, placeholder count (NFR-009)"
- **Tasklist evidence**: T03.11 acceptance criteria: "tracks output_bytes, growth_rate_bps, stall_seconds, events, line_count" — missing 3 fields
- **Exact fix**: Add convergence_iteration, findings_count, placeholder_count to T03.11 field list in steps and acceptance criteria.

#### H3. Phase 3 End Checkpoint — Incorrect dependency phase reference
- **Severity**: High
- **Affects**: phase-3-tasklist.md / End of Phase 3 checkpoint
- **Problem**: Says "Phase 5 dependency met" but roadmap says "Phase 4 requires Phase 2 observability baseline complete." Since tasklist Phase 5 = roadmap Phase 4, the text should clarify.
- **Roadmap evidence**: Line 165: "Phase 4 requires Phase 2 observability baseline complete"
- **Tasklist evidence**: End checkpoint: "Phase 5 dependency met: observability baseline ready"
- **Exact fix**: Change to "Observability baseline dependency met for Claude-assisted phases (roadmap Phase 4 / tasklist Phase 5)"

#### H4. T04.01 — Missing PASS_NO_SIGNAL vs PASS_NO_REPORT retry distinction
- **Severity**: High
- **Affects**: phase-4-tasklist.md / T04.01
- **Problem**: Roadmap Phase 3 explicitly requires gate retry logic to distinguish PASS_NO_SIGNAL (triggers retry) from PASS_NO_REPORT (no retry). No Phase 4 task addresses this.
- **Roadmap evidence**: Line 189: "Ensure gate retry logic distinguishes these two statuses"
- **Tasklist evidence**: T04.01-T04.03 have no mention of PASS_NO_SIGNAL vs PASS_NO_REPORT distinction
- **Exact fix**: Add acceptance criterion to T04.01: "Gate retry logic correctly distinguishes PASS_NO_SIGNAL (triggers retry) from PASS_NO_REPORT (treated as passing) per roadmap retry semantics note." Add verification step testing this distinction.

#### H5. Phase 5 End Checkpoint — SC-007 claimed validated but no task tests step-skipping
- **Severity**: High
- **Affects**: phase-5-tasklist.md / End of Phase 5 checkpoint
- **Problem**: SC-007 (resume skips completed steps) is claimed validated but no task in Phase 5 includes an integration test for step-skipping behavior.
- **Roadmap evidence**: Line 674: "SC-007: Resume skips completed steps | Integration test: mark steps complete, resume, verify skip"
- **Tasklist evidence**: Phase 5 checkpoint claims SC-007 validated but no task tests it
- **Exact fix**: Add verification step to T05.06: "Write integration test: mark analysis steps as completed, resume pipeline, verify completed steps are skipped (SC-007)."

#### H6. T07.02 — Incorrect severity routing language for Phase 6 brainstorm
- **Severity**: High
- **Affects**: phase-7-tasklist.md / T07.02
- **Problem**: Uses Phase 7 panel review severity routing (CRITICAL/MAJOR/MINOR) but roadmap Phase 6 brainstorm uses "actionable vs unresolvable" language.
- **Roadmap evidence**: Line 325: "incorporate actionable findings into body; route unresolvable findings to Section 11 (FR-027)"
- **Tasklist evidence**: T07.02 step 5: "incorporate CRITICAL/MAJOR findings into body sections; route unresolvable findings to Section 11"
- **Exact fix**: Change to: "incorporate actionable findings into body; route unresolvable findings to Section 11 (FR-027)" — removing CRITICAL/MAJOR classification which belongs to Phase 8 panel review.

#### H7. Phase 7 — Missing explicit BrainstormFinding model deliverable
- **Severity**: High
- **Affects**: phase-7-tasklist.md / T07.02
- **Problem**: Roadmap lists "Brainstorm finding model" as a distinct deliverable but no task explicitly delivers a BrainstormFinding dataclass.
- **Roadmap evidence**: Line 337: "Brainstorm finding model" as deliverable
- **Tasklist evidence**: T07.02 mentions finding structure but does not deliver a formal model class
- **Exact fix**: Add to T07.02 deliverables: "BrainstormFinding model class (dataclass) with fields: gap_id, description, severity, affected_section, persona." Add acceptance criterion: "BrainstormFinding dataclass defined in models.py with all 5 required fields."

#### H8. T08.05 — No reference to G-011 gate validation for panel review output
- **Severity**: High
- **Affects**: phase-8-tasklist.md / T08.05
- **Problem**: Panel review output must satisfy G-011 (has_quality_scores + has_criticals_addressed) but no Phase 8 task references this gate.
- **Roadmap evidence**: Line 206: "G-011: has_quality_scores; has_criticals_addressed"
- **Tasklist evidence**: No task in Phase 8 references G-011
- **Exact fix**: Add to T08.05 acceptance criteria: "Panel report output satisfies G-011: has_quality_scores (clarity, completeness, testability, consistency, overall) and has_criticals_addressed (all CRITICAL findings marked [INCORPORATED] or [DISMISSED])."

#### H9. T10.01 — SC-013 exit code mapping has no implementation task
- **Severity**: High
- **Affects**: phase-10-tasklist.md / T10.01
- **Problem**: SC-013 (exit codes correct) is assigned to roadmap Phase 9 but no Phase 10 task implements exit code mapping from PortifyOutcome to CLI exit codes.
- **Roadmap evidence**: Line 680: "SC-013: Exit codes correct | Unit test: map outcomes to exit codes"
- **Tasklist evidence**: No task in Phase 10 implements exit code mapping
- **Exact fix**: Add acceptance criterion to T10.01: "CLI run subcommand returns correct exit codes mapped from PortifyOutcome values: 0 for success, non-zero for failure/halted/interrupted (SC-013)."

#### H10. T11.01 — Acceptance criteria omit TurnLedger and exit code mapping tests
- **Severity**: High
- **Affects**: phase-11-tasklist.md / T11.01
- **Problem**: Acceptance criteria mention _determine_status() and timeout but omit TurnLedger budget tracking/exhaustion and exit code mapping.
- **Roadmap evidence**: Line 474: "TurnLedger budget tracking and exhaustion, exit code mapping"
- **Tasklist evidence**: T11.01 acceptance criteria omit these two categories
- **Exact fix**: Add acceptance criteria: "TurnLedger budget tracking and exhaustion tested: can_launch() false at exhaustion, HALTED outcome" and "Exit code mapping tested: each PortifyOutcome maps to correct CLI exit code."

#### H11. T11.02 — Missing gate retry acceptance criterion
- **Severity**: High
- **Affects**: phase-11-tasklist.md / T11.02
- **Problem**: Gate retry (missing EXIT_RECOMMENDATION → retry triggers) is in steps but not in acceptance criteria.
- **Roadmap evidence**: Line 475: "gate failure + retry (missing EXIT_RECOMMENDATION → retry triggers)"
- **Tasklist evidence**: T11.02 acceptance criteria list only 3 bullets, omitting gate retry
- **Exact fix**: Add acceptance criterion: "Gate retry integration test verifies missing EXIT_RECOMMENDATION triggers retry mechanism (PASS_NO_SIGNAL → retry)."

### Medium Severity

#### M1. T01.04 — Missing implementation checklist production step
- **Severity**: Medium
- **Affects**: phase-1-tasklist.md / T01.04
- **Problem**: Roadmap Phase 0 deliverable "Updated implementation checklist" has no corresponding production step in T01.04.
- **Roadmap evidence**: Line 64: "Updated implementation checklist"
- **Tasklist evidence**: T01.04 steps focus on assembling outputs but never produce/update an implementation checklist
- **Exact fix**: Add step: "[EXECUTION] Update implementation checklist reflecting Phase 0 decisions, resolved OQs, and confirmed architecture."

#### M2. T03.10 — Missing static turn count prohibition
- **Severity**: Medium
- **Affects**: phase-3-tasklist.md / T03.10
- **Problem**: Roadmap explicitly states "do not use a static turn count" for suggested_resume_budget but T03.10 omits this constraint.
- **Roadmap evidence**: Line 143: "do not use a static turn count"
- **Tasklist evidence**: T03.10 acceptance criteria omit this prohibition
- **Exact fix**: Add: "suggested_resume_budget is dynamically calculated — must not use a static/hardcoded turn count."

#### M3. Phase 3 / T03.12 — TUI dependency reference says "before Phase 5"
- **Severity**: Medium
- **Affects**: phase-3-tasklist.md / T03.12
- **Problem**: Should reference roadmap's "Required Before Phase 4" dependency.
- **Roadmap evidence**: Line 145: "Observability Baseline (Required Before Phase 4)"
- **Tasklist evidence**: T03.12: "before Phase 5"
- **Exact fix**: Change to: "Required before Claude-assisted phases (roadmap Phase 4 / tasklist Phase 5)."

#### M4. Phase 4 End Checkpoint — Incorrect super-milestone reference
- **Severity**: Medium
- **Affects**: phase-4-tasklist.md / End of Phase 4 checkpoint
- **Problem**: States "Super-milestone A complete: Phases 1-4" but roadmap defines Milestone A as Phases 0-3. Phase 4 (gate system = roadmap Phase 3) IS the last phase of Milestone A, so the claim is correct but confusing.
- **Roadmap evidence**: Line 28: "Milestone A -- Foundations: Phases 0-3" and line 223
- **Tasklist evidence**: Checkpoint: "Super-milestone A (Foundations) complete: Phases 1-4 done"
- **Exact fix**: Clarify: "Super-milestone A (Foundations) complete: roadmap Phases 0-3 / tasklist Phases 1-4."

#### M5. Phase 6 End Checkpoint — Milestone B phase numbering unclear
- **Severity**: Medium
- **Affects**: phase-6-tasklist.md / End of Phase 6 checkpoint
- **Problem**: References "Phases 5-7" for Super-milestone B but roadmap says "Phases 4-6."
- **Roadmap evidence**: Line 350: "Super-milestone B -- Pipeline Generation complete: Phases 4-6"
- **Tasklist evidence**: Checkpoint: "Phases 5-7 artifacts ready for synthesis"
- **Exact fix**: Clarify: "Super-milestone B (Pipeline Generation): roadmap Phases 4-6 / tasklist Phases 5-7."

#### M6. T09.01 — Description references "Phase 3 baseline" ambiguously
- **Severity**: Medium
- **Affects**: phase-9-tasklist.md / T09.01
- **Problem**: Says "from Phase 3" but tasklist Phase 3 IS correct (covers roadmap Phase 2 where TUI baseline lives). The confusion is between roadmap and tasklist numbering.
- **Tasklist evidence**: T09.01: "beyond the basic start/stop lifecycle from Phase 3"
- **Exact fix**: Add clarification: "from tasklist Phase 3 (roadmap Phase 2)" to reduce ambiguity.

#### M7. T09.02 — Same Phase 3 reference issue as T09.01
- **Severity**: Medium
- **Affects**: phase-9-tasklist.md / T09.02
- **Exact fix**: Same as M6: add "(roadmap Phase 2)" clarification.

#### M8. T10.01 — Missing workflow path positional argument
- **Severity**: Medium
- **Affects**: phase-10-tasklist.md / T10.01
- **Problem**: The run subcommand needs a required positional argument for the workflow path but neither T10.01 nor T10.02 mention it.
- **Roadmap evidence**: Phase 1 (line 88) establishes workflow path as primary input
- **Tasklist evidence**: T10.01 and T10.02 only describe the subcommand and option flags
- **Exact fix**: Add to T10.01 acceptance criteria: "run subcommand accepts a required positional argument for the workflow path (skill directory to portify)."

#### M9. T11.03 — Acceptance criteria omit 2 of 5 edge cases
- **Severity**: Medium
- **Affects**: phase-11-tasklist.md / T11.03
- **Problem**: ESCALATED path and >50KB template edge cases are in steps but not acceptance criteria.
- **Roadmap evidence**: Line 476: all 5 edge cases listed
- **Tasklist evidence**: T11.03 acceptance criteria list only 3 of 5
- **Exact fix**: Add: "Convergence ESCALATED test verifies status: partial with panel-report.md and downstream_ready=false" and "Template >50KB test verifies --file argument passed to Claude subprocess."

#### M10. T11.06 — Acceptance criteria omit 2 of 5 sample run scenarios
- **Severity**: Medium
- **Affects**: phase-11-tasklist.md / T11.06
- **Problem**: Interrupted and escalation scenarios are in steps but not acceptance criteria.
- **Roadmap evidence**: Line 479: all 5 scenarios listed
- **Tasklist evidence**: T11.06 acceptance criteria list only 3 of 5
- **Exact fix**: Add: "Interrupted execution produces INTERRUPTED outcome with return-contract.yaml" and "Escalation case produces ESCALATED status with panel-report.md and downstream_ready=false."

### Low Severity

#### L1. T11.07 — Milestone C phase numbering reference
- **Severity**: Low
- **Affects**: phase-11-tasklist.md / T11.07 checkpoint
- **Problem**: Says "Phases 8-11" but roadmap Milestone C is "Phases 7-10."
- **Exact fix**: Clarify: "Roadmap Phases 7-10 / tasklist Phases 8-11."

## Verification Results
Verified: 2026-03-15
Findings resolved: 22/22

| Finding | Status | Notes |
|---------|--------|-------|
| H1 | RESOLVED | DERIVATION_FAILED added to T02.02 steps and acceptance criteria |
| H2 | RESOLVED | convergence_iteration, findings_count, placeholder_count added to T03.11 |
| H3 | RESOLVED | Phase 3 checkpoint clarified with roadmap/tasklist numbering |
| H4 | RESOLVED | PASS_NO_SIGNAL vs PASS_NO_REPORT distinction added to T04.01 |
| H5 | RESOLVED | SC-007 step-skipping test added to T05.06 verification |
| H6 | RESOLVED | T07.02 severity routing changed to "actionable vs unresolvable" |
| H7 | RESOLVED | BrainstormFinding dataclass added to T07.02 deliverables and AC |
| H8 | RESOLVED | G-011 gate validation added to T08.05 acceptance criteria |
| H9 | RESOLVED | SC-013 exit code mapping added to T10.01 acceptance criteria |
| H10 | RESOLVED | TurnLedger and exit code mapping tests added to T11.01 AC |
| H11 | RESOLVED | Gate retry acceptance criterion added to T11.02 |
| M1 | RESOLVED | Implementation checklist step added to T01.04 |
| M2 | RESOLVED | Static turn count prohibition added to T03.10 |
| M3 | RESOLVED | T03.12 dependency reference clarified |
| M4 | RESOLVED | Phase 4 checkpoint milestone reference clarified |
| M5 | RESOLVED | Phase 6 checkpoint milestone B reference clarified |
| M6 | RESOLVED | T09.01 Phase 3 reference clarified with roadmap Phase 2 |
| M7 | RESOLVED | T09.02 Phase 3 reference clarified with roadmap Phase 2 |
| M8 | RESOLVED | Workflow path positional argument added to T10.01 |
| M9 | RESOLVED | ESCALATED and >50KB edge cases added to T11.03 AC |
| M10 | RESOLVED | Interrupted and escalation scenarios added to T11.06 AC |
| L1 | RESOLVED | Milestone C phase numbering clarified in T11.07 |
