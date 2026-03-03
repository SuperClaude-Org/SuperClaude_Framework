#!/usr/bin/env python3
"""
SuperClaude Framework Sync Script
Automated pull-sync with namespace isolation for Plugin distribution

This script synchronizes content from SuperClaude_Framework repository and
transforms it for distribution as a Claude Code plugin with proper namespace
isolation (sc: prefix for commands, sc- prefix for filenames).

Usage:
    python scripts/sync_from_framework.py [OPTIONS]

Options:
    --framework-repo URL    Framework repository URL
    --plugin-root PATH      Plugin repository root path
    --dry-run               Preview changes without applying
    --output-report PATH    Save sync report to file
"""

import sys
import argparse
import tempfile
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import re
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProtectionViolationError(RuntimeError):
    """Raised when sync would overwrite a Plugin-owned file listed in PROTECTED_PATHS."""
    pass


@dataclass
class SyncResult:
    """Results from sync operation."""
    success: bool
    timestamp: str
    framework_commit: str
    framework_version: str
    files_synced: int
    files_modified: int
    commands_transformed: int
    agents_transformed: int
    mcp_servers_merged: int
    warnings: List[str]
    errors: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


class ContentTransformer:
    """Transforms Framework content for Plugin namespace."""

    # Regex patterns for transformation
    COMMAND_HEADER_PATTERN = re.compile(r'^(#+\s+)/(\w+)', re.MULTILINE)
    COMMAND_REF_PATTERN = re.compile(r'(?<![/\w])/(\w+)(?=\s|$|:|`|\)|\])')
    LINK_REF_PATTERN = re.compile(r'\[/(\w+)\]')
    FRONTMATTER_NAME_PATTERN = re.compile(r'^name:\s*(.+)$', re.MULTILINE)

    @staticmethod
    def transform_command(content: str, filename: str) -> str:
        """
        Transform command content for sc: namespace.

        Transformations:
        - Header: # /brainstorm → # /sc:brainstorm
        - References: /analyze → /sc:analyze
        - Links: [/task] → [/sc:task]

        Args:
            content: Original command file content
            filename: Command filename (for logging)

        Returns:
            Transformed content with sc: namespace
        """
        logger.debug(f"Transforming command: {filename}")

        # Transform main header
        content = ContentTransformer.COMMAND_HEADER_PATTERN.sub(
            r'\1/sc:\2',
            content
        )

        # Transform command references in text
        content = ContentTransformer.COMMAND_REF_PATTERN.sub(
            r'/sc:\1',
            content
        )

        # Transform command references in links
        content = ContentTransformer.LINK_REF_PATTERN.sub(
            r'[/sc:\1]',
            content
        )

        return content

    @staticmethod
    def transform_agent(content: str, filename: str) -> str:
        """
        Transform agent frontmatter name.

        Transformations:
        - name: backend-architect → name: sc-backend-architect

        Args:
            content: Original agent file content
            filename: Agent filename (for logging)

        Returns:
            Transformed content with sc- prefix in name field
        """
        logger.debug(f"Transforming agent: {filename}")

        # Parse frontmatter
        frontmatter_pattern = re.compile(
            r'^---\n(.*?)\n---',
            re.DOTALL | re.MULTILINE
        )

        match = frontmatter_pattern.search(content)
        if not match:
            logger.warning(f"No frontmatter found in agent: {filename}")
            return content

        frontmatter = match.group(1)

        # Transform name field (add sc- prefix if not already present)
        def add_prefix(match):
            name = match.group(1).strip()
            if not name.startswith('sc-'):
                return f'name: sc-{name}'
            return match.group(0)

        frontmatter = ContentTransformer.FRONTMATTER_NAME_PATTERN.sub(
            add_prefix,
            frontmatter
        )

        # Replace frontmatter
        content = frontmatter_pattern.sub(
            f'---\n{frontmatter}\n---',
            content,
            count=1
        )

        return content


