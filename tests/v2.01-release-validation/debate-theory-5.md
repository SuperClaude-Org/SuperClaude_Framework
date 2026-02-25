# Adversarial Debate: CF-1b — Classification Instruction Triplication Causes Deferral

**Date**: 2026-02-24
**Theory ID**: CF-1b
**Assigned RCA Likelihood**: 70%
**Debater Role**: Adversarial evaluator (Prosecution + Defense + Verdict)

---

## Theory Statement

The "MANDATORY FIRST OUTPUT" classification instruction appears 3 times:
1. `task-unified.md` line 46 — "Classification (MANDATORY FIRST OUTPUT)"
2. `sc-task-unified-protocol/SKILL.md` line 7 — warning banner above the fold
3. `sc-task-unified-protocol/SKILL.md` lines 57-69 — "Section 0. MANDATORY Classification Header (ALWAYS FIRST)"

**Claim**: This triplication creates ambiguity about WHEN to classify, causing the model to defer classification until after tool calls, which consume all turns, resulting in 0.0 classification scores.

---

## Evidence Inventory

### Direct Evidence (from source files)

**task-unified.md (command file)**:
- Line 6: `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill`
- Lines 46-57: Classification block with "Before ANY text, emit this exact header"
- Line 69: `> Skill sc:task-unified-protocol` — Skill invocation AFTER classification

**sc-task-unified-protocol/SKILL.md (Skill file)**:
- Line 4: `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` (8 tools, no Skill)
- Line 7: Warning banner: "MANDATORY FIRST OUTPUT... VERY FIRST output, before ANY text, questions, or analysis"
- Lines 57-99: Section 0 with full classification block including 6 enforcement rules and two example outputs

**Structural sequence when command executes**:
```
Model sees task-unified.md first:
  → Line 46: "MANDATORY FIRST OUTPUT" (classify now)
  → Line 69: "> Skill sc:task-unified-protocol" (invoke skill)
  [Skill loads, model now sees SKILL.md:]
  → Line 7: "MANDATORY FIRST OUTPUT" again (classify now?)
  → Lines 57-69: Section 0 "MANDATORY Classification Header (ALWAYS FIRST)" again
```

**Test data**:
- `classification = 0.0` for all 48 tests
- `skill_invoked = 0.0` for all tests
- `tool_engagement = 0.0` for all tests
- All test durations match timeout ceiling to within 200ms

---

## Prosecution: Arguing FOR CF-1b

### Argument P1: Contradictory Sequencing Between Command and Skill

The command file creates a direct sequencing contradiction:

Line 46 says: "Before ANY text, emit this exact header"
Line 69 says: "> Skill sc:task-unified-protocol" (AFTER the classification block)

A model reading this linearly might interpret the intended flow as:
1. Classify immediately (lines 46-57)
2. Invoke Skill (line 69)
3. Re-encounter the SAME classification instruction in the Skill (lines 7, 57-69)

The Skill's classification instruction is phrased as if it is the authoritative, primary instruction — "VERY FIRST output, before ANY text, questions, or analysis. This is NON-NEGOTIABLE." The word NON-NEGOTIABLE is stronger than the command file's phrasing. A model could reasonably read the Skill's instruction as superseding the command's, and interpret the Skill invocation as the actual starting point. This would cause it to defer classification until the Skill is fully loaded — by which time turns are exhausted.

### Argument P2: Wording Divergence Creates Ambiguity

The three instances are NOT identical:

| Location | Wording | Format |
|----------|---------|--------|
| task-unified.md line 46 | "Before ANY text, emit this exact header" | Section heading + code block |
| SKILL.md line 7 | "You MUST output the classification header block below as your VERY FIRST output... NON-NEGOTIABLE" | Blockquote warning banner |
| SKILL.md lines 57-69 | "CRITICAL: Before ANY other output... you MUST output" + 6 enforcement rules + 2 examples | Full subsection with rules list |

Three different phrasings, three different formats, escalating severity. A model that processes instructions holistically (not sequentially) encounters competing authoritative anchors. The Skill's Section 0 (lines 57-99) is the most detailed and most emphatic — 42 lines vs 11 lines in the command. This asymmetry could cause the model to weight the Skill's instruction as the "real" classification requirement and treat the command's shorter block as merely a preview.

### Argument P3: 0.0 Scores Are Consistent With Deferral

The classification scores of 0.0 are consistent with two explanations:
- (RC-1) Tool calls consumed all turns before text output was possible
- (CF-1b) Model deferred classification to "after Skill loads," but Skill invocation itself consumed turns

