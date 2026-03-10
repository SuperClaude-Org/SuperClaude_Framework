# Release Specification: /sc:spec-panel Correctness & Adversarial Review Enhancements

**Document ID**: SPEC-PANEL-2026-Q1
**Version**: 1.0
**Date**: 2026-03-04
**Status**: Draft
**Author**: Release Spec Agent (Opus 4.6)
**Source**: Adversarial debate on 5 proposals (SP-1 through SP-5), cross-cutting analysis with AD-* and RM-* proposals

---

## 1. Executive Summary

This release enhances the `/sc:spec-panel` command to catch **execution-correctness bugs** -- a class of defects where specifications are clearly written, architecturally sound, and testable, but contain logical errors at state boundaries that escape all current review mechanisms.

The changes introduce four capabilities:

1. **An adversarial tester expert persona** (SP-2) that actively attacks specifications rather than evaluating them constructively.
2. **A mandatory guard condition boundary table artifact** (SP-3) that forces boundary-value reasoning for every conditional in the spec.
3. **A new `--focus correctness` review pass** (SP-1) that shifts the panel from document-quality review to execution-soundness verification.
4. **A pipeline dimensional analysis heuristic** (SP-4) that detects count-mismatch bugs in filter/transform pipelines.

A fifth proposal (SP-5, cross-expert challenge protocol) is deferred to a future release pending validation of SP-2.

**Expected impact**: The panel gains structural mechanisms that make it impossible to skip boundary-value reasoning and state-invariant analysis. Based on retrospective analysis, these mechanisms would have caught 100% of the state-machine edge-case bugs observed in v0.04 post-implementation.

**Overhead budget**: Less than 25% additional tokens per invocation for Phase 1-2 combined.

---

## 2. Background & Motivation

### 2.1 The Problem Class

A class of specification bugs exists where:

- The specification is **clearly written** (requirements are unambiguous).
- The architecture is **sound** (interfaces are clean, boundaries are well-defined).
- The testing strategy is **reasonable** (edge cases are mentioned, acceptance criteria exist).
- Yet the specification contains **logical errors at state boundaries** that produce incorrect behavior at runtime.

These bugs share common characteristics:

- **Guard condition failures at boundary values**: A guard like `> 0` silently fails when a variable is legitimately zero through a valid code path.
- **Pipeline dimensional mismatches**: A cursor, offset, or index uses the count from the wrong stage of a filter/transform pipeline (e.g., advancing by "widgets mounted" instead of "events consumed").
- **Cross-component state feedback**: Component B's behavior (e.g., filtering) changes the assumptions Component A depends on (e.g., cursor advancement), but no one traces this interaction.

### 2.2 Why the Current Panel Misses Them

The current spec-panel has four focus areas: requirements, architecture, testing, and compliance. All four are oriented toward **document quality** -- clarity, completeness, testability, soundness. None is oriented toward **execution correctness** -- whether the state transitions described in the spec are correct at every boundary.

The panel's ten expert personas are constructive reviewers. They ask "is this spec good enough?" They do not ask "how do I make this spec fail?" Research on code review effectiveness shows that reviewers explicitly asked to find bugs find significantly more than reviewers asked to evaluate quality.

No expert is tasked with tracing a variable through execution and asking "what is its value at each boundary?" No mandatory artifact forces the panel to enumerate boundary values for every guard condition. No heuristic triggers when a pipeline's output count can diverge from its input count.

### 2.3 Concrete Example (Generalized)

In the v0.04 development cycle, two bugs escaped the full spec-panel + adversarial debate + roadmap pipeline:

- **Bug A (Pipeline Dimensional Mismatch)**: A paginated view consumed N events from a store, filtered them to M widgets (M <= N), and advanced its cursor by M instead of N. When filtering removed events, the cursor stalled and the view looped.
- **Bug B (Guard Bypass at Zero)**: A replay guard checked `offset > 0` to prevent re-execution. When the input collection was empty, offset was 0, the guard failed, and replay ran unconditionally.

Both bugs were in areas where all panel experts agreed the spec was adequate. The specifications were clear, testable, and architecturally sound. The bugs were logical errors at state boundaries that no expert was structurally required to examine.

