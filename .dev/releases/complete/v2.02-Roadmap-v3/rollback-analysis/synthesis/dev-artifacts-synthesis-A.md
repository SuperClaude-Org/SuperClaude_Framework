# Dev Artifacts Synthesis - Rollback-Recreation Reference

**Date**: 2026-02-24
**Analyst**: claude-opus-4-6
**Source**: 9 batch analysis files covering all dev artifacts from v2.01-Roadmap-v3
**Purpose**: Comprehensive synthesis for rollback-recreation workflow

---

## 1. Executive Summary

The v2.01-Roadmap-v3 dev artifacts document a complete design-through-implementation pipeline for wiring adversarial debate capabilities (`sc:adversarial`) into the roadmap skill (`sc:roadmap`). The central technical question was how to invoke the adversarial pipeline from within a running roadmap session -- three competing approaches were proposed (`claude -p` headless CLI, empirical probe-first, and hybrid dual-path), subjected to a structured adversarial debate, scored by a hybrid quantitative/qualitative methodology, and merged into a unified specification. The entire effort spans 3 approach documents, 8 decision artifacts (D-0001 through D-0008), 1 policy artifact (T01.03), 9 adversarial pipeline outputs, and 6 evidence records.

The adversarial debate process selected Approach 2 (`claude -p` as primary invocation) as the base architecture (score 0.900/1.0), absorbing targeted elements from Approach 1 (behavioral adherence testing, reduced probe scope) and Approach 3 (enhanced 5-step fallback, real convergence tracking, 3-state mid-pipeline awareness, `invocation_method` return contract field). The merged design underwent two specification iterations: v1 addressed 10 reflection-identified issues, then v2 addressed all 27 findings from a 6-expert panel review that scored v1 at 5.5/10. However, the actual viability probe (T01.01) returned TOOL_NOT_AVAILABLE -- `claude -p` was not available in the execution environment -- forcing the entire sprint to the fallback-only variant.

This means the headless invocation design work (approaches, debate, specifications) represents architectural planning for a feature that could not be deployed in the current environment. The fallback protocol (Task-agent based adversarial pipeline with F1-F5 steps) became the sole execution path. The decision artifacts (D-0001 through D-0008) document both the probe outcome and the subsequent fallback-variant implementation: allowed-tools updates, Wave 2 step 3 decomposition into sub-steps 3a-3f, fallback protocol specification, and return contract routing logic.

All artifacts reference skill directories using pre-rename paths (`sc-adversarial/`, `sc-roadmap/`) except specification-draft-v2, which corrects to the `-protocol` suffix. The git status confirms these renames occurred during the sprint. Any rollback-recreation must account for this path change across all artifacts and source files.

---

## 2. Complete Artifact Inventory

### 2.1 Approach Documents

| ID | File | Type | Purpose | Lines | Key Content | Dependencies |
|----|------|------|---------|-------|-------------|--------------|
| AP-1 | `approach-1-empirical-probe-first.md` | Proposal | Risk-de-risking validation plan | 879 | 13 test cases, 3 strategies (S1-S3), 3 decision gates, 7 risks | GitHub #837, #1048; sprint-spec.md |
| AP-2 | `approach-2-claude-p-proposal.md` | Proposal | Full `claude -p` implementation spec | 718 | Command templates, parameter mappings, 14 sprint-spec changes, 6 risks | GitHub #837, #1048; tasklist-P6.md |
| AP-3 | `approach-3-hybrid-dual-path.md` | Proposal | Dual-path architecture with runtime routing | 1121 | Path A/B routing, mid-pipeline fallover, 6 verification specs, 6 risks | GitHub #1048; tasklist-P6.md |

### 2.2 Decision Artifacts (D-series)

