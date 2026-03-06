---
roadmap_source: .dev/releases/current/v2.03-CLI-Sprint-diag/roadmap.md
extraction_source: .dev/releases/current/v2.03-CLI-Sprint-diag/extraction.md
generated: 2026-03-04T19:00:00Z
generator: sc:tasklist v2.2
tasklist_root: .dev/releases/current/v2.03-CLI-Sprint-diag/
total_tasks: 34
total_phases: 7
total_deliverables: 34
estimated_effort: M
complexity_class: MEDIUM
primary_persona: backend
consulting_personas: [analyzer, qa]
validation_status: PASS
---

# Tasklist: Sprint CLI Diagnostic Testing Framework v1.0

## Source Snapshot

| Field | Value |
|-------|-------|
| Spec | `spec-sprint-diagnostic-framework.md` |
| Roadmap | `roadmap.md` (7 milestones, 34 deliverables) |
| Extraction | `extraction.md` (41 FRs, 7 NFRs, 48 total) |
| Complexity | 0.68 (MEDIUM) |
| Domain Split | backend 78%, performance 10%, security 7%, documentation 5% |
| Risk Count | 8 risks (0 High probability, 5 Medium, 3 Low) |
| Dependency Count | 12 (4 external, 8 internal) |

---

## Deterministic Rules Applied

### Effort Scoring
```
EFFORT_SCORE: +1 if text >= 120 chars, +1 if split task, +1 if has dependency words,
              +1 if has technical keywords (migration, auth, db, cache, deploy, etc.)
Mapping: 0 -> XS, 1 -> S, 2 -> M, 3 -> L, 4+ -> XL
```

### Risk Scoring
```
RISK_SCORE: +2 for security/vulnerability/compliance words,
            +2 for migration/data/schema words,
            +1 for auth/permissions, +1 for performance/latency,
            +1 for cross-cutting scope
Mapping: 0-1 -> Low, 2-3 -> Medium, 4+ -> High
```

### Tier Classification
```
Priority: STRICT > EXEMPT > LIGHT > STANDARD
STRICT keywords: authentication, security, database, migration, schema, model, refactor, multi-file, system-wide, breaking change
STANDARD keywords: implement, add, create, update, fix, build, modify
LIGHT keywords: typo, comment, rename, lint, style, minor
EXEMPT keywords: explain, review, check, plan, design, evaluate
Context boosters: >2 files -> +0.3 STRICT; tests/ path -> +0.2 STANDARD
```

### Task ID Format
```
T<PP>.<TT> where PP = zero-padded phase, TT = zero-padded task number within phase
```

### Deliverable ID Format
```
D-0001, D-0002, ... sequential in task order across all phases
```

---

## Roadmap Item Registry

| Roadmap ID | Title | Type | Priority | Deliverable Count | Risk | Phase |
|------------|-------|------|----------|-------------------|------|-------|
| M1 | Foundation -- Debug Logger Module | FEATURE | P0 | 5 | Low | 1 |
| M2 | Debug Instrumentation -- Event Coverage | FEATURE | P0 | 6 | Medium | 2 |
| M3 | Watchdog Mechanism | FEATURE | P0 | 4 | Medium | 3 |
| M4 | Validation Checkpoint 1 | TEST | P2 | 3 | Low | 4 |
| M5 | Diagnostics & Failure Classification | FEATURE | P0 | 5 | Medium | 5 |
| M6 | Test Infrastructure & Graduated Tests | TEST | P1 | 7 | Medium | 6 |
| M7 | Integration Validation & Acceptance | TEST | P1 | 4 | Low | 7 |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item | Description |
|----------------|---------|--------------|-------------|
| D-0001 | T01.01 | M1 / D1.1 | `_FlushHandler` class extending `logging.FileHandler` |
| D-0002 | T01.02 | M1 / D1.2 | `_DebugFormatter` class |
| D-0003 | T01.03 | M1 / D1.3 | `setup_debug_logger(config)` function |
| D-0004 | T01.04 | M1 / D1.4 | `debug_log()` helper function |
| D-0005 | T01.05 | M1 / D1.5 | `SprintConfig` model additions |
| D-0006 | T02.01 | M2 / D2.1 | `executor.py` instrumentation |
| D-0007 | T02.02 | M2 / D2.2 | `process.py` instrumentation |
| D-0008 | T02.03 | M2 / D2.3 | `monitor.py` instrumentation |
| D-0009 | T02.04 | M2 / D2.4 | `tui.py` instrumentation |
| D-0010 | T02.05 | M2 / D2.5 | `tmux.py` flag forwarding |
| D-0011 | T02.06 | M2 / D2.6 | `commands.py` CLI options |
| D-0012 | T03.01 | M3 / D3.1 | Stall timeout check in executor poll loop |
| D-0013 | T03.02 | M3 / D3.2 | `warn` action implementation |
| D-0014 | T03.03 | M3 / D3.3 | `kill` action implementation |
| D-0015 | T03.04 | M3 / D3.4 | Single-fire guard |
| D-0016 | T04.01 | M4 / D4.1 | Debug log format validation |
| D-0017 | T04.02 | M4 / D4.2 | Watchdog validation |
| D-0018 | T04.03 | M4 / D4.3 | Backward compatibility validation |
| D-0019 | T05.01 | M5 / D5.1 | `DiagnosticBundle` dataclass |
| D-0020 | T05.02 | M5 / D5.2 | `DiagnosticCollector.collect()` |
| D-0021 | T05.03 | M5 / D5.3 | `FailureClassifier.classify()` |
| D-0022 | T05.04 | M5 / D5.4 | `ReportGenerator.generate()` + `.write()` |
| D-0023 | T05.05 | M5 / D5.5 | Executor integration |
| D-0024 | T06.01 | M6 / D6.1 | `DiagnosticTestHarness` class |
| D-0025 | T06.02 | M6 / D6.2 | `DebugLogReader` integration in test fixtures |
| D-0026 | T06.03 | M6 / D6.3 | `tests/sprint/diagnostic/conftest.py` |
| D-0027 | T06.04 | M6 / D6.4 | `test_level_0.py` -- Pipeline smoke tests |
| D-0028 | T06.05 | M6 / D6.5 | `test_level_1.py` through `test_level_3.py` |
| D-0029 | T06.06 | M6 / D6.6 | `test_negative.py` -- 6 failure mode tests |
| D-0030 | T06.07 | M6 / D6.7 | Pytest markers |
| D-0031 | T07.01 | M7 / D7.1 | User story validation |
| D-0032 | T07.02 | M7 / D7.2 | Full test suite pass |
| D-0033 | T07.03 | M7 / D7.3 | Backward compatibility final check |
| D-0034 | T07.04 | M7 / D7.4 | File inventory verification |

---

## Tasklist Index

| Task ID | Title | Phase | Effort | Risk | Tier | Status |
|---------|-------|-------|--------|------|------|--------|
| T01.01 | Implement `_FlushHandler` class | 1 | S | Low | STANDARD | pending |
| T01.02 | Implement `_DebugFormatter` class | 1 | XS | Low | STANDARD | pending |
| T01.03 | Implement `setup_debug_logger(config)` function | 1 | S | Low | STANDARD | pending |
| T01.04 | Implement `debug_log()` helper function | 1 | S | Low | STANDARD | pending |
| T01.05 | Add diagnostic fields to `SprintConfig` model | 1 | M | Low | STRICT | pending |
| T02.01 | Instrument `executor.py` with debug events | 2 | M | Medium | STANDARD | pending |
| T02.02 | Instrument `process.py` with debug events | 2 | M | Low | STANDARD | pending |
| T02.03 | Instrument `monitor.py` with debug events | 2 | S | Low | STANDARD | pending |
| T02.04 | Instrument `tui.py` with debug events | 2 | S | Low | STANDARD | pending |
| T02.05 | Implement `tmux.py` flag forwarding | 2 | S | Low | STANDARD | pending |
| T02.06 | Add CLI options to `commands.py` | 2 | S | Low | STANDARD | pending |
| T03.01 | Implement stall timeout check in executor poll loop | 3 | M | Medium | STANDARD | pending |
| T03.02 | Implement `warn` stall action | 3 | S | Low | STANDARD | pending |
| T03.03 | Implement `kill` stall action | 3 | M | Medium | STANDARD | pending |
| T03.04 | Implement single-fire guard for watchdog | 3 | S | Low | STANDARD | pending |
| T04.01 | Validate debug log format | 4 | S | Low | EXEMPT | pending |
| T04.02 | Validate watchdog behavior | 4 | S | Low | EXEMPT | pending |
| T04.03 | Validate backward compatibility | 4 | S | Low | EXEMPT | pending |
| T05.01 | Implement `DiagnosticBundle` dataclass | 5 | M | Low | STANDARD | pending |
| T05.02 | Implement `DiagnosticCollector.collect()` | 5 | M | Medium | STANDARD | pending |
| T05.03 | Implement `FailureClassifier.classify()` | 5 | M | Medium | STANDARD | pending |
| T05.04 | Implement `ReportGenerator.generate()` and `.write()` | 5 | M | Low | STANDARD | pending |
| T05.05 | Integrate diagnostics into executor failure path | 5 | M | Low | STRICT | pending |
| T06.01 | Implement `DiagnosticTestHarness` class | 6 | L | Medium | STANDARD | pending |
| T06.02 | Implement `DebugLogReader` and test fixtures | 6 | M | Low | STANDARD | pending |
| T06.03 | Create `tests/sprint/diagnostic/conftest.py` | 6 | M | Low | STANDARD | pending |
| T06.04 | Implement `test_level_0.py` pipeline smoke tests | 6 | M | Low | STANDARD | pending |
| T06.05 | Implement `test_level_1.py` through `test_level_3.py` | 6 | L | Medium | STANDARD | pending |
| T06.06 | Implement `test_negative.py` failure mode tests | 6 | L | Medium | STANDARD | pending |
| T06.07 | Add pytest diagnostic markers | 6 | XS | Low | LIGHT | pending |
| T07.01 | Validate user stories US1-US5 | 7 | S | Low | EXEMPT | pending |
| T07.02 | Run full test suite and verify all pass | 7 | S | Low | EXEMPT | pending |
| T07.03 | Perform backward compatibility final check | 7 | S | Low | EXEMPT | pending |
| T07.04 | Verify file inventory against spec | 7 | XS | Low | EXEMPT | pending |

---

## Phase 1: Foundation -- Debug Logger Module

**Roadmap Item**: M1
**Priority**: P0
**Phase Risk**: Low
**Phase Dependencies**: None (foundation)
**Phase Summary**: Create `debug_logger.py` module with crash-safe file handler, structured formatter, reader class, and `SprintConfig` model additions. Establishes the logging contract all other phases depend on.

