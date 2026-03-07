# D-0025: test_rate_boundary_validation boundary test

## Test Added
- File: `tests/sprint/test_models.py`
- Test: `TestTurnLedger::test_rate_boundary_validation`
- Tests 4 boundary cases:
  - rate=0.0: accepted, zero reimbursement
  - rate=0.99: accepted, 9/10 reimbursed
  - rate=1.0: accepted (no validation), zero net cost (documents missing SC-001 enforcement)
  - rate=-0.1: credit(-1) raises ValueError via existing validation

## Note
TurnLedger does not currently enforce SC-001 (rate must be in (0.0, 1.0) exclusive). The test documents current behavior and verifies that the credit() validation catches negative reimbursement amounts.

## Verification
```
tests/sprint/test_models.py::TestTurnLedger::test_rate_boundary_validation PASSED
```
