---
spec_source: .dev/releases/current/v2.02-Roadmap-v3/sprint-spec.md
generated: 2026-02-25T12:00:00Z
generator: sc:roadmap
complexity_score: 0.547
complexity_class: MEDIUM
domain_distribution:
  frontend: 0
  backend: 72
  security: 10
  performance: 0
  documentation: 18
primary_persona: backend
consulting_personas: [scribe, architect]
milestone_count: 6
milestone_index:
  - id: M1
    title: "Pre-Implementation Gates & Probing"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    risk_level: High
  - id: M2
    title: "Invocation Wiring Restoration"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: High
  - id: M3
    title: "Return Contract Transport Mechanism"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 5
    risk_level: Medium
  - id: M4
    title: "Specification Rewrite with Executable Instructions"
    type: FEATURE
    priority: P1
    dependencies: [M2, M3]
    deliverable_count: 4
    risk_level: Low
  - id: M5
    title: "Post-Edit Sync & Quality Gates"
    type: TEST
    priority: P1
    dependencies: [M2, M3, M4]
    deliverable_count: 4
    risk_level: Low
  - id: M6
    title: "End-to-End Validation & Acceptance"
    type: TEST
    priority: P1
    dependencies: [M5]
    deliverable_count: 7
    risk_level: Medium
total_deliverables: 29
total_risks: 13
estimated_phases: 3
validation_score: 0.0
validation_status: SKIPPED
---

# Roadmap: sc:roadmap Adversarial Pipeline Remediation

## Overview

This roadmap restores full adversarial pipeline functionality for `sc:roadmap --multi-roadmap --agents` across three epics: invocation wiring restoration (RC1+S01), specification rewrite with executable instructions (RC2+S02), and return contract transport mechanism (RC4+S04). The sprint addresses the top 3 ranked root-cause/solution pairs identified through a 5-debate adversarial analysis process.

The implementation follows a dependency-driven order: a pre-implementation probe (Task 0.0) determines whether the primary Skill-tool invocation path is viable or whether the sprint must pivot to a fallback-only variant. All subsequent work branches from this decision gate. Epics 1 and 3 can partially parallelize (they modify different files), while Epic 2 depends on Epic 1 completing first. A file conflict constraint requires Task 3.2 to complete before Task 2.4 (both modify adversarial-integration.md).

Five T04 optimizations reduce estimated effort by 26.3% (3.95 hrs from an estimated 15-hour sprint): task merge (1.3+1.4+2.2), amendment fold, fallback simplification, conditional deferral, and test embedding.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Pre-Implementation Gates & Probing | FEATURE | P0 | S | None | 4 | High |
| M2 | Invocation Wiring Restoration | FEATURE | P0 | L | M1 | 5 | High |
| M3 | Return Contract Transport Mechanism | FEATURE | P0 | M | M1 | 5 | Medium |
| M4 | Specification Rewrite with Executable Instructions | FEATURE | P1 | M | M2, M3 | 4 | Low |
| M5 | Post-Edit Sync & Quality Gates | TEST | P1 | S | M2, M3, M4 | 4 | Low |
| M6 | End-to-End Validation & Acceptance | TEST | P1 | M | M5 | 7 | Medium |

## Dependency Graph

```
M1 → M2 → M4 → M5 → M6
M1 → M3 → M4 → M5 → M6
         ↗
M2 ──────┘ (M3 partially parallel with M2, but M4 needs both)
```

**File conflict constraint**: Within M3 and M4, Task 3.2 (M3) must complete before Task 2.4 (M4) — both modify `adversarial-integration.md`.

---

## M1: Pre-Implementation Gates & Probing

