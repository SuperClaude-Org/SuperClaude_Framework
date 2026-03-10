# D-0026: Certification Report Generator

## Task: T05.03 | Roadmap Item: R-034

### Deliverable
Report generator producing `certification-report.md` with YAML frontmatter and per-finding results table per spec §2.4.3.

### Implementation
- **File**: `src/superclaude/cli/roadmap/certify_prompts.py`
- Functions: `generate_certification_report(results, findings) -> str`, `parse_certification_output(output) -> list[dict]`
- YAML frontmatter: findings_verified, findings_passed, findings_failed, certified, certification_date
- Per-finding table: Finding | Severity | Result | Justification columns
- `certified` field derived from whether all findings passed

### Verification
- `uv run pytest tests/roadmap/test_certify_prompts.py -k "report"` exits 0 (8 tests pass)
