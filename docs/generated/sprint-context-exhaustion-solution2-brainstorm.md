# Solution #2 Brainstorm: Detect "Prompt is too long" in Output

## Problem Recap

When a Claude subprocess exhausts its context window (200K tokens for Sonnet), the Anthropic API returns an error with `"Prompt is too long"` and `"error":"invalid_request"`. The subprocess exits with code 1. The sprint executor's `_determine_phase_status()` sees `exit_code != 0` at line 783 and immediately returns `PhaseStatus.ERROR`, which is classified as `is_failure` (line 241), causing the sprint to halt via the `status.is_failure` check at line 698.

The critical nuance: context exhaustion typically occurs LATE in a phase's execution. The subprocess may have successfully completed 90% of its assigned tasks before hitting the context ceiling. Treating this as a hard error discards all that work and prevents the sprint from continuing to subsequent phases.

## Existing Precedent: error_max_turns Detection

The codebase already handles a structurally identical problem. The `detect_error_max_turns()` function in `monitor.py:35-59` scans the last non-empty NDJSON line for `"subtype":"error_max_turns"`. This detection is consumed in `executor.py:811` within `_determine_phase_status()`, but ONLY when `exit_code == 0` and no result file exists. The context exhaustion case differs because the subprocess exits with code 1, not 0 -- so the current detection point is never reached.

---

## 1. Implementation Approaches

### Approach A: Simple Pattern Match + Reclassify as INCOMPLETE

**Where**: Add a new detection function `detect_prompt_too_long()` in `monitor.py` alongside the existing `detect_error_max_turns()`. Consume it in `executor.py:_determine_phase_status()`.

**Pattern to match**: The Anthropic API error appears in the NDJSON stream. The exact structure is a JSON object containing `"error"` with nested fields. The key signals are:
- `"Prompt is too long"` as a message string
- `"invalid_request"` as an error type/subtype
- These may appear in the last few lines of the NDJSON output (not necessarily the very last line, since the CLI may emit additional events after the API error)

**Classification**: Return `PhaseStatus.INCOMPLETE` -- the same status used for `error_max_turns`. This is semantically correct: the phase did not complete cleanly, but it is not a catastrophic error.

**Where in `_determine_phase_status()`**: The critical change is that detection must happen BEFORE the `exit_code != 0 -> ERROR` branch at line 783. Currently the logic is:

```
1. exit_code == 124 -> TIMEOUT
2. exit_code != 0   -> ERROR        <-- context exhaustion trapped here
3. result file checks
4. output file checks (error_max_turns lives here)
```

The fix inserts a check between steps 1 and 2:

```
1. exit_code == 124 -> TIMEOUT
1.5 exit_code != 0 AND output has "prompt too long" -> INCOMPLETE   <-- NEW
2. exit_code != 0   -> ERROR
3. result file checks
4. output file checks
```

**Pros**:
- Minimal code change (one new function + one new branch)
- Follows existing pattern exactly (mirrors error_max_turns)
- INCOMPLETE already triggers HALT via `is_failure`, so downstream logic is safe
- Diagnostic collection still runs (line 699-716), providing visibility

**Cons**:
- Does not distinguish "work was completed but context ran out writing the report" from "work was NOT completed and context ran out mid-task"
- Always halts the sprint (INCOMPLETE is a failure status), even if 100% of tasks finished

---

### Approach B: Pattern Match + Result File Existence Check

**Where**: Same location as Approach A, but with a two-stage check.

**Logic**:
1. If `exit_code != 0` AND `detect_prompt_too_long(output_file)` is True:
   - If `result_file.exists()` and contains EXIT_RECOMMENDATION: CONTINUE -> `PhaseStatus.PASS`
   - If `result_file.exists()` and contains EXIT_RECOMMENDATION: HALT -> `PhaseStatus.HALT`
   - If `result_file.exists()` but has no signal -> `PhaseStatus.PASS_NO_SIGNAL`
   - If no result file -> `PhaseStatus.INCOMPLETE`

**Rationale**: Context exhaustion can happen at different points in the phase lifecycle:
- **After writing the result file**: The subprocess completed all tasks, wrote the result file with EXIT_RECOMMENDATION, but then the next API call (perhaps a final summary or acknowledgment) hit the context limit. The result file is the authoritative signal -- if it says CONTINUE, the phase is genuinely done.
- **Before writing the result file**: The subprocess ran out of context while still executing tasks or before writing the completion report. This is a true INCOMPLETE.