### Objective
Empirically determine Skill tool cross-skill invocation viability and validate all external dependencies before any file edits begin. This milestone's outcome gates the entire sprint: it may trigger a pivot to the fallback-only sprint variant.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Skill tool probe (Task 0.0): test cross-skill invocation and Task agent Skill access | Decision gate result documented: primary path viable OR blocked. Sprint plan updated if blocked. |
| D1.2 | Determine "skill already running" constraint semantics | Documented whether constraint applies to (a) same skill name, (b) any skill while another active, or (c) same instance |
| D1.3 | Prerequisite validation (Task 0.1): 6 dependency checks | All 6 checks (sc:adversarial installed, sc:roadmap installed, adversarial-integration.md present, make sync-dev available, make verify-sync available, Task 0.0 result documented) pass or have documented resolution |
| D1.4 | Sprint variant decision | If primary path blocked: fallback-only task modifications applied within 30 minutes per Fallback-Only Sprint Variant section |

### Dependencies
- None (first milestone)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-001: Task agent cannot access Skill tool | High | High | Fallback protocol ensures feature ships regardless. Empirical test before full implementation. |
| RISK-002: "Skill already running" blocks invocation | Medium | High | Fallback trigger in step 3d covers this error type explicitly. |

---

## M2: Invocation Wiring Restoration

### Objective
Enable skill-to-skill invocation by adding the Skill tool to allowed-tools in both command and skill files, then performing the merged Wave 2 step 3 rewrite (Tasks 1.3+1.4+2.2) as a single atomic edit covering Skill invocation, fallback protocol, and atomic sub-step decomposition.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `Skill` in allowed-tools of `src/superclaude/commands/roadmap.md` (Task 1.1) | `grep -q "Skill" src/superclaude/commands/roadmap.md` returns PASS |
| D2.2 | `Skill` in allowed-tools of `src/superclaude/skills/sc-roadmap/SKILL.md` (Task 1.2) | `grep -q "Skill" src/superclaude/skills/sc-roadmap/SKILL.md` returns PASS |
| D2.3 | Wave 2 step 3 rewritten as sub-steps 3a-3f (merged Task 1.3) | 6 sub-steps present; each uses exactly one glossary verb; step 3d has Skill tool call with `skill: "sc:adversarial"` |
| D2.4 | Fallback protocol with F1, F2/3, F4/5 (merged Task 1.3) | Fallback covers 3 error types; 3 fallback invocations with defined input/output/failure; WARNING emission instructed; fallback produces `fallback_mode: true` |
| D2.5 | Return contract routing in step 3e (merged Task 1.3) | 3-status routing (success/partial/failed); convergence threshold 0.6; missing-file guard; YAML parse error handling |

### Dependencies
- M1: Task 0.0 must confirm primary path viability (or sprint adapted)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-001: Skill tool inaccessible | High | High | Fallback protocol (D2.4) ensures feature ships |
| RISK-008: Execution timeout | Medium | Medium | Timeout handling guidance in Skill tool call; documented expected duration |
| RISK-009: Context exhaustion | Low | High | Documented as known limitation; spec size warnings considered |

---

## M3: Return Contract Transport Mechanism

### Objective
Establish the file-based return-contract.yaml convention so sc:adversarial reliably transports structured pipeline results back to sc:roadmap. This includes the producer schema (9 fields in sc:adversarial), consumer logic (adversarial-integration.md), and the Tier 1 artifact existence gate.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | "Return Contract (MANDATORY)" section in sc:adversarial SKILL.md (Task 3.1) | Section exists as final pipeline step; 9 fields defined; null for unreached values; write-on-failure explicit; `fallback_mode` present; example YAML block provided |
| D3.2 | Dead code removal: zero `subagent_type` lines (Task 3.1 appended scope) | `grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md` returns 0 |
| D3.3 | "Return Contract Consumption" section in adversarial-integration.md (Task 3.2) | Read instruction present; schema_version validation; 3-status routing; missing-file guard; convergence threshold 0.6; `fallback_mode` differentiated warning; example YAML blocks |
| D3.4 | "Post-Adversarial Artifact Existence Gate (Tier 1)" section (Task 3.3) | 4 existence checks in order (directory, diff-analysis.md, merged-output.md, return-contract.yaml); each with failure treatment; positioned before YAML parsing; path variable references |
| D3.5 | Cross-reference consistency between producer and consumer schemas | Identical field sets; `base_variant` and `failure_stage` present in both; `unresolved_conflicts` typed as integer in both |

