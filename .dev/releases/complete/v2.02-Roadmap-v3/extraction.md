---
spec_source: ".dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md"
generated: "2026-02-23T00:00:00Z"
generator: sc:roadmap
project_title: "sc:roadmap Adversarial Pipeline Remediation Sprint"
project_version: "v2.01"
extraction_date: "2026-02-23"
extraction_mode: "standard"
functional_requirements: 17
nonfunctional_requirements: 6
total_requirements: 23
domains_detected: [backend, documentation, quality]
complexity_score: 0.584
complexity_class: "MEDIUM"
risks_identified: 15
dependencies_identified: 7
success_criteria_count: 10
---

# Extraction Report: sc:roadmap Adversarial Pipeline Remediation Sprint

## Overview

**Project**: sc:roadmap Adversarial Pipeline Remediation Sprint
**Source**: `.dev/releases/current/v2.01-Roadmap-v3/sprint-spec.md` (452 lines)
**Summary**: Restore full adversarial pipeline functionality for `sc:roadmap --multi-roadmap --agents` by fixing the invocation wiring gap, rewriting ambiguous specification language into executable tool-call instructions, and establishing a file-based return contract transport mechanism.

## Complexity Assessment

| Factor | Raw Value | Normalized | Weight | Weighted |
|--------|-----------|------------|--------|----------|
| requirement_count | 23 | 0.460 | 0.25 | 0.115 |
| dependency_depth | 7 | 0.875 | 0.25 | 0.219 |
| domain_spread | 3 | 0.600 | 0.20 | 0.120 |
| risk_severity | 1.82 avg | 0.410 | 0.15 | 0.062 |
| scope_size | 452 lines | 0.452 | 0.15 | 0.068 |
| **Total** | | | **1.00** | **0.584** |

**Classification**: MEDIUM (0.4 <= 0.584 <= 0.7) -> 5-7 milestones, 1:2 interleave ratio

## Domain Distribution

| Domain | Percentage | Key Indicators |
|--------|------------|----------------|
| Backend | 40% | Tool invocation, pipeline wiring, YAML transport, schema definition, service integration |
| Documentation | 35% | Specification rewrite, verb glossary, reference docs, pseudo-CLI conversion |
| Quality | 25% | Validation gates, acceptance criteria, verification tests, quality thresholds |

## Persona Selection

| Role | Persona | Confidence | Rationale |
|------|---------|------------|-----------|
| Primary | architect | 0.364 | Systems design, dependency management, cross-component integration |
| Consulting | backend | 0.308 | Tool wiring, transport mechanism, YAML schema design |
| Consulting | scribe | 0.245 | Specification clarity, glossary authoring, reference documentation |

## Functional Requirements

