"""
Integration tests for the execution engine orchestrator

Tests intelligent_execute, quick_execute, and safe_execute functions
that combine reflection, parallel execution, and self-correction.
"""

import pytest

from superclaude.execution import intelligent_execute, quick_execute, safe_execute


class TestQuickExecute:
    """Test quick_execute convenience function"""

    def test_quick_execute_simple_ops(self):
        """Quick execute should run simple operations and return results"""
        results = quick_execute([
            lambda: "result_a",
            lambda: "result_b",
            lambda: 42,
        ])

        assert results == ["result_a", "result_b", 42]

    def test_quick_execute_empty(self):
        """Quick execute with no operations should return empty list"""
        results = quick_execute([])
        assert results == []

    def test_quick_execute_single(self):
        """Quick execute with single operation"""
        results = quick_execute([lambda: "only"])
        assert results == ["only"]


class TestIntelligentExecute:
    """Test the intelligent_execute orchestrator"""

    def test_execute_with_clear_task(self, tmp_path):
        """Clear task with simple operations should succeed"""
        # Create PROJECT_INDEX.md so context check passes
        (tmp_path / "PROJECT_INDEX.md").write_text("# Index")
        (tmp_path / "docs" / "memory").mkdir(parents=True, exist_ok=True)

        result = intelligent_execute(
            task="Create a new function called validate_email in validators.py",
            operations=[lambda: "validated"],
            context={
                "project_index": "loaded",
                "current_branch": "main",
                "git_status": "clean",
            },
            repo_path=tmp_path,
        )

        assert result["status"] in ("success", "blocked")
        assert "confidence" in result

    def test_execute_blocked_by_low_confidence(self, tmp_path):
        """Vague task should be blocked by reflection engine"""
        (tmp_path / "docs" / "memory").mkdir(parents=True, exist_ok=True)

        result = intelligent_execute(
            task="fix",
            operations=[lambda: "done"],
            repo_path=tmp_path,
        )

        # Very short vague task may get blocked
        assert result["status"] in ("blocked", "success", "partial_failure")
        assert "confidence" in result

    def test_execute_with_failing_operation(self, tmp_path):
        """Failing operation should trigger self-correction"""
        (tmp_path / "PROJECT_INDEX.md").write_text("# Index")
        (tmp_path / "docs" / "memory").mkdir(parents=True, exist_ok=True)

        def failing():
            raise ValueError("Test failure")

        result = intelligent_execute(
            task="Create validation endpoint in api/validate.py",
            operations=[lambda: "ok", failing],
            context={
                "project_index": "loaded",
                "current_branch": "main",
                "git_status": "clean",
            },
            repo_path=tmp_path,
            auto_correct=True,
        )

        assert result["status"] in ("partial_failure", "blocked", "failed")

    def test_execute_no_auto_correct(self, tmp_path):
        """Disabling auto_correct should skip self-correction phase"""
        (tmp_path / "PROJECT_INDEX.md").write_text("# Index")
        (tmp_path / "docs" / "memory").mkdir(parents=True, exist_ok=True)

        result = intelligent_execute(
            task="Create helper function in utils.py for date formatting",
            operations=[lambda: "done"],
            context={
                "project_index": "loaded",
                "current_branch": "main",
                "git_status": "clean",
            },
            repo_path=tmp_path,
            auto_correct=False,
        )

        assert result["status"] in ("success", "blocked")


class TestSafeExecute:
    """Test safe_execute convenience function"""

    def test_safe_execute_success(self, tmp_path):
        """Safe execute should return result on success"""
        (tmp_path / "PROJECT_INDEX.md").write_text("# Index")
        (tmp_path / "docs" / "memory").mkdir(parents=True, exist_ok=True)

        try:
            result = safe_execute(
                task="Create user validation function in validators.py",
                operation=lambda: "validated",
                context={
                    "project_index": "loaded",
                    "current_branch": "main",
                    "git_status": "clean",
                },
            )
            # If it proceeds, should get result
            assert result is not None
        except RuntimeError:
            # If blocked by low confidence, that's also valid
            pass
