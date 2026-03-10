"""
Batch Skill Installation

Installs all SuperClaude skills to ~/.claude/skills/ directory.
Wraps the single-skill installer for batch operation during `superclaude install`.

Skills whose directory name starts with "sc-" and have a corresponding
slash command (e.g. sc-roadmap → commands/roadmap.md) are served via
/sc:<name> commands and are NOT installed as separate skills to avoid
duplicate autocomplete entries.
"""

from pathlib import Path
from typing import List, Tuple

from .install_skill import install_skill_command, list_available_skills


def _has_corresponding_command(skill_name: str) -> bool:
    """Check if an sc-* skill has a matching slash command.

    For example, skill "sc-roadmap" has a command if
    src/superclaude/commands/roadmap.md exists.
    """
    if not skill_name.startswith("sc-"):
        return False
    cmd_name = skill_name[3:]  # strip "sc-" prefix
    package_root = Path(__file__).resolve().parent.parent
    return (package_root / "commands" / f"{cmd_name}.md").exists()


def install_all_skills(
    target_path: Path = None, force: bool = False
) -> Tuple[bool, str]:
    """
    Install all available SuperClaude skills to Claude Code

    Args:
        target_path: Target installation directory (default: ~/.claude/skills)
        force: Force reinstall if skills exist

    Returns:
        Tuple of (success: bool, message: str)
    """
    if target_path is None:
        target_path = Path.home() / ".claude" / "skills"

    available = list_available_skills()

    if not available:
        return True, "No skills available to install"

    installed = []
    skipped = []
    failed = []
    served_by_command = []

    for skill_name in available:
        # Skip sc-* skills that have a corresponding /sc: command
        if _has_corresponding_command(skill_name):
            served_by_command.append(skill_name)
            # Remove stale install if present
            stale = target_path / skill_name
            if stale.exists():
                import shutil

                shutil.rmtree(stale)
            continue

        skill_target = target_path / skill_name

        if skill_target.exists() and not force:
            skipped.append(skill_name)
            continue

        success, message = install_skill_command(
            skill_name=skill_name,
            target_path=target_path,
            force=force,
        )

        if success:
            installed.append(skill_name)
        else:
            failed.append(f"{skill_name}: {message}")

    messages = []

    if installed:
        messages.append(f"✅ Installed {len(installed)} skills:")
        for name in installed:
            messages.append(f"   - {name}")

    if served_by_command:
        messages.append(
            f"\n⏭️  {len(served_by_command)} skills served by /sc: commands (not installed as skills):"
        )
        for name in served_by_command:
            cmd_name = name[3:]  # strip "sc-" prefix
            messages.append(f"   - {name} → /sc:{cmd_name}")

    if skipped:
        messages.append(
            f"\n⚠️  Skipped {len(skipped)} existing skills (use --force to reinstall):"
        )
        for name in skipped:
            messages.append(f"   - {name}")

    if failed:
        messages.append(f"\n❌ Failed to install {len(failed)} skills:")
        for fail in failed:
            messages.append(f"   - {fail}")

    if not installed and not skipped and not served_by_command:
        return True, "No skills to install"

    messages.append(f"\n📁 Installation directory: {target_path}")

    success = len(failed) == 0
    return success, "\n".join(messages)


def list_installed_skills() -> List[str]:
    """
    List skills installed in ~/.claude/skills/

    Returns:
        List of installed skill names
    """
    skills_dir = Path.home() / ".claude" / "skills"

    if not skills_dir.exists():
        return []

    installed = []
    for item in skills_dir.iterdir():
        if not item.is_dir() or item.name.startswith("_"):
            continue
        # Check for SKILL.md or skill.md as indicator
        if any((item / m).exists() for m in ("SKILL.md", "skill.md")):
            installed.append(item.name)

    return sorted(installed)
