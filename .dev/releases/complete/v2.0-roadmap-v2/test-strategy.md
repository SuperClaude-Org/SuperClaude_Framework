---
spec_source: .dev/releases/current/v2.0-roadmap-v2/SC-ROADMAP-V2-SPEC.md
generated_by: sc:roadmap
generated_at: "2026-02-21"
complexity_class: MEDIUM
interleave_ratio: "1:2"
validation_philosophy: continuous_parallel
total_work_milestones: 7
total_validation_milestones: 4
---

# Test Strategy: sc:roadmap v2

## Validation Philosophy

This test strategy follows the **continuous parallel validation** philosophy: the default assumption is that work has deviated from the spec. A validation agent runs behind the work agent. Major issues trigger stop-and-fix. Validation milestones are interleaved with work milestones rather than deferred to the end.

### Interleave Ratio

**Complexity Class**: MEDIUM (score: 0.645)
**Interleave Ratio**: 1:2 (one validation milestone per two work milestones)

| Complexity | Ratio | Meaning |
|-----------|-------|---------|
| LOW (<0.4) | 1:3 | Validate after every 3rd work milestone |
| **MEDIUM (0.4-0.7)** | **1:2** | **Validate after every 2nd work milestone** |
| HIGH (>0.7) | 1:1 | Validate after every work milestone |

### Stop-and-Fix Thresholds

| Severity | Threshold | Action |
|----------|-----------|--------|
| Critical | Any single critical finding | Stop immediately. Fix before proceeding. |
| Major | ≥3 major findings in one validation pass | Stop. Review and fix all before proceeding. |
| Minor | ≥10 minor findings accumulated | Flag for batch fix at next validation milestone. |

## Validation Schedule

The 7 work milestones (M1-M7) are interleaved with 4 validation milestones (V1-V4) at a 1:2 ratio:

```
M1 (Architecture Foundation)    — P0
M2 (Extraction Pipeline)        — P0
  V1 (Validate Foundation + Extraction)
M3 (Core Generation Pipeline)   — P1
M4 (Adversarial Integration)    — P1
  V2 (Validate Generation + Adversarial)
M5 (Validation & Quality Gates) — P1
M6 (Command Interface & Session)— P1
  V3 (Validate Quality + Interface)
M7 (Polish & Combined Mode)     — P2
  V4 (Final Integration Validation)
```

## Validation Milestones

### V1: Foundation & Extraction Validation (after M1 + M2)

**Validates**: M1 (Architecture Foundation), M2 (Extraction Pipeline)

| Check | Description | Pass Criteria |
|-------|-------------|---------------|
| V1.1 | SKILL.md line count | ≤500 lines, no YAML pseudocode |
| V1.2 | refs/ directory completeness | 5 files present: extraction-pipeline.md, scoring.md, validation.md, templates.md, adversarial-integration.md |
| V1.3 | Ref cross-references | Every ref file name appears in SKILL.md at least once |
| V1.4 | On-demand loading | No wave loads >3 refs; verify per-wave ref lists |
| V1.5 | Wave 0 validation | Spec file validation, output dir setup, collision detection functional |
| V1.6 | Wave 1B extraction | 8-step pipeline produces valid extraction.md with all 9 sections |
| V1.7 | Domain classification | Keyword dictionaries produce correct domain percentages |
| V1.8 | Complexity scoring | 5-factor formula produces correct score and classification |
| V1.9 | Chunked extraction | >500 line spec triggers chunking; 4-pass verification passes |

**Stop-and-fix triggers**: V1.1 failure (SKILL.md too long), V1.2 failure (missing refs), V1.9 failure (extraction data loss)

### V2: Generation & Adversarial Validation (after M3 + M4)

**Validates**: M3 (Core Generation Pipeline), M4 (Adversarial Integration)

| Check | Description | Pass Criteria |
|-------|-------------|---------------|
| V2.1 | Template discovery | 4-tier search executes correctly; inline fallback works |
| V2.2 | Milestone structure | Each milestone has: ID, objective, deliverables with IDs, dependencies, risk assessment |
| V2.3 | roadmap.md body | Contains: Overview, Milestone Summary, Dependency Graph, per-milestone sections, Risk Register, Decision Summary |
| V2.4 | YAML frontmatter validity | Parseable by standard YAML parser; spec_source/spec_sources mutual exclusion |
| V2.5 | test-strategy.md quality | Interleave ratio matches complexity; validation milestones reference real work milestones |
| V2.6 | Decision Summary completeness | All 5 decision rows present with data-driven rationale |
| V2.7 | sc:adversarial invocation (multi-spec) | --compare invoked correctly; return contract consumed |
| V2.8 | sc:adversarial invocation (multi-roadmap) | --generate invoked correctly; agent specs parsed |
| V2.9 | Agent spec parsing | Model-only, mixed, full formats all parsed correctly; 2-10 range enforced |

