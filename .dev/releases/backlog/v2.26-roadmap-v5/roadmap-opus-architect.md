

---
spec_source: v2.25-spec-merged.md
complexity_score: 0.92
primary_persona: architect
---

# v2.25 Roadmap: Deviation-Aware Fidelity Pipeline (v5)

## Executive Summary

v2.25 introduces a **deviation-aware fidelity subsystem** into the roadmap pipeline, solving a systematic failure where intentional architectural improvements were misclassified as specification violations, causing pipeline halts and futile remediation cycles.

The solution adds two new pipeline steps (`annotate-deviations`, `deviation-analysis`) and modifies three existing components (`spec-fidelity`, `remediate`, `certify`), all built on existing executor primitives. The architecture follows a **classify → route → act** pattern: deviations are annotated against the debate record, classified by intent, routed to appropriate handlers (fix, spec-update, no-action, human-review), and only genuine SLIPs reach remediation.

**Key architectural properties:**
- Zero new executor primitives (Step, GateCriteria, SemanticCheck reuse only)
- Sprint pipeline completely isolated — no generic layer modifications
- Bounded recovery: max 3 automatic attempts (1 spec-patch + 2 remediation)
- Fail-closed semantics throughout all new gate checks
- Anti-laundering safeguards via citation requirements and cross-validation

**Scope**: 6 modified source files, 1 potential new module, ~700 lines new code, 5 modified + 1 new test file across 7 domains.

---

## Phase 1: Foundation — Data Model & Gate Infrastructure

**Goal**: Establish the type system, gate definitions, and semantic check functions that all subsequent phases depend on.

**Duration estimate**: 2–3 days

### 1.1 Data Model Changes (models.py)

1. Add `deviation_class: str = "UNCLASSIFIED"` field to `Finding` dataclass
2. Add `VALID_DEVIATION_CLASSES` frozenset: `{"SLIP", "INTENTIONAL", "AMBIGUOUS", "PRE_APPROVED", "UNCLASSIFIED"}`
3. Add `__post_init__` validation of `deviation_class` against `VALID_DEVIATION_CLASSES` (raises `ValueError`)
4. Verify backward compatibility: all existing `Finding` constructors continue to work with the default

**Requirements covered**: FR-030, FR-031, FR-032, NFR-003, NFR-005

### 1.2 Gate Infrastructure (gates.py)

1. **Rename `_parse_frontmatter()` → `parse_frontmatter()`** — update all callers (NFR-021). This must happen first as downstream phases import it.
2. Add semantic check functions (all fail-closed, NFR-016 pattern):
   - `_certified_is_true()` — FR-028
   - `_validation_complete_true()` — FR-053
   - `_no_ambiguous_deviations()` — FR-026
   - `_routing_consistent_with_slip_count()` — FR-056
   - `_pre_approved_not_in_fix_roadmap()` — FR-079
   - `_slip_count_matches_routing()` — FR-081
   - `_total_annotated_consistent()` — FR-085
   - `_total_analyzed_consistent()` — FR-086
   - `_routing_ids_valid()` — FR-074
3. Integer-parsing checks must distinguish missing / malformed / failing values with distinct log messages (FR-080)
4. Define gate criteria:
   - `ANNOTATE_DEVIATIONS_GATE` — STANDARD tier, required fields include `roadmap_hash`, checks: `_total_annotated_consistent` (FR-013, FR-070, FR-085)
   - `DEVIATION_ANALYSIS_GATE` — STRICT tier, 6 semantic checks in order: `no_ambiguous_deviations`, `validation_complete_true`, `routing_consistent_with_slip_count`, `pre_approved_not_in_fix_roadmap`, `slip_count_matches_routing`, `total_analyzed_consistent` (FR-026, FR-027, FR-046, FR-057, FR-079, FR-081, FR-086)
