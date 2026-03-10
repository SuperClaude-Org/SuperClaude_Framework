# Release Specification: /sc:adversarial Protocol Improvements

**Version**: v0.05-adversarial
**Date**: 2026-03-04
**Status**: Draft
**Source**: Adversarial debate scoring of 5 proposals (AD-1 through AD-5), cross-cutting analysis, final recommendations

---

## 1. Executive Summary

This release introduces four structural improvements to the `/sc:adversarial` debate protocol that address a fundamental blind spot: the protocol excels at resolving disagreements between variants but systematically ignores areas of agreement, which is precisely where shared assumptions -- and shared bugs -- hide.

The centerpiece is **Consensus Assumption Extraction** (AD-2, S-Tier, 82.5/100), a new sub-step in the diff analysis phase that explicitly surfaces unstated preconditions underlying variant agreement. Three additional A-Tier improvements reinforce this: a **Debate Topic Taxonomy** (AD-5, 77.5) that structurally guarantees state-mechanics-level debate cannot be skipped, an **Invariant Probe Round** (AD-1, 72.5) that applies a boundary-condition checklist to the emerging consensus, and an **Edge Case Coverage Scoring Dimension** (AD-3, 67.5) that creates scoring incentives for invariant reasoning.

Two B-Tier proposals (AD-4: Post-Merge Interaction Stress Test, 57.5) are deferred.

**Expected outcomes**:
- Elimination of the "agreement = no scrutiny" structural bias in diff-based analysis
- Structural guarantee that state-mechanics concerns cannot be bypassed during debate
- Extensible checklist infrastructure that accumulates organizational learning
- Estimated 15-25% additional overhead per invocation (within the 40% ceiling)

---

## 2. Background & Motivation

### 2.1 The Problem Class

The adversarial debate protocol is designed to resolve the question "which variant's approach is better?" through structured argument. It does this well. However, it has no mechanism to address the question "does the agreed-upon approach actually work under all conditions?"

The structural root cause is that the protocol's entire analytical pipeline -- diff analysis, debate rounds, convergence detection, scoring -- operates on *differences* between variants. When all variants share an assumption (explicitly or implicitly), that assumption receives zero scrutiny regardless of how critical it is. The more variants agree, the less scrutiny the agreed-upon approach receives. This is the opposite of what correctness demands.

### 2.2 Bug Taxonomy

The class of bugs that escape this blind spot share common characteristics:

| Class | Pattern | Example |
|-------|---------|---------|
| Filter Divergence | Output count differs from input count after a filtering stage | A pipeline where `mounted < events_consumed` causes a stall |
| Zero-is-Valid | A guard sentinel value equals a legitimate runtime value | `offset=0` meaning both "unset" and "empty sequence" |
| Boundary Event | First or last item in a sequence has properties that differ from the general case | A condensation event as the final event produces an empty tail |
| Implicit Cardinality | An assumption about collection size is never stated | "There will always be at least one widget" |
| Feedback Loop | Component A's output changes Component B's input back to A | A visualizer's filtering affects a runner's cursor, which feeds back to the visualizer |

These are well-known boundary-condition classes from state-machine analysis. They are enumerable, checklistable, and detectable -- but only if the protocol has a step that looks for them.

### 2.3 Why the Current Protocol Misses Them

Three structural factors combine to create the blind spot:

1. **Diff-only analysis (Step 1)**: The diff analysis has four phases (structural diff, content diff, contradiction detection, unique contribution extraction). All four surface *where variants differ*. None surface *where variants silently agree*.

2. **Comparative debate (Step 2)**: All three debate rounds focus on *comparative claims* ("my variant handles X better than yours"). Topics where variants agree produce no diff points, so there is nothing to debate.

3. **Agreement-as-convergence (convergence detection)**: The convergence metric measures `agreed_points / total_diff_points`. High convergence can mask situations where agents converge on a flawed consensus, because the agreed-upon approach's correctness is never evaluated.

### 2.4 Concrete Motivation

During v0.04 development, two bugs escaped the full pipeline (spec-panel, adversarial debate, roadmap generation). Both bugs lived in areas of implicit agreement across all variants. Neither was a case where "the wrong variant won" -- both were cases where all variants shared the same unexamined assumption. The adversarial structure had no mechanism to surface this.

---

## 3. Design Decisions

The following design decisions were resolved through adversarial debate scoring and cross-cutting analysis.

### DD-1: Where to inject shared assumption analysis

**Decision**: Add as a sub-step within existing Step 1 (Diff Analysis), not as a separate new step.

**Rationale**: Shared assumptions surfaced in Step 1 become first-class diff points that feed into the existing Step 2 debate without requiring modifications to the debate round structure. This maximizes downstream benefit with minimal structural change. The scoring confirmed this: AD-2's low complexity score (3/10) reflects that it integrates into existing infrastructure.

### DD-2: Mandatory vs. optional taxonomy coverage

**Decision**: Taxonomy coverage is mandatory. Convergence cannot be declared until each taxonomy level has received at least one round of explicit debate.

**Rationale**: The debate's tendency to gravitate toward architectural questions is not a user preference -- it is a structural bias. Making the taxonomy optional would leave the bias intact for the cases where it matters most (time-pressured debates). The scoring confirmed: AD-5's high generalizability (8/10) supports universal application.

### DD-3: Invariant probe as dedicated round vs. integrated into existing rounds

**Decision**: Add as a dedicated Round 2.5 between Rebuttals (Round 2) and Final Arguments (Round 3), executed by a non-advocate fault-finder agent.

