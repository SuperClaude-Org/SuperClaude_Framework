"""
Unit tests for ConfidenceChecker

Tests pre-execution confidence assessment functionality.
"""

import pytest

from superclaude.pm_agent.confidence import ConfidenceChecker


class TestConfidenceChecker:
    """Test suite for ConfidenceChecker class"""

    def test_high_confidence_scenario(self, sample_context):
        """
        Test that a well-prepared context returns high confidence (≥90%)

        All checks pass:
        - No duplicates (25%)
        - Architecture compliant (25%)
        - Official docs verified (20%)
        - OSS reference found (15%)
        - Root cause identified (15%)
        Total: 100%
        """
        checker = ConfidenceChecker()
        confidence = checker.assess(sample_context)

        assert confidence >= 0.9, f"Expected high confidence ≥0.9, got {confidence}"
        assert confidence == 1.0, "All checks passed should give 100% confidence"

    def test_low_confidence_scenario(self, low_confidence_context):
        """
        Test that an unprepared context returns low confidence (<70%)

        No checks pass: 0%
        """
        checker = ConfidenceChecker()
        confidence = checker.assess(low_confidence_context)

        assert confidence < 0.7, f"Expected low confidence <0.7, got {confidence}"
        assert confidence == 0.0, "No checks passed should give 0% confidence"

    def test_medium_confidence_scenario(self):
        """
        Test medium confidence scenario (70-89%)

        Some checks pass, some don't
        """
        checker = ConfidenceChecker()
        context = {
            "test_name": "test_feature",
            "duplicate_check_complete": True,  # 25%
            "architecture_check_complete": True,  # 25%
            "official_docs_verified": True,  # 20%
            "oss_reference_complete": False,  # 0%
            "root_cause_identified": False,  # 0%
        }

        confidence = checker.assess(context)

        assert 0.7 <= confidence < 0.9, (
            f"Expected medium confidence 0.7-0.9, got {confidence}"
        )
        assert confidence == 0.7, "Should be exactly 70%"

    def test_confidence_checks_recorded(self, sample_context):
        """Test that confidence checks are recorded in context"""
        checker = ConfidenceChecker()
        checker.assess(sample_context)

        assert "confidence_checks" in sample_context
        assert isinstance(sample_context["confidence_checks"], list)
        assert len(sample_context["confidence_checks"]) == 5

        # All checks should pass
        for check in sample_context["confidence_checks"]:
            assert check.startswith("✅"), f"Expected passing check, got: {check}"

    def test_get_recommendation_high(self):
        """Test recommendation for high confidence"""
        checker = ConfidenceChecker()
        recommendation = checker.get_recommendation(0.95)

        assert "High confidence" in recommendation
        assert "Proceed" in recommendation

    def test_get_recommendation_medium(self):
        """Test recommendation for medium confidence"""
        checker = ConfidenceChecker()
        recommendation = checker.get_recommendation(0.75)

        assert "Medium confidence" in recommendation
        assert "Continue investigation" in recommendation

    def test_get_recommendation_low(self):
        """Test recommendation for low confidence"""
        checker = ConfidenceChecker()
        recommendation = checker.get_recommendation(0.5)

        assert "Low confidence" in recommendation
        assert "STOP" in recommendation

    def test_has_official_docs_with_flag(self):
        """Test official docs check with direct flag"""
        checker = ConfidenceChecker()
        context = {"official_docs_verified": True}

        result = checker._has_official_docs(context)

        assert result is True

    def test_no_duplicates_check(self):
        """Test duplicate check validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"duplicate_check_complete": True}
        assert checker._no_duplicates(context_pass) is True

        # Without flag
        context_fail = {"duplicate_check_complete": False}
        assert checker._no_duplicates(context_fail) is False

    def test_architecture_compliance_check(self):
        """Test architecture compliance validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"architecture_check_complete": True}
        assert checker._architecture_compliant(context_pass) is True

        # Without flag
        context_fail = {}
        assert checker._architecture_compliant(context_fail) is False

    def test_oss_reference_check(self):
        """Test OSS reference validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"oss_reference_complete": True}
        assert checker._has_oss_reference(context_pass) is True

        # Without flag
        context_fail = {"oss_reference_complete": False}
        assert checker._has_oss_reference(context_fail) is False

    def test_root_cause_check(self):
        """Test root cause identification validation"""
        checker = ConfidenceChecker()

        # With flag
        context_pass = {"root_cause_identified": True}
        assert checker._root_cause_identified(context_pass) is True

        # Without flag
        context_fail = {}
        assert checker._root_cause_identified(context_fail) is False


@pytest.mark.confidence_check
def test_confidence_check_marker_integration(confidence_checker):
    """
    Test that confidence_check marker works with pytest plugin fixture

    This test should skip if confidence < 70%
    """
    context = {
        "test_name": "test_confidence_check_marker_integration",
        "has_official_docs": True,
        "duplicate_check_complete": True,
        "architecture_check_complete": True,
        "official_docs_verified": True,
        "oss_reference_complete": True,
        "root_cause_identified": True,
    }

    confidence = confidence_checker.assess(context)
    assert confidence >= 0.7, "Confidence should be high enough to not skip"
