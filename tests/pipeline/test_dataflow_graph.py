"""Tests for data flow graph builder -- T04.01 deliverable D-0040.

Five-scenario test suite:
1. M1.D1->M2.D3->M3.D1 chain -> 3-node + 2 cross-milestone edges
2. Same-deliverable birth+read -> 2-node + no cross-milestone
3. Read before birth -> error
4. Dead write -> warning
5. Empty deliverable list -> empty graph
"""

from __future__ import annotations

import warnings

import pytest

from superclaude.cli.pipeline.dataflow_graph import (
    DataFlowEdge,
    DataFlowGraph,
    DataFlowNode,
    NodeOperation,
    build_dataflow_graph,
)
from superclaude.cli.pipeline.models import Deliverable, DeliverableKind
from superclaude.cli.pipeline.mutation_inventory import MutationInventoryResult
from superclaude.cli.pipeline.invariants import MutationSite
from superclaude.cli.pipeline.state_detector import DetectionResult, IntroductionType


class TestCrossMilestoneChain:
    """Scenario 1: M1.D1->M2.D3->M3.D1 chain produces 3-node graph with 2 cross-milestone edges."""

    def test_three_milestone_chain(self):
        """Variable born in M1.D1, written in M2.D3, read in M3.D1."""
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
                    MutationSite(deliverable_id="D2.3", expression="increment offset", context="advance offset by step"),
                ],
                ambiguous_sites=[],
            ),
        ]

        deliverables = [
            Deliverable(id="D1.1", description="Introduce offset counter for event tracking"),
            Deliverable(id="D2.3", description="Increment offset by step size after batch processing"),
            Deliverable(id="D3.1", description="Read offset to determine resume position, uses offset value"),
        ]

        graph = build_dataflow_graph(detections, inventory, deliverables)

        # Should have 3 nodes: birth(D1.1), write(D2.3), read(D3.1)
        assert len(graph.nodes) == 3

        # Node operations
        ops = {(n.deliverable_id, n.operation) for n in graph.nodes}
        assert ("D1.1", NodeOperation.BIRTH) in ops
        assert ("D2.3", NodeOperation.WRITE) in ops
        assert ("D3.1", NodeOperation.READ) in ops

        # 2 edges: birth->read and write->read
        assert len(graph.edges) == 2

        # Both should be cross-milestone
        cross = graph.cross_milestone_edges
        assert len(cross) == 2

        for edge in cross:
            assert edge.is_cross_milestone
            assert edge.source_milestone != edge.target_milestone


class TestSameDeliverableBirthRead:
    """Scenario 2: Same-deliverable birth+read -> 2-node + no cross-milestone."""

    def test_same_deliverable_no_cross_milestone(self):
        """Birth and read in same milestone produce no cross-milestone edges."""
        detections = [
            DetectionResult(
                variable_name="flag",
                deliverable_id="D1.1",
                introduction_type=IntroductionType.FLAG,
                confidence=0.9,
            ),
        ]

        inventory = [
            MutationInventoryResult(
                variable_name="flag",
                mutation_sites=[
                    MutationSite(deliverable_id="D1.1", expression="introduced as flag", context="birth site"),
                ],
                ambiguous_sites=[],
            ),
        ]

        deliverables = [
            Deliverable(id="D1.1", description="Introduce flag for tracking state"),
            Deliverable(id="D1.2", description="Read flag to check if processing is complete, uses flag"),
        ]

        graph = build_dataflow_graph(detections, inventory, deliverables)

        # 2 nodes: birth(D1.1), read(D1.2)
        assert len(graph.nodes) == 2

        # 1 edge: birth->read
        assert len(graph.edges) == 1

        # No cross-milestone edges (both in M1)
        cross = graph.cross_milestone_edges
        assert len(cross) == 0


class TestReadBeforeBirth:
    """Scenario 3: Read before birth produces error."""

    def test_read_before_birth_raises(self):
        """Read in a deliverable ordered before birth should raise ValueError."""
        detections = [
            DetectionResult(
                variable_name="cursor",
                deliverable_id="D2.1",
                introduction_type=IntroductionType.CURSOR,
                confidence=0.9,
            ),
        ]

        inventory = [
            MutationInventoryResult(
                variable_name="cursor",
                mutation_sites=[
                    MutationSite(deliverable_id="D2.1", expression="introduced as cursor", context="birth site"),
                ],
                ambiguous_sites=[],
            ),
        ]

        # D1.1 reads cursor BEFORE D2.1 births it (ordering by list position)
        deliverables = [
            Deliverable(id="D1.1", description="Read cursor to determine position, uses cursor value"),
            Deliverable(id="D2.1", description="Introduce cursor for pagination tracking"),
        ]

        with pytest.raises(ValueError, match="Read-before-birth"):
            build_dataflow_graph(detections, inventory, deliverables)


