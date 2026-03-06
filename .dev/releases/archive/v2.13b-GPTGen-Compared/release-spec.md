---
title: "v2.13 — CLIRunner Pipeline Targeted Fixes"
version: "2.13"
status: draft
decision_source: ".dev/releases/current/v2.13-CLIRunner-PipelineUnification/merged-pipeline-decision.md"
decision_option: "Option 3 — Targeted Fixes (RECOMMENDED)"
generated_by: "/sc:spec-panel"
generated_date: "2026-03-05"
expert_panel: ["Fowler", "Nygard", "Wiegers", "Crispin", "Adzic"]
scope: "src/superclaude/cli/{pipeline,sprint,roadmap}/"
complexity_class: MEDIUM
domain_distribution:
  backend: 90
  testing: 10
primary_persona: refactorer
consulting_personas: [architect, qa]
---

# v2.13 Release Spec: CLIRunner Pipeline Targeted Fixes

## 1. Executive Summary

This release implements **Option 3 (Targeted Fixes)** from the adversarial-debated pipeline architecture decision. It addresses all identified bugs and duplication at minimal risk without restructuring sprint's execution model.

**Key Outcomes**:
- Eliminate ~90 lines of process method duplication between sprint and pipeline
- Remove confirmed dead code in roadmap executor
- Fix broken `--file` flag in roadmap step execution
- Expand characterization test coverage for sprint executor (6 untested subsystems remain)
- Document the architectural decision deferring executor-level unification

**Non-Goals**:
- Full executor unification (Option 1 — rejected)
- Partial executor unification (Option 2 — deferred pending increased semantic overlap)
- New features for sprint or roadmap
- Changes to sprint's poll loop, TUI, or monitoring subsystems

## 2. Background & Decision Record

The pipeline module was extracted from sprint (documented in `pipeline/process.py:3`, commit `6548f17`). The extraction proceeded bottom-up:

1. **Models extracted** (complete): `SprintConfig` inherits `PipelineConfig`, `PhaseResult` inherits `StepResult`
2. **Process extracted** (complete): Sprint's `ClaudeProcess` inherits pipeline's `ClaudeProcess`
3. **Executor NOT extracted** (deliberate): Sprint's `execute_sprint()` remains independent

Adversarial debate (convergence 0.72) settled that executor unification is premature because:
- Sprint's poll loop relocates into a callback rather than being eliminated
- Sprint phases cannot be retried (side effects) or parallelized (sequential filesystem mutations)
- Net code reduction is approximately zero
- Effort is Large with High regression risk against zero executor tests

**Full decision record**: See `merged-pipeline-decision.md` in this directory.

## 3. Deliverables

### D1: Process Logging Hooks (Priority: P0)

**Problem**: `sprint/process.py` overrides `start()`, `wait()`, and `terminate()` from `pipeline/process.py` with ~90 lines whose only functional difference is `debug_log()` calls instead of `_log.debug()` calls.

**Solution**: Add optional lifecycle hook callbacks to the pipeline `ClaudeProcess` base class. Sprint subclass provides hooks instead of overriding entire methods.

**Files Modified**:
- `src/superclaude/cli/pipeline/process.py` — Add hook protocol and default implementations
- `src/superclaude/cli/sprint/process.py` — Remove method overrides, provide hook implementations

**Interface Specification**:

```python
# In pipeline/process.py ClaudeProcess.__init__:
#   on_spawn: Optional callback(pid: int, cmd: list[str]) -> None
#   on_exit: Optional callback(pid: int, returncode: int, was_timeout: bool) -> None
#   on_signal: Optional callback(signal_name: str, pid: int) -> None

class ClaudeProcess:
    def __init__(self, *, ..., on_spawn=None, on_exit=None, on_signal=None):
        self._on_spawn = on_spawn
        self._on_exit = on_exit
        self._on_signal = on_signal

    def start(self) -> subprocess.Popen:
        # ... existing logic ...
        self._process = subprocess.Popen(self.build_command(), **popen_kwargs)
        if self._on_spawn:
            self._on_spawn(self._process.pid, self.build_command()[:3])
        _log.debug("spawn pid=%d cmd=%s", self._process.pid, ...)
        return self._process
```