### Dependencies
- M1: prerequisite validation complete
- **File constraint**: D3.3 (Task 3.2) must complete before M4's Task 2.4 — both modify adversarial-integration.md

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-003: Return contract file missing | Medium | Medium | Missing-file guard treats absence as `status: failed, failure_stage: transport` |
| RISK-004: Claude doesn't write contract on failure | Medium | Medium | Write-on-failure instruction explicit; step 3e treats parse errors as failed |
| RISK-010: Partial YAML write | Low | Medium | Step 3e YAML parsing with error handling |

---

## M4: Specification Rewrite with Executable Instructions

### Objective
Eliminate specification ambiguity by adding the verb-to-tool glossary, fixing Wave 1A step 2 invocation, and converting adversarial-integration.md from pseudo-CLI to Skill tool call format.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Verb-to-tool glossary ("Execution Vocabulary") section before Wave 0 (Task 2.1) | Glossary exists; maps: "Invoke skill" → Skill, "Dispatch agent" → Task, "Read ref" → Read, "Write artifact" → Write; scope statement present; appears before Wave 0 |
| D4.2 | Every verb in Waves 0-4 appears in glossary | Audit confirms 100% coverage |
| D4.3 | Wave 1A step 2 uses glossary-consistent Skill tool invocation (Task 2.3) | No bare "Invoke"; uses Skill tool call pattern matching Wave 2 step 3d; fallback present |
| D4.4 | adversarial-integration.md pseudo-CLI syntax fully converted (Task 2.4) | `grep -c "sc:adversarial --" src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` returns 0; args strings within Skill tool calls may contain `--flag` syntax |

### Dependencies
- M2: Skill tool must be in allowed-tools for step 3d's primary path
- M3: Task 3.2 must complete before Task 2.4 (same-file conflict avoidance)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-007: Residual pseudo-CLI syntax | Low | Low | Full audit via grep in D4.4 acceptance criteria |

---

## M5: Post-Edit Sync & Quality Gates

### Objective
Verify all code changes are synchronized between source and development copies, all quality gates pass, and the codebase is in a clean state for E2E testing.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | `make sync-dev` executed successfully | Exit code 0; .claude/ mirrors updated |
| D5.2 | `make verify-sync` passes | Exit code 0; all source ↔ dev copy diffs resolved |
| D5.3 | `make lint` passes on all modified files | Zero lint errors across all 4 modified files |
| D5.4 | `uv run pytest` passes — no existing tests broken | Exit code 0; all pre-existing tests pass |

### Dependencies
- M2, M3, M4: all code changes complete

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Low | Low | Low | Standard CI-equivalent gates; issues caught here are straightforward to fix |

---

## M6: End-to-End Validation & Acceptance

### Objective
Execute all 7 verification tests from the sprint spec's Verification Plan to confirm the full invocation chain works and all Definition of Done criteria are met.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | Verification Test 1: Skill tool in allowed-tools | grep confirms `Skill` in both files |
| D6.2 | Verification Test 2: Wave 2 step 3 structural audit | 6 sub-steps, glossary verbs, Skill tool call, fallback, missing-file guard, convergence threshold, skip-template |
| D6.3 | Verification Test 3: Return contract schema consistency | Identical field sets in producer and consumer; cross-reference comments present |
| D6.4 | Verification Test 3.5: Cross-reference field consistency | All consumer-referenced fields exist in producer schema; thresholds consistent |
| D6.5 | Verification Test 4: Pseudo-CLI elimination | `grep -c "sc:adversarial --"` returns 0 on adversarial-integration.md |
| D6.6 | Verification Test 5: E2E invocation (post-sprint, manual) | Full chain: sc:roadmap → Skill → sc:adversarial → return-contract.yaml → consumption → roadmap output with adversarial provenance |
| D6.7 | Verification Test 6: Tier 1 quality gate structure audit | Heading present, before YAML parsing, 4 checks in order, path variables used |