CF-1b would manifest identically to RC-1 in the output data because both result in zero text output. The triplication theory does not contradict the evidence — it provides an additional mechanism that reinforces the same outcome.

### Argument P4: "Invoke Skill THEN Classify" Is A Plausible Misread

The command structure could be misread as:

> "Here is what the classification looks like [lines 46-57]. After emitting it, invoke the Skill [line 69], which will tell you more details about classification [SKILL.md lines 7, 57-99]."

A model following this interpretation would try to load the Skill first to get the "complete" classification instructions before outputting anything — resulting in Skill invocation as turn 1, protocol steps consuming turns 2-5, and zero text output.

---

## Defense: Arguing AGAINST CF-1b

### Argument D1: LLMs Reinforce on Repetition — They Do Not Defer

The foundational assumption of CF-1b is that triplication causes confusion or deferral. This contradicts well-documented LLM behavior: instruction repetition strengthens compliance, it does not create ambiguity. Prompt engineering literature consistently shows that repeating critical instructions (at the start AND end of context) increases adherence rates. Three emphatic "MANDATORY FIRST OUTPUT" instructions should make the model MORE likely to classify immediately, not less.

There is no published evidence that instruction repetition causes deferral in transformer-based language models. CF-1b inverts the expected effect direction without supporting evidence.

### Argument D2: The Skill Is Likely Never Loaded

The RCA itself states: `skill_invoked = 0.0` for all tests. If the Skill is never loaded, the model only ever sees the command file's single classification instruction at lines 46-57. The triplication does not exist from the model's perspective — it only encounters one instance.

The triplication can only cause deferral if:
1. The model decides to invoke the Skill before classifying
2. The Skill loads successfully
3. The model re-reads classification instructions and defers

But `skill_invoked = 0.0` falsifies step 1. If the Skill is never invoked, the model never sees the second or third instance of the classification instruction. CF-1b therefore has no mechanism by which to operate in the observed failure scenario.

### Argument D3: RC-1 Is the Complete Explanation — CF-1b Is Redundant

RC-1 fully explains the 0.0 classification scores: `allowed-tools` enables the model to make tool calls, and the 5-turn budget is exhausted by those tool calls before any text output occurs. This is supported by:
- The discriminating variable being `allowed-tools` (present → 0% pass, absent → 9.2% pass)
- The timeout pattern being exact to within 200ms across 48 tests
- The 0.0 scores for `tool_engagement` and `protocol_flow` simultaneously

CF-1b does not add explanatory power. It describes a mechanism that ALSO produces 0.0 classification scores, but so does RC-1. Occam's Razor favors the single, well-evidenced cause (RC-1) over the additional speculative mechanism (CF-1b).

### Argument D4: The Instruction Sequence Is Logically Coherent, Not Contradictory

Reading task-unified.md carefully, the actual instruction sequence is:

1. "Here is the classification format — emit it first" (lines 46-57) — BEFORE the Skill invocation
2. "THEN invoke the Skill for the full execution protocol" (line 69)

This is a clean two-phase structure: classify, then load execution logic. The Skill repeating the classification instruction is belt-and-suspenders defensive programming — ensuring that even if the Skill is invoked in some other context (e.g., directly), classification still happens. A model with reasonable instruction-following capability reads this as: classify first, THEN invoke Skill.

The contradiction claimed in the prosecution (command says "classify before ANY text" but also "invoke Skill") is not a contradiction — the Skill invocation is in the Execution section, AFTER the Classification section. The temporal order in the document reflects the intended execution order.

### Argument D5: Deferral Would Require The Skill To Load — Which Takes A Turn

Even under the deferral hypothesis: if the model decides to load the Skill before classifying, that consumes turn 1. The Skill is 309 lines of additional context. After loading, turns 2-5 remain. But the Skill's own execution path (STRICT tier) has 11 steps. The model still runs out of turns before classifying — so CF-1b collapses into CF-1 (Skill cascade turn exhaustion), not a standalone deferral mechanism.

The triplication adds no unique causal contribution; the cascade alone explains turn exhaustion.

---

## Critical Analysis: Prosecutorial Weaknesses

**P1 weakness**: The "sequencing contradiction" requires the model to read the command as "invoke Skill to get full instructions before classifying." This is an unusual interpretation; the document clearly places classification BEFORE the Skill invocation. The sequencing is only contradictory if the model ignores document structure.

**P3 weakness**: The prosecution concedes CF-1b is "consistent with" the evidence. Consistency is not sufficiency. RC-1 is also consistent with the same evidence — and RC-1 has a direct, experimentally-validated mechanism (allowed-tools present → 100% fail; allowed-tools absent → 9.2% pass). CF-1b has no comparable controlled comparison.

