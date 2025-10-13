"""
Windows-compatible symbol fallbacks for SuperClaude UI
Handles Unicode encoding issues on Windows terminals
"""

import sys
import os
import platform


def can_display_unicode() -> bool:
    """
    Detect if terminal can display Unicode symbols safely

    Returns:
        True if Unicode is safe to use, False if fallbacks needed
    """
    # Check if we're on Windows with problematic encoding
    if platform.system() == "Windows":
        # Check console encoding
        try:
            # Test if we can encode common Unicode symbols
            test_symbols = "✓✗█░⠋═"
            test_symbols.encode(sys.stdout.encoding or "cp1252")
            return True
        except (UnicodeEncodeError, LookupError):
            return False

    # Check if stdout encoding supports Unicode
    encoding = getattr(sys.stdout, "encoding", None)
    if encoding and encoding.lower() in ["utf-8", "utf8"]:
        return True

    # Conservative fallback for unknown systems
    return False


class Symbols:
    """Cross-platform symbol definitions with Windows fallbacks"""

    def __init__(self):
        self.unicode_safe = can_display_unicode()

    @property
    def checkmark(self) -> str:
        """Success checkmark symbol"""
        return "✓" if self.unicode_safe else "+"

    @property
    def crossmark(self) -> str:
        """Error/failure cross symbol"""
        return "✗" if self.unicode_safe else "x"

    @property
    def block_filled(self) -> str:
        """Filled block for progress bars"""
        return "█" if self.unicode_safe else "#"

    @property
    def block_empty(self) -> str:
        """Empty block for progress bars"""
        return "░" if self.unicode_safe else "-"

    @property
    def double_line(self) -> str:
        """Double line separator"""
        return "═" if self.unicode_safe else "="

    @property
    def spinner_chars(self) -> str:
        """Spinner animation characters"""
        if self.unicode_safe:
            return "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        else:
            return "|/-\\|/-\\"

    @property
    def box_top_left(self) -> str:
        """Box drawing: top-left corner"""
        return "╔" if self.unicode_safe else "+"

    @property
    def box_top_right(self) -> str:
        """Box drawing: top-right corner"""
        return "╗" if self.unicode_safe else "+"

    @property
    def box_bottom_left(self) -> str:
        """Box drawing: bottom-left corner"""
        return "╚" if self.unicode_safe else "+"

    @property
    def box_bottom_right(self) -> str:
        """Box drawing: bottom-right corner"""
        return "╝" if self.unicode_safe else "+"

    @property
    def box_horizontal(self) -> str:
        """Box drawing: horizontal line"""
        return "═" if self.unicode_safe else "="

    @property
    def box_vertical(self) -> str:
        """Box drawing: vertical line"""
        return "║" if self.unicode_safe else "|"

    def make_separator(self, length: int) -> str:
        """Create a separator line of specified length"""
        return self.double_line * length

    def make_box_line(self, length: int) -> str:
        """Create a box horizontal line of specified length"""
        return self.box_horizontal * length


# Global instance for easy import
symbols = Symbols()


def safe_print(*args, **kwargs):
    """
    Print function that handles Unicode encoding errors gracefully

    Falls back to ASCII-safe representation if Unicode fails
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Convert arguments to safe strings
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace problematic Unicode characters
                safe_arg = (
                    arg.replace("✓", "+")
                    .replace("✗", "x")
                    .replace("█", "#")
                    .replace("░", "-")
                    .replace("═", "=")
                    .replace("⠋", "|")
                    .replace("⠙", "/")
                    .replace("⠹", "-")
                    .replace("⠸", "\\")
                    .replace("⠼", "|")
                    .replace("⠴", "/")
                    .replace("⠦", "-")
                    .replace("⠧", "\\")
                    .replace("⠇", "|")
                    .replace("⠏", "/")
                    .replace("╔", "+")
                    .replace("╗", "+")
                    .replace("╚", "+")
                    .replace("╝", "+")
                    .replace("║", "|")
                )
                safe_args.append(safe_arg)
            else:
                safe_args.append(str(arg))

        # Try printing with safe arguments
        try:
            print(*safe_args, **kwargs)
        except UnicodeEncodeError:
            # Last resort: encode to ASCII with replacement
            final_args = []
            for arg in safe_args:
                if isinstance(arg, str):
                    final_args.append(arg.encode("ascii", "replace").decode("ascii"))
                else:
                    final_args.append(str(arg))
            print(*final_args, **kwargs)


def format_with_symbols(text: str) -> str:
    """
    Replace Unicode symbols in text with Windows-compatible alternatives
    """
    if symbols.unicode_safe:
        return text

    # Replace symbols with safe alternatives
    replacements = {
        "✓": symbols.checkmark,
        "✗": symbols.crossmark,
        "█": symbols.block_filled,
        "░": symbols.block_empty,
        "═": symbols.double_line,
        "╔": symbols.box_top_left,
        "╗": symbols.box_top_right,
        "╚": symbols.box_bottom_left,
        "╝": symbols.box_bottom_right,
        "║": symbols.box_vertical,
    }

    for unicode_char, safe_char in replacements.items():
        text = text.replace(unicode_char, safe_char)

    return text
