"""Tests for prompt builder framework.

Covers:
- Prompt builders exist for all 5 Claude-assisted steps (Steps 3-7)
- Each builder constructs prompts with @path references to prior artifacts
- Output contracts and frontmatter expectations are embedded
- Retry augmentation supports targeted failures (placeholder residue)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.cli_portify.prompts import (
    PROMPT_BUILDERS,
    AnalyzeWorkflowPrompt,
    BasePromptBuilder,
    BrainstormGapsPrompt,
    DesignPipelinePrompt,
    PanelReviewPrompt,
    PromptContext,
    SynthesizeSpecPrompt,
    get_prompt_builder,
)


@pytest.fixture
def ctx(tmp_path):
    return PromptContext(
        workflow_path=tmp_path / "workflow",
        work_dir=tmp_path / "output",
        cli_name="test-cli",
        source_skill="test-skill",
        iteration=1,
        max_convergence=3,
    )


class TestPromptBuilderRegistry:
    """Prompt builders exist for all 5 Claude-assisted steps."""

    EXPECTED_STEPS = [
        "analyze-workflow",
        "design-pipeline",
        "synthesize-spec",
        "brainstorm-gaps",
        "panel-review",
    ]

    def test_all_five_steps_registered(self):
        for step in self.EXPECTED_STEPS:
            assert step in PROMPT_BUILDERS, f"Missing builder for {step}"

    def test_registry_has_exactly_five_entries(self):
        assert len(PROMPT_BUILDERS) == 5

    def test_all_builders_extend_base(self):
        for name, cls in PROMPT_BUILDERS.items():
            assert issubclass(cls, BasePromptBuilder), f"{name} does not extend BasePromptBuilder"

    def test_get_prompt_builder_returns_correct_type(self, ctx):
        builder = get_prompt_builder("analyze-workflow", ctx)
        assert isinstance(builder, AnalyzeWorkflowPrompt)

    def test_get_prompt_builder_raises_on_unknown(self, ctx):
        with pytest.raises(KeyError, match="No prompt builder"):
            get_prompt_builder("nonexistent-step", ctx)


class TestAtPathReferences:
    """Each builder constructs prompts with @path references to prior artifacts."""

    def test_analyze_workflow_refs_inventory(self, ctx):
        builder = AnalyzeWorkflowPrompt(ctx)
        prompt = builder.build()
        expected_ref = str((ctx.work_dir / "results" / "component-inventory.md").resolve())
        assert f"@{expected_ref}" in prompt

    def test_design_pipeline_refs_two_artifacts(self, ctx):
        builder = DesignPipelinePrompt(ctx)
        prompt = builder.build()
        assert "@" in prompt
        refs = [line for line in prompt.splitlines() if line.startswith("@")]
        assert len(refs) == 2

    def test_synthesize_spec_refs_analysis_and_design(self, ctx):
        builder = SynthesizeSpecPrompt(ctx)
        refs = builder.input_artifacts()
        assert len(refs) == 2
        ref_names = [r.name for r in refs]
        assert "portify-analysis.md" in ref_names
        assert "portify-spec.md" in ref_names

    def test_brainstorm_gaps_refs_synthesized(self, ctx):
        builder = BrainstormGapsPrompt(ctx)
        refs = builder.input_artifacts()
        assert len(refs) == 1
        assert refs[0].name == "synthesized-spec.md"

    def test_panel_review_refs_spec_and_gaps(self, ctx):
        builder = PanelReviewPrompt(ctx)
        refs = builder.input_artifacts()
        assert len(refs) == 2
        ref_names = [r.name for r in refs]
        assert "synthesized-spec.md" in ref_names
        assert "brainstorm-gaps.md" in ref_names


class TestOutputContracts:
    """Output contracts and frontmatter expectations are embedded in each prompt."""

    @pytest.mark.parametrize("step_name", list(PROMPT_BUILDERS.keys()))
    def test_prompt_contains_output_contract(self, step_name, ctx):
        builder = get_prompt_builder(step_name, ctx)
        prompt = builder.build()
        assert "## Output Contract" in prompt

    @pytest.mark.parametrize("step_name", list(PROMPT_BUILDERS.keys()))
    def test_prompt_contains_frontmatter_requirements(self, step_name, ctx):
        builder = get_prompt_builder(step_name, ctx)
        prompt = builder.build()
        assert "## Required Frontmatter" in prompt

    @pytest.mark.parametrize("step_name", list(PROMPT_BUILDERS.keys()))
    def test_required_frontmatter_non_empty(self, step_name, ctx):
        builder = get_prompt_builder(step_name, ctx)
        assert len(builder.required_frontmatter()) > 0

    @pytest.mark.parametrize("step_name", list(PROMPT_BUILDERS.keys()))
    def test_output_contract_non_empty(self, step_name, ctx):
        builder = get_prompt_builder(step_name, ctx)
        assert len(builder.output_contract()) > 0


class TestRetryAugmentation:
    """Retry augmentation supports targeted failures (placeholder residue)."""

    def test_retry_includes_failure_reason(self, ctx):
        builder = AnalyzeWorkflowPrompt(ctx)
        retry = builder.build_retry("Missing section: Complexity Assessment")
        assert "RETRY CONTEXT" in retry
        assert "Missing section: Complexity Assessment" in retry

    def test_retry_includes_remaining_placeholders(self, ctx):
        builder = SynthesizeSpecPrompt(ctx)
        retry = builder.build_retry(
            "Placeholder sentinels remaining",
            remaining_placeholders=[
                "{{SC_PLACEHOLDER:data_flow}}",
                "{{SC_PLACEHOLDER:error_handling}}",
            ],
        )
        assert "{{SC_PLACEHOLDER:data_flow}}" in retry
        assert "{{SC_PLACEHOLDER:error_handling}}" in retry
        assert "MUST be resolved" in retry

    def test_retry_without_placeholders(self, ctx):
        builder = DesignPipelinePrompt(ctx)
        retry = builder.build_retry("Gate check failed")
        assert "RETRY CONTEXT" in retry
        # Should not contain the "MUST be resolved" placeholder list section
        assert "MUST be resolved" not in retry

    def test_retry_preserves_base_prompt(self, ctx):
        builder = BrainstormGapsPrompt(ctx)
        base = builder.build()
        retry = builder.build_retry("test failure")
        assert base in retry


class TestStepNames:
    """Each builder reports the correct step_name."""

    @pytest.mark.parametrize(
        "cls,expected",
        [
            (AnalyzeWorkflowPrompt, "analyze-workflow"),
            (DesignPipelinePrompt, "design-pipeline"),
            (SynthesizeSpecPrompt, "synthesize-spec"),
            (BrainstormGapsPrompt, "brainstorm-gaps"),
            (PanelReviewPrompt, "panel-review"),
        ],
    )
    def test_step_name_correct(self, cls, expected, ctx):
        builder = cls(ctx)
        assert builder.step_name == expected
