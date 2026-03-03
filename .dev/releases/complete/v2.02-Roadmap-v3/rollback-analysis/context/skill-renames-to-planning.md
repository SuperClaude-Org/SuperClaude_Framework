# Context Linking: Skill Directory Renames to Planning Origins

**Date**: 2026-02-24
**Branch**: `feature/v2.01-Roadmap-V3`
**Purpose**: Map each skill directory rename to its architecture policy mandate, tasklist tasks, decision artifacts, and SKILL.md content changes.

---

## Overview

Five skill directories were renamed from `sc-{name}` to `sc-{name}-protocol` as part of the command-skill decoupling architecture. This document traces each rename back to its planning origins.

**Architecture Policy**: `docs/architecture/command-skill-policy.md` (v1.0.0, authored 2026-02-23)
**Canonical Tasklist**: `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P6.md`

---

## 1. sc-adversarial --> sc-adversarial-protocol

### 1.1 Architecture Policy Mandate

**Source**: `docs/architecture/command-skill-policy.md`

- **Naming Convention section** (lines 52-66): "Protocol skills MUST end in `-protocol`" and "Protocol skill directories MUST be prefixed with `sc-` and suffixed with `-protocol`"
- **Migration Checklist, Phase 1** (lines 279-287): Explicitly lists `src/skills/sc-adversarial/` --> `src/skills/sc-adversarial-protocol/` with target SKILL.md `name` field `sc:adversarial-protocol`
- **Why Separate Names section** (lines 46-48): Explains the naming split avoids the "skill already running" re-entry block in Claude Code's Skill tool
- **Decision Log** (line 334): "`-protocol` suffix convention -- Clear semantic signal, easy to lint, no ambiguity" (2026-02-23)

### 1.2 Tasklist Tasks

No tasklist task in `tasklist-P6.md` explicitly targets the adversarial directory rename itself. The rename is a prerequisite established by the architecture policy and executed as part of the policy's Migration Phase 1. However, the following tasks reference this skill post-rename:

- **T04.01** (R-014, R-015): "Return Contract write instruction in sc:adversarial SKILL.md" + dead code removal. This task modifies the adversarial SKILL.md content (separate from the rename).
- **T06.01** (R-018): Schema consistency test references the adversarial skill as the return contract producer.

### 1.3 Decision Artifacts

No D-series artifact directly specifies the adversarial rename. The rename is driven by the architecture policy document, not by a sprint task artifact.

The adversarial pipeline design artifacts (ADV-1 through ADV-8 in `artifacts/adversarial/`) reference the skill using pre-rename paths (`sc-adversarial/`), except `specification-draft-v2.md` which corrects to `sc-adversarial-protocol/`.

### 1.4 SKILL.md Content Changes

**Frontmatter only** (git similarity R099 for staged rename, with unstaged modification):

| Field | Before | After |
|-------|--------|-------|
| `name` | `sc:adversarial` | `sc:adversarial-protocol` |

No body content changes. All other frontmatter fields (`description`, `allowed-tools`) unchanged.

### 1.5 Companion Files (5 pure renames, R100)

| # | File | Type |
|---|------|------|
| 1 | `__init__.py` | Python package marker |
| 2 | `refs/agent-specs.md` | Ref file |
| 3 | `refs/artifact-templates.md` | Ref file |
| 4 | `refs/debate-protocol.md` | Ref file |
| 5 | `refs/scoring-protocol.md` | Ref file |

**Total files**: 6 (1 modified SKILL.md + 5 pure renames)

---

## 2. sc-cleanup-audit --> sc-cleanup-audit-protocol

### 2.1 Architecture Policy Mandate

**Source**: `docs/architecture/command-skill-policy.md`

- **Naming Convention section** (lines 52-66): Same rules as above
- **Migration Checklist, Phase 1** (lines 279-287): Explicitly lists `src/skills/sc-cleanup-audit/` --> `src/skills/sc-cleanup-audit-protocol/` with target SKILL.md `name` field `sc:cleanup-audit-protocol`

