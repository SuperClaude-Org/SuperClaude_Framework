# TASKLIST — sc:roadmap v2: Redesigned Planning Pipeline

## Metadata & Artifact Paths

- **TASKLIST_ROOT**: `.dev/releases/current/v2.0-roadmap-v2/`
- **Tasklist Path**: `.dev/releases/current/v2.0-roadmap-v2/tasklist-overview.md`
- **Phase Files**: `tasklist-p1.md` through `tasklist-p7.md`
- **Execution Log Path**: `.dev/releases/current/v2.0-roadmap-v2/execution-log.md`
- **Checkpoint Reports Path**: `.dev/releases/current/v2.0-roadmap-v2/checkpoints/`
- **Evidence Root**: `.dev/releases/current/v2.0-roadmap-v2/evidence/`
- **Artifacts Root**: `.dev/releases/current/v2.0-roadmap-v2/artifacts/`
- **Feedback Log Path**: `.dev/releases/current/v2.0-roadmap-v2/feedback-log.md`
- **Generated**: 2026-02-21
- **Generator**: Tasklist Generator v2.2 (Deterministic, Value-Preserving)
- **Source Roadmap**: `.dev/releases/current/v2.0-roadmap-v2/roadmap.md`
- **Supplementary Spec**: `.dev/releases/current/v2.0-roadmap-v2/SC-ROADMAP-V2-SPEC.md`
- **Total Phases**: 7
- **Total Tasks**: 38
- **Total Deliverables**: 38
- **Total Roadmap Items**: 38
- **Priority Waves**: P0 (Phases 1-2), P1 (Phases 3-6), P2 (Phase 7)

## Source Snapshot

- Roadmap implements SC-ROADMAP-V2-SPEC v2.0.0 for the sc:roadmap command redesign
- 5-wave architecture (Wave 0-4) with lean SKILL.md (~400 lines) + 5 refs/ files
- 7 milestones: 2 P0 (foundation + extraction), 4 P1 (generation, adversarial, validation, interface), 1 P2 (polish)
- 38 deliverables across domains: backend (53%), architecture (29%), quality (12%), frontend (6%)
- Key integrations: sc:adversarial (multi-spec/multi-roadmap), Serena MCP (session persistence), sc:save/sc:load (resumability)
- Complexity score: 0.645 (MEDIUM), primary persona: architect

## Deterministic Rules Applied

