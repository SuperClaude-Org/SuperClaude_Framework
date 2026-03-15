# D-0012: Replace embed constants in executor.py

## Task: T03.01

**Status**: PASS

## Diff

```diff
-# Threshold above which inline embedding falls back to --file flags
-_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB
+# Linux kernel compile-time constant (arch/arm64, x86_64, etc.)
+_MAX_ARG_STRLEN = 128 * 1024
+# 2.3x safety factor; measured template peak ~3.4 KB
+_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024
+# Derivation: MAX_ARG_STRLEN - PROMPT_TEMPLATE_OVERHEAD = 120 KB = 122,880 bytes
+_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD
```

## Verification

```
$ uv run python -c "from superclaude.cli.roadmap import executor; print('_MAX_ARG_STRLEN =', executor._MAX_ARG_STRLEN); print('_PROMPT_TEMPLATE_OVERHEAD =', executor._PROMPT_TEMPLATE_OVERHEAD); print('_EMBED_SIZE_LIMIT =', executor._EMBED_SIZE_LIMIT)"
_MAX_ARG_STRLEN = 131072
_PROMPT_TEMPLATE_OVERHEAD = 8192
_EMBED_SIZE_LIMIT = 122880
```

- `_MAX_ARG_STRLEN = 131072` = 128 × 1024 ✅
- `_PROMPT_TEMPLATE_OVERHEAD = 8192` = 8 × 1024 ✅
- `_EMBED_SIZE_LIMIT = 122880` = 120 × 1024 ✅
- No `import resource` statement ✅
- No stale `# 100 KB` comment remains ✅
