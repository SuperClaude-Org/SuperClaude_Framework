# D-0036: User Review Gates with --skip-review Bypass

## Overview

Centralized review gate module at `src/superclaude/cli/cli_portify/review.py`
providing consistent user review prompts at pipeline decision points.

## Review Gate Steps

- **design-pipeline** (Step 4): After design artifact is produced
- **panel-review** (Step 7): After convergence completes

## Protocol

1. Gate checks if step requires review via `REVIEW_GATE_STEPS`
2. If `--skip-review` is set, returns `SKIPPED` (auto-continue)
3. Otherwise, prompts on stderr: `[REVIEW GATE] Step '<name>' produced: <path>`
4. User responds:
   - `y`/`yes` -> `ACCEPTED`, pipeline continues
   - `n`/anything else -> `REJECTED`, pipeline halts
   - EOF/Ctrl+C -> `REJECTED`

## Status: `ReviewDecision` Enum

- `ACCEPTED`: User approved, continue
- `REJECTED`: User rejected, emit `USER_REJECTED` status
- `SKIPPED`: `--skip-review` bypassed, auto-continue

## API

```python
from superclaude.cli.cli_portify.review import review_gate, ReviewDecision

should_continue, decision = review_gate(
    step_name="design-pipeline",
    artifact_path="/path/to/artifact.md",
    skip_review=config.skip_review,
)
if not should_continue:
    # decision == ReviewDecision.REJECTED -> USER_REJECTED
    ...
```
