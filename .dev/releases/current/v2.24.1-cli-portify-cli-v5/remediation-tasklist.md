---
title: "Remediation Tasklist: Spec Panel Findings → portify-release-spec.md"
source: spec-panel-review.md
target: portify-release-spec.md
total_tasks: 14
task_type: spec-edit
compliance_tier: STANDARD
---

# Remediation Tasklist: Panel Review Findings

Addresses findings C-1, M-1 through M-7 from `spec-panel-review.md` by editing `portify-release-spec.md`. All tasks are spec-text edits — no code changes.

## Dependency Graph

```
Phase 1 (C-1):  R-01 ──────────────────────────────────> done
Phase 2 (M-1..M-3): R-02, R-03, R-04 ── [parallel] ──> R-05 (update test matrix)
Phase 3 (M-4..M-7): R-06, R-07, R-08, R-09 [parallel]> R-10 (update test matrix)
Phase 4 (Cleanup):  R-11, R-12, R-13, R-14 [parallel] > done
```

---

## Phase 1: Critical Fix — R3/R4 Null Guard (C-1)

### R-01: Add skill_dir None guard to resolution algorithm steps R3-R5

**Finding**: C-1 (CRITICAL) — Steps R3 and R4 attempt to read SKILL.md and scan subdirectories but do not guard against `skill_dir = None`. Standalone commands (help.md, sc.md) would crash.

**Target section**: Section 4.5 → "Resolution Algorithm" → between Step R2 and Step R3

**Action**: Insert a guard paragraph between R2 and R3:

```markdown
**Guard: Skill-less Command Path**

If `ResolvedTarget.skill_dir` is `None` after R2 (standalone command with no paired skill):
- Skip R3 (agent extraction) — no SKILL.md to parse
- Skip R4 (Tier 2 inventory) — no subdirectories to scan
- Proceed directly to R5 with `agents = []`, `refs = []`, `rules = []`, `templates = []`, `scripts = []`
- Record in `resolution_log`: "Standalone command — no skill directory, skipping component discovery"
```

**Also update**: FR-PORTIFY-WORKFLOW.2 acceptance criteria — add:
```markdown
- [ ] Standalone command (no skill) produces ComponentTree with skill=None, agents=[], refs/rules/templates/scripts=[]
```

**Verification**: Search spec for "Step R3" and confirm the guard appears before it. Search for "FR-PORTIFY-WORKFLOW.2" and confirm the new criterion exists.

**Compliance**: STRICT — correctness-critical invariant fix

---

## Phase 2: Input Validation Gaps (M-1, M-2, M-3)

### R-02: Define empty/whitespace TARGET behavior (M-1)

**Finding**: M-1 (MAJOR) — Empty string `""` or whitespace-only TARGET input has undefined behavior.

**Target section**: Section 4.5 → "Resolution Algorithm" → before Step R1

**Action**: Insert a pre-classification validation step:

```markdown
**Step R0: Input Validation**

Before classifying `input_type`, validate the raw `target` string:
- If `target` is empty, whitespace-only, or `None`: return `ERR_TARGET_NOT_FOUND` with message "No target specified. Provide a command name, path, or skill directory."
- Strip leading/trailing whitespace from `target` before proceeding to classification.
```

**Also update**: Section 5.1 CLI Surface table — change TARGET description from "required" to:
```
Command name, path, skill directory, or skill name to portify. Must be non-empty.
```

**Also update**: Error codes list in Section 4.5 validate_config — confirm `ERR_TARGET_NOT_FOUND` covers this case (it does, no change needed — just verify).

**Verification**: Search for "Step R0" or "Input Validation" in spec. Confirm it appears before R1.

**Compliance**: STANDARD — input boundary definition

---

### R-03: Define sc: prefix strip edge case (M-2)

**Finding**: M-2 (MAJOR) — `"sc:"` prefix stripping yields empty string, which then falls through with undefined behavior.

**Target section**: Section 4.5 → "Resolution Algorithm" → Step R1 (within the command name handling)

**Action**: Add post-strip validation to the input normalization description. After the sentence about stripping `sc:` prefix, add:

```markdown
After prefix stripping, if the resulting name is empty (i.e., input was exactly `"sc:"`), return `ERR_TARGET_NOT_FOUND` with message "Empty command name after prefix stripping. Provide a valid command name after 'sc:'."
```

**Verification**: Search for "Strip `sc:`" or "sc:" prefix in spec. Confirm the empty-after-strip guard is present.

**Compliance**: STANDARD — sentinel collision fix

---

### R-04: Define --include-agent deduplication semantics (M-3)

**Finding**: M-3 (MAJOR) — Spec doesn't clarify whether `--include-agent` entries are deduplicated against auto-discovered agents.

**Target section**: Section 4.5 → "Resolution Algorithm" → Step R3, after the `--include-agent` injection paragraph

**Action**: Replace the sentence "Additionally, inject any agents specified via `--include-agent` CLI option..." with:

