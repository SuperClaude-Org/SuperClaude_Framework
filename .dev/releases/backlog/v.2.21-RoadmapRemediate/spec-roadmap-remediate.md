---
title: "Roadmap Remediation Loop"
version: "2.21"
codename: "RoadmapRemediate"
status: draft
author: brainstorm-session
date: 2026-03-09
scope: src/superclaude/cli/roadmap/
dependencies:
  - v2.20-WorkflowEvolution (pipeline infrastructure)
estimated_effort: 3-5 sprints
risk: medium
---

# v2.21 — Roadmap Remediation Loop

## 1. Problem Statement

The current `roadmap run` pipeline generates a roadmap and validates it, but when
validation surfaces findings (BLOCKING, WARNING), there is no automated path from
"findings exist" to "findings are fixed." The user must:

1. Read the merged validation report manually
2. Interpret fix guidance for each finding
3. Craft custom prompts to fix the roadmap artifacts
4. Spawn agents manually (or write ad-hoc prompt wrappers)
5. Track which findings were addressed
6. Hope the fixes didn't introduce new issues (no re-validation)

This gap was exposed during v2.20 planning, where the validation report surfaced
14 findings (4 BLOCKING, 7 WARNING, 3 INFO). The remediation required a manually
composed prompt with explicit file-edit constraints, agent delegation via
`/sc:task-unified`, and manual status tracking in `reflect-merged.md`. There was
no automated re-validation to certify the roadmap was clean.

### Evidence of the Gap

- `v2.20-WorkflowEvolution/validate/reflect-merged.md` — 14 findings, manual
  remediation status tracking added post-hoc
- `v2.20-WorkflowEvolution/adversarial-forensic-validation/validate/merged-validation-report.md`
  — 12 findings from a second validation pass, no automated fix path
- `v2.20-WorkflowEvolution/tasklistValidate/TasklistPatchPlan.md` — manual patch
  plan created because tasklists were generated from an un-remediated roadmap
- User had to craft a custom prompt constraining edits to `roadmap.md`,
  `extraction.md`, and `reflect-merged.md` only

## 2. Proposed Solution

Extend the existing `roadmap run` pipeline with three new steps that execute
**after** the current validation step. No new CLI command — remediation is part
of the default `roadmap run` workflow.

### 2.1 Extended Pipeline (12 steps)

```
Step 1:  extract
Step 2a: generate-A  }  parallel
Step 2b: generate-B  }
Step 3:  diff
Step 4:  debate
Step 5:  score
Step 6:  merge
Step 7:  test-strategy
Step 8:  spec-fidelity
Step 9:  validate           ← existing (adversarial multi-agent)
Step 10: remediate          ← NEW
Step 11: certify            ← NEW
```

### 2.2 Step 9 Enhancement: User Prompt After Validation

After the existing validation step completes, the pipeline:

1. Parses the merged validation report to extract finding counts by severity
2. Prints a brief terminal summary
3. Prompts the user with Y/n

```
┌──────────────────────────────────────────────┐
│ Validation Complete                          │
│                                              │
│ 4 BLOCKING  7 WARNING  3 INFO               │
│                                              │
│ BLOCKING:                                    │
│  F-01: interleave_ratio wrong type           │
│  F-02: timeline contradiction (11 vs 10)     │
│  F-03: OQ numbering drift                    │
│  F-04: traceability gaps                     │
│                                              │
│ WARNING:                                     │
│  F-05: test phase assignment conflict        │
│  F-06: 2 tests missing from roadmap          │
│  F-08: P1.3 compound deliverable             │
│  F-09: P4.1 compound deliverable             │
│  F-10: P4.2 compound deliverable             │
│  F-11: P4.3 compound deliverable             │
│  F-12: P4.4 compound deliverable             │
│                                              │
│ INFO:                                        │
│  F-07: pre-impl no code deliverables         │
│  F-13: frontmatter count fields              │
│  F-14: interleave ratio interpretation       │
│                                              │
│ Remediate?                                   │
│  [1] BLOCKING only (4 findings)              │
│  [2] BLOCKING + WARNING (11 findings)        │
│  [3] All (14 findings)                       │
│  [n] Skip remediation                        │
└──────────────────────────────────────────────┘
```

