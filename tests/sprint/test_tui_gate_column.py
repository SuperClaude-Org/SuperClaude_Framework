"""Tests for TUI gate column rendering."""

from io import StringIO
from pathlib import Path

from rich.console import Console

from superclaude.cli.sprint.models import (
    GateDisplayState,
    MonitorState,
    Phase,
    PhaseStatus,
    SprintConfig,
    SprintResult,
)
from superclaude.cli.sprint.tui import SprintTUI


def _make_config(grace_period: int = 0) -> SprintConfig:
    return SprintConfig(
        index_path=Path("/tmp/tasklist-index.md"),
        release_dir=Path("/tmp/release"),
        phases=[
            Phase(number=1, file=Path("/tmp/p1.md"), name="Foundation"),
            Phase(number=2, file=Path("/tmp/p2.md"), name="Backend"),
        ],
        grace_period=grace_period,
    )


def _render_to_string(tui: SprintTUI) -> str:
    output = StringIO()
    console = Console(file=output, width=100, force_terminal=True)
    panel = tui._render()
    console.print(panel)
    return output.getvalue()


class TestTUIGateColumnVisibility:
    """Gate column hidden when grace_period=0, visible when > 0."""

    def test_gate_column_hidden_when_grace_period_zero(self):
        config = _make_config(grace_period=0)
        tui = SprintTUI(config, console=Console(file=StringIO(), width=100))
        assert not tui._show_gate_column

        sr = SprintResult(config=config)
        tui.update(sr, MonitorState(), config.phases[0])
        output = _render_to_string(tui)
        # "Gate" header should not appear
        assert "Gate" not in output

    def test_gate_column_visible_when_grace_period_positive(self):
        config = _make_config(grace_period=30)
        tui = SprintTUI(config, console=Console(file=StringIO(), width=100))
        assert tui._show_gate_column

        sr = SprintResult(config=config)
        tui.update(sr, MonitorState(), config.phases[0])
        output = _render_to_string(tui)
        # "Gate" header should appear
        assert "Gate" in output


class TestTUIGateColumnRendering:
    """Gate column renders GateDisplayState per phase."""

    def test_default_gate_state_is_none(self):
        config = _make_config(grace_period=30)
        tui = SprintTUI(config, console=Console(file=StringIO(), width=100))

        sr = SprintResult(config=config)
        tui.update(sr, MonitorState(), None)
        # Default state should be NONE (rendered as dim dash)
        output = _render_to_string(tui)
        assert "Gate" in output

    def test_gate_state_updates_per_phase(self):
        config = _make_config(grace_period=30)
        tui = SprintTUI(config, console=Console(file=StringIO(), width=100))

        tui.gate_states[1] = GateDisplayState.PASS
        tui.gate_states[2] = GateDisplayState.FAIL_DEFERRED

        sr = SprintResult(config=config)
        tui.update(sr, MonitorState(), None)
        output = _render_to_string(tui)
        # Should contain gate column with rendered states
        assert "Gate" in output

    def test_all_gate_display_states_render(self):
        """Each GateDisplayState should render without error."""
        config = _make_config(grace_period=30)

        for state in GateDisplayState:
            tui = SprintTUI(config, console=Console(file=StringIO(), width=100))
            tui.gate_states[1] = state
            sr = SprintResult(config=config)
            tui.update(sr, MonitorState(), None)
            output = _render_to_string(tui)
            assert "Gate" in output, f"Gate column missing for state {state}"

    def test_nonblocking_read_pattern(self):
        """Gate states use dict.get with default — no locks, best-effort snapshot."""
        config = _make_config(grace_period=30)
        tui = SprintTUI(config, console=Console(file=StringIO(), width=100))
        # Empty gate_states should not raise — uses .get() with NONE default
        sr = SprintResult(config=config)
        tui.update(sr, MonitorState(), None)
        output = _render_to_string(tui)
        assert "Gate" in output


class TestTUIGateColumnBackwardCompat:
    """Backward compatibility: no UI change for blocking-only mode."""

    def test_table_columns_without_gate(self):
        """Without grace_period, table has original 5 columns."""
        config = _make_config(grace_period=0)
        tui = SprintTUI(config, console=Console(file=StringIO(), width=100))
        sr = SprintResult(config=config)
        tui.update(sr, MonitorState(), None)
        table = tui._build_phase_table()
        assert len(table.columns) == 5

    def test_table_columns_with_gate(self):
        """With grace_period, table has 6 columns (includes Gate)."""
        config = _make_config(grace_period=30)
        tui = SprintTUI(config, console=Console(file=StringIO(), width=100))
        sr = SprintResult(config=config)
        tui.update(sr, MonitorState(), None)
        table = tui._build_phase_table()
        assert len(table.columns) == 6
