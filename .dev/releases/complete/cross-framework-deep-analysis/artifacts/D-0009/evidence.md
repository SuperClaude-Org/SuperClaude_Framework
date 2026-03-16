---
deliverable: D-0009
artifact: evidence
title: LW Path Verification — Auggie MCP Evidence Citations
generated: 2026-03-14
---

# D-0009 Evidence: Auggie MCP Query Results

## Query Log

All queries executed via `mcp__auggie-mcp__codebase-retrieval` against `/config/workspace/llm-workflows` within this session. No fallback activated.

| Query # | Topic | Result Status | Primary Path Confirmed |
|---|---|---|---|
| 1 | PABLOV method / ib_agent_core.md | Non-empty — PABLOV content returned | `.gfdoc/rules/core/ib_agent_core.md` |
| 2 | Automated QA workflow script | Non-empty — bash script content returned | `.gfdoc/scripts/automated_qa_workflow.sh` |
| 3 | Quality gates | Non-empty — full spec document returned | `.gfdoc/rules/core/quality_gates.md` |
| 4 | Anti-hallucination rules | Non-empty — full rules document returned | `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` |
| 5 | Anti-sycophancy system | Non-empty — core file + RISK_PATTERNS returned | `.gfdoc/rules/core/anti_sycophancy.md`, `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` |
| 6 | DNSP protocol / batch state flow | Non-empty — guide returned with full DNSP sections | `.gfdoc/docs/guides/RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md` |
| 7 | Session management scripts | Non-empty — both scripts returned | `.gfdoc/scripts/session_message_counter.sh`, `.gfdoc/scripts/rollover_context_functions.sh` |
| 8 | Input validation script | Non-empty — 287-line script returned | `.gfdoc/scripts/input_validation.sh` |
| 9 | Task builder command | Non-empty — command definition returned | `.claude/commands/rf/taskbuilder.md` |
| 10 | Pipeline orchestration command | Non-empty — full pipeline spec returned | `.claude/commands/rf/pipeline.md` |
| 11 | Agent definitions (rf-*.md) | Non-empty — all 4 agents returned | `.claude/agents/rf-*.md` |
| 12 | Failure debugging system | Non-empty — v2 document returned | `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md` |
| 13 | Critical flaw analysis | Non-empty — full analysis returned | `.dev/taskplanning/backlog/FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md` |
| 14 | Post-milestone review protocol | Non-empty — 7-stage protocol returned | `.dev/taskplanning/POST_MILESTONE_REVIEW_PROTOCOL.md` |

## File:Line Evidence Per Path

### Path 1: `.gfdoc/rules/core/ib_agent_core.md`
- `ib_agent_core.md:71` — "You are working with the **Rigorflow** orchestration pipeline, implementing the **PABLOV Method** (Programmatic Artifact-Based LLM Output Validation)"
- `ib_agent_core.md:99` — Core Tenets: "Artifacts > vibes", "Audit by default, trust nothing", "DNSP Protocol", "Agent Contracts are sacred"
- `ib_agent_core.md:106` — PABLOV Artifacts: taskspec, expected_set, worker_handoff, qa_report, programmatic_handoff

### Path 2: `.gfdoc/scripts/automated_qa_workflow.sh`
- `automated_qa_workflow.sh:1605` — Worker completion verification loop
- `automated_qa_workflow.sh:2151` — Batch UID multiset validation (jq-based fail-closed guards)
- `automated_qa_workflow.sh:4254` — Proactive session rollover threshold checks (MAX_MESSAGES_PER_SESSION, MAX_TOKENS_PER_SESSION)
- `automated_qa_workflow.sh:4758` — QA report PASS/FAIL verdict parsing and QA_REQUIRE_STDOUT policy

### Path 3: `.gfdoc/rules/core/quality_gates.md`
- `quality_gates.md:1` — YAML frontmatter: `title: Automated Quality Gates for Task Outputs`, `version: 1.1.0`
- `quality_gates.md:57` — "Universal Quality Gate Principles" (6 principles including Anti-Sycophancy v5.2)
- `quality_gates.md:158` — Error Severity Levels table (Sev 1/2/3)

