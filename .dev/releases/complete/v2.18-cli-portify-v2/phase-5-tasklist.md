# Phase 5 -- Validation Testing and Cleanup

End-to-end validation with golden fixtures, negative-path testing, MCP degradation testing, resume protocol validation, and final cleanup with sync verification. This phase proves the system works correctly in all expected scenarios before declaring completion.

---

### T05.01 -- Create and Validate 4 Golden Fixture Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-086, R-087, R-088, R-089, R-090 |
| Why | Golden fixtures validate that the complete pipeline produces correct output for representative workflows; they are the primary acceptance test for the system. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | cross-cutting (end-to-end validation spanning all phases), data integrity (determinism verification) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0033/evidence.md

**Deliverables:**
- 4 golden fixture test definitions and validated results (SC-014):
  1. Simple sequential skill: basic portification, all phases pass
  2. Batched audit skill: parallel step groups, trailing gates, complex DAG
  3. Adversarial multi-agent skill: multi-domain, high step count, N:1 mappings
  4. Intentionally unsupported skill: contains dynamic code gen pattern, correctly aborts in Phase 0

**Steps:**
1. **[PLANNING]** Define 4 fixture workflow files with characteristics matching each test scenario
2. **[PLANNING]** Define expected outcomes for each fixture: pass criteria, determinism assertions, conservation invariant checks
3. **[EXECUTION]** Create fixture 1 (simple sequential): define workflow, run full pipeline, verify all phases pass
4. **[EXECUTION]** Create fixture 2 (batched audit): define workflow with parallel groups and trailing gates, run pipeline
5. **[EXECUTION]** Create fixture 3 (adversarial multi-agent): define complex workflow, verify N:1 mappings handled correctly
6. **[EXECUTION]** Create fixture 4 (unsupported): define workflow with dynamic code gen, verify Phase 0 abort
7. **[VERIFICATION]** Verify determinism (SC-002): run each passing fixture twice, diff source_step_registry, step_mapping, module_plan — must be identical
8. **[COMPLETION]** Record all fixture results, determinism verification, and conservation invariant checks in D-0033/evidence.md

**Acceptance Criteria:**
- Fixtures 1-3 produce complete pipeline output with all phases passing and return contract emitted
- Fixture 4 correctly aborts in Phase 0 with unsupported-pattern blocking warning
- Repeated runs of fixtures 1-3 produce identical source_step_registry, step_mapping, and module_plan (SC-002 determinism)
- Step conservation invariant holds for all passing fixtures (SC-007)

**Validation:**
- Manual check: diff of two fixture runs shows zero differences in enumerated artifacts
- Evidence: linkable artifact produced at D-0033/evidence.md

**Dependencies:** T04.07 (complete Phase 4 output required for end-to-end testing)
**Rollback:** Delete fixture definitions (no production impact)
**Notes:** Validates SC-001, SC-002, SC-007, SC-010, SC-011, SC-014.

---

### T05.02 -- Create and Validate 4 Negative-Path Fixture Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-091, R-092, R-093, R-094 |
| Why | Negative-path fixtures prove the system fails safely and correctly for known error scenarios — stale refs, API drift, name collisions, and non-portified code. |
| Effort | L |
| Risk | High |
| Risk Drivers | security (collision safety, non-portified protection), data integrity (stale-ref detection, API drift detection), breaking (failure scenarios) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0034/evidence.md

**Deliverables:**
- 4 negative-path fixture test definitions and validated results:
  5. Stale-ref fixture: ref files with deliberately wrong field names — blocks before Phase 1
  6. API-drift fixture: modified API signatures between snapshot and generation — blocks at conformance check
  7. Name collision fixture: pre-existing non-portified code at output path — aborts with correct error
  8. Non-portified collision fixture: pre-existing human-written code at output path — never overwrites

**Steps:**
1. **[PLANNING]** Define 4 negative-path fixture scenarios with specific error conditions
2. **[PLANNING]** Define expected failure behavior for each: error code, failure phase, abort message
3. **[EXECUTION]** Create fixture 5 (stale-ref): plant wrong field names in refs, verify block before Phase 1
4. **[EXECUTION]** Create fixture 6 (API-drift): modify API signatures after snapshot, verify conformance check blocks
5. **[EXECUTION]** Create fixture 7 (name collision): pre-populate output with non-portified code, verify abort
6. **[EXECUTION]** Create fixture 8 (non-portified collision): pre-populate with human-written code, verify no overwrite
7. **[VERIFICATION]** Verify return contract emitted for all failure scenarios (SC-010); verify correct failure_phase and failure_type in each
8. **[COMPLETION]** Record all negative-path results with failure states and error messages in D-0034/evidence.md

**Acceptance Criteria:**
- Fixture 5: stale-ref detection blocks pipeline before Phase 1 with correct error identifying mismatched fields
- Fixture 6: API drift detection blocks at conformance check with hash mismatch error
- Fixture 7: name collision aborts with NAME_COLLISION error code and no files written
- Fixture 8: non-portified collision results in abort; pre-existing human code is never overwritten (NFR-013)

