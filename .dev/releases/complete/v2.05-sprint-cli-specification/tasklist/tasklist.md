# TASKLIST — `superclaude sprint` CLI Implementation

---

## Metadata & Artifact Paths

**TASKLIST_ROOT**: `.dev/releases/current/v2.05-sprint-cli-specification/`
**Tasklist Path**: `TASKLIST_ROOT/tasklist.md`
**Execution Log Path**: `TASKLIST_ROOT/execution-log.md`
**Checkpoint Reports Path**: `TASKLIST_ROOT/checkpoints/`
**Evidence Root**: `TASKLIST_ROOT/evidence/`
**Artifacts Root**: `TASKLIST_ROOT/artifacts/`
**Feedback Log Path**: `TASKLIST_ROOT/feedback-log.md`
**Generator Version**: Roadmap→Tasklist Generator v2.2
**Generated**: 2026-02-25
**Complexity Score**: 0.69 (MEDIUM)
**Primary Persona**: backend
**Consulting Personas**: architect, frontend
**Total Milestones**: 7
**Total Deliverables**: 35
**Total Tasks**: 35
**Total Checkpoints**: 11

---

## Source Snapshot

- **Sprint scope**: Implement the `superclaude sprint` CLI command — a multi-phase sprint executor replacing `execute-sprint.sh`, targeting ~2,160 lines of Python across 11 files in `src/superclaude/cli/sprint/` for SuperClaude v4.3.0.
- **Architecture**: Click CLI structure, Rich TUI, GIL-safe lock-free threading for monitor-TUI communication, process group isolation for child process cleanup.
- **Layered strategy**: Pure data models first (M1), then two independent vertical slices — backend process orchestration (M2) and frontend TUI dashboard (M3) — in parallel, followed by cross-cutting integration (M5), comprehensive testing (M6), and validation checkpoints (M4, M7).
- **Critical path**: M1 → M2 → M5 → M6 → M7.
- **Parallel opportunity**: M2 and M3 can execute concurrently after M1.
- **Validation cadence**: 1:2 ratio (MEDIUM complexity) — M4 after M2+M3, M7 after M6.
- **Priority ordering**: P0 (M1, M2) → P1 (M3, M5) → P2 (M6) → P3 (M4, M7).
- **Compliance tiers**: Tasks classified STRICT (model/schema/multi-file/system-wide), STANDARD (implement/create/build), LIGHT (minor fixes), or EXEMPT (test/review/validate); tier drives verification method and MCP requirements.

---

## Deterministic Rules Applied

- **R-RULE-01 Phase sequencing**: Phases execute in order 1 → 2 → 3 → 4 → 5 → 6 → 7; no phase may begin until the preceding phase's checkpoint is complete.
- **R-RULE-02 Single active task**: Only one task may be `in_progress` at a time; state transitions logged with timestamp.
- **R-RULE-03 Deliverable-to-artifact binding**: Every deliverable D-0001–D-0035 must produce a verifiable artifact at its declared path; deliverables without artifacts cannot be marked complete.
- **R-RULE-04 Tier-driven verification**: STRICT tasks require sub-agent verification; STANDARD tasks require direct test execution; LIGHT/EXEMPT tasks may skip verification.
- **R-RULE-05 Traceability closure**: Every Roadmap Item R-001–R-042 must map to at least one Task ID and one Deliverable ID in the Traceability Matrix.
- **R-RULE-06 Checkpoint cadence**: Checkpoint after every 5 tasks within a phase, plus end-of-phase checkpoint before next phase begins.
- **R-RULE-07 Foundation dependency**: No M2–M7 task may begin until all M1 deliverables (D-0001–D-0004) are verified complete.
- **R-RULE-08 Test isolation**: Test tasks (M4, M6, M7) must not modify source modules; they produce only test files and evidence artifacts.
- **R-RULE-09 Quality gates**: `uv run pytest`, `make lint` must pass at end-of-phase checkpoints for phases containing source changes.
- **R-RULE-10 Model stability**: Changes to `models.py` after Phase 1 require re-running all Phase 1 unit tests before proceeding.

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text |
|---|---|---|
| R-001 | Phase 1 | M1: Foundation: Data Models & Project Scaffolding |
| R-002 | Phase 1 | D1.1: `models.py` with PhaseStatus, SprintOutcome enums and Phase, SprintConfig, PhaseResult, SprintResult, MonitorState dataclasses |
| R-003 | Phase 1 | D1.2: Sprint module `__init__.py` with Click group export |
| R-004 | Phase 1 | D1.3: Integration point in `main.py`: `main.add_command(sprint_group, name="sprint")` |
| R-005 | Phase 1 | D1.4: `tests/sprint/__init__.py` and `test_models.py` with unit tests for all enum properties and dataclass aggregations |
| R-006 | Phase 2 | M2: Backend Core: CLI, Config & Process Management |
| R-007 | Phase 2 | D2.1: `commands.py`: Click command group with `run`, `attach`, `status`, `logs`, `kill` subcommands |
| R-008 | Phase 2 | D2.2: `config.py`: `discover_phases()` function supporting 4 naming conventions |
| R-009 | Phase 2 | D2.3: `config.py`: `validate_phases()` detecting missing files and sequence gaps |
| R-010 | Phase 2 | D2.4: `config.py`: `load_sprint_config()` combining discovery, validation, and auto-detection |
| R-011 | Phase 2 | D2.5: `process.py`: `ClaudeProcess` class with build_prompt, build_command, build_env, start, wait, terminate |
| R-012 | Phase 2 | D2.6: `process.py`: `SignalHandler` with SIGINT/SIGTERM handling |
| R-013 | Phase 2 | D2.7: `executor.py`: Main `execute_sprint()` orchestration loop |
| R-014 | Phase 2 | D2.8: `executor.py`: `_determine_phase_status()` implementing 7-level status priority |
| R-015 | Phase 3 | M3: TUI Dashboard & Output Monitor |
| R-016 | Phase 3 | D3.1: `tui.py`: `SprintTUI` class with start, stop, update, _render methods |
| R-017 | Phase 3 | D3.2: `tui.py`: Phase table with color-coded status rendering |
| R-018 | Phase 3 | D3.3: `tui.py`: Active phase detail panel |
| R-019 | Phase 3 | D3.4: `tui.py`: Sprint complete and halted terminal states |
| R-020 | Phase 3 | D3.5: `monitor.py`: `OutputMonitor` class with start, stop, reset and background polling |
| R-021 | Phase 3 | D3.6: `monitor.py`: Signal extraction via regex patterns |
| R-022 | Phase 4 | M4: Validation Checkpoint 1 |
| R-023 | Phase 4 | D4.1: Integration test: executor with mocked ClaudeProcess drives TUI through full phase lifecycle |
| R-024 | Phase 4 | D4.2: Integration test: executor halts on STRICT-tier failure and produces resume command |
| R-025 | Phase 4 | D4.3: Integration test: signal handler triggers graceful shutdown during execution |
| R-026 | Phase 5 | M5: Integration: Tmux, Logging & Notifications |
| R-027 | Phase 5 | D5.1: `tmux.py`: is_tmux_available, session_name, find_running_session utility functions |
| R-028 | Phase 5 | D5.2: `tmux.py`: launch_in_tmux creating detached session with two-pane layout |
| R-029 | Phase 5 | D5.3: `tmux.py`: attach_to_sprint, kill_sprint, update_tail_pane session management |
| R-030 | Phase 5 | D5.4: `logging_.py`: SprintLogger class with write_header, write_phase_result, write_summary |
| R-031 | Phase 5 | D5.5: `logging_.py`: Log levels (DEBUG→JSONL only, INFO→all, WARN/ERROR→highlighted+bell) |
| R-032 | Phase 5 | D5.6: `notify.py`: Cross-platform desktop notifications |
| R-033 | Phase 6 | M6: Testing & Hardening |
| R-034 | Phase 6 | D6.1: `test_config.py`: Phase discovery, validation tests |
| R-035 | Phase 6 | D6.2: `test_monitor.py`: Signal extraction from mock output files |
| R-036 | Phase 6 | D6.3: `test_process.py`: Command construction, env building, timeout calculation |
| R-037 | Phase 6 | D6.4: `test_tui.py`: Snapshot tests for all TUI states |
| R-038 | Phase 6 | D6.5: `test_executor.py`: Full integration test with mocked subprocess |
| R-039 | Phase 7 | M7: Final Validation & Acceptance |
| R-040 | Phase 7 | D7.1: E2E test: superclaude sprint run with mock subprocess executing 3-phase sprint to completion |
| R-041 | Phase 7 | D7.2: E2E test: superclaude sprint run with mock failure at phase 2 producing HALTED outcome |
| R-042 | Phase 7 | D7.3: CLI contract validation: all 5 subcommands match documented help text |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-002 | models.py with enums and dataclasses | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0001/spec.md`, `TASKLIST_ROOT/artifacts/D-0001/evidence.md` | M | Medium |
| D-0002 | T01.02 | R-003 | Sprint module __init__.py | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0002/spec.md`, `TASKLIST_ROOT/artifacts/D-0002/evidence.md` | XS | Low |
| D-0003 | T01.03 | R-004 | Integration point in main.py | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0003/spec.md`, `TASKLIST_ROOT/artifacts/D-0003/evidence.md` | XS | Low |
| D-0004 | T01.04 | R-005 | Unit tests for models | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0004/spec.md`, `TASKLIST_ROOT/artifacts/D-0004/evidence.md` | S | Low |
| D-0005 | T02.01 | R-007 | commands.py Click command group | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0005/spec.md`, `TASKLIST_ROOT/artifacts/D-0005/evidence.md` | M | Medium |
| D-0006 | T02.02 | R-008 | config.py discover_phases | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0006/spec.md`, `TASKLIST_ROOT/artifacts/D-0006/evidence.md` | S | Low |
| D-0007 | T02.03 | R-009 | config.py validate_phases | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0007/spec.md`, `TASKLIST_ROOT/artifacts/D-0007/evidence.md` | S | Low |
| D-0008 | T02.04 | R-010 | config.py load_sprint_config | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0008/spec.md`, `TASKLIST_ROOT/artifacts/D-0008/evidence.md` | S | Medium |
| D-0009 | T02.05 | R-011 | process.py ClaudeProcess class | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0009/spec.md`, `TASKLIST_ROOT/artifacts/D-0009/evidence.md` | M | High |
| D-0010 | T02.06 | R-012 | process.py SignalHandler | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0010/spec.md`, `TASKLIST_ROOT/artifacts/D-0010/evidence.md` | S | Medium |
| D-0011 | T02.07 | R-013 | executor.py execute_sprint loop | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0011/spec.md`, `TASKLIST_ROOT/artifacts/D-0011/evidence.md` | L | High |
| D-0012 | T02.08 | R-014 | executor.py _determine_phase_status | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0012/spec.md`, `TASKLIST_ROOT/artifacts/D-0012/evidence.md` | S | Medium |
| D-0013 | T03.01 | R-016 | tui.py SprintTUI class | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0013/spec.md`, `TASKLIST_ROOT/artifacts/D-0013/evidence.md` | M | Medium |
| D-0014 | T03.02 | R-017 | TUI phase table with status rendering | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0014/spec.md`, `TASKLIST_ROOT/artifacts/D-0014/evidence.md` | S | Low |
| D-0015 | T03.03 | R-018 | TUI active phase detail panel | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0015/spec.md`, `TASKLIST_ROOT/artifacts/D-0015/evidence.md` | S | Medium |
| D-0016 | T03.04 | R-019 | TUI terminal states | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0016/spec.md`, `TASKLIST_ROOT/artifacts/D-0016/evidence.md` | S | Low |
| D-0017 | T03.05 | R-020 | monitor.py OutputMonitor class | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0017/spec.md`, `TASKLIST_ROOT/artifacts/D-0017/evidence.md` | M | Medium |
| D-0018 | T03.06 | R-021 | Monitor signal extraction | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0018/spec.md`, `TASKLIST_ROOT/artifacts/D-0018/evidence.md` | S | Medium |
| D-0019 | T04.01 | R-023 | Integration test: full phase lifecycle | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0019/spec.md`, `TASKLIST_ROOT/artifacts/D-0019/evidence.md` | S | Medium |
| D-0020 | T04.02 | R-024 | Integration test: halt and resume | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0020/spec.md`, `TASKLIST_ROOT/artifacts/D-0020/evidence.md` | S | Low |
| D-0021 | T04.03 | R-025 | Integration test: graceful shutdown | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0021/spec.md`, `TASKLIST_ROOT/artifacts/D-0021/evidence.md` | S | Medium |
| D-0022 | T05.01 | R-027 | tmux.py utility functions | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0022/spec.md`, `TASKLIST_ROOT/artifacts/D-0022/evidence.md` | S | Low |
| D-0023 | T05.02 | R-028 | tmux.py launch_in_tmux | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0023/spec.md`, `TASKLIST_ROOT/artifacts/D-0023/evidence.md` | S | Medium |
| D-0024 | T05.03 | R-029 | tmux.py session management | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0024/spec.md`, `TASKLIST_ROOT/artifacts/D-0024/evidence.md` | S | Medium |
| D-0025 | T05.04 | R-030 | logging_.py SprintLogger class | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0025/spec.md`, `TASKLIST_ROOT/artifacts/D-0025/evidence.md` | M | Medium |
| D-0026 | T05.05 | R-031 | logging_.py log levels | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0026/spec.md`, `TASKLIST_ROOT/artifacts/D-0026/evidence.md` | S | Low |
| D-0027 | T05.06 | R-032 | notify.py desktop notifications | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0027/spec.md`, `TASKLIST_ROOT/artifacts/D-0027/evidence.md` | S | Low |
| D-0028 | T06.01 | R-034 | test_config.py | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0028/spec.md`, `TASKLIST_ROOT/artifacts/D-0028/evidence.md` | S | Low |
| D-0029 | T06.02 | R-035 | test_monitor.py | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0029/spec.md`, `TASKLIST_ROOT/artifacts/D-0029/evidence.md` | S | Low |
| D-0030 | T06.03 | R-036 | test_process.py | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0030/spec.md`, `TASKLIST_ROOT/artifacts/D-0030/evidence.md` | S | Low |
| D-0031 | T06.04 | R-037 | test_tui.py | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0031/spec.md`, `TASKLIST_ROOT/artifacts/D-0031/evidence.md` | S | Low |
| D-0032 | T06.05 | R-038 | test_executor.py | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0032/spec.md`, `TASKLIST_ROOT/artifacts/D-0032/evidence.md` | M | Medium |
| D-0033 | T07.01 | R-040 | E2E test: 3-phase sprint completion | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0033/spec.md`, `TASKLIST_ROOT/artifacts/D-0033/evidence.md` | M | Medium |
| D-0034 | T07.02 | R-041 | E2E test: failure with resume | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0034/spec.md`, `TASKLIST_ROOT/artifacts/D-0034/evidence.md` | S | Medium |
| D-0035 | T07.03 | R-042 | CLI contract validation | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0035/spec.md`, `TASKLIST_ROOT/artifacts/D-0035/evidence.md` | S | Low |

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---:|---|---|
| 1 | Foundation: Data Models & Project Scaffolding | T01.01–T01.04 | Pure-data foundation and project structure | STRICT: 1, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 2 | Backend Core: CLI, Config & Process Management | T02.01–T02.08 | CLI interface, config, subprocess, executor | STRICT: 5, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 3 | TUI Dashboard & Output Monitor | T03.01–T03.06 | Rich TUI and sidecar output monitor | STRICT: 1, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 4 | Validation Checkpoint 1 | T04.01–T04.03 | M2+M3 integration verification | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 5 | Integration: Tmux, Logging & Notifications | T05.01–T05.06 | Cross-cutting concerns wired | STRICT: 1, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 6 | Testing & Hardening | T06.01–T06.05 | Full test suite with edge cases | STRICT: 1, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |
| 7 | Final Validation & Acceptance | T07.01–T07.03 | E2E validation and CLI contract | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |

---

## Phase 1: Foundation — Data Models & Project Scaffolding

**Milestone**: M1 | **Priority**: P0 | **Effort**: S | **Dependencies**: None
**Roadmap Items**: R-001 through R-005

---

### T01.01 — Implement models.py with enums and dataclasses

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-002 |
| **Why** | All other milestones depend on these dataclasses and enums; this is the pure-data foundation with zero external dependencies |
| **Effort** | M (multiple types: 2 enums + 5 dataclasses + property methods) |
| **Risk** | Medium (model changes may be needed in later milestones) |
| **Risk Drivers** | Data model extensibility; property method correctness; spec compliance for 7 types |
| **Tier** | STRICT — keywords: model, schema, dataclass, system-wide (all milestones depend on this) |
| **Confidence Bar** | [█████████-] 90% — spec Section 2 fully defines all types |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — foundation for entire sprint |
| **Verification Method** | Sub-agent (quality-engineer): verify all 7 types match spec Section 2 |
| **MCP Requirements** | Sequential (structured analysis of spec compliance) |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No — single file, focused scope |
| **Deliverable IDs** | D-0001 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0001/spec.md`, `TASKLIST_ROOT/artifacts/D-0001/evidence.md` |

