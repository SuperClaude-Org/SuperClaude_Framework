---
spec_source: v2.25-spec-merged.md
complexity_score: 0.92
adversarial: true
---

# v2.25 Roadmap: Deviation-Aware Fidelity Pipeline (Final Merged)

## Executive Summary

v2.25 introduces a **deviation-aware fidelity subsystem** into the roadmap pipeline, solving a systematic failure where intentional architectural improvements were misclassified as specification violations, causing pipeline halts and futile remediation cycles.

The solution adds two new pipeline steps (`annotate-deviations`, `deviation-analysis`) and modifies three existing components (`spec-fidelity`, `remediate`, `certify`), all built on existing executor primitives. The architecture follows a **classify → route → act** pattern: deviations are annotated against the debate record, classified by intent, routed to appropriate handlers (fix, spec-update, no-action, human-review), and only genuine SLIPs reach remediation.

**Delivery strategy**: The primary failure mode of this pipeline is not that valid slips fail to remediate — it is that invalid intentional classifications silently pass. Negative validation (what the pipeline refuses to do) is treated as the primary correctness boundary, not an equivalent to positive validation. Release is blocked on evidence, not implementation confidence.

**Key architectural properties:**
- Zero new executor primitives (Step, GateCriteria, SemanticCheck reuse only)
- Sprint pipeline completely isolated — no generic layer modifications
- Bounded recovery: max 2 automatic remediation attempts
- Fail-closed semantics throughout all new gate checks
- Anti-laundering safeguards via citation requirements and cross-validation

**Scope**: 6–8 modified source files, 1 potential new module, ~700 lines new code, 5 modified + 1 new test file across 7 domains.

**Timeline**: 11–17 working days. Lower bound (11 days) assumes Phase 0 OQ resolution is clean, `fidelity.py` requires no modification, and team composition enables some parallelization. Upper bound (17 days) reflects OQ-A Option B body parsing (+1–2 days), `fidelity.py` modification (+0.5–1 day), and complex fixture generation. Solo-engineer lower bound is ~13 days. Re-estimate after Phase 0 completion with actual OQ resolution outcomes. Proceed to release only after Phase 5 evidence review — code-complete status is not a release gate.

---

## Phase 0: Pre-Implementation Decisions and Baselining

**Goal**: Establish implementation constraints, resolve deferred architecture decisions, and freeze the intended design before modifying any behavior.

**Duration estimate**: 0.5–1.5 days

**Dependencies**: None

### Open Question Resolution

All blocking open questions must be resolved or explicitly deferred with documented fallback behavior before Phase 1 begins:

1. **OQ-A / OQ-B**: Does `GateCriteria.aux_inputs` exist? This decision cascades to FR-079 implementation (Option A: pass `pre_approved_ids` via `aux_inputs`; Option B: embed as comma-separated frontmatter field) and FR-088 extended validation deferral. Inspect `GateCriteria` definition in `models.py` — 30-minute task.
2. **OQ-C**: How are `PRE_APPROVED` IDs extracted for gate validation? Depends on OQ-A resolution.
3. **OQ-E**: Confirm or define `_extract_fidelity_deviations()` signature. Almost certainly in `fidelity.py` given naming conventions — must be confirmed, not assumed.
4. **OQ-F**: Confirm or define `_extract_deviation_classes()` signature. Same investigation as OQ-E.
5. **OQ-G**: Confirm `build_remediate_step()` module location from v2.24.2 codebase.
6. **OQ-H**: Confirm `roadmap_run_step()` interface for the post-step hook needed for `roadmap_hash` injection.
7. **OQ-I**: Confirm token-count field availability in Claude subprocess API response. Best-effort is acceptable per NFR-024, but must be verified for `started_at`/`completed_at`/`token_count` recording.
8. **OQ-J**: Document v2.25 handling for FR-077 dual-budget-exhaustion note behavior (mechanism deferred to v2.26).

### Architecture Constraint Confirmation

Verify against codebase before coding:
- No modifications to generic pipeline layer (`pipeline/executor.py`, `pipeline/models.py`)
- No new executor primitives (Step, GateCriteria, SemanticCheck reuse only)
- No normal execution reads of `dev-*-accepted-deviation.md`
- Module dependency hierarchy remains acyclic

### `fidelity.py` Investigation

`fidelity.py` must appear explicitly in this checklist even if modification is not assumed. OQ-E/OQ-F concern extraction helper function signatures that almost certainly reside there. Confirm:
- Does `_extract_fidelity_deviations()` exist here? Require modification for v2.25?
- Does `_extract_deviation_classes()` exist here? Require modification for v2.25?
- Add to Phase 1 "Files Modified" table if modification is confirmed; otherwise annotate as "inspected, no modification required."

