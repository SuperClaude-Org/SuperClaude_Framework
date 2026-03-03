---
spec_sources:
  - .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
  - .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/roadmap.md
generated: 2026-03-03T00:00:00Z
generator: sc:roadmap
complexity_score: 0.845
complexity_class: HIGH
domain_distribution:
  backend: 42
  infrastructure: 22
  performance: 14
  documentation: 10
  frontend: 8
  security: 4
primary_persona: backend
consulting_personas: [architect, devops]
milestone_count: 10
milestone_index:
  - id: M1
    title: Foundation — Data Models and CLI Skeleton
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 5
    risk_level: Low
  - id: M2
    title: Phase Discovery and Configuration Engine
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: Medium
  - id: M3
    title: Process Management and Signal Handling
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: High
  - id: M4
    title: Sidecar Monitor and Output Extraction
    type: FEATURE
    priority: P1
    dependencies: [M3]
    deliverable_count: 4
    risk_level: Medium
  - id: M5
    title: Rich TUI Dashboard
    type: FEATURE
    priority: P1
    dependencies: [M1, M4]
    deliverable_count: 6
    risk_level: Medium
  - id: M6
    title: Executor Core Loop and Orchestration
    type: FEATURE
    priority: P0
    dependencies: [M2, M3, M4, M5]
    deliverable_count: 6
    risk_level: High
  - id: M7
    title: Tmux Integration and Session Management
    type: FEATURE
    priority: P1
    dependencies: [M6]
    deliverable_count: 5
    risk_level: Medium
  - id: M8
    title: Logging, Notifications, and Observability
    type: FEATURE
    priority: P1
    dependencies: [M6]
    deliverable_count: 5
    risk_level: Low
  - id: M9
    title: Cleanup Audit v2 Core Enhancements
    type: FEATURE
    priority: P1
    dependencies: [M1]
    deliverable_count: 6
    risk_level: High
  - id: M10
    title: Integration Testing, Migration, and Acceptance
    type: TEST
    priority: P1
    dependencies: [M6, M7, M8, M9]
    deliverable_count: 6
    risk_level: High
total_deliverables: 53
total_risks: 16
estimated_phases: 6
validation_score: 0.903
validation_status: PASS
adversarial:
  mode: multi-spec
  convergence_score: 0.85
  base_variant: null
  artifacts_dir: null
---

# Roadmap: Sprint CLI + Cleanup Audit v2

## Overview

This roadmap consolidates two complementary specifications into a unified delivery plan for SuperClaude Framework v4.3.0:

1. **Sprint CLI** (`superclaude sprint`): A new multi-phase orchestration CLI that executes Claude Code sessions sequentially with Rich TUI dashboard, tmux integration, sidecar monitoring, and structured logging. This replaces the existing `execute-sprint.sh` bash script with a production-grade Python implementation (~2,160 lines across 11 files).

2. **Cleanup Audit v2 Core Enhancements**: Improvements to the existing `sc:cleanup-audit` command covering v1-promise enforcement, scanner hardening, profiling infrastructure, and budget controls.

Given HIGH complexity (0.845) across 4 major domains (backend 42%, infrastructure 22%, performance 14%, documentation 10%), the roadmap uses 10 milestones with a bottom-up construction strategy. Sprint CLI milestones (M1-M8) are organized by component dependency — data models first, then process management and monitoring, then the executor that orchestrates everything, then tmux and logging which depend on the executor. Cleanup Audit v2 (M9) runs in parallel with Sprint CLI milestones since it has no dependency on them. Final acceptance (M10) validates everything.

