# Brainstorm: Improving sc:roadmap to Surface Edge Cases and Invariant Violations

**Context**: Two bugs escaped the v0.04 roadmap planning phase. Both involved state-tracking variables whose correctness depended on conditions (filtering, empty inputs) that were never identified as separate deliverables or risks. This document proposes general-purpose enhancements to the roadmap generation methodology.

**Date**: 2026-03-04
**Source bugs**: Index tracking stall in `load_older_events()`, replay guard bypass with empty tail after condensation.

---

## Proposal 1: State Variable Invariant Registry

### Description

For every deliverable that introduces or modifies a state-tracking variable (counters, offsets, flags, cursors), the roadmap should generate an **invariant registry entry** that names the variable, states its invariant in predicate form, and enumerates the operations that mutate it. Each mutation site becomes a sub-deliverable requiring a test that the invariant holds after the mutation.

The current roadmap treats "Replace boolean with int offset" (D2.3) as a single atomic deliverable. But an integer offset has a richer invariant surface than a boolean: it must advance by the correct amount, it must never go negative, it must be consistent with the actual events delivered. None of these invariants were called out.

### Mechanism

During deliverable generation, the roadmap scans for state variable introductions (assignments to `self._*` fields, new class attributes, counter/offset/cursor patterns). For each, it generates:

1. **Invariant predicate**: A plain-language statement of what must always be true (e.g., "`_replayed_event_offset` equals the total number of events successfully delivered to the visualizer").
2. **Mutation inventory**: Every code path that writes to the variable.
3. **Edge case inputs per mutation**: What happens when the mutation operand is zero, negative, or has a type different from the expected one (e.g., widget count vs. event count).
4. **Verification deliverable**: A test that asserts the invariant after each mutation path.

### Example: How it catches Bug 1

Bug 1: `_loaded_start_index -= mounted` used widget count instead of `events_consumed`. An invariant registry entry for `_loaded_start_index` would state: "After `load_older_events()`, `_loaded_start_index` equals `previous_value - number_of_events_consumed_from_store`." The mutation inventory would list the single decrement site and ask: "What is the operand? Is it events consumed, or something else (e.g., widgets mounted)?" The distinction between events consumed and widgets mounted would surface as a required clarification during planning.

### Example: How it catches Bug 2

Bug 2: `_replayed_event_offset = len(plan.tail_events)` is 0 when `tail_events` is empty after condensation. The invariant for `_replayed_event_offset` would include: "After replay completes, `_replayed_event_offset > 0` if and only if replay was performed." The edge case analysis would ask: "What if `tail_events` is empty?" and identify that `len([]) == 0` makes the guard indistinguishable from "never replayed."

### Generality

This catches any bug where a state variable is updated with the wrong operand, where zero/empty inputs create ambiguous state, or where multiple mutation sites drift out of sync. Common in pagination cursors, reference counts, progress trackers, cache invalidation counters, and any mutable offset.

---

## Proposal 2: Failure Mode and Effects Analysis (FMEA) Pass

### Description

After generating deliverables, the roadmap should execute a **Failure Mode and Effects Analysis** pass over each deliverable. For every deliverable that involves computation (not pure rendering or configuration), the pass asks three questions:

1. **What inputs can this computation receive?** (Including empty, null, zero, negative, duplicate, out-of-order.)
2. **What happens if the computation produces a result that is correct in type but wrong in value?** (Off-by-one, wrong unit, stale value.)
3. **What downstream consumers depend on the result, and what do they assume?**

The output is a **failure mode table** appended to the deliverable, with each identified failure mode either (a) promoted to a separate test deliverable, or (b) documented as an accepted risk with justification.

### Mechanism

The FMEA pass operates on the deliverable list after initial generation. For each deliverable:

- Parse the description for computational verbs (compute, extract, filter, count, calculate, determine, select).
- For each computation, enumerate input domains including degenerate cases.
- For each output, trace forward to consumers and check for implicit assumptions.
- Generate failure mode entries with severity (silent corruption > crash > degraded UX).

Silent corruption failures (where the system continues operating with wrong state) are flagged as highest severity because they are hardest to detect in testing.

### Example: How it catches Bug 1

D4.1 describes `load_and_prepend_older_events(page_size)`. FMEA asks: "What is the return value? Who consumes it? What if events are filtered during loading (some events skipped)?" This surfaces the distinction between "events fetched from store" and "widgets actually mounted" and flags the cursor update as a site where the wrong quantity could be used.

### Example: How it catches Bug 2

D2.3 describes replacing a boolean with an int offset. FMEA asks: "What values can `len(plan.tail_events)` take? What if it is 0? Who reads `_replayed_event_offset` and what do they assume about 0 vs. non-zero?" This identifies that `0` is ambiguous: it means both "never replayed" and "replayed but nothing to show."

### Generality

