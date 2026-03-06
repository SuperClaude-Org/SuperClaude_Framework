"""Data flow graph builder -- cross-deliverable state variable tracing.

Constructs a directed graph where:
- Nodes: (deliverable_id, variable_name, operation) tuples with operation in {birth, write, read}
- Edges: write -> read connections
- Cross-milestone edges: annotated with milestone boundary crossing

Features:
- Adjacency list representation for O(V+E) operations (R-012 mitigation)
- Cycle detection via DFS
- Dead write warnings (write with no subsequent read)
- 100-deliverable performance warning

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator

from .models import Deliverable
from .mutation_inventory import MutationInventoryResult
from .state_detector import DetectionResult


class NodeOperation(Enum):
    """Operation type for a data flow node."""
    BIRTH = "birth"
    WRITE = "write"
    READ = "read"


@dataclass(frozen=True)
class DataFlowNode:
    """A node in the data flow graph.

    Attributes:
        deliverable_id: ID of the deliverable containing this operation.
        variable_name: Name of the state variable.
        operation: The operation type (birth, write, read).
    """
    deliverable_id: str
    variable_name: str
    operation: NodeOperation

    @property
    def milestone(self) -> str:
        """Extract milestone from deliverable_id (e.g. 'D2.3' -> 'M2', 'D-0015' -> 'M0015')."""
        import re
        m = re.match(r"D(\d+)\.", self.deliverable_id)
        if m:
            return f"M{m.group(1)}"
        m = re.match(r"D-(\d+)", self.deliverable_id)
        if m:
            return f"M{m.group(1)}"
        return f"M-{self.deliverable_id}"


@dataclass
class DataFlowEdge:
    """A directed edge from a write/birth node to a read node.

    Attributes:
        source: The write/birth node.
        target: The read node.
        is_cross_milestone: True if source and target are in different milestones.
        source_milestone: Milestone of the source node.
        target_milestone: Milestone of the target node.
    """
    source: DataFlowNode
    target: DataFlowNode
    is_cross_milestone: bool = False
    source_milestone: str = ""
    target_milestone: str = ""

    def __post_init__(self) -> None:
        if not self.source_milestone:
            self.source_milestone = self.source.milestone
        if not self.target_milestone:
            self.target_milestone = self.target.milestone
        if not self.is_cross_milestone:
            self.is_cross_milestone = self.source_milestone != self.target_milestone


@dataclass
class DataFlowGraph:
    """Directed graph tracing state variables through deliverables.

    Uses adjacency list representation for O(V+E) operations.
    """
    nodes: list[DataFlowNode] = field(default_factory=list)
    edges: list[DataFlowEdge] = field(default_factory=list)
    _adjacency: dict[DataFlowNode, list[DataFlowEdge]] = field(
        default_factory=dict, repr=False,
    )
    _node_set: set[DataFlowNode] = field(default_factory=set, repr=False)

    def add_node(self, node: DataFlowNode) -> None:
        """Add a node to the graph."""
        if node not in self._node_set:
            self.nodes.append(node)
            self._node_set.add(node)
            self._adjacency.setdefault(node, [])

    def add_edge(self, edge: DataFlowEdge) -> None:
        """Add a directed edge to the graph."""
        self.add_node(edge.source)
        self.add_node(edge.target)
        self.edges.append(edge)
        self._adjacency[edge.source].append(edge)

    @property
    def cross_milestone_edges(self) -> list[DataFlowEdge]:
        """All edges that cross milestone boundaries."""
        return [e for e in self.edges if e.is_cross_milestone]

    def outgoing(self, node: DataFlowNode) -> list[DataFlowEdge]:
        """Get outgoing edges from a node."""
        return self._adjacency.get(node, [])

    def detect_cycles(self) -> list[list[DataFlowNode]]:
        """Detect cycles using iterative DFS with coloring.

        Returns list of cycles found (each cycle is a list of nodes).
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[DataFlowNode, int] = {n: WHITE for n in self.nodes}
        parent: dict[DataFlowNode, DataFlowNode | None] = {}
        cycles: list[list[DataFlowNode]] = []

        for start in self.nodes:
            if color[start] != WHITE:
                continue

            stack: list[tuple[DataFlowNode, int]] = [(start, 0)]
            parent[start] = None

            while stack:
                node, edge_idx = stack[-1]

                if color[node] == WHITE:
                    color[node] = GRAY

                outgoing = self._adjacency.get(node, [])
                if edge_idx < len(outgoing):
                    stack[-1] = (node, edge_idx + 1)
                    neighbor = outgoing[edge_idx].target

                    if color[neighbor] == GRAY:
                        # Found a cycle -- reconstruct
                        cycle = [neighbor]
                        for s_node, _ in reversed(stack):
                            cycle.append(s_node)
                            if s_node == neighbor:
                                break
                        cycles.append(list(reversed(cycle)))
                    elif color[neighbor] == WHITE:
                        parent[neighbor] = node
                        stack.append((neighbor, 0))
                else:
                    color[node] = BLACK
                    stack.pop()

        return cycles

    def find_dead_writes(self) -> list[DataFlowNode]:
        """Find write/birth nodes with no outgoing edges to read nodes.

        A dead write is a write or birth with no subsequent read edge.
        """
        dead: list[DataFlowNode] = []
        for node in self.nodes:
            if node.operation in (NodeOperation.WRITE, NodeOperation.BIRTH):
                outgoing = self._adjacency.get(node, [])
                has_read_target = any(
                    e.target.operation == NodeOperation.READ for e in outgoing
                )
                if not has_read_target:
                    dead.append(node)
        return dead


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

