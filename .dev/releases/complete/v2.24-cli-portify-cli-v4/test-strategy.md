---
validation_milestones: 8
interleave_ratio: '1:1'
---

# CLI-Portify v2.24 — Comprehensive Test Strategy

## 1. Validation Milestones Mapped to Roadmap Phases

### M0: Architecture Baseline Approved
**Validation**: Decision record completeness review
- All blocking ambiguities have documented resolutions with `[Blocking Phase N]` annotations
- Module map matches 18-module structure (DEV-001 confirmed)
- Artifact contract table covers all 9 output artifacts
- Signal vocabulary constants defined for 6 initial signal types
- **Gate**: Manual review — no automated tests; checklist sign-off

### M1: CLI and Model Foundation Operational
**Validation**: Unit test suite for config, models, and contracts
- `PortifyConfig` extends `PipelineConfig` correctly (import + instantiation test)
- CLI command group registers and parses all options (`--dry-run`, `--skip-review`, `--start`, convergence/budget/timeout controls)
- `PortifyStepResult` carries step metadata, artifact paths, gate tier, timeout settings, resume metadata as typed fields
- Contract emission produces valid JSON for all 4 terminal states: `success`, `partial`, `failed`, `dry_run`
- Contract defaults populated on failure paths (NFR-009)
- Resume command generation produces correct `--start` step and budget
- **Gate**: `uv run pytest tests/cli_portify/test_config.py tests/cli_portify/test_contracts.py` — 100% pass, <5s total

### M2: Deterministic Entry Pipeline Complete
**Validation**: Unit + lightweight integration tests for Steps 1–2
- `validate-config` completes <1s for valid input
- `validate-config` returns correct error codes for 4 failure scenarios: invalid path, derivation failure, non-writable output, name collision
- `discover-components` completes <5s for fixture skill directory
- `component-inventory.md` has correct YAML frontmatter (`source_skill`, `component_count`)
- Line counts match actual file content
- Neither step invokes Claude subprocess
- **Gate**: `uv run pytest tests/cli_portify/test_steps_deterministic.py` — 100% pass, all timing assertions met

### M3: Controlled Subprocess Platform Ready
**Validation**: Infrastructure integration tests with mock harness
- `PortifyProcess` extends `ClaudeProcess` and passes `--add-dir` correctly
- Prompt builders produce well-formed prompts with `@path` references for each step type
- Mock harness returns known-good outputs for all 5 Claude-assisted step types
- Monitoring emits NDJSON records with correct signal types
- Failure classification covers: timeout, missing artifact, malformed frontmatter, gate failure, user rejection, budget exhaustion, partial artifact
- Gate engine bindings return `tuple[bool, str]` for all gate functions
- Gate tiers (EXEMPT/STANDARD/STRICT) enforced correctly
- **Gate**: `uv run pytest tests/cli_portify/test_subprocess_platform.py tests/cli_portify/test_gates.py` — 100% pass; mock harness stable for all step types

### M4: Core Spec Generation Complete
**Validation**: Integration tests using mock harness for Steps 3–5
- `portify-analysis.md` passes STRICT gate: 5 required sections, data flow diagram, 5 YAML frontmatter fields
- `portify-spec.md` passes STRICT gate: `step_mapping_count`, `model_count`, `gate_definition_count` frontmatter present
- `--dry-run` halts after Step 4, emits `dry_run` contract with phases 3–4 marked `skipped`
- User review gate after Step 4: `y` continues, `n` produces `USER_REJECTED` status
- `synthesize-spec` produces zero remaining `{{SC_PLACEHOLDER:*}}` sentinels
- Retry prompt includes specific placeholder names on gate failure
- Template existence validated at startup (fail-fast if missing)
- **Gate**: `uv run pytest tests/cli_portify/test_content_generation.py` — 100% pass; `--dry-run` contract shape verified

