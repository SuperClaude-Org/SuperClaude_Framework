# D-0043 Spec: ALREADY_TRACKED Report Section

## Task Reference
- Task: T05.04
- Roadmap Item: R-043
- AC: AC1 (supporting)

## Section Format
Table with columns: Finding Path, Registry Entry ID, Matched Pattern, Classification

## Behavior
- Section is **present** only when registry matches exist
- Section is **absent** (not empty) when no matches exist
- Positioned after main findings sections, before validation section

## API
```python
from superclaude.cli.audit.already_tracked import build_already_tracked_section

section = build_already_tracked_section(suppressed_matches)
if section.is_present:
    report_dict.update(section.to_dict())
    markdown += section.render_markdown()
```

## Implementation
- Source: `src/superclaude/cli/audit/already_tracked.py`
- Tests: `tests/audit/test_already_tracked.py` (7 tests)
