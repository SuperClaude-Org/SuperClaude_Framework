# Phase 4 -- Contract & Command Surface

Update return contract schema, CLI command flags, and validate failure paths. This phase modifies the contract to include all new fields, updates dry-run behavior, removes the deprecated flag, and validates all failure path defaults.

### T04.01 -- Update Return Contract Schema in SKILL.md with All New Fields

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032, R-033 |
| Why | The roadmap requires updating the return contract (FR-015) with 18+ new fields including `contract_version`, `spec_file`, `panel_report`, `quality_scores`, `convergence_iterations`, `phase_timing`, `resume_substep`, `downstream_ready`, `warnings`, `failure_type` enumeration, and resume behavior semantics for Phase 3 and Phase 4. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | schema, breaking (contract schema change affects downstream consumers) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0024, D-0025 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0024/spec.md
- TASKLIST_ROOT/artifacts/D-0025/spec.md

**Deliverables:**
1. Updated return contract schema in SKILL.md with all new fields: `contract_version`, `spec_file`, `panel_report`, `quality_scores` (5 fields: clarity, completeness, testability, consistency, overall), `convergence_iterations`, `phase_timing`, `resume_substep`, `downstream_ready`, `warnings`, `output_directory`, `failure_phase`, `failure_type`, `source_step_count`, `spec_fr_count`, `api_snapshot_hash`, `resume_command`, `resume_phase`, `phase_contracts`
2. Resume behavior semantics documented: Phase 3 resume (`resume_substep=3c`) preserves populated spec from 3b, brainstorm re-runs from 3c; Phase 4 resume (`resume_substep=4a`) preserves draft spec from Phase 3, review re-runs from 4a; all prior phase artifacts preserved on resume

**Steps:**
1. **[PLANNING]** Read current return contract schema in SKILL.md to identify existing fields
2. **[PLANNING]** Map all 18+ new fields from R-032 to their types and default values
3. **[EXECUTION]** Add all new fields to the return contract schema in SKILL.md
4. **[EXECUTION]** Define `failure_type` enumeration: `template_failed | brainstorm_failed | brainstorm_timeout | focus_failed | critique_failed | convergence_exhausted | user_rejected`
5. **[EXECUTION]** Specify contract emission on every invocation including failures (SC-009)
6. **[EXECUTION]** Document resume behavior: Phase 3 resume preserves 3b output, Phase 4 resume preserves Phase 3 output
7. **[VERIFICATION]** Verify all fields present, `failure_type` has all 7 enumeration values, contract emits on all paths
8. **[COMPLETION]** Document complete contract schema with field types and defaults

**Acceptance Criteria:**
- SKILL.md return contract contains all 18+ new fields as specified in R-032
- `failure_type` enumeration includes all 7 values: `template_failed`, `brainstorm_failed`, `brainstorm_timeout`, `focus_failed`, `critique_failed`, `convergence_exhausted`, `user_rejected`
- Contract emitted on every invocation including failures (SC-009)
- Resume behavior semantics documented for Phase 3 (`resume_substep=3c`) and Phase 4 (`resume_substep=4a`) with artifact preservation rules

**Validation:**
- Manual check: SKILL.md return contract schema contains all fields from R-032 with correct types, defaults, and resume semantics
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0024/spec.md)

**Dependencies:** T03.07
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
**Notes:** Tier STRICT due to "schema" + "api contract" keyword match. Sub-agent delegation required (STRICT + Risk Medium).

---

### T04.02 -- Update --dry-run Behavior in cli-portify.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | The roadmap requires updating `--dry-run` behavior (FR-016): execute Phases 0-2 only, emit Phase 0-2 contracts only, no spec synthesis or panel review artifacts. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0026/spec.md

**Deliverables:**
1. Updated `--dry-run` behavior in `src/superclaude/commands/cli-portify.md`: execute Phases 0-2 only, emit Phase 0-2 contracts only, produce no spec synthesis or panel review artifacts

