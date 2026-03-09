# Sprint Diagnostic Framework — Spec vs Reality Analysis

> **Spec analyzed**: `.dev/releases/complete/v2.03-CLI-Sprint-diag/spec-sprint-diagnostic-framework.md` (v1.0)
> **Codebase snapshot**: `src/superclaude/cli/sprint/` + `tests/sprint/diagnostic/`
> **Analysis date**: 2026-03-08
> **Scope**: Diagnostic only — no fixes proposed

---

## Top 3 Theories for Why Bugs Survive Despite Planning Rigor

### Theory 1: Spec-to-Implementation Semantic Drift — Components Built to Different Contracts

The spec defined precise component APIs (e.g., `DiagnosticCollector.collect(config, phase, phase_result, monitor_state, process)` with a `subprocess_pid`, `output_bytes`, `was_stall_killed` etc.), but the implementation diverged into a completely different contract. The spec's `DiagnosticCollector` was stateless and accepted config as a parameter; the built version takes `config` as a constructor argument and has a different `collect()` signature (`collect(phase, phase_result, monitor_state)` — no `process` parameter). The spec's `FailureClassifier.classify()` returned `(FailureMode, confidence: float)` with 7 failure modes; the built version returns a single `FailureCategory` enum with only 5 categories and no confidence score.

This means the spec's **E4 diagnostic report JSON format** (with `classification_confidence`, `failure_mode`, `subprocess_pid`, `process_state_at_kill`, `recommended_actions`) was never built. The actual report is **Markdown**, not JSON, and contains none of the machine-parseable fields the spec mandated.

**Evidence**:
- Spec R3.1: `DiagnosticCollector` takes `config, phase, phase_result, monitor_state, process` → Built: constructor takes `config`, `collect()` takes `phase, phase_result, monitor_state` (no `process`)
- Spec R3.4-R3.9: 7 failure modes (`SPAWN_FAILURE`, `SILENT_STALL`, `OUTPUT_STALL`, `RESULT_MISSING`, `EXIT_CODE_ERROR`, `TIMEOUT`, `UNKNOWN`) → Built: 5 categories (`STALL`, `TIMEOUT`, `CRASH`, `ERROR`, `UNKNOWN`) — `SPAWN_FAILURE`, `SILENT_STALL`, `OUTPUT_STALL`, `RESULT_MISSING`, `EXIT_CODE_ERROR` collapsed/renamed
- Spec R3.10-R3.13: `diagnostic-report.json` with `report_version`, `machine-parseable`, `schema-stable` → Built: `phase-N-diagnostic.md` in Markdown format
- Spec R3.12: `Recommended actions included` with per-failure-mode debugging steps → Built: no recommended actions in `ReportGenerator.generate()`

### Theory 2: Test Levels Redefined Away from Actual Subprocess Execution

The spec defined L0-L3 as **graduated end-to-end tests that actually invoke the sprint runner** with shell scripts (L0) or real `claude` binary (L1-L3). The DiagnosticTestHarness was specified to `run_sprint()` by calling `execute_sprint()`. The built tests instead test **component internals using mock data injection** — they never call `execute_sprint()` or spawn any subprocess.

- **Spec L0** (R2.1-R2.5): "Shell script subprocess" that exercises the full runner pipeline — subprocess spawns, output file created, result file written, `_determine_phase_status` returns PASS, exit code 0, debug.log validated. The spec even includes a fake `claude` shell script design.
- **Built L0**: Tests the debug logger writing to a file and the DebugLogReader parsing it. No subprocess. No shell script. No `_determine_phase_status`. No sprint runner execution.
- **Spec LN** (R2.16-R2.21): 6 failure modes tested with real subprocess simulation — spawn failure, silent stall, output stall, result missing, exit code error, timeout.
- **Built LN**: Tests that `DiagnosticCollector` handles missing files gracefully and `FailureClassifier` returns `UNKNOWN` for empty bundles. No failure mode simulation. No stall timeout triggering. No subprocess killed.

The test levels were redefined from "pipeline integration tests" to "unit tests of diagnostic subcomponents." This means the spec's primary value proposition — **validating the sprint runner itself under controlled failure conditions** — was never built.

