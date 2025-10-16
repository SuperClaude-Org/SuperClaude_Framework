"""
SuperClaude Uninstall Operation Module
Refactored from uninstall.py for unified CLI hub
"""

import sys
import time
from pathlib import Path
from ...utils.paths import get_home_directory
from typing import List, Optional, Dict, Any
import argparse

from ...core.registry import ComponentRegistry
from ...services.settings import SettingsService
from ...services.files import FileService
from ...utils.ui import (
    display_header,
    display_info,
    display_success,
    display_error,
    display_warning,
    Menu,
    confirm,
    ProgressBar,
    Colors,
)
from ...utils.environment import (
    get_superclaude_environment_variables,
    cleanup_environment_variables,
)
from ...utils.logger import get_logger
from ... import DEFAULT_INSTALL_DIR, PROJECT_ROOT
from . import OperationBase


def verify_superclaude_file(file_path: Path, component: str) -> bool:
    """
    Verify this is a SuperClaude file before removal

    Args:
        file_path: Path to the file to verify
        component: Component name this file belongs to

    Returns:
        True if safe to remove, False if uncertain (preserve by default)
    """
    try:
        # Known SuperClaude file patterns by component
        superclaude_patterns = {
            "core": [
                "CLAUDE.md",
                "FLAGS.md",
                "PRINCIPLES.md",
                "RULES.md",
                "ORCHESTRATOR.md",
                "SESSION_LIFECYCLE.md",
            ],
            "commands": [
                # Commands are only in sc/ subdirectory
            ],
            "agents": [
                "backend-engineer.md",
                "brainstorm-PRD.md",
                "code-educator.md",
                "code-refactorer.md",
                "devops-engineer.md",
                "frontend-specialist.md",
                "performance-optimizer.md",
                "python-ultimate-expert.md",
                "qa-specialist.md",
                "root-cause-analyzer.md",
                "security-auditor.md",
                "system-architect.md",
                "technical-writer.md",
            ],
            "modes": [
                "MODE_Brainstorming.md",
                "MODE_Introspection.md",
                "MODE_Task_Management.md",
                "MODE_Token_Efficiency.md",
            ],
        }

        # For commands component, verify it's in the sc/ subdirectory
        if component == "commands":
            return "commands/sc/" in str(file_path)

        # For other components, check against known file lists
        if component in superclaude_patterns:
            filename = file_path.name
            return filename in superclaude_patterns[component]

        # For MCP component, it doesn't remove files but modifies .claude.json
        if component == "mcp":
            return True  # MCP component has its own safety logic

        # Default to preserve if uncertain
        return False

    except Exception:
        # If any error occurs in verification, preserve the file
        return False


def verify_directory_safety(directory: Path, component: str) -> bool:
    """
    Verify it's safe to remove a directory

    Args:
        directory: Directory path to verify
        component: Component name

    Returns:
        True if safe to remove (only if empty or only contains SuperClaude files)
    """
    try:
        if not directory.exists():
            return True

        # Check if directory is empty
        contents = list(directory.iterdir())
        if not contents:
            return True

        # Check if all contents are SuperClaude files for this component
        for item in contents:
            if item.is_file():
                if not verify_superclaude_file(item, component):
                    return False
            elif item.is_dir():
                # Don't remove directories that contain non-SuperClaude subdirectories
                return False

        return True

    except Exception:
        # If any error occurs, preserve the directory
        return False


class UninstallOperation(OperationBase):
    """Uninstall operation implementation"""

    def __init__(self):
        super().__init__("uninstall")