**If user enters n**: Pipeline ends. State saved as `validated-with-issues`.
The validation report remains on disk for manual review.

**If user enters 1, 2, or 3**: Pipeline continues to Step 10 (remediate) with
the selected severity scope. Findings outside the chosen scope are marked
SKIPPED in the remediation tasklist.

**If 0 BLOCKING and 0 WARNING and 0 INFO**: Skip prompt entirely, proceed
directly to certify with a no-op remediation (nothing to fix).

### 2.3 Step 10: Remediate

#### 2.3.1 Finding Extraction

Parse the merged validation report (`validate/reflect-merged.md` or
`validate/merged-validation-report.md`) into structured `Finding` objects:

```python
@dataclass
class Finding:
    id: str                    # "F-01", "F-02", etc.
    severity: str              # "BLOCKING", "WARNING", "INFO"
    dimension: str             # "Schema", "Structure", "Traceability", etc.
    description: str           # One-line summary
    location: str              # "roadmap.md:§3.1" or "test-strategy.md:1-4"
    evidence: str              # What was expected vs found
    fix_guidance: str          # Concrete steps to resolve
    files_affected: list[str]  # ["roadmap.md", "test-strategy.md"]
    status: str                # "PENDING", "FIXED", "FAILED", "SKIPPED"
    agreement_category: str    # "BOTH_AGREE", "ONLY_A", "ONLY_B", "CONFLICT"
```

#### 2.3.2 Filtering

Based on the user's selection at the prompt (§2.2):

- **Option 1 (BLOCKING only)**: Only BLOCKING findings with fix guidance → proceed.
  WARNING and INFO → SKIPPED.
- **Option 2 (BLOCKING + WARNING)**: BLOCKING and WARNING findings with fix
  guidance → proceed. INFO → SKIPPED.
- **Option 3 (All)**: BLOCKING, WARNING, and INFO findings with fix guidance →
  proceed. Only NO_ACTION_REQUIRED and OUT_OF_SCOPE → SKIPPED.

In all cases, findings already marked NO_ACTION_REQUIRED or OUT_OF_SCOPE in
the validation report are always SKIPPED regardless of the user's selection.

#### 2.3.3 Agent Batching Strategy: Batch by File

Group actionable findings by their primary target file:

```
Agent 1: roadmap.md        → [F-02, F-04, F-06, F-08, F-09, F-10, F-11]
Agent 2: test-strategy.md  → [F-01, F-05]
Agent 3: extraction.md     → [F-03]
```

- Agents touching different files run **in parallel**
- All findings for a single file go to **one agent** (avoids edit conflicts)
- Cross-file findings (e.g., F-05 spans roadmap.md + test-strategy.md) are
  included in **both** agents' prompts, with guidance on which file each
  agent should edit

#### 2.3.4 Agent Prompt Structure

Each remediation agent receives:

```
You are a remediation specialist. Apply ONLY the fixes listed below.
Do not change anything else. Do not add commentary or explanations.

## Target File: {file_path}

## Findings to Fix

### {finding.id} [{finding.severity}] {finding.description}
- Location: {finding.location}
- Evidence: {finding.evidence}
- Fix Guidance: {finding.fix_guidance}

### {finding.id} [{finding.severity}] ...
(repeat for each finding targeting this file)

## Constraints
- Edit ONLY {file_path}
- Apply ONLY the fixes described above
- Preserve existing YAML frontmatter structure
- Preserve existing markdown heading hierarchy
- Do not reorder sections unless fix guidance explicitly requires it
```

#### 2.3.5 Editable Files (Constraint)

Remediation agents may ONLY edit:
- `roadmap.md`
- `extraction.md`
- `test-strategy.md`

Phase tasklist files do NOT exist at this point in the pipeline. Tasklist
generation (`sc:tasklist`) runs downstream after the roadmap is certified.

#### 2.3.6 Output

Emit `remediation-tasklist.md` as a standalone file (not phase-tasklist format):

