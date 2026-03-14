---
validation_milestones: 9
interleave_ratio: "1:2"
---

# Cross-Framework Deep Analysis — Test Strategy

## 1. Validation Milestones Mapped to Roadmap Phases

| Milestone | Phase | Gate ID | Validation Focus |
|-----------|-------|---------|-----------------|
| VM0 | Phase 0: Pre-Sprint Setup | SC-000 | Infrastructure readiness, dependency health, OQ resolutions recorded |
| VM1 | Phase 1: Component Inventory | SC-001 | Dual-repo component map completeness and path verification |
| VM2 | Phase 2: IC Strategy Extraction | SC-002 | Anti-sycophancy coverage, evidence attachment per IC component |
| VM3 | Phase 3: LW Strategy Extraction | SC-003 | Rigor+cost coverage, anti-sycophancy, evidence per LW component |
| VM4 | Phase 4: Adversarial Comparisons | SC-004 | Dual-repo evidence, non-trivial verdicts, patterns-not-mass |
| VM5 | Phase 5: Strategy Synthesis | SC-005 | Internal consistency, 5-principle coverage, no orphaned areas |
| VM6 | Phase 6: Improvement Planning | SC-006 | Schema completeness, dependency graph, patterns-not-mass per item |
| VM7 | Phase 7: Adversarial Validation | SC-007, SC-012, SC-013, SC-014 | Full invariant re-validation, schema pre-check, corrections applied |
| VM8 | Phase 8: Consolidated Outputs | SC-008, SC-009, SC-010, SC-011 | Final artifact package, schema ingestion, traceability, resume test |

---

## 2. Test Categories

### 2.1 Unit Tests — Artifact-Level Checks

Tests that validate individual artifact files in isolation.

| Test ID | Target | Check | Failure Mode |
|---------|--------|-------|--------------|
| U01 | Each `strategy-ic-*.md` | Strength claim has paired weakness within same section | Gate SC-002 fails |
| U02 | Each `strategy-lw-*.md` | Both rigor section AND cost/bloat section present | Gate SC-003 fails |
| U03 | Each `comparison-*.md` | Verdict field populated with one of: IC stronger / LW stronger / split by context / no clear winner / discard both | Gate SC-004 fails |
| U04 | Each `improve-*.md` item | Fields present: priority, effort, file_targets, patterns_not_mass, rationale | Gate SC-006 fails |
| U05 | `improvement-backlog.md` | Schema field set exactly matches AC-010 definition (id, component, title, priority, effort, pattern_source, rationale, file_targets, acceptance_criteria, risk, patterns_not_mass_verified) | Gate SC-009 fails |
| U06 | All artifacts | No `file:line` citation references a line > file length (existence check) | Gate SC-013 fails |
| U07 | `merged-strategy.md` | All 5 principle sections (evidence integrity, deterministic gates, restartability, bounded complexity, scalable quality enforcement) present | Gate SC-005 fails |
| U08 | `improve-master.md` | Dependency graph references only IDs that exist in component improvement plans | Gate SC-006 fails |

**Implementation**: Grep-based scans and schema field validators run at each phase gate. For U05, produce the lightweight schema validator per OQ-005 resolution.

### 2.2 Integration Tests — Cross-Artifact Consistency

Tests that validate relationships between artifacts across phases.

| Test ID | Test Description | Chain Validated |
|---------|-----------------|-----------------|
| I01 | Every IC component in `component-map.md` has a corresponding `strategy-ic-*.md` | M1 → M2 traceability |
| I02 | Every LW component in `component-map.md` has a corresponding `strategy-lw-*.md` | M1 → M3 traceability |
| I03 | Every comparison pair in Phase 4 references components present in both strategy sets | M2+M3 → M4 traceability |
| I04 | Every comparison verdict in `merged-strategy.md` traces to a `comparison-*.md` source | M4 → M5 traceability |
| I05 | Every improvement item in `improve-*.md` traces to a `merged-strategy.md` principle section | M5 → M6 traceability |
| I06 | Every improvement item with `pattern_source` referencing LW has `patterns_not_mass_verified: true` and a "why not full import" sentence | NFR-004 enforcement |
| I07 | `validation-report.md` contains a pass/fail entry for every item ID in `final-improve-plan.md` | M7 completeness |
| I08 | `artifact-index.md` links every file under `artifacts/` (cross-check via `find artifacts/ -type f`) | SC-011 |
| I09 | Every Phase 1 component ID appears in `improvement-backlog.md` | SC-010 full-chain |

