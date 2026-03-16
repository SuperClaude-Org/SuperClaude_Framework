# TASKLIST INDEX -- CLI Portify Pipeline

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | CLI Portify Pipeline |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-15 |
| TASKLIST_ROOT | .dev/releases/current/v2.25-cli-portify-cli/ |
| Total Phases | 11 |
| Total Tasks | 73 |
| Total Deliverables | 93 |
| Complexity Class | HIGH |
| Primary Persona | backend |
| Consulting Personas | architect, analyzer, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/v2.25-cli-portify-cli/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-4-tasklist.md |
| Phase 5 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-5-tasklist.md |
| Phase 6 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-6-tasklist.md |
| Phase 7 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-7-tasklist.md |
| Phase 8 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-8-tasklist.md |
| Phase 9 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-9-tasklist.md |
| Phase 10 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-10-tasklist.md |
| Phase 11 Tasklist | .dev/releases/current/v2.25-cli-portify-cli/phase-11-tasklist.md |
| Execution Log | .dev/releases/current/v2.25-cli-portify-cli/execution-log.md |
| Checkpoint Reports | .dev/releases/current/v2.25-cli-portify-cli/checkpoints/ |
| Evidence Directory | .dev/releases/current/v2.25-cli-portify-cli/evidence/ |
| Artifacts Directory | .dev/releases/current/v2.25-cli-portify-cli/artifacts/ |
| Validation Reports | .dev/releases/current/v2.25-cli-portify-cli/validation/ |
| Feedback Log | .dev/releases/current/v2.25-cli-portify-cli/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Architecture Confirmation | T01.01-T01.04 | STRICT: 2, STANDARD: 1, EXEMPT: 1 |
| 2 | phase-2-tasklist.md | Prerequisites and Config | T02.01-T02.07 | STRICT: 4, STANDARD: 3 |
| 3 | phase-3-tasklist.md | Core Pipeline and Executor | T03.01-T03.12 | STRICT: 9, STANDARD: 3 |
| 4 | phase-4-tasklist.md | Gate System | T04.01-T04.03 | STRICT: 3 |
| 5 | phase-5-tasklist.md | Analysis Pipeline | T05.01-T05.06 | STRICT: 4, STANDARD: 2 |
| 6 | phase-6-tasklist.md | Specification Pipeline | T06.01-T06.07 | STRICT: 5, STANDARD: 2 |
| 7 | phase-7-tasklist.md | Release Spec Synthesis | T07.01-T07.06 | STRICT: 4, STANDARD: 2 |
| 8 | phase-8-tasklist.md | Panel Review Convergence | T08.01-T08.06 | STRICT: 5, STANDARD: 1 |
| 9 | phase-9-tasklist.md | Observability Completion | T09.01-T09.04 | STRICT: 2, STANDARD: 2 |
| 10 | phase-10-tasklist.md | CLI Integration | T10.01-T10.05 | STRICT: 3, STANDARD: 2 |
| 11 | phase-11-tasklist.md | Verification and Release | T11.01-T11.07 | STRICT: 4, STANDARD: 2, LIGHT: 1 |

## Source Snapshot

- Enterprise-grade CLI pipeline converting inference-based SuperClaude skill workflows into deterministic CLI runners
- 12-step sequentially-gated pipeline with gate enforcement, convergence-loop panel review, and resume/checkpoint support
- 65 requirements (47 functional, 18 non-functional) across 8 technical domains; complexity score 0.92
- Primary delivery: `src/superclaude/cli/cli_portify/` registered in `src/superclaude/cli/main.py`
- 3 super-milestones: A (Foundations, Phases 0-3), B (Pipeline Generation, Phases 4-6), C (Quality Loop, Phases 7-10)
- Critical path: Framework base types (D-008) stable before domain models; `claude` CLI binary (D-001) is hard runtime dependency

## Deterministic Rules Applied

