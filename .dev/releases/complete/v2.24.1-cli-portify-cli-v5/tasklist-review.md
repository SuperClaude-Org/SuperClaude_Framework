# Template Alignment Tasklist Review

**Reviewer**: Quality Engineer (QA Persona)
**Date**: 2026-03-13
**Files Reviewed**:
- `template-alignment-tasklist.md` (27 tasks)
- `release-spec-template.md` (target template)
- `synthesized-spec.md` (source spec, 903 lines)

---

## Overall Assessment: PASS WITH NOTES

The tasklist is well-structured, comprehensive, and demonstrates strong systematic thinking. It is ready for task-unified execution with the corrections noted below. No findings are blocking; all can be addressed during execution or as a fast-follow patch.

---

## Findings

### HIGH Severity

**H-1: Section 3.8 (Manifest Save) missing from Content Movement Map**

Lines 631-636 of the synthesized spec describe the `--save-manifest` write-only behavior. This content is not listed in the Content Movement Map table (lines 491-509 of the tasklist). The "Verification: Every line range in the current spec maps to a target location. Zero content is deleted." claim is therefore technically false.

**Where it should go**: FR-PORTIFY-WORKFLOW.2 (T-10) acceptance criteria already reference `--save-manifest` indirectly via `to_manifest_markdown()`. The prose from 3.8 should map to either FR-2 description or Section 5.1 CLI Surface (T-18) as a behavioral note. Alternatively, it could be captured in Section 9 Migration as a "new capability" note.

**Risk**: Content loss during execution -- an executor following the map strictly would skip these 6 lines.

**Correction**: Add a row to the Content Movement Map:
```
| Lines 631-636 (Section 3.8) | Manifest save behavior | FR-2 description (T-10) + 5.1 CLI Surface (T-18) |
```

---

**H-2: Section 9 (Effort Estimate) content destination is misleading**

The Content Movement Map says `Lines 871-884 (Section 9) -> 10. Downstream Inputs (T-25)`. However, Section 9 of the synthesized spec contains an **effort estimate table** (phases, hours, files changed). T-25 creates entirely new content about themes, milestones, and task breakdowns -- it does not preserve the effort estimate data.

The effort estimate content has no target location in the aligned spec. The template has no "Effort Estimate" section.

**Risk**: The effort estimate table (which contains useful planning data) will be silently dropped, violating the 100% content preservation guarantee.

**Correction**: Either:
1. Add the effort estimate to Appendix B as a reference document, OR
2. Include it in Section 10 (Downstream Inputs) as a subsection "### Effort Baseline", OR
3. Explicitly document this as an accepted content exclusion with rationale (effort estimates are execution artifacts, not spec content).

---

### MEDIUM Severity

**M-1: Footer metadata (lines 900-903) not in Content Movement Map**

The synthesized spec ends with:
```
*Synthesized spec completed: 2026-03-13*
*Base: Approach A (score 7.95) + selected elements from Approach B*
*Adversarial debate orchestrator: Opus 4.6*
```

These lines are not mapped. T-02 mentions moving "synthesis provenance metadata (Base, Incorporated from)" to Appendix B, but that refers to lines 6-7, not the footer. The footer provenance is a separate instance.

**Correction**: Add to Content Movement Map pointing to Appendix B: References (T-27). The footer metadata is provenance that belongs in the reference table.

---

**M-2: Template Section 5.2 Gate Criteria -- table format mismatch**

The template defines Gate Criteria with a specific table format:
```
| Step | Gate Tier | Frontmatter | Min Lines | Semantic Checks |
```

T-19 proposes prose text ("Gate criteria are unchanged from v2.24...") instead of the template's table format. While the content is correct (no gate changes), the structural format deviates from the template.

**Correction**: Either:
1. Use the template table format with a single row stating "No changes", OR
2. Keep the prose but add a note: "See v2.24 spec for full gate criteria table."

This is acceptable as-is since the template's conditional marker `[CONDITIONAL: portification]` means it should be included, but a "no changes" statement is a valid way to include it.

---

**M-3: Template Section 5.3 Phase Contracts -- YAML block expected**

The template expects a YAML code block for phase contracts. T-20 provides prose instead. Same situation as M-2 -- no contract schema changes, but the template expects structural conformance.

**Correction**: Same approach as M-2. Either include a minimal YAML block referencing v2.24 contracts or keep the prose with explicit template-deviation justification.

---

**M-4: T-04 (Scope Boundary) sources are partially ambiguous**

T-04 says "extract from current Section 7 Edge Cases and overall design scope" but does not specify which edge cases map to in-scope vs. out-of-scope. The proposed content in T-04 looks correct, but an executor unfamiliar with the domain might struggle to verify which edge cases (7.1-7.7) contributed to which scope boundary items.

**Correction**: Add explicit line references: "Source: Section 7.5 (lines 844-846) -> out of scope item 1; Section 7.3 (lines 837-838) -> out of scope item 2; etc."

---

**M-5: T-16 (Data Models) is the heaviest task but lacks specificity**

T-16 is acknowledged as "the heaviest content move -- ~200 lines of Python code" but provides no specific line ranges for what moves. It lists source sections (3.3, 3.5, 3.6) but not exact line ranges or which code blocks to extract.

**Correction**: Add explicit source ranges:
- Section 3.3 lines 214-439 (ComponentTree and all dataclasses)
- Section 3.5 lines 513-560 (PortifyConfig changes)
- Section 3.6 lines 577-602 (ValidateConfigResult, error codes)

This is important because the same source sections also feed other tasks (T-09, T-10, T-11, T-13), and an executor needs to know which parts go where vs. which parts are referenced in multiple locations.

