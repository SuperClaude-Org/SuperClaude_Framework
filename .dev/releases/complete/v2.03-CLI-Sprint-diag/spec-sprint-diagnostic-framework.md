# Sprint CLI Diagnostic Testing Framework — Specification v1.0

> **Status**: Draft (Post-Architecture Design)
> **Date**: 2026-03-04 (Updated)
> **Panel**: Wiegers (Requirements), Nygard (Reliability), Fowler (Architecture), Crispin (Testing), Adzic (Examples)
> **Origin**: Brainstorm session — user reports `superclaude sprint run` stalls silently with no diagnostic output

---

## Problem Statement

`superclaude sprint run` stalls indefinitely with no usable output — on screen or in files. The executor poll loop (`executor.py:86`) waits up to 1h45m with `time.sleep(0.5)` intervals. The output monitor detects "STALLED" status but the executor never acts on it. There is zero observability between "phase started" and "phase completed/failed".

**Root causes identified in codebase analysis**:
1. No debug-level logging exists anywhere in the sprint pipeline
2. No watchdog/stall-timeout mechanism — stall detection is display-only
3. `status` and `logs` subcommands are unimplemented stubs
4. TUI silently dies after first render exception (`_live_failed = True`)
5. No heartbeat-to-action bridge between monitor and executor

---

## R0: Prerequisites & Environment

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R0.1 | `claude` binary availability check | `shutil.which("claude")` called before any diagnostic test that requires it. Tests skip gracefully with `pytest.mark.skipif` when absent. |
| R0.2 | Pytest markers for test selection | `@pytest.mark.diagnostic` on all diagnostic tests. `@pytest.mark.diagnostic_l0` through `@pytest.mark.diagnostic_ln` for per-level selection. |
| R0.3 | CI compatibility | Level 0 tests MUST run without `claude` binary. Levels 1-3 and Negative skip with clear message when `claude` unavailable. |
| R0.4 | Environment isolation | Each test saves/restores: `CLAUDECODE`, `TMUX` env vars, signal handlers (SIGINT/SIGTERM), verifies no orphaned child processes on teardown. |

---

## R1: Debug Instrumentation (`--debug` flag)

### Core Logging

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R1.1 | `--debug` CLI flag | Click boolean option on `sprint run`, defaults to `False` |
| R1.2 | `debug.log` file creation | Created in sprint results directory alongside `execution-log.jsonl`. Uses Python `logging` module at DEBUG level. |
| R1.3 | Log format version header | First line: `# debug-log-version: 1.0` |
| R1.4 | Line-buffered writes | Every log entry flushed to disk before logging call returns. Survives crash. |
| R1.5 | Existing logs unaffected | `--debug` adds a parallel channel only. JSONL and Markdown logs unchanged. |

### Event Coverage

| ID | Component | Events Logged | Fields |
|----|-----------|---------------|--------|
| R1.6 | config | Phase discovery, path resolution, validation results | `phases_found`, `paths`, `validation_errors` |
| R1.7 | executor | Every poll loop tick (per 0.5s interval) | `phase`, `pid`, `poll_result`, `elapsed_s`, `output_bytes`, `growth_rate_bps`, `stall_seconds`, `stall_status` |
| R1.8 | executor | Phase lifecycle | `phase_begin` (with phase number, file), `phase_end` (with status, exit_code, duration) |
| R1.9 | process | Subprocess lifecycle | `spawn` (PID, full command array, env delta), `signal_sent` (signal type), `exit` (code, was_timeout) |
| R1.10 | process | Stdout/stderr file handles | `stdout_path`, `stderr_path`, `files_opened`, `files_closed` |
| R1.11 | monitor | File I/O events | `output_file_stat` (size, mtime), `read_bytes`, `signals_extracted` (task_id, tool, files_changed) |
| R1.12 | tui | State transitions | `tui_start`, `tui_update` (success/failure), `tui_live_failed` (with exception), `tui_stop` |
| R1.13 | tmux | Session operations | `session_create`, `pane_split`, `tail_update` (path), `attach`, `detach`, `kill` |

### Log Entry Schema

Each log entry MUST contain:

```
timestamp (ISO8601 with ms) | level (DEBUG/INFO/WARN/ERROR) | component | event_name | context_dict
```

### Watchdog Mechanism

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R1.14 | `--stall-timeout N` CLI option | Integer seconds. Default: 120 for normal runs, overrideable. 0 = disabled. |
| R1.15 | `--stall-action` CLI option | Enum: `warn` (log WARNING, continue), `kill` (log + terminate process). Default: `warn`. |
| R1.16 | Watchdog integration | When `--debug` is active AND `stall_seconds > stall_timeout` AND `stall_timeout > 0`: execute stall action. Log full process state at WARNING level before action. |
| R1.17 | Watchdog acts once per stall | After action taken, reset stall counter. Don't repeatedly warn/kill for the same stall period. |

### Logger Architecture

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R1.18 | Single `logging.Logger` instance | Named `superclaude.sprint.debug`, configured with FileHandler to `debug.log` |
| R1.19 | Component injection | Logger passed to: `execute_sprint()`, `ClaudeProcess.__init__()`, `OutputMonitor.__init__()`, `SprintTUI.__init__()`, tmux functions. Each uses `logger.debug(msg, extra={"component": "..."})` |
| R1.20 | Phase correlation markers | `PHASE_BEGIN phase=N` and `PHASE_END phase=N` entries bracket all events within a phase. Enables log slicing by phase. |
| R1.21 | No-op when `--debug` absent | Logger set to `NullHandler` when `--debug` not specified. Zero overhead. |

---

## R2: Diagnostic Test Framework

### Level 0 — Pipeline Smoke Test (no `claude` dependency)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R2.1 | Shell script subprocess | Phase task is a shell script (not claude) that writes a properly formatted result file with `status: PASS` and `EXIT_RECOMMENDATION: CONTINUE` |
| R2.2 | Tests sprint runner only | Validates: subprocess spawns, output file created, result file written, `_determine_phase_status` returns PASS, exit code 0 |
| R2.3 | No `claude` binary required | Uses a test harness that substitutes a shell script for the claude command |
| R2.4 | Max duration assertion | Must complete in <5s. Fails if exceeded. |
| R2.5 | Debug log validation | Asserts: `debug.log` exists, contains `PHASE_BEGIN`, contains `spawn` event with PID, contains `PHASE_END` |

### Level 1 — Claude Echo Test (~2-5s per phase)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R2.6 | 1 phase, trivial claude task | Prompt: `"Respond with exactly: status: PASS\nEXIT_RECOMMENDATION: CONTINUE"` |
| R2.7 | Validates basic claude integration | Subprocess spawns, produces output, exits 0 |
| R2.8 | Max duration assertion | Must complete in <30s. |
| R2.9 | Requires `claude` binary | `@pytest.mark.skipif(not shutil.which("claude"))` |

### Level 2 — File Operation Test (~10-15s per phase)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R2.10 | 2 phases, file read/write tasks | Phase 1: Read a provided file, summarize to result. Phase 2: Read Phase 1 output, confirm. |
| R2.11 | Validates multi-phase sequencing | Both phases pass, phase 2 runs after phase 1, sequential ordering correct |
| R2.12 | Max duration assertion | Must complete in <60s total. |

### Level 3 — Analysis Test (~30s per phase)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R2.13 | 2-3 phases, lightweight code analysis | Tasks analyze a small Python file for issues |
| R2.14 | Validates halt-on-failure | If Phase 2 configured to fail, Phase 3 must not execute |
| R2.15 | Max duration assertion | Must complete in <120s total. |

