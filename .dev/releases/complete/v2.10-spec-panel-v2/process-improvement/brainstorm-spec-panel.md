# Brainstorm: Improving sc:spec-panel to Catch Implementation-Level Bugs

**Context**: The v0.04 Adaptive Replay panel review (Wiegers, Nygard, Fowler, Crispin, Adzic, Cockburn) caught 2 CRITICAL and 18 MAJOR findings but missed two bugs that surfaced during implementation. Both bugs involved state-machine invariants that the spec described at the interface level but never traced through edge-case execution paths.

**Root Cause Pattern**: The panel reviews specifications as *documents* — checking clarity, completeness, consistency, and testability of stated requirements. It does not simulate *execution* — tracing state transitions, enumerating boundary values for guard conditions, or asking "what is the value of variable X when condition Y holds?" The two escaped bugs both lived in the gap between "what the spec says the interface does" and "what happens when the implementation runs through a degenerate input."

---

## Proposal 1: State Machine Trace-Through Pass

### Description

Add a dedicated review pass where one or more panelists must identify every piece of mutable state introduced or modified by the specification, then trace each state variable through all code paths — including degenerate inputs — to verify that invariants hold. This is distinct from the existing architecture review, which examines interface contracts and separation of concerns. The trace-through pass examines *runtime behavior of state*.

The pass should be structured as:

1. **State Inventory**: List every mutable variable the spec introduces or modifies (e.g., `_replayed_event_offset`, `_loaded_start_index`, `_prepend_in_progress`).
2. **Invariant Extraction**: For each variable, state the invariant it must maintain (e.g., "cursor must advance by the number of events consumed from the store, not the number of widgets mounted").
3. **Path Enumeration**: For each variable, enumerate the code paths that read or write it.
4. **Degenerate Input Walk**: For each path, ask: "What value does this variable have when the input is empty, maximal, filtered, or produces zero output?"

### Mechanism

Forces reviewers to shift from reviewing *what the spec says* to simulating *what the code does*. By requiring explicit invariant statements, the pass creates artifacts that are absent from typical specifications — and whose absence is precisely what allowed Bug 1 and Bug 2 to escape.

### Example: How It Catches Bug 1

The state inventory identifies `_loaded_start_index`. The invariant extraction step forces the reviewer to ask: "By how much does this index decrement per page load?" The spec says "by widget count (mounted)." The degenerate input walk asks: "What happens when some events are filtered and mounted < events_consumed?" The reviewer discovers that the cursor stalls and PageUp reprocesses the same slice indefinitely.

### Example: How It Catches Bug 2

The state inventory identifies `_replayed_event_offset`. The invariant extraction step asks: "What is the initial value?" Answer: `len(plan.tail_events)`. The degenerate input walk asks: "What is the value when tail_events is empty?" Answer: 0. The path enumeration shows the guard condition is `> 0`. The reviewer sees that the guard fails to catch replay when tail is empty.

### Generality

Catches any bug class where:
- A variable's value depends on a computation that can return zero or a degenerate result.
- A guard condition assumes a non-degenerate initial state.
- Two related variables (e.g., "events consumed" vs. "widgets mounted") diverge under filtering.
- An index or offset fails to advance, causing infinite loops or repeated processing.

This covers off-by-one errors, stale cursor bugs, guard bypass via zero-length collections, and counter divergence under filtering — a large class of state-management bugs.

---

## Proposal 2: Boundary Value Obligation on Every Guard Condition

### Description

Require that every guard condition, threshold check, or conditional branch in the specification be accompanied by a **boundary value table** listing the behavior at each boundary. The table must include at minimum: zero, one, typical, maximum, and "just past maximum." If the spec introduces a boolean or numeric guard (e.g., `offset > 0`, `mounted < page_size`, `index >= 0`), the panel must demand the table before the finding is marked resolved.

Format:

```
Guard: _replayed_event_offset > 0
| Condition            | offset value | Guard result | Behavior          |
|----------------------|-------------|--------------|-------------------|
| Empty tail           | 0           | False        | ??? (unspecified!) |
| Single event tail    | 1           | True         | Guard catches it  |
| Typical tail         | 50          | True         | Guard catches it  |
```