**Acceptance Criteria**:
- AC-1: Sprint `ClaudeProcess` no longer overrides `start()`, `wait()`, or `terminate()`
- AC-2: Sprint passes `on_spawn`, `on_exit`, `on_signal` callbacks that call `debug_log()`
- AC-3: Base class `start()`, `wait()`, `terminate()` call hooks when provided, skip when None
- AC-4: All existing sprint subprocess behavior is identical (same SIGTERM/SIGKILL escalation, same timeout handling, same file handle lifecycle)
- AC-5: NFR-007 remains satisfied — pipeline has zero imports from sprint or roadmap
- AC-6: Roadmap's usage of `ClaudeProcess` (via pipeline) is unaffected (no hooks provided = current behavior)

**Verification**:
- Unit tests for base class hooks (None hooks = no-op, provided hooks = called with correct args)
- Unit tests for sprint hook implementations (verify `debug_log` calls)
- Signal handling regression test: SIGTERM then SIGKILL escalation path preserved

**Estimated Reduction**: ~70 lines removed from sprint/process.py, ~15 lines added to pipeline/process.py

### D2: Dead Code Removal (Priority: P0)

**Problem**: `roadmap/executor.py:53-76` defines `_build_subprocess_argv()` which has zero call sites in production code. It was superseded by `ClaudeProcess.build_command()` during the pipeline extraction.

**Files Modified**:
- `src/superclaude/cli/roadmap/executor.py` — Delete lines 53-76 and associated import `_FORBIDDEN_FLAGS` (line 50)

**Acceptance Criteria**:
- AC-1: `_build_subprocess_argv` no longer exists in the codebase
- AC-2: `_FORBIDDEN_FLAGS` removed if no other references exist
- AC-3: All existing tests pass
- AC-4: `grep -r "_build_subprocess_argv" src/` returns zero results

**Verification**:
- Negative grep test confirming zero references
- Existing test suite passes unchanged

**Estimated Reduction**: ~28 lines removed

### D3: Roadmap File-Passing Fix (Priority: P1)

**Problem**: Roadmap uses `--file` flags to pass input files to claude subprocess. This is unreliable when file paths contain spaces or special characters, and is inconsistent with sprint's inline approach.

**Solution**: Switch `roadmap_run_step()` to embed file contents inline in the prompt rather than using `--file` flags.

**Files Modified**:
- `src/superclaude/cli/roadmap/executor.py` — Modify `roadmap_run_step()` to read input files and embed content in prompt

**Acceptance Criteria**:
- AC-1: `roadmap_run_step()` no longer passes `--file` flags to the subprocess
- AC-2: Input file contents are embedded in the prompt as fenced code blocks with file path headers
- AC-3: Roadmap pipeline produces identical outputs for existing test fixtures
- AC-4: File paths with spaces and special characters are handled correctly

**Verification**:
- Unit test: prompt contains embedded file content matching source files
- Integration test: roadmap pipeline end-to-end with multi-file step

### D4: Sprint Executor Characterization Tests (Priority: P0)

**Problem**: Sprint's `execute_sprint()` has partial test coverage — 4 integration tests exist covering pass/halt/timeout/interrupt, plus 14 tests for `_determine_phase_status`. However, 6 subsystems remain untested: watchdog/stall detection, multi-phase sequencing, TUI error resilience, diagnostic collection, tmux integration, and monitor thread lifecycle. Coverage is approximately 45%.

**Solution**: Write characterization tests for the **6 untested subsystems**, expanding coverage to >= 70%.

**Files Created**:
- `tests/sprint/test_executor_characterization.py`

**Test Coverage Targets** (minimum):

