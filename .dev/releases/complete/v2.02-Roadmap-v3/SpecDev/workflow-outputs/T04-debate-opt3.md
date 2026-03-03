# T04: Adversarial Debate -- Optimization 3 Adoption

> **Subject**: Simplify Fallback Protocol from 5 Steps (F1-F5) to 3 Steps (F1-F3)
> **Date**: 2026-02-23
> **Format**: Structured adversarial debate with cross-examination and scoring
> **Input**: T03-optimizations.md (Optimization 3), sprint-spec.md (Task 1.4, Risk Register), ranked-root-causes.md (RC5, dependency chain)

---

## Optimization 3 Summary

**Current state**: Task 1.4 specifies a 5-step fallback protocol (F1-F5) for when the Skill tool is unavailable: F1 Variant Generation, F2 Diff Analysis, F3 Single-Round Debate, F4 Base Selection, F5 Merge + Contract. Each step has defined input, output, failure action, and individual `return-contract.yaml` failure writes.

**Proposed change**: Reduce to 3 steps. F1 (Variant Generation) unchanged. New F2 merges old F2+F3+F4 into a single "Comparative Analysis + Scoring" step dispatched as one Task agent call. F3 (Merge + Contract) unchanged from old F5. Single unified failure handler replaces per-step handlers.

**Claimed savings**: 1.25 hours (8.3% of sprint). **Claimed effectiveness impact**: 0.15.

---

## FOR Position: Optimization 3 Should Be Adopted

### Argument 1: The 5-step decomposition is artificial granularity for a degraded-mode operation

The fallback protocol exists because the primary path (Skill tool invoking sc:adversarial) is unavailable. The full adversarial pipeline achieves quality through multi-agent structured debate across multiple rounds with scoring convergence and contradiction detection. The 5-step fallback replicates none of these dynamics -- it dispatches sequential Task agents performing single-pass operations. The distinction between "diff analysis" (F2), "single-round debate" (F3), and "base selection" (F4) is a structural echo of the full pipeline imposed on a fundamentally different execution model. A single Task agent performing comparative analysis, scoring, and selection in one pass produces output that is functionally equivalent to three sequential Task agents doing those operations separately, because:

- There is no multi-agent adversarial dynamic between the steps. F2 feeds F3, which feeds F4, in a linear chain with no feedback loops.
- Each Task agent starts from scratch (no shared state between Task agent dispatches), so the "debate" in F3 is a single agent writing advocate statements and then scoring them itself -- not a debate in any meaningful sense.
- The combined prompt ("Compare variants, identify agreements and conflicts, score each variant against the spec objectives, and select the strongest variant as base") gives the Task agent the full analytical scope in one context window, which is actually superior to splitting the reasoning across three disconnected contexts.

### Argument 2: The time savings are real and concentrated in the highest-effort task

Task 1.4 is already identified as the most specification-intensive task in the sprint. Writing 5 detailed step specifications with individual failure handlers, input/output contracts, and failure_stage values is the dominant cost of Task 1.4. Reducing to 3 steps with a single failure handler cuts specification effort nearly in half (~30 min), reduces implementation complexity in the Wave 2 step 3 atomic rewrite (~25 min), and reduces verification from 5 step validations to 3 (~15 min). The 1.25 hours saved is the second-largest single optimization in the T03 set, and it targets the sprint's most complex task.

### Argument 3: The effectiveness impact is bounded by the fallback's inherent quality ceiling

The T02 synthesis already notes that convergence scoring is "meaningless in fallback mode" (G5). The sprint spec itself (Task 3.2) acknowledges that fallback output is "substantially reduced compared to full adversarial pipeline." The fallback's quality ceiling is approximately 60% of the full pipeline regardless of step count. Moving from 5 steps to 3 steps reduces this to approximately 55% -- a 5 percentage point reduction on an already-degraded path. This is the difference between "substantially reduced quality" and "substantially reduced quality," not between "acceptable" and "unacceptable."

### Argument 4: Fewer Task agent dispatches means fewer failure points

Each Task agent dispatch is an independent operation that can fail (timeout, context limits, malformed output). Five dispatches have more failure surface area than three. The combined F2 step eliminates two agent-dispatch boundaries where failures could occur. Since the fallback already operates under adversity (the primary path has failed), reducing the number of operations that must succeed is a reliability improvement.

---

## AGAINST Position: Optimization 3 Is Risky and Undermines Effectiveness

### Argument 1: Diagnostic granularity is critical for a safety net that may fail silently

The entire sprint exists because of a silent failure -- Claude fell back to an approximation without signaling degradation. The 5-step fallback protocol with per-step `failure_stage` values (variant_generation, diff_analysis, debate, base_selection, merge) was designed to prevent exactly this pattern from recurring. If step F3 (debate) fails but F2 (diff analysis) succeeded, the implementer knows the debate logic is broken and can investigate specifically. With the combined F2, a failure in the "comparative analysis + scoring" step provides a single `failure_stage: comparative_analysis` that conflates three distinct operations. Was it the comparison that failed? The scoring? The selection? The combined step masks the failure mode.

