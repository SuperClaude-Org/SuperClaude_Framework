# Brainstorm: Improving /sc:roadmap to Surface Edge-Case Risks Earlier

## Executive Summary

The /sc:roadmap command currently generates milestone-based implementation plans with risk registers, dependency graphs, and validation waves. Analysis of the v0.04 pipeline failure reveals that the roadmap protocol has **no structural mechanism** for probing state-machine boundary conditions, guard condition completeness, or cross-component interaction effects. The risk register focuses on external/environmental risks (API compatibility, SDK evolution, scroll behavior) rather than **internal logical invariant risks** that arise from the spec's own design decisions.

This document proposes 5 improvements to the roadmap protocol that would increase the probability of catching bugs in the class of: state-machine edge cases, guard condition completeness, and filter interaction effects.

---

## Analysis of the 6 Questions

### Q1: Should the roadmap protocol require a mandatory "state invariant risk" category?

**Current state**: The risk register (refs/templates.md, roadmap.md body template) has columns for Risk, Probability, Impact, Mitigation, and Owner. Risk identification is free-form -- the generator identifies risks based on whatever it considers important. In v0.04, all 8 risks (R-001 through R-008) were environmental or API-level: scroll API limitations, SDK compatibility, event interleaving. None addressed internal state-machine invariants.

**Gap analysis**: The risk identification process has no prompting or checklist that forces the generator to consider:
- What assumptions does this design make about the relationship between input counts and output counts?
- What happens when a variable used as a guard can legitimately hold its sentinel/default value?
- Where do state variables flow across component boundaries, and what invariants must hold at each crossing?

**Conclusion**: Yes. The risk register needs a mandatory category that forces enumeration of state invariants and their potential violation modes. This is not cosmetic -- it changes the cognitive forcing function applied during generation.

### Q2: Should "edge case verification" be a mandatory milestone type?

**Current state**: The milestone generation algorithm (refs/templates.md) creates Foundation, Domain, Integration, and Validation milestones. Validation milestones check that acceptance criteria are met. There is no milestone type that specifically targets edge case exploration or boundary condition verification.

**Gap analysis**: In v0.04, M5 was titled "Edge Cases, Observability & Hardening" but its deliverables were drawn from explicit spec requirements (logging, action-observation pairing, CI checks). It did not generate any deliverables for edge cases that the spec *didn't explicitly mention*. The milestone was reactive (spec-driven) rather than proactive (invariant-driven).

**Conclusion**: Rather than a full milestone, the more effective intervention is to add mandatory verification deliverables within existing milestones. Each milestone that introduces a state variable or guard condition should include a deliverable that tests that variable's boundary values.

### Q3: Should the roadmap protocol require "negative acceptance criteria"?

**Current state**: Deliverables have acceptance criteria derived from the spec. These are overwhelmingly positive ("feature X works when Y"). The v0.04 roadmap had 21 success criteria, all positive assertions. None tested what happens when invariants break.

**Gap analysis**: The two bugs were both cases where a positive acceptance criterion passed but a negative one would have caught the issue:
- Bug 1: "AC-5: Page Up loads 200 more events" passes, but "cursor advances past filtered events" was never tested.
- Bug 2: "AC-12: all existing tests pass" passes, but "replay guard fires even when tail is empty" was never tested.

**Conclusion**: Yes. The protocol should generate negative/failure-mode acceptance criteria for any deliverable that introduces a guard condition, filter, or state transition. These should be generated algorithmically from the deliverable's positive criteria by asking "what if the count is zero?", "what if the filter removes all items?", "what if the sentinel value is legitimately reached?"

### Q4: Should the protocol require explicit "interaction boundary analysis"?

**Current state**: The extraction pipeline identifies domains and maps requirements to milestones. Cross-component dependencies are tracked at the milestone level (M3 depends on M2). But state flows between components within a milestone are not analyzed.

**Gap analysis**: Bug 1 occurred at the boundary between the runner (which manages `_loaded_start_index`) and the visualizer (which filters events via `_create_replay_widget()`). The spec correctly separated these components but did not trace how the visualizer's filtering feeds back into the runner's cursor advancement. The roadmap inherited this gap.

