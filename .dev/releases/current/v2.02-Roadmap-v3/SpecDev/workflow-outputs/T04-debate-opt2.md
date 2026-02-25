# T04: Adversarial Debate -- Optimization 2

> **Subject**: Fold Minor T02 Amendments into Existing Task Acceptance Criteria
> **Date**: 2026-02-23
> **Debaters**: Advocate (FOR adoption), Skeptic (AGAINST adoption)
> **Input**: T03-optimizations.md (Optimization 2), sprint-spec.md, ranked-root-causes.md

---

## Optimization 2 Summary

**Proposal**: Integrate 9 minor T02 amendments (G1, G4-G11) directly into the acceptance criteria of their respective parent tasks, eliminating the separate amendment backlog as a standalone cross-reference artifact.

**Claimed savings**: 0.75 hours (5% of sprint)
**Claimed effectiveness impact**: 0.0

---

## FOR Position: Optimization 2 Should Be Adopted

### Argument 1: Separate Amendment Backlogs Are a Known Anti-Pattern for Single-Sprint Work

The sprint spec is a single-implementer, single-sprint document. Maintaining a separate amendment backlog forces the implementer into a two-pass workflow: (1) complete the task per its acceptance criteria, (2) consult a separate document to discover additional requirements that apply to the task just completed. This is the "supplementary reading" anti-pattern -- requirements that are physically separated from their point of use are systematically more likely to be missed.

The T03 panel's Implementation Specialist noted this from direct experience: "I have seen amendments get dropped because the implementer finished the task, checked its AC, and moved on without consulting the separate gap list." This is not hypothetical risk; it is an observed failure mode in sprint execution.

### Argument 2: Zero Functional Content Is Lost

Every amendment (G1, G4-G11) is preserved verbatim. The mapping table in T03-optimizations.md specifies exactly which parent task receives each amendment and what the integrated AC text says. For example:

- G1 (missing-file guard contradiction) becomes a correction to Task 2.2 step 3e AC: change "status: partial" to "status: failed, failure_stage: 'transport'"
- G10 (convergence threshold rationale) becomes an AC on Task 3.2: "0.6 threshold includes rationale comment"

No requirement is weakened, deferred, or dropped. The information content of the sprint spec is identical before and after this optimization. Only the organizational structure changes.

### Argument 3: This Optimization Actually Improves Effectiveness

The T03 panel rated effectiveness impact at 0.0, but a case can be made that it should be negative (i.e., an improvement). Inline requirements are encountered at the moment of implementation, when the implementer has the relevant context loaded. Cross-referenced requirements require a context switch: stop working on the task, open the amendment document, find the relevant amendment, map it back to the current task, return to implementation.

This is particularly relevant for amendments like G5 (convergence sentinel in fallback) and G8 (fallback quality threshold), which modify Task 1.4's fallback protocol -- the most complex single task in the sprint. An implementer writing the fallback protocol should encounter G5 and G8 inline, not as afterthoughts discovered in a separate document.

### Argument 4: The Time Savings Are Conservative and Well-Grounded

The 0.75-hour estimate breaks down as:
- 9 amendments x ~3 min cross-referencing = 27 min
- Amendment tracking overhead = 10 min
- Rework risk avoidance = 8 min

The cross-referencing overhead (27 min) is the most defensible component. Each amendment requires: read the amendment description, identify the parent task, navigate to the parent task spec, determine where in the AC the amendment fits, mentally integrate it, and return to the amendment list. At 3 minutes per amendment for 9 amendments, this is a realistic estimate for a conscientious implementer. A less conscientious one would skip the cross-referencing entirely -- which is exactly the failure mode this optimization prevents.

---

## AGAINST Position: Optimization 2 Is Risky or Undermines Effectiveness

### Argument 1: Amendment Backlogs Provide an Independent Audit Trail

The T02 synthesis produced the 11-gap list (G1-G11) as a structured analysis artifact. Each gap has a provenance: it was identified by a specific evaluation step, tied to a specific root cause or specification deficiency, and classified by severity (Critical vs. Important). When these amendments are folded into task ACs, this provenance is lost. The AC simply says "0.6 threshold includes rationale comment" -- it does not say why this AC exists, which evaluation step identified the need, or what happens if it is inadvertently removed in a future spec revision.

