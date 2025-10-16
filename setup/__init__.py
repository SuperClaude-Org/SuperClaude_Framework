"""
SuperClaude Installation Suite
Pure Python installation system for SuperClaude framework
"""

from pathlib import Path

try:
    __version__ = (Path(__file__).parent.parent / "VERSION").read_text().strip()
except Exception:
    __version__ = "4.1.6"  # Fallback - Deep Research Integration

__author__ = "NomenAK, Mithun Gowda B"

# Core paths
SETUP_DIR = Path(__file__).parent
PROJECT_ROOT = SETUP_DIR.parent
DATA_DIR = SETUP_DIR / "data"

# Import home directory detection for immutable distros
from .utils.paths import get_home_directory

# Installation target - SuperClaude components installed in subdirectory
DEFAULT_INSTALL_DIR = get_home_directory() / ".claude" / "superclaude"
