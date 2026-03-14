---
spec_source: "portify-release-spec.md"
complexity_score: 0.85
adversarial: true
---

# CLI-Portify v2.24 — Final Merged Roadmap

## Executive Summary

This roadmap delivers a programmatic CLI portification pipeline (`cli_portify`) that converts inference-based SuperClaude workflows (skills/commands) into repeatable, programmatic CLI pipelines. The system extends the existing `pipeline/` and `sprint/` architecture with 18 new modules under `src/superclaude/cli/cli_portify/`, making zero modifications to base modules.

### Architectural Characteristics

- **Synchronous-only execution model** (no async/await)
- **7 consolidated steps across 4 phases**: 2 pure-programmatic, 5 Claude-assisted
- **Convergence loop** in panel-review with budget guards and escalation
- **Zero modifications** to existing `pipeline/` and `sprint/` base modules
- **Skill reuse** via subprocess invocation of `/sc:brainstorm` and `/sc:spec-panel`
- **Runner-authored truth**: Claude assists with content generation but never controls sequencing or status
- **Design for failure containment**: all exit paths emit populated contracts; resume boundaries are explicit

### Delivery Objective

Produce a working `cli_portify` command group that validates and inventories workflows quickly, generates roadmap/spec artifacts through controlled Claude subprocesses, supports user review gates and dry-run behavior, converges panel review within bounded iterations, and emits a complete machine-readable contract on every exit path.

### Complexity

0.85 (complex) — driven by multi-phase orchestration, subprocess management, convergence logic, and gate enforcement across 7 steps with 8 semantic check functions.

---

## Phased Implementation Plan

### Phase 0: Architecture Confirmation and Decision Record

**Objective**: Resolve blocking spec ambiguities and lock module layout before code changes. This lightweight phase (0.5-1 day, S) has asymmetric payoff: a small upfront investment prevents costly rework when late-phase decisions force model changes that ripple backward.

#### Work Items

1. **Resolve blocking ambiguities**
   - Timeout semantics for convergence iterations: per-iteration independent timeout vs total divided by `max_convergence`. Determines whether `PortifyConfig` needs one field or two.
   - Resume behavior for partially written `synthesize-spec`: re-run step vs skip. Determines resume metadata shape in `PortifyStepResult`.
   - Scoring precision vs downstream gate boundary handling (7.0 boundary with rounding).
   - Authoritative module/file layout: Section 4.1 (18 modules) vs Section 4.6 (13 files). DEV-001 confirms 18-module structure is authoritative.

2. **Freeze implementation architecture**
   - Confirm 18-module `cli_portify/` structure.
   - Define ownership boundaries: config/model layer, step implementations, process wrapper, monitor/logging, contract emission, CLI integration.

3. **Define artifact contract**
   - Standardize output artifact names and locations.
   - Standardize frontmatter parsing/validation behavior.
   - Standardize failure/default population rules for contracts.

4. **Define minimal signal vocabulary**
   - Initial constants: `step_start`, `step_complete`, `step_error`, `step_timeout`, `gate_pass`, `gate_fail`.
   - Extend during Phase 3 when subprocess behavior is understood.

#### Milestone M0: Architecture Baseline Approved

- Open questions triaged into: (1) must-resolve before implementation, (2) safe defaults acceptable, (3) defer-to-follow-up.
- Decision record produced with per-question blocking-phase annotations (`[Blocking Phase N]` or `[Advisory]`).

#### Deliverables

- Implementation decision record
- Final module map
- Step/artifact interface table
- Minimal signal vocabulary constants

---

### Phase 1: Deterministic Foundation and CLI Skeleton

**Objective**: Build the non-Claude substrate so orchestration rests on stable, well-typed primitives. Estimated effort: 1-2 days (S-M).

#### Work Items

1. **Configuration and domain model layer**
   - Implement `PortifyConfig` extending `PipelineConfig`: workflow path resolution (directory containing `SKILL.md`), CLI name derivation (strip `sc-`/`-protocol`, kebab/snake conversion), output directory writability check, name collision detection.
   - Implement `PortifyStepResult` extending `StepResult`: step metadata, artifact paths, gate tier metadata, timeout settings (per-iteration and total budget per Phase 0 decision), review flags, resume metadata (typed fields, not generic dict).

