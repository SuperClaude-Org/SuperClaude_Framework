---
spec_source: "spec-roadmap-remediate.md"
complexity_score: 0.72
primary_persona: analyzer
---

# Project Roadmap: Roadmap Remediation Pipeline Extension

## 1. Executive Summary

This roadmap delivers a controlled extension to the existing roadmap pipeline by adding two new post-validation stages: **remediate** and **certify**. The objective is to convert validation findings into a bounded, auditable remediation pass and then verify outcomes without creating an automatic remediation loop.

### Analyzer Assessment
1. **Primary delivery goal**
   - Turn validation output into structured, actionable remediation work.
   - Preserve pipeline determinism, rollback safety, and resume correctness.
   - Certify whether fixes actually resolved targeted findings.

2. **Primary implementation concerns**
   - Parser fragility across report variants.
   - Transaction safety for multi-agent edits.
   - Backward-compatible state evolution.
   - Non-interactive pipeline contract preservation.
   - False confidence from weak certification.

3. **Recommended implementation posture**
   - Build the feature in layers: parsing → filtering/tasklist → orchestration → certification → resume/state.
   - Treat rollback, hashing, and gate validation as first-class features, not cleanup tasks.
   - Front-load tests around failure modes and stale resume behavior.

### Outcome Target
At completion, `roadmap run` should support:
1. Validation findings summarization.
2. User-driven remediation scope selection.
3. Parallel file-scoped remediation within a strict editable-file allowlist.
4. Single-pass certification with structured PASS/FAIL output.
5. Safe resume behavior with stale detection and additive state persistence.

---

## 2. Phased Implementation Plan with Milestones

## Phase 0 — Discovery, Baseline, and Architecture Lock
**Objective:** Eliminate ambiguity before code changes.

### Key Actions
1. Review existing pipeline foundation:
   - `execute_pipeline()`
   - `execute_roadmap()`
   - `validate_executor.py`
   - step/gate/state models
   - resume flow and hash usage patterns
2. Confirm current state schema version and additive-extension strategy.
3. Resolve open questions that affect architecture:
   - SIGINT behavior during remediation
   - handling of findings outside editable allowlist
   - hash algorithm standardization
   - fallback dedupe line-resolution strategy
   - treatment of CONFLICT agreement findings
4. Define canonical finding lifecycle:
   - `SKIPPED`
   - `FIXED`
   - `FAILED`

### Deliverables
- Architecture decision notes.
- Final finding status model.
- Confirmed step wiring design for `remediate` and `certify`.

### Milestone
- **M0:** Architecture and ambiguity resolution complete.

### Timeline Estimate
- **0.5-1 day**

---

## Phase 1 — Structured Findings Parsing and Normalization
**Objective:** Build reliable ingestion of validation outputs into structured `Finding` objects.

### Key Actions
1. Implement merged-report parser for:
   - `validate/reflect-merged.md`
   - `validate/merged-validation-report.md`
2. Create `Finding` dataclass with required fields:
   - `id`
   - `severity`
   - `dimension`
   - `description`
   - `location`
   - `evidence`
   - `fix_guidance`
   - `files_affected`
   - `status`
   - `agreement_category`
3. Implement fallback parsing for individual reflect reports.
4. Add deduplication logic:
   - same file
   - within 5 lines
   - higher severity wins
5. Produce finding counts by severity for downstream prompt logic.

### Analyzer Priorities
- Parser resilience is a critical dependency for every downstream phase.
- Use fixture-based tests for known report variants before orchestration begins.
- Fail loudly when required structured fields are absent.

### Deliverables
- Findings parser module.
- Fallback parser.
- Deduplication logic.
- Parser unit tests across known report formats.

### Milestone
- **M1:** Validation reports reliably normalize into structured findings.

### Timeline Estimate
- **1-1.5 days**

---

## Phase 2 — Scope Selection, Filtering, and Remediation Tasklist Generation
**Objective:** Convert raw findings into a bounded remediation plan.

### Key Actions
1. Implement terminal summary of findings by severity.
2. Add interactive prompt in `execute_roadmap()` with options:
   - BLOCKING only
   - BLOCKING + WARNING
   - All
   - Skip remediation
3. Implement filtering rules:
   - user-selected severity scope
   - always skip `NO_ACTION_REQUIRED`
   - always skip `OUT_OF_SCOPE`
4. Add zero-findings guard behavior:
   - emit valid `remediation-tasklist.md`
   - `actionable: 0`
   - all findings `SKIPPED`
