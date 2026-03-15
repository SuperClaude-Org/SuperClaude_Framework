---
deliverable: D-0008
task: T02.01
title: IronClaude Component Inventory
status: complete
component_groups: 8
auggie_fallback: false
generated: 2026-03-14
---

# D-0008: IronClaude Component Inventory

## Summary

All 8 IronClaude component groups identified with verified file paths, exposed interfaces, internal dependencies, and extension points. Discovery performed via Auggie MCP `codebase-retrieval` against `/config/workspace/IronClaude`. No fallback activated.

---

## Component Group 1: Roadmap Pipeline

### File Paths (verified)
- `src/superclaude/cli/roadmap/commands.py` — Click CLI entry point (`roadmap_group`, `run` subcommand)
- `src/superclaude/cli/roadmap/executor.py` — 9-step pipeline orchestration (`execute_roadmap`, `_build_steps`)
- `.claude/commands/sc/roadmap.md` — slash command definition
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` — full behavioral protocol
- `.claude/skills/sc-roadmap-protocol/SKILL.md` — dev copy

### Exposed Interfaces
- CLI: `superclaude roadmap run <spec-file> [--agents ...] [--depth quick|standard|deep] [--dry-run] [--resume]`
- Slash command: `/sc:roadmap <spec-file-path>`
- Python API: `execute_roadmap(config: RoadmapConfig, resume, no_validate, auto_accept) -> None`
- Pipeline function: `_build_steps(config) -> list[Step | list[Step]]` (9 sequential/parallel steps)

### Internal Dependencies
- `src/superclaude/cli/pipeline/executor.py` (execute_pipeline)
- `src/superclaude/cli/pipeline/gates.py` (gate_passed)
- `src/superclaude/cli/pipeline/models.py` (Step, StepResult, StepStatus)
- `src/superclaude/cli/pipeline/trailing_gate.py` (TrailingGateRunner)
- `sc-adversarial-protocol` skill (adversarial merge step)

### Extension Points
- Agent specs: `--agents model[:persona]` for variant generation (parallel Steps 2a/2b)
- Depth control: `--depth quick|standard|deep` alters debate rounds
- `--no-validate` flag skips post-pipeline validation subsystem (not spec-fidelity step)
- Resume capability: `_apply_resume()` skips gate-passed steps
- Output directory: configurable via `--output <dir>`

### System Qualities
- **Maintainability**: 9-step pipeline with file-on-disk gates between steps; each step independently verifiable
- **Checkpoint Reliability**: `.roadmap-state.json` persists step state; `--resume` re-enters from last incomplete step
- **Extensibility**: New agent specs injectable via `--agents`; step list is a plain list (addable)
- **Operational Determinism**: YAML frontmatter gates enforce structural requirements per tier; parallel generate steps isolated

---

## Component Group 2: Cleanup-Audit CLI

### File Paths (verified)
- `src/superclaude/cli/cleanup_audit/commands.py` — Click CLI (`cleanup_audit_group`, `run` subcommand)
- `src/superclaude/cli/cleanup_audit/executor.py` — pipeline runner (`execute_cleanup_audit`)
- `src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md` — 3-pass protocol
- `.claude/commands/sc/cleanup-audit.md` — slash command definition
- `.claude/skills/sc-cleanup-audit-protocol/SKILL.md` — dev copy
- `src/superclaude/agents/audit-scanner.md` — Pass 1 Haiku scanner agent
- `src/superclaude/agents/audit-validator.md` — 10% spot-check validator agent
- `src/superclaude/cli/audit/dead_code.py` — dead code candidate detection
- `src/superclaude/cli/audit/dependency_graph.py` — 3-tier dependency graph
- `src/superclaude/cli/audit/tool_orchestrator.py` — static analysis with content-hash caching
- `src/superclaude/cli/audit/classification.py` — two-tier classification engine
- `src/superclaude/cli/audit/profile_generator.py` — 8-field file profiler
- `src/superclaude/cli/audit/scanner_schema.py` — schema validation (Phase 1 + Phase 2)

### Exposed Interfaces
- CLI: `superclaude cleanup-audit run [target] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus ...]`
- Slash command: `/sc:cleanup-audit`
- Audit passes: G-001 to G-006 (surface → structural → cross-cutting → consolidation → validation)
- `classify_finding(file_path, has_references, ...) -> ClassificationResult`
- `detect_dead_code(graph, analyses, entry_points) -> DeadCodeReport`
- `build_dependency_graph(analyses, file_contents) -> DependencyGraph`

### Internal Dependencies
- `src/superclaude/cli/pipeline/executor.py` (shared pipeline executor)
- `src/superclaude/cli/pipeline/gates.py` (gate_passed)
- `src/superclaude/cli/pipeline/models.py`
- `SignalHandler`, `OutputMonitor` (supervisor infrastructure)

### Extension Points
- `--pass` flag selects which audit passes run; `--all` runs full 3-pass pipeline
- `--focus` limits domain scope (infrastructure/frontend/backend/all)
- `--batch-size` controls agent load
- Pluggable analyzer in `ToolOrchestrator.__init__(analyzer=)` — custom static analysis injectable
- Conservative bias: REVIEW fallback prevents false DELETE; threshold configurable

### System Qualities
- **Maintainability**: Read-only audit (no file modification); 6 discrete gate-verified steps
- **Checkpoint Reliability**: Incremental step writes; monitor tracks output bytes
- **Extensibility**: Three audit passes are modular; each can run independently
- **Operational Determinism**: `classify_finding()` is deterministic; same inputs → same tier

---

## Component Group 3: Sprint Executor

### File Paths (verified)
- `src/superclaude/cli/sprint/commands.py` — Click CLI (`sprint_group`, `run`, `attach`, `status`, `logs`, `kill`)
- `src/superclaude/cli/sprint/executor.py` — main orchestration loop (`execute_sprint`, `execute_phase_tasks`)
- `src/superclaude/cli/sprint/process.py` — `ClaudeProcess` (sprint-specific subprocess with prompt builder)
- `src/superclaude/cli/pipeline/executor.py` — generic step sequencer shared with roadmap
- `src/superclaude/cli/pipeline/gates.py` — tier-proportional gate validation
- `src/superclaude/cli/pipeline/models.py` — `Step`, `StepResult`, `StepStatus`, `GateCriteria`
- `src/superclaude/cli/pipeline/trailing_gate.py` — `TrailingGateRunner` (daemon-thread gate eval)
- `src/superclaude/execution/parallel.py` — `ParallelExecutor`, `Task`, dependency graph

### Exposed Interfaces
- CLI: `superclaude sprint run <index-path> [--start N] [--end N] [--max-turns N] [--model ...] [--dry-run] [--no-tmux] [--shadow-gates]`
- `execute_sprint(config: SprintConfig)` — main orchestration entry point
- `execute_phase_tasks(tasks, config, phase, ledger) -> (list[TaskResult], list[str])`
- `gate_passed(output_file: Path, criteria: GateCriteria) -> (bool, str | None)`
- `execute_pipeline(steps, config, run_step, ...) -> list[StepResult]`
- `ParallelExecutor.execute(plan: ExecutionPlan) -> dict[str, Any]`

### Internal Dependencies
- `SprintConfig`, `Phase`, `TurnLedger`, `SprintResult` (config models)
- `SprintLogger`, `SprintTUI`, `OutputMonitor` (observability stack)
- `tmux` integration module (detachable sessions)
- `ClaudeProcess._PipelineClaudeProcess` base (lifecycle hooks)

### Extension Points
- `--start`/`--end` phase range execution
- `--shadow-gates` flag: trailing gates run metrics-only without blocking
- `stall_timeout` + `stall_action` (kill/warn): configurable watchdog
- `_subprocess_factory` parameter on `execute_phase_tasks` for test injection
- `TrailingGatePolicy` injectable on sprint executor (T07.01)

### System Qualities
- **Maintainability**: Phase = file-on-disk; supervisor loop is generic; sprint/roadmap share pipeline code
- **Checkpoint Reliability**: Phase results written to `results/` dir; `--start` allows phase-level re-entry
- **Extensibility**: Generic `execute_pipeline` reusable; step models declarative
- **Operational Determinism**: Gate tiers EXEMPT/LIGHT/STANDARD/STRICT produce deterministic pass/fail

---

## Component Group 4: PM Agent

### File Paths (verified)
- `src/superclaude/pm_agent/__init__.py` — module exports (`ConfidenceChecker`, `SelfCheckProtocol`, `ReflexionPattern`)
- `src/superclaude/pm_agent/confidence.py` — `ConfidenceChecker` (5-check pre-execution assessment)
- `src/superclaude/pm_agent/self_check.py` — `SelfCheckProtocol` (4-question post-implementation validation)
- `src/superclaude/pm_agent/reflexion.py` — `ReflexionPattern` (error learning, dual storage)
- `src/superclaude/pm_agent/token_budget.py` — `TokenBudgetManager` (simple/medium/complex tiers)
- `src/superclaude/pytest_plugin.py` — auto-loaded pytest fixtures and markers
- `.claude/agents/pm-agent.md` — agent definition (session start, post-implementation, mistake detection)
- `src/superclaude/execution/reflection.py` — `ReflectionEngine` (3-stage reflection)
- `src/superclaude/execution/self_correction.py` — `SelfCorrectionEngine` (failure learning + prevention rules)

### Exposed Interfaces
- `ConfidenceChecker.assess(context: dict) -> float` — returns 0.0–1.0 score (≥0.90 proceed, 0.70–0.89 alternatives, <0.70 ask)
- `SelfCheckProtocol.validate(implementation: dict) -> (bool, list[str])` — 4-question validation
- `ReflexionPattern.get_solution(error_info) -> Optional[str]`; `.record_error(error_info)`
- `TokenBudgetManager.allocate(amount) -> bool`; `.remaining -> int`
- pytest fixtures: `confidence_checker`, `self_check_protocol`, `reflexion_pattern`, `token_budget`, `pm_context`
- pytest markers: `@pytest.mark.confidence_check`, `@pytest.mark.self_check`, `@pytest.mark.reflexion`

### Internal Dependencies
- `docs/memory/solutions_learned.jsonl` (reflexion storage)
- `docs/memory/` dir (error pattern persistence)
- Mindbase MCP (semantic search, optional)

### Extension Points
- `ReflexionPattern(memory_dir=)` — configurable storage path
- `TokenBudgetManager(complexity='simple|medium|complex')` — three budget levels
- `SelfCorrectionEngine(repo_path=)` — configurable repo root
- pytest plugin auto-loaded via pyproject.toml `entry-points.pytest11` — no explicit configuration needed

### System Qualities
- **Maintainability**: Three orthogonal patterns (confidence, self-check, reflexion) independently usable
- **Checkpoint Reliability**: Error solutions persisted to JSONL; survive session reset
- **Extensibility**: Placeholder implementations in `_architecture_compliant`, `_root_cause_identified` designed for extension
- **Operational Determinism**: `TokenBudgetManager.LIMITS` are static constants; deterministic budget allocation

---

## Component Group 5: Adversarial Pipeline

### File Paths (verified)
- `.claude/commands/sc/adversarial.md` — slash command definition
- `src/superclaude/commands/adversarial.md` — source command
- `.claude/skills/sc-adversarial-protocol/SKILL.md` — full 5-step protocol (2045+ lines)
- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — source copy
- `.claude/skills/sc-adversarial-protocol/refs/debate-protocol.md` — step-by-step debate spec
- `.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` — hybrid quantitative-qualitative scoring
- `.claude/skills/sc-adversarial-protocol/refs/artifact-templates.md` — 6 artifact output templates

### Exposed Interfaces
- Slash: `/sc:adversarial --compare <files> [--depth quick|standard|deep] [--blind] [--output <dir>]`
- Mode A: `--compare file1,file2[,...,fileN]` (2–10 files)
- Mode B: `--source <file> --generate <type> --agents <spec>[,...]`
- Pipeline Mode: `--pipeline "<shorthand>"` or `--pipeline @pipeline.yaml`
- Scoring: `variant_score = (0.50 × quant_score) + (0.50 × qual_score)` where quant = 5 metrics × weights, qual = 30-criterion binary rubric
- 6 output artifacts: `diff-analysis.md`, `debate-transcript.md`, `base-selection.md`, `refactor-plan.md`, `merge-log.md`, merged output

### Internal Dependencies
- Sequential MCP (structured debate reasoning)
- Context7 MCP (pattern validation)
- Serena MCP (symbol-level analysis)
- Task tool (agent delegation for debate orchestration)

### Extension Points
- `--agents model[:persona[:"instruction"]]` — configurable agent configurations per variant
- `--depth quick|standard|deep` — controls debate rounds (1/2/up to 3)
- `--blind` — strips model identity from comparisons
- `--focus` — restricts comparison to specific dimensions
- Pipeline Mode YAML: full DAG specification for multi-phase pipelines
- Convergence threshold configurable; invariant probe (Round 2.5) gated on `--depth standard|deep`

### System Qualities
- **Maintainability**: 5 sequential steps each producing a named artifact; pipeline resume via manifest
- **Checkpoint Reliability**: Pipeline Mode has manifest-based resume; convergence plateau detection prevents infinite loops
- **Extensibility**: Generic tool invocable by any SuperClaude command; Mode B injectable agents
- **Operational Determinism**: Tiebreaker protocol (3 levels) produces deterministic base selection; CEV protocol prevents hallucinated quality claims

---

## Component Group 6: Task-Unified Tier System

### File Paths (verified)
- `.claude/commands/sc/task-unified.md` — slash command with classification header spec
- `src/superclaude/commands/task-unified.md` — source command
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` — execution protocol
- `.claude/skills/sc-task-unified-protocol/SKILL.md` — dev copy
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` — tier keyword tables + verification routing
- `src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md` — source copy

### Exposed Interfaces
- Slash: `/sc:task [description] --compliance [strict|standard|light|exempt|auto] --strategy [systematic|agile|enterprise|auto] --verify [critical|standard|skip|auto]`
- Classification header (machine-readable): `<!-- SC:TASK-UNIFIED:CLASSIFICATION -->` block with TIER, CONFIDENCE, KEYWORDS, OVERRIDE, RATIONALE
- Tier keyword scoring: STRICT (+STRICT_keywords), EXEMPT (+0.4), LIGHT (+0.3), STANDARD (+0.2); context boosters applied
- Verification routing: STRICT → quality-engineer sub-agent (3–5K tokens); STANDARD → direct test (300–500 tokens); LIGHT/EXEMPT → skip
- Compound phrase overrides (e.g., "quick fix" → LIGHT; "fix security" → STRICT)

### Internal Dependencies
- Sequential MCP (STRICT tier required)
- Serena MCP (STRICT tier required; fallback not allowed)
- `Task` tool (quality-engineer agent spawn for STRICT verification)

### Extension Points
- `--compliance` override: user can force any tier regardless of classification
- `--skip-compliance` escape hatch
- `--force-strict` override
- `--parallel` / `--delegate` flags for sub-agent coordination
- Confidence threshold <0.70 prompts user for override confirmation

### System Qualities
- **Maintainability**: Orthogonal strategy × compliance dimensions; keyword tables in separate `tier-classification.md`
- **Checkpoint Reliability**: Classification header emitted as first output (telemetry-compatible); confidence scoring transparent
- **Extensibility**: Tier keyword tables are editable YAML-like structures; new compound phrases addable
- **Operational Determinism**: Priority ordering STRICT > EXEMPT > LIGHT > STANDARD resolves conflicts deterministically; confidence <0.70 gates require explicit user confirmation

---

## Component Group 7: Quality Agents

### File Paths (verified)
- `.claude/agents/quality-engineer.md` — quality-engineer verification agent
- `src/superclaude/agents/quality-engineer.md` — source copy
- `plugins/superclaude/agents/quality-engineer.md` — plugin copy
- `.claude/agents/audit-validator.md` — audit spot-check validator (10% sample, <20% discrepancy → PASS)
- `src/superclaude/agents/audit-validator.md` — source copy
- `.claude/agents/self-review.md` — post-implementation reflexion partner
- `src/superclaude/agents/self-review.md` — source copy
- `plugins/superclaude/agents/self-review.md` — plugin copy
- `.claude/agents/pm-agent.md` — PM Agent (meta-agent; session start/mistake/monthly maintenance)

### Exposed Interfaces
- `quality-engineer` agent: invoked via `Task` tool for STRICT-tier verification; outputs test strategy, test cases, automated test suites, quality assessment reports
- `audit-validator` agent: receives 10% sample of audit findings; 4-check verification methodology; outputs `validation-report.md` with PASS/FAIL
- `self-review` agent: 4-question checklist (tests executed? edge cases? requirements matched? follow-up?); brief evidence-focused report
- `pm-agent` agent: `./sc:pm` manual invocation; auto-activates on session start, post-implementation, mistake detection

### Internal Dependencies
- Read, Grep, Glob tools (quality-engineer, audit-validator, self-review)
- Serena MCP (pm-agent — session memory)
- `docs/memory/` (pm-agent knowledge base)

### Extension Points
- `maxTurns` configurable per agent definition
- `permissionMode: plan` on audit-validator enforces read-only constraint
- PM Agent trigger conditions extensible in agent definition frontmatter
- `audit-validator` CRITICAL FAIL condition (FALSE NEGATIVE on DELETE) hard-coded as strict safety gate

### System Qualities
- **Maintainability**: Agents are .md files; no compiled code; editable without rebuild
- **Checkpoint Reliability**: Agents write reports to disk; supervisor can re-read; pm-agent persists to Serena memory
- **Extensibility**: New agent roles addable as .md files; `superclaude install` copies to `~/.claude/agents/`
- **Operational Determinism**: `audit-validator` sampling is deterministic (5 findings per 50 files); PASS/FAIL threshold fixed at 20%

---

## Component Group 8: Pipeline Analysis Subsystem

### File Paths (verified)
- `src/superclaude/cli/pipeline/__init__.py` — 42-symbol public API surface
- `src/superclaude/cli/pipeline/executor.py` — generic step sequencer (shared by sprint + roadmap)
- `src/superclaude/cli/pipeline/gates.py` — tier-proportional gate validator
- `src/superclaude/cli/pipeline/models.py` — `PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `SemanticCheck`
- `src/superclaude/cli/pipeline/trailing_gate.py` — `TrailingGateRunner` (daemon-thread)
- `src/superclaude/cli/pipeline/diagnostic_chain.py` — 4-stage diagnostic chain (troubleshoot → adversarial × 2 → summary)
- `src/superclaude/cli/pipeline/guard_analyzer.py` — guard/sentinel detection (if/else, type changes)
- `src/superclaude/cli/pipeline/dataflow_graph.py` — cross-deliverable state variable graph (birth/write/read nodes)
- `src/superclaude/cli/pipeline/combined_m2_pass.py` — combined M2 pass (invariant registry + FMEA sub-passes)
- `src/superclaude/cli/pipeline/fmea_classifier.py` — FMEA failure mode classification
- `src/superclaude/cli/pipeline/fmea_promotion.py` — FMEA promotion to release gate violations
- `src/superclaude/cli/pipeline/guard_pass.py` — guard analysis pipeline pass
- `src/superclaude/cli/pipeline/guard_resolution.py` — guard resolution (AcceptedRisk, ReleaseGateWarning)
- `src/superclaude/cli/pipeline/invariant_pass.py` — invariant registry pass
- `src/superclaude/cli/pipeline/dataflow_pass.py` — data flow tracing pass
- `src/superclaude/cli/pipeline/deliverables.py` — deliverable decomposition
- `src/superclaude/cli/pipeline/conflict_detector.py` — conflict detection
- `src/superclaude/cli/pipeline/conflict_review.py` — conflict review (detect_file_overlap, review_conflicts)
- `src/superclaude/cli/pipeline/contract_extractor.py` — implicit contract extraction
- `src/superclaude/cli/audit/dependency_graph.py` — 3-tier dependency graph (Tier-A: AST, Tier-B: grep, Tier-C: inference)
- `src/superclaude/cli/audit/tool_orchestrator.py` — static analysis orchestration + content-hash caching
- `src/superclaude/cli/audit/dead_code.py` — dead code candidate detection

