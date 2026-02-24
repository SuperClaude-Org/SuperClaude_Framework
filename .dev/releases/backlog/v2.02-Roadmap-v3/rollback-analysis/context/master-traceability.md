# Master Traceability Matrix: v2.01-Roadmap-V3

**Generated:** 2026-02-24
**Branch:** `feature/v2.01-Roadmap-V3`
**Base Commit:** `9060a65`
**Source Documents:** 6 synthesis files (2 dev-planning, 2 dev-artifacts, 2 framework)

---

## 1. Task-to-File Matrix

For each tasklist task, the framework files it changed (or will change). Tasks are sourced from `tasklist-P6.md` (18 tasks across 6 phases).

### Phase 1: Foundation

| Task | Description | Tier | Framework Files Changed | Status |
|------|-------------|------|------------------------|--------|
| **T01.01** | Skill Tool Probe | EXEMPT | None (produces D-0001 evidence only; no source file changes) | COMPLETE |
| **T01.02** | Prerequisite Validation | EXEMPT | None (validation only; produces D-0003 evidence) | COMPLETE |
| **T01.03** | Tier Classification Policy | EXEMPT | None (policy decision only; produces T01.03/notes.md) | COMPLETE |

### Phase 2: Invocation Wiring

| Task | Description | Tier | Framework Files Changed | Status |
|------|-------------|------|------------------------|--------|
| **T02.01** | Skill in roadmap.md allowed-tools | LIGHT | `src/superclaude/commands/roadmap.md` (added `, Skill` to allowed-tools frontmatter); `.claude/commands/sc/roadmap.md` (mirror) | COMPLETE |
| **T02.02** | Skill in SKILL.md allowed-tools | LIGHT | `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` (added `Skill` to allowed-tools) | COMPLETE |
| **T02.03** | Wave 2 Step 3 Rewrite | STRICT | `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` (Wave 2 Step 3 expansion, +17 lines: sub-steps 3a-3f, fallback protocol, return contract routing) | COMPLETE |

### Phase 3: Structural Validation (NOT STARTED)

| Task | Description | Tier | Framework Files Changed | Status |
|------|-------------|------|------------------------|--------|
| **T03.01** | Validation of fallback structure | EXEMPT | Expected: None (read-only validation) | PENDING |
| **T03.02** | Structural audit of wiring | EXEMPT | Expected: None (read-only audit) | PENDING |

### Phase 4: Return Contract & Artifact Gates (NOT STARTED)