This matters because the fallback protocol is the LAST LINE OF DEFENSE. When both the primary path (Skill tool) and the fallback fail, the user gets nothing. Maximizing the diagnostic surface of the fallback is not over-engineering -- it is proportional investment in the system's final safety net.

### Argument 2: Combining three operations into one Task agent prompt increases prompt complexity and failure probability

The proposed combined F2 prompt is: "Compare variants, identify agreements and conflicts, score each variant against the spec objectives, and select the strongest variant as base." This is three distinct cognitive tasks compressed into one instruction. Task agents have finite context windows and attention budgets. Asking a single agent to perform comparison, scoring, AND selection in one pass increases the probability that one operation is performed superficially or skipped entirely. The 5-step protocol ensures each operation gets dedicated attention from a fresh agent with a focused prompt.

The FOR position argues that a single context window is "superior" to split reasoning. This is only true if the combined prompt does not exceed the agent's capacity for simultaneous analytical tasks. For complex variant comparison (3+ variants with multiple dimensions), the cognitive load of compare-score-select in one pass is non-trivial.

### Argument 3: This optimization trades future extensibility for present convenience

The sprint spec explicitly defers quality gates to the follow-up sprint (S05). The T03 document itself acknowledges: "if the follow-up sprint wants to add quality thresholds per fallback step, having 3 steps instead of 5 provides fewer insertion points." The 5-step protocol was designed with extensibility in mind -- each step is a natural point for adding validation, scoring thresholds, or quality gates. Reducing to 3 steps collapses the architecture in a way that may require re-expansion in S05, potentially negating the time savings from this sprint.

### Argument 4: The 0.15 effectiveness impact is under-estimated for a path that addresses RC5

Root cause RC5 (Claude Behavioral Interpretation) is ranked #2 overall with a combined score of 0.79. The fallback protocol is the primary mitigation for RC5 -- it ensures that when Claude cannot invoke sc:adversarial, it follows a structured degradation path rather than an uncontrolled approximation. Simplifying this protocol reduces the quality of the RC5 mitigation. The 0.15 effectiveness impact was scored against Task 1.4 in isolation, not against the sprint's overall RC5 mitigation effectiveness. When scored against RC5's 0.79 problem score, a 0.15 impact on the mitigation is more consequential than it appears.

---

## CROSS-EXAMINATION

### FOR challenges AGAINST's strongest argument (Argument 1: Diagnostic granularity)

**FOR**: You argue that per-step failure_stage values are critical for debugging. But consider: the 5-step fallback has never been implemented, never been tested, and may never execute in production (Task 0.0 may confirm the primary path is viable). You are optimizing the diagnostic granularity of a code path that has a 58% chance of never being exercised. Meanwhile, the implementation cost of 5 detailed step specifications is incurred with 100% certainty. The expected diagnostic value is `0.42 (probability fallback is needed) * P(fallback fails) * value(granular failure_stage)`. Even assuming P(fallback fails) = 0.3 and assigning generous diagnostic value, the expected return on the extra two failure stages is far below the 1.25 hours invested.

Furthermore, the combined F2 step's single output file (`analysis-and-selection.md`) contains the full analytical chain. A human or agent debugging a failure can read the file to determine which sub-operation failed, even without distinct failure_stage values. The diagnostic information is preserved in the artifact; only the programmatic routing is simplified.

**AGAINST responds**: The expected-value argument is misleading. Safety nets are not evaluated on expected frequency of use -- they are evaluated on consequence of failure when they ARE needed. Fire extinguishers are rarely used; this does not justify buying cheaper ones. When the fallback fires AND fails, the per-step failure_stage is the difference between "we know F3 (debate) broke" and "something in the combined analysis step broke, read through the output file to figure out what." The 0.42 probability of needing the fallback is not low -- it is nearly a coin flip. And if the fallback fails, the user gets NO adversarial output at all. The stakes warrant the extra specification effort.

### AGAINST challenges FOR's strongest argument (Argument 1: Artificial granularity)

**AGAINST**: You argue that the 5-step decomposition is "artificial" because it replicates the full pipeline's structure without its multi-agent dynamics. But the decomposition serves a purpose beyond replication: it provides a structured execution scaffold that guides Claude's behavior. Without explicit steps, Claude must self-organize its approach to "compare, score, and select" -- which is exactly the kind of underspecification that caused RC2 (Specification-Execution Gap). The 5-step protocol is explicit instruction that reduces the degrees of freedom in Claude's execution. Reducing to 3 steps re-introduces some of the ambiguity that this sprint is designed to fix.

**FOR responds**: This conflates two different problems. RC2's specification gap was about undefined verbs and compressed steps in the PRIMARY path -- the path that is always executed and must be robust. The fallback path is a contingency that executes under exceptional conditions. Applying the same specification rigor to the fallback as to the primary path is a disproportionate investment. The combined F2 prompt explicitly lists all three operations ("compare variants, identify agreements and conflicts, score each variant, select the strongest variant"). This is not underspecified -- it is a focused, explicit instruction. The difference between "one step with three listed operations" and "three steps with one operation each" is organizational, not informational. The Task agent receives the same analytical guidance either way.

