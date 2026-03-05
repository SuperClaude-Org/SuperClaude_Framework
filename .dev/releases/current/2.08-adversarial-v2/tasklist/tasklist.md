# TASKLIST — sc:adversarial v2.0 Implementation-Level Bug Detection

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.dev/releases/current/2.07-adversarial-v2/`
- **Tasklist Path**: `.dev/releases/current/2.07-adversarial-v2/tasklist/tasklist.md`
- **Execution Log Path**: `.dev/releases/current/2.07-adversarial-v2/execution-log.md`
- **Checkpoint Reports Path**: `.dev/releases/current/2.07-adversarial-v2/checkpoints/`
- **Evidence Root**: `.dev/releases/current/2.07-adversarial-v2/evidence/`
- **Artifacts Root**: `.dev/releases/current/2.07-adversarial-v2/artifacts/`
- **Feedback Log Path**: `.dev/releases/current/2.07-adversarial-v2/feedback-log.md`

---

## Source Snapshot

- Addresses structural gap in sc:adversarial debate pipeline: absence of operational state analysis at the implementation level.
- Root cause from v0.04 Adaptive Replay post-mortem: no debater was prompted to trace concrete data through proposed state machines.
- Adds three complementary control planes: structural challenge (Devil's Advocate + failure mode enumeration), state reasoning (scenario traces + invariant declaration/challenge), and process gating (state coverage factor + post-merge trace validation).
- Six milestones (M1-M6) phased in dependency order with linearized critical path: M1 -> M2 -> M3 -> M5 -> M6, with M4 parallelizable after M1.
- Implementation approach is layered integration: inject new phases and roles into existing orchestration flow rather than rebuilding pipeline.
- Complexity class: MEDIUM (0.440). Primary persona: architect. Consulting personas: analyzer, performance.

---

## Deterministic Rules Applied

- **Phase numbering**: 6 milestones (M1-M6) mapped sequentially to Phase 1 through Phase 6 with no gaps, per Section 4.3.
- **Task ID scheme**: Zero-padded `T<PP>.<TT>` format per Section 4.5. Tasks ordered by roadmap appearance within each phase.
- **Checkpoint cadence**: Checkpoint inserted after every 5 tasks within a phase and at the end of each phase, per Section 4.8.
- **Clarification task rule**: Clarification Tasks inserted where information is missing or tier confidence < 0.70, per Section 4.6.
- **Deliverable registry**: Global `D-####` IDs assigned in task order with deterministic artifact paths under `TASKLIST_ROOT/artifacts/`, per Section 5.1.
- **Effort mapping**: Computed from `EFFORT_SCORE` using text length, split status, keyword presence, and dependency words, per Section 5.2.1.
- **Risk mapping**: Computed from `RISK_SCORE` using security, migration, auth, performance, and cross-cutting keywords, per Section 5.2.2.
- **Tier classification**: Compliance tier computed using compound phrase overrides, keyword matching, context boosters, and priority resolution `STRICT > EXEMPT > LIGHT > STANDARD`, per Section 5.3.
- **Verification routing**: Verification method assigned per computed tier (Sub-agent for STRICT, Direct test for STANDARD, Quick check for LIGHT, Skip for EXEMPT), per Section 4.10.
- **MCP requirements**: Tool dependencies declared per tier, per Section 5.5.
- **Traceability matrix**: Single table connecting R-### to T<PP>.<TT> to D-#### with tier and confidence, per Section 9.
- **Policy fork resolution**: Where alternatives existed, chosen per tie-breaker order (Section 4.9): roadmap-stated approach preferred, then no new external dependencies, then reversible, then fewest interface changes.

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<=20 words) |
|---|---|---|
| R-001 | Phase 1 | M1: Devil's Advocate Agent -- Foundation -- P0 Critical -- Medium effort -- No dependencies |
| R-002 | Phase 1 | DA agent prompt template and role specification -- Agent produces structured analysis covering assumptions |
| R-003 | Phase 1 | Pipeline orchestration integration -- DA phase inserted before Round 1 -- DA analysis available to |
| R-004 | Phase 1 | DA concern resolution tracking and final report -- Pipeline produces a DA concern resolution matrix |
| R-005 | Phase 2 | M2: State Coverage Gate -- Process Gate -- P0 Critical -- Low effort -- Depends M1 |
| R-006 | Phase 2 | State coverage category taxonomy and classification logic -- Required categories defined: happy path, empty/zero |
| R-007 | Phase 2 | Modified convergence formula: convergence = (agreed_points / total_diff_points) * state_coverage_factor |
| R-008 | Phase 2 | Coverage gap reporting in pipeline output -- Pipeline output includes a coverage matrix showing which |
| R-009 | Phase 3 | M3: Concrete Scenario Traces -- Analysis Phase -- P1 High -- High effort -- Depends M1 |
| R-010 | Phase 3 | Scenario generation engine -- orchestrator produces 3-5 concrete input scenarios from diff analysis |
| R-011 | Phase 3 | Trace execution protocol -- each advocate traces each scenario step-by-step -- Trace output includes state |
| R-012 | Phase 3 | Divergence analysis and integration with convergence formula -- Unresolved divergences feed into the state coverage |
| R-013 | Phase 3 | Divergence detector for end-state mismatch -- Automated detection of divergent end-states across advocate traces |
| R-014 | Phase 4 | M4: Invariant Declaration and Challenge -- Formal Reasoning -- P1 High -- Medium effort -- |
| R-015 | Phase 4 | Invariant declaration protocol and schema -- Each advocate declares invariants in structured format: name, formal |
| R-016 | Phase 4 | Challenge round implementation -- Opposing advocates and DA construct input sequences targeting declared invariants |
| R-017 | Phase 4 | Invariant resolution and design modification protocol -- Advocates with violated invariants must modify design or |
| R-018 | Phase 5 | M5: Failure Mode Enumeration Phase -- Enumeration Phase -- P2 Standard -- Low effort -- |
| R-019 | Phase 5 | Failure mode enumeration prompt and output schema -- Each advocate enumerates >=3 failure modes per |
| R-020 | Phase 5 | Novelty scoring for failure mode findings -- Unique failure modes earn bonus debate weight -- |
| R-021 | Phase 5 | Integration with DA analysis -- cross-reference and gap detection -- DA cross-references advocate failure modes |
| R-022 | Phase 6 | M6: Post-Merge Trace Validation -- Validation Phase -- P2 Standard -- Medium effort -- Depends |
| R-023 | Phase 6 | Post-merge validation agent prompt and role specification -- Agent is distinct from all debate participants |
| R-024 | Phase 6 | Merge artifact detection and classification -- Agent compares trace results against expected end-states from M3 |
| R-025 | Phase 6 | Pipeline integration -- Step 5.5 insertion and convergence impact -- Merge artifacts reopen debate with |
| R-026 | Phase 6 | Provenance tagging and cross-artifact consistency check -- Each validated trace includes provenance tags attributing trace |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-002 | DA agent prompt template and role specification | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0001/spec.md` | M | Medium |
| D-0002 | T01.01 | R-002 | DA output schema (machine-parseable) | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0002/spec.md` | M | Medium |
| D-0003 | T01.01 | R-002 | DA severity taxonomy (critical/high/medium/low) | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0003/spec.md` | M | Medium |
| D-0004 | T01.02 | R-003 | DA phase integration into pipeline orchestration | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0004/spec.md` | M | Medium |
| D-0005 | T01.02 | R-003 | Advocate DA-concern response enforcement | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0005/evidence.md` | M | Medium |
| D-0006 | T01.03 | R-004 | DA concern resolution matrix | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0006/spec.md` | M | Medium |
| D-0007 | T01.03 | R-004 | DA final report with resolved/unresolved tracking | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0007/evidence.md` | M | Medium |
| D-0008 | T01.04 | R-001 | Regression test suite using v0.04 post-mortem bugs | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0008/evidence.md` | M | Medium |
| D-0009 | T02.01 | R-006 | State coverage category taxonomy | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0009/spec.md` | S | Low |
| D-0010 | T02.01 | R-006 | Classification logic mapping debate points to categories | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0010/spec.md` | S | Low |
| D-0011 | T02.02 | R-007 | Modified convergence formula with state_coverage_factor | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0011/spec.md` | S | Medium |
| D-0012 | T02.02 | R-007 | Deterministic factor computation logic | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0012/evidence.md` | S | Medium |
| D-0013 | T02.03 | R-008 | Coverage gap reporting in pipeline output | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0013/spec.md` | S | Low |
| D-0014 | T02.03 | R-008 | Coverage matrix with remediation suggestions | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0014/evidence.md` | S | Low |
| D-0015 | T03.01 | R-010 | Scenario generation engine | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0015/spec.md` | L | Medium |
| D-0016 | T03.01 | R-010 | Scenario output with concrete input values | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0016/evidence.md` | L | Medium |
| D-0017 | T03.02 | R-011 | Trace execution protocol and schema | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0017/spec.md` | L | Medium |
| D-0018 | T03.02 | R-011 | Tabular trace output format | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0018/spec.md` | L | Medium |
| D-0019 | T03.03 | R-012 | Divergence analysis with severity classification | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0019/spec.md` | L | Medium |
| D-0020 | T03.03 | R-012 | Convergence penalty integration for divergences | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0020/evidence.md` | L | Medium |
| D-0021 | T03.04 | R-013 | Automated divergence detector for end-state mismatch | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0021/spec.md` | L | Medium |
| D-0022 | T03.05 | R-009 | Depth-gating for scenario traces (--depth standard+) | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0022/spec.md` | M | Medium |
| D-0023 | T03.05 | R-009 | Early-exit logic when all scenarios converge | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0023/evidence.md` | M | Medium |
| D-0024 | T04.01 | R-015 | Invariant declaration protocol and schema | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0024/spec.md` | M | Medium |
| D-0025 | T04.01 | R-015 | v0/final invariant lifecycle with refinement protocol | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0025/spec.md` | M | Medium |
| D-0026 | T04.02 | R-016 | Challenge round implementation | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0026/spec.md` | M | Medium |
| D-0027 | T04.02 | R-016 | Challenge output format and violation flagging | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0027/evidence.md` | M | Medium |
| D-0028 | T04.03 | R-017 | Invariant resolution and design modification protocol | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0028/spec.md` | M | Medium |
| D-0029 | T04.03 | R-017 | Resolution decision logging in pipeline output | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0029/evidence.md` | M | Medium |
| D-0030 | T05.01 | R-019 | Failure mode enumeration prompt and output schema | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0030/spec.md` | M | Medium |
| D-0031 | T05.02 | R-020 | Novelty scoring logic for failure mode findings | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0031/spec.md` | M | Medium |
| D-0032 | T05.03 | R-021 | DA cross-reference and gap detection integration | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0032/spec.md` | M | Medium |
| D-0033 | T05.03 | R-021 | Invariant-violation priority flagging for failure modes | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0033/evidence.md` | M | Medium |
| D-0034 | T06.01 | R-023 | Post-merge validation agent prompt and role specification | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0034/spec.md` | M | Medium |
| D-0035 | T06.02 | R-024 | Merge artifact detection and classification logic | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0035/spec.md` | M | Medium |
| D-0036 | T06.02 | R-024 | Merge artifact report format | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0036/evidence.md` | M | Medium |
| D-0037 | T06.03 | R-025 | Step 5.5 pipeline insertion with convergence impact | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0037/spec.md` | M | Medium |
| D-0038 | T06.03 | R-025 | Re-debate trigger and cap logic (1 iteration max) | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0038/evidence.md` | M | Medium |
| D-0039 | T06.04 | R-026 | Provenance tagging for validated traces | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0039/spec.md` | M | Medium |
| D-0040 | T06.04 | R-026 | Cross-artifact consistency check for untraceable entries | STANDARD | Direct test execution | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0040/evidence.md` | M | Medium |

