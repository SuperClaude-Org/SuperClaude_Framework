---
deliverable: D-0021
task: T03.10
title: Return Contract Emission and Resume Command
status: PASS
---

# D-0021: Return Contract Emission

## Implementation

`src/superclaude/cli/cli_portify/executor.py` — `_emit_return_contract()`

## Contract Schema (return-contract.yaml)

```yaml
outcome: SUCCESS | FAILURE | TIMEOUT | INTERRUPTED | HALTED | DRY_RUN
completed_steps: [list of step IDs]
remaining_steps: [list of step IDs with PENDING or INCOMPLETE status]
resume_command: "superclaude cli-portify run --resume <step-id>"
suggested_resume_budget: <remaining_count * 25>
```

## All Outcome Paths

| Outcome | Trigger |
|---------|---------|
| SUCCESS | All steps complete |
| FAILURE | Step exits non-zero |
| TIMEOUT | Step exits 124 |
| INTERRUPTED | SIGINT/SIGTERM received |
| HALTED | TurnLedger exhausted |
| DRY_RUN | `--dry-run` flag set |

## Budget Formula

`suggested_resume_budget = remaining_steps_count * 25` (NFR-011)
This is dynamically calculated from step statuses — not hardcoded.

## Validation

`uv run pytest tests/ -k "test_return_contract"` → 10 passed