### Level N — Negative Tests (failure mode coverage)

| ID | Failure Mode | Test Setup | Expected Behavior |
|----|-------------|-----------|-------------------|
| R2.16 | SPAWN_FAILURE | Point to non-existent binary | `PhaseStatus.ERROR`, diagnostic report classifies as `SPAWN_FAILURE` |
| R2.17 | SILENT_STALL | Script that sleeps indefinitely, `--stall-timeout 5 --stall-action kill` | Process killed within 10s, classified as `SILENT_STALL` |
| R2.18 | OUTPUT_STALL | Script that writes initial output then sleeps | Classified as `OUTPUT_STALL` |
| R2.19 | RESULT_MISSING | Script that writes output but no result file | `PhaseStatus.PASS_NO_REPORT` or `ERROR`, classified as `RESULT_MISSING` |
| R2.20 | EXIT_CODE_ERROR | Script that exits with code 1 | `PhaseStatus.ERROR`, classified as `EXIT_CODE_ERROR` |
| R2.21 | TIMEOUT | Script that runs longer than short test timeout | `PhaseStatus.TIMEOUT`, classified as `TIMEOUT` |

### All Diagnostic Tests

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R2.22 | `--debug` always enabled | Every diagnostic run produces a `debug.log` |
| R2.23 | `--no-tmux` always enabled | Direct execution, no tmux dependency |
| R2.24 | Debug log validated on every run | Assertions on debug.log structure (version header, phase markers, spawn events) |

---

## R3: Auto-Analysis on Failure

### Diagnostic Collection

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R3.1 | `DiagnosticCollector` gathers state on failure | Collects: subprocess spawn status (PID or None), output file existence + size, result file existence + content, debug.log tail (last 50 lines), stderr file contents, process state if still alive |
| R3.2 | Process state capture | When process still alive: PID, PPID, state (R/S/D/Z), RSS, VSZ, open FD count, CPU time, command line. Uses `/proc/PID/status` on Linux, `ps` fallback. |
| R3.3 | `DiagnosticBundle` dataclass | Structured container for all collected diagnostic data. Decouples collection from analysis. |

### Failure Classification

| ID | Mode | Detection Logic | Suggested Root Cause |
|----|------|----------------|---------------------|
| R3.4 | `SPAWN_FAILURE` | `subprocess_pid is None` OR spawn event missing from debug.log | "claude binary not found, permission denied, or command construction error" |
| R3.5 | `SILENT_STALL` | PID exists, output_bytes == 0, stall_seconds > threshold | "Subprocess started but produced no output — check command construction, --print mode, or permission flag syntax" |
| R3.6 | `OUTPUT_STALL` | PID exists, output_bytes > 0, growth_rate == 0, stall > threshold | "Subprocess was producing output but stopped — possible claude hang, resource exhaustion, or blocked I/O" |
| R3.7 | `RESULT_MISSING` | Exit code 0, output exists, result file absent | "Claude completed but did not write result file — prompt may not include completion protocol instructions" |
| R3.8 | `EXIT_CODE_ERROR` | Exit code != 0 and != 124 | "Subprocess failed with exit code N — check stderr for error details" |
| R3.9 | `TIMEOUT` | Exit code 124 OR `_timed_out` flag set | "Phase exceeded timeout — task too complex for allocated turns, or subprocess hung" |

### Report Generation

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R3.10 | `diagnostic-report.json` saved | Written to sprint results directory on any non-success outcome |
| R3.11 | Report trigger | Generated when: test assertion fails, phase status is failure/error/timeout, or stall-timeout triggers |
| R3.12 | Recommended actions included | Each failure mode maps to 2-3 specific debugging steps the user can take |
| R3.13 | Machine-parseable | Valid JSON, schema-stable with `"report_version": "1.0"` |

---

## R4: Test Infrastructure

### DiagnosticTestHarness

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R4.1 | `create_sprint(phases: list[PhaseSpec]) -> SprintConfig` | Generates temp directory with `tasklist-index.md` + phase files. PhaseSpec defines: name, task content, expected behavior. |
| R4.2 | `run_sprint(config, timeout, stall_timeout) -> DiagnosticResult` | Executes `execute_sprint()` with `--debug --no-tmux`, captures all outputs. DiagnosticResult wraps SprintResult + debug.log path + diagnostic report if failure. |
| R4.3 | `analyze_result(result) -> DiagnosticReport` | Runs `DiagnosticCollector` + classifier + root cause suggestion. Always produces a report (even on success, for validation). |

### DebugLogReader

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R4.4 | Parse `debug.log` into `DebugEvent` objects | Each event: timestamp, level, component, event_name, context dict |
| R4.5 | Filter by component/phase/level | `reader.filter(component="executor", phase=2, level="WARN")` |
| R4.6 | Slice by phase | `reader.phase_events(phase=1)` returns events between PHASE_BEGIN and PHASE_END |

### Fixture Generation

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R4.7 | Pytest `tmp_path` based | All fixtures created in temporary directories, auto-cleaned |
| R4.8 | Minimal `tasklist-index.md` format | See Example E1 below |
| R4.9 | Shell script phases for L0/LN | Executable scripts that simulate success/failure conditions |

### Project Location

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R4.10 | `tests/sprint/diagnostic/` directory | Contains: `conftest.py` (harness fixtures), `test_level_0.py`, `test_level_1.py`, `test_level_2.py`, `test_level_3.py`, `test_negative.py` |
| R4.11 | Shared fixtures in `conftest.py` | `diagnostic_harness`, `debug_log_reader`, `requires_claude` marker auto-application |

---

## R5: User Stories

| # | Story | Validates |
|---|-------|-----------|
| US1 | As a developer debugging a stall, I run `superclaude sprint run <path> --debug` and get a `debug.log` showing subprocess state at every 0.5s tick, enabling me to identify exactly where execution stopped. | R1.* |
| US2 | As a developer debugging a stall, I run with `--stall-timeout 60 --stall-action kill` and the sprint auto-terminates after 60s of no output, producing a diagnostic report with root cause suggestions. | R1.14-R1.17, R3.* |
| US3 | As a developer validating the pipeline, I run `uv run pytest tests/sprint/diagnostic/ -v` and see graduated test levels pass/fail with auto-generated diagnostic reports on failure. | R2.*, R3.* |
| US4 | As a developer investigating my current stall, I run L0 (pipeline smoke). If it passes, the runner works and the problem is in my tasklist or claude interaction. If it fails, the diagnostic report tells me which stage broke. | R2.1-R2.5, R3.* |
| US5 | As a CI pipeline, I run `uv run pytest -m diagnostic_l0` and get pipeline validation without requiring `claude` binary installation. | R0.1-R0.3, R2.1-R2.5 |

---

## R6: Concrete Examples

### E1: Minimal Test Fixture (tasklist-index.md)

```markdown
# Diagnostic Test Sprint

1. [Phase 1](phase-1-tasklist.md)
```

**phase-1-tasklist.md** (for L0 shell script test):
```markdown
# Phase 1: Pipeline Smoke Test
## Tasks
- T01.01: Write PASS status to result file
```

### E2: Debug Log Output

