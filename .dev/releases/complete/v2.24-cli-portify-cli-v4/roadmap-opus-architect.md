

---
spec_source: "portify-release-spec.md"
complexity_score: 0.85
primary_persona: architect
---

# CLI-Portify v2.24 — Project Roadmap

## 1. Executive Summary

This roadmap covers the implementation of `cli_portify`, a 7-step pipeline that converts inference-based SuperClaude workflows (skills/commands) into programmatic CLI pipelines. The system extends the existing `pipeline/` and `sprint/` architecture with 18 new modules under `src/superclaude/cli/cli_portify/`.

**Key architectural characteristics:**
- Synchronous-only execution model (no async/await)
- 7 consolidated steps across 4 phases (2 pure-programmatic, 5 Claude-assisted)
- Convergence loop in panel-review with budget guards and escalation
- Zero modifications to existing pipeline/sprint base modules
- Skill reuse via subprocess invocation of `/sc:brainstorm` and `/sc:spec-panel`

**Complexity**: 0.85 (complex) — driven by multi-phase orchestration, subprocess management, convergence logic, and gate enforcement across 7 steps with 8 semantic check functions.

---

## 2. Phased Implementation Plan

### Phase 1: Foundation (Steps 1–2) — Pure Programmatic

**Objective**: Establish config validation and component discovery with zero Claude dependency.

#### Milestone 1.1: Package Skeleton & Base Types
- [ ] Create `src/superclaude/cli/cli_portify/` directory with `__init__.py`
- [ ] Implement `config.py`: `PortifyConfig` extending `PipelineConfig`
  - Workflow path resolution (directory containing `SKILL.md`)
  - CLI name derivation (strip `sc-`/`-protocol`, kebab/snake conversion)
  - Output directory writability check
  - Name collision detection against existing non-portified CLI modules
- [ ] Implement `models.py`: `PortifyStepResult` extending `StepResult`
- [ ] Implement `contract.py`: Return contract emission for all exit paths
- [ ] Register Click command group in `main.py` via `app.add_command()`
- [ ] Write unit tests for config validation (<1s, all error code paths)

**Gate**: Config validation completes <1s; correct error codes for 4 failure scenarios (SC-001).

#### Milestone 1.2: Component Discovery
- [ ] Implement `steps/discover_components.py` using `Path.rglob()`
  - Inventory: SKILL.md, refs/, rules/, templates/, scripts/, command files
  - Line counting per component
  - YAML frontmatter emission (`source_skill`, `component_count`)
- [ ] Produce `component-inventory.md` with structured markdown table
- [ ] Write unit tests for discovery (<5s completion, accurate counts)

**Gate**: Discovery completes <5s; `component-inventory.md` has correct frontmatter and line counts (SC-002).

**Deliverables**: Working CLI entry point, config validation, component inventory generation.

---

### Phase 2: Analysis & Design (Steps 3–4) — Claude-Assisted

**Objective**: Extract workflow behavior and produce a code-ready pipeline specification.

#### Milestone 2.1: Workflow Analysis (Step 3)
- [ ] Implement `steps/analyze_workflow.py` with Claude subprocess
- [ ] Build prompt that reads all discovered components via `@path` references
- [ ] Implement `PortifyProcess` extending `pipeline.ClaudeProcess` with `--add-dir` support
- [ ] Extract: behavioral flow, step boundaries, programmatic spectrum classification, dependencies, parallel groups, gate requirements, data flow diagram
- [ ] Implement STRICT gate: 5 required sections, data flow diagram with arrow notation, 5 YAML frontmatter fields
- [ ] Output: `portify-analysis.md` (<400 lines)

**Gate**: STRICT — all 5 sections present, data flow diagram, frontmatter complete (SC-003).

#### Milestone 2.2: Pipeline Design (Step 4)
- [ ] Implement `steps/design_pipeline.py` with Claude subprocess
- [ ] Convert analysis into concrete Step graph, domain models, prompt builder specs
- [ ] Define gate criteria with semantic checks
- [ ] Implement pure-programmatic steps as runnable Python code
- [ ] Design executor loop and Click CLI integration
- [ ] Implement STRICT gate: `step_mapping_count`, `model_count`, `gate_definition_count` frontmatter
- [ ] Implement `--dry-run` halt point (emits `dry_run` contract, phases 3–4 marked `skipped`)
- [ ] Implement user review gate (stderr prompt, `y`/`n`, `USER_REJECTED` status)

**Gate**: STRICT — step mappings, 3 frontmatter fields populated. User review gate (SC-004).

**Deliverables**: Complete analysis document, code-ready pipeline specification, dry-run support.

---

### Phase 3: Spec Synthesis (Step 5) — Claude-Assisted

**Objective**: Generate the full release specification from Phase 1–2 outputs.

