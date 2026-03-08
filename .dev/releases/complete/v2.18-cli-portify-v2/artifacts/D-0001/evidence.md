# D-0001: Evidence — refs/pipeline-spec.md API Alignment

**Task**: T01.01
**Roadmap Items**: R-004, R-005
**Date**: 2026-03-08

## Changes Made

### 1. Gate Criteria Tiers (lines ~142-180)

| Field | Before (ref) | After (ref) | Live API (models.py) |
|-------|-------------|-------------|---------------------|
| Tier field name | `tier="strict"` | `enforcement_tier="STRICT"` | `enforcement_tier: Literal["STRICT", "STANDARD", "LIGHT", "EXEMPT"]` |
| Tier casing | lowercase (`"strict"`, `"standard"`) | UPPER_CASE (`"STRICT"`, `"STANDARD"`) | UPPER_CASE enum values |
| Frontmatter field | `required_frontmatter=` | `required_frontmatter_fields=` | `required_frontmatter_fields: list[str]` |
| SemanticCheck constructor | `fn=` | `check_fn=` | `check_fn: Callable[[str], bool]` |
| SemanticCheck missing field | (absent) | `failure_message=` | `failure_message: str` |
| GateCriteria EXEMPT/LIGHT | positional only | explicit all fields | requires `required_frontmatter_fields` and `min_lines` |

### 2. Semantic Check Functions (lines ~185-200)

| Aspect | Before (ref) | After (ref) | Live API |
|--------|-------------|-------------|----------|
| Return type | `tuple[bool, str]` | `bool` | `Callable[[str], bool]` |
| Function signature | `(content: str) -> tuple[bool, str]` | `(content: str) -> bool` | `check_fn: Callable[[str], bool]` |

## Verification

All field names in updated `refs/pipeline-spec.md` compared against live `models.py` (lines 58-74) and `gates.py` (line 20):

- `GateCriteria.required_frontmatter_fields` ✅ matches models.py:71
- `GateCriteria.min_lines` ✅ matches models.py:72
- `GateCriteria.enforcement_tier` ✅ matches models.py:73
- `GateCriteria.semantic_checks` ✅ matches models.py:74
- `SemanticCheck.name` ✅ matches models.py:62
- `SemanticCheck.check_fn` ✅ matches models.py:63
- `SemanticCheck.failure_message` ✅ matches models.py:64
- Tier values use UPPER_CASE ✅ matches Literal type constraint
- Semantic check signature `Callable[[str], bool]` ✅ matches models.py:63

**Zero field name mismatches remain.**
