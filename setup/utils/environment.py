"""
Environment variable management for SuperClaude
Cross-platform utilities for setting up persistent environment variables
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from .ui import display_info, display_success, display_warning, Colors
from .logger import get_logger
from .paths import get_home_directory


def _get_env_tracking_file() -> Path:
    """Get path to environment variable tracking file"""
    from .. import DEFAULT_INSTALL_DIR

    install_dir = get_home_directory() / ".claude"
    install_dir.mkdir(exist_ok=True)
    return install_dir / "superclaude_env_vars.json"


def _load_env_tracking() -> Dict[str, Dict[str, str]]:
    """Load environment variable tracking data"""
    tracking_file = _get_env_tracking_file()

    try:
        if tracking_file.exists():
            with open(tracking_file, "r") as f:
                return json.load(f)
    except Exception as e:
        get_logger().warning(f"Could not load environment tracking: {e}")

    return {}


def _save_env_tracking(tracking_data: Dict[str, Dict[str, str]]) -> bool:
    """Save environment variable tracking data"""
    tracking_file = _get_env_tracking_file()

    try:
        with open(tracking_file, "w") as f:
            json.dump(tracking_data, f, indent=2)
        return True
    except Exception as e:
        get_logger().error(f"Could not save environment tracking: {e}")
        return False


def _add_env_tracking(env_vars: Dict[str, str]) -> None:
    """Add environment variables to tracking"""
    if not env_vars:
        return

    tracking_data = _load_env_tracking()
    timestamp = datetime.now().isoformat()

    for env_var, value in env_vars.items():
        tracking_data[env_var] = {
            "set_by": "superclaude",
            "timestamp": timestamp,
            "value_hash": str(hash(value)),  # Store hash, not actual value for security
        }

    _save_env_tracking(tracking_data)
    get_logger().info(f"Added {len(env_vars)} environment variables to tracking")


def _remove_env_tracking(env_vars: list) -> None:
    """Remove environment variables from tracking"""
    if not env_vars:
        return

    tracking_data = _load_env_tracking()

    for env_var in env_vars:
        if env_var in tracking_data:
            del tracking_data[env_var]

    _save_env_tracking(tracking_data)
    get_logger().info(f"Removed {len(env_vars)} environment variables from tracking")


def detect_shell_config() -> Optional[Path]:
    """
    Detect user's shell configuration file

    Returns:
        Path to the shell configuration file, or None if not found
    """
    home = get_home_directory()

    # Check in order of preference
    configs = [
        home / ".zshrc",  # Zsh (Mac default)
        home / ".bashrc",  # Bash
        home / ".profile",  # Generic shell profile
        home / ".bash_profile",  # Mac Bash profile
    ]

    for config in configs:
        if config.exists():
            return config

    # Default to .bashrc if none exist (will be created)
    return home / ".bashrc"


def setup_environment_variables(api_keys: Dict[str, str]) -> bool:
    """
    Set up environment variables across platforms

    Args:
        api_keys: Dictionary of environment variable names to values

    Returns:
        True if all variables were set successfully, False otherwise
    """
    logger = get_logger()
    success = True

    if not api_keys:
        return True

    print(f"\n{Colors.BLUE}[INFO] Setting up environment variables...{Colors.RESET}")

    for env_var, value in api_keys.items():
        try:
            # Set for current session
            os.environ[env_var] = value

            if os.name == "nt":  # Windows
                # Use setx for persistent user variable
                result = subprocess.run(
                    ["setx", env_var, value], capture_output=True, text=True
                )
                if result.returncode != 0:
                    display_warning(
                        f"Could not set {env_var} persistently: {result.stderr.strip()}"
                    )
                    success = False
                else:
                    logger.info(
                        f"Windows environment variable {env_var} set persistently"
                    )
            else:  # Unix-like systems
                shell_config = detect_shell_config()

                # Check if the export already exists
                export_line = f'export {env_var}="{value}"'

                try:
                    with open(shell_config, "r") as f:
                        content = f.read()

                    # Check if this environment variable is already set
                    if f"export {env_var}=" in content:
                        # Variable exists - don't duplicate
                        logger.info(
                            f"Environment variable {env_var} already exists in {shell_config.name}"
                        )
                    else:
                        # Append export to shell config
                        with open(shell_config, "a") as f:
                            f.write(f"\n# SuperClaude API Key\n{export_line}\n")

                        display_info(f"Added {env_var} to {shell_config.name}")
                        logger.info(f"Added {env_var} to {shell_config}")

                except Exception as e:
                    display_warning(f"Could not update {shell_config.name}: {e}")
                    success = False

            logger.info(
                f"Environment variable {env_var} configured for current session"
            )

        except Exception as e:
            logger.error(f"Failed to set {env_var}: {e}")
            display_warning(f"Failed to set {env_var}: {e}")
            success = False

    if success:
        # Add to tracking
        _add_env_tracking(api_keys)

        display_success("Environment variables configured successfully")
        if os.name != "nt":
            display_info(
                "Restart your terminal or run 'source ~/.bashrc' to apply changes"
            )
        else:
            display_info(
                "New environment variables will be available in new terminal sessions"
            )
    else:
        display_warning("Some environment variables could not be set persistently")
        display_info("You can set them manually or check the logs for details")

    return success


def validate_environment_setup(env_vars: Dict[str, str]) -> bool:
    """
    Validate that environment variables are properly set

    Args:
        env_vars: Dictionary of environment variable names to expected values

    Returns:
        True if all variables are set correctly, False otherwise
    """
    logger = get_logger()
    all_valid = True

    for env_var, expected_value in env_vars.items():
        current_value = os.environ.get(env_var)

        if current_value is None:
            logger.warning(f"Environment variable {env_var} is not set")
            all_valid = False
        elif current_value != expected_value:
            logger.warning(f"Environment variable {env_var} has unexpected value")
            all_valid = False
        else:
            logger.info(f"Environment variable {env_var} is set correctly")

    return all_valid


def get_shell_name() -> str:
    """
    Get the name of the current shell

    Returns:
        Name of the shell (e.g., 'bash', 'zsh', 'fish')
    """
    shell_path = os.environ.get("SHELL", "")
    if shell_path:
        return Path(shell_path).name
    return "unknown"


def get_superclaude_environment_variables() -> Dict[str, str]:
    """
    Get environment variables that were set by SuperClaude

    Returns:
        Dictionary of environment variable names to their current values
    """
    # Load tracking data to get SuperClaude-managed variables
    tracking_data = _load_env_tracking()

    found_vars = {}
    for env_var, metadata in tracking_data.items():
        if metadata.get("set_by") == "superclaude":
            value = os.environ.get(env_var)
            if value:
                found_vars[env_var] = value

    # Fallback: check known SuperClaude API key environment variables
    # (for backwards compatibility with existing installations)
    known_superclaude_env_vars = [
        "TWENTYFIRST_API_KEY",  # Magic server
        "MORPH_API_KEY",  # Morphllm server
    ]

    for env_var in known_superclaude_env_vars:
        if env_var not in found_vars:
            value = os.environ.get(env_var)
            if value:
                found_vars[env_var] = value

    return found_vars


def cleanup_environment_variables(
    env_vars_to_remove: Dict[str, str], create_restore_script: bool = True
) -> bool:
    """
    Safely remove environment variables with backup and restore options

    Args:
        env_vars_to_remove: Dictionary of environment variable names to remove
        create_restore_script: Whether to create a script to restore the variables

    Returns:
        True if cleanup was successful, False otherwise
    """
    logger = get_logger()
    success = True

    if not env_vars_to_remove:
        return True

    # Create restore script if requested
    if create_restore_script:
        restore_script_path = _create_restore_script(env_vars_to_remove)
        if restore_script_path:
            display_info(f"Created restore script: {restore_script_path}")
        else:
            display_warning("Could not create restore script")

    print(f"\n{Colors.BLUE}[INFO] Removing environment variables...{Colors.RESET}")

    for env_var, value in env_vars_to_remove.items():
        try:
            # Remove from current session
            if env_var in os.environ:
                del os.environ[env_var]
                logger.info(f"Removed {env_var} from current session")

            if os.name == "nt":  # Windows
                # Remove persistent user variable using reg command
                result = subprocess.run(
                    ["reg", "delete", "HKCU\\Environment", "/v", env_var, "/f"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    # Variable might not exist in registry, which is fine
                    logger.debug(
                        f"Registry deletion for {env_var}: {result.stderr.strip()}"
                    )
                else:
                    logger.info(f"Removed {env_var} from Windows registry")
            else:  # Unix-like systems
                shell_config = detect_shell_config()
                if shell_config and shell_config.exists():
                    _remove_env_var_from_shell_config(shell_config, env_var)

        except Exception as e:
            logger.error(f"Failed to remove {env_var}: {e}")
            display_warning(f"Could not remove {env_var}: {e}")
            success = False

    if success:
        # Remove from tracking
        _remove_env_tracking(list(env_vars_to_remove.keys()))

        display_success("Environment variables removed successfully")
        if os.name != "nt":
            display_info(
                "Restart your terminal or source your shell config to apply changes"
            )
        else:
            display_info("Changes will take effect in new terminal sessions")
    else:
        display_warning("Some environment variables could not be removed")

    return success


def _create_restore_script(env_vars: Dict[str, str]) -> Optional[Path]:
    """Create a script to restore environment variables"""
    try:
        home = get_home_directory()
        if os.name == "nt":  # Windows
            script_path = home / "restore_superclaude_env.bat"
            with open(script_path, "w") as f:
                f.write("@echo off\n")
                f.write("REM SuperClaude Environment Variable Restore Script\n")
                f.write("REM Generated during uninstall\n\n")
                for env_var, value in env_vars.items():
                    f.write(f'setx {env_var} "{value}"\n')
                f.write("\necho Environment variables restored\n")
                f.write("pause\n")
        else:  # Unix-like
            script_path = home / "restore_superclaude_env.sh"
            with open(script_path, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("# SuperClaude Environment Variable Restore Script\n")
                f.write("# Generated during uninstall\n\n")
                shell_config = detect_shell_config()
                for env_var, value in env_vars.items():
                    f.write(f'export {env_var}="{value}"\n')
                    if shell_config:
                        f.write(
                            f"echo 'export {env_var}=\"{value}\"' >> {shell_config}\n"
                        )
                f.write("\necho 'Environment variables restored'\n")

            # Make script executable
            script_path.chmod(0o755)

        return script_path

    except Exception as e:
        get_logger().error(f"Failed to create restore script: {e}")
        return None


def _remove_env_var_from_shell_config(shell_config: Path, env_var: str) -> bool:
    """Remove environment variable export from shell configuration file"""
    try:
        # Read current content
        with open(shell_config, "r") as f:
            lines = f.readlines()

        # Filter out lines that export this variable
        filtered_lines = []
        skip_next_blank = False

        for line in lines:
            # Check if this line exports our variable
            if f"export {env_var}=" in line or line.strip() == f"# SuperClaude API Key":
                skip_next_blank = True
                continue

            # Skip blank line after removed export
            if skip_next_blank and line.strip() == "":
                skip_next_blank = False
                continue

            skip_next_blank = False
            filtered_lines.append(line)

        # Write back the filtered content
        with open(shell_config, "w") as f:
            f.writelines(filtered_lines)

        get_logger().info(f"Removed {env_var} export from {shell_config.name}")
        return True

    except Exception as e:
        get_logger().error(f"Failed to remove {env_var} from {shell_config}: {e}")
        return False


def create_env_file(
    api_keys: Dict[str, str], env_file_path: Optional[Path] = None
) -> bool:
    """
    Create a .env file with the API keys (alternative to shell config)

    Args:
        api_keys: Dictionary of environment variable names to values
        env_file_path: Path to the .env file (defaults to home directory)

    Returns:
        True if .env file was created successfully, False otherwise
    """
    if env_file_path is None:
        env_file_path = get_home_directory() / ".env"

    logger = get_logger()

    try:
        # Read existing .env file if it exists
        existing_content = ""
        if env_file_path.exists():
            with open(env_file_path, "r") as f:
                existing_content = f.read()

        # Prepare new content
        new_lines = []
        for env_var, value in api_keys.items():
            line = f'{env_var}="{value}"'

            # Check if this variable already exists
            if f"{env_var}=" in existing_content:
                logger.info(f"Variable {env_var} already exists in .env file")
            else:
                new_lines.append(line)

        # Append new lines if any
        if new_lines:
            with open(env_file_path, "a") as f:
                if existing_content and not existing_content.endswith("\n"):
                    f.write("\n")
                f.write("# SuperClaude API Keys\n")
                for line in new_lines:
                    f.write(line + "\n")

            # Set file permissions (readable only by owner)
            env_file_path.chmod(0o600)

            display_success(f"Created .env file at {env_file_path}")
            logger.info(f"Created .env file with {len(new_lines)} new variables")

        return True

    except Exception as e:
        logger.error(f"Failed to create .env file: {e}")
        display_warning(f"Could not create .env file: {e}")
        return False


def check_research_prerequisites() -> tuple[bool, list[str]]:
    """
    Check if deep research prerequisites are met

    Returns:
        Tuple of (success: bool, warnings: List[str])
    """
    warnings = []
    logger = get_logger()

    # Check Tavily API key
    if not os.environ.get("TAVILY_API_KEY"):
        warnings.append(
            "TAVILY_API_KEY not set - Deep research web search will not work\n"
            "Get your key from: https://app.tavily.com"
        )
        logger.warning("TAVILY_API_KEY not found in environment")
    else:
        logger.info("Found TAVILY_API_KEY in environment")

    # Check Node.js for MCP
    import shutil

    if not shutil.which("node"):
        warnings.append(
            "Node.js not found - Required for Tavily MCP\n"
            "Install from: https://nodejs.org"
        )
        logger.warning("Node.js not found - required for Tavily MCP")
    else:
        logger.info("Node.js found")

    # Check npm
    if not shutil.which("npm"):
        warnings.append(
            "npm not found - Required for MCP server installation\n"
            "Usually installed with Node.js"
        )
        logger.warning("npm not found - required for MCP installation")
    else:
        logger.info("npm found")

    return len(warnings) == 0, warnings
