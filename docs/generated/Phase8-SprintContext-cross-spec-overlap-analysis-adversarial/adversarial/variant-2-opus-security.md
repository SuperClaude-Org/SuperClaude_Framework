# Variant 2: Security Fault-Finding -- Cross-Spec Overlap Analysis

## Executive Summary

The cross-spec overlap analysis contains three material risk underestimates. First, the dismissal of SOL-D as "redundant" ignores a real crash window between subprocess exit and executor result-file write where multiple exception-throwing operations occur (lines 638-647 of executor.py). Second, the `PASS_RECOVERED` enum value creates a silent failure path in both the TUI and the logger, which use exhaustive dict lookups against `PhaseStatus` values and will crash with `KeyError` on any unregistered status. Third, the proposed `detect_prompt_too_long()` function suffers from a TOCTOU race: the output file may still be receiving writes from the monitor thread's buffered I/O when the main thread reads it after subprocess exit.

---

## Fault 1: SOL-D Discard Gap Analysis

### Claim Under Challenge

The analysis (OV-4) states: "Spec A's dead-man's switch only covers the case where the *subprocess* crashes before writing the result file. But S1 makes the *executor* write it from its own data, so subprocess crashes don't matter -- the executor always has `AggregatedPhaseReport`."

The analysis then recommends **discarding SOL-D entirely** in favor of S1 (executor writes result file between lines 643 and 658).

### Code Path Trace: Subprocess Exit to Result File Write

The proposed S1 insertion point is between lines 643 and 658 of `executor.py`. Let me trace every operation that executes in this window:

**Line 633**: `raw_rc = proc_manager._process.returncode` -- attribute access, safe.

**Line 634-637**: Conditional assignment of `exit_code` based on `_timed_out` flag -- pure logic, safe.

**Line 638**: `monitor.stop()` -- Calls `OutputMonitor.stop()` (monitor.py:129-133). This calls `self._stop_event.set()` and then `self._thread.join(timeout=2.0)`. The `join()` call **can raise** `RuntimeError` if the thread has not been started (monitor.py line 133). More critically, during the 2.0-second join window, the monitor's `_poll_loop` may still be executing its final `_poll_once()` cycle, which reads and writes to the output file.

**Line 639**: `finished_at = datetime.now(timezone.utc)` -- safe.

**Line 640**: `_phase_dur = (finished_at - started_at).total_seconds()` -- safe.

**Lines 641-647**: `debug_log(...)` -- This calls `logging.getLogger(_DBG_NAME)` methods. The `debug_log` function in `debug_logger.py` may perform file I/O to `config.debug_log_path`. If the debug log file is on a full filesystem, this **can raise** `OSError`. Additionally, if the logging module's handler is misconfigured, it can raise various exceptions.

**Lines 649-656**: Shutdown check -- branches on `signal_handler.shutdown_requested`. If True, calls `logger.write_phase_interrupt()` which performs file I/O (JSONL write at logging_.py:162-164). This **can raise** `OSError` on disk full or permissions error.

**[PROPOSED S1 INSERTION POINT]**: `report = aggregate_task_results(...)` followed by `config.result_file(phase).write_text(report.to_markdown())`.

**Lines 658-663**: `_determine_phase_status(...)` -- reads the result file that S1 just wrote.

### Failure Surface Analysis

The analysis dismisses the crash window as "vanishingly unlikely." Here is the actual failure surface:

1. **`monitor.stop()` at line 638**: If the monitor thread's final `_poll_once()` raises an unhandled exception in the thread itself, `join()` returns without error but the thread state may be corrupt. This is benign for the crash window. However, if the monitor was never started (e.g., `output_path` was invalid), `_thread` may be `None`, and `stop()` references `self._thread.join()` -- this is guarded by `if self._thread:` at monitor.py:132, so safe.

