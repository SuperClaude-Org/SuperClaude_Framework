# Phase 4 — Integration Validation

**Goal**: Validate the complete fix through manual testing and automated E2E checks.
**Tier**: STANDARD
**Phase Gate**: Sprint CLI successfully executes a 1-phase sprint with stream-json output; TUI shows live progress; no false "STALLED" indicator.

---

### T04.01 — Manual smoke test: simple 1-phase sprint

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | The ultimate validation: does the sprint CLI actually work end-to-end now? |
| **Effort** | S |
| **Risk** | Medium — requires `claude` binary and API access |
| **Tier** | STANDARD |
| **Confidence Bar** | [████████=-] 85% |
| **Requires Confirmation** | No |
| **Verification Method** | Sprint completes Phase 1 with PASS status; output file contains NDJSON |
| **MCP Requirements** | None (uses native claude) |
| **Fallback Allowed** | Yes — if claude binary unavailable, verify with mock test |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [CREATE] minimal test sprint in `/tmp/sprint-smoke-test/`:
   - `tasklist-index.md` with 1 phase reference
   - `phase-1-tasklist.md` with a single trivial EXEMPT task:
     ```markdown
     # Phase 1 — Smoke Test
     ### T01.01 — Verify sprint execution
     **Tier**: EXEMPT
     **Effort**: XS
     **Steps**:
     1. [WRITE] a file `results/phase-1-result.md` containing:
        EXIT_RECOMMENDATION: CONTINUE
     **Acceptance Criteria**:
     1. Result file exists with CONTINUE signal
     **Validation**:
     1. File exists
     **Dependencies**: None
     ```
2. [RUN] `superclaude sprint run /tmp/sprint-smoke-test/tasklist-index.md --no-tmux --max-turns 5`
3. [OBSERVE] TUI: does it show "waiting..." initially, then "active" with events, then phase completion?
4. [CHECK] `results/phase-1-output.txt` — contains NDJSON lines (not plain text)
5. [CHECK] `results/phase-1-result.md` — contains EXIT_RECOMMENDATION: CONTINUE
6. [CHECK] `execution-log.jsonl` — phase 1 status is "pass"

**Acceptance Criteria**:
1. Sprint completes without user intervention (no manual kill needed)
2. TUI shows progress events (not perpetual "STALLED")
3. Output file contains `{"type":` JSON lines
4. Phase status is PASS (not ERROR or TIMEOUT)

**Validation**:
1. Exit code 0
2. execution-log.jsonl shows `"status": "pass"`
3. Output file size > 0 bytes during execution (not just at end)

**Dependencies**: T03.04
**Rollback**: N/A (test only)

---

### T04.02 — Verify TUI stall detection accuracy

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Confirm the TUI no longer shows "STALLED" during normal multi-turn operation |
| **Effort** | S |
| **Risk** | Low |
| **Tier** | STANDARD |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | TUI transitions: "waiting..." → "active" → phase complete |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [OBSERVE] during T04.01 sprint execution, watch TUI status transitions
2. [VERIFY] initial state shows "waiting..." (dim style, not alarming)
3. [VERIFY] after first NDJSON event arrives, status shows "active" (green)
4. [VERIFY] "STALLED" (red blink) never appears during normal execution
5. [VERIFY] phase duration column shows elapsed time, not stall seconds

**Acceptance Criteria**:
1. "STALLED" never appears during a successful 1-phase sprint
2. "waiting..." appears during startup (first ~5-15 seconds)
3. "active" appears once events flow
4. Duration shows elapsed seconds, not stall counter

**Validation**:
1. Screen observation or screenshot during smoke test
2. No "STALLED" in any captured output

**Dependencies**: T04.01
**Rollback**: N/A

---

### T04.03 — Verify backward compatibility: --output-format flag

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Ensure stream-json works with the installed claude binary version. If not, document the minimum required version. |
| **Effort** | XS |
| **Risk** | Low |
| **Tier** | STANDARD |
| **Confidence Bar** | [█████████-] 90% |
| **Requires Confirmation** | No |
| **Verification Method** | claude --print --output-format stream-json produces valid NDJSON |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [RUN] `claude --version` — record version
2. [RUN] `env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT claude --print --output-format stream-json --max-turns 1 --dangerously-skip-permissions -p "Say hello"` — verify NDJSON output
3. [VERIFY] output contains `{"type":` prefixed JSON lines
4. [DOCUMENT] minimum claude version required for stream-json support

