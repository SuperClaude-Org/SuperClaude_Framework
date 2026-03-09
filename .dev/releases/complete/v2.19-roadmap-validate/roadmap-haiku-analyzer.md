---
spec_source: "spec-roadmap-validate.md"
complexity_score: 0.65
primary_persona: analyzer
---

# Executive Summary

This roadmap delivers a new `superclaude roadmap validate <output-dir>` capability that validates roadmap pipeline outputs after generation and as a standalone command. The implementation is moderately complex because it spans CLI integration, subprocess orchestration, report gating, and post-pipeline automation, but the scope is controlled by strong architectural constraints and explicit infrastructure reuse requirements.

## Analyzer Assessment

1. **Primary delivery goal**
   - Add a validation pipeline that checks `roadmap.md`, `test-strategy.md`, and `extraction.md` across 7 dimensions and produces a structured `validation-report.md`.

2. **Primary implementation risks**
   - Multi-agent merge correctness.
   - `--resume` behavior producing misleading validations if gating boundaries are wrong.
   - Architecture drift via accidental reverse imports from `pipeline/*` into `validate_*`.

3. **Primary recommendations**
   - Implement in strict dependency order.
   - Treat gate definitions as the contract first, orchestration second.
   - Add targeted tests for failure-path semantics, especially resume, multi-agent merge, and exit-code behavior.

4. **Expected outcome**
   - A standalone and auto-invoked validation stage that is additive, low-risk to existing roadmap generation, and compatible with current executor infrastructure.

---

# Phased Implementation Plan with Milestones

## Phase 1 — Foundation and Contract Definition

### Objective
Establish the data model, validation contracts, and prompt/gate boundaries before orchestration logic is added.

### Key Workstreams
1. **Extend configuration models**
   - Add `ValidateConfig` to `src/superclaude/cli/roadmap/models.py`.
   - Include:
     - output directory
     - agents
     - model
     - max turns
     - debug
     - validation mode metadata as needed by executor/reporting

2. **Define validation gates**
   - Create `src/superclaude/cli/roadmap/validate_gates.py`.
   - Implement:
     - `REFLECT_GATE`
     - `ADVERSARIAL_MERGE_GATE`
   - Reuse existing gate infrastructure from `roadmap/gates.py`.
   - Enforce:
     - frontmatter presence
     - required field presence
     - non-empty semantic validation
     - minimum line count
     - agreement table requirement for merged mode

3. **Define validation prompts**
   - Create `src/superclaude/cli/roadmap/validate_prompts.py`.
   - Encode:
     - 7 validation dimensions
     - finding severity rules
     - report structure
     - false-positive suppression guidance
     - merged report conflict escalation rules

### Milestone
**M1: Validation contract frozen**
- `ValidateConfig` exists.
- Both gates implemented.
- Prompt templates defined for reflect and merge stages.
- No executor logic yet.

### Exit Criteria
- Gate rules can be reviewed independently.
- Prompt requirements trace to FR-008 through FR-014.
- No new infrastructure types introduced.

---

## Phase 2 — Standalone Validation Execution

### Objective
Build the standalone `validate` command path using existing subprocess and pipeline execution infrastructure.

### Key Workstreams
1. **Implement validation executor**
   - Create `src/superclaude/cli/roadmap/validate_executor.py`.
   - Validate required inputs before execution:
     - `roadmap.md`
     - `test-strategy.md`
     - `extraction.md`
   - Route execution by agent count:
     - 1 agent → sequential reflection only
     - 2+ agents → parallel reflections + sequential adversarial merge

2. **Implement output directory behavior**
   - Write outputs to `<output-dir>/validate/`.
   - Ensure:
     - single-agent mode produces `validation-report.md`
     - multi-agent mode produces `reflect-<agent-id>.md` and merged `validation-report.md`

3. **Integrate CLI subcommand**
   - Extend `src/superclaude/cli/roadmap/commands.py`.
   - Add `validate` subcommand with:
     - `--agents`
     - `--model`
     - `--max-turns`
     - `--debug`

4. **Enforce non-failing validation exit behavior**
   - Blocking issues must warn users in CLI output.
   - Validation findings must not force non-zero exit solely due to roadmap quality findings.

### Milestone
**M2: Standalone validate command functional**
- `superclaude roadmap validate <dir>` runs successfully in single-agent mode.
- Output report structure matches required frontmatter and body sections.

### Exit Criteria
- SC-001 satisfied.
- SC-007 behavior implemented.
- NFR-003 and NFR-004 satisfied.

---

## Phase 3 — Multi-Agent Reflection and Adversarial Merge

### Objective
Add parallel multi-agent validation with reliable merge semantics and agreement analysis.

