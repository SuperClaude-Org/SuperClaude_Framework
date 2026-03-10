"""Budget realism caveats for dry-run and report outputs.

Implements T04.09 / D-0035 / AC19: adds estimation methodology limitations
and expected variance range to budget estimates.
"""

from __future__ import annotations

from typing import Any

BUDGET_CAVEAT = (
    "Budget estimates are based on file count heuristics and average token-per-file "
    "assumptions. Actual token usage may vary by 20-50% depending on file sizes, "
    "complexity distribution, and analysis depth. These estimates should be used "
    "for planning purposes only and are not guarantees of resource consumption."
)

ESTIMATION_METHODOLOGY = (
    "Estimation methodology: token count = file_count * avg_tokens_per_file "
    "(default: 500 tokens). Runtime = batch_count * avg_seconds_per_batch "
    "(default: 5s). Both heuristics are derived from historical audit runs "
    "on medium-sized repositories (100-500 files)."
)

VARIANCE_RANGE = "Expected variance: +/- 20-50% of estimated values."


def add_caveat_to_dry_run(dry_run_output: dict[str, Any]) -> dict[str, Any]:
    """Add budget realism caveat section to dry-run output.

    Args:
        dry_run_output: Dict from DryRunEstimate.to_dict().

    Returns:
        Updated dict with caveat section appended.
    """
    result = dict(dry_run_output)
    result["budget_realism_caveat"] = {
        "caveat": BUDGET_CAVEAT,
        "estimation_methodology": ESTIMATION_METHODOLOGY,
        "variance_range": VARIANCE_RANGE,
    }
    return result


def add_caveat_to_report(report_output: dict[str, Any]) -> dict[str, Any]:
    """Add budget realism caveat section to final report budget section.

    Args:
        report_output: Report dict that may contain budget info.

    Returns:
        Updated dict with caveat section in budget area.
    """
    result = dict(report_output)
    result["budget_realism_caveat"] = {
        "caveat": BUDGET_CAVEAT,
        "estimation_methodology": ESTIMATION_METHODOLOGY,
        "variance_range": VARIANCE_RANGE,
    }
    return result
