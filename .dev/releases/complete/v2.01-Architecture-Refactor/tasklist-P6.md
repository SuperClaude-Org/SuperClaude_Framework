# TASKLIST — v2.01 Architecture Refactor — Phase 6

**Parent document**: `TASKLIST_ROOT/tasklist-header.md`
**TASKLIST_ROOT**: `.dev/releases/current/v2.01-Architecture-Refactor/`

---

## Phase 6: Integration & Closure

Complete all remaining tasks: cross-skill invocation documentation, Tier 2 ref loader design, `task-unified.md` major extraction, remaining 4 command file updates, bug fixes (BUG-002/003/004), and final release validation including full regression, stale reference scan, and success criteria verification.

---

### T06.01 — Cross-Skill Invocation Pattern Documentation

**Roadmap Item ID(s):** R-029
**Why:** No specification exists for how one protocol skill invokes another. This documentation is needed to guide future skill development and prevent reintroduction of RC1 (invocation wiring gap).
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0030
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0030/spec.md`

**Deliverables:**
1. Documentation explaining 3 cross-skill invocation patterns: Task agent wrapper, Skill tool direct, and `claude -p`

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §8 (invocation wiring), D-0027 (verb-to-tool glossary)
2. **[PLANNING]** Check dependencies: Phase 5 complete (glossary and patterns finalized)
3. **[EXECUTION]** Document Task agent wrapper pattern: when to use, how to dispatch, return contract handling
4. **[EXECUTION]** Document Skill tool direct pattern: when to use, re-entry constraints, context implications
5. **[EXECUTION]** Document `claude -p` pattern: current status (unfinalized), design considerations, T01.01 probe findings
6. **[VERIFICATION]** Verify documentation is consistent with sprint-spec §8 and D-0027 glossary
7. **[COMPLETION]** Write documentation to `TASKLIST_ROOT/artifacts/D-0030/spec.md`

**Acceptance Criteria:**
- All 3 invocation patterns documented with clear use cases and constraints
- Decision rule provided for choosing between patterns (per sprint-spec §8)
- Re-entry deadlock risk documented for Skill tool direct pattern
- `claude -p` pattern marked as unfinalized with reference to T01.01 probe

**Validation:**
- Manual check: documentation covers all 3 patterns with decision criteria
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0030/spec.md`

**Dependencies:** Phase 5 complete (T05.01 glossary)
**Rollback:** N/A (documentation artifact)
**Notes:** Policy gap #2 from sprint-spec §16: "Cross-skill invocation not specified."

---

### T06.02 — Tier 2 Ref Loader Design (`claude -p` Script)

**Roadmap Item ID(s):** R-030
**Why:** The 3-tier model references `claude -p` for Tier 2 ref file loading but no design document exists. This task creates the design document; implementation is deferred.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** deploy/infra context, cross-cutting scope
**Tier:** `STANDARD`
**Confidence:** `[██████▌---] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: Sequential
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0031
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0031/spec.md`

**Deliverables:**
1. Design document for Tier 2 ref loading mechanism via `claude -p` script; implementation deferred to v2.02

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §8 (`claude -p` script strategy — unfinalized), §4 (Tier 2 ref files), T01.01 probe results (D-0001)
2. **[PLANNING]** Check dependencies: T06.01 complete (invocation patterns provide context)
3. **[EXECUTION]** Design the ref loader: shell script wrapper for `claude -p` with `--append-system-prompt`
4. **[EXECUTION]** Document constraints: SKILL.md injection size limits, `TOOL_NOT_AVAILABLE` implications, file system interaction
5. **[EXECUTION]** Specify the interface: input (ref file path), output (ref content injected into agent context), error handling
6. **[VERIFICATION]** Verify design is consistent with T01.01 probe findings and sprint-spec §8
7. **[COMPLETION]** Write design document to `TASKLIST_ROOT/artifacts/D-0031/spec.md`

**Acceptance Criteria:**
- Design document specifies ref loader interface (input, output, error handling)
- `claude -p` usage pattern documented with `--append-system-prompt` flag
- Constraints and limitations from T01.01 probe explicitly referenced
- Implementation explicitly marked as deferred to v2.02

