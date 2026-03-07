# D-0010: Turn Counting and TurnLedger Debit Wiring Evidence

## Deliverable

- Turn counting logic that extracts actual turn count from subprocess NDJSON output
- TurnLedger debit wiring: consumed turns debited from ledger after each task completion
- Pre-remediation budget check: `ledger.can_remediate()` before spawning remediation subprocess

## Implementation

- **count_turns_from_output()** added to `src/superclaude/cli/sprint/monitor.py`:
  - Counts `"type":"assistant"` lines in NDJSON output
  - Handles missing files, empty files, malformed lines
- **Debit wiring** in `execute_phase_tasks()` (`src/superclaude/cli/sprint/executor.py`):
  - Pre-debits minimum_allocation from ledger before task launch
  - Post-task reconciliation: adjusts for actual turns consumed
  - Credits back unused pre-allocation when actual < minimum_allocation
- **Pre-remediation check**: `ledger.can_remediate()` already in TurnLedger (Phase 1)

## Verification

```
uv run pytest tests/sprint/test_monitor.py -k CountTurns -v
# 6 passed

uv run pytest tests/sprint/test_executor.py -k "turn_count or debit" -v
# 5 passed
```

### Test Coverage

| Test | File | Status |
|------|------|--------|
| test_counts_assistant_turns | test_monitor.py | PASS |
| test_zero_turns_on_empty | test_monitor.py | PASS |
| test_zero_turns_missing_file | test_monitor.py | PASS |
| test_no_assistant_messages | test_monitor.py | PASS |
| test_many_turns | test_monitor.py | PASS |
| test_handles_malformed_json_lines | test_monitor.py | PASS |
| test_debit_called_with_correct_turns | test_executor.py | PASS |
| test_can_remediate_prevents_remediation_when_low | test_executor.py | PASS |
| test_can_remediate_allows_when_sufficient | test_executor.py | PASS |
| test_turn_count_zero_reimburses_minimum | test_executor.py | PASS |
| test_per_task_budget_debit_credit | test_executor.py | PASS |

## Files Modified

- `src/superclaude/cli/sprint/monitor.py` (added count_turns_from_output)
- `tests/sprint/test_monitor.py` (added TestCountTurnsFromOutput)
- `tests/sprint/test_executor.py` (added TestTurnCountDebit)