### `_parse_routing_list()` Module Placement

Resolve circular import risk and module boundary before Phase 1 concludes. Options: remain in `remediate.py`, extract to new `parsing.py`. This decision affects import graphs that every subsequent phase builds against — a mid-Phase-2 refactor to extract `parsing.py` is the kind of disruption that collapses timeline estimates.

### Phase 0 Deliverables

- Implementation decision log (all OQs resolved or deferred with fallback documented)
- Requirement traceability matrix (requirement → file(s) → test(s) → milestone)
- Confirmed module ownership map including `fidelity.py` disposition and `_parse_routing_list()` placement
- Test plan aligned to SC-1 through SC-10

### Phase 0 Exit Criteria

- [ ] All 8 open questions resolved or deferred with documented fallback
- [ ] `fidelity.py` inspection complete; scope impact documented
- [ ] `_parse_routing_list()` module placement decided
- [ ] No unresolved decision remains that could force rework in gates, parsing, or executor resume flow
- [ ] Architecture constraint verification complete against live codebase

---

## Phase 1: Foundation — Data Model, Parsing, and Gate Infrastructure

**Goal**: Establish the type system, gate definitions, and semantic check functions that all subsequent phases depend on.

**Duration estimate**: 2–3 days

**Dependencies**: Phase 0 complete

### Data Model Changes (models.py)

1. Add `deviation_class: str = "UNCLASSIFIED"` field to `Finding` dataclass
2. Add `VALID_DEVIATION_CLASSES` frozenset: `{"SLIP", "INTENTIONAL", "AMBIGUOUS", "PRE_APPROVED", "UNCLASSIFIED"}`
3. Add `__post_init__` validation of `deviation_class` against `VALID_DEVIATION_CLASSES` (raises `ValueError`)
4. Verify backward compatibility: all existing `Finding` constructors continue to work with the default

**Requirements covered**: FR-030, FR-031, FR-032, NFR-003, NFR-005

### Frontmatter and Parsing Hardening (gates.py)

1. **Rename `_parse_frontmatter()` → `parse_frontmatter()`** — grep all callers before rename; single atomic commit (NFR-021). This must happen first as downstream phases import it.
2. Implement `_parse_routing_list()` at the module placement decided in Phase 0:
   - Split on `,`, strip whitespace immediately
   - Validate each token against `re.compile(r'^DEV-\d+$')`
   - Log WARNING and exclude non-conforming tokens
   - Cross-check `len(returned_tokens)` against `total_analyzed`
3. Integer-parsing checks must distinguish missing / malformed / failing values with distinct log messages (FR-080)

### Semantic Check Functions (gates.py)

All fail-closed per NFR-016 pattern:

1. `_certified_is_true()` — FR-028
2. `_validation_complete_true()` — FR-053
3. `_no_ambiguous_deviations()` — FR-026
4. `_routing_consistent_with_slip_count()` — FR-056
5. `_pre_approved_not_in_fix_roadmap()` — FR-079 (implementation method depends on OQ-A resolution)
6. `_slip_count_matches_routing()` — FR-081
7. `_total_annotated_consistent()` — FR-085
8. `_total_analyzed_consistent()` — FR-086
9. `_routing_ids_valid()` — FR-074
10. `_no_ambiguous_deviations()` (alias check) — FR-026

### Gate Definitions (gates.py)

1. Define `ANNOTATE_DEVIATIONS_GATE` — STANDARD tier, required fields include `roadmap_hash`, checks: `_total_annotated_consistent` (FR-013, FR-070, FR-085)
2. Define `DEVIATION_ANALYSIS_GATE` — STRICT tier, 6 semantic checks in order: `no_ambiguous_deviations`, `validation_complete_true`, `routing_consistent_with_slip_count`, `pre_approved_not_in_fix_roadmap`, `slip_count_matches_routing`, `total_analyzed_consistent` (FR-026, FR-027, FR-046, FR-057, FR-079, FR-081, FR-086)
3. Modify `SPEC_FIDELITY_GATE`: downgrade STRICT → STANDARD, remove `high_severity_count_zero` and `tasklist_ready_consistent` from active checks, add `[DEPRECATED v2.25]` docstrings (FR-014, FR-015)
4. Modify `CERTIFY_GATE`: append `certified_true` semantic check (FR-029)
5. Update `ALL_GATES` registry with both new gate entries (FR-054)
6. Retain deprecated semantic check functions with `[DEPRECATED v2.25]` docstrings — do not delete