**P4 weakness**: The "plausible misread" argument is speculative. There is no test data showing a model actually took this interpretation. The argument could apply to virtually any multi-section document.

---

## Critical Analysis: Defense Weaknesses

**D2 weakness**: The argument "Skill is never loaded" relies on `skill_invoked = 0.0`, but this metric measures whether the Skill was invoked AND recorded a response — not whether the model attempted to invoke it. If turn budget was exhausted during Skill loading, `skill_invoked` would still be 0.0. The metric cannot distinguish "model never tried to invoke Skill" from "model tried but ran out of turns during invocation."

**D3 weakness**: The "redundant with RC-1" argument is sound but incomplete. CF-1b could still be a contributing mechanism even if RC-1 is the primary cause. The RCA framework assigns 70% likelihood to CF-1b precisely because it may amplify RC-1's effect, not replace it.

---

## Verdict

### Evidence Strength: 3/10

The theory is logically constructed but lacks direct evidence. The key observation — `skill_invoked = 0.0` — actually undermines the mechanism (triplication can only cause deferral if the Skill loads, which it does not). The 0.0 classification scores are fully explained by RC-1 without requiring triplication deferral. No controlled experiment has isolated triplication as a variable. The theory is plausible in the abstract but is not supported by the specific evidence available.

### Root Cause Likelihood: 2/10

CF-1b fails on the causal mechanism front. For triplication to cause deferral:
1. The model must decide to load the Skill before classifying — but `skill_invoked = 0.0` shows it does not
2. The Skill must load and the model must re-read classification instructions — also not evidenced
3. The model must choose the Skill's instruction as more authoritative — speculative

RC-1 explains the same symptoms without requiring any of these steps. CF-1b is not the root cause; it is a plausible nuance in a different failure scenario where tool calls are available but the Skill actually loads.

The RCA's 70% assigned likelihood is significantly overstated. The mechanism is blocked by its own evidence.

### Fix Impact: 2/10

Even if the fix for CF-1b (consolidating the classification instruction to a single authoritative location) were applied, it would have minimal impact on the current failure mode. The test results are 100% timeouts driven by `allowed-tools` enabling tool exhaustion (RC-1). Removing duplicate classification instructions would not prevent the model from making tool calls that consume all turns. The actual mechanism causing 0.0 classification scores would remain.

If RC-1 were fixed first (removing `allowed-tools`), the model would be forced to produce text output — and in that scenario, the triplication might or might not cause mild wording confusion. The marginal fix impact is low because CF-1b is not load-bearing in the failure chain.

### Fix Feasibility: 9/10

The proposed fix is straightforward: consolidate the classification instruction to a single location (either the command file or the Skill file's warning banner, not both with a third elaboration). This is a copy-editing change requiring no architectural work. There is no risk of regression from removing duplicate instructions. The fix is highly feasible regardless of its actual impact.

---

## Summary Table

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Evidence Strength | 3/10 | Theory is consistent with data but not supported by it; `skill_invoked = 0.0` undermines the primary mechanism |
| Root Cause Likelihood | 2/10 | Causal mechanism requires Skill loading, which evidence shows does not occur; RC-1 is complete without CF-1b |
| Fix Impact | 2/10 | Consolidating classification instructions would not address the `allowed-tools` tool-exhaustion mechanism |
| Fix Feasibility | 9/10 | Trivial copy-editing change with no architectural risk |
| **Composite** | **4/40** | CF-1b is a plausible narrative but not a supported root cause in the specific observed failure |

---

## Conclusion

CF-1b is a **speculative contributing factor that is internally inconsistent with the primary evidence**. The central paradox: the theory claims triplication causes deferral by causing the model to load the Skill before classifying — but the Skill was never loaded (`skill_invoked = 0.0`). This is not a case where evidence is absent; evidence actively contradicts the mechanism.

The true root cause (RC-1: `allowed-tools` enabling tool-call turn exhaustion) is the complete explanation for 0.0 classification scores. CF-1b does not survive as an independent cause. It may survive as a hypothetical secondary mechanism in a scenario where RC-1 is fixed and the Skill is successfully loaded — but that scenario is not the one under investigation.

**Recommended action**: Remove duplicate classification instructions as a defensive code quality improvement (the fix is free at feasibility 9/10), but do not treat CF-1b as a meaningful contributor to the 100% timeout failure. The RCA-assigned 70% likelihood should be reduced to approximately 15-20%, reflecting: "possible secondary mechanism in a repaired system; not operative in the current failure mode."

---

*Debate conducted: 2026-02-24*
*Theory assigned RCA likelihood: 70% (this analysis recommends revision to 15-20%)*