### 2.2 Tasklist Tasks

No tasklist task in `tasklist-P6.md` explicitly targets the cleanup-audit directory rename. The sprint scope (`tasklist-P6.md` Source Snapshot) states it modifies files across "3 skill packages (`sc-roadmap`, `sc-adversarial`, `roadmap` command)" -- cleanup-audit is not in the sprint's primary scope. The rename was executed as part of the architecture policy's Migration Phase 1 alongside the sprint.

### 2.3 Decision Artifacts

No D-series artifact references the cleanup-audit rename.

### 2.4 SKILL.md Content Changes

**Frontmatter only** (git similarity R099, with unstaged modification):

| Field | Before | After | Notes |
|-------|--------|-------|-------|
| `name` | `cleanup-audit` | `sc:cleanup-audit-protocol` | Fixed missing `sc:` prefix AND added `-protocol` suffix |

This is the only skill where the `name` field transformation also corrected a pre-existing inconsistency: the old name lacked the `sc:` prefix that all other skills had.

No body content changes.

### 2.5 Companion Files (11 pure renames, R100)

| # | File | Type |
|---|------|------|
| 1 | `__init__.py` | Python package marker |
| 2 | `rules/dynamic-use-checklist.md` | Rule file |
| 3 | `rules/pass1-surface-scan.md` | Rule file |
| 4 | `rules/pass2-structural-audit.md` | Rule file |
| 5 | `rules/pass3-cross-cutting.md` | Rule file |
| 6 | `rules/verification-protocol.md` | Rule file |
| 7 | `scripts/repo-inventory.sh` | Script |
| 8 | `templates/batch-report.md` | Template |
| 9 | `templates/final-report.md` | Template |
| 10 | `templates/finding-profile.md` | Template |
| 11 | `templates/pass-summary.md` | Template |

**Total files**: 12 (1 modified SKILL.md + 11 pure renames)

---

## 3. sc-roadmap --> sc-roadmap-protocol

### 3.1 Architecture Policy Mandate

**Source**: `docs/architecture/command-skill-policy.md`

- **Naming Convention section** (lines 52-66): Same rules as above
- **Migration Checklist, Phase 1** (lines 279-287): Explicitly lists `src/skills/sc-roadmap/` --> `src/skills/sc-roadmap-protocol/` with target SKILL.md `name` field `sc:roadmap-protocol`
- **Source Layout section** (lines 215-247): Shows `sc-roadmap-protocol/` as the target layout with SKILL.md and refs/ subdirectory

### 3.2 Tasklist Tasks

The roadmap skill is the PRIMARY target of the sprint. Multiple tasks directly modify or depend on this skill:

- **T02.01** (R-004, D-0004): "Skill in allowed-tools -- roadmap command" -- adds `Skill` to the roadmap command's allowed-tools
- **T02.02** (R-005, D-0005): "Skill in allowed-tools -- SKILL.md" -- adds `Skill` to the roadmap SKILL.md's allowed-tools
- **T02.03** (R-006/R-007/R-008, D-0006/D-0007/D-0008): "Wave 2 step 3 rewritten as sub-steps 3a-3f" -- the major SKILL.md body rewrite (STRICT tier, XL effort, Medium risk). This is the highest-risk task in the sprint.
- **T03.01** (R-009, D-0009): Verification test for Skill tool availability in this skill
- **T03.02** (R-010, D-0010): Wave 2 Step 3 structural audit
- **T05.02** (R-012, D-0016): Wave 1A step 2 fix
- **T05.03** (R-013, D-0017): Pseudo-CLI conversion in adversarial-integration.md ref
- **T06.02** (R-019, D-0019): Cross-reference field consistency between roadmap SKILL.md and adversarial integration ref

### 3.3 Decision Artifacts

