# Phase 2 — Command & Skill Implementation

Implement the full `tasklist.md` command file (M2) and reformat the v3.0 generator algorithm into `SKILL.md` with extracted reference files (M3). These two workstreams are parallelizable — the command and skill have no mutual dependencies until integration in Phase 3.

### T02.01 — Implement YAML frontmatter in `tasklist.md` with all 8 fields per §5.1

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | The command frontmatter declares identity, tools, MCP servers, and personas required by the Claude Code command system |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0005/spec.md`

**Deliverables:**
- Command frontmatter in `src/superclaude/commands/tasklist.md` with fields: name, description, category, complexity, allowed-tools, mcp-servers, personas, version

**Steps:**
1. **[PLANNING]** Read §5.1 frontmatter specification for exact field values
2. **[PLANNING]** Read existing placeholder `src/superclaude/commands/tasklist.md`
3. **[EXECUTION]** Replace placeholder frontmatter with complete 8-field YAML block matching spec values (FR-026–FR-030)
4. **[EXECUTION]** Verify field values: `name: tasklist`, `category: utility`, `complexity: high`, `version: "1.0.0"`
5. **[VERIFICATION]** Parse YAML frontmatter to confirm all 8 fields present with correct values
6. **[COMPLETION]** Record frontmatter implementation evidence

**Acceptance Criteria:**
- All 8 frontmatter fields present: name, description, category, complexity, allowed-tools, mcp-servers, personas, version
- Values match spec §5.1 exactly: `name: tasklist`, `description: "Generate deterministic, Sprint CLI-compatible tasklist bundles from roadmaps"`, `category: utility`, `complexity: high`
- YAML parses without errors
- Frontmatter evidence recorded

**Validation:**
- Manual check: YAML frontmatter parses and contains all 8 fields matching spec §5.1 values
- Evidence: linkable artifact produced (frontmatter field verification output)

**Dependencies:** T01.03
**Rollback:** Restore placeholder frontmatter from T01.03
**Notes:** None

---

### T02.02 — Implement all 8 required sections in `tasklist.md` per §5.3

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | The command file requires 8 standard sections (Triggers, Usage, Behavioral Summary, Arguments, Input Validation, Activation, Examples, Boundaries) for Claude Code command discoverability and execution |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0006/spec.md`

**Deliverables:**
- All 8 required sections in `src/superclaude/commands/tasklist.md` with correct markdown headings

**Steps:**
1. **[PLANNING]** Read §5.3 section table for required sections and content
2. **[PLANNING]** Review existing command files (e.g., `src/superclaude/commands/roadmap.md`) for section format conventions
3. **[EXECUTION]** Write `# /sc:tasklist` title and one-line description
4. **[EXECUTION]** Write all 8 sections: `## Triggers`, `## Usage`, `## Behavioral Summary`, `## Arguments`, `## Input Validation`, `## Activation`, `## Examples`, `## Boundaries`
5. **[EXECUTION]** Include 3-4 usage examples in the Examples section
6. **[VERIFICATION]** Grep for all 8 section headings in the command file; confirm correct markdown heading levels
7. **[VERIFICATION]** Count total lines — warn if >200, fail if >500 (RISK-007)
8. **[COMPLETION]** Record section implementation evidence

**Acceptance Criteria:**
- All 8 sections present with correct `##` headings matching §5.3 section table
- `# /sc:tasklist` title present as level-1 heading
- Examples section contains 3-4 usage examples
- Total line count is <200 (target) or <500 (hard limit per RISK-007)

**Validation:**
- Manual check: `grep -c "^## " src/superclaude/commands/tasklist.md` returns 8
- Evidence: linkable artifact produced (section heading verification output)

**Dependencies:** T02.01
**Rollback:** Restore to frontmatter-only state from T02.01
**Notes:** RISK-007 mitigation: target <150 lines; if approaching 400, audit for content that belongs in skill

---

### T02.03 — Implement argument spec in `tasklist.md` per §5.2

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | The command must parse required `<roadmap-path>` and optional `--spec`, `--output` arguments for skill invocation |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0007/spec.md`

**Deliverables:**
- Arguments table in `## Arguments` section matching spec §5.2 with `@file` and explicit path support documented

