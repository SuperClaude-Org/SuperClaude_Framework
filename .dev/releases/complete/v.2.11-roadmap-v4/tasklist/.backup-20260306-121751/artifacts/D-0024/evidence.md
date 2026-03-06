# D-0024: FMEA Failure Mode Classifier Test Evidence

## Test Execution
- **File**: `tests/pipeline/test_fmea_classifier.py`
- **Tests**: 11 passed, 0 failed
- **Duration**: 0.04s

## Scenario Results

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| Offset advances by wrong amount, no error raised | silent + wrong_state | silent + wrong_state | PASS |
| TypeError on null input | immediate | immediate | PASS |
| Filter returns empty instead of raising | delayed/silent | delayed | PASS |
| Signal 2 independent (no invariant predicates) | silent via signal_2 | silent via signal_2 | PASS |
| Severity ordering (data_loss > wrong_state > degraded > cosmetic) | correct ordering | correct ordering | PASS |
| Silent corruption elevated to wrong_state minimum | wrong_state minimum | wrong_state minimum | PASS |
| All detection difficulty levels classifiable | 3 levels | 3 levels | PASS |
| All severity levels classifiable | 4 levels | 4 levels | PASS |
| Empty deliverables | empty results | empty results | PASS |
| No domains → no results | empty results | empty results | PASS |
| Non-computational excluded | empty results | empty results | PASS |

## Signal 2 Independence Verification
Test `test_signal_2_independent_without_invariants` passes `invariant_entries=[]` and verifies
that Signal 2 independently detects silent corruption for "Increment replay offset, no validation
of new position" on zero input domain.
