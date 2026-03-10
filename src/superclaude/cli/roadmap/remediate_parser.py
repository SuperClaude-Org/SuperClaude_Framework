"""Parser for validation reports -- extracts Finding objects.

Provides two pure functions:
- parse_validation_report(text) -> list[Finding]  (primary: merged reports)
- parse_individual_reports(report_texts) -> list[Finding]  (fallback: with dedup)
"""

from __future__ import annotations

import re

from .models import Finding

# Severity ordering for deduplication (higher index wins)
_SEVERITY_RANK = {"INFO": 0, "WARNING": 1, "BLOCKING": 2}


def parse_validation_report(text: str) -> list[Finding]:
    """Parse a merged validation report into Finding objects.

    Supports two merged report formats:
    1. reflect-merged.md -- has Agreement Table with Remediation Status column
       and Consolidated Findings sections
    2. merged-validation-report.md -- has Agreement Table (no Remediation Status)
       and Consolidated Findings sections

    Both share the Consolidated Findings structure with BLOCKING/WARNING/INFO
    subsections containing structured finding blocks.

    This is a pure function: no I/O, no subprocess calls, no side effects.

    Raises ValueError if no findings could be extracted.
    """
    findings = _parse_consolidated_findings(text)
    if not findings:
        findings = _parse_flat_findings(text)
    if not findings:
        raise ValueError(
            "No findings extracted from report. "
            "Expected '## Consolidated Findings' or '## Findings' section "
            "with structured finding blocks."
        )
    # Overlay agreement categories from the Agreement Table if present
    _overlay_agreement_categories(text, findings)
    # Overlay remediation status from Agreement Table if present
    _overlay_remediation_status(text, findings)
    return findings


def parse_individual_reports(report_texts: list[str]) -> list[Finding]:
    """Parse multiple individual reflect-*.md reports with deduplication.

    Deduplication rule (spec §8/OQ-003):
    1. Location match: same file + within 5 lines = candidate duplicate
    2. Severity resolution: higher severity wins (BLOCKING > WARNING > INFO)
    3. Fix guidance: merged from both reports

    Non-matching findings included as-is from their source report.

    This is a pure function: no I/O, no subprocess calls, no side effects.
    """
    all_findings: list[Finding] = []
    for text in report_texts:
        try:
            findings = _parse_flat_findings(text)
            if not findings:
                findings = _parse_consolidated_findings(text)
            all_findings.extend(findings)
        except ValueError:
            continue

    if not all_findings:
        return []

    return _deduplicate_findings(all_findings)


def _parse_consolidated_findings(text: str) -> list[Finding]:
    """Extract findings from '## Consolidated Findings' sections."""
    # Find the Consolidated Findings section
    match = re.search(r"^## Consolidated Findings\s*$", text, re.MULTILINE)
    if not match:
        return []

    section_text = text[match.end():]
    # Truncate at next H2
    next_h2 = re.search(r"^## ", section_text, re.MULTILINE)
    if next_h2:
        section_text = section_text[:next_h2.start()]

    return _extract_finding_blocks(section_text)


def _parse_flat_findings(text: str) -> list[Finding]:
    """Extract findings from individual report '## Findings' sections."""
    match = re.search(r"^## Findings\s*$", text, re.MULTILINE)
    if not match:
        return []

    section_text = text[match.end():]
    next_h2 = re.search(r"^## ", section_text, re.MULTILINE)
    if next_h2:
        section_text = section_text[:next_h2.start()]

    return _extract_finding_blocks(section_text)


