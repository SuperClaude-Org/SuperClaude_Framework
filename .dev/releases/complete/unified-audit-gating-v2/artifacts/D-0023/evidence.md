# D-0023: test_budget_exhaustion_property property-based test

## Test Added
- File: `tests/sprint/test_models.py`
- Test: `TestTurnLedger::test_budget_exhaustion_property`
- Verifies NFR-008: for any rate < 1.0, budget monotonically decays and reaches 0 in finite steps
- Uses deterministic seed (42) per R-005

## Verification
```
tests/sprint/test_models.py::TestTurnLedger::test_budget_exhaustion_property PASSED
```
