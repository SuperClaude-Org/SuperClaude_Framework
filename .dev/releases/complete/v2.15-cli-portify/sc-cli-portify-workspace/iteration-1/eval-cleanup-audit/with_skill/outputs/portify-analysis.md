---
source_skill: sc-cleanup-audit-protocol
source_command: cleanup-audit
step_count: 11
parallel_groups: 3
gate_count: 9
agent_count: 5
complexity: high
---

# Portification Analysis: cleanup-audit

## Source Components

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| Command | `src/superclaude/commands/cleanup-audit.md` | 103 | CLI entry point with argument parsing, repo context injection, skill activation |
| Skill | `src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md` | 134 | Full behavioral protocol: 5-step flow (Discover, Configure, Orchestrate, Validate, Report) |
| Agent: audit-scanner | `src/superclaude/agents/audit-scanner.md` | 94 | Pass 1 Haiku surface scanner — DELETE/REVIEW/KEEP classification with grep evidence |
| Agent: audit-analyzer | `src/superclaude/agents/audit-analyzer.md` | 89 | Pass 2 Sonnet structural auditor — 8-field mandatory per-file profiles |
| Agent: audit-comparator | `src/superclaude/agents/audit-comparator.md` | 77 | Pass 3 Sonnet cross-cutting comparator — duplication matrices, overlap quantification |
| Agent: audit-consolidator | `src/superclaude/agents/audit-consolidator.md` | 69 | Report merger — pass summaries and final report synthesis |
| Agent: audit-validator | `src/superclaude/agents/audit-validator.md` | 101 | Spot-check validator — independent re-verification of sampled findings (10%) |
| Ref: pass1-surface-scan | `rules/pass1-surface-scan.md` | 78 | Pass 1 classification taxonomy, verification protocol, evidence standards |
| Ref: pass2-structural-audit | `rules/pass2-structural-audit.md` | 84 | Pass 2 mandatory 8-field profile, finding types, file-type-specific rules |
| Ref: pass3-cross-cutting | `rules/pass3-cross-cutting.md` | 70 | Pass 3 extended taxonomy, 6 differentiators, tiered depth strategy, duplication matrix |
| Ref: dynamic-use-checklist | `rules/dynamic-use-checklist.md` | 118 | 5-pattern dynamic loading check required before any DELETE classification |
| Ref: verification-protocol | `rules/verification-protocol.md` | 86 | Unified evidence requirements by recommendation type, 7-source cross-ref checklist |
| Template: batch-report | `templates/batch-report.md` | 78 | Per-agent output template: DELETE/CONSOLIDATE/MOVE/FLAG/KEEP sections with profiles |
| Template: pass-summary | `templates/pass-summary.md` | 95 | Aggregated per-pass report: metrics, patterns, validation, quality gates |
| Template: final-report | `templates/final-report.md` | 109 | Executive summary, prioritized actions, cross-cutting findings, issues registry |
| Template: finding-profile | `templates/finding-profile.md` | 68 | Mandatory per-file profile formats for Pass 2 (8 fields) and Pass 3 (7 fields) |
| Script: repo-inventory.sh | `scripts/repo-inventory.sh` | 135 | Shell script: git ls-files enumeration, domain classification, batch assignment |

## Step Graph

### Step 1: repo-inventory
- **Type**: pure-programmatic
- **Inputs**: [target-path (CLI argument)]
- **Output**: `inventory.json` (file list with domain classification and batch assignments)
- **Gate**: light (file exists and contains valid JSON with expected keys)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 60s
- **Retry**: 0 (deterministic)
- **Notes**: Runs `repo-inventory.sh` or equivalent Python. Outputs structured JSON: `{files: [{path, domain, batch_id}], domains: {name: count}, batches: [{id, files, domain}], total_files: N}`. This replaces the shell preprocessing in the original Discover step. Also computes repo context (total files, file type distribution, repo size).

### Step 2: configure-passes
- **Type**: pure-programmatic
- **Inputs**: [inventory.json, CLI arguments (--pass, --batch-size, --focus)]
- **Output**: `pass-config.json` (which passes to run, batch assignments per pass, agent assignments)
- **Gate**: light (valid JSON with expected structure)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 10s
- **Retry**: 0 (deterministic)
- **Notes**: Determines which passes run based on `--pass` flag. Filters batches by `--focus` domain. Assigns agent type per pass: `audit-scanner` (haiku) for Pass 1, `audit-analyzer` (sonnet) for Pass 2, `audit-comparator` (sonnet) for Pass 3. Sets batch sizes (default 50/25/30). Creates output directory structure `.claude-audit/pass{N}/`.

