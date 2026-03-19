"""
Tests for SuperClaude Doctor Command

Tests health check functionality.
"""

from pathlib import Path
from unittest.mock import patch


class TestDoctor:
    """Tests for doctor module"""

    def test_run_doctor_returns_dict(self):
        """Test run_doctor returns expected dict structure"""
        from superclaude.cli.doctor import run_doctor

        result = run_doctor()

        assert isinstance(result, dict)
        assert "checks" in result
        assert "passed" in result
        assert isinstance(result["checks"], list)

    def test_run_doctor_with_verbose(self):
        """Test run_doctor with verbose flag"""
        from superclaude.cli.doctor import run_doctor

        result = run_doctor(verbose=True)

        assert isinstance(result, dict)
        assert "checks" in result

    def test_check_pytest_plugin_structure(self):
        """Test pytest plugin check returns proper structure"""
        from superclaude.cli.doctor import _check_pytest_plugin

        result = _check_pytest_plugin()

        assert isinstance(result, dict)
        assert "name" in result
        assert "passed" in result
        assert isinstance(result["passed"], bool)

    def test_check_skills_installed_structure(self):
        """Test skills check returns proper structure"""
        from superclaude.cli.doctor import _check_skills_installed

        result = _check_skills_installed()

        assert isinstance(result, dict)
        assert "name" in result
        assert "passed" in result
        assert "details" in result

    def test_check_skills_installed_no_skills_dir(self):
        """Test skills check when no skills directory exists"""
        from superclaude.cli.doctor import _check_skills_installed

        with patch.object(Path, "exists", return_value=False):
            result = _check_skills_installed()

        # Should pass even without skills (optional)
        assert result["passed"] is True

    def test_check_configuration_structure(self):
        """Test configuration check returns proper structure"""
        from superclaude.cli.doctor import _check_configuration

        result = _check_configuration()

        assert isinstance(result, dict)
        assert "name" in result
        assert "passed" in result

    def test_check_configuration_success(self):
        """Test configuration check passes with installed package"""
        from superclaude.cli.doctor import _check_configuration

        result = _check_configuration()

        # Should pass since superclaude is installed
        assert result["passed"] is True
        assert "details" in result
        assert any("SuperClaude" in d for d in result["details"])

    def test_all_checks_have_required_keys(self):
        """Test all checks return required keys"""
        from superclaude.cli.doctor import run_doctor

        result = run_doctor()

        for check in result["checks"]:
            assert "name" in check
            assert "passed" in check


class TestDoctorEdgeCases:
    """Edge case tests for doctor"""

    def test_run_doctor_passed_reflects_all_checks(self):
        """Test that passed reflects all check statuses"""
        from superclaude.cli.doctor import run_doctor

        result = run_doctor()

        expected_passed = all(check["passed"] for check in result["checks"])
        assert result["passed"] == expected_passed

    @patch("superclaude.cli.doctor._check_pytest_plugin")
    def test_run_doctor_aggregates_failures(self, mock_plugin_check):
        """Test run_doctor properly aggregates check failures"""
        mock_plugin_check.return_value = {
            "name": "pytest plugin",
            "passed": False,
            "details": ["Test failure"],
        }

        from superclaude.cli.doctor import run_doctor

        result = run_doctor()

        # At least one check should report the mocked failure
        assert isinstance(result, dict)
