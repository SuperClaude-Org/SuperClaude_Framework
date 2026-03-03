# Adversarial Debate: CF-1 — Skill Invocation Cascades into Protocol Exceeding Turn Budget

**Theory ID**: CF-1
**Date**: 2026-02-24
**Analyst**: Root Cause Analyst (Adversarial Debate Agent)
**Status**: VERDICT DELIVERED

---

## Theory Statement

Line 70 of `task-unified.md` (`> Skill sc:task-unified-protocol`) loads 308 lines of additional protocol. The STRICT tier execution path has 11 mandatory steps, each requiring a tool call. With `max_turns=5` and 1-2 turns already consumed before the Skill is invoked, only 3-4 turns remain — insufficient for 11 steps. The cascade itself burns the turn budget even when the task is correctly classified.

**Classification in RCA**: Contributing Factor (CF-1), 85% likelihood. Ranked below RC-1 (`allowed-tools` enabling tool-call exhaustion) but above CF-1b (classification triplication).

---

## Evidence Collected

### Direct Code Evidence

**task-unified.md line 70** (confirmed):
```
> Skill sc:task-unified-protocol
```

**SKILL.md line count** (confirmed): 308 lines. `wc -l src/superclaude/skills/sc-task-unified-protocol/SKILL.md` returns `308`.

**STRICT Execution Steps** (SKILL.md lines 144-156):
```
1.  Activate project (mcp__serena__activate_project)
2.  Verify git working directory clean (git status)
3.  Load codebase context (codebase-retrieval)
4.  Check relevant memories (list_memories -> read_memory)
5.  Identify all affected files and test files
6.  Make changes with full checklist
7.  Identify all files that import changed code
8.  Update all affected files
9.  Spawn verification agent (quality-engineer)
10. Run comprehensive tests: pytest [path] -v
11. Answer adversarial questions
```

Steps 1-4, 9, and 10 are explicit tool calls. Steps 5, 6, 7, 8, and 11 each require at minimum one tool call (Read/Grep/Edit/Task/Bash). The minimum tool-call count for the full STRICT path is therefore 11, one per step.

**Max-turns actually used** (orchestrator.py lines 44-73): All B-tests use `max_turns=5`. This contradicts the spec document which specifies `max_turns=3` as the original design — but the orchestrator code is what was actually executed.

**Turn budget math**:
- Turn 1: Model processes the command file and either (a) emits classification header as text, consuming the turn in output, or (b) makes a tool call (Grep/Read) to investigate.
- Turn 2: Skill invocation via `Skill sc:task-unified-protocol` tool call.
- Turns 3-5: Three turns remain for 11 mandatory STRICT protocol steps.

**Test result evidence** (B1_opus_result.json, B3_opus_result.json across all runs):
- Duration: 225,164ms (opus) = exactly 45s × 5 turns — all turns consumed
- All classification scores: 0.0 — no text output produced
- `skill_invoked = 0.0` in wiring tests — Skill tool not reflected in output

---

## Prosecution: Arguments FOR CF-1

### Argument P1: The Math Is Clear and Unambiguous

The turn budget arithmetic does not require assumptions. The SKILL.md STRICT path has 11 enumerated steps. The orchestrator allocates `max_turns=5`. One turn is consumed invoking the Skill. That leaves exactly 4 turns for 11 steps — a shortfall of 7 turns.

Even granting the most generous possible interpretation (multiple steps per turn, steps batched into single tool calls), steps 9-11 require spawning a quality-engineer sub-agent, running pytest, and then engaging in adversarial Q&A. Each of these is a distinct turn. The math is falsifiable: 5 turns cannot satisfy 11 mandatory sequential steps where at minimum 3 are definitionally separate tool calls.

### Argument P2: The Skill Invocation Itself Is a Turn Expenditure

`> Skill sc:task-unified-protocol` is not a static include or preprocessor directive. In Claude Code, `Skill` is a tool. A tool call occupies one turn. The model sends the tool call, the runtime loads SKILL.md into context and returns it, and the model then processes the 308-line response. This is not free. It is verified by the `skill_invoked` metric being tracked as a distinct scoring criterion in the wiring tests (spec.md lines 362-371).

The RCA Agent 2 document (Angle 3, line 104) explicitly states: "with only 4 remaining turns (1 consumed by Skill invocation), the model cannot complete the protocol."

