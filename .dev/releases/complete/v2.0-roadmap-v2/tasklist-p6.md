# TASKLIST — sc:roadmap v2 — Phase 6: Command Interface &amp; Session Management

**Parent Tasklist**: `tasklist-overview.md`
**Phase**: 6 of 7
**Task Range**: T06.01–T06.05
**Priority Wave**: P1
**Dependencies**: Phase 1 (M1: SKILL.md must exist for wave boundary definitions); DEP-002: sc:save/sc:load must be available
**Tier Distribution**: STRICT: 2, STANDARD: 2, LIGHT: 1, EXEMPT: 0

---

## Phase 6: Command Interface &amp; Session Management

Update the roadmap.md command file with all flags and examples, and implement session persistence via sc:save/sc:load integration. This phase can be developed in parallel with Phases 2-5 (only depends on Phase 1). It ensures the command is properly documented for users and supports cross-session resumability.

---

### T06.01 — Update roadmap.md command file with all flags

**Roadmap Item ID(s):** R-029
**Why:** The command file tells Claude Code WHEN to activate and WHAT the command does; it must document all flags including new adversarial mode flags for proper command activation.
**Effort:** S
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0029
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0029/spec.md`

**Deliverables:**
- Updated roadmap.md command file (src/superclaude/commands/roadmap.md) with complete flag documentation including: --specs, --multi-roadmap, --agents, --depth, --interactive, --no-validate, --output, --template, --dry-run (FR-018), --compliance (FR-019), --persona. Total: 11+ flags per spec Section 6.2

**Steps:**
1. **[PLANNING]** Load spec Section 6.2 (flags) and Section 3.5 (command file vs SKILL.md relationship)
2. **[PLANNING]** Confirm all flags with types, defaults, and descriptions from spec
3. **[EXECUTION]** Update flag table with all 11+ flags from spec Section 6.2
4. **[EXECUTION]** Add behavioral summary covering single-spec, multi-spec, multi-roadmap, and combined modes
5. **[EXECUTION]** Add boundaries section (will do / will not do) from spec Section 10
6. **[VERIFICATION]** Validate every flag from spec Section 6.2 appears in command file; verify command file ≤~80 lines
7. **[COMPLETION]** Document flag inventory

**Acceptance Criteria:**
- All flags from spec Section 6.2 documented with types and defaults
- Command file describes WHEN to activate and WHAT the command does (not HOW)
- File stays within ~80 lines per spec Section 3.5 sizing
- Boundaries section clearly states what sc:roadmap will and will not do

**Validation:**
- Manual check: Verify all 11+ flags present; verify file ≤~80 lines; verify boundaries match spec Section 10
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.01 (SKILL.md exists, defining the command's behavioral scope)
**Rollback:** TBD
**Notes:** Per spec Section 3.5, command file is installed to ~/.claude/commands/sc/ and loaded when user types /sc:roadmap. Keep surface-level; behavioral detail in SKILL.md.

---

### T06.02 — Update usage examples covering all modes

**Roadmap Item ID(s):** R-030
**Why:** Examples demonstrate all command modes (single-spec, multi-spec, multi-roadmap, combined, model-only) to help users understand the command's capabilities.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** LIGHT
**Confidence:** [████████░░] 78%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Quick sanity check (~100 tokens, 10s timeout)
**MCP Requirements:** None | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0030
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0030/spec.md`

**Deliverables:**
- At least 7 usage examples in the command file demonstrating: basic single-spec, deep analysis with template, multi-spec consolidation, model-only multi-roadmap, explicit persona multi-roadmap, mixed format, full combined mode with interactive

**Steps:**
1. **[PLANNING]** Load spec Section 6.3 for the 7 example commands
2. **[PLANNING]** Confirm all modes are covered: single-spec, multi-spec, multi-roadmap, combined, model-only, mixed, interactive
3. **[EXECUTION]** Add all 7+ examples from spec Section 6.3 to command file
4. **[EXECUTION]** Add brief descriptions for each example explaining the mode being demonstrated
5. **[VERIFICATION]** Verify at least 7 distinct examples covering all documented modes
6. **[COMPLETION]** Document example inventory

