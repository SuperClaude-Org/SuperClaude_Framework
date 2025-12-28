"""
Pytest configuration and shared fixtures for SuperClaude tests

This file is automatically loaded by pytest and provides
shared fixtures available to all test modules.
"""

import pytest


@pytest.fixture
def sample_context():
    """
    Provide a sample context for confidence checking tests

    Returns:
        Dict with test context including various checks
    """
    return {
        "test_name": "test_sample_feature",
        "test_file": __file__,
        "duplicate_check_complete": True,
        "architecture_check_complete": True,
        "official_docs_verified": True,
        "oss_reference_complete": True,
        "root_cause_identified": True,
        "markers": ["unit", "confidence_check"],
    }


@pytest.fixture
def low_confidence_context():
    """
    Provide a context that should result in low confidence

    Returns:
        Dict with incomplete checks
    """
    return {
        "test_name": "test_unclear_feature",
        "test_file": __file__,
        "duplicate_check_complete": False,
        "architecture_check_complete": False,
        "official_docs_verified": False,
        "oss_reference_complete": False,
        "root_cause_identified": False,
        "markers": ["unit"],
    }


@pytest.fixture
def sample_implementation():
    """
    Provide a sample implementation for self-check validation

    Returns:
        Dict with implementation details
    """
    return {
        "tests_passed": True,
        "test_output": "✅ 5 tests passed in 0.42s",
        "requirements": ["Feature A", "Feature B", "Feature C"],
        "requirements_met": ["Feature A", "Feature B", "Feature C"],
        "assumptions": ["API returns JSON", "Database is PostgreSQL"],
        "assumptions_verified": ["API returns JSON", "Database is PostgreSQL"],
        "evidence": {
            "test_results": "✅ All tests passing",
            "code_changes": ["file1.py", "file2.py"],
            "validation": "Linting passed, type checking passed",
        },
        "status": "complete",
    }


@pytest.fixture
def failing_implementation():
    """
    Provide a failing implementation for self-check validation

    Returns:
        Dict with failing implementation details
    """
    return {
        "tests_passed": False,
        "test_output": "",
        "requirements": ["Feature A", "Feature B", "Feature C"],
        "requirements_met": ["Feature A"],
        "assumptions": ["API returns JSON", "Database is PostgreSQL"],
        "assumptions_verified": ["API returns JSON"],
        "evidence": {},
        "status": "complete",
        "errors": ["TypeError in module X"],
    }


@pytest.fixture
def temp_memory_dir(tmp_path):
    """
    Create temporary memory directory structure for PM Agent tests

    Args:
        tmp_path: pytest's temporary path fixture

    Returns:
        Path to temporary memory directory
    """
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)

    # Create empty memory files
    (memory_dir / "pm_context.md").write_text("# PM Context\n")
    (memory_dir / "last_session.md").write_text("# Last Session\n")
    (memory_dir / "next_actions.md").write_text("# Next Actions\n")
    (memory_dir / "reflexion.jsonl").write_text("")

    return memory_dir
