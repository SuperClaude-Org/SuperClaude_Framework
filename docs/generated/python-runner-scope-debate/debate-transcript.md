# Adversarial Debate: Python Runner Task Execution Scope

## Round 1: Opening Arguments

### Advocate B1 (Shell-only)

**Position**: Python should do the minimum: run shell commands and capture raw output. Everything else stays in Claude.

**Arguments by dimension**:

1. **Complexity**: B1 requires ~80 LoC. A `subprocess.run()` wrapper with output capture is trivially correct. No template engine, no conditional logic, no step dispatcher. Maintenance burden is near zero.

2. **Reliability**: The fewer decisions Python makes, the fewer bugs Python can have. Shell command execution is well-understood. Writing stdout to a file is well-understood. There is no conditional logic to get wrong.

3. **Generality**: B1 handles ANY future task type because it makes no assumptions about what the output means. New task types with different output formats, different success criteria, or different artifact structures all work without changing the Python code.

4. **Token efficiency**: B1 does require a Claude session to interpret results, costing ~2-5K tokens per phase. But this is a one-time cost per sprint, and the interpretation session is simple (read files, write evidence).

5. **Architectural fit**: B1 slots cleanly into the `_subprocess_factory` injection point. Minimal surface area change. Does not require new models or new abstractions.

### Advocate B2 (Shell + Artifacts)

**Position**: Python should handle execution AND artifact writing, but defer judgment to Claude.

**Arguments by dimension**:

1. **Complexity**: B2 adds ~80 LoC over B1 for template-based artifact writing. The templates are static strings with variable interpolation -- not complex. Total ~160-200 LoC is still modest.

2. **Reliability**: B2 produces deterministic artifact files. The artifact format is fixed and testable. The only non-deterministic part (WORKING/BROKEN classification) is left to Claude where LLM judgment is appropriate.

3. **Generality**: B2 handles any task that produces stdout/stderr/exit_code because the artifact template is generic. New classification criteria can be added to the Claude interpretation phase without touching Python.

4. **Token efficiency**: B2 reduces Claude's work significantly. Instead of Claude reading raw output files and writing structured artifacts, Claude only needs to read pre-formatted evidence files and add a one-word classification. Estimated savings: 40-60% of the interpretation session tokens.

5. **Architectural fit**: B2 uses `_subprocess_factory` plus a new `ArtifactWriter` class. The writer is a pure function (input -> file), easily testable, and does not couple to sprint models.

### Advocate B3 (Full mini-executor)

**Position**: Python should handle the entire task lifecycle for empirical/EXEMPT tasks. No Claude session needed.

**Arguments by dimension**:

1. **Complexity**: B3 is ~310-410 LoC, the largest variant. However, the "conditional logic" for Phase 1 tasks is trivial: `exit_code == 0 and len(stdout) > 0`. This is not AI-level judgment -- it is a deterministic check that a 3-line `if` statement handles correctly.

2. **Reliability**: B3 is the MOST reliable because it eliminates LLM non-determinism entirely. A Python `if exit_code == 0` check returns the same result every time. A Claude session interpreting "is this output non-empty?" can hallucinate, get confused by edge cases, or produce inconsistent formatting.

3. **Generality**: B3 handles Phase 1's empirical tasks completely. For future tasks with more complex judgment needs, the runner can fall back to `ClaudeProcess`. The mini-executor is scoped to EXEMPT-tier tasks where acceptance criteria are machine-checkable.

4. **Token efficiency**: B3 saves 100% of the Claude API tokens for Phase 1 execution. Zero `claude --print` subprocesses for empirical tasks. For a 14-task Phase 1, this saves 14 subprocess spawns plus the interpretation session. At ~$0.01-0.05 per task, this is $0.14-0.70 saved per sprint run.

5. **Architectural fit**: The `_subprocess_factory` injection point already supports this. `TaskResult` already has all the fields B3 needs to populate. `AggregatedPhaseReport` already derives status from `TaskResult`. B3 is the variant that most fully uses the existing model infrastructure.

---

## Round 2: Cross-Examination

### B1 challenges B3

**B1**: "Your 310-410 LoC estimate understates the real complexity. You need a step parser to extract shell commands from markdown task descriptions, a step dispatcher to route PLANNING/EXECUTION/VERIFICATION/COMPLETION steps, and conditional logic that must match the acceptance criteria in each task. When someone writes a new task with `if output contains 'ERROR' then BROKEN`, you need to update the Python code."

