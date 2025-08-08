#!/usr/bin/env python3
"""
SPARK Test Runner Hook (SubagentStop)
Automatically executes comprehensive test suite after implementation
"""

import json
import logging
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


class TestRunner:
    """SPARK intelligent test execution engine"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "coverage": 0.0,
            "execution_time": 0.0,
            "test_types": {
                "unit": {"passed": 0, "failed": 0},
                "integration": {"passed": 0, "failed": 0},
                "e2e": {"passed": 0, "failed": 0}
            }
        }
    
    def detect_test_framework(self) -> str:
        """Detect which test framework is being used"""
        # Check for pytest
        if Path(self.project_root, "pytest.ini").exists() or \
           Path(self.project_root, "pyproject.toml").exists():
            return "pytest"
        
        # Check for unittest
        if any(Path(self.project_root).rglob("test_*.py")):
            return "unittest"
        
        # Check for Jest (JavaScript)
        if Path(self.project_root, "package.json").exists():
            with open(Path(self.project_root, "package.json")) as f:
                if "jest" in f.read():
                    return "jest"
        
        return "pytest"  # Default to pytest
    
    def run_command(self, cmd: str, timeout: int = 300) -> Tuple[bool, str, str]:
        """Execute shell command with timeout"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "", f"Command timed out after {timeout}s")
        except Exception as e:
            return (False, "", str(e))
    
    def analyze_test_requirements(self, files: List[str]) -> Dict[str, bool]:
        """Analyze what types of tests are needed"""
        requirements = {
            "unit": False,
            "integration": False,
            "e2e": False,
            "security": False,
            "performance": False
        }
        
        for file_path in files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                with open(Path(self.project_root, file_path)) as f:
                    content = f.read().lower()
                    
                    # Detect test requirements based on code patterns
                    if "redis" in content or "database" in content:
                        requirements["integration"] = True
                    
                    if "@app.route" in content or "fastapi" in content:
                        requirements["e2e"] = True
                    
                    if "password" in content or "auth" in content or "token" in content:
                        requirements["security"] = True
                    
                    if "benchmark" in content or "performance" in content:
                        requirements["performance"] = True
                    
                    # Default to unit tests for any Python code
                    requirements["unit"] = True
                    
            except Exception as e:
                logger.error(f"Could not analyze {file_path}: {e}")
        
        return requirements
    
    def run_unit_tests(self) -> bool:
        """Execute unit tests with coverage"""
        logger.info("🧪 Running unit tests...")
        
        success, output, error = self.run_command(
            "pytest tests/unit -v --tb=short --cov=src --cov-report=term-missing --json-report --json-report-file=/tmp/unit-test-report.json 2>/dev/null || pytest tests/ -k 'not integration and not e2e' -v --tb=short"
        )
        
        if success:
            logger.info("✅ Unit tests passed")
            self.test_results["test_types"]["unit"]["passed"] += 1
        else:
            logger.error("❌ Unit tests failed")
            self.test_results["test_types"]["unit"]["failed"] += 1
            # Log first few lines of error for debugging
            error_lines = (output + error).split('\n')[:10]
            for line in error_lines:
                if line.strip():
                    logger.error(f"  {line}")
        
        # Extract coverage if available
        if "TOTAL" in output:
            for line in output.split('\n'):
                if "TOTAL" in line:
                    parts = line.split()
                    for part in parts:
                        if part.endswith('%'):
                            try:
                                self.test_results["coverage"] = float(part.rstrip('%'))
                            except:
                                pass
        
        return success
    
    def run_integration_tests(self) -> bool:
        """Execute integration tests"""
        logger.info("🔗 Running integration tests...")
        
        # Check if integration tests exist
        if not Path(self.project_root, "tests/integration").exists():
            logger.info("ℹ️ No integration tests found, skipping...")
            return True
        
        success, output, error = self.run_command(
            "pytest tests/integration -v --tb=short"
        )
        
        if success:
            logger.info("✅ Integration tests passed")
            self.test_results["test_types"]["integration"]["passed"] += 1
        else:
            logger.error("❌ Integration tests failed")
            self.test_results["test_types"]["integration"]["failed"] += 1
        
        return success
    
    def run_e2e_tests(self) -> bool:
        """Execute E2E tests"""
        logger.info("🌐 Running E2E tests...")
        
        # Check if E2E tests exist
        if not Path(self.project_root, "tests/e2e").exists():
            logger.info("ℹ️ No E2E tests found, skipping...")
            return True
        
        success, output, error = self.run_command(
            "pytest tests/e2e -v --tb=short"
        )
        
        if success:
            logger.info("✅ E2E tests passed")
            self.test_results["test_types"]["e2e"]["passed"] += 1
        else:
            logger.error("❌ E2E tests failed")
            self.test_results["test_types"]["e2e"]["failed"] += 1
        
        return success
    
    def run_security_tests(self) -> bool:
        """Execute security tests"""
        logger.info("🛡️ Running security tests...")
        
        # Run bandit for security analysis
        success, output, error = self.run_command(
            "bandit -r src/ -f json 2>/dev/null || echo 'Bandit not installed'"
        )
        
        if "not installed" not in output:
            if success:
                logger.info("✅ Security tests passed")
            else:
                logger.warning("⚠️ Security issues found")
        
        return True  # Don't fail on security tests
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("\n" + "="*50)
        report.append("📊 TEST EXECUTION REPORT")
        report.append("="*50)
        
        # Overall summary
        total_passed = sum(t["passed"] for t in self.test_results["test_types"].values())
        total_failed = sum(t["failed"] for t in self.test_results["test_types"].values())
        
        report.append(f"\n✅ Passed: {total_passed}")
        report.append(f"❌ Failed: {total_failed}")
        report.append(f"📈 Coverage: {self.test_results['coverage']:.1f}%")
        
        # Detailed results
        report.append("\nTest Categories:")
        for test_type, results in self.test_results["test_types"].items():
            if results["passed"] > 0 or results["failed"] > 0:
                status = "✅" if results["failed"] == 0 else "❌"
                report.append(f"  {status} {test_type.capitalize()}: {results['passed']} passed, {results['failed']} failed")
        
        # Coverage analysis
        if self.test_results["coverage"] > 0:
            report.append(f"\nCoverage Analysis:")
            if self.test_results["coverage"] >= 80:
                report.append(f"  ✅ Excellent coverage: {self.test_results['coverage']:.1f}%")
            elif self.test_results["coverage"] >= 60:
                report.append(f"  ⚠️ Good coverage: {self.test_results['coverage']:.1f}%")
            else:
                report.append(f"  ❌ Low coverage: {self.test_results['coverage']:.1f}%")
        
        # Recommendations
        if total_failed > 0:
            report.append("\n⚠️ Recommendations:")
            report.append("  - Fix failing tests before merging")
            report.append("  - Run tests locally with: pytest -v")
        
        if self.test_results["coverage"] < 80:
            report.append("  - Increase test coverage to 80%+")
            report.append("  - Focus on untested code paths")
        
        report.append("\n" + "="*50)
        return "\n".join(report)


