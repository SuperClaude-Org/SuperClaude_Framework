STATUS: FAIL
TOTAL_ISSUES_SOURCE: 6
TOTAL_ISSUES_EXTRACTED: 5

MISSES: ## Consolidated FR/NFR List
TRUNCATIONS: NONE
PHANTOMS: NONE
CONTAMINATIONS: NONE

NOTE ON ISSUE 5 PHANTOM SUBSECTION: The extracted file contains a `### Recommended Approach` subsection under ISSUE 5 with content `[MISSING]`. No `### Recommended Approach` subsection exists under ISSUE 5 in the source file. The source ISSUE 5 has `### Full Analysis` and `### Draft Spec Language` as its subsections; there is no `### Recommended Approach` heading. The `[MISSING]` placeholder was injected by the extraction process for a subsection that does not exist in the source. This is a phantom subsection artifact — not a TRUNCATION (nothing was truncated) and not a CONTAMINATION (no source prose leaked in). Because the placeholder `[MISSING]` contains no actual source content and the subsection does not exist in source, this is classified as a phantom subsection within ISSUE 5, separate from the PHANTOM `##` section category. It does not affect the CORRECTION blocks below (there is nothing to correct: no content was missing from a subsection that exists).

=== CORRECTION FOR: ## Consolidated FR/NFR List ===
Recommended Approach

[No "Recommended Approach" subsection exists in source for this section.]

Draft Spec Language

[No "Draft Spec Language" subsection exists in source for this section.]

SOURCE SECTION VERBATIM CONTENT:

## Consolidated FR/NFR List

The following table lists every new FR and NFR drafted in this brainstorm document. All are
additive to the existing v2.25 spec. Section references indicate where the language should be
inserted.

| Number | Type | Title | Insert Location | Issue |
|--------|------|--------|-----------------|-------|
| FR-056 | FR | `_routing_consistent_with_slip_count()` semantic check function | §5.5, after DEVIATION_ANALYSIS_GATE definition | W-ADV-1 |
| FR-057 | FR | DEVIATION_ANALYSIS_GATE gains third semantic check (`routing_consistent_with_slip_count`) | §5.5, replaces DEVIATION_ANALYSIS_GATE definition | W-ADV-1 |
| FR-058 | FR | `deviations_to_findings()` secondary guard: raise ValueError if fix_ids empty and slip_count > 0 | §7.2, inside deviations_to_findings() listing | W-ADV-1 |
| FR-059 | FR | Spec-patch auto-resume cycle retirement: delete `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, local vars, `auto_accept` param | New §8.7 | W-1 |
| NFR-006 | NFR | Spec-fidelity downgrade: forward compat, behavioral flip, spec-patch dormancy, state file compat (full replacement) | §14.2 (replaces existing text) | W-4+W-5 |
| NFR-011 | NFR | Spec-patch auto-resume cycle not present in v2.25; operators use explicit --resume | New §14.7 | W-1 |
| NFR-012 | NFR | No v2.25 pipeline step reads dev-*-accepted-deviation.md; format consumed only by accept-spec-change CLI | New §14.8 | W-3 |

Additionally, the following spec locations require structural additions (no new FR/NFR numbers):

| Location | Type | Content | Issue |
|----------|------|---------|-------|
| §3.1 (new subsection; renumber 3.1–3.5 → 3.2–3.6) | Taxonomy table | Deviation artifact taxonomy: spec-deviations.md vs dev-*-accepted-deviation.md | W-3 |
| §11.5 (new subsection) | Compatibility table | v2.24.2 → v2.25 executor.py symbol disposition map (RETIRED / UNCHANGED / MODIFIED / NEW) | W-2 |
| §14.7 (new subsection) | Backward-compat note | Spec-patch auto-resume retirement summary and operator migration guidance | W-1 |
| §14.8 (new subsection) | Backward-compat note | Deviation artifact taxonomy cross-reference; NFR-012 | W-3 |

### FR Number Collision Note

The existing spec assigns **FR-054** (§3.5) as the ALL_GATES registry update, and **FR-055**
appears in some spec drafts as a second ALL_GATES-related entry. Before inserting FR-056 through
FR-059 from this brainstorm, the implementor MUST verify the highest existing FR number in the
merged spec and assign the new FRs sequentially from that point. The numbers FR-056 through
FR-059 in this document are provisional and assume FR-054 is the current maximum. If FR-055 is
also used, the new FRs shift to FR-057 through FR-060.

### Summary: Pre-Implementation Actions Required

Before v2.25 implementation begins, the following spec amendments must be merged into
`v2.25-spec-merged.md`:

1. **W-1 (CRITICAL)**: Insert §8.7 (FR-059 retirement) and §14.7 (NFR-011 compat note). Update
   §14.2 (NFR-006 full replacement). Update §11.5 RETIRED rows (FR-059 reference).

2. **W-ADV-1 (CRITICAL)**: Insert `_routing_consistent_with_slip_count()` function (FR-056) and
   update `DEVIATION_ANALYSIS_GATE` definition (FR-057) in §5.5. Add secondary guard to
   `deviations_to_findings()` (FR-058) in §7.2.

3. **W-3 (MAJOR)**: Insert §3.1 taxonomy table (renumber 3.1–3.5 to 3.2–3.6). Insert §14.8
   cross-reference (NFR-012).

4. **W-2 (MAJOR)**: Insert §11.5 compatibility surface table.

5. **W-4+W-5 (MAJOR/MINOR)**: Replace §14.2 with updated NFR-006 text. Confirm FR-059 number
   (spec-patch retirement).

Issues 1 and 2 are CRITICAL and block implementation of executor.py and gates.py respectively.
Issues 3, 4, and 5 are documentation amendments that should be merged before implementation review.