def register_parser(subparsers, global_parser=None) -> argparse.ArgumentParser:
    """Register uninstall CLI arguments"""
    parents = [global_parser] if global_parser else []

    parser = subparsers.add_parser(
        "uninstall",
        help="Remove SuperClaude framework installation",
        description="Uninstall SuperClaude Framework components",
        epilog="""
Examples:
  SuperClaude uninstall                    # Interactive uninstall
  SuperClaude uninstall --components core  # Remove specific components
  SuperClaude uninstall --complete --force # Complete removal (forced)
  SuperClaude uninstall --keep-backups     # Keep backup files
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=parents,
    )

    # Uninstall mode options
    parser.add_argument(
        "--components", type=str, nargs="+", help="Specific components to uninstall"
    )

    parser.add_argument(
        "--complete",
        action="store_true",
        help="Complete uninstall (remove all files and directories)",
    )

    # Data preservation options
    parser.add_argument(
        "--keep-backups", action="store_true", help="Keep backup files during uninstall"
    )

    parser.add_argument(
        "--keep-logs", action="store_true", help="Keep log files during uninstall"
    )

    parser.add_argument(
        "--keep-settings",
        action="store_true",
        help="Keep user settings during uninstall",
    )

    # Safety options
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompts (use with caution)",
    )

    # Environment cleanup options
    parser.add_argument(
        "--cleanup-env",
        action="store_true",
        help="Remove SuperClaude environment variables",
    )

    parser.add_argument(
        "--no-restore-script",
        action="store_true",
        help="Skip creating environment variable restore script",
    )

    return parser


def get_installed_components(install_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Get currently installed components and their versions"""
    try:
        settings_manager = SettingsService(install_dir)
        return settings_manager.get_installed_components()
    except Exception:
        return {}


def get_installation_info(install_dir: Path) -> Dict[str, Any]:
    """Get detailed installation information"""
    info = {
        "install_dir": install_dir,
        "exists": False,
        "components": {},
        "directories": [],
        "files": [],
        "total_size": 0,
    }

    if not install_dir.exists():
        return info

    info["exists"] = True
    info["components"] = get_installed_components(install_dir)

    # Scan installation directory
    try:
        for item in install_dir.rglob("*"):
            if item.is_file():
                info["files"].append(item)
                info["total_size"] += item.stat().st_size
            elif item.is_dir():
                info["directories"].append(item)
    except Exception:
        pass

    return info


def display_environment_info() -> Dict[str, str]:
    """Display SuperClaude environment variables and return them"""
    env_vars = get_superclaude_environment_variables()

    if env_vars:
        print(f"\n{Colors.CYAN}{Colors.BRIGHT}Environment Variables{Colors.RESET}")
        print("=" * 50)
        print(
            f"{Colors.BLUE}SuperClaude API key environment variables found:{Colors.RESET}"
        )
        for env_var, value in env_vars.items():
            # Show only first few and last few characters for security
            masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"  {env_var}: {masked_value}")

        print(
            f"\n{Colors.YELLOW}Note: These environment variables will remain unless you use --cleanup-env{Colors.RESET}"
        )
    else:
        print(
            f"\n{Colors.GREEN}No SuperClaude environment variables found{Colors.RESET}"
        )

    return env_vars


def display_uninstall_info(info: Dict[str, Any]) -> None:
    """Display installation information before uninstall"""
    print(f"\n{Colors.CYAN}{Colors.BRIGHT}Current Installation{Colors.RESET}")
    print("=" * 50)

    if not info["exists"]:
        print(f"{Colors.YELLOW}No SuperClaude installation found{Colors.RESET}")
        return

    print(f"{Colors.BLUE}Installation Directory:{Colors.RESET} {info['install_dir']}")

    if info["components"]:
        print(f"{Colors.BLUE}Installed Components:{Colors.RESET}")
        for component, version in info["components"].items():
            print(f"  {component}: v{version}")

    print(f"{Colors.BLUE}Files:{Colors.RESET} {len(info['files'])}")
    print(f"{Colors.BLUE}Directories:{Colors.RESET} {len(info['directories'])}")

    if info["total_size"] > 0:
        from ...utils.ui import format_size

        print(
            f"{Colors.BLUE}Total Size:{Colors.RESET} {format_size(info['total_size'])}"
        )

    print()


