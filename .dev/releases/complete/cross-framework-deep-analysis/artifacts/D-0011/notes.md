---
deliverable: D-0011
task: T02.04
title: OQ-002 Decision — Pipeline-Analysis Granularity
status: complete
decision: single-group
generated: 2026-03-14
evidence_source: D-0008/spec.md
---

# D-0011: OQ-002 Resolution — Pipeline-Analysis Granularity Decision

## Decision

**DECISION: SINGLE-GROUP**

The pipeline-analysis subsystem is kept as a **single component group** for all downstream phases (Phase 3, Phase 4, Phase 5).

---

## Evidence from D-0008

The Phase 2 IC inventory (D-0008, Component Group 8) identified the following distinct modules within the Pipeline Analysis Subsystem:

| Module File | Function |
|-------------|----------|
| `executor.py` | Generic step sequencer (shared by sprint + roadmap) |
| `gates.py` | Tier-proportional gate validator |
| `models.py` | Shared data models (Step, StepResult, GateCriteria) |
| `trailing_gate.py` | TrailingGateRunner (daemon-thread shadow mode) |
| `diagnostic_chain.py` | 4-stage failure diagnostic |
| `guard_analyzer.py` + `guard_pass.py` + `guard_resolution.py` | Guard/sentinel detection |
| `dataflow_graph.py` + `dataflow_pass.py` | Cross-deliverable state variable graph |
| `combined_m2_pass.py` | Combined invariant registry + FMEA sub-passes |
| `fmea_classifier.py` + `fmea_promotion.py` | FMEA failure mode classification |
| `invariant_pass.py` | Invariant registry pass |

**Distinct module count: 10 files** across **4 functional sub-areas**: (1) execution/gating core, (2) FMEA + invariant analysis, (3) dataflow tracing, (4) guard/sentinel detection.

---

## Decision Rule Application

Per the roadmap's default rule: **keep as single group unless Phase 2 inventory revealed >3 distinct subsystems warranting separate comparison treatment.**

The inventory reveals 4 functional sub-areas (count > 3). However, the rule applies to subsystems "warranting **separate comparison treatment**" — meaning LW has distinct counterparts for each sub-area that justify independent Phase 5 comparison.

**Assessment**: The 4 sub-areas do NOT warrant separate comparison treatment because:

1. **Shared API surface**: All 10 modules are exposed through a single `__init__.py` with a 42-symbol public API. They are architecturally coupled and designed as one subsystem.
2. **No distinct LW counterparts**: The LW PABLOV system (`.gfdoc/rules/core/ib_agent_core.md` + `automated_qa_workflow.sh`) provides a single unified comparison target for the entire subsystem — there is no separate LW module for "FMEA" vs "dataflow" vs "guards."
3. **Comparison pair integrity**: Splitting would produce 4 IC sub-areas vs 1 LW counterpart — a lopsided comparison better handled within a single comparison pair using sub-dimensions.

**Conclusion**: 4 sub-areas detected, but the "separate comparison treatment" condition is NOT met. Default rule applied: **SINGLE-GROUP**.

---

## Phase Scope Impact

- **Phase 3**: Analyze pipeline-analysis as one strategy extraction unit
- **Phase 5**: One comparison pair: IC Pipeline Analysis Subsystem ↔ LW PABLOV + automated_qa_workflow
- **Phase 6**: One refactoring plan entry for pipeline-analysis subsystem

This decision is stable: the same D-0008 evidence produces the same outcome.
