"""Unit tests for spec_patch.py — the accept-spec-change leaf module.

Covers FR-2.24.1.1 through FR-2.24.1.7, AC-1 through AC-5a, AC-11, AC-14.
"""

from __future__ import annotations

import hashlib
import json
import os
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.roadmap.spec_patch import (
    DeviationRecord,
    _extract_frontmatter,
    prompt_accept_spec_change,
    scan_accepted_deviation_records,
    update_spec_hash,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create an output directory with a valid .roadmap-state.json."""
    spec_file = tmp_path / "spec.md"
    spec_file.write_text("# Test Spec\nSome content.", encoding="utf-8")
    spec_hash = hashlib.sha256(spec_file.read_bytes()).hexdigest()

    state = {
        "schema_version": 1,
        "spec_file": str(spec_file),
        "spec_hash": spec_hash,
        "agents": [{"model": "opus", "persona": "architect"}],
        "depth": "standard",
        "last_run": "2026-03-13T10:00:00+00:00",
        "steps": {
            "spec-fidelity": {
                "status": "FAIL",
                "attempt": 1,
                "output_file": "spec-fidelity.md",
                "started_at": "2026-03-13T10:00:00+00:00",
                "completed_at": "2026-03-13T10:01:00+00:00",
            }
        },
    }
    state_path = tmp_path / ".roadmap-state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    return tmp_path


@pytest.fixture
def deviation_file(output_dir: Path) -> Path:
    """Create a valid accepted deviation file."""
    dev_file = output_dir / "dev-001-accepted-deviation.md"
    dev_file.write_text(
        textwrap.dedent("""\
        ---
        id: DEV-001
        disposition: ACCEPTED
        spec_update_required: true
        affects_spec_sections:
          - "4.1"
          - "4.4"
        acceptance_rationale: debate-consensus
        ---

        ## DEV-001: Architecture layout change

        The spec's Section 4.1 was updated to match the accepted 18-module structure.
        """),
        encoding="utf-8",
    )
    return dev_file


def _modify_spec(output_dir: Path) -> str:
    """Modify the spec file and return the new hash."""
    state = json.loads((output_dir / ".roadmap-state.json").read_text())
    spec_file = Path(state["spec_file"])
    spec_file.write_text("# Modified Spec\nNew content.", encoding="utf-8")
    return hashlib.sha256(spec_file.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# TestLocateStateFile (FR-2.24.1.1)
# ---------------------------------------------------------------------------

class TestLocateStateFile:
    """FR-2.24.1.1: Missing or unreadable state file exits 1."""

    def test_missing_state_file_exits_1(self, tmp_path: Path) -> None:
        result = prompt_accept_spec_change(tmp_path)
        assert result == 1

    def test_malformed_state_file_exits_1(self, tmp_path: Path) -> None:
        (tmp_path / ".roadmap-state.json").write_text("not json", encoding="utf-8")
        result = prompt_accept_spec_change(tmp_path)
        assert result == 1


# ---------------------------------------------------------------------------
# TestRecomputeHash (FR-2.24.1.2)
# ---------------------------------------------------------------------------

class TestRecomputeHash:
    """FR-2.24.1.2: Missing spec file exits 1."""

    def test_missing_spec_file_exits_1(self, output_dir: Path) -> None:
        state = json.loads((output_dir / ".roadmap-state.json").read_text())
        Path(state["spec_file"]).unlink()
        result = prompt_accept_spec_change(output_dir)
        assert result == 1


# ---------------------------------------------------------------------------
# TestHashMismatchCheck (FR-2.24.1.3)
# ---------------------------------------------------------------------------

class TestHashMismatchCheck:
    """FR-2.24.1.3: Hash equality exits 0 (idempotent), AC-3."""

    def test_hash_current_exits_0(self, output_dir: Path) -> None:
        """Spec unchanged → nothing to do."""
        result = prompt_accept_spec_change(output_dir)
        assert result == 0

    def test_missing_spec_hash_treated_as_mismatch(
        self, output_dir: Path, deviation_file: Path
    ) -> None:
        """Null/empty spec_hash → mismatch → proceed to scan."""
        _modify_spec(output_dir)
        state = json.loads((output_dir / ".roadmap-state.json").read_text())
        state["spec_hash"] = None
        (output_dir / ".roadmap-state.json").write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )
        with patch("builtins.input", return_value="y"):
            result = prompt_accept_spec_change(output_dir)
        assert result == 0

    def test_empty_spec_hash_treated_as_mismatch(
        self, output_dir: Path, deviation_file: Path
    ) -> None:
        _modify_spec(output_dir)
        state = json.loads((output_dir / ".roadmap-state.json").read_text())
        state["spec_hash"] = ""
        (output_dir / ".roadmap-state.json").write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )
        with patch("builtins.input", return_value="y"):
            result = prompt_accept_spec_change(output_dir)
        assert result == 0


# ---------------------------------------------------------------------------
# TestScanDeviationRecords (FR-2.24.1.4)
# ---------------------------------------------------------------------------

class TestScanDeviationRecords:
    """FR-2.24.1.4: Glob, parse, filter, zero-records exit; AC-1, AC-14."""

    def test_no_deviation_files_exits_1(self, output_dir: Path) -> None:
        """AC-1: No evidence → exit 1."""
        _modify_spec(output_dir)
        result = prompt_accept_spec_change(output_dir)
        assert result == 1

    def test_accepted_record_found(self, output_dir: Path, deviation_file: Path) -> None:
        records = scan_accepted_deviation_records(output_dir)
        assert len(records) == 1
        assert records[0].id == "DEV-001"
        assert records[0].disposition == "ACCEPTED"
        assert records[0].spec_update_required is True

    def test_non_accepted_record_filtered(self, output_dir: Path) -> None:
        (output_dir / "dev-002-accepted-deviation.md").write_text(
            "---\nid: DEV-002\ndisposition: REJECTED\nspec_update_required: true\n---\n",
            encoding="utf-8",
        )
        records = scan_accepted_deviation_records(output_dir)
        assert len(records) == 0

    def test_spec_update_false_filtered(self, output_dir: Path) -> None:
        (output_dir / "dev-003-accepted-deviation.md").write_text(
            "---\nid: DEV-003\ndisposition: ACCEPTED\nspec_update_required: false\n---\n",
            encoding="utf-8",
        )
        records = scan_accepted_deviation_records(output_dir)
        assert len(records) == 0

    def test_string_true_rejected(self, output_dir: Path) -> None:
        """String "true" (quoted in YAML) is NOT accepted — must be boolean."""
        (output_dir / "dev-004-accepted-deviation.md").write_text(
            '---\nid: DEV-004\ndisposition: ACCEPTED\nspec_update_required: "true"\n---\n',
            encoding="utf-8",
        )
        records = scan_accepted_deviation_records(output_dir)
        assert len(records) == 0

    def test_malformed_yaml_skipped(self, output_dir: Path, deviation_file: Path) -> None:
        """AC-14: Malformed YAML → warning + skip, valid files still processed."""
        (output_dir / "dev-005-accepted-deviation.md").write_text(
            "---\n: invalid yaml {{{\n---\n", encoding="utf-8"
        )
        records = scan_accepted_deviation_records(output_dir)
        # Should still find the valid deviation_file
        assert len(records) == 1
        assert records[0].id == "DEV-001"

    @pytest.mark.parametrize(
        "yaml_value",
        ["yes", "on", "Yes", "YES", "true", "True", "TRUE"],
    )
    def test_yaml_boolean_coercion_accepted(
        self, output_dir: Path, yaml_value: str
    ) -> None:
        """YAML 1.1 boolean forms are intentionally accepted."""
        (output_dir / "dev-006-accepted-deviation.md").write_text(
            f"---\nid: DEV-006\ndisposition: accepted\n"
            f"spec_update_required: {yaml_value}\n---\n",
            encoding="utf-8",
        )
        records = scan_accepted_deviation_records(output_dir)
        assert len(records) == 1

    def test_disposition_case_insensitive(self, output_dir: Path) -> None:
        (output_dir / "dev-007-accepted-deviation.md").write_text(
            "---\nid: DEV-007\ndisposition: accepted\nspec_update_required: true\n---\n",
            encoding="utf-8",
        )
        records = scan_accepted_deviation_records(output_dir)
        assert len(records) == 1
        assert records[0].disposition == "ACCEPTED"


# ---------------------------------------------------------------------------
# TestPromptBehavior (FR-2.24.1.5)
# ---------------------------------------------------------------------------

class TestPromptBehavior:
    """FR-2.24.1.5: Input normalization, non-interactive; AC-4, AC-11."""

    def test_answer_n_aborts(self, output_dir: Path, deviation_file: Path) -> None:
        """AC-4: Answer N → Aborted, no state modification."""
        _modify_spec(output_dir)
        mtime_before = os.path.getmtime(output_dir / ".roadmap-state.json")
        with patch("builtins.input", return_value="n"), \
             patch("superclaude.cli.roadmap.spec_patch.sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = prompt_accept_spec_change(output_dir)
        assert result == 0
        mtime_after = os.path.getmtime(output_dir / ".roadmap-state.json")
        assert mtime_before == mtime_after

    def test_answer_yes_aborts(self, output_dir: Path, deviation_file: Path) -> None:
        """Only single-char y/Y confirms — 'yes' is treated as N."""
        _modify_spec(output_dir)
        with patch("builtins.input", return_value="yes"), \
             patch("superclaude.cli.roadmap.spec_patch.sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = prompt_accept_spec_change(output_dir)
        assert result == 0  # Aborted

    def test_empty_input_aborts(self, output_dir: Path, deviation_file: Path) -> None:
        _modify_spec(output_dir)
        with patch("builtins.input", return_value=""), \
             patch("superclaude.cli.roadmap.spec_patch.sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = prompt_accept_spec_change(output_dir)
        assert result == 0  # Aborted

    def test_non_interactive_aborts(self, output_dir: Path, deviation_file: Path) -> None:
        """AC-11: Non-interactive + auto_accept=False → Aborted."""
        _modify_spec(output_dir)
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            result = prompt_accept_spec_change(output_dir, auto_accept=False)
        assert result == 0

    def test_auto_accept_skips_prompt(self, output_dir: Path, deviation_file: Path) -> None:
        """auto_accept=True → proceeds without prompt."""
        _modify_spec(output_dir)
        result = prompt_accept_spec_change(output_dir, auto_accept=True)
        assert result == 0

    def test_answer_y_lowercase_confirms(self, output_dir: Path, deviation_file: Path) -> None:
        _modify_spec(output_dir)
        with patch("builtins.input", return_value="y"), \
             patch("superclaude.cli.roadmap.spec_patch.sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = prompt_accept_spec_change(output_dir)
        assert result == 0

    def test_answer_Y_uppercase_confirms(self, output_dir: Path, deviation_file: Path) -> None:
        _modify_spec(output_dir)
        with patch("builtins.input", return_value="Y"), \
             patch("superclaude.cli.roadmap.spec_patch.sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = prompt_accept_spec_change(output_dir)
        assert result == 0


# ---------------------------------------------------------------------------
# TestAtomicWrite (FR-2.24.1.6)
# ---------------------------------------------------------------------------

class TestAtomicWrite:
    """FR-2.24.1.6: Only spec_hash changed, all keys preserved; AC-2."""

    def test_only_spec_hash_changes(self, output_dir: Path, deviation_file: Path) -> None:
        """AC-2: All other keys preserved verbatim."""
        state_before = json.loads(
            (output_dir / ".roadmap-state.json").read_text(encoding="utf-8")
        )
        _modify_spec(output_dir)
        # Use auto_accept to bypass tty check in test environment
        prompt_accept_spec_change(output_dir, auto_accept=True)

        state_after = json.loads(
            (output_dir / ".roadmap-state.json").read_text(encoding="utf-8")
        )
        # spec_hash should differ
        assert state_after["spec_hash"] != state_before["spec_hash"]
        # All other keys should be identical
        for key in state_before:
            if key != "spec_hash":
                assert state_after[key] == state_before[key], f"Key {key} changed"

    def test_preexisting_tmp_overwritten(self, output_dir: Path) -> None:
        """Pre-existing .tmp file is overwritten without error."""
        state_path = output_dir / ".roadmap-state.json"
        tmp_path = state_path.with_suffix(".tmp")
        tmp_path.write_text("stale tmp content", encoding="utf-8")

        state = json.loads(state_path.read_text(encoding="utf-8"))
        update_spec_hash(state_path, "newhash123")
        updated = json.loads(state_path.read_text(encoding="utf-8"))
        assert updated["spec_hash"] == "newhash123"
        assert not tmp_path.exists()  # os.replace removes the tmp


# ---------------------------------------------------------------------------
# TestConfirmationOutput (FR-2.24.1.7)
# ---------------------------------------------------------------------------

class TestConfirmationOutput:
    """FR-2.24.1.7: Both hashes truncated to 12 chars."""

    def test_hashes_truncated_in_output(
        self, output_dir: Path, deviation_file: Path, capsys
    ) -> None:
        _modify_spec(output_dir)
        # Use auto_accept to bypass tty check in test environment
        prompt_accept_spec_change(output_dir, auto_accept=True)

        captured = capsys.readouterr()
        # Should contain 12-char hash snippets followed by "..."
        assert "..." in captured.out
        # Check the Old/New lines exist
        assert "Old:" in captured.out
        assert "New:" in captured.out
        assert "Accepted deviations: DEV-001" in captured.out


# ---------------------------------------------------------------------------
# TestIdempotency (AC-3)
# ---------------------------------------------------------------------------

class TestIdempotency:
    """AC-3: Running twice → second exits 0 with 'nothing to do'."""

    def test_second_run_idempotent(
        self, output_dir: Path, deviation_file: Path
    ) -> None:
        _modify_spec(output_dir)
        with patch("builtins.input", return_value="y"):
            result1 = prompt_accept_spec_change(output_dir)
        assert result1 == 0

        # Second run: hash is now current
        result2 = prompt_accept_spec_change(output_dir)
        assert result2 == 0


# ---------------------------------------------------------------------------
# TestExtractFrontmatter
# ---------------------------------------------------------------------------

class TestExtractFrontmatter:
    def test_valid_frontmatter(self) -> None:
        text = "---\nkey: value\n---\nbody"
        assert _extract_frontmatter(text) == "key: value"

    def test_no_frontmatter(self) -> None:
        assert _extract_frontmatter("no frontmatter here") is None

    def test_unclosed_frontmatter(self) -> None:
        assert _extract_frontmatter("---\nkey: value\n") is None

    def test_empty_string(self) -> None:
        assert _extract_frontmatter("") is None


# ---------------------------------------------------------------------------
# TestDeviationRecord dataclass
# ---------------------------------------------------------------------------

class TestDeviationRecord:
    def test_frozen(self, tmp_path: Path) -> None:
        rec = DeviationRecord(
            id="DEV-001",
            disposition="ACCEPTED",
            spec_update_required=True,
            affects_spec_sections=["4.1"],
            acceptance_rationale="test",
            source_file=tmp_path / "test.md",
            mtime=1234567890.0,
        )
        with pytest.raises(AttributeError):
            rec.id = "DEV-002"  # type: ignore[misc]