### Step 3: pass1-surface-scan (batched parallel group)
- **Type**: claude-assisted (batched)
- **Inputs**: [inventory.json, pass-config.json, batch file list]
- **Output**: `.claude-audit/pass1/batch-{NN}.md` (one per batch)
- **Gate**: standard
  - Required sections: "Safe to Delete", "Need Decision", "Keep", "Summary"
  - Min lines: 20 per batch report
  - Semantic: summary counts present and non-negative
- **Agent**: audit-scanner (haiku model)
- **Parallel**: yes (all Pass 1 batches run concurrently, waves of 7-8)
- **Timeout**: 300s per batch
- **Retry**: 1 attempt
- **Notes**: Each batch subprocess receives its file list, runs the Pass 1 protocol (read + grep + check imports + categorize). The executor launches up to 7-8 concurrent Claude subprocesses. Each writes its batch report to disk. Progress tracked via batch completion counting.

### Step 4: pass1-validate
- **Type**: claude-assisted
- **Inputs**: [all `.claude-audit/pass1/batch-*.md` files]
- **Output**: `.claude-audit/pass1/validation-report.md`
- **Gate**: standard
  - Required sections: "Validation Results", "Summary", "Validation Status"
  - Min lines: 30
  - Semantic: validation status is PASS or FAIL; if FAIL, discrepancy rate >= 20% noted
- **Agent**: audit-validator (sonnet model)
- **Parallel**: no (depends on all pass1 batches)
- **Timeout**: 300s
- **Retry**: 1 attempt
- **Notes**: 10% spot-check sampling (5 findings per 50 files). Re-runs grep claims independently. If validation FAIL, executor marks affected batches for regeneration. CRITICAL FAIL on any false-negative DELETE triggers immediate halt.

### Step 5: pass1-consolidate
- **Type**: claude-assisted
- **Inputs**: [all `.claude-audit/pass1/batch-*.md`, `.claude-audit/pass1/validation-report.md`]
- **Output**: `.claude-audit/pass1-summary.md`
- **Gate**: strict
  - Required frontmatter: [pass_number, total_batches, total_files_audited, coverage_percentage]
  - Required sections: "Aggregate Summary", "Coverage Metrics", "Quality Gate Status", "Batch Reports Index"
  - Min lines: 60
  - Semantic: coverage percentage is numeric 0-100; aggregate counts sum correctly; quality gate status present
- **Agent**: audit-consolidator (sonnet model)
- **Parallel**: no (depends on step 4)
- **Timeout**: 600s
- **Retry**: 1 attempt
- **Notes**: Merges all batch reports. Deduplicates findings across batches. Extracts cross-agent patterns. Produces pass summary following `pass-summary.md` template. For `--pass surface` only, this is the final output.

### Step 6: pass2-structural-audit (batched parallel group)
- **Type**: claude-assisted (batched)
- **Inputs**: [pass1-summary.md, inventory.json (filtered to KEEP/REVIEW files only), batch file list]
- **Output**: `.claude-audit/pass2/batch-{NN}.md` (one per batch)
- **Gate**: strict
  - Required: all 8 mandatory profile fields per file
  - Min lines: 40 per batch (files are profiled more deeply)
  - Semantic: every file has exactly 8 fields; no field is empty or "N/A" without justification; recommendation is one of KEEP/MOVE/DELETE/FLAG
- **Agent**: audit-analyzer (sonnet model)
- **Parallel**: yes (all Pass 2 batches run concurrently, waves of 7-8)
- **Timeout**: 600s per batch (deeper analysis)
- **Retry**: 1 attempt
- **Notes**: Only files marked KEEP or REVIEW from Pass 1. Each agent receives Pass 1 context. 8-field mandatory profiles with file-type-specific extra rules (tests, scripts, docs, config). Failed profiles (missing fields) trigger report regeneration.

### Step 7: pass2-validate
- **Type**: claude-assisted
- **Inputs**: [all `.claude-audit/pass2/batch-*.md` files]
- **Output**: `.claude-audit/pass2/validation-report.md`
- **Gate**: standard (same structure as step 4)
- **Agent**: audit-validator (sonnet model)
- **Parallel**: no
- **Timeout**: 300s
- **Retry**: 1 attempt
- **Notes**: Same 10% spot-check protocol as Pass 1 validation. Additionally checks for mandatory profile completeness (all 8 fields present and substantive).

