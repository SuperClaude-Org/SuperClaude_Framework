

---
spec_source: spec-cross-framework-deep-analysis.md
complexity_score: 0.85
primary_persona: architect
---

# Cross-Framework Deep Analysis — Project Roadmap

## 1. Executive Summary

This roadmap governs an **8-phase analysis sprint** that systematically compares IronClaude's quality-enforcement layer against the `llm-workflows` framework, producing 35+ artifacts culminating in a machine-readable improvement backlog for v3.0 planning. The sprint is strictly analytical — no production code changes are in scope.

**Core challenge**: Dual-repository evidence-backed analysis with adversarial validation, enforcing three cross-cutting invariants (Auggie MCP evidence, anti-sycophancy, adopt-patterns-not-mass) across every artifact. The sequential phase-gate architecture means any single gate failure blocks all downstream work.

**Key architectural decisions**:
- Strict phase-gate enforcement with halt-on-failure semantics
- Auggie MCP as mandatory primary tool with Serena/Grep fallback
- Adversarial validation layer (Phase 7) that re-challenges all upstream work
- All output constrained to `artifacts/` directory

**Estimated total effort**: 3–5 working days across phases, assuming Auggie MCP availability and no major gate failures.

---

## 2. Phased Implementation Plan

### Phase 0: Pre-Sprint Setup (Gate: readiness check)

**Milestone**: Sprint infrastructure validated, all dependencies confirmed accessible.

1. Verify Auggie MCP connectivity to both repositories:
   - `/config/workspace/IronClaude` — test codebase-retrieval query
   - `/config/workspace/llm-workflows` — test codebase-retrieval query
2. Confirm `superclaude sprint run` CLI is functional with `--start`/`--end` flags
3. Create `artifacts/` output directory structure
4. Verify `artifacts/prompt.md` exists and is readable
5. Resolve **OQ-006** (executor parallelism capability) — determines Phase 2/3 scheduling
6. Resolve **OQ-008** (Auggie MCP partial-result threshold) — define "unavailable" criteria

**Gate criteria**: Both repos queryable via Auggie MCP, CLI executor runs a no-op phase successfully.

**Effort**: XS (< 2 hours)

---

### Phase 1: Component Inventory & Cross-Framework Mapping

**Milestone**: `component-map.md`, `inventory-ic.md`, `inventory-lw.md` produced.

1. **T01.01** — Auggie MCP discovery against IronClaude for all 8 component groups:
   - Roadmap pipeline, cleanup-audit CLI, sprint executor, PM agent, adversarial pipeline, task-unified tier system, quality agents, pipeline analysis subsystem
   - Record: file paths, interfaces, internal dependencies, extension points
2. **T01.02** — Verify all llm-workflows paths from `artifacts/prompt.md` via Auggie MCP
   - Flag stale paths with annotation; do not modify `prompt.md`
   - Resolves **OQ-001**
3. **T01.03** — Produce `component-map.md` with ≥8 IC-to-LW mappings
   - Annotate IC-only components explicitly
4. **T01.04** — Resolve **OQ-002** (pipeline-analysis granularity) based on discovery results

**Parallelism**: T01.01 and T01.02 can run concurrently (independent repos).

**Gate criteria** (SC-001): ≥8 IC components, ≥11 LW components, ≥8 mappings, IC-only annotations present.

**Effort**: M (half day)

---

### Phase 2: IronClaude Strategy Extraction

**Milestone**: 8 `strategy-ic-*.md` files produced.

1. For each of the 8 IC component groups, extract:
   - Design philosophy
   - Execution model
   - Quality enforcement mechanism
   - Error handling strategy
   - Extension points
2. Enforce anti-sycophancy: every strength claim must have a paired weakness (NFR-002)
3. All claims backed with `file:line` evidence from Auggie MCP (NFR-003)

**Parallelism**: Per-component extraction can run in parallel (6 concurrent recommended, per AC-012 authorization).

**Gate criteria** (SC-002): 8 files, each with strength-weakness pairing verified.

**Effort**: M (half day)

**Note**: Can run concurrently with Phase 3 if executor supports it (OQ-006).

---

### Phase 3: llm-workflows Strategy Extraction

**Milestone**: 11 `strategy-lw-*.md` files produced.

1. For each of the 11 LW components from `prompt.md`, extract:
   - Same strategy dimensions as Phase 2
   - Explicit "what makes it rigorous" section
   - Explicit "what makes it bloated/slow/expensive" section
2. Anti-sycophancy and evidence rules enforced identically to Phase 2

