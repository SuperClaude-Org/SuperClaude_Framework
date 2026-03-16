---
spec_source: spec-cross-framework-deep-analysis.md
complexity_score: 0.85
adversarial: true
---

# Cross-Framework Deep Analysis — Final Merged Roadmap

## Executive Summary

This roadmap governs an **8-phase analysis sprint** that systematically compares IronClaude's quality-enforcement layer against the `llm-workflows` framework, producing 35+ artifacts culminating in a machine-readable improvement backlog for v3.0 planning. The sprint is strictly analytical — no production code changes are in scope.

**Core challenge**: Dual-repository evidence-backed analysis with adversarial validation, enforcing three cross-cutting invariants (Auggie MCP evidence, anti-sycophancy, adopt-patterns-not-mass) across every artifact. The sequential phase-gate architecture means any single gate failure blocks all downstream work.

**Architectural priorities** (synthesized from both variants):

1. **Evidence-first execution** — Auggie MCP is the primary discovery and verification mechanism; every meaningful claim must trace to verified `file:line` evidence; fallback tooling is controlled degradation requiring explicit annotation.
2. **Strict phase governance** — Hard gate enforcement with halt-on-failure semantics; no downstream artifact is trusted unless upstream gate criteria pass; resume capability is a core reliability feature.
3. **Rigor without scope inflation** — The deterministic rule `adopt patterns, not mass` governs all adoption decisions; output is a decision-quality improvement plan, not an implementation sprint.
4. **Cross-artifact consistency** — End-to-end traceability chain: `inventory → strategy → comparison → merged strategy → improvement plan → backlog`; no component area becomes orphaned or contradictory.

**Key architectural decisions**:
- Strict phase-gate enforcement with halt-on-failure semantics
- Auggie MCP as mandatory primary tool with multi-criteria unavailability definition and Serena/Grep fallback
- Adversarial validation layer (Phase 7) executed by independent Validation reviewer, not Architect lead
- Phase 5 synthesis organized around architectural principles with preserved component traceability
- All output constrained to `artifacts/` directory
- Resume testing mandatory in Phase 8 acceptance criteria (not optional QA)

**Estimated total effort**: 38 hours sequential / 34 hours with Phase 2/3 parallelism (3–5 working days), assuming Auggie MCP availability and no major gate failures. Token budget: ~170K tokens total (order-of-magnitude planning estimate; see §Resource Requirements for derivation disclosure).

---

## Phased Implementation Plan

### Phase 0: Pre-Sprint Setup

**Milestone M0**: Sprint infrastructure validated, all dependencies confirmed accessible, phase contracts defined.

#### Key Actions

1. Verify Auggie MCP connectivity to both repositories:
   - `/config/workspace/IronClaude` — execute test codebase-retrieval query
   - `/config/workspace/llm-workflows` — execute test codebase-retrieval query
2. Confirm `superclaude sprint run` CLI is functional with `--start`/`--end` flags via no-op phase test
3. Create `artifacts/` output directory structure; verify `artifacts/prompt.md` exists and is readable
4. Record dependency readiness state for: Auggie MCP, IronClaude repo access, llm-workflows repo access, prompt/source documents, downstream command expectations (`/sc:roadmap`, `/sc:tasklist`)
5. Resolve **OQ-006** (executor parallelism capability) — determines Phase 2/3 scheduling; if result is ambiguous, default to sequential execution
6. Resolve **OQ-008** (Auggie MCP unavailability definition) — apply merged multi-criteria definition: Auggie is "unavailable" if ANY of: (a) timeout occurs, (b) 3 consecutive query failures, (c) coverage confidence <50%. Fallback activates on first ANY condition met.
7. Create phase tasklists `phase-{1..8}-tasklist.md` and `tasklist-index.md`

#### Gate Criteria

Both repos queryable via Auggie MCP; CLI executor runs a no-op phase successfully; dependency health documented; OQ-006 and OQ-008 resolved with recorded decisions.

**Effort**: XS — < 2 hours / 0.5–1 working session

---

### Phase 1: Component Inventory and Cross-Framework Mapping

