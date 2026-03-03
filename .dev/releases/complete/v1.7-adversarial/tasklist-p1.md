# TASKLIST — v1.7 sc:adversarial Generic Adversarial Debate & Merge Pipeline

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.dev/releases/current/v1.7-adversarial/`
- **Tasklist Path**: `.dev/releases/current/v1.7-adversarial/tasklist.md`
- **Execution Log Path**: `.dev/releases/current/v1.7-adversarial/execution-log.md`
- **Checkpoint Reports Path**: `.dev/releases/current/v1.7-adversarial/checkpoints/`
- **Evidence Root**: `.dev/releases/current/v1.7-adversarial/evidence/`
- **Artifacts Root**: `.dev/releases/current/v1.7-adversarial/artifacts/`
- **Feedback Log Path**: `.dev/releases/current/v1.7-adversarial/feedback-log.md`

---

## Source Snapshot

- Implements `/sc:adversarial`, a generic reusable command for structured adversarial debate, comparison, and merge across 2-10 artifacts
- 5-step protocol: diff analysis → adversarial debate → hybrid scoring & base selection → refactoring plan → merge execution
- Two input modes: Mode A (compare existing files) and Mode B (generate variants from source + agents)
- Configurable debate depth (quick/standard/deep), convergence threshold (default 80%), interactive mode
- Produces 6 artifacts: diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, merged output
- 6 milestones (M0-M5) on strictly sequential critical path, 23-33 hours estimated effort

---

## Deterministic Rules Applied

1. **Phase renumbering**: M0-M5 mapped to Phase 1-6 sequentially with no gaps (Section 4.3)
2. **Task ID scheme**: `T<PP>.<TT>` zero-padded, e.g., `T01.03` (Section 4.5)
3. **Checkpoint cadence**: After every 5 tasks within a phase + end of each phase (Section 4.8)
4. **Clarification tasks**: Inserted for genuine tier ambiguity where keyword matches conflict with task semantics (Section 4.6)
5. **Deliverable registry**: Each task declares 1-5 deliverables with D-#### IDs and intended artifact paths (Section 5.1)
6. **Effort mapping**: Deterministic EFFORT_SCORE from text length (≥120 chars: +1), split status (+1), keyword presence (+1), dependency words (+1) → XS/S/M/L/XL (Section 5.2.1)
7. **Risk mapping**: Deterministic RISK_SCORE from security (+2), data (+2), auth (+1), performance (+1), cross-cutting (+1) keywords → Low/Medium/High (Section 5.2.2)
8. **Tier classification**: STRICT > EXEMPT > LIGHT > STANDARD priority, keyword matching + context boosters + compound phrase overrides (Section 5.3)
9. **Verification routing**: Tier-aligned — STRICT: sub-agent, STANDARD: direct test, LIGHT: sanity check, EXEMPT: skip (Section 4.10)
10. **MCP requirements**: Tier-driven tool dependencies per Section 5.5
11. **Traceability matrix**: R-### → T##.## → D-#### → artifact paths → tier → confidence (Section 5.7)
12. **Context normalization**: Task text includes milestone objective + task description for keyword scanning; "implement" and "create" from milestone objectives contribute to STANDARD scoring

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (≤ 20 words) |
|---|---|---|
| R-001 | Phase 1 | Command definition (~80-100 lines): usage, flags, examples, boundaries |
| R-002 | Phase 1 | Behavioral instructions (~400-500 lines): 5-step protocol, convergence, error handling |
| R-003 | Phase 1 | Process coordinator: delegates but doesn't participate |
| R-004 | Phase 1 | Plan executor: follows refactoring plan, provenance annotations |
| R-005 | Phase 1 | Reference docs: debate-protocol.md, scoring-protocol.md, agent-specs.md, artifact-templates.md |
| R-006 | Phase 1 | All files created, make sync-dev copies to .claude/, make verify-sync passes |
| R-007 | Phase 2 | Parse dual input modes: --compare file1,file2,... (Mode A) and --source/--generate/--agents (Mode B). Validate 2-10 |
| R-008 | Phase 2 | Load and normalize variant files. Mode A: copy originals to adversarial/ dir. Mode B: placeholder |
| R-009 | Phase 2 | Structural diff: compare section ordering, hierarchy depth, heading structure across variants |
| R-010 | Phase 2 | Content diff: compare approaches topic-by-topic, identify coverage differences |
| R-011 | Phase 2 | Contradiction detection: structured scan per Appendix A (opposing claims, requirement-constraint conflicts, impossible sequences) |
| R-012 | Phase 2 | Unique contribution extraction: identify ideas present in only one variant with value assessment |
| R-013 | Phase 2 | Generate diff-analysis.md following the artifact template (Section 8.1 of spec) |
| R-014 | Phase 3 | Advocate agent instantiation: parse model[:persona[:"instruction"]] spec, create Task agents with appropriate prompts |
| R-015 | Phase 3 | Round 1 (parallel): Each advocate receives their variant + all others + diff-analysis.md |
| R-016 | Phase 3 | Round 2 (sequential): Rebuttals — each advocate receives Round 1 transcripts, addresses criticisms |
| R-017 | Phase 3 | Round 3 (conditional): Final arguments if --depth deep AND convergence < threshold |
| R-018 | Phase 3 | Convergence detection: per-point agreement tracking, configurable threshold (default 80%) |
| R-019 | Phase 3 | Per-point scoring matrix: for each diff point, record winner, confidence, evidence summary |
| R-020 | Phase 3 | Generate debate-transcript.md following artifact template (Section 8.2) |
| R-021 | Phase 4 | Quantitative layer: implement 5 deterministic metrics. RC via grep-matching against source requirements |
| R-022 | Phase 4 | Qualitative layer: implement 25-criterion additive binary rubric across 5 dimensions |
| R-023 | Phase 4 | Position-bias mitigation: run qualitative evaluation twice (forward + reverse order) |
| R-024 | Phase 4 | Combined scoring: variant_score = (0.50 × quant_score) + (0.50 × qual_score) |
| R-025 | Phase 4 | Tiebreaker protocol: within-5% detection → debate performance → correctness count → input order |
| R-026 | Phase 4 | Generate base-selection.md with full scoring breakdown, evidence citations, selection rationale |
| R-027 | Phase 5 | Refactoring plan: for each non-base strength from debate, generate improvement description + integration point |
| R-028 | Phase 5 | Interactive mode: implement pause points at diff analysis, debate, base selection, and refactoring plan |
| R-029 | Phase 5 | Merge executor: apply each planned change to base document methodically. Maintain structural integrity |
| R-030 | Phase 5 | Provenance annotations: tag merged sections with source attribution |
| R-031 | Phase 5 | Post-merge consistency validation: structural integrity check, internal reference validation, contradiction re-scan |
| R-032 | Phase 5 | Generate refactor-plan.md + merge-log.md artifacts |
| R-033 | Phase 5 | Return contract: path to merged output, convergence score, artifacts dir path, status, unresolved conflicts |
| R-034 | Phase 6 | Error handling matrix (FR-006): agent failure retry + N-1 fallback, <10% diff skip |
| R-035 | Phase 6 | Mode B variant generation: parallel dispatch of Task agents per --agents spec |
| R-036 | Phase 6 | MCP integration: Sequential for debate scoring/convergence analysis, Serena for memory persistence, Context7 |
| R-037 | Phase 6 | Framework registration: update COMMANDS.md, FLAGS.md, ORCHESTRATOR.md routing tables for sc:adversarial |
| R-038 | Phase 6 | E2E validation — Mode A: compare 2-3 existing markdown files, verify all 5 artifacts |
| R-039 | Phase 6 | E2E validation — Mode B: generate 2 variants from a source spec with different agents |
| R-040 | Phase 6 | Documentation: update integration guide, add examples to command docs, document sc:roadmap v2 |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | adversarial.md command definition | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0001/spec.md` | XS | Low |
| D-0002 | T01.02 | R-002 | SKILL.md behavioral instructions | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0002/spec.md` | S | Low |
| D-0003 | T01.03 | R-003 | debate-orchestrator.md agent definition | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0003/spec.md` | S | Low |
| D-0004 | T01.04 | R-004 | merge-executor.md agent definition | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0004/spec.md` | S | Low |
| D-0005 | T01.05 | R-005 | debate-protocol.md reference doc | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0005/spec.md` | S | Low |
| D-0006 | T01.05 | R-005 | scoring-protocol.md reference doc | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0006/spec.md` | S | Low |
| D-0007 | T01.05 | R-005 | agent-specs.md reference doc | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0007/spec.md` | S | Low |
| D-0008 | T01.05 | R-005 | artifact-templates.md reference doc | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0008/spec.md` | S | Low |
| D-0009 | T01.06 | R-006 | Sync verification evidence | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0009/evidence.md` | XS | Low |
| D-0010 | T02.01 | R-007 | Input mode parser logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0010/spec.md` | S | Low |
| D-0011 | T02.02 | R-008 | Variant loading and normalization logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0011/spec.md` | XS | Low |
| D-0012 | T02.03 | R-009 | Structural diff engine | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0012/spec.md` | XS | Low |
| D-0013 | T02.04 | R-010 | Content diff engine | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0013/spec.md` | XS | Low |
| D-0014 | T02.05 | R-011 | Contradiction detection protocol | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0014/spec.md` | S | Low |
| D-0015 | T02.06 | R-012 | Unique contribution extractor | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0015/spec.md` | XS | Low |
| D-0016 | T02.07 | R-013 | diff-analysis.md artifact | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0016/spec.md` | XS | Low |
| D-0017 | T03.01 | R-014 | Advocate agent instantiation logic | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0017/spec.md` | S | Low |
| D-0018 | T03.02 | R-015 | Round 1 parallel dispatch logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0018/spec.md` | S | Low |
| D-0019 | T03.03 | R-016 | Round 2 rebuttal logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0019/spec.md` | S | Low |
| D-0020 | T03.04 | R-017 | Round 3 final arguments logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0020/spec.md` | S | Low |
| D-0021 | T03.05 | R-018 | Convergence detection algorithm | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0021/spec.md` | S | Low |
| D-0022 | T03.06 | R-019 | Per-point scoring matrix | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0022/spec.md` | XS | Low |
| D-0023 | T03.07 | R-020 | debate-transcript.md artifact | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0023/spec.md` | XS | Low |
| D-0024 | T04.01 | R-021 | Quantitative scoring engine (5 metrics) | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0024/spec.md` | S | Low |
| D-0025 | T04.02 | R-022 | Qualitative rubric engine (25 criteria) | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0025/spec.md` | S | Low |
| D-0026 | T04.03 | R-023 | Position-bias mitigation logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0026/spec.md` | S | Low |
| D-0027 | T04.04 | R-024 | Combined scoring formula | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0027/spec.md` | XS | Low |
| D-0028 | T04.05 | R-025 | Tiebreaker protocol | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0028/spec.md` | XS | Low |
| D-0029 | T04.06 | R-026 | base-selection.md artifact | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0029/spec.md` | XS | Low |
| D-0030 | T05.01 | R-027 | Refactoring plan generation logic | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0030/spec.md` | S | Low |
| D-0031 | T05.02 | R-028 | Interactive mode checkpoint logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0031/spec.md` | S | Low |
| D-0032 | T05.03 | R-029 | Merge execution logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0032/spec.md` | XS | Low |
| D-0033 | T05.04 | R-030 | Provenance annotation system | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0033/spec.md` | S | Low |
| D-0034 | T05.05 | R-031 | Post-merge validation checks | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0034/spec.md` | XS | Low |
| D-0035 | T05.06 | R-032 | refactor-plan.md artifact template | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0035/spec.md` | XS | Low |
| D-0036 | T05.06 | R-032 | merge-log.md artifact template | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0036/spec.md` | XS | Low |
| D-0037 | T05.07 | R-033 | Return contract implementation | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0037/spec.md` | S | Low |
| D-0038 | T06.01 | R-034 | Error handling matrix | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0038/spec.md` | S | Low |
| D-0039 | T06.02 | R-035 | Mode B variant generation logic | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0039/spec.md` | S | Low |
| D-0040 | T06.03 | R-036 | MCP integration layer | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0040/spec.md` | S | Low |
| D-0041 | T06.04 | R-037 | COMMANDS.md framework update | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0041/spec.md` | XS | Low |
| D-0042 | T06.04 | R-037 | ORCHESTRATOR.md routing update | STRICT | Sub-agent | `.dev/releases/current/v1.7-adversarial/artifacts/D-0042/spec.md` | XS | Low |
| D-0043 | T06.05 | R-038 | E2E Mode A validation results | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0043/evidence.md` | S | Low |
| D-0044 | T06.06 | R-039 | E2E Mode B validation results | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0044/evidence.md` | XS | Low |
| D-0045 | T06.07 | R-040 | Integration documentation | STANDARD | Direct test | `.dev/releases/current/v1.7-adversarial/artifacts/D-0045/spec.md` | XS | Low |

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---:|---|---|
| 1 | Foundation & Scaffolding | T01.01–T01.06 | All file scaffolds created and synced | STRICT: 1, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 2 | Diff Analysis Engine | T02.01–T02.07 | Step 1 produces diff-analysis.md from 2+ inputs | STRICT: 0, STANDARD: 7, LIGHT: 0, EXEMPT: 0 |
| 3 | Adversarial Debate Protocol | T03.01–T03.07 | Step 2 produces debate-transcript.md with convergence | STRICT: 1, STANDARD: 6, LIGHT: 0, EXEMPT: 0 |
| 4 | Hybrid Scoring & Base Selection | T04.01–T04.06 | Step 3 produces base-selection.md with scoring | STRICT: 0, STANDARD: 6, LIGHT: 0, EXEMPT: 0 |
| 5 | Refactoring Plan & Merge Execution | T05.01–T05.07 | Steps 4-5 produce merged output with provenance | STRICT: 1, STANDARD: 6, LIGHT: 0, EXEMPT: 0 |
| 6 | Integration, Polish & Validation | T06.01–T06.07 | Full pipeline validated E2E in both modes | STRICT: 1, STANDARD: 6, LIGHT: 0, EXEMPT: 0 |

