# Adversarial Debate: RC-3 — Insufficient Timeout Budgets Ignoring Fixed Startup Cost

**Date**: 2026-02-24
**Theory Under Examination**: RC-3 — Timeout formula `per_turn * max_turns` ignores ~30-60s fixed startup cost, producing budgets too tight for even a single turn to complete.
**Assigned Verdict Role**: Adversarial evaluator (prosecution + defense + verdict)

---

## Claim Summary

RC-3 asserts that the timeout formula is architecturally flawed: it computes `per_turn * max_turns` without accounting for fixed startup overhead components (binary startup, CLAUDE.md `@`-ref parsing, MCP server initialization, API first-turn latency with ~23K context). The claimed consequence is that all processes are killed by the timeout — not by turn exhaustion — proven by the observation that every test duration matches its timeout ceiling to within 200ms.

**Current timeout budgets under scrutiny**:
- Opus B tests: 45s × 5 turns = 225s
- Sonnet B tests: 60s × 5 turns = 300s
- Opus W tests: 72s × 5 turns = 360s (inferred)
- Sonnet W tests: 120s × 5 turns = 600s

---

## PROSECUTION: The Case FOR RC-3

### Argument P-1: The 200ms Match Is Forensic-Grade Evidence

The duration/timeout match data is the strongest evidentiary pillar of this theory:

| Test | Model | Timeout | Actual Duration | Delta |
|------|-------|---------|-----------------|-------|
| B1 | opus | 225,000ms | 225,163ms | +163ms |
| B1 | sonnet | 300,000ms | 300,179ms | +179ms |
| W1 | opus | 360,000ms | 360,200ms | +200ms |
| W4 | sonnet | 600,000ms | 600,151ms | +151ms |

These deltas are not statistical noise — they are the wall-clock overhead of Python's `asyncio` timeout machinery executing `proc.kill()` (SIGKILL) after the timeout fires. The 150-200ms overhead is consistent with OS process termination latency: the `asyncio` event loop fires the timeout callback, invokes `proc.kill()`, waits for `proc.communicate()` to return after SIGKILL delivery. This is a known latency band for Linux process teardown under asyncio.

**Implication**: No test ran to completion. Every process was externally terminated by the harness. This is a fact, not a hypothesis.

### Argument P-2: The Startup Overhead Math Is Plausible and Validated

The RCA provides live-test confirmation: "a trivial single-turn haiku call takes >30s from the repo root." This is a controlled baseline measurement. Breaking down the overhead:

- **Binary startup (2-5s)**: Node.js-based CLI with npm dependency resolution. The `claude` binary is a Node.js script; cold startup includes V8 initialization, module loading, CLI argument parsing.
- **CLAUDE.md `@`-ref parsing (5-10s)**: 8 `@`-references, each requiring a filesystem read. Total parsed content: ~93,830 bytes (~23,500 tokens). The parser must resolve relative paths, read files, concatenate context, tokenize.
- **MCP server initialization (10-30s)**: The mcp.json configures 2 servers. The command frontmatter declares up to 6. Each MCP server is a separate `npx` process: npm registry resolution for `@latest` tags, download if not cached, Node.js subprocess spawn, handshake protocol. At 30x concurrency, npm registry may rate-limit.
- **API first-turn latency (15-30s)**: With ~23,500 tokens of context, the first API call requires serialization, HTTP transport, model processing of 23K+ tokens before producing even a single output token. At controlled rate-limit conditions, this alone can exceed 20s.

**Total startup overhead: 32-75s** (live-test confirmed floor: >30s).

Against a 225s total budget for Opus B tests:
- Best case: 225s - 32s = 193s for actual turns
- Worst case: 225s - 75s = 150s for actual turns

This still leaves 30-150s per turn for 5 turns — which seems plausible. But this arithmetic assumes turns can be parallelized or that startup is the only bottleneck, which it is not. See defense counter-argument for why this cuts against RC-3 being the primary cause.

### Argument P-3: The Formula Is Structurally Wrong Regardless of Whether It Is the Primary Cause