**Acceptance Criteria**:
1. `stream-json` output format works with installed claude version
2. Output is valid NDJSON (one JSON object per line)
3. If stream-json is NOT supported, document and consider P2 fallback (feature detection)

**Validation**:
1. At least one `{"type":` line in output
2. Each line is valid JSON

**Dependencies**: None
**Rollback**: N/A

---

### T04.04 — Sprint completion: clean up and document

| Field | Value |
|---|---|
| **Roadmap Item ID(s)** | — |
| **Why** | Clean up temporary test artifacts; document what was changed and why for commit message and PR description. |
| **Effort** | XS |
| **Risk** | None |
| **Tier** | STANDARD |
| **Confidence Bar** | [██████████] 100% |
| **Requires Confirmation** | No |
| **Verification Method** | No temp files left; summary written |
| **MCP Requirements** | None |
| **Fallback Allowed** | Yes |
| **Sub-Agent Delegation** | No |
| **Deliverable IDs** | — |
| **Artifacts** | — |

**Steps**:
1. [CLEAN] Remove `/tmp/sprint-smoke-test/` if created during T04.01
2. [VERIFY] `git diff --stat` — confirm only expected files modified:
   - `src/superclaude/cli/sprint/process.py` (format + comment)
   - `src/superclaude/cli/sprint/monitor.py` (NDJSON rewrite)
   - `src/superclaude/cli/sprint/models.py` (new fields)
   - `src/superclaude/cli/sprint/tui.py` (display updates)
   - `tests/sprint/test_process.py` (assertion updates)
   - `tests/sprint/test_regression_gaps.py` (assertion update)
   - `tests/sprint/test_monitor_stream.py` (new file)
3. [VERIFY] no unrelated changes leaked in
4. [RUN] `uv run pytest tests/sprint/ -v` — final confirmation: 0 failures
5. [SUMMARIZE] changes for commit message:
   - Root cause: `--output-format text` buffered all stdout, TUI showed false "STALLED"
   - Fix: switched to `stream-json` with NDJSON monitor, event-based stall detection
   - Source: adversarial debate verdict in `.dev/releases/current/v2.03-CLI-Sprint-diag/`

**Acceptance Criteria**:
1. No temporary files left
2. Only expected files modified
3. Full test suite passes
4. Summary ready for commit

**Validation**:
1. `uv run pytest tests/sprint/ -v` — 0 failures
2. `git diff --stat` — matches expected file list
3. No files in git diff that aren't in the expected list above

**Dependencies**: T04.01, T04.02, T04.03
**Rollback**: N/A

---

## Phase 4 Checkpoint

| Criterion | Task | Status |
|---|---|---|
| Smoke test sprint completes with PASS | T04.01 | ☐ |
| TUI shows "waiting..." → "active" → complete (no false STALLED) | T04.02 | ☐ |
| stream-json verified with installed claude version | T04.03 | ☐ |
| Only expected files modified | T04.04 | ☐ |
| Final test suite pass: 0 failures | T04.04 | ☐ |
| No temp files or artifacts left | T04.04 | ☐ |

---

## Sprint Completion Criteria

| Gate | Requirement | Verified |
|---|---|---|
| Root cause addressed | `--output-format stream-json` replaces `text` | ☐ |
| Monitor rewritten | NDJSON parsing with partial-line buffering | ☐ |
| Stall detection accurate | Event-based liveness, not byte-growth | ☐ |
| TUI informative | Shows events, elapsed time, last tool/task | ☐ |
| Tests comprehensive | ≥12 new NDJSON tests + all existing pass | ☐ |
| No regressions | `uv run pytest tests/sprint/ -v` — 0 failures | ☐ |
| E2E validated | Sprint completes without false stall | ☐ |
| env.pop preserved | Defensive hygiene kept with accurate comment | ☐ |
