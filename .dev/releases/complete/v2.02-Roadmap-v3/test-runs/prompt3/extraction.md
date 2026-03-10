---
spec_source: .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
generated_by: sc:roadmap v2.0.0
generated_at: "2026-03-03"
extraction_mode: single-pass
project_title: "superclaude sprint — CLI Design Specification"
project_version: "1.0"
complexity_score: 0.624
complexity_class: MEDIUM
milestone_count_range: "5-7"
interleave_ratio: "1:2"
primary_persona: backend
consulting_personas: [architect, frontend]
persona_confidence: 0.554
domain_distribution:
  backend: 72
  frontend: 18
  performance: 6
  security: 2
  documentation: 2
total_requirements: 51
functional_requirements: 42
non_functional_requirements: 9
dependencies: 8
success_criteria: 7
risks: 6
---

# Extraction Report: `superclaude sprint` CLI Specification

## Overview

**Project**: `superclaude sprint` — a multi-phase sprint execution CLI for SuperClaude v4.3.0.

**Summary**: Replaces the existing bash `execute-sprint.sh` with a Python CLI that orchestrates sequential Claude Code sessions from tasklist-index files. Key features: tmux integration for detachable long-running sprints, Rich-based TUI dashboard with real-time monitoring, sidecar output monitoring with signal extraction, dual-format logging (JSONL + Markdown), graceful signal handling, and desktop notifications.

**Target Release**: SuperClaude v4.3.0

## Functional Requirements

