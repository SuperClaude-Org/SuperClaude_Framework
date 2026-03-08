"""Configuration loading and validation for Cleanup Audit pipeline.

Handles CLI argument resolution, file discovery, and config construction.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

from pathlib import Path

from .models import CleanupAuditConfig

DEFAULT_BATCH_SIZE = 20
DEFAULT_MAX_TURNS = 100
DEFAULT_STALL_TIMEOUT = 300
SUPPORTED_PASSES = ("surface", "structural", "cross-cutting", "all")
SUPPORTED_FOCUS = ("infrastructure", "frontend", "backend", "all")


def load_cleanup_audit_config(
    target: str | Path = ".",
    output_dir: str | Path | None = None,
    pass_selection: str = "all",
    batch_size: int = DEFAULT_BATCH_SIZE,
    focus: str = "all",
    max_turns: int = DEFAULT_MAX_TURNS,
    model: str = "",
    dry_run: bool = False,
    debug: bool = False,
) -> CleanupAuditConfig:
    """Construct and validate pipeline configuration from CLI arguments."""
    target_path = Path(target).resolve()
    if not target_path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    if pass_selection not in SUPPORTED_PASSES:
        raise ValueError(
            f"Unsupported pass: {pass_selection}. "
            f"Supported: {', '.join(SUPPORTED_PASSES)}"
        )

    if focus not in SUPPORTED_FOCUS:
        raise ValueError(
            f"Unsupported focus: {focus}. "
            f"Supported: {', '.join(SUPPORTED_FOCUS)}"
        )

    resolved_output = Path(output_dir).resolve() if output_dir else target_path

    config = CleanupAuditConfig(
        target_path=target_path,
        output_dir=resolved_output,
        work_dir=resolved_output,
        pass_selection=pass_selection,
        batch_size=batch_size,
        focus=focus,
        max_turns=max_turns,
        model=model,
        dry_run=dry_run,
        debug=debug,
        stall_timeout=DEFAULT_STALL_TIMEOUT,
    )
    return config


def discover_files(config: CleanupAuditConfig) -> list[Path]:
    """Discover files in target path for audit scanning."""
    target = config.target_path
    if target.is_file():
        return [target]

    files = []
    for p in sorted(target.rglob("*")):
        if p.is_file() and not _should_skip(p):
            files.append(p)
    return files


def _should_skip(path: Path) -> bool:
    """Check if a file should be skipped during discovery."""
    skip_dirs = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".egg-info",
    }
    for part in path.parts:
        if part in skip_dirs:
            return True
    return False


def batch_files(files: list[Path], batch_size: int) -> list[list[Path]]:
    """Split file list into batches for parallel processing."""
    return [files[i : i + batch_size] for i in range(0, len(files), batch_size)]