**Pattern to match**: Same as Approach A.

**Where in `_determine_phase_status()`**: Replace the simple `exit_code != 0 -> ERROR` with:

```
if exit_code != 0:
    if detect_prompt_too_long(output_file):
        # Context exhaustion -- check if result file was written before exhaustion
        if result_file.exists():
            # Fall through to result file parsing (steps 3-5 of current logic)
            pass
        else:
            return PhaseStatus.INCOMPLETE
    else:
        return PhaseStatus.ERROR
```

This elegantly reuses the existing result file parsing logic rather than duplicating it.

**Pros**:
- Recovers completed phases that merely exhausted context on post-completion work
- No false "sprint halted" when work was actually done
- Reuses existing result file parsing -- no new classification logic needed
- Handles the most common real-world scenario (agent finishes tasks, writes report, then context dies on cleanup)

**Cons**:
- More complex control flow in `_determine_phase_status()`
- Result file could be partially written (agent started writing it, hit context limit mid-write)
- Partially written result files could contain EXIT_RECOMMENDATION: CONTINUE for only the tasks completed so far, masking incomplete work
- Requires careful handling of the "partial result file" edge case

---

### Approach C: Structured JSON Parsing of Output Tail

**Where**: New function in `monitor.py` that does structured JSON parsing rather than regex matching.

**Logic**: Read the last N lines (e.g., 50) of the NDJSON output file. Parse each line as JSON. Look for structured error events:

```python
def detect_context_exhaustion(output_path: Path) -> dict | None:
    """Detect context window exhaustion in NDJSON output.

    Returns a dict with detection metadata if found, None otherwise.
    Metadata includes: position in output (early/mid/late), approximate
    turn count before exhaustion, last task ID seen.
    """
```

The function would:
1. Parse the last 50 lines as JSON
2. Look for events where `event.get("error", {}).get("message", "")` contains "Prompt is too long"
3. Also check for `"type": "error"` with `"error": "invalid_request"` patterns
4. Extract contextual metadata: what was the last tool used, last task ID, how many assistant turns preceded the error
5. Return structured data that the caller can use for richer classification

**Classification in `_determine_phase_status()`**: Use the metadata to make a more informed decision:
- If exhaustion happened after many turns (e.g., >80% of max_turns) AND a result file exists -> treat as PASS variant
- If exhaustion happened after many turns but no result file -> INCOMPLETE (work done, report missing)
- If exhaustion happened early (e.g., <20% of max_turns) -> ERROR (something fundamentally wrong with prompt size)

**Pros**:
- Most accurate classification -- can distinguish "prompt was too large from the start" from "context grew naturally over many turns"
- Provides rich diagnostic data for the diagnostic report
- Early exhaustion (bad prompt) correctly classified as ERROR, not INCOMPLETE
- Can feed metadata into the diagnostic bundle for operator visibility

**Cons**:
- Most complex implementation
- JSON parsing of tail is more fragile than regex (malformed JSON, encoding issues)
- Requires reading and parsing potentially large chunks of the output file
- Over-engineering risk: the simpler approaches may be sufficient for all real-world cases
- Turn count from NDJSON parsing may not be perfectly accurate

---

### Approach D: Stderr-Based Detection (Alternative Vector)

**Where**: `_determine_phase_status()` with a new `error_file` parameter, or in `diagnostics.py`.

**Rationale**: The Claude CLI may write API errors to stderr rather than (or in addition to) the NDJSON stdout stream. The process module already captures stderr to `config.error_file(phase)`. If "Prompt is too long" appears in stderr, we can detect it there.

**Logic**: Read the error file (already collected at line 666-667 of executor.py). Search for the pattern.

**Pros**:
- Error files are typically small -- fast to scan
- Complements stdout-based detection (belt and suspenders)
- May catch errors that do not appear in the NDJSON stream

**Cons**:
- Uncertain whether the Claude CLI writes this specific error to stderr
- Would need empirical verification of the actual error output location
- If the error only appears in stderr, the NDJSON-based approaches would miss it
- Requires adding `error_file` as a parameter to `_determine_phase_status()`

---

## 2. Implications

### Impact on Sprint Resume Flow

