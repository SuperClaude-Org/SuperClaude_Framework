# Phase 2 — TUI & Stall Detection (P1)

**Goal**: Update TUI to display real-time progress from stream-json events and show accurate stall detection.
**Tier**: STANDARD
**Phase Gate**: TUI shows event count, last tool used, last task ID from live NDJSON stream; "STALLED" only triggers on genuine event cessation.

---

### T02.01 — Update TUI active panel for stream-json signals

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | P1 from debate verdict (RC2) |
| **Why** | The TUI active panel currently shows `Output size: 0 B (+0.0 B/s)` during multi-turn sessions, which looks broken. With stream-json, the panel should show meaningful progress: events received, last tool, last task ID. |
| **Effort** | S |
| **Risk** | Low — cosmetic changes to TUI rendering |
| **Tier** | STANDARD |
| **Confidence Bar** | [█████████-] 92% |
| **Requires Confirmation** | No |
| **Verification Method** | Visual inspection of rendered panel; field values populated |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/tui.py` lines 187-219 — `_build_active_panel()`
2. [EDIT] Update the `lines` list in `_build_active_panel()`:
   - Change `"Status:  RUNNING -- [{stall_style}]{stall_display}[/]"` — keep but use new stall_status logic (already updated in T01.03)
   - Change `"Output size:   {ms.output_size_display}  (+{ms.growth_rate_bps:.1f} B/s)"` → `"Events:        {ms.events_received}  ({ms.output_size_display})"`
   - Keep `"Last task:     {ms.last_task_id or '-'}"` — unchanged
   - Keep `"Last tool:     {ms.last_tool_used or '-'}"` — unchanged
   - Keep `"Files changed: {ms.files_changed}"` — unchanged
3. [EDIT] Update stall style mapping to use revised thresholds:
   - `"waiting..."` → style `"dim"` (not alarming during startup)
   - `"STALLED"` → style `"bold red blink"` (unchanged — genuine stall)
   - `"thinking..."` → style `"yellow"` (unchanged)
   - `"active"` → style `"green"` (unchanged)

**Acceptance Criteria**:
1. Active panel shows `Events: N` instead of `Output size + B/s`
2. Stall display uses event-based liveness from T01.03
3. "waiting..." style is dim (not alarming) during initial startup
4. All existing TUI visual elements preserved (phase table, progress bar, header)

**Validation**:
1. Manual: instantiate `SprintTUI` with mock config, call `_render()`, inspect output
2. No import errors in tui.py

**Dependencies**: T01.03
**Rollback**: Revert tui.py changes

---

### T02.02 — Update phase table duration column for running phases

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | P1 from debate verdict |
| **Why** | The phase table shows `stall_seconds` as the duration for running phases (tui.py:156). This was the direct visual trigger for user alarm — seeing "89s" next to a phase that appeared stalled. Should show elapsed time instead. |
| **Effort** | XS |
| **Risk** | Low |
| **Tier** | STANDARD |
| **Confidence Bar** | [█████████-] 95% |
| **Requires Confirmation** | No |
| **Verification Method** | Duration column shows elapsed time, not stall seconds |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/tui.py` lines 148-161 — phase table duration logic
2. [EDIT] Change duration display for RUNNING phases:
   - Current: `f"{int(self.monitor_state.stall_seconds)}s"` — shows stall timer (misleading)
   - New: Show elapsed time since phase started. Since the TUI receives `sprint_result` which contains `started_at` for each phase_result, calculate elapsed. However, for RUNNING phases, there may not be a phase_result yet. Use `monitor_state.last_growth_time` as a proxy, OR track phase start time in the TUI.
   - Simplest approach: add `phase_started_at: float = field(default_factory=time.monotonic)` to `MonitorState` in models.py, set it in `reset()`. Display `int(time.monotonic() - ms.phase_started_at)` as elapsed.
3. [EDIT] `models.py` — add `phase_started_at: float = field(default_factory=time.monotonic)` to `MonitorState`
4. [EDIT] `monitor.py:reset()` — set `self.state.phase_started_at = time.monotonic()`
5. [EDIT] `tui.py` — duration for RUNNING: `f"{int(time.monotonic() - self.monitor_state.phase_started_at)}s"`

**Acceptance Criteria**:
1. Running phase shows elapsed time (e.g., "45s", "2m 30s") not stall timer
2. Completed phases still show actual duration from PhaseResult

**Validation**:
1. Create MonitorState, wait 2 seconds, check `phase_started_at` is reasonable
2. TUI renders without error

**Dependencies**: T01.03
**Rollback**: Revert tui.py and models.py changes

---

### T02.03 — Add --include-partial-messages flag

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — (enhancement discovered during diagnosis) |
| **Why** | Claude CLI supports `--include-partial-messages` which provides streaming token-by-token output within stream-json. This gives the finest-grained liveness signal. Without it, events only arrive at tool boundaries. |
| **Effort** | XS |
| **Risk** | Low — additive flag, no behavior change if claude binary doesn't support it |
| **Tier** | STANDARD |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | Flag present in command; no error from claude binary |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes — flag is ignored by older claude binaries |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/process.py` lines 79-95 — `build_command()`
2. [EDIT] Add `"--include-partial-messages"` to the command list, after `"stream-json"`
3. [VERIFY] `claude --help` confirms the flag exists and is compatible with `--output-format stream-json`

**Acceptance Criteria**:
1. `build_command()` includes `--include-partial-messages`
2. Flag is positioned after `--output-format stream-json`

**Validation**:
1. `claude --help | grep include-partial-messages` — confirms flag exists
2. Unit test: `build_command()` output contains `--include-partial-messages`

**Dependencies**: T01.01
**Rollback**: Remove single flag from command list

---

### T02.04 — Update build_env docstring and comment

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — (hygiene from debate verdict "Status of Applied Fix" section) |
| **Why** | The `build_env()` function was modified during initial (incorrect) diagnosis. The current code (`env.pop`) is correct hygiene per the debate verdict. The docstring/comment should accurately describe WHY we pop these vars — not because of the stall bug, but for defense-in-depth against nested session detection. |
| **Effort** | XS |
| **Risk** | None |
| **Tier** | STANDARD |
| **Confidence Bar** | [██████████] 100% |
| **Requires Confirmation** | No |
| **Verification Method** | Comment is accurate |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [READ] `src/superclaude/cli/sprint/process.py` lines 97-101 — current `build_env()` with the already-applied env.pop fix
2. [EDIT] Update the comment to accurately reflect the debate verdict findings:
   - Old comment: `"Claude Code checks for the *existence* of CLAUDECODE to detect nested sessions. Setting it to "" is not enough — we must remove it entirely."`
   - New comment: `"Remove Claude Code session markers so the child process does not detect itself as nested. The CLAUDECODE='1' guard uses strict equality, so CLAUDECODE='' also works, but removing the vars entirely is cleaner defense-in-depth."`

**Acceptance Criteria**:
1. Comment accurately reflects that `==="1"` strict equality is the actual guard
2. No claim that empty string triggers the guard (that was the incorrect diagnosis)
3. Justification is "defense-in-depth" not "bug fix"

**Validation**:
1. Read the comment — factually correct per debate verdict findings

**Dependencies**: None
**Rollback**: N/A

---

## Phase 2 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| TUI active panel shows `Events: N` | T02.01 | ☐ |
| Stall display uses "waiting..." for startup | T02.01 | ☐ |
| Phase table shows elapsed time, not stall timer | T02.02 | ☐ |
| `--include-partial-messages` in command | T02.03 | ☐ |
| `build_env()` comment is factually accurate | T02.04 | ☐ |