class TestDeadWrite:
    """Scenario 4: Dead write (write with no subsequent read) produces warning."""

    def test_dead_write_detected(self):
        """Write node with no read edge is flagged as dead write."""
        detections = [
            DetectionResult(
                variable_name="counter",
                deliverable_id="D1.1",
                introduction_type=IntroductionType.COUNTER,
                confidence=0.9,
            ),
        ]

        inventory = [
            MutationInventoryResult(
                variable_name="counter",
                mutation_sites=[
                    MutationSite(deliverable_id="D1.1", expression="introduced as counter", context="birth site"),
                    MutationSite(deliverable_id="D2.1", expression="increment counter", context="update counter value"),
                ],
                ambiguous_sites=[],
            ),
        ]

        # No deliverable reads counter -- all writes are dead
        deliverables = [
            Deliverable(id="D1.1", description="Introduce counter for event counting"),
            Deliverable(id="D2.1", description="Increment counter after each batch"),
        ]

        graph = build_dataflow_graph(detections, inventory, deliverables)

        dead_writes = graph.find_dead_writes()
        assert len(dead_writes) >= 1

        # Dead write should include the birth and write nodes
        dead_ids = {dw.deliverable_id for dw in dead_writes}
        assert "D1.1" in dead_ids or "D2.1" in dead_ids


class TestEmptyDeliverables:
    """Scenario 5: Empty deliverable list produces empty graph."""

    def test_empty_input_empty_graph(self):
        graph = build_dataflow_graph([], [], [])
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert len(graph.cross_milestone_edges) == 0
        assert graph.detect_cycles() == []
        assert graph.find_dead_writes() == []


class TestCycleDetection:
    """Additional: Verify cycle detection algorithm works."""

    def test_detects_cycle_in_manual_graph(self):
        """Manually construct a graph with a cycle and verify detection."""
        graph = DataFlowGraph()

        n1 = DataFlowNode("D1.1", "x", NodeOperation.WRITE)
        n2 = DataFlowNode("D2.1", "x", NodeOperation.READ)
        n3 = DataFlowNode("D2.1", "x", NodeOperation.WRITE)

        # n1 -> n2 -> n3 -> n1 (cycle)
        graph.add_edge(DataFlowEdge(source=n1, target=n2))
        graph.add_edge(DataFlowEdge(source=n2, target=n3))
        graph.add_edge(DataFlowEdge(source=n3, target=n1))

        cycles = graph.detect_cycles()
        assert len(cycles) >= 1

    def test_no_cycle_in_linear_graph(self):
        """Linear graph has no cycles."""
        graph = DataFlowGraph()

        n1 = DataFlowNode("D1.1", "x", NodeOperation.BIRTH)
        n2 = DataFlowNode("D2.1", "x", NodeOperation.WRITE)
        n3 = DataFlowNode("D3.1", "x", NodeOperation.READ)

        graph.add_edge(DataFlowEdge(source=n1, target=n2))
        graph.add_edge(DataFlowEdge(source=n2, target=n3))

        cycles = graph.detect_cycles()
        assert len(cycles) == 0


class TestPerformanceWarning:
    """Verify 100-deliverable performance warning."""

    def test_100_deliverable_warning(self):
        """100+ deliverables triggers performance warning."""
        detections = [
            DetectionResult(
                variable_name="x",
                deliverable_id="D1.1",
                introduction_type=IntroductionType.GENERIC,
            ),
        ]
        inventory = [
            MutationInventoryResult(
                variable_name="x",
                mutation_sites=[
                    MutationSite(deliverable_id="D1.1", expression="birth", context="birth site"),
                ],
                ambiguous_sites=[],
            ),
        ]
        deliverables = [
            Deliverable(id=f"D1.{i}", description=f"Deliverable {i}")
            for i in range(100)
        ]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            build_dataflow_graph(detections, inventory, deliverables)
            perf_warnings = [x for x in w if "slow" in str(x.message).lower()]
            assert len(perf_warnings) >= 1
