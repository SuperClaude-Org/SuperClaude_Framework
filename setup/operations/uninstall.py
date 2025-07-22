"""
SuperClaude Uninstall Operation Module
Refactored from uninstall.py for unified CLI hub
"""

import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import argparse

from ..core.registry import ComponentRegistry
from ..managers.settings_manager import SettingsManager
from ..managers.file_manager import FileManager
from ..utils.ui import (
    display_header, display_info, display_success, display_error, 
    display_warning, Menu, confirm, ProgressBar, Colors
)
from ..utils.logger import get_logger
from .. import DEFAULT_INSTALL_DIR, PROJECT_ROOT
from . import OperationBase


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
        parents=parents
    )
    
    # Uninstall mode options
    parser.add_argument(
        "--components",
        type=str,
        nargs="+",
        help="Specific components to uninstall"
    )
    
    parser.add_argument(
        "--complete",
        action="store_true",
        help="Complete uninstall (remove all files and directories)"
    )
    
    # Data preservation options
    parser.add_argument(
        "--keep-backups",
        action="store_true",
        help="Keep backup files during uninstall"
    )
    
    parser.add_argument(
        "--keep-logs",
        action="store_true",
        help="Keep log files during uninstall"
    )
    
    parser.add_argument(
        "--keep-settings",
        action="store_true",
        help="Keep user settings during uninstall"
    )
    
    # Safety options
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompts (use with caution)"
    )
    
    return parser