| Subsystem | Test Cases | Priority | Status |
|-----------|-----------|----------|--------|
| Phase sequencing | Happy path: 3 phases complete in order | P0 | NEW |
| Phase sequencing | Halt on HALT recommendation | P0 | EXISTS (test_executor.py) |
| Phase sequencing | Skip already-completed phases (resume) | P1 | NEW |
| Subprocess lifecycle | Process start, wait, exit code capture | P0 | EXISTS (test_executor.py) |
| Subprocess lifecycle | Timeout triggers terminate() | P0 | EXISTS (test_executor.py) |
| Signal handling | SIGINT sets shutdown flag, terminates current phase | P0 | EXISTS (test_executor.py) |
| Signal handling | Handler installed/uninstalled correctly | P1 | EXISTS (test_process.py) |
| TUI integration | TUI receives MonitorState updates | P1 | NEW |
| TUI integration | TUI display error does not abort sprint | P1 | NEW |
| Monitor thread | OutputMonitor parses NDJSON and updates state | P1 | NEW |
| Stall detection | Watchdog detects stall, action=kill terminates phase | P1 | NEW |
| Stall detection | Watchdog detects stall, action=warn continues | P1 | NEW |
| Stall detection | Watchdog resets when output resumes | P1 | NEW |
| Multi-phase | 3 phases: pass, pass, halt — halts at phase 3 | P0 | NEW |
| Diagnostics | Failure triggers DiagnosticCollector and report | P2 | NEW |
| Diagnostics | Diagnostic collection failure does not abort sprint | P2 | NEW |
| Tmux | Tail pane update called when tmux_session_name set | P2 | NEW |

**Acceptance Criteria**:
- AC-1: Minimum 12 NEW test cases covering all rows marked NEW above
- AC-2: Tests use mocked subprocess (no real claude invocation)
- AC-3: Tests pin current behavior — they document what IS, not what SHOULD BE
- AC-4: All tests pass on current codebase without modifications
- AC-5: Coverage of `sprint/executor.py` reaches >= 70% line coverage (up from ~45%)

**Verification**:
- `uv run pytest tests/sprint/test_executor_characterization.py -v` passes
- `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint.executor` shows >= 70%

## 4. Milestone Structure

### M1: Characterization Tests (P0) — Must ship first
**Deliverables**: D4 (revised scope — 6 untested subsystems, 12+ new tests)
**Dependencies**: None
**Rationale**: Tests must exist before any refactoring. This is the safety net for D1.

### M2: Targeted Fixes (P0) — Three independent sub-steps
**Deliverables**: D1, D2
**Dependencies**: M1 (D4 tests must pass before and after changes)
**Sub-steps** (see Section 9.9 for details):
- **M2a**: Delete sprint's `wait()` override (zero-risk, pure duplication) — immediate
- **M2b**: Add hooks to pipeline base + migrate sprint `start()`/`terminate()` — main work
- **M2c**: Delete dead code `_build_subprocess_argv` — independent of M2b

### M3: File-Passing Fix (P1)
**Deliverables**: D3
**Dependencies**: D2 (dead code removal cleans up the file in which D3 operates)
**Rationale**: Lower priority, can ship independently.

## 5. Non-Functional Requirements

### NFR-001: Backward Compatibility
All changes must preserve existing CLI behavior. No user-facing changes to `superclaude sprint` or `superclaude roadmap` commands.

### NFR-002: NFR-007 Compliance
Pipeline module must maintain zero imports from `superclaude.cli.sprint` or `superclaude.cli.roadmap`. The hook callbacks use primitive types only (int, str, bool, list).

### NFR-003: Test Gate
No deliverable in M2 or M3 may merge until all D4 characterization tests pass both before and after the change.

### NFR-004: No New Dependencies
No new Python package dependencies introduced.

## 6. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Logging hook refactor breaks SIGTERM/SIGKILL escalation | Low | High | D4 characterization tests pin signal handling; run before/after D1 |
| Dead code removal breaks an untested code path | Very Low | Medium | Grep verification + full test suite |
| File-passing change alters roadmap output format | Low | Medium | Integration test with fixture comparison |
| Characterization tests are incomplete, miss a subsystem | Medium | Medium | Coverage threshold (60%) + code review of test plan |

## 7. Out of Scope (Deferred)

The following are explicitly deferred per the architectural decision:

