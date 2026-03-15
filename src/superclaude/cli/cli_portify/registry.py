"""Step registration for the CLI Portify pipeline.

Enforces mandated module generation order per NFR-006 and AC-012.
The order is immutable at runtime (frozen tuple).

Mandated order:
    models → gates → prompts → config → inventory → monitor →
    process → executor → tui → logging_ → diagnostics → commands → __init__
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Mandated Module Generation Order (NFR-006, AC-012)
# ---------------------------------------------------------------------------

MANDATED_STEP_ORDER: tuple[str, ...] = (
    "models",
    "gates",
    "prompts",
    "config",
    "inventory",
    "monitor",
    "process",
    "executor",
    "tui",
    "logging_",
    "diagnostics",
    "commands",
    "__init__",
)

# Immutable at runtime: using a tuple prevents mutation.
# Any attempt to reassign or modify raises TypeError.


def get_step_order() -> tuple[str, ...]:
    """Return the immutable mandated step order."""
    return MANDATED_STEP_ORDER


def assert_step_order(steps: list[str]) -> None:
    """Assert that a list of step names matches the mandated order exactly.

    Raises AssertionError if the order does not match.
    """
    expected = list(MANDATED_STEP_ORDER)
    assert steps == expected, (
        f"Step order does not match mandated order.\n"
        f"Expected: {expected}\n"
        f"Got:      {steps}"
    )
