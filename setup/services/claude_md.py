"""
CLAUDE.md Manager for preserving user customizations while managing framework imports
"""

import re
from pathlib import Path
from typing import List, Set, Dict, Optional
from ..utils.logger import get_logger


class CLAUDEMdService:
    """Manages CLAUDE.md file updates while preserving user customizations"""

    def __init__(self, install_dir: Path):
        """
        Initialize CLAUDEMdService

        Args:
            install_dir: Installation directory (typically ~/.claude/superclaude)
        """
        self.install_dir = install_dir
        # CLAUDE.md is always in parent directory (~/.claude/)
        self.claude_md_path = install_dir.parent / "CLAUDE.md"
        self.logger = get_logger()

    def read_existing_imports(self) -> Set[str]:
        """
        Parse CLAUDE.md for existing @import statements

        Returns:
            Set of already imported filenames (without @)
        """
        existing_imports = set()

        if not self.claude_md_path.exists():
            return existing_imports

        try:
            with open(self.claude_md_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find all @import statements using regex
            # Supports both @superclaude/file.md and @file.md (legacy)
            import_pattern = r"^@(?:superclaude/)?([^\s\n]+\.md)\s*$"
            matches = re.findall(import_pattern, content, re.MULTILINE)
            existing_imports.update(matches)

            self.logger.debug(f"Found existing imports: {existing_imports}")

        except Exception as e:
            self.logger.warning(f"Could not read existing CLAUDE.md imports: {e}")

        return existing_imports

    def read_existing_content(self) -> str:
        """
        Read existing CLAUDE.md content

        Returns:
            Existing content or empty string if file doesn't exist
        """
        if not self.claude_md_path.exists():
            return ""

        try:
            with open(self.claude_md_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.warning(f"Could not read existing CLAUDE.md: {e}")
            return ""

    def extract_user_content(self, content: str) -> str:
        """
        Extract user content (everything before framework imports section)

        Args:
            content: Full CLAUDE.md content

        Returns:
            User content without framework imports
        """
        # Look for framework imports section marker
        framework_marker = "# ===================================================\n# SuperClaude Framework Components"

        if framework_marker in content:
            user_content = content.split(framework_marker)[0].rstrip()
        else:
            # If no framework section exists, preserve all content
            user_content = content.rstrip()

        return user_content

    def organize_imports_by_category(
        self, files_by_category: Dict[str, List[str]]
    ) -> str:
        """
        Organize imports into categorized sections

        Args:
            files_by_category: Dict mapping category names to lists of files

        Returns:
            Formatted import sections
        """
        if not files_by_category:
            return ""

        sections = []

        # Framework imports section header
        sections.append("# ===================================================")
        sections.append("# SuperClaude Framework Components")
        sections.append("# ===================================================")
        sections.append("")

        # Add each category
        for category, files in files_by_category.items():
            if files:
                sections.append(f"# {category}")
                for file in sorted(files):
                    # Add superclaude/ prefix for all imports
                    sections.append(f"@superclaude/{file}")
                sections.append("")

        return "\n".join(sections)

    def add_imports(self, files: List[str], category: str = "Framework") -> bool:
        """
        Add new imports with duplicate checking and user content preservation

        Args:
            files: List of filenames to import
            category: Category name for organizing imports

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if CLAUDE.md exists (DO NOT create it)
            if not self.ensure_claude_md_exists():
                self.logger.info("Skipping CLAUDE.md update (file does not exist)")
                return False

            # Read existing content and imports
            existing_content = self.read_existing_content()
            existing_imports = self.read_existing_imports()

            # Filter out files already imported
            new_files = [f for f in files if f not in existing_imports]

            if not new_files:
                self.logger.info("All files already imported, no changes needed")
                return True

            self.logger.info(
                f"Adding {len(new_files)} new imports to category '{category}': {new_files}"
            )

            # Extract user content (preserve everything before framework section)
            user_content = self.extract_user_content(existing_content)

            # Parse existing framework imports by category
            existing_framework_imports = self._parse_existing_framework_imports(
                existing_content
            )

            # Add new files to the specified category
            if category not in existing_framework_imports:
                existing_framework_imports[category] = []
            existing_framework_imports[category].extend(new_files)

            # Build new content
            new_content_parts = []

            # Add user content
            if user_content.strip():
                new_content_parts.append(user_content)
                new_content_parts.append("")  # Add blank line before framework section

            # Add organized framework imports
            framework_section = self.organize_imports_by_category(
                existing_framework_imports
            )
            if framework_section:
                new_content_parts.append(framework_section)

            # Write updated content
            new_content = "\n".join(new_content_parts)

            with open(self.claude_md_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            self.logger.success(f"Updated CLAUDE.md with {len(new_files)} new imports")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update CLAUDE.md: {e}")
            return False

    def _parse_existing_framework_imports(self, content: str) -> Dict[str, List[str]]:
        """
        Parse existing framework imports organized by category

        Args:
            content: Full CLAUDE.md content

        Returns:
            Dict mapping category names to lists of imported files
        """
        imports_by_category = {}

        # Look for framework imports section
        framework_marker = "# ===================================================\n# SuperClaude Framework Components"

        if framework_marker not in content:
            return imports_by_category

        # Extract framework section
        framework_section = (
            content.split(framework_marker)[1] if framework_marker in content else ""
        )

        # Parse categories and imports
        lines = framework_section.split("\n")
        current_category = None

        for line in lines:
            line = line.strip()

            # Skip section header lines and empty lines
            if line.startswith("# ===") or not line:
                continue

            # Category header (starts with # but not the section divider)
            if line.startswith("# ") and not line.startswith("# ==="):
                current_category = line[2:].strip()  # Remove "# "
                if current_category not in imports_by_category:
                    imports_by_category[current_category] = []

            # Import line (starts with @)
            elif line.startswith("@") and current_category:
                import_file = line[1:].strip()  # Remove "@"
                # Remove superclaude/ prefix if present (normalize to filename only)
                if import_file.startswith("superclaude/"):
                    import_file = import_file[len("superclaude/"):]
                if import_file not in imports_by_category[current_category]:
                    imports_by_category[current_category].append(import_file)

        return imports_by_category

    def ensure_claude_md_exists(self) -> bool:
        """
        Check if CLAUDE.md exists (DO NOT create it - Claude Code pure file)

        Returns:
            True if CLAUDE.md exists, False otherwise
        """
        if self.claude_md_path.exists():
            return True

        # CLAUDE.md is a Claude Code pure file - NEVER create or modify it
        self.logger.warning(
            f"⚠️  CLAUDE.md not found at {self.claude_md_path}\n"
            f"   SuperClaude will NOT create this file automatically.\n"
            f"   Please manually add the following to your CLAUDE.md:\n\n"
            f"   # SuperClaude Framework Components\n"
            f"   @superclaude/FLAGS.md\n"
            f"   @superclaude/PRINCIPLES.md\n"
            f"   @superclaude/RULES.md\n"
            f"   (and other SuperClaude components)\n"
        )
        return False

    def remove_imports(self, files: List[str]) -> bool:
        """
        Remove specific imports from CLAUDE.md

        Args:
            files: List of filenames to remove from imports

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.claude_md_path.exists():
                return True  # Nothing to remove

            existing_content = self.read_existing_content()
            user_content = self.extract_user_content(existing_content)
            existing_framework_imports = self._parse_existing_framework_imports(
                existing_content
            )

            # Remove files from all categories
            removed_any = False
            for category, category_files in existing_framework_imports.items():
                for file in files:
                    if file in category_files:
                        category_files.remove(file)
                        removed_any = True

            # Remove empty categories
            existing_framework_imports = {
                k: v for k, v in existing_framework_imports.items() if v
            }

            if not removed_any:
                return True  # Nothing was removed

            # Rebuild content
            new_content_parts = []

            if user_content.strip():
                new_content_parts.append(user_content)
                new_content_parts.append("")

            framework_section = self.organize_imports_by_category(
                existing_framework_imports
            )
            if framework_section:
                new_content_parts.append(framework_section)

            # Write updated content
            new_content = "\n".join(new_content_parts)

            with open(self.claude_md_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            self.logger.info(f"Removed {len(files)} imports from CLAUDE.md")
            return True

        except Exception as e:
            self.logger.error(f"Failed to remove imports from CLAUDE.md: {e}")
            return False