### Path 4: `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md`
- `anti_hallucination_task_completion_rules.md:1` — YAML frontmatter: `id: anti-hallucination-standards`, `version: 1.0.0`
- `anti_hallucination_task_completion_rules.md:59` — "1. The Presumption of Falsehood — Every claim begins with a status of 'Incorrect.'"
- `anti_hallucination_task_completion_rules.md:67` — "2. Evidence is Non-Negotiable"
- `anti_hallucination_task_completion_rules.md:76` — "3. Penalty for Forgery - ZERO TOLERANCE — FAS score of -100"

### Path 5a: `.gfdoc/rules/core/anti_sycophancy.md` [strategy_analyzable=degraded]
- File exists (Auggie returned content); however content matches anti_hallucination file title and structure
- OQ-008 degradation annotation: **content-duplication** — Auggie evidence shows file content is identical to `anti_hallucination_task_completion_rules.md`; primary strategy analysis source for 12-pattern scoring must be path 5b
- `anti_sycophancy.md:91` — Guide confirms file is referenced for anti-sycophancy system architecture
- **Phase 3/4 strategy extraction**: Must use `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md` as authoritative source for risk scoring patterns

### Path 5b: `.dev/taskplanning/v5.2/RISK_PATTERNS_COMPREHENSIVE.md`
- `RISK_PATTERNS_COMPREHENSIVE.md:1` — Version 5.2, "Complete pattern library for detecting sycophancy-prone queries"
- `RISK_PATTERNS_COMPREHENSIVE.md:11` — "Pattern Categories" — all 12 categories documented
- `RISK_PATTERNS_COMPREHENSIVE.md:323` — Risk scoring weight table (Comparative Bias 0.3, Confirmation Seeking 0.4, etc.)
- `RISK_PATTERNS_COMPREHENSIVE.md:334` — "Multiple Pattern Bonus: Risk score × 1.3 when multiple patterns detected"

### Path 6: `.gfdoc/docs/guides/RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md`
- `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1` — YAML frontmatter: `version: "5.2"`, `id: rigorflow-batch-state-flow-guide`
- `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:179` — Batch States table (initialized/worker_in_progress/worker_complete/qa_in_progress/qa_complete)
- `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1149` — "Worker Handoff Missing: DNSP Recovery Paths" — Path 1 (Active DNSP) and Path 2 (Recovery)
- `RIGORFLOW_BATCH_STATE_FLOW_GUIDE.md:1165` — DNSP 4-step sequence: Detect (backoff) → Nudge (bounded) → Synthesize → Proceed

### Path 7a: `.gfdoc/scripts/session_message_counter.sh`
- `session_message_counter.sh:1` — `#!/bin/bash` — Centralized session JSONL message counter
- `session_message_counter.sh:114` — `check_session_needs_rollover()` — dual threshold check (max_messages 375, max_tokens 175000)
- `session_message_counter.sh:103` — Python-based token estimation (CHARS_PER_TOKEN = 2.8)

### Path 7b: `.gfdoc/scripts/rollover_context_functions.sh`
- `rollover_context_functions.sh:1` — `#!/bin/bash` — Context rollover utilities
- `rollover_context_functions.sh:38` — `generate_rollover_context()` — batch-aware context summary generator
- `rollover_context_functions.sh:194` — `check_and_handle_rollover()` — threshold-triggered rollover with context injection
- `rollover_context_functions.sh:224` — `roll_to_new_session_with_context()` — new session creation with injected context

### Path 8: `.gfdoc/scripts/input_validation.sh`
- `input_validation.sh:1` — "3-layer defense-in-depth validation for task names"
- `input_validation.sh:61` — `validate_task_name()` — Layer 1: regex, length 3–100, forbidden patterns `../`, `..\\`, `..`, null bytes, `//`
- `input_validation.sh:133` — `is_path_safe()` — Layer 2: realpath workspace boundary check (`.gfdoc/tasks` or `.dev/tasks`)
- `input_validation.sh:244` — `sanitize_task_name()` — Layer 3: space→hyphen, invalid char removal, double-slash collapse