**Deliverables**:
- `models.py` containing PhaseStatus enum, SprintOutcome enum, Phase dataclass, SprintConfig dataclass, PhaseResult dataclass, SprintResult dataclass, MonitorState dataclass
- Property methods: `is_terminal`, `is_success`, `is_failure`, `duration_display`, `resume_command`, `stall_status`

**Steps**:
1. `[PLANNING]` Read spec Section 2 and extract all type definitions, field names, and property signatures
2. `[PLANNING]` Map enum members and dataclass fields to Python types with default values
3. `[EXECUTION]` Create `src/superclaude/cli/sprint/models.py` with PhaseStatus and SprintOutcome enums
4. `[EXECUTION]` Add Phase, SprintConfig, PhaseResult, SprintResult, MonitorState dataclasses with all fields per spec
5. `[EXECUTION]` Implement property methods: `is_terminal`, `is_success`, `is_failure`, `duration_display`, `resume_command`, `stall_status`
6. `[VERIFICATION]` Run `uv run pytest tests/sprint/test_models.py -v` to validate all types

**Acceptance Criteria**:
1. All 7 types (PhaseStatus, SprintOutcome, Phase, SprintConfig, PhaseResult, SprintResult, MonitorState) defined and importable
2. Property methods (`is_terminal`, `is_success`, `is_failure`, `duration_display`, `resume_command`, `stall_status`) return correct values for all enum states
3. Dataclass fields match spec Section 2 names, types, and defaults exactly
4. `from superclaude.cli.sprint.models import PhaseStatus, SprintOutcome, Phase, SprintConfig, PhaseResult, SprintResult, MonitorState` succeeds

**Validation**:
1. `uv run python -c "from superclaude.cli.sprint.models import PhaseStatus, SprintOutcome, Phase, SprintConfig, PhaseResult, SprintResult, MonitorState; print('OK')"` → OK
2. `uv run pytest tests/sprint/test_models.py -v` → all tests pass

**Dependencies**: None
**Rollback**: Delete `src/superclaude/cli/sprint/models.py`
**Notes**: Foundation task — block all subsequent phases until verified complete. Use `@dataclass(frozen=False)` for mutability where spec requires it (e.g., MonitorState).

---

### T01.02 — Create sprint module __init__.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-003 |
| **Why** | Module must be importable as a Python package with Click group export for CLI integration |
| **Effort** | XS (single small file) |
| **Risk** | Low (straightforward package init) |
| **Risk Drivers** | Click group import path correctness |
| **Tier** | STANDARD — keyword: create |
| **Confidence Bar** | [█████████-] 90% — standard Python package pattern |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — required for CLI wiring |
| **Verification Method** | Direct test: import statement |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0002 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0002/spec.md`, `TASKLIST_ROOT/artifacts/D-0002/evidence.md` |

**Deliverables**:
- `__init__.py` exporting `sprint_group` Click group

**Steps**:
1. `[PLANNING]` Identify Click group pattern from existing `src/superclaude/cli/` modules
2. `[EXECUTION]` Create `src/superclaude/cli/sprint/__init__.py` with Click group definition and export
3. `[VERIFICATION]` Verify import: `from superclaude.cli.sprint import sprint_group`

**Acceptance Criteria**:
1. `src/superclaude/cli/sprint/__init__.py` exists
2. `from superclaude.cli.sprint import sprint_group` succeeds
3. `sprint_group` is a Click Group instance
4. Module follows existing CLI package patterns in the project

**Validation**:
1. `uv run python -c "from superclaude.cli.sprint import sprint_group; print(type(sprint_group))"` → `<class 'click.core.Group'>`
2. `uv run python -c "import superclaude.cli.sprint"` → no ImportError

**Dependencies**: T01.01 (models must exist for type references)
**Rollback**: Delete `src/superclaude/cli/sprint/__init__.py`
**Notes**: Keep minimal — only export what main.py needs.

---

### T01.03 — Wire sprint_group into main.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-004 |
| **Why** | Makes `superclaude sprint` accessible as a CLI subcommand; required for all user-facing functionality |
| **Effort** | XS (single line addition to existing file) |
| **Risk** | Low (existing pattern in main.py) |
| **Risk Drivers** | Import order; existing command group conflicts |
| **Tier** | STANDARD — keyword: add, modify |
| **Confidence Bar** | [█████████-] 90% — follows existing add_command pattern |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes |
| **Verification Method** | Direct test: CLI help output |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0003 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0003/spec.md`, `TASKLIST_ROOT/artifacts/D-0003/evidence.md` |

**Deliverables**:
- `main.add_command(sprint_group, name="sprint")` added to main.py

**Steps**:
1. `[PLANNING]` Read `src/superclaude/cli/main.py` to identify existing `add_command` pattern and import location
2. `[EXECUTION]` Add import: `from superclaude.cli.sprint import sprint_group`
3. `[EXECUTION]` Add registration: `main.add_command(sprint_group, name="sprint")`
4. `[VERIFICATION]` Run `superclaude sprint --help` and verify output

**Acceptance Criteria**:
1. `superclaude sprint --help` displays sprint group help text
2. No existing commands broken by the addition
3. Import follows existing ordering convention in main.py
4. `superclaude --help` lists `sprint` in available commands

**Validation**:
1. `uv run superclaude sprint --help` → shows help text with exit code 0
2. `uv run superclaude --help` → sprint listed in commands

**Dependencies**: T01.02
**Rollback**: Revert changes to `src/superclaude/cli/main.py` (remove import and add_command lines)
**Notes**: Single-line integration — verify no circular imports.

---

### T01.04 — Write unit tests for models

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-005 |
| **Why** | Validates the foundation data model before downstream consumers are built; ensures ≥90% coverage on models.py |
| **Effort** | S (comprehensive tests for 7 types + property methods) |
| **Risk** | Low (testing pure data structures is deterministic) |
| **Risk Drivers** | Coverage completeness; edge cases in property methods |
| **Tier** | STANDARD — keyword: create, test files (+0.2 STANDARD boost) |
| **Confidence Bar** | [█████████-] 90% — property methods have deterministic behavior |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest with coverage |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0004 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0004/spec.md`, `TASKLIST_ROOT/artifacts/D-0004/evidence.md` |

**Deliverables**:
- `tests/sprint/__init__.py` (empty init)
- `tests/sprint/test_models.py` with unit tests for all enum properties and dataclass aggregations

**Steps**:
1. `[PLANNING]` List all enum members and property methods requiring test cases
2. `[EXECUTION]` Create `tests/sprint/__init__.py`
3. `[EXECUTION]` Create `tests/sprint/test_models.py` with tests for PhaseStatus enum properties, SprintOutcome enum properties, dataclass instantiation, and all property methods
4. `[EXECUTION]` Add edge case tests: default values, boundary conditions for duration_display, stall thresholds
5. `[VERIFICATION]` Run `uv run pytest tests/sprint/test_models.py -v --cov=superclaude.cli.sprint.models`

**Acceptance Criteria**:
1. All tests pass with zero failures
2. ≥90% coverage on `models.py`
3. Every enum member tested for `is_terminal`, `is_success`, `is_failure` properties
4. Dataclass aggregation methods (e.g., SprintResult totals) verified

**Validation**:
1. `uv run pytest tests/sprint/test_models.py -v` → all tests pass
2. `uv run pytest tests/sprint/test_models.py --cov=superclaude.cli.sprint.models` → ≥90% coverage

**Dependencies**: T01.01
**Rollback**: Delete `tests/sprint/` directory
**Notes**: These tests serve as regression suite for R-RULE-10 (model stability).

---

### Checkpoint: End of Phase 1

**Purpose:** Verify foundation models and module structure
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-END.md`
**Verification:**
- All 4 tasks (T01.01–T01.04) marked completed
- models.py importable with all 7 types; `uv run pytest tests/sprint/test_models.py` passes
- `superclaude sprint --help` works
**Exit Criteria:**
- All deliverables D-0001 through D-0004 verified
- `superclaude sprint --help` works
- Phase 2 and Phase 3 unblocked

