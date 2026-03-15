# D-0007 — Add `--tools default` to `build_command()`

**Task:** T02.02
**Date:** 2026-03-15
**Status:** PASS

## Change Applied

**File:** `src/superclaude/cli/pipeline/process.py`

### Diff

```diff
         "--no-session-persistence",
+        "--tools",
+        "default",
         "--max-turns",
```

### Post-Edit State (lines 69-89)

```python
def build_command(self) -> list[str]:
    """Build the claude CLI command."""
    cmd = [
        "claude",
        "--print",
        "--verbose",
        self.permission_flag,
        "--no-session-persistence",
        "--tools",
        "default",
        "--max-turns",
        str(self.max_turns),
        "--output-format",
        self.output_format,
        "-p",
        self.prompt,
    ]
    if self.model:
        cmd.extend(["--model", self.model])
    cmd.extend(self.extra_args)
    return cmd
```

## Acceptance Criteria — All Met

- [x] `"--tools"` and `"default"` appear as adjacent elements (lines 77-78)
- [x] Insertion is after `"--no-session-persistence"` and before `"--max-turns"`
- [x] Legacy flags (`--print`, `--no-session-persistence`, `--max-turns`) remain present and correctly ordered
- [x] `extra_args` ordering preserved (still appended after `--model` conditional)
- [x] Conditional `--model` behavior preserved (lines 86-87)

## Subclass Impact

Both subclasses (`sprint/process.py:ClaudeProcess`, `cleanup_audit/process.py:CleanupAuditProcess`)
do NOT override `build_command()`, so this change propagates to both automatically (confirmed in D-0006).
