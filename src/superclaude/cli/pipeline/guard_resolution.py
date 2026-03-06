"""Guard resolution -- generates guard_test deliverables and Release Gate Rule 2 enforcement.

For each ambiguous guard detected by the guard analyzer:
1. Generates guard_test deliverables requiring:
   - Semantic documentation of every guard value
   - Uniqueness test (each semantic state maps to exactly one value)
   - Type transition mapping (pre-transition states → post-transition equivalents)
2. Release Gate Rule 2: unresolved ambiguity → blocking warning with mandatory owner + review date

R-011 mitigation: Release Gate Rule 2 is blocking, not advisory.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .guard_analyzer import GuardDetection, TypeTransitionKind
from .models import Deliverable, DeliverableKind


@dataclass
class AcceptedRisk:
    """Accepted risk for guard ambiguity, requiring non-empty rationale and owner."""
    owner: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.owner or not self.owner.strip():
            raise ValueError("Accepted risk requires non-empty owner name")
        if not self.rationale or not self.rationale.strip():
            raise ValueError("Accepted risk requires non-empty rationale string")


@dataclass
class ReleaseGateWarning:
    """Release Gate Rule 2 warning for unresolved guard ambiguity.

    Blocking: pipeline must not advance without owner assignment.
    """
    guard_variable: str
    deliverable_id: str
    message: str
    owner: str = ""
    review_date: str = ""
    accepted_risk: AcceptedRisk | None = None

    @property
    def is_resolved(self) -> bool:
        """Warning is resolved if owner is assigned or risk is accepted."""
        return bool(self.owner and self.owner.strip()) or self.accepted_risk is not None

    @property
    def is_blocking(self) -> bool:
        """Unresolved warnings block pipeline advancement."""
        return not self.is_resolved


@dataclass
class GuardResolutionOutput:
    """Output of the guard resolution pass.

    Attributes:
        guard_test_deliverables: Generated guard_test deliverables.
        gate_warnings: Release Gate Rule 2 warnings.
        section_markdown: Rendered markdown section.
    """
    guard_test_deliverables: list[Deliverable] = field(default_factory=list)
    gate_warnings: list[ReleaseGateWarning] = field(default_factory=list)
    section_markdown: str = ""

    @property
    def has_blocking_warnings(self) -> bool:
        """True if any gate warning is unresolved."""
        return any(w.is_blocking for w in self.gate_warnings)

    @property
    def can_advance(self) -> bool:
        """Pipeline can advance only if no blocking warnings exist."""
        return not self.has_blocking_warnings


def resolve_guards(
    detections: list[GuardDetection],
) -> GuardResolutionOutput:
    """Generate guard_test deliverables and Release Gate Rule 2 warnings.

    For each ambiguous guard:
    - Generates semantic documentation deliverable
    - Generates uniqueness test deliverable
    - If type transition: generates transition mapping deliverable
    - Creates Release Gate Rule 2 warning with mandatory owner

    Non-ambiguous guards produce no deliverables and no warnings.
    Suppressed guards produce no deliverables and no warnings.
    """
    deliverables: list[Deliverable] = []
    warnings: list[ReleaseGateWarning] = []
    seq = 0

    for detection in detections:
        # Skip non-ambiguous guards
        if not detection.has_ambiguity:
            continue

        # Skip suppressed guards
        if detection.suppressed:
            continue

        # Generate guard_test deliverables
        seq += 1

        # 1. Semantic documentation deliverable
        sem_doc = Deliverable(
            id=f"GT-{seq:04d}.sem",
            description=(
                f"Guard test: document every value of '{detection.guard_variable}' "
                f"with its semantic meaning. "
                f"States: {_format_states(detection)}"
            ),
            kind=DeliverableKind.GUARD_TEST,
            metadata={
                "guard_variable": detection.guard_variable,
                "deliverable_id": detection.deliverable_id,
                "test_type": "semantic_documentation",
            },
        )
        deliverables.append(sem_doc)

        # 2. Uniqueness test deliverable
        uniq_test = Deliverable(
            id=f"GT-{seq:04d}.uniq",
            description=(
                f"Guard test: verify each semantic state of '{detection.guard_variable}' "
                f"maps to exactly one value. Ambiguous value(s): "
                f"{_format_ambiguous_values(detection)}"
            ),
            kind=DeliverableKind.GUARD_TEST,
            metadata={
                "guard_variable": detection.guard_variable,
                "deliverable_id": detection.deliverable_id,
                "test_type": "uniqueness",
            },
        )
        deliverables.append(uniq_test)

        # 3. Type transition mapping (if applicable)
        if detection.type_transition is not None:
            trans_test = Deliverable(
                id=f"GT-{seq:04d}.trans",
                description=(
                    f"Guard test: verify all pre-transition semantic states of "
                    f"'{detection.guard_variable}' ({detection.type_transition.value}) "
                    f"have post-transition equivalents"
                ),
                kind=DeliverableKind.GUARD_TEST,
                metadata={
                    "guard_variable": detection.guard_variable,
                    "deliverable_id": detection.deliverable_id,
                    "test_type": "transition_mapping",
                    "transition_kind": detection.type_transition.value,
                },
            )
            deliverables.append(trans_test)

        # Release Gate Rule 2: warning for unresolved ambiguity
        warning = ReleaseGateWarning(
            guard_variable=detection.guard_variable,
            deliverable_id=detection.deliverable_id,
            message=(
                f"Unresolved guard ambiguity for '{detection.guard_variable}' "
                f"in {detection.deliverable_id}. "
                f"Ambiguous values: {_format_ambiguous_values(detection)}. "
                f"Requires owner assignment and review date."
            ),
        )
        warnings.append(warning)

    section = _render_resolution_section(deliverables, warnings)

    return GuardResolutionOutput(
        guard_test_deliverables=deliverables,
        gate_warnings=warnings,
        section_markdown=section,
    )


def _format_states(detection: GuardDetection) -> str:
    """Format state enumeration for display."""
    parts = []
    for state in detection.states:
        meanings = ", ".join(m.meaning for m in state.semantic_meanings)
        parts.append(f"{state.value}=[{meanings}]")
    return "; ".join(parts)


def _format_ambiguous_values(detection: GuardDetection) -> str:
    """Format only the ambiguous values for display."""
    parts = []
    for state in detection.states:
        if state.is_ambiguous:
            meanings = ", ".join(m.meaning for m in state.semantic_meanings)
            parts.append(f"{state.value}=[{meanings}]")
    return "; ".join(parts) or "none"


def _render_resolution_section(
    deliverables: list[Deliverable],
    warnings: list[ReleaseGateWarning],
) -> str:
    """Render guard resolution as markdown."""
    lines = ["## Guard Resolution", ""]

    if not deliverables and not warnings:
        lines.append("No guard ambiguity detected. No resolution required.")
        return "\n".join(lines)

    lines.append(f"**Guard test deliverables generated**: {len(deliverables)}")
    lines.append(f"**Release gate warnings**: {len(warnings)}")
    blocking = sum(1 for w in warnings if w.is_blocking)
    if blocking:
        lines.append(f"**BLOCKING**: {blocking} unresolved warning(s) — pipeline cannot advance")
    lines.append("")

    if deliverables:
        lines.append("### Guard Test Deliverables")
        lines.append("")
        lines.append("| ID | Type | Variable | Description |")
        lines.append("|----|------|----------|-------------|")
        for d in deliverables:
            test_type = d.metadata.get("test_type", "unknown")
            var = d.metadata.get("guard_variable", "?")
            lines.append(f"| {d.id} | {test_type} | `{var}` | {d.description[:80]}... |")
        lines.append("")

    if warnings:
        lines.append("### Release Gate Rule 2 Warnings")
        lines.append("")
        for w in warnings:
            status = "RESOLVED" if w.is_resolved else "BLOCKING"
            lines.append(f"- [{status}] {w.message}")
        lines.append("")

    return "\n".join(lines)