---

## 3. Design Decisions

The following decisions were resolved through adversarial debate (Architect vs Analyzer perspectives) and composite scoring across four dimensions (complexity, overhead, impact, generalizability).

### DD-1: Add a New Expert vs. Modify Existing Experts

**Decision**: Add a new adversarial tester persona (SP-2) AND modify existing expert behaviors under a new focus area (SP-1).

**Rationale**: The debate established that the adversarial mindset is fundamentally different from constructive review and cannot be adequately grafted onto existing personas without diluting their primary roles. However, the new focus area (`--focus correctness`) also requires existing experts to shift their lens, which is a complementary mechanism. SP-2 scored 78.0 (A-Tier); SP-1 scored 70.5 (A-Tier). Both are implemented, with SP-2 in Phase 1 and SP-1 in Phase 2.

### DD-2: Mandatory Artifacts vs. Optional Analysis

**Decision**: The guard condition boundary table (SP-3) is a mandatory output artifact, not an optional analysis.

**Rationale**: The debate verdict was clear: "the power of this artifact is not in reading it -- it is in constructing it." Optional artifacts are skipped under time pressure. Mandatory artifacts force the reasoning that catches bugs. The overhead concern (formulaic output risk) is mitigated by the adversarial tester (SP-2) validating table entries. SP-3 scored 75.5 (A-Tier).

### DD-3: Broad Focus Area vs. Narrow Heuristic

**Decision**: Implement both the broad correctness focus (SP-1) and the narrow pipeline dimensional analysis heuristic (SP-4).

**Rationale**: These are complementary, not competing. SP-1 provides the structural framework; SP-4 provides a specific, high-precision heuristic for a common bug class. SP-4 is conditionally triggered (only when pipelines are detected) so it adds near-zero overhead for non-pipeline specs. SP-4 scored 68.5 (A-Tier).

### DD-4: Challenge Protocol Timing

**Decision**: Defer the cross-expert challenge protocol (SP-5) to a future release.

**Rationale**: SP-5 scored 57.5 (B-Tier) -- the lowest of all spec-panel proposals. It adds 20-30% overhead, requires workflow restructuring, and does not introduce new analytical techniques. Its value is multiplicative with SP-2 (the adversarial tester provides a strong challenger), so it should be evaluated only after SP-2 has been validated through at least one development cycle.

### DD-5: Artifact Propagation to Downstream Commands

**Decision**: SP-3's boundary table output is designed for consumption by downstream commands (adversarial debate's invariant probe round AD-1, roadmap's state invariant section RM-1).

**Rationale**: The cross-cutting analysis identified that cross-command artifact propagation is the highest-leverage underexplored opportunity. Each stage should verify prior stages' artifacts rather than re-deriving from scratch. SP-3's table format is specified to be machine-parseable for this reason.

---

## 4. Spec Items

### 4.1 SP-2: Adversarial Tester Expert Persona

**Priority**: Immediate (Phase 1)
**Composite Score**: 78.0 / 100 (A-Tier, Rank 3 overall)

#### Functional Requirements

**FR-1**: The spec-panel SHALL include a new expert persona named "James Whittaker" with the role of Adversarial Testing Pioneer.

**FR-2**: The adversarial tester persona SHALL execute five attack methodologies against the specification:
- FR-2.1: **Zero/Empty Attack** -- For every input, argument, and collection: what if it is zero, empty, null, or negative?
- FR-2.2: **Divergence Attack** -- For every pipeline/transformation: what if the output count differs from the input count?
- FR-2.3: **Sentinel Collision Attack** -- For every guard condition: what if the variable legitimately holds the sentinel value the guard checks against?
- FR-2.4: **Sequence Attack** -- For every operation: what if it is called twice, never called, called out of order, or called concurrently?
- FR-2.5: **Accumulation Attack** -- For every counter/offset/cursor: what if accumulated drift causes it to be wrong after N operations?

**FR-3**: The adversarial tester SHALL produce findings in the format: "I can break this specification by [attack]. The invariant at [location] fails when [condition]. Concrete attack: [scenario with state trace]."