| Artifact | Task | Content | Relevance to Rename/Changes |
|----------|------|---------|----------------------------|
| D-0004 | T02.01 | `Skill` added to roadmap.md allowed-tools | Enables Skill tool invocation from command |
| D-0005 | T02.02 | `Skill` added to roadmap SKILL.md allowed-tools | Enables cross-skill invocation from within the protocol |
| **D-0006** | T02.03 | Wave 2 step 3 sub-steps 3a-3f specification | Specifies the decomposition of the monolithic step 3 into 6 atomic sub-steps |
| **D-0007** | T02.03 | Fallback protocol (F1, F2/3, F4/5) specification | Specifies the 3-stage fallback state machine for when Skill tool is unavailable |
| **D-0008** | T02.03 | Return contract routing (step 3e) specification | Specifies missing-file guard, YAML error handling, 3-status routing, convergence threshold 0.6 |

**Artifact paths** (all relative to `.dev/releases/current/v2.01-Roadmap-v3/tasklist/`):
- `artifacts/D-0004/evidence.md`
- `artifacts/D-0005/evidence.md`
- `artifacts/D-0006/spec.md`
- `artifacts/D-0007/spec.md`
- `artifacts/D-0008/spec.md`

### 3.4 SKILL.md Content Changes

**THIS IS THE ONLY SKILL WITH SUBSTANTIVE BODY CHANGES.**

Git similarity: R081 (19% content change).

#### Frontmatter Changes

| Field | Before | After |
|-------|--------|-------|
| `name` | `sc:roadmap` | `sc:roadmap-protocol` |
| `allowed-tools` | `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` | `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` |

#### Body Changes: Wave 2 Step 3 Expansion (+17 lines)

The old step 3 was a single line:
```
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from
   `refs/adversarial-integration.md` "Agent Specification Parsing" section. [...]
```

The new step 3 expands into sub-steps 3a through 3f:

| Sub-step | Purpose | Specified by |
|----------|---------|-------------|
| **3a** [Parse agents] | Parse `--agents` value, validate 2-10 count | D-0006 |
| **3b** [Expand variants] | Assign primary persona to model-only agents | D-0006 |
| **3c** [Add orchestrator] | Add debate-orchestrator if agent count >= 3 | D-0006 |
| **3d** [Execute fallback protocol] | Sole invocation mechanism (Skill tool unavailable) | D-0007 |
| -- F1 | Variant generation via Task agent | D-0007 |
| -- F2/3 | Diff analysis + single-round debate (merged) | D-0007 |
| -- F4/5 | Base selection + merge + contract (merged) | D-0007 |
| **3e** [Consume return contract] | Read return-contract.yaml with guards and routing | D-0008 |
| **3f** [Skip template] | Skip template generation if adversarial succeeded | D-0006 |

The fallback protocol in step 3d includes the WARNING emission: `"sc:adversarial Skill tool unavailable -- executing fallback protocol (fallback_mode: true)"` and documents three error types that also trigger fallback: (1) Skill not in allowed-tools, (2) skill not found, (3) skill already running.

Step 3e implements a convergence threshold of 0.6, with three status routing paths (success, partial, failed) and interactive/non-interactive behavior for low-convergence partial results.

### 3.5 Cross-Reference to D-0006/D-0007/D-0008 Specifications

These three artifacts were produced by task T02.03 (STRICT tier, XL effort) and form the specification chain for the Wave 2 Step 3 expansion:

**D-0006** (`artifacts/D-0006/spec.md`):
- Specifies the 6 sub-step decomposition (3a through 3f)
- Defines atomic verification boundaries for each sub-step
- Source task: T02.03, Roadmap item: R-006

**D-0007** (`artifacts/D-0007/spec.md`):
- Specifies the 3-stage fallback state machine: F1 (variant generation), F2/3 (diff analysis + debate, merged), F4/5 (selection + merge + contract, merged)
- Defines the return contract schema with 7 fields: `status`, `merged_output_path`, `convergence_score`, `fallback_mode`, `artifacts_dir`, `unresolved_conflicts`, `base_variant`
- Sets fallback convergence sentinel at 0.5 (deliberately below the 0.6 threshold)
- Source task: T02.03, Roadmap item: R-007

