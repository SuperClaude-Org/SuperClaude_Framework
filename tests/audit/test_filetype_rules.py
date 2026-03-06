"""Tests for file-type specific verification rules (T03.02 / D-0018)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
)
from superclaude.cli.audit.filetype_rules import (
    FileType,
    classify_file_type,
    verify_classification,
)


class TestClassifyFileType:
    def test_python_source(self):
        assert classify_file_type("src/main.py") == FileType.SOURCE

    def test_typescript_source(self):
        assert classify_file_type("src/app.tsx") == FileType.SOURCE

    def test_json_config(self):
        assert classify_file_type("config/settings.json") == FileType.CONFIG

    def test_yaml_config(self):
        assert classify_file_type("docker-compose.yaml") == FileType.CONFIG

    def test_toml_config(self):
        assert classify_file_type("pyproject.toml") == FileType.CONFIG

    def test_markdown_docs(self):
        assert classify_file_type("docs/README.md") == FileType.DOCS

    def test_test_prefix(self):
        assert classify_file_type("tests/test_main.py") == FileType.TEST

    def test_test_infix(self):
        assert classify_file_type("src/app.test.ts") == FileType.TEST

    def test_spec_infix(self):
        assert classify_file_type("src/app.spec.js") == FileType.TEST

    def test_test_directory(self):
        assert classify_file_type("tests/integration/helper.py") == FileType.TEST

    def test_binary_image(self):
        assert classify_file_type("assets/logo.png") == FileType.BINARY

    def test_binary_compiled(self):
        assert classify_file_type("build/module.pyc") == FileType.BINARY


class TestVerifyClassification:
    def _make_result(
        self, path: str, action: V2Action, evidence: list[str],
    ) -> ClassificationResult:
        tier = V2Tier.TIER_2 if action == V2Action.KEEP else V2Tier.TIER_1
        return ClassificationResult(
            file_path=path,
            tier=tier,
            action=action,
            v1_category=V1Category.KEEP if action == V2Action.KEEP else V1Category.DELETE,
            confidence=0.85,
            evidence=evidence,
        )

    def test_source_keep_with_import_evidence(self):
        result = self._make_result(
            "src/main.py", V2Action.KEEP,
            ["import reference found in app.py"],
        )
        verification = verify_classification(result)
        assert verification.file_type == FileType.SOURCE
        assert verification.passed

    def test_source_keep_without_evidence_fails(self):
        result = self._make_result(
            "src/main.py", V2Action.KEEP, [],
        )
        verification = verify_classification(result)
        assert verification.file_type == FileType.SOURCE
        assert not verification.passed

    def test_config_keep_with_reference(self):
        result = self._make_result(
            "config/settings.json", V2Action.KEEP,
            ["reference in main.py config loader"],
        )
        verification = verify_classification(result)
        assert verification.file_type == FileType.CONFIG
        assert verification.passed

    def test_config_keep_without_reference_fails(self):
        result = self._make_result(
            "config/settings.json", V2Action.KEEP, [],
        )
        verification = verify_classification(result)
        assert verification.file_type == FileType.CONFIG
        assert not verification.passed

    def test_docs_keep_no_evidence_still_passes(self):
        """Docs can exist without references (min_evidence_count=0)."""
        result = self._make_result(
            "docs/guide.md", V2Action.KEEP, [],
        )
        verification = verify_classification(result)
        assert verification.file_type == FileType.DOCS
        assert verification.passed

    def test_test_keep_with_target(self):
        result = self._make_result(
            "tests/test_auth.py", V2Action.KEEP,
            ["import from auth module"],
        )
        verification = verify_classification(result)
        assert verification.file_type == FileType.TEST
        assert verification.passed

    def test_binary_keep_with_reference(self):
        result = self._make_result(
            "assets/logo.png", V2Action.KEEP,
            ["reference in index.html"],
        )
        verification = verify_classification(result)
        assert verification.file_type == FileType.BINARY
        assert verification.passed

    def test_investigate_skips_rules(self):
        """Non-KEEP/DELETE actions skip rule enforcement."""
        result = ClassificationResult(
            file_path="src/main.py",
            tier=V2Tier.TIER_1,
            action=V2Action.INVESTIGATE,
            v1_category=V1Category.INVESTIGATE,
            confidence=0.60,
            evidence=[],
        )
        verification = verify_classification(result)
        assert verification.passed  # no rules applied

    def test_all_5_categories_dispatch(self):
        """Each file type category dispatches to different rule sets."""
        paths = {
            FileType.SOURCE: "src/app.py",
            FileType.CONFIG: "config.json",
            FileType.DOCS: "README.md",
            FileType.TEST: "test_app.py",
            FileType.BINARY: "logo.png",
        }
        for file_type, path in paths.items():
            result = self._make_result(
                path, V2Action.KEEP,
                ["reference evidence for testing"],
            )
            verification = verify_classification(result)
            assert verification.file_type == file_type, f"Wrong type for {path}"

    def test_dispatch_log(self):
        """Verification result includes rule dispatch info."""
        result = self._make_result(
            "src/main.py", V2Action.KEEP,
            ["import reference found"],
        )
        verification = verify_classification(result)
        d = verification.to_dict()
        assert "rules_applied" in d
        assert len(d["rules_applied"]) > 0
        assert d["file_type"] == "source"