### Mechanism

Makes the "what happens at zero?" question structurally unavoidable. The current panel reviews acceptance criteria, which tend to describe the happy path. Boundary value tables force the spec author and reviewers to enumerate the edges. When a cell says "???" or "unspecified," it becomes a finding.

### Example: How It Catches Bug 2

The guard `_replayed_event_offset > 0` triggers the boundary value obligation. The reviewer fills in the table. The "empty tail" row produces offset = 0, guard = False, and the behavior column is blank. This is immediately flagged as a gap.

### Example: How It Catches Bug 1

The implicit guard in `load_older_events()` — "advance cursor by `mounted`" — triggers a boundary table for `mounted`. The "all events filtered" row produces mounted = 0, cursor advance = 0, and the behavior is "cursor does not advance; next page load reads same slice." Flagged as infinite loop risk.

### Generality

Catches any bug where a guard condition fails at a boundary that the spec author considered impossible or did not consider at all. This includes:
- Off-by-one errors in loop termination.
- Division by zero when a denominator is unexpectedly zero.
- Empty collection guards that use `> 0` instead of `>= 0` (or vice versa).
- Overflow/underflow at maximum values.
- Race conditions triggered only when a counter reaches zero.

---

## Proposal 3: Adversarial Tester Persona

### Description

Add a seventh panelist: an **Adversarial Tester** persona modeled after James Whittaker (author of *How to Break Software*) or a chaos engineering specialist. This persona's sole objective is to find inputs, sequences, and environmental conditions that break the specified behavior. Unlike Lisa Crispin's testing perspective (which focuses on coverage, strategy, and quality assurance), the adversarial tester focuses on *attack vectors against the spec itself*.

The adversarial tester's review protocol:

1. **Input Degeneration**: For every input to every function, ask: "What if this is empty? Null? Maximum? Negative? The wrong type? Contains duplicates?"
2. **Sequence Abuse**: "What if this operation is called twice? Called before its prerequisite? Called concurrently with itself?"
3. **State Corruption**: "What if this variable was set by a previous failed operation? What if it was never initialized?"
4. **Environmental Hostility**: "What if the event store returns fewer items than requested? What if it returns zero? What if the underlying data changes between two reads?"

### Mechanism

The existing panel personas are constructive — they review requirements for quality, examine architecture for soundness, and verify testability. None is explicitly *destructive*. The adversarial tester inverts the perspective: instead of asking "is this spec good enough?", they ask "how do I make this spec fail?" This perspective naturally gravitates toward boundary conditions, empty collections, and guard bypasses.

### Example: How It Catches Bug 1

The adversarial tester examines `load_older_events()` and asks: "What if the event store returns 50 events but after filtering, zero widgets are mounted?" This immediately surfaces the cursor advancement problem.

### Example: How It Catches Bug 2

The adversarial tester examines the replay guard and asks: "What if I trigger a condensation that produces an empty tail? Does the guard still work?" This is a direct hit on Bug 2.

### Generality

Catches any bug class that arises from:
- Inputs the spec author considered implausible but that the system can produce.
- Operation sequences that violate assumed ordering.
- Environmental conditions that differ from the spec's implicit assumptions (e.g., "the store always returns at least one event").
- Concurrency and reentrancy problems.
- State leakage between operations.

This is a broad class that includes most integration bugs, race conditions, and edge-case failures.

---

## Proposal 4: Invariant Specification Requirement

### Description

Add a structural rule to the spec-panel review: **every mutable state variable introduced by the spec must have an explicitly stated invariant, and every acceptance criterion must reference which invariants it validates.** If a spec introduces `_replayed_event_offset`, the spec must contain a line like:

> **INV-1**: `_replayed_event_offset` SHALL equal the number of events consumed from the event store during replay, regardless of how many widgets were mounted. After initialization, `_replayed_event_offset >= 0` always holds.

