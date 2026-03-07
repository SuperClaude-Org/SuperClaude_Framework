---
spec_sources:
  - .dev/releases/current/2.07-adversarial-v2/05-adversarial2.0-final-refactor-spec.md
  - .dev/releases/current/2.07-adversarial-v2/adversarial-release-spec.md
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
functional_requirements: 24
nonfunctional_requirements: 10
total_requirements: 34
domains_detected:
  - architecture
  - backend
  - quality
complexity_score: 0.690
complexity_class: MEDIUM
risks_identified: 8
dependencies_identified: 9
success_criteria_count: 10
extraction_mode: standard
adversarial:
  mode: combined
  consolidation_convergence: 0.85
  notes: Both specs are complementary (same release, additive changes). No conflicts detected.
---

# Extraction: /sc:adversarial v2.07 — Dual Release

> Structured extraction from two complementary specification documents for the v2.07 adversarial release.
> Spec 1: Meta-Orchestrator Architecture refactor.
> Spec 2: Protocol correctness improvements (assumption extraction, taxonomy, invariant probe, edge case scoring).

---

## Consolidation Notes

These two specs are explicitly designed as a unified release. Spec 1 addresses the **architectural extensibility** gap (multi-phase pipeline orchestration). Spec 2 addresses the **protocol correctness** gap (blind spots in consensus-building). They share the same target file (SKILL.md) and have zero conflicting requirements. The primary coordination concern is the order of SKILL.md modifications.

---

## Functional Requirements

### From Spec 1: Meta-Orchestrator Architecture

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-001 | `--pipeline <inline\|@path>` flag enabling multi-phase execution mode; mutually exclusive with `--compare`, `--source`, `--generate`, `--agents` | architecture | P0 | Spec1:L147-L156 |
| FR-002 | Inline pipeline shorthand parser: `phase1 -> phase2 \| phase3` where `->` = sequential, `\|` = parallel, `generate:<agents>` = Mode B, `compare` = Mode A | architecture | P0 | Spec1:L159-L175 |
| FR-003 | YAML pipeline file loader (`--pipeline @path.yaml`) with full phase schema validation (id, type, depends_on, source, generate, agents, compare_artifacts, depth, convergence, blind, output_suffix) | architecture | P0 | Spec1:L174-L264 |
| FR-004 | DAG builder with cycle detection, reference integrity checks, type validation; aborts on circular dependency | architecture | P0 | Spec1:L209-L225, L376-L381 |
| FR-005 | Phase Executor: translates phase config → Mode A (compare) or Mode B (generate) pipeline invocation per-phase | architecture | P0 | Spec1:L383-L395 |
| FR-006 | Phase-scoped output directories (`phase--<id>/`) + `pipeline-manifest.yaml` recording phase registry and return contracts | architecture | P0 | Spec1:L269-L295 |
| FR-007 | DAG scheduler with topological sort + parallel phase execution up to `--pipeline-parallel N` limit (default 3) | architecture | P0 | Spec1:L391-L406 |
| FR-008 | `--dry-run` flag: validate DAG, render execution plan (phase order, parallelism, artifact map, token estimate), exit without execution | architecture | P1 | Spec1:L47-L73 |
| FR-009 | `--blind` flag: strip model-identifying metadata from variant filenames and content headers before compare phase receives them | architecture | P1 | Spec1:L24-L43 |
| FR-010 | `--auto-stop-plateau` flag: halt pipeline when convergence delta <5% for 2 consecutive phases | architecture | P1 | Spec1:L76-L99 |
| FR-011 | `--pipeline-resume` flag: resume from last successful phase checkpoint in manifest; validates checksums of completed phases | architecture | P1 | Spec1:L360-L365 |
| FR-012 | `--pipeline-parallel N` flag: set max concurrent phases (default 3) | architecture | P1 | Spec1:L155 |
| FR-013 | `--pipeline-on-error continue` flag: skip failed phase's dependents, continue parallel branches unaffected | architecture | P1 | Spec1:L357-L361 |

