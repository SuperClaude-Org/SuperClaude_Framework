# TASKLIST INDEX -- Cross-Framework Deep Analysis

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | Cross-Framework Deep Analysis |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-14 |
| TASKLIST_ROOT | `.dev/releases/current/cross-framework-deep-analysis/` |
| Total Phases | 9 |
| Total Tasks | 38 |
| Total Deliverables | 38 |
| Complexity Class | HIGH |
| Primary Persona | analyzer |
| Consulting Personas | architect, qa, security-engineer |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `.dev/releases/current/cross-framework-deep-analysis/tasklist-index.md` |
| Phase 1 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-1-tasklist.md` |
| Phase 2 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-2-tasklist.md` |
| Phase 3 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-3-tasklist.md` |
| Phase 4 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-4-tasklist.md` |
| Phase 5 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-5-tasklist.md` |
| Phase 6 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-6-tasklist.md` |
| Phase 7 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-7-tasklist.md` |
| Phase 8 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-8-tasklist.md` |
| Phase 9 Tasklist | `.dev/releases/current/cross-framework-deep-analysis/phase-9-tasklist.md` |
| Execution Log | `.dev/releases/current/cross-framework-deep-analysis/execution-log.md` |
| Checkpoint Reports | `.dev/releases/current/cross-framework-deep-analysis/checkpoints/` |
| Evidence Directory | `.dev/releases/current/cross-framework-deep-analysis/evidence/` |
| Artifacts Directory | `.dev/releases/current/cross-framework-deep-analysis/artifacts/` |
| Validation Reports | `.dev/releases/current/cross-framework-deep-analysis/validation/` |
| Feedback Log | `.dev/releases/current/cross-framework-deep-analysis/feedback-log.md` |

---

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Pre-Sprint Setup | T01.01-T01.07 | STANDARD: 4, EXEMPT: 3 |
| 2 | phase-2-tasklist.md | Component Inventory and Mapping | T02.01-T02.04 | STRICT: 1, STANDARD: 2, EXEMPT: 1 |
| 3 | phase-3-tasklist.md | IronClaude Strategy Extraction | T03.01-T03.03 | STRICT: 1, STANDARD: 2 |
| 4 | phase-4-tasklist.md | llm-workflows Strategy Extraction | T04.01-T04.03 | STRICT: 1, STANDARD: 2 |
| 5 | phase-5-tasklist.md | Adversarial Comparisons | T05.01-T05.04 | STRICT: 4 |
| 6 | phase-6-tasklist.md | Strategy Synthesis | T06.01-T06.04 | STRICT: 1, STANDARD: 3 |
| 7 | phase-7-tasklist.md | Improvement Planning | T07.01-T07.04 | STRICT: 2, STANDARD: 2 |
| 8 | phase-8-tasklist.md | Adversarial Validation | T08.01-T08.05 | STRICT: 5 |
| 9 | phase-9-tasklist.md | Consolidated Outputs | T09.01-T09.04 | STRICT: 2, STANDARD: 2 |

---

## Source Snapshot

- 9-phase analytical sprint comparing IronClaude quality-enforcement layer against `llm-workflows` framework
- Produces 35+ artifacts culminating in a machine-readable improvement backlog for v3.0 planning
- Strictly analytical — no production code changes in scope
- Three cross-cutting invariants enforced across all artifacts: Auggie MCP evidence, anti-sycophancy, adopt-patterns-not-mass
- Sequential phase-gate architecture with halt-on-failure semantics; any single gate failure blocks all downstream work
- Estimated ~172K tokens total; 38 hours sequential / 34 hours with Phase 3/4 parallelism

---

## Deterministic Rules Applied

- **Phase renumbering**: Phase 0–8 from roadmap renumbered to Phase 1–9 sequentially (no gaps, appearance order)
- **Task ID scheme**: T<PP>.<TT> zero-padded 2-digit format; 1:1 mapping from roadmap items (no splits triggered)
- **Checkpoint cadence**: After every 5 tasks within a phase + mandatory end-of-phase checkpoint
- **Clarification task rule**: No clarification tasks inserted (all roadmap items are sufficiently specified)
- **Deliverable registry**: 38 deliverables D-0001–D-0038 in task appearance order
- **Effort mapping**: EFFORT_SCORE computed from text length, keywords, dependency words; mapped to XS/S/M/L/XL
- **Risk mapping**: RISK_SCORE computed from security/data/auth/scope keywords; mapped to Low/Medium/High
- **Tier classification algorithm**: Compound phrase check → keyword matching → context boosters → priority STRICT>EXEMPT>LIGHT>STANDARD
- **Verification routing**: STRICT→sub-agent(quality-engineer)/60s; STANDARD→direct test/30s; EXEMPT→skip/0s
- **MCP requirements**: STRICT tasks require Sequential+Serena; STANDARD tasks prefer Sequential+Context7
- **Traceability matrix**: Every R-### mapped to T<PP>.<TT> → D-#### → artifact paths → Tier → Confidence
- **Multi-file output**: 9 phase files + 1 index = 10 files total (generation); up to 2 additional validation artifacts

