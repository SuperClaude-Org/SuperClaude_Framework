"""Duplication matrix with consolidation threshold recommendations.

Implements T03.08 / D-0024: detects code duplication using structural
similarity based on shared import sets and export overlap.

Thresholds:
  >80% similarity = consolidate recommended
  >60% similarity = investigate
  <60% = ignore
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .tool_orchestrator import FileAnalysis


@dataclass
class DuplicatePair:
    """A pair of files with similarity score."""

    file_a: str
    file_b: str
    similarity: float
    shared_imports: list[str]
    shared_exports: list[str]
    recommendation: str  # "consolidate", "investigate", "ignore"

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_a": self.file_a,
            "file_b": self.file_b,
            "similarity": round(self.similarity, 4),
            "shared_imports": self.shared_imports,
            "shared_exports": self.shared_exports,
            "recommendation": self.recommendation,
        }


@dataclass
class DuplicationMatrix:
    """Matrix of file pairs above similarity threshold."""

    pairs: list[DuplicatePair] = field(default_factory=list)
    threshold: float = 0.60

    def to_dict(self) -> dict[str, Any]:
        return {
            "threshold": self.threshold,
            "pairs": [p.to_dict() for p in self.pairs],
            "consolidate_count": sum(
                1 for p in self.pairs if p.recommendation == "consolidate"
            ),
            "investigate_count": sum(
                1 for p in self.pairs if p.recommendation == "investigate"
            ),
            "total_pairs": len(self.pairs),
        }


def _normalize_import(imp: str) -> str:
    """Normalize an import statement for comparison."""
    return imp.strip().lower()


def compute_similarity(
    analysis_a: FileAnalysis,
    analysis_b: FileAnalysis,
) -> tuple[float, list[str], list[str]]:
    """Compute structural similarity between two files.

    Based on Jaccard similarity of import sets and export overlap.

    Returns (similarity, shared_imports, shared_exports).
    """
    imports_a = {_normalize_import(i) for i in analysis_a.imports}
    imports_b = {_normalize_import(i) for i in analysis_b.imports}
    exports_a = {_normalize_import(e) for e in analysis_a.exports}
    exports_b = {_normalize_import(e) for e in analysis_b.exports}

    # Jaccard similarity for imports
    import_union = imports_a | imports_b
    import_inter = imports_a & imports_b

    # Jaccard similarity for exports
    export_union = exports_a | exports_b
    export_inter = exports_a & exports_b

    total_union = len(import_union) + len(export_union)
    total_inter = len(import_inter) + len(export_inter)

    if total_union == 0:
        return 0.0, [], []

    similarity = total_inter / total_union

    return (
        similarity,
        sorted(import_inter),
        sorted(export_inter),
    )


def _recommendation(similarity: float) -> str:
    if similarity > 0.80:
        return "consolidate"
    elif similarity > 0.60:
        return "investigate"
    return "ignore"


def build_duplication_matrix(
    analyses: dict[str, FileAnalysis],
    threshold: float = 0.60,
) -> DuplicationMatrix:
    """Build duplication matrix for all file pairs above threshold.

    Args:
        analyses: Mapping of file_path -> FileAnalysis.
        threshold: Minimum similarity to include (default 0.60).

    Returns:
        DuplicationMatrix with file pairs and recommendations.
    """
    matrix = DuplicationMatrix(threshold=threshold)
    paths = sorted(analyses.keys())

    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            path_a = paths[i]
            path_b = paths[j]
            sim, shared_imp, shared_exp = compute_similarity(
                analyses[path_a], analyses[path_b],
            )
            if sim >= threshold:
                matrix.pairs.append(DuplicatePair(
                    file_a=path_a,
                    file_b=path_b,
                    similarity=sim,
                    shared_imports=shared_imp,
                    shared_exports=shared_exp,
                    recommendation=_recommendation(sim),
                ))

    return matrix
