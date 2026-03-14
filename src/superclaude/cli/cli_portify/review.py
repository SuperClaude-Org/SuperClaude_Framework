"""User review gate module for cli-portify pipeline.

Provides centralized review gate logic that pauses execution and
prompts the user on stderr. Supports --skip-review bypass for CI/CD.

Review gate insertion points:
- After design-pipeline (Step 4)
- After panel-review (Step 7)

Per D-0036 / R-025: User review gates with --skip-review bypass.
"""

from __future__ import annotations

import sys
from enum import Enum


class ReviewDecision(Enum):
    """Result of a review gate prompt."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SKIPPED = "skipped"


# Review gate insertion points (step names where review is required)
REVIEW_GATE_STEPS = ("design-pipeline", "panel-review")


def prompt_review(
    step_name: str,
    artifact_path: str,
    skip_review: bool = False,
) -> ReviewDecision:
    """Prompt user for review gate approval.

    Pauses pipeline execution and prompts on stderr. If the user
    responds 'y' or 'yes', returns ACCEPTED. If 'n' or anything
    else, returns REJECTED. If --skip-review is set, auto-accepts
    without prompting.

    Args:
        step_name: Name of the step requesting review.
        artifact_path: Path to the artifact for review.
        skip_review: If True, bypass all prompts and auto-accept.

    Returns:
        ReviewDecision indicating user's choice.
    """
    if skip_review:
        return ReviewDecision.SKIPPED

    print(
        f"\n[REVIEW GATE] Step '{step_name}' produced: {artifact_path}\n"
        "Review the output and confirm to proceed.\n"
        "Continue? [y/N]: ",
        file=sys.stderr,
        end="",
        flush=True,
    )

    try:
        response = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return ReviewDecision.REJECTED

    if response in ("y", "yes"):
        return ReviewDecision.ACCEPTED
    return ReviewDecision.REJECTED


def is_review_step(step_name: str) -> bool:
    """Check if a step requires a review gate."""
    return step_name in REVIEW_GATE_STEPS


def review_gate(
    step_name: str,
    artifact_path: str,
    skip_review: bool = False,
) -> tuple[bool, ReviewDecision]:
    """Execute a review gate for the given step.

    Combines step check and prompt in one call. If the step does not
    require review, returns (True, SKIPPED). Otherwise prompts and
    returns the outcome.

    Args:
        step_name: Name of the step.
        artifact_path: Path to the artifact for review.
        skip_review: If True, bypass all prompts.

    Returns:
        Tuple of (should_continue: bool, decision: ReviewDecision).
        should_continue is True for ACCEPTED or SKIPPED, False for REJECTED.
    """
    if not is_review_step(step_name):
        return True, ReviewDecision.SKIPPED

    decision = prompt_review(step_name, artifact_path, skip_review=skip_review)

    should_continue = decision in (ReviewDecision.ACCEPTED, ReviewDecision.SKIPPED)
    return should_continue, decision