---

## Phase 2: Backend Core — CLI, Config & Process Management

**Milestone**: M2 | **Priority**: P0 | **Effort**: L | **Dependencies**: M1
**Roadmap Items**: R-006 through R-014

---

### T02.01 — Implement commands.py Click command group

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-007 |
| **Why** | Defines the CLI interface contract — all 5 subcommands (run, attach, status, logs, kill) with their options and defaults |
| **Effort** | M (5 subcommands with multiple options each) |
| **Risk** | Medium (option types and defaults must match spec exactly) |
| **Risk Drivers** | Spec Section 3.2 compliance; Click decorator correctness; option type mapping |
| **Tier** | STRICT — keywords: api contract, multi-file (CLI contract defines public interface); context booster: >2 files affected (+0.3) |
| **Confidence Bar** | [█████████-] 90% — spec Section 3.2 fully specifies all options |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — CLI is user entry point |
| **Verification Method** | Sub-agent: verify --help output matches spec for all 5 subcommands |
| **MCP Requirements** | Context7 (Click patterns), Sequential (option mapping analysis) |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0005 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0005/spec.md`, `TASKLIST_ROOT/artifacts/D-0005/evidence.md` |

**Deliverables**:
- `commands.py` with Click command group containing `run`, `attach`, `status`, `logs`, `kill` subcommands
- All options per spec Section 3.2 with correct types and defaults

**Steps**:
1. `[PLANNING]` Extract all 5 subcommand signatures from spec Section 3.2: option names, types, defaults, help text
2. `[PLANNING]` Map spec option types to Click parameter types (Path, Int, String, Choice, Flag)
3. `[EXECUTION]` Create `commands.py` with Click group and `run` subcommand (most complex — all execution options)
4. `[EXECUTION]` Add `attach`, `status`, `logs`, `kill` subcommands with their options
5. `[EXECUTION]` Wire subcommands to placeholder functions (actual implementation in executor/tmux tasks)
6. `[VERIFICATION]` Run `superclaude sprint run --help` and compare output to spec

**Acceptance Criteria**:
1. `superclaude sprint run --help` shows all options per spec Section 3.2
2. Option types and defaults match spec exactly
3. All 5 subcommands (`run`, `attach`, `status`, `logs`, `kill`) are registered
4. Click group structure follows existing project CLI conventions

**Validation**:
1. `uv run superclaude sprint run --help` → exit 0, all options listed
2. `uv run superclaude sprint kill --help` → exit 0, options match spec

**Dependencies**: T01.02 (sprint module must exist)
**Rollback**: Delete `src/superclaude/cli/sprint/commands.py`
**Notes**: Placeholder function bodies return `click.echo("Not implemented")` until executor/tmux tasks wire real logic.

---

### T02.02 — Implement discover_phases in config.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-008 |
| **Why** | Phase discovery is the first step in sprint execution — must find phase files using 4 naming conventions with index-first fallback |
| **Effort** | S (regex matching for 4 patterns + index parsing + directory fallback) |
| **Risk** | Medium (naming convention regex must handle all variants; R-007 risk: convention changes) |
| **Risk Drivers** | Regex correctness for 4 patterns; index file parsing; directory fallback strategy |
| **Tier** | STANDARD — keyword: implement, create |
| **Confidence Bar** | [█████████-] 90% — naming conventions fully specified |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — config feeds executor |
| **Verification Method** | Direct test: unit tests with fixture directories |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0006 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0006/spec.md`, `TASKLIST_ROOT/artifacts/D-0006/evidence.md` |

**Deliverables**:
- `discover_phases()` function supporting phase-N, pN, Phase_N, tasklist-PN naming patterns
- Index-first strategy with directory-fallback

**Steps**:
1. `[PLANNING]` Define regex patterns for all 4 naming conventions: `phase-N`, `pN`, `Phase_N`, `tasklist-PN`
2. `[EXECUTION]` Create `config.py` with `discover_phases()` function
3. `[EXECUTION]` Implement index-first strategy: parse index file for phase references
4. `[EXECUTION]` Implement directory-fallback: scan directory for matching filenames
5. `[VERIFICATION]` Unit test with fixture directories for each naming convention

**Acceptance Criteria**:
1. All 4 naming patterns correctly matched by regex
2. Index-first strategy parses phase references from index files
3. Directory-fallback scans and matches files when no index exists
4. Returns list of Phase objects with correct file paths and sequence numbers

**Validation**:
1. Unit test with `phase-1.md`, `p2.md`, `Phase_3.md`, `tasklist-P4.md` fixtures → all discovered
2. Unit test with index file referencing phases → phases discovered in order

**Dependencies**: T01.01 (Phase dataclass)
**Rollback**: Delete `src/superclaude/cli/sprint/config.py`
**Notes**: Regex patterns should be configurable constants at module level for R-007 risk mitigation.

---

### T02.03 — Implement validate_phases in config.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-009 |
| **Why** | Prevents sprint execution on invalid phase configurations — detects missing files and sequence gaps before subprocess launch |
| **Effort** | S (validation logic for file existence and sequence gaps) |
| **Risk** | Low (validation is read-only analysis) |
| **Risk Drivers** | Gap detection edge cases (e.g., single phase, non-contiguous gaps) |
| **Tier** | STANDARD — keyword: implement |
| **Confidence Bar** | [█████████-] 90% — validation rules are deterministic |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: unit tests with invalid fixtures |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0007 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0007/spec.md`, `TASKLIST_ROOT/artifacts/D-0007/evidence.md` |

**Deliverables**:
- `validate_phases()` function detecting missing files and sequence gaps

**Steps**:
1. `[PLANNING]` Define validation rules: file existence check, sequence gap detection (e.g., phases 1,2,4 → gap at 3)
2. `[EXECUTION]` Implement file existence validation with error messages
3. `[EXECUTION]` Implement sequence gap detection with warning messages
4. `[VERIFICATION]` Test with missing files and gaps (e.g., phase 2→4 gap)

**Acceptance Criteria**:
1. Missing files produce error-level messages with file paths
2. Sequence gaps produce warning-level messages identifying the gap
3. Gap between phases 2→4 correctly detected and reported
4. Returns validation result with errors and warnings separated

**Validation**:
1. Unit test with missing phase file → error message contains file path
2. Unit test with phase sequence [1, 2, 4] → warning about gap at 3

**Dependencies**: T02.02 (discover_phases must exist)
**Rollback**: Revert additions to `config.py`
**Notes**: Warnings do not block execution; errors do.

---

### T02.04 — Implement load_sprint_config in config.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-010 |
| **Why** | Combines discovery + validation + auto-detection into single entry point for executor; raises ClickException on fatal errors |
| **Effort** | S (orchestration of existing functions + auto-detection logic) |
| **Risk** | Medium (integration of 3 sub-functions; ClickException handling) |
| **Risk Drivers** | Auto-detection of end_phase; ClickException formatting; config object completeness |
| **Tier** | STANDARD — keyword: implement, create |
| **Confidence Bar** | [█████████-] 90% — composes already-implemented functions |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — executor depends on this |
| **Verification Method** | Direct test: integration test with sample index |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0008 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0008/spec.md`, `TASKLIST_ROOT/artifacts/D-0008/evidence.md` |

**Deliverables**:
- `load_sprint_config()` combining discovery, validation, and auto-detection

**Steps**:
1. `[PLANNING]` Define the orchestration flow: discover → validate → build SprintConfig → auto-detect end_phase
2. `[EXECUTION]` Implement `load_sprint_config()` composing discover_phases and validate_phases
3. `[EXECUTION]` Add end_phase auto-detection from discovered phase count
4. `[EXECUTION]` Add ClickException raising for fatal validation errors
5. `[VERIFICATION]` Integration test with sample index file

**Acceptance Criteria**:
1. Full SprintConfig loaded from sample index with correct phase list
2. end_phase auto-detected when not explicitly provided
3. Fatal validation errors raise ClickException with descriptive message
4. Non-fatal warnings logged but do not abort

**Validation**:
1. Unit test with valid index → SprintConfig returned with all fields populated
2. Unit test with invalid config → ClickException raised

**Dependencies**: T02.02, T02.03
**Rollback**: Revert additions to `config.py`
**Notes**: This is the public API of config.py — other modules should only call this function.

---

### T02.05 — Implement ClaudeProcess class in process.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-011 |
| **Why** | Manages Claude CLI subprocess lifecycle — command construction, environment setup, process group isolation, and graceful termination |
| **Effort** | M (6 methods; process group management; platform considerations) |
| **Risk** | High (R-001: CLI flag changes; R-003: os.setpgrp Windows; subprocess lifecycle complexity) |
| **Risk Drivers** | Claude CLI flag compatibility; os.setpgrp platform availability; process group cleanup; timeout calculation |
| **Tier** | STRICT — keywords: system-wide, process management; context booster: security-adjacent (process isolation) |
| **Confidence Bar** | [█████████-] 90% — spec fully defines command construction |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — executor launches processes through this |
| **Verification Method** | Sub-agent: verify command flags match spec; platform check for os.setpgrp |
| **MCP Requirements** | Sequential (platform compatibility analysis) |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0009 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0009/spec.md`, `TASKLIST_ROOT/artifacts/D-0009/evidence.md` |

**Deliverables**:
- `ClaudeProcess` class with `build_prompt()`, `build_command()`, `build_env()`, `start()`, `wait()`, `terminate()` methods

**Steps**:
1. `[PLANNING]` Extract command construction rules from spec: required flags (`--print`, `--no-session-persistence`, `--max-turns`, `--output-format text`), prompt template with `/sc:task-unified`
2. `[EXECUTION]` Create `process.py` with ClaudeProcess class and `build_prompt()`, `build_command()`, `build_env()` methods
3. `[EXECUTION]` Implement `start()` with `os.setpgrp` process group creation and platform check fallback
4. `[EXECUTION]` Implement `wait()` with polling and `terminate()` with process group signal
5. `[EXECUTION]` Add timeout calculation: `max_turns * 120 + 300`
6. `[VERIFICATION]` Unit test command construction; verify all required flags present

**Acceptance Criteria**:
1. `build_command()` output includes `--print`, `--no-session-persistence`, `--max-turns`, `--output-format text`
2. `build_prompt()` contains `/sc:task-unified` invocation
3. Process group created with `os.setpgrp` on Unix; graceful fallback on unsupported platforms
4. `build_env()` sets `CLAUDECODE=""` in environment

**Validation**:
1. Unit test: `build_command()` contains all 4 required flags
2. Unit test: `build_env()` includes `CLAUDECODE=""` key

**Dependencies**: T01.01 (Phase, SprintConfig dataclasses)
**Rollback**: Delete `src/superclaude/cli/sprint/process.py`
**Notes**: Abstract command construction behind method for R-001 risk mitigation. Document Unix/macOS requirement per R-003.

---

### Checkpoint: Phase 2 / Tasks T02.01–T02.05

**Purpose:** Validate that commands.py, config.py, and process.py are complete and importable after first 5 backend tasks.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-T01-T05.md`
**Verification:**
- All 5 tasks (T02.01–T02.05) marked completed
- config.py and process.py importable; commands.py --help works
- Import verification log and --help output captured
**Exit Criteria:**
- All deliverables D-0005 through D-0009 produce verifiable artifacts
- No blocked tasks remain in Phase 2
- Remaining Phase 2 tasks (T02.06–T02.08) unblocked

---