**Milestone M1**: Verified dual-repo component map with cross-framework mappings completed; canonical truth source established for all downstream phases.

#### Key Actions

1. **T01.01** — Auggie MCP discovery against IronClaude for all 8 component groups:
   - Roadmap pipeline, cleanup-audit CLI, sprint executor, PM agent, adversarial pipeline, task-unified tier system, quality agents, pipeline analysis subsystem
   - Record per component: verified file paths, exposed interfaces, internal dependencies, extension points
2. **T01.02** — Verify all llm-workflows paths from `artifacts/prompt.md` against `/config/workspace/llm-workflows` via Auggie MCP
   - For each inventory entry, record both `path_verified` status (path resolves in repo) and `strategy_analyzable` status (evidence sufficient for strategy extraction)
   - A stale path receives `path_verified=false, strategy_analyzable=false`; a verified path with degraded Auggie evidence receives `path_verified=true, strategy_analyzable=degraded`
   - Flag stale paths with explicit annotation; do not modify `prompt.md`
   - Resolves **OQ-001**
3. **T01.03** — Produce `component-map.md` with ≥8 IC-to-LW mappings; annotate IC-only components explicitly
4. **T01.04** — Resolve **OQ-002** (pipeline-analysis granularity): keep as single group unless Phase 1 reveals >3 distinct subsystems warranting separate comparison treatment

**Parallelism**: T01.01 and T01.02 can run concurrently (independent repos).

**Architectural note**: Treat this phase as the canonical truth source. Discoveries in later phases should be flagged as inventory gaps, not silently absorbed into scope.

#### Gate Criteria (SC-001)

≥8 IC components, ≥11 LW components, ≥8 cross-framework mappings, IC-only annotations present, all file paths explicitly verified or flagged stale with `path_verified`/`strategy_analyzable` dual status.

**Effort**: M — 4 hours / 2–3 working sessions

---

### Phase 2: IronClaude Strategy Extraction

**Milestone M2**: Full IronClaude strategy set completed with balanced trade-off analysis and evidence-backed claims.

#### Key Actions

1. For each of the 8 IC component groups, produce `strategy-ic-*.md` documenting:
   - Design philosophy and *why the current design exists*
   - Execution model
   - Quality enforcement mechanism
   - Error handling strategy
   - Extension points
   - System qualities: maintainability, checkpoint reliability, extensibility boundaries, operational determinism
2. Enforce anti-sycophancy (NFR-002): every strength claim must have a paired weakness/trade-off; any "good" pattern without stated cost fails review
3. Attach `file:line` evidence from Auggie MCP to all claims (NFR-003)

**Parallelism**: Per-component extraction can run concurrently (6 concurrent recommended per AC-012). Can run concurrently with Phase 3 if OQ-006 confirmed this in Phase 0; otherwise execute Phase 2 then Phase 3 sequentially.

#### Gate Criteria (SC-002)

8 files produced, each with strength-weakness pairing verified and `file:line` evidence attached to strategic claims.

**Effort**: M — 4 hours / 2–3 working sessions

---

### Phase 3: llm-workflows Strategy Extraction

**Milestone M3**: llm-workflows strategic reference corpus completed with explicit cost and rigor analysis.

#### Key Actions

1. For each of the 11 LW components from `artifacts/prompt.md`, produce `strategy-lw-*.md` documenting:
   - What is rigorous about this component
   - What is bloated / slow / expensive (complexity overhead, operational drag, maintenance burden, token/runtime expense)
   - Execution model and quality enforcement
   - Extension points
   - Categorization: (a) directly adoptable patterns, (b) conditionally adoptable patterns, (c) patterns to reject
2. Restrict analysis to the prompt-defined component list plus verified paths from Phase 1
3. Anti-sycophancy and evidence rules enforced identically to Phase 2

**Parallelism**: Per-component extraction can run concurrently. Can run concurrently with Phase 2 if Phase 0 confirmed executor parallelism.

#### Gate Criteria (SC-003)

11 files produced, each covering both rigor and cost dimensions with paired strengths/weaknesses and evidence.

**Effort**: M — 4 hours / 2–3 working sessions