```
# debug-log-version: 1.0
2026-03-04T10:15:00.001Z INFO  [config] config_loaded phases_found=3 release_dir=/path/to/release
2026-03-04T10:15:00.050Z INFO  [executor] sprint_start total_phases=3 debug=True stall_timeout=120
2026-03-04T10:15:00.051Z INFO  [executor] PHASE_BEGIN phase=1 file=phase-1-tasklist.md
2026-03-04T10:15:00.100Z INFO  [process] spawn pid=12345 cmd=["claude","--print","--dangerously-skip-permissions","--no-session-persistence","--max-turns","50","--output-format","text","-p","..."] env_delta={"CLAUDECODE":""}
2026-03-04T10:15:00.101Z DEBUG [process] files_opened stdout=/path/to/output.txt stderr=/path/to/errors.txt
2026-03-04T10:15:00.600Z DEBUG [executor] poll_tick phase=1 pid=12345 poll=None elapsed=0.5s output_bytes=0 growth=0bps stall_sec=0.5 stall=active
2026-03-04T10:15:01.100Z DEBUG [executor] poll_tick phase=1 pid=12345 poll=None elapsed=1.0s output_bytes=256 growth=512bps stall_sec=0 stall=active
2026-03-04T10:15:01.600Z DEBUG [executor] poll_tick phase=1 pid=12345 poll=None elapsed=1.5s output_bytes=1024 growth=450bps stall_sec=0 stall=active
...
2026-03-04T10:15:05.100Z DEBUG [monitor] signal_extracted task_id=T01.01 tool=Read files_changed=0
...
2026-03-04T10:15:10.050Z DEBUG [executor] poll_tick phase=1 pid=12345 poll=0 elapsed=10.0s output_bytes=4096 growth=200bps stall_sec=0 stall=active
2026-03-04T10:15:10.051Z INFO  [executor] phase_complete phase=1 status=PASS exit_code=0 duration=10.0s
2026-03-04T10:15:10.052Z INFO  [executor] PHASE_END phase=1
```

### E3: Stall Detection in Debug Log

```
2026-03-04T10:16:30.100Z DEBUG [executor] poll_tick phase=2 pid=12346 poll=None elapsed=90.0s output_bytes=512 growth=0bps stall_sec=60.5 stall=STALLED
2026-03-04T10:16:30.101Z WARN  [executor] stall_detected phase=2 pid=12346 stall_seconds=60.5 output_bytes=512 last_growth=60s_ago stall_timeout=120
...
2026-03-04T10:17:30.100Z WARN  [executor] stall_timeout_exceeded phase=2 pid=12346 stall_seconds=120.5 action=kill
2026-03-04T10:17:30.102Z INFO  [process] signal_sent pid=12346 signal=SIGTERM
2026-03-04T10:17:40.103Z INFO  [process] signal_sent pid=12346 signal=SIGKILL
2026-03-04T10:17:40.150Z INFO  [process] exit pid=12346 code=-9 was_timeout=False was_stall_kill=True
```

### E4: Diagnostic Report

```json
{
  "report_version": "1.0",
  "timestamp": "2026-03-04T10:17:40.200Z",
  "sprint_dir": "/path/to/release",
  "failed_phase": 2,
  "failure_mode": "SILENT_STALL",
  "classification_confidence": 0.95,
  "evidence": {
    "subprocess_spawned": true,
    "subprocess_pid": 12346,
    "output_file_exists": true,
    "output_bytes": 512,
    "result_file_exists": false,
    "exit_code": -9,
    "stall_seconds": 120.5,
    "was_stall_killed": true,
    "debug_log_tail": [
      "2026-03-04T10:17:30.100Z WARN  [executor] stall_timeout_exceeded phase=2 ...",
      "2026-03-04T10:17:30.102Z INFO  [process] signal_sent pid=12346 signal=SIGTERM",
      "..."
    ],
    "stderr_contents": "",
    "process_state_at_kill": {
      "pid": 12346,
      "ppid": 12340,
      "state": "S",
      "rss_kb": 45000,
      "cpu_time_s": 0.3,
      "open_fds": 12,
      "cmdline": "claude --print ..."
    }
  },
  "suggested_root_cause": "Subprocess started and produced 512 bytes of output, then stopped. Possible causes: (1) claude hanging on tool approval prompt despite --dangerously-skip-permissions, (2) claude waiting for input that --print mode doesn't provide, (3) resource exhaustion or rate limiting.",
  "recommended_actions": [
    "Run the phase command manually: claude --print --dangerously-skip-permissions -p '<prompt>' and observe behavior",
    "Check the 512 bytes of output in /path/to/output.txt for clues about where claude stopped",
    "Verify the --dangerously-skip-permissions flag is being passed correctly (check debug.log spawn event for full command)",
    "Try with --max-turns 5 to see if a shorter run completes"
  ]
}
```

### E5: Given/When/Then Scenarios

**Level 0 — Pipeline Smoke**:
```
GIVEN a sprint directory with 1 phase containing a shell script that writes:
      "---\nstatus: PASS\nEXIT_RECOMMENDATION: CONTINUE\n---\nDone." to the result file
WHEN  sprint run executes with --debug --no-tmux --stall-timeout 10
THEN  exit code is 0
  AND result file exists with status: PASS
  AND debug.log contains version header "debug-log-version: 1.0"
  AND debug.log contains PHASE_BEGIN and PHASE_END for phase 1
  AND debug.log contains spawn event with PID
  AND total wall time < 5s
```

**Level N — Silent Stall**:
```
GIVEN a sprint directory with 1 phase containing a shell script that:
      writes "starting..." to stdout then sleeps 3600s
WHEN  sprint run executes with --debug --no-tmux --stall-timeout 5 --stall-action kill
THEN  process is terminated within 10s of start
  AND debug.log contains stall_timeout_exceeded event
  AND diagnostic-report.json exists
  AND report.failure_mode == "SILENT_STALL"
  AND report.recommended_actions is non-empty
```

---

## R7: Remaining Open Questions

| # | Question | Impact | Recommendation |
|---|----------|--------|----------------|
| 1 | Should `--stall-timeout` and `--stall-action` work WITHOUT `--debug`? | If yes, the watchdog becomes a production feature, not just a diagnostic tool. More useful but larger scope. | **Yes** — the watchdog should be independent of debug logging. It solves the core user problem (stalls) regardless of diagnostic needs. |
| 2 | Should `PhaseResult` carry a `debug_summary` field for programmatic access? | Enables downstream tools to access diagnostics without parsing files. Adds coupling. | **Defer** — file-based diagnostic report is sufficient for v1.0. Add structured access in v1.1 if needed. |
| 3 | Should per-phase debug files replace the single debug.log? | Easier to slice by phase, but more files to manage. | **No** — single file with PHASE_BEGIN/END markers + DebugLogReader.phase_events() method. Simpler. |

---

## Implementation Priority

### Phase 1: Unblock the User (Critical Path)
1. **R1.1-R1.5**: `--debug` flag + `debug.log` creation + flush safety
2. **R1.6-R1.13**: Event coverage across all 6 components
3. **R1.18-R1.21**: Logger architecture + injection + phase markers

### Phase 2: Prevent Stalls
4. **R1.14-R1.17**: `--stall-timeout` + `--stall-action` watchdog

### Phase 3: Test Infrastructure
5. **R4.1-R4.11**: DiagnosticTestHarness + DebugLogReader + fixtures
6. **R2.1-R2.5**: Level 0 pipeline smoke test
7. **R2.16-R2.21**: Level N negative tests

### Phase 4: Full Test Coverage
8. **R2.6-R2.15**: Levels 1-3 graduated tests (require claude binary)
9. **R3.1-R3.13**: Auto-analysis + DiagnosticCollector + report generation

---

## Architecture Design (Detailed)