| Item | Reason | Revisit Trigger |
|------|--------|-----------------|
| Executor unification (Option 1/2) | Net zero code reduction, Large effort, High risk | Sprint adopts gates, retry with rollback, or third consumer of execute_pipeline() |
| Two state management systems | Different domains with different semantics | Semantic overlap increases |
| Sprint retry logic | Phases have side effects; retry requires rollback infrastructure | Rollback infrastructure is designed |
| Sprint parallel phases | Sequential filesystem mutations prevent parallelism | Sprint adopts isolated workspaces |

## 8. Phased Extraction Roadmap (Future)

This release is **Phase 1** of a longer extraction roadmap:

- **Phase 1 (this release)**: Targeted fixes — logging hooks, dead code, file-passing, characterization tests
- **Phase 2 (future, when triggered)**: Extract narrower shared primitives — state/result normalization, shared cancellation interfaces
- **Phase 3 (future, re-evaluate)**: Revisit executor unification with concrete `sprint_run_step` design

## 9. Design Details

*Added by /sc:design review — 2026-03-05*

### 9.1 Alternative Analysis: Hooks vs Mixins vs Decorators

Three approaches were evaluated for eliminating the process method duplication:

**Option A: Lifecycle Hook Callbacks (SELECTED)**
- Base class accepts optional callables (`on_spawn`, `on_exit`, `on_signal`)
- Sprint passes closures that call `debug_log`
- Pros: Zero coupling, NFR-007 clean, no new types, easy to test
- Cons: Multiple callback args in constructor

**Option B: Mixin Class**
- `DebugLoggingMixin` provides `_log_spawn()`, `_log_exit()` etc.
- Sprint inherits from both `ClaudeProcess` and `DebugLoggingMixin`
- Rejected: Mixin would need to import `debug_log` from sprint, violating NFR-007. Alternatively, the mixin lives in pipeline but contains sprint-specific knowledge — wrong direction.

**Option C: Decorator / Wrapper**
- `DebugLoggingProcess(inner: ClaudeProcess)` wraps and delegates
- Rejected: Sprint's `ClaudeProcess` already extends the base (for `build_prompt`, `__init__` with config/phase). A decorator would require sprint to stop inheriting, breaking the model extraction that's already complete.

**Decision**: Option A. Hooks are the only approach that maintains NFR-007, preserves the existing inheritance hierarchy, and keeps the pipeline module consumer-agnostic.

### 9.2 Precise Diff Analysis: What Actually Differs

Line-by-line comparison of sprint overrides vs pipeline base methods:

#### `start()` — Sprint lines 91-126 vs Pipeline lines 89-113

| Aspect | Pipeline Base | Sprint Override | Different? |
|--------|--------------|-----------------|------------|
| mkdir parents | `self.output_file.parent` | `config.output_file(phase).parent` | **Yes** — sprint re-derives paths from config instead of using `self.output_file`. Functionally identical (same value) but a latent inconsistency. |
| File handle open | `self.output_file` / `self.error_file` | `config.output_file(phase)` / `config.error_file(phase)` | **Same value**, different reference path |
| Popen kwargs | Identical | Identical | No |
| setpgrp check | Identical | Identical | No |
| Post-spawn logging | `_log.debug("spawn pid=%d cmd=%s", ...)` | `debug_log(_dbg, "spawn", pid=..., cmd=..., phase=...)` + `debug_log(_dbg, "files_opened", ...)` | **Yes** — sprint emits 2 structured events vs 1 standard log |

**Hook requirement**: `on_spawn(pid: int, cmd_preview: list[str])` — sprint's closure captures `phase` and `output_file`/`error_file` from its own scope.

#### `wait()` — Sprint lines 128-137 vs Pipeline lines 115-124

| Aspect | Pipeline Base | Sprint Override | Different? |
|--------|--------------|-----------------|------------|
| wait with timeout | Identical | Identical | No |
| TimeoutExpired handling | Identical | Identical | No |
| close_handles | Identical | Identical | No |
| Return logic | Identical | Identical | No |

**Conclusion: Sprint's `wait()` override is a pure no-op duplication. Delete it with zero behavioral change.** This is the lowest-risk change in the entire deliverable.

#### `terminate()` — Sprint lines 139-179 vs Pipeline lines 126-163

