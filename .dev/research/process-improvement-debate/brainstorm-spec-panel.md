# Brainstorm: Improving /sc:spec-panel to Catch State-Machine Edge Cases

**Agent**: Brainstorm Agent (Opus 4.6)
**Date**: 2026-03-04
**Input**: v0.04 post-implementation retrospective, spec-panel command definition, persona system
**Scope**: General-purpose methodology improvements to the /sc:spec-panel command

---

## Part 1: Analysis of the 6 Questions

### Q1: Expert Methodology Gaps -- Which personas should have caught these bugs?

**Michael Nygard** was the most obvious candidate. His persona description says he focuses on "failure modes" and asks "What happens when this component fails?" But his methodology (circuit breaker patterns, operational excellence) is oriented toward *runtime infrastructure failures* -- network timeouts, service unavailability, cascading outages. He is not prompted to examine *logical state-machine failures* where the code runs without errors but produces incorrect state transitions. The word "fails" in his critique focus implies something throws an exception or becomes unavailable, not that a guard variable silently holds the wrong value.

**Lisa Crispin** should have caught these through edge case analysis. Her persona says "What are the edge cases and failure scenarios?" But her methodology (whole-team testing, risk-based testing) operates at the *test strategy* level, not at the *state-trace* level. She would ask "do we have tests for when the event list is empty?" but not "does the cursor advance by the right count when the filter removes items?" The former is a testing coverage question; the latter is a correctness-of-logic question.

**Martin Fowler** should have caught the interface contract issues. His focus on interface segregation and bounded contexts means he examines the seams between components. But his current framing is architectural -- "does this interface violate SRP?" -- rather than mechanical -- "does data flowing across this interface preserve the invariants that both sides depend on?"

**Gojko Adzic** was closest to catching these through concrete examples. His Given/When/Then methodology naturally surfaces edge cases when examples are sufficiently diverse. But the methodology as currently prompted produces *behavioral* examples (user does X, system does Y) without requiring *state-level* examples (after Y, variable Z has value W). The behavioral examples can all pass while the internal state is wrong.

**Gap diagnosis**: The panel's expert prompts are oriented toward *document quality* (requirements clarity, architectural soundness, test coverage strategy) rather than *execution correctness* (state transitions, guard completeness, pipeline dimensional consistency). No expert is explicitly tasked with asking: "Trace this variable through execution. What is its value at each boundary?"

### Q2: Structural Review Gaps -- Does the panel probe state-machine invariants?

No. The panel's four focus areas are:

1. **Requirements** (`--focus requirements`): Clarity, completeness, testability, stakeholder alignment
2. **Architecture** (`--focus architecture`): Interface design, boundaries, scalability, patterns
3. **Testing** (`--focus testing`): Strategy, coverage, edge cases, acceptance criteria
4. **Compliance** (`--focus compliance`): Regulatory, security, operational, audit

None of these focus areas includes:

- **State invariant verification**: "What must always be true about this variable?"
- **Guard condition completeness**: "Does this guard hold at every boundary value?"
- **Cross-component state feedback**: "Does component B's filtering affect component A's cursor?"
- **Pipeline dimensional analysis**: "Which count drives this index -- input count or output count?"

These are not exotic concerns. They are standard techniques from formal methods (invariant specification), boundary value analysis (testing theory), and data flow analysis (compiler theory). Their absence from the panel's structural review is the primary systemic gap.

### Q3: Review Checklist Additions

The following checklist items would force examination of the missed bug classes:

**Guard condition audit**:
- For every conditional branch: What happens when the tested expression equals the sentinel/boundary value?
- For every `> 0` check: What if the value is legitimately 0?
- For every emptiness check: Can the collection be empty through a valid code path?

**State tracking divergence audit**:
- For every pipeline with filtering: Does the downstream consumer use the pre-filter count or post-filter count?
- For every index/offset/cursor: What quantity drives its advancement? Is that quantity the right one?
- For every counter: Does it count the thing it claims to count, or a proxy?