### Exposed Interfaces
- `execute_pipeline(steps, config, run_step, ...) -> list[StepResult]` — generic pipeline executor
- `gate_passed(output_file, criteria) -> (bool, str | None)` — tier-proportional validation
- `run_combined_m2_pass(deliverables, ...) -> CombinedM2Output` — invariant + FMEA analysis
- `run_guard_analysis_pass(deliverables) -> GuardAnalysisOutput`
- `run_dataflow_tracing_pass(...) -> DataFlowTracingOutput`
- `build_dataflow_graph(nodes, edges) -> DataFlowGraph` — directed write→read graph
- `detect_dead_code(graph, analyses, entry_points) -> DeadCodeReport`
- `build_dependency_graph(analyses, file_contents) -> DependencyGraph`
- `run_diagnostic_chain(...)  -> DiagnosticReport` — 4-stage failure diagnostic

### Internal Dependencies
- `PipelineConfig`, `GateCriteria`, `Step` models (models.py)
- `TrailingGateRunner` (shadow mode)
- Sprint executor and Roadmap executor as consumers (NFR-007: no reverse imports)

### Extension Points
- `run_step` callable injected by sprint/roadmap — executor is consumer-agnostic
- `cancel_check` callback for graceful cancellation
- `trailing_runner` injectable for shadow gate mode
- Semantic checks in `GateCriteria.semantic_checks` — custom content validators addable
- FMEA promotion threshold `Severity` configurable
- `@no-ambiguity-check` annotation suppresses guard ambiguity detection (R-009)

