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


class TestCodebaseSearchImplementation:
    """Test actual codebase search logic (not just flag-based)"""

    def test_find_project_root_from_test_file(self, tmp_path):
        """Test finding project root from test file path"""
        # Create project structure
        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "src").mkdir()
        test_file = tmp_path / "tests" / "test_example.py"
        test_file.parent.mkdir()
        test_file.touch()

        checker = ConfidenceChecker()
        context = {"test_file": str(test_file)}
        root = checker._find_project_root(context)

        assert root == tmp_path

    def test_find_project_root_from_claude_md(self, tmp_path):
        """Test finding project root via CLAUDE.md"""
        (tmp_path / "CLAUDE.md").touch()
        test_file = tmp_path / "deep" / "nested" / "test.py"
        test_file.parent.mkdir(parents=True)
        test_file.touch()

        checker = ConfidenceChecker()
        context = {"test_file": str(test_file)}
        root = checker._find_project_root(context)

        assert root == tmp_path

    def test_find_project_root_explicit(self, tmp_path):
        """Test explicit project_root in context"""
        checker = ConfidenceChecker()
        context = {"project_root": str(tmp_path)}
        root = checker._find_project_root(context)

        assert root == tmp_path

    def test_search_codebase_finds_similar_files(self, tmp_path):
        """Test searching for similar file names"""
        (tmp_path / "auth_handler.py").write_text("class AuthHandler: pass")
        (tmp_path / "authentication.py").write_text("def authenticate(): pass")

        checker = ConfidenceChecker()
        results = checker._search_codebase(
            tmp_path,
            "auth",
            patterns=["**/*.py"],
            exclude_dirs=[],
        )

        assert len(results) >= 1
        assert any("auth" in r.lower() for r in results)

    def test_search_codebase_finds_function_definitions(self, tmp_path):
        """Test finding function definitions in files"""
        (tmp_path / "utils.py").write_text(
            "def validate_token(token):\n    return True"
        )

        checker = ConfidenceChecker()
        results = checker._search_codebase(
            tmp_path,
            "validate_token",
            patterns=["**/*.py"],
            exclude_dirs=[],
        )

        assert "utils.py" in results

    def test_search_codebase_excludes_directories(self, tmp_path):
        """Test excluding node_modules and similar directories"""
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "auth.py").write_text("class Auth: pass")
        (tmp_path / "src" / "auth.py").parent.mkdir()
        (tmp_path / "src" / "auth.py").write_text("class Auth: pass")

        checker = ConfidenceChecker()
        results = checker._search_codebase(
            tmp_path,
            "auth",
            patterns=["**/*.py"],
            exclude_dirs=["node_modules"],
        )

        assert not any("node_modules" in r for r in results)
        assert any("src" in r for r in results)

    def test_no_duplicates_actual_search(self, tmp_path):
        """Test duplicate detection via actual codebase search"""
        # Create project structure with potential duplicate
        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "auth_manager.py").write_text(
            "class AuthManager:\n    pass"
        )

        checker = ConfidenceChecker()
        context = {
            "project_root": str(tmp_path),
            "feature_name": "auth_manager",
        }

        result = checker._no_duplicates(context)

        # Should find potential duplicate
        assert result is False
        assert "potential_duplicates" in context
        assert len(context["potential_duplicates"]) > 0

    def test_no_duplicates_no_feature_name(self):
        """Test duplicate check returns False without feature name"""
        checker = ConfidenceChecker()
        context = {"project_root": "/tmp"}

        result = checker._no_duplicates(context)

        assert result is False


