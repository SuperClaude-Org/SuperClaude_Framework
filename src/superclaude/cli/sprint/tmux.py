"""Tmux integration — session management for detachable sprint execution."""

from __future__ import annotations

import hashlib
import os
import shlex
import shutil
import subprocess
import time
from pathlib import Path

import click

from .models import SprintConfig


def is_tmux_available() -> bool:
    """Check if tmux is installed and we are not already inside tmux."""
    if shutil.which("tmux") is None:
        return False
    # If TMUX env var is set, we are already inside a tmux session.
    return "TMUX" not in os.environ


def session_name(release_dir: Path) -> str:
    """Deterministic session name from release directory."""
    h = hashlib.sha1(str(release_dir.resolve()).encode()).hexdigest()[:8]
    return f"sc-sprint-{h}"


def find_running_session() -> str | None:
    """Find any running sc-sprint-* session."""
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.strip().splitlines():
        if line.startswith("sc-sprint-"):
            return line
    return None


def launch_in_tmux(config: SprintConfig):
    """Create a tmux session and run the sprint inside it.

    The session is cleaned up on any setup failure to prevent stale sessions
    from blocking future sprint runs on the same release directory.
    """
    name = session_name(config.release_dir)
    config.tmux_session_name = name

    # Build the command that runs the sprint in foreground (--no-tmux)
    sprint_cmd = _build_foreground_command(config)

    # Create the session with the sprint as the main command
    subprocess.run(
        [
            "tmux",
            "new-session",
            "-d",  # detached
            "-s",
            name,  # session name
            "-x",
            "120",
            "-y",
            "40",  # default size
            *sprint_cmd,
        ],
        check=True,
    )

    # All post-creation setup — clean up session on any failure
    try:
        # Split: bottom pane tails the output of the first active phase
        if config.active_phases:
            output_file = config.output_file(config.active_phases[0])
            quoted = shlex.quote(str(output_file))
            subprocess.run(
                [
                    "tmux",
                    "split-window",
                    "-t",
                    name,
                    "-v",  # vertical split
                    "-p",
                    "25",  # 25% height for tail pane
                    "bash",
                    "-c",
                    f"touch {quoted} && tail -f {quoted}; read",
                ],
                check=True,
            )

        # Select the top pane (the TUI)
        subprocess.run(["tmux", "select-pane", "-t", f"{name}:0.0"], check=True)
    except Exception:
        # Kill the partial session before re-raising
        subprocess.run(["tmux", "kill-session", "-t", name], check=False)
        raise

    # Attach — blocks until the user detaches or the session ends
    subprocess.run(["tmux", "attach-session", "-t", name])

    # Read the exit code written by execute_sprint() inside the tmux session
    sentinel = config.release_dir / ".sprint-exitcode"
    exit_code = 0
    try:
        exit_code = int(sentinel.read_text().strip())
    except (OSError, ValueError):
        pass  # session may have been killed externally; assume success
    if exit_code != 0:
        raise SystemExit(exit_code)


def _build_foreground_command(config: SprintConfig) -> list[str]:
    """Build the superclaude sprint run ... --no-tmux command."""
    cmd = [
        "superclaude",
        "sprint",
        "run",
        str(config.index_path),
        "--no-tmux",
        "--start",
        str(config.start_phase),
        "--max-turns",
        str(config.max_turns),
        "--permission-flag",
        config.permission_flag,
    ]
    if config.end_phase:
        cmd.extend(["--end", str(config.end_phase)])
    if config.model:
        cmd.extend(["--model", config.model])
    if config.tmux_session_name:
        cmd.extend(["--tmux-session-name", config.tmux_session_name])
    return cmd


def update_tail_pane(tmux_session_name: str, output_file: Path):
    """Switch the bottom pane to tail a different output file."""
    subprocess.run(
        [
            "tmux",
            "send-keys",
            "-t",
            f"{tmux_session_name}:0.1",  # bottom pane
            "C-c",  # kill current tail
        ],
        check=False,
    )
    quoted = shlex.quote(str(output_file))
    subprocess.run(
        [
            "tmux",
            "send-keys",
            "-t",
            f"{tmux_session_name}:0.1",
            f"tail -f {quoted}\n",
        ],
        check=False,
    )


def attach_to_sprint():
    """Attach to a running sprint session."""
    name = find_running_session()
    if name is None:
        click.echo("No running sprint session found.")
        raise SystemExit(1)
    subprocess.run(["tmux", "attach-session", "-t", name])


def kill_sprint(force: bool = False):
    """Kill a running sprint session."""
    name = find_running_session()
    if name is None:
        click.echo("No running sprint session found.")
        raise SystemExit(1)
    if force:
        subprocess.run(["tmux", "kill-session", "-t", name])
    else:
        # Send SIGTERM to the sprint process, wait, then kill session
        subprocess.run(["tmux", "send-keys", "-t", f"{name}:0.0", "C-c"])
        click.echo(f"Sent interrupt to {name}. Waiting 10s for graceful shutdown...")
        time.sleep(10)
        subprocess.run(["tmux", "kill-session", "-t", name], check=False)