---

## Phase 1: Foundation & Scaffolding

Create all file scaffolds so subsequent phases have clear targets. No behavioral logic — structure only.

### T01.01 — Create adversarial.md command definition

**Roadmap Item ID(s):** R-001
**Why:** The command definition is the entry point for /sc:adversarial — specifies usage, flags, examples, and boundaries.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0001
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0001/spec.md`

**Deliverables:**
1. `src/superclaude/commands/adversarial.md` — ~80-100 line command definition with usage, flags table (FR-003), examples (Section 6.3 of spec), boundaries (Section 9 of spec)

**Steps:**
1. **[PLANNING]** Read existing command definitions (e.g., `src/superclaude/commands/roadmap.md`) for structural reference
2. **[PLANNING]** Identify required sections: usage, flags table, examples, boundaries — sourced from spec Sections 6, 9
3. **[EXECUTION]** Write command definition following established pattern with all flags from FR-003
4. **[EXECUTION]** Include all 5 usage examples from spec Section 6.3
5. **[VERIFICATION]** Verify file matches structural pattern of existing commands
6. **[COMPLETION]** File created at `src/superclaude/commands/adversarial.md`

**Acceptance Criteria:**
- File contains usage, flags table, examples, and boundaries sections matching spec Sections 6 and 9
- Follows structural pattern of existing command definitions in the commands/ directory
- All 9 flags from FR-003 are documented with short form, required status, default, and description
- File path and naming convention consistent with project structure

**Validation:**
- Manual check: Compare structure against `src/superclaude/commands/roadmap.md` for pattern compliance
- Evidence: File exists at correct path with expected section headings

**Dependencies:** None
**Rollback:** Delete file
**Notes:** —

---

### T01.02 — Create SKILL.md behavioral instructions

**Roadmap Item ID(s):** R-002
**Why:** SKILL.md encodes the 5-step adversarial protocol, convergence logic, error handling, and interactive mode behavior.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0002
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0002/spec.md`

