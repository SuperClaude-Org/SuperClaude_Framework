---
spec_source: "spec-workflow-evolution-merged.md"
complexity_score: 0.72
primary_persona: analyzer
---

# 1. Executive Summary

This roadmap delivers a fidelity-validation upgrade for the roadmap and tasklist generation pipeline. The core objective is to prevent semantic drift between source artifacts by adding strict, typed, and testable validation layers at two boundaries:

1. **Spec → Roadmap**
2. **Roadmap → Tasklist**

From an analyzer perspective, the highest-value outcome is not just feature completion, but **reliable detection of omissions, signature drift, traceability errors, and gate bypass behavior** before downstream artifacts are trusted.

## Scope Summary
- **Functional requirements:** 31
- **Non-functional requirements:** 10
- **Total requirements:** 41
- **Complexity:** Moderate (`0.72`)
- **Domains involved:** 5
- **Risks identified:** 8
- **Dependencies identified:** 9
- **Success criteria:** 14
- **Extraction mode:** Full

## Primary Delivery Goals
1. Add a **spec-fidelity generation quality gate** that cannot be bypassed by `--no-validate`.
2. Add a **tasklist fidelity validation workflow** with standalone CLI entrypoint.
3. Correct existing **gate enforcement weaknesses**:
   - `REFLECT_GATE` tier promotion to STRICT
   - `_cross_refs_resolve()` from permissive stub to real validation
4. Add **state persistence and degraded-mode handling** so failure states are explicit and recoverable.
5. Preserve **architectural integrity**:
   - no new executor framework
   - existing pipeline abstractions remain the foundation
   - validation layering remains immediate-upstream only

## Analyzer Assessment
This is a moderately complex integration initiative with disproportionate risk concentrated in:
- **LLM-output consistency**
- **gate strictness rollouts**
- **cross-reference validation regressions**
- **under-specified multi-agent behavior**
- **requirement/schema ambiguity in deviation tables**

The roadmap should therefore prioritize **spec clarification, deterministic validation surfaces, regression protection, and rollout safety** over feature breadth.

---

# 2. Phased Implementation Plan with Milestones

## Phase 0. Specification Reconciliation and Decision Closure

### Objective
Remove ambiguity before code changes begin.

### Why this phase matters
Several open questions directly affect implementation correctness. If unresolved, the team risks rework in prompt builders, gate parsers, and CLI wiring.

### Key actions
1. Resolve **canonical deviation table schema**.
   - Decide between 8-column and 7-column variants.
   - Standardize terminology:
     - `Spec Quote` / `Roadmap Quote`
     - or `Upstream Quote` / `Downstream Quote`
2. Resolve **step ordering**:
   - whether `spec-fidelity` runs before or after reflect.
3. Resolve **cross-reference rollout policy**:
   - blocking immediately vs warning-first for one release.
4. Resolve **multi-agent mode definition gap**:
   - invocation path
   - report merge model
   - failure semantics
5. Clarify **timeout vs NFR expectation**:
   - 120s target vs 600s hard timeout.
6. Decide **tasklist module placement**:
   - `cli/tasklist/` vs extending `cli/roadmap/`.
7. Decide whether to add **count cross-validation** between frontmatter and deviation rows in this release.

### Deliverables
- Decision log for all 8 open questions
- Finalized deviation report schema
- Approved execution ordering and rollout policy

### Milestone
**M0: Specification closure approved**

### Exit criteria
- No unresolved blockers remain for prompt, gate, or CLI design.
- Canonical schema documented and shared with prompt builders and test authors.

---

## Phase 1. Foundation and Data Model Preparation

### Objective
Create the typed and documented foundation needed for fidelity reporting without disrupting existing architecture.

### Key actions
1. Introduce `FidelityDeviation` dataclass.
   - Fields:
     - `source_pair`
     - `severity`
     - `deviation`
     - `upstream_quote`
     - `downstream_quote`
     - `impact`
     - `recommended_correction`
2. Extend `RoadmapConfig` with optional `retrospective_file: Path | None`.
3. Add deviation report format reference accessible to prompt builders.
4. Confirm module boundaries:
   - extend `roadmap/`
   - add `tasklist/` only if Phase 0 decision requires it
   - keep `pipeline/` abstractions unchanged