### M5: Review and Convergence Pipeline Operational
**Validation**: Unit tests for convergence engine + integration tests for Steps 6–7
- Convergence engine unit tests: predicate checking, budget guards, escalation logic, terminal states (CONVERGED/ESCALATED)
- Brainstorm step passes with structured findings OR zero-gap summary
- Section 12 present with structured content (not just heading)
- Panel review terminates on convergence (0 unaddressed CRITICALs) or escalation (max iterations)
- Quality scores: `overall = mean(clarity, completeness, testability, consistency)` within 0.01 tolerance (SC-008)
- Downstream readiness boundary: 7.0 → true, 6.9 → false (SC-009)
- Additive-only protection enforced via section hashing (NFR-008)
- TurnLedger pre-launch budget guard prevents over-budget iterations
- Brainstorm/panel fallback to inline prompt when skills unavailable
- **Gate**: `uv run pytest tests/cli_portify/test_convergence.py tests/cli_portify/test_quality_steps.py` — 100% pass; boundary tests explicit

### M6: Operational Resilience Complete
**Validation**: Integration tests for resume, failure paths, and UX
- Resume works for defined resumable steps (brainstorm-gaps, panel-review)
- All 7 failure types have explicit handling: missing template, missing skills, malformed artifact, timeout, partial artifact, non-writable output, exhausted budget
- All exit paths emit complete contracts with populated defaults
- User review interaction: pause on review, stderr prompt, `y`/`n` handling
- `--skip-review` bypasses all user prompts
- Resume commands generated for resumable failures with correct `--start` and budget
- **Gate**: `uv run pytest tests/cli_portify/test_resilience.py tests/cli_portify/test_resume.py` — 100% pass

### M7: Release-Ready Implementation
**Validation**: Full compliance + evidence package
- All SC-001 through SC-014 criteria verified (see §4 below)
- End-to-end run against real skill produces all 9 artifacts
- Evidence package assembled: test results, example artifacts, failure contracts, `git diff` proof, async grep proof
- **Gate**: Full test suite green + compliance checks pass + evidence package complete

---

## 2. Test Categories

### 2.1 Unit Tests (~45 tests)

**Scope**: Pure functions, data models, deterministic logic. No subprocess invocations.

| Area | Tests | Target Files |
|------|-------|-------------|
| Config validation | Path resolution, name derivation (strip `sc-`/`-protocol`, case conversion), writability check, collision detection | `config.py`, `models.py` |
| Contract emission | 4 terminal states (success/partial/failed/dry_run), default population on failure, field completeness | `contract.py` |
| Frontmatter parsing | Valid YAML extraction, malformed YAML handling, missing frontmatter | `utils.py` |
| Score calculations | `mean(4 dimensions)` within 0.01, boundary test 7.0 true / 6.9 false, rounding behavior | `gates.py`, `scoring.py` |
| Gate result helpers | All return `tuple[bool, str]`, tier enforcement (EXEMPT/STANDARD/STRICT) | `gates.py` |
| Section hashing | Hash computation, additive-only verification, modification detection | `utils.py` |
| Resume command gen | Correct `--start` step, suggested budget, resumable step matrix | `contract.py`, `resume.py` |
| Convergence engine | Predicate checking, budget guards, terminal state transitions, max iteration enforcement | `convergence.py` |
| Name derivation | `sc-brainstorm-protocol` → `brainstorm`, `sc-task-unified` → `task-unified`, kebab/snake variants | `config.py` |
| Line counting | Accurate counts, empty files, binary file handling | `utils.py` |
| Signal vocabulary | Constant definitions, signal type validation | `signals.py` |

**Execution**: `uv run pytest tests/cli_portify/unit/ -v` — target <10s total runtime.

### 2.2 Integration Tests (~30 tests)

**Scope**: Multi-component interaction, subprocess behavior (via mock harness), artifact chaining, gate enforcement.

