# Dev Planning Synthesis: v2.01-Roadmap-V3 Rollback-Recreation Analysis

**Analysis Date:** 2026-02-24
**Branch:** `feature/v2.01-Roadmap-V3`
**Base Commit:** `9060a65`
**Source Batches:** batch1-tasklists, batch2-architecture-docs, batch3-checkpoints

---

## 1. Executive Summary

The v2.01-Roadmap-V3 branch introduces a comprehensive restructuring of SuperClaude's command-skill architecture, driven by a new policy document (`command-skill-policy.md`) authored on 2026-02-23. This policy establishes a three-tier loading model -- Commands (Tier 0, slim entry points), Protocol Skills (Tier 1, full behavioral specs), and Ref Files (Tier 2, on-demand detail) -- and mandates the renaming of all five paired skill directories to carry a `-protocol` suffix. The branch also reorganizes the sprint's dev-planning tasklist from a single monolithic file with a problematic macOS-duplicate filename into a properly-named canonical copy (`tasklist-P6.md`) and a focused Phase-5-only extract (`tasklist-P5.md`).

Two phase checkpoint reports (CP-P01-END, CP-P02-END) record the sprint's execution history through Phases 1 and 2. Phase 1 established that the `Skill` tool is unavailable at runtime (`TOOL_NOT_AVAILABLE`), selecting the fallback-only sprint variant; confirmed all 6 prerequisites; and set the tier classification policy that executable `.md` files are not compliance-exempt. Phase 2 consumed that variant decision to wire the fallback invocation protocol into Wave 2 Step 3 of the roadmap skill, confirming `Skill` presence in allowed-tools lists and implementing the F1/F2-3/F4-5 fallback as the sole invocation path.

Together, these dev-planning artifacts form a coherent decision chain: the architecture policy defines what must change, the tasklist decomposes the work into 18 tasks across 6 phases with full traceability, and the checkpoint reports provide evidence that Phases 1-2 were executed to completion with all gates passing. The net code impact of these planning files is zero -- they are purely organizational and documentary -- but they drive all the actual source changes (skill renames, command trims, SKILL.md frontmatter updates) visible elsewhere on the branch.

---

## 2. File Inventory

| # | Path | Status | Lines | Purpose |
|---|------|--------|-------|---------|
| 1 | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P5.md` | MODIFIED | -841 lines | Gutted to Phase-5-only execution view; retains all registries and templates |
| 2 | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P copy 2.md` | DELETED | -503 lines | Removed monolithic predecessor with bad macOS filename |
| 3 | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P6.md` | NEW | +503 lines | Canonical complete tasklist (all 6 phases, 18 tasks, 22 deliverables) |
| 4 | `docs/architecture/command-skill-policy.md` | NEW | 337 lines | Architecture policy document defining the 3-tier loading model |
| 5 | `src/superclaude/ARCHITECTURE.md` | NEW | 337 lines | Byte-identical copy of #4, placed alongside source code |
| 6 | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/CP-P01-END.md` | NEW | ~80 lines | Phase 1 checkpoint: probe result, prerequisites, tier policy |
| 7 | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/CP-P02-END.md` | NEW | ~80 lines | Phase 2 checkpoint: allowed-tools verification, fallback wiring |

**Totals:** 3 new files, 1 modified file, 1 deleted file. Net line delta: approximately +400 (503 new tasklist + 337+337 architecture + ~160 checkpoints - 503 deleted - 841 removed from P5).

---

## 3. Decision Chain

The sprint follows a strict chronological decision chain where each phase's output feeds the next:

```
2026-02-23: Architecture Policy Authored
    |
    v
Phase 1 (Foundation)
    |
    +-- T01.01: Skill Tool Probe
    |       Result: TOOL_NOT_AVAILABLE
    |       Decision: Fallback-only sprint variant
    |       Artifacts: D-0001 (evidence), D-0002 (variant decision)
    |
    +-- T01.02: Prerequisite Validation
    |       Result: 6/6 checks pass
    |       Verified: 3 skill files readable, 2 make targets available
    |       Artifact: D-0003 (evidence)
    |
    +-- T01.03: Tier Classification Policy
    |       Result: Executable .md files NOT exempt from compliance
    |       Impact: 9 downstream tasks affected
    |       Artifact: T01.03/notes.md
    |
    v