| ID | File | Task | Roadmap | Tier | Purpose | Key Content | Depends On |
|----|------|------|---------|------|---------|-------------|------------|
| D-0001 | `D-0001/evidence.md` | T01.01 | R-001 | EXEMPT | Skill tool probe result | TOOL_NOT_AVAILABLE -- Skill tool has no callable API | None (root) |
| D-0002 | `D-0002/notes.md` | T01.01 | R-003 | EXEMPT | Sprint variant decision | FALLBACK-ONLY selected; 3-task modification table | D-0001 |
| D-0003 | `D-0003/evidence.md` | T01.02 | R-002 | EXEMPT | Prerequisite validation | 6/6 checks PASS; file existence + build targets | D-0001, D-0002 |
| D-0004 | `D-0004/evidence.md` | T02.01 | R-004 | LIGHT | Skill in allowed-tools (roadmap.md) | Single-line `, Skill` addition to tools list | D-0003 (gate) |
| D-0005 | `D-0005/evidence.md` | T02.02 | R-005 | LIGHT | Skill in allowed-tools (sc-roadmap SKILL.md) | Same addition, skill-level file | D-0003 (gate) |
| D-0006 | `D-0006/spec.md` | T02.03 | R-006 | STRICT | Wave 2 step 3 sub-steps (3a-3f) | 6 sub-steps: parse, expand, orchestrate, execute fallback, consume contract, skip template | D-0004, D-0005, T01.01 |
| D-0007 | `D-0007/spec.md` | T02.03 | R-007 | STRICT | Fallback protocol (F1, F2/3, F4/5) | 3-stage state machine; return contract with `fallback_mode: true`, `convergence_score: 0.5` | D-0006 |
| D-0008 | `D-0008/spec.md` | T02.03 | R-008 | STRICT | Return contract routing (step 3e) | Missing-file guard, YAML error handling, 3-status routing, convergence threshold 0.6 | D-0007 |

### 2.3 Policy Artifact

| ID | File | Task | Tier | Purpose | Key Content | Impact |
|----|------|------|------|---------|-------------|--------|
| T01.03 | `T01.03/notes.md` | T01.03 | EXEMPT | Tier classification policy | `.md` path booster (+0.5 EXEMPT) does NOT apply to executable spec files | Sets tiers for T02.01-T05.03 |

### 2.4 Adversarial Pipeline Artifacts

| ID | File | Lines | Purpose | Key Content | Depends On |
|----|------|-------|---------|-------------|------------|
| ADV-1 | `adversarial/debate-transcript.md` | ~400 | Deliberative record | 2 rounds + final; 12 convergence decisions (C-001 to C-010, U-001, U-002); convergence 1.00 | AP-1, AP-2, AP-3 |
| ADV-2 | `adversarial/scoring-rubric.md` | ~300 | Hybrid scoring | 50/50 quant/qual; 5 quant metrics + 25 binary criteria; position-bias mitigation | AP-1, AP-2, AP-3 |
| ADV-3 | `adversarial/base-selection.md` | ~100 | Selection decision | Ap2 selected (0.900); absorption plan from Ap1 and Ap3 | ADV-1, ADV-2 |
| ADV-4 | `adversarial/refactoring-plan.md` | 80 | Implementation synthesis | 4 absorptions from Ap1, 5 from Ap3, 5 weakness patches, 10 rejections, 8-item priority | ADV-3 |
| ADV-5 | `adversarial/merged-approach.md` | 546 | Merged debate output | 8 sections; command template; 17-row change matrix; provenance annotations | ADV-1, ADV-3, ADV-4 |
| ADV-6 | `adversarial/specification-draft-v1.md` | 653 | Formal spec v1 | 11 sections + 2 appendices; task ID mapping; addresses 10 reflection issues | ADV-5 |
| ADV-7 | `adversarial/spec-panel-review.md` | 281 | Expert panel review | 6 reviewers, 27 findings (4 CRITICAL, 11 MAJOR); score 5.5/10 | ADV-6 |
| ADV-8 | `adversarial/specification-draft-v2.md` | 872 | Revised spec v2 | Addresses all 27 findings; 4-state scan, schema ownership, signal-safe env handling | ADV-6, ADV-7 |

### 2.5 Evidence Records

| File | Task | Result | Validation | Artifact Ref |
|------|------|--------|------------|--------------|
| `evidence/T01.01/result.md` | T01.01 | TOOL_NOT_AVAILABLE | Manual | D-0001, D-0002 |
| `evidence/T01.02/result.md` | T01.02 | PASS (6/6) | Manual bash checks | D-0003 |
| `evidence/T01.03/result.md` | T01.03 | Policy decision | Manual policy recording | T01.03/notes.md |
| `evidence/T02.01/result.md` | T02.01 | PASS | grep on roadmap.md | D-0004 |
| `evidence/T02.02/result.md` | T02.02 | PASS | grep on SKILL.md | D-0005 |
| `evidence/T02.03/result.md` | T02.03 | PASS (8/8 audit) | Structural audit + adversarial review | D-0006, D-0007, D-0008 |