**Deliverables:**
1. `src/superclaude/skills/sc-adversarial/SKILL.md` — ~400-500 line behavioral instruction document covering the full 5-step protocol

**Steps:**
1. **[PLANNING]** Read existing SKILL.md (e.g., `src/superclaude/skills/sc-roadmap/SKILL.md`) for structural reference
2. **[PLANNING]** Map spec sections to SKILL.md sections: FR-001 (input modes), FR-002 (5-step protocol), FR-003 (parameters), FR-004 (interactive mode), FR-006 (error handling)
3. **[EXECUTION]** Write behavioral instructions covering dual input modes, 5-step protocol overview, convergence detection, error handling matrix
4. **[EXECUTION]** Include agent delegation patterns, artifact output structure, and return contract spec
5. **[VERIFICATION]** Verify all functional requirements (FR-001 through FR-007) are addressable from the SKILL.md instructions
6. **[COMPLETION]** File created at `src/superclaude/skills/sc-adversarial/SKILL.md`

**Acceptance Criteria:**
- All 7 functional requirements (FR-001 through FR-007) are covered in behavioral instructions
- Follows structural pattern of existing SKILL.md files
- 5-step protocol clearly sequenced with input/output for each step
- Error handling matrix from FR-006 fully encoded

**Validation:**
- Manual check: Verify each FR-### from spec has corresponding instruction section in SKILL.md
- Evidence: File exists at correct path, ≥400 lines, covers all protocol steps

