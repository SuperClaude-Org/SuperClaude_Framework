# TASKLIST — sc:roadmap v2 — Phase 1: Architecture Foundation

**Parent Tasklist**: `tasklist-overview.md`
**Phase**: 1 of 7
**Task Range**: T01.01–T01.06
**Priority Wave**: P0
**Dependencies**: None (first milestone)
**Tier Distribution**: STRICT: 0, STANDARD: 5, LIGHT: 1, EXEMPT: 0

---

## Phase 1: Architecture Foundation

Establish the SKILL.md split pattern, refs/ directory structure, and on-demand ref loading protocol that all subsequent milestones depend on. This phase creates the lean behavioral SKILL.md (~400 lines) and populates the refs/ directory with 4 algorithm reference documents. All downstream pipeline work (extraction, generation, validation, adversarial) depends on these foundational artifacts.

---

### T01.01 — Create lean SKILL.md with wave orchestration instructions

**Roadmap Item ID(s):** R-001
**Why:** The SKILL.md split pattern separates behavioral instructions from algorithmic detail, preventing Claude from losing track of high-level intent in a monolithic file.
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
**Deliverable IDs:** D-0001
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0001/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0001/evidence.md`

**Deliverables:**
- Lean SKILL.md file (~400 lines, ≤500 hard limit) containing wave orchestration instructions, purpose/identity, flags, wave architecture, adversarial modes, output artifacts, MCP integration, boundaries, and compliance sections
- refs/ directory structure created with placeholder files

**Steps:**
1. **[PLANNING]** Load SC-ROADMAP-V2-SPEC.md Section 3.4 (SKILL.md Content Outline) and identify all 9 required sections
2. **[PLANNING]** Check existing sc-roadmap skill directory structure; confirm no conflicts with current SKILL.md
3. **[EXECUTION]** Author SKILL.md Purpose &amp; Identity section (~30 lines) defining sc:roadmap's role and pipeline position
4. **[EXECUTION]** Author Flags &amp; Options section (~40 lines) with all flags from spec Section 6.2
5. **[EXECUTION]** Author Wave Architecture section (~150 lines) with behavioral descriptions for Waves 0-4, referencing refs/ files by name (not inlining algorithms)
6. **[EXECUTION]** Author remaining sections: Adversarial Modes (~50 lines), Output Artifacts (~40 lines), MCP Integration (~20 lines), Boundaries (~30 lines), Compliance (~20 lines)
7. **[VERIFICATION]** Validate SKILL.md is ≤500 lines, contains no YAML pseudocode blocks, and references each of the 5 ref files by name
8. **[COMPLETION]** Document line count, section breakdown, and ref file references in evidence artifact

**Acceptance Criteria:**
- SKILL.md is ≤500 lines and contains all 9 sections defined in spec Section 3.4
- No YAML pseudocode, scoring formulas, domain keyword dictionaries, agent prompt templates, or template discovery paths appear in SKILL.md
- Each of the 5 refs/ files is referenced by exact filename at least once in SKILL.md
- refs/ directory exists with correctly named placeholder files

**Validation:**
- Manual check: Line count ≤500, grep for YAML code blocks (should find none), grep for each ref filename (should find at least 1 match each)
- Evidence: linkable artifact produced (spec.md documenting structure and compliance)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Per spec Section 3.2, SKILL.md contains ONLY intent, flow, behavioral guidance, and decision boundaries. Per spec risk R-001, explicit name references mitigate Claude missing ref files.

---

### T01.02 — Create refs/extraction-pipeline.md reference document

**Roadmap Item ID(s):** R-002
**Why:** The extraction pipeline reference contains the 8-step extraction algorithm, domain keyword dictionaries, chunked extraction protocol, and 4-pass verification that Wave 1B depends on.
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
**Deliverable IDs:** D-0002
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0002/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0002/evidence.md`

**Deliverables:**
- refs/extraction-pipeline.md containing 8-step extraction pipeline, domain keyword dictionaries, ID assignment rules, chunked extraction protocol (FR-016), and 4-pass completeness verification