5. Modify `SPEC_FIDELITY_GATE`: downgrade STRICT → STANDARD, remove `high_severity_count_zero` and `tasklist_ready_consistent` from active checks, add `[DEPRECATED v2.25]` docstrings (FR-014, FR-015)
6. Modify `CERTIFY_GATE`: append `certified_true` semantic check (FR-029)
7. Update `ALL_GATES` registry with both new gate entries (FR-054)

**Requirements covered**: FR-013, FR-014, FR-015, FR-026, FR-027, FR-028, FR-029, FR-046, FR-053, FR-054, FR-056, FR-057, FR-070, FR-074, FR-079, FR-080, FR-081, FR-085, FR-086, NFR-007, NFR-021

### 1.3 Resolve Open Question OQ-A (FR-079)

- **Decision required before coding**: Does `GateCriteria.aux_inputs` exist?
  - **If yes (Option A)**: Pass `pre_approved_ids` via aux_inputs to `_pre_approved_not_in_fix_roadmap()`
  - **If no (Option B)**: Embed `pre_approved_ids` as comma-separated frontmatter field in `deviation-analysis.md`
- This decision cascades to OQ-B (FR-088 extended validation) and OQ-C (body parsing approach)
- **Recommendation**: Inspect current `GateCriteria` in `models.py`. If `aux_inputs` exists, prefer Option A for cleaner separation. If not, use Option B and document the frontmatter contract.

### 1.4 Milestone Gate

- [ ] `Finding("test", deviation_class="SLIP")` constructs successfully
- [ ] `Finding("test", deviation_class="INVALID")` raises `ValueError`
- [ ] `Finding("test")` defaults to `"UNCLASSIFIED"`
- [ ] All 10 semantic check functions pass unit tests with boundary inputs
- [ ] `parse_frontmatter()` is public; all callers updated
- [ ] `SPEC_FIDELITY_GATE` is STANDARD tier
- [ ] `CERTIFY_GATE` includes `certified_true` check
- [ ] OQ-A resolved and documented

---

## Phase 2: New Pipeline Steps — Prompts, Step Wiring, and Artifact Contracts

**Goal**: Implement the two new steps (`annotate-deviations`, `deviation-analysis`) with their prompts, step definitions, and artifact output contracts.

**Duration estimate**: 3–4 days

**Depends on**: Phase 1 complete (gates, data model, `parse_frontmatter()` public)

### 2.1 Prompt Builders (prompts.py)

1. **`build_annotate_deviations_prompt()`** — new function
   - Inputs: `spec_file` (original, not extraction — FR-005), `roadmap.md`, `debate-transcript.md`, `diff-analysis.md`
   - Classification taxonomy: `INTENTIONAL_IMPROVEMENT`, `INTENTIONAL_PREFERENCE`, `SCOPE_ADDITION`, `NOT_DISCUSSED` (FR-006)
   - Anti-laundering rules: `INTENTIONAL_IMPROVEMENT` requires D-XX + round citation (FR-007, FR-008, FR-009, FR-010)
   - Output contract: `spec-deviations.md` with specified YAML frontmatter (FR-011) and body format (FR-012)
   - Must include `schema_version: "2.25"` as first frontmatter field (NFR-023)

2. **`build_deviation_analysis_prompt()`** — new function
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

3. **Modify `build_spec_fidelity_prompt()`** — add `spec_deviations_path: Path | None = None` parameter (FR-016)
   - When provided: instruct agent to VERIFY citations, EXCLUDE verified `INTENTIONAL_IMPROVEMENT`, REPORT invalid annotations as HIGH, ANALYZE `NOT_DISCUSSED` independently (FR-017)

**Requirements covered**: FR-003, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-016, FR-017, FR-021, FR-022, FR-023, FR-024, FR-025, FR-045, FR-073, FR-078, FR-087, FR-090, NFR-023

### 2.2 Step Wiring (executor.py)

1. Add `annotate-deviations` step in `_build_steps()` between `merge` and `test-strategy` (FR-004)
   - Inputs: `spec_file`, `roadmap.md`, `debate-transcript.md`, `diff-analysis.md`
   - Output: `spec-deviations.md`
   - Gate: `ANNOTATE_DEVIATIONS_GATE` (STANDARD), timeout 300s, retry_limit=0
