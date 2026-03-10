# D-0028: Round 2.5 Fault-Finder Agent Prompt with 5-Category Checklist

## Overview

Round 2.5 is a new adversarial debate round inserted between Round 2 (Sequential Rebuttals) and Round 3 (Conditional Final Arguments). It deploys an independent fault-finder agent — not an advocate for any variant — that systematically probes the emerging consensus for invariant violations using a 5-category boundary-condition checklist.

## Prompt Template Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Section: `### Round 2.5: Invariant Probe (AD-1)`

## 5-Category Checklist

| # | Category | Description | Detection Targets |
|---|----------|-------------|-------------------|
| 1 | `state_variables` | Variables maintaining values/relationships across operations | Uninitialized state, mutation ordering, cross-component coupling |
| 2 | `guard_conditions` | Preconditions, postconditions, assertions protecting correctness | Missing validation, unguarded type assumptions, swallowed errors |
| 3 | `count_divergence` | Off-by-one, loop bounds, index calculations, quantity assumptions | Inclusive/exclusive ranges, length/index confusion, iteration mismatches |
| 4 | `collection_boundaries` | Empty collections, single-element, max size, ordering assumptions | Empty collection failures, degenerate cases, implicit sort/uniqueness |
| 5 | `interaction_effects` | Emergent behaviors when components/features combine | Feature conflicts, ordering-dependent side effects, sentinel collisions |

## Output Format

Each finding uses the structure:
```
ID: INV-NNN
CATEGORY: [category_name]
ASSUMPTION: [specific assumption text]
STATUS: ADDRESSED | UNADDRESSED
SEVERITY: HIGH | MEDIUM | LOW
EVIDENCE: [specific reference]
```

## Acceptance Criteria

- AC-AD1-1: Fault-finder identifies filter divergence via state_variables or guard_conditions
- AC-AD1-2: Fault-finder identifies sentinel collision via collection_boundaries or interaction_effects
- Prompt covers all 5 categories with specific probing questions per category

## Integration Point

Inserted after Round 2 `post_round_2` convergence check, before Round 3. The `post_round_2` section now references `invariant_probe` as a step and `if_blocked_by_invariants` as a gating condition.
