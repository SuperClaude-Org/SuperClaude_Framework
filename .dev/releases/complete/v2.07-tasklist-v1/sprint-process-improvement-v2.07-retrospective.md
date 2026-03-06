# Sprint Process Improvement Analysis: v2.07-tasklist-v1 Retrospective

**Date**: 2026-03-05
**Sprint**: v2.07-tasklist-v1
**Scope**: 39 tasks across 4 phases, executed in ~23 minutes
**Outcome**: All 4 phases reported as PASS by runner; Phase 3 was actually PARTIAL (8/9)

---

## Executive Summary

The first real-world usage of the sprint runner completed successfully but exposed several gaps in telemetry fidelity, partial-result handling, and post-sprint validation. The tasklist quality was high -- Claude Code executed all 39 tasks with clear evidence trails. The most significant finding is that the runner classified Phase 3 as PASS despite the result file containing `status: PARTIAL` with 1 STRICT failure, because the Claude agent wrote `EXIT_RECOMMENDATION: CONTINUE` which takes precedence in the current parsing logic.

---

## 1. Sprint Runner Improvements

### 1.1 PARTIAL Phase Results Are Silently Promoted to PASS

**Priority**: P0 (Critical)
**Evidence**: Phase 3 result file has `status: PARTIAL` (8/9 tasks passed, 1 STRICT failure: T03.08). The JSONL log records `"status": "pass"` because `_determine_phase_status()` in `executor.py` checks `EXIT_RECOMMENDATION: CONTINUE` before `status: PARTIAL`, and CONTINUE wins.

**Current behavior** (executor.py lines 307-352):
1. Check exit code (124 = timeout, non-zero = error)
2. Check `EXIT_RECOMMENDATION: HALT` -- returns HALT
3. Check `EXIT_RECOMMENDATION: CONTINUE` -- returns PASS
4. Check `status: PASS` -- returns PASS
5. Check `status: FAIL` -- returns HALT
6. Check `status: PARTIAL` -- returns HALT
7. Fallback: PASS_NO_SIGNAL

**Problem**: Step 3 fires before step 6. When Claude writes both `EXIT_RECOMMENDATION: CONTINUE` and `status: PARTIAL`, the phase is classified as PASS. This is architecturally wrong -- a PARTIAL result should never be silently promoted.

**Recommendation**: Introduce a `PhaseStatus.PARTIAL` enum value that is classified as `is_success = True` (so the sprint continues) but is tracked distinctly in telemetry. The parsing logic should:
1. First, check for PARTIAL status in frontmatter
2. If PARTIAL + CONTINUE: return `PhaseStatus.PARTIAL` (continue, but log honestly)
3. If PARTIAL + HALT: return `PhaseStatus.HALT`
4. If PARTIAL without EXIT_RECOMMENDATION: return `PhaseStatus.HALT` (safe default)

This preserves the current behavior (sprint continues) while fixing the telemetry lie (status logged as "pass" when it was not).

**Model changes** (models.py):
- Add `PhaseStatus.PARTIAL = "partial"` to the enum
- Add PARTIAL to `is_success` (so sprint continues)
- Add PARTIAL to `is_terminal`
- Do NOT add to `is_failure`

**JSONL impact**: `"status": "partial"` instead of `"status": "pass"` -- downstream consumers can distinguish clean passes from partial ones.

---

### 1.2 files_changed Is Always 0

**Priority**: P1 (Important)
**Evidence**: All 4 phase JSONL entries show `"files_changed": 0`. Phase 1 created 6 files. Phase 2 modified/created 6 files. Phase 3 ran `make sync-dev` which synced dozens. Phase 4 was verification-only (legitimately 0).

**Root cause**: The `FILES_CHANGED_PATTERN` regex in `monitor.py` line 28 looks for patterns like `modified foo.py` or `created bar.js` in the raw output stream. However, Claude Code's `--output-format stream-json` emits structured NDJSON events, not human-readable prose. The Write/Edit tool_use events contain file paths in structured JSON fields, not in the `"modified path.py"` text pattern the regex expects.

**Recommendation**: In `_extract_signals_from_event()`, add structured extraction for tool_use events where the tool is Write, Edit, MultiEdit, or similar. Extract the `file_path` or `path` field from the tool input. Example:

```python
if event_type == "tool_use" and event.get("tool") in {"Write", "Edit", "MultiEdit"}:
    # Extract file path from tool input
    tool_input = event.get("input", {})
    if isinstance(tool_input, dict):
        path = tool_input.get("file_path") or tool_input.get("path", "")
        if path:
            self._seen_files.add(path)
```

