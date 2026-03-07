# Cleanup Audit Pipeline — Prompt Contracts

Prompt builder functions for each Claude-assisted step. Extracted from `portify-spec.md`
to keep the spec focused on code architecture.

Source workflow: `sc-cleanup-audit-protocol`

---

## Depth Instructions

```python
DEPTH_INSTRUCTIONS: dict[str, str] = {
    "surface": (
        "Perform a surface-level scan. Focus on identifying obvious waste: "
        "test artifacts, runtime files, empty placeholders, unreferenced files. "
        "Classify each file as DELETE / REVIEW / KEEP with grep evidence."
    ),
    "structural": (
        "Perform a deep structural audit. Validate placement, staleness, "
        "broken references, and structural issues. Produce mandatory 8-field "
        "profiles per file with verifiable evidence."
    ),
    "cross-cutting": (
        "Perform a cross-cutting sweep. Find duplication, sprawl, and broken "
        "references spanning directory boundaries. Produce duplication matrices "
        "with overlap percentages. Group similar files for comparison."
    ),
}
```

---

## Step 3: Pass 1 Surface Scan — Batch Prompt

```python
def build_pass1_batch_prompt(
    batch_files: list[str],
    batch_number: int,
    total_batches: int,
    output_path: str,
    rules_content: str,
    dynamic_checklist_content: str,
) -> str:
    file_list = "\n".join(f"- `{f}`" for f in batch_files)
    return f"""You are an audit-scanner agent performing Pass 1 (Surface Scan) of a repository audit.

## Your Batch
Batch {batch_number} of {total_batches}.

Files to audit:
{file_list}

## Instructions

{rules_content}

## Dynamic Loading Checklist

Before classifying ANY file as DELETE, check all 5 patterns:

{dynamic_checklist_content}

## Output Requirements

Write your report to: `{output_path}`

Your report MUST begin with this frontmatter:
```yaml
---
status: complete
batch: {batch_number}
files_audited: <number of files you actually audited>
files_total: {len(batch_files)}
---
```

Your report MUST include these sections:
- ## Safe to Delete
- ## Need Decision
- ## Keep (verified legitimate)
- ## Add to .gitignore (if applicable)
- ## Remaining / Not Audited (if any files were skipped)
- ## Summary

For each file classified as DELETE, you MUST include:
1. The grep command used
2. The match count (must be 0)
3. Dynamic loading check result

## Machine-Readable Markers

At the end of your report, include exactly one of:
```
EXIT_RECOMMENDATION: CONTINUE
```
or
```
EXIT_RECOMMENDATION: HALT
```

Use HALT only if you discover a critical issue that should stop the audit.
"""
```

---

## Step 5: Pass 1 Validation — Prompt

```python
def build_pass1_validate_prompt(
    sample_findings: list[dict],
    batch_report_paths: list[str],
    rules_content: str,
    output_path: str,
) -> str:
    findings_text = ""
    for i, finding in enumerate(sample_findings, 1):
        findings_text += f"""
### Finding {i}
- **File**: `{finding['file']}`
- **Classification**: {finding['classification']}
- **Claimed evidence**: {finding['evidence']}
- **Source batch**: {finding['batch_report']}
"""

    return f"""You are an audit-validator agent performing spot-check validation of Pass 1 findings.

## Your Task
Independently verify the following {len(sample_findings)} findings by re-testing all claims from scratch.

{findings_text}

## Verification Protocol

{rules_content}

## Independence Instruction
Do NOT assume the prior agent was correct. Verify everything from scratch:
1. Re-read the file yourself
2. Re-run the grep commands yourself
3. Independently check for dynamic loading patterns
4. Compare your findings with the original classification

## Output Requirements

Write your validation report to: `{output_path}`

Your report MUST begin with this frontmatter:
```yaml
---
status: complete
findings_checked: {len(sample_findings)}
discrepancies_found: <number where your result differs from original>
---
```

Your report MUST include for each finding:
- Original classification vs your independent classification
- Evidence you gathered (grep results, file content observations)
- AGREE or DISAGREE with brief justification

## Machine-Readable Markers

At the end:
```
EXIT_RECOMMENDATION: CONTINUE
```
"""
```

---

## Step 6 / Step 9: Pass Consolidation — Prompt

```python
def build_consolidate_prompt(
    pass_number: int,
    pass_name: str,
    batch_report_paths: list[str],
    validation_report_path: str | None,
    template_content: str,
    output_path: str,
    prior_summaries: list[str] | None = None,
) -> str:
    batch_list = "\n".join(f"- `{p}`" for p in batch_report_paths)
    prior_context = ""
    if prior_summaries:
        prior_context = "\n\n## Prior Pass Summaries\n" + "\n".join(
            f"- `{p}`" for p in prior_summaries
        )

    validation_note = ""
    if validation_report_path:
        validation_note = f"""
## Validation Report
Also read the validation report at `{validation_report_path}` and incorporate
any discrepancies noted by the validator.
"""

    return f"""You are an audit-consolidator agent merging batch reports for Pass {pass_number} ({pass_name}).

## Batch Reports to Merge
{batch_list}
{validation_note}
{prior_context}

## Template to Follow
{template_content}

## Your Task
1. Read ALL batch reports for this pass
2. Merge findings into unified lists (DELETE, CONSOLIDATE, MOVE, FLAG, KEEP, BROKEN REF)
3. Deduplicate findings appearing in multiple batches
4. Extract cross-agent patterns (systemic findings reported by multiple agents)
5. Compute aggregate metrics (total files, coverage, category counts)
6. Produce quality gate status table

## Output Requirements

Write your consolidated report to: `{output_path}`

Your report MUST begin with this frontmatter:
```yaml
---
status: complete
pass: {pass_number}
total_files: <total files audited across all batches>
coverage_pct: <coverage percentage>
delete_count: <total DELETE recommendations>
review_count: <total REVIEW recommendations>
keep_count: <total KEEP recommendations>
---
```

Required sections:
- ## Aggregate Summary (table)
- ## Coverage Metrics
- ## Cross-Agent Patterns
- ## Validation Results (if validation report available)
- ## Deduplication Notes
- ## Quality Gate Status (table)
- ## Batch Reports Index (table)

## Machine-Readable Markers

At the end:
```
EXIT_RECOMMENDATION: CONTINUE
```
"""
```