**Validation:**
- Manual check: each negative fixture produces expected error code and halts at correct phase
- Evidence: linkable artifact produced at D-0034/evidence.md

**Dependencies:** T04.07 (complete pipeline required), T01.02 (stale-ref detector for fixture 5)
**Rollback:** Delete fixture definitions (no production impact)
**Notes:** Validates SC-010, SC-012. Mitigates RISK-001 (drift), RISK-002 (stale refs), RISK-008 (collision), RISK-012 (non-portified).

---

### T05.03 -- Test MCP Degradation for All Servers

| Field | Value |
|---|---|
| Roadmap Item IDs | R-095, R-096, R-097, R-098, R-099 |
| Why | The pipeline must function when MCP servers are unavailable; graceful degradation to native tools ensures reliability in degraded environments. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance (degraded environment), cross-cutting (all MCP servers tested) |
| Tier | STANDARD |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0035/evidence.md

**Deliverables:**
- MCP degradation test results for each of 4 servers: Auggie (codebase-retrieval), Serena, Sequential, Context7
- Verified graceful degradation to native tools (NFR-008)
- Advisory warnings logged in phase contracts when MCP unavailable
- Confirmation that no phase hard-blocks on MCP unavailability

**Steps:**
1. **[PLANNING]** Define MCP unavailability simulation strategy for each of 4 servers
2. **[PLANNING]** Define expected degradation behavior: native tool fallback, advisory warning format
3. **[EXECUTION]** Simulate Auggie unavailability: run pipeline, verify fallback to native file read tools
4. **[EXECUTION]** Simulate Serena unavailability: verify fallback to native grep/glob tools
5. **[EXECUTION]** Simulate Sequential unavailability: verify fallback to native Claude reasoning
6. **[EXECUTION]** Simulate Context7 unavailability: verify fallback to WebSearch
7. **[VERIFICATION]** For each simulation: verify pipeline completes (no hard-block), advisory warnings present in contracts
8. **[COMPLETION]** Record degradation test results for all 4 servers in D-0035/evidence.md

**Acceptance Criteria:**
- Pipeline completes for each of 4 server unavailability scenarios (no hard-blocks)
- Advisory warnings logged in phase contracts when each MCP server is unavailable
- Native tool fallbacks function correctly: file reads, grep/glob, Claude reasoning, WebSearch
- No phase produces hard failure solely due to MCP unavailability

**Validation:**
- Manual check: pipeline output present after each degradation test; advisory warnings in contracts
- Evidence: linkable artifact produced at D-0035/evidence.md

**Dependencies:** T05.01 (need working golden fixture for degradation testing)
**Rollback:** N/A (testing only)
**Notes:** Runs in parallel with T05.01 and T05.04. Mitigates RISK-006.

---

### T05.04 -- Confirm: T05.05 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-100, R-101, R-102, R-103, R-104 |
| Why | Tier classification confidence for T05.05 (resume protocol validation) requires confirmation. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [██████████] 95% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | — |

**Deliverables:**
- Confirmed tier selection for T05.05

**Steps:**
1. **[PLANNING]** Review T05.05 scope: resume protocol validation at all phase boundaries
2. **[EXECUTION]** Confirm or override STRICT tier (resume involves contract validation and state integrity)
3. **[COMPLETION]** Record confirmation

**Acceptance Criteria:**
- Tier decision recorded with justification
- T05.05 unblocked for execution
- Override reason documented if changed
- Decision captured in execution log

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T05.05 -- Validate Resume Protocol at All Phase Boundaries

| Field | Value |
|---|---|
| Roadmap Item IDs | R-100, R-101, R-102, R-103, R-104 |
| Why | Resume protocol must correctly skip completed phases and re-validate contracts on resume to prevent state corruption; this is critical for production reliability. |
| Effort | M |
| Risk | High |
| Risk Drivers | data integrity (contract re-validation on resume), breaking (state corruption prevention), cross-cutting (all phase boundaries tested) |
| Tier | STRICT |
| Confidence | [████████▌-] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0036/evidence.md

**Deliverables:**
- Resume validation results for all 4 phase boundaries (0→1, 1→2, 2→3, 3→4)
- Verified: resume correctly skips completed phases
- Verified: resume re-validates completed phase contracts (not blindly trusted)
- Verified: `resume_command` template in return contract is correct and executable

**Steps:**
1. **[PLANNING]** Define failure simulation strategy for each of 4 phase boundaries
2. **[PLANNING]** Define expected resume behavior: which phases skipped, which re-entered, contract re-validation
3. **[EXECUTION]** Simulate failure at Phase 0→1 boundary: verify resume re-enters Phase 1
4. **[EXECUTION]** Simulate failure at Phase 1→2 boundary: verify resume skips Phase 0, re-validates Phase 0 contract, re-enters Phase 2
5. **[EXECUTION]** Simulate failure at Phase 2→3 and Phase 3→4 boundaries with same verification pattern
6. **[EXECUTION]** Verify resume_command template in return contract matches actual resume invocation syntax
7. **[VERIFICATION]** All 4 boundary resumes: correct phases skipped, contracts re-validated, failure phase re-entered
8. **[COMPLETION]** Record resume test results for all 4 boundaries in D-0036/evidence.md