**Dependencies:** None
**Rollback:** Delete file
**Notes:** —

---

### T01.03 — Create debate-orchestrator.md agent definition

**Roadmap Item ID(s):** R-003
**Why:** The debate-orchestrator coordinates the entire adversarial pipeline without participating in debates.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0003
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0003/spec.md`

**Deliverables:**
1. `src/superclaude/agents/debate-orchestrator.md` — ~60-80 line agent definition specifying purpose, responsibilities, tools, model preference, and explicit non-responsibilities

**Steps:**
1. **[PLANNING]** Read existing agent definitions for structural reference
2. **[PLANNING]** Extract orchestrator spec from spec Section 5.1: responsibilities, model preference (opus), tools (Task, Read, Write, Glob, Grep, Bash)
3. **[EXECUTION]** Write agent definition with purpose, responsibilities, tools, model preference
4. **[EXECUTION]** Include explicit "Does NOT" section per spec Section 5.1
5. **[VERIFICATION]** Verify all responsibilities and non-responsibilities from spec Section 5.1 are present
6. **[COMPLETION]** File created at `src/superclaude/agents/debate-orchestrator.md`

**Acceptance Criteria:**
- All 7 responsibilities from spec Section 5.1 are listed
- "Does NOT" section includes all 3 exclusions from spec
- Model preference (opus) and tool list match spec
- Follows structural pattern of existing agent definitions

**Validation:**
- Manual check: Compare against spec Section 5.1 for completeness
- Evidence: File exists at correct path with all required sections

**Dependencies:** None
**Rollback:** Delete file
**Notes:** Split from roadmap item T0.3 (was T0.3a/T0.3b); this is the orchestrator half.

---

### T01.04 — Create merge-executor.md agent definition

**Roadmap Item ID(s):** R-004
**Why:** The merge-executor applies refactoring plans to produce unified merged artifacts with provenance.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0004
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0004/spec.md`

