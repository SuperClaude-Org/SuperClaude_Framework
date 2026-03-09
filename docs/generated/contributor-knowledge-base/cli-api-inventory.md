# CLI API Inventory

## Scope and source of truth

This inventory documents the current Python code under `src/superclaude/cli/` as it exists in this repository on 2026-03-09.

When older hand-written docs and current code differ, prefer the code. In particular, command wiring and exported symbols below are derived from the current package source, not from older README-style summaries.

## Package overview

`src/superclaude/cli/` is the implementation package behind the `superclaude` console script.

| Item | Current code evidence | Notes for contributors |
| --- | --- | --- |
| Console entry point | `pyproject.toml` → `superclaude = "superclaude.cli.main:main"` | The Click root group lives in `src/superclaude/cli/main.py`. |
| Root package export | `src/superclaude/cli/__init__.py` exports `main` | Importing `superclaude.cli` exposes the top-level Click entry point. |
| CLI style | Click command groups and subcommands | Top-level commands are defined in `main.py`; larger workflow CLIs live in subpackages. |
| Major subsystems | install/update flows, MCP installation, health checks, sprint, roadmap, cleanup-audit, shared pipeline helpers, audit helpers | `pipeline/` and `audit/` are support libraries; `sprint/`, `roadmap/`, and `cleanup_audit/` expose subcommand groups. |

## Directory map

```text
src/superclaude/cli/
├── __init__.py
├── main.py
├── doctor.py
├── install_agents.py
├── install_commands.py
├── install_core.py
├── install_mcp.py
├── install_skill.py
├── install_skills.py
├── audit/
├── cleanup_audit/
├── pipeline/
├── roadmap/
└── sprint/
```

## Top-level entry points

### Root Click group

| Symbol | File | Kind | Role |
| --- | --- | --- | --- |
| `main` | `src/superclaude/cli/main.py` | Click group | Root `superclaude` CLI group with version support. |

### Top-level commands registered in `main.py`

| CLI command | Python function | Primary dependencies | Purpose |
| --- | --- | --- | --- |
| `superclaude install` | `install` | `install_core`, `install_commands`, `install_agents`, `install_skill`, `install_skills` | Install core framework files, slash commands, agents, and skills. |
| `superclaude mcp` | `mcp` | `install_mcp` | List or install MCP servers. |
| `superclaude update` | `update` | `install_core`, `install_commands`, `install_agents`, `install_skills` | Force-refresh installed framework assets. |
| `superclaude install-skill <name>` | `install_skill` | `install_skill` | Install one skill into the Claude Code skills directory. |
| `superclaude doctor` | `doctor` | `doctor.run_doctor` | Run installation/configuration checks and return non-zero on failure. |
| `superclaude version` | `version` | package `__version__` | Print framework version. |
| `superclaude sprint ...` | `sprint_group` added via `main.add_command(...)` | `src/superclaude/cli/sprint/` | Multi-phase sprint execution workflow. |
| `superclaude roadmap ...` | `roadmap_group` added via `main.add_command(...)` | `src/superclaude/cli/roadmap/` | Roadmap generation and validation workflow. |
| `superclaude cleanup-audit ...` | `cleanup_audit_group` added via `main.add_command(...)` | `src/superclaude/cli/cleanup_audit/` | Read-only cleanup audit workflow. |

## Top-level module inventory

| Module | Key symbols observed | Contributor notes |
| --- | --- | --- |
| `src/superclaude/cli/__init__.py` | `main` | Minimal re-export of the root CLI entry point. |
| `src/superclaude/cli/main.py` | `main`, `install`, `mcp`, `update`, `install_skill`, `doctor`, `version` | First file to read when tracing command registration. Also manually registers the `sprint`, `roadmap`, and `cleanup-audit` groups. |
| `src/superclaude/cli/doctor.py` | `run_doctor`, `_check_pytest_plugin`, `_check_agents_installed`, `_check_skills_installed`, `_check_configuration` | Health-check implementation used by the `doctor` command. |
| `src/superclaude/cli/install_core.py` | `install_core_files`, `list_core_files`, `list_installed_core_files` | Handles installation/listing of core framework files. |
| `src/superclaude/cli/install_commands.py` | `install_commands`, `list_available_commands`, `list_installed_commands` | Handles slash command asset installation. |
| `src/superclaude/cli/install_agents.py` | `install_agents`, `list_available_agents`, `list_installed_agents` | Handles agent asset installation; includes `_EXCLUDE_FILES` filter constant. |
| `src/superclaude/cli/install_skill.py` | `install_skill_command`, `list_available_skills`, `_get_skill_source`, `_is_valid_skill_dir` | Single-skill installer and skill discovery helpers. |
| `src/superclaude/cli/install_skills.py` | `install_all_skills`, `list_installed_skills`, `_has_corresponding_command` | Bulk skill installer. |
| `src/superclaude/cli/install_mcp.py` | `AIRIS_GATEWAY`, `MCP_SERVERS`, `install_mcp_servers`, `list_available_servers`, `install_mcp_server` | MCP server catalog and install orchestration. |

