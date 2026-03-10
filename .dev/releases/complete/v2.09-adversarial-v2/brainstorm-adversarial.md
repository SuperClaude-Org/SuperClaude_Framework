# Brainstorm: Improving sc:adversarial to Catch Implementation-Level Bugs

**Date**: 2026-03-04
**Context**: v0.04 Adaptive Replay post-mortem
**Scope**: General-purpose improvements to the adversarial debate pipeline

---

## Problem Statement

The current `sc:adversarial` pipeline excels at comparing **architectural approaches** — trade-offs between designs, coverage completeness, structural consistency, and requirement satisfaction. However, the v0.04 experience revealed a blind spot: the debate operates almost entirely at the **design abstraction layer** and never descends into **operational state analysis**.

Two bugs escaped the v0.03 adversarial debate and survived into v0.04 implementation:

1. **Index Tracking Stall**: Pagination cursor advances by widget count, not events consumed. When event filtering discards events, the cursor stalls and PageUp reprocesses the same slice forever.
2. **Replay Guard Bypass**: Guard condition assumes non-empty tail after condensation. When condensation is the last event, tail length is 0, guard evaluates false, and replay runs repeatedly.

Both bugs share a structural root cause in the debate process: **no debater was prompted to trace concrete data through the proposed state machine**. The debate compared windowing vs. virtualization, tail-based vs. turn-based — but never asked "given this input sequence, what value does variable X hold at step N?"

---

## Proposal 1: Failure Mode Enumeration Phase

### Description

Add a mandatory **Step 1.5** between Diff Analysis and the Adversarial Debate. In this phase, each advocate must enumerate concrete failure modes for **every** variant (including their own), structured as:

- **Precondition**: What state must exist for this failure to occur?
- **Trigger**: What input or event sequence activates it?
- **Mechanism**: What goes wrong in the data flow?
- **Consequence**: What does the user or system experience?
- **Detection difficulty**: How hard is this to notice in testing?

Each advocate must produce a minimum of N failure modes per variant (N configurable, default 3). Failure modes are scored for **novelty** — an advocate who identifies a failure mode no other advocate found earns bonus weight in the debate scoring.

### Mechanism

Forces debaters out of "my approach is better because..." reasoning and into "what breaks each approach?" reasoning. By requiring advocates to find failure modes in their own variant, it counteracts the natural tendency to steelman only the happy path.

### Example: How It Would Have Caught Bug 1

An advocate for Solution A (or any solution involving pagination) would need to enumerate failure modes for the pagination cursor. The structured precondition/trigger format would prompt:

> **Precondition**: Events include types that are filtered during widget creation (CondensationRequest, empty user messages).
> **Trigger**: User presses PageUp to load older events.
> **Mechanism**: Cursor decrements by `mounted` (widget count), but `mounted < events_consumed` because filtered events produce no widget. Cursor under-advances.
> **Consequence**: PageUp loads the same events repeatedly. Infinite loop for the user.

### Example: How It Would Have Caught Bug 2

An advocate enumerating failure modes for the condensation-based approach:

> **Precondition**: Condensation is the last event in the conversation. No events follow it.
> **Trigger**: Replay is invoked.
> **Mechanism**: `tail_events` is empty, so `_replayed_event_offset = len(plan.tail_events)` is 0. Guard `> 0` evaluates false. Replay proceeds as if it has never run.
> **Consequence**: Replay executes on every render cycle. Unbounded re-execution.

### Generality

Catches any bug class where the happy-path design is sound but specific input sequences create degenerate state. This includes:
- Off-by-one errors in cursor/index management
- Guard condition gaps (empty collections, zero values, null states)
- Accumulator drift (counters that diverge from the quantity they track)
- Race conditions (if timing-dependent inputs are enumerated)
- Resource leaks (if "what happens after N iterations?" is asked)

---

## Proposal 2: Concrete Scenario Trace Rounds

### Description

Add a debate round type called **Scenario Traces** that can be injected at `--depth standard` or deeper. In this round, the debate orchestrator generates 3-5 **concrete input scenarios** derived from the diff analysis, and each advocate must **trace the scenario through their variant's design step by step**, showing the value of every state variable at each step.

Scenarios are generated to include:
- **Happy path**: The most common expected usage
- **Boundary conditions**: Empty inputs, maximum inputs, single-element inputs
- **Filter/transform scenarios**: Inputs where intermediate processing removes or reshapes data
- **Temporal edge cases**: Operations at the start, end, or boundary of a sequence
- **Adversarial inputs**: Sequences specifically designed to stress assumptions

The orchestrator selects scenarios based on the **diff points** from Step 1 — if the variants disagree on how to handle pagination, the scenarios include pagination-stressing inputs.

### Mechanism