**Validation:**
- Manual check: design document is complete with interface specification and constraint analysis
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0031/spec.md`

**Dependencies:** T06.01, T01.01 (probe findings)
**Rollback:** N/A (design document only)
**Notes:** Policy gap #1 from sprint-spec §16. Design only — implementation deferred. Sprint-spec §8 notes this strategy is "not yet finalized."

---

### T06.03 — `task-unified.md` Major Extraction (567→106 Lines)

**Roadmap Item ID(s):** R-031
**Why:** `task-unified.md` at 567 lines contains the full protocol inline, violating the 3-tier model. The protocol logic must be extracted to `sc-task-unified-protocol/SKILL.md`, leaving the command file at ≤106 lines.
**Effort:** `L`
**Risk:** `High`
**Risk Drivers:** breaking change (major refactor), system-wide scope, multi-file
**Tier:** `STRICT`
**Confidence:** `[█████████-] 90%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Required (STRICT + Risk High)
**Deliverable IDs:** D-0032, D-0033
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0032/spec.md`
- `TASKLIST_ROOT/artifacts/D-0033/evidence.md`

**Deliverables:**
1. Extracted `task-unified.md` command file at ≤106 lines with `## Activation`, `## Behavioral Summary`, `## Boundaries`
2. `sc-task-unified-protocol/SKILL.md` containing all extracted protocol logic (tier classification, verification routing, compliance enforcement)

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §5 (command and skill templates); current `task-unified.md` content
2. **[PLANNING]** Check dependencies: T02.05 (skill directory renamed); T03.02 (lint-architecture validates structure)
3. **[EXECUTION]** Extract all protocol logic from `task-unified.md` to `sc-task-unified-protocol/SKILL.md`
4. **[EXECUTION]** Restructure `task-unified.md` per command template: metadata, usage, arguments, examples, activation, behavioral summary, boundaries
5. **[EXECUTION]** Add `## Activation` section referencing `Skill sc:task-unified-protocol`
6. **[EXECUTION]** Add `Skill` to `allowed-tools` in `task-unified.md` frontmatter (BUG-001 fix)
7. **[VERIFICATION]** Verify `task-unified.md` ≤106 lines; verify tier classification still works after extraction
8. **[COMPLETION]** Document extraction mapping and verification in D-0032, D-0033 artifacts

**Acceptance Criteria:**
- `task-unified.md` ≤106 lines (SC-010)
- `sc-task-unified-protocol/SKILL.md` contains all extracted protocol logic
- Tier classification behavior unchanged after extraction (functional regression test)
- `## Activation` section references `Skill sc:task-unified-protocol`

**Validation:**
- `wc -l src/superclaude/commands/task-unified.md` — shows ≤106 lines
- Evidence: linkable artifacts produced at D-0032 and D-0033 paths

**Dependencies:** T02.05, T03.02
**Rollback:** Restore original 567-line `task-unified.md`; revert SKILL.md changes
**Notes:** SC-010: "`task-unified.md` reduced to ≤106 lines." Risk: D9.6 functional regression. Verify tier classification still works after extraction.

---

### T06.04 — Remaining 4 Command Files: Add `## Activation` + Fix BUG-001

**Roadmap Item ID(s):** R-032
**Why:** 4 remaining commands (adversarial, cleanup-audit, task-unified, validate-tests) need `## Activation` sections added and `Skill` in `allowed-tools` (BUG-001 fix). These complete the 3-tier model compliance across all 5 paired commands.
**Effort:** `M`
**Risk:** `High`
**Risk Drivers:** multi-file (4 commands × 2 copies = 8 files), breaking change (invocation wiring), system-wide scope
**Tier:** `STRICT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Required (STRICT + Risk High)
**Deliverable IDs:** D-0034
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0034/spec.md`
- `TASKLIST_ROOT/artifacts/D-0034/evidence.md`

**Deliverables:**
1. All 4 commands have `## Activation` sections referencing their paired `-protocol` skills
2. All 4 commands have `Skill` in `allowed-tools` frontmatter (BUG-001 complete fix)

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §5 (command template), §12 (BUG-001), §13.7 (Group A atomic unit)
2. **[PLANNING]** Check dependencies: T02.05 (skill directories renamed); T06.03 (task-unified extraction complete)
3. **[EXECUTION]** For `adversarial.md`: add `## Activation` → `Skill sc:adversarial-protocol`; add `Skill` to `allowed-tools`
4. **[EXECUTION]** For `cleanup-audit.md`: add `## Activation` → `Skill sc:cleanup-audit-protocol`; add `Skill` to `allowed-tools`
5. **[EXECUTION]** For `validate-tests.md`: add `## Activation` → `Skill sc:validate-tests-protocol`; add `Skill` to `allowed-tools`
6. **[EXECUTION]** Apply all changes to both `src/` and `.claude/` copies; run `make sync-dev`
7. **[VERIFICATION]** All 4 commands have `## Activation` and `Skill` in `allowed-tools`; `make lint-architecture` passes
8. **[COMPLETION]** Document changes in D-0034 artifacts