The formula `timeout = per_turn * max_turns` is demonstrably incorrect as a general model:

- It assumes every second of wall clock time is available for turn execution.
- It treats startup as free.
- It assumes MCP initialization completes before the timeout clock starts.

Even if RC-1 (allowed-tools) is the primary cause of the current 0% pass rate, fixing RC-1 without fixing the timeout formula will produce tests that START completing but may STILL timeout on:
- Slow API days
- Cold MCP cache misses (npm `@latest` resolution)
- High concurrency contention periods
- Systems with slower disk I/O (CLAUDE.md parsing overhead)

The fix (add `_STARTUP_OVERHEAD = 60` constant) is a 3-line change with zero risk of regression. Its correctness as a formula improvement is independent of whether RC-3 is the primary cause of the current failure.

### Argument P-4: The Previous Version's 20-97s Completions Are Misleading

The previous version showed "some tests completed in 20-97s" with a 9.2% pass rate. This is cited as evidence that the timeout was NOT the bottleneck then. But the circumstances were likely different:
- Previous version likely ran without the 9-tool `allowed-tools` field
- Previous version likely had `max_turns=3` not 5
- Previous version may have run from a different working directory (without CLAUDE.md `@`-refs)
- Previous version may have had different MCP configuration

The 20-97s completions prove that SOME runs escaped tool-call exhaustion — not that startup overhead was absent. A test completing in 20s after a 32-75s startup is mathematically impossible, suggesting the startup estimate for those runs was significantly lower (perhaps no MCP, no heavy CLAUDE.md, earlier code version).

**Prosecution Summary**: RC-3 is real. The formula is wrong. The fix is correct and risk-free. The evidence (200ms ceiling match) definitively proves all tests were killed by timeout — not by natural completion.

---

## DEFENSE: The Case AGAINST RC-3 as Primary Root Cause

### Argument D-1: Killed by Timeout Does Not Prove Timeout Was the Bottleneck

This is the central logical fallacy in RC-3's claim. The argument runs:
1. All tests were killed by timeout (TRUE — proven by 200ms delta data)
2. Therefore, insufficient timeout budget is the root cause (INVALID INFERENCE)

Consider: if the model is stuck in an infinite tool-call loop (RC-1), it will be killed by timeout regardless of whether that timeout is 225s or 22,500s. The process being killed at the ceiling proves the harness killed it — it does NOT prove that more time would have allowed completion.

The discriminating question is: **Would doubling the timeout produce completions?**

Under RC-1's mechanism (tool-call exhaustion consuming all 5 turns), the model burns through:
- Turn 1: `Grep` to find auth module
- Turn 2: `Skill sc:task-unified-protocol` invocation (loads 308 lines)
- Turn 3-5: Protocol steps

5 turns at 30-60s each = 150-300s of turn execution time. With 32-75s startup, total = 182-375s. The Opus B timeout is 225s. So for a FAST run, the process might naturally exit after 5 turns within the timeout window. For a SLOW run, it gets killed. In both cases, the output is useless (tool call results, not classification text). The timeout budget is not the discriminating variable — RC-1 is.

**Critical Test**: Experiment 5 from the RCA: "Keep allowed-tools but set max_turns=1." If a single turn completes within 225s (even one where the model makes a tool call), it proves the startup overhead is absorbed within the existing budget. If max_turns=1 still timeouts, then RC-3 is severe. The RCA acknowledges this experiment would "identify whether RC-3 is dominant" — meaning RC-3's dominance is currently unverified.

### Argument D-2: The Previous Working State Contradicts RC-3 as Primary Cause

The previous version achieved completions in 20-97s. If startup overhead alone was 32-75s, completions in 20s are impossible — UNLESS:
(a) The startup overhead for the previous version was dramatically lower (no MCP, no heavy CLAUDE.md), OR
(b) The 32-75s startup overhead estimate is too high for typical runs

