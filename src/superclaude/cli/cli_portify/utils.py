"""Shared utilities for cli-portify pipeline.

Contains: frontmatter parsing helpers, file existence/writability checks,
section hashing utilities for additive-only verification (NFR-008),
line counting and artifact rendering helpers, signal vocabulary
constants from D-0004.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


# --- Signal Vocabulary Constants (D-0004) ---

STEP_START = "step_start"
STEP_COMPLETE = "step_complete"
STEP_ERROR = "step_error"
STEP_TIMEOUT = "step_timeout"
GATE_PASS = "gate_pass"
GATE_FAIL = "gate_fail"

SIGNAL_VOCABULARY = (
    STEP_START,
    STEP_COMPLETE,
    STEP_ERROR,
    STEP_TIMEOUT,
    GATE_PASS,
    GATE_FAIL,
)


# --- Frontmatter Parsing ---

_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from a Markdown document.

    Frontmatter is delimited by ``---`` on its own line at the start
    and end of the frontmatter block (per D-0003 Frontmatter Rules).

    Args:
        content: Full file content.

    Returns:
        Tuple of (frontmatter_dict, body_text). If no frontmatter
        is found, returns ({}, full content).
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}, content

    fm_text = match.group(1)
    body = content[match.end():]

    try:
        parsed = _parse_simple_yaml(fm_text)
    except Exception:
        return {}, content

    if not isinstance(parsed, dict):
        return {}, content

    return parsed, body


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse simple YAML key-value pairs without external dependencies.

    Handles: strings, integers, floats, booleans, and quoted strings.
    Does not handle nested structures, lists, or multi-line values.
    """
    result: dict[str, Any] = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, raw_val = line.partition(":")
        key = key.strip()
        val = raw_val.strip()
        # Unquote
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            result[key] = val[1:-1]
        elif val.lower() in ("true", "yes"):
            result[key] = True
        elif val.lower() in ("false", "no"):
            result[key] = False
        elif val.lower() in ("null", "~", ""):
            result[key] = None
        else:
            # Try int, then float, then string
            try:
                result[key] = int(val)
            except ValueError:
                try:
                    result[key] = float(val)
                except ValueError:
                    result[key] = val
    return result


def validate_frontmatter_fields(
    frontmatter: dict[str, Any],
    required_fields: list[str],
) -> list[str]:
    """Validate that required frontmatter fields are present.

    Args:
        frontmatter: Parsed frontmatter dictionary.
        required_fields: List of required field names.

    Returns:
        List of missing field names (empty if all present).
    """
    return [f for f in required_fields if f not in frontmatter]


# --- File Checks ---


def file_exists(path: Path | str) -> bool:
    """Check if a file exists."""
    return Path(path).exists()


def is_writable_dir(path: Path | str) -> bool:
    """Check if a directory exists and is writable.

    Creates the directory if it doesn't exist.
    """
    p = Path(path)
    try:
        p.mkdir(parents=True, exist_ok=True)
        return p.is_dir()
    except OSError:
        return False


# --- Section Hashing (NFR-008: Additive-Only Verification) ---


def hash_section(content: str) -> str:
    """Compute a deterministic SHA-256 hash for a content section.

    Used to verify additive-only changes: sections can be added but
    existing sections must not be modified or removed.

    Args:
        content: Section text content.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    normalized = content.strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_sections(content: str) -> dict[str, str]:
    """Extract Markdown sections by heading.

    Splits content by top-level (##) headings and returns a mapping
    of heading text to section body.

    Args:
        content: Markdown content (body, not frontmatter).

    Returns:
        Dict mapping heading text to section content.
    """
    sections: dict[str, str] = {}
    current_heading = ""
    current_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("## "):
            # Save previous section
            if current_heading:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save last section
    if current_heading:
        sections[current_heading] = "\n".join(current_lines)

    return sections


def verify_additive_only(
    old_hashes: dict[str, str],
    new_content: str,
) -> list[str]:
    """Verify that changes to a document are additive-only.

    Checks that no existing section was modified or removed.
    New sections may be added freely.

    Args:
        old_hashes: Mapping of section heading to previous hash.
        new_content: New document body content.

    Returns:
        List of violation messages (empty if additive-only).
    """
    new_sections = extract_sections(new_content)
    violations: list[str] = []

    for heading, old_hash in old_hashes.items():
        if heading not in new_sections:
            violations.append(f"Section removed: '{heading}'")
        elif hash_section(new_sections[heading]) != old_hash:
            violations.append(f"Section modified: '{heading}'")

    return violations


# --- Line Counting ---


def count_lines(path: Path | str) -> int:
    """Count lines in a file.

    Args:
        path: Path to the file.

    Returns:
        Number of lines, or 0 if file doesn't exist.
    """
    p = Path(path)
    if not p.exists():
        return 0
    try:
        return len(p.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0


def count_lines_content(content: str) -> int:
    """Count lines in a string."""
    return len(content.splitlines())