**Cross-component feedback audit**:
- For every interface between components: Can the callee's behavior change the caller's state assumptions?
- For every shared mutable variable: Do all writers agree on the invariant?
- For every callback or event: Can the handler invalidate the caller's postconditions?

### Q4: Expert Interaction Patterns -- Should cross-expert challenges be mandatory?

Yes, with a specific structural change. The current panel workflow is essentially:

```
Expert 1 reviews -> Expert 2 reviews -> ... -> Expert N reviews -> Synthesis
```

Each expert reviews the spec through their own lens. Cross-expert commentary exists in `--mode discussion` but is collaborative (building on insights), not adversarial (challenging assumptions).

The missing interaction pattern is **handoff-with-challenge**:

```
Fowler reviews interfaces -> Nygard MUST probe each interface's failure modes
Crispin identifies edge cases -> Adzic MUST write concrete state-trace examples for each
Wiegers reviews requirements -> Adversarial Tester MUST attempt to break each requirement
```

This is not the same as "discussion." Discussion allows experts to volunteer observations. Handoff-with-challenge *requires* a specific expert to attack the previous expert's output using their specialized methodology.

### Q5: Mode Enhancements -- Should there be a state-machine analysis mode?

Yes, but it should be framed more broadly than "state-machine analysis." The right framing is **`--mode invariant-probe`** or **`--focus correctness`** -- a mode that shifts the entire panel from document-quality review to execution-correctness review.

In this mode:
- Wiegers would examine each requirement for implicit state assumptions
- Fowler would trace data flow across every interface, noting where counts diverge
- Nygard would enumerate failure modes of every guard condition
- Adzic would write state-annotated examples (Given/When/Then/State)
- Crispin would design boundary value tests for every guard
- A new adversarial persona would attempt to break each invariant

This mode should be automatically suggested (not mandatory) whenever the spec introduces mutable state, guard conditions, or pipeline transformations.

### Q6: Structural Output Requirements -- Should mandatory artifacts be produced?

Yes. The panel currently produces: expert commentary, recommendations, priority rankings, quality scores. It does not produce any artifact that forces reasoning about state correctness. Two mandatory artifacts would close this gap:

1. **State Variable Registry**: A table listing every mutable variable the spec introduces, its type, its initial value, its invariant, and the operations that read/write it.

2. **Guard Condition Boundary Table**: For every conditional/guard in the spec, a table showing behavior at each boundary value (zero, one, typical, max, sentinel).

These artifacts are valuable not because someone reads them later, but because the act of constructing them forces the reasoning that catches the bugs.

---

## Part 2: Proposals

### Proposal 1: Add Mandatory "Correctness Focus" Review Pass

**Description**: Add a fifth focus area (`--focus correctness`) to the spec-panel's existing four (requirements, architecture, testing, compliance). This focus area specifically targets execution correctness of stateful specifications. When activated, the panel shifts from reviewing *document quality* to verifying *execution soundness*.

The correctness focus activates a modified expert panel behavior:
- **Wiegers**: Identifies every implicit assumption in requirements (e.g., "this collection is non-empty," "this count equals that count")
- **Fowler**: Traces data flow across every interface, annotating where input counts can diverge from output counts
- **Nygard**: Enumerates every guard condition and asks what happens at each boundary value, especially zero and empty
- **Adzic**: Writes state-annotated scenarios (Given/When/Then/State) for every stateful operation, including degenerate inputs
- **Crispin**: Designs boundary value tests targeting each guard and invariant

**Rationale**: The current focus areas are oriented toward document quality (clarity, completeness, testability) and architectural soundness (boundaries, patterns, scalability). Neither is oriented toward answering: "If I run this specification, will the state transitions be correct at every boundary?" This is a fundamentally different question that requires a different analytical lens. By making it an explicit focus area, the panel is structurally required to address it rather than hoping individual experts volunteer relevant observations.

**Expected Impact**: High. This directly addresses the root cause: the panel had no mechanism to force invariant reasoning about mutable state. Every bug in the missed class (guard bypasses, cursor stalls, counter divergence) would be examined by at least two experts under this focus area.