---

## 3. Decision Pipeline

The full decision flow from proposal to implementation follows this sequence:

```
PHASE 1: APPROACH GENERATION
  AP-1 (Empirical Probe First) ──┐
  AP-2 (claude -p as Primary) ───┼──→ Adversarial Debate
  AP-3 (Hybrid Dual-Path) ───────┘

PHASE 2: ADVERSARIAL EVALUATION
  ADV-1 (debate-transcript.md)
    ├── 2 rounds of advocate arguments + rebuttals
    ├── 12 convergence decisions (C-001..C-010, U-001, U-002)
    └── Final convergence: 1.00
              │
              v
  ADV-2 (scoring-rubric.md)
    ├── Layer 1: Quantitative (50%) → Ap1=0.670, Ap2=0.924, Ap3=0.843
    ├── Layer 2: Qualitative (50%) → 25-criterion binary rubric
    ├── Position-bias mitigation (forward + reverse passes)
    └── Combined: Ap1=0.667, Ap2=0.900, Ap3=0.825
              │
              v
  ADV-3 (base-selection.md)
    └── Approach 2 selected as base; absorption plan defined

PHASE 3: SYNTHESIS & SPECIFICATION
  ADV-4 (refactoring-plan.md)
    ├── 4 absorptions from Ap1, 5 from Ap3
    ├── 5 weakness patches, 10 rejections
    └── 8-item priority order
              │
              v
  ADV-5 (merged-approach.md)
    ├── 8-section design document with provenance annotations
    └── 17-row change matrix
              │
              v
  ADV-6 (specification-draft-v1.md)
    ├── Addresses 10 reflection issues
    └── 11 sections + 2 appendices, 653 lines
              │
              v
  ADV-7 (spec-panel-review.md)
    ├── 6 expert reviewers, 27 findings
    └── Score: 5.5/10
              │
              v
  ADV-8 (specification-draft-v2.md)
    └── Addresses all 27 findings, 872 lines

PHASE 4: PROBE & SPRINT EXECUTION
  T01.01 Probe → TOOL_NOT_AVAILABLE → D-0001
              │
              v
  D-0002 (Sprint Variant Decision) → FALLBACK-ONLY
              │
              v
  D-0003 (Prerequisites) → 6/6 PASS → Gate cleared
              │
              v
  D-0004, D-0005 (allowed-tools) → PASS
              │
              v
  D-0006, D-0007, D-0008 (Wave 2 step 3 implementation) → PASS
```

---

## 4. Evidence Chain

Evidence files serve as lightweight compliance receipts that link task execution to decision artifacts:

```
T01.01 (Skill tool probe)
  evidence/T01.01/result.md  →  D-0001/evidence.md  →  D-0002/notes.md
  Result: TOOL_NOT_AVAILABLE       (probe detail)        (variant decision)

T01.02 (Prerequisite validation)
  evidence/T01.02/result.md  →  D-0003/evidence.md
  Result: PASS (6/6)                (6-point checklist)

T01.03 (Tier classification policy)
  evidence/T01.03/result.md  →  T01.03/notes.md
  Result: Policy decision           (EXEMPT booster exclusion for exec spec files)

T02.01 (Skill in roadmap.md allowed-tools)
  evidence/T02.01/result.md  →  D-0004/evidence.md
  Result: PASS (grep)               (single-line change verification)

T02.02 (Skill in SKILL.md allowed-tools)
  evidence/T02.02/result.md  →  D-0005/evidence.md
  Result: PASS (grep)               (single-line change verification)

T02.03 (Wave 2 step 3 decomposition)
  evidence/T02.03/result.md  →  D-0006/spec.md + D-0007/spec.md + D-0008/spec.md
  Result: PASS (8/8 audit)          (sub-steps + fallback protocol + contract routing)
```

### Evidence Structure Pattern

All evidence files follow a two-tier structure:
- **Tier 1 (result.md)**: 5-6 lines; result, validation method, artifact pointer
- **Tier 2 (artifact)**: Full detailed evidence with specifications, checklists, or policy rationale

### Key Evidence Chain Dependencies

The foundational chain is: **T01.01 → D-0001 → D-0002 → all Phase 2-4 tasks**. If T01.01's TOOL_NOT_AVAILABLE result were different, the entire sprint variant would change. D-0003 acts as a go/no-go gate requiring both D-0001 and D-0002 to exist before Phase 2+ can proceed.

