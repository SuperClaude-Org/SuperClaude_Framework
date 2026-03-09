# Phase 2 -- Executor Integration and Prompt

Wire the scaffold module into the sprint execution pipeline at the correct lifecycle point in `executor.py` and update the agent prompt in `process.py` to reference the scaffold. All changes must preserve backward compatibility — scaffold failure falls back to current `PASS_NO_REPORT` behavior.

### T02.01 -- Add scaffold call to `execute_sprint()` in `executor.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | The scaffold file must exist at `config.result_file(phase)` before the agent subprocess launches to guarantee a result file exists even on max_turns |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0005/evidence.md`

**Deliverables:**
- Scaffold creation call site in `src/superclaude/cli/sprint/executor.py` between `ClaudeProcess(config, phase)` construction and `proc_manager.start()`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/executor.py` and locate the `proc_manager = ClaudeProcess(config, phase)` line and the subsequent `proc_manager.start()` call
2. **[PLANNING]** Verify `config.result_file(phase)` returns the expected path (`results/phase-N-result.md`)
3. **[EXECUTION]** Insert scaffold creation block between `ClaudeProcess` construction and `start()`: import `parse_phase_tasks` and `scaffold_result_file` from `.scaffold`, parse tasks from `phase.file`, create scaffold at `config.result_file(phase)`
4. **[EXECUTION]** Wrap the scaffold block in `try: ... except Exception as exc:` to ensure sprint continues on failure
5. **[VERIFICATION]** Verify the scaffold file exists at `config.result_file(phase)` path before `proc_manager.start()` is called (mock-based test)
6. **[COMPLETION]** Record deliverable D-0005 in execution log

**Acceptance Criteria:**
- Scaffold file exists at `config.result_file(phase)` before `proc_manager.start()` is called (verified via mock subprocess test)
- The scaffold call uses `phase.file` for task parsing and `phase.name or f"Phase {phase.number}"` for the phase name
- Import of scaffold module is inside the try block: `from .scaffold import parse_phase_tasks, scaffold_result_file`
- Existing sprint execution behavior is unchanged when scaffold creation succeeds (no new exit codes, no new status values)

**Validation:**
- `uv run pytest tests/sprint/test_executor.py -v` — existing executor tests still pass
- Evidence: diff of `executor.py` shows scaffold block inserted between `ClaudeProcess()` and `.start()`

**Dependencies:** T01.02 (parse_phase_tasks), T01.04 (scaffold_result_file)
**Rollback:** Remove the scaffold try/except block from `execute_sprint()`
**Notes:** Import inside try block is intentional — scaffold module failure must not prevent sprint execution.

---

### T02.02 -- Implement graceful degradation for scaffold failures in `executor.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | NFR-005 requires scaffold failure to be logged and sprint to continue without scaffold — graceful degradation, not hard failure |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0006/evidence.md`

**Deliverables:**
- Error handling in the scaffold try/except block: dual logging to `debug_log` (JSONL) and `stderr` (operator visibility)

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/debug_logger.py` to understand the `debug_log()` function signature and usage pattern
2. **[PLANNING]** Identify the `_dbg` debug logger variable available in `execute_sprint()` scope
3. **[EXECUTION]** In the except block: call `debug_log(_dbg, "scaffold_error", phase=phase.number, error=str(exc))` for JSONL telemetry
4. **[EXECUTION]** In the except block: call `print(f"[SCAFFOLD] Warning: could not create scaffold for phase {phase.number}: {exc}", file=sys.stderr)` for operator visibility
5. **[VERIFICATION]** Simulate `OSError` in scaffold creation (e.g., mock `scaffold_result_file` to raise), verify sprint continues and both log destinations receive the error
6. **[COMPLETION]** Record deliverable D-0006 in execution log