FMEA catches any bug where degenerate inputs produce technically valid but semantically wrong results. This includes empty collections passed to `len()`, divide-by-zero in averages, null propagation through optional chains, and off-by-one errors in boundary computations. It is the standard technique in hardware reliability engineering adapted for software state machines.

---

## Proposal 3: Guard and Sentinel Analysis Phase

### Description

Any deliverable that introduces conditional logic (guards, sentinels, flags, early returns) should trigger a **guard analysis** sub-phase. The analysis enumerates all states the guard variable can take, maps each state to the intended behavior, and explicitly identifies "confused states" where the guard variable's value is ambiguous between two or more intended meanings.

The current roadmap generated D2.3 ("Replace boolean with int offset") without analyzing the semantic meaning of every possible value of the new integer. A boolean has two states and is hard to confuse. An integer has infinite states, and the transition from boolean to integer is precisely the kind of change that introduces confused states.

### Mechanism

For each deliverable involving guards or conditional checks:

1. **State enumeration**: List all values the guard variable can hold and what each means.
2. **Ambiguity detection**: Identify any value that maps to multiple semantic meanings (e.g., `0` meaning both "uninitialized" and "empty result").
3. **Transition analysis**: For type changes (bool to int, enum to string, etc.), verify that every semantic state from the old type maps to a unique state in the new type.
4. **Resolution requirement**: If ambiguity is detected, the deliverable must include a disambiguation mechanism (sentinel value, separate flag, explicit state enum) or document the accepted risk.

### Example: How it catches Bug 2

D2.3 replaces `_historical_events_replayed: bool` with `_replayed_event_offset: int`. Guard analysis asks: "The boolean had two states: `False` (not replayed) and `True` (replayed). The integer has: `0` and `>0`. Does `0` unambiguously mean 'not replayed'? What if replay runs but produces 0 events?" This directly surfaces the empty-tail ambiguity. The resolution would be either a sentinel value (`-1` for "not replayed") or a separate `_replay_completed: bool` flag.

### Example: How it catches Bug 1

The guard `if self._loaded_start_index <= 0: disable load-more` depends on `_loaded_start_index` correctly tracking remaining events. Guard analysis asks: "Under what conditions does this reach 0? Can it reach 0 prematurely?" If the decrement uses the wrong operand (widgets instead of events), the guard fires at the wrong time. The analysis would flag that the guard's correctness depends on the decrement operand being exactly "events consumed," not "widgets mounted."

### Generality

This catches bugs in any guard/sentinel/flag system: boolean flags that can be set without the corresponding action completing, enum states that overlap, counters that reach termination conditions via the wrong decrement path, and any case where a type migration (bool to int, int to enum) introduces state ambiguity. Particularly relevant for state machines, pagination, retry logic, and lifecycle management.

---

## Proposal 4: Deliverable Decomposition into Implement/Verify Pairs

### Description

Every deliverable that introduces behavior (not documentation or configuration) should be decomposed into an **implement** sub-deliverable and a **verify** sub-deliverable. The verify sub-deliverable is not "write unit tests for the feature" (that is already standard). It is "write a test that specifically targets the correctness of the computation, including degenerate inputs."

The current roadmap conflates "implement X" with "test X works in the happy path." D2.5 says "Unit tests: windowed path, full path, cascade path selection, error recovery fallthrough." These are all happy-path and error-recovery tests. None of them test the correctness of the offset value itself under edge conditions.

### Mechanism

For each behavioral deliverable `D.x`:
- `D.x.a` (Implement): The feature implementation as currently specified.
- `D.x.b` (Verify): A test deliverable that targets the **internal correctness** of the computation, not just the external behavior. This includes:
  - Input domain boundary tests (empty, single, maximum, off-by-one).
  - Operand identity tests ("is this the right quantity being used?").
  - Post-condition assertions on internal state, not just output.

The verify deliverable must reference specific internal state variables and assert their values, not just assert that the external API returned the right thing.

### Example: How it catches Bug 1

D4.2 ("prepend_events with scroll preservation") would decompose into:
- D4.2.a: Implement `prepend_events()` with scroll save/restore.
- D4.2.b: Verify that after `load_older_events()`, `_loaded_start_index` has decreased by exactly the number of events consumed (not widgets mounted). Test with events that are filtered (some skipped) to ensure the distinction matters.

### Example: How it catches Bug 2

D2.3 ("Replace boolean with int offset") would decompose into:
- D2.3.a: Implement `_replayed_event_offset` replacing the boolean.
- D2.3.b: Verify that `_replayed_event_offset` is nonzero after any successful replay, including replay with empty tail. Verify that the early-return guard `if self._replayed_event_offset > 0: return` correctly prevents re-replay in all cases, including post-condensation with empty tail.

### Generality

This catches any bug where the implementation is correct for normal inputs but breaks for edge cases that are never tested. The separation forces the roadmap to think about what "correct" means for internal state, not just external behavior. It is particularly effective for pagination, caching, stateful protocols, and any system where internal bookkeeping must remain consistent across operations.

