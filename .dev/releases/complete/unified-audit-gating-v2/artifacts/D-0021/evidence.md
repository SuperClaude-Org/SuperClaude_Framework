# D-0021: test_max_sustainable_tasks_at_08 unit test

## Test Added
- File: `tests/sprint/test_models.py`
- Test: `TestTurnLedger::test_max_sustainable_tasks_at_08`
- Verifies: budget=200, rate=0.8 sustains 49 tasks before `can_launch()` returns False (remaining=4 < minimum_allocation=8)

## Verification
```
tests/sprint/test_models.py::TestTurnLedger::test_max_sustainable_tasks_at_08 PASSED
```
