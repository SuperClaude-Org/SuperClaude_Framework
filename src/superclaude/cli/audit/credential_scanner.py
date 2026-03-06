"""Real credential scanning with safe redaction in output.

Implements AC7: credential scanning that distinguishes real secrets from
template placeholders, with safe redaction to prevent secret leakage.

Detection patterns: API keys, tokens, passwords, env var values.
Exclusion patterns: ${VAR}, <YOUR_KEY>, xxx, placeholder templates.
Redaction: replaces detected secret values with [REDACTED] in all output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# Real secret patterns (compiled for performance)
_SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("aws_secret_key", re.compile(r"(?:aws_secret_access_key|AWS_SECRET)\s*[=:]\s*[A-Za-z0-9/+=]{40}")),
    ("github_token", re.compile(r"gh[ps]_[A-Za-z0-9_]{36,}")),
    ("github_classic_token", re.compile(r"ghp_[A-Za-z0-9_]{36}")),
    ("generic_api_key", re.compile(r"""(?:api[_-]?key|apikey|api[_-]?secret)\s*[=:"']\s*[A-Za-z0-9_\-]{20,}""", re.IGNORECASE)),
    ("generic_token", re.compile(r"""(?:token|bearer|auth[_-]?token)\s*[=:"']\s*[A-Za-z0-9_\-\.]{20,}""", re.IGNORECASE)),
    ("generic_password", re.compile(r"""(?:password|passwd|pwd)\s*[=:]\s*["']?([^\s"']{8,})""", re.IGNORECASE)),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----")),
    ("slack_token", re.compile(r"xox[baprs]-[0-9a-zA-Z\-]{10,}")),
    ("stripe_key", re.compile(r"sk_(?:live|test)_[0-9a-zA-Z]{24,}")),
]

# Template/placeholder patterns to exclude
_PLACEHOLDER_PATTERNS: list[re.Pattern] = [
    re.compile(r"\$\{[A-Z_]+\}"),                   # ${VAR_NAME}
    re.compile(r"<YOUR[_\-]?[A-Z_]*>", re.IGNORECASE),  # <YOUR_API_KEY>
    re.compile(r"(?:xxx+|XXX+|placeholder|PLACEHOLDER|changeme|CHANGEME|your[_-]?(?:key|token|password|secret))", re.IGNORECASE),
    re.compile(r"process\.env\.[A-Z_]+"),            # process.env.VAR
    re.compile(r"os\.environ\.get\("),               # os.environ.get(
    re.compile(r"os\.getenv\("),                     # os.getenv(
]

REDACTION_MARKER = "[REDACTED]"


@dataclass
class SecretDetection:
    """A single detected secret."""

    pattern_name: str
    line_number: int
    line_content: str
    match_text: str
    is_placeholder: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_name": self.pattern_name,
            "line_number": self.line_number,
            "is_placeholder": self.is_placeholder,
            "redacted_line": self.line_content.replace(self.match_text, REDACTION_MARKER) if not self.is_placeholder else self.line_content,
        }


@dataclass
class ScanResult:
    """Result of scanning a file for credentials."""

    file_path: str
    secrets_found: list[SecretDetection] = field(default_factory=list)
    placeholders_excluded: list[SecretDetection] = field(default_factory=list)

    @property
    def real_secret_count(self) -> int:
        return len(self.secrets_found)

    @property
    def placeholder_count(self) -> int:
        return len(self.placeholders_excluded)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "real_secrets": [s.to_dict() for s in self.secrets_found],
            "placeholders_excluded": [s.to_dict() for s in self.placeholders_excluded],
            "real_secret_count": self.real_secret_count,
            "placeholder_count": self.placeholder_count,
        }


def _is_placeholder(line: str, match_text: str) -> bool:
    """Check if a detected match is actually a template placeholder."""
    for pat in _PLACEHOLDER_PATTERNS:
        if pat.search(line):
            return True
    return False


def scan_content(file_path: str, content: str) -> ScanResult:
    """Scan file content for real secrets, excluding template placeholders.

    Args:
        file_path: Path to the file being scanned.
        content: File content to scan.

    Returns:
        ScanResult with real secrets and excluded placeholders.
    """
    result = ScanResult(file_path=file_path)

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern_name, pattern in _SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                match_text = match.group(0)
                detection = SecretDetection(
                    pattern_name=pattern_name,
                    line_number=line_num,
                    line_content=line,
                    match_text=match_text,
                )

                if _is_placeholder(line, match_text):
                    detection.is_placeholder = True
                    result.placeholders_excluded.append(detection)
                else:
                    result.secrets_found.append(detection)

    return result


def redact_output(text: str, detections: list[SecretDetection]) -> str:
    """Replace all detected secret values with [REDACTED] in output text."""
    redacted = text
    for det in detections:
        if not det.is_placeholder:
            redacted = redacted.replace(det.match_text, REDACTION_MARKER)
    return redacted