**Parallelism**: Per-component extraction can run in parallel. Can run concurrently with Phase 2.

**Gate criteria** (SC-003): 11 files, each covering rigor and cost dimensions with paired strengths/weaknesses.

**Effort**: M (half day)

---

### Phase 4: Adversarial Comparisons

**Milestone**: 8 `comparison-*.md` files produced.

1. For each of 8 defined comparison pairs, run `/sc:adversarial` producing:
   - Debating positions (IC advocate vs. LW advocate)
   - `file:line` evidence from both repositories
   - Clear verdict with conditions
   - Confidence score
   - "Adopt patterns not mass" verification
2. Handle inconclusive verdicts per RISK-004 mitigation: explicit "no clear winner" with rationale
3. Resolve **OQ-007** — if Phase 1 discovered additional high-value pairs, decide whether to add them (recommend: cap at 8 unless discovery reveals a critical gap)

**Parallelism**: Comparison pairs are independent; can run 4 concurrently.

**Gate criteria** (SC-004): 8 files, each with dual-repo evidence, non-trivial verdict, patterns-not-mass verified.

**Effort**: L (1 day) — adversarial debates are the most token-intensive phase.

---

### Phase 5: Strategy Synthesis

**Milestone**: `merged-strategy.md` produced.

1. Synthesize all 8 comparison verdicts into unified best-of-both strategy
2. Produce "rigor without bloat" section
3. Document all discard decisions with justification
4. Verify internal consistency — no contradictions between component sections
5. Apply "adopt patterns not mass" at synthesis level

**Parallelism**: None — depends on all Phase 4 outputs.

**Gate criteria** (SC-005): Rigor-without-bloat section present, no orphaned areas, discard decisions justified, internal consistency verified.

**Effort**: M (half day)

---

### Phase 6: Improvement Planning

**Milestone**: 8 `improve-*.md` + `improve-master.md` produced.

1. For each of 8 IC component groups, produce improvement plan items with:
   - Specific file paths, change description, rationale
   - Priority (P0/P1/P2/P3), effort (XS/S/M/L/XL)
   - Dependencies, acceptance criteria, risk assessment
2. Verify "patterns not mass" for every item adopting an LW pattern (NFR-004)
3. Distinguish "new code" items from "strengthen existing" items
4. Produce `improve-master.md` with cross-component dependency graph
5. Resolve **OQ-004** — for "discard both" verdicts, produce "IC-native improvement" items with explicit rationale

**Parallelism**: Per-component plans can run in parallel; master plan is sequential after all components complete.

**Gate criteria** (SC-006): 9 documents, P-tier + effort + file paths + patterns-not-mass status per item.

**Effort**: L (1 day)

---

### Phase 7: Adversarial Validation

**Milestone**: `validation-report.md` and `final-improve-plan.md` produced.

1. Validate improvement plan for:
   - Completeness (all Phase 1 components represented)
   - Scope creep / patterns-not-mass violations
   - Missing cross-framework insights
   - File path existence via Auggie MCP (NFR-003)
2. Produce `validation-report.md` with pass/fail per item
3. Correct all failures → produce `final-improve-plan.md`

**Parallelism**: None — depends on all Phase 6 outputs. Validation checks can be parallelized internally.

**Gate criteria** (SC-007): validation-report with per-item status, final-improve-plan with corrections applied, all file paths verified.

**Effort**: M (half day)

---

### Phase 8: Consolidated Outputs

**Milestone**: 4 final artifacts produced, sprint complete.

1. **`artifact-index.md`** — Link all produced artifacts with descriptions; verify end-to-end traceability (SC-010, SC-011)
2. **`rigor-assessment.md`** — Consolidated narrative: findings, per-component verdicts, overall rigor gap assessment
3. **`improvement-backlog.md`** — Machine-readable items per defined schema (AC-010); validate `/sc:roadmap` compatibility (SC-009)
4. **`sprint-summary.md`** — Findings count, verdict summary, items by priority, estimated effort, recommended implementation order
5. Resolve **OQ-003** — confirm FR-XFDA-001 registration is sufficient for roadmap linking
6. Resolve **OQ-005** — recommend producing a lightweight validation script alongside manual review

**Parallelism**: All 4 artifacts can be produced concurrently (independent outputs from shared inputs).

**Gate criteria** (SC-008, SC-009): 4 files produced, backlog schema validates, ≥35 total artifacts in `artifacts/`.

**Effort**: M (half day)

---

## 3. Risk Assessment & Mitigation