## Subpackage inventory

## `sprint/` subpackage

### Purpose

Implements the `superclaude sprint` command group for orchestrating multi-phase Claude Code sprint execution.

### Public command group

| Symbol | File | Role |
| --- | --- | --- |
| `sprint_group` | `src/superclaude/cli/sprint/commands.py` | Click subcommand group, re-exported by `src/superclaude/cli/sprint/__init__.py`. |

### Command structure

| CLI command | Python function | What it does |
| --- | --- | --- |
| `superclaude sprint run` | `run` | Loads sprint config, discovers phases, and either dry-runs, launches in tmux, or executes directly. |
| `superclaude sprint attach` | `attach` | Reattaches to a running sprint tmux session. |
| `superclaude sprint status` | `status` | Reads sprint execution status from logs. |
| `superclaude sprint logs` | `logs` | Tails the sprint execution log, optionally following output. |
| `superclaude sprint kill` | `kill` | Stops a running sprint, with optional force mode. |

### Important modules

| Module | Key API surface observed | Why it matters |
| --- | --- | --- |
| `commands.py` | `sprint_group`, `run`, `attach`, `status`, `logs`, `kill`, `_print_dry_run` | User-facing CLI layer. |
| `config.py` | `discover_phases`, `validate_phases`, `load_sprint_config`, `parse_tasklist`, `parse_tasklist_file` | Phase discovery and config loading. |
| `models.py` | `SprintConfig`, `Phase`, `TaskResult`, `PhaseResult`, `SprintResult`, `SprintStep`, `TaskStatus`, `PhaseStatus`, `SprintOutcome`, `MonitorState`, `TurnLedger`, `ShadowGateMetrics` | Main typed data model for sprint state and outputs. |
| `executor.py` | `execute_sprint`, `execute_phase_tasks`, `aggregate_task_results`, `setup_isolation`, `check_budget_guard`, `SprintGatePolicy`, `IsolationLayers`, `AggregatedPhaseReport` | Core runtime orchestration. |
| `process.py` | file present | Sprint-specific process helpers. |
| `tmux.py` | file present | Session launch/attach/kill integration. |
| `monitor.py`, `tui.py` | files present | Status display and live UI surfaces. |
| `logging_.py`, `debug_logger.py` | files present | Execution logging and debug output. |
| `diagnostics.py`, `kpi.py`, `notify.py` | files present | Diagnostics, metrics, and notifications. |

## `roadmap/` subpackage

### Purpose

Implements the `superclaude roadmap` command group. Current code describes this as an 8-step roadmap generation pipeline built on the shared `pipeline/` foundation, with a separate validation command.

### Public command group

| Symbol | File | Role |
| --- | --- | --- |
| `roadmap_group` | `src/superclaude/cli/roadmap/commands.py` | Click subcommand group, re-exported by `src/superclaude/cli/roadmap/__init__.py`. |

### Command structure

| CLI command | Python function | What it does |
| --- | --- | --- |
| `superclaude roadmap run` | `run` | Parses agent specs, builds `RoadmapConfig`, and executes the roadmap pipeline. |
| `superclaude roadmap validate` | `validate` | Builds `ValidateConfig`, runs validation, and prints blocking/warning/info counts. |

### Important modules

| Module | Key API surface observed | Why it matters |
| --- | --- | --- |
| `commands.py` | `roadmap_group`, `run`, `validate` | CLI entry layer for roadmap flows. |
| `models.py` | `AgentSpec`, `RoadmapConfig`, `ValidateConfig` | Core config and agent-spec parsing types. |
| `executor.py` | `execute_roadmap`, `roadmap_run_step`, `_build_steps`, state helpers, decomposition/validation helpers | Main roadmap pipeline orchestration. |
| `validate_executor.py` | `execute_validate`, `validate_run_step`, input validation helpers, single-/multi-agent step builders | Post-run validation execution path. |
| `gates.py`, `validate_gates.py` | files present | File and gate validation logic. |
| `prompts.py`, `validate_prompts.py` | files present | Prompt/template material used by roadmap subprocess steps. |
| `__init__.py` | `roadmap_group` | Public export surface. |

## `cleanup_audit/` subpackage

