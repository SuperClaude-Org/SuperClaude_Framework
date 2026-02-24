---
spec_source: ".dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md"
generated: "2026-02-23T00:00:00Z"
generator: sc:roadmap
complexity_score: 0.584
complexity_class: MEDIUM
domain_distribution:
  frontend: 0
  backend: 40
  security: 0
  performance: 0
  documentation: 35
  quality: 25
primary_persona: architect
consulting_personas: [backend, scribe]
milestone_count: 6
milestone_index:
  - id: M1
    title: "Foundation & Prerequisites"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 3
    risk_level: High
    effort: S
  - id: M2
    title: "Invocation Wiring Restoration"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: High
    effort: L
  - id: V1
    title: "Wiring Validation Checkpoint"
    type: TEST
    priority: P3
    dependencies: [M1, M2]
    deliverable_count: 2
    risk_level: Low
    effort: S
  - id: M3
    title: "Specification Rewrite with Executable Instructions"
    type: DOC
    priority: P1
    dependencies: [M2]
    deliverable_count: 3
    risk_level: Low
    effort: M
  - id: M4
    title: "Return Contract Transport Mechanism"
    type: FEATURE
    priority: P1
    dependencies: [M1]
    deliverable_count: 4
    risk_level: Medium
    effort: M
  - id: V2
    title: "Integration Validation & Acceptance"
    type: TEST
    priority: P3
    dependencies: [M3, M4, V1]
    deliverable_count: 5
    risk_level: Medium
    effort: M
total_deliverables: 22
total_risks: 15
estimated_phases: 3
validation_score: 0.9131
validation_status: PASS
---

# Roadmap: sc:roadmap Adversarial Pipeline Remediation Sprint

## Overview

This roadmap restores full adversarial pipeline functionality for `sc:roadmap --multi-roadmap --agents` by addressing three root causes ranked by combined problem-solution scoring: invocation wiring gap (RC1+S01, score 0.838), return contract data flow (RC4+S04, score 0.778), and specification-execution gap (RC2+S02, score 0.776).

The sprint modifies 4 files across 3 skill packages (`sc-roadmap`, `sc-adversarial`, and the `roadmap` command) to establish a Skill-tool-based invocation chain with structured fallback, atomic specification language, and a file-based YAML return contract. A pre-implementation gate (Task 0.0) empirically determines whether the primary invocation path is viable before committing to the full sprint plan.

The roadmap is organized into 4 work milestones and 2 validation checkpoints following a 1:2 interleave ratio (MEDIUM complexity class). M2 (Invocation Wiring) is the critical path — all downstream milestones depend on it either directly or transitively. M3 (Specification Rewrite) and M4 (Return Contract) can execute in parallel after their respective prerequisites are met, with a file-conflict ordering constraint (Task 3.2 before Task 2.4 on adversarial-integration.md).

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation & Prerequisites | FEATURE | P0 | S | None | 3 | High |
| M2 | Invocation Wiring Restoration | FEATURE | P0 | L | M1 | 5 | High |
| V1 | Wiring Validation Checkpoint | TEST | P3 | S | M1, M2 | 2 | Low |
| M3 | Specification Rewrite with Executable Instructions | DOC | P1 | M | M2 | 3 | Low |
| M4 | Return Contract Transport Mechanism | FEATURE | P1 | M | M1 | 4 | Medium |
| V2 | Integration Validation & Acceptance | TEST | P3 | M | M3, M4, V1 | 5 | Medium |

## Dependency Graph

```
M1 ──→ M2 ──→ V1 ──→ V2
│       │              ↑
│       └──→ M3 ──────┘
│                      ↑
└──────→ M4 ──────────┘
```

**Critical path**: M1 → M2 → M3 → V2
**Parallel opportunity**: M4 can execute alongside M3 (after M1 completes)
**File conflict constraint**: Within M4, Task 3.2 must complete before M3's Task 2.4 (both modify adversarial-integration.md)