---

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---|---|---|
| 1 | Devil's Advocate Agent | T01.01-T01.04 | Permanent non-advocacy agent role producing structured adversarial analysis before Round 1 | STRICT: 0, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |
| 2 | State Coverage Gate | T02.01-T02.03 | Convergence formula enforces state coverage categories as mandatory gate | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 3 | Concrete Scenario Traces | T03.01-T03.05 | Advocates trace concrete scenarios step-by-step exposing divergent end-states | STRICT: 0, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 4 | Invariant Declaration and Challenge | T04.01-T04.03 | Formal invariant declarations with adversarial challenge rounds and resolution protocol | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 5 | Failure Mode Enumeration Phase | T05.01-T05.03 | Advocate-perspective failure analysis cross-referenced with DA findings and final invariants | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 6 | Post-Merge Trace Validation | T06.01-T06.04 | Bias-free validation agent catches merge artifacts through independent scenario tracing | STRICT: 0, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |

---

## Phase 1: Devil's Advocate Agent

Introduce a permanent, non-advocacy agent role into the adversarial debate pipeline. The DA operates before Round 1, identifying assumptions, constructing adversarial inputs, flagging under-specified state transitions, and enumerating degenerate inputs. This is the foundational component upon which all subsequent milestones depend.

### T01.01 -- DA Agent Prompt Template and Role Specification

**Roadmap Item ID(s):** R-002
**Why:** The DA agent is the foundational component that produces adversarial analysis consumed by all downstream milestones. Without a well-specified prompt template and output schema, subsequent phases (M2-M6) cannot function.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** performance (prompt engineering iteration implied), cross-cutting (analysis feeds all downstream milestones)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0001, D-0002, D-0003
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0001/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0002/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0003/spec.md`

**Deliverables:**
- DA agent prompt template producing structured analysis covering: assumptions per variant, adversarial input constructions, under-specified state transitions, degenerate input enumeration
- Machine-parseable DA output schema
- Severity taxonomy (critical, high, medium, low) with configurable convergence-blocking threshold (critical-only default)

**Steps:**
1. **[PLANNING]** Load existing adversarial pipeline orchestration code and identify prompt insertion points for the DA role
2. **[PLANNING]** Review v0.04 post-mortem bugs (index tracking stall, replay guard bypass) to derive DA prompt requirements for concrete state variable references
3. **[EXECUTION]** Define DA output schema covering: assumptions, adversarial inputs, under-specified transitions, degenerate inputs -- all machine-parseable
4. **[EXECUTION]** Implement severity taxonomy (critical/high/medium/low) with configurable threshold for convergence blocking
5. **[EXECUTION]** Author DA agent prompt template that requires concrete state variable references (not abstract claims) and produces output conforming to schema
6. **[VERIFICATION]** Validate DA prompt produces structured output against schema using v0.04 post-mortem bugs as regression test inputs
7. **[COMPLETION]** Document prompt template, output schema, and severity taxonomy in deliverable artifacts

**Acceptance Criteria:**
- DA prompt produces structured analysis covering all four required categories (assumptions, adversarial inputs, under-specified transitions, degenerate inputs) per variant
- DA concerns are classified by severity with critical-only default for convergence blocking; severity threshold is configurable via pipeline settings
- DA output schema is machine-parseable and validates against a formal schema definition
- Prompt template, output schema, and severity taxonomy are documented with worked examples

**Validation:**
- Manual check: Run DA prompt against v0.04 post-mortem inputs and verify structured output covers all four categories with concrete state variable references
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** None
**Rollback:** TBD (if not specified in roadmap)
**Notes:** DA output schema defined here becomes a versioned contract consumed by M2-M6. Schema changes require backward compatibility per roadmap risk R7. DA concerns capped at 10 per variant per roadmap mitigation.

---

### T01.02 -- Pipeline Orchestration Integration for DA Phase

**Roadmap Item ID(s):** R-003
**Why:** The DA analysis must be injected before Round 1 so that all advocates receive adversarial concerns before opening statements. Without orchestration integration, the DA role exists in isolation.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (pipeline integration affects all debate phases), performance (token consumption concern)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0004, D-0005
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0004/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0005/evidence.md`

**Deliverables:**
- DA phase inserted into pipeline orchestration before Round 1 with DA analysis available to all advocates
- Enforcement mechanism requiring advocates to explicitly address DA concerns, with unresolved critical concerns tagged as convergence blockers

**Steps:**
1. **[PLANNING]** Identify pipeline orchestration entry points and phase ordering mechanism
2. **[PLANNING]** Map DA output schema (from T01.01) to advocate input interface
3. **[EXECUTION]** Insert DA phase into orchestration flow before Round 1 -- DA analysis output is passed to all advocate agents
4. **[EXECUTION]** Implement orchestrator enforcement: advocates must explicitly address DA concerns in their responses
5. **[EXECUTION]** Tag unresolved DA concerns at critical severity as convergence blockers in pipeline state
6. **[VERIFICATION]** Run pipeline with DA phase active and verify advocates receive DA output, enforcement triggers on unaddressed concerns, and critical blockers propagate to pipeline state
7. **[COMPLETION]** Document integration points and enforcement behavior

