# TASKLIST — v2.01 Architecture Refactor — Phase 2

**Parent document**: `TASKLIST_ROOT/tasklist-header.md`
**TASKLIST_ROOT**: `.dev/releases/current/v2.01-Architecture-Refactor/`

---

## Phase 2: Invocation Wiring & Activation Fix

Fix the primary invocation chain for `sc:roadmap` by adding `Skill` to `allowed-tools`, rewriting the `## Activation` section, decomposing Wave 2 Step 3 into 6 atomic sub-steps with fallback protocol, and renaming all 5 skill directories with `-protocol` suffix. This phase ends with structural audit and end-to-end activation testing.

---

### T02.01 — Add `Skill` to `roadmap.md` `allowed-tools` (BUG-001 Partial)

**Roadmap Item ID(s):** R-007
**Why:** `roadmap.md` is missing `Skill` in its `allowed-tools` frontmatter. Without this, Claude Code blocks the Skill tool invocation, breaking the entire command→skill dispatch chain.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `LIGHT`
**Confidence:** `[██████▌---] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Quick sanity check (~100 tokens, 10s)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0007
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0007/evidence.md`

**Deliverables:**
1. Updated `src/superclaude/commands/roadmap.md` with `Skill` in `allowed-tools` frontmatter

**Steps:**
1. **[PLANNING]** Load context: BUG-001 from sprint-spec §12; identify `allowed-tools` line in `roadmap.md`
2. **[PLANNING]** Check dependencies: Phase 1 complete (variant decision and prerequisites verified)
3. **[EXECUTION]** Add `Skill` to the `allowed-tools` list in `src/superclaude/commands/roadmap.md` frontmatter
4. **[EXECUTION]** Apply identical change to `.claude/commands/sc/roadmap.md` (dev copy)
5. **[VERIFICATION]** Verify `Skill` appears in `allowed-tools` in both files
6. **[COMPLETION]** Document change in `TASKLIST_ROOT/artifacts/D-0007/evidence.md`

**Acceptance Criteria:**
- `Skill` present in `allowed-tools` list in `src/superclaude/commands/roadmap.md`
- Identical change applied to `.claude/commands/sc/roadmap.md`
- No other frontmatter fields modified
- Change is part of Group A atomic unit (per §13.7)

**Validation:**
- Manual check: `grep "Skill" src/superclaude/commands/roadmap.md` shows `Skill` in `allowed-tools`
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0007/evidence.md`

**Dependencies:** Phase 1 complete
**Rollback:** Revert `allowed-tools` line to pre-change state
**Notes:** Part of BUG-001 fix. Group A atomic unit — must be applied with T02.02 and T02.04.

---

### T02.02 — Add `Skill` to `sc-roadmap-protocol/SKILL.md` `allowed-tools` (BUG-001 Partial)

**Roadmap Item ID(s):** R-008
**Why:** The protocol skill also needs `Skill` in its `allowed-tools` to enable cross-skill invocation (e.g., dispatching `sc:adversarial-protocol` from within `sc:roadmap-protocol`).
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `LIGHT`
**Confidence:** `[██████▌---] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Quick sanity check (~100 tokens, 10s)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0008
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Deliverables:**
1. Updated `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` with `Skill` in `allowed-tools` frontmatter

**Steps:**
1. **[PLANNING]** Load context: BUG-001 from sprint-spec §12; identify `allowed-tools` in SKILL.md
2. **[PLANNING]** Check dependencies: T02.01 should be applied together (Group A atomic unit)
3. **[EXECUTION]** Add `Skill` to `allowed-tools` in `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
4. **[EXECUTION]** Verify the SKILL.md file is in the `-protocol` directory (not old `sc-roadmap/`)
5. **[VERIFICATION]** Verify `Skill` appears in `allowed-tools` frontmatter
6. **[COMPLETION]** Document change in `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Acceptance Criteria:**
- `Skill` present in `allowed-tools` list in `sc-roadmap-protocol/SKILL.md`
- File location is `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`
- No other frontmatter fields modified
- Change is part of Group A atomic unit

**Validation:**
- Manual check: `grep "Skill" src/superclaude/skills/sc-roadmap-protocol/SKILL.md` confirms presence
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Dependencies:** T02.01
**Rollback:** Revert `allowed-tools` line to pre-change state
**Notes:** Part of BUG-001 fix. Group A atomic unit — must be applied with T02.01 and T02.04.

---

### T02.03 — Decompose Wave 2 Step 3 with Fallback Protocol

