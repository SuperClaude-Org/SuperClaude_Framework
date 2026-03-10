"""Tests for static-tool orchestration with caching (T02.03, D-0013)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.tool_orchestrator import (
    CacheStats,
    FileAnalysis,
    ResultCache,
    ToolOrchestrator,
    compute_content_hash,
)


class TestContentHash:
    """Content hash computation."""

    def test_deterministic(self):
        h1 = compute_content_hash("hello world")
        h2 = compute_content_hash("hello world")
        assert h1 == h2

    def test_different_content_different_hash(self):
        h1 = compute_content_hash("hello")
        h2 = compute_content_hash("world")
        assert h1 != h2

    def test_returns_hex_string(self):
        h = compute_content_hash("test")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex


class TestResultCache:
    """Cache stores and retrieves by content hash."""

    def test_miss_returns_none(self):
        cache = ResultCache()
        assert cache.get("nonexistent") is None

    def test_put_and_get(self):
        cache = ResultCache()
        result = FileAnalysis(file_path="a.py", content_hash="abc123")
        cache.put("abc123", result)
        assert cache.get("abc123") is result

    def test_hit_miss_stats(self):
        cache = ResultCache()
        result = FileAnalysis(file_path="a.py", content_hash="abc")
        cache.put("abc", result)

        cache.get("abc")   # hit
        cache.get("xyz")   # miss

        assert cache.stats.hits == 1
        assert cache.stats.misses == 1
        assert cache.stats.hit_rate == 0.5

    def test_contains(self):
        cache = ResultCache()
        cache.put("k", FileAnalysis(file_path="f", content_hash="k"))
        assert cache.contains("k")
        assert not cache.contains("missing")

    def test_clear(self):
        cache = ResultCache()
        cache.put("k", FileAnalysis(file_path="f", content_hash="k"))
        cache.clear()
        assert cache.size == 0
        assert cache.stats.hits == 0

    def test_stats_serialization(self):
        stats = CacheStats(hits=3, misses=1)
        d = stats.to_dict()
        assert d["hits"] == 3
        assert d["misses"] == 1
        assert d["total"] == 4
        assert d["hit_rate"] == 0.75


class TestToolOrchestrator:
    """Orchestrator dispatches analysis with caching."""

    def test_analyze_file_caches_result(self):
        orch = ToolOrchestrator()
        content = "import os\nprint('hello')"
        r1 = orch.analyze_file("main.py", content)
        r2 = orch.analyze_file("main.py", content)

        # Second call should hit cache
        assert orch.cache.stats.hits == 1
        assert orch.cache.stats.misses == 1

    def test_cache_invalidation_on_change(self):
        """AC: cache invalidation when file content changes."""
        orch = ToolOrchestrator()
        orch.analyze_file("main.py", "import os")
        orch.analyze_file("main.py", "import sys")  # different content

        # Both should be misses (different hashes)
        assert orch.cache.stats.misses == 2
        assert orch.cache.stats.hits == 0

    def test_second_run_100_percent_cache_hits(self):
        """AC: repeated runs with unchanged files show cache hits."""
        orch = ToolOrchestrator()
        files = {
            "a.py": "import os",
            "b.py": "import sys",
            "c.py": "x = 1",
        }

        # First run: all misses
        orch.analyze_batch(files)
        assert orch.cache.stats.misses == 3
        assert orch.cache.stats.hits == 0

        # Second run: all hits
        orch.analyze_batch(files)
        assert orch.cache.stats.hits == 3
        assert orch.cache.stats.hit_rate == 0.5  # 3 hits / 6 total

    def test_analyze_batch_returns_results(self):
        orch = ToolOrchestrator()
        files = {"a.py": "import os", "b.py": "x = 1"}
        results = orch.analyze_batch(files)
        assert len(results) == 2
        assert all(isinstance(r, FileAnalysis) for r in results)

    def test_file_analysis_schema(self):
        """AC: structured results per file match expected schema."""
        orch = ToolOrchestrator()
        result = orch.analyze_file("main.py", "import os\nimport sys")
        d = result.to_dict()
        assert "file_path" in d
        assert "content_hash" in d
        assert "imports" in d
        assert "exports" in d
        assert "references" in d
        assert "metadata" in d

    def test_imports_extracted(self):
        orch = ToolOrchestrator()
        result = orch.analyze_file("main.py", "import os\nfrom pathlib import Path")
        assert len(result.imports) == 2

    def test_custom_analyzer(self):
        def custom(fp: str, content: str) -> FileAnalysis:
            return FileAnalysis(
                file_path=fp,
                content_hash=compute_content_hash(content),
                imports=[],
                exports=[],
                references=["custom"],
                metadata={"custom": True},
            )

        orch = ToolOrchestrator(analyzer=custom)
        result = orch.analyze_file("x.py", "hello")
        assert result.references == ["custom"]
