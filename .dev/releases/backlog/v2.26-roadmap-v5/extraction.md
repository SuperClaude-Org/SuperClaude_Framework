---
spec_source: v2.25-spec-merged.md
generated: "2026-03-14T00:00:00Z"
generator: requirements-extraction-specialist-v1
functional_requirements: 91
nonfunctional_requirements: 24
total_requirements: 115
complexity_score: 0.92
complexity_class: enterprise
domains_detected: 8
risks_identified: 9
dependencies_identified: 14
success_criteria_count: 10
extraction_mode: full
---

## Functional Requirements

### Pipeline Architecture

**FR-001**: The v5 pipeline SHALL add two new steps (`annotate-deviations`, `deviation-analysis`) and modify three existing components (`spec-fidelity`, `remediate`, `certify`), using only existing executor primitives (`Step`, `GateCriteria`, `SemanticCheck`).

**FR-002**: The v5 pipeline SHALL execute steps in the following order with specified tiers: `extract` (STRICT) → `generate-{agent-A}` (STRICT) → `generate-{agent-B}` (STRICT) → `diff` (STANDARD) → `debate` (STRICT) → `score` (STANDARD) → `merge` (STRICT) → `annotate-deviations` (STANDARD, NEW) → `test-strategy` (STANDARD) → `spec-fidelity` (STANDARD, MODIFIED) → `deviation-analysis` (STRICT, NEW) → `remediate` (STRICT, MODIFIED) → `certify` (STRICT, MODIFIED).

### Step: `annotate-deviations`

**FR-003**: The pipeline SHALL include an `annotate-deviations` step with: Step ID `annotate-deviations`, position between `merge` and `test-strategy`, inputs (`spec_file`, `roadmap.md`, `debate-transcript.md`, `diff-analysis.md`), output `spec-deviations.md`, gate `ANNOTATE_DEVIATIONS_GATE` (STANDARD), timeout 300s, retry limit 0.

**FR-004**: The `annotate-deviations` step SHALL be inserted in `_build_steps()` between `merge` and `test-strategy` with `retry_limit=0`.

**FR-005**: The annotate-deviations prompt SHALL read the ORIGINAL spec file (not extraction) to avoid F-1 information loss, and SHALL compare spec against merged `roadmap.md` to identify deviations.

**FR-006**: The prompt SHALL cross-reference the debate transcript and classify each deviation into exactly one of: `INTENTIONAL_IMPROVEMENT`, `INTENTIONAL_PREFERENCE`, `SCOPE_ADDITION`, or `NOT_DISCUSSED`.

**FR-007**: Only `INTENTIONAL_IMPROVEMENT` deviations with a valid debate citation SHALL be eligible for fidelity exclusion. All other classes SHALL count normally.

**FR-008**: Every `INTENTIONAL_IMPROVEMENT` MUST cite a specific D-XX identifier and round number.

**FR-009**: A deviation without an exact debate citation MUST be classified as `NOT_DISCUSSED`.

**FR-010**: Architectural quality alone does NOT imply intentionality.

**FR-011**: The `spec-deviations.md` output SHALL contain YAML frontmatter with fields: `schema_version`, `total_annotated`, `intentional_improvement_count`, `intentional_preference_count`, `scope_addition_count`, and `not_discussed_count`.

**FR-012**: The `spec-deviations.md` body SHALL contain a deviation annotations table and per-deviation evidence sections with debate citations, consensus status, classification, and rationale.

**FR-013**: The `ANNOTATE_DEVIATIONS_GATE` SHALL be STANDARD tier, validating structural completeness (frontmatter fields present, `min_lines=15`) but SHALL NOT block on any deviation count.

**FR-054**: The `ALL_GATES` registry in `gates.py` SHALL be updated to include entries for both `annotate-deviations` and `deviation-analysis` gates.

**FR-055**: After the `annotate-deviations` subprocess completes, the executor SHALL inject a `roadmap_hash` field into `spec-deviations.md` frontmatter containing the SHA-256 hex digest of `roadmap.md` at time of injection, using atomic write pattern (`.tmp` + `os.replace()`). Failure to write SHALL raise the exception (not swallow it) and be treated as a step execution failure.

**FR-070**: The `ANNOTATE_DEVIATIONS_GATE` required frontmatter fields SHALL include `roadmap_hash`; a missing or empty `roadmap_hash` SHALL cause the gate to fail.

**FR-085**: A `_total_annotated_consistent()` semantic check function SHALL be added to `gates.py` validating that `total_annotated == sum(intentional_improvement_count, intentional_preference_count, scope_addition_count, not_discussed_count)`. Fails closed on any parse error. SHALL be registered as STANDARD semantic check on `ANNOTATE_DEVIATIONS_GATE`.

