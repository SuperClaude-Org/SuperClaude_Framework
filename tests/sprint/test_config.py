"""Tests for sprint config — phase discovery, validation, and loading."""


import click
import pytest

from superclaude.cli.sprint.config import (
    PHASE_FILE_PATTERN,
    _extract_phase_name,
    discover_phases,
    load_sprint_config,
    validate_phases,
)
from superclaude.cli.sprint.models import Phase

# ---------------------------------------------------------------------------
# Pattern matching tests
# ---------------------------------------------------------------------------


class TestPhaseFilePattern:
    """Test regex for all 4 naming conventions."""

    @pytest.mark.parametrize(
        "filename,expected_num",
        [
            ("phase-1-tasklist.md", 1),
            ("phase-2-tasklist.md", 2),
            ("p1-tasklist.md", 1),
            ("p3-tasklist.md", 3),
            ("Phase_1_tasklist.md", 1),
            ("Phase_4_tasklist.md", 4),
            ("tasklist-P1.md", 1),
            ("tasklist-p2.md", 2),
            ("phase1-tasklist.md", 1),
        ],
    )
    def test_matches_naming_conventions(self, filename, expected_num):
        m = PHASE_FILE_PATTERN.search(filename)
        assert m is not None, f"Pattern did not match: {filename}"
        num = int(m.group(1) or m.group(2))
        assert num == expected_num

    def test_no_match_irrelevant_files(self):
        assert PHASE_FILE_PATTERN.search("README.md") is None
        assert PHASE_FILE_PATTERN.search("tasklist.md") is None
        assert PHASE_FILE_PATTERN.search("notes.txt") is None


# ---------------------------------------------------------------------------
# Phase discovery tests
# ---------------------------------------------------------------------------


class TestDiscoverPhases:
    """Test phase file discovery strategies."""

    def test_discover_from_index(self, tmp_path):
        # Create index referencing phase files
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1")
        (tmp_path / "phase-2-tasklist.md").write_text("# Phase 2")
        index = tmp_path / "tasklist-index.md"
        index.write_text(
            "Phases:\n"
            "- phase-1-tasklist.md\n"
            "- phase-2-tasklist.md\n"
        )

        phases = discover_phases(index)
        assert len(phases) == 2
        assert phases[0].number == 1
        assert phases[1].number == 2

    def test_discover_from_directory(self, tmp_path):
        # No references in index, discover from directory
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1")
        (tmp_path / "phase-2-tasklist.md").write_text("# Phase 2")
        index = tmp_path / "tasklist-index.md"
        index.write_text("No phase references here\n")

        phases = discover_phases(index)
        assert len(phases) == 2

    def test_discover_sorted(self, tmp_path):
        (tmp_path / "phase-3-tasklist.md").write_text("# Phase 3")
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1")
        index = tmp_path / "tasklist-index.md"
        index.write_text("No refs\n")

        phases = discover_phases(index)
        assert [p.number for p in phases] == [1, 3]

    def test_discover_mixed_naming(self, tmp_path):
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1")
        (tmp_path / "p2-tasklist.md").write_text("# Phase 2")
        index = tmp_path / "tasklist-index.md"
        index.write_text("No refs\n")

        phases = discover_phases(index)
        assert len(phases) == 2

    def test_discover_empty(self, tmp_path):
        index = tmp_path / "tasklist-index.md"
        index.write_text("Empty\n")

        phases = discover_phases(index)
        assert len(phases) == 0


# ---------------------------------------------------------------------------
# Phase name extraction
# ---------------------------------------------------------------------------


class TestExtractPhaseName:
    def test_extracts_heading(self, tmp_path):
        f = tmp_path / "phase-1-tasklist.md"
        f.write_text("# Phase 1 — Foundation\n\nContent here")
        assert _extract_phase_name(f) == "Foundation"

    def test_plain_heading(self, tmp_path):
        f = tmp_path / "phase-1-tasklist.md"
        f.write_text("# Backend Core\n\nContent here")
        assert _extract_phase_name(f) == "Backend Core"

    def test_no_heading(self, tmp_path):
        f = tmp_path / "phase-1-tasklist.md"
        f.write_text("No heading here\n")
        assert _extract_phase_name(f) == ""

    def test_missing_file(self, tmp_path):
        f = tmp_path / "nonexistent.md"
        assert _extract_phase_name(f) == ""


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


class TestValidatePhases:
    def test_valid_phases(self, tmp_path):
        phases = [
            Phase(number=1, file=tmp_path / "p1.md"),
            Phase(number=2, file=tmp_path / "p2.md"),
        ]
        for p in phases:
            p.file.write_text("content")

        msgs = validate_phases(phases, start=1, end=2)
        assert msgs == []

    def test_missing_file(self, tmp_path):
        phases = [
            Phase(number=1, file=tmp_path / "p1.md"),
        ]
        # Don't create the file

        msgs = validate_phases(phases, start=1, end=1)
        assert len(msgs) == 1
        assert "ERROR" in msgs[0]
        assert "missing" in msgs[0]

    def test_gap_detection(self, tmp_path):
        phases = [
            Phase(number=1, file=tmp_path / "p1.md"),
            Phase(number=2, file=tmp_path / "p2.md"),
            Phase(number=4, file=tmp_path / "p4.md"),
        ]
        for p in phases:
            p.file.write_text("content")

        msgs = validate_phases(phases, start=1, end=4)
        assert len(msgs) == 1
        assert "WARN" in msgs[0]
        assert "Gap" in msgs[0]
        assert "Phase 2 -> Phase 4" in msgs[0]


# ---------------------------------------------------------------------------
# load_sprint_config tests
# ---------------------------------------------------------------------------


class TestLoadSprintConfig:
    def test_valid_config(self, tmp_path):
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1: Foundation\n")
        (tmp_path / "phase-2-tasklist.md").write_text("# Phase 2: Backend\n")
        index = tmp_path / "tasklist-index.md"
        index.write_text(
            "Phases:\n- phase-1-tasklist.md\n- phase-2-tasklist.md\n"
        )

        config = load_sprint_config(index_path=index)
        assert len(config.phases) == 2
        assert config.start_phase == 1
        assert config.end_phase == 2
        assert config.max_turns == 50

    def test_missing_index(self, tmp_path):
        with pytest.raises(click.exceptions.ClickException, match="not found"):
            load_sprint_config(index_path=tmp_path / "nonexistent.md")

    def test_no_phases_found(self, tmp_path):
        index = tmp_path / "tasklist-index.md"
        index.write_text("Empty index\n")

        with pytest.raises(click.exceptions.ClickException, match="No phase files"):
            load_sprint_config(index_path=index)

    def test_custom_options(self, tmp_path):
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1\n")
        index = tmp_path / "tasklist-index.md"
        index.write_text("- phase-1-tasklist.md\n")

        config = load_sprint_config(
            index_path=index,
            max_turns=100,
            model="claude-sonnet",
            dry_run=True,
        )
        assert config.max_turns == 100
        assert config.model == "claude-sonnet"
        assert config.dry_run is True
