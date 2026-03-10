/sc:brainstorm --strategy systematic --depth deep

## Topic: Improving /sc:spec-panel to Catch State-Machine Edge Cases

## Background: What Happened

During v0.04-AdaptiveReplay development, our pipeline (spec → panel review →
adversarial debate → roadmap → implementation) produced code with two correctness bugs
that were only caught by an external reviewer AFTER implementation:

### Bug 1: `_loaded_start_index` stall (richlog_visualizer.py:987)
`load_older_events()` decrements `_loaded_start_index` by `mounted` (widget count).
When events are filtered by `_create_replay_widget()` (returning None for
CondensationRequest, empty user messages), `mounted < events_consumed`, causing the
cursor to stall. PageUp reprocesses the same slice indefinitely.

**Root cause**: The spec (FR-4, FR-5) defined scroll-position stability and on-demand
loading but did not specify cursor advancement semantics for filtered events. The
implementation assumed all events produce widgets.

### Bug 2: Replay guard bypass (conversation_runner.py:301,353)
The replay idempotence guard checks `_replayed_event_offset > 0`, but the offset is
set to `len(plan.tail_events)`. When condensation is the last event, tail is empty
(len=0), offset stays 0, and the guard never fires — allowing repeated replay calls
that duplicate banners.

**Root cause**: The spec defined `_replayed_event_offset` as "tracks how many events
delivered to visualizer" (Interface Contracts section). The guard logic was correctly
derived from the spec, but the spec failed to consider the edge case where a valid
replay produces zero tail events.

### What the pipeline DID catch
- The 6-expert panel (Wiegers, Nygard, Fowler, Crispin, Adzic, Cockburn) correctly
  identified many issues: NFR-5/apply() contradiction, missing requirements, test gaps.
- The adversarial debate correctly resolved competing approaches (virtualization vs
  windowing, condensation handling).
- The roadmap correctly sequenced dependencies (SPEC-002 spike before SPEC-001 FR-4/FR-5).

### What the pipeline MISSED
- **State machine edge cases**: Neither the panel nor the debate probed what happens
  when invariant assumptions break (e.g., "every event produces a widget" or "tail is
  always non-empty after valid replay").
- **Guard condition completeness**: The offset-as-guard pattern was specified but its
  failure modes under edge inputs were not explored.
- **Filter interaction effects**: The spec correctly separated runner (slicing) from
  visualizer (rendering), but didn't analyze how the visualizer's filtering feeds back
  into the runner's cursor state.

### Classification of the miss
These are NOT exotic corner cases. They are **standard state-machine boundary
conditions** that a systematic review should catch:
1. "What happens when the output count differs from the input count?" (filter divergence)
2. "What happens when a guard variable can legitimately be the sentinel value?" (zero-is-valid)
3. "What happens when the last item in a sequence has special properties?" (boundary event)

## Constraints on Proposals
- Proposals MUST be **general-purpose improvements** to the command's approach/methodology
- Proposals MUST NOT be specific to this particular bug or this particular codebase
- Proposals should increase the probability of catching bugs **in the same class** (state
  machine edge cases, guard condition completeness, filter interaction effects)
- Proposals should be implementable as changes to the command's behavioral protocol,
  prompt engineering, or structural workflow — not as changes to the codebase being reviewed


## Your Focus: /sc:spec-panel Command

The spec-panel command assembles a panel of simulated experts (Wiegers, Nygard, Fowler,
Crispin, Adzic, Cockburn, etc.) to review specifications. In the v0.04 case, the panel
DID identify many real issues but MISSED the state-machine boundary conditions described
above.

### Questions to Explore

1. **Expert methodology gaps**: Which expert personas should have caught these issues?
   What specific questioning techniques or analysis frameworks are they missing?

2. **Structural review gaps**: The panel reviews requirements, architecture, testing,
   and compliance — but does it systematically probe state-machine invariants, guard
   condition completeness, or filter interaction effects?

3. **Review checklist additions**: What mandatory checklist items or review gates could
   be added to the panel's workflow that would force examination of:
   - Guard condition edge cases (sentinel values, zero-is-valid, empty collections)
   - State tracking divergence (when outputs don't map 1:1 to inputs)
   - Cross-component feedback loops (when component B's behavior affects component A's state)

4. **Expert interaction patterns**: Should the panel workflow enforce cross-expert
   challenges? E.g., after Fowler reviews interfaces, should Nygard be required to
   probe failure modes of each interface contract?

5. **Mode enhancements**: Should there be a new mode (e.g., `--mode invariant-analysis`
   or `--mode state-machine`) that specifically targets these classes of bugs?

6. **Structural output requirements**: Should the panel be required to produce a
   "failure mode matrix" or "guard condition audit" as a mandatory output artifact?

### Deliverable

Produce a structured requirements document with:
- 3-5 specific, actionable proposals for improving /sc:spec-panel
- Each proposal should include: description, rationale, expected impact, implementation sketch
- Proposals must be general (not specific to this codebase or bug)
- Focus on methodology and structural changes, not cosmetic improvements
