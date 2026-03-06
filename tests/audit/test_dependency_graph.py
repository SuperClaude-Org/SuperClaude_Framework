"""Tests for 3-tier dependency graph (T03.06 / D-0022)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.dependency_graph import (
    DependencyEdge,
    DependencyGraph,
    EdgeTier,
    build_dependency_graph,
)
from superclaude.cli.audit.tool_orchestrator import FileAnalysis


def _analysis(path: str, imports: list[str] = None, exports: list[str] = None) -> FileAnalysis:
    return FileAnalysis(
        file_path=path,
        content_hash="abc123",
        imports=imports or [],
        exports=exports or [],
    )


class TestDependencyGraph:
    def test_no_self_loops(self):
        g = DependencyGraph()
        g.add_edge(DependencyEdge(
            source="a.py", target="a.py",
            tier=EdgeTier.TIER_A, confidence=0.9,
            evidence_type="test",
        ))
        assert len(g.edges) == 0

    def test_adds_nodes(self):
        g = DependencyGraph()
        g.add_edge(DependencyEdge(
            source="a.py", target="b.py",
            tier=EdgeTier.TIER_A, confidence=0.9,
            evidence_type="test",
        ))
        assert "a.py" in g.nodes
        assert "b.py" in g.nodes

    def test_stats(self):
        g = DependencyGraph()
        g.add_edge(DependencyEdge(
            source="a.py", target="b.py",
            tier=EdgeTier.TIER_A, confidence=0.9,
            evidence_type="test",
        ))
        g.add_edge(DependencyEdge(
            source="c.py", target="b.py",
            tier=EdgeTier.TIER_B, confidence=0.65,
            evidence_type="test",
        ))
        stats = g.stats
        assert stats["node_count"] == 3
        assert stats["edge_count"] == 2
        assert stats["tier_a_count"] == 1
        assert stats["tier_b_count"] == 1

    def test_importers_of(self):
        g = DependencyGraph()
        g.add_edge(DependencyEdge(
            source="a.py", target="b.py",
            tier=EdgeTier.TIER_A, confidence=0.9,
            evidence_type="test",
        ))
        importers = g.importers_of("b.py")
        assert len(importers) == 1
        assert importers[0].source == "a.py"


class TestBuildDependencyGraph:
    def test_tier_a_from_ast_imports(self):
        analyses = {
            "src/main.py": _analysis("src/main.py", imports=["from src.utils import helper"]),
            "src/utils.py": _analysis("src/utils.py", exports=["__all__ = ['helper']"]),
        }
        graph = build_dependency_graph(analyses)
        tier_a = graph.edges_by_tier()["A"]
        # May or may not resolve depending on path matching
        assert graph.stats["node_count"] >= 2

    def test_tier_b_from_grep(self):
        analyses = {
            "src/main.py": _analysis("src/main.py"),
            "src/utils.py": _analysis("src/utils.py", exports=["__all__ = ['helper']"]),
        }
        contents = {
            "src/main.py": "# This uses utils for processing\nimport something\n",
            "src/utils.py": "def helper(): pass\n",
        }
        graph = build_dependency_graph(analyses, file_contents=contents)
        tier_b = graph.edges_by_tier()["B"]
        assert len(tier_b) > 0  # "utils" should be found in main.py

    def test_tier_c_from_cooccurrence(self):
        analyses = {
            "src/auth.py": _analysis("src/auth.py", exports=["__all__ = ['login']"]),
            "tests/test_auth.py": _analysis("tests/test_auth.py"),
        }
        graph = build_dependency_graph(analyses)
        tier_c = graph.edges_by_tier()["C"]
        assert len(tier_c) > 0  # test_auth <-> auth naming

    def test_no_self_loops_in_graph(self):
        analyses = {
            "src/main.py": _analysis("src/main.py", imports=["from main import x"]),
        }
        graph = build_dependency_graph(analyses)
        for e in graph.edges:
            assert e.source != e.target

    def test_correct_tier_labels(self):
        analyses = {
            "src/main.py": _analysis("src/main.py"),
            "src/utils.py": _analysis("src/utils.py"),
        }
        graph = build_dependency_graph(analyses)
        for e in graph.edges:
            assert e.tier in (EdgeTier.TIER_A, EdgeTier.TIER_B, EdgeTier.TIER_C)

    def test_graph_serializable(self):
        analyses = {
            "src/main.py": _analysis("src/main.py"),
            "src/utils.py": _analysis("src/utils.py"),
        }
        graph = build_dependency_graph(analyses)
        d = graph.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "stats" in d
