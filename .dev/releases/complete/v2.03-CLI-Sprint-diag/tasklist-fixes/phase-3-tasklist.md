# Phase 3 — Test Updates

**Goal**: Update all existing tests to pass with stream-json output format; add new tests for NDJSON monitor parsing.
**Tier**: STRICT
**Phase Gate**: `uv run pytest tests/sprint/ -v` passes with 0 failures.

---

### T03.01 — Update test_process.py assertions for stream-json and env.pop

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Two tests assert the old behavior: `"text" in cmd` and `env["CLAUDECODE"] == ""`. Both must be updated to match the new code. |
| **Effort** | XS |
| **Risk** | Low — straightforward assertion changes |
| **Tier** | STRICT |
| **Confidence Bar** | [██████████] 98% |
| **Requires Confirmation** | No |
| **Verification Method** | `uv run pytest tests/sprint/test_process.py -v` passes |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `tests/sprint/test_process.py` — full file
2. [EDIT] `test_build_command_required_flags` (line 36):
   - Change `assert "text" in cmd` → `assert "stream-json" in cmd`
3. [EDIT] `test_build_env_claudecode` (lines 59-64):
   - Change entire test body:
     ```python
     def test_build_env_removes_claudecode(self):
         config = _make_config()
         proc = ClaudeProcess(config, config.phases[0])
         env = proc.build_env()
         assert "CLAUDECODE" not in env
         assert "CLAUDE_CODE_ENTRYPOINT" not in env
     ```
4. [ADD] New test `test_build_command_includes_partial_messages`:
   ```python
   def test_build_command_includes_partial_messages(self):
       config = _make_config()
       proc = ClaudeProcess(config, config.phases[0])
       cmd = proc.build_command()
       assert "--include-partial-messages" in cmd
   ```
5. [RUN] `uv run pytest tests/sprint/test_process.py -v`

**Acceptance Criteria**:
1. All tests in `test_process.py` pass
2. `stream-json` assertion present
3. `CLAUDECODE not in env` assertion present
4. `--include-partial-messages` assertion present

**Validation**:
1. `uv run pytest tests/sprint/test_process.py -v` — 0 failures

**Dependencies**: T01.01, T02.03, T02.04
**Rollback**: Revert test changes

---

### T03.02 — Update test_regression_gaps.py env assertion

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | `TestClaudeProcessEdgeCases::test_build_env_preserves_existing_vars` asserts `env["CLAUDECODE"] == ""` which will fail after the env.pop fix. |
| **Effort** | XS |
| **Risk** | Low |
| **Tier** | STRICT |
| **Confidence Bar** | [██████████] 98% |
| **Requires Confirmation** | No |
| **Verification Method** | `uv run pytest tests/sprint/test_regression_gaps.py -v` passes |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `tests/sprint/test_regression_gaps.py` lines 348-354 — `test_build_env_preserves_existing_vars`
2. [EDIT] Change assertion:
   - Remove: `assert env["CLAUDECODE"] == ""`
   - Add: `assert "CLAUDECODE" not in env`
   - Add: `assert "CLAUDE_CODE_ENTRYPOINT" not in env`
   - Keep: `assert "PATH" in env` (existing, still valid)
3. [RUN] `uv run pytest tests/sprint/test_regression_gaps.py -v`

**Acceptance Criteria**:
1. All tests in `test_regression_gaps.py` pass
2. Env assertion reflects env.pop behavior

**Validation**:
1. `uv run pytest tests/sprint/test_regression_gaps.py -v` — 0 failures

**Dependencies**: T02.04
**Rollback**: Revert test changes

---

### T03.03 — Add NDJSON monitor tests

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The monitor rewrite (T01.02) has no tests yet. NDJSON parsing with partial-line buffering is the riskiest change and needs thorough test coverage. |
| **Effort** | M |
| **Risk** | Low — tests only |
| **Tier** | STRICT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | New test file passes; covers happy path, partial lines, malformed JSON, empty events |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | `tests/sprint/test_monitor_stream.py` (new file) |

**Steps**:
1. [WRITE] `tests/sprint/test_monitor_stream.py` with the following test classes:

**TestNDJSONParsing**:
- `test_complete_ndjson_lines_parsed`: Write 3 valid NDJSON lines, poll, verify events_received=3
- `test_tool_use_event_extracts_tool_name`: Write `{"type":"tool_use","tool":"Read"}`, verify `state.last_tool_used == "Read"`
- `test_assistant_message_extracts_task_id`: Write `{"type":"assistant","message":{"content":"Working on T01.03"}}`, verify `state.last_task_id == "T01.03"`
- `test_result_event_parsed`: Write `{"type":"result","result":"Done"}`, verify events_received incremented

**TestPartialLineBuffering**:
- `test_partial_line_buffered_across_polls`: Write `{"type":"tool_` (partial), poll (no crash, no new events), write `use","tool":"Edit"}\n`, poll, verify extraction
- `test_multiple_partial_writes_accumulate`: Write in 3 chunks, only complete on last, verify single event extracted

**TestMalformedJSON**:
- `test_malformed_json_line_skipped`: Write `not-json\n`, poll, verify no crash, events_received=0
- `test_malformed_then_valid_line`: Write `bad\n{"type":"tool_use","tool":"Bash"}\n`, poll, verify tool extracted from second line
- `test_empty_line_skipped`: Write `\n\n{"type":"result"}\n`, poll, verify events_received=1

**TestStallDetection**:
- `test_events_reset_stall_seconds`: Write event, poll, verify stall_seconds near 0
- `test_no_events_increases_stall`: Poll with no new data, verify stall_seconds > 0
- `test_stall_status_waiting_during_startup`: Fresh state, events_received=0, stall_seconds=90 → "waiting..."
- `test_stall_status_stalled_after_events_stop`: state with events_received=50, last_event_time 150s ago → "STALLED"

2. [RUN] `uv run pytest tests/sprint/test_monitor_stream.py -v`

**Acceptance Criteria**:
1. ≥12 tests covering NDJSON parsing, partial buffering, malformed JSON, stall detection
2. All pass
3. Tests use `tmp_path` fixture for file I/O
4. Tests do not require real `claude` binary

**Validation**:
1. `uv run pytest tests/sprint/test_monitor_stream.py -v` — 0 failures
2. `uv run pytest tests/sprint/test_monitor_stream.py --cov=superclaude.cli.sprint.monitor` — coverage of `_poll_once`, `_extract_signals_from_event`, `_line_buffer` handling

**Dependencies**: T01.02, T01.03
**Rollback**: Delete test file

---

### T03.04 — Full test suite pass

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Gate check: ALL sprint tests must pass before integration validation. Any silent regression must be caught here. |
| **Effort** | S |
| **Risk** | Medium — E2E tests may need mock output format updates |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | `uv run pytest tests/sprint/ -v` — 0 failures |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [RUN] `uv run pytest tests/sprint/ -v --tb=short`
2. [INSPECT] any failures — categorize as:
   - Expected (assertion needs updating for new format) → fix
   - Unexpected (real regression) → investigate and fix
3. [FIX] any remaining failures
4. [RUN] `uv run pytest tests/sprint/ -v` — confirm 0 failures
5. [RUN] `uv run pytest tests/sprint/ --cov=superclaude.cli.sprint -v` — check coverage

**Acceptance Criteria**:
1. `uv run pytest tests/sprint/ -v` — 0 failures
2. No tests skipped or xfailed as workarounds
3. Coverage of `process.py`, `monitor.py`, `models.py`, `tui.py` ≥ existing baseline

**Validation**:
1. `uv run pytest tests/sprint/ -v` — 0 failures, 0 errors
2. No `assert "text"` assertions remaining in test suite
3. No `assert env["CLAUDECODE"] == ""` assertions remaining

**Dependencies**: T03.01, T03.02, T03.03
**Rollback**: N/A (this is a verification task)

---

## Phase 3 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| test_process.py updated and passing | T03.01 | ☐ |
| test_regression_gaps.py updated and passing | T03.02 | ☐ |
| test_monitor_stream.py created with ≥12 tests | T03.03 | ☐ |
| Full suite `uv run pytest tests/sprint/ -v` — 0 failures | T03.04 | ☐ |
| No skipped/xfailed workarounds | T03.04 | ☐ |
