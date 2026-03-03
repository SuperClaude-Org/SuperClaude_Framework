---
spec_source: .dev/releases/current/v2.02-Roadmap-v3/sprint-spec.md
generated: 2026-02-25T12:00:00Z
generator: sc:roadmap
functional_requirements: 28
nonfunctional_requirements: 5
total_requirements: 33
domains_detected: [backend, security, documentation]
complexity_score: 0.62
complexity_class: MEDIUM
risks_identified: 13
dependencies_identified: 12
success_criteria_count: 14
extraction_mode: standard
---

# Extraction: sc:roadmap Adversarial Pipeline Remediation

## Project Overview

**Title**: sc:roadmap Adversarial Pipeline Remediation
**Version**: Sprint spec (v2.02-Roadmap-v3)
**Summary**: Restore full adversarial pipeline functionality for `sc:roadmap --multi-roadmap --agents` by fixing the invocation wiring gap, rewriting ambiguous specification language into executable tool-call instructions, and establishing a file-based return contract transport mechanism. The sprint addresses the top 3 ranked root-cause/solution pairs from a 5-debate adversarial analysis.

---

## Functional Requirements

| ID | Description | Domain | Priority | Source Lines |
|----|-------------|--------|----------|-------------|
| FR-001 | Skill tool probe: empirically determine whether the Skill tool can be called cross-skill and whether Task agents can use it | backend | P0 | L64-87 |
| FR-002 | Decision gate: route to primary path or fallback-only sprint variant based on probe results | backend | P0 | L72-78 |
| FR-003 | Prerequisite validation: confirm all external dependencies (sc:adversarial installed, sc:roadmap installed, adversarial-integration.md present, make targets available) | backend | P0 | L114-136 |
| FR-004 | Add `Skill` to allowed-tools in `src/superclaude/commands/roadmap.md` | backend | P0 | L149 |
| FR-005 | Add `Skill` to allowed-tools in `src/superclaude/skills/sc-roadmap/SKILL.md` | backend | P0 | L150 |
| FR-006 | Rewrite Wave 2 step 3 with Skill invocation as sub-steps 3a-3f with explicit tool-call syntax | backend | P0 | L151 |
| FR-007 | Sub-step 3a: parse `--agents` list into individual agent specs | backend | P1 | L151 |
| FR-008 | Sub-step 3b: expand agents into variant generation parameters | backend | P1 | L151 |
| FR-009 | Sub-step 3c: if agents >= 3, add debate-orchestrator to coordination role | backend | P1 | L151 |
| FR-010 | Sub-step 3d: Skill tool invocation of sc:adversarial with specified arguments | backend | P0 | L151 |
| FR-011 | Sub-step 3d fallback: if Skill tool returns error, execute fallback protocol (covers tool-not-in-allowed-tools, skill-not-found, skill-already-running) | backend | P0 | L151 |
| FR-012 | Fallback step F1: variant generation via Task agents per --agents spec | backend | P1 | L151 |
| FR-013 | Fallback step F2/3: diff analysis + single-round debate in single pass | backend | P1 | L151 |
| FR-014 | Fallback step F4/5: base selection + merge + return contract write | backend | P1 | L151 |
| FR-015 | Sub-step 3e: consume return-contract.yaml with 3-status routing (success/partial/failed) | backend | P0 | L151 |
| FR-016 | Sub-step 3f: skip template-based generation when adversarial succeeds/partial | backend | P1 | L151 |
| FR-017 | Add verb-to-tool glossary ("Execution Vocabulary") before Wave 0 with scope statement | documentation | P1 | L166 |
| FR-018 | Fix Wave 1A step 2 "Invoke" ambiguity — use same Skill tool call pattern as step 3d | backend | P1 | L167 |
| FR-019 | Rewrite adversarial-integration.md: convert all standalone pseudo-CLI syntax to Skill tool call format | documentation | P1 | L168 |
| FR-020 | Add "Return Contract (MANDATORY)" section as final pipeline step in sc:adversarial SKILL.md with 9 fields | backend | P0 | L184 |
| FR-021 | Return contract fields: schema_version, status, convergence_score, merged_output_path, artifacts_dir, unresolved_conflicts (integer), base_variant, failure_stage, fallback_mode | backend | P0 | L184 |
| FR-022 | Return contract: use YAML null for unreached fields, write even on failure | backend | P0 | L184 |
| FR-023 | Dead code removal: delete two `subagent_type: "general-purpose"` lines from sc:adversarial SKILL.md | backend | P2 | L184 |
| FR-024 | Add "Return Contract Consumption" section to adversarial-integration.md with schema_version validation, 3-status routing, missing-file guard, convergence threshold, fallback_mode differentiated warning | backend | P0 | L185 |
| FR-025 | Add "Post-Adversarial Artifact Existence Gate (Tier 1)" section to adversarial-integration.md with 4 existence checks in sequence before YAML parsing | backend | P1 | L186 |
| FR-026 | Tier 1 gate check 1: directory existence → failure_stage: pipeline_not_started | backend | P1 | L186 |
| FR-027 | Tier 1 gate check 2: diff-analysis.md existence → failure_stage: diff_analysis | backend | P1 | L186 |
| FR-028 | Tier 1 gate checks 3-4: merged-output.md and return-contract.yaml existence with status routing | backend | P1 | L186 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source Lines |
|----|-------------|----------|-----------|-------------|
| NFR-001 | All modified files must pass linting (`make lint`) | maintainability | Zero lint errors | L297 |
| NFR-002 | No existing tests broken (`uv run pytest` passes) | reliability | 100% existing test pass rate | L296 |
| NFR-003 | `make verify-sync` passes (`.claude/` mirrors match `src/superclaude/`) | maintainability | Sync validation green | L293 |
| NFR-004 | Fallback minimum quality threshold: F1 ≥2 variants, F2 non-empty diff, F3 scoring matrix | reliability | Minimum artifact size >100 words for analysis artifacts | L151 |
| NFR-005 | Path variable references used throughout Tier 1 gate (not hardcoded literals) | maintainability | Zero hardcoded paths | L186 |

