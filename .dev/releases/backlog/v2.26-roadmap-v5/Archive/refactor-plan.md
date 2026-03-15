# Refactoring Plan: v2.25 Roadmap v5 Spec

## Overview
- **Base**: Variant A (Incremental Refactor)
- **Incorporated from**: Variant B (Structural Refactor)
- **Changes planned**: 6
- **Changes rejected**: 3
- **Overall risk**: Low (all changes are additive to base)

---

## Planned Changes

### Change #1: Adopt "UNCLASSIFIED" default for Finding.deviation_class

- **Source**: Variant B, Section 7.1 (Finding.deviation_class)
- **Target**: Variant A, Section 7.1 (Finding Model Extension)
- **Rationale**: Variant B's `"UNCLASSIFIED"` default is more semantic than A's `""` (empty string). "UNCLASSIFIED" clearly communicates that the finding predates the classification system. Empty string is ambiguous — does it mean "not classified" or "classification not applicable"? Debate Round 2, X-004: B won this point at 55% confidence.
- **Integration approach**: Replace `deviation_class: str = ""` with `deviation_class: str = "UNCLASSIFIED"`. Add `"UNCLASSIFIED"` to `VALID_DEVIATION_CLASSES`. Remove `""` from valid set. Update `__post_init__` to always validate (remove conditional check).
- **Risk level**: Low (default value change, additive)

### Change #2: Add backward compatibility section with explicit surface enumeration

- **Source**: Variant B, Section 13 (Backward Compatibility)
- **Target**: Variant A, Section 14 (Backward Compatibility) — expand with B's 5-surface analysis
- **Rationale**: Variant B's backward compat section explicitly covers 5 surfaces (pipeline executor, pipeline models, Finding model, gate registry, sprint pipeline). Variant A covers 4 surfaces but lacks sprint pipeline analysis. Debate U-004: B at 65%.
- **Integration approach**: Add subsection "14.5 Sprint Pipeline" confirming the sprint pipeline is unaffected. Add subsection "14.6 Pipeline Executor" confirming no changes to `pipeline/executor.py` or `pipeline/models.py`.
- **Risk level**: Low (documentation only)

### Change #3: Add appendices for quick reference

- **Source**: Variant B, Appendices A-C
- **Target**: Variant A — add 3 appendices after Section 15
- **Rationale**: Appendices provide quick-lookup tables for type signatures, gate definitions, and code references without scrolling through the full spec. This is a presentation improvement, not a content change.
- **Integration approach**: Append:
  - Appendix A: Type Signature Summary (existing models + new fields)
  - Appendix B: Gate Definitions Summary (all gates with tier, checks, blocks-on)
  - Appendix C: Code References (file paths for all affected modules)
- **Risk level**: Low (additive documentation)

### Change #4: Improve terminal halt formatting

- **Source**: Variant B, Section 6.4 (Terminal Halt with Manual-Fix Instructions)
- **Target**: Variant A, Section 8.5 (Terminal Halt Output)
- **Rationale**: Variant B's terminal halt output includes a bulleted "Unfixed findings:" section with per-finding detail. Variant A's format is more generic. Incorporating B's formatting provides more actionable terminal output.
- **Integration approach**: Update `_print_terminal_halt()` to include per-finding unfixed details sourced from the certification report.
- **Risk level**: Low (output formatting only)

### Change #5: Note LoopStep as v2.26 consideration

- **Source**: Variant B, Section 5 (LoopStep Primitive)
- **Target**: Variant A, new subsection in Section 13 (Open Questions Deferred)
- **Rationale**: While LoopStep is not adopted for v2.25 (per the base selection), the concept has merit for v2.26 if the remediate-certify resume pattern proves painful in practice. Recording this consideration prevents re-deriving the design from scratch.
- **Integration approach**: Add deferred open question: "OQ-11: Should a LoopStep primitive replace --resume for remediate-certify? Deferred to v2.26. If --resume proves insufficient for the remediate-certify cycle, a LoopStep primitive (as designed in Variant B of the v2.25 adversarial process) can be added to `pipeline/models.py` and `pipeline/executor.py`."
- **Risk level**: Low (documentation only)

### Change #6: Add `_validation_complete_true` to DEVIATION_ANALYSIS_GATE

- **Source**: Variant B, Section 4.5 (classify-and-validate gate has `validation_complete_true` check)
- **Target**: Variant A, Section 5.5 (DEVIATION_ANALYSIS_GATE)
- **Rationale**: Variant B's gate includes a `_validation_complete_true` semantic check that ensures the validation step actually ran to completion. This is a useful guard — if the LLM produces a partial output with `ambiguous_count: 0` but `validation_complete: false`, the gate should still block. Currently Variant A's gate only checks `ambiguous_count`.
- **Integration approach**: Add `validation_complete` to `DEVIATION_ANALYSIS_GATE` required frontmatter fields. Add `_validation_complete_true()` semantic check function (same implementation as Variant B's). Append to semantic checks list.
- **Risk level**: Low (additive gate hardening)

---

## Changes NOT Being Made

### Rejected #1: Replace 2-step classification with unified classify-and-validate

- **Diff point**: C-001, C-004, X-001, X-003
- **Variant B approach**: Single unified step combining annotation + fidelity + classification
- **Rationale for rejection**: Debate Round 2 rebuttal established that separation of concerns aids debugging. Each step has a bounded, testable responsibility. A monolithic step conflates concerns — if classification is wrong, it's hard to tell whether annotation or fidelity analysis was the cause. A won C-001 (65%), C-004 (65%), X-001 (60%).

### Rejected #2: Add LoopStep primitive to pipeline executor

- **Diff point**: C-002, C-005, X-002
- **Variant B approach**: New `LoopStep` dataclass and `_execute_loop_step()` in generic pipeline layer
- **Rationale for rejection**: Adding ~120 LOC to the generic pipeline layer for a single consumer violates YAGNI. The `--resume` pattern is consistent with existing pipeline UX. No second consumer exists today. A won C-002 (70%), X-002 (65%). Noted as v2.26 consideration (Change #5 above).

### Rejected #3: Defer blast radius analysis to v2.26

- **Diff point**: C-009
- **Variant B approach**: No blast radius analysis in v2.25
- **Rationale for rejection**: Blast radius analysis catches downstream impacts of INTENTIONAL deviations (import chain breaks, type contract changes). Deferring this creates a gap where debate-resolved deviations can silently break integration. A won C-009 (65%).

---

## Risk Summary

| Change | Risk Level | Impact | Rollback |
|--------|-----------|--------|----------|
| #1 UNCLASSIFIED default | Low | Finding model default value | Revert to empty string |
| #2 Backward compat section | Low | Documentation only | Remove section |
| #3 Appendices | Low | Documentation only | Remove appendices |
| #4 Terminal halt formatting | Low | Output formatting | Revert format |
| #5 LoopStep deferred note | Low | Documentation only | Remove OQ-11 |
| #6 validation_complete check | Low | Gate hardening (additive) | Remove semantic check |

---

## Review Status

- Approval: auto-approved
- Timestamp: 2026-03-13T00:00:00Z