def get_installed_components(install_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Get currently installed components and their versions"""
    try:
        settings_manager = SettingsManager(install_dir)
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
        "total_size": 0
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
        from ..utils.ui import format_size
        print(f"{Colors.BLUE}Total Size:{Colors.RESET} {format_size(info['total_size'])}")
    
    print()


def get_components_to_uninstall(args: argparse.Namespace, installed_components: Dict[str, str]) -> Optional[List[str]]:
    """Determine which components to uninstall"""
    logger = get_logger()
    
    # Complete uninstall
    if args.complete:
        return list(installed_components.keys())
    
    # Explicit components specified
    if args.components:
        # Validate that specified components are installed
        invalid_components = [c for c in args.components if c not in installed_components]
        if invalid_components:
            logger.error(f"Components not installed: {invalid_components}")
            return None
        return args.components
    
    # Interactive selection
    return interactive_uninstall_selection(installed_components)


def interactive_uninstall_selection(installed_components: Dict[str, str]) -> Optional[List[str]]:
    """Interactive uninstall selection"""
    if not installed_components:
        return []
    
    print(f"\n{Colors.CYAN}Uninstall Options:{Colors.RESET}")
    
    # Create menu options
    preset_options = [
        "Complete Uninstall (remove everything)",
        "Remove Specific Components",
        "Cancel Uninstall"
    ]
    
    menu = Menu("Select uninstall option:", preset_options)
    choice = menu.display()
    
    if choice == -1 or choice == 2:  # Cancelled
        return None
    elif choice == 0:  # Complete uninstall
        return list(installed_components.keys())
    elif choice == 1:  # Select specific components
        component_options = []
        component_names = []
        
        for component, version in installed_components.items():
            component_options.append(f"{component} (v{version})")
            component_names.append(component)
        
        component_menu = Menu("Select components to uninstall:", component_options, multi_select=True)
        selections = component_menu.display()
        
        if not selections:
            return None
        
        return [component_names[i] for i in selections]
    
    return None


def display_uninstall_plan(components: List[str], args: argparse.Namespace, info: Dict[str, Any]) -> None:
    """Display uninstall plan"""
    print(f"\n{Colors.CYAN}{Colors.BRIGHT}Uninstall Plan{Colors.RESET}")
    print("=" * 50)
    
    print(f"{Colors.BLUE}Installation Directory:{Colors.RESET} {info['install_dir']}")
    
    if components:
        print(f"{Colors.BLUE}Components to remove:{Colors.RESET}")
        for i, component_name in enumerate(components, 1):
            version = info["components"].get(component_name, "unknown")
            print(f"  {i}. {component_name} (v{version})")
    
    # Show what will be preserved
    preserved = []
    if args.keep_backups:
        preserved.append("backup files")
    if args.keep_logs:
        preserved.append("log files")
    if args.keep_settings:
        preserved.append("user settings")
    
    if preserved:
        print(f"{Colors.GREEN}Will preserve:{Colors.RESET} {', '.join(preserved)}")
    
    if args.complete:
        print(f"{Colors.RED}WARNING: Complete uninstall will remove all SuperClaude files{Colors.RESET}")
    
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
                settings_manager = SettingsManager(install_dir)
                # This would need component-specific backup logic
                pass
        
        logger.success(f"Backup created: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.warning(f"Could not create backup: {e}")
        return None


def perform_uninstall(components: List[str], args: argparse.Namespace, info: Dict[str, Any]) -> bool:
    """Perform the actual uninstall"""
    logger = get_logger()
    start_time = time.time()
    
    try:
        # Create component registry
        registry = ComponentRegistry(PROJECT_ROOT / "setup" / "components")
        registry.discover_components()
        
        # Create component instances
        component_instances = registry.create_component_instances(components, args.install_dir)
        
        # Setup progress tracking
        progress = ProgressBar(
            total=len(components),
            prefix="Uninstalling: ",
            suffix=""
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
        
        # Show results
        duration = time.time() - start_time
        
        if failed_components:
            logger.warning(f"Uninstall completed with some failures in {duration:.1f} seconds")
            logger.warning(f"Failed components: {', '.join(failed_components)}")
        else:
            logger.success(f"Uninstall completed successfully in {duration:.1f} seconds")
        
        if uninstalled_components:
            logger.info(f"Uninstalled components: {', '.join(uninstalled_components)}")
        
        return len(failed_components) == 0
        
    except Exception as e:
        logger.exception(f"Unexpected error during uninstall: {e}")
        return False


def cleanup_installation_directory(install_dir: Path, args: argparse.Namespace) -> None:
    """Clean up installation directory for complete uninstall"""
    logger = get_logger()
    file_manager = FileManager()
    
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
                logger.warning(f"Could not remove installation directory: {install_dir}")
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
                "SuperClaude Uninstall v3.0",
                "Removing SuperClaude framework components"
            )
        
        # Get installation information
        info = get_installation_info(args.install_dir)
        
        # Display current installation
        if not args.quiet:
            display_uninstall_info(info)
        
        # Check if SuperClaude is installed
        if not info["exists"]:
            logger.warning(f"No SuperClaude installation found in {args.install_dir}")
            return 0
        
        # Get components to uninstall
        components = get_components_to_uninstall(args, info["components"])
        if components is None:
            logger.info("Uninstall cancelled by user")
            return 0
        elif not components:
            logger.info("No components selected for uninstall")
            return 0
        
        # Display uninstall plan
        if not args.quiet:
            display_uninstall_plan(components, args, info)
        
        # Confirmation
        if not args.no_confirm and not args.yes:
            if args.complete:
                warning_msg = "This will completely remove SuperClaude. Continue?"
            else:
                warning_msg = f"This will remove {len(components)} component(s). Continue?"
            
            if not confirm(warning_msg, default=False):
                logger.info("Uninstall cancelled by user")
                return 0
        
        # Create backup if not dry run and not keeping backups
        if not args.dry_run and not args.keep_backups:
            create_uninstall_backup(args.install_dir, components)
        
        # Perform uninstall
        success = perform_uninstall(components, args, info)
        
        if success:
            if not args.quiet:
                display_success("SuperClaude uninstall completed successfully!")
                
                if not args.dry_run:
                    print(f"\n{Colors.CYAN}Uninstall complete:{Colors.RESET}")
                    print(f"SuperClaude has been removed from {args.install_dir}")
                    if not args.complete:
                        print(f"You can reinstall anytime using 'SuperClaude install'")
                    
            return 0
        else:
            display_error("Uninstall completed with some failures. Check logs for details.")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Uninstall cancelled by user{Colors.RESET}")
        return 130
    except Exception as e:
        return operation.handle_operation_error("uninstall", e)
