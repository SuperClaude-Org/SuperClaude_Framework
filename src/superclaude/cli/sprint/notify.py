"""Desktop notifications — cross-platform, best-effort."""

from __future__ import annotations

import platform
import shutil
import subprocess

from .models import PhaseResult, SprintResult


def _notify(title: str, message: str, urgent: bool = False):
    """Send a desktop notification. Fails silently."""
    system = platform.system()
    try:
        if system == "Linux" and shutil.which("notify-send"):
            cmd = ["notify-send"]
            if urgent:
                cmd.extend(["--urgency", "critical"])
            cmd.extend([title, message])
            subprocess.run(cmd, timeout=5, check=False)

        elif system == "Darwin" and shutil.which("osascript"):
            script = (
                f'display notification "{message}" '
                f'with title "{title}"'
            )
            subprocess.run(
                ["osascript", "-e", script],
                timeout=5,
                check=False,
            )
    except Exception:
        pass  # notifications are best-effort


def notify_phase_complete(result: PhaseResult):
    """Notify on phase completion."""
    if result.status.is_failure:
        _notify(
            "Sprint HALT",
            f"Phase {result.phase.number} failed: {result.status.value}",
            urgent=True,
        )
    elif result.status.is_success:
        _notify(
            "Phase Complete",
            f"Phase {result.phase.number}: {result.status.value} "
            f"({result.duration_display})",
        )


def notify_sprint_complete(result: SprintResult):
    """Notify on sprint completion."""
    if result.outcome.value == "success":
        _notify(
            "Sprint Complete",
            f"All phases passed in {result.duration_display}",
        )
    else:
        _notify(
            "Sprint Finished",
            f"Outcome: {result.outcome.value} ({result.duration_display})",
            urgent=True,
        )