**FR-4**: The adversarial tester SHALL be activated in ALL focus areas (requirements, architecture, testing, compliance, correctness) but SHALL lead when `--focus correctness` is specified.

**FR-5**: The adversarial tester SHALL review AFTER Fowler and Nygard in review sequence, and SHALL attack every interface contract and guard condition they identified.

#### Non-Functional Requirements

**NFR-1**: The adversarial tester persona SHALL add no more than 10% token overhead per invocation when included in the panel.

**NFR-2**: The persona definition SHALL follow the existing expert panel YAML structure for consistency with other personas.

**NFR-3**: Attack findings SHALL use the existing severity classification system (CRITICAL, MAJOR, MINOR).

#### Acceptance Criteria

**AC-1**: Given a specification containing a guard condition `> 0` protecting against re-execution, When the adversarial tester reviews the specification, Then it SHALL produce at least one finding identifying the zero-value bypass scenario.

**AC-2**: Given a specification describing a pipeline with filtering (input count != output count), When the adversarial tester reviews the specification, Then it SHALL produce at least one finding questioning which count drives downstream state.

**AC-3**: Given a specification with no guard conditions, pipelines, or mutable state, When the adversarial tester reviews the specification, Then it SHALL still apply sequence attacks and accumulation attacks but MAY produce zero findings.

**AC-4**: Given the adversarial tester is included in a panel with `--mode critique`, When the panel output is generated, Then the adversarial tester's findings SHALL appear in a distinct section labeled "Adversarial Analysis" with the attack methodology identified for each finding.

#### Interface Contract

Add to the Expert Panel System section of `spec-panel.md`:

```markdown
### Adversarial Analysis Expert

**James Whittaker** - Adversarial Testing Pioneer
- **Domain**: Attack surface analysis, boundary exploitation, degenerate input generation, guard condition probing
- **Methodology**: Zero/empty attacks, divergence attacks, sentinel collision, sequence abuse, accumulation drift
- **Critique Focus**: "I can break this specification by [attack]. The invariant at [location] fails when [condition]. Concrete attack: [scenario with state trace]."
- **Activation**: Always active in all focus areas; leads when --focus correctness is specified
- **Review Order**: Reviews AFTER Fowler and Nygard; MUST attack every interface contract and guard condition they identified
```

---

### 4.2 SP-3: Mandatory Guard Condition Boundary Table Artifact

**Priority**: Next Cycle (Phase 2)
**Composite Score**: 75.5 / 100 (A-Tier, Rank 6 overall)

#### Functional Requirements

**FR-6**: The spec-panel SHALL produce a Guard Condition Boundary Table as a mandatory output artifact whenever the specification contains conditional logic, threshold checks, boolean guards, or sentinel value comparisons.

**FR-7**: The boundary table SHALL have the following columns for each guard condition:
- Guard expression
- Location (spec section or interface contract)
- Input condition (one row per boundary: zero/empty, one/minimal, typical, maximum/overflow, sentinel value match, legitimate edge case)
- Variable value at that boundary
- Guard result (pass/fail)
- Specified behavior at that boundary
- Status (OK or GAP)

**FR-8**: Any cell marked "GAP" SHALL automatically generate a finding at MAJOR severity minimum.

**FR-9**: Any row where the "Specified behavior" column is blank or states "unspecified" SHALL be classified as at least MAJOR severity.

**FR-10**: The boundary table SHALL be completed before the panel's review is considered done. Incomplete tables SHALL block synthesis output.

**FR-11**: Nygard SHALL lead boundary table construction. Crispin SHALL validate completeness. The adversarial tester (SP-2) SHALL attack each table entry.

#### Non-Functional Requirements

**NFR-4**: The boundary table SHALL add no more than 10% token overhead per invocation.

**NFR-5**: The table format SHALL be structured (markdown table) rather than prose, for downstream consumption by adversarial debate (AD-1) and roadmap (RM-1) commands.

**NFR-6**: The table SHALL be appended to panel output in a dedicated "Mandatory Artifacts" section.

#### Acceptance Criteria

**AC-5**: Given a specification containing the guard `if offset > 0`, When the boundary table is constructed, Then it SHALL include a row for `offset = 0` with the guard result "fail" and SHALL flag this as GAP if no behavior is specified for this case.

