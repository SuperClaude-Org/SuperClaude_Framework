"""Docs audit: minimal (broken refs + staleness) and full 5-section pass.

Minimal audit (T03.09 / D-0025):
  Broken internal references and temporal staleness.

Full docs audit (T05.01 / D-0040 / AC14-extended):
  Activated by --pass-docs flag.  Produces 5 sections:
    1. Broken references  (extends T03.09)
    2. Temporal staleness  (extends T03.09)
    3. Coverage gaps       (exported symbols without documentation)
    4. Orphaned docs       (doc files with no corresponding code referent)
    5. Style inconsistencies (heading hierarchy, link format, code block conventions)

Default staleness threshold: 365 days.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class BrokenLink:
    """A broken internal link found in a markdown file."""

    source_file: str
    target_path: str
    line_number: int
    link_text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "target_path": self.target_path,
            "line_number": self.line_number,
            "link_text": self.link_text,
        }


@dataclass
class StaleDoc:
    """A stale documentation file."""

    file_path: str
    last_modified: str  # ISO date
    days_stale: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "last_modified": self.last_modified,
            "days_stale": self.days_stale,
        }


@dataclass
class DocsAuditResult:
    """Result of the minimal docs audit."""

    broken_links: list[BrokenLink] = field(default_factory=list)
    stale_docs: list[StaleDoc] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "broken_links": [b.to_dict() for b in self.broken_links],
            "stale_docs": [s.to_dict() for s in self.stale_docs],
            "broken_link_count": len(self.broken_links),
            "stale_doc_count": len(self.stale_docs),
        }


# Markdown link pattern: [text](path)
_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def extract_internal_links(content: str) -> list[tuple[int, str, str]]:
    """Extract internal file references from markdown content.

    Returns list of (line_number, link_text, target_path).
    Only includes relative paths (not http://, mailto:, #anchors).
    """
    links = []
    for line_num, line in enumerate(content.splitlines(), start=1):
        for match in _LINK_PATTERN.finditer(line):
            text = match.group(1)
            target = match.group(2)
            # Skip external links, anchors, and images from URLs
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Strip anchors from paths
            target = target.split("#")[0]
            if target:
                links.append((line_num, text, target))
    return links


def check_broken_links(
    file_path: str,
    content: str,
    known_files: set[str],
    base_dir: str = "",
) -> list[BrokenLink]:
    """Check a markdown file for broken internal links.

    Args:
        file_path: Path to the markdown file.
        content: File content.
        known_files: Set of known file paths in the repository.
        base_dir: Base directory for resolving relative paths.
    """
    broken = []
    file_dir = os.path.dirname(file_path)

    for line_num, text, target in extract_internal_links(content):
        # Resolve relative path
        resolved = os.path.normpath(os.path.join(file_dir, target))

        if resolved not in known_files:
            broken.append(BrokenLink(
                source_file=file_path,
                target_path=target,
                line_number=line_num,
                link_text=text,
            ))

    return broken


def check_staleness(
    file_path: str,
    last_modified_iso: str | None = None,
    threshold_days: int = 365,
    current_date: datetime | None = None,
) -> StaleDoc | None:
    """Check if a doc file is stale based on last modification date.

    Args:
        file_path: Path to the doc file.
        last_modified_iso: ISO date of last git modification.
        threshold_days: Days after which a doc is considered stale.
        current_date: Current date for comparison (default: now).

    Returns:
        StaleDoc if stale, None otherwise.
    """
    if not last_modified_iso or last_modified_iso == "unknown":
        return None

    now = current_date or datetime.now(timezone.utc)

    try:
        modified = datetime.fromisoformat(last_modified_iso.replace("Z", "+00:00"))
        if modified.tzinfo is None:
            modified = modified.replace(tzinfo=timezone.utc)
        days_since = (now - modified).days
        if days_since > threshold_days:
            return StaleDoc(
                file_path=file_path,
                last_modified=last_modified_iso,
                days_stale=days_since,
            )
    except (ValueError, TypeError):
        pass

    return None


def audit_docs(
    doc_files: dict[str, str],
    known_files: set[str],
    last_modified: dict[str, str] | None = None,
    threshold_days: int = 365,
    current_date: datetime | None = None,
) -> DocsAuditResult:
    """Run minimal docs audit on markdown files.

    Args:
        doc_files: Mapping of file_path -> content for doc files.
        known_files: All known file paths in the repository.
        last_modified: Mapping of file_path -> ISO date of last git modification.
        threshold_days: Days after which a doc is considered stale.
        current_date: Current date for staleness check.

    Returns:
        DocsAuditResult with broken links and stale docs.
    """
    result = DocsAuditResult()
    modified_dates = last_modified or {}

    for file_path, content in doc_files.items():
        # Check broken links
        broken = check_broken_links(file_path, content, known_files)
        result.broken_links.extend(broken)

        # Check staleness
        stale = check_staleness(
            file_path,
            modified_dates.get(file_path),
            threshold_days=threshold_days,
            current_date=current_date,
        )
        if stale:
            result.stale_docs.append(stale)

    return result


# ---------------------------------------------------------------------------
# Full docs audit (T05.01 / D-0040) -- 3 additional sections
# ---------------------------------------------------------------------------


@dataclass
class CoverageGap:
    """An exported symbol without corresponding documentation."""

    symbol_name: str
    source_file: str

    def to_dict(self) -> dict[str, Any]:
        return {"symbol_name": self.symbol_name, "source_file": self.source_file}


@dataclass
class OrphanedDoc:
    """A doc file with no corresponding code referent."""

    doc_file: str

    def to_dict(self) -> dict[str, Any]:
        return {"doc_file": self.doc_file}


@dataclass
class StyleIssue:
    """A style inconsistency in a documentation file."""

    file_path: str
    line_number: int
    issue_type: str  # heading_hierarchy | link_format | code_block_convention
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "issue_type": self.issue_type,
            "description": self.description,
        }


@dataclass
class FullDocsAuditResult:
    """5-section result for --pass-docs full audit."""

    broken_links: list[BrokenLink] = field(default_factory=list)
    stale_docs: list[StaleDoc] = field(default_factory=list)
    coverage_gaps: list[CoverageGap] = field(default_factory=list)
    orphaned_docs: list[OrphanedDoc] = field(default_factory=list)
    style_issues: list[StyleIssue] = field(default_factory=list)

    @property
    def section_count(self) -> int:
        return 5

    def to_dict(self) -> dict[str, Any]:
        return {
            "broken_references": [b.to_dict() for b in self.broken_links],
            "temporal_staleness": [s.to_dict() for s in self.stale_docs],
            "coverage_gaps": [c.to_dict() for c in self.coverage_gaps],
            "orphaned_docs": [o.to_dict() for o in self.orphaned_docs],
            "style_inconsistencies": [si.to_dict() for si in self.style_issues],
            "section_count": self.section_count,
        }


# Heading pattern: lines starting with 1+ '#' characters
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")


def detect_coverage_gaps(
    exported_symbols: dict[str, list[str]],
    doc_files: dict[str, str],
) -> list[CoverageGap]:
    """Find exported symbols without documentation.

    Args:
        exported_symbols: Mapping source_file -> list of exported symbol names.
        doc_files: Mapping doc_file_path -> content.

    Returns:
        List of CoverageGap for undocumented symbols.
    """
    # Build a set of all symbol names mentioned in any doc file
    documented_names: set[str] = set()
    for content in doc_files.values():
        # Match backtick-quoted names and heading words
        documented_names.update(re.findall(r"`([^`]+)`", content))
        for line in content.splitlines():
            m = _HEADING_PATTERN.match(line)
            if m:
                documented_names.update(m.group(2).split())

    gaps = []
    for source_file, symbols in exported_symbols.items():
        for sym in symbols:
            if sym not in documented_names:
                gaps.append(CoverageGap(symbol_name=sym, source_file=source_file))
    return gaps


def detect_orphaned_docs(
    doc_files: dict[str, str],
    code_files: set[str],
) -> list[OrphanedDoc]:
    """Find doc files with no corresponding code file.

    A doc is considered orphaned if no code file shares its stem name.

    Args:
        doc_files: Mapping doc_file_path -> content.
        code_files: Set of code file paths in the repository.
    """
    code_stems = set()
    for cf in code_files:
        stem = os.path.splitext(os.path.basename(cf))[0]
        code_stems.add(stem.lower())

    orphaned = []
    for doc_path in doc_files:
        doc_stem = os.path.splitext(os.path.basename(doc_path))[0].lower()
        # Skip generic doc names that don't correspond to code
        if doc_stem in ("readme", "changelog", "contributing", "license", "index"):
            continue
        if doc_stem not in code_stems:
            orphaned.append(OrphanedDoc(doc_file=doc_path))
    return orphaned


def check_style_issues(
    file_path: str,
    content: str,
) -> list[StyleIssue]:
    """Check a doc file for style inconsistencies.

    Checks:
      1. Heading hierarchy: H1 should appear at most once, levels shouldn't skip.
      2. Link format: bare URLs without markdown link syntax.
      3. Code block conventions: unclosed fenced code blocks.
    """
    issues: list[StyleIssue] = []
    lines = content.splitlines()

    h1_count = 0
    last_heading_level = 0
    in_code_block = False
    code_block_start = 0

    for i, line in enumerate(lines, start=1):
        # Track code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                in_code_block = False
            else:
                in_code_block = True
                code_block_start = i
            continue

        if in_code_block:
            continue

        # Heading checks
        hm = _HEADING_PATTERN.match(line)
        if hm:
            level = len(hm.group(1))
            if level == 1:
                h1_count += 1
                if h1_count > 1:
                    issues.append(StyleIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type="heading_hierarchy",
                        description="Multiple H1 headings",
                    ))
            if last_heading_level > 0 and level > last_heading_level + 1:
                issues.append(StyleIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type="heading_hierarchy",
                    description=f"Heading level skipped: H{last_heading_level} -> H{level}",
                ))
            last_heading_level = level

        # Bare URL check (URLs not inside markdown link syntax or code)
        bare_urls = re.findall(r"(?<!\()(https?://\S+)(?!\))", line)
        for url in bare_urls:
            # Skip if inside a markdown link [text](url)
            if f"]({url})" in line:
                continue
            issues.append(StyleIssue(
                file_path=file_path,
                line_number=i,
                issue_type="link_format",
                description=f"Bare URL: {url}",
            ))

    # Unclosed code block
    if in_code_block:
        issues.append(StyleIssue(
            file_path=file_path,
            line_number=code_block_start,
            issue_type="code_block_convention",
            description="Unclosed fenced code block",
        ))

    return issues


def full_docs_audit(
    doc_files: dict[str, str],
    known_files: set[str],
    code_files: set[str] | None = None,
    exported_symbols: dict[str, list[str]] | None = None,
    last_modified: dict[str, str] | None = None,
    threshold_days: int = 365,
    current_date: datetime | None = None,
) -> FullDocsAuditResult:
    """Run full 5-section docs audit (--pass-docs).

    Args:
        doc_files: Mapping of doc_file_path -> content.
        known_files: All known file paths.
        code_files: Set of code file paths (for orphan detection).
        exported_symbols: Mapping source_file -> exported symbol names.
        last_modified: Mapping file_path -> ISO date.
        threshold_days: Staleness threshold in days.
        current_date: Current date for staleness check.
    """
    # Sections 1 & 2: reuse minimal audit
    minimal = audit_docs(
        doc_files, known_files, last_modified, threshold_days, current_date,
    )

    # Section 3: coverage gaps
    coverage_gaps = detect_coverage_gaps(
        exported_symbols or {}, doc_files,
    )

    # Section 4: orphaned docs
    orphaned = detect_orphaned_docs(doc_files, code_files or set())

    # Section 5: style issues
    style_issues: list[StyleIssue] = []
    for file_path, content in doc_files.items():
        style_issues.extend(check_style_issues(file_path, content))

    return FullDocsAuditResult(
        broken_links=minimal.broken_links,
        stale_docs=minimal.stale_docs,
        coverage_gaps=coverage_gaps,
        orphaned_docs=orphaned,
        style_issues=style_issues,
    )
