# Refactoring Plan: B3 Full Mini-Executor

## Base Variant: B3 (Full mini-executor)

## Integrations from Other Variants

| Source | Integration | Risk | Rationale |
|--------|------------|------|-----------|
| B1 | Fallback path to ClaudeProcess for non-EXEMPT tasks | Low | Preserves generality. If task tier is not EXEMPT, use existing subprocess path. |
| B2 | Structured artifact template for evidence files | Low | B2's artifact format is good regardless of who classifies results. Adopt the template. |
| B1 | Raw output capture (stdout/stderr files alongside evidence.md) | Low | Debugging aid. Keep raw output even when writing structured evidence. |

---

## Implementation Plan

### File 1: `src/superclaude/cli/sprint/shell_runner.py` (NEW)

**Purpose**: Execute shell commands from EXEMPT-tier task steps, capture output, write evidence artifacts, determine pass/fail.

**Functions**:

```python
def run_exempt_task(task: TaskEntry, config: SprintConfig, phase: Phase) -> TaskResult:
    """Execute an EXEMPT-tier empirical task entirely in Python.

    1. Extract shell commands from task.description [EXECUTION] steps
    2. Run each command via subprocess.run()
    3. Capture stdout, stderr, exit_code
    4. Write evidence artifact to the deliverable path
    5. Classify result: exit_code == 0 AND stdout non-empty -> PASS
    6. Return fully-populated TaskResult
    """

def extract_shell_commands(description: str) -> list[str]:
    """Extract shell commands from [EXECUTION] step descriptions.

    Parses markdown task description for lines containing
    backtick-delimited commands after [EXECUTION] tags.
    Returns list of shell command strings.
    """

def write_evidence(
    artifact_path: Path,
    command: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    classification: str,
) -> None:
    """Write structured evidence.md artifact.

    Uses B2-style template:
    - Command executed
    - Exit code
    - Stdout (truncated to 500 lines)
    - Stderr (if non-empty)
    - Classification (WORKING/BROKEN/ERROR)
    - Timestamp
    """

def classify_result(exit_code: int, stdout: str, stderr: str) -> str:
    """Classify empirical task result.

    Rules (ordered):
    1. exit_code != 0 -> "BROKEN"
    2. stdout is empty -> "BROKEN"
    3. exit_code == 0 AND stdout non-empty -> "WORKING"

    Returns: "WORKING", "BROKEN", or "ERROR"
    """
```

**LoC estimate**: ~120-150

**Integration point**: Called from a new factory function that replaces `_run_task_subprocess()` for EXEMPT-tier tasks.

### File 2: Modification to `src/superclaude/cli/sprint/executor.py` (MODIFY)

**Changes**:

1. Add tier detection in `execute_phase_tasks()` or `_run_task_subprocess()`:

```python
def _run_task_subprocess(task, config, phase):
    # NEW: Route EXEMPT empirical tasks to shell_runner
    if _is_exempt_empirical(task):
        from .shell_runner import run_exempt_task
        result = run_exempt_task(task, config, phase)
        return (result.exit_code, result.turns_consumed, result.output_bytes)

    # EXISTING: ClaudeProcess path for all other tasks
    # ... existing code unchanged ...
```

2. Add helper function:

```python
def _is_exempt_empirical(task: TaskEntry) -> bool:
    """Check if task is EXEMPT tier with empirical shell commands.

    Detects tasks that:
    - Have 'Tier | EXEMPT' in description
    - Have [EXECUTION] steps containing backtick-delimited commands
    """
```

**LoC estimate**: ~30-40 added/modified

### File 3: `tests/sprint/test_shell_runner.py` (NEW)

**Test cases**:

```python
class TestExtractShellCommands:
    def test_extracts_single_command(self): ...
    def test_extracts_multiple_commands(self): ...
    def test_ignores_planning_steps(self): ...
    def test_handles_no_execution_steps(self): ...

class TestClassifyResult:
    def test_working_on_zero_exit_and_output(self): ...
    def test_broken_on_nonzero_exit(self): ...
    def test_broken_on_empty_stdout(self): ...
    def test_broken_on_exit_124_timeout(self): ...

class TestWriteEvidence:
    def test_writes_structured_markdown(self, tmp_path): ...
    def test_truncates_long_output(self, tmp_path): ...
    def test_includes_stderr_when_present(self, tmp_path): ...

class TestRunExemptTask:
    def test_end_to_end_passing_task(self, tmp_path): ...
    def test_end_to_end_failing_task(self, tmp_path): ...
    def test_fallback_when_no_commands_found(self): ...

class TestIsExemptEmpirical:
    def test_detects_exempt_tier(self): ...
    def test_rejects_standard_tier(self): ...
    def test_rejects_exempt_without_execution_steps(self): ...
```

**LoC estimate**: ~150-200

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Shell command extraction regex misses edge cases | Medium | Comprehensive test suite with real task descriptions from Phase 1 |
| Artifact path resolution differs from Claude's path resolution | Medium | Use same path resolution logic as existing `config.output_file()` pattern |
| EXEMPT tier detection false positive (runs non-empirical task in Python) | Low | Conservative detection: require BOTH Tier=EXEMPT AND [EXECUTION] backtick commands |
| Future task format changes break command extraction | Low | Fallback to ClaudeProcess if extraction yields zero commands |

---

## Execution Order

1. Implement `shell_runner.py` with `extract_shell_commands()`, `classify_result()`, `write_evidence()`, `run_exempt_task()`
2. Write unit tests for all functions
3. Add `_is_exempt_empirical()` and routing logic to `executor.py`
4. Integration test with a real Phase 1 task description
5. Run `uv run pytest tests/sprint/` to verify no regressions

---

## Rollback Plan

If B3 introduces regressions:
1. Remove the `_is_exempt_empirical()` check in `executor.py` (1-line change)
2. All tasks fall back to `ClaudeProcess` path
3. `shell_runner.py` becomes dead code, removable at leisure

The rollback is a single-line change because the routing logic is an `if/else` gate at the top of `_run_task_subprocess()`.
