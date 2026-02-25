# Adversarial Debate: Theory RC-1
## `allowed-tools` in Frontmatter Enables Tool-Call Exhaustion

**Date**: 2026-02-24
**Evaluator**: Root Cause Analyst (adversarial debate agent)
**Theory Under Review**: RC-1 from `rca-unified.md`
**Claim**: Adding `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` to the `task-unified.md` YAML frontmatter is the primary root cause. The previous version had NO `allowed-tools`, so the model had to produce text output. Now the model consumes all turns making tool calls and never produces classification text.

---

## Part 1: Prosecution — The Case FOR RC-1 as Root Cause

### Argument 1: The Discriminating Variable

The prosecution's strongest argument is one of experimental design: `allowed-tools` is the single cleanest delta between the previous state (9.2% pass rate) and the current state (0% pass rate). The Change Diff Summary in `rca-unified.md` enumerates all structural differences between the 567-line previous version and the current 107+308-line split version. Of all the changes listed, `allowed-tools` is the only change that directly grants the model agency to take tool-call actions rather than producing text output. Without `allowed-tools`, the model operates in a text-only output mode when invoked via `claude -p`. With `allowed-tools`, the model can initiate tool call sequences that consume all available turns without ever producing classification text.

This is a strong isolation argument. If you accept that the previous version had no `allowed-tools` field, and that `claude -p` behavior differs materially based on whether tools are available, then this single change is causally sufficient to explain the transition from partial completion to total timeout.

### Argument 2: The Causal Mechanism Is Concrete and Plausible

The prosecution can articulate a step-by-step mechanism with no hand-waving:

1. The model receives `claude -p "fix security vulnerability in auth module"` with 9 tools available.
2. The model reads `task-unified.md`, which says "Before ANY text, emit classification header" but ALSO lists 9 tools and invokes `> Skill sc:task-unified-protocol`.
3. The model interprets the task literally: there is a security vulnerability in an auth module. Its training and the 23K tokens of SuperClaude context direct it toward actual task execution (activate project, grep for auth module, read code, plan fix).
4. Turn 1: `Grep` for auth module.
5. Turn 2: `Skill sc:task-unified-protocol` invocation (loads 308 more lines, consuming an entire turn).
6. Turns 3-5: Protocol steps from the 11-step STRICT execution path.
7. All 5 turns consumed. No text output. Timeout.

Each step in this chain is supported by observable model behavior patterns. The model is not malfunctioning — it is following its instructions coherently, just not the instructions the test harness expected it to follow.

### Argument 3: The Evidence Metrics Are Consistent

The RCA documents zero classification scores across all 48 tests. The `no_raw_dump = 1.0` metric — meaning the model engaged with the command rather than dumping it — combined with `skill_invoked = 0.0` and `protocol_flow = 0.0` suggests the model was consuming turns on preliminary tool calls before ever reaching the Skill invocation step. This is precisely what RC-1 predicts: the tool calls happen first, the Skill is never invoked because turns run out, and the classification header is never emitted because it was planned for after tool investigation.

### Argument 4: The Timing Pattern Is Definitive

Every behavioral test duration matches its computed timeout ceiling to within 200ms (±163ms to ±200ms). This is not a distribution of timeouts — it is a wall. This wall is only possible if every single process consumes its entire time budget without completing. A model that can produce classification text rapidly (which takes seconds, not minutes) would not uniformly hit the ceiling. The ceiling-hugging behavior is consistent with: (a) the model never reaches the text output phase, and (b) the turns are being consumed by tool calls that individually take 45-60 seconds under load. RC-1 provides the mechanism for (a).

### Argument 5: Counterfactual Is Strong

Remove `allowed-tools` from the frontmatter. The model now has no tools available. The only action it can take is text output. It reads the command, sees the classification requirement, and outputs the classification header. This is the exact behavior the test harness expects. The fix is a one-line change and is predicted to restore test completion. The counterfactual is simple, testable, and has high expected impact.

---

## Part 2: Defense — The Case AGAINST RC-1 as Sole Root Cause

