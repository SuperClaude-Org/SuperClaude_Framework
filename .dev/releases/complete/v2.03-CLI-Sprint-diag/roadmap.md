---
spec_source: .dev/releases/current/v2.03-CLI-Sprint-diag/spec-sprint-diagnostic-framework.md
generated: 2026-03-04T18:00:00Z
generator: sc:roadmap
complexity_score: 0.68
complexity_class: MEDIUM
domain_distribution:
  backend: 78
  performance: 10
  security: 7
  documentation: 5
primary_persona: backend
consulting_personas: [analyzer, qa]
milestone_count: 7
milestone_index:
  - id: M1
    title: Foundation — Debug Logger Module
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 5
    risk_level: Low
  - id: M2
    title: Debug Instrumentation — Event Coverage
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 6
    risk_level: Medium
  - id: M3
    title: Watchdog Mechanism
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 4
    risk_level: Medium
  - id: M4
    title: Validation Checkpoint 1
    type: TEST
    priority: P2
    dependencies: [M2, M3]
    deliverable_count: 3
    risk_level: Low
  - id: M5
    title: Diagnostics & Failure Classification
    type: FEATURE
    priority: P0
    dependencies: [M2, M3]
    deliverable_count: 5
    risk_level: Medium
  - id: M6
    title: Test Infrastructure & Graduated Tests
    type: TEST
    priority: P1
    dependencies: [M5]
    deliverable_count: 7
    risk_level: Medium
  - id: M7
    title: Integration Validation & Acceptance
    type: TEST
    priority: P1
    dependencies: [M4, M6]
    deliverable_count: 4
    risk_level: Low
total_deliverables: 34
total_risks: 8
estimated_phases: 4
validation_score: 0.94
validation_status: PASS
---

# Roadmap: Sprint CLI Diagnostic Testing Framework v1.0

## Overview

This roadmap addresses the critical problem of `superclaude sprint run` stalling indefinitely with zero observability. The approach is structured in 7 milestones following the spec's implementation priority: first establish debug logging infrastructure (M1), then instrument all sprint components (M2) and build the watchdog mechanism (M3) in parallel, validate the core instrumentation (M4), build the failure analysis pipeline (M5), implement the graduated test framework (M6), and perform final integration validation (M7).

The spec is heavily backend-focused (78%) with a focused scope: 7 modified source files, 2 new source modules, and 9 new test files. All changes are additive with backward-compatible defaults — existing behavior is preserved when `--debug` is not specified.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation — Debug Logger Module | FEATURE | P0 | S | None | 5 | Low |
| M2 | Debug Instrumentation — Event Coverage | FEATURE | P0 | M | M1 | 6 | Medium |
| M3 | Watchdog Mechanism | FEATURE | P0 | S | M1 | 4 | Medium |
| M4 | Validation Checkpoint 1 | TEST | P2 | XS | M2, M3 | 3 | Low |
| M5 | Diagnostics & Failure Classification | FEATURE | P0 | M | M2, M3 | 5 | Medium |
| M6 | Test Infrastructure & Graduated Tests | TEST | P1 | L | M5 | 7 | Medium |
| M7 | Integration Validation & Acceptance | TEST | P1 | S | M4, M6 | 4 | Low |

## Dependency Graph

```
M1 → M2 ──┐
           ├→ M4 ──────────────→ M7
M1 → M3 ──┘                      ↑
                                  │
M2, M3 → M5 → M6 ────────────────┘
```

---

## M1: Foundation — Debug Logger Module

### Objective

Create the `debug_logger.py` module with crash-safe file handler, structured formatter, and reader class. Establish the logging contract that all other milestones depend on.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `_FlushHandler` class extending `logging.FileHandler` | Calls `flush()` after every `emit()`. Verified by test writing log → crashing → checking disk. |
| D1.2 | `_DebugFormatter` class | Produces format: `timestamp LEVEL [component] message`. ISO8601 with milliseconds. |
| D1.3 | `setup_debug_logger(config)` function | Returns `Logger("superclaude.sprint.debug")`. Writes version header. NullHandler when `config.debug=False`. |
| D1.4 | `debug_log()` helper function | Emits structured entries: `event k1=v1 k2=v2`. No-op when logger disabled (zero overhead check). |
| D1.5 | `SprintConfig` model additions | 4 new fields: `debug`, `stall_timeout`, `stall_action`, `phase_timeout`. 1 property: `debug_log_path`. All with backward-compatible defaults. |

### Dependencies

