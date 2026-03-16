#!/usr/bin/env python3
"""
improvement-backlog.md schema validator
Validates against /sc:roadmap ingestion schema per D-0030/spec.md

Required fields per improvement item (from D-0030):
  - description (H3 heading: ### ITEM-ID — Title)
  - priority (explicit **Priority**: P0/P1/P2 field)
  - acceptance_criteria (**Acceptance criteria**: block)
  - risk (**Risk**: ... field)
  - dependencies (**Dependencies**: ... field)
  - change_description (**Change description**: block with file paths)

Usage: python3 validate_backlog.py <path-to-improvement-backlog.md>
Exit 0: schema valid | Exit 1: schema errors found
"""

import re
import sys
from pathlib import Path


# Schema field patterns per D-0030 §Improvement Item Schema
REQUIRED_PATTERNS = {
    "priority": re.compile(r"\*\*Priority\*\*:\s*(P[0-3])"),
    "acceptance_criteria": re.compile(r"\*\*Acceptance criteria\*\*:"),
    "risk": re.compile(r"\*\*Risk\*\*:"),
    "dependencies": re.compile(r"\*\*Dependencies\*\*:"),
    "change_description": re.compile(r"\*\*Change description\*\*:"),
}

ITEM_HEADING = re.compile(r"^### ([A-Z]+-\d+) —")
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
VALID_EFFORT = re.compile(r"\*\*Effort\*\*:\s*(XS|S|M|L|XL)")


def validate(path: str) -> int:
    """Validate improvement-backlog.md against /sc:roadmap schema.
    Returns number of schema errors found."""
    content = Path(path).read_text()
    lines = content.splitlines()

    errors = []
    warnings = []

    # Split into item sections on H3 item headings
    items = []
    current_item_id = None
    current_lines = []

    for line in lines:
        m = ITEM_HEADING.match(line)
        if m:
            if current_item_id:
                items.append((current_item_id, "\n".join(current_lines)))
            current_item_id = m.group(1)
            current_lines = [line]
        elif current_item_id:
            current_lines.append(line)

    if current_item_id:
        items.append((current_item_id, "\n".join(current_lines)))

    if not items:
        errors.append("ERROR: No item sections found (no '### ITEM-ID —' headings detected)")
        print(f"Schema validation FAILED: {len(errors)} error(s)")
        for e in errors:
            print(f"  {e}")
        return len(errors)

    print(f"Found {len(items)} improvement items to validate")

    for item_id, item_text in items:
        # Check each required schema field
        for field_name, pattern in REQUIRED_PATTERNS.items():
            if not pattern.search(item_text):
                errors.append(
                    f"ERROR [{item_id}]: Missing required field '{field_name}' "
                    f"(pattern: {pattern.pattern!r})"
                )

        # Check priority is a valid P-tier
        m = REQUIRED_PATTERNS["priority"].search(item_text)
        if m and m.group(1) not in VALID_PRIORITIES:
            errors.append(
                f"ERROR [{item_id}]: Invalid priority value '{m.group(1)}' "
                f"(must be one of {sorted(VALID_PRIORITIES)})"
            )

        # Check effort field present (optional per D-0030 but expected in this backlog)
        if not VALID_EFFORT.search(item_text):
            warnings.append(f"WARN [{item_id}]: Missing **Effort**: field (optional per D-0030)")

        # Check change description has at least one file path reference
        if re.search(r"\*\*Change description\*\*:", item_text):
            # Look for a src/ or .claude/ file path reference
            if not re.search(r"`src/|`.claude/|`tests/", item_text):
                warnings.append(
                    f"WARN [{item_id}]: Change description may lack file path reference "
                    f"(no src/, .claude/, or tests/ path found)"
                )

    # Summary
    print(f"\nValidation complete:")
    print(f"  Items checked: {len(items)}")
    print(f"  Schema errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print("\nERRORS (schema incompatibilities):")
        for e in errors:
            print(f"  {e}")
    else:
        print("  Result: SCHEMA VALID — zero incompatibilities")

    if warnings:
        print("\nWARNINGS (non-blocking):")
        for w in warnings:
            print(f"  {w}")

    return len(errors)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-improvement-backlog.md>")
        sys.exit(2)

    target = sys.argv[1]
    if not Path(target).exists():
        print(f"ERROR: File not found: {target}")
        sys.exit(2)

    error_count = validate(target)
    sys.exit(0 if error_count == 0 else 1)