def _extract_finding_blocks(section_text: str) -> list[Finding]:
    """Extract individual finding blocks from a findings section.

    Supports two patterns:
    1. Bold header: **[F-XX] [SEVERITY] Dimension: Description**
    2. Bold header: **[SEVERITY] Dimension**: Description
    """
    findings: list[Finding] = []

    # Pattern 1: **[F-XX] [SEVERITY] Dimension: Description**
    # Pattern 2: **F-XX [SEVERITY] Dimension: Description** (variant without brackets on ID)
    # Also matches: - **[SEVERITY] Dimension**: Description (individual reports)
    finding_pattern = re.compile(
        r"[-*]*\s*\*\*"
        r"(?:\[?(F-\d+)\]?\s+)?"          # Optional finding ID
        r"\[(BLOCKING|WARNING|INFO)\]\s+"   # Severity (required)
        r"([^:*]+)"                         # Dimension
        r"[:\s]*"                           # Separator
        r"([^*]+)?"                         # Description (optional inline)
        r"\*\*",
        re.IGNORECASE,
    )

    blocks = list(finding_pattern.finditer(section_text))

    for i, block_match in enumerate(blocks):
        block_start = block_match.end()
        block_end = blocks[i + 1].start() if i + 1 < len(blocks) else len(section_text)
        block_body = section_text[block_start:block_end]

        finding_id = block_match.group(1) or f"F-{len(findings) + 1:02d}"
        severity = block_match.group(2).upper()
        dimension = block_match.group(3).strip().rstrip(":")
        description = (block_match.group(4) or "").strip()

        # If description is empty, use the full matched text
        if not description:
            description = f"{dimension}"

        location = _extract_field(block_body, "Location")
        evidence = _extract_field(block_body, "Evidence")
        fix_guidance = _extract_field(block_body, "Fix guidance")
        agreement_raw = _extract_field(block_body, "Agreement")
        agreement = _extract_agreement_keyword(agreement_raw)

        # Validate required fields
        _validate_required_fields(finding_id, severity, description)

        files_affected = _extract_files_from_location(location)

        findings.append(Finding(
            id=finding_id,
            severity=severity,
            dimension=dimension,
            description=description,
            location=location,
            evidence=evidence,
            fix_guidance=fix_guidance,
            files_affected=files_affected,
            status="PENDING",
            agreement_category=agreement,
        ))

    return findings