| Task | Description | Tier | Framework Files Changed | Status |
|------|-------------|------|------------------------|--------|
| **T04.01** | Return contract write instruction | STRICT | Expected: `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | PENDING |
| **T04.02** | Artifact gate specification | STRICT | Expected: `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md` | PENDING |
| **T04.03** | Artifact gate standard | STANDARD | Expected: `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md` | PENDING |

### Phase 5: Polish & Documentation (NOT STARTED)

| Task | Description | Tier | Framework Files Changed | Status |
|------|-------------|------|------------------------|--------|
| **T05.01** | Execution Vocabulary Glossary | STANDARD | Expected: Documentation files | PENDING |
| **T05.02** | Wave 1A Step 2 Fix | STANDARD | Expected: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | PENDING |
| **T05.03** | Pseudo-CLI Conversion | STANDARD | Expected: `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md` | PENDING |

### Phase 6: Wrap-up (NOT STARTED)

| Task | Description | Tier | Framework Files Changed | Status |
|------|-------------|------|------------------------|--------|
| **T06.01-T06.05** | Sprint close-out tasks | EXEMPT/STANDARD | Expected: Documentation and tasklist updates only | PENDING |

### Parallel Architecture Changes (From command-skill-policy.md, not tasklist-tracked)

These framework changes were driven by the architecture policy document but are not tracked as individual tasks in the sprint tasklist:

| Change | Framework Files | Driver |
|--------|----------------|--------|
| 5 skill directory renames | 30 files in `src/superclaude/skills/` (5 SKILL.md modified, 25 pure renames) | `command-skill-policy.md` Migration Phase 1 |
| 5 command file updates (Activation sections) | 10 files (5 in `src/superclaude/commands/`, 5 in `.claude/commands/sc/`) | `command-skill-policy.md` Migration Phase 2 |
| task-unified.md major rewrite (-461 lines) | `src/superclaude/commands/task-unified.md`, `.claude/commands/sc/task-unified.md` | `command-skill-policy.md` (150-line cap) |
| Makefile updates | `Makefile` (+114 lines, -9 lines) | `command-skill-policy.md` CI enforcement spec |
| 5 new .claude/skills/ dev copies | 25 files in `.claude/skills/sc-*-protocol/` | `make sync-dev` after renames |

---

## 2. Decision-to-Implementation Matrix

For each D-series artifact, the framework changes it drove.

| Artifact | Source Task | Decision Content | Framework Changes Driven | Implementation Status |
|----------|-----------|------------------|--------------------------|----------------------|
| **D-0001** | T01.01 | Skill tool returns TOOL_NOT_AVAILABLE | No direct framework change; determines that all invocation uses fallback-only variant | RECORDED |
| **D-0002** | T01.01 | Sprint variant: FALLBACK-ONLY selected | Cascading: T02.03 omits primary Skill call path; F1/F2-3/F4-5 fallback becomes sole execution path; G2 validation deferred | APPLIED (via T02.03) |
| **D-0003** | T01.02 | 6/6 prerequisites pass | No framework change; gate clearance for Phase 2+ | VERIFIED |
| **D-0004** | T02.01 | Skill added to roadmap.md allowed-tools | `src/superclaude/commands/roadmap.md`: `, Skill` added to allowed-tools frontmatter | APPLIED |
| **D-0005** | T02.02 | Skill added to sc-roadmap SKILL.md allowed-tools | `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`: `Skill` added to allowed-tools | APPLIED |
| **D-0006** | T02.03 | Wave 2 Step 3 decomposed into sub-steps 3a-3f | `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`: Wave 2 Step 3 expansion (+17 lines) | APPLIED |
| **D-0007** | T02.03 | Fallback protocol F1, F2/3, F4/5 specified | `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`: Fallback protocol wired into step 3d | APPLIED |
| **D-0008** | T02.03 | Return contract routing in step 3e; convergence threshold 0.6 | `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`: Return contract routing inlined in step 3e | APPLIED |
| **D-0009 to D-0022** | T03.01+ | Not yet produced | Phases 3-6 framework changes pending | NOT STARTED |

### Policy Artifact

| Artifact | Decision | Framework Impact |
|----------|----------|------------------|
| **T01.03/notes.md** | `.md` EXEMPT booster does NOT apply to executable spec files | Sets compliance tiers for T02.01 (LIGHT), T02.02 (LIGHT), T02.03 (STRICT), T04.01 (STRICT), T04.02 (STRICT). Prevents 9 tasks from being auto-classified as EXEMPT. |

### Architecture Policy Artifact

| Artifact | Decision | Framework Impact |
|----------|----------|------------------|
| **command-skill-policy.md** | 3-tier loading model; `-protocol` naming; 150-line command cap; 10 CI checks | 5 directory renames (30 files), 5 command updates (10 files), Makefile changes (+105 net lines), task-unified.md 81% reduction |

---

## 3. Evidence-to-Verification Matrix

For each evidence record, what it verified and the verification method used.

| Evidence Record | Task | What Was Verified | Verification Method | Artifact Cross-Reference | Result |
|-----------------|------|-------------------|---------------------|--------------------------|--------|
| `evidence/T01.01/result.md` | T01.01 | Skill tool callable API availability | Manual runtime probe of Skill tool | D-0001, D-0002 | TOOL_NOT_AVAILABLE |
| `evidence/T01.02/result.md` | T01.02 | 6 prerequisites: 3 skill files readable, 2 Make targets, 1 git status | Manual bash checks (file existence, Make target verification) | D-0003 | PASS (6/6) |
| `evidence/T01.03/result.md` | T01.03 | Tier classification policy for executable .md files | Manual policy reasoning and recording | T01.03/notes.md | Policy decision recorded |
| `evidence/T02.01/result.md` | T02.01 | `Skill` present in roadmap.md allowed-tools | `grep` on `src/superclaude/commands/roadmap.md` | D-0004 | PASS |
| `evidence/T02.02/result.md` | T02.02 | `Skill` present in sc-roadmap SKILL.md allowed-tools | `grep` on `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | D-0005 | PASS |
| `evidence/T02.03/result.md` | T02.03 | Wave 2 Step 3 structural integrity (8-point audit) | Structural audit + adversarial review | D-0006, D-0007, D-0008 | PASS (8/8) |

### T02.03 Structural Audit Detail (8 Points)

| # | Check | Result |
|---|-------|--------|
| 1 | Sub-steps 3a through 3f present in Wave 2 Step 3 | PASS |
| 2 | Fallback protocol covers 3 error types | PASS |
| 3 | F1/F2-3/F4-5 steps implemented | PASS |
| 4 | WARNING emission present for fallback activation | PASS |
| 5 | Missing-file guard in step 3e | PASS |
| 6 | YAML parse error handler in step 3e | PASS |
| 7 | Three-status routing (success/partial/failed) | PASS |
| 8 | Convergence threshold set to 0.6 | PASS |

### Evidence Structure Pattern

All evidence files follow a two-tier structure:
- **Tier 1 (result.md)**: 5-6 lines; result, validation method, artifact pointer
- **Tier 2 (artifact)**: Full detailed evidence with specifications, checklists, or policy rationale

---

## 4. Cross-Category Dependencies

How dev planning decisions required dev artifacts which drove framework changes.

### Complete Dependency Chain

