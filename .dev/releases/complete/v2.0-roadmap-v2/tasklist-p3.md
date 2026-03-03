# TASKLIST — sc:roadmap v2 — Phase 3: Core Generation Pipeline

**Parent Tasklist**: `tasklist-overview.md`
**Phase**: 3 of 7
**Task Range**: T03.01–T03.06
**Priority Wave**: P1
**Dependencies**: Phase 2 (M2: extraction.md and complexity score must be available)
**Tier Distribution**: STRICT: 1, STANDARD: 5, LIGHT: 0, EXEMPT: 0

---

## Phase 3: Core Generation Pipeline

Implement Wave 2 (template selection, milestone planning, dependency mapping) and Wave 3 (roadmap.md + test-strategy.md generation). This phase produces the two primary output artifacts: the milestone-based roadmap.md with YAML frontmatter and the continuous parallel validation test-strategy.md. Sequencing constraint: roadmap.md must be fully generated before test-strategy.md begins.

---

### T03.01 — Implement Wave 2 template discovery with 4-tier search

**Roadmap Item ID(s):** R-012
**Why:** Template discovery finds the best-fit milestone template through a 4-tier search, falling back to inline generation when no external template matches.
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
**Deliverable IDs:** D-0012
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0012/spec.md`

**Deliverables:**
- Wave 2 template discovery implementation with 4-tier search (local → user → plugin [future] → inline generation) and compatibility scoring from refs/templates.md

**Steps:**
1. **[PLANNING]** Load refs/templates.md (on-demand per ref loading protocol) for search paths and scoring algorithm
2. **[PLANNING]** Confirm 4-tier search order and fallback logic per spec Section 9.4
3. **[EXECUTION]** Implement local template directory scan with FR-020 compatibility scoring (4-factor: domain_match 0.40, complexity_alignment 0.30, type_match 0.20, version_compatibility 0.10; threshold ≥0.6)
4. **[EXECUTION]** Implement user template directory scan with same FR-020 compatibility scoring
5. **[EXECUTION]** Implement plugin tier as annotated stub [future: v5.0 plugin marketplace]
6. **[EXECUTION]** Implement inline generation fallback when tiers 1-3 produce no match
7. **[VERIFICATION]** Validate fallback chain works: no local → no user → skip plugin → inline generation triggers
8. **[COMPLETION]** Document template selection decision and fallback chain

**Acceptance Criteria:**
- Searches local → user → plugin [future] → inline in exact order
- Compatibility scoring per FR-020 (4-factor weighted formula, ≥0.6 threshold) selects best match from available templates
- Inline generation fallback always produces a valid milestone structure
- Template selection recorded in Decision Summary with compatibility scores

**Validation:**
- Manual check: Verify 4-tier search order; verify inline fallback produces complete structure; verify Decision Summary entry
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T01.04 (refs/templates.md must exist)
**Rollback:** TBD
**Notes:** Per roadmap risk assessment, template matching producing poor fit is mitigated by inline generation fallback always being available.

---

### T03.02 — Implement Wave 2 milestone extraction with dependency mapping

**Roadmap Item ID(s):** R-013
**Why:** Milestone extraction creates the structural backbone of roadmap.md by organizing deliverables into milestones with typed dependencies and priority ordering.
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
**Deliverable IDs:** D-0013
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0013/spec.md`

**Deliverables:**
- Milestone structure with IDs (M1, M2, ...), types (FEATURE/IMPROVEMENT/DOC/TEST/MIGRATION/SECURITY), priorities (P0-P3), and dependency graph

**Steps:**
1. **[PLANNING]** Load extraction.md complexity class and domain distribution to determine milestone count
2. **[PLANNING]** Apply milestone count selection from refs/templates.md based on complexity class
3. **[EXECUTION]** Generate milestone IDs, titles, and types based on extracted requirements and domain grouping
4. **[EXECUTION]** Assign priorities (P0-P3) based on dependency ordering and domain criticality
5. **[EXECUTION]** Map inter-milestone dependencies and generate dependency graph representation
6. **[VERIFICATION]** Validate every extracted requirement maps to at least one milestone; verify no circular dependencies
7. **[COMPLETION]** Document milestone structure and dependency graph