**Steps:**
1. **[PLANNING]** Read §5.2 argument specification
2. **[PLANNING]** Identify argument format: `/sc:tasklist <roadmap-path> [--spec <spec-path>] [--output <output-dir>]`
3. **[EXECUTION]** Write syntax line in `## Usage` section
4. **[EXECUTION]** Write arguments table with columns: Argument, Required, Default, Description (FR-013–FR-016)
5. **[VERIFICATION]** Verify all 3 arguments documented with correct required/default values
6. **[COMPLETION]** Record argument specification evidence

**Acceptance Criteria:**
- Arguments table contains all 3 arguments: `<roadmap-path>` (required), `--spec` (optional), `--output` (optional)
- Default for `--output` documented as "Auto-derived from roadmap TASKLIST_ROOT"
- Both `@file` syntax and explicit path documented as supported input methods
- Argument table format matches existing command file conventions

**Validation:**
- Manual check: Arguments table in `## Arguments` section contains 3 rows with correct Required/Default values
- Evidence: linkable artifact produced (argument table verification)

**Dependencies:** T02.02
**Rollback:** Remove arguments content from `## Arguments` section
**Notes:** None

---

### T02.04 — Implement input validation in `tasklist.md` per §5.4

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | The command must validate inputs before invoking the skill to prevent partial/invalid generation runs |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0008/spec.md`

**Deliverables:**
- Input validation section with 4 validation checks, 2-field error format (`error_code` + `message`), and exit-without-invoke behavior

**Steps:**
1. **[PLANNING]** Read §5.4 input validation specification for all 4 checks
2. **[PLANNING]** Review error format: `error_code` + `message` fields
3. **[EXECUTION]** Document check 1: `<roadmap-path>` resolves to readable, non-empty file
4. **[EXECUTION]** Document check 2: `--spec` file resolves to readable file (if provided)
5. **[EXECUTION]** Document check 3: `--output` parent directory exists (if provided)
6. **[EXECUTION]** Document check 4: TASKLIST_ROOT derivation succeeds (if `--output` not provided)
7. **[VERIFICATION]** Verify all 4 checks documented; error format includes `error_code` and `message`; exit-without-invoke behavior specified (FR-018–FR-022, NFR-013)
8. **[COMPLETION]** Record validation specification evidence

**Acceptance Criteria:**
- All 4 validation checks documented in `## Input Validation` section per §5.4
- Error format specifies 2 fields: `error_code` (category string) and `message` (human-readable)
- Exit-without-invoke behavior clearly stated: command exits on failure, no partial output
- Error codes include EMPTY_INPUT, MISSING_FILE, DERIVATION_FAILED categories

**Validation:**
- Manual check: `## Input Validation` section contains 4 numbered checks and error format specification
- Evidence: linkable artifact produced (validation check verification)

**Dependencies:** T02.02
**Rollback:** Remove input validation content from `## Input Validation` section
**Notes:** Tier conflict: "implement" (STANDARD) + validation logic (STRICT) → resolved to STRICT by priority rule

---

### Checkpoint: Phase 2 / Tasks T02.01–T02.05

**Purpose:** Verify command file frontmatter, sections, arguments, validation, and activation are correctly implemented before proceeding to remaining command and skill tasks.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-T01-T05.md`

**Verification:**
- `src/superclaude/commands/tasklist.md` has complete 8-field frontmatter, 8 sections, argument table, and input validation
- Line count is within RISK-007 limits (<200 target, <500 hard limit)
- YAML frontmatter parses without errors

**Exit Criteria:**
- T02.01 through T02.04 completed; frontmatter, sections, arguments, and validation all present
- No section headings missing or misformatted
- Input validation covers all 4 checks with proper error format

---

### T02.05 — Implement `## Activation` section in `tasklist.md` per §5.5

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | The Activation section is the mandatory bridge between command and skill — it invokes `Skill sc:tasklist-protocol` with context |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0009/spec.md`

**Deliverables:**
- `## Activation` section with exact `Skill sc:tasklist-protocol` invocation text and context passing documentation