| ID | Description | Priority | Domain | Source |
|----|-------------|----------|--------|--------|
| FR-001 | Skill Tool Probe: empirically determine whether Skill tool can be called cross-skill and whether Task agents can use it | P0 | Backend | L64-L87 |
| FR-002 | Prerequisite Validation: confirm all external dependencies (sc:adversarial, sc:roadmap, refs, make targets) are present | P0 | Quality | L114-L136 |
| FR-003 | Add `Skill` to allowed-tools in `src/superclaude/commands/roadmap.md` | P0 | Backend | L149 |
| FR-004 | Add `Skill` to allowed-tools in `src/superclaude/skills/sc-roadmap/SKILL.md` | P0 | Backend | L150 |
| FR-005 | Rewrite Wave 2 step 3 with Skill invocation + fallback protocol + atomic sub-steps 3a-3f (merged Task 1.3+1.4+2.2) | P0 | Backend | L151 |
| FR-006 | Add verb-to-tool execution vocabulary glossary before Wave 0 with scope statement | P0 | Documentation | L166 |
| FR-007 | Fix Wave 1A step 2 "Invoke" ambiguity — replace with Skill tool call pattern and add fallback | P1 | Documentation | L167 |
| FR-008 | Rewrite adversarial-integration.md invocation patterns from standalone pseudo-CLI to Skill tool call format | P1 | Documentation | L168 |
| FR-009 | Add Return Contract (MANDATORY) section as final pipeline step in sc:adversarial SKILL.md with 9 YAML fields | P0 | Backend | L184 |
| FR-010 | Add Return Contract Consumption section to adversarial-integration.md with status routing and missing-file guard | P0 | Documentation | L185 |
| FR-011 | Add Post-Adversarial Artifact Existence Gate (Tier 1) with 4 sequential existence checks | P1 | Quality | L186 |
| FR-012 | Remove dead `subagent_type: "general-purpose"` lines from sc:adversarial SKILL.md (2 occurrences) | P1 | Quality | L184 |
| FR-013 | Fallback F1: Variant Generation — dispatch Task agents per --agents spec, each generates a roadmap variant | P0 | Backend | L151 |
| FR-014 | Fallback F2/3: Diff Analysis + Single-Round Debate — merged single-pass comparison of all variants | P0 | Backend | L151 |
| FR-015 | Fallback F4/5: Base Selection + Merge + Contract — score, select base, merge, write return-contract.yaml | P0 | Backend | L151 |
| FR-016 | Fallback-Only Sprint Variant: adaptation plan if Task 0.0 determines primary path is blocked | P1 | Documentation | L92-L111 |
| FR-017 | Sprint 0 Debt Register: create `.dev/releases/debt-register.md` from confidence matrix before v2.1 | P2 | Documentation | L227-L254 |

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | File-based YAML transport for return contracts between skills | Reliability | return-contract.yaml with 9 fields, parseable YAML | L40-L44 |
| NFR-002 | Fallback protocol covers all 3 Skill tool error types | Reliability | tool not in allowed-tools, skill not found, skill already running | L151 |
| NFR-003 | Return contract written even on failure paths | Reliability | status: failed with failure_stage field populated | L184 |
| NFR-004 | Minimum fallback quality threshold for analysis artifacts | Quality | >=100 words for analysis artifacts; >=2 variants for F1 | L151 |
| NFR-005 | Zero standalone pseudo-CLI syntax post-implementation | Maintainability | grep count = 0 for `sc:adversarial --` in adversarial-integration.md | L168 |
| NFR-006 | Sync integrity between src/ and .claude/ | Maintainability | make verify-sync passes | L293 |

## Dependencies

| ID | Description | Type | Affected | Source |
|----|-------------|------|----------|--------|
| DEP-001 | Task 0.0 (Skill Tool Probe) blocks all subsequent tasks | Internal | FR-002 through FR-017 | L86 |
| DEP-002 | Task 0.1 (Prerequisite Validation) blocks Epic 1 | Internal | FR-003 through FR-005 | L135 |
| DEP-003 | Epic 1 must complete before Epic 2 starts | Internal | FR-006, FR-007, FR-008 | L157 |
| DEP-004 | Task 3.2 must complete before Task 2.4 (same-file conflict avoidance) | Internal | FR-008 | L221 |
| DEP-005 | Epic 3 E2E testing requires Epic 1 complete | Internal | FR-009, FR-010, FR-011 | L215 |
| DEP-006 | Tasks 1.1 and 1.2 prerequisite for Task 1.3 (Skill must be in allowed-tools) | Internal | FR-005 | L143-L145 |
| DEP-007 | make sync-dev && verify-sync is post-edit step after all epics | Internal | NFR-006 | L152, L187 |

**Maximum dependency chain depth**: 7 (Task 0.0 -> 0.1 -> 1.1 -> 1.2 -> 1.3 -> 2.1/2.3 -> 2.4)

## Success Criteria

