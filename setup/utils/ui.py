"""
User interface utilities for SuperClaude installation system
Cross-platform console UI with colors and progress indication
"""

import sys
import time
import shutil
import getpass
from typing import List, Optional, Any, Dict, Union
from enum import Enum
from .symbols import symbols, safe_print, format_with_symbols

# Try to import colorama for cross-platform color support
try:
    import colorama
    from colorama import Fore, Back, Style

    colorama.init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

    # Fallback color codes for Unix-like systems
    class MockFore:
        RED = "\033[91m" if sys.platform != "win32" else ""
        GREEN = "\033[92m" if sys.platform != "win32" else ""
        YELLOW = "\033[93m" if sys.platform != "win32" else ""
        BLUE = "\033[94m" if sys.platform != "win32" else ""
        MAGENTA = "\033[95m" if sys.platform != "win32" else ""
        CYAN = "\033[96m" if sys.platform != "win32" else ""
        WHITE = "\033[97m" if sys.platform != "win32" else ""

    class MockStyle:
        RESET_ALL = "\033[0m" if sys.platform != "win32" else ""
        BRIGHT = "\033[1m" if sys.platform != "win32" else ""

    Fore = MockFore()
    Style = MockStyle()


class Colors:
    """Color constants for console output"""

    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL
    BRIGHT = Style.BRIGHT


class ProgressBar:
    """Cross-platform progress bar with customizable display"""

    def __init__(self, total: int, width: int = 50, prefix: str = "", suffix: str = ""):
        """
        Initialize progress bar

        Args:
            total: Total number of items to process
            width: Width of progress bar in characters
            prefix: Text to display before progress bar
            suffix: Text to display after progress bar
        """
        self.total = total
        self.width = width
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self.start_time = time.time()

        # Get terminal width for responsive display
        try:
            self.terminal_width = shutil.get_terminal_size().columns
        except OSError:
            self.terminal_width = 80

    def update(self, current: int, message: str = "") -> None:
        """
        Update progress bar

        Args:
            current: Current progress value
            message: Optional message to display
        """
        self.current = current
        percent = min(100, (current / self.total) * 100) if self.total > 0 else 100

        # Calculate filled and empty portions
        filled_width = (
            int(self.width * current / self.total) if self.total > 0 else self.width
        )
        filled = symbols.block_filled * filled_width
        empty = symbols.block_empty * (self.width - filled_width)

        # Calculate elapsed time and ETA
        elapsed = time.time() - self.start_time
        if current > 0:
            eta = (elapsed / current) * (self.total - current)
            eta_str = f" ETA: {self._format_time(eta)}"
        else:
            eta_str = ""

        # Format progress line
        if message:
            status = f" {message}"
        else:
            status = ""

        progress_line = (
            f"\r{self.prefix}[{Colors.GREEN}{filled}{Colors.WHITE}{empty}{Colors.RESET}] "
            f"{percent:5.1f}%{status}{eta_str}"
        )

        # Truncate if too long for terminal
        max_length = self.terminal_width - 5
        if len(progress_line) > max_length:
            # Remove color codes for length calculation
            plain_line = (
                progress_line.replace(Colors.GREEN, "")
                .replace(Colors.WHITE, "")
                .replace(Colors.RESET, "")
            )
            if len(plain_line) > max_length:
                progress_line = progress_line[:max_length] + "..."

        safe_print(progress_line, end="", flush=True)

    def increment(self, message: str = "") -> None:
        """
        Increment progress by 1

        Args:
            message: Optional message to display
        """
        self.update(self.current + 1, message)

    def finish(self, message: str = "Complete") -> None:
        """
        Complete progress bar

        Args:
            message: Completion message
        """
        self.update(self.total, message)
        print()  # New line after completion

    def _format_time(self, seconds: float) -> str:
        """Format time duration as human-readable string"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.0f}m {seconds%60:.0f}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}h {minutes:.0f}m"


class Menu:
    """Interactive menu system with keyboard navigation"""

    def __init__(self, title: str, options: List[str], multi_select: bool = False):
        """
        Initialize menu

        Args:
            title: Menu title
            options: List of menu options
            multi_select: Allow multiple selections
        """
        self.title = title
        self.options = options
        self.multi_select = multi_select
        self.selected = set() if multi_select else None

    def display(self) -> Union[int, List[int]]:
        """
        Display menu and get user selection

        Returns:
            Selected option index (single) or list of indices (multi-select)
        """
        print(f"\n{Colors.CYAN}{Colors.BRIGHT}{self.title}{Colors.RESET}")
        print("=" * len(self.title))

        for i, option in enumerate(self.options, 1):
            if self.multi_select:
                marker = "[x]" if i - 1 in (self.selected or set()) else "[ ]"
                print(f"{Colors.YELLOW}{i:2d}.{Colors.RESET} {marker} {option}")
            else:
                print(f"{Colors.YELLOW}{i:2d}.{Colors.RESET} {option}")

        if self.multi_select:
            print(
                f"\n{Colors.BLUE}Enter numbers separated by commas (e.g., 1,3,5) or 'all' for all options:{Colors.RESET}"
            )
        else:
            print(
                f"\n{Colors.BLUE}Enter your choice (1-{len(self.options)}):{Colors.RESET}"
            )

        while True:
            try:
                user_input = input("> ").strip().lower()

                if self.multi_select:
                    if user_input == "all":
                        return list(range(len(self.options)))
                    elif user_input == "":
                        return []
                    else:
                        # Parse comma-separated numbers
                        selections = []
                        for part in user_input.split(","):
                            part = part.strip()
                            if part.isdigit():
                                idx = int(part) - 1
                                if 0 <= idx < len(self.options):
                                    selections.append(idx)
                                else:
                                    raise ValueError(f"Invalid option: {part}")
                            else:
                                raise ValueError(f"Invalid input: {part}")
                        return list(set(selections))  # Remove duplicates
                else:
                    if user_input.isdigit():
                        choice = int(user_input) - 1
                        if 0 <= choice < len(self.options):
                            return choice
                        else:
                            print(
                                f"{Colors.RED}Invalid choice. Please enter a number between 1 and {len(self.options)}.{Colors.RESET}"
                            )
                    else:
                        print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")

            except (ValueError, KeyboardInterrupt) as e:
                if isinstance(e, KeyboardInterrupt):
                    print(f"\n{Colors.YELLOW}Operation cancelled.{Colors.RESET}")
                    return [] if self.multi_select else -1
                else:
                    print(f"{Colors.RED}Invalid input: {e}{Colors.RESET}")


def confirm(message: str, default: bool = True) -> bool:
    """
    Ask for user confirmation

    Args:
        message: Confirmation message
        default: Default response if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    suffix = "[Y/n]" if default else "[y/N]"
    print(f"{Colors.BLUE}{message} {suffix}{Colors.RESET}")

    while True:
        try:
            response = input("> ").strip().lower()

            if response == "":
                return default
            elif response in ["y", "yes", "true", "1"]:
                return True
            elif response in ["n", "no", "false", "0"]:
                return False
            else:
                print(
                    f"{Colors.RED}Please enter 'y' or 'n' (or press Enter for default).{Colors.RESET}"
                )

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Operation cancelled.{Colors.RESET}")
            return False