**Steps:**
1. **[PLANNING]** Load spec Sections 9.1 (extraction-pipeline.md spec), FR-016 (chunked extraction), and FR-006 Wave 1B description
2. **[PLANNING]** Identify all required subsections: 8-step pipeline, domain keywords, ID rules, chunked protocol, verification
3. **[EXECUTION]** Author 8-step extraction pipeline (title → FRs → NFRs → scope → deps → success criteria → risks → ID assignment)
4. **[EXECUTION]** Author domain keyword dictionaries for 5 domains (frontend, backend, security, performance, documentation) with keyword weighting rules
5. **[EXECUTION]** Author chunked extraction protocol: activation threshold (500 lines), section indexing, chunk assembly (~400 lines target, 600 max), per-chunk extraction template, merge algorithm, deduplication rules, cross-reference resolution, global ID assignment
6. **[EXECUTION]** Author 4-pass completeness verification: source coverage, anti-hallucination, section coverage, count reconciliation with thresholds
7. **[VERIFICATION]** Validate all spec-required components are present; verify chunked protocol matches FR-016 algorithm overview
8. **[COMPLETION]** Document section inventory and cross-reference to spec requirements

**Acceptance Criteria:**
- Contains complete 8-step extraction pipeline with all steps from spec
- Domain keyword dictionaries cover all 5 domains listed in spec Section 9.1
- Chunked extraction protocol includes all 7 algorithm steps from FR-016 plus worked example
- 4-pass verification includes exact thresholds: 100% source coverage, zero-tolerance anti-hallucination, 100% section coverage, exact count reconciliation

**Validation:**
- Manual check: Verify all 8 extraction steps present, all 5 domain dictionaries present, chunked protocol has 7 steps + worked example, 4-pass thresholds match spec
- Evidence: linkable artifact produced (spec.md documenting completeness)

**Dependencies:** T01.01 (refs/ directory must exist)
**Rollback:** TBD
**Notes:** This is the most content-dense ref file. Per spec Section 9.1, it must include a worked example with a 1500-line spec for the chunked extraction protocol.

---

### T01.03 — Create refs/scoring.md reference document

**Roadmap Item ID(s):** R-003
**Why:** The scoring reference defines the complexity scoring formula, classification thresholds, template compatibility scoring, and persona confidence calculation used in Wave 1B and Wave 2.
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
**Deliverable IDs:** D-0003
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0003/spec.md`

**Deliverables:**
- refs/scoring.md containing 5-factor complexity scoring formula with weights, classification thresholds, template compatibility scoring algorithm, and persona confidence calculation

**Steps:**
1. **[PLANNING]** Load spec Section 9.2 (scoring.md spec) to identify all required formulas and tables
2. **[PLANNING]** Confirm factor weights (0.25, 0.25, 0.20, 0.15, 0.15) and thresholds (LOW &lt; 0.4, MEDIUM 0.4-0.7, HIGH &gt; 0.7)
3. **[EXECUTION]** Author 5-factor complexity scoring formula with factor definitions, normalization rules, and weight table
4. **[EXECUTION]** Author classification thresholds and complexity class determination logic
5. **[EXECUTION]** Author template compatibility scoring algorithm per FR-020: 4-factor weighted formula (domain_match 0.40, complexity_alignment 0.30, type_match 0.20, version_compatibility 0.10) with ≥0.6 threshold
6. **[EXECUTION]** Author persona confidence calculation formula
7. **[VERIFICATION]** Validate all formulas produce deterministic outputs for given inputs; verify weight table sums to 1.0
8. **[COMPLETION]** Document formula inventory and verification results

**Acceptance Criteria:**
- 5-factor formula includes requirement_count, dependency_depth, domain_spread, risk_severity, scope_size with correct weights
- Classification thresholds match spec exactly: LOW &lt; 0.4, MEDIUM 0.4-0.7, HIGH &gt; 0.7
- Template compatibility scoring implements FR-020 4-factor formula (domain_match 0.40 + complexity_alignment 0.30 + type_match 0.20 + version_compatibility 0.10) with ≥0.6 selection threshold
- Persona confidence calculation produces values in [0, 1] range

**Validation:**
- Manual check: Weight table sums to 1.0; thresholds match spec Section 9.2
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.01 (refs/ directory must exist)
**Rollback:** TBD
**Notes:** None.

---

### T01.04 — Create refs/templates.md reference document

**Roadmap Item ID(s):** R-004
**Why:** The templates reference defines the 4-tier discovery search paths, version resolution, milestone count selection by complexity, and inline generation fallback used in Wave 2.
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
**Deliverable IDs:** D-0004
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0004/spec.md`

