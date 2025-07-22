"""
System validation for SuperClaude installation requirements
"""

import subprocess
import sys
import shutil
from typing import Tuple, List, Dict, Any, Optional
from pathlib import Path
import re

# Handle packaging import - if not available, use a simple version comparison
try:
    from packaging import version
    PACKAGING_AVAILABLE = True
except ImportError:
    PACKAGING_AVAILABLE = False
    
    class SimpleVersion:
        def __init__(self, version_str: str):
            self.version_str = version_str
            # Simple version parsing: split by dots and convert to integers
            try:
                self.parts = [int(x) for x in version_str.split('.')]
            except ValueError:
                self.parts = [0, 0, 0]
        
        def __lt__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            # Pad with zeros to same length
            max_len = max(len(self.parts), len(other.parts))
            self_parts = self.parts + [0] * (max_len - len(self.parts))
            other_parts = other.parts + [0] * (max_len - len(other.parts))
            return self_parts < other_parts
        
        def __gt__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            return not (self < other) and not (self == other)
        
        def __eq__(self, other):
            if isinstance(other, str):
                other = SimpleVersion(other)
            return self.parts == other.parts
    
    class version:
        @staticmethod
        def parse(version_str: str):
            return SimpleVersion(version_str)


class Validator:
    """System requirements validator"""
    
    def __init__(self):
        """Initialize validator"""
        self.validation_cache: Dict[str, Any] = {}
    
    def check_python(self, min_version: str = "3.8", max_version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check Python version requirements
        
        Args:
            min_version: Minimum required Python version
            max_version: Maximum supported Python version (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        cache_key = f"python_{min_version}_{max_version}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            # Get current Python version
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            # Check minimum version
            if version.parse(current_version) < version.parse(min_version):
                help_msg = self.get_installation_help("python")
                result = (False, f"Python {min_version}+ required, found {current_version}{help_msg}")
                self.validation_cache[cache_key] = result
                return result
            
            # Check maximum version if specified
            if max_version and version.parse(current_version) > version.parse(max_version):
                result = (False, f"Python version {current_version} exceeds maximum supported {max_version}")
                self.validation_cache[cache_key] = result
                return result
            
            result = (True, f"Python {current_version} meets requirements")
            self.validation_cache[cache_key] = result
            return result
            
        except Exception as e:
            result = (False, f"Could not check Python version: {e}")
            self.validation_cache[cache_key] = result
            return result
    
    def check_node(self, min_version: str = "16.0", max_version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check Node.js version requirements
        
        Args:
            min_version: Minimum required Node.js version
            max_version: Maximum supported Node.js version (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        cache_key = f"node_{min_version}_{max_version}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            # Check if node is installed - use shell=True on Windows for better PATH resolution
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=(sys.platform == "win32")
            )
            
            if result.returncode != 0:
                help_msg = self.get_installation_help("node")
                result_tuple = (False, f"Node.js not found in PATH{help_msg}")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
            
            # Parse version (format: v18.17.0)
            version_output = result.stdout.strip()
            if version_output.startswith('v'):
                current_version = version_output[1:]
            else:
                current_version = version_output
            
            # Check minimum version
            if version.parse(current_version) < version.parse(min_version):
                help_msg = self.get_installation_help("node")
                result_tuple = (False, f"Node.js {min_version}+ required, found {current_version}{help_msg}")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
            
            # Check maximum version if specified
            if max_version and version.parse(current_version) > version.parse(max_version):
                result_tuple = (False, f"Node.js version {current_version} exceeds maximum supported {max_version}")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
            
            result_tuple = (True, f"Node.js {current_version} meets requirements")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
            
        except subprocess.TimeoutExpired:
            result_tuple = (False, "Node.js version check timed out")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
        except FileNotFoundError:
            help_msg = self.get_installation_help("node")
            result_tuple = (False, f"Node.js not found in PATH{help_msg}")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
        except Exception as e:
            result_tuple = (False, f"Could not check Node.js version: {e}")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
    
    def check_claude_cli(self, min_version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check Claude CLI installation and version
        
        Args:
            min_version: Minimum required Claude CLI version (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        cache_key = f"claude_cli_{min_version}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            # Check if claude is installed - use shell=True on Windows for better PATH resolution
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=(sys.platform == "win32")
            )
            
            if result.returncode != 0:
                help_msg = self.get_installation_help("claude_cli")
                result_tuple = (False, f"Claude CLI not found in PATH{help_msg}")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
            
            # Parse version from output
            version_output = result.stdout.strip()
            version_match = re.search(r'(\d+\.\d+\.\d+)', version_output)
            
            if not version_match:
                result_tuple = (True, "Claude CLI found (version format unknown)")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
            
            current_version = version_match.group(1)
            
            # Check minimum version if specified
            if min_version and version.parse(current_version) < version.parse(min_version):
                result_tuple = (False, f"Claude CLI {min_version}+ required, found {current_version}")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
            
            result_tuple = (True, f"Claude CLI {current_version} found")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
            
        except subprocess.TimeoutExpired:
            result_tuple = (False, "Claude CLI version check timed out")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
        except FileNotFoundError:
            help_msg = self.get_installation_help("claude_cli")
            result_tuple = (False, f"Claude CLI not found in PATH{help_msg}")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
        except Exception as e:
            result_tuple = (False, f"Could not check Claude CLI: {e}")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
    
    def check_external_tool(self, tool_name: str, command: str, min_version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check external tool availability and version
        
        Args:
            tool_name: Display name of tool
            command: Command to check version
            min_version: Minimum required version (optional)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        cache_key = f"tool_{tool_name}_{command}_{min_version}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            # Split command into parts
            cmd_parts = command.split()
            
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=10,
                shell=(sys.platform == "win32")
            )
            
            if result.returncode != 0:
                result_tuple = (False, f"{tool_name} not found or command failed")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
            
            # Extract version if min_version specified
            if min_version:
                version_output = result.stdout + result.stderr
                version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', version_output)
                
                if version_match:
                    current_version = version_match.group(1)
                    
                    if version.parse(current_version) < version.parse(min_version):
                        result_tuple = (False, f"{tool_name} {min_version}+ required, found {current_version}")
                        self.validation_cache[cache_key] = result_tuple
                        return result_tuple
                    
                    result_tuple = (True, f"{tool_name} {current_version} found")
                    self.validation_cache[cache_key] = result_tuple
                    return result_tuple
                else:
                    result_tuple = (True, f"{tool_name} found (version unknown)")
                    self.validation_cache[cache_key] = result_tuple
                    return result_tuple
            else:
                result_tuple = (True, f"{tool_name} found")
                self.validation_cache[cache_key] = result_tuple
                return result_tuple
                
        except subprocess.TimeoutExpired:
            result_tuple = (False, f"{tool_name} check timed out")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
        except FileNotFoundError:
            result_tuple = (False, f"{tool_name} not found in PATH")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
        except Exception as e:
            result_tuple = (False, f"Could not check {tool_name}: {e}")
            self.validation_cache[cache_key] = result_tuple
            return result_tuple
    
    def check_disk_space(self, path: Path, required_mb: int = 500) -> Tuple[bool, str]:
        """
        Check available disk space
        
        Args:
            path: Path to check (file or directory)
            required_mb: Required free space in MB
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        cache_key = f"disk_{path}_{required_mb}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            # Get parent directory if path is a file
            check_path = path.parent if path.is_file() else path
            
            # Get disk usage
            stat_result = shutil.disk_usage(check_path)
            free_mb = stat_result.free / (1024 * 1024)
            
            if free_mb < required_mb:
                result = (False, f"Insufficient disk space: {free_mb:.1f}MB free, {required_mb}MB required")
            else:
                result = (True, f"Sufficient disk space: {free_mb:.1f}MB free")
            
            self.validation_cache[cache_key] = result
            return result
            
        except Exception as e:
            result = (False, f"Could not check disk space: {e}")
            self.validation_cache[cache_key] = result
            return result
    
    def check_write_permissions(self, path: Path) -> Tuple[bool, str]:
        """
        Check write permissions for path
        
        Args:
            path: Path to check
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        cache_key = f"write_{path}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            # Create parent directories if needed
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
            
            result = (True, f"Write access confirmed for {path}")
            self.validation_cache[cache_key] = result
            return result
            
        except Exception as e:
            result = (False, f"No write access to {path}: {e}")
            self.validation_cache[cache_key] = result
            return result
    
    def validate_requirements(self, requirements: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate all system requirements
        
        Args:
            requirements: Requirements configuration dict
            
        Returns:
            Tuple of (all_passed: bool, error_messages: List[str])
        """
        errors = []
        
        # Check Python requirements
        if "python" in requirements:
            python_req = requirements["python"]
            success, message = self.check_python(
                python_req["min_version"],
                python_req.get("max_version")
            )
            if not success:
                errors.append(f"Python: {message}")
        
        # Check Node.js requirements
        if "node" in requirements:
            node_req = requirements["node"]
            success, message = self.check_node(
                node_req["min_version"],
                node_req.get("max_version")
            )
            if not success:
                errors.append(f"Node.js: {message}")
        
        # Check disk space
        if "disk_space_mb" in requirements:
            success, message = self.check_disk_space(
                Path.home(),
                requirements["disk_space_mb"]
            )
            if not success:
                errors.append(f"Disk space: {message}")
        
        # Check external tools
        if "external_tools" in requirements:
            for tool_name, tool_req in requirements["external_tools"].items():
                # Skip optional tools that fail
                is_optional = tool_req.get("optional", False)
                
                success, message = self.check_external_tool(
                    tool_name,
                    tool_req["command"],
                    tool_req.get("min_version")
                )
                
                if not success and not is_optional:
                    errors.append(f"{tool_name}: {message}")
        
        return len(errors) == 0, errors
    
    def validate_component_requirements(self, component_names: List[str], all_requirements: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate requirements for specific components
        
        Args:
            component_names: List of component names to validate
            all_requirements: Full requirements configuration
            
        Returns:
            Tuple of (all_passed: bool, error_messages: List[str])
        """
        errors = []
        
        # Start with base requirements
        base_requirements = {
            "python": all_requirements.get("python", {}),
            "disk_space_mb": all_requirements.get("disk_space_mb", 500)
        }
        
        # Add conditional requirements based on components
        external_tools = {}
        
        # Check if any component needs Node.js
        node_components = []
        for component in component_names:
            # This would be enhanced with actual component metadata
            if component in ["mcp"]:  # MCP component needs Node.js
                node_components.append(component)
        
        if node_components and "node" in all_requirements:
            base_requirements["node"] = all_requirements["node"]
        
        # Add external tools needed by components
        if "external_tools" in all_requirements:
            for tool_name, tool_req in all_requirements["external_tools"].items():
                required_for = tool_req.get("required_for", [])
                
                # Check if any of our components need this tool
                if any(comp in required_for for comp in component_names):
                    external_tools[tool_name] = tool_req
        
        if external_tools:
            base_requirements["external_tools"] = external_tools
        
        # Validate consolidated requirements
        return self.validate_requirements(base_requirements)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information
        
        Returns:
            Dict with system information
        """
        info = {
            "platform": sys.platform,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_executable": sys.executable
        }
        
        # Add Node.js info if available
        node_success, node_msg = self.check_node()
        info["node_available"] = node_success
        if node_success:
            info["node_message"] = node_msg
        
        # Add Claude CLI info if available
        claude_success, claude_msg = self.check_claude_cli()
        info["claude_cli_available"] = claude_success
        if claude_success:
            info["claude_cli_message"] = claude_msg
        
        # Add disk space info
        try:
            home_path = Path.home()
            stat_result = shutil.disk_usage(home_path)
            info["disk_space"] = {
                "total_gb": stat_result.total / (1024**3),
                "free_gb": stat_result.free / (1024**3),
                "used_gb": (stat_result.total - stat_result.free) / (1024**3)
            }
        except Exception:
            info["disk_space"] = {"error": "Could not determine disk space"}
        
        return info
    
    def get_platform(self) -> str:
        """
        Get current platform for installation commands
        
        Returns:
            Platform string (linux, darwin, win32)
        """
        return sys.platform
    
    def load_installation_commands(self) -> Dict[str, Any]:
        """
        Load installation commands from requirements configuration
        
        Returns:
            Installation commands dict
        """
        try:
            from ..managers.config_manager import ConfigManager
            from .. import PROJECT_ROOT
            
            config_manager = ConfigManager(PROJECT_ROOT / "config")
            requirements = config_manager.load_requirements()
            return requirements.get("installation_commands", {})
        except Exception:
            return {}
    
    def get_installation_help(self, tool_name: str, platform: Optional[str] = None) -> str:
        """
        Get installation help for a specific tool
        
        Args:
            tool_name: Name of tool to get help for
            platform: Target platform (auto-detected if None)
            
        Returns:
            Installation help string
        """
        if platform is None:
            platform = self.get_platform()
        
        commands = self.load_installation_commands()
        tool_commands = commands.get(tool_name, {})
        
        if not tool_commands:
            return f"No installation instructions available for {tool_name}"
        
        # Get platform-specific command or fallback to 'all'
        install_cmd = tool_commands.get(platform, tool_commands.get("all", ""))
        description = tool_commands.get("description", "")
        
        if install_cmd:
            help_text = f"\n💡 Installation Help for {tool_name}:\n"
            if description:
                help_text += f"   {description}\n"
            help_text += f"   Command: {install_cmd}\n"
            return help_text
        
        return f"No installation instructions available for {tool_name} on {platform}"
    
    def diagnose_system(self) -> Dict[str, Any]:
        """
        Perform comprehensive system diagnostics
        
        Returns:
            Diagnostic information dict
        """
        diagnostics = {
            "platform": self.get_platform(),
            "checks": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check Python
        python_success, python_msg = self.check_python()
        diagnostics["checks"]["python"] = {
            "status": "pass" if python_success else "fail",
            "message": python_msg
        }
        if not python_success:
            diagnostics["issues"].append("Python version issue")
            diagnostics["recommendations"].append(self.get_installation_help("python"))
        
        # Check Node.js
        node_success, node_msg = self.check_node()
        diagnostics["checks"]["node"] = {
            "status": "pass" if node_success else "fail", 
            "message": node_msg
        }
        if not node_success:
            diagnostics["issues"].append("Node.js not found or version issue")
            diagnostics["recommendations"].append(self.get_installation_help("node"))
        
        # Check Claude CLI
        claude_success, claude_msg = self.check_claude_cli()
        diagnostics["checks"]["claude_cli"] = {
            "status": "pass" if claude_success else "fail",
            "message": claude_msg
        }
        if not claude_success:
            diagnostics["issues"].append("Claude CLI not found")
            diagnostics["recommendations"].append(self.get_installation_help("claude_cli"))
        
        # Check disk space
        disk_success, disk_msg = self.check_disk_space(Path.home())
        diagnostics["checks"]["disk_space"] = {
            "status": "pass" if disk_success else "fail",
            "message": disk_msg
        }
        if not disk_success:
            diagnostics["issues"].append("Insufficient disk space")
        
        # Check common PATH issues
        self._diagnose_path_issues(diagnostics)
        
        return diagnostics
    
    def _diagnose_path_issues(self, diagnostics: Dict[str, Any]) -> None:
        """Add PATH-related diagnostics"""
        path_issues = []
        
        # Check if tools are in PATH, with alternatives for some tools
        tool_checks = [
            # For Python, check if either python3 OR python is available
            (["python3", "python"], "Python (python3 or python)"),
            (["node"], "Node.js"),
            (["npm"], "npm"),
            (["claude"], "Claude CLI")
        ]
        
        for tool_alternatives, display_name in tool_checks:
            tool_found = False
            for tool in tool_alternatives:
                try:
                    result = subprocess.run(
                        ["which" if sys.platform != "win32" else "where", tool],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=(sys.platform == "win32")
                    )
                    if result.returncode == 0:
                        tool_found = True
                        break
                except Exception:
                    continue
            
            if not tool_found:
                # Only report as missing if none of the alternatives were found
                if len(tool_alternatives) > 1:
                    path_issues.append(f"{display_name} not found in PATH")
                else:
                    path_issues.append(f"{tool_alternatives[0]} not found in PATH")
        
        if path_issues:
            diagnostics["issues"].extend(path_issues)
            diagnostics["recommendations"].append(
                "\n💡 PATH Issue Help:\n"
                "   Some tools may not be in your PATH. Try:\n"
                "   - Restart your terminal after installation\n"
                "   - Check your shell configuration (.bashrc, .zshrc)\n"
                "   - Use full paths to tools if needed\n"
            )
    
    def clear_cache(self) -> None:
        """Clear validation cache"""
        self.validation_cache.clear()
