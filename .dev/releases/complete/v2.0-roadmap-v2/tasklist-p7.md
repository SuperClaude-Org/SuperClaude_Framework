# TASKLIST — sc:roadmap v2 — Phase 7: Polish, Edge Cases &amp; Combined Mode

**Parent Tasklist**: `tasklist-overview.md`
**Phase**: 7 of 7
**Task Range**: T07.01–T07.04
**Priority Wave**: P2
**Dependencies**: Phase 4 (adversarial integration for combined mode), Phase 5 (validation for quality gate edge cases), Phase 6 (command interface for flag handling)
**Tier Distribution**: STRICT: 1, STANDARD: 3, LIGHT: 0, EXEMPT: 0

---

## Phase 7: Polish, Edge Cases &amp; Combined Mode

Implement combined mode (multi-spec + multi-roadmap chaining), interactive mode refinements, --dry-run flag, and edge case handling. This is the final phase that integrates all capabilities from Phases 1-6 into a polished, production-ready command. Combined mode requires both adversarial integration (Phase 4) and validation (Phase 5) to be complete.

---

### T07.01 — Implement combined mode chaining multi-spec + multi-roadmap

**Roadmap Item ID(s):** R-034
**Why:** Combined mode chains multi-spec consolidation followed by multi-roadmap generation, enabling users to consolidate multiple specs AND generate competing roadmap variants in a single command invocation.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** cross-cutting scope (system-wide chaining), data integrity (artifact chaining)
**Tier:** STRICT
**Confidence:** [███████░░░] 72%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) (3-5K tokens, 60s timeout)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0034
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0034/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0034/evidence.md`

**Deliverables:**
- Combined mode implementation: chains Wave 1A (multi-spec consolidation → unified-spec.md) → Wave 1B (extraction from unified spec) → Wave 2 (multi-roadmap generation via sc:adversarial) → Waves 3-4 (validation on unified roadmap)

**Steps:**
1. **[PLANNING]** Load spec FR-005 (combined mode) for the chaining flow and artifact handoff rules
2. **[PLANNING]** Confirm chaining order: --specs → sc:adversarial --compare → unified-spec.md → extraction → sc:adversarial --generate roadmap → unified-roadmap.md → validation
3. **[EXECUTION]** Implement flag detection: both --specs AND --multi-roadmap present triggers combined mode
4. **[EXECUTION]** Implement artifact chaining: Wave 1A output (unified-spec.md) becomes Wave 1B input; Wave 1B extraction feeds Wave 2 adversarial generation
5. **[EXECUTION]** Implement error propagation: if Wave 1A fails (consolidation), abort before Wave 2 (no multi-roadmap attempt on failed unification)
6. **[EXECUTION]** Implement progress reporting for combined mode: report both adversarial pass completions
7. **[VERIFICATION]** Test combined mode end-to-end: verify both adversarial passes execute in sequence; verify artifact chaining; verify error propagation
8. **[COMPLETION]** Document chaining flow and artifact handoff points

**Acceptance Criteria:**
- Both adversarial passes execute in sequence: consolidation first, then multi-roadmap generation
- Artifacts chain correctly: unified-spec.md from Wave 1A → extraction → unified-roadmap.md from Wave 2
- Error in Wave 1A prevents Wave 2 from executing (no partial combined mode)
- Combined mode uses both --specs and --multi-roadmap --agents flags together

**Validation:**
- Manual check: Verify chaining order; verify artifact handoff; verify error propagation stops execution
- Evidence: linkable artifact produced (evidence.md with end-to-end combined mode trace)

**Dependencies:** T04.02 (multi-spec consolidation), T04.03 (multi-roadmap generation), T05.03 (validation for final output)
**Rollback:** TBD
**Notes:** Per roadmap risk R-005, combined mode may take longer; progress reporting keeps user informed. Per spec FR-005, this is the most complex invocation path.

---

### T07.02 — Implement interactive mode user prompts at all decision points

**Roadmap Item ID(s):** R-035
**Why:** Interactive mode provides user control at critical decision points including persona selection, template choice, and convergence thresholds during adversarial debate.
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
**Deliverable IDs:** D-0035
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0035/spec.md`

**Deliverables:**
- Interactive mode user prompts at all decision points: persona selection confirmation, template choice approval, convergence threshold decisions, and adversarial conflict resolution approvals

**Steps:**
1. **[PLANNING]** Load spec FR-003 and FR-005 for interactive mode decision points
2. **[PLANNING]** Identify all decision points: persona selection (Wave 1B), template choice (Wave 2), convergence thresholds (Waves 1A/2), conflict resolution (adversarial modes)
3. **[EXECUTION]** Implement user prompt for persona selection: display auto-detected persona with confidence, allow override
4. **[EXECUTION]** Implement user prompt for template choice: display compatibility scores, allow selection
5. **[EXECUTION]** Implement user prompt at convergence thresholds: display convergence score, allow proceed/abort decision
6. **[VERIFICATION]** Verify prompts appear only when --interactive flag is set; verify non-interactive mode uses auto-decisions
7. **[COMPLETION]** Document decision point inventory and prompt designs

**Acceptance Criteria:**
- User prompts appear at persona selection, template choice, and convergence thresholds when --interactive is set
- Non-interactive mode makes all decisions automatically without prompts
- Prompts display relevant data (confidence scores, compatibility scores, convergence percentages) to inform user decisions
- User responses correctly override auto-detected values

**Validation:**
- Manual check: Verify prompts only appear with --interactive; verify auto-mode works without prompts; verify user overrides take effect
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T02.04 (persona selection), T03.01 (template choice), T04.05 (--interactive flag propagation)
**Rollback:** TBD
**Notes:** None.

---

### T07.03 — Implement --dry-run flag

