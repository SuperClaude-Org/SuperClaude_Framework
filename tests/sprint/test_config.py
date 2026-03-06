"""Tests for sprint config — phase discovery, validation, and loading."""


import click
import pytest

from superclaude.cli.sprint.config import (
    PHASE_FILE_PATTERN,
    _extract_phase_name,
    discover_phases,
    load_sprint_config,
    parse_tasklist,
    parse_tasklist_file,
    validate_phases,
)
from superclaude.cli.sprint.models import Phase, TaskEntry

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
            ("phase_1_tasklist.md", 1),
            ("phase_4_tasklist.md", 4),
            ("tasklist-p1.md", 1),
            ("tasklist-p2.md", 2),
        ],
    )
    def test_matches_naming_conventions(self, filename, expected_num):
        m = PHASE_FILE_PATTERN.search(filename)
        assert m is not None, f"Pattern did not match: {filename}"
        num = int(next(g for g in m.groups() if g is not None))
        assert num == expected_num

    def test_no_match_irrelevant_files(self):
        assert PHASE_FILE_PATTERN.search("README.md") is None
        assert PHASE_FILE_PATTERN.search("tasklist.md") is None
        assert PHASE_FILE_PATTERN.search("notes.txt") is None

    @pytest.mark.parametrize(
        "filename",
        [
            "phase1-tasklist.md",
            "phase-1_tasklist.md",
            "tasklist-p-1.md",
            "tasklist_phase_1.md",
            "phase-1-tasklist-extra.md",
            "xphase-1-tasklist.md",
        ],
    )
    def test_rejects_near_match_non_canonical_forms(self, filename):
        assert PHASE_FILE_PATTERN.search(filename) is None


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

        buckets = validate_phases(phases, start=1, end=2)
        assert buckets == {"errors": [], "warnings": []}

    def test_missing_file(self, tmp_path):
        phases = [
            Phase(number=1, file=tmp_path / "p1.md"),
        ]
        # Don't create the file

        buckets = validate_phases(phases, start=1, end=1)
        assert len(buckets["errors"]) == 1
        assert "ERROR" in buckets["errors"][0]
        assert "missing" in buckets["errors"][0]
        assert buckets["warnings"] == []

    def test_gap_detection(self, tmp_path):
        phases = [
            Phase(number=1, file=tmp_path / "p1.md"),
            Phase(number=2, file=tmp_path / "p2.md"),
            Phase(number=4, file=tmp_path / "p4.md"),
        ]
        for p in phases:
            p.file.write_text("content")

        buckets = validate_phases(phases, start=1, end=4)
        assert buckets["errors"] == []
        assert len(buckets["warnings"]) == 1
        assert "WARN" in buckets["warnings"][0]
        assert "Gap" in buckets["warnings"][0]
        assert "Phase 2 -> Phase 4" in buckets["warnings"][0]


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


# ---------------------------------------------------------------------------
# Tasklist parser tests
# ---------------------------------------------------------------------------

_SAMPLE_TASKLIST = """\
# Phase 2 -- Per-Task Subprocess Architecture

### T02.01 -- Implement Tasklist Parser in sprint/config.py

| Field | Value |
|---|---|
| Effort | M |

**Deliverables:**
- Tasklist parser (~100 lines) in `src/superclaude/cli/sprint/config.py`

**Dependencies:** None (parser is independent of TurnLedger)

---

### T02.02 -- Implement Per-Task Subprocess Orchestration Loop

| Field | Value |
|---|---|
| Effort | L |

**Deliverables:**
- Per-task subprocess orchestration loop (~200 lines)

**Dependencies:** T01.01 (TurnLedger), T02.01 (TaskInventory parser)

---

### T02.03 -- Implement 4-Layer Subprocess Isolation Setup

| Field | Value |
|---|---|
| Effort | M |

**Deliverables:**
- 4-layer isolation setup (~40 lines)

**Dependencies:** T02.02 (orchestration loop spawns subprocesses)
"""


class TestTasklistParser:
    """Tests for parse_tasklist() and parse_tasklist_file()."""

    def test_extracts_task_ids(self):
        tasks = parse_tasklist(_SAMPLE_TASKLIST)
        assert [t.task_id for t in tasks] == ["T02.01", "T02.02", "T02.03"]

    def test_extracts_titles(self):
        tasks = parse_tasklist(_SAMPLE_TASKLIST)
        assert tasks[0].title == "Implement Tasklist Parser in sprint/config.py"
        assert tasks[1].title == "Implement Per-Task Subprocess Orchestration Loop"
        assert tasks[2].title == "Implement 4-Layer Subprocess Isolation Setup"

    def test_extracts_dependencies_none(self):
        tasks = parse_tasklist(_SAMPLE_TASKLIST)
        assert tasks[0].dependencies == []

    def test_extracts_dependencies_multiple(self):
        tasks = parse_tasklist(_SAMPLE_TASKLIST)
        assert tasks[1].dependencies == ["T01.01", "T02.01"]

    def test_extracts_dependencies_single(self):
        tasks = parse_tasklist(_SAMPLE_TASKLIST)
        assert tasks[2].dependencies == ["T02.02"]

    def test_extracts_description_from_deliverables(self):
        tasks = parse_tasklist(_SAMPLE_TASKLIST)
        assert "Tasklist parser" in tasks[0].description
        assert "config.py" in tasks[0].description

    def test_empty_content_returns_empty(self):
        assert parse_tasklist("") == []

    def test_whitespace_only_returns_empty(self):
        assert parse_tasklist("   \n\n  ") == []

    def test_no_headings_returns_empty(self):
        assert parse_tasklist("# Just a title\n\nSome text without task headings.") == []

    def test_malformed_heading_skipped(self):
        content = "### T02.01 -- Valid Task\n\nContent\n\n### Not a task ID\n\nMore content"
        tasks = parse_tasklist(content)
        assert len(tasks) == 1
        assert tasks[0].task_id == "T02.01"

    def test_em_dash_separator(self):
        content = "### T03.01 — Task With Em Dash\n\nContent"
        tasks = parse_tasklist(content)
        assert len(tasks) == 1
        assert tasks[0].task_id == "T03.01"
        assert tasks[0].title == "Task With Em Dash"

    def test_parse_tasklist_file(self, tmp_path):
        f = tmp_path / "phase-2-tasklist.md"
        f.write_text(_SAMPLE_TASKLIST)
        tasks = parse_tasklist_file(f)
        assert len(tasks) == 3
        assert tasks[0].task_id == "T02.01"

    def test_parse_tasklist_file_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            parse_tasklist_file(tmp_path / "nonexistent.md")
