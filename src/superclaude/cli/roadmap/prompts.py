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

_OUTPUT_FORMAT_BLOCK = (
    "\n\n<output_format>\n"
    "CRITICAL: Your response MUST begin with YAML frontmatter (--- delimited block).\n"
    "Do NOT include any text, preamble, or commentary before the opening ---.\n"
    "Do NOT say \"Here is...\", \"Sure!\", or any conversational text before the frontmatter.\n"
    "\n"
    "Correct start:\n"
    "---\n"
    "key: value\n"
    "---\n"
    "\n"
    "Incorrect start:\n"
    "Here is the output:\n"
    "---\n"
    "key: value\n"
    "---\n"
    "</output_format>"
)


def build_extract_prompt(
    spec_file: Path,
    retrospective_content: str | None = None,
) -> str:
    """Prompt for step 'extract'.

    Instructs Claude to read the provided specification and produce
    extraction.md with YAML frontmatter containing all 13 required
    protocol fields plus 8 structured body sections.

    Parameters
    ----------
    spec_file:
        Path to the specification file being extracted.
    retrospective_content:
        Optional retrospective text from a prior release cycle.
        When provided, it is framed as advisory "areas to watch"
        context -- NOT as hard requirements (RSK-004 mitigation).
    """
    base = (
        "You are a requirements extraction specialist.\n\n"
        "Read the provided specification file and produce a requirements extraction document.\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- spec_source: (string) the source specification filename\n"
        "- generated: (string) ISO-8601 timestamp of extraction\n"
        "- generator: (string) identifier of the extraction agent\n"
        "- functional_requirements: (integer) count of identified functional requirements\n"
        "- nonfunctional_requirements: (integer) count of identified non-functional requirements\n"
        "- total_requirements: (integer) sum of functional + non-functional requirements\n"
        "- complexity_score: (float 0.0-1.0) assessing overall complexity\n"
        "- complexity_class: (string) one of: simple, moderate, complex, enterprise\n"
        "- domains_detected: (integer) count of distinct technical domains identified\n"
        "- risks_identified: (integer) count of risks found in the specification\n"
        "- dependencies_identified: (integer) count of external dependencies\n"
        "- success_criteria_count: (integer) count of measurable success criteria\n"
        "- extraction_mode: (string) one of: full, partial, incremental\n\n"
        "After the frontmatter, provide the following 8 structured sections:\n\n"
        "## Functional Requirements\n"
        "Numbered list with FR-NNN IDs (e.g. FR-001, FR-002). "
        "Extract every functional requirement, even implicit ones.\n\n"
        "## Non-Functional Requirements\n"
        "Numbered list with NFR-NNN IDs (e.g. NFR-001, NFR-002). "
        "Include performance, security, scalability, maintainability.\n\n"
        "## Complexity Assessment\n"
        "Provide complexity_score and complexity_class with detailed scoring rationale.\n\n"
        "## Architectural Constraints\n"
        "List all architectural constraints, technology mandates, and integration boundaries.\n\n"
        "## Risk Inventory\n"
        "Numbered list of identified risks with severity (high/medium/low) and mitigation.\n\n"
        "## Dependency Inventory\n"
        "List all external dependencies, libraries, services, and integration points.\n\n"
        "## Success Criteria\n"
        "Measurable success criteria with acceptance thresholds.\n\n"
        "## Open Questions\n"
        "Ambiguities, gaps, or items requiring stakeholder clarification.\n\n"
        "Be thorough and precise. Extract every requirement, even implicit ones."
    )

    if retrospective_content:
        advisory = (
            "\n\n## Advisory: Areas to Watch (from prior retrospective)\n\n"
            "The following retrospective content is provided as advisory context "
            "only. These are areas to watch during extraction -- they are NOT "
            "additional requirements and MUST NOT be treated as such. Use them "
            "to inform your risk assessment and open questions sections.\n\n"
            f"{retrospective_content}"
        )
        base += advisory

    return base + _OUTPUT_FORMAT_BLOCK


