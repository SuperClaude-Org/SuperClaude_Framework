"""3-tier dependency graph with confidence labels from static and grep evidence.

Implements T03.06 / D-0022: builds a dependency graph with confidence-tiered edges.

Tiers:
  - Tier-A: AST-resolved imports (high confidence)
  - Tier-B: Grep string references (medium confidence)
  - Tier-C: Co-occurrence/naming inference (low confidence)

Policy: Tier-C edges never promote to DELETE classification.

Graph output: adjacency list with edge attributes
(source, target, tier, confidence, evidence_type).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .tool_orchestrator import FileAnalysis


class EdgeTier(Enum):
    """Dependency edge confidence tier."""

    TIER_A = "A"  # AST import, high confidence
    TIER_B = "B"  # Grep reference, medium confidence
    TIER_C = "C"  # Inferred, low confidence


TIER_CONFIDENCE: dict[EdgeTier, float] = {
    EdgeTier.TIER_A: 0.90,
    EdgeTier.TIER_B: 0.65,
    EdgeTier.TIER_C: 0.35,
}


@dataclass
class DependencyEdge:
    """A directed edge in the dependency graph."""

    source: str
    target: str
    tier: EdgeTier
    confidence: float
    evidence_type: str
    evidence_detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "tier": self.tier.value,
            "confidence": self.confidence,
            "evidence_type": self.evidence_type,
            "evidence_detail": self.evidence_detail,
        }


@dataclass
class DependencyGraph:
    """3-tier dependency graph with nodes and labeled edges."""

    nodes: set[str] = field(default_factory=set)
    edges: list[DependencyEdge] = field(default_factory=list)

    def add_edge(self, edge: DependencyEdge) -> None:
        """Add an edge, preventing self-loops."""
        if edge.source == edge.target:
            return  # skip self-loops
        self.nodes.add(edge.source)
        self.nodes.add(edge.target)
        self.edges.append(edge)

    def edges_by_tier(self) -> dict[str, list[DependencyEdge]]:
        result: dict[str, list[DependencyEdge]] = {"A": [], "B": [], "C": []}
        for e in self.edges:
            result[e.tier.value].append(e)
        return result

    def importers_of(self, target: str) -> list[DependencyEdge]:
        """Get all edges targeting a specific file."""
        return [e for e in self.edges if e.target == target]

    def tier_a_importers_of(self, target: str) -> list[DependencyEdge]:
        return [
            e for e in self.edges
            if e.target == target and e.tier == EdgeTier.TIER_A
        ]

    def tier_b_importers_of(self, target: str) -> list[DependencyEdge]:
        return [
            e for e in self.edges
            if e.target == target and e.tier == EdgeTier.TIER_B
        ]

    @property
    def stats(self) -> dict[str, int]:
        by_tier = self.edges_by_tier()
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "tier_a_count": len(by_tier["A"]),
            "tier_b_count": len(by_tier["B"]),
            "tier_c_count": len(by_tier["C"]),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": sorted(self.nodes),
            "edges": [e.to_dict() for e in self.edges],
            "stats": self.stats,
        }


import os
import re


def _resolve_import_target(
    import_stmt: str,
    source_path: str,
    known_files: set[str],
) -> str | None:
    """Try to resolve an import statement to a known file path.

    Returns file path if resolved, None otherwise.
    """
    # Python: "from foo.bar import baz" or "import foo.bar"
    py_match = re.match(r"(?:from\s+(\S+)\s+import|import\s+(\S+))", import_stmt)
    if py_match:
        module = (py_match.group(1) or py_match.group(2)).replace(".", "/")
        candidates = [
            f"{module}.py",
            f"{module}/__init__.py",
            f"src/{module}.py",
            f"src/{module}/__init__.py",
        ]
        for c in candidates:
            if c in known_files:
                return c

    # JS/TS: "import X from './foo'" or "import { X } from '../bar'"
    js_match = re.search(r"""from\s+['"]([^'"]+)['"]""", import_stmt)
    if js_match:
        raw = js_match.group(1)
        # Skip node_modules
        if not raw.startswith("."):
            return None
        # Resolve relative path
        source_dir = os.path.dirname(source_path)
        resolved = os.path.normpath(os.path.join(source_dir, raw))
        # Try extensions
        for ext in ["", ".js", ".ts", ".jsx", ".tsx", "/index.js", "/index.ts"]:
            candidate = resolved + ext
            if candidate in known_files:
                return candidate

    return None


def _find_grep_references(
    target_stem: str,
    source_path: str,
    source_content: str,
) -> bool:
    """Check if source content contains string references to target."""
    return target_stem in source_content


def _infer_cooccurrence(
    source_path: str,
    target_path: str,
) -> bool:
    """Infer relationship from naming conventions and directory co-location."""
    source_stem = os.path.splitext(os.path.basename(source_path))[0]
    target_stem = os.path.splitext(os.path.basename(target_path))[0]

    # Naming convention: test_X <-> X, X.test <-> X
    stripped_source = source_stem.replace("test_", "").replace("_test", "").replace(".test", "")
    stripped_target = target_stem.replace("test_", "").replace("_test", "").replace(".test", "")

    if stripped_source == stripped_target and source_stem != target_stem:
        return True

    # Same directory co-location
    if os.path.dirname(source_path) == os.path.dirname(target_path):
        # Only infer if stems share a common prefix (>3 chars)
        common = os.path.commonprefix([source_stem, target_stem])
        if len(common) > 3:
            return True

    return False


def build_dependency_graph(
    analyses: dict[str, FileAnalysis],
    file_contents: dict[str, str] | None = None,
) -> DependencyGraph:
    """Build a 3-tier dependency graph from file analyses.

    Args:
        analyses: Mapping of file_path -> FileAnalysis (from ToolOrchestrator).
        file_contents: Optional mapping of file_path -> content for grep matching.

    Returns:
        DependencyGraph with Tier-A, Tier-B, and Tier-C edges.
    """
    graph = DependencyGraph()
    known_files = set(analyses.keys())
    contents = file_contents or {}

    # Add all files as nodes
    for path in known_files:
        graph.nodes.add(path)

    for source_path, analysis in analyses.items():
        source_stem = os.path.splitext(os.path.basename(source_path))[0]

        # Tier-A: AST-resolved imports
        for imp in analysis.imports:
            target = _resolve_import_target(imp, source_path, known_files)
            if target and target != source_path:
                graph.add_edge(DependencyEdge(
                    source=source_path,
                    target=target,
                    tier=EdgeTier.TIER_A,
                    confidence=TIER_CONFIDENCE[EdgeTier.TIER_A],
                    evidence_type="ast_import",
                    evidence_detail=imp,
                ))

        # Tier-B: Grep string references
        if source_path in contents:
            for target_path in known_files:
                if target_path == source_path:
                    continue
                target_stem = os.path.splitext(os.path.basename(target_path))[0]
                if _find_grep_references(target_stem, source_path, contents[source_path]):
                    # Avoid duplicating Tier-A edges
                    already_tier_a = any(
                        e.source == source_path and e.target == target_path
                        and e.tier == EdgeTier.TIER_A
                        for e in graph.edges
                    )
                    if not already_tier_a:
                        graph.add_edge(DependencyEdge(
                            source=source_path,
                            target=target_path,
                            tier=EdgeTier.TIER_B,
                            confidence=TIER_CONFIDENCE[EdgeTier.TIER_B],
                            evidence_type="grep_reference",
                            evidence_detail=f"'{target_stem}' found in {source_path}",
                        ))

        # Tier-C: Co-occurrence inference
        for target_path in known_files:
            if target_path == source_path:
                continue
            if _infer_cooccurrence(source_path, target_path):
                # Avoid duplicating higher-tier edges
                already_higher = any(
                    e.source == source_path and e.target == target_path
                    and e.tier in (EdgeTier.TIER_A, EdgeTier.TIER_B)
                    for e in graph.edges
                )
                if not already_higher:
                    graph.add_edge(DependencyEdge(
                        source=source_path,
                        target=target_path,
                        tier=EdgeTier.TIER_C,
                        confidence=TIER_CONFIDENCE[EdgeTier.TIER_C],
                        evidence_type="inferred_cooccurrence",
                        evidence_detail=f"naming/co-location: {source_path} <-> {target_path}",
                    ))

    return graph
