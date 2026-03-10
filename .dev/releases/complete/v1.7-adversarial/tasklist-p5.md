# TASKLIST — v1.7 sc:adversarial Generic Adversarial Debate & Merge Pipeline

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.dev/releases/current/v1.7-adversarial/`
- **Tasklist Path**: `.dev/releases/current/v1.7-adversarial/tasklist-p5.md`
- **Execution Log Path**: `.dev/releases/current/v1.7-adversarial/execution-log-p5.md`
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


## Phase 5: Refactoring Plan & Merge Execution

Implement Steps 4-5 — generate a merge plan from debate outcomes, execute it to produce a unified document with provenance, and implement the return contract.

### T05.01 — Implement refactoring plan generation

**Roadmap Item ID(s):** R-027
**Why:** The refactoring plan translates debate outcomes into actionable merge instructions, ensuring strengths from all variants are incorporated.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STRICT`
**Confidence:** `[████████--] 72%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer)
**MCP Requirements:** Required: Sequential, Serena | Preferred: Context7
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0030
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0030/spec.md`

**Deliverables:**
1. Refactoring plan generation logic — for each non-base strength: improvement description, integration point, risk, merge approach; for each base weakness: referenced fix from non-base variant

**Steps:**
1. **[PLANNING]** Review spec FR-002 Step 4 and Section 8.4 refactor-plan template
2. **[PLANNING]** Extract from base-selection.md: strengths to incorporate, weaknesses to fix
3. **[EXECUTION]** For each non-base strength (from debate): generate change entry with description, target location, rationale, risk
4. **[EXECUTION]** For each base weakness (from debate): reference the non-base variant's approach, specify fix
5. **[EXECUTION]** Include "Changes NOT being made" section with rationale for debated-but-rejected improvements
6. **[VERIFICATION]** Verify every strength from base-selection.md "Strengths to Incorporate" section has a corresponding change
7. **[COMPLETION]** Refactoring plan ready for review/execution

**Acceptance Criteria:**
- Every non-base strength identified in base-selection.md has a planned change
- Every base weakness has a referenced fix
- Each change includes: source variant, target location, rationale, risk assessment
- "Changes NOT made" section documents rejected alternatives with rationale

**Validation:**
- Manual check: Cross-reference plan entries against base-selection.md strengths/weaknesses
- Evidence: Refactoring plan with complete coverage of all identified improvements

**Dependencies:** T04.06 (requires base-selection.md)
**Rollback:** Revert plan generation logic
**Notes:** Tier classified STRICT: "refactoring" matches "refactor" keyword → STRICT +0.4. Semantic intent aligns (restructuring document content).

---

### T05.02 — Implement interactive mode checkpoints

**Roadmap Item ID(s):** R-028
**Why:** Interactive mode allows users to override decisions at key pipeline stages, providing human-in-the-loop control.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0031
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0031/spec.md`

**Deliverables:**
1. Interactive mode checkpoint logic — 4 pause points (after diff analysis, after debate, after base selection, after refactoring plan) using AskUserQuestion; default non-interactive (auto-approve)

**Steps:**
1. **[PLANNING]** Review spec FR-004 interactive mode: 4 pause points and override capabilities
2. **[PLANNING]** Design checkpoint integration: where to insert pauses in the 5-step protocol
3. **[EXECUTION]** Implement checkpoint 1: after diff-analysis.md — user highlights priority areas
4. **[EXECUTION]** Implement checkpoint 2: after debate — user overrides convergence assessment
5. **[EXECUTION]** Implement checkpoint 3: after base selection — user overrides selected base
6. **[EXECUTION]** Implement checkpoint 4: after refactoring plan — user modifies plan before execution
7. **[VERIFICATION]** Test with `--interactive` (pauses) and without (auto-approves)
8. **[COMPLETION]** Interactive mode integrated into SKILL.md protocol flow

**Acceptance Criteria:**
- All 4 pause points trigger when `--interactive` flag is set
- Default (non-interactive) auto-approves all decisions with rationale in artifacts
- User overrides are respected and documented in output artifacts
- Pipeline resumes correctly after each checkpoint

**Validation:**
- Manual check: Run with `--interactive`, verify pause at each of 4 checkpoint positions
- Evidence: Artifact annotations showing "auto-approved" (default) or "user-overridden" (interactive)

**Dependencies:** T05.01
**Rollback:** Revert checkpoint logic
**Notes:** —

---

### T05.03 — Implement merge executor

**Roadmap Item ID(s):** R-029
**Why:** The merge executor applies the refactoring plan to the base document, producing the unified output artifact.
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
**Deliverable IDs:** D-0032
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0032/spec.md`