### T02.06 — Implement SignalHandler in process.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-012 |
| **Why** | Enables graceful shutdown on SIGINT/SIGTERM — sets shutdown flag and restores original signal handlers on cleanup |
| **Effort** | S (signal registration + flag management + handler restoration) |
| **Risk** | Medium (signal handling edge cases; handler restoration order) |
| **Risk Drivers** | Signal race conditions; original handler preservation; nested signal handling |
| **Tier** | STRICT — keywords: system-wide, signal handling (process-level concern) |
| **Confidence Bar** | [█████████-] 90% — standard signal handling pattern |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — executor needs graceful shutdown |
| **Verification Method** | Sub-agent: verify signal registration and handler restoration |
| **MCP Requirements** | None |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0010 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0010/spec.md`, `TASKLIST_ROOT/artifacts/D-0010/evidence.md` |

**Deliverables**:
- `SignalHandler` class with install/uninstall and `shutdown_requested` flag

**Steps**:
1. `[PLANNING]` Design signal handler lifecycle: install → handle signals → uninstall with original handler restoration
2. `[EXECUTION]` Implement `SignalHandler` with `install()` registering SIGINT/SIGTERM handlers
3. `[EXECUTION]` Implement `shutdown_requested` flag and `uninstall()` restoring original handlers
4. `[VERIFICATION]` Unit test: signal delivery sets flag; uninstall restores originals

**Acceptance Criteria**:
1. `shutdown_requested` flag set to True on SIGINT delivery
2. `shutdown_requested` flag set to True on SIGTERM delivery
3. Original signal handlers restored after `uninstall()`
4. Handler is idempotent — multiple signals do not cause errors

**Validation**:
1. Unit test: send SIGINT → `shutdown_requested` is True
2. Unit test: `uninstall()` → original handler restored (verified via `signal.getsignal`)

**Dependencies**: None (can be implemented independently)
**Rollback**: Revert additions to `process.py`
**Notes**: Use `signal.signal()` not `signal.sigaction()` for portability.

---

### T02.07 — Implement execute_sprint orchestration loop

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-013 |
| **Why** | Core execution engine — iterates phases, launches subprocesses, polls for completion, determines status, and halts on failure |
| **Effort** | L (orchestration of config + process + status determination; halt logic; result aggregation) |
| **Risk** | High (integration complexity; subprocess polling; status determination chain; halt-on-failure logic) |
| **Risk Drivers** | Polling loop correctness; status priority chain compliance; halt condition accuracy; result aggregation |
| **Tier** | STRICT — keywords: system-wide, multi-file (orchestrates config, process, models) |
| **Confidence Bar** | [█████████-] 90% — spec Section 8 fully defines status priority chain |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — this IS the critical path |
| **Verification Method** | Sub-agent: verify status determination matches spec Section 8 priority chain |
| **MCP Requirements** | Sequential (orchestration logic analysis) |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0011 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0011/spec.md`, `TASKLIST_ROOT/artifacts/D-0011/evidence.md` |

**Deliverables**:
- `execute_sprint()` function: main orchestration loop

**Steps**:
1. `[PLANNING]` Map orchestration flow: load config → iterate phases → launch process → poll → determine status → halt or continue
2. `[EXECUTION]` Create `executor.py` with `execute_sprint()` accepting SprintConfig
3. `[EXECUTION]` Implement phase iteration loop with ClaudeProcess launch and poll-until-exit
4. `[EXECUTION]` Integrate `_determine_phase_status()` (T02.08) for status determination after each phase
5. `[EXECUTION]` Add halt-on-failure logic: stop iteration on non-continuable status
6. `[EXECUTION]` Build and return SprintResult with all phase results
7. `[VERIFICATION]` Integration test with mocked ClaudeProcess

**Acceptance Criteria**:
1. Iterates all active phases in sequence
2. Launches one subprocess per phase via ClaudeProcess
3. Polls until process exits; respects shutdown_requested flag
4. Halts on failure status (HALT, ERROR, TIMEOUT) and skips remaining phases

**Validation**:
1. Mock test: 3 phases all PASS → SprintResult.outcome == SUCCESS
2. Mock test: phase 2 HALT → phases 3+ skipped, outcome == HALTED

**Dependencies**: T02.04 (config), T02.05 (process), T02.06 (signal handler)
**Rollback**: Delete `src/superclaude/cli/sprint/executor.py`
**Notes**: This is the highest-risk task in the sprint. Ensure signal handler is installed before entering poll loop.

---

### T02.08 — Implement _determine_phase_status

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-014 |
| **Why** | Implements the 7-level status priority chain from spec Section 8 — maps subprocess exit codes and output signals to PhaseStatus enum |
| **Effort** | S (7-level priority chain implementation) |
| **Risk** | Medium (priority ordering must exactly match spec; edge cases at each level) |
| **Risk Drivers** | Priority chain ordering correctness; exit code mapping; signal parsing; frontmatter detection |
| **Tier** | STRICT — keywords: system-wide (status determination affects all phases) |
| **Confidence Bar** | [█████████-] 90% — spec Section 8 is explicit about priority order |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — executor depends on correct status |
| **Verification Method** | Sub-agent: verify all 7 levels match spec priority chain |
| **MCP Requirements** | Sequential (priority chain verification) |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0012 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0012/spec.md`, `TASKLIST_ROOT/artifacts/D-0012/evidence.md` |

**Deliverables**:
- `_determine_phase_status()` implementing: Timeout (exit 124) → ERROR (non-zero) → HALT signal → CONTINUE signal → PASS/FAIL frontmatter → PASS_NO_REPORT → ERROR

**Steps**:
1. `[PLANNING]` Map 7-level priority chain from spec Section 8 to implementation conditions
2. `[EXECUTION]` Implement priority level 1: exit code 124 → TIMEOUT
3. `[EXECUTION]` Implement levels 2-7: non-zero exit → ERROR; HALT signal; CONTINUE signal; PASS/FAIL frontmatter; PASS_NO_REPORT fallback; ERROR default
4. `[VERIFICATION]` Unit test each priority level independently

**Acceptance Criteria**:
1. Exit code 124 → PhaseStatus.TIMEOUT (highest priority)
2. Non-zero exit (non-124) → PhaseStatus.ERROR
3. HALT signal in output → PhaseStatus.HALT
4. Priority chain ordering exactly matches spec Section 8

**Validation**:
1. Unit test: exit code 124 → TIMEOUT regardless of other signals
2. Unit test: exit code 1 with CONTINUE signal → ERROR (exit code takes priority)

**Dependencies**: T01.01 (PhaseStatus enum)
**Rollback**: Revert additions to `executor.py`
**Notes**: Priority chain is the correctness contract — any ordering mistake cascades to wrong sprint outcomes.

---

### Checkpoint: End of Phase 2

**Purpose:** Verify entire backend core complete
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-END.md`
**Verification:**
- All 8 tasks (T02.01–T02.08) marked completed
- `make lint` passes; `uv run pytest tests/sprint/` passes
- Lint and test output captured
**Exit Criteria:**
- All deliverables D-0005 through D-0012 verified
- Lint clean
- Phase 4 and Phase 5 unblocked

---

## Phase 3: TUI Dashboard & Output Monitor

**Milestone**: M3 | **Priority**: P1 | **Effort**: M | **Dependencies**: M1
**Roadmap Items**: R-015 through R-021

---

### T03.01 — Implement SprintTUI class core

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-016 |
| **Why** | Core TUI class providing real-time sprint visibility — Rich Live display at 2 FPS with header, phase table, progress bar, and active phase detail |
| **Effort** | M (Rich Live integration; layout composition; 2 FPS refresh; 4 display sections) |
| **Risk** | Medium (Rich Live API; R-002: tmux compatibility) |
| **Risk Drivers** | Rich Live display setup; refresh rate management; layout composition; tmux compatibility |
| **Tier** | STANDARD — keyword: implement, create, build |
| **Confidence Bar** | [█████████-] 90% — Rich is already a project dependency with known API |
| **Requires Confirmation** | No |
| **Critical Path Override** | No (parallel track with M2) |
| **Verification Method** | Direct test: render to StringIO |
| **MCP Requirements** | Context7 (Rich patterns) |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0013 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0013/spec.md`, `TASKLIST_ROOT/artifacts/D-0013/evidence.md` |

**Deliverables**:
- `SprintTUI` class with `start()`, `stop()`, `update()`, `_render()` methods
- Rich Live display at 2 FPS with header, phase table, progress bar, active phase detail

**Steps**:
1. `[PLANNING]` Design TUI layout: header panel, phase status table, progress bar, active phase detail panel
2. `[EXECUTION]` Create `tui.py` with `SprintTUI` class skeleton and Rich Console/Live setup
3. `[EXECUTION]` Implement `start()` and `stop()` managing Rich Live context
4. `[EXECUTION]` Implement `_render()` composing all 4 display sections into a Layout
5. `[EXECUTION]` Implement `update()` accepting MonitorState and triggering re-render at 2 FPS
6. `[VERIFICATION]` Render to StringIO and verify output contains all 4 sections

**Acceptance Criteria**:
1. `start()` initializes Rich Live display at 2 FPS refresh rate
2. `stop()` cleanly shuts down Rich Live without terminal corruption
3. `_render()` output contains header, phase table, progress bar, and active phase detail
4. `update()` accepts MonitorState and triggers re-render

**Validation**:
1. StringIO render test: output contains "Phase" table header and progress bar
2. Start/stop lifecycle test: no exceptions raised, terminal restored

**Dependencies**: T01.01 (MonitorState, Phase, SprintConfig, PhaseStatus dataclasses)
**Rollback**: Delete `src/superclaude/cli/sprint/tui.py`
**Notes**: Use `Console(file=StringIO())` for testable rendering. Design for both tmux and direct terminal use.

---

### T03.02 — Implement TUI phase table with status rendering

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-017 |
| **Why** | Color-coded phase status table provides at-a-glance sprint progress — STATUS_STYLES and STATUS_ICONS mappings per spec |
| **Effort** | S (Rich Table with Style mappings) |
| **Risk** | Low (Rich Table API is well-documented) |
| **Risk Drivers** | Color mapping correctness; Rich Style API |
| **Tier** | STANDARD — keyword: implement |
| **Confidence Bar** | [█████████-] 90% — color mappings fully specified in roadmap |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: verify color codes in rendered output |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0014 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0014/spec.md`, `TASKLIST_ROOT/artifacts/D-0014/evidence.md` |

**Deliverables**:
- Phase table with color-coded status: green (PASS), red (HALT/TIMEOUT/ERROR), yellow (RUNNING), dim (pending/skipped)

**Steps**:
1. `[PLANNING]` Define STATUS_STYLES and STATUS_ICONS constant mappings
2. `[EXECUTION]` Implement `_build_phase_table()` method with Rich Table and style application
3. `[EXECUTION]` Apply correct colors: green=PASS, red=HALT/TIMEOUT/ERROR, yellow=RUNNING, dim=pending/skipped
4. `[VERIFICATION]` Render with each status and verify color/icon mapping

**Acceptance Criteria**:
1. PASS status renders in green with success icon
2. HALT, TIMEOUT, ERROR statuses render in red with failure icons
3. RUNNING status renders in yellow with activity icon
4. Pending and skipped statuses render in dim with appropriate icons

**Validation**:
1. Render test with PASS phase → green styling in output
2. Render test with all statuses → each has correct color

**Dependencies**: T03.01 (SprintTUI class must exist)
**Rollback**: Revert additions to `tui.py`
**Notes**: Use Rich `Style` objects, not raw ANSI codes.

---