**Steps:**
1. **[PLANNING]** Read §5.5 Activation section specification
2. **[PLANNING]** Review existing command files for Activation section format conventions
3. **[EXECUTION]** Write `## Activation` section with **MANDATORY** invocation: `> Skill sc:tasklist-protocol`
4. **[EXECUTION]** Document context passing: roadmap text, spec text (if provided), output directory
5. **[VERIFICATION]** Verify `## Activation` section contains exact `Skill sc:tasklist-protocol` invocation text (FR-024)
6. **[COMPLETION]** Record activation section evidence

**Acceptance Criteria:**
- `## Activation` section present with `**MANDATORY**` label
- Contains exact invocation text: `> Skill sc:tasklist-protocol`
- Context passing documented: roadmap text, spec text, output directory
- Warning text present: "Do NOT attempt to generate the tasklist using only this command file"

**Validation:**
- Manual check: `grep "Skill sc:tasklist-protocol" src/superclaude/commands/tasklist.md` returns match
- Evidence: linkable artifact produced (activation section content verification)

**Dependencies:** T02.02
**Rollback:** Remove activation content from `## Activation` section
**Notes:** None

---

### T02.06 — Implement `## Boundaries` section in `tasklist.md` per §5.6

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | The Will/Will-Not contract defines clear scope boundaries for the command's responsibilities |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0010/spec.md`

**Deliverables:**
- `## Boundaries` section with Will and Will Not lists matching spec §5.6

**Steps:**
1. **[PLANNING]** Read §5.6 Boundaries specification for Will and Will-Not lists
2. **[PLANNING]** Review existing command files for Boundaries section conventions
3. **[EXECUTION]** Write `## Boundaries` section with **Will:** list (4 items) and **Will Not:** list (4 items) per spec
4. **[VERIFICATION]** Verify both Will and Will Not lists present with correct items (FR-032, FR-033)
5. **[COMPLETION]** Record boundaries section evidence

**Acceptance Criteria:**
- `## Boundaries` section present with both `**Will:**` and `**Will Not:**` subsections
- Will list includes: parse/validate arguments, derive TASKLIST_ROOT, invoke skill, report file paths
- Will Not list includes: execute generation algorithm, modify source files, run sprint, generate beyond bundle
- Lists match spec §5.6 exactly

**Validation:**
- Manual check: `## Boundaries` section contains `**Will:**` and `**Will Not:**` with correct list items
- Evidence: linkable artifact produced (boundaries section verification)

**Dependencies:** T02.02
**Rollback:** Remove boundaries content from `## Boundaries` section
**Notes:** None

---

### T02.07 — Emit STRICT tier classification header before skill invocation per §4.3

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | The classification header signals to the execution runtime that this is a STRICT-tier multi-file generation operation |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0011/spec.md`

**Deliverables:**
- STRICT tier classification header text in `tasklist.md` positioned before the `Skill sc:tasklist-protocol` invocation

**Steps:**
1. **[PLANNING]** Read §4.3 invocation flow for classification header requirements
2. **[PLANNING]** Identify insertion point: after input validation, before skill invocation
3. **[EXECUTION]** Add classification header text: "Emit classification header (STRICT — multi-file generation)" in the Activation section flow
4. **[VERIFICATION]** Verify classification header appears before `Skill sc:tasklist-protocol` invocation in document order (FR-023)
5. **[COMPLETION]** Record classification header evidence

**Acceptance Criteria:**
- STRICT tier classification header present in command output flow
- Header appears before `Skill sc:tasklist-protocol` invocation in document order (FR-023)
- Header identifies operation as STRICT tier with "multi-file generation" rationale
- Classification integrates with `/sc:task-unified` compliance tier system

**Validation:**
- Manual check: Classification header text appears before skill invocation in `## Activation` section
- Evidence: linkable artifact produced (header positioning verification)

**Dependencies:** T02.05
**Rollback:** Remove classification header from Activation section
**Notes:** Tier: STRICT because this implements compliance tier classification logic

---

