# D-0017: Update test_models.py:188 assertion to == 100

## Change
- File: `tests/sprint/test_models.py:188`
- Old: `assert cfg.max_turns == 50`
- New: `assert cfg.max_turns == 100`

## Verification
```
tests/sprint/test_models.py::TestSprintConfig::test_defaults PASSED
```