2. **`debug_log()` at lines 641-647**: The `debug_log` function signature (from debug_logger.py) uses `_dbg.debug()` which routes through Python's logging framework. If the file handler has been closed (e.g., by a prior exception in the finally block of a nested context), this can raise `ValueError("I/O operation on closed file")`. However, looking at the actual execution flow, this is within the main try block, so an exception here would propagate to the `finally` block at line 733, which does cleanup but **does not write the result file**.

3. **Signal handler interrupt at line 653**: If `signal_handler.shutdown_requested` is True, the code breaks at line 656 **before reaching the proposed S1 insertion point**. This means: on SIGINT/SIGTERM between subprocess exit and result-file write, the executor will skip writing the result file entirely. The sprint is marked INTERRUPTED (line 655), so this is arguably acceptable behavior -- but the analysis never mentions this path.

4. **The proposed S1 insertion itself**: `aggregate_task_results()` (lines 285-330) performs pure computation on `task_results` and `remaining` variables. But `config.result_file(phase).write_text(report.to_markdown())` performs disk I/O. On a full filesystem, this raises `OSError`. If this exception is not caught, it propagates to the `finally` block, and `_determine_phase_status` never runs. The sprint effectively crashes mid-execution with no recovery.

### Verdict on "Vanishingly Unlikely"

The analysis is **partially correct** that the window is narrow. However, it fails to account for:

- **The S1 write itself is an unprotected I/O operation** that can fail. The analysis assumes S1 will always succeed, which is the same class of assumption that made the agent-written result file unreliable. SOL-D's `tempfile + os.replace` approach at least handles `OSError` gracefully (logs warning, continues). The proposed S1 has no error handling specified.
- **The signal handler path** (lines 653-656) can cause the S1 write to be skipped entirely, leaving no result file when the sprint is resumed later.
- **The failure surface is not "vanishingly unlikely"** -- it is "unlikely under normal operation but certain under adversarial conditions" (disk full, SIGINT, logging errors). For a system that runs multi-hour sprints costing $25+, this is a material risk.

### Corrected Recommendation

SOL-D should not be discarded wholesale. The executor-written result file (S1) should be the primary mechanism, but it must be wrapped in `try/except OSError` with a fallback. SOL-D's pre-write provides defense-in-depth for the case where S1 fails. The timestamp incompatibility (C-1) is real but can be resolved by capturing `started_at` **before** the SOL-D pre-write, or by having `_determine_phase_status` treat pre-written files (containing the sentinel `# Pre-written by executor`) differently from executor-written files.

---

## Fault 2: Recovery Chain Race Conditions

### Race Condition: Output File Still Growing When `detect_prompt_too_long()` Reads It

The proposed `detect_prompt_too_long()` function (S2-R01/R02) reads the output file to scan for `"Prompt is too long"` in the last 10 lines. This function would be called from `_determine_phase_status()` at line 783 (proposed), which executes **after** `monitor.stop()` at line 638.

However, `monitor.stop()` calls `self._thread.join(timeout=2.0)` (monitor.py:132-133). The timeout is 2.0 seconds. If the monitor thread does not terminate within 2.0 seconds, `join()` returns anyway and the thread continues running in the background. The monitor's `_poll_once()` method (monitor.py:148-175) reads the output file and updates `self._last_read_pos`. This creates a race:

1. Main thread calls `monitor.stop()` at executor.py:638.
2. Monitor thread is in the middle of `_poll_once()` -- specifically in `_read_new_chunk()` (monitor.py:185-194) which has an open file handle.
3. `join(timeout=2.0)` returns (either thread finished or timed out).
4. Main thread proceeds to proposed `_determine_phase_status()` which calls `detect_prompt_too_long()`.
5. `detect_prompt_too_long()` calls `output_path.read_text()` (following the pattern from `detect_error_max_turns()` at monitor.py:44-45).
6. If the monitor thread timed out on join and is still running, both threads are now reading the same file. This is safe on Linux (concurrent reads are fine).

