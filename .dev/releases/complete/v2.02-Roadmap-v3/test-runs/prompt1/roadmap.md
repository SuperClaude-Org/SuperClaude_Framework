---
spec_source: .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
generated: "2026-03-03"
generator: sc:roadmap
complexity_score: 0.691
complexity_class: MEDIUM
domain_distribution:
  backend: 55
  frontend: 12
  performance: 25
  documentation: 8
primary_persona: backend
consulting_personas: [architect, frontend]
milestone_count: 6
milestone_index:
  - id: M1
    title: "Foundation — Pure Data Model Layer"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    risk_level: Low
    effort: S
  - id: M2
    title: "Configuration & Phase Discovery Engine"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 4
    risk_level: Medium
    effort: S
  - id: M3
    title: "Process Management & Signal Safety"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: High
    effort: M
  - id: M4
    title: "Monitoring & TUI Display Layer"
    type: FEATURE
    priority: P1
    dependencies: [M1]
    deliverable_count: 5
    risk_level: Medium
    effort: M
  - id: M5
    title: "Orchestration, Integration & CLI Wiring"
    type: FEATURE
    priority: P0
    dependencies: [M2, M3, M4]
    deliverable_count: 5
    risk_level: Medium
    effort: L
  - id: M6
    title: "End-to-End Validation & Acceptance"
    type: TEST
    priority: P1
    dependencies: [M5]
    deliverable_count: 4
    risk_level: Medium
    effort: M
total_deliverables: 27
total_risks: 8
estimated_phases: 6
validation_score: 0.0
validation_status: SKIPPED
adversarial:
  mode: multi-roadmap
  agents: ["opus:architect", "sonnet:backend", "haiku:analyzer"]
  convergence_score: 0.82
  base_variant: "opus:architect"
  artifacts_dir: ".dev/releases/current/v2.05-sprint-cli-specification/test-runs/prompt1/"
---

# Roadmap: superclaude sprint CLI

## Overview

This roadmap implements the `superclaude sprint` CLI module — a multi-phase sprint runner that orchestrates sequential Claude Code sessions with a Rich TUI dashboard, tmux integration, sidecar output monitoring, process group management, and dual-format logging. The specification defines 11 files totaling ~2,160 lines under `src/superclaude/cli/sprint/`.

The roadmap follows a **foundation-up, test-integrated** architecture: a pure data model layer (M1) followed by three parallelizable subsystems (M2 config, M3 process, M4 monitor+TUI), converging at a single integration milestone (M5) and validated by an E2E acceptance suite (M6). This structure was produced by adversarial synthesis of three competing variants (opus:architect, sonnet:backend, haiku:analyzer) with convergence score 0.82.

Key architectural decisions: (1) three-way parallelism after M1 shortens the critical path to 4 hops; (2) process safety receives elevated priority from the backend variant; (3) per-milestone test deliverables from the analyzer variant ensure defects surface early.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation — Pure Data Model Layer | FEATURE | P0 | S | None | 4 | Low |
| M2 | Configuration & Phase Discovery Engine | FEATURE | P0 | M1 | M1 | 4 | Medium |
| M3 | Process Management & Signal Safety | FEATURE | P0 | M | M1 | 5 | High |
| M4 | Monitoring & TUI Display Layer | FEATURE | P1 | M | M1 | 5 | Medium |
| M5 | Orchestration, Integration & CLI Wiring | FEATURE | P0 | L | M2, M3, M4 | 5 | Medium |
| M6 | End-to-End Validation & Acceptance | TEST | P1 | M | M5 | 4 | Medium |

## Dependency Graph

```
M1 (Foundation)
 ├──→ M2 (Config/Discovery)    ──┐
 ├──→ M3 (Process/Signals)     ──┼──→ M5 (Orchestration) ──→ M6 (E2E Validation)
 └──→ M4 (Monitor/TUI)         ──┘
```

Critical path: M1 → M3 → M5 → M6 (4 hops)
Parallel lanes: M2 ‖ M3 ‖ M4 (all depend only on M1)

---

## M1: Foundation — Pure Data Model Layer

### Objective

