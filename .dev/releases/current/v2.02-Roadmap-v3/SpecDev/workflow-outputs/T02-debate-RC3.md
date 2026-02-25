# Debate T02: Does the Sprint Spec Effectively Mitigate RC3 (Agent Dispatch Mechanism)?

**Root Cause**: RC3 -- Agent Dispatch Mechanism (Rank 5, Combined Score 0.720)
**Sprint Status**: Explicitly DEFERRED. Sprint covers RC1+S01, RC2+S02, RC4+S04 only.
**Date**: 2026-02-23
**Orchestrator**: claude-opus-4-6 (adversarial debate mode)

---

## Context

RC3 identifies that no programmatic binding exists between `sc:adversarial` and `debate-orchestrator`. The Task tool has no `subagent_type` parameter. Agent `.md` files are passive documentation never programmatically loaded. The stale agents README lists 3 of 30 agents. Validated likelihood: 0.70, validated impact: 0.75, combined score: 0.720.

The sprint spec explicitly defers RC3+S03: "RC3's agent dispatch is a latent defect that only surfaces after the top 3 fixes are applied." However, the sprint provides three points of indirect coverage:

1. **Epic 2 Task 2.2 sub-step 3c**: "If agents list length >= 3, add debate-orchestrator to coordination role"
2. **Task 1.4 fallback protocol**: References debate-orchestrator in its behavioral instructions (F1-F5 steps use Task agents with inline behavioral contracts)
3. **Task 2.1 verb glossary**: "Dispatch agent" = Task tool call (could include agent dispatch verbs)

The debate question: Is the combination of deferral + indirect coverage a SUFFICIENT strategy for RC3 in this sprint?

---

## Advocate FOR: Deferral Was Correct and Indirect Coverage Is Adequate

### Opening Position

The sprint spec makes a disciplined, evidence-based decision to defer RC3. The ranked-root-causes document validates RC3 as a latent defect at rank 5 of 5, with the lowest combined score (0.720). The dependency chain analysis explicitly shows RC3 sits downstream of RC1 and RC5 in the causal cascade. Fixing RC3 before its prerequisites are resolved would be engineering priority inversion. The sprint's indirect coverage through sub-step 3c and the fallback protocol is a pragmatic hedge that provides partial mitigation without the cost of a full agent dispatch overhaul.

### Argument 1: The Dependency Chain Makes Deferral the Only Rational Choice

The ranked-root-causes document establishes a clear causal cascade:

```
RC1 (No invocation mechanism) ---+
                                  +--> RC5 (Claude falls back) --> RC3 (Wrong agent selected)
RC2 (Ambiguous spec language) ---+
```

RC3 cannot manifest as an active failure until RC1 and RC2 are resolved. The observed failure -- system-architect selection instead of debate-orchestrator -- was caused by Claude never entering sc:adversarial at all, not by a broken dispatch mechanism within sc:adversarial. The dispatch mechanism was never exercised.

Allocating sprint capacity to a root cause that cannot be tested until after the sprint's own RC1/RC2 fixes are validated is a waste of constrained implementation bandwidth. The sprint correctly prioritizes the three root causes whose fixes can be validated end-to-end within the sprint boundary.

### Argument 2: Sub-Step 3c Provides the Critical Dispatch Hint

Task 2.2 sub-step 3c specifies: "If agents list length >= 3, add debate-orchestrator to coordination role." This is not a full agent dispatch fix, but it is the single most important piece of the dispatch puzzle: it tells Claude which agent to use for coordination.

The core of RC3 is that Claude has no context to select debate-orchestrator. Sub-step 3c directly addresses this by injecting the agent name into the execution flow at the exact decision point where agent selection occurs. Even without the full bootstrap convention (reading `debate-orchestrator.md`, frontmatter, etc.), naming the agent in the instruction stream gives Claude the strongest possible hint.

Evidence from the existing framework supports this. SC:adversarial's SKILL.md already contains a "debate-orchestrator Agent" section (lines 354-359) with role, model, tools, and responsibilities. When sc:adversarial is properly invoked (post-RC1 fix), this section provides behavioral context. Sub-step 3c in sc:roadmap reinforces the agent name before invocation occurs, creating a two-point context chain: sc:roadmap names the agent --> sc:adversarial defines the agent's behavior.

### Argument 3: The Fallback Protocol Embeds Debate-Orchestrator Behavior Inline

