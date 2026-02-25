# TASKLIST — v2.01 Architecture Refactor — Phase 5

**Parent document**: `TASKLIST_ROOT/tasklist-header.md`
**TASKLIST_ROOT**: `.dev/releases/current/v2.01-Architecture-Refactor/`

---

## Phase 5: Polish

Complete the verb-to-tool glossary to disambiguate invocation terminology, fix the Wave 1A Step 2 semantic alignment issue, and convert all pseudo-CLI invocation patterns to executable patterns. These tasks resolve specification ambiguities that would cause implementation confusion in future sprints.

---

### T05.01 — Verb-to-Tool Glossary

**Roadmap Item ID(s):** R-026
**Why:** The sprint-spec uses "Invoke", "Dispatch", and "Load" inconsistently. Without disambiguation, implementers may use the wrong tool for each operation, reintroducing RC1/RC2 root causes.
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
**Deliverable IDs:** D-0027
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0027/spec.md`

**Deliverables:**
1. Verb-to-tool glossary disambiguating "Invoke" (Bash/`claude -p`), "Dispatch" (Task tool), "Load" (Read tool/Skill tool)

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §8 (invocation wiring), §4 (3-tier model); identify all verb usages
2. **[PLANNING]** Check dependencies: Phase 4 complete (structural validation confirms invocation patterns)
3. **[EXECUTION]** Define verb→tool mappings: "Invoke" → Skill tool or Bash (`claude -p`); "Dispatch" → Task tool (fresh agent); "Load" → Read tool (file content) or Skill tool (protocol loading)
4. **[EXECUTION]** Cross-reference all SKILL.md files to verify verb consistency with glossary
5. **[VERIFICATION]** Verify glossary covers all invocation verbs used across skills and commands
6. **[COMPLETION]** Document glossary in `TASKLIST_ROOT/artifacts/D-0027/spec.md`

**Acceptance Criteria:**
- Glossary disambiguates at minimum: "Invoke", "Dispatch", "Load" with explicit tool mappings
- Each verb maps to exactly one tool (no ambiguity)
- Glossary is consistent with sprint-spec §8 Task Agent vs Skill Tool vs `claude -p` table
- Cross-referenced against actual SKILL.md usage patterns

**Validation:**
- Manual check: glossary document exists with unambiguous verb→tool mappings
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0027/spec.md`

**Dependencies:** Phase 4 complete
**Rollback:** N/A (documentation artifact)
**Notes:** —

---

### T05.02 — Wave 1A Step 2 Semantic Alignment Fix

**Roadmap Item ID(s):** R-027
**Why:** Wave 1A Step 2 semantics do not match the updated return contract schema from the v2.01 refactor. This misalignment would cause consumer confusion when processing pipeline outputs.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** none
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution — 300-500 tokens, 30s timeout
**MCP Requirements:** Required: None | Preferred: Sequential
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0028
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0028/evidence.md`

**Deliverables:**
1. Wave 1A Step 2 semantics updated to match the canonical 10-field return contract schema

**Steps:**
1. **[PLANNING]** Load context: sprint-spec §10 (return contract schema); locate Wave 1A Step 2 in `sc-roadmap-protocol/SKILL.md`
2. **[PLANNING]** Check dependencies: T04.01 (return contract tests validate schema)
3. **[EXECUTION]** Identify semantic misalignment between Step 2 and the updated return contract schema
4. **[EXECUTION]** Update Step 2 to reference correct field names, types, and consumer/producer ownership
5. **[VERIFICATION]** Verify Step 2 semantics are consistent with D-0022 (return contract test fixtures)
6. **[COMPLETION]** Document changes in `TASKLIST_ROOT/artifacts/D-0028/evidence.md`

**Acceptance Criteria:**
- Step 2 references correct field names from canonical 10-field schema
- Producer/consumer ownership model consistent with sprint-spec §10
- No semantic drift between Step 2 and validated return contract tests (D-0022)
- Change does not break existing Wave 1A Step 1 or Step 3 logic

**Validation:**
- Manual check: Step 2 field references match canonical schema; no inconsistencies
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0028/evidence.md`

**Dependencies:** T04.01
**Rollback:** Revert Step 2 to pre-change content
**Notes:** —

---

### T05.03 — Pseudo-CLI Invocation Conversion

**Roadmap Item ID(s):** R-028
**Why:** The sprint-spec contains pseudo-CLI invocation patterns (prose instructions that look like commands but are not executable). These must be converted to executable patterns using the verb-to-tool glossary from T05.01.
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
**Deliverable IDs:** D-0029
**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0029/evidence.md`

**Deliverables:**
1. All pseudo-CLI invocation patterns converted to executable patterns with correct tool bindings

**Steps:**
1. **[PLANNING]** Load context: D-0027 (verb-to-tool glossary); scan SKILL.md files for pseudo-CLI patterns
2. **[PLANNING]** Check dependencies: T05.01 complete (glossary provides verb→tool mappings)
3. **[EXECUTION]** Identify all pseudo-CLI patterns across protocol SKILL.md files (e.g., bare "Invoke sc:X" without tool specification)
4. **[EXECUTION]** Convert each pseudo-CLI pattern to explicit tool invocation using glossary (e.g., "Invoke" → "Call Skill tool with sc:X-protocol")
5. **[VERIFICATION]** Verify all converted patterns are executable (each has a concrete tool binding)
6. **[COMPLETION]** Document conversions (before→after) in `TASKLIST_ROOT/artifacts/D-0029/evidence.md`

**Acceptance Criteria:**
- Zero pseudo-CLI patterns remain in modified SKILL.md files
- Each converted pattern uses the correct tool per verb-to-tool glossary
- Conversions documented with before/after examples
- No behavioral change to pipeline logic (only invocation clarity)

**Validation:**
- Manual check: `grep -rn "Invoke sc:" src/superclaude/skills/` returns only executable patterns
- Evidence: linkable artifact produced at `TASKLIST_ROOT/artifacts/D-0029/evidence.md`

**Dependencies:** T05.01
**Rollback:** Revert SKILL.md files to pre-conversion state
**Notes:** —

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm all polish tasks are complete and the specification is ready for integration and closure work in Phase 6.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P05-END.md`

**Verification:**
- Verb-to-tool glossary created with unambiguous mappings (D-0027)
- Wave 1A Step 2 semantics aligned with return contract schema (D-0028)
- All pseudo-CLI patterns converted to executable invocations (D-0029)

**Exit Criteria:**
- D-0027 through D-0029 artifacts exist with valid content
- No pseudo-CLI patterns remain in protocol SKILL.md files
- Phase 5 polish work does not introduce regressions in Phase 2–4 deliverables

---

*End of Phase 5 — see `tasklist-P6.md` for Phase 6: Integration & Closure*