def display_header(title: str, subtitle: str = "") -> None:
    """
    Display formatted header

    Args:
        title: Main title
        subtitle: Optional subtitle
    """
    from superclaude import __author__, __email__

    print(f"\n{Colors.CYAN}{Colors.BRIGHT}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BRIGHT}{title:^60}{Colors.RESET}")
    if subtitle:
        print(f"{Colors.WHITE}{subtitle:^60}{Colors.RESET}")

    # Display authors
    authors = [a.strip() for a in __author__.split(",")]
    emails = [e.strip() for e in __email__.split(",")]

    author_lines = []
    for i in range(len(authors)):
        name = authors[i]
        email = emails[i] if i < len(emails) else ""
        author_lines.append(f"{name} <{email}>")

    authors_str = " | ".join(author_lines)
    print(f"{Colors.BLUE}{authors_str:^60}{Colors.RESET}")

    print(f"{Colors.CYAN}{Colors.BRIGHT}{'='*60}{Colors.RESET}\n")


def display_authors() -> None:
    """Display author information"""
    from superclaude import __author__, __email__, __github__

    print(f"\n{Colors.CYAN}{Colors.BRIGHT}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BRIGHT}{'superclaude Authors':^60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BRIGHT}{'='*60}{Colors.RESET}\n")

    authors = [a.strip() for a in __author__.split(",")]
    emails = [e.strip() for e in __email__.split(",")]
    github_users = [g.strip() for g in __github__.split(",")]

    for i in range(len(authors)):
        name = authors[i]
        email = emails[i] if i < len(emails) else "N/A"
        github = github_users[i] if i < len(github_users) else "N/A"

        print(f"  {Colors.BRIGHT}{name}{Colors.RESET}")
        print(f"    Email: {Colors.YELLOW}{email}{Colors.RESET}")
        print(f"    GitHub: {Colors.YELLOW}https://github.com/{github}{Colors.RESET}")
        print()

    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def display_info(message: str) -> None:
    """Display info message"""
    print(f"{Colors.BLUE}[INFO] {message}{Colors.RESET}")


