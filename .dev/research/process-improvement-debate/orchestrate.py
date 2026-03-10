#!/usr/bin/env python3
"""
Process Improvement Orchestration Script
=========================================

Multi-agent brainstorm → score → adversarial debate pipeline.

Spawns 3 parallel brainstorm agents (one per command: sc:spec-panel, sc:adversarial,
sc:roadmap), collects proposals, builds a scoring framework, then spawns an
adversarial debate agent to evaluate and score each proposal.

All artifacts are written to .md files in the output directory for downstream
agent consumption.

Usage:
    python orchestrate.py

    Or from Claude Code:
    /sc:task "Run the orchestration script at .dev/Research/process-improvement-debate/orchestrate.py"

Design Notes:
    - This script is intended to be executed BY Claude Code (not standalone Python).
    - It generates a series of Claude Code prompts that should be run as parallel agents.
    - The script itself writes the prompt files and a run-order manifest.
    - A human or orchestrating agent then executes the prompts in the specified order.
"""

import json
import os
import textwrap
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent
PROMPTS_DIR = OUTPUT_DIR / "prompts"
PROMPTS_DIR.mkdir(exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M")

# ── Shared Context (the feedback + code evidence from the adversarial debate) ──
SHARED_CONTEXT = textwrap.dedent("""\
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
""")

# ── Phase 1: Brainstorm Prompts ───────────────────────────────────────────

BRAINSTORM_SPEC_PANEL = textwrap.dedent(f"""\
/sc:brainstorm --strategy systematic --depth deep

## Topic: Improving /sc:spec-panel to Catch State-Machine Edge Cases

{SHARED_CONTEXT}

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
""")

BRAINSTORM_ADVERSARIAL = textwrap.dedent(f"""\
/sc:brainstorm --strategy systematic --depth deep

## Topic: Improving /sc:adversarial to Catch Implementation-Level Flaws

{SHARED_CONTEXT}

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
""")

BRAINSTORM_ROADMAP = textwrap.dedent(f"""\
/sc:brainstorm --strategy systematic --depth deep

## Topic: Improving /sc:roadmap to Surface Edge-Case Risks Earlier

{SHARED_CONTEXT}

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
""")

# ── Phase 2: Scoring Framework ────────────────────────────────────────────

SCORING_FRAMEWORK = textwrap.dedent("""\
# Proposal Scoring Framework

## Dimensions

Each proposal is scored on 4 dimensions, each rated 1-10:

### 1. Implementation Complexity (LOWER is better → inverted for final score)
- **1-3 (Low)**: Prompt/template change only. No structural workflow changes. <1 day effort.
- **4-6 (Medium)**: New review phase or checklist. Moderate protocol restructuring. 1-3 days.
- **7-10 (High)**: New agent roles, major workflow restructuring, cross-command changes. >3 days.
- **Scoring**: Final score = 11 - raw_score (inverted so simpler = higher score)

### 2. Cost/Time Overhead per Invocation (LOWER is better → inverted)
- **1-3 (Low)**: <10% additional tokens/time per command invocation. Negligible UX impact.
- **4-6 (Medium)**: 10-30% additional overhead. Noticeable but acceptable.
- **7-10 (High)**: >30% additional overhead. Significant UX impact, may need opt-in flag.
- **Scoring**: Final score = 11 - raw_score (inverted so cheaper = higher score)

### 3. Likelihood of Impact (HIGHER is better → direct)
- **1-3 (Low)**: Would catch <20% of state-machine edge case classes. Narrow applicability.
- **4-6 (Medium)**: Would catch 20-60% of edge case classes. Moderate breadth.
- **7-10 (High)**: Would catch >60% of edge case classes. Broad applicability across domains.
- **Scoring**: Direct (higher = better)

### 4. Generalizability (HIGHER is better → direct)
- **1-3 (Low)**: Only applies to one command or one type of specification.
- **4-6 (Medium)**: Applies to 2-3 commands or moderate range of specification types.
- **7-10 (High)**: Applies across all review/debate/roadmap commands. Universal principle.
- **Scoring**: Direct (higher = better)

## Composite Score Formula

```
composite = (
    (11 - complexity) * 0.20 +    # 20% weight: prefer simpler changes
    (11 - overhead) * 0.15 +      # 15% weight: prefer cheaper runtime cost
    impact * 0.40 +                # 40% weight: primary criterion
    generalizability * 0.25        # 25% weight: cross-command value
) / 10 * 100  # normalize to 0-100
```

## Tier Classification

| Score Range | Tier | Recommendation |
|-------------|------|----------------|
| 80-100 | S-Tier | Implement immediately |
| 65-79 | A-Tier | Implement in next release cycle |
| 50-64 | B-Tier | Consider with modifications |
| 35-49 | C-Tier | Defer or redesign |
| 0-34 | D-Tier | Do not implement |

## Debate Evaluation Criteria

When debating proposals, agents should:
1. Challenge the claimed impact score with concrete counter-examples
2. Probe whether the overhead estimate accounts for worst-case scenarios
3. Test generalizability by applying the proposal to 2-3 different specification domains
4. Verify the implementation sketch is realistic and doesn't hand-wave complexity
5. Consider interaction effects between proposals from different commands
""")

# ── Phase 3: Adversarial Debate Prompt ────────────────────────────────────

def build_adversarial_prompt():
    """Build the adversarial debate prompt that references the brainstorm outputs."""
    return textwrap.dedent(f"""\
/sc:adversarial --depth deep --convergence 0.85

## Adversarial Evaluation of Process Improvement Proposals

### Context

Three brainstorm sessions produced proposals for improving our specification/review
pipeline. Each focused on one command:
- **spec-panel proposals**: {OUTPUT_DIR}/brainstorm-spec-panel.md
- **adversarial proposals**: {OUTPUT_DIR}/brainstorm-adversarial.md
- **roadmap proposals**: {OUTPUT_DIR}/brainstorm-roadmap.md

The scoring framework is defined in: {OUTPUT_DIR}/scoring-framework.md

### Background (Why We're Doing This)

{SHARED_CONTEXT}

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

Write ALL outputs to: {OUTPUT_DIR}/

Required output files:
1. `debate-transcript.md` — Full adversarial debate transcript with round-by-round analysis
2. `scoring-results.md` — Tabular scoring of every proposal with dimension breakdowns
3. `final-recommendations.md` — Ranked list with implementation priorities and synergy notes
4. `cross-cutting-analysis.md` — Analysis of interactions between proposals across commands

### Scoring Protocol

Use the scoring framework at {OUTPUT_DIR}/scoring-framework.md.
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
""")


# ── Write All Artifacts ───────────────────────────────────────────────────

def write_artifacts():
    """Write all prompt files and the manifest."""

    # Phase 1: Brainstorm prompts
    prompts = {
        "01-brainstorm-spec-panel.md": BRAINSTORM_SPEC_PANEL,
        "02-brainstorm-adversarial.md": BRAINSTORM_ADVERSARIAL,
        "03-brainstorm-roadmap.md": BRAINSTORM_ROADMAP,
    }

    for filename, content in prompts.items():
        path = PROMPTS_DIR / filename
        path.write_text(content)
        print(f"  Wrote: {path}")

    # Phase 2: Scoring framework (standalone artifact)
    scoring_path = OUTPUT_DIR / "scoring-framework.md"
    scoring_path.write_text(SCORING_FRAMEWORK)
    print(f"  Wrote: {scoring_path}")

    # Phase 3: Adversarial debate prompt (written after brainstorms complete)
    adversarial_path = PROMPTS_DIR / "04-adversarial-debate.md"
    adversarial_path.write_text(build_adversarial_prompt())
    print(f"  Wrote: {adversarial_path}")

    # Manifest: execution order and dependencies
    manifest = {
        "generated_at": TIMESTAMP,
        "output_dir": str(OUTPUT_DIR),
        "phases": [
            {
                "phase": 1,
                "name": "Parallel Brainstorm",
                "description": "Spawn 3 parallel agents, each running /sc:brainstorm for one command",
                "execution": "parallel",
                "agents": [
                    {
                        "id": "brainstorm-spec-panel",
                        "prompt_file": "prompts/01-brainstorm-spec-panel.md",
                        "output_file": "brainstorm-spec-panel.md",
                        "model": "opus",
                        "agent_type": "general-purpose",
                        "description": "Brainstorm spec-panel improvements"
                    },
                    {
                        "id": "brainstorm-adversarial",
                        "prompt_file": "prompts/02-brainstorm-adversarial.md",
                        "output_file": "brainstorm-adversarial.md",
                        "model": "opus",
                        "agent_type": "general-purpose",
                        "description": "Brainstorm adversarial improvements"
                    },
                    {
                        "id": "brainstorm-roadmap",
                        "prompt_file": "prompts/03-brainstorm-roadmap.md",
                        "output_file": "brainstorm-roadmap.md",
                        "model": "opus",
                        "agent_type": "general-purpose",
                        "description": "Brainstorm roadmap improvements"
                    }
                ]
            },
            {
                "phase": 2,
                "name": "Adversarial Scoring Debate",
                "description": "Score and debate all proposals from Phase 1",
                "execution": "sequential (depends on Phase 1 completion)",
                "agents": [
                    {
                        "id": "adversarial-debate",
                        "prompt_file": "prompts/04-adversarial-debate.md",
                        "output_files": [
                            "debate-transcript.md",
                            "scoring-results.md",
                            "final-recommendations.md",
                            "cross-cutting-analysis.md"
                        ],
                        "model": "opus",
                        "agent_type": "general-purpose",
                        "description": "Adversarial debate on all proposals"
                    }
                ]
            }
        ],
        "expected_outputs": [
            "brainstorm-spec-panel.md",
            "brainstorm-adversarial.md",
            "brainstorm-roadmap.md",
            "scoring-framework.md",
            "debate-transcript.md",
            "scoring-results.md",
            "final-recommendations.md",
            "cross-cutting-analysis.md"
        ]
    }

    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"  Wrote: {manifest_path}")

    # Human/agent-readable execution guide
    execution_guide = textwrap.dedent(f"""\
# Process Improvement Debate — Execution Guide

**Generated**: {TIMESTAMP}
**Output directory**: `{OUTPUT_DIR}`

## Phase 1: Parallel Brainstorm (3 agents)

Launch these 3 agents IN PARALLEL. Each reads its prompt file and writes its
output to the specified .md file in `{OUTPUT_DIR}/`.

| Agent | Prompt | Output | Model |
|-------|--------|--------|-------|
| brainstorm-spec-panel | `prompts/01-brainstorm-spec-panel.md` | `brainstorm-spec-panel.md` | opus |
| brainstorm-adversarial | `prompts/02-brainstorm-adversarial.md` | `brainstorm-adversarial.md` | opus |
| brainstorm-roadmap | `prompts/03-brainstorm-roadmap.md` | `brainstorm-roadmap.md` | opus |

### Claude Code Agent Invocation (copy-paste ready)

For each agent, the orchestrating agent should:
1. Read the prompt file
2. Invoke `/sc:brainstorm` with the prompt content
3. Write the brainstorm output to the specified output file

## Phase 2: Adversarial Debate (1 agent, after Phase 1 completes)

| Agent | Prompt | Outputs | Model |
|-------|--------|---------|-------|
| adversarial-debate | `prompts/04-adversarial-debate.md` | `debate-transcript.md`, `scoring-results.md`, `final-recommendations.md`, `cross-cutting-analysis.md` | opus |

### Dependency

Phase 2 MUST wait for all 3 Phase 1 agents to complete and write their output files.

## Expected Final Artifacts

After both phases complete, `{OUTPUT_DIR}/` should contain:

```
{OUTPUT_DIR.name}/
├── prompts/
│   ├── 01-brainstorm-spec-panel.md      # Input prompt
│   ├── 02-brainstorm-adversarial.md     # Input prompt
│   ├── 03-brainstorm-roadmap.md         # Input prompt
│   └── 04-adversarial-debate.md         # Input prompt
├── manifest.json                         # Machine-readable execution manifest
├── execution-guide.md                    # This file
├── scoring-framework.md                  # Scoring dimensions and formula
├── brainstorm-spec-panel.md             # Phase 1 output
├── brainstorm-adversarial.md            # Phase 1 output
├── brainstorm-roadmap.md                # Phase 1 output
├── debate-transcript.md                 # Phase 2 output
├── scoring-results.md                   # Phase 2 output
├── final-recommendations.md             # Phase 2 output
└── cross-cutting-analysis.md            # Phase 2 output
```

## Scoring Framework Reference

See `scoring-framework.md` for the 4-dimension scoring system:
- Implementation Complexity (20% weight, inverted)
- Cost/Time Overhead (15% weight, inverted)
- Likelihood of Impact (40% weight, direct)
- Generalizability (25% weight, direct)

Composite formula normalizes to 0-100 with S/A/B/C/D tier classification.
""")

    guide_path = OUTPUT_DIR / "execution-guide.md"
    guide_path.write_text(execution_guide)
    print(f"  Wrote: {guide_path}")


# ── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Process Improvement Debate — Artifact Generator")
    print("=" * 60)
    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    print("Generating artifacts...")
    write_artifacts()
    print()
    print("=" * 60)
    print("All artifacts generated successfully.")
    print()
    print("Next steps:")
    print("  1. Read execution-guide.md for the full run order")
    print("  2. Phase 1: Launch 3 parallel brainstorm agents")
    print("  3. Phase 2: Launch adversarial debate agent (after Phase 1)")
    print("=" * 60)
