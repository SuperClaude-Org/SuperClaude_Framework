# Release Specification: sc:roadmap Invariant Reasoning Enhancements

**Version**: 1.0.0
**Date**: 2026-03-04
**Status**: APPROVED FOR IMPLEMENTATION
**Source**: Adversarial debate on proposals RM-1 through RM-5
**Affects**: `sc:roadmap` command definition, `sc:roadmap-protocol` SKILL.md, `refs/templates.md`, `refs/extraction-pipeline.md`, `refs/validation.md`

---

## 1. Executive Summary

This release adds structural invariant reasoning to the `/sc:roadmap` command. The roadmap protocol currently optimizes for feature coverage completeness but has no mechanism to analyze logical correctness of the designs it plans. Five proposals were debated and scored; all five scored A-Tier (65.0-79.5/100) and are included, phased across three implementation waves.

**What changes**:
- Risk Register gains mandatory category enforcement (STATE, XCOMP) -- RM-5
- Deliverable tables gain Negative Acceptance Criteria derived from boundary-probing transforms -- RM-2
- Roadmap body template gains a State Invariant Analysis section -- RM-1
- Extraction pipeline gains a Cross-Component State Flow Tracing step -- RM-3
- Wave 4 validation gains a third agent (Invariant Boundary Agent) that validates design correctness -- RM-4

**Why**: The v0.04 pipeline produced a roadmap that faithfully covered all spec requirements but missed two bugs rooted in state-machine boundary conditions. Both bugs were in areas where the roadmap had zero structural pressure to reason about edge cases: guard conditions that fail when counts are zero, and filter operations where output count diverges from input count. These are general bug classes, not one-off oversights.

**Expected impact**: The roadmap protocol will catch boundary-condition bugs, guard-completeness bugs, and cross-component feedback bugs during planning -- before implementation begins. Estimated 25-40% overhead increase across the full generation pipeline, offset by reduced post-implementation bug remediation.

---

## 2. Background & Motivation

### The Class of Bugs Missed

The roadmap protocol's risk identification, deliverable planning, and validation all operate on the same axis: **does the roadmap faithfully cover the specification's requirements?** None of them ask: **will the design described in the specification actually work at boundary conditions?**

This creates a systematic blind spot for three bug classes:

1. **Guard Condition Completeness**: A guard condition uses a variable (e.g., `offset > 0`) but the design never considers what happens when the variable legitimately holds the sentinel/default value (e.g., zero). The roadmap has no mechanism to enumerate guard conditions or probe their boundary values.

2. **Filter Divergence**: A pipeline stage filters items (e.g., some events produce widgets, others do not), but a downstream consumer assumes `output_count == input_count`. The roadmap tracks component dependencies at the milestone level but does not trace state variables across component boundaries.

3. **Cross-Component Feedback**: Two components share state through an interface, but the interface abstracts away feedback loops. Component A's output depends on Component B's filtering behavior, but the roadmap treats them as independent with clean boundaries.

### The v0.04 Case (Concrete Example)

In v0.04, the roadmap generated 8 risks (all environmental/API-level), 21 positive acceptance criteria (all happy-path assertions), and 5 milestones with dependency tracking at the milestone level. Two bugs shipped:

- **Bug 1**: A cursor variable (`_loaded_start_index`) advanced by the count of events loaded, but a downstream visualizer filtered some events out. The cursor advanced past events that were never rendered. The roadmap tracked the runner and visualizer as separate components with a clean interface -- it never traced the filtering feedback loop.

- **Bug 2**: A guard condition (`_replayed_event_offset > 0`) used `> 0` to detect "has replay occurred," but when condensation was the last event and `tail_events` was empty, the guard evaluated to `False` even though replay had occurred. The roadmap had no mechanism to ask "what if the count is zero?"

Both bugs would have been caught by any of the proposed improvements. The proposals are not designed for this specific case -- they address the general class of "logical correctness at boundaries."

---

## 3. Design Decisions

The following decisions are resolved based on adversarial debate outcomes and scoring.

### DD-1: All Five Proposals Are Included

**Decision**: Include all five RM proposals. None scored below B-Tier (the lowest, RM-4, scored 65.0 A-Tier).

**Rationale**: The proposals form a reinforcing chain: RM-5 (categories) forces consideration, RM-1 (invariant table) forces enumeration, RM-2 (negative ACs) forces failure-mode reasoning, RM-3 (state flow tracing) forces interaction analysis, RM-4 (boundary agent) validates the result. Each layer adds depth that the prior layer does not.

### DD-2: Phased Implementation, Not Big-Bang

**Decision**: Implement in three phases aligned with the final-recommendations phasing: Phase 1 (RM-5, RM-2 partial), Phase 2 (RM-1, RM-2 complete), Phase 3 (RM-3, RM-4).

**Rationale**: The debate identified cumulative overhead as the primary risk. Phasing allows measuring overhead per phase and setting a 40% ceiling before proceeding.

### DD-3: RM-4 (Invariant Boundary Agent) Depends on RM-1 and RM-3

