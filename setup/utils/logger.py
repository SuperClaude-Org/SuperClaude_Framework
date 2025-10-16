"""
Logging system for SuperClaude installation suite
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

from rich.console import Console
from .symbols import symbols
from .paths import get_home_directory

# Rich console for colored output
console = Console()


class LogLevel(Enum):
    """Log levels"""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Logger:
    """Enhanced logger with console and file output"""

    def __init__(
        self,
        name: str = "superclaude",
        log_dir: Optional[Path] = None,
        console_level: LogLevel = LogLevel.INFO,
        file_level: LogLevel = LogLevel.DEBUG,
    ):
        """
        Initialize logger

        Args:
            name: Logger name
            log_dir: Directory for log files (defaults to ~/.claude/logs)
            console_level: Minimum level for console output
            file_level: Minimum level for file output
        """
        self.name = name
        self.log_dir = log_dir or (get_home_directory() / ".claude" / "logs")
        self.console_level = console_level
        self.file_level = file_level
        self.session_start = datetime.now()

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Accept all levels, handlers will filter

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()

        self.log_counts: Dict[str, int] = {
            "debug": 0,
            "info": 0,
            "warning": 0,
            "error": 0,
            "critical": 0,
        }

    def _setup_console_handler(self) -> None:
        """Setup colorized console handler using rich"""
        from rich.logging import RichHandler

        handler = RichHandler(
            console=console,
            show_time=False,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
        )
        handler.setLevel(self.console_level.value)

        # Simple formatter (rich handles coloring)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def _setup_file_handler(self) -> None:
        """Setup file handler with rotation"""
        try:
            # Ensure log directory exists
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped log file
            timestamp = self.session_start.strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"{self.name}_{timestamp}.log"

            handler = logging.FileHandler(log_file, encoding="utf-8")
            handler.setLevel(self.file_level.value)

            # Detailed formatter for files
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)
            self.log_file = log_file

            # Clean up old log files (keep last 10)
            self._cleanup_old_logs()

        except Exception as e:
            # If file logging fails, continue with console only
            console.print(f"[yellow][!] Could not setup file logging: {e}[/yellow]")
            self.log_file = None

    def _cleanup_old_logs(self, keep_count: int = 10) -> None:
        """Clean up old log files"""
        try:
            # Get all log files for this logger
            log_files = list(self.log_dir.glob(f"{self.name}_*.log"))

            # Sort by modification time, newest first
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Remove old files
            for old_file in log_files[keep_count:]:
                try:
                    old_file.unlink()
                except OSError:
                    pass  # Ignore errors when cleaning up

        except Exception:
            pass  # Ignore cleanup errors

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(message, **kwargs)
        self.log_counts["debug"] += 1

    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(message, **kwargs)
        self.log_counts["info"] += 1

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(message, **kwargs)
        self.log_counts["warning"] += 1

    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self.logger.error(message, **kwargs)
        self.log_counts["error"] += 1

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(message, **kwargs)
        self.log_counts["critical"] += 1

    def success(self, message: str, **kwargs) -> None:
        """Log success message (info level with special formatting)"""
        # Use rich markup for success messages
        success_msg = f"[green]{symbols.checkmark} {message}[/green]"
        self.logger.info(success_msg, **kwargs)
        self.log_counts["info"] += 1

    def step(self, step: int, total: int, message: str, **kwargs) -> None:
        """Log step progress"""
        step_msg = f"[{step}/{total}] {message}"
        self.info(step_msg, **kwargs)

    def section(self, title: str, **kwargs) -> None:
        """Log section header"""
        separator = "=" * min(50, len(title) + 4)
        self.info(separator, **kwargs)
        self.info(f"  {title}", **kwargs)
        self.info(separator, **kwargs)

    def exception(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """Log exception with traceback"""
        self.logger.error(message, exc_info=exc_info, **kwargs)
        self.log_counts["error"] += 1

    def log_system_info(self, info: Dict[str, Any]) -> None:
        """Log system information"""
        self.section("System Information")
        for key, value in info.items():
            self.info(f"{key}: {value}")

    def log_operation_start(
        self, operation: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log start of operation"""
        self.section(f"Starting: {operation}")
        if details:
            for key, value in details.items():
                self.info(f"{key}: {value}")

    def log_operation_end(
        self,
        operation: str,
        success: bool,
        duration: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log end of operation"""
        status = "SUCCESS" if success else "FAILED"
        self.info(
            f"Operation {operation} completed: {status} (Duration: {duration:.2f}s)"
        )

        if details:
            for key, value in details.items():
                self.info(f"{key}: {value}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        runtime = datetime.now() - self.session_start

        return {
            "session_start": self.session_start.isoformat(),
            "runtime_seconds": runtime.total_seconds(),
            "log_counts": self.log_counts.copy(),
            "total_messages": sum(self.log_counts.values()),
            "log_file": (
                str(self.log_file)
                if hasattr(self, "log_file") and self.log_file
                else None
            ),
            "has_errors": self.log_counts["error"] + self.log_counts["critical"] > 0,
        }

    def set_console_level(self, level: LogLevel) -> None:
        """Change console logging level"""
        self.console_level = level
        if self.logger.handlers:
            self.logger.handlers[0].setLevel(level.value)

    def set_file_level(self, level: LogLevel) -> None:
        """Change file logging level"""
        self.file_level = level
        if len(self.logger.handlers) > 1:
            self.logger.handlers[1].setLevel(level.value)

    def flush(self) -> None:
        """Flush all handlers"""
        for handler in self.logger.handlers:
            if hasattr(handler, "flush"):
                handler.flush()

    def close(self) -> None:
        """Close logger and handlers"""
        self.section("Installation Session Complete")
        stats = self.get_statistics()

        self.info(f"Total runtime: {stats['runtime_seconds']:.1f} seconds")
        self.info(f"Messages logged: {stats['total_messages']}")
        if stats["has_errors"]:
            self.warning(
                f"Errors/warnings: {stats['log_counts']['error'] + stats['log_counts']['warning']}"
            )

        if stats["log_file"]:
            self.info(f"Full log saved to: {stats['log_file']}")

        # Close all handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


# Global logger instance
_global_logger: Optional[Logger] = None


def get_logger(name: str = "superclaude") -> Logger:
    """Get or create global logger instance"""
    global _global_logger

    if _global_logger is None or _global_logger.name != name:
        _global_logger = Logger(name)

    return _global_logger


def setup_logging(
    name: str = "superclaude",
    log_dir: Optional[Path] = None,
    console_level: LogLevel = LogLevel.INFO,
    file_level: LogLevel = LogLevel.DEBUG,
) -> Logger:
    """Setup logging with specified configuration"""
    global _global_logger
    _global_logger = Logger(name, log_dir, console_level, file_level)
    return _global_logger


# Convenience functions using global logger
def debug(message: str, **kwargs) -> None:
    """Log debug message using global logger"""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs) -> None:
    """Log info message using global logger"""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs) -> None:
    """Log warning message using global logger"""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs) -> None:
    """Log error message using global logger"""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs) -> None:
    """Log critical message using global logger"""
    get_logger().critical(message, **kwargs)


def success(message: str, **kwargs) -> None:
    """Log success message using global logger"""
    get_logger().success(message, **kwargs)