**D-0008** (`artifacts/D-0008/spec.md`):
- Specifies step 3e return contract routing logic
- Defines missing-file guard behavior
- Defines YAML parse error handling
- Defines 3-status routing with convergence threshold 0.6
- Sets interactive vs non-interactive behavior for low-convergence results
- Source task: T02.03, Roadmap item: R-008

**Evidence chain**: `T02.03 evidence (evidence/T02.03/result.md)` records an 8-point structural audit (all pass) validating that D-0006, D-0007, and D-0008 were correctly implemented in the SKILL.md body. Checkpoint `CP-P02-END.md` formally records Phase 2 completion.

**Decision lineage**: The D-0006/D-0007/D-0008 specifications are themselves informed by the adversarial pipeline output (specification-draft-v2.md, ADV-8) and the foundational probe decision (D-0001 TOOL_NOT_AVAILABLE --> D-0002 FALLBACK-ONLY variant). The probe result is why step 3d implements fallback as the sole invocation mechanism rather than a contingency path.

### 3.6 Companion Files (6 pure renames, R100)

| # | File | Type |
|---|------|------|
| 1 | `__init__.py` | Python package marker |
| 2 | `refs/adversarial-integration.md` | Ref file (adversarial pipeline integration) |
| 3 | `refs/extraction-pipeline.md` | Ref file (requirement extraction) |
| 4 | `refs/scoring.md` | Ref file (scoring algorithms) |
| 5 | `refs/templates.md` | Ref file (template discovery and generation) |
| 6 | `refs/validation.md` | Ref file (validation protocol) |

**Total files**: 7 (1 modified SKILL.md + 6 pure renames)

---

## 4. sc-task-unified --> sc-task-unified-protocol

### 4.1 Architecture Policy Mandate

**Source**: `docs/architecture/command-skill-policy.md`

- **Naming Convention section** (lines 52-66): Same rules as above
- **Migration Checklist, Phase 1** (lines 279-287): Explicitly lists `src/skills/sc-task-unified/` --> `src/skills/sc-task-unified-protocol/` with target SKILL.md `name` field `sc:task-unified-protocol`
- **Backlog section** (line 318): Notes "Split `task-unified.md` command (567L)" as Low priority since it "Already has protocol skill"

### 4.2 Tasklist Tasks

No tasklist task in `tasklist-P6.md` explicitly targets the task-unified directory rename. The sprint scope focuses on `sc-roadmap` and `sc-adversarial`. The rename was executed as part of the architecture policy's Migration Phase 1.

The task-unified skill is referenced indirectly:
- **Deterministic Rule 8** in `tasklist-P6.md`: "Applied `/sc:task-unified` algorithm with compound phrase overrides" -- the tasklist generation itself used the task-unified classification system

### 4.3 Decision Artifacts

No D-series artifact references the task-unified rename.

### 4.4 SKILL.md Content Changes

**Frontmatter only** (git similarity R099, with unstaged modification):

| Field | Before | After | Notes |
|-------|--------|-------|-------|
| `name` | `sc-task-unified` | `sc:task-unified-protocol` | Hyphen changed to colon prefix + `-protocol` suffix |

No body content changes.

### 4.5 Companion Files (1 pure rename, R100)

| # | File | Type |
|---|------|------|
| 1 | `__init__.py` | Python package marker |

**Total files**: 2 (1 modified SKILL.md + 1 pure rename)

---

## 5. sc-validate-tests --> sc-validate-tests-protocol

### 5.1 Architecture Policy Mandate

**Source**: `docs/architecture/command-skill-policy.md`

- **Naming Convention section** (lines 52-66): Same rules as above
- **Migration Checklist, Phase 1** (lines 279-287): Explicitly lists `src/skills/sc-validate-tests/` --> `src/skills/sc-validate-tests-protocol/` with target SKILL.md `name` field `sc:validate-tests-protocol`

### 5.2 Tasklist Tasks

No tasklist task in `tasklist-P6.md` explicitly targets the validate-tests directory rename. The rename was executed as part of the architecture policy's Migration Phase 1.

### 5.3 Decision Artifacts

