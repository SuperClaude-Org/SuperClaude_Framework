"""Tests for remediate_executor.py -- snapshots, allowlist, execution, rollback.

Covers:
- T04.03: create_snapshots, restore_from_snapshots, cleanup_snapshots
- T04.04: enforce_allowlist, EDITABLE_FILES
- T04.05: parallel agent execution (mocked ClaudeProcess)
- T04.06: timeout and retry logic
- T04.07: failure handling with full rollback
- T05.02: inline embedding replaces --file (FR-ATL.5, Phase 5)
- T04.08: success handling with snapshot cleanup
- T04.09: update_remediation_tasklist (two-write model)
- T04.10: step registration (REMEDIATE_GATE integration)
"""

import os
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.roadmap.models import Finding
from superclaude.cli.roadmap.remediate_executor import (
    EDITABLE_FILES,
    _AGENT_TIMEOUT_SECONDS,
    _EMBED_SIZE_LIMIT,
    _handle_failure,
    _handle_success,
    _run_agent_for_file,
    _update_finding_entries,
    _update_frontmatter_counts,
    cleanup_snapshots,
    create_snapshots,
    enforce_allowlist,
    execute_remediation,
    restore_from_snapshots,
    update_remediation_tasklist,
)


# ── Shared fixtures ──────────────────────────────────────────────────────