### System Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│ CLI Layer (commands.py)                                                  │
│                                                                          │
│  sprint run INDEX --debug --stall-timeout 120 --stall-action kill        │
│       │                                                                  │
│       ▼                                                                  │
│  load_sprint_config() ──► SprintConfig (+ debug, stall_timeout, etc.)    │
│       │                                                                  │
│       ├── tmux available? ──► launch_in_tmux(config)                     │
│       │                       (forwards --debug/--stall-* flags)         │
│       └── no-tmux ──► execute_sprint(config)                             │
└──────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Executor Layer (executor.py)                                             │
│                                                                          │
│  1. setup_debug_logger(config) ──► logging.Logger                        │
│  2. for each phase:                                                      │
│     a. debug_log("PHASE_BEGIN")                                          │
│     b. ClaudeProcess(config, phase, debug_logger).start()                │
│     c. POLL LOOP:                                                        │
│        ┌─ poll() ─ shutdown? ─ deadline? ─ WATCHDOG ─ TUI ─ sleep(0.5)  │
│        │                                     │                           │
│        │                    stall_timeout exceeded?                       │
│        │                    ├─ action=warn → log WARNING                  │
│        │                    └─ action=kill → terminate() + break          │
│        └─────────────────────────────────────────────────────────────────│
│     d. _determine_phase_status()                                         │
│     e. On failure: DiagnosticCollector → report (if debug)               │
│     f. debug_log("PHASE_END")                                            │
└──────────────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌────────────────┐ ┌─────────────────┐
│ ClaudeProcess    │ │ OutputMonitor  │ │ SprintTUI       │
│ (process.py)     │ │ (monitor.py)   │ │ (tui.py)        │
│                  │ │                │ │                 │
│ debug_log:       │ │ debug_log:     │ │ debug_log:      │
│  - spawn (PID)   │ │  - signal_ext  │ │  - tui_start    │
│  - signal_sent   │ │  - file_stat   │ │  - live_failed  │
│  - files_opened  │ │                │ │  - tui_stop     │
│  - exit          │ │                │ │                 │
└──────────────────┘ └────────────────┘ └─────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Debug Logger (debug_logger.py)                                           │
│                                                                          │
│  setup_debug_logger(config) → Logger("superclaude.sprint.debug")         │
│    ├─ config.debug=True  → FlushingFileHandler("debug.log") + version hdr│
│    └─ config.debug=False → NullHandler (zero overhead)                   │
│                                                                          │
│  debug_log(logger, component, event, **kwargs)                           │
│    → "2026-03-04T10:15:00.001Z INFO  [executor] sprint_start k1=v1 k2=v2│
│                                                                          │
│  DebugLogReader(log_path) — for tests and auto-analysis                  │
│    .events → list[DebugEvent]                                            │
│    .filter(component=, phase=, level=) → list[DebugEvent]                │
│    .phase_events(N) → events between PHASE_BEGIN/END for phase N         │
│    .has_event(name) → bool                                               │
│    .find_event(name) → DebugEvent | None                                 │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Diagnostics (diagnostics.py)                                             │
│                                                                          │
│  DiagnosticCollector.collect(config, phase, ...) → DiagnosticBundle      │
│    Gathers: spawn status, output/result/stderr files, debug.log tail,    │
│             process state from /proc or ps                               │
│                                                                          │
│  FailureClassifier.classify(bundle) → (FailureMode, confidence: float)   │
│    Priority: SPAWN_FAILURE > TIMEOUT > SILENT_STALL > OUTPUT_STALL       │
│              > EXIT_CODE_ERROR > RESULT_MISSING > UNKNOWN                │
│                                                                          │
│  FailureClassifier.suggest(mode) → (root_cause: str, actions: list[str]) │
│    Pre-defined root cause and action templates per failure mode           │
│                                                                          │
│  ReportGenerator.generate(...) → dict                                    │
│  ReportGenerator.write(report, dir) → Path("diagnostic-report.json")     │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ Test Framework (tests/sprint/diagnostic/)                                │
│                                                                          │
│  conftest.py                                                             │
│    DiagnosticTestHarness(tmp_path)                                       │
│      .create_sprint(phases: list[PhaseSpec]) → SprintConfig              │
│      .run_sprint(config, timeout) → DiagnosticResult                     │
│      .analyze_result(config, result) → dict | None                       │
│    Fixtures: diagnostic_harness, debug_log_reader, requires_claude       │
│                                                                          │
│  test_level_0.py — Pipeline smoke (shell script, no claude)              │
│  test_level_1.py — Echo test (trivial claude task)                       │
│  test_level_2.py — File operations (multi-phase)                         │
│  test_level_3.py — Analysis (halt-on-failure)                            │
│  test_negative.py — All 6 failure modes                                  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### Existing File Changes (Diff Plan)

#### models.py — Add 4 fields + 1 property to SprintConfig

```python
@dataclass
class SprintConfig:
    # ... existing fields (index_path through tmux_session_name) ...

    # NEW: Diagnostic fields
    debug: bool = False
    stall_timeout: int = 0       # seconds, 0 = disabled
    stall_action: str = "warn"   # "warn" | "kill"
    phase_timeout: int = 0       # seconds per phase, 0 = computed from max_turns

    # NEW: Computed property
    @property
    def debug_log_path(self) -> Path:
        return self.release_dir / "debug.log"
```

**Backward compatibility**: All new fields have defaults matching current behavior (debug off, no watchdog). Existing tests pass without modification.

#### commands.py — Add 3 CLI options to `run` command

```python
@click.option("--debug", is_flag=True, help="Enable debug logging to debug.log")
@click.option(
    "--stall-timeout", type=int, default=0,
    help="Kill/warn after N seconds of no output growth (0=disabled)",
)
@click.option(
    "--stall-action", type=click.Choice(["warn", "kill"]), default="warn",
    help="Action on stall timeout: warn (log only) or kill (terminate)",
)
def run(index_path, ..., debug, stall_timeout, stall_action):
    config = load_sprint_config(...)
    config.debug = debug
    config.stall_timeout = stall_timeout
    config.stall_action = stall_action
```

**tmux forwarding**: Add to `_build_foreground_command()` in tmux.py:
```python
if config.debug:
    cmd.append("--debug")
if config.stall_timeout:
    cmd.extend(["--stall-timeout", str(config.stall_timeout)])
if config.stall_action != "warn":
    cmd.extend(["--stall-action", config.stall_action])
```

#### executor.py — Instrument poll loop + watchdog

Changes to `execute_sprint()`:

