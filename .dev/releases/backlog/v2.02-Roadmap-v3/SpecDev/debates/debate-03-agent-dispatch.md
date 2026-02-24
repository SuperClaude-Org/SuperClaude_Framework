# Debate 03: Agent Dispatch Fix (Solution #3)

**Root Cause**: RC3 -- Agent Dispatch Mechanism (Rank 5, Score 0.72)
**Solution**: Option B -- Agent Bootstrap Convention
**Date**: 2026-02-22
**Orchestrator**: claude-sonnet-4-6 (debate orchestrator mode)

---

## Context

Solution #3 proposes fixing the broken dispatch chain `sc:roadmap -> sc:adversarial -> debate-orchestrator` by establishing an "Agent Bootstrap Convention." The convention requires skill executors to explicitly read agent `.md` files and either adopt their behavioral contract (role adoption) or inject their content into Task prompts (sub-agent dispatch). Six concrete changes are specified across four files.

The ranked-root-causes document (validated analysis) places RC3 at Rank 5 with a combined score of 0.72 -- the lowest of the five root causes -- and classifies it as a **latent defect** rather than an active cause of the observed failure. RC3 depends on RC1 and RC5 being resolved first before it can surface.

---

## Advocate FOR: The Fix Is Necessary and Well-Scoped

### Opening Position

Solution #3 addresses a genuine structural deficiency in the agent dispatch architecture. Even if RC3 is a latent defect rather than the primary failure mechanism, latent defects become active failures the moment their prerequisites are satisfied. Fix RC1 (add Skill to allowed-tools) and SC:adversarial will be invoked -- at which point the broken agent bootstrap becomes the next blocking failure. Fixing RC3 proactively is not premature; it is defensive engineering.

### Argument 1: The Evidence Chain Is Concrete and Verifiable

The three dispatch breaks identified in the solution are not inferred or speculative. They are directly observable:

1. `debate-orchestrator.md` exists as a 69-line passive document with no frontmatter. The file contains behavioral specification text and nothing else. Claude has no mechanism to receive this specification unless explicitly instructed to read it.
2. `subagent_type: "general-purpose"` appears in two YAML blocks (SKILL.md lines 802 and 1411). The Task tool API has no `subagent_type` parameter. These fields are dead weight. Any engineer reading the SKILL.md would infer they are executable; they are not.
3. No bootstrap step exists in sc:adversarial. The SKILL.md dispatches merge-executor via Task without reading `merge-executor.md`. The behavioral contract that governs plan fidelity and provenance tracking is never delivered to the agent that needs it.

All three can be confirmed by reading four files. This is a higher evidentiary standard than most latent defects meet.

### Argument 2: The Working Precedent Is Directly Analogous

The solution correctly identifies that sc:cleanup-audit's agents work because they have functional frontmatter (`tools`, `model`, `maxTurns`, `permissionMode`) that Claude Code's Task tool loads natively. The adversarial agents lack this frontmatter. Change 4 and Change 5 in the solution add identical frontmatter to `debate-orchestrator.md` and `merge-executor.md`.

This is not a new pattern being invented. It is applying an existing working pattern to two files that were not built to that standard. The risk is low precisely because the pattern is proven.

### Argument 3: The Role Adoption vs. Sub-Agent Dispatch Distinction Is Architecturally Correct

The solution makes a precise and important distinction:

- **Role adoption**: sc:adversarial reads `debate-orchestrator.md` and becomes the orchestrator. It is not dispatched as a Task -- it is the executor that adopts the behavioral contract.
- **Sub-agent dispatch**: sc:adversarial reads `merge-executor.md` and injects its content into the Task prompt. The agent is spawned separately and receives its behavioral contract as system context.
- **Dynamic agents**: Advocate agents have no `.md` files because they are instantiated per-debate from user-provided `--agents` specifications. This is intentional and the solution correctly identifies it as correct architecture.