class TestTechStackDetection:
    """Test tech stack detection from CLAUDE.md"""

    def test_read_tech_stack_from_claude_md(self, tmp_path):
        """Test reading tech stack from CLAUDE.md"""
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("""# Project

This project uses Supabase for backend.
Built with Next.js and TypeScript.
Uses UV for Python package management.
""")

        checker = ConfidenceChecker()
        tech_stack = checker._read_tech_stack(tmp_path)

        assert tech_stack.get("has_claude_md") is True
        assert tech_stack.get("supabase") is True
        assert tech_stack.get("nextjs") is True
        assert tech_stack.get("typescript") is True
        assert tech_stack.get("uv") is True

    def test_read_tech_stack_detects_package_files(self, tmp_path):
        """Test detecting tech stack from package files"""
        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "package.json").touch()
        (tmp_path / "turbo.json").touch()

        checker = ConfidenceChecker()
        tech_stack = checker._read_tech_stack(tmp_path)

        assert tech_stack.get("python_project") is True
        assert tech_stack.get("node_project") is True
        assert tech_stack.get("turborepo") is True

    def test_check_architecture_anti_patterns_supabase(self):
        """Test detecting Supabase anti-patterns"""
        checker = ConfidenceChecker()
        tech_stack = {"supabase": True}

        warnings = checker._check_architecture_anti_patterns(
            tech_stack, "custom api with express"
        )

        assert len(warnings) > 0
        assert any("Supabase" in w for w in warnings)

    def test_check_architecture_anti_patterns_nextjs(self):
        """Test detecting Next.js anti-patterns"""
        checker = ConfidenceChecker()
        tech_stack = {"nextjs": True}

        warnings = checker._check_architecture_anti_patterns(
            tech_stack, "custom routing solution"
        )

        assert len(warnings) > 0
        assert any("Next.js" in w for w in warnings)

    def test_check_architecture_anti_patterns_uv(self):
        """Test detecting UV anti-patterns"""
        checker = ConfidenceChecker()
        tech_stack = {"uv": True}

        warnings = checker._check_architecture_anti_patterns(
            tech_stack, "pip install requests"
        )

        assert len(warnings) > 0
        assert any("UV" in w or "uv" in w for w in warnings)

    def test_architecture_compliant_actual_check(self, tmp_path):
        """Test architecture compliance with actual tech stack check"""
        (tmp_path / "CLAUDE.md").write_text("Uses Supabase for backend")
        (tmp_path / "pyproject.toml").touch()

        checker = ConfidenceChecker()
        context = {
            "project_root": str(tmp_path),
            "proposed_technology": "custom api with express",
        }

        result = checker._architecture_compliant(context)

        assert result is False
        assert "architecture_warnings" in context


class TestRootCauseAnalysis:
    """Test root cause identification logic"""

    def test_root_cause_with_uncertainty_language(self):
        """Test detecting uncertainty language in root cause"""
        checker = ConfidenceChecker()
        uncertain_phrases = [
            "The issue is probably in the auth module",
            "Maybe the database connection is timing out",
            "It might be a race condition",
            "Could be an issue with the cache",
            "Possibly related to memory leak",
            "Not sure but I think it's in the parser",
            "I guess the config is wrong",
            "I assume the API changed",
        ]

        for phrase in uncertain_phrases:
            context = {
                "root_cause": phrase,
                "proposed_solution": "A sufficiently detailed solution here",
            }
            result = checker._root_cause_identified(context)
            assert result is False, f"Should reject uncertainty: {phrase}"
            assert "root_cause_warning" in context

    def test_root_cause_confident_language(self):
        """Test accepting confident root cause statements"""
        checker = ConfidenceChecker()
        context = {
            "root_cause": "The authentication fails because the token expiration check uses UTC time but the token contains local time. Line 45 in auth.py.",
            "proposed_solution": "Convert token timestamp to UTC before comparison in validate_token function.",
        }

        result = checker._root_cause_identified(context)

        assert result is True

    def test_root_cause_missing_solution(self):
        """Test rejecting when no solution provided"""
        checker = ConfidenceChecker()
        context = {
            "root_cause": "The database query is inefficient",
        }

        result = checker._root_cause_identified(context)

        assert result is False
        assert "No proposed solution" in context.get("root_cause_warning", "")

    def test_root_cause_brief_solution(self):
        """Test rejecting too brief solutions"""
        checker = ConfidenceChecker()
        context = {
            "root_cause": "Token validation fails",
            "proposed_solution": "Fix token",
        }

        result = checker._root_cause_identified(context)

        assert result is False
        assert "too brief" in context.get("root_cause_warning", "")


class TestOSSReferenceCheck:
    """Test OSS reference validation logic"""

    def test_has_oss_reference_with_urls(self):
        """Test detecting OSS references via URLs"""
        checker = ConfidenceChecker()
        context = {
            "oss_references": [
                "https://github.com/example/project",
            ],
        }

        result = checker._has_oss_reference(context)

        assert result is True

    def test_has_oss_reference_with_doc_urls(self):
        """Test detecting documentation URLs"""
        checker = ConfidenceChecker()
        context = {
            "documentation_urls": [
                "https://docs.example.com/api",
            ],
        }

        result = checker._has_oss_reference(context)

        assert result is True

    def test_has_oss_reference_with_research_notes(self):
        """Test detecting research notes"""
        checker = ConfidenceChecker()
        context = {
            "research_notes": "Investigated the official documentation. The recommended approach is to use async/await pattern as shown in the examples."
        }

        result = checker._has_oss_reference(context)

        assert result is True

    def test_has_oss_reference_empty(self):
        """Test missing OSS references"""
        checker = ConfidenceChecker()
        context = {}

        result = checker._has_oss_reference(context)

        assert result is False
        assert "oss_recommendation" in context