| Scenario | Tests | Key Assertions |
|----------|-------|----------------|
| Happy path (mocked) | Full 7-step pipeline with mock Claude outputs | All artifacts generated, all gates pass, success contract emitted |
| `--dry-run` | Pipeline halts after Step 4 | `dry_run` contract, phases 3–4 = `skipped`, no Steps 5–7 artifacts |
| Review rejection | User enters `n` at review gate | `USER_REJECTED` status, correct contract |
| Brainstorm fallback | `/sc:brainstorm` unavailable | Inline multi-persona prompt used, warning emitted, pipeline continues |
| Panel fallback | `/sc:spec-panel` unavailable | Inline fallback, marker parsing, pipeline continues |
| Convergence boundary | 0 CRITICALs on iteration 1 | CONVERGED after 1 iteration |
| Convergence max | CRITICALs persist through 3 iterations | ESCALATED after iteration 3 |
| Convergence budget | Budget exhausted mid-iteration | ESCALATED with budget warning, resume command |
| Template missing | `release-spec-template.md` absent | Fail-fast at startup, deterministic failure contract |
| Timeout per-iteration | Single iteration exceeds 300s | Timeout classification, diagnostic record |
| Placeholder retry | `synthesize-spec` leaves 2 placeholders | Retry prompt includes placeholder names, bounded retry |
| Artifact chaining | Step 3 reads Step 2 output via `@path` | Correct file references, no path scope failures |
| `--skip-review` | All review gates bypassed | No stderr prompts, pipeline completes |
| Resume from Step 6 | Trigger failure in brainstorm-gaps | Resume command has `--start brainstorm-gaps`, prior artifacts preserved |
| Resume from Step 7 | Trigger failure in panel-review | Resume command has `--start panel-review`, `focus-findings.md` preserved |

**Execution**: `uv run pytest tests/cli_portify/integration/ -v` — target <60s total (mock harness, no real Claude).

### 2.3 Compliance / Static Analysis (~6 checks)

| Check | Method | SC Reference |
|-------|--------|-------------|
| Zero `async def`/`await` in `cli_portify/` | `grep -r "async def\|await" src/superclaude/cli/cli_portify/` | SC-012 |
| Zero diffs in `pipeline/`/`sprint/` | `git diff --name-only -- src/superclaude/cli/pipeline/ src/superclaude/cli/sprint/` | SC-013 |
| Gate signatures return `tuple[bool, str]` | Type inspection in test or `grep` for return type annotations | NFR-004 |
| No Claude-directed sequencing | Code review: no subprocess output determines next step | NFR-005, NFR-006 |
| Module count = 18 under `cli_portify/` | `find src/superclaude/cli/cli_portify/ -name "*.py" | wc -l` | DEV-001 |
| Only `main.py` modified outside `cli_portify/` | `git diff --name-only` filtered to `src/superclaude/cli/` | Architectural constraint |

**Execution**: Shell script or dedicated `tests/cli_portify/test_compliance.py` — target <5s.

### 2.4 Acceptance / E2E Tests (~3 tests)

**Scope**: Real Claude subprocess invocations against actual skill directories. Run manually or in CI with `claude` binary available.

| Scenario | Input | Expected Outcome |
|----------|-------|------------------|
| Full run against `sc-brainstorm-protocol` | Real skill directory | All 9 artifacts produced, success contract, quality scores populated |
| `--dry-run` against real skill | Real skill directory | `portify-analysis.md` + `portify-spec.md` generated, pipeline halts |
| Interactive review gate | Real skill, no `--skip-review` | TUI pauses, stderr prompt visible, `y` continues |

**Execution**: Manual or `uv run pytest tests/cli_portify/e2e/ -v -m acceptance` — variable runtime (5–15 min).

---

## 3. Test-Implementation Interleaving Strategy

### Principle: 1:1 Ratio — Every Implementation Sprint Ends with Its Tests