---

### Phase 4: Adversarial Comparisons

**Milestone M4**: Adversarial comparison set complete with defensible, condition-specific verdicts.

#### Key Actions

1. For each of 8 defined comparison pairs, run `/sc:adversarial` producing `comparison-*.md` with:
   - Debating positions (IC advocate vs. LW advocate)
   - `file:line` evidence from both repositories
   - Clear verdict with conditions and confidence score
   - Explicit verdict class: IC stronger / LW stronger / split by context / no clear winner / discard both
   - "Adopt patterns not mass" verification
2. For "no clear winner" verdicts: require explicit condition-specific reasoning; a verdict is acceptable if conditions are explicit
3. Resolve **OQ-004**: for "discard both" verdicts, Phase 6 shall default to producing an **IC-native improvement item** with explicit rationale; placeholder omission is not permitted
4. Resolve **OQ-007**: cap comparison pairs at 8 unless Phase 1 inventory reveals a critical gap requiring an additional pair

**Parallelism**: Comparison pairs are independent; run up to 4 concurrently.

#### Gate Criteria (SC-004)

8 files produced, each with dual-repo evidence, non-trivial verdict with explicit conditions, patterns-not-mass verified.

**Effort**: L — 8 hours / 2–3 working sessions (most token-intensive phase)

---

### Phase 5: Strategy Synthesis

**Milestone M5**: Unified architectural strategy approved for planning use, organized for both architectural leverage and downstream traceability.

#### Key Actions

1. Synthesize all 8 comparison verdicts into `merged-strategy.md`
2. Organize cross-component guidance under five architectural principles, with component references explicitly preserved within each principle section to maintain Phase 1→6 traceability:
   - **Evidence integrity** — which components need stronger evidence verification; which LW patterns enforce this
   - **Deterministic gates** — gate design, halt-on-failure semantics, escape hatch discipline
   - **Restartability** — resume semantics, checkpoint placement, incremental artifact write discipline
   - **Bounded complexity** — patterns-not-mass enforcement, scope control, "why not full import" rationale
   - **Scalable quality enforcement** — anti-sycophancy, cross-artifact consistency, validation cadence
3. Include explicit "rigor without bloat" section
4. Document all discard decisions with justification; verify "adopt patterns not mass" at synthesis level
5. Run internal contradiction review; verify no orphaned component areas

**Parallelism**: None — depends on all Phase 4 outputs.

**Architectural note**: The principle-centric organization makes this document architecturally reusable across future sprints. Component references within each principle section preserve direct traceability so Phase 6 planners can produce component-level improvement items without a translation gap.

#### Gate Criteria (SC-005)

Rigor-without-bloat section present, all five principle sections cover relevant components, no orphaned areas, discard decisions justified, internal consistency verified.

**Effort**: M — 4 hours / 1–2 working sessions

---

### Phase 6: Improvement Planning

**Milestone M6**: Full improvement portfolio and dependency graph completed with all items implementation-ready and analysis-scope bounded.

#### Key Actions

1. For each of 8 IC component groups, produce `improve-*.md` with improvement plan items, each containing:
   - Specific file paths and change description
   - Rationale tracing to merged strategy principle
   - Priority (P0/P1/P2/P3), effort (XS/S/M/L/XL)
   - Dependencies, acceptance criteria, risk assessment
   - Classification: "strengthen existing code" vs. "add new code"
   - For LW-pattern adoptions: `patterns_not_mass: true` field + "why not full import" sentence
2. Apply structural leverage priority ordering:
   1. Gate integrity improvements
   2. Evidence verification improvements
   3. Restartability/resume semantic improvements
   4. Traceability automation improvements
   5. Artifact schema reliability improvements
3. Produce `improve-master.md` with cross-component dependency graph isolating prerequisites from optional refinements
4. For "discard both" verdict items: produce IC-native improvement items per OQ-004 resolution

**Parallelism**: Per-component plans can run in parallel; master plan is sequential after all component plans complete.

#### Gate Criteria (SC-006)

