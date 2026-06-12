"""
Agent Installation

Installs SuperClaude agent definitions to ~/.claude/agents/ directory.
"""

import shutil
from pathlib import Path
from typing import List, Tuple


def _get_agents_source() -> Path:
    """
    Get source directory for agent files

    Agents are stored in:
        1. package_root/agents/ (installed package)
        2. plugins/superclaude/agents/ (source checkout)

    Returns:
        Path to agents source directory
    """
    package_root = Path(__file__).resolve().parent.parent

    # Priority 1: agents/ in package
    package_agents_dir = package_root / "agents"
    if package_agents_dir.exists():
        return package_agents_dir

    # Priority 2: plugins/superclaude/agents/ in project root
    repo_root = package_root.parent.parent
    plugins_agents_dir = repo_root / "plugins" / "superclaude" / "agents"
    if plugins_agents_dir.exists():
        return plugins_agents_dir

    return package_agents_dir


def install_agents(target_path: Path = None, force: bool = False) -> Tuple[bool, str]:
    """
    Install SuperClaude agent files to ~/.claude/agents/

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

    agent_files = [f for f in agent_source.glob("*.md") if f.stem != "README"]

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
            messages.append(f"   - @{name}")

    if skipped:
        messages.append(
            f"\n⚠️  Skipped {len(skipped)} existing agents (use --force to reinstall):"
        )
        for name in skipped:
            messages.append(f"   - @{name}")

    if failed:
        messages.append(f"\n❌ Failed to install {len(failed)} agents:")
        for fail in failed:
            messages.append(f"   - {fail}")

    if not installed and not skipped:
        return False, "No agents were installed"

    messages.append(f"\n📁 Installation directory: {target_path}")

    return len(failed) == 0, "\n".join(messages)


def list_available_agents() -> List[str]:
    """List all available agent files"""
    agent_source = _get_agents_source()
    if not agent_source.exists():
        return []

    return sorted(f.stem for f in agent_source.glob("*.md") if f.stem != "README")
