# TASKLIST INDEX -- CLI Portify v2 Refactoring

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | CLI Portify v2 Refactoring |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-08 |
| TASKLIST_ROOT | .dev/releases/current/v2.18-cli-portify-v2/ |
| Total Phases | 5 |
| Total Tasks | 40 |
| Total Deliverables | 52 |
| Complexity Class | HIGH |
| Primary Persona | backend |
| Consulting Personas | architect, analyzer, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/v2.18-cli-portify-v2/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/v2.18-cli-portify-v2/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/v2.18-cli-portify-v2/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/v2.18-cli-portify-v2/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/v2.18-cli-portify-v2/phase-4-tasklist.md |
| Phase 5 Tasklist | .dev/releases/current/v2.18-cli-portify-v2/phase-5-tasklist.md |
| Execution Log | .dev/releases/current/v2.18-cli-portify-v2/execution-log.md |
| Checkpoint Reports | .dev/releases/current/v2.18-cli-portify-v2/checkpoints/ |
| Evidence Directory | .dev/releases/current/v2.18-cli-portify-v2/evidence/ |
| Artifacts Directory | .dev/releases/current/v2.18-cli-portify-v2/artifacts/ |
| Feedback Log | .dev/releases/current/v2.18-cli-portify-v2/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation and Prerequisite Remediation | T01.01-T01.10 | STRICT: 4, STANDARD: 3, LIGHT: 1, EXEMPT: 2 |
| 2 | phase-2-tasklist.md | Contract Infrastructure and Analysis | T02.01-T02.10 | STRICT: 6, STANDARD: 2, EXEMPT: 2 |
| 3 | phase-3-tasklist.md | Protocol Design | T03.01-T03.05 | STRICT: 3, STANDARD: 1, EXEMPT: 1 |
| 4 | phase-4-tasklist.md | Code Generation and Integration | T04.01-T04.08 | STRICT: 4, STANDARD: 2, EXEMPT: 2 |
| 5 | phase-5-tasklist.md | Validation Testing and Cleanup | T05.01-T05.07 | STRICT: 3, STANDARD: 2, EXEMPT: 2 |

## Source Snapshot

- Spec source: refactoring-spec-cli-portify.md (complexity score 0.92, adversarial reviewed)
- Scope: 70 requirements (52 functional, 18 non-functional) across 7 domains
- Architecture: Command/protocol split with contract-driven phase boundaries
- Critical path: Ref remediation → Split → Contracts → Phase 0-1 → Phase 2 design → CodeGen → Golden fixtures
- 5 phases, 20 milestones, 14-19 estimated working sessions
- 10 open questions (6 blocking) requiring resolution before Phase 2

## Deterministic Rules Applied

