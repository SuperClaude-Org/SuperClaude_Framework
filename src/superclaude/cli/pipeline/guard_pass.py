"""Guard analysis pipeline pass -- post-M2 analytical pass for conditional logic.

Runs after M2 combined pass (invariant registry + FMEA), cross-references:
- Invariant predicates: verifies guard variables have registered invariants
- FMEA severity: determines if guard ambiguity elevation to silent corruption is warranted

Output: guard analysis section with state enumeration tables, ambiguity flags,
guard_test deliverables in correct milestones, and gate warnings.

Pipeline order: decomposition (M1) -> invariant+FMEA (M2) -> guard analysis (M3) -> data flow (M4).

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .guard_analyzer import GuardDetection, detect_guards
from .guard_resolution import GuardResolutionOutput, ReleaseGateWarning, resolve_guards
from .invariant_pass import InvariantRegistryOutput
from .invariants import InvariantEntry
from .models import Deliverable, DeliverableKind


@dataclass
class GuardAnalysisOutput:
    """Output of the M3 guard analysis pipeline pass.

    Attributes:
        detections: All guard detections from the analyzer.
        resolution: Guard resolution output (deliverables + gate warnings).
        invariant_cross_refs: Map of guard variable -> matched InvariantEntry (if any).
        fmea_elevations: Guard variables elevated to silent corruption severity.
        section_markdown: Rendered markdown section for pipeline output.
        can_advance_to_m4: False if Release Gate Rule 2 blocks advancement.
    """
    detections: list[GuardDetection] = field(default_factory=list)
    resolution: GuardResolutionOutput = field(default_factory=GuardResolutionOutput)
    invariant_cross_refs: dict[str, InvariantEntry | None] = field(default_factory=dict)
    fmea_elevations: list[str] = field(default_factory=list)
    section_markdown: str = ""

    @property
    def can_advance_to_m4(self) -> bool:
        """Pipeline can advance to M4 only if no blocking gate warnings."""
        return self.resolution.can_advance


def run_guard_analysis_pass(
    deliverables: list[Deliverable],
    invariant_output: InvariantRegistryOutput | None = None,
    fmea_severity_map: dict[str, str] | None = None,
) -> GuardAnalysisOutput:
    """Execute the M3 guard analysis pipeline pass.

    Pipeline position: after M2 combined pass (invariant registry + FMEA).

    Args:
        deliverables: All deliverables (including M1 decomposed).
        invariant_output: Output from M2 invariant registry pass (for cross-ref).
        fmea_severity_map: Map of deliverable_id -> FMEA severity level (for elevation).

    Returns:
        GuardAnalysisOutput with detections, resolution, cross-references, and section.
    """
    if invariant_output is None:
        invariant_output = InvariantRegistryOutput()
    if fmea_severity_map is None:
        fmea_severity_map = {}

    # Step 1: Detect guards from deliverables
    detections = detect_guards(deliverables)

    if not detections:
        return GuardAnalysisOutput(
            section_markdown=_render_empty_section(),
        )

    # Step 2: Cross-reference with invariant predicates
    invariant_cross_refs = _cross_reference_invariants(
        detections, invariant_output.entries,
    )

    # Step 3: Check FMEA severity for elevation to silent corruption
    fmea_elevations = _check_fmea_elevation(detections, fmea_severity_map)

    # Step 4: Resolve guards (generate deliverables + gate warnings)
    resolution = resolve_guards(detections)

    # Step 5: Render section
    section = _render_guard_analysis_section(
        detections, resolution, invariant_cross_refs, fmea_elevations,
    )

    return GuardAnalysisOutput(
        detections=detections,
        resolution=resolution,
        invariant_cross_refs=invariant_cross_refs,
        fmea_elevations=fmea_elevations,
        section_markdown=section,
    )


def _cross_reference_invariants(
    detections: list[GuardDetection],
    invariant_entries: list[InvariantEntry],
) -> dict[str, InvariantEntry | None]:
    """Cross-reference guard variables with invariant registry entries.

    Returns map of guard_variable -> InvariantEntry (or None if no match).
    """
    # Build lookup by variable name
    entry_lookup: dict[str, InvariantEntry] = {}
    for entry in invariant_entries:
        entry_lookup[entry.variable_name] = entry
        # Also check without leading underscore
        stripped = entry.variable_name.lstrip("_")
        if stripped:
            entry_lookup[stripped] = entry

    result: dict[str, InvariantEntry | None] = {}
    for detection in detections:
        var = detection.guard_variable
        match = entry_lookup.get(var) or entry_lookup.get(var.lstrip("_"))
        result[var] = match

    return result


def _check_fmea_elevation(
    detections: list[GuardDetection],
    fmea_severity_map: dict[str, str],
) -> list[str]:
    """Check if guard ambiguity should be elevated to silent corruption.

    Elevation occurs when:
    - Guard has ambiguity
    - Source deliverable has FMEA severity >= "high"
    """
    elevations: list[str] = []
    high_severities = {"high", "critical"}

    for detection in detections:
        if not detection.has_ambiguity:
            continue
        severity = fmea_severity_map.get(detection.deliverable_id, "").lower()
        if severity in high_severities:
            elevations.append(detection.guard_variable)

    return elevations


def _render_empty_section() -> str:
    return "## Guard Analysis\n\nNo guard patterns detected.\n"


def _render_guard_analysis_section(
    detections: list[GuardDetection],
    resolution: GuardResolutionOutput,
    invariant_cross_refs: dict[str, InvariantEntry | None],
    fmea_elevations: list[str],
) -> str:
    """Render the guard analysis section as markdown."""
    lines = ["## Guard Analysis", ""]
    lines.append(f"**Guards detected**: {len(detections)}")
    ambiguous_count = sum(1 for d in detections if d.has_ambiguity)
    lines.append(f"**Ambiguous guards**: {ambiguous_count}")
    lines.append(f"**FMEA elevations**: {len(fmea_elevations)}")
    lines.append("")

    # State enumeration table
    lines.append("### State Enumeration")
    lines.append("")
    lines.append("| Variable | Kind | States | Ambiguous | Invariant Registered | FMEA Elevated |")
    lines.append("|----------|------|--------|-----------|---------------------|---------------|")
    for det in detections:
        states_str = ", ".join(s.value for s in det.states)
        ambig = "YES" if det.has_ambiguity else "no"
        inv_ref = invariant_cross_refs.get(det.guard_variable)
        has_inv = "YES" if inv_ref else "no"
        elevated = "YES" if det.guard_variable in fmea_elevations else "no"
        lines.append(
            f"| `{det.guard_variable}` | {det.guard_kind.value} | {states_str} | "
            f"{ambig} | {has_inv} | {elevated} |"
        )
    lines.append("")

    # Append resolution section
    if resolution.section_markdown:
        lines.append(resolution.section_markdown)

    # Gate status
    if resolution.has_blocking_warnings:
        lines.append("")
        lines.append("### Release Gate Rule 2: BLOCKING")
        lines.append("")
        lines.append("Pipeline cannot advance to M4. Unresolved guard ambiguity requires owner assignment.")

    return "\n".join(lines)
