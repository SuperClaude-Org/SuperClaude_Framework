---
variant_id: architect
variant_persona: architect
spec_source: .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
generated: "2026-03-03T00:00:00Z"
generator: sc:roadmap (adversarial variant)
complexity_score: 0.69
complexity_class: MEDIUM
perspective: "Architecture, dependency management, long-term maintainability, module boundaries, extensibility, testability"
milestone_count: 6
milestone_index:
  - id: M1
    title: "Foundation: Pure Data Model Layer"
    type: FEATURE
    priority: P0
    effort: S
    dependencies: []
    deliverable_count: 4
    risk_level: Low
  - id: M2
    title: "Configuration & Discovery Engine"
    type: FEATURE
    priority: P0
    effort: S
    dependencies: [M1]
    deliverable_count: 4
    risk_level: Low
  - id: M3
    title: "Process Management & Signal Handling"
    type: FEATURE
    priority: P0
    effort: M
    dependencies: [M1]
    deliverable_count: 5
    risk_level: Medium
  - id: M4
    title: "Monitoring & TUI Display Layer"
    type: FEATURE
    priority: P1
    effort: M
    dependencies: [M1]
    deliverable_count: 5
    risk_level: Low
  - id: M5
    title: "Orchestration & Integration"
    type: FEATURE
    priority: P0
    effort: L
    dependencies: [M2, M3, M4]
    deliverable_count: 5
    risk_level: High
  - id: M6
    title: "End-to-End Validation & Acceptance"
    type: TEST
    priority: P1
    effort: M
    dependencies: [M5]
    deliverable_count: 5
    risk_level: Medium
total_deliverables: 28
total_risks: 12
estimated_phases: 6
---

# Roadmap Variant: Architect Perspective

## Variant Identity

**Persona**: System Architect
**Focus**: Module boundary integrity, dependency direction, testability in isolation, extensibility for future growth, separation of concerns
**Differentiator from base roadmap**: The base roadmap groups CLI commands, config, process management, and the executor into a single large milestone (M2, effort L, 8 deliverables). This architect variant splits those into three independent milestones (M2, M3, M4) that can proceed in parallel after M1, reducing critical-path length and enforcing that each module is testable in complete isolation before integration. The executor is deferred to M5 as a pure integration milestone, which is the only place where cross-module coupling is permitted.

---

## Architectural Principles Driving This Roadmap

1. **Dependency Direction**: All arrows point inward toward `models.py`. No module imports a peer except through the data model layer. The executor (M5) is the sole integration point.
2. **Testability in Isolation**: M2, M3, and M4 must each be 100% unit-testable without importing any peer module. If a test requires mocking a peer, the boundary is wrong.
3. **Narrow Integration Surface**: The executor in M5 depends on M2 (config), M3 (process/signal), M4 (monitor/TUI), plus logging, tmux, and notify. All coupling is confined here.
4. **Late Binding**: CLI commands (commands.py) use lazy imports so that the Click layer never forces early resolution of the full dependency graph at import time.
5. **Extensibility Seam**: Each module defines a clear interface boundary (function signatures, dataclass contracts) that can be extended without modifying callers.

---

## Dependency Graph

```
         M1 (models.py)
        / |      \
       /  |       \
     M2   M3      M4
  (config)(process)(monitor+TUI)
       \   |      /
        \  |     /
         M5 (executor, tmux, logging, notify, commands wiring)
           |
          M6 (E2E validation + acceptance)
```

**Critical path**: M1 -> M3 -> M5 -> M6 (process management is hardest to get right)

**Parallel opportunity**: M2, M3, M4 are fully independent after M1 completes. Three agents can execute simultaneously.