**Acceptance Criteria:**
- At least 7 examples present demonstrating all modes from spec Section 6.3
- Each example shows a different mode or flag combination
- Examples use consistent spec file paths and realistic flag values
- Brief description accompanies each example

**Validation:**
- Manual check: Count examples (≥7); verify all modes covered; verify flag syntax correct
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T06.01 (command file must exist with flag documentation)
**Rollback:** TBD
**Notes:** LIGHT tier: documentation-only task with no code changes or data risk.

---

### T06.03 — Implement sc:save integration at wave boundaries

**Roadmap Item ID(s):** R-031
**Why:** Session persistence via sc:save at wave boundaries enables cross-session resumability, preventing lost work when roadmap generation is interrupted.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** session, schema
**Tier:** STRICT
**Confidence:** [███████░░░] 72%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) (3-5K tokens, 60s timeout)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0031
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0031/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0031/evidence.md`

**Deliverables:**
- sc:save integration at wave boundaries: saves session state to Serena memory after each wave completion, using key format `sc-roadmap:&lt;spec-name&gt;:&lt;timestamp&gt;` with the roadmap_session schema from spec Section 7.3

**Steps:**
1. **[PLANNING]** Load spec Section 7.3 (session persistence) for save points, memory key format, and session schema
2. **[PLANNING]** Confirm 6 save points: after Wave 0, 1A, 1B, 2, 3, 4 with progressive state accumulation
3. **[EXECUTION]** Implement Serena memory key generation: `sc-roadmap:&lt;spec-name&gt;:&lt;timestamp&gt;`
4. **[EXECUTION]** Implement save point after each wave with appropriate state fields from roadmap_session schema
5. **[EXECUTION]** Implement spec file hash computation and storage for mismatch detection
6. **[EXECUTION]** Implement graceful degradation: if Serena unavailable, proceed without persistence with user warning
7. **[VERIFICATION]** Verify save triggers after each wave; verify session schema completeness; verify Serena unavailable fallback
8. **[COMPLETION]** Document save point inventory and session schema

**Acceptance Criteria:**
- sc:save triggered at each of the 6 wave boundaries per spec Section 7.3
- Serena memory key follows `sc-roadmap:&lt;spec-name&gt;:&lt;timestamp&gt;` format
- roadmap_session schema includes all fields: spec_source, output_dir, flags, last_completed_wave, extraction_complete, complexity_score, primary_persona, template_selected, milestone_count, adversarial_results, validation_score
- Graceful degradation when Serena unavailable: proceed without persistence, warn user

**Validation:**
- Manual check: Verify 6 save points; verify memory key format; verify schema completeness; verify Serena fallback
- Evidence: linkable artifact produced (evidence.md with save point inventory)

**Dependencies:** T01.01 (SKILL.md wave definitions)
**Rollback:** TBD
**Notes:** Tier: STRICT due to "session" and "schema" keyword matches. Per roadmap risk R-008, spec-hash storage enables stale artifact detection on resume.

---

### T06.04 — Implement sc:load resume protocol with spec-hash mismatch detection

**Roadmap Item ID(s):** R-032
**Why:** Resume protocol detects incomplete sessions from Serena memory and offers to continue from the last completed wave, preventing duplicate work across sessions.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** session, data integrity
**Tier:** STRICT
**Confidence:** [███████░░░] 72%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) (3-5K tokens, 60s timeout)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0032
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0032/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0032/evidence.md`

**Deliverables:**
- sc:load resume protocol: detects matching Serena memory sessions, prompts user for resume, validates spec file unchanged via hash comparison, resumes from last completed wave

**Steps:**
1. **[PLANNING]** Load spec Section 7.3 resume protocol for matching logic, user prompt, and hash detection
2. **[PLANNING]** Confirm resume flow: detect session → prompt user → validate hash → resume or start fresh
3. **[EXECUTION]** Implement session matching: find Serena memory entries with matching spec_source + output_dir
4. **[EXECUTION]** Implement user prompt: "Found incomplete roadmap session (last completed: Wave X). Resume? [Y/n]"
5. **[EXECUTION]** Implement spec-hash comparison: compute current hash, compare with stored hash, warn if mismatch
6. **[EXECUTION]** Implement resume logic: skip to wave after last_completed_wave, reload artifacts from disk; if declined, start fresh (collision protocol applies)
7. **[VERIFICATION]** Test resume with: matching session, no session, spec-hash mismatch; verify correct behavior in each case
8. **[COMPLETION]** Document resume flow and hash mismatch handling