2. **CLI registration**
   - Add `cli_portify_group` and register with `main.py` via `app.add_command()`.
   - Define options: workflow path, output directory, `--dry-run`, `--skip-review`, `--start`, convergence/budget controls, timeout controls.

3. **Contract and status model**
   - Define success/partial/failed/dry_run contract schema.
   - Ensure all failure paths populate defaults (NFR-009).
   - Define resume command generation logic.

4. **Shared utility layer**
   - Frontmatter parsing helpers.
   - File existence/writability checks.
   - Section hashing utilities for additive-only verification (NFR-008).
   - Line counting and artifact rendering helpers.
   - Signal vocabulary constants (from Phase 0).

5. **Unit tests**
   - Config validation (<1s, all error code paths).
   - Contract emission for mocked success and failure flows.

#### Milestone M1: CLI and Model Foundation Operational

#### Exit Criteria

- CLI command parses correctly.
- Base config/result types compile and integrate with current architecture.
- Contract objects can be emitted for mocked success and failure flows.

---

### Phase 2: Fast Deterministic Pipeline Steps

**Objective**: Implement the two pure-programmatic steps for reliable early-phase execution and fast failure detection. Estimated effort: 1-1.5 days (S-M).

#### Work Items

1. **Implement `validate-config` (Step 1)**
   - Resolve workflow path to valid skill directory containing `SKILL.md`.
   - Derive CLI name: strip `sc-`, strip `-protocol`, normalize naming case.
   - Validate output directory writability.
   - Detect collisions with existing non-portified CLI modules.
   - Write `validate-config-result.json`.
   - EXEMPT gate: config validation completes <1s; correct error codes for 4 failure scenarios (SC-001).

2. **Implement `discover-components` (Step 2)**
   - Inventory: `SKILL.md`, `refs/`, `rules/`, `templates/`, `scripts/`, matching command files.
   - Accurate line counting per component.
   - Generate `component-inventory.md` with YAML frontmatter (`source_skill`, `component_count`).
   - EXEMPT gate: discovery completes <5s; inventory has correct frontmatter and line counts (SC-002).

3. **Deterministic gate checks**
   - Runtime limits as advisory/performance checks.
   - Structure validation for inventory output.

#### Milestone M2: Deterministic Entry Pipeline Complete

#### Exit Criteria

1. `validate-config` completes under target conditions with correct failure codes.
2. `discover-components` produces accurate inventory output.
3. Both steps run without Claude subprocesses.
4. Unit coverage exists for success and failure matrices.

---

### Phase 3: Claude Subprocess Orchestration Core

**Objective**: Introduce the executor-managed Claude integration safely, with subprocess isolation, path scoping, monitoring, and gate enforcement. This phase is a prerequisite gate before content steps — build the platform, stabilize it, then build on it. Estimated effort: 2-3 days (M-L).

#### Work Items

1. **Implement `PortifyProcess`**
   - Extend base `pipeline.ClaudeProcess`.
   - Pass `--add-dir` for both work directory and workflow path.
   - Support prompt construction with `@path` references.
   - Capture exit code, stdout/stderr, timeout state, and diagnostics.

2. **Implement prompt builder framework**
   - One builder per Claude-assisted step.
   - Inputs reference prior artifacts via `@path`.
   - Include step-specific output contracts and frontmatter expectations.
   - Include retry augmentation for targeted failures (especially placeholder residue).

3. **Implement monitoring and diagnostics**
   - NDJSON/JSONL event logging using signal vocabulary from Phase 0/1.
   - Signal extraction from subprocess output.
   - Timing capture for phases and steps.
   - Failure classification: timeout, missing artifact, malformed frontmatter, gate failure, user rejection, budget exhaustion, partial artifact.
   - Markdown report generation.

