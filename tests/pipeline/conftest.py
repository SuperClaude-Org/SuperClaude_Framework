"""Shared fixtures for pipeline tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test output files."""
    return tmp_path


@pytest.fixture
def make_file(tmp_path: Path):
    """Factory fixture to create files with given content."""
    def _make(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p
    return _make
