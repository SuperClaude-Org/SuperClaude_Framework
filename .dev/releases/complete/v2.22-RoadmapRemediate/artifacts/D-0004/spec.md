# D-0004: Finding Dataclass

## Location
`src/superclaude/cli/roadmap/models.py`

## Fields (spec §2.3.1)

| # | Field | Type | Default | Description |
|---|-------|------|---------|-------------|
| 1 | id | str | (required) | Finding identifier, e.g. "F-01" |
| 2 | severity | str | (required) | BLOCKING, WARNING, or INFO |
| 3 | dimension | str | (required) | Category: Schema, Cross-file, Traceability, Decomposition, etc. |
| 4 | description | str | (required) | Human-readable finding description |
| 5 | location | str | (required) | File path and line reference |
| 6 | evidence | str | (required) | Supporting evidence text |
| 7 | fix_guidance | str | (required) | Recommended fix action |
| 8 | files_affected | list[str] | [] | List of file paths affected by the finding |
| 9 | status | str | "PENDING" | Lifecycle status per D-0003: PENDING, FIXED, FAILED, SKIPPED |
| 10 | agreement_category | str | "" | Agreement category: BOTH_AGREE, ONLY_A, ONLY_B, CONFLICT |

## Status Validation

`__post_init__` enforces that `status` must be one of: PENDING, FIXED, FAILED, SKIPPED.
Invalid values raise `ValueError`. Valid statuses defined in module-level `VALID_FINDING_STATUSES` frozenset.

## Import

```python
from superclaude.cli.roadmap.models import Finding, VALID_FINDING_STATUSES
```