**Decision**: RM-4 consumes structured data from RM-1's State Invariant Analysis table and RM-3's Component Interaction Analysis table. It does not independently re-enumerate state variables.

**Rationale**: The cross-cutting analysis identified redundancy risk if all proposals independently enumerate state variables. Later stages should consume and verify prior stages' artifacts.

### DD-4: NAC Transforms Are a Closed Set, Extensible by Convention

**Decision**: The initial NAC transform set (RM-2) contains 6 transforms. New transforms may be added as new bug classes are encountered, but the initial set is fixed.

**Rationale**: The debate noted that an open-ended transform set could produce unbounded NACs. The 6 transforms cover the three identified bug classes. Extension is by convention (add to the set when a new class is found, document the motivating bug).

### DD-5: Risk Register Requires 3-of-5 Categories, Not All 5

**Decision**: The risk register must populate at least 3 of 5 categories. Unpopulated categories require explicit "None identified" with justification.

**Rationale**: Requiring all 5 would produce formulaic entries for domains that genuinely have no relevant risks (e.g., a documentation-only roadmap has no PERF risks). 3-of-5 with justification forces consideration without forcing fabrication.

### DD-6: Wave 4 Weight Redistribution

**Decision**: When RM-4 is active, Wave 4 score aggregation becomes: quality-engineer (0.40) + self-review (0.30) + invariant-boundary (0.30). The invariant-boundary agent can independently trigger REVISE if any dimension scores below 50.

**Rationale**: The debate assigned 0.30 weight to the invariant-boundary agent because it catches a fundamentally different class of bugs. The independent REVISE trigger prevents high scores from other agents from masking design correctness failures.

---

## 4. Spec Items

### 4.1 RM-5: Risk Register Category Enforcement

**Priority**: Immediate (Phase 1)
**Score**: 72.5/100 (A-Tier)
**Complexity**: Trivial (template change only)
**Overhead**: +100-200 tokens per roadmap

#### Functional Requirements

**FR-RM5-1**: The roadmap.md Risk Register table SHALL include a `Category` column with values from the set {ENV, INT, STATE, PERF, XCOMP}.

**FR-RM5-2**: The Risk Register SHALL contain risks in at least 3 of the 5 defined categories.

**FR-RM5-3**: For each category not populated with a risk, the Risk Register SHALL include a row with the category, "None identified" as the Risk value, and a brief justification in the Mitigation column.

**FR-RM5-4**: The five categories SHALL be defined in the roadmap.md body template with descriptions:

| Category | Description |
|----------|-------------|
| ENV | External/Environmental: SDK changes, API deprecation, third-party dependencies |
| INT | API/Integration: interface compatibility, contract violations, version mismatches |
| STATE | State Management/Invariants: guard conditions, cursor/offset correctness, sentinel values, filter divergence |
| PERF | Performance/Resource: memory, CPU, latency, scaling |
| XCOMP | Cross-Component Interaction: feedback loops, assumption mismatches across boundaries |

#### Non-Functional Requirements

**NFR-RM5-1**: Category enforcement SHALL add no more than 200 tokens to the roadmap generation.

**NFR-RM5-2**: Category definitions SHALL be stable across versions (additive only, no removals).

#### Acceptance Criteria

**AC-RM5-1**: Given a roadmap with 8 environmental risks, When the Risk Register is generated, Then at least 2 additional categories beyond ENV must be populated or explicitly marked "None identified" with justification.

**AC-RM5-2**: Given a roadmap for a stateful system with guard conditions, When the Risk Register is generated, Then the STATE category contains at least one risk referencing a state variable or guard condition.

**AC-RM5-3**: Given a roadmap where the generator identifies no performance risks, When the PERF category is unpopulated, Then a row appears with "None identified" and a justification (e.g., "No performance-sensitive operations identified in spec").

#### Interface Contracts

**Change to `refs/templates.md`** -- Risk Register section of roadmap.md Body Template:

Add the category definitions table (FR-RM5-4) and the updated Risk Register table format:

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
```

**Change to `sc:roadmap-protocol` SKILL.md** -- Wave 3 Step 1 behavioral instructions:

Append to the required body sections list: "Risk Register with mandatory category enforcement per `refs/templates.md`: at least 3 of 5 categories (ENV, INT, STATE, PERF, XCOMP) must contain risks. Remaining categories must include 'None identified' with justification."

**Change to `refs/validation.md`** -- quality-engineer prompt, consistency check:

Add: "Risk Register covers at least 3 of 5 required categories (ENV, INT, STATE, PERF, XCOMP). Any uncovered category has explicit 'None identified' justification. STATE and XCOMP categories are populated when the roadmap contains stateful components or multi-component interactions."

---

### 4.2 RM-2: Negative Acceptance Criteria Generation Protocol

**Priority**: Immediate (Phase 1 partial), Next Cycle (Phase 2 complete)
**Score**: 79.5/100 (A-Tier, highest-scoring roadmap proposal)
**Complexity**: Medium (extraction pipeline integration)
**Overhead**: +150-450 tokens per deliverable with guard/filter/transition characteristics

#### Functional Requirements

**FR-RM2-1**: The protocol SHALL define a closed set of 6 boundary-probing transforms (the "NAC Transform Set"):

| Transform | Probe Question |
|-----------|---------------|
| ZERO_COUNT | "What happens when [counted entity] is zero?" |
| EMPTY_COLLECTION | "What happens when [collection] is empty?" |
| FILTER_DIVERGENCE | "What happens when [filter] removes all/some items, causing output count != input count?" |
| SENTINEL_COLLISION | "What happens when [variable] legitimately holds its default/sentinel value?" |
| BOUNDARY_EVENT | "What happens when the triggering event is the first/last in the sequence?" |
| CONCURRENT_MUTATION | "What happens when [state] is modified during [operation]?" |

**FR-RM2-2**: During Wave 3 generation, for each deliverable, the generator SHALL scan for: guard conditions (if/when checks on state variables), filter operations (functions that may produce fewer outputs than inputs), and state transitions (variable assignments that change state).

**FR-RM2-3**: For each detected pattern in a deliverable, the generator SHALL apply the relevant NAC transforms and produce 1-3 Negative Acceptance Criteria (NACs).

**FR-RM2-4**: The deliverable table in roadmap.md SHALL include a "Negative Acceptance Criteria" column.

**FR-RM2-5**: NACs SHALL be derived algorithmically from the transform set, not ad-hoc. Each NAC SHALL reference the transform that generated it (e.g., "NAC [ZERO_COUNT]: Guard fires even when tail is empty").

**FR-RM2-6**: The NAC Transform Set SHALL be defined in `refs/extraction-pipeline.md` and referenced from Wave 3 behavioral instructions.

#### Non-Functional Requirements

**NFR-RM2-1**: NAC generation SHALL add no more than 450 tokens per deliverable.

**NFR-RM2-2**: The transform set SHALL be extensible by adding new entries. Existing transforms SHALL NOT be modified or removed (additive contract).

**NFR-RM2-3**: Deliverables with no detected guard conditions, filter operations, or state transitions SHALL have "N/A -- no guards/filters/transitions detected" in the NAC column.

#### Acceptance Criteria

**AC-RM2-1**: Given a deliverable that introduces a guard condition `offset > 0`, When NAC transforms are applied, Then at least one NAC is generated using ZERO_COUNT: "When offset is zero, [expected behavior or failure mode]."

**AC-RM2-2**: Given a deliverable that includes a filter operation producing a subset of input items, When NAC transforms are applied, Then at least one NAC is generated using FILTER_DIVERGENCE: "When filter removes all/some items, [downstream consumer behavior]."

**AC-RM2-3**: Given a deliverable with no guard conditions, filters, or state transitions (e.g., a documentation deliverable), When the deliverable table is generated, Then the NAC column reads "N/A -- no guards/filters/transitions detected."

**AC-RM2-4**: Given the v0.04 spec as input, When a roadmap is generated with NAC enforcement, Then deliverable D2.3 (or equivalent offset-replacement deliverable) has a NAC for ZERO_COUNT addressing the empty-tail-events case, AND a deliverable involving the visualizer's filtering has a NAC for FILTER_DIVERGENCE addressing cursor advancement.

**AC-RM2-5**: Given all NACs in a generated roadmap, When each NAC is inspected, Then each references a transform name from the closed set (ZERO_COUNT, EMPTY_COLLECTION, FILTER_DIVERGENCE, SENTINEL_COLLISION, BOUNDARY_EVENT, CONCURRENT_MUTATION).

#### Interface Contracts

**Change to `refs/extraction-pipeline.md`** -- new section after the existing 8-step pipeline:

```markdown
## NAC Transform Set

Boundary-probing transforms for generating Negative Acceptance Criteria. Applied during
Wave 3 generation for each deliverable containing guard conditions, filter operations,
or state transitions.

| Transform ID | Trigger Pattern | Probe Question |
|-------------|----------------|---------------|
| ZERO_COUNT | Count-based guard (>, >=, ==) | "What happens when [counted entity] is zero?" |
| EMPTY_COLLECTION | Collection iteration or length check | "What happens when [collection] is empty?" |
| FILTER_DIVERGENCE | Function with fewer outputs than inputs | "What happens when [filter] removes all/some items, causing output count != input count?" |
| SENTINEL_COLLISION | Variable compared to default/sentinel | "What happens when [variable] legitimately holds its default/sentinel value?" |
| BOUNDARY_EVENT | Sequence-dependent operation (first/last) | "What happens when the triggering event is the first/last in the sequence?" |
| CONCURRENT_MUTATION | State modified during iteration/callback | "What happens when [state] is modified during [operation]?" |