---

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | Verify Auggie MCP connectivity to both repositories: IronClaude and llm-workflows |
| R-002 | Phase 1 | Confirm `superclaude sprint run` CLI is functional with `--start`/`--end` flags via no-op phase test |
| R-003 | Phase 1 | Create `artifacts/` output directory structure; verify `artifacts/prompt.md` exists and is readable |
| R-004 | Phase 1 | Record dependency readiness state for: Auggie MCP, IronClaude repo, llm-workflows repo, prompt/source documents |
| R-005 | Phase 1 | Resolve OQ-006 (executor parallelism capability) — determines Phase 2/3 scheduling |
| R-006 | Phase 1 | Resolve OQ-008 (Auggie MCP unavailability definition) — apply merged multi-criteria definition |
| R-007 | Phase 1 | Create phase tasklists `phase-{1..8}-tasklist.md` and `tasklist-index.md` |
| R-008 | Phase 2 | T01.01 — Auggie MCP discovery against IronClaude for all 8 component groups |
| R-009 | Phase 2 | T01.02 — Verify all llm-workflows paths from `artifacts/prompt.md` against llm-workflows via Auggie MCP |
| R-010 | Phase 2 | T01.03 — Produce `component-map.md` with ≥8 IC-to-LW mappings; annotate IC-only components |
| R-011 | Phase 2 | T01.04 — Resolve OQ-002 (pipeline-analysis granularity): keep as single group unless Phase 1 reveals >3 |
| R-012 | Phase 3 | For each of the 8 IC component groups, produce `strategy-ic-*.md` documenting design philosophy |
| R-013 | Phase 3 | Enforce anti-sycophancy (NFR-002): every strength claim must have a paired weakness/trade-off |
| R-014 | Phase 3 | Attach `file:line` evidence from Auggie MCP to all claims (NFR-003) |
| R-015 | Phase 4 | For each of 11 LW components from `artifacts/prompt.md`, produce `strategy-lw-*.md` |
| R-016 | Phase 4 | Restrict analysis to the prompt-defined component list plus verified paths from Phase 1 |
| R-017 | Phase 4 | Anti-sycophancy and evidence rules enforced identically to Phase 2 |
| R-018 | Phase 5 | For each of 8 defined comparison pairs, run `/sc:adversarial` producing `comparison-*.md` |
| R-019 | Phase 5 | For "no clear winner" verdicts: require explicit condition-specific reasoning |
| R-020 | Phase 5 | Resolve OQ-004: for "discard both" verdicts, Phase 6 shall default to producing IC-native improvement item |
| R-021 | Phase 5 | Resolve OQ-007: cap comparison pairs at 8 unless Phase 1 inventory reveals a critical gap |
| R-022 | Phase 6 | Synthesize all 8 comparison verdicts into `merged-strategy.md` |
| R-023 | Phase 6 | Organize cross-component guidance under five architectural principles with component references |
| R-024 | Phase 6 | Include explicit "rigor without bloat" section; document all discard decisions with justification |
| R-025 | Phase 6 | Run internal contradiction review; verify no orphaned component areas |
| R-026 | Phase 7 | For each of 8 IC component groups, produce `improve-*.md` with improvement plan items |
| R-027 | Phase 7 | Apply structural leverage priority ordering to all improvement items |
| R-028 | Phase 7 | Produce `improve-master.md` with cross-component dependency graph isolating prerequisites |
| R-029 | Phase 7 | For "discard both" verdict items: produce IC-native improvement items per OQ-004 resolution |
| R-030 | Phase 8 | Pre-gate action: validate `/sc:roadmap` schema against `improvement-backlog.md` schema before Phase 8 |
| R-031 | Phase 8 | Execute formal architecture review gate by independent Validation reviewer, not Architect lead |
| R-032 | Phase 8 | Validate for: file path existence, anti-sycophancy coverage, patterns-not-mass compliance, completeness |
| R-033 | Phase 8 | Produce `validation-report.md` with per-item pass/fail status |
| R-034 | Phase 8 | Correct all failures; produce `final-improve-plan.md` |
| R-035 | Phase 9 | Produce all 4 final artifacts concurrently: artifact-index.md, rigor-assessment.md, improvement-backlog.md |
| R-036 | Phase 9 | Verify mandatory resume testing: sprint SHALL NOT complete unless `--start 3` with Phase 1–2 artifacts passes |
| R-037 | Phase 9 | Resolve OQ-003 — confirm FR-XFDA-001 registration is sufficient for roadmap linking |
| R-038 | Phase 9 | Resolve OQ-005 — produce lightweight schema validator script or document manual validation protocol |