The sprint resume mechanism (`SprintResult.resume_command()` at models.py:407-416) generates a command with `--start {halt_phase}`. Currently:
- `PhaseStatus.ERROR` -> sprint halts, resume command points to the failed phase
- `PhaseStatus.INCOMPLETE` -> sprint halts, resume command points to the failed phase

Both Approaches A and B would classify context exhaustion as INCOMPLETE, so the resume flow remains correct: the operator is told to resume from the phase that exhausted context. The difference is:
- Approach A: ALWAYS resumes from this phase (may re-do completed work)
- Approach B: If result file says CONTINUE, sprint continues automatically -- no resume needed for completed phases

Approach B is strictly better for resume flow because it avoids unnecessary re-execution of completed phases.

### Impact on Execution Logging and Diagnostics

The diagnostic system (`diagnostics.py`) already collects:
- `output_tail` (last 10 lines of stdout)
- `stderr_tail` (last 10 lines of stderr)
- `classification_evidence` list

Context exhaustion detection should add evidence to the diagnostic bundle. The `FailureClassifier.classify()` method (diagnostics.py:148) currently has no category for context exhaustion -- it would fall through to CRASH (exit_code != 0, low stall) or ERROR. Adding a `CONTEXT_EXHAUSTION` category to `FailureCategory` would improve diagnostic accuracy, but is not strictly required for the fix.

For all approaches, the detection function should be called from `_determine_phase_status()` BEFORE the diagnostic collector runs (lines 699-716), so the phase status is already correct when diagnostics are collected.

### Impact on Phase Transition Logic

The phase loop at executor.py:526-720 checks `status.is_failure` at line 698 to decide whether to halt. Current `is_failure` statuses: INCOMPLETE, HALT, TIMEOUT, ERROR.