### 2.3 End-to-End Tests — Sprint Behavioral Tests

Tests that validate the sprint executor and full pipeline behavior.

| Test ID | Test Description | Validates |
|---------|-----------------|-----------|
| E01 | `--start 3` with Phase 1+2 artifacts present → Phase 3 executes without re-running earlier phases | SC-015, NFR-005 |
| E02 | Delete a required gate artifact (e.g., `component-map.md`), attempt to start Phase 2 → sprint halts with clear error | SC-016 |
| E03 | `find artifacts/ -type f \| wc -l` ≥ 35 at Phase 8 completion | SC-018 |
| E04 | Feed `improvement-backlog.md` to `/sc:roadmap` → 0 schema errors | SC-009, NFR-006 |
| E05 | Phase 0 no-op phase test → CLI executor exits cleanly with gate pass recorded | AC-008 |

### 2.4 Acceptance Tests — Business-Level Validation

Tests that confirm the sprint delivers decision-quality outputs.

| Test ID | Acceptance Criterion | Measurable Target | SC Reference |
|---------|---------------------|-------------------|--------------|
| A01 | Human reviewer confirms ≥2 comparison documents contain non-trivial verdicts with dual-repo evidence | 2 docs reviewed, reviewer sign-off | SC-017 |
| A02 | Anti-sycophancy grep scan across all strategy and comparison artifacts | 0 unpaired strength claims | SC-012 |
| A03 | All `file:line` citations verified via Auggie MCP during Phase 7 | 100% verified | SC-013 |
| A04 | All LW-sourced backlog items have `patterns_not_mass_verified: true` | 100% compliance | SC-014 |
| A05 | `rigor-assessment.md` contains per-component-area verdicts for all 8 IC groups | 8/8 areas covered | FR-021 |
| A06 | `sprint-summary.md` includes items-by-priority count and recommended implementation order | Both sections present | FR-023 |

---

## 3. Test-Implementation Interleaving Strategy

**Ratio: 1:2** — one validation pass for every two tasks completed within a phase.

### Interleaving Model by Phase

```
Phase 0:  [Setup tasks T0.1–T0.7] → VM0 gate check (inline, synchronous)

Phase 1:  [T01.01 IC inventory] → spot-check U06 (file paths resolve)
          [T01.02 LW path verification] → run U06 for LW paths
          [T01.03 component-map.md produced] → VM1 gate: run U01 count checks, I01 prereq
          Gate VM1 must pass before Phase 2 starts.

Phase 2:  [Per-component IC extraction, 2 components] → run U01 (anti-syco check)
          [Next 3 components] → run U01 again
          [Final 3 components + gate] → VM2: full U01 scan + file:line spot-check
          Gate VM2 must pass before Phase 4 starts.

Phase 3:  [Per-component LW extraction, 3 components] → run U02
          [Next 4 components] → run U02
          [Final 4 components + gate] → VM3: full U02 scan
          Gate VM3 must pass before Phase 4 starts.

Phase 4:  [Comparison pairs 1–4] → run U03 on completed pairs
          [Comparison pairs 5–8] → run U03 on remaining pairs
          [Gate] → VM4: full U03 + dual-repo evidence spot-check (2 pairs sampled)
          Gate VM4 must pass before Phase 5 starts.

Phase 5:  [Principle sections drafted] → run U07 (all 5 sections present)
          [Traceability pass] → run I04
          [Gate] → VM5: U07 + I04 + contradiction scan
          Gate VM5 must pass before Phase 6 starts.

Phase 6:  [Per-component plans 1–4] → run U04 on completed items
          [Per-component plans 5–8] → run U04 + I06 (patterns-not-mass)
          [improve-master.md] → run U08
          [Gate] → VM6: full U04 + I06 + U08 + I05
          Gate VM6 must pass before Phase 7 starts.

Phase 7:  [Phase 7 validation checks] → run A02 (anti-syco grep), A03 (evidence check)
          [Schema pre-validation] → run U05 + E04 dry-run
          [Corrections applied] → run I07
          [Gate] → VM7: A02 + A03 + A04 + I07 + U05
          Gate VM7 must pass before Phase 8 starts.

Phase 8:  [4 artifacts produced concurrently] → run I08 (artifact-index), I09 (full-chain)
          [Resume test] → run E01 (mandatory)
          [Gate] → VM8: E01 + E03 + E04 + SC-009 schema ingestion
```

**Rationale**: Interleaving at 1:2 catches violations while evidence is still fresh, prevents cascading failures from propagating through expensive downstream phases, and supports the sprint's halt-on-failure gate semantics without adding excessive overhead to short phases.

