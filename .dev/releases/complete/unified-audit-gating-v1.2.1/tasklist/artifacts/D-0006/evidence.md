# D-0006: Per-Task Subprocess Orchestration Loop Evidence

## Deliverable

Per-task subprocess orchestration loop in `src/superclaude/cli/sprint/executor.py` that iterates over TaskInventory, spawns one subprocess per task, and integrates with TurnLedger for budget allocation and tracking.

## Implementation

- **Data models** added to `src/superclaude/cli/sprint/models.py`:
  - `TaskStatus` enum: PASS, FAIL, INCOMPLETE, SKIPPED
  - `TaskResult` dataclass: task, status, turns_consumed, exit_code, started_at, finished_at, output_bytes
- **Orchestration function** `execute_phase_tasks()` added to `src/superclaude/cli/sprint/executor.py`:
  - Iterates task inventory, spawns one subprocess per task
  - Pre-debits minimum_allocation from ledger, reconciles actual consumption post-task
  - Starvation prevention: skips remaining tasks when budget insufficient
  - Returns (results, remaining_task_ids) tuple for HALT signal

## Verification

```
uv run pytest tests/sprint/test_executor.py -k per_task -v
# 8 passed
```

### Test Coverage

| Test | Status |
|------|--------|
| test_per_task_spawns_one_subprocess_per_task | PASS |
| test_per_task_all_pass | PASS |
| test_per_task_budget_prevents_starvation | PASS |
| test_per_task_budget_debit_credit | PASS |
| test_per_task_empty_inventory | PASS |
| test_per_task_fail_records_status | PASS |
| test_per_task_timeout_produces_incomplete | PASS |
| test_per_task_no_ledger_always_launches | PASS |

## Files Modified

- `src/superclaude/cli/sprint/models.py` (added TaskStatus, TaskResult)
- `src/superclaude/cli/sprint/executor.py` (added execute_phase_tasks, _run_task_subprocess)
- `tests/sprint/test_executor.py` (added TestPerTaskOrchestration)
