# D-0028: Combined M2 Pipeline Pass Integration Test Evidence

## Test Execution
- **File**: `tests/pipeline/test_combined_m2_pass.py`
- **Tests**: 11 passed, 0 failed
- **Duration**: 0.04s

## Integration Test Results

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| Both sections present (invariant + FMEA) | Both in markdown | Both present | PASS |
| Invariant entries generated | ≥1 entry | Entries generated | PASS |
| Invariant check deliverables generated | ≥1 inv_check | Generated | PASS |
| FMEA failure modes detected | ≥1 failure mode | Detected | PASS |
| Cross-links correct | Entries have verification IDs | Cross-linked | PASS |
| Silent corruption triggers Release Gate | Blocking violations | Triggered correctly | PASS |
| Idempotent (same input) | Identical output | Identical | PASS |
| Idempotent (with generated fed back) | Same entry count | Same count | PASS |
| All generated is union of inv_check + fmea_test | Correct total | Correct | PASS |
| Empty input | No errors | Clean output | PASS |
| Non-implement only | No invariant entries | Zero entries | PASS |

## Test Input
5 deliverables:
- D2.1: State variable introduction (replay offset counter)
- D3.1: State variable mutation (increment replay offset)
- D4.1: Computational deliverable (filter + compute)
- D2.2: State variable introduction (session cursor flag)
- D1.1: Non-computational (documentation)

## Verification
- Invariant registry detects offset and cursor variables
- FMEA enumerates domains for the filter/compute deliverable
- Cross-links bind invariant entries to generated fmea_test deliverables
- Idempotency verified with re-run and with generated fed back