**Acceptance Criteria:**
- Detects incomplete sessions from Serena memory matching current spec_source + output_dir
- Prompts user with exact message format from spec Section 7.3
- Spec-hash mismatch triggers warning: "Spec file has changed since last session. Starting fresh to avoid stale extraction."
- Fresh start uses collision protocol (-N suffix) for existing artifacts

**Validation:**
- Manual check: Verify session matching logic; verify prompt message format; verify hash mismatch warning; verify collision protocol on fresh start
- Evidence: linkable artifact produced (evidence.md with resume scenario test matrix)

**Dependencies:** T06.03 (sc:save must store session data first)
**Rollback:** TBD
**Notes:** Tier: STRICT due to "session" keyword match. Per spec Section 7.3, resume is best-effort; hash mismatch forces fresh start to avoid stale extraction.

---

### Checkpoint: Phase 6 / Tasks 01-04

**Purpose:** Validate command interface updates and session persistence before progress reporting implementation.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P06-T01-T04.md`
**Verification:**
- Command file contains all flags and at least 7 examples
- sc:save triggers at wave boundaries with complete session schema
- sc:load detects sessions, validates hash, and offers resume

**Exit Criteria:**
- Command file documentation complete and correctly sized
- Session persistence round-trip tested: save → load → resume
- Spec-hash mismatch detection verified

---

### T06.05 — Implement progress reporting at wave boundaries

**Roadmap Item ID(s):** R-033
**Why:** Progress reporting keeps users informed during long-running roadmap generation, especially in combined mode with two adversarial passes.
**Effort:** XS
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0033
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0033/spec.md`

**Deliverables:**
- Progress reporting at each wave boundary: wave number/name, completion status, key decisions made, next wave

**Steps:**
1. **[PLANNING]** Load spec FR-013 (progress reporting) for message format and required content
2. **[PLANNING]** Confirm progress message format includes: wave number, completion status, key decisions, next steps
3. **[EXECUTION]** Implement progress message emission after Wave 0, 1A, 1B, 2, 3, 4 completion
4. **[EXECUTION]** Include key decisions in each message: Wave 0 (validation results), Wave 1B (requirement count, complexity), Wave 2 (milestone count), Wave 3 (artifacts written), Wave 4 (validation score)
5. **[VERIFICATION]** Verify all 6 wave boundaries emit progress messages with correct format
6. **[COMPLETION]** Document progress message inventory

**Acceptance Criteria:**
- Progress messages emitted at all 6 wave boundaries (0, 1A, 1B, 2, 3, 4)
- Each message includes wave number/name, completion status, key decisions, and next steps
- Message formats match spec FR-013 examples exactly (e.g., "Wave 1B complete: extraction finished (XX requirements, complexity: X.XX). extraction.md written.")
- Final message (Wave 4 or end of generation) includes artifact summary per spec FR-008

**Validation:**
- Manual check: Verify all 6 progress messages present; verify format matches spec examples
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.01 (SKILL.md wave definitions)
**Rollback:** TBD
**Notes:** Per spec risk R-005, progress reporting keeps users informed during combined mode which may take longer.

---

### Checkpoint: End of Phase 6

**Purpose:** Final gate for command interface and session management; confirms documentation, persistence, and reporting are complete.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P06-END.md`
**Verification:**
- Command file has all flags, examples, and boundaries
- Session persistence save/load/resume cycle works end-to-end
- Progress messages emit at all wave boundaries

**Exit Criteria:**
- All 5 tasks (T06.01-T06.05) marked complete with evidence artifacts
- Phase 7 dependency (command interface for flag handling) confirmed available
- User-facing documentation complete and accurately reflects all modes

---

**End of Phase 6** | Tasks: 5 | Deliverables: 5 (D-0029–D-0033) | Tier Distribution: STRICT: 2, STANDARD: 2, LIGHT: 1, EXEMPT: 0
