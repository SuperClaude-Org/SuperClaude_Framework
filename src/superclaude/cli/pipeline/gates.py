"""Pipeline gate validation -- pure Python, no subprocess, no LLM invocation.

Validates step outputs against GateCriteria with tier-proportional checks:
  EXEMPT  -> always passes
  LIGHT   -> file exists + non-empty
  STANDARD -> + min lines + YAML frontmatter fields
  STRICT  -> + semantic checks (if defined)

NFR-003: No subprocess import. NFR-007: No sprint/roadmap imports.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import GateCriteria, SemanticCheck


def gate_passed(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]:
    """Validate a step's output against its gate criteria.

    Returns (True, None) on pass.
    Returns (False, reason) on failure where reason is human-readable.
    """
    tier = criteria.enforcement_tier

    # EXEMPT: always passes
    if tier == "EXEMPT":
        return True, None

    # LIGHT, STANDARD, STRICT: file must exist
    if not output_file.exists():
        return False, f"File not found: {output_file}"

    # LIGHT, STANDARD, STRICT: file must be non-empty
    content = output_file.read_text(encoding="utf-8")
    if len(content.strip()) == 0:
        return False, f"File empty (0 bytes): {output_file}"

    # LIGHT stops here
    if tier == "LIGHT":
        return True, None

    # STANDARD, STRICT: minimum line count
    lines = content.splitlines()
    if len(lines) < criteria.min_lines:
        return False, (
            f"Below minimum line count: {len(lines)} < {criteria.min_lines} "
            f"in {output_file}"
        )

    # STANDARD, STRICT: YAML frontmatter fields
    if criteria.required_frontmatter_fields:
        ok, reason = _check_frontmatter(content, criteria.required_frontmatter_fields, output_file)
        if not ok:
            return False, reason

    # STANDARD stops here
    if tier == "STANDARD":
        return True, None

    # STRICT: semantic checks
    if criteria.semantic_checks:
        for check in criteria.semantic_checks:
            if not check.check_fn(content):
                return False, f"Semantic check '{check.name}' failed: {check.failure_message}"

    return True, None


_FRONTMATTER_RE = re.compile(
    r"^---[ \t]*\n((?:[ \t]*\w[\w\s]*:.*\n)+)---[ \t]*$",
    re.MULTILINE,
)


def _check_frontmatter(
    content: str, required_fields: list[str], output_file: Path
) -> tuple[bool, str | None]:
    """Extract and validate YAML frontmatter fields.

    Uses regex with re.MULTILINE to discover frontmatter anywhere in the
    document (not just byte 0), allowing conversational preamble before the
    ``---`` delimiters.  Horizontal rules (``---`` with no ``key: value``
    content) are rejected because the pattern requires at least one
    ``key: value`` line between delimiters.
    """
    match = _FRONTMATTER_RE.search(content)
    if match is None:
        return False, f"YAML frontmatter not found in {output_file}"

    frontmatter_text = match.group(1)

    # Extract keys from key: value lines
    found_keys: set[str] = set()
    for line in frontmatter_text.splitlines():
        line = line.strip()
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            if key:
                found_keys.add(key)

    for field in required_fields:
        if field not in found_keys:
            return False, f"Missing required frontmatter field '{field}' in {output_file}"

    return True, None
