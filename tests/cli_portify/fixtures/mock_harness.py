"""Claude subprocess mock harness for cli-portify testing.

Returns known-good outputs for each of the 5 Claude-assisted step types:
- analyze-workflow (Step 3)
- design-pipeline (Step 4)
- synthesize-spec (Step 5)
- brainstorm-gaps (Step 6)
- panel-review (Step 7)

Also provides edge case fixtures:
- Partial output (has placeholder sentinels)
- Malformed frontmatter
- Timeout simulation

Per D-0021: Enables unit testing without actual Claude invocations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable
from unittest.mock import patch

from superclaude.cli.cli_portify.process import PortifyProcess, ProcessResult


# --- Known-Good Fixture Content ---

ANALYZE_WORKFLOW_GOOD = """\
---
step: analyze-workflow
source_skill: test-skill
cli_name: test-cli
component_count: 5
analysis_sections: 5
---

## Workflow Summary

The test-skill workflow processes input through 5 components in a linear pipeline.

## Component Analysis

1. **InputValidator** - Validates user input parameters
2. **DataTransformer** - Transforms raw data into pipeline format
3. **CoreProcessor** - Main processing logic
4. **OutputFormatter** - Formats results for output
5. **QualityChecker** - Post-processing quality validation

## Data Flow

InputValidator → DataTransformer → CoreProcessor → OutputFormatter → QualityChecker

## Complexity Assessment

Overall complexity: Medium
- Linear data flow with no branching
- 5 components with clear responsibilities
- No external dependencies beyond the pipeline framework

## Recommendations

1. Preserve linear step ordering in CLI pipeline
2. Add gate checks between each step
3. Use STANDARD tier gates for intermediate steps
4. Use STRICT tier gate for final quality check
"""

DESIGN_PIPELINE_GOOD = """\
---
step: design-pipeline
source_skill: test-skill
cli_name: test-cli
pipeline_steps: 7
gate_count: 7
---

## Pipeline Overview

A 7-step pipeline converting the test-skill workflow into a CLI command.

## Step Definitions

### Step 1: validate-config (EXEMPT)
- Inputs: CLI arguments
- Outputs: validated config object
- Gate: EXEMPT (deterministic)

### Step 2: discover-components (STANDARD)
- Inputs: workflow path
- Outputs: component-inventory.md
- Gate: STANDARD (frontmatter + line count)

### Step 3: analyze-workflow (STRICT)
- Inputs: component-inventory.md
- Outputs: portify-analysis.md
- Gate: STRICT (5 required sections)

### Step 4: design-pipeline (STRICT)
- Inputs: portify-analysis.md
- Outputs: portify-spec.md
- Gate: STRICT (frontmatter field count)

### Step 5: synthesize-spec (STRICT)
- Inputs: portify-analysis.md, portify-spec.md
- Outputs: synthesized-spec.md
- Gate: STRICT (zero placeholder sentinels)

### Step 6: brainstorm-gaps (STANDARD)
- Inputs: synthesized-spec.md
- Outputs: brainstorm-gaps.md
- Gate: STANDARD

### Step 7: panel-review (STRICT)
- Inputs: synthesized-spec.md, brainstorm-gaps.md
- Outputs: panel-report.md
- Gate: STRICT (convergence terminal state)

## Data Flow Diagram

```
validate-config → discover-components → analyze-workflow → design-pipeline
                                                              ↓
panel-review ← brainstorm-gaps ← synthesize-spec ←──────────┘
```

## Gate Strategy

- EXEMPT: Steps with deterministic, non-Claude outputs
- STANDARD: Steps with structural validation only
- STRICT: Steps requiring semantic validation and content quality checks

## Error Handling

- Timeout: Configurable per-step (default 300s)
- Retry: Up to 3 attempts for STRICT gate failures
- Resume: --start flag supports re-entry at Steps 5-7
"""

SYNTHESIZE_SPEC_GOOD = """\
---
step: synthesize-spec
source_skill: test-skill
cli_name: test-cli
synthesis_version: 1
placeholder_count: 0
---

## Unified Specification

This specification merges the workflow analysis and pipeline design into a
single authoritative document for implementing the test-cli command.

## Architecture

The pipeline follows a 7-step linear architecture with gate checks.

## Step Contracts

Each step produces a Markdown artifact with YAML frontmatter.

## Data Flow

Linear progression from config validation through panel review.

## Quality Gates

All gates return tuple[bool, str] per NFR-004.

## Implementation Notes

No placeholder sentinels remain. All sections are complete.
"""

BRAINSTORM_GAPS_GOOD = """\
---
step: brainstorm-gaps
source_skill: test-skill
cli_name: test-cli
gaps_found: 3
severity_high: 1
---

## Gaps Identified

### Gap 1: Missing timeout escalation (HIGH)
No mechanism to escalate timeout failures to the user with actionable guidance.

### Gap 2: Incomplete error messages (MEDIUM)
Gate failure messages lack step-specific context for debugging.

