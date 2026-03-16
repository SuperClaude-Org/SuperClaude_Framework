# Refactoring Plan: Merged Validation Report

## Overview
- **Base variant**: Variant B (Architectural Validation)
- **Incorporated variant**: Variant A (Factual Accuracy Validation)
- **Planned changes**: 3
- **Risk**: Low (additive integration, no architectural changes)

---

## Planned Changes

### Change #1: Integrate exhaustive line-number verification
- **Source**: Variant A, FACT-01 through FACT-30
- **Target**: New "Appendix: Line-Number Verification" section in merged output
- **Rationale**: Variant A provides granular per-claim verification that Variant B references but does not replicate
- **Integration approach**: Append as appendix with summary statistics
- **Risk**: Low (additive)

### Change #2: Elevate FACT-26 finding into Step 5 assessment
- **Source**: Variant A, FACT-26 (insertion point not empty)
- **Target**: Merged output Step 5 verdict
- **Rationale**: Variant B confirms Step 5 but does not note the insertion point imprecision
- **Integration approach**: Add note to Step 5 about lines 158-160 occupying the proposed gap
- **Risk**: Low (refinement)

### Change #3: Cross-reference FACT-27 with CBS-3/Step 2
- **Source**: Variant A, FACT-27 (aggregate_task_results never called)
- **Target**: Merged output Step 2 REJECT verdict
- **Rationale**: Variant A independently verified the factual basis for Variant B's critical finding
- **Integration approach**: Add corroboration note citing FACT-27
- **Risk**: Low (strengthening evidence)

---

## Changes NOT Being Made

| Diff Point | Non-base Approach | Rationale for Rejection |
|------------|------------------|------------------------|
| S-001 (organization) | Variant A's flat FACT-NNN structure | Variant B's hierarchical structure by document section is better for readers navigating the analysis |

---

## Risk Summary
All changes are additive. No structural modifications to the base. No risk of introducing inconsistencies.

## Review Status
Auto-approved (non-interactive mode).