**AC-6**: Given a specification containing three distinct guard conditions, When the panel completes review, Then the boundary table SHALL contain entries for all three guards, each with at least four boundary rows (zero, one, typical, max).

**AC-7**: Given a specification containing no conditional logic, guard conditions, or threshold checks, When the panel completes review, Then the boundary table section SHALL state "No guard conditions identified" and SHALL NOT block synthesis.

**AC-8**: Given a boundary table with 2 GAP entries, When synthesis output is generated, Then the synthesis SHALL list both GAPs as findings with MAJOR severity or higher.

#### Interface Contract

Add to `spec-panel.md` after the "Output Formats" section:

```markdown
## Mandatory Output Artifacts

### Guard Condition Boundary Table
**Trigger**: Any specification containing conditional logic, threshold checks, boolean guards, or sentinel value comparisons
**Responsibility**: Nygard (lead construction), Crispin (completeness validation), Whittaker (adversarial attack on entries)
**Format**:
| Guard | Location | Input Condition | Variable Value | Guard Result | Specified Behavior | Status |
|-------|----------|-----------------|----------------|--------------|-------------------|--------|
| [expr] | [section] | Zero / empty | ... | ... | ... | OK/GAP |
| [expr] | [section] | One / minimal | ... | ... | ... | OK/GAP |
| [expr] | [section] | Typical | ... | ... | ... | OK/GAP |
| [expr] | [section] | Maximum / overflow | ... | ... | ... | OK/GAP |
| [expr] | [section] | Sentinel value match | ... | ... | ... | OK/GAP |
| [expr] | [section] | Legitimate edge case | ... | ... | ... | OK/GAP |

**Completion Criteria**:
- Every guard identified by any panelist has a table entry
- Every row is filled (no blank cells)
- All GAP rows have corresponding findings at MAJOR severity minimum
- Table is complete before synthesis output is generated

**Downstream Propagation**: This table is designed for consumption by /sc:adversarial (invariant probe round) and /sc:roadmap (state invariant analysis section). Use structured format for machine parseability.
```

---

### 4.3 SP-1: Correctness Focus Review Pass

**Priority**: Future (Phase 3)
**Composite Score**: 70.5 / 100 (A-Tier, Rank 9 overall)

#### Functional Requirements

**FR-12**: The spec-panel SHALL support a fifth focus area: `--focus correctness`, targeting execution correctness of stateful specifications.

**FR-13**: When `--focus correctness` is activated, the expert panel SHALL consist of: Nygard (lead), Fowler, Adzic, Crispin, Whittaker (adversarial tester).

**FR-14**: Under the correctness focus, each expert SHALL shift their methodology as follows:
- FR-14.1: Wiegers SHALL examine each requirement for implicit state assumptions (e.g., "this collection is non-empty," "this count equals that count").
- FR-14.2: Fowler SHALL trace data flow across every interface, annotating where input counts can diverge from output counts.
- FR-14.3: Nygard SHALL enumerate every guard condition and analyze behavior at each boundary value, including zero and empty.
- FR-14.4: Adzic SHALL write state-annotated scenarios (Given/When/Then/State) for every stateful operation, including degenerate inputs.
- FR-14.5: Crispin SHALL design boundary value tests targeting each guard and invariant.
- FR-14.6: Whittaker SHALL attack each invariant and guard using his five attack methodologies.

**FR-15**: The correctness focus SHALL produce three mandatory outputs:
- FR-15.1: **State Variable Registry** -- A table listing every mutable variable the spec introduces, its type, initial value, invariant, and the operations that read/write it.
- FR-15.2: **Guard Condition Boundary Table** -- As specified in SP-3 (FR-6 through FR-11).
- FR-15.3: **Pipeline Flow Diagram** -- Annotated with counts at each stage (when pipelines are present).

**FR-16**: The spec-panel SHALL auto-suggest `--focus correctness` (via a recommendation in output, not forced activation) when the specification introduces 3 or more mutable state variables, contains guard conditions with numeric thresholds, or describes pipeline/filter operations.

#### Non-Functional Requirements