2. Add `deviation-analysis` step in `_build_steps()` after `spec-fidelity` (FR-020)
   - Inputs: `spec-fidelity.md`, `debate-transcript.md`, `diff-analysis.md`, `spec-deviations.md`, `roadmap-A.md`, `roadmap-B.md`
   - Output: `deviation-analysis.md`
   - Gate: `DEVIATION_ANALYSIS_GATE` (STRICT), timeout 300s, retry_limit=1
3. Update `_get_all_step_ids()` to include both new steps in correct pipeline order (FR-038)
4. Pass `spec-deviations.md` as additional input to `spec-fidelity` step (FR-018)
5. Add `roadmap_hash` injection after `annotate-deviations` subprocess completes (FR-055)
   - SHA-256 of `roadmap.md` at injection time
   - Atomic write: `.tmp` + `os.replace()` (NFR-022)
6. Record `started_at`, `completed_at`, `token_count` for new steps in `_save_state()` (NFR-024)

**Requirements covered**: FR-002, FR-003, FR-004, FR-018, FR-019, FR-020, FR-038, FR-055, NFR-002, NFR-022, NFR-024

### 2.3 Remediation Module (remediate.py)

1. **`deviations_to_findings()`** — new function (FR-033)
   - Converts classified deviations into `Finding` objects
   - Only produces findings for deviations routed to `fix_roadmap` (FR-035)
   - Severity mapping: HIGH→BLOCKING, MEDIUM→WARNING, LOW→INFO (FR-034)
   - `ValueError` if routing is empty but `slip_count > 0` (defense-in-depth, FR-058)
   - WARNING log when routing ID not found in fidelity table (FR-082)
2. **`_parse_routing_list()`** — new function (FR-075, FR-083)
   - Split on `,`, strip whitespace immediately
   - Validate each token against `re.compile(r'^DEV-\d+$')`
   - Log WARNING and exclude non-conforming tokens
   - Cross-check `len(returned_tokens)` against `total_analyzed`
3. Update remediation step to use `deviation-analysis.md` routing table as primary input (FR-036)
4. Update remediation prompt with deviation-class awareness (FR-037)

**Requirements covered**: FR-033, FR-034, FR-035, FR-036, FR-037, FR-058, FR-075, FR-082, FR-083

### 2.4 Milestone Gate

- [ ] Both prompts produce well-formed output contracts (manual prompt review)
- [ ] Pipeline step order matches FR-002 exactly
- [ ] `_get_all_step_ids()` returns 13 steps in correct order
- [ ] `roadmap_hash` injection uses atomic write pattern
- [ ] `deviations_to_findings()` unit tests pass for all severity mappings
- [ ] `_parse_routing_list()` handles edge cases: empty string, whitespace, invalid IDs, valid IDs

---

## Phase 3: Resume Logic, Recovery Mechanisms & Retirement

**Goal**: Implement resume freshness detection, remediation budget enforcement, and retire the spec-patch auto-resume cycle.

**Duration estimate**: 2–3 days

**Depends on**: Phase 2 complete (steps wired, hash injection working)

### 3.1 Resume Logic Enhancements (executor.py)

1. **`_check_annotate_deviations_freshness()`** — new function (FR-071, NFR-016)
   - Compare `roadmap_hash` in `spec-deviations.md` against current SHA-256 of `roadmap.md`
   - Fail-closed: missing file, missing field, read error → return `False`
   - When returning `False`: re-add `annotate-deviations` to execution queue
   - Also reset gate-pass state for `spec-fidelity` and `deviation-analysis` (FR-084)
2. Integrate freshness check into `_apply_resume()` before skipping `annotate-deviations` (FR-071)

**Requirements covered**: FR-071, FR-084, NFR-016, NFR-020

### 3.2 Remediation Budget (executor.py)