### From Spec 2: Protocol Quality Improvements

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-014 | Shared Assumption Extraction sub-phase in Step 1 diff analysis (executes after unique_contribution_extraction, before diff_analysis_assembly) | quality | P0 | Spec2:L115-L195 |
| FR-015 | UNSTATED preconditions promoted to synthetic `[SHARED-ASSUMPTION]` diff points tagged A-NNN, included in total_diff_points for convergence formula | quality | P0 | Spec2:L123-L125 |
| FR-016 | Advocate prompt template updated: advocates must explicitly ACCEPT/REJECT/QUALIFY each `[SHARED-ASSUMPTION]` point in Round 1 | quality | P0 | Spec2:L126, L215-L226 |
| FR-017 | Three-level Debate Topic Taxonomy: L1 (Architecture), L2 (Interface Contracts), L3 (State Mechanics); each diff point tagged with 1+ levels | quality | P0 | Spec2:L246-L336 |
| FR-018 | Convergence gate: convergence not declared if any taxonomy level has zero debated points; forces one additional round on uncovered level | quality | P0 | Spec2:L252-L257 |
| FR-019 | Forced round for uncovered taxonomy level: structured instruction for each level (L3: enumerate state variables, trace transitions, identify boundary conditions) | quality | P0 | Spec2:L254-L257, L326-L336 |
| FR-020 | Round 2.5 Invariant Probe: fault-finder agent (not advocate) applies boundary-condition checklist (5 categories) to emerging consensus; condition on `--depth standard/deep` | quality | P1 | Spec2:L353-L466 |
| FR-021 | Convergence gate: HIGH-severity UNADDRESSED invariants from Round 2.5 block convergence; MEDIUM items logged as warnings in merge-log.md | quality | P1 | Spec2:L366-L370 |
| FR-022 | 6th qualitative scoring dimension "Invariant & Edge Case Coverage" with 5 binary CEV criteria; formula updated from /25 to /30 | quality | P2 | Spec2:L499-L578 |
| FR-023 | Floor requirement for base selection: variant scoring 0/5 on edge case dimension is INELIGIBLE as base (suspended if all variants score 0/5) | quality | P2 | Spec2:L514-L515 |
| FR-024 | Return contract extended: new `unaddressed_invariants` field listing HIGH-severity UNADDRESSED items from invariant-probe.md | quality | P1 | Spec2:L485-L495 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | Zero changes to the existing 5-step pipeline (diff → debate → score → plan → merge) | maintainability | Existing pipeline: ZERO CHANGES | Spec1:L406-L410 |
| NFR-002 | Zero changes to Mode A/B code paths | maintainability | Mode A and B: ZERO CHANGES | Spec1:L406-L410 |
| NFR-003 | Zero changes to existing return contract per-phase fields (backward compatible; only additions) | maintainability | All existing fields preserved | Spec1:L339-L341 |
| NFR-004 | Shared Assumption Extraction overhead ≤10% of Step 1 execution time | performance | ≤10% Step 1 overhead | Spec2:L129 |
| NFR-005 | Invariant Probe Round overhead ≤15% overall debate execution | performance | ≤15% total debate overhead | Spec2:L374 |
| NFR-006 | Edge case scoring dimension overhead ≤3% of scoring step | performance | ≤3% Step 3 overhead | Spec2:L521 |
| NFR-007 | Total cumulative overhead ceiling: ≤40% above pre-improvement baseline | performance | ≤40% total overhead ceiling | Spec2:L21 |
| NFR-008 | New artifacts (invariant-probe.md, expanded diff-analysis.md) use structured table format (not prose) for machine-parseable downstream consumption | maintainability | Structured tables required | Spec2:L131, L380 |
| NFR-009 | Invariant probe checklist extensible: new failure categories addable without modifying debate protocol structure | maintainability | Additive extensibility only | Spec2:L373, L375 |
| NFR-010 | Blind evaluation verification: merged output contains zero model-name references when `--blind` active | security | Zero model-name leakage | Spec1:L43 |

---

## Dependencies

| ID | Description | Type | Affected Requirements | Source |
|----|-------------|------|----------------------|--------|
| DEP-001 | FR-007 (DAG scheduler) requires FR-004 (DAG builder + validator) to be complete | internal | FR-004, FR-007 | Spec1 |
| DEP-002 | FR-005 (Phase Executor) requires FR-001 (pipeline flag detection) to be in place | internal | FR-001, FR-005 | Spec1 |
| DEP-003 | FR-008 (dry-run) requires FR-004 (DAG validation) — dry-run stops after validation | internal | FR-004, FR-008 | Spec1 |
| DEP-004 | FR-015 (synthetic diff points) requires FR-014 (shared assumption extraction) to produce them | internal | FR-014, FR-015 | Spec2 |
| DEP-005 | FR-018 (taxonomy convergence gate) requires FR-017 (taxonomy definition and tagging) | internal | FR-017, FR-018 | Spec2 |
| DEP-006 | FR-021 (invariant convergence gate) requires FR-020 (Round 2.5 invariant probe) | internal | FR-020, FR-021 | Spec2 |
| DEP-007 | FR-023 (edge case floor) requires FR-022 (6th scoring dimension) to be implemented | internal | FR-022, FR-023 | Spec2 |
| DEP-008 | FR-020 (invariant probe) benefits from FR-014 (shared assumption output) as richer input; not a hard dependency but recommended sequencing | internal | FR-014, FR-020 | Spec2:L692-L696 |
| DEP-009 | Both specs target the same SKILL.md file; Spec 1 adds ~400-600 lines (meta-orchestrator section), Spec 2 adds ~multiple sections within existing protocol; merge coordination required to prevent SKILL.md conflicts | internal | FR-001 through FR-024 | Both specs |