| ID | Description | Domain | Priority | Source |
|----|------------|--------|----------|--------|
| FR-001 | CLI command group `sprint` with subcommands: run, attach, status, logs, kill | backend | P0 | L269-L414 |
| FR-002 | `run` command accepts index_path, --start, --end, --max-turns, --model, --dry-run, --no-tmux, --permission-flag | backend | P0 | L310-L367 |
| FR-003 | Phase discovery: parse tasklist-index.md for phase file references via regex | backend | P0 | L1596-L1650 |
| FR-004 | Phase discovery fallback: directory scan when index has no refs | backend | P1 | L1639-L1650 |
| FR-005 | Flexible phase file naming: phase-N, pN, Phase_N, tasklist-PN patterns | backend | P1 | L1609-L1616 |
| FR-006 | Phase validation: detect missing files and sequence gaps | backend | P0 | L1667-L1691 |
| FR-007 | Sequential phase execution: iterate active phases, launch subprocess per phase | backend | P0 | L1287-L1460 |
| FR-008 | Claude subprocess: build `claude --print -p` command with prompt, flags, model | backend | P0 | L1096-L1250 |
| FR-009 | Process group isolation via `os.setpgrp` for clean child tree management | backend | P0 | L1115-L1119 |
| FR-010 | Graceful shutdown: SIGTERM → 10s wait → SIGKILL sequence | backend | P0 | L1216-L1242 |
| FR-011 | Phase timeout: `max_turns * 120 + 300` seconds | backend | P1 | L1127-L1129 |
| FR-012 | Phase status determination: 7-priority exit code + result file parsing | backend | P0 | L1423-L1460 |
| FR-013 | EXIT_RECOMMENDATION protocol: CONTINUE/HALT signals in result files | backend | P0 | L1146-L1156 |
| FR-014 | Sidecar monitor: daemon thread polling output file at 500ms intervals | backend | P0 | L927-L1059 |
| FR-015 | Signal extraction: task IDs (T##.##), tool names, file paths from output | backend | P0 | L943-L1058 |
| FR-016 | Stall detection: report after 60s output idle | backend | P1 | L250-L256 |
| FR-017 | Growth rate tracking: exponential moving average bytes/second | backend | P1 | L1020-L1026 |
| FR-018 | Rich TUI dashboard: phase table, progress bar, active phase detail panel | frontend | P0 | L429-L738 |
| FR-019 | TUI status styling: green/red/yellow/dim by phase status | frontend | P1 | L562-L582 |
| FR-020 | TUI stall indicator: blink style for STALLED status | frontend | P1 | L496-L504 |
| FR-021 | Sprint complete state: final summary with log location | frontend | P1 | L506-L534 |
| FR-022 | Sprint halted state: halt info with resume command | frontend | P1 | L536-L547 |
| FR-023 | Tmux session management: create, attach, status, kill | backend | P0 | L742-L912 |
| FR-024 | Deterministic tmux session naming: `sc-sprint-{sha1[:8]}` | backend | P1 | L746 |
| FR-025 | Tmux pane layout: 75% TUI + 25% raw output tail | frontend | P1 | L749-L765 |
| FR-026 | Tmux reattach preserves terminal state, auto-redraw by Rich | backend | P1 | L914-L923 |
| FR-027 | Dual-format logging: JSONL (machine) + Markdown (human) | backend | P0 | L1464-L1592 |
| FR-028 | Log events: sprint_start, phase_complete, sprint_complete | backend | P0 | L1494-L1578 |
| FR-029 | Screen output with severity styling: INFO/WARN/ERROR + terminal bell | frontend | P1 | L1584-L1591 |
| FR-030 | Desktop notifications: Linux (notify-send), macOS (osascript), best-effort | backend | P2 | L1751-L1815 |
| FR-031 | `attach` subcommand: reconnect to running sprint tmux session | backend | P0 | L369-L377 |
| FR-032 | `status` subcommand: read execution log without attaching | backend | P0 | L379-L386 |
| FR-033 | `logs` subcommand: tail log with -n lines and -f follow | backend | P0 | L388-L400 |
| FR-034 | `kill` subcommand: stop sprint with optional --force (skip grace period) | backend | P0 | L402-L413 |
| FR-035 | Signal handling: SIGINT/SIGTERM → shutdown flag → executor terminates | backend | P0 | L1252-L1283 |
| FR-036 | Resume command generation from halt state | backend | P1 | L225-L234 |
| FR-037 | main.py integration: add sprint_group to existing superclaude CLI | backend | P0 | L271-L281 |
| FR-038 | `/sc:task-unified` prompt generation per phase with compliance tiers | backend | P0 | L1131-L1162 |
| FR-039 | Dry-run mode: display discovered phases without executing | backend | P1 | L320-L321 |
| FR-040 | SprintConfig dataclass with computed properties | backend | P0 | L128-L168 |
| FR-041 | SprintResult aggregation: passed/failed counts, duration, resume command | backend | P0 | L195-L234 |
| FR-042 | MonitorState real-time metrics: bytes, growth rate, stall, task/tool tracking | backend | P0 | L237-L264 |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|------------|----------|------------|--------|
| NFR-001 | Zero new dependencies — stdlib + existing click + rich only | maintainability | No new deps | L2038-L2041 |
| NFR-002 | Module size ~2,160 lines across 11 files | maintainability | <2,200 lines | L47 |
| NFR-003 | Monitor polling at 500ms (2 Hz) | performance | ≤500ms cycle | L960 |
| NFR-004 | TUI refresh at 2 FPS | performance | 2 Hz | L601 |
| NFR-005 | Process timeout: max_turns * 120 + 300 seconds | reliability | Bounded time | L1129 |
| NFR-006 | GIL-safe shared state: no locks for scalar writes | performance | Lock-free | L1092 |
| NFR-007 | Graceful notification degradation: fail silently | reliability | Best-effort | L1783 |
| NFR-008 | Platform support: Linux + macOS for notifications | maintainability | Cross-platform | L1766-L1783 |
| NFR-009 | Concurrent sprint support via unique tmux session names | scalability | Multi-sprint | L2052 |

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|------------|------|----------------------|
| DEP-001 | Sprint depends on existing `superclaude` CLI main.py | internal | FR-037 |
| DEP-002 | Requires Claude CLI installed and accessible | external | FR-008 |
| DEP-003 | Tmux integration requires tmux (graceful fallback to foreground) | external | FR-023 |
| DEP-004 | TUI depends on Rich library (existing dependency) | external | FR-018 |
| DEP-005 | Monitor lifecycle managed by executor | internal | FR-014, FR-007 |
| DEP-006 | Desktop notifications require platform-specific tools | external | FR-030 |
| DEP-007 | Phase discovery depends on tasklist-index.md format convention | internal | FR-003 |
| DEP-008 | Sprint prompt depends on `/sc:task-unified` command availability | external | FR-038 |

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|------------|-------------|-----------|
| SC-001 | `superclaude sprint run` executes all phases with pass/halt semantics | FR-007, FR-012 | Yes |
| SC-002 | Tmux sessions survive SSH disconnects and allow reattach | FR-023, FR-026 | Yes |
| SC-003 | TUI dashboard shows real-time phase progress | FR-018, FR-014 | Yes |
| SC-004 | HALT on STRICT-tier task failure stops sprint execution | FR-012, FR-013 | Yes |
| SC-005 | Resume command generated on halt | FR-036 | Yes |
| SC-006 | No new dependencies introduced | NFR-001 | Yes |
| SC-007 | All test cases pass | Testing strategy (Sec 12) | Yes |

## Risk Register

| ID | Description | Probability | Impact | Affected |
|----|------------|-------------|--------|----------|
| RISK-001 | Claude CLI interface changes break subprocess command construction | Medium | High | FR-008 |
| RISK-002 | Rich Live + tmux interaction issues on terminal resize | Low | Medium | FR-018, FR-026 |
| RISK-003 | GIL-safe assumption may not hold for all Python implementations | Low | High | NFR-006 |
| RISK-004 | Long-running sprints exhaust disk space with output files | Medium | Medium | FR-014 |
| RISK-005 | Signal handling race conditions between executor and process manager | Medium | High | FR-035, FR-010 |
| RISK-006 | Process group management (`os.setpgrp`) behavior varies across OS | Low | Medium | FR-009 |

## Domain Distribution

```
Backend       ████████████████████████████████████  72%
Frontend      █████████                             18%
Performance   ███                                    6%
Security      █                                      2%
Documentation █                                      2%
```

## Complexity Assessment

**Score**: 0.624 / 1.0 — **MEDIUM**

| Factor | Raw | Normalized | Weight | Weighted |
|--------|-----|-----------|--------|----------|
| requirement_count | 51 | 1.000 | 0.25 | 0.250 |
| dependency_depth | 3 | 0.375 | 0.25 | 0.094 |
| domain_spread | 2 | 0.400 | 0.20 | 0.080 |
| risk_severity | 1.67 | 0.333 | 0.15 | 0.050 |
| scope_size | 2054 | 1.000 | 0.15 | 0.150 |

**Implications**: 5-7 milestones recommended, 1:2 interleave ratio (one validation per two work milestones).
