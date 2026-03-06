# Brainstorm: Improving /sc:adversarial to Catch Implementation-Level Flaws

## Executive Summary

The adversarial debate protocol currently excels at resolving high-level architectural trade-offs but systematically misses implementation-level edge cases -- specifically state-machine boundary conditions, guard condition completeness, and filter interaction effects. This document proposes 5 structural improvements to the protocol that address the gap between "which approach is better?" (what the debate does well) and "does this approach actually work under all conditions?" (what the debate misses).

The core diagnosis is that the current protocol's debate rounds, convergence model, and scoring dimensions are all oriented around *comparative superiority between variants* rather than *absolute correctness of any variant*. The two bugs that escaped the pipeline are not cases where "the wrong variant won" -- they are cases where *all variants shared the same unexamined assumption*, and the adversarial structure had no mechanism to surface that.

---

## Analysis of the Six Questions

### Q1: Debate Depth Gaps

The current debate protocol (debate-protocol.md) structures rounds as: Round 1 (Advocate Statements), Round 2 (Rebuttals), Round 3 (Final Arguments). All three rounds focus on *comparative claims* -- "my variant handles X better than yours." This framing inherently biases agents toward topics where variants disagree, not toward topics where all variants share silent assumptions.

The two missed bugs exemplify this: no variant explicitly stated "every event produces a widget" or "tail is always non-empty" -- these were *implicit shared assumptions*. Since all variants agreed (implicitly), there was no diff point to debate. The diff-analysis step (Step 1) only surfaces *differences*, so shared blind spots are structurally invisible.

**Key insight**: The protocol needs a round that targets the *consensus itself* -- specifically the unstated assumptions that underlie agreement.

### Q2: Challenge Framework

The current steelman requirement asks advocates to "construct the strongest possible version of opposing positions before critiquing them." This is valuable for avoiding strawman dismissals, but it still operates within the adversarial frame of variant-vs-variant comparison. The challenge framework has no role whose job is to ask: "Regardless of which variant is better, does the *shared approach* actually handle these edge conditions?"

The bugs that escaped are precisely the kind a dedicated fault-finder would target:
- "What if the count of outputs differs from the count of inputs?" (Bug 1: filter divergence)
- "What if a guard variable legitimately equals its sentinel value?" (Bug 2: zero-is-valid)
- "What if the last item in a sequence has properties that differ from other items?" (Bug 2: boundary event)

These are not exotic -- they are from a well-known taxonomy of state-machine boundary conditions. A devil's advocate agent armed with this taxonomy would ask the questions systematically.

### Q3: Convergence Trap

The convergence metric is defined as "percentage of diff points where agents agree on superior approach." This means convergence can reach 0.85 when agents agree on *which variant handles each diff point better* -- but convergence says nothing about whether the agreed-upon approach is *correct*.

This is a structural problem: the convergence metric measures *inter-agent agreement*, not *solution quality*. High convergence can mask situations where agents converge on a flawed consensus. The two missed bugs occurred precisely because convergence was high -- agents agreed on the approach -- but the agreed-upon approach had unexamined edge cases.

**Key insight**: Convergence should have a minimum required breadth before it can be declared. Specifically, the set of diff points being converged upon must include implementation-level concerns, not just architectural ones.

### Q4: Agent Specialization

The current protocol assigns one advocate agent per variant. Agent specialization is by *position* (which variant you defend), not by *analytical function* (what class of issues you look for). This means the protocol has N advocates but zero auditors.

A dedicated "invariant-prober" role would operate orthogonally to the advocate structure. Rather than defending any variant, it would systematically probe all variants (and the emerging consensus) against a checklist of known failure patterns. This role is analogous to a QA engineer in a code review -- not competing with the developers, but checking their shared work against failure taxonomies.

### Q5: Merge Verification

Step 5 (Merge Execution) includes a "post-merge validation" with structural integrity check, internal reference validation, and contradiction re-scan. However, this validation is purely structural -- it checks that the merged document is internally consistent, not that the merged *design* handles edge cases.

