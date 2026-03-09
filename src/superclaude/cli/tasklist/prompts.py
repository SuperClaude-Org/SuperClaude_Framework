"""Tasklist prompt builders -- pure functions returning prompt strings.

All functions are pure: they accept concrete values, return ``str``,
and perform no I/O, subprocess calls, or side effects (NFR-004).

Validation layering guard: tasklist fidelity checks roadmap→tasklist ONLY.
It does NOT check spec→tasklist (that is the spec-fidelity step's job).
"""

from __future__ import annotations

from pathlib import Path

from superclaude.cli.roadmap.prompts import _OUTPUT_FORMAT_BLOCK


def build_tasklist_fidelity_prompt(
    roadmap_file: Path,
    tasklist_dir: Path,
) -> str:
    """Prompt for the tasklist-fidelity validation step.

    Instructs Claude to compare the roadmap against the generated tasklist,
    checking deliverable coverage, signature preservation, traceability ID
    validity, and dependency chain correctness.

    VALIDATION LAYERING GUARD: This prompt validates roadmap→tasklist
    alignment ONLY. Spec→tasklist validation is NOT in scope here;
    that is handled by the spec-fidelity step in the roadmap pipeline.

    Embeds explicit severity definitions (HIGH/MEDIUM/LOW) to reduce
    LLM classification drift (RSK-007). Reuses the deviation report
    format from Phase 2 (docs/reference/deviation-report-format.md).
    """
    return (
        "You are a tasklist fidelity analyst.\n\n"
        "Read the provided roadmap file and the generated tasklist files. "
        "Compare them systematically to identify deviations where the tasklist "
        "diverges from or omits requirements in the roadmap.\n\n"
        "## VALIDATION LAYERING GUARD\n\n"
        "IMPORTANT: You are validating ROADMAP → TASKLIST alignment ONLY.\n"
        "Do NOT compare the tasklist against the original specification.\n"
        "Do NOT check whether the roadmap itself is faithful to the spec.\n"
        "Those checks are handled by a separate spec-fidelity step.\n"
        "Your SOLE concern is whether the tasklist accurately reflects the roadmap.\n\n"
        "## Severity Definitions\n\n"
        "Apply these severity classifications precisely:\n\n"
        "**HIGH**: The tasklist omits, contradicts, or fundamentally misrepresents "
        "a roadmap item. The tasklist cannot be used as-is for execution. Examples:\n"
        "- A roadmap item (R-NNN) has no corresponding task in the tasklist\n"
        "- A deliverable ID (D-NNNN) appears in the tasklist but does not exist "
        "in the roadmap (fabricated traceability)\n"
        "- A dependency chain in the tasklist contradicts the roadmap's ordering\n"
        "- A task's deliverables omit outputs specified in the roadmap item\n\n"
        "**MEDIUM**: The tasklist addresses the roadmap item but with insufficient "
        "detail, ambiguous language, or minor misalignment that could lead to "
        "execution issues. Examples:\n"
        "- A task's effort estimate diverges significantly from the roadmap\n"
        "- Acceptance criteria are weaker than the roadmap's success criteria\n"
        "- A dependency is acknowledged but not properly sequenced\n"
        "- Verification method differs from roadmap recommendation\n\n"
        "**LOW**: Minor stylistic, formatting, or organizational differences that "
        "do not affect execution correctness. Examples:\n"
        "- Different heading structure or section ordering\n"
        "- Terminology variations that don't change meaning\n"
        "- Missing cross-references that don't affect understanding\n\n"
        "## Comparison Dimensions\n\n"
        "Compare across ALL of these dimensions:\n"
        "1. **Deliverable Coverage**: Every roadmap deliverable (D-NNNN) has a "
        "corresponding task with matching deliverable IDs\n"
        "2. **Signature Preservation**: Function/method/API signatures from the "
        "roadmap are preserved in task descriptions and acceptance criteria\n"
        "3. **Traceability ID Validity**: Every Roadmap Item ID (R-NNN) and "
        "Deliverable ID (D-NNNN) in the tasklist traces back to the roadmap. "
        "Flag fabricated IDs that do not exist in the roadmap.\n"
        "4. **Dependency Chain Correctness**: Task dependencies match the "
        "roadmap's sequencing and prerequisites\n"
        "5. **Acceptance Criteria Completeness**: Task acceptance criteria "
        "cover all success criteria from the corresponding roadmap items\n\n"
        "## Output Requirements\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- source_pair: roadmap-to-tasklist\n"
        "- upstream_file: (string) the roadmap filename\n"
        "- downstream_file: (string) the tasklist directory path\n"
        "- high_severity_count: (integer) number of HIGH severity deviations\n"
        "- medium_severity_count: (integer) number of MEDIUM severity deviations\n"
        "- low_severity_count: (integer) number of LOW severity deviations\n"
        "- total_deviations: (integer) total number of deviations found\n"
        "- validation_complete: (boolean) true if analysis completed fully\n"
        "- tasklist_ready: (boolean) true ONLY if high_severity_count is 0 AND "
        "validation_complete is true\n\n"
        "After the frontmatter, provide:\n\n"
        "## Deviation Report\n\n"
        "For each deviation, provide a numbered entry with:\n"
        "- **ID**: DEV-NNN (zero-padded 3-digit)\n"
        "- **Severity**: HIGH, MEDIUM, or LOW\n"
        "- **Deviation**: Concise description of what differs\n"
        "- **Upstream Quote**: Verbatim quote from the roadmap\n"
        "- **Downstream Quote**: Verbatim quote from the tasklist, or '[MISSING]' if absent\n"
        "- **Impact**: Assessment of how the deviation affects execution correctness\n"
        "- **Recommended Correction**: Specific action to resolve the deviation\n\n"
        "## Summary\n\n"
        "Provide a brief summary of findings with severity distribution.\n\n"
        "Be thorough and precise. Quote both documents for every deviation. "
        "Do not invent deviations -- only report genuine differences between "
        "the roadmap and tasklist."
    ) + _OUTPUT_FORMAT_BLOCK