---

### LOW Severity

**L-1: Quality scores in T-01 frontmatter use wrong scale**

T-01 sets quality scores to `0.0` with a note that they'll be populated later. The template uses `{{SC_PLACEHOLDER:0.0_to_10.0}}` indicating a 0-10 scale. T-01's proposed values are correct (0.0 as placeholder), but the note should clarify the scale is 0.0-10.0, not 0.0-1.0 (which would match `complexity_score`).

**Correction**: Minor -- add "(scale: 0.0-10.0)" to the T-01 notes.

---

**L-2: T-12 and T-13 lack proposed table content**

T-12 (New Files) and T-13 (Modified Files) say "Reformat into template table with Purpose and Dependencies columns" and "Reformat into template table with Change and Rationale columns" respectively, but don't show the proposed table content. All other tasks include explicit proposed content.

**Risk**: Low -- the source content is clear and the template format is unambiguous. But for consistency with other tasks, showing the expected output would reduce executor ambiguity.

---

**L-3: T-22 Risk Assessment table column mismatch**

T-22 says "Verify table format matches template (Risk | Probability | Impact | Mitigation)." The current synthesized spec already uses this exact format (line 860-861), so the verification will trivially pass. The task could be simplified to "Renumber from 8 to 7; no content changes needed."

---

**L-4: Section numbering gap in Content Movement Map for Section 3**

The Content Movement Map lists Section 3 subsections up to 3.7 but skips 3.8 (as noted in H-1). The line ranges also have a small gap: Section 3.7 ends at line 635, Section 3.8 starts at line 631 (overlapping). The actual content shows 3.7 ends at line 635 and 3.8 begins at line 631. This appears to be a line-range estimation issue -- 3.8 actually starts at line 631.

**Correction**: Verify line ranges. Section 3.7 runs lines 604-635 (the `discover_components` changes end with the YAML frontmatter block). Section 3.8 runs lines 631-636. There is overlap because the YAML block in 3.7 ends around line 629, and 3.8's heading is on line 631. The Content Movement Map's line 604-635 for Section 3.7 is approximately correct.

---

## Dependency and Ordering Analysis

The phase ordering is sound:

1. **Phase 1 (Frontmatter)**: Independent. No content dependencies.
2. **Phase 2 (Problem Statement)**: Independent. Additive to existing content.
3. **Phase 3 (Solution Overview)**: Independent. Reformats existing content.
4. **Phase 4 (Functional Requirements)**: Depends on understanding Section 3, but not on prior phase outputs.
5. **Phase 5 (Architecture)**: Draws from same Section 3 source as Phase 4 -- **potential conflict** if Phase 4 has already moved/transformed content in the working file. However, since this is a restructure of the output document (not modifying the source), phases operate on different output sections.
6. **Phase 6 (Interface Contracts)**: Depends on content already identified in Phase 4 (CLI changes).
7. **Phase 7 (NFRs)**: Independent -- extracts from scattered sources.
8. **Phase 8 (Renumbering)**: Must execute after Phases 4-7 have created Sections 3-6, to avoid number conflicts.
9. **Phase 9 (Missing Sections)**: Must execute last -- creates new sections that reference earlier content.

**Ordering verdict**: Correct. No circular dependencies. Phase 8 correctly follows Phase 7.

---

## Execution Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Content duplication (same source used by multiple tasks) | Medium | Low | Tasks reference the same source but place content in different structural locations. Acceptable for a template alignment. |
| Large T-16 task causes errors | Medium | Medium | Break into sub-tasks if executor struggles. The ~200 lines of Python code are well-defined dataclass blocks. |
| Executor misinterprets "keep existing" instructions | Low | Medium | T-05, T-07, T-08 say "keep" existing content. Executor must understand these mean "preserve in place, add new subsections around it." |
| Section renumbering in Phase 8 causes reference drift | Low | Low | Internal cross-references (e.g., "See Section 3") need updating. Not explicitly called out in any task. |

---

## Summary of Required Corrections

| Finding | Severity | Action |
|---------|----------|--------|
| H-1: Section 3.8 missing from map | HIGH | Add Content Movement Map row |
| H-2: Effort estimate content dropped | HIGH | Decide destination or document exclusion |
| M-1: Footer metadata unmapped | MEDIUM | Add to Appendix B mapping |
| M-2: Gate Criteria format mismatch | MEDIUM | Acceptable as-is; note deviation |
| M-3: Phase Contracts format mismatch | MEDIUM | Acceptable as-is; note deviation |
| M-4: T-04 source ambiguity | MEDIUM | Add line references |
| M-5: T-16 lacks line ranges | MEDIUM | Add explicit source line ranges |
| L-1: Quality score scale | LOW | Clarify in notes |
| L-2: T-12/T-13 lack proposed content | LOW | Optional -- add for consistency |
| L-3: T-22 trivial verification | LOW | Simplify task description |
| L-4: Line range overlap | LOW | Verify and correct |

---

## Recommendation

**Ready for task-unified execution**: YES, with pre-execution patch.

Before dispatching to task-unified, apply these two corrections (HIGH severity):

1. Add the Section 3.8 row to the Content Movement Map
2. Decide on the effort estimate content destination (recommend Appendix B or an explicit exclusion note)

All MEDIUM findings can be addressed during execution by an informed executor. The LOW findings are cosmetic.

The tasklist demonstrates thorough analysis, correct dependency ordering, and specific enough instructions for each task. The Content Movement Map is the strongest quality feature -- it enables post-execution verification that nothing was lost.