Phase 2 (Invocation Wiring)
    |
    +-- T02.01: Skill in roadmap.md allowed-tools
    |       Result: PASS (grep-verified)
    |       Artifact: D-0004
    |
    +-- T02.02: Skill in SKILL.md allowed-tools
    |       Result: PASS (grep-verified)
    |       Artifact: D-0005
    |
    +-- T02.03: Wave 2 Step 3 Rewrite (STRICT, XL effort)
    |       Applied: Fallback-only variant from T01.01
    |       Wired: F1/F2-3/F4-5 fallback protocol
    |       Inlined: Return contract routing in step 3e
    |       8-point structural audit: all pass
    |       Artifacts: D-0006, D-0007, D-0008
    |
    v
Phase 3+ (Not yet checkpointed)
```

**Critical pivot point:** T01.01's `TOOL_NOT_AVAILABLE` result is the single most consequential decision. It determined that every downstream task involving skill invocation uses the fallback protocol exclusively, and deferred G2 validation per T04 Opt 4.

---

## 4. Architecture Policy Summary

The `command-skill-policy.md` (v1.0.0) establishes the foundational architecture for SuperClaude's command-skill relationship:

### Three-Tier Model

| Tier | Component | Loading | Size Constraint | Example |
|------|-----------|---------|-----------------|---------|
| 0 | Command | Auto-loaded on `/sc:<name>` | Hard cap: 150 lines (WARN at 200, ERROR at 500) | `adversarial.md` |
| 1 | Protocol Skill | Loaded via `Skill` tool invocation | No limit | `sc-adversarial-protocol/SKILL.md` |
| 2 | Ref File | On-demand via `claude -p` | Self-contained, one concern per file | `scoring-protocol.md` |

**Core metaphor:** "Commands are doors. Skills are rooms. Refs are drawers."

### Naming Convention

Commands use bare names (`adversarial`). Protocol skills use `sc:<name>-protocol` with directory names `sc-<name>-protocol/`. This naming split is architecturally critical -- it avoids the "skill already running" re-entry block in Claude Code's Skill tool.

### CI Enforcement

10 automated checks are defined under a `make lint-architecture` target (not yet implemented in the Makefile). Checks enforce bidirectional links between commands and skills, line count limits, frontmatter completeness, and sync integrity.

### Migration Status

- **Phase 1 (Rename directories):** EXECUTED -- all 5 renames visible in git status as `RM` operations
- **Phase 2 (Refactor commands):** IN PROGRESS -- all 5 command files show as `M` (modified)
- **Phase 3 (Build system):** NOT STARTED -- `lint-architecture` target does not exist yet
- **Phase 4 (Validate):** BLOCKED on Phase 3

### Duplication Issue

The policy document exists in two identical locations: `docs/architecture/command-skill-policy.md` and `src/superclaude/ARCHITECTURE.md`. Recreation should resolve this by designating one as canonical (likely `docs/architecture/`) and making the other a reference or symlink.

### Unresolved Backlog

Two high-priority items remain: (1) designing the `claude -p` Tier 2 ref loader script, and (2) defining cross-skill invocation patterns. Six medium/low-priority command splits are queued.

---

## 5. Tasklist Evolution

### Before (Problematic State)

A single file `tasklist-P copy 2.md` contained all 6 phases, 18 tasks, and all infrastructure (registries, templates, glossary). The filename with spaces and "copy 2" suffix indicated it was a macOS Finder duplicate -- unsuitable for reliable referencing.

### After (Clean State)

| File | Content | Role |
|------|---------|------|
| `tasklist-P6.md` | All 6 phases, 18 tasks, all infrastructure (503 lines) | Canonical complete tasklist; single source of truth |
| `tasklist-P5.md` | Phase 5 only + all infrastructure (registries, templates) | Focused execution document for Phase 5 work |
| `tasklist-P copy 2.md` | DELETED | Removed problematic predecessor |

### What Changed and What Didn't

- **Changed:** File organization and naming; `Tasklist Path` metadata self-reference updated
- **Unchanged:** Every task definition, acceptance criterion, deliverable, compliance tier, effort estimate, and risk rating. Content is byte-for-byte identical between the deleted file and the new `tasklist-P6.md`.

### Path Inconsistency Warning

The tasklist files reference skill paths using the OLD directory names (`sc-adversarial/`, `sc-roadmap/`) but the git status shows these directories are being renamed to `sc-adversarial-protocol/`, `sc-roadmap-protocol/`, etc. If the renames proceed, the tasklist paths will be stale and need updating.

---

## 6. Key Dependencies

### What These Planning Docs Drive (Downstream)

| Planning Document | Drives These Changes |
|-------------------|---------------------|
| `command-skill-policy.md` | All 5 skill directory renames (`sc-*` to `sc-*-protocol`), all 5 command file trims to 150 lines, SKILL.md frontmatter updates, planned `make lint-architecture` target |
| `tasklist-P6.md` | Execution order and acceptance criteria for all 18 tasks; artifact paths for evidence collection |
| `CP-P01-END.md` | Fallback-only variant decision consumed by Phase 2+; tier classification policy affecting 9 tasks |
| `CP-P02-END.md` | Confirmation that invocation wiring is complete; unblocks Phase 3 |

### What These Planning Docs Depend On (Upstream)

| Dependency | Required By |
|------------|-------------|
| `src/superclaude/commands/roadmap.md` | T02.01 (verifies allowed-tools) |
| `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | T02.02 (verifies allowed-tools), T02.03 (Wave 2 Step 3 target) |
| `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | T04.01 (return contract write instruction) |
| `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md` | T04.02, T04.03, T05.03 (return contract and artifact gates) |
| `Makefile` (`sync-dev`, `verify-sync` targets) | T01.02 prerequisite check, Phase 3 build system updates |
| Claude Code runtime (Skill tool availability) | T01.01 probe result determines entire sprint variant |

### Cross-File Dependency Graph

```
command-skill-policy.md (POLICY)
    |
    +-- Drives --> 5 skill directory renames (Phase 1, EXECUTED)
    +-- Drives --> 5 command file refactors (Phase 2, IN PROGRESS)
    +-- Drives --> Makefile updates (Phase 3, NOT STARTED)
    +-- Drives --> CI validation (Phase 4, BLOCKED)
    |