**Deliverables:**
1. `src/superclaude/agents/merge-executor.md` — ~40-60 line agent definition specifying purpose, responsibilities, tools, model preference, and explicit non-responsibilities

**Steps:**
1. **[PLANNING]** Read existing agent definitions for structural reference
2. **[PLANNING]** Extract merge-executor spec from spec Section 5.2: responsibilities, model preference (opus/sonnet), tools (Read, Write, Edit, Grep)
3. **[EXECUTION]** Write agent definition with purpose, responsibilities, tools, model preference
4. **[EXECUTION]** Include explicit "Does NOT" section per spec Section 5.2
5. **[VERIFICATION]** Verify all responsibilities and non-responsibilities from spec Section 5.2 are present
6. **[COMPLETION]** File created at `src/superclaude/agents/merge-executor.md`

**Acceptance Criteria:**
- All 6 responsibilities from spec Section 5.2 are listed
- "Does NOT" section includes all 3 exclusions from spec
- Model preference and tool list match spec
- Follows structural pattern of existing agent definitions

**Validation:**
- Manual check: Compare against spec Section 5.2 for completeness
- Evidence: File exists at correct path with all required sections

**Dependencies:** None
**Rollback:** Delete file
**Notes:** Split from roadmap item T0.3 (was T0.3a/T0.3b); this is the executor half.

