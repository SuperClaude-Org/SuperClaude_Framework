"""Remediation functions -- pure functions for Phase 3 remediation pipeline.

All functions in this module are pure (no I/O, no subprocess calls, no side
effects) per NFR-004, except where explicitly noted.

Provides:
- format_validation_summary(findings) -> str  (T03.01)
- RemediationScope enum  (T03.01/T03.02)
- filter_findings(findings, scope) -> tuple  (T03.02)
- generate_remediation_tasklist(findings, source_report_path, source_report_content) -> str  (T03.04)
"""

from __future__ import annotations

import enum
import hashlib
from datetime import datetime, timezone

from .models import Finding


class RemediationScope(enum.Enum):
    """User-selected scope for remediation filtering.

    Maps to prompt options:
    [1] BLOCKING_ONLY  -- only BLOCKING findings
    [2] BLOCKING_WARNING -- BLOCKING + WARNING
    [3] ALL -- all findings with fix_guidance
    """

    BLOCKING_ONLY = "blocking_only"
    BLOCKING_WARNING = "blocking_warning"
    ALL = "all"


# Agreement categories that trigger auto-SKIP regardless of scope selection
_AUTO_SKIP_CATEGORIES = frozenset({"NO_ACTION_REQUIRED", "OUT_OF_SCOPE"})


