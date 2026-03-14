---
spec_source: "portify-release-spec.md"
complexity_score: 0.85
primary_persona: architect
---

# 1. Executive summary

This roadmap delivers a **programmatic CLI portification pipeline** for the `sc-cli-portify` workflow by extending the existing `pipeline/` and `sprint/` architecture without modifying those base modules. The target system is a **7-step, 4-phase synchronous pipeline** that combines fast deterministic Python-controlled flow with bounded Claude-assisted analysis and review.

## Architectural priorities

1. **Preserve architectural invariants**
   - Keep all new implementation under `src/superclaude/cli/cli_portify/`.
   - Make **zero changes** to `pipeline/` and `sprint/`.
   - Enforce **runner-authored truth** and **deterministic flow control**.

2. **Separate deterministic logic from model-assisted reasoning**
   - Steps 1-2 must be pure programmatic and fast.
   - Steps 3-7 must be executor-controlled, artifact-driven, and gate-enforced.
   - Claude assists with content generation, but **never controls sequencing or status**.

3. **Design for failure containment and resumability**
   - All steps emit observable artifacts.
   - Failure paths must still produce populated contracts.
   - Resume boundaries must be explicit, especially for `synthesize-spec`, `brainstorm-gaps`, and `panel-review`.

4. **Optimize for operability over cleverness**
   - Synchronous polling only.
   - Explicit gate tiers: EXEMPT, STANDARD, STRICT.
   - Strong monitoring, diagnostics, and user review checkpoints.

## Delivery objective

Produce a working `cli_portify` command group that:
- validates and inventories workflows quickly,
- generates roadmap/spec artifacts through controlled Claude subprocesses,
- supports user review gates and dry-run behavior,
- converges panel review within bounded iterations,
- emits a complete machine-readable contract on every exit path.

---

# 2. Phased implementation plan with milestones

## Phase 0 - Architecture confirmation and delivery scaffolding

### Goals
Establish implementation boundaries, confirm unresolved spec ambiguities, and lock module layout before code changes.

### Work items
1. **Confirm authoritative spec interpretations**
   - Resolve timeout semantics for convergence iterations.
   - Resolve resume behavior for partially written `synthesize-spec`.
   - Resolve scoring precision vs downstream gate boundary handling.
   - Resolve authoritative module/file layout where Section 4.1 and 4.6 differ.

2. **Freeze implementation architecture**
   - Confirm 18-module `cli_portify/` structure.
   - Define ownership of:
     - config/model layer,
     - step implementations,
     - process wrapper,
     - monitor/logging,
     - contract emission,
     - CLI integration.

3. **Define artifact contract**
   - Standardize output artifact names and locations.
   - Standardize frontmatter parsing/validation behavior.
   - Standardize failure/default population rules for contracts.

### Milestone
- **M0: Architecture baseline approved**
  - Open questions triaged into:
    1. must-resolve before implementation,
    2. safe defaults acceptable,
    3. defer-to-follow-up.

### Deliverables
- Implementation decision record.
- Final module map.
- Step/artifact interface table.

---

## Phase 1 - Deterministic foundation and CLI skeleton

### Goals
Build the non-Claude substrate first so orchestration rests on stable primitives.

### Work items
1. **Create configuration and domain model layer**
   - Implement `PortifyConfig extends PipelineConfig`.
   - Implement `PortifyStepResult extends StepResult`.
   - Define step metadata, artifact paths, gate tier metadata, timeout settings, review flags, and resume metadata.

2. **Implement CLI registration**
   - Add `cli_portify_group` and register with `main.py`.
   - Define options for:
     - workflow path,
     - output directory,
     - `--dry-run`,
     - `--skip-review`,
     - `--start`,
     - convergence/budget controls,
     - timeout controls.

3. **Implement contract and status model**
   - Define success/partial/failed/dry_run contract schema.
   - Ensure all failure paths populate defaults.
   - Define resume command generation logic.

4. **Implement shared utility layer**
   - Frontmatter parsing helpers.
   - file existence/writability checks.
   - section hashing utilities for additive-only verification.
   - line counting and artifact rendering helpers.

### Architect emphasis
This phase must produce the **stable backbone** before any subprocess orchestration is introduced. Configuration drift or ambiguous contracts here will multiply failure modes later.

### Milestone
- **M1: CLI and model foundation operational**

### Exit criteria
- CLI command parses correctly.
- Base config/result types compile and integrate with current architecture.
- Contract objects can be emitted for mocked success and failure flows.

---

## Phase 2 - Fast deterministic pipeline steps

