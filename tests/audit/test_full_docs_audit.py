"""Tests for full 5-section docs audit (T05.01 / D-0040)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from superclaude.cli.audit.docs_audit import (
    CoverageGap,
    FullDocsAuditResult,
    OrphanedDoc,
    StyleIssue,
    check_style_issues,
    detect_coverage_gaps,
    detect_orphaned_docs,
    full_docs_audit,
)


class TestDetectCoverageGaps:
    def test_undocumented_symbol_detected(self):
        exported = {"src/utils.py": ["calculate_tax", "parse_date"]}
        docs = {"docs/utils.md": "# Utils\n\nUse `parse_date` for dates.\n"}
        gaps = detect_coverage_gaps(exported, docs)
        assert len(gaps) == 1
        assert gaps[0].symbol_name == "calculate_tax"

    def test_all_documented_no_gaps(self):
        exported = {"src/utils.py": ["parse_date"]}
        docs = {"docs/utils.md": "Use `parse_date` here.\n"}
        gaps = detect_coverage_gaps(exported, docs)
        assert len(gaps) == 0

    def test_empty_exports_no_gaps(self):
        gaps = detect_coverage_gaps({}, {"docs/x.md": "content"})
        assert len(gaps) == 0

    def test_heading_words_count_as_documented(self):
        exported = {"src/foo.py": ["FooClass"]}
        docs = {"docs/foo.md": "## FooClass\n\nDetails here.\n"}
        gaps = detect_coverage_gaps(exported, docs)
        assert len(gaps) == 0


class TestDetectOrphanedDocs:
    def test_orphaned_doc_detected(self):
        doc_files = {"docs/widget.md": "# Widget\n"}
        code_files = {"src/utils.py", "src/main.py"}
        orphaned = detect_orphaned_docs(doc_files, code_files)
        assert len(orphaned) == 1
        assert orphaned[0].doc_file == "docs/widget.md"

    def test_matched_doc_not_orphaned(self):
        doc_files = {"docs/utils.md": "# Utils\n"}
        code_files = {"src/utils.py"}
        orphaned = detect_orphaned_docs(doc_files, code_files)
        assert len(orphaned) == 0

    def test_readme_never_orphaned(self):
        doc_files = {"README.md": "# Project\n"}
        orphaned = detect_orphaned_docs(doc_files, set())
        assert len(orphaned) == 0

    def test_changelog_never_orphaned(self):
        doc_files = {"CHANGELOG.md": "# Changes\n"}
        orphaned = detect_orphaned_docs(doc_files, set())
        assert len(orphaned) == 0

    def test_case_insensitive_matching(self):
        doc_files = {"docs/Utils.md": "# Utils\n"}
        code_files = {"src/utils.py"}
        orphaned = detect_orphaned_docs(doc_files, code_files)
        assert len(orphaned) == 0


class TestCheckStyleIssues:
    def test_multiple_h1_flagged(self):
        content = "# Title\n\n# Another Title\n"
        issues = check_style_issues("doc.md", content)
        h1_issues = [i for i in issues if i.description == "Multiple H1 headings"]
        assert len(h1_issues) == 1

    def test_heading_level_skip(self):
        content = "# Title\n\n### Subsection\n"
        issues = check_style_issues("doc.md", content)
        skip_issues = [i for i in issues if "skipped" in i.description]
        assert len(skip_issues) == 1
        assert "H1 -> H3" in skip_issues[0].description

    def test_bare_url_flagged(self):
        content = "Visit https://example.com for details.\n"
        issues = check_style_issues("doc.md", content)
        url_issues = [i for i in issues if i.issue_type == "link_format"]
        assert len(url_issues) == 1

    def test_markdown_link_not_flagged(self):
        content = "Visit [Example](https://example.com) for details.\n"
        issues = check_style_issues("doc.md", content)
        url_issues = [i for i in issues if i.issue_type == "link_format"]
        assert len(url_issues) == 0

    def test_unclosed_code_block(self):
        content = "```python\ndef foo():\n    pass\n"
        issues = check_style_issues("doc.md", content)
        cb_issues = [i for i in issues if i.issue_type == "code_block_convention"]
        assert len(cb_issues) == 1

    def test_closed_code_block_ok(self):
        content = "```python\ndef foo():\n    pass\n```\n"
        issues = check_style_issues("doc.md", content)
        cb_issues = [i for i in issues if i.issue_type == "code_block_convention"]
        assert len(cb_issues) == 0

    def test_no_issues_clean_doc(self):
        content = "# Title\n\n## Section\n\nSome text.\n"
        issues = check_style_issues("doc.md", content)
        assert len(issues) == 0


class TestFullDocsAudit:
    def test_produces_5_sections(self):
        now = datetime(2026, 3, 5, tzinfo=timezone.utc)
        doc_files = {
            "docs/README.md": "# Project\n\n[Missing](./missing.md)\n",
            "docs/old.md": "# Old doc\n",
            "docs/widget.md": "# Widget\n\n# Another H1\n",
        }
        known_files = {"docs/README.md", "docs/old.md", "docs/widget.md"}
        code_files = {"src/utils.py", "src/main.py"}
        exported = {"src/utils.py": ["undocumented_func"]}
        last_modified = {
            "docs/README.md": "2026-01-01T00:00:00+00:00",
            "docs/old.md": "2023-01-01T00:00:00+00:00",
            "docs/widget.md": "2026-01-01T00:00:00+00:00",
        }

        result = full_docs_audit(
            doc_files=doc_files,
            known_files=known_files,
            code_files=code_files,
            exported_symbols=exported,
            last_modified=last_modified,
            threshold_days=365,
            current_date=now,
        )

        assert result.section_count == 5
        assert len(result.broken_links) >= 1
        assert len(result.stale_docs) >= 1
        assert len(result.coverage_gaps) >= 1
        assert len(result.orphaned_docs) >= 1  # widget.md has no code match
        assert len(result.style_issues) >= 1   # multiple H1

    def test_to_dict_has_all_sections(self):
        result = full_docs_audit({}, set())
        d = result.to_dict()
        assert d["section_count"] == 5
        assert "broken_references" in d
        assert "temporal_staleness" in d
        assert "coverage_gaps" in d
        assert "orphaned_docs" in d
        assert "style_inconsistencies" in d

    def test_empty_input_no_crash(self):
        result = full_docs_audit({}, set())
        assert result.section_count == 5
        assert len(result.broken_links) == 0
        assert len(result.coverage_gaps) == 0
