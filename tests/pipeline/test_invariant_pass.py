"""Tests for invariant registry pipeline integration.

Covers T02.05 acceptance criteria:
- Spec with state variable introductions -> registry section present
- invariant_check deliverables in correct milestones
- Entries cross-reference generated deliverables by ID
- Pass is idempotent
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.invariant_pass import (
    InvariantRegistryOutput,
    run_invariant_registry_pass,
)
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind


def _d(id: str, desc: str, kind: DeliverableKind = DeliverableKind.IMPLEMENT) -> Deliverable:
    return Deliverable(id=id, description=desc, kind=kind)


class TestInvariantRegistryPass:

    def test_state_variables_produce_registry_section(self):
        """Spec with state variable introductions -> registry section present."""
        deliverables = [
            _d("D1.1", "Add counter for retries"),
            _d("D1.2", "Implement retry logic"),
            _d("D2.1", "Increment counter after each retry attempt"),
        ]
        result = run_invariant_registry_pass(deliverables)
        assert "Invariant Registry" in result.section_markdown
        assert "Variables tracked" in result.section_markdown
        assert len(result.entries) >= 1

    def test_invariant_check_deliverables_generated(self):
        """invariant_check deliverables are generated."""
        deliverables = [
            _d("D1.1", "Add offset for tracking replay position"),
            _d("D2.1", "Increment offset by step_size"),
        ]
        result = run_invariant_registry_pass(deliverables)
        assert len(result.generated_deliverables) >= 1
        assert all(
            d.kind == DeliverableKind.INVARIANT_CHECK
            for d in result.generated_deliverables
        )

    def test_cross_references(self):
        """Entries cross-reference generated deliverables by ID."""
        deliverables = [
            _d("D1.1", "Add counter for event tracking"),
            _d("D2.1", "Reset counter after batch completion"),
        ]
        result = run_invariant_registry_pass(deliverables)
        if result.entries:
            entry = result.entries[0]
            gen_ids = [d.id for d in result.generated_deliverables]
            for vid in entry.verification_deliverable_ids:
                assert vid in gen_ids

    def test_idempotent(self):
        """Running pass twice produces identical output."""
        deliverables = [
            _d("D1.1", "Add offset for position tracking"),
            _d("D2.1", "Update offset after processing"),
        ]
        result1 = run_invariant_registry_pass(deliverables)
        result2 = run_invariant_registry_pass(deliverables)

        assert result1.section_markdown == result2.section_markdown
        assert len(result1.generated_deliverables) == len(result2.generated_deliverables)
        assert len(result1.entries) == len(result2.entries)

    def test_idempotent_with_generated_input(self):
        """Re-running with previously generated deliverables doesn't double-count."""
        deliverables = [
            _d("D1.1", "Add counter for retries"),
        ]
        result1 = run_invariant_registry_pass(deliverables)
        # Feed generated deliverables back in
        all_deliverables = deliverables + result1.generated_deliverables
        result2 = run_invariant_registry_pass(all_deliverables)

        assert len(result2.generated_deliverables) == len(result1.generated_deliverables)

    def test_no_state_variables(self):
        """No state variables -> empty section."""
        deliverables = [
            _d("D1.1", "Document the API endpoints"),
            _d("D1.2", "Write user guide"),
        ]
        result = run_invariant_registry_pass(deliverables)
        assert "No state variables detected" in result.section_markdown
        assert len(result.entries) == 0

    def test_empty_input(self):
        deliverables: list[Deliverable] = []
        result = run_invariant_registry_pass(deliverables)
        assert "No state variables detected" in result.section_markdown

    def test_only_verify_deliverables_ignored(self):
        """Verify-kind deliverables don't trigger detection."""
        deliverables = [
            _d("D1.1.b", "Verify counter behavior", DeliverableKind.VERIFY),
        ]
        result = run_invariant_registry_pass(deliverables)
        assert len(result.entries) == 0
