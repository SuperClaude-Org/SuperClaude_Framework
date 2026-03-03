# T02 Adversarial Debate: Does the Sprint Spec Effectively Mitigate RC1?

**RC1: Invocation Wiring Gap** -- The Skill tool is absent from `allowed-tools` in both `roadmap.md` and `SKILL.md`. The Skill tool description says "Do not invoke a skill that is already running," confirming skill-to-skill chaining was never designed. Zero precedents for cross-skill invocation exist. Likelihood: 0.90, Impact: 0.90, Combined Score: 0.900.

**Debate question**: Does the sprint specification effectively mitigate RC1?

---

## FOR Position (Advocate)

The sprint specification addresses RC1 with a layered, empirically-grounded approach that accounts for both the known wiring gap and the uncertainty surrounding the Skill tool's runtime behavior.

### Argument 1: Task 0.0 eliminates the largest unknown before any code is written

RC1's danger is not merely that the Skill tool is absent from `allowed-tools` -- it is that we do not know whether adding it will be sufficient. The "Do not invoke a skill that is already running" constraint could block cross-skill invocation entirely, regardless of `allowed-tools`. Task 0.0 (Skill Tool Probe) directly confronts this by empirically testing three scenarios: Task-agent Skill tool access, main-agent cross-skill invocation, and the semantics of "already running." The decision gate has four explicit branches, each with a defined adaptation path. This is not optimistic hand-waving; it is a scientific probe with falsifiable hypotheses and contingency plans.

No other approach to RC1 could responsibly skip this step. The spec earns credibility by making Task 0.0 a hard blocker for all subsequent work.

### Argument 2: Tasks 1.1 and 1.2 directly remove the infrastructure blocker

The most concrete aspect of RC1 is the absence of `Skill` from `allowed-tools`. Tasks 1.1 and 1.2 add it to both `src/superclaude/commands/roadmap.md` and `src/superclaude/skills/sc-roadmap/SKILL.md`. The acceptance criteria are binary and verifiable: either `Skill` appears in the allowed-tools line or it does not. Verification Test 1 provides a grep-based confirmation. This is a textbook minimal fix for the textbook infrastructure gap.

### Argument 3: Task 1.4 provides a comprehensive fallback that ships the feature regardless

Even if the primary Skill tool invocation path fails (Risk R1, probability 0.40), Task 1.4 defines a 5-step fallback protocol (F1-F5) that reconstructs a degraded version of the adversarial pipeline using only Task agents. Each fallback step has defined inputs, outputs, and failure actions. The fallback writes `return-contract.yaml` with `fallback_mode: true` and appropriate `failure_stage` on any intermediate failure. This means the feature ships even in the worst case -- the sprint cannot be blocked by Skill tool limitations.

The fallback is not an afterthought. It is a first-class citizen with the same structural rigor as the primary path: explicit state machine, sequential hard-stop semantics, WARNING emission before degraded execution.

### Argument 4: Risk R1 and R2 explicitly model the two failure modes

The risk register quantifies both failure scenarios:
- R1 (Task agent cannot access Skill tool, probability 0.40, impact HIGH): mitigated by the fallback protocol.
- R2 ("Skill already running" blocks invocation, probability 0.30, impact HIGH): mitigated by explicit inclusion of this error type in the fallback trigger (step 3d).

Both risks have concrete mitigations tied to specific tasks. The combined probability of both being needed is high (~0.58 if independent), which is why the fallback protocol is so detailed -- the spec authors expected it would likely be used.

### Argument 5: The Definition of Done is verifiable and complete for RC1

The DoD includes:
- `Skill` in `allowed-tools` in both files (checked by Verification Test 1)
- Fallback trigger covers three error types: tool not in allowed-tools, skill not found, skill already running (checked by Verification Test 2, item 4)
- Wave 2 step 3 contains explicit Skill tool call syntax (checked by Verification Test 2, item 3)