---

## M1: Foundation & Prerequisites

### Objective

Validate that the Skill tool can be called cross-skill, confirm all external dependencies are present, and establish whether the primary invocation path or fallback-only variant applies to the remainder of the sprint.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Skill Tool Probe result documented (Task 0.0) | Decision gate result recorded: primary path viable, "skill already running" block, or "tool not available". Sprint plan updated if primary path non-viable. Completed in <15 minutes. |
| D1.2 | Prerequisite Validation checklist completed (Task 0.1) | All 6 checks documented with pass/fail: sc:adversarial installed, sc:roadmap installed, adversarial-integration.md present, make sync-dev available, make verify-sync available, Task 0.0 result documented. |
| D1.3 | Sprint variant decision | If primary path blocked: fallback-only sprint variant applied per spec L92-L111 task modification table within 30 minutes. If viable: proceed with standard plan. |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Task agent cannot access Skill tool | HIGH (0.40) | HIGH | Fallback protocol ensures feature ships regardless; empirical test before full implementation |
| R-002: "Skill already running" blocks invocation | MEDIUM (0.30) | HIGH | Fallback trigger covers this error type explicitly; promotes fallback to primary if confirmed |

---

## M2: Invocation Wiring Restoration

### Objective

Enable skill-to-skill invocation by adding the Skill tool to allowed-tools and implementing a complete Wave 2 step 3 rewrite with atomic sub-steps (3a-3f), Skill tool call syntax, and a structured 5-step fallback protocol (F1 through F4/5).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `Skill` in allowed-tools — roadmap command (Task 1.1) | `grep -q "Skill" src/superclaude/commands/roadmap.md` returns PASS. Existing tools unchanged. |
| D2.2 | `Skill` in allowed-tools — SKILL.md (Task 1.2) | `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md` returns PASS. Existing tools unchanged. |
| D2.3 | Wave 2 step 3 rewritten as sub-steps 3a-3f (Task 1.3 — merged) | 6 sub-steps present: 3a (parse agents), 3b (expand variants), 3c (debate-orchestrator for >=3 agents), 3d (Skill tool call OR fallback), 3e (consume return-contract.yaml with status routing), 3f (skip template if adversarial succeeded). Each sub-step uses exactly one glossary verb. |
| D2.4 | Fallback protocol with 3 invocation steps (F1, F2/3, F4/5) | Fallback triggers on 3 error types. F1 produces >=2 variant files. F2/3 produces diff-analysis.md with labeled sections. F4/5 produces base-selection.md + merged-output.md + return-contract.yaml with `fallback_mode: true`. Minimum quality threshold enforced (>=100 words for analysis artifacts). |
| D2.5 | Return contract routing in step 3e | Missing-file guard present. Three-status routing: success -> proceed, partial -> warn if convergence >= 0.6, failed -> abort. YAML parse error treated as `status: failed`. Canonical schema comment present. |

### Dependencies

- M1: Foundation must confirm primary path viability (D1.1) and prerequisites (D1.2)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-001: Task agent cannot access Skill tool | HIGH (0.40) | HIGH | D2.4 fallback protocol is the primary mitigation |
| R-008: Execution timeout during adversarial pipeline | MEDIUM (0.25) | MEDIUM | Timeout handling guidance in Skill tool call; document expected duration |
| R-009: Context window exhaustion with multiple variants | LOW (0.20) | HIGH | Document as known limitation; spec size warnings |
| R-014: Scope creep from merged Task 1.3 | MEDIUM | MEDIUM | Single atomic edit eliminates coordination risk; clear sub-step boundaries |

---

## V1: Wiring Validation Checkpoint

### Objective

