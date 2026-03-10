# Phase 1 — Output Format Switch (P0)

**Goal**: Switch subprocess output format from `text` to `stream-json` and adapt the monitor to parse NDJSON.
**Tier**: STRICT
**Phase Gate**: `build_command()` emits `stream-json`; monitor extracts task IDs and tool names from NDJSON lines; existing unit tests updated to reflect new format.

---

### T01.01 — Switch build_command() to stream-json

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | P0 from debate verdict |
| **Why** | `--output-format text` buffers all stdout until session end, producing 0-byte output files during multi-turn execution. This is the root cause of the false stall appearance. |
| **Effort** | XS |
| **Risk** | Low — single line change, but downstream effects on monitor and executor |
| **Tier** | STRICT |
| **Confidence Bar** | [██████████] 98% |
| **Requires Confirmation** | No |
| **Verification Method** | Unit test: `test_build_command_required_flags` passes with `stream-json` |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/process.py` lines 79-95 — confirm current `build_command()` implementation
2. [EDIT] `process.py:89` — change `"text"` to `"stream-json"` in the `--output-format` argument
3. [VERIFY] no other references to `"text"` output format in the sprint module that need updating

**Acceptance Criteria**:
1. `build_command()` returns a list containing `["--output-format", "stream-json"]`
2. No other references to `--output-format text` remain in `src/superclaude/cli/sprint/`

**Validation**:
1. `uv run pytest tests/sprint/test_process.py::TestClaudeProcess::test_build_command_required_flags -v` — will fail (expected, updated in T03.01)
2. Grep `src/superclaude/cli/sprint/` for `output-format.*text` — zero hits

**Dependencies**: None
**Rollback**: Revert single line change in `process.py:89`

---

### T01.02 — Rewrite monitor._poll_once() for NDJSON parsing

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | P1 from debate verdict (RC2) |
| **Why** | The monitor must parse stream-json NDJSON lines instead of raw text to extract progress signals. Without this, the TUI cannot display real-time task progress. |
| **Effort** | M |
| **Risk** | Medium — must handle partial line writes (thread safety) and malformed JSON gracefully |
| **Tier** | STRICT |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Unit tests for NDJSON parsing with partial writes, malformed lines, and valid stream |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/monitor.py` — full file (130 lines)
2. [EDIT] `_read_new_bytes()` → rename to `_read_new_chunk()` — read raw bytes, return str
3. [EDIT] Add `_line_buffer: str = ""` field to `OutputMonitor.__init__()` for accumulating partial lines across polls
4. [EDIT] Rewrite `_poll_once()`:
   - Read new chunk from file (same stat + seek approach)
   - Prepend `_line_buffer` to chunk
   - Split on `\n`
   - Last element goes back into `_line_buffer` (may be partial)
   - For each complete line: attempt `json.loads()`, extract signals
   - On `json.JSONDecodeError`: skip line (malformed or non-JSON)
   - Update `output_bytes`, `last_growth_time`, `stall_seconds` as before
5. [EDIT] Rewrite `_extract_signals(text)` → `_extract_signals_from_event(event: dict)`:
   - If `event.get("type") == "tool_use"`: extract tool name from `event.get("tool", "")`
   - If `event.get("type") == "assistant"`: search message content for task ID pattern `T\d{2}\.\d{2}`
   - If `event.get("type") == "result"`: extract final result text
   - For all event types: search stringified content for task IDs and file change patterns
6. [PRESERVE] existing regex patterns (`TASK_ID_PATTERN`, `TOOL_PATTERN`, `FILES_CHANGED_PATTERN`) — apply to stringified event content for backward compat
7. [EDIT] `reset()` — also reset `_line_buffer`

**Acceptance Criteria**:
1. `_poll_once()` correctly parses complete NDJSON lines
2. Partial lines buffered across polls (no lost data)
3. Malformed JSON lines skipped without exception
4. Task IDs extracted from assistant messages
5. Tool names extracted from tool_use events
6. `stall_seconds` resets on any new NDJSON line (not just text growth)
7. `reset()` clears line buffer

**Validation**:
1. New test: write 3 NDJSON lines to file, poll, verify state.last_tool_used and state.last_task_id
2. New test: write partial line, poll (no crash), write rest + newline, poll, verify extraction
3. New test: write malformed JSON line, poll (no crash), state unchanged
4. `uv run pytest tests/sprint/test_regression_gaps.py::TestOutputMonitorIdempotency -v` — still passes

**Dependencies**: T01.01
**Rollback**: Revert monitor.py changes; restore text-mode `_extract_signals`

---

