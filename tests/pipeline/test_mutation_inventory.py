"""Tests for mutation inventory generator.

Covers T02.03 acceptance criteria:
- Variable introduced in D2.3 and mutated in D3.1 and D4.2 -> 3 mutation sites
- No mutations beyond birth -> 1 site
- Mutation sites include deliverable ID
- Ambiguous mutations flagged rather than dropped
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.models import Deliverable, DeliverableKind
from superclaude.cli.pipeline.mutation_inventory import (
    MutationInventoryResult,
    generate_mutation_inventory,
)
from superclaude.cli.pipeline.state_detector import DetectionResult, IntroductionType


def _d(id: str, desc: str) -> Deliverable:
    return Deliverable(id=id, description=desc, kind=DeliverableKind.IMPLEMENT)


def _det(var: str, did: str, itype: IntroductionType = IntroductionType.OFFSET) -> DetectionResult:
    return DetectionResult(variable_name=var, deliverable_id=did, introduction_type=itype)


class TestMutationInventory:
    """Four-scenario test suite per tasklist spec."""

    def test_cross_deliverable_mutations(self):
        """Variable introduced in D2.3, mutated in D3.1 and D4.2 -> 3 sites."""
        detections = [_det("offset", "D2.3")]
        deliverables = [
            _d("D2.3", "Introduce offset for tracking position"),
            _d("D3.1", "Increment offset by step_size after processing"),
            _d("D4.2", "Reset offset to zero when replay completes"),
        ]
        results = generate_mutation_inventory(detections, deliverables)
        assert len(results) == 1
        r = results[0]
        assert len(r.mutation_sites) == 3
        ids = [ms.deliverable_id for ms in r.mutation_sites]
        assert "D2.3" in ids  # birth site
        assert "D3.1" in ids  # increment
        assert "D4.2" in ids  # reset

    def test_no_mutations_beyond_birth(self):
        """No mutations beyond birth -> 1 site (birth only)."""
        detections = [_det("counter", "D1.1")]
        deliverables = [
            _d("D1.1", "Add counter for retries"),
            _d("D2.1", "Log the results to file"),  # no counter reference
            _d("D3.1", "Update documentation"),       # no counter mutation
        ]
        results = generate_mutation_inventory(detections, deliverables)
        assert len(results) == 1
        assert len(results[0].mutation_sites) == 1
        assert results[0].mutation_sites[0].context == "birth site"

    def test_mutation_sites_include_deliverable_id(self):
        """Each MutationSite carries the deliverable_id."""
        detections = [_det("offset", "D1.0")]
        deliverables = [
            _d("D1.0", "Create offset tracker"),
            _d("D2.0", "Update offset after each batch"),
        ]
        results = generate_mutation_inventory(detections, deliverables)
        for ms in results[0].mutation_sites:
            assert ms.deliverable_id in ("D1.0", "D2.0")

    def test_ambiguous_mutations_flagged(self):
        """Ambiguous mutations flagged rather than silently dropped."""
        detections = [_det("offset", "D1.0")]
        deliverables = [
            _d("D1.0", "Create offset tracker"),
            _d("D3.0", "Adjust offset based on user preference"),
        ]
        results = generate_mutation_inventory(detections, deliverables)
        assert len(results[0].ambiguous_sites) >= 1
        assert results[0].ambiguous_sites[0].deliverable_id == "D3.0"


class TestEdgeCases:

    def test_empty_detections(self):
        results = generate_mutation_inventory([], [_d("D1", "something")])
        assert results == []

    def test_empty_deliverables(self):
        detections = [_det("x", "D1")]
        results = generate_mutation_inventory(detections, [])
        assert len(results) == 1
        # Only birth site
        assert len(results[0].mutation_sites) == 1

    def test_multiple_variables(self):
        detections = [_det("offset", "D1"), _det("counter", "D2")]
        deliverables = [
            _d("D1", "Create offset"),
            _d("D2", "Add counter"),
            _d("D3", "Increment offset and reset counter"),
        ]
        results = generate_mutation_inventory(detections, deliverables)
        assert len(results) == 2
        # offset: birth + D3
        offset_r = [r for r in results if r.variable_name == "offset"][0]
        assert len(offset_r.mutation_sites) >= 2
        # counter: birth + D3
        counter_r = [r for r in results if r.variable_name == "counter"][0]
        assert len(counter_r.mutation_sites) >= 2
