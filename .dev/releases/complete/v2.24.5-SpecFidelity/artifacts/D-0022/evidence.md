# D-0022 Evidence — T05.03: Fix validate_executor.py:109 inline embedding

## Task

Replace `--file` fallback at `validate_executor.py:109` with inline embedding.
Conditional on Phase 1 result = BROKEN (confirmed).

## Change Description

**File**: `src/superclaude/cli/roadmap/validate_executor.py`

In `validate_run_step()`, the `elif embedded:` branch used `--file` flags as
fallback for oversized prompts. Since `--file` is broken, the branch now always
embeds inline, logging a warning if the composed prompt exceeds `_EMBED_SIZE_LIMIT`.

### Before (lines 104-110)

```python
elif embedded:
    effective_prompt = step.prompt
    extra_args = [
        arg
        for input_path in step.inputs
        for arg in ("--file", str(input_path))
    ]
```

### After

```python
if embedded:
    composed = step.prompt + "\n\n" + embedded
    if len(composed.encode("utf-8")) > _EMBED_SIZE_LIMIT:
        _log.warning(
            "validate_executor: composed prompt exceeds %d bytes;"
            " embedding inline anyway (--file fallback is unavailable)",
            _EMBED_SIZE_LIMIT,
        )
    effective_prompt = composed
    extra_args: list[str] = []
```

## Acceptance Criteria Verification

- [x] `--file` no longer used at `validate_executor.py:109`
- [x] Inline embedding delivers equivalent content to subprocess
- [x] No other `--file` usages remain in executable paths of `validate_executor.py`
- [x] Module docstring updated to reflect `--file` removal
- [x] Constant comment updated

## Verification

```
grep -n "\-\-file" src/superclaude/cli/roadmap/validate_executor.py
```
Result: Only in comments/docstrings (lines 11, 31, 100, 108) — no executable usage.