No new external dependencies are introduced — the implementation uses only `click` (existing), `rich` (existing), and Python stdlib.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|:---:|------|
| M1 | Foundation — Data Models and CLI Skeleton | FEATURE | P0 | S | None | 5 | Low |
| M2 | Phase Discovery and Configuration Engine | FEATURE | P0 | S | M1 | 5 | Medium |
| M3 | Process Management and Signal Handling | FEATURE | P0 | M | M1 | 5 | High |
| M4 | Sidecar Monitor and Output Extraction | FEATURE | P1 | S | M3 | 4 | Medium |
| M5 | Rich TUI Dashboard | FEATURE | P1 | M | M1, M4 | 6 | Medium |
| M6 | Executor Core Loop and Orchestration | FEATURE | P0 | M | M2, M3, M4, M5 | 6 | High |
| M7 | Tmux Integration and Session Management | FEATURE | P1 | S | M6 | 5 | Medium |
| M8 | Logging, Notifications, and Observability | FEATURE | P1 | S | M6 | 5 | Low |
| M9 | Cleanup Audit v2 Core Enhancements | FEATURE | P1 | L | M1 | 6 | High |
| M10 | Integration Testing, Migration, and Acceptance | TEST | P1 | M | M6, M7, M8, M9 | 6 | High |

## Dependency Graph

```
M1 → M2 → M6 → M7 → M10
M1 → M3 → M4 → M5 → M6
                M4 → M6
M1 → M9 → M10
M6 → M8 → M10
```

**Critical Path**: M1 → M3 → M4 → M5 → M6 → M10

**Parallel Opportunities**:
- M2 and M3 can execute in parallel (both depend only on M1)
- M7 and M8 can execute in parallel (both depend only on M6)
- M9 can execute in parallel with M2-M8 (independent feature track)

---

## M1: Foundation — Data Models and CLI Skeleton

### Objective
Implement all pure data models (`models.py`) and the CLI command group skeleton (`commands.py`, `__init__.py`), establishing the type system and interface contract for all subsequent milestones.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `models.py` with all enums and dataclasses: PhaseStatus, SprintOutcome, Phase, SprintConfig, PhaseResult, SprintResult, MonitorState | All properties compute correctly; PhaseStatus.is_terminal, is_success, is_failure return expected booleans |
| D1.2 | `__init__.py` with Click group definition and subcommand registration | `superclaude sprint --help` displays all subcommands |
| D1.3 | `commands.py` with all 5 Click commands (`run`, `attach`, `status`, `logs`, `kill`) as stubs with correct signatures and option definitions | CLI argument parsing works; `--help` for each subcommand shows correct options |
| D1.4 | Integration point in `main.py`: `main.add_command(sprint_group, name="sprint")` | `superclaude sprint` group is accessible from main CLI |
| D1.5 | Unit tests for `models.py`: property correctness, edge cases, serialization | All model tests pass with >90% coverage of models.py |

### Dependencies
- None

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data model changes needed during later milestones | Medium | Low | Design for extensibility; use dataclass defaults for new fields |

---

## M2: Phase Discovery and Configuration Engine

### Objective
Implement `config.py` with phase discovery, validation, and SprintConfig construction from tasklist-index files.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `discover_phases()` with regex matching all 4 naming conventions: `phase-N-tasklist.md`, `pN-tasklist.md`, `Phase_N_tasklist.md`, `tasklist-PN.md` | Test fixtures cover all 4 patterns; phases sorted by number |
| D2.2 | Two-strategy discovery: parse index file references first, fall back to directory scan | Both strategies produce correct results; fallback activates only when index parsing yields no phases |
| D2.3 | `validate_phases()` detecting missing files and sequence gaps | Missing files produce ERROR messages; gaps produce WARN messages |
| D2.4 | `_extract_phase_name()` from first heading in phase file | Phase names extracted and truncated to 50 chars |
| D2.5 | `load_sprint_config()` assembling and validating complete configuration | Config loads successfully from valid index; raises ClickException on invalid input |

### Dependencies
- M1: Uses Phase, SprintConfig dataclasses

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Phase file naming convention too rigid | Medium | Medium | Support 4 naming patterns; document convention clearly |
| Large directories slow discovery | Low | Low | Index-first strategy avoids directory scan in common case |

---

## M3: Process Management and Signal Handling

