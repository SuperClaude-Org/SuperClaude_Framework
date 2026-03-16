# Architectural Validation Report

## Agent Role
Architect: Validate every architectural claim, implementation order, conflict resolution, and overlap/synergy conclusion against the real codebase signatures and control flow.

## Focus Areas
architectural-correctness, overlap-completeness, conflict-resolution, implementation-order

---

## 1. Codebase State Claims

### CBS-1: PhaseStatus enum location and content (lines 203-241)
**Verdict**: AMEND
**Evidence**: The actual `PhaseStatus` class definition begins at line 204, not 203. Line 203 is a blank line. The inline code comment correctly says "models.py:204-216" for the enum values. The enum values, `is_terminal`, `is_success`, and `is_failure` properties all match exactly.
**Reasoning**: Minor off-by-one in the section header. The claim that no `PASS_WITH_WARNINGS` or `PASS_RECOVERED` exists today is confirmed.

### CBS-2: _determine_phase_status() location and signature
**Verdict**: AMEND
**Evidence**: The function definition starts at line 765, not 764. Line 764 is blank. The actual signature matches exactly. The critical early return at line 783-784 is confirmed. The section header says "lines 764-814" but the function spans 765-815.
**Reasoning**: Off-by-one. The signature and logic are correctly described.

### CBS-3: AggregatedPhaseReport location and content (lines 178-281)
**Verdict**: AMEND
**Evidence**: The class starts at line 179 (`@dataclass`) or 180 (`class` keyword). The `to_markdown()` method spans lines 244-282, not "lines 243-281". The method does produce `EXIT_RECOMMENDATION: CONTINUE` at line 278 and `EXIT_RECOMMENDATION: HALT` at line 280.

**CRITICAL FINDING on "Already called in the execution loop"**: The analysis claims `aggregate_task_results()` is "Already called in the execution loop but its output is not persisted." This is **FALSE**. `aggregate_task_results()` is NEVER called from `execute_sprint()`. The function `execute_sprint()` uses `ClaudeProcess` to launch a single subprocess per phase. There are no `task_results` or `remaining` variables in `execute_sprint()`'s scope. `execute_phase_tasks()` exists separately (lines 348-488) but is NOT called from `execute_sprint()`.

**Reasoning**: The line numbers are off by 1-2. More importantly, the claim about `aggregate_task_results()` being already called is incorrect and materially affects the feasibility of Step 2.

### CBS-4: execute_sprint() structure (lines 489-761)
**Verdict**: AMEND
**Evidence**: Function starts at line 490. Most line references within are accurate: line 541 ClaudeProcess (confirmed), line 543 started_at (confirmed), poll loop at lines 557-629 (analysis says 557-625), exit code extraction at lines 631-647 (analysis says 635-643), _determine_phase_status call at lines 658-663 (confirmed).

**CRITICAL FINDING**: The analysis Step 2 context claims "task_results and remaining variables are available from the earlier call to execute_phase_tasks() at lines 348-445." This is **FALSE**. `execute_sprint()` does NOT call `execute_phase_tasks()`. The current architecture runs one subprocess per entire phase, not per task.

**Reasoning**: The structural description is mostly correct but the critical assumption that `task_results` exists in `execute_sprint()` is wrong, undermining Step 2.

### CBS-5: build_prompt() (lines 115-157)
**Verdict**: CONFIRM
**Evidence**: Confirmed exactly. Completion Protocol at lines 137-150 as claimed.

### CBS-6: detect_error_max_turns() (lines 35-59)
**Verdict**: CONFIRM
**Evidence**: Confirmed. Function at lines 35-59.

### CBS-7: FailureCategory (lines 19-26)
**Verdict**: CONFIRM
**Evidence**: Confirmed exactly. Five values, no CONTEXT_EXHAUSTION.

### CBS-8: commands.py run() (lines 34-170)
**Verdict**: CONFIRM
**Evidence**: Confirmed. No fidelity check exists. Insertion point between 156 and 162 is valid.

---

## 2. Overlap Table

### OV-1: PhaseStatus enum -- PASS_RECOVERED vs PASS_WITH_WARNINGS
**Verdict**: CONFIRM
**Evidence**: Both specs propose the same semantic addition. The recommendation to use PASS_RECOVERED is sound. "Recovered" conveys abnormal-but-successful completion; "with warnings" is ambiguous.