**Implementation Sketch**:
```
## Correctness Focus (`--focus correctness`)
**Expert Panel**: Nygard (lead), Fowler, Adzic, Crispin
**Analysis Areas**:
- State variable inventory and invariant specification
- Guard condition boundary analysis (zero, empty, sentinel, max)
- Pipeline dimensional consistency (input count vs. output count at each stage)
- Cross-component state feedback loops
- Degenerate input trace-through for every stateful operation

**Mandatory Outputs**:
- State Variable Registry (table of all mutable state with invariants)
- Guard Condition Boundary Table (behavior at each boundary value)
- Pipeline Flow Diagram (annotated with counts at each stage)
```

Auto-activation heuristic: suggest `--focus correctness` when the spec introduces 3+ mutable state variables, contains guard conditions with numeric thresholds, or describes pipeline/filter operations.

---

### Proposal 2: Introduce Adversarial Tester Expert Persona

**Description**: Add a new expert persona to the panel: an **Adversarial Tester** modeled on James Whittaker's "How to Break Software" methodology and chaos engineering principles. This persona's sole objective is to find inputs, sequences, and conditions that violate the spec's stated or implied guarantees. Unlike Crispin (who designs test strategies) and Adzic (who writes behavioral examples), the Adversarial Tester actively attacks the specification.

The Adversarial Tester's review protocol:
1. **Zero/Empty Attack**: For every input, function argument, and collection: what if it is zero, empty, null, or negative?
2. **Divergence Attack**: For every pipeline/transformation: what if the output count differs from the input count?
3. **Sentinel Collision Attack**: For every guard condition: what if the variable legitimately holds the sentinel value the guard checks against?
4. **Sequence Attack**: For every operation: what if it is called twice, never called, called out of order, or called concurrently?
5. **Accumulation Attack**: For every counter/offset/cursor: what if accumulated drift causes it to be wrong after N operations?

**Critique Focus**: "I can break this specification by providing [X]. The guard at [Y] fails because [Z]. Here is the concrete attack scenario."

**Rationale**: The current panel is constructive. Every expert asks "is this spec good enough?" The adversarial tester asks "how do I make this spec fail?" This is a fundamentally different cognitive mode. Research on code review effectiveness shows that reviewers who are explicitly asked to find bugs find significantly more than reviewers asked to evaluate quality. The same principle applies to specification review.

The existing panel correctly identified missing requirements, testability gaps, and architectural concerns. These are *quality* issues. The missed bugs were *correctness* issues -- specifications that were clearly written, architecturally sound, and testable, but that contained logical errors at state boundaries. An adversarial mindset naturally gravitates toward exactly these boundaries.

**Expected Impact**: High. The adversarial tester would have directly attacked both missed bugs:
- Bug 1: "What if I filter all events in a page? Cursor advances by zero. PageUp loops forever."
- Bug 2: "What if tail_events is empty? Offset is 0. Guard `> 0` fails. Replay runs again."

More broadly, the adversarial mindset catches any bug arising from degenerate inputs, boundary conditions, or unexpected legitimate states. This is a large class that includes most state-machine bugs.

**Implementation Sketch**:
```yaml
# Addition to spec-panel.md Expert Panel System

### Adversarial Analysis Expert

**James Whittaker** - Adversarial Testing Pioneer
- **Domain**: Attack surface analysis, boundary exploitation,
  degenerate input generation, guard condition probing
- **Methodology**: Zero/empty attacks, divergence attacks,
  sentinel collision, sequence abuse, accumulation drift
- **Critique Focus**: "I can break this specification by [attack].
  The invariant at [location] fails when [condition].
  Concrete attack: [scenario with state trace]."
- **Activation**: Always active when --focus correctness;
  available in all other focus areas
- **Interaction Pattern**: Reviews AFTER Fowler and Nygard;
  MUST attack every interface contract and guard condition
  they identified
```

---

