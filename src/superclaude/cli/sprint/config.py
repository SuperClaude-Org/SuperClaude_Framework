"""Sprint configuration — phase discovery, validation, and config loading."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import click

from .models import Phase, SprintConfig, TaskEntry

# Canonical phase filename conventions (case-insensitive):
# 1) phase-1-tasklist.md
# 2) p1-tasklist.md
# 3) phase_1_tasklist.md
# 4) tasklist-p1.md
PHASE_FILE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:phase-(\d+)-tasklist\.md"
    r"|p(\d+)-tasklist\.md"
    r"|phase_(\d+)_tasklist\.md"
    r"|tasklist-p(\d+)\.md)(?![A-Za-z0-9])",
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
        num = int(next(g for g in match.groups() if g is not None))
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
                num = int(next(g for g in m.groups() if g is not None))
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
) -> dict[str, list[str]]:
    """Validate phase files exist and check for gaps.

    Returns separated buckets with keys: errors, warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []
    active = [p for p in phases if start <= p.number <= end]

    # Check files exist
    for p in active:
        if not p.file.exists():
            errors.append(f"ERROR: Phase {p.number} file missing: {p.file}")

    # Check for gaps
    numbers = [p.number for p in active]
    for i in range(1, len(numbers)):
        if numbers[i] != numbers[i - 1] + 1:
            warnings.append(
                f"WARN: Gap in sequence: Phase {numbers[i-1]} -> Phase {numbers[i]}"
            )

    return {"errors": errors, "warnings": warnings}


def load_sprint_config(
    index_path: Path,
    start_phase: int = 1,
    end_phase: int = 0,
    max_turns: int = 50,
    model: str = "",
    dry_run: bool = False,
    permission_flag: str = "--dangerously-skip-permissions",
    debug: bool = False,
    stall_timeout: int = 0,
    stall_action: str = "warn",
    shadow_gates: bool = False,
) -> SprintConfig:
    """Load and validate a complete sprint configuration."""
    index_path = Path(index_path).resolve()

    if not index_path.exists():
        raise click.ClickException(f"Index file not found: {index_path}")

    phases = discover_phases(index_path)
    if not phases:
        raise click.ClickException(
            "No phase files discovered. Expected canonical filenames like: "
            "phase-1-tasklist.md, p1-tasklist.md, phase_1_tasklist.md, tasklist-p1.md"
        )

    # Enrich phases with names
    for phase in phases:
        phase.name = _extract_phase_name(phase.file)

    # Auto-detect end phase
    if end_phase == 0:
        end_phase = max(p.number for p in phases)

    # Validate
    validation = validate_phases(phases, start_phase, end_phase)
    errors = validation["errors"]
    warnings = validation["warnings"]
    if errors:
        for e in errors:
            click.echo(e, err=True)
        raise click.ClickException(f"{len(errors)} phase file(s) missing.")

    for w in warnings:
        click.echo(w, err=True)

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
        debug=debug,
        stall_timeout=stall_timeout,
        stall_action=stall_action,
        shadow_gates=shadow_gates,
    )

    # Validate that the requested range yields at least one active phase
    if not config.active_phases:
        available = [p.number for p in phases]
        raise click.ClickException(
            f"No phases in range [{start_phase}, {end_phase}]. "
            f"Available phase numbers: {available}"
        )

    return config


# ---------------------------------------------------------------------------
# Tasklist parser — extracts task inventory from phase markdown
# ---------------------------------------------------------------------------

_TASK_HEADING_RE = re.compile(
    r"^###\s+(T\d{2}\.\d{2})\s*(?:--|-—|—)\s*(.+)",
    re.MULTILINE,
)

_DEPENDENCY_RE = re.compile(
    r"\*\*Dependencies:\*\*\s*(.*)",
    re.IGNORECASE,
)

_TASK_ID_REF_RE = re.compile(r"T\d{2}\.\d{2}")

_logger = logging.getLogger("superclaude.sprint.config")


def parse_tasklist(content: str) -> list[TaskEntry]:
    """Parse phase tasklist markdown into a structured task inventory.

    Extracts task ID, title, and dependency annotations from each
    ``### T<PP>.<TT> -- Title`` block. Malformed input (missing headings,
    invalid IDs, empty content) is handled gracefully — invalid blocks
    are skipped with a logged warning.

    Args:
        content: Raw markdown text of a phase tasklist file.

    Returns:
        Ordered list of :class:`TaskEntry` instances.
    """
    if not content or not content.strip():
        return []

    headings = list(_TASK_HEADING_RE.finditer(content))
    if not headings:
        _logger.warning("No task headings (### T<PP>.<TT>) found in tasklist content")
        return []

    tasks: list[TaskEntry] = []
    for i, match in enumerate(headings):
        task_id = match.group(1)
        title = match.group(2).strip()

        # Extract the block body between this heading and the next (or EOF)
        block_start = match.end()
        block_end = headings[i + 1].start() if i + 1 < len(headings) else len(content)
        block = content[block_start:block_end]

        # Extract dependencies
        dependencies: list[str] = []
        dep_match = _DEPENDENCY_RE.search(block)
        if dep_match:
            dep_text = dep_match.group(1).strip()
            if dep_text.lower() not in ("none", ""):
                dependencies = _TASK_ID_REF_RE.findall(dep_text)

        # Build description from the deliverables section if present
        description = ""
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith("**Deliverables:**"):
                # Grab the next non-empty line(s) after "Deliverables:"
                idx = block.index(stripped) + len(stripped)
                rest = block[idx:].strip()
                desc_lines = []
                for dline in rest.splitlines():
                    dline = dline.strip()
                    if not dline or dline.startswith("**"):
                        break
                    # Strip leading "- " from markdown list items
                    if dline.startswith("- "):
                        dline = dline[2:]
                    desc_lines.append(dline)
                description = " ".join(desc_lines)
                break

        tasks.append(
            TaskEntry(
                task_id=task_id,
                title=title,
                description=description,
                dependencies=dependencies,
            )
        )

    return tasks


def parse_tasklist_file(path: Path) -> list[TaskEntry]:
    """Read a phase tasklist file and parse it into a task inventory.

    Args:
        path: Path to the phase tasklist markdown file.

    Returns:
        Ordered list of :class:`TaskEntry` instances.

    Raises:
        FileNotFoundError: If the path does not exist.
    """
    content = path.read_text(errors="replace")
    return parse_tasklist(content)
