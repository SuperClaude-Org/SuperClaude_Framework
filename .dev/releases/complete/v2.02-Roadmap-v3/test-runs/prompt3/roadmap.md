---
spec_source: .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
generated_by: sc:roadmap v2.0.0
generated_at: "2026-03-03"
complexity_score: 0.624
complexity_class: MEDIUM
milestone_count: 6
primary_persona: backend
template: inline
domain_distribution:
  backend: 72
  frontend: 18
  performance: 6
  security: 2
  documentation: 2
validation_status: PASS
validation_score: 0.87
adversarial:
  mode: multi-roadmap
  agents: ["opus:architect", "sonnet:security"]
  convergence_score: 0.82
  base_variant: "opus:architect"
  artifacts_dir: .dev/releases/current/v2.05-sprint-cli-specification/prompt3/
---

# Roadmap: `superclaude sprint` CLI

## Overview

Implementation roadmap for the `superclaude sprint` CLI module — a multi-phase sprint execution orchestrator for SuperClaude v4.3.0. Replaces the existing `execute-sprint.sh` bash script with a Python implementation featuring tmux integration, Rich TUI dashboard, sidecar monitoring, and structured logging.

**Complexity**: MEDIUM (0.624) — 6 milestones, 1:2 interleave ratio
**Estimated scope**: ~2,160 lines across 11 files in `src/superclaude/cli/sprint/`
**Dependencies**: Zero new — uses existing click + rich + stdlib

## Milestone Summary

| ID | Milestone | Effort | Dependencies | Key Deliverables |
|----|-----------|--------|-------------|------------------|
| M1 | Data Models & Package Init | S | — | models.py, __init__.py |
| M2 | Config, Process & Signal Handling | M | M1 | config.py, process.py |
| M3 | Executor Core Loop & Monitor | L | M2 | executor.py, monitor.py |
| M4 | TUI Dashboard & Logging | M | M3 | tui.py, logging_.py |
| M5 | Tmux Integration & CLI Commands | M | M3 | tmux.py, commands.py, notify.py |
| M6 | Integration Testing & Quality Gates | M | M4, M5 | Test suite, migration shim |

**Effort key**: S = Small (1-2 days), M = Medium (2-4 days), L = Large (4-6 days)

## Dependency Graph

```
M1 (Models)
 └──▶ M2 (Config + Process)
       └──▶ M3 (Executor + Monitor)
             ├──▶ M4 (TUI + Logging)
             └──▶ M5 (Tmux + CLI + Notify)
                    └──┐
             M4 ──────▶ M6 (Integration + Quality)
```

M4 and M5 can execute in parallel after M3 completes.

---

## M1: Data Models & Package Init

**Objective**: Establish the pure-data foundation with all dataclasses, enums, and package structure.

**Deliverables**:
| ID | Deliverable | Requirements |
|----|------------|-------------|
| D1.1 | `models.py` — PhaseStatus enum with is_terminal, is_success, is_failure properties | FR-040, FR-041, FR-042 |
| D1.2 | `models.py` — SprintOutcome enum (SUCCESS, HALTED, INTERRUPTED, ERROR) | FR-041 |
| D1.3 | `models.py` — Phase, SprintConfig, PhaseResult, SprintResult, MonitorState dataclasses | FR-040, FR-041, FR-042, NFR-002 |
| D1.4 | `models.py` — Computed properties: active_phases, output_file, duration_display, resume_command | FR-036, FR-040 |
| D1.5 | `__init__.py` — Click group definition and exports | FR-001 |

**Dependencies**: None

**Risk Assessment**:
- Low risk — pure data structures with no external dependencies
- Ensure PhaseStatus enum covers all 8 states from spec

**Effort**: S (1-2 days) — ~200 lines, pure dataclasses

**Acceptance Criteria**:
- All dataclass fields match spec Section 2
- Property methods return correct values for edge cases (empty phases, zero duration)
- Unit tests for PhaseStatus properties (is_terminal, is_success, is_failure)
- Unit tests for SprintResult aggregation (phases_passed, phases_failed)

---

## M2: Config, Process & Signal Handling

**Objective**: Implement phase discovery, configuration loading, subprocess management, and signal handling with secure input validation.

