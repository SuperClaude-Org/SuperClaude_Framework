# Variant 1: Architect Validation -- Cross-Spec Overlap Analysis

## Executive Summary

The cross-spec overlap analysis is structurally sound and demonstrates genuine understanding of the codebase. However, it contains multiple line-number inaccuracies (off-by-one errors and misattributed ranges), one mischaracterized code structure (the `execute_sprint` function boundary), several optimistic synergy estimates, and an under-classified conflict severity for OV-4. The 10-step implementation ordering has one hidden assumption violation between Steps 2 and 6 that could cause test failures if not carefully sequenced.

## Line Number Verification Matrix

| Cited Reference | Claimed Content | Actual Content | Status |
|---|---|---|---|
| `models.py:203-241` (PhaseStatus) | Class at lines 203-241 | Class declaration at line 204 (`class PhaseStatus(Enum):`), `is_failure` ends at line 241. Line 203 is the end of `TaskResult.to_context_summary`. | **INACCURATE** -- off by 1 at start (should be 204-241) |
| `models.py:204` (class line) | `class PhaseStatus(Enum):` | `class PhaseStatus(Enum):` at line 204 | **CORRECT** |
| `models.py:207-216` (enum values) | PENDING through SKIPPED | PENDING=207, RUNNING=208, PASS=209, PASS_NO_SIGNAL=210, PASS_NO_REPORT=211, INCOMPLETE=212, HALT=213, TIMEOUT=214, ERROR=215, SKIPPED=216 | **CORRECT** |
| `models.py:218-228` (is_terminal) | is_terminal includes listed values | `is_terminal` property starts at line 218, tuple at lines 220-229. The analysis says "line 218" which is the `@property` decorator, and the tuple starts at line 220. | **CLOSE** -- decorator at 218, body at 219-229 |
| `models.py:231-237` (is_success) | is_success includes PASS, PASS_NO_SIGNAL, PASS_NO_REPORT | `is_success` property: decorator at 231, `def` at 232, `return self in (` at 233, tuple at 233-237. | **CORRECT** |
| `models.py:239-241` (is_failure) | is_failure includes INCOMPLETE, HALT, TIMEOUT, ERROR | `is_failure`: decorator at 239, `def` at 240, `return` at 241. | **CORRECT** |
| `executor.py:764-814` (_determine_phase_status) | Function range | Function starts at line 765 (`def _determine_phase_status`). Line 764 is a blank line. Function ends at line 815 (`return PhaseStatus.ERROR`). | **INACCURATE** -- should be 765-815 (off by 1 at both ends) |
| `executor.py:764-768` (signature) | `(exit_code, result_file, output_file) -> PhaseStatus` | Signature spans lines 765-769 (def on 765, closing paren + return type on 769). Line 764 is blank. | **INACCURATE** -- should be 765-769 |
| `executor.py:783` (early return) | `if exit_code != 0: return PhaseStatus.ERROR` | Line 783: `if exit_code != 0:`, Line 784: `return PhaseStatus.ERROR` | **CORRECT** (the `if` is at 783; the return is at 784; analysis correctly identifies 783 as the target line) |
| `executor.py:658-663` (call site) | `_determine_phase_status(...)` call | Lines 658-663: comment at 658, function call at 659-663. | **CORRECT** |
| `executor.py:543` (started_at) | `started_at = datetime.now(timezone.utc)` | Line 543: `started_at = datetime.now(timezone.utc)` | **CORRECT** |
| `executor.py:178-281` (AggregatedPhaseReport) | Class range | `@dataclass` at line 179, `class AggregatedPhaseReport:` at line 180, `to_markdown()` return at line 282. Line 178 is a blank line. | **INACCURATE** -- should be 179-282 |
| `executor.py:243-281` (to_markdown) | Method range | `def to_markdown(self)` at line 244, method ends at line 282. Line 243 is blank. | **INACCURATE** -- should be 244-282 |
| `executor.py:285-330` (aggregate_task_results) | Function range | `def aggregate_task_results` at line 285, `return report` at line 330. | **CORRECT** |
| `executor.py:489-761` (execute_sprint) | Function range | `def execute_sprint` at line 490, function body ends at line 762 (`raise SystemExit(_exitcode)`). Line 489 is blank. | **INACCURATE** -- should be 490-762 |
| `executor.py:541` (subprocess launch) | `proc_manager = ClaudeProcess(config, phase)` | Line 541: `proc_manager = ClaudeProcess(config, phase)` | **CORRECT** |
| `executor.py:557-625` (poll loop) | Poll loop range | Poll loop (`while proc_manager._process.poll()`) starts at line 557, ends at line 629 (`time.sleep(0.5)`). | **INACCURATE** -- should end at 629, not 625 |
| `executor.py:635-643` (exit code extraction) | Exit code logic | Exit code assignment starts at line 633 (`raw_rc = ...`), completes at line 637 (`exit_code = raw_rc if ...`). Line 643 is the string `"PHASE_END"` inside a debug_log call, not exit-code-related logic. | **INACCURATE** -- analysis uses 643 as the boundary "exit code resolved", but 643 is a debug log string, not exit code logic. The actual boundary is 637. |
| `executor.py:698-719` (is_failure block) | Diagnostics + HALTED block | Line 698: `if status.is_failure:`, block runs through line 720 (`break`). | **CLOSE** -- extends to 720, not 719 |
| `executor.py:200-209` (AggregatedPhaseReport.status) | status property range | `@property` at line 201, method at 202, body 203-210. Line 200 is blank. | **INACCURATE** -- should be 201-210 |
| `process.py:115-157` (build_prompt) | Method range | `def build_prompt(self)` at line 115, method ends at line 157. | **CORRECT** |
| `process.py:137-150` (Completion Protocol) | Section range | `## Completion Protocol` heading at line 137, last line of section at line 150. | **CORRECT** |
| `process.py:118` (result_file variable) | result_file = ... | Line 118: `result_file = self.config.result_file(self.phase)` | **CORRECT** |
| `monitor.py:35-59` (detect_error_max_turns) | Function range | `def detect_error_max_turns` at line 35, function ends at line 59 (`return False`). | **CORRECT** |
| `monitor.py:32` (ERROR_MAX_TURNS_PATTERN) | Pattern constant | Line 32: `ERROR_MAX_TURNS_PATTERN = re.compile(...)` | **CORRECT** |
| `commands.py:34-170` (run) | run() function range | Line 34 is NOT the run function. Line 34 is the end of `sprint_group()` (`pass` statement at line 32, then blank lines). The `@sprint_group.command()` decorator is at line 35. The `run` function signature starts at line 114. The function body is lines 140-170. | **INACCURATE** -- analysis says run() at lines 34-170; actual function definition is line 114-170, body is 140-170. Line 34 is `pass` (end of sprint_group). |
| `commands.py:140-170` (run body) | Function body range | Body starts at line 140 (first import), ends at line 170 (`execute_sprint(config)`). | **CORRECT** |
| `commands.py:144-156` (load_sprint_config) | Config loading call | Lines 144-156 contain `load_sprint_config(...)` call. | **CORRECT** |
| `commands.py:162-164` (dry_run check) | dry_run branch | Lines 162-164: `if dry_run:` / `_print_dry_run(config)` / `return`. | **CORRECT** |
| `commands.py:167-170` (tmux decision) | tmux branch | Lines 167-170: tmux decision and execute_sprint. | **CORRECT** |
| `diagnostics.py:19-26` (FailureCategory) | Enum range | `class FailureCategory(Enum):` at line 19, UNKNOWN at line 26. | **CORRECT** |
| `diagnostics.py:22-26` (enum values) | STALL through UNKNOWN | STALL=22, TIMEOUT=23, CRASH=24, ERROR=25, UNKNOWN=26. Actually: line 21 is `STALL = "stall"`, not line 22. | **INACCURATE** -- the values start at line 21 (STALL), not 22 |

