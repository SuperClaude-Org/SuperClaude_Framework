---
phase: 3
status: PASS
tasks_total: 7
tasks_passed: 7
tasks_failed: 0
---

# Phase 3 Result — FIX-ARG-TOO-LONG Constants and Guard

## Summary

All 7 tasks completed successfully. The embed guard in `executor.py` now uses derived constants
based on the Linux kernel `MAX_ARG_STRLEN` (128 KB), includes a module-level assertion tripwire,
and measures the full composed string (prompt + embedded) against `_EMBED_SIZE_LIMIT` (120 KB).
All 6 tests pass with 0 failures.

## Per-Task Status

| Task ID | Title | Tier | Status | Evidence |
|---------|-------|------|--------|----------|
| T03.01 | Replace embed constants in executor.py | STRICT | pass | D-0012/evidence.md |
| T03.02 | Add module-level overhead assertion in executor.py | STRICT | pass | D-0013/evidence.md |
| T03.03 | Fix embed guard to measure composed string | STRICT | pass | D-0014/evidence.md |
| T03.04 | Update renamed test_embed_size_guard_fallback class | STANDARD | pass | D-0015/evidence.md |
| T03.05 | Add TestComposedStringGuard test class | STANDARD | pass | D-0016/evidence.md |
| T03.06 | Add exact-limit boundary test | STRICT | pass | D-0017/evidence.md |
| T03.07 | Run roadmap tests for Phase 3 validation | EXEMPT | pass | D-0018/evidence.md |

## Files Modified

- `src/superclaude/cli/roadmap/executor.py`
- `tests/roadmap/test_file_passing.py`

## Key Changes

### executor.py

**Constants replaced** (T03.01):
```python
# Before:
_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB

# After:
_MAX_ARG_STRLEN = 128 * 1024          # Linux kernel compile-time constant
_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024  # 2.3x safety factor; measured template peak ~3.4 KB
_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD  # 120 KB = 122,880 bytes
```

**Assertion added** (T03.02):
```python
assert _PROMPT_TEMPLATE_OVERHEAD >= 4096, (
    "Kernel margin violated: _PROMPT_TEMPLATE_OVERHEAD must be >=4096 bytes "
    "to stay safely below MAX_ARG_STRLEN=128 KB; measured template peak ~3.4 KB"
)
```

**Guard fixed** (T03.03):
```python
# Now measures composed string, not just embedded:
composed = step.prompt + "\n\n" + embedded
# <= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB
if len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
```

### test_file_passing.py

- Renamed `TestSizeGuardFallback` → `TestEmbedSizeGuardFallback` (T03.04)
- Added `TestComposedStringGuard` with `test_prompt_plus_embedded_exceeds_limit` (T03.05)
- Added `TestExactLimitBoundary` with at-limit and over-limit tests (T03.06)

## Test Results

```
$ uv run pytest tests/roadmap/test_file_passing.py -v
6 passed in 0.10s
```

| Test | Result |
|------|--------|
| TestPromptContainsEmbeddedContent::test_prompt_contains_embedded_content | PASS |
| TestPathsWithSpaces::test_paths_with_spaces | PASS |
| TestEmbedSizeGuardFallback::test_embed_size_guard_fallback | PASS |
| TestComposedStringGuard::test_prompt_plus_embedded_exceeds_limit | PASS |
| TestExactLimitBoundary::test_exact_limit_embeds_inline | PASS |
| TestExactLimitBoundary::test_one_over_limit_triggers_fallback | PASS |

## Blockers for Next Phase

None.

EXIT_RECOMMENDATION: CONTINUE
