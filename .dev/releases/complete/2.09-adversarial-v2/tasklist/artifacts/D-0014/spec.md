# D-0014: Three-Level Taxonomy (L1/L2/L3) Definition in SKILL.md

## Overview

Three-level debate topic taxonomy defined in SKILL.md with >=5 auto-tag signals per level, including A-NNN auto-tagging rules for L3.

## Taxonomy Levels

| Level | Name | Description | Signal Count |
|-------|------|-------------|--------------|
| L1 | Surface | Naming, formatting, style, wording | 6 signals |
| L2 | Structural | Architecture, organization, API design | 7 signals |
| L3 | State Mechanics | State management, guards, boundaries, concurrency | 8 signals |

## Auto-Tag Signals

### L1 (Surface): 6 signals
1. naming convention
2. formatting
3. wording
4. style choice
5. cosmetic
6. presentation

### L2 (Structural): 7 signals
1. architecture
2. API design
3. component
4. module
5. interface
6. dependency
7. organization

### L3 (State Mechanics): 8 signals
1. state
2. guard
3. boundary
4. invariant
5. concurrency
6. race condition
7. validation rule
8. transition

## Auto-Tag Rules

- Priority: L3 > L2 > L1 (highest matching level wins)
- A-NNN auto-tag: Shared assumption points with state/guard/boundary terms auto-tag as L3 (AC-AD5-3)
- Fallback: If no signals match, default to L2
- Each diff point gets exactly one level

## AC-AD5-3 Test

- Input: A-NNN point with text containing "state transition guard"
- Expected: Auto-tagged as L3

## Deliverable Status

- **Task**: T02.10
- **Roadmap Item**: R-014
- **Status**: COMPLETE
- **Tier**: STRICT