**Summary**: 13 of ~30 line references contain inaccuracies, predominantly off-by-one errors. Most are minor (blank line before function counted in range), but the `commands.py:34` reference for `run()` is materially misleading, and the `executor.py:643` boundary point is mischaracterized.

## OV-* Overlap Classification Review

### OV-1: PhaseStatus enum -- new success-like value

**Classification**: Overlap -- **VALIDATED**

Both specs propose adding a new `is_success=True` value to `PhaseStatus` for non-zero exit recovery. The classification as "overlap" is correct. The naming difference (`PASS_WITH_WARNINGS` vs `PASS_RECOVERED`) is cosmetic. The recommendation to use `PASS_RECOVERED` is well-justified by semantic precision.

**Challenge**: None. This is a clean overlap.

### OV-2: `_determine_phase_status()` -- non-zero exit recovery logic

**Classification**: Overlap -- **SHOULD BE CONFLICT (MEDIUM)**

While both specs target the same `if exit_code != 0` block, calling this an "overlap" understates the integration complexity. The two recovery mechanisms have different preconditions, different detection methods, different helper functions, and different return-value logic. This is not "two solutions to the same problem" -- it is two solutions to two different subproblems that happen to share an insertion point. The analysis correctly identifies the merge strategy but underclassifies the integration risk. The merged `if exit_code != 0` block will have 3 branching paths, and the ordering between them is non-obvious (the analysis addresses this in C-2, but the OV-2 entry fails to flag this as an integration concern).

