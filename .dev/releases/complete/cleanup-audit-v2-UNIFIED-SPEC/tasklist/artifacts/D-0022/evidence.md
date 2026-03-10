# D-0022: Evidence - 3-Tier Dependency Graph Builder

## Test Results

10 tests passed (0 failures):
- TestGraphConstruction: 3/3 passed (empty graph, single edge, multi-tier edges)
- TestTierClassification: 3/3 passed (AST import -> Tier A, grep match -> Tier B, inferred -> Tier C)
- TestTierCPolicy: 2/2 passed (Tier-C excluded from DELETE promotion, Tier-C visible in graph output)
- TestQueryMethods: 2/2 passed (query_importers groups by tier, query_exports returns correct targets)

## Tier Confidence Verification

- Tier-A edge: confidence = 0.90 (verified against AST-parsed import)
- Tier-B edge: confidence = 0.65 (verified against grep pattern match)
- Tier-C edge: confidence = 0.35 (verified against inferred relationship)

## Tier-C Safety Verification

Test with file having only Tier-C importers:
- File not promoted to DELETE despite having dependency edges
- Classification remains INVESTIGATE due to insufficient evidence tier