**Application Protocol**:
1. For each deliverable, scan description and acceptance criteria for trigger patterns
2. Match trigger patterns to transform IDs
3. Apply matching transforms to generate 1-3 NACs per deliverable
4. Format NACs with transform ID prefix: "NAC [TRANSFORM_ID]: <specific failure scenario>"
5. Deliverables with no matching patterns: "N/A -- no guards/filters/transitions detected"
```

**Change to `refs/templates.md`** -- deliverable table format in roadmap.md Body Template:

```markdown
| ID | Description | Acceptance Criteria | Negative Acceptance Criteria |
|----|-------------|---------------------|------------------------------|
| D2.3 | Replace boolean with offset | AC: State tracks count | NAC [ZERO_COUNT]: Guard fires even when tail is empty |
```

**Change to `sc:roadmap-protocol` SKILL.md** -- Wave 3 Step 1 behavioral instructions:

Append: "For each deliverable: scan for guard conditions (if/when checks on state variables), filter operations (functions that may produce fewer outputs than inputs), and state transitions (variable assignments). For each detected pattern, apply the relevant NAC transforms from `refs/extraction-pipeline.md` 'NAC Transform Set' and add 1-3 negative acceptance criteria to the deliverable table. Reference the transform ID in each NAC."

**Change to `refs/validation.md`** -- quality-engineer prompt, completeness check:

Add: "Every deliverable with a guard condition, filter, or state transition has at least one NAC. NACs reference a transform from the NAC Transform Set. Deliverables without applicable patterns are marked 'N/A'."

---

### 4.3 RM-1: Mandatory State Invariant Analysis Section

**Priority**: Next Cycle (Phase 2)
**Score**: 76.5/100 (A-Tier)
**Complexity**: Low (template change + Wave 3/4 instruction update)
**Overhead**: +200-500 tokens per roadmap

#### Functional Requirements

**FR-RM1-1**: The roadmap.md body template SHALL include a mandatory "State Invariant Analysis" section, placed after the Risk Register and before the Decision Summary.

**FR-RM1-2**: The State Invariant Analysis section SHALL enumerate every state variable introduced or modified by the roadmap's milestones, in a table with columns: Variable, Component, Introduced In, Invariant, Guard Conditions, Boundary Values, Failure Mode.

**FR-RM1-3**: "State variable" is defined as any field, counter, offset, flag, or index that is introduced, modified, or consumed across deliverables.

**FR-RM1-4**: Boundary Values SHALL include at minimum: zero, empty, sentinel/default, and maximum where applicable.

**FR-RM1-5**: Failure Mode SHALL describe the concrete consequence of the invariant breaking (e.g., "cursor advances past unrendered events"), not generic descriptions (e.g., "undefined behavior").

**FR-RM1-6**: If the roadmap introduces no state variables, the section SHALL read "No state variables introduced by this roadmap" with a brief justification.

#### Non-Functional Requirements

**NFR-RM1-1**: The section SHALL add no more than 500 tokens to the roadmap.

**NFR-RM1-2**: The table format SHALL be stable across versions (columns may be added but not removed).

#### Acceptance Criteria

**AC-RM1-1**: Given a spec that introduces a counter variable `_replayed_event_offset` with a guard `> 0`, When the roadmap is generated, Then the State Invariant Analysis table contains a row with: Variable = `_replayed_event_offset`, Invariant = "positive when replay has occurred", Boundary Values includes "zero (when tail_events is empty)", Failure Mode describes the guard bypass consequence.

**AC-RM1-2**: Given a spec with two components sharing a cursor variable, When the roadmap is generated, Then the State Invariant Analysis table contains a row for the cursor with guard conditions from both components listed.

**AC-RM1-3**: Given a documentation-only spec with no state variables, When the roadmap is generated, Then the State Invariant Analysis section reads "No state variables introduced by this roadmap" with justification.

**AC-RM1-4**: Given a generated roadmap, When the State Invariant Analysis table is inspected, Then no Failure Mode cell contains only "undefined behavior", "error", or similarly generic descriptions.

#### Interface Contracts

**Change to `refs/templates.md`** -- roadmap.md Body Template, after Risk Register:

```markdown
## State Invariant Analysis

For each state variable introduced or modified by this roadmap's milestones:

| Variable | Component | Introduced In | Invariant | Guard Conditions | Boundary Values | Failure Mode |
|----------|-----------|---------------|-----------|-----------------|-----------------|--------------|
| <var_name> | <component> | M<N> D<N.N> | <what must be true> | <conditions that check this var> | <zero, empty, sentinel, max> | <concrete consequence if invariant breaks> |
```

**Change to `sc:roadmap-protocol` SKILL.md** -- Wave 3 Step 1 behavioral instructions:

Append to required body sections list: "State Invariant Analysis: enumerate all state variables from deliverables that introduce new fields, counters, offsets, or flags. For each, identify the invariant, guard conditions, boundary values (zero, empty, max, sentinel), and failure mode if the invariant is violated. Failure modes must be concrete, not generic."

**Change to `refs/validation.md`** -- quality-engineer prompt:

Add new validation dimension: "5. STATE INVARIANT COVERAGE (weight: 0.10 -- redistributed from existing weights): Every state variable in the deliverables has a corresponding entry in the State Invariant Analysis table. Every guard condition has at least one boundary value identified. Failure modes are concrete (not 'undefined behavior')."

Adjust existing weights: Completeness 0.30, Consistency 0.25, Traceability 0.20, Test Strategy 0.15, State Invariant Coverage 0.10.

---

### 4.4 RM-3: Cross-Component State Flow Tracing

**Priority**: Future (Phase 3)
**Score**: 68.5/100 (A-Tier)
**Complexity**: Medium (extraction pipeline + template change)
**Overhead**: +300-600 tokens per component pair

#### Functional Requirements

**FR-RM3-1**: The extraction pipeline SHALL include a Step 9 "Interaction Boundary Analysis" that executes after Step 8 (the existing final step).

**FR-RM3-2**: Step 9 SHALL, for each pair of components identified in Step 6 (domain classification), identify: shared state variables, producer-consumer relationships, and callback/return value dependencies.

**FR-RM3-3**: For each identified interaction, Step 9 SHALL trace the state variable from producer to consumer and back, documenting: (a) what the producer assumes about the consumer's behavior, (b) what the consumer assumes about the producer's output, (c) where these assumptions could diverge.

**FR-RM3-4**: The roadmap.md body template SHALL include a "Component Interaction Analysis" section, placed after the Dependency Graph.

**FR-RM3-5**: If the spec defines only one component or no inter-component state sharing, the section SHALL read "Single-component design -- no cross-component interactions identified."

**FR-RM3-6**: When a divergence risk is identified as non-trivial, a corresponding entry SHALL exist in the Risk Register under the XCOMP category.

#### Non-Functional Requirements

**NFR-RM3-1**: Overhead SHALL scale linearly with component pair count, at no more than 600 tokens per pair.

**NFR-RM3-2**: Step 9 SHALL execute only when the extraction identifies 2 or more distinct components. Single-component specs skip Step 9 entirely.

#### Acceptance Criteria

**AC-RM3-1**: Given a spec with a runner component (managing `_loaded_start_index`) and a visualizer component (filtering events via `_create_replay_widget()`), When the extraction pipeline runs Step 9, Then the Component Interaction Analysis table contains a row with: Producer = runner, Consumer = visualizer, Shared State = `_loaded_start_index`, Producer Assumption = "all loaded events are consumed", Consumer Assumption = "some events may produce no widget", Divergence Risk = "cursor advances past unrendered events."

**AC-RM3-2**: Given a spec with a non-trivial divergence risk in the Component Interaction Analysis, When the Risk Register is generated, Then the XCOMP category contains a risk referencing the identified divergence.

**AC-RM3-3**: Given a single-component spec, When the roadmap is generated, Then the Component Interaction Analysis section reads "Single-component design -- no cross-component interactions identified."

#### Interface Contracts

**Change to `refs/extraction-pipeline.md`** -- new Step 9:

```markdown
## Step 9: Interaction Boundary Analysis

**Trigger**: 2+ distinct components identified in Step 6.
**Skip condition**: Single-component specs.

For each pair of components identified in Step 6:
1. Identify shared state variables (fields read or written by both components)
2. Identify producer-consumer relationships (one component's output is another's input)
3. Identify callback/return value dependencies
4. For each identified interaction, trace the state variable from producer to consumer:
   a. What does the producer assume about the consumer's behavior?
   b. What does the consumer assume about the producer's output?
   c. Where could these assumptions diverge?
5. Record results in the Component Interaction Analysis table
6. For non-trivial divergence risks, create a corresponding XCOMP risk entry
```

**Change to `refs/templates.md`** -- roadmap.md Body Template, after Dependency Graph:

```markdown
## Component Interaction Analysis

