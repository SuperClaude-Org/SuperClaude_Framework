"""ALREADY_TRACKED report section for suppressed findings.

Implements T05.04 / D-0043 / AC1 (supporting):
  Renders a table of findings suppressed by the known-issues registry,
  showing file path, registry entry ID, and matched pattern.

  Section is present only when registry matches exist (not an empty section).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .known_issues import MatchResult


@dataclass
class AlreadyTrackedSection:
    """Report section listing suppressed findings."""

    suppressed: list[MatchResult] = field(default_factory=list)

    @property
    def is_present(self) -> bool:
        return len(self.suppressed) > 0

    def to_dict(self) -> dict[str, Any]:
        if not self.is_present:
            return {}
        return {
            "already_tracked": [s.to_dict() for s in self.suppressed],
            "already_tracked_count": len(self.suppressed),
        }

    def render_markdown(self) -> str:
        """Render the section as markdown table."""
        if not self.is_present:
            return ""
        lines = [
            "## Already Tracked",
            "",
            "| Finding Path | Registry Entry ID | Matched Pattern | Classification |",
            "|---|---|---|---|",
        ]
        for s in self.suppressed:
            lines.append(
                f"| {s.file_path} | {s.registry_entry_id} | "
                f"{s.matched_pattern} | {s.classification} |"
            )
        lines.append("")
        return "\n".join(lines)


def build_already_tracked_section(
    suppressed: list[MatchResult],
) -> AlreadyTrackedSection:
    """Build the ALREADY_TRACKED section from match results.

    Returns a section that is only present (non-empty) when matches exist.
    """
    return AlreadyTrackedSection(suppressed=suppressed)