**Requirements covered**: FR-013, FR-014, FR-015, FR-026, FR-027, FR-028, FR-029, FR-046, FR-053, FR-054, FR-056, FR-057, FR-070, FR-074, FR-079, FR-080, FR-081, FR-085, FR-086, NFR-007, NFR-021

### Phase 1 Exit Criteria

- [ ] `Finding("test", deviation_class="SLIP")` constructs successfully
- [ ] `Finding("test", deviation_class="INVALID")` raises `ValueError`
- [ ] `Finding("test")` defaults to `"UNCLASSIFIED"`
- [ ] All 9+ semantic check functions pass unit tests with boundary inputs — including **missing**, **malformed**, and **failing-value** cases with distinct log messages
- [ ] `parse_frontmatter()` is public; all callers updated; grep confirms no remaining private references
- [ ] `_parse_routing_list()` placed in decided module; handles empty string, whitespace, invalid IDs, valid IDs
- [ ] `SPEC_FIDELITY_GATE` is STANDARD tier
- [ ] `CERTIFY_GATE` includes `certified_true` check
- [ ] `DEVIATION_ANALYSIS_GATE` semantic check order verified, not just existence
- [ ] Phase 0 OQ-A resolved and documented; gate implementation matches chosen option
- [ ] Full test suite passes — STANDARD downgrade is a relaxation and unlikely to break, but confirm

---

## Phase 2: New Pipeline Steps — Prompts, Step Wiring, and Artifact Contracts

**Goal**: Implement the two new steps (`annotate-deviations`, `deviation-analysis`) with their prompts, step definitions, and artifact output contracts. FR-087 CLI surfacing and FR-089 graceful degradation are scoped here.

**Duration estimate**: 3–4 days

**Dependencies**: Phase 1 complete (gates, data model, `parse_frontmatter()` public, `_parse_routing_list()` placed)

### Prompt Builders (prompts.py)

#### `build_annotate_deviations_prompt()` — new function

- Inputs: `spec_file` (original, not extraction — FR-005), `roadmap.md`, `debate-transcript.md`, `diff-analysis.md`
- Classification taxonomy: `INTENTIONAL_IMPROVEMENT`, `INTENTIONAL_PREFERENCE`, `SCOPE_ADDITION`, `NOT_DISCUSSED` (FR-006)
- Anti-laundering rules: `INTENTIONAL_IMPROVEMENT` requires D-XX + round citation (FR-007, FR-008, FR-009, FR-010). Prompt wording must be unambiguous: architectural-quality inference is not proof of intentionality; missing citation defaults to `NOT_DISCUSSED`.
- Output contract: `spec-deviations.md` with specified YAML frontmatter (FR-011) and body format (FR-012)
- `schema_version: "2.25"` as first frontmatter field (NFR-023)

#### `build_deviation_analysis_prompt()` — new function

- Inputs: `spec-fidelity.md`, `debate-transcript.md`, `diff-analysis.md`, `spec-deviations.md`, `roadmap-A.md`, `roadmap-B.md`
- Classification taxonomy: `PRE_APPROVED`, `INTENTIONAL`, `SLIP`, `AMBIGUOUS` (FR-021)
- Normative classification mapping table from §5.3a (FR-078)
- Routing table output: `fix_roadmap`, `update_spec`, `no_action`, `human_review` (FR-022)
- Blast radius analysis for each `INTENTIONAL` deviation (FR-023)
- `routing_intent` sub-field (`superior` | `preference`) for INTENTIONAL deviations (FR-090)
- `## Spec Update Recommendations` subsection for `update_spec` routed deviations (FR-087)
- Output contract: `deviation-analysis.md` with specified YAML frontmatter (FR-024) and body (FR-025)
- Flat routing fields with comma-separated DEV-\d+ IDs (FR-045, FR-073)
- `schema_version: "2.25"` as first frontmatter field (NFR-023)

#### Modify `build_spec_fidelity_prompt()` — add `spec_deviations_path: Path | None = None` parameter (FR-016)

When provided: instruct agent to VERIFY citations, EXCLUDE verified `INTENTIONAL_IMPROVEMENT`, REPORT invalid annotations as HIGH, ANALYZE `NOT_DISCUSSED` independently (FR-017).

### Step Wiring (executor.py)

1. Add `annotate-deviations` step in `_build_steps()` between `merge` and `test-strategy` (FR-004)
   - Inputs: `spec_file`, `roadmap.md`, `debate-transcript.md`, `diff-analysis.md`
   - Output: `spec-deviations.md`
   - Gate: `ANNOTATE_DEVIATIONS_GATE` (STANDARD), timeout 300s, retry_limit=0