**Stop-and-fix triggers**: V2.4 failure (invalid frontmatter), V2.7/V2.8 failure (adversarial integration broken)

### V3: Quality & Interface Validation (after M5 + M6)

**Validates**: M5 (Validation & Quality Gates), M6 (Command Interface & Session)

| Check | Description | Pass Criteria |
|-------|-------------|---------------|
| V3.1 | quality-engineer agent dispatch | Agent dispatched with correct prompt; produces score |
| V3.2 | self-review agent dispatch | 4-question protocol executed; produces score |
| V3.3 | Score aggregation | PASS ≥85%, REVISE 70-84%, REJECT <70% thresholds applied |
| V3.4 | REVISE loop | Wave 3 → Wave 4 re-execution works; max 2 iterations; PASS_WITH_WARNINGS fallback |
| V3.5 | --no-validate flag | Sets validation_score: 0.0, validation_status: SKIPPED |
| V3.6 | test-strategy validation criteria | Wave 4 checks interleave ratio, milestone refs, philosophy, stop-and-fix |
| V3.7 | Command file completeness | All flags documented; ≥7 examples; boundaries defined |
| V3.8 | sc:save wave boundary integration | Save points created after each wave |
| V3.9 | sc:load resume protocol | Detects incomplete sessions; offers resume; validates spec hash |
| V3.10 | Progress reporting | Wave boundary emissions include current wave, context, next steps |

**Stop-and-fix triggers**: V3.3 failure (scoring broken), V3.4 failure (REVISE loop infinite or missing)

### V4: Final Integration Validation (after M7)

**Validates**: M7 (Polish & Combined Mode), full pipeline end-to-end

| Check | Description | Pass Criteria |
|-------|-------------|---------------|
| V4.1 | Combined mode chaining | Multi-spec → multi-roadmap executes in sequence; artifacts chained |
| V4.2 | Interactive mode prompts | User prompted at persona, template, convergence decisions |
| V4.3 | --dry-run flag | Structure output to console; no files written |
| V4.4 | Edge cases | Empty spec, invalid YAML, circular deps handled gracefully |
| V4.5 | End-to-end single-spec | Full pipeline produces 3 valid artifacts from a real spec |
| V4.6 | End-to-end multi-spec | Full pipeline with --specs produces unified + roadmap artifacts |
| V4.7 | End-to-end multi-roadmap | Full pipeline with --agents produces merged roadmap |
| V4.8 | Success criteria coverage | All 27 success criteria from spec Section 12 verified |

**Stop-and-fix triggers**: V4.5 failure (core pipeline broken), V4.8 failure (success criteria not met)

## Validation Agent Responsibilities

### Work Agent
- Implements milestone deliverables
- Reports completion status at each deliverable
- Flags uncertainties or spec ambiguities encountered during implementation

### Validation Agent
- Runs behind the work agent at validation milestones
- Executes all checks in the validation milestone
- Reports findings with severity (critical/major/minor)
- Triggers stop-and-fix when thresholds exceeded
- Does NOT modify code — only reports and recommends

### Orchestration
- Work agent completes M1 + M2 → Validation agent executes V1
- If V1 passes → Work agent proceeds to M3 + M4
- If V1 triggers stop-and-fix → Work agent fixes before M3
- Pattern repeats through V2, V3, V4

## Risk-Based Testing Priorities

| Priority | Area | Rationale |
|----------|------|-----------|
| P0 | SKILL.md split + ref loading | Architectural foundation — if broken, nothing works |
| P0 | Extraction pipeline + chunked extraction | Data integrity — if extraction loses data, roadmap is wrong |
| P1 | YAML frontmatter validity | Contract — if invalid, downstream consumption breaks |
| P1 | REVISE loop convergence | Quality gate — if broken, no quality assurance |
| P1 | Adversarial integration | Major feature — if broken, multi-spec/multi-roadmap modes fail |
| P2 | Combined mode | Composition of working parts — lower individual risk |
| P2 | Session persistence | Quality of life — if broken, user restarts from scratch |