### Proposal 3: Mandatory Guard Condition Boundary Table Artifact

**Description**: Add a structural output requirement to the spec-panel: for every guard condition, threshold check, or conditional branch identified in the specification, the panel MUST produce a **boundary value table** showing the behavior at each boundary. The table is a mandatory artifact that must be completed before the panel's review is considered done.

Table format:
```
Guard: [expression]
Location: [spec section or interface contract]
| Input condition         | Variable value | Guard result | Specified behavior | Status    |
|-------------------------|---------------|--------------|-------------------|-----------|
| Zero / empty            | ...           | ...          | ...               | OK / GAP  |
| One / minimal           | ...           | ...          | ...               | OK / GAP  |
| Typical                 | ...           | ...          | ...               | OK / GAP  |
| Maximum / overflow      | ...           | ...          | ...               | OK / GAP  |
| Sentinel value match    | ...           | ...          | ...               | OK / GAP  |
| Legitimate edge case    | ...           | ...          | ...               | OK / GAP  |
```

Any cell marked "GAP" becomes a finding. Any cell where the "Specified behavior" column is blank or says "unspecified" is automatically classified as at least MAJOR severity.

**Rationale**: The power of this artifact is not in reading it -- it is in *constructing* it. The act of filling in the table forces the reviewer to answer "what happens at zero?" for every guard. This is the exact question that would have caught both missed bugs. The table makes it structurally impossible to skip this question.

Current panel output is narrative (expert commentary) and evaluative (quality scores). Neither format forces the reviewer to enumerate boundary values. The boundary table is a *generative* artifact -- it creates new information about the spec that did not exist before the review.

This approach is grounded in boundary value analysis, one of the most effective defect detection techniques in software testing. Studies consistently show that boundary conditions account for a disproportionate share of software defects (estimates range from 25-50% of all defects). Yet the current spec-panel has no mechanism to systematically surface them.

**Expected Impact**: Medium-High. Directly catches any bug where a guard condition fails at a boundary the spec author did not consider. This includes Bug 2 (offset = 0 when tail is empty) and partially catches Bug 1 (mounted = 0 when all events are filtered, though the dimensional mismatch is better caught by Proposal 4).

**Implementation Sketch**:
```
## Mandatory Output Artifacts

### Guard Condition Boundary Table
**Trigger**: Any specification containing conditional logic, threshold checks,
  boolean guards, or sentinel value comparisons
**Responsibility**: Nygard (lead) with Crispin validation
**Format**: [table template as above]
**Completion Criteria**:
  - Every guard identified by any panelist has a table entry
  - Every row is filled in (no blank cells)
  - All GAP rows have corresponding findings in the review
**Integration**: Table is appended to panel output;
  GAP rows auto-generate findings at MAJOR severity minimum
```

---

### Proposal 4: Pipeline Dimensional Analysis Heuristic

**Description**: Add a mandatory review heuristic triggered whenever the spec describes a data pipeline where input count can differ from output count: **the panel must produce a quantity flow annotation showing which count is used at each downstream step, and must flag any step that uses the wrong count.**

The heuristic works by:
1. **Pipeline Detection**: Identify any spec section describing data flowing through stages (read -> filter -> transform -> consume)
2. **Quantity Annotation**: At each stage, annotate the count: "N items in, M items out"
3. **Downstream Tracing**: For every index, offset, cursor, or counter downstream of a filtering/transformation stage, ask: "Does this use the pre-stage count (N) or the post-stage count (M)?"
4. **Consistency Check**: Verify that each downstream consumer uses the count from the correct stage

```
Quantity Flow Diagram:

  EventStore ──[N events]──> _create_replay_widget() ──[M widgets (M<=N)]──> mount()
                                                                                |
                                                          _loaded_start_index -= ???

  Question: Does _loaded_start_index advance by N (events consumed) or M (widgets mounted)?
  If M: cursor stalls when M < N (filtering removes events)
  If N: correct behavior
```

