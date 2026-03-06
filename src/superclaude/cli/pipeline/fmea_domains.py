"""FMEA input domain enumerator -- generates degenerate test domains for computations.

For each computational deliverable, generates up to 8 input domains
prioritizing degenerate cases (empty, zero, null, boundary).

R-007 mitigation: 8-domain limit prevents combinatorial explosion.
Configurable via max_domains parameter (maps to --max-fmea-domains).

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .deliverables import is_behavioral
from .models import Deliverable


class DomainCategory(Enum):
    """Input domain categories ordered by priority (degenerate first)."""
    EMPTY = "empty"
    NULL = "null"
    ZERO = "zero"
    NEGATIVE = "negative"
    SINGLE = "single_element"
    DUPLICATE = "duplicate"
    OUT_OF_ORDER = "out_of_order"
    NORMAL = "normal"
    MAXIMUM = "maximum_size"
    FILTER_ALL = "filter_removes_all"
    FILTER_NONE = "filter_removes_none"


@dataclass
class InputDomain:
    """A single input domain for FMEA analysis."""
    category: DomainCategory
    description: str


# Domain generation rules keyed by computational verb patterns
_DOMAIN_RULES: dict[str, list[DomainCategory]] = {
    "filter": [
        DomainCategory.NORMAL, DomainCategory.EMPTY,
        DomainCategory.FILTER_ALL, DomainCategory.FILTER_NONE,
        DomainCategory.SINGLE, DomainCategory.NULL,
        DomainCategory.DUPLICATE, DomainCategory.MAXIMUM,
    ],
    "count": [
        DomainCategory.NORMAL, DomainCategory.ZERO,
        DomainCategory.SINGLE, DomainCategory.MAXIMUM,
        DomainCategory.EMPTY, DomainCategory.NEGATIVE,
        DomainCategory.DUPLICATE, DomainCategory.NULL,
    ],
    "compute": [
        DomainCategory.NORMAL, DomainCategory.ZERO,
        DomainCategory.NEGATIVE, DomainCategory.EMPTY,
        DomainCategory.SINGLE, DomainCategory.MAXIMUM,
        DomainCategory.NULL, DomainCategory.OUT_OF_ORDER,
    ],
    "aggregate": [
        DomainCategory.NORMAL, DomainCategory.EMPTY,
        DomainCategory.SINGLE, DomainCategory.ZERO,
        DomainCategory.MAXIMUM, DomainCategory.DUPLICATE,
        DomainCategory.NULL, DomainCategory.NEGATIVE,
    ],
    "_default": [
        DomainCategory.NORMAL, DomainCategory.EMPTY,
        DomainCategory.NULL, DomainCategory.ZERO,
        DomainCategory.NEGATIVE, DomainCategory.SINGLE,
        DomainCategory.MAXIMUM, DomainCategory.DUPLICATE,
    ],
}

# Human-readable domain descriptions
_DOMAIN_DESCRIPTIONS: dict[DomainCategory, str] = {
    DomainCategory.EMPTY: "Empty input collection/string",
    DomainCategory.NULL: "Null/None input value",
    DomainCategory.ZERO: "Zero numeric input",
    DomainCategory.NEGATIVE: "Negative numeric input",
    DomainCategory.SINGLE: "Single-element input",
    DomainCategory.DUPLICATE: "Input with duplicate values",
    DomainCategory.OUT_OF_ORDER: "Unsorted/out-of-order input",
    DomainCategory.NORMAL: "Normal/typical input",
    DomainCategory.MAXIMUM: "Maximum-size input (boundary)",
    DomainCategory.FILTER_ALL: "Filter predicate removes all elements",
    DomainCategory.FILTER_NONE: "Filter predicate removes no elements",
}

# Default max domains per computation
DEFAULT_MAX_DOMAINS = 8


def enumerate_input_domains(
    deliverable: Deliverable,
    max_domains: int = DEFAULT_MAX_DOMAINS,
) -> list[InputDomain]:
    """Generate input domains for a single deliverable.

    Returns empty list for non-computational deliverables.
    Returns up to max_domains domains with degenerate cases prioritized.
    """
    if not is_behavioral(deliverable.description):
        return []

    desc_lower = deliverable.description.lower()

    # Find the best matching verb-specific rule
    categories = _select_domains(desc_lower)

    # Cap at max_domains
    categories = categories[:max_domains]

    return [
        InputDomain(
            category=cat,
            description=_DOMAIN_DESCRIPTIONS.get(cat, cat.value),
        )
        for cat in categories
    ]


def enumerate_all_domains(
    deliverables: list[Deliverable],
    max_domains: int = DEFAULT_MAX_DOMAINS,
) -> dict[str, list[InputDomain]]:
    """Generate input domains for all computational deliverables.

    Returns dict mapping deliverable_id -> domain list.
    Non-computational deliverables get empty lists.
    """
    result: dict[str, list[InputDomain]] = {}
    for d in deliverables:
        domains = enumerate_input_domains(d, max_domains=max_domains)
        if domains:
            result[d.id] = domains
    return result


def _select_domains(desc_lower: str) -> list[DomainCategory]:
    """Select domain categories based on computational verb in description."""
    for verb, categories in _DOMAIN_RULES.items():
        if verb == "_default":
            continue
        if verb in desc_lower:
            return list(categories)
    return list(_DOMAIN_RULES["_default"])
