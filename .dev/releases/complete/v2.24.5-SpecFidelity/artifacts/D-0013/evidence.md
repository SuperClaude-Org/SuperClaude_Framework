# D-0013: Module-level overhead assertion in executor.py

## Task: T03.02

**Status**: PASS

## Code Added

```python
assert _PROMPT_TEMPLATE_OVERHEAD >= 4096, (
    "Kernel margin violated: _PROMPT_TEMPLATE_OVERHEAD must be >=4096 bytes "
    "to stay safely below MAX_ARG_STRLEN=128 KB; measured template peak ~3.4 KB"
)
```

## Placement

Immediately after the three constant definitions (lines 59-62 in executor.py).

## Verification

```
$ uv run python -c "from superclaude.cli.roadmap import executor"
(no output = assertion passes)
```

- Assertion fires on every `import executor` (module-level) ✅
- Error message states kernel margin rationale and measured template peak (~3.4 KB) ✅
- `_PROMPT_TEMPLATE_OVERHEAD = 8192 >= 4096` → assertion passes ✅