- Phase numbering: Sequential by appearance (1-5), no gaps, matching roadmap structure
- Task IDs: Zero-padded T<PP>.<TT> format (e.g., T01.03)
- Checkpoint cadence: Every 5 tasks within phase plus mandatory end-of-phase checkpoint
- Clarification tasks: Inserted immediately before blocked task when tier confidence < 0.70
- Deliverable registry: Global D-#### IDs assigned in task appearance order
- Effort mapping: Deterministic 5-level scoring (XS/S/M/L/XL) from keyword presence
- Risk mapping: Deterministic 3-level scoring (Low/Medium/High) from keyword categories
- Tier classification: /sc:task-unified algorithm with compound phrase overrides, keyword scoring, context boosters
- Verification routing: Tier-proportional (STRICT=sub-agent, STANDARD=direct test, LIGHT=sanity, EXEMPT=skip)
- MCP requirements: Tier-proportional mandatory/preferred/fallback tool declarations
- Traceability matrix: R-### → T<PP>.<TT> → D-#### → artifact paths with tier and confidence
- Multi-file output: tasklist-index.md + 5 phase files for Sprint CLI compatibility
- XL splitting: T04.01 decomposed into 4 subtasks per structural check #16

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Context | This roadmap delivers the refactoring of sc-cli-portify from a monolithic skill into a command/protocol split |
| R-002 | Phase 1 | Phase 1: Foundation and Prerequisite Remediation |
| R-003 | Phase 1 | Milestone 1.1: Ref File API Alignment |
| R-004 | Phase 1 | Read live models.py and gates.py to capture current API signatures |
| R-005 | Phase 1 | Update refs/pipeline-spec.md: Fix tier casing, align GateCriteria field names, correct SemanticCheck contract |
| R-006 | Phase 1 | Update refs/code-templates.md: Align all import paths to superclaude.cli.pipeline.models / .gates |
| R-007 | Phase 1 | Validation: Diff ref files against live API — zero field name mismatches. Add stale-ref detector |
| R-008 | Phase 1 | Milestone 1.2: Command/Protocol Split |
| R-009 | Phase 1 | Create src/superclaude/skills/sc-cli-portify-protocol/ directory structure |
| R-010 | Phase 1 | Create src/superclaude/commands/cli-portify.md (thin command shim) with argument parsing and validation |
| R-011 | Phase 1 | Promote YAML frontmatter in SKILL.md: name, description, category, complexity, allowed-tools, mcp-servers |
| R-012 | Phase 1 | Ensure make verify-sync covers sc-cli-portify-protocol/ directory |
| R-013 | Phase 1 | Deprecate sc-cli-portify/ — mark for removal in Phase 5 after all validation passes |
| R-014 | Phase 1 | Milestone 1.3: Open Question Resolution |
| R-015 | Phase 1 | Resolve OQ-001 through OQ-010 before proceeding to Phase 2 |
| R-016 | Phase 1 | Phase 1 Exit Criteria |
| R-017 | Phase 2 | Phase 2: Protocol Core — Contract Infrastructure, Phase 0, and Phase 1 |
| R-018 | Phase 2 | Milestone 2.1: Contract Infrastructure and Schema Versioning |
| R-019 | Phase 2 | Define contract schema versioning policy with backward-compatibility rules |
| R-020 | Phase 2 | Define YAML contract common header schema (schema_version, phase, status, timestamp, resume_checkpoint) |
| R-021 | Phase 2 | Define per-phase contract schemas (portify-prerequisites.yaml through portify-integration.yaml and return contract) |
| R-022 | Phase 2 | Implement contract validation logic — next phase reads and validates incoming contract |
| R-023 | Phase 2 | Implement return contract structure (FR-043): status, failure_phase, generated_files, resume_command |
| R-024 | Phase 2 | Implement resume protocol (FR-052): read latest contract, validate completed phases, resume from failure |
| R-025 | Phase 2 | Validate resume semantics with a synthetic failure scenario |
| R-026 | Phase 2 | Define null-field policy: unreached fields explicitly set to null |
| R-027 | Phase 2 | Milestone 2.2: Phase 0 — Prerequisites |
| R-028 | Phase 2 | Workflow path resolution from --workflow argument (FR-010) |
| R-029 | Phase 2 | Live API snapshot (FR-011): read models.py and gates.py, extract signatures, store as api-snapshot.yaml |
| R-030 | Phase 2 | Output directory collision check (FR-012): check portify-summary.md marker, apply collision policy |
| R-031 | Phase 2 | Early unsupported-pattern scan (FR-013): detect recursive agent self-orchestration, interactive decisions |
| R-032 | Phase 2 | Emit portify-prerequisites.yaml contract (FR-014) |
| R-033 | Phase 2 | Milestone 2.3: Phase 1 — Workflow Analysis |
| R-034 | Phase 2 | Build component inventory with stable component_id (C-NNN) (FR-015) |
| R-035 | Phase 2 | Step decomposition with stable source_id (S-NNN) and conservation invariant (FR-016, FR-049) |
| R-036 | Phase 2 | Step classification: pure_programmatic / claude_assisted / hybrid with confidence scoring (FR-017) |
| R-037 | Phase 2 | Dependency DAG with acyclicity validation (FR-018) |
| R-038 | Phase 2 | Gate tier assignment (EXEMPT/LIGHT/STANDARD/STRICT) and mode (BLOCKING/TRAILING) (FR-019) |
| R-039 | Phase 2 | Trailing gate safety escalation (FR-020) |
| R-040 | Phase 2 | Divergence detection for ambiguous step boundaries (FR-050) |
| R-041 | Phase 2 | 7 self-validation checks (6 blocking, 1 advisory) (FR-021) |
| R-042 | Phase 2 | Emit portify-analysis.md (< 400 lines) and portify-analysis.yaml (FR-022) |
| R-043 | Phase 2 | User review gate — present analysis, allow classification overrides (FR-023) |
| R-044 | Phase 2 | Milestone 2.4: TodoWrite Integration |
| R-045 | Phase 2 | Define 23 subphase tasks across 5 phases (FR-051) |
| R-046 | Phase 2 | Implement checkpoint triggers: after phase completion, user review gates, before write operations |
| R-047 | Phase 2 | Wire TodoWrite updates into Phase 0 and Phase 1 execution flow |
| R-048 | Phase 2 | Phase 2 Exit Criteria |
| R-049 | Phase 3 | Phase 3: Protocol Core — Phase 2 Implementation (Design) |
| R-050 | Phase 3 | Milestone 3.1: Step Graph Design |
| R-051 | Phase 3 | Source-to-generated step mapping with 1:1, 1:N, N:1, 1:0 recording and justification (FR-024) |
| R-052 | Phase 3 | Coverage invariant enforcement: source_step_registry == mapped_steps + elimination_records (FR-025) |
| R-053 | Phase 3 | Elimination records with source_id, reason, approved_by fields |
| R-054 | Phase 3 | Milestone 3.2: Model and Gate Design |
| R-055 | Phase 3 | Domain-specific dataclass models extending PipelineConfig and StepResult (FR-026) |
| R-056 | Phase 3 | Gate design using live GateCriteria fields (FR-028) |
| R-057 | Phase 3 | API conformance verification against Phase 0 snapshot hash (RISK-001 mitigation) |
| R-058 | Phase 3 | Milestone 3.3: Prompt and Executor Design |
| R-059 | Phase 3 | Prompt design for Claude-assisted steps (FR-027) |
| R-060 | Phase 3 | Pure-programmatic step implementation as full Python code (FR-029) |
| R-061 | Phase 3 | Executor design: sprint-style synchronous supervisor with ThreadPoolExecutor (FR-030) |
| R-062 | Phase 3 | Pattern coverage matrix — verify all required patterns covered (FR-031) |
| R-063 | Phase 3 | Milestone 3.4: Phase 2 Self-Validation and Output |
| R-064 | Phase 3 | 8 self-validation checks (7 blocking, 1 advisory) (FR-032) |
| R-065 | Phase 3 | Emit portify-spec.yaml with step_mapping, module_plan, gate_definitions (FR-033) |
| R-066 | Phase 3 | User approval gate before Phase 3 code generation |
| R-067 | Phase 3 | Phase 3 Exit Criteria |
| R-068 | Phase 4 | Phase 4: Code Generation and Integration (Phases 3-4) |
| R-069 | Phase 4 | Milestone 4.1: Phase 3 — Code Generation Engine |
| R-070 | Phase 4 | Generate 12 Python files in strict dependency order (FR-034) |
| R-071 | Phase 4 | Atomic generation — halt entirely on any file failure (FR-035) |
| R-072 | Phase 4 | Per-file validation: ast.parse(), import paths, base class contract, GateCriteria fields (FR-036) |
| R-073 | Phase 4 | Cross-file validation: module completeness, circular import detection, export matching (FR-037) |
| R-074 | Phase 4 | Emit portify-codegen.yaml (FR-038) |
| R-075 | Phase 4 | Milestone 4.2: Phase 4 — CLI Integration |
| R-076 | Phase 4 | Patch main.py with import and app.add_command() (FR-039) |
| R-077 | Phase 4 | Integration smoke test: module imports, Click command exists, name matches (FR-040) |
| R-078 | Phase 4 | Generate structural test file test_name_structure.py in tests/ (FR-041) |
| R-079 | Phase 4 | Write portify-summary.md: file inventory, CLI usage, step graph, limitations (FR-042) |
| R-080 | Phase 4 | Emit portify-integration.yaml contract |
| R-081 | Phase 4 | Milestone 4.3: Name Normalization and Collision Policy |
| R-082 | Phase 4 | Implement naming convention derivation: kebab-case, snake_case, PascalCase, UPPER_SNAKE (FR-046) |
| R-083 | Phase 4 | Collision policy enforcement: check portify-summary.md marker, never overwrite non-portified (FR-047) |
| R-084 | Phase 4 | Phase 4 Exit Criteria |
| R-085 | Phase 5 | Phase 5: Validation, Testing, and Cleanup |
| R-086 | Phase 5 | Milestone 5.1: Golden Fixture Tests and Negative-Path Validation |
| R-087 | Phase 5 | Golden fixture 1: Simple sequential skill — basic portification, all phases pass |
| R-088 | Phase 5 | Golden fixture 2: Batched audit skill — parallel step groups, trailing gates |
| R-089 | Phase 5 | Golden fixture 3: Adversarial multi-agent skill — multi-domain, N:1 mappings |
| R-090 | Phase 5 | Golden fixture 4: Intentionally unsupported skill — aborts in Phase 0 |
| R-091 | Phase 5 | Negative-path fixture 5: Stale-ref fixture — blocks before Phase 1 |
| R-092 | Phase 5 | Negative-path fixture 6: API-drift fixture — blocks at conformance check |
| R-093 | Phase 5 | Negative-path fixture 7: Name collision fixture — aborts with correct error |
| R-094 | Phase 5 | Negative-path fixture 8: Non-portified collision — never overwrites |
| R-095 | Phase 5 | Milestone 5.2: MCP Degradation Testing |
| R-096 | Phase 5 | Simulate MCP server unavailability for Auggie, Serena, Sequential, Context7 |
| R-097 | Phase 5 | Verify graceful degradation to native tools (NFR-008) |
| R-098 | Phase 5 | Verify advisory warnings logged in phase contracts |
| R-099 | Phase 5 | Verify no phase hard-blocks on MCP unavailability |
| R-100 | Phase 5 | Milestone 5.3: Resume Protocol Validation |
| R-101 | Phase 5 | Simulate failures at each phase boundary (0→1, 1→2, 2→3, 3→4) |
| R-102 | Phase 5 | Verify resume correctly skips completed phases |
| R-103 | Phase 5 | Verify resume re-validates completed phase contracts |
| R-104 | Phase 5 | Verify resume_command template in return contract is correct |
| R-105 | Phase 5 | Milestone 5.4: Cleanup and Sync |
| R-106 | Phase 5 | Remove old sc-cli-portify/ directory |
| R-107 | Phase 5 | Run make verify-sync — confirm src/ and .claude/ match |
| R-108 | Phase 5 | Final make test — all existing tests still pass |
| R-109 | Phase 5 | Final make lint — no ruff violations |
| R-110 | Phase 5 | Phase 5 Exit Criteria |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-004, R-005 | Updated refs/pipeline-spec.md aligned to live API | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0001/evidence.md | M | Medium |
| D-0002 | T01.02 | R-006, R-007 | Updated refs/code-templates.md with correct imports and templates | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0002/evidence.md | M | Medium |
| D-0003 | T01.02 | R-007 | Stale-ref detector script comparing refs against live API | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0003/spec.md | M | Medium |
| D-0004 | T01.03 | R-009 | sc-cli-portify-protocol directory with SKILL.md and __init__.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0004/evidence.md | S | Low |
| D-0005 | T01.04 | R-010 | cli-portify.md command shim with 6 error codes | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0005/spec.md | M | Low |
| D-0006 | T01.05 | R-011, R-012 | YAML frontmatter in SKILL.md and verify-sync coverage | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0006/evidence.md | S | Low |
| D-0007 | T01.06 | R-013 | Deprecation marker on sc-cli-portify/ directory | LIGHT | Quick sanity check | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0007/notes.md | XS | Low |
| D-0008 | T01.09 | R-015 | Documented resolutions for all 10 open questions | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0008/spec.md | L | Medium |
| D-0009 | T01.09 | R-015 | decisions.yaml with blocking OQ implementation decisions | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0009/spec.md | L | Medium |
| D-0010 | T02.01 | R-019, R-020, R-026 | Contract schema versioning policy and common header schema | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0010/spec.md | M | Medium |
| D-0011 | T02.02 | R-021 | Per-phase contract YAML schemas (6 contracts) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0011/spec.md | L | Medium |
| D-0012 | T02.03 | R-022, R-023, R-024, R-025 | Contract validation logic with resume protocol | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0012/evidence.md | L | Medium |
| D-0013 | T02.03 | R-025 | Synthetic failure validation of resume semantics | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0013/evidence.md | L | Medium |
| D-0014 | T02.04 | R-028, R-029, R-030 | Phase 0 prerequisite scanner (path resolution, API snapshot, collision) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0014/evidence.md | L | High |
| D-0015 | T02.04 | R-029 | api-snapshot.yaml with content hash | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0015/spec.md | L | High |
| D-0016 | T02.06 | R-031, R-032 | Phase 0 unsupported-pattern scan and portify-prerequisites.yaml emission | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0016/evidence.md | M | Medium |
| D-0017 | T02.07 | R-034, R-035, R-036 | Component inventory, step decomposition, classification engine | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0017/evidence.md | L | Medium |
| D-0018 | T02.08 | R-037, R-038, R-039 | Dependency DAG with gate tier assignment and trailing safety | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0018/evidence.md | L | High |
| D-0019 | T02.09 | R-040, R-041, R-042, R-043 | Analysis output, self-validation checks, review gate | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0019/evidence.md | M | Medium |
| D-0020 | T02.09 | R-042 | portify-analysis.md (< 400 lines) and portify-analysis.yaml | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0020/spec.md | M | Medium |
| D-0021 | T02.10 | R-045, R-046, R-047 | TodoWrite task definitions and checkpoint wiring | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0021/evidence.md | S | Low |
| D-0022 | T03.01 | R-051, R-052, R-053 | Step mapping with coverage invariant and elimination records | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0022/spec.md | M | Medium |
| D-0023 | T03.02 | R-055, R-056, R-057 | Domain dataclass models, gate designs, API conformance check | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0023/spec.md | L | High |
| D-0024 | T03.03 | R-059, R-060, R-061, R-062 | Prompt templates, executor design, pattern coverage matrix | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0024/spec.md | L | Medium |
| D-0025 | T03.05 | R-064, R-065, R-066 | Phase 2 self-validation checks and portify-spec.yaml | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0025/spec.md | M | Medium |
| D-0026 | T03.05 | R-065 | portify-spec.yaml with step_mapping and module_plan | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0026/evidence.md | M | Medium |
| D-0027 | T04.01 | R-070, R-071 | 12 generated Python files in dependency order with atomic semantics | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0027/evidence.md | XL | High |
| D-0028 | T04.02 | R-072, R-073 | Per-file validation (5 blocking) and cross-file validation (4 blocking) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0028/evidence.md | L | High |
| D-0029 | T04.04 | R-074 | portify-codegen.yaml contract | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0029/evidence.md | S | Low |
| D-0030 | T04.05 | R-076, R-077 | Patched main.py with passing integration smoke test | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0030/evidence.md | M | Medium |
| D-0031 | T04.07 | R-078, R-079, R-080 | Structural test file, portify-summary.md, integration contract | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0031/spec.md | M | Low |
| D-0032 | T04.08 | R-082, R-083 | Name normalization engine and collision policy enforcement | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0032/evidence.md | M | Medium |
| D-0033 | T05.01 | R-087, R-088, R-089, R-090 | 4 golden fixture test definitions and results | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0033/evidence.md | L | Medium |
| D-0034 | T05.02 | R-091, R-092, R-093, R-094 | 4 negative-path fixture test definitions and results | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0034/evidence.md | L | High |
| D-0035 | T05.03 | R-096, R-097, R-098, R-099 | MCP degradation test results for all 4 servers | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0035/evidence.md | M | Medium |
| D-0036 | T05.05 | R-101, R-102, R-103, R-104 | Resume validation results for all 4 phase boundaries | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0036/evidence.md | M | High |
| D-0037 | T05.07 | R-106, R-107, R-108, R-109 | Clean repository with passing sync, tests, and lint | STANDARD | Direct test execution | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0037/evidence.md | M | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-004, R-005 | T01.01 | D-0001 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0001/ |
| R-006, R-007 | T01.02 | D-0002, D-0003 | STRICT | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0002/, D-0003/ |
| R-009 | T01.03 | D-0004 | STRICT | 70% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0004/ |
| R-010 | T01.04 | D-0005 | STRICT | 70% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0005/ |
| R-011, R-012 | T01.05 | D-0006 | STANDARD | 70% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0006/ |
| R-013 | T01.06 | D-0007 | LIGHT | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0007/ |
| R-015 | T01.09 | D-0008, D-0009 | STANDARD | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0008/, D-0009/ |
| R-019, R-020, R-026 | T02.01 | D-0010 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0010/ |
| R-021 | T02.02 | D-0011 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0011/ |
| R-022, R-023, R-024, R-025 | T02.03 | D-0012, D-0013 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0012/, D-0013/ |
| R-028, R-029, R-030 | T02.04 | D-0014, D-0015 | STRICT | 85% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0014/, D-0015/ |
| R-031, R-032 | T02.06 | D-0016 | STANDARD | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0016/ |
| R-034, R-035, R-036 | T02.07 | D-0017 | STRICT | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0017/ |
| R-037, R-038, R-039 | T02.08 | D-0018 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0018/ |
| R-040, R-041, R-042, R-043 | T02.09 | D-0019, D-0020 | STRICT | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0019/, D-0020/ |
| R-045, R-046, R-047 | T02.10 | D-0021 | STANDARD | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0021/ |
| R-051, R-052, R-053 | T03.01 | D-0022 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0022/ |
| R-055, R-056, R-057 | T03.02 | D-0023 | STRICT | 85% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0023/ |
| R-059, R-060, R-061, R-062 | T03.03 | D-0024 | STANDARD | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0024/ |
| R-064, R-065, R-066 | T03.05 | D-0025, D-0026 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0025/, D-0026/ |
| R-070, R-071 | T04.01 | D-0027 | STRICT | 90% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0027/ |
| R-072, R-073 | T04.02 | D-0028 | STRICT | 85% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0028/ |
| R-074 | T04.04 | D-0029 | STANDARD | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0029/ |
| R-076, R-077 | T04.05 | D-0030 | STRICT | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0030/ |
| R-078, R-079, R-080 | T04.07 | D-0031 | STANDARD | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0031/ |
| R-082, R-083 | T04.08 | D-0032 | STANDARD | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0032/ |
| R-087, R-088, R-089, R-090 | T05.01 | D-0033 | STRICT | 85% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0033/ |
| R-091, R-092, R-093, R-094 | T05.02 | D-0034 | STRICT | 85% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0034/ |
| R-096, R-097, R-098, R-099 | T05.03 | D-0035 | STANDARD | 75% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0035/ |
| R-101, R-102, R-103, R-104 | T05.05 | D-0036 | STRICT | 85% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0036/ |
| R-106, R-107, R-108, R-109 | T05.07 | D-0037 | STANDARD | 80% | .dev/releases/current/v2.18-cli-portify-v2/artifacts/D-0037/ |