---

### T01.01 -- Implement `_FlushHandler` class

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M1 |
| Why | Crash-safe logging requires every emit to flush to disk immediately. Without this, debug log entries are lost on stall or crash, defeating the purpose of diagnostic instrumentation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None significant -- standard Python logging extension |
| Tier | STANDARD |
| Confidence | 0.95 |
| Verification Method | Unit test: write log entry, simulate crash, verify entry on disk |
| MCP Requirements | None |
| Deliverable IDs | D-0001 |

**Deliverables**:
- `src/superclaude/cli/sprint/debug_logger.py` containing `_FlushHandler(logging.FileHandler)` class

**Steps**:
1. [PLAN] Review Python `logging.FileHandler` API and `emit()`/`flush()` contract
2. [IMPL] Create `src/superclaude/cli/sprint/debug_logger.py` with `_FlushHandler` class that overrides `emit()` to call `self.flush()` after `super().emit(record)`
3. [IMPL] Add error handling in `emit()` to catch and suppress I/O errors gracefully
4. [TEST] Write unit test that logs an entry, confirms it is on disk immediately without explicit flush
5. [VERIFY] Confirm crash-safe behavior: log entry, kill process, verify entry persisted

**Acceptance Criteria**:
1. `_FlushHandler` extends `logging.FileHandler` and overrides `emit()`
2. Every call to `emit()` results in data flushed to disk before returning
3. I/O errors in `emit()` do not propagate exceptions to callers
4. Unit test demonstrates crash-safe write behavior

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "flush_handler" -v` passes
2. Manual verification: write log + kill process + check file shows entry

**Dependencies**: None
**Rollback**: Delete `debug_logger.py` -- no other code depends on it yet
**Notes**: FR-004 (line-buffered writes). This is the foundation class for all debug logging.

---

### T01.02 -- Implement `_DebugFormatter` class

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M1 |
| Why | Structured log format enables programmatic parsing by `DebugLogReader` (M6) and human readability. ISO8601 timestamps with milliseconds are required for precise timing analysis of stalls. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None -- standard formatter implementation |
| Tier | STANDARD |
| Confidence | 0.95 |
| Verification Method | Unit test: format a record, assert output matches spec pattern |
| MCP Requirements | None |
| Deliverable IDs | D-0002 |

**Deliverables**:
- `_DebugFormatter` class in `debug_logger.py` producing `timestamp LEVEL [component] message` format

**Steps**:
1. [PLAN] Define the exact format string: `{iso8601_ms} {LEVEL} [{component}] {message}`
2. [IMPL] Create `_DebugFormatter(logging.Formatter)` with `format()` override
3. [IMPL] Extract `component` from logger name or record extras
4. [TEST] Assert formatted output matches `2026-03-04T19:00:00.123 DEBUG [executor] poll_tick pid=1234`

**Acceptance Criteria**:
1. Format output matches `timestamp LEVEL [component] message` pattern
2. Timestamps are ISO8601 with milliseconds precision
3. Component name is extracted from log record
4. Level name is uppercase and padded consistently

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "debug_formatter" -v` passes
2. Visual inspection of formatted output against spec examples

**Dependencies**: None
**Rollback**: Remove class from `debug_logger.py`
**Notes**: FR-003 specifies log format version header; this formatter handles per-line format. Version header is written by `setup_debug_logger()` (T01.03).

---

### T01.03 -- Implement `setup_debug_logger(config)` function

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M1 |
| Why | Central factory function creates the correctly configured logger instance. Must handle both enabled (FileHandler + FlushHandler + formatter) and disabled (NullHandler, zero overhead) paths. |
| Effort | S |
| Risk | Low |
| Risk Drivers | Logger naming conflicts with existing loggers (R-001 mitigated by unique name + propagate=False) |
| Tier | STANDARD |
| Confidence | 0.92 |
| Verification Method | Unit test: verify logger config for both enabled and disabled paths |
| MCP Requirements | None |
| Deliverable IDs | D-0003 |

**Deliverables**:
- `setup_debug_logger(config)` function in `debug_logger.py`

**Steps**:
1. [PLAN] Define function signature: accepts `SprintConfig`, returns `logging.Logger`
2. [IMPL] Create logger named `superclaude.sprint.debug` with `propagate=False`
3. [IMPL] When `config.debug=True`: attach `_FlushHandler` with `_DebugFormatter`, write version header `# debug-log-version: 1.0`, set DEBUG level
4. [IMPL] When `config.debug=False`: attach `NullHandler` only
5. [TEST] Verify enabled path creates file with version header; disabled path creates no file and has NullHandler

**Acceptance Criteria**:
1. Returns `logging.Logger` named `superclaude.sprint.debug`
2. Logger has `propagate=False` to prevent parent logger interference
3. When enabled: writes version header as first line, attaches `_FlushHandler` with `_DebugFormatter`
4. When disabled: attaches `NullHandler` only, zero file I/O

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "setup_debug_logger" -v` passes
2. Verify `debug.log` file starts with `# debug-log-version: 1.0` when enabled

**Dependencies**: T01.01 (`_FlushHandler`), T01.02 (`_DebugFormatter`)
**Rollback**: Remove function from `debug_logger.py`
**Notes**: FR-002, FR-003, FR-018, FR-021. The logger name is unique to avoid conflicts (R-001 mitigation).

---

### T01.04 -- Implement `debug_log()` helper function

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M1 |
| Why | Convenience helper provides consistent structured event format across all components. The no-op check when disabled ensures zero overhead in production mode. |
| Effort | S |
| Risk | Low |
| Risk Drivers | Performance overhead if no-op check is inefficient |
| Tier | STANDARD |
| Confidence | 0.95 |
| Verification Method | Unit test: verify structured output format and no-op behavior |
| MCP Requirements | None |
| Deliverable IDs | D-0004 |

**Deliverables**:
- `debug_log()` helper function in `debug_logger.py`

**Steps**:
1. [PLAN] Define function signature: `debug_log(logger, event, **kwargs)` producing `event k1=v1 k2=v2`
2. [IMPL] Implement with early return when logger has no effective handlers (no-op path)
3. [IMPL] Format kwargs into `key=value` pairs with consistent ordering
4. [TEST] Verify output format matches `poll_tick pid=1234 elapsed=5.2`
5. [TEST] Verify no-op path has negligible overhead (< 1 microsecond)

**Acceptance Criteria**:
1. Emits structured entries in format `event k1=v1 k2=v2`
2. No-op when logger is disabled (NullHandler) with zero overhead
3. Handles all Python value types in kwargs (int, float, str, None)
4. Key-value pairs are consistently ordered for deterministic output

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "debug_log" -v` passes
2. Performance benchmark: disabled path completes in < 1 microsecond per call

**Dependencies**: T01.03 (`setup_debug_logger`)
**Rollback**: Remove function from `debug_logger.py`
**Notes**: FR-005 (existing logs unchanged). This helper is the primary interface used by all instrumented components (M2).

---

### T01.05 -- Add diagnostic fields to `SprintConfig` model

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M1 |
| Why | `SprintConfig` is the single source of truth for sprint configuration. New fields with backward-compatible defaults ensure existing behavior is preserved while enabling diagnostic capabilities. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Model change affects all consumers; backward compatibility is critical (NFR-007) |
| Tier | STRICT |
| Confidence | 0.90 |
| Verification Method | Unit test: verify defaults match pre-change behavior; existing tests pass |
| MCP Requirements | None |
| Deliverable IDs | D-0005 |

**Deliverables**:
- 4 new fields on `SprintConfig`: `debug`, `stall_timeout`, `stall_action`, `phase_timeout`
- 1 new property: `debug_log_path`
- All with backward-compatible defaults

**Steps**:
1. [PLAN] Review current `SprintConfig` in `src/superclaude/cli/sprint/models.py` for field patterns and conventions
2. [IMPL] Add `debug: bool = False` field
3. [IMPL] Add `stall_timeout: int = 0` field (0 = disabled, per spec default)
4. [IMPL] Add `stall_action: str = "warn"` field (enum: warn, kill)
5. [IMPL] Add `phase_timeout: int = 0` field
6. [IMPL] Add `debug_log_path` property that computes path from results directory
7. [TEST] Verify all existing `SprintConfig` tests pass without modification
8. [TEST] Verify new fields default to values that preserve pre-change behavior

**Acceptance Criteria**:
1. All 4 new fields have defaults matching current behavior (debug=False, stall_timeout=0, stall_action="warn", phase_timeout=0)
2. `debug_log_path` property returns correct path relative to results directory
3. Existing `SprintConfig` instantiation without new args produces identical behavior
4. All existing tests in `tests/sprint/test_config.py` pass without modification

**Validation**:
1. `uv run pytest tests/sprint/test_config.py -v` passes (existing tests)
2. `uv run pytest tests/sprint/diagnostic/ -k "sprint_config" -v` passes (new tests)

**Dependencies**: None (modifies existing model)
**Rollback**: Revert changes to `models.py` -- git diff shows exact lines to restore
**Notes**: FR-001, FR-014, FR-015, NFR-007. This is STRICT tier because it modifies a model used across the system. The backward-compatible defaults are the primary safety mechanism.

---

### CHECKPOINT CP-01 (after T01.05)

**Phase 1 Completion Check**:
- [ ] All 5 tasks (T01.01-T01.05) completed
- [ ] `debug_logger.py` module exists with `_FlushHandler`, `_DebugFormatter`, `setup_debug_logger()`, `debug_log()`
- [ ] `SprintConfig` has 4 new fields + 1 property with backward-compatible defaults
- [ ] `uv run pytest tests/sprint/test_config.py -v` passes (backward compat)
- [ ] No regressions in existing test suite

**Gate Criteria**: All 5 deliverables (D-0001 through D-0005) verified before proceeding to Phase 2/3.

---

## Phase 2: Debug Instrumentation -- Event Coverage

**Roadmap Item**: M2
**Priority**: P0
**Phase Risk**: Medium
**Phase Dependencies**: Phase 1 (M1 complete)
**Phase Summary**: Inject the debug logger into all 6 sprint components and emit structured events for every state transition. Modifies 6 existing files.

---

### T02.01 -- Instrument `executor.py` with debug events

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M2 |
| Why | The executor poll loop is where stalls manifest. PHASE_BEGIN/END markers and 0.5s poll_tick events provide the primary diagnostic data for stall analysis. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Poll tick logging at 0.5s may generate excessive I/O (R-001); phase correlation markers must bracket all per-phase events correctly |
| Tier | STANDARD |
| Confidence | 0.88 |
| Verification Method | Unit test: mock logger, verify events emitted in correct order with correct fields |
| MCP Requirements | None |
| Deliverable IDs | D-0006 |

**Deliverables**:
- `executor.py` modified with `PHASE_BEGIN`, `poll_tick`, `phase_complete`, `PHASE_END` events

**Steps**:
1. [PLAN] Map all executor state transitions to debug events per FR-007, FR-008, FR-020
2. [IMPL] Add logger parameter to `execute_sprint()` function signature
3. [IMPL] Emit `PHASE_BEGIN` with phase number and file at start of each phase
4. [IMPL] Emit `poll_tick` every 0.5s with: phase, PID, poll_result, elapsed, output_bytes, growth_rate, stall_seconds, stall_status
5. [IMPL] Emit `phase_complete` and `PHASE_END` with status, exit_code, duration
6. [TEST] Verify event sequence: PHASE_BEGIN -> poll_tick(s) -> phase_complete -> PHASE_END

**Acceptance Criteria**:
1. `PHASE_BEGIN` event emitted at start of each phase with phase number and file
2. `poll_tick` events emitted every 0.5s with all 8 required fields
3. `PHASE_END` event emitted at end of each phase with status, exit_code, duration
4. Phase correlation: all events between PHASE_BEGIN and PHASE_END share the same phase identifier

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "executor_instrumentation" -v` passes
2. Manual: run `sprint run --debug` and verify debug.log contains expected event sequence