### Key Workstreams
1. **Parallel reflection orchestration**
   - Reuse `execute_pipeline` and `ClaudeProcess`.
   - Ensure each agent gets isolated reflection execution.
   - Emit deterministic agent-specific filenames.

2. **Merged report generation**
   - Run sequential merge after all reflection outputs complete.
   - Produce:
     - final `validation-report.md`
     - Agent Agreement Analysis table
   - Enforce category mapping:
     - BOTH_AGREE
     - ONLY_A
     - ONLY_B
     - CONFLICT

3. **Conflict resolution policy**
   - Escalate severity disagreements to higher severity.
   - Deduplicate semantically equivalent findings.
   - Preserve source-agent provenance in merge metadata.

4. **Gate hardening**
   - Apply stricter semantic checks to merged report than individual reflections.
   - Confirm presence of agreement table and merged metadata fields.

### Milestone
**M3: Multi-agent validation operational**
- Parallel reflection files generated.
- Merged report generated with agreement table.
- Severity conflict escalation verified.

### Exit Criteria
- SC-003 satisfied.
- FR-012 through FR-014 satisfied.
- NFR-005 validated by shared execution path design.

---

## Phase 4 — Roadmap Pipeline Auto-Invocation Integration

### Objective
Attach validation to `roadmap run` without violating dependency constraints or introducing confirmation bias.

### Key Workstreams
1. **Modify `execute_roadmap()`**
   - In `src/superclaude/cli/roadmap/executor.py`, auto-invoke validation after successful completion of the 8-step pipeline.
   - Inherit:
     - `--agents`
     - `--model`
     - `--max-turns`
     - `--debug`

2. **Add `--no-validate` control**
   - Extend `roadmap run` options in `commands.py`.
   - Ensure explicit opt-out disables post-run validation only.

3. **Implement resume behavior**
   - If `--resume` reaches successful final artifacts, validation still runs.
   - If resumed execution halts before pipeline success, validation is skipped.

4. **Preserve architectural direction**
   - Confirm no imports from `validate_*` into `pipeline/*`.
   - Keep validation dependent on roadmap artifacts, not vice versa.

### Milestone
**M4: Validation integrated into roadmap run**
- Auto-validation occurs after successful roadmap generation.
- `--no-validate` bypass works.
- Resume semantics behave as specified.

### Exit Criteria
- SC-004 and SC-005 satisfied.
- FR-005 through FR-007 satisfied.
- NFR-002 satisfied.

---

## Phase 5 — Validation Logic Verification and Test Coverage

### Objective
Prove correctness through focused unit and integration testing, especially around the failure and edge-case boundaries.

### Key Workstreams
1. **Unit tests**
   - Gate validation:
     - missing frontmatter fields
     - empty semantic values
     - line count thresholds
     - agreement table enforcement
   - Config parsing:
     - agent parsing
     - default handling
   - Report semantics:
     - `tasklist_ready == (blocking_issues_count == 0)`

2. **Integration tests**
   - Standalone single-agent validation.
   - Standalone multi-agent validation.
   - `roadmap run` auto-invokes validation.
   - `roadmap run --no-validate` skips validation.
   - `--resume` success path runs validation.
   - `--resume` failed-step path skips validation.

3. **Known-defect detection tests**
   - Duplicate D-ID detection.
   - Missing milestone reference detection.
   - Untraced requirement detection.
   - Cross-file inconsistency detection.

4. **Architecture verification**
   - Grep/assert no reverse imports from `pipeline/*` into `validate_*`.
   - Verify infrastructure reuse.

### Milestone
**M5: Test suite passes and behavior locked**
- All required unit and integration tests pass.
- Behavioral regressions are guarded.

### Exit Criteria
- SC-006, SC-008, SC-009 satisfied.
- Evidence exists for all major requirement clusters.

---

## Phase 6 — Performance, Usability, and Release Hardening

### Objective
Validate non-functional constraints and reduce operational surprises before release.

### Key Workstreams
1. **Performance measurement**
   - Measure single-agent validation wall time.
   - Compare validation overhead against full roadmap pipeline duration.
   - Confirm target overhead ≤10%.

2. **CLI output refinement**
   - Make blocking findings visible but non-fatal.
   - Ensure debug mode is actionable.
   - Clearly distinguish:
     - validation execution failure
     - validation report findings

3. **Operational documentation**
   - Document standalone use.
   - Document multi-agent trade-offs.
   - Document `--no-validate` and `--resume` semantics.

4. **Open-question triage**
   - Decide whether standalone default should remain single-agent.
   - Decide failure semantics when one reflection agent fails gating.
   - Clarify interleave ratio calculation.