#### Milestone 3.1: Template Instantiation
- [ ] Verify `src/superclaude/examples/release-spec-template.md` exists (fail-fast if missing)
- [ ] Implement `steps/synthesize_spec.py` with Claude subprocess
- [ ] Populate all template sections from Phase 1–2 outputs (referenced by `@path`)
- [ ] Include step consolidation mapping table (12 logical → 7 actual)
- [ ] Implement SC-003 self-validation: scan for remaining `{{SC_PLACEHOLDER:*}}` sentinels
- [ ] On gate failure: retry prompt includes specific remaining placeholder names
- [ ] STRICT gate

**Gate**: Zero remaining `{{SC_PLACEHOLDER:*}}` sentinels; 7 FRs with consolidation mapping (SC-005).

**Deliverable**: Fully populated release spec with zero placeholders.

---

### Phase 4: Review & Convergence (Steps 6–7) — Claude-Assisted

**Objective**: Multi-persona gap analysis and expert panel review with convergence.

#### Milestone 4.1: Brainstorm Gap Analysis (Step 6)
- [ ] Implement `steps/brainstorm_gaps.py`
- [ ] Pre-flight check: verify `/sc:brainstorm` availability
- [ ] Fallback: inline multi-persona prompt with warning if skill unavailable
- [ ] Invoke `/sc:brainstorm` with `--strategy systematic --depth deep --no-codebase`
- [ ] Post-process findings into structured objects (`gap_id`, `description`, `severity`, `affected_section`, `persona`)
- [ ] Incorporate actionable findings into spec body sections marked `[INCORPORATED]`
- [ ] Route unresolvable items to Section 11 marked `[OPEN]`
- [ ] Append Section 12 with summary
- [ ] STANDARD gate: findings table OR zero-gap summary text (zero-gap is valid)

**Gate**: STANDARD — Section 12 present with structured content (SC-006).

#### Milestone 4.2: Panel Review with Convergence (Step 7)
- [ ] Implement `steps/panel_review.py` with executor-managed convergence loop
- [ ] Pre-flight check: verify `/sc:spec-panel` availability; inline fallback if unavailable
- [ ] Each iteration: single Claude subprocess running both focus pass (discussion mode) AND critique pass (critique mode)
- [ ] TurnLedger guard before each iteration launch (budget check)
- [ ] Per-iteration independent timeout (default 300s)
- [ ] Convergence predicate: zero unaddressed CRITICALs → CONVERGED
- [ ] Max iterations: `max_convergence` (default 3)
- [ ] Terminal states: CONVERGED (success) or ESCALATED (partial, user escalation)
- [ ] Quality scores: clarity, completeness, testability, consistency; overall = mean of 4
- [ ] Downstream readiness gate: `overall >= 7.0` (boundary: 7.0 true, 6.9 false)
- [ ] Produce `panel-report.md` with machine-readable convergence block
- [ ] Section hashing to enforce additive-only modifications (NFR-008)
- [ ] User review gate at end
- [ ] STRICT gate

**Gate**: STRICT — convergence terminal state reached, quality scores populated, downstream readiness evaluated (SC-007).

**Deliverables**: Gap-analyzed spec, converged panel report with quality scores.

---

### Phase 5: Infrastructure & Cross-Cutting

**Objective**: Monitoring, logging, resume, and contract emission.

#### Milestone 5.1: Monitor & TUI
- [ ] Implement `monitor.py`: JSONL logging, markdown report generation, signal extraction from Claude subprocess output
- [ ] Rich TUI live dashboard rendering with step progress
- [ ] Define NDJSON signal vocabulary (resolve Open Question GAP-008)

#### Milestone 5.2: Resume & Checkpointing
- [ ] Implement per-step resumability classification
- [ ] Prior-context injection for Phase 4 resume (preserve `focus-findings.md`)
- [ ] Generate resume commands for resumable failures (`--start` step, suggested budget)
- [ ] Define resume entry points precisely (resolve Open Question GAP-005)

#### Milestone 5.3: Diagnostics & Failure Handling
- [ ] Implement `diagnostics.py`: failure classification, diagnostic collection
- [ ] Contract emission on all exit paths: success, partial, failed, dry_run
- [ ] All contract fields populated with defaults on failure paths (NFR-009)

#### Milestone 5.4: Gate Infrastructure
- [ ] Implement 8 semantic check functions
- [ ] All gate functions return `tuple[bool, str]` (NFR-004)
- [ ] Integrate with `pipeline.gates.gate_passed()` validation engine
- [ ] EXEMPT / STANDARD / STRICT tier enforcement

**Deliverables**: Full monitoring stack, resume support, contract emission, gate infrastructure.

---

## 3. Risk Assessment & Mitigation

### HIGH Risks