**Dependencies**: T01.03 (`setup_debug_logger`), T01.04 (`debug_log`)
**Rollback**: Revert `executor.py` changes via git
**Notes**: FR-007, FR-008, FR-020. Poll tick logging is DEBUG level only -- NullHandler when disabled ensures zero overhead (FR-021).

---

### T02.02 -- Instrument `process.py` with debug events

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M2 |
| Why | Process lifecycle events (spawn, signal, exit) are critical for diagnosing subprocess failures. PID, command array, and env delta provide the necessary context. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None significant -- straightforward event injection |
| Tier | STANDARD |
| Confidence | 0.92 |
| Verification Method | Unit test: mock logger, verify spawn/exit events with correct fields |
| MCP Requirements | None |
| Deliverable IDs | D-0007 |

**Deliverables**:
- `process.py` modified with `spawn`, `files_opened`, `signal_sent`, `exit` events

**Steps**:
1. [PLAN] Map `ClaudeProcess` lifecycle to debug events per FR-009, FR-010
2. [IMPL] Add logger parameter to `ClaudeProcess` constructor or inject via method
3. [IMPL] Emit `spawn` event with PID, command array, env delta on process start
4. [IMPL] Emit `files_opened` event with stdout/stderr file paths
5. [IMPL] Emit `signal_sent` event on any signal delivery
6. [IMPL] Emit `exit` event with code and was_timeout flag on process termination
7. [TEST] Verify all 4 event types emitted with correct fields

**Acceptance Criteria**:
1. `spawn` event includes PID, command array, and env delta
2. `files_opened` event includes stdout and stderr file paths
3. `signal_sent` event emitted on every signal delivery with signal name
4. `exit` event includes exit code and was_timeout boolean

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "process_instrumentation" -v` passes
2. Manual: run `sprint run --debug` and verify spawn/exit events in debug.log

**Dependencies**: T01.03 (`setup_debug_logger`), T01.04 (`debug_log`)
**Rollback**: Revert `process.py` changes via git
**Notes**: FR-009, FR-010.

---

### T02.03 -- Instrument `monitor.py` with debug events

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M2 |
| Why | Monitor events track file I/O state that reveals output stalls vs. silent stalls. `output_file_stat` and `signal_extracted` events are inputs to stall classification. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None significant |
| Tier | STANDARD |
| Confidence | 0.93 |
| Verification Method | Unit test: mock logger, verify events emitted on file stat and signal extraction |
| MCP Requirements | None |
| Deliverable IDs | D-0008 |

**Deliverables**:
- `monitor.py` modified with `output_file_stat`, `signal_extracted` events

**Steps**:
1. [PLAN] Map `OutputMonitor` operations to debug events per FR-011. **Note**: the output buffering fix sprint (tasklist-fixes) rewrites `_poll_once()` to parse NDJSON lines and renames `_extract_signals(text)` to `_extract_signals_from_event(event: dict)`. Instrumentation must target the **post-fix** NDJSON API.
2. [IMPL] Add `debug_logger` parameter to `OutputMonitor.__init__()` or inject via method
3. [IMPL] Emit `output_file_stat` event inside `_poll_once()` on file stat checks, including `events_received` count and `last_event_time` from the NDJSON monitor state
4. [IMPL] Emit `signal_extracted` event inside `_extract_signals_from_event(event)` when task IDs or tool names are extracted from NDJSON events
5. [IMPL] Emit `ndjson_line_parsed` event per complete NDJSON line processed (includes event type and parsed status)
6. [TEST] Verify events emitted with correct fields using NDJSON mock data

**Acceptance Criteria**:
1. `output_file_stat` event includes file path, size, `events_received`, and `last_event_time`
2. `signal_extracted` event includes extracted signal type (task_id, tool_name) and source NDJSON event type
3. Events emitted only when debug logger is active (no-op otherwise)
4. Instrumentation targets the NDJSON-aware `_extract_signals_from_event()` method (not the removed text-based `_extract_signals()`)

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "monitor_instrumentation" -v` passes
2. `uv run pytest tests/sprint/test_monitor_stream.py -v` passes (NDJSON tests from buffering fix)

**Dependencies**: T01.03, T01.04
**Rollback**: Revert `monitor.py` changes via git
**Notes**: FR-011. **Prerequisite**: the output buffering fix (tasklist-fixes Phase 1) must be applied first, as it rewrites `_poll_once()` and `_extract_signals()` to NDJSON-based methods.

---

### T02.04 -- Instrument `tui.py` with debug events

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M2 |
| Why | TUI state transitions help diagnose display failures. The `tui_live_failed` event with exception object is particularly important because the TUI currently masks errors silently (R-005). |
| Effort | S |
| Risk | Low |
| Risk Drivers | TUI live_failed mask may hide underlying errors (R-005); debug logging captures the exception |
| Tier | STANDARD |
| Confidence | 0.92 |
| Verification Method | Unit test: mock logger, verify TUI lifecycle events |
| MCP Requirements | None |
| Deliverable IDs | D-0009 |

**Deliverables**:
- `tui.py` modified with `tui_start`, `tui_update`, `tui_live_failed`, `tui_stop` events

**Steps**:
1. [PLAN] Map `SprintTUI` lifecycle to debug events per FR-012. **Note**: the output buffering fix (tasklist-fixes Phase 2) changes the active panel to display `Events: N` instead of `Output size`, adds `"waiting..."` stall state, and uses event-based liveness. Debug events must capture these post-fix display values.
2. [IMPL] Add `debug_logger` parameter to `SprintTUI` constructor
3. [IMPL] Emit `tui_start` on TUI initialization
4. [IMPL] Emit `tui_update` on display refresh cycles, including `events_received`, `stall_status` (which now includes `"waiting..."`, `"active"`, `"thinking..."`, `"STALLED"` states), and `last_event_time`
5. [IMPL] Emit `tui_live_failed` with exception object when live display fails
6. [IMPL] Emit `tui_stop` on TUI teardown
7. [TEST] Verify all 4 event types emitted in correct lifecycle order with event-based fields

**Acceptance Criteria**:
1. `tui_start` emitted on TUI initialization
2. `tui_update` emitted on each display refresh, including `events_received`, `stall_status`, and `last_event_time` fields
3. `tui_live_failed` includes exception type and message
4. `tui_stop` emitted on TUI teardown

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "tui_instrumentation" -v` passes
2. Existing TUI tests pass without modification

**Dependencies**: T01.03, T01.04
**Rollback**: Revert `tui.py` changes via git
**Notes**: FR-012. The `tui_live_failed` event is key to solving root cause 4 from the spec. **Prerequisite**: the output buffering fix (tasklist-fixes Phase 2) changes TUI display to event-based metrics; debug logging should capture these post-fix values.

---

### T02.05 -- Implement `tmux.py` flag forwarding

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M2 |
| Why | When sprint runs in tmux mode, the `--debug`, `--stall-timeout`, and `--stall-action` flags must be forwarded to the foreground command. Without this, tmux sessions lose diagnostic capabilities. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None significant -- extends existing flag forwarding pattern |
| Tier | STANDARD |
| Confidence | 0.93 |
| Verification Method | Unit test: verify `_build_foreground_command()` includes new flags |
| MCP Requirements | None |
| Deliverable IDs | D-0010 |

**Deliverables**:
- `tmux.py` modified to forward `--debug`, `--stall-timeout`, `--stall-action` via `_build_foreground_command()`

**Steps**:
1. [PLAN] Review `_build_foreground_command()` in `tmux.py` for existing flag forwarding pattern
2. [IMPL] Add `--debug` flag forwarding when `config.debug=True`
3. [IMPL] Add `--stall-timeout` forwarding when `config.stall_timeout > 0`
4. [IMPL] Add `--stall-action` forwarding when `config.stall_action != "warn"` (non-default)
5. [TEST] Verify command array includes new flags with correct values

**Acceptance Criteria**:
1. `--debug` flag forwarded when `config.debug=True`
2. `--stall-timeout N` forwarded when stall_timeout is set
3. `--stall-action ACTION` forwarded when non-default
4. Existing tmux command building unchanged when new flags are at defaults

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "tmux_forwarding" -v` passes
2. Existing tmux tests pass without modification

**Dependencies**: T01.05 (`SprintConfig` fields)
**Rollback**: Revert `tmux.py` changes via git
**Notes**: FR-041.

---

### CHECKPOINT CP-02 (after T02.05)

**Progress Check (5 tasks since last checkpoint)**:
- [ ] T02.01-T02.05 completed
- [ ] 5 source files modified: executor.py, process.py, monitor.py, tui.py, tmux.py
- [ ] All debug events emit in correct format via `debug_log()` helper
- [ ] Existing tests for all modified files still pass
- [ ] No regressions detected

---

### T02.06 -- Add CLI options to `commands.py`

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M2 |
| Why | CLI options are the user-facing interface for diagnostic features. Without `--debug`, `--stall-timeout`, and `--stall-action` Click options, users cannot activate the diagnostic framework. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None significant -- extends existing Click option pattern |
| Tier | STANDARD |
| Confidence | 0.94 |
| Verification Method | Unit test: verify Click options parsed correctly and passed to SprintConfig |
| MCP Requirements | None |
| Deliverable IDs | D-0011 |

**Deliverables**:
- `commands.py` modified with 3 new Click options: `--debug`, `--stall-timeout`, `--stall-action`

