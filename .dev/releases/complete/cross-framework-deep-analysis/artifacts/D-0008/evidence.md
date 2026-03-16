---
deliverable: D-0008
artifact: evidence
title: IC Component Inventory — Auggie MCP Evidence Citations
generated: 2026-03-14
---

# D-0008 Evidence: Auggie MCP Query Results

## Query Log

All queries executed via `mcp__auggie-mcp__codebase-retrieval` against `/config/workspace/IronClaude`.
No fallback activated (OQ-008 criteria not triggered).

| Query # | Topic | Result Status |
|---|---|---|
| 1 | Roadmap pipeline | Non-empty — returned 6+ file excerpts |
| 2 | PM Agent | Non-empty — returned 8+ file excerpts |
| 3 | Cleanup-audit CLI | Non-empty — returned 6+ file excerpts |
| 4 | Sprint executor | Non-empty — returned 7+ file excerpts |
| 5 | Adversarial pipeline | Non-empty — returned 8+ file excerpts |
| 6 | Task-unified tier system | Non-empty — returned 6+ file excerpts |
| 7 | Quality agents | Non-empty — returned 8+ file excerpts |
| 8 | Pipeline analysis subsystem | Non-empty — returned 10+ file excerpts |
| 9 | Parallel execution engine | Non-empty — returned 5+ file excerpts |

## File:Line Evidence Per Component Group

### Group 1: Roadmap Pipeline

- `src/superclaude/cli/roadmap/commands.py:14` — `@click.group("roadmap")` entry point
- `src/superclaude/cli/roadmap/executor.py:302` — `_build_steps()` 9-step pipeline builder
- `src/superclaude/cli/roadmap/executor.py:822` — `execute_roadmap()` main entry point
- `src/superclaude/skills/sc-roadmap-protocol/SKILL.md:1` — behavioral protocol header
- `.claude/commands/sc/roadmap.md:1` — slash command definition

### Group 2: Cleanup-Audit CLI

- `src/superclaude/cli/cleanup_audit/commands.py:18` — `@click.group("cleanup-audit")` entry point
- `src/superclaude/cli/cleanup_audit/commands.py:24` — `@cleanup_audit_group.command("run")` subcommand
- `src/superclaude/cli/cleanup_audit/executor.py:54` — `execute_cleanup_audit()` main runner
- `src/superclaude/cli/audit/dead_code.py:108` — `detect_dead_code()` function
- `src/superclaude/cli/audit/dependency_graph.py:198` — `build_dependency_graph()` function
- `src/superclaude/cli/audit/tool_orchestrator.py:1` — `ToolOrchestrator` + `FileAnalysis` classes
- `src/superclaude/cli/audit/classification.py:110` — `classify_finding()` deterministic classifier
- `src/superclaude/agents/audit-scanner.md:1` — Haiku scanner agent definition

### Group 3: Sprint Executor

- `src/superclaude/cli/sprint/commands.py:15` — `@click.group("sprint")` entry point
- `src/superclaude/cli/sprint/executor.py:490` — `execute_sprint()` main orchestration loop
- `src/superclaude/cli/sprint/executor.py:349` — `execute_phase_tasks()` per-task loop
- `src/superclaude/cli/sprint/process.py:88` — `ClaudeProcess` sprint-specific subprocess class
- `src/superclaude/cli/pipeline/executor.py:46` — `execute_pipeline()` generic sequencer
- `src/superclaude/cli/pipeline/gates.py:20` — `gate_passed()` pure Python gate validator
- `src/superclaude/cli/pipeline/trailing_gate.py:88` — `TrailingGateRunner` daemon-thread evaluator
- `src/superclaude/execution/parallel.py:80` — `ParallelExecutor` (Wave→Checkpoint→Wave)

### Group 4: PM Agent