5. Generate `remediation-tasklist.md` with required YAML frontmatter and grouped entries.
6. Implement `REMEDIATE_GATE` with:
   - required fields
   - minimum line count
   - semantic validation
   - all actionable findings must have status

### Analyzer Priorities
- This phase defines the control surface users see; behavior must be deterministic.
- Prompt handling must stay outside `execute_pipeline()` to preserve architecture.
- Tasklist output becomes the audit trail for remediation, so schema rigor matters.

### Deliverables
- Interactive selection flow.
- Filtering engine.
- Tasklist renderer.
- Gate criteria and semantic checks.

### Milestone
- **M2:** User-approved remediation scope produces a valid, auditable tasklist.

### Timeline Estimate
- **1 day**

---

## Phase 3 — Remediation Orchestration and Transaction Safety
**Objective:** Execute remediation safely with rollback guarantees.

### Key Actions
1. Group actionable findings by primary target file.
2. Enforce editable-file allowlist:
   - `roadmap.md`
   - `extraction.md`
   - `test-strategy.md`
3. Handle cross-file findings by duplicating scoped guidance into each relevant agent prompt.
4. Build pure prompt functions for remediation.
5. Implement internal remediation executor using `ClaudeProcess` directly.
6. Snapshot editable targets to `.pre-remediate` before agent execution.
7. Run different-file agents in parallel.
8. Enforce runtime controls:
   - 300-second timeout
   - single retry on failure
   - inherited model configuration
   - no session continuation flags
9. On any failure:
   - halt remaining agents
   - rollback all target files
   - mark failed/cross-file-related findings `FAILED`
   - fail step and halt pipeline
10. On full success:
   - delete snapshots
   - mark targeted findings `FIXED`

### Analyzer Priorities
- This is the highest-risk phase.
- Rollback logic must be tested before parallel agent execution is considered complete.
- Parallelism is valuable, but only after same-file conflict elimination is proven.

### Deliverables
- Remediation executor.
- Prompt builder.
- Snapshot/rollback subsystem.
- Parallel dispatch and collection flow.
- Failure-path tests.

### Milestone
- **M3:** Remediation executes atomically with bounded concurrency and rollback protection.

### Timeline Estimate
- **1.5-2 days**

---

## Phase 4 — Certification Review and Outcome Classification
**Objective:** Verify remediation results without re-running full adversarial validation.

### Key Actions
1. Implement scoped certification input assembly using only relevant sections around finding locations.
2. Build pure certification prompt function.
3. Add single-agent certification step via `execute_pipeline()`.
4. Generate `certification-report.md` with required frontmatter:
   - `findings_verified`
   - `findings_passed`
   - `findings_failed`
   - `certified`
   - `certification_date`
5. Emit per-finding PASS/FAIL table with justifications.
6. Implement `CERTIFY_GATE` with:
   - required fields
   - minimum line count
   - semantic checks
   - per-finding table presence
7. Update final state outcomes:
   - all pass → `certified: true`, `tasklist_ready: true`
   - some fail → `certified-with-caveats`
   - no auto-loop

### Analyzer Priorities
- Keep certification narrow enough to control token cost but broad enough to avoid false passes.
- Certification must be skeptical by design; justification quality matters as much as PASS/FAIL labels.

### Deliverables
- Certification prompt builder.
- Certification context extractor.
- Certification report writer.
- Step integration and state transitions.

### Milestone
- **M4:** Certification produces reliable PASS/FAIL verification with explicit caveat handling.

### Timeline Estimate
- **1 day**

---

## Phase 5 — State, Resume, and Backward Compatibility
**Objective:** Integrate new steps without breaking existing consumers.

### Key Actions
1. Extend `.roadmap-state.json` with additive fields only.
2. Add new step metadata for:
   - `remediate`
   - `certify`
3. Implement resume rules:
   - skip validate→remediate when valid gate exists
   - verify `source_report_hash`
   - detect stale remediation tasklists
   - skip certify if certification gate passes
4. Define and standardize report hashing algorithm.
5. Validate compatibility with existing status/tasklist consumers.

### Analyzer Priorities
- Resume correctness is a high-leverage risk reducer.
- Stale detection is essential; otherwise resume may certify against outdated findings.
- Backward compatibility should be tested explicitly, not assumed.

### Deliverables
- State schema extension.
- Resume-path logic.
- Stale detection.
- Backward compatibility test coverage.

### Milestone
- **M5:** Resume behavior is correct, additive, and safe against stale artifacts.