---

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation: Pure Data Model Layer | FEATURE | P0 | S | None | 4 | Low |
| M2 | Configuration & Discovery Engine | FEATURE | P0 | S | M1 | 4 | Low |
| M3 | Process Management & Signal Handling | FEATURE | P0 | M | M1 | 5 | Medium |
| M4 | Monitoring & TUI Display Layer | FEATURE | P1 | M | M1 | 5 | Low |
| M5 | Orchestration & Integration | FEATURE | P0 | L | M2, M3, M4 | 5 | High |
| M6 | End-to-End Validation & Acceptance | TEST | P1 | M | M5 | 5 | Medium |

---

## M1: Foundation -- Pure Data Model Layer

### Objective

Establish the zero-dependency data model layer that all other modules import from. This milestone defines the type vocabulary of the entire system. Every enum value, every dataclass field, and every computed property is locked down here with exhaustive unit tests. No external dependencies beyond Python stdlib.

### Architectural Rationale

The data model is the gravity center of the dependency graph. Getting it wrong forces cascading changes across all consumers. By completing and fully testing models.py first, we freeze the contract that M2-M4 develop against. The `__init__.py` and `main.py` integration point are included here because they are trivial wiring that enables early verification of the Click group registration.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `models.py`: PhaseStatus (8 values), SprintOutcome (4 values), Phase, SprintConfig, PhaseResult, SprintResult, MonitorState dataclasses | All 7 types match spec Section 2. Properties `is_terminal`, `is_success`, `is_failure`, `duration_display`, `resume_command`, `stall_status`, `output_size_display`, `active_phases` pass unit tests. Zero imports from any sprint peer module. Only stdlib imports. |
| D1.2 | `__init__.py` exporting `sprint_group` from commands.py | `from superclaude.cli.sprint import sprint_group` succeeds at import time. |
| D1.3 | `main.py` integration: `main.add_command(sprint_group, name="sprint")` | `superclaude sprint --help` returns group help text. Verified via Click's `CliRunner`. |
| D1.4 | `tests/sprint/test_models.py`: exhaustive unit tests | Coverage >=95% on models.py. Every enum member, every property, every edge case (empty phases list, zero duration, halt_phase=None). |

### Dependencies

None. This is the foundation.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data model changes needed during M2-M4 | Medium | Low | Dataclasses are additive -- new fields with defaults never break existing consumers. Properties isolate computation from field layout. |
| SKIPPED enum value debate (spec has it, implementation removed it) | Low | Low | Decision already made in implementation: SKIPPED removed with rationale documented in code comment. Validate that no downstream code references it. |

---

## M2: Configuration & Discovery Engine

### Objective

Implement phase discovery, validation, and config loading. This module translates filesystem state (index files, phase file naming conventions) into the SprintConfig dataclass. It depends only on M1 types and stdlib/Click. It must be fully testable with synthetic filesystem fixtures (tmp_path), no subprocess calls, no threading.

### Architectural Rationale

Configuration is separated from execution because discovery logic (regex matching, directory scanning, index parsing) has fundamentally different failure modes than process management. Config errors are user-facing (missing files, naming mismatches) and should produce clear Click error messages. Process errors are system-level (signals, timeouts). Mixing them in one milestone creates confused error handling.

The config module defines a pure function pipeline: `discover_phases() -> validate_phases() -> load_sprint_config()`. Each function is independently testable.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `config.py`: `discover_phases()` with index-first and directory-fallback strategies | Unit tests with tmp_path fixtures verify all 4 naming conventions: `phase-N-tasklist.md`, `pN-tasklist.md`, `Phase_N_tasklist.md`, `tasklist-PN.md`. Index parsing finds phase references in markdown links. Directory fallback activates when index contains no phase references. Deduplication by phase number. Sorted ascending. |
| D2.2 | `config.py`: `validate_phases()` detecting missing files and sequence gaps | Returns ERROR messages for missing files, WARN messages for gaps. Gap between phases 2 and 4 detected. Empty phase list returns no messages. |
| D2.3 | `config.py`: `load_sprint_config()` combining discovery, validation, auto-detection, and error reporting | Full config loaded from sample index fixture. end_phase auto-detected as max phase number when 0. Errors abort with ClickException. Warnings printed to stderr. Active phases computed correctly for --start/--end range. |
| D2.4 | `tests/sprint/test_config.py`: full unit test coverage | All 4 naming conventions. Index-first vs directory-fallback. Gap detection. Missing file errors. Range validation. Phase name extraction from headings. >=90% coverage on config.py. |

