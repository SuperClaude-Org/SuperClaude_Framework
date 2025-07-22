"""
SuperClaude Installation Operation Module
Refactored from install.py for unified CLI hub
"""

import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import argparse

from ..base.installer import Installer
from ..core.registry import ComponentRegistry
from ..managers.config_manager import ConfigManager
from ..core.validator import Validator
from ..utils.ui import (
    display_header, display_info, display_success, display_error, 
    display_warning, Menu, confirm, ProgressBar, Colors, format_size
)
from ..utils.logger import get_logger
from .. import DEFAULT_INSTALL_DIR, PROJECT_ROOT
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
  SuperClaude install --quick --dry-run        # Quick installation (dry-run)
  SuperClaude install --profile developer      # Developer profile  
  SuperClaude install --components core mcp    # Specific components
  SuperClaude install --verbose --force        # Verbose with force mode
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=parents
    )
    
    # Installation mode options
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Quick installation with pre-selected components"
    )
    
    parser.add_argument(
        "--minimal",
        action="store_true", 
        help="Minimal installation (core only)"
    )
    
    parser.add_argument(
        "--profile",
        type=str,
        help="Installation profile (quick, minimal, developer, etc.)"
    )
    
    parser.add_argument(
        "--components",
        type=str,
        nargs="+",
        help="Specific components to install"
    )
    
    # Installation options
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation"
    )
    
    parser.add_argument(
        "--list-components",
        action="store_true",
        help="List available components and exit"
    )
    
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Run system diagnostics and show installation help"
    )
    
    return parser


def validate_system_requirements(validator: Validator, component_names: List[str]) -> bool:
    """Validate system requirements"""
    logger = get_logger()
    
    logger.info("Validating system requirements...")
    
    try:
        # Load requirements configuration
        config_manager = ConfigManager(PROJECT_ROOT / "config")
        requirements = config_manager.get_requirements_for_components(component_names)
        
        # Validate requirements
        success, errors = validator.validate_component_requirements(component_names, requirements)
        
        if success:
            logger.success("All system requirements met")
            return True
        else:
            logger.error("System requirements not met:")
            for error in errors:
                logger.error(f"  - {error}")
            
            # Provide additional guidance
            print(f"\n{Colors.CYAN}💡 Installation Help:{Colors.RESET}")
            print("  Run 'SuperClaude install --diagnose' for detailed system diagnostics")
            print("  and step-by-step installation instructions.")
            
            return False
            
    except Exception as e:
        logger.error(f"Could not validate system requirements: {e}")
        return False


def get_components_to_install(args: argparse.Namespace, registry: ComponentRegistry, config_manager: ConfigManager) -> Optional[List[str]]:
    """Determine which components to install"""
    logger = get_logger()
    
    # Explicit components specified
    if args.components:
        if 'all' in args.components:
            return ["core", "commands", "hooks", "mcp"]
        return args.components
    
    # Profile-based selection
    if args.profile:
        try:
            profile_path = PROJECT_ROOT / "profiles" / f"{args.profile}.json"
            profile = config_manager.load_profile(profile_path)
            return profile["components"]
        except Exception as e:
            logger.error(f"Could not load profile '{args.profile}': {e}")
            return None
    
    # Quick installation
    if args.quick:
        try:
            profile_path = PROJECT_ROOT / "profiles" / "quick.json"
            profile = config_manager.load_profile(profile_path)
            return profile["components"]
        except Exception as e:
            logger.warning(f"Could not load quick profile: {e}")
            return ["core"]  # Fallback to core only
    
    # Minimal installation
    if args.minimal:
        return ["core"]
    
    # Interactive selection
    return interactive_component_selection(registry, config_manager)


def interactive_component_selection(registry: ComponentRegistry, config_manager: ConfigManager) -> Optional[List[str]]:
    """Interactive component selection"""
    logger = get_logger()
    
    try:
        # Get available components
        available_components = registry.list_components()
        
        if not available_components:
            logger.error("No components available for installation")
            return None
        
        # Create component menu with descriptions
        menu_options = []
        component_info = {}
        
        for component_name in available_components:
            metadata = registry.get_component_metadata(component_name)
            if metadata:
                description = metadata.get("description", "No description")
                category = metadata.get("category", "unknown")
                menu_options.append(f"{component_name} ({category}) - {description}")
                component_info[component_name] = metadata
            else:
                menu_options.append(f"{component_name} - Component description unavailable")
                component_info[component_name] = {"description": "Unknown"}
        
        # Add preset options
        preset_options = [
            "Quick Installation (recommended components)",
            "Minimal Installation (core only)",
            "Custom Selection"
        ]
        
        print(f"\n{Colors.CYAN}SuperClaude Installation Options:{Colors.RESET}")
        menu = Menu("Select installation type:", preset_options)
        choice = menu.display()
        
        if choice == -1:  # Cancelled
            return None
        elif choice == 0:  # Quick
            try:
                profile_path = PROJECT_ROOT / "profiles" / "quick.json"
                profile = config_manager.load_profile(profile_path)
                return profile["components"]
            except Exception:
                return ["core"]
        elif choice == 1:  # Minimal
            return ["core"]
        elif choice == 2:  # Custom
            print(f"\n{Colors.CYAN}Available Components:{Colors.RESET}")
            component_menu = Menu("Select components to install:", menu_options, multi_select=True)
            selections = component_menu.display()
            
            if not selections:
                logger.warning("No components selected")
                return None
            
            return [available_components[i] for i in selections]
        
        return None
        
    except Exception as e:
        logger.error(f"Error in component selection: {e}")
        return None