---

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Auggie MCP connectivity confirmation | EXEMPT | Skip | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0001/evidence.md` | S | Low |
| D-0002 | T01.02 | R-002 | CLI executor functional confirmation | EXEMPT | Skip | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0002/evidence.md` | S | Low |
| D-0003 | T01.03 | R-003 | artifacts/ directory + prompt.md verification | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0003/evidence.md` | S | Low |
| D-0004 | T01.04 | R-004 | Dependency readiness document | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0004/spec.md` | S | Low |
| D-0005 | T01.05 | R-005 | OQ-006 resolution decision record | EXEMPT | Skip | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0005/notes.md` | XS | Low |
| D-0006 | T01.06 | R-006 | OQ-008 resolution decision record | EXEMPT | Skip | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0006/notes.md` | XS | Low |
| D-0007 | T01.07 | R-007 | Phase tasklist files + tasklist-index.md | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0007/evidence.md` | S | Low |
| D-0008 | T02.01 | R-008 | IC component inventory (8 groups) with file paths | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0008/spec.md` | M | Medium |
| D-0009 | T02.02 | R-009 | LW path verification with dual-status tracking | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0009/spec.md` | M | Medium |
| D-0010 | T02.03 | R-010 | component-map.md with ≥8 IC-to-LW mappings | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0010/spec.md` | M | Low |
| D-0011 | T02.04 | R-011 | OQ-002 resolution with pipeline-analysis decision | EXEMPT | Skip | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0011/notes.md` | XS | Low |
| D-0012 | T03.01 | R-012 | 8 x strategy-ic-*.md files | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0012/spec.md` | L | Medium |
| D-0013 | T03.02 | R-013 | Anti-sycophancy compliance log for IC strategies | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0013/evidence.md` | S | Low |
| D-0014 | T03.03 | R-014 | file:line evidence citations attached to IC strategies | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0014/evidence.md` | M | Medium |
| D-0015 | T04.01 | R-015 | 11 x strategy-lw-*.md files | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0015/spec.md` | L | Medium |
| D-0016 | T04.02 | R-016 | Scope restriction confirmation log | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0016/evidence.md` | S | Low |
| D-0017 | T04.03 | R-017 | Anti-sycophancy and evidence compliance log for LW | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0017/evidence.md` | S | Medium |
| D-0018 | T05.01 | R-018 | 8 x comparison-*.md files via /sc:adversarial | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0018/spec.md` | L | High |
| D-0019 | T05.02 | R-019 | "No clear winner" verdict justification records | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0019/notes.md` | S | Medium |
| D-0020 | T05.03 | R-020 | OQ-004 resolution: discard-both handling decision | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0020/notes.md` | XS | Low |
| D-0021 | T05.04 | R-021 | OQ-007 resolution: comparison pair count decision | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0021/notes.md` | XS | Low |
| D-0022 | T06.01 | R-022 | merged-strategy.md | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0022/spec.md` | L | Medium |
| D-0023 | T06.02 | R-023 | Five-principle sections in merged-strategy.md | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0023/evidence.md` | M | Low |
| D-0024 | T06.03 | R-024 | Rigor-without-bloat section + discard decisions | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0024/notes.md` | S | Low |
| D-0025 | T06.04 | R-025 | Contradiction review report + orphan check | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0025/evidence.md` | S | Medium |
| D-0026 | T07.01 | R-026 | 8 x improve-*.md component improvement plan files | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0026/spec.md` | L | Medium |
| D-0027 | T07.02 | R-027 | Priority-ordered improvement items per structural leverage | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0027/evidence.md` | S | Low |
| D-0028 | T07.03 | R-028 | improve-master.md with cross-component dependency graph | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0028/spec.md` | M | Medium |
| D-0029 | T07.04 | R-029 | IC-native improvement items for "discard both" verdicts | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0029/evidence.md` | S | Low |
| D-0030 | T08.01 | R-030 | /sc:roadmap schema pre-validation report | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0030/spec.md` | S | Medium |
| D-0031 | T08.02 | R-031 | Formal architecture review gate execution record | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0031/evidence.md` | M | High |
| D-0032 | T08.03 | R-032 | Six-dimension validation pass results | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0032/evidence.md` | M | High |
| D-0033 | T08.04 | R-033 | validation-report.md with per-item pass/fail | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0033/spec.md` | M | Medium |
| D-0034 | T08.05 | R-034 | final-improve-plan.md with all corrections applied | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0034/spec.md` | M | Medium |
| D-0035 | T09.01 | R-035 | 4 final artifacts: artifact-index.md, rigor-assessment.md, improvement-backlog.md, sprint-summary.md | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0035/spec.md` | L | Medium |
| D-0036 | T09.02 | R-036 | Resume test pass record (--start 3 with Phase 1-2 artifacts) | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0036/evidence.md` | S | Medium |
| D-0037 | T09.03 | R-037 | OQ-003 resolution: FR-XFDA-001 registration decision | EXEMPT | Skip | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0037/notes.md` | XS | Low |
| D-0038 | T09.04 | R-038 | Schema validator script or manual validation protocol | STANDARD | Direct test | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0038/spec.md` | S | Low |

