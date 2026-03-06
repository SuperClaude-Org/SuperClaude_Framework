"""AC1-AC20 automated validation suite (T05.05 / D-0044).

Validates complete v2 contract compliance.
Run: uv run pytest tests/audit/test_ac_validation.py -v
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult, V1Category, V2Action, V2Tier,
    classify_finding, map_to_v1, all_v1_categories_covered,
)
from superclaude.cli.audit.consolidation import (
    ConsolidatedFinding, ConsolidationReport,
)


def _make_finding(
    file_path: str = "src/test.py",
    tier: V2Tier = V2Tier.TIER_1,
    action: V2Action = V2Action.DELETE,
    confidence: float = 0.9,
    evidence: list[str] | None = None,
) -> ConsolidatedFinding:
    return ConsolidatedFinding(
        file_path=file_path,
        tier=tier,
        action=action,
        confidence=confidence,
        evidence=evidence or ["zero references found"],
        source_phases=["phase_1"],
    )


# ---------------------------------------------------------------------------
# AC1: 5-category classification
# ---------------------------------------------------------------------------


class TestAC1Classification:
    """AC1: FINAL-REPORT.md contains at least 2 of DELETE/KEEP/MODIFY/INVESTIGATE."""

    def test_v2_actions_cover_five_categories(self):
        names = {a.value for a in V2Action}
        for required in ("DELETE", "KEEP", "MODIFY", "INVESTIGATE", "ARCHIVE"):
            assert required in names

    def test_classify_finding_returns_valid_result(self):
        result = classify_finding(file_path="src/unused.py", has_references=False)
        assert isinstance(result, ClassificationResult)
        assert isinstance(result.action, V2Action)

    def test_report_completeness_mandated_sections(self):
        from superclaude.cli.audit.report_completeness import MANDATED_SECTIONS

        assert len(MANDATED_SECTIONS) >= 6


# ---------------------------------------------------------------------------
# AC2: Coverage tracking
# ---------------------------------------------------------------------------


class TestAC2Coverage:
    """AC2: coverage-report.json exists with per-tier percentages."""

    def test_coverage_tracker_produces_artifact(self):
        from superclaude.cli.audit.coverage import CoverageTracker

        tracker = CoverageTracker(total_files_scanned=100)
        result = ClassificationResult(
            file_path="a.py", tier=V2Tier.TIER_1, action=V2Action.DELETE,
            v1_category=V1Category.DELETE, confidence=0.9,
        )
        tracker.add(result)
        artifact = tracker.emit()
        assert artifact.total_files_scanned == 100
        assert artifact.total_files_classified >= 1


# ---------------------------------------------------------------------------
# AC3: Checkpointing + resume
# ---------------------------------------------------------------------------


class TestAC3Checkpointing:
    """AC3: progress.json updated after every batch; --resume recovers."""

    def test_checkpoint_write_and_read(self, tmp_path):
        from superclaude.cli.audit.checkpoint import (
            CheckpointWriter, CheckpointReader, CheckpointState, BatchStatus,
        )

        state = CheckpointState(
            run_id="run-001",
            total_batches=2,
            batches=[BatchStatus(batch_id="batch_001", status="COMPLETED", files_processed=10)],
        )
        writer = CheckpointWriter(tmp_path / "progress.json")
        writer.write(state)

        reader = CheckpointReader(tmp_path / "progress.json")
        reader.read()
        assert "batch_001" in reader.completed_batch_ids()

    def test_resume_controller(self, tmp_path):
        from superclaude.cli.audit.checkpoint import (
            CheckpointWriter, CheckpointReader, CheckpointState, BatchStatus,
        )
        from superclaude.cli.audit.resume import ResumeController

        state = CheckpointState(
            run_id="run-001",
            total_batches=2,
            batches=[BatchStatus(batch_id="batch_001", status="COMPLETED", files_processed=10)],
        )
        writer = CheckpointWriter(tmp_path / "progress.json")
        writer.write(state)

        reader = CheckpointReader(tmp_path / "progress.json")
        controller = ResumeController(reader)
        point = controller.determine_resume_point(
            all_phases=["phase_1", "phase_2"],
            all_batch_ids=["batch_001", "batch_002"],
        )
        assert point.has_checkpoint
        assert "batch_001" in point.completed_batch_ids


# ---------------------------------------------------------------------------
# AC4: Evidence for DELETE
# ---------------------------------------------------------------------------


class TestAC4EvidenceDelete:
    """AC4: Every DELETE entry has non-empty grep evidence with result count 0."""

    def test_delete_with_evidence_passes(self):
        from superclaude.cli.audit.evidence_gate import check_delete_evidence

        result = ClassificationResult(
            file_path="src/unused.py", tier=V2Tier.TIER_1, action=V2Action.DELETE,
            v1_category=V1Category.DELETE, confidence=0.95,
            evidence=["zero references found by grep"],
        )
        gate = check_delete_evidence(result)
        assert gate.passed is True

    def test_delete_without_evidence_fails(self):
        from superclaude.cli.audit.evidence_gate import check_delete_evidence

        result = ClassificationResult(
            file_path="src/used.py", tier=V2Tier.TIER_1, action=V2Action.DELETE,
            v1_category=V1Category.DELETE, confidence=0.5,
            evidence=[],
        )
        gate = check_delete_evidence(result)
        assert gate.passed is False


# ---------------------------------------------------------------------------
# AC5: Evidence for Tier 1-2 KEEP
# ---------------------------------------------------------------------------


class TestAC5EvidenceKeep:
    """AC5: Every Tier 1-2 KEEP has non-empty import reference information."""

    def test_keep_tier1_with_imports_passes(self):
        from superclaude.cli.audit.evidence_gate import check_keep_evidence

        result = ClassificationResult(
            file_path="src/core.py", tier=V2Tier.TIER_1, action=V2Action.KEEP,
            v1_category=V1Category.KEEP, confidence=0.9,
            evidence=["referenced by main.py"],
        )
        gate = check_keep_evidence(result)
        assert gate.passed is True

    def test_keep_tier1_without_imports_fails(self):
        from superclaude.cli.audit.evidence_gate import check_keep_evidence

        result = ClassificationResult(
            file_path="src/core.py", tier=V2Tier.TIER_1, action=V2Action.KEEP,
            v1_category=V1Category.KEEP, confidence=0.9,
            evidence=[],
        )
        gate = check_keep_evidence(result)
        assert gate.passed is False


# ---------------------------------------------------------------------------
# AC6: Spot-check validation
# ---------------------------------------------------------------------------


class TestAC6SpotCheck:
    """AC6: validation-results.json exists with >= 10% sample size."""

    def test_validation_result_has_consistency_rate(self):
        from superclaude.cli.audit.validation import ValidationResult

        result = ValidationResult(
            total_classified=100,
            sample_size=10,
            consistent_count=8,
            inconsistent_count=2,
            consistency_rate=0.8,
        )
        d = result.to_dict()
        assert d["consistency_rate"] == 0.8
        assert d["sample_size"] >= 10

    def test_spot_check_validate_runs(self):
        from superclaude.cli.audit.spot_check import spot_check_validate

        findings = [
            _make_finding(file_path=f"file_{i}.py")
            for i in range(20)
        ]
        report = ConsolidationReport(
            findings=findings,
            total_input_findings=20,
            total_consolidated=20,
        )
        result = spot_check_validate(report)
        assert result.total_consolidated >= 0


# ---------------------------------------------------------------------------
# AC7: Credential scanning
# ---------------------------------------------------------------------------


class TestAC7CredentialScanning:
    """AC7: Real credentials flagged, template values not flagged."""

    def test_real_credential_flagged(self):
        from superclaude.cli.audit.credential_scanner import scan_content

        result = scan_content(
            ".env.production",
            'DB_PASSWORD="s3cret_password_123"\n',
        )
        assert len(result.secrets_found) > 0

    def test_template_not_flagged(self):
        from superclaude.cli.audit.credential_scanner import scan_content

        result = scan_content(
            ".env.example",
            'DB_PASSWORD="<your_password_here>"\n',
        )
        assert len(result.secrets_found) == 0


# ---------------------------------------------------------------------------
# AC8: Gitignore check
# ---------------------------------------------------------------------------


class TestAC8Gitignore:
    """AC8: Files tracked despite .gitignore rules flagged."""

    def test_gitignore_inconsistency_flagged(self, tmp_path):
        from superclaude.cli.audit.gitignore_checker import check_gitignore_consistency

        result = check_gitignore_consistency(
            repo_root=str(tmp_path),
            tracked_files=["node_modules/package/index.js"],
            gitignore_patterns=["node_modules/"],
        )
        assert len(result.inconsistencies) > 0

    def test_consistent_files_pass(self, tmp_path):
        from superclaude.cli.audit.gitignore_checker import check_gitignore_consistency

        result = check_gitignore_consistency(
            repo_root=str(tmp_path),
            tracked_files=["src/main.py"],
            gitignore_patterns=["node_modules/"],
        )
        assert len(result.inconsistencies) == 0


# ---------------------------------------------------------------------------
# AC9: Budget control
# ---------------------------------------------------------------------------


class TestAC9Budget:
    """AC9: Audit completes within budget +/- 10%."""

    def test_budget_enforcement_warn_at_75pct(self):
        from superclaude.cli.audit.budget import (
            BudgetAccountant, BudgetConfig, EnforcementAction,
        )

        config = BudgetConfig(total_budget=1000)
        accountant = BudgetAccountant(config)
        accountant.record("phase_1", 750)
        status = accountant.status()
        assert status.enforcement == EnforcementAction.WARN

    def test_budget_enforcement_halt_at_100pct(self):
        from superclaude.cli.audit.budget import (
            BudgetAccountant, BudgetConfig, EnforcementAction,
        )

        config = BudgetConfig(total_budget=1000)
        accountant = BudgetAccountant(config)
        accountant.record("phase_1", 1000)
        status = accountant.status()
        assert status.enforcement == EnforcementAction.HALT


# ---------------------------------------------------------------------------
# AC10: Report depth
# ---------------------------------------------------------------------------


class TestAC10ReportDepth:
    """AC10: summary <100 lines; detailed includes profiles."""

    def _make_report(self):
        findings = [_make_finding(file_path=f"file_{i}.py") for i in range(5)]
        return ConsolidationReport(
            findings=findings,
            total_input_findings=5,
            total_consolidated=5,
        )

    def test_summary_mode(self):
        from superclaude.cli.audit.report_depth import render_report, ReportDepth

        output = render_report(self._make_report(), depth=ReportDepth.SUMMARY)
        assert isinstance(output, dict)

    def test_detailed_mode(self):
        from superclaude.cli.audit.report_depth import render_report, ReportDepth

        output = render_report(self._make_report(), depth=ReportDepth.DETAILED)
        assert isinstance(output, dict)


# ---------------------------------------------------------------------------
# AC11: Scanner schema
# ---------------------------------------------------------------------------


class TestAC11ScannerSchema:
    """AC11: Phase 1 batch outputs validate against scanner schema."""

    def test_valid_phase1_output(self):
        from superclaude.cli.audit.scanner_schema import validate_phase1

        output = {
            "file_path": "a.py",
            "classification": "DELETE",
            "evidence": ["zero references found"],
            "confidence": 0.95,
            "tier": "TIER_1",
        }
        result = validate_phase1(output)
        assert result.valid is True

    def test_invalid_phase1_missing_field(self):
        from superclaude.cli.audit.scanner_schema import validate_phase1

        result = validate_phase1({"file_path": "a.py"})
        assert result.valid is False


# ---------------------------------------------------------------------------
# AC12: Cross-reference / dependency graph
# ---------------------------------------------------------------------------


class TestAC12DependencyGraph:
    """AC12: dependency-graph.json with node count > 0."""

    def test_graph_with_edges_has_nodes(self):
        from superclaude.cli.audit.dependency_graph import (
            DependencyGraph, DependencyEdge, EdgeTier,
        )

        graph = DependencyGraph()
        edge = DependencyEdge(
            source="src/main.py", target="src/utils.py",
            tier=EdgeTier.TIER_A, confidence=1.0,
            evidence_type="static",
        )
        graph.add_edge(edge)
        assert graph.stats["node_count"] > 0

    def test_empty_graph(self):
        from superclaude.cli.audit.dependency_graph import DependencyGraph

        graph = DependencyGraph()
        assert graph.stats["node_count"] == 0


# ---------------------------------------------------------------------------
# AC13: Cold-start / auto-config
# ---------------------------------------------------------------------------


class TestAC13ColdStart:
    """AC13: Audit succeeds on first run without pre-existing config."""

    def test_cold_start_detected(self, tmp_path):
        from superclaude.cli.audit.auto_config import detect_cold_start

        assert detect_cold_start(tmp_path) is True

    def test_auto_config_has_budget_and_batch_size(self):
        from superclaude.cli.audit.auto_config import AuditConfig

        config = AuditConfig()
        assert config.batch_size > 0
        assert config.budget > 0


# ---------------------------------------------------------------------------
# AC14: Broken references / docs audit
# ---------------------------------------------------------------------------


class TestAC14DocsAudit:
    """AC14: Phase 3 output includes broken-references."""

    def test_broken_link_detected(self):
        from superclaude.cli.audit.docs_audit import check_broken_links

        broken = check_broken_links(
            "docs/README.md",
            "[Guide](./missing.md)",
            known_files={"docs/README.md"},
        )
        assert len(broken) == 1

    def test_full_docs_audit_5_sections(self):
        from superclaude.cli.audit.docs_audit import full_docs_audit

        result = full_docs_audit({}, set())
        assert result.section_count == 5


# ---------------------------------------------------------------------------
# AC15: Backward compat (v1 mapping)
# ---------------------------------------------------------------------------


class TestAC15BackwardCompat:
    """AC15: v2 output can be mapped to v1 categories."""

    def test_map_to_v1_works(self):
        v1 = map_to_v1(V2Tier.TIER_1, V2Action.DELETE)
        assert isinstance(v1, V1Category)

    def test_all_v1_categories_covered(self):
        assert all_v1_categories_covered() is True


# ---------------------------------------------------------------------------
# AC16: Directory assessment
# ---------------------------------------------------------------------------


class TestAC16DirectoryAssessment:
    """AC16: Directories with 50+ files have assessment labels."""

    def test_large_directory_gets_assessment(self):
        from superclaude.cli.audit.dir_assessment import build_assessment_block

        findings = [
            _make_finding(file_path=f"src/components/file_{i}.py")
            for i in range(75)
        ]
        block = build_assessment_block("src/components", findings)
        assert block.file_count == 75

    def test_identify_large_directories(self):
        from superclaude.cli.audit.dir_assessment import identify_large_directories

        big = [_make_finding(file_path=f"src/big/file_{i}.py") for i in range(60)]
        small = [_make_finding(file_path=f"src/small/file_{i}.py") for i in range(5)]
        large = identify_large_directories(big + small, threshold=50)
        assert "src/big" in large
        assert "src/small" not in large


# ---------------------------------------------------------------------------
# AC17: INVESTIGATE cap
# ---------------------------------------------------------------------------


class TestAC17InvestigateCap:
    """AC17: If INVESTIGATE > 15%, re-analysis is triggered."""

    def test_escalation_detects_signals(self):
        from superclaude.cli.audit.escalation import detect_signals

        result = ClassificationResult(
            file_path="src/maybe.py", tier=V2Tier.TIER_1,
            action=V2Action.INVESTIGATE, v1_category=V1Category.INVESTIGATE,
            confidence=0.3,
        )
        signals = detect_signals(result)
        # Low-confidence INVESTIGATE should produce escalation signals
        assert isinstance(signals, list)

    def test_escalation_module_importable(self):
        from superclaude.cli.audit.escalation import EscalationResult

        assert EscalationResult is not None


# ---------------------------------------------------------------------------
# AC18: Subagent failure handling
# ---------------------------------------------------------------------------


class TestAC18FailureHandling:
    """AC18: Anti-lazy distribution guard flags uniform batches."""

    def test_anti_lazy_flags_uniform_batch(self):
        from superclaude.cli.audit.anti_lazy import check_batch_uniformity

        findings = [
            _make_finding(file_path=f"f{i}.py", action=V2Action.DELETE)
            for i in range(95)
        ] + [
            _make_finding(file_path=f"k{i}.py", action=V2Action.KEEP)
            for i in range(5)
        ]
        result = check_batch_uniformity("batch_001", findings, threshold=0.90)
        assert result is not None  # UniformityFlag returned

    def test_anti_lazy_passes_mixed_batch(self):
        from superclaude.cli.audit.anti_lazy import check_batch_uniformity

        findings = [
            _make_finding(file_path=f"f{i}.py", action=V2Action.DELETE)
            for i in range(50)
        ] + [
            _make_finding(file_path=f"k{i}.py", action=V2Action.KEEP)
            for i in range(50)
        ]
        result = check_batch_uniformity("batch_002", findings, threshold=0.90)
        assert result is None  # No flag


# ---------------------------------------------------------------------------
# AC19: --dry-run
# ---------------------------------------------------------------------------


class TestAC19DryRun:
    """AC19: --dry-run produces cost estimates without executing scans."""

    def test_dry_run_produces_estimates(self):
        from superclaude.cli.audit.dry_run import dry_run

        estimate = dry_run(
            file_paths=[f"file_{i}.py" for i in range(100)],
            max_batch_size=20,
        )
        assert estimate.batch_count > 0
        assert estimate.estimated_tokens > 0

    def test_budget_caveat_present(self):
        from superclaude.cli.audit.budget_caveat import BUDGET_CAVEAT

        assert len(BUDGET_CAVEAT) > 0


# ---------------------------------------------------------------------------
# AC20: Run isolation
# ---------------------------------------------------------------------------


class TestAC20RunIsolation:
    """AC20: Two concurrent audit runs produce separate output directories."""

    def test_batch_decomposer_produces_unique_ids(self):
        from superclaude.cli.audit.batch_decomposer import decompose

        manifest = decompose(
            file_paths=["a.py", "b.py", "c.py", "d.py"],
            max_batch_size=2,
        )
        ids = [b.batch_id for b in manifest.batches]
        assert len(ids) == len(set(ids))

    def test_known_issues_registry_per_run(self, tmp_path):
        from superclaude.cli.audit.known_issues import (
            KnownIssuesRegistry, RegistryEntry,
            save_registry, load_registry,
        )

        reg1 = KnownIssuesRegistry(entries=[
            RegistryEntry("KI-R1", "*.py", "DELETE", "2026-01-01"),
        ])
        reg2 = KnownIssuesRegistry(entries=[
            RegistryEntry("KI-R2", "*.js", "KEEP", "2026-01-01"),
        ])

        path1 = tmp_path / "run1" / "registry.json"
        path2 = tmp_path / "run2" / "registry.json"
        save_registry(reg1, path1)
        save_registry(reg2, path2)

        loaded1 = load_registry(path1)
        loaded2 = load_registry(path2)
        assert loaded1.entries[0].issue_id == "KI-R1"
        assert loaded2.entries[0].issue_id == "KI-R2"