```python
def execute_sprint(config: SprintConfig):
    from .debug_logger import setup_debug_logger, debug_log

    # NEW: Setup debug logger (NullHandler if config.debug=False)
    dbg = setup_debug_logger(config)
    debug_log(dbg, "executor", "sprint_start",
              total_phases=len(config.active_phases),
              debug=config.debug,
              stall_timeout=config.stall_timeout)

    # Pre-flight (unchanged)
    if shutil.which("claude") is None:
        raise SystemExit(...)

    signal_handler = SignalHandler()
    signal_handler.install()

    logger = SprintLogger(config)
    tui = SprintTUI(config, debug_logger=dbg)          # CHANGED: pass logger
    monitor = OutputMonitor(Path("/dev/null"), debug_logger=dbg)  # CHANGED
    proc_manager: ClaudeProcess | None = None

    # ... existing setup ...

    try:
        for phase in config.active_phases:
            # ... existing shutdown check ...

            debug_log(dbg, "executor", "PHASE_BEGIN",
                      phase=phase.number, file=phase.basename)

            # ... existing monitor.reset, monitor.start ...

            proc_manager = ClaudeProcess(config, phase, debug_logger=dbg)  # CHANGED
            proc_manager.start()
            started_at = datetime.now(timezone.utc)
            start_mono = time.monotonic()                   # NEW: for elapsed calc
            deadline = start_mono + proc_manager.timeout_seconds

            # ... existing logger.write_phase_start, tui.update ...

            _timed_out = False
            _stall_acted = False                            # NEW: watchdog flag
            while proc_manager._process.poll() is None:
                if signal_handler.shutdown_requested:
                    proc_manager.terminate()
                    break
                if time.monotonic() > deadline:
                    _timed_out = True
                    proc_manager.terminate()
                    break

                ms = monitor.state

                # NEW: Poll tick logging
                debug_log(dbg, "executor", "poll_tick",
                          phase=phase.number,
                          pid=proc_manager._process.pid,
                          poll="None",
                          elapsed=f"{time.monotonic() - start_mono:.1f}s",
                          output_bytes=ms.output_bytes,
                          growth=f"{ms.growth_rate_bps:.0f}bps",
                          stall_sec=f"{ms.stall_seconds:.1f}",
                          stall=ms.stall_status)

                # NEW: Watchdog check (works with or without --debug)
                if (config.stall_timeout > 0
                        and ms.stall_seconds > config.stall_timeout
                        and not _stall_acted):
                    debug_log(dbg, "executor", "stall_timeout_exceeded",
                              phase=phase.number,
                              pid=proc_manager._process.pid,
                              stall_seconds=f"{ms.stall_seconds:.1f}",
                              action=config.stall_action)
                    _stall_acted = True
                    if config.stall_action == "kill":
                        _timed_out = True  # treat as timeout for status
                        proc_manager.terminate()
                        break

                try:
                    tui.update(sprint_result, ms, phase)
                except Exception as _tui_exc:
                    import sys
                    print(f"[TUI] Display error: {_tui_exc}", file=sys.stderr)
                time.sleep(0.5)

            # ... existing exit code handling ...

            # NEW: Phase end logging
            debug_log(dbg, "executor", "phase_complete",
                      phase=phase.number, status=status.value,
                      exit_code=exit_code,
                      duration=f"{(finished_at - started_at).total_seconds():.1f}s")
            debug_log(dbg, "executor", "PHASE_END", phase=phase.number)

            # NEW: Diagnostic report on failure (when debug enabled)
            if status.is_failure and config.debug:
                try:
                    from .diagnostics import (
                        DiagnosticCollector, FailureClassifier, ReportGenerator,
                    )
                    collector = DiagnosticCollector()
                    bundle = collector.collect(config, phase,
                                              phase_result=phase_result,
                                              monitor_state=ms,
                                              process=proc_manager)
                    if _stall_acted and config.stall_action == "kill":
                        bundle.was_stall_killed = True
                    classifier = FailureClassifier()
                    mode, conf = classifier.classify(bundle)
                    root_cause, actions = classifier.suggest(mode)
                    report = ReportGenerator().generate(
                        bundle, mode, conf, root_cause, actions)
                    ReportGenerator().write(report, config.results_dir)
                except Exception:
                    pass  # diagnostic report is best-effort

            # ... existing halt check ...
```

#### process.py — Add debug logging

```python
class ClaudeProcess:
    def __init__(self, config, phase, debug_logger=None):
        self.config = config
        self.phase = phase
        self._process = None
        self._stdout_fh = None
        self._stderr_fh = None
        self._debug = debug_logger  # NEW

    def start(self):
        # ... existing Popen ...
        if self._debug:
            from .debug_logger import debug_log
            debug_log(self._debug, "process", "spawn",
                      pid=self._process.pid,
                      cmd=str(self.build_command()[:6]) + "...",
                      env_delta="CLAUDECODE=<removed>")
            debug_log(self._debug, "process", "files_opened",
                      stdout=str(output_file), stderr=str(error_file))
        return self._process

    def terminate(self):
        if self._debug:
            from .debug_logger import debug_log
            debug_log(self._debug, "process", "signal_sent",
                      pid=self._process.pid, signal="SIGTERM")
        # ... existing SIGTERM logic ...
        # After SIGKILL:
        if self._debug:
            debug_log(self._debug, "process", "signal_sent",
                      pid=self._process.pid, signal="SIGKILL")
```

#### tui.py — Add debug logging for state transitions

```python
class SprintTUI:
    def __init__(self, config, console=None, debug_logger=None):
        # ... existing ...
        self._debug = debug_logger  # NEW

    def start(self):
        if self._debug:
            from .debug_logger import debug_log
            debug_log(self._debug, "tui", "tui_start")
        # ... existing ...

    def update(self, ...):
        # ... existing ...
        if self._live and not self._live_failed:
            try:
                self._live.update(self._render())
            except Exception as exc:
                self._live_failed = True
                if self._debug:
                    from .debug_logger import debug_log
                    debug_log(self._debug, "tui", "tui_live_failed",
                              error=str(exc))
                # ... existing stderr print ...

    def stop(self):
        if self._debug:
            from .debug_logger import debug_log
            debug_log(self._debug, "tui", "tui_stop")
        # ... existing ...
```

#### monitor.py — Add debug logging for signal extraction

```python
class OutputMonitor:
    def __init__(self, output_path, poll_interval=0.5, debug_logger=None):
        # ... existing ...
        self._debug = debug_logger  # NEW

    def _extract_signals(self, text):
        # ... existing extraction ...
        if self._debug and (task_matches or tool_matches or file_matches):
            from .debug_logger import debug_log
            debug_log(self._debug, "monitor", "signal_extracted",
                      task_id=self.state.last_task_id,
                      tool=self.state.last_tool_used,
                      files_changed=self.state.files_changed)
```

#### tmux.py — Forward new flags

```python
def _build_foreground_command(config: SprintConfig) -> list[str]:
    cmd = [...]  # existing
    # NEW: Forward diagnostic flags
    if config.debug:
        cmd.append("--debug")
    if config.stall_timeout:
        cmd.extend(["--stall-timeout", str(config.stall_timeout)])
    if config.stall_action != "warn":
        cmd.extend(["--stall-action", config.stall_action])
    return cmd
```

---

### New File: `debug_logger.py`