Additionally, check `tool_result` events for success confirmations. The regex fallback should remain as a secondary extraction method for non-structured output.

---

### 1.3 last_task_id Accuracy

**Priority**: P2 (Recommended)
**Evidence**: Phase 4 JSONL shows `"last_task_id": "T03.08"` -- a task from Phase 3, not Phase 4. Phase 4 has tasks T04.01 through T04.10. The monitor's regex `T\d{2}\.\d{2}` matched T03.08 appearing in Phase 4's output because Phase 4 references the Phase 3 failure in its verification text.

**Root cause**: The `TASK_ID_PATTERN` regex greedily matches any `T##.##` pattern in the output, including backward references to earlier phases. It takes the last match, which in Phase 4's case was a reference to T03.08 in the inherited issues discussion.

**Recommendation**: This is a fundamental limitation of regex-based extraction from unstructured output. Two mitigation approaches:

1. **Phase-scoped filtering** (simple): Only accept task IDs where the phase prefix matches the current phase. E.g., during Phase 4, only accept `T04.XX`. This requires the monitor to know the current phase number.

2. **Recency-weighted matching** (better): Track the most recent task ID that appears in a "working on" or "starting" context versus a "referencing" context. This is harder but more robust.

The simpler approach (option 1) would catch the observed problem. Pass `phase.number` to the monitor on reset, and filter accordingly.

---

### 1.4 Per-Task Granularity in JSONL

**Priority**: P2 (Recommended)
**Evidence**: The JSONL log has only 4 data points for 39 tasks -- one `phase_complete` event per phase. There is no visibility into which tasks passed/failed within a phase without reading the result markdown files.

**Recommendation**: After a phase completes, parse the result file's per-task table and emit individual `task_complete` events to JSONL:

```json
{"event": "task_complete", "phase": 3, "task_id": "T03.08", "status": "fail", "tier": "STRICT", "title": "Verify skill NOT installed..."}
```

This enables:
- Automated dashboards without markdown parsing
- Per-task duration tracking (if Claude reports timestamps)
- Failure pattern analysis across sprints
- Machine-readable success criteria verification

**Implementation**: Add a `_parse_result_file_tasks()` function to executor.py that extracts the per-task status table from the result markdown using a simple regex on the markdown table rows. Call it after `_determine_phase_status()` and before writing the phase_complete JSONL entry.

---

### 1.5 Error File Handling

**Priority**: P3 (Low)
**Evidence**: All 4 error files are 0 bytes. This is correct behavior -- `--output-format stream-json` routes stderr through the NDJSON stream rather than a separate stderr file. The error files are created by the process manager's stderr redirection but receive no content.

**Current behavior**: `error_bytes` is correctly computed and logged as 0. The files exist but are empty.

**Recommendation**: No immediate fix needed. However, document that with stream-json output, stderr content appears within the NDJSON stream (in `system` type events) rather than the error file. Consider:
1. Extracting error/warning events from NDJSON and writing them to the error file as a post-processing step
2. Or removing the error file creation entirely and noting in telemetry that errors are inline

---

## 2. Process Improvements

### 2.1 Was 50 Max Turns Sufficient?

**Priority**: P2 (Recommended)
**Evidence**: The sprint completed in ~23 minutes total across all 4 phases. Phase durations: 1m32s, 8m48s, 4m58s, 7m58s. No timeout or turn-limit issues observed. The 50-turn limit applied per-phase to the Claude subprocess.

**Assessment**: 50 turns was more than sufficient for this sprint. Phase 2 (16 tasks, heaviest implementation) completed in under 9 minutes. However, this was a relatively clean execution with well-structured tasks.

**Recommendation**: 50 turns is a reasonable default for phases with up to 16 tasks. For larger phases (20+ tasks) or tasks requiring complex debugging, consider:
- Making max_turns configurable per-phase in the tasklist index
- A formula like `max_turns = max(50, tasks_in_phase * 4)`
- Logging actual turn count per phase in JSONL for future calibration

---

### 2.2 Was the 4-Phase Structure Optimal?

**Priority**: P2 (Recommended)
**Evidence**: Phase distribution: P1=4 tasks, P2=16 tasks, P3=9 tasks, P4=10 tasks. Phase 2 was the largest by far (41% of tasks) and took the longest wall-clock time (38% of total). The structure followed a logical progression: foundation, implementation, integration, validation.

**Assessment**: The 4-phase structure worked well for 39 tasks. The phase boundaries created natural checkpoints. However, Phase 2 was disproportionately large.

