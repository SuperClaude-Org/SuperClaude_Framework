---
spec_source: docs/design/sprint-cli-specification.md
generated: "2026-02-25T12:00:00Z"
generator: sc:roadmap
complexity_score: 0.69
complexity_class: MEDIUM
domain_distribution:
  backend: 52
  frontend: 23
  performance: 13
  documentation: 8
  security: 4
primary_persona: backend
consulting_personas: [architect, frontend]
milestone_count: 7
milestone_index:
  - id: M1
    title: "Foundation: Data Models & Project Scaffolding"
    type: FEATURE
    priority: P0
    effort: S
    dependencies: []
    deliverable_count: 4
    risk_level: Low
  - id: M2
    title: "Backend Core: CLI, Config & Process Management"
    type: FEATURE
    priority: P0
    effort: L
    dependencies: [M1]
    deliverable_count: 8
    risk_level: Medium
  - id: M3
    title: "TUI Dashboard & Output Monitor"
    type: FEATURE
    priority: P1
    effort: M
    dependencies: [M1]
    deliverable_count: 6
    risk_level: Low
  - id: M4
    title: "Validation Checkpoint 1"
    type: TEST
    priority: P3
    effort: S
    dependencies: [M2, M3]
    deliverable_count: 3
    risk_level: Low
  - id: M5
    title: "Integration: Tmux, Logging & Notifications"
    type: FEATURE
    priority: P1
    effort: M
    dependencies: [M2, M3]
    deliverable_count: 6
    risk_level: Medium
  - id: M6
    title: "Testing & Hardening"
    type: TEST
    priority: P2
    effort: M
    dependencies: [M5]
    deliverable_count: 5
    risk_level: Medium
  - id: M7
    title: "Final Validation & Acceptance"
    type: TEST
    priority: P3
    effort: S
    dependencies: [M4, M6]
    deliverable_count: 3
    risk_level: Low
total_deliverables: 35
total_risks: 9
estimated_phases: 6
validation_score: 0.92
validation_status: PASS
---

# Roadmap: `superclaude sprint` CLI

## Overview

This roadmap defines the implementation plan for the `superclaude sprint` CLI command — a multi-phase sprint executor that replaces the existing `execute-sprint.sh` shell script. The scope is ~2,160 lines of Python across 11 files in `src/superclaude/cli/sprint/`, targeting SuperClaude v4.3.0.

The approach follows a layered strategy: pure data models first (zero dependencies), then the two independent vertical slices (backend process orchestration and frontend TUI dashboard) in parallel, followed by integration of cross-cutting concerns (tmux, logging, notifications), and finally comprehensive testing. Validation checkpoints are interleaved at a 1:2 ratio (MEDIUM complexity) to catch integration issues before they compound.

Key architectural decisions: Click for CLI structure (consistent with existing `superclaude` commands), Rich for TUI (already a project dependency), GIL-safe lock-free threading for monitor-TUI communication, and process group isolation for reliable child process cleanup.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation: Data Models & Project Scaffolding | FEATURE | P0 | S | None | 4 | Low |
| M2 | Backend Core: CLI, Config & Process Management | FEATURE | P0 | L | M1 | 8 | Medium |
| M3 | TUI Dashboard & Output Monitor | FEATURE | P1 | M | M1 | 6 | Low |
| M4 | Validation Checkpoint 1 | TEST | P3 | S | M2, M3 | 3 | Low |
| M5 | Integration: Tmux, Logging & Notifications | FEATURE | P1 | M | M2, M3 | 6 | Medium |
| M6 | Testing & Hardening | TEST | P2 | M | M5 | 5 | Medium |
| M7 | Final Validation & Acceptance | TEST | P3 | S | M4, M6 | 3 | Low |

## Dependency Graph

```
M1 → M2 ──→ M4 ──→ M7
 ↓         ↗    ↗
M1 → M3 ──→ M5 → M6 ──→ M7
```

**Critical path**: M1 → M2 → M5 → M6 → M7

**Parallel opportunity**: M2 and M3 can execute concurrently after M1.

---

## M1: Foundation: Data Models & Project Scaffolding

### Objective

