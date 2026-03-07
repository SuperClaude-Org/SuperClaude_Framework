---
source_skill: sc-cleanup-audit-protocol
source_command: /sc:cleanup-audit
step_count: 12
parallel_groups: 3
gate_count: 10
agent_count: 5
complexity: high
---

# Portification Analysis: cleanup-audit

## Source Components

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| Skill | `src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md` | 134 | Multi-pass read-only repository audit protocol |
| Rule: Pass 1 | `rules/pass1-surface-scan.md` | 78 | Surface scan classification rules (DELETE/REVIEW/KEEP) |
| Rule: Pass 2 | `rules/pass2-structural-audit.md` | 80 | Structural audit with 8-field mandatory profiles |
| Rule: Pass 3 | `rules/pass3-cross-cutting.md` | 72 | Cross-cutting sweep with duplication matrices |
| Rule: Verification | `rules/verification-protocol.md` | 86 | Evidence requirements and cross-reference checklist |
| Rule: Dynamic Use | `rules/dynamic-use-checklist.md` | 118 | 5 dynamic loading patterns to check before DELETE |
| Script: Inventory | `scripts/repo-inventory.sh` | 134 | Shell script for file enumeration and domain classification |
| Template: Batch Report | `templates/batch-report.md` | 78 | Per-batch output format |
| Template: Pass Summary | `templates/pass-summary.md` | 95 | Consolidated pass summary format |
| Template: Final Report | `templates/final-report.md` | 109 | Executive final report format |
| Template: Finding Profile | `templates/finding-profile.md` | 68 | Mandatory per-file profile formats (Pass 2: 8-field, Pass 3: 7-field) |
| Agent: audit-scanner | `agents/audit-scanner.md` | ~80 | Pass 1 Haiku surface scanner |
| Agent: audit-analyzer | `agents/audit-analyzer.md` | ~100 | Pass 2 Sonnet structural auditor |
| Agent: audit-comparator | `agents/audit-comparator.md` | ~90 | Pass 3 Sonnet cross-cutting comparator |
| Agent: audit-consolidator | `agents/audit-consolidator.md` | ~80 | Report merger and synthesizer |
| Agent: audit-validator | `agents/audit-validator.md` | ~70 | Spot-check quality validator |

## Step Graph

### Step 1: repo-inventory (pure-programmatic)
- **Type**: pure-programmatic
- **Inputs**: target path, git ls-files output
- **Output**: `inventory.json` — structured file inventory with domain grouping, type distribution, batch assignments
- **Gate**: LIGHT (file exists, non-empty JSON)
- **GateMode**: BLOCKING
- **Agent**: none
- **Parallel**: no
- **Timeout**: 30s
- **Retry**: 0 (deterministic)
- **Notes**: Reimplements `repo-inventory.sh` in Python. Enumerates files via `git ls-files`, classifies into domains (infrastructure, frontend, backend, tests, documentation, config, assets, other), computes batch assignments by domain with configurable batch size. Pure computation, no Claude needed.

### Step 2: configure-passes (pure-programmatic)
- **Type**: pure-programmatic
- **Inputs**: `inventory.json`, CLI arguments (--pass, --focus, --batch-size)
- **Output**: `pass-config.json` — pass configurations with batch assignments, agent types, file lists per batch
- **Gate**: LIGHT (file exists, valid JSON)
- **GateMode**: BLOCKING
- **Agent**: none
- **Parallel**: no
- **Timeout**: 10s
- **Retry**: 0 (deterministic)
- **Notes**: Builds per-pass, per-batch configuration. Filters inventory by focus area. Assigns agent types (haiku for Pass 1, sonnet for Pass 2/3). Creates batch file lists respecting batch-size parameter. Output consumed by all downstream pass steps.

