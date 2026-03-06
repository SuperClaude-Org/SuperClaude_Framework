"""Tests for implicit contract extractor -- T04.02 deliverable D-0042.

Four-scenario test suite:
1. Writer "set offset to events delivered" + reader "assumes offset equals events processed" -> contract captured
2. No explicit semantics -> writer_semantics=UNSPECIFIED (flagged)
3. Both UNSPECIFIED -> highest-risk classification
4. Confidence scoring calibrated (not all 0.5 or 1.0)
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.contract_extractor import (
    CONFIDENCE_THRESHOLD,
    UNSPECIFIED,
    ImplicitContract,
    extract_implicit_contracts,
    extract_reader_assumption,
    extract_writer_semantics,
)
from superclaude.cli.pipeline.dataflow_graph import (
    DataFlowEdge,
    DataFlowGraph,
    DataFlowNode,
    NodeOperation,
)
from superclaude.cli.pipeline.models import Deliverable


class TestContractCaptured:
    """Scenario 1: Writer + reader semantics both captured."""

    def test_explicit_writer_reader_captured(self):
        """Writer 'set offset to events delivered' + reader 'assumes offset equals events processed'."""
        writer_desc = "Set offset to track events delivered in this batch"
        reader_desc = "Assumes offset equals events processed so far to determine resume point"

        w_sem, w_conf = extract_writer_semantics(writer_desc, "offset")
        r_asm, r_conf = extract_reader_assumption(reader_desc, "offset")

        assert w_sem != UNSPECIFIED, f"Writer semantics should be captured, got UNSPECIFIED (conf={w_conf})"
        assert r_asm != UNSPECIFIED, f"Reader assumption should be captured, got UNSPECIFIED (conf={r_conf})"
        assert w_conf >= CONFIDENCE_THRESHOLD
        assert r_conf >= CONFIDENCE_THRESHOLD

    def test_full_contract_extraction(self):
        """Full pipeline: graph -> cross-milestone edge -> contract extracted."""
        graph = DataFlowGraph()
        writer = DataFlowNode("D1.1", "offset", NodeOperation.WRITE)
        reader = DataFlowNode("D2.1", "offset", NodeOperation.READ)
        edge = DataFlowEdge(source=writer, target=reader)
        graph.add_edge(edge)

        deliverable_lookup = {
            "D1.1": Deliverable(
                id="D1.1",
                description="Set offset to track events delivered after batch processing",
            ),
            "D2.1": Deliverable(
                id="D2.1",
                description="Assumes offset equals events processed, uses offset to resume",
            ),
        }

        contracts = extract_implicit_contracts(graph, deliverable_lookup)
        assert len(contracts) == 1

        c = contracts[0]
        assert c.variable == "offset"
        assert c.writer_deliverable == "D1.1"
        assert c.reader_deliverable == "D2.1"
        assert c.writer_semantics != UNSPECIFIED
        assert c.reader_assumption != UNSPECIFIED
        assert c.is_fully_specified


class TestUnspecifiedWriter:
    """Scenario 2: No explicit semantics -> UNSPECIFIED (flagged)."""

    def test_no_writer_semantics(self):
        """Vague description with no semantic patterns -> UNSPECIFIED."""
        writer_desc = "Process batch data"  # No semantic patterns
        w_sem, w_conf = extract_writer_semantics(writer_desc, "offset")

        assert w_sem == UNSPECIFIED
        assert w_conf < CONFIDENCE_THRESHOLD

    def test_unspecified_flagged_for_review(self):
        """UNSPECIFIED writer semantics produce needs_human_review=True."""
        contract = ImplicitContract(
            variable="offset",
            writer_deliverable="D1.1",
            reader_deliverable="D2.1",
            writer_semantics=UNSPECIFIED,
            reader_assumption="events processed",
            writer_confidence=0.3,
            reader_confidence=0.85,
        )
        assert contract.needs_human_review


class TestBothUnspecified:
    """Scenario 3: Both UNSPECIFIED -> highest-risk classification."""

    def test_both_unspecified_highest_risk(self):
        """Both writer and reader UNSPECIFIED is highest risk."""
        contract = ImplicitContract(
            variable="counter",
            writer_deliverable="D1.1",
            reader_deliverable="D3.1",
            writer_semantics=UNSPECIFIED,
            reader_assumption=UNSPECIFIED,
            writer_confidence=0.2,
            reader_confidence=0.1,
        )
        assert contract.highest_risk
        assert contract.needs_human_review
        assert not contract.is_fully_specified

    def test_one_specified_not_highest_risk(self):
        """Only one side UNSPECIFIED is NOT highest risk."""
        contract = ImplicitContract(
            variable="counter",
            writer_deliverable="D1.1",
            reader_deliverable="D3.1",
            writer_semantics="total events processed",
            reader_assumption=UNSPECIFIED,
            writer_confidence=0.85,
            reader_confidence=0.3,
        )
        assert not contract.highest_risk
        assert contract.needs_human_review  # Still needs review (reader low)


class TestConfidenceCalibration:
    """Scenario 4: Confidence scoring calibrated (not all 0.5 or 1.0)."""

    def test_varied_confidence_scores(self):
        """Different description quality should produce varied confidence scores."""
        # High-confidence writer (explicit semantics)
        _, conf_high = extract_writer_semantics(
            "Set offset to represent events delivered in this batch", "offset"
        )

        # Medium-confidence writer (weaker pattern)
        _, conf_med = extract_writer_semantics(
            "Update offset with new batch count", "offset"
        )

        # Low-confidence writer (no clear pattern)
        _, conf_low = extract_writer_semantics(
            "Handle the offset somehow", "offset"
        )

        # Verify calibration: not all the same
        scores = {round(conf_high, 1), round(conf_med, 1), round(conf_low, 1)}
        assert len(scores) >= 2, (
            f"Confidence scores should be calibrated across range, "
            f"got: high={conf_high}, med={conf_med}, low={conf_low}"
        )

        # High should be higher than low
        assert conf_high > conf_low

    def test_reader_confidence_varies(self):
        """Reader assumptions with different patterns produce varied confidence."""
        _, conf_high = extract_reader_assumption(
            "Assumes offset equals total events processed", "offset"
        )
        _, conf_low = extract_reader_assumption(
            "Uses offset", "offset"
        )

        assert conf_high > conf_low

    def test_overall_confidence_geometric_mean(self):
        """Overall confidence is geometric mean of writer and reader."""
        contract = ImplicitContract(
            variable="x",
            writer_deliverable="D1.1",
            reader_deliverable="D2.1",
            writer_semantics="events delivered",
            reader_assumption="events processed",
            writer_confidence=0.80,
            reader_confidence=0.90,
        )
        expected = (0.80 * 0.90) ** 0.5
        assert abs(contract.overall_confidence - expected) < 0.01


class TestEdgeCases:
    """Additional edge case coverage."""

    def test_empty_description(self):
        """Empty description returns UNSPECIFIED."""
        w_sem, w_conf = extract_writer_semantics("", "x")
        assert w_sem == UNSPECIFIED
        assert w_conf == 0.0

    def test_no_cross_milestone_edges_no_contracts(self):
        """Graph with no cross-milestone edges produces no contracts."""
        graph = DataFlowGraph()
        writer = DataFlowNode("D1.1", "x", NodeOperation.WRITE)
        reader = DataFlowNode("D1.2", "x", NodeOperation.READ)
        edge = DataFlowEdge(source=writer, target=reader)
        graph.add_edge(edge)

        contracts = extract_implicit_contracts(graph, {})
        assert len(contracts) == 0

    def test_deduplication_of_same_pair(self):
        """Same writer-reader pair should not produce duplicate contracts."""
        graph = DataFlowGraph()
        writer = DataFlowNode("D1.1", "x", NodeOperation.WRITE)
        reader = DataFlowNode("D2.1", "x", NodeOperation.READ)
        # Add same edge twice (shouldn't happen but defensive)
        graph.add_edge(DataFlowEdge(source=writer, target=reader))
        graph.add_edge(DataFlowEdge(source=writer, target=reader))

        deliverable_lookup = {
            "D1.1": Deliverable(id="D1.1", description="Set x to track count"),
            "D2.1": Deliverable(id="D2.1", description="Assumes x equals total count"),
        }
        contracts = extract_implicit_contracts(graph, deliverable_lookup)
        assert len(contracts) == 1
