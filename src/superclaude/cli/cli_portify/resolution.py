"""Target resolution for cli-portify pipeline.

Deterministic resolution of user-supplied target strings into
ResolvedTarget instances. Classifies inputs into 6 forms and
resolves command/skill pairs.

Pure module: no side effects, no I/O beyond file existence checks.
No async code.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from superclaude.cli.cli_portify.models import (
    ERR_AMBIGUOUS_TARGET,
    ERR_TARGET_NOT_FOUND,
    ResolvedTarget,
    TargetInputType,
)

logger = logging.getLogger(__name__)


class ResolutionError(Exception):
    """Raised when target resolution fails."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


def resolve_target(
    target: str | None,
    project_root: Path | None = None,
    commands_dir: Path | None = None,
    skills_dir: Path | None = None,
    agents_dir: Path | None = None,
) -> ResolvedTarget:
    """Resolve a user-supplied target string into a ResolvedTarget.

    Classifies the target into one of 6 input forms and resolves
    the command/skill pair.

    Args:
        target: User-supplied target string.
        project_root: Root of the SuperClaude project.
        commands_dir: Directory containing command .md files.
        skills_dir: Directory containing skill directories.
        agents_dir: Directory containing agent .md files.

    Returns:
        ResolvedTarget with resolved paths.

    Raises:
        ResolutionError: If target cannot be resolved.
    """
    start = time.monotonic()

    # Guard: empty/whitespace/None
    if target is None or not target.strip():
        logger.debug("resolve_target: empty/None target")
        raise ResolutionError(
            "Target is empty or None",
            ERR_TARGET_NOT_FOUND,
        )

    original = target.strip()

    # Guard: sc: prefix stripping
    if original.startswith("sc:"):
        stripped = original[3:].strip()
        if not stripped:
            logger.debug("resolve_target: sc: prefix with empty remainder")
            raise ResolutionError(
                "Target is empty after stripping 'sc:' prefix",
                ERR_TARGET_NOT_FOUND,
            )
        logger.debug("resolve_target: stripped sc: prefix -> %s", stripped)
        original = stripped

    # Resolve default directories from project_root
    if project_root is not None:
        if commands_dir is None:
            commands_dir = project_root / "commands"
        if skills_dir is None:
            skills_dir = project_root / "skills"
        if agents_dir is None:
            agents_dir = project_root / "agents"

    # Classify and resolve
    result = _classify_and_resolve(
        original,
        project_root=project_root,
        commands_dir=commands_dir,
        skills_dir=skills_dir,
        agents_dir=agents_dir,
    )

    elapsed = time.monotonic() - start
    logger.debug("resolve_target: resolved in %.4fs", elapsed)
    return result