| ID | Description | Measurable | Derived From | Source |
|----|-------------|------------|-------------|--------|
| SC-001 | `Skill` in allowed-tools in both roadmap.md and SKILL.md | Yes (grep) | FR-003, FR-004 | L282-L283 |
| SC-002 | Verb-to-tool glossary exists before Wave 0 | Yes (section exists) | FR-006 | L284 |
| SC-003 | Wave 2 step 3 decomposed into sub-steps 3a-3f with tool-call syntax | Yes (structural audit) | FR-005 | L285-L286 |
| SC-004 | Zero standalone pseudo-CLI syntax in adversarial-integration.md | Yes (grep count = 0) | FR-008 | L287 |
| SC-005 | Return contract with 9 fields, null semantics, write-on-failure in sc:adversarial | Yes (field count) | FR-009 | L288 |
| SC-006 | Return contract read instruction with 3-status routing and fallback_mode warning | Yes (section audit) | FR-010 | L289 |
| SC-007 | Tier 1 artifact existence gate with 4 ordered checks | Yes (structural audit) | FR-011 | L291-L292 |
| SC-008 | make verify-sync passes | Yes (command exit code) | NFR-006 | L293 |
| SC-009 | All 7 verification tests pass | Yes (test execution) | All FRs | L305-L313 |
| SC-010 | No existing tests broken, linting passes | Yes (pytest + ruff) | All FRs | L296-L297 |

## Risk Register

| ID | Description | Probability | Impact | Affected | Source |
|----|-------------|-------------|--------|----------|--------|
| RISK-001 | Task agent cannot access Skill tool (primary path fails) | HIGH (0.40) | HIGH | FR-005, FR-013-015 | L261 |
| RISK-002 | "Skill already running" blocks sc:roadmap -> sc:adversarial | MEDIUM (0.30) | HIGH | FR-005, FR-007 | L262 |
| RISK-003 | return-contract.yaml does not exist after pipeline runs | MEDIUM (0.25) | MEDIUM | FR-010, FR-011 | L263 |
| RISK-004 | Claude does not write return contract on failure paths | MEDIUM (0.30) | MEDIUM | FR-009, NFR-003 | L264 |
| RISK-005 | Wave 2 step 3 rewrite conflict — ELIMINATED by T04 Opt 1 | ELIMINATED | N/A | N/A | L265 |
| RISK-006 | Fallback protocol bitrot as sc:adversarial evolves | LOW (0.15) | MEDIUM | FR-013-015 | L266 |
| RISK-007 | Residual pseudo-CLI syntax in unconverted sections | LOW (0.15) | LOW | FR-008, NFR-005 | L267 |
| RISK-008 | Claude execution timeout during adversarial pipeline | MEDIUM (0.25) | MEDIUM | FR-005, NFR-001 | L268 |
| RISK-009 | Context window exhaustion with multiple variants | LOW (0.20) | HIGH | FR-013, NFR-004 | L269 |
| RISK-010 | Partial file writes producing malformed YAML | LOW (0.15) | MEDIUM | NFR-001 | L270 |
| RISK-011 | Recursive skill invocation depth limits | LOW (0.10) | LOW | FR-005 | L271 |
| RISK-012 | Deferred root causes (RC3/RC5) surfacing as second-order failures | MEDIUM (0.30) | MEDIUM | FR-005 | L272 |
| RISK-013 | Concurrency namespacing if framework-level protocol adopted | CONDITIONAL | HIGH (conditional) | NFR-001 | L273 |
| RISK-014 | Sprint scope creep from merged Task 1.3 complexity | MEDIUM | MEDIUM | FR-005 | Inferred |
| RISK-015 | Integration risk from 4-file edit spanning 3 skill packages | MEDIUM | MEDIUM | All FRs | Inferred |

## Verification Cross-Reference

| Test | Validates | Method |
|------|-----------|--------|
| Test 1 | SC-001 (Skill in allowed-tools) | grep static analysis |
| Test 2 | SC-003 (Wave 2 step 3 structure) | Manual inspection checklist |
| Test 3 | SC-005 (Return contract schema consistency) | Field diff producer vs consumer |
| Test 3.5 | SC-005, SC-006 (Cross-reference field consistency) | Manual cross-reference |
| Test 4 | SC-004 (Pseudo-CLI elimination) | grep pattern count |
| Test 5 | SC-009 (End-to-end invocation) | Manual execution test |
| Test 6 | SC-007 (Tier 1 quality gate structure) | Manual inspection checklist |
| Test 7 | NFR-002, NFR-004 (Fallback protocol) | Controlled execution test |

---

*Extraction completed 2026-02-23. Pipeline: standard single-pass (452 lines < 500 threshold). Analyst persona: architect (0.364 confidence).*