```
LAYER 1: ARCHITECTURE POLICY (Dev Planning)
===========================================
command-skill-policy.md (2026-02-23)
    |
    |-- Defines 3-tier loading model
    |-- Mandates `-protocol` naming convention
    |-- Sets 150-line command cap
    |-- Specifies 10 CI enforcement checks
    |
    v

LAYER 2: DESIGN ARTIFACTS (Dev Artifacts)
==========================================
3 Approach Documents (AP-1, AP-2, AP-3)
    |
    v
Adversarial Pipeline (ADV-1 through ADV-8)
    |-- debate-transcript.md (12 convergence decisions)
    |-- scoring-rubric.md (Ap2 scores 0.900)
    |-- base-selection.md (Ap2 selected as base)
    |-- refactoring-plan.md (4 from Ap1, 5 from Ap3 absorbed)
    |-- merged-approach.md (unified design, 546 lines)
    |-- specification-draft-v1.md (653 lines, 10 issues addressed)
    |-- spec-panel-review.md (27 findings, score 5.5/10)
    |-- specification-draft-v2.md (872 lines, all 27 findings addressed)
    |
    v

LAYER 3: SPRINT EXECUTION (Dev Planning + Dev Artifacts)
=========================================================
tasklist-P6.md (18 tasks, 6 phases)
    |
    +-- Phase 1: Foundation
    |       T01.01 --> D-0001 (probe) --> D-0002 (variant) --> FALLBACK-ONLY
    |       T01.02 --> D-0003 (prereqs) --> GATE CLEARED
    |       T01.03 --> Policy ruling (EXEMPT exclusion)
    |
    +-- Phase 2: Invocation Wiring
    |       T02.01 --> D-0004 --> roadmap.md allowed-tools change
    |       T02.02 --> D-0005 --> SKILL.md allowed-tools change
    |       T02.03 --> D-0006/D-0007/D-0008 --> Wave 2 Step 3 expansion
    |
    v

LAYER 4: FRAMEWORK CHANGES (Actual Source Code)
=================================================
Architecture policy drives:
    +-- 5 skill directory renames (30 files)
    +-- 5 command file updates (10 files)
    +-- task-unified.md rewrite (567 -> 106 lines)
    +-- Makefile changes (+105 net lines)
    +-- 5 .claude/skills/ dev copies (25 files)

Sprint execution drives:
    +-- roadmap.md: Skill in allowed-tools (D-0004)
    +-- sc-roadmap-protocol SKILL.md: Skill in allowed-tools (D-0005)
    +-- sc-roadmap-protocol SKILL.md: Wave 2 Step 3 expansion (D-0006/D-0007/D-0008)
```

### Key Cross-Category Linkages

| Dev Planning Decision | Required Dev Artifact | Drove Framework Change |
|-----------------------|----------------------|----------------------|
| Architecture policy: `-protocol` naming | N/A (policy is self-contained) | 5 directory renames (30 files), 5 frontmatter updates |
| Architecture policy: 150-line command cap | N/A | task-unified.md reduction (567 -> 106 lines) |
| Architecture policy: CI enforcement | N/A | Makefile `lint-architecture` target (+113 lines) |
| T01.01 probe decision (TOOL_NOT_AVAILABLE) | D-0001 (probe evidence), D-0002 (variant decision) | T02.03 implements fallback-only variant in SKILL.md |
| T01.03 tier classification ruling | T01.03/notes.md (policy artifact) | T02.03 classified as STRICT (not EXEMPT), requiring 8-point structural audit |
| Adversarial debate convergence (C-002) | ADV-1 debate transcript | Enhanced 5-step fallback (F1-F5) in D-0007, applied to SKILL.md |
| Adversarial debate convergence (C-006) | ADV-1 debate transcript | `invocation_method` field in return contract, applied via D-0008 |
| Spec-v2 panel review resolution | ADV-7 (27 findings), ADV-8 (spec-v2) | Specification drives D-0006/D-0007/D-0008 structural decisions |

### Information Flow Diagram

```
command-skill-policy.md -----> Renames, Command updates, Makefile
        |                           (Architecture-driven changes)
        |
        v
tasklist-P6.md -----> Checkpoints (CP-P01, CP-P02)
        |                           (Execution records)
        |
        v
D-0001 (probe) -----> D-0002 (variant) -----> All Phase 2+ execution
        |                                           |
        v                                           v
D-0003 (prereqs) -----> GATE -----> D-0004/D-0005 -----> D-0006/D-0007/D-0008
                                    (allowed-tools)       (Wave 2 Step 3 specs)
                                          |                       |
                                          v                       v
                                   roadmap.md change       SKILL.md expansion
                                   (framework change)      (framework change)
```

---

## 5. Unresolved Items

Tasks, decisions, and planned changes that do NOT yet have corresponding framework changes.

### 5.1 Incomplete Sprint Tasks (Phases 3-6)

