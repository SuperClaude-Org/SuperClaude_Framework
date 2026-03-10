# Phase 2 -- Spec Synthesis Rewrite

Replace code generation Phase 3 with spec synthesis including embedded brainstorm. This phase rewrites SKILL.md to implement template instantiation, content population, brainstorm pass, and gap incorporation while removing legacy code generation instructions.

### T02.01 -- Rewrite Phase 3 Template Instantiation (3a) and Content Population (3b) in SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013, R-014, R-015 |
| Why | The roadmap requires rewriting Phase 3 in SKILL.md (FR-013) to add step 3a (load template, create working copy at `{work_dir}/portify-release-spec.md`) and step 3b (map Phase 1+2 outputs to template sections per the 10-section mapping table). |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0009, D-0010 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0009/spec.md
- TASKLIST_ROOT/artifacts/D-0010/spec.md

**Deliverables:**
1. Phase 3 step 3a instructions in SKILL.md: load template from `src/superclaude/examples/release-spec-template.md`, create working copy at `{work_dir}/portify-release-spec.md` (FR-001)
2. Phase 3 step 3b instructions in SKILL.md: map Phase 1 + Phase 2 outputs to template sections per the 10-section mapping table (FR-002, FR-003)

**Steps:**
1. **[PLANNING]** Read current SKILL.md Phase 3 to understand existing structure and identify replacement boundaries
2. **[PLANNING]** Map the 10-section mapping table from spec to template section names
3. **[EXECUTION]** Write step 3a: template loading with path `src/superclaude/examples/release-spec-template.md` and working copy creation at `{work_dir}/portify-release-spec.md`
4. **[EXECUTION]** Write step 3b: content population instructions mapping each Phase 1+2 output to its corresponding template section
5. **[EXECUTION]** Specify the Phase 2→3 entry gate conditions (FR-060.1): Phase 2 contract `status: completed`, blocking checks passed, `step_mapping` contains >=1 entry
6. **[VERIFICATION]** Verify step 3a references correct template path and step 3b covers all 10 mapping entries
7. **[COMPLETION]** Document mapping correspondence in evidence artifacts

**Acceptance Criteria:**
- SKILL.md contains Phase 3 step 3a that loads template from `src/superclaude/examples/release-spec-template.md` and creates working copy at `{work_dir}/portify-release-spec.md`
- SKILL.md contains Phase 3 step 3b with explicit mapping of all Phase 1+2 outputs to template sections per the 10-section mapping table
- Phase 2→3 entry gate conditions (contract `status: completed`, blocking checks passed, `step_mapping` >=1) are specified
- Every `step_mapping` entry produces a corresponding FR reference per SC-004

**Validation:**
- Manual check: SKILL.md Phase 3 contains step 3a (template instantiation) and step 3b (content population) with correct paths and mapping entries
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0009/spec.md)

**Dependencies:** T01.02, T01.03
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
**Notes:** Tier STRICT due to "rewrite" + "restructure" keyword match on SKILL.md behavioral protocol. R-013 / FR-013 is treated as umbrella rewrite scope here; T02.01 covers the 3a/3b rewrite while T02.03 covers the removal sub-aspect of that same umbrella change.

---

### T02.02 -- Implement Embedded Brainstorm Pass (3c) and Gap Incorporation (3d) in SKILL.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016, R-017 |
| Why | The roadmap requires Phase 3 step 3c (FR-004, FR-005, FR-006): multi-persona non-interactive brainstorm analysis with structured output format, and step 3d (FR-007): incorporating actionable findings into spec body with unresolvable items going to Section 11. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011, D-0012 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0011/spec.md
- TASKLIST_ROOT/artifacts/D-0012/notes.md

**Deliverables:**
1. Phase 3 step 3c instructions in SKILL.md: multi-persona (architect + analyzer + backend) non-interactive analysis with structured output format `{gap_id, description, severity, affected_section, persona}` and zero-gap handling with explicit "No gaps identified" summary and `gaps_identified: 0` contract field
2. Phase 3 step 3d instructions in SKILL.md: incorporate actionable findings into spec body sections, route unresolvable gaps to Section 11 (Open Items)

**Steps:**
1. **[PLANNING]** Review `sc:brainstorm` behavioral patterns in `src/superclaude/commands/brainstorm.md` to identify patterns to embed
2. **[PLANNING]** Define the structured output schema for brainstorm findings
3. **[EXECUTION]** Write step 3c: multi-persona analysis instructions with architect, analyzer, and backend persona perspectives
4. **[EXECUTION]** Write step 3c structured output format: `{gap_id, description, severity, affected_section, persona}`
5. **[EXECUTION]** Write step 3c zero-gap handling: explicit "No gaps identified" summary with `gaps_identified: 0` contract field
6. **[EXECUTION]** Write step 3d: gap incorporation rules — actionable to spec body, unresolvable to Section 11
7. **[VERIFICATION]** Verify brainstorm output schema matches specification and zero-gap path produces correct summary
8. **[COMPLETION]** Document brainstorm behavioral patterns embedded and gap routing logic

**Acceptance Criteria:**
- SKILL.md contains Phase 3 step 3c with multi-persona (architect, analyzer, backend) non-interactive brainstorm instructions
- Brainstorm output uses structured format with fields: `gap_id`, `description`, `severity`, `affected_section`, `persona`
- Zero-gap path produces explicit "No gaps identified" summary and sets `gaps_identified: 0` in contract
- Step 3d routes actionable findings to corresponding spec body sections and unresolvable gaps to Section 11