---

## 5. Adversarial Pipeline

### 5.1 Pipeline Stages

The adversarial pipeline followed the sc:adversarial Mode A protocol with these stages:

| Stage | Artifact | Input | Output | Quality Gate |
|-------|----------|-------|--------|--------------|
| **Debate** | debate-transcript.md | 3 approach documents | 12 convergence decisions | Convergence >= 0.80 (achieved 1.00) |
| **Scoring** | scoring-rubric.md | 3 approach documents | Combined scores per approach | Position-bias delta < 5% |
| **Selection** | base-selection.md | Debate + scores | Base approach + absorption plan | Gap between top-2 > 5% (achieved 7.5%) |
| **Synthesis** | refactoring-plan.md | Selection + approaches | Priority-ordered implementation plan | All absorptions justified |
| **Merge** | merged-approach.md | Refactoring plan + approaches | Unified design with provenance | Section provenance annotations |
| **Specification** | specification-draft-v1.md | Merged approach | Formal spec (v1) | 10 reflection issues addressed |
| **Review** | spec-panel-review.md | Spec v1 | 27 findings, 4 CRITICAL | Score reported (5.5/10) |
| **Revision** | specification-draft-v2.md | Spec v1 + review findings | Revised spec (v2) | All 27 findings addressed |

### 5.2 Debate Convergence Decisions

The debate produced 12 decisions that shaped the final architecture:

| ID | Decision | Source |
|----|----------|--------|
| C-001 | Extend Task 0.0 with behavioral adherence rubric from Ap1 T05 | Ap1 absorption |
| C-002 | Upgrade fallback from 3-step to 5-step (F1-F5) with real convergence | Ap3 absorption |
| C-003 | Use primary/fallback architecture, not dual-path peer | Ap2 base |
| C-004 | Drop `--invocation-mode` flag (YAGNI) | Ap3 rejection |
| C-005 | Drop depth-based routing (premature optimization) | Ap3 rejection |
| C-006 | Add `invocation_method` field to return contract | Ap3 absorption |
| C-007 | Adopt CLAUDECODE environment variable handling pattern | Ap2 base |
| C-008 | Reduce 13-test probe to 4 essential tests in Task 0.0 | Ap1 reduction |
| C-009 | Drop 10-run reliability test (YAGNI for sprint scope) | Ap1 rejection |
| C-010 | Use Ap2's 14-row sprint-spec modification table | Ap2 base |
| U-001 | 3-state mid-pipeline fallover (no artifacts / variants / diff-analysis) | Compromise |
| U-002 | 4-test probe: 3 mechanical + 1 behavioral adherence (~20min, ~$4) | Compromise |

### 5.3 Expert Panel Review Summary

The 6-expert panel (Wiegers, Fowler, Nygard, Adzic, Crispin, Newman) produced 27 findings:

| Severity | Count | Key Issues |
|----------|-------|------------|
| CRITICAL | 4 | Return contract field count mismatch (W1/F1/S1); heading mapping inaccurate (A1); no SKILL.md content validation/ARG_MAX (N1); no mid-pipeline recovery tests (C1) |
| MAJOR | 11 | `unresolved_conflicts` type (int vs list[string]); schema in 3 places; fallback directory mismatch; 3-state model incomplete; no budget ceiling; non-executable rubric; threshold gap |
| MINOR | 6 | Stderr discarded; cost arithmetic error; compound `invocation_method`; CLAUDECODE restore not signal-safe; grep pattern misalignment; no logging test |
| SUGGESTION | 6 | Probe idempotency; configurable cost guard; fixture content; budget exceeded test; schema validation |

---

## 6. Specification Evolution

### 6.1 Lineage

```
merged-approach.md (convergence 1.00, 546 lines)
    │
    ├── [Reflection review: 5 critical + 5 important issues]
    │
    v
specification-draft-v1.md (653 lines, resolves 10 issues)
    │
    ├── [Expert panel: 27 findings, score 5.5/10]
    │
    v
specification-draft-v2.md (872 lines, resolves all 27 findings)
```

### 6.2 Key Evolution Table