Every RC1-relevant claim is backed by a verification step. There is no gap between "what the spec promises" and "how we know it was delivered."

---

## AGAINST Position (Challenger)

The sprint specification addresses the surface symptoms of RC1 but contains structural blind spots, untested assumptions, and an over-reliance on a fallback mechanism that has never been validated.

### Argument 1: Task 0.0 is a probe, not a mitigation -- and the spec has no plan for its most likely outcome

Task 0.0 tests whether cross-skill invocation works. But the spec's own Risk R1 assigns a 0.40 probability that Task agents cannot access the Skill tool, and R2 assigns 0.30 probability that "skill already running" blocks invocation. The combined probability that the primary path works is approximately 0.42 (assuming independence: 0.60 * 0.70). In other words, the spec's own risk model predicts the primary path will fail more often than it succeeds.

Yet the spec is structured around the primary path succeeding. Epic 1 is titled "Invocation Wiring Restoration" -- but the most likely outcome is that invocation wiring is confirmed impossible and the entire feature runs on a fallback that was never the original design. Task 0.0's decision gate says "Promote the fallback protocol to the ONLY invocation mechanism. Remove primary-path framing." But no tasks exist for this rewrite. What does the sprint look like after primary-path failure? The spec is silent.

### Argument 2: The fallback protocol (F1-F5) is untested and significantly weaker than the full pipeline

Task 1.4's 5-step fallback is described with structural rigor, but it has never been executed. It attempts to reconstruct the adversarial pipeline using sequential Task agent dispatches, but:

1. **F3 (Single-Round Debate)** reduces a multi-round convergence-tracking debate to one round. The ranked root causes document notes that the observed failure already produced a "~20% of the adversarial pipeline's functionality." A single-round debate may not materially exceed that baseline.

2. **No convergence tracking**: The full sc:adversarial pipeline tracks convergence across rounds. The fallback has no convergence mechanism -- it produces `convergence_score: 0.0` or whatever F5 writes. Step 3e routes on `convergence_score >= 0.6`, but the fallback cannot produce a meaningful convergence score because it never measured convergence.

3. **No quality gate on fallback output**: The spec differentiates `fallback_mode: true` with a WARNING message, but it still proceeds with the output. There is no acceptance threshold for fallback quality. A user could receive output that is barely better than the original failure mode, stamped with a warning they might ignore.

### Argument 3: "Adding Skill to allowed-tools" may be necessary but not sufficient

RC1's key evidence includes: "skill-to-skill chaining was never designed" and "zero precedents for cross-skill invocation exist." Adding `Skill` to `allowed-tools` removes one barrier, but:

1. **The Skill tool's internal validation** may reject calls from within an active skill context, regardless of `allowed-tools`. The tool description says "Do not invoke a skill that is already running" -- this is a behavioral instruction to Claude, not a programmatic check. But Claude may interpret it conservatively, refusing to invoke ANY skill while one is active.

2. **No framework changes**: The spec modifies only markdown files. It does not modify the Skill tool itself, Claude Code's skill loading mechanism, or any runtime code. If the limitation is architectural (skills are designed as exclusive-lock resources), no amount of markdown editing will fix it. The spec assumes the limitation is purely a configuration gap (missing from allowed-tools), but the root cause analysis itself notes it was "never designed."

3. **Task 0.0 is the only safeguard** against this assumption being wrong. But Task 0.0 is a single test in a single session. The Skill tool's behavior may vary across Claude Code versions, model updates, or session contexts.

### Argument 4: Risk R2 mitigation is superficial

R2 ("Skill already running" blocks invocation) is mitigated by "fallback trigger in step 3d must cover 'skill already running' error type explicitly." But this is not a mitigation of the risk -- it is a detection of the failure. The actual mitigation is the fallback protocol, which (per Argument 2) is unvalidated and substantially weaker.

A true mitigation would be one of:
- A mechanism to suspend the calling skill before invoking the target skill
- A mechanism to invoke the target skill in a separate context
- Confirmation that the "already running" constraint applies only to the same skill name, not to any skill