**Acceptance Criteria:**
- DA analysis is available to all advocates before opening statements in pipeline execution
- Orchestrator enforces that advocates explicitly address DA concerns (non-compliance triggers re-prompt)
- Unresolved DA concerns at critical severity are tagged as convergence blockers in pipeline state
- Integration points and enforcement behavior documented with pipeline flow diagram

**Validation:**
- Manual check: Execute pipeline run and verify DA analysis appears in advocate input, enforcement triggers on unaddressed concerns
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T01.01
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Non-critical DA concerns are surfaced in the final report but do not block convergence by default per roadmap.

---

### T01.03 -- DA Concern Resolution Tracking and Final Report

**Roadmap Item ID(s):** R-004
**Why:** Without resolution tracking, DA concerns have no lifecycle -- they are raised but never formally resolved or escalated. The resolution matrix and final report close this loop and feed the convergence formula in M2.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (resolution status feeds M2 convergence formula)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0006, D-0007
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0006/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0007/evidence.md`

**Deliverables:**
- DA concern resolution matrix produced at debate conclusion with each concern marked resolved, partially-resolved, or unresolved with severity level
- DA final report where unresolved critical concerns block convergence and feed M2 state coverage gate

**Steps:**
1. **[PLANNING]** Define resolution states (resolved, partially-resolved, unresolved) and their transitions during debate rounds
2. **[PLANNING]** Map resolution matrix output to M2 convergence formula input interface
3. **[EXECUTION]** Implement resolution tracking: DA receives advocate responses and updates concern status after each round
4. **[EXECUTION]** Implement final report generation: resolution matrix with severity, status, and resolution evidence per concern
5. **[EXECUTION]** Wire unresolved critical concerns as convergence blockers that feed M2
6. **[VERIFICATION]** Run pipeline end-to-end and verify resolution matrix is populated correctly, final report is generated, and unresolved critical concerns propagate as blockers
7. **[COMPLETION]** Document resolution tracking lifecycle and final report schema

**Acceptance Criteria:**
- Pipeline produces a DA concern resolution matrix at debate conclusion with each concern marked resolved, partially-resolved, or unresolved
- Each concern in the matrix includes its severity level and resolution evidence
- Unresolved critical concerns block convergence and are available as input to M2
- Resolution tracking lifecycle and final report schema documented

**Validation:**
- Manual check: Verify resolution matrix contains all DA concerns with correct status after a complete pipeline run
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T01.01, T01.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Resolution matrix is the primary handoff artifact to M2 (State Coverage Gate).

---

### T01.04 -- DA Regression Test Suite Using v0.04 Post-Mortem Bugs

**Roadmap Item ID(s):** R-001
**Why:** The roadmap identifies two specific bugs (index tracking stall, replay guard bypass) that escaped adversarial review. A regression test suite validates the DA agent catches these known bugs and prevents future regressions.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** performance (token budget monitoring), cross-cutting (regression suite validates entire DA pipeline)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0008
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0008/evidence.md`

**Deliverables:**
- Regression test suite that replays v0.04 post-mortem bugs (index tracking stall, replay guard bypass) through the DA pipeline and verifies both are flagged

**Steps:**
1. **[PLANNING]** Identify v0.04 post-mortem bug specifications (index tracking stall, replay guard bypass) and their concrete state variable manifestations
2. **[PLANNING]** Define regression test input format compatible with DA pipeline entry point
3. **[EXECUTION]** Construct regression test inputs that encode the two v0.04 bugs as pipeline scenarios
4. **[EXECUTION]** Implement regression test harness that runs DA pipeline against these inputs and checks for flagged concerns
5. **[EXECUTION]** Verify both bugs are flagged by DA analysis with concrete state variable references
6. **[VERIFICATION]** Execute regression test suite and confirm binary pass/fail: both bugs must be flagged (success criterion SC2)
7. **[COMPLETION]** Document regression test suite with input specifications and expected outputs

**Acceptance Criteria:**
- Regression test suite contains test cases for both v0.04 post-mortem bugs (index tracking stall, replay guard bypass)
- Both bugs are caught by the enhanced DA pipeline when replayed as regression inputs (SC2)
- Regression tests produce binary pass/fail results with concrete state variable references in DA output
- Test suite documented with input specifications, expected outputs, and execution instructions

**Validation:**
- Manual check: Run regression test suite and verify both v0.04 bugs are flagged by DA with concrete state variable references
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T01.01, T01.02, T01.03
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Token usage monitoring should be applied during first 5 regression test runs per roadmap risk mitigation. DA prompt must require concrete state variable references per risk R2 mitigation.

---

### Checkpoint: End of Phase 1

**Purpose:** Validate that the Devil's Advocate agent is fully functional, integrated into the pipeline, and catches known regression bugs before proceeding to convergence formula modifications.
**Checkpoint Report Path:** `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P01-END.md`

**Verification:**
- DA agent produces structured adversarial analysis conforming to output schema with severity classification
- Pipeline orchestration inserts DA phase before Round 1 with advocate enforcement and convergence blocker propagation
- Regression test suite passes: both v0.04 post-mortem bugs flagged by DA analysis

**Exit Criteria:**
- All Phase 1 deliverables (D-0001 through D-0008) are complete with evidence artifacts
- DA output schema is versioned and documented as a contract for downstream milestones
- Token consumption of DA phase measured and within acceptable range (monitored, not yet gated)

---

## Phase 2: State Coverage Gate

Modify the convergence formula to include a state coverage factor, transforming DA concerns and scenario coverage from advisory to enforceable. The gate prevents debate convergence without addressing required scenario categories.

### T02.01 -- State Coverage Category Taxonomy and Classification Logic

**Roadmap Item ID(s):** R-006
**Why:** The convergence gate requires a defined set of coverage categories to enforce. Without a taxonomy, the gate has no criteria to evaluate against.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 82%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0009, D-0010
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0009/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0010/spec.md`

**Deliverables:**
- State coverage category taxonomy: required categories (happy path, empty/zero inputs, boundary conditions) and conditional categories (filter divergence, error paths, concurrent/reentrant)
- Classification logic that maps debate points to coverage categories

**Steps:**
1. **[PLANNING]** Review DA concern taxonomy (from T01.01) to align coverage categories with DA output structure
2. **[PLANNING]** Define required vs conditional category distinction and activation rules for conditional categories
3. **[EXECUTION]** Implement category taxonomy: required (happy path, empty/zero inputs, boundary conditions) and conditional (filter divergence, error paths, concurrent/reentrant)
4. **[EXECUTION]** Implement classification logic that maps debate points to categories using keyword and structural matching
5. **[VERIFICATION]** Test classification logic against synthetic debate points and verify correct category assignment
6. **[COMPLETION]** Document taxonomy and classification logic with examples

**Acceptance Criteria:**
- Required categories defined: happy path, empty/zero inputs, boundary conditions
- Conditional categories defined: filter divergence, error paths, concurrent/reentrant with activation rules
- Classification logic maps debate points to categories deterministically
- Taxonomy is extensible by design for quarterly review cycles (per roadmap risk mitigation)

**Validation:**
- Manual check: Run classification logic against 5 synthetic debate points and verify category assignments
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T01.01 (DA concern taxonomy feeds coverage categories)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Taxonomy is extensible per roadmap. Quarterly reviews against escaped bugs planned per risk mitigation.

---

### T02.02 -- Modified Convergence Formula with State Coverage Factor

**Roadmap Item ID(s):** R-007
**Why:** The convergence formula must be modified to include a multiplicative state coverage factor so that debates cannot converge without addressing required categories. This is the enforcement mechanism for the coverage gate.
**Effort:** `S`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (convergence formula affects all debates), performance (factor computation must be deterministic and auditable)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0011, D-0012
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0011/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0012/evidence.md`

**Deliverables:**
- Modified convergence formula: `convergence = (agreed_points / total_diff_points) * state_coverage_factor` where factor < 1.0 when required categories are unaddressed
- Deterministic and auditable factor computation logic

**Steps:**
1. **[PLANNING]** Identify current convergence formula location in pipeline code and its existing inputs
2. **[PLANNING]** Define state_coverage_factor computation: how unaddressed required categories reduce the factor below 1.0
3. **[EXECUTION]** Implement multiplicative state_coverage_factor in convergence formula
4. **[EXECUTION]** Ensure factor computation is deterministic (same inputs produce same factor) and auditable (factor breakdown logged)
5. **[EXECUTION]** Implement `--override-coverage` escape hatch (logged and auditable) per roadmap risk mitigation
6. **[VERIFICATION]** Verify on 5 synthetic debates that missing required categories produce factor < 1.0 and prevent convergence (SC3)
7. **[COMPLETION]** Document formula, factor computation, and override mechanism