**Deliverables:**
1. Merge execution logic — dispatches merge-executor agent (T01.04) via Task tool with base variant + refactoring plan; agent applies each change methodically and maintains structural integrity

**Steps:**
1. **[PLANNING]** Review spec FR-002 Step 5 and merge-executor agent definition (T01.04)
2. **[PLANNING]** Design merge dispatch: pass base document + refactoring plan to merge-executor agent
3. **[EXECUTION]** Implement merge dispatch via Task tool targeting merge-executor agent
4. **[EXECUTION]** Implement result collection: receive merged document from agent
5. **[VERIFICATION]** Verify merged document preserves base structure while incorporating planned changes
6. **[COMPLETION]** Merge execution integrated into protocol

**Acceptance Criteria:**
- Merge-executor agent receives correct inputs (base + plan)
- Each planned change from refactoring plan is applied
- Base document structure preserved after merge
- Merged output written to correct path per FR-005

**Validation:**
- Manual check: Compare merged output against base + refactoring plan, verify changes applied
- Evidence: Merged output file with planned improvements integrated

**Dependencies:** T05.01, T01.04 (merge-executor agent)
**Rollback:** Discard merged output, retain base + plan for manual execution
**Notes:** Tier conflict: "merge" → EXEMPT (git keyword), "implement" → STANDARD. Resolved: context is document merge, not git. STANDARD applied.

---

### T05.04 — Implement provenance annotation system

**Roadmap Item ID(s):** R-030
**Why:** Provenance annotations track which source contributed each section of the merged output, enabling auditability.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0033
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0033/spec.md`

**Deliverables:**
1. Provenance annotation system — HTML comments in merged output: `<!-- Source: Variant N, Section X.Y -->` for each section with non-base origin

**Steps:**
1. **[PLANNING]** Review spec Section FR-002 Step 5 provenance requirement
2. **[PLANNING]** Design annotation format: HTML comments with variant ID and section reference
3. **[EXECUTION]** Implement annotation insertion: for each merged section, add source attribution comment
4. **[EXECUTION]** Tag base-origin sections as "Base" and non-base sections with their source variant
5. **[VERIFICATION]** Verify every non-base section in merged output has a provenance annotation
6. **[COMPLETION]** Provenance system integrated into merge executor workflow

**Acceptance Criteria:**
- Every section in merged output from a non-base variant has a provenance annotation
- Annotation format: `<!-- Source: Variant N, Section X.Y -->`
- Base-origin sections optionally annotated as `<!-- Source: Base -->`
- Annotations are non-intrusive (HTML comments, invisible in rendered markdown)

**Validation:**
- Manual check: Search merged output for `<!-- Source:` comments, verify coverage
- Evidence: Merged output with provenance annotations for all incorporated changes

**Dependencies:** T05.03
**Rollback:** Strip annotations from merged output
**Notes:** —

---

### T05.05 — Implement post-merge consistency validation

**Roadmap Item ID(s):** R-031
**Why:** Post-merge validation catches structural corruption, broken references, and introduced contradictions before output.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0034
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0034/spec.md`

**Deliverables:**
1. Post-merge validation checks — structural integrity (valid headings, no orphaned sections), internal reference resolution, contradiction re-scan

**Steps:**
1. **[PLANNING]** Review spec FR-002 Step 5 validation requirements
2. **[PLANNING]** Define 3 validation checks: structure, references, contradictions
3. **[EXECUTION]** Implement structural integrity check: valid heading hierarchy, no orphaned subsections
4. **[EXECUTION]** Implement reference resolution: internal cross-references all resolve
5. **[EXECUTION]** Implement contradiction re-scan: no new contradictions introduced by merge
6. **[VERIFICATION]** Test with a deliberately corrupted merge to verify detection
7. **[COMPLETION]** Validation integrated as final gate before output

**Acceptance Criteria:**
- Structural integrity check catches orphaned sections and heading gaps
- Internal reference check identifies broken cross-references
- Contradiction re-scan detects newly introduced conflicts
- Validation failure triggers FR-006 error handling (preserve artifacts, flag failure)

**Validation:**
- Manual check: Introduce a deliberate structural error, verify detection
- Evidence: Validation report showing pass/fail for each check

