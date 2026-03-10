"""Tests for retrospective parameter wiring (T05.01 / FR-027-FR-029).

Validates:
- build_extract_prompt() accepts retrospective_content
- Retrospective content is framed as advisory "areas to watch"
- Missing retrospective file does not cause errors
- RoadmapConfig supports retrospective_file field
- CLI --retrospective flag is accepted
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.roadmap.models import RoadmapConfig
from superclaude.cli.roadmap.prompts import build_extract_prompt


class TestBuildExtractPromptRetrospective:
    """Tests for retrospective_content parameter on build_extract_prompt."""

    def test_accepts_retrospective_content_none(self):
        """Default None produces a valid prompt without advisory section."""
        prompt = build_extract_prompt(Path("/tmp/spec.md"))
        assert "areas to watch" not in prompt.lower()

    def test_accepts_retrospective_content_explicit_none(self):
        """Explicit None produces the same as default."""
        prompt = build_extract_prompt(
            Path("/tmp/spec.md"), retrospective_content=None
        )
        assert "areas to watch" not in prompt.lower()

    def test_retrospective_content_framed_as_advisory(self):
        """Retrospective text is framed as advisory 'areas to watch'."""
        retro = "Gate strictness caused false positives in v2.19."
        prompt = build_extract_prompt(
            Path("/tmp/spec.md"), retrospective_content=retro
        )
        assert "areas to watch" in prompt.lower()
        assert "advisory" in prompt.lower()
        assert retro in prompt

    def test_retrospective_not_framed_as_requirements(self):
        """Retrospective content must NOT be framed as requirements."""
        retro = "Performance regression in merge step."
        prompt = build_extract_prompt(
            Path("/tmp/spec.md"), retrospective_content=retro
        )
        assert "NOT" in prompt
        assert "not additional requirements" in prompt.lower() or (
            "not" in prompt.lower() and "requirements" in prompt.lower()
        )

    def test_retrospective_empty_string_treated_as_absent(self):
        """Empty string is falsy, so no advisory section is appended."""
        prompt = build_extract_prompt(
            Path("/tmp/spec.md"), retrospective_content=""
        )
        assert "areas to watch" not in prompt.lower()

    def test_prompt_still_valid_with_retrospective(self):
        """Core prompt structure is preserved when retrospective is provided."""
        retro = "Some retrospective content."
        prompt = build_extract_prompt(
            Path("/tmp/spec.md"), retrospective_content=retro
        )
        # Core extraction instructions still present
        assert "requirements extraction specialist" in prompt.lower()
        assert "spec_source" in prompt
        assert "functional_requirements" in prompt
        assert "## Open Questions" in prompt


class TestRoadmapConfigRetrospective:
    """Tests for retrospective_file field on RoadmapConfig."""

    def test_default_retrospective_file_is_none(self):
        config = RoadmapConfig()
        assert config.retrospective_file is None

    def test_set_retrospective_file(self):
        config = RoadmapConfig(retrospective_file=Path("/tmp/retro.md"))
        assert config.retrospective_file == Path("/tmp/retro.md")

    def test_set_retrospective_file_none(self):
        config = RoadmapConfig(retrospective_file=None)
        assert config.retrospective_file is None


class TestRetrospectiveCLIFlag:
    """Tests for --retrospective CLI flag integration."""

    def test_cli_run_help_includes_retrospective(self):
        from click.testing import CliRunner

        from superclaude.cli.roadmap.commands import roadmap_group

        runner = CliRunner()
        result = runner.invoke(roadmap_group, ["run", "--help"])
        assert "--retrospective" in result.output

    def test_cli_missing_retrospective_file_not_error(self, tmp_path):
        """Missing retrospective file should not cause a crash."""
        from click.testing import CliRunner

        from superclaude.cli.roadmap.commands import roadmap_group

        spec = tmp_path / "spec.md"
        spec.write_text("# Test spec\n")
        missing = tmp_path / "nonexistent-retro.md"

        runner = CliRunner()
        result = runner.invoke(
            roadmap_group,
            [
                "run",
                str(spec),
                "--retrospective",
                str(missing),
                "--dry-run",
            ],
        )
        # Should not crash -- either 0 exit or a known dry-run message
        assert result.exit_code == 0 or "dry" in (result.output or "").lower()