**Steps**:
1. [PLAN] Review existing Click options in `commands.py` for patterns and conventions
2. [IMPL] Add `@click.option("--debug", is_flag=True, default=False, help="Enable debug logging")`
3. [IMPL] Add `@click.option("--stall-timeout", type=int, default=0, help="Stall timeout in seconds")`
4. [IMPL] Add `@click.option("--stall-action", type=click.Choice(["warn", "kill"]), default="warn", help="Action on stall")`
5. [IMPL] Pass new option values to `SprintConfig` constructor
6. [TEST] Verify CLI parsing for all three options with various inputs

**Acceptance Criteria**:
1. `--debug` is a boolean flag defaulting to False
2. `--stall-timeout` is an integer defaulting to 0
3. `--stall-action` is a choice of ["warn", "kill"] defaulting to "warn"
4. All values correctly passed to `SprintConfig` instance

**Validation**:
1. `uv run pytest tests/sprint/test_cli_contract.py -v` passes (if CLI tests exist)
2. `superclaude sprint run --help` shows all three new options

**Dependencies**: T01.05 (`SprintConfig` fields)
**Rollback**: Revert `commands.py` changes via git
**Notes**: FR-001, FR-014, FR-015.

---

## Phase 3: Watchdog Mechanism

**Roadmap Item**: M3
**Priority**: P0
**Phase Risk**: Medium
**Phase Dependencies**: Phase 1 (M1 complete)
**Phase Summary**: Implement stall detection and response (warn or kill) in the executor poll loop. Works independently of `--debug` flag, solving the core user problem of indefinite stalls.

---

### T03.01 -- Implement stall timeout check in executor poll loop

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M3 |
| Why | This is the core stall detection logic. When `stall_seconds > stall_timeout` and `stall_timeout > 0`, the configured action triggers. This directly solves the primary user problem of indefinite stalling. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Watchdog relies on OutputMonitor growth rate which may have edge cases (R-004); stall_seconds must be monotonically increasing when no growth |
| Tier | STANDARD |
| Confidence | 0.85 |
| Verification Method | Integration test: create stalling subprocess, verify timeout triggers |
| MCP Requirements | Sequential (for complex logic analysis if needed) |
| Deliverable IDs | D-0012 |

**Deliverables**:
- Stall timeout check logic in executor poll loop

**Steps**:
1. [PLAN] Review executor poll loop and stall detection semantics. **Note**: the output buffering fix (tasklist-fixes) changes stall detection from byte-growth-based to event-based liveness. After the fix, `MonitorState.stall_status` returns `"STALLED"` only when NDJSON events stop arriving (genuine stall), not when bytes stop growing (which was a false positive with `--output-format text`). The watchdog should use `state.stall_status == "STALLED"` as its primary trigger, OR use `stall_seconds > stall_timeout` where `stall_seconds` now reflects time since last NDJSON event (not last byte growth).
2. [PLAN] Map stall detection logic: `if config.stall_timeout > 0 and ms.stall_seconds > config.stall_timeout`
3. [IMPL] Add stall timeout check after each poll tick in executor
4. [IMPL] Dispatch to configured stall action (warn or kill) when threshold exceeded
5. [TEST] Verify timeout triggers at correct threshold with mock monitor using event-based stall semantics
6. [TEST] Verify no trigger when stall_timeout=0 (disabled)
7. [TEST] Verify no trigger during startup phase when `stall_status == "waiting..."` (no events received yet, not a genuine stall)

**Acceptance Criteria**:
1. Stall check evaluates `stall_seconds > stall_timeout` when `stall_timeout > 0`, where `stall_seconds` reflects time since last NDJSON event
2. Configured action (warn or kill) dispatched when threshold exceeded
3. No stall detection when `stall_timeout=0` (disabled by default)
4. Watchdog does NOT trigger during startup (`stall_status == "waiting..."` / `events_received == 0`) — only after events have been flowing and then stop

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "stall_timeout" -v` passes
2. Integration test: subprocess that stalls triggers timeout at configured threshold

**Dependencies**: T01.05 (`SprintConfig.stall_timeout`), T02.01 (executor instrumentation)
**Rollback**: Revert executor poll loop changes via git
**Notes**: FR-016, R-004 (risk). Watchdog works independently of `--debug` per R7.1 recommendation. **Prerequisite**: output buffering fix changes stall semantics from byte-growth to event-based liveness; watchdog must use the post-fix `stall_seconds` (time since last NDJSON event).

---

### T03.02 -- Implement `warn` stall action

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M3 |
| Why | The `warn` action logs a WARNING with full process state but continues execution. This is the default action -- it alerts without disrupting the sprint run, giving users visibility without risk. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None significant |
| Tier | STANDARD |
| Confidence | 0.93 |
| Verification Method | Unit test: verify warning logged with process state, execution continues |
| MCP Requirements | None |
| Deliverable IDs | D-0013 |

**Deliverables**:
- `warn` action handler that logs WARNING with process state and continues execution

**Steps**:
1. [IMPL] Create warn action handler that logs WARNING level message
2. [IMPL] Include full process state in warning: PID, stall_seconds, output_bytes, growth_rate
3. [IMPL] Ensure execution continues after warning (no break/return)
4. [TEST] Verify WARNING logged with correct fields; poll loop continues

**Acceptance Criteria**:
1. WARNING level log entry emitted with full process state
2. Execution continues after warning (poll loop not interrupted)
3. Warning includes: PID, stall duration, output size, growth rate
4. Stall counter resets after warning (acts once per stall period)

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "warn_action" -v` passes
2. Manual: run with `--stall-action warn` and verify warning appears in output

**Dependencies**: T03.01 (stall detection)
**Rollback**: Revert warn handler
**Notes**: FR-015 (default action), FR-017 (acts once per stall).

---

### T03.03 -- Implement `kill` stall action

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M3 |
| Why | The `kill` action terminates the stalled subprocess and breaks the poll loop. Uses SIGTERM then SIGKILL escalation for reliable termination. Sets `_timed_out=True` for diagnostic classification. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Signal handling edge cases; SIGTERM may not terminate; must escalate to SIGKILL; orphaned processes |
| Tier | STANDARD |
| Confidence | 0.85 |
| Verification Method | Integration test: stalling subprocess terminated by kill action |
| MCP Requirements | None |
| Deliverable IDs | D-0014 |

**Deliverables**:
- `kill` action handler with SIGTERM -> SIGKILL escalation and `_timed_out` flag

**Steps**:
1. [IMPL] Create kill action handler that logs WARNING with process state
2. [IMPL] Send SIGTERM to subprocess; wait brief grace period
3. [IMPL] Escalate to SIGKILL if process still alive after grace period
4. [IMPL] Set `_timed_out=True` flag on the process state
5. [IMPL] Break the poll loop after kill
6. [TEST] Verify subprocess terminated and `_timed_out=True` set

**Acceptance Criteria**:
1. WARNING logged before kill with full process state
2. SIGTERM sent first with grace period before SIGKILL escalation
3. `_timed_out=True` flag set on process state after kill
4. Poll loop breaks after successful termination

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "kill_action" -v` passes
2. Integration test: stalling subprocess killed within 5s of timeout trigger

**Dependencies**: T03.01 (stall detection)
**Rollback**: Revert kill handler
**Notes**: FR-015 (kill action), FR-016. SIGTERM->SIGKILL escalation prevents orphaned processes.

---

### T03.04 -- Implement single-fire guard for watchdog

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M3 |
| Why | Without a single-fire guard, the watchdog would trigger on every poll tick once the stall threshold is exceeded, flooding logs with repeated warnings or attempting to kill an already-dead process. |
| Effort | S |
| Risk | Low |
| Risk Drivers | Guard reset on output growth must be correct to avoid missing subsequent stalls |
| Tier | STANDARD |
| Confidence | 0.92 |
| Verification Method | Unit test: verify action fires once per stall, resets on output growth |
| MCP Requirements | None |
| Deliverable IDs | D-0015 |

**Deliverables**:
- `_stall_acted` flag preventing repeated action per stall period, reset on output growth

**Steps**:
1. [IMPL] Add `_stall_acted: bool = False` state variable to executor context
2. [IMPL] Check `_stall_acted` before dispatching stall action; skip if already acted
3. [IMPL] Set `_stall_acted = True` after action dispatch
4. [IMPL] Reset `_stall_acted = False` when output growth detected (stall ends)
5. [TEST] Verify: first stall triggers action, subsequent ticks skip, growth resets guard

**Acceptance Criteria**:
1. `_stall_acted` flag prevents repeated action during same stall period
2. Flag set to True after action dispatch
3. Flag resets to False when output growth detected
4. Second stall after growth triggers action again (not permanently suppressed)

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "single_fire" -v` passes
2. Log analysis: exactly one warning per stall period in debug.log

**Dependencies**: T03.01, T03.02 or T03.03
**Rollback**: Revert guard logic
**Notes**: FR-017.

---

### CHECKPOINT CP-03 (after T03.04)

**Phase 2+3 Completion Check (5 tasks since CP-02)**:
- [ ] T02.06 and T03.01-T03.04 completed
- [ ] CLI options `--debug`, `--stall-timeout`, `--stall-action` functional
- [ ] Watchdog triggers on stall with warn/kill actions
- [ ] Single-fire guard prevents repeated actions
- [ ] Existing test suite passes: `uv run pytest tests/sprint/ -v`
- [ ] No regressions in existing sprint behavior

---

## Phase 4: Validation Checkpoint 1

**Roadmap Item**: M4
**Priority**: P2
**Phase Risk**: Low
**Phase Dependencies**: Phase 2 (M2) and Phase 3 (M3) complete
**Phase Summary**: Manual validation and basic assertions verifying M2 and M3 deliverables before building the full diagnostics pipeline. This is a quality gate checkpoint.

---

### T04.01 -- Validate debug log format

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M4 |
| Why | Before building the diagnostics pipeline (M5) and test infrastructure (M6) that depend on debug.log format, validate that the log output matches the spec format exactly. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None -- validation only |
| Tier | EXEMPT |
| Confidence | 0.95 |
| Verification Method | Manual run + assertion script |
| MCP Requirements | None |
| Deliverable IDs | D-0016 |

**Deliverables**:
- Validation evidence that debug.log format matches spec

**Steps**:
1. [VERIFY] Run `superclaude sprint run --debug` on a simple task
2. [VERIFY] Check debug.log starts with `# debug-log-version: 1.0`
3. [VERIFY] Check PHASE_BEGIN/PHASE_END markers present and correctly bracketing events
4. [VERIFY] Check poll_tick events present with all 8 required fields
5. [VERIFY] Check spawn event includes PID and command array

**Acceptance Criteria**:
1. Version header `# debug-log-version: 1.0` is the first line
2. PHASE_BEGIN/PHASE_END markers bracket all per-phase events
3. poll_tick events contain: phase, PID, poll_result, elapsed, output_bytes, growth_rate, stall_seconds, stall_status
4. spawn event contains: PID, command array, env delta