**Dependencies:** T05.03
**Rollback:** Retain unvalidated output with validation report
**Notes:** —

---

### Checkpoint: Phase 5 / Tasks T05.01–T05.05

**Purpose:** Verify merge pipeline produces valid output before artifact generation and contract implementation.
**Checkpoint Report Path:** `.dev/releases/current/v1.7-adversarial/checkpoints/CP-P05-T01-T05.md`
**Verification:**
- Refactoring plan covers all identified strengths and weaknesses
- Merge executor produces structurally valid output
- Provenance annotations present for all incorporated changes
**Exit Criteria:**
- Merged output passes all 3 post-merge validation checks
- All non-base strengths from base-selection.md are incorporated
- Interactive mode checkpoint logic tested

---

### T05.06 — Generate refactor-plan.md and merge-log.md artifacts

**Roadmap Item ID(s):** R-032
**Why:** Process artifacts provide transparency and enable manual recovery if merge fails.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** None
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0035, D-0036
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0035/spec.md`
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0036/spec.md`

**Deliverables:**
1. refactor-plan.md — per spec Section 8.4 template: overview, planned changes with rationale, changes not made, review status
2. merge-log.md — Step 5 execution log: each applied change, structural validation results, issues encountered

**Steps:**
1. **[PLANNING]** Review spec Section 8.4 refactor-plan template
2. **[PLANNING]** Design merge-log format: per-change entry with before/after, validation results
3. **[EXECUTION]** Generate refactor-plan.md from T05.01 output
4. **[EXECUTION]** Generate merge-log.md from T05.03 execution trace
5. **[VERIFICATION]** Verify both artifacts are complete and match templates
6. **[COMPLETION]** Both files written to `<output-dir>/adversarial/`

**Acceptance Criteria:**
- refactor-plan.md matches spec Section 8.4 template with all required sections
- merge-log.md documents each applied change with before/after state
- Both files written to correct paths per FR-005
- Combined artifacts enable manual recovery of merge if needed

**Validation:**
- Manual check: Inspect both artifacts for completeness
- Evidence: Both files exist in adversarial/ directory with expected content

**Dependencies:** T05.01, T05.03
**Rollback:** Delete generated artifacts
**Notes:** —

---

### T05.07 — Implement return contract (FR-007)

**Roadmap Item ID(s):** R-033
**Why:** The return contract enables other commands (sc:roadmap, sc:design) to consume adversarial results programmatically.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0037
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0037/spec.md`

**Deliverables:**
1. Return contract implementation — returns: path to merged output, final convergence score, path to adversarial/ artifacts directory, status (success/partial/failed), list of unresolved conflicts

**Steps:**
1. **[PLANNING]** Review spec FR-007 return contract fields
2. **[PLANNING]** Design return structure: 5 fields matching FR-007
3. **[EXECUTION]** Implement return data collection from pipeline state
4. **[EXECUTION]** Implement status determination: success (all steps complete), partial (some steps failed), failed (pipeline aborted)
5. **[VERIFICATION]** Verify all 5 return fields populated correctly for success, partial, and failed scenarios
6. **[COMPLETION]** Return contract integrated into SKILL.md protocol exit

**Acceptance Criteria:**
- All 5 fields from FR-007 populated: merged output path, convergence score, artifacts dir path, status, unresolved conflicts
- Status correctly reflects pipeline outcome (success/partial/failed)
- Return contract usable by sc:roadmap v2 integration pattern (spec Section 7.1)
- Unresolved conflicts list is empty for successful pipelines

**Validation:**
- Manual check: Run pipeline, verify return contract contains all 5 fields with correct values
- Evidence: Return contract output with all fields populated

**Dependencies:** T05.03, T05.05
**Rollback:** Revert contract logic
**Notes:** —

---

### Checkpoint: End of Phase 5

**Purpose:** Gate check — merge pipeline must produce complete output before integration phase.
**Checkpoint Report Path:** `.dev/releases/current/v1.7-adversarial/checkpoints/CP-P05-END.md`
**Verification:**
- Merged output produced with provenance annotations
- refactor-plan.md and merge-log.md artifacts generated
- Return contract returns all 5 FR-007 fields
**Exit Criteria:**
- Phase 5 deliverables D-0030 through D-0037 all produced
- Post-merge validation passes all 3 checks
- Ready to begin Phase 6 integration

---

## Phase 6: Integration, Polish & Validation

Wire everything together: error handling, Mode B generation, MCP integration, framework registration, and end-to-end validation.

### T06.01 — Implement error handling matrix (FR-006)

**Roadmap Item ID(s):** R-034
**Why:** Robust error handling ensures the pipeline degrades gracefully across 5 failure scenarios defined in the spec.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0038
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0038/spec.md`