---

### T01.05 — Create reference documents in refs/ directory

**Roadmap Item ID(s):** R-005
**Why:** Reference docs provide detailed protocol specifications, scoring algorithms, agent formats, and artifact templates consumed by the SKILL.md.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STRICT`
**Confidence:** `[██████████] 78%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0005, D-0006, D-0007, D-0008
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0005/spec.md`
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0006/spec.md`
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0007/spec.md`
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0008/spec.md`

**Deliverables:**
1. `src/superclaude/skills/sc-adversarial/refs/debate-protocol.md` — 5-step protocol detail from spec FR-002
2. `src/superclaude/skills/sc-adversarial/refs/scoring-protocol.md` — Full Appendix A algorithm: quant metrics, qual rubric, CEV protocol, combined scoring, tiebreaker, position-bias mitigation
3. `src/superclaude/skills/sc-adversarial/refs/agent-specs.md` — Agent specification format, advocate behavior, model/persona/instruction parsing
4. `src/superclaude/skills/sc-adversarial/refs/artifact-templates.md` — Output templates for all 6 artifacts (Sections 8.1-8.4 of spec)

**Steps:**
1. **[PLANNING]** Identify source sections for each ref doc: FR-002 → debate-protocol, Appendix A → scoring-protocol, Section 5 → agent-specs, Section 8 → artifact-templates
2. **[PLANNING]** Ensure refs/ directory exists; create `__init__.py` if needed
3. **[EXECUTION]** Write debate-protocol.md covering 5-step protocol, convergence detection, round structure
4. **[EXECUTION]** Write scoring-protocol.md with full Appendix A: quantitative metrics, qualitative rubric, CEV, combined formula, tiebreaker, position-bias mitigation
5. **[EXECUTION]** Write agent-specs.md with agent specification format and advocate behavior rules
6. **[EXECUTION]** Write artifact-templates.md with templates for diff-analysis, debate-transcript, base-selection, refactor-plan, merge-log, merged output
7. **[VERIFICATION]** Verify each ref doc covers its source spec sections completely
8. **[COMPLETION]** All 4 files created in `src/superclaude/skills/sc-adversarial/refs/`

**Acceptance Criteria:**
- debate-protocol.md covers all 5 steps with input/output/delegation per step
- scoring-protocol.md contains complete Appendix A algorithm with all formulas
- agent-specs.md documents the `model[:persona[:"instruction"]]` format and advocate behavior
- artifact-templates.md includes templates matching spec Sections 8.1-8.4

**Validation:**
- Manual check: Each ref doc cross-referenced against its source spec section
- Evidence: 4 files exist in refs/ directory with expected content

**Dependencies:** None
**Rollback:** Delete refs/ directory contents
**Notes:** Tier classified STRICT due to >2 files affected (+0.3 context booster) and multi-file scope of 4 deliverables.

---

### Checkpoint: Phase 1 / Tasks T01.01–T01.05

**Purpose:** Verify all scaffolding files are created before proceeding to implementation phases.
**Checkpoint Report Path:** `.dev/releases/current/v1.7-adversarial/checkpoints/CP-P01-T01-T05.md`
**Verification:**
- All 8 new files exist at expected paths in `src/superclaude/`
- File sizes are non-trivial (command ≥80 lines, SKILL.md ≥400 lines, agents ≥40 lines)
- Structural patterns match existing files in the same directories
**Exit Criteria:**
- Zero missing files from the File Manifest M0 section
- Each file has all required sections per its source spec section
- No placeholder/TODO content in any file

---

### T01.06 — Run component sync and verify