### Milestone
**M6: Release-ready validation workflow**
- Meets performance target.
- Behavior documented.
- Open questions either resolved or explicitly deferred.

### Exit Criteria
- NFR-001 through NFR-007 reviewed and either validated or explicitly tracked.

---

# Risk Assessment and Mitigation Strategies

## High-Priority Risks

### 1. Adversarial merge produces inconsistent or misleading final findings
- **Risk ID**: R-004
- **Impact**: High on trustworthiness of final report.
- **Likelihood**: Medium.
- **Mitigation**
  1. Treat merged report gate as stricter than reflection gates.
  2. Require explicit agreement table.
  3. Force severity escalation on disagreements.
  4. Add integration tests with intentionally conflicting reflection inputs.

### 2. Resume semantics validate incomplete artifacts
- **Risk ID**: R-005
- **Impact**: High on correctness.
- **Likelihood**: Medium.
- **Mitigation**
  1. Gate validation invocation on final pipeline success only.
  2. Add explicit tests for resumed-success and resumed-failure branches.
  3. Keep validation state separate from roadmap execution state unless future requirements demand tracking.

### 3. Architectural drift violates unidirectional dependency rule
- **Risk ID**: NFR-derived architectural risk
- **Impact**: High on maintainability.
- **Likelihood**: Medium.
- **Mitigation**
  1. Implement files in specified order.
  2. Add grep-based architecture test in CI.
  3. Restrict validate modules to importing shared roadmap/pipeline primitives only.

## Medium-Priority Risks

### 4. False positives waste user time
- **Risk ID**: R-001
- **Impact**: Medium.
- **Likelihood**: Medium.
- **Mitigation**
  1. Add explicit prompt instruction to avoid speculative blocking findings.
  2. Use multi-agent merge to deduplicate unsupported concerns.
  3. Prefer evidence-linked findings with concrete location and fix guidance.

### 5. Token and wall-time cost grows in multi-agent mode
- **Risk ID**: R-002
- **Impact**: Medium.
- **Likelihood**: Medium.
- **Mitigation**
  1. Preserve single-agent standalone default unless data disproves it.
  2. Reuse existing executor infrastructure instead of adding orchestration layers.
  3. Limit validation inputs to final artifact set only.
  4. Measure and report overhead.

## Low-Priority Risks

### 6. Reflect gate allows shallow outputs
- **Risk ID**: R-003
- **Impact**: Low to medium.
- **Likelihood**: Medium.
- **Mitigation**
  1. Keep semantic checks, not just line-count checks.
  2. Add negative tests for minimal-but-useless reports.
  3. Tighten prompt structure if shallow outputs appear in test data.

### 7. Shared helper coupling becomes brittle
- **Risk ID**: R-006
- **Impact**: Low.
- **Likelihood**: Low.
- **Mitigation**
  1. Reuse only pure helper functions.
  2. Avoid deeper shared state or implicit contracts.
  3. Document the acceptable coupling boundary.

---

# Resource Requirements and Dependencies

## Engineering Resources

### Core implementation
1. **CLI/Executor engineer**
   - Owns command wiring, config parsing, executor integration.
2. **Validation logic engineer**
   - Owns gates, prompts, report semantics.
3. **QA/test engineer**
   - Owns unit/integration coverage and edge-case validation.

### Optional review support
1. **Architecture reviewer**
   - Confirms dependency direction and infrastructure reuse.
2. **Performance reviewer**
   - Confirms ≤10% overhead target and ≤2 minute single-agent target.

## Code Dependencies

1. `src/superclaude/cli/roadmap/commands.py`
2. `src/superclaude/cli/roadmap/executor.py`
3. `src/superclaude/cli/roadmap/models.py`
4. `src/superclaude/cli/roadmap/gates.py`
5. `src/superclaude/cli/roadmap/pipeline/executor.py`
6. `click`
7. `ClaudeProcess`
8. `AgentSpec`

## Infrastructure Constraints

1. No new orchestration framework.
2. No new subprocess abstraction.
3. No reverse imports into `pipeline/*`.
4. Validation must run as an isolated Claude subprocess.
5. Outputs must remain under `<output-dir>/validate/`.

## External/Process Dependencies

1. Existing roadmap generation artifacts must be valid and present.
2. Existing gate framework must support the needed semantic checks.
3. Existing subprocess execution must support sequential and parallel validation stages.
4. Test fixtures or fixture directories must be available to simulate both clean and flawed roadmap outputs.

---

# Success Criteria and Validation Approach

## Success Criteria Mapping

1. **SC-001 — Standalone command produces valid report**
   - Validate via integration test against sample output dir.
   - Assert frontmatter fields exist and parse.

2. **SC-002 — Single-agent ≤2 minutes**
   - Validate via timed execution on representative fixture.