### Dependencies

- **M1**: Phase, SprintConfig types (frozen contract)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Phase file naming convention changes | Low | Medium | Regex pattern is a module-level constant -- single point of change. Integration tests use real directory fixtures. |
| Index file format varies across projects | Medium | Low | Discovery has two strategies (index parse + directory scan). If index parsing fails, directory scan provides fallback. |

---

## M3: Process Management & Signal Handling

### Objective

Implement subprocess lifecycle management and signal handling. This is the highest-risk module because it interacts with OS-level primitives (process groups, signals, file handles). It depends only on M1 types and stdlib. Must be testable with mocked subprocess.Popen -- no actual claude binary required.

### Architectural Rationale

Process management is isolated from execution orchestration (the "what to run" vs "how to run" separation). ClaudeProcess knows how to build commands, start processes, wait with timeout, and terminate gracefully. It does not know about phases, results, monitors, or TUI. SignalHandler is a standalone utility that sets a flag -- it does not call any other sprint module.

This separation means process management bugs (leaked file handles, zombie processes, signal races) are testable in a controlled environment without spinning up the full executor loop.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | `process.py`: `ClaudeProcess.build_prompt()` generating the `/sc:task-unified` invocation | Prompt contains phase file reference, compliance/strategy flags, execution rules, completion protocol with result file path, EXIT_RECOMMENDATION instructions. Verified by string assertion on known phase input. |
| D3.2 | `process.py`: `ClaudeProcess.build_command()` and `build_env()` | Command list includes `--print`, `--no-session-persistence`, `--max-turns N`, `--output-format text`, `-p <prompt>`. Model flag appended only when non-empty. Env dict contains `CLAUDECODE=""`. |
| D3.3 | `process.py`: `ClaudeProcess.start()`, `wait()`, `terminate()` with process group isolation | `start()` creates results directory, opens file handles, spawns Popen with `preexec_fn=os.setpgrp`. `wait()` returns exit code or 124 on timeout. `terminate()` sends SIGTERM to process group, waits 10s, then SIGKILL. File handles closed in all paths (success, timeout, terminate). |
| D3.4 | `process.py`: `SignalHandler` with install/uninstall and shutdown flag | `install()` registers SIGINT+SIGTERM handlers. `_handle()` sets `shutdown_requested=True`. `uninstall()` restores original handlers. Handlers are idempotent (double-signal does not crash). |
| D3.5 | `tests/sprint/test_process.py`: unit tests with mocked Popen | Command construction verified. Env verified. Timeout formula (`max_turns * 120 + 300`) verified. Terminate sequence verified with mock process group. Signal handler flag transition verified. File handle cleanup verified for all exit paths. |

### Dependencies

- **M1**: Phase, SprintConfig types (frozen contract)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `os.setpgrp` not available on Windows | Medium | High | Platform check with graceful fallback to direct Popen (no process group). Document Unix/macOS requirement. |
| Claude CLI `--print`/`--no-session-persistence` flags change | Medium | High | Command construction is a single method (`build_command`). Version-pin claude CLI in dev dependencies. Abstract flag names as class constants for single-point-of-change. |
| File handle leaks on exception paths | Medium | Medium | `_close_handles()` called in `wait()`, `terminate()`, and via finally blocks. Tests verify handle state after each exit path. |

---

## M4: Monitoring & TUI Display Layer

### Objective

Build the output monitor (daemon thread) and the Rich TUI dashboard. These are the observability layer -- they read state but never modify execution flow. The monitor depends only on M1 (MonitorState). The TUI depends only on M1 types and Rich. Neither imports config, process, executor, tmux, logging, or notify.

### Architectural Rationale

