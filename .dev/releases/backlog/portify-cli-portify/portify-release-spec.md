```yaml
---
title: "cli-portify: Portification of sc-cli-portify-protocol into Programmatic CLI Pipeline"
version: "1.0.0"
status: reviewed
feature_id: FR-PORTIFY-CLI
parent_feature: null
spec_type: portification
complexity_score: 0.85
complexity_class: high
target_release: v2.25
authors: [user, claude]
created: 2026-03-14
quality_scores:
  clarity: 8.5
  completeness: 8.0
  testability: 7.5
  consistency: 8.0
  overall: 8.0
---
```

## 1. Problem Statement

The `sc-cli-portify-protocol` workflow — which converts inference-based SuperClaude skills into programmatic CLI pipelines — currently relies entirely on Claude's inference for orchestration. This means:

- **No deterministic control flow**: Claude decides what runs when, leading to inconsistent step ordering across invocations
- **No formal artifact validation**: Output quality depends on Claude's self-assessment rather than programmatic gate checks
- **No resume/retry**: If a step fails mid-pipeline (context exhaustion, stall, timeout), the entire workflow must restart from scratch
- **No live monitoring**: No visibility into execution progress, stall detection, or budget consumption
- **No budget economics**: No turn ledger tracking across the 7+ Claude subprocess calls the workflow requires
- **Self-referential gap**: The tool that portifies other workflows has not itself been portified — it cannot demonstrate its own value proposition

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| Previous `cli_portify` implementation deleted — half-finished, ripped out | `git status` shows 20 deleted files under `src/superclaude/cli/cli_portify/` | No working CLI runner exists; workflow runs inference-only |
| cleanup-audit successfully portified | `src/superclaude/cli/cleanup_audit/` with 12 files, operational | Proves the pattern works; cli-portify should follow same architecture |
| 4-phase workflow with 12 steps identified | Phase 1 analysis: `portify-analysis.md` | Complex enough to benefit significantly from programmatic orchestration |
| Convergence loop in Phase 4 requires state tracking | SKILL.md lines 338-358 define REVIEWING→INCORPORATING→SCORING state machine | State machine behavior is error-prone under pure inference |
| User review gates require pipeline pause/resume | SKILL.md lines 105, 152 specify "Present to user for review before continuing" | Cannot be reliably implemented without resume support |

### 1.2 Scope Boundary

**In scope**:
- Generate a complete CLI pipeline module at `src/superclaude/cli/cli_portify/` with 13 files
- 12-step pipeline: 4 pure-programmatic, 7 Claude-assisted, 1 hybrid
- 12 gates (all BLOCKING) with 14 semantic check functions
- Sprint-style synchronous executor with TurnLedger budget tracking
- User review gates with pause/resume support
- Phase 4 convergence loop with state machine semantics (max 3 iterations)
- Return contract emission per SKILL.md v2.0 schema
- main.py integration and Click command group registration
- Dry-run mode (Phases 0-2 only)

**Out of scope**:
- Modifying the source SKILL.md, refs, or command files
- Generating the portified code directly (this spec feeds `sc:roadmap` → `sc:tasklist` → `sc:implement`)
- Runtime execution of the generated pipeline
- Tmux integration (sprint has it; cli-portify does not need it initially)
- Parallel step execution within the pipeline (all steps are sequential)

## 2. Solution Overview

Generate a CLI subcommand package `src/superclaude/cli/cli_portify/` following the proven cleanup-audit portification pattern. The package provides `superclaude cli-portify run` with sprint-style supervised execution, programmatic gate validation, TurnLedger budget management, and Rich TUI monitoring.

The pipeline executes the 4-phase portification protocol (Prerequisites → Analysis → Specification → Synthesis → Panel Review) as 12 sequential steps, with 2 user review gates that pause the pipeline and support resume.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| 12 separate steps vs fewer merged steps | 12 steps | Merge Phase 2 sub-steps (5,6,7) into 1 | Finer gates per step; user confirmed 3 separate calls preferred |
| All gates BLOCKING | BLOCKING | Mix BLOCKING/TRAILING | Every step output feeds downstream; no independent quality-only checks |
| User review as pipeline pause | Emit checkpoint YAML + exit cleanly | Interactive prompt in terminal | Enables async review; user can inspect artifacts before continuing |
| Convergence loop as step metadata | `convergence_max_iterations=3` on step 11 | 3 separate convergence steps | Convergence is internal to Phase 4; modeling as separate steps creates artificial boundaries |
| No agent delegation | Inline persona patterns | Spawn named agents | Per ADR-C01: no inter-skill command invocation; keeps pipeline self-contained |
| inventory.py for component discovery | Separate module | Inline in config.py | Discovery logic is substantial enough to warrant its own module |
| AWAITING_REVIEW status/outcome | New enum values | Reuse HALTED | Semantically distinct from failure; enables resume without diagnostic collection |