Establish the pure-data foundation (`models.py`) and project file structure. All other milestones depend on these dataclasses and enums.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `models.py` with PhaseStatus, SprintOutcome enums and Phase, SprintConfig, PhaseResult, SprintResult, MonitorState dataclasses | All 7 types defined per spec Section 2; property methods (`is_terminal`, `is_success`, `is_failure`, `duration_display`, `resume_command`, `stall_status`) pass unit tests |
| D1.2 | Sprint module `__init__.py` with Click group export | `from superclaude.cli.sprint import sprint_group` importable |
| D1.3 | Integration point in `main.py`: `main.add_command(sprint_group, name="sprint")` | `superclaude sprint --help` displays group help |
| D1.4 | `tests/sprint/__init__.py` and `test_models.py` with unit tests for all enum properties and dataclass aggregations | All tests pass; ≥90% coverage on models.py |

### Dependencies

- None (foundation milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data model changes needed during later milestones | Medium | Low | Dataclasses are easily extensible; properties isolate change impact |

---

## M2: Backend Core: CLI, Config & Process Management

### Objective

Implement the CLI command interface (`commands.py`), phase discovery and configuration (`config.py`), subprocess management (`process.py`), and the core executor loop (`executor.py`). This is the largest milestone and forms the execution backbone.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `commands.py`: Click command group with `run`, `attach`, `status`, `logs`, `kill` subcommands and all documented options | `superclaude sprint run --help` shows all options per spec Section 3.2; option types and defaults match spec |
| D2.2 | `config.py`: `discover_phases()` function supporting 4 naming conventions (phase-N, pN, Phase_N, tasklist-PN) | Unit tests verify all 4 naming patterns; index-first and directory-fallback strategies both work |
| D2.3 | `config.py`: `validate_phases()` detecting missing files and sequence gaps | Error messages for missing files; warning messages for gaps; gap between phases 2→4 detected |
| D2.4 | `config.py`: `load_sprint_config()` combining discovery, validation, and auto-detection | Full config loaded from sample index; end_phase auto-detected; errors abort with ClickException |
| D2.5 | `process.py`: `ClaudeProcess` class with `build_prompt()`, `build_command()`, `build_env()`, `start()`, `wait()`, `terminate()` | Command includes `--print`, `--no-session-persistence`, `--max-turns`, `--output-format text`; prompt contains `/sc:task-unified` invocation; process group created with `os.setpgrp` |
| D2.6 | `process.py`: `SignalHandler` with SIGINT/SIGTERM handling | `shutdown_requested` flag set on signal; original handlers restored on uninstall |
| D2.7 | `executor.py`: Main `execute_sprint()` orchestration loop | Iterates active phases; launches subprocess per phase; polls until process exits; determines phase status per priority chain (spec Section 8); halts on failure status |
| D2.8 | `executor.py`: `_determine_phase_status()` implementing 7-level status priority | Timeout (exit 124) → ERROR (non-zero) → HALT signal → CONTINUE signal → PASS/FAIL frontmatter → PASS_NO_REPORT → ERROR |

### Dependencies

- M1: Phase, SprintConfig, PhaseResult, SprintResult, PhaseStatus, SprintOutcome dataclasses

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Claude CLI `--print` or `--no-session-persistence` flags change | Medium | High | Version-pin claude CLI in dev dependencies; abstract command construction for easy updates |
| `os.setpgrp` not available on Windows | Medium | High | Platform check in process.py; document Unix/macOS requirement; graceful fallback to direct Popen |
| Phase file naming convention changes | Low | Medium | Regex pattern is configurable; add integration test with real directory structures |

---

## M3: TUI Dashboard & Output Monitor

### Objective

Build the Rich-based terminal UI (`tui.py`) and sidecar output monitor thread (`monitor.py`). These components provide real-time visibility into sprint execution.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | `tui.py`: `SprintTUI` class with `start()`, `stop()`, `update()`, `_render()` methods | Live display at 2 FPS; panel contains header, phase table, progress bar, active phase detail |
| D3.2 | `tui.py`: Phase table with color-coded status rendering per STATUS_STYLES and STATUS_ICONS mappings | Green for PASS, red for HALT/TIMEOUT/ERROR, yellow for RUNNING, dim for pending/skipped |
| D3.3 | `tui.py`: Active phase detail panel showing file, status, stall indicator, last task/tool, output size, growth rate, files changed | Panel updates on each `tui.update()` call; stall display shows "STALLED" (red blink) after 60s, "thinking..." (yellow) after 30s |
| D3.4 | `tui.py`: Sprint complete and halted terminal states | Complete state shows "ALL PHASES PASSED" with total duration; halted state shows failure details and resume command |
| D3.5 | `monitor.py`: `OutputMonitor` class with `start()`, `stop()`, `reset()` and background polling | Daemon thread polls at 500ms; reads only new bytes since last position; extracts signals without holding file open |
| D3.6 | `monitor.py`: Signal extraction via regex patterns for task IDs (T##.##), tool names, and file paths | Correctly parses task IDs, tool names (Read, Edit, Bash, etc.), and file modification patterns from sample output |

### Dependencies

- M1: MonitorState, Phase, SprintConfig, SprintResult, PhaseStatus dataclasses

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Rich Live display conflicts with older tmux versions | Low | Medium | Document minimum tmux version; test with tmux 3.0+ and 2.x |
| Monitor regex misses new Claude output formats | Medium | Medium | Patterns are centralized; add integration test with real Claude output samples |

---

## M4: Validation Checkpoint 1

### Objective

Verify that M2 (backend core) and M3 (TUI + monitor) integrate correctly. Validate the executor can launch processes and update the TUI via monitor state.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Integration test: executor with mocked ClaudeProcess drives TUI through full phase lifecycle (PENDING → RUNNING → PASS) | Test renders TUI to StringIO; status transitions verified in output |
| D4.2 | Integration test: executor halts on STRICT-tier failure and produces resume command | Halted sprint result contains correct resume_command(); TUI shows halted state |
| D4.3 | Integration test: signal handler triggers graceful shutdown during execution | SIGINT during poll loop → process terminated → partial log written → INTERRUPTED outcome |

### Dependencies

- M2: executor.py, process.py, config.py
- M3: tui.py, monitor.py

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Integration issues between executor polling and TUI refresh | Low | Medium | Mock-based testing isolates timing; acceptance criteria focus on state transitions not timing |

---

## M5: Integration: Tmux, Logging & Notifications

### Objective

Wire the cross-cutting concerns: tmux session management for detachable execution, dual-format structured logging, and desktop notifications. These components complete the user-facing experience.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | `tmux.py`: `is_tmux_available()`, `session_name()`, `find_running_session()` utility functions | Detects tmux binary; generates deterministic session name from release dir hash; finds sc-sprint-* sessions |
| D5.2 | `tmux.py`: `launch_in_tmux()` creating detached session with two-pane layout (75% TUI / 25% tail) | Tmux commands verified via mocked subprocess.run; correct pane split and session naming |
| D5.3 | `tmux.py`: `attach_to_sprint()`, `kill_sprint()`, `update_tail_pane()` session management | Attach reconnects to running session; kill sends SIGTERM then SIGKILL after 10s; tail pane switches output file on phase change |
| D5.4 | `logging_.py`: `SprintLogger` class with `write_header()`, `write_phase_result()`, `write_summary()` | JSONL events contain all documented fields; Markdown table rows appended correctly; summary includes outcome, duration, resume command |
| D5.5 | `logging_.py`: Log levels (DEBUG→JSONL only, INFO→all, WARN/ERROR→highlighted+bell) | Error events produce terminal bell (\a); screen output goes to stderr (TUI uses stdout) |
| D5.6 | `notify.py`: Cross-platform desktop notifications via `notify-send` (Linux) and `osascript` (macOS) | Platform detection correct; notifications fail silently with 5s timeout; urgent flag sets critical urgency |

### Dependencies

- M2: SprintConfig, ClaudeProcess (tmux wraps the foreground command)
- M3: SprintTUI (tmux top pane runs the TUI)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Tmux unavailable in CI/container environments | Medium | Low | `--no-tmux` fallback already designed; tests mock tmux entirely |
| Desktop notification deps not installed | Low | Low | Best-effort pattern with silent failure; documented as optional |

---

## M6: Testing & Hardening

### Objective

Build the full test suite with unit tests for all modules and integration tests for the executor. Harden edge cases: empty phases, sequence gaps, stall detection, timeout handling.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | `test_config.py`: Phase discovery (index parsing, directory fallback, flexible naming), validation (missing files, gaps) | All 4 naming conventions tested; gap detection verified; missing file error messages correct |
| D6.2 | `test_monitor.py`: Signal extraction from mock output files (task IDs, tools, file paths, stall detection) | Regex patterns verified against sample Claude output; stall counter increments when no growth |
| D6.3 | `test_process.py`: Command construction, env building, timeout calculation | Command contains all required flags; CLAUDECODE="" in env; timeout = max_turns*120+300 |
| D6.4 | `test_tui.py`: Snapshot tests rendering to StringIO for all TUI states (running, complete, halted, stalled) | Console output matches expected snapshots for each state variant |
| D6.5 | `test_executor.py`: Full integration test with mocked subprocess covering PASS, HALT, TIMEOUT, INTERRUPTED flows | Each outcome produces correct SprintResult; HALTED includes resume command; TIMEOUT returns exit 124 |

### Dependencies

- M5: All source modules must be complete before comprehensive testing

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GIL-free Python (PEP 703) breaks lock-free monitor pattern | Low | High | Add threading lock as optional safety; document GIL dependency; test with free-threading builds when available |
| Long-running sprint resource growth in monitor | Low | Medium | Monitor resets state per phase; seen_files set bounded by phase scope |

---

## M7: Final Validation & Acceptance

### Objective

End-to-end validation of the complete sprint CLI. Verify all CLI subcommands work together, tmux integration is functional, and the system handles real-world scenarios.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D7.1 | E2E test: `superclaude sprint run` with mock Claude subprocess executing a 3-phase sprint to completion | All 3 phases PASS; execution log written with correct JSONL events and Markdown table; final outcome SUCCESS |
| D7.2 | E2E test: `superclaude sprint run` with mock failure at phase 2 producing HALTED outcome with resume command | Phase 2 HALT; phases 3+ not executed; resume command in log; TUI shows halted state |
| D7.3 | CLI contract validation: all 5 subcommands match documented help text and option signatures | `--help` output for each subcommand matches spec Section 3.3 |

### Dependencies

- M4: Earlier validation results inform any rework
- M6: Full test suite must pass before acceptance

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| E2E tests flaky due to subprocess timing | Low | Medium | Use mocked subprocess with deterministic behavior; avoid real process spawning in CI |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Claude CLI `--print`/`--no-session-persistence` flags change in future versions | M2, M6 | Medium | High | Version-pin in dev dependencies; abstract command construction | backend |
| R-002 | Rich Live display conflicts with older tmux versions | M3, M5 | Low | Medium | Document min tmux version; test with tmux 3.0+ and 2.x | frontend |
| R-003 | `os.setpgrp` not available on Windows | M2 | Medium | High | Platform check with graceful fallback; document Unix/macOS req | backend |
| R-004 | GIL-free Python (PEP 703) breaks lock-free monitor pattern | M3, M6 | Low | High | Add optional threading lock; document GIL dependency | backend |
| R-005 | Monitor regex misses new Claude output formats | M3, M6 | Medium | Medium | Centralized patterns; integration tests with real output samples | backend |
| R-006 | Tmux unavailable in CI/container environments | M5 | Medium | Low | `--no-tmux` fallback; mock-based testing | backend |
| R-007 | Phase file naming convention changes | M2 | Low | Medium | Configurable regex; integration tests with directory fixtures | backend |
| R-008 | Long-running sprints (>2h) hit resource limits | M2, M3 | Low | Medium | Per-phase state reset; bounded data structures | backend |
| R-009 | Desktop notification deps not installed | M5 | Low | Low | Best-effort silent failure; documented as optional | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend | architect (0.91 generalist), frontend (0.16) | Highest domain-specific confidence; backend domain at 52% |
| Template | inline (Tier 4) | No templates found in Tiers 1-3 | No project or user templates exist; inline generation from extraction data |
| Milestone Count | 7 (5 work + 2 validation) | Range 5-7 (MEDIUM class) | MEDIUM base(5) + floor(3 domains ≥10% / 2) = 6 candidate slots; 5 work milestones + 2 validation at 1:2 interleave = 7 total; within range |
| Adversarial Mode | none | N/A | No --specs or --multi-roadmap flags provided |
| Adversarial Base Variant | N/A | N/A | Adversarial mode not active |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | All 5 CLI subcommands (run, attach, status, logs, kill) functional | M1, M2, M7 | Yes |
| SC-002 | Phase discovery works with all 4 naming conventions | M2, M6 | Yes |
| SC-003 | TUI renders correctly in tmux and non-tmux modes | M3, M5, M7 | Yes |
| SC-004 | Sprint halts on STRICT-tier failure and produces resume command | M2, M4, M7 | Yes |
| SC-005 | Signal handling produces clean shutdown and partial log | M2, M6 | Yes |
| SC-006 | JSONL and Markdown logs contain all required fields | M5, M6 | Yes |
| SC-007 | Monitor extracts task IDs, tool names, and file paths | M3, M6 | Yes |
| SC-008 | Full test suite passes with ≥80% coverage | M6, M7 | Yes |
