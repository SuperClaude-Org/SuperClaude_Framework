# D-0040 Spec: Full Docs Audit Pass (--pass-docs)

## Task Reference
- Task: T05.01
- Roadmap Item: R-040
- AC: AC14 (extended)

## 5-Section Output Format

The `--pass-docs` flag activates a full documentation audit producing these sections:

1. **broken_references**: Internal markdown links pointing to non-existent files
2. **temporal_staleness**: Doc files with last-modified date exceeding threshold (default 365 days)
3. **coverage_gaps**: Exported code symbols without corresponding documentation mentions
4. **orphaned_docs**: Doc files with no corresponding code file (by stem name matching)
5. **style_inconsistencies**: Heading hierarchy violations, bare URLs, unclosed code blocks

## API

```python
from superclaude.cli.audit.docs_audit import full_docs_audit, FullDocsAuditResult

result: FullDocsAuditResult = full_docs_audit(
    doc_files={"path": "content"},
    known_files={"path1", "path2"},
    code_files={"src/utils.py"},
    exported_symbols={"src/utils.py": ["func_name"]},
    last_modified={"path": "2024-01-01T00:00:00+00:00"},
)

assert result.section_count == 5
d = result.to_dict()
# Keys: broken_references, temporal_staleness, coverage_gaps, orphaned_docs, style_inconsistencies, section_count
```

## Style Checks
- **heading_hierarchy**: Multiple H1, skipped levels (H1 -> H3)
- **link_format**: Bare URLs not wrapped in markdown link syntax
- **code_block_convention**: Unclosed fenced code blocks

## Implementation
- Source: `src/superclaude/cli/audit/docs_audit.py`
- Tests: `tests/audit/test_full_docs_audit.py` (19 tests)
