---
spec_source: .dev/releases/current/v2.03-CLI-Sprint-diag/spec-sprint-diagnostic-framework.md
generated: 2026-03-04T18:00:00Z
generator: sc:roadmap
functional_requirements: 41
nonfunctional_requirements: 7
total_requirements: 48
domains_detected: [backend, security, performance, documentation]
complexity_score: 0.68
complexity_class: MEDIUM
risks_identified: 8
dependencies_identified: 12
success_criteria_count: 5
extraction_mode: chunked (3 chunks)
---

# Extraction: Sprint CLI Diagnostic Testing Framework v1.0

## Project Overview

**Title**: Sprint CLI Diagnostic Testing Framework
**Version**: 1.0
**Summary**: A diagnostic framework for `superclaude sprint run` that addresses silent stalling via debug instrumentation (`--debug` flag producing `debug.log`), a watchdog mechanism (`--stall-timeout` / `--stall-action`), auto-analysis on failure with structured diagnostic reports, and a graduated test framework (Levels 0-3 + Negative tests) with a reusable test harness.

---

## Functional Requirements

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-001 | `--debug` CLI boolean flag on `sprint run`, defaults to False | backend | P0 | L40 (R1.1) |
| FR-002 | `debug.log` file creation in sprint results directory alongside `execution-log.jsonl` using Python `logging` at DEBUG level | backend | P0 | L42 (R1.2) |
| FR-003 | Log format version header: first line `# debug-log-version: 1.0` | backend | P0 | L43 (R1.3) |
| FR-004 | Line-buffered writes — every log entry flushed to disk before logging call returns (crash-safe) | backend | P0 | L44 (R1.4) |
| FR-005 | Existing JSONL and Markdown logs unchanged when `--debug` is active | backend | P1 | L45 (R1.5) |
| FR-006 | Config component logging: phase discovery, path resolution, validation results | backend | P0 | L50 (R1.6) |
| FR-007 | Executor poll loop tick logging every 0.5s: phase, PID, poll_result, elapsed, output_bytes, growth_rate, stall_seconds, stall_status | backend | P0 | L51 (R1.7) |
| FR-008 | Executor phase lifecycle logging: PHASE_BEGIN (phase number, file) and PHASE_END (status, exit_code, duration) | backend | P0 | L52 (R1.8) |
| FR-009 | Process subprocess lifecycle logging: spawn (PID, command array, env delta), signal_sent, exit (code, was_timeout) | backend | P0 | L53 (R1.9) |
| FR-010 | Process stdout/stderr file handle logging: paths, opens, closes | backend | P0 | L54 (R1.10) |
| FR-011 | Monitor file I/O event logging: output_file_stat, read_bytes, signals_extracted | backend | P1 | L55 (R1.11) |
| FR-012 | TUI state transition logging: tui_start, tui_update, tui_live_failed (with exception), tui_stop | backend | P1 | L56 (R1.12) |
| FR-013 | Tmux session operation logging: session_create, pane_split, tail_update, attach, detach, kill | backend | P1 | L57 (R1.13) |
| FR-014 | `--stall-timeout N` CLI option: integer seconds, default 120 for normal runs, 0 = disabled | backend | P0 | L71 (R1.14) |
| FR-015 | `--stall-action` CLI option: enum `warn` (log + continue) or `kill` (log + terminate), default: `warn` | backend | P0 | L72 (R1.15) |
| FR-016 | Watchdog integration: when stall_seconds > stall_timeout and stall_timeout > 0, execute stall action with full process state logged | backend | P0 | L73 (R1.16) |
| FR-017 | Watchdog acts once per stall: reset stall counter after action, no repeated warnings | backend | P1 | L74 (R1.17) |
| FR-018 | Single `logging.Logger` instance named `superclaude.sprint.debug` with FileHandler | backend | P0 | L80 (R1.18) |
| FR-019 | Logger component injection into execute_sprint, ClaudeProcess, OutputMonitor, SprintTUI, tmux functions | backend | P0 | L81 (R1.19) |
| FR-020 | Phase correlation markers: PHASE_BEGIN/PHASE_END entries bracket all events per phase for log slicing | backend | P0 | L82 (R1.20) |
| FR-021 | No-op when `--debug` absent: NullHandler, zero overhead | backend | P1 | L83 (R1.21) |
| FR-022 | Level 0 test: shell script subprocess (no claude), writes PASS result file, validates pipeline only | backend | P0 | L91-L98 (R2.1-R2.5) |
| FR-023 | Level 1 test: 1 phase trivial claude echo task, validates basic claude integration | backend | P1 | L101-L107 (R2.6-R2.9) |
| FR-024 | Level 2 test: 2 phases file read/write, validates multi-phase sequencing | backend | P1 | L110-L114 (R2.10-R2.12) |
| FR-025 | Level 3 test: 2-3 phases lightweight code analysis, validates halt-on-failure | backend | P1 | L117-L122 (R2.13-R2.15) |
| FR-026 | Negative test: SPAWN_FAILURE — non-existent binary → PhaseStatus.ERROR | backend | P0 | L127 (R2.16) |
| FR-027 | Negative test: SILENT_STALL — script sleeps, stall-timeout kills → classified correctly | backend | P0 | L128 (R2.17) |
| FR-028 | Negative test: OUTPUT_STALL — writes then sleeps → classified correctly | backend | P0 | L129 (R2.18) |
| FR-029 | Negative test: RESULT_MISSING — writes output, no result file → classified | backend | P1 | L130 (R2.19) |
| FR-030 | Negative test: EXIT_CODE_ERROR — exit code 1 → classified | backend | P1 | L131 (R2.20) |
| FR-031 | Negative test: TIMEOUT — exceeds timeout → classified | backend | P1 | L132 (R2.21) |
| FR-032 | All diagnostic tests run with `--debug` enabled and `--no-tmux` | backend | P1 | L138-L142 (R2.22-R2.24) |
| FR-033 | DiagnosticCollector gathers state on failure: spawn status, output/result/stderr files, debug.log tail, process state | backend | P0 | L150-L154 (R3.1-R3.3) |
| FR-034 | Process state capture when alive: PID, PPID, state, RSS, VSZ, open FDs, CPU time, command line via /proc or ps fallback | backend | P1 | L152 (R3.2) |
| FR-035 | FailureClassifier with 6 failure modes: SPAWN_FAILURE, SILENT_STALL, OUTPUT_STALL, RESULT_MISSING, EXIT_CODE_ERROR, TIMEOUT | backend | P0 | L157-L165 (R3.4-R3.9) |
| FR-036 | diagnostic-report.json generation on any non-success outcome with version, evidence, root cause, recommended actions | backend | P0 | L168-L173 (R3.10-R3.13) |
| FR-037 | DiagnosticTestHarness: create_sprint(), run_sprint(), analyze_result() methods | backend | P0 | L181-L186 (R4.1-R4.3) |
| FR-038 | DebugLogReader: parse debug.log into DebugEvent objects, filter by component/phase/level, slice by phase | backend | P0 | L189-L194 (R4.4-R4.6) |
| FR-039 | Pytest tmp_path based fixtures with minimal tasklist-index.md format | backend | P1 | L198-L201 (R4.7-R4.9) |
| FR-040 | Test files in tests/sprint/diagnostic/ directory with conftest.py and 5 test files | backend | P1 | L204-L208 (R4.10-R4.11) |
| FR-041 | Tmux flag forwarding: --debug, --stall-timeout, --stall-action forwarded via _build_foreground_command | backend | P1 | L527-L535 (tmux) |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | Level 0 tests complete in <5s | performance | <5s wall time | L96 (R2.4) |
| NFR-002 | Level 1 tests complete in <30s | performance | <30s wall time | L105 (R2.8) |
| NFR-003 | Level 2 tests complete in <60s total | performance | <60s wall time | L113 (R2.12) |
| NFR-004 | Level 3 tests complete in <120s total | performance | <120s wall time | L121 (R2.15) |
| NFR-005 | CI compatibility: L0 tests run without claude binary; L1-3 and negative tests skip gracefully | reliability | clean skip messages | L29 (R0.3) |
| NFR-006 | Environment isolation: save/restore CLAUDECODE, TMUX env vars, signal handlers; verify no orphaned children | reliability | zero leaked state | L30 (R0.4) |
| NFR-007 | Backward compatibility: all new fields have defaults matching current behavior; existing tests pass without modification | maintainability | zero breaking changes | L1493-L1505 |

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|----------------------|
| DEP-001 | `claude` binary must be available for L1-L3 tests | external | FR-023, FR-024, FR-025 |
| DEP-002 | Python `logging` module (stdlib) | external | FR-001, FR-002, FR-018 |
| DEP-003 | pytest and pytest markers for test selection | external | FR-022, FR-040, NFR-005 |
| DEP-004 | `/proc` filesystem (Linux) or `ps` command for process state capture | external | FR-034 |
| DEP-005 | debug.log must exist for DebugLogReader operations | internal | FR-038 depends on FR-002 |
| DEP-006 | Logger must be set up before executor poll loop | internal | FR-018 → FR-007 |
| DEP-007 | Logger injection must reach all components | internal | FR-019 → FR-006 through FR-013 |
| DEP-008 | Watchdog requires monitor state for stall detection | internal | FR-016 depends on OutputMonitor |
| DEP-009 | DiagnosticCollector requires debug.log + process artifacts | internal | FR-033 depends on FR-002, FR-009 |
| DEP-010 | FailureClassifier requires DiagnosticBundle from Collector | internal | FR-035 depends on FR-033 |
| DEP-011 | Negative tests require watchdog to be functional | internal | FR-027 depends on FR-014, FR-015 |
| DEP-012 | L0 test requires test harness infrastructure | internal | FR-022 depends on FR-037 |

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|------------|
| SC-001 | Developer can run `sprint run --debug` and get debug.log showing subprocess state at every 0.5s tick | FR-001, FR-002, FR-007 (US1) | Yes |
| SC-002 | Developer can run with `--stall-timeout 60 --stall-action kill` and sprint auto-terminates with diagnostic report | FR-014, FR-015, FR-016, FR-036 (US2) | Yes |
| SC-003 | `uv run pytest tests/sprint/diagnostic/ -v` shows graduated test levels pass/fail with auto-generated reports | FR-022 through FR-036 (US3) | Yes |
| SC-004 | L0 pipeline smoke test passes without claude binary, validates runner pipeline | FR-022, NFR-005 (US4, US5) | Yes |
| SC-005 | All new features are backward-compatible — existing tests and CLI behavior unaffected | NFR-007 | Yes |