### Step 3: pass1-surface-scan (claude-assisted, batched parallel)
- **Type**: claude-assisted (batched parallel group)
- **Inputs**: `pass-config.json`, batch file lists, `rules/pass1-surface-scan.md`, `rules/dynamic-use-checklist.md`
- **Output**: `pass1/batch-{NN}.md` — per-batch surface scan reports
- **Gate**: STANDARD (min 30 lines, required frontmatter: `status`, `batch`, `files_audited`, `files_total`)
- **GateMode**: BLOCKING
- **Agent**: audit-scanner (Haiku, maxTurns=20)
- **Parallel**: yes — up to 7-8 concurrent batches within the pass
- **Timeout**: 300s per batch subprocess
- **Retry**: 1 attempt per failed batch
- **Notes**: Each batch subprocess receives a file list and writes a batch report. Fan-out pattern: executor launches N concurrent Claude subprocesses via ThreadPoolExecutor. Each batch writes its report independently to disk. Incremental checkpointing: if a batch fails, only that batch retries.

### Step 4: pass1-gate (pure-programmatic)
- **Type**: pure-programmatic
- **Inputs**: all `pass1/batch-*.md` files
- **Output**: `pass1/gate-results.json` — per-batch gate status, aggregated coverage metric
- **Gate**: STANDARD (all batches must have gate status, coverage >= 90%)
- **GateMode**: BLOCKING
- **Agent**: none
- **Parallel**: no
- **Timeout**: 15s
- **Retry**: 0
- **Notes**: Runs programmatic gate checks on each batch report. Validates required sections (Safe to Delete, Need Decision, Keep, Summary), mandatory frontmatter fields, and minimum line count. Records which batches passed and which need regeneration. If any batch fails its gate, the executor retries only that batch (step 3 partial retry). Blocks before proceeding to pass 2.

### Step 5: pass1-validate (claude-assisted)
- **Type**: claude-assisted
- **Inputs**: `pass1/batch-*.md` (random sample), `rules/verification-protocol.md`
- **Output**: `pass1/validation.md` — spot-check results
- **Gate**: STANDARD (min 20 lines, required frontmatter: `status`, `findings_checked`, `discrepancies_found`)
- **GateMode**: TRAILING
- **Agent**: audit-validator (Sonnet, maxTurns=25)
- **Parallel**: no (single subprocess)
- **Timeout**: 300s
- **Retry**: 1
- **Notes**: 10% spot-check sampling (5 findings per 50 files). Validator re-tests claims independently. TRAILING gate mode: validation results inform quality but do not block pass 2 from starting. Discrepancies are recorded for consolidation step.

### Step 6: pass1-consolidate (claude-assisted)
- **Type**: claude-assisted
- **Inputs**: all `pass1/batch-*.md`, `pass1/validation.md`, `templates/pass-summary.md`
- **Output**: `pass1-summary.md` — consolidated Pass 1 summary
- **Gate**: STRICT (min 80 lines, required frontmatter: `status`, `total_files`, `coverage_pct`, `delete_count`, `review_count`, `keep_count`; semantic checks: has_required_sections, has_quality_gate_table)
- **GateMode**: BLOCKING
- **Agent**: audit-consolidator (Sonnet, maxTurns=40)
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Merges batch reports, deduplicates findings, extracts cross-agent patterns, produces aggregate metrics. Must follow pass-summary template. Consolidator also produces `pass1-keep-review.json` — the filtered file list for Pass 2 (files classified KEEP or REVIEW).

### Step 7: filter-pass2-files (pure-programmatic)
- **Type**: pure-programmatic
- **Inputs**: `pass1-summary.md`, `pass1/batch-*.md`, `inventory.json`
- **Output**: `pass2-config.json` — batch assignments for Pass 2 (KEEP/REVIEW files only)
- **Gate**: LIGHT (file exists, valid JSON with batch lists)
- **GateMode**: BLOCKING
- **Agent**: none
- **Parallel**: no
- **Timeout**: 15s
- **Retry**: 0
- **Notes**: Parses Pass 1 batch reports to extract file classifications. Filters to only KEEP and REVIEW files. Re-batches with Pass 2 batch size (default 25). Assigns sonnet agent type. Pure Python — no Claude needed.