| Aspect | merged-approach | spec-v1 | spec-v2 |
|--------|----------------|---------|---------|
| SKILL.md path | `sc-adversarial/` (old) | `sc-adversarial/` (old) | `sc-adversarial-protocol/` (corrected) |
| Artifact scan states | 3 (A/B/C) | 3 (A/B/C) | 4 (A/B/C/D) |
| `unresolved_conflicts` type | integer | integer | `list[string]` |
| `invocation_method` values | headless, task_agent, headless+task_agent | headless, task_agent, headless+task_agent | headless, task_agent (simple enum only) |
| Schema ownership model | Not addressed | Not addressed | Producer/consumer with dual-format handling |
| SKILL.md content validation | None | None | Empty check + ARG_MAX warning at 1.5MB |
| Stderr handling | Discarded (`2>/dev/null`) | Discarded (`2>/dev/null`) | Captured to temp file |
| CLAUDECODE env restore | Basic if/then | Basic if/then | `trap EXIT` signal-safe |
| Budget ceiling | Per-invocation only | Per-invocation only | Total adversarial = 2x BUDGET |
| Fallback behavioral threshold | 10/20 (50%) | 14/20 (70%) headless only | 14/20 headless, 12/20 (60%) fallback with rationale |
| T03.01 validation checks | Not addressed | 4-point | 5-point (added SKILL.md path verification) |
| T03.02 audit checks | Not addressed | 8-point | 9-point (added dual-format + dir normalization) |
| Risk count | 7 (R1-R7) | 7 (R1-R7) | 9 (R1-R9, added SKILL.md read failure + cost doubling) |
| Verification sections | 5 | 5 | 9 (added mid-pipeline, schema transition, budget, invocation logging) |
| Prompt construction | Enumerates all 10 contract fields | Enumerates all 10 contract fields | References "your FR-007 section" (decoupled) |
| Schema evolution policy | None | None | Minor/major versioning with consumer behavior rules |
| Probe cost estimate | ~$4 | ~$4 | <= $2.15 (corrected arithmetic) |
| Instruction heading mapping | By section heading (generic) | Paraphrased headings | Exact SKILL.md headings with line numbers + matching algorithm |

---

## 7. Technical Decisions

### 7.1 Foundational Decisions

| Decision | Rationale | Impact | Reversibility |
|----------|-----------|--------|---------------|
| **TOOL_NOT_AVAILABLE** (D-0001) | Skill tool has no callable API; skills are declarative .md files, not agent endpoints | Forces fallback-only sprint variant for all subsequent phases | Irreversible (environment fact) |
| **FALLBACK-ONLY variant** (D-0002) | Deterministic given D-0001 probe result | 3 tasks modified; fallback protocol is sole invocation mechanism | Reversible if Skill tool API becomes available |
| **EXEMPT booster exclusion** (T01.03) | Executable spec files (.md) function as code, not documentation | Sets T02.03, T04.01, T04.02 as STRICT; prevents under-verification | Policy decision; reversible by future sprint |

### 7.2 Architectural Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| `claude -p` as primary, Task-agent as fallback | Simplest viable architecture; Ap2 scored 0.900 vs Ap3's 0.825 | ADV-3 (base-selection) |
| Enhanced 5-step fallback (F1-F5) | Ap3's upgrade from compressed 3-step improves quality floor | C-002 (debate) |
| 3-state mid-pipeline awareness | Compromise: simpler than Ap3's 5-state, more robust than Ap2's 2-state | U-001 (debate) |
| Return contract as abstraction boundary | Consumers ignorant of invocation method; enables future path addition | All approaches agreed |
| `invocation_method` field (observability only) | Logging/debugging value without consumer branching | C-006 (debate) |
| Drop `--invocation-mode` flag | YAGNI; user-facing flag for internal routing not justified | C-004 (debate) |
| Drop depth-based routing | Premature optimization; insufficient evidence for depth-specific routing | C-005 (debate) |

### 7.3 Schema Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| `unresolved_conflicts`: integer → `list[string]` | Integer loses conflict detail; list preserves actionable information | ADV-7 panel review |
| `invocation_method`: drop compound value | `headless+task_agent` leaks execution history across abstraction boundary | ADV-7 panel review |
| Schema ownership model (producer/consumer) | Prevents spec from requiring producer changes out of scope | ADV-8 spec-v2 |
| Convergence threshold: 0.6 | Below this, partial results are insufficiently reliable for downstream use | D-0008 |
| Fallback convergence sentinel: 0.5 | Deliberately below 0.6 threshold; forces partial/low-convergence path | D-0007 |