---

## Success Criteria

| ID | Description | Derived From | Measurable | Source |
|----|-------------|-------------|------------|--------|
| SC-001 | Canonical 8-step workflow executes end-to-end: `--pipeline "generate:opus:arch,opus:backend,opus:security -> generate:haiku:arch,haiku:backend,haiku:security -> compare --blind"` | FR-001 through FR-007, FR-009 | Yes | Spec1:Phase 4 test |
| SC-002 | Dry-run output matches actual execution plan (phase order, parallelism levels, artifact map) | FR-008 | Yes | Spec1:Merge 2 verification |
| SC-003 | Blind mode: merged output contains zero model-name references in provenance annotations | FR-009 | Yes | Spec1:Merge 1 verification |
| SC-004 | Plateau detection: fires warning when convergence delta <5% for 2 consecutive compare phases in a pipeline | FR-010 | Yes | Spec1:Merge 3 verification |
| SC-005 | Protocol regression: replay v0.04 variants through updated protocol and catch both escaped bug classes (filter divergence + zero-is-valid sentinel) | FR-014, FR-017, FR-018 | Yes | Spec2:Phase 1 validation |
| SC-006 | AC-AD2-1 through AC-AD2-4: shared assumption extraction produces correct output for all 4 acceptance scenarios | FR-014, FR-015, FR-016 | Yes | Spec2:L137-L155 |
| SC-007 | AC-AD5-1 through AC-AD5-4: taxonomy coverage gate triggers correctly, forced rounds execute and produce scored diff points | FR-017, FR-018, FR-019 | Yes | Spec2:L268-L286 |
| SC-008 | AC-AD1-1 through AC-AD1-4: invariant probe checklist fires, UNADDRESSED HIGH items block convergence, Round 2.5 skipped at depth=quick | FR-020, FR-021 | Yes | Spec2:L384-L402 |
| SC-009 | AC-AD3-1 through AC-AD3-3: edge case floor rejects zero-coverage variant, scoring differentiates high vs. low coverage variants | FR-022, FR-023 | Yes | Spec2:L529-L543 |
| SC-010 | Overhead measurement: all phases combined add ≤40% overhead above pre-improvement baseline in empirical testing | NFR-004 through NFR-007 | Yes | Spec2:L705 |

---

## Risks

| ID | Description | Probability | Impact | Affected Requirements | Source |
|----|-------------|-------------|--------|----------------------|--------|
| RISK-001 | Shared assumption extraction produces formulaic, low-quality output ("no assumptions identified") | Medium | High | FR-014, FR-015, SC-005 | Spec2:R-1 |
| RISK-002 | Cumulative overhead from all four improvements exceeds 40% ceiling | Medium | Medium | NFR-004 to NFR-007, SC-010 | Spec2:R-2 |
| RISK-003 | Forced taxonomy rounds produce shallow L3 analysis (agents have nothing substantive to say) | Low | Medium | FR-019, SC-007 | Spec2:R-3 |
| RISK-004 | Invariant checklist becomes stale as new bug classes emerge not covered by the 5 categories | Low | High | FR-020, SC-008 | Spec2:R-4 |
| RISK-005 | Context window competition from new artifacts (invariant-probe.md, expanded diff-analysis.md) in downstream steps | Low | Medium | FR-020, FR-024 | Spec2:R-5 |
| RISK-006 | SKILL.md merge conflicts between Spec 1 (large structural addition) and Spec 2 (in-protocol modifications); requires careful integration sequencing | Medium | High | DEP-009, NFR-001 to NFR-003 | Inferred |
| RISK-007 | Multi-phase pipeline significantly exceeds token cost estimates for complex pipelines | Medium | High | FR-007, FR-012 | Inferred |
| RISK-008 | Parallel phase execution in SKILL.md requires state isolation; shared state contamination between concurrent phases | Low | High | FR-007, NFR-001 | Inferred |

---

## Domain Distribution

| Domain | Percentage | Basis |
|--------|-----------|-------|
| Architecture / Protocol Design | ~50% | Meta-orchestrator, DAG, phase execution, pipeline management |
| Quality / Testing / Correctness | ~30% | Assumption extraction, taxonomy, invariant probe, scoring |
| Backend / Integration | ~20% | Artifact routing, manifest management, return contracts |

**Primary Persona**: `architect` (confidence: 0.78)
**Consulting Personas**: `analyzer` (0.54), `qa` (0.42)

---

> **Warning**: Adversarial consolidation used (combined mode). Convergence: 85%. Both specs are explicitly complementary. No unresolved conflicts.