**Steps:**
1. **[PLANNING]** Read current `--dry-run` behavior in `src/superclaude/commands/cli-portify.md`
2. **[PLANNING]** Identify sections referencing dry-run behavior
3. **[EXECUTION]** Update `--dry-run` description to specify: execute Phases 0-2 only
4. **[EXECUTION]** Specify: emit Phase 0-2 contracts only, no spec synthesis (Phase 3) or panel review (Phase 4) artifacts
5. **[VERIFICATION]** Verify `--dry-run` documentation matches FR-016 specification
6. **[COMPLETION]** Document updated dry-run behavior

**Acceptance Criteria:**
- `src/superclaude/commands/cli-portify.md` specifies `--dry-run` executes Phases 0-2 only
- `--dry-run` emits only Phase 0-2 contracts, no Phase 3/4 artifacts
- No spec synthesis or panel review operations execute under `--dry-run`
- SC-002 dry run validation criteria documented

**Validation:**
- Manual check: `cli-portify.md` `--dry-run` section specifies Phase 0-2 only execution with no Phase 3/4 artifacts
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0026/spec.md)

**Dependencies:** T04.01
**Rollback:** `git checkout -- src/superclaude/commands/cli-portify.md`

---

### T04.03 -- Remove --skip-integration Flag from cli-portify.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035 |
| Why | The roadmap requires removing the `--skip-integration` flag from `cli-portify.md` (SC-014) since integration phase no longer exists. |
| Effort | XS |
| Risk | Medium |
| Risk Drivers | breaking (API surface change — removing a CLI flag) |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0027/notes.md

**Deliverables:**
1. `--skip-integration` flag removed from `src/superclaude/commands/cli-portify.md` with no residual references

**Steps:**
1. **[PLANNING]** Locate `--skip-integration` flag definition in `src/superclaude/commands/cli-portify.md`
2. **[PLANNING]** Search for any other references to `--skip-integration` across the codebase
3. **[EXECUTION]** Remove `--skip-integration` flag definition from cli-portify.md
4. **[EXECUTION]** Remove any documentation referencing `--skip-integration` behavior
5. **[VERIFICATION]** `grep -rn 'skip-integration' src/superclaude/` returns zero results
6. **[COMPLETION]** Document flag removal

**Acceptance Criteria:**
- `--skip-integration` flag absent from `src/superclaude/commands/cli-portify.md`
- `grep -rn 'skip-integration' src/superclaude/` returns zero results across entire source tree
- Flag rejected by command if user attempts to pass it (SC-014)
- No residual documentation references to the removed flag

**Validation:**
- Manual check: `grep -rn 'skip-integration' src/superclaude/` returns zero matches
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0027/notes.md)

**Dependencies:** T04.01
**Rollback:** `git checkout -- src/superclaude/commands/cli-portify.md`
**Notes:** Tier STRICT due to "change api" compound override — removing a CLI flag is a breaking API surface change.

---

### T04.04 -- Update refs/pipeline-spec.md for Phase 2→3 Bridge

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | The roadmap requires updating `refs/pipeline-spec.md` to document the Phase 2→3 bridge (D-008), reflecting the new transition from Phase 2 (workflow analysis) to Phase 3 (spec synthesis). |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████▓░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0028/spec.md

**Deliverables:**
1. Updated `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md` documenting the Phase 2→3 bridge: Phase 2 outputs flow into Phase 3 spec synthesis instead of code generation

**Steps:**
1. **[PLANNING]** Read current `refs/pipeline-spec.md` to understand existing Phase 2→3 transition documentation
2. **[PLANNING]** Identify sections describing Phase 2 output consumption
3. **[EXECUTION]** Update Phase 2→3 bridge documentation to reflect spec synthesis as the Phase 3 consumer
4. **[EXECUTION]** Remove references to code generation as Phase 3 output
5. **[VERIFICATION]** Verify pipeline-spec.md Phase 2→3 bridge is consistent with SKILL.md Phase 3 entry gate
6. **[COMPLETION]** Document bridge update

**Acceptance Criteria:**
- `refs/pipeline-spec.md` documents Phase 2→3 bridge with Phase 2 outputs flowing to spec synthesis (not code generation)
- Pipeline diagram or description reflects new Phase 3 (spec synthesis) and Phase 4 (panel review)
- No residual references to code generation as Phase 3 output in pipeline-spec.md
- Bridge documentation consistent with SKILL.md Phase 2→3 entry gate conditions