**NFR-7**: The correctness focus SHALL add no more than 25% token overhead compared to a standard focus area invocation.

**NFR-8**: The auto-suggestion heuristic (FR-16) SHALL have a false positive rate below 30% (i.e., it should not suggest correctness focus for specs that have no meaningful state).

#### Acceptance Criteria

**AC-9**: Given a specification describing a paginated data pipeline with filtering, When `/sc:spec-panel @spec --focus correctness` is invoked, Then the output SHALL contain a State Variable Registry, a Guard Condition Boundary Table, and a Pipeline Flow Diagram annotated with counts.

**AC-10**: Given a specification introducing 4 mutable state variables and 2 guard conditions, When `/sc:spec-panel @spec --focus requirements` is invoked (without correctness), Then the output SHALL include a recommendation suggesting `--focus correctness` for this specification.

**AC-11**: Given a specification with no mutable state, no guard conditions, and no pipelines, When `/sc:spec-panel @spec --focus requirements` is invoked, Then the output SHALL NOT suggest `--focus correctness`.

**AC-12**: Given `--focus correctness` is specified, When the panel reviews a spec containing an interface where Component B's filtering affects Component A's cursor, Then at least one expert (Fowler or Whittaker) SHALL identify the cross-component state feedback as a finding.

#### Interface Contract

Add to the "Focus Areas" section of `spec-panel.md`:

```markdown
### Correctness Focus (`--focus correctness`)
**Expert Panel**: Nygard (lead), Fowler, Adzic, Crispin, Whittaker
**Analysis Areas**:
- State variable inventory and invariant specification
- Guard condition boundary analysis (zero, empty, sentinel, max)
- Pipeline dimensional consistency (input count vs. output count at each stage)
- Cross-component state feedback loops
- Degenerate input trace-through for every stateful operation

**Mandatory Outputs**:
- State Variable Registry (table of all mutable state with invariants)
- Guard Condition Boundary Table (per SP-3 artifact specification)
- Pipeline Flow Diagram (annotated with counts at each stage, when pipelines present)

**Auto-Suggestion**: Panel recommends --focus correctness when the spec introduces 3+ mutable state variables, contains guard conditions with numeric thresholds, or describes pipeline/filter operations.
```

Update the Usage line to include the new focus option:

```markdown
/sc:spec-panel [specification_content|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus requirements|architecture|testing|compliance|correctness] [--iterations N] [--format standard|structured|detailed]
```

---

### 4.4 SP-4: Pipeline Dimensional Analysis Heuristic

**Priority**: Future (Phase 3)
**Composite Score**: 68.5 / 100 (A-Tier, Rank 10 overall)

#### Functional Requirements

**FR-17**: The spec-panel SHALL include a pipeline dimensional analysis heuristic that triggers whenever the specification describes data flowing through 2 or more stages where the output count can differ from the input count (filtering, transformation, aggregation, deduplication).

**FR-18**: When triggered, the heuristic SHALL execute the following steps:
- FR-18.1: **Pipeline Detection** -- Identify spec sections describing multi-stage data flow.
- FR-18.2: **Quantity Annotation** -- At each stage, annotate the count: "N items in, M items out."
- FR-18.3: **Downstream Tracing** -- For every index, offset, cursor, or counter downstream of a filtering/transformation stage, determine whether it uses the pre-stage count or the post-stage count.
- FR-18.4: **Consistency Check** -- Verify that each downstream consumer uses the count from the correct stage. Flag mismatches.

**FR-19**: Any dimensional mismatch SHALL be classified as CRITICAL severity by default, because a dimensional mismatch is always wrong regardless of the values involved.

**FR-20**: Fowler SHALL be responsible for pipeline identification and quantity annotation. The adversarial tester (Whittaker) SHALL attack each annotated stage with divergence attacks.

**FR-21**: The heuristic SHALL produce a Quantity Flow Diagram as output, showing counts at each pipeline stage and annotating which count each downstream consumer uses.

#### Non-Functional Requirements

**NFR-9**: The heuristic SHALL add no more than 5% token overhead when no pipelines are detected in the specification.

**NFR-10**: When pipelines are detected, the heuristic SHALL add no more than 10% additional overhead for diagram construction and analysis.

