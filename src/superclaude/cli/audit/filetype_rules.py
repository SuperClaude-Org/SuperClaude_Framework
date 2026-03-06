"""File-type specific verification rules for classification decisions.

Implements T03.02 / D-0018: verification rules adapt to file type.
Configuration files need different evidence than source code files.

File type categories:
  - source: .py, .ts, .js, .jsx, .tsx, .go, .rs, .java
  - config: .json, .yaml, .yml, .toml, .ini, .cfg, .env
  - docs:   .md, .rst, .txt
  - test:   test_*.py, *.test.ts, *.spec.js, etc.
  - binary: images, compiled, archives

Each category has specific evidence requirements for classification.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .classification import ClassificationResult, V2Action


class FileType(Enum):
    """File type categories."""

    SOURCE = "source"
    CONFIG = "config"
    DOCS = "docs"
    TEST = "test"
    BINARY = "binary"


# Extension-based classification
_SOURCE_EXTS = frozenset({
    ".py", ".ts", ".js", ".jsx", ".tsx", ".vue", ".svelte",
    ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".h",
})

_CONFIG_EXTS = frozenset({
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".env", ".properties", ".xml",
})

_DOCS_EXTS = frozenset({
    ".md", ".rst", ".txt", ".adoc",
})

_BINARY_EXTS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot",
    ".pyc", ".pyo", ".class", ".o", ".so", ".dll",
    ".zip", ".tar", ".gz", ".bz2",
})

# Test file name patterns
_TEST_PREFIXES = ("test_", "spec_")
_TEST_INFIXES = (".test.", ".spec.", "_test.", "_spec.")


def classify_file_type(file_path: str) -> FileType:
    """Classify a file into a type category based on extension and name.

    Test detection takes priority over extension-based classification.
    """
    base = os.path.basename(file_path).lower()
    stem = os.path.splitext(base)[0]
    ext = os.path.splitext(base)[1].lower()

    # Test detection first (highest priority)
    if any(stem.startswith(p) for p in _TEST_PREFIXES):
        return FileType.TEST
    if any(infix in base for infix in _TEST_INFIXES):
        return FileType.TEST
    lower_path = file_path.lower().replace("\\", "/")
    if (
        "/tests/" in lower_path or "/test/" in lower_path
        or lower_path.startswith("tests/") or lower_path.startswith("test/")
    ):
        return FileType.TEST

    # Extension-based
    if ext in _BINARY_EXTS:
        return FileType.BINARY
    if ext in _CONFIG_EXTS:
        return FileType.CONFIG
    if ext in _DOCS_EXTS:
        return FileType.DOCS
    if ext in _SOURCE_EXTS:
        return FileType.SOURCE

    # Default to source for unknown
    return FileType.SOURCE


@dataclass
class VerificationRule:
    """A single verification rule with evidence requirement."""

    name: str
    description: str
    required_evidence_types: list[str]
    min_evidence_count: int = 1


# Per-type verification rule sets
_SOURCE_RULES = [
    VerificationRule(
        name="import_export_evidence",
        description="Source files require import/export analysis evidence",
        required_evidence_types=["import", "export", "reference"],
        min_evidence_count=1,
    ),
    VerificationRule(
        name="usage_evidence",
        description="Source files should have usage/reference evidence for KEEP",
        required_evidence_types=["reference", "import", "usage"],
        min_evidence_count=1,
    ),
]

_CONFIG_RULES = [
    VerificationRule(
        name="reference_evidence",
        description="Config files require reference evidence (something reads them)",
        required_evidence_types=["reference", "config_ref", "env_ref"],
        min_evidence_count=1,
    ),
]

_DOCS_RULES = [
    VerificationRule(
        name="link_validation",
        description="Docs require link validity check",
        required_evidence_types=["link", "reference", "doc_ref"],
        min_evidence_count=0,  # docs can exist without references
    ),
]

_TEST_RULES = [
    VerificationRule(
        name="test_target_evidence",
        description="Test files should reference a test target",
        required_evidence_types=["import", "reference", "test_target"],
        min_evidence_count=1,
    ),
]

_BINARY_RULES = [
    VerificationRule(
        name="binary_reference",
        description="Binary files need at least one reference to justify keeping",
        required_evidence_types=["reference", "usage"],
        min_evidence_count=1,
    ),
]

_RULES_BY_TYPE: dict[FileType, list[VerificationRule]] = {
    FileType.SOURCE: _SOURCE_RULES,
    FileType.CONFIG: _CONFIG_RULES,
    FileType.DOCS: _DOCS_RULES,
    FileType.TEST: _TEST_RULES,
    FileType.BINARY: _BINARY_RULES,
}


@dataclass
class RuleCheckResult:
    """Result of checking a single verification rule."""

    rule_name: str
    passed: bool
    reason: str | None = None
    matched_evidence: list[str] = field(default_factory=list)


@dataclass
class FileTypeVerificationResult:
    """Result of running file-type-specific verification."""

    file_path: str
    file_type: FileType
    rules_applied: list[str]
    checks: list[RuleCheckResult]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_type": self.file_type.value,
            "passed": self.passed,
            "rules_applied": self.rules_applied,
            "checks": [
                {
                    "rule": c.rule_name,
                    "passed": c.passed,
                    "reason": c.reason,
                    "matched_evidence": c.matched_evidence,
                }
                for c in self.checks
            ],
        }


def _check_rule(
    rule: VerificationRule,
    evidence: list[str],
) -> RuleCheckResult:
    """Check if evidence satisfies a verification rule."""
    matched = []
    for ev in evidence:
        ev_lower = ev.lower()
        for req_type in rule.required_evidence_types:
            if req_type.lower() in ev_lower:
                matched.append(ev)
                break

    if len(matched) >= rule.min_evidence_count:
        return RuleCheckResult(
            rule_name=rule.name,
            passed=True,
            matched_evidence=matched,
        )

    return RuleCheckResult(
        rule_name=rule.name,
        passed=False,
        reason=f"Insufficient evidence: need {rule.min_evidence_count} of types "
               f"{rule.required_evidence_types}, found {len(matched)}",
        matched_evidence=matched,
    )


def verify_classification(
    result: ClassificationResult,
) -> FileTypeVerificationResult:
    """Run file-type-specific verification on a classification result.

    Dispatches to the correct rule set based on file type.
    Only applies verification for KEEP and DELETE actions (others pass through).
    """
    file_type = classify_file_type(result.file_path)
    rules = _RULES_BY_TYPE.get(file_type, [])

    # Only enforce rules for actionable classifications
    if result.action not in (V2Action.KEEP, V2Action.DELETE):
        return FileTypeVerificationResult(
            file_path=result.file_path,
            file_type=file_type,
            rules_applied=[],
            checks=[],
        )

    checks = []
    for rule in rules:
        check = _check_rule(rule, result.evidence)
        checks.append(check)

    return FileTypeVerificationResult(
        file_path=result.file_path,
        file_type=file_type,
        rules_applied=[r.name for r in rules],
        checks=checks,
    )