```markdown
---
type: remediation-tasklist
source_report: validate/reflect-merged.md
generated: 2026-03-09T14:30:00Z
total_findings: 14
actionable: 10
skipped: 4
---

# Remediation Tasklist

## BLOCKING

- [x] F-01 | test-strategy.md | FIXED — replaced interleave_ratio '1:2' with 0.83
- [x] F-02 | roadmap.md | FIXED — updated Executive Summary to 10 sprints
- [x] F-03 | roadmap.md, extraction.md | FIXED — renumbered OQ decisions
- [x] F-04 | roadmap.md | FIXED — added NFR-006/007 verification paths

## WARNING

- [x] F-05 | roadmap.md, test-strategy.md | FIXED — moved test to Phase 1
- [x] F-06 | roadmap.md | FIXED — added 2 missing tests to §3.2
- [x] F-08 | roadmap.md | FIXED — decomposed into 3 deliverables
- [x] F-09 | roadmap.md | FIXED — decomposed into 4 deliverables
- [x] F-10 | roadmap.md | FIXED — decomposed into 4 deliverables
- [x] F-11 | roadmap.md | FIXED — decomposed into 4 deliverables

## SKIPPED

- F-07 | NO_ACTION_REQUIRED — acceptable by design
- F-12 | NO_ACTION_REQUIRED
- F-13 | NO_ACTION_REQUIRED
- F-14 | NO_ACTION_REQUIRED
```

### 2.4 Step 11: Certify

#### 2.4.1 Purpose

Lightweight re-validation scoped to the fixed findings. Confirms remediation
was applied correctly without running the full adversarial multi-agent debate.

#### 2.4.2 Approach: Single-Agent Scoped Review

One agent, one pass, checklist verification. The agent receives only the
**relevant sections** of each artifact (not full file content) — specifically,
the sections surrounding each finding's location. This keeps token cost low
while maintaining verification accuracy.

```
You are a certification specialist. The following N findings were reported
during validation and remediated. For each finding, verify the fix was
applied correctly by checking the referenced location in the artifacts.

Report PASS or FAIL for each finding with a one-line justification.

## Findings to Verify

### F-01 [BLOCKING] interleave_ratio wrong type
- Original issue: frontmatter uses string '1:2', should be numeric
- Fix applied: replaced with numeric 0.83
- Check: verify test-strategy.md frontmatter has numeric interleave_ratio

### F-02 [BLOCKING] timeline contradiction
- Original issue: Executive Summary says 11 sprints, Timeline says 10
- Fix applied: updated Executive Summary to 10 sprints
- Check: verify roadmap.md Executive Summary matches Timeline Summary

(repeat for each fixed finding)
```

#### 2.4.3 Output: certification-report.md

```markdown
---
findings_verified: 10
findings_passed: 10
findings_failed: 0
certified: true
certification_date: 2026-03-09T15:00:00Z
---

# Certification Report

## Per-Finding Results

| Finding | Severity | Result | Justification |
|---------|----------|--------|---------------|
| F-01 | BLOCKING | PASS | interleave_ratio is now 0.83 (numeric) |
| F-02 | BLOCKING | PASS | Executive Summary now says 10 sprints |
| F-03 | BLOCKING | PASS | OQ IDs match extraction |
| F-04 | BLOCKING | PASS | NFR-006/007 have deliverables and tests |
| F-05 | WARNING | PASS | test moved to Phase 1 |
| ... | ... | ... | ... |

## Summary

All 10 findings verified. Roadmap certified for tasklist generation.
```

#### 2.4.4 Certification Outcomes

- **All pass** → State updated to `certified: true`, `tasklist_ready: true`.
  Pipeline completes successfully.
- **Some fail** → State updated to `certified-with-caveats`. The certification
  report lists failures. Pipeline completes (does NOT loop). The user can
  re-run `roadmap validate` for a fresh full report if desired.

**No automatic loop.** If certification finds remaining issues, it reports
them and stops. The user stays in control.

#### 2.4.5 Certification Gate

```python
CERTIFY_GATE = GateCriteria(
    required_frontmatter_fields=[
        "findings_verified",
        "findings_passed",
        "findings_failed",
        "certified",
    ],
    min_lines=15,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="Certification frontmatter has empty values",
        ),
        SemanticCheck(
            name="per_finding_table_present",
            check_fn=_has_per_finding_table,
            failure_message="No per-finding results table in certification report",
        ),
    ],
)
```

