"""
Minimal backward-compatible UI utilities
Stub implementation for legacy installer code
"""


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BRIGHT = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def display_header(title: str, subtitle: str = "") -> None:
    """Display a formatted header"""
    print(f"\n{Colors.CYAN}{Colors.BRIGHT}{title}{Colors.RESET}")
    if subtitle:
        print(f"{Colors.DIM}{subtitle}{Colors.RESET}")
    print()


def display_success(message: str) -> None:
    """Display a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def display_error(message: str) -> None:
    """Display an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def display_warning(message: str) -> None:
    """Display a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def display_info(message: str) -> None:
    """Display an info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")


def confirm(prompt: str, default: bool = True) -> bool:
    """
    Simple confirmation prompt

    Args:
        prompt: The prompt message
        default: Default response if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ("y", "yes")


class Menu:
    """Minimal menu implementation"""

    def __init__(self, title: str, options: list, multi_select: bool = False):
        self.title = title
        self.options = options
        self.multi_select = multi_select

    def display(self):
        """Display menu and get selection"""
        print(f"\n{Colors.CYAN}{Colors.BRIGHT}{self.title}{Colors.RESET}\n")

        for i, option in enumerate(self.options, 1):
            print(f"{i}. {option}")

        if self.multi_select:
            print(f"\n{Colors.DIM}Enter comma-separated numbers (e.g., 1,3,5) or 'all' for all options{Colors.RESET}")
            while True:
                try:
                    choice = input(f"Select [1-{len(self.options)}]: ").strip().lower()

                    if choice == "all":
                        return list(range(len(self.options)))

                    if not choice:
                        return []

                    selections = [int(x.strip()) - 1 for x in choice.split(",")]
                    if all(0 <= s < len(self.options) for s in selections):
                        return selections
                    print(f"{Colors.RED}Invalid selection{Colors.RESET}")
                except (ValueError, KeyboardInterrupt):
                    print(f"\n{Colors.RED}Invalid input{Colors.RESET}")
        else:
            while True:
                try:
                    choice = input(f"\nSelect [1-{len(self.options)}]: ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(self.options):
                        return choice_num - 1
                    print(f"{Colors.RED}Invalid selection{Colors.RESET}")
                except (ValueError, KeyboardInterrupt):
                    print(f"\n{Colors.RED}Invalid input{Colors.RESET}")


class ProgressBar:
    """Minimal progress bar implementation"""

    def __init__(self, total: int, prefix: str = "", suffix: str = ""):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0

    def update(self, current: int = None, message: str = None) -> None:
        """Update progress"""
        if current is not None:
            self.current = current
        else:
            self.current += 1

        percent = int((self.current / self.total) * 100) if self.total > 0 else 100
        display_msg = message or f"{self.prefix}{self.current}/{self.total} {self.suffix}"
        print(f"\r{display_msg} {percent}%", end="", flush=True)

        if self.current >= self.total:
            print()  # New line when complete

    def finish(self, message: str = "Complete") -> None:
        """Finish progress bar"""
        self.current = self.total
        print(f"\r{message} 100%")

    def close(self) -> None:
        """Close progress bar"""
        if self.current < self.total:
            print()


def format_size(size: int) -> str:
    """
    Format size in bytes to human-readable string

    Args:
        size: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB", "256 KB")
    """
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"


def prompt_api_key(service_name: str, env_var_name: str) -> str:
    """
    Prompt user for API key

    Args:
        service_name: Name of the service requiring the key
        env_var_name: Environment variable name for the key

    Returns:
        API key string (empty if user skips)
    """
    print(f"\n{Colors.CYAN}{service_name} API Key{Colors.RESET}")
    print(f"{Colors.DIM}Environment variable: {env_var_name}{Colors.RESET}")
    print(f"{Colors.YELLOW}Press Enter to skip{Colors.RESET}")

    try:
        # Use getpass for password-like input (hidden)
        import getpass

        key = getpass.getpass("Enter API key: ").strip()
        return key
    except (EOFError, KeyboardInterrupt):
        print(f"\n{Colors.YELLOW}Skipped{Colors.RESET}")
        return ""
