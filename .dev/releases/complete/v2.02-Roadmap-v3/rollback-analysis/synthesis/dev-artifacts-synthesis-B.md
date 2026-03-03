# Dev Artifacts Synthesis (Agent B)

**Date**: 2026-02-24
**Analyst**: claude-opus-4-6 (Agent B -- independent analysis)
**Source**: 9 batch analysis files covering 25+ individual artifacts
**Purpose**: Comprehensive synthesis for rollback-recreation workflow

---

## 1. Executive Summary

The dev artifact corpus documents a complete **design-decision-implementation pipeline** for wiring adversarial debate capabilities into the `sc:roadmap` skill via `claude -p` headless CLI invocation. The artifacts span six categories:

1. **Design Approaches** (3 competing proposals for headless invocation architecture)
2. **Adversarial Debate Outputs** (scoring, debate transcript, base selection, merged approach)
3. **Specification Evolution** (merged-approach -> spec-v1 -> spec-v2, with panel review)
4. **Decision Records** (D-0001 through D-0008, tracking probe results, sprint variant selection, allowed-tools changes, protocol specs)
5. **Policy Artifacts** (T01.03 tier classification ruling)
6. **Evidence Records** (T01.01 through T02.03 result files)

The central narrative: Three approaches were proposed for integrating `claude -p` headless invocation. An adversarial debate selected Approach 2 as the base with selective absorptions from Approaches 1 and 3. The resulting specification went through two draft revisions informed by reflection review and expert panel critique. However, the actual runtime probe (T01.01) returned `TOOL_NOT_AVAILABLE`, forcing the entire sprint to the **fallback-only** variant. All subsequent implementation tasks (Phase 2-4) executed under fallback-only constraints.

**Key tension**: Extensive design work was performed for a headless invocation path that the environment cannot currently support. The fallback-only path is the only one exercised. The design artifacts preserve the architectural intent for when `claude -p` becomes available.

---

## 2. Artifact Dependency Graph

```
                    APPROACH DOCUMENTS (Design Layer)
                    ================================
    approach-1-empirical-probe-first.md
    approach-2-claude-p-proposal.md
    approach-3-hybrid-dual-path.md
                |           |           |
                +-----+-----+-----+-----+
                      |
                      v
              ADVERSARIAL PIPELINE (Evaluation Layer)
              ======================================
              debate-transcript.md
                      |
                      v
              scoring-rubric.md
                      |
                      v
              base-selection.md -----> refactoring-plan.md
                                              |
                                              v
                                    merged-approach.md (design output)
                                              |
                      +-----------------------+
                      |                       |
                      v                       v
              specification-draft-v1.md   spec-panel-review.md (27 findings)
                      |                       |
                      +-----------+-----------+
                                  |
                                  v
                        specification-draft-v2.md (final spec)


                    DECISION RECORDS (Execution Layer)
                    ==================================

    D-0001 (Skill Tool Probe: TOOL_NOT_AVAILABLE)
      |
      +---> D-0002 (Sprint Variant: FALLBACK-ONLY)
      |       |
      |       +---> D-0004 (Skill in allowed-tools: roadmap.md)
      |       |       |
      |       +---> D-0005 (Skill in allowed-tools: sc-roadmap SKILL.md)
      |       |       |
      |       +---> D-0006 (Wave 2 Step 3 sub-steps 3a-3f)
      |       |       |
      |       +---> D-0007 (Fallback Protocol F1/F2-3/F4-5)
      |       |       |
      |       +---> D-0008 (Return Contract Routing in 3e)
      |       |
      |       +---> T01.03 (Tier Classification Policy)
      |
      +---> D-0003 (Prerequisite Checklist, depends on D-0001 + D-0002)


                    EVIDENCE RECORDS (Verification Layer)
                    ====================================

    T01.01/result.md --> D-0001, D-0002
    T01.02/result.md --> D-0003
    T01.03/result.md --> T01.03/notes.md (policy artifact)
    T02.01/result.md --> D-0004
    T02.02/result.md --> D-0005
    T02.03/result.md --> D-0006, D-0007, D-0008
```

### Critical Path

```
D-0001 (probe) --> D-0002 (variant selection) --> D-0003 (prerequisite gate) --> Phase 2+ execution
```

Every implementation artifact depends transitively on D-0001's `TOOL_NOT_AVAILABLE` result. This is the single root dependency.

---

## 3. Quality Assessment

### Completeness: 8/10

