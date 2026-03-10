---
title: "Variant A: Inline Prompt Embedding Is the Correct Architecture"
author: analysis-agent-alpha
scope: src/superclaude/cli/{pipeline,sprint,roadmap}/
analysis_type: architectural-decision
position: pro-inline
confidence: 0.85
---

# Position: Roadmap Executor Must Switch from --file to Inline Prompt Embedding

## 1. The Current Architecture Has a Behavioral Split

The SuperClaude CLI has two pipeline consumers that spawn `claude -p` subprocesses:

- **Sprint** (`src/superclaude/cli/sprint/`): Executes tasklist phases sequentially
- **Roadmap** (`src/superclaude/cli/roadmap/`): Executes an 8-step adversarial roadmap pipeline

Both inherit from a shared base (`src/superclaude/cli/pipeline/process.py:ClaudeProcess`) but use fundamentally different strategies to pass file content to the subprocess.

### Sprint: Inline via `@file` syntax

File: `src/superclaude/cli/sprint/process.py`, lines 47-89

```python
def build_prompt(self) -> str:
    phase_file = self.phase.file
    return (
        f"/sc:task-unified Execute all tasks in @{phase_file} "
        f"--compliance strict --strategy systematic\n"
        ...
    )
```

The `@{phase_file}` reference is embedded directly in the prompt string. Claude Code resolves it internally. No external flags, no env vars, no auth tokens.

### Roadmap: `--file` flags via `extra_args`

File: `src/superclaude/cli/roadmap/executor.py`, lines 103-117

```python
proc = ClaudeProcess(
    prompt=step.prompt,
    ...
    extra_args=[
        arg
        for input_path in step.inputs
        for arg in ("--file", str(input_path))
    ],
)
```

This appends `--file /absolute/path` to the subprocess argv. The base `ClaudeProcess.build_command()` in `pipeline/process.py:58-76` places these after `-p <prompt>`.

## 2. The `--file` Approach Is Broken in Practice

### 2a. Observed failure

Running `superclaude roadmap run spec.md` from a bare terminal produces 0-byte output files. The extract step fails with "File empty (0 bytes)" at the gate check.

### 2b. Root cause: `--file` semantics

The Claude CLI's `--file` flag expects `file_id:relative_path` format for remote file downloads — it is not a local filesystem path injector. Passing `--file /absolute/path/to/extraction.md` is semantically wrong. The flag silently fails or is ignored, meaning the subprocess receives the prompt text but none of the input file content.

### 2c. Session token dependency

Even if `--file` accepted local paths, it requires `CLAUDE_CODE_SESSION_ACCESS_TOKEN` — an env var that only exists inside an active Claude Code session. The `build_env()` method in `pipeline/process.py:78-87` copies `os.environ`, so it would pass this token through if it existed. But when running from a terminal, it does not exist.

### 2d. Sprint works everywhere

Sprint's `@file` inline syntax works because it is resolved by the Claude process itself after launch. There is no dependency on external auth tokens or env vars. Sprint has never exhibited this failure.

## 3. The Pipeline Layer Is Only Half-Adopted

### 3a. Sprint bypasses execute_pipeline()

`pipeline/executor.py` provides `execute_pipeline()` — a generic step sequencer with retry, gate checks, parallel dispatch, and cancellation. Roadmap uses it (`roadmap/executor.py:494`). Sprint does NOT — it has a completely independent 300-line orchestration loop in `sprint/executor.py:32-304`.

Evidence: Searching for `execute_pipeline` in `src/superclaude/cli/sprint/` returns zero matches.

### 3b. Sprint overrides process methods unnecessarily

`sprint/process.py:25` subclasses `pipeline/process.py:ClaudeProcess` but overrides `start()`, `wait()`, and `terminate()` with near-identical code. The only difference is sprint-specific `debug_log()` calls (4-6 extra lines per method). This is ~90 lines of duplication.

### 3c. Dead code in roadmap

`roadmap/executor.py:53-76` defines `_build_subprocess_argv()` which manually constructs a `claude` command list. This function is never called — the actual execution uses `ClaudeProcess` at line 103. It is dead code left from an earlier iteration.

## 4. The Inline Approach Is Superior

### 4a. Portability (weight: 3x)

Inline works from any terminal, any environment, any context. `--file` is broken today and requires a Claude Code session. This alone is decisive.

### 4b. Correctness (weight: 2x)

The `--file` flag is being used for a purpose it was not designed for. Inline with `<file path="...">` provenance headers in the prompt is semantically correct — it puts content where Claude expects to find it.

### 4c. Debuggability (weight: 2x)

With inline embedding, the full prompt (including all file content) is a single string. It can be logged, hashed for reproducibility, and replayed exactly. With `--file`, the prompt and inputs are split across different domains — you cannot reconstruct what the subprocess actually received.

### 4d. Atomic error handling (weight: 1x)

Inline embedding reads files in Python before subprocess launch. If a file is missing or unreadable, you get a Python exception with a clear traceback — before any subprocess is spawned. With `--file`, the failure happens inside the subprocess, producing silent 0-byte output.

### 4e. Scalability concern (weight: 1x)

The theoretical disadvantage of inline is ARG_MAX overflow. Linux ARG_MAX is ~2-3.2MB. The largest combined roadmap input (all variant files for the merge step) is ~60-100KB — 30x headroom. For the theoretical edge case, a stdin pipe fallback handles it.

### 4f. Shell safety is a non-concern

`subprocess.Popen` with a list argument (which `ClaudeProcess.build_command()` returns) already bypasses shell interpolation entirely. No escaping is needed regardless of approach.

## 5. Proposed Implementation

1. In the Python executor layer, read input files from `step.inputs` paths
2. Embed content in the prompt string with `<file path="relative/path">content</file>` provenance headers
3. Remove `extra_args` `--file` usage from `roadmap_run_step()`
4. Add a size guard: if combined prompt exceeds 2MB, pipe via subprocess stdin instead
5. Delete dead `_build_subprocess_argv()` from `roadmap/executor.py`

## 6. Weighted Scoring Summary

| Dimension | Weight | --file | Inline |
|---|---|---|---|
| Portability | 3x | 1 | 10 |
| Correctness | 2x | 2 | 9 |
| Debuggability | 2x | 3 | 8 |
| Scalability | 1x | 7 | 6 |
| Arch Cleanliness | 1x | 5 | 8 |
| **Weighted Total** | | **25/90** | **80/90** |