**But there is a subtler issue**: The subprocess (`claude`) writes to the output file. When the subprocess exits (poll returns non-None at line 557), there may be **buffered data** in the OS pipe/file that has not been flushed to disk yet. The output file is opened by `ClaudeProcess` as a file descriptor that the subprocess writes to. On process exit, the OS flushes pipe buffers, but this happens asynchronously. The `"Prompt is too long"` error message may be one of the **last** things written to the output file. If `detect_prompt_too_long()` reads the file before the OS has flushed the final subprocess output, it will miss the pattern.

This is a genuine TOCTOU vulnerability. The `detect_error_max_turns()` function has the same vulnerability but is only called in the `exit_code == 0` path (executor.py:811), where the subprocess exited cleanly and presumably had time to flush. In the `exit_code != 0` path (where context exhaustion occurs), the subprocess may have been killed or crashed, making incomplete flush more likely.

### Exception Path in `_classify_from_result_file()`

The proposed `_classify_from_result_file()` helper (S2-R05) reads the result file and classifies the phase. If this function throws an exception (e.g., the result file is a broken symlink, or `read_text()` raises `UnicodeDecodeError` despite `errors="replace"`), the exception would propagate up through `_determine_phase_status()`. Since `_determine_phase_status()` is called at line 659, an unhandled exception would propagate to the `finally` block at line 733.

The current `_determine_phase_status()` function (lines 765-815) already handles this gracefully for the `exit_code == 0` path: `result_file.read_text(errors="replace")` at line 787 catches encoding issues. But neither the analysis nor the specs mention wrapping the recovery chain in exception handling. If Path 1 (context exhaustion detection) partially succeeds but Path 1's `_classify_from_result_file` throws, Path 2 (checkpoint inference) never executes.

The correct pattern would be:

```python
if exit_code != 0:
    try:
        if detect_prompt_too_long(output_file):
            return _classify_from_result_file(result_file, started_at=started_at, recovered=True)
    except Exception:
        pass  # Fall through to checkpoint inference

    try:
        if config is not None and phase is not None:
            if _check_checkpoint_pass(config, phase):
                contaminated = _check_contamination(config, phase)
                _write_crash_recovery_log(config, phase, contaminated)
                if not contaminated:
                    return PhaseStatus.PASS_RECOVERED
    except Exception:
        pass  # Fall through to ERROR

    return PhaseStatus.ERROR
```

The analysis does not specify this defensive wrapping.

### Partial Checkpoint File Reads

The proposed `_check_checkpoint_pass()` (Spec A, Step 3.2) reads `checkpoints/CP-P{N:02d}-END.md` and checks for `"STATUS: PASS"`. Checkpoint files are written by the agent subprocess. If the subprocess crashed mid-write (the exact scenario SOL-C targets), the checkpoint file may be truncated. Consider:

```
## Phase 8 Completion Checkpoint
**STATUS: PA
```

The `.upper()` check `"STATUS: PASS" in content` would return `False` on this truncated content, which is the correct (safe) behavior -- a partial checkpoint should not be trusted. This specific case is handled correctly.

However, the alternative pattern `"**RESULT**: PASS"` (Step 3.2 code) uses a bold markdown format that is more likely to be partially written:

```
**RESULT**: P
```

This also returns `False`, which is correct. Both patterns fail safe. No fault here.

---

## Fault 3: PASS_RECOVERED Specificity Loss

### TUI: Hard `KeyError` on Unknown PhaseStatus

The TUI (tui.py) uses two dictionary lookups that enumerate every `PhaseStatus` value:

**`STATUS_STYLES` (tui.py:28-39)**:
```python
STATUS_STYLES = {
    PhaseStatus.PASS: "bold green",
    PhaseStatus.PASS_NO_SIGNAL: "green",
    PhaseStatus.PASS_NO_REPORT: "green",
    PhaseStatus.INCOMPLETE: "bold red",
    PhaseStatus.HALT: "bold red",
    PhaseStatus.TIMEOUT: "bold red",
    PhaseStatus.ERROR: "bold red",
    PhaseStatus.RUNNING: "bold yellow",
    PhaseStatus.PENDING: "dim",
    PhaseStatus.SKIPPED: "dim strikethrough",
}
```