**Strengths:**
- Full traceability from design through decision through implementation evidence
- Each decision artifact links to its parent task, roadmap item, and downstream consumers
- The adversarial pipeline produced a complete evaluation chain (debate -> scoring -> selection -> merge -> spec-v1 -> review -> spec-v2)
- Evidence records provide two-tier structure (summary result -> detailed artifact)

**Gaps:**
- No evidence records exist for tasks beyond T02.03 (Phases 3-4 appear unexecuted or unrecorded)
- Probe fixtures referenced in approach documents (`spec-minimal.md`, `variant-a.md`, `variant-b.md`, `expected-schema.yaml`) were never created
- The `refs/headless-invocation.md` infrastructure file was never created
- D-0009 and D-0010 are referenced in spec-v2's deliverable registry but no corresponding artifacts exist in the analyzed set

### Consistency: 6/10

**Consistent elements:**
- All artifacts share the same date (2026-02-23), confirming single-session production
- GitHub issues #837, #1048 referenced consistently across all approach and adversarial documents
- Fallback-only variant selection is consistently applied from D-0002 onward
- Return contract schema fields are eventually reconciled in spec-v2

**Inconsistencies found:**
- **Path naming**: Pre-rename paths (`sc-adversarial/`, `sc-roadmap/`) used in D-0001 through D-0008, approach documents, merged-approach, and spec-v1. Only spec-v2 corrects to `-protocol` suffix.
- **Return contract field count**: merged-approach claims "9+1=10 fields" but SKILL.md FR-007 defines only 5 fields. Panel review flagged this as CRITICAL (W1/F1/S1).
- **`unresolved_conflicts` type**: Integer in merged-approach and spec-v1; corrected to `list[string]` in spec-v2.
- **`invocation_method` compound values**: `headless+task_agent` allowed in merged-approach and spec-v1; restricted to simple enum in spec-v2.
- **Convergence sentinel**: 0.5 in D-0007 fallback, but convergence threshold is 0.6 in D-0008. This is by design (fallback results always trigger partial/low-convergence path) but is a subtle interaction.
- **Fallback behavioral threshold**: 50% in merged-approach, inconsistently 70% in spec-v1, finally reconciled to 14/20 headless + 12/20 fallback in spec-v2.
- **Artifact scan states**: 3-state in merged-approach through spec-v1; 4-state in spec-v2.

### Internal Coherence: 7/10

The artifacts tell a coherent story but with redundancy. The refactoring-plan.md, merged-approach.md, and base-selection.md all overlap significantly in recording the "what was selected and why" narrative. The three-file adversarial output structure (debate -> scoring -> selection) is clean, but the refactoring plan is largely redundant with the merged approach.

---

## 4. Gap Analysis

### Missing Artifacts

| Expected Artifact | Referenced By | Status |
|---|---|---|
| `refs/headless-invocation.md` | Approach 2, merged-approach, spec-v1, spec-v2 | Never created |
| Probe fixtures (`spec-minimal.md`, `variant-a.md`, `variant-b.md`) | Approach 1, spec-v2 | Never created |
| `expected-schema.yaml` / `return-contract.yaml` schema file | Approach 1 (Appendix B) | Never created |
| D-0009, D-0010 artifacts | spec-v2 deliverable registry | Not found |
| Phase 3 evidence (T03.01, T03.02) | Tasklist structure implies these | Not found |
| Phase 4 evidence (T04.01, T04.02, T04.03) | Tasklist structure implies these | Not found |
| Phase 5 evidence (T05.01, T05.02, T05.03) | Tasklist structure implies these | Not found |

### Broken References

| Reference | In File | Issue |
|---|---|---|
| `TASKLIST_ROOT/tasklist/evidence/T01.01/` | D-0001, D-0003 | Uses `TASKLIST_ROOT` variable; resolves correctly if understood as relative |
| `../../../artifacts/D-0001/evidence.md` | T01.01/result.md | Relative path; valid within directory structure |
| `tasklist-P6.md` | Approach 2, Approach 3 | Referenced as the "phase 6 tasklist" but relationship to actual tasklist files unclear |
| `sc-adversarial/SKILL.md` line numbers | spec-panel-review.md | Line numbers are point-in-time; post-rename the file has likely changed |
| `sprint-spec.md` | Approach 1 | Referenced but never appears in the artifact set |

### Structural Gaps

