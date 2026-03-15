# D-0023 Evidence — T05.04: Fix tasklist/executor.py:121 inline embedding

## Task

Replace `--file` fallback at `tasklist/executor.py:121` with inline embedding.
Conditional on Phase 1 result = BROKEN (confirmed).

## Change Description

**File**: `src/superclaude/cli/tasklist/executor.py`

In the step execution function, the `elif embedded:` branch used `--file` flags
as fallback. Since `--file` is broken, the branch now always embeds inline,
logging a warning if the composed prompt exceeds `_EMBED_SIZE_LIMIT`.

### Before (lines 116-122)

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
            "tasklist executor: composed prompt exceeds %d bytes;"
            " embedding inline anyway (--file fallback is unavailable)",
            _EMBED_SIZE_LIMIT,
        )
    effective_prompt = composed
    extra_args: list[str] = []
```

## Acceptance Criteria Verification

- [x] `--file` no longer used at `tasklist/executor.py:121`
- [x] Inline embedding delivers equivalent content to subprocess
- [x] No other `--file` usages remain in executable paths of `tasklist/executor.py`
- [x] Module docstring updated to reflect `--file` removal
- [x] Constant comment updated

## Verification

```
grep -n "\-\-file" src/superclaude/cli/tasklist/executor.py
```
Result: Only in comments/docstrings (lines 10, 33, 112, 120) — no executable usage.
