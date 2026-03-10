# v2.02 QA Remediation — Fix Tasklist

**Sprint**: v2.02-Roadmap-v3 (Adversarial Pipeline Remediation)
**QA Score**: 21/28 (75%) — needs 22/28 (79%)
**Date**: 2026-03-03
**Status**: EXECUTED — ALL 12 TASKS COMPLETE

---

## Origin

Derived from:
1. **Spec Panel Review** — 4-expert critique (Wiegers/Nygard/Fowler/Crispin)
2. **Adversarial Debate: Fix 1** — 3-round debate, Advocate vs Challenger on observability
3. **Adversarial Debate: Fix 2** — 3-round debate, Advocate vs Challenger on failure injection

## Expected Score Impact

| Criterion | Current | After Fix 1 | After Fix 2 | Net |
|-----------|---------|-------------|-------------|-----|
| 4 (Return contract validation evidence) | 1/2 | **2/2** | — | +1 |
| 5 (Consumer defaults evidence) | 1/2 | **2/2** | — | +1 |
| 7 (Tier 1 gate evidence) | 1/2 | **2/2** | — | +1 |
| 8 (Missing-file guard evidence) | 1/2 | **2/2** | — | +1 |
| 9 (Fallback protocol tested) | 1/2 | — | **2/2** | +1 |
| 10 (fallback_mode warning tested) | 1/2 | — | **2/2** | +1 |
| 11 (YAML parse error tested) | 1/2 | — | **2/2** | +1 |
| **Total** | **21/28** | **25/28** | **28/28** | **+7** |

Note: Fix 2 criteria 9 covers DC-1/DC-2/DC-3 (6/9 error paths automated). 3 Fallback Protocol cascade paths (F1/F2-F3/F4-F5) documented as manual-only.

---

## Fix 1: Observability Gaps

### T-FIX1.1 — Add `pipeline_diagnostics` schema to refs/templates.md

**File**: `src/superclaude/skills/sc-roadmap-protocol/refs/templates.md`
**Section**: `### extraction.md Frontmatter` (after `extraction_mode` field)
**Action**: Add YAML block:

```yaml
pipeline_diagnostics:
  prereq_checks:
    spec_validated: true                     # Wave 0: spec file(s) exist and readable
    output_collision_resolved: false          # Wave 0: collision suffix applied
    adversarial_skill_present: true|na        # Wave 0: sc:adversarial SKILL.md exists (na if not needed)
    tier1_templates_found: 0                  # Wave 2: count of Tier 1 template matches
  contract_validation:                        # Present only if adversarial mode used; omit if not
    fields_received: 9                        # Count of non-null fields in return contract
    fields_defaulted: []                      # List of field names where consumer defaults applied
    convergence_score: 0.72                   # Raw score from return contract
    routing_decision: pass|partial|fail       # Threshold decision applied
    file_guard_passed: true                   # merged_output_path verified on disk
  fallback_activated: false                   # Any fallback protocol (F1-F5) triggered
```

**Scope**: ~15 lines added
**Risk**: LOW — additive schema change, no existing fields modified

---

### T-FIX1.2 — Add logging directive to SKILL.md Wave 1B exit criteria

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
**Section**: Wave 1B exit criteria (after "extraction.md body written")
**Action**: Append instruction:

> Include `pipeline_diagnostics` block in extraction.md frontmatter per the schema in `refs/templates.md` "extraction.md Frontmatter" section. Populate `prereq_checks` from Wave 0 results carried in pipeline state. If adversarial mode is not active, omit the `contract_validation` sub-block entirely.

**Scope**: ~3 sentences added
**Risk**: LOW — additive instruction, no behavioral change

---

### T-FIX1.3 — Add logging directive to SKILL.md Wave 3 Step 3

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
**Section**: Wave 3 Step 3 (extraction.md frontmatter update)
**Action**: Append instruction:

> If adversarial mode was used in Wave 1A or Wave 2: populate the `contract_validation` sub-block of `pipeline_diagnostics` in extraction.md frontmatter using the return contract values consumed in Wave 1A Step 2e or Wave 2 Step 3e. Set `fallback_activated: true` if any fallback protocol (F1-F5) was triggered during this pipeline run.

**Scope**: ~3 sentences added
**Risk**: LOW — additive instruction, no behavioral change

---

### T-FIX1.4 — Run make sync-dev

**Action**: `make sync-dev && make verify-sync`
**Scope**: Copies src/ changes to .claude/
**Risk**: NEGLIGIBLE

---

## Fix 2: Failure-Injection Testing

### T-FIX2.1 — Add `--resume-from` flag to SKILL.md Section 3

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
**Section**: Section 3 (Flags & Options table)
**Action**: Add row:

| `--resume-from` | | No | - | Path to pre-existing adversarial output directory. Skips sc:adversarial Skill invocation; consumes return contract from specified directory. Requires `--specs` or `--multi-roadmap`. Incompatible with `--dry-run`. |

**Scope**: +3 lines
**Risk**: LOW — flag table addition only

---

### T-FIX2.2 — Add `--resume-from` validation to Wave 0

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
**Section**: Wave 0 (Prerequisites), after existing validation steps
**Action**: Add validation step:

> If `--resume-from` present:
> 1. Verify `--specs` or `--multi-roadmap` is also present. If neither: abort with `"--resume-from requires --specs or --multi-roadmap."`
> 2. Verify `--dry-run` is NOT present. If present: abort with `"--resume-from is incompatible with --dry-run."`
> 3. Verify the specified directory exists. If not: abort with `"--resume-from directory not found: <path>"`
> 4. Verify `return-contract.yaml` exists in the directory. If not: abort with `"return-contract.yaml not found in --resume-from directory: <path>"`

**Scope**: ~8 lines
**Risk**: LOW — validation-only, fails fast on bad input

---

### T-FIX2.3 — Add `--resume-from` skip conditions to Wave 1A and Wave 2

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
**Section**: Wave 1A step 2 and Wave 2 step 3
**Action**:

**Wave 1A step 2** — Add before step 2a:
> If `--resume-from` present: skip Skill invocation (steps 2a-2d). Read return contract from `<resume-from-dir>/return-contract.yaml` via Read tool. Proceed to step 2e with file-based contract.

**Wave 2 step 3** — Add before step 3a:
> If `--resume-from` present: skip steps 3a-3d. Read return contract from `<resume-from-dir>/return-contract.yaml` via Read tool. Proceed to step 3e with file-based contract.

**Scope**: ~10 lines total
**Risk**: MEDIUM — modifies execution flow. Mitigated by narrow scoping (only bypasses Skill invocation, consumption logic unchanged).

---

### T-FIX2.4 — Document `--resume-from` interaction in adversarial-integration.md

**File**: `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md`
**Section**: New section after "Invocation Patterns"
**Action**: Add `## --resume-from Interaction` section documenting:
- Flag validation rules (requires --specs or --multi-roadmap)
- Consumption path (same as file-fallback path, line 164)
- Session persistence behavior (skipped waves not recorded)
- Incompatibilities (--dry-run)

**Scope**: ~25 lines
**Risk**: LOW — documentation only

---

### T-FIX2.5 — Create DC fixture directories

**Location**: `.dev/releases/current/v2.02-Roadmap-v3/test-fixtures/`
**Action**: Create 5 fixture directories:

| Fixture | Contents | Tests |
|---------|----------|-------|
| `DC-1-missing-fields/` | return-contract.yaml with `status` and `convergence_score` absent; diff-analysis.md; merged-output.md | Consumer defaults (T-FIX1.1 `fields_defaulted`) |
| `DC-2-null-values/` | return-contract.yaml with all nullable fields set to `null`; diff-analysis.md; merged-output.md | Null routing semantics |
| `DC-3-missing-referenced-file/` | return-contract.yaml with `merged_output_path: "./does-not-exist.md"`; diff-analysis.md; NO merged-output.md | Missing-file guard |
| `DC-4-malformed-yaml/` | return-contract.yaml containing `{invalid: yaml: [`; diff-analysis.md; merged-output.md | YAML parse error handler |
| `DC-5-fallback-mode/` | Valid return-contract.yaml with `fallback_mode: true`; diff-analysis.md; merged-output.md | Differentiated fallback warning |