### Objective
Implement `process.py` with subprocess management, process group handling, timeout enforcement, and signal-based graceful shutdown.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | `ClaudeProcess.build_command()` constructing correct `claude` CLI invocation with all flags | Command includes `--print`, `--no-session-persistence`, `--max-turns`, `--output-format text`, `-p` with prompt |
| D3.2 | `ClaudeProcess.build_prompt()` generating `/sc:task-unified` prompt with phase-specific execution rules | Prompt includes compliance strict, tier-based rules, completion protocol with EXIT_RECOMMENDATION |
| D3.3 | `ClaudeProcess.start()` launching subprocess with process group isolation (`os.setpgrp`) and file handle redirection | Child process starts in own process group; stdout/stderr redirected to output/error files |
| D3.4 | `ClaudeProcess.terminate()` implementing 3-phase shutdown: SIGTERM → 10s wait → SIGKILL to process group | Graceful shutdown within 15s; no orphaned processes |
| D3.5 | `SignalHandler` for SIGINT/SIGTERM setting shutdown flag with original handler restoration | Handler installs/uninstalls cleanly; flag checked by executor loop |

### Dependencies
- M1: Uses Phase, SprintConfig dataclasses

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Process group kill may leave orphaned grandchild processes | Low | High | Use os.killpg with SIGKILL fallback; document limitation |
| Timeout calculation too aggressive or too loose | Medium | Medium | Make timeout formula configurable; default max_turns*120+300 |

---

## M4: Sidecar Monitor and Output Extraction

### Objective
Implement `monitor.py` with daemon thread that polls output files at 500ms intervals, extracting task IDs, tool names, file changes, and stall detection.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | `OutputMonitor` with daemon thread polling at configurable interval (default 500ms) | Thread starts/stops cleanly; polls at specified interval |
| D4.2 | Incremental file read via `seek()` — only reads new bytes since last poll | No re-reading of previously consumed data; handles file-not-found gracefully |
| D4.3 | Signal extraction: task IDs (T\d{2}\.\d{2}), tool names, file paths from Claude output | Last task ID, last tool, file count correctly extracted from sample output |
| D4.4 | Stall detection and growth rate tracking (exponential moving average, alpha=0.3) | Stall status transitions: active → thinking (>30s) → STALLED (>60s); growth rate updates smoothly |

### Dependencies
- M3: MonitorState dataclass (actually in M1); output file paths from process management

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Claude output format changes break regex patterns | Medium | High | Use permissive patterns; log extraction failures without crashing |
| GIL-reliance for thread safety may break on future Python | Low | Medium | Atomic scalar writes are sufficient for display purposes; document assumption |

---

## M5: Rich TUI Dashboard

### Objective
Implement `tui.py` with Rich Live-based dashboard showing phase table, overall progress bar, active phase detail panel with stall indicators.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | `SprintTUI` class with start/stop/update lifecycle matching executor polling | Live display starts, updates at 2 FPS, stops cleanly |
| D5.2 | Phase table with color-coded status: green (PASS), red (HALT/ERROR), yellow (RUNNING), dim (pending) | All 8 PhaseStatus values render with correct style |
| D5.3 | Overall progress bar showing phases completed vs total | Progress bar updates as phases complete |
| D5.4 | Active phase detail panel: file name, status, last task, last tool, output size, growth rate, files changed | Panel displays all fields from MonitorState; updates in real-time |
| D5.5 | Stall warning display: "thinking..." (>30s, yellow), "STALLED" (>60s, bold red blink) | Visual stall indicators appear at correct thresholds |
| D5.6 | Sprint complete/halted final states with summary, log path, and resume command | Terminal states render correctly with appropriate formatting |

### Dependencies
- M1: All model dataclasses for rendering
- M4: MonitorState for active phase panel data

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Rich Live display flickers on narrow terminals | Low | Medium | Use Panel wrapping with fixed widths; test on 80-col terminal |
| Terminal resize during execution | Low | Low | Rich handles SIGWINCH automatically; tmux forwards on reattach |

---

## M6: Executor Core Loop and Orchestration

