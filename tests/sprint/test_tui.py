"""Tests for sprint TUI — snapshot tests for all display states."""

from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

from rich.console import Console

from superclaude.cli.sprint.models import (
    MonitorState,
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
    SprintResult,
)
from superclaude.cli.sprint.tui import STATUS_ICONS, STATUS_STYLES, SprintTUI


def _make_config():
    return SprintConfig(
        index_path=Path("/tmp/tasklist-index.md"),
        release_dir=Path("/tmp/release"),
        phases=[
            Phase(number=1, file=Path("/tmp/p1.md"), name="Foundation"),
            Phase(number=2, file=Path("/tmp/p2.md"), name="Backend"),
            Phase(number=3, file=Path("/tmp/p3.md"), name="Frontend"),
        ],
    )


def _render_to_string(tui: SprintTUI) -> str:
    """Render TUI to string for testing."""
    output = StringIO()
    console = Console(file=output, width=80, force_terminal=True)
    panel = tui._render()
    console.print(panel)
    return output.getvalue()


class TestStatusMappings:
    """Verify STATUS_STYLES and STATUS_ICONS cover all statuses."""

    def test_all_statuses_have_styles(self):
        for status in PhaseStatus:
            assert status in STATUS_STYLES, f"Missing style for {status}"

    def test_all_statuses_have_icons(self):
        for status in PhaseStatus:
            assert status in STATUS_ICONS, f"Missing icon for {status}"


class TestSprintTUI:
    """Test TUI rendering states."""

    def test_initial_render(self):
        config = _make_config()
        tui = SprintTUI(config, console=Console(file=StringIO(), width=80))
        output = _render_to_string(tui)
        assert "SUPERCLAUDE SPRINT RUNNER" in output

    def test_render_with_running_phase(self):
        config = _make_config()
        tui = SprintTUI(config, console=Console(file=StringIO(), width=80))

        now = datetime.now(timezone.utc)
        sr = SprintResult(config=config, started_at=now - timedelta(seconds=60))
        ms = MonitorState(last_task_id="T01.02", last_tool_used="Edit")

        tui.update(sr, ms, config.phases[0])
        output = _render_to_string(tui)
        assert "Foundation" in output
        assert "ACTIVE" in output

    def test_render_phase_table(self):
        config = _make_config()
        tui = SprintTUI(config, console=Console(file=StringIO(), width=80))

        now = datetime.now(timezone.utc)
        sr = SprintResult(
            config=config,
            phase_results=[
                PhaseResult(
                    phase=config.phases[0],
                    status=PhaseStatus.PASS,
                    exit_code=0,
                    started_at=now - timedelta(seconds=120),
                    finished_at=now,
                ),
            ],
        )
        tui.update(sr, MonitorState(), None)
        output = _render_to_string(tui)
        assert "PASS" in output
        assert "Foundation" in output

    def test_render_stall_thinking(self):
        config = _make_config()
        tui = SprintTUI(config, console=Console(file=StringIO(), width=80))

        sr = SprintResult(config=config)
        ms = MonitorState(stall_seconds=35.0)

        tui.update(sr, ms, config.phases[0])
        output = _render_to_string(tui)
        assert "thinking" in output

    def test_render_stall_stalled(self):
        config = _make_config()
        tui = SprintTUI(config, console=Console(file=StringIO(), width=80))

        sr = SprintResult(config=config)
        ms = MonitorState(stall_seconds=65.0)

        tui.update(sr, ms, config.phases[0])
        output = _render_to_string(tui)
        assert "STALLED" in output

    def test_render_complete_state(self):
        config = _make_config()
        tui = SprintTUI(config, console=Console(file=StringIO(), width=80))

        now = datetime.now(timezone.utc)
        sr = SprintResult(
            config=config,
            outcome=SprintOutcome.SUCCESS,
            started_at=now - timedelta(seconds=300),
            finished_at=now,
            phase_results=[
                PhaseResult(
                    phase=p,
                    status=PhaseStatus.PASS,
                    exit_code=0,
                    started_at=now - timedelta(seconds=100),
                    finished_at=now,
                )
                for p in config.phases
            ],
        )
        tui.update(sr, MonitorState(), None)
        output = _render_to_string(tui)
        assert "ALL PHASES PASSED" in output

    def test_render_halted_state(self):
        config = _make_config()
        tui = SprintTUI(config, console=Console(file=StringIO(), width=80))

        now = datetime.now(timezone.utc)
        sr = SprintResult(
            config=config,
            outcome=SprintOutcome.HALTED,
            halt_phase=2,
            started_at=now - timedelta(seconds=200),
            finished_at=now,
            phase_results=[
                PhaseResult(
                    phase=config.phases[0],
                    status=PhaseStatus.PASS,
                    exit_code=0,
                    started_at=now - timedelta(seconds=200),
                    finished_at=now - timedelta(seconds=100),
                ),
                PhaseResult(
                    phase=config.phases[1],
                    status=PhaseStatus.HALT,
                    exit_code=1,
                    started_at=now - timedelta(seconds=100),
                    finished_at=now,
                ),
            ],
        )
        tui.update(sr, MonitorState(), None)
        output = _render_to_string(tui)
        assert "HALTED" in output
        assert "Resume" in output

    def test_start_stop_lifecycle(self):
        config = _make_config()
        console = Console(file=StringIO(), width=80)
        tui = SprintTUI(config, console=console)

        live = tui.start()
        assert live is not None
        tui.stop()
        # Should not raise