1. **No checkpoint artifacts**: The tasklist references a `checkpoints/` directory but no checkpoint files were analyzed.
2. **No tasklist-P6.md analysis**: Multiple artifacts reference this file but it was not included in the batch analysis scope.
3. **No `command-skill-policy.md` analysis**: D-0004 references this policy document but it was not analyzed.
4. **No adversarial SKILL.md content analysis**: The panel review references specific line numbers (FR-007 at lines 339-350, implementation at 411-1589) but the SKILL.md itself was not part of the analysis.

---

## 5. Path Evolution Tracking

### Rename Event

Git status shows these renames occurred during the sprint:
- `sc-adversarial/` -> `sc-adversarial-protocol/`
- `sc-roadmap/` -> `sc-roadmap-protocol/`
- `sc-cleanup-audit/` -> `sc-cleanup-audit-protocol/`
- `sc-task-unified/` -> `sc-task-unified-protocol/`
- `sc-validate-tests/` -> `sc-validate-tests-protocol/`

### Per-Artifact Path Reference State

| Artifact | Path Convention | Notes |
|---|---|---|
| approach-1-empirical-probe-first.md | PRE-RENAME (`sc-adversarial/`, `sc-roadmap/`) | |
| approach-2-claude-p-proposal.md | PRE-RENAME | |
| approach-3-hybrid-dual-path.md | PRE-RENAME | References specific SKILL.md line numbers |
| D-0001 through D-0008 | PRE-RENAME | All evidence/artifact references use old paths |
| T01.03/notes.md | PRE-RENAME | Lists affected files with old paths |
| merged-approach.md | PRE-RENAME | Explicitly noted in batch 6 analysis |
| refactoring-plan.md | PRE-RENAME (implied) | References `sc:adversarial SKILL.md` generically |
| specification-draft-v1.md | PRE-RENAME | Noted as "retained issue" |
| **specification-draft-v2.md** | **POST-RENAME** (`sc-adversarial-protocol/`) | Only artifact to use corrected paths |
| spec-panel-review.md | PRE-RENAME | Line number references to old file locations |
| debate-transcript.md | PRE-RENAME (implied) | References approach documents |
| scoring-rubric.md | PRE-RENAME (implied) | References approach documents |
| base-selection.md | PRE-RENAME (implied) | References approach documents |
| All evidence/T*/result.md | PRE-RENAME | Grep validations ran against old paths |

**Summary**: 24 of 25 artifacts use pre-rename paths. Only `specification-draft-v2.md` uses the corrected `-protocol` suffix. This means any recreation that runs after the rename must update path references in all recreated artifacts, or the artifacts will contain stale paths.

---

## 6. Recreation Difficulty Rating

| Category | Artifacts | Difficulty | Rationale |
|---|---|---|---|
| **Approach Documents** | approach-1, approach-2, approach-3 | HARD | 879+718+1121 lines of original design work. These are creative artifacts capturing architectural reasoning. Cannot be mechanically regenerated; would require re-running the entire design process. |
| **Adversarial Debate Outputs** | debate-transcript, scoring-rubric, base-selection | HARD | Products of a multi-round adversarial debate with specific convergence decisions (C-001 through C-010, U-001, U-002). The debate transcript records emergent reasoning that cannot be deterministically reproduced. |
| **Merged Approach** | merged-approach.md | MEDIUM | Synthesized from the three approaches + debate outcomes. Recreatable if approach docs and debate outputs survive, but provenance annotations would be lost. |
| **Refactoring Plan** | refactoring-plan.md | MEDIUM | Synthesized from the merged approach. Recreatable from merged-approach.md. |
| **Specification Drafts** | spec-v1, spec-v2 | MEDIUM-HARD | v1 is derivable from merged-approach + reflection review. v2 requires the panel review findings. The exact section structure, task ID mappings, and line-number references are fragile. |
| **Panel Review** | spec-panel-review.md | MEDIUM | Structured critique with 6 expert personas. Recreatable if spec-v1 and the SKILL.md files survive, but specific finding numbers and cross-references would change. |
| **Decision Records (D-0001 to D-0003)** | Probe + Variant + Prereqs | EASY | Deterministic outcomes. D-0001 will always return TOOL_NOT_AVAILABLE (Skill tool has no API). D-0002 is a mechanical consequence. D-0003 is a file-existence check. |
| **Decision Records (D-0004, D-0005)** | Allowed-tools changes | EASY | Single-line additions. Trivially recreatable from the policy. |
| **Decision Records (D-0006 to D-0008)** | Protocol specs | MEDIUM | Structural specifications derived from the merged approach. Recreatable if the merged approach survives. |
| **Policy Artifact (T01.03)** | Tier classification ruling | EASY | Policy decision with clear rationale. Recreatable from the tier classification algorithm + the observation that SKILL.md files are executable. |
| **Evidence Records** | T01.01 through T02.03 | EASY | Minimal result files (5-6 lines each) that are byproducts of task execution. Auto-generated during recreation. |