This three-pattern taxonomy (role adoption, sub-agent dispatch, dynamic agents) is a genuine contribution to framework clarity. It resolves the current ambiguity about when to create agent files and when to inline behavior.

### Argument 4: Blast Radius Is Minimal

Four files are modified. Three of the four changes are purely additive (frontmatter addition to agent files, convention documentation). The one substantive change -- adding the agent bootstrap section to sc:adversarial SKILL.md -- is a documentation block that instructs Claude to read files before proceeding. No executable code is changed. No other skills are affected. SC:cleanup-audit explicitly does not need changes because it already complies.

### Argument 5: The Convention Scales

By documenting the agent bootstrap convention in `agents/README.md`, the solution creates a standard that applies to all future skills. The current state -- where the pattern is implicit in cleanup-audit and absent in adversarial -- creates a two-tiered system where future authors have no guidance. The convention eliminates this ambiguity at low cost.

### Summary FOR

The fix addresses real, verifiable defects. It applies a working pattern from an analogous system. It correctly models the architectural relationships between skills and agents. The blast radius is four files, three of which receive only additive changes. The convention establishes forward-looking clarity. This fix should be applied.

---

## Advocate AGAINST: The Fix Is Misranked, Premature, and Overconfident

### Opening Position

Solution #3 conflates architectural documentation with functional defect repair. The ranked-root-causes document validates RC3 at rank 5 precisely because it is a latent defect whose causal contribution to the observed failure is zero. The solution's confidence score of 0.82 is not supported by the evidence, particularly given the acknowledged residual risk: "Claude may still not read the agent `.md` file in all cases." A fix that depends on heuristic instruction-following to resolve a structural dispatch problem is not a fix -- it is a documentation update that hopes the problem will not recur.

### Argument 1: RC3 Did Not Cause the Observed Failure

The ranked-root-causes document is explicit: "The agent dispatch mechanism within sc:adversarial was never tested." System-architect was selected not because the agent dispatch was broken, but because Claude was operating entirely outside sc:adversarial due to RC1. The dispatch mechanism's failure mode was never exercised.

The solution's opening claim -- "There is no binding mechanism between skill invocations and agent definitions" -- is accurate but irrelevant to the observed failure. Fixing a binding mechanism that was never reached during the failure does not repair the failure. It repairs a future failure that has not yet occurred.

This is engineering priority inversion. RC1 and RC2 are blocking. RC3 is non-blocking until RC1 and RC2 are resolved.

### Argument 2: The Confidence Score Is Inflated

The solution reports an overall confidence of 0.82 but the residual risk factor scores only 0.65 with this explanation: "Claude interprets markdown instructions heuristically, not deterministically. Even with perfect bootstrap instructions, Claude may still not read the agent `.md` file in all cases."

A 0.65 residual risk score on the key execution mechanism of the proposed fix -- the MANDATORY read instruction -- is not a secondary concern. It is the central mechanism. If Claude does not reliably follow the bootstrap read instruction, the three dispatch breaks identified in the solution remain broken. The behavioral contract is still not delivered. The `subagent_type` fields are still dead. Nothing functionally changes except that the SKILL.md now contains additional markdown text instructing Claude to do something it may not do.

The 0.82 overall confidence is a weighted average that obscures this critical weakness. A solution whose core execution mechanism has only 0.65 confidence should not be scored at 0.82 overall.

### Argument 3: "MANDATORY" in Markdown Is Not a Guarantee

Change 1 inserts a section titled "Agent Bootstrap (MANDATORY -- execute before pipeline)." The word MANDATORY carries no enforcement weight in a markdown document. Claude processes the SKILL.md as natural language instructions. The instruction to read a file before proceeding competes with all other instructions in a 1747-line document. Under context pressure, tool call limits, or when Claude infers the read is unnecessary (because the SKILL.md already contains all implementation details), the bootstrap step may be skipped.