| Producer | Consumer | Shared State | Producer Assumption | Consumer Assumption | Divergence Risk |
|----------|----------|-------------|---------------------|---------------------|-----------------|
```

**Change to `sc:roadmap-protocol` SKILL.md** -- Wave 1B behavioral instructions:

Append after step 3: "3b. If extraction identifies 2+ distinct components, execute Step 9 (Interaction Boundary Analysis) from `refs/extraction-pipeline.md`. Write results to extraction.md."

**Change to `refs/validation.md`** -- self-review agent, Question 3 (risk assessment):

Add: "Are cross-component state flow risks identified? For each component interaction in the Component Interaction Analysis, is there a corresponding risk in the Risk Register (XCOMP category) when the divergence risk is non-trivial?"

---

### 4.5 RM-4: Invariant Boundary Validation Agent

**Priority**: Future (Phase 3, after RM-1 and RM-3)
**Score**: 65.0/100 (A-Tier)
**Complexity**: High (new validation agent)
**Overhead**: +3,000-5,000 tokens per validation run

#### Functional Requirements

**FR-RM4-1**: Wave 4 SHALL include a third validation agent, the "invariant-boundary" agent, dispatched in parallel with quality-engineer and self-review agents.

**FR-RM4-2**: The invariant-boundary agent SHALL consume: the source spec, roadmap.md, extraction.md (including RM-1's State Invariant Analysis table and RM-3's Component Interaction Analysis table when present).

**FR-RM4-3**: The agent SHALL perform four analysis dimensions:

| Dimension | Weight | Analysis |
|-----------|--------|----------|
| Guard Condition Inventory | 0.35 | Enumerate all guards, identify variables, generate boundary inputs (zero, empty, max, default-equals-sentinel), trace through guard |
| Filter Divergence Analysis | 0.30 | Enumerate all filters, identify output consumers, check for output_count == input_count assumptions, generate all-removed and some-removed test cases |
| Boundary Event Analysis | 0.20 | Identify sequence-dependent operations, test boundary events with special properties (last event is condensation, first event is filtered, only one event) |
| Cross-Component Invariant Check | 0.15 | Verify producer postconditions match consumer preconditions, generate adversarial inputs at crossings |

**FR-RM4-4**: The agent SHALL output a structured JSON report with per-dimension scores, issues found, weighted aggregate score, and a recommendation of PASS, REVISE, or REJECT.

**FR-RM4-5**: If any dimension scores below 50, the agent SHALL recommend REVISE regardless of aggregate score.

**FR-RM4-6**: The agent prompt SHALL include guidance for distinguishing "not handled" from "intentionally out of scope" to reduce false positives.

**FR-RM4-7**: When the invariant-boundary agent is active, Wave 4 score aggregation SHALL use: quality-engineer (0.40) + self-review (0.30) + invariant-boundary (0.30).

**FR-RM4-8**: When the invariant-boundary agent is not active (e.g., RM-4 not yet implemented), Wave 4 SHALL continue using the existing 2-agent formula: quality-engineer (0.55) + self-review (0.45).

#### Non-Functional Requirements

**NFR-RM4-1**: The agent SHALL add no more than 5,000 tokens per validation run.

**NFR-RM4-2**: The agent SHALL complete within the same timeout constraints as existing Wave 4 agents.

**NFR-RM4-3**: The agent SHALL be dispatched in parallel with existing agents (no sequential dependency).

#### Acceptance Criteria

**AC-RM4-1**: Given a roadmap with a guard condition `offset > 0` and no boundary analysis for the zero case, When the invariant-boundary agent runs, Then the Guard Condition Inventory dimension reports a boundary issue for the zero case, AND the dimension score is below 100.

**AC-RM4-2**: Given a roadmap with a filter operation where a downstream consumer assumes output_count == input_count, When the invariant-boundary agent runs, Then the Filter Divergence Analysis dimension reports a divergence issue, AND the dimension score is below 100.

**AC-RM4-3**: Given a roadmap where the invariant-boundary agent's Guard Condition Inventory score is 40 (below 50), When the agent produces its recommendation, Then the recommendation is REVISE regardless of scores in other dimensions.

**AC-RM4-4**: Given a roadmap where all invariants are properly analyzed with boundary values covered, When the invariant-boundary agent runs, Then all dimension scores are above 80 and the recommendation is PASS.

**AC-RM4-5**: Given a roadmap with a guard condition that is intentionally out of scope (marked in the spec as deferred), When the invariant-boundary agent evaluates the guard, Then the agent notes it as "intentionally deferred" rather than raising a boundary issue.

#### Interface Contracts

**Change to `refs/validation.md`** -- new agent section:

```markdown
## Invariant-Boundary Agent Prompt

You are an invariant-boundary validation agent for sc:roadmap. Your task is to
stress-test the DESIGN described in the roadmap by generating boundary inputs
and tracing them through the proposed implementation.

INPUT FILES:
- Source spec: {spec_path}
- roadmap.md: {roadmap_path}
- extraction.md: {extraction_path}

Perform the following analysis:

### 1. GUARD CONDITION INVENTORY (weight: 0.35)
- List every guard condition mentioned in the roadmap deliverables
- For each guard, identify the variable(s) it depends on
- For each variable, identify: default value, expected range, sentinel values
- Generate boundary inputs: zero, empty, max, default-equals-sentinel
- Trace each boundary input through the guard: does it fire correctly?
- Note: if a guard is marked "intentionally deferred" in the spec, record as
  deferred rather than a boundary issue
- Score: (guards_with_boundary_analysis / total_guards) * correctness_rate

### 2. FILTER DIVERGENCE ANALYSIS (weight: 0.30)
- List every filter operation (any function that may produce fewer outputs than inputs)
- For each filter, identify what consumes the filter's output count
- Check: does any downstream consumer assume output_count == input_count?
- Generate test case: filter removes all items. What happens downstream?
- Generate test case: filter removes some items. Does the cursor/offset/index
  advance by input_count or output_count?
- Score: (filters_with_divergence_analysis / total_filters) * correctness_rate

### 3. BOUNDARY EVENT ANALYSIS (weight: 0.20)
- Identify sequence-dependent operations (first event, last event, Nth event)
- For each: what happens when the boundary event has special properties?
- Trace through the milestone deliverables
- Score: (sequences_with_boundary_analysis / total_sequences) * correctness_rate

### 4. CROSS-COMPONENT INVARIANT CHECK (weight: 0.15)
- Identify state variables that cross component boundaries
  (consume Component Interaction Analysis table from extraction.md if available)
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

