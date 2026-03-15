# D-0016: TestComposedStringGuard test class

## Task: T03.05

**Status**: PASS

## Test Added

```python
class TestComposedStringGuard:
    """Guard measures the composed string (prompt + embedded), not just the embedded file."""

    def test_prompt_plus_embedded_exceeds_limit(self, tmp_path: Path, caplog):
        """File at 90% of _EMBED_SIZE_LIMIT plus a large prompt exceeds composed limit."""
        file_size = int(_EMBED_SIZE_LIMIT * 0.9)
        input_file = tmp_path / "spec.md"
        input_file.write_text("y" * file_size)

        remaining = _EMBED_SIZE_LIMIT - file_size
        large_prompt = "P" * (remaining + 1024)  # overshoot by 1 KB
        ...
        # Asserts: fallback fires, file content absent, --file in extra_args
```

## Verification

```
$ uv run pytest tests/roadmap/test_file_passing.py::TestComposedStringGuard -v
PASSED tests/roadmap/test_file_passing.py::TestComposedStringGuard::test_prompt_plus_embedded_exceeds_limit
1 passed in 0.06s
```

- Test class `TestComposedStringGuard` exists ✅
- Method `test_prompt_plus_embedded_exceeds_limit` ✅
- Scenario: file at 90% + large prompt overshoots limit ✅
- Assertions: fallback fires, content absent, `--file` in `extra_args` ✅
