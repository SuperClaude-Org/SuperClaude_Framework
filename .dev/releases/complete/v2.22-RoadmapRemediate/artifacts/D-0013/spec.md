# D-0013: REMEDIATE_GATE Definition

## Implementation

`REMEDIATE_GATE` constant in `src/superclaude/cli/roadmap/gates.py`

## Gate Definition

```python
REMEDIATE_GATE = GateCriteria(
    required_frontmatter_fields=[
        "type", "source_report", "source_report_hash",
        "total_findings", "actionable", "skipped",
    ],
    min_lines=10,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(name="frontmatter_values_non_empty", ...),
        SemanticCheck(name="all_actionable_have_status", ...),
    ],
)
```

## Semantic Checks

1. `frontmatter_values_non_empty`: Rejects empty frontmatter values
2. `all_actionable_have_status`: Rejects findings without FIXED/FAILED status (PENDING fails)

## Verification

`uv run pytest tests/roadmap/test_remediate.py -k "remediate_gate"` exits 0