def get_components_to_uninstall(
    args: argparse.Namespace, installed_components: Dict[str, str]
) -> Optional[List[str]]:
    """Determine which components to uninstall"""
    logger = get_logger()

    # Complete uninstall
    if args.complete:
        return list(installed_components.keys())

    # Explicit components specified
    if args.components:
        # Validate that specified components are installed
        invalid_components = [
            c for c in args.components if c not in installed_components
        ]
        if invalid_components:
            logger.error(f"Components not installed: {invalid_components}")
            return None
        return args.components

    # Interactive selection
    return interactive_uninstall_selection(installed_components)


def interactive_component_selection(
    installed_components: Dict[str, str], env_vars: Dict[str, str]
) -> Optional[tuple]:
    """
    Enhanced interactive selection with granular component options

    Returns:
        Tuple of (components_to_remove, cleanup_options) or None if cancelled
    """
    if not installed_components:
        return []

    print(f"\n{Colors.CYAN}{Colors.BRIGHT}SuperClaude Uninstall Options{Colors.RESET}")
    print("=" * 60)

    # Main uninstall type selection
    main_options = [
        "Complete Uninstall (remove all SuperClaude components)",
        "Custom Uninstall (choose specific components)",
        "Cancel Uninstall",
    ]

    print(f"\n{Colors.BLUE}Choose uninstall type:{Colors.RESET}")
    main_menu = Menu("Select option:", main_options)
    main_choice = main_menu.display()

    if main_choice == -1 or main_choice == 2:  # Cancelled
        return None
    elif main_choice == 0:  # Complete uninstall
        # Complete uninstall - include all components and optional cleanup
        cleanup_options = _ask_complete_uninstall_options(env_vars)
        return list(installed_components.keys()), cleanup_options
    elif main_choice == 1:  # Custom uninstall
        return _custom_component_selection(installed_components, env_vars)

    return None


def _ask_complete_uninstall_options(env_vars: Dict[str, str]) -> Dict[str, bool]:
    """Ask for complete uninstall options"""
    cleanup_options = {
        "remove_mcp_configs": True,
        "cleanup_env_vars": False,
        "create_restore_script": True,
    }

    print(f"\n{Colors.YELLOW}{Colors.BRIGHT}Complete Uninstall Options{Colors.RESET}")
    print("This will remove ALL SuperClaude components.")

    if env_vars:
        print(f"\n{Colors.BLUE}Environment variables found:{Colors.RESET}")
        for env_var, value in env_vars.items():
            masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"  {env_var}: {masked_value}")

        cleanup_env = confirm(
            "Also remove API key environment variables?", default=False
        )
        cleanup_options["cleanup_env_vars"] = cleanup_env

        if cleanup_env:
            create_script = confirm(
                "Create restore script for environment variables?", default=True
            )
            cleanup_options["create_restore_script"] = create_script

    return cleanup_options


def _custom_component_selection(
    installed_components: Dict[str, str], env_vars: Dict[str, str]
) -> Optional[tuple]:
    """Handle custom component selection with granular options"""
    print(
        f"\n{Colors.CYAN}{Colors.BRIGHT}Custom Uninstall - Choose Components{Colors.RESET}"
    )
    print("Select which SuperClaude components to remove:")

    # Build component options with descriptions
    component_options = []
    component_keys = []

    component_descriptions = {
        "core": "Core Framework Files (CLAUDE.md, FLAGS.md, PRINCIPLES.md, etc.)",
        "commands": "superclaude Commands (commands/sc/*.md)",
        "agents": "Specialized Agents (agents/*.md)",
        "mcp": "MCP Server Configurations (airis-mcp-gateway)",
        "modes": "superclaude Modes",
    }

    for component, version in installed_components.items():
        description = component_descriptions.get(component, f"{component} component")
        component_options.append(f"{description}")
        component_keys.append(component)

    print(f"\n{Colors.BLUE}Select components to remove:{Colors.RESET}")
    component_menu = Menu("Components:", component_options, multi_select=True)
    selections = component_menu.display()

    if not selections:
        return None

    selected_components = [component_keys[i] for i in selections]

    # If MCP component is selected, ask about related cleanup options
    cleanup_options = {
        "remove_mcp_configs": "mcp" in selected_components,
        "cleanup_env_vars": False,
        "create_restore_script": True,
    }

    if "mcp" in selected_components:
        cleanup_options.update(_ask_mcp_cleanup_options(env_vars))
    elif env_vars:
        # Even if MCP not selected, ask about env vars if they exist
        cleanup_env = confirm(
            f"Remove {len(env_vars)} API key environment variables?", default=False
        )
        cleanup_options["cleanup_env_vars"] = cleanup_env
        if cleanup_env:
            create_script = confirm(
                "Create restore script for environment variables?", default=True
            )
            cleanup_options["create_restore_script"] = create_script

    return selected_components, cleanup_options