def main():
    """Main hook entry point"""
    # Read task data from stdin
    try:
        task_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        logger.error("Failed to parse task data")
        sys.exit(1)
    
    # Check if this is a test-related task
    task_name = task_data.get("name", "").lower()
    if "test" not in task_name and not task_data.get("run_tests", False):
        # Not a test task, skip
        sys.exit(0)
    
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', '.')
    runner = TestRunner(project_root)
    
    # Get modified files from task
    artifacts = task_data.get("artifacts", {})
    files = artifacts.get("files_created", []) + artifacts.get("files_modified", [])
    
    # Analyze what tests are needed
    logger.info("🔍 Analyzing test requirements...")
    requirements = runner.analyze_test_requirements(files)
    
    # Execute appropriate tests
    all_passed = True
    
    if requirements["unit"]:
        if not runner.run_unit_tests():
            all_passed = False
    
    if requirements["integration"]:
        if not runner.run_integration_tests():
            all_passed = False
    
    if requirements["e2e"]:
        if not runner.run_e2e_tests():
            all_passed = False
    
    if requirements["security"]:
        runner.run_security_tests()  # Don't fail on security
    
    # Generate and display report
    report = runner.generate_test_report()
    print(report, file=sys.stderr)
    
    # Exit with appropriate code
    if not all_passed:
        logger.error("❌ Some tests failed. Please fix them before proceeding.")
        sys.exit(1)
    else:
        logger.info("✅ All tests passed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()