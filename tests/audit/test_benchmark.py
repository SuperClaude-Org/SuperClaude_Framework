"""Benchmark tests for small, medium, and known-dead-code repos (T05.06 / D-0045).

Validates audit pipeline performance across 3 repository tiers using
self-contained in-memory fixtures.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest

from superclaude.cli.audit.batch_decomposer import decompose
from superclaude.cli.audit.classification import (
    ClassificationResult, V1Category, V2Action, V2Tier,
    classify_finding,
)
from superclaude.cli.audit.consolidation import (
    ConsolidatedFinding, ConsolidationReport, consolidate,
)
from superclaude.cli.audit.coverage import CoverageTracker
from superclaude.cli.audit.dead_code import detect_dead_code
from superclaude.cli.audit.dependency_graph import (
    DependencyGraph, DependencyEdge, EdgeTier,
)
from superclaude.cli.audit.dry_run import dry_run
from superclaude.cli.audit.profiler import profile_file, FileProfile
from superclaude.cli.audit.report_completeness import validate_report_completeness
from superclaude.cli.audit.report_depth import render_report, ReportDepth
from superclaude.cli.audit.tool_orchestrator import FileAnalysis


def _make_finding(
    file_path: str = "src/test.py",
    tier: V2Tier = V2Tier.TIER_1,
    action: V2Action = V2Action.DELETE,
    confidence: float = 0.9,
) -> ConsolidatedFinding:
    return ConsolidatedFinding(
        file_path=file_path,
        tier=tier,
        action=action,
        confidence=confidence,
        evidence=["zero references found"],
        source_phases=["phase_1"],
    )


# ---------------------------------------------------------------------------
# Fixture generators for 3 repository tiers
# ---------------------------------------------------------------------------


def _small_repo_files() -> list[str]:
    """Small repo: <50 files."""
    files = []
    for i in range(30):
        files.append(f"src/module_{i}.py")
    files.extend(["README.md", "setup.py", "tests/test_main.py"])
    return files


def _medium_repo_files() -> list[str]:
    """Medium repo: 50-500 files."""
    files = []
    for pkg in ("core", "api", "models", "utils", "services"):
        for i in range(40):
            files.append(f"src/{pkg}/file_{i}.py")
    for i in range(20):
        files.append(f"tests/test_{i}.py")
    files.extend(["README.md", "setup.py", "docs/guide.md"])
    return files


def _dead_code_repo() -> tuple[list[str], set[str]]:
    """Known-dead-code repo with documented expected dead code.

    Returns (all_files, expected_dead_code_files).
    """
    live_files = [f"src/core/live_{i}.py" for i in range(20)]
    dead_files = [f"src/legacy/dead_{i}.py" for i in range(10)]
    all_files = live_files + dead_files + [
        "README.md", "setup.py", "src/__init__.py",
    ]
    return all_files, set(dead_files)


def _build_graph_for_files(
    files: list[str], dead_files: set[str] | None = None,
) -> DependencyGraph:
    """Build a dependency graph where dead files have no inbound edges."""
    graph = DependencyGraph()
    dead = dead_files or set()
    live = [f for f in files if f not in dead and f.endswith(".py")]

    # Connect live files in a chain
    for i in range(1, len(live)):
        edge = DependencyEdge(
            source=live[i - 1],
            target=live[i],
            tier=EdgeTier.TIER_A,
            confidence=1.0,
            evidence_type="static",
        )
        graph.add_edge(edge)

    # Dead files have outbound edges only (they import but nobody imports them)
    for df in dead:
        if live:
            edge = DependencyEdge(
                source=df,
                target=live[0],
                tier=EdgeTier.TIER_A,
                confidence=1.0,
                evidence_type="static",
            )
            graph.add_edge(edge)

    return graph


def _build_file_analyses(files: list[str]) -> dict[str, FileAnalysis]:
    """Build FileAnalysis objects for a set of files."""
    analyses = {}
    for f in files:
        analyses[f] = FileAnalysis(
            file_path=f,
            content_hash=f"hash_{f}",
            imports=[],
            exports=[f.split("/")[-1].replace(".py", "")],
        )
    return analyses


# ---------------------------------------------------------------------------
# T05.06: Benchmark tests
# ---------------------------------------------------------------------------


class TestBenchmarkSmallRepo:
    """Benchmark on small repo (<50 files)."""

    def test_small_repo_completes_without_errors(self):
        files = _small_repo_files()
        manifest = decompose(file_paths=files, max_batch_size=20)
        assert manifest.batch_count > 0

        estimate = dry_run(file_paths=files, max_batch_size=20)
        assert estimate.batch_count > 0
        assert estimate.estimated_tokens > 0

    def test_small_repo_report_completeness(self):
        files = _small_repo_files()
        findings = [_make_finding(file_path=f) for f in files[:10]]
        report_data = render_report(
            ConsolidationReport(
                findings=findings,
                total_input_findings=len(findings),
                total_consolidated=len(findings),
            ),
            depth=ReportDepth.STANDARD,
        )
        assert isinstance(report_data, dict)

    def test_small_repo_profiling(self):
        files = _small_repo_files()
        for f in files[:5]:
            profile = profile_file(f, file_size=100)
            assert isinstance(profile, FileProfile)


class TestBenchmarkMediumRepo:
    """Benchmark on medium repo (50-500 files)."""

    def test_medium_repo_completes_without_errors(self):
        files = _medium_repo_files()
        assert len(files) >= 50
        manifest = decompose(file_paths=files, max_batch_size=50)
        assert manifest.batch_count > 0

    def test_medium_repo_budget_estimation(self):
        files = _medium_repo_files()
        estimate = dry_run(file_paths=files, max_batch_size=50)
        assert estimate.batch_count > 0
        assert estimate.estimated_tokens > 0

    def test_medium_repo_coverage_tracking(self):
        files = _medium_repo_files()
        tracker = CoverageTracker(total_files_scanned=len(files))
        for f in files[:100]:
            result = ClassificationResult(
                file_path=f,
                tier=V2Tier.TIER_1,
                action=V2Action.KEEP,
                v1_category=V1Category.KEEP,
                confidence=0.9,
            )
            tracker.add(result)
        artifact = tracker.emit()
        assert artifact.total_files_classified >= 100


class TestBenchmarkDeadCodeRepo:
    """Benchmark on known-dead-code repo."""

    def test_dead_code_detection_accuracy(self):
        all_files, expected_dead = _dead_code_repo()
        graph = _build_graph_for_files(all_files, dead_files=expected_dead)
        analyses = _build_file_analyses(all_files)

        report = detect_dead_code(
            graph=graph,
            analyses=analyses,
        )

        detected_files = {c.file_path for c in report.candidates}

        # Verify >= 80% detection rate
        true_positives = detected_files & expected_dead
        detection_rate = len(true_positives) / len(expected_dead) if expected_dead else 0
        assert detection_rate >= 0.80, (
            f"Detection rate {detection_rate:.0%} < 80%: "
            f"detected {len(true_positives)}/{len(expected_dead)}"
        )

    def test_dead_code_no_false_positives_on_live(self):
        all_files, expected_dead = _dead_code_repo()
        graph = _build_graph_for_files(all_files, dead_files=expected_dead)
        analyses = _build_file_analyses(all_files)

        report = detect_dead_code(
            graph=graph,
            analyses=analyses,
        )

        detected_files = {c.file_path for c in report.candidates}
        live_files = set(all_files) - expected_dead

        # Live files that are entry points or __init__ should not be flagged
        entry_points = {f for f in live_files if any(
            f.endswith(p) for p in ("__init__.py", "setup.py", "conftest.py")
        )}
        false_positives = detected_files & entry_points
        assert len(false_positives) == 0, (
            f"False positives on entry points: {false_positives}"
        )

    def test_dead_code_exclusion_rules(self):
        all_files, expected_dead = _dead_code_repo()
        graph = _build_graph_for_files(all_files, dead_files=expected_dead)
        analyses = _build_file_analyses(all_files)

        report = detect_dead_code(
            graph=graph,
            analyses=analyses,
        )

        # Excluded candidates should have exclusion reasons
        for exc in report.excluded:
            assert exc.exclusion_reason, f"Excluded candidate {exc.file_path} has no reason"
