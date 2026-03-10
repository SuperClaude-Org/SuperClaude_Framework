"""
Agent Installation

Installs SuperClaude agent definitions to ~/.claude/agents/ directory.
"""

import shutil
from pathlib import Path
from typing import List, Tuple

# Files to exclude from installation
_EXCLUDE_FILES = {"README.md", "__init__.py"}


def install_agents(
    target_path: Path = None, force: bool = False
) -> Tuple[bool, str]:
    """
    Install all SuperClaude agent definitions to Claude Code

    Args:
        target_path: Target installation directory (default: ~/.claude/agents)
        force: Force reinstall if agents exist

    Returns:
        Tuple of (success: bool, message: str)
    """
    if target_path is None:
        target_path = Path.home() / ".claude" / "agents"

    agent_source = _get_agents_source()

    if not agent_source or not agent_source.exists():
        return False, f"Agent source directory not found: {agent_source}"

    target_path.mkdir(parents=True, exist_ok=True)

    agent_files = [
        f
        for f in sorted(agent_source.glob("*.md"))
        if f.name not in _EXCLUDE_FILES
    ]

    if not agent_files:
        return False, f"No agent files found in {agent_source}"

    installed = []
    skipped = []
    failed = []

    for agent_file in agent_files:
        target_file = target_path / agent_file.name
        agent_name = agent_file.stem

        if target_file.exists() and not force:
            skipped.append(agent_name)
            continue

        try:
            shutil.copy2(agent_file, target_file)
            installed.append(agent_name)
        except Exception as e:
            failed.append(f"{agent_name}: {e}")

    messages = []

    if installed:
        messages.append(f"✅ Installed {len(installed)} agents:")
        for name in installed:
            messages.append(f"   - {name}")

    if skipped:
        messages.append(
            f"\n⚠️  Skipped {len(skipped)} existing agents (use --force to reinstall):"
        )
        for name in skipped:
            messages.append(f"   - {name}")

    if failed:
        messages.append(f"\n❌ Failed to install {len(failed)} agents:")
        for fail in failed:
            messages.append(f"   - {fail}")

    if not installed and not skipped:
        return False, "No agents were installed"

    messages.append(f"\n📁 Installation directory: {target_path}")

    success = len(failed) == 0
    return success, "\n".join(messages)


def _get_agents_source() -> Path:
    """
    Get source directory for agent definitions.

    Agents are stored in:
        1. package_root/agents/ (installed package)
        2. src/superclaude/agents/ (source checkout)

    Returns:
        Path to agents source directory
    """
    package_root = Path(__file__).resolve().parent.parent

    # Priority 1: agents/ in package (for installed package via pipx/pip)
    package_agents_dir = package_root / "agents"
    if package_agents_dir.exists():
        return package_agents_dir

    # If not found, return package location (will fail with clear error)
    return package_agents_dir


def list_available_agents() -> List[str]:
    """
    List all available agent definitions.

    Returns:
        List of agent names
    """
    agent_source = _get_agents_source()

    if not agent_source.exists():
        return []

    return sorted(
        f.stem
        for f in agent_source.glob("*.md")
        if f.name not in _EXCLUDE_FILES
    )


def list_installed_agents() -> List[str]:
    """
    List agent definitions installed in ~/.claude/agents/

    Returns:
        List of installed agent names
    """
    agents_dir = Path.home() / ".claude" / "agents"

    if not agents_dir.exists():
        return []

    return sorted(
        f.stem
        for f in agents_dir.glob("*.md")
        if f.name not in _EXCLUDE_FILES
    )