Validate that the invocation wiring (M1 + M2) is structurally correct before proceeding to specification rewrite and return contract implementation.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| DV1.1 | Verification Test 1: Skill Tool Availability | Both grep commands return PASS for roadmap.md and SKILL.md |
| DV1.2 | Verification Test 2: Wave 2 Step 3 Structural Audit | 7-point manual checklist passes: 6 sub-steps counted, glossary verbs used, Skill call syntax present, 3 fallback error types covered, missing-file guard present, convergence threshold 0.6 present, skip-template instruction present |

### Dependencies

- M1: Foundation complete
- M2: Invocation Wiring complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| No significant risks | — | — | Validation is read-only static analysis |

---

## M3: Specification Rewrite with Executable Instructions

### Objective

Eliminate specification ambiguity by adding a verb-to-tool execution vocabulary, fixing Wave 1A's "Invoke" ambiguity, and converting adversarial-integration.md from standalone pseudo-CLI syntax to Skill tool call format.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Verb-to-tool execution vocabulary glossary (Task 2.1) | Glossary section exists before Wave 0. 4 mappings: "Invoke skill" = Skill tool, "Dispatch agent" = Task tool, "Read ref" = Read tool, "Write artifact" = Write tool. Scope statement present. Every verb in Wave 0-4 and F1-F5 appears in glossary. |
| D3.2 | Wave 1A step 2 fixed (Task 2.3) | "Invoke sc:adversarial" replaced with Skill tool call pattern matching Wave 2 step 3d. Fallback protocol present. Glossary-consistent verb used. |
| D3.3 | adversarial-integration.md pseudo-CLI converted (Task 2.4) | `grep -c "sc:adversarial --" adversarial-integration.md` returns 0. All standalone invocation examples wrapped in Skill tool call format. Args strings within Skill calls may contain `--flag` syntax. |

### Dependencies