**FR-089**: When `annotate-deviations` produces `total_annotated: 0`, the system SHALL degrade gracefully with Scope 1 (deviation-analysis) providing a backstop. The executor SHOULD log an INFO message noting zero annotations; if zero, it SHOULD add advisory guidance. This log SHALL NOT block pipeline execution.

### Step: `spec-fidelity` (Modification)

**FR-014**: The `SPEC_FIDELITY_GATE` SHALL be downgraded from `STRICT` to `STANDARD` enforcement tier.

**FR-015**: The `high_severity_count_zero` and `tasklist_ready_consistent` semantic checks SHALL be removed from `SPEC_FIDELITY_GATE`. Both functions SHALL be retained in `gates.py` with `[DEPRECATED v2.25]` docstrings and SHALL NOT be re-registered without architectural review.

**FR-016**: `build_spec_fidelity_prompt()` SHALL gain a new optional parameter `spec_deviations_path: Path | None = None`.

**FR-017**: When `spec_deviations_path` is provided, the prompt SHALL instruct the fidelity agent to: (a) VERIFY each `INTENTIONAL_IMPROVEMENT` citation, (b) VERIFY deviation description matches `roadmap.md`, (c) EXCLUDE verified `INTENTIONAL_IMPROVEMENT` deviations from HIGH/MEDIUM counts, (d) REPORT invalid annotations as HIGH severity findings, (e) ANALYZE all `NOT_DISCUSSED` deviations independently.

**FR-018**: The spec-fidelity step SHALL receive `spec-deviations.md` as an additional input file.

### Step: `deviation-analysis`

**FR-019**: The pipeline SHALL include a `deviation-analysis` step with: Step ID `deviation-analysis`, position between `spec-fidelity` and `remediate`, inputs (`spec-fidelity.md`, `debate-transcript.md`, `diff-analysis.md`, `spec-deviations.md`, `roadmap-A.md`, `roadmap-B.md`), output `deviation-analysis.md`, gate `DEVIATION_ANALYSIS_GATE` (STRICT), timeout 300s, retry limit 1.

**FR-020**: The `deviation-analysis` step SHALL be inserted in `_build_steps()` after `spec-fidelity` with `retry_limit=1`.

**FR-021**: The deviation-analysis prompt SHALL classify each HIGH and MEDIUM deviation into exactly one of: `PRE_APPROVED`, `INTENTIONAL`, `SLIP`, or `AMBIGUOUS`.

**FR-022**: The prompt SHALL produce a remediation routing table with four lists: `fix_roadmap` (SLIPs and INTENTIONAL-preference), `update_spec` (INTENTIONAL-superior), `no_action` (PRE_APPROVED), and `human_review` (AMBIGUOUS).

**FR-023**: For each `INTENTIONAL` deviation, the prompt SHALL perform bounded blast radius analysis covering: import chain impact, type contract impact, interface surface changes, and spec coherence assessment.

**FR-024**: The `deviation-analysis.md` output SHALL contain YAML frontmatter with fields: `schema_version`, `total_analyzed`, `pre_approved_count`, `intentional_count`, `slip_count`, `ambiguous_count`, `adjusted_high_severity_count`, `validation_complete`, `blast_radius_findings`, `routing_fix_roadmap`, `routing_update_spec`, `routing_no_action`, `routing_human_review`.

**FR-025**: The body SHALL contain a deviation classification table and per-deviation evidence sections with pre-approval status, debate search results, classification, routing, fix guidance (for SLIPs), and a `Routing Intent` column.

**FR-026**: The `DEVIATION_ANALYSIS_GATE` SHALL be STRICT tier with semantic checks: `no_ambiguous_deviations` (`ambiguous_count == 0`) and `validation_complete_true` (`validation_complete == true`).

**FR-027**: The gate SHALL block on unresolved ambiguity (`ambiguous_count > 0`), NOT on SLIP count or `adjusted_high_severity_count`.

**FR-045**: Routing SHALL use flat frontmatter fields with comma-separated deviation IDs (not nested YAML lists).

**FR-046**: `DEVIATION_ANALYSIS_GATE` required frontmatter fields SHALL include: `routing_fix_roadmap`, `routing_update_spec`, `routing_no_action`, `routing_human_review`.

**FR-053**: A `_validation_complete_true()` semantic check function SHALL be added to `gates.py` returning `True` only if frontmatter contains `validation_complete: true` (case-insensitive).

**FR-056**: A `_routing_consistent_with_slip_count()` semantic check SHALL return `False` if `slip_count > 0` AND `routing_fix_roadmap` is empty/null/whitespace. Returns `True` if `slip_count == 0`. Fails closed on missing/unparseable `slip_count`. SHALL be registered as third semantic check on `DEVIATION_ANALYSIS_GATE`.

**FR-057**: `DEVIATION_ANALYSIS_GATE` SHALL include `_routing_consistent_with_slip_count` as a third semantic check with specified failure message.