Monitor and TUI are grouped because they form a producer-consumer pair (monitor writes MonitorState scalars, TUI reads them) and share the same dependency profile (M1 only). They are architecturally "read-only" -- they observe execution but do not control it. This means TUI rendering bugs or monitor extraction errors cannot crash or halt a sprint.

The lock-free communication model (GIL-safe scalar writes on MonitorState fields) is a deliberate architectural choice that avoids deadlock risk. This is documented and tested.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | `monitor.py`: `OutputMonitor` with `start()`, `stop()`, `reset()`, daemon thread, incremental file reading | Daemon thread polls at 500ms. Reads only new bytes via `seek()`. Does not hold file open between polls. `reset()` clears state for new phase. `stop()` joins thread within 2s. |
| D4.2 | `monitor.py`: Signal extraction via regex (task IDs, tool names, file paths) and stall detection | TASK_ID_PATTERN matches `T##.##`. TOOL_PATTERN matches known tool names. FILES_CHANGED_PATTERN extracts file paths from modification messages. Stall counter increments when no growth detected. Growth rate computed as EMA with alpha=0.3. |
| D4.3 | `tui.py`: `SprintTUI` with `start()`, `stop()`, `update()`, `_render()` | Rich Live at 2 FPS. Panel contains header (elapsed time, index name), phase table, progress bar, active phase detail. Rendering errors caught and logged to stderr without aborting sprint. `_live_failed` flag silences repeated errors. |
| D4.4 | `tui.py`: Phase table with STATUS_STYLES/STATUS_ICONS, active phase detail panel, terminal state panels | Green for PASS variants, red for HALT/TIMEOUT/ERROR, yellow for RUNNING, dim for PENDING. Active panel shows file, stall status (with blink for >60s), last task/tool, output size, growth rate, files changed. Terminal panels: "ALL PHASES PASSED" (green) or halt details with resume command (red). |
| D4.5 | `tests/sprint/test_monitor.py` and `tests/sprint/test_tui.py` | Monitor: regex patterns verified against sample Claude output. Stall counter verified. Growth rate EMA verified. TUI: snapshot tests rendering to StringIO for RUNNING, PASS, HALT, STALLED states. >=85% coverage on both files. |

### Dependencies

- **M1**: MonitorState, Phase, SprintConfig, SprintResult, PhaseStatus types (frozen contract)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GIL-free Python (PEP 703) breaks lock-free scalar writes | Low | High | Add optional `threading.Lock` behind a flag. Document GIL dependency. Monitor writes only scalar fields (int, float, str) -- even without GIL, these are safe on CPython due to word-sized atomic writes. |
| Monitor regex misses new Claude output formats | Medium | Medium | Patterns are module-level constants -- single point of change. Integration tests use captured real-world output samples. |
| Rich Live conflicts with older tmux terminal capabilities | Low | Medium | Document minimum tmux 3.0+. `screen=False` avoids alternate screen buffer. Rendering errors caught and do not abort sprint. |

---

## M5: Orchestration & Integration

### Objective

Wire all components together: the executor core loop (`executor.py`), tmux session management (`tmux.py`), dual-format logging (`logging_.py`), desktop notifications (`notify.py`), and the CLI command wiring (`commands.py`). This is the only milestone where cross-module imports are permitted beyond models.py.

### Architectural Rationale

This milestone exists precisely because the architect variant defers all integration to a single, explicit milestone rather than distributing it across M2 (as the base roadmap does). The executor is the composition root -- it imports config, process, monitor, TUI, logger, notifier, and tmux. By building all leaf modules first (M2-M4) and integrating last, we guarantee that:

1. Each leaf module works in isolation (proven by M2-M4 tests).
2. Integration bugs are confined to this milestone and cannot be confused with leaf-module bugs.
3. The executor's control flow (the phase loop, status determination, halt/continue decision) is tested against already-validated components.