**Recommendation**:
- For sprints with >40 tasks, consider splitting the largest phase when it exceeds 12-15 tasks
- The tasklist generator should have a soft cap of ~12 tasks per phase
- Phase 2 could have been split into "Command Implementation" (T02.01-T02.08) and "Skill Implementation" (T02.09-T02.16), creating a 5-phase sprint
- Document a guideline: phases should contain 4-12 tasks for optimal Claude Code execution

---

### 2.3 Inter-Phase Checkpoints

**Priority**: P3 (Low)
**Evidence**: Each phase result file includes a "Blockers for Next Phase" section and checkpoint verification. Phase 3 explicitly recommended `EXIT_RECOMMENDATION: CONTINUE` despite T03.08 failing, with clear rationale that the failure was pre-existing and non-blocking.

**Assessment**: The current checkpoint mechanism works well. Claude Code produces detailed rationale for continue/halt decisions. The problem is on the runner side (see 1.1) -- the runner does not surface PARTIAL status.

**Recommendation**: No structural change needed to inter-phase checkpoints. The result file format with frontmatter status + EXIT_RECOMMENDATION + blockers section is effective. The improvement should be on the runner's parsing side (see 1.1).

---

### 2.4 Pre-Existing Failures

**Priority**: P1 (Important)
**Evidence**: Phase 3 encountered two categories of pre-existing issues:
1. `make verify-sync` exit code 2 due to `sc-forensic-qa-protocol` drift (unrelated to sprint)
2. `make lint-architecture` exit code 2 due to 2 pre-existing lint errors (unrelated to sprint)
3. T03.08: `_has_corresponding_command()` bug affecting all `-protocol` skills (pre-existing)

Claude Code handled these well -- it scoped its pass/fail assessments to the sprint's own work and clearly documented pre-existing issues. But the non-zero exit codes could have caused false failures if the tasks had been structured differently.

**Recommendation**:
1. **Pre-flight scan**: Before sprint execution, run a baseline of `make lint-architecture`, `make verify-sync`, and `uv run pytest` to capture known failures. Store as `baseline-failures.json` in the results directory.
2. **Delta assessment**: Tasks that run validation commands should compare against the baseline, not against zero-error expectations.
3. **Tasklist guidance**: The tasklist generator should include NFR-style notes like "exit code may be non-zero due to pre-existing issues; assess only changes introduced by this sprint" when referencing lint/test commands.

---

## 3. Tasklist Generation Improvements

### 3.1 Tasklist Quality Assessment

**Priority**: P3 (Low -- it was good)
**Evidence**: 39 tasks across 4 phases. All tasks had: T##.## IDs, tier classifications, effort/risk/confidence metadata. All task descriptions used imperative verbs with explicit direct objects. Phase 4 T04.05 verified 100% standalone description quality.

**Assessment**: The tasklist quality was high. Every task was actionable and specific enough for automated execution. The tier system (STRICT/STANDARD/LIGHT/EXEMPT) provided useful risk signals. Evidence requirements were clear.

**Recommendation**: Minor improvements:
- Include expected output file paths in task descriptions (Claude had to infer where to write results)
- Include explicit "precondition" fields for tasks that depend on prior tasks
- The T03.05/T03.06 tasks could have included the caveat about pre-existing failures directly in the task description

---

### 3.2 Task Descriptions Actionability

**Priority**: P3 (Low)
**Evidence**: Claude Code completed all 39 tasks without apparent confusion or backtracking. The result files show systematic, confident execution with clear evidence for each task.

**Assessment**: Task descriptions were sufficiently actionable. The combination of task title + tier + evidence requirements gave Claude Code enough context.

**Recommendation**: No significant changes needed. The current format works well for automated execution.

---

### 3.3 Explicit Tool Specifications

**Priority**: P3 (Low)
**Evidence**: The SKILL.md's Tool Usage section maps tools to generation stages, but individual task descriptions do not specify which tools to use. Claude Code selected appropriate tools autonomously.

**Assessment**: Explicit tool specifications in tasks are unnecessary and potentially counterproductive. Claude Code's tool selection was appropriate throughout. Over-specifying tools reduces the agent's ability to adapt to unexpected situations.

**Recommendation**: Do not add explicit tool specifications to task descriptions. The current approach of tool guidance at the skill level (not task level) is correct.

---

## 4. Release Process Improvements

### 4.1 Auto-Commit Results

**Priority**: P1 (Important)
**Evidence**: The sprint generated result files in `results/` that are currently unstaged (shown in git status as modified/untracked). The execution log files are also modified but uncommitted.

**Recommendation**: Add a `--auto-commit` flag (default off) to the sprint runner that:
1. After sprint completion (success or halt), stages all files in the results directory
2. Creates a commit with a standardized message: `sprint(v2.07): phase 1-4 complete [39 tasks, 38 pass, 1 partial]`
3. Does NOT push (leave that to the operator)

