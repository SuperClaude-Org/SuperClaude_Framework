# D-0032: Explicit Override Regression Test

## Command
```
uv run pytest tests/sprint/test_config.py::TestLoadSprintConfig::test_explicit_max_turns_override -v
```

## Result
- **Status**: PASSED
- **Isolation**: Yes (1 collected, 1 passed)
- **Duration**: 0.09s
- **SC-005 Verified**: Explicit `--max-turns=50` overrides new default of 100

## Verdict
**PASS** — SC-005 confirmed: backward compatibility preserved for explicit max_turns overrides.