### Summary Difficulty Distribution

- **EASY**: 10 artifacts (decision records D-0001 to D-0005, policy T01.03, all evidence files)
- **MEDIUM**: 4 artifacts (merged-approach, refactoring-plan, D-0006 to D-0008)
- **MEDIUM-HARD**: 3 artifacts (spec-v1, spec-v2, panel review)
- **HARD**: 6 artifacts (3 approach documents, 3 adversarial debate outputs)

---

## 7. Critical Information Extraction

These facts and decisions MUST survive rollback regardless of artifact recreation:

### Architectural Decisions

1. **Skill tool has no callable API** (D-0001). Skills are declarative `.md` files consumed by Claude Code during slash command sessions, not agent-callable endpoints. This is an environment fact, not a design choice.

2. **Fallback-only sprint variant** (D-0002). All task modifications follow from this: T02.03 omits primary Skill tool step, T04.01 writes contract as part of fallback, Phase 3 validates fallback structure.

3. **Approach 2 selected as base** (base-selection.md). Score 0.900 vs Approach 3's 0.825 and Approach 1's 0.667. Primary/fallback hierarchy, not dual-path peer architecture.

4. **12 convergence decisions** from adversarial debate (debate-transcript.md):
   - C-001: Behavioral adherence rubric in Task 0.0
   - C-002: 5-step fallback with real convergence
   - C-003: Primary/fallback architecture (not dual-path)
   - C-004: No `--invocation-mode` flag
   - C-005: No depth-based routing
   - C-006: `invocation_method` field in return contract
   - C-007: CLAUDECODE env variable handling
   - C-008: 4-test probe (not 13)
   - C-009: No 10-run reliability test
   - C-010: Approach 2's sprint-spec modification table
   - U-001: 3-state mid-pipeline fallover
   - U-002: 4-test probe scope (~20min, ~$4)

5. **Executable spec files are NOT EXEMPT** (T01.03). SKILL.md, command .md, and ref .md files are classified as code for compliance tier purposes.

### Schema Decisions (spec-v2 final state)

6. Return contract: 10 fields (5 producer + 2 consumer-existing + 3 new). `schema_version: "1.0"`.
7. `unresolved_conflicts`: type `list[string]` (not integer).
8. `invocation_method`: simple enum (`headless`, `task_agent`), no compound values.
9. 4-state artifact scan model (States A/B/C/D).
10. Schema ownership: producer/consumer model with dual-format handling.

### Implementation Specifications

11. Fallback protocol: 3 stages (F1 variant generation, F2/3 diff+debate, F4/5 selection+merge+contract).
12. Convergence threshold: 0.6 (D-0008). Fallback convergence sentinel: 0.5 (D-0007). This means fallback results always trigger the partial/low-convergence routing path.
13. Wave 2 step 3 decomposition: 6 sub-steps (3a parse agents, 3b expand variants, 3c add orchestrator, 3d execute fallback, 3e consume contract, 3f skip template).
14. `Skill` added to allowed-tools in both `roadmap.md` and `sc-roadmap SKILL.md`.

### Quality Metrics

15. Specification-draft-v2 is the authoritative spec (panel score 5.5/10 for v1; v2 addresses all 27 findings).
16. 4 CRITICAL panel findings resolved: contract field ownership, heading mapping, SKILL.md content validation, mid-pipeline recovery tests.

---

## 8. Recommended Recreation Order

Recreation should follow the dependency graph, starting from the root and proceeding level by level. Items at the same level can be parallelized.

### Phase 0: Environment Validation (Parallelize)
```
[1] D-0001: Skill Tool Probe          (deterministic, ~2 min)
[2] Path rename verification           (confirm -protocol suffix state)
```

### Phase 1: Foundation Decisions (Sequential from D-0001)
```
[3] D-0002: Sprint Variant Selection   (mechanical consequence of D-0001)
[4] D-0003: Prerequisite Checklist     (depends on D-0001 + D-0002)
[5] T01.03: Tier Classification Policy (independent of D-0001 chain, parallelize with [3])
```