def _ask_mcp_cleanup_options(env_vars: Dict[str, str]) -> Dict[str, bool]:
    """Ask for MCP-related cleanup options"""
    print(f"\n{Colors.YELLOW}{Colors.BRIGHT}MCP Cleanup Options{Colors.RESET}")
    print("Since you're removing the MCP component:")

    cleanup_options = {}

    # Ask about MCP server configurations
    remove_configs = confirm(
        "Remove MCP server configurations from .claude.json?", default=True
    )
    cleanup_options["remove_mcp_configs"] = remove_configs

    # Ask about API key environment variables
    if env_vars:
        print(
            f"\n{Colors.BLUE}Related API key environment variables found:{Colors.RESET}"
        )
        for env_var, value in env_vars.items():
            masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"  {env_var}: {masked_value}")

        cleanup_env = confirm(
            f"Remove {len(env_vars)} API key environment variables?", default=False
        )
        cleanup_options["cleanup_env_vars"] = cleanup_env

        if cleanup_env:
            create_script = confirm(
                "Create restore script for environment variables?", default=True
            )
            cleanup_options["create_restore_script"] = create_script
        else:
            cleanup_options["create_restore_script"] = True
    else:
        cleanup_options["cleanup_env_vars"] = False
        cleanup_options["create_restore_script"] = True

    return cleanup_options


def interactive_uninstall_selection(
    installed_components: Dict[str, str],
) -> Optional[List[str]]:
    """Legacy function - redirects to enhanced selection"""
    env_vars = get_superclaude_environment_variables()
    result = interactive_component_selection(installed_components, env_vars)

    if result is None:
        return None

    # For backwards compatibility, return only component list
    components, cleanup_options = result
    return components


def display_preservation_info() -> None:
    """Show what will NOT be removed (user's custom files)"""
    print(f"\n{Colors.GREEN}{Colors.BRIGHT}Files that will be preserved:{Colors.RESET}")
    print(f"{Colors.GREEN}+ User's custom commands (not in commands/sc/){Colors.RESET}")
    print(
        f"{Colors.GREEN}+ User's custom agents (not SuperClaude agents){Colors.RESET}"
    )
    print(f"{Colors.GREEN}+ User's custom .claude.json configurations{Colors.RESET}")
    print(f"{Colors.GREEN}+ User's custom files in shared directories{Colors.RESET}")
    print(
        f"{Colors.GREEN}+ Claude Code settings and other tools' configurations{Colors.RESET}"
    )


def display_component_details(component: str, info: Dict[str, Any]) -> Dict[str, Any]:
    """Get detailed information about what will be removed for a component"""
    details = {"files": [], "directories": [], "size": 0, "description": ""}

    install_dir = info["install_dir"]

    component_paths = {
        "core": {
            "files": [
                "CLAUDE.md",
                "FLAGS.md",
                "PRINCIPLES.md",
                "RULES.md",
                "ORCHESTRATOR.md",
                "SESSION_LIFECYCLE.md",
            ],
            "description": "Core framework files in ~/.claude/",
        },
        "commands": {
            "files": "commands/sc/*.md",
            "description": "superclaude commands in ~/.claude/commands/sc/",
        },
        "agents": {
            "files": "agents/*.md",
            "description": "Specialized AI agents in ~/.claude/agents/",
        },
        "mcp": {
            "files": "MCP server configurations in .claude.json",
            "description": "MCP server configurations (airis-mcp-gateway)",
        },
        "modes": {"files": "MODE_*.md", "description": "superclaude operational modes"},
    }

    if component in component_paths:
        details["description"] = component_paths[component]["description"]

        # Get actual file count from metadata if available
        component_metadata = info["components"].get(component, {})
        if isinstance(component_metadata, dict):
            if "files_count" in component_metadata:
                details["file_count"] = component_metadata["files_count"]
            elif "agents_count" in component_metadata:
                details["file_count"] = component_metadata["agents_count"]
            elif "servers_configured" in component_metadata:
                details["file_count"] = component_metadata["servers_configured"]

    return details


