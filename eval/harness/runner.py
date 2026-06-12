"""Run one arm against one task: fresh workdir -> claude -p (host) -> capture.

Scoring lives in scoring.py (docker). Keeping the agent on the host means CLI
auth and speed are unaffected; the workdir is a throwaway copy of the task's
`environment/` so edits never touch the canonical task or the verifier.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import DEFAULT_MODEL, PERMISSION_MODE, Arm, Task


def prepare_workdir(task: Task, parent: Path | None = None) -> Path:
    """Copy the task's environment/ into a fresh dir the agent may mutate."""
    dst = Path(tempfile.mkdtemp(prefix=f"sc-eval-{task.id}-", dir=parent))
    work = dst / "work"
    if task.environment_dir.is_dir():
        shutil.copytree(task.environment_dir, work)
    else:
        work.mkdir(parents=True)
    return work


def _build_command(task: Task, arm: Arm, model: str) -> list[str]:
    cmd = [
        "claude",
        "-p",
        task.prompt(),
        "--output-format",
        "json",
        "--model",
        model,
        "--permission-mode",
        PERMISSION_MODE,
        "--max-turns",
        str(task.max_turns),
    ]
    if arm.plugin_dir is not None:
        cmd += ["--plugin-dir", str(arm.plugin_dir)]
    return cmd


def run_agent(task: Task, arm: Arm, workdir: Path, model: str = DEFAULT_MODEL,
              timeout_s: int = 1800) -> dict:
    """Invoke claude headless in `workdir`. Returns the parsed result JSON
    (augmented with `_timed_out` / `_parse_error` flags). Never raises on a
    failed agent run — a crash is just a failing trial."""
    cmd = _build_command(task, arm, model)
    try:
        proc = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return {"is_error": True, "_timed_out": True, "result": "",
                "usage": {}, "modelUsage": {}}

    stdout = proc.stdout.strip()
    if not stdout:
        return {"is_error": True, "_parse_error": True,
                "result": proc.stderr[-2000:], "usage": {}, "modelUsage": {}}
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        # stream-json or trailing noise: take the last JSON line.
        line = next((ln for ln in reversed(stdout.splitlines())
                     if ln.startswith("{")), "")
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return {"is_error": True, "_parse_error": True,
                    "result": stdout[-2000:], "usage": {}, "modelUsage": {}}
    return data