5. Prepare state file handling contract for new `fidelity_status`.

### Deliverables
- Typed deviation model
- format reference document
- config extension
- agreed file/module map

### Milestone
**M1: Validation foundation merged**

### Exit criteria
- All foundational types compile and integrate with current Python 3.10+ syntax expectations.
- No new executor/process abstraction introduced.

---

## Phase 2. Spec-Fidelity Validation Capability

### Objective
Implement the roadmap fidelity layer at the **spec → roadmap** boundary.

### Key actions
1. Add `build_spec_fidelity_prompt(spec_content: str, roadmap_content: str) -> str` in `roadmap/prompts.py`.
2. Ensure prompt explicitly enforces:
   - comparison of every function signature, data model, gate criteria, CLI option, and NFR
   - quote pairing from both source and downstream artifact
   - required YAML frontmatter fields
   - normalized deviation table format
   - severity definitions
3. Define `SPEC_FIDELITY_GATE` in `roadmap/gates.py` with **STRICT** enforcement.
4. Implement semantic checks:
   - `high_severity_count == 0`
   - missing field => fail
   - degraded pass-through when:
     - `validation_complete: false`
     - `fidelity_check_attempted: true`
5. Add `spec-fidelity` step to `_build_steps()` in `roadmap/executor.py`.
   - placed after `test-strategy` unless Phase 0 changes ordering
   - inputs: `spec_file`, `roadmap.md`
   - output: `{output_dir}/spec-fidelity.md`
   - timeout: 600s
   - retry_limit: 1
6. Enforce bypass protection:
   - `--no-validate` must not skip spec-fidelity
7. Persist `fidelity_status` to `.roadmap-state.json`
   - `pass|fail|skipped|degraded`
8. Implement degraded artifact generation on agent failure:
   - explicit frontmatter
   - error summary in body
   - `tasklist_ready: false` when fidelity incomplete

### Deliverables
- prompt builder
- gate definition and semantic logic
- executor step
- state persistence behavior
- degraded-mode artifact generation

### Milestone
**M2: Spec-fidelity gate active in pipeline**

### Exit criteria
- Pipeline blocks on HIGH deviations.
- Pipeline continues with warning in degraded mode.
- `spec-fidelity` runs even with `--no-validate`.

---

## Phase 3. Gate Engine Corrections and Integrity Hardening

### Objective
Fix known validation blind spots in existing gate behavior.

### Key actions
1. Promote `REFLECT_GATE` from `STANDARD` to `STRICT`.
2. Replace `_cross_refs_resolve()` permissive stub with actual validation:
   - extract heading anchors
   - find cross-reference targets
   - fail when target heading does not exist
3. Add semantic consistency checks:
   - `_high_severity_count_zero(content: str) -> bool`
   - `_tasklist_ready_consistent(content: str) -> bool`
4. If approved in Phase 0, add row/frontmatter count cross-validation to reduce silent LLM inconsistencies.
5. Validate behavior against existing artifacts in `.dev/releases/complete/`.

### Deliverables
- corrected cross-reference validation
- stricter reflect gate enforcement
- semantic consistency checks

### Milestone
**M3: Existing validation layer hardened**

### Exit criteria
- REFLECT semantic checks execute under STRICT rules.
- Broken cross-references are detected reliably.
- Existing valid artifacts do not regress unexpectedly.

---

## Phase 4. Tasklist Fidelity Validation Capability

### Objective
Implement the second validation boundary at **roadmap → tasklist**.

### Key actions
1. Add `build_tasklist_fidelity_prompt(roadmap_content: str, tasklist_content: str) -> str`.
2. Ensure prompt checks:
   - deliverable coverage
   - signature preservation
   - traceability ID validity
   - dependency chain correctness
3. Reuse normalized deviation reporting format.
4. Define `TASKLIST_FIDELITY_GATE` with **STRICT** enforcement.
5. Add CLI subcommand:
   - `superclaude tasklist validate <output-dir>`
   - options:
     - `--roadmap-file`
     - `--tasklist-dir`
     - `--model`
     - `--max-turns`
     - `--debug`
6. Ensure standalone invocability.
7. Return exit code `1` on HIGH-severity deviations.
8. Optimize tasklist input assembly to limit token cost:
   - use index + relevant phase files
   - avoid unnecessary full-bundle expansion unless required