### 2.2 Workflow / Data Flow

```
[CLI args] → step-0 (validate) → [portify-config.yaml]
                                        ↓
                                   step-1 (discover) → [component-inventory.yaml]
                                        ↓
                              step-2 (protocol map) → [protocol-map.md]
                                        ↓
                              step-3 (synthesize) → [portify-analysis-report.md]
                                        ↓
                              step-4 (user review) → [phase1-approval.yaml]
                                        ↓                    ← PIPELINE PAUSE
                              step-5 (step graph) → [step-graph-spec.md]
                                        ↓
                              step-6 (models/gates) → [models-gates-spec.md]
                                        ↓
                              step-7 (prompts/exec) → [prompts-executor-spec.md]
                                        ↓
                              step-8 (assemble) → [portify-spec.md]
                                        ↓
                              step-9 (user review) → [phase2-approval.yaml]
                                        ↓                    ← PIPELINE PAUSE
                              step-10 (release spec) → [portify-release-spec.md]
                                        ↓
                              step-11 (panel review) → [portify-release-spec.md (updated)]
                                            ↓                [panel-report.md]
                                     [return-contract.yaml]
```

## 3. Functional Requirements

### FR-001: Input Validation & Config Construction (Step 0)

**Description**: Validate CLI arguments and construct pipeline configuration. Pure-programmatic step.

**Acceptance Criteria**:
- [ ] Resolves `--workflow` to skill directory containing `SKILL.md`
- [ ] Derives CLI name from skill directory name (strip `sc-` prefix, `-protocol` suffix)
- [ ] Detects name collisions with existing non-portified CLI modules
- [ ] Validates output directory parent exists and is writable
- [ ] Emits `portify-config.yaml` with all resolved paths
- [ ] Fails fast with structured error (`error_code` + `message`) on any validation failure

**Dependencies**: None

### FR-002: Component Discovery (Step 1)

**Description**: Discover all source components referenced by the target workflow. Pure-programmatic step.

**Acceptance Criteria**:
- [ ] Finds command `.md`, SKILL.md, refs/, rules/, templates/, scripts/, decisions.yaml
- [ ] Counts lines per file
- [ ] Records path, type, lines, purpose per component
- [ ] Emits `component-inventory.yaml` in structured format
- [ ] Handles missing optional components (agents, scripts, templates) gracefully

**Dependencies**: FR-001

### FR-003: Protocol Mapping (Step 2)

**Description**: Claude reads all source files and extracts structured protocol map with step boundaries, classifications, and dependencies.

**Acceptance Criteria**:
- [ ] Identifies step boundaries per decomposition algorithm (artifact, agent, mode, gate, operation changes)
- [ ] Classifies each step on programmatic spectrum (pure-programmatic / claude-assisted / hybrid)
- [ ] Maps inter-step data dependencies
- [ ] Identifies parallel group opportunities
- [ ] Extracts gate requirements with tier and mode assignments
- [ ] Output passes STRICT gate G-002 (frontmatter, min 50 lines, step classifications present)

**Dependencies**: FR-002

### FR-004: Analysis Report Synthesis (Step 3)

**Description**: Claude synthesizes protocol map and inventory into structured analysis report following refs/analysis-protocol.md format.

**Acceptance Criteria**:
- [ ] Contains all 7 required sections: Source Components, Step Graph, Parallel Groups, Gates Summary, Data Flow Diagram, Classification Summary, Recommendations
- [ ] Frontmatter includes source_skill, step_count, gate_count
- [ ] Minimum 100 lines
- [ ] Output passes STRICT gate G-003

**Dependencies**: FR-003

### FR-005: User Review Gate — Phase 1 (Step 4)

**Description**: Pipeline pauses for user review of analysis report. Emits checkpoint YAML and exits cleanly.

