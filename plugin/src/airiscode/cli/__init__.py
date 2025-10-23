"""
SuperClaude CLI

Commands:
    - superclaude install-skill pm-agent  # Install PM Agent skill
    - superclaude doctor                   # Check installation health
    - superclaude version                  # Show version
"""

from .main import main

__all__ = ["main"]
