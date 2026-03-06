# D-0027: Combined M2 Pipeline Pass Specification

## Module
`src/superclaude/cli/pipeline/combined_m2_pass.py`

## Architecture
Combined invariant registry + FMEA pass with shared scanning infrastructure.

### Pipeline Position
After M1 decomposition, before M3 guard analysis.

### Pass Order
1. **Shared scanning**: filter deliverables by kind (exclude previously generated M2 deliverables)
2. **Invariant registry sub-pass**: detect state variables → mutation inventory → emit verification deliverables
3. **FMEA sub-pass**: enumerate domains → classify failures → promote above-threshold
4. **Cross-linking**: connect invariant entries to fmea_test deliverables
5. **Combine output**: merge generated deliverables + render section

### Shared Infrastructure
- Single pass over deliverable descriptions feeds both detector chains
- Invariant entries inform FMEA Signal 1 (cross-reference)
- Both sub-passes share the same filtered source deliverable list

## Cross-Linking Schema
- InvariantEntry.verification_deliverable_ids includes both:
  - invariant_check IDs (from verification emitter)
  - fmea_test IDs (from promotion, when referencing same mutation sites)
- Links are bidirectional: fmea_test metadata contains source_deliverable_id

## Idempotency
- Filters out `invariant_check` and `fmea_test` deliverables before processing
- Running twice produces identical output
- Re-running with generated deliverables fed back doesn't double-count

## M2 Grouping Decision
From adversarial Round 3: both advocates agreed P1 (invariant) + P2 (FMEA) share trigger detection infrastructure.
