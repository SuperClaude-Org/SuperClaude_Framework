---
spec_source: .dev/releases/current/v2.03-CLI-Sprint-diag/spec-sprint-diagnostic-framework.md
generated: 2026-03-04T18:00:00Z
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
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 (M4) | M2 (Debug Instrumentation), M3 (Watchdog) | Debug log format correctness, all 8 event types present, watchdog terminates stalled process, backward compatibility with existing tests | Any PHASE_BEGIN without matching PHASE_END; watchdog fails to terminate within 2x stall_timeout; existing test failures |
| V2 (M7) | M5 (Diagnostics), M6 (Test Infrastructure) | FailureClassifier correctly identifies all 6 modes, diagnostic-report.json schema valid, L0 passes without claude, L1-3 skip gracefully, LN tests match expected failure modes | Classification mismatch on any of 6 modes; report schema validation failure; L0 test failure; orphaned child processes detected |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | debug.log not created when --debug set; watchdog kills wrong process; existing tests broken |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Missing event type in debug.log; FailureClassifier returns UNKNOWN for known mode; env leak between tests |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Inconsistent log timestamp format; unnecessary stderr output; test runs slower than threshold but completes |
| Info | Log only, no action required | N/A | Alternative ps-based approach for process state; optimization opportunity in log parsing |

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | `setup_debug_logger()` returns Logger; version header written; NullHandler when debug=False | Unit test: logger type, handler count, file existence, zero-overhead assertion |
| M2 | All 8 event types emitted; PHASE_BEGIN/END bracket events; poll_tick has all 7 fields | Run sprint with --debug; parse debug.log with DebugLogReader; filter assertions per component |
| M3 | Stall detected and acted upon within stall_timeout+5s; single-fire guard works; warn mode logs without killing | Manual test with sleep script; verify debug.log stall_timeout_exceeded event; verify _stall_acted reset |
| M4 | Debug log format correct; watchdog works; existing tests pass | D4.1-D4.3 deliverables verified |
| M5 | All 6 FailureMode classifications correct; confidence >= 0.85 for each; diagnostic-report.json valid | Unit tests per mode with synthetic DiagnosticBundles; JSON schema check |
| M6 | L0 passes <5s no claude; L1 passes <30s; LN all 6 modes classified; conftest fixtures work | `uv run pytest tests/sprint/diagnostic/ -v` with and without claude binary |
| M7 | US1-US5 validated; full suite green; backward compat confirmed; file inventory matches | Integration run + checklist verification |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V1 | M2 | Verify --debug flag accepted by Click command |
| FR-002 | V1 | M2 | Verify debug.log created in release_dir |
| FR-003 | V1 | M2 | Parse first line of debug.log for version header |
| FR-004 | V1 | M2 | Write + crash test; verify last entry flushed |
| FR-005 | V1 | M2 | Compare JSONL output with/without --debug; must be identical |
| FR-006 through FR-013 | V1 | M2 | DebugLogReader filter by component; assert event presence |
| FR-014, FR-015 | V1 | M3 | CLI option parsing test; SprintConfig field assertions |
| FR-016, FR-017 | V1 | M3 | Stall script + --stall-timeout 5 --stall-action kill; timing assertion |
| FR-018 through FR-021 | V1 | M2 | Logger name assertion; injection into 5 components; NullHandler test |
| FR-022 | V2 | M6 | test_level_0.py execution; <5s assertion |
| FR-023 through FR-025 | V2 | M6 | test_level_1-3.py execution with claude; skip without |
| FR-026 through FR-031 | V2 | M6 | test_negative.py; 6 failure modes classified correctly |
| FR-032 | V2 | M6 | Assert --debug and --no-tmux in all test configs |
| FR-033 through FR-036 | V2 | M5 | Unit tests with synthetic bundles; report schema validation |
| FR-037 through FR-040 | V2 | M6 | conftest.py fixture tests; directory structure assertion |
| FR-041 | V1 | M2 | Tmux command builder test; flag presence assertions |
| NFR-001 through NFR-004 | V2 | M6 | Timing assertions in each test level |
| NFR-005 | V2 | M6 | Run without claude; L0 passes, L1-3 skip cleanly |
| NFR-006 | V2 | M6 | Env save/restore in harness; orphan process check |
| NFR-007 | V1, V2 | M4, M7 | Existing test suite passes unchanged |