### Goals
Implement the two pure-programmatic steps to establish reliable early-phase execution and fast failure detection.

### Work items
1. **Implement `validate-config`**
   - Resolve workflow path to valid skill directory containing `SKILL.md`.
   - Derive CLI name:
     - strip `sc-`,
     - strip `-protocol`,
     - normalize naming case.
   - Validate output directory writability.
   - Detect collisions with existing non-portified CLI modules.
   - Write `validate-config-result.json`.

2. **Implement `discover-components`**
   - Inventory:
     - `SKILL.md`,
     - `refs/`,
     - `rules/`,
     - `templates/`,
     - `scripts/`,
     - matching command files.
   - Count lines accurately.
   - Generate `component-inventory.md` with required frontmatter.

3. **Implement deterministic gate checks**
   - Runtime limits as advisory/performance checks.
   - Structure validation for inventory output.
   - Defensive behavior for large files if size cap decision is adopted.

### Milestone
- **M2: Deterministic entry pipeline complete**

### Exit criteria
1. `validate-config` completes under target conditions with correct failure codes.
2. `discover-components` produces accurate inventory output.
3. Both steps run without Claude subprocesses.
4. Unit coverage exists for success and failure matrices.

---

## Phase 3 - Claude subprocess orchestration core

### Goals
Introduce the executor-managed Claude integration safely, with subprocess isolation, path scoping, monitoring, and gate enforcement.

### Work items
1. **Implement `PortifyProcess`**
   - Extend base `pipeline.ClaudeProcess`.
   - Pass `--add-dir` for both work directory and workflow path.
   - Support prompt construction with `@path` references.
   - Capture exit code, stdout/stderr, timeout state, and diagnostics.

2. **Implement prompt builder framework**
   - One builder per Claude-assisted step.
   - Inputs reference prior artifacts via `@path`.
   - Include step-specific output contracts and frontmatter expectations.
   - Include retry augmentation for targeted failures, especially placeholder residue.

3. **Implement monitoring and diagnostics**
   - NDJSON/JSONL event logging.
   - signal extraction from subprocess output.
   - timing capture for phases and steps.
   - failure classification:
     - timeout,
     - missing artifact,
     - malformed frontmatter,
     - gate failure,
     - user rejection,
     - budget exhaustion.

4. **Implement gate engine bindings**
   - Ensure every gate function returns `tuple[bool, str]`.
   - Add structural and semantic validators for STRICT/STANDARD outputs.
   - Ensure status is derived only from observed artifacts and gate results.

### Milestone
- **M3: Controlled subprocess platform ready**

### Exit criteria
- Claude-assisted steps can be executed in a harness with mocked or real subprocess behavior.
- Monitoring emits consistent machine-readable records.
- Gate engine integration is stable and deterministic.

---

## Phase 4 - Phase 1/2 content generation steps

### Goals
Deliver the core design intelligence of the pipeline: workflow analysis, pipeline design, and spec synthesis.

### Work items
1. **Implement `analyze-workflow`**
   - Read discovered components via `@path`.
   - Produce `portify-analysis.md`.
   - Enforce required sections:
     - behavioral flow,
     - step boundaries,
     - programmatic spectrum classification,
     - dependency/parallel groups,
     - gate requirements,
     - data flow diagram.
   - Enforce line budget and frontmatter requirements.

2. **Implement `design-pipeline`**
   - Produce `portify-spec.md`.
   - Define:
     - Step graph,
     - domain models,
     - prompt builder specs,
     - gate criteria,
     - pure-programmatic runnable code plan,
     - executor loop,
     - Click CLI integration.
   - Add dry-run stop behavior here.
   - Add user review gate here.

3. **Implement `synthesize-spec`**
   - Instantiate `release-spec-template.md`.
   - Populate all required sections from prior outputs.
   - Enforce zero `{{SC_PLACEHOLDER:*}}` residue.
   - Retry with targeted placeholder list if failure occurs.
   - Include consolidation mapping table.

### Architect emphasis
These steps define the **translation from workflow to executable architecture**. Quality here determines whether downstream brainstorming and panel review refine a good design or merely expose a weak one.

### Milestone
- **M4: Core spec generation complete**

### Exit criteria
1. All three artifacts are generated and gated successfully.
2. `--dry-run` halts after `design-pipeline` with correct contract semantics.
3. Retry logic for unresolved placeholders is working and bounded.

---

## Phase 5 - Quality amplification steps

### Goals
Add controlled critique loops without surrendering orchestration authority to Claude.