### T02.08 — Implement file path reporting and TASKLIST_ROOT auto-derivation per §3.1

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | The command must report generated file paths on completion and auto-derive TASKLIST_ROOT when `--output` is omitted |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Cross-cutting scope (derivation algorithm + output reporting) |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0012/spec.md`

**Deliverables:**
- File path reporting on completion (FR-025) and TASKLIST_ROOT derivation logic matching §3.1 algorithm (FR-017)

**Steps:**
1. **[PLANNING]** Read §3.1 TASKLIST_ROOT derivation algorithm (3-step priority order)
2. **[PLANNING]** Identify RISK-002: §3.1 algorithm must be located in v3.0 source and documented exactly
3. **[EXECUTION]** Document TASKLIST_ROOT derivation: (1) match `.dev/releases/current/<segment>/`, (2) match `v<digits>`, (3) fallback `v0.0-unknown`
4. **[EXECUTION]** Document file path reporting: print generated file paths to stdout on successful completion
5. **[VERIFICATION]** Verify derivation logic matches §3.1 exactly; verify path reporting on completion documented
6. **[COMPLETION]** Record derivation and reporting evidence

**Acceptance Criteria:**
- TASKLIST_ROOT derivation logic documents all 3 priority steps from §3.1 algorithm
- File path reporting prints generated `tasklist-index.md` and all `phase-N-tasklist.md` paths on completion
- Derivation algorithm matches v3.0 source exactly (RISK-002 mitigation)
- Both `--output` override and auto-derivation paths are documented

**Validation:**
- Manual check: `## Input Validation` or `## Behavioral Summary` documents the 3-step TASKLIST_ROOT derivation
- Evidence: linkable artifact produced (derivation algorithm documentation)

**Dependencies:** T02.02
**Rollback:** Remove derivation and reporting content
**Notes:** RISK-002: locate exact derivation algorithm in v3.0 source before documenting

---

### T02.09 — Implement SKILL.md frontmatter per §6.1

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | The SKILL.md frontmatter declares the skill identity, tools, and MCP server requirements for Claude Code |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0013/spec.md`

**Deliverables:**
- SKILL.md frontmatter with all required fields per §6.1: name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint

**Steps:**
1. **[PLANNING]** Read §6.1 SKILL.md frontmatter specification
2. **[PLANNING]** Read existing placeholder SKILL.md from T01.04
3. **[EXECUTION]** Replace placeholder frontmatter with complete YAML block: `name: sc:tasklist-protocol`, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint
4. **[VERIFICATION]** Verify `name:` field is `sc:tasklist-protocol` (ends in `-protocol` per FR-057); all fields present (FR-053–FR-057)
5. **[COMPLETION]** Record frontmatter implementation evidence

**Acceptance Criteria:**
- All frontmatter fields present per §6.1: name, description, category, complexity, allowed-tools, mcp-servers, personas, argument-hint
- `name: sc:tasklist-protocol` — ends in `-protocol` (FR-057)
- `allowed-tools: Read, Glob, Grep, Write, Bash, TodoWrite`
- YAML parses without errors

**Validation:**
- Manual check: YAML frontmatter in SKILL.md parses and `name:` value ends in `-protocol`
- Evidence: linkable artifact produced (frontmatter field verification)

**Dependencies:** T01.04
**Rollback:** Restore placeholder frontmatter from T01.04
**Notes:** None

---

### Checkpoint: Phase 2 / Tasks T02.05–T02.09

**Purpose:** Verify command file is complete and SKILL.md frontmatter is ready before proceeding to v3.0 algorithm reformatting.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-T05-T09.md`

**Verification:**
- `tasklist.md` has Activation, Boundaries, classification header, file path reporting, and TASKLIST_ROOT derivation
- `SKILL.md` has complete frontmatter with `name: sc:tasklist-protocol`
- Command file line count is within RISK-007 limits

**Exit Criteria:**
- T02.05 through T02.09 completed; command file structurally complete
- SKILL.md frontmatter ready for body content population
- No orphaned sections or missing content in command file

---