### Phase 2: Design Artifacts -- PRESERVE, DO NOT RECREATE
```
[6] approach-1-empirical-probe-first.md   (HARD -- preserve original)
[7] approach-2-claude-p-proposal.md       (HARD -- preserve original)
[8] approach-3-hybrid-dual-path.md        (HARD -- preserve original)
[9] debate-transcript.md                  (HARD -- preserve original)
[10] scoring-rubric.md                    (HARD -- preserve original)
[11] base-selection.md                    (HARD -- preserve original)
```

These 6 artifacts are the highest-value, hardest-to-recreate items. They should be preserved through rollback, not recreated. If they must be recreated, budget 4-8 hours of design work plus adversarial debate execution.

### Phase 3: Synthesis Artifacts (Sequential, depends on Phase 2)
```
[12] refactoring-plan.md                  (derives from [9]-[11])
[13] merged-approach.md                   (derives from [6]-[11])
```

### Phase 4: Specification Pipeline (Sequential)
```
[14] specification-draft-v1.md            (derives from [13])
[15] spec-panel-review.md                 (derives from [14] + SKILL.md files)
[16] specification-draft-v2.md            (derives from [14] + [15])
```

### Phase 5: Implementation Artifacts (Parallelize, depends on Phase 1)
```
[17] D-0004: Skill in allowed-tools (roadmap.md)        (EASY, ~5 min)
[18] D-0005: Skill in allowed-tools (sc-roadmap SKILL.md) (EASY, ~5 min)
[19] D-0006: Wave 2 Step 3 sub-steps                    (MEDIUM, ~30 min, depends on [13])
[20] D-0007: Fallback Protocol spec                     (MEDIUM, ~30 min, depends on [13])
[21] D-0008: Return Contract Routing spec               (MEDIUM, ~30 min, depends on [20])
```

### Phase 6: Evidence Records (Auto-generated during execution)
```
[22] T01.01/result.md   (byproduct of [1])
[23] T01.02/result.md   (byproduct of [4])
[24] T01.03/result.md   (byproduct of [5])
[25] T02.01/result.md   (byproduct of [17])
[26] T02.02/result.md   (byproduct of [18])
[27] T02.03/result.md   (byproduct of [19]-[21])
```

### Path Correction Note

All recreated artifacts MUST use post-rename paths (`-protocol` suffix) unless the rollback reverts the rename itself. If the rename is preserved through rollback:
- `sc-adversarial/` -> `sc-adversarial-protocol/`
- `sc-roadmap/` -> `sc-roadmap-protocol/`

The spec-v2 already uses the corrected paths and can serve as the path reference standard.

---

## Appendix A: Artifact Inventory by Batch

| Batch | Focus | Files | Key Insight |
|---|---|---|---|
| 1 | Three approach documents | 3 | Competing designs for headless invocation |
| 2 | D-0001 to D-0003 | 3 | Probe result + sprint variant + prereqs |
| 3 | D-0004 to D-0006 | 3 | Allowed-tools + Wave 2 step decomposition |
| 4 | D-0007, D-0008, T01.03 | 3 | Fallback protocol + contract routing + tier policy |
| 5 | Adversarial outputs (debate, scoring, selection) | 3 | Full evaluation pipeline |
| 6 | Specification pipeline (merged, v1, v2) | 3 | Design-to-spec evolution |
| 7 | Refactoring plan, panel review, T01.01 evidence | 3 | Synthesis + critique + probe result |
| 8 | Evidence T01.02, T01.03, T02.01 | 3 | Phase 1-2 verification receipts |
| 9 | Evidence T02.02, T02.03 | 2 | Phase 2 verification with adversarial review |

**Total unique artifacts analyzed**: 26 (across 25 files, with T01.01 evidence appearing in both batch 7 and the decision chain)

## Appendix B: Risk Register for Recreation

| Risk | Impact | Mitigation |
|---|---|---|
| Approach documents lost in rollback | HIGH -- 2718 lines of irreproducible design work | Preserve these files outside the rollback scope |
| Adversarial debate outputs lost | HIGH -- convergence decisions cannot be deterministically reproduced | Preserve; if lost, re-run debate with approach docs as input |
| Path references stale after rename | MEDIUM -- grep validations and line-number references will fail | Update all path references in recreated artifacts |
| SKILL.md content changed since analysis | MEDIUM -- panel review line numbers become invalid | Re-validate line numbers against current file state |
| `claude -p` becomes available | LOW -- changes the D-0001 probe outcome | Design artifacts already cover this path; switch to primary variant |
| Phases 3-5 never executed | LOW -- no evidence to preserve | Phases 3-5 can be executed fresh post-recreation |