**Roadmap Item ID(s):** R-010, R-011
**Why:** Wave 2 Step 3 was a single vague "Invoke sc:adversarial" line with no tool binding, no sub-steps, no fallback, and no return handling. This must be decomposed into 6 atomic sub-steps (3a–3f) with explicit tool bindings and the F1/F2-3/F4-5 fallback protocol.
**Effort:** `L`
**Risk:** `High`
**Risk Drivers:** system-wide scope, breaking change (invocation protocol rewrite), end-to-end dependency
**Tier:** `STRICT`
**Confidence:** `[█████████-] 90%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Required (STRICT + Risk High)
**Deliverable IDs:** D-0009, D-0010
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0009/spec.md`
- `TASKLIST_ROOT/artifacts/D-0010/spec.md`

**Deliverables:**
1. Wave 2 Step 3 decomposed into 6 sub-steps (3a–3f) with verb→tool mapping for each
2. Fallback protocol F1/F2-3/F4-5 fully specified with 3-status convergence routing (Pass ≥0.6, Partial ≥0.5, Fail <0.5)

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §9 (fallback protocol), §8 (invocation wiring), §10 (return contract schema)
2. **[PLANNING]** Check dependencies: T02.01 and T02.02 must be complete (Skill in allowed-tools)
3. **[EXECUTION]** Write sub-step 3a: Parse agent specs from `--agents` flag or SKILL.md FR-008 section
4. **[EXECUTION]** Write sub-step 3b: Expand agent specs with model/persona; 3c: Add debate-orchestrator if `agent_count >= 3`
5. **[EXECUTION]** Write sub-step 3d: Execute fallback protocol (F1 variant generation → F2/3 diff+debate → F4/5 selection+merge+contract)
6. **[EXECUTION]** Write sub-step 3e: Consume return contract with missing-file guard, YAML parse error handling, and 3-status routing
7. **[EXECUTION]** Write sub-step 3f: Skip primary template (no-op in FALLBACK-ONLY variant)
8. **[VERIFICATION]** Verify all 6 sub-steps have explicit tool bindings; verify fallback produces `return-contract.yaml`
9. **[COMPLETION]** Document specifications in D-0009 and D-0010 artifacts

**Acceptance Criteria:**
- 6 sub-steps (3a–3f) each have verb→tool mapping (Task, Read, Write, Bash as applicable)
- Fallback protocol covers F1 (variant generation), F2/3 (diff+debate), F4/5 (selection+merge+contract)
- Convergence routing implements 3-status: Pass (≥0.6), Partial (≥0.5), Fail (<0.5)
- Missing-file guard and YAML parse error handling specified in step 3e

**Validation:**
- Manual check: all 6 sub-steps have tool bindings; convergence thresholds match sprint-spec §9
- Evidence: linkable artifacts produced at D-0009 and D-0010 paths

**Dependencies:** T02.01, T02.02
**Rollback:** Revert Wave 2 Step 3 to original single-step form
**Notes:** R-001 risk: partial application breaks all invocation wiring. Apply as complete atomic set. Orchestrator threshold aligned to ≥3 (not ≥5) per D-0006.

---

### T02.04 — Fix BUG-006: Rewrite `roadmap.md` `## Activation` Section

**Roadmap Item ID(s):** R-009
**Why:** The `## Activation` section in `roadmap.md` references the old path `src/superclaude/skills/sc-roadmap/SKILL.md` instead of invoking `Skill sc:roadmap-protocol`. This breaks the entire invocation chain for the primary command.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `LIGHT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Quick sanity check (~100 tokens, 10s)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0011
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Deliverables:**
1. Rewritten `## Activation` section containing exact string `Skill sc:roadmap-protocol` and "Do NOT proceed" warning

**Steps:**
1. **[PLANNING]** Load context: BUG-006 from sprint-spec §12; command template from §5
2. **[PLANNING]** Check dependencies: T02.01 must be complete (Skill in allowed-tools)
3. **[EXECUTION]** Replace `## Activation` section in `src/superclaude/commands/roadmap.md` with template from §5
4. **[EXECUTION]** Apply identical change to `.claude/commands/sc/roadmap.md`
5. **[VERIFICATION]** Verify `## Activation` contains exact string `Skill sc:roadmap-protocol` and "Do NOT proceed" warning
6. **[COMPLETION]** Document change in `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Acceptance Criteria:**
- `## Activation` section contains exact string `Skill sc:roadmap-protocol`
- "Do NOT proceed" warning present per command template (§5)
- Both `src/` and `.claude/` copies updated identically
- Old path reference to `sc-roadmap/SKILL.md` completely removed