Establish all shared data types, enums, and computed properties as a zero-dependency foundation. Every downstream module imports from `models.py` — freezing these contracts first eliminates a class of integration bugs.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `models.py` with all 7 types: PhaseStatus, SprintOutcome, Phase, SprintConfig, PhaseResult, SprintResult, MonitorState | All enums have correct members; all dataclass properties compute correctly; is_terminal, is_success, is_failure return correct values for every PhaseStatus member |
| D1.2 | `__init__.py` with sprint_group export and `main.py` integration point | `from superclaude.cli.sprint import sprint_group` works; `superclaude sprint --help` renders without error |
| D1.3 | Unit test suite for all model properties | 100% of computed properties covered; tests for SprintResult.resume_command, PhaseResult.duration_display, MonitorState.stall_status, SprintConfig.active_phases; edge cases (empty phases list, zero duration) |
| D1.4 | Serialization round-trip verification | All dataclasses produce valid dict representations; PhaseStatus/SprintOutcome enum values are JSON-serializable strings |

### Dependencies

- None (foundation layer)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Over-engineering types before usage patterns emerge | Low | Low | Keep models minimal per spec; add fields only when consumer modules require them |
| Enum member changes in later milestones | Low | Medium | Treat PhaseStatus as a public contract; new members may be added but existing ones must not be renamed |

---

## M2: Configuration & Phase Discovery Engine

### Objective

Implement deterministic phase file discovery from tasklist-index.md with strict validation. A malformed config or missing tasklist file must fail at startup, never silently during phase 4 of 6.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `config.py` with discover_phases() supporting all 4 naming patterns from spec | Regex matches: phase-N-tasklist.md, pN-tasklist.md, Phase_N_tasklist.md, tasklist-PN.md; numeric sort (phase-10 after phase-9); directory fallback when index has no refs |
| D2.2 | validate_phases() with gap detection and missing file errors | Missing files produce ERROR messages; non-sequential phases produce WARN; errors block execution; gaps do not block |
| D2.3 | load_sprint_config() with full option mapping and path resolution | Relative paths resolved to absolute; all Click options map 1:1 to SprintConfig fields; end_phase=0 auto-detects; phase names extracted from file headings |
| D2.4 | Edge case test matrix for discovery | Tests: empty index file (fallback to directory), mixed naming conventions, duplicate phase numbers (first wins), zero discovered phases (ClickException), Unicode filenames, very large phase numbers |

### Dependencies

- M1: Requires Phase, SprintConfig types

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Phase naming convention changes break discovery regex | Low | Medium | Pin regex as named constant PHASE_FILE_PATTERN; document all supported patterns |
| Symlinks in roadmap directory cause discovery duplication | Low | Low | Resolve to real paths during discovery; deduplicate by phase number |

---

## M3: Process Management & Signal Safety

### Objective

Implement bulletproof subprocess lifecycle management with process group isolation, graceful shutdown sequencing, and orphan prevention. This is the highest-risk module — an escaped child process consumes resources indefinitely and corrupts subsequent sprints.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | ClaudeProcess wrapper with process group isolation | Popen with preexec_fn=os.setpgrp; build_command() includes --print, --no-session-persistence, --max-turns, --output-format text, -p prompt; build_env() sets CLAUDECODE=""; pgid captured immediately after spawn |
| D3.2 | Graceful shutdown sequence: SIGTERM → 10s wait → SIGKILL | terminate() sends SIGTERM to process group via os.killpg; waits up to 10s; escalates to SIGKILL; handles ProcessLookupError; _close_handles() runs in all exit paths |
| D3.3 | SignalHandler for SIGINT/SIGTERM on sprint runner | Sets shutdown_requested flag; does NOT immediately kill child (delegates to executor loop); restores original handlers on uninstall(); second SIGINT within 2s does not cause double-shutdown |
| D3.4 | Timeout enforcement: max_turns × 120s + 300s buffer | wait() raises TimeoutExpired at computed deadline; terminate() called automatically on timeout; exit code 124 returned (bash convention) |
| D3.5 | Failure-mode test harness | Tests: SIGTERM to process group; SIGKILL escalation; timeout expiry; zombie prevention; process that ignores SIGTERM; concurrent start/terminate race; _close_handles idempotency |

### Dependencies

- M1: Requires Phase, SprintConfig types

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| os.setpgrp / os.killpg behavior differs macOS vs Linux | Medium | High | Test on both platforms; guard killpg with pgid > 0 check |
| Race between spawn and signal before pgid captured | Low | High | Capture pgid atomically in start(); never expose process before pgid is set |
| Process group kill misses grandchild processes | Low | High | Use os.killpg on the group; document limitation for deeply-nested subprocesses |

