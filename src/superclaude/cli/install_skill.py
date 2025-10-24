"""
Skill Installation Command

Installs SuperClaude skills to ~/.claude/skills/ directory.
"""

from pathlib import Path
from typing import List, Optional, Tuple
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


def _get_skill_source(skill_name: str) -> Optional[Path]:
    """
    Get source directory for skill

    Skills are stored in:
        src/superclaude/skills/{skill_name}/

    Args:
        skill_name: Name of skill

    Returns:
        Path to skill source directory
    """
    package_root = Path(__file__).resolve().parent.parent
    skill_dirs: List[Path] = []

    def _candidate_paths(base: Path) -> List[Path]:
        if not base.exists():
            return []
        normalized = skill_name.replace("-", "_")
        return [
            base / skill_name,
            base / normalized,
        ]

    # Packaged skills (src/superclaude/skills/…)
    skill_dirs.extend(_candidate_paths(package_root / "skills"))

    # Repository root skills/ when running from source checkout
    repo_root = package_root.parent  # -> src/
    if repo_root.name == "src":
        project_root = repo_root.parent
        skill_dirs.extend(_candidate_paths(project_root / "skills"))

    for candidate in skill_dirs:
        if _is_valid_skill_dir(candidate):
            return candidate

    return None


def _is_valid_skill_dir(path: Path) -> bool:
    """Return True if directory looks like a SuperClaude skill payload."""
    if not path or not path.exists() or not path.is_dir():
        return False

    manifest_files = {"SKILL.md", "skill.md", "implementation.md"}
    if any((path / manifest).exists() for manifest in manifest_files):
        return True

    # Otherwise check for any content files (ts/py/etc.)
    for item in path.iterdir():
        if item.is_file() and item.suffix in {".ts", ".js", ".py", ".json"}:
            return True
    return False


def list_available_skills() -> list[str]:
    """
    List all available skills

    Returns:
        List of skill names
    """
    package_root = Path(__file__).resolve().parent.parent
    candidate_dirs = [
        package_root / "skills",
    ]

    repo_root = package_root.parent
    if repo_root.name == "src":
        candidate_dirs.append(repo_root.parent / "skills")

    skills: List[str] = []
    seen: set[str] = set()

    for base in candidate_dirs:
        if not base.exists():
            continue
        for item in base.iterdir():
            if not item.is_dir() or item.name.startswith("_"):
                continue
            if not _is_valid_skill_dir(item):
                continue

            # Prefer kebab-case names as canonical
            canonical = item.name.replace("_", "-")
            if canonical not in seen:
                seen.add(canonical)
                skills.append(canonical)

    skills.sort()
    return skills