### Step 8: pass2-structural-audit (claude-assisted, batched parallel)
- **Type**: claude-assisted (batched parallel group)
- **Inputs**: `pass2-config.json`, batch file lists, `rules/pass2-structural-audit.md`, `rules/verification-protocol.md`, `templates/finding-profile.md`, Pass 1 context
- **Output**: `pass2/batch-{NN}.md` — per-batch structural audit reports with 8-field profiles
- **Gate**: STRICT (min 50 lines, required frontmatter: `status`, `batch`, `files_audited`; semantic checks: has_mandatory_profiles, profiles_have_all_fields)
- **GateMode**: BLOCKING
- **Agent**: audit-analyzer (Sonnet, maxTurns=35)
- **Parallel**: yes — up to 7-8 concurrent batches
- **Timeout**: 600s per batch subprocess
- **Retry**: 1 per failed batch
- **Notes**: Deep structural audit with mandatory 8-field profiles per file. Each batch receives Pass 1 context (known issues). Gate enforces profile completeness — reports missing fields trigger regeneration. More expensive (Sonnet) and slower than Pass 1.

### Step 9: pass2-consolidate (claude-assisted)
- **Type**: claude-assisted
- **Inputs**: all `pass2/batch-*.md`, `pass1-summary.md`, `templates/pass-summary.md`
- **Output**: `pass2-summary.md` — consolidated Pass 2 summary
- **Gate**: STRICT (min 80 lines, required frontmatter: `status`, `total_files`, `coverage_pct`; semantic checks: has_required_sections, has_quality_gate_table)
- **GateMode**: BLOCKING
- **Agent**: audit-consolidator (Sonnet, maxTurns=40)
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Identical pattern to step 6 but for Pass 2. Also produces file groupings for Pass 3 (similar files identified during structural audit).

### Step 10: filter-pass3-files (pure-programmatic)
- **Type**: pure-programmatic
- **Inputs**: `pass2-summary.md`, `pass2/batch-*.md`, `inventory.json`
- **Output**: `pass3-config.json` — grouped batch assignments for Pass 3 (files grouped by similarity for cross-cutting comparison)
- **Gate**: LIGHT (file exists, valid JSON)
- **GateMode**: BLOCKING
- **Agent**: none
- **Parallel**: no
- **Timeout**: 15s
- **Retry**: 0
- **Notes**: Groups files by type/similarity for cross-cutting comparison (all docker-compose files together, all deploy scripts together, etc.). Uses domain classification from inventory plus file-type grouping. Re-batches with Pass 3 batch size (default 30).

### Step 11: pass3-cross-cutting (claude-assisted, batched parallel)
- **Type**: claude-assisted (batched parallel group)
- **Inputs**: `pass3-config.json`, batch file lists, `rules/pass3-cross-cutting.md`, Pass 1 + Pass 2 context, `templates/finding-profile.md`
- **Output**: `pass3/batch-{NN}.md` — per-batch cross-cutting reports with duplication matrices
- **Gate**: STRICT (min 40 lines, required frontmatter: `status`, `batch`, `files_audited`; semantic checks: has_duplication_matrix, has_7field_profiles)
- **GateMode**: BLOCKING
- **Agent**: audit-comparator (Sonnet, maxTurns=35)
- **Parallel**: yes — up to 7-8 concurrent batches
- **Timeout**: 600s per batch subprocess
- **Retry**: 1 per failed batch
- **Notes**: Groups similar files for comparative analysis. Mandatory duplication matrix when similar files detected. 7-field profiles. Tiered depth (deep for infra, medium for source, light for assets).