9 documents (8 component + 1 master), every item has P-tier + effort + file paths + `patterns_not_mass` status + "why not full import" where applicable, dependency graph present.

**Effort**: L — 8 hours / 2–3 working sessions

---

### Phase 7: Adversarial Validation

**Milestone M7**: Validated and corrected final improvement plan approved by independent Validation reviewer.

#### Key Actions

1. **Pre-gate action**: Validate `/sc:roadmap` schema expectations against `improvement-backlog.md` schema *before* Phase 8 begins. Schema incompatibilities discovered here are corrected at planning level; Phase 8 confirms schema compliance rather than discovering violations.
2. Execute formal architecture review gate (not a formatting pass or compliance scan); this phase shall be executed by the **Validation reviewer role**, not the Architect lead, to preserve adversarial independence
3. Validate for:
   - File path existence via Auggie MCP verification (NFR-003)
   - Anti-sycophancy coverage completeness
   - Patterns-not-mass compliance for all LW-sourced items
   - Completeness: all Phase 1 components represented in improvement plans
   - Absence of scope creep / drift into implementation scope
   - Missing cross-framework insights
   - Cross-artifact lineage integrity (no broken traceability chain)
4. **Disqualifying conditions** (items failing any of these must be reworked, not approved):
   - Evidence is unverifiable
   - Copied mass appears in adoption recommendations
   - Cross-artifact lineage is broken
   - Recommendations drift into implementation scope
5. Produce `validation-report.md` with per-item pass/fail status
6. Correct all failures; produce `final-improve-plan.md`

**Parallelism**: Internal validation checks can be parallelized; phase output is sequential after all checks complete.

#### Gate Criteria (SC-007, SC-012, SC-013, SC-014)

`validation-report.md` with per-item status, `final-improve-plan.md` with corrections applied, all file paths verified, `/sc:roadmap` schema pre-validated, all failed items corrected or explicitly retired.

**Effort**: M — 4 hours / 1–2 working sessions

---

### Phase 8: Consolidated Outputs

**Milestone M8**: Final artifact package complete, traceable, and consumable by downstream tooling.

#### Key Actions

1. Produce all 4 final artifacts concurrently (independent outputs from shared inputs):
   - **`artifact-index.md`** — Link all produced artifacts with descriptions; control-plane asset for audit and future execution; verify end-to-end traceability (SC-010, SC-011)
   - **`rigor-assessment.md`** — Consolidated narrative: findings, per-component verdicts, overall rigor gap assessment; surface any inventory incompleteness as architecture debt
   - **`improvement-backlog.md`** — Machine-readable items per AC-010 schema; confirm `/sc:roadmap` schema compatibility (SC-009); this is an integration boundary artifact requiring strict schema discipline
   - **`sprint-summary.md`** — Findings count, verdict summary, items by priority, estimated effort, recommended implementation order
2. Verify mandatory **resume testing**: sprint SHALL NOT complete Phase 8 unless `--start 3` with Phase 1–2 artifacts present succeeds; this is a mandatory gate condition, not optional QA
3. Resolve **OQ-003** — confirm FR-XFDA-001 registration is sufficient for roadmap linking
4. Resolve **OQ-005** — produce a lightweight schema validator script (recommended: always low effort relative to manual review of 35+ artifacts); if not produced, document manual validation protocol and all known failure modes

**Parallelism**: All 4 artifacts can be produced concurrently.

#### Gate Criteria (SC-008, SC-009)

4 files produced, backlog schema validates, ≥35 total artifacts in `artifacts/`, resume test passes, `/sc:roadmap` schema confirmation passes.

**Effort**: M — 4 hours / 1–2 working sessions

---

## Risk Assessment

### High-Priority Risks

