"""Tests for decompose_deliverables() -- T01.02 decomposition rule."""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.deliverables import decompose_deliverables
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


class TestDecomposeDeliverables:
    def test_three_behavioral_produce_six(self):
        """3 behavioral deliverables -> 6 output (3 Implement + 3 Verify)."""
        inputs = [
            Deliverable(id="D-1", description="Implement retry logic"),
            Deliverable(id="D-2", description="Replace boolean with int offset"),
            Deliverable(id="D-3", description="Parse configuration from YAML"),
        ]
        result = decompose_deliverables(inputs)
        assert len(result) == 6
        # Check IDs alternate .a / .b
        assert result[0].id == "D-1.a"
        assert result[1].id == "D-1.b"
        assert result[2].id == "D-2.a"
        assert result[3].id == "D-2.b"
        assert result[4].id == "D-3.a"
        assert result[5].id == "D-3.b"
        # Check kinds
        assert all(r.kind == DeliverableKind.IMPLEMENT for r in result[::2])
        assert all(r.kind == DeliverableKind.VERIFY for r in result[1::2])

    def test_two_behavioral_one_doc_produce_five(self):
        """2 behavioral + 1 doc -> 5 output."""
        inputs = [
            Deliverable(id="D-1", description="Implement retry logic"),
            Deliverable(id="D-2", description="Document API endpoints"),
            Deliverable(id="D-3", description="Parse configuration from YAML"),
        ]
        result = decompose_deliverables(inputs)
        assert len(result) == 5
        assert result[0].id == "D-1.a"
        assert result[1].id == "D-1.b"
        assert result[2].id == "D-2"  # doc passes through unchanged
        assert result[3].id == "D-3.a"
        assert result[4].id == "D-3.b"

    def test_empty_input_returns_empty(self):
        assert decompose_deliverables([]) == []

    def test_already_decomposed_not_re_decomposed(self):
        """Deliverables ending in .a or .b are not re-decomposed."""
        inputs = [
            Deliverable(
                id="D-1.a",
                description="Implement retry logic",
                kind=DeliverableKind.IMPLEMENT,
            ),
            Deliverable(
                id="D-1.b",
                description="Verify D-1.a: validate retry logic",
                kind=DeliverableKind.VERIFY,
            ),
        ]
        result = decompose_deliverables(inputs)
        assert len(result) == 2
        assert result[0].id == "D-1.a"
        assert result[1].id == "D-1.b"

    def test_verify_description_references_implement_id(self):
        """Verify deliverable cross-references the Implement deliverable by ID."""
        inputs = [
            Deliverable(id="D-42", description="Compute hash of input"),
        ]
        result = decompose_deliverables(inputs)
        assert len(result) == 2
        verify = result[1]
        assert verify.id == "D-42.b"
        assert "D-42.a" in verify.description

    def test_non_behavioral_passes_through_unchanged(self):
        inputs = [
            Deliverable(id="D-1", description="Document API endpoints"),
        ]
        result = decompose_deliverables(inputs)
        assert len(result) == 1
        assert result[0].id == "D-1"
        assert result[0].description == "Document API endpoints"

    def test_verify_contains_state_assertions(self):
        """Verify descriptions mention internal correctness checks."""
        inputs = [
            Deliverable(id="D-1", description="Implement retry logic"),
        ]
        result = decompose_deliverables(inputs)
        verify = result[1]
        assert "internal correctness" in verify.description
        assert "post-condition assertions" in verify.description

    def test_metadata_preserved_in_decomposition(self):
        inputs = [
            Deliverable(
                id="D-1",
                description="Compute hash",
                metadata={"source": "spec"},
            ),
        ]
        result = decompose_deliverables(inputs)
        assert result[0].metadata == {"source": "spec"}
        assert result[1].metadata == {"source": "spec"}

    def test_idempotent_double_decomposition(self):
        """Running decompose twice produces identical results."""
        inputs = [
            Deliverable(id="D-1", description="Implement retry logic"),
            Deliverable(id="D-2", description="Document API"),
        ]
        first = decompose_deliverables(inputs)
        second = decompose_deliverables(first)
        assert len(first) == len(second)
        for a, b in zip(first, second):
            assert a.id == b.id
            assert a.kind == b.kind