**Validation:**
- Manual check: `refs/pipeline-spec.md` Phase 2→3 section references spec synthesis as downstream consumer
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0028/spec.md)

**Dependencies:** T04.01
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md`

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.04

**Purpose:** Verify contract schema and command surface updates are complete before failure path validation.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P04-T01-T04.md
**Verification:**
- Return contract contains all 18+ new fields with correct types and defaults
- `--dry-run` behavior updated to Phase 0-2 only execution
- `--skip-integration` flag removed with zero residual references
**Exit Criteria:**
- Tasks T04.01-T04.04 completed with deliverables D-0024 through D-0028 produced
- `failure_type` enumeration has all 7 values
- Resume behavior semantics documented for Phase 3 and Phase 4

---

### T04.05 -- Validate Contract Failure Paths

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | The roadmap requires early validation of contract failure paths (debate D-06, D-14): quality scores default to `0.0` on failure (not null), `downstream_ready = false` on failure, contract schema complete on all paths, `resume_substep` populated for resumable failures, boundary test at 7.0 threshold. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema (contract validation), breaking (failure path correctness) |
| Tier | STRICT |
| Confidence | [███████░░░] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0029/evidence.md

**Deliverables:**
1. Contract failure path validation results confirming: quality scores = `0.0` on failure (not null per NFR-009), `downstream_ready = false` on failure, contract schema complete on all paths (success, partial, failure), `resume_substep` populated for resumable failures, boundary test `overall = 7.0` → ready and `overall = 6.9` → not ready (SC-012)

**Steps:**
1. **[PLANNING]** Enumerate all contract emission paths: success, partial (convergence exhausted), failure (7 failure types), dry-run
2. **[PLANNING]** Define expected field values for each path
3. **[EXECUTION]** Verify quality scores default to `0.0` (not null) on all failure paths
4. **[EXECUTION]** Verify `downstream_ready = false` on all failure and partial paths
5. **[EXECUTION]** Verify contract schema is complete (all fields present) on every emission path
6. **[EXECUTION]** Verify `resume_substep` populated for resumable failure types
7. **[VERIFICATION]** Test boundary: `overall = 7.0` → `downstream_ready: true`, `overall = 6.9` → `downstream_ready: false` (SC-012)
8. **[COMPLETION]** Document validation results for all paths

**Acceptance Criteria:**
- On failure: all quality scores = `0.0` (not null), `downstream_ready = false` per NFR-009
- Contract schema complete on all 4 paths: success, partial, failure, dry-run (SC-009)
- `resume_substep` populated for resumable failures: `3c` (brainstorm), `4a` (focus pass)
- Boundary test passes: `overall = 7.0` → `downstream_ready: true`, `overall = 6.9` → `downstream_ready: false` (SC-012)

**Validation:**
- Manual check: Contract emission verified on all 4 paths with correct defaults and boundary behavior at 7.0 threshold
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0029/evidence.md)

**Dependencies:** T04.01, T04.02, T04.03, T04.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Tier conflict: "validate" → EXEMPT vs "schema" → STRICT. Resolved to STRICT by priority rule (STRICT > EXEMPT).

---

### Checkpoint: End of Phase 4

**Purpose:** Verify Gate C criteria are met: return contract emitted on success, failure, and dry-run (SC-009), `--skip-integration` flag rejected (SC-014), quality score formula verified (SC-010), all failure path defaults validated.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P04-END.md
**Verification:**
- Return contract emitted on all paths: success, failure, partial, and dry-run (SC-009)
- `--skip-integration` flag returns error when passed to command (SC-014)
- Quality formula `overall == mean(clarity, completeness, testability, consistency)` verified (SC-010)
- SC-010 is preserved here as a Gate C checkpoint criterion; detailed formula validation is exercised in Phase 5 task T05.03
**Exit Criteria:**
- All 5 tasks (T04.01-T04.05) completed with deliverables D-0024 through D-0029 produced
- All failure path defaults validated (quality scores 0.0, downstream_ready false)
- Boundary behavior at 7.0 threshold confirmed
