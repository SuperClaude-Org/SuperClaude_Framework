# T02 Adversarial Debate: RC5 (Claude Behavioral Interpretation)

**Debate Question**: Does the sprint specification effectively mitigate RC5 (Claude Behavioral Interpretation)?

**RC5 Summary**: Claude's rational fallback decision chain when invocation failed: (1) instruction says "invoke," (2) Skill tool unavailable, (3) approximate using Task agents, (4) spawn system-architect agents for variant generation, (5) manually synthesize. The approximation preserved ~20% of the adversarial pipeline's functionality (variant generation + rough merge) while skipping 80% (diff analysis, debate, scoring, refactoring plan, provenance). Likelihood: 0.85, Impact: 0.70, Combined Score: 0.790.

**Sprint Treatment**: RC5+S05 was formally deferred (combined score 0.761, ranked 4th of 5 pairs). The spec states: "RC5's fallback protocol is partially absorbed by S02's fallback in Wave 2 step 3d." Specific mechanisms:
- Epic 1 Task 1.4: 5-step fallback protocol (F1-F5)
- Epic 2 Task 2.2 sub-step 3d: Skill tool invocation with structured fallback
- Epic 2 Task 2.2 sub-step 3e: Return contract routing with status-based decisions
- Epic 2 Task 2.1: Verb glossary removing the ambiguity that triggered the original degraded behavior
- Risk R6: Fallback protocol bitrot acknowledged

---

## Round 1: Opening Statements

### FOR Position (Advocate)

The sprint specification effectively mitigates RC5 despite formally deferring the dedicated S05 solution. The key insight is that RC5 is not an independent root cause -- it is a *behavioral consequence* of RC1 and RC2. The ranked-root-causes document itself confirms this: "RC1 blocks invocation entirely. RC2 compounds this by providing no fallback guidance. Together they trigger RC5." The sprint attacks RC5 at its roots rather than treating the symptom.

**Three pillars of mitigation**:

1. **Root cause elimination (Epic 1 + Epic 2)**: By adding the Skill tool to `allowed-tools` (Tasks 1.1-1.2) and rewriting the ambiguous "Invoke" verb into explicit `Skill` tool call syntax (Task 2.1 glossary + Task 2.2 sub-steps), the sprint removes the two conditions that triggered Claude's fallback behavior in the first place. If the Skill tool is available AND the instructions are unambiguous, Claude has no reason to fall back. The original RC5 behavior required both conditions to be absent -- both are now addressed.

2. **Structured fallback protocol (Task 1.4, F1-F5)**: Even if the primary path fails (Risk R1: Task agent cannot access Skill tool, probability 0.40; Risk R2: "skill already running" blocks invocation, probability 0.30), the fallback protocol provides explicit 5-step instructions covering variant generation (F1), diff analysis (F2), single-round debate (F3), base selection (F4), and merge + contract (F5). This is categorically different from the original failure: instead of Claude improvising with ~20% pipeline coverage, it follows a prescribed procedure covering ~60-70% of pipeline functionality. The critical missing pieces from the original failure -- diff analysis, debate, and scoring -- are all present in the fallback.

3. **Return contract transport (Epic 3)**: The `fallback_mode: true` field in the return contract ensures the consuming skill (sc:roadmap) knows the output came from a degraded path and can warn the user appropriately. Task 3.2 specifies differentiated warning language: "Output produced by degraded fallback (single-round debate, no convergence tracking). Quality is substantially reduced compared to full adversarial pipeline." This transparency was entirely absent in the original failure.

**Quantitative improvement**: The original behavior preserved ~20% of pipeline functionality. The F1-F5 fallback preserves ~60-70% (variant generation + diff analysis + single-round debate + base selection + merge). This is a 3x improvement in degraded-mode quality. Combined with the primary path (which should work in the majority case after RC1/RC2 fixes), the expected pipeline functionality is approximately: `P(primary) * 100% + P(fallback) * 65% + P(total_failure) * 0%` where P(primary) is high given RC1+RC2 fixes.

### AGAINST Position (Challenger)

The sprint specification provides meaningful improvement over the status quo but falls short of *effectively mitigating* RC5 for three structural reasons:

1. **The fallback IS still degraded -- by design**: Task 1.4's F3 specifies "Single-Round Debate" where the full sc:adversarial pipeline uses multi-round debate with convergence tracking. The spec itself acknowledges this through the `fallback_mode` differentiated warning: "Quality is substantially reduced compared to full adversarial pipeline." A 60-70% functional fallback is better than 20%, but it is not mitigation of RC5 -- it is a better-managed instance of the same problem. RC5's core issue is that Claude produces degraded output when the full pipeline is unavailable. The fallback *formalizes* the degradation rather than *eliminating* it.

