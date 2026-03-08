"""Prompt builders for Cleanup Audit pipeline.

Each function constructs the LLM contract for one pipeline step.
The prompt specifies:
- What context/inputs to read
- What output format is required
- What machine-readable markers must appear
- What quality expectations apply

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

from pathlib import Path

from .models import CleanupAuditConfig


def build_surface_scan_prompt(config: CleanupAuditConfig, batch_files: list[str]) -> str:
    """Build prompt for Pass 1: Surface scanning (file classification)."""
    file_list = "\n".join(f"- {f}" for f in batch_files)
    return (
        f"/sc:task-unified Perform a surface-level scan of the following files "
        f"and classify each as DELETE, REVIEW, or KEEP with grep evidence.\n\n"
        f"## Files to Scan\n{file_list}\n\n"
        f"## Output Requirements\n"
        f"- Write results to the designated output file\n"
        f"- Include a classification table with columns: File | Classification | Evidence\n"
        f"- Provide grep-based evidence for each classification\n"
        f"- Mark files with no references as DELETE candidates\n"
        f"- Mark files with potential issues as REVIEW\n"
        f"- Mark actively used files as KEEP\n\n"
        f"## Machine-Readable Markers\n"
        f"- End with: EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT\n"
    )


def build_structural_analysis_prompt(
    config: CleanupAuditConfig, batch_files: list[str], surface_results: str
) -> str:
    """Build prompt for Pass 2: Deep structural analysis (per-file profiles)."""
    file_list = "\n".join(f"- {f}" for f in batch_files)
    return (
        f"/sc:task-unified Perform deep structural analysis producing "
        f"mandatory 8-field per-file profiles with evidence.\n\n"
        f"## Prior Context\n"
        f"Surface scan results are available at: {surface_results}\n\n"
        f"## Files to Analyze\n{file_list}\n\n"
        f"## Output Requirements\n"
        f"Write output with YAML frontmatter:\n"
        f"```\n---\ntitle: Structural Analysis\nstatus: PASS\npass: structural\n---\n```\n\n"
        f"For each file produce an 8-field profile:\n"
        f"1. Purpose\n2. Dependencies (imports)\n3. Dependents (who imports this)\n"
        f"4. Complexity estimate\n5. Test coverage indicator\n6. Last modified context\n"
        f"7. Issues found\n8. Recommendation\n\n"
        f"## Machine-Readable Markers\n"
        f"- End with: EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT\n"
    )


def build_cross_cutting_prompt(
    config: CleanupAuditConfig, structural_results: str
) -> str:
    """Build prompt for Pass 3: Cross-cutting analysis (duplication, sprawl)."""
    return (
        f"/sc:task-unified Detect duplication, sprawl, and consolidation "
        f"opportunities across the codebase.\n\n"
        f"## Prior Context\n"
        f"Structural analysis results are available at: {structural_results}\n\n"
        f"## Output Requirements\n"
        f"Write output with YAML frontmatter:\n"
        f"```\n---\ntitle: Cross-Cutting Analysis\nstatus: PASS\n"
        f"pass: cross_cutting\nfinding_count: <N>\n---\n```\n\n"
        f"## Analysis Areas\n"
        f"1. **Duplication Detection**: Identify duplicate or near-duplicate code/files\n"
        f"2. **Sprawl Analysis**: Detect unnecessary file/directory sprawl\n"
        f"3. **Consolidation Opportunities**: Suggest files that can be merged\n"
        f"4. **Import Chain Analysis**: Identify unnecessary dependency chains\n\n"
        f"## Machine-Readable Markers\n"
        f"- End with: EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT\n"
    )


def build_consolidation_prompt(
    config: CleanupAuditConfig, cross_cutting_results: str
) -> str:
    """Build prompt for Pass 4: Consolidation and summary with deduplication."""
    return (
        f"/sc:task-unified Consolidate audit findings into a final summary "
        f"report with deduplication evidence.\n\n"
        f"## Prior Context\n"
        f"Cross-cutting analysis results: {cross_cutting_results}\n\n"
        f"## Output Requirements\n"
        f"Write output with YAML frontmatter:\n"
        f"```\n---\ntitle: Audit Consolidation Report\nstatus: PASS\n"
        f"total_findings: <N>\nseverity_distribution: {{critical: N, high: N, medium: N, low: N}}\n---\n```\n\n"
        f"## Required Sections\n"
        f"1. Executive Summary\n"
        f"2. Deduplicated Findings (with deduplication evidence)\n"
        f"3. Severity Distribution\n"
        f"4. Recommended Actions (prioritized)\n"
        f"5. Estimated Impact\n\n"
        f"## Machine-Readable Markers\n"
        f"- End with: EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT\n"
    )


def build_validation_prompt(
    config: CleanupAuditConfig, consolidation_results: str
) -> str:
    """Build prompt for Pass 5: Validation of audit findings."""
    return (
        f"/sc:task-unified Validate audit findings by spot-checking claims "
        f"against actual codebase state.\n\n"
        f"## Prior Context\n"
        f"Consolidation report: {consolidation_results}\n\n"
        f"## Output Requirements\n"
        f"Write output with YAML frontmatter:\n"
        f"```\n---\ntitle: Audit Validation\nstatus: PASS\n---\n```\n\n"
        f"## Validation Process\n"
        f"1. Sample findings from the consolidation report\n"
        f"2. Independently verify each sampled finding\n"
        f"3. Record verdict (PASS/FAIL) with evidence\n"
        f"4. Report overall validation rate\n\n"
        f"## Machine-Readable Markers\n"
        f"- End with: EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT\n"
    )