### T02.10 — Reformat v3.0 §0–§9 + Appendix into SKILL.md body per §6.2 structural mapping

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | The SKILL.md body must contain the full v3.0 generator algorithm reformatted into skill convention while preserving exact functional parity |
| Effort | L |
| Risk | High |
| Risk Drivers | Cross-cutting scope (full algorithm reformatting); data integrity (algorithm drift risk) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0014/spec.md`

**Deliverables:**
- v3.0 sections §0–§9 + Appendix reformatted into SKILL.md body following the §6.2 structural mapping table

**Steps:**
1. **[PLANNING]** Read full v3.0 source (`Tasklist-Generator-Prompt-v2.1-unified.md`) and §6.2 structural mapping table
2. **[PLANNING]** Create mapping checklist: each v3.0 section → target SKILL.md section per §6.2
3. **[EXECUTION]** Reformat §0 Non-Leakage Rules → `## Non-Leakage + Truthfulness Rules` (verbatim)
4. **[EXECUTION]** Reformat §1–§9 + Appendix → corresponding SKILL.md sections per §6.2 mapping (all verbatim)
5. **[EXECUTION]** Adapt header + intro to skill format (frontmatter + opening paragraph)
6. **[VERIFICATION]** Diff v3.0 source against SKILL.md body: any non-formatting delta is a defect (RISK-001 mitigation)
7. **[VERIFICATION]** Verify all 12 v3.0 sections are present in SKILL.md per §6.2 mapping table
8. **[COMPLETION]** Record reformatting evidence with diff output

**Acceptance Criteria:**
- All 12 v3.0 sections mapped to SKILL.md per §6.2 structural mapping table
- Content is verbatim — no algorithmic changes, no new features, no behavioral modifications
- Diff between v3.0 source and SKILL.md body shows only formatting/structural changes (RISK-001)
- Every section heading in SKILL.md matches §6.2 target column

**Validation:**
- Manual check: Side-by-side comparison of v3.0 source sections vs. SKILL.md sections confirms verbatim content
- Evidence: linkable artifact produced (diff output showing only structural changes)

**Dependencies:** T02.09
**Rollback:** Restore to frontmatter-only SKILL.md
**Notes:** RISK-001 (HIGH): algorithm drift is the primary project risk. Character-level diff required after reformatting.

---

### T02.11 — Add 6-stage completion reporting contract to SKILL.md per §4.3

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | The stage completion reporting contract enables automated sprint execution monitoring and structural gating between generation stages |
| Effort | M |
| Risk | Medium |
| Risk Drivers | Cross-cutting scope (6 stages with validation criteria and TodoWrite integration) |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0015/spec.md`

**Deliverables:**
- 6-stage completion reporting contract in SKILL.md with per-stage validation criteria, TodoWrite integration, and structural vs. semantic gate distinction

**Steps:**
1. **[PLANNING]** Read §4.3 stage completion reporting contract specification
2. **[PLANNING]** Review the 6 stages: Input Ingest, Parse+Bucket, Task Conversion, Enrichment, File Emission, Self-Check
3. **[EXECUTION]** Add stage reporting section to SKILL.md with all 6 stages and their validation criteria per §4.3 table
4. **[EXECUTION]** Document structural vs. semantic gate distinction: structural gates block advancement, semantic gates are advisory
5. **[EXECUTION]** Document TodoWrite integration for stage progress reporting
6. **[VERIFICATION]** Verify all 6 stages present with validation criteria matching §4.3 (FR-036–FR-049)
7. **[COMPLETION]** Record stage reporting evidence

**Acceptance Criteria:**
- All 6 stages documented with names, validation criteria per §4.3 table
- Structural gates defined: non-empty output, valid ID format, field presence block advancement
- Semantic gates defined: content quality, prose adequacy are advisory (logged but not blocking)
- TodoWrite integration documented for per-stage progress reporting

**Validation:**
- Manual check: SKILL.md contains 6-stage table with validation criteria for each stage
- Evidence: linkable artifact produced (stage contract verification)

**Dependencies:** T02.10
**Rollback:** Remove stage reporting section from SKILL.md
**Notes:** RISK-008: pre-write quality gate criteria must be explicitly defined here (pass/fail for §9 AC #8 and #9)

---

### T02.12 — Extract `rules/tier-classification.md` from SKILL.md §5.3 + Appendix

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Extracted reference file enables human review of tier classification rules without reading the full SKILL.md |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0016/spec.md`

**Deliverables:**
- `src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md` extracted from §5.3 + Appendix

**Steps:**
1. **[PLANNING]** Identify §5.3 and Appendix content in SKILL.md for extraction
2. **[PLANNING]** Confirm `rules/` directory exists (from T01.01)
3. **[EXECUTION]** Write `rules/tier-classification.md` with tier keywords, compound phrases, context boosters, verification routing from §5.3 + Appendix
4. **[VERIFICATION]** Verify extracted content matches SKILL.md §5.3 + Appendix (FR-009)
5. **[COMPLETION]** Record extraction evidence

