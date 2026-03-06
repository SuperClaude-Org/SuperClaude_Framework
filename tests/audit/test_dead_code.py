"""Tests for dead code detection (T03.07 / D-0023)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.dead_code import detect_dead_code
from superclaude.cli.audit.dependency_graph import (
    DependencyEdge,
    DependencyGraph,
    EdgeTier,
)
from superclaude.cli.audit.tool_orchestrator import FileAnalysis


def _analysis(path, exports=None, imports=None):
    return FileAnalysis(
        file_path=path, content_hash="h",
        imports=imports or [], exports=exports or [],
    )


def _graph_with_edges(edges):
    g = DependencyGraph()
    for src, tgt, tier in edges:
        g.add_edge(DependencyEdge(
            source=src, target=tgt, tier=tier,
            confidence=0.9, evidence_type="test",
        ))
    return g


class TestDetectDeadCode:
    def test_unused_export_detected(self):
        analyses = {
            "src/orphan.py": _analysis("src/orphan.py", exports=["__all__ = ['foo']"]),
            "src/main.py": _analysis("src/main.py"),
        }
        graph = _graph_with_edges([])
        graph.nodes = set(analyses.keys())
        report = detect_dead_code(graph, analyses)
        paths = [c.file_path for c in report.candidates]
        assert "src/orphan.py" in paths

    def test_used_export_not_detected(self):
        analyses = {
            "src/utils.py": _analysis("src/utils.py", exports=["__all__ = ['x']"]),
            "src/main.py": _analysis("src/main.py"),
        }
        graph = _graph_with_edges([
            ("src/main.py", "src/utils.py", EdgeTier.TIER_A),
        ])
        report = detect_dead_code(graph, analyses)
        paths = [c.file_path for c in report.candidates]
        assert "src/utils.py" not in paths

    def test_entry_point_excluded(self):
        analyses = {
            "src/main.py": _analysis("src/main.py", exports=["__all__ = ['run']"]),
        }
        graph = _graph_with_edges([])
        graph.nodes = set(analyses.keys())
        report = detect_dead_code(graph, analyses)
        excluded = [e.file_path for e in report.excluded]
        assert "src/main.py" in excluded

    def test_framework_hook_excluded(self):
        analyses = {
            "conftest.py": _analysis("conftest.py", exports=["__all__ = ['fixture']"]),
        }
        graph = _graph_with_edges([])
        graph.nodes = set(analyses.keys())
        report = detect_dead_code(graph, analyses)
        excluded = [e.file_path for e in report.excluded]
        assert "conftest.py" in excluded

    def test_custom_entry_point(self):
        analyses = {
            "src/startup.py": _analysis("src/startup.py", exports=["__all__ = ['boot']"]),
        }
        graph = _graph_with_edges([])
        graph.nodes = set(analyses.keys())
        report = detect_dead_code(
            graph, analyses, entry_points=["src/startup.py"],
        )
        excluded = [e.file_path for e in report.excluded]
        assert "src/startup.py" in excluded

    def test_candidate_has_evidence(self):
        analyses = {
            "src/orphan.py": _analysis("src/orphan.py", exports=["__all__ = ['foo']"]),
            "src/main.py": _analysis("src/main.py"),
        }
        graph = _graph_with_edges([])
        graph.nodes = set(analyses.keys())
        report = detect_dead_code(graph, analyses)
        for c in report.candidates:
            assert c.export_location
            assert c.boundary_search_scope
            assert c.tier_a_importers == 0
            assert c.tier_b_importers == 0

    def test_file_without_exports_skipped(self):
        analyses = {
            "src/helper.py": _analysis("src/helper.py", exports=[]),
        }
        graph = _graph_with_edges([])
        graph.nodes = set(analyses.keys())
        report = detect_dead_code(graph, analyses)
        assert len(report.candidates) == 0

    def test_report_serializable(self):
        analyses = {
            "src/orphan.py": _analysis("src/orphan.py", exports=["__all__ = ['x']"]),
        }
        graph = _graph_with_edges([])
        graph.nodes = set(analyses.keys())
        report = detect_dead_code(graph, analyses)
        d = report.to_dict()
        assert "candidates" in d
        assert "excluded" in d