| ID | Risk | Sev | Prob | Mitigation | Contingency |
|----|------|-----|------|------------|-------------|
| RISK-001 | Auggie MCP unavailable (IronClaude) | High | Low | Test in Phase 0; Serena + Grep/Glob fallback | Annotate all fallback usage; Phase 7 flags unverified citations |
| RISK-002 | Auggie MCP unavailable (llm-workflows) | High | Low | Test in Phase 0; partial list from `prompt.md` reduces exposure | Proceed with known components; annotate gaps |
| RISK-003 | Stale llm-workflows paths | Med | Med | Phase 1 T01.02 explicitly verifies; stale paths flagged | Downstream phases use verified paths only |
| RISK-004 | Inconclusive comparison verdicts | Med | Med | Allow explicit "no clear winner" with rationale | Valid input to Phase 5; merged strategy addresses ambiguity |
| RISK-005 | Patterns-not-mass violations in plans | High | Med | R-RULE checkpoint at Phase 6; Phase 7 independent scan | Sprint halts on violation; item reworked before proceeding |
| RISK-006 | Sprint crash mid-phase (exit code -9) | Med | Low | Phase-gate checkpoints; `--start N` resume | Incremental artifact writes within phases |
| RISK-007 | Incomplete IC inventory | Med | Med | Broad Auggie queries; Phase 7 cross-checks file existence | Gaps annotated in sprint summary; backlog marked incomplete |

**Architect's assessment**: RISK-005 (patterns-not-mass violation) and RISK-001/002 (Auggie MCP availability) are the highest-impact risks. Phase 0 validation eliminates RISK-001/002 early. RISK-005 has dual enforcement (Phase 6 checkpoint + Phase 7 adversarial review), which is architecturally sound.

---

## 4. Resource Requirements & Dependencies

### Critical Dependencies (must be available before Phase 1)

| Dep | Resource | Validation |
|-----|----------|-----------|
| DEP-001 | Auggie MCP server | Phase 0: test query against both repos |
| DEP-002 | IronClaude repo at `/config/workspace/IronClaude` | Phase 0: path accessible |
| DEP-003 | llm-workflows repo at `/config/workspace/llm-workflows` | Phase 0: path accessible |
| DEP-004 | `artifacts/prompt.md` | Phase 0: file exists and readable |
| DEP-005 | `superclaude sprint run` CLI | Phase 0: functional with `--start`/`--end` |

### Phase-Specific Dependencies

| Phase | Dependencies |
|-------|-------------|
| Phase 4 | DEP-006: `/sc:adversarial` skill available |
| Phase 8 | DEP-007: `/sc:roadmap` schema known for validation |
| Post-sprint | DEP-008: `/sc:tasklist` for v3.0 sequencing |

### Fallback Dependencies (activated on primary failure)

| Primary | Fallback | Capability Loss |
|---------|----------|----------------|
| DEP-001 (Auggie) | DEP-009 (Serena) + DEP-010 (Grep/Glob) | No semantic search; reduced evidence quality |

### Token Budget Estimates

| Phase | Estimated Tokens | Driver |
|-------|-----------------|--------|
| Phase 0 | 2K | Connectivity tests |
| Phase 1 | 15K | Dual-repo inventory queries |
| Phase 2 | 20K | 8 strategy extractions with evidence |
| Phase 3 | 25K | 11 strategy extractions with evidence |
| Phase 4 | 40K | 8 adversarial debates (most expensive) |
| Phase 5 | 15K | Synthesis of 8 verdicts |
| Phase 6 | 25K | 9 improvement plan documents |
| Phase 7 | 20K | Adversarial validation + corrections |
| Phase 8 | 10K | 4 consolidated outputs |
| **Total** | **~170K** | |

---

## 5. Success Criteria & Validation Approach

### Validation Strategy

**Three-layer validation architecture**:

1. **Per-phase gate validation** (automated via sprint executor)
   - Table-based pass/fail per criterion
   - Halt-on-failure semantics
   - Covers SC-001 through SC-008

2. **Cross-cutting invariant validation** (Phase 7 adversarial + continuous)
   - Anti-sycophancy scan: grep for unpaired strength claims (SC-012)
   - Evidence verification: all `file:line` citations checked via Auggie MCP (SC-013)
   - Patterns-not-mass audit: every LW-sourced item flagged and verified (SC-014)

3. **End-to-end traceability validation** (Phase 8)
   - Component → strategy → comparison → merged → plan → backlog chain (SC-010)
   - Artifact index completeness — no orphans (SC-011)
   - Schema compliance for `/sc:roadmap` consumption (SC-009)

