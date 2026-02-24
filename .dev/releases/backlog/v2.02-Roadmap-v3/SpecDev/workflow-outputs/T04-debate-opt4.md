# T04: Adversarial Debate -- Optimization 4 (Defer G2/G3 Until After Task 0.0)

> **Debate Panel**: Advocate (FOR), Challenger (AGAINST), Moderator (CROSS-EXAMINATION)
> **Date**: 2026-02-23
> **Subject**: Optimization 4 -- Defer G2 (Fallback Validation Test) and G3 (Fallback Sprint Variant) until after Task 0.0 gate
> **Context**: Quality Advocate dissented in T03 panel, arguing untested fallbacks reproduce the exact failure mode this sprint exists to fix

---

## Optimization 4: Summary

**Proposal**: Convert G2 (fallback validation test, 1-2 hrs) and G3 (fallback-only sprint variant, 30 min) from unconditional work into conditional work gated on Task 0.0 outcome. If Task 0.0 confirms the primary path is viable (~58% probability), defer both to the follow-up sprint. If primary path is blocked (~42%), implement both immediately.

**Claimed savings**: 2.0 hours (~13.3% of sprint). **Claimed effectiveness impact**: 0.15.

---

## FOR Position: Optimization 4 Should Be Adopted

### Argument 1: The conditional gate is structurally sound

Task 0.0 is the very first action in the sprint. It produces a binary decision before any other work begins. This is not a deferred decision that creates downstream risk -- it is an upfront decision that eliminates unnecessary work. If the primary path works, the fallback is a contingency for a scenario that has been empirically disproven within the sprint's own execution context.

Spending 2+ hours testing a fallback for a path that was just confirmed to work is the textbook definition of speculative effort. The sprint has a 15-hour budget. Allocating 13% of that budget to testing a backup plan for a scenario you have already ruled out is poor resource allocation.

### Argument 2: The DVL schema validator provides a compensating control

Even if Optimization 4 is adopted and the fallback goes untested in this sprint, the `validate_return_contract.py` script (DVL Task 3.5) provides structural validation of `return-contract.yaml` regardless of which path produced it. If the fallback ever fires in production and produces a malformed contract, the schema validator catches the structural failure. This is not "no safety net" -- it is a different, lighter safety net that matches the probability of the scenario.

### Argument 3: The time savings are the largest single optimization

At 2.0 hours, this is 35% of total optimization savings (5.75 hrs). Rejecting it would reduce total sprint savings from 38.3% to 25%, undermining the optimization effort's primary goal. The remaining four optimizations save 3.75 hours -- still meaningful, but significantly less impactful. If the panel wants to deliver a meaningfully shorter sprint, this optimization is the centerpiece.

### Argument 4: Fallback testing is better placed in the follow-up sprint

The follow-up sprint (S05) is explicitly scoped for quality gates and hardening. Testing the fallback in S05 means it gets tested with the full quality infrastructure in place -- including the DVL scripts, the return contract schema, and any lessons learned from the primary path's execution. Testing it now, before that infrastructure exists, produces a lower-quality test anyway.

### Argument 5: G3 deferral is uncontroversial even the dissenter accepts it

The Quality Advocate explicitly accepted deferring G3 (the fallback-only sprint variant). This is 30 minutes of the 2.0-2.5 hour savings. The debate is really about G2 (the fallback validation test), which is 1-2 hours. Framing this as "2.0 hours of savings" slightly overstates the contested portion.

---

## AGAINST Position: Optimization 4 Is Risky and Undermines Sprint Purpose

### Argument 1: This sprint exists to fix silent failures -- deferring fallback testing creates a new one

The entire diagnostic chain (ranked-root-causes.md) traces the original failure to RC5: "Claude rationally fell back to spawning generic Task agents... forfeiting the adversarial pipeline's 5-step structured debate, scoring, and contradiction detection." The fallback protocol in Task 1.4 is this sprint's answer to that exact failure mode. Shipping an untested fallback is building a safety net and then never checking whether it has holes. If the Skill tool works during Task 0.0 but fails intermittently due to context limits, session length, or platform-specific behavior, the first time the fallback is exercised will be in a real user session. A broken fallback would produce a silent failure -- the exact problem this sprint was created to solve.

### Argument 2: Task 0.0's binary gate does not capture intermittent failure modes

Task 0.0 tests the Skill tool once, in controlled conditions, at the start of a fresh session. It does not test:
- Skill tool behavior under high context pressure (late in a session)
- Skill tool behavior when invoked from within a complex Wave 2 pipeline
- Skill tool behavior when the target skill (sc:adversarial) takes a long time to execute
- Platform-specific differences between Claude environments

