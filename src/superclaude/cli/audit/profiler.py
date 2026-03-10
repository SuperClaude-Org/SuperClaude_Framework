"""Domain and risk-tier profiling for repository file sets.

Implements AC13: automated domain/risk-tier profiling to drive batch planning
and analysis depth decisions.

Domains: frontend, backend, infra, docs, test
Risk tiers: high, medium, low

Profiling is deterministic: same file set produces identical output.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any


# --- Domain classification rules (path-pattern matching) ---

_DOMAIN_RULES: list[tuple[str, list[str]]] = [
    ("test", [
        "tests/", "test/", "__tests__/", "spec/",
        "test_", "_test.", ".test.", ".spec.",
        "conftest.py", "pytest.ini",
    ]),
    ("docs", [
        "docs/", "doc/", "documentation/",
        "README", "CHANGELOG", "LICENSE", "CONTRIBUTING",
        "PLANNING.md", "TASK.md", "KNOWLEDGE.md",
        ".md",
    ]),
    ("infra", [
        "infra/", "infrastructure/", "deploy/", "deployment/",
        ".github/", ".gitlab/", ".circleci/",
        "Dockerfile", "docker-compose", ".dockerignore",
        "terraform/", "ansible/", "k8s/", "kubernetes/",
        "Makefile", "Justfile", "Vagrantfile",
        ".yml", ".yaml",
        "scripts/",
    ]),
    ("frontend", [
        "src/components/", "src/ui/", "src/views/", "src/pages/",
        "components/", "ui/", "views/", "pages/",
        ".jsx", ".tsx", ".vue", ".svelte",
        ".css", ".scss", ".sass", ".less",
        "tailwind", "postcss",
    ]),
    ("backend", [
        "src/api/", "src/server/", "src/services/", "src/models/",
        "api/", "server/", "services/", "models/",
        "controllers/", "routes/", "middleware/",
        "src/superclaude/",
    ]),
]

# --- Risk-tier rules ---

_HIGH_RISK_PATTERNS: list[str] = [
    "auth", "security", "crypto", "secret", "credential",
    "password", "token", "session", "oauth", "jwt",
    "migration", "schema", "database", "models/",
    ".env", ".pem", ".key",
]

_MEDIUM_RISK_PATTERNS: list[str] = [
    "config", "settings", "pyproject.toml", "package.json",
    "Cargo.toml", "go.mod", "requirements.txt",
    "Makefile", "Dockerfile", "docker-compose",
    ".yml", ".yaml", ".toml", ".ini", ".cfg",
    "setup.py", "setup.cfg",
]

# Files matching neither high nor medium patterns default to low risk.


@dataclass
class FileProfile:
    """Profile for a single file: domain, risk tier, confidence."""

    file_path: str
    domain: str
    risk_tier: str  # "high", "medium", "low"
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "domain": self.domain,
            "risk_tier": self.risk_tier,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FileProfile:
        return cls(
            file_path=data["file_path"],
            domain=data["domain"],
            risk_tier=data["risk_tier"],
            confidence=data["confidence"],
        )


@dataclass
class ProfileReport:
    """Complete profiling output for a repository."""

    files: list[FileProfile] = field(default_factory=list)

    @property
    def domain_distribution(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for fp in self.files:
            counts[fp.domain] = counts.get(fp.domain, 0) + 1
        return counts

    @property
    def risk_distribution(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for fp in self.files:
            counts[fp.risk_tier] = counts.get(fp.risk_tier, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_count": len(self.files),
            "domain_distribution": self.domain_distribution,
            "risk_distribution": self.risk_distribution,
            "files": [f.to_dict() for f in self.files],
        }


def classify_domain(file_path: str) -> tuple[str, float]:
    """Classify a file into a domain based on path patterns.

    Returns (domain, confidence). Deterministic: same path always
    produces same result.

    Rules are checked in priority order: test > docs > infra > frontend > backend.
    Files not matching any pattern default to 'backend' with lower confidence.
    """
    normalized = file_path.replace("\\", "/")
    lower = normalized.lower()

    for domain, patterns in _DOMAIN_RULES:
        for pattern in patterns:
            pat_lower = pattern.lower()
            if pat_lower in lower:
                return domain, 0.85
            # Check filename suffix for extension patterns
            if pat_lower.startswith(".") and lower.endswith(pat_lower):
                return domain, 0.80

    # Default: backend with lower confidence
    return "backend", 0.60


def classify_risk_tier(
    file_path: str,
    *,
    file_size: int | None = None,
) -> tuple[str, float]:
    """Assign a risk tier based on path patterns and optional file characteristics.

    Returns (risk_tier, confidence). Deterministic for same inputs.

    Args:
        file_path: Path to the file.
        file_size: Optional file size in bytes (large files get risk bump).
    """
    normalized = file_path.replace("\\", "/")
    lower = normalized.lower()

    # High risk check
    for pattern in _HIGH_RISK_PATTERNS:
        if pattern.lower() in lower:
            return "high", 0.90

    # Medium risk check
    for pattern in _MEDIUM_RISK_PATTERNS:
        if pattern.lower() in lower:
            return "medium", 0.85

    # Size-based risk bump: files over 500 lines (≈15KB) get medium
    if file_size is not None and file_size > 15_000:
        return "medium", 0.70

    return "low", 0.80


def profile_file(
    file_path: str,
    *,
    file_size: int | None = None,
) -> FileProfile:
    """Profile a single file: domain + risk tier.

    Deterministic: same inputs always produce same profile.
    """
    domain, domain_conf = classify_domain(file_path)
    risk, risk_conf = classify_risk_tier(file_path, file_size=file_size)

    # Combined confidence is the minimum of domain and risk confidence
    confidence = min(domain_conf, risk_conf)

    return FileProfile(
        file_path=file_path,
        domain=domain,
        risk_tier=risk,
        confidence=confidence,
    )


def profile_repository(
    file_paths: list[str],
    *,
    file_sizes: dict[str, int] | None = None,
) -> ProfileReport:
    """Profile all files in a repository.

    Args:
        file_paths: List of relative file paths.
        file_sizes: Optional mapping of file_path -> size in bytes.

    Returns:
        ProfileReport with domain, risk_tier, and confidence per file.
        Every file receives exactly one domain and one risk tier.
    """
    sizes = file_sizes or {}
    report = ProfileReport()

    for fp in file_paths:
        size = sizes.get(fp)
        report.files.append(profile_file(fp, file_size=size))

    return report
