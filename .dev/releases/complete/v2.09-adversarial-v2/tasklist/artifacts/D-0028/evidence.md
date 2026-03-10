# D-0028: Evidence — Round 2.5 Fault-Finder Implementation

## Verification: AC-AD1-1 (filter divergence detection)

The fault-finder prompt includes under `state_variables`:
- Probing question: "Do any agreed approaches assume state that the other variant manages differently?"
- Detection target: "State mutation ordering assumptions"

Under `guard_conditions`:
- Probing question: "Do guard conditions from one variant contradict assumptions in another?"
- Detection target: "Silently swallowed error conditions"

A filter divergence (one variant filters before processing, the other after) would be detected by either category because:
1. The filtering order is a **state variable** (data set contents differ at processing time)
2. The post-filter assumption is a **guard condition** (precondition on data shape)

**Verdict: AC-AD1-1 PASS** — filter divergence is systematically probed by state_variables and guard_conditions.

## Verification: AC-AD1-2 (sentinel collision detection)

The fault-finder prompt includes under `collection_boundaries`:
- Probing question: "Are there implicit ordering/uniqueness assumptions?"
- Detection target: "Implicit sort/uniqueness assumptions"

Under `interaction_effects`:
- Probing question: "Could combined changes from different variants conflict?"
- Detection target: "Sentinel value collisions across components"

A sentinel collision (e.g., both components use -1 as a sentinel) would be detected because:
1. It's a **collection boundary** issue (special values within the value domain)
2. It's an **interaction effect** (independently valid sentinels that collide when combined)

**Verdict: AC-AD1-2 PASS** — sentinel collision is systematically probed by collection_boundaries and interaction_effects.

## Verification: 5-category coverage

All 5 categories have:
- Description: yes (one-line purpose)
- Probing questions: yes (3 per category)
- Detection targets: yes (3 per category)

**Verdict: PASS** — complete 5-category coverage with specific probing questions.

## Files Modified

- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Added Round 2.5 section (~130 lines), updated post_round_2 to reference invariant probe