The cleanup-audit precedent cited by the solution is not directly analogous. Cleanup-audit agents work because the Task tool natively loads `.md` files with functional frontmatter -- this is a framework mechanism, not an instruction. The bootstrap convention for role adoption (Change 1) has no such native mechanism. It depends entirely on Claude's interpretation of "you MUST read this file."

The FOR advocate claims the cleanup-audit pattern is "proven." But the cleanup-audit pattern uses native Task tool loading, not MANDATORY read instructions. The adversarial bootstrap pattern (role adoption) is genuinely untested, as the solution itself acknowledges.

### Argument 4: The Three-Pattern Taxonomy Creates New Ambiguity

The solution introduces three patterns: role adoption, sub-agent dispatch, dynamic agents. This taxonomy is useful but it raises questions the solution does not answer:

- How does a future skill author know whether to use role adoption or sub-agent dispatch?
- What is the decision criterion for creating a dynamic agent vs. a static agent `.md` file?
- If debate-orchestrator is a role adoption (not a spawned sub-agent), why does Change 4 add frontmatter with `permissionMode: plan` and `maxTurns: 50`? These fields are only relevant to Task-spawned agents, not role-adopted orchestrators.

Change 4 adds frontmatter that would only be used if debate-orchestrator were loaded as a native Task agent. But Change 1's role adoption pattern explicitly states "the agent is not spawned as a separate Task -- the skill executor BECOMES the agent." The frontmatter added in Change 4 is either vestigial (role adoption never uses it) or contradicts the role adoption architecture by implicitly treating the orchestrator as Task-spawnable.

This inconsistency suggests the solution has not fully resolved the architectural relationship between the two patterns.

### Argument 5: Convention Documentation Has Low Enforcement

The convention documented in `agents/README.md` has no enforcement mechanism. Code reviews are the only check, and the solution explicitly lists "Convention not followed by future skills" as a medium-probability risk with a mitigation of "README documentation + code review checklist." A medium-probability risk mitigated only by documentation and manual review is an unresolved risk, not a resolved one.

The FOR advocate correctly identifies that Option C (agent loader template) would provide a more enforceable abstraction. The solution rejects Option C as "over-engineering" because only 2 skills currently use Task agents. But the convention-only approach defers the enforcement problem indefinitely. When the fourth or fifth skill using Task agents is added by a developer who has not read the README, the latent defect re-appears in a new location.

### Argument 6: Implementation Order Dependency Is Understated

The solution correctly notes "Fix 1 MUST be applied before this solution has any observable effect." This is a significant qualifier. Solution #3 delivers zero observable improvement in isolation. Its value is entirely contingent on Fix 1 (RC1) and implicitly on Fix 2 (RC2, RC5) being applied correctly. A solution that cannot be validated independently has a higher integration risk than its individual component analysis suggests.

### Summary AGAINST

RC3 is a latent defect correctly ranked last. The solution's core mechanism depends on heuristic instruction-following with acknowledged 0.65 confidence. The MANDATORY keyword is not enforceable. The three-pattern taxonomy contains an internal inconsistency (debate-orchestrator frontmatter vs. role adoption semantics). The convention has no enforcement mechanism beyond documentation. The fix cannot be validated in isolation. These are not minor concerns -- they collectively describe a fix that is directionally correct but structurally incomplete.

---

## Rebuttal: Resolution of Key Disagreements

### On RC3 Being Latent vs. Active

Both advocates agree on the fact: RC3 did not cause the observed failure. The disagreement is whether fixing it now is appropriate.

The AGAINST position is correct that RC3 is not blocking. However, the FOR position is also correct that once RC1 is fixed, RC3 becomes the next blocking failure in the chain. The dependency chain analysis in the ranked-root-causes document supports this: `RC1 → RC5 → RC3`. Fixing RC3 as part of the same repair cycle is operationally sound. Deferring it to a separate cycle risks the same failure re-appearing in a different form.