### Challenge 1: The Model Can Still Output Text on Turn 1 Before Making Tool Calls

This is the prosecution's most significant logical gap. Nothing in the `allowed-tools` mechanism *prevents* the model from outputting text before making any tool call. The classification header instruction is explicit: "Before ANY text, emit this exact header." A model with tools available could, in principle:

- Turn 1: Emit the classification header as text output.
- Turn 2: Call `Skill sc:task-unified-protocol`.
- Turns 3-5: Execute protocol steps.

If the model did this, the test would pass (classification score > 0) AND the model would have tools available. The fact that the model does NOT emit the classification header first is not explained by `allowed-tools` alone. It requires an additional assumption: that the model consistently prioritizes tool calls over text output when tools are available, regardless of explicit instructions.

This additional assumption is unproven by the available evidence. The RCA acknowledges the "MANDATORY FIRST OUTPUT" instruction exists in the command file. Why does the model ignore it? RC-1 attributes this to the dual-interpretation problem and contradictory instructions, but these are separate mechanisms from `allowed-tools` itself. The defense argues: `allowed-tools` enables tool exhaustion, but the reason the model ignores the immediate-text instruction is a separate causal factor (instruction contradiction, context override from SuperClaude's 23K tokens, or model behavior under `claude -p`).

Put simply: the prosecution is conflating two distinct failures — (a) tools consuming turns, and (b) the model not outputting text first. RC-1 explains (a) but does not fully explain (b). A model that outputs the header first and then exhausts tools would still pass the classification test.

### Challenge 2: `allowed-tools` Is Not the Only Discriminating Variable

The RCA's Change Diff Summary lists multiple simultaneous changes between the previous and current versions:

| Change | Previous | Current |
|--------|----------|---------|
| `allowed-tools` | Not present | 9 tools listed |
| Skill invocation | None | Line 70 |
| "MANDATORY FIRST OUTPUT" | Not present | Lines 46-48 |
| Classification logic | Implicit | Explicitly inlined |
| Instruction volume | 567 lines, self-contained | 107 + 308 = 415 lines, split |

The RCA claims `allowed-tools` is "the ONLY structural change that directly enables tool-call consumption of turns" — but this is not accurate. The Skill invocation at line 70 (`> Skill sc:task-unified-protocol`) is also a new addition that was NOT present in the previous version. The Skill invocation is itself a tool-consuming step. Even without `allowed-tools`, if `Skill` were in the allowed tools list, the model would still invoke the Skill and potentially get lost in the 308-line protocol.

Furthermore, the `mcp-servers` field is also new: `[sequential, context7, serena, playwright, magic, morphllm]`. Six MCP servers are now declared in the frontmatter. This means the model is initialized with additional tool surfaces (MCP tool calls) that did not exist in the previous version. The prosecution needs to explain why `allowed-tools` is the discriminating variable rather than MCP server availability.

### Challenge 3: The 9.2% Pass Rate in the Previous Version Is Not a Clean Baseline

The RCA references "some tests completed in 20-97s → 9.2% pass rate" for the previous version, but the conditions under which those tests were run may not be identical to the current test conditions. If the previous version was tested:

- Without the full 23K token SuperClaude context (CLAUDE.md at-references),
- At lower concurrency (not 30 processes),
- Without `alwaysThinkingEnabled: true`,
- Without 6 MCP servers declared in frontmatter,

then the 9.2% vs 0% comparison is confounded. The prosecution cannot cleanly attribute the degradation to `allowed-tools` alone because multiple other variables changed simultaneously (CF-2, CF-3, CF-4, RC-2 all potentially differ between test runs).

### Challenge 4: RC-3 (Timeout Budget) May Be Sufficient Alone

If the startup overhead for a single `claude -p` process is 30-60 seconds, and the per-turn budget for opus tests is 45 seconds (225s total for 5 turns), then even a model that immediately outputs the classification header on Turn 1 might not complete within the budget. Consider:

- Startup overhead: 30-60s consumed before first token.
- Turn 1 first-token latency with 23K context under 30x concurrency: 15-30s.
- Total before any output: potentially 45-90s — already at or exceeding the per-turn budget for Turn 1.

If this analysis is correct, the test would timeout even if the model produces the classification header immediately, because the process itself cannot receive that output within the timeout window. In this scenario, removing `allowed-tools` would not fix the 0% pass rate — RC-3 is the dominant cause.

The RCA provides Verification Experiment 5 for exactly this case: "Keep `allowed-tools` but set `max_turns=1` — if timeout persists, RC-3 is dominant." This experiment has not been run, meaning the prosecution cannot exclude RC-3 as sufficient alone.

### Challenge 5: The `--dangerously-skip-permissions` Flag Is a Confound

The RCA mentions `--dangerously-skip-permissions` in the context of the dual-interpretation problem. If this flag was NOT present in the previous test runs but IS present in the current runs, it would independently change model behavior — the model now has permission to execute tool calls it would previously decline, independent of `allowed-tools`. The prosecution does not isolate this variable.

### Challenge 6: Classification Score = 0.0 Does Not Prove the Mechanism

The prosecution interprets `classification scores = 0.0` as "zero text output produced." But there is an alternative interpretation: the classification output WAS produced, but the test harness failed to capture it because the process was killed (SIGKILL) and the output buffer was discarded. Under high memory pressure (30 concurrent Node.js processes), pipe buffers can be dropped. The `proc.kill()` (SIGKILL) identified in `runner.py` does not flush stdout before terminating the child process. This means classification text could theoretically have been produced but not captured by the harness.

This is a weaker challenge (SIGKILL-induced output loss is a known issue), but it introduces uncertainty about whether the diagnosis of "no text output" is the correct interpretation of `classification_score = 0.0`.

---

## Part 3: Rebuttal — Prosecution's Response to Defense Challenges

### Response to Challenge 1 (Model can output text first):

The defense correctly identifies that `allowed-tools` does not PREVENT text output on Turn 1. However, the prosecution points to the empirical result: in 48/48 tests across both models, the model never outputs text first. This is not random failure — it is a systematic behavioral pattern. The most parsimonious explanation is that the combination of `allowed-tools` + the instruction to invoke a Skill + the 23K SuperClaude context primes the model toward tool-first behavior. The SuperClaude ORCHESTRATOR.md explicitly instructs: "Understand → Plan (with parallelization analysis) → TodoWrite (3+ tasks) → Execute → Track → Validate" — none of these steps are text classification. The model is following its primary training, which has been overridden by the SuperClaude framework away from simple text output.

### Response to Challenge 2 (Not the only discriminating variable):

The defense is correct that Skill invocation and MCP servers are also new. But the prosecution maintains that `allowed-tools` is the proximate cause: without tools, the model cannot invoke the Skill, cannot call MCP servers, cannot run Grep. `allowed-tools` is the gate that enables all other tool-consuming behavior. Removing it removes all downstream tool consumption simultaneously.

### Response to Challenge 3 (Confounded baseline):

The prosecution acknowledges this weakness. The comparison between previous and current test conditions may not be clean. However, the 100% timeout rate vs any partial completion rate is itself evidence that something fundamental changed. The prosecution holds that `allowed-tools` is the most parsimonious explanation for the fundamental change, while acknowledging that RC-2 and RC-3 contribute to the magnitude.

### Response to Challenge 4 (RC-3 may be sufficient alone):

The prosecution partially concedes this point. RC-3 (timeout budget) may be sufficient to cause timeout even after removing `allowed-tools`, IF the startup overhead consistently exceeds the per-turn budget. Verification Experiment 5 would settle this. The prosecution's position is that removing `allowed-tools` is necessary but may not be sufficient — both RC-1 and RC-3 must be fixed to restore pass rate.

### Response to Challenges 5 and 6:

The prosecution acknowledges `--dangerously-skip-permissions` as an uncontrolled variable and the SIGKILL output loss as a measurement uncertainty. These reduce the evidentiary strength of the `classification_score = 0.0` metric, though not enough to invalidate the theory.

---

## Part 4: Verdict

### Synthesis

RC-1 (`allowed-tools`) is a real and significant contributing cause of the 0% pass rate. The mechanism is sound: tools enable turn consumption, and the evidence shows all turns are consumed. The prosecution correctly identifies that `allowed-tools` is the single structural change that most directly enables model behavior incompatible with the test harness's expectations.

However, RC-1 is not the sole root cause and is not fully sufficient:

1. The model could still output text before tool calls — the failure to do so implicates RC-2 (SuperClaude context override) and CF-1b (classification instruction triplication/deferral) as co-causes.
2. RC-3 (insufficient timeout budget) may independently cause timeouts regardless of tool availability, meaning removing `allowed-tools` may not restore 0% → non-zero pass rate without also fixing timeouts.
3. Multiple variables changed simultaneously between the previous and current versions, making clean attribution difficult.
4. Verification Experiment 5 (keep tools, set max_turns=1) has not been run and could alter the verdict significantly.

The correct characterization is: **RC-1 is a necessary component of the failure compound but is not sufficient alone, and its relative contribution cannot be precisely quantified without running the proposed verification experiments.**

### Scores

| Dimension | Score (0-10) | Rationale |
|-----------|-------------|-----------|
| **Evidence Strength** | 6 | Strong circumstantial evidence (correlation between version change and failure, plausible mechanism, consistent timing data). Weakened by: uncontrolled variables between test runs, unverified assumption that model never outputs text before tool calls, SIGKILL output loss as alternative explanation for score=0.0. No controlled experiment isolating `allowed-tools` as sole variable has been run. |
| **Root Cause Likelihood** | 7 | Very likely a significant contributing cause. The mechanism is plausible and the change is clearly the most direct enabler of tool consumption. However, reduced from 10 because RC-3 alone may be sufficient to cause timeout, and the model's failure to output text first implicates RC-2 and CF-1b as independent contributing causes. The 95% likelihood stated in the RCA is slightly overstated given uncontrolled variables. |
| **Fix Impact** | 6 | Removing `allowed-tools` will likely improve pass rate, but the improvement may be partial, not complete. If RC-3 (startup overhead exceeding per-turn budget) is the dominant cause, removing `allowed-tools` could change the failure mode (model now produces text but timeout still occurs before output is captured) without changing the 0% pass rate. Confident improvement only if RC-3 is also addressed simultaneously. |
| **Fix Feasibility** | 9 | Trivial one-line change: remove `allowed-tools` from the YAML frontmatter. No architectural change required. Risk: removing tools changes the production behavior of `/sc:task` for actual users (not just tests), which may break the command's intended task execution capability. A test-only fix (strip `allowed-tools` in test context) would be preferable. |

### Overall Assessment

RC-1 is a high-priority fix candidate with strong theoretical support but insufficient empirical isolation. It should be fixed immediately as the most likely single improvement to pass rate. However, the prosecution's claim that it is "the primary root cause" and that `allowed-tools` is "the ONLY structural change that directly enables tool-call consumption" overstates the case. The true failure is a compound of RC-1 + RC-2 + RC-3, where RC-1 provides the mechanism for tool exhaustion, RC-2 provides the behavioral priming that makes the model choose tools over text, and RC-3 ensures that even if one or two tests produce output, they still timeout before the harness captures it.

**Recommended action**: Run Verification Experiment 1 (remove `allowed-tools`, max_turns=2) first, followed by Experiment 5 (keep `allowed-tools`, max_turns=1) to quantify RC-1's independent contribution. Do not close RC-3 based solely on fixing RC-1.

---

*Debate conducted by: Root Cause Analyst agent*
*Evidence basis: `rca-unified.md`, `src/superclaude/commands/task-unified.md`, `src/superclaude/skills/sc-task-unified-protocol/SKILL.md`*
*Methodology: Adversarial prosecution/defense with structured verdict*