**Scope**: 5 directories, ~15 files
**Risk**: LOW — test artifacts only, no production code

---

### T-FIX2.6 — Write failure-injection test prompt

**Location**: `.dev/releases/current/v2.02-Roadmap-v3/test-prompts/fix2-failure-injection.md`
**Action**: Structured test prompt that:
1. Creates a minimal valid spec file
2. Runs `sc:roadmap --specs <spec> --multi-roadmap --agents opus,sonnet --resume-from <DC-N>` for each fixture
3. Checks extraction.md `pipeline_diagnostics` for expected values per fixture
4. Reports PASS/FAIL per fixture

**Scope**: ~80-100 lines
**Risk**: LOW — test prompt only

---

### T-FIX2.7 — Document untestable paths

**File**: `.dev/releases/current/v2.02-Roadmap-v3/test-fixtures/MANUAL-TEST-PROCEDURES.md`
**Action**: Document 3 untestable Fallback Protocol cascade paths with manual procedures:

| Path | Manual Procedure |
|------|-----------------|
| F1 (Skill tool error) | Temporarily rename sc:adversarial-protocol SKILL.md, run sc:roadmap with --multi-roadmap, observe retry behavior |
| F2/F3 (Template fallback) | Same as F1; continue observing after retry failure to verify template fallback activates |
| F4/F5 (Terminal abort) | Rename SKILL.md AND corrupt template directory; verify abort message |

**Scope**: ~40 lines
**Risk**: NEGLIGIBLE — documentation only

---

### T-FIX2.8 — Run make sync-dev

**Action**: `make sync-dev && make verify-sync`
**Scope**: Copies src/ changes to .claude/
**Risk**: NEGLIGIBLE

---

## Execution Order

```
Fix 1 (parallel-safe, no dependencies between tasks):
  T-FIX1.1 (templates.md schema)
  T-FIX1.2 (SKILL.md Wave 1B)     ← depends on T-FIX1.1 for schema reference
  T-FIX1.3 (SKILL.md Wave 3)      ← depends on T-FIX1.1 for schema reference
  T-FIX1.4 (sync)                  ← depends on T-FIX1.1 + T-FIX1.2 + T-FIX1.3

Fix 2 (sequential where noted):
  T-FIX2.1 (flag table)
  T-FIX2.2 (Wave 0 validation)    ← depends on T-FIX2.1
  T-FIX2.3 (skip conditions)      ← depends on T-FIX2.1
  T-FIX2.4 (refs documentation)   ← depends on T-FIX2.1
  T-FIX2.5 (fixtures)             ← independent
  T-FIX2.6 (test prompt)          ← depends on T-FIX2.5 + T-FIX2.3
  T-FIX2.7 (manual procedures)    ← independent
  T-FIX2.8 (sync)                 ← depends on all T-FIX2.1-2.4

Optimal execution:
  Wave A: [T-FIX1.1, T-FIX2.1, T-FIX2.5, T-FIX2.7]  ← 4 parallel
  Wave B: [T-FIX1.2, T-FIX1.3, T-FIX2.2, T-FIX2.3, T-FIX2.4]  ← 5 parallel
  Wave C: [T-FIX1.4, T-FIX2.6, T-FIX2.8]  ← 3 parallel (sync + test prompt)
```

**Total estimated scope**: ~200 lines across 5 files + 15 fixture files + 2 new files
**Files modified**: 3 (SKILL.md, refs/templates.md, refs/adversarial-integration.md)
**Files created**: ~17 (fixtures, test prompt, manual procedures)