| Aspect | Pipeline Base | Sprint Override | Different? |
|--------|--------------|-----------------|------------|
| Early exit check | Identical | Identical | No |
| pgroup detection | Identical | Identical | No |
| SIGTERM send | Identical | Identical | No |
| SIGTERM logging | `_log.debug("signal_sent SIGTERM pid=%d")` | `debug_log(_dbg, "signal_sent", signal="SIGTERM", pid=...)` | **Yes** — structured vs standard |
| 10s wait | Identical | Identical | No |
| SIGKILL send | Identical | Identical | No |
| SIGKILL logging | `_log.debug("signal_sent SIGKILL pid=%d")` | `debug_log(_dbg, "signal_sent", signal="SIGKILL", pid=...)` | **Yes** — structured vs standard |
| Exit logging | `_log.debug("exit pid=%d code=%s", pid, rc)` | `debug_log(_dbg, "exit", pid=..., code=rc, was_timeout=...)` | **Yes** — sprint adds `was_timeout` |
| close_handles | Identical | Identical | No |

**Hook requirement**: `on_signal(signal_name: str, pid: int)` for SIGTERM/SIGKILL events, `on_exit(pid: int, returncode: int | None)` for exit event. The `was_timeout` information is sprint-specific — the sprint closure computes it from `getattr(self, "_timed_out", False)`.

#### `_close_handles()` — Sprint lines 181-187 vs Pipeline lines 165-171

Identical. Sprint's override is pure duplication. However, sprint does NOT override `_close_handles()` — it inherits it. No action needed.

### 9.3 Concrete Interface Contract

```python
# In pipeline/process.py — Type aliases (no new imports needed)
from typing import Callable, Optional

# Hook type signatures
OnSpawnHook = Callable[[int, list[str]], None]      # (pid, cmd_preview) -> None
OnSignalHook = Callable[[str, int], None]           # (signal_name, pid) -> None
OnExitHook = Callable[[int, int | None], None]      # (pid, returncode) -> None

class ClaudeProcess:
    def __init__(
        self,
        *,
        prompt: str,
        output_file: Path,
        error_file: Path,
        max_turns: int = 50,
        model: str = "",
        permission_flag: str = "--dangerously-skip-permissions",
        timeout_seconds: int = 6300,
        output_format: str = "stream-json",
        extra_args: list[str] | None = None,
        # NEW: lifecycle hooks (all optional, default None = no-op)
        on_spawn: OnSpawnHook | None = None,
        on_signal: OnSignalHook | None = None,
        on_exit: OnExitHook | None = None,
    ):
        # ... existing assignments ...
        self._on_spawn = on_spawn
        self._on_signal = on_signal
        self._on_exit = on_exit
```

**Hook call sites in base class methods:**

```python
def start(self) -> subprocess.Popen:
    # ... existing logic up to Popen ...
    self._process = subprocess.Popen(self.build_command(), **popen_kwargs)
    if self._on_spawn:
        self._on_spawn(self._process.pid, self.build_command()[:3])
    _log.debug("spawn pid=%d cmd=%s", self._process.pid, ...)
    return self._process

def terminate(self) -> None:
    # ... after SIGTERM send ...
    if self._on_signal:
        self._on_signal("SIGTERM", self._process.pid)
    _log.debug("signal_sent SIGTERM pid=%d", self._process.pid)

    # ... after SIGKILL send ...
    if self._on_signal:
        self._on_signal("SIGKILL", self._process.pid)
    _log.debug("signal_sent SIGKILL pid=%d", self._process.pid)

    # ... at exit ...
    if self._on_exit:
        self._on_exit(self._process.pid, self._process.returncode)
    _log.debug("exit pid=%d code=%s", self._process.pid, self._process.returncode)
    self._close_handles()
```

**Design decisions:**
- Hooks fire BEFORE the standard `_log.debug` calls (hooks may want to log at a different level)
- Hooks receive primitive types only (int, str, list, None) — no process objects, no config objects
- Hook exceptions are NOT caught — a failing hook should surface, not be silently swallowed
- The base class `_log.debug` calls remain — they provide baseline observability for all consumers

### 9.4 Sprint Subclass Migration: Before/After

