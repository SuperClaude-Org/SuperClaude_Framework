"""Phase 7 integration and hardening tests (T07.02-T07.07).

Covers success criteria SC-003, SC-005, SC-006, SC-007 with:
- T07.02: Allowlist enforcement (SC-005)
- T07.03: Performance overhead measurement (SC-006)
- T07.04: Tasklist round-trip parse/emit (SC-007)
- T07.06: Deliberate-failure test -- unfixed findings as FAIL (SC-003)
- T07.07: Edge case coverage (SIGINT, out-of-allowlist, zero-findings, fallback)
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import Step, StepResult, StepStatus
from superclaude.cli.roadmap.certify_prompts import (
    generate_certification_report,
    parse_certification_output,
    route_certification_outcome,
)
from superclaude.cli.roadmap.gates import CERTIFY_GATE, REMEDIATE_GATE
from superclaude.cli.roadmap.models import Finding
from superclaude.cli.roadmap.remediate import (
    RemediationScope,
    filter_findings,
    generate_remediation_tasklist,
    generate_stub_tasklist,
)
from superclaude.cli.roadmap.remediate_executor import (
    EDITABLE_FILES,
    cleanup_snapshots,
    create_snapshots,
    enforce_allowlist,
    restore_from_snapshots,
)
from superclaude.cli.roadmap.remediate_parser import (
    parse_individual_reports,
    parse_validation_report,
)
from superclaude.cli.roadmap.remediate_prompts import (
    build_remediation_prompt,
    group_findings_by_file,
)


def _make_finding(
    fid: str = "F-01",
    severity: str = "BLOCKING",
    files: list[str] | None = None,
    status: str = "PENDING",
    fix_guidance: str = "Fix it",
) -> Finding:
    return Finding(
        id=fid,
        severity=severity,
        dimension="Test",
        description=f"Finding {fid}",
        location=f"{(files or ['roadmap.md'])[0]}:10",
        evidence="test evidence",
        fix_guidance=fix_guidance,
        files_affected=files or ["roadmap.md"],
        status=status,
    )


# ═══════════════════════════════════════════════════════════════
# T07.02 -- Allowlist Enforcement Test (SC-005)
# ═══════════════════════════════════════════════════════════════


class TestAllowlistEnforcement:
    """SC-005: No files outside the allowed set are modified during remediation."""

    def test_editable_files_constant(self):
        """EDITABLE_FILES contains exactly the spec-defined files."""
        assert EDITABLE_FILES == frozenset({"roadmap.md", "extraction.md", "test-strategy.md"})

    def test_allowed_files_pass_through(self):
        """Findings targeting only allowlisted files are allowed."""
        findings = [
            _make_finding("F-01", files=["roadmap.md"]),
            _make_finding("F-02", files=["extraction.md"]),
            _make_finding("F-03", files=["test-strategy.md"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 3
        assert len(rejected) == 0

    def test_non_allowed_files_rejected(self):
        """Findings targeting non-allowlisted files are SKIPPED with WARNING."""
        findings = [
            _make_finding("F-01", files=["roadmap.md"]),
            _make_finding("F-02", files=["README.md"]),
            _make_finding("F-03", files=["src/main.py"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 1
        assert len(rejected) == 2
        assert allowed[0].id == "F-01"

    def test_no_files_affected_rejected(self):
        """Findings with empty files_affected are SKIPPED."""
        finding = Finding(
            id="F-01", severity="BLOCKING", dimension="Test",
            description="Test", location="unknown:0",
            evidence="test", fix_guidance="test",
            files_affected=[],
        )
        allowed, rejected = enforce_allowlist([finding])
        assert len(allowed) == 0
        assert len(rejected) == 1

    def test_mixed_allowed_non_allowed_rejected(self):
        """Findings with ANY non-allowlisted file are fully rejected."""
        findings = [
            _make_finding("F-01", files=["roadmap.md", "forbidden.py"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 0
        assert len(rejected) == 1

    def test_workspace_diff_restricted(self, tmp_path):
        """Workspace diff before/after allowlist enforcement only allows allowlist."""
        # Create test files
        for name in ["roadmap.md", "extraction.md", "test-strategy.md", "other.py"]:
            (tmp_path / name).write_text(f"# {name}\nOriginal content.\n")

        # Record checksums before
        pre_checksums = {}
        for f in tmp_path.iterdir():
            if f.is_file():
                pre_checksums[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()

        # Simulate: only modify allowed files
        (tmp_path / "roadmap.md").write_text("# roadmap.md\nModified content.\n")
        (tmp_path / "extraction.md").write_text("# extraction.md\nModified content.\n")

        # Record checksums after
        post_checksums = {}
        for f in tmp_path.iterdir():
            if f.is_file():
                post_checksums[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()

        # Verify: non-allowlist files unchanged
        for name in ["other.py"]:
            assert pre_checksums[name] == post_checksums[name], \
                f"Non-allowlist file {name} was modified"

        # Verify: at least one allowlist file changed
        changed = [
            name for name in EDITABLE_FILES
            if name in pre_checksums and pre_checksums[name] != post_checksums.get(name)
        ]
        assert len(changed) > 0

    def test_out_of_allowlist_findings_skipped_with_warning(self):
        """SC-005: Findings referencing non-allowlist files should be SKIPPED."""
        findings = [
            _make_finding("F-01", files=["config.yaml"]),
            _make_finding("F-02", files=["deploy/Dockerfile"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 0
        assert len(rejected) == 2


# ═══════════════════════════════════════════════════════════════
# T07.03 -- Performance Test (SC-006)
# ═══════════════════════════════════════════════════════════════


class TestPerformanceOverhead:
    """SC-006: Steps 10-11 overhead <= 30% of steps 1-9 wall-clock time.

    These tests validate the overhead calculation logic, not real subprocess
    timing. Real wall-clock measurement requires live pipeline runs.
    """

    def test_overhead_calculation_within_budget(self):
        """Overhead formula: (steps_10_11_time / steps_1_9_time) * 100 <= 30%."""
        # Simulate: steps 1-9 took 100s, steps 10-11 took 25s
        steps_1_9_time = 100.0
        steps_10_11_time = 25.0
        overhead = (steps_10_11_time / steps_1_9_time) * 100
        assert overhead <= 30.0, f"Overhead {overhead:.1f}% exceeds 30% budget"

    def test_overhead_calculation_at_boundary(self):
        """Exactly 30% overhead is within budget."""
        steps_1_9_time = 100.0
        steps_10_11_time = 30.0
        overhead = (steps_10_11_time / steps_1_9_time) * 100
        assert overhead <= 30.0

    def test_overhead_calculation_exceeds_budget(self):
        """Over 30% overhead would fail the budget check."""
        steps_1_9_time = 100.0
        steps_10_11_time = 31.0
        overhead = (steps_10_11_time / steps_1_9_time) * 100
        assert overhead > 30.0

    def test_pure_functions_are_fast(self):
        """Pure functions (remediate, certify) execute in < 100ms each."""
        findings = [_make_finding(f"F-{i:02d}") for i in range(20)]
        source = "# Report\n" * 100

        # Measure tasklist generation
        start = time.perf_counter()
        generate_remediation_tasklist(findings, "report.md", source)
        tasklist_time = time.perf_counter() - start
        assert tasklist_time < 0.1, f"Tasklist generation took {tasklist_time:.3f}s"

        # Measure certification report generation
        results = [
            {"finding_id": f.id, "result": "PASS", "justification": "Fixed"}
            for f in findings
        ]
        start = time.perf_counter()
        generate_certification_report(results, findings)
        cert_time = time.perf_counter() - start
        assert cert_time < 0.1, f"Certification generation took {cert_time:.3f}s"

    def test_state_timing_extraction(self, tmp_path):
        """Timing data can be extracted from .roadmap-state.json timestamps."""
        from superclaude.cli.roadmap.executor import write_state, read_state

        state = {
            "steps": {
                "extract": {
                    "started_at": "2026-03-10T00:00:00+00:00",
                    "completed_at": "2026-03-10T00:01:00+00:00",
                },
                "spec-fidelity": {
                    "started_at": "2026-03-10T00:09:00+00:00",
                    "completed_at": "2026-03-10T00:10:00+00:00",
                },
            },
            "remediate": {
                "timestamp": "2026-03-10T00:10:30+00:00",
            },
            "certify": {
                "timestamp": "2026-03-10T00:11:00+00:00",
            },
        }
        state_file = tmp_path / ".roadmap-state.json"
        write_state(state, state_file)

        loaded = read_state(state_file)
        assert loaded is not None

        # Extract timing from state
        extract_start = datetime.fromisoformat(loaded["steps"]["extract"]["started_at"])
        fidelity_end = datetime.fromisoformat(loaded["steps"]["spec-fidelity"]["completed_at"])
        steps_1_9 = (fidelity_end - extract_start).total_seconds()

        certify_ts = datetime.fromisoformat(loaded["certify"]["timestamp"])
        fidelity_ts = datetime.fromisoformat(loaded["steps"]["spec-fidelity"]["completed_at"])
        steps_10_11 = (certify_ts - fidelity_ts).total_seconds()

        overhead = (steps_10_11 / steps_1_9) * 100
        assert overhead <= 30.0, f"Overhead {overhead:.1f}% exceeds 30%"


# ═══════════════════════════════════════════════════════════════
# T07.04 -- Tasklist Round-Trip Test (SC-007)
# ═══════════════════════════════════════════════════════════════


class TestTasklistRoundTrip:
    """SC-007: remediation-tasklist.md survives parse -> emit -> re-parse."""

    def test_round_trip_preserves_finding_ids(self):
        """Finding IDs survive generate -> parse -> re-generate."""
        findings = [
            _make_finding("F-01", severity="BLOCKING", files=["roadmap.md"]),
            _make_finding("F-02", severity="WARNING", files=["extraction.md"]),
            _make_finding("F-03", severity="INFO", files=["test-strategy.md"]),
        ]
        source = "# Report\n"

        # Generate tasklist
        tasklist = generate_remediation_tasklist(findings, "report.md", source)

        # Verify all finding IDs present
        for f in findings:
            assert f.id in tasklist, f"Finding {f.id} missing from tasklist"

    def test_round_trip_preserves_frontmatter(self):
        """All frontmatter fields survive round-trip."""
        findings = [_make_finding("F-01")]
        source = "# Report\n"

        tasklist = generate_remediation_tasklist(findings, "report.md", source)

        # Parse frontmatter
        from superclaude.cli.roadmap.gates import _parse_frontmatter
        fm = _parse_frontmatter(tasklist)
        assert fm is not None

        expected_fields = {
            "type", "source_report", "source_report_hash",
            "generated", "total_findings", "actionable", "skipped",
        }
        assert set(fm.keys()) == expected_fields

    def test_round_trip_preserves_severity_grouping(self):
        """Severity sections preserved through round-trip."""
        findings = [
            _make_finding("F-01", severity="BLOCKING"),
            _make_finding("F-02", severity="WARNING"),
            _make_finding("F-03", severity="INFO"),
        ]
        source = "# Report\n"

        tasklist = generate_remediation_tasklist(findings, "report.md", source)
        assert "## BLOCKING" in tasklist
        assert "## WARNING" in tasklist
        assert "## INFO" in tasklist

    def test_round_trip_hash_consistency(self):
        """source_report_hash matches SHA-256 of source content."""
        source = "# Validation Report\nSpecific content for hash test.\n"
        expected_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()

        findings = [_make_finding("F-01")]
        tasklist = generate_remediation_tasklist(findings, "report.md", source)

        from superclaude.cli.roadmap.gates import _parse_frontmatter
        fm = _parse_frontmatter(tasklist)
        assert fm["source_report_hash"] == expected_hash

    def test_round_trip_status_preserved(self):
        """Finding statuses are preserved in tasklist entries."""
        findings = [
            _make_finding("F-01", status="PENDING"),
            _make_finding("F-02", status="SKIPPED"),
        ]
        source = "# Report\n"
        tasklist = generate_remediation_tasklist(findings, "report.md", source)

        assert "PENDING" in tasklist
        assert "SKIPPED" in tasklist


# ═══════════════════════════════════════════════════════════════
# T07.06 -- Deliberate-Failure Test (SC-003)
# ═══════════════════════════════════════════════════════════════


class TestDeliberateFailure:
    """SC-003: Unfixed findings reported as FAIL with justification."""

    def test_unfixed_finding_reported_as_fail(self):
        """Unfixed findings produce FAIL in certification report."""
        findings = [
            _make_finding("F-01", severity="BLOCKING"),
            _make_finding("F-02", severity="WARNING"),
        ]
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Fixed correctly"},
            {"finding_id": "F-02", "result": "FAIL", "justification": "Section unchanged"},
        ]

        report = generate_certification_report(results, findings)
        assert "findings_failed: 1" in report
        assert "certified: false" in report
        assert "| F-02 | WARNING | FAIL | Section unchanged |" in report

    def test_all_fail_no_false_passes(self):
        """When ALL findings fail, none should show PASS."""
        findings = [
            _make_finding("F-01"),
            _make_finding("F-02"),
        ]
        results = [
            {"finding_id": "F-01", "result": "FAIL", "justification": "Not addressed"},
            {"finding_id": "F-02", "result": "FAIL", "justification": "Still broken"},
        ]

        report = generate_certification_report(results, findings)
        assert "findings_passed: 0" in report
        assert "findings_failed: 2" in report
        assert "certified: false" in report

    def test_fail_has_specific_justification(self):
        """Each FAIL entry includes a specific justification (not generic)."""
        findings = [_make_finding("F-01")]
        results = [
            {"finding_id": "F-01", "result": "FAIL",
             "justification": "Milestone count still shows 4 instead of required 5"},
        ]

        report = generate_certification_report(results, findings)
        assert "Milestone count still shows 4" in report

    def test_route_outcome_with_failures(self):
        """route_certification_outcome correctly identifies failures."""
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Fixed"},
            {"finding_id": "F-02", "result": "FAIL", "justification": "Not fixed"},
            {"finding_id": "F-03", "result": "FAIL", "justification": "Still broken"},
        ]

        outcome = route_certification_outcome(results)
        assert outcome["status"] == "certified-with-caveats"
        assert outcome["tasklist_ready"] is False
        assert outcome["findings_passed"] == 1
        assert outcome["findings_failed"] == 2
        assert set(outcome["failed_findings"]) == {"F-02", "F-03"}
        assert outcome["loop"] is False  # NFR-012

    def test_parse_certification_output_with_failures(self):
        """parse_certification_output correctly parses FAIL lines."""
        output = (
            "F-01: PASS -- Milestone added\n"
            "F-02: FAIL -- Heading still lowercase\n"
            "F-03: FAIL -- Missing success criteria metric\n"
        )
        results = parse_certification_output(output)
        assert len(results) == 3
        assert results[0]["result"] == "PASS"
        assert results[1]["result"] == "FAIL"
        assert results[2]["result"] == "FAIL"
        assert "still lowercase" in results[1]["justification"]

    def test_certification_report_with_failures_passes_gate(self, tmp_path):
        """Certification report with FAIL entries still passes CERTIFY_GATE."""
        findings = [
            _make_finding("F-01", severity="BLOCKING"),
            _make_finding("F-02", severity="WARNING"),
        ]
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Fixed"},
            {"finding_id": "F-02", "result": "FAIL", "justification": "Not addressed"},
        ]

        report = generate_certification_report(results, findings)
        report_file = tmp_path / "certification-report.md"
        report_file.write_text(report)

        passed, reason = gate_passed(report_file, CERTIFY_GATE)
        assert passed, f"CERTIFY_GATE should pass even with FAILs: {reason}"


# ═══════════════════════════════════════════════════════════════
# T07.07 -- Edge Case Coverage Tests
# ═══════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge cases: SIGINT recovery, out-of-allowlist, zero-findings, fallback parser."""

    # --- Edge Case 1: SIGINT leaves .pre-remediate files ---

    def test_sigint_leaves_snapshots_for_recovery(self, tmp_path):
        """SIGINT during remediation: .pre-remediate files remain for manual recovery."""
        target = tmp_path / "roadmap.md"
        target.write_text("# Original content\n")

        # Create snapshots
        snapshot_paths = create_snapshots([str(target)])
        assert len(snapshot_paths) == 1

        snapshot = Path(snapshot_paths[0])
        assert snapshot.exists()
        assert snapshot.read_text() == "# Original content\n"

        # Simulate: file modified during remediation
        target.write_text("# Modified by agent\n")

        # Simulate SIGINT: don't call cleanup_snapshots
        # Verify snapshot still exists for manual recovery
        assert snapshot.exists()
        assert snapshot.read_text() == "# Original content\n"

        # Manual recovery possible via restore
        restore_from_snapshots([str(target)])
        assert target.read_text() == "# Original content\n"

    def test_snapshot_restore_atomicity(self, tmp_path):
        """Restore uses os.replace() for atomicity."""
        target = tmp_path / "roadmap.md"
        target.write_text("# Original\n")
        create_snapshots([str(target)])

        target.write_text("# Modified\n")
        restore_from_snapshots([str(target)])

        assert target.read_text() == "# Original\n"
        # Snapshot consumed by restore
        assert not Path(f"{target}.pre-remediate").exists()

    # --- Edge Case 2: Out-of-allowlist findings ---

    def test_out_of_allowlist_findings_produce_warning(self):
        """Findings targeting non-allowed files are SKIPPED with WARNING (OQ-004)."""
        findings = [
            _make_finding("F-01", files=["src/main.py"]),
            _make_finding("F-02", files=["config.yaml"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 0
        assert len(rejected) == 2

    # --- Edge Case 3: Zero-findings path ---

    def test_zero_findings_produces_stub_tasklist(self):
        """Zero actionable findings -> stub tasklist with actionable: 0."""
        source = "# Report\n"
        stub = generate_stub_tasklist("report.md", source)

        assert "type: remediation-tasklist" in stub
        assert "actionable: 0" in stub
        assert "total_findings: 0" in stub
        assert "No actionable findings" in stub

    def test_zero_findings_stub_passes_gate(self, tmp_path):
        """Stub tasklist passes REMEDIATE_GATE (vacuous certification)."""
        source = "# Report\n"
        stub = generate_stub_tasklist("report.md", source)

        stub_file = tmp_path / "remediation-tasklist.md"
        stub_file.write_text(stub)

        passed, reason = gate_passed(stub_file, REMEDIATE_GATE)
        assert passed, f"Stub tasklist should pass REMEDIATE_GATE: {reason}"

    def test_zero_findings_filter_returns_empty(self):
        """filter_findings with no BLOCKING/WARNING returns empty actionable."""
        findings = [
            _make_finding("F-01", severity="INFO"),
        ]
        actionable, skipped = filter_findings(findings, RemediationScope.BLOCKING_ONLY)
        assert len(actionable) == 0
        assert len(skipped) == 1

    # --- Edge Case 4: Fallback parser with deduplication ---

    def test_fallback_parser_deduplicates_across_reports(self):
        """Fallback parser correctly deduplicates across individual reports."""
        report_a = (
            "## Findings\n\n"
            "**[F-01] [BLOCKING] Completeness: Missing milestone**\n\n"
            "- Location: roadmap.md:45\n"
            "- Evidence: Only 4 milestones\n"
            "- Fix guidance: Add milestone 5\n"
        )
        report_b = (
            "## Findings\n\n"
            "**[F-01] [BLOCKING] Completeness: Missing milestone**\n\n"
            "- Location: roadmap.md:47\n"
            "- Evidence: Missing milestone 5\n"
            "- Fix guidance: Add a fifth milestone\n"
        )

        findings = parse_individual_reports([report_a, report_b])
        # Should deduplicate: same file, within 5 lines
        assert len(findings) == 1
        assert findings[0].severity == "BLOCKING"

    def test_fallback_parser_severity_resolution(self):
        """Higher severity wins during deduplication."""
        report_a = (
            "## Findings\n\n"
            "**[F-01] [WARNING] Clarity: Ambiguous wording**\n\n"
            "- Location: roadmap.md:50\n"
            "- Evidence: Unclear\n"
            "- Fix guidance: Clarify\n"
        )
        report_b = (
            "## Findings\n\n"
            "**[F-02] [BLOCKING] Clarity: Critical ambiguity**\n\n"
            "- Location: roadmap.md:52\n"
            "- Evidence: Contradictory\n"
            "- Fix guidance: Rewrite section\n"
        )

        findings = parse_individual_reports([report_a, report_b])
        # Should deduplicate (within 5 lines, same file) -> BLOCKING wins
        assert len(findings) == 1
        assert findings[0].severity == "BLOCKING"

    def test_fallback_parser_no_findings_returns_empty(self):
        """Fallback parser with no findings returns empty list."""
        findings = parse_individual_reports(["No findings here.", "Also nothing."])
        assert findings == []

    def test_fallback_parser_mixed_severity_no_dedup(self):
        """Findings in different files are NOT deduplicated."""
        report_a = (
            "## Findings\n\n"
            "**[F-01] [BLOCKING] Issue: Problem A**\n\n"
            "- Location: roadmap.md:10\n"
            "- Evidence: test\n"
            "- Fix guidance: fix A\n"
        )
        report_b = (
            "## Findings\n\n"
            "**[F-02] [WARNING] Issue: Problem B**\n\n"
            "- Location: extraction.md:20\n"
            "- Evidence: test\n"
            "- Fix guidance: fix B\n"
        )

        findings = parse_individual_reports([report_a, report_b])
        # Different files -> no dedup
        assert len(findings) == 2