**Deliverables:**
1. Error handling matrix — implements all 5 scenarios from FR-006: agent failure (retry + N-1), similar variants (<10% diff → skip debate), non-convergence (force-select by score), invalid merge (preserve artifacts), single variant (abort with warning)

**Steps:**
1. **[PLANNING]** Review spec FR-006 error handling table: 5 scenarios with behaviors
2. **[PLANNING]** Map each scenario to pipeline insertion point
3. **[EXECUTION]** Implement agent failure: retry once, then proceed with N-1 variants (minimum 2)
4. **[EXECUTION]** Implement similarity detection: <10% diff → skip debate, select either as base
5. **[EXECUTION]** Implement non-convergence: force-select by score after max rounds, flag for review
6. **[EXECUTION]** Implement invalid merge: preserve all artifacts, return partial status with refactor-plan.md
7. **[EXECUTION]** Implement single variant: abort adversarial process, return variant as-is with warning
8. **[VERIFICATION]** Test each error scenario independently
9. **[COMPLETION]** Error handling integrated throughout pipeline

**Acceptance Criteria:**
- All 5 FR-006 scenarios handled with correct behavior
- Minimum-2-variants constraint enforced (single variant → abort)
- Failed pipeline preserves all artifacts for manual recovery
- Error conditions documented in appropriate output artifacts

**Validation:**
- Manual check: Trigger each of the 5 error scenarios, verify correct handling
- Evidence: Error handling tested for all 5 scenarios with expected outcomes

**Dependencies:** T05.07 (full pipeline must exist to add error handling)
**Rollback:** Revert error handling logic
**Notes:** —

---

### T06.02 — Implement Mode B variant generation

**Roadmap Item ID(s):** R-035
**Why:** Mode B generates variant artifacts from a source file using different agent/model configurations before running the comparison pipeline.
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
**Deliverable IDs:** D-0039
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0039/spec.md`

**Deliverables:**
1. Mode B variant generation logic — parallel dispatch of Task agents per `--agents` spec; each agent generates an artifact from `--source` using `--generate` type; outputs saved as `variant-N-<model>-<persona>.md`

**Steps:**
1. **[PLANNING]** Review spec FR-001 Mode B and NFR-001 parallel generation requirement
2. **[PLANNING]** Design parallel dispatch: one Task agent per `--agents` spec entry
3. **[EXECUTION]** Implement parallel agent dispatch: each agent receives source file + generation type + their persona/instruction
4. **[EXECUTION]** Implement result collection and naming: `variant-N-<model>-<persona>.md` per FR-005
5. **[EXECUTION]** Wire generated variants into the T02.02 variant loading pipeline (replacing Mode B placeholder)
6. **[VERIFICATION]** Test with 2 agents generating roadmap variants from a test spec
7. **[COMPLETION]** Mode B generation integrated and wired to pipeline entry

**Acceptance Criteria:**
- All agents dispatched in parallel (NFR-001)
- Each agent produces a variant artifact from the source
- Variant naming follows FR-005 convention: `variant-N-<model>-<persona>.md`
- Generated variants feed into the existing diff analysis pipeline (T02.02+)

**Validation:**
- Manual check: Run Mode B with 2 agents, verify 2 variant files produced with correct names
- Evidence: Variant files in adversarial/ directory with generated content

**Dependencies:** T02.02 (replaces Mode B placeholder), T03.01 (agent instantiation)
**Rollback:** Revert generation logic, restore Mode B placeholder
**Notes:** —

---

### T06.03 — Implement MCP integration layer

**Roadmap Item ID(s):** R-036
**Why:** MCP servers enhance debate quality (Sequential), enable cross-session learning (Serena), and provide domain validation (Context7).
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
**Deliverable IDs:** D-0040
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0040/spec.md`

**Deliverables:**
1. MCP integration layer — Sequential for debate scoring/convergence analysis (Steps 2-4), Serena for memory persistence (Step 5), Context7 for domain pattern validation (Step 5); circuit breaker fallbacks per spec Section 10