**BEFORE** (current — 188 lines in sprint/process.py):
```python
class ClaudeProcess(_PipelineClaudeProcess):
    def __init__(self, config, phase):     # 14 lines — custom constructor
    def build_prompt(self) -> str:          # 37 lines — sprint-specific prompt
    def start(self) -> subprocess.Popen:    # 36 lines — DUPLICATED with debug_log
    def wait(self) -> int:                  # 10 lines — PURE DUPLICATION
    def terminate(self):                    # 41 lines — DUPLICATED with debug_log
    def _close_handles(self):               # 7 lines  — PURE DUPLICATION
```

**AFTER** (target — ~75 lines in sprint/process.py):
```python
class ClaudeProcess(_PipelineClaudeProcess):
    def __init__(self, config, phase):      # ~25 lines — constructor + hook wiring
    def build_prompt(self) -> str:          # 37 lines — unchanged, sprint-specific
    # start()      — DELETED (inherited, hooks handle logging)
    # wait()       — DELETED (inherited, was pure duplication)
    # terminate()  — DELETED (inherited, hooks handle logging)
    # _close_handles() — already inherited, never overridden

def _make_spawn_hook(dbg, phase, config):
    """Factory for sprint's on_spawn hook — captures phase context."""
    def hook(pid: int, cmd_preview: list[str]) -> None:
        debug_log(dbg, "spawn", pid=pid, cmd=str(cmd_preview), phase=phase.number)
        debug_log(dbg, "files_opened",
                  stdout=str(config.output_file(phase)),
                  stderr=str(config.error_file(phase)))
    return hook

def _make_signal_hook(dbg):
    """Factory for sprint's on_signal hook."""
    def hook(signal_name: str, pid: int) -> None:
        debug_log(dbg, "signal_sent", signal=signal_name, pid=pid)
    return hook

def _make_exit_hook(dbg):
    """Factory for sprint's on_exit hook."""
    def hook(pid: int, returncode: int | None) -> None:
        debug_log(dbg, "exit", pid=pid, code=returncode,
                  was_timeout=(returncode == 124))
    return hook
```

**Constructor change:**
```python
def __init__(self, config: SprintConfig, phase: Phase):
    self.config = config
    self.phase = phase
    prompt = self.build_prompt()
    super().__init__(
        prompt=prompt,
        output_file=config.output_file(phase),
        error_file=config.error_file(phase),
        max_turns=config.max_turns,
        model=config.model,
        permission_flag=config.permission_flag,
        timeout_seconds=config.max_turns * 120 + 300,
        output_format="stream-json",
        on_spawn=_make_spawn_hook(_dbg, phase, config),
        on_signal=_make_signal_hook(_dbg),
        on_exit=_make_exit_hook(_dbg),
    )
```

**Lines removed**: ~94 (start + wait + terminate + _close_handles overrides)
**Lines added**: ~30 (hook factories) + ~6 (constructor args)
**Net reduction**: ~58 lines from sprint/process.py, ~9 lines added to pipeline/process.py

### 9.5 Correction: Existing Test Coverage

The original spec stated "Sprint has zero executor tests." This is **incorrect**. Actual coverage:

**`tests/sprint/test_executor.py`** (existing):
- `TestDeterminePhaseStatus` — 14 test cases covering the 7-level status priority chain
- `TestExecuteSprintIntegrationCoverage` — 4 integration tests:
  - `test_execute_sprint_pass` — happy path, 1 phase, CONTINUE signal
  - `test_execute_sprint_halt` — HALT recommendation, SystemExit(1)
  - `test_execute_sprint_timeout_exit_code_124` — monotonic timeout, exit 124
  - `test_execute_sprint_interrupted` — SIGINT via SignalHandler, INTERRUPTED outcome

**`tests/sprint/test_process.py`** (existing):
- `TestClaudeProcess` — 8 tests: command construction, model, env, prompt, timeout
- `TestClaudeProcessPlatformFallback` — 2 tests: non-Unix start, non-Unix terminate
- `TestSignalHandler` — 4 tests: initial state, install/uninstall, handle, idempotent