### Argument P3: The Protocol References Tools That Are Turn-Consuming

The STRICT execution checklist (SKILL.md lines 144-156) references: `mcp__serena__activate_project`, `git status` via Bash, `codebase-retrieval`, `list_memories`, `read_memory`, `pytest`, and a Task sub-agent for the quality-engineer. Each of these involves a tool call. MCP tool calls (`mcp__serena__activate_project`, `codebase-retrieval`) may individually consume significant latency, eating into the per-turn time budget even before `max_turns` is reached. This is not speculative: MCP connection overhead is estimated at 10-30 seconds per server (rca-unified.md line 84).

### Argument P4: B3 "Fix Typo" Theoretically Avoids STRICT, But Still Fails

The defense's strongest rebuttal will be that B3 ("fix typo in error message") should classify as LIGHT and therefore never enter the 11-step STRICT path. However, B3 still timed out (225s opus, 300s sonnet). If CF-1 were the only mechanism, B3 should succeed because LIGHT tier requires only 3 steps (quick scope check, change, sanity check) and even a brief LIGHT path would produce the classification header. B3's failure therefore shows CF-1 does not operate in isolation — RC-1 (`allowed-tools`) is the prerequisite condition that causes Turn 1 to be consumed by tool investigation rather than text output, preventing even the classification header from appearing before turns are exhausted.

However, this does not weaken CF-1 for STRICT-tier tasks. For B1 ("fix security vulnerability in auth module"), CF-1 is a genuine secondary constraint: even if the classification header were emitted on Turn 1, the model would then invoke the Skill on Turn 2 and attempt STRICT execution, exhausting turns 3-5 and producing no further useful output. The test would still receive a partial score at best (header present but no protocol completion).

---

## Defense: Arguments AGAINST CF-1

### Argument D1: Non-STRICT Tasks Should Not Trigger the 11-Step Protocol

The 11-step STRICT execution path applies only when the model classifies a task as STRICT. B3 ("fix typo in error message") should classify as LIGHT. LIGHT execution (SKILL.md lines 167-170) requires only 3 steps: scope check, change, sanity check. This is trivially completable in 3 turns.

B2 ("explain how the routing middleware works") should classify as EXEMPT and execute immediately with no verification overhead.

The CF-1 framing — "11 steps exceed 5 turns" — applies only to STRICT tasks (B1 and implicitly W1). It is not a general mechanism explaining 100% failure across all 8 behavioral tests.

**Counterpoint from prosecution**: Correct on theory, but irrelevant to observed results. ALL tests timed out, including B2 and B3. The 11-step cascade is not the root cause of B2 and B3 failures — RC-1 is. But CF-1 accurately characterizes an additional failure mode for B1 and W1 even after RC-1 is fixed.

### Argument D2: The Model Does Not Have to Follow All 11 Steps

LLMs are not deterministic state machines. The SKILL.md STRICT protocol is a behavioral instruction, not compiled code. The model could:
- Recognize that `max_turns` is limited and abbreviate the protocol
- Emit the classification header and a summary response without completing all steps
- Exercise judgment about which steps are essential given context

The RCA framing treats the model as a rigid rule-follower. In practice, Claude models will often compress or skip steps when they recognize resource constraints.

**Counterpoint from prosecution**: This argument is theoretically sound but empirically falsified. The test results show 0.0 across ALL scoring criteria — not abbreviated output, but zero output. The model did not abbreviate; it produced nothing. This is consistent with tool-call exhaustion (RC-1) rather than protocol abbreviation. The defense's argument would be relevant IF the model were attempting to follow the protocol in abbreviated form; instead, it is not reaching the text-output stage at all. The abbreviation defense is a hypothetical that the actual results contradict.

### Argument D3: CF-1 Is Derivative of RC-1 — Not Independent

If `allowed-tools` were removed from the frontmatter (RC-1 fix), the `Skill` tool would also be unavailable. Without the `Skill` tool available, the model cannot execute `> Skill sc:task-unified-protocol` on line 70. The cascade never occurs. Therefore, CF-1 is fully subsumed by RC-1: fix RC-1 and CF-1 disappears as a separate concern.

