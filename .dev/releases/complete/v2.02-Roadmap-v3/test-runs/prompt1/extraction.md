---
spec_source: .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
generated_by: sc:roadmap v2.0.0
generated_at: "2026-03-03"
extraction_mode: "chunked (4 chunks)"
project_title: "superclaude sprint — CLI Design Specification"
project_version: "1.0"
target_release: "SuperClaude v4.3.0"
complexity_score: 0.691
complexity_class: MEDIUM
domain_distribution:
  backend: 55
  frontend: 12
  performance: 25
  documentation: 8
primary_persona: backend
consulting_personas: [frontend, architect]
total_frs: 28
total_nfrs: 10
total_deps: 12
total_risks: 8
total_success_criteria: 7
adversarial_status: pending
validation_status: SKIPPED
validation_score: 0.0
---

# Extraction Report: superclaude sprint CLI

**Source**: `sprint-cli-specification.md` (2054 lines, 14 sections)
**Summary**: A multi-phase CLI sprint runner for SuperClaude that orchestrates sequential Claude Code sessions with a Rich TUI dashboard, tmux integration for detachable execution, sidecar output monitoring, process group management with graceful shutdown, and dual-format JSONL/markdown logging.

---

## Functional Requirements

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-001 | Module architecture: 11 files under `src/superclaude/cli/sprint/` with defined responsibilities | backend | P0 | L10-L47 |
| FR-002 | Data models: PhaseStatus enum with 9 states, is_terminal/is_success/is_failure properties | backend | P0 | L52-L101 |
| FR-003 | SprintOutcome enum with 4 states (SUCCESS, HALTED, INTERRUPTED, ERROR) | backend | P0 | L104-L109 |
| FR-004 | Phase dataclass with number, file, name fields and display_name property | backend | P0 | L112-L126 |
| FR-005 | SprintConfig dataclass with all execution parameters, path computation properties, active_phases filtering | backend | P0 | L128-L168 |
| FR-006 | PhaseResult dataclass with duration computation and display formatting | backend | P0 | L170-L193 |
| FR-007 | SprintResult with aggregate statistics (phases_passed, phases_failed) and resume_command generation | backend | P0 | L195-L234 |
| FR-008 | MonitorState dataclass with stall_status property and output_size_display formatting | backend, performance | P0 | L237-L265 |
| FR-009 | Click CLI group `sprint` with 5 subcommands: run, attach, status, logs, kill | backend | P0 | L269-L414 |
| FR-010 | `run` subcommand with --start, --end, --max-turns, --model, --dry-run, --no-tmux, --permission-flag options | backend | P0 | L310-L367 |
| FR-011 | `attach` subcommand to reconnect to running tmux sprint session | backend | P1 | L369-L378 |
| FR-012 | `status` subcommand to read execution log without attaching | backend | P1 | L380-L387 |
| FR-013 | `logs` subcommand with --lines and --follow options | backend | P1 | L389-L400 |
| FR-014 | `kill` subcommand with --force option for graceful/immediate shutdown | backend | P1 | L403-L414 |
| FR-015 | Rich TUI dashboard with persistent header, phase table, progress bar, active phase detail panel | frontend | P0 | L429-L738 |
| FR-016 | Phase table with status-specific styling (green/red/yellow/dim) and status icons | frontend | P0 | L562-L695 |
| FR-017 | Active phase detail panel showing file, status, last task, last tool, output size, files changed | frontend | P0 | L710-L738 |
| FR-018 | Stall warning display when output stops growing >60s, with "STALLED" text in bold red blink | frontend, performance | P0 | L496-L504 |
| FR-019 | Tmux session management with deterministic hash-based naming (`sc-sprint-{hash[:8]}`) | backend | P0 | L746-L852 |
| FR-020 | Tmux pane layout: 75% TUI dashboard top, 25% tail raw output bottom | backend | P0 | L750-L766 |
| FR-021 | Sidecar output monitor in daemon thread polling at 500ms intervals | performance | P0 | L929-L1059 |
| FR-022 | Monitor signal extraction: task IDs (T\d{2}\.\d{2}), tool names, file paths | performance | P0 | L943-L1056 |
| FR-023 | Growth rate computation via exponential moving average (alpha=0.3) | performance | P1 | L1020-L1027 |
| FR-024 | Process management with process groups (os.setpgrp) for clean tree kill | backend | P0 | L1099-L1250 |
| FR-025 | Graceful shutdown: SIGTERM → 10s wait → SIGKILL sequence | backend | P0 | L1217-L1243 |
| FR-026 | Executor core loop: launch phase → monitor → parse result → decide continue/halt | backend | P0 | L1289-L1460 |
| FR-027 | Phase discovery from index file and directory scan with flexible naming patterns | backend | P0 | L1598-L1651 |
| FR-028 | Desktop notifications via notify-send (Linux) and osascript (macOS), fail-silent | backend | P2 | L1753-L1816 |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | TUI refresh rate at 2 FPS for responsive display | performance | ≤500ms render cycle | L601 |
| NFR-002 | Monitor poll interval at 500ms for signal detection | performance | 500ms ±50ms jitter tolerance | L961 |
| NFR-003 | Process timeout computed as max_turns × 120s + 300s buffer | reliability | Configurable via --max-turns | L1129 |
| NFR-004 | No new dependencies — stdlib + existing click + rich only | maintainability | Zero new packages | L2038-L2042 |
| NFR-005 | Approximately 2,160 lines across 11 files | maintainability | Target line budget | L47 |
| NFR-006 | GIL-based thread safety for MonitorState scalar writes | reliability | No explicit locking required | L1092 |
| NFR-007 | Incremental file reading — monitor never holds file open | performance | stat() + seek() + read() pattern | L957-L958 |
| NFR-008 | Tmux screen state preservation on detach/reattach | reliability | Transparent Rich Live continuity | L916-L924 |
| NFR-009 | CLAUDECODE="" env var to prevent nested session detection | reliability | Required for child process isolation | L1183 |
| NFR-010 | Dual-format logging: JSONL (machine) + Markdown (human) | maintainability | Both formats always written | L1465-L1592 |

