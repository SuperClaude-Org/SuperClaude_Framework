# TASKLIST — v2.01 Architecture Refactor — Phase 3

**Parent document**: `TASKLIST_ROOT/tasklist-header.md`
**TASKLIST_ROOT**: `.dev/releases/current/v2.01-Architecture-Refactor/`

---

## Phase 3: Build System Enforcement

Implement CI enforcement infrastructure before any structural migration work per Rule 7.5: enforcement BEFORE migration. Remove the old skill-skip heuristic from `sync-dev` and `verify-sync`, add the `lint-architecture` target implementing 6 designed checks, and validate with both positive and negative tests.

---

### T03.01 — Remove Skill-Skip Heuristic from `sync-dev` and `verify-sync`

**Roadmap Item ID(s):** R-015
**Why:** The Makefile contains a 4-line heuristic in `sync-dev` and a 5-line heuristic in `verify-sync` that skip syncing skills "served by commands." This heuristic is incompatible with the `-protocol` naming convention where commands delegate TO skills — both must exist in `.claude/`.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** build system change, deploy/infra keyword match
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0017
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0017/evidence.md`

**Deliverables:**
1. Updated Makefile with skill-skip heuristics removed from both `sync-dev` and `verify-sync` targets

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §11 (make sync-dev/verify-sync changes); locate heuristic code in Makefile
2. **[PLANNING]** Check dependencies: Phase 2 complete (skill directories renamed with `-protocol` suffix)
3. **[EXECUTION]** Remove 4-line skill-skip heuristic from `sync-dev` target
4. **[EXECUTION]** Remove 5-line skip heuristic with "served by command" message from `verify-sync` target
5. **[EXECUTION]** Verify new behavior: ALL skills including `-protocol` ones are synced and checked
6. **[VERIFICATION]** Run `make sync-dev && make verify-sync` — both exit 0 with all skills synced
7. **[COMPLETION]** Document changes and verification in `TASKLIST_ROOT/artifacts/D-0017/evidence.md`

**Acceptance Criteria:**
- Old 4-line heuristic removed from `sync-dev` (no skill skipping)
- Old 5-line heuristic removed from `verify-sync` (no "served by command" skip)
- `make sync-dev` syncs ALL skills including `-protocol` directories
- `make verify-sync` checks ALL skills for sync drift

**Validation:**
- `make sync-dev && make verify-sync` exits 0 with all skills synced
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0017/evidence.md`

**Dependencies:** Phase 2 complete (T02.05 skill renames)
**Rollback:** Restore heuristic lines from git history
**Notes:** Part of Group B atomic unit (§13.7). Must be applied with T03.02 Makefile changes.

---

### T03.02 — Add `lint-architecture` Target to Makefile

