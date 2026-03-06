"""Validation output formatting with consistency-rate language.

Implements T04.03 / D-0029 / AC6 (quality extension): uses "consistency rate"
instead of "accuracy", includes calibration notes, states limitations.
"""

from __future__ import annotations

from typing import Any

from .spot_check import SpotCheckResult

# Calibration disclaimer
CALIBRATION_NOTES = (
    "Consistency rate measures self-agreement between the original classification "
    "and an independent re-classification using the same methodology. It does NOT "
    "measure ground-truth correctness. A high consistency rate indicates stable, "
    "reproducible classifications, but the underlying methodology itself has not "
    "been validated against human-expert judgement."
)

METHODOLOGY_LIMITATIONS = (
    "Limitations: (1) Re-classification uses the same heuristic engine — systematic "
    "biases in the engine are not detectable. (2) Sample is stratified but random — "
    "edge cases may not be represented. (3) Consistency is necessary but not sufficient "
    "for correctness."
)


def format_validation_report(result: SpotCheckResult) -> dict[str, Any]:
    """Format a spot-check result using consistency-rate language.

    Uses "consistency rate" throughout — never "accuracy".
    Includes calibration notes and methodology limitations.

    Args:
        result: SpotCheckResult from spot_check_validate.

    Returns:
        Formatted report dict with consistency-rate language.
    """
    per_tier_summary = []
    for tier_key, rate in sorted(result.per_tier_rates.items()):
        count = result.per_tier_sample_counts.get(tier_key, 0)
        per_tier_summary.append({
            "tier": tier_key,
            "consistency_rate": round(rate, 4),
            "sample_count": count,
        })

    return {
        "title": "Post-Consolidation Consistency Validation",
        "methodology": "Stratified 10% spot-check with independent re-classification",
        "overall_consistency_rate": round(result.overall_consistency_rate, 4),
        "sample_size": result.sample_size,
        "total_consolidated": result.total_consolidated,
        "per_tier_summary": per_tier_summary,
        "inconsistency_count": result.inconsistent_count,
        "inconsistencies": result.inconsistencies,
        "calibration_notes": CALIBRATION_NOTES,
        "methodology_limitations": METHODOLOGY_LIMITATIONS,
    }


def render_validation_text(result: SpotCheckResult) -> str:
    """Render a human-readable validation report in text format.

    Uses "consistency rate" language — never "accuracy".
    """
    lines = [
        "## Post-Consolidation Consistency Validation",
        "",
        f"**Overall Consistency Rate:** {result.overall_consistency_rate:.1%}",
        f"**Sample Size:** {result.sample_size} of {result.total_consolidated} "
        f"({result.sample_size / result.total_consolidated * 100:.1f}%)"
        if result.total_consolidated > 0 else
        f"**Sample Size:** {result.sample_size}",
        "",
        "### Per-Tier Consistency Rates",
        "",
    ]

    for tier_key in sorted(result.per_tier_rates.keys()):
        rate = result.per_tier_rates[tier_key]
        count = result.per_tier_sample_counts.get(tier_key, 0)
        lines.append(f"- **{tier_key}:** {rate:.1%} (n={count})")

    if result.inconsistencies:
        lines.extend([
            "",
            f"### Inconsistencies ({result.inconsistent_count})",
            "",
        ])
        for inc in result.inconsistencies:
            lines.append(
                f"- `{inc['file_path']}`: "
                f"{inc['original_tier']}/{inc['original_action']} -> "
                f"{inc['re_tier']}/{inc['re_action']}"
            )

    lines.extend([
        "",
        "### Calibration Notes",
        "",
        CALIBRATION_NOTES,
        "",
        METHODOLOGY_LIMITATIONS,
    ])

    return "\n".join(lines)
