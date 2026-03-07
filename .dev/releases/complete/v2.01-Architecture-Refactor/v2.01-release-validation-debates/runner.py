"""
v2.01 Release Validation — Test Runners

Executes individual tests (structural via bash, behavioral via claude -p).
"""

import asyncio
import subprocess
from pathlib import Path


async def run_structural_test(test_id: str, repo_root: Path) -> tuple[str, int]:
    """Run a structural test and return (output, exit_code)."""
    commands = {
        "S1": ["make", "-C", str(repo_root), "lint-architecture"],
        "S2": ["make", "-C", str(repo_root), "verify-sync"],
        "S3": None,  # Special: multi-grep
        "S4": None,  # Special: wc -l
        "S5": None,  # Special: grep frontmatter
    }

    if test_id == "S3":
        return await _run_stale_reference_scan(repo_root)
    elif test_id == "S4":
        return await _run_size_check(repo_root)
    elif test_id == "S5":
        return await _run_frontmatter_check(repo_root)
    else:
        cmd = commands[test_id]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(repo_root),
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
        return stdout.decode(errors="replace"), proc.returncode


async def _run_stale_reference_scan(repo_root: Path) -> tuple[str, int]:
    """S3: Scan for stale references to old skill directory names."""
    old_names = [
        "sc-adversarial/",
        "sc-cleanup-audit/",
        "sc-roadmap/",
        "sc-task-unified/",
        "sc-validate-tests/",
    ]
    output_lines = []
    total_matches = 0

    for name in old_names:
        # Search for skills/<old-name> pattern to avoid test dir false positives
        cmd = [
            "grep",
            "-rn",
            f"skills/{name}",
            str(repo_root / "src"),
            str(repo_root / ".claude"),
            "--include=*.md",
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        matches = stdout.decode(errors="replace").strip()
        count = len(matches.splitlines()) if matches else 0
        total_matches += count
        output_lines.append(f"skills/{name}: {count} matches")
        if matches:
            output_lines.append(matches)

    output = "\n".join(output_lines)
    exit_code = 0 if total_matches == 0 else 1
    return output, exit_code


async def _run_size_check(repo_root: Path) -> tuple[str, int]:
    """S4: Check task-unified.md line count ≤ 200."""
    target = repo_root / "src" / "superclaude" / "commands" / "task-unified.md"
    if not target.exists():
        return f"FILE NOT FOUND: {target}", 1

    line_count = len(target.read_text().splitlines())
    output = f"task-unified.md: {line_count} lines (threshold: 200)"
    exit_code = 0 if line_count <= 200 else 1
    return output, exit_code


async def _run_frontmatter_check(repo_root: Path) -> tuple[str, int]:
    """S5: Check all 5 paired commands have Skill in allowed-tools."""
    commands_dir = repo_root / "src" / "superclaude" / "commands"
    target_files = [
        "adversarial.md",
        "cleanup-audit.md",
        "task-unified.md",
        "validate-tests.md",
        "roadmap.md",
    ]

    found = 0
    output_lines = []
    for fname in target_files:
        fpath = commands_dir / fname
        if not fpath.exists():
            output_lines.append(f"  MISSING: {fname}")
            continue

        content = fpath.read_text()
        if "allowed-tools" in content and "Skill" in content:
            found += 1
            output_lines.append(f"  PASS: {fname}")
        else:
            output_lines.append(f"  FAIL: {fname} — missing allowed-tools with Skill")

    output = f"Frontmatter check: {found}/{len(target_files)}\n" + "\n".join(
        output_lines
    )
    exit_code = 0 if found == len(target_files) else 1
    return output, exit_code


# Per-turn timeout by model (seconds). Derived from observed run durations:
# haiku successful 3-turn runs: 80-177s (~27-59s/turn), so 90s/turn gives headroom.
# sonnet and opus are progressively faster.
_TIMEOUT_PER_TURN: dict[str, int] = {
    "haiku": 90,
    "sonnet": 60,
    "opus": 45,
}
_TIMEOUT_DEFAULT_PER_TURN = 60  # For unknown models
_TIMEOUT_MAX = 600  # Hard cap: never wait longer than 10 minutes

# Startup overhead measured experimentally (2026-02-25):
# - Trivial prompt: ~6s
# - /sc:task prompt: ~12s (CLAUDE.md + skill resolution)
# Conservative buffer covers both cases with headroom.
_STARTUP_BUFFER = 15  # seconds


def _compute_timeout(model: str, max_turns: int, concurrency: int = 1) -> int:
    """Compute timeout with startup buffer and concurrency scaling.

    Formula: startup_buffer + per_turn * max_turns * concurrency_factor
    Concurrency factor: linear scaling based on measured 2.41x at N=30.
    """
    per_turn = _TIMEOUT_PER_TURN.get(model, _TIMEOUT_DEFAULT_PER_TURN)
    concurrency_factor = 1.0 + (concurrency / 50.0)
    turn_budget = int(per_turn * max_turns * concurrency_factor)
    return min(_STARTUP_BUFFER + turn_budget, _TIMEOUT_MAX)


async def run_behavioral_test(
    prompt: str,
    model: str,
    max_turns: int = 3,
    repo_root: Path = None,
    extra_dirs: list[str] | None = None,
    concurrency: int = 1,
) -> tuple[str, int]:
    """Run a behavioral test via claude -p and return (output, exit_code)."""
    cmd = [
        "env",
        "-u",
        "CLAUDECODE",
        "claude",
        "-p",
        "--dangerously-skip-permissions",
        "--model",
        model,
        "--max-turns",
        str(max_turns),
        "--output-format",
        "text",
    ]

    if extra_dirs:
        for d in extra_dirs:
            if d:
                cmd.extend(["--add-dir", d])

    # Use '--' to separate options from the positional prompt argument.
    # Without this, variadic options like --add-dir <directories...> can
    # consume the prompt string as another directory value, leaving claude
    # with no prompt (which causes the --print input error).
    cmd.append("--")
    cmd.append(prompt)

    timeout = _compute_timeout(model, max_turns, concurrency)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(repo_root) if repo_root else None,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        output = stdout.decode(errors="replace")
        if proc.returncode != 0:
            output += f"\n\n--- STDERR ---\n{stderr.decode(errors='replace')}"
        return output, proc.returncode

    except asyncio.TimeoutError:
        try:
            proc.kill()
            await proc.wait()
        except Exception:
            pass
        return f"TIMEOUT after {timeout}s", -1

    except FileNotFoundError:
        return "ERROR: claude binary not found", -2

    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}", -3