### 7.4 Implementation Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| Wave 2 step 3 decomposed into 3a-3f | Atomic sub-steps enable individual verification and fallback targeting | D-0006 |
| `Skill` added to allowed-tools in both command and skill files | Dual-layer enforcement requires both; future-compatible if Skill API emerges | D-0004, D-0005 |
| Fallback protocol: 3-stage state machine (F1, F2/3, F4/5) | Balanced granularity; merged stages reduce Task agent dispatch overhead | D-0007 |
| Signal-safe CLAUDECODE restore (`trap EXIT`) | Basic if/then can leak env var on unexpected termination | ADV-8 spec-v2 |
| SKILL.md content validation before injection | Empty file or ARG_MAX overflow would cause silent failure | ADV-8 spec-v2 |

---

## 8. Rollback Impact Assessment

### 8.1 Critical (Cannot Reconstruct Without Source Material)

| Artifact | Why Critical | Recreation Difficulty |
|----------|-------------|----------------------|
| **T01.01 evidence** (D-0001) | Records point-in-time environment state; outcome would differ if `claude -p` becomes available | Cannot reproduce same result in changed environment |
| **Debate transcript** (ADV-1) | Specific advocate arguments, concessions, and convergence narrative | Reproducible in structure but not in exact content; debate is stochastic |
| **Expert panel review** (ADV-7) | 27 specific findings with line-number references to v1 spec | Line numbers become invalid if source files change |
| **Git status snapshot** (in D-0003) | Records pre-rename directory state at 2026-02-23 | Historical state; directories have since been renamed |

### 8.2 Reconstructable (Can Be Re-derived from Preserved Inputs)

| Artifact | Reconstruction Source | Confidence |
|----------|----------------------|------------|
| **D-0002** (sprint variant) | Deterministic from D-0001 probe result | 100% -- same input always yields FALLBACK-ONLY |
| **D-0003** (prerequisites) | Re-run file existence checks + Makefile target verification | 95% -- depends on current filesystem state |
| **D-0004, D-0005** (allowed-tools) | Single-line additions; trivially re-applied | 100% |
| **D-0006** (sub-steps 3a-3f) | Re-derivable from D-0007/D-0008 specs + fallback variant decision | 90% |
| **D-0007, D-0008** (fallback + routing) | Re-derivable from specification-draft-v2 sections 3.3 and 3.5 | 85% |
| **Scoring rubric** (ADV-2) | Re-runnable against approach documents with defined methodology | 80% -- scores may vary slightly |
| **Base selection** (ADV-3) | Deterministic from scoring output | 95% |
| **Refactoring plan** (ADV-4) | Re-derivable from base selection + approach documents | 85% |
| **Merged approach** (ADV-5) | Re-derivable from refactoring plan + approach documents | 80% |
| **Spec v1** (ADV-6) | Re-derivable from merged approach + reflection issues | 75% |
| **Spec v2** (ADV-8) | Re-derivable from spec v1 + panel review findings | 80% |
| **Evidence records** (T01.02-T02.03) | Re-runnable validation checks against current filesystem | 90% |

### 8.3 Rollback Action Summary

| Scope | Action | Risk | Dependencies |
|-------|--------|------|--------------|
| **Full rollback** | Revert all source file changes; remove artifact/evidence directories | Low | Requires git restore to pre-sprint state |
| **D-0004/D-0005 only** | Remove `, Skill` from allowed-tools in roadmap.md and SKILL.md | Low | Safe if D-0006 also rolled back |
| **D-0006 only** | Remove 3a-3f sub-step decomposition; restore monolithic step 3 | Medium | D-0007/D-0008 become orphaned specs |
| **D-0007/D-0008 only** | Remove fallback protocol spec and routing spec | Medium | D-0006 step 3d loses its specification |
| **Adversarial artifacts only** | Remove `artifacts/adversarial/` directory | Low | Design artifacts only; no source code impact |
| **Evidence only** | Remove `evidence/` directory | Low | Compliance records only; no functional impact |

### 8.4 Path Rename Consideration

All pre-rename references in artifacts use:
- `src/superclaude/skills/sc-adversarial/SKILL.md`
- `src/superclaude/skills/sc-roadmap/SKILL.md`

Post-rename paths (current) are:
- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Only `specification-draft-v2.md` uses the corrected `-protocol` paths. A rollback-recreation must either:
1. Update all artifact references to `-protocol` paths, or
2. Ensure the rollback also reverts the directory rename