The spec acknowledges this question in Task 0.0 ("Does 'Do not invoke a skill that is already running' apply to (a) the exact same skill name, (b) any skill while another is active, or (c) the same skill instance?") but has no contingency beyond the fallback if the answer is (b).

### Argument 5: The spec conflates "shipping the feature" with "mitigating RC1"

RC1 is "Invocation Wiring Gap" -- the Skill tool is absent from allowed-tools, and cross-skill invocation was never designed. The sprint spec's response is: add Skill to allowed-tools, test if it works, and if it does not, run a degraded fallback.

But RC1's mitigation is not "the feature ships somehow." It is "cross-skill invocation works." If the primary path fails and the fallback is used, RC1 is not mitigated -- it is bypassed. The fallback does not fix the wiring gap; it routes around it. This is a valid engineering choice, but it should be scored honestly: the spec mitigates RC1's impact on the user (they get output), not RC1 itself (the invocation mechanism remains broken).

---

## CROSS-EXAMINATION

### Challenger to Advocate

**Question**: You cite Task 0.0 as the spec's strongest safeguard. But Task 0.0 produces a decision gate result, not a fix. If the probe reveals that cross-skill invocation is fundamentally impossible (answer (b) to the "already running" question), what specific tasks in the sprint spec restore invocation wiring? The fallback protocol is not invocation wiring -- it is an alternative to invocation wiring.

**Advocate's response**: This is a fair distinction. If cross-skill invocation is architecturally impossible, no sprint-level markdown change can create it. But the spec is honest about this: it defines the fallback as the ONLY path in that scenario and instructs "Remove primary-path framing." The sprint's goal is "Restore full adversarial pipeline functionality" -- not "Make the Skill tool support cross-skill invocation." The fallback protocol delivers 60-70% of the pipeline's value. The spec mitigates RC1's downstream effects even if it cannot eliminate RC1's root infrastructure limitation. Whether that constitutes "effective mitigation" depends on whether we define mitigation as "fix the root cause" or "neutralize the root cause's impact."

### Advocate to Challenger

**Question**: You argue the fallback is "untested and significantly weaker." But the original failure mode was ~20% pipeline functionality with no structured output. Even a single-round debate with explicit variant generation, diff analysis, and scored base selection is structurally superior. Given that the alternative is the status quo (complete pipeline bypass), is "untested but structurally sound" not a significant improvement over "no fallback at all"?

**Challenger's response**: It is an improvement over the status quo, yes. But "better than nothing" is a low bar for a sprint that claims to mitigate a 0.900-severity root cause. The fallback's structural soundness is asserted, not demonstrated. F3 (single-round debate) has no precedent in the codebase. F5 (merge + contract) has no quality criteria. The spec would be substantially stronger if it included a fallback validation step -- run the fallback on a known input and verify the output meets minimum quality thresholds. Without that, we are taking it on faith that 5 sequential Task agent dispatches will coherently reconstruct a pipeline that was purpose-built as an integrated skill.

---