#### Acceptance Criteria

**AC-13**: Given a specification describing "read N events from store, filter to M widgets, advance cursor," When the pipeline dimensional analysis heuristic runs, Then it SHALL produce a Quantity Flow Diagram showing N events in, M widgets out, and SHALL flag the cursor advancement if it uses M instead of N.

**AC-14**: Given a specification describing a simple CRUD operation with no filtering or transformation stages, When the pipeline dimensional analysis heuristic evaluates the spec, Then it SHALL NOT trigger and SHALL produce no output.

**AC-15**: Given a specification with a dimensional mismatch identified, When the finding is generated, Then it SHALL be classified as CRITICAL severity with a concrete scenario showing incorrect behavior.

#### Interface Contract

Add to `spec-panel.md` after the Mandatory Output Artifacts section:

```markdown
## Review Heuristics

### Pipeline Dimensional Analysis
**Trigger**: Specification describes data flowing through 2+ stages where output count can differ from input count (filtering, transformation, aggregation, deduplication)
**Responsibility**: Fowler (pipeline identification, quantity annotation), Whittaker (divergence attack on each stage)
**Process**:
1. Draw quantity flow diagram with counts at each stage
2. Identify all downstream consumers of any count (indexes, offsets, cursors, counters)
3. For each consumer, verify it uses the count from the correct stage
4. For each mismatch, generate a CRITICAL finding with concrete scenario

**Severity**: Any dimensional mismatch is CRITICAL by default (it is always wrong, not just at boundaries)
**Output**: Quantity Flow Diagram annotated with counts at each pipeline stage
```

---

## 5. Integration Points

### 5.1 Integration with /sc:adversarial

**Artifact propagation (SP-3 to AD-1)**: The guard condition boundary table produced by spec-panel (SP-3) is consumed by the adversarial debate's invariant probe round (AD-1). The probe round verifies SP-3's entries rather than re-deriving boundary conditions. GAP entries from SP-3 become priority targets for AD-1's fault-finder agent.

**Assumption surfacing (SP-2 to AD-2)**: Attack findings from the adversarial tester (SP-2) feed into the adversarial debate's consensus assumption extraction (AD-2). If the adversarial tester identifies an assumption that all panel experts shared (e.g., "the input collection is non-empty"), this becomes a candidate for AD-2's shared assumption list.

**Coverage taxonomy (SP-1 to AD-5)**: The correctness focus (SP-1) aligns with AD-5's debate topic taxonomy Level 3 (state mechanics). When `--focus correctness` produces findings, those findings map directly to AD-5's taxonomy level that must be covered in debate.

### 5.2 Integration with /sc:roadmap

**State variable propagation (SP-3 to RM-1)**: SP-3's guard condition boundary table and SP-1's state variable registry propagate to RM-1's state invariant analysis section in the roadmap. RM-1's table is initialized from SP-3's output, not derived from scratch.

**Pipeline diagrams (SP-4 to RM-3)**: SP-4's quantity flow diagrams feed into RM-3's cross-component state flow tracing. RM-3 extends the analysis to non-pipeline interactions but references SP-4's diagrams for pipeline-specific flows.

**Negative ACs (SP-2 to RM-2)**: The adversarial tester's attack findings inform RM-2's negative acceptance criteria generation. Each attack that identifies a valid failure mode becomes a candidate negative AC in the roadmap.

### 5.3 Artifact Flow Summary

```
spec-panel                    adversarial              roadmap
==========                    ===========              =======
SP-2 (Attack findings) -----> AD-2 (Assumption list)
SP-3 (Boundary table) ------> AD-1 (Invariant probe)-> RM-1 (State invariant table)
SP-1 (Correctness findings)-> AD-5 (Taxonomy L3)
SP-4 (Quantity flow) -------> RM-3 (State flow tracing)
SP-2 (Attack scenarios) ----> RM-2 (Negative ACs)
```

---

## 6. Implementation Phasing

### Phase 1: Adversarial Mindset (Immediate, 1-3 days)