**Validation:**
- Manual check: SKILL.md Phase 3 step 3c contains brainstorm instructions with all 3 personas and structured output schema, step 3d contains gap routing rules
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0011/spec.md)

**Dependencies:** T02.01
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
**Notes:** Behavioral patterns from `sc:brainstorm` are embedded inline per Constraint 1 (no inter-skill command invocation).

---

### T02.03 -- Remove Code Generation Instructions and Preserve refs/code-templates.md

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018, R-019 |
| Why | The roadmap requires removing all code generation instructions from SKILL.md (FR-013) and preserving `refs/code-templates.md` as reference-only while ensuring no phase loads it (R-006). |
| Effort | S |
| Risk | Medium |
| Risk Drivers | breaking (removal of existing functionality) |
| Tier | STANDARD |
| Confidence | [███████░░░] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013, D-0014 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0013/evidence.md
- TASKLIST_ROOT/artifacts/D-0014/evidence.md

**Deliverables:**
1. SKILL.md with all code generation instructions removed (no Phase 3/4 references to code output, main.py patching, or integration test generation)
2. `refs/code-templates.md` confirmed preserved on disk but not loaded by any workflow phase

**Steps:**
1. **[PLANNING]** Identify all code generation instructions in current SKILL.md Phase 3 and Phase 4
2. **[PLANNING]** Scan SKILL.md for any `refs/code-templates.md` load references
3. **[EXECUTION]** Remove all code generation instructions from SKILL.md Phase 3
4. **[EXECUTION]** Verify `refs/code-templates.md` exists on disk but is not referenced by any phase's load step
5. **[VERIFICATION]** Grep SKILL.md for residual code generation keywords (`code_output`, `main.py`, `generate_code`, `integration_test`)
6. **[COMPLETION]** Document removed instructions and refs preservation status

**Acceptance Criteria:**
- SKILL.md contains zero code generation instructions: no references to generating code files, patching `main.py`, or creating integration tests
- `src/superclaude/skills/sc-cli-portify-protocol/refs/code-templates.md` exists on disk (file preserved)
- Zero SKILL.md phases contain load/read instructions for `refs/code-templates.md`
- Grep for `code-templates` in SKILL.md phase sections returns zero matches in load/execution contexts

**Validation:**
- Manual check: `grep -n 'code-templates\|code_output\|generate_code\|main\.py' src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` returns zero results in phase execution sections
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0013/evidence.md)

**Dependencies:** T02.01, T02.02
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
**Notes:** Risk is medium due to removing existing functionality; regression testing in Phase 5 covers this. This task covers the removal sub-aspect of umbrella requirement R-013 / FR-013, while T02.01 covers the 3a/3b rewrite scope.

---

### T02.04 -- Add Phase 3 Timing Instrumentation (phase_3_seconds)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | The roadmap requires adding phase timing instrumentation for `phase_3_seconds` (SC-013) to track Phase 3 execution duration in the return contract. |
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
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0015/evidence.md

**Deliverables:**
1. Phase 3 timing instrumentation in SKILL.md that records `phase_3_seconds` in the return contract's `phase_timing` field

**Steps:**
1. **[PLANNING]** Identify the return contract structure for `phase_timing` field
2. **[PLANNING]** Determine instrumentation placement (Phase 3 start/end boundaries)
3. **[EXECUTION]** Add timing start marker at Phase 3 entry
4. **[EXECUTION]** Add timing end marker and `phase_3_seconds` computation at Phase 3 exit
5. **[VERIFICATION]** Verify `phase_3_seconds` is populated in the `phase_timing` contract field
6. **[COMPLETION]** Document timing instrumentation location and contract field reference

**Acceptance Criteria:**
- SKILL.md Phase 3 contains timing instrumentation that populates `phase_3_seconds` in the return contract
- `phase_3_seconds` value represents elapsed wall clock seconds for Phase 3 execution
- Timing field appears in the `phase_timing` section of the return contract
- NFR-001 10-minute advisory target documented alongside instrumentation

**Validation:**
- Manual check: SKILL.md Phase 3 has explicit start/end timing markers and `phase_3_seconds` appears in return contract schema
- Evidence: linkable artifact produced (TASKLIST_ROOT/artifacts/D-0015/evidence.md)

**Dependencies:** T02.01
**Rollback:** `git checkout -- src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`

---

### Checkpoint: End of Phase 2

**Purpose:** Verify Gate B criteria are met: every `step_mapping` entry produces a corresponding FR, brainstorm section present in output, zero remaining placeholder sentinels, phase timing target documented.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P02-END.md
**Verification:**
- Every `step_mapping` entry in SKILL.md Phase 3 produces a corresponding FR reference (SC-004)
- Brainstorm section (step 3c) is present in SKILL.md Phase 3 output with structured output format (SC-005)
- Self-validation check (SC-003) confirms zero remaining `{{SC_PLACEHOLDER:}}` sentinels in generated output
- Phase 3 timing instrumentation documents the NFR-001 10-minute wall clock advisory target (non-blocking)
**Exit Criteria:**
- All 4 tasks (T02.01-T02.04) completed with deliverables D-0009 through D-0015 produced
- Code generation instructions fully removed from SKILL.md
- `refs/code-templates.md` preserved but unloaded by any phase