### Step 8: pass2-consolidate
- **Type**: claude-assisted
- **Inputs**: [all pass2 batch reports, pass2 validation report, pass1-summary.md]
- **Output**: `.claude-audit/pass2-summary.md`
- **Gate**: strict (same structure as step 5, plus finding-type breakdown)
- **Agent**: audit-consolidator (sonnet model)
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1 attempt
- **Notes**: Same consolidation protocol as step 5, plus finding-type distribution (MISPLACED/STALE/STRUCTURAL ISSUE/BROKEN REFS/VERIFIED OK). For `--pass structural` only, this is the final output.

### Step 9: pass3-cross-cutting (batched parallel group)
- **Type**: claude-assisted (batched)
- **Inputs**: [pass1-summary.md, pass2-summary.md, grouped-similar-files (from inventory), batch file list]
- **Output**: `.claude-audit/pass3/batch-{NN}.md` (one per batch)
- **Gate**: strict
  - Required: 7 mandatory profile fields per file; duplication matrix when similar files detected
  - Min lines: 40 per batch
  - Semantic: duplication matrix present with numeric overlap percentages; no re-flagging of known issues without "Already tracked" annotation
- **Agent**: audit-comparator (sonnet model)
- **Parallel**: yes (all Pass 3 batches concurrently, waves of 7-8)
- **Timeout**: 600s per batch
- **Retry**: 1 attempt
- **Notes**: Files grouped by similarity (all docker-compose, all deploy scripts, etc.) not by directory. Receives known-issues list from Passes 1-2 to avoid re-flagging. Tiered depth strategy: Deep (root configs, infra), Medium (source dirs, sampling), Light (assets, docs).

### Step 10: pass3-validate-and-consolidate
- **Type**: claude-assisted
- **Inputs**: [all pass3 batch reports, pass1-summary.md, pass2-summary.md]
- **Output**: `.claude-audit/pass3-summary.md`
- **Gate**: strict (same as step 8, plus mandatory duplication matrix presence)
- **Agent**: audit-consolidator (sonnet model) + audit-validator spot-check
- **Parallel**: no (sequential: validate then consolidate)
- **Timeout**: 900s
- **Retry**: 1 attempt
- **Notes**: Combined validate + consolidate for Pass 3 (same pattern as steps 4+5 and 7+8 but merged for efficiency since this is the last pass).

### Step 11: final-report
- **Type**: claude-assisted
- **Inputs**: [pass1-summary.md, pass2-summary.md, pass3-summary.md]
- **Output**: `.claude-audit/final-report.md`
- **Gate**: strict
  - Required frontmatter: [repository, date, passes_completed, total_files, total_audited, coverage]
  - Required sections: "Executive Summary", "Action Items by Priority", "Cross-Cutting Findings", "Discovered Issues Registry", "Audit Methodology"
  - Min lines: 100
  - Semantic: action items categorized as Immediate/Requires Decision/Requires Code Changes; all counts are numeric; methodology lists all passes executed
- **Agent**: audit-consolidator (sonnet model)
- **Parallel**: no (final step)
- **Timeout**: 900s
- **Retry**: 1 attempt
- **Notes**: Only runs when `--pass all` is selected. Synthesizes all 3 pass summaries into executive report. Applies ultrathink-depth synthesis for cross-pass pattern extraction. Produces prioritized action items, duplication matrix from Pass 3, and discovered issues registry.

## Parallel Groups

| Group | Steps | Max Concurrency | Rationale |
|-------|-------|-----------------|-----------|
| 1 | step-3 (pass1 batches) | 7-8 subprocesses | Independent file batches, no inter-batch dependencies |
| 2 | step-6 (pass2 batches) | 7-8 subprocesses | Independent file batches, filtered to KEEP/REVIEW only |
| 3 | step-9 (pass3 batches) | 7-8 subprocesses | Independent similarity-grouped file batches |

Note: Groups 1, 2, and 3 are NOT concurrent with each other. Pass 2 depends on Pass 1 results, Pass 3 depends on Pass 1+2 results. Parallelism is within each pass only.

## Gates Summary