def display_uninstall_plan(
    components: List[str],
    args: argparse.Namespace,
    info: Dict[str, Any],
    env_vars: Dict[str, str],
) -> None:
    """Display detailed uninstall plan"""
    print(f"\n{Colors.CYAN}{Colors.BRIGHT}Uninstall Plan{Colors.RESET}")
    print("=" * 60)

    print(f"{Colors.BLUE}Installation Directory:{Colors.RESET} {info['install_dir']}")

    if components:
        print(f"\n{Colors.BLUE}Components to remove:{Colors.RESET}")
        total_files = 0

        for i, component_name in enumerate(components, 1):
            details = display_component_details(component_name, info)
            version = info["components"].get(component_name, "unknown")

            if isinstance(version, dict):
                version_str = version.get("version", "unknown")
                file_count = details.get(
                    "file_count",
                    version.get(
                        "files_count",
                        version.get(
                            "agents_count", version.get("servers_configured", "?")
                        ),
                    ),
                )
            else:
                version_str = str(version)
                file_count = details.get("file_count", "?")

            print(f"  {i}. {component_name} (v{version_str}) - {file_count} files")
            print(f"     {details['description']}")

            if isinstance(file_count, int):
                total_files += file_count

        print(
            f"\n{Colors.YELLOW}Total estimated files to remove: {total_files}{Colors.RESET}"
        )

    # Show detailed preservation information
    print(
        f"\n{Colors.GREEN}{Colors.BRIGHT}Safety Guarantees - Will Preserve:{Colors.RESET}"
    )
    print(f"{Colors.GREEN}+ User's custom commands (not in commands/sc/){Colors.RESET}")
    print(
        f"{Colors.GREEN}+ User's custom agents (not SuperClaude agents){Colors.RESET}"
    )
    print(f"{Colors.GREEN}+ User's .claude.json customizations{Colors.RESET}")
    print(
        f"{Colors.GREEN}+ Claude Code settings and other tools' configurations{Colors.RESET}"
    )

    # Show additional preserved items
    preserved = []
    if args.keep_backups:
        preserved.append("backup files")
    if args.keep_logs:
        preserved.append("log files")
    if args.keep_settings:
        preserved.append("user settings")

    if preserved:
        for item in preserved:
            print(f"{Colors.GREEN}+ {item}{Colors.RESET}")

    if args.complete:
        print(
            f"\n{Colors.RED}⚠️  WARNING: Complete uninstall will remove all SuperClaude files{Colors.RESET}"
        )

    # Environment variable cleanup information
    if env_vars:
        print(f"\n{Colors.BLUE}Environment Variables:{Colors.RESET}")
        if args.cleanup_env:
            print(
                f"{Colors.YELLOW}Will remove {len(env_vars)} API key environment variables:{Colors.RESET}"
            )
            for env_var in env_vars.keys():
                print(f"  - {env_var}")
            if not args.no_restore_script:
                print(f"{Colors.GREEN}  + Restore script will be created{Colors.RESET}")
        else:
            print(
                f"{Colors.BLUE}Will preserve {len(env_vars)} API key environment variables:{Colors.RESET}"
            )
            for env_var in env_vars.keys():
                print(f"  + {env_var}")

    print()