**Validation:**
- Manual check: `grep "Skill sc:roadmap-protocol" src/superclaude/commands/roadmap.md` returns match
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Dependencies:** T02.01
**Rollback:** Revert `## Activation` section to pre-change content
**Notes:** Risk R-006: Context compaction may drop `## Activation`. The "Do NOT proceed" warning mitigates this.

---

### T02.05 — Rename 5 Skill Directories with `-protocol` Suffix

**Roadmap Item ID(s):** R-012
**Why:** All 5 paired skill directories must be renamed with the `-protocol` suffix to match the naming convention that prevents Skill tool re-entry deadlocks. This is Layer 1 in the execution DAG and must be completed before enforcement (Phase 3) and command updates (Phase 6).
**Effort:** `XL`
**Risk:** `High`
**Risk Drivers:** migration (~30 files), breaking change (directory renames), cross-cutting scope (5 skills + 5 commands + dev copies)
**Tier:** `STRICT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Required (STRICT + Risk High)
**Deliverable IDs:** D-0012, D-0013, D-0014
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0012/spec.md`
- `TASKLIST_ROOT/artifacts/D-0013/evidence.md`
- `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Deliverables:**
1. 5 skill directories renamed: `sc-adversarial/` → `sc-adversarial-protocol/`, `sc-cleanup-audit/` → `sc-cleanup-audit-protocol/`, `sc-roadmap/` → `sc-roadmap-protocol/`, `sc-task-unified/` → `sc-task-unified-protocol/`, `sc-validate-tests/` → `sc-validate-tests-protocol/`
2. All 5 SKILL.md `name:` fields updated to match new `-protocol` convention
3. `make sync-dev` copies created in `.claude/skills/` for all 5 renamed directories

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §7 (5 skills to rename), §6 (naming convention), §13.7 (atomic change groups)
2. **[PLANNING]** Check dependencies: T02.01–T02.04 complete; all prior work on these directories treated as untrusted
3. **[EXECUTION]** For each of 5 skills: rename `src/superclaude/skills/sc-{name}/` → `sc-{name}-protocol/`
4. **[EXECUTION]** For each of 5 skills: update SKILL.md frontmatter `name:` field to `sc:{name}-protocol`
5. **[EXECUTION]** Fix `sc-cleanup-audit` missing `sc:` prefix: old `cleanup-audit` → new `sc:cleanup-audit-protocol`
6. **[EXECUTION]** Run `make sync-dev` to create `.claude/skills/` copies
7. **[EXECUTION]** Fix stale path references: BUG-005 (`sc-roadmap-protocol/SKILL.md` references to old `sc-adversarial/`)
8. **[VERIFICATION]** Verify all 5 directories renamed; all `name:` fields end in `-protocol`; `make verify-sync` passes
9. **[COMPLETION]** Document all renames and verifications in D-0012, D-0013, D-0014 artifacts

**Acceptance Criteria:**
- All 5 directories renamed with `-protocol` suffix in `src/superclaude/skills/`
- All 5 SKILL.md `name:` fields updated (including `sc:` prefix fix for cleanup-audit)
- `.claude/skills/` mirrors match via `make sync-dev && make verify-sync`
- Zero references to old directory names in renamed files

**Validation:**
- Manual check: `ls src/superclaude/skills/sc-*-protocol/` lists all 5 renamed directories
- Evidence: linkable artifacts produced at D-0012, D-0013, D-0014 paths

**Dependencies:** T02.01, T02.02, T02.03, T02.04
**Rollback:** Rename directories back to original names; revert SKILL.md frontmatter changes
**Notes:** ⚠️ DO NOT TRUST any staged rogue-agent work. Execute all renames fresh. ~30 files affected across 5 directories + dev copies. Risk R-002 applies.

---

### Checkpoint: Phase 2 / Tasks T02.01–T02.05

**Purpose:** Verify the invocation wiring changes and skill renames are complete and consistent before proceeding to structural audit.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-T01-T05.md`

**Verification:**
- `Skill` present in `allowed-tools` for both `roadmap.md` and SKILL.md (D-0007, D-0008)
- Wave 2 Step 3 decomposed into 6 sub-steps with fallback protocol (D-0009, D-0010)
- All 5 skill directories renamed with `-protocol` suffix (D-0012, D-0013, D-0014)

**Exit Criteria:**
- `## Activation` section in `roadmap.md` references `Skill sc:roadmap-protocol` (D-0011)
- `make sync-dev && make verify-sync` pass with renamed directories
- No stale references to old skill directory names in modified files