**Acceptance Criteria:**
- All 4 commands have `## Activation` containing `Skill sc:<name>-protocol` (SC-002)
- All 4 commands have `Skill` in `allowed-tools` (SC-003, BUG-001 complete)
- Both `src/` and `.claude/` copies updated identically
- `make lint-architecture` still exits 0 after changes

**Validation:**
- `grep -l "## Activation" src/superclaude/commands/{adversarial,cleanup-audit,task-unified,validate-tests}.md` — returns all 4
- Evidence: linkable artifacts produced at D-0034 spec and evidence paths

**Dependencies:** T02.05, T06.03
**Rollback:** Revert `## Activation` and `allowed-tools` changes in all 8 files
**Notes:** SC-002 + SC-003. Apply per-command atomic groups (Group A from §13.7). Risk R-001: partial application. Risk R-006: context compaction. Note: `task-unified.md` `## Activation` already added in T06.03; this task handles the other 3 + verification of all 4.

---

### T06.05 — Resolve BUG-004: Architecture Policy Deduplication

**Roadmap Item ID(s):** R-033
**Why:** `docs/architecture/command-skill-policy.md` and `src/superclaude/ARCHITECTURE.md` are byte-identical duplicates. There is no canonical source, creating maintenance risk.
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
**Deliverable IDs:** D-0035
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0035/evidence.md`

**Deliverables:**
1. `docs/architecture/command-skill-policy.md` designated as canonical source; `src/superclaude/ARCHITECTURE.md` replaced with symlink or removed

**Steps:**
1. **[PLANNING]** Load context: BUG-004 from sprint-spec §12; verify both files exist and are byte-identical
2. **[PLANNING]** Check dependencies: T01.04 (architecture policy doc verified)
3. **[EXECUTION]** Designate `docs/architecture/command-skill-policy.md` as canonical source
4. **[EXECUTION]** Replace `src/superclaude/ARCHITECTURE.md` with symlink to `docs/architecture/command-skill-policy.md` (or remove if symlink not feasible)
5. **[VERIFICATION]** Verify no other files reference `src/superclaude/ARCHITECTURE.md` as a source; canonical path is used consistently
6. **[COMPLETION]** Document resolution in `TASKLIST_ROOT/artifacts/D-0035/evidence.md`

**Acceptance Criteria:**
- Single canonical source at `docs/architecture/command-skill-policy.md`
- No byte-identical duplicate exists (symlink or removal)
- All references to the architecture policy point to canonical path
- BUG-004 marked as resolved

**Validation:**
- Manual check: `ls -la src/superclaude/ARCHITECTURE.md` shows symlink or file removed
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0035/evidence.md`

**Dependencies:** T01.04
**Rollback:** Restore `src/superclaude/ARCHITECTURE.md` from git history
**Notes:** Tie-breaker: `docs/architecture/` chosen per roadmap explicit naming.

---

### Checkpoint: Phase 6 / Tasks T06.01–T06.05

**Purpose:** Verify documentation, extraction, and command updates are complete before proceeding to bug fixes and final validation.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P06-T01-T05.md`

**Verification:**
- Cross-skill invocation documentation complete (D-0030)
- `task-unified.md` extraction complete with ≤106 lines (D-0032, D-0033)
- All 4 remaining commands updated with `## Activation` and BUG-001 fixed (D-0034)

**Exit Criteria:**
- D-0030 through D-0035 artifacts exist with valid content
- SC-002, SC-003, SC-010 validated
- `make lint-architecture` exits 0 after all command updates

---

### T06.06 — Fix BUG-002 (Stale Path) + BUG-003 (Threshold Inconsistency)