| ID | Risk | Impact | Mitigation | Owner |
|----|------|--------|------------|-------|
| R-1 | Claude output truncation in Steps 5–7 due to large context | Incomplete specs, gate failures | Use `@path` references exclusively; set generous `max_turns`; monitor output length in TUI | Phase 2–4 |
| R-2 | Panel review prompt mode mapping incorrect (GAP-006) | Convergence never reached; wasted budget | Acceptance criterion explicit in FR-007: both focus AND critique in single subprocess; integration test validates | Phase 4 |
| R-8 | Sequential execution → long wall-clock time | User frustration; timeout pressure | 12→7 step consolidation already applied; timing is advisory not blocking; consider parallel Phase 1 milestones | All phases |

### MEDIUM Risks

| ID | Risk | Impact | Mitigation |
|----|------|--------|------------|
| R-3 | Convergence loop exhausts budget before 3 iterations | Partial review, ESCALATED state | TurnLedger pre-launch guards; budget estimation per iteration; ESCALATED is valid terminal state |
| R-4 | Skills don't produce machine-readable convergence markers | Parse failures in executor | Post-processing with fallback to structural checks; regex patterns for known output formats |
| R-5 | Subprocess can't read `@path` outside working directory | Step failures | `PortifyProcess` passes `--add-dir` for work directory and workflow path |
| R-6 | User review gates have no programmatic interaction | CI/CD incompatibility | `--skip-review` flag; stderr prompt for interactive use |
| R-7 | Partial synthesize-spec output on resume | Gate failure on resume | Define precise resume entry points; re-run `synthesize-spec` on resume rather than skip |

### LOW Risks

| ID | Risk | Impact | Mitigation |
|----|------|--------|------------|
| R-9 | Self-portification circularity | Unexpected behavior | Source skill files read-only during portification; generated code in separate output directory |

---

## 4. Resource Requirements & Dependencies

### External Dependencies (Must Exist Before Implementation)

| Priority | Dependency | Used By | Risk if Missing |
|----------|-----------|---------|-----------------|
| **Critical** | `pipeline.models` (PipelineConfig, Step, StepResult, GateCriteria, GateMode) | All phases | Cannot build; blocks everything |
| **Critical** | `pipeline.process` (ClaudeProcess with `extra_args`) | Phase 2–4 | Cannot launch Claude subprocesses |
| **Critical** | `pipeline.gates` (`gate_passed()`) | All gates | Cannot validate steps |
| **Critical** | `sprint.models` (TurnLedger, GateDisplayState) | Phase 4 | Cannot manage convergence budget |
| **Critical** | `claude` binary in PATH | Phase 2–4 | All Claude-assisted steps fail |
| **Critical** | `release-spec-template.md` | Phase 3 | Spec synthesis impossible |
| **High** | `/sc:brainstorm` skill | Phase 4 (Step 6) | Falls back to inline prompt (degraded) |
| **High** | `/sc:spec-panel` skill | Phase 4 (Step 7) | Falls back to inline prompt (degraded) |
| **Medium** | Click ≥8.0.0, Rich ≥13.0.0, PyYAML | All phases | Install via `uv pip install` |

### Pre-Implementation Validation Checklist

1. Verify `pipeline/` and `sprint/` base modules expose required types (import test)
2. Verify `release-spec-template.md` exists and is ≥8KB
3. Verify `claude` binary available and functional
4. Verify `/sc:brainstorm` and `/sc:spec-panel` skills are installed and invocable
5. Verify Click, Rich, PyYAML in `pyproject.toml` dependencies

---

## 5. Success Criteria & Validation Approach

### Automated Validation Matrix

| SC | Criterion | Test Type | Validation Method |
|----|-----------|-----------|-------------------|
| SC-001 | Config validation <1s, 4 error paths | Unit | `pytest` with timing assertions |
| SC-002 | Discovery <5s, accurate inventory | Unit | `pytest` with fixture skill directory |
| SC-003 | Analysis STRICT gate passes | Integration | Gate function against known-good analysis |
| SC-004 | Design STRICT gate + dry-run halt | Integration | `--dry-run` emits correct contract |
| SC-005 | Zero `{{SC_PLACEHOLDER:*}}` remaining | Integration | Regex scan of synthesized spec |
| SC-006 | Section 12 present with structure | Integration | Gate function validates content |
| SC-007 | Convergence terminal state + quality scores | Integration | Mock convergence loop with known outputs |
| SC-008 | Overall = mean(4 dimensions) ±0.01 | Unit | Arithmetic test with boundary values |
| SC-009 | Downstream: 7.0→true, 6.9→false | Unit | Boundary test |
| SC-010 | Contract on all exit paths | Unit | Test each exit path (success, partial, failed, dry_run) |
| SC-011 | `--dry-run` halts after Step 4 | Integration | Verify phases 3–4 marked `skipped` |
| SC-012 | Zero `async def`/`await` in `cli_portify/` | Static | `grep -r "async def\|await" src/superclaude/cli/cli_portify/` |
| SC-013 | Zero changes to `pipeline/`/`sprint/` | Static | `git diff --name-only` |
| SC-014 | Resume commands for resumable failures | Integration | Trigger failure in Step 6/7, verify resume command |