**Roadmap Item ID(s):** R-006
**Why:** Ensures all new files are synced from src/superclaude/ to .claude/ for Claude Code to access during development.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0009
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0009/evidence.md`

**Deliverables:**
1. Sync verification — `make sync-dev` succeeds, `make verify-sync` passes with zero differences

**Steps:**
1. **[PLANNING]** Confirm all Phase 1 files are written to src/superclaude/
2. **[PLANNING]** Check no pending changes block sync
3. **[EXECUTION]** Run `make sync-dev` to copy files to `.claude/`
4. **[EXECUTION]** Run `make verify-sync` to confirm src/ and .claude/ match
5. **[VERIFICATION]** Both commands exit with status 0
6. **[COMPLETION]** Record sync verification output

**Acceptance Criteria:**
- `make sync-dev` completes without errors
- `make verify-sync` reports zero differences
- New files visible in both `src/superclaude/` and `.claude/` directories
- No unintended files modified during sync

**Validation:**
- `make sync-dev && make verify-sync`
- Evidence: Command output showing success

**Dependencies:** T01.01, T01.02, T01.03, T01.04, T01.05
**Rollback:** Re-run sync after fixing issues
**Notes:** —

---

### Checkpoint: End of Phase 1

**Purpose:** Gate check before proceeding to Phase 2 implementation work.
**Checkpoint Report Path:** `.dev/releases/current/v1.7-adversarial/checkpoints/CP-P01-END.md`
**Verification:**
- All 9 files from File Manifest M0 exist and are non-empty
- `make verify-sync` passes cleanly
- File structures match existing patterns in the project
**Exit Criteria:**
- Phase 1 deliverables D-0001 through D-0009 all produced
- Zero sync differences between src/ and .claude/
- Ready to begin Phase 2 implementation

---

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0001/` |
| R-002 | T01.02 | D-0002 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0002/` |
| R-003 | T01.03 | D-0003 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0003/` |
| R-004 | T01.04 | D-0004 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0004/` |
| R-005 | T01.05 | D-0005, D-0006, D-0007, D-0008 | STRICT | 78% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0005/` through `D-0008/` |
| R-006 | T01.06 | D-0009 | STANDARD | 80% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0009/` |
| R-007 | T02.01 | D-0010 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0010/` |
| R-008 | T02.02 | D-0011 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0011/` |
| R-009 | T02.03 | D-0012 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0012/` |
| R-010 | T02.04 | D-0013 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0013/` |
| R-011 | T02.05 | D-0014 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0014/` |
| R-012 | T02.06 | D-0015 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0015/` |
| R-013 | T02.07 | D-0016 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0016/` |
| R-014 | T03.01 | D-0017 | STRICT | 72% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0017/` |
| R-015 | T03.02 | D-0018 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0018/` |
| R-016 | T03.03 | D-0019 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0019/` |
| R-017 | T03.04 | D-0020 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0020/` |
| R-018 | T03.05 | D-0021 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0021/` |
| R-019 | T03.06 | D-0022 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0022/` |
| R-020 | T03.07 | D-0023 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0023/` |
| R-021 | T04.01 | D-0024 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0024/` |
| R-022 | T04.02 | D-0025 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0025/` |
| R-023 | T04.03 | D-0026 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0026/` |
| R-024 | T04.04 | D-0027 | STANDARD | 80% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0027/` |
| R-025 | T04.05 | D-0028 | STANDARD | 80% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0028/` |
| R-026 | T04.06 | D-0029 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0029/` |
| R-027 | T05.01 | D-0030 | STRICT | 72% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0030/` |
| R-028 | T05.02 | D-0031 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0031/` |
| R-029 | T05.03 | D-0032 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0032/` |
| R-030 | T05.04 | D-0033 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0033/` |
| R-031 | T05.05 | D-0034 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0034/` |
| R-032 | T05.06 | D-0035, D-0036 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0035/`, `D-0036/` |
| R-033 | T05.07 | D-0037 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0037/` |
| R-034 | T06.01 | D-0038 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0038/` |
| R-035 | T06.02 | D-0039 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0039/` |
| R-036 | T06.03 | D-0040 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0040/` |
| R-037 | T06.04 | D-0041, D-0042 | STRICT | 78% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0041/`, `D-0042/` |
| R-038 | T06.05 | D-0043 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0043/` |
| R-039 | T06.06 | D-0044 | STANDARD | 75% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0044/` |
| R-040 | T06.07 | D-0045 | STANDARD | 80% | `.dev/releases/current/v1.7-adversarial/artifacts/D-0045/` |

---

## Execution Log Template