The panel then reviews:
1. Are all invariants stated?
2. Are they correct?
3. Does each acceptance criterion trace to at least one invariant?
4. Are there invariants that no acceptance criterion tests?

### Mechanism

The fundamental gap in the v0.04 review was that the spec described *what* the variables are and *how they are used* but never stated *what must always be true about them*. Invariants are the bridge between interface contracts (which the panel reviews well) and implementation correctness (which the panel missed). By requiring invariants as first-class spec artifacts, the panel is forced to review the very statements that, if wrong or absent, produce bugs like Bug 1 and Bug 2.

### Example: How It Catches Bug 1

The spec would be required to state: "INV-cursor: `_loaded_start_index` SHALL decrement by the number of events consumed from the store, not the number of widgets mounted." The panel reviews this invariant and asks: "Does the spec actually guarantee this?" If the spec says "decrement by mounted," the invariant is violated under filtering, and the panel flags the contradiction.

### Example: How It Catches Bug 2

The spec would be required to state: "INV-guard: After replay, `_replayed_event_offset > 0` SHALL hold if and only if replay has been performed." The panel reviews this and asks: "Does `len(plan.tail_events)` guarantee `> 0` after replay?" The answer is no (empty tail), and the invariant is flagged as unenforceable.

### Generality

Catches any bug where:
- A state variable lacks a clear contract, leading to divergent assumptions between spec author and implementer.
- An acceptance criterion tests the happy path but not the invariant boundary.
- Two variables have coupled invariants that the spec treats as independent.

This is particularly effective for stateful systems, protocol implementations, and any code involving cursors, offsets, indexes, or counters.

---

## Proposal 5: Concrete Execution Scenarios with State Snapshots

### Description

Extend Gojko Adzic's "Specification by Example" methodology from Given/When/Then behavioral scenarios to **Given/When/Then/State** scenarios that include explicit snapshots of all mutable state at each step. Instead of:

```
Given: A conversation with 500 events, condensation at event 200, tail of 300 events
When: User resumes the conversation
Then: 200 events are shown with a condensation banner
```

Require:

```
Given: A conversation with 500 events, condensation at event 200, tail of 300 events
When: User resumes the conversation
Then: 200 events are shown with a condensation banner
State: _replayed_event_offset = 300, _loaded_start_index = 200, banner.visible = True

Given: (continuing) User presses PageUp, 50 events in page, 10 are CondensationRequest (filtered)
When: load_older_events() executes
Then: 40 new widgets prepended
State: _loaded_start_index = 150 (advanced by 50, not 40), mounted_count = 240
```

### Mechanism

The current panel evaluates behavioral examples but does not trace internal state. By requiring state snapshots, the examples become executable specifications that can be mechanically verified. More importantly, the act of *writing* the state snapshot forces the spec author to think about what each variable's value should be at each step — which is precisely the reasoning that would have caught both bugs.

### Example: How It Catches Bug 1

Writing the state snapshot for "load_older_events() when some events are filtered" forces the author to specify whether `_loaded_start_index` decreases by 50 (events consumed) or 40 (widgets mounted). The discrepancy becomes visible in the State line.

### Example: How It Catches Bug 2

Writing the state snapshot for "condensation is the last event, tail is empty" forces the author to write `_replayed_event_offset = 0`. The next scenario — "system receives a new event" — requires checking the replay guard, which reads `offset > 0`. The guard evaluates False, and the State snapshot shows replay running again. The bug is caught in the scenario.

### Generality

Catches any bug where:
- The behavioral output is correct but internal state is wrong (the state is a ticking time bomb for the next operation).
- Two sequential operations interact through shared mutable state.
- A degenerate input produces correct output but leaves state in an invalid configuration.
- Accumulated state drift causes failures after multiple operations.

---

## Proposal 6: Difference Analysis Between Consumed and Produced Quantities

### Description

Add a review heuristic: **whenever the spec describes a pipeline where input count can differ from output count (filtering, transformation, aggregation), the panel must explicitly ask: "Which count is used downstream, and what happens when they differ?"**