---

### T02.06 — 8-Point Structural Audit of Wave 2 Step 3

**Roadmap Item ID(s):** R-013
**Why:** The Wave 2 Step 3 decomposition must pass the 8-point structural audit defined in sprint-spec §9 before any downstream work depends on it.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** end-to-end validation scope
**Tier:** `STRICT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended (STRICT tier)
**Deliverable IDs:** D-0015
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0015/evidence.md`

**Deliverables:**
1. 8-point structural audit report with pass/fail for each audit point

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §9 (8-point audit criteria); D-0009 (Wave 2 Step 3 decomposition)
2. **[PLANNING]** Check dependencies: T02.03 must be complete (Step 3 decomposition exists)
3. **[EXECUTION]** Audit point 1: Each sub-step has explicit tool binding
4. **[EXECUTION]** Audit point 2: Fallback protocol covers F1/F2-3/F4-5
5. **[EXECUTION]** Audit points 3-6: Return contract routing, convergence thresholds, error handling, no-op step 3f
6. **[EXECUTION]** Audit points 7-8: Orchestrator threshold (≥3), agent dispatch consistency
7. **[VERIFICATION]** All 8 audit points pass with documented evidence
8. **[COMPLETION]** Record audit results in `TASKLIST_ROOT/artifacts/D-0015/evidence.md`

**Acceptance Criteria:**
- All 8 audit points assessed with explicit pass/fail determination
- Zero failing audit points (all must pass for SC-006 success criterion)
- Each audit finding includes evidence reference (line numbers, file paths)
- Audit methodology documented for reproducibility

**Validation:**
- Manual check: audit report shows 8/8 pass with evidence for each point
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0015/evidence.md`

**Dependencies:** T02.03
**Rollback:** N/A (audit is read-only); if audit fails, T02.03 requires rework
**Notes:** SC-006: "Wave 2 Step 3 passes 8-point audit" — this task directly validates that success criterion.

---

### T02.07 — End-to-End Activation Chain Test

**Roadmap Item ID(s):** R-014
**Why:** The complete invocation chain `/sc:roadmap` → `Skill sc:roadmap-protocol` → SKILL.md loads must be tested end-to-end to confirm no silent failures or skips occur.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** end-to-end scope, test coverage gap (R-007)
**Tier:** `STRICT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended (STRICT tier)
**Deliverable IDs:** D-0016
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0016/evidence.md`

**Deliverables:**
1. End-to-end activation chain test report documenting invocation chain success or failure

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §8 (invocation wiring chain); D-0007 through D-0014
2. **[PLANNING]** Check dependencies: T02.01–T02.05 complete (all wiring changes applied)
3. **[EXECUTION]** Test: invoke `/sc:roadmap` and verify `Skill sc:roadmap-protocol` loads
4. **[EXECUTION]** Verify SKILL.md content is accessible in agent context after invocation
5. **[EXECUTION]** Document any errors, silent skips, or unexpected behavior
6. **[VERIFICATION]** Invocation chain completes without errors or silent skips
7. **[COMPLETION]** Record test results in `TASKLIST_ROOT/artifacts/D-0016/evidence.md`

**Acceptance Criteria:**
- Invocation chain `/sc:roadmap` → `Skill sc:roadmap-protocol` → SKILL.md loads completes without errors
- No silent skips or partial execution detected
- Test conducted with fresh agent context (Risk R-006 mitigation)
- Expected behavior documented for future regression testing

**Validation:**
- Manual check: invocation chain completes with SKILL.md content accessible
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0016/evidence.md`

**Dependencies:** T02.01, T02.02, T02.03, T02.04, T02.05
**Rollback:** N/A (testing is read-only)
**Notes:** Risk R-007: Zero test coverage for activation flow. This task creates the first manual activation test. Recommend automated test for v2.02.

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm all invocation wiring changes are applied, validated, and the system is ready for build system enforcement in Phase 3.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-END.md`

**Verification:**
- BUG-001 partially fixed (roadmap.md and SKILL.md have `Skill` in `allowed-tools`)
- BUG-006 fixed (`## Activation` references `Skill sc:roadmap-protocol`)
- Wave 2 Step 3 passes 8-point audit (SC-006)

**Exit Criteria:**
- D-0007 through D-0016 artifacts exist with valid content
- End-to-end activation chain test passes (T02.07)
- All 5 skill directories renamed with `-protocol` suffix and synced

---

*End of Phase 2 — see `tasklist-P3.md` for Phase 3: Build System Enforcement*