This matters for the follow-up sprint (S05). If S05 needs to audit which T02 gaps were addressed, the auditor must reverse-engineer the mapping from the T03 optimization table rather than consulting a standalone gap list. The optimization trades implementation convenience for auditability.

### Argument 2: Longer Acceptance Criteria Increase Cognitive Load Per Task

The sprint spec's most complex task is Task 2.2 (Wave 2 step 3 decomposition), which already has dense acceptance criteria covering 6 sub-steps (3a-3f), each with explicit tool-call syntax, fallback triggers, return contract routing, and a missing-file guard. Optimization 1 (merging Tasks 1.3 + 1.4 + 2.2) will further expand Task 2.2's scope by absorbing invocation wiring and fallback protocol requirements.

Adding G1, G4, and G9 to Task 2.2 (as proposed) creates a task with acceptance criteria spanning invocation wiring, specification decomposition, fallback protocol, return contract routing, tool-call specifics, convergence sentinel behavior, and debate-orchestrator bootstrap -- all in one task. There is a point where inline completeness becomes counterproductive: the implementer cannot hold all ACs in working memory simultaneously, and the risk shifts from "missed a cross-reference" to "missed a bullet point in a 25-item AC list."

### Argument 3: The 0.75-Hour Savings May Be Overstated

The 3-minute-per-amendment cross-referencing estimate assumes a naive implementer who reads each amendment cold and manually maps it to a task. In practice, an implementer who has read the sprint spec (which they must do before starting) will already have a mental model of the task structure. The cross-referencing overhead is closer to 1-1.5 minutes per amendment (scan amendment, recall parent task, confirm fit), yielding 9-14 minutes total. The "amendment tracking overhead" (10 min) and "rework risk avoidance" (8 min) are speculative -- they assume the implementer would otherwise forget to check the amendment list, which is a behavioral assumption, not a structural certainty.

A more realistic savings estimate is 0.3-0.4 hours, which is still positive but less compelling as a justification for restructuring the spec.

### Argument 4: The Optimization Creates a Dependency on Optimization 1

The amendment mapping table assigns G1, G4, and G9 to "Task 2.2." But Optimization 1 proposes merging Tasks 1.3 + 1.4 + 2.2 into a single task. If Optimization 1 is adopted, the merged task is the correct target. If Optimization 1 is rejected, G5, G7, and G8 (assigned to Task 1.4) and G1, G4, G9 (assigned to Task 2.2) target different tasks. The mapping table must be recalculated depending on Optimization 1's adoption status. This is a minor implementation detail, but it contradicts the T03 summary's claim that "Optimizations 1 and 2 are fully independent."

---

## CROSS-EXAMINATION

### FOR challenges AGAINST's strongest argument (Argument 1: Audit Trail)

**FOR**: The audit trail argument has theoretical merit but fails on practical grounds. Who is the auditor? The follow-up sprint (S05) is executed by the same team that implemented S04. They have access to T02-synthesis.md (which contains the full gap analysis with provenance) and T03-optimizations.md (which contains the exact mapping table). The audit trail is not destroyed -- it is preserved in the workflow artifacts. What is removed is the duplication of that trail in the sprint spec itself. The sprint spec is an implementation document, not an audit document. Requiring it to serve both purposes is scope creep.

Furthermore, if auditability is the concern, a one-line provenance note per integrated AC (e.g., "Per T02 G1:") would preserve the trail at zero additional overhead. This is a trivial modification to the optimization, not a reason to reject it.

**AGAINST responds**: The provenance note is a reasonable mitigation. However, the argument that "the team has access to T02-synthesis.md" assumes institutional memory. If the follow-up sprint is delayed or the implementer changes, the separate gap list provides self-contained context. Relying on cross-document provenance is the same anti-pattern the FOR position argues against -- except now applied to the audit trail rather than the requirements.

### AGAINST challenges FOR's strongest argument (Argument 3: Improved Effectiveness)