**Steps:**
1. **[PLANNING]** Review spec Section 10 MCP integration table and circuit breaker requirements
2. **[PLANNING]** Map MCP usage to pipeline steps: Sequential (2-4), Serena (5), Context7 (5)
3. **[EXECUTION]** Integrate Sequential thinking for debate scoring and convergence analysis
4. **[EXECUTION]** Integrate Serena memory persistence for adversarial outcomes
5. **[EXECUTION]** Integrate Context7 for domain pattern validation during merge
6. **[EXECUTION]** Implement circuit breaker: if Sequential unavailable, fall back with depth reduction (deep→standard, standard→quick)
7. **[VERIFICATION]** Test with MCP servers available and unavailable (fallback path)
8. **[COMPLETION]** MCP integration documented in SKILL.md

**Acceptance Criteria:**
- Sequential used for debate scoring in Steps 2-4
- Serena persists adversarial outcomes for cross-session learning
- Context7 validates domain patterns during merge
- Circuit breaker correctly reduces depth when Sequential unavailable

**Validation:**
- Manual check: Verify MCP calls in pipeline logs for available servers
- Evidence: Pipeline runs successfully with and without MCP servers (fallback tested)

**Dependencies:** T05.07 (full pipeline)
**Rollback:** Remove MCP integration, pipeline runs with native reasoning only
**Notes:** —

---

### T06.04 — Framework registration

**Roadmap Item ID(s):** R-037
**Why:** sc:adversarial must be registered in framework configuration files for routing, auto-activation, and persona integration.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STRICT`
**Confidence:** `[██████████] 78%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Sub-agent (quality-engineer)
**MCP Requirements:** Required: Sequential, Serena
**Fallback Allowed:** No
**Sub-Agent Delegation:** Recommended
**Deliverable IDs:** D-0041, D-0042
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0041/spec.md`
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0042/spec.md`

**Deliverables:**
1. COMMANDS.md update — add sc:adversarial entry with auto-persona, MCP preferences, tools, flags
2. ORCHESTRATOR.md update — add routing rules for adversarial pattern in master routing table

**Steps:**
1. **[PLANNING]** Review COMMANDS.md structure for existing command entries
2. **[PLANNING]** Review ORCHESTRATOR.md routing table format
3. **[EXECUTION]** Add sc:adversarial entry to COMMANDS.md following existing pattern
4. **[EXECUTION]** Add adversarial routing rules to ORCHESTRATOR.md master routing table
5. **[VERIFICATION]** Verify entries are syntactically consistent with existing entries
6. **[COMPLETION]** Framework files updated

**Acceptance Criteria:**
- COMMANDS.md contains sc:adversarial with correct auto-persona, MCP, and tools
- ORCHESTRATOR.md routing table includes adversarial pattern matching
- Entries follow existing formatting and organizational patterns
- No existing entries broken by additions

**Validation:**
- Manual check: Verify new entries are syntactically consistent with neighbors
- Evidence: Framework files updated with correct entries

**Dependencies:** T01.01 (command definition provides entry content)
**Rollback:** Revert framework file changes
**Notes:** Tier classified STRICT: >2 files affected (+0.3 context booster). Modifying framework configuration files affects system-wide routing.

---

### Checkpoint: Phase 6 / Tasks T06.01–T06.05 (covers T06.01–T06.04 + T06.05 below)

**Purpose:** Verify all integration components before final E2E validation.
**Checkpoint Report Path:** `.dev/releases/current/v1.7-adversarial/checkpoints/CP-P06-T01-T05.md`
**Verification:**
- Error handling covers all 5 FR-006 scenarios
- Mode B generation produces valid variants
- Framework registration entries are syntactically correct
**Exit Criteria:**
- All error scenarios tested independently
- Mode B pipeline produces variants and feeds into debate
- MCP fallback paths verified

---

### T06.05 — End-to-end validation — Mode A