| Task | Description | Expected Framework Change | Blocking Factor |
|------|-------------|--------------------------|-----------------|
| **T03.01** | Fallback structure validation | None (read-only) | Phase 2 just completed |
| **T03.02** | Structural audit of wiring | None (read-only) | Phase 2 just completed |
| **T04.01** | Return contract write instruction | Edit to `sc-adversarial-protocol/SKILL.md` | Blocked on Phase 3 |
| **T04.02** | Artifact gate specification | Edit to `refs/adversarial-integration.md` | Blocked on Phase 3 |
| **T04.03** | Artifact gate standard | Edit to `refs/adversarial-integration.md` | Blocked on T04.02 |
| **T05.01** | Execution Vocabulary Glossary | Documentation additions | Blocked on Phase 4 |
| **T05.02** | Wave 1A Step 2 Fix | Edit to roadmap SKILL.md | Blocked on Phase 4 |
| **T05.03** | Pseudo-CLI Conversion | Edit to `refs/adversarial-integration.md` | Blocked on Phase 4 |
| **T06.01-T06.05** | Sprint close-out | Documentation and tasklist updates | Blocked on Phase 5 |

### 5.2 Architecture Policy Items Not Yet Implemented

| Item | Priority | Description | Current Status |
|------|----------|-------------|----------------|
| `make lint-architecture` target | HIGH | 10 CI checks defined in policy; 6 implemented in Makefile | PARTIAL -- 6 of 10 checks implemented |
| `claude -p` Tier 2 ref loader | HIGH | Script to load ref files on-demand via headless CLI | NOT STARTED (design phase) |
| Cross-skill invocation patterns | HIGH | Patterns for skills to invoke other skills | NOT STARTED (design phase) |
| 6 oversized command splits | MEDIUM | Commands exceeding 150-line cap to be split | NOT STARTED |
| Architecture policy deduplication | LOW | Two identical copies of policy doc exist; need single canonical source | NOT RESOLVED |

### 5.3 Missing Dev Artifacts

| Expected Artifact | Referenced By | Why Missing |
|-------------------|---------------|-------------|
| `refs/headless-invocation.md` | Approach 2, merged-approach, spec-v1, spec-v2 | Infrastructure file never created |
| Probe fixtures (`spec-minimal.md`, `variant-a.md`, `variant-b.md`) | Approach 1, spec-v2 | Test fixtures never created |
| `expected-schema.yaml` / `return-contract.yaml` | Approach 1 (Appendix B) | Schema file never created |
| D-0009, D-0010 | spec-v2 deliverable registry | Phases 3-4 not yet executed |
| Phase 3-6 evidence records | Tasklist structure | Phases not yet executed |
| Phase 3-6 checkpoint reports | Tasklist checkpoint definitions | Phases not yet executed |

---

## 6. Bug Tracking

All bugs and issues consolidated from all 6 synthesis documents, deduplicated and severity-ranked.

### BUG-001: `allowed-tools` Gap (4 of 5 Commands Missing `Skill`)

**Severity:** HIGH -- Potential functional break
**Found in:** Framework Synthesis A (Section 5.3), Framework Synthesis B (Section 3.1)
**Confirmed by:** Both agents independently identified this issue

**Description:** All 5 commands now include a mandatory `## Activation` section that invokes `> Skill sc:{name}-protocol`. However, only `roadmap.md` added `Skill` to its `allowed-tools` frontmatter. The other 4 commands (`adversarial.md`, `cleanup-audit.md`, `task-unified.md`, `validate-tests.md`) did NOT add `Skill` to their `allowed-tools`.

**Affected Files (8):**
- `src/superclaude/commands/adversarial.md` + `.claude/commands/sc/adversarial.md`
- `src/superclaude/commands/cleanup-audit.md` + `.claude/commands/sc/cleanup-audit.md`
- `src/superclaude/commands/task-unified.md` + `.claude/commands/sc/task-unified.md`
- `src/superclaude/commands/validate-tests.md` + `.claude/commands/sc/validate-tests.md`

**Risk:** If Claude Code enforces the `allowed-tools` whitelist strictly, 4 of 5 commands will fail to invoke their protocol skill.

**Mitigation Notes:**
- Some commands use `mcp-servers` instead of `allowed-tools`, so the field may not apply uniformly.
- The `Skill` tool may bypass the `allowed-tools` gate (treated as a meta-tool).
- Needs empirical testing to confirm whether this is a real break.

**Recommendation:** Add `Skill` to `allowed-tools` in all 4 affected command files.

---

### BUG-002: Path Inconsistency Between Tasklist and Git State

**Severity:** MEDIUM -- Stale references
**Found in:** Dev Planning Synthesis A (Section 5), Dev Planning Synthesis B (Issue 1)
**Confirmed by:** Both agents independently identified this issue

**Description:** The tasklist files (`tasklist-P5.md`, `tasklist-P6.md`) reference skill paths using OLD directory names (`sc-adversarial/`, `sc-roadmap/`), but git status shows these directories have already been renamed to `sc-adversarial-protocol/`, `sc-roadmap-protocol/`, etc.