**Acceptance Criteria:**
- Milestones have IDs, types, priorities, and a dependency graph
- Milestone count matches complexity class range from refs/templates.md
- Every functional requirement from extraction.md traces to at least one milestone deliverable
- Dependency graph contains no cycles

**Validation:**
- Manual check: Verify milestone count within expected range; verify all FRs mapped; verify no circular deps
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T02.03 (extraction.md must exist), T02.05 (complexity score must be available)
**Rollback:** TBD
**Notes:** None.

---

### T03.03 — Implement Wave 2 effort estimation per milestone

**Roadmap Item ID(s):** R-014
**Why:** Effort estimation provides planning metadata for each milestone, informing the roadmap's risk assessment and the future tasklist generator's effort allocation.
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
**Deliverable IDs:** D-0014
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0014/spec.md`

**Deliverables:**
- Effort estimation for each milestone based on deliverable count, complexity, and risk factors

**Steps:**
1. **[PLANNING]** Review milestone structure from T03.02 to identify estimation inputs
2. **[PLANNING]** Identify estimation factors: deliverable count, domain complexity, dependency depth, risk level
3. **[EXECUTION]** Implement effort estimation algorithm using deliverable count and complexity as primary drivers
4. **[EXECUTION]** Assign risk levels (Low/Medium/High) to each milestone based on associated risks from extraction.md
5. **[VERIFICATION]** Validate every milestone has an estimated effort and risk level
6. **[COMPLETION]** Document estimation methodology and results

**Acceptance Criteria:**
- Each milestone has an estimated effort level and risk level
- Estimation is deterministic: same inputs produce same outputs
- Risk levels derived from risks identified in extraction.md (not invented)
- Effort and risk appear in the Milestone Summary table of roadmap.md

**Validation:**
- Manual check: Verify all milestones have effort and risk; verify consistency with extraction.md risks
- Evidence: linkable artifact produced (spec.md)

**Dependencies:** T03.02 (milestone structure must exist)
**Rollback:** TBD
**Notes:** Per style rules, no story points or timelines are invented; effort is relative (Low/Medium/High).

---

### T03.04 — Implement Wave 3 roadmap.md generation with full body template

**Roadmap Item ID(s):** R-015
**Why:** roadmap.md is the primary output artifact containing the milestone hierarchy, dependency graph, per-milestone details, risk register, and Decision Summary that the future tasklist generator consumes.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [███████░░░] 70%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0015
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0015/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0015/evidence.md`

**Deliverables:**
- roadmap.md generation using body template from spec Section 8.1: Overview, Milestone Summary table, Dependency Graph, per-milestone sections (Objective, Deliverables, Dependencies, Risk Assessment), Risk Register, Decision Summary, Success Criteria

**Steps:**
1. **[PLANNING]** Load spec Section 8.1 (roadmap.md body template) and identify all required sections
2. **[PLANNING]** Gather all inputs: milestone structure (T03.02), effort estimates (T03.03), extraction data (Phase 2)
3. **[EXECUTION]** Generate roadmap.md Overview section (1-3 paragraphs from extraction summary)
4. **[EXECUTION]** Generate Milestone Summary table and Dependency Graph from milestone structure
5. **[EXECUTION]** Generate per-milestone sections: Objective, Deliverables (with IDs and ACs), Dependencies, Risk Assessment
6. **[EXECUTION]** Generate Risk Register and Decision Summary per spec Section 8.1 (every row must cite specific data points)
7. **[VERIFICATION]** Validate all required sections present; verify every milestone has Objective, Deliverables, Dependencies, Risk Assessment
8. **[COMPLETION]** Document section inventory and completeness verification

