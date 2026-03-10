"""Certification prompt builder, context extractor, report generator, and outcome router.

All functions in this module are pure (no I/O, no subprocess calls, no side
effects) per NFR-004.

Provides:
- build_certification_prompt(findings, context_sections) -> str  (T05.01)
- extract_finding_context(file_content, finding) -> str  (T05.02)
- generate_certification_report(results, findings) -> str  (T05.03)
- route_certification_outcome(results) -> dict  (T05.04)
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .models import Finding


def build_certification_prompt(
    findings: list[Finding],
    context_sections: dict[str, str],
) -> str:
    """Build a certification agent prompt per spec section 2.4.2 template.

    Produces prompt with:
    - Header: "You are a certification specialist..."
    - Per-finding verification checklist (original issue, fix applied, check instruction)
    - Output format: PASS/FAIL per finding with one-line justification

    Accepts pre-extracted context sections (not full file content) per NFR-011.

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    lines: list[str] = []

    # Header
    lines.append(
        "You are a certification specialist. Your task is to verify that "
        "remediation fixes were applied correctly. Be skeptical -- check that "
        "each fix actually addresses the original issue, not just that the "
        "file was modified."
    )
    lines.append("")

    # Context sections
    if context_sections:
        lines.append("## Context Sections")
        lines.append("")
        for section_key, section_content in context_sections.items():
            lines.append(f"### {section_key}")
            lines.append("")
            lines.append(section_content)
            lines.append("")

    # Per-finding verification checklist
    lines.append("## Findings to Verify")
    lines.append("")
    for f in findings:
        lines.append(f"### {f.id} [{f.severity}]")
        lines.append("")
        lines.append(f"- **Original Issue**: {f.description}")
        lines.append(f"- **Location**: {f.location}")
        lines.append(f"- **Fix Guidance**: {f.fix_guidance}")
        lines.append(f"- **Check Instruction**: Verify that the fix at `{f.location}` "
                      f"addresses: {f.description}")
        lines.append("")

    # Output format requirement
    lines.append("## Output Format")
    lines.append("")
    lines.append("For EACH finding above, output exactly one line in this format:")
    lines.append("")
    lines.append("```")
    lines.append("FINDING_ID: PASS|FAIL -- one-line justification")
    lines.append("```")
    lines.append("")
    lines.append("Example:")
    lines.append("```")
    lines.append("F-01: PASS -- Milestone count updated from 3 to 5 matching spec")
    lines.append("F-02: FAIL -- Section header changed but content still references old value")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def extract_finding_context(
    file_content: str,
    finding: Finding,
) -> str:
    """Extract the section surrounding a finding's location from file content.

    Handles two location formats:
    - Section references: "file.md:section X.Y" or "file.md:heading text"
    - Line-range references: "file.md:85" or "file.md:85-92"

    Returns the extracted context (section heading + content through next
    same-level heading), not full file content, per NFR-011.

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    if not file_content or not finding.location:
        return ""

    # Try line-range extraction first
    line_match = re.search(r":(\d+)(?:-(\d+))?", finding.location)
    if line_match:
        start_line = int(line_match.group(1))
        end_line = int(line_match.group(2)) if line_match.group(2) else start_line
        return _extract_by_lines(file_content, start_line, end_line)

    # Try section reference extraction
    section_match = re.search(r"[§:](\d+(?:\.\d+)*)", finding.location)
    if section_match:
        section_ref = section_match.group(1)
        return _extract_by_section(file_content, section_ref)

    # Fallback: return first 20 lines as context
    content_lines = file_content.splitlines()
    return "\n".join(content_lines[:20])


def _extract_by_lines(content: str, start: int, end: int, context: int = 5) -> str:
    """Extract lines around a range with context window."""
    lines = content.splitlines()
    # Convert to 0-indexed
    actual_start = max(0, start - 1 - context)
    actual_end = min(len(lines), end + context)

    # Expand to include enclosing section heading
    for i in range(actual_start - 1, -1, -1):
        if lines[i].startswith("#"):
            actual_start = i
            break

    return "\n".join(lines[actual_start:actual_end])


def _extract_by_section(content: str, section_ref: str) -> str:
    """Extract a section by heading number reference."""
    lines = content.splitlines()
    target_idx = -1
    target_level = 0

    # Find the heading containing the section reference
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#") and section_ref in stripped:
            target_idx = i
            target_level = len(stripped) - len(stripped.lstrip("#"))
            break

    if target_idx == -1:
        return ""

    # Extract content until next same-level or higher heading
    end_idx = len(lines)
    for i in range(target_idx + 1, len(lines)):
        stripped = lines[i].lstrip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            if level <= target_level:
                end_idx = i
                break

    return "\n".join(lines[target_idx:end_idx])


def generate_certification_report(
    results: list[dict],
    findings: list[Finding],
) -> str:
    """Generate certification-report.md with YAML frontmatter per spec section 2.4.3.

    Parameters:
    - results: list of dicts with keys: finding_id, result (PASS/FAIL), justification
    - findings: original Finding objects for severity lookup

    Returns markdown string with:
    - YAML frontmatter: findings_verified, findings_passed, findings_failed,
      certified, certification_date
    - Per-finding results table: Finding | Severity | Result | Justification
    - Summary section

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    # Build lookup for severity
    severity_map = {f.id: f.severity for f in findings}

    findings_verified = len(results)
    findings_passed = sum(1 for r in results if r.get("result") == "PASS")
    findings_failed = sum(1 for r in results if r.get("result") == "FAIL")
    certified = findings_failed == 0 and findings_verified > 0
    certification_date = datetime.now(timezone.utc).isoformat()

    lines: list[str] = []

    # YAML frontmatter
    lines.append("---")
    lines.append(f"findings_verified: {findings_verified}")
    lines.append(f"findings_passed: {findings_passed}")
    lines.append(f"findings_failed: {findings_failed}")
    lines.append(f"certified: {str(certified).lower()}")
    lines.append(f"certification_date: {certification_date}")
    lines.append("---")
    lines.append("")

    # Title
    lines.append("# Certification Report")
    lines.append("")

    # Per-finding results table
    lines.append("## Per-Finding Results")
    lines.append("")
    lines.append("| Finding | Severity | Result | Justification |")
    lines.append("|---------|----------|--------|---------------|")
    for r in results:
        fid = r.get("finding_id", "unknown")
        severity = severity_map.get(fid, "UNKNOWN")
        result = r.get("result", "UNKNOWN")
        justification = r.get("justification", "")
        lines.append(f"| {fid} | {severity} | {result} | {justification} |")
    lines.append("")

    # Summary section
    lines.append("## Summary")
    lines.append("")
    if certified:
        lines.append(
            f"All {findings_verified} findings verified. "
            f"{findings_passed} passed, {findings_failed} failed. "
            "Certification: **CERTIFIED**."
        )
    else:
        lines.append(
            f"{findings_verified} findings verified. "
            f"{findings_passed} passed, {findings_failed} failed. "
            "Certification: **CERTIFIED WITH CAVEATS**."
        )
    lines.append("")

    return "\n".join(lines)


