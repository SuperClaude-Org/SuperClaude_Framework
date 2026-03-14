"""Tests for deterministic gate checks (Steps 1-2).

Covers:
- Gate functions return tuple[bool, str] per NFR-004
- Timing advisory enforcement (<1s for Step 1, <5s for Step 2)
- Frontmatter structure validation for inventory output
- Integration with pipeline.gates.gate_passed()
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.cli_portify.steps.gates import (
    DISCOVER_COMPONENTS_GATE,
    VALIDATE_CONFIG_GATE,
    gate_discover_components,
    gate_validate_config,
)
from superclaude.cli.cli_portify.steps.validate_config import ValidateConfigResult
from superclaude.cli.pipeline.gates import gate_passed


class TestGateValidateConfig:
    """EXEMPT gate for validate-config (Step 1)."""

    def test_returns_tuple_bool_str(self):
        result = ValidateConfigResult(valid=True, duration_seconds=0.01)
        passed, msg = gate_validate_config(result)
        assert isinstance(passed, bool)
        assert isinstance(msg, str)

    def test_passes_on_valid_result(self):
        result = ValidateConfigResult(valid=True, duration_seconds=0.05)
        passed, msg = gate_validate_config(result)
        assert passed is True

    def test_fails_on_timing_violation(self):
        result = ValidateConfigResult(valid=True, duration_seconds=2.5)
        passed, msg = gate_validate_config(result)
        assert passed is False
        assert "Timing advisory" in msg

    def test_fails_on_inconsistency_valid_with_errors(self):
        result = ValidateConfigResult(
            valid=True,
            errors=[{"code": "ERR", "message": "something"}],
            duration_seconds=0.01,
        )
        passed, msg = gate_validate_config(result)
        assert passed is False
        assert "Inconsistency" in msg

    def test_fails_on_inconsistency_invalid_no_errors(self):
        result = ValidateConfigResult(valid=False, duration_seconds=0.01)
        passed, msg = gate_validate_config(result)
        assert passed is False
        assert "Inconsistency" in msg

    def test_invalid_with_errors_passes_gate(self):
        result = ValidateConfigResult(
            valid=False,
            errors=[{"code": "ERR_INVALID_PATH", "message": "not found"}],
            duration_seconds=0.01,
        )
        passed, msg = gate_validate_config(result)
        assert passed is True


class TestGateDiscoverComponents:
    """STANDARD gate for discover-components (Step 2)."""

    def _write_inventory(self, path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_returns_tuple_bool_str(self, tmp_path):
        artifact = self._write_inventory(
            tmp_path / "component-inventory.md",
            "---\nsource_skill: test\ncomponent_count: 1\ntotal_lines: 10\nduration_seconds: 0.01\n---\n\n# Inventory\n\nContent here.\n",
        )
        passed, msg = gate_discover_components(artifact)
        assert isinstance(passed, bool)
        assert isinstance(msg, str)

    def test_passes_on_valid_inventory(self, tmp_path):
        artifact = self._write_inventory(
            tmp_path / "component-inventory.md",
            "---\nsource_skill: test-skill\ncomponent_count: 3\ntotal_lines: 50\nduration_seconds: 0.05\n---\n\n# Inventory\n\nContent.\n",
        )
        passed, msg = gate_discover_components(artifact)
        assert passed is True

    def test_fails_on_missing_file(self, tmp_path):
        passed, msg = gate_discover_components(tmp_path / "nonexistent.md")
        assert passed is False
        assert "not found" in msg

    def test_fails_on_missing_frontmatter(self, tmp_path):
        artifact = self._write_inventory(
            tmp_path / "component-inventory.md",
            "# Inventory\n\nNo frontmatter here.\n\nMore content.\nEven more.\n",
        )
        passed, msg = gate_discover_components(artifact)
        assert passed is False
        assert "frontmatter" in msg.lower()

    def test_fails_on_missing_source_skill(self, tmp_path):
        artifact = self._write_inventory(
            tmp_path / "component-inventory.md",
            "---\ncomponent_count: 1\ntotal_lines: 5\n---\n\n# Inv\n\nContent.\n",
        )
        passed, msg = gate_discover_components(artifact)
        assert passed is False
        assert "source_skill" in msg

    def test_fails_on_missing_component_count(self, tmp_path):
        artifact = self._write_inventory(
            tmp_path / "component-inventory.md",
            "---\nsource_skill: test\ntotal_lines: 5\n---\n\n# Inv\n\nContent.\n",
        )
        passed, msg = gate_discover_components(artifact)
        assert passed is False
        assert "component_count" in msg

    def test_fails_on_timing_violation(self, tmp_path):
        artifact = self._write_inventory(
            tmp_path / "component-inventory.md",
            "---\nsource_skill: test\ncomponent_count: 1\ntotal_lines: 10\nduration_seconds: 0.01\n---\n\n# Inv\n\nContent.\n",
        )
        # Pass actual_duration that exceeds limit
        passed, msg = gate_discover_components(artifact, actual_duration=10.0)
        assert passed is False
        assert "Timing advisory" in msg


class TestGateIntegrationWithPipelineGates:
    """Gates integrate with pipeline.gates.gate_passed()."""

    def test_validate_config_exempt_gate_always_passes(self, tmp_path):
        """EXEMPT tier gates always pass via pipeline.gates.gate_passed()."""
        # Create a dummy output file (EXEMPT tier doesn't check content)
        output_file = tmp_path / "validate-config-result.json"
        output_file.write_text("{}")
        passed, reason = gate_passed(output_file, VALIDATE_CONFIG_GATE)
        assert passed is True
        assert reason is None

    def test_discover_components_standard_gate(self, tmp_path):
        """STANDARD tier gate checks frontmatter via pipeline.gates.gate_passed()."""
        output_file = tmp_path / "component-inventory.md"
        output_file.write_text(
            "---\nsource_skill: test\ncomponent_count: 2\ntotal_lines: 20\n---\n\n# Inventory\n\nContent.\n"
        )
        passed, reason = gate_passed(output_file, DISCOVER_COMPONENTS_GATE)
        assert passed is True

    def test_discover_components_standard_gate_fails_no_frontmatter(self, tmp_path):
        """STANDARD tier gate fails when frontmatter missing."""
        output_file = tmp_path / "component-inventory.md"
        output_file.write_text("# Inventory\n\nNo frontmatter.\n\n\n\n")
        passed, reason = gate_passed(output_file, DISCOVER_COMPONENTS_GATE)
        assert passed is False
        assert reason is not None