**`STATUS_ICONS` (tui.py:41-52)**: Same exhaustive enumeration.

At tui.py:174, the code performs:
```python
style = STATUS_STYLES[status]
```

And at tui.py:189:
```python
STATUS_ICONS.get(status, str(status.value))
```

The `STATUS_STYLES` access at line 174 is a **raw dict subscript**, not `.get()`. If `status` is `PhaseStatus.PASS_RECOVERED`, this raises `KeyError`. The `STATUS_ICONS` access at line 189 uses `.get()` with a fallback, so it is safe.

The `KeyError` at line 174 would be caught by the `try/except` wrapper at tui.py:104-117:
```python
try:
    self._live.update(self._render())
except Exception as exc:
    self._live_failed = True
```

This sets `_live_failed = True`, which **permanently disables the TUI** for the remainder of the sprint. The sprint continues (the TUI error does not abort execution), but the operator loses all visual feedback. For a multi-hour sprint costing $25+, losing the TUI dashboard is a significant operational impact.

**The analysis rates this risk as "Medium"** in the Risk Assessment table (line 508): "Verify [`SprintTUI.update()`] and [`SprintLogger.write_phase_result()`] handle unknown `PhaseStatus` values gracefully before adding the new status." This is correct that verification is needed, but it understates the consequence: it is not "unknown values handled gracefully" -- it is a guaranteed `KeyError` that permanently kills the TUI.

### Logger: Silent Drop of PASS_RECOVERED Events

The logger (logging_.py:88-140) routes screen output based on specific `PhaseStatus` values:

```python
# logging_.py:126-140
if result.status == PhaseStatus.ERROR:
    self._screen_error(...)
elif result.status in (PhaseStatus.HALT, PhaseStatus.TIMEOUT):
    self._screen_warn(...)
elif result.status in (PhaseStatus.PASS, PhaseStatus.PASS_NO_REPORT):
    self._screen_info(...)
```

A `PASS_RECOVERED` status matches **none** of these conditions. It would:
1. Still be written to JSONL (line 91-106) -- correct.
2. Still be written to Markdown (line 109-119), since it is not `PASS_NO_SIGNAL` -- correct.
3. **Not** produce any screen output -- the operator sees nothing on the console when a phase recovers from context exhaustion.

This is a silent failure mode. The operator has no indication that context exhaustion occurred and recovery was attempted. For a diagnostic status specifically designed to provide "diagnostic visibility" (analysis line 504), producing zero screen output is a critical gap.

### Diagnostic Specificity: Is Single PASS_RECOVERED Acceptable?

The analysis claims (line 504): "`FailureCategory` at `diagnostics.py:19` carries root cause specificity. Execution log entry distinguishes the trigger."

However, the diagnostics system (diagnostics.py:145-194) only runs when `status.is_failure` is True (executor.py:698). Since `PASS_RECOVERED` has `is_success=True` and `is_failure=False`, the `DiagnosticCollector`, `FailureClassifier`, and `ReportGenerator` are **never invoked** for recovered phases. The `FailureCategory.CONTEXT_EXHAUSTION` value (S2-R07) would never be assigned to a `PASS_RECOVERED` phase.

The only place root cause specificity would be recorded is in the execution log, and only if the `_classify_from_result_file` or `_check_checkpoint_pass` helper explicitly logs the recovery type. Neither the analysis nor the specs specify this logging. The proposed merged code (analysis lines 208-223) shows early returns with no logging call between the detection and the return.

**Corrected Assessment**: Losing diagnostic specificity between checkpoint-inference recovery and context-exhaustion recovery is not "Low" risk. Without explicit logging at the recovery point, there is **no mechanism** to distinguish recovery types post-hoc. The `FailureCategory` system cannot help because it does not run for success statuses.

