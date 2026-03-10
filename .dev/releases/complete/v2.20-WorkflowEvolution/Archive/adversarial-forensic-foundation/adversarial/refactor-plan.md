# Refactoring Plan

## Overview
- Base variant: B (forensic-diagnostic-report)
- Incorporated variants: A (workflow-meta-analysis), C (workflow-failure-theories)
- Total changes planned: 8
- Overall risk: Low (additive restructuring, no content loss)
- Approval: auto-approved (non-interactive mode)

## Planned Changes

### Change 1: Restructure around findings/theories/conflicts taxonomy
- Source: C — epistemic separation principle
- Target: Document-level organization
- Integration: Replace B's stage-based primary structure with: Validated Findings → Partially Validated Theories → Unresolved Conflicts → Hidden Assumptions → Evidence Chains → System Boundaries
- Rationale: User explicitly requested this structure. C's epistemic honesty approach (separating what we know from what we theorize) is superior for a forensic foundation.
- Risk: Low (restructuring, not content removal)

### Change 2: Incorporate proxy measurement table
- Source: A, Section E
- Target: Within Validated Finding on confidence inflation
- Integration: Embed A's Signal→Measures→Proxy For→Gap table as the definitive confidence-inflation decomposition
- Rationale: Debate consensus: A's table is the most analytically useful artifact for this topic (90% confidence)
- Risk: Low (additive)

### Change 3: Incorporate Can/Cannot table for adversarial stage
- Source: A, Section C
- Target: Within Validated Finding on adversarial limitations
- Integration: Embed A's Can Catch / Cannot Catch table
- Rationale: Debate consensus: most specific and falsifiable decomposition (75% confidence)
- Risk: Low (additive)

### Change 4: Incorporate seam enumeration
- Source: C, Cross-stage blind spot #4
- Target: System Boundaries section
- Integration: Use C's 6-seam enumeration as the boundary framework, augmented with B's specific evidence at each boundary
- Rationale: Debate consensus: C's enumeration most complete (90% confidence)
- Risk: Low (additive)

### Change 5: Add Theory 6 (shared abstractions)
- Source: C, Theory 6
- Target: Partially Validated Theories section
- Integration: Include as a partially validated theory (single-source, limited evidence)
- Rationale: Unique contribution from C, not covered by A or B
- Risk: Low (additive, clearly labeled as theory)

### Change 6: Add "category error" as partially validated theory
- Source: A, Theory 1 / Section F
- Target: Partially Validated Theories section
- Integration: Present A's "category error" thesis as a partially validated theory rather than a validated finding, because it's philosophically strong but not independently confirmed and has unfalsifiability concerns raised in debate
- Rationale: Debate raised valid concern about falsifiability (B's challenge). Keep as theory, not finding.
- Risk: Low (additive)

### Change 7: Incorporate hidden assumptions from diff analysis
- Source: Adversarial protocol analysis (A-001 through A-007)
- Target: Hidden Assumptions section
- Integration: New section enumerating unstated premises shared by all three documents
- Rationale: Protocol requirement; these assumptions are not examined by any source document
- Risk: Low (additive)

### Change 8: Consolidate duplicate claims
- Source: All three variants
- Target: Throughout
- Integration: Where all three make the same point (confidence inflation, structural≠semantic, mock boundaries), consolidate to single entry with strongest evidence rather than repeating
- Rationale: User explicitly requested: "If multiple documents make the same point, consolidate them"
- Risk: Low (deduplication)

## Changes NOT Being Made

1. **Not including B's "structurally sound" characterization**: Debate found this conflicts with B's own evidence of structural defects. The merged document will not characterize the pipeline as structurally sound.
2. **Not including A's 3-theory ranking**: The merged document uses a findings/theories taxonomy instead of A's ranked-theories format. The content of A's theories is preserved; the ranking structure is not.
3. **Not including C's Gap A-F enumeration**: These overlap with the proxy measurement table (Change 2) and add no unique information.
4. **Not proposing fixes**: All three documents and the user's instructions specify diagnostic-only output.

## Risk Summary
All 8 changes are additive (restructuring or incorporating). No content is deleted. Risk: Low across all changes.

## Review Status
Auto-approved (non-interactive mode). Timestamp: 2026-03-08.
