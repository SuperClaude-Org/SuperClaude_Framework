---
spec_sources:
  - .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
  - .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/roadmap.md
generated: 2026-03-03T00:00:00Z
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 5
work_milestones: 10
interleave_ratio: "1:1"
major_issue_policy: stop-and-fix
complexity_class: HIGH
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is **1:1** (one validation milestone per one work milestone), derived from complexity class **HIGH** (score: 0.845)

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M1 (Foundation — Data Models and CLI Skeleton) | Model property correctness, CLI group registration, import chain integrity | Any model property returns wrong boolean; CLI group not accessible |
| V2 | M3 (Process Management and Signal Handling) | Subprocess spawning, signal handler lifecycle, timeout enforcement, process group kill correctness | Process group kill fails; signal handler leaves zombie processes |
| V3 | M6 (Executor Core Loop and Orchestration) | Phase iteration flow, HALT/CONTINUE decision logic, shutdown handling, TUI integration, result file parsing | Executor continues past HALT signal; shutdown leaves running processes |
| V4 | M7+M8 (Tmux + Logging combined) | Tmux session lifecycle, pane layout, attach/detach, JSONL/Markdown log correctness, notification dispatch | Tmux session naming collisions; log entries missing events |
| V5 | M9+M10 (Cleanup Audit v2 + Acceptance) | AC1-AC20 traceability, credential scanning safety, budget degradation, E2E sprint execution, migration shim | Any AC fails; credential values appear in output; migration shim breaks |

**Placement rule**: Validation milestones are placed after every 1 work milestone per the 1:1 interleave ratio. For practical grouping, V4 combines M7+M8 (both depend on M6 and can execute in parallel) and V5 combines M9+M10 (final validation pass).

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Process group kill leaves orphans (R-003); credential exposure (R-014); executor ignores HALT signal |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Monitor regex extraction fails on real output (R-001); phase discovery misses valid patterns (R-005); budget controls don't degrade gracefully (R-008) |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | TUI flicker on narrow terminal (R-004); notification silent failure on headless; doc gap in migration guide |
| Info | Log only, no action required | N/A | Optimization opportunity; alternative timeout formula; future Python GIL concern (R-007) |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | D1.1-D1.5: All model properties correct; CLI accessible; unit tests pass | >90% coverage of models.py; `superclaude sprint --help` works |
| M2 | D2.1-D2.5: All 4 naming conventions discovered; validation catches missing files and gaps | Phase discovery tests pass; config loads from valid index |
| M3 | D3.1-D3.5: Correct CLI command construction; process group isolation; graceful shutdown within 15s | Signal handler installs/uninstalls cleanly; CLAUDECODE env set |
| M4 | D4.1-D4.4: Incremental file read works; signal extraction correct; stall detection thresholds met | Monitor tests pass with mock output files; no re-reading |
| M5 | D5.1-D5.6: All 8 PhaseStatus styles render correctly; stall indicators at correct thresholds | TUI snapshot tests pass; active panel updates with MonitorState |
| M6 | D6.1-D6.6: Full executor loop; all 7 status paths tested; shutdown produces INTERRUPTED | Integration test with mocked subprocess passes; no hanging processes |
| M7 | D7.1-D7.5: Tmux available detection; deterministic session naming; pane layout correct | Tmux command construction tests pass; attach/kill work |
| M8 | D8.1-D8.5: Both log formats written; level routing correct; notifications dispatch | Log format tests pass; status/logs subcommands read from log |
| M9 | D9.1-D9.6: v1 promises enforced; credential safety; budget degradation; dependency graph valid | AC1-AC20 subset automated; no secret exposure in output |
| M10 | D10.1-D10.6: E2E sprint test passes; migration shim works; AC1-AC20 full suite passes | >80% module coverage; release readiness documented |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V1 | M1 | CLI import verification; `superclaude sprint --help` |
| FR-002 | V1 | M1 | Argument parsing with all flag combinations |
| FR-007 | V3 | M5, M6 | TUI snapshot test with mock SprintResult |
| FR-008 | V3 | M5 | Style map verification for all 8 PhaseStatus values |
| FR-009 | V3 | M5 | Stall threshold test: 30s → thinking, 60s → STALLED |
| FR-012 | V4 | M7 | SHA1 hash determinism test on known paths |
| FR-014 | V4 | M7 | is_tmux_available() with/without TMUX env var |
| FR-016 | V2 | M4 | Signal extraction from fixture output files |
| FR-019 | V2 | M3 | Process group creation verified via mock |
| FR-021 | V2 | M3 | Graceful shutdown timing test |
| FR-022 | V2 | M3 | Signal handler flag propagation |
| FR-023 | V3 | M6 | Full executor loop with mocked subprocess |
| FR-024 | V3 | M6 | All 7 status determination paths |
| FR-025 | V2 | M3 | Prompt content verification |
| FR-027 | V4 | M8 | JSONL + Markdown output format verification |
| FR-029 | V1 | M2 | All 4 naming conventions in fixture directory |
| FR-032 | V4 | M8 | Platform detection with mocked subprocess |
| FR-037 | V5 | M9 | AC1-AC6 automated checks |
| FR-038 | V5 | M9 | Credential scanning test with mock secrets |
| FR-043 | V5 | M9 | Budget accounting with forced degradation |
| FR-046 | V5 | M10 | Full AC1-AC20 validation suite |
| NFR-002 | V2 | M4 | Thread safety: concurrent read/write to MonitorState |
| NFR-003 | V2 | M3 | Shutdown timing: <15s from SIGTERM to cleanup |
| NFR-004 | V1 | M1 | Dependency check: no new entries in pyproject.toml |
| NFR-005 | V4 | M7 | Tmux detach/reattach preserves TUI state |
| NFR-008 | V4 | M8 | Notification failure silencing (mock tool absence) |
| NFR-012 | V5 | M9 | Output scrubbing for credential values |

## Test Infrastructure Requirements

### Sprint CLI Tests (`tests/sprint/`)

| File | Milestone | Type | Key Fixtures |
|------|-----------|------|-------------|
| `test_models.py` | M1 | Unit | None (pure dataclasses) |
| `test_config.py` | M2 | Unit | `tmp_path` with fixture phase files |
| `test_process.py` | M3 | Unit | Mock `subprocess.Popen` |
| `test_monitor.py` | M4 | Unit | Temp output files with signal patterns |
| `test_tui.py` | M5 | Snapshot | `Console(file=StringIO)` for render capture |
| `test_executor.py` | M6 | Integration | Mock `ClaudeProcess`, mock monitor |
| `test_tmux.py` | M7 | Unit | Mock `subprocess.run` for tmux commands |
| `test_logging.py` | M8 | Unit | `tmp_path` for log file output |
| `test_notify.py` | M8 | Unit | Mock `subprocess.run`, mock platform |

### Cleanup Audit v2 Tests

Leverage existing test infrastructure from cleanup-audit-v2 roadmap. Add AC1-AC20 automated validation as a new test module.

### Fixture Files

```
tests/sprint/fixtures/
  sample-index.md          # Minimal tasklist-index referencing 2 phase files
  phase-1-tasklist.md      # Phase file with heading for name extraction
  phase-2-tasklist.md      # Second phase file
  sample-result.md         # Phase result with YAML frontmatter + EXIT_RECOMMENDATION
  sample-output.txt        # Claude output with task IDs, tool names, file paths
```