---

## Fault 4: Timestamp Conflict Verification

### SOL-D Pre-Write Timing vs `started_at` Capture

The analysis (C-1) claims timestamp incompatibility between SOL-D and S2-R06. Let me verify:

- **SOL-D pre-write**: Spec A Step 1.3 says "immediately before the subprocess is launched (before `ClaudeProcess` is started)." Looking at executor.py, this would be before line 541 (`proc_manager = ClaudeProcess(config, phase)`).
- **`started_at` capture**: Line 543: `started_at = datetime.now(timezone.utc)`. This is a `datetime` object, not a float.
- **S2-R06 mtime check**: The PRD says "Validate result file `mtime > phase_started_at`." The analysis proposes `started_at: float = 0.0` in the signature (line 247) and `started_at=started_at.timestamp()` at the call site (line 259), converting `datetime` to epoch float.

**Timing sequence under SOL-D + S2**:
1. T0: SOL-D pre-writes result file. File gets `mtime = T0` (epoch float).
2. T1: `started_at = datetime.now(timezone.utc)` at line 543. `started_at.timestamp()` gives epoch float T1.
3. Subprocess runs for N minutes.
4. S2-R06 checks: `result_file.stat().st_mtime > started_at.timestamp()` i.e. `T0 > T1`.

Since T0 < T1 (the pre-write happens before `started_at` is captured), the check `T0 > T1` is **always False**. The pre-written file would always be rejected as stale. The analysis is **correct** about this incompatibility.

### Clock Resolution Concern

