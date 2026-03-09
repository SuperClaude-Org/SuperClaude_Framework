# TASKLIST INDEX -- v2.20 WorkflowEvolution Fidelity Validation

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.20 WorkflowEvolution Fidelity Validation |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-09 |
| TASKLIST_ROOT | .dev/releases/current/v2.20-WorkflowEvolution/ |
| Total Phases | 6 |
| Total Tasks | 48 |
| Total Deliverables | 55 |
| Complexity Class | HIGH |
| Primary Persona | analyzer |
| Consulting Personas | backend, architect, qa, devops |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/v2.20-WorkflowEvolution/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/v2.20-WorkflowEvolution/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/v2.20-WorkflowEvolution/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/v2.20-WorkflowEvolution/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/v2.20-WorkflowEvolution/phase-4-tasklist.md |
| Phase 5 Tasklist | .dev/releases/current/v2.20-WorkflowEvolution/phase-5-tasklist.md |
| Phase 6 Tasklist | .dev/releases/current/v2.20-WorkflowEvolution/phase-6-tasklist.md |
| Execution Log | .dev/releases/current/v2.20-WorkflowEvolution/execution-log.md |
| Checkpoint Reports | .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/ |
| Evidence Directory | .dev/releases/current/v2.20-WorkflowEvolution/evidence/ |
| Artifacts Directory | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/ |
| Feedback Log | .dev/releases/current/v2.20-WorkflowEvolution/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Pre-Implementation Decisions | T01.01-T01.09 | STRICT: 0, STANDARD: 0, LIGHT: 0, EXEMPT: 9 |
| 2 | phase-2-tasklist.md | Foundation | T02.01-T02.10 | STRICT: 1, STANDARD: 6, LIGHT: 0, EXEMPT: 3 |
| 3 | phase-3-tasklist.md | Spec-Fidelity Gate | T03.01-T03.06 | STRICT: 0, STANDARD: 5, LIGHT: 0, EXEMPT: 1 |
| 4 | phase-4-tasklist.md | Tasklist Fidelity and CLI | T04.01-T04.05 | STRICT: 1, STANDARD: 3, LIGHT: 0, EXEMPT: 1 |
| 5 | phase-5-tasklist.md | Retrospective and Hardening | T05.01-T05.14 | STRICT: 1, STANDARD: 2, LIGHT: 0, EXEMPT: 11 |
| 6 | phase-6-tasklist.md | Release Readiness | T06.01-T06.04 | STRICT: 0, STANDARD: 1, LIGHT: 0, EXEMPT: 3 |

## Source Snapshot

- Implements fidelity validation across the SuperClaude pipeline: spec-fidelity gate, tasklist-fidelity gate, gate fixes, and retrospective-aware extraction
- 41 requirements (31 functional, 10 non-functional) across 5 domains (pipeline, CLI, gate engine, prompt engineering, state management)
- 8 open questions resolved before implementation with concrete recommendations
- Validation layering: each artifact checks against its immediate upstream only
- Risk concentration in LLM-output consistency, gate strictness rollouts, and cross-reference validation regressions
- Estimated effort: 6 phases, ~30 working days for a single developer

## Deterministic Rules Applied