### Gap 3: No dry-run coverage for Steps 3-7 (LOW)
Dry-run mode only validates Steps 1-2; no preview for Claude-assisted steps.

## Missing Edge Cases

- Empty workflow (0 components)
- Workflow with circular dependencies
- Very large workflows (>100 components)

## Integration Risks

- ClaudeProcess subprocess may not respect --add-dir in all Claude versions
- Signal vocabulary constants may need updating for new Claude releases

## Suggested Improvements

1. Add timeout escalation with suggested --iteration-timeout override
2. Enrich gate failure messages with step context and artifact path
3. Add dry-run simulation for Claude-assisted steps
"""

PANEL_REVIEW_GOOD = """\
---
step: panel-review
source_skill: test-skill
cli_name: test-cli
iteration: 1
convergence_state: converged
---

## Review Summary

The specification is complete and implementation-ready after reviewing
the synthesized spec and gap analysis findings.

## Findings

1. All 3 identified gaps have actionable mitigation strategies
2. The pipeline architecture is sound and follows existing patterns
3. Gate strategy aligns with NFR-004 requirements

## Convergence Assessment

**State: CONVERGED**

The specification meets all quality criteria:
- Zero placeholder sentinels
- Complete section coverage
- All gaps addressed with mitigation strategies
- Data flow is consistent and complete

## Action Items

No further iterations required. Proceed to implementation.
"""


# --- Edge Case Fixtures ---

PARTIAL_OUTPUT = """\
---
step: synthesize-spec
source_skill: test-skill
cli_name: test-cli
synthesis_version: 1
placeholder_count: 2
---

## Unified Specification

This specification merges the workflow analysis and pipeline design.

## Architecture

{{SC_PLACEHOLDER:architecture_details}}

## Implementation Notes

{{SC_PLACEHOLDER:implementation_notes}}
"""

MALFORMED_FRONTMATTER = """\
This output has no YAML frontmatter at all.

## Content

Just some content without proper formatting.
"""

TIMEOUT_OUTPUT = ""  # Empty - simulates process killed before producing output


# --- Fixture Registry ---

STEP_FIXTURES: dict[str, str] = {
    "analyze-workflow": ANALYZE_WORKFLOW_GOOD,
    "design-pipeline": DESIGN_PIPELINE_GOOD,
    "synthesize-spec": SYNTHESIZE_SPEC_GOOD,
    "brainstorm-gaps": BRAINSTORM_GAPS_GOOD,
    "panel-review": PANEL_REVIEW_GOOD,
}

EDGE_CASE_FIXTURES: dict[str, str] = {
    "partial": PARTIAL_OUTPUT,
    "malformed_frontmatter": MALFORMED_FRONTMATTER,
    "timeout": TIMEOUT_OUTPUT,
}


def get_fixture(step_name: str) -> str:
    """Get known-good fixture content for a step.

    Raises:
        KeyError: If step_name is not a known step.
    """
    if step_name not in STEP_FIXTURES:
        raise KeyError(f"No fixture for step '{step_name}'. Known: {', '.join(STEP_FIXTURES)}")
    return STEP_FIXTURES[step_name]


def get_edge_case(case_name: str) -> str:
    """Get edge case fixture content.

    Raises:
        KeyError: If case_name is not a known edge case.
    """
    if case_name not in EDGE_CASE_FIXTURES:
        raise KeyError(f"No edge case '{case_name}'. Known: {', '.join(EDGE_CASE_FIXTURES)}")
    return EDGE_CASE_FIXTURES[case_name]


def mock_process_run(
    step_name: str,
    exit_code: int = 0,
    timed_out: bool = False,
    fixture_override: str | None = None,
) -> Callable:
    """Create a mock for PortifyProcess.run() that returns fixture content.

    Args:
        step_name: Step to return fixture for.
        exit_code: Simulated exit code.
        timed_out: Whether to simulate timeout.
        fixture_override: Override content (e.g., edge case fixture).

    Returns:
        A callable that patches PortifyProcess.run.
    """
    content = fixture_override if fixture_override is not None else get_fixture(step_name)

    def _mock_run(self: PortifyProcess) -> ProcessResult:
        # Write fixture content to the output file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(content, encoding="utf-8")
        self.error_file.parent.mkdir(parents=True, exist_ok=True)
        self.error_file.write_text("", encoding="utf-8")

        return ProcessResult(
            exit_code=exit_code,
            stdout_text=content,
            stderr_text="",
            timed_out=timed_out,
            duration_seconds=1.0,
            output_file=self.output_file,
            error_file=self.error_file,
        )

    return _mock_run


def patch_portify_process(step_name: str, **kwargs):
    """Context manager that patches PortifyProcess.run with mock output.

    Usage:
        with patch_portify_process("analyze-workflow"):
            result = proc.run()
    """
    mock_fn = mock_process_run(step_name, **kwargs)
    return patch.object(PortifyProcess, "run", mock_fn)