The interleaving follows the roadmap's strict phase sequencing. Each phase produces both implementation code and its corresponding test suite before the milestone gate is evaluated.

```
Phase 0: Architecture Decisions
  └─ No code, no tests — decision record only

Phase 1: Foundation
  ├─ IMPLEMENT: config.py, models.py, contract.py, cli.py, utils.py, signals.py
  ├─ TEST: unit/test_config.py, unit/test_contracts.py, unit/test_utils.py
  └─ GATE M1: all unit tests pass

Phase 2: Deterministic Steps
  ├─ IMPLEMENT: steps/validate_config.py, steps/discover_components.py
  ├─ TEST: unit/test_validate_config.py, unit/test_discover_components.py
  │         (timing assertions, error code coverage, fixture skill dir)
  └─ GATE M2: deterministic tests pass, timing within budget

Phase 3: Subprocess Platform
  ├─ IMPLEMENT: process.py, prompt_builders.py, monitor.py, gate_engine.py
  ├─ TEST: unit/test_mock_harness.py, integration/test_subprocess_platform.py,
  │         unit/test_gates.py
  ├─ BUILD: Mock harness (critical enabler for Phases 4–5)
  └─ GATE M3: mock harness stable, gate engine deterministic

Phase 4: Content Generation
  ├─ IMPLEMENT: steps/analyze_workflow.py, steps/design_pipeline.py,
  │              steps/synthesize_spec.py
  ├─ TEST: integration/test_content_generation.py, integration/test_dry_run.py,
  │         integration/test_placeholder_retry.py
  └─ GATE M4: all STRICT gates pass with mock outputs, dry-run semantics correct

Phase 5: Quality Amplification
  ├─ IMPLEMENT: steps/brainstorm_gaps.py, steps/panel_review.py, convergence.py
  ├─ TEST: unit/test_convergence.py, integration/test_brainstorm.py,
  │         integration/test_panel_review.py, unit/test_scoring_boundary.py
  └─ GATE M5: convergence engine tests pass, boundary tests explicit

Phase 6: UX and Hardening
  ├─ IMPLEMENT: tui.py, resume logic, failure-path handling
  ├─ TEST: integration/test_resilience.py, integration/test_resume.py,
  │         integration/test_review_gates.py
  └─ GATE M6: all failure paths covered, resume commands correct

Phase 7: Validation and Release
  ├─ RUN: full test suite, compliance checks, E2E against real skill
  ├─ ASSEMBLE: evidence package
  └─ GATE M7: all SC criteria verified, evidence package complete
```

### Interleaving Rules

1. **No phase advances without its test gate passing.** M3 explicitly gates Phase 4.
2. **Mock harness built in Phase 3, consumed in Phases 4–7.** This is the critical enabler — without it, Claude-assisted step tests require real subprocess invocations.
3. **Boundary tests written alongside the logic they guard.** Score boundary (7.0/6.9) tests ship with the scoring code, not deferred to Phase 7.
4. **Compliance checks run continuously from Phase 1.** `grep` for async and `git diff` for base-module immutability run after every phase.
5. **E2E acceptance tests run only in Phase 7.** They require real Claude and are too slow for development iteration.

---

## 4. Risk-Based Test Prioritization

### Priority 1 — CRITICAL (Must pass before any merge consideration)

| Risk | Test Focus | SC Reference | Rationale |
|------|-----------|-------------|-----------|
| R-2: Convergence prompt design | Each iteration runs BOTH focus + critique; predicate checks after iteration; terminal states correct | SC-007 | Incorrect convergence = wasted iterations + unusable quality scores |
| R-1: Claude output truncation | Mock harness includes truncated output scenario; gate detects incomplete artifacts | SC-003, SC-005 | Truncation = silent corruption of spec artifacts |
| Async prohibition | Static grep scan | SC-012 | Architectural invariant — synchronous-only model |
| Base module immutability | `git diff` scan | SC-013 | Zero-modification constraint |
| Contract completeness | All 4 terminal states emit populated contracts | SC-010, NFR-009 | Every exit path must be machine-readable |
| Scoring boundary | 7.0 true / 6.9 false, mean calculation 0.01 tolerance | SC-008, SC-009 | Gate boundary correctness is non-negotiable |

