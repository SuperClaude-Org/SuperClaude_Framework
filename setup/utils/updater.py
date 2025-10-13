"""
Auto-update checker for SuperClaude Framework
Checks PyPI for newer versions and offers automatic updates
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from packaging import version
import urllib.request
import urllib.error
from datetime import datetime, timedelta

from .ui import display_info, display_warning, display_success, Colors
from .logger import get_logger
from .paths import get_home_directory


class UpdateChecker:
    """Handles automatic update checking for SuperClaude"""

    PYPI_URL = "https://pypi.org/pypi/superclaude/json"
    CACHE_FILE = get_home_directory() / ".claude" / ".update_check"
    CHECK_INTERVAL = 86400  # 24 hours in seconds
    TIMEOUT = 2  # seconds

    def __init__(self, current_version: str):
        """
        Initialize update checker

        Args:
            current_version: Current installed version
        """
        self.current_version = current_version
        self.logger = get_logger()

    def should_check_update(self, force: bool = False) -> bool:
        """
        Determine if we should check for updates based on last check time

        Args:
            force: Force check regardless of last check time

        Returns:
            True if update check should be performed
        """
        if force:
            return True

        if not self.CACHE_FILE.exists():
            return True

        try:
            with open(self.CACHE_FILE, "r") as f:
                data = json.load(f)
                last_check = data.get("last_check", 0)

            # Check if 24 hours have passed
            if time.time() - last_check > self.CHECK_INTERVAL:
                return True

        except (json.JSONDecodeError, KeyError):
            return True

        return False

    def save_check_timestamp(self):
        """Save the current timestamp as last check time"""
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE, "r") as f:
                    data = json.load(f)
            except:
                pass

        data["last_check"] = time.time()

        with open(self.CACHE_FILE, "w") as f:
            json.dump(data, f)

    def get_latest_version(self) -> Optional[str]:
        """
        Query PyPI for the latest version of SuperClaude

        Returns:
            Latest version string or None if check fails
        """
        try:
            # Create request with timeout
            req = urllib.request.Request(
                self.PYPI_URL, headers={"User-Agent": "superclaude-Updater"}
            )

            # Set timeout for the request
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as response:
                data = json.loads(response.read().decode())
                latest = data.get("info", {}).get("version")

            if self.logger:
                self.logger.debug(f"Latest PyPI version: {latest}")

            return latest

        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            json.JSONDecodeError,
        ) as e:
            if self.logger:
                self.logger.debug(f"Failed to check PyPI: {e}")
            return None
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Unexpected error checking updates: {e}")
            return None

    def compare_versions(self, latest: str) -> bool:
        """
        Compare current version with latest version

        Args:
            latest: Latest version string

        Returns:
            True if update is available
        """
        try:
            return version.parse(latest) > version.parse(self.current_version)
        except Exception:
            return False

    def detect_installation_method(self) -> str:
        """
        Detect how SuperClaude was installed (pip, pipx, etc.)

        Returns:
            Installation method string
        """
        # Check pipx first
        try:
            result = subprocess.run(
                ["pipx", "list"], capture_output=True, text=True, timeout=2
            )
            if "superclaude" in result.stdout or "superclaude" in result.stdout:
                return "pipx"
        except:
            pass

        # Check if pip installation exists
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "superclaude"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                # Check if it's a user installation
                if "--user" in result.stdout or get_home_directory() in Path(
                    result.stdout
                ):
                    return "pip-user"
                return "pip"
        except:
            pass

        return "unknown"

    def get_update_command(self) -> str:
        """
        Get the appropriate update command based on installation method

        Returns:
            Update command string
        """
        method = self.detect_installation_method()

        commands = {
            "pipx": "pipx upgrade SuperClaude",
            "pip-user": "pip install --upgrade --user SuperClaude",
            "pip": "pip install --upgrade SuperClaude",
            "unknown": "pip install --upgrade SuperClaude",
        }

        return commands.get(method, commands["unknown"])

    def show_update_banner(self, latest: str, auto_update: bool = False) -> bool:
        """
        Display update available banner

        Args:
            latest: Latest version available
            auto_update: Whether to auto-update without prompting

        Returns:
            True if user wants to update
        """
        update_cmd = self.get_update_command()

        # Display banner
        print(
            f"\n{Colors.CYAN}+================================================+{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}║{Colors.YELLOW}  🚀 Update Available: {self.current_version} → {latest}        {Colors.CYAN}║{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}║{Colors.GREEN}  Run: {update_cmd:<30} {Colors.CYAN}║{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}+================================================+{Colors.RESET}\n"
        )

        if auto_update:
            return True

        # Check if running in non-interactive mode
        if not sys.stdin.isatty():
            return False

        # Prompt user
        try:
            response = (
                input(
                    f"{Colors.YELLOW}Would you like to update now? (y/N): {Colors.RESET}"
                )
                .strip()
                .lower()
            )
            return response in ["y", "yes"]
        except (EOFError, KeyboardInterrupt):
            return False

    def perform_update(self) -> bool:
        """
        Execute the update command

        Returns:
            True if update succeeded
        """
        update_cmd = self.get_update_command()

        print(f"{Colors.CYAN}🔄 Updating superclaude...{Colors.RESET}")

        try:
            result = subprocess.run(update_cmd.split(), capture_output=False, text=True)

            if result.returncode == 0:
                display_success("Update completed successfully!")
                print(
                    f"{Colors.YELLOW}Please restart SuperClaude to use the new version.{Colors.RESET}"
                )
                return True
            else:
                display_warning("Update failed. Please run manually:")
                print(f"  {update_cmd}")
                return False

        except Exception as e:
            display_warning(f"Could not auto-update: {e}")
            print(f"Please run manually: {update_cmd}")
            return False

    def check_and_notify(self, force: bool = False, auto_update: bool = False) -> bool:
        """
        Main method to check for updates and notify user

        Args:
            force: Force check regardless of last check time
            auto_update: Automatically update if available

        Returns:
            True if update was performed
        """
        # Check if we should skip based on environment variable
        if os.getenv("SUPERCLAUDE_NO_UPDATE_CHECK", "").lower() in ["true", "1", "yes"]:
            return False

        # Check if auto-update is enabled via environment
        if os.getenv("SUPERCLAUDE_AUTO_UPDATE", "").lower() in ["true", "1", "yes"]:
            auto_update = True

        # Check if enough time has passed
        if not self.should_check_update(force):
            return False

        # Get latest version
        latest = self.get_latest_version()
        if not latest:
            return False

        # Save timestamp
        self.save_check_timestamp()

        # Compare versions
        if not self.compare_versions(latest):
            return False

        # Show banner and potentially update
        if self.show_update_banner(latest, auto_update):
            return self.perform_update()

        return False


def check_for_updates(current_version: str = None, **kwargs) -> bool:
    """
    Convenience function to check for updates

    Args:
        current_version: Current installed version (defaults to reading from setup)
        **kwargs: Additional arguments passed to check_and_notify

    Returns:
        True if update was performed
    """
    if current_version is None:
        from setup import __version__

        current_version = __version__
    checker = UpdateChecker(current_version)
    return checker.check_and_notify(**kwargs)