**Evidence**:
- Spec R4.1: `create_sprint(phases: list[PhaseSpec]) → SprintConfig` with `PhaseSpec` defining `task_content, expected_behavior` → Built: `DiagnosticTestHarness.__init__()` creates phases from `num_phases: int` with no task content or behavior spec
- Spec R4.2: `run_sprint(config, timeout, stall_timeout) → DiagnosticResult` that calls `execute_sprint()` → Built: `run_sprint()` method **does not exist** on the harness. No sprint execution at any test level.
- Spec R4.3: `analyze_result(result) → DiagnosticReport` runs collector + classifier + root cause → Built: no `analyze_result()` on harness
- Spec E5 (Given/When/Then): "WHEN sprint run executes with --debug --no-tmux --stall-timeout 10 THEN exit code is 0 AND result file exists" → No test exercises this scenario
- Spec R2.4: "Max duration assertion: Must complete in <5s" → No duration assertions in any built test

### Theory 3: The `debug_log()` API Signature Mismatch Creates Silent Incompatibility

The spec defined `debug_log(logger, component, event, **kwargs)` where `component` is an explicit parameter determining the `[component]` field in log output. The built version uses `debug_log(logger, event, **kwargs)` — no `component` parameter. Instead, the component is derived from the Python logger name's last segment (e.g., `logging.getLogger("superclaude.sprint.debug.executor")` → `[executor]`).

This seemingly minor API difference means every call site in the spec's diff plan (`executor.py`, `process.py`, `tui.py`, `monitor.py`) would need to create component-specific child loggers instead of passing a string. The executor implementation does this correctly (`_dbg = logging.getLogger(_DBG_NAME)` where `_DBG_NAME = "superclaude.sprint.debug.executor"`), but the spec's pattern for `process.py`, `tui.py`, and `monitor.py` of passing the debug logger instance and calling `debug_log(self._debug, "process", "spawn", ...)` would not produce the expected output — it would use the parent logger's component name.

In practice, `process.py` and `monitor.py` and `tui.py` don't appear to call `debug_log()` at all in their actual implementations — the executor logs on their behalf during the poll loop. This means the fine-grained per-component event coverage (R1.9-R1.13) specified for process, monitor, TUI, and tmux was never independently instrumented.

**Evidence**:
- Spec R1.19: "Logger passed to: `execute_sprint()`, `ClaudeProcess.__init__()`, `OutputMonitor.__init__()`, `SprintTUI.__init__()`, tmux functions" → Built: Only executor calls `debug_log()`. `ClaudeProcess`, `OutputMonitor`, `SprintTUI`, and tmux functions have no `debug_logger` parameter.
- Spec R1.9-R1.10: Process events (`spawn`, `signal_sent`, `files_opened`, `exit`) specified as emitted by `process.py` → Built: These events are only verified in `test_instrumentation.py` via manual `debug_log()` calls in tests, not emitted by the actual `ClaudeProcess` class
- Spec R1.11: Monitor events (`output_file_stat`, `signal_extracted`) → Not emitted by `OutputMonitor`
- Spec R1.12: TUI events (`tui_start`, `tui_update`, `tui_live_failed`, `tui_stop`) → Not emitted by `SprintTUI`

---

## Blind Spots Identified

### Blind Spot 1: Tests Validate Test Infrastructure, Not Production Code

The diagnostic test suite (`tests/sprint/diagnostic/`) tests the `DebugLogReader`, `DiagnosticCollector`, `FailureClassifier`, and `ReportGenerator` as isolated units with **harness-injected data**. No test validates that the **production executor** (`executor.py`) actually emits the events it's supposed to, that the watchdog actually kills a process, or that a diagnostic report is actually generated when a real phase fails.

- `test_instrumentation.py`: All "instrumentation" tests manually call `debug_log()` in the test body and then verify the log file contains the string. This proves `debug_log()` writes to a file — it does not prove `executor.py` calls `debug_log()` with the right arguments at the right times.
- `test_watchdog.py` (in `tests/sprint/`): Only 2 tests: `test_single_fire_guard_logic` and `test_single_fire_guard_resets_on_growth` — both test pure Python logic (if/else guard), not actual subprocess stall detection.