## Execution Log Template

**Intended Path:** .dev/releases/current/v2.18-cli-portify-v2/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|

## Checkpoint Report Template

**Template:**

```
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** .dev/releases/current/v2.18-cli-portify-v2/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>
## Status
Overall: Pass | Fail | TBD
## Verification Results
- <bullet 1>
- <bullet 2>
- <bullet 3>
## Exit Criteria Assessment
- <bullet 1>
- <bullet 2>
- <bullet 3>
## Issues & Follow-ups
- <list blocking issues; reference T<PP>.<TT> and D-####>
## Evidence
- <intended evidence paths under .dev/releases/current/v2.18-cli-portify-v2/evidence/>
```

## Feedback Collection Template

**Intended Path:** .dev/releases/current/v2.18-cli-portify-v2/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|

## Generation Notes

- Phase numbering preserved from roadmap (1-5, no gaps)
- TASKLIST_ROOT derived from roadmap file path: .dev/releases/current/v2.18-cli-portify-v2/
- Complexity class HIGH based on roadmap complexity_score 0.92 and 70 requirements
- 8 Clarification Tasks (EXEMPT tier) inserted for tasks with tier confidence < 0.70
- T04.01 classified as XL effort; subtask decomposition markers included in phase file
- Primary persona: backend (CLI pipeline, Python code generation, API integration)
- Consulting personas: architect (contract schema design), analyzer (validation checks), qa (fixture testing)
- All R-### IDs assigned in strict top-to-bottom appearance order from roadmap
- Deliverable IDs D-0001 through D-0037 assigned in task appearance order