**B3 response**: "The step parser concern is valid but overblown. Phase 1 tasks have a structured format with explicit `[EXECUTION]` tags. Extracting the shell command from `Run \`claude --print -p \"hello\" --max-turns 1\`` is a regex, not a natural language parser. For the conditional logic: the acceptance criteria for EXEMPT empirical tasks are machine-checkable by definition (exit code + output presence). If a future task requires LLM judgment, it should not be EXEMPT tier -- it should be STANDARD or STRICT, and the existing `ClaudeProcess` path handles it."

### B3 challenges B1

**B3**: "You claim generality, but B1 cannot actually execute Phase 1 tasks at all without solving the deadlock problem. If Python only runs the shell command and then delegates to Claude for interpretation, that Claude session itself needs to run the shell commands to verify results. You have not eliminated the nested-claude problem -- you have just moved it."

**B1 response**: "Incorrect. B1 runs the shell command in Python (solving the deadlock), captures stdout/stderr/exit_code to files, and then a SEPARATE Claude session reads those files and writes evidence.md. The interpretation session does not need to re-run any commands -- it reads pre-captured output. The deadlock only occurs when Claude tries to spawn claude inside itself."

### B2 challenges B3

**B2**: "Your conditional logic is brittle. Today it is `exit_code == 0`. Tomorrow someone writes a task where success means 'output contains exactly 3 lines' or 'output matches regex X'. You are building a mini rules engine in Python that will accumulate special cases."

**B3 response**: "For EXEMPT-tier empirical tasks, the acceptance criteria pattern is consistent: run command, check exit code, check output is non-empty. I do not need a rules engine -- I need a simple check function. If a task requires regex matching, that is a 2-line addition to the check function, not a rules engine. And the alternative (B2) still requires a Claude session for this trivial check, which is like hiring a lawyer to verify that a light switch is in the ON position."

### B1 challenges B2

**B1**: "You do the hard work (artifact writing) but skip the easy work (conditional classification). This means you still need a Claude session, but the session has almost nothing to do -- read a pre-formatted file and write one word. The token cost of spawning that session (prompt overhead, context loading) may exceed the cost of the actual classification. You have the worst cost/benefit ratio of all three."

**B2 response**: "The value of B2 is not in the current cost savings but in the artifact trail. B2 produces machine-readable, deterministic evidence files that are useful for debugging regardless of who does the classification. If B3's conditional logic misclassifies a result, you have no structured artifact to diagnose why. B2's artifacts are the debugging checkpoint that both B1 and B3 lack."

---

## Round 3: Convergence Assessment

### Per-Point Scoring Matrix

| Dimension | B1 | B2 | B3 | Convergence |
|-----------|----|----|-----|-------------|
| Complexity (lower is better) | 9/10 | 7/10 | 5/10 | Agreed: B1 < B2 < B3 in complexity. No dispute. (100%) |
| Reliability | 6/10 | 7/10 | 9/10 | Partial: B1/B2 argue simplicity=reliability. B3 argues determinism=reliability. (60%) |
| Generality | 8/10 | 7/10 | 6/10 | Partial: B1 handles unknown future tasks. B3 handles known empirical tasks better. Different optimization targets. (50%) |
| Token efficiency | 4/10 | 6/10 | 10/10 | Agreed: B3 > B2 > B1. No dispute on ordering. (100%) |
| Architectural fit | 7/10 | 7/10 | 9/10 | Partial: All use `_subprocess_factory`. B3 best uses existing `TaskResult` fields. (70%) |

### Key Points of Agreement

1. All three variants solve the nested-claude deadlock by running shell commands in Python.
2. All three use the `_subprocess_factory` injection point in `execute_phase_tasks()`.
3. B3 saves the most tokens. B1 costs the most tokens. This is undisputed.
4. B1 is the simplest to implement. B3 is the most complex. This is undisputed.
5. The conditional logic in B3 for EXEMPT-tier tasks is genuinely simple (exit code + output presence check).

### Key Points of Disagreement

1. **Reliability framing**: B1 equates simplicity with reliability. B3 equates determinism with reliability. Both are valid but optimize for different failure modes (Python bugs vs LLM variance).
2. **Generality scope**: B1 optimizes for unknown future task types. B3 optimizes for the known Phase 1 task type. The right answer depends on how stable the task format is.
3. **B2's value**: B1 and B3 both argue B2 occupies an awkward middle ground. B2 argues its artifact trail has independent value.

### Overall Convergence Score: 76%

---

## Unresolved Conflicts

1. Whether "simplicity = reliability" or "determinism = reliability" is the correct framing for EXEMPT-tier empirical tasks.
2. Whether the task format will change frequently enough to justify B1's generality premium.
3. Whether B2's artifact trail has sufficient independent value to justify its existence as a distinct variant.
