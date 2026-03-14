STATUS: FAIL
TOTAL_ISSUES_SOURCE: 6
TOTAL_ISSUES_EXTRACTED: 4

MISSES: ## Consolidated FR/NFR List, ## v2.25 vs. v2.26 Deferral Assessment
TRUNCATIONS: NONE
PHANTOMS: NONE
CONTAMINATIONS: NONE

=== CORRECTION FOR: ## Consolidated FR/NFR List ===
Recommended Approach

[NO "Recommended Approach" SUBSECTION EXISTS UNDER THIS HEADING IN SOURCE]

Draft Spec Language

[NO "Draft Spec Language" SUBSECTION EXISTS UNDER THIS HEADING IN SOURCE]

Verbatim source content for this section:

## Consolidated FR/NFR List

| Number | Type | Section | Summary | v2.25 or v2.26 |
|--------|------|---------|---------|----------------|
| FR-055 | FR | §3.2 | Executor injects `roadmap_hash` into `spec-deviations.md` frontmatter after subprocess completes | v2.25 |
| FR-056 | FR | §3.5 | `ANNOTATE_DEVIATIONS_GATE` required fields include `roadmap_hash` | v2.25 |
| FR-057 | FR | §8.2 | `_apply_resume()` calls `_check_annotate_deviations_freshness()` before skipping `annotate-deviations`; fail-closed | v2.25 |
| NFR-011 | NFR | §8.2 | `_check_annotate_deviations_freshness()` is fail-closed; missing file/field/error returns False (force re-run), never raises | v2.25 |
| FR-058 | FR | §8.4 | `_check_remediation_budget()` coerces `remediation_attempts` to `int`; logs WARNING on corrupt value; treats corruption as 0 | v2.25 |
| NFR-012 | NFR | §8.4 | `_save_state()` coerces `existing_attempts` to `int` before incrementing; `remediation_attempts` is always written as Python `int` | v2.25 |
| FR-059 | FR | §5.4 | Deviation IDs SHALL match `DEV-\d+`; prompt instructs agent to use only IDs as they appear in `spec-fidelity.md` | v2.25 |
| FR-060 | FR | §5.5 | `_routing_ids_valid(content: str) -> bool` added to `gates.py`; validates all routing field tokens against `^DEV-\d+$`; registered as STRICT check on `DEVIATION_ANALYSIS_GATE` | v2.25 |
| FR-061 | FR | §7.2 | `_parse_routing_list()` validates each token against `^DEV-\d+$`; warns and excludes non-conforming; cross-checks `len(returned_tokens) <= total_analyzed` | v2.25 |
| FR-062 | FR | §8.7 (new) | Spec-patch cycle and remediation budget remain independent; no global budget counter introduced | v2.25 (doc) |
| FR-063 | FR | §8.7 (new) | `_print_terminal_halt()` SHALL include spec-patch-also-fired note when both mechanisms are exhausted; state mechanism deferred to v2.26 | v2.26 (impl) |
| NFR-013 | NFR | §8.7 (new) | Combined max recovery attempts SHALL NOT exceed 3; enforced by independent caps | v2.25 (doc) |
| NFR-014 | NFR | §14.7 (new) | `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` SHALL be retained unchanged in v5; not removed | v2.25 (doc) |

=== CORRECTION FOR: ## v2.25 vs. v2.26 Deferral Assessment ===
Recommended Approach

[NO "Recommended Approach" SUBSECTION EXISTS UNDER THIS HEADING IN SOURCE]

Draft Spec Language

[NO "Draft Spec Language" SUBSECTION EXISTS UNDER THIS HEADING IN SOURCE]

Verbatim source content for this section:

## v2.25 vs. v2.26 Deferral Assessment

### Do in v2.25

**FR-055, FR-056, FR-057, NFR-011 (Issue 1 — roadmap hash stale detection)**

Rationale: The failure mode (stale `spec-deviations.md` silently feeds incorrect
routing to downstream steps) is a correctness defect with no workaround. If a
user edits `roadmap.md` and resumes, the pipeline produces wrong results without
warning. The implementation is ~35 lines in executor.py, one new helper function,
one new required frontmatter field. This is firmly within v2.25 scope alongside
the `annotate-deviations` step implementation.

Cost: low. Risk: very low. Value: high (prevents silent data corruption).

**FR-058, NFR-012 (Issue 2 — non-integer remediation_attempts)**

Rationale: This is a one-step crash defect with a targeted 14-line fix. It
crashes the pipeline with an uncaught exception rather than a controlled halt,
breaking the `sys.exit(1)` contract and losing diagnostic output. Fixing it
requires no architectural changes, no new dependencies, and no spec ambiguity.
This must be in v2.25.

Cost: minimal. Risk: zero. Value: high (correctness).

**FR-059, FR-060, FR-061 (Issue 3 — deviation ID format)**

Rationale: Comma in a deviation ID silently corrupts routing, causing SLIPs to
be skipped in remediation. The STRICT gate check (`FR-060`) prevents malformed
output from reaching `deviations_to_findings()`. The defensive parse filter
(`FR-061`) is defense in depth. Both are pure-function additions to `gates.py`
and executor.py. The `DEVIATION_ANALYSIS_GATE` is new in v2.25 and adding a
new semantic check during initial definition has zero migration cost.

Cost: low (~45 lines). Risk: very low. Value: high (prevents silent data loss).

**FR-062, NFR-013, NFR-014 (Issue 4 — counter interaction documentation)**

Rationale: The §8.7 table and §14.7 dormancy note are documentation-only
changes that cost minutes to add and prevent future implementers from
misunderstanding the retry architecture. Including them in v2.25 alongside the
counter implementation is the natural time to document them.

Cost: documentation only. Risk: zero. Value: medium (long-term maintainability).

### Defer to v2.26

**FR-063 implementation (Issue 4 — `_print_terminal_halt()` dual-mechanism note)**

Rationale: Implementing the "both mechanisms exhausted" note in
`_print_terminal_halt()` requires adding a `spec_patch_attempted` boolean to
`.roadmap-state.json` and a new write call mid-execution in `execute_roadmap()`.
This is disproportionate to the diagnostic value. The scenario (spec-patch fires
AND remediation exhausts) is extremely unlikely in a functioning v5 pipeline.
The spec text (FR-063) is included in v2.25 as a forward requirement; the
implementation is deferred.

Defer to v2.26 with the note "implement state schema extension for
`spec_patch_attempted` tracking."

**Approach C (Issue 1) — Generic input hash tracking for all steps**

Rationale: A pipeline-wide `input_hash` mechanism would provide comprehensive
staleness detection across all steps. For v2.25, the targeted `roadmap_hash`
approach (FR-055/FR-057) is sufficient and correct for the identified failure
mode. The generic mechanism is a v2.26 enhancement that would eliminate the
entire class of stale-artifact problems.

**Formal JSON schema for `.roadmap-state.json` (Issue 2, Approach C)**

Rationale: Schema validation with a library like `jsonschema` adds a runtime
dependency not currently in `pyproject.toml`. The inline coercions in
FR-058 and NFR-012 address the immediate defect without the dependency cost.
A formal schema definition would be appropriate in v2.26 when the state file
has stabilized and all fields from v2.25 are confirmed.

**Separator change (Issue 3, Approaches B/C)**

Rationale: Changing comma to semicolon or space is a cosmetic mitigation that
does not address the root cause (unconstrained ID format). FR-059's regex
constraint eliminates the root cause. The separator change adds a breaking
spec change (8+ locations to update) for no additional protection over Approach A.
Not recommended for any version unless Approach A proves insufficient.