**Deliverables**:
| ID | Deliverable | Requirements |
|----|------------|-------------|
| D2.1 | `config.py` — Phase discovery from index file with regex parsing | FR-003, FR-004, FR-005 |
| D2.2 | `config.py` — Phase validation: missing files, sequence gaps | FR-006 |
| D2.3 | `config.py` — `load_sprint_config()` with validation and error reporting | FR-002, FR-040 |
| D2.4 | `process.py` — ClaudeProcess: command building, env construction, process groups | FR-008, FR-009, NFR-008 |
| D2.5 | `process.py` — Graceful shutdown: SIGTERM → 10s → SIGKILL | FR-010, NFR-005 |
| D2.6 | `process.py` — Phase timeout enforcement (max_turns * 120 + 300s) | FR-011, NFR-005 |
| D2.7 | `process.py` — SignalHandler: SIGINT/SIGTERM → shutdown flag | FR-035 |
| D2.8 | `process.py` — `/sc:task-unified` prompt generation per phase | FR-038 |

**Dependencies**: M1 (Phase, SprintConfig, PhaseResult dataclasses)

**Risk Assessment**:
| Risk | Mitigation |
|------|-----------|
| R-001: Claude CLI interface changes | Abstract command construction behind method; version-pin expected flags |
| R-005: Signal handling race conditions | Use threading.Event for shutdown flag; test with concurrent signals |
| R-006: OS-specific process group behavior | Test on Linux and macOS; document Windows incompatibility |

**Security Considerations** (from sonnet:security variant):
- Validate phase file paths exist before executing (no path traversal)
- Sanitize model parameter (alphanumeric + hyphens only)
- Environment variable isolation: CLAUDECODE="" prevents nested sessions

**Effort**: M (2-4 days) — ~580 lines (config ~200 + process ~180 + tests)

**Acceptance Criteria**:
- Phase discovery works with all naming conventions (phase-N, pN, Phase_N, tasklist-PN)
- Directory fallback triggers when index has no phase refs
- Gap detection produces warnings, missing files produce errors
- Command construction includes all required flags
- Signal handler sets flag without raising
- Process group kill terminates child tree

---

## M3: Executor Core Loop & Monitor

**Objective**: Implement the main orchestration loop and sidecar monitoring thread. This is the largest and most critical milestone.

**Deliverables**:
| ID | Deliverable | Requirements |
|----|------------|-------------|
| D3.1 | `executor.py` — `execute_sprint()` main loop: iterate phases, launch, poll, collect results | FR-007 |
| D3.2 | `executor.py` — Phase status determination: 7-priority exit code + result file parsing | FR-012, FR-013 |
| D3.3 | `executor.py` — Halt-on-failure logic: stop on STRICT-tier failure | FR-012 |
| D3.4 | `executor.py` — Shutdown integration: check signal handler flag in poll loop | FR-035 |
| D3.5 | `monitor.py` — OutputMonitor: daemon thread with 500ms polling | FR-014, NFR-003 |
| D3.6 | `monitor.py` — Signal extraction: task IDs, tool names, file paths | FR-015 |
| D3.7 | `monitor.py` — Stall detection and growth rate tracking (GIL-safe scalar writes) | FR-016, FR-017, NFR-006 |
| D3.8 | `monitor.py` — Incremental file reading (_read_new_bytes) | FR-014 |

**Dependencies**: M2 (ClaudeProcess, SignalHandler, SprintConfig)

**Risk Assessment**:
| Risk | Mitigation |
|------|-----------|
| R-003: GIL-safe shared state | Document CPython assumption; use threading.Lock as optional safety net |
| R-004: Disk space exhaustion | Log output file sizes in SprintLogger; warn if >100MB per phase |
| R-005: Race conditions | Sequential phase execution eliminates inter-phase races; monitor reads are idempotent |

**Effort**: L (4-6 days) — ~550 lines (executor ~300 + monitor ~250) plus integration tests

**Acceptance Criteria**:
- Executor runs phases sequentially, collects results
- HALT status stops further phase execution
- INTERRUPTED outcome set on signal receipt
- Monitor extracts task IDs matching T##.## pattern
- Monitor reports stall after 60s with no output growth
- Growth rate EMA converges to actual write rate
- Phase status correctly maps all 7 priority levels