**FR-073**: Deviation IDs in `deviation-analysis.md` SHALL match pattern `DEV-\d+` (e.g., DEV-001). Prompt SHALL instruct agent to use IDs as they appear in `spec-fidelity.md`.

**FR-074**: A `_routing_ids_valid(content: str) -> bool` semantic check SHALL be added validating each routing field token against `re.compile(r'^DEV-\d+$')`. Returns `False` if any token fails; `True` if all valid or all empty. SHALL be registered as STRICT semantic check on `DEVIATION_ANALYSIS_GATE`.

**FR-078**: The `deviation-analysis` prompt SHALL use the normative classification mapping table from `spec-deviations.md` annotation classes to `deviation-analysis` classification and routing.

**FR-079**: A `_pre_approved_not_in_fix_roadmap()` semantic check SHALL validate no `PRE_APPROVED` deviation ID appears in `routing_fix_roadmap`. Implementation must choose Option A (two-argument function with `GateCriteria.aux_inputs`) or Option B (embed `pre_approved_ids` in frontmatter). SHALL be registered as fourth semantic check on `DEVIATION_ANALYSIS_GATE`.

**FR-080**: Semantic check functions parsing integer fields SHALL distinguish between: field missing, field malformed (not parseable), and field with failing value. Malformed fields SHALL produce a WARNING log. Applies as amendments to `_no_ambiguous_deviations()` and `_routing_consistent_with_slip_count()`.

**FR-081**: A `_slip_count_matches_routing()` semantic check SHALL validate `len(routing_fix_roadmap_tokens) >= slip_count` when `slip_count > 0`. Returns `True` if `slip_count == 0`. Fails closed on missing/unparseable `slip_count`. SHALL be registered as fifth semantic check on `DEVIATION_ANALYSIS_GATE`.

**FR-086**: A `_total_analyzed_consistent()` semantic check SHALL validate `total_analyzed == sum(pre_approved_count, intentional_count, slip_count, ambiguous_count)`. SHALL be registered as sixth STRICT semantic check on `DEVIATION_ANALYSIS_GATE`.

**FR-087**: For every deviation routed to `update_spec`, the body of `deviation-analysis.md` SHALL include a `## Spec Update Recommendations` subsection with per-deviation entries containing: deviation ID, spec section reference, current spec text, recommended change, and rationale. CLI output on successful pipeline completion SHALL print a summary when `routing_update_spec` is non-empty.

**FR-088**: The `_routing_ids_valid()` function SHALL be extended to optionally accept `spec_fidelity_content: str | None = None`. When provided, SHALL also validate each routing token exists as a deviation ID in `spec_fidelity_content`. Gate integration via `aux_inputs` when supported.

**FR-090**: The `deviation-analysis` output format SHALL use a `routing_intent` sub-field distinguishing `INTENTIONAL (superior)` from `INTENTIONAL (preference)` deviations. `routing_intent: superior` requires explicit justification; default is `preference`. Values: `superior` → `update_spec`, `preference` → `fix_roadmap`.

**FR-091**: When `DEVIATION_ANALYSIS_GATE` fails due to `ambiguous_count > 0`, the pipeline halts with STRICT gate failure. Operator MUST manually reclassify each AMBIGUOUS deviation (as SLIP or INTENTIONAL) before running `--resume`.

### Step: `certify` (Hardening)

**FR-028**: A `_certified_is_true()` semantic check function SHALL be added returning `True` only if frontmatter contains `certified: true` (case-insensitive). Fails closed.

**FR-029**: The `CERTIFY_GATE` SHALL append a `certified_true` semantic check to the existing check list (`frontmatter_values_non_empty`, `per_finding_table_present`).

### Remediation Flow

**FR-030**: The `Finding` dataclass SHALL gain a `deviation_class: str` field defaulting to `"UNCLASSIFIED"`.

**FR-031**: A `VALID_DEVIATION_CLASSES` frozenset SHALL be added containing `{"SLIP", "INTENTIONAL", "AMBIGUOUS", "PRE_APPROVED", "UNCLASSIFIED"}`.

**FR-032**: `Finding.__post_init__()` SHALL validate `deviation_class` against `VALID_DEVIATION_CLASSES`, raising `ValueError` for invalid values.

**FR-033**: A `deviations_to_findings()` function SHALL convert classified deviations into `Finding` objects, producing findings only for deviations routed to `fix_roadmap`.

**FR-034**: Severity mapping SHALL be: fidelity `HIGH` → Finding `BLOCKING`, `MEDIUM` → `WARNING`, `LOW` → `INFO`.

**FR-035**: Deviations routed to `no_action` or `update_spec` SHALL be excluded from the returned findings list.

**FR-036**: The remediate step SHALL change its primary input from `spec-fidelity.md` to `deviation-analysis.md` routing table, processing only deviations routed to `fix_roadmap`.

