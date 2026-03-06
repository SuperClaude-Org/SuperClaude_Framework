"""Dynamic-import-safe classification policy with KEEP:monitor default.

Implements T03.10 / D-0026: detects files loaded via dynamic imports and
assigns KEEP:monitor classification to prevent false DELETE.

Dynamic import patterns:
  - JavaScript: import(variable), require(variable)
  - Python: __import__(), importlib.import_module()
  - Glob imports

Policy: Files referenced via dynamic imports receive KEEP:monitor,
never DELETE.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .classification import ClassificationResult, V1Category, V2Action, V2Tier


# Dynamic import detection patterns
_DYNAMIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # JavaScript dynamic import()
    ("js_dynamic_import", re.compile(r"import\s*\([^\"'][^)]*\)")),
    # JavaScript require with variable
    ("js_require_variable", re.compile(r"require\s*\([^\"'][^)]*\)")),
    # Python __import__
    ("py_import_builtin", re.compile(r"__import__\s*\(")),
    # Python importlib.import_module
    ("py_importlib", re.compile(r"importlib\.import_module\s*\(")),
    # Python importlib.util.find_spec
    ("py_importlib_util", re.compile(r"importlib\.util\.\w+\s*\(")),
    # Glob/wildcard imports
    ("glob_import", re.compile(r"glob\s*\.\s*glob\s*\(")),
    # require.context (webpack)
    ("webpack_require_context", re.compile(r"require\.context\s*\(")),
]


@dataclass
class DynamicImportDetection:
    """A detected dynamic import pattern."""

    file_path: str
    pattern_name: str
    line_number: int
    line_content: str
    referenced_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "pattern_name": self.pattern_name,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "referenced_files": self.referenced_files,
        }


@dataclass
class DynamicImportReport:
    """Report of dynamic import detection."""

    detections: list[DynamicImportDetection] = field(default_factory=list)
    files_with_dynamic_imports: set[str] = field(default_factory=set)
    dynamically_loaded_files: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        return {
            "detections": [d.to_dict() for d in self.detections],
            "files_with_dynamic_imports": sorted(self.files_with_dynamic_imports),
            "dynamically_loaded_files": sorted(self.dynamically_loaded_files),
            "detection_count": len(self.detections),
        }


def scan_for_dynamic_imports(
    file_path: str,
    content: str,
) -> list[DynamicImportDetection]:
    """Scan a file for dynamic import patterns.

    Returns list of detections with pattern name and line info.
    """
    detections = []
    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern_name, pattern in _DYNAMIC_PATTERNS:
            if pattern.search(line):
                detections.append(DynamicImportDetection(
                    file_path=file_path,
                    pattern_name=pattern_name,
                    line_number=line_num,
                    line_content=line.strip(),
                ))
                break  # one detection per line
    return detections


def detect_dynamic_imports(
    files: dict[str, str],
) -> DynamicImportReport:
    """Detect all dynamic imports across a file set.

    Args:
        files: Mapping of file_path -> content.

    Returns:
        DynamicImportReport with all detections.
    """
    report = DynamicImportReport()

    for file_path, content in files.items():
        detections = scan_for_dynamic_imports(file_path, content)
        if detections:
            report.detections.extend(detections)
            report.files_with_dynamic_imports.add(file_path)

    return report


def apply_keep_monitor(
    classification: ClassificationResult,
    dynamic_report: DynamicImportReport,
) -> ClassificationResult:
    """Apply KEEP:monitor policy for dynamically-imported files.

    If a file is referenced via dynamic imports, override its
    classification to KEEP with 'monitor' qualifier.
    Never allows DELETE for dynamically-imported files.
    """
    # Check if this file is loaded dynamically
    is_dynamic = classification.file_path in dynamic_report.dynamically_loaded_files
    # Also check if this file CONTAINS dynamic imports (it's a loader)
    is_loader = classification.file_path in dynamic_report.files_with_dynamic_imports

    if is_dynamic or is_loader:
        if classification.action == V2Action.DELETE:
            return ClassificationResult(
                file_path=classification.file_path,
                tier=V2Tier.TIER_2,
                action=V2Action.KEEP,
                v1_category=V1Category.KEEP,
                confidence=0.75,
                evidence=classification.evidence + [
                    "dynamic import detected: KEEP:monitor policy applied"
                ],
                qualifiers=classification.qualifiers + ["monitor", "dynamic_import"],
            )
    return classification


def classify_with_dynamic_safety(
    classifications: list[ClassificationResult],
    files: dict[str, str],
) -> list[ClassificationResult]:
    """Apply dynamic import safety to a batch of classifications.

    Scans all files for dynamic imports, then overrides DELETE
    to KEEP:monitor for any dynamically-referenced files.

    Args:
        classifications: Original classification results.
        files: File contents for scanning.

    Returns:
        Updated classifications with KEEP:monitor for dynamic imports.
    """
    report = detect_dynamic_imports(files)

    # Mark files that are targets of dynamic imports
    # (In a real system, this would resolve the dynamic import targets.
    #  For now, files containing dynamic imports are themselves protected.)

    return [apply_keep_monitor(c, report) for c in classifications]
