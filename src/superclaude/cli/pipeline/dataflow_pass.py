"""Data flow tracing pipeline pass -- final pass after guard analysis (M4).

Integrates:
- T04.01: Data flow graph builder
- T04.02: Implicit contract extractor
- T04.03: Conflict detector

Generates contract_test deliverables for conflicts and high-risk contracts.
Conditional: below 6-milestone threshold produces summary only with M2 reference.
Configurable via --dataflow-threshold (default 6).

Pipeline order: decomposition (M1) -> invariant+FMEA (M2) -> guard analysis (M3) -> data flow tracing (M4).

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .conflict_detector import ConflictDetection, ConflictKind, detect_conflicts
from .contract_extractor import (
    UNSPECIFIED,
    ImplicitContract,
    extract_implicit_contracts,
)
from .dataflow_graph import DataFlowGraph, build_dataflow_graph
from .invariant_pass import InvariantRegistryOutput
from .invariants import InvariantEntry
from .models import Deliverable, DeliverableKind
from .mutation_inventory import MutationInventoryResult
from .state_detector import DetectionResult


DEFAULT_DATAFLOW_THRESHOLD = 6


@dataclass
class DataFlowTracingOutput:
    """Output of the M4 data flow tracing pipeline pass.

    Attributes:
        graph: The constructed data flow graph.
        contracts: Extracted implicit contracts.
        conflicts: Detected conflicts.
        generated_deliverables: contract_test deliverables for conflicts.
        section_markdown: Rendered markdown section for pipeline output.
        was_skipped: True if milestone count below threshold (summary only).
        milestone_count: Number of milestones detected.
    """
    graph: DataFlowGraph = field(default_factory=DataFlowGraph)
    contracts: list[ImplicitContract] = field(default_factory=list)
    conflicts: list[ConflictDetection] = field(default_factory=list)
    generated_deliverables: list[Deliverable] = field(default_factory=list)
    section_markdown: str = ""
    was_skipped: bool = False
    milestone_count: int = 0


def _count_milestones(deliverables: list[Deliverable]) -> int:
    """Count distinct milestones from deliverable IDs."""
    milestones: set[str] = set()
    for d in deliverables:
        m = re.match(r"D(\d+)\.", d.id)
        if m:
            milestones.add(m.group(1))
            continue
        m = re.match(r"D-(\d+)", d.id)
        if m:
            milestones.add(m.group(1))
    return len(milestones)


def _emit_contract_test_deliverables(
    conflicts: list[ConflictDetection],
    contracts: list[ImplicitContract],
) -> list[Deliverable]:
    """Generate contract_test deliverables for conflicts and high-risk contracts.

    Each deliverable is placed in the reader's milestone.
    """
    generated: list[Deliverable] = []
    seq = 1

    # For each conflict, generate a contract_test deliverable
    for conflict in conflicts:
        c = conflict.contract
        reader_milestone = _extract_milestone(c.reader_deliverable)

        deliverable = Deliverable(
            id=f"D{reader_milestone}.{seq}.ct",
            description=(
                f"Contract test: verify '{c.variable}' compatibility between "
                f"writer {c.writer_deliverable} and reader {c.reader_deliverable}. "
                f"Conflict: {conflict.kind.value}. "
                f"Resolution: {conflict.suggested_resolution}"
            ),
            kind=DeliverableKind.CONTRACT_TEST,
            metadata={
                "variable": c.variable,
                "writer_deliverable": c.writer_deliverable,
                "reader_deliverable": c.reader_deliverable,
                "conflict_kind": conflict.kind.value,
                "writer_semantics": c.writer_semantics,
                "reader_assumption": c.reader_assumption,
            },
        )
        generated.append(deliverable)
        seq += 1

    # For high-risk contracts without explicit conflicts
    for contract in contracts:
        if contract.highest_risk and not any(
            cf.contract is contract for cf in conflicts
        ):
            reader_milestone = _extract_milestone(contract.reader_deliverable)
            deliverable = Deliverable(
                id=f"D{reader_milestone}.{seq}.ct",
                description=(
                    f"Contract test: verify '{contract.variable}' between "
                    f"writer {contract.writer_deliverable} and reader {contract.reader_deliverable}. "
                    f"Both sides UNSPECIFIED -- highest risk."
                ),
                kind=DeliverableKind.CONTRACT_TEST,
                metadata={
                    "variable": contract.variable,
                    "writer_deliverable": contract.writer_deliverable,
                    "reader_deliverable": contract.reader_deliverable,
                    "conflict_kind": "highest_risk_unspecified",
                    "writer_semantics": contract.writer_semantics,
                    "reader_assumption": contract.reader_assumption,
                },
            )
            generated.append(deliverable)
            seq += 1

    return generated


def _extract_milestone(deliverable_id: str) -> str:
    """Extract milestone number from deliverable ID."""
    m = re.match(r"D(\d+)\.", deliverable_id)
    if m:
        return m.group(1)
    m = re.match(r"D-(\d+)", deliverable_id)
    if m:
        return m.group(1)
    return deliverable_id.lstrip("D-")


def run_dataflow_tracing_pass(
    deliverables: list[Deliverable],
    detections: list[DetectionResult],
    inventory_results: list[MutationInventoryResult],
    invariant_output: InvariantRegistryOutput | None = None,
    fmea_severity_map: dict[str, str] | None = None,
    dataflow_threshold: int = DEFAULT_DATAFLOW_THRESHOLD,
    force_dataflow: bool = False,
) -> DataFlowTracingOutput:
    """Execute the M4 data flow tracing pipeline pass.

    Pipeline position: after M3 guard analysis. Reads all deliverables
    including M1/M2/M3 generated deliverables.

    Args:
        deliverables: All deliverables (including M1-M3 generated).
        detections: State variable detections from M2.
        inventory_results: Mutation inventory from M2.
        invariant_output: Output from M2 invariant registry.
        fmea_severity_map: M2 FMEA severity map.
        dataflow_threshold: Milestone count threshold for full tracing (default 6).
        force_dataflow: Override threshold (--force-dataflow).

    Returns:
        DataFlowTracingOutput with graph, contracts, conflicts, and section.
    """
    if invariant_output is None:
        invariant_output = InvariantRegistryOutput()
    if fmea_severity_map is None:
        fmea_severity_map = {}

    milestone_count = _count_milestones(deliverables)

    # Conditional threshold check
    if not force_dataflow and milestone_count < dataflow_threshold:
        return DataFlowTracingOutput(
            was_skipped=True,
            milestone_count=milestone_count,
            section_markdown=_render_skip_summary(milestone_count, dataflow_threshold),
        )

    # Step 1: Build data flow graph
    graph = build_dataflow_graph(detections, inventory_results, deliverables)

    # Step 2: Extract implicit contracts
    deliverable_lookup = {d.id: d for d in deliverables}
    contracts = extract_implicit_contracts(graph, deliverable_lookup)

    # Step 3: Detect conflicts
    conflicts = detect_conflicts(
        contracts,
        invariant_entries=invariant_output.entries,
        fmea_severity_map=fmea_severity_map,
    )

    # Step 4: Generate contract_test deliverables
    generated = _emit_contract_test_deliverables(conflicts, contracts)

    # Step 5: Render section
    section = _render_dataflow_section(
        graph, contracts, conflicts, generated, milestone_count,
    )

    return DataFlowTracingOutput(
        graph=graph,
        contracts=contracts,
        conflicts=conflicts,
        generated_deliverables=generated,
        section_markdown=section,
        was_skipped=False,
        milestone_count=milestone_count,
    )


def _render_skip_summary(milestone_count: int, threshold: int) -> str:
    """Render summary when data flow tracing is skipped (below threshold)."""
    lines = [
        "## Data Flow Tracing",
        "",
        f"**Skipped**: Roadmap has {milestone_count} milestones "
        f"(threshold: {threshold}+).",
        "",
        "Cross-milestone variable tracking is available via the M2 Invariant Registry.",
        "Use `--force-dataflow` to enable full data flow tracing regardless of milestone count.",
    ]
    return "\n".join(lines)


def _render_dataflow_section(
    graph: DataFlowGraph,
    contracts: list[ImplicitContract],
    conflicts: list[ConflictDetection],
    generated: list[Deliverable],
    milestone_count: int,
) -> str:
    """Render the data flow tracing section as markdown."""
    lines = [
        "## Data Flow Tracing",
        "",
        f"**Milestones**: {milestone_count}",
        f"**Nodes**: {len(graph.nodes)}",
        f"**Edges**: {len(graph.edges)}",
        f"**Cross-milestone edges**: {len(graph.cross_milestone_edges)}",
        "",
    ]

    # Cycles
    cycles = graph.detect_cycles()
    if cycles:
        lines.append(f"**Cycles detected**: {len(cycles)}")
        lines.append("")

    # Dead writes
    dead_writes = graph.find_dead_writes()
    if dead_writes:
        lines.append(f"**Dead writes**: {len(dead_writes)}")
        for dw in dead_writes:
            lines.append(f"  - `{dw.variable_name}` in `{dw.deliverable_id}`")
        lines.append("")

    # Contracts
    if contracts:
        lines.append("### Implicit Contracts")
        lines.append("")
        lines.append("| Variable | Writer | Reader | Writer Semantics | Reader Assumption | Confidence |")
        lines.append("|----------|--------|--------|-----------------|-------------------|------------|")
        for c in contracts:
            lines.append(
                f"| `{c.variable}` | {c.writer_deliverable} | {c.reader_deliverable} | "
                f"{c.writer_semantics} | {c.reader_assumption} | "
                f"{c.overall_confidence:.2f} |"
            )
        lines.append("")

    # Conflicts
    if conflicts:
        lines.append("### Conflicts")
        lines.append("")
        lines.append("| Variable | Kind | Severity | Description |")
        lines.append("|----------|------|----------|-------------|")
        for cf in conflicts:
            lines.append(
                f"| `{cf.contract.variable}` | {cf.kind.value} | "
                f"{cf.severity} | {cf.description[:80]}... |"
            )
        lines.append("")

    # Generated deliverables
    if generated:
        lines.append("### Contract Test Deliverables")
        lines.append("")
        lines.append(f"**Generated**: {len(generated)} contract_test deliverables")
        lines.append("")
        for d in generated:
            lines.append(f"- `{d.id}`: {d.description[:80]}...")
        lines.append("")

    return "\n".join(lines)