If (a) is true, then the startup overhead is not fixed — it is configuration-dependent. Fixing the timeout formula without fixing the MCP initialization and CLAUDE.md loading is addressing a symptom of the configuration complexity, not the startup overhead itself.

If (b) is true, then the proposed fix (`_STARTUP_OVERHEAD = 60`) is over-calibrated, and a smaller constant (e.g., 15-20s) would be more accurate. The RCA's confidence in "30-60s" startup is based on a single live measurement ("trivial haiku call takes >30s") which may not be representative of post-warm-cache conditions.

### Argument D-3: Fixing Timeout Budget Alone Will Not Produce Passing Tests

Suppose we implement the proposed fix: `timeout = 60 + per_turn * max_turns`. Opus B tests now get 285s instead of 225s. What happens?

Under RC-1's active mechanism (allowed-tools):
- The model still makes 5 tool calls
- 5 turns of tool execution: still ~150-300s of wall time
- Total: 210-360s
- New timeout 285s: STILL fails for the slow case
- Even if all 5 turns complete within 285s: the output is 5 tool-call results, no classification text, classification scores all 0.0

**The test would still FAIL even if it didn't timeout.** The fix to RC-3 addresses the process termination cause (killed by OS signal) but not the test failure cause (no classification output). A passing TEST requires a classification header — which requires removing `allowed-tools` (RC-1 fix).

### Argument D-4: The 200ms Evidence Is Consistent with Turn-Exhaustion + Timeout Coincidence

An alternative explanation for the uniform 200ms-at-ceiling behavior: the tool-call loop exhausts 5 turns, the process prepares to exit naturally, but the exit sequence (closing MCP connections, flushing output buffers, Node.js garbage collection) takes 30-150ms more than the timeout allows. This would produce the SAME signature as RC-3: process killed at ceiling + 150-200ms overhead.

Under this model, RC-3's evidence does not distinguish between:
- Scenario A: Startup overhead starves turn execution time → killed mid-turn
- Scenario B: All 5 turns exhaust naturally → cleanup sequence killed at ceiling

Both produce identical forensic evidence. Without internal telemetry (per-turn timestamps, turn-start/end markers), the external duration data cannot distinguish these scenarios.

### Argument D-5: Fix Feasibility Is Not the Same as Fix Impact

The prosecution argues the fix is "easy" and "risk-free" — 3 lines of code. This is correct for feasibility. But the fix's IMPACT on the 0% pass rate is near-zero if RC-1 remains active. The RCA's own interaction matrix states RC-3's "Alone Causes Timeout?" as "Depends on turn count" — not YES. This hedge is the defense's strongest point: the RCA's own authors are uncertain whether RC-3 alone causes timeouts.

**Defense Summary**: RC-3 is a real formula bug that should be fixed. But it is a contributing factor to timeout risk under normal conditions, not the root cause of the current 100% failure rate. The timeout being the process termination mechanism does not make it the bottleneck. Fixing RC-3 without RC-1 will not restore passing tests. Fixing RC-1 without RC-3 will likely restore completions (as the previous 9.2% pass rate demonstrated with shorter timeouts and no `allowed-tools`).

---

## SYNTHESIS: Where Prosecution and Defense Agree

Both sides agree on the following facts:
1. All 48 tests were killed by OS SIGKILL at the timeout ceiling — this is not disputed.
2. The timeout formula `per_turn * max_turns` does not account for startup overhead — this is a real formula deficiency.
3. The proposed fix (add startup constant) is correct as a formula improvement.
4. Fixing RC-3 alone will not produce passing tests while RC-1 remains active.
5. The current 0% failure rate is primarily caused by RC-1 (allowed-tools).

The dispute is whether RC-3 is a "root cause" (ranking it alongside RC-1, RC-2) or a "contributing factor" (alongside CF-1 through CF-4). The RCA classifies it as RC-3 with Impact: HIGH and Likelihood: 95% — the defense argues this overstates its role in the CURRENT failure while the prosecution argues its future impact risk is real.

---

## CRITICAL UNANSWERED QUESTIONS