- Phase renumbering: Roadmap Phases 0-10 renumbered to output Phases 1-11 (no gaps per Section 4.3)
- Task ID scheme: `T<PP>.<TT>` zero-padded 2-digit format (Section 4.5)
- Checkpoint cadence: every 5 tasks within a phase + mandatory end-of-phase checkpoint (Section 4.8)
- Clarification tasks: inserted when info missing or tier confidence < 0.70 (Section 4.6)
- Deliverable registry: `D-####` IDs in global appearance order with artifact path placeholders (Section 5.1)
- Effort mapping: deterministic keyword scoring → XS/S/M/L/XL (Section 5.2.1)
- Risk mapping: deterministic keyword scoring → Low/Medium/High (Section 5.2.2)
- Tier classification: compound phrase check → keyword scoring → context boosters → priority resolution (Section 5.3)
- Verification routing: STRICT→sub-agent, STANDARD→direct test, LIGHT→sanity check, EXEMPT→skip (Section 4.10)
- MCP requirements: tier-based tool dependency declaration (Section 5.5)
- Traceability matrix: R-### → T<PP>.<TT> → D-#### with tier and confidence (Section 5.7)
- Multi-file output: tasklist-index.md + 11 phase-N-tasklist.md files (Section 3.3)

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | 1 | Validate target architecture against existing SuperClaude CLI framework |
| R-002 | 1 | Confirm imports and stable locations for: PipelineConfig, Step, StepResult, GateCriteria, GateMode, SemanticCheck |
| R-003 | 1 | Assess all 14 open questions; resolve at minimum the 5 contract-affecting blocking OQs |
| R-004 | 1 | Assess OQ-002 and OQ-013 as potential additional blockers |
| R-005 | 1 | Confirm prompt splitting threshold location (executor vs. prompt builder) |
| R-006 | 1 | Confirm overwrite rules for generated modules using Generated by / Portified from markers |
| R-007 | 1 | Confirm OQ-007 and OQ-014 are non-blocking and document |
| R-008 | 1 | Architecture decision notes deliverable |
| R-009 | 1 | Finalized interface assumptions with import verification deliverable |
| R-010 | 1 | Open question resolution list deliverable |
| R-011 | 1 | Updated implementation checklist deliverable |
| R-012 | 2 | Implement workflow path resolution under src/superclaude/skills/; require SKILL.md; raise AMBIGUOUS_PATH or INVALID_PATH |
| R-013 | 2 | Implement CLI name derivation: strip sc- prefix and -protocol suffix, normalize to kebab-case |
| R-014 | 2 | Implement collision detection: scan src/superclaude/cli/, allow overwrite only for previously portified modules |
| R-015 | 2 | Validate output destination: parent exists and is writable |
| R-016 | 2 | Create workdir at .dev/portify-workdir/<cli_name>/ |
| R-017 | 2 | Emit portify-config.yaml with resolved paths |
| R-018 | 2 | Implement component discovery and inventory: scan SKILL.md, command files, refs, rules, templates, scripts |
| R-019 | 2 | Emit component-inventory.yaml with path, lines, purpose, type per component |
| R-020 | 2 | Enforce timeouts: 30s for input-validation, 60s for component-discovery |
| R-021 | 2 | config.py deliverable |
| R-022 | 2 | inventory.py deliverable |
| R-023 | 2 | models.py foundations including all 5 error code definitions |
| R-024 | 2 | portify-config.yaml deliverable |
| R-025 | 2 | component-inventory.yaml deliverable |
| R-026 | 3 | Implement core domain models: PortifyPhaseType, ConvergenceState, PortifyConfig, PortifyStep, PortifyStepResult, PortifyOutcome, PortifyStatus, MonitorState, TurnLedger |
| R-027 | 3 | Implement __init__.py with Generated by / Portified from marker |
| R-028 | 3 | Implement step registration in mandated module generation order |
| R-029 | 3 | Implement executor: sequential execution only, --dry-run, --resume, signal handling |
| R-030 | 3 | Add unit test: assert dry-run execution filters steps to PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION |
| R-031 | 3 | Implement claude binary detection via shutil.which |
| R-032 | 3 | Implement timeout classification: exit code 124 → TIMEOUT, other non-zero → ERROR |
| R-033 | 3 | Implement _determine_status() classification based on exit code + EXIT_RECOMMENDATION + artifact presence |
| R-034 | 3 | Implement retry mechanism with retry_limit=1 for Claude-assisted steps |
| R-035 | 3 | Implement TurnLedger: can_launch() check, budget exhaustion → HALTED outcome |
| R-036 | 3 | Implement signal handlers: SIGINT/SIGTERM → complete current step → set INTERRUPTED outcome |
| R-037 | 3 | Implement mandatory return-contract.yaml emission on all outcomes |
| R-038 | 3 | Implement resume_command() with exact CLI command |
| R-039 | 3 | Implement suggested_resume_budget calculation: remaining * 25 |
| R-040 | 3 | Implement OutputMonitor tracking: output bytes, growth rate, stall seconds, events, line count |
| R-041 | 3 | Implement execution-log.jsonl and execution-log.md skeleton |
| R-042 | 3 | Implement stall detection with kill action via OutputMonitor.growth_rate_bps |
| R-043 | 3 | Implement basic PortifyTUI start/stop lifecycle |
| R-044 | 3 | models.py deliverable |
| R-045 | 3 | process.py deliverable |
| R-046 | 3 | executor.py deliverable (includes resume logic and return-contract emission) |
| R-047 | 3 | monitor.py baseline deliverable |
| R-048 | 3 | logging_.py skeleton and tui.py lifecycle deliverables |
| R-049 | 4 | Implement all 12 gates (G-000 through G-011) with frontmatter field checks, minimum line counts, tier assignment |
| R-050 | 4 | Implement semantic check functions returning tuple[bool, str] |
| R-051 | 4 | Implement gate diagnostics formatting |
| R-052 | 4 | Per-gate check mapping table (G-000 through G-011) |
| R-053 | 4 | gates.py deliverable with all 12 gate implementations and per-gate semantic checks |
| R-054 | 4 | Semantic check helpers deliverable |
| R-055 | 5 | Implement protocol-mapping prompt builder and execution; generate protocol-map.md with required YAML frontmatter |
| R-056 | 5 | Enforce EXIT_RECOMMENDATION marker for protocol-mapping |
| R-057 | 5 | Implement analysis-synthesis prompt builder and execution; generate portify-analysis-report.md with required sections |
| R-058 | 5 | Enforce EXIT_RECOMMENDATION marker for analysis-synthesis |
| R-059 | 5 | Enforce 600s timeout for both steps |
| R-060 | 5 | Implement user-review-p1 review gate: write phase1-approval.yaml with status: pending |
| R-061 | 5 | Implement --resume logic: require status: approved in approval YAML with YAML parse + schema validation |
| R-062 | 5 | prompts.py with Phase 1 prompt builders deliverable |
| R-063 | 5 | Analysis step functions deliverable |
| R-064 | 5 | Review-gate logic with YAML parse validation deliverable |
| R-065 | 5 | protocol-map.md deliverable |
| R-066 | 5 | portify-analysis-report.md deliverable |
| R-067 | 5 | phase1-approval.yaml deliverable |
| R-068 | 6 | Implement step-graph-design prompt builder → step-graph-spec.md |
| R-069 | 6 | Implement models-gates-design prompt builder → models-gates-spec.md |
| R-070 | 6 | Implement prompts-executor-design prompt builder → prompts-executor-spec.md |
| R-071 | 6 | Implement pipeline-spec-assembly: programmatic pre-assembly + Claude synthesis → portify-spec.md |
| R-072 | 6 | Enforce EXIT_RECOMMENDATION markers on all Phase 2 Claude steps |
| R-073 | 6 | Enforce 600s timeout per step |
| R-074 | 6 | Implement user-review-p2 validation: status: completed, all blocking gates passed, step_mapping has entries |
| R-075 | 6 | Implement phase2-approval.yaml resume enforcement with YAML parse + schema validation |
| R-076 | 6 | Phase 2 prompt builders in prompts.py deliverable |
| R-077 | 6 | Spec assembly logic deliverable |
| R-078 | 6 | portify-spec.md deliverable |
| R-079 | 6 | Second review pause/resume flow deliverable |
| R-080 | 6 | phase2-approval.yaml deliverable |
| R-081 | 6 | step-graph-spec.md, models-gates-spec.md, prompts-executor-spec.md deliverables |
| R-082 | 7 | Load template from src/superclaude/examples/release-spec-template.md |
| R-083 | 7 | Create working copy |
| R-084 | 7 | Implement 4-substep synthesis: working copy, populate 13 template sections, 3-persona brainstorm, incorporate findings |
| R-085 | 7 | Validate zero SC_PLACEHOLDER sentinels |
| R-086 | 7 | Validate Section 12 exists |
| R-087 | 7 | Emit portify-release-spec.md with frontmatter title, status, quality_scores |
| R-088 | 7 | Implement --file argument passing for templates exceeding 50KB |
| R-089 | 7 | Enforce 900s timeout |
| R-090 | 7 | Release synthesis logic deliverable |
| R-091 | 7 | Placeholder detection deliverable |
| R-092 | 7 | Brainstorm finding model deliverable |
| R-093 | 7 | portify-release-spec.md deliverable |
| R-094 | 8 | Implement convergence state machine: NOT_STARTED → REVIEWING → INCORPORATING → SCORING → CONVERGED or ESCALATED |
| R-095 | 8 | Implement per-iteration logic: 4-expert focus pass, finding incorporation with severity routing, full panel critique |
| R-096 | 8 | Implement CONVERGED condition: zero unaddressed CRITICALs → status: success |
| R-097 | 8 | Implement ESCALATED condition: 3 iterations exhausted → status: partial |
| R-098 | 8 | Set downstream_ready = true only when overall >= 7.0 |
| R-099 | 8 | Emit updated portify-release-spec.md and panel-report.md on both CONVERGED and ESCALATED |
| R-100 | 8 | Use internal convergence loop, NOT outer retry mechanism |
| R-101 | 8 | Enforce 1200s timeout |
| R-102 | 8 | review.py deliverable |
| R-103 | 8 | Convergence state machine deliverable |
| R-104 | 8 | panel-report.md deliverable |
| R-105 | 9 | Complete PortifyTUI lifecycle: full real-time progress display via rich |
| R-106 | 9 | Complete OutputMonitor integration: convergence iteration, findings count, placeholder count tracking |
| R-107 | 9 | Implement failure diagnostics collection: gate failure reason, exit code, missing artifacts, resume guidance |
| R-108 | 9 | Finalize execution-log.jsonl and execution-log.md with complete event coverage |
| R-109 | 9 | tui.py complete deliverable |
| R-110 | 9 | monitor.py complete deliverable |
| R-111 | 9 | diagnostics.py deliverable |
| R-112 | 9 | logging_.py complete deliverable |
| R-113 | 10 | Implement Click command group with run subcommand |
| R-114 | 10 | Wire options: --name, --output, --max-turns, --model, --dry-run, --resume, --debug |
| R-115 | 10 | Implement --dry-run: limit to PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION phase types |
| R-116 | 10 | Register in src/superclaude/cli/main.py via main.add_command |
| R-117 | 10 | Implement prompt splitting: if aggregate prompt length exceeds 300 lines, split to portify-prompts.md |
| R-118 | 10 | Verify module generation order enforced |
| R-119 | 10 | commands.py deliverable |
| R-120 | 10 | __init__.py deliverable |
| R-121 | 10 | main.py integration deliverable |
| R-122 | 11 | Unit tests: all 5 validation error paths, all 12 gates, _determine_status(), TurnLedger, exit code mapping |
| R-123 | 11 | Integration tests: dry-run against real skill directory; resume flow; signal handling; gate failure + retry |
| R-124 | 11 | Edge case tests: ambiguous skill name, name collision, budget exhaustion, convergence ESCALATED, template >50KB |
| R-125 | 11 | Run project validation using uv run pytest |
| R-126 | 11 | Validate all 14 success criteria (SC-001 through SC-014) |
| R-127 | 11 | Perform sample runs on: valid workflow, ambiguous workflow, insufficient budget, interrupted, escalation |
| R-128 | 11 | Confirm logs and workdir behavior are acceptable |
| R-129 | 11 | Test coverage for all critical paths deliverable |
| R-130 | 11 | Validation report against SC-001 through SC-014 deliverable |
| R-131 | 11 | Release readiness checklist deliverable |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001, R-002 | Architecture validation notes | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0001/notes.md | M | Medium |
| D-0002 | T01.02 | R-003, R-004 | Open question resolution list | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0002/spec.md | M | Medium |
| D-0003 | T01.03 | R-005, R-006, R-007 | Design decision confirmations | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0003/notes.md | S | Low |
| D-0004 | T01.04 | R-008, R-009, R-010, R-011 | Architecture baseline package | EXEMPT | Skip verification | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0004/spec.md | S | Low |
| D-0005 | T02.01 | R-012 | Workflow path resolution in config.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0005/spec.md | M | Medium |
| D-0006 | T02.02 | R-013 | CLI name derivation logic | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0006/spec.md | S | Low |
| D-0007 | T02.03 | R-014, R-015 | Collision detection and output validation | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0007/spec.md | M | Medium |
| D-0008 | T02.04 | R-016, R-017 | Workdir creation and portify-config.yaml emission | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0008/spec.md | S | Low |
| D-0009 | T02.05 | R-018, R-019 | Component discovery and inventory.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0009/spec.md | M | Medium |
| D-0010 | T02.06 | R-020 | Timeout enforcement for Steps 0-1 | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0010/evidence.md | S | Low |
| D-0011 | T02.07 | R-023 | models.py error code foundations | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0011/spec.md | M | Medium |
| D-0012 | T03.01 | R-026 | Core domain models in models.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0012/spec.md | L | Medium |
| D-0013 | T03.02 | R-027 | __init__.py with generation markers | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0013/evidence.md | XS | Low |
| D-0014 | T03.03 | R-028 | Step registration in mandated order | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0014/evidence.md | S | Low |
| D-0015 | T03.04 | R-029, R-030 | Executor with sequential execution, dry-run, resume, signal handling | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0015/spec.md | XL | High |
| D-0016 | T03.05 | R-031 | Claude binary detection via shutil.which | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0016/evidence.md | S | Medium |
| D-0017 | T03.06 | R-032, R-033 | Timeout classification and _determine_status() | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0017/spec.md | M | Medium |
| D-0018 | T03.07 | R-034 | Retry mechanism with retry_limit=1 | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0018/spec.md | M | Medium |
| D-0019 | T03.08 | R-035 | TurnLedger with can_launch() and budget exhaustion | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0019/spec.md | M | Medium |
| D-0020 | T03.09 | R-036 | Signal handlers for SIGINT/SIGTERM | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0020/spec.md | M | High |
| D-0021 | T03.10 | R-037, R-038, R-039 | Return contract emission and resume command | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0021/spec.md | M | Medium |
| D-0022 | T03.11 | R-040, R-041, R-042 | OutputMonitor baseline and stall detection | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0022/spec.md | M | Medium |
| D-0023 | T03.12 | R-043 | Basic PortifyTUI start/stop lifecycle | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0023/evidence.md | S | Low |
| D-0024 | T04.01 | R-049, R-052 | All 12 gates (G-000 through G-011) in gates.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0024/spec.md | XL | High |
| D-0025 | T04.02 | R-050 | Semantic check functions returning tuple[bool, str] | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0025/spec.md | M | Medium |
| D-0026 | T04.03 | R-051 | Gate diagnostics formatting | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0026/spec.md | S | Low |
| D-0027 | T05.01 | R-055, R-056 | Protocol-mapping prompt builder and EXIT_RECOMMENDATION enforcement | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0027/spec.md | M | Medium |
| D-0028 | T05.02 | R-057, R-058 | Analysis-synthesis prompt builder and EXIT_RECOMMENDATION enforcement | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0028/spec.md | M | Medium |
| D-0029 | T05.03 | R-059 | 600s timeout enforcement for analysis steps | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0029/evidence.md | S | Low |
| D-0030 | T05.04 | R-060 | User-review-p1 gate writing phase1-approval.yaml | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0030/spec.md | M | Medium |
| D-0031 | T05.05 | R-061 | Resume logic requiring status: approved with YAML parse validation | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0031/spec.md | M | Medium |
| D-0032 | T05.06 | R-062, R-063, R-064 | prompts.py Phase 1 builders, analysis step functions, review-gate logic | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0032/spec.md | M | Low |
| D-0033 | T06.01 | R-068 | Step-graph-design prompt builder → step-graph-spec.md | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0033/spec.md | M | Medium |
| D-0034 | T06.02 | R-069 | Models-gates-design prompt builder → models-gates-spec.md | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0034/spec.md | M | Medium |
| D-0035 | T06.03 | R-070 | Prompts-executor-design prompt builder → prompts-executor-spec.md | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0035/spec.md | M | Medium |
| D-0036 | T06.04 | R-071 | Pipeline-spec-assembly: pre-assembly + Claude synthesis → portify-spec.md | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0036/spec.md | L | Medium |
| D-0037 | T06.05 | R-072, R-073 | EXIT_RECOMMENDATION markers and 600s timeout for Phase 2 steps | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0037/evidence.md | S | Low |
| D-0038 | T06.06 | R-074, R-075 | User-review-p2 validation and phase2-approval.yaml resume enforcement | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0038/spec.md | M | Medium |
| D-0039 | T06.07 | R-076, R-077, R-078, R-079, R-080, R-081 | Phase 2 prompt builders, spec assembly, review flow, deliverable artifacts | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0039/spec.md | M | Low |
| D-0040 | T07.01 | R-082, R-083 | Template loading and working copy creation | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0040/evidence.md | S | Low |
| D-0041 | T07.02 | R-084 | 4-substep synthesis: populate sections, brainstorm pass, incorporate findings | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0041/spec.md | XL | High |
| D-0042 | T07.03 | R-085, R-086 | Placeholder validation (zero SC_PLACEHOLDER) and Section 12 existence check | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0042/spec.md | M | Medium |
| D-0043 | T07.04 | R-087 | portify-release-spec.md emission with frontmatter | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0043/spec.md | S | Low |
| D-0044 | T07.05 | R-088 | --file argument passing for templates exceeding 50KB | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0044/spec.md | M | Medium |
| D-0045 | T07.06 | R-089 | 900s timeout enforcement for synthesis step | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0045/evidence.md | S | Low |
| D-0046 | T08.01 | R-094 | Convergence state machine in review.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0046/spec.md | L | High |
| D-0047 | T08.02 | R-095 | Per-iteration panel review logic: 4-expert focus, incorporation, critique, scoring | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0047/spec.md | XL | High |
| D-0048 | T08.03 | R-096, R-097 | CONVERGED and ESCALATED terminal conditions | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0048/spec.md | M | Medium |
| D-0049 | T08.04 | R-098 | downstream_ready gated on overall >= 7.0 | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0049/spec.md | S | Medium |
| D-0050 | T08.05 | R-099, R-100 | Panel report emission on both terminal conditions; internal loop enforcement | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0050/spec.md | M | Medium |
| D-0051 | T08.06 | R-101 | 1200s timeout enforcement for convergence step | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0051/evidence.md | S | Low |
| D-0052 | T09.01 | R-105 | Complete PortifyTUI lifecycle with rich real-time display | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0052/spec.md | M | Low |
| D-0053 | T09.02 | R-106 | Complete OutputMonitor integration with convergence tracking | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0053/spec.md | M | Low |
| D-0054 | T09.03 | R-107 | Failure diagnostics collection in diagnostics.py | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0054/spec.md | M | Medium |
| D-0055 | T09.04 | R-108 | Finalized execution-log.jsonl and execution-log.md | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0055/spec.md | S | Low |
| D-0056 | T10.01 | R-113 | Click command group with run subcommand in commands.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0056/spec.md | M | Low |
| D-0057 | T10.02 | R-114 | CLI options wiring: --name, --output, --max-turns, --model, --dry-run, --resume, --debug | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0057/spec.md | S | Low |
| D-0058 | T10.03 | R-115 | --dry-run phase type filtering (PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0058/spec.md | M | Medium |
| D-0059 | T10.04 | R-116 | Registration in src/superclaude/cli/main.py via main.add_command | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0059/spec.md | S | Low |
| D-0060 | T10.05 | R-117, R-118 | Prompt splitting for >300 lines and module generation order verification | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0060/spec.md | M | Low |
| D-0061 | T11.01 | R-122 | Unit tests for validation errors, gates, status classification, TurnLedger, exit codes | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0061/spec.md | XL | Medium |
| D-0062 | T11.02 | R-123 | Integration tests for dry-run, resume, signal handling, gate failure + retry | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0062/spec.md | XL | High |
| D-0063 | T11.03 | R-124 | Edge case tests for ambiguous skill, collision, budget exhaustion, ESCALATED, >50KB template | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0063/spec.md | L | High |
| D-0064 | T11.04 | R-125 | Project validation via uv run pytest | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0064/evidence.md | S | Low |
| D-0065 | T11.05 | R-126 | SC-001 through SC-014 validation report | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0065/spec.md | L | Medium |
| D-0066 | T11.06 | R-127 | Sample run results across 5 scenarios | STANDARD | Direct test execution | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0066/evidence.md | M | Medium |
| D-0067 | T11.07 | R-128, R-129, R-130, R-131 | Release readiness checklist and final validation artifacts | LIGHT | Quick sanity check | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0067/spec.md | S | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001, R-002 | T01.01 | D-0001 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0001/ |
| R-003, R-004 | T01.02 | D-0002 | STRICT | 82% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0002/ |
| R-005, R-006, R-007 | T01.03 | D-0003 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0003/ |
| R-008, R-009, R-010, R-011 | T01.04 | D-0004 | EXEMPT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0004/ |
| R-012 | T02.01 | D-0005 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0005/ |
| R-013 | T02.02 | D-0006 | STRICT | 82% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0006/ |
| R-014, R-015 | T02.03 | D-0007 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0007/ |
| R-016, R-017 | T02.04 | D-0008 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0008/ |
| R-018, R-019 | T02.05 | D-0009 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0009/ |
| R-020 | T02.06 | D-0010 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0010/ |
| R-023 | T02.07 | D-0011 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0011/ |
| R-026 | T03.01 | D-0012 | STRICT | 90% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0012/ |
| R-027 | T03.02 | D-0013 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0013/ |
| R-028 | T03.03 | D-0014 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0014/ |
| R-029, R-030 | T03.04 | D-0015 | STRICT | 92% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0015/ |
| R-031 | T03.05 | D-0016 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0016/ |
| R-032, R-033 | T03.06 | D-0017 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0017/ |
| R-034 | T03.07 | D-0018 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0018/ |
| R-035 | T03.08 | D-0019 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0019/ |
| R-036 | T03.09 | D-0020 | STRICT | 90% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0020/ |
| R-037, R-038, R-039 | T03.10 | D-0021 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0021/ |
| R-040, R-041, R-042 | T03.11 | D-0022 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0022/ |
| R-043 | T03.12 | D-0023 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0023/ |
| R-049, R-052 | T04.01 | D-0024 | STRICT | 92% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0024/ |
| R-050 | T04.02 | D-0025 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0025/ |
| R-051 | T04.03 | D-0026 | STRICT | 82% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0026/ |
| R-055, R-056 | T05.01 | D-0027 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0027/ |
| R-057, R-058 | T05.02 | D-0028 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0028/ |
| R-059 | T05.03 | D-0029 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0029/ |
| R-060 | T05.04 | D-0030 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0030/ |
| R-061 | T05.05 | D-0031 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0031/ |
| R-062, R-063, R-064 | T05.06 | D-0032 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0032/ |
| R-068 | T06.01 | D-0033 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0033/ |
| R-069 | T06.02 | D-0034 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0034/ |
| R-070 | T06.03 | D-0035 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0035/ |
| R-071 | T06.04 | D-0036 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0036/ |
| R-072, R-073 | T06.05 | D-0037 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0037/ |
| R-074, R-075 | T06.06 | D-0038 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0038/ |
| R-076, R-077, R-078, R-079, R-080, R-081 | T06.07 | D-0039 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0039/ |
| R-082, R-083 | T07.01 | D-0040 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0040/ |
| R-084 | T07.02 | D-0041 | STRICT | 90% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0041/ |
| R-085, R-086 | T07.03 | D-0042 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0042/ |
| R-087 | T07.04 | D-0043 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0043/ |
| R-088 | T07.05 | D-0044 | STRICT | 82% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0044/ |
| R-089 | T07.06 | D-0045 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0045/ |
| R-094 | T08.01 | D-0046 | STRICT | 92% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0046/ |
| R-095 | T08.02 | D-0047 | STRICT | 90% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0047/ |
| R-096, R-097 | T08.03 | D-0048 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0048/ |
| R-098 | T08.04 | D-0049 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0049/ |
| R-099, R-100 | T08.05 | D-0050 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0050/ |
| R-101 | T08.06 | D-0051 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0051/ |
| R-105 | T09.01 | D-0052 | STRICT | 82% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0052/ |
| R-106 | T09.02 | D-0053 | STRICT | 82% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0053/ |
| R-107 | T09.03 | D-0054 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0054/ |
| R-108 | T09.04 | D-0055 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0055/ |
| R-113 | T10.01 | D-0056 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0056/ |
| R-114 | T10.02 | D-0057 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0057/ |
| R-115 | T10.03 | D-0058 | STRICT | 85% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0058/ |
| R-116 | T10.04 | D-0059 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0059/ |
| R-117, R-118 | T10.05 | D-0060 | STANDARD | 78% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0060/ |
| R-122 | T11.01 | D-0061 | STRICT | 90% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0061/ |
| R-123 | T11.02 | D-0062 | STRICT | 90% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0062/ |
| R-124 | T11.03 | D-0063 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0063/ |
| R-125 | T11.04 | D-0064 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0064/ |
| R-126 | T11.05 | D-0065 | STRICT | 88% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0065/ |
| R-127 | T11.06 | D-0066 | STANDARD | 80% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0066/ |
| R-128, R-129, R-130, R-131 | T11.07 | D-0067 | LIGHT | 75% | .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0067/ |

## Execution Log Template

**Intended Path:** .dev/releases/current/v2.25-cli-portify-cli/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

**Template:**

# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/<deterministic-name>.md

**Scope:** <tasks covered>

## Status

Overall: Pass | Fail | TBD

## Verification Results

- (exactly 3 bullets aligned to checkpoint Verification bullets)

## Exit Criteria Assessment

- (exactly 3 bullets aligned to checkpoint Exit Criteria bullets)

## Issues & Follow-ups

- List blocking issues; reference T<PP>.<TT> and D-####

## Evidence

- Bullet list of intended evidence paths under .dev/releases/current/v2.25-cli-portify-cli/evidence/

## Feedback Collection Template

**Intended Path:** .dev/releases/current/v2.25-cli-portify-cli/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

## Generation Notes

- Roadmap Phases 0-10 renumbered to output Phases 1-11 (no gaps)
- TASKLIST_ROOT derived via fallback rule (no version token or .dev/releases/current/ path found in roadmap)
- No glossary emitted (roadmap does not explicitly define terms)
- T03.04 (executor) classified as XL effort and split into subtasks per Section 4.4 (executor + dry-run unit test combined due to explicit roadmap coupling)
- T04.01 (12 gates) classified as XL; gate implementations G-000 through G-005 and G-006 through G-011 can be parallelized per roadmap note
- T07.02 (4-substep synthesis) classified as XL per roadmap complexity
- T08.02 (per-iteration panel logic) classified as XL per roadmap complexity