This is the defense's strongest argument. The RCA's recommended Fix 1 is to "remove `allowed-tools` from frontmatter entirely." If this fix is applied, the Skill invocation is prevented regardless of whether line 70 exists. CF-1 is not an independent failure mode — it is a consequence of RC-1 being present.

**Counterpoint from prosecution**: Partially valid, but incomplete. If RC-1 is fixed by reducing `allowed-tools` to `Skill` only (Fix 6 from the recommended fix list), the Skill cascade remains active. Fix 6 explicitly states: "Reduce `allowed-tools` to `Skill` only — the model can invoke the Skill but cannot make investigative tool calls." Under this partial fix, CF-1 becomes the dominant failure mode. Removing `allowed-tools` entirely is the cleaner fix, but CF-1 is not eliminated by all candidate RC-1 fixes. CF-1 therefore has independent analytical value.

### Argument D4: Does the Skill Tool Work in `claude -p` Mode?

This is the most penetrating challenge. The `Skill` tool is a Claude Code-specific construct. Its availability in `claude -p` (print mode) is not documented. The `claude -p --help` output does not mention Skill tool support. If the Skill tool does not function in `-p` mode, then:
1. The cascade never happens — the Skill is never loaded
2. The model may receive a tool error and consume a turn handling it
3. The `> Skill sc:task-unified-protocol` directive on line 70 is simply ignored or fails silently

Evidence for this concern: the wiring test scorer tracks `skill_invoked = 0.0` for ALL wiring tests across all runs. Not partial invocation — zero evidence of Skill invocation anywhere. This is consistent with either (a) the Skill tool failing before the model can emit evidence of it, or (b) the model never reaching line 70 because turns were exhausted by prior tool calls.

If the Skill tool does not work in `-p` mode, CF-1's mechanism is invalidated. The cascade does not occur because the cascade requires the Skill tool to function. The 11-step protocol is never loaded. Instead, turns are consumed by other tool calls (Read, Grep) and the model exhausts `max_turns` without producing output — which is RC-1, not CF-1.

**Counterpoint from prosecution**: `skill_invoked = 0.0` is ambiguous evidence. It could mean (a) Skill tool is unavailable in `-p` mode, (b) Skill tool is available but invocation fails, (c) Skill tool is available but the model never reaches line 70 because prior tool calls exhaust turns, or (d) Skill tool functions but the model's output is truncated before recording the invocation. Experiment 6 in rca-unified.md ("Keep allowed-tools but set max_turns=1 — if timeout persists, RC-3 is dominant") and Experiment 7 ("Keep allowed-tools, remove Skill invocation — isolate Skill cascade from tool-call exhaustion") are specifically designed to resolve this ambiguity. Without running these experiments, the `skill_invoked = 0.0` metric cannot definitively rule out the cascade.

The defense's challenge is a valid open question that requires empirical resolution, not a falsification of the theory.

---

## Synthesis: Where CF-1 Stands

### What CF-1 Correctly Identifies

CF-1 accurately identifies a structural problem in the command design: the split between a 107-line command file and a 308-line skill creates a two-phase loading model where the second phase (Skill execution) requires more turns than the budget allows for the STRICT path. This is a real architectural defect regardless of whether CF-1 is the proximate cause of the observed timeouts.

### What CF-1 Does Not Explain

CF-1 does not explain the failure of B2 (EXEMPT), B3 (LIGHT), or W2-W4 (non-task-unified wiring tests). These tests fail for reasons traceable to RC-1 and RC-3, not to the STRICT protocol exceeding the turn budget. CF-1 is correctly classified as a Contributing Factor, not a Root Cause.

### The Dependency Relationship

CF-1 is conditionally dependent on RC-1 in the following sense: CF-1 is only an active failure mechanism when the `Skill` tool is available (via `allowed-tools` containing `Skill`). Removing `Skill` from `allowed-tools` disables CF-1. However, CF-1 is not fully identical to RC-1 — it describes a different mechanism (turn-budget exhaustion from protocol steps) that would persist even if `allowed-tools` were reduced to `Skill` only.

### The Open Empirical Question

Whether the Skill tool functions in `claude -p` mode is unresolved. The existing test data cannot distinguish between "Skill invocation fails silently" and "model never reaches line 70." This question must be resolved experimentally before CF-1's exact contribution can be quantified.