The tmux, logging, and notify modules are also integrated here because they are cross-cutting concerns that touch multiple other modules but are small enough (80-200 lines each) to not warrant standalone milestones.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | `executor.py`: `execute_sprint()` orchestration loop and `_determine_phase_status()` | Iterates `config.active_phases`. For each phase: resets monitor, starts monitor thread, launches ClaudeProcess, polls with 0.5s sleep until process exits or deadline reached, determines phase status via 7-level priority chain, records PhaseResult, decides continue/halt. Signal handler checked each poll iteration. Claude binary pre-flight check. Monotonic deadline enforcement. Finally block cleans up monitor, process, TUI, signal handler independently. |
| D5.2 | `tmux.py`: Session management (`is_tmux_available`, `session_name`, `find_running_session`, `launch_in_tmux`, `attach_to_sprint`, `kill_sprint`, `update_tail_pane`) | Deterministic session name: `sc-sprint-{sha1(release_dir)[:8]}`. Two-pane layout: 75% TUI, 25% tail. Auto-detect tmux binary and TMUX env var. Bottom pane updates on phase change. Session cleaned up on setup failure. Exit code read from sentinel file. |
| D5.3 | `logging_.py`: `SprintLogger` with `write_header`, `write_phase_start`, `write_phase_interrupt`, `write_phase_result`, `write_summary` | JSONL events contain all documented fields (event type, timestamps, phase info, status, metrics). Markdown table appended per phase. Summary includes outcome, duration, halt phase, resume command. Error events produce terminal bell. Screen output uses stderr (TUI uses stdout). `read_status_from_log()` and `tail_log()` stubs present. |
| D5.4 | `notify.py`: Cross-platform notifications + `commands.py`: full CLI wiring | `_notify()` detects Linux (notify-send) vs macOS (osascript). 5s timeout. Silent failure. `notify_phase_complete` fires on success/failure. `notify_sprint_complete` fires on completion. Commands: `run` (all options wired, dry-run, tmux decision), `attach`, `status`, `logs`, `kill`. Lazy imports in command handlers. |
| D5.5 | `tests/sprint/test_executor.py`: integration tests with mocked ClaudeProcess | PASS flow: 3 phases all succeed, outcome=SUCCESS. HALT flow: phase 2 fails, phases 3+ skipped, outcome=HALTED, resume_command present. TIMEOUT flow: exit_code=124, outcome=HALTED. INTERRUPTED flow: signal_handler.shutdown_requested during poll, outcome=INTERRUPTED. Status determination: all 7 priority levels verified with fixture result files. |

### Dependencies

- **M2**: `load_sprint_config`, `discover_phases` (config loading)
- **M3**: `ClaudeProcess`, `SignalHandler` (process lifecycle)
- **M4**: `OutputMonitor`, `SprintTUI` (observability layer)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Integration surface complexity -- executor imports 7 peer modules | Medium | High | Each peer module is fully tested in isolation (M2-M4). Integration tests mock at the subprocess boundary, not at module boundaries. The executor's own logic (poll loop, status determination, halt decision) is thin orchestration code. |
| Tmux unavailable in CI/container environments | Medium | Low | `--no-tmux` flag bypasses tmux entirely. All tmux calls are mocked in tests. `is_tmux_available()` checks both binary and TMUX env var. |
| Race between process exit and monitor thread final poll | Low | Medium | Monitor stop is called after process wait completes. A final `_poll_once()` could be added before stop to capture last bytes. Current design accepts that the last 500ms of output may be missed in monitor state (logged to file regardless). |
| TUI rendering error during phase transition | Low | Low | TUI update wrapped in try/except in both executor poll loop and TUI.update(). `_live_failed` flag prevents repeated error spam. Sprint continues regardless of TUI state. |

---

## M6: End-to-End Validation & Acceptance

### Objective

Validate the complete system through end-to-end tests, CLI contract verification, regression gap tests, and integration tests that exercise cross-module paths. This milestone proves the system meets all 8 success criteria (SC-001 through SC-008) from the extraction.

