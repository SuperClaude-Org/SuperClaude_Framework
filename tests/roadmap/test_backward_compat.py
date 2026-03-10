"""Tests for backward compatibility with old state files (T06.05).

Validates SC-008: additive schema extension. Old .roadmap-state.json files
without remediate/certify fields must not crash. Existing consumers
(fidelity_status, steps.validate) must still work with new schema.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import GateCriteria, Step, StepResult, StepStatus
from superclaude.cli.roadmap.executor import (
    _save_state,
    build_certify_metadata,
    build_remediate_metadata,
    derive_pipeline_status,
    read_state,
    write_state,
)
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


def _make_config(tmp_path: Path) -> tuple[RoadmapConfig, Path]:
    spec = tmp_path / "spec.md"
    spec.write_text("# Test Spec\nContent.\n")
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    config = RoadmapConfig(
        spec_file=spec,
        output_dir=output,
        agents=[AgentSpec("opus", "architect")],
        depth="standard",
    )
    return config, output


def _old_state_v1() -> dict:
    """Create an old-format state file with only steps 1-9 (no remediate/certify)."""
    return {
        "schema_version": 1,
        "spec_file": "spec.md",
        "spec_hash": "a" * 64,
        "agents": [{"model": "opus", "persona": "architect"}],
        "depth": "standard",
        "last_run": "2026-03-01T00:00:00+00:00",
        "steps": {
            "extract": {
                "status": "PASS",
                "attempt": 1,
                "output_file": "output/extraction.md",
                "started_at": "2026-03-01T00:00:00+00:00",
                "completed_at": "2026-03-01T00:01:00+00:00",
            },
            "generate-opus-architect": {
                "status": "PASS",
                "attempt": 1,
                "output_file": "output/roadmap-opus-architect.md",
                "started_at": "2026-03-01T00:01:00+00:00",
                "completed_at": "2026-03-01T00:05:00+00:00",
            },
            "spec-fidelity": {
                "status": "PASS",
                "attempt": 1,
                "output_file": "output/spec-fidelity.md",
                "started_at": "2026-03-01T00:10:00+00:00",
                "completed_at": "2026-03-01T00:12:00+00:00",
            },
        },
        "fidelity_status": "pass",
        "validation": {
            "status": "fail",
            "timestamp": "2026-03-01T00:15:00+00:00",
        },
    }


# ═══════════════════════════════════════════════════════════════
# SC-008: Old state files load without exceptions
# ═══════════════════════════════════════════════════════════════


class TestOldStateFileLoad:
    """Old state files without remediate/certify fields load without exceptions."""

    def test_load_old_state_no_crash(self, tmp_path):
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps(_old_state_v1()))

        result = read_state(state_file)
        assert result is not None
        assert result["schema_version"] == 1

    def test_missing_remediate_field_defaults_to_none(self, tmp_path):
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps(_old_state_v1()))

        result = read_state(state_file)
        assert result.get("remediate") is None  # Missing = step not run

    def test_missing_certify_field_defaults_to_none(self, tmp_path):
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps(_old_state_v1()))

        result = read_state(state_file)
        assert result.get("certify") is None  # Missing = step not run

    def test_derive_pipeline_status_from_old_state(self, tmp_path):
        """Pipeline status derivation works with old state (no remediate/certify)."""
        old_state = _old_state_v1()
        # Old state has validation.status = "fail" -> validated-with-issues
        assert derive_pipeline_status(old_state) == "validated-with-issues"

    def test_old_state_without_validation_returns_pending(self):
        state = {
            "schema_version": 1,
            "steps": {"extract": {"status": "PASS"}},
        }
        assert derive_pipeline_status(state) == "pending"


# ═══════════════════════════════════════════════════════════════
# SC-008: Resume with old state file
# ═══════════════════════════════════════════════════════════════


class TestOldStateResume:
    """Old state file + --resume starts from earliest incomplete step."""

    def test_resume_with_old_state_starts_from_validate(self, tmp_path):
        """Old state without remediate/certify -> pipeline status is
        validated-with-issues, so remediate/certify should run."""
        old_state = _old_state_v1()
        status = derive_pipeline_status(old_state)
        assert status == "validated-with-issues"
        # This means remediate and certify both need to run


# ═══════════════════════════════════════════════════════════════
# SC-008: Existing consumers unaffected
# ═══════════════════════════════════════════════════════════════


class TestExistingConsumersUnaffected:
    """Existing consumers (fidelity_status, steps.validate) still work."""

    def test_fidelity_status_preserved(self, tmp_path):
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps(_old_state_v1()))

        result = read_state(state_file)
        assert result["fidelity_status"] == "pass"

    def test_validation_status_preserved(self, tmp_path):
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps(_old_state_v1()))

        result = read_state(state_file)
        assert result["validation"]["status"] == "fail"

    def test_steps_extract_accessible(self, tmp_path):
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps(_old_state_v1()))

        result = read_state(state_file)
        assert result["steps"]["extract"]["status"] == "PASS"

    def test_spec_fidelity_step_accessible(self, tmp_path):
        state_file = tmp_path / ".roadmap-state.json"
        state_file.write_text(json.dumps(_old_state_v1()))

        result = read_state(state_file)
        assert result["steps"]["spec-fidelity"]["status"] == "PASS"


# ═══════════════════════════════════════════════════════════════
# SC-008: Schema extension is additive-only
# ═══════════════════════════════════════════════════════════════


class TestAdditiveSchemaExtension:
    """New fields are additive-only: adding remediate/certify doesn't break old fields."""

    def test_save_state_preserves_old_fields(self, tmp_path):
        """_save_state() preserves existing remediate/certify across rewrites."""
        config, output = _make_config(tmp_path)

        # Write initial state with remediate metadata
        old_state = _old_state_v1()
        old_state["remediate"] = build_remediate_metadata(
            status="PASS",
            scope="all",
            findings_total=5,
            findings_actionable=3,
            findings_fixed=3,
            findings_failed=0,
            findings_skipped=2,
            agents_spawned=2,
            tasklist_file="output/remediation-tasklist.md",
        )
        write_state(old_state, output / ".roadmap-state.json")

        # Now call _save_state with new results (no remediate_metadata)
        now = datetime.now(timezone.utc)
        results = [
            StepResult(
                step=Step(
                    id="extract",
                    prompt="test",
                    output_file=output / "extraction.md",
                    gate=None,
                    timeout_seconds=300,
                ),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now,
            ),
        ]

        _save_state(config, results)  # No remediate_metadata passed

        # Verify remediate was preserved
        reloaded = read_state(output / ".roadmap-state.json")
        assert reloaded is not None
        assert "remediate" in reloaded
        assert reloaded["remediate"]["status"] == "PASS"
        assert reloaded["remediate"]["findings_fixed"] == 3

    def test_save_state_with_new_remediate_metadata(self, tmp_path):
        """_save_state() correctly writes new remediate metadata."""
        config, output = _make_config(tmp_path)

        now = datetime.now(timezone.utc)
        results = [
            StepResult(
                step=Step(
                    id="extract",
                    prompt="test",
                    output_file=output / "extraction.md",
                    gate=None,
                    timeout_seconds=300,
                ),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now,
            ),
        ]

        remediate_meta = build_remediate_metadata(
            status="PASS",
            scope="blocking_only",
            findings_total=3,
            findings_actionable=2,
            findings_fixed=2,
            findings_failed=0,
            findings_skipped=1,
            agents_spawned=1,
            tasklist_file="output/remediation-tasklist.md",
        )

        _save_state(config, results, remediate_metadata=remediate_meta)

        reloaded = read_state(output / ".roadmap-state.json")
        assert reloaded["remediate"]["status"] == "PASS"
        assert reloaded["remediate"]["scope"] == "blocking_only"
        assert reloaded["remediate"]["findings_total"] == 3
        assert reloaded["remediate"]["findings_fixed"] == 2
        assert "timestamp" in reloaded["remediate"]

    def test_save_state_with_certify_metadata(self, tmp_path):
        """_save_state() correctly writes certify metadata."""
        config, output = _make_config(tmp_path)

        now = datetime.now(timezone.utc)
        results = [
            StepResult(
                step=Step(
                    id="extract",
                    prompt="test",
                    output_file=output / "extraction.md",
                    gate=None,
                    timeout_seconds=300,
                ),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now,
            ),
        ]

        certify_meta = build_certify_metadata(
            status="certified",
            findings_verified=3,
            findings_passed=3,
            findings_failed=0,
            certified=True,
            report_file="output/certification-report.md",
        )

        _save_state(config, results, certify_metadata=certify_meta)

        reloaded = read_state(output / ".roadmap-state.json")
        assert reloaded["certify"]["status"] == "certified"
        assert reloaded["certify"]["certified"] is True
        assert reloaded["certify"]["findings_verified"] == 3
        assert "timestamp" in reloaded["certify"]

    def test_old_fields_not_removed_by_new_save(self, tmp_path):
        """Schema extension doesn't remove old top-level fields."""
        config, output = _make_config(tmp_path)

        # Set up old state with validation and fidelity
        old_state = _old_state_v1()
        write_state(old_state, output / ".roadmap-state.json")

        now = datetime.now(timezone.utc)
        results = [
            StepResult(
                step=Step(
                    id="extract",
                    prompt="test",
                    output_file=output / "extraction.md",
                    gate=None,
                    timeout_seconds=300,
                ),
                status=StepStatus.PASS,
                attempt=1,
                started_at=now,
                finished_at=now,
            ),
        ]

        _save_state(config, results, remediate_metadata={"status": "PASS"})

        reloaded = read_state(output / ".roadmap-state.json")
        # Old fields still present
        assert reloaded["validation"]["status"] == "fail"
        # New field added
        assert reloaded["remediate"]["status"] == "PASS"


