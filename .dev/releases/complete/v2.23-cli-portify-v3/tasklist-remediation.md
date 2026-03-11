Remediation Tasklist                                                                                                                                  
                                                                                                                                                      
  Phase A — Required checkpoint fixes                                                                                                                   
                                                                                                                                                        
  These are the only items flagged as MAJOR.                                                                                                            

  T01 — Fix Gate B completeness in phase-2-tasklist.md                                                                                                  
                                                                                                                                                        
  Target: .dev/releases/current/v2.23-cli-portify-v3/phase-2-tasklist.md                                                                                
  Goal: Add the missing Gate B checkpoint criterion for the Phase 3 timing advisory.                                                                    
  - Add a verification bullet for:                                                                                                                      
    - NFR-001 10-minute wall clock target / advisory timing check
  - Ensure the checkpoint preserves all 4 roadmap Gate B criteria

  Done when
  - Gate B checkpoint explicitly includes the timing/advisory criterion
  - Phase 2 checkpoint matches roadmap Gate B 1:1

  ---
  T02 — Fix Gate D completeness in phase-6-tasklist.md

  Target: .dev/releases/current/v2.23-cli-portify-v3/phase-6-tasklist.md
  Goal: Add the 2 missing Gate D verification items.
  - Add explicit verification/exit bullets for:
    - No unaddressed CRITICAL findings remain
    - Overall quality threshold logic validated end-to-end

  Done when
  - Gate D checkpoint has all 5 roadmap criteria as discrete, checkable items
  - Nothing is only implied in purpose text

  ---
  Phase B — Traceability cleanup

  These are structural/minor, but worth fixing for auditability.

  T03 — Close Phase 1 traceability gaps

  Targets:
  - .dev/releases/current/v2.23-cli-portify-v3/phase-1-tasklist.md
  - .dev/releases/current/v2.23-cli-portify-v3/tasklist-index.md

  Goal: Resolve untracked Phase 1 roadmap IDs.
  - Add explicit traceability treatment for:
    - R-001 (Pre-Implementation Verification Checklist heading)
    - R-006 (Template Creation heading)
    - R-011 (Gate A)
  - Decide one consistent pattern:
    a. map parent headings to owning tasks/checkpoints, or
    b. mark them as structural/non-task trace items in the index

  Done when
  - No orphaned Phase 1 roadmap IDs remain
  - Index and phase file use the same traceability convention

  ---
  T04 — Close Phase 6 gate traceability gap

  Target: .dev/releases/current/v2.23-cli-portify-v3/tasklist-index.md
  Goal: Make R-051 traceable.
  - Add explicit mapping for Gate D / checkpoint handling
  - Follow the same convention used for other gate IDs

  Done when
  - R-051 is traceable in the index
  - Gate-to-checkpoint mapping rule is consistent across A/B/C/D

  ---
  Phase C — Acceptance criteria and wording alignment

  T05 — Strengthen Gate A wording fidelity

  Target: .dev/releases/current/v2.23-cli-portify-v3/phase-1-tasklist.md
  Goal: Make Gate A criterion 3 explicit in the checkpoint.
  - Expand wording so it explicitly says:
    - sections map 1:1 to the section-to-source mapping table

  Done when
  - Gate A checkpoint wording is no longer abbreviated
  - No reliance on task-level acceptance criteria to recover checkpoint meaning

  ---
  T06 — Make additive-only validation explicit in Phase 5 acceptance criteria

  Target: .dev/releases/current/v2.23-cli-portify-v3/phase-5-tasklist.md
  Goal: Promote an existing validation check into formal acceptance criteria.
  - Add explicit acceptance criterion that additive-only incorporation is verified/respected

  Done when
  - T05.02 acceptance criteria includes additive-only validation explicitly
  - Behavioral validation list and acceptance criteria are aligned

  ---
  Phase D — Ambiguity reduction / consistency notes

  T07 — Clarify brainstorm failure type semantics

  Targets:
  - .dev/releases/current/v2.23-cli-portify-v3/phase-5-tasklist.md
  - optionally .dev/releases/current/v2.23-cli-portify-v3/tasklist-index.md if needed for notes

  Goal: Resolve or document the brainstorm_failed vs brainstorm_timeout ambiguity.
  - Choose one of:
    a. explicitly state timeout is represented as brainstorm_failed for this scenario, or
    b. distinguish timeout from other brainstorm failures in validation wording
  - Keep consistent with the roadmap/contract semantics already defined

  Done when
  - Validation wording no longer leaves ambiguity
  - Timeout scenario language is internally consistent

  ---
  T08 — Clarify FR-013 / Phase 2 ownership wording

  Target: .dev/releases/current/v2.23-cli-portify-v3/phase-2-tasklist.md
  Goal: Reduce audit confusion around umbrella vs sub-task ownership.
  - Keep current structure if desired, but clarify that:
    - R-013 / FR-013 is umbrella rewrite/removal scope
    - T02.01 and T02.03 cover different sub-aspects of that umbrella

  Done when
  - Traceability readers can tell why FR-013 appears in more than one task
  - No ambiguity about task ownership

  ---
  T09 — Clarify cross-phase SC-010 ownership

  Targets:
  - .dev/releases/current/v2.23-cli-portify-v3/phase-4-tasklist.md
  - optionally .dev/releases/current/v2.23-cli-portify-v3/tasklist-index.md

  Goal: Avoid confusion where Gate C references SC-010 but validation ownership is cross-phase.
  - Add note or wording that SC-010 is checkpoint-preserved here, while validation is exercised in later validation work

  Done when
  - Gate C remains intact
  - Readers understand why formula verification appears at checkpoint level

  ---
  Phase E — Final consistency pass

  T10 — Re-validate all affected artifacts

  Targets: all edited phase tasklists + tasklist-index.md
  Goal: Confirm the remediation did not introduce new drift.
  - Re-check:
    - gate completeness
    - roadmap item traceability
    - tier distribution unchanged
    - deliverable mappings unchanged
    - no new contradictions

  Done when
  - All previous MAJOR findings are cleared
  - Remaining findings, if any, are cosmetic only

  ---
  Recommended execution order

  1. T01
  2. T02
  3. T03
  4. T04
  5. T05
  6. T06
  7. T07
  8. T08
  9. T09
  10. T10