**Validation**:
1. Manual inspection of debug.log output matches spec format
2. Grep verification: `grep -c "PHASE_BEGIN" debug.log` > 0

**Dependencies**: T02.01 (executor instrumentation), T02.02 (process instrumentation)
**Rollback**: N/A -- validation only, no changes made
**Notes**: D4.1 from roadmap. This is a read-only validation checkpoint.

---

### T04.02 -- Validate watchdog behavior

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M4 |
| Why | Validate that the watchdog mechanism works end-to-end before building diagnostics that depend on `was_stall_killed` flag. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None -- validation only |
| Tier | EXEMPT |
| Confidence | 0.93 |
| Verification Method | Manual run with stalling task |
| MCP Requirements | None |
| Deliverable IDs | D-0017 |

**Deliverables**:
- Validation evidence that watchdog terminates stalled processes correctly

**Steps**:
1. [VERIFY] Run with `--stall-timeout 10 --stall-action kill` on a task designed to stall
2. [VERIFY] Confirm process terminates within 15 seconds of stall detection
3. [VERIFY] Confirm WARNING log entry present with process state
4. [VERIFY] Confirm `_timed_out` flag is set correctly

**Acceptance Criteria**:
1. Stalled process terminated within 5 seconds of timeout threshold
2. WARNING log entry includes PID, stall duration, output state
3. `_timed_out=True` flag set on terminated process
4. Sprint run exits with appropriate error status after kill

**Validation**:
1. Manual: `superclaude sprint run --stall-timeout 10 --stall-action kill` terminates stalled task
2. Log verification: WARNING entry present in output

**Dependencies**: T03.01-T03.04 (watchdog mechanism)
**Rollback**: N/A -- validation only
**Notes**: D4.2 from roadmap.

---

### T04.03 -- Validate backward compatibility

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M4 |
| Why | NFR-007 requires zero breaking changes. Running the full existing test suite validates that all additions are backward-compatible. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None -- validation only |
| Tier | EXEMPT |
| Confidence | 0.96 |
| Verification Method | Full existing test suite execution |
| MCP Requirements | None |
| Deliverable IDs | D-0018 |

**Deliverables**:
- Evidence that all existing tests pass after both the output buffering fix and diagnostic framework changes

**Steps**:
1. [VERIFY] Run `uv run pytest tests/sprint/test_*.py -v` (all existing sprint tests)
2. [VERIFY] Confirm zero failures, zero errors
3. [VERIFY] Confirm no tests were modified **by the diagnostic framework** to pass (diff check against post-buffering-fix baseline)

**Acceptance Criteria**:
1. All existing `tests/sprint/test_*.py` tests pass
2. Zero test modifications required by the diagnostic framework (note: the output buffering fix sprint already modified `test_process.py` and `test_regression_gaps.py` assertions for `stream-json` format and `env.pop` behavior — those changes are the pre-existing baseline, not diagnostic framework changes)
3. No new warnings introduced by the diagnostic framework
4. `SprintConfig()` with no args behaves identically to pre-change (debug=False, stall_timeout=0, stall_action="warn")

**Validation**:
1. `uv run pytest tests/sprint/ -v --tb=short` shows all green
2. `git diff tests/sprint/test_*.py` shows no changes to existing tests beyond those already made by the output buffering fix

**Dependencies**: All Phase 1, 2, 3 tasks
**Rollback**: N/A -- validation only
**Notes**: D4.3, NFR-007. This is the gate before proceeding to the diagnostics pipeline. **Context**: the output buffering fix (tasklist-fixes) already modified `test_process.py` (`text`→`stream-json`, `CLAUDECODE` env assertion) and `test_regression_gaps.py` (env assertion). The diagnostic framework introduces NO additional modifications to those tests — backward compatibility is measured against the post-buffering-fix baseline.

---

### CHECKPOINT CP-04 (end of Phase 4)

**Validation Checkpoint**:
- [ ] Debug log format validated (T04.01)
- [ ] Watchdog behavior validated (T04.02)
- [ ] Backward compatibility confirmed (T04.03)
- [ ] All existing tests pass without modification
- [ ] GATE: Proceed to Phase 5 only when all 3 validations pass

---

## Phase 5: Diagnostics & Failure Classification

**Roadmap Item**: M5
**Priority**: P0
**Phase Risk**: Medium
**Phase Dependencies**: Phase 2 (M2) and Phase 3 (M3)
**Phase Summary**: Create `diagnostics.py` module with `DiagnosticBundle`, `DiagnosticCollector`, `FailureClassifier`, `ReportGenerator`, and integrate into executor failure path.

---

### T05.01 -- Implement `DiagnosticBundle` dataclass

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M5 |
| Why | The `DiagnosticBundle` is the data contract between collector, classifier, and report generator. Defining it first enables parallel development of the consumer components. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Must capture all fields needed by FailureClassifier decision tree |
| Tier | STANDARD |
| Confidence | 0.93 |
| Verification Method | Unit test: create bundle with all fields, verify serialization |
| MCP Requirements | None |
| Deliverable IDs | D-0019 |

**Deliverables**:
- `DiagnosticBundle` dataclass in `src/superclaude/cli/sprint/diagnostics.py`

**Steps**:
1. [PLAN] Define all fields from spec: phase_number, subprocess_spawned, subprocess_pid, output_file_exists, output_bytes, result_file_exists, result_file_content, exit_code, stall_seconds, was_stall_killed, debug_log_tail, stderr_contents, process_state
2. [IMPL] Create `diagnostics.py` module with `DiagnosticBundle` dataclass
3. [IMPL] Add type annotations and default values for optional fields
4. [IMPL] Add `to_dict()` method for JSON serialization
5. [TEST] Verify all 13 fields accessible and serializable

**Acceptance Criteria**:
1. Dataclass contains all 13 fields specified in D5.1
2. All fields have appropriate type annotations
3. Optional fields have sensible defaults (None for missing data)
4. `to_dict()` produces JSON-serializable dictionary

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "diagnostic_bundle" -v` passes
2. `DiagnosticBundle()` with minimal args creates valid instance

**Dependencies**: None (data structure only)
**Rollback**: Delete `diagnostics.py`
**Notes**: FR-033. This is the first file in the diagnostics module.

---

### T05.02 -- Implement `DiagnosticCollector.collect()`

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M5 |
| Why | The collector gathers all diagnostic state from sprint artifacts on failure. Process state capture via `/proc` with `ps` fallback handles cross-platform compatibility. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Process state capture fails in sandboxed environments (R-002); /proc unavailable on non-Linux |
| Tier | STANDARD |
| Confidence | 0.85 |
| Verification Method | Unit test with mock filesystem; integration test on real process |
| MCP Requirements | None |
| Deliverable IDs | D-0020 |

**Deliverables**:
- `DiagnosticCollector` class with `collect()` method in `diagnostics.py`

**Steps**:
1. [IMPL] Create `DiagnosticCollector` class with `collect(sprint_result, config)` method
2. [IMPL] Gather file state: output file exists/size, result file exists/content, stderr contents
3. [IMPL] Gather process state: try `/proc/{pid}/` first (Linux)
4. [IMPL] Fallback to `ps -p {pid} -o pid,ppid,state,rss,vsz,time,args` if `/proc` unavailable
5. [IMPL] Read debug.log tail (last 50 lines) if debug mode was active
6. [IMPL] Return populated `DiagnosticBundle`
7. [TEST] Verify collection with mock artifacts; verify `/proc` and `ps` paths

**Acceptance Criteria**:
1. Collects all file-based diagnostic state (output, result, stderr, debug.log tail)
2. Process state captured via `/proc` with `ps` fallback
3. Graceful handling when process already terminated (None for process_state)
4. Returns fully populated `DiagnosticBundle`

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "diagnostic_collector" -v` passes
2. Integration: collector produces valid bundle from real sprint artifacts

**Dependencies**: T05.01 (`DiagnosticBundle`)
**Rollback**: Remove `DiagnosticCollector` from `diagnostics.py`
**Notes**: FR-033, FR-034, R-002.

---

### T05.03 -- Implement `FailureClassifier.classify()`

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M5 |
| Why | The classifier converts raw diagnostic data into actionable failure modes with confidence scores. Priority ordering ensures the most specific classification wins. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Heuristic misclassification on edge cases (R-004); confidence scoring must reflect classifier certainty |
| Tier | STANDARD |
| Confidence | 0.85 |
| Verification Method | Unit test: each failure mode triggered by specific bundle state |
| MCP Requirements | None |
| Deliverable IDs | D-0021 |

**Deliverables**:
- `FailureClassifier` class with `classify()` method returning `(FailureMode, confidence)`
- `FailureMode` enum with 7 modes

**Steps**:
1. [IMPL] Create `FailureMode` enum: SPAWN_FAILURE, TIMEOUT, SILENT_STALL, OUTPUT_STALL, EXIT_CODE_ERROR, RESULT_MISSING, UNKNOWN
2. [IMPL] Create `FailureClassifier` class with `classify(bundle: DiagnosticBundle)` method
3. [IMPL] Implement priority-ordered classification: SPAWN_FAILURE > TIMEOUT > SILENT_STALL > OUTPUT_STALL > EXIT_CODE_ERROR > RESULT_MISSING > UNKNOWN
4. [IMPL] Calculate confidence score (0.0-1.0) based on evidence strength
5. [IMPL] Return `(FailureMode, confidence)` tuple
6. [TEST] Test each failure mode with a crafted bundle that triggers it
7. [TEST] Test edge cases where multiple modes could apply (verify priority)

**Acceptance Criteria**:
1. All 7 failure modes defined in `FailureMode` enum
2. Classification follows strict priority ordering per spec
3. Confidence score reflects evidence strength (0.0-1.0)
4. UNKNOWN returned only when no other mode matches

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "failure_classifier" -v` passes
2. Each of 7 failure modes tested with dedicated test case

**Dependencies**: T05.01 (`DiagnosticBundle`)
**Rollback**: Remove `FailureClassifier` from `diagnostics.py`
**Notes**: FR-035.

---

### T05.04 -- Implement `ReportGenerator.generate()` and `.write()`

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M5 |
| Why | The diagnostic report is the primary output artifact -- a structured JSON file with version, evidence, root cause, and recommended actions that users and tools can consume. |
| Effort | M |
| Risk | Low |
| Risk Drivers | JSON schema must be stable for downstream consumers |
| Tier | STANDARD |
| Confidence | 0.92 |
| Verification Method | Unit test: verify JSON structure and content |
| MCP Requirements | None |
| Deliverable IDs | D-0022 |

**Deliverables**:
- `ReportGenerator` class with `generate()` and `write()` methods producing `diagnostic-report.json`

**Steps**:
1. [IMPL] Create `ReportGenerator` class with `generate(bundle, failure_mode, confidence)` method
2. [IMPL] Produce report dict with: version (1.0), timestamp, failure_mode, confidence, evidence dict, suggested_root_cause, recommended_actions list
3. [IMPL] Create `write(report, path)` method that writes JSON with indentation
4. [IMPL] Map each failure mode to specific root cause text and action list
5. [TEST] Verify JSON structure matches spec schema
6. [TEST] Verify write produces valid, readable JSON file

**Acceptance Criteria**:
1. Report contains: version "1.0", timestamp, failure_mode, confidence, evidence, root_cause, actions
2. Evidence dict includes all relevant DiagnosticBundle fields
3. Recommended actions are specific and actionable per failure mode
4. `write()` produces valid JSON file at specified path

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "report_generator" -v` passes
2. JSON schema validation on generated report