### Purpose

Implements the `superclaude cleanup-audit` command group. Current package docstring says it was portified from `sc-cleanup-audit-protocol` and exposes the cleanup-audit CLI group.

### Public command group

| Symbol | File | Role |
| --- | --- | --- |
| `cleanup_audit_group` | `src/superclaude/cli/cleanup_audit/commands.py` | Click subcommand group, re-exported by `src/superclaude/cli/cleanup_audit/__init__.py`. |

### Command structure

| CLI command | Python function | What it does |
| --- | --- | --- |
| `superclaude cleanup-audit run` | `run` | Loads audit config, optionally prints a dry run, executes the cleanup-audit pipeline, and exits non-zero on unsuccessful outcome. |

### Important modules

| Module | Key API surface observed | Why it matters |
| --- | --- | --- |
| `commands.py` | `cleanup_audit_group`, `run`, `_print_dry_run` | User-facing CLI entry layer. |
| `config.py` | `load_cleanup_audit_config`, `discover_files`, `batch_files`; constants `SUPPORTED_PASSES`, `SUPPORTED_FOCUS` | Audit target discovery and batching. |
| `models.py` | `CleanupAuditConfig`, `CleanupAuditResult`, `CleanupAuditStep`, `CleanupAuditStepResult`, `CleanupAuditStatus`, `CleanupAuditOutcome`, `AuditPassType`, `CleanupAuditMonitorState` | Typed model layer for audit execution. |
| `executor.py` | `execute_cleanup_audit`, `_build_steps`, `_determine_status` | Pipeline orchestration. |
| `gates.py`, `prompts.py`, `process.py`, `monitor.py`, `tui.py`, `diagnostics.py`, `logging_.py` | files present | Supporting validation, prompting, runtime, monitoring, and diagnostics pieces. |
| `portify-summary.md` | generated summary file in package directory | Historical/generated support artifact; useful for understanding portification context, but current code should take precedence. |

## `pipeline/` subpackage

### Purpose

Shared pipeline foundation used by workflow-oriented CLIs. The package docstring explicitly describes it as the shared base for sprint and roadmap commands, and its `__all__` exposes a broad reusable API.

### Exported/public surface from `pipeline/__init__.py`

| Category | Exported symbols |
| --- | --- |
| Core models | `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`, `SemanticCheck`, `Deliverable`, `DeliverableKind` |
| Execution/process | `execute_pipeline`, `ClaudeProcess`, `gate_passed` |
| Deliverable analysis | `decompose_deliverables`, `is_behavioral` |
| Guard analysis | `GuardDetection`, `GuardKind`, `TypeTransitionKind`, `GuardAnalysisOutput`, `run_guard_analysis_pass`, `GuardResolutionOutput`, `ReleaseGateWarning`, `AcceptedRisk` |
| Invariants/FMEA | `InvariantRegistryOutput`, `run_invariant_registry_pass`, `DetectionDifficulty`, `Severity`, `FMEAFailureMode`, `classify_failure_modes`, `FMEAPromotionOutput`, `ReleaseGateViolation`, `promote_failure_modes`, `CombinedM2Output`, `run_combined_m2_pass` |
| Dataflow/conflict analysis | `DataFlowGraph`, `DataFlowNode`, `DataFlowEdge`, `NodeOperation`, `build_dataflow_graph`, `ImplicitContract`, `extract_implicit_contracts`, `ConflictKind`, `ConflictDetection`, `detect_conflicts`, `DataFlowTracingOutput`, `run_dataflow_tracing_pass` |
| Trailing gate/remediation | `TrailingGatePolicy`, `TrailingGateResult`, `TrailingGateRunner`, `GateResultQueue`, `GateScope`, `DeferredRemediationLog`, `RemediationEntry`, `RemediationStatus`, `build_remediation_prompt`, `resolve_gate_mode` |
| Conflict review helpers | `ConflictAction`, `ConflictReviewResult`, `detect_file_overlap`, `review_conflicts` |
| Diagnostics | `DiagnosticReport`, `DiagnosticStage`, `StageResult`, `run_diagnostic_chain` |

### Important modules

