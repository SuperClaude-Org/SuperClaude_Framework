"""
SuperClaude CLI

Commands:
    - superclaude install                  # Install all components (core, commands, agents, skills)
    - superclaude update                   # Update all components to latest version
    - superclaude install-skill <name>     # Install a single skill
    - superclaude mcp                      # Install MCP servers
    - superclaude doctor                   # Check installation health
    - superclaude version                  # Show version
"""

from .main import main

__all__ = ["main"]