After the merge is the most dangerous point for unexamined assumptions, because the merge can introduce new interactions between ideas from different variants. Bug 1 (filter divergence) is exactly this pattern: the runner's cursor logic (from one part of the design) interacted with the visualizer's filtering (from another part), and the interaction was never stress-tested.

### Q6: Scoring Dimensions

The current scoring has 5 quantitative metrics (RC, IC, SR, DC, SC) and 5 qualitative dimensions (Completeness, Correctness, Structure, Clarity, Risk Coverage). None of these dimensions explicitly measure *edge case coverage* or *invariant completeness*.

The Completeness dimension includes "Addresses edge cases and failure scenarios" as criterion 2, but this is one binary criterion out of 25 total -- worth only 2% of the qualitative score. A variant could score 24/25 while completely ignoring edge cases. Moreover, the criterion is assessed holistically ("does this document address edge cases?") rather than systematically ("for each state variable, are its boundary conditions enumerated?").

---

## Proposal 1: Mandatory Invariant Probe Round

### Description

Add a dedicated debate round between the current Round 2 (Rebuttals) and Round 3 (Final Arguments) called the "Invariant Probe Round." In this round, a fault-finder agent (not an advocate for any variant) systematically applies a boundary-condition checklist to the emerging consensus. The round produces a list of "unexamined assumptions" that must be explicitly addressed before convergence can be declared.

### Rationale

The two missed bugs are instances of well-known boundary-condition classes: filter divergence (output count != input count), zero-is-valid (guard variable equals sentinel), and boundary event (last item has special properties). These classes are enumerable and checklistable. The current protocol has no step that applies such a checklist. Adding one directly targets the structural gap.

The probe round operates on the *consensus* rather than on individual variants, which means it catches shared blind spots that the comparative debate structure inherently misses.

### Expected Impact

- **Direct coverage**: Catches the three specific bug classes (filter divergence, zero-is-valid, boundary event) that escaped the pipeline
- **Broader coverage**: The checklist is extensible -- new failure classes can be added as they are encountered, creating an organizational learning loop
- **Low overhead**: The probe round adds one additional agent invocation, not a full debate round. It produces a checklist output, not a discursive argument
- **No regression**: Existing debate rounds are unmodified; the probe round is additive

### Implementation Sketch

**Structural change to debate-protocol.md**:

```yaml
round_2_5_invariant_probe:
  condition: "--depth standard OR --depth deep"
  agent: "fault-finder (not an advocate for any variant)"
  input:
    - "All variants"
    - "debate-transcript.md (Rounds 1-2)"
    - "Emerging consensus points from convergence tracking"

  checklist_categories:
    state_variables:
      - "For each state variable identified in any variant, enumerate: initial value, valid range, update triggers, boundary values"
      - "For each boundary value: what happens when the variable equals it?"
      - "For each pair of state variables: are there interaction constraints?"

    guard_conditions:
      - "For each guard/sentinel check: what is the sentinel value?"
      - "Can the guarded variable legitimately equal the sentinel through normal operation?"
      - "What happens if the guard fires when it should not, or does not fire when it should?"

    count_divergence:
      - "For each pipeline stage that consumes N items and produces M items: is N always equal to M?"
      - "If N can differ from M: do downstream stages use N or M for their bookkeeping?"
      - "What happens when M is zero?"

    collection_boundaries:
      - "For each collection: what happens when it is empty?"
      - "For each iteration: what happens on the first item? The last item?"
      - "For each filter: what happens when the filter removes all items?"

    interaction_effects:
      - "For each pair of components that share state: trace all write-read paths"
      - "For each feedback loop: what happens when one component's output changes the other's assumptions?"

  output:
    - "invariant-probe.md: list of unexamined assumptions with severity ratings"
    - "Each assumption tagged: ADDRESSED (variant X, section Y) or UNADDRESSED"
    - "UNADDRESSED assumptions become mandatory discussion items for Round 3"

  convergence_gate:
    - "Convergence cannot be declared if any HIGH-severity assumptions are UNADDRESSED"
    - "MEDIUM-severity assumptions are logged as warnings in the merge output"
```