---

## Proposal 5: Cross-Deliverable Data Flow Tracing

### Description

The roadmap should generate a **data flow trace** that follows each piece of mutable state from its point of creation through every deliverable that reads or writes it. When a state variable is written in one milestone and read in another, the trace identifies **implicit contracts** between the milestones that are not captured by the dependency graph.

The current dependency graph (M1 -> M2 -> M3 -> M4 -> M5) captures structural dependencies ("M4 needs M2's API") but not data flow dependencies ("M4's `load_older_events` writes to `_loaded_start_index` which was initialized in M2 and whose semantics are defined by the offset convention chosen in D2.3"). The data flow trace makes these implicit contracts explicit and testable.

### Mechanism

1. **Variable birth**: For each deliverable that introduces a state variable, record the variable name, initial value, and semantic meaning.
2. **Write trace**: For each deliverable that writes to the variable, record the write expression and the intended semantics of the new value.
3. **Read trace**: For each deliverable that reads the variable, record what the reader assumes about the variable's value.
4. **Contract extraction**: Where a writer and reader are in different milestones, extract the implicit contract ("writer guarantees X, reader assumes X") and promote it to an explicit acceptance criterion.
5. **Conflict detection**: Flag any case where the writer's semantics and the reader's assumptions are not provably identical.

### Example: How it catches Bug 1

`_loaded_start_index` is initialized in M2 (or M4), written in M4's `load_older_events`, and read in M4's "disable load-more" guard. The data flow trace would identify that the writer (decrement by `mounted`) and the reader (check `<= 0`) have an implicit contract: "the decrement operand represents events consumed from the store." If the writer uses widget count instead, the contract is violated. The trace surfaces this as a testable cross-deliverable contract.

### Example: How it catches Bug 2

`_replayed_event_offset` is written in M2's `replay_historical_events` (D2.3) and read in M2's early-return guard and M4's `load_older_events`. The data flow trace identifies the reader's assumption: "`_replayed_event_offset > 0` means replay has occurred." The writer's semantics: "`_replayed_event_offset = len(plan.tail_events)`." The trace flags: "If `tail_events` is empty, the writer produces 0 but the reader interprets 0 as 'not replayed.' Contract violation."

### Generality

This catches any bug arising from implicit assumptions between components that share mutable state. It is particularly effective in systems with multiple write sites for the same variable, pagination state shared across request/response boundaries, and any architecture where one component's correctness depends on another component's post-conditions. Also catches stale-state bugs where a variable is written in one lifecycle phase but read in a later phase after conditions have changed.

---

## Summary Matrix

| # | Proposal | Primary Bug Class | Catches Bug 1 | Catches Bug 2 | Implementation Cost |
|---|----------|-------------------|---------------|---------------|---------------------|
| 1 | State Variable Invariant Registry | Wrong operand, zero ambiguity | Yes (wrong operand) | Yes (zero ambiguity) | Medium |
| 2 | FMEA Pass | Degenerate inputs, silent corruption | Yes (filtered events) | Yes (empty tail) | Medium |
| 3 | Guard and Sentinel Analysis | State ambiguity, type migration | Partial (guard correctness) | Yes (0 ambiguity) | Low |
| 4 | Implement/Verify Decomposition | Untested edge cases | Yes (operand identity test) | Yes (empty-tail test) | Low |
| 5 | Cross-Deliverable Data Flow Tracing | Implicit contracts, stale state | Yes (write/read mismatch) | Yes (writer/reader contract) | High |

### Recommended Priority

1. **Proposal 4** (Implement/Verify Pairs): Lowest cost, highest immediate impact. Forces edge case thinking at deliverable granularity.
2. **Proposal 1** (Invariant Registry): Medium cost, catches the most dangerous class (silent state corruption). Natural extension of deliverable generation.
3. **Proposal 2** (FMEA Pass): Medium cost, systematic coverage. The standard reliability engineering technique adapted for software.
4. **Proposal 3** (Guard Analysis): Low cost, narrowly targeted but catches a specific and common class of bug (sentinel ambiguity).
5. **Proposal 5** (Data Flow Tracing): Highest cost, highest coverage for cross-milestone bugs. Worth implementing for complex roadmaps (6+ milestones) but may be overkill for smaller ones.

### Integration Notes

These proposals are complementary, not alternatives. The recommended implementation order allows incremental adoption:

- **Phase 1**: Add Proposals 3 and 4 (low cost, high signal). These are structural changes to deliverable generation.
- **Phase 2**: Add Proposals 1 and 2 (medium cost). These are analysis passes over the generated deliverables.
- **Phase 3**: Add Proposal 5 (high cost). This is a cross-deliverable analysis that requires the full roadmap to be generated first.

All proposals produce artifacts (invariant tables, failure mode tables, guard analysis tables, verify deliverables, data flow traces) that serve double duty as implementation guidance and review checklists.