---

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | EXEMPT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0001/evidence.md` |
| R-002 | T01.02 | D-0002 | EXEMPT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0002/evidence.md` |
| R-003 | T01.03 | D-0003 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0003/evidence.md` |
| R-004 | T01.04 | D-0004 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0004/spec.md` |
| R-005 | T01.05 | D-0005 | EXEMPT | [█████████-] 90% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0005/notes.md` |
| R-006 | T01.06 | D-0006 | EXEMPT | [█████████-] 90% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0006/notes.md` |
| R-007 | T01.07 | D-0007 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0007/evidence.md` |
| R-008 | T02.01 | D-0008 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0008/spec.md` |
| R-009 | T02.02 | D-0009 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0009/spec.md` |
| R-010 | T02.03 | D-0010 | STANDARD | [███████---] 75% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0010/spec.md` |
| R-011 | T02.04 | D-0011 | EXEMPT | [█████████-] 90% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0011/notes.md` |
| R-012 | T03.01 | D-0012 | STANDARD | [███████---] 74% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0012/spec.md` |
| R-013 | T03.02 | D-0013 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0013/evidence.md` |
| R-014 | T03.03 | D-0014 | STRICT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0014/evidence.md` |
| R-015 | T04.01 | D-0015 | STANDARD | [███████---] 74% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0015/spec.md` |
| R-016 | T04.02 | D-0016 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0016/evidence.md` |
| R-017 | T04.03 | D-0017 | STRICT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0017/evidence.md` |
| R-018 | T05.01 | D-0018 | STRICT | [█████████-] 88% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0018/spec.md` |
| R-019 | T05.02 | D-0019 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0019/notes.md` |
| R-020 | T05.03 | D-0020 | STRICT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0020/notes.md` |
| R-021 | T05.04 | D-0021 | STRICT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0021/notes.md` |
| R-022 | T06.01 | D-0022 | STANDARD | [███████---] 74% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0022/spec.md` |
| R-023 | T06.02 | D-0023 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0023/evidence.md` |
| R-024 | T06.03 | D-0024 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0024/notes.md` |
| R-025 | T06.04 | D-0025 | STRICT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0025/evidence.md` |
| R-026 | T07.01 | D-0026 | STANDARD | [███████---] 74% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0026/spec.md` |
| R-027 | T07.02 | D-0027 | STANDARD | [███████---] 72% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0027/evidence.md` |
| R-028 | T07.03 | D-0028 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0028/spec.md` |
| R-029 | T07.04 | D-0029 | STRICT | [████████--] 80% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0029/evidence.md` |
| R-030 | T08.01 | D-0030 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0030/spec.md` |
| R-031 | T08.02 | D-0031 | STRICT | [█████████-] 88% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0031/evidence.md` |
| R-032 | T08.03 | D-0032 | STRICT | [█████████-] 88% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0032/evidence.md` |
| R-033 | T08.04 | D-0033 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0033/spec.md` |
| R-034 | T08.05 | D-0034 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0034/spec.md` |
| R-035 | T09.01 | D-0035 | STANDARD | [███████---] 74% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0035/spec.md` |
| R-036 | T09.02 | D-0036 | STRICT | [████████--] 82% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0036/evidence.md` |
| R-037 | T09.03 | D-0037 | EXEMPT | [█████████-] 90% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0037/notes.md` |
| R-038 | T09.04 | D-0038 | STANDARD | [███████---] 74% | `.dev/releases/current/cross-framework-deep-analysis/artifacts/D-0038/spec.md` |

---

## Execution Log Template

**Intended Path:** `.dev/releases/current/cross-framework-deep-analysis/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| (fill during execution) | T01.01 | EXEMPT | D-0001 | Verified Auggie MCP connectivity to both repos | Manual | TBD | `.dev/releases/current/cross-framework-deep-analysis/evidence/T01.01/` |