2. **Partial deferral creates a coverage gap**: The sprint explicitly defers S05 (Claude Behavior: probe-and-branch + quality gate, solution score 0.732). S05's specific recommendations included a probe-and-branch mechanism and a quality gate that would detect when fallback output is below acceptable thresholds. Without S05, there is no *automated* quality gate on fallback output. The convergence threshold check in step 3e (>= 0.6) applies to the return contract's `convergence_score`, but in fallback mode, convergence tracking is not performed (F3 is single-round, no convergence loop). The `convergence_score` field in fallback mode will be either absent, null, or a fabricated estimate -- none of which provide genuine quality assurance.

3. **Claude behavioral drift is unaddressed**: RC5 is fundamentally about how Claude *interprets* instructions when edge cases arise. The verb glossary (Task 2.1) helps with the specific ambiguity that triggered the original failure, but it does not address future ambiguities. What happens when Claude encounters an instruction not in the glossary? What happens when the fallback protocol's F1-F5 steps themselves contain ambiguity that Claude must interpret? The sprint has no mechanism for detecting or preventing future instances of the same behavioral pattern. Risk R6 ("Fallback protocol bitrot") acknowledges this at LOW probability (0.15) with only a version comment as mitigation -- a passive measure that depends on human review processes.

4. **The "partial absorption" claim is imprecise**: The spec states RC5 is "partially absorbed by S02's fallback in Wave 2 step 3d." But S02 addresses RC2 (Specification-Execution Gap), not RC5 directly. The fallback protocol in step 3d is part of S01 (Task 1.4), not S02. S02's contribution is the verb glossary and atomic sub-steps, which prevent the *specific* ambiguity that triggered RC5 but do not address Claude's general tendency to approximate when faced with obstacles. The attribution is muddled, making it harder to verify completeness.

---

## Round 2: Cross-Examination

### Advocate Challenges Challenger

**Q1**: You claim the fallback "formalizes degradation rather than eliminating it." But RC5's impact score is 0.70, not 1.0, precisely because some output WAS produced. If the fallback raises functional coverage from ~20% to ~65%, and the primary path (which should work most of the time after RC1+RC2 fixes) provides 100%, isn't the residual risk of RC5 dramatically reduced? The expected value of pipeline functionality goes from ~20% (always falling back) to ~93% (assuming 80% primary path success, 20% fallback at 65%). How is that not effective mitigation?

**Q2**: You raise the convergence_score gap in fallback mode. But step 3e already has a guard: "If return-contract.yaml not found, treat as status: partial with convergence_score: 0.0." And Task 3.2 requires `fallback_mode: true` to trigger a differentiated warning. The consumer explicitly knows it is receiving fallback output and adjusts expectations. What additional quality gate would S05 have provided that this transparency mechanism does not?

**Q3**: On "behavioral drift" -- you are essentially arguing that any fix short of solving the general AI instruction-following problem is insufficient. Is that a fair standard for a sprint-scoped remediation? The sprint addresses the *specific* behavioral failure that occurred, provides a structured fallback for the *known* failure modes, and flags future drift as a maintenance risk. What concrete, sprint-achievable mechanism would you propose instead?

### Challenger Challenges Advocate

**Q1**: You calculate ~93% expected functionality based on 80% primary path success. But Risk R1 (Task agent cannot access Skill tool) has probability 0.40, and Risk R2 ("skill already running") has probability 0.30. These are not independent -- they represent different failure modes of the same invocation attempt. The combined probability of primary path failure could be as high as 0.40-0.55. With a 55% fallback rate, expected functionality drops to: `0.45 * 100% + 0.55 * 65% = 80.75%`. Is 81% "effective mitigation" of a root cause with 0.79 severity?

**Q2**: The fallback protocol's F2 (Diff Analysis) and F3 (Single-Round Debate) are dispatched as independent Task agents. Each Task agent receives input files but operates without the behavioral context of the full sc:adversarial pipeline. How confident are you that Task agents, operating outside sc:adversarial's SKILL.md behavioral constraints, will produce diff analysis and debate output that matches the quality the pipeline would produce? This is precisely the RC5 pattern: Claude approximating a structured process with ad-hoc Task agents.