| ID | Risk | Sev | Prob | Mitigation | Contingency |
|----|------|-----|------|------------|-------------|
| RISK-001 | Auggie MCP unavailable (IronClaude) | High | Low | Test in Phase 0; multi-criteria unavailability definition (OQ-008); Serena + Grep/Glob fallback protocol defined in advance | Annotate all fallback-derived claims; downgrade confidence in affected artifacts; Phase 7 flags unverified citations; re-run verification if Auggie restored |
| RISK-002 | Auggie MCP unavailable (llm-workflows) | High | Low | Test in Phase 0; partial list from `prompt.md` reduces exposure; same multi-criteria protocol as RISK-001 | Proceed with verified components; annotate gaps; downstream phases use verified paths only |
| RISK-003 | Stale llm-workflows file paths | Med | Med | Phase 1 T01.02 hard gate: dual-status tracking (`path_verified`/`strategy_analyzable`); stale paths explicitly flagged | Downstream phases use verified paths only; stale-path items cannot enter Phase 3 unmarked |
| RISK-004 | Inconclusive comparison verdicts | Med | Med | Normalize verdict taxonomy; permit "no clear winner" with mandatory condition-specific reasoning | Explicit conditions required; valid input to Phase 5; merged strategy addresses ambiguity |
| RISK-005 | Patterns-not-mass violations in plans | High | Med | Phase 6 checklist: pattern extracted? minimum viable adaptation? no large-scale import implied? "why not full import" sentence required; Phase 7 independent adversarial scan | Sprint halts on violation; item reworked before proceeding; disqualifying condition in Phase 7 |
| RISK-006 | Sprint crash mid-phase (prior history documented) | Med | Med | Incremental artifact writes within long phases; gate-based restart via `--start`; resume testing is mandatory Phase 8 acceptance, not optional QA | `--start N` recovery; validated at Phase 8 gate |
| RISK-007 | Incomplete IC inventory due to codebase drift | Med | Med | Broad Auggie queries in Phase 1; Phase 7 cross-checks file existence; annotate late-discovered gaps | Surface incompleteness in `rigor-assessment.md` as architecture debt; backlog marked incomplete where applicable |

### Cross-Cutting Risk Controls

1. **Gate tables with pass/fail criteria** — prevents subjective progression
2. **Explicit invariant enforcement** — anti-sycophancy, evidence verification, patterns-not-mass, restartability
3. **Traceability enforcement** — prevents orphaned outputs and reasoning gaps
4. **Artifact isolation** — all outputs remain inside designated artifacts tree
5. **Independent Phase 7 reviewer** — Validation reviewer (not Architect lead) preserves adversarial integrity

**Architect's assessment**: RISK-005 (patterns-not-mass violation) and RISK-001/002 (Auggie MCP availability) are the highest-impact risks. Phase 0 multi-criteria definition and connectivity testing eliminates RISK-001/002 early. RISK-005 has dual enforcement (Phase 6 checklist + Phase 7 formal gate with disqualifying conditions). RISK-006 prior crash history is elevated from "Low" to "Med" probability given documented operational evidence — mandatory resume testing is the mitigation.

---

## Resource Requirements

### Team / Roles

| Role | Responsibilities | Phase Focus | Notes |
|------|-----------------|-------------|-------|
| Architect lead | Phase design, consistency, strategy synthesis | Phases 0, 5, 6 | Must NOT execute Phase 7 to preserve adversarial independence |
| Analysis operator | Discovery, evidence gathering, artifact drafting | Phases 1, 2, 3, 4 | Primary Auggie MCP executor |
| Validation reviewer | Gate verification, Phase 7 adversarial review | Phases 7, 8 | Must be independent of Architect lead for Phase 7 |
| Optional human reviewer | Spot-checks comparison quality and verdict usefulness | Phase 7, Phase 8 | Recommended given Phase 7's formal gate requirements |

**Coordination note**: Multi-person execution adds coordination overhead not fully reflected in per-phase hour estimates. Budget additional 10–15% for handoff overhead when Architect lead and Validation reviewer transitions occur between Phase 6 and Phase 7.

### Tooling Dependencies

