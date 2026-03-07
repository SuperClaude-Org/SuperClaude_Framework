# D-0011: Shared Assumption Extraction Sub-Phase in Step 1

## Overview

Shared assumption extraction sub-phase added to Step 1 of the adversarial debate protocol. Addresses the AD-2 "agreement = no scrutiny" blind spot by identifying agreement points, enumerating assumptions behind each, and classifying as STATED/UNSTATED/CONTRADICTED.

## Algorithm

1. **Agreement Identification**: Scan all diff categories for points where all variants converge
2. **Assumption Enumeration**: For each agreement, ask "What must be true for this agreement to be valid?" and extract preconditions
3. **Classification**:
   - STATED: Precondition explicitly mentioned in at least one variant
   - UNSTATED: Precondition implicit — no variant states it, all depend on it
   - CONTRADICTED: Precondition inconsistent — variants depend on it but evidence contradicts it
4. **Promotion**: UNSTATED preconditions become synthetic [SHARED-ASSUMPTION] diff points (A-NNN)

## Integration Points

| Location | Change |
|----------|--------|
| Step 1 Overview (line ~96) | Added shared_assumption_extraction sub-phase description |
| After Unique Contribution Extraction | Added full Shared Assumption Extraction Engine section |
| diff-analysis.md Assembly | Added `6_shared_assumptions` section with A-NNN table |
| Assembly Metadata | Updated to include shared assumptions count |
| Assembly Validation | Updated to validate A-NNN ID sequences |

## AC-AD2-1 Test Scenario

- Input: 3 variants all assuming 1:1 event-widget mapping
- Expected: UNSTATED precondition "1:1 event-widget mapping" is surfaced as A-001
- Classification: UNSTATED

## Deliverable Status

- **Task**: T02.07
- **Roadmap Item**: R-011
- **Status**: COMPLETE
- **Tier**: STRICT