---

## M4: Monitoring & TUI Display Layer

### Objective

Implement the read-only observability layer: sidecar daemon thread for output monitoring and signal extraction, plus the Rich TUI dashboard for real-time sprint visualization.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | OutputMonitor daemon thread with 500ms polling | stat() + seek() + read() incremental pattern; never holds file open; extracts task IDs (T\d{2}\.\d{2}), tool names, file paths via regex; growth rate EMA with alpha=0.3 |
| D4.2 | Stall detection with configurable thresholds | stall_seconds computed from time since last growth; stall_status returns "active" (<30s), "thinking..." (30-60s), "STALLED" (>60s); tested with time manipulation |
| D4.3 | SprintTUI with Rich Live dashboard | Phase table with STATUS_STYLES color coding; active phase detail panel; overall progress bar; 2 FPS refresh (refresh_per_second=2); screen=False for tmux compatibility |
| D4.4 | Monitor robustness test suite | Tests: empty file, file not yet created (FileNotFoundError handled), large file incremental read, encoding errors (errors="replace"), rapid growth (no buffer overflow), reset() for new phase |
| D4.5 | TUI snapshot tests for all render states | Console(file=StringIO) capture; snapshots for: all-pending, one-running, pass+running+pending, halt state, sprint complete, stall warning display |

### Dependencies

- M1: Requires MonitorState, PhaseStatus, SprintResult, Phase types

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Claude CLI output format changes break monitor regex | Medium | High | Define patterns as named constants; test extraction against real Claude output samples |
| GIL atomicity assumption for MonitorState fails on non-CPython | Low | Medium | Document CPython requirement; scalar field writes are atomic under GIL |
| Rich TUI + tmux resize interaction | Low | Low | Rich handles SIGWINCH natively; tmux forwards on reattach; test with different terminal sizes |

---

## M5: Orchestration, Integration & CLI Wiring

### Objective

Wire all subsystems together through the executor core loop. This is the sole milestone where cross-module coupling is permitted — the composition root. Includes tmux session management, dual-format logging, desktop notifications, and full Click CLI surface.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | execute_sprint() core loop: phase iteration → subprocess → monitor → TUI → result determination | Phases run strictly sequentially; halt on is_failure status; signal_handler.shutdown_requested breaks loop; final outcome set from phase results; all phase results collected |
| D5.2 | _determine_phase_status() with 7-level priority chain | Timeout (exit 124) → ERROR (non-zero) → HALT (EXIT_RECOMMENDATION: HALT) → PASS (EXIT_RECOMMENDATION: CONTINUE) → PASS (status: PASS) → HALT (status: FAIL) → PASS_NO_SIGNAL (result file exists) → PASS_NO_REPORT (output exists) → ERROR (no output) |
| D5.3 | Tmux integration: session naming, pane layout, attach/kill | Deterministic hash-based naming sc-sprint-{hash[:8]}; 75/25 split layout; is_tmux_available checks binary AND TMUX env; update_tail_pane on phase change; attach/kill subcommands |
| D5.4 | SprintLogger dual-format output with event-driven writes | JSONL (one SprintEvent per line, valid JSON Lines) + Markdown table; flush after every write; terminal bell on ERROR; screen output for phase pass/fail |
| D5.5 | Desktop notifications and Click CLI commands | notify-send (Linux) / osascript (macOS); fail-silent; 5 subcommands: run, attach, status, logs, kill; all options from spec §3.2; dry-run mode prints phase table |

### Dependencies

- M2: SprintConfig, phase discovery
- M3: ClaudeProcess, SignalHandler
- M4: OutputMonitor, SprintTUI

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cross-module contract drift between M2-M4 implementations | Medium | High | Integration tests at module boundaries; strict type checking via mypy |
| Executor poll loop CPU usage (busy-wait with time.sleep) | Low | Medium | 0.5s sleep interval matches monitor poll rate; CPU overhead negligible for 2 Hz |
| Tmux send-keys blocks if buffer full | Low | Low | Non-blocking tmux writes with check=False; tmux failure does not abort sprint |

---

## M6: End-to-End Validation & Acceptance

### Objective