### Architectural Rationale

Validation is a separate milestone (not distributed across M2-M5) because the architect perspective demands that acceptance testing operates at the system boundary, not the module boundary. Module-level tests (in M2-M5) prove correctness of individual components. E2E tests prove that the composed system behaves correctly under realistic scenarios including:
- Multi-phase sprints completing successfully
- Halted sprints producing resume commands
- Signal interrupts producing clean shutdown
- CLI subcommand contracts matching specification

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | `test_e2e_success.py`: Full sprint to completion | Mock Claude subprocess executing a 3-phase sprint. All phases PASS. Execution log written with correct JSONL events and Markdown table. Final outcome SUCCESS. TUI renders complete state. |
| D6.2 | `test_e2e_halt.py`: Sprint halted at phase 2 | Phase 2 produces HALT signal. Phases 3+ not executed. Resume command in log and SprintResult. TUI shows halted state with resume command. |
| D6.3 | `test_cli_contract.py`: All 5 subcommands match spec | `sprint run --help` shows all documented options with correct types and defaults. `sprint attach`, `sprint status`, `sprint logs`, `sprint kill` all registered and respond to --help. Option names and types match spec Section 3.2-3.6. |
| D6.4 | `test_integration_signal.py` + `test_integration_halt.py` + `test_integration_lifecycle.py`: Cross-cutting integration paths | Signal handler triggers graceful shutdown during execution. Halt produces correct SprintOutcome. Lifecycle test exercises PENDING->RUNNING->PASS and PENDING->RUNNING->HALT transitions end-to-end. |
| D6.5 | `test_regression_gaps.py`: Edge cases and boundary conditions | Empty phase list handling. Phase gaps (1, 2, 4 -- gap at 3). Stall detection at 30s and 60s boundaries. Timeout computation edge cases. Resume command generation with various start/end ranges. |

### Dependencies

- **M5**: All source modules must be complete and individually tested

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| E2E tests flaky due to subprocess timing | Low | Medium | All tests use mocked subprocess with deterministic behavior. No real process spawning in CI. Timeouts set conservatively. |
| CLI contract drift from spec | Low | Medium | Contract tests are generated from extraction FR-001 through FR-008. Any spec update triggers contract test update. |

---

## Risk Register (Consolidated)

| ID | Risk | Affected | Probability | Impact | Mitigation |
|----|------|----------|-------------|--------|------------|
| R-01 | Claude CLI `--print`/`--no-session-persistence` flags change | M3, M5 | Medium | High | Abstract flags as constants in `ClaudeProcess`; version-pin claude CLI |
| R-02 | `os.setpgrp` unavailable on Windows | M3 | Medium | High | Platform guard with fallback to direct Popen; document Unix/macOS requirement |
| R-03 | GIL-free Python (PEP 703) breaks lock-free monitor | M4 | Low | High | Optional threading.Lock; scalar-only writes are word-sized atomic |
| R-04 | Monitor regex misses new Claude output formats | M4, M5 | Medium | Medium | Centralized patterns; integration tests with captured output samples |
| R-05 | Rich Live conflicts with older tmux | M4, M5 | Low | Medium | Document min tmux 3.0+; `screen=False`; rendering errors non-fatal |
| R-06 | Tmux unavailable in CI/containers | M5 | Medium | Low | `--no-tmux` flag; all tmux calls mocked in tests |
| R-07 | Phase naming convention changes | M2 | Low | Medium | Regex is module-level constant; directory scan fallback |
| R-08 | Long-running sprints (>2h) resource growth | M4, M5 | Low | Medium | Per-phase state reset in monitor; bounded `_seen_files` set |
| R-09 | Desktop notification deps missing | M5 | Low | Low | Best-effort silent failure; documented as optional |
| R-10 | File handle leaks on exception paths | M3 | Medium | Medium | `_close_handles()` in all exit paths; tests verify handle state |
| R-11 | Integration surface complexity (executor imports 7 modules) | M5 | Medium | High | Leaf modules proven in isolation first; integration tests mock at subprocess boundary |
| R-12 | Data model changes cascade to all consumers | M2-M5 | Medium | Low | Additive-only changes (new fields with defaults); properties isolate computation |