| Step | Action | Effort |
|------|--------|--------|
| 1 | Define James Whittaker adversarial tester persona in `spec-panel.md` Expert Panel System | 2 hours |
| 2 | Add adversarial tester to the expert review sequence (after Fowler and Nygard) | 1 hour |
| 3 | Add "Adversarial Analysis" section to all output format examples | 1 hour |
| 4 | Update the Boundaries section to reflect the new expert count (11 simulated experts) | 30 min |
| 5 | Validate: Run spec-panel on the v0.04 specification and verify adversarial tester catches both bug classes | 4 hours |

**Expected overhead**: ~5-10% additional tokens per invocation.
**Dependencies**: None. SP-2 is fully standalone.

### Phase 2: Structural Forcing Functions (Next Cycle, 3-5 days)

| Step | Action | Effort |
|------|--------|--------|
| 1 | Add Mandatory Output Artifacts section to `spec-panel.md` | 2 hours |
| 2 | Define guard condition boundary table template and completion criteria | 2 hours |
| 3 | Add table trigger detection logic (conditional logic, threshold checks, guards) | 2 hours |
| 4 | Integrate adversarial tester (SP-2) as validator of boundary table entries | 1 hour |
| 5 | Define downstream propagation format for AD-1 and RM-1 consumption | 2 hours |
| 6 | Validate: Run spec-panel on v0.04 specification and verify all guards produce table entries with GAPs identified | 4 hours |

**Expected overhead**: ~10% additional tokens per invocation (cumulative ~15-20% with Phase 1).
**Dependencies**: SP-2 (Phase 1) must be complete for the adversarial validation of table entries.

### Phase 3: Depth and Breadth (Future, after Phase 1-2 validation, 5-8 days)

| Step | Action | Effort |
|------|--------|--------|
| 1 | Add `--focus correctness` to the Focus Areas section of `spec-panel.md` | 4 hours |
| 2 | Define modified expert behaviors under correctness focus (FR-14.1 through FR-14.6) | 4 hours |
| 3 | Add State Variable Registry template and completion criteria | 2 hours |
| 4 | Add Pipeline Flow Diagram output specification | 2 hours |
| 5 | Implement auto-suggestion heuristic for correctness focus (FR-16) | 2 hours |
| 6 | Add Pipeline Dimensional Analysis heuristic to Review Heuristics section | 2 hours |
| 7 | Define pipeline detection trigger and quantity annotation process | 2 hours |
| 8 | Update Usage line to include `correctness` in focus options | 30 min |
| 9 | Validate: Run spec-panel with `--focus correctness` on v0.04 spec and verify all three mandatory outputs are produced with dimensional mismatch flagged as CRITICAL | 4 hours |

**Expected overhead**: ~20-25% additional tokens when `--focus correctness` is active; ~5% when not active (pipeline heuristic detection only). Cumulative with Phase 1-2: ~20-25% for non-correctness invocations, ~35-45% for correctness-focused invocations.
**Dependencies**: SP-2 (Phase 1) and SP-3 (Phase 2) must be complete. The correctness focus area references both the adversarial tester and the boundary table.

---

## 7. Risks & Mitigations

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| R-1 | **Correctness theater**: Forcing functions produce formulaic, low-quality entries that satisfy structural requirements without genuine analysis | Medium | High | SP-2 (adversarial tester) validates boundary table entries. Track ratio of GAP findings to total entries; investigate if ratio drops below 10% consistently. |
| R-2 | **Cumulative overhead exceeds tolerance**: All four proposals together push token usage beyond the 40% ceiling | Medium | Medium | Phase implementation with measurement. Phase 1 alone adds 5-10%. If Phase 2 pushes past 25%, defer Phase 3. Correctness focus is opt-in, not default. |
| R-3 | **Context window competition**: Boundary tables and quantity flow diagrams consume context needed for deeper expert analysis | Low | Medium | Artifacts use concise structured formats (tables, not prose). Downstream consumers receive summary versions. |
| R-4 | **Adversarial tester produces false positives**: The destructive mindset generates excessive findings for well-specified systems | Medium | Low | Findings require concrete attack scenarios with state traces. Vague or hypothetical attacks are filtered during synthesis. Severity classification gates low-confidence findings. |
| R-5 | **Pipeline detection heuristic under-triggers**: Complex data flows are not recognized as pipelines by the trigger condition | Low | Medium | Trigger condition is intentionally broad ("data flowing through 2+ stages where output count can differ from input count"). Manual activation via `--focus correctness` as fallback. |
| R-6 | **Expert persona bloat**: Adding Whittaker brings the panel to 11 experts, increasing cognitive load on the orchestrating prompt | Low | Low | Whittaker is focused and specialized. His review runs after Fowler and Nygard, attacking their output, so he does not require independent specification analysis. Token cost is bounded by FR count. |

