# Refactoring Plan

## Overview
- **Base variant**: Variant 1 (merged-decision.md) — score 0.967
- **Incorporated variants**: Variant 2 (merged-adversarial-analysis.md) — score 0.675
- **Planned changes**: 3
- **Changes NOT being made**: 2
- **Overall risk**: Low (additive changes only)

## Planned Changes

### Change #1: Add phased-extraction framing to Recommendation section
- **Source variant**: Variant 2, Section "What the Stronger Proposal Still Contributes" + "Recommended Plan"
- **Target location**: Variant 1, "Recommendation" section (after Option 3 endorsement)
- **Integration approach**: Append — add paragraph reframing targeted fixes as Phase 1 of longer extraction roadmap
- **Rationale**: U-004 rated Medium value; adds forward-looking context without contradicting recommendation. V1 advocate conceded V2's phased plan was "arguably more actionable."
- **Risk level**: Low (additive)

### Change #2: Add pro-unification architectural value acknowledgment
- **Source variant**: Variant 2, Section "What the Stronger Proposal Still Contributes" (Section 7)
- **Target location**: Variant 1, between "Challenge 5" and "Three Options" sections
- **Integration approach**: Insert — add brief section acknowledging long-term extraction value
- **Rationale**: U-005 rated Medium value; V1 currently frames unification only as rejected/conditional. V2's acknowledgment of architectural direction adds intellectual balance.
- **Risk level**: Low (additive)

### Change #3: Add hypothesis-framing language to Recommendation
- **Source variant**: Variant 2, "Final Verdict" — "executor unification as a hypothesis to validate, not a decision already earned"
- **Target location**: Variant 1, "Recommendation" section
- **Integration approach**: Append — add framing sentence
- **Rationale**: Both advocates agreed this is a strong framing. Converts recommendation from binary (accept/reject) to scientific (hypothesis to test).
- **Risk level**: Low (additive)

## Changes NOT Being Made

### Rejected: Replace V1's Verified/Unverified treatment with V2's approach
- **Diff point**: X-001, X-002
- **Variant 2 approach**: List extraction history and unification complexity as "Unverified"
- **Rationale for rejection**: V1 cites specific code evidence (`pipeline/process.py:3`, commit `6548f17`, NFR-007) that V2's own body implicitly confirms. V2 advocate conceded this was an internal inconsistency. V1's SETTLED classification is better supported.

### Rejected: Replace V1's structure with V2's narrative format
- **Diff point**: S-001
- **Variant 2 approach**: Narrative sections ("What Gets Right", "What Contributes")
- **Rationale for rejection**: V1's challenge-based structure scored higher on Structure (5/5 vs 3/5) and Completeness (5/5 vs 1/5). V2 advocate conceded traceability value of V1's structure.

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Phased framing | Low | Additive paragraph | Delete paragraph |
| #2 Pro-unification value | Low | Additive section | Delete section |
| #3 Hypothesis language | Low | Additive sentence | Delete sentence |

## Review Status
- **Approval**: Auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-05