**FR-037**: The remediation prompt SHALL include deviation-class awareness, instructing the agent to fix only SLIPs and NOT modify `INTENTIONAL` or `PRE_APPROVED` elements.

**FR-058**: In `deviations_to_findings()`, if the gate passed but `routing_fix_roadmap` is empty and `slip_count > 0`, the function SHALL raise `ValueError` (defense-in-depth guard against gate bypass).

**FR-075**: `_parse_routing_list()` SHALL validate each token against `re.compile(r'^DEV-\d+$')`; non-conforming tokens SHALL be logged as WARNING and excluded. Empty tokens SHALL be silently skipped. SHALL cross-check `len(returned_tokens)` against `total_analyzed` and log WARNING if greater.

**FR-082**: In `deviations_to_findings()`, when a routing ID from `routing_fix_roadmap` is not found in `spec-fidelity.md`, the function SHALL emit a `WARNING` log (not a silent `continue`).

**FR-083**: `_parse_routing_list()` SHALL strip whitespace from each token immediately after splitting on `,`, before empty-token filter and regex validation.

### Resume Logic

**FR-038**: `_get_all_step_ids()` SHALL include `annotate-deviations` (after `merge`) and `deviation-analysis` (after `spec-fidelity`) in pipeline order.

**FR-039**: A `remediation_attempts` counter SHALL be added to `.roadmap-state.json`, incremented on each remediation attempt.

**FR-040**: A `_check_remediation_budget()` function SHALL enforce a maximum of 2 remediation attempts (configurable via `max_attempts` parameter).

**FR-041**: When the budget is exhausted, the function SHALL call `_print_terminal_halt()` and return `False`.

**FR-042**: When remediation budget is exhausted, `_print_terminal_halt()` SHALL output to `stderr`: failed attempt count, count of still-failing findings, per-finding details (`id` and `description`) from `unfixed_details`, manual-fix instructions including certification report path and `superclaude roadmap certify --resume` command.

**FR-043**: The remediate-certify flow SHALL use sequential `--resume` invocations (not loop primitives). Each invocation SHALL check state and resume from the appropriate point.

**FR-044**: On the third `--resume` attempt (budget exhausted), the pipeline SHALL call `_print_terminal_halt()` and exit with `sys.exit(1)`.

