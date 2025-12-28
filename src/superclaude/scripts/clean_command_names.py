#!/usr/bin/env python3
"""
SuperClaude Plugin - Command Name Attribute Cleanup Script

This script automatically removes redundant 'name:' attributes from command
frontmatter in markdown files. The plugin naming system derives command names
from the plugin name + filename, making explicit name attributes unnecessary.

Usage:
    python scripts/clean_command_names.py

Exit Codes:
    0 - Success (files modified or no changes needed)
    1 - Error (directory not found or processing failed)
"""

import re
import sys
from pathlib import Path
from typing import Tuple


def find_project_root() -> Path:
    """
    Find the project root directory by locating plugin.json.

    Returns:
        Path: Project root directory

    Raises:
        FileNotFoundError: If project root cannot be determined
    """
    script_dir = Path(__file__).parent.absolute()
    current_dir = script_dir.parent

    # Look for plugin.json up to 3 levels up
    for _ in range(3):
        if (current_dir / "plugin.json").exists():
            return current_dir
        current_dir = current_dir.parent

    raise FileNotFoundError("Could not find project root (plugin.json not found)")


def clean_name_attributes(content: str) -> Tuple[str, bool]:
    """
    Remove 'name:' attributes from YAML frontmatter.

    Args:
        content: File content as string

    Returns:
        Tuple of (cleaned content, was_modified)
    """
    # Pattern to match 'name: value' in frontmatter
    # Matches: name: value, name : value, NAME: value (case-insensitive)
    name_pattern = re.compile(r"^\s*name\s*:\s*.*$", re.MULTILINE | re.IGNORECASE)

    # Check if modification is needed
    if not name_pattern.search(content):
        return content, False

    # Remove name attributes
    cleaned = name_pattern.sub("", content)

    # Clean up multiple consecutive newlines (max 2)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Remove trailing whitespace while preserving final newline
    cleaned = cleaned.rstrip() + "\n" if cleaned.strip() else ""

    return cleaned, True


def process_commands_directory(commands_dir: Path) -> int:
    """
    Process all command markdown files in directory.

    Args:
        commands_dir: Path to commands directory

    Returns:
        Number of files modified
    """
    if not commands_dir.is_dir():
        print(f"Error: Directory not found: {commands_dir}", file=sys.stderr)
        return -1

    modified_count = 0
    processed_count = 0
    error_count = 0

    print(f"🔍 Scanning: {commands_dir}")
    print(f"{'=' * 60}")

    # Process all .md files
    for md_file in sorted(commands_dir.glob("*.md")):
        processed_count += 1

        try:
            # Read file content
            content = md_file.read_text(encoding="utf-8")

            # Clean name attributes
            cleaned_content, was_modified = clean_name_attributes(content)

            if was_modified:
                # Write cleaned content back
                md_file.write_text(cleaned_content, encoding="utf-8")
                modified_count += 1
                print(f"✅ Modified: {md_file.name}")
            else:
                print(f"⏭️  Skipped:  {md_file.name} (no name attribute)")

        except Exception as e:
            error_count += 1
            print(f"❌ Error:    {md_file.name} - {e}", file=sys.stderr)

    print("=" * 60)
    print("📊 Summary:")
    print(f"   • Processed: {processed_count} files")
    print(f"   • Modified:  {modified_count} files")
    print(f"   • Errors:    {error_count} files")

    return modified_count if error_count == 0 else -1


def main() -> int:
    """
    Main execution function.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    print("🚀 SuperClaude Plugin - Command Name Cleanup")
    print()

    try:
        # Find project root and commands directory
        project_root = find_project_root()
        commands_dir = project_root / "commands"

        print(f"📁 Project root: {project_root}")
        print()

        # Process commands directory
        result = process_commands_directory(commands_dir)

        if result < 0:
            print("\n❌ Cleanup failed with errors", file=sys.stderr)
            return 1

        print("\n✅ Cleanup completed successfully")
        return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