**Acceptance Criteria:**
- state_coverage_factor is < 1.0 when any required category is unaddressed
- Factor computation is deterministic and produces an auditable breakdown in pipeline output
- Convergence threshold cannot be met without all required categories covered
- `--override-coverage` escape hatch is available, logged, and auditable

**Validation:**
- Manual check: Run 5 synthetic debates with intentionally missing categories and verify factor < 1.0 (SC3)
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T02.01, T01.03 (DA unresolved concerns reduce coverage factor)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap decision: multiplicative factor chosen over additive bonus or hard gate. Multiplicative factor degrades gracefully. Factor weight tuning planned based on first 10 pipeline runs.

---

### T02.03 -- Coverage Gap Reporting in Pipeline Output

**Roadmap Item ID(s):** R-008
**Why:** The coverage gate needs to surface its findings in the pipeline output so that users can see which categories are addressed, partially addressed, or missing, along with suggested remediation.
**Effort:** `S`
**Risk:** `Low`
**Risk Drivers:** None matched
**Tier:** `STANDARD`
**Confidence:** `[████████--] 82%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0013, D-0014
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0013/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0014/evidence.md`

**Deliverables:**
- Coverage gap reporting integrated into pipeline output showing category-level addressed/partially-addressed/missing status
- Coverage matrix with missing required categories surfaced as explicit blockers with suggested remediation

**Steps:**
1. **[PLANNING]** Define coverage matrix output format (category, status, evidence, remediation suggestion)
2. **[PLANNING]** Identify pipeline output insertion point for coverage report
3. **[EXECUTION]** Implement coverage matrix generation from classification logic output (T02.01) and convergence factor state (T02.02)
4. **[EXECUTION]** Implement remediation suggestion generation for missing required categories
5. **[VERIFICATION]** Verify coverage report appears in pipeline output with correct category statuses and remediation suggestions
6. **[COMPLETION]** Document coverage report format and remediation suggestion logic

**Acceptance Criteria:**
- Pipeline output includes coverage matrix showing which categories are addressed, partially addressed, or missing
- Missing required categories are surfaced as explicit blockers with suggested remediation
- Coverage report is generated deterministically from classification and convergence state
- Report format and remediation logic documented

**Validation:**
- Manual check: Run pipeline and verify coverage matrix appears with correct statuses for each category
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T02.01, T02.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** None.

---

### Checkpoint: End of Phase 2

**Purpose:** Validate that the state coverage gate enforces required scenario categories in the convergence formula and produces actionable gap reporting before proceeding to scenario trace implementation.
**Checkpoint Report Path:** `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P02-END.md`

**Verification:**
- State coverage taxonomy is defined with required and conditional categories, and classification logic maps debate points correctly
- Modified convergence formula with multiplicative state_coverage_factor prevents convergence when required categories are unaddressed (SC3 verified on 5 synthetic debates)
- Coverage gap reporting produces correct matrix with remediation suggestions in pipeline output

**Exit Criteria:**
- All Phase 2 deliverables (D-0009 through D-0014) are complete with evidence artifacts
- Convergence formula change is backward-compatible with existing pipeline runs
- `--override-coverage` escape hatch tested and audit-logged

---

## Phase 3: Concrete Scenario Traces

Add a Scenario Traces debate round type where each advocate traces concrete input scenarios step-by-step, showing state variable values at each transition. This grounds the debate in operational reality and exposes divergent end-states that abstract discussion misses. Scenario traces are gated behind `--depth standard` or deeper.

### T03.01 -- Scenario Generation Engine

**Roadmap Item ID(s):** R-010
**Why:** Scenario traces require concrete input scenarios derived from diff analysis. The generation engine produces 3-5 scenarios covering required categories (happy path, boundary conditions, filter/transform, temporal edge cases, adversarial inputs from DA analysis).
**Effort:** `L`
**Risk:** `Medium`
**Risk Drivers:** performance (token-expensive scenario generation), cross-cutting (scenarios feed M5 and M6)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0015, D-0016
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0015/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0016/evidence.md`

**Deliverables:**
- Scenario generation engine that produces 3-5 concrete input scenarios from diff analysis
- Scenario output with concrete input values (not abstract descriptions) covering: happy path, boundary conditions, filter/transform, temporal edge cases, adversarial inputs from DA

**Steps:**
1. **[PLANNING]** Review DA analysis output schema (T01.01) to identify adversarial input sources for scenario generation
2. **[PLANNING]** Define scenario generation algorithm: diff analysis -> category mapping -> concrete value selection
3. **[EXECUTION]** Implement scenario generation engine that analyzes pipeline diff and produces 3-5 scenarios with concrete input values
4. **[EXECUTION]** Implement category coverage: happy path, boundary conditions, filter/transform, temporal edge cases, adversarial inputs (sourced from DA)
5. **[EXECUTION]** Enforce concrete input values in scenario output -- reject abstract descriptions
6. **[VERIFICATION]** Verify engine produces 3-5 scenarios with concrete values covering required categories against test diffs
7. **[COMPLETION]** Document engine logic, scenario format, and category mapping

**Acceptance Criteria:**
- Engine produces 3-5 concrete input scenarios from diff analysis per pipeline run
- Scenarios cover: happy path, boundary conditions, filter/transform, temporal edge cases, adversarial inputs from DA analysis (M1)
- Scenarios include concrete input values, not abstract descriptions
- Engine logic and scenario format documented with examples

**Validation:**
- Manual check: Run engine against a test diff and verify 3-5 scenarios produced with concrete values covering required categories
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T01.01 (DA adversarial inputs are primary source for scenario generation), T02.01 (coverage categories inform scenario categories)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Scenario count gated by depth: 3 at standard, 5 at deep per roadmap decision.

---

### T03.02 -- Trace Execution Protocol

**Roadmap Item ID(s):** R-011
**Why:** Each advocate must trace each scenario step-by-step with state variable values at each transition. This is the core mechanism that grounds debate in operational reality and enables automated divergence detection.
**Effort:** `L`
**Risk:** `Medium`
**Risk Drivers:** performance (token-expensive trace execution), cross-cutting (trace format must be consistent for automated analysis)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0017, D-0018
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0017/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0018/spec.md`

**Deliverables:**
- Trace execution protocol requiring each advocate to trace each scenario step-by-step
- Tabular trace output format: step / state variable / value per variant, with divergent end-states automatically flagged

**Steps:**
1. **[PLANNING]** Define strict trace output schema: tabular format with step number, state variable name, value per variant
2. **[PLANNING]** Design orchestrator validation: format checking before divergence analysis, reject malformed traces with re-prompt
3. **[EXECUTION]** Implement trace execution protocol: each advocate receives scenarios and produces tabular trace output per scenario
4. **[EXECUTION]** Implement orchestrator schema validation: reject malformed traces, re-prompt advocate
5. **[EXECUTION]** Implement automatic flagging of divergent end-states across advocate traces
6. **[VERIFICATION]** Run protocol against test scenarios with known divergences and verify format compliance and divergence flagging
7. **[COMPLETION]** Document trace protocol, output schema, and validation rules

**Acceptance Criteria:**
- Trace output includes state variable values at each step in tabular format (step / state variable / value per variant)
- Divergent end-states are automatically flagged as unresolved divergences
- Orchestrator validates trace format before divergence analysis and rejects malformed traces with re-prompt
- Protocol and schema documented with worked example

**Validation:**
- Manual check: Run protocol against test scenarios and verify tabular format, divergence flagging, and malformed trace rejection
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T03.01 (scenarios feed trace execution)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Strict output schema enforcement per roadmap risk R4 mitigation.

---

### T03.03 -- Divergence Analysis and Convergence Formula Integration