### Objective
Implement `executor.py` — the central orchestration loop that iterates phases, launches subprocesses, coordinates monitor and TUI, parses results, and makes CONTINUE/HALT decisions.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | `execute_sprint()` main loop: iterate active_phases, launch process, monitor, parse, decide | Full loop executes for multi-phase sprint; correct CONTINUE/HALT behavior |
| D6.2 | Phase status determination with priority: timeout(124) → non-zero exit → HALT signal → CONTINUE signal → no-report fallback | All 7 status paths tested with mock result files |
| D6.3 | Shutdown handling: signal_handler.shutdown_requested terminates current process and exits with INTERRUPTED outcome | Ctrl-C during execution produces clean shutdown with partial log |
| D6.4 | TUI update polling: 500ms loop with process.poll() check | TUI refreshes during execution; stops when process exits |
| D6.5 | Result file parsing: YAML frontmatter + EXIT_RECOMMENDATION string detection | Correctly parses PASS, FAIL, HALT from real result file format |
| D6.6 | End-of-sprint validation: verify all phases actually passed before setting SUCCESS outcome | Edge case: non-zero exit with PASS signal does not yield SUCCESS |

### Dependencies
- M2: SprintConfig with active_phases and file paths
- M3: ClaudeProcess for subprocess management, SignalHandler
- M4: OutputMonitor for real-time data extraction
- M5: SprintTUI for display

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Race conditions between monitor thread and executor | Low | Medium | Atomic scalar writes; stale reads acceptable for display |
| Executor loop timing affects TUI responsiveness | Medium | Medium | Fixed 500ms poll; monitor thread handles data extraction independently |

---

## M7: Tmux Integration and Session Management

### Objective
Implement `tmux.py` with session creation, pane layout, attach/detach, and sprint lifecycle management in tmux.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D7.1 | `is_tmux_available()` detecting tmux binary and avoiding nesting (TMUX env var check) | Returns false when tmux absent or already inside tmux session |
| D7.2 | `session_name()` generating deterministic `sc-sprint-{SHA1[:8]}` from release directory | Same directory always produces same session name; different dirs produce different names |
| D7.3 | `launch_in_tmux()` creating detached session with sprint command as main pane, split bottom pane for tail | Tmux session created with correct layout; sprint runs in top pane |
| D7.4 | `update_tail_pane()` switching bottom pane to tail new phase output file | Pane switches to correct file when executor starts new phase |
| D7.5 | `attach_to_sprint()` / `kill_sprint()` for session management subcommands | attach reconnects to running session; kill terminates with grace period |

### Dependencies
- M6: Executor provides the foreground sprint command and phase transitions

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Tmux version incompatibilities across distributions | Low | Medium | Use minimal tmux API; test against tmux 2.x and 3.x |
| Terminal size mismatch on reattach | Low | Low | Rich handles SIGWINCH; tmux forwards resize signal |

---

## M8: Logging, Notifications, and Observability

### Objective
Implement `logging_.py` with dual JSONL/Markdown logging, `notify.py` with cross-platform desktop notifications, and the `sprint status`/`sprint logs` subcommands.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D8.1 | `SprintLogger` with JSONL and Markdown dual output: sprint_start, phase_complete, sprint_complete events | Both log formats contain all events; JSONL is machine-parseable; Markdown is human-readable |
| D8.2 | Log-level-based routing: DEBUG (JSONL only), INFO (all), WARN (highlighted), ERROR (highlighted + bell) | Screen output correctly filtered by level; terminal bell on errors |
| D8.3 | `notify_phase_complete()` and `notify_sprint_complete()` with platform detection | Linux: notify-send called; macOS: osascript called; failures silenced |
| D8.4 | `sprint status` subcommand reading JSONL log to display current state | Status works without tmux; shows phase completion, timing, outcome |
| D8.5 | `sprint logs` subcommand with `--lines N` and `--follow` functionality | Tails markdown log correctly; follow mode streams new entries |

### Dependencies
- M6: Executor calls logger and notify at each phase transition

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Notification tools unavailable on headless servers | Medium | Low | Best-effort with silent failure; always available via logs |

---

## M9: Cleanup Audit v2 Core Enhancements