REVISE OVERRIDE: If any single dimension scores below 50, recommend REVISE
regardless of weighted_score.
```

**Change to `refs/validation.md`** -- Score Aggregation section:

Add conditional formula:
```
If invariant-boundary agent active:
  final_score = (quality_engineer * 0.40) + (self_review * 0.30) + (invariant_boundary * 0.30)
Else:
  final_score = (quality_engineer * 0.55) + (self_review * 0.45)
```

**Change to `sc:roadmap-protocol` SKILL.md** -- Wave 4 behavioral instructions:

Add after step 2: "2b. Dispatch invariant-boundary agent using the prompt from `refs/validation.md` 'Invariant-Boundary Agent Prompt' section. Agent runs in parallel with quality-engineer and self-review agents."

Update step 3 to reference three agents: "Both [all three] agents run in parallel (independent read-only validators)."

Update step 4 aggregation formula reference: "Aggregate scores using the formula from `refs/validation.md` 'Score Aggregation' section (2-agent or 3-agent formula depending on agent availability)."

---

## 5. Integration Points

### 5.1 Integration with sc:spec-panel Improvements

The following cross-command synergies are identified from the cross-cutting analysis:

**SP-3 (Guard Boundary Table) feeds RM-1 (State Invariant Analysis)**: When `sc:spec-panel` produces a guard boundary table as part of its review output, the roadmap's State Invariant Analysis table (RM-1) SHOULD consume and verify the spec-panel's boundary table rather than re-deriving state variables from scratch. This is an optimization, not a dependency -- RM-1 functions independently if SP-3 output is unavailable.

**SP-2 (Adversarial Tester Persona) amplifies RM-2 (Negative ACs)**: The adversarial tester in spec-panel may identify failure modes that inform NAC generation. If the spec-panel's adversarial tester output is available in the extraction pipeline, it SHOULD be used as an additional input for NAC generation. This is additive, not required.

### 5.2 Integration with sc:adversarial Improvements

**AD-2 (Consensus Assumption Extraction) surfaces inputs for RM-1 and RM-2**: When sc:adversarial extracts shared assumptions during debate, these assumptions are prime candidates for state invariant analysis and negative acceptance criteria. If the adversarial debate produces an assumption inventory, RM-1 and RM-2 SHOULD use it as a seed for their analysis.

**AD-5 (Debate Topic Taxonomy) ensures state mechanics are debated**: AD-5's coverage guarantee for state mechanics means that any multi-roadmap generation will have debated state-machine behavior before the roadmap reaches Wave 3 generation. This provides additional confidence in the state invariant analysis.

### 5.3 Cross-Command Artifact Propagation Chain

The recommended propagation chain (from cross-cutting analysis):

```
SP-3 (Guard Boundary Table)
  -> AD-1 (Invariant Probe Round, consumes boundary table as probe targets)
    -> RM-1 (State Invariant Analysis, initialized from boundary table + probe findings)
      -> RM-4 (Invariant Boundary Agent, validates RM-1's entries)
```

**Implementation note**: This chain is aspirational for Phase 3. Phases 1 and 2 implement each proposal independently. Phase 3 should implement artifact propagation as a separate integration task after the individual proposals are validated.

---

## 6. Implementation Phasing

### Phase 1: Minimum Viable Improvement (Week 1)

**Goal**: Catch guard-condition-completeness and filter-divergence bugs with minimal disruption.

| Day | Task | Proposal | Effort | Files Changed |
|-----|------|----------|--------|---------------|
| 1 | Add category column and definitions to Risk Register template | RM-5 | 30 min | `refs/templates.md` |
| 1 | Add category enforcement instruction to Wave 3 | RM-5 | 15 min | SKILL.md (Wave 3) |
| 1 | Add category validation to quality-engineer prompt | RM-5 | 15 min | `refs/validation.md` |
| 2 | Define NAC Transform Set in extraction pipeline | RM-2 (partial) | 4 hours | `refs/extraction-pipeline.md` |
| 3 | Add NAC column to deliverable table template | RM-2 (partial) | 1 hour | `refs/templates.md` |
| 3 | Add NAC generation instruction to Wave 3 | RM-2 (partial) | 1 hour | SKILL.md (Wave 3) |
| 4 | Add NAC completeness check to quality-engineer | RM-2 (partial) | 1 hour | `refs/validation.md` |
| 5 | Integration test: run on v0.04 spec | -- | 4 hours | -- |

**Overhead added**: ~10-15% per roadmap generation.

**Exit criteria**: Roadmap generated from v0.04 spec includes STATE risks in the Risk Register and NACs on deliverables with guard conditions.

### Phase 2: Structural Reinforcement (Weeks 2-3)

**Goal**: Add the State Invariant Analysis table and complete NAC integration.

| Week | Task | Proposal | Effort | Files Changed |
|------|------|----------|--------|---------------|
| 2 | Add State Invariant Analysis section to template | RM-1 | 2 hours | `refs/templates.md` |
| 2 | Add invariant enumeration instruction to Wave 3 | RM-1 | 2 hours | SKILL.md (Wave 3) |
| 2 | Add State Invariant Coverage validation dimension | RM-1 | 2 hours | `refs/validation.md` |
| 2 | Redistribute quality-engineer weights (add 0.10 for invariant coverage) | RM-1 | 1 hour | `refs/validation.md` |
| 3 | Complete NAC integration: verify end-to-end transform application | RM-2 (complete) | 4 hours | `refs/extraction-pipeline.md`, SKILL.md |
| 3 | Validation: run on 2-3 diverse specs to verify artifact quality | -- | 4 hours | -- |

**Overhead added**: Additional ~10-15% (cumulative ~20-30%).

**Exit criteria**: Roadmap includes State Invariant Analysis table with concrete failure modes. NACs reference transform IDs. Quality-engineer validates invariant coverage.

### Phase 3: Deep Analysis (Weeks 4+, after Phase 2 validation)

**Goal**: Add cross-component tracing and design-level validation.

| Week | Task | Proposal | Effort | Files Changed |
|------|------|----------|--------|---------------|
| 4 | Add Step 9 to extraction pipeline | RM-3 | 4 hours | `refs/extraction-pipeline.md` |
| 4 | Add Component Interaction Analysis section to template | RM-3 | 2 hours | `refs/templates.md` |
| 4 | Add cross-component risk validation to self-review | RM-3 | 2 hours | `refs/validation.md` |
| 4 | Update Wave 1B instructions for Step 9 | RM-3 | 1 hour | SKILL.md (Wave 1B) |
| 5 | Implement invariant-boundary agent prompt | RM-4 | 4 hours | `refs/validation.md` |
| 5 | Update Wave 4 aggregation formula (3-agent) | RM-4 | 2 hours | `refs/validation.md` |
| 5 | Update Wave 4 behavioral instructions (3-agent dispatch) | RM-4 | 2 hours | SKILL.md (Wave 4) |
| 6 | Integration test: run on 3+ specs of varying complexity | -- | 8 hours | -- |

**Overhead added**: Additional ~10-15% (cumulative ~30-40%).

**Exit criteria**: Multi-component specs produce Component Interaction Analysis tables. Invariant-boundary agent catches boundary issues that quality-engineer and self-review miss. Total pipeline overhead stays below 40%.

---

## 7. Risks & Mitigations

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-RS-1 | Cumulative overhead exceeds 40% tolerance | Medium | High | Phase implementation; measure per phase; halt if ceiling reached before Phase 3 |
| R-RS-2 | Forcing functions produce formulaic, low-quality entries | Medium | Medium | Wave 4 quality-engineer validates entry quality; RM-1 requires "concrete" failure modes (not "undefined behavior"); periodic audit of artifact quality |
| R-RS-3 | Context window competition from additional sections | Low | Medium | All new sections use structured tables, not prose; summary propagation across stages |
| R-RS-4 | False positives from RM-4 invariant-boundary agent | Medium | Low | Agent prompt includes guidance for "intentionally deferred" vs "not handled"; REVISE (not REJECT) for boundary issues |
| R-RS-5 | NAC transform set is incomplete for future bug classes | Low | Medium | Transform set is explicitly extensible; new transforms added when new bug classes are encountered, documented with motivating case |
| R-RS-6 | Generator produces "None identified" for STATE/XCOMP categories on specs that clearly have state | Low | High | Quality-engineer prompt specifically checks that STATE and XCOMP are populated when the roadmap contains stateful components or multi-component interactions |
| R-RS-7 | RM-4 agent catches issues that are genuine design decisions, not bugs | Medium | Low | Agent prompt includes "intentionally out of scope" guidance; human review of REVISE recommendations before action |

---

## 8. NOT Doing

All five roadmap proposals scored A-Tier (65.0+) and are included in this release. No roadmap-specific proposals are excluded.

The following items are explicitly scoped out despite being related:

### Cross-Command Proposals (Not In Scope for This Release)

**SP-1 through SP-5**: Spec-panel improvements are covered by a separate release spec. They are referenced in Integration Points (Section 5) but not implemented by this release.

**AD-1 through AD-5**: Adversarial debate improvements are covered by a separate release spec. They are referenced in Integration Points (Section 5) but not implemented by this release.

### Aspirational Items Deferred

**Cross-command artifact propagation** (the SP-3 -> AD-1 -> RM-1 chain described in Section 5.3): Deferred until all three commands' individual improvements are validated. Artifact propagation requires stable artifact formats, which will be established during Phase 1-2 implementation.

**Automatic NAC transform extension**: The system does not auto-discover new transform types from encountered bugs. New transforms are added manually with documented rationale. Automatic discovery is a future consideration if the manual process proves burdensome.

**RM-4 agent as a standalone tool**: The invariant-boundary agent is designed as a Wave 4 sub-agent, not an independently invocable tool. Making it standalone (e.g., `/sc:boundary-check <roadmap.md>`) is a future consideration after the agent's effectiveness is validated.

---

*Release specification completed 2026-03-04. Document is self-contained and suitable for handoff to an implementing agent.*