**Rationale**: Bug 1 is a textbook instance of pipeline dimensional inconsistency: the cursor indexes the input (event store) but advances by the output count (mounted widgets). This is a common and pernicious bug class in any system with filtering, transformation, or aggregation stages. The analogy is dimensional analysis in physics -- if you mix meters and seconds, you get a wrong answer. If you mix event-counts and widget-counts, you get a cursor that stalls.

This heuristic is distinct from the guard condition boundary table (Proposal 3). The boundary table catches bugs where a guard fails at a specific value. The dimensional analysis catches bugs where the wrong *quantity* is being used, regardless of its value. Bug 1 is wrong even when `mounted > 0` -- it is always wrong because it uses the wrong count. The boundary table would only catch it when `mounted = 0` (the degenerate case).

**Expected Impact**: Medium. Highly targeted at a specific bug class (dimensional mismatches in pipelines) but that class is common in paginated systems, data processing pipelines, ETL workflows, scroll/viewport implementations, and any code involving filters with downstream state. Catches Bug 1 directly. Partially relevant to Bug 2 (the "quantity" is the length of tail_events, which drives the offset).

**Implementation Sketch**:
```
## Review Heuristics

### Pipeline Dimensional Analysis
**Trigger**: Specification describes data flowing through 2+ stages
  where output count can differ from input count (filtering,
  transformation, aggregation, deduplication)
**Responsibility**: Fowler (identification) + Adversarial Tester (attack)
**Process**:
  1. Draw quantity flow diagram with counts at each stage
  2. Identify all downstream consumers of any count
  3. For each consumer, verify it uses the count from the correct stage
  4. For each mismatch, generate a finding showing the concrete
     scenario where the wrong count causes incorrect behavior
**Severity**: Any dimensional mismatch is CRITICAL by default
  (it is always wrong, not just at boundaries)
```

---

### Proposal 5: Mandatory Cross-Expert Challenge Protocol

**Description**: Replace the current sequential-review-then-synthesis workflow with a structured **challenge protocol** where specific expert pairs are required to attack each other's findings. After the initial review pass, the panel enters a challenge round where:

1. **Fowler -> Nygard**: Every interface contract Fowler identifies must be probed by Nygard for failure modes. "Fowler says this interface is clean. Nygard: how does it fail?"
2. **Nygard -> Adversarial Tester**: Every failure mode Nygard identifies must be attacked by the Adversarial Tester with concrete degenerate inputs. "Nygard says this guard protects against re-entry. Adversarial Tester: break it."
3. **Adzic -> Crispin**: Every behavioral example Adzic writes must be extended by Crispin with boundary value variations. "Adzic's example uses 50 events. Crispin: what happens with 0, 1, and MAX_INT?"
4. **Wiegers -> Fowler**: Every requirement Wiegers validates must be checked by Fowler for implicit coupling. "Wiegers says FR-4 is well-specified. Fowler: does FR-4's implementation affect FR-5's state?"