---

## M4: TUI Dashboard & Logging

**Objective**: Implement the Rich-based terminal UI and dual-format logging system.

**Deliverables**:
| ID | Deliverable | Requirements |
|----|------------|-------------|
| D4.1 | `tui.py` — SprintTUI class with Live display at 2 FPS refresh | FR-018, NFR-004 |
| D4.2 | `tui.py` — Phase table with status-specific styling | FR-019 |
| D4.3 | `tui.py` — Overall progress bar | FR-018 |
| D4.4 | `tui.py` — Active phase detail panel with stall indicator | FR-020 |
| D4.5 | `tui.py` — Sprint complete and halted states | FR-021, FR-022 |
| D4.6 | `logging_.py` — SprintLogger: JSONL + Markdown dual-format | FR-027 |
| D4.7 | `logging_.py` — Event logging: sprint_start, phase_complete, sprint_complete events | FR-028 |
| D4.8 | `logging_.py` — Screen output with severity styling | FR-029 |

**Dependencies**: M3 (executor provides SprintResult, MonitorState data for display)

**Risk Assessment**:
| Risk | Mitigation |
|------|-----------|
| R-002: Rich + tmux resize | Rich handles SIGWINCH automatically; test manually on resize |

**Effort**: M (2-4 days) — ~500 lines (tui ~350 + logging ~150)

**Acceptance Criteria**:
- TUI renders all phase statuses with correct styling (green/red/yellow/dim)
- Progress bar shows accurate completion percentage
- Active panel displays monitor state (task ID, tool, output size, stall status)
- JSONL entries are valid JSON with required fields
- Markdown log has table format with all phase rows
- Screen output uses correct severity colors

---

## M5: Tmux Integration & CLI Commands

**Objective**: Wire up tmux session management, CLI subcommands, and desktop notifications. Can run in parallel with M4.

**Deliverables**:
| ID | Deliverable | Requirements |
|----|------------|-------------|
| D5.1 | `tmux.py` — Session management: create, attach, find, kill | FR-023, NFR-009 |
| D5.2 | `tmux.py` — Deterministic session naming from release dir hash | FR-024, NFR-009 |
| D5.3 | `tmux.py` — Pane layout: 75% TUI + 25% tail | FR-025 |
| D5.4 | `tmux.py` — `update_tail_pane()` for phase transitions | FR-023 |
| D5.10 | `tmux.py` — Reattach: terminal state preservation, Rich auto-redraw on reconnect | FR-026 |
| D5.5 | `commands.py` — `run` command: config loading, tmux decision, execution | FR-002 |
| D5.6 | `commands.py` — `attach`, `status`, `logs`, `kill` subcommands | FR-031, FR-032, FR-033, FR-034 |
| D5.7 | `commands.py` — Dry-run mode | FR-039 |
| D5.8 | `notify.py` — Desktop notifications (Linux + macOS), best-effort silent failure | FR-030, NFR-007, NFR-008 |
| D5.9 | `main.py` — Integration: add sprint_group | FR-037 |

**Dependencies**: M3 (executor.execute_sprint, ClaudeProcess for tmux command building)

**Risk Assessment**:
- Low-medium risk — tmux commands are well-documented
- Notification failures are silenced (best-effort design)

**Effort**: M (2-4 days) — ~550 lines (tmux ~200 + commands ~250 + notify ~80 + main.py ~20)

**Acceptance Criteria**:
- Tmux session created with correct name and pane layout
- Attach finds running session, reports when none found
- Kill sends SIGTERM with grace period, --force sends immediate SIGKILL
- Logs subcommand supports -n and -f flags
- Status reads JSONL log without requiring tmux
- Notifications sent on Linux (notify-send) and macOS (osascript)
- Sprint group accessible via `superclaude sprint --help`
- Tmux reattach preserves Rich TUI state (terminal buffer maintained by tmux)

---

## M6: Integration Testing & Quality Gates

**Objective**: End-to-end integration tests, migration shim, and quality validation.