4. **Build Claude subprocess mock harness**
   - Returns known-good outputs for each step type.
   - Enables unit testing of all Claude-assisted steps without actual Claude invocations.
   - Dramatically reduces development iteration time for Phases 4-5.

5. **Implement gate engine bindings**
   - All gate functions return `tuple[bool, str]` (NFR-004).
   - Structural and semantic validators for STRICT/STANDARD outputs.
   - Integration with `pipeline.gates.gate_passed()` validation engine.
   - EXEMPT / STANDARD / STRICT tier enforcement.

#### Milestone M3: Controlled Subprocess Platform Ready

This milestone explicitly gates Phase 4. Content steps must not begin until the subprocess platform is stable.

#### Exit Criteria

- Claude-assisted steps can be executed in harness with mocked or real subprocess behavior.
- Monitoring emits consistent machine-readable records.
- Gate engine integration is stable and deterministic.
- Mock harness produces realistic outputs for all step types.

---

### Phase 4: Core Content Generation Steps

**Objective**: Deliver the core design intelligence of the pipeline: workflow analysis, pipeline design, and spec synthesis. Estimated effort: 2-3 days (M-L).

#### Work Items

1. **Implement `analyze-workflow` (Step 3)**
   - Read discovered components via `@path` references.
   - Produce `portify-analysis.md` (<400 lines).
   - Enforce required sections: behavioral flow, step boundaries, programmatic spectrum classification, dependency/parallel groups, gate requirements, data flow diagram with arrow notation.
   - STRICT gate: 5 required sections, data flow diagram, 5 YAML frontmatter fields (SC-003).

2. **Implement `design-pipeline` (Step 4)**
   - Produce `portify-spec.md`.
   - Define: Step graph, domain models, prompt builder specs, gate criteria with semantic checks, pure-programmatic steps as runnable Python code, executor loop, Click CLI integration.
   - Implement `--dry-run` halt point: emits `dry_run` contract, phases 3-4 marked `skipped`.
   - Implement user review gate: stderr prompt, `y`/`n`, `USER_REJECTED` status.
   - STRICT gate: `step_mapping_count`, `model_count`, `gate_definition_count` frontmatter (SC-004).

