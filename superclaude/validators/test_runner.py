"""Test Runner Validator

Validates that:
- Unit tests exist for changes
- Tests pass before implementation is approved
- Test coverage is maintained
"""

from typing import Dict, Any, List, Optional
import subprocess
from pathlib import Path

from .base import Validator, ValidationResult


class TestRunnerValidator(Validator):
    """Validates test execution"""

    def __init__(self):
        super().__init__("Test Runner")

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate tests.

        Context should contain:
        - changes: File changes
        - git_root: Repository root
        - contract: Context Contract
        - test_command: Optional custom test command
        """
        changes = context.get("changes", {})
        git_root = context.get("git_root")
        test_command = context.get("test_command")

        if not git_root:
            return self._skip("No git root provided")

        # Detect test files in changes
        test_files = [
            path for path in changes.keys()
            if self._is_test_file(path)
        ]

        # If no tests and no test files changed, skip
        if not test_files and not test_command:
            return self._warning("No tests detected for changes")

        # Run tests
        test_result = self._run_tests(git_root, test_command)

        if test_result["success"]:
            return self._pass(
                "Tests passed",
                details={
                    "test_files": test_files,
                    "output": test_result.get("output", "")[:500]  # First 500 chars
                }
            )
        else:
            return self._fail(
                "Tests failed",
                details={
                    "test_files": test_files,
                    "output": test_result.get("output", "")[:1000],  # First 1000 chars
                    "error": test_result.get("error", "")[:500]
                },
                suggestions=[
                    "Fix failing tests before proceeding",
                    "Review test output for specific failures"
                ]
            )

    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file"""
        path = Path(file_path)

        # Common test file patterns
        test_patterns = [
            "test_",  # Python: test_*.py
            "_test.",  # Go: *_test.go
            ".test.",  # JS/TS: *.test.js, *.test.ts
            ".spec.",  # JS/TS: *.spec.js, *.spec.ts
            "/tests/",  # In tests directory
            "/test/",  # In test directory
            "/__tests__/",  # React convention
        ]

        file_path_lower = file_path.lower()
        return any(pattern in file_path_lower for pattern in test_patterns)

    def _run_tests(self, git_root: Path, test_command: Optional[str] = None) -> Dict[str, Any]:
        """Run tests and return results"""
        if test_command:
            # Use custom test command
            return self._execute_test_command(git_root, test_command)

        # Auto-detect test framework
        if (git_root / "package.json").exists():
            return self._run_npm_tests(git_root)
        elif (git_root / "pyproject.toml").exists():
            return self._run_python_tests(git_root)
        else:
            return {
                "success": False,
                "output": "",
                "error": "Could not detect test framework"
            }

    def _execute_test_command(self, git_root: Path, command: str) -> Dict[str, Any]:
        """Execute custom test command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes max
                check=False
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Test execution timed out (5 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Test execution failed: {str(e)}"
            }

    def _run_npm_tests(self, git_root: Path) -> Dict[str, Any]:
        """Run npm/pnpm tests"""
        # Try pnpm first, fall back to npm
        if (git_root / "pnpm-lock.yaml").exists():
            return self._execute_test_command(git_root, "pnpm test")
        else:
            return self._execute_test_command(git_root, "npm test")

    def _run_python_tests(self, git_root: Path) -> Dict[str, Any]:
        """Run Python tests (pytest/unittest)"""
        # Try UV first, fall back to pytest
        if (git_root / "uv.lock").exists():
            return self._execute_test_command(git_root, "uv run pytest")
        else:
            return self._execute_test_command(git_root, "pytest")
