"""Gate engine bindings for all 7 cli-portify pipeline steps.

Gate functions validate step outputs and enforce EXEMPT/STANDARD/STRICT
tier compliance. All gates return tuple[bool, str] per NFR-004.

Steps 1-2 gates (SC-001, SC-002) are re-exported from steps.gates for
completeness. Steps 3-7 gates (SC-003 through SC-007) are defined here
with structural and semantic validators for STRICT enforcement.

Integrates with pipeline.gates.gate_passed() validation engine.

Per D-0022: Gate engine bindings for all 7 steps.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from superclaude.cli.cli_portify.utils import (
    extract_sections,
    parse_frontmatter,
    validate_frontmatter_fields,
)
from superclaude.cli.pipeline.models import GateCriteria, SemanticCheck

# Re-export Steps 1-2 gates from steps.gates
from superclaude.cli.cli_portify.steps.gates import (  # noqa: F401
    DISCOVER_COMPONENTS_GATE,
    VALIDATE_CONFIG_GATE,
    gate_discover_components,
    gate_validate_config,
)


# --- Semantic Check Helpers ---


def _check_section_count(content: str, min_count: int) -> bool:
    """Check that content has at least min_count ## sections."""
    sections = extract_sections(content)
    return len(sections) >= min_count


def _check_no_placeholders(content: str) -> bool:
    """Check that no {{SC_PLACEHOLDER:*}} sentinels remain."""
    return "{{SC_PLACEHOLDER:" not in content


def _check_convergence_terminal(content: str) -> bool:
    """Check that convergence_state is a terminal value ('converged' or 'blocked')."""
    fm, _ = parse_frontmatter(content)
    state = fm.get("convergence_state", "")
    return state in ("converged", "blocked")


def _check_data_flow_diagram(content: str) -> bool:
    """Check that a data flow diagram exists (code block or arrow notation)."""
    # Look for code blocks with arrows or arrow notation in text
    has_code_block = "```" in content
    has_arrows = "→" in content or "->" in content
    return has_code_block or has_arrows


# --- Gate Criteria Definitions for Steps 3-7 ---

ANALYZE_WORKFLOW_GATE = GateCriteria(
    required_frontmatter_fields=[
        "step", "source_skill", "cli_name", "component_count", "analysis_sections",
    ],
    min_lines=20,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="section_count",
            check_fn=lambda c: _check_section_count(c, 5),
            failure_message="Analysis must contain at least 5 sections (Workflow Summary, Component Analysis, Data Flow, Complexity Assessment, Recommendations)",
        ),
    ],
)

DESIGN_PIPELINE_GATE = GateCriteria(
    required_frontmatter_fields=[
        "step", "source_skill", "cli_name", "pipeline_steps", "gate_count",
    ],
    min_lines=30,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_field_count",
            check_fn=lambda c: len(parse_frontmatter(c)[0]) >= 5,
            failure_message="Design spec must have at least 5 frontmatter fields",
        ),
        SemanticCheck(
            name="data_flow_diagram",
            check_fn=_check_data_flow_diagram,
            failure_message="Design spec must include a data flow diagram with arrows",
        ),
    ],
)

SYNTHESIZE_SPEC_GATE = GateCriteria(
    required_frontmatter_fields=[
        "step", "source_skill", "cli_name", "synthesis_version", "placeholder_count",
    ],
    min_lines=15,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="zero_placeholders",
            check_fn=_check_no_placeholders,
            failure_message="Synthesized spec must have zero {{SC_PLACEHOLDER:*}} sentinels",
        ),
    ],
)

BRAINSTORM_GAPS_GATE = GateCriteria(
    required_frontmatter_fields=[
        "step", "source_skill", "cli_name", "gaps_found",
    ],
    min_lines=10,
    enforcement_tier="STANDARD",
)

PANEL_REVIEW_GATE = GateCriteria(
    required_frontmatter_fields=[
        "step", "source_skill", "cli_name", "iteration", "convergence_state",
    ],
    min_lines=15,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="convergence_terminal",
            check_fn=_check_convergence_terminal,
            failure_message="Panel review must reach terminal convergence state ('converged' or 'blocked')",
        ),
    ],
)

# --- Gate Registry ---

GATE_REGISTRY: dict[str, GateCriteria] = {
    "validate-config": VALIDATE_CONFIG_GATE,
    "discover-components": DISCOVER_COMPONENTS_GATE,
    "analyze-workflow": ANALYZE_WORKFLOW_GATE,
    "design-pipeline": DESIGN_PIPELINE_GATE,
    "synthesize-spec": SYNTHESIZE_SPEC_GATE,
    "brainstorm-gaps": BRAINSTORM_GAPS_GATE,
    "panel-review": PANEL_REVIEW_GATE,
}


# --- Gate Functions for Steps 3-7 ---


def gate_analyze_workflow(artifact_path: Path) -> tuple[bool, str]:
    """STRICT gate for analyze-workflow (Step 3 / SC-003).

    Validates:
    - Required frontmatter fields
    - At least 5 sections
    - Minimum 20 lines
    """
    return _run_gate(artifact_path, ANALYZE_WORKFLOW_GATE, "analyze-workflow")


def gate_design_pipeline(artifact_path: Path) -> tuple[bool, str]:
    """STRICT gate for design-pipeline (Step 4 / SC-004).

    Validates:
    - Required frontmatter fields (>=5)
    - Data flow diagram present
    - Minimum 30 lines
    """
    return _run_gate(artifact_path, DESIGN_PIPELINE_GATE, "design-pipeline")


def gate_synthesize_spec(artifact_path: Path) -> tuple[bool, str]:
    """STRICT gate for synthesize-spec (Step 5 / SC-005).

    Validates:
    - Required frontmatter fields
    - Zero {{SC_PLACEHOLDER:*}} sentinels
    - Minimum 15 lines
    """
    return _run_gate(artifact_path, SYNTHESIZE_SPEC_GATE, "synthesize-spec")


def gate_brainstorm_gaps(artifact_path: Path) -> tuple[bool, str]:
    """STANDARD gate for brainstorm-gaps (Step 6 / SC-006).

    Validates:
    - Required frontmatter fields
    - Minimum 10 lines
    """
    return _run_gate(artifact_path, BRAINSTORM_GAPS_GATE, "brainstorm-gaps")


def gate_panel_review(artifact_path: Path) -> tuple[bool, str]:
    """STRICT gate for panel-review (Step 7 / SC-007).

    Validates:
    - Required frontmatter fields
    - Convergence state is terminal ('converged' or 'blocked')
    - Minimum 15 lines
    """
    return _run_gate(artifact_path, PANEL_REVIEW_GATE, "panel-review")


def _run_gate(artifact_path: Path, criteria: GateCriteria, step_name: str) -> tuple[bool, str]:
    """Run gate validation using pipeline.gates.gate_passed() integration.

    Returns tuple[bool, str] per NFR-004.
    """
    from superclaude.cli.pipeline.gates import gate_passed

    passed, reason = gate_passed(artifact_path, criteria)
    if passed:
        return True, f"{step_name} gate passed"
    return False, reason or f"{step_name} gate failed"


def get_gate_criteria(step_name: str) -> GateCriteria:
    """Get gate criteria for a step by name.

    Raises:
        KeyError: If step_name is not a known step.
    """
    if step_name not in GATE_REGISTRY:
        raise KeyError(
            f"No gate criteria for step '{step_name}'. "
            f"Known: {', '.join(GATE_REGISTRY)}"
        )
    return GATE_REGISTRY[step_name]