| Step | Tier | Frontmatter | Min Lines | Semantic Checks |
|------|------|-------------|-----------|-----------------|
| 1: repo-inventory | LIGHT | n/a (JSON) | 1 | valid JSON, has `files`, `batches`, `total_files` keys |
| 2: configure-passes | LIGHT | n/a (JSON) | 1 | valid JSON, has `passes`, `batches_per_pass` keys |
| 3: pass1-surface-scan | STANDARD | none | 20/batch | has required sections; summary counts present |
| 4: pass1-validate | STANDARD | none | 30 | has "Validation Status: PASS/FAIL" |
| 5: pass1-consolidate | STRICT | pass_number, total_batches, total_files_audited, coverage_percentage | 60 | coverage numeric 0-100; aggregate counts sum; quality gate present |
| 6: pass2-structural-audit | STRICT | none (profiles are tables) | 40/batch | all 8 profile fields per file; no empty fields; valid recommendation |
| 7: pass2-validate | STANDARD | none | 30 | has "Validation Status: PASS/FAIL" |
| 8: pass2-consolidate | STRICT | pass_number, total_batches, total_files_audited, coverage_percentage | 60 | same as step 5 + finding-type breakdown |
| 9: pass3-cross-cutting | STRICT | none | 40/batch | 7 profile fields; duplication matrix present; no re-flagged known issues |
| 10: pass3-validate-consolidate | STRICT | pass_number, total_batches, total_files_audited, coverage_percentage | 60 | duplication matrix present; quality gate present |
| 11: final-report | STRICT | repository, date, passes_completed, total_files, total_audited, coverage | 100 | action items categorized; all counts numeric; methodology present |

## Agent Delegation Map

| Agent | Model | Used In Steps | Parallel | Contract Summary |
|-------|-------|--------------|----------|------------------|
| audit-scanner | haiku | 3 (pass1 batches) | yes (7-8 concurrent) | Read 20-30 lines + grep for references + check imports + categorize DELETE/REVIEW/KEEP. Output: batch-report.md sections. Max 20 turns. |
| audit-analyzer | sonnet | 6 (pass2 batches) | yes (7-8 concurrent) | 8-field mandatory profile per file. Only KEEP/REVIEW from Pass 1. File-type-specific extra rules. Max 35 turns. |
| audit-comparator | sonnet | 9 (pass3 batches) | yes (7-8 concurrent) | 7-field profile + duplication matrix. Groups by similarity. Receives known-issues list. Max 35 turns. |
| audit-consolidator | sonnet | 5, 8, 10, 11 | no (sequential) | Merge batch reports, deduplicate, extract patterns, compute metrics. Max 40 turns. |
| audit-validator | sonnet | 4, 7, 10 | no (sequential) | 10% spot-check: re-run grep, re-read files, verify classification, check evidence. Max 25 turns. |

## Data Flow Diagram

```
[CLI args: target-path, --pass, --batch-size, --focus]
                    |
              step-1: repo-inventory
                    |
              [inventory.json]
                    |
              step-2: configure-passes
                    |
              [pass-config.json]
                    |
    ================|================  (--pass surface or --pass all)
    |                                |
    |  step-3: pass1-surface-scan    |
    |  ┌─batch-01─┐                  |
    |  │ batch-02  │ (7-8 parallel)  |
    |  │ batch-03  │                 |
    |  │  ...      │                 |
    |  └─batch-NN─┘                  |
    |       |                        |
    |  [pass1/batch-*.md]            |
    |       |                        |
    |  step-4: pass1-validate        |
    |       |                        |
    |  [pass1/validation-report.md]  |
    |       |                        |
    |  step-5: pass1-consolidate     |
    |       |                        |
    |  [pass1-summary.md]            |
    |                                |
    =================================
                    |
    ================|================  (--pass structural or --pass all)
    |                                |
    |  step-6: pass2-structural      |
    |  ┌─batch-01─┐                  |
    |  │ batch-02  │ (7-8 parallel)  |
    |  └─batch-NN─┘                  |
    |       |                        |
    |  step-7: pass2-validate        |
    |       |                        |
    |  step-8: pass2-consolidate     |
    |       |                        |
    |  [pass2-summary.md]            |
    |                                |
    =================================
                    |
    ================|================  (--pass cross-cutting or --pass all)
    |                                |
    |  step-9: pass3-cross-cutting   |
    |  ┌─batch-01─┐                  |
    |  │ batch-02  │ (7-8 parallel)  |
    |  └─batch-NN─┘                  |
    |       |                        |
    |  step-10: pass3-validate+cons  |
    |       |                        |
    |  [pass3-summary.md]            |
    |                                |
    =================================
                    |
              step-11: final-report   (--pass all only)
                    |
              [final-report.md]
```

## Classification Summary