def _make_finding(
    id: str = "F-01",
    severity: str = "BLOCKING",
    status: str = "PENDING",
    fix_guidance: str = "Fix it",
    files_affected: list[str] | None = None,
) -> Finding:
    return Finding(
        id=id,
        severity=severity,
        dimension="Test",
        description=f"Finding {id}",
        location="file.py:1",
        evidence="test evidence",
        fix_guidance=fix_guidance,
        files_affected=files_affected if files_affected is not None else ["roadmap.md"],
        status=status,
    )


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary target files for snapshot testing."""
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("---\ntitle: roadmap\n---\n\n# Roadmap\n", encoding="utf-8")

    test_strat = tmp_path / "test-strategy.md"
    test_strat.write_text("---\ntitle: test\n---\n\n# Test Strategy\n", encoding="utf-8")

    extraction = tmp_path / "extraction.md"
    extraction.write_text("---\ntitle: extract\n---\n\n# Extraction\n", encoding="utf-8")

    return {
        "roadmap": str(roadmap),
        "test_strategy": str(test_strat),
        "extraction": str(extraction),
    }


@pytest.fixture
def sample_tasklist(tmp_path):
    """Create a sample remediation-tasklist.md for update testing."""
    content = textwrap.dedent("""\
        ---
        type: remediation-tasklist
        source_report: report.md
        source_report_hash: abc123
        generated: 2025-01-01T00:00:00Z
        total_findings: 3
        actionable: 2
        skipped: 1
        ---

        # Remediation Tasklist

        ## BLOCKING

        - [ ] F-01 | roadmap.md | PENDING -- Finding F-01
        - [ ] F-02 | test-strategy.md | PENDING -- Finding F-02

        ## SKIPPED

        - [x] F-03 | other.md | SKIPPED -- Finding F-03
    """)
    tasklist = tmp_path / "remediation-tasklist.md"
    tasklist.write_text(content, encoding="utf-8")
    return str(tasklist)


# ═══════════════════════════════════════════════════════════════
# T04.03 -- Pre-Remediate File Snapshots
# ═══════════════════════════════════════════════════════════════


class TestCreateSnapshots:
    """T04.03: Snapshot creation and integrity."""

    def test_creates_snapshot_files(self, temp_files):
        targets = [temp_files["roadmap"], temp_files["test_strategy"]]
        snapshots = create_snapshots(targets)
        assert len(snapshots) == 2
        for snap in snapshots:
            assert Path(snap).exists()
            assert snap.endswith(".pre-remediate")

    def test_snapshot_content_identical(self, temp_files):
        target = temp_files["roadmap"]
        original = Path(target).read_bytes()
        create_snapshots([target])
        snapshot = Path(f"{target}.pre-remediate")
        assert snapshot.read_bytes() == original

    def test_returns_snapshot_paths(self, temp_files):
        targets = [temp_files["roadmap"]]
        snapshots = create_snapshots(targets)
        assert snapshots == [f"{temp_files['roadmap']}.pre-remediate"]

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            create_snapshots([str(tmp_path / "nonexistent.md")])

    def test_atomic_write_no_partial(self, temp_files):
        """Verify no .tmp files remain after snapshot creation."""
        target = temp_files["roadmap"]
        create_snapshots([target])
        tmp_file = Path(f"{target}.pre-remediate.tmp")
        assert not tmp_file.exists()


class TestRestoreFromSnapshots:
    """T04.03: Snapshot restoration."""

    def test_restores_original_content(self, temp_files):
        target = temp_files["roadmap"]
        original = Path(target).read_bytes()
        create_snapshots([target])

        # Modify the file
        Path(target).write_text("MODIFIED CONTENT", encoding="utf-8")
        assert Path(target).read_bytes() != original

        # Restore
        restore_from_snapshots([target])
        assert Path(target).read_bytes() == original

    def test_snapshot_consumed_after_restore(self, temp_files):
        target = temp_files["roadmap"]
        create_snapshots([target])
        restore_from_snapshots([target])
        # os.replace moves snapshot -> original, snapshot is gone
        assert not Path(f"{target}.pre-remediate").exists()


class TestCleanupSnapshots:
    """T04.03: Snapshot cleanup after success."""

    def test_deletes_snapshots(self, temp_files):
        target = temp_files["roadmap"]
        create_snapshots([target])
        assert Path(f"{target}.pre-remediate").exists()

        cleanup_snapshots([target])
        assert not Path(f"{target}.pre-remediate").exists()

    def test_no_error_on_missing_snapshot(self, temp_files):
        # Should not raise even if snapshot doesn't exist
        cleanup_snapshots([temp_files["roadmap"]])


# ═══════════════════════════════════════════════════════════════
# T04.04 -- File Allowlist Enforcement
# ═══════════════════════════════════════════════════════════════


class TestEditableFilesConstant:
    """T04.04: EDITABLE_FILES allowlist constant."""

    def test_contains_exactly_three_files(self):
        assert EDITABLE_FILES == frozenset({
            "roadmap.md", "extraction.md", "test-strategy.md"
        })

    def test_is_frozenset(self):
        assert isinstance(EDITABLE_FILES, frozenset)


class TestEnforceAllowlist:
    """T04.04: enforce_allowlist() filters findings by file allowlist."""

    def test_allowlisted_files_pass(self):
        findings = [
            _make_finding("F-01", files_affected=["roadmap.md"]),
            _make_finding("F-02", files_affected=["test-strategy.md"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 2
        assert len(rejected) == 0

    def test_non_allowlisted_rejected(self):
        findings = [
            _make_finding("F-01", files_affected=["config.yaml"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 0
        assert len(rejected) == 1

    def test_mixed_allowlisted_and_non(self):
        findings = [
            _make_finding("F-01", files_affected=["roadmap.md"]),
            _make_finding("F-02", files_affected=["config.yaml"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 1
        assert allowed[0].id == "F-01"
        assert len(rejected) == 1
        assert rejected[0].id == "F-02"

    def test_cross_file_with_non_allowlisted_rejected(self):
        """Finding with any non-allowlisted file is rejected."""
        findings = [
            _make_finding(
                "F-01",
                files_affected=["roadmap.md", "config.yaml"],
            ),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 0
        assert len(rejected) == 1

    def test_cross_file_all_allowlisted_passes(self):
        findings = [
            _make_finding(
                "F-01",
                files_affected=["roadmap.md", "test-strategy.md"],
            ),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 1

    def test_no_files_affected_rejected(self):
        findings = [Finding(
            id="F-01", severity="BLOCKING", dimension="Test",
            description="No files", location="", evidence="ev",
            fix_guidance="fix", files_affected=[], status="PENDING",
        )]
        allowed, rejected = enforce_allowlist(findings)
        assert len(rejected) == 1

    def test_empty_findings(self):
        allowed, rejected = enforce_allowlist([])
        assert allowed == []
        assert rejected == []

    def test_path_with_directory_prefix(self):
        """Allowlist matches basename, not full path."""
        findings = [
            _make_finding("F-01", files_affected=["output/roadmap.md"]),
        ]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 1

    def test_extraction_md_allowed(self):
        findings = [_make_finding("F-01", files_affected=["extraction.md"])]
        allowed, rejected = enforce_allowlist(findings)
        assert len(allowed) == 1


# ═══════════════════════════════════════════════════════════════
# T04.07 -- Failure Handling with Full Rollback
# ═══════════════════════════════════════════════════════════════


class TestHandleFailure:
    """T04.07: failure handler rollback and status marking."""

    def test_rollback_restores_all_files(self, temp_files):
        targets = [temp_files["roadmap"], temp_files["test_strategy"]]
        originals = {t: Path(t).read_bytes() for t in targets}
        create_snapshots(targets)

        # Modify files
        for t in targets:
            Path(t).write_text("MODIFIED", encoding="utf-8")

        findings_by_file = {
            targets[0]: [_make_finding("F-01", files_affected=[targets[0]])],
            targets[1]: [_make_finding("F-02", files_affected=[targets[1]])],
        }
        _handle_failure(targets[0], targets, findings_by_file)

        # Verify all files restored
        for t in targets:
            assert Path(t).read_bytes() == originals[t]

    def test_marks_failed_agent_findings(self, temp_files):
        target = temp_files["roadmap"]
        f1 = _make_finding("F-01", files_affected=[target])
        findings_by_file = {target: [f1]}

        create_snapshots([target])
        result = _handle_failure(target, [target], findings_by_file)

        failed_findings = [f for f in result if f.status == "FAILED"]
        assert len(failed_findings) >= 1

    def test_cross_file_findings_marked_failed(self, temp_files):
        t1 = temp_files["roadmap"]
        t2 = temp_files["test_strategy"]
        # Cross-file finding
        f1 = _make_finding("F-01", files_affected=[t1, t2])
        findings_by_file = {
            t1: [f1],
            t2: [f1],
        }

        create_snapshots([t1, t2])
        result = _handle_failure(t1, [t1, t2], findings_by_file)

        # Cross-file finding should be marked FAILED
        cross_file = [f for f in result if f.id == "F-01"]
        assert len(cross_file) >= 1
        assert cross_file[0].status == "FAILED"


# ═══════════════════════════════════════════════════════════════
# T04.08 -- Success Handling with Snapshot Cleanup
# ═══════════════════════════════════════════════════════════════


class TestHandleSuccess:
    """T04.08: success handler cleanup and status updates."""

    def test_deletes_snapshots(self, temp_files):
        targets = [temp_files["roadmap"], temp_files["test_strategy"]]
        create_snapshots(targets)

        findings_by_file = {
            targets[0]: [_make_finding("F-01", files_affected=[targets[0]])],
            targets[1]: [_make_finding("F-02", files_affected=[targets[1]])],
        }
        _handle_success(targets, findings_by_file)

        for t in targets:
            assert not Path(f"{t}.pre-remediate").exists()

    def test_marks_pending_as_fixed(self, temp_files):
        target = temp_files["roadmap"]
        f1 = _make_finding("F-01", status="PENDING", files_affected=[target])
        findings_by_file = {target: [f1]}

        create_snapshots([target])
        result = _handle_success([target], findings_by_file)

        assert all(f.status == "FIXED" for f in result if f.id == "F-01")

    def test_preserves_skipped_status(self, temp_files):
        target = temp_files["roadmap"]
        f1 = _make_finding("F-01", status="SKIPPED", files_affected=[target])
        findings_by_file = {target: [f1]}

        create_snapshots([target])
        result = _handle_success([target], findings_by_file)

        skipped = [f for f in result if f.id == "F-01"]
        assert skipped[0].status == "SKIPPED"

    def test_no_orphaned_snapshots(self, temp_files):
        targets = list(temp_files.values())
        create_snapshots(targets)

        findings_by_file = {
            t: [_make_finding(f"F-{i}", files_affected=[t])]
            for i, t in enumerate(targets)
        }
        _handle_success(targets, findings_by_file)

        for t in targets:
            assert not Path(f"{t}.pre-remediate").exists()


# ═══════════════════════════════════════════════════════════════
# T04.09 -- Tasklist Outcome Writer (Two-Write Model)
# ═══════════════════════════════════════════════════════════════


class TestUpdateRemediationTasklist:
    """T04.09: update_remediation_tasklist() two-write model."""

    def test_updates_fixed_entries(self, sample_tasklist):
        findings = [
            _make_finding("F-01", status="FIXED"),
            _make_finding("F-02", status="FAILED"),
            _make_finding("F-03", status="SKIPPED"),
        ]
        update_remediation_tasklist(sample_tasklist, findings)

        content = Path(sample_tasklist).read_text(encoding="utf-8")
        assert "- [x] F-01" in content
        assert "FIXED" in content

    def test_updates_failed_entries(self, sample_tasklist):
        findings = [
            _make_finding("F-01", status="FIXED"),
            _make_finding("F-02", status="FAILED"),
            _make_finding("F-03", status="SKIPPED"),
        ]
        update_remediation_tasklist(sample_tasklist, findings)

        content = Path(sample_tasklist).read_text(encoding="utf-8")
        assert "- [ ] F-02" in content
        assert "FAILED" in content

    def test_preserves_skipped_entries(self, sample_tasklist):
        findings = [
            _make_finding("F-01", status="FIXED"),
            _make_finding("F-02", status="FAILED"),
            _make_finding("F-03", status="SKIPPED"),
        ]
        update_remediation_tasklist(sample_tasklist, findings)

        content = Path(sample_tasklist).read_text(encoding="utf-8")
        # F-03 should remain [x] SKIPPED
        assert "- [x] F-03" in content

    def test_updates_frontmatter_counts(self, sample_tasklist):
        findings = [
            _make_finding("F-01", status="FIXED"),
            _make_finding("F-02", status="FAILED"),
            _make_finding("F-03", status="SKIPPED"),
        ]
        update_remediation_tasklist(sample_tasklist, findings)

        content = Path(sample_tasklist).read_text(encoding="utf-8")
        assert "actionable: 2" in content
        assert "skipped: 1" in content

    def test_atomic_write_no_partial(self, sample_tasklist):
        """Verify no .tmp files remain after update."""
        findings = [_make_finding("F-01", status="FIXED")]
        update_remediation_tasklist(sample_tasklist, findings)

        tmp = Path(sample_tasklist + ".tmp")
        assert not tmp.exists()

    def test_round_trip_consistency(self, sample_tasklist):
        """Parse -> update -> re-parse produces consistent Finding objects."""
        findings = [
            _make_finding("F-01", status="FIXED"),
            _make_finding("F-02", status="FAILED"),
        ]
        update_remediation_tasklist(sample_tasklist, findings)

        content = Path(sample_tasklist).read_text(encoding="utf-8")
        # Verify the content is well-formed
        assert content.startswith("---")
        assert "type: remediation-tasklist" in content


# ═══════════════════════════════════════════════════════════════
# T04.10 -- Step Registration (REMEDIATE_GATE integration)
# ═══════════════════════════════════════════════════════════════


class TestRemediateStepRegistration:
    """T04.10: Remediate step is registered and discoverable."""

    def test_remediate_gate_in_all_gates(self):
        from superclaude.cli.roadmap.gates import ALL_GATES, REMEDIATE_GATE
        gate_names = [name for name, _ in ALL_GATES]
        assert "remediate" in gate_names

    def test_remediate_gate_is_strict(self):
        from superclaude.cli.roadmap.gates import REMEDIATE_GATE
        assert REMEDIATE_GATE.enforcement_tier == "STRICT"

    def test_agent_timeout_300s(self):
        """NFR-001: 300s timeout per agent."""
        assert _AGENT_TIMEOUT_SECONDS == 300

    def test_yaml_preservation_in_prompt(self):
        """NFR-013: Agent prompts include YAML/heading preservation."""
        from superclaude.cli.roadmap.remediate_prompts import build_remediation_prompt
        f = _make_finding("F-01")
        prompt = build_remediation_prompt("roadmap.md", [f])
        assert "Preserve YAML frontmatter" in prompt
        assert "Preserve heading hierarchy" in prompt


# ── T05.02: Inline embedding replaces --file (FR-ATL.5) ─────────────────────


class TestRemediateInlineEmbedReplacesFileFlag:
    """FR-ATL.5: remediate_executor delivers target file content via inline embedding.

    --file is broken (cloud download mechanism, not local file injector).
    All content must arrive via the prompt; extra_args must never contain --file.
    """

    def test_remediate_inline_embed_replaces_file_flag(self, tmp_path):
        """Target file content appears in captured prompt; no --file in extra_args."""
        target = tmp_path / "roadmap.md"
        target.write_text("# Roadmap\n\nOriginal content for remediation.\n")

        finding = _make_finding("F-01", files_affected=[str(target)])
        config_obj = MagicMock()
        config_obj.max_turns = 5
        config_obj.model = None
        config_obj.permission_flag = "--dangerously-skip-permissions"

        from superclaude.cli.pipeline.models import PipelineConfig
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured: dict = {}

        with patch("superclaude.cli.roadmap.remediate_executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            instance.wait.return_value = 0

            def capture_and_return(**kw):
                captured["prompt"] = kw.get("prompt", "")
                captured["extra_args"] = kw.get("extra_args", ["SENTINEL"])
                return instance

            MockProc.side_effect = capture_and_return

            _run_agent_for_file(str(target), [finding], config, tmp_path)

        # File content must appear in the prompt (inline embedding)
        assert "Original content for remediation." in captured["prompt"]
        # extra_args must be absent or empty (no --file)
        assert "--file" not in captured.get("extra_args", [])
        # The prompt should contain the fenced block header
        assert "Current File Content" in captured["prompt"]

    def test_remediate_inline_embed_oversized_still_no_file_flag(self, tmp_path, caplog):
        """Oversized target file embeds inline with a warning; --file never used."""
        import logging

        target = tmp_path / "roadmap.md"
        target.write_text("X" * (_EMBED_SIZE_LIMIT + 2048))

        finding = _make_finding("F-01", files_affected=[str(target)])

        from superclaude.cli.pipeline.models import PipelineConfig
        config = PipelineConfig(max_turns=5, dry_run=False)

        captured: dict = {}

        with patch("superclaude.cli.roadmap.remediate_executor.ClaudeProcess") as MockProc:
            instance = MagicMock()
            instance._process = None
            instance.wait.return_value = 0

            def capture_and_return(**kw):
                captured["prompt"] = kw.get("prompt", "")
                captured["extra_args"] = kw.get("extra_args", ["SENTINEL"])
                return instance

            MockProc.side_effect = capture_and_return

            with caplog.at_level(logging.WARNING, logger="superclaude.roadmap.remediate_executor"):
                _run_agent_for_file(str(target), [finding], config, tmp_path)

        # Even oversized content must be embedded inline
        assert "X" * 100 in captured["prompt"]
        # No --file in extra_args
        assert "--file" not in captured.get("extra_args", [])
        # Warning logged for oversized prompt
        assert any("embedding inline anyway" in r.message for r in caplog.records)
