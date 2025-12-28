"""
Unit tests for SelfCheckProtocol

Tests post-implementation validation functionality.
"""

import pytest

from superclaude.pm_agent.self_check import SelfCheckProtocol


class TestSelfCheckProtocol:
    """Test suite for SelfCheckProtocol class"""

    def test_validate_passing_implementation(self, sample_implementation):
        """
        Test validation of a complete, passing implementation

        Should pass all four questions:
        1. Tests passing? ✅
        2. Requirements met? ✅
        3. Assumptions verified? ✅
        4. Evidence provided? ✅
        """
        protocol = SelfCheckProtocol()
        passed, issues = protocol.validate(sample_implementation)

        assert passed is True, f"Expected validation to pass, got issues: {issues}"
        assert len(issues) == 0, f"Expected no issues, got {len(issues)}: {issues}"

    def test_validate_failing_implementation(self, failing_implementation):
        """
        Test validation of a failing implementation

        Should fail multiple checks
        """
        protocol = SelfCheckProtocol()
        passed, issues = protocol.validate(failing_implementation)

        assert passed is False, "Expected validation to fail"
        assert len(issues) > 0, "Expected issues to be detected"

        # Check specific issues
        issue_text = " ".join(issues)
        assert "Tests not passing" in issue_text or "test" in issue_text.lower()

    def test_check_tests_passing_with_output(self):
        """Test that tests_passed requires actual output"""
        protocol = SelfCheckProtocol()

        # Tests passed WITH output - should pass
        impl_with_output = {
            "tests_passed": True,
            "test_output": "✅ 10 tests passed",
        }
        assert protocol._check_tests_passing(impl_with_output) is True

        # Tests passed WITHOUT output - should fail (hallucination detection)
        impl_without_output = {
            "tests_passed": True,
            "test_output": "",
        }
        assert protocol._check_tests_passing(impl_without_output) is False

    def test_check_requirements_met(self):
        """Test requirements validation"""
        protocol = SelfCheckProtocol()

        # All requirements met
        impl_complete = {
            "requirements": ["A", "B", "C"],
            "requirements_met": ["A", "B", "C"],
        }
        unmet = protocol._check_requirements_met(impl_complete)
        assert len(unmet) == 0

        # Some requirements not met
        impl_incomplete = {
            "requirements": ["A", "B", "C"],
            "requirements_met": ["A", "B"],
        }
        unmet = protocol._check_requirements_met(impl_incomplete)
        assert len(unmet) == 1
        assert "C" in unmet

    def test_check_assumptions_verified(self):
        """Test assumptions verification"""
        protocol = SelfCheckProtocol()

        # All assumptions verified
        impl_verified = {
            "assumptions": ["API is REST", "DB is PostgreSQL"],
            "assumptions_verified": ["API is REST", "DB is PostgreSQL"],
        }
        unverified = protocol._check_assumptions_verified(impl_verified)
        assert len(unverified) == 0

        # Some assumptions unverified
        impl_unverified = {
            "assumptions": ["API is REST", "DB is PostgreSQL"],
            "assumptions_verified": ["API is REST"],
        }
        unverified = protocol._check_assumptions_verified(impl_unverified)
        assert len(unverified) == 1
        assert "DB is PostgreSQL" in unverified

    def test_check_evidence_exists(self):
        """Test evidence requirement validation"""
        protocol = SelfCheckProtocol()

        # All evidence present
        impl_with_evidence = {
            "evidence": {
                "test_results": "Tests passed",
                "code_changes": ["file1.py"],
                "validation": "Linting passed",
            }
        }
        missing = protocol._check_evidence_exists(impl_with_evidence)
        assert len(missing) == 0

        # Missing all evidence
        impl_no_evidence = {"evidence": {}}
        missing = protocol._check_evidence_exists(impl_no_evidence)
        assert len(missing) == 3
        assert "test_results" in missing
        assert "code_changes" in missing
        assert "validation" in missing

    def test_detect_hallucinations_tests_without_output(self):
        """Test hallucination detection: claims tests pass without output"""
        protocol = SelfCheckProtocol()

        impl = {
            "tests_passed": True,
            "test_output": "",  # No output - hallucination!
        }

        detected = protocol._detect_hallucinations(impl)

        assert len(detected) > 0
        assert any("without showing output" in d for d in detected)

    def test_detect_hallucinations_complete_without_evidence(self):
        """Test hallucination detection: claims complete without evidence"""
        protocol = SelfCheckProtocol()

        impl = {
            "status": "complete",
            "evidence": None,  # No evidence - hallucination!
        }

        detected = protocol._detect_hallucinations(impl)

        assert len(detected) > 0
        assert any("without evidence" in d for d in detected)

    def test_detect_hallucinations_complete_with_failing_tests(self):
        """Test hallucination detection: claims complete despite failing tests"""
        protocol = SelfCheckProtocol()

        impl = {
            "status": "complete",
            "tests_passed": False,  # Tests failed but claims complete!
        }

        detected = protocol._detect_hallucinations(impl)

        assert len(detected) > 0
        assert any("failing tests" in d for d in detected)

    def test_detect_hallucinations_ignored_errors(self):
        """Test hallucination detection: ignored errors/warnings"""
        protocol = SelfCheckProtocol()

        impl = {
            "status": "complete",
            "errors": ["TypeError in module X"],
            "warnings": ["Deprecated function used"],
        }

        detected = protocol._detect_hallucinations(impl)

        assert len(detected) > 0
        assert any("errors/warnings" in d for d in detected)

    def test_detect_hallucinations_uncertainty_language(self):
        """Test hallucination detection: uncertainty language"""
        protocol = SelfCheckProtocol()

        impl = {
            "description": "This probably works and might be correct",
        }

        detected = protocol._detect_hallucinations(impl)

        assert len(detected) > 0
        assert any("Uncertainty language" in d for d in detected)

    def test_format_report_passing(self):
        """Test report formatting for passing validation"""
        protocol = SelfCheckProtocol()

        report = protocol.format_report(passed=True, issues=[])

        assert "PASSED" in report
        assert "✅" in report

    def test_format_report_failing(self):
        """Test report formatting for failing validation"""
        protocol = SelfCheckProtocol()

        issues = [
            "❌ Tests not passing",
            "❌ Missing evidence: test_results",
        ]

        report = protocol.format_report(passed=False, issues=issues)

        assert "FAILED" in report
        assert "❌" in report
        for issue in issues:
            assert issue in report


@pytest.mark.self_check
def test_self_check_marker_integration(self_check_protocol, sample_implementation):
    """
    Test that self_check marker works with pytest plugin fixture

    This test validates the fixture provided by pytest plugin
    """
    passed, issues = self_check_protocol.validate(sample_implementation)

    assert passed is True, f"Sample implementation should pass validation: {issues}"
    assert len(issues) == 0, "No issues should be detected in sample implementation"