**Deliverables:**
- refs/templates.md containing 4-tier template discovery search paths, version resolution rules, matching criteria, inline generation fallback, milestone count selection, domain-specific milestone mapping, and required sections per milestone

**Steps:**
1. **[PLANNING]** Load spec Section 9.4 (templates.md spec) to identify all required components
2. **[PLANNING]** Confirm 4-tier search order: local → user → plugin [future: v5.0] → inline generation
3. **[EXECUTION]** Author 4-tier template discovery search paths with directory patterns for each tier
4. **[EXECUTION]** Author version resolution rules, matching criteria, and compatibility scoring integration
5. **[EXECUTION]** Author inline template generation fallback algorithm (used when tiers 1-3 produce no match)
6. **[EXECUTION]** Author milestone count selection by complexity class and domain-specific milestone mapping
7. **[VERIFICATION]** Validate 4-tier discovery is deterministic; verify plugin tier is annotated as [future: v5.0]
8. **[COMPLETION]** Document component inventory

**Acceptance Criteria:**
- 4-tier discovery search paths defined in correct order with directory patterns
- Plugin tier annotated as [future: v5.0 plugin marketplace] per spec
- Inline generation fallback provides complete milestone structure when no template matches
- Milestone count selection maps each complexity class to a milestone count range

**Validation:**
- Manual check: 4 tiers present in correct order; plugin tier marked as future; inline fallback complete
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.01 (refs/ directory must exist)
**Rollback:** TBD
**Notes:** None.

---

### T01.05 — Create refs/validation.md reference document

**Roadmap Item ID(s):** R-005
**Why:** The validation reference defines agent prompts for quality-engineer and self-review agents, score aggregation formula, and decision thresholds used in Wave 4.
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
**Deliverable IDs:** D-0005
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0005/spec.md`

**Deliverables:**
- refs/validation.md containing quality-engineer agent prompt, self-review agent prompt (4-question protocol), score aggregation formula, and PASS/REVISE/REJECT decision thresholds

**Steps:**
1. **[PLANNING]** Load spec Section 9.3 (validation.md spec) and FR-006 Wave 4 description to identify all required components
2. **[PLANNING]** Confirm thresholds: PASS ≥85%, REVISE 70-84%, REJECT &lt;70%, and REVISE loop max 2 iterations
3. **[EXECUTION]** Author quality-engineer agent prompt with completeness, consistency, and traceability check instructions
4. **[EXECUTION]** Author self-review agent prompt with 4-question validation protocol
5. **[EXECUTION]** Author score aggregation formula with defined weights for each validation dimension
6. **[EXECUTION]** Author REVISE loop behavior specification (max 2 iterations, PASS_WITH_WARNINGS fallback)
7. **[VERIFICATION]** Validate thresholds match spec exactly; verify both agent prompts are complete and actionable
8. **[COMPLETION]** Document prompt inventory and threshold verification

**Acceptance Criteria:**
- quality-engineer prompt includes completeness, consistency, and traceability checks as specified in spec
- self-review prompt includes exactly 4 questions per the validation protocol
- Score aggregation produces PASS (≥85%), REVISE (70-84%), REJECT (&lt;70%) deterministically
- REVISE loop capped at 2 iterations with PASS_WITH_WARNINGS fallback documented

**Validation:**
- Manual check: Both agent prompts present; thresholds match ≥85%/70-84%/&lt;70%; REVISE loop documented with max 2 iterations
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.01 (refs/ directory must exist)
**Rollback:** TBD
**Notes:** None.

---

### T01.06 — Create minimal roadmap.md command file for integration testing

**Roadmap Item ID(s):** R-038
**Why:** The command file (`src/superclaude/commands/roadmap.md`) is the entry point users invoke; without a minimal version in Phase 1, the SKILL.md and refs/ cannot be integration-tested through the actual command activation path.
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
**Deliverable IDs:** D-0038
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0038/spec.md`