2. Add `deviation-analysis` step in `_build_steps()` after `spec-fidelity` (FR-020)
   - Inputs: `spec-fidelity.md`, `debate-transcript.md`, `diff-analysis.md`, `spec-deviations.md`, `roadmap-A.md`, `roadmap-B.md`
   - Output: `deviation-analysis.md`
   - Gate: `DEVIATION_ANALYSIS_GATE` (STRICT), timeout 300s, retry_limit=1
3. Update `_get_all_step_ids()` to include both new steps in correct pipeline order (FR-038) — verify 13 steps in correct order
4. Pass `spec-deviations.md` as additional input to `spec-fidelity` step (FR-018)
5. Add `roadmap_hash` injection after `annotate-deviations` subprocess completes (FR-055):
   - SHA-256 of `roadmap.md` at injection time
   - Atomic write: `.tmp` + `os.replace()` (NFR-022)
6. Record `started_at`, `completed_at`, `token_count` (best-effort) for new steps in `_save_state()` (NFR-024)

### Graceful Degradation Specification (executor.py)

1. When `annotate-deviations` produces `total_annotated: 0`: log at INFO level, emit operator message explaining that `deviation-analysis` will act as backstop, continue pipeline — do not halt (FR-089)
2. Print `routing_update_spec` summary in CLI output when non-empty (FR-087) — this is a required explicit behavior, not an implicit side-effect

### Remediation Module (remediate.py)

1. **`deviations_to_findings()`** — new function (FR-033):
   - Converts classified deviations into `Finding` objects
   - Only produces findings for deviations routed to `fix_roadmap` (FR-035)
   - Severity mapping: HIGH→BLOCKING, MEDIUM→WARNING, LOW→INFO (FR-034)
   - `ValueError` if routing is empty but `slip_count > 0` (defense-in-depth, FR-058)
   - WARNING log when routing ID not found in fidelity table (FR-082)
2. Update remediation step to use `deviation-analysis.md` routing table as primary input (FR-036)
3. Update remediation prompt with deviation-class awareness: instruct agent to fix only SLIPs, explicitly prohibit modification of `INTENTIONAL` and `PRE_APPROVED` items (FR-037)

**Requirements covered**: FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-016, FR-017, FR-018, FR-019, FR-020, FR-021, FR-022, FR-023, FR-024, FR-025, FR-033, FR-034, FR-035, FR-036, FR-037, FR-038, FR-045, FR-055, FR-058, FR-073, FR-075, FR-078, FR-082, FR-083, FR-087, FR-089, FR-090, NFR-002, NFR-022, NFR-023, NFR-024

### Phase 2 Exit Criteria

- [ ] Both prompts produce well-formed output contracts (manual prompt review with golden artifact samples)
- [ ] Pipeline step order matches FR-002 exactly
- [ ] `_get_all_step_ids()` returns 13 steps in correct order
- [ ] `roadmap_hash` injection uses atomic write pattern
- [ ] `deviations_to_findings()` unit tests pass for all severity mappings
- [ ] FR-089: `total_annotated: 0` produces INFO log and continues — does not halt
- [ ] FR-087: `routing_update_spec` appears in CLI output when non-empty
- [ ] Prompt-level golden tests or fixture assertions confirm required anti-laundering instructions and expected schema fields
- [ ] Integration tests for `deviations_to_findings()` noted as sequenced after Phase 3 completes budget mechanism (may be scaffolded now, completed in Phase 3)

---

## Phase 3: Resume Logic, Recovery Mechanisms, and Spec-Patch Retirement

**Goal**: Implement resume freshness detection, remediation budget enforcement, and retire the spec-patch auto-resume cycle. This is the highest regression-risk phase.

**Duration estimate**: 2–4 days

**Dependencies**: Phase 2 complete (steps wired, hash injection working)

### Resume Freshness Detection (executor.py)

1. **`_check_annotate_deviations_freshness()`** — new function (FR-071, NFR-016):
   - Compare `roadmap_hash` in `spec-deviations.md` against current SHA-256 of `roadmap.md`
   - Fail-closed: missing file, missing field, read error → return `False`; log the specific failure reason (not just that it failed — silent re-execution will complicate incident analysis)
   - When returning `False`: re-add `annotate-deviations` to execution queue
   - Also reset gate-pass state for `spec-fidelity` and `deviation-analysis` (FR-084)
2. Integrate freshness check into `_apply_resume()` before skipping `annotate-deviations` (FR-071)