**Conclusion**: Yes. When the extraction identifies multiple components with shared state (e.g., runner and visualizer both touching event indices), the roadmap should include an explicit "interaction boundary" section that traces state variables across component boundaries and identifies invariant assumptions at each crossing.

### Q5: Should the validation wave include mandatory "invariant fuzzing"?

**Current state**: Wave 4 dispatches quality-engineer and self-review agents. The quality-engineer checks completeness, consistency, traceability, and test strategy. The self-review checks faithfulness, achievability, risk quality, and test actionability. Neither agent is prompted to generate edge inputs and trace them through the design.

**Gap analysis**: The validation agents validate the *document* (roadmap) against the *document* (spec). They do not validate the *design* against *boundary conditions*. This means the validation wave can score 100% on a roadmap that faithfully reproduces a spec with undetected invariant violations.

**Conclusion**: Yes, but carefully scoped. Adding a third validation agent specifically for invariant analysis would be the most effective intervention. This agent would enumerate guard conditions, state transitions, and filter operations in the roadmap, then generate boundary inputs (zero, empty, sentinel values) and trace them through the proposed design.

### Q6: Should roadmap templates include mandatory sections for guard condition inventory or state machine boundary analysis?

**Current state**: The roadmap.md body template requires: Overview, Milestone Summary, Dependency Graph, per-milestone details (Objective, Deliverables, Dependencies, Risk Assessment), Risk Register, Decision Summary, Success Criteria. None of these sections prompt for guard condition enumeration.

**Gap analysis**: The template structure determines what the generator produces. If there is no section for "Guard Condition Inventory" or "State Invariant Analysis," the generator will never produce one. The template is the strongest forcing function.

**Conclusion**: Yes. Adding a mandatory "State Invariant Analysis" section to the roadmap.md body template would force the generator to enumerate all state variables, their expected value ranges, guard conditions that depend on them, and failure modes when values are at boundaries.

---

## Proposals

### Proposal 1: Mandatory State Invariant Analysis Section in roadmap.md

**Description**: Add a required "State Invariant Analysis" section to the roadmap.md body template (refs/templates.md). This section must enumerate: (a) all state variables introduced or modified by the roadmap's milestones, (b) the invariants assumed about each variable, (c) guard conditions that depend on each variable, and (d) boundary values where invariants might break.

**Rationale**: The template is the strongest forcing function in the generation process. By requiring this section, the generator must reason about state invariants during Wave 3 (Generation), not as an afterthought. The v0.04 bugs both involved state variables (`_loaded_start_index`, `_replayed_event_offset`) whose boundary conditions were never analyzed because no template section prompted for it.

This addresses the root cause: the roadmap protocol optimizes for *completeness of feature coverage* but has zero structural pressure to analyze *correctness of state management*. Adding the section creates that pressure at the lowest-cost intervention point (template change, not algorithmic change).

**Expected Impact**:
- High probability of catching guard-condition-completeness bugs (Bug 2 class): the generator would be forced to list `_replayed_event_offset` as a state variable, note that `> 0` is used as a guard, and identify `len(tail_events) == 0` as a boundary value.
- Medium probability of catching filter-divergence bugs (Bug 1 class): the generator would list `_loaded_start_index` and note that its decrement assumes `mounted == events_consumed`, prompting boundary analysis.
- Low overhead: one additional section per roadmap, ~200-500 tokens.

**Implementation Sketch**:

1. Add to refs/templates.md under "roadmap.md Body Template", after "Risk Register" and before "Decision Summary":

```markdown
## State Invariant Analysis

For each state variable introduced or modified by this roadmap's milestones:

| Variable | Component | Introduced In | Invariant | Guard Conditions | Boundary Values | Failure Mode |
|----------|-----------|---------------|-----------|-----------------|-----------------|--------------|
| <var_name> | <component> | M<N> D<N.N> | <what must be true> | <conditions that check this var> | <zero, empty, sentinel, max> | <what happens if invariant breaks> |
```