### T01.03 — Add last_message_at to MonitorState

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | P1 from debate verdict (RC2) |
| **Why** | With stream-json, the monitor receives events even when the final text output hasn't been produced yet. `last_message_at` tracks when the last NDJSON event arrived, enabling accurate liveness detection distinct from stall detection. |
| **Effort** | S |
| **Risk** | Low |
| **Tier** | STRICT |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Field exists and is updated by monitor |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/models.py` lines 193-222 — `MonitorState` dataclass
2. [EDIT] Add field: `last_event_time: float = field(default_factory=time.monotonic)` after `last_growth_time`
3. [EDIT] Add field: `events_received: int = 0` for TUI display
4. [EDIT] Update `stall_status` property:
   - Use `last_event_time` instead of `last_growth_time` for stall calculation when `events_received > 0`
   - If `events_received == 0` AND `stall_seconds > 120`: return "waiting..." (initial startup)
   - If `events_received > 0` AND `time.monotonic() - last_event_time > 120`: return "STALLED"
   - If `events_received > 0` AND `time.monotonic() - last_event_time > 30`: return "thinking..."
   - Otherwise: return "active"
5. [EDIT] `monitor.py:_poll_once()` — set `self.state.last_event_time = now` and increment `events_received` when processing each NDJSON line

**Acceptance Criteria**:
1. `MonitorState` has `last_event_time` and `events_received` fields
2. `stall_status` distinguishes "no events yet" (startup) from "events stopped" (real stall)
3. During initial startup (0 events, <120s): returns "waiting..." not "STALLED"
4. After events flowing then stopping >120s: returns "STALLED"

**Validation**:
1. Unit test: fresh MonitorState with events_received=0, stall_seconds=90 → "waiting..."
2. Unit test: MonitorState with events_received=50, last_event_time 150s ago → "STALLED"
3. Unit test: MonitorState with events_received=50, last_event_time 10s ago → "active"

**Dependencies**: T01.02
**Rollback**: Revert models.py field additions

---

### T01.04 — Update _determine_phase_status for stream-json output

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | P1 from debate verdict |
| **Why** | The `PASS_NO_REPORT` fallback checks `output_file.stat().st_size > 0`. With stream-json, the output file always has content (NDJSON lines) even if the agent didn't write a result file. This is a minor adjustment but prevents false ERROR status. |
| **Effort** | XS |
| **Risk** | Low — the result file path is unchanged; only the fallback behavior changes |
| **Tier** | STRICT |
| **Confidence Bar** | [█████████-] 92% |
| **Requires Confirmation** | No |
| **Verification Method** | Existing executor tests still pass |
| **MCP Requirements** | None |
| **Fallback Allowed** | No |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/executor.py` lines 202-247 — `_determine_phase_status()`
2. [VERIFY] the result file parsing (lines 223-242) does NOT read from stdout output — it reads the separate `result_file`. Confirm no changes needed here.
3. [ASSESS] the fallback at line 244: `if output_file.exists() and output_file.stat().st_size > 0: return PhaseStatus.PASS_NO_REPORT`. With stream-json, this will almost always be true (NDJSON lines present). This is **correct behavior** — if the agent produced output but no result file, PASS_NO_REPORT is appropriate.
4. [VERIFY] the ERROR fallback at line 247: `return PhaseStatus.ERROR`. This only fires when output_file has 0 bytes AND no result file. With stream-json, 0 bytes means the subprocess never started writing — genuinely an error. No change needed.
5. [DOCUMENT] findings: `_determine_phase_status` requires NO code changes for stream-json. The result file is independent of stdout format.

**Acceptance Criteria**:
1. Confirmed: `_determine_phase_status` needs no code changes
2. All existing executor tests pass without modification (besides the env.pop assertion, handled in Phase 3)
3. Documentation note added as code comment if helpful

**Validation**:
1. `uv run pytest tests/sprint/test_executor.py -v` — all pass
2. `uv run pytest tests/sprint/test_regression_gaps.py::TestDeterminePhaseStatusGaps -v` — all pass

**Dependencies**: T01.01
**Rollback**: N/A (no changes expected)

---

## Phase 1 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| `build_command()` emits `stream-json` | T01.01 | ☐ |
| `_poll_once()` parses NDJSON with partial-line buffering | T01.02 | ☐ |
| `MonitorState` has `last_event_time` and `events_received` | T01.03 | ☐ |
| `stall_status` uses event-based liveness | T01.03 | ☐ |
| `_determine_phase_status` verified — no changes needed | T01.04 | ☐ |
| No regressions in existing test_executor tests | T01.04 | ☐ |
