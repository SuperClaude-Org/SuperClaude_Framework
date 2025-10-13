"""
Path utilities for SuperClaude installation system
Handles cross-platform path operations and immutable distro support
"""

import os
from pathlib import Path


def get_home_directory() -> Path:
    """
    Get the correct home directory path, handling immutable distros.

    On immutable distros like Fedora Silverblue/Universal Blue,
    the home directory is at /var/home/$USER instead of /home/$USER.
    This function properly detects the actual home directory.

    Returns:
        Path: The actual home directory path
    """
    # First try the standard method
    try:
        home = Path.home()
        # Verify the path actually exists and is accessible
        if home.exists() and home.is_dir():
            return home
    except Exception:
        pass

    # Fallback methods for edge cases and immutable distros

    # Method 1: Use $HOME environment variable
    home_env = os.environ.get("HOME")
    if home_env:
        home_path = Path(home_env)
        if home_path.exists() and home_path.is_dir():
            return home_path

    # Method 2: Check for immutable distro patterns
    username = os.environ.get("USER") or os.environ.get("USERNAME")
    if username:
        # Check common immutable distro paths
        immutable_paths = [
            Path(f"/var/home/{username}"),  # Fedora Silverblue/Universal Blue
            Path(f"/home/{username}"),  # Standard Linux
        ]

        for path in immutable_paths:
            if path.exists() and path.is_dir():
                return path

    # Method 3: Last resort - use the original Path.home() even if it seems wrong
    # This ensures we don't crash the installation
    return Path.home()