**Actual gaps** (subsystems with zero test coverage):
- Stall detection / watchdog (executor lines 126-162)
- Multi-phase sequencing (>1 phase, sequential progression)
- TUI error resilience (executor lines 166-170)
- Diagnostic collection on failure (executor lines 242-258)
- Tmux tail pane updates (executor line 80)
- Monitor thread integration (OutputMonitor.reset/start/stop lifecycle)

**Revised D4 scope**: Write characterization tests for the **6 untested subsystems** above, not the full 12-test suite originally specified. Target coverage increase from current ~45% to >= 70%.

### 9.6 Edge Cases in Signal Handling and File Handle Lifecycle

#### Edge Case 1: Hook exception during SIGTERM

If `on_signal("SIGTERM", pid)` raises, the SIGKILL escalation path is skipped. This is **acceptable** — a buggy hook should surface loudly, and the process will be orphaned (cleaned up by OS on parent exit). The alternative (try/except around hooks) would silently mask bugs.

**Design decision**: Do NOT wrap hooks in try/except. Document that hooks must not raise.

#### Edge Case 2: `_close_handles()` called multiple times

Currently both `wait()` and `terminate()` call `_close_handles()`. The base class handles this safely — the `try: fh.close()` pattern is idempotent. After migration, sprint inherits this behavior unchanged.

**Risk**: None. Already handled.

#### Edge Case 3: Sprint's `was_timeout` in exit hook

Sprint's current `terminate()` computes `was_timeout=(rc == 124 or getattr(self, "_timed_out", False))`. The `_timed_out` attribute is set by `execute_sprint()` (executor.py:105), not by `ClaudeProcess`. After migration, the exit hook receives only `(pid, returncode)` — it cannot access `_timed_out`.