tasklist-P6.md (EXECUTION PLAN)
    |
    +-- Phase 1 --> CP-P01-END.md (COMPLETE)
    +-- Phase 2 --> CP-P02-END.md (COMPLETE)
    +-- Phase 3 --> (NOT STARTED)
    +-- Phase 4 --> (NOT STARTED)
    +-- Phase 5 --> tasklist-P5.md (focused view)
    +-- Phase 6 --> (NOT STARTED)
    |
Evidence artifacts (D-0001 through D-0008)
    |
    +-- Stored in --> .dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/
    +-- Stored in --> .dev/releases/current/v2.01-Roadmap-v3/tasklist/evidence/
```

---

## 7. Rollback Impact

### If These Files Are Lost

| File | Recreation Difficulty | Impact of Loss |
|------|----------------------|----------------|
| `tasklist-P6.md` | LOW -- Content is mechanical (registries, task templates). Can be regenerated from the roadmap source and the deterministic rules. | Loss of the canonical task execution plan. All 18 task definitions, acceptance criteria, and deliverable mappings would need reconstruction. |
| `tasklist-P5.md` | TRIVIAL -- It is a subset of P6. | Loss of the Phase-5-focused working view. Easily re-derived from P6. |
| `command-skill-policy.md` | MEDIUM -- Contains original architectural decisions, rationale, and the specific naming conventions. The decision *reasoning* is harder to reconstruct than the decisions themselves. | Loss of the authoritative architecture policy. The skill renames and command trims would lose their documented justification. The CI enforcement spec (10 checks) would need to be re-designed. |
| `ARCHITECTURE.md` (src copy) | TRIVIAL -- Identical to the docs/ copy. | No unique content lost. |
| `CP-P01-END.md` | LOW -- Can be reconstructed from the evidence artifacts (D-0001 through D-0003). | Loss of the formal Phase 1 completion record. The critical `TOOL_NOT_AVAILABLE` decision and tier classification policy would need to be re-verified. |
| `CP-P02-END.md` | LOW -- Can be reconstructed from evidence artifacts (D-0004 through D-0008). | Loss of the formal Phase 2 completion record. The fallback wiring verification would need re-execution. |

### Rollback Procedure

To fully rollback the dev-planning changes:

1. **Restore** `tasklist-P copy 2.md` from the base commit
2. **Restore** full content of `tasklist-P5.md` (un-gut it by adding back Phases 1-4, 6)
3. **Delete** `tasklist-P6.md`
4. **Delete** `docs/architecture/command-skill-policy.md`
5. **Delete** `src/superclaude/ARCHITECTURE.md`
6. **Delete** `checkpoints/CP-P01-END.md` and `CP-P02-END.md`
7. **Revert** skill directory renames (restore `sc-adversarial/` etc. from `sc-adversarial-protocol/`)

**Risk:** LOW. All files are dev-planning documents with zero runtime impact. No production code depends on these files existing.

### Recreation Priority

If recreating from scratch rather than rolling back:

1. **First:** Recreate `command-skill-policy.md` -- it is the foundational policy that all other changes derive from
2. **Second:** Recreate `tasklist-P6.md` -- it is the execution plan that drives task ordering and acceptance criteria
3. **Third:** Recreate checkpoint reports -- they are formal records but can be re-derived from evidence artifacts
4. **Last:** `tasklist-P5.md` and the `src/` ARCHITECTURE copy -- both are derived views of other files

---

## 8. Technical Breakdown

### File-by-File Detail

#### 8.1 `tasklist-P5.md` (MODIFIED: -841 lines)

**What was removed:** Complete task bodies for Phases 1-4 and Phase 6, totaling 841 lines across 15 tasks. The removed content includes all acceptance criteria, compliance tiers, effort estimates, deliverable mappings, and checkpoint definitions for those phases.

**What survives:** Metadata header, Source Snapshot, 12 Deterministic Rules, Roadmap Item Registry (R-001 to R-022), Deliverable Registry (D-0001 to D-0022), Tasklist Index (all 6 phases listed), Phase 5 task bodies (T05.01, T05.02, T05.03 + checkpoint), Traceability Matrix, and all templates (Execution Log, Checkpoint Report, Feedback Collection, Glossary).

**Key structural detail:** The registries and index still reference all 6 phases even though only Phase 5 bodies remain. This is intentional -- it allows cross-phase reference resolution from the focused view.

**Phase 5 tasks retained:**
- T05.01: Execution Vocabulary Glossary (STANDARD, S effort)
- T05.02: Wave 1A Step 2 Fix (STANDARD, S effort)
- T05.03: Pseudo-CLI Conversion (STANDARD, S effort)

#### 8.2 `tasklist-P copy 2.md` (DELETED: -503 lines)

**Sole differentiator from P6:** Line 6 metadata reads `TASKLIST_ROOT/tasklist/tasklist.md` instead of `TASKLIST_ROOT/tasklist/tasklist-P6.md`. All 503 lines of task definitions, registries, and templates are otherwise byte-for-byte identical to `tasklist-P6.md`.

**Deletion rationale:** macOS Finder duplicate with space-containing filename. Unsuitable for reliable path referencing in scripts or documentation.

#### 8.3 `tasklist-P6.md` (NEW: +503 lines)

**Sprint scope (from Source Snapshot):** "sc:roadmap Adversarial Pipeline Remediation Sprint" -- a sprint to fix the adversarial integration pipeline within the roadmap skill.

**Task distribution by compliance tier:**
- EXEMPT: 8 tasks (T01.01-T01.03, T03.01-T03.02, T06.01-T06.04)
- LIGHT: 2 tasks (T02.01, T02.02)
- STANDARD: 5 tasks (T04.03, T05.01-T05.03, T06.05)
- STRICT: 3 tasks (T02.03, T04.01, T04.02)

**Effort distribution:** 1 XL, 1 L, 1 M, 13 S, 2 XS

**Risk distribution:** 4 Medium risk (T02.03, T04.01, T04.02, T06.01), 14 Low risk

**Highest-risk task:** T02.03 (Wave 2 Step 3 Rewrite) -- STRICT compliance, XL effort, Medium risk. This is the largest and most consequential task in the sprint, rewriting the core invocation wiring.

#### 8.4 `command-skill-policy.md` / `ARCHITECTURE.md` (NEW: 337 lines each)

**Version:** 1.0.0, authored 2026-02-23

**Key quotes:**
- "Commands are doors. Skills are rooms. Refs are drawers."
- "The primary reason for the Command != Skill name invariant: Claude Code's Skill tool blocks re-entry if a skill with the same name is already running."
- "Hard cap at 150 lines for commands ensures auto-loaded context stays minimal."

**10 CI checks defined** (severity breakdown): 7 ERROR, 3 WARN. The checks enforce structural integrity between commands and skills.

**Migration Phase 1 progress:** All 5 directory renames are confirmed executed via git status `RM` operations:
- `sc-adversarial` -> `sc-adversarial-protocol` (content modified)
- `sc-cleanup-audit` -> `sc-cleanup-audit-protocol` (content modified)
- `sc-roadmap` -> `sc-roadmap-protocol` (content modified)
- `sc-task-unified` -> `sc-task-unified-protocol` (content modified)
- `sc-validate-tests` -> `sc-validate-tests-protocol` (content modified)

**Unresolved items:** `make lint-architecture` not yet implemented; `claude -p` ref loader not yet designed; 6 oversized command files not yet split.

#### 8.5 `CP-P01-END.md` (NEW: Phase 1 Checkpoint)

**Phase result:** PASS (all 3 tasks complete, no blockers)

**Most consequential outcome:** T01.01 probe returned `TOOL_NOT_AVAILABLE`, selecting the fallback-only sprint variant. This single result cascades through every subsequent phase.

**Tier policy established:** T01.03 confirmed that the `*.md` EXEMPT booster in the compliance system does NOT apply to executable specification files. This affects 9 tasks by preventing them from being auto-classified as EXEMPT just because they edit markdown files.

**Pre-execution confidence for T01.01:** 40% (expected for a probe with uncertain outcome). Post-execution confidence: definitive.

#### 8.6 `CP-P02-END.md` (NEW: Phase 2 Checkpoint)

**Phase result:** PASS (all 3 tasks complete, no blockers)

**T02.03 structural audit results (8 points, all pass):**
1. Sub-steps 3a through 3f present in Wave 2 Step 3
2. Fallback protocol covers 3 error types
3. F1/F2-3/F4-5 steps implemented
4. WARNING emission present for fallback activation
5. Missing-file guard in step 3e
6. YAML parse error handler in step 3e
7. Three-status routing (success/partial/failed)
8. Convergence threshold set to 0.6

**Architectural note:** Step 3e inlines return contract routing directly rather than delegating to the ref section -- a divergence from Wave 1A's pattern that may need documentation.

---

## Appendix: Artifact Cross-Reference

| Artifact | Source Task | Type | Storage Path |
|----------|------------|------|-------------|
| D-0001 | T01.01 | evidence | `artifacts/D-0001/evidence.md` |
| D-0002 | T01.01 | notes | `artifacts/D-0002/notes.md` |
| D-0003 | T01.02 | evidence | `artifacts/D-0003/evidence.md` |
| D-0004 | T02.01 | evidence | `artifacts/D-0004/evidence.md` |
| D-0005 | T02.02 | evidence | `artifacts/D-0005/evidence.md` |
| D-0006 | T02.03 | spec | `artifacts/D-0006/spec.md` |
| D-0007 | T02.03 | spec | `artifacts/D-0007/spec.md` |
| D-0008 | T02.03 | spec | `artifacts/D-0008/spec.md` |
| D-0009 to D-0022 | T03.01 to T06.05 | various | Not yet produced (Phases 3-6 pending) |

All artifact paths are relative to `.dev/releases/current/v2.01-Roadmap-v3/tasklist/`.
