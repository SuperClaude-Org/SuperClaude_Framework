# D-0018: Update test_config.py:215 assertion to == 100

## Change
- File: `tests/sprint/test_config.py:215`
- Old: `assert config.max_turns == 50`
- New: `assert config.max_turns == 100`

## Verification
```
tests/sprint/test_config.py::TestLoadSprintConfig::test_valid_config PASSED
```