- Phase buckets derived from roadmap explicit labels: Pre-Implementation Decisions + Phase 1-5 mapped to output Phase 1-6
- Phase numbering is sequential (1-6) with no gaps; roadmap phases renumbered by appearance order
- Task IDs use zero-padded `T<PP>.<TT>` format (e.g., T01.03)
- 1 task per roadmap item by default; splits only for independently deliverable outputs
- Checkpoint cadence: every 5 tasks within a phase + mandatory end-of-phase checkpoint
- Deliverable IDs assigned globally in task order: D-0001 through D-0055
- Effort scoring: character length (+1 if >=120), split bonus (+1), infrastructure keywords (+1), dependency words (+1)
- Risk scoring: security keywords (+2), data/migration keywords (+2), auth keywords (+1), performance keywords (+1), cross-cutting scope (+1)
- Tier classification: STRICT > EXEMPT > LIGHT > STANDARD priority; compound phrase overrides checked first; context boosters applied
- Verification routing: STRICT=sub-agent, STANDARD=direct test, LIGHT=sanity check, EXEMPT=skip
- MCP requirements assigned per tier (STRICT requires Sequential+Serena)
- Traceability: every task traces to R-### roadmap items and D-#### deliverables

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | 1 | OQ-001 — Cross-reference strictness rollout: Warning-first for one release, then blocking. De-risks RSK-003. |
| R-002 | 1 | OQ-004 — Fidelity vs. reflect step ordering: Spec-fidelity runs after reflect. Complementary, not redundant. |
| R-003 | 1 | OQ-006 — Deviation table schema: 7-column FR-051.4 schema with generic Upstream Quote/Downstream Quote names. |
| R-004 | 1 | OQ-007 — Multi-agent mode: Defer multi-agent severity resolution (FR-012) to v2.21. Document conservative merge. |
| R-005 | 1 | OQ-002 — Module placement: cli/tasklist/ as a new module — keeps tasklist validation cleanly separated. |
| R-006 | 1 | OQ-003 — Count cross-validation: Implement frontmatter-vs-table-row count cross-validation as a warning log. |
| R-007 | 1 | OQ-005 — MEDIUM severity blocking policy: Only HIGH-severity deviations block in v2.20. MEDIUM logged non-blocking. |
| R-008 | 1 | OQ-008 — Step timeout vs. NFR mismatch: 120s is p95 performance target; 600s is hard timeout. |
| R-009 | 1 | Exit Criteria: Decision log published with all 8 resolutions. Canonical deviation report schema documented. |
| R-010 | 2 | REFLECT_GATE tier promotion (FR-018): Change enforcement tier from STANDARD to STRICT in validate_gates.py. |
| R-011 | 2 | Cross-reference resolution fix (FR-019): Replace always-True stub in _cross_refs_resolve() with actual validation. |
| R-012 | 2 | Cross-reference unit tests (FR-020): Add unit tests for valid and invalid cross-references. |
| R-013 | 2 | Deviation report format specification (FR-021, FR-026): Create docs/reference/deviation-report-format.md documenting 7-column schema. |
| R-014 | 2 | Severity classification definition (FR-022, FR-023): Define severity classification (HIGH/MEDIUM/LOW) with concrete examples. |
| R-015 | 2 | FidelityDeviation dataclass (FR-031): Create dataclass in new roadmap/fidelity.py module implementing 7-column schema. |
| R-016 | 2 | Semantic check _high_severity_count_zero() (FR-024): Implement in roadmap/gates.py. |
| R-017 | 2 | Semantic check _tasklist_ready_consistent() (FR-025): Implement in roadmap/gates.py. |
| R-018 | 2 | Resolve OQ-002/OQ-003 as exit criteria (AC-006, NFR-006): Confirm cli/tasklist/ module placement and count validation. |
| R-019 | 2 | Phase 1 Tests: Unit, integration, and regression tests for cross-refs, gates, semantic checks, dataclass. |
| R-020 | 2 | Phase 1 Exit Criteria: All existing tests pass, _cross_refs_resolve() rejects dangling references, 100% branch coverage. |
| R-021 | 3 | Spec-fidelity prompt builder (FR-001-004): build_spec_fidelity_prompt() in roadmap/prompts.py with severity definitions. |
| R-022 | 3 | SPEC_FIDELITY_GATE (FR-005-007): New gate in roadmap/gates.py with STRICT enforcement, blocks on high_severity_count. |
| R-023 | 3 | Pipeline step integration (FR-008-010): New spec-fidelity step in _build_steps() in roadmap/executor.py. |
| R-024 | 3 | State persistence and degraded reporting (FR-011, FR-030, FR-051.6): Write fidelity_status to .roadmap-state.json. |
| R-025 | 3 | Performance measurement: Measure step execution time against 120s p95 target during this phase. |
| R-026 | 3 | Phase 2 Tests: Unit and integration tests for prompt builder, gate, pipeline step, state persistence. |
| R-027 | 3 | Phase 2 Exit Criteria: SC-001, SC-002, SC-007, SC-008, SC-014 verified. Pipeline overhead <=5%. |
| R-028 | 4 | Tasklist-fidelity prompt builder (FR-013, FR-014): build_tasklist_fidelity_prompt() with validation layering guard. |
| R-029 | 4 | TASKLIST_FIDELITY_GATE (FR-015): STRICT enforcement, blocks on high_severity_count > 0. |
| R-030 | 4 | CLI subcommand (FR-016, FR-017): superclaude tasklist validate with options in src/superclaude/cli/tasklist/. |
| R-031 | 4 | Performance measurement: Tasklist validation timed against 120s target during this phase. |
| R-032 | 4 | Phase 3 Tests: Unit, integration, E2E tests for tasklist fidelity and CLI. |
| R-033 | 4 | Phase 3 Exit Criteria: SC-005, SC-009, SC-013 verified. CLI registered. Reports parseable. |
| R-034 | 5 | Retrospective parameter wiring (FR-027-029): build_extract_prompt() accepts retrospective_content, RoadmapConfig extended. |
| R-035 | 5 | Multi-agent severity resolution (FR-012) — Documentation only. Conservative merge protocol documented. |
| R-036 | 5 | Full pipeline integration run: Run against 3+ existing specs from .dev/releases/complete/. |
| R-037 | 5 | Cross-reference warning mode verification: Verify warning mode works without blocking. |
| R-038 | 5 | Pipeline performance measurement (SC-012): Measure total pipeline time delta before/after new gates. |
| R-039 | 5 | --no-validate behavior verification (SC-014): Verify --no-validate does NOT skip fidelity step. |
| R-040 | 5 | Historical artifact replay validation (NFR-004, NFR-006): Replay against stricter gates, document failures. |
| R-041 | 5 | Degraded-state semantics documentation: Document failure-state semantics for degraded reports. |
| R-042 | 5 | Monitoring metrics definition: false positive rate, degraded-run frequency, pipeline time drift, severity drift. |
| R-043 | 5 | Rollback plan: Prepare rollback plan if regressions appear in stored artifacts. |
| R-044 | 5 | PLANNING.md pipeline documentation update: Update with new pipeline step documentation. |
| R-045 | 5 | CLI help text update: Update CLI help text for new subcommands and flags. |
| R-046 | 5 | Deviation format reference finalization (FR-026): Deviation format reference doc finalized and reviewed. |
| R-047 | 5 | Operational guidance documentation: Document fidelity status meanings and expected output artifacts. |
| R-048 | 5 | Phase 4 Tests: Unit and integration tests for retrospective wiring, full pipeline. |
| R-049 | 5 | Phase 4 Exit Criteria: SC-006, SC-010, SC-012 verified. All 14 success criteria passing. |
| R-050 | 6 | Full pipeline validation run with all gates active: Execute complete pipeline against representative specs. |
| R-051 | 6 | Release artifact archive: Verify all .dev/releases/ outputs are present and well-formed. |
| R-052 | 6 | Release sign-off checklist completion: Walk through all 14 success criteria with passing evidence. |
| R-053 | 6 | Phase 5 Tests: Full suite 0 failures, E2E full pipeline run, all 14 SC-* criteria verified. |
| R-054 | 6 | Phase 5 Exit Criteria: All 14 SC passing, no regressions, artifacts archived, sign-off documented. |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Written decision for OQ-001 cross-reference strictness | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0001/spec.md | XS | Low |
| D-0002 | T01.02 | R-002 | Written decision for OQ-004 fidelity vs reflect ordering | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0002/spec.md | XS | Low |
| D-0003 | T01.03 | R-003 | Written decision for OQ-006 deviation table schema | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0003/spec.md | S | Low |
| D-0004 | T01.04 | R-004 | Written decision for OQ-007 multi-agent mode deferral | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0004/spec.md | XS | Low |
| D-0005 | T01.05 | R-005 | Written decision for OQ-002 module placement | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0005/spec.md | S | Low |
| D-0006 | T01.06 | R-006 | Written decision for OQ-003 count cross-validation | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0006/spec.md | XS | Low |
| D-0007 | T01.07 | R-007 | Written decision for OQ-005 MEDIUM severity policy | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0007/spec.md | XS | Low |
| D-0008 | T01.08 | R-008 | Written decision for OQ-008 timeout vs NFR | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0008/spec.md | S | Low |
| D-0009 | T01.09 | R-009 | Published decision log with all 8 resolutions | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0009/spec.md | S | Low |
| D-0010 | T01.09 | R-009 | Canonical deviation report schema document | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0010/spec.md | S | Low |
| D-0011 | T02.01 | R-010 | REFLECT_GATE tier changed to STRICT in validate_gates.py | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0011/evidence.md | S | Medium |
| D-0012 | T02.01 | R-010 | Blast radius assessment against existing artifacts | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0012/notes.md | S | Medium |
| D-0013 | T02.02 | R-011 | Fixed _cross_refs_resolve() with heading-anchor validation | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0013/evidence.md | S | Low |
| D-0014 | T02.03 | R-012 | Cross-reference unit tests (valid, invalid, no-refs) | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0014/evidence.md | XS | Low |
| D-0015 | T02.04 | R-013 | docs/reference/deviation-report-format.md | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0015/spec.md | S | Low |
| D-0016 | T02.05 | R-014 | Severity classification document with examples | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0016/spec.md | S | Low |
| D-0017 | T02.06 | R-015 | FidelityDeviation dataclass in roadmap/fidelity.py | STRICT | Sub-agent | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0017/evidence.md | M | Medium |
| D-0018 | T02.07 | R-016 | _high_severity_count_zero() in roadmap/gates.py with tests | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0018/evidence.md | S | Low |
| D-0019 | T02.08 | R-017 | _tasklist_ready_consistent() in roadmap/gates.py with tests | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0019/evidence.md | S | Low |
| D-0020 | T02.09 | R-018 | OQ-002/OQ-003 confirmation recorded in decision log | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0020/notes.md | XS | Low |
| D-0021 | T02.10 | R-019, R-020 | Phase 2 test results — all pass, 0 regressions | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0021/evidence.md | S | Low |
| D-0022 | T03.01 | R-021 | build_spec_fidelity_prompt() in roadmap/prompts.py | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0022/evidence.md | S | Low |
| D-0023 | T03.02 | R-022 | SPEC_FIDELITY_GATE in roadmap/gates.py | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0023/evidence.md | S | Low |
| D-0024 | T03.03 | R-023 | spec-fidelity step in roadmap/executor.py | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0024/evidence.md | M | Low |
| D-0025 | T03.04 | R-024 | fidelity_status state persistence in .roadmap-state.json | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0025/evidence.md | S | Low |
| D-0026 | T03.04 | R-024 | Degraded reporting logic with agent failure details | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0026/evidence.md | S | Low |
| D-0027 | T03.05 | R-025 | Spec-fidelity step performance measurement results | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0027/notes.md | M | Low |
| D-0028 | T03.06 | R-026, R-027 | Phase 3 test results — all pass, SC criteria verified | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0028/evidence.md | S | Low |
| D-0029 | T04.01 | R-028 | build_tasklist_fidelity_prompt() with layering guard | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0029/evidence.md | S | Low |
| D-0030 | T04.02 | R-029 | TASKLIST_FIDELITY_GATE implementation | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0030/evidence.md | S | Low |
| D-0031 | T04.03 | R-030 | CLI module src/superclaude/cli/tasklist/ | STRICT | Sub-agent | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0031/evidence.md | S | Low |
| D-0032 | T04.03 | R-030 | Registered subcommand with help text | STRICT | Sub-agent | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0032/evidence.md | S | Low |
| D-0033 | T04.04 | R-031 | Tasklist validation performance results | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0033/notes.md | M | Low |
| D-0034 | T04.05 | R-032, R-033 | Phase 4 test results — all pass, SC criteria verified | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0034/evidence.md | S | Low |
| D-0035 | T05.01 | R-034 | retrospective_content parameter in build_extract_prompt() | STRICT | Sub-agent | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0035/evidence.md | S | Low |
| D-0036 | T05.01 | R-034 | retrospective_file field in RoadmapConfig | STRICT | Sub-agent | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0036/evidence.md | S | Low |
| D-0037 | T05.01 | R-034 | CLI --retrospective flag in roadmap run | STRICT | Sub-agent | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0037/evidence.md | S | Low |
| D-0038 | T05.02 | R-035 | Multi-agent severity resolution protocol document | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0038/spec.md | XS | Low |
| D-0039 | T05.03 | R-036 | Integration run results for 3+ specs | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0039/evidence.md | M | Low |
| D-0040 | T05.04 | R-037 | Cross-reference warning verification results | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0040/evidence.md | XS | Low |
| D-0041 | T05.05 | R-038 | Pipeline performance delta report | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0041/notes.md | M | Low |
| D-0042 | T05.06 | R-039 | --no-validate behavior verification results | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0042/evidence.md | XS | Low |
| D-0043 | T05.07 | R-040 | Historical artifact replay results with failure reasons | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0043/evidence.md | S | Medium |
| D-0044 | T05.08 | R-041 | Degraded-state semantics document | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0044/spec.md | XS | Low |
| D-0045 | T05.09 | R-042 | Monitoring metrics definition document | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0045/spec.md | M | Medium |
| D-0046 | T05.09 | R-043 | Rollback plan document | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0046/spec.md | M | Medium |
| D-0047 | T05.10 | R-044 | Updated PLANNING.md with pipeline step documentation | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0047/notes.md | S | Low |
| D-0048 | T05.11 | R-045 | Updated CLI help text for new subcommands | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0048/evidence.md | XS | Low |
| D-0049 | T05.12 | R-046 | Finalized deviation format reference document | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0049/spec.md | XS | Low |
| D-0050 | T05.13 | R-047 | Operational guidance document with status examples | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0050/spec.md | S | Low |
| D-0051 | T05.14 | R-048, R-049 | Phase 5 test results — all pass, SC criteria verified | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0051/evidence.md | S | Low |
| D-0052 | T06.01 | R-050 | Full pipeline validation results with all gates | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0052/evidence.md | M | Low |
| D-0053 | T06.02 | R-051 | Archived release artifacts in .dev/releases/ | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0053/notes.md | S | Low |
| D-0054 | T06.03 | R-052 | Completed sign-off checklist with evidence per criterion | EXEMPT | Skip | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0054/spec.md | S | Low |
| D-0055 | T06.04 | R-053, R-054 | Final test suite results — 0 failures, all SC verified | STANDARD | Direct test | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0055/evidence.md | S | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0001/ |
| R-002 | T01.02 | D-0002 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0002/ |
| R-003 | T01.03 | D-0003 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0003/ |
| R-004 | T01.04 | D-0004 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0004/ |
| R-005 | T01.05 | D-0005 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0005/ |
| R-006 | T01.06 | D-0006 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0006/ |
| R-007 | T01.07 | D-0007 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0007/ |
| R-008 | T01.08 | D-0008 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0008/ |
| R-009 | T01.09 | D-0009, D-0010 | EXEMPT | 90% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0009/, .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0010/ |
| R-010 | T02.01 | D-0011, D-0012 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0011/, .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0012/ |
| R-011 | T02.02 | D-0013 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0013/ |
| R-012 | T02.03 | D-0014 | STANDARD | 75% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0014/ |
| R-013 | T02.04 | D-0015 | EXEMPT | 80% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0015/ |
| R-014 | T02.05 | D-0016 | EXEMPT | 82% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0016/ |
| R-015 | T02.06 | D-0017 | STRICT | 78% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0017/ |
| R-016 | T02.07 | D-0018 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0018/ |
| R-017 | T02.08 | D-0019 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0019/ |
| R-018 | T02.09 | D-0020 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0020/ |
| R-019, R-020 | T02.10 | D-0021 | STANDARD | 75% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0021/ |
| R-021 | T03.01 | D-0022 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0022/ |
| R-022 | T03.02 | D-0023 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0023/ |
| R-023 | T03.03 | D-0024 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0024/ |
| R-024 | T03.04 | D-0025, D-0026 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0025/, .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0026/ |
| R-025 | T03.05 | D-0027 | EXEMPT | 78% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0027/ |
| R-026, R-027 | T03.06 | D-0028 | STANDARD | 75% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0028/ |
| R-028 | T04.01 | D-0029 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0029/ |
| R-029 | T04.02 | D-0030 | STANDARD | 72% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0030/ |
| R-030 | T04.03 | D-0031, D-0032 | STRICT | 73% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0031/, .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0032/ |
| R-031 | T04.04 | D-0033 | EXEMPT | 78% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0033/ |
| R-032, R-033 | T04.05 | D-0034 | STANDARD | 75% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0034/ |
| R-034 | T05.01 | D-0035, D-0036, D-0037 | STRICT | 73% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0035/, .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0036/, .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0037/ |
| R-035 | T05.02 | D-0038 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0038/ |
| R-036 | T05.03 | D-0039 | EXEMPT | 78% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0039/ |
| R-037 | T05.04 | D-0040 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0040/ |
| R-038 | T05.05 | D-0041 | EXEMPT | 78% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0041/ |
| R-039 | T05.06 | D-0042 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0042/ |
| R-040 | T05.07 | D-0043 | EXEMPT | 80% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0043/ |
| R-041 | T05.08 | D-0044 | EXEMPT | 90% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0044/ |
| R-042 | T05.09 | D-0045 | EXEMPT | 78% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0045/ |
| R-043 | T05.09 | D-0046 | EXEMPT | 78% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0046/ |
| R-044 | T05.10 | D-0047 | EXEMPT | 88% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0047/ |
| R-045 | T05.11 | D-0048 | STANDARD | 70% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0048/ |
| R-046 | T05.12 | D-0049 | EXEMPT | 88% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0049/ |
| R-047 | T05.13 | D-0050 | EXEMPT | 88% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0050/ |
| R-048, R-049 | T05.14 | D-0051 | STANDARD | 75% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0051/ |
| R-050 | T06.01 | D-0052 | EXEMPT | 82% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0052/ |
| R-051 | T06.02 | D-0053 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0053/ |
| R-052 | T06.03 | D-0054 | EXEMPT | 85% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0054/ |
| R-053, R-054 | T06.04 | D-0055 | STANDARD | 75% | .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0055/ |

## Execution Log Template

**Intended Path:** .dev/releases/current/v2.20-WorkflowEvolution/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

**Template:**

```markdown
# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/<deterministic-name>.md
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
- .dev/releases/current/v2.20-WorkflowEvolution/evidence/<relevant-file>
```

## Feedback Collection Template

**Intended Path:** .dev/releases/current/v2.20-WorkflowEvolution/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

## Generation Notes

- Pre-Implementation Decisions section mapped as Phase 1 (output); roadmap Phase 1-5 mapped to output Phase 2-6
- All 8 open questions from roadmap have concrete recommendations; no Clarification Tasks generated
- Risk register items (RSK-001 through RSK-008) incorporated as risk drivers in relevant tasks
- Parallelization opportunity noted (Phases 3/4 can branch from Phase 2) preserved via cross-phase dependencies
- FR-012 (multi-agent severity resolution) explicitly scoped as documentation-only per roadmap decision
- No XL effort tasks; largest tasks are M (pipeline integration, performance measurement)