Task 1.4's fallback protocol (F1-F5) is designed for the case where the Skill tool fails entirely. In this degraded path, the fallback steps embed debate-orchestrator-like behavior directly into Task agent prompts:

- F3 (Single-Round Debate) dispatches a Task agent for "one round of advocate statements + scoring" -- this is debate-orchestrator behavior without the agent file.
- F4 (Base Selection) dispatches a Task agent to "score variants and select base" -- again, core debate-orchestrator responsibility.
- F5 (Merge + Contract) dispatches a Task agent for merging -- merge-executor behavior.

The fallback protocol effectively inlines the agent behavioral contracts. This is not as clean as proper agent dispatch, but it is functionally equivalent for the degraded path. Any user who hits the fallback still gets debate coordination, just without the agent file being loaded.

### Argument 4: Full RC3 Fix Has Known Weaknesses That Justify Delay

Debate 03 (the prior adversarial analysis of RC3's solution) scored S03 at 0.700 overall with three mandatory conditions and five unresolved concerns. The highest-severity concern was: "Role Adoption Pattern Is Untested." The core mechanism of S03 -- the MANDATORY read instruction for `debate-orchestrator.md` -- was assessed at only 0.65 residual risk confidence.

Implementing a fix with 0.65 confidence on its central mechanism in the same sprint that tackles three higher-priority root causes would be a strategic error. It would introduce untested patterns into an already complex multi-epic sprint. Better to defer S03 to a follow-up sprint where it can be the primary focus, validated independently, and tested end-to-end after the foundational fixes are confirmed working.

### Argument 5: The Sprint's Combined Score Ranking Supports the Cutoff

The sprint uses a transparent combined scoring formula: `combined = (problem_score * 0.5) + (solution_score * 0.5)`. The top 3 pairs score 0.838, 0.778, and 0.776. RC3+S03 scores 0.728 -- a 0.048-point gap below the third-ranked pair. This is not a close call. The gap between the included set and the deferred set is larger than the gap between the second and third ranked pairs (0.002). The quantitative ranking supports the deferral decision.

### Summary FOR

Deferral is the rational choice given the dependency chain, combined scoring, and S03's known weaknesses. The indirect coverage through sub-step 3c (naming debate-orchestrator at the decision point) and the fallback protocol (inlining agent behavior) provide partial mitigation that is proportionate to a latent defect. Full RC3 resolution belongs in a follow-up sprint where it can be validated independently.

---

## Advocate AGAINST: Deferral Creates a Predictable Next Failure

### Opening Position

The sprint spec fixes the invocation wiring (RC1), specification ambiguity (RC2), and return contract transport (RC4). Once these three fixes are applied, the very next invocation of `sc:roadmap --multi-roadmap --agents opus,haiku` will successfully invoke sc:adversarial via the Skill tool -- and immediately encounter the unfixed RC3. The debate-orchestrator agent file will not be read. The `subagent_type: "general-purpose"` fields will still be dead weight. Claude will default to general-purpose agent behavior for pipeline coordination. The sprint will have successfully moved the failure point from "cannot invoke" to "invokes but dispatches wrong agent" -- a lateral move in terms of user-visible outcome quality.

### Argument 1: The Sprint Creates the Exact Conditions for RC3 to Manifest

The ranked-root-causes document explicitly states: RC3 is "a latent defect that only surfaces after the top 3 fixes are applied." The sprint applies exactly those top 3 fixes. This is not a theoretical concern about a distant future -- it is a predictable, immediate consequence of the sprint's own success.

After this sprint:
1. The Skill tool is in allowed-tools (RC1 fixed).
2. Wave 2 step 3 has explicit Skill tool call syntax (RC2 fixed).
3. Return-contract.yaml transport is defined (RC4 fixed).
4. Claude invokes sc:adversarial successfully.
5. sc:adversarial begins its pipeline.
6. sc:adversarial needs to coordinate the 5-step protocol. It dispatches Task agents.
7. **No bootstrap step exists.** `debate-orchestrator.md` is not read. The Task prompt contains no behavioral contract from the agent file. Claude uses general-purpose agent behavior.
8. The 5-step protocol runs with degraded coordination quality.

The sprint fixes the gateway but leaves the room behind it unfurnished. The user experience is: "The feature no longer fails silently, but the adversarial debate quality is significantly below spec because the orchestrator agent is not properly loaded."

### Argument 2: Sub-Step 3c Is Insufficient -- Naming Is Not Binding

Sub-step 3c says: "If agents list length >= 3, add debate-orchestrator to coordination role." The FOR position claims this "names the agent" and provides "the strongest possible hint." But naming is not binding. The instruction is inside sc:roadmap's SKILL.md. Once the Skill tool invokes sc:adversarial, a new execution context begins. Sc:adversarial's SKILL.md becomes the governing document, not sc:roadmap's.

What happens inside sc:adversarial when it needs to coordinate the pipeline?

1. Sc:adversarial's SKILL.md mentions debate-orchestrator in its "Agent Delegation" section (line 354), but only as documentation -- "Role: Coordinates the entire pipeline without participating in debates."
2. No instruction in sc:adversarial says "Read `src/superclaude/agents/debate-orchestrator.md` and adopt its behavioral contract."
3. No frontmatter in the current `debate-orchestrator.md` would cause the Task tool to load it natively (the file has `name`, `description`, `category` frontmatter but lacks `tools`, `model`, `maxTurns`, `permissionMode`).
4. Claude's Task tool dispatch will create a general-purpose agent, not a debate-orchestrator agent.

Sub-step 3c's naming of debate-orchestrator in sc:roadmap does not propagate into sc:adversarial's execution context. The Skill tool creates a boundary. The hint is lost at the invocation boundary.

### Argument 3: The Fallback Protocol Is Not the Primary Path

The FOR position argues that the fallback protocol (F1-F5) embeds debate-orchestrator behavior inline. This is true -- but the fallback only executes when the Skill tool fails. After this sprint fixes RC1, the Skill tool should succeed. The primary path -- not the fallback -- will be taken.

On the primary path, sc:adversarial runs its own pipeline. The fallback protocol with its inline behavioral contracts is never reached. The agent dispatch problem within sc:adversarial is exactly where RC3 lives. The fallback mitigates a different scenario (Skill tool failure) from the one RC3 describes (agent dispatch within sc:adversarial).

This is a category error in the FOR position's analysis. The fallback is designed for invocation failure. RC3 is about dispatch failure after successful invocation. They are orthogonal concerns.

### Argument 4: The "0.048-Point Gap" Is Within Noise

The FOR position cites a 0.048-point gap between the third-ranked pair (0.776) and RC3+S03 (0.728) as evidence the cutoff is well-supported. But the scoring formula uses self-reported estimates that were subsequently validated with reductions of 0.05-0.25 across multiple dimensions. A 0.048 gap is within the estimation error margin.

More importantly, the combined scoring formula weights problem and solution equally. RC3's problem score (0.720) is depressed because it is a latent defect, not because it is unimportant. Its importance is contingent on the sprint's own success. If we condition on "sprint succeeds" (which is the assumption when planning follow-up work), RC3's effective importance increases significantly -- it becomes the next active failure.

The scoring formula does not account for conditional probability. A more sophisticated analysis would ask: "Given that RC1, RC2, and RC4 are fixed, what is the effective score of RC3?" The answer is substantially higher than 0.720.

### Argument 5: The Minimal Incremental Cost of Partial RC3 Coverage

S03 was scored at 0.700 with concerns about its full 6-change scope. But the sprint does not need to implement all of S03 to meaningfully reduce RC3's impact. A minimal addition would be:

- **One line in sc:adversarial SKILL.md**: Before the pipeline begins, add: "Read `src/superclaude/agents/debate-orchestrator.md` and adopt its behavioral contract for pipeline coordination."
- **Add functional frontmatter to debate-orchestrator.md**: `tools`, `model`, `maxTurns`, `permissionMode` -- 4 lines, directly copied from the cleanup-audit agent pattern.

This is approximately 30 minutes of implementation time. It addresses the two most critical dispatch breaks identified in the RC3 analysis (no bootstrap step, no functional frontmatter) without requiring the full convention documentation, README update, or taxonomy resolution. The risk is low because both changes are additive and follow a proven pattern.

The sprint chose to defer the entire RC3 scope when a partial, low-cost mitigation was available. This is scope discipline taken too far -- it optimized for sprint purity over user-visible outcome quality.

### Argument 6: What the User Experiences

After this sprint, the user runs `sc:roadmap --multi-roadmap --agents opus,haiku`. The invocation works. Sc:adversarial starts. But the 5-step adversarial protocol runs with a general-purpose coordinator instead of a debate-orchestrator. The concrete consequences:

- Debate rounds may not properly track convergence (debate-orchestrator's responsibility #4).
- Base selection may not use the hybrid quantitative-qualitative scoring algorithm (responsibility #5).
- Merge handoff may not include proper behavioral constraints for merge-executor (responsibility #6).
- The return contract may be populated with lower-quality data (lower convergence scores, more unresolved conflicts).

The user sees "the feature works" but gets substantially lower quality than the spec promises. This is a different failure mode than the pre-sprint state (silent approximation), but it is still a failure relative to the specified behavior.

### Summary AGAINST

The sprint creates the exact conditions for RC3 to manifest. Sub-step 3c's naming does not cross the Skill tool invocation boundary. The fallback protocol addresses a different failure mode (invocation failure, not dispatch failure). The scoring gap is within noise and does not account for conditional probability. A minimal 30-minute partial fix was available and not taken. The user experience after the sprint will be "invocation works, but debate quality is degraded" -- which is a lateral move from "invocation fails, approximate debate quality."

---

## Cross-Examination

### FOR Challenges AGAINST's Strongest Argument

**Challenge**: The AGAINST position's strongest argument is that the sprint "creates the exact conditions for RC3 to manifest." But this conflates "creates conditions" with "causes failure." Does the AGAINST position acknowledge that a two-sprint approach -- fix the gateway first, fix the room behind it second -- is a standard engineering pattern? And if so, is the criticism really that the sprint should have included a partial RC3 fix, not that deferral itself was wrong?

**Response from AGAINST**: Yes, two-sprint sequencing is standard. The criticism is specifically that the sprint chose *complete* deferral when a *partial* fix (bootstrap instruction + frontmatter, ~30 minutes) was available at minimal risk. The sprint already includes indirect RC3 references (sub-step 3c) that acknowledge the problem exists. The gap between "acknowledge in spec" and "add one Read instruction to sc:adversarial" is small enough that complete deferral was an overcorrection. The two-sprint approach is fine as architecture; the objection is that the boundary between sprints was drawn in the wrong place.

### AGAINST Challenges FOR's Strongest Argument

**Challenge**: The FOR position's strongest argument is the dependency chain: RC3 cannot be tested until RC1 and RC2 are resolved. But the sprint includes Task 0.0 (Skill Tool Probe) as a pre-implementation gate. If the probe succeeds and the Skill tool works, would it not be straightforward to add a lightweight RC3 validation after the probe -- dispatch a Task agent with `debate-orchestrator.md` content and verify it adopts the behavioral contract?

**Response from FOR**: The probe validates whether the Skill tool can cross skill boundaries, not whether agent dispatch works within sc:adversarial. Testing RC3 requires running the full adversarial pipeline, which requires all three epics to be complete. Adding an agent dispatch probe mid-sprint would test a mechanism in isolation that only matters in context. However, the point about adding functional frontmatter to debate-orchestrator.md is conceded -- it is low-cost, follows a proven pattern, and does not require full S03 implementation. The disagreement narrows to: should the sprint include a minimal two-change RC3 hedge (bootstrap + frontmatter)?

---

## Scoring Matrix

| Dimension | Weight | FOR Score | AGAINST Score | Adjudicated Score | Weighted | Rationale |
|-----------|--------|-----------|---------------|-------------------|----------|-----------|
| Root cause coverage | 0.25 | 0.40 | 0.70 | 0.58 | 0.145 | Sprint explicitly defers RC3. Indirect coverage (sub-step 3c) does not cross the Skill invocation boundary. AGAINST correctly identifies that the primary path post-sprint leaves RC3 fully exposed. FOR correctly notes RC3 is latent and cannot be validated in-sprint. Adjudicated below 0.60 because deferral means the root cause is not mitigated. |
| Completeness | 0.20 | 0.45 | 0.65 | 0.57 | 0.114 | The sprint's RC3-relevant content (sub-step 3c, fallback F1-F5, verb glossary) provides partial coverage for the fallback path but zero coverage for the primary invocation path through sc:adversarial. The AGAINST critique that fallback and primary path are orthogonal concerns is valid. |
| Feasibility | 0.25 | 0.80 | 0.75 | 0.78 | 0.195 | Both sides agree a minimal partial fix (~30 min) is feasible. The FOR position correctly notes that full S03 has 0.65 confidence on its core mechanism. The sprint's choice to defer is feasible as a project management decision; the AGAINST argument that a partial fix was feasible and omitted is also correct. High score reflects that either approach (full deferral or partial fix) is implementable. |
| Blast radius | 0.15 | 0.85 | 0.55 | 0.68 | 0.102 | FOR correctly notes that deferral has zero blast radius by definition. AGAINST correctly notes that the *consequence* of deferral -- degraded debate quality on first post-sprint invocation -- has meaningful user-facing impact. Adjudicated at 0.68: low implementation blast radius, moderate outcome blast radius. |
| Confidence | 0.15 | 0.60 | 0.65 | 0.63 | 0.095 | Confidence that the sprint adequately handles RC3 is moderate-low. The indirect coverage is real but insufficient for the primary path. The FOR position's reliance on sub-step 3c crossing the invocation boundary was refuted. The AGAINST position's claim about conditional probability is sound but unquantified. |
| **TOTAL** | **1.00** | | | | **0.651** | |

---

## Verdict: NEEDS AMENDMENTS

**Score: 0.651** -- Below the 0.70 threshold for SUFFICIENT, above 0.40 for INSUFFICIENT.

### Rationale

The sprint made a defensible but imperfect decision to defer RC3. The dependency chain analysis is correct: RC3 cannot be fully validated until RC1 and RC2 are fixed. The combined scoring formula supports the cutoff. However, the AGAINST position successfully demonstrated three weaknesses:

1. **Sub-step 3c does not cross the Skill invocation boundary.** Naming debate-orchestrator in sc:roadmap does not propagate into sc:adversarial's execution context. The indirect coverage claimed by the sprint is weaker than it appears.

2. **The fallback protocol mitigates invocation failure, not dispatch failure.** The F1-F5 steps inline debate-orchestrator behavior, but only execute when the Skill tool fails. On the primary path (Skill tool succeeds), RC3 is fully exposed.

3. **A minimal partial fix was available at low cost.** Adding one bootstrap Read instruction to sc:adversarial's SKILL.md and functional frontmatter to `debate-orchestrator.md` would take approximately 30 minutes, follow a proven pattern (sc:cleanup-audit), and meaningfully reduce RC3's impact without requiring the full S03 scope.

### Recommended Amendments

**Amendment 1 (Recommended, ~15 min)**: Add functional frontmatter to `src/superclaude/agents/debate-orchestrator.md`:
```yaml
tools: Task, Read, Write, Glob, Grep, Bash
model: opus
maxTurns: 50
permissionMode: plan
```
This follows the sc:cleanup-audit agent pattern exactly. It enables the Task tool's native agent loading mechanism. No new patterns required.

**Amendment 2 (Recommended, ~15 min)**: Add one line to sc:adversarial's SKILL.md pipeline preamble: "Before beginning the 5-step protocol, read `src/superclaude/agents/debate-orchestrator.md` and adopt its behavioral contract for pipeline coordination. If the file cannot be read, proceed with the behavioral specification in the Agent Delegation section below."

This is the minimal bootstrap instruction with a defined fallback. It does not require the full agent bootstrap convention, README update, or taxonomy documentation from S03.

**Amendment 3 (Optional, deferred to follow-up sprint)**: Full S03 implementation including convention documentation, README update, three-pattern taxonomy, `subagent_type` cleanup. This remains correctly deferred.

### Risk of Not Amending

If the sprint ships without Amendments 1 and 2, the first post-sprint invocation of `sc:roadmap --multi-roadmap --agents opus,haiku` will:
- Successfully invoke sc:adversarial (RC1 fixed).
- SC:adversarial will coordinate the pipeline with general-purpose agent behavior rather than debate-orchestrator's specialized behavior.
- Debate quality will be degraded: convergence tracking may be absent, scoring may not use the hybrid algorithm, merge handoff may lack proper constraints.
- The return contract will be written (RC4 fixed) but with potentially lower-quality data.
- The user will perceive a partially working feature rather than the fully specified adversarial pipeline.

This is a meaningful improvement over the pre-sprint state (feature was non-functional), but it falls short of the sprint's own stated goal: "Restore full adversarial pipeline functionality."

---

*Debate conducted 2026-02-23. Orchestrator: claude-opus-4-6.*
*Inputs: sprint-spec.md, ranked-root-causes.md, debate-03-agent-dispatch.md, debate-orchestrator.md (agent file), sc-adversarial/SKILL.md.*
*Methodology: Two-advocate adversarial scoring with cross-examination, adjudicated resolution, and concrete amendment recommendations.*