**Acceptance Criteria:**
- File `rules/tier-classification.md` exists in `src/superclaude/skills/sc-tasklist-protocol/rules/`
- Content matches §5.3 tier keywords, compound phrases, context boosters exactly
- Appendix quick reference content included
- File is read-only reference — not an independent specification

**Validation:**
- Manual check: `rules/tier-classification.md` exists and content matches §5.3 + Appendix sections
- Evidence: linkable artifact produced (content match verification)

**Dependencies:** T02.10
**Rollback:** `rm src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md`
**Notes:** None

---

### T02.13 — Extract `rules/file-emission-rules.md` from SKILL.md §3.3

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | Extracted reference file enables human review of file emission naming conventions and content boundaries |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0017/spec.md`

**Deliverables:**
- `src/superclaude/skills/sc-tasklist-protocol/rules/file-emission-rules.md` extracted from §3.3

**Steps:**
1. **[PLANNING]** Identify §3.3 File Emission Rules content in SKILL.md for extraction
2. **[PLANNING]** Confirm `rules/` directory exists (from T01.01)
3. **[EXECUTION]** Write `rules/file-emission-rules.md` with naming conventions, phase heading format, content boundaries, target directory layout from §3.3
4. **[VERIFICATION]** Verify extracted content matches SKILL.md §3.3 (FR-010)
5. **[COMPLETION]** Record extraction evidence

**Acceptance Criteria:**
- File `rules/file-emission-rules.md` exists in `src/superclaude/skills/sc-tasklist-protocol/rules/`
- Content matches §3.3: naming conventions (`phase-N-tasklist.md`), heading format (`# Phase N — <Name>`), content boundaries
- Target directory layout included
- File is read-only reference — not an independent specification

**Validation:**
- Manual check: `rules/file-emission-rules.md` exists and content matches §3.3
- Evidence: linkable artifact produced (content match verification)

**Dependencies:** T02.10
**Rollback:** `rm src/superclaude/skills/sc-tasklist-protocol/rules/file-emission-rules.md`
**Notes:** None

---

### T02.14 — Extract `templates/index-template.md` from SKILL.md §6A

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Extracted template enables human review of the complete tasklist-index.md structure |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0018/spec.md`

**Deliverables:**
- `src/superclaude/skills/sc-tasklist-protocol/templates/index-template.md` extracted from §6A

**Steps:**
1. **[PLANNING]** Identify §6A index file template content in SKILL.md
2. **[PLANNING]** Confirm `templates/` directory exists (from T01.01)
3. **[EXECUTION]** Write `templates/index-template.md` with complete tasklist-index.md template including all §6A sections
4. **[VERIFICATION]** Verify template contains all §6A sections: Title, Metadata, Phase Files, Source Snapshot, Rules, Registries, Traceability, Templates, Glossary (FR-011)
5. **[COMPLETION]** Record extraction evidence

**Acceptance Criteria:**
- File `templates/index-template.md` exists in `src/superclaude/skills/sc-tasklist-protocol/templates/`
- Template contains complete tasklist-index.md structure with all §6A subsections
- Template is self-contained reference for the index file format
- File is read-only reference — not an independent specification

**Validation:**
- Manual check: `templates/index-template.md` exists and contains all §6A section headings
- Evidence: linkable artifact produced (template completeness verification)

**Dependencies:** T02.10
**Rollback:** `rm src/superclaude/skills/sc-tasklist-protocol/templates/index-template.md`
**Notes:** None

---

### Checkpoint: Phase 2 / Tasks T02.10–T02.14

**Purpose:** Verify SKILL.md body and first batch of extracted reference files are complete and faithful to v3.0 source.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-T10-T14.md`

**Verification:**
- SKILL.md body contains all 12 v3.0 sections per §6.2 mapping
- Stage completion reporting contract has all 6 stages with validation criteria
- `rules/tier-classification.md`, `rules/file-emission-rules.md`, and `templates/index-template.md` exist and match source sections