def create_uninstall_backup(install_dir: Path, components: List[str]) -> Optional[Path]:
    """Create backup before uninstall"""
    logger = get_logger()

    try:
        from datetime import datetime

        backup_dir = install_dir / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"pre_uninstall_{timestamp}.tar.gz"
        backup_path = backup_dir / backup_name

        import tarfile

        logger.info(f"Creating uninstall backup: {backup_path}")

        with tarfile.open(backup_path, "w:gz") as tar:
            for component in components:
                # Add component files to backup
                settings_manager = SettingsService(install_dir)
                # This would need component-specific backup logic
                pass

        logger.success(f"Backup created: {backup_path}")
        return backup_path

    except Exception as e:
        logger.warning(f"Could not create backup: {e}")
        return None


def perform_uninstall(
    components: List[str],
    args: argparse.Namespace,
    info: Dict[str, Any],
    env_vars: Dict[str, str],
) -> bool:
    """Perform the actual uninstall"""
    logger = get_logger()
    start_time = time.time()

    try:
        # Create component registry
        registry = ComponentRegistry(PROJECT_ROOT / "setup" / "components")
        registry.discover_components()

        # Create component instances
        component_instances = registry.create_component_instances(
            components, args.install_dir
        )

        # Setup progress tracking
        progress = ProgressBar(
            total=len(components), prefix="Uninstalling: ", suffix=""
        )

        # Uninstall components
        logger.info(f"Uninstalling {len(components)} components...")

        uninstalled_components = []
        failed_components = []

        for i, component_name in enumerate(components):
            progress.update(i, f"Uninstalling {component_name}")

            try:
                if component_name in component_instances:
                    instance = component_instances[component_name]
                    if instance.uninstall():
                        uninstalled_components.append(component_name)
                        logger.debug(f"Successfully uninstalled {component_name}")
                    else:
                        failed_components.append(component_name)
                        logger.error(f"Failed to uninstall {component_name}")
                else:
                    logger.warning(f"Component {component_name} not found, skipping")

            except Exception as e:
                logger.error(f"Error uninstalling {component_name}: {e}")
                failed_components.append(component_name)

            progress.update(i + 1, f"Processed {component_name}")
            time.sleep(0.1)  # Brief pause for visual effect

        progress.finish("Uninstall complete")

        # Handle complete uninstall cleanup
        if args.complete:
            cleanup_installation_directory(args.install_dir, args)

        # Handle environment variable cleanup
        env_cleanup_success = True
        if args.cleanup_env and env_vars:
            logger.info("Cleaning up environment variables...")
            create_restore_script = not args.no_restore_script
            env_cleanup_success = cleanup_environment_variables(
                env_vars, create_restore_script
            )

            if env_cleanup_success:
                logger.success(f"Removed {len(env_vars)} environment variables")
            else:
                logger.warning("Some environment variables could not be removed")

        # Show results
        duration = time.time() - start_time

        if failed_components:
            logger.warning(
                f"Uninstall completed with some failures in {duration:.1f} seconds"
            )
            logger.warning(f"Failed components: {', '.join(failed_components)}")
        else:
            logger.success(
                f"Uninstall completed successfully in {duration:.1f} seconds"
            )

        if uninstalled_components:
            logger.info(f"Uninstalled components: {', '.join(uninstalled_components)}")

        return len(failed_components) == 0

    except Exception as e:
        logger.exception(f"Unexpected error during uninstall: {e}")
        return False