**Acceptance Criteria:**
- Resume from each of 4 phase boundaries correctly skips completed phases and re-enters failed phase
- Completed phase contracts are re-validated on resume (not blindly trusted)
- `resume_command` template in return contract produces correct resume invocation when executed
- No state corruption detected: filesystem state matches contract state after resume

**Validation:**
- Manual check: resume from Phase 2→3 failure correctly re-validates Phase 0 and Phase 1 contracts before entering Phase 2
- Evidence: linkable artifact produced at D-0036/evidence.md

**Dependencies:** T05.01 (need working fixtures that can be interrupted for resume testing)
**Rollback:** N/A (testing only)
**Notes:** Runs in parallel with T05.01 and T05.03. Mitigates RISK-009. Validates SC-001, FR-052.

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.05

**Purpose:** Verify all validation testing passes before proceeding to final cleanup.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P05-T01-T05.md
**Verification:**
- All 4 golden fixture tests pass with deterministic output verified
- All 4 negative-path fixtures produce correct failure behavior
- MCP degradation produces advisory warnings, not hard failures
**Exit Criteria:**
- Resume from each phase boundary works correctly with contract re-validation
- Determinism verified: repeated runs produce identical enumerated artifacts
- Return contract emitted for both success and failure scenarios

---

### T05.06 -- Confirm: T05.07 Tier Classification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-105, R-106, R-107, R-108, R-109 |
| Why | Tier classification confidence for T05.07 (cleanup and sync) requires confirmation. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [██████████] 95% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | — |

**Deliverables:**
- Confirmed tier selection for T05.07

**Steps:**
1. **[PLANNING]** Review T05.07 scope: directory removal, sync, tests, lint
2. **[EXECUTION]** Confirm or override STANDARD tier
3. **[COMPLETION]** Record confirmation

**Acceptance Criteria:**
- Tier decision recorded with justification
- T05.07 unblocked for execution
- Override reason documented if changed
- Decision captured in execution log

**Validation:**
- Manual check: tier confirmation recorded
- Evidence: decision captured in execution log

**Dependencies:** None
**Rollback:** N/A

---

### T05.07 -- Remove Old Directory, Run Final Sync, Tests, and Lint

| Field | Value |
|---|---|
| Roadmap Item IDs | R-105, R-106, R-107, R-108, R-109 |
| Why | Final cleanup removes the deprecated directory, and sync/test/lint verify the repository is in clean state before declaring completion. |
| Effort | M |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0037/evidence.md

**Deliverables:**
- Removed `sc-cli-portify/` directory (deprecated in Phase 1, all validation passed in Phase 5)
- Verified `make verify-sync` passes with protocol directory included (FR-006)
- Verified `make test` passes with no regressions
- Verified `make lint` passes with no ruff violations in new/modified files

**Steps:**
1. **[PLANNING]** Confirm all Phase 5 validation tasks passed (T05.01-T05.05) before cleanup
2. **[EXECUTION]** Remove old `src/superclaude/skills/sc-cli-portify/` directory and corresponding `.claude/` copy
3. **[EXECUTION]** Run `make verify-sync` — confirm `src/` and `.claude/` match for protocol directory
4. **[EXECUTION]** Run `make test` — all existing tests plus generated structural tests pass
5. **[EXECUTION]** Run `make lint` — no ruff violations in new or modified files
6. **[VERIFICATION]** All 3 commands exit 0: verify-sync, test, lint
7. **[COMPLETION]** Record cleanup actions and verification results in D-0037/evidence.md

**Acceptance Criteria:**
- `src/superclaude/skills/sc-cli-portify/` directory no longer exists (removed, not just deprecated)
- `make verify-sync` exits 0 with `sc-cli-portify-protocol/` in sync scope
- `make test` exits 0 with no regressions (all prior tests still pass)
- `make lint` exits 0 with no ruff violations in new/modified files

**Validation:**
- `make verify-sync && make test && make lint` exits 0
- Evidence: linkable artifact produced at D-0037/evidence.md

**Dependencies:** T05.01 through T05.05 (all validation must pass before cleanup)
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify/`

---

### Checkpoint: End of Phase 5

**Purpose:** Final gate confirming all validation, testing, and cleanup is complete — the system is ready for acceptance.
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/CP-P05-END.md
**Verification:**
- All 4 golden fixture tests pass with deterministic output
- All 4 negative-path fixtures produce correct failure behavior
- MCP degradation, resume validation, and cleanup all verified
**Exit Criteria:**
- Old sc-cli-portify/ directory removed; make verify-sync passes
- make test passes with no regressions; make lint passes with no violations
- All 9 acceptance gate criteria from roadmap verified (golden fixtures, negative fixtures, determinism, safety, integration, contracts, resume, sync, tests)
