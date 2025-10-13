"""
SuperClaude CLI Base Module

Base class for all CLI operations providing common functionality
"""

from pathlib import Path

# Read version from VERSION file
try:
    __version__ = (Path(__file__).parent.parent.parent / "VERSION").read_text().strip()
except Exception:
    __version__ = "4.1.5"  # Fallback


def get_command_info():
    """Get information about available commands"""
    return {
        "install": {
            "name": "install",
            "description": "Install SuperClaude framework components",
            "module": "setup.cli.commands.install",
        },
        "update": {
            "name": "update",
            "description": "Update existing SuperClaude installation",
            "module": "setup.cli.commands.update",
        },
        "uninstall": {
            "name": "uninstall",
            "description": "Remove SuperClaude framework installation",
            "module": "setup.cli.commands.uninstall",
        },
        "backup": {
            "name": "backup",
            "description": "Backup and restore SuperClaude installations",
            "module": "setup.cli.commands.backup",
        },
    }


class OperationBase:
    """Base class for all operations providing common functionality"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.logger = None

    def setup_operation_logging(self, args):
        """Setup operation-specific logging"""
        from ..utils.logger import get_logger

        self.logger = get_logger()
        self.logger.info(f"Starting {self.operation_name} operation")

    def validate_global_args(self, args):
        """Validate global arguments common to all operations"""
        errors = []

        # Validate install directory
        if hasattr(args, "install_dir") and args.install_dir:
            from ..utils.security import SecurityValidator

            is_safe, validation_errors = SecurityValidator.validate_installation_target(
                args.install_dir
            )
            if not is_safe:
                errors.extend(validation_errors)

        # Check for conflicting flags
        if hasattr(args, "verbose") and hasattr(args, "quiet"):
            if args.verbose and args.quiet:
                errors.append("Cannot specify both --verbose and --quiet")

        return len(errors) == 0, errors

    def handle_operation_error(self, operation: str, error: Exception):
        """Standard error handling for operations"""
        if self.logger:
            self.logger.exception(f"Error in {operation} operation: {error}")
        else:
            print(f"Error in {operation} operation: {error}")
        return 1
