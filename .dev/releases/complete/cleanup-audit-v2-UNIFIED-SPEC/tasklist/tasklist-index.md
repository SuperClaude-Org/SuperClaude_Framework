# TASKLIST INDEX -- sc:cleanup-audit v2

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | sc:cleanup-audit v2 |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-05T00:00:00Z |
| TASKLIST_ROOT | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/ |
| Total Phases | 5 |
| Total Tasks | 48 |
| Total Deliverables | 48 |
| Complexity Class | HIGH |
| Primary Persona | backend |
| Consulting Personas | architect, security |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/phase-4-tasklist.md |
| Phase 5 Tasklist | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/phase-5-tasklist.md |
| Execution Log | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/execution-log.md |
| Checkpoint Reports | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/ |
| Evidence Directory | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/evidence/ |
| Artifacts Directory | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/ |
| Feedback Log | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Enforce Promises and Correctness | T01.01-T01.10 | STRICT: 8, STANDARD: 2 |
| 2 | phase-2-tasklist.md | Profile and Batch Infrastructure | T02.01-T02.06 | STRICT: 4, STANDARD: 2 |
| 3 | phase-3-tasklist.md | Structural Depth and Synthesis | T03.01-T03.10 | STRICT: 8, STANDARD: 2 |
| 4 | phase-4-tasklist.md | Validation and Budget Controls | T04.01-T04.13 | STRICT: 8, STANDARD: 5 |
| 5 | phase-5-tasklist.md | Extensions and Final Acceptance | T05.01-T05.09 | STRICT: 5, STANDARD: 2, LIGHT: 2 |

## Source Snapshot

- Unified cleanup-audit v2 specification targeting closure of v1 promise gaps before optional extensions
- 10 milestones (M1-M10) with explicit dependency sequencing and 20 acceptance criteria (AC1-AC20)
- HIGH complexity (0.799) with backend-dominant domain distribution (55% backend, 15% performance, 12% security)
- Adversarial multi-roadmap comparison selected sonnet:backend as base variant (convergence 0.86)
- Key risks: token budget underestimation, spec-implementation gap recurrence, large-repo scaling limits
- 20 success criteria with measurable validation targets across all milestones

## Deterministic Rules Applied