**Resolution**: The hook factory uses `returncode == 124` as the timeout indicator. This is sufficient because:
- When the executor sets `_timed_out = True` and calls `terminate()`, the process returncode after SIGTERM/SIGKILL will NOT be 124 (it'll be -15 or -9)
- The `_timed_out` flag was a belt-and-suspenders check
- The executor already handles timeout classification independently (executor.py:176-178)
- Sprint's debug_log `was_timeout` field is informational only — it doesn't drive control flow

**Mitigation**: Accept `was_timeout=(returncode == 124)` in the hook. Document in commit message that the `_timed_out` cross-reference is dropped because the executor handles timeout classification upstream.

#### Edge Case 4: `on_spawn` called but process immediately crashes

If `Popen()` succeeds but the process exits before `on_spawn` runs, `pid` is still valid (process existed). The hook fires with correct data. No issue.

#### Edge Case 5: `on_exit` not called when `wait()` path is taken

In the current base class, `wait()` does NOT call any exit logging — it just calls `_close_handles()`. Sprint's `wait()` override also doesn't log on exit. So the `on_exit` hook is ONLY called from `terminate()`.

**Design decision**: Add `on_exit` call to `wait()` as well, in the success path after `_close_handles()`:

```python
def wait(self) -> int:
    try:
        self._process.wait(timeout=self.timeout_seconds)
    except subprocess.TimeoutExpired:
        self.terminate()  # on_exit called inside terminate
        return 124

    rc = self._process.returncode if self._process.returncode is not None else -1
    if self._on_exit:
        self._on_exit(self._process.pid, rc)
    self._close_handles()
    return rc
```

This is a **behavioral addition** (new logging in the normal exit path) but is the correct design — the exit hook should fire on ALL exit paths, not just terminate.

### 9.7 D2 Design: Dead Code Removal Details

**Target**: `roadmap/executor.py` lines 50-78 (`_FORBIDDEN_FLAGS` + `_build_subprocess_argv`)

**Verification before deletion**:
```bash
# Confirm zero call sites
grep -rn "_build_subprocess_argv" src/
# Expected: only the definition at roadmap/executor.py:53

grep -rn "_FORBIDDEN_FLAGS" src/
# Expected: only the definition at roadmap/executor.py:50
# and the usage at roadmap/executor.py:74
```

**Note**: `_FORBIDDEN_FLAGS` is only used within `_build_subprocess_argv`. The context isolation assertion has been relocated to `pipeline/process.py` via `ClaudeProcess.build_command()` which uses `--no-session-persistence` flag instead. Safe to delete both.

### 9.8 D3 Design: File-Passing Fix Details

**Current behavior** (`roadmap/executor.py:112-116`):
```python
extra_args=[
    arg
    for input_path in step.inputs
    for arg in ("--file", str(input_path))
],
```

**Problem**: `--file` passes file references to the claude subprocess. If files are large or paths have special characters, this can fail. Sprint uses inline prompt embedding instead.

**Proposed fix**: Read input files and embed in prompt within `roadmap_run_step()`:

```python
def _embed_inputs(prompt: str, inputs: list[Path]) -> str:
    """Embed input file contents inline in the prompt."""
    if not inputs:
        return prompt
    parts = [prompt, "\n\n## Input Files\n"]
    for path in inputs:
        content = path.read_text(encoding="utf-8")
        parts.append(f"\n### {path.name}\n```\n{content}\n```\n")
    return "".join(parts)
```

Then in `roadmap_run_step`:
```python
proc = ClaudeProcess(
    prompt=_embed_inputs(step.prompt, step.inputs),
    # ... other args ...
    extra_args=[],  # no more --file flags
)
```

**Risk**: Prompt size increases. Each input file adds its full content to the prompt. For the roadmap pipeline, input files are markdown documents (typically 5-50KB each), well within claude's context window.

**Mitigation**: Add a size check — if total embedded content exceeds 100KB, fall back to `--file` flags with a warning.

### 9.9 Revised Milestone Dependencies

```
M1: Characterization Tests (REVISED scope — 6 untested subsystems)
 |
 v
M2a: Delete wait() override (zero-risk, pure duplication)  ← Can ship immediately after M1
M2b: Add hooks to pipeline base class + migrate sprint start()/terminate()
M2c: Delete dead code (_build_subprocess_argv)  ← Independent of M2b
 |
 v
M3: File-passing fix (after M2c cleans up the file)
```

**Key change**: M2 is split into M2a/M2b/M2c because `wait()` deletion is trivially safe and can be verified independently, reducing the blast radius of the hook migration (M2b).

### 9.10 Implementation Sequence (Step-by-Step)

**Step 1** — M1: Add characterization tests for 6 untested subsystems
- Write tests, verify they pass on current code, measure coverage delta

**Step 2** — M2a: Delete sprint's `wait()` override
- Delete `sprint/process.py` lines 128-137
- Run full test suite — expect zero failures (pure no-op override)
- Commit: `refactor(sprint): remove no-op wait() override (identical to base)`

**Step 3** — M2b: Add hooks to pipeline base
- Add `on_spawn`, `on_signal`, `on_exit` params to `pipeline/process.py ClaudeProcess.__init__`
- Add hook call sites to `start()`, `terminate()`, `wait()`
- Write unit tests for hooks in `tests/pipeline/test_process_hooks.py`
- Commit: `feat(pipeline): add lifecycle hooks to ClaudeProcess`

**Step 4** — M2b continued: Migrate sprint to use hooks
- Add hook factory functions to `sprint/process.py`
- Wire hooks in sprint's `__init__`
- Delete `start()` and `terminate()` overrides
- Delete `_close_handles()` if still present as override
- Run full test suite + characterization tests
- Commit: `refactor(sprint): replace method overrides with lifecycle hooks`

**Step 5** — M2c: Delete dead code
- Delete `_FORBIDDEN_FLAGS` and `_build_subprocess_argv` from `roadmap/executor.py`
- Grep verification
- Commit: `cleanup(roadmap): remove dead _build_subprocess_argv`

**Step 6** — M3: File-passing fix
- Add `_embed_inputs()` helper
- Modify `roadmap_run_step()` to use inline embedding
- Add/update tests
- Commit: `fix(roadmap): embed input files inline instead of --file flags`

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lines removed (duplication) | >= 58 net | `git diff --stat` on sprint/process.py |
| Lines removed (dead code) | >= 25 | `git diff --stat` on roadmap/executor.py |
| Sprint executor test coverage | >= 70% | `pytest --cov` report (up from ~45%) |
| Regression count | 0 | Full test suite green |
| NFR-007 violations | 0 | `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` |