3. **SC-003 — Multi-agent mode produces reflection files and merged report**
   - Assert presence of:
     - `reflect-<agent-id>.md`
     - `validation-report.md`
     - agreement table content

4. **SC-004 — `roadmap run` auto-validates**
   - Assert `validate/` directory exists after successful run.

5. **SC-005 — `--no-validate` skips auto-validation**
   - Assert `validate/` directory absent.

6. **SC-006 — Known defects detected as blocking**
   - Feed seeded flawed artifacts and assert blocking issue entries.

7. **SC-007 — Blocking findings keep exit code 0**
   - Assert process exit code remains success while CLI warnings are emitted.

8. **SC-008 — Test suite passes**
   - Run all targeted unit/integration tests.

9. **SC-009 — No forbidden import direction**
   - Grep/assert architecture rule across `pipeline/*`.

## Validation Approach

### Functional validation
- Use golden-path fixtures for valid roadmap output.
- Use defect-injection fixtures for known blocking issues.
- Test both single-agent and multi-agent paths.

### Structural validation
- Parse report YAML frontmatter.
- Assert required body sections:
  - Summary
  - Blocking Issues
  - Warnings
  - Info
  - Validation Metadata

### Behavioral validation
- Confirm `tasklist_ready` flips to `true` only at zero blocking issues.
- Confirm warnings and infos do not affect exit code.
- Confirm merge severity escalation behavior.

### Architectural validation
- Grep-based import boundary test.
- Review for executor/gate reuse and zero new infrastructure types.

### Performance validation
- Time-box single-agent execution.
- Compare added validation time against base roadmap pipeline runtime.

---

# Timeline Estimates per Phase

## Overall Estimate
Given the moderate complexity and bounded scope, this work is suitable for a **6-phase delivery across roughly 2 to 3 implementation iterations**.

## Phase-by-Phase Estimates

1. **Phase 1 — Foundation and Contract Definition**
   - **Estimate**: 0.5-1 day
   - **Reasoning**: Low implementation volume, high importance. Must be correct before orchestration starts.

2. **Phase 2 — Standalone Validation Execution**
   - **Estimate**: 1-1.5 days
   - **Reasoning**: Core executor path, CLI wiring, and output handling are the first real integration point.

3. **Phase 3 — Multi-Agent Reflection and Adversarial Merge**
   - **Estimate**: 1-1.5 days
   - **Reasoning**: Highest logic risk due to merge correctness, conflict handling, and agreement table semantics.

4. **Phase 4 — Roadmap Pipeline Auto-Invocation Integration**
   - **Estimate**: 0.5-1 day
   - **Reasoning**: Small code surface, but behaviorally sensitive due to `--resume` and `--no-validate`.

5. **Phase 5 — Validation Logic Verification and Test Coverage**
   - **Estimate**: 1-1.5 days
   - **Reasoning**: Test depth is essential because most risk is in edge-case behavior rather than volume of code.

6. **Phase 6 — Performance, Usability, and Release Hardening**
   - **Estimate**: 0.5 day
   - **Reasoning**: Final measurement, output refinement, and documentation.

## Critical Path

1. `models.py`
2. `validate_gates.py` and `validate_prompts.py`
3. `validate_executor.py`
4. `commands.py` and `executor.py`
5. tests
6. performance validation

## Schedule Risks

1. **Merge semantics ambiguity**
   - Could extend Phase 3 if agreement categorization needs iteration.

2. **Resume edge-case clarification**
   - Could extend Phase 4 if current pipeline state handling is less explicit than assumed.

3. **Interleave ratio ambiguity**
   - Could delay final prompt stabilization if detection expectations are inconsistent.

---

# Recommended Implementation Priorities

1. **Priority 1**
   - Gate definitions and report contracts.
   - Reason: They govern correctness across all later stages.

2. **Priority 2**
   - Standalone single-agent path.
   - Reason: Lowest complexity path; establishes end-to-end vertical slice.

3. **Priority 3**
   - Multi-agent merge path.
   - Reason: Highest correctness risk and most likely source of regressions.

4. **Priority 4**
   - Auto-validation integration into `roadmap run`.
   - Reason: Depends on stable standalone executor semantics.

5. **Priority 5**
   - Performance tuning and documentation.
   - Reason: Important, but only after behavioral correctness is proven.

---

# Final Analyzer Recommendation

Proceed with implementation, but treat this as a **contract-first integration** rather than a CLI feature-first change. The main failure modes are not around command wiring; they are around **false confidence**, **merge correctness**, **resume gating**, and **architectural drift**. If the team locks report contracts and gate semantics first, the remaining implementation risk stays manageable and aligned with the moderate complexity score.
