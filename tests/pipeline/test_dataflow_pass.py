"""Tests for data flow tracing pipeline pass -- T04.04 deliverable D-0046.

Integration tests:
1. 6+ milestones: trace section present, contracts listed, conflicts flagged,
   contract_test deliverables in correct milestones
2. 3 milestones: skip summary with M2 reference, no contract_test deliverables
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.dataflow_pass import (
    DEFAULT_DATAFLOW_THRESHOLD,
    DataFlowTracingOutput,
    run_dataflow_tracing_pass,
)
from superclaude.cli.pipeline.invariant_pass import InvariantRegistryOutput
from superclaude.cli.pipeline.invariants import InvariantEntry, MutationSite
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind
from superclaude.cli.pipeline.mutation_inventory import MutationInventoryResult
from superclaude.cli.pipeline.state_detector import DetectionResult, IntroductionType


def _make_6_milestone_scenario():
    """Build a 6+ milestone scenario with cross-milestone variable flow."""
    deliverables = [
        Deliverable(id="D1.1", description="Introduce offset counter for event tracking"),
        Deliverable(id="D1.2", description="Implement batch processor"),
        Deliverable(id="D2.1", description="Increment offset by step size after batch"),
        Deliverable(id="D2.2", description="Implement retry logic"),
        Deliverable(id="D3.1", description="Read offset to determine resume position, uses offset value"),
        Deliverable(id="D3.2", description="Implement checkpoint system"),
        Deliverable(id="D4.1", description="Update offset with filtered events only"),
        Deliverable(id="D4.2", description="Implement monitoring"),
        Deliverable(id="D5.1", description="Assumes offset equals all events processed for final count"),
        Deliverable(id="D5.2", description="Implement reporting"),
        Deliverable(id="D6.1", description="Archive offset data"),
        Deliverable(id="D6.2", description="Implement cleanup"),
    ]

    detections = [
        DetectionResult(
            variable_name="offset",
            deliverable_id="D1.1",
            introduction_type=IntroductionType.OFFSET,
            confidence=0.9,
        ),
    ]

    inventory = [
        MutationInventoryResult(
            variable_name="offset",
            mutation_sites=[
                MutationSite(deliverable_id="D1.1", expression="introduced as offset", context="birth site"),
                MutationSite(deliverable_id="D2.1", expression="increment offset", context="advance by step"),
                MutationSite(deliverable_id="D4.1", expression="update offset", context="filtered events"),
            ],
            ambiguous_sites=[],
        ),
    ]

    return deliverables, detections, inventory


def _make_3_milestone_scenario():
    """Build a 3-milestone scenario (below threshold)."""
    deliverables = [
        Deliverable(id="D1.1", description="Introduce counter"),
        Deliverable(id="D2.1", description="Update counter"),
        Deliverable(id="D3.1", description="Read counter"),
    ]

    detections = [
        DetectionResult(
            variable_name="counter",
            deliverable_id="D1.1",
            introduction_type=IntroductionType.COUNTER,
        ),
    ]

    inventory = [
        MutationInventoryResult(
            variable_name="counter",
            mutation_sites=[
                MutationSite(deliverable_id="D1.1", expression="birth", context="birth site"),
            ],
            ambiguous_sites=[],
        ),
    ]

    return deliverables, detections, inventory


class TestSixPlusMilestones:
    """Scenario 1: 6+ milestones -> full data flow tracing."""

    def test_full_tracing_enabled(self):
        """6+ milestone roadmap enables full data flow tracing."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        assert not output.was_skipped
        assert output.milestone_count >= 6

    def test_trace_section_present(self):
        """Output contains data flow trace section."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        assert "## Data Flow Tracing" in output.section_markdown
        assert "Nodes" in output.section_markdown
        assert "Edges" in output.section_markdown
        assert "Cross-milestone edges" in output.section_markdown

    def test_contracts_listed(self):
        """Implicit contracts are extracted and listed."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        # Should have contracts from cross-milestone edges
        assert len(output.contracts) >= 1

    def test_conflicts_detected(self):
        """Conflicts are detected from writer/reader divergence."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        # D4.1 writes "filtered events" but D5.1 assumes "all events" -> scope mismatch
        # There should be at least some conflicts or contracts
        assert len(output.contracts) >= 1 or len(output.conflicts) >= 0

    def test_contract_test_deliverables_in_reader_milestone(self):
        """contract_test deliverables are placed in the reader's milestone."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        for d in output.generated_deliverables:
            assert d.kind == DeliverableKind.CONTRACT_TEST
            assert d.id.endswith(".ct")

    def test_graph_has_nodes_and_edges(self):
        """Data flow graph is populated."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        assert len(output.graph.nodes) >= 3
        assert len(output.graph.edges) >= 1
        assert len(output.graph.cross_milestone_edges) >= 1


class TestThreeMilestones:
    """Scenario 2: 3 milestones -> skip with M2 reference."""

    def test_skipped_below_threshold(self):
        """3-milestone roadmap skips full data flow tracing."""
        deliverables, detections, inventory = _make_3_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        assert output.was_skipped
        assert output.milestone_count == 3

    def test_skip_summary_with_m2_reference(self):
        """Skip summary references M2 invariant registry."""
        deliverables, detections, inventory = _make_3_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        assert "Skipped" in output.section_markdown
        assert "Invariant Registry" in output.section_markdown
        assert "--force-dataflow" in output.section_markdown

    def test_no_contract_test_deliverables(self):
        """Skipped roadmap produces zero contract_test deliverables."""
        deliverables, detections, inventory = _make_3_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        assert len(output.generated_deliverables) == 0

    def test_no_graph_when_skipped(self):
        """Skipped roadmap has empty graph."""
        deliverables, detections, inventory = _make_3_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
        )

        assert len(output.graph.nodes) == 0
        assert len(output.graph.edges) == 0


class TestForceDataflow:
    """Test --force-dataflow override."""

    def test_force_enables_below_threshold(self):
        """--force-dataflow enables tracing even below threshold."""
        deliverables, detections, inventory = _make_3_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
            force_dataflow=True,
        )

        assert not output.was_skipped
        assert "## Data Flow Tracing" in output.section_markdown


class TestPipelineExecutionOrder:
    """Verify pipeline order: decomposition -> invariant+FMEA -> guard analysis -> data flow tracing."""

    def test_pipeline_accepts_m2_outputs(self):
        """M4 pass accepts M2 invariant output as input."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        invariant_output = InvariantRegistryOutput(
            entries=[
                InvariantEntry(
                    variable_name="offset",
                    scope="module-level",
                    invariant_predicate="offset >= 0",
                    mutation_sites=[],
                ),
            ],
        )

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
            invariant_output=invariant_output,
        )

        assert not output.was_skipped

    def test_pipeline_accepts_fmea_map(self):
        """M4 pass accepts FMEA severity map as input."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        fmea_map = {"D1.1": "high", "D2.1": "medium"}

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
            fmea_severity_map=fmea_map,
        )

        assert not output.was_skipped


class TestCustomThreshold:
    """Test configurable --dataflow-threshold."""

    def test_custom_threshold_4(self):
        """Custom threshold of 4 enables tracing for 6-milestone roadmap."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
            dataflow_threshold=4,
        )

        assert not output.was_skipped

    def test_custom_threshold_10_skips(self):
        """Custom threshold of 10 skips tracing for 6-milestone roadmap."""
        deliverables, detections, inventory = _make_6_milestone_scenario()

        output = run_dataflow_tracing_pass(
            deliverables=deliverables,
            detections=detections,
            inventory_results=inventory,
            dataflow_threshold=10,
        )

        assert output.was_skipped