```python
"""Debug logging for sprint execution — structured, line-buffered, crash-safe."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SprintConfig

LOG_VERSION = "1.0"


class _FlushHandler(logging.FileHandler):
    """FileHandler that flushes after every emit for crash safety."""

    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        self.flush()


class _DebugFormatter(logging.Formatter):
    """Format: timestamp LEVEL [component] message"""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc)
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"
        level = record.levelname.ljust(5)
        component = getattr(record, "component", "unknown")
        return f"{ts_str} {level} [{component}] {record.getMessage()}"


def setup_debug_logger(config: SprintConfig) -> logging.Logger:
    """Create debug logger. Returns NullHandler logger when debug=False."""
    logger = logging.getLogger("superclaude.sprint.debug")
    logger.handlers.clear()
    logger.propagate = False

    if not config.debug:
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)
        return logger

    logger.setLevel(logging.DEBUG)
    config.release_dir.mkdir(parents=True, exist_ok=True)

    # Write version header first
    config.debug_log_path.write_text(f"# debug-log-version: {LOG_VERSION}\n")

    # Open in append mode after header
    handler = _FlushHandler(str(config.debug_log_path), mode="a")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_DebugFormatter())
    logger.addHandler(handler)

    return logger


def debug_log(
    logger: logging.Logger,
    component: str,
    event: str,
    level: int = logging.DEBUG,
    **kwargs,
) -> None:
    """Emit a structured debug log entry.

    Usage: debug_log(dbg, "executor", "poll_tick", phase=1, pid=123)
    Output: 2026-03-04T10:15:00.001Z DEBUG [executor] poll_tick phase=1 pid=123
    """
    if not logger.isEnabledFor(level):
        return
    parts = [event]
    for k, v in kwargs.items():
        parts.append(f"{k}={v}")
    logger.log(level, " ".join(parts), extra={"component": component})


# --- Reader (for tests and auto-analysis) ---


@dataclass
class DebugEvent:
    """Parsed debug log entry."""

    timestamp: str
    level: str
    component: str
    event: str
    context: dict[str, str]
    raw_line: str


_LINE_PATTERN = re.compile(
    r"^(\S+)\s+(DEBUG|INFO|WARN|ERROR)\s+\[(\w+)\]\s+(\S+)\s*(.*)"
)
_KV_PATTERN = re.compile(r"(\w+)=(\S+)")


class DebugLogReader:
    """Parse and query debug.log files."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._events: list[DebugEvent] | None = None

    @property
    def events(self) -> list[DebugEvent]:
        if self._events is None:
            self._events = self._parse()
        return self._events

    def _parse(self) -> list[DebugEvent]:
        if not self.log_path.exists():
            return []
        events = []
        for line in self.log_path.read_text().splitlines():
            if line.startswith("#"):
                continue
            m = _LINE_PATTERN.match(line)
            if m:
                ts, level, comp, event, ctx_str = m.groups()
                ctx = dict(_KV_PATTERN.findall(ctx_str))
                events.append(DebugEvent(ts, level, comp, event, ctx, line))
        return events

    def filter(
        self,
        component: str | None = None,
        phase: int | None = None,
        level: str | None = None,
    ) -> list[DebugEvent]:
        result = self.events
        if component:
            result = [e for e in result if e.component == component]
        if level:
            result = [e for e in result if e.level == level]
        if phase is not None:
            result = [e for e in result if e.context.get("phase") == str(phase)]
        return result

    def phase_events(self, phase: int) -> list[DebugEvent]:
        """Events between PHASE_BEGIN and PHASE_END for the given phase."""
        in_phase = False
        result = []
        for ev in self.events:
            if ev.event == "PHASE_BEGIN" and ev.context.get("phase") == str(phase):
                in_phase = True
            if in_phase:
                result.append(ev)
            if ev.event == "PHASE_END" and ev.context.get("phase") == str(phase):
                break
        return result

    def has_event(self, event_name: str) -> bool:
        return any(e.event == event_name for e in self.events)

    def find_event(self, event_name: str) -> DebugEvent | None:
        return next((e for e in self.events if e.event == event_name), None)
```

---

### New File: `diagnostics.py`

```python
"""Diagnostic collection, failure classification, and report generation."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import MonitorState, Phase, PhaseResult, SprintConfig
    from .process import ClaudeProcess


class FailureMode(Enum):
    SPAWN_FAILURE = "SPAWN_FAILURE"
    SILENT_STALL = "SILENT_STALL"
    OUTPUT_STALL = "OUTPUT_STALL"
    RESULT_MISSING = "RESULT_MISSING"
    EXIT_CODE_ERROR = "EXIT_CODE_ERROR"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


@dataclass
class DiagnosticBundle:
    """All diagnostic data collected for a failed phase."""

    phase_number: int
    subprocess_spawned: bool
    subprocess_pid: int | None
    output_file_exists: bool
    output_bytes: int
    result_file_exists: bool
    result_file_content: str
    exit_code: int | None
    stall_seconds: float
    was_stall_killed: bool
    debug_log_tail: list[str] = field(default_factory=list)
    stderr_contents: str = ""
    process_state: dict | None = None


class DiagnosticCollector:
    """Gathers diagnostic state from sprint artifacts."""

    def collect(
        self,
        config: SprintConfig,
        phase: Phase,
        phase_result: PhaseResult | None = None,
        monitor_state: MonitorState | None = None,
        process: ClaudeProcess | None = None,
    ) -> DiagnosticBundle:
        output_file = config.output_file(phase)
        result_file = config.result_file(phase)
        error_file = config.error_file(phase)

        output_exists = output_file.exists()
        output_bytes = output_file.stat().st_size if output_exists else 0
        result_exists = result_file.exists()
        result_content = (
            result_file.read_text(errors="replace") if result_exists else ""
        )
        stderr = error_file.read_text(errors="replace") if error_file.exists() else ""

        debug_tail = []
        if config.debug_log_path.exists():
            lines = config.debug_log_path.read_text().splitlines()
            debug_tail = lines[-50:]

        proc_state = None
        spawned = process is not None and process._process is not None
        pid = process._process.pid if spawned else None
        if spawned and process._process.poll() is None:
            proc_state = self._capture_process_state(pid)

        return DiagnosticBundle(
            phase_number=phase.number,
            subprocess_spawned=spawned,
            subprocess_pid=pid,
            output_file_exists=output_exists,
            output_bytes=output_bytes,
            result_file_exists=result_exists,
            result_file_content=result_content,
            exit_code=phase_result.exit_code if phase_result else None,
            stall_seconds=monitor_state.stall_seconds if monitor_state else 0,
            was_stall_killed=False,
            debug_log_tail=debug_tail,
            stderr_contents=stderr,
            process_state=proc_state,
        )

    def _capture_process_state(self, pid: int) -> dict | None:
        """Capture process state from /proc (Linux) or ps (fallback)."""
        try:
            status_text = Path(f"/proc/{pid}/status").read_text()
            state = {}
            for line in status_text.splitlines():
                for key in ("Pid", "PPid", "State", "VmRSS", "VmSize"):
                    if line.startswith(key + ":"):
                        state[key.lower()] = line.split(":", 1)[1].strip()
            try:
                state["open_fds"] = len(list(Path(f"/proc/{pid}/fd").iterdir()))
            except PermissionError:
                pass
            return state
        except (FileNotFoundError, PermissionError):
            try:
                result = subprocess.run(
                    ["ps", "-p", str(pid), "-o", "pid,ppid,state,rss,vsz,args",
                     "--no-headers"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return {"ps_output": result.stdout.strip()}
            except Exception:
                pass
        return None


class FailureClassifier:
    """Classifies failure mode from diagnostic evidence."""

    ROOT_CAUSES: dict[FailureMode, tuple[str, list[str]]] = {
        FailureMode.SPAWN_FAILURE: (
            "claude binary not found, permission denied, or command construction error",
            [
                "Verify 'claude' is on PATH: which claude",
                "Check debug.log for spawn event — if absent, Popen failed",
                "Check stderr file for subprocess error messages",
            ],
        ),
        FailureMode.SILENT_STALL: (
            "Subprocess started but produced no output",
            [
                "Run the phase command manually and observe behavior",
                "Check if --dangerously-skip-permissions flag is accepted",
                "Try: claude --print -p 'hello' to verify basic functionality",
                "Check debug.log spawn event for the exact command constructed",
            ],
        ),
        FailureMode.OUTPUT_STALL: (
            "Subprocess was producing output but stopped",
            [
                "Check output file for clues about where claude stopped",
                "Possible: claude hang, resource exhaustion, rate limiting",
                "Try with --max-turns 5 to see if a shorter run completes",
            ],
        ),
        FailureMode.RESULT_MISSING: (
            "Claude completed but did not write result file",
            [
                "The prompt may not include completion protocol instructions",
                "Check output file — claude may have finished without writing result",
                "Verify result file path matches what the prompt specifies",
            ],
        ),
        FailureMode.EXIT_CODE_ERROR: (
            "Subprocess failed with non-zero exit code",
            [
                "Check stderr file for error details",
                "Common: invalid flags, auth failure, API errors",
            ],
        ),
        FailureMode.TIMEOUT: (
            "Phase exceeded timeout",
            [
                "Task may be too complex for allocated turns",
                "Try increasing --max-turns or simplifying the task",
                "Check output file to see how far claude got",
            ],
        ),
    }

    def classify(self, bundle: DiagnosticBundle) -> tuple[FailureMode, float]:
        """Returns (failure_mode, confidence)."""
        if not bundle.subprocess_spawned or bundle.subprocess_pid is None:
            return FailureMode.SPAWN_FAILURE, 0.95
        if bundle.exit_code == 124:
            return FailureMode.TIMEOUT, 0.95
        if bundle.output_bytes == 0 and bundle.stall_seconds > 0:
            return FailureMode.SILENT_STALL, 0.90
        if bundle.output_bytes > 0 and bundle.stall_seconds > 30:
            return FailureMode.OUTPUT_STALL, 0.85
        if bundle.exit_code is not None and bundle.exit_code != 0:
            return FailureMode.EXIT_CODE_ERROR, 0.90
        if bundle.output_bytes > 0 and not bundle.result_file_exists:
            return FailureMode.RESULT_MISSING, 0.85
        return FailureMode.UNKNOWN, 0.50

    def suggest(self, mode: FailureMode) -> tuple[str, list[str]]:
        return self.ROOT_CAUSES.get(
            mode, ("Unknown failure", ["Review debug.log manually"])
        )


class ReportGenerator:
    """Generates and writes diagnostic-report.json."""

    def generate(
        self,
        bundle: DiagnosticBundle,
        failure_mode: FailureMode,
        confidence: float,
        root_cause: str,
        actions: list[str],
    ) -> dict:
        return {
            "report_version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "failed_phase": bundle.phase_number,
            "failure_mode": failure_mode.value,
            "classification_confidence": confidence,
            "evidence": {
                "subprocess_spawned": bundle.subprocess_spawned,
                "subprocess_pid": bundle.subprocess_pid,
                "output_file_exists": bundle.output_file_exists,
                "output_bytes": bundle.output_bytes,
                "result_file_exists": bundle.result_file_exists,
                "exit_code": bundle.exit_code,
                "stall_seconds": bundle.stall_seconds,
                "was_stall_killed": bundle.was_stall_killed,
                "debug_log_tail": bundle.debug_log_tail[-10:],
                "stderr_contents": bundle.stderr_contents[:500],
                "process_state": bundle.process_state,
            },
            "suggested_root_cause": root_cause,
            "recommended_actions": actions,
        }

    def write(self, report: dict, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "diagnostic-report.json"
        path.write_text(json.dumps(report, indent=2, default=str))
        return path
```