**Exit Criteria:**
- Diff between v3.0 source and SKILL.md shows no algorithmic changes (RISK-001)
- All extracted files are read-only references with content matching their source sections
- Pre-write quality gate criteria defined in SKILL.md (RISK-008)

---

### T02.15 — Extract `templates/phase-template.md` from SKILL.md §6B

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | Extracted template enables human review of the phase-N-tasklist.md structure including task format and checkpoints |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0019/spec.md`

**Deliverables:**
- `src/superclaude/skills/sc-tasklist-protocol/templates/phase-template.md` extracted from §6B

**Steps:**
1. **[PLANNING]** Identify §6B phase file template content in SKILL.md
2. **[PLANNING]** Confirm `templates/` directory exists (from T01.01)
3. **[EXECUTION]** Write `templates/phase-template.md` with complete phase-N-tasklist.md template including task format, checkpoints, near-field completion criteria
4. **[VERIFICATION]** Verify template contains all §6B sections: Phase heading, Task format, Inline checkpoints, End-of-phase checkpoint (FR-012)
5. **[COMPLETION]** Record extraction evidence

**Acceptance Criteria:**
- File `templates/phase-template.md` exists in `src/superclaude/skills/sc-tasklist-protocol/templates/`
- Template contains complete task format with all metadata fields from §6B.2
- Near-field completion criterion rules included (accepted and rejected forms)
- Checkpoint format and end-of-phase checkpoint rules included

**Validation:**
- Manual check: `templates/phase-template.md` exists and contains §6B task format and checkpoint sections
- Evidence: linkable artifact produced (template completeness verification)

**Dependencies:** T02.10
**Rollback:** `rm src/superclaude/skills/sc-tasklist-protocol/templates/phase-template.md`
**Notes:** None

---

### T02.16 — Document Tool Usage and MCP Usage sections in SKILL.md per §6.4 and §6.5

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | The SKILL.md must declare which tools and MCP servers are used at each generation phase for runtime environment validation |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0020/spec.md`

**Deliverables:**
- Tool Usage section mapping Read/Grep/Write/TodoWrite/Bash/Glob to generation phases; MCP Usage section for sequential and context7

**Steps:**
1. **[PLANNING]** Read §6.4 Tool Usage and §6.5 MCP Usage specifications
2. **[PLANNING]** Map tools to phases: Read (Input), Grep (Parsing), Write (Output), TodoWrite (Throughout), Bash (Output), Glob (Validation)
3. **[EXECUTION]** Add `## Tool Usage` section to SKILL.md with tool-to-phase mapping table (FR-060)
4. **[EXECUTION]** Add `## MCP Usage` section specifying sequential for tier classification (FR-058) and context7 for pattern validation (FR-059)
5. **[VERIFICATION]** Verify both sections present with correct tool and MCP server mappings
6. **[COMPLETION]** Record tool/MCP documentation evidence

**Acceptance Criteria:**
- `## Tool Usage` section present with table mapping 6 tools to generation phases (FR-060)
- `## MCP Usage` section present specifying sequential for tier classification and context7 for pattern validation
- Tool mappings match §6.4 specification exactly
- MCP usage matches §6.5 specification exactly

**Validation:**
- Manual check: SKILL.md contains `## Tool Usage` and `## MCP Usage` sections with correct content
- Evidence: linkable artifact produced (tool/MCP section verification)

**Dependencies:** T02.10
**Rollback:** Remove Tool Usage and MCP Usage sections from SKILL.md
**Notes:** RISK-006 mitigation: MCP documented as optional for tier classification; core generation works without MCP

---

### Checkpoint: End of Phase 2

**Purpose:** Verify complete command file and skill file with all extracted references are ready for integration testing.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-END.md`

**Verification:**
- `tasklist.md` is complete with all 8 sections, frontmatter, and line count within limits
- `SKILL.md` body contains full v3.0 algorithm with stage reporting contract
- All 4 extracted reference files exist: `rules/tier-classification.md`, `rules/file-emission-rules.md`, `templates/index-template.md`, `templates/phase-template.md`

**Exit Criteria:**
- T02.01 through T02.16 all completed
- Diff confirms no algorithm drift between v3.0 source and SKILL.md body (RISK-001)
- Pre-write quality gate criteria defined (RISK-008)