### Deliverables
- tasklist fidelity prompt
- strict gate
- standalone CLI validate flow
- output artifact `{output_dir}/tasklist-fidelity.md`

### Milestone
**M4: Tasklist fidelity validator available**

### Exit criteria
- Tasklist validation catches fabricated traceability.
- CLI works standalone and is automation-ready.

---

## Phase 5. Test, Regression, and Performance Validation

### Objective
Prove correctness, non-regression, and acceptable overhead.

### Key actions
1. Add and update unit tests for:
   - cross-reference resolution
   - severity count extraction
   - tasklist readiness consistency
   - retrospective prompt insertion
2. Add integration tests for:
   - spec-fidelity blocking on HIGH
   - clean roadmap pass
   - degraded-mode continuation
   - `--no-validate` non-bypass
   - state persistence updates
3. Add E2E/CLI tests for:
   - `superclaude tasklist validate`
   - fabricated traceability detection
4. Run full roadmap test suite:
   - `uv run pytest tests/roadmap/`
5. Benchmark:
   - spec-fidelity runtime
   - tasklist validation runtime
   - overall pipeline overhead excluding new step baseline comparison

### Deliverables
- regression-safe test suite
- performance benchmark results
- release readiness summary

### Milestone
**M5: Validation evidence complete**

### Exit criteria
- 100% of existing passing roadmap tests still pass.
- New success criteria have direct test evidence.
- Runtime and overhead targets are measured and documented.

---

## Phase 6. Rollout, Monitoring, and Safe Adoption

### Objective
Deploy with controlled risk, especially around stricter gates.

### Key actions
1. Decide rollout mode for cross-reference enforcement:
   - immediate blocking
   - or temporary warning-first
2. Document failure-state semantics for degraded reports.
3. Update user/developer guidance for:
   - new CLI usage
   - fidelity status meanings
   - expected output artifacts
4. Monitor:
   - false positives
   - degraded-run frequency
   - pipeline time drift
   - LLM severity drift patterns
5. Prepare rollback plan for gate strictness if regressions appear in stored artifacts.

### Deliverables
- rollout checklist
- operational guidance
- monitoring metrics definition
- rollback trigger thresholds

### Milestone
**M6: Controlled production rollout**

### Exit criteria
- Team can distinguish clean pass, fail, skipped, and degraded states.
- Rollback path is tested and documented.

---

# 3. Risk Assessment and Mitigation Strategies

## Highest-Priority Risks

### 1. Schema ambiguity causes incompatible implementations
- **Source:** OQ-006
- **Impact:** Prompt builders, parsers, tests, and report consumers diverge.
- **Mitigation:**
  1. Resolve canonical schema in Phase 0.
  2. Publish one authoritative reference format.
  3. Bind tests to that format only.
- **Analyzer recommendation:** Treat this as a pre-implementation blocker.

### 2. Gate strictness changes break existing artifacts unexpectedly
- **Sources:** RSK-003, RSK-006
- **Impact:** Previously accepted outputs begin failing after rollout.
- **Mitigation:**
  1. Replay strict gates against `.dev/releases/complete/`.
  2. Use warning-first rollout if failure rate is material.
  3. Log exact failure reasons for migration.
- **Analyzer recommendation:** Require baseline artifact audit before enabling blocking behavior.

### 3. LLM severity inconsistency undermines trust in fidelity checks
- **Sources:** RSK-001, RSK-007
- **Impact:** Same deviation receives inconsistent severity or count reporting.
- **Mitigation:**
  1. Encode explicit severity definitions in prompts.
  2. Use conservative highest-severity resolution in multi-agent mode.
  3. Add optional count/table cross-validation if feasible.
  4. Track disagreement frequency in test fixtures.
- **Analyzer recommendation:** Prioritize deterministic parser and semantic guardrails over prompt-only trust.

### 4. Multi-agent mode is under-specified
- **Source:** OQ-007
- **Impact:** Merge semantics and failure handling may be inconsistent.
- **Mitigation:**
  1. Either fully define multi-agent invocation/merge behavior before Phase 2
  2. or defer multi-agent support behind an explicit non-default path
- **Analyzer recommendation:** Avoid partial implementation of multi-agent semantics.