**Rationale**: The fault-finder role is fundamentally different from the advocate role. Advocates argue for their variant's strengths; the fault-finder probes the consensus for weaknesses. Mixing these roles in the same agent dilutes both. The probe operates on the consensus, which only exists after Round 2, so it cannot run earlier.

### DD-4: Edge case scoring as incentive vs. gate

**Decision**: Implement as a scoring incentive with a floor requirement, not as a hard gate.

**Rationale**: The floor requirement (score >= 1/5 to be eligible as base) prevents the worst case (a variant that completely ignores edge cases being selected). But the primary mechanism is incentive: variants that enumerate edge cases score higher. This avoids the risk of formulaic "check-the-box" analysis that a hard gate would encourage. The debate scored AD-3 lower on impact (5/10) precisely because it is an indirect mechanism -- the floor requirement addresses the concern without over-weighting it.

### DD-5: Convergence gate interaction

**Decision**: Convergence requires both the original metric (agreed_points / total_diff_points >= threshold) AND the invariant probe gate (zero HIGH-severity unaddressed assumptions) AND taxonomy coverage (all levels have minimum coverage).

**Rationale**: These three conditions are orthogonal. The original metric measures inter-agent agreement breadth. The invariant gate measures assumption completeness. The taxonomy gate measures debate depth across levels. All three must be satisfied for convergence to be meaningful.

### DD-6: Interaction with cross-command improvements