## Risk Register

| ID | Description | Probability | Impact | Affected Requirements | Source |
|----|-------------|-------------|--------|----------------------|--------|
| RISK-001 | Poll tick logging at 0.5s interval generates excessive disk I/O under long-running phases | Medium | Medium | FR-007 | inferred |
| RISK-002 | Process state capture via /proc may fail on non-Linux or in sandboxed environments | Medium | Low | FR-034, NFR-006 | inferred |
| RISK-003 | Fake claude script in L0 tests may not faithfully reproduce real subprocess behavior | Low | Medium | FR-022, FR-037 | inferred |
| RISK-004 | Watchdog stall detection relies on OutputMonitor growth rate which may have edge cases | Medium | High | FR-016 | L351 (R7.1) |
| RISK-005 | TUI live_failed=True flag suppresses errors silently — debug logging may mask underlying TUI issues | Low | Medium | FR-012 | L18 (Root cause 4) |
| RISK-006 | Environment variable manipulation in test harness (PATH override) may cause test flakiness | Medium | Medium | FR-037, NFR-006 | inferred |
| RISK-007 | debug.log parsing in DebugLogReader uses regex that may break on unusual log content | Low | Low | FR-038 | inferred |
| RISK-008 | Stall-timeout working independently of --debug flag (per R7.1 recommendation) increases scope | Medium | Medium | FR-014, FR-016 | L351 (R7.1) |

## Domain Distribution

| Domain | Percentage | Requirements |
|--------|-----------|--------------|
| Backend | 78% | FR-001 through FR-041, NFR-005 through NFR-007 |
| Performance | 10% | NFR-001 through NFR-004 |
| Security | 7% | FR-034 (process state), NFR-006 (isolation) |
| Documentation | 5% | FR-003 (log format), FR-036 (report schema) |

## Completeness Verification

| Pass | Result | Notes |
|------|--------|-------|
| Source Coverage | PASS | All requirement-indicating patterns in R0-R5 sections mapped to extracted items |
| Anti-Hallucination | PASS | Every FR/NFR traces to specific spec line ranges |
| Section Coverage | PASS | All sections tagged FR_BLOCK (R0-R4) and SUCCESS (R5) were processed |
| Count Reconciliation | PASS | 41 FRs + 7 NFRs = 48 total requirements |
