# TASKLIST — sc:roadmap v2 — Phase 2: Extraction Pipeline

**Parent Tasklist**: `tasklist-overview.md`
**Phase**: 2 of 7
**Task Range**: T02.01–T02.06
**Priority Wave**: P0
**Dependencies**: Phase 1 (M1: refs/extraction-pipeline.md and refs/scoring.md must exist)
**Tier Distribution**: STRICT: 0, STANDARD: 6, LIGHT: 0, EXEMPT: 0

---

## Phase 2: Extraction Pipeline

Implement Wave 0 (prerequisite validation) and Wave 1B (detection, analysis, extraction.md generation) including the chunked extraction protocol for large specs. This phase makes the sc:roadmap command capable of parsing any specification file and producing a complete extraction.md artifact with requirements, domain classification, and complexity scoring.

---

### T02.01 — Implement Wave 0 spec file validation and collision detection

**Roadmap Item ID(s):** R-006
**Why:** Wave 0 prerequisites must validate inputs and detect output collisions before any pipeline work begins, preventing wasted computation and data loss from overwrites.
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
**Deliverable IDs:** D-0006
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0006/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0006/evidence.md`

**Deliverables:**
- Wave 0 validation logic in SKILL.md: spec file exists/readable check, output directory creation, collision detection with -N suffix protocol, template directory availability check, adversarial skill availability check (when --specs or --multi-roadmap flags present), compliance tier auto-detection per FR-019 (security keywords → STRICT, >500 lines → STRICT, <100 lines with <5 requirements → LIGHT, default → STANDARD)

**Steps:**
1. **[PLANNING]** Load spec FR-006 Wave 0 description and identify all validation checks required
2. **[PLANNING]** Confirm collision protocol: existing artifacts → append -2, if -2 exists → -3, etc.
3. **[EXECUTION]** Implement spec file validation: file exists, file readable, file non-empty
4. **[EXECUTION]** Implement output directory creation with collision detection (-N suffix protocol)
5. **[EXECUTION]** Implement template directory availability check (4-tier: local → user → plugin → inline)
6. **[EXECUTION]** Implement sc:adversarial availability check when --specs or --multi-roadmap flags present
7. **[EXECUTION]** Implement compliance tier auto-detection per FR-019: scan spec for security keywords → STRICT; check line count >500 → STRICT; <100 lines with <5 extractable requirements → LIGHT; --compliance flag overrides auto-detection
8. **[VERIFICATION]** Test collision detection: verify -2, -3 suffix generation; verify abort on missing spec file; verify compliance tier auto-detection for each threshold
8. **[COMPLETION]** Document validation check inventory and test results

**Acceptance Criteria:**
- Validates spec file exists, is readable, and is non-empty before proceeding
- Output collision detection appends -N suffix (not overwrite) when artifacts exist
- sc:adversarial availability check triggers only when --specs or --multi-roadmap flags are present
- Compliance tier auto-detected per FR-019 algorithm and logged in Wave 0 output (overridable via --compliance flag)
- Progress message emitted: "Wave 0 complete: prerequisites validated."

**Validation:**
- Manual check: Verify collision detection produces correct -N suffix; verify abort on missing file; verify progress message format
- Evidence: linkable artifact produced (evidence.md with test scenarios)

**Dependencies:** T01.01 (SKILL.md must exist for Wave 0 definition)
**Rollback:** TBD
**Notes:** Per FR-006, collision check applies to roadmap.md, extraction.md, and test-strategy.md simultaneously.

---

### T02.02 — Implement Wave 0 model identifier validation

**Roadmap Item ID(s):** R-007
**Why:** Invalid model identifiers in --agents must be caught at Wave 0 to prevent late failures during adversarial generation in Wave 2.
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
**Deliverable IDs:** D-0007
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0007/spec.md`

**Deliverables:**
- Model identifier validation logic: validates all model names in --agents flag, aborts with error listing unrecognized models and available alternatives

**Steps:**
1. **[PLANNING]** Load spec FR-006 Wave 0 model validation and FR-004 agent spec format sections
2. **[PLANNING]** Identify known model identifiers from spec: opus, sonnet, haiku, gpt52, gemini
3. **[EXECUTION]** Implement model identifier extraction from --agents flag (split on comma, then split each on colon, first segment = model)
4. **[EXECUTION]** Implement validation against known model list with error message: "Unknown model '&lt;model&gt;' in --agents. Available models: opus, sonnet, haiku, gpt52, gemini, ..."
5. **[VERIFICATION]** Test with valid models, invalid models, and mixed valid/invalid lists
6. **[COMPLETION]** Document model list and validation behavior

**Acceptance Criteria:**
- All model identifiers in --agents are validated before pipeline starts
- Unrecognized models trigger abort with clear error message listing available models
- Validation only triggers when --multi-roadmap flag is present
- Multiple unrecognized models are all listed in the error message

**Validation:**
- Manual check: Verify error message format matches spec; verify valid models pass; verify abort behavior
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T02.01 (Wave 0 validation framework must exist)
**Rollback:** TBD
**Notes:** Per spec risk R-009, early validation prevents late failures during adversarial generation.