| Module | Key API surface observed | Why it matters |
| --- | --- | --- |
| `__init__.py` | Broad `__all__` export list | Best starting point for shared workflow primitives. |
| `models.py` | `StepStatus`, `GateMode`, `SemanticCheck`, `GateCriteria`, `Step`, `StepResult`, `DeliverableKind`, `Deliverable`, `PipelineConfig` | Common typed model layer. |
| `executor.py` | `execute_pipeline`, `_execute_single_step`, `_run_parallel_steps`, `_build_state`, `StepRunner` | Generic pipeline runner. |
| `process.py` | `ClaudeProcess` with `build_command`, `build_env`, `start`, `wait`, `terminate` | Shared subprocess wrapper for Claude execution. |
| `gates.py`, `deliverables.py`, `trailing_gate.py` | files present | Gate enforcement, deliverable handling, remediation/trailing gate logic. |
| `guard_*`, `invariant_pass.py`, `fmea_*`, `combined_m2_pass.py` | files present | Analysis passes layered on top of the generic pipeline model. |
| `dataflow_*`, `contract_extractor.py`, `conflict_*` | files present | Cross-step structural analysis and conflict handling. |
| `diagnostic_chain.py`, `verification_emitter.py`, `mutation_inventory.py`, `state_detector.py` | files present | Diagnostics and verification support. |

## `audit/` subpackage

### Purpose

Support library for cleanup/audit-oriented analysis. The package docstring calls it a cleanup-audit v2 module covering classification, coverage, checkpointing, validation, and profiling.

### Important modules

| Module | Key API surface observed | Why it matters |
| --- | --- | --- |
| `tool_orchestrator.py` | `ToolOrchestrator`, `ResultCache`, `FileAnalysis`, `CacheStats`, `compute_content_hash` | Central orchestration/cache layer for per-file and batch analysis. |
| `validation.py` | `ValidationResult`, `stratified_sample`, `validate_consistency` | Validation utilities. |
| `classification.py`, `duplication.py`, `dead_code.py`, `dynamic_imports.py`, `dependency_graph.py`, `coverage.py` | files present | Domain-specific audit analyses. |
| `checkpoint.py`, `resume.py`, `batch_decomposer.py`, `batch_retry.py`, `budget.py` | files present | Audit execution control and resilience helpers. |
| `artifact_emitter.py`, `report_completeness.py`, `report_depth.py`, `report_limitations.py`, `validation_output.py` | files present | Reporting and artifact shaping. |
| `credential_scanner.py`, `gitignore_checker.py`, `manifest_gate.py`, `evidence_gate.py`, `anti_lazy.py`, `known_issues.py` | files present | Safety, policy, and evidence-oriented checks. |
| `docs_audit.py`, `filetype_rules.py`, `dir_assessment.py`, `profile_generator.py`, `profiler.py`, `env_matrix.py` | files present | Supporting audit heuristics and profiling. |

## Command group structure at a glance

| Level | Registered names |
| --- | --- |
| Root group | `superclaude` |
| Root commands | `install`, `mcp`, `update`, `install-skill`, `doctor`, `version` |
| Root subgroups | `sprint`, `roadmap`, `cleanup-audit` |
| Sprint subcommands | `run`, `attach`, `status`, `logs`, `kill` |
| Roadmap subcommands | `run`, `validate` |
| Cleanup-audit subcommands | `run` |

## Contributor navigation tips

### If you need to change command registration
Start with `src/superclaude/cli/main.py`.

That file owns:
- the root Click group
- top-level commands
- manual registration of `sprint`, `roadmap`, and `cleanup-audit`

### If you need to change installation behavior
Read these in order:
1. `src/superclaude/cli/main.py`
2. `src/superclaude/cli/install_core.py`
3. `src/superclaude/cli/install_commands.py`
4. `src/superclaude/cli/install_agents.py`
5. `src/superclaude/cli/install_skill.py` and `install_skills.py`
6. `src/superclaude/cli/install_mcp.py`

### If you need to change workflow orchestration
Use this split:
- `sprint/`, `roadmap/`, `cleanup_audit/` for user-facing workflow CLIs
- `pipeline/` for shared execution, gate, process, and analysis primitives
- `audit/` for lower-level audit analysis and reporting support

### If older docs disagree with current code
Prefer the current package code.

Examples from the current tree:
- the active console-script target is `superclaude.cli.main:main`
- the currently registered root workflow groups are `sprint`, `roadmap`, and `cleanup-audit`
- `pipeline/__init__.py` exports a larger shared API surface than older high-level docs usually summarize

## Fast start reading order for contributors

1. `pyproject.toml` — console-script wiring
2. `src/superclaude/cli/main.py` — root command graph
3. One workflow package:
   - `src/superclaude/cli/sprint/commands.py`, or
   - `src/superclaude/cli/roadmap/commands.py`, or
   - `src/superclaude/cli/cleanup_audit/commands.py`
4. Matching `models.py` and `executor.py`
5. `src/superclaude/cli/pipeline/__init__.py` and `pipeline/models.py`
6. `src/superclaude/cli/audit/` if the change touches cleanup/audit internals