def format_validation_summary(findings: list[Finding]) -> str:
    """Format findings into a severity-grouped terminal summary.

    Groups findings by severity (BLOCKING, WARNING, INFO) with counts
    and lists each finding's ID and description. Returns a formatted
    string suitable for terminal output per spec section 2.2 box layout.

    Pure function: no I/O or side effects.
    """
    blocking = [f for f in findings if f.severity == "BLOCKING"]
    warning = [f for f in findings if f.severity == "WARNING"]
    info = [f for f in findings if f.severity == "INFO"]

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("  VALIDATION SUMMARY")
    lines.append("=" * 60)
    lines.append("")

    total = len(findings)
    lines.append(f"  Total findings: {total}")
    lines.append(f"  BLOCKING: {len(blocking)}  |  WARNING: {len(warning)}  |  INFO: {len(info)}")
    lines.append("")

    if blocking:
        lines.append("  --- BLOCKING ---")
        for f in blocking:
            lines.append(f"  {f.id} | {f.description}")
        lines.append("")

    if warning:
        lines.append("  --- WARNING ---")
        for f in warning:
            lines.append(f"  {f.id} | {f.description}")
        lines.append("")

    if info:
        lines.append("  --- INFO ---")
        for f in info:
            lines.append(f"  {f.id} | {f.description}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def should_skip_prompt(findings: list[Finding]) -> bool:
    """Return True when prompt should be skipped (zero BLOCKING + zero WARNING).

    Per spec section 2.2: when there are no BLOCKING and no WARNING findings,
    the prompt is auto-skipped.

    Pure function: no I/O or side effects.
    """
    blocking = sum(1 for f in findings if f.severity == "BLOCKING")
    warning = sum(1 for f in findings if f.severity == "WARNING")
    return blocking == 0 and warning == 0


def filter_findings(
    findings: list[Finding],
    scope: RemediationScope,
) -> tuple[list[Finding], list[Finding]]:
    """Filter findings by user-selected scope with auto-SKIP logic.

    Auto-SKIP is applied first: findings with agreement_category of
    NO_ACTION_REQUIRED or OUT_OF_SCOPE are always moved to skipped,
    regardless of scope selection.

    Then scope filtering is applied:
    - BLOCKING_ONLY: keeps only BLOCKING severity
    - BLOCKING_WARNING: keeps BLOCKING + WARNING
    - ALL: keeps all findings that have fix_guidance

    Returns (actionable, skipped) tuple.

    Pure function: no I/O or side effects.
    """
    actionable: list[Finding] = []
    skipped: list[Finding] = []

    for f in findings:
        # Auto-SKIP: NO_ACTION_REQUIRED and OUT_OF_SCOPE always skipped
        if f.agreement_category in _AUTO_SKIP_CATEGORIES:
            skipped.append(f)
            continue

        # Already terminal status (FIXED, SKIPPED) -> skip
        if f.status in ("FIXED", "SKIPPED"):
            skipped.append(f)
            continue

        # Scope filtering
        if scope == RemediationScope.BLOCKING_ONLY:
            if f.severity == "BLOCKING":
                actionable.append(f)
            else:
                skipped.append(f)
        elif scope == RemediationScope.BLOCKING_WARNING:
            if f.severity in ("BLOCKING", "WARNING"):
                actionable.append(f)
            else:
                skipped.append(f)
        else:  # ALL
            if f.fix_guidance:
                actionable.append(f)
            else:
                skipped.append(f)

    return actionable, skipped


def generate_remediation_tasklist(
    findings: list[Finding],
    source_report_path: str,
    source_report_content: str,
) -> str:
    """Generate remediation-tasklist.md with YAML frontmatter.

    Produces markdown with:
    - YAML frontmatter: type, source_report, source_report_hash, generated,
      total_findings, actionable, skipped
    - Severity-grouped entries: - [ ] F-XX | file | STATUS -- description

    The source_report_hash is SHA-256 of the source report content.

    Pure function: no I/O or side effects (datetime injected via UTC now).
    """
    source_hash = hashlib.sha256(source_report_content.encode("utf-8")).hexdigest()
    generated = datetime.now(timezone.utc).isoformat()

    actionable_findings = [f for f in findings if f.status == "PENDING"]
    skipped_findings = [f for f in findings if f.status != "PENDING"]
    total = len(findings)

    # YAML frontmatter
    lines: list[str] = [
        "---",
        "type: remediation-tasklist",
        f"source_report: {source_report_path}",
        f"source_report_hash: {source_hash}",
        f"generated: {generated}",
        f"total_findings: {total}",
        f"actionable: {len(actionable_findings)}",
        f"skipped: {len(skipped_findings)}",
        "---",
        "",
        "# Remediation Tasklist",
        "",
    ]

    # Group by severity
    blocking = [f for f in findings if f.severity == "BLOCKING"]
    warning = [f for f in findings if f.severity == "WARNING"]
    info = [f for f in findings if f.severity == "INFO"]
    skipped_sev = [f for f in findings if f.status == "SKIPPED"]

    if blocking:
        lines.append("## BLOCKING")
        lines.append("")
        for f in blocking:
            status = f.status
            files = ", ".join(f.files_affected) if f.files_affected else "unknown"
            lines.append(f"- [ ] {f.id} | {files} | {status} -- {f.description}")
        lines.append("")

    if warning:
        lines.append("## WARNING")
        lines.append("")
        for f in warning:
            status = f.status
            files = ", ".join(f.files_affected) if f.files_affected else "unknown"
            lines.append(f"- [ ] {f.id} | {files} | {status} -- {f.description}")
        lines.append("")

    if info:
        lines.append("## INFO")
        lines.append("")
        for f in info:
            status = f.status
            files = ", ".join(f.files_affected) if f.files_affected else "unknown"
            lines.append(f"- [ ] {f.id} | {files} | {status} -- {f.description}")
        lines.append("")

    # Skipped section (findings that were already SKIPPED before tasklist generation)
    if skipped_sev:
        lines.append("## SKIPPED")
        lines.append("")
        for f in skipped_sev:
            files = ", ".join(f.files_affected) if f.files_affected else "unknown"
            lines.append(f"- [x] {f.id} | {files} | SKIPPED -- {f.description}")
        lines.append("")

    return "\n".join(lines)


def generate_stub_tasklist(
    source_report_path: str,
    source_report_content: str,
) -> str:
    """Generate a stub remediation-tasklist.md when no actionable findings exist.

    Produces minimal tasklist with actionable: 0 in frontmatter.

    Pure function: no I/O or side effects.
    """
    source_hash = hashlib.sha256(source_report_content.encode("utf-8")).hexdigest()
    generated = datetime.now(timezone.utc).isoformat()

    return "\n".join([
        "---",
        "type: remediation-tasklist",
        f"source_report: {source_report_path}",
        f"source_report_hash: {source_hash}",
        f"generated: {generated}",
        "total_findings: 0",
        "actionable: 0",
        "skipped: 0",
        "---",
        "",
        "# Remediation Tasklist",
        "",
        "No actionable findings. All entries SKIPPED or no findings detected.",
        "",
    ])