Transforms the debate from "which design philosophy is better?" to "given this exact input, what does your design produce?" This is the intellectual equivalent of a unit test applied during the design phase. Abstract claims like "the cursor advances correctly" are replaced with concrete traces like "after processing [event1, filtered_event2, event3], cursor = 1, mounted = 2, events_consumed = 3."

When advocates trace through the same scenario, discrepancies become visible: one advocate might assume filtered events still advance the cursor while another does not. The orchestrator flags traces that produce different end states as **unresolved divergences** requiring explicit resolution before convergence can be declared.

### Example: How It Would Have Caught Bug 1

Orchestrator generates scenario:
> **Scenario**: Events = [UserMsg, AssistantMsg, CondensationRequest, UserMsg, AssistantMsg]. Window size = 3. User presses PageUp.

Advocate traces through Solution A:
> Step 1: Render last 3 events (indices 2-4). mounted = 2 (CondensationRequest filtered). loaded_start = 5 - 2 = 3.
> Step 2: PageUp. Load events at indices 0-2. But index 3 was already just processed...

The trace would expose the stall: `loaded_start` should be 2 (the start of what was consumed), not 3 (5 minus what was mounted).

### Example: How It Would Have Caught Bug 2

Orchestrator generates scenario:
> **Scenario**: Events = [UserMsg, AssistantMsg, Condensation]. No events after condensation. Replay invoked.

Advocate traces through:
> tail_events = events after condensation = []. len(tail_events) = 0.
> _replayed_event_offset = 0. Guard: 0 > 0 = false. Replay proceeds.
> Next call: _replayed_event_offset still 0. Guard: 0 > 0 = false. Replay proceeds again. Infinite.

### Generality

Catches any bug where the design's correctness depends on **specific value relationships** between state variables. This includes:
- Index/offset calculation errors
- Boundary conditions in loops and iterators
- State machine transitions with unexpected inputs
- Accumulated rounding or truncation errors
- Any case where "it works in principle" diverges from "it works with this input"

---

## Proposal 3: Invariant Declaration and Challenge

### Description

Add a structured phase where each advocate must declare the **invariants** their design relies upon. An invariant is a property that must always hold true for the design to be correct. Examples:

- "After `load_older_events()`, `_loaded_start_index` equals the index of the oldest rendered event."
- "After replay completes, `_replayed_event_offset > 0`."
- "The number of widgets in the DOM equals `window_size` or `total_events`, whichever is smaller."

After invariants are declared, opposing advocates enter a **Challenge Round** where they attempt to construct input sequences that **violate** the declared invariants. If an advocate can demonstrate a concrete scenario where an invariant breaks, that invariant is flagged as **unproven**, and the design must either be modified or the invariant must be weakened (which itself becomes a debate point about whether the weakened invariant is sufficient).

### Mechanism

This borrows directly from formal verification and design-by-contract. Invariants make implicit assumptions explicit. The challenge round turns every advocate into a **property-based fuzzer** trying to break the other designs. Unlike Proposal 1 (which asks "what could go wrong?"), this proposal asks "what MUST be true?" and then tries to disprove it. This is a stronger discipline — it forces advocates to commit to specific correctness properties rather than describing behavior in prose.

### Example: How It Would Have Caught Bug 1

Solution A advocate declares:
> **Invariant**: After `load_older_events()`, `_loaded_start_index` == index of the first event in the currently rendered window.

Solution B or C advocate challenges:
> **Challenge**: Events = [Msg1, FilteredEvent, Msg2, Msg3, Msg4]. Window = 3. Initial render shows indices 2-4 (3 widgets for 3 events, but FilteredEvent at index 1 does not produce a widget). After load_older_events: mounted = 2 (only Msg1 produces a widget from the new slice; FilteredEvent is skipped). loaded_start_index = 5 - 2 = 3. But the oldest rendered event is at index 0 (Msg1). Invariant violated: 3 != 0.

### Example: How It Would Have Caught Bug 2

Condensation-approach advocate declares:
> **Invariant**: After replay completes, `_replayed_event_offset > 0`.

Challenger constructs:
> Events = [Msg, Condensation]. tail_events = []. offset = len([]) = 0. Invariant violated on the very first replay.

This would immediately expose that the invariant does not hold for the empty-tail case, forcing a design fix before implementation.

### Generality

Catches any bug class rooted in **violated assumptions**:
- Guard conditions that do not cover all states
- Accumulator invariants that drift
- Ordering guarantees that break under specific sequences
- Capacity/bound assumptions that fail at extremes
- Type/nullability assumptions (e.g., "this list is never empty")

---

## Proposal 4: Devil's Advocate — Dedicated Edge Case Hunter Role

### Description