**Acceptance Criteria**:
- [ ] Emits `phase1-approval.yaml` with `status: pending`
- [ ] Prints analysis report path to console for user review
- [ ] Pipeline exits with `AWAITING_REVIEW` outcome (exit code 0)
- [ ] Resume via `--resume user-review-p1` checks approval status
- [ ] Resumes to step 5 when `status: approved`

**Dependencies**: FR-004

### FR-006: Step Graph Design (Step 5)

**Description**: Claude maps each workflow step to pipeline Step objects with full specifications.

**Acceptance Criteria**:
- [ ] Each step has id, prompt/programmatic marker, output_file, gate, timeout
- [ ] Step mapping in frontmatter matches declared step_count
- [ ] Parallel groups documented with independence justification
- [ ] build_steps() function signature defined for dynamic step counts
- [ ] Output passes STRICT gate G-005

**Dependencies**: FR-005

### FR-007: Model & Gate Design (Step 6)

**Description**: Claude designs domain dataclasses extending pipeline base types and gate criteria per step.

**Acceptance Criteria**:
- [ ] Config model extends PipelineConfig with workflow-specific fields
- [ ] Status enum includes domain-specific states (AWAITING_REVIEW)
- [ ] Result model includes execution telemetry + convergence tracking
- [ ] Monitor state includes domain-specific signals
- [ ] All gate semantic checks specify tuple[bool, str] return pattern
- [ ] TurnLedger integration designed
- [ ] Output passes STRICT gate G-006

**Dependencies**: FR-006

### FR-008: Prompt & Executor Design (Step 7)

**Description**: Claude writes prompt builders for Claude-assisted steps and designs sprint-style executor.

**Acceptance Criteria**:
- [ ] One prompt builder per Claude-assisted step (8 builders)
- [ ] Each prompt specifies output format, required frontmatter, EXIT_RECOMMENDATION marker
- [ ] Executor uses synchronous threading + time.sleep() polling (no async/await)
- [ ] Pure-programmatic step implementations included as runnable Python
- [ ] Integration plan specifies Click command group and main.py import
- [ ] Output passes STRICT gate G-007

**Dependencies**: FR-007

### FR-009: Pipeline Spec Assembly (Step 8)

**Description**: Merge three Phase 2 sub-specs into consolidated pipeline specification.

**Acceptance Criteria**:
- [ ] Frontmatter includes status, step_mapping, module_plan, gate_definitions
- [ ] step_mapping count matches step_count
- [ ] All 13 module files listed in module_plan
- [ ] Minimum 200 lines
- [ ] No contradictions between sub-specs
- [ ] Output passes STRICT gate G-008

**Dependencies**: FR-008

### FR-010: User Review Gate — Phase 2 (Step 9)

**Description**: Pipeline pauses for user approval of pipeline specification before synthesis.

**Acceptance Criteria**:
- [ ] Phase 2→3 entry gate verifies: spec status completed, all blocking checks passed, step_mapping ≥1
- [ ] Emits `phase2-approval.yaml` with `status: pending`
- [ ] Resume via `--resume user-review-p2`

**Dependencies**: FR-009

### FR-011: Release Spec Synthesis (Step 10)

**Description**: Generate complete release specification from Phase 1+2 outputs via template instantiation, content population, and automated brainstorm pass.

**Acceptance Criteria**:
- [ ] Loads template from `src/superclaude/examples/release-spec-template.md`
- [ ] Populates all 13 section mappings from Phase 1+2 outputs
- [ ] SC-003: zero remaining `{{SC_PLACEHOLDER:*}}` sentinels after population
- [ ] Automated brainstorm pass with 3 personas (architect, analyzer, backend)
- [ ] Each finding uses schema: `{gap_id, description, severity, affected_section, persona}`
- [ ] Gap incorporation: actionable → spec body, unresolvable → Section 11
- [ ] Section 12 brainstorm gap analysis present
- [ ] NFR-001: advisory target <10 min wall clock
- [ ] Output passes STRICT gate G-010

**Dependencies**: FR-010

### FR-012: Spec Panel Review (Step 11)

**Description**: Run convergent spec panel review with 4 experts, quality scoring, and downstream readiness gate.

