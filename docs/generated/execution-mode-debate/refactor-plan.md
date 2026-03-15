# Refactoring Plan -- execution_mode Annotation Implementation

## Selected Value Set

```python
class ExecutionMode(str, Enum):
    CLAUDE = "claude"   # Default. Phase executed via Claude subprocess.
    PYTHON = "python"   # Shell commands extracted and run via subprocess.run().
    SKIP = "skip"       # Phase not executed. Used for conditional deactivation.
```

## Integration Points

### 1. Tasklist Format (Markdown Annotation)

**Location**: Phase header metadata tables in `phase-N-tasklist.md` files.

**Format**: Add `execution_mode` row to the phase-level metadata block.

```markdown
# Phase 1 -- Empirical Validation Gate

| Field | Value |
|---|---|
| execution_mode | python |
```

When absent, `execution_mode` defaults to `claude` (backward compatible).

**Risk**: LOW -- additive change to markdown format; existing tasklists work unchanged.

### 2. Tasklist Parser

**Location**: `src/superclaude/cli/sprint/` (tasklist parsing module).

**Change**: Add `execution_mode` field extraction from phase metadata tables. Parse the value, validate against `ExecutionMode` enum, default to `CLAUDE` if absent.

**Risk**: LOW -- parser extension, no existing behavior changes.

### 3. Sprint Models

**Location**: `src/superclaude/cli/sprint/models.py`

**Changes**:
- Add `ExecutionMode` enum (3 values).
- Add `execution_mode: ExecutionMode = ExecutionMode.CLAUDE` field to `PhaseResult` or equivalent phase-tracking dataclass.
- Add `execution_mode` to `TaskEntry` if per-task mode is desired (deferred -- phase-level only for now).

**Risk**: LOW -- additive dataclass fields with defaults.

### 4. Sprint Executor Dispatch

**Location**: `src/superclaude/cli/sprint/executor.py`

**Changes**: In the phase execution loop, dispatch based on `execution_mode`:

```python
if phase.execution_mode == ExecutionMode.SKIP:
    # Return immediately with SKIPPED status
    return PhaseResult(status=PhaseStatus.SKIPPED, ...)

elif phase.execution_mode == ExecutionMode.PYTHON:
    # Extract shell commands from task steps
    # Run each via subprocess.run()
    # Capture stdout/stderr/exit_code
    # Write evidence artifacts
    return _execute_python_phase(phase, config)

else:  # ExecutionMode.CLAUDE (default)
    # Current behavior unchanged
    return _execute_claude_phase(phase, config)
```

**Risk**: MEDIUM -- new execution path (`_execute_python_phase`) requires testing.

### 5. Python Phase Executor (New)

**Location**: New function `_execute_python_phase()` in `src/superclaude/cli/sprint/executor.py` (or new module `python_executor.py`).

**Responsibilities**:
1. Parse task step markdown for shell command blocks (fenced code blocks with `bash` or `sh` language tag, or lines starting with `$`).
2. For each command: run via `subprocess.run(cmd, shell=True, capture_output=True, timeout=...)`.
3. Capture stdout, stderr, exit code.
4. Write output to the task's evidence artifact path.
5. Return `TaskResult` with pass/fail based on exit code.

**Shell Command Extraction Rules**:
- Lines within `**Steps:**` section that contain backtick-quoted commands.
- Fenced code blocks with `bash`/`sh`/`shell` language hints.
- Lines matching pattern: `Run \`<command>\``

**Risk**: MEDIUM -- markdown parsing for commands is inherently fragile. Mitigate by requiring explicit `[SHELL]` step tags or a dedicated `commands:` metadata field.

**Recommendation**: Rather than parsing commands from prose, add a `commands` list to the phase metadata:

```markdown
| Field | Value |
|---|---|
| execution_mode | python |
| commands | claude --print -p "hello" --max-turns 1; claude --help \| grep -A5 file |
```

Or use a fenced code block under a `## Commands` section. This is more reliable than extracting commands from step descriptions.

### 6. Evidence Artifact Writer

**Location**: Within `_execute_python_phase()`.

**Format**: Write `evidence.md` with:
```markdown
# Evidence: T01.01 -- CLI Availability

## Command
\`\`\`bash
claude --print -p "hello" --max-turns 1
\`\`\`

## Exit Code
0

## Stdout
\`\`\`
Hello! How can I help you today?
\`\`\`

## Stderr
(empty)

## Result
PASS
```

**Risk**: LOW -- straightforward file writing.

## Implementation Order

| Step | What | Depends On | Effort | Risk |
|---|---|---|---|---|
| 1 | Add `ExecutionMode` enum to models.py | Nothing | XS | Low |
| 2 | Add `execution_mode` parsing to tasklist parser | Step 1 | S | Low |
| 3 | Add dispatch logic to executor.py | Steps 1, 2 | S | Low |
| 4 | Implement `skip` path (trivial) | Step 3 | XS | Low |
| 5 | Implement `_execute_python_phase()` | Step 3 | M | Medium |
| 6 | Add evidence artifact writing | Step 5 | S | Low |
| 7 | Add tests for all three modes | Steps 4, 5, 6 | M | Low |
| 8 | Update v2.24.5 Phase 1 tasklist with annotation | Step 2 | XS | Low |

**Total estimated effort**: M (Medium) -- approximately 150-200 LOC of new code plus tests.

## Future Evolution Path

When machine-readable gating is needed (second gating use case emerges):

1. Add `condition` field to phase metadata: `condition: phase-1.result == BROKEN`
2. Add condition evaluator to the sprint runner (reads prior phase results, evaluates boolean expressions).
3. `skip` becomes the runtime result of a failed condition, rather than a static annotation.
4. `python-gate` is NOT added -- the combination of `execution_mode: python` + `condition` on downstream phases achieves the same result with better separation of concerns.

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Shell command extraction from markdown is fragile | Medium | Medium | Use explicit `commands` metadata field instead of prose parsing |
| Python executor subprocess.run() hangs | Low | High | Set timeout parameter; inherit from phase timeout_seconds |
| Backward incompatibility with existing tasklists | Very Low | Medium | Default to `claude` when annotation absent |
| Security risk from shell=True | Low | Medium | Only run commands from trusted tasklist files (same trust model as Claude execution) |