**Affected Files:**
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P5.md`
- `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P6.md`

**Impact:** Task descriptions reference paths that no longer exist. Breaks automated path validation and causes confusion during execution.

**Recommendation:** Update both tasklist files to use `-protocol` paths.

---

### BUG-003: Path Inconsistency Across 24 of 25 Dev Artifacts

**Severity:** MEDIUM -- Stale references in historical documents
**Found in:** Dev Artifacts Synthesis A (Section 8.4), Dev Artifacts Synthesis B (Section 5)
**Confirmed by:** Both agents independently identified this issue

**Description:** 24 of 25 dev artifacts use pre-rename paths (`sc-adversarial/`, `sc-roadmap/`). Only `specification-draft-v2.md` uses the corrected `-protocol` suffix.

**Affected Artifacts:** All D-0001 through D-0008, all approach documents, all adversarial pipeline outputs except spec-v2, all evidence records.

**Impact:** Artifact path references are stale. Any automated validation or grep-based checking against these paths will fail.

**Recommendation:** Accept as historical (artifacts record the state at time of creation) or batch-update all artifact path references.

---

### BUG-004: Architecture Policy Document Duplication

**Severity:** MEDIUM -- Drift risk
**Found in:** Dev Planning Synthesis A (Section 4), Dev Planning Synthesis B (Issue 2)
**Confirmed by:** Both agents independently identified this issue

**Description:** Two identical 337-line files exist with no indication of which is canonical:
- `docs/architecture/command-skill-policy.md`
- `src/superclaude/ARCHITECTURE.md`

No symlink, no `make sync` target, and no note in either file about the other.

**Impact:** Future edits to one will not propagate to the other. High drift risk.

**Recommendation:** Designate one as canonical (likely `docs/architecture/`) and make the other a symlink or add to `sync-dev` target.

---

### BUG-005: Roadmap SKILL.md Internal Stale Path Reference

**Severity:** MEDIUM -- Potential read failure
**Found in:** Framework Synthesis B (Section 3.2)

**Description:** The roadmap SKILL.md Wave 0 step 5 still references `src/superclaude/skills/sc-adversarial/SKILL.md` (old path without `-protocol` suffix).

**Affected File:** `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

**Impact:** If Claude follows this path literally, it will attempt to read a non-existent file. May cause silent failure in the adversarial pipeline integration.

**Recommendation:** Update to `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`.

---

### BUG-006: `make lint-architecture` Incomplete vs Policy Spec

**Severity:** LOW -- Partial enforcement
**Found in:** Dev Planning Synthesis A (Section 4), Dev Planning Synthesis B (Issue 4)

**Description:** The architecture policy defines 10 CI enforcement checks, but the Makefile implements only 6 checks. The 4 missing checks are not specified in the synthesis documents.

**Impact:** Gap between policy-specified and implemented enforcement. Violations against the 4 unimplemented checks can accumulate undetected.

**Recommendation:** Implement remaining 4 checks or document which checks were deferred and why.

---

### BUG-007: Checkpoint Artifact Existence Unverified

**Severity:** LOW -- Potential phantom references
**Found in:** Dev Planning Synthesis B (Issue 6)

**Description:** Checkpoint reports reference 8 artifact files (D-0001 through D-0008) across `artifacts/` and task-specific directories. The `evidence/` directory appears as untracked in git status, but whether all referenced artifact files actually exist on disk was not confirmed.

**Recommendation:** Run `find .dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/ -type f` to verify existence.

---

### BUG-008: Return Contract Field Count Mismatch

**Severity:** LOW (resolved in spec-v2) -- Historical inconsistency
**Found in:** Dev Artifacts Synthesis A (Section 6.2), Dev Artifacts Synthesis B (Section 3)

**Description:** `merged-approach.md` claims "9+1=10 fields" for the return contract, but `SKILL.md` FR-007 defines only 5 fields. This was flagged as CRITICAL (W1/F1/S1) in the panel review and resolved in spec-v2 with a producer/consumer ownership model.

**Status:** Resolved in `specification-draft-v2.md`. Historical artifacts still contain the inconsistency.

---

### BUG-009: Wave 2 Step 3e Architectural Divergence

**Severity:** LOW -- Design debt
**Found in:** Dev Planning Synthesis A (Section 8.6, Architectural note)

**Description:** Step 3e inlines return contract routing directly rather than delegating to the ref section, diverging from Wave 1A's pattern of ref-delegation. This is a conscious implementation choice but may need documentation to prevent confusion.

**Recommendation:** Document the divergence rationale in the SKILL.md or a design decision record.

---

### BUG-010: Sprint Variant Decision May Be Environment-Dependent

**Severity:** LOW -- Forward-execution risk
**Found in:** Dev Planning Synthesis B (Issue 7)

**Description:** T01.01's `TOOL_NOT_AVAILABLE` result is an empirical finding about the runtime environment. If the Skill tool becomes available in a different environment or Claude Code version, the entire fallback-only variant decision chain could be invalidated.

**Impact:** Low for rollback-recreation (the decision is recorded). High for forward execution in a changed environment.

**Recommendation:** Re-validate the probe result if the execution environment changes.

---

## 7. Complete Change Narrative

A chronological story of the full arc from architecture policy creation through framework changes applied.

### Prologue: The Problem (Pre-Sprint)

SuperClaude's command-skill architecture had grown organically. Slash command files contained both interface metadata (flags, usage) and full behavioral protocols (algorithms, checklists, routing tables). The `task-unified.md` command alone was 567 lines. This caused two problems: (1) every command invocation auto-loaded the entire protocol into Claude's context window, consuming tokens even when the protocol was not needed; and (2) when command summaries diverged from skill specifications, Claude would hallucinate protocol steps rather than failing explicitly.