**Changes to convergence detection**:

```yaml
convergence_with_invariant_gate:
  original_metric: "agreed_points / total_diff_points >= threshold"
  additional_requirement: "high_severity_unaddressed_count == 0"
  combined: "convergence is met IFF original_metric AND additional_requirement"
```

---

## Proposal 2: Consensus Assumption Extraction Step

### Description

Add a sub-step to Step 1 (Diff Analysis) that explicitly extracts *shared assumptions* across all variants -- not just differences. For each topic where all variants agree (explicitly or implicitly), enumerate the unstated preconditions that the agreement depends on. These shared assumptions become first-class diff points that must be debated in Step 2, just like disagreements.

### Rationale

The current diff analysis (Step 1) has four phases: structural diff, content diff, contradiction detection, and unique contribution extraction. All four focus on *where variants differ*. None surface *where variants silently agree*. This creates a systematic blind spot: the more variants agree on an approach, the less scrutiny that approach receives.

The two missed bugs were in areas of strong agreement -- all variants assumed events produce widgets, all variants assumed tail is non-empty. Strong agreement should *increase* scrutiny on the underlying assumptions, not decrease it.

This is a well-known problem in group decision-making (groupthink), and the standard mitigation is to explicitly surface and challenge shared assumptions.

### Expected Impact

- **Structural fix**: Eliminates the "agreement = no scrutiny" bias that is built into the current diff-only analysis
- **Upstream benefit**: Shared assumptions surfaced in Step 1 feed into Step 2 debate as explicit diff points, so the entire downstream protocol benefits without modification
- **Compounding with Proposal 1**: The invariant probe (Proposal 1) operates on the consensus; shared assumption extraction gives it a richer input

### Implementation Sketch

**Addition to Step 1 (diff-analysis.md output)**:

```yaml
step_1_5_shared_assumption_extraction:
  purpose: "Identify implicit agreements and their unstated preconditions"

  process:
    phase_1_agreement_identification:
      - "For each topic covered by 2+ variants, check if all variants take the same approach"
      - "Agreement can be explicit (same stated approach) or implicit (topic not mentioned = default assumed)"
      - "Output: list of agreement points with coverage (all-explicit, partial-explicit, all-implicit)"

    phase_2_assumption_enumeration:
      - "For each agreement point, ask: what must be true for this approach to work?"
      - "Focus on: data shape assumptions, cardinality assumptions, ordering assumptions, timing assumptions"
      - "Output: list of preconditions per agreement point"

    phase_3_assumption_classification:
      - "STATED: precondition is explicitly documented in at least one variant"
      - "UNSTATED: precondition is not documented in any variant"
      - "CONTRADICTED: precondition is contradicted by evidence elsewhere in the variants"

    phase_4_promotion:
      - "All UNSTATED assumptions become synthetic diff points in the diff-analysis output"
      - "These synthetic diff points are tagged [SHARED-ASSUMPTION] so advocates know to address them"
      - "Advocates in Round 1 must explicitly state whether they accept or reject each shared assumption"

  output_section_in_diff_analysis:
    heading: "## Shared Assumptions"
    format: |
      ### [Agreement Point Title]
      **Agreement**: [What all variants agree on]
      **Stated preconditions**: [Preconditions explicitly documented]
      **Unstated preconditions**: [Preconditions not documented -- PROMOTED TO DIFF POINTS]
      **Risk if precondition fails**: [What breaks]
```

---

## Proposal 3: Edge Case Coverage as Mandatory Scoring Dimension

### Description

Add a sixth qualitative dimension to the scoring protocol called "Invariant & Edge Case Coverage" with 5 binary criteria. This dimension is weighted equally with the other 5 dimensions but has a **floor requirement**: a variant cannot be selected as the base if it scores 0/5 on this dimension, regardless of its overall score.