### T03.03 — Implement TUI active phase detail panel

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-018 |
| **Why** | Shows real-time detail for the currently executing phase — file, status, stall indicator, last task/tool, output size, growth rate, files changed |
| **Effort** | S (Rich Panel with dynamic MonitorState data binding) |
| **Risk** | Medium (stall detection display logic; growth rate calculation) |
| **Risk Drivers** | Stall indicator timing (30s thinking, 60s stalled); growth rate display accuracy |
| **Tier** | STANDARD — keyword: implement, build |
| **Confidence Bar** | [█████████-] 90% — display fields fully specified |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: verify stall indicator text |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0015 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0015/spec.md`, `TASKLIST_ROOT/artifacts/D-0015/evidence.md` |

**Deliverables**:
- Active phase detail panel showing: file, status, stall indicator, last task/tool, output size, growth rate, files changed
- Stall display: "thinking..." (yellow) after 30s, "STALLED" (red blink) after 60s

**Steps**:
1. `[PLANNING]` Map MonitorState fields to display layout: file path, status text, stall indicator, task/tool info, metrics
2. `[EXECUTION]` Implement `_build_active_detail()` method with Rich Panel
3. `[EXECUTION]` Add stall indicator logic: "thinking..." (yellow) at 30s, "STALLED" (red blink) at 60s
4. `[EXECUTION]` Add growth rate and output size display from MonitorState
5. `[VERIFICATION]` Render with stall states and verify indicator text/color

**Acceptance Criteria**:
1. Panel updates on each `tui.update()` call with current MonitorState
2. Stall display shows "thinking..." in yellow after 30s of no growth
3. Stall display shows "STALLED" in red (blink) after 60s of no growth
4. All fields (file, status, last task/tool, output size, growth rate, files changed) rendered

**Validation**:
1. Render test with stall_seconds=35 → "thinking..." in output
2. Render test with stall_seconds=65 → "STALLED" in output

**Dependencies**: T03.01 (SprintTUI class)
**Rollback**: Revert additions to `tui.py`
**Notes**: Use MonitorState.stall_status property for threshold logic.

---

### T03.04 — Implement TUI terminal states

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-019 |
| **Why** | Final TUI displays for sprint completion (success) and halt (failure with resume command) — user's last impression of sprint outcome |
| **Effort** | S (two terminal state layouts) |
| **Risk** | Low (static display, no timing concerns) |
| **Risk Drivers** | Resume command formatting; duration display accuracy |
| **Tier** | STANDARD — keyword: implement |
| **Confidence Bar** | [█████████-] 90% — terminal states fully specified |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: verify terminal state text |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0016 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0016/spec.md`, `TASKLIST_ROOT/artifacts/D-0016/evidence.md` |

**Deliverables**:
- Complete state: "ALL PHASES PASSED" with total duration
- Halted state: failure details and resume command

**Steps**:
1. `[PLANNING]` Design complete and halted terminal state layouts
2. `[EXECUTION]` Implement `_render_complete()` showing "ALL PHASES PASSED" with total duration
3. `[EXECUTION]` Implement `_render_halted()` showing failure details and resume_command()
4. `[VERIFICATION]` Render both states and verify text content

**Acceptance Criteria**:
1. Complete state displays "ALL PHASES PASSED" with total duration
2. Halted state displays failure details identifying the failed phase
3. Halted state includes resume command from SprintResult.resume_command()
4. Both states stop the Live display refresh (static final output)

**Validation**:
1. Render complete state → "ALL PHASES PASSED" in output
2. Render halted state → resume command string in output

**Dependencies**: T03.01 (SprintTUI class)
**Rollback**: Revert additions to `tui.py`
**Notes**: Terminal states replace the Live display with static Rich output.

---

### T03.05 — Implement OutputMonitor class

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-020 |
| **Why** | Sidecar daemon thread that reads Claude subprocess output in real-time — provides MonitorState updates to TUI without blocking executor |
| **Effort** | M (daemon thread; file polling; incremental reads; thread safety) |
| **Risk** | Medium (R-004: GIL-free threading; file handle management; race conditions) |
| **Risk Drivers** | Thread safety without locks (GIL-dependent); file polling interval; incremental byte tracking |
| **Tier** | STRICT — keywords: system-wide (threading, GIL dependency); context booster: multi-file communication pattern |
| **Confidence Bar** | [█████████-] 90% — GIL-safe pattern is well-understood for CPython |
| **Requires Confirmation** | No |
| **Critical Path Override** | No (parallel track) |
| **Verification Method** | Sub-agent: verify thread safety and file handle management |
| **MCP Requirements** | Sequential (threading analysis) |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0017 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0017/spec.md`, `TASKLIST_ROOT/artifacts/D-0017/evidence.md` |

**Deliverables**:
- `OutputMonitor` class with `start()`, `stop()`, `reset()` methods
- Daemon thread polling at 500ms; incremental reads; no held file handles

**Steps**:
1. `[PLANNING]` Design monitor lifecycle: start daemon thread → poll output file → read new bytes → update MonitorState → stop on request
2. `[EXECUTION]` Create `monitor.py` with `OutputMonitor` class
3. `[EXECUTION]` Implement daemon thread with 500ms polling interval
4. `[EXECUTION]` Implement incremental read: track last position, read only new bytes, close file after each read
5. `[EXECUTION]` Implement `reset()` for phase transitions (new output file)
6. `[VERIFICATION]` Test with mock output file growing over time

**Acceptance Criteria**:
1. Daemon thread polls at 500ms intervals
2. Reads only new bytes since last position (no re-reading)
3. Does not hold file open between polls
4. `reset()` clears state for new phase output file

**Validation**:
1. Test: write bytes to file → monitor detects new content within 1s
2. Test: `stop()` → daemon thread terminates within 1s

**Dependencies**: T01.01 (MonitorState dataclass)
**Rollback**: Delete `src/superclaude/cli/sprint/monitor.py`
**Notes**: GIL-safe pattern: single writer (monitor thread) to MonitorState, single reader (TUI main thread). Document GIL dependency per R-004.

---

### Checkpoint: Phase 3 / Tasks T03.01–T03.05

**Purpose:** Validate TUI core and monitor complete
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-T01-T05.md`
**Verification:**
- All 5 tasks (T03.01–T03.05) marked completed
- tui.py and monitor.py importable; StringIO render tests pass
- Import verification and render test output captured
**Exit Criteria:**
- All deliverables D-0013 through D-0017 verified
- No blocked tasks remain in Phase 3
- T03.06 unblocked

---

### T03.06 — Implement monitor signal extraction

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-021 |
| **Why** | Extracts structured signals from Claude output — task IDs, tool names, and file paths feed into MonitorState and TUI active phase detail |
| **Effort** | S (regex pattern matching for 3 signal types) |
| **Risk** | Medium (R-005: regex may miss new output formats) |
| **Risk Drivers** | Regex pattern completeness; new Claude output format compatibility |
| **Tier** | STANDARD — keyword: implement |
| **Confidence Bar** | [████████--] 85% — regex patterns based on known Claude output format; R-005 risk applies |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: regex against sample Claude output |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0018 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0018/spec.md`, `TASKLIST_ROOT/artifacts/D-0018/evidence.md` |

**Deliverables**:
- Signal extraction via regex: task IDs (T##.##), tool names (Read, Edit, Bash, etc.), file paths

**Steps**:
1. `[PLANNING]` Define regex patterns: `T\d{2}\.\d{2}` for task IDs; tool name list; file path pattern
2. `[EXECUTION]` Implement `_extract_signals()` method in OutputMonitor
3. `[EXECUTION]` Integrate extraction into polling loop — update MonitorState with latest signals
4. `[VERIFICATION]` Test against sample Claude output strings

**Acceptance Criteria**:
1. Correctly parses task IDs matching T##.## pattern
2. Correctly identifies tool names (Read, Edit, Bash, Write, Grep, Glob, etc.)
3. Correctly extracts file modification path patterns
4. Updates MonitorState with latest extracted signals

**Validation**:
1. Test: sample output containing "T02.05" → task_id extracted
2. Test: sample output containing "Read tool" → tool name extracted

**Dependencies**: T03.05 (OutputMonitor class)
**Rollback**: Revert additions to `monitor.py`
**Notes**: Centralize regex patterns as module-level constants for easy updates per R-005 mitigation.

---

### Checkpoint: End of Phase 3

**Purpose:** Verify TUI and monitor fully functional
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-END.md`
**Verification:**
- All 6 tasks (T03.01–T03.06) marked completed
- `make lint` passes on tui.py and monitor.py; all render tests pass
- Lint and render test output captured
**Exit Criteria:**
- All deliverables D-0013 through D-0018 verified
- Lint clean
- Phase 4 unblocked

---

## Phase 4: Validation Checkpoint 1

**Milestone**: M4 | **Priority**: P3 | **Effort**: S | **Dependencies**: M2, M3
**Roadmap Items**: R-022 through R-025

---

### T04.01 — Integration test: full phase lifecycle

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-023 |
| **Why** | Validates that executor + mocked ClaudeProcess + TUI integrate correctly through the full lifecycle: PENDING → RUNNING → PASS |
| **Effort** | S (mocking subprocess + TUI StringIO capture + lifecycle assertion) |
| **Risk** | Medium (integration timing; mock fidelity to real ClaudeProcess behavior) |
| **Risk Drivers** | Mock completeness; TUI state transition capture; lifecycle coverage |
| **Tier** | STANDARD — keyword: test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [████████--] 85% — mock-based testing isolates timing issues |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0019 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0019/spec.md`, `TASKLIST_ROOT/artifacts/D-0019/evidence.md` |

**Deliverables**:
- Integration test driving TUI through PENDING → RUNNING → PASS lifecycle with mocked ClaudeProcess

**Steps**:
1. `[PLANNING]` Design mock ClaudeProcess that exits successfully with PASS frontmatter
2. `[EXECUTION]` Create test file with mock subprocess and TUI StringIO capture
3. `[EXECUTION]` Assert TUI output shows PENDING → RUNNING → PASS state transitions
4. `[VERIFICATION]` Run test and verify lifecycle transitions captured

**Acceptance Criteria**:
1. Test renders TUI to StringIO successfully
2. Status transitions PENDING → RUNNING → PASS verified in output
3. Mock ClaudeProcess behavior matches real process lifecycle
4. Test completes within 10s timeout

**Validation**:
1. `uv run pytest tests/sprint/test_integration_lifecycle.py -v` → passes
2. Test output contains all 3 status transitions

**Dependencies**: T02.07 (executor), T03.01 (TUI), T03.05 (monitor)
**Rollback**: Delete test file
**Notes**: R-RULE-08 — test must not modify source modules.

---

### T04.02 — Integration test: halt and resume command

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-024 |
| **Why** | Validates halt behavior: executor stops on STRICT-tier failure; SprintResult contains correct resume_command(); TUI shows halted state |
| **Effort** | S (mock failure + resume command validation) |
| **Risk** | Low (deterministic failure scenario) |
| **Risk Drivers** | Resume command format correctness; halt state TUI rendering |
| **Tier** | STANDARD — keyword: test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [█████████-] 90% — halt behavior is deterministic |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0020 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0020/spec.md`, `TASKLIST_ROOT/artifacts/D-0020/evidence.md` |

**Deliverables**:
- Integration test: executor halts on failure; resume command produced; TUI shows halted state

**Steps**:
1. `[PLANNING]` Design mock ClaudeProcess that exits with non-zero code at phase 2
2. `[EXECUTION]` Create test with multi-phase config where phase 2 fails
3. `[EXECUTION]` Assert SprintResult contains correct resume_command() and halted outcome
4. `[VERIFICATION]` Run test and verify halt behavior

**Acceptance Criteria**:
1. Halted sprint result contains correct `resume_command()` value
2. TUI shows halted state with failure details
3. Phases after failure phase are not executed (skipped)
4. SprintResult outcome is HALTED

**Validation**:
1. `uv run pytest tests/sprint/test_integration_halt.py -v` → passes
2. Assert `resume_command()` contains correct start_phase

**Dependencies**: T02.07 (executor), T03.04 (TUI terminal states)
**Rollback**: Delete test file
**Notes**: Tests resume command format only — actual resume execution tested in M7.

---

### T04.03 — Integration test: graceful shutdown

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-025 |
| **Why** | Validates that SIGINT during execution triggers graceful shutdown: process terminated, partial log written, INTERRUPTED outcome |
| **Effort** | S (signal delivery during test + state verification) |
| **Risk** | Medium (signal timing in test environment; partial state verification) |
| **Risk Drivers** | Signal delivery timing; process termination verification; partial log correctness |
| **Tier** | STANDARD — keyword: test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [████████--] 85% — signal handling in tests can have timing sensitivity |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0021 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0021/spec.md`, `TASKLIST_ROOT/artifacts/D-0021/evidence.md` |

**Deliverables**:
- Integration test: SIGINT during poll loop → process terminated → partial log written → INTERRUPTED outcome

**Steps**:
1. `[PLANNING]` Design test that sends SIGINT to own process during executor poll loop
2. `[EXECUTION]` Create test with signal delivery via threading.Timer
3. `[EXECUTION]` Assert process terminated, partial results captured, INTERRUPTED outcome
4. `[VERIFICATION]` Run test and verify graceful shutdown

**Acceptance Criteria**:
1. SIGINT during poll loop triggers shutdown_requested flag
2. Running process is terminated via SignalHandler
3. Partial log/results written for completed phases
4. SprintResult outcome is INTERRUPTED

**Validation**:
1. `uv run pytest tests/sprint/test_integration_signal.py -v` → passes
2. Assert outcome == SprintOutcome.INTERRUPTED

**Dependencies**: T02.06 (SignalHandler), T02.07 (executor)
**Rollback**: Delete test file
**Notes**: Use `threading.Timer(0.5, os.kill, (os.getpid(), signal.SIGINT))` for deterministic signal delivery.

---

### Checkpoint: End of Phase 4

**Purpose:** Verify M2+M3 integration
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-END.md`
**Verification:**
- All 3 integration tests pass; executor↔TUI↔monitor integration verified
- Test output logged
**Exit Criteria:**
- All deliverables D-0019 through D-0021 verified
- No integration blockers
- Phase 7 informed

