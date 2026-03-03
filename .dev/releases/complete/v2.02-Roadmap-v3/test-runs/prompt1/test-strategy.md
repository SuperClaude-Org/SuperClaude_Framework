---
spec_source: .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
generated: "2026-03-03"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 6
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (score: 0.691)

## Validation Milestones

| ID | After Work Milestones | Validates | Stop Criteria |
|----|----------------------|-----------|---------------|
| V1 | M2 (Config & Discovery), M3 (Process & Signals) | Module contracts between config→executor and process→executor; phase discovery correctness across all naming patterns; graceful shutdown sequence under all termination scenarios; signal handler isolation | Integration failure between config output and executor expectations; process group not created; SIGTERM/SIGKILL sequence broken; zombie processes detected |
| V2 | M5 (Orchestration & Integration), M6 (E2E Validation) | Complete system integration; executor drives all subsystems correctly; CLI contract matches spec; dual-format logging completeness; all 7 success criteria met | E2E test failure; CLI subcommand contract violation; JSONL log contains invalid entries; test coverage below 80%; any SC-001 through SC-007 criterion unmet |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. V1 validates the two foundational subsystems (config + process) before the integration milestone begins. V2 validates the complete integrated system after E2E testing.

**Note**: M1 (Foundation) and M4 (Monitor/TUI) are validated through their own per-milestone test deliverables (D1.3, D1.4, D4.4, D4.5) rather than a separate validation milestone, since they are parallel with M2/M3 and their defects surface in V1 integration testing.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Process group not created (child processes leak); executor loop deadlock; TUI crashes on update; SIGTERM sent to wrong process group |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Phase status determination returns wrong status; monitor misses all task IDs; config discovery fails for documented naming patterns; JSONL log produces invalid JSON |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Stall display threshold off by seconds; notification message formatting; TUI column alignment; progress bar rounding |
| Info | Log only, no action required | N/A | Performance optimization in monitor polling; alternative tmux pane layout; improved error messages |

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | All dataclass properties compute correctly; sprint CLI help works | Unit tests pass for all 7 data types; Click group importable; PhaseStatus.is_terminal/is_success/is_failure correct for all members |
| M2 | Phase discovery handles all 4 naming patterns; validation catches errors and gaps | D2.1-D2.4 acceptance criteria met; edge case matrix includes empty index, mixed naming, zero phases |
| M3 | Process groups isolate children; graceful shutdown works; timeouts enforce | D3.1-D3.5 acceptance criteria met; no zombie processes after any test; SIGKILL fires after 10s SIGTERM timeout |
| M4 | TUI renders all states; monitor extracts signals; stall detection triggers correctly | Snapshot tests pass; regex extraction verified for task IDs, tools, files; stall thresholds at 30s/60s |
| M5 | Executor drives all subsystems; tmux works; logging writes both formats | D5.1-D5.5 acceptance criteria met; integration between all modules verified; CLI options match spec §3.2 |
| M6 | E2E tests pass; edge cases covered; all success criteria met | SC-001 through SC-007 verified; regression suite passes; no process leaks in CI |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V2 | M1, M5 | File count verification; wc -l per module |
| FR-002 | M1 tests | M1 | Unit tests for all PhaseStatus properties |
| FR-003 | M1 tests | M1 | SprintOutcome enum value tests |
| FR-004 | M1 tests | M1 | Phase dataclass property tests |
| FR-005 | V1 | M1, M2 | SprintConfig.active_phases, results_dir, path computation |
| FR-006 | M1 tests | M1 | PhaseResult duration_display edge cases |
| FR-007 | V1 | M1 | SprintResult.resume_command generation |
| FR-008 | M4 tests | M4 | MonitorState.stall_status, output_size_display |
| FR-009 | V2 | M5 | CLI help output; all 5 subcommands accessible |
| FR-010 | V2 | M5 | Click option parsing for all --start/--end/--max-turns/etc. |
| FR-011 | V2 | M5 | Tmux attach subcommand with session discovery |
| FR-012 | V2 | M5 | Status reads JSONL log correctly |
| FR-013 | V2 | M5 | Logs --lines and --follow options |
| FR-014 | V2 | M5 | Kill --force vs graceful shutdown |
| FR-015 | M4 tests | M4 | TUI snapshot: full dashboard layout |
| FR-016 | M4 tests | M4 | TUI snapshot: status-specific styling per STATUS_STYLES |
| FR-017 | M4 tests | M4 | TUI snapshot: active phase detail panel content |
| FR-018 | M4 tests | M4 | Stall warning rendering at >60s threshold |
| FR-019 | V2 | M5 | Tmux session naming hash determinism |
| FR-020 | V2 | M5 | Tmux split -p 25 for 25% pane height |
| FR-021 | M4 tests | M4 | Monitor 500ms poll interval; incremental read |
| FR-022 | M4 tests | M4 | Regex extraction: TASK_ID_PATTERN, TOOL_PATTERN, FILES_CHANGED_PATTERN |
| FR-023 | M4 tests | M4 | Growth rate EMA computation |
| FR-024 | V1 | M3 | Process group creation via os.setpgrp |
| FR-025 | V1 | M3 | SIGTERM → 10s → SIGKILL shutdown sequence |
| FR-026 | V2 | M5, M6 | Executor core loop E2E: phase iteration with halt |
| FR-027 | V1 | M2 | Phase discovery from index + directory fallback |
| FR-028 | V2 | M5 | Notification platform detection; fail-silent |
| NFR-001 | M4 tests | M4 | Rich Live refresh_per_second=2 |
| NFR-002 | M4 tests | M4 | Monitor poll_interval=0.5 |
| NFR-003 | V1 | M3 | Timeout formula: max_turns*120+300 |
| NFR-004 | V2 | All | pip freeze diff: zero new packages |
| NFR-005 | V2 | All | wc -l across all 11 files |
| NFR-006 | M4 tests | M4 | MonitorState scalar field writes (GIL safety) |
| NFR-007 | M4 tests | M4 | Monitor seek-based incremental read |
| NFR-008 | V2 | M5 | Tmux detach/reattach with Rich Live continuity |
| NFR-009 | V1 | M3 | CLAUDECODE="" in child env |
| NFR-010 | V2 | M5 | JSONL + Markdown log verification |

---

*Generated by sc:roadmap v2.0.0 — continuous parallel validation strategy for MEDIUM complexity (1:2 interleave)*
