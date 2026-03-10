"""Tests for dynamic-import-safe classification (T03.10 / D-0026)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
)
from superclaude.cli.audit.dynamic_imports import (
    classify_with_dynamic_safety,
    detect_dynamic_imports,
    scan_for_dynamic_imports,
)


JS_DYNAMIC = """\
const mod = 'myModule';
const loaded = import(mod);
"""

JS_REQUIRE_VAR = """\
const name = getModuleName();
const m = require(name);
"""

PY_IMPORT_BUILTIN = """\
module_name = "os"
mod = __import__(module_name)
"""

PY_IMPORTLIB = """\
import importlib
mod = importlib.import_module("my_module")
"""

STATIC_ONLY = """\
import os
from pathlib import Path
"""


class TestScanForDynamicImports:
    def test_js_dynamic_import(self):
        detections = scan_for_dynamic_imports("loader.js", JS_DYNAMIC)
        assert len(detections) > 0
        assert detections[0].pattern_name == "js_dynamic_import"

    def test_js_require_variable(self):
        detections = scan_for_dynamic_imports("loader.js", JS_REQUIRE_VAR)
        assert len(detections) > 0
        assert detections[0].pattern_name == "js_require_variable"

    def test_py_import_builtin(self):
        detections = scan_for_dynamic_imports("loader.py", PY_IMPORT_BUILTIN)
        assert len(detections) > 0
        assert detections[0].pattern_name == "py_import_builtin"

    def test_py_importlib(self):
        detections = scan_for_dynamic_imports("loader.py", PY_IMPORTLIB)
        assert len(detections) > 0
        assert detections[0].pattern_name == "py_importlib"

    def test_static_import_no_detection(self):
        detections = scan_for_dynamic_imports("main.py", STATIC_ONLY)
        assert len(detections) == 0

    def test_covers_js_and_python(self):
        """Dynamic import patterns cover JS and Python."""
        js_det = scan_for_dynamic_imports("x.js", JS_DYNAMIC)
        py_det = scan_for_dynamic_imports("x.py", PY_IMPORTLIB)
        assert len(js_det) > 0
        assert len(py_det) > 0


class TestDetectDynamicImports:
    def test_detects_across_files(self):
        files = {
            "loader.js": JS_DYNAMIC,
            "main.py": STATIC_ONLY,
            "plugin.py": PY_IMPORTLIB,
        }
        report = detect_dynamic_imports(files)
        assert "loader.js" in report.files_with_dynamic_imports
        assert "plugin.py" in report.files_with_dynamic_imports
        assert "main.py" not in report.files_with_dynamic_imports

    def test_report_serializable(self):
        files = {"loader.js": JS_DYNAMIC}
        report = detect_dynamic_imports(files)
        d = report.to_dict()
        assert "detections" in d
        assert "detection_count" in d


class TestClassifyWithDynamicSafety:
    def _make_delete(self, path):
        return ClassificationResult(
            file_path=path,
            tier=V2Tier.TIER_1,
            action=V2Action.DELETE,
            v1_category=V1Category.DELETE,
            confidence=0.90,
            evidence=["zero references found"],
        )

    def _make_keep(self, path):
        return ClassificationResult(
            file_path=path,
            tier=V2Tier.TIER_2,
            action=V2Action.KEEP,
            v1_category=V1Category.KEEP,
            confidence=0.85,
            evidence=["reference found"],
        )

    def test_dynamic_import_file_not_deleted(self):
        """Files with dynamic imports must not be classified DELETE."""
        classifications = [self._make_delete("loader.js")]
        files = {"loader.js": JS_DYNAMIC}
        result = classify_with_dynamic_safety(classifications, files)
        assert result[0].action == V2Action.KEEP
        assert "monitor" in result[0].qualifiers

    def test_static_file_can_be_deleted(self):
        """Files without dynamic imports retain original classification."""
        classifications = [self._make_delete("static.py")]
        files = {"static.py": STATIC_ONLY}
        result = classify_with_dynamic_safety(classifications, files)
        assert result[0].action == V2Action.DELETE

    def test_no_dynamic_import_in_delete_candidates(self):
        """Scan output and verify no dynamic-import file appears as DELETE."""
        classifications = [
            self._make_delete("loader.js"),
            self._make_delete("static.py"),
            self._make_keep("utils.py"),
        ]
        files = {
            "loader.js": JS_DYNAMIC,
            "static.py": STATIC_ONLY,
            "utils.py": "import os\n",
        }
        result = classify_with_dynamic_safety(classifications, files)
        deletes = [r for r in result if r.action == V2Action.DELETE]
        for d in deletes:
            assert d.file_path != "loader.js"

    def test_keep_monitor_qualifier(self):
        classifications = [self._make_delete("plugin.py")]
        files = {"plugin.py": PY_IMPORTLIB}
        result = classify_with_dynamic_safety(classifications, files)
        assert "monitor" in result[0].qualifiers
        assert "dynamic_import" in result[0].qualifiers