- Phase bucketing from explicit milestone dependency graph: M1+M2 -> M3 -> M4+M5 -> M6+M7+M8 -> M9+M10
- Sequential phase numbering 1-5 with no gaps (roadmap milestones M1-M10 mapped to 5 phases)
- Task IDs use T<PP>.<TT> zero-padded format (T01.01 through T05.09)
- One task per deliverable (D1.1-D10.5); no splits required as each deliverable is independently actionable
- Checkpoint cadence: every 5 tasks within a phase plus mandatory end-of-phase checkpoint
- Clarification tasks inserted when tier classification confidence < 0.70 (none triggered)
- Effort scoring: keyword match on roadmap item text per Section 5.2.1 algorithm
- Risk scoring: keyword match with security/migration/auth/performance/cross-cutting categories per Section 5.2.2
- Tier classification: STRICT/STANDARD/LIGHT/EXEMPT with compound phrase overrides checked first
- Verification routing: STRICT -> sub-agent (quality-engineer), STANDARD -> direct test, LIGHT -> sanity check
- MCP requirements: STRICT tasks require Sequential + Serena; STANDARD prefer Sequential + Context7
- Traceability: every R-### maps to T<PP>.<TT> maps to D-#### with artifact paths

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | 1 | Two-tier classification with backward mapping |
| R-002 | 1 | Coverage tracking by risk tier |
| R-003 | 1 | Batch-level checkpointing (`progress.json`) |
| R-004 | 1 | Evidence-gated DELETE/KEEP rules |
| R-005 | 1 | 10% consistency validation pass |
| R-006 | 1 | Real credential scanning with safe redaction |
| R-007 | 1 | Gitignore inconsistency detection |
| R-008 | 1 | Phase-1 simplified scanner schema |
| R-009 | 1 | Phase-2 full profile schema alignment |
| R-010 | 1 | Batch failure/retry handling policy |
| R-011 | 2 | Domain/risk-tier profiling |
| R-012 | 2 | Monorepo-aware batch decomposition |
| R-013 | 2 | Static-tool orchestration and caching |
| R-014 | 2 | Auto-config generation for cold start |
| R-015 | 2 | Dry-run profile and estimate output |
| R-016 | 2 | Manifest completeness gate |
| R-017 | 3 | 8-field profile generation for target sets |
| R-018 | 3 | File-type specific verification rules |
| R-019 | 3 | Signal-triggered full-file escalation |
| R-020 | 3 | Tiered KEEP evidence enforcement |
| R-021 | 3 | Env key-presence matrix for drift |
| R-022 | 3 | 3-tier dependency graph with confidence labels |
| R-023 | 3 | Cross-boundary dead code candidate logic |
| R-024 | 3 | Duplication matrix with consolidation thresholds |
| R-025 | 3 | Minimal docs audit (broken refs + temporal) |
| R-026 | 3 | Dynamic-import-safe classification policy |
| R-027 | 4 | Cross-phase dedup consolidation |
| R-028 | 4 | Stratified 10% spot-check validation |
| R-029 | 4 | Consistency-rate and calibration framing |
| R-030 | 4 | Coverage + validation output artifacts |
| R-031 | 4 | Directory assessment blocks for large dirs |
| R-032 | 4 | Budget accounting and enforcement |
| R-033 | 4 | Degradation sequence implementation |
| R-034 | 4 | Degrade-priority override handling |
| R-035 | 4 | Budget realism caveat/reporting |
| R-036 | 4 | Report depth modes (summary/standard/detailed) |
| R-037 | 4 | Resume semantics from checkpoints |
| R-038 | 4 | Anti-lazy distribution and consistency guards |
| R-039 | 4 | Final report section completeness checks |
| R-040 | 5 | Full docs pass (`--pass-docs`) with 5-section output |
| R-041 | 5 | Known-issues registry load/match/output |
| R-042 | 5 | TTL/LRU lifecycle rules in registry behavior |
| R-043 | 5 | ALREADY_TRACKED report section integration |
| R-044 | 5 | AC1-AC20 automated validation suite |
| R-045 | 5 | Benchmark runs (small/medium/known-dead-code repo) |
| R-046 | 5 | Concurrent-run isolation validation |
| R-047 | 5 | Non-determinism/limitations reporting |
| R-048 | 5 | Final release readiness decision record |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Two-tier classification with backward mapping | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0001/spec.md | M | High |
| D-0002 | T01.02 | R-002 | Coverage tracking by risk tier | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0002/spec.md | S | Medium |
| D-0003 | T01.03 | R-003 | Batch-level checkpointing (progress.json) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0003/spec.md | M | Medium |
| D-0004 | T01.04 | R-004 | Evidence-gated DELETE/KEEP rules | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0004/spec.md | M | High |
| D-0005 | T01.05 | R-005 | 10% consistency validation pass | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0005/spec.md | S | Medium |
| D-0006 | T01.06 | R-006 | Real credential scanning with safe redaction | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0006/spec.md | M | High |
| D-0007 | T01.07 | R-007 | Gitignore inconsistency detection | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0007/spec.md | S | Low |
| D-0008 | T01.08 | R-008 | Phase-1 simplified scanner schema | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0008/spec.md | M | Medium |
| D-0009 | T01.09 | R-009 | Phase-2 full profile schema alignment | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0009/spec.md | M | Medium |
| D-0010 | T01.10 | R-010 | Batch failure/retry handling policy | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0010/spec.md | S | Medium |
| D-0011 | T02.01 | R-011 | Domain/risk-tier profiling | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0011/spec.md | M | Medium |
| D-0012 | T02.02 | R-012 | Monorepo-aware batch decomposition | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0012/spec.md | L | High |
| D-0013 | T02.03 | R-013 | Static-tool orchestration and caching | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0013/spec.md | M | Medium |
| D-0014 | T02.04 | R-014 | Auto-config generation for cold start | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0014/spec.md | S | Low |
| D-0015 | T02.05 | R-015 | Dry-run profile and estimate output | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0015/spec.md | S | Low |
| D-0016 | T02.06 | R-016 | Manifest completeness gate | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0016/spec.md | S | Medium |
| D-0017 | T03.01 | R-017 | 8-field profile generation for target sets | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0017/spec.md | M | Medium |
| D-0018 | T03.02 | R-018 | File-type specific verification rules | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0018/spec.md | M | Medium |
| D-0019 | T03.03 | R-019 | Signal-triggered full-file escalation | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0019/spec.md | M | Medium |
| D-0020 | T03.04 | R-020 | Tiered KEEP evidence enforcement | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0020/spec.md | M | High |
| D-0021 | T03.05 | R-021 | Env key-presence matrix for drift | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0021/spec.md | M | High |
| D-0022 | T03.06 | R-022 | 3-tier dependency graph with confidence labels | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0022/spec.md | L | High |
| D-0023 | T03.07 | R-023 | Cross-boundary dead code candidate logic | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0023/spec.md | M | High |
| D-0024 | T03.08 | R-024 | Duplication matrix with consolidation thresholds | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0024/spec.md | M | Medium |
| D-0025 | T03.09 | R-025 | Minimal docs audit (broken refs + temporal) | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0025/spec.md | S | Low |
| D-0026 | T03.10 | R-026 | Dynamic-import-safe classification policy | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0026/spec.md | M | High |
| D-0027 | T04.01 | R-027 | Cross-phase dedup consolidation | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0027/spec.md | M | Medium |
| D-0028 | T04.02 | R-028 | Stratified 10% spot-check validation | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0028/spec.md | M | Medium |
| D-0029 | T04.03 | R-029 | Consistency-rate and calibration framing | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0029/spec.md | S | Low |
| D-0030 | T04.04 | R-030 | Coverage + validation output artifacts | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0030/spec.md | S | Low |
| D-0031 | T04.05 | R-031 | Directory assessment blocks for large dirs | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0031/spec.md | S | Low |
| D-0032 | T04.06 | R-032 | Budget accounting and enforcement | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0032/spec.md | M | High |
| D-0033 | T04.07 | R-033 | Degradation sequence implementation | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0033/spec.md | M | High |
| D-0034 | T04.08 | R-034 | Degrade-priority override handling | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0034/spec.md | M | Medium |
| D-0035 | T04.09 | R-035 | Budget realism caveat/reporting | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0035/spec.md | S | Low |
| D-0036 | T04.10 | R-036 | Report depth modes (summary/standard/detailed) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0036/spec.md | M | Medium |
| D-0037 | T04.11 | R-037 | Resume semantics from checkpoints | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0037/spec.md | M | Medium |
| D-0038 | T04.12 | R-038 | Anti-lazy distribution and consistency guards | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0038/spec.md | M | Medium |
| D-0039 | T04.13 | R-039 | Final report section completeness checks | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0039/spec.md | M | Medium |
| D-0040 | T05.01 | R-040 | Full docs pass (--pass-docs) with 5-section output | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0040/spec.md | M | Medium |
| D-0041 | T05.02 | R-041 | Known-issues registry load/match/output | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0041/spec.md | M | Medium |
| D-0042 | T05.03 | R-042 | TTL/LRU lifecycle rules in registry behavior | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0042/spec.md | M | Medium |
| D-0043 | T05.04 | R-043 | ALREADY_TRACKED report section integration | LIGHT | Quick sanity check | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0043/spec.md | S | Low |
| D-0044 | T05.05 | R-044 | AC1-AC20 automated validation suite | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0044/spec.md | L | High |
| D-0045 | T05.06 | R-045 | Benchmark runs (small/medium/known-dead-code repo) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0045/spec.md | L | High |
| D-0046 | T05.07 | R-046 | Concurrent-run isolation validation | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0046/spec.md | M | High |
| D-0047 | T05.08 | R-047 | Non-determinism/limitations reporting | LIGHT | Quick sanity check | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0047/spec.md | S | Low |
| D-0048 | T05.09 | R-048 | Final release readiness decision record | STANDARD | Direct test execution | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0048/spec.md | S | Medium |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0001/ |
| R-002 | T01.02 | D-0002 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0002/ |
| R-003 | T01.03 | D-0003 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0003/ |
| R-004 | T01.04 | D-0004 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0004/ |
| R-005 | T01.05 | D-0005 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0005/ |
| R-006 | T01.06 | D-0006 | STRICT | 90% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0006/ |
| R-007 | T01.07 | D-0007 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0007/ |
| R-008 | T01.08 | D-0008 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0008/ |
| R-009 | T01.09 | D-0009 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0009/ |
| R-010 | T01.10 | D-0010 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0010/ |
| R-011 | T02.01 | D-0011 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0011/ |
| R-012 | T02.02 | D-0012 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0012/ |
| R-013 | T02.03 | D-0013 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0013/ |
| R-014 | T02.04 | D-0014 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0014/ |
| R-015 | T02.05 | D-0015 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0015/ |
| R-016 | T02.06 | D-0016 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0016/ |
| R-017 | T03.01 | D-0017 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0017/ |
| R-018 | T03.02 | D-0018 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0018/ |
| R-019 | T03.03 | D-0019 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0019/ |
| R-020 | T03.04 | D-0020 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0020/ |
| R-021 | T03.05 | D-0021 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0021/ |
| R-022 | T03.06 | D-0022 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0022/ |
| R-023 | T03.07 | D-0023 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0023/ |
| R-024 | T03.08 | D-0024 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0024/ |
| R-025 | T03.09 | D-0025 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0025/ |
| R-026 | T03.10 | D-0026 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0026/ |
| R-027 | T04.01 | D-0027 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0027/ |
| R-028 | T04.02 | D-0028 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0028/ |
| R-029 | T04.03 | D-0029 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0029/ |
| R-030 | T04.04 | D-0030 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0030/ |
| R-031 | T04.05 | D-0031 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0031/ |
| R-032 | T04.06 | D-0032 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0032/ |
| R-033 | T04.07 | D-0033 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0033/ |
| R-034 | T04.08 | D-0034 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0034/ |
| R-035 | T04.09 | D-0035 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0035/ |
| R-036 | T04.10 | D-0036 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0036/ |
| R-037 | T04.11 | D-0037 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0037/ |
| R-038 | T04.12 | D-0038 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0038/ |
| R-039 | T04.13 | D-0039 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0039/ |
| R-040 | T05.01 | D-0040 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0040/ |
| R-041 | T05.02 | D-0041 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0041/ |
| R-042 | T05.03 | D-0042 | STRICT | 80% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0042/ |
| R-043 | T05.04 | D-0043 | LIGHT | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0043/ |
| R-044 | T05.05 | D-0044 | STRICT | 90% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0044/ |
| R-045 | T05.06 | D-0045 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0045/ |
| R-046 | T05.07 | D-0046 | STRICT | 85% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0046/ |
| R-047 | T05.08 | D-0047 | LIGHT | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0047/ |
| R-048 | T05.09 | D-0048 | STANDARD | 75% | .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/artifacts/D-0048/ |

## Execution Log Template

**Intended Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

For each checkpoint created under Section 4.8, execution must produce one report using this template.

**Template:**

```
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/checkpoints/<deterministic-name>.md
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
- <reference T<PP>.<TT> and D-####>

## Evidence
- .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/evidence/<artifact>
```

## Feedback Collection Template

**Intended Path:** .dev/releases/current/cleanup-audit-v2-UNIFIED-SPEC/tasklist/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

## Generation Notes

- Phase bucketing used explicit milestone dependency graph rather than top-level headings
- Milestones M1+M2 combined into Phase 1 (both P0, M2 depends on M1)
- Milestones M4+M5 combined into Phase 3 (linear dependency, both P1 structural/synthesis)
- Milestones M6+M7+M8 combined into Phase 4 (M7 depends on M3-M5, M6/M8 are sequential)
- Milestones M9+M10 combined into Phase 5 (final acceptance and optional extensions)
- No clarification tasks needed; all roadmap items have sufficient specificity
- No XL effort tasks detected; no subtask splitting required
