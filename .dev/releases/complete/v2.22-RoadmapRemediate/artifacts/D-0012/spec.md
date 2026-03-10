# D-0012: Remediation Tasklist Generation

## Implementation

`generate_remediation_tasklist(findings: list[Finding], source_report_path: str, source_report_content: str) -> str`
in `src/superclaude/cli/roadmap/remediate.py`

## Output Format

### YAML Frontmatter
```yaml
---
type: remediation-tasklist
source_report: <path>
source_report_hash: <sha256>
generated: <iso8601>
total_findings: <int>
actionable: <int>
skipped: <int>
---
```

### Entry Format
```
- [ ] F-XX | file(s) | STATUS -- description
- [x] F-XX | file(s) | SKIPPED -- description
```

### Grouping
Findings grouped by severity: BLOCKING, WARNING, INFO, SKIPPED

## Verification

`uv run pytest tests/roadmap/test_remediate.py -k "tasklist"` exits 0