---

## Phase 5: Integration — Tmux, Logging & Notifications

**Milestone**: M5 | **Priority**: P1 | **Effort**: M | **Dependencies**: M2, M3
**Roadmap Items**: R-026 through R-032

---

### T05.01 — Implement tmux utility functions

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-027 |
| **Why** | Foundation for tmux integration — binary detection, deterministic session naming, and session discovery enable detachable sprint execution |
| **Effort** | S (3 utility functions; subprocess.run for tmux commands) |
| **Risk** | Low (R-006: tmux unavailable in CI — mitigated by fallback design) |
| **Risk Drivers** | Tmux binary detection; session name hash determinism; session listing reliability |
| **Tier** | STANDARD — keyword: implement, create |
| **Confidence Bar** | [█████████-] 90% — tmux CLI is stable and well-documented |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: mocked subprocess.run |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0022 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0022/spec.md`, `TASKLIST_ROOT/artifacts/D-0022/evidence.md` |

**Deliverables**:
- `is_tmux_available()`, `session_name()`, `find_running_session()` functions

**Steps**:
1. `[PLANNING]` Design utility functions: binary check via `shutil.which`, session name from directory hash, session list via `tmux ls`
2. `[EXECUTION]` Create `tmux.py` with `is_tmux_available()` using `shutil.which("tmux")`
3. `[EXECUTION]` Implement `session_name()` generating deterministic name from release dir hash: `sc-sprint-{hash[:8]}`
4. `[EXECUTION]` Implement `find_running_session()` parsing `tmux ls` output for `sc-sprint-*` sessions
5. `[VERIFICATION]` Test with mocked subprocess.run

**Acceptance Criteria**:
1. `is_tmux_available()` correctly detects tmux binary presence/absence
2. `session_name()` generates deterministic name from release directory hash
3. `find_running_session()` correctly identifies `sc-sprint-*` sessions from `tmux ls` output
4. All functions handle tmux-not-found gracefully (return False/None, no exceptions)

**Validation**:
1. Mock test: `shutil.which` returns path → `is_tmux_available()` returns True
2. Mock test: same directory → same session name (deterministic)

**Dependencies**: T02.05 (SprintConfig for directory path)
**Rollback**: Delete `src/superclaude/cli/sprint/tmux.py`
**Notes**: Session name hash ensures unique but reproducible names per release directory.

---

### T05.02 — Implement launch_in_tmux

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-028 |
| **Why** | Creates detachable tmux session with two-pane layout (75% TUI / 25% tail) for background sprint execution |
| **Effort** | S (tmux new-session + split-pane commands) |
| **Risk** | Medium (tmux command syntax; pane percentage calculation; R-002: older tmux compatibility) |
| **Risk Drivers** | Tmux command correctness; pane split percentage; session creation error handling |
| **Tier** | STANDARD — keyword: implement, create |
| **Confidence Bar** | [████████--] 85% — tmux split-window syntax varies slightly between versions |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: mocked subprocess.run with command verification |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0023 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0023/spec.md`, `TASKLIST_ROOT/artifacts/D-0023/evidence.md` |

**Deliverables**:
- `launch_in_tmux()` creating detached session with 75%/25% pane split

**Steps**:
1. `[PLANNING]` Map tmux commands: `new-session -d`, `split-window -v -p 25`, pane targeting
2. `[EXECUTION]` Implement `launch_in_tmux()` with tmux new-session and split-window commands
3. `[EXECUTION]` Configure top pane (75%) for TUI command, bottom pane (25%) for `tail -f` of output
4. `[VERIFICATION]` Verify mocked subprocess.run calls contain correct tmux commands

**Acceptance Criteria**:
1. Creates detached tmux session with correct session name
2. Top pane (75%) runs the sprint TUI command
3. Bottom pane (25%) runs `tail -f` on phase output file
4. Tmux commands verified via mocked `subprocess.run`

**Validation**:
1. Mock test: verify `tmux new-session` command in subprocess.run calls
2. Mock test: verify `split-window -v -p 25` in subprocess.run calls

**Dependencies**: T05.01 (tmux utility functions)
**Rollback**: Revert additions to `tmux.py`
**Notes**: Use `-p` flag for percentage split; fallback to absolute size for tmux <3.0.

---

### T05.03 — Implement tmux session management

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-029 |
| **Why** | Enables sprint lifecycle management: attach to running sprint, kill with graceful timeout, switch tail pane on phase change |
| **Effort** | S (3 management functions; SIGTERM→SIGKILL escalation) |
| **Risk** | Medium (SIGTERM→SIGKILL timing; tail pane update during execution) |
| **Risk Drivers** | Kill escalation timing (10s); pane targeting correctness; session state verification |
| **Tier** | STANDARD — keyword: implement |
| **Confidence Bar** | [█████████-] 90% — tmux session management is well-documented |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: mocked subprocess.run |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0024 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0024/spec.md`, `TASKLIST_ROOT/artifacts/D-0024/evidence.md` |

**Deliverables**:
- `attach_to_sprint()`, `kill_sprint()`, `update_tail_pane()` functions
- Kill sends SIGTERM then SIGKILL after 10s

**Steps**:
1. `[PLANNING]` Design kill escalation: SIGTERM → wait 10s → SIGKILL if still alive
2. `[EXECUTION]` Implement `attach_to_sprint()` using `tmux attach-session`
3. `[EXECUTION]` Implement `kill_sprint()` with SIGTERM→SIGKILL escalation after 10s
4. `[EXECUTION]` Implement `update_tail_pane()` switching output file in tail pane on phase change
5. `[VERIFICATION]` Verify kill escalation sequence via mocked subprocess

**Acceptance Criteria**:
1. `attach_to_sprint()` reconnects to running sprint session
2. `kill_sprint()` sends SIGTERM first, then SIGKILL after 10s if needed
3. `update_tail_pane()` switches tail target file on phase change
4. All functions handle missing/dead sessions gracefully

**Validation**:
1. Mock test: `kill_sprint()` → SIGTERM sent, then SIGKILL after timeout
2. Mock test: `attach_to_sprint()` → `tmux attach-session` command executed

**Dependencies**: T05.01 (tmux utility functions)
**Rollback**: Revert additions to `tmux.py`
**Notes**: SIGTERM→SIGKILL pattern matches standard daemon shutdown conventions.

---

### T05.04 — Implement SprintLogger class

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-030 |
| **Why** | Dual-format structured logging — JSONL for machine parsing and Markdown table for human reading; provides execution audit trail |
| **Effort** | M (dual format writing; JSONL schema; Markdown table appending; summary generation) |
| **Risk** | Medium (JSONL schema compliance; Markdown formatting; file handle management) |
| **Risk Drivers** | JSONL field completeness; Markdown table alignment; file write atomicity |
| **Tier** | STRICT — keywords: schema (JSONL event schema); multi-file (writes to 2 formats); context booster: >2 files affected (+0.3) |
| **Confidence Bar** | [█████████-] 90% — JSONL and Markdown formats are well-defined |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Sub-agent: verify JSONL schema and Markdown format |
| **MCP Requirements** | None |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0025 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0025/spec.md`, `TASKLIST_ROOT/artifacts/D-0025/evidence.md` |

**Deliverables**:
- `SprintLogger` class with `write_header()`, `write_phase_result()`, `write_summary()` methods
- JSONL events with all documented fields; Markdown table rows

**Steps**:
1. `[PLANNING]` Define JSONL event schema and Markdown table format from spec
2. `[EXECUTION]` Create `logging_.py` with `SprintLogger` class
3. `[EXECUTION]` Implement `write_header()` — initial JSONL event + Markdown header row
4. `[EXECUTION]` Implement `write_phase_result()` — append JSONL event + Markdown table row per phase
5. `[EXECUTION]` Implement `write_summary()` — final JSONL event + Markdown summary with outcome, duration, resume command
6. `[VERIFICATION]` Verify JSONL is valid JSON per line; Markdown table renders correctly

**Acceptance Criteria**:
1. JSONL events contain all documented fields (timestamp, phase, status, duration, etc.)
2. Markdown table rows appended correctly with aligned columns
3. Summary includes outcome, total duration, and resume command (if halted)
4. Each JSONL line is valid JSON (parseable by `json.loads`)

**Validation**:
1. Test: `write_phase_result()` → JSONL line parseable; contains required fields
2. Test: `write_summary()` → Markdown contains outcome and duration

**Dependencies**: T01.01 (SprintResult, PhaseResult dataclasses)
**Rollback**: Delete `src/superclaude/cli/sprint/logging_.py`
**Notes**: Use `logging_` (trailing underscore) to avoid shadowing stdlib `logging` module.

---

### T05.05 — Implement log levels and output routing

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-031 |
| **Why** | Routes log output by severity: DEBUG→JSONL only, INFO→all targets, WARN/ERROR→highlighted with terminal bell; screen output to stderr (TUI uses stdout) |
| **Effort** | S (level routing; stderr output; terminal bell) |
| **Risk** | Low (standard logging patterns) |
| **Risk Drivers** | Stderr vs stdout routing; terminal bell character; level-based filtering |
| **Tier** | STANDARD — keyword: implement |
| **Confidence Bar** | [█████████-] 90% — standard logging level pattern |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: verify output routing per level |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0026 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0026/spec.md`, `TASKLIST_ROOT/artifacts/D-0026/evidence.md` |

**Deliverables**:
- Log level routing: DEBUG→JSONL, INFO→all, WARN/ERROR→highlighted+bell
- Screen output to stderr; JSONL to file

**Steps**:
1. `[PLANNING]` Map log levels to output targets: DEBUG→file only, INFO→file+stderr, WARN/ERROR→file+stderr+bell
2. `[EXECUTION]` Implement level-based routing in SprintLogger
3. `[EXECUTION]` Add terminal bell (`\a`) for ERROR events
4. `[EXECUTION]` Ensure all screen output goes to stderr (TUI owns stdout)
5. `[VERIFICATION]` Test each log level routes to correct targets

**Acceptance Criteria**:
1. DEBUG events appear only in JSONL file, not on screen
2. INFO events appear in both JSONL file and stderr
3. ERROR events produce terminal bell character (`\a`) on stderr
4. All screen output uses stderr (stdout reserved for TUI)

**Validation**:
1. Test: DEBUG log → not in stderr capture, present in JSONL file
2. Test: ERROR log → `\a` character in stderr output

**Dependencies**: T05.04 (SprintLogger class)
**Rollback**: Revert additions to `logging_.py`
**Notes**: `sys.stderr.write()` for screen output; `sys.stdout` reserved for Rich Live display.

---

### Checkpoint: Phase 5 / Tasks T05.01–T05.05

**Purpose:** Validate tmux and logging complete
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P05-T01-T05.md`
**Verification:**
- All 5 tasks (T05.01–T05.05) marked completed
- tmux.py and logging_.py importable; JSONL output valid
- Import verification and JSONL validation captured
**Exit Criteria:**
- All deliverables D-0022 through D-0026 verified
- No blocked tasks remain in Phase 5
- T05.06 unblocked

---

