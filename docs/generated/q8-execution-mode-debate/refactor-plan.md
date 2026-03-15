# Refactoring Plan: Execution Mode Annotation

## Base: Manual (B) with selective imports from Auto (A) and Hybrid (C)

---

## Integration Points

### From Manual (B) -- Base

1. **Roadmap schema extension**: Add optional `execution_mode` field to phase metadata
   - Location: Phase heading or phase metadata block in roadmap markdown
   - Format: `execution_mode: python | claude | default`
   - Default: `claude` (no behavior change if omitted)
   - Risk: Low -- additive, backward-compatible

2. **Generator passthrough**: Tasklist generator reads `execution_mode` from roadmap and propagates to generated phase files
   - Location: `src/superclaude/skills/sc-tasklist-protocol/SKILL.md`, Section 5 (phase parsing)
   - Implementation: Add to phase metadata extraction alongside existing fields (objective, milestone)
   - Risk: Low -- simple field passthrough

3. **Phase file output**: Include `execution_mode` in phase file header metadata table
   - Location: `src/superclaude/skills/sc-tasklist-protocol/templates/phase-template.md`
   - Format: New row in task metadata table
   - Risk: Low -- additive to template

### From Hybrid (C) -- Selective Import

4. **Dry-run advisory** (imported from Hybrid): During `--dry-run`, if a phase has ALL tasks classified EXEMPT and contains backtick shell commands, emit an advisory message:
   ```
   ADVISORY: Phase N appears to be shell-executable. Consider adding
   `execution_mode: python` to the roadmap phase metadata.
   ```
   - This is NOT auto-annotation. It is a suggestion printed to stderr/log.
   - Location: Tasklist generator validation pass
   - Risk: Low -- advisory only, no mutation

5. **Documentation template** (imported from Hybrid): Roadmap templates include `execution_mode` field with inline comment explaining when to use it
   - Location: Roadmap generator output templates
   - Risk: Low -- documentation only

### From Auto (A) -- Deferred

6. **Auto-detection engine**: DEFERRED to Phase 2 (contingent on adoption data)
   - Condition: If >50% of eligible phases go unannotated after 3 release cycles, revisit Auto
   - Design: Same heuristics as proposed, but behind `--auto-execution-mode` flag (opt-in)
   - Risk: Medium -- deferred, no immediate cost

---

## Implementation Tasks

| # | Task | Effort | Risk | Priority |
|---|------|--------|------|----------|
| 1 | Add `execution_mode` field documentation to roadmap format spec | XS | Low | P0 |
| 2 | Update SKILL.md phase parsing to extract `execution_mode` | S | Low | P0 |
| 3 | Update phase-template.md to include `execution_mode` row | XS | Low | P0 |
| 4 | Update index-template.md Phase Files table to show execution_mode | XS | Low | P1 |
| 5 | Add dry-run advisory for likely Python-executable phases | S | Low | P1 |
| 6 | Update roadmap generator templates with execution_mode field | XS | Low | P1 |
| 7 | Add validation: reject invalid execution_mode values | XS | Low | P1 |
| 8 | Document execution_mode in user-facing docs | S | Low | P2 |

**Total effort**: S-M (approximately 2-3 hours)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Users do not discover execution_mode | Medium | Low | Dry-run advisory (Task 5) surfaces the feature |
| Roadmap schema change breaks existing roadmaps | Low | Low | Field is optional, default is `claude` |
| Sprint executor does not consume execution_mode | Medium | Medium | Coordinate with sprint executor implementation |
| Advisory message creates noise | Low | Low | Advisory is stderr-only, suppressed in non-dry-run mode |

---

## Migration Path

1. **Immediate**: Manual annotation works with existing roadmaps (no migration needed)
2. **Short-term**: Dry-run advisory teaches users about the feature
3. **Long-term**: If adoption is low, add opt-in `--auto-execution-mode` flag (deferred Auto)

---

## Success Criteria

1. Roadmap authors can declare `execution_mode: python` and it propagates to generated tasklists
2. Sprint executor respects `execution_mode` when routing phase execution
3. `--dry-run` output includes advisory for likely Python-executable phases
4. No existing roadmaps or tasklists are broken by the change