---

## Step 8: Pass 2 Structural Audit — Batch Prompt

```python
def build_pass2_batch_prompt(
    batch_files: list[str],
    batch_number: int,
    total_batches: int,
    output_path: str,
    rules_content: str,
    profile_template_content: str,
    pass1_context: str,
) -> str:
    file_list = "\n".join(f"- `{f}`" for f in batch_files)
    return f"""You are an audit-analyzer agent performing Pass 2 (Structural Audit) of a repository audit.

## Your Batch
Batch {batch_number} of {total_batches}.

Files to audit (only KEEP/REVIEW from Pass 1):
{file_list}

## Pass 1 Context (Known Issues)
{pass1_context}

Do not re-flag issues already identified in Pass 1.

## Instructions

{rules_content}

## Mandatory Per-File Profile Format (8 Fields — ALL REQUIRED)

{profile_template_content}

## CRITICAL: Profile Completeness
Reports missing mandatory per-file profiles will be FAILED and must be regenerated.
Every file must have ALL 8 fields filled. "N/A" requires justification.

## Output Requirements

Write your report to: `{output_path}`

Your report MUST begin with this frontmatter:
```yaml
---
status: complete
batch: {batch_number}
files_audited: <number of files you actually profiled>
files_total: {len(batch_files)}
---
```

Your report MUST include the mandatory 8-field profile table for EVERY file.

## Machine-Readable Markers

At the end:
```
EXIT_RECOMMENDATION: CONTINUE
```
"""
```

---

## Step 11: Pass 3 Cross-Cutting — Batch Prompt

```python
def build_pass3_batch_prompt(
    batch_files: list[str],
    batch_number: int,
    total_batches: int,
    output_path: str,
    rules_content: str,
    profile_template_content: str,
    pass1_context: str,
    pass2_context: str,
    file_grouping: str,
) -> str:
    file_list = "\n".join(f"- `{f}`" for f in batch_files)
    return f"""You are an audit-comparator agent performing Pass 3 (Cross-Cutting Sweep) of a repository audit.

## Your Batch
Batch {batch_number} of {total_batches}.

Files to compare (grouped by similarity):
{file_list}

File grouping rationale:
{file_grouping}

## Prior Pass Context

### Pass 1 Known Issues
{pass1_context}

### Pass 2 Known Issues
{pass2_context}

Do not re-flag issues already identified in Passes 1 or 2.

## Instructions

{rules_content}

## Per-File Profile Format (7 Fields — ALL REQUIRED)

{profile_template_content}

## CRITICAL DIFFERENTIATORS
1. COMPARE, don't just catalog — DIFF similar files and quantify overlap %
2. GROUP AUDIT — audit similar files together, compare within the group
3. MANDATORY DUPLICATION MATRIX when similar files are detected
4. AUTO-KEEP for files already profiled in Pass 2 — focus on cross-cutting relationships

## Output Requirements

Write your report to: `{output_path}`

Your report MUST begin with this frontmatter:
```yaml
---
status: complete
batch: {batch_number}
files_audited: <number of files you compared>
files_total: {len(batch_files)}
---
```

If similar files are detected, your report MUST include a Duplication Matrix:
| File A | File B | Overlap % | Key Differences | Recommendation |

## Machine-Readable Markers

At the end:
```
EXIT_RECOMMENDATION: CONTINUE
```
"""
```

---

## Step 12: Final Report — Prompt

```python
def build_final_report_prompt(
    pass1_summary_path: str,
    pass2_summary_path: str,
    pass3_batch_paths: list[str],
    template_content: str,
    output_path: str,
    repo_name: str,
) -> str:
    pass3_list = "\n".join(f"- `{p}`" for p in pass3_batch_paths)
    return f"""You are an audit-consolidator agent producing the Final Audit Report.

## Repository
{repo_name}

## Input Sources
- Pass 1 Summary: `{pass1_summary_path}`
- Pass 2 Summary: `{pass2_summary_path}`
- Pass 3 Batch Reports:
{pass3_list}

## Template
{template_content}

## Your Task
Produce a comprehensive final report with:
1. **Executive Summary** — Total files, coverage, action counts, estimated effort
2. **Action Items by Priority** — Immediate (safe DELETEs/MOVEs), Decision-required (REVIEW/CONSOLIDATE), Code-changes (FLAG/BROKEN REF)
3. **Cross-Cutting Findings** — Systemic patterns spanning all passes
4. **Discovered Issues Registry** — Numbered list of all systemic issues
5. **Duplication Matrix** — From Pass 3 findings
6. **Audit Methodology** — Passes executed, quality assurance, exclusions
7. **Recommendations** — Process improvements, suggested workflow

## Output Requirements

Write your final report to: `{output_path}`

Your report MUST begin with this frontmatter:
```yaml
---
status: complete
total_files: <total files in repo>
passes_completed: <number of passes run>
delete_count: <total DELETE recommendations across all passes>
consolidate_count: <total CONSOLIDATE recommendations>
flag_count: <total FLAG recommendations>
---
```

## Machine-Readable Markers

At the end:
```
EXIT_RECOMMENDATION: CONTINUE
```
"""
```