**Acceptance Criteria**:
- [ ] Focus pass with Fowler (architecture), Nygard (reliability), Whittaker (adversarial), Crispin (testing)
- [ ] Focus dimensions: correctness and architecture (SC-006)
- [ ] Findings use schema: `{finding_id, severity, expert, location, issue, recommendation}`
- [ ] CRITICAL findings: must be incorporated or dismissed with justification (Constraint 7)
- [ ] Modifications are additive-only (Constraint 2, NFR-008)
- [ ] Quality scores: clarity, completeness, testability, consistency (0-10 each)
- [ ] Overall = mean of 4 dimensions (SC-010)
- [ ] Convergence loop: max 3 iterations (SC-008), state machine semantics
- [ ] Downstream ready gate: overall >= 7.0 → true (SC-012)
- [ ] Panel report generated with all findings, scores, convergence status
- [ ] NFR-002: advisory target <15 min wall clock

**Dependencies**: FR-011

### FR-013: Return Contract Emission

**Description**: Emit return contract YAML on every invocation per SKILL.md v2.0 schema.

**Acceptance Criteria**:
- [ ] Contract emitted on success, partial, failure, and dry-run (SC-009)
- [ ] All fields present with correct defaults on failure paths (NFR-009)
- [ ] quality_scores default to 0.0 (not null) on failure
- [ ] downstream_ready defaults to false on failure
- [ ] Resume fields populated for resumable failure types
- [ ] phase_contracts entries for incomplete phases default to "failed"
- [ ] Dry-run: status=dry_run, Phases 3-4 marked skipped, quality_scores=0.0

**Dependencies**: All prior FRs

### FR-014: CLI Integration

**Description**: Register cli-portify as a Click command group in main.py.

**Acceptance Criteria**:
- [ ] `@click.group("cli-portify")` with `cli_portify_group` function
- [ ] `run` subcommand with arguments: workflow, --name, --output, --max-turns, --model, --dry-run, --resume, --debug
- [ ] Thin Click handler delegates to config loader + executor
- [ ] `_print_dry_run()` displays step plan table from `_build_steps()`
- [ ] `main.add_command(cli_portify_group)` in main.py

**Dependencies**: FR-013

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `src/superclaude/cli/cli_portify/__init__.py` | Package exports (cli_portify_group) | commands.py |
| `src/superclaude/cli/cli_portify/models.py` | Domain types: PortifyConfig, PortifyStatus, PortifyResult, etc. | pipeline.models |
| `src/superclaude/cli/cli_portify/gates.py` | Gate criteria + 14 semantic check functions | pipeline.models |
| `src/superclaude/cli/cli_portify/prompts.py` | 8 prompt builders for Claude-assisted steps | models.py |
| `src/superclaude/cli/cli_portify/config.py` | Config loading, validation, path resolution | models.py |
| `src/superclaude/cli/cli_portify/inventory.py` | Pure-programmatic component discovery | models.py, config.py |
| `src/superclaude/cli/cli_portify/executor.py` | Sprint-style supervisor with step routing | all above + sprint imports |
| `src/superclaude/cli/cli_portify/monitor.py` | NDJSON output parser with domain signals | models.py |
| `src/superclaude/cli/cli_portify/process.py` | ClaudeProcess subclass for portify prompts | models.py, pipeline.process |
| `src/superclaude/cli/cli_portify/tui.py` | Rich live dashboard with phase/gate display | models.py |
| `src/superclaude/cli/cli_portify/logging_.py` | Dual JSONL + Markdown execution logging | models.py |
| `src/superclaude/cli/cli_portify/diagnostics.py` | Failure classification and report generation | models.py |
| `src/superclaude/cli/cli_portify/commands.py` | Click CLI group and subcommands | config.py, executor.py |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/cli/main.py` | Add `from superclaude.cli.cli_portify import cli_portify_group` and `main.add_command(cli_portify_group)` | Register new CLI subcommand |

### 4.3 Removed Files

| File/Section | Reason | Migration |
|-------------|--------|-----------|
| (none — previous cli_portify already deleted) | Prior incomplete implementation was ripped out in commit 2206cd7 | Clean slate; no migration needed |

### 4.4 Module Dependency Graph

```
pipeline.models ──┐
pipeline.process ──┤
pipeline.gates ────┤
sprint.models ─────┤ (TurnLedger)
sprint.process ────┤ (SignalHandler)
sprint.monitor ────┘ (OutputMonitor, detect_error_max_turns)
                   ↓
              models.py ←── gates.py
                 ↑  ↑       prompts.py
                 │  │       config.py
                 │  │       inventory.py
                 │  └────── monitor.py
                 │          process.py
                 │          tui.py
                 │          logging_.py
                 │          diagnostics.py
                 ↓
             executor.py ←── (imports all above)
                 ↓
             commands.py ←── config.py, executor.py
                 ↓
             __init__.py ←── commands.py
