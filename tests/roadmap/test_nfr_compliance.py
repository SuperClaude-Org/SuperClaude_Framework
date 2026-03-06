"""NFR compliance tests -- architectural constraint enforcement via code analysis.

NFR-003: gate_passed is pure Python, no subprocess import in pipeline/gates.py
NFR-004: prompts.py has no file I/O or subprocess calls
NFR-005: roadmap/gates.py contains only data definitions (GateCriteria instances)
NFR-006: pipeline/models.py has no sprint-specific fields
NFR-007: no file under pipeline/ imports from sprint/ or roadmap/
"""

from __future__ import annotations

from pathlib import Path

import pytest


_SRC_ROOT = Path(__file__).resolve().parent.parent.parent / "src" / "superclaude" / "cli"


class TestNFR003PureGates:
    """NFR-003: pipeline/gates.py contains zero subprocess imports."""

    def test_no_subprocess_in_pipeline_gates(self):
        gates_path = _SRC_ROOT / "pipeline" / "gates.py"
        content = gates_path.read_text(encoding="utf-8")
        assert "import subprocess" not in content
        assert "from subprocess" not in content

    def test_gate_passed_is_pure_python(self):
        """gate_passed uses only Path + str operations, no shell/exec calls."""
        gates_path = _SRC_ROOT / "pipeline" / "gates.py"
        content = gates_path.read_text(encoding="utf-8")
        assert "os.system" not in content
        assert "os.popen" not in content
        assert "exec(" not in content
        assert "eval(" not in content


class TestNFR004PurePrompts:
    """NFR-004: roadmap/prompts.py has no file I/O or subprocess calls."""

    def test_no_open_calls(self):
        prompts_path = _SRC_ROOT / "roadmap" / "prompts.py"
        content = prompts_path.read_text(encoding="utf-8")
        # Should not have open() for file I/O
        assert "open(" not in content

    def test_no_subprocess(self):
        prompts_path = _SRC_ROOT / "roadmap" / "prompts.py"
        content = prompts_path.read_text(encoding="utf-8")
        assert "import subprocess" not in content
        assert "from subprocess" not in content

    def test_no_os_path(self):
        prompts_path = _SRC_ROOT / "roadmap" / "prompts.py"
        content = prompts_path.read_text(encoding="utf-8")
        assert "import os.path" not in content
        assert "from os.path" not in content
        assert "import os" not in content

    def test_no_io_operations(self):
        prompts_path = _SRC_ROOT / "roadmap" / "prompts.py"
        content = prompts_path.read_text(encoding="utf-8")
        assert ".read_text(" not in content
        assert ".write_text(" not in content
        assert ".read_bytes(" not in content


class TestNFR005GateDataSeparation:
    """NFR-005: roadmap/gates.py contains only GateCriteria data, no enforcement logic."""

    def test_no_gate_passed_import(self):
        gates_data_path = _SRC_ROOT / "roadmap" / "gates.py"
        content = gates_data_path.read_text(encoding="utf-8")
        # Should not import gate_passed from pipeline
        assert "from ..pipeline.gates import" not in content
        assert "from superclaude.cli.pipeline.gates import" not in content

    def test_imports_only_models(self):
        gates_data_path = _SRC_ROOT / "roadmap" / "gates.py"
        content = gates_data_path.read_text(encoding="utf-8")
        # Should only import data types from pipeline.models
        assert "from ..pipeline.models import" in content
        # Should not import executor or process
        assert "from ..pipeline.executor" not in content
        assert "from ..pipeline.process" not in content

    def test_defines_gate_criteria_instances(self):
        """Verify module-level GateCriteria constants exist."""
        from superclaude.cli.roadmap.gates import (
            EXTRACT_GATE,
            GENERATE_A_GATE,
            GENERATE_B_GATE,
            DIFF_GATE,
            DEBATE_GATE,
            SCORE_GATE,
            MERGE_GATE,
            TEST_STRATEGY_GATE,
        )
        from superclaude.cli.pipeline.models import GateCriteria

        for gate in [EXTRACT_GATE, GENERATE_A_GATE, GENERATE_B_GATE,
                     DIFF_GATE, DEBATE_GATE, SCORE_GATE, MERGE_GATE, TEST_STRATEGY_GATE]:
            assert isinstance(gate, GateCriteria)


class TestNFR006NoSprintFieldsInPipeline:
    """NFR-006: pipeline/models.py contains zero sprint-specific fields."""

    def test_no_index_path_field(self):
        models_path = _SRC_ROOT / "pipeline" / "models.py"
        content = models_path.read_text(encoding="utf-8")
        assert "index_path" not in content

    def test_no_phases_field(self):
        models_path = _SRC_ROOT / "pipeline" / "models.py"
        content = models_path.read_text(encoding="utf-8")
        # Check that "phases" doesn't appear as a field name
        # (it may appear in comments/docstrings, so check for field definition)
        lines = content.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("phases:") or stripped.startswith("phases ="):
                pytest.fail(f"Sprint-specific field 'phases' found: {stripped}")

    def test_no_stall_timeout_field(self):
        models_path = _SRC_ROOT / "pipeline" / "models.py"
        content = models_path.read_text(encoding="utf-8")
        assert "stall_timeout" not in content


class TestNFR007NoCrossModuleImports:
    """NFR-007: no file under pipeline/ imports from sprint/ or roadmap/."""

    def _get_import_lines(self, path: Path) -> list[str]:
        """Extract actual import statements (not docstrings/comments)."""
        content = path.read_text(encoding="utf-8")
        lines = []
        in_docstring = False
        for line in content.splitlines():
            stripped = line.strip()
            # Skip docstring blocks
            if '"""' in stripped:
                if stripped.count('"""') == 1:
                    in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            # Skip comments
            if stripped.startswith("#"):
                continue
            if stripped.startswith(("import ", "from ")):
                lines.append(stripped)
        return lines

    def test_no_sprint_imports_in_pipeline(self):
        pipeline_dir = _SRC_ROOT / "pipeline"
        for py_file in pipeline_dir.glob("*.py"):
            import_lines = self._get_import_lines(py_file)
            for line in import_lines:
                assert "sprint" not in line, \
                    f"{py_file.name} imports from sprint/: {line}"

    def test_no_roadmap_imports_in_pipeline(self):
        pipeline_dir = _SRC_ROOT / "pipeline"
        for py_file in pipeline_dir.glob("*.py"):
            import_lines = self._get_import_lines(py_file)
            for line in import_lines:
                assert "roadmap" not in line, \
                    f"{py_file.name} imports from roadmap/: {line}"

    def test_pipeline_init_has_no_cross_module_imports(self):
        init_path = _SRC_ROOT / "pipeline" / "__init__.py"
        import_lines = self._get_import_lines(init_path)
        for line in import_lines:
            assert "sprint" not in line, f"__init__.py imports sprint: {line}"
            assert "roadmap" not in line, f"__init__.py imports roadmap: {line}"
