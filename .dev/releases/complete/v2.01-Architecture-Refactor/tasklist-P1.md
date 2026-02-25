# TASKLIST — v2.01 Architecture Refactor — Phase 1

**Parent document**: `TASKLIST_ROOT/tasklist-header.md`
**TASKLIST_ROOT**: `.dev/releases/current/v2.01-Architecture-Refactor/`

---

## Phase 1: Foundation & Environment Probe

Validate the development environment, confirm the FALLBACK-ONLY variant still holds, establish tier classification policy for executable `.md` files, and verify the architecture policy document exists. This phase produces no code changes — it establishes verified preconditions for all subsequent phases.

---

### T01.01 — Skill Tool Probe Re-Run

**Roadmap Item ID(s):** R-001
**Why:** The prior sprint's probe returned `TOOL_NOT_AVAILABLE`, forcing the FALLBACK-ONLY variant. This must be re-verified in the current environment before any invocation wiring work begins.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0001
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0001/spec.md`

**Deliverables:**
1. Probe result document recording variant decision (FALLBACK-ONLY confirmed or updated)

**Steps:**
1. **[PLANNING]** Identify scope: re-run Skill tool probe and `claude -p` viability test in current environment
2. **[PLANNING]** Check dependencies: none (first task); verify branch is on `feature/v2.01-Architecture-Refactor`
3. **[EXECUTION]** Attempt `Skill sc:adversarial-protocol` invocation to test tool availability
4. **[EXECUTION]** Attempt `claude -p` subprocess invocation to test headless path viability
5. **[EXECUTION]** Document probe results: tool available/unavailable, error messages, variant decision
6. **[VERIFICATION]** Verify probe result is deterministic and reproducible
7. **[COMPLETION]** Record variant decision in `TASKLIST_ROOT/artifacts/D-0001/spec.md`

**Acceptance Criteria:**
- Probe executed empirically in current environment with result documented
- Variant decision (FALLBACK-ONLY or updated) is deterministic and reproducible
- If result differs from prior sprint (TOOL_NOT_AVAILABLE), downstream impact analysis recorded
- Probe methodology and exact commands documented for future re-runs

**Validation:**
- Manual check: probe result document exists with variant decision and evidence
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0001/spec.md`

**Dependencies:** None
**Rollback:** N/A (read-only probe; no changes to revert)
**Notes:** Prior result: `TOOL_NOT_AVAILABLE` → D-0001/D-0002 forced FALLBACK-ONLY. Re-verify empirically.

---

### T01.02 — Prerequisite Validation