```markdown
Additionally, inject any agents specified via `--include-agent` CLI option. These are resolved the same way: if a bare name, look up in `agents_dir`; if a path, use directly.

**Deduplication rule**: All agents — both auto-discovered and manually injected — are deduplicated by name. If `--include-agent` specifies an agent already discovered from SKILL.md:
- The manually specified entry takes precedence (overwrites auto-discovered)
- `referenced_in` is set to `"cli-override"` for the merged entry
- No duplicate `AgentEntry` objects exist in the final `ComponentTree.agents` list

If `--include-agent` receives an empty string `""`, it is silently ignored (no agent lookup attempted).
```

**Verification**: Search for "Deduplication rule" in spec. Confirm it appears in R3. Search for `--include-agent` and confirm empty-string handling is stated.

**Compliance**: STANDARD — behavioral specification

---

### R-05: Add 5 missing test cases to Section 8.1 (Crispin findings)

**Finding**: Crispin identified 5 missing boundary test cases.

**Target section**: Section 8.1 Unit Tests table

**Action**: Append 5 rows to the Unit Tests table, after the existing "Directory cap (>10 dirs)" row:

```markdown
| `resolve_target()`: empty/whitespace input | `test_resolution.py` | Returns ERR_TARGET_NOT_FOUND for `""`, `" "` |
| `resolve_target()`: `"sc:"` prefix with empty name | `test_resolution.py` | Returns ERR_TARGET_NOT_FOUND after stripping |
| `resolve_target()`: standalone command (no skill) | `test_resolution.py` | R3/R4 skipped, agents=[], skill=None |
| `--include-agent` dedup against auto-discovered | `test_resolution.py` | Manual agent replaces auto-discovered, no duplicates |
| `ValidateConfigResult.to_dict()` new fields | `test_validate_config.py` | New fields and `warnings` present in dict output |
```

**Also update**: Total estimated test count from "~32" to "~37".

**Dependencies**: R-01, R-02, R-03, R-04 (test cases reference the behaviors defined in those tasks)

**Verification**: Count rows in Section 8.1 table. Confirm >=25 rows. Search for "~37" estimated tests.

**Compliance**: STANDARD — test coverage gap

---

## Phase 3: Specification Clarifications (M-4, M-5, M-6, M-7)

### R-06: Define directory consolidation algorithm (M-4)

**Finding**: M-4 (MAJOR) — ">10 directories triggers consolidation" but no algorithm defined.

**Target section**: Section 4.5 → Subprocess Scoping Extensions → after the "Directory Cap" paragraph

**Action**: Replace the paragraph "If `all_source_dirs` returns more than 10 directories, emit a warning and consolidate to common parent directories. This prevents `--add-dir` argument explosion." with:

```markdown
**Directory Cap and Consolidation**

If `all_source_dirs` returns more than 10 directories:

1. Emit a warning: "Component tree spans {N} directories (cap: 10). Consolidating to parent directories."
2. Group directories by their nearest common parent using `os.path.commonpath()` for each pair within 2 levels of depth.
3. Replace groups sharing a common parent with the common parent directory, provided the parent directory contains no more than 3x the total file count of its constituent directories.
4. If consolidation still exceeds 10 directories, use only the top 10 by component count (most components first).
5. Record all consolidation decisions in `resolution_log`.

This prevents `--add-dir` argument explosion while limiting over-scoping of Claude subprocess access.
```

**Verification**: Search for "Directory Cap and Consolidation" in spec. Confirm the 5-step algorithm is present.

**Compliance**: STANDARD — algorithm specification

---

### R-07: Clarify ambiguity detection rules (M-5)

**Finding**: M-5 (MAJOR) — Command-name vs skill-name collision semantics undefined.

**Target section**: Section 4.5 → Resolution Algorithm → Step R1 (command resolution)

**Action**: Add after the Step R1 description, before Step R2:

```markdown
**Ambiguity Resolution Policy**

`ERR_AMBIGUOUS_TARGET` is raised only when multiple matches exist **within the same input type class**:
- Bare name `"roadmap"` matching two files in `commands/` (e.g., `roadmap.md` and `roadmap-v2.md`) → ERR_AMBIGUOUS_TARGET
- Bare name `"roadmap"` matching both `commands/roadmap.md` AND `skills/roadmap/` → **NOT ambiguous** — command wins per command-first policy

A bare name that matches a command always resolves as COMMAND_NAME. The skill is discovered from the command's `## Activation` directive, not from name matching. Only if no command matches does the resolver attempt SKILL_NAME matching.
```

**Verification**: Search for "Ambiguity Resolution Policy" in spec. Confirm it appears between R1 and R2.

**Compliance**: STANDARD — behavioral specification

---

### R-08: Document ComponentEntry path type convention (M-6)

**Finding**: M-6 (MAJOR) — Existing `ComponentEntry.path` uses `str`, new models use `Path`. Undocumented inconsistency.

**Target section**: Section 4.5 → Data Models → before the Component Tree Model heading

**Action**: Add a note after the `ComponentEntry` is first referenced (within the `to_flat_inventory()` code comments or as a standalone note):

```markdown
**Type Convention Note**: The existing `ComponentEntry` dataclass (v2.24) uses `path: str` for backward compatibility with serialization and artifact generation. All new dataclasses introduced in this spec (`ResolvedTarget`, `CommandEntry`, `SkillEntry`, `AgentEntry`, `ComponentTree`) use `Path` objects for type safety. The `to_flat_inventory()` method converts `Path` → `str` via `str()` at the boundary. This convention is intentional and should be preserved — do not change `ComponentEntry.path` to `Path`.
```

**Verification**: Search for "Type Convention Note" in spec. Confirm it exists.

**Compliance**: LIGHT — documentation clarification

---

### R-09: Specify ValidateConfigResult.to_dict() serialization (M-7)

**Finding**: M-7 (MAJOR) — New fields (`command_path`, `skill_dir`, `target_type`, `agent_count`, `warnings`) not specified for `to_dict()` serialization.

**Target section**: Section 4.5 → ValidateConfigResult Extensions

**Action**: After the `ValidateConfigResult` dataclass definition, add:

```markdown
The `to_dict()` method MUST be updated to include all new fields:

