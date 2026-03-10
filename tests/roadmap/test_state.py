"""Tests for .roadmap-state.json management (T04.04)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from superclaude.cli.roadmap.executor import read_state, write_state


class TestWriteState:
    def test_atomic_write_creates_file(self, tmp_path):
        state = {"schema_version": 1, "spec_hash": "abc123"}
        target = tmp_path / ".roadmap-state.json"
        write_state(state, target)

        assert target.exists()
        data = json.loads(target.read_text())
        assert data["schema_version"] == 1
        assert data["spec_hash"] == "abc123"

    def test_atomic_write_no_tmp_left(self, tmp_path):
        state = {"schema_version": 1}
        target = tmp_path / ".roadmap-state.json"
        write_state(state, target)

        tmp = target.with_suffix(".tmp")
        assert not tmp.exists()

    def test_atomic_write_overwrites_existing(self, tmp_path):
        target = tmp_path / ".roadmap-state.json"
        target.write_text('{"schema_version": 0}')

        write_state({"schema_version": 2}, target)
        data = json.loads(target.read_text())
        assert data["schema_version"] == 2

    def test_atomic_write_creates_parent_dirs(self, tmp_path):
        target = tmp_path / "nested" / "dir" / ".roadmap-state.json"
        write_state({"ok": True}, target)
        assert target.exists()


class TestReadState:
    def test_read_valid_state(self, tmp_path):
        target = tmp_path / ".roadmap-state.json"
        state = {
            "schema_version": 1,
            "spec_hash": "sha256:abc",
            "agents": [{"model": "opus", "persona": "architect"}],
            "depth": "standard",
            "steps": {
                "extract": {"status": "PASS", "attempt": 1},
            },
        }
        target.write_text(json.dumps(state))

        result = read_state(target)
        assert result is not None
        assert result["schema_version"] == 1
        assert result["spec_hash"] == "sha256:abc"
        assert len(result["agents"]) == 1

    def test_read_missing_file(self, tmp_path):
        result = read_state(tmp_path / "nonexistent.json")
        assert result is None

    def test_read_empty_file(self, tmp_path):
        target = tmp_path / ".roadmap-state.json"
        target.write_text("")
        result = read_state(target)
        assert result is None

    def test_read_malformed_json(self, tmp_path):
        target = tmp_path / ".roadmap-state.json"
        target.write_text("{bad json!!! not valid")
        result = read_state(target)
        assert result is None

    def test_read_whitespace_only(self, tmp_path):
        target = tmp_path / ".roadmap-state.json"
        target.write_text("   \n  \n  ")
        result = read_state(target)
        assert result is None


class TestStateSchema:
    def test_schema_includes_required_fields(self, tmp_path):
        """Verify state written by _save_state includes all required fields."""
        from datetime import datetime, timezone
        from superclaude.cli.pipeline.models import Step, StepResult, StepStatus, GateCriteria
        from superclaude.cli.roadmap.executor import _save_state
        from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig

        spec = tmp_path / "spec.md"
        spec.write_text("# Test Spec\nContent here.\n")
        output = tmp_path / "output"
        output.mkdir()

        config = RoadmapConfig(
            spec_file=spec,
            output_dir=output,
            agents=[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")],
            depth="deep",
        )

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

        _save_state(config, results)

        state_file = output / ".roadmap-state.json"
        assert state_file.exists()
        data = json.loads(state_file.read_text())

        # Required top-level fields
        assert data["schema_version"] == 1
        assert "spec_hash" in data
        assert len(data["spec_hash"]) == 64  # SHA-256 hex
        assert isinstance(data["agents"], list)
        assert data["agents"][0]["model"] == "opus"
        assert data["depth"] == "deep"

        # Per-step fields
        step_data = data["steps"]["extract"]
        assert step_data["status"] == "PASS"
        assert step_data["attempt"] == 1
        assert "started_at" in step_data
        assert "completed_at" in step_data
        # ISO-8601 timestamps should be parseable
        datetime.fromisoformat(step_data["started_at"])
        datetime.fromisoformat(step_data["completed_at"])