### OV-2: _determine_phase_status() -- non-zero exit recovery logic
**Verdict**: AMEND
**Evidence**: The ordering recommendation (S2 first, SOL-C second) is architecturally sound. However, the proposed merged code has a **circularity problem**: `_classify_from_result_file(result_file, started_at=started_at, recovered=True)` assumes the executor has already written the result file (Step 2). But if the executor writes the result file before calling `_determine_phase_status`, then `_classify_from_result_file` is reading the executor's own output, not independent evidence. The executor already knows the status from `AggregatedPhaseReport.status` directly. This makes the read-back circular and the timestamp validation (S2-R06) a no-op (executor file always newer than `started_at`).
**Reasoning**: The merged code needs to distinguish between agent-written and executor-written result files.

### OV-3: _determine_phase_status() -- signature change
**Verdict**: CONFIRM
**Evidence**: The merged signature with keyword-only args and defaults is sound. Backward compatible. `started_at.timestamp()` converts datetime to float correctly.

### OV-4: Pre-write (SOL-D) vs executor-write (S1)
**Verdict**: AMEND (CRITICAL)
**Evidence**: The analysis correctly identifies S1 as architecturally superior. However, it claims implementation is "~5 lines" because the executor "already has `AggregatedPhaseReport` from `aggregate_task_results()` at lines 285-330." This is **misleading**. `aggregate_task_results()` requires `list[TaskResult]` which does NOT exist in `execute_sprint()`'s scope. The current architecture runs one subprocess per phase, not per task. There is no `task_results` variable. To implement S1 as described requires EITHER:
  - (a) Refactoring `execute_sprint()` to use per-task execution — a massive change
  - (b) Constructing a minimal `AggregatedPhaseReport` from phase-level exit code and monitor state — far less data than assumed
**Reasoning**: "~5 lines" dramatically understates implementation effort. The analysis overstates readiness of existing infrastructure.

### OV-5: Phase prompt -- add vs remove instruction
**Verdict**: CONFIRM
**Evidence**: If the executor writes the result file, removing the agent instruction is correct. The 2-line "Scope Boundary" replacement is clean. However, viability depends on OV-4/Step 2 being implementable.

---

## 3. Synergy Table

### SY-1: Executor writes result file deterministically
**Verdict**: AMEND
**Evidence**: The synergy is real in principle but overstated. "~30 lines saved" assumes the executor CAN write the file easily. Since `execute_sprint()` lacks task-level results, implementation cost is higher than claimed.

### SY-2: Agent no longer responsible for result file
**Verdict**: AMEND
**Evidence**: Conditionally valid, contingent on SY-1 being implementable.

### SY-3: Shared PASS_RECOVERED enum value
**Verdict**: CONFIRM
**Evidence**: Genuine synergy with zero caveats.

### SY-4: Combined signature extension
**Verdict**: CONFIRM
**Evidence**: Genuine synergy. One change instead of two.

### SY-5: Context token reduction
**Verdict**: CONFIRM
**Evidence**: Token savings are real. S3 isolation savings are architecturally reasonable.

---

## 4. Conflict Table

### C-1: Pre-write vs executor-written (MEDIUM)
**Verdict**: CONFIRM
**Evidence**: Timestamp incompatibility analysis is correct. SOL-D writes at T0 < started_at at T1, so S2-R06 staleness check would always reject it. MEDIUM severity appropriate.

### C-2: Checkpoint vs context-exhaustion ordering (HIGH)
**Verdict**: CONFIRM
**Evidence**: Ordering concern is real. S2-first preserves diagnostic specificity. HIGH appropriate.

### C-3: Two enum names (HIGH)
**Verdict**: CONFIRM
**Evidence**: Two values for same semantic purpose = maintenance hazard. HIGH appropriate.

### C-4: Add vs remove prompt instruction (CRITICAL)
**Verdict**: CONFIRM
**Evidence**: Genuine logical contradiction. SOL-A adds, S1-R04 removes. CRITICAL appropriate.

### C-5: Checkpoint file dependency (LOW)
**Verdict**: CONFIRM
**Evidence**: SOL-C as fallback is less reliable but defense-in-depth is valid. LOW appropriate.

### C-6: Fidelity preflight (NONE)
**Verdict**: CONFIRM
**Evidence**: No overlap verified. NONE correct.

---

## 5. Implementation Order (Steps 1-10)

### Step 1: Add PASS_RECOVERED to PhaseStatus
**Verdict**: CONFIRM
**Evidence**: Foundation step. Additive, low risk, correct insertion point.

