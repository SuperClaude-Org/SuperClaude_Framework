---
deliverable: D-0010
task: T02.03
title: component-map.md — IC-to-LW Cross-Framework Mappings
status: complete
ic_components: 8
lw_components_mapped: 14
mapping_rows: 12
ic_only_components: 0
generated: 2026-03-14
---

# D-0010: Component Map — IronClaude to llm-workflows

## Overview

This document maps the 8 IronClaude (IC) component groups (from D-0008) to their counterparts in the llm-workflows (LW) repository (from D-0009 verified paths). Mapping types:

- **Direct**: IC and LW components serve the same function and have structural parallels
- **Functional analog**: IC and LW components address the same problem with different architectures
- **Partial**: IC component overlaps with LW component in some but not all aspects
- **No counterpart**: IC component has no LW equivalent (IC-only)

All LW path references use only `path_verified=true` entries from D-0009.

---

## Cross-Framework Mapping Table

| # | IC Component | IC Files (key) | LW Counterpart(s) | LW Files (key, verified) | Mapping Type | Notes |
|---|---|---|---|---|---|---|
| 1 | **Roadmap Pipeline** | `src/superclaude/cli/roadmap/executor.py`, `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | Pipeline orchestration + Task builder | `.claude/commands/rf/pipeline.md`, `.claude/commands/rf/taskbuilder.md` | Functional analog | IC uses 9-step file-on-disk pipeline with gate verification; LW uses event-driven agent team (researcher→builder→executor) per track. Both orchestrate multi-step LLM workflows with artifact hand-offs. |
| 2 | **Cleanup-Audit CLI** | `src/superclaude/cli/cleanup_audit/executor.py`, `src/superclaude/cli/audit/dead_code.py`, `src/superclaude/cli/audit/classification.py` | Automated QA workflow + Failure debugging | `.gfdoc/scripts/automated_qa_workflow.sh`, `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` | Partial | IC focuses on static analysis / dead-code detection with classification; LW workflow focuses on Worker/QA validation loops. Both produce audit findings with evidence. IC has no equivalent of LW's automated failure debugging classification. |
| 3 | **Sprint Executor** | `src/superclaude/cli/sprint/executor.py`, `src/superclaude/cli/sprint/process.py`, `src/superclaude/cli/pipeline/executor.py` | Automated QA workflow | `.gfdoc/scripts/automated_qa_workflow.sh` | Direct | Both are the primary supervised execution engine for LLM-driven task batches. IC uses Python subprocess orchestration with per-phase gates; LW uses bash-scripted Worker/QA loops with PABLOV artifact handoffs. Closest structural parallel in both frameworks. |
| 4 | **PM Agent** | `src/superclaude/pm_agent/confidence.py`, `src/superclaude/pm_agent/reflexion.py`, `src/superclaude/pm_agent/self_check.py` | Anti-hallucination rules + PABLOV method | `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md`, `.gfdoc/rules/core/ib_agent_core.md` | Functional analog | IC's PM Agent provides pre-execution confidence checking, post-implementation self-check, and error reflexion. LW provides presumption-of-falsehood rules and PABLOV artifact-based validation. Both address agent reliability; IC operates at Claude-session level, LW operates at Rigorflow pipeline level. |
| 5 | **Adversarial Pipeline** | `.claude/skills/sc-adversarial-protocol/SKILL.md`, `.claude/skills/sc-adversarial-protocol/refs/scoring-protocol.md` | Anti-sycophancy system | `.gfdoc/rules/core/anti_sycophancy.md`, `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` | Functional analog | IC's adversarial pipeline runs structured debate between LLM variants with scoring; LW's anti-sycophancy system runs inline risk-pattern detection with tier-escalation. Both fight sycophancy and bias but at different operational layers. |
| 6 | **Task-Unified Tier System** | `.claude/commands/sc/task-unified.md`, `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` | Quality gates + Task builder | `.gfdoc/rules/core/quality_gates.md`, `.claude/commands/rf/taskbuilder.md` | Functional analog | IC classifies tasks by compliance tier (STRICT/STANDARD/LIGHT/EXEMPT) and routes verification; LW uses quality gate categories (Sev 1/2/3) for output validation. IC operates at task-dispatch level; LW operates at output-validation level. Both encode "how much rigor is proportionate." |
| 7 | **Quality Agents** | `.claude/agents/quality-engineer.md`, `.claude/agents/audit-validator.md`, `.claude/agents/pm-agent.md` | Agent definitions (rf-*) | `.claude/agents/rf-team-lead.md`, `.claude/agents/rf-task-builder.md`, `.claude/agents/rf-task-executor.md`, `.claude/agents/rf-task-researcher.md` | Direct | Both frameworks define specialized sub-agents with explicit roles. IC: quality-engineer (STRICT verification), audit-validator (10% spot-check), pm-agent (meta-orchestrator). LW: team-lead (orchestrator), researcher, builder, executor. Both use `.claude/agents/` and `.md` definitions. |
| 8 | **Pipeline Analysis Subsystem** | `src/superclaude/cli/pipeline/__init__.py`, `src/superclaude/cli/pipeline/gates.py`, `src/superclaude/cli/pipeline/combined_m2_pass.py`, `src/superclaude/cli/pipeline/diagnostic_chain.py` | Critical flaw analysis + Post-milestone review | `.dev/taskplanning/backlog/FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md`, `.dev/taskplanning/POST_MILESTONE_REVIEW_PROTOCOL.md` | Partial | IC's pipeline analysis subsystem provides programmatic gate validation, FMEA classification, dataflow analysis, and diagnostic chains. LW documents critical flaws and retrospective review protocols. IC has deeper programmatic analysis; LW's equivalent is primarily documentation-driven retrospective. |

### Additional Mappings (Supporting)

| # | IC Component | IC Files (key) | LW Counterpart(s) | LW Files (key, verified) | Mapping Type | Notes |
|---|---|---|---|---|---|---|
| 9 | **Sprint Executor** (session) | `src/superclaude/cli/sprint/process.py` (ClaudeProcess) | Session management | `.gfdoc/scripts/session_message_counter.sh`, `.gfdoc/scripts/rollover_context_functions.sh` | Functional analog | IC manages Claude subprocess lifecycle (start/resume/kill). LW manages JSONL-based session message counting and proactive context rollover. Both handle Claude session lifecycle; LW's rollover mechanism addresses a problem IC does not explicitly solve. |
| 10 | **Sprint Executor** (input) | `src/superclaude/cli/sprint/commands.py` (Click CLI arg parsing) | Input validation | `.gfdoc/scripts/input_validation.sh` | Partial | IC uses Click's built-in argument parsing; LW has an explicit 3-layer defense-in-depth validation library for task name security. IC has no equivalent of LW's path-traversal prevention. |
| 11 | **PM Agent** (reflexion) | `src/superclaude/pm_agent/reflexion.py`, `src/superclaude/execution/self_correction.py` | Post-milestone review | `.dev/taskplanning/POST_MILESTONE_REVIEW_PROTOCOL.md` | Functional analog | IC's ReflexionPattern stores error solutions for cross-session learning. LW's post-milestone review is a structured 7-stage retrospective for forward propagation. Both capture learnings; IC is automatic/lightweight, LW is structured/comprehensive. |
| 12 | **Roadmap Pipeline** (gates) | `src/superclaude/cli/pipeline/gates.py` (gate_passed) | PABLOV method (artifact validation) | `.gfdoc/rules/core/ib_agent_core.md` (PABLOV artifacts) | Functional analog | IC uses `gate_passed()` pure-Python function with tier-proportional criteria. LW uses PABLOV artifact chain (taskspec → expected_set → worker_handoff → qa_report → programmatic_handoff). Both are evidence-based completion verification; architecturally different (Python function vs. artifact file chain). |

---

## IC-Only Components

**None.** All 8 IC component groups have at least one functional analog or direct counterpart in llm-workflows. This is notable — it indicates the two frameworks evolved solutions to the same underlying problems independently.

---

## Mapping Summary

| Mapping Type | Count | IC Components |
|---|---|---|
| Direct | 2 | Sprint Executor (vs. automated_qa_workflow), Quality Agents (vs. rf-* agents) |
| Functional analog | 6 | Roadmap Pipeline, PM Agent, Adversarial Pipeline, Task-Unified Tier System, Sprint Executor (session mgmt), Roadmap Pipeline (gates) |
| Partial | 4 | Cleanup-Audit CLI, Pipeline Analysis Subsystem, Sprint Executor (input), PM Agent (reflexion) |
| No counterpart (IC-only) | 0 | — |

**Total primary mapping rows: 12 (≥8 required per acceptance criteria)**

---

## Verification

- IC component groups covered: 8/8 ✅
- LW `path_verified=true` paths referenced only: Yes ✅ (all LW paths sourced from D-0009 `path_verified=true` entries)
- IC-only annotation section present: Yes ✅ (0 IC-only components)
- Mapping rows ≥ 8: Yes ✅ (12 rows)
- `strategy_analyzable=degraded` entries excluded from analysis: Yes ✅ (path 5a excluded; path 5b used for anti-sycophancy)