### Work items
1. **Implement `brainstorm-gaps`**
   - Pre-flight skill availability check for `/sc:brainstorm`.
   - Invoke skill with required flags.
   - Provide inline fallback with warning if unavailable.
   - Post-process results into structured findings.
   - Incorporate actionable findings into spec sections with `[INCORPORATED]`.
   - Route unresolved items to Section 11 as `[OPEN]`.
   - Append Section 12 summary.
   - Accept zero-gap outcome as valid.

2. **Implement `panel-review`**
   - Pre-flight skill availability check for `/sc:spec-panel`.
   - One subprocess per iteration.
   - Each iteration must include both:
     - focus discussion,
     - critique pass.
   - Parse convergence markers and quality scores.
   - Compute `overall` as mean of 4 dimensions.
   - Enforce `overall >= 7.0` readiness gate.
   - Support terminal states:
     - CONVERGED,
     - ESCALATED.

3. **Implement convergence control**
   - TurnLedger pre-launch budget guard.
   - independent per-iteration timeout.
   - bounded `max_convergence`.
   - resume semantics for review steps.

4. **Implement additive-only protection**
   - Section hashing verifies review phases append/extend only.
   - Prevent destructive rewrites in review stages.

### Milestone
- **M5: Review and convergence pipeline operational**

### Exit criteria
1. Brainstorm step passes with findings or zero-gap summary.
2. Panel review stops correctly on convergence or escalation.
3. Quality scoring and downstream readiness are computed deterministically.
4. Additive-only protection is enforced.

---

## Phase 6 - UX, resume, and operational hardening

### Goals
Make the system usable in real workflows, not just correct in narrow successful paths.

### Work items
1. **Implement TUI/live status experience**
   - show current step,
   - gate state,
   - timing,
   - current iteration,
   - review pause prompts,
   - warnings/advisories.

2. **Implement user review gates**
   - Pause TUI when review required.
   - Prompt on stderr.
   - Continue on `y`, halt with `USER_REJECTED` on `n`.

3. **Implement resume semantics**
   - Define resumable steps clearly.
   - Preserve prior context for review steps.
   - Generate correct `--start` commands and budget suggestions.

4. **Implement comprehensive failure-path handling**
   - missing template,
   - missing skills,
   - malformed artifact,
   - timeout,
   - partial artifact,
   - non-writable output,
   - exhausted budget.

### Milestone
- **M6: Operational resilience complete**

### Exit criteria
- Resume behavior works for intended boundaries.
- All exit paths emit complete contracts.
- User review interaction is reliable and testable.

---

## Phase 7 - Validation, compliance, and release readiness

### Goals
Prove the implementation meets both functional and non-functional requirements before merge.

### Work items
1. **Unit testing**
   - validation rules,
   - naming derivation,
   - gate functions,
   - score calculations,
   - contract defaults,
   - hashing/additive protections,
   - resume command generation.

2. **Integration testing**
   - full happy path,
   - `--dry-run`,
   - review rejection,
   - brainstorm fallback,
   - panel fallback/marker parsing,
   - convergence boundary cases,
   - template missing case.

3. **Compliance verification**
   - zero `async def` / `await`,
   - zero diffs in `pipeline/` and `sprint/`,
   - gate signatures compliant,
   - runner-authored truth enforced.

4. **Performance verification**
   - Phase 3 advisory budget,
   - Phase 4 advisory budget,
   - early deterministic steps within required limits.

5. **Developer readiness**
   - command help text,
   - example invocation,
   - artifact expectations,
   - troubleshooting notes.

### Milestone
- **M7: Release-ready implementation**

### Exit criteria
- Success criteria satisfied or explicitly waived with evidence.
- No architectural constraint violations remain.
- Merge candidate is ready.

---

# 3. Risk assessment and mitigation strategies

## A. High-priority risks

### 1. Claude output truncation in later steps
- **Impact**
  - incomplete artifacts,
  - malformed frontmatter,
  - hidden placeholder residue,
  - failed convergence evidence.
- **Mitigation**
  1. Use `@path` references instead of inline embedding.
  2. Keep prompts concise and artifact-specific.
  3. Enforce output size expectations per step.
  4. Validate artifact completeness structurally before semantic checks.
- **Architect recommendation**
  - Treat prompt budget and artifact size as first-class architecture constraints, not prompt-tuning details.

### 2. Incorrect convergence prompt design in `panel-review`
- **Impact**
  - false non-convergence,
  - wasted iterations,
  - unusable quality scoring.
- **Mitigation**
  1. Lock iteration contract: each iteration includes both focus and critique.
  2. Add integration tests validating iteration prompt shape.
  3. Record per-iteration mode execution in diagnostics.