### Manual Validation

- [ ] End-to-end run against a real skill (e.g., `sc-brainstorm-protocol`)
- [ ] `--dry-run` produces coherent analysis + design without proceeding to synthesis
- [ ] User review gates pause correctly in interactive mode
- [ ] `--skip-review` bypasses user prompts
- [ ] TUI dashboard renders step progress legibly

---

## 6. Timeline Estimates per Phase

| Phase | Steps | Type | Estimated Effort | Dependencies |
|-------|-------|------|-----------------|--------------|
| **Phase 1: Foundation** | 1–2 | Pure programmatic | Small — config parsing, file globbing, Click registration | Base module imports only |
| **Phase 2: Analysis & Design** | 3–4 | Claude-assisted | Medium — subprocess management, prompt engineering, STRICT gates | Phase 1 complete |
| **Phase 3: Spec Synthesis** | 5 | Claude-assisted | Medium — template instantiation, placeholder validation, retry logic | Phase 2 complete |
| **Phase 4: Review & Convergence** | 6–7 | Claude-assisted | Large — convergence loop, budget guards, skill integration, section hashing | Phase 3 complete |
| **Phase 5: Infrastructure** | Cross-cutting | Pure programmatic | Medium — monitor, resume, diagnostics, contract emission | Can start in parallel with Phase 2 |

### Critical Path

```
Phase 1 (Foundation) → Phase 2 (Analysis & Design) → Phase 3 (Synthesis) → Phase 4 (Review & Convergence)
                    ↗ Phase 5 (Infrastructure) — parallel from Phase 2 onward
```

Phase 5 (infrastructure) is the only parallelizable track. The main pipeline phases are strictly sequential due to data dependencies between steps.

---

## 7. Open Questions Requiring Resolution Before Implementation

These must be resolved to avoid rework. Ordered by implementation-blocking potential:

1. **[Blocking Phase 5]** GAP-008: Define NDJSON signal vocabulary for `monitor.py` — what signals does the monitor extract from Claude output?
2. **[Blocking Phase 4]** F-004: Per-iteration timeout — independent 300s each, or total divided by `max_convergence`? Spec text and pseudocode conflict.
3. **[Blocking Phase 4]** F-006: Resume context injection — how is `focus-findings.md` produced and injected into first iteration prompt on resume?
4. **[Blocking Phase 3]** Template availability: verify `release-spec-template.md` exists; define runtime behavior if missing.
5. **[Blocking Phase 4]** GAP-005: Resume from partial `synthesize-spec` — re-run step or skip?
6. **[Advisory]** GAP-004: Score rounding — display 1 or 2 decimal places; rounding impact on 7.0 boundary.
7. **[Advisory]** GAP-007: Inline vs module-level imports in `contract.py` — minor, resolve during implementation.
8. **[Advisory]** Implementation order discrepancy: Section 4.1 (18 modules) vs Section 4.6 (13 files). DEV-001 confirms 18-module structure is authoritative.
9. **[Advisory]** Subprocess MCP availability: do skills invoked in Claude subprocesses have MCP access?
10. **[Advisory]** GAP-009: File size cap for line counting in discovery — 1MB cap mentioned but not in reference implementation.

---

## 8. Architectural Recommendations

1. **Implement Phase 5 infrastructure in parallel with Phase 2**. Monitor, logging, and contract emission are not gated on Claude-assisted outputs and can be developed and unit-tested independently.

2. **Resolve all "Blocking" open questions before starting the blocked phase**. Do not start Phase 4 without resolving F-004 (timeout semantics) and F-006 (resume context injection).

3. **Build a test harness for Claude subprocess mocking early**. Phases 2–4 all depend on Claude subprocesses. A mock harness that returns known-good outputs enables unit testing without actual Claude invocations and dramatically reduces development iteration time.

4. **Treat the 18-module structure (DEV-001) as authoritative**. The Section 4.1 file table supersedes Section 4.6 references. Update any remaining documentation references during implementation.

5. **Gate the `release-spec-template.md` dependency at startup**. If the template doesn't exist, fail fast with a clear error message rather than proceeding through Phases 1–2 only to fail at Phase 3.

6. **Design the convergence loop as a standalone, testable component**. The panel-review convergence logic (predicate checking, budget guards, escalation) is the highest-complexity subsystem. Extract it into a convergence engine that can be unit-tested with mock iteration results independently of Claude subprocess management.