---

### T02.03 — Implement Wave 1B 8-step extraction pipeline

**Roadmap Item ID(s):** R-008
**Why:** The 8-step extraction pipeline is the core of Wave 1B, producing the structured extraction.md artifact that all subsequent generation depends on.
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
**Deliverable IDs:** D-0008
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0008/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0008/evidence.md`

**Deliverables:**
- Wave 1B extraction pipeline implementation in SKILL.md behavioral instructions that references refs/extraction-pipeline.md for algorithmic details
- extraction.md output written to output directory upon Wave 1B completion

**Steps:**
1. **[PLANNING]** Load refs/extraction-pipeline.md (on-demand per ref loading protocol) for the 8-step algorithm
2. **[PLANNING]** Confirm 8 steps: title extraction → FR extraction → NFR extraction → scope analysis → dependency identification → success criteria extraction → risk identification → ID assignment
3. **[EXECUTION]** Implement SKILL.md Wave 1B behavioral instructions that trigger each extraction step
4. **[EXECUTION]** Implement extraction.md generation using the body template from spec Section 8.2
5. **[EXECUTION]** Implement extraction.md frontmatter generation per spec FR-002 extraction.md schema
6. **[EXECUTION]** Implement early write of extraction.md to output directory (per FR-006: "writing early enables resumability and provides immediate user value")
7. **[VERIFICATION]** Validate extraction.md contains all 9 sections: FRs, NFRs, Domain Distribution, Complexity Analysis, Persona Assignment, Dependencies, Risks, Success Criteria, Warnings
8. **[COMPLETION]** Document extraction pipeline flow and output validation

**Acceptance Criteria:**
- Produces complete extraction.md with all 9 structured sections from spec Section 8.2
- extraction.md is written to disk at end of Wave 1B (not deferred to Wave 3)
- YAML frontmatter includes all fields from spec FR-002 extraction.md schema
- Progress message emitted: "Wave 1B complete: extraction finished (XX requirements, complexity: X.XX). extraction.md written."

**Validation:**
- Manual check: Verify 9 sections present in extraction.md; verify frontmatter fields match spec; verify early write behavior
- Evidence: linkable artifact produced (evidence.md with extraction output sample)

**Dependencies:** T01.01 (SKILL.md), T01.02 (refs/extraction-pipeline.md)
**Rollback:** TBD
**Notes:** Per spec FR-006 Wave 1B, extraction.md is written early for resumability. The SKILL.md contains behavioral instructions; refs/extraction-pipeline.md contains the algorithm.

---

### T02.04 — Implement Wave 1B domain classification with keyword weighting

**Roadmap Item ID(s):** R-009
**Why:** Domain classification determines primary persona assignment and consulting persona selection, which influences template selection and downstream generation quality.
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
**Deliverable IDs:** D-0009
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0009/spec.md`

**Deliverables:**
- Domain classification logic that produces correct domain percentages and primary persona assignment with confidence score, using keyword dictionaries from refs/extraction-pipeline.md

**Steps:**
1. **[PLANNING]** Load domain keyword dictionaries from refs/extraction-pipeline.md
2. **[PLANNING]** Confirm 5 target domains: frontend, backend, security, performance, documentation
3. **[EXECUTION]** Implement keyword scanning across extracted requirements with weighting rules
4. **[EXECUTION]** Implement domain percentage calculation and primary persona assignment based on highest domain percentage
5. **[EXECUTION]** Implement --persona flag override for auto-detected primary persona (per spec FR-006 Wave 1B)
6. **[VERIFICATION]** Validate domain percentages sum to 100%; verify persona confidence score is in [0, 1] range
7. **[COMPLETION]** Document classification algorithm and test results

**Acceptance Criteria:**
- Domain percentages are computed for all 5 domains and sum to 100%
- Primary persona assigned based on highest domain percentage with confidence score
- --persona flag override propagates correctly when provided
- Domain Distribution section populated in extraction.md

**Validation:**
- Manual check: Verify domain percentages sum to 100%; verify persona assignment matches highest domain; verify --persona override works
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T02.03 (extraction pipeline must produce requirements for classification)
**Rollback:** TBD
**Notes:** None.

---

### T02.05 — Implement Wave 1B complexity scoring

