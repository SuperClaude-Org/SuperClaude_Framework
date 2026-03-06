# D-0001 Spec: Two-Tier Classification with Backward Mapping

## Module
`src/superclaude/cli/audit/classification.py`

## V2-to-V1 Category Mapping
| V2 Tier | V2 Action | V1 Category |
|---------|-----------|-------------|
| TIER_1 | DELETE | DELETE |
| TIER_1 | INVESTIGATE | INVESTIGATE |
| TIER_2 | KEEP | KEEP |
| TIER_2 | REORGANIZE | REORGANIZE |
| TIER_2 | ARCHIVE | DELETE |

## Determinism
`classify_finding()` is purely functional: same inputs always produce same output.