**Dependencies**: T05.01 (`DiagnosticBundle`), T05.03 (`FailureMode`)
**Rollback**: Remove `ReportGenerator` from `diagnostics.py`
**Notes**: FR-036.

---

### CHECKPOINT CP-05 (after T05.04)

**Progress Check (5 tasks since CP-03)**:
- [ ] T04.01-T04.03 and T05.01-T05.04 completed (validation + diagnostics core)
- [ ] `diagnostics.py` contains: DiagnosticBundle, DiagnosticCollector, FailureClassifier, ReportGenerator
- [ ] All 7 failure modes classifiable
- [ ] Report generation produces valid JSON
- [ ] Existing test suite still passes

---

### T05.05 -- Integrate diagnostics into executor failure path

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M5 |
| Why | The integration point connects the diagnostics pipeline to the sprint executor. On phase failure with debug mode active, the pipeline runs: collect -> classify -> suggest -> generate -> write. Best-effort to avoid masking the original error. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Exception handling must be best-effort -- diagnostic failures must not mask the original sprint error |
| Tier | STRICT |
| Confidence | 0.88 |
| Verification Method | Integration test: failing sprint produces diagnostic report |
| MCP Requirements | None |
| Deliverable IDs | D-0023 |

**Deliverables**:
- Executor failure path modified to run diagnostic pipeline when `config.debug=True`

**Steps**:
1. [PLAN] Identify the failure detection point in executor (phase failure handler)
2. [IMPL] On phase failure when `config.debug=True`: instantiate DiagnosticCollector
3. [IMPL] Call `collect()` to gather diagnostic state
4. [IMPL] Call `FailureClassifier.classify()` on the bundle
5. [IMPL] Call `ReportGenerator.generate()` and `.write()` to produce report
6. [IMPL] Wrap entire pipeline in try/except -- log but don't re-raise diagnostic errors
7. [TEST] Verify: failing phase with debug=True produces diagnostic-report.json
8. [TEST] Verify: diagnostic pipeline failure does not mask original error

**Acceptance Criteria**:
1. On phase failure with `config.debug=True`: diagnostic pipeline runs automatically
2. `diagnostic-report.json` written to sprint results directory
3. Pipeline exceptions caught and logged -- never mask original sprint error
4. No diagnostic pipeline execution when `config.debug=False`

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "executor_integration" -v` passes
2. Integration: failing sprint with `--debug` produces diagnostic-report.json

**Dependencies**: T05.02, T05.03, T05.04, T02.01 (executor)
**Rollback**: Revert executor changes via git
**Notes**: D5.5, FR-036. STRICT tier because it modifies the executor's error handling path -- must be best-effort to avoid regression.

---

## Phase 6: Test Infrastructure & Graduated Tests

**Roadmap Item**: M6
**Priority**: P1
**Phase Risk**: Medium
**Phase Dependencies**: Phase 5 (M5 complete)
**Phase Summary**: Build the `DiagnosticTestHarness` and implement all test files: Level 0 (pipeline smoke), Levels 1-3 (graduated claude tests), negative tests (failure modes), and pytest markers.

---

### T06.01 -- Implement `DiagnosticTestHarness` class

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M6 |
| Why | The test harness provides a reusable foundation for all diagnostic tests. `create_sprint()` generates controlled environments, `run_sprint()` executes with PATH override for fake claude, and `analyze_result()` runs the diagnostic pipeline. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | PATH substitution for fake claude may have edge cases (R-003); env var manipulation may cause flakiness (R-006) |
| Tier | STANDARD |
| Confidence | 0.82 |
| Verification Method | Unit test: harness creates sprint, runs it, analyzes result |
| MCP Requirements | None |
| Deliverable IDs | D-0024 |

**Deliverables**:
- `DiagnosticTestHarness` class in `src/superclaude/cli/sprint/test_harness.py` (or in test conftest)

**Steps**:
1. [PLAN] Design harness API: `create_sprint(phases)`, `run_sprint(config_overrides)`, `analyze_result()`
2. [IMPL] `create_sprint()`: generates temp dirs with tasklist-index.md + phase files using pytest `tmp_path`
3. [IMPL] `run_sprint()`: executes sprint with PATH override pointing to fake claude script, captures result
4. [IMPL] `analyze_result()`: runs DiagnosticCollector + FailureClassifier on sprint output
5. [IMPL] Add environment save/restore in try/finally pattern (R-006 mitigation)
6. [IMPL] Add cleanup of temporary files and orphaned processes
7. [TEST] Verify full create -> run -> analyze cycle produces valid DiagnosticBundle
8. [TEST] Verify env isolation: no leaked environment variables after run

**Acceptance Criteria**:
1. `create_sprint()` generates valid temp directory with tasklist and phases
2. `run_sprint()` executes with PATH override for fake claude
3. `analyze_result()` produces `DiagnosticBundle` with classification
4. Environment variables saved and restored via try/finally pattern

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "test_harness" -v` passes
2. Verify no orphaned processes or leaked env vars after test run

**Dependencies**: T05.01-T05.03 (diagnostics module)
**Rollback**: Delete harness file
**Notes**: FR-037, R-003, R-006. Save/restore pattern from spec: `os.environ.copy()` in try/finally.

---

### T06.02 -- Implement `DebugLogReader` and test fixtures

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M6 |
| Why | `DebugLogReader` provides programmatic access to debug.log for test assertions. Filter by component, phase, and level enables precise event verification in tests. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Regex parsing may break on unusual content (R-007); mitigated by returning empty list on parse errors |
| Tier | STANDARD |
| Confidence | 0.90 |
| Verification Method | Unit test: parse sample debug.log, filter by component/phase |
| MCP Requirements | None |
| Deliverable IDs | D-0025 |

**Deliverables**:
- `DebugLogReader` class with parse, filter, and `phase_events()` slicing
- `debug_log_reader` fixture factory

**Steps**:
1. [IMPL] Create `DebugLogReader` class that parses debug.log into `DebugEvent` objects
2. [IMPL] Add filter methods: `by_component(name)`, `by_phase(number)`, `by_level(level)`
3. [IMPL] Add `phase_events(phase_number)` that returns events between PHASE_BEGIN and PHASE_END
4. [IMPL] Handle parse errors gracefully -- return empty list, not exception (R-007)
5. [IMPL] Create `debug_log_reader` fixture factory that returns configured reader
6. [TEST] Parse sample debug.log and verify filtering works correctly

**Acceptance Criteria**:
1. Parses debug.log into `DebugEvent` objects with timestamp, level, component, message
2. Filter by component, phase, and level returns correct subsets
3. `phase_events()` returns events strictly between PHASE_BEGIN and PHASE_END markers
4. Parse errors return empty results, not exceptions

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ -k "debug_log_reader" -v` passes
2. Edge case: empty file, malformed lines, partial phase brackets all handled

**Dependencies**: T01.02 (formatter defines the format to parse)
**Rollback**: Remove reader class and fixture
**Notes**: FR-038, R-007.

---

### T06.03 -- Create `tests/sprint/diagnostic/conftest.py`

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M6 |
| Why | Centralized test fixtures and dataclasses for all diagnostic tests. The `requires_claude` fixture enables graceful skip when claude binary is absent (CI compatibility). |
| Effort | M |
| Risk | Low |
| Risk Drivers | None significant |
| Tier | STANDARD |
| Confidence | 0.93 |
| Verification Method | Import conftest fixtures in a test and verify they work |
| MCP Requirements | None |
| Deliverable IDs | D-0026 |

**Deliverables**:
- `tests/sprint/diagnostic/conftest.py` with fixtures: `diagnostic_harness`, `debug_log_reader`, `requires_claude`
- `PhaseSpec` and `DiagnosticResult` dataclasses

**Steps**:
1. [IMPL] Create `tests/sprint/diagnostic/` directory with `__init__.py`
2. [IMPL] Create `conftest.py` with `diagnostic_harness` fixture (yields `DiagnosticTestHarness`)
3. [IMPL] Add `debug_log_reader` fixture factory
4. [IMPL] Add `requires_claude` fixture that skips test when claude binary absent
5. [IMPL] Define `PhaseSpec` dataclass for test phase definitions
6. [IMPL] Define `DiagnosticResult` dataclass for test result assertions
7. [TEST] Verify fixtures importable and functional

**Acceptance Criteria**:
1. `diagnostic_harness` fixture yields configured `DiagnosticTestHarness`
2. `debug_log_reader` fixture returns `DebugLogReader` for current test's debug.log
3. `requires_claude` skips test with clear message when claude not in PATH
4. `PhaseSpec` and `DiagnosticResult` dataclasses defined and usable

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/ --collect-only` shows fixtures available
2. Tests using `requires_claude` skip cleanly when claude absent

**Dependencies**: T06.01 (harness), T06.02 (reader)
**Rollback**: Delete `tests/sprint/diagnostic/` directory
**Notes**: FR-039, FR-040, NFR-005.

---

### T06.04 -- Implement `test_level_0.py` pipeline smoke tests

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M6 |
| Why | Level 0 tests validate the sprint pipeline with a shell script (no claude dependency). These are the most important CI tests -- they run everywhere, fast (<5s), and catch pipeline regressions. |
| Effort | M |
| Risk | Low |
| Risk Drivers | Shell script must faithfully exercise the pipeline; PATH override must work reliably |
| Tier | STANDARD |
| Confidence | 0.90 |
| Verification Method | Run tests in CI-like environment without claude binary |
| MCP Requirements | None |
| Deliverable IDs | D-0027 |

**Deliverables**:
- `tests/sprint/diagnostic/test_level_0.py` with pipeline smoke tests