- **Architect recommendation**
  - Model the convergence loop as a deterministic state machine with explicit entry/exit criteria.

### 3. Long wall-clock time from sequential execution
- **Impact**
  - operator frustration,
  - timeout exposure,
  - poor perceived reliability.
- **Mitigation**
  1. Preserve current 7-step consolidation.
  2. Keep pure-programmatic steps fast.
  3. Add phase timing telemetry and advisory warnings.
  4. Optimize prompt sizes and artifact reuse.
- **Architect recommendation**
  - Do not introduce async complexity; optimize by reducing work, not changing concurrency model.

## B. Medium-priority risks

### 4. Budget exhaustion before convergence
- **Mitigation**
  - TurnLedger pre-flight checks,
  - estimated cost per iteration,
  - early ESCALATED terminal state,
  - clear resume guidance.

### 5. Skill availability or non-machine-readable output
- **Mitigation**
  - pre-flight skill checks,
  - inline fallback prompts,
  - executor-side parsing,
  - structural fallback validation where markers are missing.

### 6. `@path` scope failures for subprocess file access
- **Mitigation**
  - always pass `--add-dir` for work dir and workflow path,
  - integration test with out-of-dir artifacts,
  - classify scope failures distinctly in diagnostics.

### 7. Resume ambiguity after partial spec synthesis
- **Mitigation**
  - formalize step-level resumability matrix,
  - define whether partial files are replaced or continued,
  - prefer re-running `synthesize-spec` over trusting partially gated output.

### 8. Missing template at runtime
- **Mitigation**
  - validate template presence during startup or before synthesis,
  - emit deterministic failure contract,
  - surface remediation path immediately.

## C. Low-priority risk

### 9. Self-portification circularity
- **Mitigation**
  - treat source skill files as read-only inputs,
  - isolate generated output directory,
  - test against self-referential scenarios only after core stability is proven.

---

# 4. Resource requirements and dependencies

## Team/role requirements

1. **Architect / lead implementer**
   - Owns module boundaries, flow control, and invariant protection.
2. **Backend/Python implementer**
   - Builds CLI, models, step runners, contracts, diagnostics.
3. **QA engineer**
   - Owns boundary tests, failure-path coverage, resume behavior validation.
4. **Optional UX/TUI contributor**
   - Improves live rendering and review pause experience.

## Technical dependencies

1. **Existing internal base modules**
   - `pipeline.models`
   - `pipeline.gates`
   - `pipeline.process`
   - `sprint.models`
   - `sprint.process`

2. **Tool/runtime dependencies**
   - `claude` binary in PATH
   - Click >= 8.0.0
   - Rich >= 13.0.0
   - PyYAML
   - Python >= 3.10
   - UV execution environment

3. **Workflow content dependencies**
   - `/sc:brainstorm`
   - `/sc:spec-panel`
   - `release-spec-template.md`

## Artifact requirements

1. `validate-config-result.json`
2. `component-inventory.md`
3. `portify-analysis.md`
4. `portify-spec.md`
5. synthesized release spec
6. brainstorm findings/augmented spec sections
7. `panel-report.md`
8. final return contract
9. step/phase timing and diagnostic logs

## Environmental requirements

1. Synchronous execution environment only.
2. Writable output directory.
3. Stable filesystem visibility for `@path` references.
4. Local test harness able to run via `uv run pytest`.

## Dependency management recommendations

1. **Validate external prerequisites early**
   - `claude` binary,
   - template existence,
   - skill availability.
2. **Prefer graceful degradation for optional skill behavior**
   - brainstorm/spec-panel fallbacks.
3. **Do not degrade core invariants**
   - if base architecture assumptions fail, stop explicitly rather than improvising.

---

# 5. Success criteria and validation approach

## Success criteria alignment

### Functional validation
1. `validate-config` meets correctness and runtime requirements.
2. `discover-components` produces complete inventory with accurate counts.
3. `analyze-workflow` passes STRICT gate and includes required sections.
4. `design-pipeline` passes STRICT gate and supports dry-run/user review.
5. `synthesize-spec` leaves zero placeholder sentinels.
6. `brainstorm-gaps` produces structurally valid summary output.
7. `panel-review` terminates with valid convergence state within limits.

### Non-functional validation
1. No `async def` or `await` under `cli_portify/`.
2. All gate functions return `tuple[bool, str]`.
3. All status determination is runner-authored.
4. No changes to `pipeline/` or `sprint/`.
5. Failure contracts always populate defaults.
6. Review-phase spec edits are additive-only.
7. User review gates behave correctly.

