"""
Settings management for SuperClaude installation system
Handles settings.json migration to the new SuperClaude metadata json file
Allows for manipulation of these json files with deep merge and backup
"""

import json
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import copy


class SettingsManager:
    """Manages settings.json file operations"""
    
    def __init__(self, install_dir: Path):
        """
        Initialize settings manager
        
        Args:
            install_dir: Installation directory containing settings.json
        """
        self.install_dir = install_dir
        self.settings_file = install_dir / "settings.json"
        self.metadata_file = install_dir / ".superclaude-metadata.json"
        self.backup_dir = install_dir / "backups" / "settings"
        
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from settings.json
        
        Returns:
            Settings dict (empty if file doesn't exist)
        """
        if not self.settings_file.exists():
            return {}
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Could not load settings from {self.settings_file}: {e}")
    
    def save_settings(self, settings: Dict[str, Any], create_backup: bool = True) -> None:
        """
        Save settings to settings.json with optional backup
        
        Args:
            settings: Settings dict to save
            create_backup: Whether to create backup before saving
        """
        # Create backup if requested and file exists
        if create_backup and self.settings_file.exists():
            self._create_settings_backup()
        
        # Ensure directory exists
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with pretty formatting
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False, sort_keys=True)
        except IOError as e:
            raise ValueError(f"Could not save settings to {self.settings_file}: {e}")
    
    def load_metadata(self) -> Dict[str, Any]:
        """
        Load SuperClaude metadata from .superclaude-metadata.json
        
        Returns:
            Metadata dict (empty if file doesn't exist)
        """
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Could not load metadata from {self.metadata_file}: {e}")
    
    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Save SuperClaude metadata to .superclaude-metadata.json
        
        Args:
            metadata: Metadata dict to save
        """
        # Ensure directory exists
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with pretty formatting
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, sort_keys=True)
        except IOError as e:
            raise ValueError(f"Could not save metadata to {self.metadata_file}: {e}")

    def merge_metadata(self, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge modifications into existing settings

        Args:
            modifications: Settings modifications to merge

        Returns:
            Merged settings dict
        """
        existing = self.load_metadata()
        return self._deep_merge(existing, modifications)

    def update_metadata(self, modifications: Dict[str, Any]) -> None:
        """
        Update settings with modifications

        Args:
            modifications: Settings modifications to apply
            create_backup: Whether to create backup before updating
        """
        merged = self.merge_metadata(modifications)
        self.save_metadata(merged)

    def migrate_superclaude_data(self) -> bool:
        """
        Migrate SuperClaude-specific data from settings.json to metadata file
        
        Returns:
            True if migration occurred, False if no data to migrate
        """
        settings = self.load_settings()
        
        # SuperClaude-specific fields to migrate
        superclaude_fields = ["components", "framework", "superclaude", "mcp"]
        data_to_migrate = {}
        fields_found = False
        
        # Extract SuperClaude data
        for field in superclaude_fields:
            if field in settings:
                data_to_migrate[field] = settings[field]
                fields_found = True
        
        if not fields_found:
            return False
        
        # Load existing metadata (if any) and merge
        existing_metadata = self.load_metadata()
        merged_metadata = self._deep_merge(existing_metadata, data_to_migrate)
        
        # Save to metadata file
        self.save_metadata(merged_metadata)
        
        # Remove SuperClaude fields from settings
        clean_settings = {k: v for k, v in settings.items() if k not in superclaude_fields}
        
        # Save cleaned settings
        self.save_settings(clean_settings, create_backup=True)
        
        return True
    
    def merge_settings(self, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge modifications into existing settings
        
        Args:
            modifications: Settings modifications to merge
            
        Returns:
            Merged settings dict
        """
        existing = self.load_settings()
        return self._deep_merge(existing, modifications)
    
    def update_settings(self, modifications: Dict[str, Any], create_backup: bool = True) -> None:
        """
        Update settings with modifications
        
        Args:
            modifications: Settings modifications to apply
            create_backup: Whether to create backup before updating
        """
        merged = self.merge_settings(modifications)
        self.save_settings(merged, create_backup)
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """
        Get setting value using dot-notation path
        
        Args:
            key_path: Dot-separated path (e.g., "hooks.enabled")
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        settings = self.load_settings()
        
        try:
            value = settings
            for key in key_path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key_path: str, value: Any, create_backup: bool = True) -> None:
        """
        Set setting value using dot-notation path
        
        Args:
            key_path: Dot-separated path (e.g., "hooks.enabled")
            value: Value to set
            create_backup: Whether to create backup before updating
        """
        # Build nested dict structure
        keys = key_path.split('.')
        modification = {}
        current = modification
        
        for key in keys[:-1]:
            current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        
        self.update_settings(modification, create_backup)
    
    def remove_setting(self, key_path: str, create_backup: bool = True) -> bool:
        """
        Remove setting using dot-notation path
        
        Args:
            key_path: Dot-separated path to remove
            create_backup: Whether to create backup before updating
            
        Returns:
            True if setting was removed, False if not found
        """
        settings = self.load_settings()
        keys = key_path.split('.')
        
        # Navigate to parent of target key
        current = settings
        try:
            for key in keys[:-1]:
                current = current[key]
            
            # Remove the target key
            if keys[-1] in current:
                del current[keys[-1]]
                self.save_settings(settings, create_backup)
                return True
            else:
                return False
                
        except (KeyError, TypeError):
            return False
    
    def add_component_registration(self, component_name: str, component_info: Dict[str, Any]) -> None:
        """
        Add component to registry in metadata
        
        Args:
            component_name: Name of component
            component_info: Component metadata dict
        """
        metadata = self.load_metadata()
        if "components" not in metadata:
            metadata["components"] = {}
        
        metadata["components"][component_name] = {
            **component_info,
            "installed_at": datetime.now().isoformat()
        }
        
        self.save_metadata(metadata)
    
    def remove_component_registration(self, component_name: str) -> bool:
        """
        Remove component from registry in metadata
        
        Args:
            component_name: Name of component to remove
            
        Returns:
            True if component was removed, False if not found
        """
        metadata = self.load_metadata()
        if "components" in metadata and component_name in metadata["components"]:
            del metadata["components"][component_name]
            self.save_metadata(metadata)
            return True
        return False
    
    def get_installed_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all installed components from registry
        
        Returns:
            Dict of component_name -> component_info
        """
        metadata = self.load_metadata()
        return metadata.get("components", {})
    
    def is_component_installed(self, component_name: str) -> bool:
        """
        Check if component is registered as installed
        
        Args:
            component_name: Name of component to check
            
        Returns:
            True if component is installed, False otherwise
        """
        components = self.get_installed_components()
        return component_name in components
    
    def get_component_version(self, component_name: str) -> Optional[str]:
        """
        Get installed version of component
        
        Args:
            component_name: Name of component
            
        Returns:
            Version string or None if not installed
        """
        components = self.get_installed_components()
        component_info = components.get(component_name, {})
        return component_info.get("version")
    
    def update_framework_version(self, version: str) -> None:
        """
        Update SuperClaude framework version in metadata
        
        Args:
            version: Framework version string
        """
        metadata = self.load_metadata()
        if "framework" not in metadata:
            metadata["framework"] = {}
        
        metadata["framework"]["version"] = version
        metadata["framework"]["updated_at"] = datetime.now().isoformat()
        
        self.save_metadata(metadata)
    
    def check_installation_exists(self) -> bool:
        """
        Get SuperClaude framework version from metadata
        
        Returns:
            Version string or None if not set
        """
        return self.metadata_file.exists()

    def check_v2_installation_exists(self) -> bool:
        """
        Get SuperClaude framework version from metadata

        Returns:
            Version string or None if not set
        """
        return self.settings_file.exists()
    
    def get_metadata_setting(self, key_path: str, default: Any = None) -> Any:
        """
        Get metadata value using dot-notation path
        
        Args:
            key_path: Dot-separated path (e.g., "framework.version")
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        metadata = self.load_metadata()
        
        try:
            value = metadata
            for key in key_path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries
        
        Args:
            base: Base dictionary
            overlay: Dictionary to merge on top
            
        Returns:
            Merged dictionary
        """
        result = copy.deepcopy(base)
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        
        return result
    
    def _create_settings_backup(self) -> Path:
        """
        Create timestamped backup of settings.json
        
        Returns:
            Path to backup file
        """
        if not self.settings_file.exists():
            raise ValueError("Cannot backup non-existent settings file")
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"settings_{timestamp}.json"
        
        shutil.copy2(self.settings_file, backup_file)
        
        # Keep only last 10 backups
        self._cleanup_old_backups()
        
        return backup_file
    
    def _cleanup_old_backups(self, keep_count: int = 10) -> None:
        """
        Remove old backup files, keeping only the most recent
        
        Args:
            keep_count: Number of backups to keep
        """
        if not self.backup_dir.exists():
            return
        
        # Get all backup files sorted by modification time
        backup_files = []
        for file in self.backup_dir.glob("settings_*.json"):
            backup_files.append((file.stat().st_mtime, file))
        
        backup_files.sort(reverse=True)  # Most recent first
        
        # Remove old backups
        for _, file in backup_files[keep_count:]:
            try:
                file.unlink()
            except OSError:
                pass  # Ignore errors when cleaning up
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available settings backups
        
        Returns:
            List of backup info dicts with name, path, and timestamp
        """
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for file in self.backup_dir.glob("settings_*.json"):
            try:
                stat = file.stat()
                backups.append({
                    "name": file.name,
                    "path": str(file),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except OSError:
                continue
        
        # Sort by creation time, most recent first
        backups.sort(key=lambda x: x["created"], reverse=True)
        return backups
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore settings from backup
        
        Args:
            backup_name: Name of backup file to restore
            
        Returns:
            True if successful, False otherwise
        """
        backup_file = self.backup_dir / backup_name
        
        if not backup_file.exists():
            return False
        
        try:
            # Validate backup file first
            with open(backup_file, 'r', encoding='utf-8') as f:
                json.load(f)  # Will raise exception if invalid
            
            # Create backup of current settings
            if self.settings_file.exists():
                self._create_settings_backup()
            
            # Restore backup
            shutil.copy2(backup_file, self.settings_file)
            return True
            
        except (json.JSONDecodeError, IOError):
            return False