## Dependencies

| ID | Description | Type | Affected | Source |
|----|-------------|------|----------|--------|
| DEP-001 | `models.py` is imported by all other sprint modules | internal | FR-002 through FR-008 | L29 |
| DEP-002 | `config.py` must run before `executor.py` (phases must be discovered) | internal | FR-026, FR-027 | L344-L356 |
| DEP-003 | `monitor.py` depends on `models.py` MonitorState | internal | FR-021, FR-008 | L940-L941 |
| DEP-004 | `executor.py` depends on all other modules (orchestrator) | internal | FR-026 | L1296-L1310 |
| DEP-005 | `tui.py` depends on `models.py` for status enums and state objects | internal | FR-015, FR-002 | L562-L572 |
| DEP-006 | `process.py` depends on `models.py` Phase and SprintConfig | internal | FR-024, FR-005 | L1108-L1109 |
| DEP-007 | `tmux.py` requires tmux binary installed on system | external | FR-019, FR-020 | L778-L785 |
| DEP-008 | `notify.py` requires notify-send (Linux) or osascript (macOS) | external | FR-028 | L1767-L1783 |
| DEP-009 | `main.py` integration point — must add sprint_group import | internal | FR-009 | L276-L281 |
| DEP-010 | `claude` CLI binary must be available in PATH | external | FR-024, FR-026 | L1167 |
| DEP-011 | `tui.py` → `executor.py`: executor calls tui.update() in poll loop | internal | FR-015, FR-026 | L1356-L1366 |
| DEP-012 | Phase result files must follow EXIT_RECOMMENDATION protocol | internal | FR-026 | L1146-L1157 |

## Success Criteria

| ID | Description | Derived From | Measurable | Source |
|----|-------------|-------------|-----------|--------|
| SC-001 | All 11 module files implemented with defined responsibilities | FR-001 | Yes | L10-L47 |
| SC-002 | `sprint run` executes multi-phase sprint with correct phase sequencing | FR-010, FR-026 | Yes | L310-L367 |
| SC-003 | TUI displays real-time phase status, progress, and stall detection | FR-015, FR-018 | Yes | L429-L504 |
| SC-004 | Tmux sessions survive SSH disconnects with transparent reattach | FR-019, NFR-008 | Yes | L916-L924 |
| SC-005 | HALT on STRICT-tier task failure stops sprint execution | FR-026 | Yes | L1397-L1401 |
| SC-006 | Validates against existing v2.02 tasklist-index.md | All | Yes | L2011 |
| SC-007 | Zero new dependencies added to project | NFR-004 | Yes | L2038-L2042 |

## Risk Register

| ID | Description | Probability | Impact | Affected | Source |
|----|-------------|-------------|--------|----------|--------|
| RISK-001 | Tmux not available on target system (Docker, CI) | Medium | Medium | FR-019, FR-020 | L778-L785 |
| RISK-002 | Claude CLI output format changes break monitor regex patterns | Medium | High | FR-022 | L943-L949 |
| RISK-003 | Process group kill may not terminate all grandchild processes | Low | High | FR-024, FR-025 | L1196-L1243 |
| RISK-004 | GIL-based atomicity assumption may not hold on non-CPython | Low | Medium | NFR-006 | L1092 |
| RISK-005 | Long-running phases exceed timeout causing premature SIGKILL | Medium | High | NFR-003, FR-025 | L1207-L1212 |
| RISK-006 | Rich Live + tmux interaction on terminal resize edge cases | Low | Low | FR-015, NFR-008 | L916-L924 |
| RISK-007 | Phase file naming pattern regex may miss unconventional names | Low | Medium | FR-027 | L1612-L1616 |
| RISK-008 | Desktop notification commands may have security implications (osascript injection) | Low | Medium | FR-028 | L1776-L1778 |

---

## Domain Analysis

| Domain | Percentage | Key Areas |
|--------|-----------|-----------|
| Backend | 55% | CLI framework, process management, subprocess orchestration, config parsing, logging, tmux integration |
| Frontend/TUI | 12% | Rich dashboard, status styling, progress bars, panel layout |
| Performance | 25% | Sidecar monitor, poll-based signal extraction, growth rate EMA, stall detection, incremental reads |
| Documentation | 8% | JSONL/markdown dual logging, help text, dry-run output |

## Complexity Factor Breakdown

| Factor | Raw | Normalized | Weight | Weighted |
|--------|-----|-----------|--------|----------|
| requirement_count | 38 | 0.760 | 0.25 | 0.190 |
| dependency_depth | 5 | 0.625 | 0.25 | 0.156 |
| domain_spread | 3 | 0.600 | 0.20 | 0.120 |
| risk_severity | 2.00 | 0.500 | 0.15 | 0.075 |
| scope_size | 2054 | 1.000 | 0.15 | 0.150 |
| **Total** | | | | **0.691** |

**Classification**: MEDIUM → 5-7 milestones, 1:2 interleave ratio

---

*Generated by sc:roadmap v2.0.0 extraction pipeline (chunked mode, 4 chunks)*