- If context exhaustion -> INCOMPLETE: sprint halts (same as today's ERROR, but with correct classification)
- If context exhaustion -> PASS (Approach B, result file exists with CONTINUE): sprint continues to next phase

The Approach B path where a PASS is returned is the most impactful change to phase transition logic. It means a non-zero exit code can result in a passing phase -- which breaks the current assumption that `exit_code != 0` always means failure. This is architecturally correct (the result file is the authoritative signal, not the exit code), but may surprise operators who expect non-zero exit = failure.

### Interaction with Existing error_max_turns Detection

The existing `detect_error_max_turns()` check at line 811 is inside the `exit_code == 0` branch (reached only when exit_code is 0, no result file, but output exists). Context exhaustion exits with code 1, so these two detections are mutually exclusive in practice.

However, they are conceptually related: both represent "subprocess ran out of resources." A future refactor could unify them into a single `detect_resource_exhaustion()` function that checks for both patterns. For now, they should remain separate -- unification is a clean-up task, not a bug fix.

One subtle interaction: if a future Claude CLI version changes the exit code for context exhaustion to 0 (possible but unlikely), the existing `detect_error_max_turns` path would need to also check for prompt-too-long. The current architecture handles this correctly as long as both detection functions are called in the right order.

---

## 3. Risks

### False Positive Detection

**Risk**: The pattern "Prompt is too long" or "invalid_request" could appear in user content, task descriptions, or agent output that happens to discuss API errors (e.g., "The user reported seeing 'Prompt is too long'").

**Mitigation**:
- For regex approaches (A, B): Match within the LAST few lines only (not the entire output). Context exhaustion errors appear at the very end of the stream, since no further output is possible after the error.
- For structured JSON parsing (C): Only match when the error appears as a top-level event field, not within nested content strings.
- For all approaches: Require BOTH the error message AND exit_code != 0. A string match alone is not sufficient.
- Confidence: LOW risk. The pattern is highly specific and appears in a very constrained position (end of file). A false positive would require the very last NDJSON event to contain the exact error message string in a non-error context, AND the subprocess to exit non-zero -- an extremely unlikely combination.

### Masking Real Errors

**Risk**: A subprocess that fails for a legitimate reason (code error, assertion failure, permission denied) could coincidentally have "Prompt is too long" in its output from a prior API call or logged error, causing the real failure to be misclassified as context exhaustion.

**Mitigation**:
- Scan only the last 5-10 lines, not the entire output
- For Approach C: Require the error to be the LAST error event in the stream
- For Approach B: Even if misclassified, the result file check provides a second layer of validation. If the result file says HALT or contains failure signals, the phase still halts correctly.
- Add the detection result to the diagnostic bundle's `classification_evidence` so operators can audit the classification.

### Incomplete Work Treated as Complete

**Risk**: Approach B could classify a phase as PASS when the agent only completed some tasks. The result file might have been written early (e.g., the agent wrote a partial report before finishing all tasks), or the agent might have written EXIT_RECOMMENDATION: CONTINUE prematurely.

**Mitigation**:
- This risk exists with or without the context exhaustion fix -- a buggy agent can always write a misleading result file. The runner-constructed `AggregatedPhaseReport` (executor.py:179-282) is designed to be the authoritative source, but it only applies to the per-task subprocess loop, not the phase-level subprocess.
- For Approach B: Cross-check the result file's `tasks_total` and `tasks_passed` counts. If `tasks_passed < tasks_total`, classify as INCOMPLETE regardless of EXIT_RECOMMENDATION.
- Accept that perfect detection is impossible without re-executing the phase. The goal is "better than ERROR" -- which all approaches achieve.

### Edge Cases: Partial Writes and Corrupted Output

**Risk**: Context exhaustion might occur mid-write, producing:
- A truncated last NDJSON line (incomplete JSON)
- A partially written result file
- An output file that ends with binary garbage or encoding errors

**Mitigation**:
- `detect_error_max_turns()` already handles this by iterating from the end and skipping empty lines. The new detection function should follow the same pattern.
- Use `errors="replace"` when reading files (already done throughout the codebase).
- JSON parse errors on individual lines should be caught and skipped, not treated as detection failures.
- If no pattern is found in the last N lines, fall through to the default ERROR classification -- safe default.

### Exit Code Ambiguity

**Risk**: Exit code 1 is generic. Many different Claude CLI failures produce exit code 1. Relying on exit code alone is insufficient -- which is why pattern detection is necessary. But the converse risk is: what if a future Claude CLI version changes the exit code for context exhaustion to something else (e.g., 2, or a specific code like 137)?

**Mitigation**:
- Do NOT rely on exit code for detection. Use exit code only as a precondition (`exit_code != 0`), not as the classifier.
- The pattern match on the output content is the authoritative signal.
- Document the expected API error format so future maintainers know what to update if the format changes.

---

## 4. Detailed Sub-Approach Analysis

### Approach A: Simple Pattern Match + INCOMPLETE

**Implementation sketch** (monitor.py):
```
PROMPT_TOO_LONG_PATTERN = re.compile(r'"Prompt is too long"')

def detect_prompt_too_long(output_path: Path) -> bool:
    # Read last 10 non-empty lines
    # Check each for PROMPT_TOO_LONG_PATTERN
    # Return True if found
```

**Implementation sketch** (_determine_phase_status):
```
if exit_code == 124:
    return PhaseStatus.TIMEOUT
if exit_code != 0:
    if detect_prompt_too_long(output_file):
        return PhaseStatus.INCOMPLETE
    return PhaseStatus.ERROR
# ... rest unchanged
```

**Effort**: ~20 lines of code. 1 new function, 3 new lines in _determine_phase_status.

**Test coverage needed**:
- Unit test for detect_prompt_too_long with positive and negative cases
- Unit test for _determine_phase_status with exit_code=1 + prompt-too-long output
- Integration test with a mock output file containing the error pattern

### Approach B: Pattern Match + Result File Fallthrough

**Implementation sketch** (_determine_phase_status):
```
if exit_code == 124:
    return PhaseStatus.TIMEOUT
if exit_code != 0:
    if not detect_prompt_too_long(output_file):
        return PhaseStatus.ERROR
    # Context exhaustion: fall through to result file parsing
    # (exit_code != 0 but we treat it like exit_code == 0 for result file logic)

if result_file.exists():
    # ... existing result file parsing (unchanged)

if output_file.exists() and output_file.stat().st_size > 0:
    if detect_error_max_turns(output_file):
        return PhaseStatus.INCOMPLETE
    if detect_prompt_too_long(output_file):  # redundant but defensive
        return PhaseStatus.INCOMPLETE
    return PhaseStatus.PASS_NO_REPORT

return PhaseStatus.ERROR
```

**Effort**: ~30 lines of code. 1 new function, restructured _determine_phase_status control flow.

**Test coverage needed**:
- All Approach A tests, plus:
- Test: exit_code=1 + prompt-too-long + result file with CONTINUE -> PASS
- Test: exit_code=1 + prompt-too-long + result file with HALT -> HALT
- Test: exit_code=1 + prompt-too-long + no result file -> INCOMPLETE
- Test: exit_code=1 + prompt-too-long + partial/empty result file -> INCOMPLETE or PASS_NO_SIGNAL

### Approach C: Structured JSON Parsing

**Implementation sketch** (monitor.py):
```
def detect_context_exhaustion(output_path: Path) -> dict | None:
    lines = read_last_n_lines(output_path, 50)
    for line in reversed(lines):
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        # Check for API error structure
        if is_context_exhaustion_event(event):
            return {
                "detected": True,
                "line_position": ...,
                "turns_before_error": ...,
                "last_task_id": ...,
            }
    return None
```

**Effort**: ~60-80 lines of code. Multiple new functions, richer return type, additional diagnostic integration.

**Test coverage needed**: All Approach B tests, plus metadata validation tests, malformed JSON edge cases, early vs late exhaustion classification.

---

## 5. Recommendation

**Primary recommendation: Approach B** (Pattern Match + Result File Fallthrough).

**Rationale**:

1. **Correctness**: Approach B handles the most common real-world scenario correctly. In practice, context exhaustion usually happens late in a phase after most or all tasks are done. If the agent wrote the result file before exhaustion, the sprint should continue -- not halt and force a re-run.

2. **Safety**: When no result file exists, Approach B falls back to INCOMPLETE (same as Approach A), which halts the sprint. This is the safe default for genuinely incomplete work.

3. **Simplicity**: Approach B is only marginally more complex than Approach A but significantly more capable. Approach C is over-engineered for the problem at hand -- the additional metadata it provides is useful for diagnostics but not necessary for correct classification.

4. **Consistency**: The control flow restructuring in Approach B makes `_determine_phase_status()` more principled. Instead of "exit_code != 0 means ERROR, period," the function becomes "exit_code != 0 means ERROR, UNLESS we can identify a recoverable condition." This pattern is already established for exit_code == 124 (TIMEOUT).

5. **Incremental path**: Approach B can be enhanced later with Approach C's structured parsing if the regex-based detection proves insufficient. The function signature (`detect_prompt_too_long(output_path) -> bool`) can be evolved to return richer metadata without changing the calling code.

**Secondary recommendation**: Regardless of which approach is chosen, also add `CONTEXT_EXHAUSTION` to `FailureCategory` in `diagnostics.py` so the diagnostic report correctly identifies the root cause rather than classifying it as CRASH or ERROR.

**Pattern to use**: `r'"Prompt is too long"'` as a regex on the last 10 non-empty lines. This is specific enough to avoid false positives and simple enough to maintain. If the Anthropic API changes its error message, the regex is a single-line update.

**Stderr consideration**: As a belt-and-suspenders measure, also scan `error_file` for the pattern. This requires adding an `error_file` parameter to `_determine_phase_status()`, which is a clean change since the caller already has access to `config.error_file(phase)`.

---

## 6. Open Questions for Implementation

1. **What is the exact NDJSON structure of a "Prompt is too long" error?** The brainstorm assumes it contains the literal string `"Prompt is too long"` as a JSON string value. This should be verified by examining actual Claude CLI output from a context exhaustion event. If the structure differs, the regex pattern needs adjustment.

2. **Does the error appear in stdout (NDJSON), stderr, or both?** The pipeline process redirects stdout to the output file and stderr to the error file. If the error only appears in stderr, the stdout-based detection functions will miss it entirely.

3. **Should INCOMPLETE trigger an automatic retry with a reduced prompt?** Currently INCOMPLETE just halts. A future enhancement could have the executor strip earlier context and retry the phase, but that is out of scope for this fix.

4. **Should we add a new PhaseStatus (e.g., CONTEXT_EXHAUSTED) instead of reusing INCOMPLETE?** A dedicated status would improve diagnostic clarity but adds complexity. Since INCOMPLETE already has the correct `is_failure` semantics, reusing it is pragmatic. The diagnostic bundle's `classification_evidence` can carry the specificity.

5. **What about the per-task subprocess loop (execute_phase_tasks)?** The task-level loop at executor.py:349-446 has its own exit code classification at lines 417-422. Context exhaustion could also happen at the task level. Should `detect_prompt_too_long` be called there too? The answer depends on whether per-task subprocesses can realistically hit the context limit (they have shorter prompts and fewer turns, so it is less likely but not impossible).