**Roadmap Item ID(s):** R-034
**Why:** BUG-002: `validate-tests.md` line 63 references old path `skills/sc-validate-tests/classification-algorithm.yaml`. BUG-003: orchestrator threshold inconsistent (`>= 3` in step 3c vs `>= 5` in Section 5).
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
**Deliverable IDs:** D-0036, D-0037
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0036/evidence.md`
- `TASKLIST_ROOT/artifacts/D-0037/evidence.md`

**Deliverables:**
1. BUG-002 fixed: `validate-tests.md` line 63 updated to `sc-validate-tests-protocol/` path
2. BUG-003 fixed: all orchestrator threshold references aligned to `>= 3` per D-0006

**Steps:**
1. **[PLANNING]** Load context: BUG-002 and BUG-003 from sprint-spec §12
2. **[PLANNING]** Check dependencies: T02.05 (skill directories renamed for correct paths)
3. **[EXECUTION]** Fix BUG-002: update line 63 in `src/superclaude/commands/validate-tests.md` from `sc-validate-tests/` to `sc-validate-tests-protocol/`
4. **[EXECUTION]** Fix BUG-003: search `sc-roadmap-protocol/SKILL.md` for all threshold references; align to `>= 3`
5. **[EXECUTION]** Apply fixes to `.claude/` copies as well
6. **[VERIFICATION]** Verify no remaining stale paths; verify threshold consistency
7. **[COMPLETION]** Document fixes in D-0036 and D-0037 artifacts

**Acceptance Criteria:**
- Zero references to old `sc-validate-tests/` path in `validate-tests.md`
- All orchestrator threshold references read `>= 3` (not `>= 5`)
- Both `src/` and `.claude/` copies fixed
- No regressions introduced by path or threshold changes

**Validation:**
- `grep "sc-validate-tests/" src/superclaude/commands/validate-tests.md` — returns empty (no stale paths)
- Evidence: linkable artifacts produced at D-0036 and D-0037 paths

**Dependencies:** T02.05
**Rollback:** Revert line 63 and threshold references
**Notes:** BUG-002: MEDIUM severity. BUG-003: MEDIUM severity. Both are single-line fixes.

---

### T06.07 — Full Regression: `sync-dev` + `verify-sync` + `lint-architecture`

**Roadmap Item ID(s):** R-035
**Why:** Before final release, the complete build system validation pipeline must pass. This is the primary gate for SC-004 and SC-005.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** end-to-end scope, ci/pipeline context
**Tier:** `STANDARD`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0038
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0038/evidence.md`

**Deliverables:**
1. Full regression pass: all 3 commands (`sync-dev`, `verify-sync`, `lint-architecture`) exit 0

**Steps:**
1. **[PLANNING]** Load context: SC-004, SC-005 success criteria
2. **[PLANNING]** Check dependencies: All Phase 6 tasks T06.01–T06.06 complete
3. **[EXECUTION]** Run `make sync-dev` — verify exit 0
4. **[EXECUTION]** Run `make verify-sync` — verify exit 0 (src ↔ .claude parity)
5. **[EXECUTION]** Run `make lint-architecture` — verify exit 0 (all 6 checks pass)
6. **[VERIFICATION]** All 3 commands exit 0 with expected output
7. **[COMPLETION]** Document full output in `TASKLIST_ROOT/artifacts/D-0038/evidence.md`

**Acceptance Criteria:**
- `make sync-dev` exits 0 (SC-005)
- `make verify-sync` exits 0 (SC-005)
- `make lint-architecture` exits 0 (SC-004)
- Full output captured as evidence

**Validation:**
- `make sync-dev && make verify-sync && make lint-architecture` — exits 0
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0038/evidence.md`

**Dependencies:** T06.01–T06.06
**Rollback:** N/A (validation only; fixes go back to specific tasks)
**Notes:** SC-004 + SC-005 direct validation. D10.1 from roadmap.

---

### T06.08 — Stale Reference Scan

**Roadmap Item ID(s):** R-036
**Why:** After all skill renames and command updates, zero references should remain to old skill directory names. Any stale references indicate incomplete migration.
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
**Deliverable IDs:** D-0039
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0039/evidence.md`

**Deliverables:**
1. Stale reference scan showing zero matches for all 5 old skill directory names

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §11 (post-rename stale reference check scripts)
2. **[PLANNING]** Check dependencies: T06.07 (full regression passes)
3. **[EXECUTION]** Scan for stale references to all 5 old names:
   - `grep -rn "sc-adversarial/" src/ .claude/ docs/ --include="*.md"`
   - `grep -rn "sc-cleanup-audit/" src/ .claude/ docs/ --include="*.md"`
   - `grep -rn "sc-roadmap/" src/ .claude/ docs/ --include="*.md"`
   - `grep -rn "sc-task-unified/" src/ .claude/ docs/ --include="*.md"`
   - `grep -rn "sc-validate-tests/" src/ .claude/ docs/ --include="*.md"`
