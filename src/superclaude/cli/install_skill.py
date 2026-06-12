"""
Skill Installation Command

Installs SuperClaude skills to ~/.claude/skills/ directory.
"""

import shutil
from pathlib import Path
from typing import List, Optional, Tuple


def install_skill_command(
    skill_name: str, target_path: Path, force: bool = False
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
        return (
            False,
            f"Skill '{skill_name}' already installed (use --force to reinstall)",
        )

    # Remove existing if force
    if skill_target.exists() and force:
        shutil.rmtree(skill_target)

    # Copy skill files
    try:
        shutil.copytree(skill_source, skill_target)
        return True, f"Skill '{skill_name}' installed successfully to {skill_target}"
    except Exception as e:
        return False, f"Failed to install skill: {e}"


def _get_skill_source_dirs() -> List[Path]:
    """
    Get candidate base directories containing skills

    Skills are stored in:
        1. package_root/skills/ (installed package)
        2. plugins/superclaude/skills/ (source checkout)

    Returns:
        List of existing base directories
    """
    package_root = Path(__file__).resolve().parent.parent

    candidates = [
        package_root / "skills",
        package_root.parent.parent / "plugins" / "superclaude" / "skills",
    ]

    return [base for base in candidates if base.exists()]


def _get_skill_source(skill_name: str) -> Optional[Path]:
    """
    Get source directory for skill

    Args:
        skill_name: Name of skill

    Returns:
        Path to skill source directory
    """
    skill_dirs: List[Path] = []
    normalized = skill_name.replace("-", "_")

    for base in _get_skill_source_dirs():
        skill_dirs.append(base / skill_name)
        skill_dirs.append(base / normalized)

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
    skills: List[str] = []
    seen: set[str] = set()

    for base in _get_skill_source_dirs():
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


def install_all_skills(
    target_path: Path, force: bool = False, only: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """
    Install all available skills (or a subset) to target directory

    Args:
        target_path: Target installation directory (e.g., ~/.claude/skills)
        force: Force reinstall if skills exist
        only: Optional list of skill names to restrict installation to

    Returns:
        Tuple of (success: bool, message: str)
    """
    available = list_available_skills()

    if only is not None:
        missing = [name for name in only if name not in available]
        if missing:
            return False, f"Skill(s) not found: {', '.join(missing)}"
        available = [name for name in available if name in only]

    if not available:
        return False, "No skills available to install"

    installed = []
    skipped = []
    failed = []

    for skill_name in available:
        success, message = install_skill_command(skill_name, target_path, force=force)
        if success:
            installed.append(skill_name)
        elif "already installed" in message:
            skipped.append(skill_name)
        else:
            failed.append(f"{skill_name}: {message}")

    messages = []

    if installed:
        messages.append(f"✅ Installed {len(installed)} skills:")
        for name in installed:
            messages.append(f"   - {name}")

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

    if not installed and not skipped:
        return False, "No skills were installed"

    messages.append(f"\n📁 Installation directory: {target_path}")

    return len(failed) == 0, "\n".join(messages)