_PERFORMANCE_WARNING_THRESHOLD = 100

# Read indicator patterns for scanning deliverable descriptions
_READ_INDICATORS = [
    "read", "reads", "reading",
    "consume", "consumes", "consuming",
    "use", "uses", "using",
    "check", "checks", "checking",
    "access", "accesses", "accessing",
    "query", "queries", "querying",
    "fetch", "fetches", "fetching",
    "load", "loads", "loading",
    "get", "gets", "getting",
    "retrieve", "retrieves", "retrieving",
    "based on", "depends on", "requires",
    "assumes", "expects", "when",
]


def build_dataflow_graph(
    detections: list[DetectionResult],
    inventory_results: list[MutationInventoryResult],
    all_deliverables: list[Deliverable],
    milestone_map: dict[str, str] | None = None,
) -> DataFlowGraph:
    """Build a data flow graph from state variable detections and mutation inventory.

    Args:
        detections: State variable detections from M2.
        inventory_results: Mutation inventory from M2.
        all_deliverables: All deliverables for read-site scanning.
        milestone_map: Optional map of deliverable_id -> milestone_id.
                       If not provided, milestones are inferred from IDs.

    Returns:
        DataFlowGraph with nodes, edges, and cross-milestone annotations.

    Raises:
        ValueError: If a read-before-birth condition is detected.
    """
    if len(all_deliverables) >= _PERFORMANCE_WARNING_THRESHOLD:
        warnings.warn(
            f"Data flow graph construction with {len(all_deliverables)} deliverables "
            f"may be slow. Consider --skip-dataflow flag.",
            stacklevel=2,
        )

    if not detections:
        return DataFlowGraph()

    graph = DataFlowGraph()

    # Build lookup: variable_name -> MutationInventoryResult
    inv_lookup: dict[str, MutationInventoryResult] = {}
    for inv in inventory_results:
        inv_lookup[inv.variable_name] = inv

    # For each detected variable, construct the subgraph
    for detection in detections:
        var_name = detection.variable_name

        # Birth node
        birth_node = DataFlowNode(
            deliverable_id=detection.deliverable_id,
            variable_name=var_name,
            operation=NodeOperation.BIRTH,
        )
        graph.add_node(birth_node)

        # Write nodes from mutation inventory
        write_nodes: list[DataFlowNode] = []
        inv_result = inv_lookup.get(var_name)
        if inv_result:
            for site in inv_result.mutation_sites:
                # Skip the birth site itself
                if site.context == "birth site":
                    continue
                write_node = DataFlowNode(
                    deliverable_id=site.deliverable_id,
                    variable_name=var_name,
                    operation=NodeOperation.WRITE,
                )
                graph.add_node(write_node)
                write_nodes.append(write_node)

        # Read nodes from deliverable descriptions
        read_nodes: list[DataFlowNode] = []
        birth_deliverable = detection.deliverable_id
        write_deliverables = {wn.deliverable_id for wn in write_nodes}
        write_deliverables.add(birth_deliverable)

        for d in all_deliverables:
            if not d.description:
                continue
            # Skip deliverables that are already write/birth sites
            if d.id in write_deliverables:
                continue
            if _references_variable_as_read(d.description, var_name):
                read_node = DataFlowNode(
                    deliverable_id=d.id,
                    variable_name=var_name,
                    operation=NodeOperation.READ,
                )
                graph.add_node(read_node)
                read_nodes.append(read_node)

        # Check for read-before-birth
        _check_read_before_birth(birth_node, read_nodes, all_deliverables)

        # Connect edges: birth -> reads, writes -> reads
        all_writers = [birth_node] + write_nodes
        for writer in all_writers:
            for reader in read_nodes:
                edge = DataFlowEdge(source=writer, target=reader)
                graph.add_edge(edge)

    return graph


def _references_variable_as_read(description: str, var_name: str) -> bool:
    """Check if a description references a variable in a read context."""
    desc_lower = description.lower()
    var_lower = var_name.lower().lstrip("_")

    if var_lower not in desc_lower and var_name.lower() not in desc_lower:
        return False

    # Check for read indicators near the variable reference
    for indicator in _READ_INDICATORS:
        if indicator in desc_lower:
            return True

    return False


def _check_read_before_birth(
    birth_node: DataFlowNode,
    read_nodes: list[DataFlowNode],
    all_deliverables: list[Deliverable],
) -> None:
    """Check for read-before-birth conditions.

    Raises ValueError if a read node's deliverable appears before the
    birth node's deliverable in the deliverable ordering.
    """
    # Build ordering from deliverable list
    id_to_index: dict[str, int] = {}
    for idx, d in enumerate(all_deliverables):
        id_to_index[d.id] = idx

    birth_idx = id_to_index.get(birth_node.deliverable_id, -1)

    for read_node in read_nodes:
        read_idx = id_to_index.get(read_node.deliverable_id, -1)
        if read_idx >= 0 and birth_idx >= 0 and read_idx < birth_idx:
            raise ValueError(
                f"Read-before-birth: variable '{birth_node.variable_name}' "
                f"read in '{read_node.deliverable_id}' (index {read_idx}) "
                f"before birth in '{birth_node.deliverable_id}' (index {birth_idx})"
            )
