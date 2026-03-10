# D-0039: Data Flow Graph Builder Specification

## Graph Structure

### Node Schema
```
DataFlowNode(frozen=True):
  deliverable_id: str      # e.g. "D1.1", "D-0015"
  variable_name: str       # e.g. "offset", "_cursor"
  operation: NodeOperation  # BIRTH | WRITE | READ
```

### Edge Schema
```
DataFlowEdge:
  source: DataFlowNode           # Writer/birth node
  target: DataFlowNode           # Reader node
  is_cross_milestone: bool       # Auto-computed from milestone comparison
  source_milestone: str          # e.g. "M1"
  target_milestone: str          # e.g. "M2"
```

### Graph Representation
- **Adjacency list** (`dict[DataFlowNode, list[DataFlowEdge]]`) for O(V+E) traversal
- Node deduplication via frozen dataclass + `_node_set`
- Edge storage in both flat list and adjacency map

## Construction Algorithm

1. For each detected state variable:
   a. Create BIRTH node at detection's deliverable
   b. Create WRITE nodes from mutation inventory (excluding birth site)
   c. Scan all deliverables for READ references (using read indicator patterns)
   d. Check read-before-birth ordering → raise ValueError
   e. Connect all writers (birth + writes) to all readers

## Cycle Detection Algorithm

- **Method**: Iterative DFS with 3-color marking (WHITE/GRAY/BLACK)
- **Complexity**: O(V+E)
- Back edges (GRAY→GRAY) indicate cycles; cycle path reconstructed from stack

## Dead Write Detection

- Any WRITE or BIRTH node with no outgoing edge to a READ node
- Returns list of dead write nodes with deliverable_id for user action

## Performance Characteristics

- Construction: O(D × V) where D = deliverables, V = detected variables
- Cycle detection: O(V + E)
- Dead write detection: O(V)
- **Warning threshold**: 100 deliverables triggers performance warning
- **Mitigation flags**: `--skip-dataflow`, intermediate result caching
