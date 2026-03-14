"""Unit tests for contract emission.

Covers all 4 exit states: success, partial, failed, dry_run.
Verifies NFR-009: no None/empty fields on failure paths.
"""

from __future__ import annotations

import json

import pytest

from superclaude.cli.cli_portify.contract import (
    ContractStatus,
    PhaseStatus,
    PortifyContract,
    StepTiming,
    build_dry_run_contract,
    build_failed_contract,
    build_partial_contract,
    build_success_contract,
    generate_resume_command,
    RESUMABLE_STEPS,
)
from superclaude.cli.cli_portify.models import PortifyStepResult, PortifyStatus


class TestSuccessContract:
    def test_status_is_success(self):
        c = build_success_contract(
            artifacts=["spec.md"],
            step_timings=[StepTiming("validate-config", 0.5)],
            gate_results={"validate-config": "pass"},
            total_duration=10.0,
        )
        assert c.status == ContractStatus.SUCCESS

    def test_all_phases_completed(self):
        c = build_success_contract(
            artifacts=[], step_timings=[], gate_results={}, total_duration=1.0,
        )
        d = c.to_dict()
        for phase in d["phases"]:
            assert phase["status"] == "completed"
            assert phase["steps_completed"] == phase["steps_total"]

    def test_no_resume_command(self):
        c = build_success_contract(
            artifacts=[], step_timings=[], gate_results={}, total_duration=1.0,
        )
        assert c.resume_command == ""

    def test_artifacts_preserved(self):
        c = build_success_contract(
            artifacts=["a.md", "b.md"],
            step_timings=[], gate_results={}, total_duration=1.0,
        )
        assert c.artifacts == ["a.md", "b.md"]


class TestPartialContract:
    def test_status_is_partial(self):
        c = build_partial_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=5.0, resume_step="panel-review",
        )
        assert c.status == ContractStatus.PARTIAL

    def test_resume_command_generated(self):
        c = build_partial_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=5.0, resume_step="panel-review",
        )
        assert "panel-review" in c.resume_command
        assert "--start" in c.resume_command


class TestFailedContract:
    def test_status_is_failed(self):
        c = build_failed_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=2.0,
            error_message="gate failure", resume_step="synthesize-spec",
        )
        assert c.status == ContractStatus.FAILED

    def test_error_message_preserved(self):
        c = build_failed_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=2.0,
            error_message="SC-005 sentinel check failed",
        )
        assert c.error_message == "SC-005 sentinel check failed"

    def test_nfr009_no_none_fields(self):
        """NFR-009: All failure paths must produce populated contracts."""
        c = build_failed_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=2.0,
        )
        d = c.to_dict()
        # No field should be None
        assert d["status"] is not None
        assert d["phases"] is not None and len(d["phases"]) > 0
        assert d["artifacts"] is not None
        assert d["timing"] is not None
        assert d["step_timings"] is not None
        assert d["gate_results"] is not None

    def test_phases_populated_on_failure(self):
        """NFR-009: Phase statuses populated with last-known state."""
        c = build_failed_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=2.0,
        )
        assert len(c.phases) == 4  # All 4 phases populated

    def test_resume_command_for_resumable_step(self):
        c = build_failed_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=2.0,
            resume_step="synthesize-spec",
        )
        assert "synthesize-spec" in c.resume_command

    def test_no_resume_for_non_resumable_step(self):
        c = build_failed_contract(
            step_results=[], artifacts=[], step_timings=[],
            gate_results={}, total_duration=2.0,
            resume_step="validate-config",  # Not resumable
        )
        assert c.resume_command == ""


class TestDryRunContract:
    def test_status_is_dry_run(self):
        c = build_dry_run_contract(
            step_results=[], artifacts=["inv.md"],
            step_timings=[], total_duration=1.0,
        )
        assert c.status == ContractStatus.DRY_RUN

    def test_phases_3_4_skipped(self):
        """Per D-0003: dry_run marks phases 3-4 as skipped."""
        c = build_dry_run_contract(
            step_results=[], artifacts=[],
            step_timings=[], total_duration=1.0,
        )
        d = c.to_dict()
        # Phase indices 2 and 3 (0-indexed) = conceptual phases 3-4
        assert d["phases"][2]["status"] == "skipped"
        assert d["phases"][3]["status"] == "skipped"

    def test_phases_1_2_completed(self):
        c = build_dry_run_contract(
            step_results=[], artifacts=[],
            step_timings=[], total_duration=1.0,
        )
        d = c.to_dict()
        assert d["phases"][0]["status"] == "completed"
        assert d["phases"][1]["status"] == "completed"


class TestResumeCommandGeneration:
    def test_resumable_steps(self):
        for step in RESUMABLE_STEPS:
            cmd = generate_resume_command(step)
            assert cmd != "", f"Step {step} should be resumable"
            assert f"--start {step}" in cmd

    def test_non_resumable_step(self):
        cmd = generate_resume_command("validate-config")
        assert cmd == ""

    def test_suggested_budget(self):
        cmd = generate_resume_command("panel-review", suggested_budget=2)
        assert "--max-convergence 2" in cmd


class TestContractSerialization:
    def test_json_round_trip(self):
        c = build_success_contract(
            artifacts=["x.md"], step_timings=[StepTiming("s1", 1.5)],
            gate_results={"s1": "pass"}, total_duration=5.0,
        )
        j = c.to_json()
        parsed = json.loads(j)
        assert parsed["status"] == "success"
        assert parsed["artifacts"] == ["x.md"]

    def test_default_contract_is_failed(self):
        """Default PortifyContract should be in failed state per NFR-009."""
        c = PortifyContract()
        assert c.status == ContractStatus.FAILED
        assert len(c.phases) == 4