---

## Verdict

### Dimension Scores (0-10 each)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Evidence Strength** | 6 / 10 | The math (11 steps vs 5 turns) is solid and the code references are verified. The SKILL.md line count (308) is confirmed. However, the critical mechanism — whether the Skill tool actually loads in `-p` mode — is empirically unresolved. `skill_invoked = 0.0` across all tests is ambiguous: it could mean Skill tool fails, or turns are exhausted before line 70 is reached. The evidence supports the theory's structural critique but cannot confirm the runtime cascade actually occurs. |
| **Root Cause Likelihood** | 5 / 10 | CF-1 describes a real turn-budget problem, but it is a secondary mechanism that requires RC-1 to be present (tools must be enabled for the Skill to be invocable) and may require Skill tool support in `-p` mode (which is unconfirmed). It accurately predicts failure for STRICT tasks but does not explain EXEMPT/LIGHT failures. The RCA's 85% likelihood estimate is overstated given the unresolved Skill-in-p-mode question; a more defensible estimate is 60-70% conditional on RC-1 being the primary driver. |
| **Fix Impact** | 7 / 10 | Fixing CF-1 (removing the Skill invocation from line 70, or reducing `max_turns` appropriately for classification tests) would materially improve the STRICT-tier test results. Removing the Skill invocation also eliminates the classification triplication (CF-1b) as a side effect, which has additional impact. However, fixing CF-1 alone without addressing RC-1 would not restore the 0% pass rate because EXEMPT and LIGHT tests would still fail. Fix impact is significant but not sufficient in isolation. |
| **Fix Feasibility** | 9 / 10 | The fix is trivially simple: remove line 70 (`> Skill sc:task-unified-protocol`) from `task-unified.md`. This is a one-line deletion. Alternatively, reduce `max_turns` to 2 for classification tests (as suggested in the RCA short-term fixes). No architectural redesign is required. The fix has no downside risk — the classification logic is already inlined in the command file (lines 46-66), so removing the Skill invocation does not remove any functionality needed for classification. |

**Aggregate Score**: (6 + 5 + 7 + 9) / 4 = **6.75 / 10**

### Final Assessment

CF-1 is a **real but conditional secondary failure mode**. The theory is architecturally sound and the code evidence is verified. The turn-budget arithmetic is correct and unfalsifiable on its own terms. However, CF-1 is:

1. Dependent on RC-1 being active (tools must be enabled for cascade to occur)
2. Constrained to STRICT-tier tasks only (does not explain EXEMPT/LIGHT failures)
3. Empirically unverified at the mechanism level (Skill tool availability in `-p` mode is unconfirmed)
4. Subsumed by the more general RC-1 fix in most scenarios

The theory deserves its 85% likelihood classification in the RCA document for STRICT tasks specifically, but should be understood as a layered effect on top of RC-1 rather than an independent root cause. The fix is the easiest of all recommended fixes (one-line deletion) and should be applied regardless of the mechanism question, because the line 70 Skill invocation is architecturally problematic whether or not it currently executes.

**Recommended action**: Remove `> Skill sc:task-unified-protocol` from line 70 regardless of mechanism confirmation. Then run Experiment 6 (remove Skill invocation only, keep `allowed-tools`) to measure CF-1's isolated contribution versus RC-1's contribution, and use results to confirm whether CF-1 is an independent active mechanism or a theoretically valid but currently inert failure mode.

---

## Comparison to Other Theories

| Theory | Score | Relationship to CF-1 |
|--------|-------|----------------------|
| RC-1 (allowed-tools) | ~9/10 | CF-1 is conditional on RC-1; RC-1 fix may fully subsume CF-1 |
| RC-2 (context explosion) | ~7/10 | Independent amplifier; CF-1 and RC-2 both worsen the situation RC-1 creates |
| RC-3 (timeout budget) | ~7/10 | Independent; RC-3 would cause failures even if CF-1 were fixed |
| CF-1 (this theory) | 6.75/10 | Secondary mechanism; correct but not sufficient alone |
| CF-1b (triplication) | ~5/10 | CF-1b would be eliminated as a side effect of fixing CF-1 |

---

*Analysis produced using adversarial debate protocol. Prosecution and defense arguments independently constructed before synthesis.*
