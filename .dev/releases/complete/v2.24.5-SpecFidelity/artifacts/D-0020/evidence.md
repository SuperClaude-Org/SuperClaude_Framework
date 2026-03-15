# D-0020 Evidence — T05.01: Fix executor.py fallback path

## Task

Replace `--file` fallback path in `src/superclaude/cli/roadmap/executor.py` with
inline `-p` embedding. Conditional on Phase 1 result = BROKEN (confirmed).

## Change Description

**File**: `src/superclaude/cli/roadmap/executor.py`

In `roadmap_run_step()`, the oversized-prompt branch previously fell back to
`--file` flags. Since `--file` is a cloud download mechanism (Phase 1 confirmed
BROKEN), this branch was replaced with unconditional inline embedding.

### Before

```python
if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = step.prompt + "\n\n" + embedded
    extra_args: list[str] = []
elif embedded:
    _log.warning(
        "Step '%s': embedded inputs exceed %d bytes, falling back to --file flags",
        step.id,
        _EMBED_SIZE_LIMIT,
    )
    effective_prompt = step.prompt
    extra_args = [
        arg
        for input_path in step.inputs
        for arg in ("--file", str(input_path))
    ]
else:
    effective_prompt = step.prompt
    extra_args = []
```

### After

```python
# --file is broken (cloud download mechanism, not local file injector) so
# inline embedding is always used regardless of composed prompt size.
embedded = _embed_inputs(step.inputs)
if embedded:
    composed = step.prompt + "\n\n" + embedded
    if len(composed.encode("utf-8")) > _EMBED_SIZE_LIMIT:
        # <= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB
        _log.warning(
            "Step '%s': composed prompt exceeds %d bytes; embedding inline anyway"
            " (--file fallback is unavailable)",
            step.id,
            _EMBED_SIZE_LIMIT,
        )
    effective_prompt = composed
    extra_args: list[str] = []
else:
    effective_prompt = step.prompt
    extra_args = []
```

## Acceptance Criteria Verification

- [x] `--file` no longer appears in the fallback path of `executor.py`
- [x] Inline `-p` embedding delivers equivalent content to the subprocess
- [x] Fallback behavior (oversized prompt) now warns and embeds inline rather than using `--file`
- [x] Module docstring updated to remove `--file` reference

## Verification

```
grep -n "\-\-file" src/superclaude/cli/roadmap/executor.py
```
Result: Only appears in module docstring comment (line 7, removed reference)
and old comment line 181 (explaining the fix) — no longer in executable code path.

All `extra_args` in the embedded branch are set to `[]` — no `--file` flags passed.