Add a new agent role to the debate: the **Devil's Advocate**. This agent does not advocate for any variant. Instead, it receives all variants and the diff analysis, and its sole job is to:

1. Identify **assumptions** each variant makes (implicitly or explicitly)
2. Construct **adversarial input sequences** designed to violate those assumptions
3. Identify **state transitions** that are under-specified or ambiguous
4. Flag **guard conditions** that might not cover all cases
5. Enumerate **degenerate inputs**: empty collections, zero values, maximum values, type boundaries

The Devil's Advocate produces its analysis before Round 1, and advocates must address the Devil's Advocate's concerns in their opening statements. Any concern left unaddressed by all advocates is flagged as a **convergence blocker** — the debate cannot declare convergence until every Devil's Advocate concern has been explicitly resolved.

The Devil's Advocate is implemented as a separate agent with a distinct system prompt emphasizing **destructive creativity** — not "which design is better?" but "how does each design break?"

### Mechanism

Creates a structural asymmetry in the debate. Currently, all agents are advocates with a secondary responsibility to critique. The Devil's Advocate has criticism as its primary and only function. This prevents the failure mode where all advocates focus on selling their own variant's strengths and treat edge cases as an afterthought.

The convergence-blocker mechanism is critical: without it, the Devil's Advocate's findings could be acknowledged and then ignored during scoring. By making unresolved concerns block convergence, the debate cannot conclude until edge cases are addressed.

### Example: How It Would Have Caught Bug 1

Devil's Advocate analysis before Round 1:
> **Assumption flagged** (all pagination variants): "Widget count from a slice equals event count in that slice."
> **Adversarial input**: Slice containing CondensationRequest or empty UserMessage events that do not produce widgets.
> **Question for advocates**: "If `mounted != events_in_slice`, how does your cursor advance? Show the math."

This question would have been a convergence blocker. No advocate could answer it without exposing the stall.

### Example: How It Would Have Caught Bug 2

Devil's Advocate analysis:
> **Assumption flagged** (condensation-based variants): "After condensation, at least one tail event exists."
> **Adversarial input**: Conversation ending with a Condensation event and no subsequent messages.
> **Question for advocates**: "What is `len(tail_events)` when condensation is the final event? What does your replay guard evaluate to?"

### Generality

Catches any bug class rooted in **unstated assumptions**:
- "This collection is never empty"
- "These two counts are always equal"
- "This function is only called when X is true"
- "The input always has at least one element of type Y"
- Implicit type constraints, ordering assumptions, cardinality assumptions

The Devil's Advocate role is especially effective against the class of bugs where every advocate independently makes the same wrong assumption — a blind spot that advocate-vs-advocate debate cannot surface because nobody challenges it.

---

## Proposal 5: Convergence Criteria Tightening — State Coverage Gate

### Description

Modify the convergence calculation to include a **state coverage** dimension alongside the current "percentage of diff points agreed upon." Currently:

```
convergence = agreed_points / total_diff_points
```

Proposed:

```
convergence = (agreed_points / total_diff_points) * state_coverage_factor
```

Where `state_coverage_factor` is determined by whether the debate has addressed a minimum set of state categories:

| Category | Description | Required? |
|----------|-------------|-----------|
| Happy path | Normal expected flow | Yes |
| Empty/zero inputs | Degenerate inputs that produce empty intermediate state | Yes |
| Boundary conditions | First element, last element, max capacity | Yes |
| Filter divergence | Inputs where intermediate processing changes cardinality | Conditional (if any variant involves filtering) |
| Error/exception paths | Inputs that trigger error handling | Conditional (if error handling is specified) |
| Concurrent/reentrant | Multiple simultaneous operations | Conditional (if concurrency is involved) |

If a required category has not been addressed in any debate round, `state_coverage_factor < 1.0`, and convergence cannot be reached even if all advocates agree on every diff point.

### Mechanism

Prevents "shallow convergence" — the scenario where advocates quickly agree on architectural trade-offs but never discuss operational edge cases. The current 80% convergence threshold measures **breadth** (how many points are agreed upon) but not **depth** (whether those agreements were stress-tested). The state coverage gate adds a depth dimension.

### Example: How It Would Have Caught Bug 1

The debate would reach, say, 85% agreement on diff points. But the state coverage audit would flag:

> **Filter divergence**: No debate round addressed what happens when intermediate filtering changes the count of elements produced from a slice. state_coverage_factor = 0.8. Effective convergence = 85% * 0.8 = 68% < 80% threshold.

Debate would continue with an additional round specifically targeting the filter divergence gap.

### Example: How It Would Have Caught Bug 2

> **Empty/zero inputs**: No debate round addressed the case where `tail_events` is empty after condensation. state_coverage_factor = 0.85. Effective convergence = 85% * 0.85 = 72.25% < 80% threshold.