| Category | Count | Steps |
|----------|-------|-------|
| Pure Programmatic | 2 | step-1 (repo-inventory), step-2 (configure-passes) |
| Claude-Assisted | 9 | step-3 (pass1-scan), step-4 (pass1-validate), step-5 (pass1-consolidate), step-6 (pass2-audit), step-7 (pass2-validate), step-8 (pass2-consolidate), step-9 (pass3-compare), step-10 (pass3-validate+consolidate), step-11 (final-report) |
| Hybrid | 0 | none |
| Pure Inference | 0 | none |

## Key Complexity Factors

### Batched Parallel Execution
Unlike the sprint/roadmap pipelines which run single sequential steps, this workflow requires **batched parallel Claude subprocesses** (7-8 concurrent). This is the primary architectural challenge:
- The executor must launch N subprocesses per pass, each with its own file list
- Monitor must track N concurrent output streams
- TUI must show per-batch progress, not just per-step
- Gate evaluation happens per-batch, with pass-level gate aggregating batch results
- Failed batches can be retried individually without re-running the whole pass

### Dynamic Step Count
The number of batches (and thus subprocess count) is determined at runtime by `inventory.json` and `--batch-size`. The step graph is not fully known at compile time. The executor must generate steps dynamically.

### Inter-Pass Dependencies
Pass 2 consumes Pass 1 outputs (filtered to KEEP/REVIEW). Pass 3 consumes both Pass 1 and Pass 2 outputs. The executor must pass prior-pass artifacts as inputs to subsequent-pass prompts.

### Conditional Execution
Not all passes run every time. `--pass surface` runs only steps 1-5. `--pass structural` runs steps 1-2 then 6-8 (requiring prior Pass 1 results). `--pass all` runs everything. The step graph must be prunable.

### Validation-Triggered Regeneration
If the audit-validator reports FAIL (discrepancy rate >= 20%), affected batch reports must be regenerated. This is a retry-on-validation-failure pattern not present in the sprint executor.

## Recommendations

### Move to Programmatic (currently inference)
1. **Batch assignment**: The current skill relies on Claude to divide files into batches. This should be fully programmatic (Python divides `inventory.json` into batches of `--batch-size`).
2. **File filtering between passes**: Currently Claude reads Pass 1 summary to determine which files go to Pass 2. This should be programmatic: parse Pass 1 batch reports, extract DELETE classifications, filter inventory for Pass 2.
3. **Validation sampling**: Currently Claude picks which findings to spot-check. This should be programmatic: random sample with stratified selection (at least 1 DELETE, 1 KEEP, 1 FLAG).
4. **Progress tracking**: Currently uses TodoWrite. Should be `progress.json` updated by the executor.
5. **Report structure validation**: Checking for required sections and mandatory fields is currently implicit in agent instructions. Should be explicit gate functions that parse markdown and check field presence.

### Steps That Could Be Split
1. **Step 10** combines validate + consolidate for Pass 3. Could split for cleaner gate coverage, but merging reduces overhead for the final pass.
2. **Batch report parsing** (extracting classifications from markdown) could be a pure-programmatic intermediate step between each pass's scan and its consolidation. This would make the inter-pass data flow more explicit and reduce the consolidator's burden.

### Parallelization Opportunities
1. Pass 1 batches are fully independent — already parallel.
2. Pass 2 batches are fully independent — already parallel.
3. Pass 3 batches are mostly independent (grouped by file type) — already parallel.
4. Validation could run in parallel with consolidation if the consolidator doesn't need validation results. However, the current design makes validation a prerequisite for consolidation (failed reports must be regenerated first).

### Potential Failure Modes
1. **Subprocess crash mid-batch**: Monitor detects stall or error exit; batch marked FAIL; retry once; if still fails, continue with reduced coverage and note in summary.
2. **Gate failure on batch report**: Missing sections or profiles. Retry the batch subprocess once. If still fails, record as incomplete coverage.
3. **Validation CRITICAL FAIL**: False-negative DELETE found. Halt entire pass, report which batches need re-audit.
4. **Token exhaustion in batch subprocess**: Claude hits max turns before completing all files. Detect via `INCOMPLETE` status. Record partial results and assign remaining files to a new batch.
5. **Huge repositories**: Inventory with 10,000+ files could produce 200+ batches. Need configurable concurrency cap and staggered launch to avoid overwhelming the system.
6. **Missing prior-pass results**: If `--pass structural` is run without prior Pass 1 results, the executor must either error clearly or run Pass 1 first.