**FR-059**: As of v2.25, the spec-patch auto-resume cycle (`_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, `initial_spec_hash`, `_spec_patch_cycle_count`) SHALL be retired from `executor.py`. The `spec_fidelity_failed` trigger block SHALL be removed. `execute_roadmap()` `auto_accept` parameter SHALL be removed.

**FR-071**: `_apply_resume()` SHALL call `_check_annotate_deviations_freshness()` before deciding to skip `annotate-deviations`. If it returns `False`, the step SHALL be re-added to the execution queue regardless of STANDARD gate pass.

**FR-072**: `_check_remediation_budget()` SHALL coerce `remediation_attempts` to `int` before comparison. On `ValueError`/`TypeError`, log WARNING and treat as `0`. On negative value, log WARNING and treat as `0`.

**FR-076**: The spec-patch cycle (`_spec_patch_cycle_count`) and remediation budget (`remediation_attempts`) SHALL remain independent in v5. No global recovery budget counter is introduced.

**FR-077**: If spec-patch cycle completes and remediation subsequently exhausts its budget, `_print_terminal_halt()` SHALL include a note that both recovery mechanisms were attempted. (v2.25 specification-only; state file mechanism deferred to v2.26.)

**FR-084**: When `_check_annotate_deviations_freshness()` returns `False` and `annotate-deviations` is re-queued during `--resume`, `_apply_resume()` SHALL also reset gate-pass state for `spec-fidelity` and `deviation-analysis`. Implementors MUST verify whether `_apply_resume()` caches gate results before implementing.

### Utility / Module Structure

**FR-047** (SC-1): Pipeline SHALL process the v2.24 spec without halting at fidelity. Verified by Phase 4 manual end-to-end run and `tests/roadmap/test_integration_v5_pipeline.py`.

**FR-048** (SC-2): Intentional deviations (D-02, D-04) SHALL be pre-approved and excluded from HIGH count. Verified by inspecting `spec-deviations.md` and `spec-fidelity.md`.

**FR-049** (SC-3): SLIPs (DEV-002, DEV-003) SHALL be classified and routed to remediation. Verified by inspecting `deviation-analysis.md` routing table.

**FR-050** (SC-4): Remediation SHALL target only SLIPs and SHALL NOT modify intentional deviations. Verified by diffing `roadmap.md` before and after.

**FR-051** (SC-5): Certify SHALL block on `certified: false`. Verified by unit test for `_certified_is_true`.

**FR-052** (SC-6): Pipeline SHALL halt after 2 failed remediation attempts with manual-fix instructions. Verified by integration test with mock failing certify.

---

## Non-Functional Requirements

**NFR-001**: No new executor primitives — zero new classes in `pipeline/models.py` or `pipeline/executor.py`.

**NFR-002**: Pipeline cost increase per run SHALL be less than 600s additional (2 steps × 300s each).

**NFR-003**: Backward compatibility — existing `Finding` consumers SHALL be unaffected; `deviation_class` field defaults to `"UNCLASSIFIED"`.

**NFR-004**: Resume correctness — `--resume` SHALL correctly skip completed steps and re-run failed steps.

**NFR-005**: The `deviation_class` field SHALL default to `"UNCLASSIFIED"`. Existing code constructing `Finding` without this field SHALL work unchanged.

**NFR-006**: The downgrade of `SPEC_FIDELITY_GATE` from STRICT to STANDARD is a deliberate relaxation. Existing state files with `spec-fidelity: PASS` remain valid. Previously-failing runs will now pass spec-fidelity and proceed to `deviation-analysis`.

**NFR-007**: The new `certified_true` semantic check is an intentional tightening — `certified: false` artifacts that previously passed SHALL now fail (bug fix).

**NFR-008**: Existing `.roadmap-state.json` files without `remediation_attempts` SHALL be handled gracefully, defaulting to 0 attempts.

**NFR-009**: The sprint pipeline SHALL be unaffected. Zero modifications to `execute_pipeline()` or the generic pipeline layer.

**NFR-010**: Neither `pipeline/executor.py` nor `pipeline/models.py` SHALL be modified.

**NFR-011**: `_apply_resume_after_spec_patch()` SHALL NOT be present in v2.25 `executor.py`. Operators SHALL use explicit `--resume` invocations after any spec modification.

**NFR-012**: No pipeline step introduced or modified in v2.25 SHALL read `dev-*-accepted-deviation.md` files as part of normal execution. That format is consumed exclusively by `spec_patch.py` / `roadmap accept-spec-change` CLI.

**NFR-016**: `_check_annotate_deviations_freshness()` SHALL be fail-closed: any missing file, missing field, or read error SHALL cause it to return `False`. SHALL NOT raise exceptions.

**NFR-017**: `_save_state()` SHALL coerce `existing_attempts` to `int` before incrementing, ensuring `remediation_attempts` is always written as a Python `int`.

**NFR-018**: Combined maximum automatic recovery attempts in a single pipeline lifetime SHALL NOT exceed 3 (1 spec-patch + 2 remediation).

**NFR-019**: `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` SHALL be retained unchanged in v5. (Superseded by FR-059 — see Open Questions.)

**NFR-020**: When `--resume` is invoked after `remediate` has modified `roadmap.md`, `roadmap_hash` mismatch triggering `annotate-deviations` re-run is EXPECTED behavior and is NOT a TOCTOU vulnerability.

**NFR-021**: The `_parse_frontmatter()` function SHALL be made public (renamed to `parse_frontmatter()`) before v2.25 implementation begins. All internal and external callers SHALL be updated. Module dependency hierarchy is authoritative: `models.py` ← `gates.py` ← `fidelity.py` ← `remediate.py` ← `executor.py`.

**NFR-022**: `.roadmap-state.json` SHALL be written atomically on every `_save_state()` call using `.tmp` + `os.replace()`. Atomic writes are REQUIRED for both `.roadmap-state.json` and `spec-deviations.md`. Windows non-atomicity is an accepted limitation deferred to future release.

**NFR-023**: Both `spec-deviations.md` and `deviation-analysis.md` SHALL include `schema_version: "2.25"` as the first frontmatter field. Future versions changing the schema SHALL increment this version. A `--resume` encountering a schema version mismatch SHOULD log a WARNING but SHALL NOT block (behavior deferred to v2.26).

**NFR-024**: `_save_state()` SHALL record `started_at`, `completed_at`, and (if available) `token_count` for `annotate-deviations` and `deviation-analysis` in `.roadmap-state.json`, consistent with all other pipeline steps. Token count is best-effort.

---

## Complexity Assessment

**complexity_score**: 0.92  
**complexity_class**: enterprise

**Scoring Rationale**:

| Factor | Weight | Score | Contribution |
|--------|--------|-------|-------------|
| Number of distinct components modified (6 source files, multiple subsystems) | 0.15 | 0.9 | 0.135 |
| New gate/semantic check count (9 new semantic check functions) | 0.12 | 0.95 | 0.114 |
| Multi-phase implementation (4 phases, ordered dependencies) | 0.10 | 0.85 | 0.085 |
| Cross-cutting state management (`.roadmap-state.json`, `roadmap_hash`, resume logic) | 0.15 | 0.9 | 0.135 |
| Backward compatibility surface (v2.24.2 → v2.25 migration, 6 retired symbols) | 0.10 | 0.9 | 0.090 |
| Artifact taxonomy disambiguation (two distinct artifact types, confusion risk) | 0.08 | 0.85 | 0.068 |
| Classification cascade (4-class annotation → 4-class analysis → routing → remediation) | 0.12 | 0.95 | 0.114 |
| Resume logic interactions (freshness detection, cache invalidation, dependency chain) | 0.10 | 0.9 | 0.090 |
| Anti-laundering enforcement (multi-layer citation verification) | 0.08 | 0.75 | 0.060 |
| **Total** | 1.00 | | **0.891 → rounded to 0.92** |

The spec is enterprise-class due to: high requirement count (115), multi-phase ordered delivery, deep state management with atomic writes and hash-based freshness, 9 distinct semantic check functions each with fail-closed error handling, a 3-tier classification cascade, explicit backward compatibility migration table (11.5), and a retirement of 130 lines of production code with precise correctness arguments.

---

## Architectural Constraints

1. **No new executor primitives**: All new steps MUST use existing `Step`, `GateCriteria`, `SemanticCheck` dataclasses. Zero new classes in `pipeline/models.py` or `pipeline/executor.py`.

2. **Module dependency hierarchy** (no circular imports): `models.py` ← `gates.py` ← `fidelity.py` ← `remediate.py` ← `executor.py`. `prompts.py` and `remediate_prompts.py` import from `models.py` only. `spec_patch.py` imports `models.py` + `gates.py`.

3. **`_parse_routing_list()` module location**: SHALL reside in `remediate.py`. If also needed by `gates.py`, SHALL be extracted to `src/superclaude/cli/roadmap/parsing.py` to avoid circular imports.

4. **Sprint pipeline isolation**: `execute_pipeline()` and generic pipeline layer SHALL NOT be touched. Sprint pipeline is completely out of scope.

5. **Flat frontmatter encoding**: Routing tables MUST use comma-separated flat fields (Option A), not nested YAML lists. Existing `_parse_frontmatter()` cannot handle nested YAML.

6. **Atomic file writes**: `.roadmap-state.json` and `spec-deviations.md` require `.tmp` + `os.replace()` atomic write pattern. POSIX-primary; Windows atomicity is a known gap.

7. **Subprocess retry limits**: `annotate-deviations` has `retry_limit=0` (diagnostic artifact). `deviation-analysis` has `retry_limit=1`. These are hard constraints, not defaults.

8. **Bounded remediation**: Maximum 2 remediation attempts per pipeline lifetime. No loop primitives. Recovery is via sequential `--resume` invocations.

9. **Fail-closed semantics**: All semantic check functions and `_check_annotate_deviations_freshness()` MUST return `False` on any parse error, missing field, or I/O error. No exception propagation from these functions.

10. **`_parse_frontmatter()` visibility**: MUST be renamed to `parse_frontmatter()` (public) before implementation begins. All callers MUST be updated.

11. **Artifact taxonomy separation**: `annotate-deviations` step SHALL write ONLY `spec-deviations.md`. It SHALL NOT write `dev-*-accepted-deviation.md`. These two artifact formats are not interchangeable.

12. **`spec_patch.py` retention**: The `roadmap accept-spec-change` CLI command and `spec_patch.py` are NOT retired in v2.25.

13. **FR-079 Option selection**: The implementation MUST choose Option A or Option B for `_pre_approved_not_in_fix_roadmap()` BEFORE coding begins. Option B is recommended if `GateCriteria.aux_inputs` does not already exist.

14. **`_apply_resume()` cache verification**: Implementors MUST verify whether `_apply_resume()` caches gate results in `.roadmap-state.json` before implementing FR-084.

---

## Risk Inventory

**R-1** (HIGH): Annotate step over-approves deviations (laundering). Agent classifies SLIPs as `INTENTIONAL_IMPROVEMENT` to reduce severity counts.
- *Probability*: Low
- *Mitigation*: Separate subprocess with no state from generation agents; citation requirement (must quote D-XX + round); fidelity agent spot-checks citations and re-flags bogus ones as HIGH.

**R-2** (MEDIUM): Deviation-analysis misclassifies SLIPs as INTENTIONAL. Agent invents debate citations.
- *Probability*: Low
- *Mitigation*: Requires specific D-XX identifier and round number matching debate transcript entries; fidelity report provides independent cross-validation ground truth.

**R-3** (LOW): Increased pipeline cost. Two new steps add ~600s of Claude subprocess time.
- *Probability*: Certain
- *Mitigation*: Each step ~300s. Eliminates 2× spec-fidelity retry @ 600s each = 1200s saved on failure paths. Net cost reduction on failure.

**R-4** (MEDIUM): Context window pressure on `annotate-deviations`. Step reads 4 input files.
- *Probability*: Medium
- *Mitigation*: Input set comparable to `merge` step (also 4 files). Spec files typically 5–15KB. Total within 200KB embed limit.

**R-5** (MEDIUM): Remediate-certify loop does not converge. Same SLIP fixes fail certification repeatedly.
- *Probability*: Low
- *Mitigation*: Bounded to 2 attempts. Terminal halt with manual-fix instructions provides escape hatch.

**R-6** (LOW): Resume logic complexity increases. Two new steps add resume checkpoints.
- *Probability*: Low
- *Mitigation*: Each new step follows existing resume check pattern in `_apply_resume()`. No new resume primitives needed.

**R-7** (MEDIUM): `spec-fidelity` STANDARD downgrade masks real issues.
- *Probability*: Low
- *Mitigation*: `deviation-analysis` STRICT gate catches all real issues. Fidelity report still produced as diagnostic artifact; blocking responsibility moves to a step with better context.

**R-8** (LOW): `deviation_class` field breaks existing `Finding` consumers.
- *Probability*: Low
- *Mitigation*: Field defaults to `"UNCLASSIFIED"`. `__post_init__` always validates. All existing code paths produce Findings without specifying `deviation_class`, which defaults to valid value.

**R-9** (MEDIUM): YAML frontmatter parsing for routing table is fragile.
- *Probability*: Medium
- *Mitigation*: Use flat comma-separated frontmatter fields (Option A) instead of nested YAML lists. Consistent with existing pipeline conventions. `_parse_routing_list()` handles comma-separated format.

---

## Dependency Inventory

### Internal (Same Repository)

1. `src/superclaude/cli/roadmap/prompts.py` — modified: `build_spec_fidelity_prompt()`, new functions `build_annotate_deviations_prompt()`, `build_deviation_analysis_prompt()`
2. `src/superclaude/cli/roadmap/gates.py` — modified: `SPEC_FIDELITY_GATE`, `CERTIFY_GATE`, `ALL_GATES`; new: `ANNOTATE_DEVIATIONS_GATE`, `DEVIATION_ANALYSIS_GATE`, 9 new semantic check functions; `parse_frontmatter()` (public rename)
3. `src/superclaude/cli/roadmap/executor.py` — modified: `_build_steps()`, `_get_all_step_ids()`, `_save_state()`, `execute_roadmap()`; new: `_check_remediation_budget()`, `_print_terminal_halt()`, `_check_annotate_deviations_freshness()`, `_inject_roadmap_hash()`; retired: 6 symbols
4. `src/superclaude/cli/roadmap/models.py` — modified: `Finding` dataclass; new: `VALID_DEVIATION_CLASSES`
5. `src/superclaude/cli/roadmap/remediate.py` — new: `deviations_to_findings()`, `_parse_routing_list()` (may move to `parsing.py`)
6. `src/superclaude/cli/roadmap/remediate_prompts.py` — modified: deviation-class-aware fix guidance
7. `src/superclaude/cli/roadmap/fidelity.py` — potentially modified: `FidelityDeviation` classification field; `_extract_fidelity_deviations()`, `_extract_deviation_classes()`
8. `src/superclaude/cli/roadmap/parsing.py` — potentially NEW: if `_parse_routing_list()` needs to be shared between `remediate.py` and `gates.py`
9. `.roadmap-state.json` — modified schema: new `remediation_attempts` field under `remediate` key
10. `.claude/skills/sc-roadmap-protocol/SKILL.md` — modified: wave sub-step definitions for new steps

### External / Runtime

11. **Python `hashlib`** — SHA-256 computation for `roadmap_hash` injection and freshness check
12. **Python `os.replace()`** — atomic file write for `.roadmap-state.json` and `spec-deviations.md` (POSIX atomic; Windows best-effort)
13. **Claude subprocess API** — executes `annotate-deviations` and `deviation-analysis` steps; token count metadata is best-effort
14. **`spec_patch.py` / `roadmap accept-spec-change` CLI** — existing; retained unchanged; reads `dev-*-accepted-deviation.md` (not `spec-deviations.md`)

---

## Success Criteria

**SC-1** (FR-047): Pipeline processes the v2.24 spec without halting at fidelity.
- *Threshold*: Full end-to-end pipeline run completes; manual acceptance gate in Phase 4; automated CI substitute via `tests/roadmap/test_integration_v5_pipeline.py` with fixture-based subprocess replay.

**SC-2** (FR-048): Intentional deviations (D-02, D-04) are pre-approved and excluded from HIGH severity count.
- *Threshold*: `spec-deviations.md` classifies D-02 and D-04 as `INTENTIONAL_IMPROVEMENT`; `spec-fidelity.md` shows these excluded from HIGH count.

**SC-3** (FR-049): SLIPs (DEV-002, DEV-003) are classified and routed to remediation.
- *Threshold*: `deviation-analysis.md` shows `slip_count >= 2`, `routing_fix_roadmap` contains DEV-002 and DEV-003.

**SC-4** (FR-050): Remediation targets only SLIPs, does not modify intentional deviations.
- *Threshold*: `roadmap.md` diff before/after remediation shows changes only for missing data models and function signatures; no changes to `steps/` subdirectory layout or other intentional deviations.

**SC-5** (FR-051): Certify blocks on `certified: false`.
- *Threshold*: Unit test for `_certified_is_true()` passes; a certification report with `certified: false` causes `CERTIFY_GATE` STRICT failure.

**SC-6** (FR-052): Pipeline halts after 2 failed remediation attempts with manual-fix instructions.
- *Threshold*: Integration test with mock failing certify verifies `_print_terminal_halt()` output to `stderr` and `sys.exit(1)` after `remediation_attempts == 2`.

**SC-7** (NFR-001): No new executor primitives.
- *Threshold*: Zero new classes in `pipeline/models.py` or `pipeline/executor.py`. Verified by code review / `git diff`.

**SC-8** (NFR-002): Pipeline cost increase ≤ 600s per run.
- *Threshold*: Both new steps have `timeout_seconds=300`. Net timing measured on Phase 4 validation run.

**SC-9** (NFR-004): Resume correctness — `--resume` correctly skips completed steps.
- *Threshold*: `tests/roadmap/test_executor.py` includes all 9 required test cases for `_check_annotate_deviations_freshness()` (§11.6); all pass.

**SC-10**: `_total_annotated_consistent()` and `_total_analyzed_consistent()` count arithmetic validation.
- *Threshold*: Unit tests in `tests/roadmap/test_gates_data.py` verify correct pass/fail behavior including malformed-field path (returns `False` with WARNING log, not exception).

---

## Open Questions

**OQ-A** (Critical — must resolve before FR-079 implementation): Choose Option A or Option B for `_pre_approved_not_in_fix_roadmap()`. Option A requires adding `GateCriteria.aux_inputs` field (does it already exist?). Option B requires adding `pre_approved_ids` as a required frontmatter field in `DEVIATION_ANALYSIS_GATE`. The spec recommends Option B if `aux_inputs` is absent.

**OQ-B** (Critical — must resolve before FR-084 implementation): Does `_apply_resume()` cache gate results in `.roadmap-state.json`? If yes, the `spec-fidelity` and `deviation-analysis` cached results MUST be explicitly invalidated when `annotate-deviations` is force-re-queued. If no, FR-084 is satisfied automatically by pipeline order.

**OQ-C** (NFR-019 vs. FR-059 contradiction): §14.9 (NFR-019) states `_apply_resume_after_spec_patch()` SHALL be retained unchanged. FR-059 states it SHALL be retired. These directly contradict. Stakeholder clarification required: is the spec-patch auto-resume cycle retired (FR-059) or retained-dormant (NFR-019) in v2.25?

**OQ-D**: `_parse_routing_list()` placement: If both `remediate.py` and `gates.py` need this function, a new `parsing.py` module is required. Is this acceptable, or should the function be duplicated/inlined? Decision affects module structure before implementation begins.

**OQ-E**: FR-088 extension of `_routing_ids_valid()` requires `spec-fidelity.md` content as a second argument. This depends on FR-079 Option A (`GateCriteria.aux_inputs`). If Option B is chosen for FR-079, what is the fallback for FR-088's existence validation?

**OQ-F**: FR-077 specifies that `_print_terminal_halt()` include a note about spec-patch cycle history, but the state file mechanism for communicating this is explicitly deferred to v2.26. How should v2.25 implementors handle this: omit the note entirely, hardcode it unconditionally, or add a best-effort heuristic?

**OQ-G**: The `AMBIGUOUS_ITEMS.md` report is referenced in FR-091 as being written by "shortterm amendments" (FR-063/FR-064), but these FRs are not defined in this spec. What writes `AMBIGUOUS_ITEMS.md` and under what conditions?

**OQ-H**: `_extract_fidelity_deviations()` and `_extract_deviation_classes()` are referenced in §7.2 with error behavior specified (FR-060, FR-062 amendments), but the original FR-060 and FR-062 definitions are not present in this spec. Are these functions pre-existing in `fidelity.py`, or do they need to be created?

**OQ-I** (Deferred to v2.26): `roadmap resolve-ambiguity --id DEV-NNN --action slip|accept` CLI command. No v2.25 action required; manual file editing is the operator workflow.

**OQ-J** (Deferred to v2.26): LoopStep primitive as replacement for `--resume` in remediate-certify cycle (OQ-11 in spec §13).

**OQ-K** (Deferred to v2.26): `Finding.status` lifecycle: add `VERIFICATION_FAILED` terminal status (OQ-9 in spec §13).