### Generality

Catches any bug class that exists in an **unexplored region of the input space**. This is a meta-improvement — rather than catching specific bugs, it catches the *process failure* of not exploring important input categories. It is especially effective when combined with any of the other proposals, as it provides a structural guarantee that the debate cannot shortcut past edge case analysis.

---

## Proposal 6: Post-Merge Trace Validation

### Description

Add a **Step 5.5** after merge execution. In this step, the merged solution is subjected to the same Concrete Scenario Traces from Proposal 2, but now applied to the **final merged design** rather than individual variants. A validation agent (not any of the original advocates) traces 3-5 scenarios through the merged output and flags any inconsistencies, ambiguities, or underdetermined states.

This catches a different failure mode than the pre-merge proposals: **merge artifacts** — bugs introduced not by any individual variant but by the merge process itself. When Solution A's cursor management is combined with Solution C's condensation boundary, the interaction between them may create bugs that existed in neither original.

### Mechanism

The merged solution often combines mechanisms from different variants that were never designed to work together. By running traces through the merged output, integration bugs become visible. The validation agent is specifically chosen to be a fresh agent with no advocacy bias — it has no stake in any original variant and evaluates the merge purely on operational correctness.

### Example: How It Would Have Caught Bug 1

The merged solution combined A's pagination with C's condensation boundary. Post-merge trace:

> **Scenario**: Condensed conversation with mixed event types in tail. User presses PageUp.
> Trace reveals that A's cursor advancement logic (decrement by `mounted`) was merged without adapting it for C's condensation-aware event filtering. The merged cursor logic inherits A's assumption that `mounted == events_consumed`.

### Example: How It Would Have Caught Bug 2

> **Scenario**: Condensation as final event.
> Trace through merged design reveals that the replay guard from variant A/B was kept, but the offset calculation was adapted from C. The interaction produces `offset = 0` with `guard > 0` — a combination that neither original variant would have produced in its pure form.

### Generality

Catches:
- **Integration bugs**: Mechanisms from different variants that conflict when combined
- **Assumption mismatches**: Variant A assumes X, Variant C assumes not-X, merge inherits both assumptions
- **Incomplete adaptation**: A mechanism is moved from one context to another without updating its dependencies
- **Semantic drift**: A term or variable means something slightly different in the merged context than in the original

---

## Summary Matrix

| # | Proposal | Phase | Bug 1 | Bug 2 | Primary Bug Class |
|---|----------|-------|-------|-------|-------------------|
| 1 | Failure Mode Enumeration | Step 1.5 (pre-debate) | Yes | Yes | Degenerate input states |
| 2 | Concrete Scenario Traces | Debate round | Yes | Yes | Value-level correctness |
| 3 | Invariant Declaration and Challenge | Debate round | Yes | Yes | Violated assumptions |
| 4 | Devil's Advocate Role | Structural (new agent) | Yes | Yes | Unstated shared assumptions |
| 5 | State Coverage Gate | Convergence criteria | Yes | Yes | Unexplored input regions |
| 6 | Post-Merge Trace Validation | Step 5.5 (post-merge) | Yes | Yes | Integration/merge artifacts |

## Recommended Implementation Priority

1. **Proposal 4 (Devil's Advocate)** — Highest ROI. Adds a single new agent role with a focused prompt. Minimal changes to the pipeline structure. Addresses the root cause directly: no one was assigned to break things.

2. **Proposal 5 (State Coverage Gate)** — Low implementation cost (modify convergence formula). Provides a structural guarantee that the debate explores edge cases regardless of advocate behavior.

3. **Proposal 2 (Scenario Traces)** — Highest bug-catching power but also highest token cost. Could be gated behind `--depth deep` to control cost.

4. **Proposal 3 (Invariant Challenge)** — Powerful but requires advocates to think formally. Best for designs involving state machines, cursors, or counters.

5. **Proposal 1 (Failure Mode Enumeration)** — Overlaps significantly with Proposal 4. Implement if the Devil's Advocate alone proves insufficient.

6. **Proposal 6 (Post-Merge Validation)** — Important for catching merge artifacts specifically. Lower priority because Proposals 2-5 catch most bugs before they reach the merge.

## Combinatorial Synergies

The strongest configuration combines proposals that operate at different levels:

- **Structural**: Devil's Advocate (Proposal 4) ensures someone is always trying to break things.
- **Analytical**: Invariant Challenge (Proposal 3) forces explicit correctness claims.
- **Empirical**: Scenario Traces (Proposal 2) grounds the debate in concrete values.
- **Systemic**: State Coverage Gate (Proposal 5) prevents the process from shortcutting.

This four-layer approach addresses the failure at every level: role assignment, reasoning methodology, evidence requirements, and process gates.