### Rationale

The current scoring protocol has "Addresses edge cases and failure scenarios" as one criterion under Completeness (criterion 2/5). This gives edge case coverage a weight of 1/25 = 4% of the qualitative score, or 2% of the overall score. A variant that completely ignores edge cases loses at most 2% -- an insignificant penalty.

By elevating edge case coverage to a full dimension with a floor requirement, the protocol structurally ensures that edge case analysis is performed and rewarded, regardless of how well a variant scores on other dimensions.

### Expected Impact

- **Scoring incentive**: Variants that enumerate edge cases and boundary conditions score significantly higher
- **Floor protection**: The floor requirement prevents a high-scoring but edge-case-ignorant variant from being selected
- **Measurable**: Each criterion is binary (met/not met) with CEV protocol, so the assessment is auditable

### Implementation Sketch

**Addition to scoring-protocol.md**:

```yaml
qualitative_dimension_6_invariant_coverage:
  name: "Invariant & Edge Case Coverage"
  weight: "Equal to other dimensions (1/6 of qualitative score)"
  floor_requirement: "Score >= 1/5 to be eligible as base variant"

  criteria:
    1:
      description: "Enumerates state variables with their valid ranges and boundary values"
      cev_guidance: "Look for explicit lists of state variables, their types, ranges, and edge values (zero, empty, max)"

    2:
      description: "Identifies guard conditions and documents their failure modes"
      cev_guidance: "Look for guard/sentinel patterns and analysis of what happens when guards fire incorrectly or fail to fire"

    3:
      description: "Analyzes filter/transform stages for count divergence"
      cev_guidance: "Look for pipeline stages where input count may differ from output count, with explicit handling of the divergence"

    4:
      description: "Documents empty-collection and single-element behaviors"
      cev_guidance: "Look for explicit handling of empty lists, zero-length sequences, and single-element edge cases"

    5:
      description: "Traces cross-component state interactions and feedback loops"
      cev_guidance: "Look for analysis of how shared state between components creates interaction effects"

  formula_update:
    old: "qual_score = total_criteria_met / 25"
    new: "qual_score = total_criteria_met / 30"
    note: "Total criteria increases from 25 to 30 with the new dimension"

  combined_formula_update:
    note: "No change to combined formula -- qual_score is still weighted 50%"
```

---

## Proposal 4: Post-Merge Interaction Stress Test

### Description

Add a Step 4.5 between Refactoring Plan (Step 4) and Merge Execution (Step 5) called the "Interaction Stress Test." This step takes the refactoring plan and, for each planned merge operation that combines logic from different variants, traces the interaction between the merged components to identify emergent failure modes that exist in neither source variant individually.

### Rationale

The merge step is uniquely dangerous because it combines ideas from different variants that were not designed to work together. Bug 1 (filter divergence) is a textbook case: the runner's cursor logic and the visualizer's filter logic each worked correctly in isolation, but their interaction produced a stall. The current post-merge validation (Step 5) checks structural integrity and internal contradictions, but does not trace cross-component interactions.

The stress test targets *emergent properties of the merge itself*, not properties of any individual variant. This is a fundamentally different analysis that cannot be performed earlier in the pipeline (before the merge plan exists).

### Expected Impact

- **Catches merge-emergent bugs**: Specifically targets the class of bugs that arise from combining independently-correct components
- **Targeted scope**: Only applies to merge operations that combine logic from different variants (additive merges like "append a new section" are excluded)
- **Risk-proportional**: Higher-risk merges (those marked "restructures" in the refactoring plan) receive deeper analysis

### Implementation Sketch

**New step in debate-protocol.md**:

```yaml
step_4_5_interaction_stress_test:
  purpose: "Identify emergent failure modes in the merged design"
  condition: "Refactoring plan contains at least one MEDIUM or HIGH risk merge operation"

  input:
    - "refactor-plan.md"
    - "Base variant"
    - "Non-base variants (source material for merges)"
    - "invariant-probe.md (if Proposal 1 is adopted)"

  process:
    phase_1_interaction_surface_identification:
      - "For each merge operation in the refactoring plan:"
      - "  Identify the components being combined"
      - "  Identify shared state, shared interfaces, and data flow between them"
      - "  Output: interaction surfaces (pairs of components that touch the same state or data)"

    phase_2_interaction_trace:
      - "For each interaction surface:"
      - "  Trace data flow: Component A writes X, Component B reads X"
      - "  Enumerate: what values can X take after A's write?"
      - "  For each value: does B's read handle it correctly?"
      - "  Special attention: boundary values, empty values, zero values"

    phase_3_emergent_failure_enumeration:
      - "For each interaction that can produce an unhandled value:"
      - "  Document: the write path, the value, the read path, the expected failure"
      - "  Classify: CRITICAL (data loss, infinite loop), HIGH (incorrect behavior), MEDIUM (degraded behavior)"

    phase_4_plan_amendment:
      - "For each CRITICAL or HIGH emergent failure:"
      - "  Add a mitigation step to the refactoring plan"
      - "  Mitigation may be: add a guard, add a range check, add a fallback, revise the merge approach"

  output:
    - "interaction-stress-test.md: enumerated interaction surfaces and failure modes"
    - "Amended refactor-plan.md (if failures found)"

  abort_condition:
    - "If CRITICAL failures cannot be mitigated: abort merge, document the incompatibility"
```

---

## Proposal 5: Debate Topic Taxonomy with Minimum Coverage Requirements

### Description

Introduce a mandatory topic taxonomy for the debate that requires coverage across three levels: Architecture (current strength), Interface Contracts (partially covered), and State Mechanics (currently missing). Convergence cannot be declared until each level has received at least one round of explicit debate. The taxonomy is checked as a structural prerequisite, independent of the convergence score.

### Rationale

The current debate structure is topic-agnostic -- agents debate whatever diff points emerge from Step 1. In practice, this means the debate gravitates toward high-level architectural questions (which are the most salient diff points) and neglects implementation-level mechanics (which tend to be shared assumptions, not diff points).

By requiring explicit coverage across a taxonomy of debate levels, the protocol ensures that agents cannot declare convergence without having addressed state mechanics, regardless of how quickly they agree on architecture. This is analogous to requiring branch coverage in testing -- you cannot declare a test suite complete just because line coverage is high.

### Expected Impact

- **Structural guarantee**: Implementation-level concerns cannot be skipped, regardless of how quickly architectural questions converge
- **Taxonomy is extensible**: New levels can be added as new failure classes are identified
- **Minimal overhead**: The taxonomy check is a structural gate, not an additional debate round. It may trigger additional rounds if coverage is insufficient, but adds no overhead when coverage is already adequate

### Implementation Sketch

**New section in debate-protocol.md**:

```yaml
debate_topic_taxonomy:
  purpose: "Ensure debate covers all levels of design, not just architectural trade-offs"

  levels:
    L1_architecture:
      description: "High-level structural decisions: patterns, component boundaries, technology choices"
      examples: "windowing vs virtualization, monolith vs microservice, SQL vs NoSQL"
      minimum_coverage: "At least 1 diff point debated at this level"
      current_status: "Well-covered by existing protocol"

    L2_interface_contracts:
      description: "Component interfaces, data formats, API contracts, type signatures"
      examples: "function signatures, event schemas, message formats, return types"
      minimum_coverage: "At least 1 diff point debated at this level"
      current_status: "Partially covered (depends on variant specificity)"

    L3_state_mechanics:
      description: "State variables, transitions, guards, invariants, boundary conditions"
      examples: "cursor advancement logic, offset tracking, guard conditions, filter effects on counts"
      minimum_coverage: "At least 1 diff point debated at this level"
      current_status: "NOT covered -- this is the gap that allowed both bugs to escape"

  coverage_check:
    timing: "After each debate round, before convergence check"
    process:
      - "Classify each debated diff point into one or more taxonomy levels"
      - "Check minimum coverage requirement for each level"
      - "If any level has zero coverage: convergence CANNOT be declared"
      - "If a level has zero coverage and max rounds are exhausted: force one additional round focused on the uncovered level"

    forced_round_behavior:
      - "Agents are given the specific uncovered taxonomy level as a debate focus"
      - "For L3 (state mechanics): agents must enumerate state variables, trace transitions, and identify boundary conditions"
      - "The forced round produces additional diff points that are scored normally"

  interaction_with_convergence:
    original: "convergence = agreed_points / total_diff_points >= threshold"
    updated: "convergence = (agreed_points / total_diff_points >= threshold) AND (all taxonomy levels have >= minimum coverage)"
```