1. **Phase mapping**: 7 milestones (M1-M7) → 7 sequential phases (Phase 1-7) preserving roadmap order
2. **Task ID scheme**: `T<PP>.<TT>` where PP = phase number (2-digit), TT = task number within phase (2-digit)
3. **Roadmap Item IDs**: R-001 through R-038, one per deliverable in appearance order (R-038 added via spec-panel P0 review)
4. **Deliverable IDs**: D-0001 through D-0038, one primary deliverable per task in task order
5. **Checkpoint cadence**: After every 5 tasks within a phase + end-of-phase checkpoint
6. **No splits applied**: Each deliverable maps to exactly 1 task (no independently deliverable sub-outputs detected per Section 4.4 criteria)
7. **Effort scoring**: Deterministic EFFORT_SCORE from text length (≥120 chars: +1), splits (+1), keywords (+1), dependency words (+1) → XS/S/M/L/XL
8. **Risk scoring**: Deterministic RISK_SCORE from security (+2), migration/data (+2), auth (+1), performance (+1), cross-cutting (+1) → Low/Medium/High
9. **Tier classification**: Keyword matching with compound phrase overrides, context boosters, priority order STRICT > EXEMPT > LIGHT > STANDARD
10. **Verification routing**: STRICT → sub-agent, STANDARD → direct test, LIGHT → sanity check, EXEMPT → skip
11. **MCP requirements**: STRICT requires Sequential + Serena; STANDARD prefers Sequential + Context7; LIGHT/EXEMPT have no requirements
12. **Clarification tasks**: None generated (all deliverables have complete acceptance criteria in roadmap)

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (≤ 20 words) |
|---|---|---|
| R-001 | Phase 1 | Lean SKILL.md (~400 lines) with wave orchestration instructions |
| R-002 | Phase 1 | refs/extraction-pipeline.md with 8-step extraction + chunked protocol |
| R-003 | Phase 1 | refs/scoring.md with complexity + template compatibility scoring |
| R-004 | Phase 1 | refs/templates.md with 4-tier discovery + inline generation |
| R-005 | Phase 1 | refs/validation.md with agent prompts + score aggregation |
| R-006 | Phase 2 | Wave 0: spec file validation, output dir setup, collision detection (-N suffix) |
| R-007 | Phase 2 | Wave 0: model identifier validation for --agents flag |
| R-008 | Phase 2 | Wave 1B: 8-step extraction pipeline (title → FRs → NFRs → scope → deps → success criteria → risks → IDs) |
| R-009 | Phase 2 | Wave 1B: domain classification with keyword weighting |
| R-010 | Phase 2 | Wave 1B: complexity scoring (5-factor weighted formula) |
| R-011 | Phase 2 | Wave 1B: chunked extraction for >500 line specs |
| R-012 | Phase 3 | Wave 2: template discovery (4-tier search) with compatibility scoring |
| R-013 | Phase 3 | Wave 2: milestone extraction with dependency mapping |
| R-014 | Phase 3 | Wave 2: effort estimation per milestone |
| R-015 | Phase 3 | Wave 3: roadmap.md generation with full body template |
| R-016 | Phase 3 | Wave 3: test-strategy.md generation (authored by SKILL.md, hardened) |
| R-017 | Phase 3 | Wave 3: YAML frontmatter generation with all required fields |
| R-018 | Phase 4 | refs/adversarial-integration.md with mode detection + invocation patterns |
| R-019 | Phase 4 | Wave 1A: multi-spec consolidation via sc:adversarial --compare |
| R-020 | Phase 4 | Wave 1A: multi-roadmap generation via sc:adversarial --generate |
| R-021 | Phase 4 | Agent specification parsing (model:persona:"instruction" format) |
| R-022 | Phase 4 | --interactive flag propagation to sc:adversarial |
| R-023 | Phase 5 | quality-engineer agent dispatch with completeness/consistency/traceability checks |
| R-024 | Phase 5 | self-review agent dispatch with 4-question protocol |
| R-025 | Phase 5 | Score aggregation formula producing PASS/REVISE/REJECT |
| R-026 | Phase 5 | REVISE loop: Wave 3 → Wave 4 re-execution (max 2 iterations) |
| R-027 | Phase 5 | test-strategy.md validation criteria in Wave 4 |
| R-028 | Phase 5 | --no-validate flag support |
| R-029 | Phase 6 | Updated roadmap.md command file with all flags |
| R-030 | Phase 6 | Updated examples covering single-spec, multi-spec, multi-roadmap, combined, model-only |
| R-031 | Phase 6 | sc:save integration at wave boundaries |
| R-032 | Phase 6 | sc:load resume protocol with spec-hash mismatch detection |
| R-033 | Phase 6 | Progress reporting at wave boundaries |
| R-034 | Phase 7 | Combined mode: chains multi-spec consolidation → multi-roadmap generation |
| R-035 | Phase 7 | Interactive mode user prompts at all decision points |
| R-036 | Phase 7 | --dry-run flag: preview roadmap structure without writing files |
| R-037 | Phase 7 | Edge case handling: empty specs, invalid YAML, circular dependencies |
| R-038 | Phase 1 | Minimal roadmap.md command file for integration testing (spec-panel M3) |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Lean SKILL.md behavioral instructions file | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0001/spec.md` | S | Low |
| D-0002 | T01.02 | R-002 | Extraction pipeline reference document | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0002/spec.md` | S | Low |
| D-0003 | T01.03 | R-003 | Scoring formulas reference document | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0003/spec.md` | XS | Low |
| D-0004 | T01.04 | R-004 | Template discovery reference document | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0004/spec.md` | XS | Low |
| D-0005 | T01.05 | R-005 | Validation agent prompts reference document | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0005/spec.md` | XS | Low |
| D-0006 | T02.01 | R-006 | Wave 0 spec validation and collision detection | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0006/spec.md` | S | Low |
| D-0007 | T02.02 | R-007 | Wave 0 model identifier validation | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0007/spec.md` | XS | Low |
| D-0008 | T02.03 | R-008 | Wave 1B 8-step extraction pipeline implementation | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0008/spec.md` | S | Low |
| D-0009 | T02.04 | R-009 | Domain classification with keyword weighting | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0009/spec.md` | XS | Low |
| D-0010 | T02.05 | R-010 | Complexity scoring implementation | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0010/spec.md` | XS | Low |
| D-0011 | T02.06 | R-011 | Chunked extraction protocol for large specs | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0011/spec.md` | M | Low |
| D-0012 | T03.01 | R-012 | Template discovery with 4-tier search | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0012/spec.md` | S | Low |
| D-0013 | T03.02 | R-013 | Milestone extraction with dependency mapping | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0013/spec.md` | S | Low |
| D-0014 | T03.03 | R-014 | Effort estimation per milestone | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0014/spec.md` | XS | Low |
| D-0015 | T03.04 | R-015 | roadmap.md body generation with full template | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0015/spec.md` | M | Low |
| D-0016 | T03.05 | R-016 | test-strategy.md generation with interleave ratio | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0016/spec.md` | M | Low |
| D-0017 | T03.06 | R-017 | YAML frontmatter generation with schema contract | STRICT | Sub-agent | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0017/spec.md` | S | Medium |
| D-0018 | T04.01 | R-018 | Adversarial integration reference document | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0018/spec.md` | S | Low |
| D-0019 | T04.02 | R-019 | Multi-spec consolidation via sc:adversarial | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0019/spec.md` | M | Medium |
| D-0020 | T04.03 | R-020 | Multi-roadmap generation via sc:adversarial | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0020/spec.md` | M | Medium |
| D-0021 | T04.04 | R-021 | Agent specification parsing implementation | STRICT | Sub-agent | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0021/spec.md` | S | Low |
| D-0022 | T04.05 | R-022 | Interactive flag propagation | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0022/spec.md` | XS | Low |
| D-0023 | T05.01 | R-023 | quality-engineer agent dispatch | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0023/spec.md` | S | Low |
| D-0024 | T05.02 | R-024 | self-review agent dispatch with 4-question protocol | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0024/spec.md` | S | Low |
| D-0025 | T05.03 | R-025 | Score aggregation formula implementation | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0025/spec.md` | XS | Low |
| D-0026 | T05.04 | R-026 | REVISE loop with max 2 iterations | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0026/spec.md` | M | Medium |
| D-0027 | T05.05 | R-027 | test-strategy.md validation criteria | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0027/spec.md` | S | Low |
| D-0028 | T05.06 | R-028 | --no-validate flag implementation | LIGHT | Sanity check | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0028/spec.md` | XS | Low |
| D-0029 | T06.01 | R-029 | Updated command file with all flags | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0029/spec.md` | S | Low |
| D-0030 | T06.02 | R-030 | Updated usage examples | LIGHT | Sanity check | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0030/spec.md` | XS | Low |
| D-0031 | T06.03 | R-031 | sc:save integration at wave boundaries | STRICT | Sub-agent | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0031/spec.md` | M | Medium |
| D-0032 | T06.04 | R-032 | sc:load resume protocol | STRICT | Sub-agent | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0032/spec.md` | M | Medium |
| D-0033 | T06.05 | R-033 | Progress reporting at wave boundaries | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0033/spec.md` | XS | Low |
| D-0034 | T07.01 | R-034 | Combined mode chaining implementation | STRICT | Sub-agent | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0034/spec.md` | M | Medium |
| D-0035 | T07.02 | R-035 | Interactive mode user prompts | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0035/spec.md` | S | Low |
| D-0036 | T07.03 | R-036 | --dry-run flag implementation | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0036/spec.md` | S | Low |
| D-0037 | T07.04 | R-037 | Edge case handling implementation | STANDARD | Direct test | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0037/spec.md` | M | Medium |
| D-0038 | T01.06 | R-038 | Minimal command file for integration testing | LIGHT | Sanity check | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0038/spec.md` | XS | Low |