**Deliverables**:
| ID | Deliverable | Requirements |
|----|------------|-------------|
| D6.1 | Integration test: full sprint lifecycle with mocked subprocess | SC-001 |
| D6.2 | Integration test: halt-on-failure stops execution | SC-004 |
| D6.3 | Integration test: signal handling (SIGINT) during execution | FR-035 |
| D6.4 | Snapshot tests: TUI render output verification | FR-018 |
| D6.5 | Test fixtures: sample-index.md, phase files, result files | FR-003, FR-006 |
| D6.6 | Security-focused tests: path validation, env isolation, model sanitization | NFR-001, R-001 |
| D6.7 | Migration shim: bash wrapper for backward compatibility | FR-037 |
| D6.8 | Validation: run against existing v2.02 tasklist-index.md | SC-001 |
| D6.9 | NFR verification: zero new dependencies, module size budget, platform support | NFR-001, NFR-002, NFR-008 |
| D6.10 | Tmux reattach verification: terminal state preserved after detach/attach cycle | FR-026, SC-002 |

**Dependencies**: M4, M5 (all components integrated)

**Risk Assessment**:
- Medium risk — integration test complexity with mocked subprocesses
- Validation against real tasklist-index.md may reveal edge cases

**Effort**: M (2-4 days) — test suite + migration shim + validation

**Acceptance Criteria**:
- All unit tests from Sec 12 pass (models, config, monitor, process, executor, tui, tmux, logging)
- Integration test: 6-phase sprint completes with SUCCESS outcome
- Integration test: HALT at phase 3 produces correct resume command
- TUI snapshot matches expected output format
- Migration shim forwards to `superclaude sprint run`
- No new dependencies in pyproject.toml

---

## Risk Register

| ID | Risk | Probability | Impact | Milestone | Mitigation |
|----|------|-------------|--------|-----------|-----------|
| R-001 | Claude CLI interface changes break command construction | Medium | High | M2 | Abstract command builder; integration test catches regressions |
| R-002 | Rich Live + tmux resize interaction | Low | Medium | M4 | Rich handles SIGWINCH; manual testing on resize |
| R-003 | GIL-safe assumption fails on non-CPython | Low | High | M3 | Document CPython requirement; optional Lock |
| R-004 | Disk space exhaustion from output files | Medium | Medium | M3 | Log file sizes; warn at >100MB per phase |
| R-005 | Signal handling race conditions | Medium | High | M2, M3 | threading.Event; sequential phase execution |
| R-006 | OS-specific process group behavior | Low | Medium | M2 | Test on Linux + macOS; document limitations |
| R-007 | Claude CLI not installed or incompatible version | Medium | High | M2, M6 | Check `claude --version` at startup; clear error message with install instructions |
| R-008 | Tmux unavailable in target environment | Low | Low | M5 | Graceful fallback to foreground mode (--no-tmux) already designed |

## Decision Summary

| Decision | Rationale | Source |
|----------|----------|--------|
| Template: inline generation | No pre-existing template matches this feature type | Wave 2 |
| 6 milestones (MEDIUM complexity) | 51 requirements, 0.624 complexity score | Scoring formula |
| Architect-first ordering (models → config → executor) | Clean dependency chain, no circular deps | Adversarial: opus:architect |
| Security hardening in M2 (not deferred) | Process isolation and signal handling are foundational | Adversarial: sonnet:security |
| M4 and M5 parallelizable | No data dependency between TUI/logging and tmux/CLI | Dependency analysis |
| No new dependencies | Spec explicitly requires zero new deps (NFR-001) | Spec Section 13.4 |

## Success Criteria

| ID | Criterion | Validation Method |
|----|----------|-------------------|
| SC-001 | `superclaude sprint run` executes all phases with pass/halt semantics | Integration test |
| SC-002 | Tmux sessions survive SSH disconnect + reattach | Manual test |
| SC-003 | TUI dashboard shows real-time phase progress | Snapshot test + manual |
| SC-004 | HALT on STRICT-tier task failure | Integration test |
| SC-005 | Resume command generated on halt | Unit test |
| SC-006 | No new dependencies | pyproject.toml diff check |
| SC-007 | All test cases pass | `uv run pytest tests/sprint/ -v` |