- M2: Invocation Wiring must be complete (Skill tool in allowed-tools for step 3d's primary path to be meaningful)
- M4 Task 3.2 must complete before Task 2.4 begins (same-file conflict avoidance on adversarial-integration.md)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-007: Residual pseudo-CLI syntax in unconverted sections | LOW (0.15) | LOW | Full audit via Verification Test 4 grep pattern |

---

## M4: Return Contract Transport Mechanism

### Objective

Establish a file-based return-contract.yaml convention enabling sc:adversarial to transport structured pipeline results back to sc:roadmap, with producer-consumer schema alignment and a Tier 1 artifact existence gate.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Return Contract write instruction in sc:adversarial SKILL.md (Task 3.1) | "Return Contract (MANDATORY)" section exists as final pipeline step. 9 fields defined: schema_version, status, convergence_score, merged_output_path, artifacts_dir, unresolved_conflicts (integer), base_variant, failure_stage, fallback_mode. YAML null for unreached values. Write-on-failure instruction explicit. Example YAML block provided. |
| D4.2 | Dead code removal — subagent_type lines (Task 3.1 appended scope) | `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns 0. Both `subagent_type: "general-purpose"` lines removed. |
| D4.3 | Return Contract Consumption section in adversarial-integration.md (Task 3.2) | Read instruction present. schema_version validation present. Three-status routing defined (success/partial/failed). Missing-file guard present. Convergence threshold 0.6 specified. `fallback_mode` routing with differentiated user warning. Example YAML blocks for success and failure. |
| D4.4 | Post-Adversarial Artifact Existence Gate (Tier 1) in adversarial-integration.md (Task 3.3) | Section heading "Post-Adversarial Artifact Existence Gate (Tier 1)" exists. 4 sequential checks: directory existence, diff-analysis.md, merged-output.md, return-contract.yaml. Each check has defined failure treatment. Gate positioned before YAML parsing. Path variable references used throughout. |

### Dependencies

- M1: Foundation prerequisites validated (sc:adversarial SKILL.md readable)
- Note: E2E testing requires M2 complete, but implementation can begin after M1

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-003: return-contract.yaml does not exist | MEDIUM (0.25) | MEDIUM | D4.4 Tier 1 gate provides pre-YAML-parsing defense |
| R-004: Claude doesn't write contract on failure paths | MEDIUM (0.30) | MEDIUM | D4.1 explicit write-on-failure instruction; D4.3 YAML parse error treated as `status: failed` |
| R-010: Partial file writes / malformed YAML | LOW (0.15) | MEDIUM | Step 3e routing treats parse errors as `status: failed` |

---

## V2: Integration Validation & Acceptance

### Objective

Validate end-to-end pipeline functionality, schema consistency between producer and consumer, and all Definition of Done criteria before sprint completion.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| DV2.1 | Verification Test 3: Return contract schema consistency | Producer (sc:adversarial) and consumer (adversarial-integration.md) field sets identical. `base_variant` and `failure_stage` present in both. Cross-reference comments present. |
| DV2.2 | Verification Test 3.5: Cross-reference field consistency | All consumer-referenced fields exist in producer schema. Convergence threshold consistent (0.6 / 60%). |
| DV2.3 | Verification Test 4: Pseudo-CLI elimination | `grep -c "sc:adversarial --" adversarial-integration.md` returns 0. |
| DV2.4 | Verification Test 6: Tier 1 quality gate structure audit | 7-point checklist passes: section heading exists, positioned before YAML parsing, 4 checks with correct failure treatments, path variables used. |
| DV2.5 | Sync and quality gates | `make sync-dev && make verify-sync` passes. `uv run pytest` passes (no regressions). `make lint` passes. Every glossary verb used in Wave 0-4. Zero `subagent_type` lines remain. |

### Dependencies

- M3: Specification Rewrite complete
- M4: Return Contract complete
- V1: Wiring Validation passed

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-012: Deferred root causes surfacing | MEDIUM (0.30) | MEDIUM | Flag as post-sprint monitoring item |
| R-015: Integration risk from 4-file edit | MEDIUM | MEDIUM | Verification Tests 3, 3.5 catch schema misalignment |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Task agent cannot access Skill tool — primary invocation path fails | M1, M2 | HIGH (0.40) | HIGH | Fallback protocol (M2 D2.4); empirical probe (M1 D1.1) | architect |
| R-002 | "Skill already running" blocks sc:roadmap -> sc:adversarial invocation | M1, M2 | MEDIUM (0.30) | HIGH | Fallback trigger covers error type; sprint variant adaptation | architect |
| R-003 | return-contract.yaml does not exist after pipeline execution | M4, V2 | MEDIUM (0.25) | MEDIUM | Tier 1 artifact existence gate (M4 D4.4); missing-file guard (M4 D4.3) | backend |
| R-004 | Claude does not write return contract on failure paths | M4 | MEDIUM (0.30) | MEDIUM | Write-on-failure instruction (M4 D4.1); YAML parse error routing | backend |
| R-005 | Wave 2 step 3 rewrite conflict between epics | N/A | ELIMINATED | N/A | T04 Opt 1 merged Tasks 1.3+1.4+2.2 into single Task 1.3 | N/A |
| R-006 | Fallback protocol bitrot as sc:adversarial pipeline evolves | M2 | LOW (0.15) | MEDIUM | Version comment in fallback section; maintenance task logged | architect |
| R-007 | Residual pseudo-CLI syntax in unconverted sections | M3, V2 | LOW (0.15) | LOW | Verification Test 4 grep audit (V2 DV2.3) | scribe |
| R-008 | Claude execution timeout during adversarial pipeline (10+ min) | M2 | MEDIUM (0.25) | MEDIUM | Timeout handling guidance in Skill tool call; duration documentation | architect |
| R-009 | Context window exhaustion with multiple full-text variants | M2 | LOW (0.20) | HIGH | Document as known limitation; spec size warnings in sc:roadmap | architect |
| R-010 | Partial file writes producing malformed return-contract.yaml | M4 | LOW (0.15) | MEDIUM | YAML parse error treated as `status: failed` in step 3e | backend |
| R-011 | Recursive skill invocation depth limits (sc:roadmap -> sc:adversarial -> ...) | M2 | LOW (0.10) | LOW | Document invocation depth limit of 1 | architect |
| R-012 | Deferred root causes (RC3/RC5) surfacing as second-order failures | V2 | MEDIUM (0.30) | MEDIUM | Post-sprint monitoring item; follow-up sprint scope | architect |
| R-013 | Concurrency namespacing if framework-level protocol (Item 14) adopted | Future | CONDITIONAL | HIGH (conditional) | Caller-controlled `--output-dir` provides implicit namespacing; Item 17 constraint documented | architect |
| R-014 | Sprint scope creep from merged Task 1.3 complexity | M2 | MEDIUM (0.25) | MEDIUM | Single atomic edit; clear sub-step boundaries (3a-3f + F1-F4/5) | architect |
| R-015 | Integration risk from 4-file edit spanning 3 skill packages | V2 | MEDIUM (0.30) | MEDIUM | Verification Tests 3, 3.5 catch schema misalignment; file conflict ordering | backend |

## Deferred Scope

| ID | Description | Priority | Rationale | Trigger |
|----|-------------|----------|-----------|---------|
| FR-017 | Sprint 0 Debt Register: create `.dev/releases/debt-register.md` from confidence matrix | P2 | Spec L227-L254: "If initialization is deferred until sometime in v2.1, it will be deferred indefinitely." Not in-sprint scope but must execute before v2.1 kickoff. | Pre-v2.1 gap (~30 min, zero blast radius) |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect (0.364) | backend (0.308), scribe (0.245), qa (0.175) | Highest confidence score; backend domain 40% but architect covers all 3 domains as generalist with coverage_bonus 1.3 |
| Template | inline | No templates found in Tiers 1-3 | Tier 4 fallback: inline generation from extraction data |
| Milestone Count | 6 (4 work + 2 validation) | Range 5-7 for MEDIUM class | Formula: base(5) + floor(3 domains / 2) = 6 |
| Adversarial Mode | none | N/A | No `--multi-roadmap` or `--specs` flags provided |
| Milestone Structure | Epic-aligned (3 epics -> 3 domain milestones + foundation) | Flat task-by-task; IMP-07 (Epic 3 before Epic 1 Tasks 1.3-1.4) | 3 epics x 1 domain each = 3 domain milestones; spec L194-L224 confirms Epic-to-domain alignment. IMP-07 rejected: current order preserves the spec's explicit dependency chain (S01 prerequisite for all fixes) and avoids forward-referencing the return contract schema before it exists |
| M3/M4 Ordering | Parallel with file-conflict constraint | Strictly sequential | Spec L221: Task 3.2 before Task 2.4; otherwise independent |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | `Skill` in allowed-tools in both roadmap.md and SKILL.md | M2 (D2.1, D2.2) | Yes — grep |
| SC-002 | Verb-to-tool glossary exists before Wave 0 | M3 (D3.1) | Yes — section exists |
| SC-003 | Wave 2 step 3 decomposed into 3a-3f with tool-call syntax | M2 (D2.3) | Yes — structural audit |
| SC-004 | Zero standalone pseudo-CLI syntax in adversarial-integration.md | M3 (D3.3) | Yes — grep count = 0 |
| SC-005 | Return contract with 9 fields in sc:adversarial SKILL.md | M4 (D4.1) | Yes — field count |
| SC-006 | Return contract read with 3-status routing and fallback_mode warning | M4 (D4.3) | Yes — section audit |
| SC-007 | Tier 1 artifact existence gate with 4 ordered checks | M4 (D4.4) | Yes — structural audit |
| SC-008 | make verify-sync passes | V2 (DV2.5) | Yes — command exit code |
| SC-009 | All 7 verification tests pass | V1, V2 | Yes — test execution |
| SC-010 | No existing tests broken, linting passes | V2 (DV2.5) | Yes — pytest + ruff |