**Roadmap Item ID(s):** R-010
**Why:** Complexity scoring determines the complexity class (LOW/MEDIUM/HIGH) which drives template selection, milestone count, and interleave ratio for test-strategy.md.
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
**Deliverable IDs:** D-0010
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0010/spec.md`

**Deliverables:**
- Complexity scoring implementation using the 5-factor weighted formula from refs/scoring.md, producing a score in [0, 1] and classification (LOW/MEDIUM/HIGH)

**Steps:**
1. **[PLANNING]** Load refs/scoring.md (on-demand per ref loading protocol) for the 5-factor formula
2. **[PLANNING]** Confirm factors and weights: requirement_count (0.25), dependency_depth (0.25), domain_spread (0.20), risk_severity (0.15), scope_size (0.15)
3. **[EXECUTION]** Implement raw value extraction from extraction results for each of the 5 factors
4. **[EXECUTION]** Implement normalization, weighting, and aggregation to produce complexity_score
5. **[EXECUTION]** Implement classification: LOW (&lt; 0.4), MEDIUM (0.4-0.7), HIGH (&gt; 0.7)
6. **[VERIFICATION]** Validate weights sum to 1.0; verify score is in [0, 1]; verify classification thresholds match spec
7. **[COMPLETION]** Document scoring results and classification

**Acceptance Criteria:**
- Score computable from extraction results using 5-factor formula with correct weights
- Classification thresholds applied correctly: LOW &lt; 0.4, MEDIUM 0.4-0.7, HIGH &gt; 0.7
- Complexity Analysis section populated in extraction.md with per-factor breakdown
- complexity_score and complexity_class populated in extraction.md frontmatter

**Validation:**
- Manual check: Verify weight sum = 1.0; verify classification matches threshold ranges; verify frontmatter fields populated
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T02.03 (extraction pipeline must produce data for scoring), T01.03 (refs/scoring.md must exist)
**Rollback:** TBD
**Notes:** None.

---

### Checkpoint: Phase 2 / Tasks 01-05

**Purpose:** Validate Wave 0 prerequisites and Wave 1B core extraction are functional before proceeding to chunked extraction.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P02-T01-T05.md`
**Verification:**
- Wave 0 validation catches missing/unreadable spec files and produces collision suffixes correctly
- 8-step extraction pipeline produces complete extraction.md with valid frontmatter
- Domain classification and complexity scoring produce consistent, deterministic results

**Exit Criteria:**
- All 5 tasks (T02.01-T02.05) produce evidence artifacts
- extraction.md passes YAML frontmatter parse test
- Complexity score produces correct classification for a known test input

---

### T02.06 — Implement Wave 1B chunked extraction for large specs

**Roadmap Item ID(s):** R-011
**Why:** Specs exceeding 500 lines overwhelm context; chunked extraction processes large specs in multiple passes with completeness verification to prevent data loss.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [██████░░░░] 60%
**Requires Confirmation:** Yes
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0011
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0011/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0011/evidence.md`

**Deliverables:**
- Chunked extraction protocol implementation: section indexing, chunk assembly (~400 lines target, 600 max), per-chunk extraction, merge, deduplication, cross-reference resolution, global ID assignment, 4-pass verification

**Steps:**
1. **[PLANNING]** Load chunked extraction protocol from refs/extraction-pipeline.md
2. **[PLANNING]** Confirm activation threshold (500 lines), chunk size (400 target, 600 max), and verification pass thresholds
3. **[EXECUTION]** Implement section indexing: scan H1-H3 headings to build structural map with line ranges and extraction-relevance tags
4. **[EXECUTION]** Implement chunk assembly: group sections into ~400-line chunks, prepend title/overview as context header, handle oversized sections at paragraph boundaries
5. **[EXECUTION]** Implement per-chunk extraction with global ID counters, merge algorithm, and deduplication (ID collision, normalized description match, substring match)
6. **[EXECUTION]** Implement 4-pass completeness verification: source coverage (100%/95%), anti-hallucination (zero tolerance), section coverage (100%), count reconciliation (exact)
7. **[VERIFICATION]** Test with spec exceeding 500 lines; verify extraction_mode metadata in output; verify 4-pass verification passes
8. **[COMPLETION]** Document chunk metrics and verification results

**Acceptance Criteria:**
- Activates automatically for specs &gt;500 lines; standard single-pass used for shorter specs
- Produces extraction.md in identical format to single-pass extraction plus extraction_mode metadata
- 4-pass verification runs with correct thresholds: 100% source coverage, zero-tolerance anti-hallucination, 100% section coverage, exact count reconciliation
- On verification failure: re-processes failing chunks (max 1 retry), then stops with error (no partial extraction)

**Validation:**
- Manual check: Verify activation threshold; verify output format matches single-pass; verify 4-pass verification runs with correct thresholds
- Evidence: linkable artifact produced (evidence.md with chunk metrics and verification results)

**Dependencies:** T02.03 (single-pass extraction must work first), T01.02 (refs/extraction-pipeline.md chunked protocol)
**Rollback:** TBD
**Notes:** Per spec risk R-007, chunked extraction with 4-pass verification mitigates large spec context overflow. Per FR-016, max 1 retry on verification failure, then hard stop.

---

### Checkpoint: End of Phase 2

**Purpose:** Final gate before core generation pipeline; confirms extraction pipeline handles both standard and large specs correctly.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P02-END.md`
**Verification:**
- Wave 0 + Wave 1B produce correct extraction.md for a standard-size spec
- Chunked extraction activates for specs &gt;500 lines and produces identical output format
- All frontmatter fields in extraction.md are valid YAML

**Exit Criteria:**
- All 6 tasks (T02.01-T02.06) marked complete with evidence artifacts
- extraction.md and complexity score available for Phase 3 consumption
- No known extraction failures for specs within supported size range

---

**End of Phase 2** | Tasks: 6 | Deliverables: 6 (D-0006–D-0011) | Tier Distribution: STRICT: 0, STANDARD: 6, LIGHT: 0, EXEMPT: 0