Most likely hidden failures in this phase:
- Stale `spec-deviations.md` incorrectly reused
- Remediation attempts miscounted
- State corruption on interrupted writes
- Downstream gates not invalidated when annotate freshness fails

### Remediation Budget Enforcement (executor.py)

1. Add `remediation_attempts` counter to `.roadmap-state.json` (FR-039)
2. **`_check_remediation_budget()`** — new function (FR-040, FR-041):
   - Coerce `remediation_attempts` to `int` before comparison (FR-072); coercion failure: log WARNING, treat as 0
   - Max 2 attempts (configurable via `max_attempts` parameter)
   - On budget exhaustion: call `_print_terminal_halt()` and return `False`
   - Must NOT call `sys.exit(1)` directly — callers own exit (Constraint #12)
3. **`_print_terminal_halt()`** — new function (FR-042):
   - Output to stderr: attempt count, remaining failing finding count, per-finding details, manual-fix instructions with certification report path and resume command
   - Stderr content assertions must be covered by unit tests (not just implementation-specified)
4. Caller logic: on third `--resume` attempt (budget exhausted), `sys.exit(1)` (FR-044)
5. Atomic state writes: `.tmp` + `os.replace()` for `.roadmap-state.json` (NFR-022)
6. `_save_state()` coerces `existing_attempts` to `int` before incrementing (NFR-017)
7. Existing `.roadmap-state.json` without `remediation_attempts` defaults to 0 gracefully

### Spec-Patch Cycle Retirement (executor.py)

1. Retire `_apply_resume_after_spec_patch()` from active execution (FR-059)
2. Retain `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` as functionally dormant (NFR-019) — do not delete
3. Ensure spec-patch and remediation budgets remain independent counters (FR-076)
4. When both mechanisms exhausted, `_print_terminal_halt()` includes note about both (FR-077 — placeholder for v2.25, mechanism deferred to v2.26 per OQ-J)

**Requirements covered**: FR-039, FR-040, FR-041, FR-042, FR-043, FR-044, FR-059, FR-071, FR-072, FR-076, FR-077, FR-084, NFR-008, NFR-011, NFR-016, NFR-017, NFR-018, NFR-019, NFR-022

### Phase 3 Exit Criteria

- [ ] `_check_annotate_deviations_freshness()` passes all 9 specified test cases (SC-8)
- [ ] Freshness failure reason logged explicitly before returning `False`
- [ ] Freshness mismatch triggers re-run of `annotate-deviations` + resets `spec-fidelity` and `deviation-analysis` gate-pass state
- [ ] Remediation budget caps at 2 attempts; third attempt triggers terminal halt
- [ ] `_print_terminal_halt()` stderr content covered by assertion-based unit tests
- [ ] Coercion handling: non-integer `remediation_attempts` treated as 0 with WARNING
- [ ] Existing `.roadmap-state.json` without `remediation_attempts` handled gracefully
- [ ] `_apply_resume_after_spec_patch()` code retained but never invoked in normal v2.25 flow
- [ ] Integration tests for `deviations_to_findings()` (scaffolded in Phase 2) completed against stable budget mechanism
- [ ] Resume behavior verified across: fresh resume, stale roadmap hash, exhausted remediation budget, malformed state file attempt values

---

## Phase 4: Negative Validation and Release Verification

**Goal**: Validate that only actionable slips are remediated and that all required refusal behaviors are verified with evidence. This phase treats negative validation as the primary correctness boundary.

**Duration estimate**: 1.5–3 days

**Dependencies**: Phases 1–3 complete

### Negative Validation Release Blockers

**Block release on evidence, not implementation confidence.** For a 0.92-complexity feature, passing tests and artifact inspection are the acceptance threshold — code-complete status alone is not.

The following refusal behaviors must be verified with explicit test or artifact evidence before release is permitted:

1. **Refuse bogus intentional claims**: `INTENTIONAL_IMPROVEMENT` annotation without valid D-XX + round citation is rejected; promoted to HIGH severity in `spec-fidelity`
2. **Refuse stale deviation artifacts**: `spec-deviations.md` with `roadmap_hash` mismatch is never used; `annotate-deviations` reruns
3. **Refuse ambiguous continuation**: `ambiguous_count > 0` causes STRICT gate failure; pipeline halts with operator instructions for manual reclassification
4. **Refuse false certification**: `certified: false` causes `CERTIFY_GATE` failure; pipeline does not advance
5. **Refuse third remediation attempt**: budget exhaustion after 2 attempts triggers terminal halt with `sys.exit(1)`

These are not lower-priority than positive behavior tests — they represent the primary correctness boundary of the v5 design.

### Certify Behavior Alignment

- Ensure `_certified_is_true()` blocks certification on `certified: false` (SC-5)
- Ensure manual-fix recovery path works after repeated failure

### Roadmap Diff Verification

Before/after roadmap diffs serve as evidence for SC-4, not just passing tests:
- Identify changed sections in `roadmap.md` before and after remediation
- Confirm changed sections map exclusively to SLIP-classified deviation IDs
- Confirm no `INTENTIONAL` or `PRE_APPROVED` item content is modified

### Phase 4 Exit Criteria

- [ ] All 5 refusal behaviors verified with explicit test or artifact reference
- [ ] SC-4 verified with before/after roadmap diff (not just test pass)
- [ ] SC-5 verified with explicit true/false/missing/malformed unit tests for `_certified_is_true()`
- [ ] SC-6 verified with failing-certify integration test including stderr assertion
- [ ] No prohibited file modifications in generic pipeline layer

---

## Phase 5: Integration Testing and Release Readiness

**Goal**: Validate the complete pipeline against real and mock scenarios, confirming all success criteria with evidence.

**Duration estimate**: 2–3 days

**Dependencies**: Phases 1–4 complete

### Unit Test Completion

1. `tests/roadmap/test_gates_data.py` — all 10 semantic check functions with boundary inputs (SC-9):
   - Each of the 6 `DEVIATION_ANALYSIS_GATE` checks: correct return for valid/invalid/missing/malformed inputs
   - `_certified_is_true`: true/false/missing/malformed cases
   - `_total_annotated_consistent`: sum matches / doesn't match
   - `_routing_ids_valid`: valid DEV-\d+ / invalid / empty / mixed
2. `tests/roadmap/test_models.py` — `Finding` with `deviation_class` (existing + new field, default compatibility)
3. `tests/roadmap/test_remediate.py` — `deviations_to_findings()` and `_parse_routing_list()`
4. `tests/roadmap/test_executor.py` — `_check_annotate_deviations_freshness()` 9 test cases, `_check_remediation_budget()`, `_print_terminal_halt()` stderr assertions

### Integration Test Completion

1. **`tests/roadmap/test_integration_v5_pipeline.py`** — complete or finalize:
   - v2.24 scenario fixtures with pre-recorded subprocess outputs (no live Claude calls)
   - Validate complete pipeline flow: extract → ... → certify
   - SC-1: Pipeline reaches certify without manual intervention
   - SC-2: D-02 and D-04 pre-approved, excluded from HIGH count
   - SC-3: DEV-002 and DEV-003 classified as SLIP, routed to fix_roadmap
   - SC-4: Remediation modifies only SLIP-routed elements (diff-based verification)
   - SC-6: Terminal halt after 2 failed remediation attempts with stderr detail assertions
2. Verify NFR-009/NFR-010: `pipeline/executor.py` and `pipeline/models.py` have zero modifications (static diff review)

### Manual Validation Run

1. Execute full pipeline against v2.24 spec file
2. Inspect artifacts:
   - `spec-deviations.md`: classification correctness, citation format, `roadmap_hash` present, `schema_version: "2.25"` first (SC-10)
   - `deviation-analysis.md`: routing correctness, blast radius entries, `schema_version: "2.25"` first (SC-10)
   - `spec-fidelity.md`: excluded intentional deviations from HIGH count
3. Verify pipeline completes without halting at fidelity (SC-1)
4. Verify SC-7: no new classes in `pipeline/models.py` or `pipeline/executor.py`

### Release Readiness Checklist

- [ ] All unit tests pass (`uv run pytest tests/roadmap/ -v`)
- [ ] Integration tests pass with mock subprocess outputs
- [ ] SC-1 through SC-10 all marked verified with explicit test or artifact references
- [ ] All 5 refusal behaviors from Phase 4 verified with evidence
- [ ] No regressions in existing test suite
- [ ] Zero modifications to generic pipeline layer (NFR-009, NFR-010) confirmed by static diff
- [ ] Artifact `schema_version: "2.25"` fields present and ordered first (NFR-023)
- [ ] No unresolved open question remains in code comments or documentation
- [ ] `.roadmap-state.json` backward compatibility confirmed for old state files without `remediation_attempts`
- [ ] `_apply_resume_after_spec_patch()` retained but unreachable from normal v2.25 execution paths

---

## Risk Assessment

### High-Priority Risks

| ID | Risk | Severity | Probability | Phase | Mitigation | Validation Evidence |
|----|------|----------|-------------|-------|------------|---------------------|
| R-1 | Deviation laundering / over-approval | HIGH | LOW | 2 | Separate subprocess; D-XX + round citation required; fidelity cross-validation; invalid annotations → HIGH severity | Negative tests for bogus citations; fixture cases where intentional claims are rejected |
| R-2 | Resume/freshness corruption | HIGH | MEDIUM | 3 | Atomic `roadmap_hash` injection; fail-closed freshness check; downstream gate-pass reset on stale detection | All 9 freshness test cases; integration test with changed `roadmap.md` |
| R-3 | Routing/frontmatter parsing fragility | MEDIUM | MEDIUM | 2 | Flat comma-separated fields only; regex validation; gate consistency check when `slip_count > 0`; defense-in-depth `ValueError` | Malformed token tests; empty routing with slips; token presence cross-check |

### Medium-Priority Risks

| ID | Risk | Severity | Probability | Phase | Mitigation | Validation Evidence |
|----|------|----------|-------------|-------|------------|---------------------|
| R-4 | Ambiguity handling not enforced | MEDIUM | LOW | 1, 5 | STRICT gate blocks on `ambiguous_count > 0`; operator reclassification flow documented | Gate failure test; resume-after-manual-fix scenario |
| R-5 | Remediation non-convergence | MEDIUM | LOW | 3 | 2-attempt cap; terminal halt with manual-fix instructions; budgets independent | Integration test with failing certify mock; stderr assertion coverage |
| R-6 | Backward compatibility drift | MEDIUM | LOW | 1, 3 | `deviation_class` default safe; generic pipeline layer untouched; existing state files default `remediation_attempts` to 0 | Constructor compatibility tests; state migration tests; static diff review |
| R-7 | STANDARD downgrade masks issues | MEDIUM | LOW | 1 | `deviation-analysis` STRICT gate catches all real issues | Run full test suite after Phase 1 gate changes |
| R-8 | Context window pressure on `annotate-deviations` | MEDIUM | MEDIUM | 2 | Input set comparable to merge step; within 200KB limit | Monitor during manual validation run |

### Low-Priority Risks

| ID | Risk | Severity | Probability | Phase | Mitigation | Validation Evidence |
|----|------|----------|-------------|-------|------------|---------------------|
| R-9 | Pipeline runtime increase (+600s) | LOW | HIGH | 2 | Eliminates 1200s retry cost on failure paths; net positive; 300s cap per step | Step duration metrics in state file; observed run delta during manual validation |
| R-10 | OQ-A decision delays Phase 1 | LOW | HIGH | 0 | Resolve immediately by inspecting `GateCriteria` definition; 30-minute task | Phase 0 exit criterion: OQ-A resolved |
| R-11 | `parse_frontmatter()` rename causes import errors | LOW | LOW | 1 | Grep all callers before rename; single atomic commit | Full test suite pass after rename |

---

## Resource Requirements

### Files Modified by Phase

| Phase | File | Changes |
|-------|------|---------|
| 0 | `fidelity.py` | Investigation only — confirm `_extract_fidelity_deviations()` and `_extract_deviation_classes()` signatures; modify if required per OQ-E/OQ-F |
| 1 | `models.py` | `Finding.deviation_class`, `VALID_DEVIATION_CLASSES`, `__post_init__` |
| 1 | `gates.py` | `parse_frontmatter()` rename, 9+ semantic checks, 3 gate definitions modified/added, `_parse_routing_list()` if placed here, `ALL_GATES` |
| 1 | (potentially) `parsing.py` | New module if circular imports require `_parse_routing_list()` extraction (decided in Phase 0) |
| 2 | `prompts.py` | 2 new prompt builders, 1 modified (`build_spec_fidelity_prompt`) |
| 2 | `executor.py` | `_build_steps()`, `_get_all_step_ids()`, hash injection, step inputs, FR-087 CLI output, FR-089 graceful degradation |
| 2 | `remediate.py` | `deviations_to_findings()`, input source change |
| 2 | `remediate_prompts.py` | Deviation-class awareness; SLIP-only instructions |
| 3 | `executor.py` | Resume freshness, remediation budget, terminal halt, spec-patch retirement |

### External and Runtime Dependencies

- All stdlib: `hashlib`, `os`, `re`, `json` — no new third-party dependencies
- Claude subprocess API — existing; `token_count` field best-effort (NFR-024, confirm via OQ-I)
- `.roadmap-state.json`, `spec-deviations.md`, `deviation-analysis.md`

### Team Roles

1. **Primary engineer**: owns prompts, gates, executor, remediation integration
2. **QA/test engineer**: owns unit/integration fixture design and SC-1 through SC-10 verification
3. **Reviewer with architecture context**: validates OQ resolutions and module-boundary compliance

### Parallelization Opportunities

The following work can proceed in parallel within phases (team-scenario acceleration):

| While | Parallel work |
|-------|--------------|
| Phase 1 gate implementation | Draft unit tests for new gate functions; prepare fixture schemas for new artifacts |
| Phase 2 prompt integration | Build golden artifact samples; write body/frontmatter schema assertions |
| Phase 3 freshness/executor implementation | Prepare resume/freshness integration fixtures; draft stderr/halt assertions |
| Phase 4 negative validation | Run roadmap diff verification in parallel with certify-block unit tests |

Solo-engineer lower bound is ~13 days; parallelization figures above assume dedicated QA resource.

---

## Success Criteria and Validation

### Validation Model

Three-layer validation is required:

1. **Unit validation**: semantic checks, parsing behavior, model validation, routing conversion, state coercion
2. **Integration validation**: step ordering, resume behavior, remediation budget, certification blocking, end-to-end routing
3. **Artifact inspection**: frontmatter shape, schema version ordering first, routing contents, before/after roadmap diffs

### Success Criteria Mapping

| SC | Criterion | Verification Method | Phase |
|----|-----------|-------------------|-------|
| SC-1 | Pipeline processes v2.24 spec without fidelity halt | Integration test + manual run; run logs and state progression showing certify reached | 5 |
| SC-2 | D-02, D-04 pre-approved, excluded from HIGH | Inspect `spec-deviations.md`, `spec-fidelity.md`, `deviation-analysis.md`: IDs cited, verified, routed to `no_action` | 5 |
| SC-3 | DEV-002, DEV-003 classified SLIP, routed to fix_roadmap | Inspect `deviation-analysis.md` routing fields; `ambiguous_count == 0` | 5 |
| SC-4 | Remediation targets only SLIPs | Before/after roadmap diff — changed sections map exclusively to SLIP IDs | 4–5 |
| SC-5 | Certify blocks on `certified: false` | Unit test `_certified_is_true()` with true/false/missing/malformed cases | 1, 5 |
| SC-6 | Terminal halt after 2 failed remediations | Integration test with mock failing certify; stderr content assertions | 3–5 |
| SC-7 | No new executor primitives | Static diff: zero new classes in generic pipeline layer | 5 |
| SC-8 | Freshness check passes all 9 test cases | Unit tests in `test_executor.py` | 3 |
| SC-9 | `DEVIATION_ANALYSIS_GATE` 6 checks correct | Targeted gate tests — boundary coverage for each check individually | 1, 5 |
| SC-10 | `schema_version: "2.25"` in artifacts, ordered first | Artifact inspection from integration/manual run; frontmatter ordering assertions | 5 |

---

## Timeline Summary

| Phase | Name | Duration | Key Deliverables |
|-------|------|----------|-----------------|
| **0** | Pre-implementation decisions | 0.5–1.5 days | OQ-A through OQ-J resolved; `fidelity.py` disposition confirmed; `_parse_routing_list()` placement decided; architecture freeze |
| **1** | Data model, parsing, gate foundation | 2–3 days | `Finding.deviation_class`; 9+ semantic checks; `ANNOTATE_DEVIATIONS_GATE` and `DEVIATION_ANALYSIS_GATE`; `parse_frontmatter()` public |
| **2** | Prompts, step wiring, artifact contracts | 3–4 days | Both prompt builders; step graph updated; `deviations_to_findings()`; FR-087 CLI output; FR-089 graceful degradation |
| **3** | Resume, recovery, retirement | 2–4 days | Freshness detection; remediation budget; `_print_terminal_halt()`; spec-patch retirement |
| **4** | Negative validation | 1.5–3 days | 5 refusal behaviors verified with evidence; roadmap diffs; certify block confirmed |
| **5** | Integration testing and release | 2–3 days | Full test coverage; SC-1 through SC-10 verified; manual validation evidence package |

**Total estimated duration**: 11–17 working days

**Critical path**: Phase 0 (OQ-A) → Phase 1 (gates) → Phase 2 (steps + prompts) → Phase 3 (resume) → Phase 4 (negative validation) → Phase 5 (integration)

**Within-phase parallelization**: In Phase 2, prompt authoring (2.1) and remediation module work (2.3) can proceed in parallel once step wiring decisions are made. In Phase 5, unit test completion and integration test scaffolding can be developed concurrently.

**Release gate**: Proceed only after Phase 5 evidence review. Code-complete status is not a release criterion.