**Roadmap Item ID(s):** R-012
**Why:** Divergent end-states from scenario traces must feed into the state coverage factor (M2) so that unresolved divergences reduce convergence. Divergences are classified by severity to influence convergence penalty magnitude.
**Effort:** `L`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (divergences affect convergence formula system-wide)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0019, D-0020
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0019/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0020/evidence.md`

**Deliverables:**
- Divergence analysis with severity classification (data loss, incorrect output, stall, crash)
- Convergence penalty integration: unresolved divergences feed into state_coverage_factor (M2) with severity-scaled penalties

**Steps:**
1. **[PLANNING]** Define severity classification taxonomy for divergences: data loss, incorrect output, stall, crash
2. **[PLANNING]** Define convergence penalty formula: how divergence severity maps to state_coverage_factor reduction
3. **[EXECUTION]** Implement divergence severity classification from trace comparison output
4. **[EXECUTION]** Implement convergence penalty integration: divergence findings reduce state_coverage_factor proportional to severity
5. **[VERIFICATION]** Verify on synthetic traces with injected divergences that severity classification is correct and convergence penalty is applied (SC4)
6. **[COMPLETION]** Document divergence classification taxonomy and penalty integration logic

**Acceptance Criteria:**
- Unresolved divergences feed into the state coverage factor (M2) as convergence penalties
- Divergences are classified by severity: data loss, incorrect output, stall, crash
- Severity classification influences convergence penalty magnitude deterministically
- Classification taxonomy and penalty logic documented

**Validation:**
- Manual check: Inject known divergences into 10 test scenarios and verify >=90% detection rate with correct severity (SC4)
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T03.02 (trace output feeds divergence analysis), T02.02 (convergence formula accepts divergence input)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** None.

---

### T03.04 -- Divergence Detector for End-State Mismatch

**Roadmap Item ID(s):** R-013
**Why:** An independent binary divergence detector provides a fast-path signal before qualitative severity analysis. This detector operates independently from the severity classification in T03.03, catching end-state mismatches as convergence input.
**Effort:** `L`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (detector output feeds convergence and downstream milestones)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0021
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0021/spec.md`

**Deliverables:**
- Automated divergence detector that compares end-states across advocate traces and produces binary divergence signal (divergent / convergent) per scenario, independent of severity classification

**Steps:**
1. **[PLANNING]** Define end-state comparison algorithm: how to determine if advocate end-states match or diverge
2. **[PLANNING]** Clarify interface with T03.03: detector provides binary signal before qualitative severity analysis
3. **[EXECUTION]** Implement automated divergence detector that compares final state variable values across advocate traces per scenario
4. **[EXECUTION]** Output binary divergence signal (divergent / convergent) per scenario, surfaced as convergence input
5. **[VERIFICATION]** Test detector against traces with known convergent and divergent end-states; verify correct binary classification
6. **[COMPLETION]** Document detector algorithm and interface with severity classification

**Acceptance Criteria:**
- Automated detection of divergent end-states across advocate traces per scenario
- Divergent end-states flagged as unresolved and surfaced as convergence input
- Detector operates independently from severity classification in T03.03, providing binary signal before qualitative analysis
- Algorithm documented with convergent/divergent test cases

**Validation:**
- Manual check: Run detector against traces with known convergent and divergent end-states and verify correct binary output
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T03.02 (trace output feeds detector)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** None.

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.04

**Purpose:** Validate scenario generation, trace execution, divergence analysis, and detection are functional before implementing depth-gating and performance controls.
**Checkpoint Report Path:** `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P03-T01-T04.md`

**Verification:**
- Scenario generation engine produces 3-5 concrete scenarios with concrete input values covering required categories
- Trace execution protocol enforces tabular format and rejects malformed traces
- Divergence detector and severity analysis correctly identify and classify divergences in synthetic test cases

**Exit Criteria:**
- Deliverables D-0015 through D-0021 are complete with evidence artifacts
- Divergence detection rate >=90% on synthetically injected divergences (SC4)
- Trace output schema is stable and consumed correctly by divergence analysis

---

### T03.05 -- Depth-Gating and Performance Controls for Scenario Traces

**Roadmap Item ID(s):** R-009
**Why:** Scenario traces are token-expensive. Depth-gating ensures traces only activate at `--depth standard` or deeper, and early-exit logic prevents unnecessary token consumption when all scenarios converge early.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** performance (token budget management is primary concern)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0022, D-0023
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0022/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0023/evidence.md`

**Deliverables:**
- Depth-gating: scenario traces activate only at `--depth standard` or deeper (3 scenarios at standard, 5 at deep)
- Early-exit logic: when all scenarios converge at an intermediate step, trace execution terminates early to save tokens

**Steps:**
1. **[PLANNING]** Identify `--depth` flag integration points in pipeline orchestration
2. **[PLANNING]** Define early-exit condition: all scenarios have convergent end-states at intermediate evaluation point
3. **[EXECUTION]** Implement depth-gating: scenario traces disabled below `--depth standard`; 3 scenarios at standard, 5 at deep
4. **[EXECUTION]** Implement early-exit logic: evaluate end-state convergence at intermediate points, terminate trace execution when all converge
5. **[EXECUTION]** Add token consumption monitoring for scenario trace phase
6. **[VERIFICATION]** Verify depth-gating activates/deactivates correctly at each depth level and early-exit triggers when all scenarios converge
7. **[COMPLETION]** Document depth-gating rules and early-exit conditions

**Acceptance Criteria:**
- Scenario traces are gated behind `--depth standard` and deeper, disabled at shallower depths
- 3 scenarios at standard depth, 5 scenarios at deep depth
- Early-exit triggers when all scenarios converge, saving token budget
- Depth-gating and early-exit documented with pipeline flag interaction

**Validation:**
- Manual check: Run pipeline at shallow, standard, and deep depths; verify trace activation/deactivation and early-exit behavior
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T03.01, T03.02, T03.03, T03.04
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap decision: gated at `--depth standard` and deeper. Always-on was too expensive for shallow/quick runs.

---

### Checkpoint: End of Phase 3

**Purpose:** Validate complete scenario trace pipeline including generation, execution, divergence detection, analysis, and performance controls before proceeding to invariant declaration.
**Checkpoint Report Path:** `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P03-END.md`

**Verification:**
- Full scenario trace pipeline executes end-to-end: generation -> trace execution -> divergence detection -> severity analysis -> convergence penalty
- Depth-gating and early-exit logic function correctly at all depth levels
- Token consumption increase measured against v1.0 baseline (target: <=40% increase at standard depth, SC7 partial)

**Exit Criteria:**
- All Phase 3 deliverables (D-0015 through D-0023) are complete with evidence artifacts
- SC4 verified: >=90% divergence detection rate on synthetically injected divergences
- Scenario trace output schema is stable and documented as input contract for M5 and M6

---

## Phase 4: Invariant Declaration and Challenge

Introduce formal reasoning discipline where advocates declare invariants their designs rely upon and opposing advocates plus the DA attempt to construct violating input sequences. M4 begins after M1 and produces v0 (draft) invariants. A mandatory refinement pass upgrades v0 to final after M3 scenario trace outputs are available. Only final invariants are consumed by M5.

### T04.01 -- Invariant Declaration Protocol and Schema with v0/Final Lifecycle

**Roadmap Item ID(s):** R-015
**Why:** Invariant declarations make correctness claims explicit and testable. The v0/final lifecycle enables parallel execution: v0 invariants start from DA analysis alone (M1), then refine to final using M3 scenario trace evidence.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (invariant schema consumed by M5 and transitively by M6)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0024, D-0025
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0024/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0025/spec.md`

**Deliverables:**
- Invariant declaration protocol and schema: structured format (name, formal statement, scope, assumed preconditions), machine-parseable, minimum 2 invariants per variant enforced by orchestrator
- v0/final invariant lifecycle: v0 produced from DA analysis (M1), explicitly marked draft, mandatory refinement to final after M3 outputs available, refinement must demonstrate each invariant holds or is modified against at least one M3 trace

**Steps:**
1. **[PLANNING]** Review DA analysis output schema (T01.01) to identify invariant source material for v0 declarations
2. **[PLANNING]** Define v0/final lifecycle transitions and refinement protocol trigger conditions (M3 availability)
3. **[EXECUTION]** Implement invariant declaration schema: name, formal statement, scope, assumed preconditions -- machine-parseable
4. **[EXECUTION]** Implement orchestrator enforcement: minimum 2 invariants per variant; reject trivially true invariants (DA evaluates strength)
5. **[EXECUTION]** Implement v0/final lifecycle: v0 status on initial declaration, mandatory refinement to final when M3 trace outputs available, refinement evidence required
6. **[VERIFICATION]** Verify protocol produces well-formed v0 invariants from DA input and transitions to final with M3 trace grounding
7. **[COMPLETION]** Document protocol, schema, and lifecycle with worked examples including v0-to-final transition

**Acceptance Criteria:**
- Each advocate declares invariants in structured format (name, formal statement, scope, assumed preconditions) that is machine-parseable
- Minimum 2 invariants per variant enforced by orchestrator; trivially true invariants rejected with re-prompt
- v0 invariants produced from M1 DA analysis are explicitly marked draft and not consumed by downstream milestones until refined to final
- Protocol, schema, and v0/final lifecycle documented with worked examples

