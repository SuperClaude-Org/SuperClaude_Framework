# D-0020: Evidence - Tiered KEEP Evidence

## Test Results

13 tests passed (0 failures):
- TestClassifyKeepTier: 4/4 passed (low=1 ref, medium=2 refs, high=3+ refs, zero refs rejected)
- TestEscalationPath: 5/5 passed (upgrade with evidence, no upgrade without evidence, multiple escalation attempts, boundary transitions, rejection flow)
- TestTierIntegration: 4/4 passed (end-to-end with profile data, batch tier assignment, confidence score accuracy, tier distribution reporting)

## Tier Assignment Verification

- 1 reference: classified as `low` with moderate confidence
- 2 references: classified as `medium` with high confidence
- 5 references: classified as `high` with very high confidence
- 0 references: rejected from KEEP pathway entirely

## Escalation Verification

- File with 1 reference + additional import evidence: upgraded from `low` to `medium`
- File with 1 reference + no additional evidence: remained `low`, returned INVESTIGATE
