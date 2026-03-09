# Refactoring Plan: Merge into Base (Variant 3)

## Overview
- Base: Variant 3 (forensic-diagnostic-report.md)
- Incorporating strengths from: Variant 1, Variant 2, Variant 4
- Planned changes: 6
- Risk level: Medium

## Planned Changes

### Change 1: Replace linear stage-only synthesis with epistemic partitioning
- **Source variant and section**: Variant 1, Parts I-VI and unresolved-conflicts structure
- **Target location in base**: Whole-document structure
- **Integration approach**: restructure
- **Rationale**: Debate points S-001, S-003, and C-008 favored Variant 1’s ability to preserve contradiction recovery and minority insight.
- **Risk level**: Medium

### Change 2: Preserve Variant 3 evidence chains as the factual backbone
- **Source variant and section**: Variant 3, executive memo, cross-cutting findings, evidence chains
- **Target location in base**: findings and evidence sections throughout merged document
- **Integration approach**: preserve and sharpen
- **Rationale**: Variant 3 won the highest-severity points on causal precision, evidence hierarchy, and boundary evidence.
- **Risk level**: Low

### Change 3: Insert explicit confidence-signal / proxy table
- **Source variant and section**: Variant 2, Section E proxy table
- **Target location in base**: Cross-cutting findings / confidence inflation section
- **Integration approach**: insert
- **Rationale**: Debate point C-002 strongly favored Variant 2 for explaining false confidence.
- **Risk level**: Low

### Change 4: Add seam-centered boundary framing and blast-radius language
- **Source variant and section**: Variant 4, seam failures and “misallocated rigor” framing
- **Target location in base**: system boundaries / cross-cutting findings
- **Integration approach**: append and edit
- **Rationale**: Debate point S-004 and A-002 favored Variant 4’s seam language.
- **Risk level**: Low

### Change 5: Preserve unresolved contradictions rather than forcing closure
- **Source variant and section**: Variant 1 unresolved conflicts + Variant 4 plural-theory framing
- **Target location in base**: new unresolved conflicts section near conclusion
- **Integration approach**: insert
- **Rationale**: Debate points X-001 and X-002 remained partially unresolved; user explicitly requested contradiction recovery and false-consensus detection.
- **Risk level**: Low

### Change 6: Add hidden assumptions section with clearly labeled shared assumptions
- **Source variant and section**: Variant 1 hidden assumptions and adversarial shared assumptions
- **Target location in base**: after unresolved conflicts
- **Integration approach**: insert
- **Rationale**: Debate point C-008 and shared-assumption analysis favored explicit assumption handling.
- **Risk level**: Medium

## Changes NOT Being Made

| Diff Point | Non-Base Approach | Rationale for Keeping Base |
|------------|-------------------|---------------------------|
| C-001 | Variant 2 single dominant category-error framing | Debate found stronger evidence for a multi-mechanism diagnosis anchored in concrete evidence chains. |
| C-001 / X-001 | Variant 4 theory-only framing with no primary base | Too weak on evidence hierarchy for base selection despite strong minority-insight preservation. |
| S-001 | Variant 1 as direct base | User warned against privileging the already-merged foundation artifact over the original three peer analyses. |

## Risk Summary

| Change # | Risk | Impact if Failed | Rollback |
|----------|------|------------------|----------|
| 1 | Medium | Over-complex merged structure or duplicated sections | Revert to base structure and re-insert only conflict/assumption sections |
| 2 | Low | Evidence chains weakened | Restore original Variant 3 passages |
| 3 | Low | Redundant explanation | Remove inserted proxy table |
| 4 | Low | Seam framing duplicates existing text | Remove appended seam-focused edits |
| 5 | Low | Reader confusion from unresolved tensions | Collapse section back into cross-cutting findings |
| 6 | Medium | Assumption section feels speculative | Remove or reduce to a short caveat list |

## Review Status
- [x] Auto-approved (default)
- [ ] User-approved (--interactive)
- Approved by: auto
- Approval timestamp: 2026-03-08T00:00:00Z