---

## 4. Risk-Based Test Prioritization

Priority ordering maps directly to RISK table from the roadmap:

| Priority | Risk | Test IDs | Enforcement Point |
|----------|------|----------|-------------------|
| P0 — Block sprint if violated | RISK-001/002: Auggie MCP unavailability | E05 (Phase 0 connectivity), U06 (all phases) | Phase 0 gate; repeated per phase |
| P0 — Block sprint if violated | RISK-005: Patterns-not-mass violation | I06, A04, U04 `patterns_not_mass` field | Phase 6 checkpoint + Phase 7 disqualifying scan |
| P1 — Gate failure halts downstream | RISK-003: Stale LW paths | U06 on LW artifacts, T01.02 dual-status tracking | Phase 1 gate VM1 |
| P1 — Gate failure halts downstream | RISK-007: Incomplete IC inventory | I09 (all 8 components traced), I01 | Phase 7 cross-check + Phase 8 VM8 |
| P2 — Degrade quality if missed | RISK-004: Inconclusive verdicts | U03 (verdict class populated with conditions), A01 (human review) | Phase 4 gate VM4 |
| P2 — Degrade quality if missed | RISK-006: Sprint crash / resume failure | E01 (resume test), E02 (gate enforcement) | Phase 8 mandatory gate |
| P3 — Documentation gap | NFR-002: Anti-sycophancy gaps | A02 (full grep scan) | Phase 7 gate VM7; spot-checks VM2, VM3 |

**Fallback coverage**: When Auggie MCP triggers RISK-001/002, test U06 must be re-run against fallback (Serena/Grep) evidence; any claim that cannot be verified via fallback must be annotated `evidence: unverified` and flagged by A03 as a Phase 7 failure item.

---

## 5. Acceptance Criteria Per Milestone

### VM0 — Pre-Sprint Setup
- Both repos queryable via Auggie MCP (test query returns ≥1 result from each)
- CLI executor `--start`/`--end` flags functional via no-op phase
- OQ-006 (parallelism) and OQ-008 (unavailability threshold) documented with explicit decisions
- `artifacts/` directory structure created; `artifacts/prompt.md` readable
- Phase tasklists `phase-{1..8}-tasklist.md` + `tasklist-index.md` produced

### VM1 — Component Inventory
- `component-map.md` contains ≥8 IC components with file paths, interfaces, dependencies, extension points
- ≥11 LW components listed; each carries `path_verified` and `strategy_analyzable` status
- ≥8 IC-to-LW cross-framework mappings recorded
- All IC-only components explicitly annotated
- Zero stale paths silently absorbed; each stale path carries `path_verified: false`

### VM2 — IC Strategy Extraction
- 8 `strategy-ic-*.md` files present
- Each file contains: design philosophy, execution model, quality enforcement, error handling, extension points
- Every strength claim has a paired weakness in the same document
- ≥1 `file:line` evidence citation per strategic claim

### VM3 — LW Strategy Extraction
- 11 `strategy-lw-*.md` files present
- Each covers both rigor dimensions AND cost/bloat/overhead dimensions
- Every strength claim has a paired weakness
- Adoption categorization present: directly adoptable / conditionally adoptable / reject

### VM4 — Adversarial Comparisons
- 8 `comparison-*.md` files present
- Each contains: IC advocate position, LW advocate position, dual-repo `file:line` evidence, explicit verdict with confidence score
- Verdict class is one of the 5 defined classes; "no clear winner" verdicts include explicit conditions
- `patterns_not_mass` verification recorded per comparison

### VM5 — Strategy Synthesis
- `merged-strategy.md` present
- All 5 architectural principle sections present and non-empty
- No component from Phase 1 map is orphaned (missing from all principle sections)
- "Rigor without bloat" section explicitly present
- All discard decisions include justification
- No internal contradictions between principle sections

### VM6 — Improvement Planning
- 9 documents present: 8 per-component + `improve-master.md`
- Every improvement item contains: priority (P0–P3), effort (XS–XL), ≥1 specific file path, rationale tracing to principle, acceptance criteria, risk assessment
- Every LW-pattern adoption item has `patterns_not_mass: true` + "why not full import" sentence
- "Discard both" verdict items produce IC-native improvement items (not placeholders)
- `improve-master.md` dependency graph distinguishes prerequisites from optional refinements