The following experiments from the RCA's proposed verification suite are the only way to settle this debate definitively:

**Experiment 5** (highest discriminating value for RC-3): "Keep allowed-tools but set max_turns=1." If B1 still timeouts at 225s with max_turns=1, startup overhead alone exceeds 225s → RC-3 is dominant. If B1 completes (even with tool-call output) within 225s, startup is absorbed within budget → RC-3 is not dominant.

**Experiment 2** (establishes baseline): "Run single test with --concurrency 1 from clean env." A single-process run eliminates CF-2 (resource contention) and establishes whether the timeout budget is adequate under non-contended conditions.

Without these experiments, RC-3's dominance claim (vs. contributing factor claim) remains architecturally inferred, not empirically validated.

---

## VERDICT

### Scoring Matrix (0-10 each)

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **Evidence Strength** | 7/10 | The 200ms ceiling-match data is compelling and definitively proves all tests were externally killed. However, the evidence cannot distinguish between timeout-as-bottleneck vs. timeout-as-cleanup-killer. The "haiku call takes >30s" baseline is a single data point. The startup overhead breakdown (32-75s) is an estimate, not measured. Strong circumstantial evidence, but not definitive isolation. |
| **Root Cause Likelihood** | 5/10 | RC-3 is a real formula bug that contributes to timeout risk. But the RCA's own data shows the previous version achieved completions with similar or lower timeouts. The current 100% failure rate is best explained by RC-1 (allowed-tools). RC-3 elevates failure probability under adverse conditions but is not the primary mechanism. The RCA's "Likelihood: 95%" for RC-3 is credible for the formula being wrong — less credible for RC-3 being the sole/primary cause. |
| **Fix Impact** | 4/10 | The fix (add 60s startup constant) will not restore any passing tests while RC-1 (allowed-tools) remains active. It addresses process termination cause, not test failure cause. After RC-1 is fixed, RC-3's fix becomes more valuable — it reduces flakiness under slow-startup conditions. The fix is a future reliability improvement, not a current failure recovery. |
| **Fix Feasibility** | 9/10 | The proposed 3-line change is correct, low-risk, and immediately implementable. The constant value (60s) may need calibration but can be tuned empirically. No architectural risk. Should be implemented regardless of RC-3's root cause ranking. |

**Aggregate Score**: 25/40

### Classification Decision

**RC-3 is correctly identified as a formula bug but INCORRECTLY ranked as a primary root cause of the current 100% failure rate.**

The evidence proves that all tests were killed by timeout (timeout was the termination mechanism). It does NOT prove that insufficient timeout budget was the reason the tests couldn't complete (timeout as bottleneck). This is a critical distinction that the RCA blurs.

**Correct classification**: RC-3 should be downgraded from "Root Cause" to a "Contributing Factor" — specifically CF-0 or CF-2b — with the note that it becomes an independent root cause of flakiness AFTER RC-1 is fixed.

**Fix recommendation**: Implement the startup overhead constant regardless of classification. The formula is wrong, the fix is trivial, and it prevents RC-3 from becoming the dominant failure mode once RC-1 is resolved.

### Priority Ordering Recommendation

1. Fix RC-1 (remove `allowed-tools`) — restores text output production
2. Fix RC-3 (add startup overhead) — prevents timeout flakiness after RC-1 fixed
3. Fix CF-2 (reduce concurrency to 5) — eliminates resource contention amplification
4. Fix CF-3 (env filtering for CLAUDECODE) — prevents prospective failure mode

RC-3's fix belongs at position 2, not position 1. The RCA correctly identifies it as "Immediate" in the fix priority list, and this verdict agrees — but for different reasons: fix it because the formula is wrong and cheap to fix, not because it is the primary cause of the current 0% rate.

---

**Debate concluded**: 2026-02-24
**Verdict confidence**: HIGH — the logical distinction between "termination mechanism" and "bottleneck cause" is well-established, and the interaction matrix in the RCA itself hedges on RC-3's standalone causal power.