---

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|----------------------|
| DEP-001 | Task 0.0 (Skill tool probe) blocks all subsequent tasks | internal | FR-001 → FR-002 → all |
| DEP-002 | Task 0.1 (prerequisite validation) blocks Epic 1 | internal | FR-003 → FR-004..FR-016 |
| DEP-003 | Epic 1 (invocation wiring) must complete before Epic 2 (spec rewrite) | internal | FR-004..FR-016 → FR-017..FR-019 |
| DEP-004 | Epic 3 can parallel Epic 2 but E2E testing requires Epic 1 | internal | FR-020..FR-028 ∥ FR-017..FR-019 |
| DEP-005 | Task 3.2 must complete before Task 2.4 (same file conflict avoidance) | internal | FR-024 → FR-019 |
| DEP-006 | sc:adversarial skill must be installed | external | FR-003, FR-010, FR-020 |
| DEP-007 | sc:roadmap skill must be installed | external | FR-003, FR-004, FR-005 |
| DEP-008 | `make sync-dev` and `make verify-sync` targets must be available | external | NFR-003 |
| DEP-009 | Tasks 1.3, 1.4, 2.2 merged into single Task 1.3 (T04 Opt 1) | internal | FR-006..FR-016 |
| DEP-010 | Task 0.0 decision determines sprint variant (primary vs fallback-only) | internal | FR-002 → sprint scope |
| DEP-011 | Fallback protocol references sc:adversarial SKILL.md output format | external | FR-012..FR-014 |
| DEP-012 | Return contract schema must be consistent between producer (sc:adversarial) and consumer (adversarial-integration.md) | internal | FR-020..FR-022 → FR-024 |