### Blind Spot 2: No Process-State Capture Implemented

The spec (R3.2) specified detailed process state capture: "PID, PPID, state (R/S/D/Z), RSS, VSZ, open FD count, CPU time, command line. Uses `/proc/PID/status` on Linux, `ps` fallback." The built `DiagnosticCollector` has no `_capture_process_state()` method and doesn't accept a `process` parameter. The process state is entirely absent from the diagnostic bundle and reports.

### Blind Spot 3: DebugLogReader Lives in Test Fixtures, Not Production Code

The spec (R4.4-R4.6) specified `DebugLogReader` as a test infrastructure component in `conftest.py`. The spec's architecture diagram also shows it in the debug_logger module for both tests and auto-analysis. The built `DebugLogReader` lives only in `tests/sprint/diagnostic/conftest.py` — it is test infrastructure, not importable by production code. This means the auto-analysis pipeline (R3.1-R3.13) cannot use `DebugLogReader` to parse the debug log programmatically. The `DiagnosticCollector._read_phase_debug_entries()` reimplements a subset of `DebugLogReader`'s parsing with raw string matching.

### Blind Spot 4: Report Format Completely Changed Without Spec Update

The spec mandated JSON reports (`diagnostic-report.json`) with a versioned schema (`report_version: "1.0"`), machine-parseable structure, and specific fields. The implementation produces Markdown reports (`phase-N-diagnostic.md`). This means any downstream tooling expecting JSON diagnostic reports would break, and the machine-parseability requirement (R3.13) is unmet. There's no evidence of a deliberate decision to change formats — it appears to be an implementation-time interpretation.

### Blind Spot 5: "Assumed Working" Event Coverage in Executor

The executor's `execute_sprint()` does emit `PHASE_BEGIN`, `poll_tick`, `watchdog_triggered`, `phase_complete`, `PHASE_END`, and `diagnostic_report` events. However, R1.6 (config events: `phases_found`, `paths`, `validation_errors`), R1.8 partial (process lifecycle from executor perspective), and R1.13 (tmux events) are absent from the executor. The executor emits 6 event types; the spec specified 13+ distinct event types across 6 components.

---

## Confidence vs Reality Gaps

### Gap 1: Test Count Suggests Coverage; Actual Scope is Narrow

The `tests/sprint/diagnostic/` directory contains 7 test files with seemingly thorough class names (`TestL0DebugLogPipeline`, `TestL0DiagnosticPipeline`, `TestLogToClassificationPipeline`, `TestFullDiagnosticScenarios`, `TestMissingFiles`, `TestCorruptData`). This creates an impression of comprehensive graduated testing. However:

- **L0 tests** test the debug logger, not the sprint pipeline
- **L1 tests** test the `DebugLogReader` parser, not Claude echo integration
- **L2 tests** test collect → classify → report with mock data, not multi-phase execution
- **L3 tests** test the same pipeline with slightly more complex mock scenarios
- **Negative tests** test edge cases of the diagnostic framework, not the 6 failure modes from the spec

The test levels map to **component isolation levels** (unit → integration of diagnostic components), not the spec's **pipeline execution levels** (no-claude → echo → file-ops → analysis).

### Gap 2: Watchdog "Works" in Tests but Untested in Production Path

The executor's watchdog code path (`config.stall_timeout > 0 and ms.stall_seconds > config.stall_timeout and ms.events_received > 0 and not _stall_acted`) is present in `executor.py` but never exercised by any test that runs through `execute_sprint()`. The `test_watchdog.py` tests validate the boolean logic of the guard in isolation. The `test_instrumentation.py` tests validate that `debug_log()` can write "watchdog_triggered" events. Neither tests that the executor actually triggers the watchdog when a subprocess stalls.

### Gap 3: Spec's Given/When/Then Scenarios Were Never Implemented