### Step 12: final-report (claude-assisted)
- **Type**: claude-assisted
- **Inputs**: `pass1-summary.md`, `pass2-summary.md`, all `pass3/batch-*.md`, `templates/final-report.md`
- **Output**: `final-report.md` — executive summary with prioritized action items
- **Gate**: STRICT (min 150 lines, required frontmatter: `status`, `total_files`, `passes_completed`, `delete_count`, `consolidate_count`, `flag_count`; semantic checks: has_executive_summary, has_action_items, has_methodology)
- **GateMode**: BLOCKING
- **Agent**: audit-consolidator (Sonnet, maxTurns=40)
- **Parallel**: no
- **Timeout**: 900s
- **Retry**: 1
- **Notes**: Produces final report with executive summary, prioritized action items (immediate/decision/code-changes), cross-cutting findings, discovered issues registry, duplication matrix, audit methodology. Uses ultrathink-level synthesis. This is the most expensive single step.

## Parallel Groups

| Group | Steps | Max Concurrency | Rationale |
|-------|-------|-----------------|-----------|
| 1 | step-3 (pass1-surface-scan batches) | 7-8 | Independent file batches, fan-out pattern |
| 2 | step-8 (pass2-structural-audit batches) | 7-8 | Independent file batches, fan-out pattern |
| 3 | step-11 (pass3-cross-cutting batches) | 7-8 | Independent file-group batches, fan-out pattern |

Note: Inter-pass parallelism is NOT possible. Passes are strictly sequential because each pass consumes the previous pass's output.

## Gates Summary

| Step | Tier | GateMode | Frontmatter | Min Lines | Semantic Checks |
|------|------|----------|-------------|-----------|-----------------|
| 1: repo-inventory | LIGHT | BLOCKING | — | — | valid JSON structure |
| 2: configure-passes | LIGHT | BLOCKING | — | — | valid JSON with batch lists |
| 3: pass1-surface-scan | STANDARD | BLOCKING | status, batch, files_audited, files_total | 30 | — |
| 4: pass1-gate | STANDARD | BLOCKING | — | — | all_batches_gated, coverage_met |
| 5: pass1-validate | STANDARD | TRAILING | status, findings_checked, discrepancies_found | 20 | — |
| 6: pass1-consolidate | STRICT | BLOCKING | status, total_files, coverage_pct, delete_count, review_count, keep_count | 80 | has_required_sections, has_quality_gate_table |
| 7: filter-pass2-files | LIGHT | BLOCKING | — | — | valid JSON |
| 8: pass2-structural-audit | STRICT | BLOCKING | status, batch, files_audited | 50 | has_mandatory_profiles, profiles_have_all_fields |
| 9: pass2-consolidate | STRICT | BLOCKING | status, total_files, coverage_pct | 80 | has_required_sections, has_quality_gate_table |
| 10: filter-pass3-files | LIGHT | BLOCKING | — | — | valid JSON |
| 11: pass3-cross-cutting | STRICT | BLOCKING | status, batch, files_audited | 40 | has_duplication_matrix, has_7field_profiles |
| 12: final-report | STRICT | BLOCKING | status, total_files, passes_completed, delete_count, consolidate_count, flag_count | 150 | has_executive_summary, has_action_items, has_methodology |

## Agent Delegation Map

| Agent | Model | maxTurns | Used In Steps | Parallel | Contract |
|-------|-------|----------|--------------|----------|----------|
| audit-scanner | Haiku | 20 | 3 (Pass 1 batches) | Yes (7-8x) | Classify files as DELETE/REVIEW/KEEP with grep evidence |
| audit-analyzer | Sonnet | 35 | 8 (Pass 2 batches) | Yes (7-8x) | Produce 8-field profiles with evidence per file |
| audit-comparator | Sonnet | 35 | 11 (Pass 3 batches) | Yes (7-8x) | Cross-cutting comparison with duplication matrices |
| audit-consolidator | Sonnet | 40 | 6, 9, 12 | No | Merge batch reports into pass summaries / final report |
| audit-validator | Sonnet | 25 | 5 | No | 10% spot-check of findings with independent verification |

## Data Flow Diagram

