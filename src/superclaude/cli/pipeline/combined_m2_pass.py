"""Combined invariant registry + FMEA pipeline pass (M2).

Merges invariant registry (state variable detection, mutation inventory, verification
emitter) with FMEA (domain enumeration, failure classification, deliverable promotion)
into a single analytical pass with shared scanning infrastructure.

Cross-links invariant entries to fmea_test deliverables. Idempotent.

Pipeline position: after M1 decomposition, before M3 guard analysis.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .fmea_classifier import (
    DetectionDifficulty,
    FMEAFailureMode,
    Severity,
    classify_failure_modes,
)
from .fmea_domains import enumerate_all_domains
from .fmea_promotion import (
    FMEAPromotionOutput,
    ReleaseGateViolation,
    promote_failure_modes,
)
from .invariant_pass import InvariantRegistryOutput, run_invariant_registry_pass
from .invariants import InvariantEntry
from .models import Deliverable, DeliverableKind


@dataclass
class CombinedM2Output:
    """Output of the combined M2 invariant registry + FMEA pipeline pass.

    Attributes:
        invariant_output: Output from the invariant registry sub-pass.
        failure_modes: Classified FMEA failure modes.
        promotion_output: FMEA deliverable promotion results.
        all_generated_deliverables: Union of invariant_check + fmea_test deliverables.
        section_markdown: Combined markdown section for pipeline output.
        has_blocking_violations: True if Release Gate Rule 1 violations exist.
    """

    invariant_output: InvariantRegistryOutput = field(
        default_factory=InvariantRegistryOutput
    )
    failure_modes: list[FMEAFailureMode] = field(default_factory=list)
    promotion_output: FMEAPromotionOutput = field(default_factory=FMEAPromotionOutput)
    all_generated_deliverables: list[Deliverable] = field(default_factory=list)
    section_markdown: str = ""

    @property
    def has_blocking_violations(self) -> bool:
        return self.promotion_output.has_blocking_violations

    @property
    def release_gate_violations(self) -> list[ReleaseGateViolation]:
        return self.promotion_output.release_gate_violations


def run_combined_m2_pass(
    deliverables: list[Deliverable],
    max_checks_per_variable: int = 5,
    max_fmea_domains: int = 8,
    promotion_threshold: Severity = Severity.WRONG_STATE,
) -> CombinedM2Output:
    """Execute the combined M2 analytical pass.

    Pipeline:
    1. Shared scanning: filter deliverables by kind
    2. Invariant registry sub-pass: detect, inventory, emit verification deliverables
    3. FMEA sub-pass: enumerate domains, classify failures, promote
    4. Cross-link: connect invariant entries to fmea_test deliverables
    5. Render combined section

    Idempotent: filters out previously generated invariant_check and fmea_test
    deliverables before processing.

    Args:
        deliverables: All deliverables from M1 decomposition.
        max_checks_per_variable: Cap for invariant_check deliverables per variable.
        max_fmea_domains: Maximum input domains per computation.
        promotion_threshold: Severity threshold for FMEA promotion.

    Returns:
        CombinedM2Output with all results and combined section.
    """
    # Idempotency: filter out previously generated M2 deliverables
    source_deliverables = [
        d for d in deliverables
        if d.kind not in (DeliverableKind.INVARIANT_CHECK, DeliverableKind.FMEA_TEST)
    ]

    # --- Invariant Registry Sub-Pass ---
    invariant_output = run_invariant_registry_pass(
        source_deliverables,
        max_checks_per_variable=max_checks_per_variable,
    )

    # --- FMEA Sub-Pass ---
    # Step 1: Enumerate input domains for computational deliverables
    domain_map = enumerate_all_domains(source_deliverables, max_domains=max_fmea_domains)

    # Step 2: Classify failure modes using dual-signal detection
    failure_modes = classify_failure_modes(
        source_deliverables,
        domain_map,
        invariant_entries=invariant_output.entries,
    )

    # Step 3: Promote above-threshold failure modes
    promotion_output = promote_failure_modes(
        failure_modes,
        promotion_threshold=promotion_threshold,
    )

    # --- Cross-Linking ---
    _cross_link_invariant_to_fmea(
        invariant_output.entries,
        promotion_output.promoted_deliverables,
    )

    # --- Combine Generated Deliverables ---
    all_generated = (
        list(invariant_output.generated_deliverables)
        + list(promotion_output.promoted_deliverables)
    )

    # --- Render Combined Section ---
    section = _render_combined_section(
        invariant_output, failure_modes, promotion_output,
    )

    return CombinedM2Output(
        invariant_output=invariant_output,
        failure_modes=failure_modes,
        promotion_output=promotion_output,
        all_generated_deliverables=all_generated,
        section_markdown=section,
    )


def _cross_link_invariant_to_fmea(
    entries: list[InvariantEntry],
    fmea_deliverables: list[Deliverable],
) -> None:
    """Cross-link invariant entries to corresponding fmea_test deliverables.

    Adds fmea_test deliverable IDs to InvariantEntry metadata (in-place).
    """
    for entry in entries:
        linked_fmea_ids = []
        for d in fmea_deliverables:
            source_id = d.metadata.get("source_deliverable_id", "")
            invariant_pred = d.metadata.get("invariant_predicate", "")

            # Link if the fmea_test references a deliverable in this entry's mutation sites
            mutation_ids = {ms.deliverable_id for ms in entry.mutation_sites}
            if source_id in mutation_ids or invariant_pred == entry.invariant_predicate:
                linked_fmea_ids.append(d.id)

        if linked_fmea_ids:
            # Store cross-link in the entry's verification_deliverable_ids
            for fid in linked_fmea_ids:
                if fid not in entry.verification_deliverable_ids:
                    entry.verification_deliverable_ids.append(fid)


def _render_combined_section(
    invariant_output: InvariantRegistryOutput,
    failure_modes: list[FMEAFailureMode],
    promotion_output: FMEAPromotionOutput,
) -> str:
    """Render combined M2 section as markdown."""
    lines = ["## M2: State Variable Invariant Registry and FMEA Analysis", ""]

    # Invariant registry subsection
    lines.append(invariant_output.section_markdown)
    lines.append("")

    # FMEA failure modes table
    if failure_modes:
        lines.append("### FMEA Failure Mode Table")
        lines.append("")
        lines.append("| Deliverable | Domain | Detection | Severity | Signal |")
        lines.append("|-------------|--------|-----------|----------|--------|")
        for fm in failure_modes:
            lines.append(
                f"| {fm.deliverable_id} | {fm.domain_description} | "
                f"{fm.detection_difficulty.value} | {fm.severity.value} | "
                f"{fm.signal_source} |"
            )
        lines.append("")

    # Promotion section
    lines.append(promotion_output.section_markdown)

    return "\n".join(lines)
