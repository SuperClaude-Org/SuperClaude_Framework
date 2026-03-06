# D-0020: Tiered KEEP Evidence Specification

## Reference-Count Tiers

| Tier | Reference Count | Confidence | Implication |
|------|----------------|------------|-------------|
| low | 1 reference | Moderate | File is used but only in one place; may warrant investigation |
| medium | 2 references | High | File has meaningful usage across multiple consumers |
| high | 3+ references | Very high | File is well-integrated; strong KEEP signal |

## Escalation Path

When a file's reference count is below the threshold for a confident KEEP:
1. Accept `additional_evidence` parameter with supplementary import/export data
2. Re-evaluate tier assignment with the augmented evidence
3. If tier upgrades: return upgraded KEEP with new confidence score
4. If tier remains low and no additional evidence available: reject KEEP, return INVESTIGATE

## Implementation

- Module: `src/superclaude/cli/audit/tiered_keep.py`
- `classify_keep_tier()`: maps reference count to tier label and confidence
- `evaluate_with_escalation()`: accepts additional evidence for borderline cases
- Tier thresholds are configurable but default to 1/2/3 boundaries

## Design Decision

Tier boundaries use discrete counts rather than percentile-based scoring. This keeps the logic transparent and auditable: a reviewer can verify the reference count directly against the threshold without needing project-wide statistics.