**Roadmap Item ID(s):** R-036
**Why:** The --dry-run flag allows users to preview the roadmap structure (milestones, dependencies, estimated effort) without writing output files, useful for iterating on inputs.
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
**Deliverable IDs:** D-0036
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0036/spec.md`

**Deliverables:**
- --dry-run flag implementation per FR-018: executes Waves 0-2 (prerequisites, extraction, planning) and outputs structured console preview (milestone summary table, dependency graph, template selection, complexity assessment), skips Wave 3 (file generation) and Wave 4 (validation), no session persistence

**Steps:**
1. **[PLANNING]** Load spec FR-018 (--dry-run mode behavior) for output format, wave execution scope, and session persistence rules
2. **[PLANNING]** Confirm behavior: preview structure to console, no files written
3. **[EXECUTION]** Implement flag detection: --dry-run stops after Wave 2 planning
4. **[EXECUTION]** Implement console preview output: milestone summary, dependency graph, template selection, complexity assessment
5. **[VERIFICATION]** Verify no files written to output directory when --dry-run is set; verify console output contains expected preview sections
6. **[COMPLETION]** Document --dry-run output format

**Acceptance Criteria:**
- --dry-run outputs structured roadmap preview to console per FR-018 format (milestone summary table, dependency graph, template selection with score, complexity assessment)
- No files written to output directory; no session persistence triggered
- Waves 0-2 execute normally (prerequisites validated, extraction performed, planning complete)
- Wave 3 (generation) and Wave 4 (validation) are skipped
- Console output uses FR-018 structured format with clear section headers

**Validation:**
- Manual check: Verify no output files written; verify console output contains preview sections; verify Waves 0-2 execute
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T03.02 (milestone planning must work for preview), T06.01 (flag documented in command file)
**Rollback:** TBD
**Notes:** None.

---

### T07.04 — Implement edge case handling

**Roadmap Item ID(s):** R-037
**Why:** Edge cases (empty specs, invalid YAML, circular dependencies) must produce graceful errors with actionable messages rather than silent failures or confusing stack traces.
**Effort:** M
**Risk:** Medium
**Risk Drivers:** data integrity (invalid input handling)
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0037
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0037/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0037/evidence.md`

**Deliverables:**
- Edge case handling for: empty spec files, malformed/invalid YAML in specs, circular milestone dependencies, very small specs (&lt;5 lines), spec files with no actionable requirements

**Steps:**
1. **[PLANNING]** Identify edge cases from spec deliverable D7.4 and roadmap risk register
2. **[PLANNING]** Catalog expected behavior for each edge case: error message format, recovery action, user guidance
3. **[EXECUTION]** Implement empty spec detection: abort with "Specification file is empty. Provide a non-empty spec."
4. **[EXECUTION]** Implement invalid YAML detection: catch parse errors in spec frontmatter, report line/column if available
5. **[EXECUTION]** Implement circular dependency detection: validate milestone dependency graph is a DAG, report cycle if found
6. **[EXECUTION]** Implement minimal spec handling: warn for &lt;5 lines but attempt extraction; abort if no requirements extractable
7. **[VERIFICATION]** Test each edge case; verify graceful error messages and no silent failures
8. **[COMPLETION]** Document edge case catalog with expected behaviors

**Acceptance Criteria:**
- Empty specs produce clear error: abort with actionable message
- Invalid YAML in spec frontmatter caught and reported with location info
- Circular dependencies detected during milestone planning with cycle reported
- All edge cases produce graceful errors with actionable messages (no stack traces, no silent failures)

**Validation:**
- Manual check: Trigger each edge case and verify error message; verify no silent failures; verify no stack traces
- Evidence: linkable artifact produced (evidence.md with edge case test matrix)

**Dependencies:** T02.01 (Wave 0 validation framework), T03.02 (milestone dependency mapping)
**Rollback:** TBD
**Notes:** None.

---

### Checkpoint: End of Phase 7

**Purpose:** Final gate for entire roadmap; confirms all modes, edge cases, and polish items are complete and the command is production-ready.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P07-END.md`
**Verification:**
- Combined mode chains both adversarial passes correctly end-to-end
- Interactive mode prompts appear at all decision points when flag is set
- All cataloged edge cases produce graceful errors

**Exit Criteria:**
- All 4 tasks (T07.01-T07.04) marked complete with evidence artifacts
- End-to-end functional: single-spec, multi-spec, multi-roadmap, combined modes
- sc:roadmap command production-ready per spec success criteria (Section 12)

---

**End of Phase 7** | Tasks: 4 | Deliverables: 4 (D-0034–D-0037) | Tier Distribution: STRICT: 1, STANDARD: 3, LIGHT: 0, EXEMPT: 0

---

## End of Tasklist

**Total Tasks**: 37 (T01.01–T07.04)
**Total Deliverables**: 37 (D-0001–D-0037)
**Phases**: 7 (2 P0 + 4 P1 + 1 P2)
**Tier Distribution**: STRICT: 5, STANDARD: 27, LIGHT: 3, EXEMPT: 0
**Checkpoints**: 12 (7 end-of-phase + 5 mid-phase)

**Dependency Summary**:
- Phase 1: No dependencies (start here)
- Phase 2: Depends on Phase 1
- Phase 3: Depends on Phase 2
- Phase 4: Depends on Phase 3 + sc:adversarial availability
- Phase 5: Depends on Phase 3 (parallel with Phase 4)
- Phase 6: Depends on Phase 1 (parallel with Phases 2-5)
- Phase 7: Depends on Phases 4, 5, 6

**Parallel Opportunities**:
- Phase 4 ‖ Phase 5 (both depend on Phase 3)
- Phase 6 ‖ Phases 2-5 (only depends on Phase 1)
