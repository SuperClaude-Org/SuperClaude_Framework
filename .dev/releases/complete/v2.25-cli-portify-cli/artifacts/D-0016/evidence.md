---
deliverable: D-0016
task: T03.05
title: Claude Binary Detection
status: PASS
---

# D-0016: Claude Binary Detection

## Implementation

`src/superclaude/cli/cli_portify/process.py` — `detect_claude_binary()`

## Logic

```python
def detect_claude_binary() -> str:
    binary = shutil.which("claude")
    if binary is None:
        raise RuntimeError(
            "claude CLI binary not found in PATH.\n"
            "Install Claude Code: https://claude.ai/code\n"
            "After installation, ensure 'claude' is on your PATH."
        )
    return binary
```

Uses `shutil.which("claude")` — the standard Python approach for binary detection on both POSIX and Windows. The error message includes installation guidance (FR-036, AC-008).

## Usage

Must be called in pipeline initialization before any Claude-assisted steps.

## Validation

`uv run pytest tests/ -k "test_claude_binary"` → 5 passed