def display_success(message: str) -> None:
    """Display success message"""
    safe_print(f"{Colors.GREEN}[{symbols.checkmark}] {message}{Colors.RESET}")


def display_warning(message: str) -> None:
    """Display warning message"""
    print(f"{Colors.YELLOW}[!] {message}{Colors.RESET}")


def display_error(message: str) -> None:
    """Display error message"""
    safe_print(f"{Colors.RED}[{symbols.crossmark}] {message}{Colors.RESET}")


def display_step(step: int, total: int, message: str) -> None:
    """Display step progress"""
    print(f"{Colors.CYAN}[{step}/{total}] {message}{Colors.RESET}")


def display_table(headers: List[str], rows: List[List[str]], title: str = "") -> None:
    """
    Display data in table format

    Args:
        headers: Column headers
        rows: Data rows
        title: Optional table title
    """
    if not rows:
        return

    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Display title
    if title:
        print(f"\n{Colors.CYAN}{Colors.BRIGHT}{title}{Colors.RESET}")
        print()

    # Display headers
    header_line = " | ".join(
        f"{header:<{col_widths[i]}}" for i, header in enumerate(headers)
    )
    print(f"{Colors.YELLOW}{header_line}{Colors.RESET}")
    print("-" * len(header_line))

    # Display rows
    for row in rows:
        row_line = " | ".join(
            f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row)
        )
        print(row_line)

    print()


def prompt_api_key(service_name: str, env_var_name: str) -> Optional[str]:
    """
    Prompt for API key with security and UX best practices

    Args:
        service_name: Human-readable service name (e.g., "Magic", "Morphllm")
        env_var_name: Environment variable name (e.g., "TWENTYFIRST_API_KEY")

    Returns:
        API key string if provided, None if skipped
    """
    print(
        f"{Colors.BLUE}[API KEY] {service_name} requires: {Colors.BRIGHT}{env_var_name}{Colors.RESET}"
    )
    print(
        f"{Colors.WHITE}Visit the service documentation to obtain your API key{Colors.RESET}"
    )
    print(
        f"{Colors.YELLOW}Press Enter to skip (you can set this manually later){Colors.RESET}"
    )

    try:
        # Use getpass for hidden input
        api_key = getpass.getpass(f"Enter {env_var_name}: ").strip()

        if not api_key:
            print(
                f"{Colors.YELLOW}[SKIPPED] {env_var_name} - set manually later{Colors.RESET}"
            )
            return None

        # Basic validation (non-empty, reasonable length)
        if len(api_key) < 10:
            print(
                f"{Colors.RED}[WARNING] API key seems too short. Continue anyway? (y/N){Colors.RESET}"
            )
            if not confirm("", default=False):
                return None

        safe_print(
            f"{Colors.GREEN}[{symbols.checkmark}] {env_var_name} configured{Colors.RESET}"
        )
        return api_key

    except KeyboardInterrupt:
        safe_print(f"\n{Colors.YELLOW}[SKIPPED] {env_var_name}{Colors.RESET}")
        return None


def wait_for_key(message: str = "Press Enter to continue...") -> None:
    """Wait for user to press a key"""
    try:
        input(f"{Colors.BLUE}{message}{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled.{Colors.RESET}")


def clear_screen() -> None:
    """Clear terminal screen"""
    import os

    os.system("cls" if os.name == "nt" else "clear")


class StatusSpinner:
    """Simple status spinner for long operations"""

    def __init__(self, message: str = "Working..."):
        """
        Initialize spinner

        Args:
            message: Message to display with spinner
        """
        self.message = message
        self.spinning = False
        self.chars = symbols.spinner_chars
        self.current = 0

    def start(self) -> None:
        """Start spinner in background thread"""
        import threading

        def spin():
            while self.spinning:
                char = self.chars[self.current % len(self.chars)]
                safe_print(
                    f"\r{Colors.BLUE}{char} {self.message}{Colors.RESET}",
                    end="",
                    flush=True,
                )
                self.current += 1
                time.sleep(0.1)

        self.spinning = True
        self.thread = threading.Thread(target=spin, daemon=True)
        self.thread.start()

    def stop(self, final_message: str = "") -> None:
        """
        Stop spinner

        Args:
            final_message: Final message to display
        """
        self.spinning = False
        if hasattr(self, "thread"):
            self.thread.join(timeout=0.2)

        # Clear spinner line
        safe_print(f"\r{' ' * (len(self.message) + 5)}\r", end="")

        if final_message:
            safe_print(final_message)


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with optional suffix"""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
