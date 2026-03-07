# D-0003: SKILL.md Track A/B Integration Sequencing Plan

## Overview

Track A (Meta-Orchestrator) and Track B (Protocol Quality) both modify SKILL.md. This plan maps all modification sites, identifies conflicts, and specifies merge order.

## Modification Site Map

### Track A (Meta-Orchestrator) — M2 + M4

| # | Section | Lines (approx) | Modification | Milestone | Conflict Risk |
|---|---------|----------------|-------------|-----------|---------------|
| A1 | Required Input | 24-33 | DONE (M1/D1.1): Added `--pipeline` option | M1 | None (complete) |
| A2 | Configurable Parameters (FR-003) | 258-267 | DONE (M1/D1.1): Added `--pipeline` flag row | M1 | None (complete) |
| A3 | Input Mode Parsing Protocol | 438-460 | DONE (M1/D1.1): Added step_0_pipeline_guard | M1 | None (complete) |
| A4 | Meta-Orchestrator: Pipeline Mode | 1786+ | **NEW SECTION** — inline shorthand parser, YAML loader, DAG builder, cycle detection, dry-run | M2 | None (additive, end of file) |
| A5 | Meta-Orchestrator: Pipeline Mode | 1786+ | **EXTEND** — Phase Executor, artifact routing, parallel scheduler, manifest, resume, blind eval, plateau detection, error policies | M4 | None (extends A4) |
| A6 | Return Contract (MANDATORY) | 342-376 | **EXTEND** — Add pipeline-specific return fields (pipeline_manifest_path, phase_results) | M4 | Low (additive fields only) |
| A7 | Error Handling Matrix (FR-006) | 314-340 | **EXTEND** — Add pipeline-level error policies (halt-on-failure, continue) | M4 | Low (additive entries) |

### Track B (Protocol Quality) — M3 + M5

| # | Section | Lines (approx) | Modification | Milestone | Conflict Risk |
|---|---------|----------------|-------------|-----------|---------------|
| B1 | Step 1: Diff Analysis (overview) | 72-102 | **MODIFY** — Add shared assumption extraction sub-phase description | M3 | None |
| B2 | Structural Diff Engine | 567-615 | **EXTEND** — Add SHARED-ASSUMPTION extraction logic (A-NNN scheme) | M3 | None |
| B3 | diff-analysis.md Artifact Assembly | 734-790 | **MODIFY** — Add Shared Assumptions section to artifact template | M3 | None |
| B4 | Advocate Agent Instantiation (T03.01) | 795-866 | **MODIFY** — Update advocate prompt to require ACCEPT/REJECT/QUALIFY for shared assumptions | M3 | None |
| B5 | Step 2: Adversarial Debate (overview) | 104-141 | **MODIFY** — Add taxonomy levels (L1/L2/L3) and coverage check | M3 | None |
| B6 | Convergence Detection (T03.05) | 947-997 | **MODIFY** — Add taxonomy gate to convergence formula; include A-NNN in denominator | M3 | None |
| B7 | Round 2: Sequential Rebuttals (T03.03) | 899-922 | **EXTEND** — Add forced round trigger for uncovered taxonomy levels | M3 | None |
| B8 | Step 2: Adversarial Debate | 104-141 | **EXTEND** — Add Round 2.5 (invariant probe) description | M5 | None |
| B9 | Between Round 2 and Round 3 | ~922-946 | **NEW** — Round 2.5 fault-finder agent prompt, dispatch logic, invariant-probe.md assembly | M5 | None |
| B10 | Convergence Detection (T03.05) | 947-997 | **MODIFY** — Add invariant probe gate (HIGH UNADDRESSED blocks convergence) | M5 | Medium (overlaps B6) |
| B11 | Qualitative Scoring Layer (T04.02) | 1165-1228 | **EXTEND** — Add 6th dimension "Invariant & Edge Case Coverage" | M5 | None |
| B12 | Return Contract (MANDATORY) | 342-376 | **EXTEND** — Add `unaddressed_invariants` field | M5 | Low (overlaps A6) |

## Conflict Analysis

### Overlapping Modification Sites

| Site | Track A Modification | Track B Modification | Risk | Resolution |
|------|---------------------|---------------------|------|------------|
| Return Contract (342-376) | A6: Add pipeline fields (M4) | B12: Add `unaddressed_invariants` (M5) | Low | Both are additive field extensions. **Sequence: A6 first (M4), then B12 (M5)** — M5 depends on M4 so natural ordering resolves this. |
| Convergence Detection (947-997) | None | B6 (M3) + B10 (M5) | Medium | Same-track overlap. **Sequence: B6 first (M3 adds taxonomy gate), then B10 (M5 adds invariant gate)** — M5 depends on M3 so natural ordering resolves this. |
| Error Handling Matrix (314-340) | A7: Add pipeline errors (M4) | None | None | No conflict. |

### Non-Overlapping Sections (No Conflict)

- Track A modifies: lines 1786+ (new section), 342-376, 314-340
- Track B modifies: lines 72-102, 104-141, 567-615, 734-790, 795-866, 899-997, 1165-1228, 342-376
- The only shared section is the Return Contract (342-376), which is additive-only for both tracks.

## Merge Order

### Phase 1: Foundation (M1) — COMPLETE
- A1, A2, A3: `--pipeline` flag guard (done)

### Phase 2: Parallel Development (M2 || M3)

**Track A (M2)** modifies:
- A4: New Meta-Orchestrator section at end of file (no conflict)

**Track B (M3)** modifies:
- B1-B7: Diff analysis, debate protocol, convergence (no overlap with A4)

**Merge strategy**: Both tracks work on completely separate sections. No merge coordination needed. Can be developed in any order or in parallel.

### Phase 3: Integration (V1)
- Regression testing only, no SKILL.md changes

### Phase 4: Track A Phase 2 (M4)
- A5: Extend Meta-Orchestrator section (extends A4, no conflict)
- A6: Extend Return Contract (additive fields)
- A7: Extend Error Handling Matrix (additive entries)

### Phase 5: Track B Phase 2 (M5)
- B8-B11: Invariant probe round, scoring dimension (no overlap with M4 sections)
- B12: Extend Return Contract (additive field, after A6)
- B10: Extend Convergence Detection (after B6)

### Phase 6: Final Validation (V2)
- No SKILL.md changes

## Summary

| Conflict | Status | Resolution |
|----------|--------|------------|
| Return Contract (A6 vs B12) | **Resolved** | Natural dependency ordering (M4 before M5) |
| Convergence Detection (B6 vs B10) | **Resolved** | Natural dependency ordering (M3 before M5) |
| Blocking conflicts | **Zero** | All modifications are either in separate sections or resolved by milestone ordering |

## Deliverable Status

- **Task**: T01.03
- **Roadmap Item**: R-003
- **Status**: COMPLETE
- **Tier**: STANDARD