---

## SCORING

| Dimension | Score | Justification |
|-----------|-------|---------------|
| **time_savings** | 0.75 | 1.25 hours is substantial (8.3% of sprint, second-largest single optimization). Score not 1.0 because some savings assume the specification writing is proportional to step count, which may not hold if the combined F2 requires a more carefully crafted prompt to ensure all three operations are performed. |
| **effectiveness_preservation** | 0.78 | The fallback is inherently degraded (~60% quality ceiling). Moving to 3 steps reduces this marginally (~55%). The diagnostic granularity loss is real but partially compensated by the combined output file. Score reflects that the change is not zero-impact but the impact is bounded by the fallback's quality ceiling. |
| **feasibility** | 0.90 | Straightforward specification change. No new tools, no new patterns, no dependencies on external systems. The combined F2 prompt is well-defined. The single failure handler is simpler than per-step handlers. High confidence in implementation. |
| **risk** | 0.70 | (higher = lower risk) Two genuine risks: (1) combined F2 prompt may produce lower-quality output than three focused prompts under high variant count, (2) future S05 sprint may need to re-decompose F2 to add quality gates, partially negating savings. Neither risk is catastrophic -- both have clear mitigations. Score reflects low-moderate risk, not minimal. |
| **net_benefit** | 0.75 | Weighted assessment: the optimization delivers real time savings on the sprint's most complex task, with bounded effectiveness loss on an already-degraded path. The AGAINST position raises valid concerns about diagnostic granularity and future extensibility that prevent a higher score. The net benefit is positive but not overwhelming. |

**Composite score**: (0.75 + 0.78 + 0.90 + 0.70 + 0.75) / 5 = **0.776**

---

## RECOMMENDATION: Adopt-With-Modifications

### Rationale

The FOR position is stronger on the core economic argument: 1.25 hours saved against a bounded 0.15 effectiveness loss on a degraded path is a favorable trade. The AGAINST position is stronger on the diagnostic and extensibility arguments: losing per-step failure granularity in the sprint's last line of defense is a real cost, and S05 may need to re-expand the protocol.

The modification below preserves the FOR position's time savings while addressing the AGAINST position's two strongest concerns.

### Exact Modifications

**Modification 1: Retain sub-operation labels within the combined F2 step**

The combined F2 prompt should instruct the Task agent to structure its output with explicit section headers:

```
F2 prompt addition: "Structure your output file (analysis-and-selection.md) with
three labeled sections: '## Comparative Analysis', '## Variant Scoring',
'## Base Selection'. If any section cannot be completed, note the failure
in that section header."
```

This preserves diagnostic traceability (a reader can identify which sub-operation failed by checking which section is missing or incomplete) without requiring three separate Task agent dispatches. Time cost: ~5 minutes of additional prompt specification. Effectiveness gain: partial recovery of diagnostic granularity.

**Modification 2: Use a structured failure_stage value that encodes sub-operation progress**

Instead of a single `failure_stage: comparative_analysis`, use a compound value:

```yaml
# If comparison succeeded but scoring failed:
failure_stage: "comparative_analysis:scoring_failed"

# If comparison failed:
failure_stage: "comparative_analysis:comparison_failed"

# If all sub-operations succeeded but selection failed:
failure_stage: "comparative_analysis:selection_failed"
```

This provides S05 with structured failure data for quality gate insertion without requiring step re-decomposition. Time cost: ~10 minutes of additional failure-handler specification. Addresses the extensibility concern directly.

**Modification 3: Add the Quality Advocate's "not a substitute" comment**

As noted in the T03 panel consensus, add a prominent comment in the fallback section:

```
> WARNING: This fallback is NOT a substitute for the full adversarial pipeline.
> It provides a structured degradation path, not equivalent functionality.
> Quality is substantially reduced. Prioritize fixing the primary path.
```

Time cost: ~2 minutes. Addresses the concern that engineers might mistake the simplified fallback for "good enough."

### Net Impact of Modifications

| Metric | Original Opt 3 | Modified Opt 3 | Delta |
|--------|----------------|----------------|-------|
| Time savings | 1.25 hrs | 1.0 hrs | -0.25 hrs (modifications cost ~15 min) |
| Effectiveness impact | 0.15 | 0.08 | -0.07 (diagnostic recovery + warning) |
| Net benefit | 1.0625 hrs | 0.92 hrs | -0.14 hrs |
| Diagnostic granularity | Lost | Partially recovered | Improvement |
| S05 extensibility | Reduced | Preserved via compound failure_stage | Improvement |

The modified optimization still delivers ~1.0 hour of net benefit (6.7% of sprint) while recovering most of the diagnostic and extensibility concerns raised by the AGAINST position.

---

*Debate conducted 2026-02-23. Format: structured adversarial with cross-examination.*
*Input: T03-optimizations.md (Optimization 3), sprint-spec.md, ranked-root-causes.md.*
*Recommendation: adopt-with-modifications (3 modifications specified, ~15 min additional cost, partial diagnostic recovery).*
