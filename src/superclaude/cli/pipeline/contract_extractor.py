"""Implicit contract extractor -- extracts cross-milestone contracts from data flow edges.

For each cross-milestone edge in the data flow graph, parses:
- Writer semantics: "set X to mean Y", "X represents Z after this operation"
- Reader assumptions: "assumes X is", "when X equals", "based on X"

Below 60% confidence -> UNSPECIFIED with mandatory human review flag.

R-013 acknowledged: implicit contract extraction from natural language has
fundamental reliability limits. UNSPECIFIED below 60% with mandatory human
review is the mitigation.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .dataflow_graph import DataFlowEdge, DataFlowGraph
from .models import Deliverable


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

UNSPECIFIED = "UNSPECIFIED"
CONFIDENCE_THRESHOLD = 0.60


@dataclass
class ImplicitContract:
    """A contract between a writer and reader across milestone boundaries.

    Attributes:
        variable: Name of the state variable.
        writer_deliverable: ID of the deliverable performing the write.
        reader_deliverable: ID of the deliverable performing the read.
        writer_semantics: What the writer claims the variable means after writing.
        reader_assumption: What the reader assumes the variable means.
        writer_confidence: Confidence score for writer semantics extraction (0.0-1.0).
        reader_confidence: Confidence score for reader assumption extraction (0.0-1.0).
        needs_human_review: True if either confidence < CONFIDENCE_THRESHOLD.
    """
    variable: str
    writer_deliverable: str
    reader_deliverable: str
    writer_semantics: str = UNSPECIFIED
    reader_assumption: str = UNSPECIFIED
    writer_confidence: float = 0.0
    reader_confidence: float = 0.0

    @property
    def needs_human_review(self) -> bool:
        return (
            self.writer_confidence < CONFIDENCE_THRESHOLD
            or self.reader_confidence < CONFIDENCE_THRESHOLD
        )

    @property
    def overall_confidence(self) -> float:
        """Combined confidence (geometric mean of writer and reader)."""
        return (self.writer_confidence * self.reader_confidence) ** 0.5

    @property
    def is_fully_specified(self) -> bool:
        return (
            self.writer_semantics != UNSPECIFIED
            and self.reader_assumption != UNSPECIFIED
        )

    @property
    def highest_risk(self) -> bool:
        """Both sides UNSPECIFIED -> highest risk."""
        return (
            self.writer_semantics == UNSPECIFIED
            and self.reader_assumption == UNSPECIFIED
        )


# ---------------------------------------------------------------------------
# Writer semantic patterns
# ---------------------------------------------------------------------------

_WRITER_PATTERNS: list[tuple[re.Pattern, float]] = [
    # "set X to mean Y" / "set X to represent Y"
    (re.compile(r"\bset\s+\w+\s+to\s+(?:mean|represent|indicate|track)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.85),
    # "X represents Y after this"
    (re.compile(r"\b\w+\s+represents?\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.80),
    # "X tracks Y" / "X counts Y"
    (re.compile(r"\b\w+\s+(?:tracks?|counts?|measures?|records?)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.80),
    # "store Y in X" / "write Y to X"
    (re.compile(r"\b(?:store|write|save|persist)\s+(.+?)\s+(?:in|to|into)\s+\w+", re.IGNORECASE), 0.75),
    # "X equals Y after" / "X will be Y"
    (re.compile(r"\b\w+\s+(?:equals?|will\s+be|becomes?|is\s+set\s+to)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.75),
    # "update X with Y" / "update X to Y"
    (re.compile(r"\bupdate\s+\w+\s+(?:with|to)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.70),
    # "increment X by Y" / "advance X by Y"
    (re.compile(r"\b(?:increment|advance|increase|decrease)\s+\w+\s+by\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.75),
    # Weaker: "X is Y"
    (re.compile(r"\b\w+\s+is\s+(?:the\s+)?(.+?)(?:\.|,|$)", re.IGNORECASE), 0.55),
]

# ---------------------------------------------------------------------------
# Reader assumption patterns
# ---------------------------------------------------------------------------

_READER_PATTERNS: list[tuple[re.Pattern, float]] = [
    # "assumes X is Y" / "assumes X equals Y"
    (re.compile(r"\bassumes?\s+\w+\s+(?:is|equals?|contains?|represents?)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.90),
    # "when X equals Y" / "when X is Y"
    (re.compile(r"\bwhen\s+\w+\s+(?:equals?|is|reaches?|exceeds?)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.85),
    # "based on X" / "depends on X"
    (re.compile(r"\b(?:based\s+on|depends?\s+on|relies?\s+on)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.70),
    # "expects X to be Y"
    (re.compile(r"\bexpects?\s+\w+\s+to\s+(?:be|equal|contain|represent)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.85),
    # "if X then" / "check if X"
    (re.compile(r"\b(?:if|check\s+(?:if|whether))\s+\w+\s+(?:is|equals?|has|contains?)\s+(.+?)(?:\s+then|\.|,|$)", re.IGNORECASE), 0.75),
    # "X should be Y" / "X must be Y"
    (re.compile(r"\b\w+\s+(?:should|must|shall)\s+(?:be|equal|contain)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.80),
    # "requires X" / "needs X"
    (re.compile(r"\b(?:requires?|needs?)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.60),
    # Weaker: "uses X" / "reads X"
    (re.compile(r"\b(?:uses?|reads?|accesses?|fetches?)\s+(.+?)(?:\.|,|$)", re.IGNORECASE), 0.50),
]


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_writer_semantics(
    description: str, variable_name: str,
) -> tuple[str, float]:
    """Extract writer semantics from a deliverable description.

    Returns (semantics_text, confidence). Returns (UNSPECIFIED, 0.0)
    if no pattern matches or confidence < threshold.
    """
    if not description:
        return UNSPECIFIED, 0.0

    best_match: str = UNSPECIFIED
    best_confidence: float = 0.0

    for pattern, base_confidence in _WRITER_PATTERNS:
        for m in pattern.finditer(description):
            extracted = m.group(1).strip()
            if not extracted:
                continue

            # Boost confidence if variable name is near the match
            var_lower = variable_name.lower().lstrip("_")
            proximity_boost = 0.05 if var_lower in description.lower()[max(0, m.start()-50):m.end()+50] else 0.0
            confidence = min(base_confidence + proximity_boost, 1.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = extracted

    if best_confidence < CONFIDENCE_THRESHOLD:
        return UNSPECIFIED, best_confidence

    return best_match, best_confidence


def extract_reader_assumption(
    description: str, variable_name: str,
) -> tuple[str, float]:
    """Extract reader assumption from a deliverable description.

    Returns (assumption_text, confidence). Returns (UNSPECIFIED, 0.0)
    if no pattern matches or confidence < threshold.
    """
    if not description:
        return UNSPECIFIED, 0.0

    best_match: str = UNSPECIFIED
    best_confidence: float = 0.0

    for pattern, base_confidence in _READER_PATTERNS:
        for m in pattern.finditer(description):
            extracted = m.group(1).strip()
            if not extracted:
                continue

            var_lower = variable_name.lower().lstrip("_")
            proximity_boost = 0.05 if var_lower in description.lower()[max(0, m.start()-50):m.end()+50] else 0.0
            confidence = min(base_confidence + proximity_boost, 1.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = extracted

    if best_confidence < CONFIDENCE_THRESHOLD:
        return UNSPECIFIED, best_confidence

    return best_match, best_confidence


def extract_implicit_contracts(
    graph: DataFlowGraph,
    deliverable_lookup: dict[str, Deliverable],
) -> list[ImplicitContract]:
    """Extract implicit contracts from all cross-milestone edges in the data flow graph.

    Args:
        graph: The data flow graph from T04.01.
        deliverable_lookup: Map of deliverable_id -> Deliverable for description access.

    Returns:
        List of ImplicitContract objects, one per cross-milestone edge.
    """
    contracts: list[ImplicitContract] = []
    seen_pairs: set[tuple[str, str, str]] = set()

    for edge in graph.cross_milestone_edges:
        pair_key = (edge.source.variable_name, edge.source.deliverable_id, edge.target.deliverable_id)
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        variable = edge.source.variable_name
        writer_d = deliverable_lookup.get(edge.source.deliverable_id)
        reader_d = deliverable_lookup.get(edge.target.deliverable_id)

        writer_desc = writer_d.description if writer_d else ""
        reader_desc = reader_d.description if reader_d else ""

        writer_semantics, writer_conf = extract_writer_semantics(writer_desc, variable)
        reader_assumption, reader_conf = extract_reader_assumption(reader_desc, variable)

        contract = ImplicitContract(
            variable=variable,
            writer_deliverable=edge.source.deliverable_id,
            reader_deliverable=edge.target.deliverable_id,
            writer_semantics=writer_semantics,
            reader_assumption=reader_assumption,
            writer_confidence=writer_conf,
            reader_confidence=reader_conf,
        )
        contracts.append(contract)

    return contracts
