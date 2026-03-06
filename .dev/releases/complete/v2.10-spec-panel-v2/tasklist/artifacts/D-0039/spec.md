# D-0039: Release Documentation

## Changelog

### spec-panel v2.0 -- Correctness and Adversarial Review Enhancements

**Version**: 2.09
**Date**: 2026-03-05
**Breaking Changes**: None (all enhancements are additive)

#### New Capabilities

**SP-2: James Whittaker Adversarial Testing Persona**
- Added 11th expert to the review panel: James Whittaker, adversarial testing pioneer
- Five systematic attack methodologies: Zero/Empty, Divergence, Sentinel Collision, Sequence, Accumulation
- Structured finding output format with attack, invariant, condition, and scenario fields
- Active in every panel review; positioned after Fowler and Nygard in review sequence
- Token overhead: 5-9% per review (within 10% NFR-1 budget)

**SP-3: Guard Condition Boundary Table**
- Mandatory 7-column structured output when guard conditions detected in specification
- Input condition categories: Zero/Empty, One/Minimal, Typical, Maximum/Overflow, Sentinel, Edge Case
- Three completion hard gates: GAP->MAJOR severity, blank behavior->MAJOR, synthesis-blocking
- Expert assignments: Nygard (lead), Crispin (validation), Whittaker (attacks)
- Machine-parseable downstream output for sc:adversarial AD-1 integration
- Token overhead: 6-15% per review depending on guard count (within cumulative budget)

**SP-1: Correctness Focus Mode (`--focus correctness`)**
- New focus area with specialized 5-expert panel: Nygard (lead), Fowler, Adzic, Crispin, Whittaker
- Modified expert behaviors (FR-14.1 through FR-14.6): additive correctness shifts
- State Variable Registry: mandatory catalog of all mutable variables
- Guard Condition Boundary Table: always produced (not trigger-gated) under correctness focus
- Pipeline Flow Diagram: produced when pipelines present
- Auto-suggestion heuristic: recommends correctness focus when 3+ mutable state variables, guard conditions with thresholds, or pipeline/filter operations detected (advisory only)
- Token overhead: ~38% per correctness-focused review (within 40% SC-004 budget)

**SP-4: Pipeline Dimensional Analysis**
- Trigger: 2+ stage data flows where output count may differ from input count
- 4-step analysis: Detection, Quantity Annotation, Downstream Tracing, Consistency Check
- CRITICAL severity for dimensional mismatches (count conservation violations)
- Quantity Flow Diagram output artifact with N->M annotations
- Expert assignments: Fowler (leads detection and annotation), Whittaker (attacks divergence points)
- Does NOT trigger on CRUD-only specifications
- Token overhead: <1% when no pipelines, ~9% when pipelines detected

#### Integration Points

| Source | Target | Data Flow |
|--------|--------|-----------|
| SP-3 (Boundary Table GAPs) | sc:adversarial AD-1 | Priority invariant probe candidates |
| SP-2 (Attack Findings) | sc:adversarial AD-2 | Assumption challenge input |
| SP-1 (Correctness Findings) | sc:adversarial AD-5 | Edge case generation input |
| SP-4 (Quantity Flow Diagram) | sc:roadmap RM-3 | Risk-weighted prioritization input |
| SP-2 (Assumptions) | sc:roadmap RM-2 | Assumption tracking input |

#### Usage

```
/sc:spec-panel [specification_content|@file] [--mode discussion|critique|socratic] [--experts "name1,name2"] [--focus requirements|architecture|testing|compliance|correctness] [--iterations N] [--format standard|structured|detailed]
```

New flag: `--focus correctness` activates the correctness-focused review panel.

---

## Version Bump

- **From**: spec-panel v1.x (10 experts, no boundary table, no correctness focus, no pipeline analysis)
- **To**: spec-panel v2.0 (11 experts, boundary table, correctness focus, pipeline analysis)
- **Sprint version**: v2.09

---

## Migration Notes

- **No breaking changes**: All enhancements are additive. Existing usage patterns continue to work unchanged.
- **New output sections**: Panel reviews now include an "Adversarial Analysis" section (Whittaker findings) and may include a "Guard Condition Boundary Table" section when guard conditions are detected.
- **Correctness focus is opt-in**: The `--focus correctness` flag must be explicitly set or accepted from the auto-suggestion. It does not activate automatically.
- **Pipeline analysis is automatic**: When pipelines are detected, the analysis runs automatically. No opt-in required. Can be observed in output via the Quantity Flow Diagram artifact.

---

## Known Limitations

1. **FR-14.1 (Wiegers Correctness Shift)**: Defined but only activates when Wiegers is explicitly added via `--experts` alongside `--focus correctness`. The default correctness panel excludes Wiegers.
2. **AD-1 Consumer**: The boundary table output is formatted for sc:adversarial AD-1 consumption, but the adversarial skill does not yet declare an AD-1 receiver. This is a forward-declared integration point.
3. **RM-2/RM-3 Consumers**: Similar forward-declared integration points for sc:roadmap.
4. **Overhead edge cases**: Specifications with both guard conditions AND multi-stage pipelines may produce cumulative overhead slightly above the 25% standard threshold (measured ~26% mid). This is accepted as proportional to analytical value.

---

## Traceability
- Roadmap Item: R-038
- Task: T05.03
- Deliverable: D-0039
