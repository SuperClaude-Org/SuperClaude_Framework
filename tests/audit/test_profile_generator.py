"""Tests for 8-field profile generator (T03.01 / D-0017)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.profile_generator import (
    FullFileProfile,
    ProfileGenerator,
    compute_complexity,
)
from superclaude.cli.audit.scanner_schema import (
    PHASE2_PROFILE_FIELDS,
    has_full_profile,
    validate_phase2,
)
from superclaude.cli.audit.tool_orchestrator import ToolOrchestrator


# --- Fixtures ---

SAMPLE_PY = """\
import os
from pathlib import Path

def hello():
    if True:
        for x in range(10):
            print(x)
    elif False:
        pass
    else:
        return None

__all__ = ["hello"]
"""

SAMPLE_JS = """\
import React from 'react';
import { useState } from 'react';

export function App() {
    if (true) {
        return <div />;
    }
}

export default App;
"""

SAMPLE_CONFIG = """\
[tool.pytest]
testpaths = ["tests"]
"""


@pytest.fixture
def generator():
    return ProfileGenerator(repo_root="/nonexistent")


@pytest.fixture
def sample_files():
    return {
        "src/main.py": SAMPLE_PY,
        "src/App.jsx": SAMPLE_JS,
        "pyproject.toml": SAMPLE_CONFIG,
    }


@pytest.fixture
def test_files():
    return {
        "src/main.py": SAMPLE_PY,
        "tests/test_main.py": "import pytest\ndef test_hello(): pass\n",
    }


# --- Tests ---

class TestComputeComplexity:
    def test_empty_content(self):
        assert compute_complexity("") == 1.0

    def test_python_branches(self):
        result = compute_complexity(SAMPLE_PY)
        # if, elif, else, for = 4 branches + 1 base
        assert result == 5.0

    def test_js_branches(self):
        result = compute_complexity(SAMPLE_JS)
        # if(true) = 1 branch + 1 base
        assert result == 2.0

    def test_no_branches(self):
        result = compute_complexity("x = 1\ny = 2\n")
        assert result == 1.0


class TestFullFileProfile:
    def test_to_dict_has_all_fields(self, generator: ProfileGenerator):
        profile = generator.profile_file(
            "src/main.py", SAMPLE_PY, all_analyses={}, all_files=[],
        )
        d = profile.to_dict()
        assert "imports" in d
        assert "exports" in d
        assert "size" in d
        assert "complexity" in d
        assert "age" in d
        assert "churn" in d
        assert "coupling" in d
        assert "test_coverage" in d

    def test_to_schema_dict_valid(self, generator: ProfileGenerator):
        profile = generator.profile_file(
            "src/main.py", SAMPLE_PY, all_analyses={}, all_files=[],
        )
        schema = profile.to_schema_dict()
        result = validate_phase2(schema)
        assert result.valid, f"Schema errors: {[e.to_dict() for e in result.errors]}"

    def test_has_full_profile(self, generator: ProfileGenerator):
        profile = generator.profile_file(
            "src/main.py", SAMPLE_PY, all_analyses={}, all_files=[],
        )
        schema = profile.to_schema_dict()
        assert has_full_profile(schema)


class TestProfileGenerator:
    def test_all_8_fields_populated(self, generator: ProfileGenerator, sample_files):
        profiles = generator.profile_batch(sample_files)
        assert len(profiles) == 3

        for p in profiles:
            d = p.to_dict()
            assert d["imports"] is not None
            assert d["exports"] is not None
            assert isinstance(d["size"], int)
            assert isinstance(d["complexity"], float)
            assert isinstance(d["age"], str)
            assert isinstance(d["churn"], int)
            assert isinstance(d["coupling"], float)
            # test_coverage can be None for non-source files

    def test_deterministic_output(self, generator: ProfileGenerator, sample_files):
        """Same file state produces identical profile across runs."""
        profiles_1 = generator.profile_batch(sample_files)
        profiles_2 = generator.profile_batch(sample_files)

        for p1, p2 in zip(profiles_1, profiles_2):
            assert p1.to_dict() == p2.to_dict()

    def test_cache_hit_on_repeat(self, generator: ProfileGenerator, sample_files):
        """Repeated runs leverage cache (cache hit counter > 0)."""
        generator.profile_batch(sample_files)
        # Second run should hit cache
        generator.profile_batch(sample_files)
        stats = generator.orchestrator.cache.stats
        assert stats.hits > 0, "Expected cache hits on repeated profile run"

    def test_imports_extracted(self, generator: ProfileGenerator):
        files = {"src/main.py": SAMPLE_PY}
        profiles = generator.profile_batch(files)
        assert len(profiles[0].imports) > 0

    def test_exports_extracted(self, generator: ProfileGenerator):
        files = {"src/main.py": SAMPLE_PY}
        profiles = generator.profile_batch(files)
        assert len(profiles[0].exports) > 0

    def test_size_matches_line_count(self, generator: ProfileGenerator):
        files = {"src/main.py": SAMPLE_PY}
        profiles = generator.profile_batch(files)
        assert profiles[0].size == len(SAMPLE_PY.splitlines())

    def test_test_coverage_detected(self, generator: ProfileGenerator, test_files):
        profiles = generator.profile_batch(test_files)
        main_profile = [p for p in profiles if p.file_path == "src/main.py"][0]
        assert main_profile.test_coverage == 1.0

    def test_test_coverage_missing(self, generator: ProfileGenerator):
        files = {"src/orphan.py": "x = 1\n"}
        profiles = generator.profile_batch(files)
        assert profiles[0].test_coverage == 0.0

    def test_config_file_coverage_none(self, generator: ProfileGenerator):
        files = {"config.toml": "[tool]\n"}
        profiles = generator.profile_batch(files)
        assert profiles[0].test_coverage is None

    def test_schema_validation(self, generator: ProfileGenerator, sample_files):
        profiles = generator.profile_batch(sample_files)
        results = generator.validate_profiles(profiles)
        for r in results:
            assert r["valid"], f"Schema validation failed: {r['errors']}"
