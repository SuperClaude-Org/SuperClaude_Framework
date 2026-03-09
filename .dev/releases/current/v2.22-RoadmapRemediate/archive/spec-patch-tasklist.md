---
type: spec-patch-tasklist
target: spec-roadmap-remediate.md
source: spec-panel-review.md
date: 2026-03-09
total_patches: 10
blocking_patches: 3
major_patches: 7
estimated_effort: single session
---

# Spec Patch Tasklist: v2.22 Roadmap Remediation Loop

All patches target a single file:
`/.dev/releases/backlog/v.2.22-RoadmapRemediate/spec-roadmap-remediate.md`

Patches are ordered by dependency — earlier patches may create sections
referenced by later patches.

---

## CRITICAL Patches (must complete before roadmap generation)

### P-01: Add §2.3.7 — Remediate Architectural Model [C-01]

**Location**: Insert new subsection after §2.3.6 (Output)

**Patch content**: Add section defining how remediate presents to the pipeline:

```markdown
#### 2.3.7 Pipeline Integration Model

The remediate step presents as a **single Step** to `execute_pipeline()`,
consistent with `validate_executor.py` which already manages its own internal
orchestration. The outer pipeline sees:

- **Step ID**: `remediate`
- **output_file**: `remediation-tasklist.md`
- **gate**: `REMEDIATE_GATE` (checks remediation-tasklist.md frontmatter and
  status entries)

Internally, `remediate_executor.py` manages:

1. Parse validation report → `Finding` objects
2. Filter by user-selected scope
3. Group findings by file
4. Snapshot target files (copy to `<file>.pre-remediate` for rollback)
5. Spawn one `ClaudeProcess` per file group, in parallel via `threading`
6. Collect exit codes, update `remediation-tasklist.md` with per-finding status
7. On any agent failure: execute rollback (see §2.3.8)

The `remediate_executor` does NOT use `execute_pipeline()` for its internal
agents. It uses `ClaudeProcess` directly, matching the pattern in
`validate_executor.py:validate_run_step()`.

```python
REMEDIATE_GATE = GateCriteria(
    required_frontmatter_fields=[
        "type",
        "source_report",
        "total_findings",
        "actionable",
        "skipped",
    ],
    min_lines=10,
    enforcement_tier="STRICT",
    semantic_checks=[
        SemanticCheck(
            name="frontmatter_values_non_empty",
            check_fn=_frontmatter_values_non_empty,
            failure_message="Remediation tasklist frontmatter has empty values",
        ),
        SemanticCheck(
            name="all_actionable_have_status",
            check_fn=_all_actionable_have_status,
            failure_message="Not all actionable findings have a FIXED/FAILED status",
        ),
    ],
)
```
```

**Acceptance**: Section explicitly states single-Step model, references
`ClaudeProcess` directly, and includes gate definition.

---

### P-02: Add §2.3.8 — Partial Failure and Rollback [C-02]

**Location**: Insert new subsection after §2.3.7 (Pipeline Integration Model)

**Patch content**:

```markdown
#### 2.3.8 Partial Failure and Rollback

Before spawning remediation agents, the executor snapshots all target files:

```
roadmap.md          → roadmap.md.pre-remediate
test-strategy.md    → test-strategy.md.pre-remediate
extraction.md       → extraction.md.pre-remediate
```

**Failure semantics**: If ANY remediation agent exits non-zero or times out:

1. **Halt** all remaining agents (if still running)
2. **Rollback** all target files from `.pre-remediate` snapshots
3. **Mark** all findings for the failed agent as FAILED in
   `remediation-tasklist.md`
4. **Mark** all cross-file findings involving the failed file as FAILED
   (even if the other agent succeeded — half-applied cross-file fixes
   create worse inconsistencies than the original finding)
5. **Set** remediate step status to FAIL
6. **Pipeline halts** — consistent with existing parallel group behavior
   where any failure stops the pipeline

**On full success**: Delete `.pre-remediate` snapshots. Set all agent-targeted
findings to FIXED.

**Rationale**: Rollback-on-any-failure is preferred over partial success because
cross-file findings (e.g., F-05) create consistency dependencies between files.
Keeping one side of a cross-file fix while the other failed produces artifacts
in a worse state than before remediation.
```

**Acceptance**: Section defines snapshot, rollback trigger, cross-file marking,
and cleanup on success.

