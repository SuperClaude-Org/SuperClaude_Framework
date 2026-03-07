# D-0019: Update test_models.py:527 assertion to == 0.8

## Change
- File: `tests/sprint/test_models.py:527`
- Old: `assert ledger.reimbursement_rate == 0.5`
- New: `assert ledger.reimbursement_rate == 0.8`

## Verification
```
tests/sprint/test_models.py::TestTurnLedger::test_defaults PASSED
```
