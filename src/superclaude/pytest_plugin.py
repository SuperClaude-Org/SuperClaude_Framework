"""
SuperClaude pytest plugin

Auto-loaded when superclaude is installed.
Provides PM Agent fixtures and hooks for enhanced testing.

Entry point registered in pyproject.toml:
    [project.entry-points.pytest11]
    superclaude = "superclaude.pytest_plugin"
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional

from .pm_agent.confidence import ConfidenceChecker
from .pm_agent.self_check import SelfCheckProtocol
from .pm_agent.reflexion import ReflexionPattern
from .pm_agent.token_budget import TokenBudgetManager


def pytest_configure(config):
    """
    Register SuperClaude plugin and custom markers

    Markers:
        - confidence_check: Pre-execution confidence assessment
        - self_check: Post-implementation validation
        - reflexion: Error learning and prevention
        - complexity(level): Set test complexity (simple, medium, complex)
    """
    config.addinivalue_line(
        "markers",
        "confidence_check: Pre-execution confidence assessment (min 70%)"
    )
    config.addinivalue_line(
        "markers",
        "self_check: Post-implementation validation with evidence requirement"
    )
    config.addinivalue_line(
        "markers",
        "reflexion: Error learning and prevention pattern"
    )
    config.addinivalue_line(
        "markers",
        "complexity(level): Set test complexity (simple, medium, complex)"
    )


@pytest.fixture
def confidence_checker():
    """
    Fixture for pre-execution confidence checking

    Usage:
        def test_example(confidence_checker):
            confidence = confidence_checker.assess(context)
            assert confidence >= 0.7
    """
    return ConfidenceChecker()


@pytest.fixture
def self_check_protocol():
    """
    Fixture for post-implementation self-check protocol

    Usage:
        def test_example(self_check_protocol):
            passed, issues = self_check_protocol.validate(implementation)
            assert passed
    """
    return SelfCheckProtocol()


@pytest.fixture
def reflexion_pattern():
    """
    Fixture for reflexion error learning pattern

    Usage:
        def test_example(reflexion_pattern):
            reflexion_pattern.record_error(...)
            solution = reflexion_pattern.get_solution(error_signature)
    """
    return ReflexionPattern()


@pytest.fixture
def token_budget(request):
    """
    Fixture for token budget management

    Complexity levels:
        - simple: 200 tokens (typo fix)
        - medium: 1,000 tokens (bug fix)
        - complex: 2,500 tokens (feature implementation)

    Usage:
        @pytest.mark.complexity("medium")
        def test_example(token_budget):
            assert token_budget.limit == 1000
    """
    # Get test complexity from marker
    marker = request.node.get_closest_marker("complexity")
    complexity = marker.args[0] if marker else "medium"
    return TokenBudgetManager(complexity=complexity)


@pytest.fixture
def pm_context(tmp_path):
    """
    Fixture providing PM Agent context for testing

    Creates temporary memory directory structure:
        - docs/memory/pm_context.md
        - docs/memory/last_session.md
        - docs/memory/next_actions.md

    Usage:
        def test_example(pm_context):
            assert pm_context["memory_dir"].exists()
            pm_context["pm_context"].write_text("# Context")
    """
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)

    # Create empty memory files
    (memory_dir / "pm_context.md").touch()
    (memory_dir / "last_session.md").touch()
    (memory_dir / "next_actions.md").touch()

    return {
        "memory_dir": memory_dir,
        "pm_context": memory_dir / "pm_context.md",
        "last_session": memory_dir / "last_session.md",
        "next_actions": memory_dir / "next_actions.md",
    }


def pytest_runtest_setup(item):
    """
    Pre-test hook for confidence checking

    If test is marked with @pytest.mark.confidence_check,
    run pre-execution confidence assessment and skip if < 70%.
    """
    marker = item.get_closest_marker("confidence_check")
    if marker:
        checker = ConfidenceChecker()

        # Build context from test
        context = {
            "test_name": item.name,
            "test_file": str(item.fspath),
            "markers": [m.name for m in item.iter_markers()],
        }

        confidence = checker.assess(context)

        if confidence < 0.7:
            pytest.skip(
                f"Confidence too low: {confidence:.0%} (minimum: 70%)"
            )


def pytest_runtest_makereport(item, call):
    """
    Post-test hook for self-check and reflexion

    Records test outcomes for reflexion learning.
    Stores error information for future pattern matching.
    """
    if call.when == "call":
        # Check for reflexion marker
        marker = item.get_closest_marker("reflexion")

        if marker and call.excinfo is not None:
            # Test failed - apply reflexion pattern
            reflexion = ReflexionPattern()

            # Record error for future learning
            error_info = {
                "test_name": item.name,
                "test_file": str(item.fspath),
                "error_type": type(call.excinfo.value).__name__,
                "error_message": str(call.excinfo.value),
                "traceback": str(call.excinfo.traceback),
            }

            reflexion.record_error(error_info)


def pytest_report_header(config):
    """Add SuperClaude version to pytest header"""
    from . import __version__
    return f"SuperClaude: {__version__}"


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add automatic markers

    - Adds 'unit' marker to test files in tests/unit/
    - Adds 'integration' marker to test files in tests/integration/
    - Adds 'hallucination' marker to test files matching *hallucination*
    - Adds 'performance' marker to test files matching *performance*
    """
    for item in items:
        test_path = str(item.fspath)

        # Auto-mark by directory
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)

        # Auto-mark by filename
        if "hallucination" in test_path:
            item.add_marker(pytest.mark.hallucination)
        elif "performance" in test_path or "benchmark" in test_path:
            item.add_marker(pytest.mark.performance)