### Priority 2 — HIGH (Must pass for release readiness)

| Risk | Test Focus | SC Reference |
|------|-----------|-------------|
| R-3: Budget exhaustion | TurnLedger pre-flight guard, ESCALATED terminal state, resume guidance | SC-007 |
| R-5: Subprocess `@path` scope | `--add-dir` passes work dir + workflow path; out-of-dir artifact test | FR-003–007 |
| R-7: Partial synthesize-spec | Resume re-runs step; partial output doesn't pass gate | SC-005 |
| R-10: Missing template | Fail-fast at startup with clear error | FR-005 |
| Placeholder elimination | Zero `{{SC_PLACEHOLDER:*}}` after synthesis + retry | SC-005 |
| Dry-run halt point | Correct contract, phases 3–4 = `skipped` | SC-011 |

### Priority 3 — MEDIUM (Should pass; acceptable risk if deferred with justification)

| Risk | Test Focus | SC Reference |
|------|-----------|-------------|
| R-4: Skill output parsing | Fallback structural checks when markers missing | FR-006, FR-007 |
| R-6: User review gate | stderr prompt, `y`/`n` handling, `--skip-review` bypass | NFR-011 |
| Additive-only protection | Section hashing detects unauthorized modifications | NFR-008 |
| Resume command generation | Correct `--start` step and budget for resumable failures | SC-014 |
| NDJSON logging | Events emitted with correct signal types and timing | Monitoring |

### Priority 4 — LOW (Nice to have; manual validation acceptable)

| Risk | Test Focus |
|------|-----------|
| R-9: Self-portification circularity | Manual test against `sc-cli-portify-protocol` itself |
| TUI rendering | Manual visual inspection |
| R-8: Wall-clock time | Advisory timing — measured but not blocking |

---

## 5. Acceptance Criteria Per Milestone

### M0: Architecture Baseline
- [ ] Decision record produced with per-question `[Blocking Phase N]` or `[Advisory]` annotations
- [ ] All Phase 1-blocking questions resolved (timeout semantics, resume behavior, scoring boundary)
- [ ] 18-module structure confirmed as authoritative
- [ ] Signal vocabulary constants documented (6 initial types)

### M1: CLI and Model Foundation
- [ ] `superclaude cli-portify --help` renders all options without error
- [ ] `PortifyConfig` instantiates with valid workflow path and derives correct CLI name
- [ ] `PortifyStepResult` carries typed resume metadata (not generic `dict`)
- [ ] Contract JSON validates against schema for all 4 terminal states
- [ ] Failure contract populates all fields with defaults (NFR-009 unit test)
- [ ] All unit tests pass in <5s

### M2: Deterministic Entry Pipeline
- [ ] `validate-config` returns in <1s for valid and invalid inputs
- [ ] 4 error codes tested: invalid path, derivation failure, non-writable output, name collision
- [ ] `discover-components` returns in <5s for fixture skill directory
- [ ] `component-inventory.md` has YAML frontmatter with `source_skill` and `component_count`
- [ ] Line counts match `wc -l` on fixture files
- [ ] Zero Claude subprocess invocations during Steps 1–2

### M3: Subprocess Platform
- [ ] `PortifyProcess` inherits from `ClaudeProcess` and passes `--add-dir` correctly
- [ ] Mock harness returns realistic outputs for all 5 Claude-assisted steps
- [ ] Prompt builders include `@path` references to prior artifacts
- [ ] NDJSON log contains `step_start`, `step_complete`, `step_error` signals
- [ ] Failure classification distinguishes all 7 failure types
- [ ] All gate functions return `tuple[bool, str]`
- [ ] EXEMPT/STANDARD/STRICT enforcement verified with test cases