- None (foundation milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Logger naming conflicts with existing loggers | Low | Low | Use unique name `superclaude.sprint.debug`, set `propagate=False` |

---

## M2: Debug Instrumentation — Event Coverage

### Objective

Inject the debug logger into all 6 sprint components (executor, process, monitor, TUI, tmux, config) and emit structured events for every state transition specified in R1.6-R1.13.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `executor.py` instrumentation | `PHASE_BEGIN`, `poll_tick` (every 0.5s), `phase_complete`, `PHASE_END` events. Phase correlation markers bracket all per-phase events. |
| D2.2 | `process.py` instrumentation | `spawn` (PID, command array, env delta), `files_opened`, `signal_sent`, `exit` events. |
| D2.3 | `monitor.py` instrumentation | `output_file_stat`, `signal_extracted` events when signals detected. |
| D2.4 | `tui.py` instrumentation | `tui_start`, `tui_update`, `tui_live_failed` (with exception), `tui_stop` events. |
| D2.5 | `tmux.py` flag forwarding | `--debug`, `--stall-timeout`, `--stall-action` forwarded via `_build_foreground_command()`. |
| D2.6 | `commands.py` CLI options | 3 new Click options: `--debug` (flag), `--stall-timeout` (int), `--stall-action` (choice). Passed to `SprintConfig`. |

### Dependencies

- M1: Debug logger module must exist for injection

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Poll tick logging at 0.5s generates excessive I/O | Medium | Medium | Log at DEBUG level only; NullHandler when disabled ensures zero overhead in normal mode |
| TUI live_failed mask may hide underlying errors | Low | Medium | Debug log captures the exception object in `tui_live_failed` event |

---

## M3: Watchdog Mechanism

### Objective

Implement stall detection and response (warn or kill) that works independently of `--debug` flag, solving the core user problem of indefinite stalls.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Stall timeout check in executor poll loop | When `stall_seconds > stall_timeout` and `stall_timeout > 0`, triggers configured action. |
| D3.2 | `warn` action implementation | Logs WARNING with full process state. Continues execution. Resets stall counter (acts once per stall). |
| D3.3 | `kill` action implementation | Logs WARNING + terminates process (SIGTERM → SIGKILL). Sets `_timed_out=True`. Breaks poll loop. |
| D3.4 | Single-fire guard | `_stall_acted` flag prevents repeated warn/kill for same stall period. Resets on output growth. |

### Dependencies

- M1: SprintConfig fields (`stall_timeout`, `stall_action`) must exist

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Watchdog relies on OutputMonitor growth rate edge cases | Medium | High | Watchdog checks `ms.stall_seconds` from monitor; stall_seconds is monotonically increasing when no growth |
| Stall-timeout as independent feature increases scope | Medium | Medium | Spec R7.1 recommends this; keep implementation minimal — just the poll-loop check |

---

## M4: Validation Checkpoint 1

### Objective

Validate M2 and M3 deliverables through manual testing and basic assertions before building the full diagnostics pipeline.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Debug log format validation | Run `sprint run --debug` manually. Verify: version header present, PHASE_BEGIN/END markers, poll_tick events with all fields, spawn event with PID. |
| D4.2 | Watchdog validation | Run with `--stall-timeout 10 --stall-action kill` on a task that stalls. Verify process terminates within 15s. |
| D4.3 | Backward compatibility validation | Run existing `tests/sprint/test_*.py` suite. All pass without modification. |

### Dependencies

- M2: All instrumentation complete
- M3: Watchdog implemented

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Low risk — validation only | Low | Low | N/A |

---

## M5: Diagnostics & Failure Classification

### Objective

Create `diagnostics.py` module with `DiagnosticCollector`, `FailureClassifier`, `ReportGenerator`, and integrate diagnostic report generation into the executor on failure.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | `DiagnosticBundle` dataclass | Contains: phase_number, subprocess_spawned, subprocess_pid, output_file_exists, output_bytes, result_file_exists, result_file_content, exit_code, stall_seconds, was_stall_killed, debug_log_tail, stderr_contents, process_state. |
| D5.2 | `DiagnosticCollector.collect()` | Gathers all diagnostic state from sprint artifacts. Process state via `/proc` with `ps` fallback. |
| D5.3 | `FailureClassifier.classify()` | Returns `(FailureMode, confidence)`. Priority order: SPAWN_FAILURE > TIMEOUT > SILENT_STALL > OUTPUT_STALL > EXIT_CODE_ERROR > RESULT_MISSING > UNKNOWN. |
| D5.4 | `ReportGenerator.generate()` + `.write()` | Produces `diagnostic-report.json` with version 1.0, evidence dict, suggested root cause, recommended actions list. |
| D5.5 | Executor integration | On phase failure when `config.debug=True`: collect → classify → suggest → generate → write report. Best-effort (exceptions caught). |

### Dependencies

- M2: Debug events must exist for collector to read debug.log tail
- M3: Watchdog `was_stall_killed` flag needed in bundle

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Process state capture fails in sandboxed environments | Medium | Low | ps fallback + graceful None return |
| FailureClassifier heuristics may misclassify edge cases | Medium | Medium | Confidence scoring allows downstream tools to assess reliability |

---

## M6: Test Infrastructure & Graduated Tests

### Objective

Build the `DiagnosticTestHarness` and implement all 5 test files: Level 0 (pipeline smoke), Level 1-3 (graduated claude tests), and Level N (negative/failure mode tests).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | `DiagnosticTestHarness` class | `create_sprint()` generates temp dirs with tasklist + phases. `run_sprint()` executes with PATH override for fake claude. `analyze_result()` runs collector + classifier. |
| D6.2 | `DebugLogReader` integration in test fixtures | `debug_log_reader` fixture factory. Supports filter by component/phase/level. `phase_events()` slicing. |
| D6.3 | `tests/sprint/diagnostic/conftest.py` | `diagnostic_harness`, `debug_log_reader`, `requires_claude` fixtures. `PhaseSpec` and `DiagnosticResult` dataclasses. |
| D6.4 | `test_level_0.py` — Pipeline smoke tests | Shell script phase, no claude dependency. Validates: subprocess spawns, output created, result file written, PASS status, debug.log structure. <5s. |
| D6.5 | `test_level_1.py` through `test_level_3.py` | Graduated complexity tests requiring claude binary. L1: echo (<30s), L2: file ops (<60s), L3: analysis + halt-on-failure (<120s). All skip when claude absent. |
| D6.6 | `test_negative.py` — 6 failure mode tests | SPAWN_FAILURE, SILENT_STALL, OUTPUT_STALL, RESULT_MISSING, EXIT_CODE_ERROR, TIMEOUT. Each validates correct classification + diagnostic report generation. |
| D6.7 | Pytest markers | `@pytest.mark.diagnostic` on all. `@pytest.mark.diagnostic_l0` through `@pytest.mark.diagnostic_ln` for per-level selection. |

### Dependencies

- M5: Diagnostics module must exist for test harness to use collector/classifier

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Fake claude via PATH substitution may have edge cases | Low | Medium | Script receives same args as real claude; harness controls environment precisely |
| Environment variable manipulation in tests may cause flakiness | Medium | Medium | Save/restore env in try/finally; use `os.environ.copy()` pattern from spec |
| Tests requiring claude binary may fail in CI | Medium | Low | All L1-L3 + LN tests use `@pytest.mark.skipif` when claude absent |

---

## M7: Integration Validation & Acceptance

### Objective

End-to-end validation that all components work together: debug instrumentation, watchdog, diagnostics, and test framework. Verify all 5 user stories and success criteria.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D7.1 | User story validation | US1-US5 from spec R5 all validated with evidence. Each story traced to passing tests or manual verification. |
| D7.2 | Full test suite pass | `uv run pytest tests/sprint/ -v` passes. Existing tests (test_*.py) + new diagnostic tests all green. |
| D7.3 | Backward compatibility final check | `SprintConfig` with no new flags behaves identically to pre-change behavior. No debug.log created. No watchdog active. |
| D7.4 | File inventory verification | All 7 modified files + 9 new files accounted for per spec File Inventory table. No extraneous files. |

### Dependencies

- M4: Core validation must have passed
- M6: All test infrastructure and tests must be complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Low risk — integration validation | Low | Low | All components individually validated in prior milestones |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Poll tick logging excessive disk I/O | M2 | Medium | Medium | DEBUG level only; NullHandler when disabled | backend |
| R-002 | /proc unavailable in sandboxed/non-Linux environments | M5 | Medium | Low | ps fallback + graceful None return | backend |
| R-003 | Fake claude script doesn't reproduce real behavior | M6 | Low | Medium | Script receives same args; env controlled | qa |
| R-004 | Watchdog stall detection edge cases in growth rate | M3 | Medium | High | stall_seconds is monotonic when no growth; test with LN negative tests | backend |
| R-005 | TUI live_failed masks errors | M2 | Low | Medium | Debug log captures exception in tui_live_failed event | backend |
| R-006 | Test env var manipulation causes flakiness | M6 | Medium | Medium | Save/restore pattern; try/finally; os.environ.copy() | qa |
| R-007 | DebugLogReader regex breaks on unusual content | M6 | Low | Low | Regex covers documented format; edge cases return empty list | backend |
| R-008 | Stall-timeout independence increases scope | M3 | Medium | Medium | Minimal implementation — poll loop check only | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend | analyzer (0.24), qa (0.21), architect (default) | Backend domain 78% → highest confidence 0.38 |
| Template | inline | No templates in local/user tiers | Tier 4 fallback — no project-level templates exist |
| Milestone Count | 7 | 5-7 range (MEDIUM class) | base=5 + floor(4 domains / 2) = 7 |
| Adversarial Mode | none | N/A | No --multi-roadmap or --specs flags |
| Interleave Ratio | 1:2 | 1:3 (LOW), 1:1 (HIGH) | MEDIUM complexity → validation after every 2 work milestones |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Developer runs `sprint run --debug` and gets debug.log with 0.5s-interval subprocess state | M1, M2 | Yes |
| SC-002 | `--stall-timeout 60 --stall-action kill` auto-terminates and produces diagnostic report | M3, M5 | Yes |
| SC-003 | `uv run pytest tests/sprint/diagnostic/ -v` shows graduated pass/fail with auto-reports | M6, M7 | Yes |
| SC-004 | L0 pipeline smoke test passes without claude binary | M6 (D6.4) | Yes |
| SC-005 | All changes backward-compatible — existing tests and CLI behavior unaffected | M1, M7 | Yes |
