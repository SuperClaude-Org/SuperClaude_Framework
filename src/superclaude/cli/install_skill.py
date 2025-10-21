"""
Skill Installation Command

Installs SuperClaude skills to ~/.claude/skills/ directory.
"""

from pathlib import Path
from typing import Tuple
import shutil


def install_skill_command(
    skill_name: str,
    target_path: Path,
    force: bool = False
) -> Tuple[bool, str]:
    """
    Install a skill to target directory

    Args:
        skill_name: Name of skill to install (e.g., 'pm-agent')
        target_path: Target installation directory
        force: Force reinstall if skill exists

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Get skill source directory
    skill_source = _get_skill_source(skill_name)

    if not skill_source:
        return False, f"Skill '{skill_name}' not found"

    if not skill_source.exists():
        return False, f"Skill source directory not found: {skill_source}"

    # Create target directory
    skill_target = target_path / skill_name
    target_path.mkdir(parents=True, exist_ok=True)

    # Check if skill already installed
    if skill_target.exists() and not force:
        return False, f"Skill '{skill_name}' already installed (use --force to reinstall)"

    # Remove existing if force
    if skill_target.exists() and force:
        shutil.rmtree(skill_target)

    # Copy skill files
    try:
        shutil.copytree(skill_source, skill_target)
        return True, f"Skill '{skill_name}' installed successfully to {skill_target}"
    except Exception as e:
        return False, f"Failed to install skill: {e}"


def _get_skill_source(skill_name: str) -> Path:
    """
    Get source directory for skill

    Skills are stored in:
        src/superclaude/skills/{skill_name}/

    Args:
        skill_name: Name of skill

    Returns:
        Path to skill source directory
    """
    # Get package root
    package_root = Path(__file__).parent.parent

    # Skill source directory
    skill_source = package_root / "skills" / skill_name

    return skill_source if skill_source.exists() else None


def list_available_skills() -> list[str]:
    """
    List all available skills

    Returns:
        List of skill names
    """
    package_root = Path(__file__).parent.parent
    skills_dir = package_root / "skills"

    if not skills_dir.exists():
        return []

    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            # Check if skill has implementation.md
            if (item / "implementation.md").exists():
                skills.append(item.name)

    return skills