Implementation: Add a post-sprint hook in `execute_sprint()` after `logger.write_summary()`. Use subprocess to run `git add` and `git commit` on the results directory only.

---

### 4.2 Auto-Triggered Retrospective

**Priority**: P2 (Recommended)
**Evidence**: This retrospective analysis was manually triggered. The sprint runner has no concept of post-sprint analysis.

**Recommendation**: Add a `--retrospective` flag that, after sprint completion:
1. Collects all JSONL events, result files, and error files
2. Generates a structured retrospective template in `results/retrospective.md`
3. Pre-fills with quantitative data (duration, pass rates, files changed)
4. Leaves qualitative sections (lessons learned, process improvements) for human or agent completion

This is lower priority than fixing the telemetry issues (sections 1.1-1.4) since the retrospective depends on accurate data.

---

### 4.3 Post-Sprint Validation Phase

**Priority**: P1 (Important)
**Evidence**: The sprint reported success, but Phase 3 had a PARTIAL result that was silently promoted. Without manual review of the result files, this would have been invisible.

**Recommendation**: Add a post-sprint validation step (not a new phase, but a runner-level check):
1. Re-read all result files after sprint completion
2. Parse frontmatter `status`, `tasks_passed`, `tasks_failed` fields
3. Compute aggregate metrics: total tasks, total passed, total failed
4. If any phase has `tasks_failed > 0`, flag the sprint outcome as PARTIAL even if all phases "passed"
5. Write a `sprint-summary.md` with aggregated per-task results across all phases

This catches the exact scenario observed: the runner thinks everything passed, but a deeper read reveals partial failures.

---

## Prioritized Improvement Backlog

| Priority | ID | Category | Title | Effort | Impact |
|----------|-----|----------|-------|--------|--------|
| P0 | IMP-001 | Runner | Add PhaseStatus.PARTIAL with honest telemetry | S | Critical -- fixes silent data loss |
| P1 | IMP-002 | Runner | Fix files_changed extraction from NDJSON events | M | Important -- enables file tracking |
| P1 | IMP-003 | Process | Pre-flight baseline scan for known failures | M | Important -- prevents false negatives |
| P1 | IMP-004 | Release | Post-sprint validation (aggregate task results) | M | Important -- catches partial failures |
| P1 | IMP-005 | Release | Auto-commit flag for sprint results | S | Important -- reduces manual steps |
| P2 | IMP-006 | Runner | Phase-scoped task ID filtering in monitor | S | Recommended -- fixes last_task_id |
| P2 | IMP-007 | Runner | Per-task JSONL events from result file parsing | M | Recommended -- enables dashboards |
| P2 | IMP-008 | Process | Per-phase max_turns calibration guidance | S | Recommended -- future-proofing |
| P2 | IMP-009 | Process | Soft cap of 12 tasks per phase in generator | S | Recommended -- better granularity |
| P2 | IMP-010 | Release | Auto-retrospective template generation | M | Recommended -- process maturity |
| P3 | IMP-011 | Runner | Document/fix error file behavior with stream-json | S | Low -- cosmetic clarity |
| P3 | IMP-012 | Tasklist | Add expected output paths to task descriptions | S | Low -- minor quality bump |
| P3 | IMP-013 | Tasklist | Add precondition fields for dependent tasks | S | Low -- minor quality bump |

**Effort key**: S = small (1-2 hours), M = medium (half day), L = large (full day+)

---

## Key Observations

1. **The sprint runner works.** 39 tasks across 4 phases completed in 23 minutes with no crashes, timeouts, or stuck processes. The core orchestration loop is solid.

2. **Telemetry fidelity is the biggest gap.** The JSONL log tells a simpler story than reality: all phases "pass", zero files changed, wrong task IDs for Phase 4. This makes the log unreliable for automated analysis or dashboards.

3. **Claude Code's judgment was excellent.** The PARTIAL result in Phase 3 was correctly diagnosed as a pre-existing bug. The `EXIT_RECOMMENDATION: CONTINUE` was the right call. The problem is that the runner erases this nuance.

4. **The tasklist format is production-ready.** Task descriptions were consistently actionable, well-scoped, and evidence-oriented. No significant format changes needed.

5. **Three failed attempts preceded the successful run.** The JSONL log shows runs at 02:44 (killed, exit -9), 02:53 (2-turn test), and 02:55 (2-turn test) before the full run at 10:54. The runner correctly logged these. Consider tracking run attempt counts as metadata.
