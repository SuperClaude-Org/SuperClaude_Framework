---
spec_source: docs/design/sprint-cli-specification.md
generated: "2026-02-25T12:00:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 5
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
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (score: 0.69)

## Validation Milestones

| ID | After Work Milestones | Validates | Stop Criteria |
|----|----------------------|-----------|---------------|
| V1 (M4) | M2 (Backend Core), M3 (TUI Dashboard) | Integration between executor, process management, TUI, and monitor; state transitions through full phase lifecycle; signal handler graceful shutdown | Any integration failure between executor polling and TUI updates; process group cleanup fails; signal handler doesn't trigger shutdown |
| V2 (M7) | M5 (Integration), M6 (Testing & Hardening) | End-to-end sprint execution; all CLI subcommands; tmux+TUI interaction; logging completeness; full test suite passage | E2E test failure; CLI subcommand contract violation; log missing required fields; test suite coverage <80% |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. V1 validates the two core verticals (backend + frontend) before integration work begins. V2 validates the complete system after testing and hardening.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Process group not created (child processes leak); executor loop deadlocks; TUI crashes on update |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Phase status determination returns wrong status; monitor misses all task IDs; config discovery fails for documented naming patterns |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Stall display threshold off by a few seconds; notification message formatting; TUI column alignment issues |
| Info | Log only, no action required | N/A | Performance optimization opportunity in monitor polling; alternative approach for tmux pane management |

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | All dataclass properties compute correctly; `superclaude sprint --help` works | Unit tests pass for all 7 data types; Click group importable and registered |
| M2 | CLI options match spec; phase discovery handles all 4 naming patterns; process builds correct claude command; executor iterates phases and determines status correctly | All D2.1-D2.8 acceptance criteria met; no Critical/Major issues |
| M3 | TUI renders all states; monitor extracts signals from sample output; 2 FPS refresh stable | Snapshot tests pass; regex extraction verified; no rendering errors in tmux |
| M4 (V1) | Executor drives TUI through lifecycle; halt produces resume command; signal handler works | D4.1-D4.3 all pass; integration issues documented and resolved |
| M5 | Tmux session management works; logging writes both formats; notifications fire on correct events | All tmux commands verified; JSONL/Markdown validated; notification platform detection correct |
| M6 | Full test suite passes; edge cases covered (empty phases, gaps, stalls, timeouts) | ≥80% code coverage; all test files in spec Section 12.1 implemented |
| M7 (V2) | E2E tests pass; CLI contract verified; system handles real-world scenarios | D7.1-D7.3 all pass; all SC-001 through SC-008 success criteria met |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V2 (M7) | M1, M2 | CLI integration test: `superclaude sprint --help` |
| FR-002 | V2 (M7) | M2 | CLI option parsing test with all option combinations |
| FR-003 | V2 (M7) | M5 | Mocked tmux attach verification |
| FR-004 | V2 (M7) | M5 | Status command reads execution log correctly |
| FR-005 | V2 (M7) | M5 | Logs command tails with --lines and --follow |
| FR-006 | V2 (M7) | M5 | Kill command sends signals in correct order |
| FR-007 | V1 (M4) | M2 | Click.Choice validation for permission flags |
| FR-008 | V1 (M4) | M2 | Dry-run outputs phase list without executing |
| FR-009 | V1 (M4) | M1 | PhaseStatus enum property tests (is_terminal, is_success, is_failure) |
| FR-010 | V1 (M4) | M1 | SprintOutcome enum value tests |
| FR-011 | V1 (M4) | M1 | Phase dataclass property tests |
| FR-012 | V1 (M4) | M1 | SprintConfig property and method tests |
| FR-013 | V1 (M4) | M1 | PhaseResult duration and display tests |
| FR-014 | V1 (M4) | M1 | SprintResult aggregation and resume_command tests |
| FR-015 | V1 (M4) | M1, M3 | MonitorState stall_status and display tests |
| FR-016 | V1 (M4) | M3 | TUI snapshot: dashboard table with phase rows |
| FR-017 | V1 (M4) | M3 | TUI snapshot: status color rendering per STATUS_STYLES |
| FR-018 | V1 (M4) | M3 | TUI snapshot: active phase detail panel content |
| FR-019 | V1 (M4) | M3 | TUI snapshot: progress bar percentage and task count |
| FR-020 | V2 (M7) | M3 | TUI snapshot: complete and halted terminal states |
| FR-021 | V1 (M4) | M3 | Monitor stall detection at 30s and 60s thresholds |
| FR-022 | V2 (M7) | M5 | Session name determinism: same dir → same name |
| FR-023 | V2 (M7) | M5 | Tmux split command uses -p 25 for 25% height |
| FR-024 | V2 (M7) | M5 | is_tmux_available checks binary AND TMUX env var |
| FR-025 | V2 (M7) | M5 | update_tail_pane sends correct tmux send-keys |
| FR-026 | V1 (M4) | M2 | Integration test: executor loop iterates phases |
| FR-027 | V1 (M4) | M2 | Command includes all required claude flags |
| FR-028 | V1 (M4) | M2 | Popen preexec_fn=os.setpgrp verified |
| FR-029 | V1 (M4) | M2 | Terminate: SIGTERM → 10s → SIGKILL on process group |
| FR-030 | V1 (M4) | M2 | Status determination: 7-level priority chain verified |
| FR-031 | V1 (M4) | M2 | Phase discovery from index and directory fallback |
| FR-032 | V1 (M4) | M2 | All 4 naming conventions matched by regex |
| FR-033 | V1 (M4) | M2 | Validation detects missing files and gaps |
| FR-034 | V2 (M7) | M5 | JSONL events and Markdown table rows verified |
| FR-035 | V2 (M7) | M5 | Notification platform detection and silent failure |
| NFR-001 | V1 (M4) | M3 | Rich Live refresh_per_second=2 configured |
| NFR-002 | V1 (M4) | M3 | Monitor poll_interval=0.5 configured |
| NFR-003 | V1 (M4) | M2 | Timeout formula: max_turns*120+300 verified |
| NFR-004 | V1 (M4) | M3 | No threading locks between monitor and TUI (code review) |
| NFR-005 | V2 (M7) | All | Line count verification across all source files |
| NFR-006 | V2 (M7) | M5 | Tmux session survives simulated detach/reattach |
| NFR-007 | V2 (M7) | M5 | Notification subprocess timeout=5 verified |
| NFR-008 | V1 (M4) | M3 | Monitor seek-based incremental read verified |