- `src/superclaude/pm_agent/confidence.py:26` — `ConfidenceChecker` class
- `src/superclaude/pm_agent/confidence.py:42` — `assess()` method with 5 weighted checks
- `src/superclaude/pm_agent/self_check.py:19` — `SelfCheckProtocol` class
- `src/superclaude/pm_agent/self_check.py:64` — `validate()` method with 4-question check
- `src/superclaude/pm_agent/reflexion.py:32` — `ReflexionPattern` class
- `src/superclaude/pm_agent/token_budget.py:17` — `TokenBudgetManager` with LIMITS dict
- `src/superclaude/pytest_plugin.py:1` — auto-loaded pytest plugin entry point
- `.claude/agents/pm-agent.md:1` — PM Agent definition

### Group 5: Adversarial Pipeline

- `.claude/commands/sc/adversarial.md:1` — slash command (Mode A/B/Pipeline)
- `.claude/skills/sc-adversarial-protocol/refs/debate-protocol.md:1` — 5-step protocol spec
- `.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md:13` — hybrid scoring formula
- `.claude/skills/sc-adversarial-protocol/refs/artifact-templates.md:1` — 6 artifact templates
- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md:18` — core objective statement
- `src/superclaude/skills/sc-adversarial-protocol/SKILL.md:2045` — status determination and integration patterns

### Group 6: Task-Unified Tier System

- `.claude/commands/sc/task-unified.md:1` — command definition with classification spec
- `.claude/commands/sc/task-unified.md:55` — classification header format
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md:7` — execution-only entry note
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md:1` — priority order (STRICT > EXEMPT > LIGHT > STANDARD)
- `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md:75` — verification routing table
- `src/superclaude/commands/task-unified.md:86` — `<0.70` confidence prompt rule

### Group 7: Quality Agents

- `.claude/agents/quality-engineer.md:1` — quality-engineer agent definition
- `.claude/agents/audit-validator.md:1` — audit-validator agent definition
- `src/superclaude/agents/audit-validator.md:24` — 10% sampling rate spec
- `src/superclaude/agents/audit-validator.md:33` — 4-check verification methodology
- `.claude/agents/self-review.md:1` — self-review agent (4 mandatory questions)
- `.claude/agents/pm-agent.md:9` — PM Agent trigger conditions
- `src/superclaude/agents/README.md:1` — agents directory README (sync protocol)

### Group 8: Pipeline Analysis Subsystem

- `src/superclaude/cli/pipeline/__init__.py:3` — 42-symbol public API surface
- `src/superclaude/cli/pipeline/executor.py:46` — `execute_pipeline()` generic step sequencer
- `src/superclaude/cli/pipeline/gates.py:20` — `gate_passed()` with tier-proportional logic
- `src/superclaude/cli/pipeline/diagnostic_chain.py:1` — 4-stage diagnostic chain
- `src/superclaude/cli/pipeline/guard_analyzer.py:1` — guard/sentinel detection
- `src/superclaude/cli/pipeline/dataflow_graph.py:1` — cross-deliverable data flow graph
- `src/superclaude/cli/pipeline/combined_m2_pass.py:65` — `run_combined_m2_pass()` (invariant + FMEA)
- `src/superclaude/cli/audit/dependency_graph.py:196` — 3-tier dependency graph builder
- `src/superclaude/cli/audit/tool_orchestrator.py:146` — `ToolOrchestrator` with content-hash cache

## Reproducibility

All queries executed within the same session. Auggie MCP returned consistent non-empty results across all 9 queries. The same query topics return the same primary file paths within this session.

## OQ-008 Check

| Criterion | Threshold | Result |
|---|---|---|
| Timeout | Any single query timeout | 0 timeouts |
| Consecutive failures | ≥3 consecutive empty results | 0 failures |
| Coverage confidence | <50% of groups with non-empty results | 100% (9/9) |

**Conclusion**: OQ-008 fallback NOT triggered. All results are Auggie-primary (not fallback-derived).
