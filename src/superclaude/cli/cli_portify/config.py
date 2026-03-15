"""Configuration loading and validation for CLI Portify pipeline.

Implements:
  T02.01 — Workflow path resolution (INVALID_PATH, AMBIGUOUS_PATH)
  T02.02 — CLI name derivation (DERIVATION_FAILED, --name override)
  T02.03 — Collision detection (NAME_COLLISION, OUTPUT_NOT_WRITABLE)
  T02.04 — Workdir creation and portify-config.yaml emission
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

from .models import (
    AMBIGUOUS_PATH,
    DERIVATION_FAILED,
    INVALID_PATH,
    NAME_COLLISION,
    OUTPUT_NOT_WRITABLE,
    PortifyConfig,
    _derive_name_from_path,
)

# ---------------------------------------------------------------------------
# Known CLI modules that block collision by default (reserved names)
# ---------------------------------------------------------------------------
_KNOWN_CLI_MODULES = frozenset(
    {
        "sprint",
        "roadmap",
        "tasklist",
        "cleanup-audit",
        "cleanup_audit",
        "audit",
        "pipeline",
        "main",
    }
)


def load_portify_config(
    workflow_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    cli_name: Optional[str] = None,
    commands_dir: Optional[Union[str, Path]] = None,
    skills_dir: Optional[Union[str, Path]] = None,
    agents_dir: Optional[Union[str, Path]] = None,
    include_agents: Optional[Union[bool, list[str]]] = None,
    save_manifest_path: Optional[Union[str, Path]] = None,
    dry_run: bool = False,
    debug: bool = False,
    max_turns: int = 200,
    model: str = "",
    stall_timeout: int = 300,
) -> PortifyConfig:
    """Construct a PortifyConfig from CLI arguments.

    Does NOT validate — call validate_portify_config() separately.

    Args:
        workflow_path: Path to the workflow skill directory or SKILL.md file.
        output_dir: Where generated CLI module will be written. Defaults to
                    src/superclaude/cli/ relative to workflow_path project root.
        cli_name: Explicit CLI module name override. If omitted, derived
                  automatically from workflow directory name.
        commands_dir: Override for commands discovery directory.
        skills_dir: Override for skills discovery directory.
        agents_dir: Override for agents discovery directory.
        include_agents: If a list, enables agent inclusion and stores the list.
                        If True/False, sets include_agents flag only.
        save_manifest_path: Path to write the component manifest.
        dry_run: Limit run to config validation only.
        debug: Enable debug logging.
        max_turns: Maximum subprocess turns allowed.
        model: Claude model identifier.
        stall_timeout: Seconds before stall detection triggers.
    """
    wp = Path(workflow_path).resolve()
    target_input = str(workflow_path)

    # Resolve optional directories
    resolved_commands = Path(commands_dir).resolve() if commands_dir else None
    resolved_skills = Path(skills_dir).resolve() if skills_dir else None
    resolved_agents = Path(agents_dir).resolve() if agents_dir else None
    resolved_manifest = Path(save_manifest_path).resolve() if save_manifest_path else None
    resolved_output = Path(output_dir).resolve() if output_dir else None

    # Handle include_agents
    include_agents_flag = False
    include_agents_list: list[str] = []
    if isinstance(include_agents, list):
        include_agents_flag = True
        include_agents_list = include_agents
    elif include_agents is True:
        include_agents_flag = True

    config = PortifyConfig(
        workflow_path=wp,
        cli_name=cli_name or "",
        output_dir=resolved_output,
        commands_dir=resolved_commands,
        skills_dir=resolved_skills,
        agents_dir=resolved_agents,
        include_agents=include_agents_flag,
        _include_agents_list=include_agents_list,
        save_manifest_path=resolved_manifest,
        target_input=target_input,
        dry_run=dry_run,
        debug=debug,
        max_turns=max_turns,
        model=model,
        stall_timeout=stall_timeout,
    )
    return config


def validate_portify_config(config: PortifyConfig) -> list[str]:
    """Validate a PortifyConfig and return a list of error strings.

    Returns an empty list on success. Never raises — all errors are
    collected and returned as human-readable strings.

    Checks (in order):
      1. workflow_path exists
      2. SKILL.md present at resolved workflow path
      3. output_dir parent is writable (or can be created)
      4. CLI name does not collide with existing non-portified modules
    """
    errors: list[str] = []

    # --- 1. Workflow path existence ---
    try:
        resolved = config.resolve_workflow_path()
    except Exception as exc:
        errors.append(f"Cannot resolve workflow path: {exc}")
        return errors

    if not resolved.exists():
        errors.append(
            f"Workflow path does not exist: {resolved}"
        )
        return errors  # No point continuing if path missing

    # --- 2. SKILL.md check ---
    skill_md = resolved / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"SKILL.md not found at {resolved}")

    # --- 3. Output directory writability ---
    if config.output_dir is not None:
        out_parent = config.output_dir.parent
        out_path = config.output_dir

        # Allow path that doesn't exist yet if parent exists and is writable
        if out_path.exists() and not os.access(out_path, os.W_OK):
            errors.append(f"Output path is not writable: {out_path}")
        elif not out_path.exists():
            # Check if parent directory is reachable
            try:
                out_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as exc:
                errors.append(f"Cannot create output directory {out_path}: {exc}")

    # --- 4. Collision detection ---
    try:
        derived_name = config.derive_cli_name()
        collision_errors = _check_collision(derived_name, config)
        errors.extend(collision_errors)
    except Exception as exc:
        # DerivationFailedError or similar
        errors.append(str(exc))

    return errors


# ---------------------------------------------------------------------------
# T02.01: Workflow Path Resolution
# ---------------------------------------------------------------------------


def resolve_workflow_path(
    name_or_path: Union[str, Path],
    skills_root: Optional[Path] = None,
) -> Path:
    """Resolve a skill name or path to a concrete skill directory.

    Rules:
      1. If the input is an existing absolute or relative path to a directory
         containing SKILL.md → return it directly.
      2. If the input is a SKILL.md file → return its parent.
      3. If skills_root is provided, search for matching subdirectories.
         - Exact match → return it.
         - Partial match (multiple) → raise AmbiguousPathError.
         - No match → raise InvalidPathError.
      4. If no skills_root, treat name_or_path as a literal path.

    Raises:
        InvalidPathError: Path found but no SKILL.md present.
        AmbiguousPathError: Partial name matches multiple skill directories.
    """
    from .models import AmbiguousPathError, InvalidPathError

    p = Path(name_or_path).resolve()

    # Direct path resolution
    if p.exists():
        if p.is_file() and p.name == "SKILL.md":
            return p.parent
        if p.is_dir():
            if not (p / "SKILL.md").exists():
                raise InvalidPathError(str(p))
            return p
        raise InvalidPathError(str(p))

    # Search under skills_root
    if skills_root and skills_root.exists():
        name = Path(name_or_path).name
        candidates = [
            d for d in skills_root.iterdir()
            if d.is_dir() and name.lower() in d.name.lower()
        ]
        if len(candidates) == 1:
            candidate = candidates[0]
            if not (candidate / "SKILL.md").exists():
                raise InvalidPathError(str(candidate))
            return candidate
        elif len(candidates) > 1:
            from .models import AmbiguousPathError
            raise AmbiguousPathError(str(name), [str(c) for c in candidates])
        # No match under skills_root → fall through to not-found

    raise InvalidPathError(str(p))


# ---------------------------------------------------------------------------
# T02.02: CLI Name Derivation
# ---------------------------------------------------------------------------


def derive_cli_name(workflow_path: Path, explicit_name: Optional[str] = None) -> str:
    """Derive the CLI module name from a workflow path.

    If explicit_name is provided, it is used directly (bypasses derivation).
    Otherwise, derives from the workflow directory name by:
      1. Stripping 'sc-' prefix
      2. Stripping '-protocol' suffix
      3. Normalizing to kebab-case

    Raises:
        DerivationFailedError: If derivation yields an empty string and no
                               explicit_name was provided.
    """
    from .models import DerivationFailedError

    if explicit_name:
        return explicit_name
    return _derive_name_from_path(workflow_path)


# ---------------------------------------------------------------------------
# T02.03: Collision Detection
# ---------------------------------------------------------------------------


def _check_collision(derived_name: str, config: PortifyConfig) -> list[str]:
    """Check if derived CLI name collides with an existing module.

    Returns list of error strings (empty if no collision).

    A collision is blocked unless the existing module's __init__.py contains
    portification markers ('Generated by' or 'Portified from').
    """
    from .utils import is_portified_module

    errors: list[str] = []

    # Check known reserved CLI module names
    normalized = derived_name.replace("-", "_")
    if derived_name in _KNOWN_CLI_MODULES or normalized in _KNOWN_CLI_MODULES:
        errors.append(
            f"CLI name '{derived_name}' collides with existing module "
            f"'{normalized}' — use --name to choose a different name"
        )
        return errors

    # Check filesystem collision under src/superclaude/cli/
    cli_root = _find_cli_root(config)
    if cli_root is None:
        return errors

    candidate = cli_root / normalized
    if candidate.exists():
        init_py = candidate / "__init__.py"
        if init_py.exists() and is_portified_module(init_py):
            # Overwrite allowed
            return errors
        errors.append(
            f"CLI name '{derived_name}' collides with existing module at "
            f"{candidate} — use --name to choose a different name, or "
            "add portification marker to __init__.py to allow overwrite"
        )

    return errors


def _find_cli_root(config: PortifyConfig) -> Optional[Path]:
    """Find the src/superclaude/cli/ root for collision checking."""
    # Walk up from workflow_path to find the cli directory
    search = config.workflow_path
    for _ in range(10):
        candidate = search / "src" / "superclaude" / "cli"
        if candidate.exists():
            return candidate
        parent = search.parent
        if parent == search:
            break
        search = parent
    # Fallback: look relative to the package
    import superclaude.cli
    import importlib
    try:
        spec = importlib.util.find_spec("superclaude.cli")
        if spec and spec.submodule_search_locations:
            return Path(list(spec.submodule_search_locations)[0])
    except Exception:
        pass
    return None
