"""Roadmap prompt builders -- pure functions returning prompt strings.

All functions are pure: they accept concrete values, return ``str``,
and perform no I/O, subprocess calls, or side effects (NFR-004).

The returned string is passed to ``claude -p "<prompt>"``. The executor
separately appends ``--file <path>`` for each entry in ``step.inputs``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .models import AgentSpec

_DEPTH_INSTRUCTIONS = {
    "quick": (
        "Conduct a single focused debate round. Each perspective states its "
        "position on the key divergence points, then provide a convergence assessment."
    ),
    "standard": (
        "Conduct two debate rounds:\n"
        "  Round 1: Each perspective states initial positions on divergence points.\n"
        "  Round 2: Each perspective rebuts the other's key claims.\n"
        "Then provide a convergence assessment."
    ),
    "deep": (
        "Conduct three debate rounds:\n"
        "  Round 1: Each perspective states initial positions on divergence points.\n"
        "  Round 2: Each perspective rebuts the other's key claims.\n"
        "  Round 3: Final synthesis -- each perspective identifies concessions and "
        "remaining disagreements.\n"
        "Then provide a convergence assessment."
    ),
}


def build_extract_prompt(spec_file: Path) -> str:
    """Prompt for step 'extract'.

    Instructs Claude to read the provided specification and produce
    extraction.md with YAML frontmatter containing functional_requirements,
    complexity_score, and complexity_class.
    """
    return (
        "You are a requirements extraction specialist.\n\n"
        "Read the provided specification file and produce a requirements extraction document.\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- functional_requirements: (integer count of identified requirements)\n"
        "- complexity_score: (float 0.0-1.0 assessing overall complexity)\n"
        "- complexity_class: (one of: simple, moderate, complex, enterprise)\n\n"
        "After the frontmatter, provide:\n"
        "1. A numbered list of all functional requirements extracted from the spec\n"
        "2. A numbered list of all non-functional requirements\n"
        "3. A complexity assessment with justification\n"
        "4. Key architectural constraints identified in the spec\n"
        "5. Open questions or ambiguities found\n\n"
        "Be thorough and precise. Extract every requirement, even implicit ones."
    )


def build_generate_prompt(agent: AgentSpec, extraction_path: Path) -> str:
    """Prompt for step 'generate-{agent.id}'.

    Instructs Claude to read the extraction document and generate a
    complete project roadmap with the agent's persona as a role instruction.
    """
    return (
        f"You are a {agent.persona} specialist creating a project roadmap.\n\n"
        "Read the provided requirements extraction document and generate a comprehensive "
        "project roadmap.\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        f"- spec_source: (the source specification filename)\n"
        "- complexity_score: (float 0.0-1.0 from the extraction)\n"
        f"- primary_persona: {agent.persona}\n\n"
        "After the frontmatter, provide a complete roadmap including:\n"
        "1. Executive summary\n"
        "2. Phased implementation plan with milestones\n"
        "3. Risk assessment and mitigation strategies\n"
        "4. Resource requirements and dependencies\n"
        "5. Success criteria and validation approach\n"
        "6. Timeline estimates per phase\n\n"
        f"Apply your {agent.persona} perspective throughout: prioritize concerns, "
        f"risks, and recommendations that a {agent.persona} would emphasize.\n\n"
        "Use numbered and bulleted lists for actionable items. Be specific and concrete."
    )


def build_diff_prompt(variant_a_path: Path, variant_b_path: Path) -> str:
    """Prompt for step 'diff'.

    Instructs Claude to compare two roadmap variants and produce
    diff-analysis.md with frontmatter fields total_diff_points,
    shared_assumptions_count.
    """
    return (
        "You are a comparative analysis specialist.\n\n"
        "Read the two provided roadmap variants and produce a structured diff analysis.\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- total_diff_points: (integer count of identified divergence points)\n"
        "- shared_assumptions_count: (integer count of shared assumptions)\n\n"
        "After the frontmatter, provide:\n"
        "1. Shared assumptions and agreements between variants\n"
        "2. Numbered list of divergence points, each with:\n"
        "   - Description of the difference\n"
        "   - Which variant takes which position\n"
        "   - Potential impact of each approach\n"
        "3. Areas where one variant is clearly stronger\n"
        "4. Areas requiring debate to resolve\n\n"
        "Be objective. Present both positions fairly without bias."
    )


def build_debate_prompt(
    diff_path: Path,
    variant_a_path: Path,
    variant_b_path: Path,
    depth: Literal["quick", "standard", "deep"],
) -> str:
    """Prompt for step 'debate'.

    Depth controls the number of debate rounds embedded in the prompt.
    """
    depth_instruction = _DEPTH_INSTRUCTIONS[depth]
    return (
        "You are a structured debate facilitator.\n\n"
        "Read the provided diff analysis and both roadmap variants. "
        "Facilitate a structured adversarial debate between the two approaches.\n\n"
        f"Debate format:\n{depth_instruction}\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- convergence_score: (float 0.0-1.0 indicating how much agreement was reached)\n"
        "- rounds_completed: (integer number of debate rounds conducted)\n\n"
        "After the frontmatter, provide the full debate transcript with:\n"
        "- Each round clearly labeled\n"
        "- Positions attributed to Variant A and Variant B\n"
        "- A convergence assessment summarizing areas of agreement and remaining disputes\n\n"
        "Ensure each perspective argues its strongest case. Do not artificially force agreement."
    )


def build_score_prompt(
    debate_path: Path,
    variant_a_path: Path,
    variant_b_path: Path,
) -> str:
    """Prompt for step 'score'.

    Instructs Claude to select a base variant and score both.
    """
    return (
        "You are an objective evaluation specialist.\n\n"
        "Read the debate transcript and both roadmap variants. "
        "Score each variant and select a base for the final merge.\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- base_variant: (string: the identifier of the selected base variant)\n"
        "- variant_scores: (string summary of scores, e.g. 'A:78 B:72')\n\n"
        "After the frontmatter, provide:\n"
        "1. Scoring criteria used (derived from the debate)\n"
        "2. Per-criterion scores for each variant\n"
        "3. Overall scores with justification\n"
        "4. Base variant selection rationale\n"
        "5. Specific improvements from the non-base variant to incorporate in merge\n\n"
        "Be evidence-based. Reference specific debate points and variant content."
    )


def build_merge_prompt(
    base_selection_path: Path,
    variant_a_path: Path,
    variant_b_path: Path,
    debate_path: Path,
) -> str:
    """Prompt for step 'merge'.

    Instructs Claude to produce the final merged roadmap.
    """
    return (
        "You are a synthesis specialist producing the final merged roadmap.\n\n"
        "Read the base selection document, both roadmap variants, and the debate transcript. "
        "Produce a final merged roadmap that uses the selected base variant as foundation "
        "and incorporates the best elements from the other variant as identified in the debate.\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- spec_source: (the original specification filename)\n"
        "- complexity_score: (float from the extraction)\n"
        "- adversarial: true\n\n"
        "After the frontmatter, provide the complete final roadmap with:\n"
        "1. Executive summary (synthesized from both variants)\n"
        "2. Phased implementation plan incorporating debate-resolved improvements\n"
        "3. Risk assessment merging insights from both perspectives\n"
        "4. Resource requirements\n"
        "5. Success criteria and validation approach\n"
        "6. Timeline estimates\n\n"
        "Use proper heading hierarchy (H2, H3, H4) with no gaps. "
        "Ensure all internal cross-references resolve. "
        "Do not duplicate heading text at H2 or H3 level."
    )


def build_test_strategy_prompt(
    roadmap_path: Path,
    extraction_path: Path,
) -> str:
    """Prompt for step 'test-strategy'.

    Instructs Claude to produce a test strategy for the roadmap.
    """
    return (
        "You are a test strategy specialist.\n\n"
        "Read the final roadmap and the requirements extraction document. "
        "Produce a comprehensive test strategy.\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- validation_milestones: (integer count of validation milestones defined)\n"
        "- interleave_ratio: (string describing test-to-implementation ratio, e.g. '1:3')\n\n"
        "After the frontmatter, provide:\n"
        "1. Validation milestones mapped to roadmap phases\n"
        "2. Test categories (unit, integration, E2E, acceptance)\n"
        "3. Test-implementation interleaving strategy\n"
        "4. Risk-based test prioritization\n"
        "5. Acceptance criteria per milestone\n"
        "6. Quality gates between phases\n\n"
        "Be specific about what to test at each milestone."
    )