def _classify_and_resolve(
    target: str,
    project_root: Path | None,
    commands_dir: Path | None,
    skills_dir: Path | None,
    agents_dir: Path | None,
) -> ResolvedTarget:
    """Classify input form and resolve to ResolvedTarget.

    Classification order:
    1. Path-based forms (filesystem checks first)
       - SKILL_FILE: path ends with SKILL.md
       - COMMAND_PATH: path to an existing .md file
       - SKILL_DIR: path to an existing directory
    2. Name-based forms
       - SKILL_NAME: matches sc-*-protocol pattern in skills_dir
       - COMMAND_NAME: bare name matched in commands_dir
    """
    target_path = Path(target)

    # Form 5: SKILL_FILE — path to SKILL.md
    if target_path.name == "SKILL.md" and target_path.exists():
        skill_dir = target_path.parent
        logger.debug("classify: SKILL_FILE -> %s", skill_dir)
        cmd_path = _find_command_for_skill(skill_dir, commands_dir)
        return ResolvedTarget(
            input_form=target,
            input_type=TargetInputType.SKILL_FILE,
            command_path=cmd_path,
            skill_dir=skill_dir,
            project_root=project_root,
            commands_dir=commands_dir,
            skills_dir=skills_dir,
            agents_dir=agents_dir,
        )

    # Form 2: COMMAND_PATH — path to an existing .md file
    if target_path.suffix == ".md" and target_path.exists() and target_path.is_file():
        logger.debug("classify: COMMAND_PATH -> %s", target_path)
        skill = _find_skill_for_command(target_path, skills_dir)
        return ResolvedTarget(
            input_form=target,
            input_type=TargetInputType.COMMAND_PATH,
            command_path=target_path,
            skill_dir=skill,
            project_root=project_root,
            commands_dir=commands_dir,
            skills_dir=skills_dir,
            agents_dir=agents_dir,
        )

    # Form 3: SKILL_DIR — path to an existing directory
    if target_path.is_dir():
        logger.debug("classify: SKILL_DIR -> %s", target_path)
        cmd_path = _find_command_for_skill(target_path, commands_dir)
        return ResolvedTarget(
            input_form=target,
            input_type=TargetInputType.SKILL_DIR,
            command_path=cmd_path,
            skill_dir=target_path,
            project_root=project_root,
            commands_dir=commands_dir,
            skills_dir=skills_dir,
            agents_dir=agents_dir,
        )

    # Name-based resolution with ambiguity detection (command-first policy)
    cmd_match: Path | None = None
    skill_match: Path | None = None

    if commands_dir is not None:
        candidate_cmd = commands_dir / f"{target}.md"
        if candidate_cmd.exists() and candidate_cmd.is_file():
            cmd_match = candidate_cmd

    if skills_dir is not None:
        candidate_skill = skills_dir / target
        if candidate_skill.is_dir():
            skill_match = candidate_skill

    # Ambiguity detection: target matches both namespaces
    if cmd_match is not None and skill_match is not None:
        logger.debug(
            "classify: ambiguous target '%s' matches both command and skill; "
            "applying command-first policy",
            target,
        )
        # Command-first policy: resolve as COMMAND_NAME
        skill = _find_skill_for_command(cmd_match, skills_dir)
        return ResolvedTarget(
            input_form=target,
            input_type=TargetInputType.COMMAND_NAME,
            command_path=cmd_match,
            skill_dir=skill,
            project_root=project_root,
            commands_dir=commands_dir,
            skills_dir=skills_dir,
            agents_dir=agents_dir,
        )

    # Form 1: COMMAND_NAME — bare name matched in commands_dir
    if cmd_match is not None:
        logger.debug("classify: COMMAND_NAME -> %s", cmd_match)
        skill = _find_skill_for_command(cmd_match, skills_dir)
        return ResolvedTarget(
            input_form=target,
            input_type=TargetInputType.COMMAND_NAME,
            command_path=cmd_match,
            skill_dir=skill,
            project_root=project_root,
            commands_dir=commands_dir,
            skills_dir=skills_dir,
            agents_dir=agents_dir,
        )

    # Form 4: SKILL_NAME — skill directory name in skills_dir
    if skill_match is not None:
        logger.debug("classify: SKILL_NAME -> %s", skill_match)
        cmd_path = _find_command_for_skill(skill_match, commands_dir)
        return ResolvedTarget(
            input_form=target,
            input_type=TargetInputType.SKILL_NAME,
            command_path=cmd_path,
            skill_dir=skill_match,
            project_root=project_root,
            commands_dir=commands_dir,
            skills_dir=skills_dir,
            agents_dir=agents_dir,
        )

    logger.debug("classify: target not found -> %s", target)
    raise ResolutionError(
        f"Target '{target}' could not be resolved to a command or skill",
        ERR_TARGET_NOT_FOUND,
    )


def _find_skill_for_command(
    command_path: Path,
    skills_dir: Path | None,
) -> Path | None:
    """Find the linked skill directory for a command file.

    Parses the command file for an ## Activation section containing
    a Skill sc:<name>-protocol reference.
    """
    if skills_dir is None:
        return None

    try:
        content = command_path.read_text(encoding="utf-8")
    except OSError:
        return None

    skill_name = _parse_activation_skill(content)
    if skill_name is None:
        return None

    candidate = skills_dir / skill_name
    if candidate.is_dir():
        return candidate
    return None


def _find_command_for_skill(
    skill_dir: Path,
    commands_dir: Path | None,
) -> Path | None:
    """Backward-resolve: derive command name from skill directory name.

    Strips sc- prefix and -protocol suffix to derive candidate command name.
    """
    if commands_dir is None:
        return None

    dir_name = skill_dir.name
    # Strip sc- prefix
    name = dir_name
    if name.startswith("sc-"):
        name = name[3:]
    # Strip -protocol suffix
    if name.endswith("-protocol"):
        name = name[: -len("-protocol")]

    if not name:
        return None

    candidate = commands_dir / f"{name}.md"
    if candidate.exists() and candidate.is_file():
        return candidate
    return None


def _parse_activation_skill(content: str) -> str | None:
    """Parse ## Activation section for Skill sc:<name>-protocol reference.

    Returns the first matched skill directory name, or None.
    """
    in_activation = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("## Activation"):
            in_activation = True
            continue
        if in_activation and stripped.startswith("## "):
            break
        if in_activation and "Skill sc:" in stripped:
            # Extract the skill name after "Skill sc:"
            idx = stripped.index("Skill sc:") + len("Skill sc:")
            remainder = stripped[idx:].strip()
            # The skill name is the first word/token
            skill_ref = remainder.split()[0] if remainder else ""
            # Clean trailing punctuation
            skill_ref = skill_ref.rstrip(".,;:)")
            if skill_ref:
                # Convert to directory name: sc-<name>
                return f"sc-{skill_ref}"
    return None
