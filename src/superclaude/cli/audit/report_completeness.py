"""Final report section completeness checks.

Implements T04.13 / D-0039 / AC1+AC16: validates the final report contains
all mandated sections and directory assessments for large directories.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Mandated sections per AC1
MANDATED_SECTIONS = [
    "executive_summary",
    "findings_by_tier",
    "action_items",
    "coverage_metrics",
    "validation_results",
    "dependency_graph_summary",
]


@dataclass
class CompletenessResult:
    """Result of completeness checking."""

    complete: bool
    present_sections: list[str]
    missing_sections: list[str]
    directory_assessment_check: bool
    missing_assessments: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "complete": self.complete,
            "present_sections": self.present_sections,
            "missing_sections": self.missing_sections,
            "directory_assessment_check": self.directory_assessment_check,
            "missing_assessments": self.missing_assessments,
        }


def check_section_completeness(
    report: dict[str, Any],
    mandated: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Check which mandated sections are present/missing.

    Args:
        report: Report dict to check.
        mandated: List of required section keys (default: MANDATED_SECTIONS).

    Returns:
        Tuple of (present, missing) section lists.
    """
    required = mandated or MANDATED_SECTIONS
    present = [s for s in required if s in report]
    missing = [s for s in required if s not in report]
    return present, missing


def check_directory_assessments(
    report: dict[str, Any],
    large_directories: list[str],
) -> tuple[bool, list[str]]:
    """Check that large directories have assessment blocks.

    Args:
        report: Report dict containing directory_assessments key.
        large_directories: List of directory paths that should have blocks.

    Returns:
        Tuple of (all_present, missing_directories).
    """
    assessments = report.get("directory_assessments", [])
    assessed_dirs = set()
    for a in assessments:
        if isinstance(a, dict):
            assessed_dirs.add(a.get("directory", ""))

    missing = [d for d in large_directories if d not in assessed_dirs]
    return len(missing) == 0, missing


def validate_report_completeness(
    report: dict[str, Any],
    large_directories: list[str] | None = None,
    mandated_sections: list[str] | None = None,
) -> CompletenessResult:
    """Validate that the final report has all mandated content.

    Args:
        report: The final report dict.
        large_directories: Directories that should have assessment blocks.
        mandated_sections: Required section keys (default: MANDATED_SECTIONS).

    Returns:
        CompletenessResult with pass/fail and details.
    """
    present, missing = check_section_completeness(report, mandated_sections)

    dir_ok = True
    missing_dirs: list[str] = []
    if large_directories:
        dir_ok, missing_dirs = check_directory_assessments(report, large_directories)

    complete = len(missing) == 0 and dir_ok

    return CompletenessResult(
        complete=complete,
        present_sections=present,
        missing_sections=missing,
        directory_assessment_check=dir_ok,
        missing_assessments=missing_dirs,
    )
