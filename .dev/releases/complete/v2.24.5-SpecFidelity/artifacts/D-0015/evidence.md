# D-0015: Updated test_embed_size_guard_fallback class

## Task: T03.04

**Status**: PASS

## Changes

- Renamed `TestSizeGuardFallback` → `TestEmbedSizeGuardFallback`
- Renamed test method `test_100kb_guard_fallback` → `test_embed_size_guard_fallback`
- Updated docstring to reference `_EMBED_SIZE_LIMIT` (not "100KB")
- No hardcoded byte counts in assertions (uses `_EMBED_SIZE_LIMIT + 1024`)
- `_EMBED_SIZE_LIMIT` imported at top of file

## Verification

```
$ uv run pytest tests/roadmap/test_file_passing.py::TestEmbedSizeGuardFallback -v
PASSED tests/roadmap/test_file_passing.py::TestEmbedSizeGuardFallback::test_embed_size_guard_fallback
1 passed in 0.05s
```

- Import: `from superclaude.cli.roadmap.executor import _EMBED_SIZE_LIMIT` ✅
- No hardcoded byte counts ✅
- Docstring references `_EMBED_SIZE_LIMIT` ✅