### 8.5 Key Preservation Priority

For rollback-recreation, preserve in this priority order:

1. **specification-draft-v2.md** -- Most mature design document; contains all decisions and addresses all review findings
2. **Three approach documents** (AP-1, AP-2, AP-3) -- Source material for the entire pipeline; enables full re-derivation
3. **D-0001 + D-0002** -- Foundational probe result and variant decision; determines sprint trajectory
4. **spec-panel-review.md** -- 27 specific, actionable findings that drove v1→v2 evolution
5. **debate-transcript.md** -- Convergence decisions that shaped the merged architecture
6. **T01.03 policy** -- Tier classification ruling that affects all future sprints
7. **D-0006, D-0007, D-0008** -- Implementation specifications for the fallback path
8. **Everything else** -- Evidence records, scoring rubric, base selection, refactoring plan (all reconstructable)

---

## Appendix A: Artifact File Paths

All paths relative to `.dev/releases/current/v2.01-Roadmap-v3/tasklist/`:

```
artifacts/
├── approach-1-empirical-probe-first.md
├── approach-2-claude-p-proposal.md
├── approach-3-hybrid-dual-path.md
├── D-0001/evidence.md
├── D-0002/notes.md
├── D-0003/evidence.md
├── D-0004/evidence.md
├── D-0005/evidence.md
├── D-0006/spec.md
├── D-0007/spec.md
├── D-0008/spec.md
├── T01.03/notes.md
└── adversarial/
    ├── base-selection.md
    ├── scoring-rubric.md
    ├── debate-transcript.md
    ├── refactoring-plan.md
    ├── merged-approach.md
    ├── specification-draft-v1.md
    ├── spec-panel-review.md
    └── specification-draft-v2.md

evidence/
├── T01.01/result.md
├── T01.02/result.md
├── T01.03/result.md
├── T02.01/result.md
├── T02.02/result.md
└── T02.03/result.md
```

## Appendix B: Dependency Graph

```
                    ┌─────────────────────────────────────────────┐
                    │         APPROACH DOCUMENTS (AP-1,2,3)       │
                    └──────────────┬──────────────────────────────┘
                                   │
                    ┌──────────────v──────────────────────────────┐
                    │     ADVERSARIAL DEBATE (ADV-1)              │
                    │     12 convergence decisions                │
                    └──────────────┬──────────────────────────────┘
                                   │
                    ┌──────────────v──────────────┐
                    │  SCORING (ADV-2) ──→ SELECTION (ADV-3)     │
                    └──────────────┬──────────────────────────────┘
                                   │
                    ┌──────────────v──────────────────────────────┐
                    │  REFACTORING PLAN (ADV-4) ──→ MERGE (ADV-5)│
                    └──────────────┬──────────────────────────────┘
                                   │
                    ┌──────────────v──────────────────────────────┐
                    │  SPEC v1 (ADV-6) ──→ REVIEW (ADV-7) ──→   │
                    │  SPEC v2 (ADV-8)                           │
                    └────────────────────────────────────────────-┘

     ┌────────────┐
     │ T01.01     │ ──→ D-0001 (TOOL_NOT_AVAILABLE)
     │ Probe      │       │
     └────────────┘       ├──→ D-0002 (FALLBACK-ONLY)
                          │       │
     ┌────────────┐       │       v
     │ T01.02     │ ──→ D-0003 (6/6 prerequisites) ──→ GATE: Phase 2+
     │ Prereqs    │
     └────────────┘

     ┌────────────┐
     │ T01.03     │ ──→ Tier policy (EXEMPT booster exclusion)
     │ Policy     │       │
     └────────────┘       └──→ Tier assignments for T02.01-T05.03

     ┌────────────┐     ┌────────────┐
     │ T02.01     │     │ T02.02     │
     │ D-0004     │     │ D-0005     │
     │ roadmap.md │     │ SKILL.md   │
     └─────┬──────┘     └─────┬──────┘
           │                  │
           └────────┬─────────┘
                    v
     ┌──────────────────────────────────────┐
     │ T02.03                               │
     │ D-0006 (sub-steps 3a-3f)            │
     │ D-0007 (fallback F1, F2/3, F4/5)   │
     │ D-0008 (return contract routing)     │
     └──────────────────────────────────────┘
```
