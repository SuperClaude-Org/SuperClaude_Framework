"""Environment variable key-presence matrix for configuration drift detection.

Implements T03.05 / D-0021: cross-references keys across .env, .env.example,
.env.production, and code references (process.env, os.environ) to identify drift.

CRITICAL: outputs key names only, never secret values.
Non-disclosure policy: never output secret values.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any


# Code reference patterns for env key extraction
_CODE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("process_env", re.compile(r"process\.env\.([A-Z_][A-Z0-9_]*)")),
    ("os_environ_bracket", re.compile(r"""os\.environ\[["']([A-Z_][A-Z0-9_]*)["']\]""")),
    ("os_getenv", re.compile(r"""os\.getenv\(["']([A-Z_][A-Z0-9_]*)["']""")),
    ("os_environ_get", re.compile(r"""os\.environ\.get\(["']([A-Z_][A-Z0-9_]*)["']""")),
    ("dotenv_key", re.compile(r"""(?:ENV|config)\[["']([A-Z_][A-Z0-9_]*)["']\]""", re.IGNORECASE)),
]


@dataclass
class EnvKeyEntry:
    """Presence information for a single env key across sources."""

    key: str
    present_in: dict[str, bool] = field(default_factory=dict)
    # source -> True/False

    @property
    def drift_categories(self) -> list[str]:
        """Identify drift categories for this key."""
        drifts = []
        in_code = self.present_in.get("code", False)
        in_env = self.present_in.get(".env", False)
        in_example = self.present_in.get(".env.example", False)

        if in_code and not in_example:
            drifts.append("missing_from_example")
        if in_env and not in_code:
            drifts.append("unused_in_code")
        if in_code and not in_env:
            drifts.append("missing_from_env")
        if in_example and not in_code:
            drifts.append("example_unused")
        return drifts


@dataclass
class EnvKeyMatrix:
    """Presence matrix: key x source with drift detection."""

    entries: dict[str, EnvKeyEntry] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)

    def add_key(self, key: str, source: str) -> None:
        """Register a key as present in a source."""
        if key not in self.entries:
            self.entries[key] = EnvKeyEntry(key=key)
        self.entries[key].present_in[source] = True
        if source not in self.sources:
            self.sources.append(source)

    @property
    def all_drifts(self) -> list[dict[str, Any]]:
        """Get all drift findings across all keys."""
        drifts = []
        for key, entry in sorted(self.entries.items()):
            categories = entry.drift_categories
            if categories:
                drifts.append({
                    "key": key,
                    "categories": categories,
                    "present_in": {
                        s: entry.present_in.get(s, False)
                        for s in self.sources
                    },
                })
        return drifts

    def to_dict(self) -> dict[str, Any]:
        """Serialize matrix (keys only, never values)."""
        rows = []
        for key in sorted(self.entries):
            entry = self.entries[key]
            row: dict[str, Any] = {"key": key}
            for source in self.sources:
                row[source] = entry.present_in.get(source, False)
            row["drift_categories"] = entry.drift_categories
            rows.append(row)
        return {
            "sources": self.sources,
            "keys": rows,
            "drift_count": len(self.all_drifts),
            "total_keys": len(self.entries),
        }


def parse_env_file(content: str) -> list[str]:
    """Extract key names (NOT values) from .env file content.

    Returns list of key names only. Never returns values.
    """
    keys = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # KEY=value or KEY="value" or export KEY=value
        if stripped.startswith("export "):
            stripped = stripped[7:].strip()
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                keys.append(key)
    return keys


def scan_code_references(content: str) -> list[str]:
    """Extract env key references from source code.

    Returns list of key names found in process.env, os.environ, etc.
    """
    keys: set[str] = set()
    for _pattern_name, pattern in _CODE_PATTERNS:
        for match in pattern.finditer(content):
            keys.add(match.group(1))
    return sorted(keys)


def build_matrix(
    env_files: dict[str, str],
    code_files: dict[str, str],
) -> EnvKeyMatrix:
    """Build env key-presence matrix from env files and code files.

    Args:
        env_files: Mapping of env filename -> content (e.g., ".env" -> "KEY=val")
        code_files: Mapping of source filename -> content

    Returns:
        EnvKeyMatrix with all keys and their presence across sources.
        Contains only key names, never secret values.
    """
    matrix = EnvKeyMatrix()

    # Parse env files
    for filename, content in env_files.items():
        keys = parse_env_file(content)
        for key in keys:
            matrix.add_key(key, filename)

    # Scan code files
    for filename, content in code_files.items():
        keys = scan_code_references(content)
        for key in keys:
            matrix.add_key(key, "code")

    return matrix