**Validation:**
- Manual check: Run protocol and verify v0 invariants are produced, marked draft, and transition to final after M3 trace grounding with evidence
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T01.01 (DA analysis is sole input for v0 invariant declaration). M3 completion required for v0-to-final refinement.
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap decision: CEGAR-style approach preserves schedule parallelism (M4 starts after M1, concurrent with M2/M3) without sacrificing evidence grounding. Invariant templates provided for non-formal advocates per roadmap risk mitigation.

---

### T04.02 -- Challenge Round Implementation

**Roadmap Item ID(s):** R-016
**Why:** Challenge rounds expose invariant violations by having opposing advocates and the DA construct input sequences targeting declared invariants. This makes correctness claims testable and surfaces design weaknesses.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (challenge results feed resolution protocol and downstream milestones)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0026, D-0027
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0026/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0027/evidence.md`

**Deliverables:**
- Challenge round implementation where opposing advocates and DA construct input sequences targeting declared invariants
- Challenge output format (target invariant, input sequence, expected violation, trace) with violated invariants flagged as "unproven"

**Steps:**
1. **[PLANNING]** Define challenge round orchestration: who challenges whom, round ordering, DA participation
2. **[PLANNING]** Define challenge output format: target invariant, input sequence, expected violation, trace
3. **[EXECUTION]** Implement challenge round: opposing advocates and DA receive invariant declarations and construct targeted input sequences
4. **[EXECUTION]** Implement challenge output formatting and violated invariant flagging ("unproven" status)
5. **[VERIFICATION]** Run challenge round against test invariants with known violations and verify correct flagging
6. **[COMPLETION]** Document challenge round protocol and output format

**Acceptance Criteria:**
- Opposing advocates and DA construct input sequences targeting declared invariants during challenge round
- Challenge output format includes: target invariant, input sequence, expected violation, trace
- Violated invariants are flagged as "unproven" in pipeline state
- Challenge protocol and output format documented with examples

**Validation:**
- Manual check: Run challenge round against test invariants with known-violatable inputs and verify violation flagging
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T04.01 (invariant declarations feed challenge round)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** DA sources challenge inputs from its pre-Round-1 analysis (T01.01).

---

### T04.03 -- Invariant Resolution and Design Modification Protocol

**Roadmap Item ID(s):** R-017
**Why:** Advocates with violated invariants must either modify their design to restore the invariant or weaken the invariant and accept the consequence. Unresolved violated invariants are convergence blockers.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (unresolved invariants block convergence)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0028, D-0029
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0028/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0029/evidence.md`

**Deliverables:**
- Resolution protocol: advocates with violated invariants must (a) modify design to restore invariant or (b) weaken invariant and accept consequence
- Resolution decision logging in pipeline output with unresolved violated invariants marked as convergence blockers

**Steps:**
1. **[PLANNING]** Define resolution options (modify design / weaken invariant) and their required evidence
2. **[PLANNING]** Define convergence blocker tagging for unresolved violations
3. **[EXECUTION]** Implement resolution protocol: advocate receives violation, chooses resolution path, provides evidence
4. **[EXECUTION]** Implement resolution logging in pipeline output and convergence blocker tagging for unresolved violations
5. **[VERIFICATION]** Run end-to-end invariant lifecycle: declare -> challenge -> violate -> resolve and verify logging and blocker behavior
6. **[COMPLETION]** Document resolution protocol and convergence impact

**Acceptance Criteria:**
- Advocates with violated invariants must either modify design to restore invariant or weaken invariant and accept consequence
- Unresolved violated invariants are tagged as convergence blockers
- Resolution decisions (modify/weaken) are logged in pipeline output with evidence
- Protocol documented with both resolution paths illustrated

**Validation:**
- Manual check: Run invariant lifecycle end-to-end and verify resolution options, logging, and convergence blocker behavior
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T04.02 (challenge round produces violated invariants)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** SC5 target: >=1 violated invariant per 10 pipeline runs (averaged over 30 runs).

---

### Checkpoint: End of Phase 4

**Purpose:** Validate complete invariant lifecycle (declaration -> challenge -> resolution) including v0/final lifecycle before invariant outputs are consumed by M5.
**Checkpoint Report Path:** `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P04-END.md`

**Verification:**
- Invariant declaration protocol produces machine-parseable invariants with v0/final lifecycle functioning correctly
- Challenge rounds successfully target declared invariants and flag violations as "unproven"
- Resolution protocol enforces modify/weaken options with convergence blocker tagging for unresolved violations

**Exit Criteria:**
- All Phase 4 deliverables (D-0024 through D-0029) are complete with evidence artifacts
- v0-to-final refinement pathway tested with M3 trace outputs (or simulated if M3 not yet complete)
- Only final invariants are available for consumption by M5

---

## Phase 5: Failure Mode Enumeration Phase

Add Step 1.5 between Diff Analysis and Adversarial Debate where each advocate enumerates concrete failure modes per variant. This provides advocate-perspective failure analysis that the DA cross-references against its own findings. Final invariants from M4 inform failure mode prioritization.

### T05.01 -- Failure Mode Enumeration Prompt and Output Schema

**Roadmap Item ID(s):** R-019
**Why:** Each advocate must enumerate >=3 failure modes per variant in a structured format. The schema ensures consistency for automated cross-referencing with DA analysis and invariant-based prioritization.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (enumeration feeds DA cross-reference and downstream M6)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0030
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0030/spec.md`

**Deliverables:**
- Failure mode enumeration prompt and output schema: each advocate enumerates >=3 failure modes per variant (including their own) with fields: Precondition / Trigger / Mechanism / Consequence / Detection difficulty

**Steps:**
1. **[PLANNING]** Review DA output schema (T01.01) and invariant schema (T04.01) to align failure mode format for cross-referencing
2. **[PLANNING]** Define failure mode output schema: Precondition / Trigger / Mechanism / Consequence / Detection difficulty
3. **[EXECUTION]** Implement failure mode enumeration prompt requiring >=3 failure modes per variant per advocate (including own variant)
4. **[EXECUTION]** Implement output schema validation: reject malformed enumerations with re-prompt
5. **[VERIFICATION]** Run enumeration prompt against test scenarios and verify >=3 failure modes per variant with correct schema
6. **[COMPLETION]** Document prompt template and output schema

**Acceptance Criteria:**
- Each advocate enumerates >=3 failure modes per variant (including their own) in structured format
- Schema includes: Precondition / Trigger / Mechanism / Consequence / Detection difficulty
- Output schema validation rejects malformed entries
- Prompt and schema documented with examples

**Validation:**
- Manual check: Run enumeration prompt and verify >=3 failure modes per variant with all schema fields populated
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T01.01 (DA analysis baseline), T03.03 (scenario trace outputs for evidence grounding), T04.01 (final invariants for prioritization)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** M5 consumes only M4-final invariants (post-refinement). Exploratory-grade fallback available per roadmap if M3 completion is delayed.

---

### T05.02 -- Novelty Scoring for Failure Mode Findings

**Roadmap Item ID(s):** R-020
**Why:** Novelty scoring ensures incremental value by rewarding unique failure modes not already identified by DA or other advocates. Without novelty scoring, enumeration risks being pure redundancy.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** performance (semantic similarity computation)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0031
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0031/spec.md`

**Deliverables:**
- Novelty scoring logic: unique failure modes (not identified by DA or other advocates) earn bonus debate weight, determined by semantic similarity comparison

**Steps:**
1. **[PLANNING]** Define novelty determination algorithm: semantic similarity threshold against DA analysis and other advocate enumerations
2. **[PLANNING]** Define bonus debate weight mechanism for novel failure modes
3. **[EXECUTION]** Implement novelty scoring: compare each failure mode against DA analysis and other advocate enumerations using semantic similarity
4. **[EXECUTION]** Implement bonus debate weight for novel failure modes
5. **[VERIFICATION]** Test novelty scoring against known novel and redundant failure modes; verify correct scoring
6. **[COMPLETION]** Document novelty algorithm and scoring weights

**Acceptance Criteria:**
- Unique failure modes (not identified by DA or other advocates) earn bonus debate weight
- Novelty determined by semantic similarity against DA analysis and other advocate enumerations
- Scoring is deterministic for identical inputs
- Algorithm and weights documented

**Validation:**
- Manual check: Run scoring against test failure modes with known novel and redundant entries; verify correct novelty detection
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T05.01 (failure mode output to score), T01.03 (DA analysis as novelty baseline)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap risk mitigation: if post-deployment metrics show <10% novel findings over 20 runs, consider merging enumeration into DA phase.

---

### T05.03 -- DA Cross-Reference and Gap Detection with Invariant Priority Flagging