**Steps**:
1. [PLAN] Design L0 test: shell script phase that writes output and PASS result
2. [IMPL] Create shell script that exercises: subprocess spawn, output write, result file creation
3. [IMPL] Write test_subprocess_spawns: verify process started and completed
4. [IMPL] Write test_output_created: verify output file exists with content
5. [IMPL] Write test_result_written: verify result file contains PASS status
6. [IMPL] Write test_debug_log_structure: verify debug.log has version header + events
7. [TEST] Run all L0 tests, verify completion in <5s

**Acceptance Criteria**:
1. All tests use shell script phases (no claude dependency)
2. Validates: subprocess spawn, output creation, result file, PASS status, debug.log structure
3. All tests complete in <5s total
4. Tests run successfully without claude binary in PATH

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/test_level_0.py -v` passes in <5s
2. Tests pass in environment without claude binary

**Dependencies**: T06.03 (conftest fixtures)
**Rollback**: Delete `test_level_0.py`
**Notes**: FR-022, NFR-001, SC-004. These are the primary CI-safe tests.

---

### CHECKPOINT CP-06 (after T06.04)

**Progress Check (5 tasks since CP-05)**:
- [ ] T05.05, T06.01-T06.04 completed
- [ ] Diagnostics integrated into executor failure path
- [ ] Test harness functional: create -> run -> analyze
- [ ] DebugLogReader parses and filters correctly
- [ ] L0 pipeline smoke tests passing in <5s
- [ ] No regressions in existing test suite

---

### T06.05 -- Implement `test_level_1.py` through `test_level_3.py`

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M6 |
| Why | Graduated complexity tests validate increasingly complex sprint scenarios with real claude. L1: basic echo, L2: multi-phase file ops, L3: analysis with halt-on-failure. All skip gracefully without claude. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | Depends on claude binary availability; test timeouts must be generous but bounded; environment isolation critical |
| Tier | STANDARD |
| Confidence | 0.80 |
| Verification Method | Run with claude binary present; verify graceful skip when absent |
| MCP Requirements | None |
| Deliverable IDs | D-0028 |

**Deliverables**:
- `tests/sprint/diagnostic/test_level_1.py` (echo, <30s)
- `tests/sprint/diagnostic/test_level_2.py` (file ops, <60s)
- `tests/sprint/diagnostic/test_level_3.py` (analysis + halt-on-failure, <120s)

**Steps**:
1. [IMPL] `test_level_1.py`: 1 phase trivial echo task, validate basic claude integration (<30s)
2. [IMPL] `test_level_2.py`: 2 phases file read/write, validate multi-phase sequencing (<60s)
3. [IMPL] `test_level_3.py`: 2-3 phases lightweight analysis, validate halt-on-failure behavior (<120s)
4. [IMPL] All tests use `@pytest.mark.skipif` when claude binary absent
5. [IMPL] All tests use `requires_claude` fixture from conftest
6. [TEST] Verify skip behavior when claude absent
7. [TEST] Verify timeouts enforced per level

**Acceptance Criteria**:
1. L1 test: 1 phase, echo task, completes in <30s
2. L2 test: 2 phases, file read/write, completes in <60s
3. L3 test: 2-3 phases, analysis, halt-on-failure validated, completes in <120s
4. All tests skip with clear message when claude binary absent

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/test_level_1.py -v` passes (with claude)
2. `uv run pytest tests/sprint/diagnostic/ -k "level" -v` shows clean skips (without claude)

**Dependencies**: T06.03 (conftest), T06.01 (harness)
**Rollback**: Delete L1-L3 test files
**Notes**: FR-023, FR-024, FR-025, NFR-002, NFR-003, NFR-004, NFR-005.

---

### T06.06 -- Implement `test_negative.py` failure mode tests

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M6 |
| Why | Negative tests validate that each of the 6 failure modes is correctly detected and classified. These are the core diagnostic accuracy tests -- each simulates a specific failure scenario and verifies the classifier output. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | Each failure mode requires a specific simulation script; timing-dependent tests (SILENT_STALL, TIMEOUT) may be flaky |
| Tier | STANDARD |
| Confidence | 0.82 |
| Verification Method | Each test triggers specific failure mode and verifies classification |
| MCP Requirements | None |
| Deliverable IDs | D-0029 |

**Deliverables**:
- `tests/sprint/diagnostic/test_negative.py` with 6 failure mode test cases

**Steps**:
1. [IMPL] `test_spawn_failure`: non-existent binary -> PhaseStatus.ERROR, FailureMode.SPAWN_FAILURE
2. [IMPL] `test_silent_stall`: script sleeps forever, stall-timeout kills -> FailureMode.SILENT_STALL
3. [IMPL] `test_output_stall`: script writes then sleeps -> FailureMode.OUTPUT_STALL
4. [IMPL] `test_result_missing`: script writes output but no result file -> FailureMode.RESULT_MISSING
5. [IMPL] `test_exit_code_error`: script exits with code 1 -> FailureMode.EXIT_CODE_ERROR
6. [IMPL] `test_timeout`: script exceeds phase timeout -> FailureMode.TIMEOUT
7. [TEST] Each test validates correct classification AND diagnostic report generation
8. [TEST] Verify confidence scores are reasonable (>0.5 for clear cases)

**Acceptance Criteria**:
1. All 6 failure modes tested with dedicated simulation scripts
2. Each test verifies correct `FailureMode` classification
3. Each test verifies `diagnostic-report.json` generated with correct content
4. Confidence scores > 0.5 for all clear-cut failure scenarios

**Validation**:
1. `uv run pytest tests/sprint/diagnostic/test_negative.py -v` passes
2. Each failure mode produces correct classification in diagnostic report

**Dependencies**: T06.03 (conftest), T06.01 (harness), T05.03 (classifier)
**Rollback**: Delete `test_negative.py`
**Notes**: FR-026 through FR-031, FR-032.

---

### T06.07 -- Add pytest diagnostic markers

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M6 |
| Why | Custom pytest markers enable selective test execution by diagnostic level. CI can run L0 only (fast), while local development runs all levels. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | LIGHT |
| Confidence | 0.97 |
| Verification Method | Verify marker filtering works: `pytest -m diagnostic_l0` |
| MCP Requirements | None |
| Deliverable IDs | D-0030 |

**Deliverables**:
- Pytest markers: `@pytest.mark.diagnostic`, `@pytest.mark.diagnostic_l0` through `@pytest.mark.diagnostic_ln`
- Marker registration in `pyproject.toml` or `conftest.py`

**Steps**:
1. [IMPL] Register markers in pytest configuration: `diagnostic`, `diagnostic_l0`, `diagnostic_l1`, `diagnostic_l2`, `diagnostic_l3`, `diagnostic_ln`
2. [IMPL] Apply `@pytest.mark.diagnostic` to all test files in `tests/sprint/diagnostic/`
3. [IMPL] Apply level-specific markers: `diagnostic_l0` to test_level_0.py, `diagnostic_ln` to test_negative.py, etc.
4. [TEST] Verify `uv run pytest -m diagnostic_l0` runs only L0 tests

**Acceptance Criteria**:
1. `@pytest.mark.diagnostic` applied to all diagnostic tests
2. Per-level markers (`diagnostic_l0` through `diagnostic_ln`) enable selective execution
3. `pytest -m diagnostic_l0` runs only pipeline smoke tests
4. Markers registered to avoid pytest warnings

**Validation**:
1. `uv run pytest -m diagnostic_l0 --collect-only` shows only L0 tests
2. `uv run pytest -m diagnostic --collect-only` shows all diagnostic tests

**Dependencies**: T06.04-T06.06 (test files to apply markers to)
**Rollback**: Remove marker decorators and registration
**Notes**: FR-040, D6.7.

---

### CHECKPOINT CP-07 (end of Phase 6)

**Phase 6 Completion Check**:
- [ ] All 7 tasks (T06.01-T06.07) completed
- [ ] Test harness functional with create/run/analyze cycle
- [ ] L0 tests pass without claude (<5s)
- [ ] L1-L3 tests skip cleanly or pass with claude
- [ ] All 6 negative tests pass with correct classification
- [ ] Pytest markers enable selective execution
- [ ] Existing test suite still passes

---

## Phase 7: Integration Validation & Acceptance

**Roadmap Item**: M7
**Priority**: P1
**Phase Risk**: Low
**Phase Dependencies**: Phase 4 (M4) and Phase 6 (M6)
**Phase Summary**: End-to-end validation that all components work together. Verify all 5 user stories and success criteria. Final backward compatibility check and file inventory verification.

---

### T07.01 -- Validate user stories US1-US5

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M7 |
| Why | User story validation ensures the framework meets its intended purpose from the user's perspective. Each story maps to specific success criteria that must be demonstrably met. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None -- validation only |
| Tier | EXEMPT |
| Confidence | 0.93 |
| Verification Method | Manual validation with evidence collection |
| MCP Requirements | None |
| Deliverable IDs | D-0031 |

**Deliverables**:
- Validation evidence for US1-US5 traced to passing tests or manual verification

**Steps**:
1. [VERIFY] US1 (SC-001): Run `sprint run --debug`, verify debug.log with 0.5s poll ticks
2. [VERIFY] US2 (SC-002): Run with `--stall-timeout 60 --stall-action kill`, verify auto-terminate + diagnostic report
3. [VERIFY] US3 (SC-003): Run `uv run pytest tests/sprint/diagnostic/ -v`, verify graduated pass/fail
4. [VERIFY] US4 (SC-004): Verify L0 tests pass without claude binary
5. [VERIFY] US5 (SC-005): Verify backward compatibility -- existing behavior unchanged

**Acceptance Criteria**:
1. US1: debug.log shows subprocess state at 0.5s intervals
2. US2: Stalled sprint auto-terminates with diagnostic report
3. US3: Graduated tests show per-level pass/fail with auto reports
4. US4: L0 pipeline smoke test passes without claude

**Validation**:
1. Each user story traced to at least one passing test or manual verification record
2. Success criteria SC-001 through SC-005 all marked PASS with evidence

**Dependencies**: All prior phases
**Rollback**: N/A -- validation only
**Notes**: D7.1.

---

### T07.02 -- Run full test suite and verify all pass

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M7 |
| Why | Final integration gate -- both existing sprint tests and new diagnostic tests must pass together, proving no regressions and full functionality. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None -- validation only |
| Tier | EXEMPT |
| Confidence | 0.95 |
| Verification Method | Full pytest suite execution |
| MCP Requirements | None |
| Deliverable IDs | D-0032 |

**Deliverables**:
- Full test suite pass evidence

**Steps**:
1. [VERIFY] Run `uv run pytest tests/sprint/ -v` (all sprint tests)
2. [VERIFY] Confirm zero failures across existing + new tests
3. [VERIFY] Confirm no test modifications were needed for existing tests