### Objective
Implement priority enhancements to sc:cleanup-audit v2 as defined in the cleanup-audit-v2 unified spec: v1-promise enforcement, scanner hardening, profiling infrastructure, and budget controls.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D9.1 | Enforce v1-promised behaviors: two-tier classification with backward mapping, coverage tracking by risk tier, batch-level checkpointing, evidence-gated DELETE/KEEP rules | AC1, AC2, AC3, AC4, AC5, AC15 from unified spec |
| D9.2 | Correctness fixes: real credential scanning with safe redaction, gitignore inconsistency detection, Phase-1 scanner schema hardening | AC7, AC8, AC11; credential values never appear in output |
| D9.3 | Phase-0 profiling: domain/risk-tier profiling, monorepo-aware batch decomposition, auto-config for cold start, dry-run estimates | AC13, AC19, AC20 |
| D9.4 | Budget controls: budget accounting and enforcement, degradation sequence, degrade-priority override, budget realism reporting | AC9 |
| D9.5 | Cross-reference synthesis: 3-tier dependency graph with confidence labels, dead code candidates, duplication matrix | AC12 |
| D9.6 | Consolidation and validation: cross-phase dedup, stratified 10% spot-check, consistency-rate framing, coverage output artifacts | AC6, AC18 |

### Dependencies
- M1: Shared framework infrastructure (dataclasses pattern, CLI integration point)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Token budget underestimation for deep analysis | High | High | Dry-run estimates + degradation controls + benchmark calibration |
| Spec-implementation gap recurrence | High | High | AC traceability enforcement; automated validation suite |
| Context-window pressure in synthesis/consolidation | High | High | Summary-first artifact reads + budget caveats |

---

## M10: Integration Testing, Migration, and Acceptance

### Objective
Validate the full sprint CLI end-to-end, migrate from bash to Python, execute cleanup audit v2 acceptance criteria, and produce final release readiness evidence.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D10.1 | Integration test suite: full sprint execution with mocked subprocess, verifying phase flow, HALT/CONTINUE, and resume | All executor paths tested; >80% coverage across sprint module |
| D10.2 | End-to-end validation: sprint run against real tasklist-index (v2.02 as reference) | Sprint completes or halts appropriately; execution log is correct |
| D10.3 | Migration Phase 1: ship all sprint modules in v4.3.0 | All 11 files implemented, tested, integrated |
| D10.4 | Migration Phase 2: replace execute-sprint.sh with forwarding shim | Shim correctly forwards all arguments to `superclaude sprint run` |
| D10.5 | Cleanup audit v2 AC1-AC20 automated validation suite | All acceptance criteria verified with evidence |
| D10.6 | Release readiness decision record with benchmark evidence | Documented go/no-go decision with metrics |