**Roadmap Item ID(s):** R-021
**Why:** DA cross-references advocate failure modes against its own analysis to surface blind spots. Failure modes that violate M4 final invariants are flagged as high-priority, bridging structural challenge and formal reasoning.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (cross-reference connects M1, M4, and M5 outputs)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0032, D-0033
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0032/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0033/evidence.md`

**Deliverables:**
- DA cross-reference: gaps (failure modes found by DA but not by any advocate) surfaced as blind-spot warnings
- Invariant-violation priority flagging: failure modes that violate M4 final invariants flagged as high-priority

**Steps:**
1. **[PLANNING]** Define cross-reference matching algorithm: DA failure modes vs advocate failure modes
2. **[PLANNING]** Define invariant-violation matching: failure modes mapped against M4 final invariant declarations
3. **[EXECUTION]** Implement DA cross-reference: compare advocate failure modes against DA analysis, surface gaps as blind-spot warnings
4. **[EXECUTION]** Implement invariant-violation priority flagging: failure modes that violate M4 final invariants marked high-priority
5. **[VERIFICATION]** Test cross-reference with known gaps and invariant violations; verify correct gap detection and priority flagging
6. **[COMPLETION]** Document cross-reference logic and priority flagging rules

**Acceptance Criteria:**
- DA cross-references advocate failure modes against its own analysis; gaps surfaced as blind-spot warnings
- Failure modes that violate M4 final invariants flagged as high-priority
- Cross-reference and priority flagging are deterministic
- Logic and rules documented with examples

**Validation:**
- Manual check: Run cross-reference with known DA-only gaps and invariant-violating failure modes; verify gap detection and priority flags
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T05.01 (advocate failure modes), T05.02 (novelty scores), T01.03 (DA analysis), T04.01 (M4 final invariants)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** None.

---

### Checkpoint: End of Phase 5

**Purpose:** Validate complete failure mode enumeration pipeline including novelty scoring, DA cross-reference, and invariant priority flagging before post-merge validation consumes these outputs.
**Checkpoint Report Path:** `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P05-END.md`

**Verification:**
- Failure mode enumeration produces >=3 failure modes per variant per advocate with correct schema
- Novelty scoring correctly identifies unique failure modes and assigns bonus debate weight
- DA cross-reference surfaces gaps and invariant-violation priority flagging works correctly

**Exit Criteria:**
- All Phase 5 deliverables (D-0030 through D-0033) are complete with evidence artifacts
- Cross-reference and priority flagging tested with M4 final invariants
- Exploratory-grade fallback (if used) has been upgraded to full-grade

---

## Phase 6: Post-Merge Trace Validation

Introduce a fresh validation agent (Step 5.5) that traces scenarios through the merged solution with no advocacy bias. This agent catches merge artifacts -- bugs introduced by the synthesis process itself. Provenance tagging enables traceability of trace elements to their originating milestones.

### T06.01 -- Post-Merge Validation Agent Prompt and Role Specification

**Roadmap Item ID(s):** R-023
**Why:** The validation agent must be isolated from debate history to eliminate confirmation bias. It receives only the merged solution and original scenarios, simulating a fresh reviewer.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (validation agent consumes M3 scenarios and produces merge artifact reports for pipeline)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential, Context7 | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0034
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0034/spec.md`

**Deliverables:**
- Post-merge validation agent prompt and role specification: agent is distinct from all debate participants, receives merged solution and original scenarios (from M3) but not debate history, traces 3-5 scenarios independently

**Steps:**
1. **[PLANNING]** Define agent isolation requirements: no debate history, no advocate identity, only merged solution + M3 scenarios
2. **[PLANNING]** Define agent input/output interface: receives merged solution + scenarios, produces trace results
3. **[EXECUTION]** Author validation agent prompt: distinct role, no debate history access, trace 3-5 scenarios through merged solution
4. **[EXECUTION]** Implement agent isolation in pipeline: debate history is not passed to validation agent
5. **[VERIFICATION]** Verify agent produces independent traces without debate history leakage
6. **[COMPLETION]** Document agent specification, isolation guarantees, and input/output interface

**Acceptance Criteria:**
- Agent is distinct from all debate participants with no access to debate history
- Agent receives merged solution and original scenarios (from M3) only
- Agent traces 3-5 scenarios through merged solution independently
- Specification and isolation guarantees documented

**Validation:**
- Manual check: Run validation agent and verify it receives only merged solution + scenarios, no debate history
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T03.01 (original scenarios from M3 scenario generation), T03.02 (trace protocol for consistent format)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap decision: no debate history access chosen over full context or summary-only. Eliminates confirmation bias.

---

### T06.02 -- Merge Artifact Detection and Classification

**Roadmap Item ID(s):** R-024
**Why:** The validation agent must compare its trace results against expected end-states from M3 scenario traces and classify divergences as merge artifacts with root cause hypotheses.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (merge artifact reports feed pipeline re-debate logic)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0035, D-0036
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0035/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0036/evidence.md`

**Deliverables:**
- Merge artifact detection: agent compares trace results against M3 expected end-states and identifies divergences as merge artifacts
- Merge artifact report format: source scenario, expected state, actual state, root cause hypothesis per artifact

**Steps:**
1. **[PLANNING]** Define merge artifact detection algorithm: compare validation agent traces against M3 expected end-states
2. **[PLANNING]** Define artifact report format: source scenario, expected state, actual state, root cause hypothesis
3. **[EXECUTION]** Implement merge artifact detection: compare validation agent end-states against M3 scenario trace end-states
4. **[EXECUTION]** Implement artifact classification and report generation with root cause hypothesis per detected artifact
5. **[VERIFICATION]** Inject known merge artifacts into test cases and verify detection and correct report format (SC6)
6. **[COMPLETION]** Document detection algorithm and report format

**Acceptance Criteria:**
- Agent compares its trace results against expected end-states from M3 scenario traces
- Divergences classified as merge artifacts with report: source scenario, expected state, actual state, root cause hypothesis
- All known merge artifacts detected in synthetic test cases (SC6)
- Algorithm and report format documented

**Validation:**
- Manual check: Inject known merge artifacts into 5 test cases and verify all are detected with correct reports (SC6)
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T06.01 (validation agent), T03.02 (M3 expected end-states for comparison)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** None.

---

### T06.03 -- Pipeline Integration -- Step 5.5 Insertion and Convergence Impact

**Roadmap Item ID(s):** R-025
**Why:** Merge artifacts must trigger debate reopening when critical artifacts are found. The re-debate is capped at 1 iteration to prevent unbounded loops, with escalation to human review if artifacts persist.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (re-debate trigger affects pipeline flow), performance (unbounded iteration risk mitigated by cap)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0037, D-0038
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0037/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0038/evidence.md`

**Deliverables:**
- Step 5.5 inserted into pipeline: post-merge validation runs after merge, before pipeline completion
- Re-debate trigger: >0 critical merge artifacts reject merged solution and re-enter debate with artifact constraints; capped at 1 re-debate iteration with human escalation if artifacts persist

**Steps:**
1. **[PLANNING]** Identify pipeline insertion point for Step 5.5 (after merge, before completion)
2. **[PLANNING]** Define re-debate trigger conditions and iteration cap logic
3. **[EXECUTION]** Insert Step 5.5 into pipeline orchestration flow
4. **[EXECUTION]** Implement re-debate trigger: >0 critical merge artifacts -> reject merged solution -> re-enter debate with artifact-specific constraints
5. **[EXECUTION]** Implement iteration cap: 1 re-debate maximum; if artifacts persist after re-merge, escalate to human review with full trace evidence
6. **[VERIFICATION]** Test pipeline with and without merge artifacts; verify Step 5.5 triggers correctly and re-debate cap enforced
7. **[COMPLETION]** Document pipeline insertion, trigger logic, and escalation path

**Acceptance Criteria:**
- Step 5.5 executes after merge and before pipeline completion
- >0 critical merge artifacts trigger debate reopening with artifact-specific focus
- Re-debate capped at 1 iteration; persistent artifacts escalate to human review with full trace evidence
- Pipeline output includes merge validation report

**Validation:**
- Manual check: Run pipeline with injected merge artifacts and verify Step 5.5 triggers re-debate, cap enforced, escalation works
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T06.01, T06.02
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap risk R6 mitigation: 1 iteration cap prevents unbounded loops.

---

### T06.04 -- Provenance Tagging and Cross-Artifact Consistency Check