## 3. State Management

### 3.1 .roadmap-state.json Extensions

New step entries alongside existing ones:

```json
{
  "schema_version": 2,
  "steps": {
    "extract": {"status": "PASS", ...},
    "generate-opus-architect": {"status": "PASS", ...},
    "...": "...",
    "validate": {
      "status": "PASS",
      "blocking_count": 4,
      "warning_count": 7,
      "info_count": 3,
      "report_file": "validate/reflect-merged.md"
    },
    "remediate": {
      "status": "PASS",
      "scope": "blocking+warning",
      "findings_total": 14,
      "findings_actionable": 10,
      "findings_fixed": 10,
      "findings_failed": 0,
      "findings_skipped": 4,
      "agents_spawned": 3,
      "tasklist_file": "remediation-tasklist.md"
    },
    "certify": {
      "status": "PASS",
      "findings_verified": 10,
      "findings_passed": 10,
      "findings_failed": 0,
      "certified": true,
      "report_file": "certification-report.md"
    }
  },
  "validation": {"status": "certified"},
  "fidelity_status": "pass"
}
```

### 3.2 Resume Behavior

`--resume` works identically to existing steps:

- If `validate` output passes its gate → skip to `remediate`
- If `remediate` output exists and `remediation-tasklist.md` shows all FIXED →
  skip to `certify`
- If `certify` output passes its gate → pipeline complete, nothing to do

Resume checks are based on gate evaluation of output files, consistent with
the existing `_apply_resume()` logic.

### 3.3 Validation Status Lifecycle

```
validated-with-issues  → user said N at prompt (or pipeline halted)
remediated             → remediate completed, certify pending
certified              → all findings verified, tasklist_ready
certified-with-caveats → some findings failed certification
```

## 4. Implementation Plan

### 4.1 New Files

| File | Purpose | Est. Lines |
|------|---------|------------|
| `remediate_parser.py` | Parse validation reports → `Finding` objects | 120-150 |
| `remediate_prompts.py` | Build scoped fix prompts per file-group | 80-100 |
| `remediate_executor.py` | Orchestrate extract → batch → spawn → collect | 200-250 |
| `certify_prompts.py` | Build certification verification prompt | 60-80 |
| `certify_gates.py` | Gate definition for certification step | 40-50 |

### 4.2 Modified Files

| File | Change | Impact |
|------|--------|--------|
| `executor.py` | Add validate→prompt→remediate→certify to `_build_steps()` | Medium |
| `executor.py` | Add user prompt logic after validation summary | Medium |
| `executor.py` | Extend `_get_all_step_ids()` with new step IDs | Trivial |
| `executor.py` | Extend `_save_state()` for new step metadata | Low |
| `models.py` | Add `Finding` dataclass | Low |
| `models.py` | Extend `RoadmapConfig` — no new fields needed | None |
| `validate_executor.py` | Return structured finding counts (already does this) | None |

### 4.3 New Test Files

| File | Coverage |
|------|----------|
| `tests/roadmap/test_remediate_parser.py` | Finding extraction from various report formats |
| `tests/roadmap/test_remediate_prompts.py` | Prompt construction, file grouping, constraint injection |
| `tests/roadmap/test_remediate_executor.py` | Orchestration flow, agent batching, status collection |
| `tests/roadmap/test_certify_prompts.py` | Certification prompt with finding checklist |
| `tests/roadmap/test_certify_gates.py` | Gate criteria validation |
| `tests/roadmap/test_pipeline_integration.py` | End-to-end: validate → prompt → remediate → certify |

### 4.4 Implementation Phases

**Phase 1: Parser + Models (1 sprint)**
- `Finding` dataclass in `models.py`
- `remediate_parser.py` — parse merged validation reports
- Fallback parser for individual reflect reports when merged is unavailable
- Deduplication logic for findings from multiple individual reports
- Unit tests for parser against all known report formats:
  - `reflect-merged.md` format (with remediation status column)
  - `merged-validation-report.md` format (without remediation status)
  - Individual `reflect-*.md` reports (fallback path)

**Phase 2: Remediation Executor (1-2 sprints)**
- `remediate_prompts.py` — prompt builders with file-scoping constraints
- `remediate_executor.py` — finding grouping, agent spawning, result collection
- `remediation-tasklist.md` emission
- Integration with `execute_pipeline()` step model