### 5. Runtime overhead exceeds acceptable operational budget
- **Sources:** NFR-001, NFR-002, NFR-003, RSK-002, RSK-005
- **Impact:** Pipeline becomes too slow for routine use.
- **Mitigation:**
  1. Limit tasklist inputs intelligently.
  2. Measure wall-clock performance continuously.
  3. Distinguish soft target (120s) from hard timeout (600s).
- **Analyzer recommendation:** Make performance telemetry part of acceptance, not post-release observation.

### 6. State file corruption or ambiguous status states
- **Source:** RSK-008
- **Impact:** Pipeline recovery and downstream decision logic become unreliable.
- **Mitigation:**
  1. Keep writes additive and atomic where possible.
  2. Validate allowed status enum values.
  3. Ensure degraded writes always include explicit booleans.
- **Analyzer recommendation:** Treat state persistence as part of contract, not incidental metadata.

### 7. Retrospective content biases extraction
- **Source:** RSK-004
- **Impact:** New requirements may be under-detected.
- **Mitigation:**
  1. Phrase retrospective as advisory context only.
  2. Test prompt composition explicitly.
  3. Avoid converting retrospective content into implicit requirements.
- **Analyzer recommendation:** Keep extraction independent; retrospective should sharpen scrutiny, not redefine scope.

### 8. Validation layering violations create coupling
- **Source:** NFR-010 / AC-004
- **Impact:** Tasklist validation may inappropriately compare against original spec.
- **Mitigation:**
  1. Enforce immediate-upstream-only checks.
  2. Reflect this rule in prompts, tests, and CLI help.
- **Analyzer recommendation:** This should be guarded by tests because it is a subtle regression risk.

---

# 4. Resource Requirements and Dependencies

## Team / Capability Requirements

### Core engineering capabilities
1. **Pipeline/gate engineer**
   - executor wiring
   - gate enforcement
   - state persistence
2. **Prompt/validation engineer**
   - prompt builders
   - output schema enforcement
   - degraded report behavior
3. **CLI engineer**
   - Click subcommand integration
   - standalone validation UX
4. **QA/test engineer**
   - unit, integration, E2E, regression, performance validation
5. **Analyzer/reviewer**
   - ambiguity resolution
   - rollout risk review
   - artifact replay analysis

## Technical Dependencies
1. **Pipeline framework**
   - `src/superclaude/cli/pipeline/`
2. **Roadmap module**
   - `src/superclaude/cli/roadmap/`
3. **Click**
   - CLI registration and option parsing
4. **Python `re`**
   - semantic field extraction
5. **Python `dataclasses`**
   - typed report model
6. **Claude API**
   - fidelity validation execution
7. **Existing roadmap tests**
   - regression baseline
8. **`.roadmap-state.json`**
   - pipeline status persistence
9. **Existing pipeline artifacts**
   - regression replay corpus

## Artifact and Environment Requirements
- Representative spec/roadmap/tasklist fixtures
- Existing release artifacts for regression analysis
- Benchmarks for baseline pipeline timing
- Test matrix covering:
  - clean pass
  - HIGH deviation
  - degraded mode
  - malformed/missing frontmatter
  - dangling cross-references
  - fabricated traceability IDs

## Recommended Dependency Handling Order
1. Lock schema decisions
2. Prepare typed/reporting foundation
3. Wire gates and semantic checks
4. Add CLI and executor integration
5. Run regression and performance validation
6. Roll out strict enforcement

---

# 5. Success Criteria and Validation Approach

## Success Criteria Mapping

### Functional correctness
1. **Spec-fidelity blocks HIGH deviations**
   - Validate with integration test simulating `high_severity_count > 0`
2. **Spec-fidelity passes clean roadmap**
   - Validate with clean fixture
3. **Cross-reference validation enforced**
   - Unit tests for valid and invalid targets
4. **REFLECT semantic checks execute**
   - Confirm STRICT tier now triggers semantic evaluation
5. **Tasklist validation catches fabricated traceability**
   - E2E test on known-bad bundle
6. **Retrospective reaches extraction prompt**
   - Prompt composition test
7. **Degraded fidelity remains explicit and non-blocking**
   - Simulate agent failure after retry exhaustion
8. **State persistence records fidelity status**
   - Verify `.roadmap-state.json` contents