The spec included 2 concrete Given/When/Then scenarios (E5) that would serve as acceptance tests:
1. L0 pipeline smoke: create shell script phase → run sprint → assert exit 0, result file, debug.log structure
2. LN silent stall: create sleeping script → run with stall-timeout 5 → assert killed within 10s, diagnostic report generated

These would catch all the gaps identified above. Neither scenario was implemented in any test file.

### Gap 4: The `DiagnosticTestHarness` Was Redesigned Away from the Spec

The spec's harness had 3 methods: `create_sprint()`, `run_sprint()`, `analyze_result()`. The built harness has: `simulate_phase_output()`, `simulate_phase_error()`, `emit_debug_events()`, `make_phase_result()`, `get_log_reader()`. This is a fundamentally different tool — it simulates artifacts rather than executing the pipeline. The name "DiagnosticTestHarness" was preserved, creating a false sense of spec compliance.

---

## Evidence Citations

### From the Spec

1. **R2.1**: "Shell script subprocess — Phase task is a shell script (not claude) that writes a properly formatted result file" → No shell script phase exists in any test
2. **R2.2**: "Tests sprint runner only — Validates: subprocess spawns, output file created, result file written, `_determine_phase_status` returns PASS, exit code 0" → No test calls `_determine_phase_status` or `execute_sprint`
3. **R2.16-R2.21**: 6 failure modes with specific test setups (non-existent binary, sleeping script, etc.) → Only `FailureClassifier` unit tests exist, none with actual subprocess simulation
4. **R3.1**: "DiagnosticCollector gathers state on failure — Collects: subprocess spawn status (PID or None), output file existence + size, result file existence + content, debug.log tail (last 50 lines), stderr file contents, process state if still alive" → Built collector gathers monitor state snapshot, output/error tails, and debug log entries, but not subprocess spawn status or process state
5. **R3.2**: "Process state capture — When process still alive: PID, PPID, state (R/S/D/Z), RSS, VSZ, open FD count, CPU time, command line. Uses `/proc/PID/status` on Linux" → Not implemented
6. **R3.10**: "diagnostic-report.json saved — Written to sprint results directory on any non-success outcome" → Built as `phase-N-diagnostic.md` in Markdown
7. **R3.13**: "Machine-parseable — Valid JSON, schema-stable with `report_version: 1.0`" → Report is Markdown, not JSON
8. **R4.2**: "run_sprint(config, timeout, stall_timeout) → DiagnosticResult — Executes `execute_sprint()` with `--debug --no-tmux`" → Method does not exist on built harness
9. **R1.19**: "Component injection — Logger passed to: `execute_sprint()`, `ClaudeProcess.__init__()`, `OutputMonitor.__init__()`, `SprintTUI.__init__()`, tmux functions" → Only executor uses debug logging; other components uninstrumented
10. **Implementation Priority Phase 3**: "DiagnosticTestHarness + DebugLogReader + fixtures → Level 0 pipeline smoke test → Level N negative tests" → Harness built without `run_sprint()`, L0 tests logger not pipeline, LN tests edge cases not failure modes

### From the Built Code

1. `diagnostics.py:FailureCategory` has 5 values vs spec's 7 `FailureMode` values — `SPAWN_FAILURE`, `SILENT_STALL`, `OUTPUT_STALL`, `RESULT_MISSING`, `EXIT_CODE_ERROR` were collapsed into `STALL`, `CRASH`, `ERROR`
2. `diagnostics.py:FailureClassifier.classify()` returns `FailureCategory` (single enum) vs spec's `tuple[FailureMode, float]` (enum + confidence)
3. `diagnostics.py:ReportGenerator.generate()` returns `str` (Markdown) vs spec's `dict` (JSON)
4. `executor.py:execute_sprint()` calls `DiagnosticCollector(config)` then `collector.collect(phase, phase_result, monitor.state)` — matches built API, not spec API
5. `conftest.py:DiagnosticTestHarness` has `simulate_phase_output()`, `emit_debug_events()` etc. — data injection methods, not execution methods
6. `test_level_0.py:TestL0DebugLogPipeline` asserts `reader.version == DEBUG_LOG_VERSION` and `reader.events("poll_tick")` — tests the reader, not the pipeline
