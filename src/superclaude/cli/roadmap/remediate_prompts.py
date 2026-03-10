"""Remediation prompt builder -- produces agent prompts for file-level remediation.

All functions in this module are pure (no I/O, no subprocess calls, no side
effects) per NFR-004.

Provides:
- build_remediation_prompt(target_file, findings) -> str  (T04.01)
- group_findings_by_file(findings) -> dict  (T04.02)
- build_cross_file_fragment(finding, target_file) -> str  (T04.02)
"""

from __future__ import annotations

from .models import Finding


def build_remediation_prompt(
    target_file: str,
    findings: list[Finding],
) -> str:
    """Build a remediation agent prompt for a single target file.

    Produces the prompt template per spec section 2.3.4:
    - Header: "You are a remediation specialist..."
    - Target File section
    - Findings to Fix section (per-finding blocks with 6 detail fields)
    - Constraints section

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    lines: list[str] = []

    # Header
    lines.append(
        "You are a remediation specialist. Your task is to apply specific, "
        "targeted fixes to a single file based on validation findings."
    )
    lines.append("")

    # Target File section
    lines.append("## Target File")
    lines.append("")
    lines.append(f"`{target_file}`")
    lines.append("")

    # Findings to Fix section
    lines.append("## Findings to Fix")
    lines.append("")
    for f in findings:
        lines.append(f"### {f.id} [{f.severity}]")
        lines.append("")
        lines.append(f"- **ID**: {f.id}")
        lines.append(f"- **Severity**: {f.severity}")
        lines.append(f"- **Description**: {f.description}")
        lines.append(f"- **Location**: {f.location}")
        lines.append(f"- **Evidence**: {f.evidence}")
        lines.append(f"- **Fix Guidance**: {f.fix_guidance}")
        lines.append("")

    # Constraints section
    lines.append("## Constraints")
    lines.append("")
    lines.append(f"1. You may ONLY edit the target file: `{target_file}`")
    lines.append("2. Apply ONLY the fixes listed above -- do not make unrelated changes")
    lines.append("3. Preserve YAML frontmatter structure and values (unless a fix explicitly targets them)")
    lines.append("4. Preserve heading hierarchy -- do not add, remove, or reorder headings (unless a fix explicitly targets them)")
    lines.append("5. Preserve existing content that is not targeted by a fix")
    lines.append("")

    return "\n".join(lines)


def group_findings_by_file(
    findings: list[Finding],
) -> dict[str, list[Finding]]:
    """Group actionable findings by primary target file.

    Primary target is the first entry in files_affected for each finding.
    Cross-file findings (len(files_affected) > 1) appear in ALL relevant
    file groups with scoped guidance.

    Returns dict[str, list[Finding]] with no concurrent same-file groups.
    Every actionable finding appears in at least one group (no orphans).

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    groups: dict[str, list[Finding]] = {}

    for finding in findings:
        if not finding.files_affected:
            # Findings with no files_affected go to an "unknown" group
            groups.setdefault("unknown", []).append(finding)
            continue

        # Add to all affected file groups
        for file_path in finding.files_affected:
            groups.setdefault(file_path, []).append(finding)

    return groups


def build_cross_file_fragment(
    finding: Finding,
    target_file: str,
) -> str:
    """Build scoped prompt fragment for a cross-file finding.

    For findings that span multiple files, produces guidance scoped to
    the target file with a note about the other file being handled
    by a separate agent.

    Pure function: no I/O, no subprocess, no side effects (NFR-004).
    """
    other_files = [f for f in finding.files_affected if f != target_file]

    lines: list[str] = []
    lines.append(f"- **Fix Guidance (YOUR FILE)**: {finding.fix_guidance}")
    if other_files:
        other_list = ", ".join(f"`{f}`" for f in other_files)
        lines.append(
            f"- **Note**: The {other_list} side is handled by a separate agent."
        )
    return "\n".join(lines)