**Roadmap Item ID(s):** R-016, R-018
**Why:** The architecture policy specifies 10 CI checks but none were implemented. This task adds the `lint-architecture` target implementing 6 designed checks (#1-4, #6, #8-9) plus updates `.PHONY` and `help` targets.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** ci/pipeline keyword match, build system change
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0018
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0018/spec.md`
- `TASKLIST_ROOT/artifacts/D-0018/evidence.md`

**Deliverables:**
1. `lint-architecture` target in Makefile implementing 6 checks with ERROR/WARN exit behavior
2. `.PHONY` and `help` targets updated to reference `lint-architecture`

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §11 (all 10 policy-defined checks; 6 are DESIGNED)
2. **[PLANNING]** Check dependencies: T03.01 complete (heuristics removed); skill renames in place
3. **[EXECUTION]** Implement Check #1: Command → Skill link (ERROR)
4. **[EXECUTION]** Implement Check #2: Skill → Command link (ERROR); Check #3: Command size WARN >200; Check #4: Command size ERROR >500
5. **[EXECUTION]** Implement Check #6: Activation section present (ERROR); Check #8: Skill frontmatter complete (ERROR); Check #9: Protocol naming consistency (ERROR)
6. **[EXECUTION]** Add `lint-architecture` to `.PHONY` target and `help` target descriptions
7. **[VERIFICATION]** Run `make lint-architecture` — verify all 6 checks execute and produce expected output
8. **[COMPLETION]** Document implementation and check behavior in D-0018 artifacts

**Acceptance Criteria:**
- `lint-architecture` target exists in Makefile and is executable
- All 6 checks (#1, #2, #3, #4, #6, #8, #9) implemented per §11 specifications
- Any ERROR → `exit 1` (CI failure); warnings only → `exit 0`
- Target discoverable via `make help`

**Validation:**
- `make lint-architecture` executes all 6 checks with appropriate output
- Evidence: linkable artifacts produced at D-0018 spec and evidence paths

**Dependencies:** T03.01
**Rollback:** Remove `lint-architecture` target and `.PHONY`/`help` references
**Notes:** 4 checks deferred: #5 (inline protocol detection — needs design), #7 (activation references correct skill — needs design), #10 (sync integrity — delegated to `verify-sync`). Risk R-005 applies. Part of Group B atomic unit.

---

### T03.03 — Run `make lint-architecture` and Resolve ERRORs

**Roadmap Item ID(s):** R-017
**Why:** The newly created `lint-architecture` target must pass on the current tree before any Phase 4 work begins. All ERROR-level findings must be resolved.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0019
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0019/evidence.md`

**Deliverables:**
1. `make lint-architecture` exits 0 on the current codebase (all ERRORs resolved)

**Steps:**
1. **[PLANNING]** Load context: T03.02 lint-architecture implementation; expected check behavior
2. **[PLANNING]** Check dependencies: T03.02 complete (target exists)
3. **[EXECUTION]** Run `make lint-architecture` against current tree
4. **[EXECUTION]** If any ERRORs: fix the underlying issues (missing links, naming inconsistencies, etc.)
5. **[EXECUTION]** Re-run `make lint-architecture` until exit 0
6. **[VERIFICATION]** Final run exits 0 with all 6 checks passing
7. **[COMPLETION]** Record lint output in `TASKLIST_ROOT/artifacts/D-0019/evidence.md`

**Acceptance Criteria:**
- `make lint-architecture` exits 0 (no ERROR-level findings)
- All 6 checks produce PASS results
- Any fixes applied are documented with before/after evidence
- WARN-level findings (e.g., command size >200) documented but not blocking

**Validation:**
- `make lint-architecture` — exits 0
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0019/evidence.md`

**Dependencies:** T03.02
**Rollback:** Revert fixes if they cause regressions
**Notes:** SC-004: "`make lint-architecture` exits 0" — this task directly validates that success criterion.

---

### T03.04 — Positive Lint Test

**Roadmap Item ID(s):** R-019
**Why:** Verify that `make lint-architecture` correctly reports success on a compliant tree. This validates the "happy path" of the enforcement infrastructure.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0020
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0020/evidence.md`

**Deliverables:**
1. Documented positive lint test result: exit code 0 with all 6 checks passing

**Steps:**
1. **[PLANNING]** Load context: T03.03 result (lint passes on current tree)
2. **[PLANNING]** Check dependencies: T03.03 complete (tree is compliant)
3. **[EXECUTION]** Run `make lint-architecture` on the compliant tree
4. **[EXECUTION]** Capture full output including all 6 check results
5. **[VERIFICATION]** Confirm exit code 0 and all checks report PASS
6. **[COMPLETION]** Document test result in `TASKLIST_ROOT/artifacts/D-0020/evidence.md`

**Acceptance Criteria:**
- `make lint-architecture` exits 0 on compliant tree
- All 6 checks produce explicit PASS output
- Test is reproducible (deterministic result on same tree state)
- Output format documented for regression comparison

**Validation:**
- `make lint-architecture` exits 0
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0020/evidence.md`

**Dependencies:** T03.03
**Rollback:** N/A (test is read-only)
**Notes:** —

---

### T03.05 — Negative Lint Test

**Roadmap Item ID(s):** R-020
**Why:** Verify that `make lint-architecture` correctly reports failure when a skill is missing or `## Activation` is absent. This validates the enforcement catches real violations.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0021
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0021/evidence.md`

**Deliverables:**
1. Documented negative lint test result: exit code 1 with appropriate error messages

**Steps:**
1. **[PLANNING]** Load context: T03.02 lint-architecture checks; identify testable violations
2. **[PLANNING]** Check dependencies: T03.03 complete (baseline compliant tree established)
3. **[EXECUTION]** Temporarily introduce violation: remove `## Activation` from a command file
4. **[EXECUTION]** Run `make lint-architecture` and capture output (expect exit 1 with Check #6 ERROR)
5. **[EXECUTION]** Restore the command file to original state
6. **[VERIFICATION]** Confirm exit code 1 was produced with meaningful error message referencing the violation
7. **[COMPLETION]** Document test result in `TASKLIST_ROOT/artifacts/D-0021/evidence.md`

**Acceptance Criteria:**
- `make lint-architecture` exits 1 when `## Activation` is absent from a paired command
- Error message clearly identifies the violation (file name, check number)
- Tree is restored to compliant state after negative test
- Test methodology documented for reproducibility

**Validation:**
- `make lint-architecture` exits 1 on non-compliant tree, then exits 0 after restoration
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0021/evidence.md`

**Dependencies:** T03.03
**Rollback:** Restore command file to pre-test state (part of test procedure)
**Notes:** Known gap: false positive/negative risk. Test with known-good and known-bad fixtures per M6 mitigation.

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm build system enforcement infrastructure is operational and ready to support structural validation in Phase 4.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-END.md`

**Verification:**
- `sync-dev` and `verify-sync` heuristics removed; all skills synced (D-0017)
- `lint-architecture` target implements 6 checks and is discoverable via `make help` (D-0018)
- Positive and negative lint tests both pass with expected results (D-0020, D-0021)

**Exit Criteria:**
- D-0017 through D-0021 artifacts exist with valid content
- `make lint-architecture` exits 0 on current tree (SC-004)
- Phase 3 exit criteria met: enforcement before migration rule satisfied

---

*End of Phase 3 — see `tasklist-P4.md` for Phase 4: Structural Validation & Testing*