### Dependencies
- M5: all quality gates pass

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-012: Deferred RC3/RC5 second-order failures | Medium | Medium | Flag as post-sprint monitoring; add to follow-up sprint |
| RISK-006: Fallback bitrot | Low | Medium | Version comment at top of fallback section; maintenance task logged |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Task agent cannot access Skill tool | M1, M2 | High | High | Fallback protocol; empirical probe in M1 | backend |
| R-002 | "Skill already running" blocks invocation | M1, M2 | Medium | High | Fallback trigger covers error type explicitly | backend |
| R-003 | Return contract file missing | M3, M6 | Medium | Medium | Missing-file guard: treat as status: failed, failure_stage: transport | backend |
| R-004 | Claude doesn't write contract on failure | M3, M6 | Medium | Medium | Write-on-failure instruction; parse errors → failed | backend |
| R-005 | Wave 2 step 3 rewrite conflict | — | Eliminated | — | T04 Opt 1 task merge eliminates risk | — |
| R-006 | Fallback protocol bitrot | M2, M6 | Low | Medium | Version comment; maintenance task | backend |
| R-007 | Residual pseudo-CLI syntax | M4, M6 | Low | Low | Full grep audit in M4 acceptance criteria | scribe |
| R-008 | Execution timeout (10+ min) | M2, M6 | Medium | Medium | Timeout handling guidance; documented duration range | backend |
| R-009 | Context window exhaustion | M2, M6 | Low | High | Documented as known limitation; spec size warnings | backend |
| R-010 | Partial YAML file write | M3, M6 | Low | Medium | YAML parsing with error handling in step 3e | backend |
| R-011 | Recursive skill invocation depth limits | M2 | Low | Low | Document invocation depth limit of 1 | architect |
| R-012 | Deferred RC3/RC5 second-order failures | M6 | Medium | Medium | Post-sprint monitoring; follow-up sprint scope | architect |
| R-013 | Concurrency namespacing (conditional on Item 14) | M3 | Conditional | High | Caller-controlled --output-dir provides implicit namespacing; flag dependency in v2.1 planning | architect |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend (0.605) | scribe (0.176), architect (0.210 safe default) | Backend domain at 72% — highest domain weight |
| Template | inline (Tier 4) | No templates found in Tiers 1-3 | No local/user/plugin templates exist |
| Milestone Count | 6 | Range 5-7 (MEDIUM class) | base 5 + floor(3 domains / 2) = 6 |
| Adversarial Mode | none | N/A | No --multi-roadmap or --specs flags present |
| Implementation Order | Task 0.0 → 0.1 → Epic 1 → Epic 3 ∥ Epic 2 → sync → validate | Alternative: 0.1 → 1.1-1.2 → Epic 3 → Epic 1 Tasks 1.3+ + Epic 2 (IMP-07) | Dependency-driven: RC1+S01 is prerequisite for all other fixes (combined score 0.838) |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Skill in allowed-tools (both files) | M2 | Yes |
| SC-002 | Glossary exists before Wave 0 | M4 | Yes |
| SC-003 | Wave 2 step 3 has sub-steps 3a-3f | M2 | Yes |
| SC-004 | Wave 1A step 2 glossary-consistent | M4 | Yes |
| SC-005 | Zero pseudo-CLI syntax | M4 | Yes |
| SC-006 | Return contract 9 fields in sc:adversarial | M3 | Yes |
| SC-007 | Return contract read + 3-status routing | M3 | Yes |
| SC-008 | Tier 1 gate with 4 checks | M3 | Yes |
| SC-009 | Fallback covers 3 error types | M2 | Yes |
| SC-010 | Fallback verbs glossary-consistent | M2, M4 | Yes |
| SC-011 | Zero subagent_type lines | M3 | Yes |
| SC-012 | make verify-sync passes | M5 | Yes |
| SC-013 | No existing tests broken | M5 | Yes |
| SC-014 | E2E invocation test passes | M6 | Yes |
