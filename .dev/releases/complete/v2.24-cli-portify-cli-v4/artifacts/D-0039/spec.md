# D-0039: Comprehensive Failure-Path Handling

## 7 Failure Types

| # | Type | Handler | Terminal | Resumable | Recovery |
|---|------|---------|----------|-----------|----------|
| 1 | Missing template | `handle_missing_template` | Yes | No | Provide file, re-run |
| 2 | Missing skills | `handle_missing_skills` | No | N/A | Install skills (fallback active) |
| 3 | Malformed artifact | `handle_malformed_artifact` | Yes | If step 5-7 | Re-run step |
| 4 | Timeout | `handle_timeout` | Yes | If step 5-7 | Increase timeout/budget |
| 5 | Partial artifact | `handle_partial_artifact` | Yes | If step 5-7 | Re-run (never trust) |
| 6 | Non-writable output | `handle_non_writable_output` | Yes | No | Fix permissions |
| 7 | Exhausted budget | `handle_budget_exhausted` | Yes | Yes | Increase max-convergence |

## NFR-009 Compliance

All handlers produce `PortifyStepResult` with:
- Populated `portify_status` (never None)
- Populated `failure_classification` (except missing-skills which is a warning)
- Populated `resume_context` with resume command for resumable steps
- Clear `error_message` and `remediation` guidance

Implementation: `src/superclaude/cli/cli_portify/failures.py`