2. Add to Wave 3 behavioral instructions (step 1), after the list of required body sections:
   - "State Invariant Analysis: enumerate all state variables from deliverables that introduce new fields, counters, offsets, or flags. For each, identify the invariant, guard conditions, boundary values (zero, empty, max, sentinel), and failure mode if the invariant is violated."

3. Add to Wave 4 quality-engineer prompt, as a new validation dimension:
   - "5. STATE INVARIANT COVERAGE (weight: 0.10 -- redistributed from existing weights): Every state variable in the deliverables has a corresponding entry in the State Invariant Analysis table. Every guard condition has at least one boundary value identified. Failure modes are non-trivial (not just 'undefined behavior')."
   - Adjust existing weights: Completeness 0.30, Consistency 0.25, Traceability 0.20, Test Strategy 0.15, State Invariant 0.10.

---

### Proposal 2: Negative Acceptance Criteria Generation Protocol

**Description**: Extend the deliverable acceptance criteria generation in Wave 1B/Wave 3 to require "negative acceptance criteria" (NAC) for any deliverable that introduces a guard condition, filter operation, or state transition. NACs are derived algorithmically from positive ACs by applying a set of boundary-probing transforms.

**Rationale**: The v0.04 roadmap had 21 positive acceptance criteria and zero negative ones. Both bugs would have been caught by simple negations:
- Bug 1 NAC: "When `_create_replay_widget()` returns None for some events, `_loaded_start_index` still advances past those events."
- Bug 2 NAC: "When condensation is the last event and `tail_events` is empty, the replay guard still prevents duplicate replay."

Positive ACs verify that the happy path works. NACs verify that failure modes are handled. The absence of NACs is a systematic blind spot, not a one-off oversight.

**Expected Impact**:
- High probability of catching zero-is-valid bugs (Bug 2 class): the transform "what if the count is zero?" applied to any deliverable involving a count-based guard would generate the relevant NAC.
- High probability of catching filter-divergence bugs (Bug 1 class): the transform "what if the filter removes some/all items?" applied to any deliverable involving a filter would generate the relevant NAC.
- Medium overhead: 1-3 NACs per deliverable with guard/filter/transition characteristics, ~50-150 tokens each.

**Implementation Sketch**:

1. Define a set of boundary-probing transforms in a new section of refs/extraction-pipeline.md:

```
NAC Transform Set:
- ZERO_COUNT: "What happens when [counted entity] is zero?"
- EMPTY_COLLECTION: "What happens when [collection] is empty?"
- FILTER_DIVERGENCE: "What happens when [filter] removes all/some items, causing output count != input count?"
- SENTINEL_COLLISION: "What happens when [variable] legitimately holds its default/sentinel value?"
- BOUNDARY_EVENT: "What happens when the triggering event is the first/last in the sequence?"
- CONCURRENT_MUTATION: "What happens when [state] is modified during [operation]?"
```

2. Add to Wave 3 behavioral instructions, in the deliverable generation step:
   - "For each deliverable: scan for guard conditions (if/when checks on state variables), filter operations (functions that may produce fewer outputs than inputs), and state transitions (variable assignments). For each detected pattern, apply the relevant NAC transforms and add 1-3 negative acceptance criteria to the deliverable table."

3. Add NAC column to the deliverable table template:

```markdown
| ID | Description | Acceptance Criteria | Negative Acceptance Criteria |
|----|-------------|---------------------|------------------------------|
| D2.3 | Replace boolean with offset | AC: State tracks count | NAC: Guard fires even when tail is empty (zero-is-valid) |
```

4. Add to Wave 4 quality-engineer completeness check:
   - "Every deliverable with a guard condition, filter, or state transition has at least one NAC. NACs are derived from the boundary-probing transform set, not ad-hoc."

---

### Proposal 3: Cross-Component State Flow Tracing

**Description**: Add a mandatory "Interaction Boundary Analysis" step to Wave 1B (Detection & Analysis) that traces state variables across component boundaries. When the extraction identifies multiple components that share state or have producer-consumer relationships, the roadmap must include an explicit analysis of how state flows between them, what invariants are assumed at each crossing, and where divergence can occur.

