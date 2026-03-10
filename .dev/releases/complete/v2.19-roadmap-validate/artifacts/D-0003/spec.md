# D-0003: Validation Gate Specifications

## Location
`src/superclaude/cli/roadmap/validate_gates.py`

## REFLECT_GATE

| Property | Value |
|----------|-------|
| Enforcement | STANDARD |
| min_lines | 20 |
| Required Frontmatter | `blocking_issues_count`, `warnings_count`, `tasklist_ready` |
| Semantic Checks | `frontmatter_values_non_empty` |

## ADVERSARIAL_MERGE_GATE

| Property | Value |
|----------|-------|
| Enforcement | STRICT |
| min_lines | 30 |
| Required Frontmatter | `blocking_issues_count`, `warnings_count`, `tasklist_ready`, `validation_mode`, `validation_agents` |
| Semantic Checks | `frontmatter_values_non_empty`, `agreement_table_present` |

## Dependencies
- Imports `GateCriteria`, `SemanticCheck` from `pipeline/models.py`
- Imports `_frontmatter_values_non_empty` from `roadmap/gates.py`
- Defines `_has_agreement_table` locally (pure function: content -> bool)

## Verification
```
uv run python -c "from superclaude.cli.roadmap.validate_gates import REFLECT_GATE, ADVERSARIAL_MERGE_GATE; print('OK')"
```
Exits 0.