A single positive probe is weak evidence that the fallback will never be needed. The sprint's own risk register assigns R1 a probability of 0.40 -- meaning the sprint authors themselves believe there is a 40% chance the primary path fails. The "58% probability" used to justify the expected-value calculation is the complement of this risk. A 40% failure probability is not a low-probability scenario that justifies skipping testing.

### Argument 3: The DVL schema validator is not a substitute for functional testing

`validate_return_contract.py` validates the **structure** of `return-contract.yaml` -- correct fields, correct types, no sentinel values. It does not validate:
- Whether the fallback protocol actually produces meaningful content in the variant files
- Whether the fallback's F1-F5 (or F1-F3 per Optimization 3) steps execute in sequence
- Whether the fallback correctly writes `fallback_mode: true`
- Whether the fallback's failure handlers write the correct `failure_stage` values
- Whether the merged output from the fallback is usable by downstream consumers

A schema validator catching a malformed YAML file is the last line of defense. The fallback validation test (G2) is the first line. Removing the first line because the last line exists is defense-in-breadth reduction, not defense-in-depth preservation.

### Argument 4: The "test it in S05" argument assumes S05 happens promptly

Follow-up sprints are aspirational. If S05 is delayed, deprioritized, or scoped differently, the fallback remains untested indefinitely. The current sprint is the only guaranteed opportunity to test it, because the fallback protocol is being written in this sprint. Testing code in the same sprint it is written is basic engineering hygiene. "We will test it later" is the most common lie in software development.

### Argument 5: The time savings are inflated by the expected-value framing

