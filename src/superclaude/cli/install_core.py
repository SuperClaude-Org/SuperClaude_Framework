"""
Core Framework Installation

Installs SuperClaude core framework files to ~/.claude/ directory.
These are the behavioral instruction files that Claude Code reads on startup.
"""

import shutil
from pathlib import Path
from typing import List, Tuple


def install_core_files(
    target_path: Path = None, force: bool = False
) -> Tuple[bool, str]:
    """
    Install SuperClaude core framework files to Claude Code config directory.

    Copies all .md files from src/superclaude/core/ to ~/.claude/,
    providing the behavioral instructions that power the SuperClaude framework.

    Args:
        target_path: Target installation directory (default: ~/.claude)
        force: Force overwrite if files already exist

    Returns:
        Tuple of (success: bool, message: str)
    """
    if target_path is None:
        target_path = Path.home() / ".claude"

    core_source = _get_core_source()

    if not core_source or not core_source.exists():
        return False, f"Core source directory not found: {core_source}"

    target_path.mkdir(parents=True, exist_ok=True)

    core_files = sorted(core_source.glob("*.md"))

    if not core_files:
        return False, f"No core framework files found in {core_source}"

    installed = []
    skipped = []
    failed = []

    for src_file in core_files:
        dest_file = target_path / src_file.name

        if dest_file.exists() and not force:
            skipped.append(src_file.name)
            continue

        try:
            shutil.copy2(src_file, dest_file)
            installed.append(src_file.name)
        except Exception as e:
            failed.append(f"{src_file.name}: {e}")

    messages = []

    if installed:
        messages.append(f"✅ Installed {len(installed)} core framework files:")
        for name in installed:
            messages.append(f"   - {name}")

    if skipped:
        messages.append(
            f"\n⚠️  Skipped {len(skipped)} existing files (use --force to overwrite):"
        )
        for name in skipped:
            messages.append(f"   - {name}")

    if failed:
        messages.append(f"\n❌ Failed to install {len(failed)} files:")
        for fail in failed:
            messages.append(f"   - {fail}")

    if not installed and not skipped:
        return False, "No core framework files were installed"

    messages.append(f"\n📁 Installation directory: {target_path}")

    success = len(failed) == 0
    return success, "\n".join(messages)


def _get_core_source() -> Path:
    """
    Get source directory for core framework files.

    Core files are stored in:
        1. package_root/core/ (installed package)
        2. src/superclaude/core/ (source checkout)

    Returns:
        Path to core source directory
    """
    package_root = Path(__file__).resolve().parent.parent

    # Priority 1: core/ in package (for installed package via pipx/pip)
    package_core_dir = package_root / "core"
    if package_core_dir.exists():
        return package_core_dir

    # If neither exists, return package location (will fail with clear error)
    return package_core_dir


def list_core_files() -> List[str]:
    """
    List all available core framework files.

    Returns:
        List of core file names
    """
    core_source = _get_core_source()

    if not core_source.exists():
        return []

    return sorted(f.name for f in core_source.glob("*.md"))


def list_installed_core_files() -> List[str]:
    """
    List core framework files installed in ~/.claude/

    Returns:
        List of installed core file names
    """
    claude_dir = Path.home() / ".claude"

    if not claude_dir.exists():
        return []

    # Only check for known core files, not all .md files in ~/.claude/
    known_core = {
        "CLAUDE.md",
        "COMMANDS.md",
        "FLAGS.md",
        "PRINCIPLES.md",
        "RULES.md",
        "MCP.md",
        "PERSONAS.md",
        "ORCHESTRATOR.md",
        "MODES.md",
        "BUSINESS_PANEL_EXAMPLES.md",
        "BUSINESS_SYMBOLS.md",
        "RESEARCH_CONFIG.md",
    }

    return sorted(f.name for f in claude_dir.glob("*.md") if f.name in known_core)