```python
def to_dict(self) -> dict[str, Any]:
    return {
        "step": "validate-config",
        "valid": self.valid,
        "cli_name_kebab": self.cli_name_kebab,
        "cli_name_snake": self.cli_name_snake,
        "workflow_path_resolved": self.workflow_path_resolved,
        "output_dir": self.output_dir,
        "errors": self.errors,
        "warnings": self.warnings,          # NEW
        "duration_seconds": self.duration_seconds,
        "command_path": self.command_path,   # NEW
        "skill_dir": self.skill_dir,         # NEW
        "target_type": self.target_type,     # NEW
        "agent_count": self.agent_count,     # NEW
    }
```

These fields are consumed by downstream contract emission (`contract.py`) and resume context (`resume.py`). Omitting them would cause silent data loss in pipeline telemetry.
```

**Verification**: Search for "to_dict()" in spec. Confirm the updated method with all NEW fields is present.

**Compliance**: STANDARD — interface contract specification

---

### R-10: Update test matrix for Phase 3 additions

**Target section**: Section 8.1 Unit Tests table (already extended by R-05)

**Action**: Verify that R-05's additions already cover:
- `ValidateConfigResult.to_dict()` serialization (yes — added in R-05)
- No additional test cases needed for M-4 through M-7 (consolidation algorithm is internal, ambiguity rules are tested via existing resolution tests, type convention is documentation-only)

**Dependencies**: R-05, R-06, R-07, R-08, R-09

**Verification**: Re-read Section 8.1 and confirm no further gaps.

**Compliance**: LIGHT — verification pass

---

## Phase 4: Cleanup and Score Update

### R-11: Update quality_scores after remediation

**Target section**: YAML frontmatter

**Action**: After all edits are complete, reassess quality scores:
- `completeness`: 7.5 → 8.5 (8 boundary GAPs closed, C-1 resolved)
- `consistency`: 8.0 → 8.5 (type convention documented, to_dict() specified)
- `overall`: 8.0 → 8.5 (recalculated from updated dimensions)
- `clarity` and `testability` unchanged (8.5 and 8.0)

**Dependencies**: R-01 through R-10

**Compliance**: LIGHT — metadata update

---

### R-12: Update Open Items table

**Target section**: Section 11 Open Items

**Action**: Mark OI-4 as resolved:

Change:
```
| OI-4 | Quality scores for this spec | Required for release readiness | Run `/sc:spec-panel` after template alignment |
```
To:
```
| OI-4 | Quality scores for this spec | Required for release readiness | **RESOLVED** — panel review completed 2026-03-13, scores populated |
```

**Dependencies**: R-11

**Compliance**: LIGHT — metadata update

---

### R-13: Add remediation provenance to Appendix B

**Target section**: Appendix B: Reference Documents

**Action**: Add row:

```markdown
| `spec-panel-review.md` | Panel review findings (C-1, M-1..M-7, m-1..m-3) driving this remediation |
```

**Compliance**: LIGHT — traceability

---

### R-14: Run sentinel verification

**Action**: After all edits, run:
```bash
grep -c '{{SC_PLACEHOLDER:' portify-release-spec.md
```

Expected result: `0`

Also verify no broken markdown tables by checking pipe alignment on modified sections.

**Dependencies**: R-01 through R-13

**Compliance**: LIGHT — final verification

---

## Execution Summary

| Phase | Tasks | Compliance | Parallelizable | Estimated Edits |
|-------|-------|-----------|---------------|----------------|
| 1: Critical Fix | R-01 | STRICT | No (blocking) | 2 sections |
| 2: Input Validation | R-02, R-03, R-04, R-05 | STANDARD | R-02/R-03/R-04 parallel, then R-05 | 4 sections + test table |
| 3: Clarifications | R-06, R-07, R-08, R-09, R-10 | STANDARD/LIGHT | R-06/R-07/R-08/R-09 parallel, then R-10 | 4 sections + verification |
| 4: Cleanup | R-11, R-12, R-13, R-14 | LIGHT | All parallel except R-14 last | Frontmatter + 2 tables + grep |

**Total tasks**: 14
**Blocking dependency**: R-01 must complete first (CRITICAL fix)
**Estimated effort**: 20-30 minutes of spec editing