**Intended Path:** `.dev/releases/current/v1.7-adversarial/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | T01.01 | STANDARD | D-0001 | | Manual | TBD | `.dev/releases/current/v1.7-adversarial/evidence/` |
| | T01.02 | STANDARD | D-0002 | | Manual | TBD | `.dev/releases/current/v1.7-adversarial/evidence/` |
| | T01.06 | STANDARD | D-0009 | | `make sync-dev && make verify-sync` | TBD | `.dev/releases/current/v1.7-adversarial/evidence/` |

*(Rows for all 40 tasks follow same pattern — populate during execution)*

---

## Checkpoint Report Template

For each checkpoint, execution produces one report using this template:

```
# Checkpoint Report — <Checkpoint Title>
**Checkpoint Report Path:** .dev/releases/current/v1.7-adversarial/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>

## Status
Overall: Pass | Fail | TBD

## Verification Results
- <Verification bullet 1 result>
- <Verification bullet 2 result>
- <Verification bullet 3 result>

## Exit Criteria Assessment
- <Exit criterion 1 result>
- <Exit criterion 2 result>
- <Exit criterion 3 result>

## Issues & Follow-ups
- <List blocking issues; reference T##.## and D-####>

## Evidence
- .dev/releases/current/v1.7-adversarial/evidence/<relevant-evidence-files>
```

**Checkpoint reports to generate:**
- `CP-P01-T01-T05.md` — Phase 1 mid-phase
- `CP-P01-END.md` — Phase 1 end
- `CP-P02-T01-T05.md` — Phase 2 mid-phase
- `CP-P02-END.md` — Phase 2 end
- `CP-P03-T01-T05.md` — Phase 3 mid-phase
- `CP-P03-END.md` — Phase 3 end
- `CP-P04-T01-T05.md` — Phase 4 mid-phase
- `CP-P04-END.md` — Phase 4 end
- `CP-P05-T01-T05.md` — Phase 5 mid-phase
- `CP-P05-END.md` — Phase 5 end
- `CP-P06-T01-T05.md` — Phase 6 mid-phase
- `CP-P06-END.md` — Phase 6 end

---

## Feedback Collection Template

**Intended Path:** `.dev/releases/current/v1.7-adversarial/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤ 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| T01.01 | STANDARD | | | | | |
| T01.02 | STANDARD | | | | | |
| T01.03 | STANDARD | | | | | |
| T01.04 | STANDARD | | | | | |
| T01.05 | STRICT | | | | | |
| T01.06 | STANDARD | | | | | |
| T02.01 | STANDARD | | | | | |
| T02.02 | STANDARD | | | | | |
| T02.03 | STANDARD | | | | | |
| T02.04 | STANDARD | | | | | |
| T02.05 | STANDARD | | | | | |
| T02.06 | STANDARD | | | | | |
| T02.07 | STANDARD | | | | | |
| T03.01 | STRICT | | | | | |
| T03.02 | STANDARD | | | | | |
| T03.03 | STANDARD | | | | | |
| T03.04 | STANDARD | | | | | |
| T03.05 | STANDARD | | | | | |
| T03.06 | STANDARD | | | | | |
| T03.07 | STANDARD | | | | | |
| T04.01 | STANDARD | | | | | |
| T04.02 | STANDARD | | | | | |
| T04.03 | STANDARD | | | | | |
| T04.04 | STANDARD | | | | | |
| T04.05 | STANDARD | | | | | |
| T04.06 | STANDARD | | | | | |
| T05.01 | STRICT | | | | | |
| T05.02 | STANDARD | | | | | |
| T05.03 | STANDARD | | | | | |
| T05.04 | STANDARD | | | | | |
| T05.05 | STANDARD | | | | | |
| T05.06 | STANDARD | | | | | |
| T05.07 | STANDARD | | | | | |
| T06.01 | STANDARD | | | | | |
| T06.02 | STANDARD | | | | | |
| T06.03 | STANDARD | | | | | |
| T06.04 | STRICT | | | | | |
| T06.05 | STANDARD | | | | | |
| T06.06 | STANDARD | | | | | |
| T06.07 | STANDARD | | | | | |

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification (e.g., "Involved auth paths", "Actually trivial")
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`