1. Add `remediation_attempts` counter to `.roadmap-state.json` (FR-039)
2. **`_check_remediation_budget()`** — new function (FR-040, FR-041)
   - Coerce `remediation_attempts` to `int` before comparison (FR-072)
   - Coercion failure: log WARNING, treat as 0
   - Max 2 attempts (configurable via `max_attempts` parameter)
   - On budget exhaustion: call `_print_terminal_halt()` and return `False`
   - Must NOT call `sys.exit(1)` directly — callers own exit (Constraint #12)
3. **`_print_terminal_halt()`** — new/modified function (FR-042)
   - Output to stderr: attempt count, failing finding count, per-finding details, manual-fix instructions with cert report path and resume command
4. Caller logic: on third `--resume` attempt (budget exhausted), `sys.exit(1)` (FR-044)
5. Atomic state writes: `.tmp` + `os.replace()` for `.roadmap-state.json` (NFR-022)
6. `_save_state()` coerces `existing_attempts` to `int` before incrementing (NFR-017)

**Requirements covered**: FR-039, FR-040, FR-041, FR-042, FR-043, FR-044, FR-072, NFR-008, NFR-017, NFR-018, NFR-022

### 3.3 Spec-Patch Cycle Retirement (executor.py)

1. Retire `_apply_resume_after_spec_patch()` from active execution (FR-059)
2. Retain `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` as functionally dormant (NFR-019)
3. Ensure spec-patch and remediation budgets remain independent counters (FR-076)
4. When both mechanisms exhausted, `_print_terminal_halt()` includes note about both (FR-077 — placeholder for v2.25, mechanism deferred to v2.26 per OQ-J)

**Requirements covered**: FR-059, FR-076, FR-077, NFR-011, NFR-019

### 3.4 Graceful Degradation (executor.py)

1. When `annotate-deviations` produces `total_annotated: 0`, log INFO and continue — `deviation-analysis` acts as backstop (FR-089)
2. When `DEVIATION_ANALYSIS_GATE` fails on `ambiguous_count > 0`, halt with STRICT gate failure; log operator instructions for manual reclassification (FR-091)
3. Print `routing_update_spec` summary in CLI output when non-empty (FR-087)

**Requirements covered**: FR-089, FR-091

### 3.5 Milestone Gate

- [ ] `_check_annotate_deviations_freshness()` passes all 9 test cases (SC-8)
- [ ] Freshness mismatch triggers re-run of `annotate-deviations` + resets `spec-fidelity` and `deviation-analysis` gates
- [ ] Remediation budget caps at 2 attempts; third attempt triggers terminal halt
- [ ] `_print_terminal_halt()` produces correct stderr output
- [ ] Coercion handling: non-integer `remediation_attempts` treated as 0 with WARNING
- [ ] Existing `.roadmap-state.json` without `remediation_attempts` handled gracefully (defaults to 0)
- [ ] `_apply_resume_after_spec_patch()` code retained but never invoked in normal v2.25 flow

---

## Phase 4: Integration Testing & Validation

**Goal**: Validate the complete pipeline against real and mock scenarios, confirming all success criteria.

**Duration estimate**: 2–3 days

**Depends on**: Phases 1–3 complete

### 4.1 Unit Tests

1. `tests/roadmap/test_gates_data.py` — all 10 semantic check functions with boundary inputs (SC-9)
   - Each of the 6 `DEVIATION_ANALYSIS_GATE` checks: correct return for valid/invalid/missing/malformed inputs
   - `_certified_is_true`: true/false/missing/malformed cases (SC-5)
   - `_total_annotated_consistent`: sum matches / doesn't match
   - `_routing_ids_valid`: valid DEV-\d+ / invalid / empty / mixed
2. `tests/roadmap/test_models.py` — `Finding` with `deviation_class` (existing + new field)
3. `tests/roadmap/test_remediate.py` — `deviations_to_findings()` and `_parse_routing_list()`
4. `tests/roadmap/test_executor.py` — `_check_annotate_deviations_freshness()` 9 test cases, `_check_remediation_budget()`

### 4.2 Integration Tests

1. **`tests/roadmap/test_integration_v5_pipeline.py`** — new file
   - v2.24 scenario fixtures with pre-recorded subprocess outputs (no live Claude calls)
   - Validate complete pipeline flow: extract → ... → certify
   - SC-1: Pipeline reaches certify without manual intervention
   - SC-2: D-02 and D-04 pre-approved, excluded from HIGH count
   - SC-3: DEV-002 and DEV-003 classified as SLIP, routed to fix_roadmap
   - SC-4: Remediation modifies only SLIP-routed elements
   - SC-6: Terminal halt after 2 failed remediation attempts
2. Verify NFR-009/NFR-010: `pipeline/executor.py` and `pipeline/models.py` have zero modifications

### 4.3 Manual Validation Run

1. Execute full pipeline against v2.24 spec file
2. Inspect artifacts:
   - `spec-deviations.md`: classification correctness, citation format, `roadmap_hash` present, `schema_version: "2.25"` (SC-10)
   - `deviation-analysis.md`: routing correctness, blast radius entries, `schema_version: "2.25"` (SC-10)
   - `spec-fidelity.md`: excluded intentional deviations from HIGH count
3. Verify pipeline completes without halting at fidelity (SC-1)
4. Verify SC-7: no new classes in `pipeline/models.py` or `pipeline/executor.py`

### 4.4 Milestone Gate (Final)

- [ ] All unit tests pass (`uv run pytest tests/roadmap/ -v`)
- [ ] Integration tests pass with mock subprocess outputs
- [ ] SC-1 through SC-10 all verified
- [ ] No regressions in existing test suite
- [ ] Zero modifications to generic pipeline layer (NFR-009, NFR-010)
- [ ] Artifact `schema_version` fields present (NFR-023)

---

## Risk Assessment & Mitigation

### Risk Matrix

| ID | Risk | Severity | Probability | Mitigation | Phase |
|----|------|----------|-------------|------------|-------|
| R-1 | Annotator over-approval (deviation laundering) | HIGH | LOW | Separate subprocess, D-XX citation requirement, fidelity cross-validation | 2 |
| R-2 | Deviation-analysis misclassifies SLIPs | MEDIUM | LOW | D-XX + round matching, independent fidelity ground truth | 2 |
| R-3 | +600s pipeline cost | LOW | HIGH | Eliminates 1200s retry cost on failure paths; net positive | 2 |
| R-4 | Context window pressure on annotate-deviations | MEDIUM | MEDIUM | Input set comparable to merge step; within 200KB limit | 2 |
| R-5 | Remediate-certify non-convergence | MEDIUM | LOW | 2-attempt budget, terminal halt with manual instructions | 3 |
| R-6 | Resume logic complexity | LOW | LOW | Follows existing resume pattern; no new primitives | 3 |
| R-7 | STANDARD downgrade masks issues | MEDIUM | LOW | deviation-analysis STRICT gate catches all real issues | 1 |
| R-8 | Finding.deviation_class breaks consumers | LOW | LOW | Default "UNCLASSIFIED", __post_init__ validates | 1 |
| R-9 | YAML frontmatter parsing fragility | MEDIUM | MEDIUM | Flat comma-separated fields, token normalization | 2 |

### Architectural Risks Not in Spec

| Risk | Assessment | Mitigation |
|------|-----------|------------|
| Phase 1 gate changes break existing tests | MEDIUM probability | Run full test suite after Phase 1; STANDARD downgrade is relaxation, unlikely to break |
| `parse_frontmatter()` rename causes import errors | LOW probability | Grep all callers before rename; single atomic commit |
| Circular import from `_parse_routing_list()` in wrong module | MEDIUM probability | Resolve module placement (remediate.py vs new parsing.py) during Phase 2 start |
| OQ-A decision delays Phase 1 | HIGH probability | Resolve immediately by inspecting `GateCriteria` definition; 30-minute task |

---

## Resource Requirements & Dependencies

### Files Modified (by phase)

| Phase | File | Changes |
|-------|------|---------|
| 1 | `models.py` | `Finding.deviation_class`, `VALID_DEVIATION_CLASSES`, `__post_init__` |
| 1 | `gates.py` | `parse_frontmatter()` rename, 10 semantic checks, 3 gate definitions modified/added, `ALL_GATES` |
| 2 | `prompts.py` | 2 new prompt builders, 1 modified (`build_spec_fidelity_prompt`) |
| 2 | `executor.py` | `_build_steps()`, `_get_all_step_ids()`, hash injection, step inputs |
| 2 | `remediate.py` | `deviations_to_findings()`, `_parse_routing_list()`, input source change |
| 2 | `remediate_prompts.py` | Deviation-class awareness in remediation prompt |
| 3 | `executor.py` | Resume freshness, remediation budget, terminal halt, spec-patch retirement |
| 3 | (potentially) `parsing.py` | New module if circular imports require `_parse_routing_list()` extraction |

### External Dependencies

- All stdlib: `hashlib`, `os`, `re`, `json` — no new third-party dependencies
- Claude subprocess API — existing; `token_count` field is best-effort (NFR-024 / OQ-I)

### Pre-Implementation Decisions Required

1. **OQ-A**: `GateCriteria.aux_inputs` existence → Option A or B for FR-079
2. **OQ-B**: FR-088 extended validation deferral if no `aux_inputs`
3. **OQ-C**: Body parsing approach for `PRE_APPROVED` IDs
4. **OQ-G**: Confirm `build_remediate_step()` module location from v2.24.2 codebase
5. **OQ-H**: Confirm `roadmap_run_step()` interface for hash injection hook

---

## Success Criteria Validation Approach

| SC | Criterion | Verification Method | Phase |
|----|-----------|-------------------|-------|
| SC-1 | Pipeline processes v2.24 spec without fidelity halt | Integration test + manual run | 4 |
| SC-2 | D-02, D-04 pre-approved, excluded from HIGH | Artifact inspection | 4 |
| SC-3 | DEV-002, DEV-003 classified SLIP, routed to fix_roadmap | Artifact inspection | 4 |
| SC-4 | Remediation targets only SLIPs | Diff roadmap.md before/after | 4 |
| SC-5 | Certify blocks on `certified: false` | Unit test `_certified_is_true` | 1 |
| SC-6 | Terminal halt after 2 failed remediations | Integration test with mock | 3–4 |
| SC-7 | No new executor primitives | Static diff inspection | 4 |
| SC-8 | Freshness check passes 9 test cases | Unit tests | 3 |
| SC-9 | DEVIATION_ANALYSIS_GATE 6 checks correct | Unit tests | 1, 4 |
| SC-10 | `schema_version: "2.25"` in artifacts | Artifact inspection | 4 |

---

## Timeline Summary

| Phase | Name | Duration | Dependencies | Key Deliverables |
|-------|------|----------|-------------|-----------------|
| **0** | Pre-implementation decisions | 0.5 day | None | OQ-A through OQ-H resolved |
| **1** | Foundation | 2–3 days | Phase 0 | Data model, gates, semantic checks |
| **2** | New pipeline steps | 3–4 days | Phase 1 | Prompts, step wiring, remediation module |
| **3** | Resume & recovery | 2–3 days | Phase 2 | Freshness detection, budget enforcement, retirement |
| **4** | Integration & validation | 2–3 days | Phases 1–3 | Full test coverage, SC-1 through SC-10 verified |

**Total estimated duration**: 10–14 working days

**Critical path**: Phase 0 (OQ-A) → Phase 1 (gates) → Phase 2 (steps + prompts) → Phase 3 (resume) → Phase 4 (validation)

No phases can be parallelized — each depends on the prior phase's deliverables. However, within Phase 2, prompt authoring (2.1) and remediation module work (2.3) can proceed in parallel once step wiring decisions (2.2) are made. Within Phase 4, unit tests (4.1) and integration test scaffolding (4.2) can be developed concurrently.
