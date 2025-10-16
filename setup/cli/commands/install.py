"""
SuperClaude Installation Operation Module
Refactored from install.py for unified CLI hub
"""

import sys
import time
from pathlib import Path
from ...utils.paths import get_home_directory
from typing import List, Optional, Dict, Any
import argparse

from ...core.installer import Installer
from ...core.registry import ComponentRegistry
from ...services.config import ConfigService
from ...core.validator import Validator
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
    format_size,
    prompt_api_key,
)
from ...utils.environment import setup_environment_variables
from ...utils.logger import get_logger
from ... import DEFAULT_INSTALL_DIR, PROJECT_ROOT, DATA_DIR
from . import OperationBase


class InstallOperation(OperationBase):
    """Installation operation implementation"""

    def __init__(self):
        super().__init__("install")


def register_parser(subparsers, global_parser=None) -> argparse.ArgumentParser:
    """Register installation CLI arguments"""
    parents = [global_parser] if global_parser else []

    parser = subparsers.add_parser(
        "install",
        help="Install SuperClaude framework components",
        description="Install SuperClaude Framework with various options and profiles",
        epilog="""
Examples:
  SuperClaude install                          # Interactive installation
  SuperClaude install --dry-run                # Dry-run mode  
  SuperClaude install --components core mcp    # Specific components
  SuperClaude install --verbose --force        # Verbose with force mode
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=parents,
    )

    # Installation mode options

    parser.add_argument(
        "--components", type=str, nargs="+", help="Specific components to install"
    )

    # Installation options
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")

    parser.add_argument(
        "--list-components",
        action="store_true",
        help="List available components and exit",
    )

    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Run system diagnostics and show installation help",
    )

    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy mode: install individual official MCP servers instead of unified gateway",
    )

    return parser


def validate_system_requirements(
    validator: Validator, component_names: List[str]
) -> bool:
    """Validate system requirements"""
    logger = get_logger()

    logger.info("Validating system requirements...")

    try:
        # Load requirements configuration
        config_manager = ConfigService(DATA_DIR)
        requirements = config_manager.get_requirements_for_components(component_names)

        # Validate requirements
        success, errors = validator.validate_component_requirements(
            component_names, requirements
        )

        if success:
            logger.success("All system requirements met")
            return True
        else:
            logger.error("System requirements not met:")
            for error in errors:
                logger.error(f"  - {error}")

            # Provide additional guidance
            print(f"\n{Colors.CYAN}💡 Installation Help:{Colors.RESET}")
            print(
                "  Run 'superclaude install --diagnose' for detailed system diagnostics"
            )
            print("  and step-by-step installation instructions.")

            return False

    except Exception as e:
        logger.error(f"Could not validate system requirements: {e}")
        return False


def get_components_to_install(
    args: argparse.Namespace, registry: ComponentRegistry, config_manager: ConfigService
) -> Optional[List[str]]:
    """Determine which components to install"""
    logger = get_logger()

    # Explicit components specified
    if args.components:
        if "all" in args.components:
            components = ["framework_docs", "commands", "agents", "modes", "mcp"]
        else:
            components = args.components

        # If mcp is specified, handle MCP server selection
        if "mcp" in components and not args.yes:
            selected_servers = select_mcp_servers(registry)
            if not hasattr(config_manager, "_installation_context"):
                config_manager._installation_context = {}
            config_manager._installation_context["selected_mcp_servers"] = (
                selected_servers
            )

            # If the user selected some servers, ensure mcp is included
            if selected_servers:
                if "mcp" not in components:
                    components.append("mcp")
                    logger.debug(
                        f"Auto-added 'mcp' component for selected servers: {selected_servers}"
                    )

                logger.info(f"Final components to install: {components}")

        return components

    # Interactive two-stage selection
    return interactive_component_selection(registry, config_manager)


def collect_api_keys_for_servers(
    selected_servers: List[str], mcp_instance
) -> Dict[str, str]:
    """
    Collect API keys for servers that require them

    Args:
        selected_servers: List of selected server keys
        mcp_instance: MCP component instance

    Returns:
        Dictionary of environment variable names to API key values
    """
    # Filter servers needing keys
    servers_needing_keys = [
        (server_key, mcp_instance.mcp_servers[server_key])
        for server_key in selected_servers
        if server_key in mcp_instance.mcp_servers
        and mcp_instance.mcp_servers[server_key].get("requires_api_key", False)
    ]

    if not servers_needing_keys:
        return {}

    # Display API key configuration header
    print(f"\n{Colors.CYAN}{Colors.BRIGHT}=== API Key Configuration ==={Colors.RESET}")
    print(
        f"{Colors.YELLOW}The following servers require API keys for full functionality:{Colors.RESET}\n"
    )

    collected_keys = {}
    for server_key, server_info in servers_needing_keys:
        api_key_env = server_info.get("api_key_env")
        service_name = server_info["name"]

        if api_key_env:
            key = prompt_api_key(service_name, api_key_env)
            if key:
                collected_keys[api_key_env] = key

    return collected_keys


def select_mcp_servers(registry: ComponentRegistry) -> List[str]:
    """Stage 1: MCP Server Selection with API Key Collection"""
    logger = get_logger()

    try:
        # Get MCP component to access server list
        mcp_instance = registry.get_component_instance(
            "mcp", DEFAULT_INSTALL_DIR
        )
        if not mcp_instance or not hasattr(mcp_instance, "mcp_servers"):
            logger.error("Could not access MCP server information")
            return []

        # Create MCP server menu
        mcp_servers = mcp_instance.mcp_servers
        server_options = []

        for server_key, server_info in mcp_servers.items():
            description = server_info["description"]
            api_key_note = (
                " (requires API key)"
                if server_info.get("requires_api_key", False)
                else ""
            )
            server_options.append(f"{server_key} - {description}{api_key_note}")

        print(f"\n{Colors.CYAN}{Colors.BRIGHT}{'='*51}{Colors.RESET}")
        print(
            f"{Colors.CYAN}{Colors.BRIGHT}Stage 1: MCP Server Selection (Optional){Colors.RESET}"
        )
        print(f"{Colors.CYAN}{Colors.BRIGHT}{'='*51}{Colors.RESET}")
        print(
            f"\n{Colors.BLUE}MCP servers extend Claude Code with specialized capabilities.{Colors.RESET}"
        )
        print(
            f"{Colors.BLUE}Select servers to configure (you can always add more later):{Colors.RESET}"
        )

        # Add option to skip MCP
        server_options.append("Skip MCP Server installation")

        menu = Menu(
            "Select MCP servers to configure:", server_options, multi_select=True
        )
        selections = menu.display()

        if not selections:
            logger.info("No MCP servers selected")
            return []

        # Filter out the "skip" option and return server keys
        server_keys = list(mcp_servers.keys())
        selected_servers = []

        for i in selections:
            if i < len(server_keys):  # Not the "skip" option
                selected_servers.append(server_keys[i])

        if selected_servers:
            logger.info(f"Selected MCP servers: {', '.join(selected_servers)}")

            # NEW: Collect API keys for selected servers
            collected_keys = collect_api_keys_for_servers(
                selected_servers, mcp_instance
            )

            # Set up environment variables
            if collected_keys:
                setup_environment_variables(collected_keys)

                # Store keys for MCP component to use during installation
                mcp_instance.collected_api_keys = collected_keys
        else:
            logger.info("No MCP servers selected")

        return selected_servers

    except Exception as e:
        logger.error(f"Error in MCP server selection: {e}")
        return []


def select_framework_components(
    registry: ComponentRegistry,
    config_manager: ConfigService,
    selected_mcp_servers: List[str],
) -> List[str]:
    """Stage 2: Framework Component Selection"""
    logger = get_logger()

    try:
        # Framework components (excluding MCP-related ones)
        framework_components = ["framework_docs", "modes", "commands", "agents"]

        # Create component menu
        component_options = []
        component_info = {}

        for component_name in framework_components:
            metadata = registry.get_component_metadata(component_name)
            if metadata:
                description = metadata.get("description", "No description")
                component_options.append(f"{component_name} - {description}")
                component_info[component_name] = metadata

        # MCP documentation is integrated into airis-mcp-gateway, no separate component needed

        print(f"\n{Colors.CYAN}{Colors.BRIGHT}{'='*51}{Colors.RESET}")
        print(
            f"{Colors.CYAN}{Colors.BRIGHT}Stage 2: Framework Component Selection{Colors.RESET}"
        )
        print(f"{Colors.CYAN}{Colors.BRIGHT}{'='*51}{Colors.RESET}")
        print(
            f"\n{Colors.BLUE}Select SuperClaude framework components to install:{Colors.RESET}"
        )

        menu = Menu(
            "Select components (Core is recommended):",
            component_options,
            multi_select=True,
        )
        selections = menu.display()

        if not selections:
            # Default to framework_docs if nothing selected
            logger.info("No components selected, defaulting to framework_docs")
            selected_components = ["framework_docs"]
        else:
            selected_components = []
            all_components = framework_components

            for i in selections:
                if i < len(all_components):
                    selected_components.append(all_components[i])

        # Always include MCP component if servers were selected
        if selected_mcp_servers and "mcp" not in selected_components:
            selected_components.append("mcp")

        logger.info(f"Selected framework components: {', '.join(selected_components)}")
        return selected_components

    except Exception as e:
        logger.error(f"Error in framework component selection: {e}")
        return ["framework_docs"]  # Fallback to framework_docs


def interactive_component_selection(
    registry: ComponentRegistry, config_manager: ConfigService
) -> Optional[List[str]]:
    """Two-stage interactive component selection"""
    logger = get_logger()

    try:
        print(f"\n{Colors.CYAN}SuperClaude Interactive Installation{Colors.RESET}")
        print(
            f"{Colors.BLUE}Select components to install using the two-stage process:{Colors.RESET}"
        )

        # Stage 1: MCP Server Selection
        selected_mcp_servers = select_mcp_servers(registry)

        # Stage 2: Framework Component Selection
        selected_components = select_framework_components(
            registry, config_manager, selected_mcp_servers
        )

        # Store selected MCP servers for components to use
        if not hasattr(config_manager, "_installation_context"):
            config_manager._installation_context = {}
        config_manager._installation_context["selected_mcp_servers"] = (
            selected_mcp_servers
        )

        return selected_components

    except Exception as e:
        logger.error(f"Error in component selection: {e}")
        return None


def display_installation_plan(
    components: List[str], registry: ComponentRegistry, install_dir: Path
) -> None:
    """Display installation plan"""
    logger = get_logger()

    print(f"\n{Colors.CYAN}{Colors.BRIGHT}Installation Plan{Colors.RESET}")
    print("=" * 50)

    # Resolve dependencies
    try:
        ordered_components = registry.resolve_dependencies(components)

        print(f"{Colors.BLUE}Installation Directory:{Colors.RESET} {install_dir}")
        print(f"{Colors.BLUE}Components to install:{Colors.RESET}")

        total_size = 0
        for i, component_name in enumerate(ordered_components, 1):
            metadata = registry.get_component_metadata(component_name)
            if metadata:
                description = metadata.get("description", "No description")
                print(f"  {i}. {component_name} - {description}")

                # Get size estimate if component supports it
                try:
                    instance = registry.get_component_instance(
                        component_name, install_dir
                    )
                    if instance and hasattr(instance, "get_size_estimate"):
                        size = instance.get_size_estimate()
                        total_size += size
                except Exception:
                    pass
            else:
                print(f"  {i}. {component_name} - Unknown component")

        if total_size > 0:
            print(
                f"\n{Colors.BLUE}Estimated size:{Colors.RESET} {format_size(total_size)}"
            )

        print()

    except Exception as e:
        logger.error(f"Could not resolve dependencies: {e}")
        raise


def run_system_diagnostics(validator: Validator) -> None:
    """Run comprehensive system diagnostics"""
    logger = get_logger()

    print(f"\n{Colors.CYAN}{Colors.BRIGHT}SuperClaude System Diagnostics{Colors.RESET}")
    print("=" * 50)

    # Run diagnostics
    diagnostics = validator.diagnose_system()

    # Display platform info
    print(f"{Colors.BLUE}Platform:{Colors.RESET} {diagnostics['platform']}")

    # Display check results
    print(f"\n{Colors.BLUE}System Checks:{Colors.RESET}")
    all_passed = True

    for check_name, check_info in diagnostics["checks"].items():
        status = check_info["status"]
        message = check_info["message"]

        if status == "pass":
            print(f"  ✅ {check_name}: {message}")
        else:
            print(f"  ❌ {check_name}: {message}")
            all_passed = False

    # Display issues and recommendations
    if diagnostics["issues"]:
        print(f"\n{Colors.YELLOW}Issues Found:{Colors.RESET}")
        for issue in diagnostics["issues"]:
            print(f"  ⚠️  {issue}")

        print(f"\n{Colors.CYAN}Recommendations:{Colors.RESET}")
        for recommendation in diagnostics["recommendations"]:
            print(recommendation)

    # Summary
    if all_passed:
        print(
            f"\n{Colors.GREEN}✅ All system checks passed! Your system is ready for superclaude.{Colors.RESET}"
        )
    else:
        print(
            f"\n{Colors.YELLOW}⚠️  Some issues found. Please address the recommendations above.{Colors.RESET}"
        )

    print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
    if all_passed:
        print("  1. Run 'superclaude install' to proceed with installation")
        print(
            "  2. Choose your preferred installation mode (quick, minimal, or custom)"
        )
    else:
        print("  1. Install missing dependencies using the commands above")
        print("  2. Restart your terminal after installing tools")
        print("  3. Run 'superclaude install --diagnose' again to verify")


def perform_installation(
    components: List[str],
    args: argparse.Namespace,
    config_manager: ConfigService = None,
) -> bool:
    """Perform the actual installation"""
    logger = get_logger()
    start_time = time.time()

    try:
        # Create installer
        installer = Installer(args.install_dir, dry_run=args.dry_run)

        # Create component registry
        registry = ComponentRegistry(PROJECT_ROOT / "setup" / "components")
        registry.discover_components()

        # Create component instances
        component_instances = registry.create_component_instances(
            components, args.install_dir
        )

        if not component_instances:
            logger.error("No valid component instances created")
            return False

        # Register components with installer
        installer.register_components(list(component_instances.values()))

        # The 'components' list is already resolved, so we can use it directly.
        ordered_components = components

        # Setup progress tracking
        progress = ProgressBar(
            total=len(ordered_components), prefix="Installing: ", suffix=""
        )

        # Install components
        logger.info(f"Installing {len(ordered_components)} components...")

        config = {
            "force": args.force,
            "backup": not args.no_backup,
            "dry_run": args.dry_run,
            "legacy_mode": getattr(args, "legacy", False),
            "selected_mcp_servers": getattr(
                config_manager, "_installation_context", {}
            ).get("selected_mcp_servers", []),
        }

        success = installer.install_components(ordered_components, config)

        # Update progress
        for i, component_name in enumerate(ordered_components):
            if component_name in installer.installed_components:
                progress.update(i + 1, f"Installed {component_name}")
            else:
                progress.update(i + 1, f"Failed {component_name}")
            time.sleep(0.1)  # Brief pause for visual effect

        progress.finish("Installation complete")

        # Show results
        duration = time.time() - start_time

        if success:
            logger.success(
                f"Installation completed successfully in {duration:.1f} seconds"
            )

            # Show summary
            summary = installer.get_installation_summary()
            if summary["installed"]:
                logger.info(f"Installed components: {', '.join(summary['installed'])}")

        else:
            logger.error(
                f"Installation completed with errors in {duration:.1f} seconds"
            )

            summary = installer.get_installation_summary()
            if summary["failed"]:
                logger.error(f"Failed components: {', '.join(summary['failed'])}")

        return success

    except Exception as e:
        logger.exception(f"Unexpected error during installation: {e}")
        return False


def run(args: argparse.Namespace) -> int:
    """Execute installation operation with parsed arguments"""
    operation = InstallOperation()
    operation.setup_operation_logging(args)
    logger = get_logger()
    # ✅ Enhanced security validation with symlink protection
    expected_home = get_home_directory().resolve()
    install_dir_original = args.install_dir
    install_dir_resolved = args.install_dir.resolve()

    # Check for symlink attacks - compare original vs resolved paths
    try:
        # Verify the resolved path is still within user home
        install_dir_resolved.relative_to(expected_home)

        # Additional check: if there's a symlink in the path, verify it doesn't escape user home
        if install_dir_original != install_dir_resolved:
            # Path contains symlinks - verify each component stays within user home
            current_path = expected_home
            parts = install_dir_original.parts
            home_parts = expected_home.parts

            # Skip home directory parts
            if len(parts) >= len(home_parts) and parts[: len(home_parts)] == home_parts:
                relative_parts = parts[len(home_parts) :]

                for part in relative_parts:
                    current_path = current_path / part
                    if current_path.is_symlink():
                        symlink_target = current_path.resolve()
                        # Ensure symlink target is also within user home
                        symlink_target.relative_to(expected_home)
    except ValueError:
        print(f"\n[x] Installation must be inside your user profile directory.")
        print(f"    Expected prefix: {expected_home}")
        print(f"    Provided path:   {install_dir_resolved}")
        print(f"    Security: Symlinks outside user directory are not allowed.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[x] Security validation failed: {e}")
        print(f"    Please use a standard directory path within your user profile.")
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
                f"SuperClaude Installation v{__version__}",
                "Installing SuperClaude framework components",
            )

        # Handle special modes
        if args.list_components:
            registry = ComponentRegistry(PROJECT_ROOT / "setup" / "components")
            registry.discover_components()

            components = registry.list_components()
            if components:
                print(f"\n{Colors.CYAN}Available Components:{Colors.RESET}")
                for component_name in components:
                    metadata = registry.get_component_metadata(component_name)
                    if metadata:
                        desc = metadata.get("description", "No description")
                        category = metadata.get("category", "unknown")
                        print(f"  {component_name} ({category}) - {desc}")
                    else:
                        print(f"  {component_name} - Unknown component")
            else:
                print("No components found")
            return 0

        # Handle diagnostic mode
        if args.diagnose:
            validator = Validator()
            run_system_diagnostics(validator)
            return 0

        # Create component registry and load configuration
        logger.info("Initializing installation system...")

        registry = ComponentRegistry(PROJECT_ROOT / "setup" / "components")
        registry.discover_components()

        config_manager = ConfigService(DATA_DIR)
        validator = Validator()

        # Validate configuration
        config_errors = config_manager.validate_config_files()
        if config_errors:
            logger.error("Configuration validation failed:")
            for error in config_errors:
                logger.error(f"  - {error}")
            return 1

        # Get components to install
        components_to_install = get_components_to_install(
            args, registry, config_manager
        )
        if not components_to_install:
            logger.error("No components selected for installation")
            return 1

        # Resolve dependencies
        try:
            resolved_components = registry.resolve_dependencies(components_to_install)
        except ValueError as e:
            logger.error(f"Dependency resolution error: {e}")
            return 1

        # Validate system requirements for all components
        if not validate_system_requirements(validator, resolved_components):
            if not args.force:
                logger.error("System requirements not met. Use --force to override.")
                return 1
            else:
                logger.warning(
                    "System requirements not met, but continuing due to --force flag"
                )

        # Check for existing installation
        if args.install_dir.exists() and not args.force:
            if not args.dry_run:
                logger.warning(
                    f"Installation directory already exists: {args.install_dir}"
                )
                if not args.yes and not confirm(
                    "Continue and update existing installation?", default=False
                ):
                    logger.info("Installation cancelled by user")
                    return 0

        # Display installation plan
        if not args.quiet:
            display_installation_plan(resolved_components, registry, args.install_dir)

            if not args.dry_run:
                if not args.yes and not confirm(
                    "Proceed with installation?", default=True
                ):
                    logger.info("Installation cancelled by user")
                    return 0

        # Perform installation
        success = perform_installation(resolved_components, args, config_manager)

        if success:
            if not args.quiet:
                display_success("SuperClaude installation completed successfully!")

                if not args.dry_run:
                    print(f"\n{Colors.CYAN}Next steps:{Colors.RESET}")
                    print(f"1. Restart your Claude Code session")
                    print(f"2. Framework files are now available in {args.install_dir}")
                    print(f"3. Use SuperClaude commands and features in Claude Code")

            return 0
        else:
            display_error("Installation failed. Check logs for details.")
            return 1

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Installation cancelled by user{Colors.RESET}")
        return 130
    except Exception as e:
        return operation.handle_operation_error("install", e)
