# D-0024: test_explicit_max_turns_override regression test

## Test Added
- File: `tests/sprint/test_config.py`
- Test: `TestLoadSprintConfig::test_explicit_max_turns_override`
- Verifies NFR-006/SC-004: `load_sprint_config(max_turns=50)` returns config with max_turns=50, not default 100

## Verification
```
tests/sprint/test_config.py::TestLoadSprintConfig::test_explicit_max_turns_override PASSED
```