**Acceptance Criteria:**
- roadmap.md contains all sections from spec Section 8.1 body template
- Every milestone has: objective, deliverables with IDs, dependencies, risk assessment
- Decision Summary records persona selection, template choice, milestone count, adversarial mode with data-driven rationale
- Risk Register maps risks to affected milestones with probability/impact/mitigation

**Validation:**
- Manual check: Verify all 8.1 template sections present; verify Decision Summary has data-driven rationale (not subjective); verify deliverable IDs are unique
- Evidence: linkable artifact produced (evidence.md with section checklist)

**Dependencies:** T03.02 (milestone structure), T03.03 (effort estimates), T02.03 (extraction data)
**Rollback:** TBD
**Notes:** Per spec FR-006 Wave 3, roadmap.md MUST be fully generated before test-strategy.md begins (sequencing constraint).

---

### Checkpoint: Phase 3 / Tasks 01-04

**Purpose:** Validate Wave 2 planning and roadmap.md generation before proceeding to test-strategy.md and frontmatter tasks.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P03-T01-T04.md`
**Verification:**
- Template discovery fallback chain works correctly (inline generation produces valid structure)
- Milestone structure has correct types, priorities, and dependency graph without cycles
- roadmap.md contains all required sections from spec Section 8.1

**Exit Criteria:**
- roadmap.md body is complete and ready for test-strategy.md reference
- All milestone deliverables have unique IDs matching the D#.# pattern
- Decision Summary contains only data-driven rationale (no subjective claims)

---

### T03.05 — Implement Wave 3 test-strategy.md generation

**Roadmap Item ID(s):** R-016
**Why:** test-strategy.md encodes the continuous parallel validation philosophy with interleave ratio computed from complexity and concrete milestone references from roadmap.md.
**Effort:** M
**Risk:** Low
**Risk Drivers:** None matched
**Tier:** STANDARD
**Confidence:** [███████░░░] 70%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | Fallback Allowed: Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0016
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0016/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0016/evidence.md`

**Deliverables:**
- test-strategy.md with: Validation Philosophy, Validation Milestones table (referencing concrete work milestones from roadmap.md), Issue Classification, Acceptance Gates, and YAML frontmatter with interleave_ratio

**Steps:**
1. **[PLANNING]** Load spec FR-007 (test strategy philosophy) and Section 8.3 (body template) for all requirements
2. **[PLANNING]** Determine interleave ratio from complexity class: LOW→1:3, MEDIUM→1:2, HIGH→1:1
3. **[EXECUTION]** Generate Validation Philosophy section encoding continuous parallel validation with stop-and-fix principles
4. **[EXECUTION]** Generate Validation Milestones table with V# IDs, each referencing a real M# work milestone from roadmap.md
5. **[EXECUTION]** Generate Issue Classification table (Critical/Major/Minor/Info with actions) and Acceptance Gates per milestone
6. **[EXECUTION]** Generate test-strategy.md YAML frontmatter per spec FR-002 schema
7. **[VERIFICATION]** Validate interleave ratio matches complexity class; verify every validation milestone references a real work milestone; verify stop-and-fix thresholds defined
8. **[COMPLETION]** Document interleave ratio calculation and milestone cross-references

**Acceptance Criteria:**
- Interleave ratio matches complexity class: LOW→1:3, MEDIUM→1:2, HIGH→1:1
- Every validation milestone references a real work milestone from the just-generated roadmap.md
- Continuous parallel validation philosophy is explicitly encoded (not generic boilerplate)
- Stop-and-fix thresholds defined for each severity level (Critical, Major, Minor, Info)

**Validation:**
- Manual check: Verify interleave ratio matches complexity; verify V# milestones reference valid M# milestones; verify philosophy is specific not boilerplate
- Evidence: linkable artifact produced (evidence.md with ratio calculation and cross-references)