**Integration with Step 1 (diff analysis)**:

```yaml
diff_point_classification:
  addition_to_step_1:
    - "Each diff point in diff-analysis.md is tagged with its taxonomy level(s)"
    - "Diff points can span multiple levels (e.g., an API design decision involves both L1 and L2)"
    - "If Step 1 produces zero L3 diff points: the shared assumption extraction (Proposal 2) is triggered with L3 focus"
```

---

## Cross-Proposal Interaction Analysis

The five proposals are designed to be complementary and independently valuable:

| Proposal | Independent Value | Synergy With |
|----------|------------------|--------------|
| P1: Invariant Probe Round | Catches boundary-condition bugs via checklist | P2 (richer input), P5 (ensures L3 coverage) |
| P2: Shared Assumption Extraction | Surfaces consensus blind spots as debate topics | P1 (provides assumptions to probe), P5 (generates L3 diff points) |
| P3: Edge Case Scoring Dimension | Creates scoring incentive for edge case coverage | P1 (probe findings inform scoring), P4 (stress test findings inform scoring) |
| P4: Post-Merge Interaction Stress Test | Catches merge-emergent interaction bugs | P1 (pre-merge invariants inform post-merge checks) |
| P5: Debate Topic Taxonomy | Structural guarantee against level-skipping | P2 (generates missing-level content), P1 (probe is L3-focused) |

**Recommended adoption order**: P5 (taxonomy gate -- cheapest, most structural) > P2 (shared assumptions -- enriches Step 1) > P1 (invariant probe -- adds dedicated agent) > P3 (scoring dimension -- requires rubric redesign) > P4 (stress test -- adds full new step).

**Minimum viable improvement**: Adopting only P5 (taxonomy) and P2 (shared assumptions) would have been sufficient to catch both bugs in the v0.04 pipeline, because:
- P2 would have surfaced "events always produce widgets" and "tail is always non-empty" as unstated assumptions
- P5 would have forced at least one debate round on state mechanics (L3), where those assumptions would have been challenged

---

## Appendix: Bug Classification Taxonomy

For reference, the boundary-condition classes that the proposals target:

| Class | Pattern | Example | Caught By |
|-------|---------|---------|-----------|
| Filter Divergence | Output count != input count after filtering | `mounted < events_consumed` stall | P1 (count_divergence checklist), P2 (shared assumption: 1:1 mapping) |
| Zero-is-Valid | Guard sentinel equals a legitimate value | `offset=0` means both "unset" and "empty tail" | P1 (guard_conditions checklist), P5 (L3 forced debate) |
| Boundary Event | Last/first item has special properties | Condensation as last event produces empty tail | P1 (collection_boundaries checklist), P4 (interaction trace) |
| Implicit Cardinality | Assumption about collection size never stated | "There will always be at least one widget" | P2 (shared assumption extraction) |
| Feedback Loop | Component A's output changes Component B's input to A | Visualizer filtering affects runner cursor | P4 (interaction stress test), P1 (interaction_effects checklist) |
