# TASKLIST INDEX -- v2.22 RoadmapRemediate Pipeline Extension

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.22 RoadmapRemediate Pipeline Extension |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-10 |
| TASKLIST_ROOT | `.dev/releases/current/v2.22-RoadmapRemediate/` |
| Total Phases | 7 |
| Total Tasks | 43 |
| Total Deliverables | 43 |
| Complexity Class | HIGH |
| Primary Persona | backend-architect |
| Consulting Personas | analyzer, qa, security |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `.dev/releases/current/v2.22-RoadmapRemediate/tasklist-index.md` |
| Phase 1 Tasklist | `.dev/releases/current/v2.22-RoadmapRemediate/phase-1-tasklist.md` |
| Phase 2 Tasklist | `.dev/releases/current/v2.22-RoadmapRemediate/phase-2-tasklist.md` |
| Phase 3 Tasklist | `.dev/releases/current/v2.22-RoadmapRemediate/phase-3-tasklist.md` |
| Phase 4 Tasklist | `.dev/releases/current/v2.22-RoadmapRemediate/phase-4-tasklist.md` |
| Phase 5 Tasklist | `.dev/releases/current/v2.22-RoadmapRemediate/phase-5-tasklist.md` |
| Phase 6 Tasklist | `.dev/releases/current/v2.22-RoadmapRemediate/phase-6-tasklist.md` |
| Phase 7 Tasklist | `.dev/releases/current/v2.22-RoadmapRemediate/phase-7-tasklist.md` |
| Execution Log | `.dev/releases/current/v2.22-RoadmapRemediate/execution-log.md` |
| Checkpoint Reports | `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/` |
| Evidence Directory | `.dev/releases/current/v2.22-RoadmapRemediate/evidence/` |
| Artifacts Directory | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/` |
| Validation Reports | `.dev/releases/current/v2.22-RoadmapRemediate/validation/` |
| Feedback Log | `.dev/releases/current/v2.22-RoadmapRemediate/feedback-log.md` |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Discovery and Architecture Lock | T01.01-T01.03 | STRICT: 0, STANDARD: 0, LIGHT: 0, EXEMPT: 3 |
| 2 | phase-2-tasklist.md | Foundation — Models, State, Parsing | T02.01-T02.05 | STRICT: 2, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 3 | phase-3-tasklist.md | Interactive Prompt and Tasklist Plan | T03.01-T03.05 | STRICT: 0, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 4 | phase-4-tasklist.md | Remediation Orchestrator | T04.01-T04.10 | STRICT: 3, STANDARD: 7, LIGHT: 0, EXEMPT: 0 |
| 5 | phase-5-tasklist.md | Certification Step | T05.01-T05.06 | STRICT: 0, STANDARD: 6, LIGHT: 0, EXEMPT: 0 |
| 6 | phase-6-tasklist.md | Resume Support and State Finalization | T06.01-T06.05 | STRICT: 2, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 7 | phase-7-tasklist.md | Integration Testing and Release Hardening | T07.01-T07.09 | STRICT: 2, STANDARD: 6, LIGHT: 0, EXEMPT: 1 |

## Source Snapshot

- Extends `roadmap run` pipeline with remediate (step 10) and certify (step 11) post-validation steps
- Multi-agent orchestration with file-level batching and snapshot-based rollback
- Parser infrastructure for validation report extraction with fallback deduplication
- Interactive severity-scoped prompt (BLOCKING / +WARNING / All / Skip)
- Single-pass certification with scoped evidence windows and skeptical design
- Resume support with SHA-256 stale hash detection and backward-compatible state schema

## Deterministic Rules Applied

- Phase renumbering: roadmap P0-P6 renumbered to contiguous Phase 1-7
- Task ID scheme: `T<PP>.<TT>` zero-padded 2-digit format
- Checkpoint cadence: every 5 tasks within a phase + end-of-phase mandatory checkpoint
- Clarification task rule: inserted when missing specifics prevent execution
- Deliverable registry: D-0001 through D-0055 in global appearance order
- Effort mapping: keyword-scored XS/S/M/L/XL per §5.2.1
- Risk mapping: keyword-scored Low/Medium/High per §5.2.2
- Tier classification: STRICT > EXEMPT > LIGHT > STANDARD priority with compound phrase overrides
- Verification routing: STRICT → sub-agent, STANDARD → direct test, LIGHT → sanity, EXEMPT → skip
- MCP requirements: STRICT requires Sequential + Serena; STANDARD prefers Sequential + Context7
- Traceability matrix: R-### → T<PP>.<TT> → D-#### complete chain
- Multi-file output: index + 7 phase files compatible with Sprint CLI discovery

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | 1 | Review existing pipeline foundation: execute_pipeline(), execute_roadmap(), validate_executor.py, step/gate/state models, resume flow, hash usage patterns |
| R-002 | 1 | Confirm current state schema version and additive-extension strategy |
| R-003 | 1 | Resolve structural open questions: SIGINT behavior during remediation, hash algorithm standardization, step wiring confirmation |
| R-004 | 1 | Define canonical finding lifecycle: PENDING → FIXED / FAILED / SKIPPED |
| R-005 | 2 | Finding dataclass with all specified fields (id, severity, dimension, description, location, evidence, fix_guidance, files_affected, status, agreement_category) |
| R-006 | 2 | State schema shape definition: .roadmap-state.json extended with remediate and certify step entry structures |
| R-007 | 2 | Primary report parser (remediate_parser.py) for validate/reflect-merged.md and validate/merged-validation-report.md |
| R-008 | 2 | Fallback parser for individual reflect-* reports with deduplication (same file, within 5 lines, higher severity) |
| R-009 | 2 | Unit tests for both parser paths against 3+ known report format variants |
| R-010 | 3 | Terminal summary printer: findings grouped by severity with IDs and descriptions |
| R-011 | 3 | Interactive 4-option prompt in execute_roadmap() (NOT in execute_pipeline()) |
| R-012 | 3 | Scope filter: Option 1 BLOCKING only, Option 2 BLOCKING+WARNING, Option 3 all with fix_guidance |
| R-013 | 3 | Auto-SKIP logic for NO_ACTION_REQUIRED and OUT_OF_SCOPE findings |
| R-014 | 3 | Zero-findings guard: 0 actionable emit stub tasklist, proceed to certify |
| R-015 | 3 | Skip-remediation path: user selects n, save state as validated-with-issues, end |
| R-016 | 3 | remediation-tasklist.md generation with full YAML frontmatter and grouped entries |
| R-017 | 3 | REMEDIATE_GATE definition with required fields, minimum line count, semantic validation |
| R-018 | 4 | File-level grouping: batch actionable findings by primary target file |
| R-019 | 4 | Cross-file finding handling: include in both agents prompts with scoped guidance |
| R-020 | 4 | Prompt builder (remediate_prompts.py): pure function producing agent prompts with target file |
| R-021 | 4 | File allowlist enforcement: agents may ONLY edit roadmap.md, extraction.md, test-strategy.md |
| R-022 | 4 | Pre-remediate snapshots: file.pre-remediate before agent spawn |
| R-023 | 4 | Parallel agent execution via ClaudeProcess (not execute_pipeline()) |
| R-024 | 4 | Timeout enforcement: 300s per agent, single retry |
| R-025 | 4 | Failure handling: halt remaining agents, rollback all files, mark FAILED |
| R-026 | 4 | Success handling: delete snapshots, mark FIXED |
| R-027 | 4 | Tasklist update: write outcomes (FIXED/FAILED/SKIPPED) to existing remediation-tasklist.md |
| R-028 | 4 | Step registration: remediate step with REMEDIATE_GATE, dual-nature (outer pipeline + internal ClaudeProcess) |
| R-029 | 4 | Context isolation: agents receive only prompt + --file, no session flags |
| R-030 | 4 | Model inheritance from parent pipeline config |
| R-031 | 4 | YAML frontmatter and heading preservation by agents |
| R-032 | 5 | Certification prompt builder (certify_prompts.py): pure function, scoped sections only |
| R-033 | 5 | Certification context extractor: assembles only relevant sections around finding locations |
| R-034 | 5 | certification-report.md with YAML frontmatter and per-finding PASS/FAIL table with justifications |
| R-035 | 5 | Outcome routing: all pass certified true, some fail certified-with-caveats |
| R-036 | 5 | CERTIFY_GATE with required frontmatter, min 15 lines, semantic checks, per-finding table |
| R-037 | 5 | Step registration via execute_pipeline([certify_step]) |
| R-038 | 5 | No automatic loop — single pass only |
| R-039 | 6 | State schema field finalization: complete metadata fields for remediate and certify entries |
| R-040 | 6 | --resume skip logic for remediate step (gate check) |
| R-041 | 6 | --resume skip logic for certify step (gate check) |
| R-042 | 6 | Stale hash detection: source_report_hash (SHA-256) comparison on resume |
| R-043 | 6 | Resume from each state: post-validate, post-remediate, post-certify |
| R-044 | 6 | State transitions: correct metadata fields written at each step boundary |
| R-045 | 6 | Backward-compatibility validation: old state files without new fields don't crash |
| R-046 | 7 | End-to-end integration test: full 12-step pipeline run |
| R-047 | 7 | Allowlist enforcement test: verify no files outside set are modified |
| R-048 | 7 | Performance test: ≤30% overhead for steps 10-11 |
| R-049 | 7 | Tasklist round-trip test: parse emit re-parse validates format |
| R-050 | 7 | Backward-compatibility test: old consumers + new state schema |
| R-051 | 7 | Deliberate-failure test: unfixed findings correctly reported as FAIL |
| R-052 | 7 | Edge case coverage: SIGINT during remediation, out-of-allowlist findings, zero-findings path, fallback parser |
| R-053 | 7 | Regression validation on pre-existing roadmap flows (steps 1-9) |
| R-054 | 7 | Code review against architectural constraints: pure prompts, unidirectional imports, atomic writes |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001, R-002 | Pipeline foundation review notes | EXEMPT | Skip | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0001/notes.md` | M | Medium |
| D-0002 | T01.02 | R-003 | Structural decisions document (SIGINT, hash, wiring) | EXEMPT | Skip | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0002/spec.md` | M | Low |
| D-0003 | T01.03 | R-004 | Finding lifecycle model definition | EXEMPT | Skip | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0003/spec.md` | XS | Low |
| D-0004 | T02.01 | R-005 | Finding dataclass in roadmap/models.py | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0004/spec.md` | S | Medium |
| D-0005 | T02.02 | R-006 | State schema shape definition | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0005/spec.md` | S | Medium |
| D-0006 | T02.03 | R-007 | remediate_parser.py (primary parser) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0006/spec.md` | S | Low |
| D-0007 | T02.04 | R-008 | Fallback parser with deduplication logic | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0007/spec.md` | S | Low |
| D-0008 | T02.05 | R-009 | Parser unit test suite (3+ format variants) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0008/evidence.md` | S | Low |
| D-0009 | T03.01 | R-010, R-011 | Terminal summary printer + interactive prompt | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0009/spec.md` | S | Low |
| D-0010 | T03.02 | R-012, R-013 | Scope filter + auto-SKIP functions | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0010/spec.md` | XS | Low |
| D-0011 | T03.03 | R-014, R-015 | Zero-findings guard + skip path | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0011/spec.md` | XS | Low |
| D-0012 | T03.04 | R-016 | remediation-tasklist.md generator | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0012/spec.md` | S | Low |
| D-0013 | T03.05 | R-017 | REMEDIATE_GATE definition | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0013/spec.md` | XS | Low |
| D-0014 | T04.01 | R-020 | remediate_prompts.py (prompt builder) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0014/spec.md` | S | Low |
| D-0015 | T04.02 | R-018, R-019 | File-level grouping + cross-file handler | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0015/spec.md` | S | Low |
| D-0016 | T04.03 | R-022 | Pre-remediate snapshot mechanism | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0016/spec.md` | XS | Medium |
| D-0017 | T04.04 | R-021 | File allowlist enforcement | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0017/spec.md` | XS | Low |
| D-0018 | T04.05 | R-023, R-029, R-030 | Parallel ClaudeProcess executor with context isolation | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0018/spec.md` | M | Low |
| D-0019 | T04.06 | R-024 | Timeout + retry handler (300s, 1 retry) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0019/spec.md` | XS | Low |
| D-0020 | T04.07 | R-025 | Failure handler with full rollback | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0020/spec.md` | S | High |
| D-0021 | T04.08 | R-026 | Success handler with snapshot cleanup | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0021/spec.md` | XS | Low |
| D-0022 | T04.09 | R-027 | Tasklist outcome writer (two-write model) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0022/spec.md` | XS | Low |
| D-0023 | T04.10 | R-028, R-031 | Remediate step registration + YAML preservation | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0023/spec.md` | S | Low |
| D-0024 | T05.01 | R-032 | certify_prompts.py (prompt builder) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0024/spec.md` | XS | Low |
| D-0025 | T05.02 | R-033 | Certification context extractor | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0025/spec.md` | XS | Low |
| D-0026 | T05.03 | R-034 | certification-report.md generator | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0026/spec.md` | XS | Low |
| D-0027 | T05.04 | R-035, R-038 | Outcome routing + no-loop enforcement | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0027/spec.md` | XS | Low |
| D-0028 | T05.05 | R-036 | CERTIFY_GATE definition | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0028/spec.md` | XS | Low |
| D-0029 | T05.06 | R-037 | Certify step registration via execute_pipeline() | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0029/spec.md` | S | Low |
| D-0030 | T06.01 | R-039, R-044 | Finalized state schema fields + step transitions | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0030/spec.md` | S | Medium |
| D-0031 | T06.02 | R-040, R-041 | Resume skip logic for remediate + certify | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0031/spec.md` | XS | Low |
| D-0032 | T06.03 | R-042 | Stale hash detection (SHA-256) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0032/spec.md` | XS | Low |
| D-0033 | T06.04 | R-043 | Resume state test suite | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0033/evidence.md` | XS | Low |
| D-0034 | T06.05 | R-045 | Backward-compatibility validation suite | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0034/evidence.md` | XS | High |
| D-0035 | T07.01 | R-046 | E2E integration test (12-step pipeline) | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0035/evidence.md` | L | Medium |
| D-0036 | T07.02 | R-047 | Allowlist enforcement test | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0036/evidence.md` | S | Low |
| D-0037 | T07.03 | R-048 | Performance benchmark test | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0037/evidence.md` | M | Medium |
| D-0038 | T07.04 | R-049 | Tasklist round-trip test | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0038/evidence.md` | S | Low |
| D-0039 | T07.05 | R-050 | Backward-compatibility test | STRICT | Sub-agent | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0039/evidence.md` | S | Medium |
| D-0040 | T07.06 | R-051 | Deliberate-failure test | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0040/evidence.md` | M | Low |
| D-0041 | T07.07 | R-052 | Edge case test suite | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0041/evidence.md` | M | Medium |
| D-0042 | T07.08 | R-053 | Regression test suite (steps 1-9) | STANDARD | Direct test | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0042/evidence.md` | M | Medium |
| D-0043 | T07.09 | R-054 | Architectural constraint review report | EXEMPT | Skip | `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0043/notes.md` | M | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | EXEMPT | 80% | `artifacts/D-0001/notes.md` |
| R-002 | T01.01 | D-0001 | EXEMPT | 80% | `artifacts/D-0001/notes.md` |
| R-003 | T01.02 | D-0002 | EXEMPT | 72% | `artifacts/D-0002/spec.md` |
| R-004 | T01.03 | D-0003 | EXEMPT | 82% | `artifacts/D-0003/spec.md` |
| R-005 | T02.01 | D-0004 | STRICT | 78% | `artifacts/D-0004/spec.md` |
| R-006 | T02.02 | D-0005 | STRICT | 85% | `artifacts/D-0005/spec.md` |
| R-007 | T02.03 | D-0006 | STANDARD | 82% | `artifacts/D-0006/spec.md` |
| R-008 | T02.04 | D-0007 | STANDARD | 80% | `artifacts/D-0007/spec.md` |
| R-009 | T02.05 | D-0008 | STANDARD | 85% | `artifacts/D-0008/evidence.md` |
| R-010 | T03.01 | D-0009 | STANDARD | 80% | `artifacts/D-0009/spec.md` |
| R-011 | T03.01 | D-0009 | STANDARD | 80% | `artifacts/D-0009/spec.md` |
| R-012 | T03.02 | D-0010 | STANDARD | 82% | `artifacts/D-0010/spec.md` |
| R-013 | T03.02 | D-0010 | STANDARD | 82% | `artifacts/D-0010/spec.md` |
| R-014 | T03.03 | D-0011 | STANDARD | 82% | `artifacts/D-0011/spec.md` |
| R-015 | T03.03 | D-0011 | STANDARD | 82% | `artifacts/D-0011/spec.md` |
| R-016 | T03.04 | D-0012 | STANDARD | 82% | `artifacts/D-0012/spec.md` |
| R-017 | T03.05 | D-0013 | STANDARD | 80% | `artifacts/D-0013/spec.md` |
| R-018 | T04.02 | D-0015 | STRICT | 72% | `artifacts/D-0015/spec.md` |
| R-019 | T04.02 | D-0015 | STRICT | 72% | `artifacts/D-0015/spec.md` |
| R-020 | T04.01 | D-0014 | STANDARD | 82% | `artifacts/D-0014/spec.md` |
| R-021 | T04.04 | D-0017 | STANDARD | 75% | `artifacts/D-0017/spec.md` |
| R-022 | T04.03 | D-0016 | STANDARD | 80% | `artifacts/D-0016/spec.md` |
| R-023 | T04.05 | D-0018 | STRICT | 75% | `artifacts/D-0018/spec.md` |
| R-024 | T04.06 | D-0019 | STANDARD | 82% | `artifacts/D-0019/spec.md` |
| R-025 | T04.07 | D-0020 | STRICT | 88% | `artifacts/D-0020/spec.md` |
| R-026 | T04.08 | D-0021 | STANDARD | 82% | `artifacts/D-0021/spec.md` |
| R-027 | T04.09 | D-0022 | STANDARD | 82% | `artifacts/D-0022/spec.md` |
| R-028 | T04.10 | D-0023 | STANDARD | 80% | `artifacts/D-0023/spec.md` |
| R-029 | T04.05 | D-0018 | STRICT | 75% | `artifacts/D-0018/spec.md` |
| R-030 | T04.05 | D-0018 | STRICT | 75% | `artifacts/D-0018/spec.md` |
| R-031 | T04.10 | D-0023 | STANDARD | 80% | `artifacts/D-0023/spec.md` |
| R-032 | T05.01 | D-0024 | STANDARD | 82% | `artifacts/D-0024/spec.md` |
| R-033 | T05.02 | D-0025 | STANDARD | 82% | `artifacts/D-0025/spec.md` |
| R-034 | T05.03 | D-0026 | STANDARD | 82% | `artifacts/D-0026/spec.md` |
| R-035 | T05.04 | D-0027 | STANDARD | 82% | `artifacts/D-0027/spec.md` |
| R-036 | T05.05 | D-0028 | STANDARD | 80% | `artifacts/D-0028/spec.md` |
| R-037 | T05.06 | D-0029 | STANDARD | 80% | `artifacts/D-0029/spec.md` |
| R-038 | T05.04 | D-0027 | STANDARD | 82% | `artifacts/D-0027/spec.md` |
| R-039 | T06.01 | D-0030 | STRICT | 85% | `artifacts/D-0030/spec.md` |
| R-040 | T06.02 | D-0031 | STANDARD | 82% | `artifacts/D-0031/spec.md` |
| R-041 | T06.02 | D-0031 | STANDARD | 82% | `artifacts/D-0031/spec.md` |
| R-042 | T06.03 | D-0032 | STANDARD | 80% | `artifacts/D-0032/spec.md` |
| R-043 | T06.04 | D-0033 | STANDARD | 85% | `artifacts/D-0033/evidence.md` |
| R-044 | T06.01 | D-0030 | STRICT | 85% | `artifacts/D-0030/spec.md` |
| R-045 | T06.05 | D-0034 | STRICT | 85% | `artifacts/D-0034/evidence.md` |
| R-046 | T07.01 | D-0035 | STRICT | 88% | `artifacts/D-0035/evidence.md` |
| R-047 | T07.02 | D-0036 | STANDARD | 80% | `artifacts/D-0036/evidence.md` |
| R-048 | T07.03 | D-0037 | STANDARD | 80% | `artifacts/D-0037/evidence.md` |
| R-049 | T07.04 | D-0038 | STANDARD | 78% | `artifacts/D-0038/evidence.md` |
| R-050 | T07.05 | D-0039 | STRICT | 80% | `artifacts/D-0039/evidence.md` |
| R-051 | T07.06 | D-0040 | STANDARD | 80% | `artifacts/D-0040/evidence.md` |
| R-052 | T07.07 | D-0041 | STANDARD | 80% | `artifacts/D-0041/evidence.md` |
| R-053 | T07.08 | D-0042 | STANDARD | 80% | `artifacts/D-0042/evidence.md` |
| R-054 | T07.09 | D-0043 | EXEMPT | 85% | `artifacts/D-0043/notes.md` |

## Execution Log Template

**Intended Path:** `.dev/releases/current/v2.22-RoadmapRemediate/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

**Template:**

```
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** .dev/releases/current/v2.22-RoadmapRemediate/checkpoints/<deterministic-name>.md
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
- <list blocking issues referencing T<PP>.<TT> and D-####>
## Evidence
- <bullet list of intended evidence paths>
```

## Feedback Collection Template

**Intended Path:** `.dev/releases/current/v2.22-RoadmapRemediate/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

## Generation Notes

- Phase renumbering applied: roadmap P0-P6 → output Phase 1-7 (contiguous, no gaps)
- Sprint-to-days assumption from roadmap §6: 1 sprint ≈ 3-5 working days
- Roadmap items R-001/R-002 consolidated into single task T01.01 (both are review activities in same phase)
- Cross-file roadmap items (R-018/R-019, R-010/R-011, R-012/R-013, R-014/R-015) consolidated where independently non-deliverable
- No Clarification Tasks needed: all roadmap items are sufficiently specified with concrete deliverables
- Phase mapping table available in roadmap §6 (spec phases → roadmap phases)