**Deliverables:**
- Minimal roadmap.md command file (~40 lines) with basic triggers, usage line, SKILL.md activation, and placeholder flag table. Phase 6 (T06.01) expands this to full documentation.

**Steps:**
1. **[PLANNING]** Load spec Section 3.5 (command file vs SKILL.md relationship) for sizing and content guidelines
2. **[PLANNING]** Identify minimum viable content: trigger description, usage syntax, SKILL.md reference
3. **[EXECUTION]** Create `src/superclaude/commands/roadmap.md` with trigger description ("When user requests roadmap generation from a spec file")
4. **[EXECUTION]** Add basic usage line and SKILL.md activation reference
5. **[EXECUTION]** Add placeholder flag table with core flags (--depth, --template, --output) — full flags deferred to T06.01
6. **[VERIFICATION]** Verify file is ≤50 lines and correctly references SKILL.md
7. **[COMPLETION]** Document command file structure

**Acceptance Criteria:**
- Command file exists at `src/superclaude/commands/roadmap.md`
- Contains trigger description, usage syntax, and SKILL.md activation
- File is ≤50 lines (minimal — T06.01 expands to ~80 lines with all flags)
- Correctly references the sc-roadmap SKILL.md for behavioral delegation

**Validation:**
- Manual check: Verify file exists, ≤50 lines, references SKILL.md
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.01 (SKILL.md must exist to reference)
**Rollback:** TBD
**Notes:** Per spec-panel finding M3, the command file is the user's entry point. Without it in Phase 1, integration testing of the SKILL.md activation path is blocked until Phase 6. This minimal version unblocks testing; T06.01 provides the complete version.

---

### Checkpoint: Phase 1 / Tasks 01-06

**Purpose:** Validate that all architectural foundation artifacts are created and internally consistent before proceeding to implementation phases.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P01-T01-T06.md`
**Verification:**
- All 5 refs/ files exist and are non-empty with correct filenames
- SKILL.md is ≤500 lines and references each ref file by name
- No algorithmic content (formulas, dictionaries, prompts) appears in SKILL.md
- Minimal command file exists and references SKILL.md

**Exit Criteria:**
- SKILL.md + 4 refs/ files + minimal command file pass structural completeness check
- On-demand ref loading protocol is documented in SKILL.md wave descriptions
- All spec Section 9 requirements are traceable to content in refs/ files

---

### Checkpoint: End of Phase 1

**Purpose:** Final gate before extraction pipeline implementation begins; confirms architectural foundation is complete and ready for downstream consumption.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P01-END.md`
**Verification:**
- refs/ directory contains exactly 5 files: extraction-pipeline.md, scoring.md, templates.md, validation.md, adversarial-integration.md (placeholder for Phase 4)
- SKILL.md wave descriptions correctly specify which refs to load at each wave per spec Section 3.3
- No content duplication between SKILL.md and any refs/ file
- Minimal command file enables integration testing of SKILL.md activation

**Exit Criteria:**
- All 6 tasks (T01.01-T01.06) marked complete with evidence artifacts
- Architecture matches spec Section 3.2 file structure exactly
- Phase 2 dependency (refs/extraction-pipeline.md and refs/scoring.md) confirmed available
- Command file activation path testable end-to-end

---

**End of Phase 1** | Tasks: 6 | Deliverables: 6 (D-0001–D-0005, D-0038) | Tier Distribution: STRICT: 0, STANDARD: 5, LIGHT: 1, EXEMPT: 0