**AGAINST**: The "improved effectiveness" argument proves too much. By this logic, every cross-referenced requirement in every sprint spec should be inlined, producing a single monolithic document with no separation of concerns. The sprint spec already cross-references the root-cause analysis, the debate transcripts, and the DVL brainstorm. Should those be inlined too? The argument needs a limiting principle: when does inline completeness become counterproductive?

The answer is cognitive load. The 9 amendments are individually small (15-30 min fixes), but they span 5 different parent tasks. Inlining them does not create a single coherent narrative; it creates 5 slightly longer task specifications. The implementer still needs to track which tasks were amended and which were not. The cognitive load is redistributed, not eliminated.

**FOR responds**: The limiting principle is already provided by the optimization itself: only amendments that map to a single, identifiable parent task are inlined. The root-cause analysis, debate transcripts, and DVL brainstorm are reference documents that inform multiple tasks -- they cannot be inlined without duplication. Each T02 amendment maps to exactly one task, making it a natural candidate for integration. The distinction is 1:1 mapping (inline) vs. 1:N mapping (cross-reference). This is a sound structural principle, not an unbounded expansion of inlining.

---

## SCORING

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Time Savings** | 0.70 | The 0.75-hour estimate is directionally correct but likely overstated by 30-40%. Realistic savings are 0.4-0.55 hours. The cross-referencing overhead is real but less burdensome than claimed for an implementer who has already read the full spec. Score reflects genuine but moderate savings. |
| **Effectiveness Preservation** | 0.90 | No functional content is lost. The audit trail concern is valid but mitigable with provenance notes. Inline placement likely improves discoverability for the implementer. Slight risk of AC bloat on Task 2.2 prevents a perfect score. |
| **Feasibility** | 0.95 | The optimization is straightforward editorial work: move 9 bullet points from one section to another. The mapping table in T03 provides exact instructions. No technical risk, no tool dependencies, no coordination requirements. |
| **Risk (higher = lower risk)** | 0.85 | Primary risk is AC length inflation on Task 2.2 (the merged mega-task). Secondary risk is the implicit dependency on Optimization 1 for correct task targeting. Both are low-severity and easily mitigated. No risk of data loss, functional regression, or structural damage. |
| **Net Benefit** | 0.80 | Positive net benefit. The optimization is a sound organizational improvement that reduces the probability of missed requirements. It is not transformative (the savings are modest), but it makes the sprint spec a better implementation document with no meaningful downside when paired with provenance notes. |

---

## RECOMMENDATION

**Adopt with modifications.**

### Modifications

1. **Add provenance notes to each integrated AC.** Format: `[T02-G{N}]` prefix on each amendment-derived AC. Example: `"[T02-G1] step 3e: If return-contract.yaml not found, treat as status: failed, failure_stage: 'transport'"`. This preserves the audit trail at zero additional implementation cost and addresses the AGAINST position's strongest concern.

2. **Make the amendment-to-task mapping conditional on Optimization 1.** If Optimization 1 is adopted (Tasks 1.3 + 1.4 + 2.2 merged), amendments G1, G4, G5, G7, G8, and G9 all target the merged task. If Optimization 1 is rejected, the mapping table from T03 applies as-is (G5, G7, G8 to Task 1.4; G1, G4, G9 to Task 2.2). Document both mappings explicitly.

3. **Cap Task 2.2 AC length.** If the merged task (post-Optimization 1) exceeds 20 AC bullet points after amendment integration, organize the AC into labeled subsections (e.g., "Invocation ACs", "Fallback ACs", "Return Contract ACs", "Amendment ACs") to manage cognitive load. This addresses the AGAINST position's concern about AC bloat without reverting to a separate amendment document.

### Rationale

The core argument FOR adoption is sound: requirements belong at their point of use, not in a separate cross-reference document. The AGAINST position identified real concerns (audit trail loss, AC bloat, dependency on Optimization 1), but all three are addressable through low-cost modifications rather than outright rejection. The modified optimization preserves the time savings (~0.5 hours realistic) while eliminating the identified risks.

---

*Debate conducted 2026-02-23. Method: structured adversarial argumentation with cross-examination.*
*Input: T03-optimizations.md (Optimization 2), sprint-spec.md, ranked-root-causes.md.*
