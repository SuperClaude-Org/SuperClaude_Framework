"""Validation prompt builders -- pure functions returning prompt strings.

All functions are pure: they accept concrete values, return ``str``,
and perform no I/O, subprocess calls, or side effects (NFR-004).

Prompt templates for the validate pipeline:
- ``build_reflect_prompt``: single-agent reflection across 7 validation dimensions
- ``build_merge_prompt``: adversarial merge with agreement categorization
"""

from __future__ import annotations

from .prompts import _OUTPUT_FORMAT_BLOCK


def build_reflect_prompt(roadmap: str, test_strategy: str, extraction: str) -> str:
    """Prompt for the 'reflect' validation step.

    Instructs Claude to validate pipeline outputs across 7 dimensions
    with BLOCKING/WARNING severity classifications.  Returns a structured
    report with YAML frontmatter matching REFLECT_GATE criteria.

    Parameters
    ----------
    roadmap:
        Path (as string) to the merged roadmap file.
    test_strategy:
        Path (as string) to the test-strategy file.
    extraction:
        Path (as string) to the extraction file.
    """
    return (
        "You are a validation specialist. You did NOT generate these artifacts.\n\n"
        "Read the provided roadmap, test-strategy, and extraction documents. "
        "Validate the roadmap across the 7 dimensions listed below. "
        "Be thorough but precise -- false positives waste user time. "
        "Every finding must cite a specific location (file:line or file:section).\n\n"
        "## Validation Dimensions\n\n"
        "Each finding MUST be classified as BLOCKING, WARNING, or INFO.\n\n"
        "### BLOCKING Dimensions (failure = roadmap not ready for tasklist generation)\n\n"
        "1. **Schema** -- YAML frontmatter fields present, non-empty, correctly typed.\n"
        "2. **Structure** -- Milestone DAG acyclic, all refs resolve, no duplicate "
        "deliverable IDs, heading hierarchy valid (H2 > H3 > H4, no gaps).\n"
        "3. **Traceability** -- Every deliverable traces to a requirement AND every "
        "requirement traces to a deliverable. Report untraced items.\n"
        "4. **Cross-file consistency** -- test-strategy milestone refs match roadmap "
        "milestones exactly. No dangling references in either direction.\n"
        "5. **Parseability** -- Content is parseable into actionable items via "
        "headings, bullets, and numbered lists by sc:tasklist's splitter.\n\n"
        "### WARNING Dimensions (non-blocking but worth reporting)\n\n"
        "6. **Interleave** -- Compute interleave_ratio using this formula:\n"
        "   `interleave_ratio = unique_phases_with_deliverables / total_phases`\n"
        "   (initial, subject to refinement)\n"
        "   Ratio must be in [0.1, 1.0]. Test activities must not be back-loaded "
        "(i.e., concentrated only in the final phase).\n"
        "7. **Decomposition** -- Flag compound deliverables that would need splitting "
        "by sc:tasklist. A deliverable is compound if it describes multiple distinct "
        "outputs or actions joined by 'and'/'or'.\n\n"
        "## Output Format\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- blocking_issues_count: (integer) total number of BLOCKING findings\n"
        "- warnings_count: (integer) total number of WARNING findings\n"
        "- tasklist_ready: (boolean) true ONLY if blocking_issues_count == 0\n\n"
        "After the frontmatter, provide:\n\n"
        "## Findings\n\n"
        "For each finding, provide:\n"
        "- **[BLOCKING|WARNING|INFO]** Dimension name: Description\n"
        "  - Location: file:line or file:section\n"
        "  - Evidence: what was expected vs. what was found\n"
        "  - Fix guidance: concrete steps to resolve\n\n"
        "## Summary\n\n"
        "Total counts by severity and overall assessment.\n\n"
        "## Interleave Ratio\n\n"
        "Show the computed interleave_ratio with the formula and values used."
    ) + _OUTPUT_FORMAT_BLOCK


def build_merge_prompt(reflect_reports: list[str]) -> str:
    """Prompt for the 'adversarial-merge' validation step.

    Instructs Claude to merge multiple agent reflection reports into a
    single consolidated validation report with agreement categorization.

    Parameters
    ----------
    reflect_reports:
        List of paths (as strings) to individual agent reflection reports.
    """
    agent_count = len(reflect_reports)
    return (
        "You are an adversarial merge specialist consolidating validation reports.\n\n"
        f"Read the {agent_count} provided reflection reports from independent "
        "validation agents. Merge them into a single consolidated validation report.\n\n"
        "## Merge Categorization\n\n"
        "For each finding across reports, categorize it as:\n\n"
        "- **BOTH_AGREE**: Finding appears in both/all reports with consistent severity. "
        "High confidence -- include in final report as-is.\n"
        "- **ONLY_A**: Finding appears only in Agent A's report. "
        "Review recommended -- may be a true positive missed by other agents, "
        "or a false positive.\n"
        "- **ONLY_B**: Finding appears only in Agent B's report. "
        "Review recommended -- likely structural difference in analysis approach.\n"
        "- **CONFLICT**: Finding appears in multiple reports but with different "
        "severity classifications. Escalate to BLOCKING.\n\n"
        "## Agreement Table\n\n"
        "Produce a markdown table with columns:\n"
        "| Finding ID | Agent A | Agent B | Agreement Category |\n"
        "|---|---|---|---|\n\n"
        "Where Agent A/B columns show FOUND/-- and the category is one of "
        "BOTH_AGREE, ONLY_A, ONLY_B, CONFLICT.\n\n"
        "## Output Format\n\n"
        "Your output MUST begin with YAML frontmatter delimited by --- lines containing:\n"
        "- blocking_issues_count: (integer) total BLOCKING findings after merge\n"
        "- warnings_count: (integer) total WARNING findings after merge\n"
        "- tasklist_ready: (boolean) true ONLY if blocking_issues_count == 0\n"
        "- validation_mode: adversarial\n"
        f"- validation_agents: (string) agent identifiers, e.g. 'agent-1, agent-2'\n\n"
        "After the frontmatter, provide:\n\n"
        "## Agreement Table\n\n"
        "The categorized finding table as described above.\n\n"
        "## Consolidated Findings\n\n"
        "Merged findings list, ordered by severity (BLOCKING first, then WARNING, "
        "then INFO). For CONFLICT items, explain the disagreement and your resolution.\n\n"
        "## Summary\n\n"
        "Total counts by severity, agreement statistics, and overall assessment."
    ) + _OUTPUT_FORMAT_BLOCK
