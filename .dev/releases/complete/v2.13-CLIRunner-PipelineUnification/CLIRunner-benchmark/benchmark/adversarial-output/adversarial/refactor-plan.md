# Refactoring Plan: Merged Pipeline Architecture Decision

## Overview
- **Base variant**: Variant B (skeptical-counterargument)
- **Incorporated from**: Variant A (pro-unification)
- **Planned changes**: 7
- **Changes NOT being made**: 3
- **Overall risk**: Low (additive changes only — no structural reorganization of base)

## Planned Changes

### Change #1: Add documented extraction evidence to Challenge 2
- **Source**: Variant A, Section 2a-2b, Round 2 evidence
- **Target**: Challenge 2 ("The Half-Completed Extraction Narrative May Be Wrong")
- **Rationale**: Variant B conceded in Round 2 that "built for roadmap" hypothesis is wrong. pipeline/process.py:3 says "Extracted from sprint/process.py." NFR-007 confirms generic intent. Commit 6548f17 created pipeline+roadmap+reparented sprint atomically. Challenge 2 must be updated to reflect this evidence rather than maintaining a debunked hypothesis.
- **Integration approach**: Restructure Challenge 2 to acknowledge the extraction evidence while preserving the valid reframe: "extraction happened but stopped at executor boundary for good reasons"
- **Risk**: Low (improves accuracy)

### Change #2: Add concrete architecture evidence from Variant A
- **Source**: Variant A, Section 2a-2f
- **Target**: New section after Challenge 1
- **Rationale**: Variant A's evidence section documents specific file paths, line numbers, and code relationships that strengthen the architectural analysis. B's challenges are stronger when they reference specific code.
- **Integration approach**: Insert condensed evidence summary showing what the codebase actually looks like today (imports, dependencies, dead code)
- **Risk**: Low (additive)

### Change #3: Incorporate Variant A's Round 3 "partial unification" as a third option
- **Source**: Variant A, Round 3 Final Position
- **Target**: New section after Challenge 6 (before Summary)
- **Rationale**: By Round 3, Variant A evolved from "full unification" to "partial unification" — adopting execute_pipeline for sequencing while keeping sprint_run_step as a substantial closure. This represents a genuine middle-ground that the merged document should present alongside Variant B's targeted-fix approach.
- **Integration approach**: Add new section presenting 3 options: (1) Full unification (original Variant A, with its debunked claims removed), (2) Partial unification (Variant A Round 3), (3) Targeted fixes (Variant B Challenge 6). Include effort/risk/reward comparison.
- **Risk**: Medium (structural addition, but does not modify existing content)

### Change #4: Add type-level dependency analysis
- **Source**: Variant A Round 2, Evidence D
- **Target**: Within restructured Challenge 2
- **Rationale**: Sprint already imports PipelineConfig, Step, StepResult, StepStatus from pipeline (models.py). Sprint's ClaudeProcess inherits from pipeline's ClaudeProcess. This factual evidence is relevant to the architectural analysis — the extraction is already 2/3 complete at type+process level.
- **Integration approach**: Integrate as supporting evidence for the "natural stopping point" argument
- **Risk**: Low (additive evidence)

### Change #5: Correct Variant B's factual error about extraction origin
- **Source**: Variant A Round 1, pipeline/process.py:3
- **Target**: Challenge 2, point 1
- **Rationale**: B's original claim "The pipeline module was built FOR roadmap, not extracted FROM sprint" is factually wrong per code documentation. The merged document must not contain debunked claims.
- **Integration approach**: Replace speculation with documented fact, then argue the valid point: extraction was correct at models+process level but the executor boundary is the natural stopping point
- **Risk**: Low (corrects error)

### Change #6: Add dead code evidence
- **Source**: Variant A, Section 2f
- **Target**: Within evidence section or Challenge 2
- **Rationale**: _build_subprocess_argv in roadmap/executor.py:53-76 is dead code confirmed by both variants. This is a concrete, uncontested finding that should appear in the merged document.
- **Integration approach**: Brief mention as evidence of architectural drift
- **Risk**: Low (additive, uncontested)

### Change #7: Incorporate debate-settled conclusions into Summary
- **Source**: Debate transcript, scoring matrix
- **Target**: Summary table (questions that must be answered)
- **Rationale**: Several of B's original verification questions were ANSWERED during the debate (Q1 poll loop: partially answered; Q2 pipeline origin: answered; Q4 retry/parallel: answered). The merged summary should reflect which questions are now settled and which remain open.
- **Integration approach**: Update summary table to show answered vs open questions with debate evidence
- **Risk**: Low (improves accuracy)

## Changes NOT Being Made

### Rejected #1: Full executor unification proposal
- **Diff point**: C-002, X-003
- **Variant A approach**: Refactor sprint to use execute_pipeline() completely
- **Rationale for rejection**: Debate established that (a) net code reduction is 60-80 lines at best, (b) sprint_run_step closure would be 100-150 lines containing the entire poll loop, (c) effort is Large, (d) regression risk is High for production-critical path. The cost-benefit ratio does not support full unification. Both advocates moved away from this position by Round 3.

### Rejected #2: StateManager protocol
- **Diff point**: C-008
- **Variant A approach**: Shared StateManager Protocol with save()/load_resume_point()
- **Rationale for rejection**: Variant A abandoned this in Round 3 after conceding that sprint's _determine_phase_status and pipeline's gate_passed are fundamentally incompatible validation paradigms.

### Rejected #3: Parallel phases as sprint benefit
- **Diff point**: X-007
- **Variant A approach**: Claim sprint could use parallel step groups
- **Rationale for rejection**: Variant A conceded in Round 1 that sprint phases mutate the filesystem sequentially. Parallel execution would cause data races.

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Extraction evidence | Low | Improves accuracy | Revert to original Challenge 2 |
| #2 Architecture evidence | Low | Additive | Remove section |
| #3 Three-option comparison | Medium | Structural addition | Remove section |
| #4 Type dependency | Low | Additive | Remove paragraph |
| #5 Factual correction | Low | Corrects error | N/A (error should not persist) |
| #6 Dead code evidence | Low | Additive | Remove mention |
| #7 Summary update | Low | Improves accuracy | Revert to original summary |

## Review Status
- Approval: auto-approved (non-interactive mode)
- Timestamp: 2026-03-05