| Dep | Resource | Phase Required | Validation |
|-----|----------|---------------|-----------|
| DEP-001 | Auggie MCP server | Phase 0–8 (primary) | Phase 0: test query against both repos |
| DEP-002 | IronClaude repo at `/config/workspace/IronClaude` | Phase 0–8 | Phase 0: path accessible |
| DEP-003 | llm-workflows repo at `/config/workspace/llm-workflows` | Phase 0–8 | Phase 0: path accessible |
| DEP-004 | `artifacts/prompt.md` | Phase 0 | File exists and readable |
| DEP-005 | `superclaude sprint run` CLI | Phase 0–8 | Phase 0: functional with `--start`/`--end` |
| DEP-006 | `/sc:adversarial` skill | Phase 4 | Available before Phase 4 begins |
| DEP-007 | `/sc:roadmap` schema | Phase 7 (pre-validation) | Schema known before Phase 7 gate |
| DEP-008 | `/sc:tasklist` | Post-sprint | For v3.0 sequencing |

### Fallback Dependencies

| Primary | Fallback | Capability Loss |
|---------|----------|----------------|
| DEP-001 (Auggie MCP) | Serena MCP + Grep/Glob | No semantic search; reduced evidence quality; all fallback claims annotated |

### Token Budget

Estimates are **architectural approximations** based on comparable adversarial debate costs and inventory query patterns. Treat as order-of-magnitude planning inputs, not measured targets. Actual Phase 4 costs may vary 2x based on evidence contestation intensity. No derivation methodology was applied — teams should treat this as a planning floor, not a commitment.

| Phase | Estimated Tokens | Driver |
|-------|-----------------|--------|
| Phase 0 | 2K | Connectivity tests, OQ resolution |
| Phase 1 | 15K | Dual-repo inventory queries, dual-status tracking |
| Phase 2 | 20K | 8 strategy extractions with evidence |
| Phase 3 | 25K | 11 strategy extractions with evidence |
| Phase 4 | 40K | 8 adversarial debates (most expensive; variable with evidence contestation) |
| Phase 5 | 15K | Synthesis of 8 verdicts into principle-centric structure |
| Phase 6 | 25K | 9 improvement plan documents with dependency graph |
| Phase 7 | 20K | Formal gate validation + schema pre-validation + corrections |
| Phase 8 | 10K | 4 consolidated outputs + resume test |
| **Total** | **~172K** | |

---

## Success Criteria and Validation Approach

### Validation Architecture

**Layer 1 — Per-phase gate validation** (automated via sprint executor):
- Table-based pass/fail per criterion at each phase boundary
- Halt-on-failure semantics; no downstream phase executes against unvalidated input
- Covers SC-001 through SC-008

**Layer 2 — Cross-cutting invariant validation** (Phase 7 formal gate + continuous):
- **Coverage domain**: All 8 IC component groups represented; all 11 LW components covered; all required artifact classes present; artifact count ≥35
- **Evidence domain**: 100% of `file:line` citations verified; dual-repo evidence for all comparison artifacts; stale paths flagged, not hidden
- **Rule compliance domain**: Anti-sycophancy coverage complete; patterns-not-mass verified for all relevant items; no production code modifications; outputs only in permitted directory
- **Flow and traceability domain**: Every Phase 1 component maps through all later stages; no orphaned artifacts; merged strategy covers all component areas
- **Operability domain**: Resume via `--start` works from existing checkpoint; missing gate artifact blocks phase execution; `improvement-backlog.md` accepted by `/sc:roadmap`

**Layer 3 — End-to-end traceability validation** (Phase 8 confirmation):
- Component → strategy → comparison → merged → plan → backlog chain (SC-010)
- Artifact index completeness — no orphans (SC-011)
- Schema compliance for `/sc:roadmap` consumption (SC-009; pre-validated in Phase 7)

### Measurable Acceptance Criteria

| Criterion | Measurement Method | Target |
|-----------|-------------------|--------|
| Artifact count | `find artifacts/ -type f \| wc -l` | ≥ 35 |
| Anti-sycophancy coverage | Grep scan for unpaired strength claims | 100% paired |
| Evidence coverage | Auggie MCP verification pass on all citations | 100% verified |
| Patterns-not-mass compliance | Schema field check on all LW-sourced items | 100% `true` |
| Backlog schema validity | `/sc:roadmap` ingestion confirmation | 0 errors |
| Sprint resume | `--start 3` with Phase 1–2 artifacts present | **Mandatory pass** (gate condition) |
| Gate enforcement | Delete gate artifact + attempt next phase | Sprint halts |
| Schema pre-validation | `/sc:roadmap` schema validated before Phase 8 | 0 incompatibilities entering Phase 8 |
| Human review | Optional: review 2 comparison docs | Non-trivial verdicts confirmed |
| Inventory completeness | Cross-check Phase 1 components against Phase 6 improvement items | 0 orphaned component areas |

