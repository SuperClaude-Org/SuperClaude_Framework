"""Prompt builder framework for cli-portify Claude-assisted steps.

One builder per Claude-assisted step (Steps 3-7):
- AnalyzeWorkflowPrompt (Step 3)
- DesignPipelinePrompt (Step 4)
- SynthesizeSpecPrompt (Step 5)
- BrainstormGapsPrompt (Step 6)
- PanelReviewPrompt (Step 7)

Each builder constructs prompts with:
- @path references to prior step artifacts
- Step-specific output contracts and frontmatter expectations
- Retry augmentation for targeted failures (placeholder residue)

Per D-0018: Cross-cutting prompt framework for all Claude-assisted steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PromptContext:
    """Shared context available to all prompt builders."""

    workflow_path: Path = field(default_factory=lambda: Path("."))
    work_dir: Path = field(default_factory=lambda: Path("."))
    cli_name: str = ""
    source_skill: str = ""
    iteration: int = 0
    max_convergence: int = 3


class BasePromptBuilder:
    """Base class for prompt builders.

    Subclasses must implement:
    - step_name: str property
    - _build_instructions(): step-specific prompt body
    - input_artifacts(): list of artifact paths this step reads
    - output_contract(): expected output format description
    - required_frontmatter(): list of required frontmatter field names
    """

    def __init__(self, context: PromptContext):
        self.context = context

    @property
    def step_name(self) -> str:
        raise NotImplementedError

    def build(self) -> str:
        """Construct the full prompt with @path references and output contract."""
        parts: list[str] = []

        # @path references to input artifacts
        refs = self.input_artifacts()
        if refs:
            for ref in refs:
                parts.append(f"@{ref.resolve()}")
            parts.append("")

        # Step instructions
        parts.append(self._build_instructions())

        # Output contract
        contract = self.output_contract()
        if contract:
            parts.append("")
            parts.append("## Output Contract")
            parts.append(contract)

        # Frontmatter expectations
        fm_fields = self.required_frontmatter()
        if fm_fields:
            parts.append("")
            parts.append("## Required Frontmatter")
            parts.append("The output MUST begin with YAML frontmatter containing:")
            for f in fm_fields:
                parts.append(f"- {f}")

        return "\n".join(parts)

    def build_retry(self, failure_reason: str, remaining_placeholders: list[str] | None = None) -> str:
        """Build a retry prompt augmented with failure context.

        Args:
            failure_reason: Why the previous attempt failed.
            remaining_placeholders: Any {{SC_PLACEHOLDER:*}} sentinels still present.
        """
        base = self.build()
        augment_parts = [
            base,
            "",
            "## RETRY CONTEXT",
            f"Previous attempt failed: {failure_reason}",
        ]

        if remaining_placeholders:
            augment_parts.append("")
            augment_parts.append("The following placeholders MUST be resolved (not left as sentinels):")
            for ph in remaining_placeholders:
                augment_parts.append(f"- {ph}")

        augment_parts.append("")
        augment_parts.append("Fix the issues above and produce complete output. Do NOT leave any {{SC_PLACEHOLDER:*}} sentinels.")

        return "\n".join(augment_parts)

    def input_artifacts(self) -> list[Path]:
        """Return list of artifact paths this step reads."""
        return []

    def output_contract(self) -> str:
        """Return output contract description."""
        return ""

    def required_frontmatter(self) -> list[str]:
        """Return list of required frontmatter fields."""
        return []

    def _build_instructions(self) -> str:
        raise NotImplementedError


class AnalyzeWorkflowPrompt(BasePromptBuilder):
    """Prompt builder for Step 3: analyze-workflow.

    Reads: component-inventory.md (Step 2 output)
    Produces: portify-analysis.md
    """

    @property
    def step_name(self) -> str:
        return "analyze-workflow"

    def input_artifacts(self) -> list[Path]:
        return [
            self.context.work_dir / "results" / "component-inventory.md",
        ]

    def required_frontmatter(self) -> list[str]:
        return ["step", "source_skill", "cli_name", "component_count", "analysis_sections"]

    def output_contract(self) -> str:
        return (
            "Produce a Markdown document with YAML frontmatter and the following sections:\n"
            "- ## Workflow Summary\n"
            "- ## Component Analysis\n"
            "- ## Data Flow\n"
            "- ## Complexity Assessment\n"
            "- ## Recommendations\n"
            "Each section must contain substantive content, not placeholders."
        )

    def _build_instructions(self) -> str:
        return (
            f"Analyze the workflow defined in {self.context.source_skill} "
            f"and its component inventory.\n\n"
            f"CLI name: {self.context.cli_name}\n"
            f"Workflow path: {self.context.workflow_path}\n\n"
            "Produce a comprehensive analysis covering:\n"
            "1. Workflow structure and step dependencies\n"
            "2. Component types and their roles\n"
            "3. Data flow between components\n"
            "4. Complexity assessment for CLI conversion\n"
            "5. Recommendations for pipeline design"
        )


class DesignPipelinePrompt(BasePromptBuilder):
    """Prompt builder for Step 4: design-pipeline.

    Reads: portify-analysis.md (Step 3 output)
    Produces: portify-spec.md (draft pipeline specification)
    """

    @property
    def step_name(self) -> str:
        return "design-pipeline"

    def input_artifacts(self) -> list[Path]:
        return [
            self.context.work_dir / "results" / "component-inventory.md",
            self.context.work_dir / "results" / "portify-analysis.md",
        ]

    def required_frontmatter(self) -> list[str]:
        return ["step", "source_skill", "cli_name", "pipeline_steps", "gate_count"]

    def output_contract(self) -> str:
        return (
            "Produce a pipeline specification with YAML frontmatter and:\n"
            "- ## Pipeline Overview\n"
            "- ## Step Definitions (each with inputs, outputs, gate criteria)\n"
            "- ## Data Flow Diagram\n"
            "- ## Gate Strategy\n"
            "- ## Error Handling\n"
            "Include concrete step definitions, not abstract descriptions."
        )

    def _build_instructions(self) -> str:
        return (
            f"Design a CLI pipeline for '{self.context.cli_name}' based on the "
            f"workflow analysis.\n\n"
            "The pipeline must:\n"
            "1. Define concrete steps with inputs, outputs, and gate criteria\n"
            "2. Include a data flow diagram showing artifact dependencies\n"
            "3. Specify gate tiers (EXEMPT/STANDARD/STRICT) for each step\n"
            "4. Define error handling and retry strategies\n"
            "5. Follow the pipeline.models.Step schema"
        )


class SynthesizeSpecPrompt(BasePromptBuilder):
    """Prompt builder for Step 5: synthesize-spec.

    Reads: portify-analysis.md + portify-spec.md
    Produces: synthesized specification (merged, no placeholders)
    """

    @property
    def step_name(self) -> str:
        return "synthesize-spec"

    def input_artifacts(self) -> list[Path]:
        return [
            self.context.work_dir / "results" / "portify-analysis.md",
            self.context.work_dir / "results" / "portify-spec.md",
        ]

    def required_frontmatter(self) -> list[str]:
        return ["step", "source_skill", "cli_name", "synthesis_version", "placeholder_count"]

    def output_contract(self) -> str:
        return (
            "Produce a unified specification with YAML frontmatter where:\n"
            "- placeholder_count: 0 (MUST be zero)\n"
            "- No {{SC_PLACEHOLDER:*}} sentinels remain\n"
            "- All sections from analysis and design are merged\n"
            "- Contradictions are resolved with explicit rationale"
        )

    def _build_instructions(self) -> str:
        return (
            f"Synthesize the analysis and pipeline design into a unified "
            f"specification for '{self.context.cli_name}'.\n\n"
            "Requirements:\n"
            "1. Merge all sections from both source documents\n"
            "2. Resolve any contradictions with explicit rationale\n"
            "3. Ensure ZERO {{SC_PLACEHOLDER:*}} sentinels remain\n"
            "4. Set placeholder_count to 0 in frontmatter\n"
            "5. Produce a complete, self-contained specification"
        )


class BrainstormGapsPrompt(BasePromptBuilder):
    """Prompt builder for Step 6: brainstorm-gaps.

    Reads: synthesized spec
    Produces: gap analysis findings
    """

    @property
    def step_name(self) -> str:
        return "brainstorm-gaps"

    def input_artifacts(self) -> list[Path]:
        return [
            self.context.work_dir / "results" / "synthesized-spec.md",
        ]

    def required_frontmatter(self) -> list[str]:
        return ["step", "source_skill", "cli_name", "gaps_found", "severity_high"]

    def output_contract(self) -> str:
        return (
            "Produce gap analysis with YAML frontmatter and:\n"
            "- ## Gaps Identified (each with severity: high/medium/low)\n"
            "- ## Missing Edge Cases\n"
            "- ## Integration Risks\n"
            "- ## Suggested Improvements"
        )

    def _build_instructions(self) -> str:
        return (
            f"Review the synthesized specification for '{self.context.cli_name}' "
            f"and identify gaps, missing edge cases, and integration risks.\n\n"
            "Focus on:\n"
            "1. Missing error handling paths\n"
            "2. Unaddressed edge cases\n"
            "3. Integration risks with existing pipeline infrastructure\n"
            "4. Performance or scalability concerns\n"
            "5. Security considerations"
        )


class PanelReviewPrompt(BasePromptBuilder):
    """Prompt builder for Step 7: panel-review.

    Reads: synthesized spec + gap analysis
    Produces: panel-report.md with convergence state
    """

    @property
    def step_name(self) -> str:
        return "panel-review"

    def input_artifacts(self) -> list[Path]:
        return [
            self.context.work_dir / "results" / "synthesized-spec.md",
            self.context.work_dir / "results" / "brainstorm-gaps.md",
        ]

    def required_frontmatter(self) -> list[str]:
        return ["step", "source_skill", "cli_name", "iteration", "convergence_state"]

    def output_contract(self) -> str:
        return (
            "Produce a panel review with YAML frontmatter where:\n"
            "- convergence_state: one of 'converged', 'iterate', 'blocked'\n"
            "- iteration: current iteration number\n"
            "Sections:\n"
            "- ## Review Summary\n"
            "- ## Findings\n"
            "- ## Convergence Assessment\n"
            "- ## Action Items (if convergence_state != 'converged')"
        )

    def _build_instructions(self) -> str:
        return (
            f"Conduct a panel review of the specification and gap analysis "
            f"for '{self.context.cli_name}'.\n\n"
            f"This is iteration {self.context.iteration} of {self.context.max_convergence}.\n\n"
            "Evaluate:\n"
            "1. Specification completeness and correctness\n"
            "2. Gap resolution adequacy\n"
            "3. Whether the spec is ready for implementation (converged)\n"
            "4. If not converged, specific action items for next iteration\n\n"
            "Set convergence_state to 'converged' only if all gaps are resolved "
            "and the specification is implementation-ready."
        )


# Builder registry for lookup by step name
PROMPT_BUILDERS: dict[str, type[BasePromptBuilder]] = {
    "analyze-workflow": AnalyzeWorkflowPrompt,
    "design-pipeline": DesignPipelinePrompt,
    "synthesize-spec": SynthesizeSpecPrompt,
    "brainstorm-gaps": BrainstormGapsPrompt,
    "panel-review": PanelReviewPrompt,
}


def get_prompt_builder(step_name: str, context: PromptContext) -> BasePromptBuilder:
    """Get the prompt builder for a given step name.

    Args:
        step_name: One of the 5 Claude-assisted step names.
        context: Shared prompt context.

    Returns:
        Instantiated prompt builder.

    Raises:
        KeyError: If step_name is not a known Claude-assisted step.
    """
    cls = PROMPT_BUILDERS.get(step_name)
    if cls is None:
        raise KeyError(
            f"No prompt builder for step '{step_name}'. "
            f"Valid steps: {', '.join(PROMPT_BUILDERS)}"
        )
    return cls(context)
