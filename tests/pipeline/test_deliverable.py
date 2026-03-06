"""Tests for Deliverable and DeliverableKind -- T01.01 schema extension."""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


class TestDeliverableKind:
    def test_all_six_values(self):
        expected = {
            "implement",
            "verify",
            "invariant_check",
            "fmea_test",
            "guard_test",
            "contract_test",
        }
        actual = {k.value for k in DeliverableKind}
        assert actual == expected

    def test_from_str_valid(self):
        for kind in DeliverableKind:
            assert DeliverableKind.from_str(kind.value) is kind

    def test_from_str_unknown_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown deliverable kind.*'bogus'"):
            DeliverableKind.from_str("bogus")

    def test_from_str_empty_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown deliverable kind"):
            DeliverableKind.from_str("")


class TestDeliverable:
    def test_defaults(self):
        d = Deliverable(id="D-0001", description="Implement feature X")
        assert d.kind == DeliverableKind.IMPLEMENT
        assert d.metadata == {}

    def test_metadata_defaults_to_empty_dict(self):
        d = Deliverable(id="D-0001", description="test")
        assert d.metadata == {}
        assert isinstance(d.metadata, dict)

    def test_metadata_not_shared_between_instances(self):
        d1 = Deliverable(id="D-0001", description="a")
        d2 = Deliverable(id="D-0002", description="b")
        d1.metadata["key"] = "value"
        assert d2.metadata == {}

    def test_round_trip_serialization(self):
        original = Deliverable(
            id="D-0001",
            description="Implement feature X",
            kind=DeliverableKind.VERIFY,
            metadata={"invariant": "x > 0", "source": "M2"},
        )
        data = original.to_dict()
        restored = Deliverable.from_dict(data)
        assert restored.id == original.id
        assert restored.description == original.description
        assert restored.kind == original.kind
        assert restored.metadata == original.metadata

    def test_round_trip_preserves_all_kinds(self):
        for kind in DeliverableKind:
            d = Deliverable(id="D-X", description="test", kind=kind)
            restored = Deliverable.from_dict(d.to_dict())
            assert restored.kind == kind

    def test_from_dict_without_kind_defaults_to_implement(self):
        """Pre-extension deliverables (without kind) default to implement."""
        data = {"id": "D-OLD", "description": "Legacy deliverable"}
        d = Deliverable.from_dict(data)
        assert d.kind == DeliverableKind.IMPLEMENT

    def test_from_dict_without_metadata_defaults_to_empty(self):
        data = {"id": "D-OLD", "description": "Legacy", "kind": "verify"}
        d = Deliverable.from_dict(data)
        assert d.metadata == {}

    def test_existing_roadmaps_parse_without_error(self):
        """Simulate parsing multiple pre-extension deliverables."""
        legacy_deliverables = [
            {"id": "D-0001", "description": "Build auth module"},
            {"id": "D-0002", "description": "Document API endpoints"},
            {"id": "D-0003", "description": "Implement retry logic"},
        ]
        results = [Deliverable.from_dict(d) for d in legacy_deliverables]
        assert len(results) == 3
        assert all(d.kind == DeliverableKind.IMPLEMENT for d in results)
        assert all(d.metadata == {} for d in results)

    def test_to_dict_structure(self):
        d = Deliverable(
            id="D-0001",
            description="test",
            kind=DeliverableKind.FMEA_TEST,
            metadata={"risk": "high"},
        )
        data = d.to_dict()
        assert data == {
            "id": "D-0001",
            "description": "test",
            "kind": "fmea_test",
            "metadata": {"risk": "high"},
        }