### Timeline Estimate
- **0.75-1 day**

---

## Phase 6 — Validation, Performance, and Release Hardening
**Objective:** Prove the feature meets functional and nonfunctional acceptance criteria.

### Key Actions
1. Build end-to-end tests for:
   - remediation approved
   - remediation skipped
   - zero findings
   - fallback parser path
   - rollback on agent failure
   - partial certification failure
   - resume from each new state boundary
2. Add file-safety test ensuring no edits outside allowlist.
3. Add performance measurement for SC-006:
   - steps 10-11 overhead ≤30% vs steps 1-9 baseline
4. Validate gate strictness and semantic checks.
5. Perform code review against architectural constraints:
   - pure prompts
   - unidirectional imports
   - atomic writes
   - reuse of `ClaudeProcess`
6. Run regression validation on pre-existing roadmap flows.

### Analyzer Priorities
- Functional completeness is insufficient without rollback, resume, and performance evidence.
- Release readiness depends on proving the new stages do not destabilize the existing pipeline.

### Deliverables
- Full test suite additions.
- Performance benchmark report.
- Release-readiness checklist.

### Milestone
- **M6:** Feature is validated, performant, and ready for integration.

### Timeline Estimate
- **1-1.5 days**

---

## 3. Risk Assessment and Mitigation Strategies

## High-Priority Risks

### 1. Report parser breakage from format drift
- **Risk:** Upstream validation report structure changes invalidate parsing.
- **Impact:** High
- **Probability:** Low-Medium
- **Mitigation:**
  - Maintain fixtures for all known report variants.
  - Separate parsing from normalization logic.
  - Add graceful fallback to individual reflect reports.
  - Prefer schema-tolerant extraction with explicit required-field checks.

### 2. Rollback failure during multi-agent remediation
- **Risk:** Partial edits remain after timeout/failure/interruption.
- **Impact:** High
- **Probability:** Medium
- **Mitigation:**
  - Snapshot every target file before any agent starts.
  - Centralize rollback orchestration.
  - Treat SIGINT handling as an explicit design case.
  - Test failure after first agent success and second agent timeout.

### 3. Stale resume causing invalid certification
- **Risk:** Resume path reuses outdated tasklist/report state.
- **Impact:** High
- **Probability:** Medium
- **Mitigation:**
  - Require `source_report_hash` validation.
  - Fail closed on hash mismatch.
  - Make resume decisions gate- and hash-based, not timestamp-only.

### 4. Certification false passes
- **Risk:** Certification marks unresolved findings as PASS.
- **Impact:** Medium-High
- **Probability:** Medium
- **Mitigation:**
  - Use finding-scoped evidence windows.
  - Require explicit justification per finding.
  - Add negative tests with intentionally unfixed findings.
  - Keep certification single-pass, but skeptical.

### 5. Cross-file finding coordination errors
- **Risk:** Agents make incompatible edits across related files.
- **Impact:** Medium
- **Probability:** Low-Medium
- **Mitigation:**
  - Batch by target file.
  - Scope prompt guidance per file.
  - Mark coupled failures appropriately on any agent failure.
  - Prefer deterministic tasklist representation for cross-file linkage.

## Secondary Risks

### 6. Allowlist mismatch with findings outside editable scope
- **Mitigation:**
  - Define deterministic behavior: likely `SKIPPED` + warning emission.
  - Cover in parser/filter tests.

### 7. Performance overhead exceeds SC-006
- **Mitigation:**
  - Keep certification context minimal.
  - Maximize parallelism only across disjoint files.
  - Reuse existing process abstractions.

### 8. State schema breaks existing consumers
- **Mitigation:**
  - Additive fields only.
  - Regression test status and tasklist generation consumers.

---

## 4. Resource Requirements and Dependencies

## Engineering Resources
1. **Primary backend/pipeline engineer**
   - Pipeline orchestration
   - state/resume logic
   - rollback semantics
2. **QA / test engineer support**
   - parser fixtures
   - integration tests
   - performance validation
3. **Analyzer/reviewer**
   - architecture verification
   - failure-mode review
   - acceptance criteria traceability

## Technical Dependencies
1. **Pipeline infrastructure from v2.20-WorkflowEvolution**
   - `execute_pipeline()`
   - step/gate framework
   - resume and state patterns
2. **`ClaudeProcess`**
   - required for remediation subprocess orchestration
3. **Gate framework**
   - `GateCriteria`
   - `SemanticCheck`
