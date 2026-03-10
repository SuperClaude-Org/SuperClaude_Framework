# D-0028: CERTIFY_GATE Definition

## Task: T05.05 | Roadmap Item: R-036

### Deliverable
`CERTIFY_GATE` GateCriteria instance per spec §2.4.5.

### Implementation
- **File**: `src/superclaude/cli/roadmap/gates.py`
- Required frontmatter: findings_verified, findings_passed, findings_failed, certified, certification_date
- min_lines: 15
- enforcement_tier: STRICT
- Semantic checks: `frontmatter_values_non_empty` (reused), `per_finding_table_present` (new)
- `_has_per_finding_table()` checks for table header with required columns AND at least one data row

### Verification
- `uv run pytest tests/roadmap/test_certify_gates.py` exits 0 (12 tests pass)