### VM7 — Adversarial Validation
- `validation-report.md` with per-item pass/fail status
- `final-improve-plan.md` with all failures corrected
- Anti-sycophancy grep scan: 0 unpaired strength claims across all strategy + comparison artifacts
- 100% of `file:line` citations verified via Auggie MCP (or annotated as unverified with fallback notation)
- 100% of LW-sourced items have `patterns_not_mass_verified: true`
- `/sc:roadmap` schema pre-validated: 0 incompatibilities identified before Phase 8

### VM8 — Consolidated Outputs
- 4 final artifacts present: `artifact-index.md`, `rigor-assessment.md`, `improvement-backlog.md`, `sprint-summary.md`
- `find artifacts/ -type f | wc -l` ≥ 35
- `improvement-backlog.md` ingested by `/sc:roadmap` with 0 schema errors
- Every artifact file linked in `artifact-index.md` (zero orphans)
- Full traceability chain confirmed: every Phase 1 IC component appears in strategy → comparison → merged-strategy → improvement plan → backlog
- Resume test passes: `--start 3` with Phase 1+2 artifacts produces Phase 3 execution without re-running prior phases

---

## 6. Quality Gates Between Phases

Each gate is a hard blocker. No downstream phase executes against an unvalidated upstream gate.

### Gate G0 → G1 (Phase 0 → Phase 1)
**Required passing conditions**:
- Auggie MCP connectivity confirmed for both repos
- CLI executor no-op test passes
- OQ-006 and OQ-008 decisions recorded
- `artifacts/` structure initialized

**Automated checks**: E05, connectivity probe returning ≥1 result per repo

---

### Gate G1 → G2/G3 (Phase 1 → Phase 2 and/or Phase 3)
**Required passing conditions** (SC-001):
- `component-map.md` with ≥8 IC + ≥11 LW + ≥8 mappings
- Dual-status tracking on all LW paths
- Zero stale paths without annotation

**Automated checks**: grep count assertions on component-map.md, U06 on all IC paths cited

---

### Gate G2 → G4 and G3 → G4 (Phase 2 + Phase 3 → Phase 4)
**Both gates must pass before Phase 4 begins.**

**G2 required** (SC-002): 8 `strategy-ic-*.md` with paired strengths/weaknesses and evidence
**G3 required** (SC-003): 11 `strategy-lw-*.md` with rigor + cost sections

**Automated checks**: U01 on all IC files, U02 on all LW files, file count assertions

---

### Gate G4 → G5 (Phase 4 → Phase 5)
**Required passing conditions** (SC-004):
- 8 `comparison-*.md` present
- Each has populated verdict class and confidence score
- Dual-repo evidence present in each
- `patterns_not_mass` field present in each

**Automated checks**: U03 on all comparisons, file count assertion

---

### Gate G5 → G6 (Phase 5 → Phase 6)
**Required passing conditions** (SC-005):
- `merged-strategy.md` with all 5 principle sections
- "Rigor without bloat" section present
- No orphaned component areas
- I04 traceability from Phase 4 verdicts

**Automated checks**: U07, I04 cross-check

---

### Gate G6 → G7 (Phase 6 → Phase 7)
**Required passing conditions** (SC-006):
- 9 documents present
- All improvement items have required fields
- I05 traceability from merged-strategy principles
- I06 patterns-not-mass compliance for all LW-sourced items

**Automated checks**: U04, U08, I05, I06 full pass

---

### Gate G7 → G8 (Phase 7 → Phase 8)
**Required passing conditions** (SC-007, SC-012, SC-013, SC-014):
- `validation-report.md` and `final-improve-plan.md` produced
- A02 (anti-sycophancy) = 0 violations
- A03 (evidence coverage) = 100% verified or annotated
- A04 (patterns-not-mass) = 100% compliant
- `/sc:roadmap` schema pre-validated with 0 incompatibilities
- All disqualifying conditions clear: no unverifiable evidence, no mass adoption, no broken lineage, no implementation scope drift

**Automated checks**: A02 grep scan, U05 schema field check, I07 validation-report completeness

---

### Gate G8 — Sprint Complete
**Required passing conditions** (SC-008, SC-009, SC-010, SC-011, SC-015, SC-018):
- 4 final artifacts produced
- E03: artifact count ≥ 35
- E04: `/sc:roadmap` ingestion 0 errors
- I08: zero orphaned artifacts in index
- I09: full-chain traceability confirmed
- E01: resume test **mandatory pass** — sprint completion is blocked until this passes

**Disqualifying condition**: Sprint cannot be declared complete if E01 (resume test) fails, regardless of all other gates passing.