def parse_certification_output(output: str) -> list[dict]:
    """Parse certification agent output into structured results.

    Expected format per line: FINDING_ID: PASS|FAIL -- justification

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    results: list[dict] = []
    pattern = re.compile(
        r"(F-\d+)\s*:\s*(PASS|FAIL)\s*--\s*(.+)",
        re.IGNORECASE,
    )
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            results.append({
                "finding_id": match.group(1),
                "result": match.group(2).upper(),
                "justification": match.group(3).strip(),
            })
    return results


def route_certification_outcome(
    results: list[dict],
) -> dict:
    """Route certification outcomes per spec section 2.4.4.

    Maps certification results to state updates:
    - All pass: validation.status = "certified", tasklist_ready = true
    - Some fail: validation.status = "certified-with-caveats", failure list in report

    No automatic loop: pipeline completes after single certification pass (NFR-012).

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    findings_passed = sum(1 for r in results if r.get("result") == "PASS")
    findings_failed = sum(1 for r in results if r.get("result") == "FAIL")
    total = len(results)

    if findings_failed == 0 and total > 0:
        return {
            "status": "certified",
            "tasklist_ready": True,
            "findings_passed": findings_passed,
            "findings_failed": 0,
            "loop": False,  # NFR-012: no automatic loop
        }
    else:
        failed_ids = [
            r["finding_id"] for r in results if r.get("result") == "FAIL"
        ]
        return {
            "status": "certified-with-caveats",
            "tasklist_ready": False,
            "findings_passed": findings_passed,
            "findings_failed": findings_failed,
            "failed_findings": failed_ids,
            "loop": False,  # NFR-012: no automatic loop
        }
