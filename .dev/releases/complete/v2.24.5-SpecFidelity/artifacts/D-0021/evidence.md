# D-0021 Evidence — T05.02: Fix remediate_executor.py:177 inline embedding

## Task

Replace unconditional `--file` usage at `remediate_executor.py:177` with inline
embedding. Conditional on Phase 1 result = BROKEN (confirmed).

## Change Description

**File**: `src/superclaude/cli/roadmap/remediate_executor.py`

In `_run_agent_for_file()`, `extra_args=["--file", target_file]` was the only
mechanism to deliver the target file content to the remediation agent. Since
`--file` is broken, the fix reads the file content and embeds it inline in the
prompt, prepended as a fenced code block.

### Added constants

```python
_MAX_ARG_STRLEN = 128 * 1024
_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024
_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD
```

### Before (line 177)

```python
extra_args=["--file", target_file],
```

### After

```python
# Inline embedding: read target file content into the prompt.
# --file is broken (cloud download mechanism, not local file injector).
try:
    file_content = Path(target_file).read_text(encoding="utf-8")
    file_block = f"## Current File Content\n\n```\n{file_content}\n```"
    composed = base_prompt + "\n\n" + file_block
    if len(composed.encode("utf-8")) > _EMBED_SIZE_LIMIT:
        _log.warning(...)
    prompt = composed
except OSError as exc:
    _log.warning(...)
    prompt = base_prompt
# extra_args=["--file", target_file] removed entirely
```

## Acceptance Criteria Verification

- [x] `--file` no longer used at `remediate_executor.py:177`
- [x] Inline embedding delivers equivalent content to subprocess (file content embedded in prompt)
- [x] No other `--file` usages remain in `remediate_executor.py`
- [x] `extra_args` parameter removed from `ClaudeProcess(...)` call

## Verification

```
grep -n "\-\-file" src/superclaude/cli/roadmap/remediate_executor.py
```
Result: Only in comments (lines 39, 172, 180) explaining WHY the change was made.
No executable `--file` usage remains.
