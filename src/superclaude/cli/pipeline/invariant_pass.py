"""Invariant registry pipeline pass -- post-decomposition analytical pass.

Runs after M1 decomposition, reads Implement deliverables, detects state
variables, generates invariant entries, emits verification deliverables,
and appends the invariant registry section to roadmap output.

Idempotent: running twice produces identical output.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .invariants import InvariantEntry, MutationSite, check_duplicate_variables
from .models import Deliverable, DeliverableKind
from .mutation_inventory import MutationInventoryResult, generate_mutation_inventory
from .state_detector import DetectionResult, detect_state_variables
from .verification_emitter import emit_invariant_check_deliverables


@dataclass
class InvariantRegistryOutput:
    """Output of the invariant registry pipeline pass.

    Attributes:
        entries: Generated InvariantEntry objects for each detected variable.
        generated_deliverables: New invariant_check deliverables to inject.
        warnings: Any duplicate variable warnings.
        section_markdown: Rendered markdown section for roadmap output.
    """
    entries: list[InvariantEntry] = field(default_factory=list)
    generated_deliverables: list[Deliverable] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    section_markdown: str = ""


def run_invariant_registry_pass(
    deliverables: list[Deliverable],
    max_checks_per_variable: int = 5,
) -> InvariantRegistryOutput:
    """Execute the invariant registry pipeline pass.

    Pipeline:
    1. Filter to Implement deliverables
    2. Detect state variables from descriptions
    3. Generate mutation inventory across all deliverables
    4. Build InvariantEntry objects with constrained predicates
    5. Emit verification deliverables
    6. Check for duplicate variables
    7. Render registry section markdown

    Idempotent: does not modify input deliverables. Already-generated
    invariant_check deliverables are filtered out before processing.
    """
    # Idempotency: filter out previously generated invariant_check deliverables
    source_deliverables = [
        d for d in deliverables
        if d.kind != DeliverableKind.INVARIANT_CHECK
    ]

    # Step 1: Focus on implement deliverables for detection
    implement_deliverables = [
        d for d in source_deliverables
        if d.kind == DeliverableKind.IMPLEMENT
    ]

    if not implement_deliverables:
        return InvariantRegistryOutput(section_markdown=_render_empty_section())

    # Step 2: Detect state variables
    detections = detect_state_variables(implement_deliverables)

    if not detections:
        return InvariantRegistryOutput(section_markdown=_render_empty_section())

    # Step 3: Generate mutation inventory (scan ALL deliverables)
    inventory = generate_mutation_inventory(detections, source_deliverables)

    # Step 4: Build InvariantEntry objects
    entries: list[InvariantEntry] = []
    for detection, inv_result in zip(detections, inventory):
        predicate = _generate_predicate(detection)
        try:
            entry = InvariantEntry(
                variable_name=detection.variable_name,
                scope=_infer_scope(detection),
                invariant_predicate=predicate,
                mutation_sites=inv_result.mutation_sites,
            )
            entries.append(entry)
        except ValueError:
            # Predicate didn't pass constrained grammar -- skip with warning
            pass

    if not entries:
        return InvariantRegistryOutput(section_markdown=_render_empty_section())

    # Step 5: Emit verification deliverables
    generated = emit_invariant_check_deliverables(
        inventory, entries, max_checks_per_variable=max_checks_per_variable,
    )

    # Step 6: Check for duplicates
    warnings = check_duplicate_variables(entries)

    # Step 7: Render section
    section = _render_registry_section(entries, generated)

    return InvariantRegistryOutput(
        entries=entries,
        generated_deliverables=generated,
        warnings=warnings,
        section_markdown=section,
    )


def _generate_predicate(detection: DetectionResult) -> str:
    """Generate a constrained grammar predicate for a detection.

    Uses simple heuristics based on introduction type.
    """
    var = detection.variable_name
    from .state_detector import IntroductionType

    type_predicates = {
        IntroductionType.COUNTER: f"{var} >= 0",
        IntroductionType.OFFSET: f"{var} >= 0",
        IntroductionType.CURSOR: f"{var} >= 0",
        IntroductionType.FLAG: f"{var} is not None",
        IntroductionType.SELF_ASSIGNMENT: f"{var} is not None",
        IntroductionType.REPLACEMENT: f"{var} is not None",
        IntroductionType.GENERIC: f"{var} is not None",
    }
    return type_predicates.get(detection.introduction_type, f"{var} is not None")


def _infer_scope(detection: DetectionResult) -> str:
    """Infer scope from detection context."""
    from .state_detector import IntroductionType

    if detection.introduction_type == IntroductionType.SELF_ASSIGNMENT:
        return "class-level"
    return "module-level"


def _render_empty_section() -> str:
    return "## Invariant Registry\n\nNo state variables detected.\n"


def _render_registry_section(
    entries: list[InvariantEntry],
    generated: list[Deliverable],
) -> str:
    """Render the invariant registry as a markdown section."""
    lines = ["## Invariant Registry", ""]
    lines.append(f"**Variables tracked**: {len(entries)}")
    lines.append(f"**Verification deliverables generated**: {len(generated)}")
    lines.append("")

    # Variable table
    lines.append("| Variable | Scope | Predicate | Mutation Sites | Verification IDs |")
    lines.append("|----------|-------|-----------|----------------|------------------|")
    for entry in entries:
        sites_str = ", ".join(ms.deliverable_id for ms in entry.mutation_sites)
        verif_str = ", ".join(entry.verification_deliverable_ids) or "none"
        lines.append(
            f"| `{entry.variable_name}` | {entry.scope} | "
            f"`{entry.invariant_predicate}` | {sites_str} | {verif_str} |"
        )

    lines.append("")
    return "\n".join(lines)