**Q3**: Task 0.0 (Skill Tool Probe) is the decision gate. If it reveals the primary path is non-viable, the spec says to "Promote the fallback protocol to the ONLY invocation mechanism." In that scenario, EVERY invocation of the adversarial pipeline goes through the degraded F1-F5 path. The sprint would ship with 0% primary path usage. How does permanently shipping a 65%-functional fallback constitute effective RC5 mitigation?

---

## Round 3: Rebuttals

### Advocate Rebuttal

**On probability estimates (CQ1)**: The 0.40 and 0.30 probabilities are pre-sprint estimates for risks that are *specifically being mitigated* by Epic 1. Task 0.0 provides empirical data before implementation proceeds. If the probe shows Task agents can access the Skill tool, R1 drops to near zero. If it shows "skill already running" applies only to the same skill name, R2 drops significantly. The sprint is designed to resolve this uncertainty, not to accept it as a given.

**On Task agent quality (CQ2)**: This is a fair concern, but it conflates two different issues. The original RC5 failure involved Claude inventing its own procedure (spawn system-architect, generate variants, manually synthesize). The F1-F5 fallback provides *explicit instructions* for each step including inputs, outputs, and failure conditions. A Task agent following "compare all variants, produce diff-analysis.md covering structural differences, content differences, contradiction detection, and unique contributions" is qualitatively different from Claude deciding on its own to do something vaguely similar. The instructions channel behavior even without the full SKILL.md context.

**On fallback-only scenario (CQ3)**: If Task 0.0 reveals the primary path is entirely non-viable, the sprint adapts. The fallback-only scenario is explicitly planned for (line 72-73: "Promote the fallback protocol to the ONLY invocation mechanism"). In that scenario, the sprint still delivers a 3x improvement over the original failure (65% vs 20% functionality). The follow-up sprint for S05 would then become higher priority. But shipping 65% is better than shipping 20%, which is what we have today.

### Challenger Rebuttal

**On root cause elimination**: The advocate correctly identifies that fixing RC1+RC2 removes the *proximate* triggers. But RC5 is categorized as a distinct root cause precisely because it describes a *pattern of behavior*, not a specific trigger. The ranked-root-causes document validates RC5 independently: "Scores held up. This is the most honestly self-assessed of the five reports." If RC5 were merely a consequence of RC1+RC2, it would not have been ranked separately. The sprint treats it as a consequence; the diagnostics treat it as independent. This inconsistency suggests incomplete understanding of the behavioral risk.

**On Task 0.0 resolving uncertainty**: If the probe reveals favorable results (Skill tool accessible, cross-skill invocation works), then yes, the primary path handles most of RC5's impact. But the probe's outcome is unknown at spec time. The spec should be evaluated on what it guarantees, not what it hopes. What it guarantees is a 65%-functional fallback. What it hopes is that the primary path works.

**On "quality is substantially reduced" warning**: Transparency about degradation is not the same as mitigation of degradation. A doctor who tells you "this treatment will only work 65% as well as the full treatment" is being honest, but the patient is still receiving inferior care. The user warning in Task 3.2 is good practice, but it does not make the output better -- it just makes the user aware it is worse. RC5 mitigation should aim to make the output better, not just the user experience of receiving worse output.

---

## Scoring Matrix (0.0 - 1.0)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| **1. Root Cause Coverage** | 0.70 | The sprint addresses RC5's proximate triggers (RC1 wiring gap + RC2 ambiguity) comprehensively via Epics 1-2. The 5-step fallback protocol (F1-F5) provides structured degradation. However, RC5 as a behavioral pattern (Claude approximating when obstacles arise) is not directly addressed -- only the specific instance is. The dedicated S05 solution (probe-and-branch + quality gate) is deferred. Coverage is substantial but incomplete. |
| **2. Completeness** | 0.55 | Significant gaps remain. (a) No automated quality gate on fallback output. (b) Convergence score is meaningless in fallback mode (single-round debate, no convergence loop). (c) Task agent behavioral fidelity to full-pipeline steps is untested and unverified. (d) S05's probe-and-branch mechanism is absent. (e) No mechanism for detecting future behavioral drift beyond passive version comments (R6). The sprint addresses the invocation chain end-to-end but treats RC5's behavioral dimension as a side effect rather than a first-class concern. |
| **3. Feasibility** | 0.80 | The proposed mechanisms are realistic and implementable within sprint scope. The verb glossary, atomic sub-steps, fallback protocol, and return contract are all concrete, file-level changes. Task 0.0's decision gate provides empirical grounding. The main feasibility risk is whether Task agents executing F2/F3 will produce adequate quality -- this is inherently uncertain but the structured instructions improve the odds. |
| **4. Blast Radius** | 0.75 | Changes are well-scoped to 4 files. The fallback protocol adds significant new instruction text to SKILL.md, which increases the surface area for future interpretation ambiguity (the very problem RC5 describes). However, the verb glossary and atomic sub-steps constrain this risk. R6 (fallback bitrot) is a legitimate ongoing concern but is acknowledged and flagged. No unintended side effects are apparent. |
| **5. Confidence** | 0.60 | Confidence is moderate. The primary path (if viable) mitigates RC5 well. But the primary path's viability depends on Task 0.0's empirical outcome, which is unknown at spec time. If the primary path fails, the fallback-only scenario delivers meaningful improvement (3x over status quo) but leaves RC5 partially unresolved. The partial deferral of S05 means the spec consciously accepts residual RC5 risk. The "partial absorption" framing is imprecise -- it overstates how much of RC5 is covered by S01/S02's fallback versus what S05 would have added (quality gates, probe-and-branch). |