---

## Architectural Observations on Existing Implementation

Having reviewed all 11 source files (~1,850 actual lines), I note the following deviations and concerns that this roadmap's validation phases should verify:

1. **SKIPPED enum removed**: The implementation removed `PhaseStatus.SKIPPED` with a code comment explaining the rationale. The spec includes SKIPPED (9 states), the implementation has 8 states. M1/D1.1 should confirm this is intentional and that no downstream code path produces or consumes SKIPPED.

2. **Stub functions in logging_.py**: `read_status_from_log()` and `tail_log()` are stubs that print "not yet connected" messages. The `status` and `logs` CLI subcommands exist but are non-functional. M5/D5.3 should either complete these or document them as deferred.

3. **Executor accesses `proc_manager._process.poll()`**: Direct access to the private `_process` attribute breaks the ClaudeProcess encapsulation. M5 should consider adding a `poll()` method to ClaudeProcess to preserve the abstraction boundary.

4. **MonitorState threading safety**: The monitor writes multiple fields per poll cycle (output_bytes, stall_seconds, growth_rate_bps, etc.). While individual scalar writes are GIL-safe, a TUI read could observe a partially-updated state (e.g., new output_bytes but old stall_seconds). This is acceptable for display purposes but should be documented.

5. **Tmux session cleanup on failure**: `launch_in_tmux` has a try/except that kills the session on post-creation setup failure. This is good defensive programming. M5/D5.2 should verify this path.

---

## Success Criteria Mapping

| ID | Criterion | Validates Milestone(s) |
|----|-----------|------------------------|
| SC-001 | All 5 CLI subcommands functional | M1 (group registration), M5 (wiring), M6 (contract) |
| SC-002 | Phase discovery with 4 naming conventions | M2 (discovery), M6 (regression) |
| SC-003 | TUI renders in tmux and non-tmux modes | M4 (TUI), M5 (tmux), M6 (E2E) |
| SC-004 | Sprint halts on failure with resume command | M3 (signal), M5 (executor), M6 (E2E halt) |
| SC-005 | Signal handling produces clean shutdown | M3 (SignalHandler), M5 (executor), M6 (integration) |
| SC-006 | JSONL and Markdown logs correct | M5 (logging), M6 (E2E) |
| SC-007 | Monitor extracts task IDs, tools, file paths | M4 (monitor), M6 (regression) |
| SC-008 | Full test suite passes >=80% coverage | M6 (all tests) |

---

## Key Differences from Base Roadmap

| Aspect | Base Roadmap (7 milestones) | Architect Variant (6 milestones) |
|--------|---------------------------|--------------------------------|
| M2 scope | Monolithic: CLI + Config + Process + Executor (8 deliverables, L effort) | Split: Config only (4 deliverables, S effort) |
| Process mgmt | Inside M2 with CLI and config | Standalone M3 (5 deliverables, M effort) |
| Executor | Inside M2 (coupled with process mgmt) | Deferred to M5 as pure integration |
| Validation checkpoints | 2 explicit (M4 + M7) | 1 explicit (M6) + per-milestone unit tests |
| Parallel width | 2 (M2 \|\| M3) | 3 (M2 \|\| M3 \|\| M4) |
| Critical path length | M1->M2->M5->M6->M7 (5 hops) | M1->M3->M5->M6 (4 hops) |
| Total milestones | 7 | 6 |
| Integration surface | Distributed across M2 and M5 | Concentrated in M5 only |

**Trade-off**: The architect variant has fewer validation checkpoints (1 vs 2) but compensates by requiring each milestone to include its own unit tests as deliverables. The base roadmap's M4 (Validation Checkpoint 1) is absorbed into M5 and M6 integration testing.