On Linux, `datetime.now(timezone.utc)` and `os.stat().st_mtime` both use `clock_gettime(CLOCK_REALTIME)` with nanosecond resolution (though Python's float representation limits to microseconds). The gap between T0 and T1 includes the `ClaudeProcess.__init__()` call (line 541), which performs string formatting in `build_prompt()` (process.py:115-157). This takes microseconds to milliseconds. The clock resolution is far finer than this gap, so T0 < T1 always holds. The analysis is correct.

### However: What If SOL-D Is Retained as Defense-in-Depth?

If SOL-D pre-write is retained (contrary to the analysis's recommendation), the timestamp check needs modification. The simplest fix: capture `started_at` **before** the pre-write, not after. Or: have `_classify_from_result_file` check for the sentinel string `# Pre-written by executor` and reject such files regardless of mtime.

---

## Fault 5: Unhandled `aggregate_task_results` Dependency on Per-Task Execution

### The `task_results` Variable Availability Problem

The analysis (Step 2) says: "call `aggregate_task_results()` (already exists at line 285), write `report.to_markdown()` to `config.result_file(phase)`." It also notes: "The `task_results` and `remaining` variables are available from the earlier call to `execute_phase_tasks()` at lines 348-445."

But examining the actual `execute_sprint()` function (lines 490-762), **there is no call to `execute_phase_tasks()` in `execute_sprint()`**. The phase execution model in `execute_sprint()` is a single-subprocess-per-phase model (line 541: `proc_manager = ClaudeProcess(config, phase)`), not a per-task subprocess model.

`execute_phase_tasks()` (lines 349-446) is a separate function that implements the per-task subprocess loop. It is not called from `execute_sprint()`. The `execute_sprint()` function launches one Claude subprocess per phase and monitors it, but does not parse individual task results.

This means **`task_results` and `remaining` do not exist** in the scope of `execute_sprint()` at the proposed insertion point (between lines 643 and 658). The proposed S1 implementation:

```python
report = aggregate_task_results(phase.number, task_results, remaining)
config.result_file(phase).write_text(report.to_markdown())
```

would raise `NameError: name 'task_results' is not defined`.

The analysis fundamentally misunderstands the execution architecture. `execute_sprint()` does not produce `TaskResult` objects -- it produces `PhaseResult` objects. The `AggregatedPhaseReport` class and `aggregate_task_results()` function exist for the per-task model, not the per-phase model.

To make S1 work in the per-phase model, the executor would need to either:
1. Parse task results from the subprocess output (which defeats the purpose of not relying on agent output), or
2. Construct a synthetic `AggregatedPhaseReport` from the phase-level data available (exit code, output bytes, etc.), which would lack per-task granularity.

**This is the most critical fault in the entire analysis.** The recommended "~5 lines" of code cannot work as specified because the required data structures do not exist at the insertion point. The analysis appears to have conflated two different execution models.

---

## Fault 6: FailureClassifier Does Not Handle PASS_RECOVERED Path

The `FailureClassifier.classify()` method (diagnostics.py:148-194) is invoked at executor.py:703 only when `status.is_failure` is True (line 698):

```python
if status.is_failure:
    # Collect diagnostics for the failed phase
    collector = DiagnosticCollector(config)
    bundle = collector.collect(phase, phase_result, monitor.state)
    classifier = FailureClassifier()
    bundle.category = classifier.classify(bundle)
```

Since `PASS_RECOVERED.is_failure` returns `False`, the diagnostic collection is entirely bypassed. The proposed `FailureCategory.CONTEXT_EXHAUSTION` value (S2-R07) can only be assigned by the `FailureClassifier`, which never runs for recovered phases.

The analysis mentions adding `CONTEXT_EXHAUSTION` to diagnostics (Step 8) and updating `FailureClassifier` to detect it. But the classifier only runs on failures. For the context-exhaustion-then-recovery scenario (the primary use case), the classifier is never invoked. The `CONTEXT_EXHAUSTION` category would only apply to context exhaustion events where recovery **fails** (result file says HALT or is missing), which is the minority case.

This means the primary diagnostic benefit advertised by both specs -- distinguishing context exhaustion from generic crashes -- is **not achieved** for the success case. The operator sees `PASS_RECOVERED` with no indication of what triggered the recovery.

---

## Fault 7: `detect_error_max_turns` Path Inconsistency

The existing `detect_error_max_turns()` function is called at executor.py:811, but only in the `exit_code == 0` path:

```python
if output_file.exists() and output_file.stat().st_size > 0:
    if detect_error_max_turns(output_file):
        return PhaseStatus.INCOMPLETE
    return PhaseStatus.PASS_NO_REPORT
```

The proposed `detect_prompt_too_long()` function would be called in the `exit_code != 0` path. But `error_max_turns` can also occur with `exit_code != 0`. Currently, if the subprocess exits with code 1 due to `error_max_turns`, it is classified as `PhaseStatus.ERROR` at line 784 with no further analysis. The proposed recovery chain adds context-exhaustion detection but does not add `error_max_turns` detection to the non-zero exit path.

This means the system would recover from context exhaustion (Prompt is too long) on non-zero exit but **not** from budget exhaustion (error_max_turns) on non-zero exit. The analysis does not address this asymmetry.

---

## Risk Severity Matrix

| Fault | Severity | Likelihood | Evidence | Recommendation |
|---|---|---|---|---|
| F1: SOL-D discard gap | Medium | Low-Medium | S1 write itself is unprotected I/O; signal handler can skip S1 entirely (executor.py:653-656) | Wrap S1 write in try/except; retain SOL-D as defense-in-depth or add explicit error handling |
| F2: TOCTOU race in detect_prompt_too_long | Low | Low | OS pipe flush may be incomplete at read time; mitigated by poll loop exit condition | Add short sleep or explicit fsync; scan error_file (stderr) as backup per S2-R08 |
| F3: TUI KeyError on PASS_RECOVERED | High | Certain | STATUS_STYLES dict subscript at tui.py:174 will throw KeyError; permanently disables TUI | Add PASS_RECOVERED to STATUS_STYLES and STATUS_ICONS before deploying the enum value |
| F4: Logger silent drop | Medium | Certain | logging_.py:126-140 has no branch for PASS_RECOVERED; no screen output produced | Add PASS_RECOVERED to the screen routing logic (suggest _screen_info with "[RECOVERED]" prefix) |
| F5: task_results NameError | Critical | Certain | execute_sprint() does not call execute_phase_tasks(); task_results variable does not exist at insertion point | Redesign S1 to work with per-phase execution model or restructure execute_sprint to use per-task model |
| F6: FailureClassifier bypass | Medium | Certain | Classifier only runs when is_failure is True; PASS_RECOVERED has is_failure=False | Add recovery-specific logging in the recovery code path; do not rely on FailureClassifier for PASS_RECOVERED diagnostics |
| F7: error_max_turns asymmetry | Low | Low | error_max_turns detection missing from exit_code!=0 path | Add error_max_turns check alongside detect_prompt_too_long in the non-zero exit recovery chain |

---

## Corrected Risk Assessment

### Analysis Underestimates

| Risk Item | Analysis Rating | Corrected Rating | Justification |
|---|---|---|---|
| TUI/logger don't handle PASS_RECOVERED | Medium | **High (TUI) / Medium (Logger)** | TUI will crash with KeyError at tui.py:174, not "handle ungracefully" -- it will permanently disable the dashboard. Logger will silently drop the event. Both are certain, not probabilistic. |
| PASS_RECOVERED used for two recovery mechanisms -- loss of diagnostic specificity | Low | **Medium** | FailureClassifier never runs for PASS_RECOVERED phases. No logging is specified in the recovery path. Post-hoc diagnosis is impossible without manual log forensics. |
| SOL-C checkpoint inference depends on agent-written checkpoint files | Low | **Low** (agree) | This remains a last-resort fallback. Correct assessment. |

### Analysis Overestimates

| Risk Item | Analysis Rating | Corrected Rating | Justification |
|---|---|---|---|
| _determine_phase_status signature change breaks existing test mocks | Low | **Low** (agree) | Keyword-only args with defaults is the correct backward-compatible pattern. However, note that the function is module-private (underscore prefix), so external consumers should not exist. |

### Analysis Misses Entirely

| Risk Item | Severity | Justification |
|---|---|---|
| S1 implementation assumes execute_phase_tasks is called from execute_sprint -- it is not | **Critical** | The proposed ~5 lines of code reference variables (task_results, remaining) that do not exist in scope. The entire S1 design needs rework for the per-phase execution model. |
| S1 write has no exception handling | **Medium** | A disk-full OSError during S1 write would crash execute_sprint with no result file and no recovery. |
| Signal handler can skip S1 write entirely | **Low** | Lines 653-656 break before the proposed insertion point on SIGINT/SIGTERM. Sprint is marked INTERRUPTED so impact is limited, but stale result files from prior runs remain. |

---

## Summary of Actionable Findings

1. **BLOCKING**: The S1 implementation as specified in the analysis cannot work. `task_results` and `remaining` do not exist in `execute_sprint()` scope. The execution architecture must be reconciled before proceeding.

2. **REQUIRED**: `STATUS_STYLES` and `STATUS_ICONS` dicts in tui.py must be updated to include `PASS_RECOVERED` before the enum value is deployed. Failure to do so will permanently disable the TUI on first recovery event.

3. **REQUIRED**: The logger's screen routing (logging_.py:126-140) must be updated to handle `PASS_RECOVERED` with appropriate severity (suggest INFO level with "[RECOVERED]" annotation).

4. **RECOMMENDED**: The recovery chain in `_determine_phase_status()` should wrap each recovery path in `try/except` to ensure fallback to the next path on exception.

5. **RECOMMENDED**: Recovery-specific logging should be added at the point where `PASS_RECOVERED` is returned, since the `FailureClassifier` system does not run for success statuses.

6. **ADVISABLE**: Reconsider the wholesale discard of SOL-D. If S1's write is wrapped in exception handling with graceful fallback, SOL-D becomes less necessary. But if S1 remains unprotected, SOL-D provides valuable defense-in-depth.
