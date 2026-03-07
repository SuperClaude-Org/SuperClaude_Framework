# D-0001: TurnLedger Dataclass Evidence

## Deliverable
TurnLedger dataclass in `src/superclaude/cli/sprint/models.py`

## Implementation
- Added `TurnLedger` dataclass with fields: `initial_budget`, `consumed`, `reimbursed`, `reimbursement_rate`, `minimum_allocation`, `minimum_remediation_budget`
- Methods: `debit()`, `credit()`, `can_launch()`, `can_remediate()`, `available()`
- Budget monotonicity enforced: `consumed` only increases, negative debit/credit raises `ValueError`
- Also added `PhaseStatus.INCOMPLETE` enum member with correct `is_terminal=True`, `is_success=False`, `is_failure=True`

## Test Results
```
uv run pytest tests/sprint/test_models.py -k TurnLedger -v
15 passed in 0.08s
```

## Acceptance Criteria Verification
- [x] `uv run pytest tests/sprint/test_models.py -k TurnLedger` exits 0 with all arithmetic tests passing
- [x] Budget monotonicity invariant holds: consumed never decreases
- [x] `available() = initial_budget - consumed + reimbursed`
- [x] `can_launch()` returns False when `available() < minimum_allocation`
- [x] `can_remediate()` returns False when `available() < minimum_remediation_budget`
- [x] TurnLedger follows existing dataclass conventions in models.py