**Phase 3: Certification (1 sprint)**
- `certify_prompts.py` — single-agent verification prompt
- `certify_gates.py` — gate criteria for certification report
- `certification-report.md` emission

**Phase 4: Pipeline Integration (0.5-1 sprint)**
- Wire new steps into `_build_steps()`
- Add user prompt after validation
- Extend state management
- Resume support for new steps
- End-to-end integration tests

## 5. Design Constraints

### 5.1 Architectural Constraints (inherited from pipeline)

- **Context isolation**: Each agent subprocess receives only its prompt and
  `--file` inputs. No `--continue`, `--session`, or `--resume` flags (FR-003).
- **Pure prompts**: All prompt builders are pure functions — no I/O, no
  subprocess calls, no side effects (NFR-004).
- **Unidirectional imports**: `remediate_*` and `certify_*` modules may import
  from `pipeline.models` and `roadmap.models`, but NOT vice versa (NFR-007).
- **Atomic writes**: All file writes use tmp + `os.replace()` pattern.
- **No new subprocess abstractions**: Reuse existing `ClaudeProcess` from
  `pipeline.process` (per roadmap constraint).

### 5.2 Scope Constraints

- Remediation agents may ONLY edit: `roadmap.md`, `extraction.md`,
  `test-strategy.md`
- Phase tasklist files are NOT in scope — they are generated downstream
- No automatic remediation loop — single pass, then certify, then done
- User selects remediation scope at prompt (BLOCKING / +WARNING / All)

### 5.3 Non-Goals

- Full re-validation (adversarial multi-agent) after remediation — that is
  what `roadmap validate` is for, and the user can invoke it manually
- Tasklist-level remediation — tasklists are derived artifacts; fix the source
- Per-finding cherry-picking (fix F-01 but skip F-02 within the same severity
  tier) — user selects severity scope, not individual findings

## 6. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Remediation agent introduces new issues | Medium | Medium | Certification step catches regressions; user can re-run validate |
| Report format changes break parser | Low | High | Parser tests against multiple known formats; graceful degradation |
| Cross-file findings cause conflicting edits | Low | Medium | Batch-by-file strategy eliminates concurrent edits to same file |
| User interrupts during remediation | Low | Low | Resume support picks up from last completed step |
| Certification agent is too lenient | Medium | Low | Gate criteria enforce structured output; user can re-run full validate |

## 7. Success Criteria

- SC-001: `roadmap run` completes all 12 steps without manual intervention when
  user approves remediation
- SC-002: Remediation fixes ≥90% of BLOCKING findings on first pass
- SC-003: Certification correctly identifies unfixed findings (no false passes)
- SC-004: `--resume` correctly skips completed remediation/certification steps
- SC-005: No edits to files outside the allowed set (roadmap.md, extraction.md,
  test-strategy.md)
- SC-006: Pipeline time increase ≤30% over current validate-only pipeline
  (remediate + certify should be fast — scoped prompts, single-agent certify)
- SC-007: `remediation-tasklist.md` accurately reflects all findings and their
  final status
- SC-008: `.roadmap-state.json` schema remains backward-compatible (new fields
  are additive, existing consumers unaffected)

## 8. Resolved Design Questions

- **OQ-001 [RESOLVED]**: User prompt offers tiered remediation scope.
  The prompt groups findings by severity and presents three options:
  `[1] BLOCKING only  [2] BLOCKING + WARNING  [3] All (incl. INFO)`
  See §2.2 for updated prompt design.

- **OQ-002 [RESOLVED]**: Certification prompt includes only relevant sections,
  not full file content. Each finding's check references a specific location;
  the certify agent receives only the sections surrounding each fix, not the
  entire artifact. Reduces token cost while maintaining verification accuracy.

- **OQ-003 [RESOLVED]**: If the merged validation report is missing or
  malformed, remediation falls back to parsing individual reflect reports
  (`reflect-opus-architect.md`, `reflect-haiku-analyzer.md`, etc.). Findings
  from individual reports are deduplicated by location + description similarity.
  If no parseable reports exist at all, remediation is skipped with a warning.