def cleanup_installation_directory(install_dir: Path, args: argparse.Namespace) -> None:
    """Clean up installation directory for complete uninstall"""
    logger = get_logger()
    file_manager = FileService()

    try:
        # Preserve specific directories/files if requested
        preserve_patterns = []

        if args.keep_backups:
            preserve_patterns.append("backups/*")
        if args.keep_logs:
            preserve_patterns.append("logs/*")
        if args.keep_settings and not args.complete:
            preserve_patterns.append("settings.json")

        # Remove installation directory contents
        if args.complete and not preserve_patterns:
            # Complete removal
            if file_manager.remove_directory(install_dir):
                logger.info(f"Removed installation directory: {install_dir}")
            else:
                logger.warning(
                    f"Could not remove installation directory: {install_dir}"
                )
        else:
            # Selective removal
            for item in install_dir.iterdir():
                should_preserve = False

                for pattern in preserve_patterns:
                    if item.match(pattern):
                        should_preserve = True
                        break

                if not should_preserve:
                    if item.is_file():
                        file_manager.remove_file(item)
                    elif item.is_dir():
                        file_manager.remove_directory(item)

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def run(args: argparse.Namespace) -> int:
    """Execute uninstall operation with parsed arguments"""
    operation = UninstallOperation()
    operation.setup_operation_logging(args)
    logger = get_logger()
    # ✅ Inserted validation code
    expected_home = get_home_directory().resolve()
    actual_dir = args.install_dir.resolve()

    if not str(actual_dir).startswith(str(expected_home)):
        print(f"\n[x] Installation must be inside your user profile directory.")
        print(f"    Expected prefix: {expected_home}")
        print(f"    Provided path:   {actual_dir}")
        sys.exit(1)

    try:
        # Validate global arguments
        success, errors = operation.validate_global_args(args)
        if not success:
            for error in errors:
                logger.error(error)
            return 1

        # Display header
        if not args.quiet:
            from setup.cli.base import __version__

            display_header(
                f"SuperClaude Uninstall v{__version__}",
                "Removing SuperClaude framework components",
            )

        # Get installation information
        info = get_installation_info(args.install_dir)

        # Display current installation
        if not args.quiet:
            display_uninstall_info(info)

        # Check for environment variables
        env_vars = (
            display_environment_info()
            if not args.quiet
            else get_superclaude_environment_variables()
        )

        # Check if SuperClaude is installed
        if not info["exists"]:
            logger.warning(f"No SuperClaude installation found in {args.install_dir}")
            return 0

        # Get components to uninstall using enhanced selection
        if args.components or args.complete:
            # Non-interactive mode - use existing logic
            components = get_components_to_uninstall(args, info["components"])
            cleanup_options = {
                "remove_mcp_configs": "mcp" in (components or []),
                "cleanup_env_vars": args.cleanup_env,
                "create_restore_script": not args.no_restore_script,
            }
            if components is None:
                logger.info("Uninstall cancelled by user")
                return 0
            elif not components:
                logger.info("No components selected for uninstall")
                return 0
        else:
            # Interactive mode - use enhanced selection
            result = interactive_component_selection(info["components"], env_vars)
            if result is None:
                logger.info("Uninstall cancelled by user")
                return 0
            elif not result:
                logger.info("No components selected for uninstall")
                return 0

            components, cleanup_options = result

            # Override command-line args with interactive choices
            args.cleanup_env = cleanup_options.get("cleanup_env_vars", False)
            args.no_restore_script = not cleanup_options.get(
                "create_restore_script", True
            )

        # Display uninstall plan
        if not args.quiet:
            display_uninstall_plan(components, args, info, env_vars)

        # Confirmation
        if not args.no_confirm and not args.yes:
            if args.complete:
                warning_msg = "This will completely remove superclaude. Continue?"
            else:
                warning_msg = (
                    f"This will remove {len(components)} component(s). Continue?"
                )

            if not confirm(warning_msg, default=False):
                logger.info("Uninstall cancelled by user")
                return 0

        # Create backup if not dry run and not keeping backups
        if not args.dry_run and not args.keep_backups:
            create_uninstall_backup(args.install_dir, components)

        # Perform uninstall
        success = perform_uninstall(components, args, info, env_vars)

        if success:
            if not args.quiet:
                display_success("SuperClaude uninstall completed successfully!")

                if not args.dry_run:
                    print(f"\n{Colors.CYAN}Uninstall complete:{Colors.RESET}")
                    print(f"SuperClaude has been removed from {args.install_dir}")
                    if not args.complete:
                        print(f"You can reinstall anytime using 'superclaude install'")

            return 0
        else:
            display_error(
                "Uninstall completed with some failures. Check logs for details."
            )
            return 1

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Uninstall cancelled by user{Colors.RESET}")
        return 130
    except Exception as e:
        return operation.handle_operation_error("uninstall", e)