class FileSyncer:
    """Handles file synchronization with git integration."""

    def __init__(self, plugin_root: Path, dry_run: bool = False):
        self.plugin_root = plugin_root
        self.dry_run = dry_run
        self.git_available = self._check_git()

    def _check_git(self) -> bool:
        """Check if git is available and repo is initialized."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.plugin_root,
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Git not available - file operations will not preserve history")
            return False

    def sync_directory(
        self,
        source_dir: Path,
        dest_dir: Path,
        filename_prefix: str = "",
        transform_fn=None
    ) -> Dict[str, int]:
        """
        Sync directory with namespace prefix and transformation.

        Args:
            source_dir: Source directory path
            dest_dir: Destination directory path
            filename_prefix: Prefix to add to filenames (e.g., 'sc-')
            transform_fn: Optional content transformation function

        Returns:
            Statistics dict with counts of synced/modified files
        """
        stats = {'synced': 0, 'modified': 0, 'renamed': 0}

        if not source_dir.exists():
            logger.warning(f"Source directory not found: {source_dir}")
            return stats

        dest_dir.mkdir(parents=True, exist_ok=True)

        # Get existing files in dest (with sc- prefix)
        existing_files = {f.name: f for f in dest_dir.glob('*.md')}
        synced_files = set()

        for source_file in source_dir.glob('*.md'):
            # Apply filename prefix
            new_name = f"{filename_prefix}{source_file.name}"
            synced_files.add(new_name)
            dest_file = dest_dir / new_name

            # Read and transform content
            content = source_file.read_text(encoding='utf-8')
            if transform_fn:
                content = transform_fn(content, source_file.name)

            # Check if file exists with different name (needs git mv)
            old_unprefixed = source_file.name
            old_file_path = dest_dir / old_unprefixed

            if old_file_path.exists() and new_name != old_unprefixed:
                # File needs renaming: use git mv to preserve history
                if self.git_available:
                    self._git_mv(old_file_path, dest_file)
                    stats['renamed'] += 1
                else:
                    # Fallback to regular rename
                    if not self.dry_run:
                        old_file_path.rename(dest_file)
                    stats['renamed'] += 1
                    logger.info(f"  📝 Renamed: {old_unprefixed} → {new_name}")

            # Write content
            if not self.dry_run:
                dest_file.write_text(content, encoding='utf-8')

            if dest_file.exists():
                stats['modified'] += 1
            else:
                stats['synced'] += 1

        # Remove files that no longer exist in source
        # (only remove files with prefix that aren't in synced set)
        for filename, filepath in existing_files.items():
            if filename.startswith(filename_prefix) and filename not in synced_files:
                if not self.dry_run:
                    filepath.unlink()
                logger.info(f"  🗑️  Removed: {filepath.relative_to(self.plugin_root)}")

        return stats

    def _git_mv(self, old_path: Path, new_path: Path):
        """Use git mv to preserve history."""
        if self.dry_run:
            logger.info(f"  [DRY RUN] git mv {old_path.name} {new_path.name}")
            return

        try:
            subprocess.run(
                ['git', 'mv', str(old_path), str(new_path)],
                cwd=self.plugin_root,
                check=True,
                capture_output=True
            )
            logger.info(f"  📝 Renamed (git mv): {old_path.name} → {new_path.name}")
        except subprocess.CalledProcessError as e:
            # Fallback to regular rename
            logger.warning(f"  ⚠️  Git mv failed, using regular rename: {e}")
            old_path.rename(new_path)

    def copy_directory(self, source_dir: Path, dest_dir: Path) -> int:
        """
        Copy directory contents as-is (no transformation).

        Args:
            source_dir: Source directory path
            dest_dir: Destination directory path

        Returns:
            Number of files copied
        """
        if not source_dir.exists():
            logger.warning(f"Source directory not found: {source_dir}")
            return 0

        dest_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for source_file in source_dir.glob('**/*'):
            if source_file.is_file():
                rel_path = source_file.relative_to(source_dir)
                dest_file = dest_dir / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                if not self.dry_run:
                    shutil.copy2(source_file, dest_file)

                count += 1
                logger.debug(f"  📄 Copied: {rel_path}")

        return count


class PluginJsonGenerator:
    """Generates .claude-plugin/plugin.json from synced commands."""

    def __init__(self, plugin_root: Path):
        self.plugin_root = plugin_root

    def generate(self, framework_version: str) -> dict:
        """
        Generate plugin.json with command mappings.

        Args:
            framework_version: Version from Framework repository

        Returns:
            Complete plugin.json dictionary
        """
        commands_dir = self.plugin_root / 'commands'

        # Base metadata from existing plugin.json
        root_plugin_json = self.plugin_root / 'plugin.json'
        if root_plugin_json.exists():
            base_metadata = json.loads(root_plugin_json.read_text())
        else:
            base_metadata = {
                "name": "sc",
                "description": "SuperClaude Plugin",
                "author": {"name": "SuperClaude Team"},
                "license": "MIT"
            }

        # Build command mappings
        commands = {}
        if commands_dir.exists():
            for cmd_file in sorted(commands_dir.glob('sc-*.md')):
                # Extract command name from filename
                # sc-brainstorm.md → brainstorm
                cmd_name = cmd_file.stem.replace('sc-', '')

                # Map sc:brainstorm to path
                commands[f"sc:{cmd_name}"] = f"commands/{cmd_file.name}"

        plugin_json = {
            "name": "sc",
            "version": framework_version,
            "description": base_metadata.get("description", ""),
            "author": base_metadata.get("author", {}),
            "homepage": base_metadata.get("homepage", ""),
            "repository": base_metadata.get("repository", ""),
            "license": base_metadata.get("license", "MIT"),
            "keywords": base_metadata.get("keywords", [])
        }

        logger.info(f"✅ Generated plugin.json with {len(commands)} commands")

        return plugin_json

    def write(self, plugin_json: dict, dry_run: bool = False):
        """Write plugin.json to .claude-plugin/ directory."""
        output_path = self.plugin_root / '.claude-plugin' / 'plugin.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if dry_run:
            logger.info(f"[DRY RUN] Would write plugin.json to: {output_path}")
            logger.info(json.dumps(plugin_json, indent=2))
            return

        output_path.write_text(
            json.dumps(plugin_json, indent=2) + '\n',
            encoding='utf-8'
        )
        logger.info(f"✅ Written: {output_path}")


class McpMerger:
    """Safely merges MCP server configurations."""

    def __init__(self, plugin_root: Path):
        self.plugin_root = plugin_root

    def merge(
        self,
        framework_mcp: dict,
        plugin_mcp: dict
    ) -> Tuple[dict, List[str]]:
        """
        Merge MCP configurations with conflict detection.

        Strategy:
        - Framework servers take precedence
        - Preserve Plugin-specific servers
        - Log warnings for conflicts

        Args:
            framework_mcp: MCP servers from Framework
            plugin_mcp: MCP servers from Plugin

        Returns:
            (merged_config, warnings)
        """
        merged = {}
        warnings = []

        # Add Framework servers (source of truth)
        for name, config in framework_mcp.items():
            merged[name] = config

        # Add Plugin-specific servers if not in Framework
        for name, config in plugin_mcp.items():
            if name not in merged:
                merged[name] = config
                warnings.append(
                    f"Preserved plugin-specific MCP server: {name}"
                )
            else:
                # Check if configurations differ
                if config != merged[name]:
                    warnings.append(
                        f"MCP server '{name}' conflict - using Framework version"
                    )

        return merged, warnings

    def backup_current(self) -> Optional[Path]:
        """Create backup of current plugin.json."""
        plugin_json = self.plugin_root / 'plugin.json'
        if not plugin_json.exists():
            return None

        backup_dir = self.plugin_root / 'backups'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'plugin.json.{timestamp}.backup'

        shutil.copy2(plugin_json, backup_path)
        logger.info(f"📦 Backup created: {backup_path}")

        return backup_path


class FrameworkSyncer:
    """Main orchestrator for Framework → Plugin sync."""

    # ── SYNC MAPPINGS ──────────────────────────────────────────────────────────
    # What to pull from Framework and transform for Plugin distribution.
    # Symmetric pair with PROTECTED_PATHS below: a path appears in one or the other,
    # never both.
    SYNC_MAPPINGS = {
        "src/superclaude/commands": "commands",   # /cmd → /sc:cmd, sc- prefix
        "src/superclaude/agents":   "agents",     # name → sc-name in frontmatter
        # core/ and modes/ are intentionally absent — they live in PROTECTED_PATHS
    }

    # ── PROTECTED PATHS ────────────────────────────────────────────────────────
    # Plugin-owned files and directories that must NEVER be overwritten by sync,
    # regardless of what the Framework contains.
    #
    # Algorithm: before sync → hash all protected paths → after sync → re-hash
    # and raise ProtectionViolationError if anything changed.
    #
    # To move a path from protected to synced: remove it here, add to SYNC_MAPPINGS.
    PROTECTED_PATHS: List[str] = [
        # Plugin-specific documentation (Plugin spec, not Framework spec)
        "README.md",
        "README-ja.md",
        "README-zh.md",
        "BACKUP_GUIDE.md",
        "MIGRATION_GUIDE.md",
        "SECURITY.md",
        "CLAUDE.md",
        "LICENSE",
        ".gitignore",
        # Plugin configuration & marketplace metadata
        ".claude-plugin/",
        # Plugin infrastructure (workflows, scripts, tests are Plugin-owned)
        ".github/",
        "docs/",
        "scripts/",
        "tests/",
        "backups/",
        # Plugin-customized behavioral content
        # Plugin maintains its own tuned versions; Framework versions are ignored.
        "core/",
        "modes/",
    ]

    def __init__(
        self,
        framework_repo: str,
        plugin_root: Path,
        dry_run: bool = False
    ):
        self.framework_repo = framework_repo
        self.plugin_root = plugin_root
        self.dry_run = dry_run
        self.temp_dir = None
        self.warnings = []
        self.errors = []

    def sync(self) -> SyncResult:
        """Execute full sync workflow."""
        try:
            logger.info("🔄 Starting Framework sync...")

            # Step 1: Clone Framework
            framework_path = self._clone_framework()
            framework_commit = self._get_commit_hash(framework_path)
            framework_version = self._get_version(framework_path)

            logger.info(f"📦 Framework version: {framework_version}")
            logger.info(f"📝 Framework commit: {framework_commit[:8]}")

            # Step 2: Snapshot protected files BEFORE any changes
            protection_snapshot = self._snapshot_protected_files()

            # Step 3: Create backup
            self._create_backup()

            # Step 4: Transform and sync content
            stats = self._sync_content(framework_path)

            # Step 5: Verify protected files were NOT touched
            self._validate_protected_files(protection_snapshot)

            # Step 6: Generate plugin.json
            self._generate_plugin_json(framework_version)

            # Step 7: Merge MCP configurations
            mcp_merged = self._merge_mcp_configs(framework_path)

            # Step 8: Validate sync results
            self._validate_sync()

            logger.info("✅ Sync completed successfully!")

            return SyncResult(
                success=True,
                timestamp=datetime.now().isoformat(),
                framework_commit=framework_commit,
                framework_version=framework_version,
                files_synced=stats['files_synced'],
                files_modified=stats['files_modified'],
                commands_transformed=stats['commands'],
                agents_transformed=stats['agents'],
                mcp_servers_merged=mcp_merged,
                warnings=self.warnings,
                errors=self.errors
            )

        except ProtectionViolationError as e:
            # Protection violations are logged already; surface them clearly in the report
            self.errors.append(str(e))
            return SyncResult(
                success=False,
                timestamp=datetime.now().isoformat(),
                framework_commit="",
                framework_version="",
                files_synced=0,
                files_modified=0,
                commands_transformed=0,
                agents_transformed=0,
                mcp_servers_merged=0,
                warnings=self.warnings,
                errors=self.errors
            )
        except Exception as e:
            logger.error(f"❌ Sync failed: {e}", exc_info=True)
            self.errors.append(str(e))
            return SyncResult(
                success=False,
                timestamp=datetime.now().isoformat(),
                framework_commit="",
                framework_version="",
                files_synced=0,
                files_modified=0,
                commands_transformed=0,
                agents_transformed=0,
                mcp_servers_merged=0,
                warnings=self.warnings,
                errors=self.errors
            )
        finally:
            self._cleanup()

    # ── Protection helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _hash_file(path: Path) -> str:
        """Return SHA-256 hex digest of a file's contents."""
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    def _snapshot_protected_files(self) -> Dict[str, str]:
        """
        Hash every file that lives under a PROTECTED_PATHS entry.

        Called BEFORE sync begins so we have a baseline to compare against.

        Returns:
            Mapping of relative-path-string → SHA-256 hex digest.
        """
        snapshot: Dict[str, str] = {}
        for protected in self.PROTECTED_PATHS:
            target = self.plugin_root / protected
            if target.is_file():
                rel = protected
                snapshot[rel] = self._hash_file(target)
            elif target.is_dir():
                for f in sorted(target.rglob('*')):
                    if f.is_file():
                        rel = str(f.relative_to(self.plugin_root))
                        snapshot[rel] = self._hash_file(f)
        logger.info(f"🔒 Protection snapshot: {len(snapshot)} Plugin-owned files hashed")
        return snapshot

    def _validate_protected_files(self, snapshot: Dict[str, str]) -> None:
        """
        Re-hash every file from the snapshot and compare.

        Called AFTER sync to verify no protected file was touched.

        Raises:
            ProtectionViolationError: if any protected file was modified or deleted.
        """
        violations: List[str] = []
        for rel_path, original_hash in snapshot.items():
            current = self.plugin_root / rel_path
            if not current.exists():
                violations.append(f"DELETED  : {rel_path}")
            else:
                current_hash = self._hash_file(current)
                if current_hash != original_hash:
                    violations.append(f"MODIFIED : {rel_path}")

        if violations:
            msg = (
                "🚨 PROTECTION VIOLATION — sync modified Plugin-owned files:\n"
                + "\n".join(f"  • {v}" for v in violations)
                + "\n\nFix: ensure SYNC_MAPPINGS does not target any path in PROTECTED_PATHS."
            )
            logger.error(msg)
            raise ProtectionViolationError(msg)

        logger.info(f"🔒 Protection check passed — {len(snapshot)} Plugin-owned files unchanged")

    # ── Core sync workflow ─────────────────────────────────────────────────────

    def _clone_framework(self) -> Path:
        """Clone Framework repository to temp directory."""
        logger.info(f"📥 Cloning Framework: {self.framework_repo}")

        self.temp_dir = tempfile.mkdtemp(prefix='superclaude_framework_')
        framework_path = Path(self.temp_dir) / 'framework'

        try:
            subprocess.run(
                ['git', 'clone', '--depth', '1', self.framework_repo, str(framework_path)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"✅ Cloned to: {framework_path}")
            return framework_path

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone Framework: {e.stderr}")
            raise

    def _get_commit_hash(self, repo_path: Path) -> str:
        """Get current commit hash from repository."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def _get_version(self, framework_path: Path) -> str:
        """Extract version from Framework."""
        # Try to read version from plugin.json or package.json
        for version_file in ['plugin.json', 'package.json']:
            version_path = framework_path / version_file
            if version_path.exists():
                try:
                    data = json.loads(version_path.read_text())
                    if 'version' in data:
                        return data['version']
                except (json.JSONDecodeError, KeyError):
                    continue

        # Fallback to current Plugin version
        plugin_json = self.plugin_root / 'plugin.json'
        if plugin_json.exists():
            try:
                data = json.loads(plugin_json.read_text())
                return data.get('version', '1.0.0')
            except json.JSONDecodeError:
                pass

        return '1.0.0'

    def _create_backup(self):
        """Create backup of current plugin state."""
        logger.info("📦 Creating backup...")

        mcp_merger = McpMerger(self.plugin_root)
        backup_path = mcp_merger.backup_current()

        if backup_path:
            logger.info(f"✅ Backup created: {backup_path}")

    def _sync_content(self, framework_path: Path) -> Dict[str, int]:
        """Sync and transform content from Framework."""
        logger.info("🔄 Syncing content...")

        file_syncer = FileSyncer(self.plugin_root, self.dry_run)
        stats = {
            'files_synced': 0,
            'files_modified': 0,
            'commands': 0,
            'agents': 0
        }

        # Sync commands with transformation
        logger.info("📝 Syncing commands...")
        source_commands = framework_path / 'src/superclaude/commands'
        dest_commands = self.plugin_root / 'commands'

        if source_commands.exists():
            cmd_stats = file_syncer.sync_directory(
                source_commands,
                dest_commands,
                filename_prefix='sc-',
                transform_fn=ContentTransformer.transform_command
            )
            stats['commands'] = cmd_stats['synced'] + cmd_stats['modified']
            stats['files_synced'] += cmd_stats['synced']
            stats['files_modified'] += cmd_stats['modified']
            logger.info(f"✅ Commands: {stats['commands']} transformed")

        # Sync agents with transformation
        logger.info("📝 Syncing agents...")
        source_agents = framework_path / 'src/superclaude/agents'
        dest_agents = self.plugin_root / 'agents'

        if source_agents.exists():
            agent_stats = file_syncer.sync_directory(
                source_agents,
                dest_agents,
                filename_prefix='sc-',
                transform_fn=ContentTransformer.transform_agent
            )
            stats['agents'] = agent_stats['synced'] + agent_stats['modified']
            stats['files_synced'] += agent_stats['synced']
            stats['files_modified'] += agent_stats['modified']
            logger.info(f"✅ Agents: {stats['agents']} transformed")

        # core/ and modes/ are in PROTECTED_PATHS — Plugin maintains its own versions.
        # They are intentionally excluded from SYNC_MAPPINGS and will never be
        # overwritten here.  To re-enable Framework sync for either directory,
        # remove it from PROTECTED_PATHS and add it back to SYNC_MAPPINGS.
        logger.info("🔒 core/ and modes/ are Plugin-owned (PROTECTED_PATHS) — skipping")

        return stats

    def _generate_plugin_json(self, framework_version: str):
        """Generate plugin.json from synced commands."""
        logger.info("📄 Generating plugin.json...")

        generator = PluginJsonGenerator(self.plugin_root)
        plugin_json = generator.generate(framework_version)
        generator.write(plugin_json, self.dry_run)

    def _merge_mcp_configs(self, framework_path: Path) -> int:
        """Merge MCP configurations from Framework."""
        logger.info("🔗 Merging MCP configurations...")

        # Read Framework MCP config
        framework_plugin_json = framework_path / 'plugin.json'
        framework_mcp = {}

        if framework_plugin_json.exists():
            try:
                data = json.loads(framework_plugin_json.read_text())
                framework_mcp = data.get('mcpServers', {})
            except json.JSONDecodeError:
                logger.warning("Failed to read Framework plugin.json")

        # Read Plugin MCP config
        plugin_json_path = self.plugin_root / 'plugin.json'
        plugin_mcp = {}

        if plugin_json_path.exists():
            try:
                data = json.loads(plugin_json_path.read_text())
                plugin_mcp = data.get('mcpServers', {})
            except json.JSONDecodeError:
                logger.warning("Failed to read Plugin plugin.json")

        # Merge configurations
        merger = McpMerger(self.plugin_root)
        merged_mcp, warnings = merger.merge(framework_mcp, plugin_mcp)

        # Log warnings
        for warning in warnings:
            logger.warning(f"⚠️  {warning}")
            self.warnings.append(warning)

        # Update plugin.json with merged MCP config
        if not self.dry_run and plugin_json_path.exists():
            data = json.loads(plugin_json_path.read_text())
            data['mcpServers'] = merged_mcp
            plugin_json_path.write_text(
                json.dumps(data, indent=2) + '\n',
                encoding='utf-8'
            )

        logger.info(f"✅ MCP servers merged: {len(merged_mcp)}")
        return len(merged_mcp)

    def _validate_sync(self):
        """Validate sync results."""
        logger.info("🔍 Validating sync...")

        # Check commands directory
        commands_dir = self.plugin_root / 'commands'
        if commands_dir.exists():
            sc_commands = list(commands_dir.glob('sc-*.md'))
            logger.info(f"✅ Found {len(sc_commands)} sc- prefixed commands")

        # Check agents directory
        agents_dir = self.plugin_root / 'agents'
        if agents_dir.exists():
            sc_agents = list(agents_dir.glob('sc-*.md'))
            logger.info(f"✅ Found {len(sc_agents)} sc- prefixed agents")

        # Check plugin.json
        plugin_json_path = self.plugin_root / '.claude-plugin' / 'plugin.json'
        if plugin_json_path.exists():
            logger.info(f"✅ plugin.json exists at {plugin_json_path}")
        else:
            logger.warning("⚠️  plugin.json not found")

    def _cleanup(self):
        """Clean up temporary directories."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            logger.debug(f"🧹 Cleaned up temp directory: {self.temp_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync SuperClaude Framework to Plugin with namespace isolation'
    )
    parser.add_argument(
        '--framework-repo',
        default='https://github.com/SuperClaude-Org/SuperClaude_Framework',
        help='Framework repository URL'
    )
    parser.add_argument(
        '--plugin-root',
        type=Path,
        default=Path.cwd(),
        help='Plugin repository root path'
    )
    parser.add_argument(
        '--dry-run',
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=False,
        help='Preview changes without applying'
    )
    parser.add_argument(
        '--output-report',
        type=Path,
        help='Save sync report to file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be applied")

    # Run sync
    syncer = FrameworkSyncer(
        framework_repo=args.framework_repo,
        plugin_root=args.plugin_root,
        dry_run=args.dry_run
    )

    result = syncer.sync()

    # Output report
    if args.output_report:
        args.output_report.write_text(
            json.dumps(result.to_dict(), indent=2) + '\n'
        )
        logger.info(f"📊 Report saved to: {args.output_report}")

    # Print summary
    print("\n" + "=" * 60)
    print("SYNC SUMMARY")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Framework Version: {result.framework_version}")
    print(f"Framework Commit: {result.framework_commit[:8]}")
    print(f"Files Synced: {result.files_synced}")
    print(f"Files Modified: {result.files_modified}")
    print(f"Commands Transformed: {result.commands_transformed}")
    print(f"Agents Transformed: {result.agents_transformed}")
    print(f"MCP Servers Merged: {result.mcp_servers_merged}")

    if result.warnings:
        print(f"\n⚠️  Warnings: {len(result.warnings)}")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.errors:
        print(f"\n❌ Errors: {len(result.errors)}")
        for error in result.errors:
            print(f"  - {error}")

    print("=" * 60)

    sys.exit(0 if result.success else 1)


if __name__ == '__main__':
    main()