**Resolution**: RC3 should be fixed, but it should be explicitly sequenced after Fix 1 and Fix 2, not treated as a parallel or equivalent priority.

### On the 0.82 Confidence Score

The AGAINST critique is valid. The residual risk factor (0.65) describes the central execution mechanism -- whether Claude reliably follows MANDATORY read instructions. A 0.65 score on the core mechanism should weight more heavily in the overall confidence calculation. The 0.82 overall score is computed as a simple average across five factors, which obscures that one factor is load-bearing.

A more accurate weighted confidence would be approximately 0.73-0.76, reflecting that the implementation feasibility (0.80) and residual risk (0.65) apply specifically to the role adoption pattern (Change 1), which is the novel and untested component.

**Resolution**: Confidence should be recalibrated to 0.74. The solution is sound for Changes 2-6 (sub-agent dispatch, frontmatter, documentation). Change 1 (role adoption via MANDATORY instruction) carries the highest uncertainty.

### On the Frontmatter Inconsistency

The AGAINST critique identifies a genuine inconsistency: Change 4 adds Task-agent frontmatter to `debate-orchestrator.md` even though Change 1's role adoption pattern says the orchestrator is never spawned as a Task. The FOR advocate did not address this.

**Resolution**: The inconsistency is real. One of two resolutions is needed:
- Option X: Remove the frontmatter from `debate-orchestrator.md` (it will never be used under role adoption).
- Option Y: Clarify that debate-orchestrator MAY be invoked either way -- as a role adoption by sc:adversarial or as a native Task agent if directly invoked. The frontmatter supports the latter case.

Option Y is more robust. The frontmatter does not hurt anything and provides a fallback invocation path. But the solution document should explicitly acknowledge this dual-invocation capability rather than leaving it implicit.

### On Convention Enforcement

The AGAINST position correctly identifies that convention-only approaches have medium-probability failure modes. The FOR position's response -- that Option C can be extracted later as a natural refactoring -- is directionally correct but does not address the present enforcement gap.

**Resolution**: The convention is acceptable for the current state (2 skills). The solution should add a specific trigger condition for when Option C becomes appropriate: "When the third skill using Task agents is added, extract the agent loader as a reusable pattern." This converts the enforcement concern from an open risk to a scheduled decision point.

### On "MANDATORY" Not Being Enforceable

The AGAINST critique is correct that MANDATORY in markdown carries no programmatic enforcement. However, the baseline comparison matters. Before this fix, Claude has no instruction at all to read agent files. After this fix, Claude has an explicit, prominent instruction to read them before proceeding. The improvement is real even if imperfect.

The correct framing is: this fix raises the probability of correct agent loading from approximately 0% (no instruction) to an estimated 70-80% (strong instruction, context-dependent). The 0.65 residual risk score captures that the remaining 20-30% probability of non-compliance is not eliminated.

**Resolution**: The fix is worth applying, but the SKILL.md should include the fallback instruction from the Risk Matrix: "If agent `.md` not found or unreadable, proceed with SKILL.md instructions only." This converts a silent failure mode into a defined degraded path.

---

## Scoring Matrix

| Dimension | Weight | FOR Score | AGAINST Score | Adjudicated Score | Weighted |
|-----------|--------|-----------|---------------|-------------------|---------|
| Root cause coverage | 0.25 | 0.75 | 0.45 | 0.62 | 0.155 |
| Completeness | 0.20 | 0.72 | 0.50 | 0.63 | 0.126 |
| Feasibility | 0.25 | 0.82 | 0.60 | 0.73 | 0.183 |
| Blast radius | 0.15 | 0.88 | 0.75 | 0.83 | 0.125 |
| Confidence | 0.15 | 0.82 | 0.55 | 0.74 | 0.111 |
| **TOTAL** | **1.00** | | | | **0.700** |

### Scoring Rationale