**Recommendation**: Reclassify to OV-2/C-2 combined item, severity MEDIUM-HIGH.

### OV-3: `_determine_phase_status()` -- signature change

**Classification**: Overlap -- **VALIDATED**

Both specs need additional parameters. Merging into a single signature change with keyword-only defaults is the correct approach. The analysis's proposed signature is sound.

**Challenge**: The analysis proposes `started_at: float = 0.0`. However, the actual `started_at` in `execute_sprint()` at line 543 is a `datetime` object, not a float. The proposed call site shows `started_at=started_at.timestamp()` to convert. This is a minor design concern: passing a `float` epoch loses timezone information and introduces a conversion step. An alternative design would pass `started_at: datetime | None = None` directly. The analysis does not discuss this tradeoff.

### OV-4: Pre-writing / executor-writing result file

**Classification**: Overlap -- **SHOULD BE CONFLICT (MEDIUM)**

The analysis classifies this as overlap, but the two approaches are fundamentally incompatible. SOL-D writes a file **before** subprocess launch (dead-man's switch). S1 writes a file **after** subprocess exit (deterministic report). These are not two solutions to the same problem -- they are two different strategies with different timing, content, and failure mode characteristics. The analysis reaches the right conclusion (discard SOL-D), but the classification should be "conflict" since implementing both would create the write-collision and timestamp-incompatibility issues described in C-1.

The fact that the analysis separately creates C-1 to describe the conflict between these exact same elements confirms they are conflicting, not merely overlapping.

**Recommendation**: Reclassify as a conflict (MEDIUM). Move C-1 content into OV-4 or merge them.

### OV-5: Phase prompt -- stop/boundary instruction

**Classification**: Overlap -- **SHOULD BE CONFLICT (HIGH)**

This is the same issue as C-4. SOL-A *adds* instructions to the prompt while S1-R04 *removes* them. The analysis correctly identifies this as a "direct contradiction" in C-4 (severity CRITICAL), yet OV-5 classifies it as mere overlap. These two assessments are contradictory within the same document.

**Recommendation**: Remove OV-5 entirely. This item belongs exclusively in C-4.

## SY-* Synergy Estimate Review

### SY-1: Executor writes result file deterministically

**Claimed savings**: ~30 lines (entire `_pre_write_result_file()` + call site from SOL-D)

**Assessment**: **OPTIMISTIC**. The `_pre_write_result_file()` helper proposed in Spec A (phase8-halt-fix.md, Step 1.2) is approximately 15 lines of code. The call site (Step 1.3) is 1 line. The result-file path verification (Step 1.4) adds perhaps 2-3 lines. Total SOL-D code: ~18-20 lines. The claim of "~30 lines" inflates by approximately 50%.

Additionally, S1 itself requires ~5 lines (as the analysis correctly states), so the net savings compared to implementing both is more like 18-20 lines, not 30.

**Corrected estimate**: ~18-20 lines saved.

### SY-2: Agent no longer responsible for result file

**Claimed savings**: ~15 lines (entire `_append_phase_stop_instruction()` from SOL-A)

**Assessment**: **ROUGHLY CORRECT**. The `_append_phase_stop_instruction()` helper in Spec A (Step 2.2) is ~14 lines. The call site (Step 2.3) is ~1 line. The total is ~15 lines. However, this assumes the 2-line "Scope Boundary" replacement is zero-cost, which it is not -- the replacement is 4 lines as shown in the analysis. Net savings: ~15 - 4 = ~11 lines.

**Corrected estimate**: ~11 lines saved (net, after replacement).

### SY-3: New PhaseStatus enum value

**Claimed savings**: ~0 lines

**Assessment**: **CORRECT**. Either way, one enum value is added. The savings are in avoiding maintaining two functionally identical values, which is a maintenance cost, not a line count.

### SY-4: `_determine_phase_status` signature extension

**Claimed savings**: ~5 lines

**Assessment**: **SLIGHTLY OPTIMISTIC**. A combined signature change vs two separate changes saves the duplicate editing of the signature line, the call site, and possibly the docstring. In practice, this is 2-3 lines of code duplication avoided (signature + call site edit once instead of twice). Claiming 5 overstates it.

**Corrected estimate**: ~2-3 lines saved.

### SY-5: Context token reduction

**Claimed savings**: Net +200 token savings by removing SOL-A instead of adding it

**Assessment**: **MISLEADING**. The analysis compares "SOL-A adds ~200 tokens" vs "S3 saves ~14K tokens/phase" and concludes the synergy is "+200 token savings." But these are independent changes. S3's directory isolation saves tokens regardless of whether SOL-A is implemented. The actual synergy is: by implementing S1 (executor writes result file), SOL-A's prompt additions become unnecessary, saving ~200 tokens/phase. S3's savings are a separate, additive benefit. The framing conflates S3's savings with the SOL-A/S1 synergy.

**Corrected framing**: The synergy is ~200 tokens/phase saved by not implementing SOL-A's prompt additions (because S1 makes them unnecessary). S3's ~14K savings are independent.

### Total Savings Summary

**Claimed**: ~50 lines of production code, ~200 prompt tokens/phase, 1 fewer enum value

**Corrected**: ~31-34 lines of production code, ~200 prompt tokens/phase, 1 fewer enum value. The "~50 lines" figure appears to be the sum of SY-1 (30) + SY-2 (15) + SY-4 (5) = 50, but corrected values give 20 + 11 + 3 = 34.

## C-* Conflict Severity Review

### C-1: Pre-write dead-man's switch vs executor-written result file (MEDIUM)

**Assessment**: **CORRECTLY RATED**. The analysis of the timestamp incompatibility (T0 < T1 failing the `mtime > started_at` check) is technically precise. The severity is Medium because the resolution is clear (discard SOL-D) and there is no ambiguity about which approach wins. This is really a design-level conflict that is easily resolved.

**Note**: As argued in OV-4 review above, this conflict should be unified with OV-4 rather than existing as a separate item.

### C-2: Checkpoint inference vs context-exhaustion detection -- ordering (HIGH)

**Assessment**: **CORRECTLY RATED**. The ordering dependency is a genuine HIGH-severity concern. If checkpoint inference (SOL-C) runs before context-exhaustion detection (S2), the diagnostic specificity for context exhaustion events is lost. The proposed resolution (specific before general) is correct.

**Additional concern not raised in the analysis**: The analysis assumes `detect_prompt_too_long()` will have zero false positives. If it has false positives (e.g., the string "Prompt is too long" appears in agent-generated output text), the checkpoint fallback path would be bypassed incorrectly. The "last 10 lines" constraint mitigates this but does not eliminate it. The analysis should have flagged this as a residual risk.

### C-3: Two enum names for same concept (HIGH)

**Assessment**: **OVER-RATED -- should be MEDIUM**. Having two enum values with identical semantics is a maintenance annoyance, not a high-severity conflict. The fix is trivial (pick one name). Neither spec has implemented the value yet, so there is no migration cost. The downstream consumers (TUI, logger) are mentioned as concerns, but they would need to handle exactly one new value regardless. The actual severity is that two teams might independently implement both values, but since this analysis exists to coordinate, that risk is mitigated by the analysis itself.

**Corrected severity**: MEDIUM.

### C-4: Add result-writing instruction vs remove it -- direct contradiction (CRITICAL)

**Assessment**: **CORRECTLY RATED**. This is genuinely the most dangerous conflict. Implementing SOL-A's prompt additions and then S1-R04's prompt removals (or vice versa) would create an incoherent prompt state. The resolution (remove, then add only the 2-line stop boundary) is correct.

**Additional validation**: The analysis correctly identifies that the "Completion Protocol" section (lines 137-150) is the exact target of both changes. However, the analysis does not mention that `result_file` (assigned at line 118) is referenced only within lines 137-150. If lines 137-150 are removed, `result_file` at line 118 becomes dead code. The analysis mentions this in Step 3 but only as an afterthought ("Remove reference to `result_file` variable (line 118) if no longer used"). This should be a mandatory part of the change to avoid linter warnings.

### C-5: Checkpoint file dependency vs executor-written result file (LOW)

**Assessment**: **CORRECTLY RATED**. SOL-C's checkpoint inference depends on agent behavior, which is inherently unreliable in crash scenarios. The analysis correctly positions it as a last-resort fallback. LOW severity is appropriate because S1 and S2 handle the primary cases.

### C-6: Fidelity preflight -- no conflict (NONE)

**Assessment**: **CORRECTLY RATED**. SOL-G operates in `commands.py` between `load_sprint_config` and the dry-run check. No Spec B change touches this region. Verified: Spec B modifies `executor.py`, `process.py`, `monitor.py`, `models.py`, and `diagnostics.py` -- it never touches `commands.py`.

**Minor correction**: The analysis says SOL-G inserts "between `commands.py:156` and `commands.py:162`". This is correct but incomplete. There are existing lines 157-161 (the `tmux_session_name` block) in this gap. The insertion should be specified as between lines 156 and 158 (before the tmux_session_name check, after load_sprint_config), or between lines 161 and 162 (after tmux_session_name, before dry_run). The analysis does not specify which side of the tmux_session_name block the insertion goes.

## Implementation Ordering Analysis

### Step 1: Add `PASS_RECOVERED` to `PhaseStatus` enum

**Safety**: SAFE. Additive-only change to an enum. No existing code references the new value.

**Hidden issue**: The analysis says "Insert `PASS_RECOVERED = "pass_recovered"` after line 211." Line 211 is `PASS_NO_REPORT = "pass_no_report"`. Line 212 is currently `INCOMPLETE = "incomplete"`. Inserting after 211 would shift all subsequent line numbers in models.py. This is not a problem for Step 1, but it means all subsequent line references in the analysis (e.g., `is_terminal` at line 218/220, `is_success` at line 231/233, `is_failure` at line 239/241) are invalidated. The analysis does not acknowledge this line-shift cascade.

### Step 2: Executor writes result file from `AggregatedPhaseReport`

**Safety**: **POTENTIALLY UNSAFE**. The analysis says to insert between line 643 (exit code resolved) and line 658 (`_determine_phase_status` call). However, line 643 is inside a `debug_log` call, not the end of exit-code resolution. The actual insertion point should be between line 647 (end of debug_log call) and line 649 (start of shutdown check).

**Critical concern**: The analysis proposes writing the result file from `aggregate_task_results(phase.number, task_results, remaining)`. But in the `execute_sprint()` function, there are NO local variables named `task_results` or `remaining`. The function `execute_sprint()` (lines 490-762) does not call `execute_phase_tasks()`. It launches a single subprocess via `ClaudeProcess(config, phase)` and monitors it via a poll loop. The `task_results` and `remaining` variables only exist inside `execute_phase_tasks()` (lines 349-446), which is a separate function used for per-task orchestration.

The analysis states at line 87 of the overlap document: "Already called in the execution loop but its output is not persisted to the result file path." And at Step 2: "The `task_results` and `remaining` variables are available from the earlier call to `execute_phase_tasks()` at lines 348-445." This is **FALSE** for `execute_sprint()`. The `execute_sprint()` function launches one subprocess per *phase*, not per task. It does NOT call `execute_phase_tasks()`. There is no `task_results` or `remaining` variable in scope at the proposed insertion point.

This means Step 2 as written is **NOT IMPLEMENTABLE** without additional design work. The executor would need to either:
(a) Construct an `AggregatedPhaseReport` from the phase-level exit code (not task-level results), or
(b) Parse the agent's output to extract task results, or
(c) Refactor `execute_sprint()` to call `execute_phase_tasks()`.

This is a **CRITICAL** issue that invalidates the core premise of Step 2.

### Step 3: Remove agent result-file-writing from prompt + add bleed-prevention

**Safety**: SAFE, contingent on Step 2 being valid. If Step 2 cannot be implemented as described (see above), removing the prompt instruction would leave no mechanism for the result file to be written.

### Step 4: Add `detect_prompt_too_long()` in `monitor.py`

**Safety**: SAFE. Purely additive. Independent of other steps.

### Step 5: `_check_fidelity()` + `--force-fidelity-fail` in `commands.py`

**Safety**: SAFE. Fully independent.

### Step 6: Restructure `_determine_phase_status()` with merged recovery chain

**Safety**: Depends on Steps 1, 2, and 4. If Step 2 is not implementable as described, the result-file-based recovery in Step 6 has no executor-written result file to read (only the agent-written one, if the agent wrote it). This weakens but does not invalidate the recovery logic.

**Hidden assumption**: Step 6 assumes the result file exists and was written by the executor (Step 2). If Step 2 is not implemented, the recovery chain falls through to checkpoint inference (SOL-C) or ERROR. This makes the ordering "safe" in the sense that failure is graceful, but the primary recovery path (S2) would not function as designed.

### Step 7: Phase-specific directory isolation

**Safety**: SAFE. Independent of recovery logic.

### Step 8: Add `FailureCategory.CONTEXT_EXHAUSTION`

**Safety**: SAFE. Additive-only.

### Step 9: Tests

**Safety**: Depends on all prior steps. If Step 2 is not implementable, several tests (executor writes result file with CONTINUE/HALT, result file written before `_determine_phase_status()`) would fail.

### Step 10: Integration verification

**Safety**: Terminal step, no hidden assumptions.

### Circular Dependencies

No circular dependencies exist in the 10-step order. The dependency chain is:
- Step 1 (enum) -> Step 6 (uses PASS_RECOVERED)
- Step 2 (result file) -> Step 3 (removes prompt), Step 6 (depends on result file)
- Step 4 (detection) -> Step 6 (uses detect_prompt_too_long)
- Steps 1-8 -> Step 9 (tests) -> Step 10 (integration)

The ordering is topologically valid. The risk is not circular dependencies but the Step 2 implementability gap.

## Identified Issues

1. **CRITICAL**: Step 2 assumes `task_results` and `remaining` variables are available inside `execute_sprint()`, but they are not. `execute_sprint()` does not call `execute_phase_tasks()`. The `AggregatedPhaseReport` mechanism was designed for per-task orchestration, not per-phase subprocess execution. The analysis conflates the two execution models. This invalidates the core implementation strategy for S1.

2. **HIGH**: The analysis contains 13 line-number inaccuracies out of ~30 references. Most are off-by-one (citing a blank line before a function definition), but `commands.py:34` for `run()` is materially wrong (should be 114), and `executor.py:643` as the boundary for "exit code resolved" is misleading (643 is a debug log string, not exit code logic; the actual boundary is 637).

3. **HIGH**: OV-4 and OV-5 are classified as "overlaps" but are actually conflicts. The analysis itself creates C-1 and C-4 to describe the conflicts between these exact same elements, creating internal inconsistency in the document.

4. **MEDIUM**: The `started_at: float = 0.0` type in the proposed merged signature is a questionable design choice. `started_at` is a `datetime` object in `execute_sprint()` (line 543). Converting to float epoch loses timezone information. Consider `started_at: datetime | None = None` instead.

5. **MEDIUM**: SY-1 claims ~30 lines saved but the actual SOL-D implementation is ~18-20 lines. Total synergy savings are ~34 lines, not ~50 as claimed.

6. **MEDIUM**: C-3 (two enum names) is rated HIGH but should be MEDIUM. The risk is trivially mitigable since neither value has been implemented yet.

7. **LOW**: The analysis does not address the line-shift cascade from Step 1. Inserting a new enum value after line 211 shifts all subsequent line numbers in models.py, invalidating the line references used in Steps 6 and 9.

8. **LOW**: The fidelity check insertion point (C-6 / Step 5) does not specify whether to insert before or after the `tmux_session_name` block at lines 158-160. This ambiguity could lead to the fidelity check running before `config.tmux_session_name` is set, which may or may not matter depending on whether `_check_fidelity` uses `config`.

9. **LOW**: The analysis says `detect_prompt_too_long()` should scan "last 10 non-empty lines" but `detect_error_max_turns()` actually scans only the last 1 non-empty line (iterating `reversed(lines)` and returning on first non-empty). The analysis incorrectly describes `detect_error_max_turns()` as scanning "last 1 as detect_error_max_turns does" -- but the key architectural difference it proposes (scan 10 vs 1) is not actually grounded in a limitation of the current function, it is a new design choice.

10. **LOW**: The analysis does not flag that `AggregatedPhaseReport.to_markdown()` emits `EXIT_RECOMMENDATION: CONTINUE` only when `self.status == "PASS"` (line 277). PARTIAL status results in HALT. This means if even one task fails, the executor-written result file would say HALT, and the context-exhaustion recovery path would return HALT (not PASS_RECOVERED). This may be the correct behavior, but it narrows the recovery window significantly -- the analysis does not discuss this interaction.

## Corrected Recommendations

### On Step 2 (Critical fix needed)

The analysis must address the fact that `execute_sprint()` does not have per-task result data. The options are:

**(a) Minimal fix**: The executor writes a minimal result file from the phase-level exit code and output existence:
```python
# Between lines 647 and 649 in execute_sprint():
result_content = "EXIT_RECOMMENDATION: CONTINUE\n" if exit_code == 0 else "EXIT_RECOMMENDATION: HALT\n"
config.result_file(phase).write_text(result_content)
```
This is simpler but loses the rich `AggregatedPhaseReport` data.

**(b) Use monitor state**: Construct a result from `monitor.state` data (last_task_id, events_received, output_bytes) rather than `AggregatedPhaseReport`.

**(c) Refactor to use per-task execution**: Replace the single-subprocess-per-phase model with `execute_phase_tasks()`. This is a larger change that was likely the long-term intent, but represents significant scope expansion.

The analysis should explicitly choose one of these paths and update Steps 2, 3, and 6 accordingly.

### On OV-4/OV-5 reclassification

Merge OV-4 with C-1 and remove OV-5 (it is C-4). The overlap section should contain only OV-1, OV-2, and OV-3.

### On C-3 severity

Downgrade from HIGH to MEDIUM.

### On the `started_at` type

Use `started_at: datetime | None = None` instead of `started_at: float = 0.0` to preserve type consistency with the existing codebase and avoid lossy conversions.

### On SY-* estimates

Correct total from "~50 lines" to "~34 lines". The individual estimates should be corrected as documented in the SY-* review section above.