This is a specialized form of dimensional analysis applied to data flow. The heuristic triggers whenever:
- A function consumes N items and produces M items where M <= N.
- A filter, map, or reduce operation sits between a source and a consumer.
- An index or counter is updated after a transformation step.

The panel should create a **quantity flow diagram**:

```
EventStore --[50 events]--> filter --[40 widgets]--> mount
                                                        |
                                              cursor advances by: ???
```

The "???" must be resolved to either 50 (source count) or 40 (output count), with justification.

### Mechanism

Bug 1 is a textbook instance of the "consumed vs. produced" confusion. The spec described a pipeline (events from store -> filter -> mount) but used the output count (mounted) for the cursor that indexes the input (store). This class of bug is endemic in any system with filtering or transformation stages. The quantity flow diagram makes the dimensional mismatch visible.

### Example: How It Catches Bug 1

The quantity flow diagram for `load_older_events()` shows: `store[start:start+page_size] --(filter)--> mounted_widgets`. The cursor `_loaded_start_index` is decremented. The question "by which count?" exposes the ambiguity. The correct answer is "by page_size (events consumed from store)" and the incorrect answer is "by len(mounted_widgets)."

### Example: How It Catches Bug 2

The quantity flow for `_build_replay_plan()` shows: `condensation --(extract tail)--> tail_events --(len)--> offset`. The question "what is len when tail is empty?" produces 0. The downstream guard `offset > 0` is then traced with input 0, revealing the bypass.

### Generality

Catches any bug where:
- An index is advanced by the wrong count after a filtering or transformation step.
- A counter accumulates at the wrong granularity (e.g., counting bytes instead of records, or widgets instead of events).
- A ratio or rate is computed from mismatched numerator/denominator.
- A buffer size is calculated from the wrong stage of a pipeline.

This is particularly effective for data processing pipelines, pagination systems, and any code involving ETL-style transformations.

---

## Summary Table

| # | Proposal | Primary Bug Class | Catches Bug 1? | Catches Bug 2? | Implementation Cost |
|---|----------|-------------------|-----------------|-----------------|---------------------|
| 1 | State Machine Trace-Through Pass | Stale state, cursor stalls, guard failures | Yes | Yes | Medium (new review pass) |
| 2 | Boundary Value Obligation | Guard bypass at boundaries | Partially | Yes | Low (table template) |
| 3 | Adversarial Tester Persona | Degenerate inputs, sequence abuse | Yes | Yes | Low (new persona) |
| 4 | Invariant Specification Requirement | Missing contracts on mutable state | Yes | Yes | Medium (spec structure change) |
| 5 | Execution Scenarios with State Snapshots | State drift, accumulated errors | Yes | Yes | Medium (scenario format change) |
| 6 | Difference Analysis (Consumed vs. Produced) | Pipeline dimensional mismatches | Yes | Partially | Low (review heuristic) |

### Recommended Priority

**Tier 1 — Highest impact, implement first**:
- Proposal 1 (State Machine Trace-Through) and Proposal 4 (Invariant Specification Requirement) address the root cause most directly: the panel had no mechanism to force invariant reasoning about mutable state. These two proposals are complementary — Proposal 4 ensures invariants are stated in the spec, and Proposal 1 ensures the panel verifies them through trace-through.

**Tier 2 — High impact, implement second**:
- Proposal 3 (Adversarial Tester Persona) adds a perspective that is entirely absent from the current panel. The adversarial mindset naturally finds boundary conditions. This is low-cost to add (one additional persona).
- Proposal 6 (Difference Analysis) is a targeted heuristic that catches a common and pernicious bug class (dimensional mismatches in pipelines). Also low-cost.

**Tier 3 — Reinforce with structured artifacts**:
- Proposal 2 (Boundary Value Obligation) and Proposal 5 (State Snapshots) add structured artifacts that make the trace-through and invariant reasoning more rigorous. They are most valuable when combined with Tier 1 proposals.

---

*Generated 2026-03-04 as part of v0.04 post-implementation retrospective.*
