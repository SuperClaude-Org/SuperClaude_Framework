"""
SuperClaude Installation Suite
Pure Python installation system for SuperClaude framework
"""

from pathlib import Path

try:
    __version__ = (Path(__file__).parent.parent / "VERSION").read_text().strip()
except Exception:
    __version__ = "4.1.0"  # Fallback

__author__ = "NomenAK, Mithun Gowda B"

# Core paths
SETUP_DIR = Path(__file__).parent
PROJECT_ROOT = SETUP_DIR.parent
DATA_DIR = SETUP_DIR / "data"

# Installation target
DEFAULT_INSTALL_DIR = Path.home() / ".claude"