**Roadmap Item ID(s):** R-026
**Why:** Provenance tags attribute trace elements to their originating milestones (M3 scenarios, M4 invariants, M5 failure modes), enabling traceability. The consistency check catches untraceable entries.
**Effort:** `M`
**Risk:** `Medium`
**Risk Drivers:** cross-cutting (provenance spans M3, M4, M5 outputs)
**Tier:** `STANDARD`
**Confidence:** `[████████--] 80%`
**Requires Confirmation:** No
**Critical Path Override:** No
**Verification Method:** Direct test execution (300-500 tokens, 30s timeout)
**MCP Requirements:** Preferred: Sequential | None required
**Fallback Allowed:** Yes
**Sub-Agent Delegation:** None
**Deliverable IDs:** D-0039, D-0040
**Artifacts (Intended Paths):**
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0039/spec.md`
- `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0040/evidence.md`

**Deliverables:**
- Provenance tagging: each validated trace in merge validation report includes tags attributing elements to M3 scenario source, M4 invariant references, M5 failure mode cross-references
- Cross-artifact consistency check: verifies M4 invariant claims and M5 failure mode entries are traceable through merged artifact; untraceable entries flagged as provenance gaps

**Steps:**
1. **[PLANNING]** Define provenance tag schema: milestone source (M3/M4/M5), artifact ID, element reference
2. **[PLANNING]** Define consistency check rules: what constitutes a traceable vs untraceable entry
3. **[EXECUTION]** Implement provenance tagging: insert tags into merge validation report traces attributing elements to originating milestones
4. **[EXECUTION]** Implement consistency check: verify M4 invariant claims and M5 failure mode entries are traceable through merged artifact; flag untraceable entries as provenance gaps
5. **[VERIFICATION]** Test with traces containing known traceable and untraceable entries; verify correct tagging and gap detection
6. **[COMPLETION]** Document tag schema and consistency check rules

**Acceptance Criteria:**
- Each validated trace includes provenance tags attributing elements to M3, M4, and M5 sources
- Consistency check verifies traceability of M4 invariant claims and M5 failure mode entries through merged artifact
- Untraceable entries flagged as provenance gaps
- Tag schema and consistency rules documented

**Validation:**
- Manual check: Run provenance tagging and consistency check; verify tags present and gaps correctly flagged for known untraceable entries
- Evidence: linkable artifact produced (spec/test log/screenshot/doc)

**Dependencies:** T06.01, T06.02, T06.03 (provenance tagging operates on merge validation output)
**Rollback:** TBD (if not specified in roadmap)
**Notes:** Roadmap risk mitigation: if provenance tagging time exceeds 30% of total Step 5.5 duration, simplify to milestone-level tags only.

---

### Checkpoint: End of Phase 6

**Purpose:** Validate complete post-merge validation pipeline including agent isolation, merge artifact detection, re-debate triggering, and provenance tagging before declaring v2.0 implementation complete.
**Checkpoint Report Path:** `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P06-END.md`

**Verification:**
- Post-merge validation agent produces independent traces without debate history leakage
- Merge artifact detection catches all injected artifacts in synthetic test cases (SC6)
- Provenance tagging and consistency check correctly attribute trace elements and flag untraceable entries

**Exit Criteria:**
- All Phase 6 deliverables (D-0034 through D-0040) are complete with evidence artifacts
- SC6 verified: all known merge artifacts detected in 5 synthetic test cases
- Pipeline convergence rate measured over test runs (target: >=80% without human intervention, SC8)

---

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.04 | D-0008 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0008/evidence.md` |
| R-002 | T01.01 | D-0001, D-0002, D-0003 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0001/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0002/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0003/spec.md` |
| R-003 | T01.02 | D-0004, D-0005 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0004/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0005/evidence.md` |
| R-004 | T01.03 | D-0006, D-0007 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0006/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0007/evidence.md` |
| R-005 | T02.01, T02.02, T02.03 | D-0009, D-0010, D-0011, D-0012, D-0013, D-0014 | STANDARD | 82% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0009/spec.md` through `D-0014/evidence.md` |
| R-006 | T02.01 | D-0009, D-0010 | STANDARD | 82% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0009/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0010/spec.md` |
| R-007 | T02.02 | D-0011, D-0012 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0011/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0012/evidence.md` |
| R-008 | T02.03 | D-0013, D-0014 | STANDARD | 82% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0013/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0014/evidence.md` |
| R-009 | T03.05 | D-0022, D-0023 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0022/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0023/evidence.md` |
| R-010 | T03.01 | D-0015, D-0016 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0015/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0016/evidence.md` |
| R-011 | T03.02 | D-0017, D-0018 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0017/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0018/spec.md` |
| R-012 | T03.03 | D-0019, D-0020 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0019/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0020/evidence.md` |
| R-013 | T03.04 | D-0021 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0021/spec.md` |
| R-014 | T04.01, T04.02, T04.03 | D-0024, D-0025, D-0026, D-0027, D-0028, D-0029 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0024/spec.md` through `D-0029/evidence.md` |
| R-015 | T04.01 | D-0024, D-0025 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0024/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0025/spec.md` |
| R-016 | T04.02 | D-0026, D-0027 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0026/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0027/evidence.md` |
| R-017 | T04.03 | D-0028, D-0029 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0028/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0029/evidence.md` |
| R-018 | T05.01, T05.02, T05.03 | D-0030, D-0031, D-0032, D-0033 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0030/spec.md` through `D-0033/evidence.md` |
| R-019 | T05.01 | D-0030 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0030/spec.md` |
| R-020 | T05.02 | D-0031 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0031/spec.md` |
| R-021 | T05.03 | D-0032, D-0033 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0032/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0033/evidence.md` |
| R-022 | T06.01, T06.02, T06.03, T06.04 | D-0034, D-0035, D-0036, D-0037, D-0038, D-0039, D-0040 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0034/spec.md` through `D-0040/evidence.md` |
| R-023 | T06.01 | D-0034 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0034/spec.md` |
| R-024 | T06.02 | D-0035, D-0036 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0035/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0036/evidence.md` |
| R-025 | T06.03 | D-0037, D-0038 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0037/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0038/evidence.md` |
| R-026 | T06.04 | D-0039, D-0040 | STANDARD | 80% | `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0039/spec.md`, `.dev/releases/current/2.07-adversarial-v2/artifacts/D-0040/evidence.md` |

---

## Execution Log Template

**Intended Path:** `.dev/releases/current/2.07-adversarial-v2/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<=12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | `.dev/releases/current/2.07-adversarial-v2/evidence/` |

---

## Checkpoint Report Template

For each checkpoint created in this tasklist, execution must produce one report using this template.

**Template:**

```markdown
# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** .dev/releases/current/2.07-adversarial-v2/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>

## Status
Overall: Pass | Fail | TBD

## Verification Results
- <Verification bullet 1 result>
- <Verification bullet 2 result>
- <Verification bullet 3 result>

## Exit Criteria Assessment
- <Exit criterion 1 assessment>
- <Exit criterion 2 assessment>
- <Exit criterion 3 assessment>

## Issues & Follow-ups
- <List blocking issues; reference T<PP>.<TT> and D-####>

## Evidence
- .dev/releases/current/2.07-adversarial-v2/evidence/<relevant-evidence-file>
```

**Checkpoint paths:**
- `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P01-END.md`
- `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P02-END.md`
- `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P03-T01-T04.md`
- `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P03-END.md`
- `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P04-END.md`
- `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P05-END.md`
- `.dev/releases/current/2.07-adversarial-v2/checkpoints/CP-P06-END.md`

---

## Feedback Collection Template

**Intended Path:** `.dev/releases/current/2.07-adversarial-v2/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (<=15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| T01.01 | STANDARD | | | | | |
| T01.02 | STANDARD | | | | | |
| T01.03 | STANDARD | | | | | |
| T01.04 | STANDARD | | | | | |
| T02.01 | STANDARD | | | | | |
| T02.02 | STANDARD | | | | | |
| T02.03 | STANDARD | | | | | |
| T03.01 | STANDARD | | | | | |
| T03.02 | STANDARD | | | | | |
| T03.03 | STANDARD | | | | | |
| T03.04 | STANDARD | | | | | |
| T03.05 | STANDARD | | | | | |
| T04.01 | STANDARD | | | | | |
| T04.02 | STANDARD | | | | | |
| T04.03 | STANDARD | | | | | |
| T05.01 | STANDARD | | | | | |
| T05.02 | STANDARD | | | | | |
| T05.03 | STANDARD | | | | | |
| T06.01 | STANDARD | | | | | |
| T06.02 | STANDARD | | | | | |
| T06.03 | STANDARD | | | | | |
| T06.04 | STANDARD | | | | | |

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification (e.g., "Involved auth paths", "Actually trivial")
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`