## Validation strategy

### 1. Unit test layer
- Focus on deterministic logic:
  - path validation,
  - naming derivation,
  - frontmatter parsing,
  - score math,
  - gate result helpers,
  - hashing,
  - resume command generation,
  - contract defaults.

### 2. Integration test layer
- Focus on orchestration:
  - subprocess execution behavior,
  - artifact chaining,
  - gate enforcement,
  - fallback skill behavior,
  - dry-run,
  - review rejection,
  - convergence boundaries,
  - timeout behavior.

### 3. Compliance checks
- Grep/code inspection for async prohibition.
- `git diff` enforcement for base-module immutability.
- Type and signature checks for gate functions.

### 4. Architectural validation
- Verify:
  1. no Claude-directed sequencing,
  2. all decisions derive from observed artifacts,
  3. resume boundaries are deterministic,
  4. additive-only review guarantees hold.

## Evidence package for release readiness

1. Test results for all functional criteria.
2. Example output artifacts from happy path.
3. Failure-path contract samples.
4. `git diff` proof for no base-module modifications.
5. Search proof for no async usage.
6. Boundary tests for:
   - `overall >= 7.0`,
   - convergence termination,
   - placeholder elimination,
   - dry-run stop point.

---

# 6. Timeline estimates per phase

## Estimated roadmap by phase

### Phase 0 - Architecture confirmation
- **Estimate**: 0.5-1 day
- **Reasoning**
  - Limited coding, high decision leverage.
  - Should be completed before implementation expands.

### Phase 1 - Deterministic foundation and CLI skeleton
- **Estimate**: 1-2 days
- **Reasoning**
  - Moderate implementation scope with low uncertainty.
  - Core types and CLI integration need careful alignment with existing architecture.

### Phase 2 - Fast deterministic pipeline steps
- **Estimate**: 1-1.5 days
- **Reasoning**
  - Straightforward logic, but requires complete error matrix coverage and artifact formatting.

### Phase 3 - Claude subprocess orchestration core
- **Estimate**: 2-3 days
- **Reasoning**
  - Highest infrastructure complexity.
  - Monitoring, diagnostics, subprocess handling, and gate wiring are foundational and failure-sensitive.

### Phase 4 - Core content-generation steps
- **Estimate**: 2-3 days
- **Reasoning**
  - Prompt/artifact design and semantic validation are complex.
  - Retry behavior and dry-run handling add edge cases.

### Phase 5 - Quality amplification steps
- **Estimate**: 2-3 days
- **Reasoning**
  - Convergence logic, additive-only enforcement, and fallback review handling are architecturally delicate.

### Phase 6 - UX, resume, and hardening
- **Estimate**: 1.5-2 days
- **Reasoning**
  - Operational polish and resume semantics often expose latent design flaws.

### Phase 7 - Validation and release readiness
- **Estimate**: 1.5-2.5 days
- **Reasoning**
  - Test breadth is substantial given 18 requirements, 9 risks, and multiple boundary conditions.

## Total estimated implementation span
- **Estimate**: 10.5-18 days of focused engineering work**

## Recommended milestone cadence

1. **Week 1**
   - Phase 0-3 complete
   - deterministic foundation and subprocess platform established

2. **Week 2**
   - Phase 4-6 complete
   - core generation, review loop, and hardening delivered

3. **Week 3 buffer / release validation**
   - Phase 7 completion
   - remediation of defects found during integration validation

---

# Recommended implementation order

1. Phase 0 architecture decisions
2. Phase 1 models/CLI/contracts
3. Phase 2 deterministic steps
4. Phase 3 subprocess/gates/monitoring
5. Phase 4 analysis/design/synthesis
6. Phase 5 brainstorm/panel convergence
7. Phase 6 resume/review/TUI hardening
8. Phase 7 validation and release readiness

---

# Final architect recommendations

1. **Resolve spec ambiguities before coding the convergence loop**
   - timeout semantics,
   - resume semantics,
   - scoring boundary/rounding behavior.

2. **Treat contracts, gates, and artifacts as the real system boundary**
   - not prompts, not prose outputs.

3. **Bias toward explicit state machines**
   - especially for review gates, convergence, resume, and failure classification.

4. **Keep the implementation additive and isolated**
   - no leakage into `pipeline/` or `sprint/`.

5. **Validate the hardest invariants continuously**
   - deterministic control,
   - runner-authored truth,
   - additive-only review behavior,
   - full contract emission on all exits.

If these priorities are maintained, the roadmap supports a reliable v4 CLI portification capability without destabilizing the existing framework architecture.
