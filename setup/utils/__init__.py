"""Utility modules for SuperClaude installation system

Note: UI utilities (ProgressBar, Menu, confirm, Colors) have been removed.
The new CLI uses typer + rich natively via superclaude/cli/
"""

from .logger import Logger
from .security import SecurityValidator

__all__ = ["Logger", "SecurityValidator"]