Additionally, the Skill tool in Claude Code had a re-entry block: if a skill with the same name as the command was already running, invoking it again would fail. This meant command names and skill names needed to be different.

### Act 1: Architecture Policy (2026-02-23)

A policy document was authored: `command-skill-policy.md` (337 lines, v1.0.0). This document established:

- **Three-tier loading model**: Commands (Tier 0, auto-loaded, 150-line cap) are "doors." Protocol Skills (Tier 1, loaded on-demand via Skill tool) are "rooms." Ref files (Tier 2, loaded via `claude -p`) are "drawers."
- **Naming convention**: Skills carry a `-protocol` suffix to avoid the Skill tool re-entry block. Directory names use `sc-{name}-protocol`, frontmatter names use `sc:{name}-protocol`.
- **CI enforcement**: 10 checks under `make lint-architecture` to enforce bidirectional command-skill links, size limits, and naming consistency.
- **4-phase migration**: (1) Rename directories, (2) Refactor commands, (3) Build system updates, (4) Validate.

The policy was placed in two identical locations (`docs/architecture/` and `src/superclaude/`), creating a duplication that remains unresolved.

### Act 2: Design Work -- The Adversarial Pipeline (2026-02-23)

In parallel with the architecture policy, design work proceeded on how to wire the adversarial debate capability (`sc:adversarial`) into the roadmap skill (`sc:roadmap`). The central question: how should a running roadmap session invoke the adversarial pipeline?

Three competing approaches were proposed:
- **Approach 1** (879 lines): Empirical probe-first. 13 test cases, 3 strategies, 3 decision gates.
- **Approach 2** (718 lines): `claude -p` headless CLI as primary invocation. Command templates, parameter mappings.
- **Approach 3** (1121 lines): Hybrid dual-path. Runtime routing between primary and fallback.

These were subjected to a structured adversarial debate (Mode A protocol). Two rounds of advocate arguments and rebuttals produced 12 convergence decisions (C-001 through C-010, U-001, U-002) with perfect convergence (1.00). A hybrid scoring rubric (50% quantitative, 50% qualitative with position-bias mitigation) ranked the approaches: Approach 2 scored 0.900, Approach 3 scored 0.825, Approach 1 scored 0.667.

**Approach 2 was selected as the base**, with targeted absorptions: behavioral adherence testing from Approach 1, enhanced 5-step fallback and `invocation_method` return contract field from Approach 3.

The merged design went through two specification iterations:
- **Spec v1** (653 lines): Addressed 10 reflection-identified issues.
- **Panel review**: 6 experts produced 27 findings (4 CRITICAL, 11 MAJOR). Score: 5.5/10.
- **Spec v2** (872 lines): Addressed all 27 findings. Added 4-state artifact scan, schema ownership model, signal-safe env handling, corrected path references to `-protocol` suffix.

### Act 3: The Probe -- Sprint Variant Selection (Phase 1, 2026-02-23)

The sprint began execution against `tasklist-P6.md` (18 tasks, 6 phases).

**T01.01 (Skill Tool Probe)**: The probe returned `TOOL_NOT_AVAILABLE`. The Skill tool has no callable API -- skills are declarative `.md` files consumed by Claude Code during slash command sessions, not agent-callable endpoints. Pre-execution confidence was 40% (expected for a probe with uncertain outcome). Post-execution confidence: definitive.

**This was the single most consequential decision of the sprint.** It forced the entire sprint to the FALLBACK-ONLY variant. The extensive `claude -p` headless invocation design work (approaches, debate, specifications) became architectural planning for a feature that could not be deployed in the current environment.

**T01.02 (Prerequisites)**: 6/6 checks passed. Three skill files readable, two Make targets available.

**T01.03 (Tier Classification)**: Established that executable `.md` files are NOT exempt from compliance. This affected 9 downstream tasks by preventing them from being auto-classified as EXEMPT despite editing markdown files.

**Phase 1 Checkpoint (CP-P01-END)**: PASS. All 3 tasks complete, no blockers.

### Act 4: Invocation Wiring (Phase 2, 2026-02-23)

With the fallback-only variant selected, Phase 2 wired the fallback invocation protocol into the roadmap skill.

**T02.01**: Added `, Skill` to `roadmap.md`'s `allowed-tools` frontmatter. Verified by grep.

**T02.02**: Added `Skill` to `sc-roadmap-protocol/SKILL.md`'s `allowed-tools`. Verified by grep.

**T02.03 (The Big One)**: STRICT compliance, XL effort, Medium risk. Wave 2 Step 3 was decomposed into 6 sub-steps:
- 3a: Parse agents
- 3b: Expand variants
- 3c: Add orchestrator
- 3d: Execute fallback (F1 variant generation, F2/3 diff+debate, F4/5 selection+merge+contract)
- 3e: Consume return contract (with missing-file guard, YAML error handling, 3-status routing, convergence threshold 0.6)
- 3f: Skip template