---

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|------------|
| SC-001 | `Skill` present in allowed-tools in both roadmap.md and SKILL.md | FR-004, FR-005 | Yes: grep verification |
| SC-002 | Verb-to-tool glossary exists before Wave 0 with scope statement | FR-017 | Yes: section presence |
| SC-003 | Wave 2 step 3 decomposed into sub-steps 3a-3f with tool-call syntax | FR-006..FR-016 | Yes: structural audit |
| SC-004 | Wave 1A step 2 uses glossary-consistent Skill tool invocation | FR-018 | Yes: verb match |
| SC-005 | Zero standalone `sc:adversarial --` pseudo-CLI syntax in adversarial-integration.md | FR-019 | Yes: grep count = 0 |
| SC-006 | Return contract write instruction in sc:adversarial SKILL.md with 9 fields | FR-020..FR-022 | Yes: field count |
| SC-007 | Return contract read instruction with 3-status routing and missing-file guard | FR-024 | Yes: routing presence |
| SC-008 | Post-Adversarial Artifact Existence Gate (Tier 1) with 4 checks in order | FR-025..FR-028 | Yes: structural audit |
| SC-009 | Fallback trigger covers three error types | FR-011 | Yes: error type list |
| SC-010 | Fallback steps use glossary-consistent verbs | FR-012..FR-014 | Yes: verb match |
| SC-011 | Zero `subagent_type` lines remain in sc:adversarial SKILL.md | FR-023 | Yes: grep count = 0 |
| SC-012 | `make verify-sync` passes | NFR-003 | Yes: exit code 0 |
| SC-013 | No existing tests broken | NFR-002 | Yes: pytest exit code 0 |
| SC-014 | E2E invocation test passes (post-sprint) | FR-006, FR-010, FR-020, FR-024 | Yes: manual verification |

---

## Risk Register

| ID | Description | Probability | Impact | Affected Requirements | Source Lines |
|----|-------------|-------------|--------|----------------------|-------------|
| RISK-001 | Task agent cannot access the Skill tool (primary invocation path fails) | High | High | FR-010, FR-011 | L261 |
| RISK-002 | "Skill already running" constraint blocks sc:roadmap from invoking sc:adversarial | Medium | High | FR-010, FR-011 | L262 |
| RISK-003 | Return contract routing fails when return-contract.yaml does not exist | Medium | Medium | FR-015, FR-024 | L263 |
| RISK-004 | Claude does not write return-contract.yaml on failure paths | Medium | Medium | FR-022, FR-024 | L264 |
| RISK-005 | Wave 2 step 3 rewrite conflict between epics — ELIMINATED by T04 Opt 1 task merge | Eliminated | High | FR-006 | L265 |
| RISK-006 | Fallback protocol bitrot as sc:adversarial pipeline evolves | Low | Medium | FR-012..FR-014 | L266 |
| RISK-007 | Pseudo-CLI syntax remains in unconverted adversarial-integration.md sections | Low | Low | FR-019 | L267 |
| RISK-008 | Claude execution timeout — adversarial pipeline may take 10+ minutes | Medium | Medium | FR-010, FR-015 | L268 |
| RISK-009 | Context window exhaustion during sc:adversarial — silent total failure | Low | High | FR-010, FR-022 | L269 |
| RISK-010 | Partial file writes — return-contract.yaml may be malformed YAML | Low | Medium | FR-015, FR-024 | L270 |
| RISK-011 | Recursive skill invocation hitting platform depth limits | Low | Low | FR-010 | L271 |
| RISK-012 | Deferred root causes RC3/RC5 surfacing as second-order failures | Medium | Medium | FR-006 | L272 |
| RISK-013 | Concurrency namespacing becomes mandatory if Framework-level Skill Return Protocol adopted | Conditional (Low→High) | High | FR-020..FR-022 | L273 |

---

## Domain Distribution

| Domain | Percentage | Primary Keywords Matched |
|--------|-----------|------------------------|
| Backend | 72% | Skill tool, API, service, handler, endpoint, schema, pipeline, YAML, transport, middleware |
| Documentation | 18% | glossary, specification, reference, documentation, rewrite, guide |
| Security | 10% | authentication, authorization, threat, vulnerability, compliance (in spec examples) |

---

*Extraction performed using standard single-pass pipeline (455 lines < 500-line chunked threshold). 28 FRs, 5 NFRs, 12 dependencies, 14 success criteria, 13 risks identified.*