**Roadmap Item ID(s):** R-038
**Why:** E2E validation confirms the full pipeline works correctly with real input files in the compare-existing-files mode.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** end-to-end (+1)
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0043
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0043/evidence.md`

**Deliverables:**
1. E2E Mode A validation results — complete pipeline run comparing 2-3 real markdown files; all 6 artifacts produced; return contract valid

**Steps:**
1. **[PLANNING]** Select 2-3 real markdown files with known differences for test input
2. **[PLANNING]** Define expected outcomes: all 6 artifacts produced, return contract populated
3. **[EXECUTION]** Run full pipeline: `/sc:adversarial --compare file1.md,file2.md --depth standard`
4. **[EXECUTION]** Verify all artifacts: diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md, merge-log.md, merged output
5. **[VERIFICATION]** Validate return contract: merged path exists, convergence score reasonable, status = success
6. **[COMPLETION]** E2E Mode A test results documented

**Acceptance Criteria:**
- All 6 artifacts produced in adversarial/ directory
- Return contract contains all 5 FR-007 fields with valid values
- Merged output is structurally valid (passes post-merge validation)
- Pipeline completes within reasonable time (<5 min for standard depth)

**Validation:**
- Manual check: Inspect all 6 artifacts for completeness and correctness
- Evidence: Full artifact set produced from real input files

**Dependencies:** T06.01, T06.03
**Rollback:** N/A (validation only)
**Notes:** —

---

### T06.06 — End-to-end validation — Mode B

**Roadmap Item ID(s):** R-039
**Why:** E2E validation confirms the generate-then-compare pipeline works correctly with agent-generated variants.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** end-to-end (+1)
**Tier:** `STANDARD`
**Confidence:** `[██████████] 75%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Sequential, Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0044
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0044/evidence.md`

**Deliverables:**
1. E2E Mode B validation results — complete pipeline run generating 2 variants from a source spec with different model/persona combos; all artifacts produced

**Steps:**
1. **[PLANNING]** Select a source spec file for variant generation
2. **[PLANNING]** Define agent specs for test: e.g., `opus:architect,sonnet:security`
3. **[EXECUTION]** Run full pipeline: `/sc:adversarial --source spec.md --generate roadmap --agents opus:architect,sonnet:security`
4. **[EXECUTION]** Verify variants generated with correct naming convention
5. **[VERIFICATION]** Validate all artifacts produced and return contract valid
6. **[COMPLETION]** E2E Mode B test results documented

**Acceptance Criteria:**
- 2 variant files generated with correct naming (variant-1-opus-architect.md, etc.)
- All 6 artifacts produced from generated variants
- Return contract valid with status = success
- Pipeline handles agent-generated content correctly through all 5 steps

**Validation:**
- Manual check: Inspect generated variants and final merged output
- Evidence: Full artifact set produced from agent-generated variants

**Dependencies:** T06.02, T06.05
**Rollback:** N/A (validation only)
**Notes:** —

---

### T06.07 — Documentation and integration guide

**Roadmap Item ID(s):** R-040
**Why:** Documentation enables other developers and commands to correctly invoke and integrate with sc:adversarial.
**Effort:** `XS`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[██████████] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution
**MCP Requirements:** Preferred: Context7
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0045
**Artifacts (Intended Paths):**
- `.dev/releases/current/v1.7-adversarial/artifacts/D-0045/spec.md`

**Deliverables:**
1. Integration documentation — sc:roadmap v2 integration pattern (spec Section 7.1), usage examples, flag reference, return contract documentation

**Steps:**
1. **[PLANNING]** Review spec Section 7.1 sc:roadmap v2 integration patterns (multi-spec, multi-roadmap, combined)
2. **[PLANNING]** Identify documentation targets: command docs, integration guide
3. **[EXECUTION]** Document sc:roadmap v2 integration patterns with concrete invocation examples
4. **[EXECUTION]** Add additional usage examples covering common scenarios
5. **[VERIFICATION]** Verify documentation examples are syntactically correct and match implemented flags
6. **[COMPLETION]** Documentation complete

**Acceptance Criteria:**
- sc:roadmap v2 integration patterns documented for all 3 modes (multi-spec, multi-roadmap, combined)
- Usage examples match implemented command interface
- Return contract documentation enables programmatic integration
- Documentation follows existing project documentation patterns

**Validation:**
- Manual check: Verify example commands from documentation would execute correctly
- Evidence: Documentation files with integration patterns and examples

**Dependencies:** T06.05, T06.06
**Rollback:** Revert documentation changes
**Notes:** —

---

### Checkpoint: End of Phase 6

**Purpose:** Final gate — confirm complete pipeline is functional, documented, and integrated.
**Checkpoint Report Path:** `.dev/releases/current/v1.7-adversarial/checkpoints/CP-P06-END.md`
**Verification:**
- E2E Mode A and Mode B both pass with all artifacts produced
- Error handling tested for all 5 FR-006 scenarios
- Framework files updated and synced
**Exit Criteria:**
- Phase 6 deliverables D-0038 through D-0045 all produced
- `make sync-dev && make verify-sync` passes
- All success criteria from spec Section 11 met

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
