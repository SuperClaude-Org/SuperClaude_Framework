"""
Cross-platform file management for SuperClaude installation system
"""

import shutil
import stat
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
import fnmatch
import hashlib


class FileManager:
    """Cross-platform file operations manager"""
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize file manager
        
        Args:
            dry_run: If True, only simulate file operations
        """
        self.dry_run = dry_run
        self.copied_files: List[Path] = []
        self.created_dirs: List[Path] = []
        
    def copy_file(self, source: Path, target: Path, preserve_permissions: bool = True) -> bool:
        """
        Copy single file with permission preservation
        
        Args:
            source: Source file path
            target: Target file path
            preserve_permissions: Whether to preserve file permissions
            
        Returns:
            True if successful, False otherwise
        """
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        if not source.is_file():
            raise ValueError(f"Source is not a file: {source}")
        
        if self.dry_run:
            print(f"[DRY RUN] Would copy {source} -> {target}")
            return True
        
        try:
            # Ensure target directory exists
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            if preserve_permissions:
                shutil.copy2(source, target)
            else:
                shutil.copy(source, target)
            
            self.copied_files.append(target)
            return True
            
        except Exception as e:
            print(f"Error copying {source} to {target}: {e}")
            return False
    
    def copy_directory(self, source: Path, target: Path, ignore_patterns: Optional[List[str]] = None) -> bool:
        """
        Recursively copy directory with gitignore-style patterns
        
        Args:
            source: Source directory path
            target: Target directory path
            ignore_patterns: List of patterns to ignore (gitignore style)
            
        Returns:
            True if successful, False otherwise
        """
        if not source.exists():
            raise FileNotFoundError(f"Source directory not found: {source}")
        
        if not source.is_dir():
            raise ValueError(f"Source is not a directory: {source}")
        
        ignore_patterns = ignore_patterns or []
        default_ignores = ['.git', '.gitignore', '__pycache__', '*.pyc', '.DS_Store']
        all_ignores = ignore_patterns + default_ignores
        
        if self.dry_run:
            print(f"[DRY RUN] Would copy directory {source} -> {target}")
            return True
        
        try:
            # Create ignore function
            def ignore_func(directory: str, contents: List[str]) -> List[str]:
                ignored = []
                for item in contents:
                    item_path = Path(directory) / item
                    rel_path = item_path.relative_to(source)
                    
                    # Check against ignore patterns
                    for pattern in all_ignores:
                        if fnmatch.fnmatch(item, pattern) or fnmatch.fnmatch(str(rel_path), pattern):
                            ignored.append(item)
                            break
                
                return ignored
            
            # Copy tree
            shutil.copytree(source, target, ignore=ignore_func, dirs_exist_ok=True)
            
            # Track created directories and files
            for item in target.rglob('*'):
                if item.is_dir():
                    self.created_dirs.append(item)
                else:
                    self.copied_files.append(item)
            
            return True
            
        except Exception as e:
            print(f"Error copying directory {source} to {target}: {e}")
            return False
    
    def ensure_directory(self, directory: Path, mode: int = 0o755) -> bool:
        """
        Create directory and parents if they don't exist
        
        Args:
            directory: Directory path to create
            mode: Directory permissions (Unix only)
            
        Returns:
            True if successful, False otherwise
        """
        if self.dry_run:
            print(f"[DRY RUN] Would create directory {directory}")
            return True
        
        try:
            directory.mkdir(parents=True, exist_ok=True, mode=mode)
            
            if directory not in self.created_dirs:
                self.created_dirs.append(directory)
            
            return True
            
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False
    
    def remove_file(self, file_path: Path) -> bool:
        """
        Remove single file
        
        Args:
            file_path: Path to file to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path.exists():
            return True  # Already gone
        
        if self.dry_run:
            print(f"[DRY RUN] Would remove file {file_path}")
            return True
        
        try:
            if file_path.is_file():
                file_path.unlink()
            else:
                print(f"Warning: {file_path} is not a file, skipping")
                return False
            
            # Remove from tracking
            if file_path in self.copied_files:
                self.copied_files.remove(file_path)
            
            return True
            
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
            return False
    
    def remove_directory(self, directory: Path, recursive: bool = False) -> bool:
        """
        Remove directory
        
        Args:
            directory: Directory path to remove
            recursive: Whether to remove recursively
            
        Returns:
            True if successful, False otherwise
        """
        if not directory.exists():
            return True  # Already gone
        
        if self.dry_run:
            action = "recursively remove" if recursive else "remove"
            print(f"[DRY RUN] Would {action} directory {directory}")
            return True
        
        try:
            if recursive:
                shutil.rmtree(directory)
            else:
                directory.rmdir()  # Only works if empty
            
            # Remove from tracking
            if directory in self.created_dirs:
                self.created_dirs.remove(directory)
            
            return True
            
        except Exception as e:
            print(f"Error removing directory {directory}: {e}")
            return False
    
    def resolve_home_path(self, path: str) -> Path:
        """
        Convert path with ~ to actual home path on any OS
        
        Args:
            path: Path string potentially containing ~
            
        Returns:
            Resolved Path object
        """
        return Path(path).expanduser().resolve()
    
    def make_executable(self, file_path: Path) -> bool:
        """
        Make file executable (Unix/Linux/macOS)
        
        Args:
            file_path: Path to file to make executable
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path.exists():
            return False
        
        if self.dry_run:
            print(f"[DRY RUN] Would make {file_path} executable")
            return True
        
        try:
            # Get current permissions
            current_mode = file_path.stat().st_mode
            
            # Add execute permissions for owner, group, and others
            new_mode = current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            
            file_path.chmod(new_mode)
            return True
            
        except Exception as e:
            print(f"Error making {file_path} executable: {e}")
            return False
    
    def get_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> Optional[str]:
        """
        Calculate file hash
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256, etc.)
            
        Returns:
            Hex hash string or None if error
        """
        if not file_path.exists() or not file_path.is_file():
            return None
        
        try:
            hasher = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception:
            return None
    
    def verify_file_integrity(self, file_path: Path, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """
        Verify file integrity using hash
        
        Args:
            file_path: Path to file to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            True if file matches expected hash, False otherwise
        """
        actual_hash = self.get_file_hash(file_path, algorithm)
        return actual_hash is not None and actual_hash.lower() == expected_hash.lower()
    
    def get_directory_size(self, directory: Path) -> int:
        """
        Calculate total size of directory in bytes
        
        Args:
            directory: Directory path
            
        Returns:
            Total size in bytes
        """
        if not directory.exists() or not directory.is_dir():
            return 0
        
        total_size = 0
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass  # Skip files we can't access
        
        return total_size
    
    def find_files(self, directory: Path, pattern: str = '*', recursive: bool = True) -> List[Path]:
        """
        Find files matching pattern
        
        Args:
            directory: Directory to search
            pattern: Glob pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        if not directory.exists() or not directory.is_dir():
            return []
        
        try:
            if recursive:
                return list(directory.rglob(pattern))
            else:
                return list(directory.glob(pattern))
        except Exception:
            return []
    
    def backup_file(self, file_path: Path, backup_suffix: str = '.backup') -> Optional[Path]:
        """
        Create backup copy of file
        
        Args:
            file_path: Path to file to backup
            backup_suffix: Suffix to add to backup file
            
        Returns:
            Path to backup file or None if failed
        """
        if not file_path.exists() or not file_path.is_file():
            return None
        
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
        
        if self.copy_file(file_path, backup_path):
            return backup_path
        return None
    
    def get_free_space(self, path: Path) -> int:
        """
        Get free disk space at path in bytes
        
        Args:
            path: Path to check (can be file or directory)
            
        Returns:
            Free space in bytes
        """
        try:
            if path.is_file():
                path = path.parent
            
            stat_result = shutil.disk_usage(path)
            return stat_result.free
        except Exception:
            return 0
    
    def cleanup_tracked_files(self) -> None:
        """Remove all files and directories created during this session"""
        if self.dry_run:
            print("[DRY RUN] Would cleanup tracked files")
            return
        
        # Remove files first
        for file_path in reversed(self.copied_files):
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
        
        # Remove directories (in reverse order of creation)
        for directory in reversed(self.created_dirs):
            try:
                if directory.exists() and not any(directory.iterdir()):
                    directory.rmdir()
            except Exception:
                pass
        
        self.copied_files.clear()
        self.created_dirs.clear()
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """
        Get summary of file operations performed
        
        Returns:
            Dict with operation statistics
        """
        return {
            'files_copied': len(self.copied_files),
            'directories_created': len(self.created_dirs),
            'dry_run': self.dry_run,
            'copied_files': [str(f) for f in self.copied_files],
            'created_directories': [str(d) for d in self.created_dirs]
        }