**Dependencies:** T03.04 (roadmap.md must be fully generated first — sequencing constraint)
**Rollback:** TBD
**Notes:** Per spec FR-006 Wave 3 and FR-007, SKILL.md authors test-strategy.md directly (not a separate agent) because it has full context and correct timing. quality-engineer validates in Wave 4 but does not author.

---

### T03.06 — Implement Wave 3 YAML frontmatter generation

**Roadmap Item ID(s):** R-017
**Why:** YAML frontmatter is a versioned contract for downstream consumption by the future tasklist generator; schema stability and correctness are critical.
**Effort:** S
**Risk:** Medium
**Risk Drivers:** schema
**Tier:** STRICT
**Confidence:** [███████░░░] 72%
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer) (3-5K tokens, 60s timeout)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7 | Fallback Allowed: No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0017
**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0017/spec.md`
- `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0017/evidence.md`

**Deliverables:**
- YAML frontmatter generation for all 3 artifacts (roadmap.md, extraction.md, test-strategy.md) per spec FR-002 schemas, with mutual exclusion rule for spec_source/spec_sources

**Steps:**
1. **[PLANNING]** Load spec FR-002 for all 3 frontmatter schemas (roadmap.md, extraction.md, test-strategy.md)
2. **[PLANNING]** Confirm mutual exclusion rule: exactly one of spec_source or spec_sources, never both
3. **[EXECUTION]** Implement roadmap.md frontmatter with all required fields including milestone_index, adversarial block (when applicable), and validation fields
4. **[EXECUTION]** Implement extraction.md frontmatter with requirement counts, domains, complexity fields
5. **[EXECUTION]** Implement test-strategy.md frontmatter with validation_philosophy, interleave_ratio, major_issue_policy
6. **[EXECUTION]** Implement spec_source/spec_sources mutual exclusion enforcement
7. **[VERIFICATION]** Parse all 3 frontmatters with YAML parser; verify spec_source/spec_sources mutual exclusion; verify all required fields present
8. **[COMPLETION]** Document schema compliance and YAML parse results

**Acceptance Criteria:**
- All 3 artifacts have valid, parseable YAML frontmatter
- Exactly one of spec_source or spec_sources present in each frontmatter (never both, never neither)
- roadmap.md frontmatter includes milestone_index with complete M# entries
- Adversarial block present in frontmatter only when adversarial mode was used

**Validation:**
- Manual check: Parse all frontmatters with YAML parser; verify mutual exclusion rule; verify all FR-002 fields present
- Evidence: linkable artifact produced (evidence.md with YAML parse results)

**Dependencies:** T03.04 (roadmap.md), T03.05 (test-strategy.md), T02.03 (extraction.md)
**Rollback:** TBD
**Notes:** Tier conflict: "schema" keyword matches STRICT (data category). Per spec NFR-003, frontmatter schema is a contract — fields may be added but not removed or renamed. Per risk R-003, versioned contract prevents breaking tasklist generator.

---

### Checkpoint: End of Phase 3

**Purpose:** Final gate before adversarial integration and validation phases; confirms all 3 output artifacts are generated with valid frontmatter.
**Checkpoint Report Path:** `.dev/releases/current/v2.0-roadmap-v2/checkpoints/CP-P03-END.md`
**Verification:**
- roadmap.md, extraction.md, and test-strategy.md all written to output directory
- All 3 artifacts have valid, parseable YAML frontmatter
- test-strategy.md references concrete milestones from roadmap.md

**Exit Criteria:**
- All 6 tasks (T03.01-T03.06) marked complete with evidence artifacts
- Single-spec pipeline (Waves 0-3) is end-to-end functional
- YAML frontmatter for all 3 artifacts validated by parser

---

**End of Phase 3** | Tasks: 6 | Deliverables: 6 (D-0012–D-0017) | Tier Distribution: STRICT: 1, STANDARD: 5, LIGHT: 0, EXEMPT: 0