### Dependencies
- M6: Sprint executor must be functional
- M7: Tmux integration for full E2E
- M8: Logging for test verification
- M9: Cleanup audit v2 features for AC validation

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hidden integration gaps despite unit test coverage | Medium | High | E2E test against real tasklist; benchmark repos |
| Migration breaks existing execute-sprint.sh users | Medium | Medium | Shim provides backward compatibility during transition |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Claude output format changes break monitor regex patterns | M4, M6 | Medium | High | Permissive patterns; log extraction failures without crashing | backend |
| R-002 | Tmux version incompatibilities across Linux/macOS | M7 | Low | Medium | Minimal tmux API; test tmux 2.x and 3.x | devops |
| R-003 | Process group kill leaves orphaned grandchild processes | M3, M6 | Low | High | os.killpg with SIGKILL fallback; document limitation | backend |
| R-004 | Rich Live display flickers on narrow terminals | M5 | Low | Medium | Panel wrapping with fixed widths; 80-col testing | backend |
| R-005 | Phase file naming convention too rigid | M2 | Medium | Medium | 4 naming patterns; clear documentation | backend |
| R-006 | Timeout calculation too aggressive or too loose | M3, M6 | Medium | Medium | Configurable formula; default max_turns*120+300 | backend |
| R-007 | GIL-reliance for thread safety in monitor-TUI communication | M4, M5 | Low | Medium | Atomic scalar writes; document assumption | architect |
| R-008 | Token budget underestimation for cleanup audit | M9 | High | High | Dry-run estimates + degradation controls + calibration | performance |
| R-009 | Spec-implementation gap recurrence in cleanup audit | M9, M10 | High | High | AC traceability enforcement; automated suite | architect |
| R-010 | Scanner schema malformation from Haiku outputs | M9 | Medium | Medium | Schema validation + retry + FAILED handling | backend |
| R-011 | Dynamic import false positives in cross-reference synthesis | M9 | Medium | High | Dynamic import checks + KEEP:monitor default | backend |
| R-012 | Large-repo scaling limits in cleanup audit | M9 | High | High | Monorepo segmentation + bounded degradation | architect |
| R-013 | Context-window pressure in synthesis/consolidation | M9 | High | High | Summary-first artifact reads + budget caveats | performance |
| R-014 | Credential value exposure in audit output | M9 | Low | High | Non-disclosure policy + output scrub checks | security |
| R-015 | Validation results interpreted as accuracy | M9, M10 | Medium | Medium | Consistency-rate language + calibration notes | qa |
| R-016 | Migration breaks existing execute-sprint.sh users | M10 | Medium | Medium | Backward-compatible shim during transition | devops |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend | architect (0.35), devops (0.31) | Backend domain dominant at 42% in extraction |
| Template | inline | local/user/plugin templates | No template files found in Tiers 1-3 |
| Milestone Count | 10 | 8-12 (HIGH complexity range) | Formula: base(8) + floor(4 domains / 2) = 10 |
| Adversarial Mode | multi-spec | none, multi-roadmap | `--specs` flag present with 2 spec files |
| Adversarial Base Variant | N/A | N/A | Multi-spec consolidation only (no competing roadmaps) |
| Sprint CLI Track | M1-M8 (8 milestones) | 6-10 milestones | Component-based decomposition matching 11-file architecture |
| Cleanup Audit Track | M9 (1 consolidated milestone) | 2-4 milestones | Existing roadmap already has detailed milestone breakdown; this roadmap references it |
| Parallel Strategy | M9 parallel with M2-M8 | Sequential after M8 | Zero functional overlap enables concurrent execution |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | `superclaude sprint run` discovers and executes all phases from a tasklist-index | M1, M2, M6 | Yes |
| SC-002 | TUI displays real-time phase progress with correct status colors and active panel | M5 | Yes |
| SC-003 | Sprint survives SSH disconnect and is resumable via `sprint attach` | M7 | Yes |
| SC-004 | Stall detection triggers visual warning after 60s no output growth | M4, M5 | Yes |
| SC-005 | HALT on STRICT-tier failure stops execution and shows resume command | M6 | Yes |
| SC-006 | Multiple concurrent sprints run isolated via unique tmux sessions | M7 | Yes |
| SC-007 | Phase discovery handles all 4 naming conventions | M2 | Yes |
| SC-008 | Dual JSONL + Markdown logs capture all phase events | M8 | Yes |
| SC-009 | Process cleanup terminates entire child tree on shutdown | M3, M6 | Yes |
| SC-010 | Dry-run mode shows phases without execution | M2, M6 | Yes |
| SC-011 | Desktop notifications fire on phase completion and sprint completion | M8 | Yes |
| SC-012 | No new external dependencies introduced | M1-M10 | Yes |
| SC-013 | All test files pass with >80% coverage across sprint module | M10 | Yes |
| SC-014 | Migration shim correctly forwards to Python implementation | M10 | Yes |
| SC-015 | Cleanup audit v1-promise enforcement complete (AC1-AC6) | M9 | Yes |
| SC-016 | Budget-limited audit runs complete gracefully with degradation | M9 | Yes |
| SC-017 | Credential scanning distinguishes real vs template secrets | M9 | Yes |
| SC-018 | Dependency graph emitted with valid nodes and confidence labels | M9 | Yes |
| SC-019 | AC1-AC20 automated validation suite passes | M10 | Yes |
| SC-020 | Release readiness decision documented with benchmark evidence | M10 | Yes |