---

### New File: `tests/sprint/diagnostic/conftest.py`

```python
"""Diagnostic test infrastructure — harness, fixtures, shell script phases."""

from __future__ import annotations

import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path

import pytest

from superclaude.cli.sprint.debug_logger import DebugLogReader
from superclaude.cli.sprint.diagnostics import (
    DiagnosticCollector,
    FailureClassifier,
    ReportGenerator,
)
from superclaude.cli.sprint.models import Phase, SprintConfig

HAS_CLAUDE = shutil.which("claude") is not None

requires_claude = pytest.mark.skipif(
    not HAS_CLAUDE, reason="claude binary not found on PATH"
)


@dataclass
class PhaseSpec:
    """Specification for a diagnostic test phase."""

    name: str
    task_content: str
    script: str | None = None  # shell script body (L0/LN); None = use real claude
    expect_pass: bool = True


@dataclass
class DiagnosticResult:
    """Result wrapper from a diagnostic test run."""

    exit_code: int
    sprint_dir: Path
    debug_log: Path | None
    results_dir: Path
    report: dict | None = None
    exception: Exception | None = None


class DiagnosticTestHarness:
    """Creates test sprint directories and runs them with full instrumentation.

    L0 tests: installs a shell script as fake 'claude' binary via PATH.
    L1-L3 tests: uses real claude binary (requires_claude marker).
    LN tests: installs failure-simulating scripts.
    """

    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path
        self._bin_dir = tmp_path / "bin"
        self._bin_dir.mkdir()

    def create_sprint(
        self,
        phases: list[PhaseSpec],
        max_turns: int = 5,
        stall_timeout: int = 30,
        stall_action: str = "kill",
    ) -> SprintConfig:
        sprint_dir = self.tmp_path / "sprint"
        sprint_dir.mkdir(exist_ok=True)

        phase_objects = []
        index_lines = ["# Diagnostic Test Sprint\n"]

        for i, spec in enumerate(phases, 1):
            phase_file = sprint_dir / f"phase-{i}-tasklist.md"
            phase_file.write_text(
                f"# Phase {i}: {spec.name}\n## Tasks\n{spec.task_content}\n"
            )
            index_lines.append(f"{i}. [Phase {i}](phase-{i}-tasklist.md)\n")
            phase_objects.append(Phase(number=i, file=phase_file, name=spec.name))

            if spec.script is not None:
                self._install_fake_claude(spec.script)

        index_path = sprint_dir / "tasklist-index.md"
        index_path.write_text("".join(index_lines))

        return SprintConfig(
            index_path=index_path,
            release_dir=sprint_dir,
            phases=phase_objects,
            start_phase=1,
            end_phase=len(phases),
            max_turns=max_turns,
            debug=True,
            stall_timeout=stall_timeout,
            stall_action=stall_action,
            permission_flag="--dangerously-skip-permissions",
        )

    def _install_fake_claude(self, script_body: str):
        """Install a shell script as 'claude' in our private bin/."""
        script_path = self._bin_dir / "claude"
        script_path.write_text(f"#!/bin/bash\n{script_body}\n")
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP)

    def run_sprint(
        self,
        config: SprintConfig,
        timeout: int = 30,
        override_path: str | None = None,
    ) -> DiagnosticResult:
        """Execute sprint, capturing exit code and artifacts.

        For L0/LN: prepends fake bin/ to PATH so our script is found as 'claude'.
        For L1-L3: uses real PATH (real claude binary).
        """
        from superclaude.cli.sprint.executor import execute_sprint

        env_backup = os.environ.copy()
        if override_path is not None:
            os.environ["PATH"] = override_path
        elif (self._bin_dir / "claude").exists():
            os.environ["PATH"] = f"{self._bin_dir}:{env_backup.get('PATH', '')}"

        # Remove TMUX to prevent tmux code paths
        os.environ.pop("TMUX", None)

        exit_code = 0
        exception = None

        try:
            execute_sprint(config)
        except SystemExit as e:
            exit_code = e.code if isinstance(e.code, int) else 1
        except Exception as e:
            exit_code = -1
            exception = e
        finally:
            os.environ.clear()
            os.environ.update(env_backup)

        debug_log = config.debug_log_path if config.debug_log_path.exists() else None

        return DiagnosticResult(
            exit_code=exit_code,
            sprint_dir=config.release_dir,
            debug_log=debug_log,
            results_dir=config.results_dir,
            exception=exception,
        )

    def analyze_result(
        self, config: SprintConfig, result: DiagnosticResult
    ) -> dict | None:
        if result.exit_code == 0:
            return None

        collector = DiagnosticCollector()
        classifier = FailureClassifier()
        generator = ReportGenerator()

        for phase in config.active_phases:
            output_file = config.output_file(phase)
            result_file = config.result_file(phase)
            if not result_file.exists() or not output_file.exists():
                bundle = collector.collect(config, phase)
                mode, confidence = classifier.classify(bundle)
                root_cause, actions = classifier.suggest(mode)
                report = generator.generate(bundle, mode, confidence, root_cause, actions)
                generator.write(report, config.results_dir)
                return report

        return None


@pytest.fixture
def diagnostic_harness(tmp_path):
    return DiagnosticTestHarness(tmp_path)


@pytest.fixture
def debug_log_reader():
    def _factory(log_path: Path) -> DebugLogReader:
        return DebugLogReader(log_path)
    return _factory
```

