"""End-to-end integration test for the full 12-step pipeline (T07.01).

Tests SC-001: roadmap run must complete all 12 steps without manual intervention.
Uses a controlled mock runner (not ClaudeProcess mock) that writes gate-passing
output files per step, then validates the orchestration logic end-to-end.

The mock runner follows the same pattern as test_executor.py::TestIntegrationMockSubprocess
but extends coverage to the full 12-step pipeline including:
- Steps 1-9: extract, generate-A, generate-B, diff, debate, score, merge,
  test-strategy, spec-fidelity
- Step 10: validate (auto-invoked post-pipeline)
- Step 11: remediate (remediation-tasklist.md)
- Step 12: certify (certification-report.md)
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.executor import execute_pipeline
from superclaude.cli.pipeline.models import Step, StepResult, StepStatus
from superclaude.cli.roadmap.certify_prompts import (
    generate_certification_report,
    parse_certification_output,
    route_certification_outcome,
)
from superclaude.cli.roadmap.executor import (
    _build_steps,
    _save_state,
    build_certify_metadata,
    build_certify_step,
    build_remediate_metadata,
    derive_pipeline_status,
    read_state,
    write_state,
)
from superclaude.cli.roadmap.gates import CERTIFY_GATE, REMEDIATE_GATE
from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.roadmap.models import AgentSpec, Finding, RoadmapConfig
from superclaude.cli.roadmap.remediate import (
    RemediationScope,
    filter_findings,
    format_validation_summary,
    generate_remediation_tasklist,
    generate_stub_tasklist,
)
from superclaude.cli.roadmap.remediate_executor import (
    EDITABLE_FILES,
    enforce_allowlist,
)
from superclaude.cli.roadmap.remediate_parser import parse_validation_report


def _now():
    return datetime.now(timezone.utc)


def _make_config(tmp_path: Path) -> RoadmapConfig:
    spec = tmp_path / "spec.md"
    spec.write_text("# Test Spec\nContent for testing.\n")
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    return RoadmapConfig(
        spec_file=spec,
        output_dir=output,
        agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
        depth="standard",
    )


def _gate_passing_content(step: Step) -> str:
    """Generate gate-passing output content for any step."""
    fm_values = {
        "spec_source": "spec.md",
        "generated": "2026-03-10T00:00:00Z",
        "generator": "test-agent",
        "functional_requirements": "5",
        "nonfunctional_requirements": "3",
        "total_requirements": "8",
        "complexity_score": "0.7",
        "complexity_class": "moderate",
        "domains_detected": "2",
        "risks_identified": "3",
        "dependencies_identified": "4",
        "success_criteria_count": "5",
        "extraction_mode": "full",
        "primary_persona": "architect",
        "total_diff_points": "3",
        "shared_assumptions_count": "4",
        "convergence_score": "0.85",
        "rounds_completed": "2",
        "base_variant": "A",
        "variant_scores": "A:78 B:72",
        "adversarial": "true",
        "validation_milestones": "3",
        "interleave_ratio": "1:3",
        "high_severity_count": "0",
        "medium_severity_count": "0",
        "low_severity_count": "0",
        "total_deviations": "0",
        "validation_complete": "true",
        "tasklist_ready": "true",
        "fidelity_check_attempted": "true",
    }

    fm_fields = {}
    if step.gate and step.gate.required_frontmatter_fields:
        for f in step.gate.required_frontmatter_fields:
            fm_fields[f] = fm_values.get(f, "test_value")

    content_lines = ["---"]
    for k, v in fm_fields.items():
        content_lines.append(f"{k}: {v}")
    content_lines.append("---")
    content_lines.append("## Overview")
    min_needed = step.gate.min_lines if step.gate else 10
    for i in range(max(min_needed, 10)):
        content_lines.append(f"- Item {i}: content for {step.id}")
    return "\n".join(content_lines)


def _mock_runner(step, cfg, cancel_check):
    """Mock step runner that writes gate-passing output."""
    content = _gate_passing_content(step)
    step.output_file.parent.mkdir(parents=True, exist_ok=True)
    step.output_file.write_text(content)
    return StepResult(
        step=step,
        status=StepStatus.PASS,
        attempt=1,
        started_at=_now(),
        finished_at=_now(),
    )


# ═══════════════════════════════════════════════════════════════
# T07.01 -- E2E Integration Test (SC-001)
# ═══════════════════════════════════════════════════════════════


class TestE2EFullPipeline:
    """SC-001: Full 12-step pipeline completes with PASS status."""

    def test_e2e_steps_1_through_9_complete(self, tmp_path):
        """Steps 1-9 execute with mock runner and all pass gates."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)

        results = execute_pipeline(
            steps=steps,
            config=config,
            run_step=_mock_runner,
        )

        # 9 individual steps (2 parallel generate + 7 sequential)
        assert len(results) == 9
        assert all(r.status == StepStatus.PASS for r in results)

    def test_e2e_state_saved_after_steps_1_9(self, tmp_path):
        """State file written with all 9 steps after pipeline completion."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)

        results = execute_pipeline(
            steps=steps,
            config=config,
            run_step=_mock_runner,
        )
        _save_state(config, results)

        state = read_state(config.output_dir / ".roadmap-state.json")
        assert state is not None
        assert state["schema_version"] == 1
        assert "extract" in state["steps"]
        assert state["steps"]["extract"]["status"] == "PASS"

    def test_e2e_validation_report_creates_findings(self, tmp_path):
        """Step 10: Validation report with controlled findings can be parsed."""
        report = (
            "## Consolidated Findings\n\n"
            "### BLOCKING\n\n"
            "**[F-01] [BLOCKING] Completeness: Missing milestone 5**\n\n"
            "- Location: roadmap.md:45\n"
            "- Evidence: Spec requires 5 milestones, only 4 found\n"
            "- Fix guidance: Add milestone 5 covering deployment\n\n"
            "### WARNING\n\n"
            "**[F-02] [WARNING] Clarity: Ambiguous success criteria**\n\n"
            "- Location: roadmap.md:100\n"
            "- Evidence: SC-003 lacks measurable target\n"
            "- Fix guidance: Add specific metric to SC-003\n\n"
            "### INFO\n\n"
            "**[F-03] [INFO] Style: Inconsistent heading format**\n\n"
            "- Location: extraction.md:12\n"
            "- Evidence: Mix of Title Case and lowercase\n"
            "- Fix guidance: Standardize to Title Case\n"
        )
        findings = parse_validation_report(report)
        assert len(findings) == 3
        assert findings[0].severity == "BLOCKING"
        assert findings[1].severity == "WARNING"
        assert findings[2].severity == "INFO"

    def test_e2e_remediation_tasklist_generated(self, tmp_path):
        """Step 11: Remediation tasklist generated from findings."""
        findings = [
            Finding(
                id="F-01", severity="BLOCKING", dimension="Completeness",
                description="Missing milestone", location="roadmap.md:45",
                evidence="Only 4 milestones", fix_guidance="Add milestone 5",
                files_affected=["roadmap.md"],
            ),
            Finding(
                id="F-02", severity="WARNING", dimension="Clarity",
                description="Ambiguous criteria", location="roadmap.md:100",
                evidence="SC-003 lacks target", fix_guidance="Add metric",
                files_affected=["roadmap.md"],
            ),
        ]
        source_content = "# Validation Report\nContent.\n"
        tasklist = generate_remediation_tasklist(
            findings, "reflect-merged.md", source_content
        )
        assert "type: remediation-tasklist" in tasklist
        assert "F-01" in tasklist
        assert "F-02" in tasklist
        assert "BLOCKING" in tasklist

    def test_e2e_certification_report_generated(self, tmp_path):
        """Step 12: Certification report generated from verification results."""
        findings = [
            Finding(
                id="F-01", severity="BLOCKING", dimension="Completeness",
                description="Missing milestone", location="roadmap.md:45",
                evidence="Only 4 milestones", fix_guidance="Add milestone 5",
                files_affected=["roadmap.md"],
            ),
        ]
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Milestone 5 added"},
        ]
        report = generate_certification_report(results, findings)

        assert "findings_verified: 1" in report
        assert "findings_passed: 1" in report
        assert "findings_failed: 0" in report
        assert "certified: true" in report
        assert "| F-01 |" in report

    def test_e2e_certification_report_passes_gate(self, tmp_path):
        """Certification report passes CERTIFY_GATE validation."""
        findings = [
            Finding(
                id="F-01", severity="BLOCKING", dimension="Completeness",
                description="Missing milestone", location="roadmap.md:45",
                evidence="test", fix_guidance="test",
                files_affected=["roadmap.md"],
            ),
        ]
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Fixed correctly"},
        ]
        report = generate_certification_report(results, findings)

        # Write to file and validate gate
        report_file = tmp_path / "certification-report.md"
        report_file.write_text(report)

        passed, reason = gate_passed(report_file, CERTIFY_GATE)
        assert passed, f"CERTIFY_GATE failed: {reason}"

    def test_e2e_remediation_tasklist_passes_gate(self, tmp_path):
        """Remediation tasklist after two-write model passes REMEDIATE_GATE.

        Two-write model: first write generates PENDING entries, second write
        (update_remediation_tasklist) stamps terminal statuses (FIXED/FAILED).
        """
        from superclaude.cli.roadmap.remediate_executor import update_remediation_tasklist

        # Step 1: Generate tasklist with all-PENDING findings (no SKIPPED)
        findings_pending = [
            Finding(
                id="F-01", severity="BLOCKING", dimension="Completeness",
                description="Missing milestone", location="roadmap.md:45",
                evidence="test", fix_guidance="test",
                files_affected=["roadmap.md"], status="PENDING",
            ),
        ]
        source_content = "# Report\n"
        tasklist = generate_remediation_tasklist(
            findings_pending, "reflect-merged.md", source_content
        )
        tasklist_file = tmp_path / "remediation-tasklist.md"
        tasklist_file.write_text(tasklist)

        # Step 2: Simulate remediation -> mark F-01 as FIXED
        findings_done = [
            Finding(
                id="F-01", severity="BLOCKING", dimension="Completeness",
                description="Missing milestone", location="roadmap.md:45",
                evidence="test", fix_guidance="test",
                files_affected=["roadmap.md"], status="FIXED",
            ),
        ]
        update_remediation_tasklist(str(tasklist_file), findings_done)

        passed, reason = gate_passed(tasklist_file, REMEDIATE_GATE)
        assert passed, f"REMEDIATE_GATE failed: {reason}"

    def test_e2e_state_with_all_12_steps(self, tmp_path):
        """State file contains all steps including remediate and certify."""
        config = _make_config(tmp_path)
        steps = _build_steps(config)

        # Run steps 1-9
        results = execute_pipeline(
            steps=steps, config=config, run_step=_mock_runner,
        )

        # Add remediate and certify metadata
        remediate_meta = build_remediate_metadata(
            status="PASS", scope="all",
            findings_total=2, findings_actionable=1,
            findings_fixed=1, findings_failed=0, findings_skipped=1,
            agents_spawned=1, tasklist_file="output/remediation-tasklist.md",
        )
        certify_meta = build_certify_metadata(
            status="certified", findings_verified=1,
            findings_passed=1, findings_failed=0,
            certified=True, report_file="output/certification-report.md",
        )

        _save_state(config, results,
                     remediate_metadata=remediate_meta,
                     certify_metadata=certify_meta)

        state = read_state(config.output_dir / ".roadmap-state.json")
        assert state is not None

        # Verify all 9 step results + remediate + certify metadata
        assert len(state["steps"]) == 9
        assert all(
            state["steps"][sid]["status"] == "PASS"
            for sid in state["steps"]
        )
        assert state["remediate"]["status"] == "PASS"
        assert state["certify"]["certified"] is True

        # Pipeline status should be "certified"
        assert derive_pipeline_status(state) == "certified"

    def test_e2e_pipeline_status_transitions(self):
        """Verify pipeline status transitions through all 12 steps."""
        # Step 0: No data
        assert derive_pipeline_status({}) == "pending"

        # Step 10: Post-validate (pass)
        assert derive_pipeline_status({"validation": {"status": "pass"}}) == "validated"

        # Step 10: Post-validate (fail)
        assert derive_pipeline_status({"validation": {"status": "fail"}}) == "validated-with-issues"

        # Step 11: Post-remediate
        state = {"validation": {"status": "fail"}, "remediate": {"status": "PASS"}}
        assert derive_pipeline_status(state) == "remediated"

        # Step 12: Post-certify (all pass)
        state["certify"] = {"certified": True}
        assert derive_pipeline_status(state) == "certified"

        # Step 12: Post-certify (some fail)
        state["certify"] = {"certified": False}
        assert derive_pipeline_status(state) == "certified-with-caveats"

    def test_e2e_build_certify_step(self, tmp_path):
        """build_certify_step produces a valid Step with CERTIFY_GATE."""
        config = _make_config(tmp_path)
        findings = [
            Finding(
                id="F-01", severity="BLOCKING", dimension="Test",
                description="Test finding", location="roadmap.md:1",
                evidence="test", fix_guidance="test",
                files_affected=["roadmap.md"],
            ),
        ]
        step = build_certify_step(config, findings=findings)
        assert step.id == "certify"
        assert step.gate == CERTIFY_GATE
        assert step.timeout_seconds == 300
        assert "certification specialist" in step.prompt

    def test_e2e_full_flow_validation_to_certification(self, tmp_path):
        """Full flow: parse findings -> filter -> tasklist -> certify -> report."""
        config = _make_config(tmp_path)
        out = config.output_dir

        # 1. Parse validation report
        report_text = (
            "## Consolidated Findings\n\n"
            "**[F-01] [BLOCKING] Completeness: Missing milestone**\n\n"
            "- Location: roadmap.md:45\n"
            "- Evidence: Only 4 milestones\n"
            "- Fix guidance: Add milestone 5\n\n"
            "**[F-02] [WARNING] Clarity: Ambiguous criteria**\n\n"
            "- Location: roadmap.md:100\n"
            "- Evidence: SC-003 lacks target\n"
            "- Fix guidance: Add metric to SC-003\n\n"
            "**[F-03] [INFO] Style: Inconsistent headings**\n\n"
            "- Location: extraction.md:12\n"
            "- Evidence: Mix of formats\n"
            "- Fix guidance: Standardize headings\n"
        )
        findings = parse_validation_report(report_text)
        assert len(findings) == 3

        # 2. Format summary
        summary = format_validation_summary(findings)
        assert "BLOCKING: 1" in summary
        assert "WARNING: 1" in summary

        # 3. Filter by scope
        actionable, skipped = filter_findings(findings, RemediationScope.BLOCKING_WARNING)
        assert len(actionable) == 2  # BLOCKING + WARNING
        assert len(skipped) == 1     # INFO

        # 4. Generate tasklist
        tasklist = generate_remediation_tasklist(
            findings, "reflect-merged.md", report_text
        )
        assert "type: remediation-tasklist" in tasklist

        # 5. Simulate remediation (mark findings as FIXED)
        for f in findings:
            if f.severity in ("BLOCKING", "WARNING"):
                f.status = "FIXED"
            else:
                f.status = "SKIPPED"

        # 6. Generate certification results
        cert_results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Milestone 5 added"},
            {"finding_id": "F-02", "result": "PASS", "justification": "Metric added to SC-003"},
        ]

        # 7. Generate report
        cert_report = generate_certification_report(cert_results, findings)
        assert "certified: true" in cert_report

        # 8. Route outcome
        outcome = route_certification_outcome(cert_results)
        assert outcome["status"] == "certified"
        assert outcome["tasklist_ready"] is True
        assert outcome["loop"] is False  # NFR-012

        # 9. Verify report passes gate
        report_file = out / "certification-report.md"
        report_file.write_text(cert_report)
        passed, reason = gate_passed(report_file, CERTIFY_GATE)
        assert passed, f"Gate failed: {reason}"