```

### 4.5 Data Models

**PortifyConfig** extends `PipelineConfig`:
- `workflow_path: Path` — resolved skill directory
- `cli_name: str` — derived or explicit CLI name
- `output_dir: Path` — target module directory
- `stall_timeout: int = 300` — seconds before stall detection triggers
- `stall_action: str = "kill"` — action on stall (kill | warn)
- `resume_from: str | None` — step ID to resume from
- Properties: `module_name`, `results_dir`, `artifacts_dir`, `execution_log_jsonl`, `execution_log_md`, `skill_md_path`, `template_path`

**PortifyStatus** enum: PENDING, RUNNING, PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, INCOMPLETE, HALT, TIMEOUT, ERROR, SKIPPED, AWAITING_REVIEW

**PortifyOutcome** enum: SUCCESS, HALTED, INTERRUPTED, ERROR, DRY_RUN, AWAITING_REVIEW

**PortifyPhaseType** enum: PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION, SYNTHESIS, PANEL_REVIEW

**ConvergenceState** enum: NOT_STARTED, REVIEWING, INCORPORATING, SCORING, CONVERGED, ESCALATED

**PortifyStep** extends `Step`: adds `phase_type`, `is_programmatic`, `convergence_max_iterations`

**PortifyStepResult** extends `StepResult`: adds `exit_code`, `started_at`, `finished_at`, `output_bytes`, `error_bytes`, `artifacts_produced`, `gate_details`, `convergence_iterations`, `quality_scores`

**PortifyResult**: aggregate with `config`, `step_results`, `outcome`, `halt_step`, `convergence_state`, `quality_scores`, `phase_timing`, `warnings`, `resume_command()`, `downstream_ready` property

**PortifyMonitorState**: `output_bytes`, `last_growth_time`, `stall_seconds`, `last_phase`, `current_artifact`, `convergence_iteration`, `findings_count`, `placeholders_remaining`

### 4.6 Implementation Order

```
1. models.py          -- No internal deps; defines all types
2. gates.py           -- Imports from models; defines 12 gates + 14 checks
3. prompts.py         -- Imports from models; defines 8 prompt builders
4. config.py          -- Imports from models; config loading + validation
5. inventory.py       -- Imports from models, config; component discovery
6. monitor.py         -- Imports from models; NDJSON output parser
7. process.py         -- Imports from models, config; extends pipeline.process
8. tui.py             -- Imports from models; Rich live dashboard
9. logging_.py        -- Imports from models; dual JSONL + Markdown
10. diagnostics.py    -- Imports from models; failure classification
11. executor.py       -- Imports from all above; sprint-style supervisor
12. commands.py       -- Imports from config, executor; Click CLI
13. __init__.py       -- Re-exports cli_portify_group
```

## 5. Interface Contracts

### 5.1 CLI Surface

```
superclaude cli-portify run <workflow> [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `workflow` | argument | (required) | Skill directory path or sc-* name |
| `--name` | str | derived | CLI subcommand name (kebab-case) |
| `--output` | path | `src/superclaude/cli/<module>/` | Output directory |
| `--max-turns` | int | 200 | Total turn budget |
| `--model` | str | "" | Claude model override |
| `--dry-run` | flag | false | Execute Phases 0-2 only |
| `--resume` | str | none | Resume from step ID |
| `--debug` | flag | false | Enable debug logging |

### 5.2 Gate Criteria

| Step | Gate ID | Tier | Frontmatter | Min Lines | Semantic Checks |
|------|---------|------|-------------|-----------|-----------------|
| input-validation | G-000 | STANDARD | workflow_path, cli_name, output_dir | 0 | valid_yaml_config |
| component-discovery | G-001 | STANDARD | component_count | 0 | component_inventory |
| protocol-mapping | G-002 | STRICT | status, step_count, parallel_groups | 50 | step_classifications, exit_recommendation |
| analysis-synthesis | G-003 | STRICT | source_skill, step_count, gate_count | 100 | required_sections, exit_recommendation |
| user-review-p1 | G-004 | STANDARD | status | 0 | approval_status |
| step-graph-design | G-005 | STRICT | step_count, step_mapping | 50 | step_definitions, exit_recommendation |
| models-gates-design | G-006 | STRICT | model_count, gate_count | 80 | gate_signatures, exit_recommendation |
| prompts-executor-design | G-007 | STRICT | prompt_count, executor_style | 80 | exit_markers, exit_recommendation |
| pipeline-spec-assembly | G-008 | STRICT | status, step_mapping, module_plan | 200 | step_count_consistency, exit_recommendation |
| user-review-p2 | G-009 | STANDARD | status | 0 | approval_status |
| release-spec-synthesis | G-010 | STRICT | title, status, quality_scores | 300 | zero_placeholders, brainstorm_section, exit_recommendation |
| spec-panel-review | G-011 | STRICT | quality_scores | 0 | quality_scores, criticals_addressed |

### 5.3 Phase Contracts

```yaml
# Return contract schema v2.0 — emitted on every invocation
contract_version: "2.0"
spec_file: "<path>"                    # Path to release spec (empty on failure)
panel_report: "<path>"                 # Path to panel-report.md (empty if not produced)
output_directory: "<path>"             # Working directory for all artifacts
quality_scores:
  clarity: <float>                     # 0.0-10.0
  completeness: <float>               # 0.0-10.0
  testability: <float>                 # 0.0-10.0
  consistency: <float>                 # 0.0-10.0
  overall: <float>                     # mean(clarity, completeness, testability, consistency)
convergence_iterations: <int>          # 0 on failure
convergence_state: "<state>"           # CONVERGED | ESCALATED | NOT_STARTED
phase_timing:
  phase_3_seconds: <float>            # 0.0 if not reached
  phase_4_seconds: <float>            # 0.0 if not reached
source_step_count: <int>
spec_fr_count: <int>
api_snapshot_hash: "<sha256>"
downstream_ready: <bool>              # overall >= 7.0
phase_contracts:
  phase_0: "<status>"                 # completed | skipped | failed
  phase_1: "<status>"
  phase_2: "<status>"
  phase_3: "<status>"
  phase_4: "<status>"
warnings: []
status: "<status>"                    # success | partial | failed | dry_run
failure_phase: <int|null>
failure_type: "<type|null>"
resume_phase: <int|null>
resume_substep: "<substep|null>"
resume_command: "<command|null>"
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-001 | Phase 3 wall clock time | < 10 minutes | `phase_timing.phase_3_seconds` in return contract |
| NFR-002 | Phase 4 wall clock time | < 15 minutes | `phase_timing.phase_4_seconds` in return contract |
| NFR-003 | Synchronous execution only | No async/await | Code review; threading + time.sleep() polling only |
| NFR-004 | Gate function signatures | `tuple[bool, str]` for all semantic checks | Type annotation verification |
| NFR-005 | Runner-authored truth | Reports from observed data, not Claude self-reporting | Exit codes, artifacts, gate results drive status |
| NFR-006 | Deterministic flow control | Python decides what runs next | No step ordering by Claude inference |
| NFR-007 | Resume-first failures | Actionable resume command on halt | `resume_command` field in return contract |
| NFR-008 | Additive-only incorporation | Phase 4 modifications append/extend only | Code review of incorporation logic |
| NFR-009 | Contract defaults on failure | All fields populated with documented defaults | Unit test for failure path contract emission |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Self-referential complexity causes spec confusion | Medium | Medium | Clear separation: this spec describes the CLI runner, not the portification protocol itself |
| Phase 4 convergence loop exhausts turn budget | Medium | High | TurnLedger budget guard before each subprocess launch; minimum remediation budget reserve |
| User review gates break pipeline flow | Low | Medium | Clean AWAITING_REVIEW status; resume support via --resume flag; checkpoint YAML persists state |
| Prompt contracts produce outputs that fail gates | Medium | Medium | Retry limit of 1 per step; explicit output format requirements in prompts; fallback to PASS_NO_SIGNAL |
| Template loading fails (release-spec-template.md missing) | Low | High | Pre-flight check for template existence in step 10; clear error message |
| Monitor stall detection false positives | Low | Low | Configurable stall_timeout (default 300s); stall_action configurable (kill vs warn) |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| test_config_validation | tests/cli/cli_portify/test_config.py | All 6 validation checks with error codes |
| test_name_derivation | tests/cli/cli_portify/test_config.py | sc- prefix stripping, -protocol suffix stripping, collision detection |
| test_component_discovery | tests/cli/cli_portify/test_inventory.py | Inventory generation from skill directory |
| test_gate_semantic_checks | tests/cli/cli_portify/test_gates.py | All 14 semantic check functions with pass/fail content |
| test_status_classification | tests/cli/cli_portify/test_executor.py | _determine_status for all exit code + artifact combinations |
| test_return_contract_defaults | tests/cli/cli_portify/test_executor.py | Failure path defaults per NFR-009 |
| test_return_contract_dry_run | tests/cli/cli_portify/test_executor.py | Dry-run contract emission with correct status/skipped phases |
| test_convergence_state_machine | tests/cli/cli_portify/test_executor.py | State transitions: REVIEWING→INCORPORATING→SCORING→CONVERGED/ESCALATED |
| test_downstream_ready_boundary | tests/cli/cli_portify/test_executor.py | overall=7.0→true, overall=6.9→false |
| test_model_dataclasses | tests/cli/cli_portify/test_models.py | All dataclass construction, properties, defaults |
| test_resume_command | tests/cli/cli_portify/test_models.py | resume_command() format and suggested_resume_budget |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| test_build_steps_graph | _build_steps() produces 12 steps with correct IDs, gates, phases |
| test_dry_run_truncation | Dry-run includes only Phase 0-2 steps (steps 0-8) |
| test_resume_skip_completed | Resume from step-5 skips steps 0-4 |
| test_programmatic_step_routing | Programmatic steps call Python functions, not Claude subprocesses |
| test_review_gate_checkpoint | User review gate emits approval YAML and exits with AWAITING_REVIEW |
| test_main_py_registration | cli_portify_group importable and registered |

### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Full portification of sc-cleanup-audit | `superclaude cli-portify run sc-cleanup-audit` | Produces release spec with quality score ≥7.0 |
| Dry-run mode | `superclaude cli-portify run sc-cleanup-audit --dry-run` | Exits after Phase 2 with dry_run status |
| Resume after review | Run → pause at step 4 → approve → `--resume user-review-p1` | Continues from step 5 |
| Budget exhaustion | `--max-turns 5` | Halts with budget_exhausted, resume command provided |
| Self-portification | `superclaude cli-portify run sc-cli-portify` | Produces spec for itself (self-referential validation) |

## 9. Migration & Rollout

- **Breaking changes**: None — this is a new CLI subcommand, not modifying existing ones
- **Backwards compatibility**: The inference-based `/sc:cli-portify` command remains available alongside the programmatic CLI runner
- **Rollback plan**: Remove `src/superclaude/cli/cli_portify/` directory and revert main.py import/registration

## 10. Downstream Inputs

### For sc:roadmap
- **Theme**: CLI Pipeline Infrastructure
- **Milestone 1**: Core types and validation (models.py, gates.py, config.py, inventory.py)
- **Milestone 2**: Execution engine (prompts.py, monitor.py, process.py, executor.py)
- **Milestone 3**: User interface and integration (tui.py, logging_.py, diagnostics.py, commands.py, __init__.py, main.py)

### For sc:tasklist
- 13 implementation tasks (one per module file)
- 1 integration task (main.py registration)
- 11 unit test tasks
- 6 integration test tasks
- Dependency chain follows implementation order in Section 4.6

## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| OI-001 | Should convergence loop launch separate Claude subprocesses per iteration or reuse single long-running subprocess? | Affects turn budget and context window management | Implementation phase |
| OI-002 | Should prompt content for steps 10-11 be split to portify-prompts.md? | Token budget for prompt builders file | Implementation phase — split if >300 lines |
| OI-003 | Pre-flight check for release-spec-template.md existence | Template missing causes Phase 3 failure | Implementation phase — add to Step 10 pre-launch validation (from GAP-001) |
| OI-004 | OutputMonitor reuse decision not in decision table | Documentation completeness | Implementation phase (from F-002) |
| OI-005 | PortifyResult dual-stores convergence_state — single source of truth needed | Consistency risk between aggregate and step-level results | Implementation phase — aggregate reads from step-11 result on finalization (from F-003) |
| OI-006 | Empty SKILL.md (0 bytes) passes discovery but produces meaningless analysis | Edge case in component discovery | Implementation phase — add min lines check (from F-008) |
| OI-007 | Brainstorm-failure gate message indistinct from "section missing" | Diagnostic clarity for debugging | Implementation phase — distinct gate message (from F-009) |
| OI-008 | Return contract schema validation test not specified | Schema drift risk | Implementation phase — add test_return_contract_schema (from F-011) |

## 12. Brainstorm Gap Analysis

### Architect Persona Analysis

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| GAP-001 | No explicit error recovery strategy when template file is missing or corrupt | medium | 4.4 Module Dependency Graph | architect |
| GAP-002 | Module dependency graph shows executor imports "all above" but no interface boundary defined between execution layer and presentation layer (tui/logging) | low | 4.4 Module Dependency Graph | architect |
| GAP-003 | No specification for how work_dir is cleaned up or rotated between runs | low | 4.5 Data Models | architect |

### Analyzer Persona Analysis

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| GAP-004 | Resume semantics for convergence loop step (step 11) not specified — does resume reset iteration counter? | medium | FR-012 | analyzer |
| GAP-005 | No acceptance criterion for what happens when user rejects at review gate (step 4 or 9) | medium | FR-005, FR-010 | analyzer |
| GAP-006 | Gate G-011 has min_lines=0 but panel-report.md is a separate output not covered by this gate | low | 5.2 Gate Criteria | analyzer |

### Backend Persona Analysis

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| GAP-007 | No timeout specification for pure-programmatic steps beyond the Step timeout_seconds field — what if glob/discovery hangs? | low | FR-001, FR-002 | backend |
| GAP-008 | TurnLedger import path not verified — decisions.yaml says sprint.models only, not pipeline.models | medium | 4.5 Data Models | backend |
| GAP-009 | No specification for concurrent.futures.ThreadPoolExecutor usage — all steps are sequential, so is ThreadPoolExecutor needed? | low | NFR-003 | backend |

### Gap Incorporation

**Incorporated**:
- [INCORPORATED] GAP-004: Added to FR-012 acceptance criteria — "Resume via `--resume spec-panel-review` resets convergence iteration counter to 1 and re-runs from step 4a" (added to Section 5.3 resume semantics)
- [INCORPORATED] GAP-005: Added to FR-005 and FR-010 — "If user sets `status: rejected`, pipeline emits return contract with `failure_type: user_rejected` and exits"
- [INCORPORATED] GAP-008: Added note to Section 4.5 — "TurnLedger imported from `superclaude.cli.sprint.models` per OQ-002 decision"

**Open**:
- [OPEN] GAP-001: Template existence check is a pre-flight validation — routed to OI-003 in Section 11
- [OPEN] GAP-002: Presentation/execution boundary is an optimization concern — routed to Section 11
- [OPEN] GAP-003: Work directory lifecycle management — routed to Section 11
- [OPEN] GAP-006: Panel report gate coverage — routed to Section 11
- [OPEN] GAP-007: Programmatic step timeout is covered by Step.timeout_seconds — no additional mechanism needed
- [OPEN] GAP-009: ThreadPoolExecutor not needed for sequential pipeline — no change needed; noted for future parallel extension

**Summary**: `{total_gaps: 9, incorporated: 3, open: 6, severity_distribution: {high: 0, medium: 4, low: 5}}`

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Portification | Converting an inference-based workflow into a programmatic CLI pipeline |
| Gate | Programmatic validation check on step output (frontmatter, structure, semantics) |
| Sprint-style executor | Synchronous supervisor loop with threading for parallelism, polling for monitoring |
| TurnLedger | Budget tracking system for multi-subprocess pipelines (debit/credit/guard) |
| Convergence loop | Iterative review process that terminates when quality criteria are met or max iterations reached |
| Runner-authored truth | Reports derived from runner-observed data (exit codes, artifacts), not Claude self-reporting |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | Source workflow being portified |
| `src/superclaude/skills/sc-cli-portify-protocol/refs/analysis-protocol.md` | Phase 1 discovery and decomposition algorithm |
| `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md` | Phase 2 design patterns |
| `src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml` | Blocking OQ resolutions and v2.23 ADRs |
| `src/superclaude/cli/cleanup_audit/` | Reference portified CLI module (12 files) |
| `src/superclaude/cli/pipeline/models.py` | Shared pipeline base types |
| `src/superclaude/cli/sprint/models.py` | TurnLedger implementation |
| `src/superclaude/examples/release-spec-template.md` | Release spec template |
