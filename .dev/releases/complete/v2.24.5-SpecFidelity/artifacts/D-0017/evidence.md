# D-0017: Exact-limit boundary test

## Task: T03.06

**Status**: PASS

## Tests Added (in TestExactLimitBoundary)

1. `test_exact_limit_embeds_inline` — composed length == `_EMBED_SIZE_LIMIT` → inline embed (no fallback)
2. `test_one_over_limit_triggers_fallback` — composed length == `_EMBED_SIZE_LIMIT + 1` → fallback fires

## Boundary Calculation

```python
# overhead = len((step_prompt + "\n\n" + "# <path>\n```\n\n```").encode("utf-8"))
# fill_size = _EMBED_SIZE_LIMIT - overhead     # exact limit
# fill_size = _EMBED_SIZE_LIMIT - overhead + 1  # one over
```

## Verification

```
$ uv run pytest tests/roadmap/test_file_passing.py::TestExactLimitBoundary -v
PASSED tests/roadmap/test_file_passing.py::TestExactLimitBoundary::test_exact_limit_embeds_inline
PASSED tests/roadmap/test_file_passing.py::TestExactLimitBoundary::test_one_over_limit_triggers_fallback
2 passed in 0.07s
```

- Composed length exactly `_EMBED_SIZE_LIMIT` → embeds inline ✅ (validates `<=`)
- Composed length `_EMBED_SIZE_LIMIT + 1` → triggers fallback ✅
