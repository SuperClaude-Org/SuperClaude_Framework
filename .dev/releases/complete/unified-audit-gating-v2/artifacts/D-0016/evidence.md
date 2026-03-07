# D-0016: Update test_models.py:54 assertion to == 100

## Change
- File: `tests/pipeline/test_models.py:54`
- Old: `assert cfg.max_turns == 50`
- New: `assert cfg.max_turns == 100`

## Verification
```
tests/pipeline/test_models.py::TestPipelineConfig::test_defaults PASSED
```
All 21 tests in `tests/pipeline/test_models.py` pass.