**Root cause coverage (0.62)**: The solution addresses RC3 directly and correctly. The three dispatch breaks are real. However, RC3 is rank 5 in a 5-rank chain; it covers a latent defect whose causal contribution to the observed failure is validated at 0.72 (lowest of five). The high FOR score (0.75) reflects genuine coverage of the actual defect. The AGAINST discount (to 0.45) correctly penalizes the misalignment between fix priority and failure ranking. Adjudicated at 0.62 -- the fix covers its stated root cause but not the primary cause of the observed failure.

**Completeness (0.63)**: The solution handles the sub-agent dispatch path (merge-executor) and the dynamic agent path (advocates) well. Change 2 and Change 3 are complete. The role adoption path (Change 1) is incomplete: the frontmatter inconsistency is unresolved, the MANDATORY instruction has no fallback, and the role adoption pattern is untested. The convention documentation (Change 6) lacks an enforcement trigger condition. Adjudicated at 0.63 -- the solution covers the identified cases but contains gaps in the novel role adoption pattern and convention governance.

**Feasibility (0.73)**: All six changes are to markdown files. No executable code is modified. The highest-risk change (Change 1, MANDATORY read instruction) depends on Claude's instruction-following, which the solution itself rates at 0.65 residual risk. Changes 2-6 are low-risk. Implementation is technically trivial; the feasibility risk is behavioral (will Claude follow the instructions). Adjudicated at 0.73 -- high feasibility for the structural changes, moderate feasibility for the behavioral enforcement.

**Blast radius (0.83)**: Four files modified. Three receive only additive changes. Upstream (sc:roadmap) is unaffected. Downstream agents receive clearer behavioral contracts. The convention applies forward to future skills without modifying existing ones. SC:cleanup-audit is explicitly exempt. The blast radius analysis in the solution is accurate and the AGAINST position did not substantially challenge it. Adjudicated at 0.83 -- this is the solution's strongest dimension.

**Confidence (0.74)**: The solution's self-reported 0.82 is inflated. The AGAINST critique of the 0.65 residual risk factor is valid -- it applies to the load-bearing mechanism of Change 1. The recalibrated confidence of 0.74 reflects: high confidence in Changes 2-6 (proven patterns, additive changes), moderate confidence in Change 1 (novel pattern, heuristic instruction-following, untested). The frontmatter inconsistency on debate-orchestrator adds a small additional discount.

---

## Fix Likelihood

**Fix Likelihood: 0.70 (Apply with conditions)**

This solution should be applied, but with three mandatory conditions:

1. **Sequencing**: This fix must be applied after Fix 1 (RC1) and Fix 2 (RC2, RC5). It has no independent observable effect and cannot be validated in isolation. Applying it first would create false assurance.

2. **Frontmatter clarification**: The debate-orchestrator.md frontmatter inconsistency must be resolved before implementation. Either remove the frontmatter (if role adoption only) or add explicit documentation that it supports dual-invocation (role adoption by sc:adversarial, direct Task invocation by other callers).

3. **Fallback instruction**: Change 1 must include the fallback: "If `src/superclaude/agents/debate-orchestrator.md` cannot be read, proceed with the behavioral specification contained in this SKILL.md." This converts the silent failure mode into a defined degraded path.

Without these conditions, the fix applies the correct pattern to the correct problem but leaves implementation gaps that will likely surface during the first end-to-end test of the repaired invocation chain.

---

## Unresolved Concerns

### Concern 1: Role Adoption Pattern Is Untested

**Severity**: High
**Description**: Change 1 introduces the role adoption pattern -- where sc:adversarial reads `debate-orchestrator.md` and "becomes" the orchestrator rather than spawning it as a Task. This pattern does not exist anywhere else in the framework. It is not analogous to the cleanup-audit precedent (which uses native Task loading). The solution's 0.65 residual risk score for implementation feasibility reflects this uncertainty.
**Resolution path**: Requires end-to-end testing of the `sc:roadmap --multi-roadmap --agents opus,haiku` flow after Fix 1 and Fix 2 are applied. The role adoption instruction should be validated empirically before the convention is documented as a framework standard.