An 8-point structural audit verified the implementation. All 8 checks passed.

**Notable design choice**: Step 3e inlines return contract routing directly rather than delegating to the ref section, diverging from Wave 1A's pattern.

**Phase 2 Checkpoint (CP-P02-END)**: PASS. All 3 tasks complete, no blockers.

### Act 5: Architecture Migration (Concurrent with Sprint Execution)

While the sprint executed Phases 1-2 against the tasklist, the architecture policy's migration phases proceeded:

**Migration Phase 1 (Renames -- EXECUTED)**: All 5 skill directories renamed:
- `sc-adversarial` -> `sc-adversarial-protocol`
- `sc-cleanup-audit` -> `sc-cleanup-audit-protocol`
- `sc-roadmap` -> `sc-roadmap-protocol`
- `sc-task-unified` -> `sc-task-unified-protocol`
- `sc-validate-tests` -> `sc-validate-tests-protocol`

30 files affected: 5 SKILL.md files with frontmatter `name` updates, 25 companion files as pure renames. The rename also fixed pre-existing naming inconsistencies (`cleanup-audit` lacked the `sc:` prefix; `task-unified` and `validate-tests` used hyphens instead of colons).

**Migration Phase 2 (Command Refactoring -- IN PROGRESS)**: All 5 command files received a new `## Activation` section with mandatory `Skill sc:{name}-protocol` invocation directive. The most dramatic change was `task-unified.md`: reduced from 567 to 106 lines (81% reduction) as the tier classification engine, compliance checklists, MCP integration matrix, and sub-agent delegation tables were extracted to the skill.

**However**, only `roadmap.md` added `Skill` to its `allowed-tools` frontmatter. The other 4 commands did not. **This is BUG-001.**

**Migration Phase 3 (Build System -- PARTIAL)**: The Makefile received three categories of changes:
1. Removed the skill-skip heuristic from `sync-dev` (4 lines) and `verify-sync` (5 lines)
2. Added `lint-architecture` target (113 lines, 6 checks)
3. Updated `.PHONY` and `help` targets

6 of the policy's 10 CI checks are implemented.

**Migration Phase 4 (Validation -- BLOCKED)**: Blocked on Phase 3 completion.

### Act 6: Dev Copy Sync

`make sync-dev` created 5 new `.claude/skills/sc-*-protocol/` directories (25 files total), byte-identical to their `src/` counterparts minus `__init__.py`. All 5 command pairs verified as byte-identical between `.claude/commands/sc/` and `src/superclaude/commands/`.

### Act 7: Tasklist Housekeeping (Concurrent)

The monolithic tasklist file (`tasklist-P copy 2.md`, with its macOS Finder duplicate filename) was replaced by:
- `tasklist-P6.md` (503 lines): Canonical complete tasklist with all 6 phases
- `tasklist-P5.md` (Phase 5 only + all infrastructure): Focused execution document

Content was byte-for-byte identical to the original; only file organization changed.

### Epilogue: Current State (2026-02-24)

The branch is in an intermediate state:

**Completed:**
- Architecture policy authored and placed (2 copies)
- All 5 skill directories renamed with frontmatter updates
- All 5 command files updated with Activation sections
- task-unified.md reduced from 567 to 106 lines
- Makefile updated (heuristic removal + lint-architecture)
- .claude/ dev copies synced
- Sprint Phases 1-2 executed with all gates passing
- 8 decision artifacts (D-0001 through D-0008) produced
- Full adversarial pipeline (3 approaches, debate, scoring, 2 spec drafts, panel review)

**In Progress:**
- Sprint Phases 3-6 (13 remaining tasks)
- Architecture migration Phases 3-4

**Unresolved Bugs:**
- BUG-001: 4 commands missing `Skill` in `allowed-tools` (HIGH)
- BUG-002/003: Path inconsistencies in tasklist and dev artifacts (MEDIUM)
- BUG-004: Architecture policy duplication without canonical authority (MEDIUM)
- BUG-005: Roadmap SKILL.md stale path reference (MEDIUM)

**Key Metrics:**
- ~68 files affected across the entire change set
- ~246 lines added, ~992 lines removed (net reduction driven by task-unified.md extraction)
- 8 decision artifacts, 6 evidence records, 9 adversarial pipeline outputs, 3 approach documents
- The entire change set is one atomic unit -- partial application breaks the system

---

## Appendix A: Synthesis Document Cross-Reference

Which synthesis documents provide primary coverage for each topic.