**Rationale**: The v0.04 spec correctly separated the runner (state management, slicing) from the visualizer (rendering, filtering). But the roadmap treated them as independent components with a clean interface. In reality, the visualizer's filtering behavior feeds back into the runner's cursor state through the `mounted` count. This feedback loop was invisible in the roadmap because no analysis traced state across the component boundary.

This is a general problem: specs define interfaces between components, but interfaces abstract away the feedback loops and side-channel dependencies that cause bugs. The roadmap should de-abstract these at the state variable level.

**Expected Impact**:
- High probability of catching cross-component feedback bugs (Bug 1 class): tracing `_loaded_start_index` across the runner-visualizer boundary would reveal that the visualizer's filtering affects the runner's cursor advancement.
- Medium probability of catching guard condition bugs that span components: if a guard in component A depends on output from component B, the trace would identify this dependency.
- Medium overhead: one analysis per pair of interacting components, ~300-600 tokens per pair.

**Implementation Sketch**:

1. Add to refs/extraction-pipeline.md, as step 9 (after the existing 8-step pipeline):
   - "Step 9: Interaction Boundary Analysis. For each pair of components identified in step 6 (domain classification), identify shared state variables, producer-consumer relationships, and callback/return value dependencies. For each identified interaction, trace the state variable from producer to consumer and back, noting: (a) what the producer assumes about the consumer's behavior, (b) what the consumer assumes about the producer's output, (c) where these assumptions could diverge."

2. Add to roadmap.md body template, after "Dependency Graph":

```markdown
## Component Interaction Analysis

| Producer | Consumer | Shared State | Producer Assumption | Consumer Assumption | Divergence Risk |
|----------|----------|-------------|---------------------|---------------------|-----------------|
| <component A> | <component B> | <variable/interface> | <what A assumes about B> | <what B assumes about A> | <how assumptions could conflict> |
```

3. Add to Wave 4 self-review agent, Question 3 (risk assessment):
   - "Are cross-component state flow risks identified? For each component interaction in the Component Interaction Analysis, is there a corresponding risk in the Risk Register when divergence risk is non-trivial?"

---

### Proposal 4: Invariant Boundary Validation Agent (Wave 4 Enhancement)

**Description**: Add a third validation agent to Wave 4 -- an "invariant-boundary" agent -- that specifically generates edge inputs (empty collections, zero counts, sentinel values, boundary events) and traces them through the proposed design as described in the roadmap milestones. This agent does not validate the document; it validates the design's logical soundness.

**Rationale**: The existing Wave 4 agents (quality-engineer and self-review) validate the roadmap *as a document*: completeness, consistency, traceability, faithfulness. They do not validate the *design described by the roadmap* for logical correctness. This means a roadmap can score 100% validation while faithfully describing a design with invariant violations.

The v0.04 validation was skipped (`--no-validate`), but even if it had run, neither agent would have caught the bugs because neither agent is prompted to reason about boundary conditions in the design itself.

This is the highest-impact change because it adds a fundamentally different validation dimension: not "does the roadmap match the spec?" but "does the design in the roadmap handle edge cases?"

**Expected Impact**:
- High probability of catching all three bug classes (state-machine edge cases, guard condition completeness, filter interaction effects): the agent's explicit purpose is to generate boundary inputs and trace them through the design.
- Higher cost than other proposals: adds a third parallel validation agent, ~3-5K additional tokens per validation run.
- May produce false positives for designs where edge cases are intentionally deferred. The agent prompt should include guidance for distinguishing "not handled" from "intentionally out of scope."

**Implementation Sketch**:

1. Add to refs/validation.md, a new agent section:

```
## Invariant-Boundary Agent Prompt

You are an invariant-boundary validation agent for sc:roadmap. Your task is to
stress-test the DESIGN described in the roadmap by generating boundary inputs
and tracing them through the proposed implementation.

INPUT FILES:
- Source spec: {spec_path}
- roadmap.md: {roadmap_path}
- extraction.md: {extraction_path}

Perform the following analysis:

## 1. GUARD CONDITION INVENTORY (weight: 0.35)
- List every guard condition mentioned in the roadmap deliverables
  (if/when checks, boolean flags, threshold comparisons, offset checks)
- For each guard, identify the variable(s) it depends on
- For each variable, identify: default value, expected range, sentinel values
- Generate boundary inputs: zero, empty, max, default-equals-sentinel
- Trace each boundary input through the guard: does it fire correctly?
- Score: (guards_with_boundary_analysis / total_guards) * correctness_rate

## 2. FILTER DIVERGENCE ANALYSIS (weight: 0.30)
- List every filter operation (any function that may produce fewer outputs
  than inputs, including: event filtering, widget creation, validation checks)
- For each filter, identify what consumes the filter's output count
- Check: does any downstream consumer assume output_count == input_count?
- Generate test case: filter removes all items. What happens downstream?
- Generate test case: filter removes some items. Does the cursor/offset/index
  advance by input_count or output_count?
- Score: (filters_with_divergence_analysis / total_filters) * correctness_rate

## 3. BOUNDARY EVENT ANALYSIS (weight: 0.20)
- Identify sequence-dependent operations (first event, last event, Nth event)
- For each: what happens when the boundary event has special properties?
  (e.g., last event is condensation, first event is filtered, only one event)
- Trace through the milestone deliverables
- Score: (sequences_with_boundary_analysis / total_sequences) * correctness_rate

## 4. CROSS-COMPONENT INVARIANT CHECK (weight: 0.15)
- Identify state variables that cross component boundaries
- For each: does the producer's postcondition match the consumer's precondition?
- Generate adversarial input: producer outputs edge value. Does consumer handle it?
- Score: (crossings_with_invariant_check / total_crossings) * correctness_rate

OUTPUT FORMAT:
{
  "guard_conditions": {"score": <0-100>, "guards_found": <N>,
    "boundary_issues": [{"guard": "...", "input": "...", "failure": "..."}]},
  "filter_divergence": {"score": <0-100>, "filters_found": <N>,
    "divergence_issues": [{"filter": "...", "assumption": "...", "failure": "..."}]},
  "boundary_events": {"score": <0-100>, "sequences_found": <N>,
    "boundary_issues": [{"sequence": "...", "event": "...", "failure": "..."}]},
  "cross_component": {"score": <0-100>, "crossings_found": <N>,
    "invariant_issues": [{"crossing": "...", "mismatch": "..."}]},
  "weighted_score": <computed>,
  "recommendation": "<PASS|REVISE|REJECT>",
  "critical_findings": [<findings that should block implementation>]
}
```

2. Update Wave 4 score aggregation formula:
   - `final_score = (quality_engineer * 0.40) + (self_review * 0.30) + (invariant_boundary * 0.30)`
   - The invariant-boundary agent receives significant weight (0.30) because it catches a fundamentally different class of bugs.

3. Update Wave 4 behavioral instructions:
   - "Dispatch invariant-boundary agent in parallel with quality-engineer and self-review agents."
   - "If invariant-boundary agent finds any issues with score < 50 in any dimension, flag as REVISE regardless of overall score."

---

### Proposal 5: Risk Register Category Enforcement

**Description**: Mandate that the Risk Register in roadmap.md must include risks in at least 3 of 5 defined categories: (1) External/Environmental, (2) API/Integration, (3) State Management/Invariants, (4) Performance/Resource, (5) Cross-Component Interaction. The generator must either populate each category or explicitly state "No risks identified in this category" with justification.

**Rationale**: The v0.04 Risk Register contained 8 risks, all in categories 1, 2, and 4. Categories 3 and 5 were completely absent. This is not because there were no risks in those categories -- the bugs proved there were -- but because the generator's risk identification is unconstrained and naturally gravitates toward visible, environmental risks rather than subtle, logical risks.

Mandatory categories act as a checklist. Checklists are proven to reduce omission errors in complex processes (Gawande, "The Checklist Manifesto"). The key insight is that the generator needs to be *forced* to think about each risk category, even if it concludes there are no risks in that category. The act of considering and dismissing is itself valuable.

