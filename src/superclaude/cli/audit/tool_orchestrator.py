"""Static-tool orchestration layer with result caching.

Implements AC12 (supporting): static-tool results as evidence inputs.
Orchestrates grep/AST/file-stat invocations per batch with content-hash
caching to prevent redundant invocations.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class FileAnalysis:
    """Static analysis results for a single file."""

    file_path: str
    content_hash: str
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "imports": self.imports,
            "exports": self.exports,
            "references": self.references,
            "metadata": self.metadata,
        }


@dataclass
class CacheStats:
    """Cache hit/miss statistics."""

    hits: int = 0
    misses: int = 0

    @property
    def total(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        return self.hits / self.total if self.total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": self.total,
            "hit_rate": round(self.hit_rate, 4),
        }


class ResultCache:
    """Content-hash keyed cache for static analysis results.

    Stores results keyed by content hash. On cache hit, skips
    re-invocation. Invalidates when content changes (different hash).
    """

    def __init__(self) -> None:
        self._store: dict[str, FileAnalysis] = {}
        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        return self._stats

    def get(self, content_hash: str) -> FileAnalysis | None:
        result = self._store.get(content_hash)
        if result is not None:
            self._stats.hits += 1
        else:
            self._stats.misses += 1
        return result

    def put(self, content_hash: str, result: FileAnalysis) -> None:
        self._store[content_hash] = result

    def contains(self, content_hash: str) -> bool:
        return content_hash in self._store

    def clear(self) -> None:
        self._store.clear()
        self._stats = CacheStats()

    @property
    def size(self) -> int:
        return len(self._store)


def compute_content_hash(content: str) -> str:
    """Compute a SHA-256 hash of file content for cache keying."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# Type for analysis tool functions
AnalysisTool = Callable[[str, str], FileAnalysis]


def _default_analyzer(file_path: str, content: str) -> FileAnalysis:
    """Default static analyzer: extracts basic import/export patterns.

    This is a simple line-based scanner. In production, AST-based
    analysis would be plugged in via the tool parameter.
    """
    lines = content.splitlines()
    imports: list[str] = []
    exports: list[str] = []

    for line in lines:
        stripped = line.strip()
        # Python imports
        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(stripped)
        # JS/TS imports
        elif stripped.startswith("import "):
            imports.append(stripped)
        # Python __all__
        elif "__all__" in stripped:
            exports.append(stripped)
        # JS/TS exports
        elif stripped.startswith("export "):
            exports.append(stripped)

    return FileAnalysis(
        file_path=file_path,
        content_hash=compute_content_hash(content),
        imports=imports,
        exports=exports,
        references=[],
        metadata={
            "line_count": len(lines),
            "size_bytes": len(content),
        },
    )


class ToolOrchestrator:
    """Orchestrates static analysis tools per batch with caching.

    Dispatches analysis for each file, using cached results when
    content hasn't changed. Tracks cache statistics.
    """

    def __init__(
        self,
        analyzer: AnalysisTool | None = None,
        cache: ResultCache | None = None,
    ) -> None:
        self._analyzer = analyzer or _default_analyzer
        self._cache = cache or ResultCache()

    @property
    def cache(self) -> ResultCache:
        return self._cache

    def analyze_file(self, file_path: str, content: str) -> FileAnalysis:
        """Analyze a single file, using cache when possible."""
        content_hash = compute_content_hash(content)

        cached = self._cache.get(content_hash)
        if cached is not None:
            return cached

        result = self._analyzer(file_path, content)
        self._cache.put(content_hash, result)
        return result

    def analyze_batch(
        self,
        files: dict[str, str],
    ) -> list[FileAnalysis]:
        """Analyze a batch of files (path -> content mapping).

        Returns list of FileAnalysis results. Uses cache for unchanged files.
        """
        results = []
        for file_path, content in files.items():
            result = self.analyze_file(file_path, content)
            results.append(result)
        return results

    def get_cache_stats(self) -> CacheStats:
        return self._cache.stats