### Path 9: `.claude/commands/rf/taskbuilder.md`
- `taskbuilder.md:15` — "# /rf:taskbuilder_v2 - MDTM Task Builder (Self-Contained Items)"
- `taskbuilder.md:180` — "SELF-CONTAINED CHECKLIST ITEMS (CRITICAL - SESSION ROLLOVER PROTECTION)"
- `taskbuilder.md:200` — "Self-Contained Checklist Item Pattern" — 6-element mandatory structure
- `taskbuilder.md:315` — Pre-write validation checklist (7 checks including self-contained and integrated verification)

### Path 10: `.claude/commands/rf/pipeline.md`
- `pipeline.md:1` — "# Rigorflow Pipeline - Agent Team Orchestration"
- `pipeline.md:48` — Multi-Track diagram: N parallel researcher→builder→executor chains
- `pipeline.md:67` — "Event-driven per-track (EXPERIMENTAL): Each track progresses independently"
- `pipeline.md:804` — Message protocol table (RESEARCH_READY, TASK_READY, EXECUTION_COMPLETE)

### Path 11: Agent Definitions (`.claude/agents/rf-*.md`)
- `rf-team-lead.md:1` — `name: rf-team-lead`, model: opus, orchestrates team + template selection
- `rf-task-builder.md:1` — `name: rf-task-builder`, creates MDTM task files
- `rf-task-executor.md:1` — `name: rf-task-executor`, runs `automated_qa_workflow.sh`
- `rf-task-researcher.md:1` — `name: rf-task-researcher`, codebase context gathering
- `.claude/agents/README.md:29` — Agent Team Members table confirming all 4 agents

### Path 12: `.dev/taskplanning/backlog/05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md`
- `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:32` — Key Benefits: 50% debugging time reduction, 90%+ success rate
- `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:155` — Trigger points: QA FAIL after 3rd retry, batch retry limit, critical violation, manual invocation
- `05_AUTOMATED_QA_FAILURE_DEBUGGING_SYSTEM_v2.md:784` — Pattern scoring with 4 categories (execution_score, template_score, evidence_score, workflow_score)

### Path 13: `.dev/taskplanning/backlog/FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md`
- `FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md:1` — "Severity: CRITICAL - Causes infinite loop in automated QA workflow"
- `FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md:13` — Root cause: bash fallback parser → null section_type → filter failure → infinite loop
- `FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md:311` — Multi-Layered Failure Chain (5 layers: creation, parsing, batch assignment, execution, QA)
- `FRAMEWORK_CRITICAL_FLAW_ANALYSIS.md:339` — "The Critical Missing Layer: [Taskbuilder] → [Write Task File] → [VALIDATE] → [Run Workflow or REJECT]"

### Path 14: `.dev/taskplanning/POST_MILESTONE_REVIEW_PROTOCOL.md`
- `POST_MILESTONE_REVIEW_PROTOCOL.md:1` — Version 1.0, 7-stage continuous improvement loop
- `POST_MILESTONE_REVIEW_PROTOCOL.md:22` — Stage 1: Completion Checkpoint (4 conditions: tasks done, QA passed, deliverables verified, success criteria met)
- `POST_MILESTONE_REVIEW_PROTOCOL.md:34` — Stage 2: Reflection & Analysis using `/sc:reflect`
- `POST_MILESTONE_REVIEW_PROTOCOL.md:276` — Stage 6: Forward Propagation to next milestone (prevents recurring issues)

## Reproducibility

All 14 Auggie MCP queries returned non-empty results within this session. The same component topics return the same primary file paths within this session. No OQ-008 timeout or consecutive failure threshold was triggered.

## OQ-001 Resolution (LW Path Staleness)

Per T02.02 instructions, stale paths are annotated and excluded from Phase 4 strategy extraction. Result: **0 stale paths**. All 16 path entries are `path_verified=true`. One entry (path 5a) is flagged `strategy_analyzable=degraded` due to content duplication; Phase 4 must use path 5b as the authoritative anti-sycophancy strategy source.
