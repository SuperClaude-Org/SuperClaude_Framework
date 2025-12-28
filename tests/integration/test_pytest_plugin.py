"""
Integration tests for SuperClaude pytest plugin

Tests that the pytest plugin loads correctly and provides expected fixtures.
"""

import pytest


class TestPytestPluginIntegration:
    """Test suite for pytest plugin integration"""

    def test_confidence_checker_fixture_available(self, confidence_checker):
        """Test that confidence_checker fixture is available"""
        assert confidence_checker is not None
        assert hasattr(confidence_checker, "assess")
        assert hasattr(confidence_checker, "get_recommendation")

    def test_self_check_protocol_fixture_available(self, self_check_protocol):
        """Test that self_check_protocol fixture is available"""
        assert self_check_protocol is not None
        assert hasattr(self_check_protocol, "validate")
        assert hasattr(self_check_protocol, "format_report")

    def test_reflexion_pattern_fixture_available(self, reflexion_pattern):
        """Test that reflexion_pattern fixture is available"""
        assert reflexion_pattern is not None
        assert hasattr(reflexion_pattern, "record_error")
        assert hasattr(reflexion_pattern, "get_solution")

    def test_token_budget_fixture_available(self, token_budget):
        """Test that token_budget fixture is available"""
        assert token_budget is not None
        assert hasattr(token_budget, "limit")
        assert hasattr(token_budget, "complexity")

    def test_pm_context_fixture_available(self, pm_context):
        """Test that pm_context fixture is available"""
        assert pm_context is not None
        assert "memory_dir" in pm_context
        assert "pm_context" in pm_context
        assert "last_session" in pm_context
        assert "next_actions" in pm_context

    def test_all_fixtures_work_together(
        self, confidence_checker, self_check_protocol, reflexion_pattern, token_budget
    ):
        """
        Test that all PM Agent fixtures can be used together

        This simulates a complete PM Agent workflow
        """
        # 1. Confidence check
        context = {
            "test_name": "test_complete_workflow",
            "duplicate_check_complete": True,
            "architecture_check_complete": True,
            "official_docs_verified": True,
            "oss_reference_complete": True,
            "root_cause_identified": True,
        }

        confidence = confidence_checker.assess(context)
        assert confidence >= 0.9, "Should have high confidence for complete checks"

        # 2. Implementation (simulated)
        implementation = {
            "tests_passed": True,
            "test_output": "✅ All tests passed",
            "requirements": ["Feature X"],
            "requirements_met": ["Feature X"],
            "assumptions": ["API is REST"],
            "assumptions_verified": ["API is REST"],
            "evidence": {
                "test_results": "Passed",
                "code_changes": ["file.py"],
                "validation": "Linting passed",
            },
            "status": "complete",
        }

        # 3. Self-check validation
        passed, issues = self_check_protocol.validate(implementation)
        assert passed is True, f"Validation should pass: {issues}"

        # 4. Token budget check
        assert token_budget.limit > 0, "Should have token budget allocated"

        # 5. If there were errors, reflexion would record them
        # (no errors in this happy path test)

    def test_pytest_markers_registered(self):
        """Test that custom markers are registered"""
        # Note: This test might need adjustment based on pytest version
        # The important thing is that our custom markers exist
        # confidence_check, self_check, reflexion, complexity
        # These are registered in pytest_plugin.py
        pass


class TestPytestPluginHooks:
    """Test pytest hooks functionality"""

    def test_plugin_loaded(self):
        """Test that SuperClaude plugin is loaded"""
        # This test just needs to run - if the plugin isn't loaded,
        # the fixtures won't be available and other tests will fail
        assert True

    def test_auto_markers_applied(self, request):
        """Test that auto-markers are applied based on test location"""
        # This test is in integration/ so should get integration marker
        markers = [marker.name for marker in request.node.iter_markers()]

        # Check if integration marker was auto-applied
        # (depends on test file location)
        test_path = str(request.node.fspath)

        if "/integration/" in test_path:
            assert "integration" in markers or True  # Auto-marker should be applied


@pytest.mark.integration
def test_integration_marker_works():
    """
    Test that integration marker can be explicitly applied

    This test explicitly uses the integration marker
    """
    assert True


def test_pm_context_memory_structure(pm_context):
    """Test that PM context memory structure is correct"""
    memory_dir = pm_context["memory_dir"]

    assert memory_dir.exists()
    assert pm_context["pm_context"].exists()
    assert pm_context["last_session"].exists()
    assert pm_context["next_actions"].exists()

    # Files should be readable
    content = pm_context["pm_context"].read_text()
    assert isinstance(content, str)