### System Qualities
- **Maintainability**: NFR-007 enforces no cross-imports between pipeline and sprint/roadmap; 42-symbol clean API surface
- **Checkpoint Reliability**: Diagnostic chain degrades gracefully (stage errors isolated); partial results available
- **Extensibility**: Pluggable run_step and cancel_check make executor reusable across pipeline types
- **Operational Determinism**: `gate_passed()` is pure Python (no subprocess, no LLM); same input → same result; DFS cycle detection on dataflow graph

---

## OQ-008 Annotation

No components triggered the OQ-008 degraded-coverage annotation. All 8 groups returned non-empty Auggie MCP results. Fallback chain (Serena + Grep/Glob) was not activated.

## Coverage Verification

| Component Group | File:Line Evidence | Interfaces Non-Empty | Deps Non-Empty | Extension Points Non-Empty |
|---|---|---|---|---|
| 1. Roadmap Pipeline | `src/superclaude/cli/roadmap/executor.py:302` | ✅ | ✅ | ✅ |
| 2. Cleanup-Audit CLI | `src/superclaude/cli/cleanup_audit/commands.py:18` | ✅ | ✅ | ✅ |
| 3. Sprint Executor | `src/superclaude/cli/sprint/executor.py:490` | ✅ | ✅ | ✅ |
| 4. PM Agent | `src/superclaude/pm_agent/confidence.py:26` | ✅ | ✅ | ✅ |
| 5. Adversarial Pipeline | `.claude/skills/sc-adversarial-protocol/refs/debate-protocol.md:1` | ✅ | ✅ | ✅ |
| 6. Task-Unified Tier System | `.claude/commands/sc/task-unified.md:1` | ✅ | ✅ | ✅ |
| 7. Quality Agents | `.claude/agents/quality-engineer.md:1` | ✅ | ✅ | ✅ |
| 8. Pipeline Analysis Subsystem | `src/superclaude/cli/pipeline/__init__.py:1` | ✅ | ✅ | ✅ |
