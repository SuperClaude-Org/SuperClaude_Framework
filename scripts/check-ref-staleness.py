#!/usr/bin/env python3
"""Stale-ref detector: compare ref field names against live API signatures.

Exits 0 if all refs match live API. Exits 1 with details on mismatch.
Designed to run in CI or as a pre-generation guard.

Usage:
    uv run python scripts/check-ref-staleness.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_PY = REPO_ROOT / "src" / "superclaude" / "cli" / "pipeline" / "models.py"
GATES_PY = REPO_ROOT / "src" / "superclaude" / "cli" / "pipeline" / "gates.py"
PIPELINE_SPEC = (
    REPO_ROOT
    / "src"
    / "superclaude"
    / "skills"
    / "sc-cli-portify"
    / "refs"
    / "pipeline-spec.md"
)
CODE_TEMPLATES = (
    REPO_ROOT
    / "src"
    / "superclaude"
    / "skills"
    / "sc-cli-portify"
    / "refs"
    / "code-templates.md"
)

# Also check protocol directory if it exists
PROTOCOL_PIPELINE_SPEC = (
    REPO_ROOT
    / "src"
    / "superclaude"
    / "skills"
    / "sc-cli-portify-protocol"
    / "refs"
    / "pipeline-spec.md"
)
PROTOCOL_CODE_TEMPLATES = (
    REPO_ROOT
    / "src"
    / "superclaude"
    / "skills"
    / "sc-cli-portify-protocol"
    / "refs"
    / "code-templates.md"
)


def extract_dataclass_fields(source: str, class_name: str) -> dict[str, str]:
    """Extract field names and their type annotations from a dataclass."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            fields = {}
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(
                    item.target, ast.Name
                ):
                    fields[item.target.id] = ast.unparse(item.annotation)
            return fields
    return {}


def extract_function_signatures(source: str) -> dict[str, str]:
    """Extract top-level function signatures."""
    tree = ast.parse(source)
    sigs = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            returns = ast.unparse(node.returns) if node.returns else "None"
            sigs[node.name] = returns
    return sigs


def check_ref_file(ref_path: Path, live_fields: dict) -> list[str]:
    """Check a ref file for field name mismatches against live API."""
    if not ref_path.exists():
        return []

    content = ref_path.read_text()
    errors = []

    # Check GateCriteria field names
    gc_fields = live_fields["GateCriteria"]

    # Detect old field names
    if re.search(r'\btier\s*=\s*"', content):
        if not re.search(r'\benforcement_tier\s*=\s*"', content):
            errors.append(
                f"{ref_path.name}: uses 'tier=' instead of 'enforcement_tier='"
            )

    if "required_frontmatter=" in content and "required_frontmatter_fields=" not in content:
        errors.append(
            f"{ref_path.name}: uses 'required_frontmatter=' instead of 'required_frontmatter_fields='"
        )

    # Check tier casing — enforcement_tier values must be UPPER_CASE
    for match in re.finditer(r'enforcement_tier\s*=\s*"(\w+)"', content):
        val = match.group(1)
        if val != val.upper():
            errors.append(
                f"{ref_path.name}: enforcement_tier value '{val}' should be UPPER_CASE"
            )

    # Also catch old-style lowercase tier values
    for match in re.finditer(r'(?<!\w)tier\s*=\s*"(\w+)"', content):
        val = match.group(1)
        if val != val.upper():
            errors.append(
                f"{ref_path.name}: tier value '{val}' should be UPPER_CASE"
            )

    # Check SemanticCheck field names
    sc_fields = live_fields["SemanticCheck"]
    if "fn=" in content and "check_fn=" not in content:
        errors.append(
            f"{ref_path.name}: uses 'fn=' instead of 'check_fn=' for SemanticCheck"
        )

    # Check SemanticCheck signature — should be Callable[[str], bool], not tuple[bool, str]
    if "-> tuple[bool, str]" in content:
        errors.append(
            f"{ref_path.name}: semantic check signature shows 'tuple[bool, str]' "
            f"but live API uses 'Callable[[str], bool]'"
        )

    return errors


def main() -> int:
    # Read live API
    if not MODELS_PY.exists():
        print(f"ERROR: Live API file not found: {MODELS_PY}")
        return 1
    if not GATES_PY.exists():
        print(f"ERROR: Live API file not found: {GATES_PY}")
        return 1

    models_source = MODELS_PY.read_text()

    live_fields = {
        "GateCriteria": extract_dataclass_fields(models_source, "GateCriteria"),
        "SemanticCheck": extract_dataclass_fields(models_source, "SemanticCheck"),
        "Step": extract_dataclass_fields(models_source, "Step"),
        "StepResult": extract_dataclass_fields(models_source, "StepResult"),
        "PipelineConfig": extract_dataclass_fields(models_source, "PipelineConfig"),
    }

    gates_source = GATES_PY.read_text()
    live_sigs = extract_function_signatures(gates_source)

    print("=== Stale-Ref Detector ===")
    print()
    print("Live API fields:")
    for cls, fields in live_fields.items():
        print(f"  {cls}: {', '.join(fields.keys())}")
    print(f"  gate_passed() -> {live_sigs.get('gate_passed', 'NOT FOUND')}")
    print()

    all_errors: list[str] = []

    # Check all ref file locations
    for ref_path in [
        PIPELINE_SPEC,
        CODE_TEMPLATES,
        PROTOCOL_PIPELINE_SPEC,
        PROTOCOL_CODE_TEMPLATES,
    ]:
        if ref_path.exists():
            errors = check_ref_file(ref_path, live_fields)
            all_errors.extend(errors)
            status = "PASS" if not errors else "FAIL"
            print(f"[{status}] {ref_path.relative_to(REPO_ROOT)}")
            for err in errors:
                print(f"  - {err}")

    print()
    if all_errors:
        print(f"FAIL: {len(all_errors)} mismatch(es) found")
        return 1
    else:
        print("PASS: All ref files match live API signatures")
        return 0


if __name__ == "__main__":
    sys.exit(main())