**Roadmap Item ID(s):** R-002
**Why:** Before any implementation begins, all files must exist, build targets must be valid, and branch state must be clean. This prevents building on a broken foundation.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[█████████-] 90%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0002
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0002/evidence.md`

**Deliverables:**
1. Prerequisite verification report confirming all checks pass

**Steps:**
1. **[PLANNING]** Load context: Day 1 verification procedure from sprint-spec §15
2. **[PLANNING]** Check dependencies: T01.01 should complete first (variant decision informs prerequisites)
3. **[EXECUTION]** Run `git status` to check for rogue-agent staged changes (treat all as untrusted)
4. **[EXECUTION]** Run `ls docs/architecture/command-skill-policy.md` to confirm policy doc exists
5. **[EXECUTION]** Run `grep -l "## Activation" src/superclaude/commands/*.md` (expect only `roadmap.md`)
6. **[EXECUTION]** Run `grep "Skill" src/superclaude/commands/roadmap.md | head -5` to check `allowed-tools`
7. **[VERIFICATION]** Confirm all 4 checks produce expected results per §15
8. **[COMPLETION]** Document results in `TASKLIST_ROOT/artifacts/D-0002/evidence.md`

**Acceptance Criteria:**
- All files referenced in sprint-spec exist and are accessible
- Build targets (`make sync-dev`, `make verify-sync`) execute without errors
- No rogue-agent staged changes detected (or explicitly documented as untrusted)
- Day 1 verification procedure (§15) passes with all 4 checks documented

**Validation:**
- Manual check: all 4 verification commands from §15 produce expected output
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0002/evidence.md`

**Dependencies:** T01.01
**Rollback:** N/A (read-only verification; no changes to revert)
**Notes:** —

---

### T01.03 — Tier Classification Policy for Executable `.md` Files

**Roadmap Item ID(s):** R-003
**Why:** Executable `.md` files (commands, skills, agents) must be classified as STANDARD minimum, not EXEMPT. This prevents downstream tasks from being incorrectly assigned EXEMPT tier when they modify executable specification files.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0003
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0003/spec.md`

**Deliverables:**
1. Tier classification policy document (Rule 7.6) with downstream compliance tier assignments

**Steps:**
1. **[PLANNING]** Load context: D-T01.03 decision from sprint-spec §17 (executable `.md` files NOT exempt)
2. **[PLANNING]** Check dependencies: T01.01 and T01.02 should complete first
3. **[EXECUTION]** Document policy: `.md` extension ≠ documentation; SKILL.md, command `.md`, and agent `.md` files are executable specifications
4. **[EXECUTION]** Apply policy to all downstream tasks: assign compliance tiers per generator Section 5.3 with this override
5. **[VERIFICATION]** Verify all 9 downstream tasks that modify executable `.md` files have STANDARD or higher tier
6. **[COMPLETION]** Record policy in `TASKLIST_ROOT/artifacts/D-0003/spec.md`

**Acceptance Criteria:**
- Policy explicitly states executable `.md` files (commands, skills, agents) are STANDARD minimum
- All downstream task compliance tiers reflect this policy (no EXEMPT for executable `.md` modifications)
- Policy is consistent with sprint-spec Decision D-T01.03
- Document references Rule 7.6 and provides classification rationale

**Validation:**
- Manual check: tier classification policy document exists with clear rule and downstream assignments
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0003/spec.md`

**Dependencies:** T01.01, T01.02
**Rollback:** N/A (policy document; no code changes)
**Notes:** Decision D-T01.03: `.md` extension ≠ documentation; SKILL.md is code.

---

### T01.04 — Architecture Policy Document Verification

**Roadmap Item ID(s):** R-004
**Why:** The architecture policy document at `docs/architecture/command-skill-policy.md` is the canonical reference for the 3-tier model. It must exist and be valid before any enforcement or migration work begins (Layer 0 in the execution DAG).
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0004
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Deliverables:**
1. Verified architecture policy document exists, is non-empty, and matches v1.0.0 policy spec

**Steps:**
1. **[PLANNING]** Load context: §18 policy document reference (version 1.0.0, 11 sections)
2. **[PLANNING]** Check dependencies: none (but logically part of foundation)
3. **[EXECUTION]** Verify file exists at `docs/architecture/command-skill-policy.md`
4. **[EXECUTION]** Verify file is non-empty and contains expected 11 sections from §18
5. **[EXECUTION]** If file missing: create from sprint-spec §4–§11 (3-tier model, naming conventions, contracts, CI enforcement)
6. **[VERIFICATION]** Confirm document content covers: Overview, 3-Tier Model, Naming, Command Contract, Skill Contract, Ref Convention, Invocation Patterns, Anti-Patterns, CI Enforcement, Migration Checklist, Decision Log
7. **[COMPLETION]** Record verification results in `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Acceptance Criteria:**
- File exists at `docs/architecture/command-skill-policy.md` and is non-empty
- Content includes all 11 sections listed in §18
- Version matches 1.0.0 as specified in the policy document reference
- FR-001 (Layer 0) gate cleared for downstream phases

**Validation:**
- Manual check: `ls -la docs/architecture/command-skill-policy.md` shows existing non-empty file
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Dependencies:** None
**Rollback:** N/A (verification; creation only if missing)
**Notes:** Sprint-spec §15 states "Primary: YES (check if still present)" — likely exists but must verify.

---

### T01.05 — Foundation Validation: Probe Result Verification

**Roadmap Item ID(s):** R-005
**Why:** The probe result from T01.01 must be independently verified to confirm the variant decision is deterministic and reproducible. This is a quality gate before Phase 2 work begins.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0005
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0005/evidence.md`

**Deliverables:**
1. Independent verification that D-0001 variant decision is correct and reproducible

**Steps:**
1. **[PLANNING]** Load context: T01.01 probe results (D-0001)
2. **[PLANNING]** Check dependencies: T01.01 must be complete
3. **[EXECUTION]** Review probe methodology and results from D-0001
4. **[EXECUTION]** If variant changed from FALLBACK-ONLY: document impact on downstream Phase 2 design
5. **[VERIFICATION]** Confirm variant decision matches between T01.01 output and this verification
6. **[COMPLETION]** Record confirmation in `TASKLIST_ROOT/artifacts/D-0005/evidence.md`

**Acceptance Criteria:**
- Variant decision independently verified as deterministic and reproducible
- If variant differs from D-0001: impact analysis documents all affected downstream tasks
- Verification methodology documented for future re-runs
- D-0005 confirmation artifact references D-0001 for traceability

**Validation:**
- Manual check: variant decision confirmed with reproducibility evidence
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0005/evidence.md`

**Dependencies:** T01.01
**Rollback:** N/A (read-only verification)
**Notes:** —

---

### Checkpoint: Phase 1 / Tasks T01.01–T01.05

**Purpose:** Verify the first 5 foundation tasks are complete before proceeding to branch state verification.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-T01-T05.md`

**Verification:**
- Probe result documented with variant decision (FALLBACK-ONLY or updated)
- All prerequisite checks pass per §15 Day 1 verification procedure
- Tier classification policy established and architecture policy document verified

**Exit Criteria:**
- D-0001 through D-0005 artifacts exist and are non-empty
- Variant decision is deterministic (T01.01 and T01.05 agree)
- No blocking issues preventing Phase 1 completion

---

### T01.06 — Foundation Validation: Branch State Clean

**Roadmap Item ID(s):** R-006
**Why:** Before any code changes begin in Phase 2, the branch must be confirmed clean with no untrusted staged changes from the rogue-agent incident.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `EXEMPT`
**Confidence:** `[█████████-] 90%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Skip verification (EXEMPT tier)
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0006
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0006/evidence.md`

**Deliverables:**
1. Branch state verification report showing clean working tree

**Steps:**
1. **[PLANNING]** Load context: §15 current branch state and rogue-agent risk (R-002)
2. **[PLANNING]** Check dependencies: T01.02 prerequisite validation should be complete
3. **[EXECUTION]** Run `git status` and document all staged, modified, and untracked files
4. **[EXECUTION]** Compare against expected state from §15 (only expected modifications permitted)
5. **[VERIFICATION]** Confirm working tree shows only expected modifications (no rogue-agent artifacts)
6. **[COMPLETION]** Record branch state in `TASKLIST_ROOT/artifacts/D-0006/evidence.md`

**Acceptance Criteria:**
- `git status` output documented and analyzed
- All staged files identified and assessed as trusted or untrusted
- No rogue-agent artifacts remain in working tree
- Branch state matches expectations from §15 current branch state analysis

**Validation:**
- Manual check: `git status` shows clean working tree with only expected modifications
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0006/evidence.md`

**Dependencies:** T01.02
**Rollback:** N/A (read-only verification)
**Notes:** Risk R-002: Rogue agent staged changes. Treat all staged files as untrusted per sprint-spec §7.

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm all foundation preconditions are met and the environment is ready for invocation wiring work in Phase 2.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-END.md`

**Verification:**
- All 6 foundation tasks (T01.01–T01.06) complete with artifacts produced
- Variant decision documented and verified (FALLBACK-ONLY or updated)
- Branch state clean and all prerequisites validated

**Exit Criteria:**
- D-0001 through D-0006 artifacts exist with valid content
- Phase 1 exit criteria met: variant decision documented, current state verified, tier policy established
- No blocking issues for Phase 2 entry

---

*End of Phase 1 — see `tasklist-P2.md` for Phase 2: Invocation Wiring & Activation Fix*