### Concern 2: Frontmatter on Debate-Orchestrator Is Architecturally Ambiguous

**Severity**: Medium
**Description**: Change 4 adds Task-agent frontmatter (`tools`, `model`, `maxTurns`, `permissionMode`) to `debate-orchestrator.md`. Change 1 states the orchestrator is adopted by role (not spawned as a Task). The frontmatter is either unused (role adoption never triggers it) or it implies an undocumented dual-invocation mode. The solution does not resolve this.
**Resolution path**: Add a comment to the debate-orchestrator frontmatter: "This frontmatter supports direct Task invocation by callers other than sc:adversarial. When invoked by sc:adversarial, role adoption applies instead." Alternatively, remove the frontmatter if dual-invocation is not intended.

### Concern 3: Convention Enforcement Has No Trigger Condition

**Severity**: Medium
**Description**: The agent bootstrap convention is documented in README.md with no automated enforcement and no specified threshold for upgrading to Option C (agent loader template). As additional skills adopt Task agents, the convention-only approach degrades. The solution identifies this risk but does not schedule its resolution.
**Resolution path**: Add a decision condition: "When the third skill using Task agents is added to the framework, implement Option C (agent loader template) as a standardized abstraction." Document this condition in both the README and the solution document.

### Concern 4: Merge-Executor Content Injection Increases Prompt Size

**Severity**: Low
**Description**: Change 2 (updated `task_dispatch_config` for merge execution) requires injecting the full content of `merge-executor.md` as system context in the Task prompt. The current `merge-executor.md` is not shown in the solution document; its size is unknown. If it is large (>500 lines), content injection may create Task prompt size issues or context pressure in long-running pipelines.
**Resolution path**: Review `merge-executor.md` size before implementing Change 2. If the file exceeds 200 lines, consider a summarized behavioral contract injection rather than full-content injection, with a pointer to the full specification.

### Concern 5: Advocate Agents Have No Behavioral Validation

**Severity**: Low
**Description**: The solution correctly identifies that advocate agents are dynamic (no `.md` files) and generated from `advocate_prompt_template`. However, the solution does not validate that the current template is sufficient to produce advocates with consistent adversarial behavior. If the template is weak, removing the dead `subagent_type` field (Change 3) surfaces the inadequacy without fixing it.
**Resolution path**: Review `advocate_prompt_template` in SKILL.md for completeness. Verify it produces structurally consistent advocate behavior before the `subagent_type` cleanup is applied. This is a separate concern from the bootstrap mechanism but relevant to overall dispatch quality.

---

## Summary Verdict

Solution #3 correctly identifies three real dispatch breaks and applies a sound architectural pattern (agent bootstrap convention) derived from a working precedent (sc:cleanup-audit). Its primary weaknesses are: (1) the role adoption pattern is novel and untested, (2) the confidence score is inflated relative to the acknowledged uncertainty, (3) the frontmatter inconsistency on debate-orchestrator needs resolution, and (4) the fix cannot be validated independently of Fix 1.

The fix should be applied with the three mandatory conditions specified above. It is a necessary component of the full repair cycle but not a standalone fix, and should not be treated as one.

**Adjudicated overall score**: 0.700
**Fix likelihood**: Apply (with conditions, after Fix 1 and Fix 2)
**Priority**: Third in implementation sequence, after RC1 and RC2/RC5 fixes

---

*Debate conducted 2026-02-22. Orchestrator: claude-sonnet-4-6.*
*Input: solution-03-agent-dispatch.md, ranked-root-causes.md.*
*Methodology: Two-advocate adversarial scoring with rebuttal and adjudicated resolution.*
