"""Tests for cross-phase deduplication and consolidation engine (T04.01 / D-0027)."""

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
)
from superclaude.cli.audit.consolidation import (
    ConsolidatedFinding,
    ConsolidationReport,
    PhaseFinding,
    consolidate,
)


def _make_result(
    file_path: str,
    tier: V2Tier = V2Tier.TIER_2,
    action: V2Action = V2Action.KEEP,
    confidence: float = 0.85,
    evidence: list[str] | None = None,
) -> ClassificationResult:
    from superclaude.cli.audit.classification import map_to_v1

    return ClassificationResult(
        file_path=file_path,
        tier=tier,
        action=action,
        v1_category=map_to_v1(tier, action),
        confidence=confidence,
        evidence=evidence or [],
    )


class TestConsolidateDedup:
    """Verify deduplication by file_path."""

    def test_unique_file_entries(self):
        """Consolidated output has exactly one entry per file path."""
        findings = [
            PhaseFinding("surface", _make_result("a.py", evidence=["ev1"])),
            PhaseFinding("structural", _make_result("a.py", evidence=["ev2"])),
            PhaseFinding("surface", _make_result("b.py", evidence=["ev3"])),
        ]
        report = consolidate(findings)
        paths = [f.file_path for f in report.findings]
        assert len(paths) == len(set(paths)), "Duplicate file entries found"
        assert set(paths) == {"a.py", "b.py"}

    def test_evidence_merged(self):
        """Evidence from all phases is merged into the consolidated entry."""
        findings = [
            PhaseFinding("surface", _make_result("a.py", evidence=["ev1", "ev2"])),
            PhaseFinding("structural", _make_result("a.py", evidence=["ev3"])),
            PhaseFinding("cross-cutting", _make_result("a.py", evidence=["ev4"])),
        ]
        report = consolidate(findings)
        a_finding = [f for f in report.findings if f.file_path == "a.py"][0]
        assert set(a_finding.evidence) == {"ev1", "ev2", "ev3", "ev4"}

    def test_no_duplicate_evidence(self):
        """Same evidence string from multiple phases is not duplicated."""
        findings = [
            PhaseFinding("surface", _make_result("a.py", evidence=["shared"])),
            PhaseFinding("structural", _make_result("a.py", evidence=["shared"])),
        ]
        report = consolidate(findings)
        a_finding = [f for f in report.findings if f.file_path == "a.py"][0]
        assert a_finding.evidence.count("shared") == 1

    def test_source_phases_tracked(self):
        """Source phases are recorded for each consolidated finding."""
        findings = [
            PhaseFinding("surface", _make_result("a.py")),
            PhaseFinding("cross-cutting", _make_result("a.py")),
        ]
        report = consolidate(findings)
        a_finding = report.findings[0]
        assert "surface" in a_finding.source_phases
        assert "cross-cutting" in a_finding.source_phases


class TestConflictResolution:
    """Verify highest-confidence-wins conflict resolution."""

    def test_conflict_resolved_by_highest_confidence(self):
        """When phases disagree, highest confidence wins."""
        findings = [
            PhaseFinding(
                "surface",
                _make_result("a.py", tier=V2Tier.TIER_1, action=V2Action.DELETE, confidence=0.70),
            ),
            PhaseFinding(
                "structural",
                _make_result("a.py", tier=V2Tier.TIER_2, action=V2Action.KEEP, confidence=0.95),
            ),
        ]
        report = consolidate(findings)
        a_finding = [f for f in report.findings if f.file_path == "a.py"][0]
        assert a_finding.tier == V2Tier.TIER_2
        assert a_finding.action == V2Action.KEEP
        assert a_finding.confidence == 0.95

    def test_conflict_logged(self):
        """Conflicts are logged in the report."""
        findings = [
            PhaseFinding(
                "surface",
                _make_result("a.py", tier=V2Tier.TIER_1, action=V2Action.DELETE, confidence=0.70),
            ),
            PhaseFinding(
                "structural",
                _make_result("a.py", tier=V2Tier.TIER_2, action=V2Action.KEEP, confidence=0.95),
            ),
        ]
        report = consolidate(findings)
        assert len(report.conflicts) == 1
        assert report.conflicts[0].file_path == "a.py"
        assert report.conflicts[0].winner_phase == "structural"

    def test_no_conflict_when_agree(self):
        """No conflict recorded when phases agree on classification."""
        findings = [
            PhaseFinding("surface", _make_result("a.py", confidence=0.85)),
            PhaseFinding("structural", _make_result("a.py", confidence=0.90)),
        ]
        report = consolidate(findings)
        assert len(report.conflicts) == 0

    def test_conflict_record_in_finding(self):
        """Conflict record attached to the consolidated finding."""
        findings = [
            PhaseFinding(
                "surface",
                _make_result("a.py", tier=V2Tier.TIER_1, action=V2Action.DELETE, confidence=0.60),
            ),
            PhaseFinding(
                "structural",
                _make_result("a.py", tier=V2Tier.TIER_2, action=V2Action.KEEP, confidence=0.90),
            ),
        ]
        report = consolidate(findings)
        a_finding = [f for f in report.findings if f.file_path == "a.py"][0]
        assert a_finding.conflict is not None
        assert a_finding.conflict.resolution_rule == "highest-confidence-wins"


class TestConsolidationReport:
    """Verify report structure and serialization."""

    def test_report_counts(self):
        """Report tracks input and consolidated counts."""
        findings = [
            PhaseFinding("surface", _make_result("a.py")),
            PhaseFinding("structural", _make_result("a.py")),
            PhaseFinding("surface", _make_result("b.py")),
        ]
        report = consolidate(findings)
        assert report.total_input_findings == 3
        assert report.total_consolidated == 2

    def test_to_dict_roundtrip(self):
        """Report serializes to dict without errors."""
        findings = [
            PhaseFinding(
                "surface",
                _make_result("a.py", tier=V2Tier.TIER_1, action=V2Action.DELETE, confidence=0.70),
            ),
            PhaseFinding(
                "structural",
                _make_result("a.py", tier=V2Tier.TIER_2, action=V2Action.KEEP, confidence=0.95),
            ),
        ]
        report = consolidate(findings)
        d = report.to_dict()
        assert d["total_input_findings"] == 2
        assert d["total_consolidated"] == 1
        assert d["conflict_count"] == 1
        assert len(d["findings"]) == 1
        assert d["findings"][0]["v1_category"] == "KEEP"

    def test_file_paths_accessor(self):
        """file_paths() returns set of all consolidated file paths."""
        findings = [
            PhaseFinding("surface", _make_result("a.py")),
            PhaseFinding("surface", _make_result("b.py")),
        ]
        report = consolidate(findings)
        assert report.file_paths() == {"a.py", "b.py"}

    def test_empty_input(self):
        """Empty input produces empty report."""
        report = consolidate([])
        assert report.total_input_findings == 0
        assert report.total_consolidated == 0
        assert len(report.findings) == 0