No D-series artifact references the validate-tests rename.

### 5.4 SKILL.md Content Changes

**Frontmatter only** (git similarity R099, with unstaged modification):

| Field | Before | After | Notes |
|-------|--------|-------|-------|
| `name` | `sc-validate-tests` | `sc:validate-tests-protocol` | Hyphen changed to colon prefix + `-protocol` suffix |

No body content changes.

### 5.5 Companion Files (2 pure renames, R100)

| # | File | Type |
|---|------|------|
| 1 | `__init__.py` | Python package marker |
| 2 | `classification-algorithm.yaml` | YAML specification |

**Total files**: 3 (1 modified SKILL.md + 2 pure renames)

---

## Summary: Roadmap SKILL.md as the Only Substantive Body Change

Of all 5 skill renames, only `sc-roadmap-protocol/SKILL.md` received body content changes beyond frontmatter updates. The other 4 skills had frontmatter-only `name` field changes (R099 git similarity). The roadmap SKILL.md had R081 git similarity (19% content change) due to the Wave 2 Step 3 expansion.

| Skill | Frontmatter Changes | Body Changes | Git Similarity | Driving Artifacts |
|-------|---------------------|--------------|----------------|-------------------|
| adversarial | `name` field only | None | R099 | Architecture policy only |
| cleanup-audit | `name` field + `sc:` prefix fix | None | R099 | Architecture policy only |
| **roadmap** | **`name` field + `Skill` in allowed-tools** | **Wave 2 Step 3: +17 lines (3a-3f sub-steps)** | **R081** | **D-0006, D-0007, D-0008 (via T02.03)** |
| task-unified | `name` field only | None | R099 | Architecture policy only |
| validate-tests | `name` field only | None | R099 | Architecture policy only |

The roadmap SKILL.md body changes were specified by three STRICT-tier artifacts produced by task T02.03 (the sprint's highest-risk task at XL effort, Medium risk):

- **D-0006** -- Sub-step decomposition (3a-3f)
- **D-0007** -- Fallback protocol state machine (F1, F2/3, F4/5)
- **D-0008** -- Return contract routing logic (step 3e)

These artifacts are stored at:
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0006/spec.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0007/spec.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0008/spec.md`

Evidence of correct implementation: `.dev/releases/current/v2.01-Roadmap-v3/tasklist/evidence/T02.03/result.md` (8-point structural audit, all pass).

Checkpoint confirming Phase 2 completion: `.dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/CP-P02-END.md`.

---

## Grand Totals

| Metric | Count |
|--------|-------|
| Skill directories renamed | 5 |
| SKILL.md files modified (frontmatter) | 5 |
| SKILL.md files with body changes | 1 (roadmap only) |
| Companion files (pure rename, R100) | 25 |
| Total files affected by renames | 30 |
| D-series artifacts specifying body changes | 3 (D-0006, D-0007, D-0008) |
| Tasklist tasks driving body changes | 1 primary (T02.03), 2 supporting (T02.01, T02.02) |

---

## Source Cross-Reference Index

| Document | Path | Role in This Analysis |
|----------|------|-----------------------|
| Architecture policy | `docs/architecture/command-skill-policy.md` | Mandates `-protocol` suffix, naming convention, migration checklist |
| Canonical tasklist | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P6.md` | Task definitions (T02.01-T02.03), deliverable mappings, traceability matrix |
| Framework synthesis | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/framework-synthesis-A.md` | Rename inventory, SKILL.md change details, atomic change groups |
| Dev planning synthesis | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/dev-planning-synthesis-A.md` | Decision chain, policy summary, task evolution |
| Dev artifacts synthesis | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/dev-artifacts-synthesis-A.md` | D-0006/D-0007/D-0008 specs, evidence chain, adversarial pipeline lineage |
| Phase 1 checkpoint | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/CP-P01-END.md` | TOOL_NOT_AVAILABLE probe result driving fallback-only variant |
| Phase 2 checkpoint | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/CP-P02-END.md` | 8-point structural audit confirming Wave 2 Step 3 implementation |