Prove the complete system works through E2E tests with mocked Claude processes, edge case scenarios, and CLI contract verification. Validates all 7 success criteria from the specification.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | E2E: Successful multi-phase sprint | Real subprocess (shell script as phase command); all phases PASS; JSONL log contains correct event sequence; exit code 0; execution-log.md has all rows |
| D6.2 | E2E: Halt on STRICT failure | Phase 2 of 3 exits non-zero; phase 3 never spawned; SPRINT_HALT in log; resume_command generated correctly |
| D6.3 | Integration: Signal during execution | SIGINT to executor during phase 2; child receives SIGTERM; process group reaped; no zombies; non-zero exit |
| D6.4 | Regression and edge case suite | Tests: empty phase file, phase gap (1→3), stall detection timeout, tmux unavailable fallback, notify-send missing, CLI help output, dry-run mode, --start/--end range filtering |

### Dependencies

- M5: All integrated components

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| E2E tests flaky due to timing sensitivity | Medium | Medium | Use deterministic test scripts with explicit timing; mark slow tests; retry logic in CI |
| Signal tests cause zombie processes in CI | Low | High | Aggressive teardown in test fixtures; ps-based verification; process group cleanup |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Tmux not available on target system (Docker, CI) | M5, M6 | Medium | Medium | Graceful fallback to foreground mode; is_tmux_available() check | backend |
| R-002 | Claude CLI output format changes break monitor regex | M4, M6 | Medium | High | Named pattern constants; test against real output samples; regex versioning | performance |
| R-003 | Process group kill misses grandchild processes | M3, M5 | Low | High | os.killpg on group; document limitation; atexit cleanup | backend |
| R-004 | GIL atomicity assumption fails on non-CPython | M4 | Low | Medium | Document CPython requirement; scalar writes only; no compound updates | architect |
| R-005 | Long phases exceed timeout causing premature SIGKILL | M3, M5 | Medium | High | Configurable --max-turns; timeout = max_turns × 120 + 300s buffer | backend |
| R-006 | Rich TUI + tmux resize edge cases | M4, M5 | Low | Low | Rich handles SIGWINCH; tmux forwards on reattach | frontend |
| R-007 | Phase file naming regex misses unconventional names | M2 | Low | Medium | Support 4 documented patterns; directory fallback scan | backend |
| R-008 | osascript injection in desktop notifications | M5 | Low | Medium | Sanitize notification message content; use parameterized commands | security |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend | architect (0.462), frontend (0.193) | Backend domain 55% highest; process management is dominant concern |
| Template | inline | No templates at ≥0.6 compatibility | No local/user templates found; inline generation from extraction data |
| Milestone Count | 6 | 5-7 (MEDIUM range) | base=5 + floor(3 domains / 2) = 6; matches all 3 adversarial variants |
| Adversarial Mode | multi-roadmap | N/A | --multi-roadmap flag present with 3 agents |
| Adversarial Base Variant | opus:architect | sonnet:backend (0.78), haiku:analyzer (0.75) | Cleanest module boundaries; widest parallelism (3-way after M1); shortest critical path (4 hops) |
| M2/M3 Ordering | Parallel (both depend on M1 only) | M3 before M2 (backend), M2 before M3 (analyzer) | Architecture perspective: no dependency between config and process; parallel maximizes schedule efficiency |
| Process Safety Emphasis | Elevated (5 deliverables in M3) | Standard (3 deliverables) | Merged from sonnet:backend variant; orphan prevention and graceful shutdown are critical |
| Per-Milestone Testing | Included in each milestone | Separate testing milestone | Merged from haiku:analyzer variant; early defect detection outweighs milestone overhead |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | All 11 module files implemented with defined responsibilities | M1-M5 | Yes — file count and wc -l verification |
| SC-002 | `sprint run` executes multi-phase sprint with correct sequencing | M5, M6 | Yes — E2E test D6.1 |
| SC-003 | TUI displays real-time phase status, progress, stall detection | M4, M5 | Yes — snapshot tests D4.5 |
| SC-004 | Tmux sessions survive SSH disconnects with transparent reattach | M5, M6 | Yes — tmux integration test |
| SC-005 | HALT on STRICT-tier task failure stops sprint execution | M5, M6 | Yes — E2E test D6.2 |
| SC-006 | Validates against existing v2.02 tasklist-index.md | M6 | Yes — regression test with real index |
| SC-007 | Zero new dependencies added to project | M1-M5 | Yes — pip freeze diff before/after |

---

*Generated by sc:roadmap v2.0.0 — adversarial synthesis from 3 variants (convergence: 0.82)*