---

## 8. NOT Doing

### SP-5: Mandatory Cross-Expert Challenge Protocol (57.5, B-Tier) -- DEFERRED

**What it proposed**: Replace the sequential-review-then-synthesis workflow with a structured challenge protocol where specific expert pairs attack each other's findings.

**Why it is deferred**:

1. **B-Tier score (57.5)**: Below the A-Tier threshold of 65. The adversarial debate scored it as having high overhead (20-30%) for an indirect mechanism that does not add new analytical techniques.
2. **Dependency on SP-2**: The challenge protocol is most valuable when the adversarial tester is available as a challenger. SP-5 should be evaluated only after SP-2 has been validated through at least one development cycle.
3. **Overhead concern**: Adding a full challenge round after the initial review pass nearly doubles the review time. The debate verdict noted this conflicts with the design principle of "adding 15-20 minutes of focused analysis, not doubling the review time."
4. **Indirect bug-catching mechanism**: SP-5 ensures existing perspectives are compositionally applied but does not introduce new analysis. The direct mechanisms (SP-2's attacks, SP-3's boundary table, SP-4's dimensional analysis) are more cost-effective at catching bugs.

**Revisit conditions**: Implement SP-5 if (a) SP-2 proves effective and a natural pairing emerges, (b) bugs are observed that escaped because experts reviewed in silos despite having relevant findings, or (c) `--mode critique` is extended to support structured challenge rounds as a pilot.

### Items Never Proposed

The following items were considered during brainstorming but not elevated to formal proposals:

- **Formal verification integration**: Using model checking or theorem proving on specifications. Rejected as too heavyweight for the spec-panel's workflow and inappropriate for natural-language specifications.
- **Automated test generation from boundary tables**: Generating executable test cases from SP-3's GAP entries. Deferred as a separate command enhancement, not a spec-panel concern.
- **Real-time specification simulation**: Executing the specification's state machine to find violations. Rejected as requiring a specification language beyond what the panel reviews (natural language and structured specs, not executable models).

---

## 9. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| **Primary**: State-boundary bugs caught during spec review (before implementation) | >80% catch rate for boundary condition bugs | Retrospective analysis: re-run enhanced panel on past specs where bugs were later found |
| **Secondary**: GAP cells in boundary tables per review | >0 for specs with guard conditions | Count GAP entries in panel output |
| **Secondary**: Adversarial tester findings per review | 2+ findings for specs with mutable state | Count attack findings in panel output |
| **Tertiary**: Overhead per invocation | <25% increase (Phase 1+2), <40% increase (Phase 3 with correctness focus) | Token count comparison with baseline |
| **Quality**: Formulaic output ratio | <50% of boundary table entries are trivially obvious | Manual audit of boundary table quality quarterly |

---

## 10. Glossary

| Term | Definition |
|------|-----------|
| Guard condition | A conditional check that controls execution flow (e.g., `if offset > 0`) |
| Boundary value | A value at the edge of a guard condition's threshold (zero, one, max, sentinel) |
| Pipeline dimensional mismatch | A bug where downstream state uses the count from the wrong pipeline stage |
| Sentinel collision | When a variable legitimately holds the value a guard uses as its "special" check value |
| Degenerate input | A valid input that is at the extreme of the expected range (empty, zero, maximum) |
| Correctness theater | Formulaic completion of correctness artifacts without genuine analytical reasoning |
| Forcing function | A structural mechanism that makes it impossible to skip specific reasoning |

---

*Release specification completed 2026-03-04. This document is self-contained and suitable for handoff to an implementing agent.*