# ═══════════════════════════════════════════════════════════════
# Metadata builder tests
# ═══════════════════════════════════════════════════════════════


class TestMetadataBuilders:
    """Tests for build_remediate_metadata and build_certify_metadata."""

    def test_remediate_metadata_has_all_fields(self):
        meta = build_remediate_metadata(
            status="PASS",
            scope="all",
            findings_total=10,
            findings_actionable=5,
            findings_fixed=4,
            findings_failed=1,
            findings_skipped=5,
            agents_spawned=3,
            tasklist_file="out/tasklist.md",
        )
        assert meta["status"] == "PASS"
        assert meta["scope"] == "all"
        assert meta["findings_total"] == 10
        assert meta["findings_actionable"] == 5
        assert meta["findings_fixed"] == 4
        assert meta["findings_failed"] == 1
        assert meta["findings_skipped"] == 5
        assert meta["agents_spawned"] == 3
        assert meta["tasklist_file"] == "out/tasklist.md"
        assert "timestamp" in meta

    def test_certify_metadata_has_all_fields(self):
        meta = build_certify_metadata(
            status="certified",
            findings_verified=5,
            findings_passed=4,
            findings_failed=1,
            certified=False,
            report_file="out/cert.md",
        )
        assert meta["status"] == "certified"
        assert meta["findings_verified"] == 5
        assert meta["findings_passed"] == 4
        assert meta["findings_failed"] == 1
        assert meta["certified"] is False
        assert meta["report_file"] == "out/cert.md"
        assert "timestamp" in meta

    def test_timestamps_are_iso_format(self):
        meta = build_remediate_metadata(
            status="PASS", scope="all",
            findings_total=0, findings_actionable=0,
            findings_fixed=0, findings_failed=0,
            findings_skipped=0, agents_spawned=0,
            tasklist_file="t.md",
        )
        # Should parse without error
        datetime.fromisoformat(meta["timestamp"])