### Step 2: Executor writes result file from AggregatedPhaseReport
**Verdict**: REJECT
**Evidence**: The step claims "~5 lines: call aggregate_task_results() (already exists at line 285), write report.to_markdown() to config.result_file(phase)." It claims "task_results and remaining variables are available from the earlier call to execute_phase_tasks() at lines 348-445." This is **FALSE**. `execute_sprint()` does NOT call `execute_phase_tasks()`. There is no `task_results` list in `execute_sprint()`'s scope. There is no `remaining` variable. `aggregate_task_results()` is never invoked from the main loop. Implementing this step as described requires either a substantial architectural refactor or a degraded minimal implementation.
**Reasoning**: Not implementable against current codebase as written. This is the most critical error in the document because Steps 3, 6, and OV-4 all depend on it.

### Step 3: Remove Completion Protocol + add stop line
**Verdict**: AMEND
**Evidence**: The change itself is well-defined. However, removing the Completion Protocol is only safe IF the executor writes the result file (Step 2). Since Step 2 is not implementable as described, removing the agent's result-file instructions would leave NO mechanism for result file creation. Every phase would hit PASS_NO_REPORT or ERROR.
**Reasoning**: Hard dependency on a working Step 2 must be explicitly flagged.

### Step 4: Add detect_prompt_too_long() in monitor.py
**Verdict**: CONFIRM
**Evidence**: Independent. Follows exact pattern of detect_error_max_turns(). Correct insertion.

### Step 5: _check_fidelity() in commands.py
**Verdict**: CONFIRM
**Evidence**: Fully independent. Can be implemented in parallel.

### Step 6: Restructure _determine_phase_status()
**Verdict**: AMEND
**Evidence**: The restructuring logic is sound in isolation, but has the circularity problem from OV-2. If the executor writes the result file before calling `_determine_phase_status()`, then `_classify_from_result_file()` reads the executor's own output. The timestamp validation becomes a no-op. The recovery chain needs to distinguish file authorship.
**Reasoning**: Design requirement for distinguishing agent-written vs executor-written result files is missing.

### Step 7: Phase-specific directory isolation
**Verdict**: CONFIRM
**Evidence**: Independent prevention layer. Architecturally sound.

### Step 8: Add FailureCategory.CONTEXT_EXHAUSTION
**Verdict**: CONFIRM
**Evidence**: Simple additive change. Independent. Low risk.

### Step 9: Tests
**Verdict**: AMEND
**Evidence**: Several tests assume Step 2 works as described. Tests for detect_prompt_too_long(), PASS_RECOVERED, checkpoint inference, and fidelity are independently valid.

### Step 10: Integration verification
**Verdict**: CONFIRM
**Evidence**: Standard step. No issues.

---

## 6. Overall Assessment

### Overstated Claims

1. **Step 2 feasibility is critically overstated.** The analysis repeatedly claims that `aggregate_task_results()` is "already called in the execution loop" and that `task_results` and `remaining` variables are "available." This is false. `execute_sprint()` runs one subprocess per entire phase and has no per-task result data. This error propagates into line savings estimates ("~5 lines"), synergy table (SY-1 "~30 lines saved"), and conflict resolution for C-1 and OV-4.

2. **The circularity in OV-2/Step 6 is understated.** If the executor writes the result file (Step 2) and then `_classify_from_result_file()` reads it (Step 6), the executor is reading its own output. The timestamp validation becomes meaningless. This interaction is not identified.

### Understated Claims

1. **SOL-C's checkpoint inference has more value than credited.** In the current architecture (agent writes result file), checkpoints are the ONLY recovery mechanism reading agent-produced artifacts that existed BEFORE a crash. S1 and S2 both depend on infrastructure changes that do not yet exist.

2. **The prompt token savings from removing Completion Protocol are understated in magnitude but overstated in safety.** If removed without a working executor replacement, no result file is ever created.

### Missed Dependencies

1. Step 2 depends on either refactoring `execute_sprint()` to call `execute_phase_tasks()`, or creating a new minimal result-file writer. Neither is acknowledged.
2. Step 3 has a hard dependency on Step 2 not flagged as a risk.
3. Step 6's `_classify_from_result_file()` needs to distinguish agent-written vs executor-written result files.

### Summary Verdict

The analysis is architecturally well-reasoned in overlap identification, conflict severity ratings, and resolution preferences. The ordering of specific-before-general recovery (C-2), elimination of SOL-D (C-1), and C-4 contradiction resolution are all correct. However, the document contains one **critical factual error** -- the assumption that `execute_phase_tasks()` and `aggregate_task_results()` are already wired into `execute_sprint()` -- which undermines Step 2 and cascades into Steps 3, 6, and 9. The implementation plan cannot be executed as written without first resolving the execution model mismatch.

**Recommended corrective action**: Either (a) add a prerequisite Step 0 wiring `execute_phase_tasks()` into `execute_sprint()`, or (b) redesign Step 2 to write a minimal result file from phase-level exit code and monitor state rather than per-task aggregation.
