/sc:adversarial --depth deep --convergence 0.85

## Adversarial Evaluation of Process Improvement Proposals

### Context

Three brainstorm sessions produced proposals for improving our specification/review
pipeline. Each focused on one command:
- **spec-panel proposals**: /config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/brainstorm-spec-panel.md
- **adversarial proposals**: /config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/brainstorm-adversarial.md
- **roadmap proposals**: /config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/brainstorm-roadmap.md

The scoring framework is defined in: /config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/scoring-framework.md

### Background (Why We're Doing This)

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


### Your Task

1. **Read all three brainstorm outputs** and the scoring framework
2. **For each proposal across all three documents**:
   a. Score it on the 4 dimensions (complexity, overhead, impact, generalizability)
   b. Calculate the composite score
   c. Assign a tier (S/A/B/C/D)
3. **Debate the merits** of each proposal:
   - Agent A (Architect): Evaluate structural soundness and integration feasibility
   - Agent B (Analyzer): Challenge impact claims and probe for hidden costs
   - Minimum 2 rounds per proposal, 3 rounds for any proposal with score disagreement >15 points
4. **Cross-proposal analysis**: Identify synergies and conflicts between proposals from different commands
5. **Produce a final ranked recommendation list** with implementation priority

### Output Requirements

Write ALL outputs to: /config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/

Required output files:
1. `debate-transcript.md` — Full adversarial debate transcript with round-by-round analysis
2. `scoring-results.md` — Tabular scoring of every proposal with dimension breakdowns
3. `final-recommendations.md` — Ranked list with implementation priorities and synergy notes
4. `cross-cutting-analysis.md` — Analysis of interactions between proposals across commands

### Scoring Protocol

Use the scoring framework at /config/workspace/IronHands-CLI/.dev/Research/process-improvement-debate/scoring-framework.md.
For each proposal, produce a scoring block:

```
### [Proposal Name] — [Source Command]
| Dimension | Raw Score | Rationale | Final Score |
|-----------|-----------|-----------|-------------|
| Complexity | X/10 | ... | (11-X) |
| Overhead | X/10 | ... | (11-X) |
| Impact | X/10 | ... | X |
| Generalizability | X/10 | ... | X |
| **Composite** | | | **XX.X/100** |
| **Tier** | | | **X-Tier** |
```

### Debate Structure

For each proposal:
```
#### Round 1
**Agent A (Architect)**: [Assessment of structural soundness, integration points, complexity estimate]
**Agent B (Analyzer)**: [Challenge on impact claims, hidden costs, practical obstacles]

#### Round 2
**Agent A**: [Response to challenges, revised assessment if warranted]
**Agent B**: [Final position, areas of agreement/disagreement]

#### Verdict
**Score**: XX.X/100 | **Tier**: X | **Confidence**: X.XX
**Key insight**: [One sentence summary of the most important finding from the debate]
```