```
[target-path + CLI args]
         │
    step-1: repo-inventory (programmatic)
         │
    [inventory.json]
         │
    step-2: configure-passes (programmatic)
         │
    [pass-config.json]
         │
    ┌──────────────────────────────────────┐
    │  step-3: pass1-surface-scan          │
    │  ┌─batch-01─┐┌─batch-02─┐...        │  (fan-out: 7-8 concurrent)
    │  └──────────┘└──────────┘            │
    └──────────────────────────────────────┘
         │
    [pass1/batch-*.md]
         │
    step-4: pass1-gate (programmatic) ──→ retry failed batches in step 3
         │
    ┌────┴────┐
    │         │
step-5:    step-6: pass1-consolidate
validate      │
(TRAILING)    │
    │    [pass1-summary.md]
    └─────────┤
              │
    step-7: filter-pass2-files (programmatic)
              │
    [pass2-config.json]
              │
    ┌──────────────────────────────────────┐
    │  step-8: pass2-structural-audit      │
    │  ┌─batch-01─┐┌─batch-02─┐...        │  (fan-out: 7-8 concurrent)
    │  └──────────┘└──────────┘            │
    └──────────────────────────────────────┘
              │
    [pass2/batch-*.md]
              │
    step-9: pass2-consolidate
              │
    [pass2-summary.md]
              │
    step-10: filter-pass3-files (programmatic)
              │
    [pass3-config.json]
              │
    ┌──────────────────────────────────────┐
    │  step-11: pass3-cross-cutting        │
    │  ┌─batch-01─┐┌─batch-02─┐...        │  (fan-out: 7-8 concurrent)
    │  └──────────┘└──────────┘            │
    └──────────────────────────────────────┘
              │
    [pass3/batch-*.md]
              │
    step-12: final-report
              │
    [final-report.md]
```

## Classification Summary

| Category | Count | Steps |
|----------|-------|-------|
| Pure Programmatic | 5 | 1 (repo-inventory), 2 (configure-passes), 4 (pass1-gate), 7 (filter-pass2-files), 10 (filter-pass3-files) |
| Claude-Assisted | 7 | 3 (pass1-scan), 5 (pass1-validate), 6 (pass1-consolidate), 8 (pass2-audit), 9 (pass2-consolidate), 11 (pass3-cross-cutting), 12 (final-report) |
| Hybrid | 0 | — |
| Pure Inference | 0 | — |

## Recommendations

1. **Repo inventory should be 100% programmatic**: The shell script `repo-inventory.sh` is already deterministic; reimplement in Python for portability and testability. This avoids shell subprocess dependency.

2. **File filtering between passes should be programmatic**: Parsing batch reports to extract file classifications (KEEP/REVIEW/DELETE) and rebuilding batch lists is a structural operation — regex on markdown. No LLM needed.

3. **Gate checks on batch reports should be programmatic**: Validating mandatory profile fields, required sections, and frontmatter can be done with pure Python regex/YAML parsing. This removes one Claude subprocess per pass.

4. **Validation (step 5) should use TRAILING gate**: The spot-check validation is a quality signal but should not block the pipeline. If discrepancies are found, they're noted in the final report. Using TRAILING mode avoids unnecessary pipeline stalls.

5. **Budget planning is critical**: With potentially 20+ Claude subprocesses (7-8 batches x 3 passes + 3 consolidators + 1 validator + 1 final report), turn budget management via TurnLedger is essential. Pre-launch guards should prevent launching when insufficient budget remains.

6. **Pass-level resume is the natural resume boundary**: On failure, the pipeline should be resumable at the pass level. Within a pass, individual batch failures should retry without restarting the entire pass. Between passes, resume should skip completed passes.

7. **Model-per-agent matters for cost**: Pass 1 uses Haiku (cheaper, faster) while Pass 2/3 use Sonnet. The pipeline should enforce model selection per agent type, not a global model setting.

8. **Subprocess isolation is critical**: Each batch subprocess should have isolated work directories to prevent file conflicts when running 7-8 concurrent agents writing to disk.