### M4: Core Spec Generation
- [ ] `portify-analysis.md` has 5 required sections + data flow diagram + 5 frontmatter fields
- [ ] `portify-spec.md` has `step_mapping_count`, `model_count`, `gate_definition_count` frontmatter
- [ ] `--dry-run` emits correct contract with phases 3–4 = `skipped`
- [ ] Review rejection produces `USER_REJECTED` status
- [ ] Zero `{{SC_PLACEHOLDER:*}}` sentinels after synthesis
- [ ] Retry prompt includes specific placeholder names
- [ ] Template absence triggers fail-fast at startup

### M5: Review and Convergence
- [ ] Convergence engine: CONVERGED when 0 unaddressed CRITICALs
- [ ] Convergence engine: ESCALATED after `max_convergence` iterations
- [ ] TurnLedger prevents iteration launch when budget exhausted
- [ ] `overall = mean(clarity, completeness, testability, consistency)` within 0.01 (SC-008)
- [ ] Downstream readiness: 7.0 → true, 6.9 → false (SC-009)
- [ ] Section 12 present with structured findings or zero-gap summary
- [ ] Additive-only protection: hash mismatch detected on unauthorized modification
- [ ] Brainstorm fallback works when `/sc:brainstorm` unavailable
- [ ] Panel fallback works when `/sc:spec-panel` unavailable
- [ ] Convergence engine passes unit tests independently of subprocess management

### M6: Operational Resilience
- [ ] Resume from `brainstorm-gaps` restores prior artifacts and generates correct `--start` command
- [ ] Resume from `panel-review` preserves `focus-findings.md` context
- [ ] 7 failure types have explicit handling paths (tested individually)
- [ ] `--skip-review` bypasses all user prompts (no stderr output)
- [ ] User review: `y` continues, `n` halts with `USER_REJECTED`
- [ ] All exit paths emit contracts with populated defaults

### M7: Release Ready
- [ ] All SC-001 through SC-014 verified with evidence
- [ ] Zero `async def`/`await` in `cli_portify/` (grep proof)
- [ ] Zero diffs in `pipeline/`/`sprint/` (git diff proof)
- [ ] E2E run against real skill produces all 9 artifacts
- [ ] `--dry-run` E2E produces coherent analysis + design
- [ ] Evidence package assembled and complete

---

## 6. Quality Gates Between Phases

### Gate Structure

Each phase boundary enforces a gate before the next phase can begin. Gates are **blocking** — no exceptions without documented waiver.

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Phase N  │────▶│  GATE   │────▶│Phase N+1│────▶│  GATE   │──▶ ...
│  Code +  │     │ Tests   │     │  Code + │     │ Tests   │
│  Tests   │     │ Comply  │     │  Tests  │     │ Comply  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### Gate Definitions

| Gate | Between | Automated Checks | Manual Checks | Blocking? |
|------|---------|-----------------|---------------|-----------|
| G0→1 | Phase 0 → 1 | None | Decision record reviewed, ambiguities resolved | Yes |
| G1→2 | Phase 1 → 2 | Unit tests pass, CLI parses, contracts emit | Code review of model types | Yes |
| G2→3 | Phase 2 → 3 | Deterministic step tests pass, timing within budget | Verify no subprocess deps | Yes |
| **G3→4** | **Phase 3 → 4** | **Mock harness stable, gate engine tests pass, monitoring emits records** | **Subprocess platform review** | **Yes (M3 critical gate)** |
| G4→5 | Phase 4 → 5 | Content generation tests pass, dry-run correct, template validated | Artifact quality review | Yes |
| G5→6 | Phase 5 → 6 | Convergence + quality tests pass, boundary tests explicit | Convergence behavior review | Yes |
| G6→7 | Phase 6 → 7 | Resilience + resume tests pass, all failure paths covered | UX review (TUI, prompts) | Yes |
| **G7→merge** | **Phase 7 → merge** | **Full suite green, compliance green, SC matrix complete** | **Evidence package review, E2E sign-off** | **Yes** |