3. **Implement `synthesize-spec` (Step 5)**
   - Verify `release-spec-template.md` exists (fail-fast if missing — gate at startup per Recommendation #5).
   - Populate all template sections from Phase 1-2 outputs (referenced by `@path`).
   - Include step consolidation mapping table (12 logical to 7 actual).
   - SC-003 self-validation: scan for remaining `{{SC_PLACEHOLDER:*}}` sentinels.
   - On gate failure: retry prompt includes specific remaining placeholder names.
   - Resume policy: prefer re-running `synthesize-spec` over trusting partially gated output (per Phase 0 decision).
   - STRICT gate: zero remaining sentinels; 7 FRs with consolidation mapping (SC-005).

#### Milestone M4: Core Spec Generation Complete

#### Exit Criteria

1. All three artifacts are generated and gated successfully.
2. `--dry-run` halts after `design-pipeline` with correct contract semantics.
3. Retry logic for unresolved placeholders is working and bounded.
4. Template existence validated at startup.

---

### Phase 5: Quality Amplification Steps

**Objective**: Add controlled critique loops without surrendering orchestration authority to Claude. The convergence engine is extracted as a standalone, testable component. Estimated effort: 2-3 days (M-L).

#### Work Items

1. **Implement `brainstorm-gaps` (Step 6)**
   - Pre-flight check: verify `/sc:brainstorm` availability.
   - Fallback: inline multi-persona prompt with warning if skill unavailable.
   - Invoke `/sc:brainstorm` with `--strategy systematic --depth deep --no-codebase`.
   - Post-process findings into structured objects (`gap_id`, `description`, `severity`, `affected_section`, `persona`).
   - Incorporate actionable findings into spec body sections marked `[INCORPORATED]`.
   - Route unresolvable items to Section 11 marked `[OPEN]`.
   - Append Section 12 with summary.
   - STANDARD gate: Section 12 present with structural content validation per F-007: must contain either a findings table (with Gap ID column) or the literal zero-gap summary text — heading-only content MUST fail the gate; zero-gap is a valid outcome (SC-006).

2. **Implement convergence engine (standalone component)**
   - Extract convergence logic (predicate checking, budget guards, escalation) into a testable engine independent of Claude subprocess management.
   - TurnLedger pre-launch budget guard before each iteration.
   - Convergence predicate: zero unaddressed CRITICALs -> CONVERGED.
   - Max iterations: `max_convergence` (default 3).
   - Terminal states: CONVERGED (success) or ESCALATED (partial, user escalation).
   - Unit-testable with mock iteration results.

3. **Implement `panel-review` (Step 7)**
   - Pre-flight check: verify `/sc:spec-panel` availability; inline fallback if unavailable.
   - Each iteration: single Claude subprocess running both focus pass (discussion mode) AND critique pass (critique mode).
   - Per-iteration independent timeout (default 300s, per Phase 0 decision).
   - Quality scores: clarity, completeness, testability, consistency; overall = mean of 4 dimensions.
   - Downstream readiness gate: `overall >= 7.0` (boundary: 7.0 true, 6.9 false).
   - Produce `panel-report.md` with machine-readable convergence block.
   - Section hashing to enforce additive-only modifications (NFR-008).
   - User review gate at end.
   - STRICT gate: convergence terminal state reached, quality scores populated, downstream readiness evaluated (SC-007).

#### Milestone M5: Review and Convergence Pipeline Operational

#### Exit Criteria

1. Brainstorm step passes with findings or zero-gap summary.
2. Panel review stops correctly on convergence or escalation.
3. Quality scoring and downstream readiness are computed deterministically.
4. Additive-only protection is enforced.
5. Convergence engine passes unit tests independently of subprocess management.

---

### Phase 6: UX, Resume, and Operational Hardening

**Objective**: Make the system usable in real workflows, not just correct in narrow successful paths. Estimated effort: 1.5-2 days (M).

#### Work Items

1. **TUI / live status experience**
   - Rich TUI live dashboard rendering with step progress, gate state, timing, current iteration, review pause prompts, warnings/advisories.

2. **User review gates**
   - Pause TUI when review required.
   - Prompt on stderr.
   - Continue on `y`, halt with `USER_REJECTED` on `n`.
   - `--skip-review` bypasses user prompts.

3. **Resume semantics**
   - Define resumable steps with explicit resumability matrix.
   - Prior-context injection for Phase 4 resume (preserve `focus-findings.md`).
   - Generate resume commands for resumable failures (`--start` step, suggested budget).
   - Define resume entry points precisely.

4. **Comprehensive failure-path handling**
   - Missing template: fail-fast with clear error and remediation path.
   - Missing skills: graceful fallback with warning.
   - Malformed artifact: diagnostic classification and targeted retry.
   - Timeout: per-iteration and total budget handling.
   - Partial artifact: re-run policy (prefer re-run over trust).
   - Non-writable output: early detection in validate-config.
   - Exhausted budget: ESCALATED terminal state with resume guidance.

#### Milestone M6: Operational Resilience Complete

#### Exit Criteria

- Resume behavior works for intended boundaries.
- All exit paths emit complete contracts with populated defaults.
- User review interaction is reliable and testable.
- All 7 failure types have explicit handling paths.

---

### Phase 7: Validation, Compliance, and Release Readiness

**Objective**: Prove the implementation meets both functional and non-functional requirements before merge. Estimated effort: 1.5-2.5 days (M-L).

#### Work Items

1. **Unit test layer**
   - Validation rules, naming derivation, gate functions, score calculations (including boundary: 7.0 true / 6.9 false), contract defaults, hashing/additive protections, resume command generation.

2. **Integration test layer**
   - Full happy path, `--dry-run`, review rejection, brainstorm fallback, panel fallback/marker parsing, convergence boundary cases, template missing case, timeout behavior.

3. **Compliance verification**
   - Zero `async def` / `await` in `cli_portify/` (SC-012): `grep -r "async def\|await" src/superclaude/cli/cli_portify/`
   - Zero diffs in `pipeline/` and `sprint/` (SC-013): `git diff --name-only`
   - Gate signatures compliant: all return `tuple[bool, str]`
   - Runner-authored truth enforced: no Claude-directed sequencing

4. **SC validation matrix cross-reference**

| SC | Criterion | Test Layer | Validation Method |
|----|-----------|------------|-------------------|
| SC-001 | Config validation <1s, 4 error paths | Unit | `pytest` with timing assertions |
| SC-002 | Discovery <5s, accurate inventory | Unit | `pytest` with fixture skill directory |
| SC-003 | Analysis STRICT gate passes | Integration | Gate function against known-good analysis |
| SC-004 | Design STRICT gate + dry-run halt | Integration | `--dry-run` emits correct contract |
| SC-005 | Zero `{{SC_PLACEHOLDER:*}}` remaining | Integration | Regex scan of synthesized spec |
| SC-006 | Section 12 present with structure | Integration | Gate function validates content |
| SC-007 | Convergence terminal state + quality scores | Integration | Mock convergence loop with known outputs |
| SC-008 | Overall = mean(4 dimensions) +/-0.01 | Unit | Arithmetic test with boundary values |
| SC-009 | Downstream: 7.0 true, 6.9 false | Unit | Boundary test |
| SC-010 | Contract on all exit paths | Unit | Test each path (success, partial, failed, dry_run) |
| SC-011 | `--dry-run` halts after Step 4 | Integration | Verify phases 3-4 marked `skipped` |
| SC-012 | Zero `async def`/`await` in `cli_portify/` | Static | grep scan |
| SC-013 | Zero changes to `pipeline/`/`sprint/` | Static | `git diff --name-only` |
| SC-014 | Resume commands for resumable failures | Integration | Trigger failure in Step 6/7, verify resume command |
| SC-015 | `has_section_12` structural content validation [F-007] | Unit | Gate rejects heading-only Section 12; accepts findings table with Gap ID column; accepts zero-gap summary text |
| SC-016 | Per-iteration independent timeout [F-004] | Unit | Each convergence iteration gets independent timeout (default 300s), not total divided by `max_convergence` |

5. **Evidence package for release readiness**
   - Test results for all functional criteria.
   - Example output artifacts from happy path.
   - Failure-path contract samples.
   - `git diff` proof for no base-module modifications.
   - Search proof for no async usage.
   - Boundary test evidence (7.0 gate, convergence termination, placeholder elimination, dry-run stop).

6. **Developer readiness**
   - Command help text, example invocation, artifact expectations, troubleshooting notes.

#### Milestone M7: Release-Ready Implementation

#### Exit Criteria

- All SC criteria satisfied or explicitly waived with evidence.
- No architectural constraint violations remain.
- Evidence package complete.
- Merge candidate is ready.

---

## Risk Assessment

### High-Priority Risks

| ID | Risk | Impact | Mitigation |
|----|------|--------|------------|
| R-1 | Claude output truncation in Steps 5-7 due to large context | Incomplete specs, gate failures | Use `@path` references exclusively; set generous `max_turns`; monitor output length in TUI; treat prompt budget and artifact size as first-class architecture constraints |
| R-2 | Incorrect convergence prompt design in `panel-review` | False non-convergence, wasted iterations, unusable quality scoring | Lock iteration contract: each iteration includes both focus and critique; integration tests validate prompt shape; model convergence loop as deterministic state machine with explicit entry/exit criteria |
| R-8 | Sequential execution produces long wall-clock time | User frustration, timeout pressure | 12-to-7 step consolidation already applied; keep pure-programmatic steps fast; add phase timing telemetry; do not introduce async complexity — optimize by reducing work |

### Medium-Priority Risks

| ID | Risk | Impact | Mitigation |
|----|------|--------|------------|
| R-3 | Budget exhaustion before convergence | Partial review, ESCALATED state | TurnLedger pre-flight checks; estimated cost per iteration; ESCALATED is valid terminal state; clear resume guidance |
| R-4 | Skills produce non-machine-readable output | Parse failures in executor | Pre-flight skill checks; inline fallback prompts; executor-side parsing; structural fallback validation where markers are missing |
| R-5 | Subprocess `@path` scope failures | Step failures for out-of-dir artifacts | Always pass `--add-dir` for work dir and workflow path; integration test with out-of-dir artifacts; classify scope failures distinctly in diagnostics |
| R-6 | User review gates have no programmatic interaction | CI/CD incompatibility | `--skip-review` flag; stderr prompt for interactive use |
| R-7 | Partial `synthesize-spec` output on resume | Gate failure on resume | Prefer re-running `synthesize-spec` over trusting partially gated output; define precise resume entry points |
| R-10 | Missing template at runtime | Spec synthesis impossible | Validate template presence at startup (fail-fast); emit deterministic failure contract; surface remediation path immediately |

### Low-Priority Risks

| ID | Risk | Impact | Mitigation |
|----|------|--------|------------|
| R-9 | Self-portification circularity | Unexpected behavior | Source skill files read-only during portification; generated code in separate output directory; test against self-referential scenarios only after core stability is proven |

---

## Resource Requirements

### Pre-Implementation Validation Checklist

1. Verify `pipeline/` and `sprint/` base modules expose required types (import test for `PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `GateMode`, `ClaudeProcess`, `TurnLedger`, `GateDisplayState`)
2. Verify `release-spec-template.md` exists and is >=8KB
3. Verify `claude` binary available and functional
4. Verify `/sc:brainstorm` and `/sc:spec-panel` skills are installed and invocable
5. Verify Click, Rich, PyYAML in `pyproject.toml` dependencies

### Technical Dependencies

| Priority | Dependency | Used By | Risk if Missing |
|----------|-----------|---------|-----------------|
| Critical | `pipeline.models` (PipelineConfig, Step, StepResult, GateCriteria, GateMode) | All phases | Cannot build; blocks everything |
| Critical | `pipeline.process` (ClaudeProcess with `extra_args`) | Phase 3-5 | Cannot launch Claude subprocesses |
| Critical | `pipeline.gates` (`gate_passed()`) | All gates | Cannot validate steps |
| Critical | `sprint.models` (TurnLedger, GateDisplayState) | Phase 5 | Cannot manage convergence budget |
| Critical | `claude` binary in PATH | Phase 3-5 | All Claude-assisted steps fail |
| Critical | `release-spec-template.md` | Phase 4 | Spec synthesis impossible |
| High | `/sc:brainstorm` skill | Phase 5 (Step 6) | Falls back to inline prompt (degraded) |
| High | `/sc:spec-panel` skill | Phase 5 (Step 7) | Falls back to inline prompt (degraded) |
| Medium | Click >=8.0.0, Rich >=13.0.0, PyYAML | All phases | Install via `uv pip install` |

### Team/Role Requirements

1. **Architect / lead implementer**: Owns module boundaries, flow control, and invariant protection.
2. **Backend/Python implementer**: Builds CLI, models, step runners, contracts, diagnostics.
3. **QA engineer**: Owns boundary tests, failure-path coverage, resume behavior validation.
4. **Optional UX/TUI contributor**: Improves live rendering and review pause experience.

### Artifact Outputs

1. `validate-config-result.json`
2. `component-inventory.md`
3. `portify-analysis.md`
4. `portify-spec.md`
5. Synthesized release spec
6. Brainstorm findings / augmented spec sections
7. `panel-report.md`
8. Final return contract
9. Step/phase timing and diagnostic logs (NDJSON)

---

## Success Criteria and Validation Approach

### Validation Strategy

Testing is organized in four layers for execution, with the SC validation matrix providing traceability across all layers.

#### Layer 1: Unit Tests
Focus on deterministic logic: path validation, naming derivation, frontmatter parsing, score math (including 7.0/6.9 boundary), gate result helpers, hashing, resume command generation, contract defaults, convergence engine (standalone).

#### Layer 2: Integration Tests
Focus on orchestration: subprocess execution behavior, artifact chaining, gate enforcement, fallback skill behavior, `--dry-run`, review rejection, convergence boundaries, timeout behavior, template missing case.

#### Layer 3: Compliance Checks
Static analysis: async prohibition (`grep`), base-module immutability (`git diff`), gate function signatures, runner-authored truth enforcement.

#### Layer 4: Architectural Validation
Verify: no Claude-directed sequencing, all decisions derive from observed artifacts, resume boundaries are deterministic, additive-only review guarantees hold.

### Manual Validation

- End-to-end run against a real skill (e.g., `sc-brainstorm-protocol`)
- `--dry-run` produces coherent analysis + design without proceeding to synthesis
- User review gates pause correctly in interactive mode
- `--skip-review` bypasses user prompts
- TUI dashboard renders step progress legibly

---

## Timeline Estimates

| Phase | Steps | Type | Effort (days) | Size | Dependencies |
|-------|-------|------|---------------|------|--------------|
| Phase 0: Architecture Confirmation | — | Decision | 0.5-1 | S | None |
| Phase 1: Foundation and CLI Skeleton | — | Pure programmatic | 1-2 | S-M | Phase 0 |
| Phase 2: Deterministic Steps | 1-2 | Pure programmatic | 1-1.5 | S-M | Phase 1 |
| Phase 3: Subprocess Platform | — | Infrastructure | 2-3 | M-L | Phase 2 |
| Phase 4: Content Generation | 3-5 | Claude-assisted | 2-3 | M-L | Phase 3 (M3 gate) |
| Phase 5: Quality Amplification | 6-7 | Claude-assisted | 2-3 | M-L | Phase 4 |
| Phase 6: UX and Hardening | — | Operational | 1.5-2 | M | Phase 5 |
| Phase 7: Validation and Release | — | Testing | 1.5-2.5 | M-L | Phase 6 |
| **Total** | | | **12-18 days** | | |

### Critical Path

```
Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5 -> Phase 6 -> Phase 7
```

All phases are strictly sequential. Phase 3 (subprocess platform) is a prerequisite gate (M3) before any content generation steps begin. Infrastructure parallelization is a valid optimization for future releases once the extension surface is proven stable.

### Recommended Milestone Cadence

| Week | Phases | Checkpoint |
|------|--------|------------|
| Week 1 | Phase 0-3 | Deterministic foundation and subprocess platform established |
| Week 2 | Phase 4-6 | Core generation, review loop, and hardening delivered |
| Week 3 | Phase 7 + buffer | Validation complete, remediation of defects, merge candidate ready |

---

## Architectural Recommendations

1. **Resolve spec ambiguities in Phase 0 before coding the convergence loop.** Timeout semantics, resume semantics, and scoring boundary/rounding behavior must have concrete answers in the decision record.

2. **Treat contracts, gates, and artifacts as the real system boundary** — not prompts, not prose outputs. All status determination derives from observed artifacts and gate results.

3. **Bias toward explicit state machines**, especially for review gates, convergence, resume, and failure classification. The convergence engine in particular should be a standalone, testable component.

4. **Build a Claude subprocess mock harness early** (Phase 3). Phases 4-5 all depend on Claude subprocesses. A mock harness that returns known-good outputs enables unit testing without actual Claude invocations and dramatically reduces development iteration time.

5. **Gate the `release-spec-template.md` dependency at startup.** If the template does not exist, fail fast with a clear error message rather than proceeding through Phases 1-2 only to fail at Phase 4.

6. **Validate external prerequisites early**: `claude` binary, template existence, skill availability. Prefer graceful degradation for optional skill behavior but do not degrade core invariants — if base architecture assumptions fail, stop explicitly.

7. **Keep the implementation additive and isolated** — no leakage into `pipeline/` or `sprint/`. Validate continuously with `git diff`.

8. **Consider infrastructure parallelization in v2.25+.** Once the `PortifyProcess` extension surface is proven stable, monitor/diagnostics/TUI work can safely run in parallel with content steps. For this first implementation, sequential ordering eliminates integration risk.
