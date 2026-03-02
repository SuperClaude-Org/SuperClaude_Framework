# Diff Analysis: cleanup-audit-v2 Roadmap Comparison

## Metadata
- Generated: 2026-02-25T00:00:00Z
- Variants compared: 3
- Total differences found: 6
- Categories: structural (2), content (2), contradictions (0), unique (2)

## Structural Differences

| # | Area | Variant 1 | Variant 2 | Variant 3 | Severity |
|---|---|---|---|---|---|
| S-001 | Milestone granularity | 6 milestones, medium detail | 6 milestones, highest detail and AC mapping | 6 milestones, minimal detail | Medium |
| S-002 | Risk/criteria structure | Separate sections with brief bullets | Explicit risk-mitigation + AC block | Minimal risk and criteria statements | Low |

## Content Differences

| # | Topic | Variant 1 Approach | Variant 2 Approach | Variant 3 Approach | Severity |
|---|---|---|---|---|---|
| C-001 | AC traceability | Mentions AC1-AC20 mapping broadly | Explicit per-milestone AC assignment | Mentions direct mapping only | High |
| C-002 | Hybrid architecture emphasis | Notes dynamic import and schema risk | Explicit static-tool-first evidence strategy | Mentions scale/non-determinism only | Medium |

## Contradictions

No direct contradictions detected across variants.

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---|---|---|
| U-001 | Variant 2 | Clear per-milestone AC mapping (M1..M6 to AC groups) | High |
| U-002 | Variant 1 | Explicit context-window pressure risk callout for Phase 3/4 | Medium |

## Summary
- Total structural differences: 2
- Total content differences: 2
- Total contradictions: 0
- Total unique contributions: 2
- Highest-severity items: C-001