### T05.06 — Implement cross-platform desktop notifications

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-032 |
| **Why** | Notifies user of sprint completion or failure when running in detached tmux — best-effort with silent failure |
| **Effort** | S (platform detection + 2 notification backends) |
| **Risk** | Low (R-009: notification deps optional — silent failure pattern) |
| **Risk Drivers** | Platform detection accuracy; `notify-send`/`osascript` availability; timeout handling |
| **Tier** | STANDARD — keyword: implement, create |
| **Confidence Bar** | [█████████-] 90% — platform detection via `sys.platform` is deterministic |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: mocked notification commands |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0027 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0027/spec.md`, `TASKLIST_ROOT/artifacts/D-0027/evidence.md` |

**Deliverables**:
- Cross-platform notifications: `notify-send` (Linux), `osascript` (macOS)
- Silent failure with 5s timeout; urgent flag sets critical urgency

**Steps**:
1. `[PLANNING]` Map platform → notification command: Linux=`notify-send`, macOS=`osascript`
2. `[EXECUTION]` Create `notify.py` with platform detection and notification dispatch
3. `[EXECUTION]` Implement `notify-send` backend with urgency levels and 5s timeout
4. `[EXECUTION]` Implement `osascript` backend with display notification and 5s timeout
5. `[EXECUTION]` Add silent failure: catch all exceptions, log warning, continue
6. `[VERIFICATION]` Test with mocked subprocess; verify silent failure on missing binary

**Acceptance Criteria**:
1. Platform detection correctly identifies Linux vs macOS
2. Linux uses `notify-send` with correct urgency parameter
3. macOS uses `osascript -e 'display notification ...'`
4. Missing notification binary fails silently (no exception propagation)

**Validation**:
1. Mock test: `sys.platform="linux"` → `notify-send` command used
2. Mock test: subprocess raises FileNotFoundError → function returns without exception

**Dependencies**: None (independent utility)
**Rollback**: Delete `src/superclaude/cli/sprint/notify.py`
**Notes**: Documented as optional feature per R-009.

---

### Checkpoint: End of Phase 5

**Purpose:** Verify all source modules complete
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P05-END.md`
**Verification:**
- All 6 tasks (T05.01–T05.06) marked completed
- `make lint` passes; all D5.x deliverables verified
- Lint and JSONL validation captured
**Exit Criteria:**
- All deliverables D-0022 through D-0027 verified
- All source modules complete
- Phase 6 unblocked

---

## Phase 6: Testing & Hardening

**Milestone**: M6 | **Priority**: P2 | **Effort**: M | **Dependencies**: M5
**Roadmap Items**: R-033 through R-038

---

### T06.01 — Write test_config.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-034 |
| **Why** | Comprehensive tests for phase discovery (all 4 naming conventions), validation (missing files, gaps), and config loading |
| **Effort** | S (test fixtures for 4 naming patterns + error cases) |
| **Risk** | Low (testing deterministic functions) |
| **Risk Drivers** | Fixture directory setup; naming pattern coverage |
| **Tier** | STANDARD — keyword: create, test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [█████████-] 90% — config functions are deterministic |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0028 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0028/spec.md`, `TASKLIST_ROOT/artifacts/D-0028/evidence.md` |

**Deliverables**:
- Tests for all 4 naming conventions; gap detection; missing file error messages

**Steps**:
1. `[PLANNING]` Design test fixtures: directories with phase-N, pN, Phase_N, tasklist-PN files; index files; invalid configs
2. `[EXECUTION]` Create `tests/sprint/test_config.py` with discovery tests for all 4 naming patterns
3. `[EXECUTION]` Add validation tests: missing file error, sequence gap warning, gap at phase 3
4. `[EXECUTION]` Add load_sprint_config tests: valid config, invalid config (ClickException)
5. `[VERIFICATION]` Run `uv run pytest tests/sprint/test_config.py -v`

**Acceptance Criteria**:
1. All 4 naming conventions tested with positive discovery results
2. Gap detection verified: phases [1, 2, 4] → gap at 3 detected
3. Missing file produces error message containing the file path
4. Load config test covers both success and ClickException paths

**Validation**:
1. `uv run pytest tests/sprint/test_config.py -v` → all tests pass
2. Test count ≥ 8 (4 naming + 2 validation + 2 load)

**Dependencies**: T02.04 (config.py complete)
**Rollback**: Delete test file
**Notes**: Use `tmp_path` pytest fixture for temporary directory structures.

---

### T06.02 — Write test_monitor.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-035 |
| **Why** | Validates signal extraction regex against sample Claude output; verifies stall counter increments when no growth detected |
| **Effort** | S (regex test fixtures from sample Claude output) |
| **Risk** | Low (regex testing is deterministic) |
| **Risk Drivers** | Sample output representativeness; stall counter edge cases |
| **Tier** | STANDARD — keyword: create, test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [████████--] 85% — regex patterns may need tuning (R-005) |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0029 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0029/spec.md`, `TASKLIST_ROOT/artifacts/D-0029/evidence.md` |

**Deliverables**:
- Tests for task ID, tool name, and file path regex extraction; stall detection

**Steps**:
1. `[PLANNING]` Collect sample Claude output strings containing task IDs, tool names, file paths
2. `[EXECUTION]` Create `tests/sprint/test_monitor.py` with regex extraction tests
3. `[EXECUTION]` Add stall detection tests: no growth → counter increments; growth → counter resets
4. `[VERIFICATION]` Run `uv run pytest tests/sprint/test_monitor.py -v`

**Acceptance Criteria**:
1. Regex correctly extracts task IDs (e.g., "T02.05") from sample output
2. Regex correctly identifies tool names (Read, Edit, Bash, etc.)
3. Stall counter increments when output file size unchanged between polls
4. Stall counter resets when new bytes detected

**Validation**:
1. `uv run pytest tests/sprint/test_monitor.py -v` → all tests pass
2. Test count ≥ 6 (3 regex + 2 stall + 1 reset)

**Dependencies**: T03.06 (monitor signal extraction complete)
**Rollback**: Delete test file
**Notes**: Include edge cases: empty output, partial task IDs, unknown tool names.

---

### T06.03 — Write test_process.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-036 |
| **Why** | Validates command construction, environment building, and timeout calculation — ensures ClaudeProcess produces correct subprocess arguments |
| **Effort** | S (command flag verification + env check + timeout math) |
| **Risk** | Low (deterministic output verification) |
| **Risk Drivers** | Command flag completeness; env key correctness; timeout formula |
| **Tier** | STANDARD — keyword: create, test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [█████████-] 90% — command construction is deterministic |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0030 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0030/spec.md`, `TASKLIST_ROOT/artifacts/D-0030/evidence.md` |

**Deliverables**:
- Tests for command construction, env building, timeout calculation

**Steps**:
1. `[PLANNING]` Define expected command flags, env keys, and timeout formula
2. `[EXECUTION]` Create `tests/sprint/test_process.py` with command construction tests
3. `[EXECUTION]` Add env building test: verify `CLAUDECODE=""` present
4. `[EXECUTION]` Add timeout calculation test: `max_turns * 120 + 300`
5. `[VERIFICATION]` Run `uv run pytest tests/sprint/test_process.py -v`

**Acceptance Criteria**:
1. `build_command()` output contains `--print`, `--no-session-persistence`, `--max-turns`, `--output-format text`
2. `build_env()` output contains `CLAUDECODE=""` key
3. Timeout calculated as `max_turns * 120 + 300` seconds
4. `build_prompt()` output contains `/sc:task-unified`

**Validation**:
1. `uv run pytest tests/sprint/test_process.py -v` → all tests pass
2. Test count ≥ 4 (command + env + timeout + prompt)

**Dependencies**: T02.05 (ClaudeProcess), T02.06 (SignalHandler)
**Rollback**: Delete test file
**Notes**: Test command construction only — no real subprocess spawning.

---

### T06.04 — Write test_tui.py

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-037 |
| **Why** | Snapshot tests for all TUI states ensure visual correctness across RUNNING, COMPLETE, HALTED, and STALLED states |
| **Effort** | S (4 state variants rendered to StringIO) |
| **Risk** | Low (StringIO rendering is deterministic) |
| **Risk Drivers** | Snapshot stability across Rich versions; terminal width assumptions |
| **Tier** | STANDARD — keyword: create, test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [█████████-] 90% — StringIO rendering eliminates terminal dependencies |
| **Requires Confirmation** | No |
| **Critical Path Override** | No |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0031 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0031/spec.md`, `TASKLIST_ROOT/artifacts/D-0031/evidence.md` |

**Deliverables**:
- Snapshot tests for RUNNING, COMPLETE, HALTED, STALLED TUI states

**Steps**:
1. `[PLANNING]` Define expected output patterns for each TUI state
2. `[EXECUTION]` Create `tests/sprint/test_tui.py` with Console(file=StringIO()) rendering
3. `[EXECUTION]` Add snapshot tests for RUNNING, COMPLETE, HALTED, STALLED states
4. `[EXECUTION]` Verify key text patterns: "ALL PHASES PASSED", "STALLED", resume command
5. `[VERIFICATION]` Run `uv run pytest tests/sprint/test_tui.py -v`

**Acceptance Criteria**:
1. RUNNING state renders phase table with yellow RUNNING indicator
2. COMPLETE state renders "ALL PHASES PASSED" with duration
3. HALTED state renders failure details and resume command
4. STALLED state renders "STALLED" text (after 60s threshold)

**Validation**:
1. `uv run pytest tests/sprint/test_tui.py -v` → all tests pass
2. Test count ≥ 4 (one per state)

**Dependencies**: T03.04 (TUI terminal states complete)
**Rollback**: Delete test file
**Notes**: Use fixed Console width (e.g., 120 chars) for deterministic snapshots.

---

### T06.05 — Write test_executor.py integration tests

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-038 |
| **Why** | Full integration test of executor with mocked subprocess covering all 4 outcome flows: PASS, HALT, TIMEOUT, INTERRUPTED |
| **Effort** | M (4 outcome flows; mocked subprocess; state verification; result validation) |
| **Risk** | Medium (integration complexity across executor, process, config, models) |
| **Risk Drivers** | Mock subprocess fidelity; outcome flow coverage; SprintResult validation |
| **Tier** | STRICT — keywords: multi-file (tests integration across executor+process+config+models); system-wide testing |
| **Confidence Bar** | [████████--] 85% — mock-based integration has timing sensitivity |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — validates entire backend |
| **Verification Method** | Sub-agent: verify all 4 outcome flows produce correct SprintResult |
| **MCP Requirements** | Sequential (outcome flow analysis) |
| **Fallback Allowed** | No — STRICT tier |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0032 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0032/spec.md`, `TASKLIST_ROOT/artifacts/D-0032/evidence.md` |

**Deliverables**:
- Integration tests: PASS flow, HALT flow (with resume), TIMEOUT flow (exit 124), INTERRUPTED flow

**Steps**:
1. `[PLANNING]` Design mock subprocess behaviors for each outcome: success exit, failure exit, exit 124, signal interrupt
2. `[EXECUTION]` Create `tests/sprint/test_executor.py` with PASS outcome test
3. `[EXECUTION]` Add HALT outcome test: non-zero exit at phase N → remaining phases skipped
4. `[EXECUTION]` Add TIMEOUT outcome test: exit code 124 → TIMEOUT status
5. `[EXECUTION]` Add INTERRUPTED outcome test: SIGINT → INTERRUPTED outcome
6. `[EXECUTION]` Verify SprintResult fields for each outcome: outcome, phase_results, resume_command
7. `[VERIFICATION]` Run `uv run pytest tests/sprint/test_executor.py -v`

**Acceptance Criteria**:
1. PASS flow: all phases succeed → SprintResult.outcome == SUCCESS
2. HALT flow: phase N fails → phases N+1..end skipped; resume_command set
3. TIMEOUT flow: exit 124 → PhaseStatus.TIMEOUT; SprintResult reflects timeout
4. INTERRUPTED flow: SIGINT → SprintResult.outcome == INTERRUPTED

**Validation**:
1. `uv run pytest tests/sprint/test_executor.py -v` → all tests pass
2. Test count ≥ 4 (one per outcome flow)

**Dependencies**: T02.07 (executor), T02.08 (status determination)
**Rollback**: Delete test file
**Notes**: Most comprehensive test file — serves as integration regression suite.

---

### Checkpoint: Phase 6 / Tasks T06.01–T06.05

**Purpose:** Validate test suite complete
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P06-T01-T05.md`
**Verification:**
- All 5 test files created; `uv run pytest tests/sprint/ -v` passes; `make lint` passes
- Full pytest output and lint output captured
**Exit Criteria:**
- All deliverables D-0028 through D-0032 verified
- Full pytest output clean
- Phase 7 unblocked

