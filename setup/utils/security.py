"""
Security utilities for SuperClaude installation system
Path validation and input sanitization
"""

import re
import os
from pathlib import Path
from typing import List, Optional, Tuple, Set
import urllib.parse


class SecurityValidator:
    """Security validation utilities"""
    
    # Dangerous path patterns
    DANGEROUS_PATTERNS = [
        r'\.\./',           # Directory traversal
        r'\.\.\.',          # Directory traversal
        r'//+',             # Multiple slashes
        r'/etc/',           # System directories
        r'/bin/',
        r'/sbin/',
        r'/usr/bin/',
        r'/usr/sbin/',
        r'/var/',
        r'/tmp/',
        r'/dev/',
        r'/proc/',
        r'/sys/',
        r'c:\\windows\\',   # Windows system dirs
        r'c:\\program files\\',
        # Note: Removed c:\\users\\ to allow installation in user directories
        # Claude Code installs to user home directory by default
    ]
    
    # Dangerous filename patterns
    DANGEROUS_FILENAMES = [
        r'\.exe$',          # Executables
        r'\.bat$',
        r'\.cmd$',
        r'\.scr$',
        r'\.dll$',
        r'\.so$',
        r'\.dylib$',
        r'passwd',          # System files
        r'shadow',
        r'hosts',
        r'\.ssh/',
        r'\.aws/',
        r'\.env',           # Environment files
        r'\.secret',
    ]
    
    # Allowed file extensions for installation
    ALLOWED_EXTENSIONS = {
        '.md', '.json', '.py', '.js', '.ts', '.jsx', '.tsx',
        '.txt', '.yml', '.yaml', '.toml', '.cfg', '.conf',
        '.sh', '.ps1', '.html', '.css', '.svg', '.png', '.jpg', '.gif'
    }
    
    # Maximum path lengths
    MAX_PATH_LENGTH = 4096
    MAX_FILENAME_LENGTH = 255
    
    @classmethod
    def validate_path(cls, path: Path, base_dir: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Validate path for security issues
        
        Args:
            path: Path to validate
            base_dir: Base directory that path should be within
            
        Returns:
            Tuple of (is_safe: bool, error_message: str)
        """
        try:
            # Convert to absolute path
            abs_path = path.resolve()
            path_str = str(abs_path).lower()
            
            # Check path length
            if len(str(abs_path)) > cls.MAX_PATH_LENGTH:
                return False, f"Path too long: {len(str(abs_path))} > {cls.MAX_PATH_LENGTH}"
            
            # Check filename length
            if len(abs_path.name) > cls.MAX_FILENAME_LENGTH:
                return False, f"Filename too long: {len(abs_path.name)} > {cls.MAX_FILENAME_LENGTH}"
            
            # Check for dangerous patterns
            for pattern in cls.DANGEROUS_PATTERNS:
                if re.search(pattern, path_str, re.IGNORECASE):
                    return False, f"Dangerous path pattern detected: {pattern}"
            
            # Check for dangerous filenames
            for pattern in cls.DANGEROUS_FILENAMES:
                if re.search(pattern, abs_path.name, re.IGNORECASE):
                    return False, f"Dangerous filename pattern detected: {pattern}"
            
            # Check if path is within base directory
            if base_dir:
                base_abs = base_dir.resolve()
                try:
                    abs_path.relative_to(base_abs)
                except ValueError:
                    return False, f"Path outside allowed directory: {abs_path} not in {base_abs}"
            
            # Check for null bytes
            if '\x00' in str(path):
                return False, "Null byte detected in path"
            
            # Check for Windows reserved names
            if os.name == 'nt':
                reserved_names = [
                    'CON', 'PRN', 'AUX', 'NUL',
                    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
                ]
                
                name_without_ext = abs_path.stem.upper()
                if name_without_ext in reserved_names:
                    return False, f"Reserved Windows filename: {name_without_ext}"
            
            return True, "Path is safe"
            
        except Exception as e:
            return False, f"Path validation error: {e}"
    
    @classmethod
    def validate_file_extension(cls, path: Path) -> Tuple[bool, str]:
        """
        Validate file extension is allowed
        
        Args:
            path: Path to validate
            
        Returns:
            Tuple of (is_allowed: bool, message: str)
        """
        extension = path.suffix.lower()
        
        if not extension:
            return True, "No extension (allowed)"
        
        if extension in cls.ALLOWED_EXTENSIONS:
            return True, f"Extension {extension} is allowed"
        else:
            return False, f"Extension {extension} is not allowed"
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename by removing dangerous characters
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Remove or replace dangerous characters
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(dangerous_chars, '_', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure not empty
        if not filename:
            filename = 'unnamed'
        
        # Truncate if too long
        if len(filename) > cls.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(filename)
            max_name_len = cls.MAX_FILENAME_LENGTH - len(ext)
            filename = name[:max_name_len] + ext
        
        # Check for Windows reserved names
        if os.name == 'nt':
            name_without_ext = os.path.splitext(filename)[0].upper()
            reserved_names = [
                'CON', 'PRN', 'AUX', 'NUL',
                'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
            ]
            
            if name_without_ext in reserved_names:
                filename = f"safe_{filename}"
        
        return filename
    
    @classmethod
    def sanitize_input(cls, user_input: str, max_length: int = 1000) -> str:
        """
        Sanitize user input
        
        Args:
            user_input: Raw user input
            max_length: Maximum allowed length
            
        Returns:
            Sanitized input
        """
        if not user_input:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', user_input)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """
        Validate URL for security issues
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_safe: bool, message: str)
        """
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return False, f"Invalid scheme: {parsed.scheme}"
            
            # Check for localhost/private IPs (basic check)
            hostname = parsed.hostname
            if hostname:
                if hostname.lower() in ['localhost', '127.0.0.1', '::1']:
                    return False, "Localhost URLs not allowed"
                
                # Basic private IP check
                if hostname.startswith('192.168.') or hostname.startswith('10.') or hostname.startswith('172.'):
                    return False, "Private IP addresses not allowed"
            
            # Check URL length
            if len(url) > 2048:
                return False, "URL too long"
            
            return True, "URL is safe"
            
        except Exception as e:
            return False, f"URL validation error: {e}"
    
    @classmethod
    def check_permissions(cls, path: Path, required_permissions: Set[str]) -> Tuple[bool, List[str]]:
        """
        Check file/directory permissions
        
        Args:
            path: Path to check
            required_permissions: Set of required permissions ('read', 'write', 'execute')
            
        Returns:
            Tuple of (has_permissions: bool, missing_permissions: List[str])
        """
        missing = []
        
        try:
            if not path.exists():
                # For non-existent paths, check parent directory
                parent = path.parent
                if not parent.exists():
                    missing.append("path does not exist")
                    return False, missing
                path = parent
            
            if 'read' in required_permissions:
                if not os.access(path, os.R_OK):
                    missing.append('read')
            
            if 'write' in required_permissions:
                if not os.access(path, os.W_OK):
                    missing.append('write')
            
            if 'execute' in required_permissions:
                if not os.access(path, os.X_OK):
                    missing.append('execute')
            
            return len(missing) == 0, missing
            
        except Exception as e:
            missing.append(f"permission check error: {e}")
            return False, missing
    
    @classmethod
    def validate_installation_target(cls, target_dir: Path) -> Tuple[bool, List[str]]:
        """
        Validate installation target directory
        
        Args:
            target_dir: Target installation directory
            
        Returns:
            Tuple of (is_safe: bool, error_messages: List[str])
        """
        errors = []
        
        # Special handling for Claude installation directory
        abs_target = target_dir.resolve()
        abs_target_str = str(abs_target).lower()
        
        # Allow installation to .claude directory in user home
        if abs_target_str.endswith('.claude') or abs_target_str.endswith('.claude' + os.sep):
            home_path = Path.home()
            try:
                # Check if it's under user home directory
                abs_target.relative_to(home_path)
                # If we reach here, it's under home directory - allow it
                # Still check permissions
                has_perms, missing = cls.check_permissions(target_dir, {'read', 'write'})
                if not has_perms:
                    errors.append(f"Insufficient permissions: missing {missing}")
                return len(errors) == 0, errors
            except ValueError:
                # Not under home directory, continue with normal validation
                pass
        
        # Validate path for non-.claude directories
        is_safe, msg = cls.validate_path(target_dir)
        if not is_safe:
            errors.append(f"Invalid target path: {msg}")
        
        # Check permissions
        has_perms, missing = cls.check_permissions(target_dir, {'read', 'write'})
        if not has_perms:
            errors.append(f"Insufficient permissions: missing {missing}")
        
        # Check if it's a system directory
        system_dirs = [
            Path('/etc'), Path('/bin'), Path('/sbin'), Path('/usr/bin'), Path('/usr/sbin'),
            Path('/var'), Path('/tmp'), Path('/dev'), Path('/proc'), Path('/sys')
        ]
        
        if os.name == 'nt':
            system_dirs.extend([
                Path('C:\\Windows'), Path('C:\\Program Files'), Path('C:\\Program Files (x86)')
            ])
        
        for sys_dir in system_dirs:
            try:
                if abs_target.is_relative_to(sys_dir):
                    errors.append(f"Cannot install to system directory: {sys_dir}")
                    break
            except (ValueError, AttributeError):
                # is_relative_to not available in older Python versions
                try:
                    abs_target.relative_to(sys_dir)
                    errors.append(f"Cannot install to system directory: {sys_dir}")
                    break
                except ValueError:
                    continue
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_component_files(cls, file_list: List[Tuple[Path, Path]], base_source_dir: Path, base_target_dir: Path) -> Tuple[bool, List[str]]:
        """
        Validate list of files for component installation
        
        Args:
            file_list: List of (source, target) path tuples
            base_source_dir: Base source directory
            base_target_dir: Base target directory
            
        Returns:
            Tuple of (all_safe: bool, error_messages: List[str])
        """
        errors = []
        
        for source, target in file_list:
            # Validate source path
            is_safe, msg = cls.validate_path(source, base_source_dir)
            if not is_safe:
                errors.append(f"Invalid source path {source}: {msg}")
            
            # Validate target path
            is_safe, msg = cls.validate_path(target, base_target_dir)
            if not is_safe:
                errors.append(f"Invalid target path {target}: {msg}")
            
            # Validate file extension
            is_allowed, msg = cls.validate_file_extension(source)
            if not is_allowed:
                errors.append(f"File {source}: {msg}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def create_secure_temp_dir(cls, prefix: str = "superclaude_") -> Path:
        """
        Create secure temporary directory
        
        Args:
            prefix: Prefix for temp directory name
            
        Returns:
            Path to secure temporary directory
        """
        import tempfile
        
        # Create with secure permissions (0o700)
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        temp_dir.chmod(0o700)
        
        return temp_dir
    
    @classmethod
    def secure_delete(cls, path: Path) -> bool:
        """
        Securely delete file or directory
        
        Args:
            path: Path to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not path.exists():
                return True
            
            if path.is_file():
                # Overwrite file with random data before deletion
                try:
                    import secrets
                    file_size = path.stat().st_size
                    
                    with open(path, 'r+b') as f:
                        # Overwrite with random data
                        f.write(secrets.token_bytes(file_size))
                        f.flush()
                        os.fsync(f.fileno())
                except Exception:
                    pass  # If overwrite fails, still try to delete
                
                path.unlink()
            
            elif path.is_dir():
                # Recursively delete directory contents
                import shutil
                shutil.rmtree(path)
            
            return True
            
        except Exception:
            return False