---

### L0 Test: Fake Claude Script Design

The fake `claude` script receives the same arguments as real claude:
```
claude --print --dangerously-skip-permissions --no-session-persistence \
       --max-turns 5 --output-format text -p "<big prompt>"
```

stdout/stderr are redirected to files by `ClaudeProcess.start()`. The script must:
1. Write something to stdout (goes to output file)
2. Extract the result file path from the prompt
3. Write a valid result file

**Result file path extraction**: The prompt contains:
```
1. Write a phase completion report to /absolute/path/to/results/phase-N-result.md containing:
```

The script uses env var `DIAG_RESULTS_DIR` (set by harness) for reliability:

```bash
# PASS_SCRIPT — writes output + valid result file
echo "Processing phase tasks..."
echo "Task T01.01: Pipeline smoke test - complete"

# Extract phase number from prompt
PROMPT=""
while [[ $# -gt 0 ]]; do
    case $1 in -p) PROMPT="$2"; shift 2;; *) shift;; esac
done
PHASE=$(echo "$PROMPT" | grep -oP 'Phase (\d+)' | head -1 | grep -oP '\d+')
PHASE=${PHASE:-1}

# Write result file (results dir created by ClaudeProcess.start())
RESULT_DIR="$(dirname "$(dirname "$0")")/../sprint/results"
# Actually: harness sets DIAG_RESULTS_DIR env var
RESULT_FILE="${DIAG_RESULTS_DIR:-results}/phase-${PHASE}-result.md"
mkdir -p "$(dirname "$RESULT_FILE")"
cat > "$RESULT_FILE" << 'EOF'
---
phase: PHASE_NUM
status: PASS
tasks_total: 1
tasks_passed: 1
tasks_failed: 0
---
EXIT_RECOMMENDATION: CONTINUE
EOF
sed -i "s/PHASE_NUM/${PHASE}/" "$RESULT_FILE"
```

The harness sets `DIAG_RESULTS_DIR` before calling execute_sprint:
```python
os.environ["DIAG_RESULTS_DIR"] = str(config.results_dir)
```

---

### Negative Test Script Templates

```bash
# SILENT_STALL_SCRIPT — starts but produces nothing
sleep 3600

# OUTPUT_STALL_SCRIPT — writes initial output then hangs
echo "Starting analysis..."
echo "Reading files..."
sleep 3600

# RESULT_MISSING_SCRIPT — writes output, exits clean, no result file
echo "Processing all tasks..."
echo "Analysis complete."
exit 0

# EXIT_CODE_ERROR_SCRIPT — fails with error
echo "Error: authentication failed" >&2
exit 1

# TIMEOUT_SCRIPT — produces output continuously but never finishes
while true; do
    echo "Still processing..."
    sleep 1
done
```

---

### File Inventory

| File | Type | Purpose |
|------|------|---------|
| `src/superclaude/cli/sprint/debug_logger.py` | **NEW** | Logger setup, debug_log helper, DebugEvent, DebugLogReader |
| `src/superclaude/cli/sprint/diagnostics.py` | **NEW** | FailureMode, DiagnosticBundle, Collector, Classifier, ReportGenerator |
| `src/superclaude/cli/sprint/models.py` | **MODIFY** | +4 fields, +1 property on SprintConfig |
| `src/superclaude/cli/sprint/commands.py` | **MODIFY** | +3 Click options (--debug, --stall-timeout, --stall-action) |
| `src/superclaude/cli/sprint/executor.py` | **MODIFY** | Logger setup, poll tick logging, watchdog, diagnostic report |
| `src/superclaude/cli/sprint/process.py` | **MODIFY** | +debug_logger param, spawn/signal/exit logging |
| `src/superclaude/cli/sprint/monitor.py` | **MODIFY** | +debug_logger param, signal extraction logging |
| `src/superclaude/cli/sprint/tui.py` | **MODIFY** | +debug_logger param, start/failed/stop logging |
| `src/superclaude/cli/sprint/tmux.py` | **MODIFY** | Forward --debug/--stall-* flags in _build_foreground_command |
| `tests/sprint/diagnostic/__init__.py` | **NEW** | Package marker |
| `tests/sprint/diagnostic/conftest.py` | **NEW** | DiagnosticTestHarness, PhaseSpec, fixtures |
| `tests/sprint/diagnostic/test_level_0.py` | **NEW** | Pipeline smoke tests (2 tests) |
| `tests/sprint/diagnostic/test_level_1.py` | **NEW** | Claude echo tests (2 tests) |
| `tests/sprint/diagnostic/test_level_2.py` | **NEW** | File operation tests (2 tests) |
| `tests/sprint/diagnostic/test_level_3.py` | **NEW** | Analysis tests (2 tests) |
| `tests/sprint/diagnostic/test_negative.py` | **NEW** | Failure mode tests (6 tests) |

**Total**: 7 modified files, 9 new files, ~16 new tests

---

### Backward Compatibility

All changes are additive. Existing behavior preserved by:

| New Field | Default | Effect |
|-----------|---------|--------|
| `SprintConfig.debug` | `False` | No debug.log created |
| `SprintConfig.stall_timeout` | `0` | Watchdog disabled |
| `SprintConfig.stall_action` | `"warn"` | Log-only, no termination |
| `SprintConfig.phase_timeout` | `0` | Uses computed value |
| `ClaudeProcess(debug_logger=None)` | `None` | No debug logging |
| `OutputMonitor(debug_logger=None)` | `None` | No debug logging |
| `SprintTUI(debug_logger=None)` | `None` | No debug logging |

Existing tests in `tests/sprint/test_*.py` create `SprintConfig` with positional/keyword args. New fields use defaults. No test changes required.

---

## Panel Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 8.5/10 | Concrete examples for all major outputs. Log schema defined. |
| Completeness | 8.0/10 | All failure modes covered. Watchdog added. CI strategy defined. |
| Testability | 9.0/10 | Given/When/Then scenarios. Negative tests. Timing assertions. |
| Architecture | 9.0/10 | Full code-level design. Injection points defined. Backward-compatible. |
| Operational | 8.5/10 | Watchdog solves the actual problem. Process state capture defined. |
| **Overall** | **8.6/10** | Up from 8.4 post-panel. Architecture detail adds +1.0 to design score. |

### Expert Sign-off

- **Wiegers**: Requirements now have measurable acceptance criteria and concrete examples. Approved.
- **Nygard**: Watchdog mechanism transforms spec from diagnostic-only to preventive. Critical gap closed. Approved.
- **Fowler**: Logger architecture is clean with constructor injection. DiagnosticBundle decouples collection from analysis. DebugLogReader provides missing abstraction. Full diff plan verifiable against existing code. Approved.
- **Crispin**: Level 0 + Level N provide pipeline isolation and failure mode coverage. CI strategy resolved. Fake claude via PATH substitution is real execution, not mocking. Approved.
- **Adzic**: Given/When/Then scenarios make requirements executable. Shell scripts, log formats, and report schemas all have concrete examples. Approved.