9. **Tasklist readiness consistency enforced**
   - Semantic check pass/fail tests
10. **`--no-validate` does not skip spec-fidelity**
   - Pipeline integration test

### Non-functional assurance
11. **No roadmap test regression**
   - `uv run pytest tests/roadmap/`
12. **Spec-fidelity runtime within target**
   - Wall-clock benchmark
13. **Tasklist runtime within target**
   - Wall-clock benchmark
14. **Pipeline overhead controlled**
   - compare against prior baseline
15. **Deviation reports are 100% parseable**
   - varied-format unit fixtures

## Validation Strategy

### A. Unit validation
- semantic checks
- dataclass serialization
- prompt generation content
- cross-reference resolution
- frontmatter parsing

### B. Integration validation
- step insertion in pipeline
- gate blocking/pass-through behavior
- state persistence
- `--no-validate` interaction
- degraded-mode report generation

### C. End-to-end validation
- CLI subcommand execution
- roadmap-to-tasklist fidelity review
- regression replay on archived artifacts

### D. Performance validation
- per-step execution timing
- aggregate overhead analysis
- large-input behavior assessment

### E. Rollout validation
- replay historical artifacts before enabling strict blocking
- compare warning-only vs blocking impact if needed

## Analyzer Recommendation
Every success criterion should have one of:
- a named automated test,
- a benchmark result,
- or a documented artifact replay outcome.

Anything not backed by one of those should not be considered done.

---

# 6. Timeline Estimates per Phase

Given the **moderate complexity (0.72)** and the concentration of risk in spec ambiguity and regression sensitivity, the roadmap should be executed in short, verification-heavy phases.

## Estimated Phase Timeline

1. **Phase 0 – Specification Reconciliation**
   - **Estimate:** 0.5–1.0 week
   - **Critical dependency:** stakeholder decisions on open questions

2. **Phase 1 – Foundation and Data Models**
   - **Estimate:** 0.5 week
   - **Focus:** dataclass, config extension, format reference

3. **Phase 2 – Spec-Fidelity Capability**
   - **Estimate:** 1.0–1.5 weeks
   - **Focus:** prompt builder, gate, executor, degraded handling, state persistence

4. **Phase 3 – Gate Integrity Hardening**
   - **Estimate:** 0.5–1.0 week
   - **Focus:** reflect promotion, cross-ref validation, semantic checks

5. **Phase 4 – Tasklist Fidelity Capability**
   - **Estimate:** 1.0 week
   - **Focus:** prompt builder, strict gate, CLI validate subcommand

6. **Phase 5 – Testing and Performance Validation**
   - **Estimate:** 1.0 week
   - **Focus:** unit/integration/E2E coverage, regression replay, runtime measurement

7. **Phase 6 – Rollout and Monitoring**
   - **Estimate:** 0.5 week
   - **Focus:** guarded rollout, operational guidance, rollback readiness

## Total Estimated Delivery Window
- **Best case:** 5.0 weeks
- **Expected case:** 5.5–6.0 weeks
- **Risk-adjusted case:** 6.5 weeks if open-question resolution or regression fallout delays strict rollout

## Timeline Notes
- The largest schedule risk is **not implementation volume**, but **decision latency** on open questions and **unexpected regressions** from stricter gate enforcement.
- If cross-reference or reflect strictness causes broad artifact failures, rollout should split into:
  1. implementation complete
  2. warning-first observation window
  3. blocking enforcement activation

---

# Actionable Recommendations

## Immediate next steps
1. Finalize the 8 open questions before coding begins.
2. Freeze the deviation report schema as a single canonical contract.
3. Replay current artifacts against proposed stricter gates early.
4. Treat degraded-mode semantics and state persistence as first-class acceptance criteria.
5. Add performance measurement during implementation, not after it.

## Analyzer Priority Order
1. **Ambiguity elimination**
2. **Gate correctness**
3. **Regression containment**
4. **Deterministic output parsing**
5. **Performance overhead control**
6. **Rollout safety**

## Final Assessment
This initiative is appropriately scoped for a moderate-complexity release, but only if handled as a **validation-hardening project**, not merely a feature-addition project. The roadmap should optimize for **trustworthiness, reproducibility, and safe enforcement** rather than maximizing new surface area.
