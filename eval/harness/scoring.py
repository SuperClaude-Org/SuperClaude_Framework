"""Score a finished run by executing the task's verify.sh inside a container.

Machine pass/fail only — no LLM judge (rule #1 of the eval methodology). The
verifier is mounted read-only and outside the agent's workdir so the model can
neither read nor edit the test. Docker is required (runtime-workflow rule:
tests run in containers for CI parity).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .config import Task


def verify(task: Task, workdir: Path, timeout_s: int = 900) -> tuple[bool, str]:
    """Run verify.sh in `task.verify_image` against `workdir`. exit 0 => pass.
    Returns (passed, tail_of_output)."""
    if not task.verify_script.is_file():
        return False, "no verify.sh"

    cmd = [
        "docker", "run", "--rm",
        "--network", "none",                       # hermetic: no network during scoring
        "-v", f"{workdir}:/work",
        "-v", f"{task.verify_script}:/verify.sh:ro",
        "-w", "/work",
        task.verify_image,
        "bash", "/verify.sh",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return False, "verify timeout"
    tail = (proc.stdout + proc.stderr)[-2000:]
    return proc.returncode == 0, tail