## SCORING

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **1. Root cause coverage** | 0.75 | The spec addresses the surface mechanism of RC1 (Skill absent from allowed-tools) completely via Tasks 1.1-1.2. It addresses the "never designed" aspect partially through Task 0.0's empirical probe. However, it cannot address the possibility that cross-skill invocation is architecturally unsupported -- that is beyond the sprint's scope. The fallback covers the impact but not the cause. |
| **2. Completeness** | 0.70 | Gaps exist: (a) no plan for sprint restructuring if Task 0.0 reveals primary path impossible, (b) no quality threshold for fallback output, (c) no validation test for the fallback protocol itself, (d) convergence scoring is meaningless in fallback mode. The 5-step fallback is detailed but unvalidated. |
| **3. Feasibility** | 0.85 | Tasks 1.1-1.2 (add Skill to allowed-tools) are trivially feasible. Task 0.0 (probe) is straightforward. Task 1.3 (Skill invocation rewrite) is feasible if the primary path works. Task 1.4 (fallback protocol) is feasible to write but untested at runtime. The main feasibility risk is that the primary path fails and the sprint becomes fallback-only, which changes the character of the deliverable. |
| **4. Blast radius** | 0.80 | Adding Skill to allowed-tools is low-risk (additive change). The fallback protocol is contained within Wave 2 step 3. The main blast radius concern is Risk R6 (fallback bitrot) -- the fallback duplicates sc:adversarial's logic and will drift. The spec acknowledges this with a version comment but no automated drift detection. The rewrite of Wave 2 step 3 touches a critical path, but Risk R5 mitigates this with single-author coordination. |
| **5. Confidence** | 0.65 | The spec's own risk model implies a ~42% probability that the primary path works. The fallback is the likely execution path, and it has never been tested. Confidence that the feature ships is moderate-high; confidence that RC1 (the invocation wiring gap) is actually resolved is moderate-low. The spec effectively converts RC1 from "complete failure" to "degraded-but-functional," which is a meaningful improvement but not a full resolution. |

### Weighted Average

Using equal weights (0.20 each):

```
Overall = (0.75 + 0.70 + 0.85 + 0.80 + 0.65) / 5 = 0.750
```

---

## VERDICT: NEEDS AMENDMENTS

**Score: 0.750** -- The sprint specification is a strong engineering response to RC1 that demonstrates rigorous thinking about failure modes and fallback paths. However, it falls short of "sufficient" for three reasons:

1. **No fallback validation**: The fallback protocol (F1-F5) is the most likely execution path (~58% probability by the spec's own risk model) but has no validation test. The verification plan includes Test 5 (end-to-end) but marks it as "post-sprint, manual" and only checks whether the fallback "activates and produces expected partial-quality output." A dedicated fallback validation test -- run F1-F5 on known input, verify output structure and minimum quality -- should be added to the sprint's Definition of Done.

2. **No sprint adaptation plan**: Task 0.0's decision gate says to "adapt the sprint" if the primary path fails, but no adapted task list exists. The spec should include a brief "Fallback-Only Sprint Variant" section that specifies which tasks are modified or removed when the primary path is non-viable.

3. **Conflation of impact mitigation with root cause resolution**: The spec should explicitly state that if the primary path fails, RC1 is not resolved but its impact is reduced from 0.90 to approximately 0.30-0.40 (degraded but functional output). This honest framing would improve confidence scoring and set correct expectations for follow-up work.

### Recommended Amendments

| # | Amendment | Effort | Impact |
|---|-----------|--------|--------|
| A1 | Add Verification Test 6: "Fallback Protocol Validation" -- run F1-F5 on a test input, verify return-contract.yaml structure, verify output files exist | 1-2 hours | High -- validates the most-likely execution path |
| A2 | Add "Fallback-Only Sprint Variant" section after Task 0.0, listing task modifications when primary path is confirmed non-viable | 30 minutes | Medium -- removes ambiguity about sprint adaptation |
| A3 | Add explicit residual risk statement: "If primary path fails, RC1 is bypassed (not resolved). Residual impact estimated at 0.30-0.40. Follow-up sprint required for architectural investigation of cross-skill invocation." | 15 minutes | Medium -- sets honest expectations |
| A4 | Add minimum quality threshold for fallback output (e.g., "fallback output must contain at least 2 differentiated variants, 1 diff analysis, and 1 scored comparison") | 30 minutes | Medium -- prevents low-quality fallback from silently passing |

---

*Debate conducted 2026-02-23. Analyst: claude-opus-4-6 (adversarial debate mode).*
*Inputs: sprint-spec.md, ranked-root-causes.md.*
*Methodology: Structured FOR/AGAINST debate with cross-examination, 5-dimension scoring (0.0-1.0), weighted verdict.*