4. **Existing model modules**
   - `pipeline.models`
   - `roadmap.models`
5. **Validation executor pattern**
   - `validate_executor.py`
6. **Main roadmap orchestration entrypoint**
   - `execute_roadmap()`

## Environmental / Process Requirements
1. Stable test fixtures for merged and individual validation reports.
2. Ability to simulate subprocess timeout/failure deterministically.
3. Performance benchmarking harness for overhead measurement.
4. Controlled test assets for editable-file allowlist enforcement.

---

## 5. Success Criteria and Validation Approach

## Success Criteria Mapping

### SC-001 — End-to-end 12-step completion
- **Validation Approach:**
  - Integration test with approved remediation.
  - Assert successful completion through certify stage.

### SC-002 — ≥90% BLOCKING findings pass certification
- **Validation Approach:**
  - Controlled test corpus with known fixable blocking findings.
  - Measure pass ratio by severity.

### SC-003 — No false passes on unfixed findings
- **Validation Approach:**
  - Seed deliberate unresolved findings.
  - Assert certification outputs FAIL with justification.

### SC-004 — Correct `--resume` behavior
- **Validation Approach:**
  - Resume from:
    1. post-validate
    2. post-remediate
    3. post-certify
  - Include stale-hash mismatch scenario.

### SC-005 — No out-of-scope file edits
- **Validation Approach:**
  - Snapshot workspace diff before/after remediation.
  - Assert edits restricted to allowlist.

### SC-006 — ≤30% wall-clock overhead
- **Validation Approach:**
  - Benchmark steps 1-9 baseline.
  - Benchmark steps 10-11 added overhead.
  - Assert ≤1.3x total relative cost.

### SC-007 — Accurate remediation tasklist status reporting
- **Validation Approach:**
  - Round-trip parse/render verification.
  - Compare expected statuses vs emitted document.

### SC-008 — Backward-compatible state schema
- **Validation Approach:**
  - Regression tests against pre-existing consumers.
  - Verify additive-only field changes.

## Recommended Validation Layers
1. **Unit tests**
   - parsing
   - deduplication
   - filtering
   - prompt builders
   - hash validation
2. **Integration tests**
   - prompt flow
   - remediation orchestration
   - rollback
   - certification
3. **Contract tests**
   - gate outputs
   - state schema
   - output frontmatter
4. **Performance tests**
   - timing overhead
   - token-scope control for certification
5. **Failure-path tests**
   - timeout
   - retry exhaustion
   - stale resume
   - interruption handling

---

## 6. Timeline Estimates per Phase

| Phase | Name | Estimate | Primary Output |
|---|---|---:|---|
| 0 | Discovery and architecture lock | 0.5-1 day | Resolved design decisions |
| 1 | Findings parsing and normalization | 1-1.5 days | Structured parser + tests |
| 2 | Scope selection and tasklist generation | 1 day | Prompt flow + `remediation-tasklist.md` |
| 3 | Remediation orchestration and rollback | 1.5-2 days | Parallel remediation executor |
| 4 | Certification and outcome handling | 1 day | `certification-report.md` |
| 5 | State/resume/backward compatibility | 0.75-1 day | Safe resume + additive state |
| 6 | Validation and hardening | 1-1.5 days | E2E coverage + perf evidence |

## Total Estimated Delivery Window
- **Baseline:** 6.75 days
- **Likely range:** 7-9 working days including defect correction and review

---

## Recommended Milestone Sequence

1. **M0:** Architecture locked and open questions resolved.
2. **M1:** Parser and normalization stable across report variants.
3. **M2:** User selection and remediation tasklist generation complete.
4. **M3:** Transaction-safe remediation orchestration working with rollback.
5. **M4:** Certification step integrated and producing structured PASS/FAIL output.
6. **M5:** Resume/state compatibility verified.
7. **M6:** Full release hardening and acceptance validation complete.

---

## Final Analyzer Recommendations

1. **Do not start with agent orchestration.**
   - Start with parser, tasklist, and state contracts first.

2. **Treat rollback as a release gate.**
   - If rollback is not deterministic, the feature is not ready.

3. **Resolve open questions before finalizing implementation.**
   - Especially SIGINT handling, allowlist-outside findings, and hash algorithm standardization.

4. **Optimize for correctness before speed.**
   - Parallelism helps, but stale resume and false certification are more damaging than slower execution.

5. **Use acceptance criteria as an implementation checklist.**
   - Every phase should map directly to SC-001 through SC-008 with explicit evidence.