## Tasklist Index

| Phase | Phase Name | Task IDs | Primary Outcome | Tier Distribution |
|---|---|---:|---|---|
| Phase 1 | Architecture Foundation | T01.01–T01.06 | Lean SKILL.md + 4 refs/ reference documents + minimal command file | STRICT: 0, STANDARD: 5, LIGHT: 1, EXEMPT: 0 |
| Phase 2 | Extraction Pipeline | T02.01–T02.06 | Wave 0 prerequisites + Wave 1B extraction pipeline | STRICT: 0, STANDARD: 6, LIGHT: 0, EXEMPT: 0 |
| Phase 3 | Core Generation Pipeline | T03.01–T03.06 | Wave 2 planning + Wave 3 artifact generation | STRICT: 1, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| Phase 4 | Adversarial Integration | T04.01–T04.05 | Wave 1A adversarial modes + integration ref doc | STRICT: 1, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |
| Phase 5 | Validation & Quality Gates | T05.01–T05.06 | Wave 4 validation agents + REVISE loop | STRICT: 0, STANDARD: 5, LIGHT: 1, EXEMPT: 0 |
| Phase 6 | Command Interface & Session | T06.01–T06.05 | Command file + session persistence + progress | STRICT: 2, STANDARD: 2, LIGHT: 1, EXEMPT: 0 |
| Phase 7 | Polish & Combined Mode | T07.01–T07.04 | Combined mode + interactive + edge cases | STRICT: 1, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0001/` |
| R-002 | T01.02 | D-0002 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0002/` |
| R-003 | T01.03 | D-0003 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0003/` |
| R-004 | T01.04 | D-0004 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0004/` |
| R-005 | T01.05 | D-0005 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0005/` |
| R-006 | T02.01 | D-0006 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0006/` |
| R-007 | T02.02 | D-0007 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0007/` |
| R-008 | T02.03 | D-0008 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0008/` |
| R-009 | T02.04 | D-0009 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0009/` |
| R-010 | T02.05 | D-0010 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0010/` |
| R-011 | T02.06 | D-0011 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0011/` |
| R-012 | T03.01 | D-0012 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0012/` |
| R-013 | T03.02 | D-0013 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0013/` |
| R-014 | T03.03 | D-0014 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0014/` |
| R-015 | T03.04 | D-0015 | STANDARD | [███████░░░] 70% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0015/` |
| R-016 | T03.05 | D-0016 | STANDARD | [███████░░░] 70% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0016/` |
| R-017 | T03.06 | D-0017 | STRICT | [███████░░░] 72% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0017/` |
| R-018 | T04.01 | D-0018 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0018/` |
| R-019 | T04.02 | D-0019 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0019/` |
| R-020 | T04.03 | D-0020 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0020/` |
| R-021 | T04.04 | D-0021 | STRICT | [█████░░░░░] 52% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0021/` |
| R-022 | T04.05 | D-0022 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0022/` |
| R-023 | T05.01 | D-0023 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0023/` |
| R-024 | T05.02 | D-0024 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0024/` |
| R-025 | T05.03 | D-0025 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0025/` |
| R-026 | T05.04 | D-0026 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0026/` |
| R-027 | T05.05 | D-0027 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0027/` |
| R-028 | T05.06 | D-0028 | LIGHT | [████████░░] 78% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0028/` |
| R-029 | T06.01 | D-0029 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0029/` |
| R-030 | T06.02 | D-0030 | LIGHT | [████████░░] 78% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0030/` |
| R-031 | T06.03 | D-0031 | STRICT | [███████░░░] 72% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0031/` |
| R-032 | T06.04 | D-0032 | STRICT | [███████░░░] 72% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0032/` |
| R-033 | T06.05 | D-0033 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0033/` |
| R-034 | T07.01 | D-0034 | STRICT | [███████░░░] 72% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0034/` |
| R-035 | T07.02 | D-0035 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0035/` |
| R-036 | T07.03 | D-0036 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0036/` |
| R-037 | T07.04 | D-0037 | STANDARD | [██████░░░░] 60% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0037/` |
| R-038 | T01.06 | D-0038 | LIGHT | [████████░░] 78% | `.dev/releases/current/v2.0-roadmap-v2/artifacts/D-0038/` |

## Execution Log Template

**Intended Path:** `.dev/releases/current/v2.0-roadmap-v2/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| _to be filled during execution_ | | | | | | | |

## Checkpoint Report Template

For each checkpoint created within phase files, execution must produce one report using this template:

- `# Checkpoint Report — <Checkpoint Title>`
- `**Checkpoint Report Path:** .dev/releases/current/v2.0-roadmap-v2/checkpoints/<deterministic-name>.md`
- `**Scope:** <tasks covered>`
- `## Status`
  - `Overall: Pass | Fail | TBD`
- `## Verification Results` (exactly 3 bullets)
  - ...
- `## Exit Criteria Assessment` (exactly 3 bullets)
  - ...
- `## Issues & Follow-ups`
  - List blocking issues; reference `T<PP>.<TT>` and `D-####`
- `## Evidence`
  - Bullet list of intended evidence paths under `.dev/releases/current/v2.0-roadmap-v2/evidence/`

## Feedback Collection Template

**Intended Path:** `.dev/releases/current/v2.0-roadmap-v2/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤ 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| _to be filled during execution_ | | | | | | |

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification (e.g., "Involved auth paths", "Actually trivial")
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`

---

**End of Overview** | Total Tasks: 38 | Total Deliverables: 38 | Phases: 7 | STRICT: 5, STANDARD: 27, LIGHT: 4, EXEMPT: 0