def display_installation_plan(components: List[str], registry: ComponentRegistry, install_dir: Path) -> None:
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
                    instance = registry.get_component_instance(component_name, install_dir)
                    if instance and hasattr(instance, 'get_size_estimate'):
                        size = instance.get_size_estimate()
                        total_size += size
                except Exception:
                    pass
            else:
                print(f"  {i}. {component_name} - Unknown component")
        
        if total_size > 0:
            print(f"\n{Colors.BLUE}Estimated size:{Colors.RESET} {format_size(total_size)}")
        
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
    
    for check_name, check_info in diagnostics['checks'].items():
        status = check_info['status']
        message = check_info['message']
        
        if status == 'pass':
            print(f"  ✅ {check_name}: {message}")
        else:
            print(f"  ❌ {check_name}: {message}")
            all_passed = False
    
    # Display issues and recommendations
    if diagnostics['issues']:
        print(f"\n{Colors.YELLOW}Issues Found:{Colors.RESET}")
        for issue in diagnostics['issues']:
            print(f"  ⚠️  {issue}")
        
        print(f"\n{Colors.CYAN}Recommendations:{Colors.RESET}")
        for recommendation in diagnostics['recommendations']:
            print(recommendation)
    
    # Summary
    if all_passed:
        print(f"\n{Colors.GREEN}✅ All system checks passed! Your system is ready for SuperClaude.{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some issues found. Please address the recommendations above.{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
    if all_passed:
        print("  1. Run 'SuperClaude install' to proceed with installation")
        print("  2. Choose your preferred installation mode (quick, minimal, or custom)")
    else:
        print("  1. Install missing dependencies using the commands above")
        print("  2. Restart your terminal after installing tools")
        print("  3. Run 'SuperClaude install --diagnose' again to verify")


def perform_installation(components: List[str], args: argparse.Namespace) -> bool:
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
        component_instances = registry.create_component_instances(components, args.install_dir)
        
        if not component_instances:
            logger.error("No valid component instances created")
            return False
        
        # Register components with installer
        installer.register_components(list(component_instances.values()))
        
        # Resolve dependencies
        ordered_components = registry.resolve_dependencies(components)
        
        # Setup progress tracking
        progress = ProgressBar(
            total=len(ordered_components),
            prefix="Installing: ",
            suffix=""
        )
        
        # Install components
        logger.info(f"Installing {len(ordered_components)} components...")
        
        config = {
            "force": args.force,
            "backup": not args.no_backup,
            "dry_run": args.dry_run
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
            logger.success(f"Installation completed successfully in {duration:.1f} seconds")
            
            # Show summary
            summary = installer.get_installation_summary()
            if summary['installed']:
                logger.info(f"Installed components: {', '.join(summary['installed'])}")
            
            if summary['backup_path']:
                logger.info(f"Backup created: {summary['backup_path']}")
                
        else:
            logger.error(f"Installation completed with errors in {duration:.1f} seconds")
            
            summary = installer.get_installation_summary()
            if summary['failed']:
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
    # ✅ Inserted validation code
    expected_home = Path.home().resolve()
    actual_dir = args.install_dir.resolve()

    if not str(actual_dir).startswith(str(expected_home)):
        print(f"\n[✗] Installation must be inside your user profile directory.")
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
            display_header(
                "SuperClaude Installation v3.0",
                "Installing SuperClaude framework components"
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
        
        config_manager = ConfigManager(PROJECT_ROOT / "config")
        validator = Validator()
        
        # Validate configuration
        config_errors = config_manager.validate_config_files()
        if config_errors:
            logger.error("Configuration validation failed:")
            for error in config_errors:
                logger.error(f"  - {error}")
            return 1
        
        # Get components to install
        components = get_components_to_install(args, registry, config_manager)
        if not components:
            logger.error("No components selected for installation")
            return 1
        
        # Validate system requirements
        if not validate_system_requirements(validator, components):
            if not args.force:
                logger.error("System requirements not met. Use --force to override.")
                return 1
            else:
                logger.warning("System requirements not met, but continuing due to --force flag")
        
        # Check for existing installation
        if args.install_dir.exists() and not args.force:
            if not args.dry_run:
                logger.warning(f"Installation directory already exists: {args.install_dir}")
                if not args.yes and not confirm("Continue and update existing installation?", default=False):
                    logger.info("Installation cancelled by user")
                    return 0
        
        # Display installation plan
        if not args.quiet:
            display_installation_plan(components, registry, args.install_dir)
            
            if not args.dry_run:
                if not args.yes and not confirm("Proceed with installation?", default=True):
                    logger.info("Installation cancelled by user")
                    return 0
        
        # Perform installation
        success = perform_installation(components, args)
        
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