def _extract_field(body: str, field_name: str) -> str:
    """Extract a field value from a finding block body.

    Handles multi-line values that continue with indentation.
    """
    pattern = re.compile(
        rf"^\s*-\s+{field_name}\s*:\s*(.+?)(?=\n\s*-\s+\w|\n\s*\n\*\*|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return ""
    # Clean up the extracted text
    raw = match.group(1).strip()
    # Collapse continuation lines
    lines = raw.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") and cleaned:
            # Sub-bullet -- keep as-is
            cleaned.append(stripped)
        elif stripped:
            cleaned.append(stripped)
    return " ".join(cleaned) if len(cleaned) <= 2 else "\n".join(cleaned)


def _extract_agreement_keyword(raw: str) -> str:
    """Extract agreement category keyword from raw agreement text.

    E.g. 'CONFLICT (Agent A: INFO, Agent B: BLOCKING).' -> 'CONFLICT'
    """
    if not raw:
        return ""
    match = re.match(r"(BOTH_AGREE|ONLY_A|ONLY_B|CONFLICT)", raw, re.IGNORECASE)
    return match.group(1).upper() if match else raw


def _extract_files_from_location(location: str) -> list[str]:
    """Extract file paths from a location string like 'roadmap.md:23, 359-363'."""
    if not location:
        return []
    # Match patterns like filename.ext, path/filename.ext
    file_pattern = re.compile(r"`?([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)(?::\d+[^`]*)?`?")
    matches = file_pattern.findall(location)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for f in matches:
        if f not in seen:
            seen.add(f)
            result.append(f)
    return result


def _validate_required_fields(
    finding_id: str, severity: str, description: str
) -> None:
    """Validate that required structured fields are present.

    Raises ValueError when required fields are absent.
    """
    missing = []
    if not finding_id:
        missing.append("id")
    if not severity:
        missing.append("severity")
    if not description:
        missing.append("description")
    if missing:
        raise ValueError(
            f"Required finding fields missing: {', '.join(missing)}. "
            "Cannot parse finding without id, severity, and description."
        )


def _overlay_agreement_categories(text: str, findings: list[Finding]) -> None:
    """Overlay agreement_category from Agreement Table onto findings."""
    # Match Agreement Table rows: | F-XX... | ... | ... | CATEGORY |
    table_pattern = re.compile(
        r"\|\s*(F-\d+)[^|]*\|"   # Finding ID column
        r"[^|]*\|"               # Agent A or Description column
        r"[^|]*\|"               # Agent B or another column
        r"[^|]*\|?"              # Possible extra column
        r"\s*(BOTH_AGREE|ONLY_A|ONLY_B|CONFLICT)\s*\|",
        re.IGNORECASE,
    )
    categories: dict[str, str] = {}
    for match in table_pattern.finditer(text):
        fid = match.group(1)
        cat = match.group(2).upper()
        categories[fid] = cat

    for finding in findings:
        if finding.id in categories:
            finding.agreement_category = categories[finding.id]


def _overlay_remediation_status(text: str, findings: list[Finding]) -> None:
    """Overlay remediation status from reflect-merged.md Agreement Table.

    In reflect-merged.md format, the table has a Remediation Status column
    with values like **FIXED**, **OUT_OF_SCOPE**, **NO_ACTION_REQUIRED**.
    """
    # Look for remediation status pattern in Agreement Table rows
    status_pattern = re.compile(
        r"\|\s*(F-\d+)[^|]*\|"       # Finding ID
        r"[^|]*\|[^|]*\|[^|]*\|"     # Middle columns
        r"\s*\*\*([A-Z_]+)\*\*",      # Bold status value
        re.IGNORECASE,
    )
    for match in status_pattern.finditer(text):
        fid = match.group(1)
        status_text = match.group(2).upper()
        for finding in findings:
            if finding.id == fid:
                if status_text == "FIXED":
                    finding.status = "FIXED"
                elif status_text in ("OUT_OF_SCOPE", "NO_ACTION_REQUIRED"):
                    finding.status = "SKIPPED"
                break


def _deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    """Deduplicate findings using two-step rule from spec §8/OQ-003.

    Step 1: Location match -- same file + within 5 lines = candidate duplicate
    Step 2: Severity resolution -- higher severity wins; fix_guidance merged
    """
    if not findings:
        return []

    result: list[Finding] = []
    merged_indices: set[int] = set()

    for i, f1 in enumerate(findings):
        if i in merged_indices:
            continue

        best = f1
        for j, f2 in enumerate(findings):
            if j <= i or j in merged_indices:
                continue

            if _is_location_match(f1, f2):
                merged_indices.add(j)
                best = _merge_findings(best, f2)

        result.append(best)

    return result


def _is_location_match(f1: Finding, f2: Finding) -> bool:
    """Check if two findings refer to the same file within 5 lines."""
    files1 = set(f1.files_affected)
    files2 = set(f2.files_affected)
    if not files1 or not files2:
        return False
    if not files1 & files2:
        return False

    # Extract line numbers from locations
    lines1 = _extract_line_numbers(f1.location)
    lines2 = _extract_line_numbers(f2.location)

    if not lines1 or not lines2:
        # Same file but can't compare lines -- treat as match
        return bool(files1 & files2)

    # Check if any line pair is within 5 lines
    for l1 in lines1:
        for l2 in lines2:
            if abs(l1 - l2) <= 5:
                return True
    return False


def _extract_line_numbers(location: str) -> list[int]:
    """Extract line numbers from a location string."""
    # Match patterns like :23, :359-363
    line_pattern = re.compile(r":(\d+)(?:-(\d+))?")
    numbers: list[int] = []
    for match in line_pattern.finditer(location):
        numbers.append(int(match.group(1)))
        if match.group(2):
            numbers.append(int(match.group(2)))
    return numbers


def _merge_findings(f1: Finding, f2: Finding) -> Finding:
    """Merge two duplicate findings. Higher severity wins; guidance merged."""
    rank1 = _SEVERITY_RANK.get(f1.severity, 0)
    rank2 = _SEVERITY_RANK.get(f2.severity, 0)

    winner = f1 if rank1 >= rank2 else f2
    loser = f2 if rank1 >= rank2 else f1

    # Merge fix guidance
    merged_guidance = winner.fix_guidance
    if loser.fix_guidance and loser.fix_guidance != winner.fix_guidance:
        merged_guidance = f"{winner.fix_guidance}\n[Additional]: {loser.fix_guidance}"

    # Merge files_affected
    all_files = list(dict.fromkeys(winner.files_affected + loser.files_affected))

    return Finding(
        id=winner.id,
        severity=winner.severity,
        dimension=winner.dimension,
        description=winner.description,
        location=winner.location,
        evidence=winner.evidence,
        fix_guidance=merged_guidance,
        files_affected=all_files,
        status="PENDING",
        agreement_category=winner.agreement_category,
    )
