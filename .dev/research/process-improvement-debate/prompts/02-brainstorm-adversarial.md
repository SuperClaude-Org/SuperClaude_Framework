/sc:brainstorm --strategy systematic --depth deep

## Topic: Improving /sc:adversarial to Catch Implementation-Level Flaws

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


## Your Focus: /sc:adversarial Command

The adversarial command runs structured debates between agents to compare, challenge,
and merge competing approaches. In v0.04, the adversarial debate successfully resolved
high-level design questions (windowing vs virtualization) but did NOT probe
implementation-level edge cases that led to the two bugs.

### Questions to Explore

1. **Debate depth gaps**: The debate focused on architectural trade-offs but not on
   state-machine mechanics. Should the adversarial protocol require a dedicated
   "implementation edge case" debate round?

2. **Challenge framework**: The current protocol has agents challenge each other's
   proposals. Should there be a mandatory "devil's advocate" phase where an agent
   specifically tries to find guard condition failures, off-by-one errors, and
   state tracking bugs in each proposal?

3. **Convergence trap**: The convergence threshold (0.80-0.85) may cause debates to
   settle too early on high-level agreement without probing low-level failure modes.
   Should the protocol enforce minimum debate depth on specific categories before
   allowing convergence?

4. **Agent specialization**: Should the adversarial protocol support a dedicated
   "fault-finder" or "invariant-prober" agent role that specifically targets:
   - "What if this count is zero?"
   - "What if this collection is empty?"
   - "What if the filter removes all items?"
   - "What if the guard variable equals its sentinel?"

5. **Merge verification**: After merging proposals, should the protocol require a
   "merged solution stress test" phase where edge cases are explicitly enumerated
   and traced through the merged design?

6. **Scoring dimensions**: The current scoring is qualitative-quantitative hybrid.
   Should "edge case coverage" or "invariant completeness" be a mandatory scoring
   dimension?

### Deliverable

Produce a structured requirements document with:
- 3-5 specific, actionable proposals for improving /sc:adversarial
- Each proposal should include: description, rationale, expected impact, implementation sketch
- Proposals must be general (not specific to this codebase or bug)
- Focus on protocol structure and agent behavior, not cosmetic improvements