**Expected Impact**:
- Medium-high probability of catching state management risks (Bug 2 class): the "State Management/Invariants" category would force the generator to consider whether any state variables have boundary conditions.
- Medium probability of catching cross-component risks (Bug 1 class): the "Cross-Component Interaction" category would force consideration of feedback loops between components.
- Very low overhead: adds a category column to the existing Risk Register table and requires explicit coverage of each category. ~100-200 additional tokens.

**Implementation Sketch**:

1. Add to refs/templates.md, in the Risk Register section of the roadmap.md body template:

```markdown
## Risk Register

**Required categories** (at least 3 of 5 must contain risks; remaining must include "None identified" with justification):

| Category | Description |
|----------|-------------|
| ENV | External/Environmental: SDK changes, API deprecation, third-party dependencies |
| INT | API/Integration: interface compatibility, contract violations, version mismatches |
| STATE | State Management/Invariants: guard conditions, cursor/offset correctness, sentinel values, filter divergence |
| PERF | Performance/Resource: memory, CPU, latency, scaling |
| XCOMP | Cross-Component Interaction: feedback loops, assumption mismatches across boundaries |

| ID | Category | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|----------|------|---------------------|-------------|--------|------------|-------|
| R-001 | ENV | <risk> | M1, M3 | Medium | High | <mitigation> | <persona> |
| R-002 | STATE | <risk> | M2 | Low | Medium | <mitigation> | <persona> |
```

2. Add to Wave 3 behavioral instructions:
   - "When generating the Risk Register, ensure at least 3 of the 5 required categories (ENV, INT, STATE, PERF, XCOMP) contain at least one risk. For categories with no identified risks, include a row with 'None identified' and a brief justification (e.g., 'No state variables with non-trivial guard conditions identified')."

3. Add to Wave 4 quality-engineer consistency check:
   - "Risk Register covers at least 3 of 5 required categories. Any uncovered category has explicit 'None identified' justification."

---

## Proposal Comparison Matrix

| Proposal | Bug 1 (Filter Divergence) | Bug 2 (Guard Bypass) | Cost (tokens) | Implementation Difficulty | Synergy |
|----------|--------------------------|---------------------|---------------|--------------------------|---------|
| P1: State Invariant Section | Medium | High | +200-500 | Low (template change) | Feeds P4 |
| P2: Negative ACs | High | High | +150-450/deliverable | Medium (extraction change) | Independent |
| P3: Interaction Boundary | High | Medium | +300-600/pair | Medium (extraction change) | Feeds P4 |
| P4: Invariant Boundary Agent | High | High | +3-5K/validation | High (new agent) | Consumes P1, P3 |
| P5: Risk Categories | Medium | Medium-High | +100-200 | Low (template change) | Independent |

## Recommended Implementation Order

1. **P5 (Risk Categories)** -- Lowest cost, immediate value, no dependencies. Can be implemented as a template change in refs/templates.md in minutes.
2. **P1 (State Invariant Section)** -- Low cost, high value for guard-condition bugs. Template change plus Wave 3 instruction update.
3. **P2 (Negative ACs)** -- Medium cost, highest coverage across bug classes. Requires extraction pipeline changes and transform set definition.
4. **P3 (Interaction Boundary)** -- Medium cost, specifically targets cross-component bugs. Extraction pipeline and template changes.
5. **P4 (Invariant Boundary Agent)** -- Highest cost, highest impact. Should be implemented after P1 and P3 are in place so the agent has structured data to work with.

## Key Insight

All five proposals share a common principle: **the roadmap protocol currently optimizes for feature coverage but has no structural mechanism for logical correctness analysis**. The template, extraction pipeline, and validation agents all ask "did we capture everything from the spec?" but none ask "will the design described in the spec actually work at boundary conditions?" The proposals progressively add this missing dimension: P5 through categorization, P1 through enumeration, P2 through negation, P3 through interaction tracing, and P4 through adversarial boundary testing.