### Validation Cadence

1. **Per phase**: gate-specific pass/fail table with halt-on-failure
2. **At Phase 6 exit**: dependency graph and planning completeness review
3. **At Phase 7** (pre-Phase 8): formal adversarial re-validation of all major invariants + `/sc:roadmap` schema pre-validation
4. **At Phase 8**: downstream integration certification and traceability confirmation

---

## Timeline Estimates

| Phase | Hours | Sessions | Depends On | Parallelizes With |
|-------|-------|----------|-----------|-------------------|
| Phase 0: Setup | 2h | 0.5–1 | — | — |
| Phase 1: Inventory | 4h | 2–3 | Phase 0 | — |
| Phase 2: IC Strategy | 4h | 2–3 | Phase 1 | Phase 3 (if OQ-006 confirmed) |
| Phase 3: LW Strategy | 4h | 2–3 | Phase 1 | Phase 2 (if OQ-006 confirmed) |
| Phase 4: Comparisons | 8h | 2–3 | Phases 2 + 3 | — |
| Phase 5: Synthesis | 4h | 1–2 | Phase 4 | — |
| Phase 6: Planning | 8h | 2–3 | Phase 5 | — |
| Phase 7: Validation | 4h | 1–2 | Phase 6 | — |
| Phase 8: Outputs | 4h | 1–2 | Phase 7 | — |

**Critical path (sequential)**: Phase 0 → 1 → 2 → 4 → 5 → 6 → 7 → 8 = **38 hours**

**With Phase 2/3 parallelism** (if OQ-006 confirmed in Phase 0): Phase 0 → 1 → (2 ∥ 3) → 4 → 5 → 6 → 7 → 8 = **34 hours**

**Calendar estimate**: 3–5 working days. Budget for one gate failure and rework cycle — plan for 4 days, not 3. Multi-person coordination overhead adds approximately 10–15% to phases with role handoffs (Phase 6→7 transition).

**On timeline units**: Use hours for calendar scheduling and resource planning. Use session counts for effort-uncertainty communication (sessions acknowledge variable-duration units; the 78% session-range variance reflects calibrated uncertainty, not imprecision). Both are provided; neither supersedes the other.

---

## Open Questions Resolution Plan

| OQ | Question | Resolution Phase | Resolved Default |
|----|----------|-----------------|-----------------|
| OQ-001 | LW path staleness handling | Phase 1 (T01.02) | Proceed with verified paths; flag stale with `path_verified=false, strategy_analyzable=false` |
| OQ-002 | Pipeline-analysis granularity | Before Phase 2 | Keep as single group unless Phase 1 reveals >3 distinct subsystems |
| OQ-003 | FR registry requirement for roadmap linking | Before Phase 8 | Spec-internal ID sufficient; add registry note if external registry exists |
| OQ-004 | "Discard both" verdict content | Before Phase 6 | Produce IC-native improvement item with explicit rationale; placeholder omission not permitted |
| OQ-005 | Schema validator: script vs. manual | Phase 8 | Produce lightweight schema validator (always low effort vs. manual review of 35+ artifacts); if not produced, document manual protocol and failure modes |
| OQ-006 | Executor parallelism support | Phase 0 | Test; if confirmed: Phase 2/3 concurrent; if ambiguous or unsupported: Phase 2 then Phase 3 sequentially |
| OQ-007 | Fixed vs. dynamic comparison pair count | Phase 1 exit | Cap at 8 unless critical gap discovered in Phase 1 inventory |
| OQ-008 | Auggie MCP unavailability definition | Phase 0 | ANY of: (a) timeout, (b) 3 consecutive query failures, (c) coverage confidence <50%; fallback activates on first ANY condition met |
