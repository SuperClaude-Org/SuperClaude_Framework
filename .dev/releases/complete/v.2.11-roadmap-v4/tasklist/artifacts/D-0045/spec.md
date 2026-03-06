# D-0045: Cross-Milestone Verification Emitter & Pipeline Integration Spec

## Emitter Logic

The verification emitter (`dataflow_pass._emit_contract_test_deliverables`) generates `CONTRACT_TEST` deliverables for:

1. **Conflicts**: Each `ConflictDetection` produces a `contract_test` deliverable placed in the reader's milestone.
2. **High-risk contracts**: Contracts where both writer and reader are `UNSPECIFIED` (highest risk) also produce `contract_test` deliverables, unless already covered by a conflict.

### Deliverable ID Format

```
D{reader_milestone}.{seq}.ct
```

Where `reader_milestone` is extracted from the reader deliverable ID and `seq` is a sequential counter starting at 1.

### Deliverable Metadata

Each generated deliverable carries metadata:
- `variable`: The state variable name
- `writer_deliverable`: ID of the writer deliverable
- `reader_deliverable`: ID of the reader deliverable
- `conflict_kind`: The conflict classification or `"highest_risk_unspecified"`
- `writer_semantics`: Extracted writer semantics (or `UNSPECIFIED`)
- `reader_assumption`: Extracted reader assumption (or `UNSPECIFIED`)

## Pipeline Position

```
M1 (decomposition) → M2 (invariant+FMEA) → M3 (guard analysis) → M4 (data flow tracing)
```

The M4 pass (`run_dataflow_tracing_pass`) is the final pipeline pass. It:
1. Counts milestones from all deliverables
2. Applies conditional threshold check (default: 6+ milestones)
3. Builds data flow graph (T04.01)
4. Extracts implicit contracts (T04.02)
5. Detects conflicts (T04.03)
6. Emits `contract_test` deliverables
7. Renders markdown section

## Conditional Threshold

- **6+ milestones** (default): Full data flow tracing with contracts, conflicts, and `contract_test` deliverables
- **Below threshold**: Skip summary referencing M2 Invariant Registry, zero `contract_test` deliverables
- **`--force-dataflow`**: Overrides threshold, enables full tracing regardless
- **`--dataflow-threshold N`**: Configures the threshold (default: 6)

## Output Section Format

The `section_markdown` includes:
- Milestone count, node count, edge count, cross-milestone edge count
- Cycle warnings (if any)
- Dead write warnings with deliverable IDs
- Implicit contracts table (Variable, Writer, Reader, Semantics, Assumption, Confidence)
- Conflicts table (Variable, Kind, Severity, Description)
- Generated `contract_test` deliverables list

## Public API

Exported from `superclaude.cli.pipeline`:
- `DataFlowTracingOutput` - Output dataclass
- `run_dataflow_tracing_pass()` - M4 orchestration function
- `DataFlowGraph`, `DataFlowNode`, `DataFlowEdge`, `NodeOperation` - Graph types
- `ImplicitContract`, `extract_implicit_contracts` - Contract extraction
- `ConflictKind`, `ConflictDetection`, `detect_conflicts` - Conflict detection
- `build_dataflow_graph` - Graph construction

## Implementation Files

- `src/superclaude/cli/pipeline/dataflow_pass.py` - M4 orchestration pass
- `src/superclaude/cli/pipeline/dataflow_graph.py` - Graph builder (T04.01)
- `src/superclaude/cli/pipeline/contract_extractor.py` - Contract extractor (T04.02)
- `src/superclaude/cli/pipeline/conflict_detector.py` - Conflict detector (T04.03)
- `src/superclaude/cli/pipeline/__init__.py` - Public API exports (42 symbols)
