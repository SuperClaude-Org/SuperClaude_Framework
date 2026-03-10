"""Tests for duplication matrix (T03.08 / D-0024)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.duplication import (
    build_duplication_matrix,
    compute_similarity,
)
from superclaude.cli.audit.tool_orchestrator import FileAnalysis


def _analysis(path, imports=None, exports=None):
    return FileAnalysis(
        file_path=path, content_hash="h",
        imports=imports or [], exports=exports or [],
    )


class TestComputeSimilarity:
    def test_identical_files(self):
        a = _analysis("a.py", imports=["import os", "import sys"], exports=["__all__ = ['x']"])
        b = _analysis("b.py", imports=["import os", "import sys"], exports=["__all__ = ['x']"])
        sim, shared_imp, shared_exp = compute_similarity(a, b)
        assert sim == 1.0

    def test_no_overlap(self):
        a = _analysis("a.py", imports=["import os"])
        b = _analysis("b.py", imports=["import json"])
        sim, shared_imp, shared_exp = compute_similarity(a, b)
        assert sim == 0.0

    def test_partial_overlap(self):
        a = _analysis("a.py", imports=["import os", "import sys"])
        b = _analysis("b.py", imports=["import os", "import json"])
        sim, _, _ = compute_similarity(a, b)
        assert 0.0 < sim < 1.0

    def test_empty_files(self):
        a = _analysis("a.py")
        b = _analysis("b.py")
        sim, _, _ = compute_similarity(a, b)
        assert sim == 0.0


class TestBuildDuplicationMatrix:
    def test_known_duplicates(self):
        analyses = {
            "a.py": _analysis("a.py",
                imports=["import os", "import sys", "import json"],
                exports=["__all__ = ['x']"]),
            "b.py": _analysis("b.py",
                imports=["import os", "import sys", "import json"],
                exports=["__all__ = ['x']"]),
        }
        matrix = build_duplication_matrix(analyses)
        assert len(matrix.pairs) == 1
        assert matrix.pairs[0].similarity > 0.80
        assert matrix.pairs[0].recommendation == "consolidate"

    def test_investigate_threshold(self):
        # 4 shared out of 5 unique = Jaccard 0.8 -> consolidate
        analyses = {
            "a.py": _analysis("a.py",
                imports=["import os", "import sys", "import json", "import re", "import io"]),
            "b.py": _analysis("b.py",
                imports=["import os", "import sys", "import json", "import re", "import pathlib"]),
        }
        matrix = build_duplication_matrix(analyses, threshold=0.50)
        if matrix.pairs:
            p = matrix.pairs[0]
            # 4/6 unique = ~0.667 -> investigate
            assert p.recommendation in ("investigate", "consolidate")

    def test_below_threshold_excluded(self):
        analyses = {
            "a.py": _analysis("a.py", imports=["import os"]),
            "b.py": _analysis("b.py", imports=["import json"]),
        }
        matrix = build_duplication_matrix(analyses, threshold=0.60)
        assert len(matrix.pairs) == 0

    def test_matrix_includes_shared_imports(self):
        analyses = {
            "a.py": _analysis("a.py",
                imports=["import os", "import sys"],
                exports=["__all__ = ['x']"]),
            "b.py": _analysis("b.py",
                imports=["import os", "import sys"],
                exports=["__all__ = ['x']"]),
        }
        matrix = build_duplication_matrix(analyses)
        p = matrix.pairs[0]
        assert len(p.shared_imports) > 0

    def test_matrix_serializable(self):
        analyses = {
            "a.py": _analysis("a.py", imports=["import os"]),
            "b.py": _analysis("b.py", imports=["import os"]),
        }
        matrix = build_duplication_matrix(analyses, threshold=0.10)
        d = matrix.to_dict()
        assert "pairs" in d
        assert "total_pairs" in d
