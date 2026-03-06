/sc:brainstorm --strategy systematic --depth deep

## Topic: Improving /sc:roadmap to Surface Edge-Case Risks Earlier

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


## Your Focus: /sc:roadmap Command

The roadmap command generates structured implementation plans from specifications.
In v0.04, the roadmap correctly sequenced the spike (SPEC-002) before the main
feature work, but did NOT flag state-machine edge cases as risks or create
verification milestones for guard condition completeness.

### Questions to Explore

1. **Risk identification gaps**: The roadmap generates risk registers, but the v0.04
   risk register (R-1 through R-6) focused on API compatibility, scroll behavior,
   and SDK evolution — not on state-machine boundary conditions. Should the roadmap
   protocol require a mandatory "state invariant risk" category?

2. **Verification milestone gaps**: The roadmap created milestones for the spike and
   for acceptance criteria, but did not create specific verification milestones for
   guard condition testing or filter interaction testing. Should "edge case verification"
   be a mandatory milestone type?

3. **Acceptance criteria completeness**: The spec had 21 acceptance criteria (AC-1
   through AC-21) but none tested the specific failure modes (empty tail + guard bypass,
   filtered events + cursor stall). Should the roadmap protocol require generation of
   "negative acceptance criteria" or "failure mode acceptance criteria"?

4. **Cross-component interaction analysis**: The roadmap treated runner and visualizer
   as separate components. Should the protocol require explicit "interaction boundary
   analysis" where state flows between components are traced for edge cases?

5. **Validation wave enhancement**: The roadmap has a validation wave (Wave 4). Should
   this wave include mandatory "invariant fuzzing" where the validator generates edge
   inputs (empty collections, zero counts, sentinel values) and traces them through
   the proposed design?

6. **Template enhancements**: Should the roadmap templates include mandatory sections
   for "guard condition inventory" or "state machine boundary analysis"?

### Deliverable

Produce a structured requirements document with:
- 3-5 specific, actionable proposals for improving /sc:roadmap
- Each proposal should include: description, rationale, expected impact, implementation sketch
- Proposals must be general (not specific to this codebase or bug)
- Focus on structural additions to the roadmap protocol, not cosmetic improvements