**Acceptance Criteria**:
1. `uv run pytest tests/sprint/ -v` shows all green
2. Existing `test_*.py` files pass without modification
3. New `tests/sprint/diagnostic/` tests pass (L0 always, L1-3 when claude available)
4. Zero errors, zero unexpected warnings

**Validation**:
1. `uv run pytest tests/sprint/ -v --tb=short` shows 100% pass rate
2. CI-compatible: L0 + existing tests pass without claude binary

**Dependencies**: All tasks complete
**Rollback**: N/A -- validation only
**Notes**: D7.2.

---

### T07.03 -- Perform backward compatibility final check

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M7 |
| Why | NFR-007 is a hard constraint. This final check verifies that `SprintConfig` with no new flags behaves identically to pre-change behavior: no debug.log created, no watchdog active. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None -- validation only |
| Tier | EXEMPT |
| Confidence | 0.96 |
| Verification Method | Run sprint without new flags, verify identical behavior |
| MCP Requirements | None |
| Deliverable IDs | D-0033 |

**Deliverables**:
- Backward compatibility validation evidence

**Steps**:
1. [VERIFY] Create `SprintConfig()` with no new arguments -- verify all defaults
2. [VERIFY] Run `superclaude sprint run` without `--debug` -- verify no debug.log created
3. [VERIFY] Verify no watchdog triggers when `stall_timeout=0` (default)

**Acceptance Criteria**:
1. `SprintConfig()` defaults: debug=False, stall_timeout=0, stall_action="warn"
2. No debug.log file created when `--debug` not specified
3. No watchdog activity when stall_timeout=0
4. CLI `--help` output unchanged except for new option additions

**Validation**:
1. Sprint run without new flags produces identical output to pre-change behavior
2. No debug.log, no diagnostic-report.json, no watchdog warnings

**Dependencies**: All implementation tasks
**Rollback**: N/A -- validation only
**Notes**: D7.3, NFR-007.

---

### T07.04 -- Verify file inventory against spec

| Field | Value |
|-------|-------|
| Roadmap Item IDs | M7 |
| Why | Spec defines exactly 7 modified files and 9 new files. Verifying the file inventory catches missing deliverables and extraneous files that could indicate scope creep. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None -- verification only |
| Tier | EXEMPT |
| Confidence | 0.97 |
| Verification Method | git diff --stat against spec file inventory |
| MCP Requirements | None |
| Deliverable IDs | D-0034 |

**Deliverables**:
- File inventory verification evidence

**Steps**:
1. [VERIFY] List all modified files via `git diff --stat` against base branch
2. [VERIFY] Cross-reference against spec File Inventory table (7 modified, 9 new)
3. [VERIFY] Confirm no extraneous files beyond spec scope

**Acceptance Criteria**:
1. All 7 modified source files accounted for
2. All 9 new files (2 source modules + 7 test files) accounted for
3. No extraneous files beyond spec scope
4. All file paths match spec conventions

**Validation**:
1. `git diff --stat` file count matches spec inventory
2. Manual cross-reference with spec File Inventory table

**Dependencies**: All implementation tasks
**Rollback**: N/A -- verification only
**Notes**: D7.4.

---

### CHECKPOINT CP-08 (end of Phase 7 -- Final)

**Final Acceptance Gate**:
- [ ] All 34 tasks completed
- [ ] All 5 user stories validated (US1-US5)
- [ ] All 5 success criteria met (SC-001 through SC-005)
- [ ] Full test suite passes (existing + diagnostic)
- [ ] Backward compatibility confirmed
- [ ] File inventory matches spec
- [ ] Zero regressions in existing functionality
- [ ] RELEASE GATE: All checkpoints (CP-01 through CP-08) passed

---

## Traceability Matrix

| Task ID | Roadmap ID | FR IDs | NFR IDs | Risk IDs | SC IDs | Deliverable IDs |
|---------|------------|--------|---------|----------|--------|-----------------|
| T01.01 | M1/D1.1 | FR-004 | - | - | SC-001 | D-0001 |
| T01.02 | M1/D1.2 | FR-003 | - | - | SC-001 | D-0002 |
| T01.03 | M1/D1.3 | FR-002, FR-003, FR-018, FR-021 | - | R-001 | SC-001, SC-005 | D-0003 |
| T01.04 | M1/D1.4 | FR-005 | - | - | SC-001 | D-0004 |
| T01.05 | M1/D1.5 | FR-001, FR-014, FR-015 | NFR-007 | - | SC-005 | D-0005 |
| T02.01 | M2/D2.1 | FR-007, FR-008, FR-020 | - | R-001 | SC-001 | D-0006 |
| T02.02 | M2/D2.2 | FR-009, FR-010 | - | - | SC-001 | D-0007 |
| T02.03 | M2/D2.3 | FR-011 | - | - | SC-001 | D-0008 |
| T02.04 | M2/D2.4 | FR-012 | - | R-005 | SC-001 | D-0009 |
| T02.05 | M2/D2.5 | FR-041 | - | - | - | D-0010 |
| T02.06 | M2/D2.6 | FR-001, FR-014, FR-015 | - | - | SC-001, SC-002 | D-0011 |
| T03.01 | M3/D3.1 | FR-016 | - | R-004, R-008 | SC-002 | D-0012 |
| T03.02 | M3/D3.2 | FR-015, FR-017 | - | - | SC-002 | D-0013 |
| T03.03 | M3/D3.3 | FR-015, FR-016 | - | - | SC-002 | D-0014 |
| T03.04 | M3/D3.4 | FR-017 | - | - | SC-002 | D-0015 |
| T04.01 | M4/D4.1 | FR-003, FR-007, FR-008, FR-020 | - | - | SC-001 | D-0016 |
| T04.02 | M4/D4.2 | FR-016 | - | R-004 | SC-002 | D-0017 |
| T04.03 | M4/D4.3 | - | NFR-007 | - | SC-005 | D-0018 |
| T05.01 | M5/D5.1 | FR-033 | - | - | - | D-0019 |
| T05.02 | M5/D5.2 | FR-033, FR-034 | - | R-002 | - | D-0020 |
| T05.03 | M5/D5.3 | FR-035 | - | R-004 | - | D-0021 |
| T05.04 | M5/D5.4 | FR-036 | - | - | SC-002 | D-0022 |
| T05.05 | M5/D5.5 | FR-036 | - | - | SC-002 | D-0023 |
| T06.01 | M6/D6.1 | FR-037 | NFR-006 | R-003, R-006 | SC-003 | D-0024 |
| T06.02 | M6/D6.2 | FR-038 | - | R-007 | SC-003 | D-0025 |
| T06.03 | M6/D6.3 | FR-039, FR-040 | NFR-005 | - | SC-003 | D-0026 |
| T06.04 | M6/D6.4 | FR-022 | NFR-001, NFR-005 | - | SC-003, SC-004 | D-0027 |
| T06.05 | M6/D6.5 | FR-023, FR-024, FR-025 | NFR-002, NFR-003, NFR-004 | - | SC-003 | D-0028 |
| T06.06 | M6/D6.6 | FR-026, FR-027, FR-028, FR-029, FR-030, FR-031 | - | R-006 | SC-003 | D-0029 |
| T06.07 | M6/D6.7 | FR-040 | - | - | SC-003 | D-0030 |
| T07.01 | M7/D7.1 | - | - | - | SC-001, SC-002, SC-003, SC-004, SC-005 | D-0031 |
| T07.02 | M7/D7.2 | - | NFR-007 | - | SC-003, SC-005 | D-0032 |
| T07.03 | M7/D7.3 | - | NFR-007 | - | SC-005 | D-0033 |
| T07.04 | M7/D7.4 | - | - | - | - | D-0034 |

---

## Execution Log Template

Use this template to track task execution:

```markdown
### Execution Entry: T<PP>.<TT>

| Field | Value |
|-------|-------|
| Task ID | T<PP>.<TT> |
| Started | YYYY-MM-DDTHH:MM:SSZ |
| Completed | YYYY-MM-DDTHH:MM:SSZ |
| Actual Effort | XS / S / M / L / XL |
| Status | PASS / FAIL / BLOCKED |
| Executor | (agent or person) |

**Steps Completed**:
1. [x] Step 1 description
2. [x] Step 2 description
3. [ ] Step 3 description (if incomplete)

**Acceptance Criteria Results**:
1. [x] AC-1: (evidence)
2. [x] AC-2: (evidence)
3. [ ] AC-3: (reason if not met)
4. [x] AC-4: (evidence)

**Validation Results**:
1. [x] V-1: (command output or evidence)
2. [x] V-2: (command output or evidence)

**Notes**: (any deviations, discoveries, or follow-up items)
```

---

## Checkpoint Report Template

Use this template at each checkpoint:

```markdown
### Checkpoint Report: CP-<NN>

| Field | Value |
|-------|-------|
| Checkpoint | CP-<NN> |
| Date | YYYY-MM-DDTHH:MM:SSZ |
| Tasks Completed | N / M |
| Tasks Blocked | N (list IDs) |
| Tasks Failed | N (list IDs) |
| Deliverables Verified | N / M |
| Gate Status | PASS / FAIL |

**Completed Tasks**: T<PP>.<TT>, T<PP>.<TT>, ...

**Blocked Tasks**:
- T<PP>.<TT>: (reason)

**Failed Tasks**:
- T<PP>.<TT>: (reason, recovery plan)

**Risk Updates**:
- R-<NNN>: (status update)

**Gate Decision**: PROCEED / HOLD / ESCALATE
**Justification**: (brief rationale)
```

---

## Feedback Collection Template

Use this template to capture execution feedback:

```markdown
### Feedback: T<PP>.<TT>

| Field | Value |
|-------|-------|
| Task ID | T<PP>.<TT> |
| Feedback Type | BLOCKER / IMPROVEMENT / OBSERVATION |
| Severity | HIGH / MEDIUM / LOW |
| Reporter | (agent or person) |
| Date | YYYY-MM-DDTHH:MM:SSZ |

**Description**: (what was observed)

**Impact**: (how it affects execution)

**Suggested Action**: (proposed resolution)

**Related Tasks**: T<PP>.<TT>, T<PP>.<TT>
```

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 34 |
| Total Phases | 7 |
| Total Deliverables | 34 |
| Total Checkpoints | 8 |
| Effort Distribution | XS: 3, S: 13, M: 14, L: 3, XL: 0 |
| Risk Distribution | Low: 22, Medium: 11, High: 0 |
| Tier Distribution | STRICT: 2, STANDARD: 22, LIGHT: 1, EXEMPT: 9 |
| Estimated Duration | 5-7 working days (single executor) |
| Critical Path | M1 -> M2/M3 -> M5 -> M6 -> M7 |
| Parallelizable Phases | Phase 2 and Phase 3 (after Phase 1) |