| Topic | Dev-Planning-A | Dev-Planning-B | Dev-Artifacts-A | Dev-Artifacts-B | Framework-A | Framework-B |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|
| Architecture policy content | PRIMARY | PRIMARY | context | context | context | context |
| Tasklist structure/evolution | PRIMARY | PRIMARY | -- | -- | -- | -- |
| Checkpoint reports (CP-P01, CP-P02) | PRIMARY | PRIMARY | context | context | -- | -- |
| Decision artifacts (D-0001 to D-0008) | context | context | PRIMARY | PRIMARY | -- | -- |
| Adversarial pipeline (debate, scoring, specs) | -- | -- | PRIMARY | PRIMARY | -- | -- |
| Evidence records | -- | -- | PRIMARY | PRIMARY | -- | -- |
| Approach documents (AP-1, AP-2, AP-3) | -- | -- | PRIMARY | PRIMARY | -- | -- |
| Command file changes | -- | -- | -- | -- | PRIMARY | PRIMARY |
| Skill directory renames | context | context | -- | -- | PRIMARY | PRIMARY |
| Makefile changes | -- | -- | -- | -- | PRIMARY | PRIMARY |
| .claude/ dev copies | -- | -- | -- | -- | PRIMARY | PRIMARY |
| allowed-tools gap (BUG-001) | -- | -- | -- | -- | PRIMARY | PRIMARY |
| Path inconsistency (BUG-002/003) | PRIMARY | PRIMARY | PRIMARY | PRIMARY | -- | context |
| Policy duplication (BUG-004) | PRIMARY | PRIMARY | -- | -- | -- | -- |
| Rollback procedures | PRIMARY | -- | PRIMARY | PRIMARY | PRIMARY | PRIMARY |
| Recreation priority/ordering | PRIMARY | PRIMARY | PRIMARY | PRIMARY | -- | PRIMARY |

## Appendix B: Complete Artifact Inventory

All artifacts produced by this sprint, organized by storage location.

```
.dev/releases/current/v2.01-Roadmap-v3/
|
+-- tasklist/
|   |-- tasklist-P5.md                    (MODIFIED: Phase 5 focused view)
|   |-- tasklist-P6.md                    (NEW: canonical complete tasklist)
|   |-- [tasklist-P copy 2.md]            (DELETED: macOS duplicate)
|   |
|   +-- artifacts/
|   |   |-- approach-1-empirical-probe-first.md     (879 lines)
|   |   |-- approach-2-claude-p-proposal.md         (718 lines)
|   |   |-- approach-3-hybrid-dual-path.md          (1121 lines)
|   |   |-- D-0001/evidence.md                      (Skill probe result)
|   |   |-- D-0002/notes.md                         (Sprint variant decision)
|   |   |-- D-0003/evidence.md                      (Prerequisite checklist)
|   |   |-- D-0004/evidence.md                      (roadmap.md allowed-tools)
|   |   |-- D-0005/evidence.md                      (SKILL.md allowed-tools)
|   |   |-- D-0006/spec.md                          (Wave 2 sub-steps 3a-3f)
|   |   |-- D-0007/spec.md                          (Fallback protocol F1/F2-3/F4-5)
|   |   |-- D-0008/spec.md                          (Return contract routing)
|   |   |-- T01.03/notes.md                         (Tier classification policy)
|   |   +-- adversarial/
|   |       |-- debate-transcript.md                (12 convergence decisions)
|   |       |-- scoring-rubric.md                   (50/50 quant/qual scoring)
|   |       |-- base-selection.md                   (Ap2 selected, score 0.900)
|   |       |-- refactoring-plan.md                 (Absorption + rejection plan)
|   |       |-- merged-approach.md                  (546 lines, unified design)
|   |       |-- specification-draft-v1.md           (653 lines, 10 issues)
|   |       |-- spec-panel-review.md                (27 findings, score 5.5/10)
|   |       +-- specification-draft-v2.md           (872 lines, all resolved)
|   |
|   +-- evidence/
|   |   |-- T01.01/result.md                        (TOOL_NOT_AVAILABLE)
|   |   |-- T01.02/result.md                        (PASS 6/6)
|   |   |-- T01.03/result.md                        (Policy decision)
|   |   |-- T02.01/result.md                        (PASS)
|   |   |-- T02.02/result.md                        (PASS)
|   |   +-- T02.03/result.md                        (PASS 8/8)
|   |
|   +-- checkpoints/
|       |-- CP-P01-END.md                           (Phase 1: PASS)
|       +-- CP-P02-END.md                           (Phase 2: PASS)
|
+-- rollback-analysis/
    +-- synthesis/                                   (6 synthesis files)
    +-- context/
        +-- master-traceability.md                  (THIS FILE)

docs/architecture/
+-- command-skill-policy.md                         (337 lines, policy v1.0.0)

src/superclaude/
+-- ARCHITECTURE.md                                 (337 lines, identical copy)
```

## Appendix C: Abbreviation Key

| Abbreviation | Meaning |
|--------------|---------|
| AP-1/2/3 | Approach documents 1, 2, 3 |
| ADV-1..8 | Adversarial pipeline artifacts 1-8 |
| C-001..C-010 | Convergence decisions from debate |
| U-001, U-002 | Unique compromise decisions from debate |
| D-0001..D-0008 | Decision artifacts (evidence/spec/notes) |
| CP-P01-END | Phase 1 checkpoint report |
| CP-P02-END | Phase 2 checkpoint report |
| R-001..R-022 | Roadmap item registry entries |
| T01.01..T06.05 | Sprint task identifiers (Phase.Task) |
| R081/R099/R100 | Git rename similarity percentages |