---

### P-03: Add Zero-Findings Guard to §2.3.2 and §2.2 [C-03]

**Location**: Two edits — §2.2 and §2.3.2

**Patch 3a** — Amend §2.2, replace the "0 BLOCKING and 0 WARNING and 0 INFO"
paragraph:

```markdown
**If 0 BLOCKING and 0 WARNING**: Skip prompt entirely. If also 0 INFO,
proceed directly to certify with a no-op (nothing to fix). If INFO findings
exist, skip remediation (INFO-only remediation is low value) and proceed
to certify.
```

**Patch 3b** — Amend §2.3.2, add guard at the top of the section:

```markdown
**Zero-findings guard**: If filtering produces 0 actionable findings (all
findings are SKIPPED due to NO_ACTION_REQUIRED, OUT_OF_SCOPE, or severity
below the user's selected scope), the remediate step emits a
`remediation-tasklist.md` with `actionable: 0` and all entries marked SKIPPED.
The certify step receives this and produces a `certification-report.md` with
`findings_verified: 0`, `certified: true` — vacuously certified since there
was nothing to fix.
```

**Acceptance**: Both the user prompt and the filtering logic define behavior
for 0-actionable-findings explicitly.

---

## MAJOR Patches (complete before tasklist generation)

### P-04: Refine SC-002 Measurement [M-01]

**Location**: §7, SC-002 entry

**Replace**:
```
- SC-002: Remediation fixes ≥90% of BLOCKING findings on first pass
```

**With**:
```
- SC-002: ≥90% of BLOCKING findings receive PASS in the certification report
  (§2.4.3). Measurement: `findings_passed / findings_verified` where severity
  is BLOCKING.
```

**Acceptance**: SC-002 defines the measurement instrument (certification report)
and formula.

---

### P-05: Refine SC-006 Baseline [M-02]

**Location**: §7, SC-006 entry

**Replace**:
```
- SC-006: Pipeline time increase ≤30% over current validate-only pipeline
  (remediate + certify should be fast — scoped prompts, single-agent certify)
```

**With**:
```
- SC-006: Steps 10-11 (remediate + certify) add ≤30% wall-clock time relative
  to the wall-clock time of steps 1-9 in the same run. Baseline is measured
  from step 1 start to step 9 completion.
```

**Acceptance**: Baseline is defined as same-run steps 1-9 wall-clock time.

---

### P-06: Add Cross-File Prompt Example to §2.3.4 [M-03]

**Location**: Insert after the existing prompt template in §2.3.4

**Patch content**:

```markdown
**Cross-file finding example**: Finding F-05 spans roadmap.md and
test-strategy.md. Each agent receives a scoped version:

Agent 1 (roadmap.md) prompt fragment:
```
### F-05 [WARNING] test phase assignment conflict
- Location: roadmap.md:§3.1 Phase 1 Tests
- Evidence: test_fidelity_deviation_dataclass listed under Phase 2 in
  test-strategy.md but should be Phase 1 per roadmap
- Fix Guidance (YOUR FILE): Add test_fidelity_deviation_dataclass to the
  Phase 1 test listing in §3.1. Do NOT modify Phase 2.
- Note: The test-strategy.md side of this fix is handled by a separate agent.
```

Agent 2 (test-strategy.md) prompt fragment:
```
### F-05 [WARNING] test phase assignment conflict
- Location: test-strategy.md:§2.1 Phase 2
- Evidence: test_fidelity_deviation_dataclass listed under Phase 2 but
  belongs in Phase 1 per roadmap
- Fix Guidance (YOUR FILE): Move test_fidelity_deviation_dataclass from
  §2.1 (Phase 2) to Phase 1 section. Adjust Phase 1 count to 10, Phase 2
  count to 5.
- Note: The roadmap.md side of this fix is handled by a separate agent.
```
```

**Acceptance**: Concrete example shows both sides of a cross-file finding
with file-scoped guidance and cross-reference note.

---

### P-07: Define Deduplication Rule in §8, OQ-003 [M-04]

**Location**: §8, OQ-003 entry — expand the deduplication definition

**Replace**:
```
  Findings from individual reports are deduplicated by location + description
  similarity.
```