**Weighted Composite Score**: 0.68

Calculation: `(0.70 * 0.25) + (0.55 * 0.25) + (0.80 * 0.20) + (0.75 * 0.15) + (0.60 * 0.15) = 0.175 + 0.1375 + 0.16 + 0.1125 + 0.09 = 0.675 ~ 0.68`

---

## Verdict: NEEDS AMENDMENTS

### Rationale

The sprint specification provides meaningful improvement over the status quo for RC5 but does not constitute effective mitigation on its own. The core tension is that the sprint treats RC5 as a downstream consequence of RC1+RC2 (and therefore "partially absorbed" by S01+S02) while the diagnostics validate RC5 as an independent root cause with its own behavioral dimension.

**What works well**:
- Removing the proximate triggers (Skill tool wiring + verb ambiguity) is the right first step
- The F1-F5 fallback protocol is a 3x improvement over the original ~20% degradation
- The return contract's `fallback_mode` field provides transparency to consumers
- Task 0.0's empirical probe resolves key uncertainty early

**What falls short**:
- No automated quality gate on fallback output (S05's key contribution, deferred)
- Convergence score is undefined/meaningless in fallback mode, creating a blind spot in step 3e routing
- Task agent fidelity to full-pipeline steps is assumed but not verified
- Future behavioral drift is acknowledged (R6) but only passively mitigated

### Recommended Amendments

1. **Add a fallback quality gate** (low cost, high value): In step 3e, when `fallback_mode: true`, require the consuming skill to check that all 5 fallback artifacts (variant files, diff-analysis.md, debate-transcript.md, base-selection.md, merged-output.md) exist before proceeding. If any artifact is missing, treat as `status: failed` with `failure_stage` set to the missing step. This provides structural verification without requiring the deferred S05 quality scoring.

2. **Define convergence_score semantics in fallback mode**: Specify that fallback mode should set `convergence_score` to a fixed sentinel value (e.g., 0.5) with a comment "estimated, not measured" rather than leaving it undefined. This ensures step 3e's routing logic (>= 0.6 threshold) has a defined input and the threshold correctly triggers the "warn and proceed" path rather than silently passing or failing.

3. **Add behavioral anchoring to F2/F3 Task agent prompts**: In the fallback protocol, specify that Task agents dispatched for F2 (Diff Analysis) and F3 (Single-Round Debate) must be given a prompt preamble referencing sc:adversarial's Step 1 and Step 2 output format requirements. This channels Task agent behavior toward the pipeline's expected output structure without requiring full SKILL.md context.

4. **Elevate R6 mitigation**: Change R6 from passive (version comment) to active: add to the Definition of Done a check that the F1-F5 fallback step descriptions match the corresponding sc:adversarial pipeline steps at time of implementation. This catches bitrot at implementation time rather than hoping for future manual review.

These amendments are sprint-achievable additions, not scope expansions. They close the gap between "partial absorption" and effective mitigation without requiring the full S05 solution.

---

*Debate conducted 2026-02-23. Analyst: claude-opus-4-6 (debate-orchestrator mode).*
*Inputs: sprint-spec.md, ranked-root-causes.md, sc-adversarial/SKILL.md.*
*Methodology: Structured adversarial debate with advocate/challenger positions, cross-examination, scoring on 5 criteria.*