---

### Checkpoint: End of Phase 6

**Purpose:** Verify test suite and coverage targets
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P06-END.md`
**Verification:**
- All 5 tasks completed; full test suite passes; ≥80% coverage target met
- `uv run pytest --cov` and lint output captured
**Exit Criteria:**
- All deliverables D-0028 through D-0032 verified
- `uv run pytest --cov` clean
- Phase 7 unblocked

---

## Phase 7: Final Validation & Acceptance

**Milestone**: M7 | **Priority**: P3 | **Effort**: S | **Dependencies**: M4, M6
**Roadmap Items**: R-039 through R-042

---

### T07.01 — E2E test: 3-phase sprint to completion

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-040 |
| **Why** | End-to-end validation: mock Claude subprocess executes a full 3-phase sprint; verifies execution log, JSONL events, and Markdown table |
| **Effort** | M (full E2E orchestration with mock subprocess; log verification) |
| **Risk** | Medium (E2E complexity; subprocess timing; log format verification) |
| **Risk Drivers** | Mock subprocess behavior fidelity; JSONL event completeness; Markdown table correctness |
| **Tier** | STANDARD — keyword: test, create; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [████████--] 85% — mocked subprocess eliminates real-process flakiness |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — final acceptance gate |
| **Verification Method** | Direct test: pytest execution + log artifact inspection |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0033 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0033/spec.md`, `TASKLIST_ROOT/artifacts/D-0033/evidence.md` |

**Deliverables**:
- E2E test: 3 phases all PASS; execution log with JSONL events and Markdown table; final outcome SUCCESS

**Steps**:
1. `[PLANNING]` Design E2E test: create 3 phase files, mock Claude subprocess with PASS outcomes, verify full execution
2. `[EXECUTION]` Create `tests/sprint/test_e2e_success.py` with full sprint execution
3. `[EXECUTION]` Verify execution log: JSONL events for each phase + summary event
4. `[EXECUTION]` Verify Markdown table: 3 rows with PASS status
5. `[EXECUTION]` Assert SprintResult.outcome == SUCCESS with correct duration
6. `[VERIFICATION]` Run test and inspect generated log artifacts

**Acceptance Criteria**:
1. All 3 phases execute with PASS status
2. Execution log contains JSONL events for each phase completion
3. Markdown table shows 3 phase rows with PASS status
4. Final SprintResult.outcome == SprintOutcome.SUCCESS

**Validation**:
1. `uv run pytest tests/sprint/test_e2e_success.py -v` → passes
2. Generated JSONL log file is valid (each line parseable by json.loads)

**Dependencies**: T06.05 (test_executor.py passes)
**Rollback**: Delete test file
**Notes**: Use `tmp_path` for all generated artifacts; clean up after test.

---

### T07.02 — E2E test: failure at phase 2 with resume

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-041 |
| **Why** | Validates failure handling end-to-end: phase 2 fails, phases 3+ not executed, resume command in log, TUI shows halted state |
| **Effort** | S (failure scenario E2E with resume verification) |
| **Risk** | Medium (failure propagation through full stack) |
| **Risk Drivers** | Failure propagation correctness; resume command accuracy; phase skip verification |
| **Tier** | STANDARD — keyword: test, create; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [█████████-] 90% — failure behavior already validated in T04.02 |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — failure path acceptance |
| **Verification Method** | Direct test: pytest execution |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0034 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0034/spec.md`, `TASKLIST_ROOT/artifacts/D-0034/evidence.md` |

**Deliverables**:
- E2E test: phase 2 HALT; phases 3+ not executed; resume command in log; TUI halted state

**Steps**:
1. `[PLANNING]` Design E2E failure test: 3 phases, phase 2 mock returns non-zero exit
2. `[EXECUTION]` Create `tests/sprint/test_e2e_halt.py` with failure at phase 2
3. `[EXECUTION]` Assert phases 3+ not executed (no JSONL events for phase 3)
4. `[EXECUTION]` Verify resume command in execution log summary
5. `[VERIFICATION]` Run test and verify halt behavior end-to-end

**Acceptance Criteria**:
1. Phase 2 produces HALT status
2. Phases 3+ are not executed (skipped)
3. Resume command appears in execution log summary
4. TUI shows halted state with failure details

**Validation**:
1. `uv run pytest tests/sprint/test_e2e_halt.py -v` → passes
2. Assert no phase 3 events in JSONL log

**Dependencies**: T06.05 (test_executor.py passes)
**Rollback**: Delete test file
**Notes**: Resume command format: `superclaude sprint run --start-phase N` where N = failed_phase.

---

### T07.03 — CLI contract validation for all subcommands

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | R-042 |
| **Why** | Final contract validation: all 5 subcommands (run, attach, status, logs, kill) match documented help text and option signatures from spec Section 3.3 |
| **Effort** | S (5 subcommand --help outputs compared to spec) |
| **Risk** | Low (--help output is deterministic) |
| **Risk Drivers** | Spec Section 3.3 completeness; option naming accuracy |
| **Tier** | STANDARD — keyword: check, test; context booster: test files (+0.2 STANDARD) |
| **Confidence Bar** | [█████████-] 90% — deterministic --help output comparison |
| **Requires Confirmation** | No |
| **Critical Path Override** | Yes — final acceptance |
| **Verification Method** | Direct test: CLI --help output comparison |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | D-0035 |
| **Artifacts (Intended Paths)** | `TASKLIST_ROOT/artifacts/D-0035/spec.md`, `TASKLIST_ROOT/artifacts/D-0035/evidence.md` |

**Deliverables**:
- CLI contract test: all 5 subcommands' --help output matches spec Section 3.3

**Steps**:
1. `[PLANNING]` Extract expected option names and types from spec Section 3.3 for each subcommand
2. `[EXECUTION]` Create `tests/sprint/test_cli_contract.py` with Click CliRunner
3. `[EXECUTION]` Test each subcommand: `run`, `attach`, `status`, `logs`, `kill` — verify --help output contains expected options
4. `[VERIFICATION]` Run test and compare to spec

**Acceptance Criteria**:
1. `superclaude sprint run --help` output contains all documented options
2. `superclaude sprint attach --help` output matches spec
3. `superclaude sprint status --help`, `logs --help`, `kill --help` all match spec
4. All 5 subcommands exit cleanly with `--help` flag

**Validation**:
1. `uv run pytest tests/sprint/test_cli_contract.py -v` → all 5 tests pass
2. Each subcommand --help exits with code 0

**Dependencies**: T02.01 (commands.py)
**Rollback**: Delete test file
**Notes**: Use Click's `CliRunner` for programmatic --help invocation.

---

### Checkpoint: End of Phase 7

**Purpose:** Final acceptance gate
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P07-END.md`
**Verification:**
- All 3 E2E/contract tests pass; full suite passes; SC-001 through SC-008 validated
- Full pytest output and lint output captured
**Exit Criteria:**
- All deliverables D-0033 through D-0035 verified
- All success criteria met
- Sprint complete

---

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01, T01.02, T01.03, T01.04 | D-0001, D-0002, D-0003, D-0004 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0001/` through `D-0004/` |
| R-002 | T01.01 | D-0001 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0001/` |
| R-003 | T01.02 | D-0002 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0002/` |
| R-004 | T01.03 | D-0003 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0003/` |
| R-005 | T01.04 | D-0004 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0004/` |
| R-006 | T02.01–T02.08 | D-0005–D-0012 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0005/` through `D-0012/` |
| R-007 | T02.01 | D-0005 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0005/` |
| R-008 | T02.02 | D-0006 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0006/` |
| R-009 | T02.03 | D-0007 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0007/` |
| R-010 | T02.04 | D-0008 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0008/` |
| R-011 | T02.05 | D-0009 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0009/` |
| R-012 | T02.06 | D-0010 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0010/` |
| R-013 | T02.07 | D-0011 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0011/` |
| R-014 | T02.08 | D-0012 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0012/` |
| R-015 | T03.01–T03.06 | D-0013–D-0018 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0013/` through `D-0018/` |
| R-016 | T03.01 | D-0013 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0013/` |
| R-017 | T03.02 | D-0014 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0014/` |
| R-018 | T03.03 | D-0015 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0015/` |
| R-019 | T03.04 | D-0016 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0016/` |
| R-020 | T03.05 | D-0017 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0017/` |
| R-021 | T03.06 | D-0018 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0018/` |
| R-022 | T04.01, T04.02, T04.03 | D-0019, D-0020, D-0021 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0019/` through `D-0021/` |
| R-023 | T04.01 | D-0019 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0019/` |
| R-024 | T04.02 | D-0020 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0020/` |
| R-025 | T04.03 | D-0021 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0021/` |
| R-026 | T05.01–T05.06 | D-0022–D-0027 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0022/` through `D-0027/` |
| R-027 | T05.01 | D-0022 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0022/` |
| R-028 | T05.02 | D-0023 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0023/` |
| R-029 | T05.03 | D-0024 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0024/` |
| R-030 | T05.04 | D-0025 | STRICT | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0025/` |
| R-031 | T05.05 | D-0026 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0026/` |
| R-032 | T05.06 | D-0027 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0027/` |
| R-033 | T06.01–T06.05 | D-0028–D-0032 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0028/` through `D-0032/` |
| R-034 | T06.01 | D-0028 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0028/` |
| R-035 | T06.02 | D-0029 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0029/` |
| R-036 | T06.03 | D-0030 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0030/` |
| R-037 | T06.04 | D-0031 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0031/` |
| R-038 | T06.05 | D-0032 | STRICT | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0032/` |
| R-039 | T07.01, T07.02, T07.03 | D-0033, D-0034, D-0035 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0033/` through `D-0035/` |
| R-040 | T07.01 | D-0033 | STANDARD | [████████--] 85% | `TASKLIST_ROOT/artifacts/D-0033/` |
| R-041 | T07.02 | D-0034 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0034/` |
| R-042 | T07.03 | D-0035 | STANDARD | [█████████-] 90% | `TASKLIST_ROOT/artifacts/D-0035/` |

**Coverage**: 42/42 roadmap items mapped (100%). 35/35 deliverables mapped (100%). 0 gaps.

---

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| 2026-MM-DDTHH:MM:SSZ | T01.01 | STRICT | D-0001 | Started models.py implementation | Manual | TBD | `TASKLIST_ROOT/evidence/T01.01/` |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

## Checkpoint Report Template

```markdown
# Checkpoint Report — C{PP}.{NN}

**Phase**: {N}
**Checkpoint Type**: {Mid-phase | End-of-phase}
**Date**: YYYY-MM-DD
**Tasks Covered**: {task list}

## Gate Conditions

| Condition | Status | Evidence |
|---|---|---|
| All tasks completed | ☐ PASS / ☐ FAIL | Task status in execution log |
| Deliverables verified | ☐ PASS / ☐ FAIL | Artifact paths confirmed |
| Quality gates pass | ☐ PASS / ☐ FAIL | lint + pytest output |
| No blocked tasks | ☐ PASS / ☐ FAIL | Blocked tasks table empty |

## Deliverable Verification

| Deliverable ID | Artifact Path | Exists | Valid |
|---|---|---|---|
| D{M}.{N} | {path} | ☐ Yes / ☐ No | ☐ Yes / ☐ No |

## Quality Metrics

| Metric | Target | Actual | Status |
|---|---|---|---|
| Test pass rate | 100% | — | — |
| Lint errors | 0 | — | — |
| Coverage (if applicable) | ≥80% | — | — |

## Issues & Risks

| Issue | Severity | Resolution | Impact on Schedule |
|---|---|---|---|
| — | — | — | — |

## Decision

- ☐ **PASS**: Proceed to next phase
- ☐ **FAIL**: Rework required (list tasks)
- ☐ **CONDITIONAL PASS**: Proceed with noted caveats

**Reviewer Notes**: —
```

---

## Feedback Collection Template

**Intended Path:** `TASKLIST_ROOT/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤ 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| T01.01 | STRICT | | | | | |
| T01.02 | STANDARD | | | | | |
| ... | ... | | | | | |

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification (e.g., "Involved auth paths", "Actually trivial")
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`