---

## Checkpoint Report Template

For each checkpoint, execution must produce one report at the path specified in the checkpoint block.

**Template:**
```
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** .dev/releases/current/cross-framework-deep-analysis/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>
## Status
- Overall: Pass | Fail | TBD
## Verification Results
- <verify bullet 1>
- <verify bullet 2>
- <verify bullet 3>
## Exit Criteria Assessment
- <exit criterion 1>
- <exit criterion 2>
- <exit criterion 3>
## Issues & Follow-ups
- (list blocking issues; reference T<PP>.<TT> and D-####)
## Evidence
- (bullet list of intended evidence paths under .dev/releases/current/cross-framework-deep-analysis/evidence/)
```

---

## Feedback Collection Template

**Intended Path:** `.dev/releases/current/cross-framework-deep-analysis/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| T01.01 | EXEMPT | | | | | |

---

## Generation Notes

- Phase 0 from source roadmap renumbered to Phase 1 (sequential numbering, no gaps)
- All roadmap items mapped 1:1 to tasks; no split triggers activated
- No Clarification Tasks required; all items were sufficiently specified
- TASKLIST_ROOT derived via Rule 1 match: `.dev/releases/current/cross-framework-deep-analysis/` found in roadmap text
- Gate SC-001 through SC-008 from roadmap are reflected as acceptance criteria in corresponding phase end-of-phase checkpoints
- Open Questions OQ-001 through OQ-008 are each represented as EXEMPT tasks or embedded within STANDARD/STRICT tasks

### Patch Regeneration: Phase 8 and Phase 9 (2026-03-14)

`phase-8-tasklist.md` and `phase-9-tasklist.md` regenerated from scratch with all ValidationReport patches applied. Phases 1-7 unchanged.

**Phase 8 patches applied:**
- H10: T08.03 Dimension 4 — corrected "Phase 2 components" to "Phase 1 components" (roadmap Key Action 3 item 4)
- H11: T08.03 — added four Disqualifying Conditions to steps and AC: (1) evidence unverifiable, (2) copied mass in adoption, (3) broken cross-artifact lineage, (4) implementation-scope drift; any triggered condition = Fail-Rework
- H12: T08.05 — added Auggie MCP file path verification step and AC criterion (Gate Criteria SC-007: "all file paths verified")
- M11: T08.01 — replaced invented "AC-010 schema" identifier with "schema expectations from the `/sc:roadmap` command definition"
- M12: T08.01 — added AC criterion: D-0030 findings are referenced in validation-report.md (D-0033) per Gate Criteria requirement
- M13: T08.04 — replaced "list of reworked items with corrections" in AC with "failed items listed with Fail classification and Disqualifying Condition reference for T08.05 consumption"
- M14: T08.05 — added AC criterion: final-improve-plan.md confirmed schema-compliant with `/sc:roadmap` expectations from D-0030
- L12: T08.02 — expanded AC gate scope to explicitly state "formal architecture review, not a formatting pass or compliance scan"

**Phase 9 patches applied:**
- H13: T09.02 — replaced failure branch AC with unconditional block: sprint completion blocked on failure; test MUST be re-executed and pass before T09.03/T09.04 proceed; removed language permitting sprint completion with a documented failure
- L13: T09.04 — added step 2 preference statement: script is the strongly preferred path; fallback to manual protocol requires explicit documentation of why script was not viable