The optimization claims "2.0 hours saved" but the honest expected-value calculation (shown in the optimization's own text) is 1.3 hours: `0.58 * 2.25 + 0.42 * 0 = 1.3 hrs`. The optimization then discards its own calculation and reports the best-case number. In the 42% scenario where the primary path is blocked, there are zero savings AND G2 becomes the critical validation mechanism for the now-primary fallback path. The optimization is effectively a bet: 58% chance of saving 2 hours, 42% chance of saving nothing. The "net benefit" of 1.70 hours is computed against the best-case, not the expected value.

---

## CROSS-EXAMINATION

### FOR challenges AGAINST's strongest argument (Argument 1: silent failure recurrence)

**FOR**: "You claim shipping an untested fallback repeats the original failure. But the original failure was *invisible* -- Claude silently degraded with no warning, no error, and no indication that the adversarial pipeline was skipped. The fallback protocol in Task 1.4 is fundamentally different: it emits a WARNING to the user, it writes `fallback_mode: true` in the return contract, and the consumer (step 3e) displays a differentiated degradation warning. Even if the fallback has bugs, the user *knows* the fallback activated. The original failure's silent nature is what made it critical. The new fallback is loud by design."

**AGAINST responds**: "The fallback being 'loud' depends on the fallback code actually executing correctly. If step F1 crashes before emitting the WARNING, the user sees nothing -- exactly like the original failure. If `return-contract.yaml` is never written because a failure handler has a bug, step 3e's missing-file guard treats it as `status: failed` -- but only if THAT guard was also implemented correctly. You are trusting a chain of untested error handlers to correctly report their own failures. This is precisely the class of bug that functional testing catches and schema validation does not."

### AGAINST challenges FOR's strongest argument (Argument 3: largest time savings)

**AGAINST**: "You argue this optimization is the centerpiece of time savings. But the optimization that saves the most time is also the one with the highest risk to sprint integrity. That is not a coincidence -- large time savings come from cutting large work items, and large work items tend to be large because they are important. The fact that fallback testing is 13% of the sprint budget reflects the sprint authors' judgment that fallback testing is important enough to warrant 13% of the budget. Cutting the largest item is not inherently good -- it requires the strongest justification, which this optimization does not provide."

**FOR responds**: "The 13% budget allocation was made *before* Task 0.0 exists as a conditional gate. The original T02 synthesis classified G2 as 'critical' unconditionally because it was evaluating the fallback in isolation, without considering that the sprint's first action empirically resolves whether the fallback is on the critical path. The conditional gate changes the calculus. If Task 0.0 confirms the primary path, 13% of the budget is allocated to testing a contingency for a disproven scenario. That is not importance -- that is inertia from a pre-gate analysis."

---

## SCORING

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **1. Time Savings** | 0.75 | Claimed 2.0 hrs, but honest expected value is 1.3 hrs (58% viable * 2.25 hrs). Still the largest single optimization. Reduced from 1.0 because the reporting uses best-case rather than expected value. |
| **2. Effectiveness Preservation** | 0.55 | The untested fallback is a real coverage gap. The DVL validator provides partial compensation but does not substitute for functional testing. The "loud fallback" design mitigates but does not eliminate the silent-failure risk. In the viable-path scenario, impact is bounded (fallback may never fire). In the blocked-path scenario, impact is zero (G2 is implemented). Weighted: moderate preservation. |
| **3. Feasibility** | 0.90 | Straightforward conditional gate. Task 0.0 already exists and produces a binary decision. Implementation requires only restructuring the task list, not new design. |
| **4. Risk (higher = lower risk)** | 0.45 | The AGAINST position identifies a genuine concern: intermittent Skill tool failures are not captured by a single probe, and the chain of untested error handlers could reproduce the original silent-failure pattern. The 40% failure probability in the sprint's own risk register means the fallback is not a remote contingency. The "test it in S05" mitigation depends on S05 happening. |
| **5. Net Benefit** | 0.55 | Time savings are real but the risk profile is unfavorable for a sprint whose stated purpose is eliminating silent failures. The optimization saves the most time but carries the most philosophical tension with the sprint's goals. |

**Weighted composite**: `(0.75 + 0.55 + 0.90 + 0.45 + 0.55) / 5 = 0.64`

---

## RECOMMENDATION: Adopt-With-Modifications

### Rationale

The pure FOR position underweights the risk of untested fallbacks in a sprint dedicated to fixing silent failures. The pure AGAINST position overweights the cost of conditional work optimization, ignoring that Task 0.0 provides genuine new information. The correct position is between: adopt the conditional gate but retain a lightweight fallback validation.

### Exact Modifications

**1. Defer G3 unconditionally (accepted by all parties)**
- The fallback-only sprint variant (30 min) is only needed if the primary path is blocked. Defer to conditional execution after Task 0.0. If primary path is viable, G3 is never needed.
- **Savings**: 0.5 hours (in the viable-path scenario).

**2. Replace G2 (full fallback validation test) with G2-lite (fallback smoke test)**
- Instead of running F1-F5 (or F1-F3) on test input and validating all output files (1-2 hours), perform a **single-step smoke test** (15-20 minutes):
  - Dispatch one Task agent with F1 (variant generation) using a minimal test input.
  - Verify: (a) the variant file is written, (b) on simulated failure, `return-contract.yaml` is written with `status: failed` and correct `failure_stage`.
  - This tests the critical chain: Task agent dispatch works, file writing works, failure handling writes the contract.
- **Does NOT test**: multi-step sequencing (F2-F5), merged output quality, convergence scoring. These are deferred to S05.
- **Rationale**: The AGAINST position's strongest argument is that the error-handler chain is untested. The smoke test validates the most critical link (failure -> contract write) without the full 1-2 hour investment. It converts "completely untested" to "structurally validated."

**3. Gate G2-lite on Task 0.0 outcome (conditional)**
- If primary path is **viable**: Run G2-lite (15-20 min). This is the compromise -- not zero testing, not full testing.
- If primary path is **blocked**: Run full G2 (1-2 hrs) + G3. The fallback is now the primary path and must be thoroughly tested.

### Modified Time Savings

| Scenario | Probability | G3 | G2 | Total Saved vs. Original |
|----------|------------|-----|-----|--------------------------|
| Primary viable | 58% | Deferred (30 min saved) | G2-lite instead of G2 (60-100 min saved) | ~1.5 hrs |
| Primary blocked | 42% | Implemented | Full G2 implemented | 0 hrs |
| **Expected value** | | | | **0.87 hrs** |

Compared to the original optimization's expected value of 1.3 hrs, this modification sacrifices ~0.43 hrs of savings to close the untested-fallback gap. Compared to full rejection (0 hrs saved), it preserves 0.87 hrs.

### Sprint Impact

| Metric | Full Adoption | Modified Adoption | Full Rejection |
|--------|--------------|-------------------|----------------|
| Expected time saved | 1.3 hrs | 0.87 hrs | 0 hrs |
| Fallback test coverage | None (viable path) | Smoke test (viable path) | Full test |
| Silent failure risk | Moderate | Low | Minimal |
| Alignment with sprint purpose | Weak | Acceptable | Strong |

### Open Item for Sprint Retrospective

Regardless of adoption mode, document: "Full fallback validation (multi-step sequencing, output quality, convergence scoring) deferred to S05. Smoke test covers failure-handler contract writing only."

---

*Debate conducted 2026-02-23. Structure: FOR/AGAINST/CROSS-EXAMINATION/SCORING.*
*Input: T03-optimizations.md (Optimization 4), sprint-spec.md, ranked-root-causes.md.*
*Quality Advocate dissent from T03 incorporated as AGAINST Argument 1.*