**Acceptance Criteria:**
- When scaffold creation raises any `Exception`, the sprint continues to `proc_manager.start()` without interruption
- The error is logged via `debug_log(_dbg, "scaffold_error", ...)` (JSONL telemetry channel)
- The error is printed to `sys.stderr` with `[SCAFFOLD] Warning:` prefix (operator visibility channel)
- The sprint outcome for the affected phase falls back to normal classification (no scaffold file → `PASS_NO_REPORT` if agent hits max_turns)

**Validation:**
- `uv run pytest tests/sprint/test_executor.py -v` — existing executor tests still pass, no scaffold-related regressions
- Evidence: simulated `OSError` in scaffold creation produces both debug log entry and stderr output

**Dependencies:** T02.01 (scaffold call site must exist)
**Rollback:** Part of the scaffold try/except block — same rollback as T02.01
**Notes:** Uses broad `except Exception` intentionally to catch any failure mode including import errors.

---

### T02.03 -- Replace Completion Protocol with Reporting Protocol in `build_prompt()`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009, R-010 |
| Why | The monolithic Completion Protocol is the root cause of lost reports — the new Reporting Protocol tells the agent a scaffold exists and instructs incremental updates |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0007/evidence.md`

**Deliverables:**
- Updated `build_prompt()` method in `src/superclaude/cli/sprint/process.py` with "Reporting Protocol" section replacing "Completion Protocol"

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/process.py` and locate the `build_prompt()` method, specifically the "Completion Protocol" section
2. **[PLANNING]** Verify the exact text to remove ("## Completion Protocol") and the replacement text ("## Reporting Protocol") from the release spec Section D4
3. **[EXECUTION]** Remove the "Completion Protocol" section from `build_prompt()` output
4. **[EXECUTION]** Insert the "Reporting Protocol" section: (a) "A scaffold report already exists at {result_file}", (b) incremental update instructions with "you may", (c) mandatory finalization with "you MUST finalize", (d) EXIT_RECOMMENDATION instructions
5. **[EXECUTION]** Verify `{result_file}` placeholder resolves to `config.result_file(self.phase)` in the formatted prompt
6. **[VERIFICATION]** Assert prompt output contains "scaffold report already exists", "you MUST finalize", "EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT" and does NOT contain "Completion Protocol"
7. **[COMPLETION]** Record deliverable D-0007 in execution log

**Acceptance Criteria:**
- `build_prompt()` output contains the string `"scaffold report already exists"` (scaffold awareness)
- `build_prompt()` output contains `"you MUST finalize"` (mandatory final report)
- `build_prompt()` output does NOT contain `"Completion Protocol"` (old section fully removed)
- `build_prompt()` output references the correct result file path from `config.result_file(self.phase)`

**Validation:**
- `uv run pytest tests/sprint/test_process.py -v` — existing process tests still pass, plus new prompt content assertions
- Evidence: diff of `process.py` shows Completion Protocol section replaced with Reporting Protocol section

**Dependencies:** None within Phase 2 (modifies `process.py` independently of `executor.py` changes)
**Rollback:** Restore original "Completion Protocol" section in `build_prompt()`
**Notes:** Step 1 uses "you may" (best-effort incremental). Step 2 uses "you MUST" (mandatory final). This distinction is deliberate per Nygard review.

---

### Checkpoint: End of Phase 2

**Purpose:** Verify executor integration and prompt update are correct and backward-compatible before writing tests.

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-END.md`

**Verification:**
- `executor.py` contains scaffold creation block between `ClaudeProcess(config, phase)` and `proc_manager.start()`
- `process.py` `build_prompt()` output contains "Reporting Protocol" and does not contain "Completion Protocol"
- Existing sprint tests pass without modification: `uv run pytest tests/sprint/ -v`

**Exit Criteria:**
- All 3 deliverables (D-0005 through D-0007) are implemented
- No existing test regressions in `tests/sprint/test_executor.py` or `tests/sprint/test_process.py`
- Scaffold failure in executor produces dual-channel logging (debug_log + stderr)