4. **[EXECUTION]** If any stale references found: fix them and re-scan
5. **[VERIFICATION]** All 5 scans return empty (zero stale references)
6. **[COMPLETION]** Document scan results in `TASKLIST_ROOT/artifacts/D-0039/evidence.md`

**Acceptance Criteria:**
- Zero references to `sc-adversarial/` (without `-protocol` suffix) in `src/`, `.claude/`, `docs/`
- Zero references to `sc-cleanup-audit/`, `sc-roadmap/`, `sc-task-unified/`, `sc-validate-tests/` similarly
- SC-009 validated: "Zero stale references to old skill directory names"
- Scan methodology documented for future regression checks

**Validation:**
- `grep -rn` for all 5 old names returns empty
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0039/evidence.md`

**Dependencies:** T06.07
**Rollback:** N/A (scan is read-only; fixes are forward)
**Notes:** SC-009 direct validation. Note: scans must exclude this tasklist file itself (it references old names in context).

---

### T06.09 — All 10 Success Criteria (SC-001 through SC-010) Verified

**Roadmap Item ID(s):** R-037
**Why:** The final release gate requires all 10 success criteria from the roadmap to be verified with documented evidence. This is the comprehensive release readiness assessment.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** end-to-end scope, system-wide applicability
**Tier:** `STRICT`
**Confidence:** `[████████▌-] 85%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) — 3-5K tokens, 60s timeout
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended (STRICT tier)
**Deliverable IDs:** D-0040
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0040/spec.md`
- `TASKLIST_ROOT/artifacts/D-0040/evidence.md`

**Deliverables:**
1. SC-001 through SC-010 verification report with PASS/FAIL status and evidence for each criterion

**Steps:**
1. **[PLANNING]** Load context: roadmap Success Criteria table (SC-001 through SC-010)
2. **[PLANNING]** Check dependencies: T06.07 (regression), T06.08 (stale scan) — all prior Phase 6 tasks complete
3. **[EXECUTION]** Verify SC-001: All 5 skill directories renamed with `-protocol` suffix → evidence from T02.05
4. **[EXECUTION]** Verify SC-002 through SC-005: Activation sections, allowed-tools, lint-architecture, sync → evidence from T02.04, T06.04, T03.03, T06.07
5. **[EXECUTION]** Verify SC-006 through SC-008: Wave 2 audit, return contract routing, BUG fixes → evidence from T02.06, T04.01, T06.06
6. **[EXECUTION]** Verify SC-009 through SC-010: Stale references, task-unified size → evidence from T06.08, T06.03
7. **[VERIFICATION]** All 10 criteria documented as PASS with evidence references
8. **[COMPLETION]** Write verification report to D-0040 artifacts

**Acceptance Criteria:**
- All 10 success criteria (SC-001 through SC-010) assessed
- Each criterion documented as PASS with specific evidence reference (task ID, artifact path)
- Zero FAIL criteria (any failures must be resolved before release)
- Report format supports release sign-off decision

**Validation:**
- Manual check: verification report shows 10/10 PASS with evidence for each
- Evidence: linkable artifacts produced at D-0040 spec and evidence paths

**Dependencies:** T06.07, T06.08 (and transitively all prior tasks)
**Rollback:** N/A (verification report; failures require rework of originating tasks)
**Notes:** SC-008: "All BUG-001 through BUG-006 resolved" — verify BUG-005 (stale path in SKILL.md) was addressed in T02.05. This is the final release gate.

---

### Checkpoint: End of Phase 6

**Purpose:** Confirm all integration, closure, and release validation tasks are complete. This is the final project checkpoint.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P06-END.md`

**Verification:**
- All 4 remaining commands updated with `## Activation` and BUG-001 fixed (D-0034)
- Full regression passes: `sync-dev`, `verify-sync`, `lint-architecture` all exit 0 (D-0038)
- All 10 success criteria verified as PASS (D-0040)

**Exit Criteria:**
- D-0030 through D-0040 artifacts exist with valid content
- Zero stale references to old skill directory names (D-0039)
- Release-ready: all success criteria met, all bugs resolved, full regression passes

---

*End of Phase 6 — v2.01 Architecture Refactor tasklist generation complete.*
*35 tasks across 6 phases: STRICT: 10, STANDARD: 13, LIGHT: 2, EXEMPT: 8*
*See `tasklist-header.md` for registries, traceability matrix, and templates.*