### Measurable Acceptance Criteria

| Criterion | Measurement | Target |
|-----------|------------|--------|
| Artifact count | `find artifacts/ -type f \| wc -l` | ≥ 35 |
| Anti-sycophancy coverage | Grep scan for unpaired strengths | 100% paired |
| Evidence coverage | Auggie MCP verification of citations | 100% verified |
| Patterns-not-mass compliance | Schema field check | 100% `true` |
| Backlog schema validity | `/sc:roadmap` dry-run ingestion | 0 errors |
| Sprint resume | `--start 3` with Phase 1-2 artifacts present | Successful |
| Gate enforcement | Delete gate artifact + attempt next phase | Sprint halts |
| Human review | Review 2 comparison docs | Non-trivial verdicts confirmed |

---

## 6. Timeline Estimates

| Phase | Duration | Depends On | Can Parallelize With |
|-------|----------|-----------|---------------------|
| Phase 0: Setup | 2 hours | — | — |
| Phase 1: Inventory | 4 hours | Phase 0 | — |
| Phase 2: IC Strategy | 4 hours | Phase 1 | Phase 3 (if executor supports) |
| Phase 3: LW Strategy | 4 hours | Phase 1 | Phase 2 (if executor supports) |
| Phase 4: Comparisons | 8 hours | Phases 2 + 3 | — |
| Phase 5: Synthesis | 4 hours | Phase 4 | — |
| Phase 6: Planning | 8 hours | Phase 5 | — |
| Phase 7: Validation | 4 hours | Phase 6 | — |
| Phase 8: Outputs | 4 hours | Phase 7 | — |

**Critical path** (sequential): Phase 0 → 1 → 2 → 4 → 5 → 6 → 7 → 8 = **38 hours**

**With Phase 2/3 parallelism**: Phase 0 → 1 → (2 ∥ 3) → 4 → 5 → 6 → 7 → 8 = **34 hours**

**Calendar estimate**: 3–5 working days, accounting for gate failures, rework, and open question resolution.

---

## 7. Open Questions Resolution Plan

| OQ | Question | Resolution Phase | Recommended Default |
|----|----------|-----------------|-------------------|
| OQ-001 | LW path staleness | Phase 1 (T01.02) | Proceed; annotate stale paths |
| OQ-002 | Pipeline-analysis granularity | Before Phase 2 | Keep as single group unless Phase 1 reveals >3 distinct subsystems |
| OQ-003 | FR registry requirement | Before Phase 8 | Spec-internal ID sufficient; add registry note if exists |
| OQ-004 | "Discard both" plan content | Before Phase 6 | Produce "IC-native improvement" item |
| OQ-005 | Validation script vs manual | Phase 8 | Produce lightweight schema validator |
| OQ-006 | Executor parallelism | Phase 0 | Test; if unsupported, run Phase 2 then Phase 3 sequentially |
| OQ-007 | Fixed vs dynamic pair count | Phase 1 exit | Cap at 8 unless critical gap discovered |
| OQ-008 | Auggie partial-result threshold | Phase 0 | Define: <50% query coverage = "unavailable"; annotate partial results |

---

## 8. Architect's Notes

**Strengths of this design**:
- The phase-gate architecture with halt-on-failure provides strong quality guarantees — no downstream phase consumes unvalidated input
- Triple invariant enforcement (anti-sycophancy, evidence-only, patterns-not-mass) as R-RULEs rather than advisory guidance is architecturally sound
- Phase 7 adversarial validation as an independent re-challenge layer catches errors that per-phase gates might miss

**Weaknesses and trade-offs**:
- Strict sequential gating makes the critical path long; a single Phase 4 gate failure blocks 4 downstream phases
- Token cost (~170K) is substantial for a pure-analysis sprint with no code output
- The 8 comparison pairs are fixed early; if Phase 1 reveals a fundamentally different component landscape, the Phase 4 structure may be suboptimal
- Auggie MCP is a single point of failure for the entire sprint's evidence quality

**Recommendations**:
1. **Prioritize Phase 0 thoroughly** — 80% of sprint risk is eliminated by confirming Auggie MCP works against both repos
2. **Resolve OQ-006 early** — Phase 2/3 parallelism saves 4 hours on the critical path
3. **Budget for one gate failure** — plan for 4 days, not 3, to absorb one rework cycle
4. **Consider a lightweight schema validator** (OQ-005) — manual validation of 35+ artifacts is error-prone; a 50-line script pays for itself immediately