**Decision**: AD-2's shared assumption output and AD-1's invariant probe output are designed as structured artifacts that can be consumed by downstream commands (specifically sc:roadmap's RM-1 State Invariant Analysis Section), but this release does not mandate the cross-command integration.

**Rationale**: Cross-command artifact propagation (the SP-3 -> AD-1 -> RM-1 chain identified in the cross-cutting analysis) is a high-value opportunity, but it depends on the roadmap release spec being implemented first. This release defines the artifact formats; the integration is a separate work item.

---

## 4. Spec Items

### 4.1 AD-2: Consensus Assumption Extraction Step

**Priority**: S-Tier (82.5/100) -- Immediate implementation
**Composite breakdown**: Complexity 3/10, Overhead 3/10, Impact 8/10, Generalizability 9/10

#### Functional Requirements

**FR-AD2-1**: The diff analysis engine (Step 1) SHALL include a new phase called "Shared Assumption Extraction" that executes after the existing four phases (structural diff, content diff, contradiction detection, unique contribution extraction) and before the diff-analysis.md artifact assembly.

**FR-AD2-2**: The Shared Assumption Extraction phase SHALL identify agreement points -- topics where two or more variants take the same approach, either explicitly (same stated approach) or implicitly (topic not mentioned, implying default assumed).

**FR-AD2-3**: For each agreement point, the phase SHALL enumerate the unstated preconditions that must be true for the agreed approach to work. Precondition categories SHALL include at minimum: data shape assumptions, cardinality assumptions, ordering assumptions, and timing assumptions.

**FR-AD2-4**: Each precondition SHALL be classified as STATED (explicitly documented in at least one variant), UNSTATED (not documented in any variant), or CONTRADICTED (contradicted by evidence elsewhere).

**FR-AD2-5**: All UNSTATED preconditions SHALL be promoted to synthetic diff points in the diff-analysis.md output, tagged with `[SHARED-ASSUMPTION]`. These synthetic diff points SHALL be included in the total diff point count used by convergence detection.

**FR-AD2-6**: Advocates in Round 1 SHALL be required to explicitly state whether they accept or reject each `[SHARED-ASSUMPTION]` diff point. The advocate prompt template SHALL be updated to include this requirement.

#### Non-Functional Requirements

**NFR-AD2-1**: The Shared Assumption Extraction phase SHALL add no more than 10% overhead to Step 1 execution time.

**NFR-AD2-2**: The output format SHALL use structured tables (not prose) to minimize context window consumption by downstream steps.

**NFR-AD2-3**: The phase SHALL be idempotent -- running it twice on the same input SHALL produce identical output.

#### Acceptance Criteria

**AC-AD2-1**:
- Given: 3 variants that all assume a 1:1 mapping between input events and output widgets (none states this explicitly)
- When: Shared Assumption Extraction executes
- Then: The output includes an UNSTATED precondition: "Input events map 1:1 to output widgets" with risk assessment "If precondition fails: output count diverges from input count, downstream bookkeeping breaks"

**AC-AD2-2**:
- Given: 2 variants where Variant A explicitly states "offset=0 means uninitialized" and Variant B does not mention offset semantics
- When: Shared Assumption Extraction executes
- Then: The output includes a STATED precondition for Variant A and an implicit agreement point for Variant B (topic not mentioned = default assumed), with an UNSTATED precondition: "offset=0 is never a legitimate runtime value"

**AC-AD2-3**:
- Given: diff-analysis.md with 10 diff points from existing phases and 3 `[SHARED-ASSUMPTION]` synthetic diff points from this phase
- When: Convergence detection runs after Round 2
- Then: The convergence formula uses 13 as the total_diff_points denominator (not 10)

**AC-AD2-4**:
- Given: A Round 1 advocate statement that does not address the `[SHARED-ASSUMPTION]` diff points
- When: The debate-orchestrator validates Round 1 output
- Then: The advocate is prompted to address the missing shared assumption points (or the omission is flagged in the transcript)

#### Interface Contracts

**Change to SKILL.md -- Step 1 Diff Analysis**:

Add a new phase after `unique_contribution_extraction` and before `diff_analysis_assembly`:

```yaml
shared_assumption_extraction:
  purpose: "Identify implicit agreements and their unstated preconditions"

  phase_1_agreement_identification:
    action: "For each topic covered by 2+ variants, check if all variants take the same approach"
    agreement_types:
      all_explicit: "All variants state the same approach"
      partial_explicit: "Some variants state, others omit (implicit agreement via silence)"
      all_implicit: "No variant addresses the topic, but all designs depend on a shared default"
    output: "List of agreement points with coverage classification"

  phase_2_assumption_enumeration:
    action: "For each agreement point, enumerate preconditions that must hold"
    precondition_categories:
      - "Data shape: what structure does the data have?"
      - "Cardinality: how many items? Can it be zero? One? Unbounded?"
      - "Ordering: does order matter? Is it guaranteed?"
      - "Timing: do events arrive in a specific order or at specific rates?"
    output: "List of preconditions per agreement point"

  phase_3_assumption_classification:
    STATED: "Precondition is explicitly documented in at least one variant"
    UNSTATED: "Precondition is not documented in any variant"
    CONTRADICTED: "Precondition is contradicted by evidence in at least one variant"

  phase_4_promotion:
    action: "All UNSTATED preconditions become synthetic diff points"
    tagging: "[SHARED-ASSUMPTION] prefix in diff point ID"
    id_scheme: "A-NNN (sequential, starting at A-001)"
    requirement: "Advocates must explicitly accept or reject each shared assumption in Round 1"
```

**Change to diff-analysis.md assembly**:

Add a new section between `## Unique Contributions` and `## Summary`:

```yaml
6_shared_assumptions:
  source: "Shared assumption extraction output"
  section: "## Shared Assumptions"
  format: |
    ### [Agreement Point Title]
    **Agreement**: [What all variants agree on]
    **Coverage**: [all-explicit | partial-explicit | all-implicit]
    **Stated preconditions**: [Preconditions documented in at least one variant]
    **Unstated preconditions**: [PROMOTED TO DIFF POINTS as A-NNN]
    - A-001: [Precondition description] — Risk: [What breaks if this fails]
    - A-002: ...
  id_scheme: "A-NNN (sequential, starting at A-001)"
```

**Change to advocate prompt template** (Round 1):

Add to the RULES section of `advocate_instantiation.prompt_generation.template`:

```
6. For each [SHARED-ASSUMPTION] diff point (A-NNN), you MUST explicitly state:
   - ACCEPT: "I accept this assumption because [evidence]"
   - REJECT: "I reject this assumption because [evidence/counter-example]"
   - QUALIFY: "This assumption holds under [conditions] but fails when [conditions]"
   Failure to address shared assumptions will be flagged as incomplete advocacy.
```

**Change to convergence detection**:

Update `convergence_detection.formula`:

```yaml
convergence_detection:
  formula: "convergence = agreed_points / total_diff_points"
  total_diff_points_includes: "S-NNN + C-NNN + X-NNN + A-NNN (shared assumption points)"
```

---

### 4.2 AD-5: Debate Topic Taxonomy with Minimum Coverage Requirements

**Priority**: A-Tier (77.5/100) -- Immediate implementation
**Composite breakdown**: Complexity 3/10, Overhead 2/10, Impact 7/10, Generalizability 8/10

#### Functional Requirements

**FR-AD5-1**: The debate protocol SHALL define a three-level topic taxonomy: L1 (Architecture), L2 (Interface Contracts), L3 (State Mechanics).

**FR-AD5-2**: Each diff point in diff-analysis.md (including `[SHARED-ASSUMPTION]` points from AD-2) SHALL be tagged with one or more taxonomy levels.

**FR-AD5-3**: After each debate round, the debate-orchestrator SHALL check taxonomy coverage: each level must have at least one diff point that was explicitly debated.

**FR-AD5-4**: Convergence SHALL NOT be declared if any taxonomy level has zero coverage. If a level has zero coverage and maximum rounds are exhausted, the protocol SHALL force one additional round focused on the uncovered level.

**FR-AD5-5**: The forced round SHALL instruct advocates to enumerate concerns at the uncovered taxonomy level. For L3 (state mechanics), this means: enumerate state variables, trace transitions, and identify boundary conditions.

**FR-AD5-6**: Diff points generated by AD-2 (Shared Assumption Extraction) that relate to state variables, guards, or boundaries SHALL be automatically tagged as L3.

#### Non-Functional Requirements

**NFR-AD5-1**: The taxonomy coverage check SHALL add negligible overhead (< 1% of step execution time). It is a structural gate, not an analytical step.

**NFR-AD5-2**: The taxonomy SHALL be extensible -- new levels can be added without restructuring the debate protocol.

**NFR-AD5-3**: Forced rounds triggered by insufficient taxonomy coverage SHALL produce diff points that are scored normally (no special weighting).

#### Acceptance Criteria

**AC-AD5-1**:
- Given: A debate with 8 diff points, all tagged L1 (Architecture) or L2 (Interface Contracts), zero tagged L3 (State Mechanics)
- When: Convergence check runs after Round 2 with 87% agreement
- Then: Convergence is NOT declared despite exceeding the 80% threshold. A forced round focused on L3 is triggered.

**AC-AD5-2**:
- Given: A forced L3 round produces 3 new diff points about state variables and boundary conditions
- When: The debate continues with these new diff points
- Then: The convergence denominator increases by 3, and the new points are debated and scored normally.

**AC-AD5-3**:
- Given: AD-2 produces `[SHARED-ASSUMPTION]` diff point A-001 about "offset=0 is never a legitimate runtime value"
- When: Taxonomy tagging runs
- Then: A-001 is automatically tagged L3 (State Mechanics) because it concerns a state variable boundary value.

**AC-AD5-4**:
- Given: `--depth quick` is specified (Round 1 only)
- When: Taxonomy check runs after Round 1
- Then: If L3 has zero coverage, one forced round is still triggered (taxonomy gate overrides depth limitation for coverage).

#### Interface Contracts

**New section in SKILL.md** (after convergence detection, before scoring matrix):

```yaml
debate_topic_taxonomy:
  purpose: "Ensure debate covers all levels of design, not just architectural trade-offs"

  levels:
    L1_architecture:
      description: "High-level structural decisions: patterns, component boundaries, technology choices"
      examples: "windowing vs virtualization, monolith vs microservice, SQL vs NoSQL"
      minimum_coverage: 1
      auto_tag_signals: ["architecture", "pattern", "component", "structure", "framework"]

    L2_interface_contracts:
      description: "Component interfaces, data formats, API contracts, type signatures"
      examples: "function signatures, event schemas, message formats, return types"
      minimum_coverage: 1
      auto_tag_signals: ["interface", "API", "contract", "schema", "type", "signature", "format"]

    L3_state_mechanics:
      description: "State variables, transitions, guards, invariants, boundary conditions"
      examples: "cursor logic, offset tracking, guard conditions, filter effects on counts"
      minimum_coverage: 1
      auto_tag_signals: ["state", "guard", "sentinel", "boundary", "invariant", "cursor", "offset", "filter", "count", "empty", "zero"]

  tagging:
    timing: "During diff-analysis assembly, after all phases complete"
    method: "Each diff point tagged with 1+ levels based on content analysis and auto_tag_signals"
    shared_assumptions: "A-NNN points from AD-2 involving state/guard/boundary are auto-tagged L3"
    multi_level: "A diff point can span multiple levels (e.g., an API design affecting state management)"

  coverage_check:
    timing: "After each debate round, before convergence check"
    gate: "convergence_eligible = all(level.debated_count >= level.minimum_coverage)"
    integration: "Added as AND condition to existing convergence formula"

  forced_round:
    trigger: "Any taxonomy level has zero coverage after max configured rounds"
    instruction: |
      This is a forced debate round focused on {uncovered_level.description}.
      Advocates MUST enumerate concerns at this level:
      - For L1: structural trade-offs, component boundaries
      - For L2: interface contracts, data format assumptions
      - For L3: state variables, their ranges, boundary values, guard conditions, transition logic
    output: "New diff points tagged with the uncovered level, scored normally"
    limit: "Maximum 1 forced round per uncovered level"
```

**Change to convergence detection**:

Update `convergence_detection` to include taxonomy gate:

```yaml
convergence_detection:
  formula: "convergence = agreed_points / total_diff_points"
  additional_gates:
    taxonomy_coverage: "all taxonomy levels have >= minimum_coverage debated points"
    invariant_probe: "high_severity_unaddressed_count == 0 (if AD-1 is active)"
  combined: "convergence_met = (formula >= threshold) AND taxonomy_coverage AND invariant_probe"
```

---

### 4.3 AD-1: Mandatory Invariant Probe Round

**Priority**: A-Tier (72.5/100) -- Next cycle implementation
**Composite breakdown**: Complexity 5/10, Overhead 4/10, Impact 8/10, Generalizability 7/10

#### Functional Requirements

**FR-AD1-1**: The debate protocol SHALL include a Round 2.5 (Invariant Probe Round) that executes between Round 2 (Rebuttals) and Round 3 (Final Arguments), conditioned on `--depth standard` or `--depth deep`.

**FR-AD1-2**: The Invariant Probe Round SHALL be executed by a fault-finder agent that is NOT an advocate for any variant. This agent operates orthogonally to the advocate structure.

**FR-AD1-3**: The fault-finder agent SHALL systematically apply a boundary-condition checklist to the emerging consensus, organized into five categories: state variables, guard conditions, count divergence, collection boundaries, and interaction effects.

**FR-AD1-4**: The checklist output SHALL classify each identified assumption as ADDRESSED (with variant and section citation) or UNADDRESSED, with a severity rating (HIGH, MEDIUM, LOW).

**FR-AD1-5**: UNADDRESSED HIGH-severity assumptions SHALL become mandatory discussion items for Round 3 (or a forced round if depth is standard).

**FR-AD1-6**: Convergence SHALL NOT be declared if any HIGH-severity assumptions remain UNADDRESSED. MEDIUM-severity assumptions SHALL be logged as warnings in the merge output.

**FR-AD1-7**: The boundary-condition checklist SHALL be extensible. New failure classes can be added to the checklist without modifying the debate protocol structure.

#### Non-Functional Requirements

**NFR-AD1-1**: The Invariant Probe Round SHALL add no more than 15% overhead to the overall debate execution.

**NFR-AD1-2**: The fault-finder agent SHALL operate within a single agent invocation (not a full debate round). It produces a checklist output, not a discursive argument.

**NFR-AD1-3**: The invariant-probe.md artifact SHALL use structured tables with clear ADDRESSED/UNADDRESSED tagging for machine-parseable downstream consumption.

#### Acceptance Criteria

**AC-AD1-1**:
- Given: An emerging consensus where all variants assume a pipeline stage produces exactly one output per input (no filtering)
- When: The fault-finder applies the count_divergence checklist
- Then: The output includes: "UNADDRESSED (HIGH): Pipeline stage X consumes N items but may produce M != N items. No variant addresses the M < N case."

**AC-AD1-2**:
- Given: A consensus where offset=0 is used as a sentinel for "uninitialized"
- When: The fault-finder applies the guard_conditions checklist
- Then: The output includes: "UNADDRESSED (HIGH): Guard uses offset=0 as sentinel. The guarded variable can legitimately equal 0 through normal operation (empty sequence). Sentinel collision possible."

**AC-AD1-3**:
- Given: invariant-probe.md contains 2 HIGH-severity UNADDRESSED assumptions
- When: Convergence check runs with 90% agreement on diff points
- Then: Convergence is NOT declared. The 2 assumptions are injected as mandatory Round 3 discussion items.

**AC-AD1-4**:
- Given: `--depth quick` is specified
- When: The protocol reaches the point where Round 2.5 would execute
- Then: The Invariant Probe Round is SKIPPED (it requires `--depth standard` or `--depth deep`).

#### Interface Contracts

**New round in SKILL.md** (between Round 2 and Round 3):

```yaml
round_2_5_invariant_probe:
  condition: "--depth standard OR --depth deep"
  skip_condition: "--depth quick → skip (log: 'Invariant probe skipped: depth=quick')"
  agent: "fault-finder (NOT an advocate for any variant)"
  model: "High-capability (opus preferred)"

  input:
    - "All variants"
    - "debate-transcript.md (Rounds 1-2)"
    - "Emerging consensus points from convergence tracking"
    - "Shared assumptions from diff-analysis.md (A-NNN points, if AD-2 is active)"

  checklist_categories:
    state_variables:
      - "For each state variable: enumerate initial value, valid range, update triggers, boundary values"
      - "For each boundary value: what happens when the variable equals it?"
      - "For each pair of state variables: are there interaction constraints?"

    guard_conditions:
      - "For each guard/sentinel check: what is the sentinel value?"
      - "Can the guarded variable legitimately equal the sentinel through normal operation?"
      - "What happens if the guard fires incorrectly, or fails to fire when it should?"

    count_divergence:
      - "For each pipeline stage that consumes N items and produces M items: is N always equal to M?"
      - "If N can differ from M: do downstream stages use N or M for bookkeeping?"
      - "What happens when M is zero?"

    collection_boundaries:
      - "For each collection: what happens when it is empty?"
      - "For each iteration: what happens on the first item? The last item?"
      - "For each filter: what happens when the filter removes all items?"

    interaction_effects:
      - "For each pair of components that share state: trace all write-read paths"
      - "For each feedback loop: what happens when one component's output changes the other's assumptions?"

  output:
    artifact: "adversarial/invariant-probe.md"
    format: |
      # Invariant Probe Results
      ## Metadata
      - Checklist categories applied: 5
      - Assumptions identified: <N>
      - ADDRESSED: <N>
      - UNADDRESSED: <N> (HIGH: <N>, MEDIUM: <N>, LOW: <N>)

      ## Findings
      | ID | Category | Assumption | Status | Severity | Evidence |
      |----|----------|------------|--------|----------|----------|
      | IP-001 | guard_conditions | offset=0 used as sentinel | UNADDRESSED | HIGH | No variant addresses zero-is-valid |
      ...

  convergence_gate:
    condition: "high_severity_unaddressed_count == 0"
    failure_action: "UNADDRESSED HIGH items become mandatory Round 3 discussion items"
    medium_severity: "Logged as warnings in merge-log.md"
```

**Change to artifact output structure**:

Add `invariant-probe.md` to the adversarial directory listing:

```
<output-dir>/
├── <merged-output>.md
└── adversarial/
    ├── variant-N-<agent>.md
    ├── diff-analysis.md            # Step 1 (now includes Shared Assumptions section)
    ├── debate-transcript.md        # Step 2
    ├── invariant-probe.md          # Step 2.5 (NEW)
    ├── base-selection.md           # Step 3
    ├── refactor-plan.md            # Step 4
    └── merge-log.md                # Step 5
```

**Change to return contract**:

```yaml
return_contract:
  merged_output_path: "<path>"
  convergence_score: "<percentage>"
  artifacts_dir: "<path>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list>"]
  unaddressed_invariants: ["<list of HIGH-severity UNADDRESSED items>"]  # NEW
```

---

### 4.4 AD-3: Edge Case Coverage as Mandatory Scoring Dimension

**Priority**: A-Tier (67.5/100) -- Future implementation
**Composite breakdown**: Complexity 3/10, Overhead 2/10, Impact 5/10, Generalizability 7/10

#### Functional Requirements

**FR-AD3-1**: The qualitative scoring layer (Step 3) SHALL include a sixth dimension called "Invariant & Edge Case Coverage" with 5 binary criteria, evaluated using the same CEV (Claim-Evidence-Verdict) protocol as existing dimensions.

**FR-AD3-2**: The 5 criteria SHALL be:
1. Enumerates state variables with their valid ranges and boundary values
2. Identifies guard conditions and documents their failure modes
3. Analyzes filter/transform stages for count divergence
4. Documents empty-collection and single-element behaviors
5. Traces cross-component state interactions and feedback loops

**FR-AD3-3**: A variant SHALL NOT be eligible as the base if it scores 0/5 on this dimension, regardless of its overall score (floor requirement).

**FR-AD3-4**: The qualitative score formula SHALL be updated from `total_criteria_met / 25` to `total_criteria_met / 30` to accommodate the new dimension.

**FR-AD3-5**: The combined scoring formula SHALL remain unchanged -- qual_score is still weighted at 0.50 of the variant_score.

#### Non-Functional Requirements

**NFR-AD3-1**: The new dimension SHALL add negligible overhead (< 3%) to the scoring step, since scoring already requires reading each variant.

**NFR-AD3-2**: Each criterion SHALL have CEV guidance specifying what evidence to search for, consistent with the existing 25 criteria.

#### Acceptance Criteria

**AC-AD3-1**:
- Given: Variant A scores 24/25 on existing criteria but 0/5 on the new dimension. Variant B scores 20/25 on existing criteria and 3/5 on the new dimension.
- When: Base selection runs
- Then: Variant A is ineligible as base (floor requirement: score >= 1/5). Variant B is eligible.

**AC-AD3-2**:
- Given: Two variants with identical scores on all existing dimensions
- When: Variant A has 4/5 on edge case coverage and Variant B has 1/5
- Then: Variant A scores higher overall (4/30 vs 1/30 difference in qual_score).

**AC-AD3-3**:
- Given: A variant that includes a section enumerating state variables with ranges and boundary values
- When: CEV evaluation runs for criterion 1
- Then: The evaluator cites the specific section as evidence and assigns MET.

#### Interface Contracts

**Change to qualitative scoring layer in SKILL.md**:

Add after `risk_coverage` dimension:

```yaml
qualitative_scoring:
  rubric:
    # ... existing 5 dimensions unchanged ...

    invariant_edge_case_coverage:
      criteria:
        1:
          description: "Enumerates state variables with their valid ranges and boundary values"
          cev_guidance: "Look for explicit lists of state variables, their types, ranges, and edge values (zero, empty, max)"
        2:
          description: "Identifies guard conditions and documents their failure modes"
          cev_guidance: "Look for guard/sentinel patterns and analysis of what happens when guards fire incorrectly or fail to fire"
        3:
          description: "Analyzes filter/transform stages for count divergence"
          cev_guidance: "Look for pipeline stages where input count may differ from output count, with explicit handling"
        4:
          description: "Documents empty-collection and single-element behaviors"
          cev_guidance: "Look for explicit handling of empty lists, zero-length sequences, and single-element edge cases"
        5:
          description: "Traces cross-component state interactions and feedback loops"
          cev_guidance: "Look for analysis of how shared state between components creates interaction effects"

      floor_requirement:
        threshold: 1
        effect: "Variant with score < 1/5 is INELIGIBLE as base"

  formula: "qual_score = total_criteria_met / 30"  # Updated from /25
```

**Change to base selection logic**:

Add floor check before combined scoring:

```yaml
base_selection:
  pre_scoring_gate:
    invariant_floor:
      check: "invariant_edge_case_coverage_score >= 1"
      failure: "Variant marked INELIGIBLE — excluded from base selection"
      log: "Variant {N} excluded: edge case coverage floor not met (0/5)"
```

---

## 5. Integration Points

### 5.1 Integration with sc:spec-panel Improvements

The cross-cutting analysis identifies Cluster B ("Surface Hidden Assumptions and Shared Blind Spots") as the primary integration surface:

| Adversarial Proposal | Spec-Panel Proposal | Integration |
|---------------------|---------------------|-------------|
| AD-2: Shared Assumption Extraction | SP-2: Adversarial Tester Persona | SP-2 provides the destructive mindset during spec review; AD-2 surfaces the assumptions during debate. SP-2's attack taxonomy (zero/empty, divergence, sentinel collision) aligns with AD-2's precondition categories. |
| AD-1: Invariant Probe Checklist | SP-3: Guard Boundary Table | SP-3's boundary table from spec review can feed into AD-1's probe as pre-identified state variables and guards, reducing the probe's search space and increasing its precision. |
| AD-5: Taxonomy (L3 gate) | SP-3: Guard Boundary Table | SP-3 generates L3-level content at the spec review stage. If AD-5's taxonomy check finds L3 coverage is insufficient, SP-3 artifacts provide ready-made L3 diff points to inject. |

**Artifact propagation chain** (from cross-cutting analysis):

```
SP-3 (Guard Boundary Table) → AD-1 (Invariant Probe input) → RM-1 (State Invariant Analysis)
```

This chain is defined but not mandated in this release. Each stage can operate independently. The integration is a separate work item after both the adversarial and spec-panel release specs are implemented.

### 5.2 Integration with sc:roadmap Improvements

| Adversarial Proposal | Roadmap Proposal | Integration |
|---------------------|------------------|-------------|
| AD-2: Shared Assumptions output | RM-1: State Invariant Analysis Section | RM-1's state invariant table can be initialized from AD-2's shared assumption output rather than derived from scratch. |
| AD-1: invariant-probe.md | RM-2: Negative Acceptance Criteria | AD-1's UNADDRESSED items are natural candidates for negative acceptance criteria generation. Each UNADDRESSED assumption suggests a "must NOT" criterion. |
| AD-3: Edge Case Scoring | RM-5: Risk Register Categories | AD-3's scoring criteria map to RM-5's STATE and XCOMP risk categories, providing consistent coverage language across commands. |

### 5.3 No Breaking Changes

All four proposals are additive to the existing protocol. No existing steps are removed or restructured. The changes are:
- One new sub-phase in Step 1 (AD-2)
- One new section in the debate protocol (AD-5 taxonomy)
- One new round between existing rounds (AD-1, Round 2.5)
- One new scoring dimension (AD-3, 6th dimension)
- Updated convergence formula with additional AND conditions

Existing invocations of `/sc:adversarial` will gain the new behaviors automatically. No flag changes are required for the default case.

---

## 6. Implementation Phasing

### Phase 1: Minimum Viable (Immediate, Days 1-3)

**Goal**: Eliminate the "agreement = no scrutiny" structural bias. Catch both v0.04 bug classes.

| Day | Task | Proposal | Effort | Files Modified |
|-----|------|----------|--------|----------------|
| 1 | Define three taxonomy levels and add coverage gate to convergence detection | AD-5 | 4 hours | SKILL.md |
| 1-2 | Implement shared assumption extraction sub-phase in Step 1 diff analysis | AD-2 | 8 hours | SKILL.md |
| 2 | Update advocate prompt template to require shared assumption responses | AD-2 | 1 hour | SKILL.md |
| 2 | Update diff-analysis.md assembly to include Shared Assumptions section | AD-2 | 1 hour | SKILL.md |
| 3 | Update convergence detection formula with taxonomy gate | AD-5 | 2 hours | SKILL.md |
| 3 | Integration test: replay v0.04 variants through updated protocol | -- | 4 hours | -- |

**Expected outcome**: Protocol surfaces unstated assumptions as debatable diff points. Taxonomy gate forces L3 (state mechanics) coverage. Both v0.04 bug classes are caught. Overhead: ~10-15%.

**Validation**: Run the updated protocol against the v0.04 spec variants. Verify that the two bugs appear as either UNSTATED shared assumptions (AD-2) or forced L3 debate topics (AD-5).

### Phase 2: Structural Reinforcement (Next Cycle, Days 4-8)

**Goal**: Add dedicated fault-finding capability and convergence teeth.

| Day | Task | Proposal | Effort | Files Modified |
|-----|------|----------|--------|----------------|
| 4 | Define fault-finder agent prompt and boundary-condition checklist | AD-1 | 4 hours | SKILL.md |
| 5 | Implement Round 2.5 dispatch logic (condition on depth, agent instantiation) | AD-1 | 6 hours | SKILL.md |
| 6 | Implement invariant-probe.md artifact assembly | AD-1 | 4 hours | SKILL.md |
| 6 | Add convergence gate (HIGH-severity UNADDRESSED = convergence blocked) | AD-1 | 2 hours | SKILL.md |
| 7 | Update return contract to include unaddressed_invariants field | AD-1 | 1 hour | SKILL.md, adversarial.md |
| 7-8 | Integration test: verify probe catches boundary conditions, gate blocks convergence | -- | 4 hours | -- |

**Expected outcome**: Dedicated fault-finder agent probes the consensus with a systematic checklist. Convergence requires zero HIGH-severity gaps. Overhead: ~15-25% total (Phase 1 + Phase 2).

### Phase 3: Scoring Incentives (Future, after Phase 1-2 validation)

**Goal**: Create lasting incentive for edge case coverage in variant quality.

| Task | Proposal | Effort | Files Modified |
|------|----------|--------|----------------|
| Add 6th qualitative dimension with 5 criteria and CEV guidance | AD-3 | 4 hours | SKILL.md |
| Update qualitative formula from /25 to /30 | AD-3 | 30 min | SKILL.md |
| Implement floor requirement (score >= 1/5 for base eligibility) | AD-3 | 2 hours | SKILL.md |
| Update base-selection.md template to include new dimension | AD-3 | 1 hour | SKILL.md |
| Validation: verify scoring produces expected differentiation | -- | 2 hours | -- |

**Expected outcome**: Variants that enumerate edge cases score measurably higher. Variants that completely ignore edge cases are ineligible as base. Overhead: negligible (< 3% additional).

### Dependency Graph

```
AD-2 (Shared Assumptions) ← independent, no dependencies
    ↓ feeds
AD-5 (Taxonomy) ← independent, but synergizes with AD-2 (auto-tags A-NNN as L3)
    ↓ taxonomy creates L3 coverage
AD-1 (Invariant Probe) ← depends on AD-2 output for richer input
    ↓ probe findings inform
AD-3 (Scoring Dimension) ← independent, but benefits from AD-1 findings as scoring evidence
```

AD-2 and AD-5 can be implemented in parallel (Phase 1). AD-1 should follow (Phase 2). AD-3 is independent and can be implemented at any time but benefits from the context of Phases 1-2.

---

## 7. Risks & Mitigations

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-1 | Shared assumption extraction produces formulaic, low-quality output ("no assumptions identified") | Medium | High | AD-5's taxonomy gate forces L3 coverage regardless. AD-1's checklist provides a structured alternative path to the same findings. Defense in depth: if AD-2 misses assumptions, AD-1 or AD-5 catch them. |
| R-2 | Cumulative overhead exceeds tolerance (40% ceiling) | Medium | Medium | Phase implementation with measurement after each phase. Phase 1 targets 10-15%; Phase 2 targets 15-25%. If Phase 1 alone reaches 25%, defer Phase 2 pending optimization. |
| R-3 | Forced taxonomy rounds produce shallow analysis (agents have nothing substantive to say about L3) | Low | Medium | AD-2's shared assumption extraction generates concrete L3 diff points. The forced round has specific targets, not a vague "discuss state mechanics" instruction. |
| R-4 | Invariant probe checklist becomes stale (new bug classes emerge that are not in the checklist) | Low | High | NFR-AD1-7 requires the checklist to be extensible. Post-implementation bugs should trigger checklist updates. Track whether post-implementation bugs are in checked categories as a success metric. |
| R-5 | Context window competition from new artifacts (invariant-probe.md, expanded diff-analysis.md) | Low | Medium | NFR-AD2-2 and NFR-AD1-3 require structured table formats (not prose). Downstream steps consume summary counts, not full artifacts. |
| R-6 | Edge case scoring floor requirement rejects all variants in edge cases where no variant addresses invariants | Very Low | Medium | Floor is 1/5, not 3/5. A variant needs only one criterion met. If all variants score 0/5, the floor is suspended with a warning (all variants equally deficient). |
| R-7 | False sense of security from checklists ("the checklist passed, so it must be correct") | Low | High | Track whether post-implementation bugs are in checked checklist categories. If new classes emerge, extend the checklist. The checklist is a forcing function, not a guarantee. |

---

## 8. NOT Doing

### AD-4: Post-Merge Interaction Stress Test (B-Tier, 57.5/100) -- DEFERRED

**What it would do**: Add a Step 4.5 that traces cross-component interactions in the merge plan to identify emergent failure modes that exist in neither source variant individually.

**Why it is deferred**:

1. **High cost, narrow scope**: Complexity 7/10, Overhead 6/10. It adds a full new step with multi-phase analysis (interaction surface identification, interaction tracing, failure enumeration, plan amendment). This is the most expensive adversarial proposal by a significant margin.

2. **Partially redundant with other proposals**: AD-2 (shared assumptions) and AD-1 (invariant probe with interaction_effects checklist) already cover many of the same cross-component interaction bugs at lower cost. The cross-cutting analysis notes that "SP-4 and RM-3 catch many of the same bugs at lower cost" from different pipeline stages.

3. **Low generalizability**: Scored 5/10 on generalizability. The stress test is specific to the adversarial debate merge step and is not transferable to other commands.

4. **Conditional value**: The stress test targets merge-emergent bugs specifically. If AD-2 + AD-5 + AD-1 prove effective at catching interaction bugs before the merge step, the stress test's value is further reduced.

**Reconsideration trigger**: If merge-emergent bugs become a recurrent pattern despite Phase 1-2 improvements, this proposal should be re-evaluated.

### Items explicitly out of scope for this release

- **Cross-command artifact propagation**: The SP-3 -> AD-1 -> RM-1 chain is designed but not mandated. Integration depends on the spec-panel and roadmap release specs.
- **Mode B variant generation improvements**: No changes to the `--agents` specification or variant generation pipeline.
- **Interactive mode changes**: No new interactive checkpoints added (existing checkpoints remain).
- **Depth level changes**: No changes to the quick/standard/deep depth semantics beyond the AD-5 forced round (which adds a round, not a depth level).
- **Command definition changes**: The `adversarial.md` command definition file requires no changes. All improvements are in the protocol SKILL.md.

---

## Appendix A: Artifact Format References

### A.1 Shared Assumptions Section (diff-analysis.md)

```markdown
## Shared Assumptions

### Event-to-Widget Mapping
**Agreement**: All variants process events through a pipeline that produces widgets
**Coverage**: all-implicit
**Stated preconditions**: None
**Unstated preconditions**:
- A-001: Events map 1:1 to widgets (every event produces exactly one widget) — Risk: If a filter removes events, `mounted_widgets < events_consumed`, causing cursor stall
- A-002: At least one event exists in every batch — Risk: Empty batch produces zero widgets, downstream division-by-zero

### Offset Sentinel Semantics
**Agreement**: All variants use offset=0 as "uninitialized" sentinel
**Coverage**: partial-explicit (Variant A states, Variant B implicit)
**Stated preconditions**: Variant A, Section 3.2: "offset initialized to 0 before first event"
**Unstated preconditions**:
- A-003: offset=0 is never a legitimate runtime value — Risk: Empty sequence legitimately has offset=0, sentinel collision makes "uninitialized" indistinguishable from "empty"
```

### A.2 Invariant Probe Artifact (invariant-probe.md)

```markdown
# Invariant Probe Results

## Metadata
- Checklist categories applied: 5
- Assumptions identified: 7
- ADDRESSED: 3
- UNADDRESSED: 4 (HIGH: 2, MEDIUM: 1, LOW: 1)

## Findings

| ID | Category | Assumption | Status | Severity | Evidence |
|----|----------|------------|--------|----------|----------|
| IP-001 | count_divergence | Pipeline stage produces M != N items when filter active | UNADDRESSED | HIGH | No variant addresses M < N case |
| IP-002 | guard_conditions | offset=0 sentinel collides with legitimate empty-sequence value | UNADDRESSED | HIGH | Variant A uses 0 as sentinel (Section 3.2); no variant considers empty sequence |
| IP-003 | collection_boundaries | Last event in sequence may produce empty tail | ADDRESSED | -- | Variant B, Section 4.1 handles empty tail explicitly |
| IP-004 | state_variables | cursor range is [0, event_count) but event_count can change during iteration | UNADDRESSED | MEDIUM | No variant addresses concurrent modification |
| IP-005 | interaction_effects | Visualizer filtering affects runner cursor via shared mounted_count | UNADDRESSED | LOW | Interaction not traced in any variant |

## Convergence Gate
- HIGH-severity UNADDRESSED: 2
- Gate status: BLOCKED — convergence cannot be declared
- Required: Address IP-001 and IP-002 in Round 3 or forced round
```

---

*Release specification authored 2026-03-04. Ready for implementation handoff.*