**With**:
```
  Findings from individual reports are deduplicated using a two-step rule:
  1. **Location match**: Two findings are candidates for deduplication if they
     reference the same file AND their locations overlap or are within 5 lines
     of each other (e.g., "roadmap.md:§3.1" and "roadmap.md:lines 85-92" where
     §3.1 starts at line 83).
  2. **Severity resolution**: On match, take the higher severity (BLOCKING >
     WARNING > INFO). Merge fix guidance from both reports, preferring the more
     specific guidance.
  Findings that don't match any candidate are included as-is from their source
  report.
```

**Acceptance**: Deduplication rule is concrete, testable, and includes severity
resolution.

---

### P-08: Add §2.5 — Pipeline Execution Flow [M-05]

**Location**: Insert new section between §2.4 (Certify) and §3 (State Management)

**Patch content**:

```markdown
### 2.5 Pipeline Execution Flow

The extended pipeline runs as two `execute_pipeline()` phases with an
interactive prompt between them, consistent with the existing
`_auto_invoke_validate()` pattern in `execute_roadmap()`:

```
Phase A: execute_pipeline(steps 1-9)
         ↓
         _auto_invoke_validate() ← existing
         ↓
         Parse validation report, print summary
         ↓
         User prompt: [1] / [2] / [3] / [n]
         ↓ (if user selects 1/2/3)
Phase B: remediate_executor.execute() ← internal dispatch, not execute_pipeline
         ↓
         certify step via execute_pipeline([certify_step])
```

The user prompt is handled in `execute_roadmap()`, NOT inside
`execute_pipeline()`. This preserves `execute_pipeline()`'s non-interactive
contract. The remediate step uses internal dispatch (§2.3.7) rather than
`execute_pipeline()`. The certify step can run as a single Step via
`execute_pipeline()` since it's a standard single-agent step.
```

**Acceptance**: Section explicitly documents the two-phase execution model
and where the user prompt lives.

---

### P-09: Add Timeout and Retry to §2.3.4 [M-06]

**Location**: Append to the Constraints block in §2.3.4

**Patch content** — add after "Do not reorder sections unless fix guidance
explicitly requires it":

```markdown
## Execution Parameters
- Timeout: 300 seconds per agent (scoped edits are faster than generation)
- Retry: 1 retry on failure (consistent with other pipeline steps)
- Model: inherits from parent pipeline config (same as validation agents)
```

**Acceptance**: Timeout and retry values are specified with rationale.

---

### P-10: Add source_report_hash to §2.3.6 and §3.2 [M-07]

**Location**: Two edits — §2.3.6 (remediation-tasklist.md frontmatter) and
§3.2 (Resume Behavior)

**Patch 10a** — Add to the remediation-tasklist.md frontmatter example:

```yaml
---
type: remediation-tasklist
source_report: validate/reflect-merged.md
source_report_hash: "a1b2c3d4e5f6..."
generated: 2026-03-09T14:30:00Z
total_findings: 14
actionable: 10
skipped: 4
---
```

**Patch 10b** — Amend §3.2 (Resume Behavior), replace the remediate bullet:

```markdown
- If `remediate` output exists and `remediation-tasklist.md` shows all FIXED →
  verify `source_report_hash` matches the current validation report's SHA-256.
  If hash matches, skip to `certify`. If hash differs (stale tasklist from a
  prior run), re-run remediate from scratch.
```

**Acceptance**: Stale-detection hash is present in frontmatter and verified
during resume.

---

## Execution Order

```
P-01 (§2.3.7 arch model)     ← foundation for P-02, P-08
P-02 (§2.3.8 partial failure) ← depends on P-01 (snapshots referenced)
P-03 (zero-findings guard)    ← independent
P-04 (SC-002 measurement)     ← independent
P-05 (SC-006 baseline)        ← independent
P-06 (cross-file example)     ← independent
P-07 (dedup rule)             ← independent
P-08 (execution flow)         ← depends on P-01 (references §2.3.7)
P-09 (timeout/retry)          ← independent
P-10 (stale hash)             ← independent
```

**Parallelizable groups**:
- Wave 1: P-01
- Wave 2: P-02, P-03, P-04, P-05, P-06, P-07, P-09, P-10 (all independent
  after P-01)
- Wave 3: P-08 (references P-01)

**Estimated effort**: All 10 patches are text amendments to a single markdown
file. Total: ~45 minutes of focused editing.
