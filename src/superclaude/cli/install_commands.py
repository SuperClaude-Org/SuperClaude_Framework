"""
Command Installation

Installs SuperClaude slash commands to ~/.claude/commands/sc/ directory.
"""

import shutil
from pathlib import Path
from typing import List, Tuple


def install_commands(target_path: Path = None, force: bool = False) -> Tuple[bool, str]:
    """
    Install all SuperClaude commands to Claude Code

    Args:
        target_path: Target installation directory (default: ~/.claude/commands/sc)
        force: Force reinstall if commands exist

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Default to ~/.claude/commands/sc to maintain /sc: namespace
    if target_path is None:
        target_path = Path.home() / ".claude" / "commands" / "sc"

    # Get command source directory
    command_source = _get_commands_source()

    if not command_source or not command_source.exists():
        return False, f"Command source directory not found: {command_source}"

    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)

    # Get all command files
    command_files = list(command_source.glob("*.md"))

    if not command_files:
        return False, f"No command files found in {command_source}"

    installed_commands = []
    skipped_commands = []
    failed_commands = []

    for command_file in command_files:
        target_file = target_path / command_file.name
        command_name = command_file.stem

        # Check if already exists
        if target_file.exists() and not force:
            skipped_commands.append(command_name)
            continue

        # Copy command file
        try:
            shutil.copy2(command_file, target_file)
            installed_commands.append(command_name)
        except Exception as e:
            failed_commands.append(f"{command_name}: {e}")

    # Build result message
    messages = []

    if installed_commands:
        messages.append(f"✅ Installed {len(installed_commands)} commands:")
        for cmd in installed_commands:
            messages.append(f"   - /{cmd}")

    if skipped_commands:
        messages.append(
            f"\n⚠️  Skipped {len(skipped_commands)} existing commands (use --force to reinstall):"
        )
        for cmd in skipped_commands:
            messages.append(f"   - /{cmd}")

    if failed_commands:
        messages.append(f"\n❌ Failed to install {len(failed_commands)} commands:")
        for fail in failed_commands:
            messages.append(f"   - {fail}")

    if not installed_commands and not skipped_commands:
        return False, "No commands were installed"

    messages.append(f"\n📁 Installation directory: {target_path}")
    messages.append("\n💡 Tip: Restart Claude Code to use the new commands")

    success = len(failed_commands) == 0
    return success, "\n".join(messages)


def _get_commands_source() -> Path:
    """
    Get source directory for commands

    Commands are stored in:
        1. package_root/commands/ (installed package)
        2. plugins/superclaude/commands/ (source checkout)

    Returns:
        Path to commands source directory
    """
    # Get package root (superclaude/ when installed, src/superclaude/ in dev)
    package_root = Path(__file__).resolve().parent.parent

    # Priority 1: Try commands/ in package (for installed package via pipx/pip)
    # This will be site-packages/superclaude/commands/
    package_commands_dir = package_root / "commands"
    if package_commands_dir.exists():
        return package_commands_dir

    # Priority 2: Try plugins/superclaude/commands/ in project root (for source checkout)
    # package_root = src/superclaude/
    # repo_root = src/superclaude/../../ = project root
    repo_root = package_root.parent.parent
    plugins_commands_dir = repo_root / "plugins" / "superclaude" / "commands"

    if plugins_commands_dir.exists():
        return plugins_commands_dir

    # If neither exists, return package location (will fail with clear error)
    return package_commands_dir


def list_available_commands() -> List[str]:
    """
    List all available commands

    Returns:
        List of command names
    """
    command_source = _get_commands_source()

    if not command_source.exists():
        return []

    commands = []
    for file in command_source.glob("*.md"):
        if file.stem != "README":
            commands.append(file.stem)

    return sorted(commands)


def list_installed_commands() -> List[str]:
    """
    List installed commands in ~/.claude/commands/sc/

    Returns:
        List of installed command names
    """
    commands_dir = Path.home() / ".claude" / "commands" / "sc"

    if not commands_dir.exists():
        return []

    installed = []
    for file in commands_dir.glob("*.md"):
        if file.stem != "README":
            installed.append(file.stem)

    return sorted(installed)