def build_generate_prompt(agent: AgentSpec, extraction_path: Path) -> str:
    """Prompt for step 'generate-{agent.id}'.

    Instructs Claude to read the extraction document and generate a
    complete project roadmap with the agent's persona as a role instruction.
    References expanded extraction fields for richer context.
    """
    return (
        f"You are a {agent.persona} specialist creating a project roadmap.\n\n"
        "Read the provided requirements extraction document and generate a comprehensive "
        "project roadmap.\n\n"
        "The extraction document contains YAML frontmatter with these fields you should "
        "reference for context:\n"
        "- spec_source, generated, generator: provenance metadata\n"
        "- functional_requirements, nonfunctional_requirements, total_requirements: scope counts\n"
        "- complexity_score, complexity_class: complexity assessment\n"
        "- domains_detected: number of technical domains to address\n"
        "- risks_identified: number of risks to mitigate in the roadmap\n"
        "- dependencies_identified: external dependencies to plan around\n"
        "- success_criteria_count: measurable criteria to validate against\n"
        "- extraction_mode: extraction completeness indicator\n\n"
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
    ) + _OUTPUT_FORMAT_BLOCK


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
    ) + _OUTPUT_FORMAT_BLOCK


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
    ) + _OUTPUT_FORMAT_BLOCK


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
    ) + _OUTPUT_FORMAT_BLOCK


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
    ) + _OUTPUT_FORMAT_BLOCK


def build_spec_fidelity_prompt(
    spec_file: Path,
    roadmap_path: Path,
) -> str:
    """Prompt for step 'spec-fidelity'.

    Instructs Claude to compare the specification against the roadmap,
    quote both documents for each deviation, and produce structured YAML
    frontmatter output with severity counts and tasklist_ready field.

    Embeds explicit severity definitions (HIGH/MEDIUM/LOW) to reduce
    LLM classification drift (RSK-007).
    """
    return (
        "You are a specification fidelity analyst.\n\n"
        "Read the provided specification file and the generated roadmap. "
        "Compare them systematically to identify deviations where the roadmap "
        "diverges from or omits requirements in the specification.\n\n"
        "## Severity Definitions\n\n"
        "Apply these severity classifications precisely:\n\n"
        "**HIGH**: The roadmap omits, contradicts, or fundamentally misrepresents "
        "a specification requirement. The roadmap cannot be used as-is without "
        "risking incorrect implementation. Examples:\n"
        "- A functional requirement (FR-NNN) is entirely missing from the roadmap\n"
        "- A non-functional requirement (NFR-NNN) is contradicted by the roadmap\n"
        "- A success criterion (SC-NNN) has no corresponding validation in the roadmap\n"
        "- An architectural constraint is violated by the roadmap's proposed approach\n\n"
        "**MEDIUM**: The roadmap addresses the requirement but with insufficient "
        "detail, ambiguous language, or minor misalignment that could lead to "
        "implementation issues. Examples:\n"
        "- A requirement is mentioned but lacks specific acceptance criteria\n"
        "- The roadmap's phasing differs from the spec's priority ordering\n"
        "- A dependency is acknowledged but not properly sequenced\n\n"
        "**LOW**: Minor stylistic, formatting, or organizational differences that "
        "do not affect correctness. Examples:\n"
        "- Different heading structure or section ordering\n"
        "- Terminology variations that don't change meaning\n"
        "- Missing cross-references that don't affect understanding\n\n"
        "## Comparison Dimensions\n\n"
        "Compare across ALL of these dimensions:\n"
        "1. **Signatures**: Function/method/API signatures specified vs. roadmapped\n"
        "2. **Data Models**: Data structures, schemas, field definitions\n"
        "3. **Gates**: Quality gates, validation checkpoints, acceptance criteria\n"
        "4. **CLI Options**: Command-line flags, arguments, configuration options\n"
        "5. **NFRs**: Performance targets, security requirements, scalability constraints\n\n"
        "## Output Requirements\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
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
        "- **Spec Quote**: Verbatim quote from the specification\n"
        "- **Roadmap Quote**: Verbatim quote from the roadmap, or '[MISSING]' if absent\n"
        "- **Impact**: Assessment of how the deviation affects correctness\n"
        "- **Recommended Correction**: Specific action to resolve the deviation\n\n"
        "## Summary\n\n"
        "Provide a brief summary of findings with severity distribution.\n\n"
        "Be thorough and precise. Quote both documents for every deviation. "
        "Do not invent deviations -- only report genuine differences between "
        "the spec and roadmap."
    ) + _OUTPUT_FORMAT_BLOCK


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
    ) + _OUTPUT_FORMAT_BLOCK
