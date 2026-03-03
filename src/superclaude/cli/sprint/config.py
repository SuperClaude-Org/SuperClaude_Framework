"""Sprint configuration — phase discovery, validation, and config loading."""

from __future__ import annotations

import re
from pathlib import Path

import click

from .models import Phase, SprintConfig

# Matches: phase-1-tasklist.md, p1-tasklist.md, phase1-tasklist.md,
# Phase_1_tasklist.md, tasklist-P1.md, tasklist-p1.md
PHASE_FILE_PATTERN = re.compile(
    r"(?:phase|p)[-_]?(\d+)[-_]tasklist[^\s|)]*\.md"
    r"|"
    r"tasklist[-_](?:phase|p)[-_]?(\d+)[^\s|)]*\.md",
    re.IGNORECASE,
)


def discover_phases(index_path: Path) -> list[Phase]:
    """Discover phase files from the index and/or directory.

    Strategy 1: grep the index file for phase file references.
    Strategy 2: scan the directory for files matching the pattern.
    Deduplicates by phase number, sorts ascending.
    """
    index_dir = index_path.parent
    index_name = index_path.name
    phases: dict[int, Phase] = {}

    # Strategy 1: parse index file
    index_text = index_path.read_text(errors="replace")
    for match in PHASE_FILE_PATTERN.finditer(index_text):
        num = int(match.group(1) or match.group(2))
        filename = match.group(0)
        filepath = index_dir / filename
        if filepath.exists() and num not in phases:
            phases[num] = Phase(number=num, file=filepath)

    # Strategy 2: scan directory if nothing found
    if not phases:
        for f in sorted(index_dir.iterdir()):
            if f.name == index_name or not f.is_file():
                continue
            m = PHASE_FILE_PATTERN.search(f.name)
            if m:
                num = int(m.group(1) or m.group(2))
                if num not in phases:
                    phases[num] = Phase(number=num, file=f)

    return [phases[k] for k in sorted(phases)]


def _extract_phase_name(phase_file: Path) -> str:
    """Try to extract a phase name from the first heading."""
    try:
        for line in phase_file.open():
            line = line.strip()
            if line.startswith("# "):
                # Strip markdown heading and phase number prefix
                name = re.sub(r"^#\s+(?:Phase\s+\d+\s*[-:—]\s*)?", "", line)
                return name[:50]  # truncate
    except OSError:
        pass
    return ""


def validate_phases(
    phases: list[Phase],
    start: int,
    end: int,
) -> list[str]:
    """Validate phase files exist and check for gaps.

    Returns list of warning/error messages.
    """
    messages = []
    active = [p for p in phases if start <= p.number <= end]

    # Check files exist
    for p in active:
        if not p.file.exists():
            messages.append(f"ERROR: Phase {p.number} file missing: {p.file}")

    # Check for gaps
    numbers = [p.number for p in active]
    for i in range(1, len(numbers)):
        if numbers[i] != numbers[i - 1] + 1:
            messages.append(
                f"WARN: Gap in sequence: Phase {numbers[i-1]} -> Phase {numbers[i]}"
            )

    return messages


def load_sprint_config(
    index_path: Path,
    start_phase: int = 1,
    end_phase: int = 0,
    max_turns: int = 50,
    model: str = "",
    dry_run: bool = False,
    permission_flag: str = "--dangerously-skip-permissions",
) -> SprintConfig:
    """Load and validate a complete sprint configuration."""
    index_path = Path(index_path).resolve()

    if not index_path.exists():
        raise click.ClickException(f"Index file not found: {index_path}")

    phases = discover_phases(index_path)
    if not phases:
        raise click.ClickException(
            "No phase files discovered. Expected filenames like: "
            "phase-1-tasklist.md, p1-tasklist.md, tasklist-P1.md"
        )

    # Enrich phases with names
    for phase in phases:
        phase.name = _extract_phase_name(phase.file)

    # Auto-detect end phase
    if end_phase == 0:
        end_phase = max(p.number for p in phases)

    # Validate
    messages = validate_phases(phases, start_phase, end_phase)
    errors = [m for m in messages if m.startswith("ERROR")]
    if errors:
        for e in errors:
            click.echo(e, err=True)
        raise click.ClickException(f"{len(errors)} phase file(s) missing.")

    for m in messages:
        if m.startswith("WARN"):
            click.echo(m, err=True)

    config = SprintConfig(
        index_path=index_path,
        release_dir=index_path.parent,
        phases=phases,
        start_phase=start_phase,
        end_phase=end_phase,
        max_turns=max_turns,
        model=model,
        dry_run=dry_run,
        permission_flag=permission_flag,
    )

    # Validate that the requested range yields at least one active phase
    if not config.active_phases:
        available = [p.number for p in phases]
        raise click.ClickException(
            f"No phases in range [{start_phase}, {end_phase}]. "
            f"Available phase numbers: {available}"
        )

    return config