**Rationale**: The current panel's `--mode discussion` allows collaborative commentary but does not *require* adversarial challenge. The missed bugs lived in the gaps between expert domains: Fowler reviewed the interface (correct) but did not probe its failure modes (Nygard's job). Nygard reviewed operational failure modes (correct) but did not probe logical state-machine failures (nobody's job). The challenge protocol ensures that every expert's output is stress-tested by the expert best positioned to find its weaknesses.

This is modeled on the concept of "red team / blue team" in security and on the formal inspection process where different reviewers have mandatory roles (moderator, reader, tester, author). The key insight is that *structured disagreement* finds more defects than *collaborative agreement*.

**Expected Impact**: Medium. This does not add new analytical techniques (those are covered by Proposals 1-4). What it does is ensure that existing expert perspectives are *compositionally applied* rather than operating in silos. The challenge protocol would have forced Nygard to probe Fowler's interface contracts for state-machine failure modes, which is exactly the gap that allowed both bugs to escape.

**Implementation Sketch**:
```
## Expert Interaction Protocol

### Challenge Round (after initial review)
**Structure**: Mandatory pairwise challenges between specific expert pairs.
  Each challenge must produce:
  - The claim being challenged (from the first expert's review)
  - The attack vector (from the challenging expert's methodology)
  - The outcome: claim survives, claim needs modification, or new finding generated

**Challenge Pairs**:
| Expert A (claim) | Expert B (challenger) | Challenge Focus |
|------------------|-----------------------|-----------------|
| Fowler (interfaces) | Nygard (failure modes) | How does each interface fail? |
| Nygard (guards) | Adversarial Tester | Can each guard be bypassed? |
| Adzic (examples) | Crispin (boundaries) | What happens at boundary values? |
| Wiegers (requirements) | Fowler (coupling) | Does this requirement affect other state? |

**Integration**: Challenge round runs after initial expert review,
  before synthesis. Challenge findings are added to the panel output
  with the tag [CHALLENGE-FINDING] to distinguish from initial review findings.
```

---

## Part 3: Summary and Prioritization

| # | Proposal | Bug Class Targeted | Catches Bug 1? | Catches Bug 2? | Cost | Independence |
|---|----------|-------------------|-----------------|-----------------|------|-------------|
| 1 | Correctness Focus Pass | All state-machine edge cases | Yes | Yes | Medium | Standalone |
| 2 | Adversarial Tester Persona | Degenerate inputs, guard bypasses | Yes | Yes | Low | Standalone |
| 3 | Guard Boundary Table | Guard failures at boundaries | Partially | Yes | Low | Best with #1 |
| 4 | Pipeline Dimensional Analysis | Count mismatches in pipelines | Yes | Partially | Low | Standalone |
| 5 | Cross-Expert Challenge Protocol | Gaps between expert domains | Indirectly | Indirectly | Medium | Best with #2 |

### Recommended Implementation Order

**Phase 1 -- Immediate, highest ROI**:
- **Proposal 2 (Adversarial Tester Persona)**: Low cost, high impact. Adding one persona with a destructive mindset directly addresses the root cause -- the panel is entirely constructive. This is the single change most likely to catch bugs in this class.
- **Proposal 3 (Guard Boundary Table)**: Low cost, forces the specific reasoning that catches boundary bugs. Can be added as a mandatory output artifact without changing the panel's structure.

**Phase 2 -- Structural enhancement**:
- **Proposal 1 (Correctness Focus Pass)**: Medium cost, but provides the structural framework for the other proposals. The correctness focus area gives the adversarial tester a home, gives the boundary table a trigger, and gives the dimensional analysis a context.
- **Proposal 4 (Pipeline Dimensional Analysis)**: Low cost, targeted at a specific and common bug class. Natural fit within the correctness focus area.

**Phase 3 -- Interaction model upgrade**:
- **Proposal 5 (Cross-Expert Challenge Protocol)**: Medium cost, requires restructuring the panel workflow. Most valuable after the adversarial tester is added (giving the challenge protocol a strong challenger). Should be piloted in `--mode critique` before being generalized.

### Design Principles for All Proposals

1. **Generality**: Every proposal targets a *class* of bugs, not a specific bug. They apply to any specification involving mutable state, guard conditions, or data pipelines.

2. **Structural forcing**: The proposals work by making it *structurally impossible* to skip the reasoning that catches bugs, rather than hoping reviewers volunteer the right questions. Tables must be filled. Challenges must be answered. Counts must be traced.

3. **Composability**: The proposals are independent and can be implemented incrementally. Each adds value alone; together they provide defense in depth.

4. **Low ceremony**: The proposals add targeted artifacts (tables, diagrams) and specific expert behaviors (attacks, challenges), not heavyweight processes. The goal is to add 15-20 minutes of focused analysis, not to double the review time.

5. **Measurability**: Success can be measured by tracking how many GAP cells and CHALLENGE-FINDING items are generated per review, and whether those findings correspond to bugs found later in implementation.

---

*Generated 2026-03-04 by Brainstorm Agent as input to the process-improvement adversarial debate.*