### Continuous Gates (Run After Every Phase)

These checks run as part of every gate, not just their originating phase:

| Check | Command | Failure Action |
|-------|---------|---------------|
| Async prohibition | `grep -r "async def\|await" src/superclaude/cli/cli_portify/` | Block phase advancement |
| Base module immutability | `git diff --name-only -- src/superclaude/cli/pipeline/ src/superclaude/cli/sprint/` | Block phase advancement |
| Test suite regression | `uv run pytest tests/cli_portify/ -v` | Block phase advancement |
| Lint clean | `uv run ruff check src/superclaude/cli/cli_portify/` | Block phase advancement |

### Gate G3→4: Special Emphasis

Phase 3 → Phase 4 is the **highest-risk transition** in the roadmap. The subprocess platform must be stable before content generation steps build on it. This gate requires:

1. Mock harness produces realistic outputs for **all 5** Claude-assisted step types
2. Gate engine correctly enforces EXEMPT, STANDARD, and STRICT tiers
3. `PortifyProcess` correctly passes `--add-dir` for both work directory and workflow path
4. Monitoring emits parseable NDJSON with timing data
5. Failure classification distinguishes all 7 failure types
6. At least one real `claude` subprocess invocation succeeds (smoke test, not full content)

### Gate G7→merge: Evidence Package Requirements

| Evidence Item | Format | Source |
|---------------|--------|--------|
| Full test results | JUnit XML or pytest output | `uv run pytest --junitxml=results.xml` |
| SC-001 through SC-014 traceability | Markdown table with pass/fail + evidence link | Manual assembly |
| Example artifacts (happy path) | 9 files in example output directory | E2E run |
| Failure contract samples | JSON files for partial, failed, dry_run | Integration test outputs |
| Async grep proof | Shell output showing zero matches | `grep` command output |
| Git diff proof | Shell output showing zero files | `git diff` command output |
| Boundary test evidence | Test output for 7.0/6.9, convergence termination, placeholder elimination | Pytest output |
| Timing data | Phase timing from NDJSON logs | E2E run |

---

## Appendix: SC Validation Matrix — Test Mapping

| SC | Criterion | Layer | Test File | Priority |
|----|-----------|-------|-----------|----------|
| SC-001 | Config <1s, 4 errors | Unit | `test_validate_config.py` | P1 |
| SC-002 | Discovery <5s, frontmatter | Unit | `test_discover_components.py` | P1 |
| SC-003 | Analysis STRICT gate | Integration | `test_content_generation.py` | P1 |
| SC-004 | Design STRICT + dry-run | Integration | `test_dry_run.py` | P1 |
| SC-005 | Zero placeholders | Integration | `test_placeholder_retry.py` | P1 |
| SC-006 | Section 12 structure | Integration | `test_brainstorm.py` | P2 |
| SC-007 | Convergence terminal state | Integration | `test_panel_review.py` | P1 |
| SC-008 | Score mean ±0.01 | Unit | `test_scoring_boundary.py` | P1 |
| SC-009 | 7.0 true / 6.9 false | Unit | `test_scoring_boundary.py` | P1 |
| SC-010 | Contract all exit paths | Unit | `test_contracts.py` | P1 |
| SC-011 | Dry-run halts Step 4 | Integration | `test_dry_run.py` | P2 |
| SC-012 | Zero async | Compliance | `test_compliance.py` | P1 |
| SC-013 | Zero base-module diffs | Compliance | `test_compliance.py` | P1 |
| SC-014 | Resume commands | Integration | `test_resume.py` | P2 |
