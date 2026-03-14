"""Deterministic gate checks for Steps 1-2 (validate-config, discover-components).

EXEMPT tier gates that provide advisory timing checks and structural
validation for deterministic steps. These run without Claude subprocesses.

Per NFR-004: all gate functions return tuple[bool, str].
Per tasklist T03.03: integrate with pipeline.gates.gate_passed().
"""

from __future__ import annotations

from pathlib import Path

from superclaude.cli.cli_portify.models import PortifyConfig
from superclaude.cli.cli_portify.steps.validate_config import ValidateConfigResult
from superclaude.cli.cli_portify.utils import parse_frontmatter, validate_frontmatter_fields
from superclaude.cli.pipeline.models import GateCriteria


# --- Gate Criteria Definitions ---

VALIDATE_CONFIG_GATE = GateCriteria(
    required_frontmatter_fields=[],
    min_lines=0,
    enforcement_tier="EXEMPT",
)

DISCOVER_COMPONENTS_GATE = GateCriteria(
    required_frontmatter_fields=["source_skill", "component_count"],
    min_lines=5,
    enforcement_tier="STANDARD",
)


# --- Gate Functions ---


def gate_validate_config(
    result: ValidateConfigResult,
    timing_limit: float = 1.0,
) -> tuple[bool, str]:
    """EXEMPT gate for validate-config (Step 1).

    Checks:
    - Timing advisory: duration should be <1s
    - Validation result consistency (errors present iff not valid)

    Args:
        result: The ValidateConfigResult from Step 1.
        timing_limit: Advisory timing limit in seconds.

    Returns:
        Tuple of (passed: bool, message: str).
    """
    issues: list[str] = []

    # Timing advisory
    if result.duration_seconds > timing_limit:
        issues.append(
            f"Timing advisory: validate-config took {result.duration_seconds:.3f}s "
            f"(limit: {timing_limit}s)"
        )

    # Consistency: errors iff not valid
    if result.valid and result.errors:
        issues.append(
            "Inconsistency: result marked valid but errors present"
        )
    if not result.valid and not result.errors:
        issues.append(
            "Inconsistency: result marked invalid but no errors listed"
        )

    if issues:
        return False, "; ".join(issues)
    return True, "validate-config gate passed"


def gate_discover_components(
    artifact_path: Path,
    timing_limit: float = 5.0,
    actual_duration: float | None = None,
) -> tuple[bool, str]:
    """STANDARD gate for discover-components (Step 2).

    Checks:
    - Timing advisory: duration should be <5s
    - YAML frontmatter presence with source_skill and component_count
    - Line count format validation (component_count is integer >= 0)

    Args:
        artifact_path: Path to component-inventory.md.
        timing_limit: Advisory timing limit in seconds.
        actual_duration: Actual step duration for timing check.
            If None, reads from frontmatter.

    Returns:
        Tuple of (passed: bool, message: str).
    """
    issues: list[str] = []

    # File existence
    if not artifact_path.exists():
        return False, f"Artifact not found: {artifact_path}"

    content = artifact_path.read_text(encoding="utf-8")

    # Frontmatter validation
    fm, body = parse_frontmatter(content)
    if not fm:
        return False, f"No YAML frontmatter found in {artifact_path}"

    missing = validate_frontmatter_fields(fm, ["source_skill", "component_count"])
    if missing:
        return False, f"Missing frontmatter fields: {', '.join(missing)}"

    # component_count must be non-negative integer
    count = fm.get("component_count")
    if not isinstance(count, int) or count < 0:
        issues.append(
            f"Invalid component_count: {count!r} (expected non-negative integer)"
        )

    # total_lines should be present and non-negative
    total_lines = fm.get("total_lines")
    if total_lines is not None:
        if not isinstance(total_lines, int) or total_lines < 0:
            issues.append(
                f"Invalid total_lines: {total_lines!r} (expected non-negative integer)"
            )

    # Timing advisory
    duration = actual_duration
    if duration is None:
        duration = fm.get("duration_seconds")
    if duration is not None and duration > timing_limit:
        issues.append(
            f"Timing advisory: discover-components took {duration:.3f}s "
            f"(limit: {timing_limit}s)"
        )

    if issues:
        return False, "; ".join(issues)
    return True, "discover-components gate passed"
