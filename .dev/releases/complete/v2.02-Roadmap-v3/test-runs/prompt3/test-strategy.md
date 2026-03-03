---
spec_source: .dev/releases/current/v2.05-sprint-cli-specification/sprint-cli-specification.md
generated_by: sc:roadmap v2.0.0
generated_at: "2026-03-03"
complexity_class: MEDIUM
interleave_ratio: "1:2"
milestone_count: 6
test_milestones: [M1, M2, M3, M6]
validation_milestones: [M6]
---

# Test Strategy: `superclaude sprint` CLI

## Philosophy: Continuous Parallel Validation

Testing is not a phase — it is woven into every milestone. The 1:2 interleave ratio means every two work milestones are followed by validation activity. For this roadmap:

- **M1** (Models): Unit tests written alongside dataclasses
- **M2** (Config + Process): Unit tests for discovery, validation, command building
- **M3** (Executor + Monitor): Integration tests for execution flow + unit tests for monitor
- **M4** (TUI + Logging): Snapshot tests + format verification tests
- **M5** (Tmux + CLI): Command construction tests + mock subprocess tests
- **M6** (Integration): Full lifecycle tests, security tests, migration validation

## Interleave Schedule

The 1:2 interleave ratio means one dedicated validation checkpoint per two work milestones. Unit tests are written alongside each milestone (co-located), but formal validation gates occur at the midpoint and end.

| Milestone | Work Activity | Test Activity | Type |
|-----------|--------------|---------------|------|
| M1 | Data models | Co-located unit tests | work + co-test |
| M2 | Config + Process | Co-located unit tests | work + co-test |
| — | — | **Validation Gate 1: M1-M2 tests green, config integration verified** | 1:2 gate |
| M3 | Executor + Monitor | Co-located unit + integration tests | work + co-test |
| M4 | TUI + Logging | Co-located snapshot + format tests | work + co-test |
| — | — | **Validation Gate 2: M3-M4 tests green, executor-TUI integration verified** | 1:2 gate |
| M5 | Tmux + CLI | Co-located mock subprocess tests | work + co-test |
| M6 | — | Full integration + security + NFR verification + migration | validation |

## Test Categories

### Unit Tests (per milestone)

**M1 — models.py**:
- PhaseStatus.is_terminal returns True for all terminal states
- PhaseStatus.is_success returns True only for PASS variants
- PhaseStatus.is_failure returns True for HALT, TIMEOUT, ERROR
- SprintResult.phases_passed/phases_failed count correctly
- SprintResult.resume_command generates correct format
- SprintConfig.active_phases filters by start/end range
- MonitorState.stall_status returns correct string based on stall_seconds

**M2 — config.py**:
- discover_phases: finds phases from index file references
- discover_phases: falls back to directory scan
- discover_phases: handles all naming conventions (phase-N, pN, Phase_N, tasklist-PN)
- validate_phases: detects missing files (ERROR)
- validate_phases: detects sequence gaps (WARN)
- load_sprint_config: raises ClickException on missing index
- load_sprint_config: raises ClickException on no phases found

**M2 — process.py**:
- build_command: includes claude, --print, --no-session-persistence, --max-turns
- build_command: includes --model when specified
- build_prompt: generates /sc:task-unified prompt with correct phase number
- build_env: sets CLAUDECODE=""
- timeout_seconds: computes max_turns * 120 + 300

**M3 — monitor.py**:
- Extracts last task ID matching T##.## pattern
- Extracts last tool name from known tool list
- Tracks unique files changed
- Computes stall_seconds from time since last growth
- Reads only new bytes (incremental read)
- Handles missing output file without error

**M3 — executor.py**:
- _determine_phase_status: timeout exit code → TIMEOUT
- _determine_phase_status: non-zero exit → ERROR
- _determine_phase_status: EXIT_RECOMMENDATION: HALT → HALT
- _determine_phase_status: EXIT_RECOMMENDATION: CONTINUE → PASS
- _determine_phase_status: no result file but output → PASS_NO_REPORT
- _determine_phase_status: no result file and no output → ERROR

**M4 — tui.py**:
- Phase table renders all status styles correctly
- Progress bar reflects phases_passed / total
- Active panel shows monitor state fields
- Stall display uses correct Rich markup (bold red blink for STALLED)

**M4 — logging_.py**:
- JSONL entries are valid JSON
- Markdown log has correct table format
- write_phase_result appends row to markdown
- write_summary includes outcome and duration

**M5 — tmux.py**:
- session_name: produces `sc-sprint-{8-char-hash}`
- is_tmux_available: returns False when TMUX env set
- _build_foreground_command: includes --no-tmux and all config flags

**M5 — notify.py**:
- notify_phase_complete: sends notification on failure (urgent=True)
- notify_phase_complete: sends notification on success
- _notify: handles missing notify-send/osascript gracefully

### Integration Tests (M3, M6)

**M3 — executor integration**:
- Full phase execution with mocked ClaudeProcess (start/wait)
- Phase failure halts execution (SprintOutcome.HALTED)
- Signal handler sets INTERRUPTED outcome
- Multiple phases execute in sequence

**M6 — full lifecycle**:
- 3-phase sprint: all PASS → SUCCESS outcome
- 3-phase sprint: HALT at phase 2 → HALTED outcome, resume command generated
- Signal during phase 2 → INTERRUPTED outcome, partial log written
- Dry-run mode: phases listed, nothing executed

### Security Tests (M6)

From sonnet:security adversarial variant:
- Phase file path validation: no path traversal beyond release_dir
- Environment isolation: CLAUDECODE="" always set
- Command construction: no shell injection in model parameter
- Tmux session name: deterministic hash, no user-controlled content in session name

### Snapshot Tests (M4)

- TUI dashboard render: all-pending state
- TUI dashboard render: mixed state (2 pass, 1 running, 3 pending)
- TUI dashboard render: sprint complete (all pass)
- TUI dashboard render: sprint halted
- Compare rendered output to expected strings via `Console(file=StringIO)`

## Stop-and-Fix Thresholds

| Severity | Threshold | Action |
|----------|-----------|--------|
| Critical (P0 FR test failure) | Any single failure | Stop. Fix before continuing to next milestone |
| High (Integration test failure) | Any failure | Stop current milestone. Debug and fix |
| Medium (Snapshot drift) | >2 snapshots differ | Review and update snapshots or fix rendering |
| Low (Non-functional test) | >3 failures | Log and continue, fix in M6 |

## Test Infrastructure

**Framework**: pytest (existing)
**Fixtures**: tmp_path for file-based tests, monkeypatch for env/subprocess mocking
**Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.snapshot`
**Location**: `tests/sprint/`
**Execution**: `uv run pytest tests/sprint/ -v`

## Coverage Targets

| Component | Target | Rationale |
|-----------|--------|-----------|
| models.py | 95% | Pure logic, easy to test exhaustively |
| config.py | 90% | File I/O with known edge cases |
| process.py | 85% | Subprocess mocking covers main paths |
| monitor.py | 90% | File polling with controlled test files |
| executor.py | 80% | Complex orchestration, integration tests primary |
| tui.py | 75% | Snapshot tests cover rendering; Rich internals untested |
| tmux.py | 80% | Command construction; actual tmux not tested |
| logging_.py | 90% | File output verification |
| notify.py | 85% | Platform detection + subprocess mocking |
| commands.py | 75% | Click integration; end-to-end via CLI runner |

**Overall target**: ≥85% line coverage across `src/superclaude/cli/sprint/`
