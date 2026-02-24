---
spec_source: .dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md
generated: 2026-02-24T00:00:00Z
generator: sc:roadmap
functional_requirements: 26
nonfunctional_requirements: 7
total_requirements: 33
domains_detected: [backend, infrastructure, architecture, documentation]
complexity_score: 0.727
complexity_class: HIGH
risks_identified: 7
dependencies_identified: 9
success_criteria_count: 10
extraction_mode: chunked (3 chunks)
---

# Extraction: v2.01 Architecture Refactor

## Project Summary

**Title**: v2.01 Architecture Refactor
**Version**: v2.01
**Summary**: Strict architectural refactor of the SuperClaude Framework enforcing clean separation between Commands (thin entry points), Skills (full behavioral protocols), and Refs (step-specific detail). Fixes root causes of agents not following `/sc:command` instructions. Not a feature release.

---

## Functional Requirements

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-001 | Create formal architecture policy document (`docs/architecture/command-skill-policy.md`) | documentation | P0 | L48 |
| FR-002 | Rename 5 skill directories with `-protocol` suffix (`sc-adversarial`, `sc-cleanup-audit`, `sc-roadmap`, `sc-task-unified`, `sc-validate-tests`) | backend | P0 | L463-481 |
| FR-003 | Refactor 5 command files with mandatory `## Activation` sections pointing to protocol skills | backend | P0 | L50, L277-303 |
| FR-004 | Implement `make lint-architecture` CI target with 6 of 10 designed policy checks | infrastructure | P0 | L661-688 |
| FR-005 | Remove skill-skip heuristic from `make sync-dev` (4-line removal) | infrastructure | P0 | L690-694 |
| FR-006 | Remove skip heuristic from `make verify-sync` (5-line removal) | infrastructure | P0 | L696-700 |
| FR-007 | Implement fallback invocation protocol F1/F2-3/F4-5 for Wave 2 Step 3 | backend | P0 | L576-608 |
| FR-008 | Define canonical 10-field return contract schema with YAML file-based transport | backend | P0 | L618-654 |
| FR-009 | Fix BUG-001: Add `Skill` to `allowed-tools` in all 5 paired command files | backend | P0 | L754 |
| FR-010 | Fix BUG-006: Rewrite `roadmap.md` `## Activation` to reference `Skill sc:roadmap-protocol` | backend | P0 | L759 |
| FR-011 | Fix BUG-002: Update `validate-tests.md` line 63 stale path to `sc-validate-tests-protocol/` | backend | P1 | L755 |
| FR-012 | Fix BUG-003: Align orchestrator threshold to `>= 3` across all references | backend | P1 | L756 |
| FR-013 | Fix BUG-004: Resolve architecture policy duplication (designate canonical, symlink) | documentation | P1 | L757 |
| FR-014 | Fix BUG-005: Update Wave 0 Step 5 stale path to `sc-adversarial-protocol/SKILL.md` | backend | P1 | L758 |
| FR-015 | Decompose Wave 2 Step 3 into 6 atomic sub-steps (3a-3f) with explicit tool bindings | backend | P0 | L577-607 |
| FR-016 | Execute T01.01 Skill tool probe to verify TOOL_NOT_AVAILABLE in current environment | backend | P0 | L776 |
| FR-017 | Document cross-skill invocation patterns | documentation | P1 | L839 |
| FR-018 | Design Tier 2 ref loader (`claude -p` script pattern) | architecture | P1 | L840 |
| FR-019 | Extract `task-unified.md` from 567 to ≤106 lines | backend | P1 | L841 |
| FR-020 | Add `## Activation` and fix BUG-001 for remaining 4 command files (adversarial, cleanup-audit, task-unified, validate-tests) | backend | P0 | L842 |
| FR-021 | Create verb-to-tool glossary (disambiguates "Invoke" → Bash/`claude -p` vs "Dispatch" → Task tool) | documentation | P1 | L829 |
| FR-022 | Fix Wave 1A Step 2 semantic alignment | backend | P1 | L830 |
| FR-023 | Convert pseudo-CLI invocations to executable patterns | backend | P1 | L831 |
| FR-024 | Implement return contract consumer routing tests (Pass/Partial/Fail) | backend | P0 | L819 |
| FR-025 | Implement adversarial pipeline integration tests | backend | P0 | L820 |
| FR-026 | Define artifact gate specification and standards | architecture | P0 | L821 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | Command files must be ≤150 lines (target), hard limit ≤350 lines when paired with protocol skill | maintainability | WARN at 350, ERROR at 500 | L297 |
| NFR-002 | Protocol skills have no size limit but should split deep detail into refs/ for context efficiency | maintainability | Prefer refs/ for step-specific detail | L370 |
| NFR-003 | Ref files must be independently useful with no dangling references requiring SKILL.md context | maintainability | `## Purpose` section required | L400 |
| NFR-004 | All changes within a command group must be applied atomically (no partial application) | reliability | 4 files per atomic group | L880-898 |
| NFR-005 | `make lint-architecture` must exit 1 on any ERROR-severity check failure | reliability | Zero ERROR tolerance at CI | L688 |
| NFR-006 | Zero tolerance for partial migration — breaks invocation wiring for all affected commands | reliability | Full atomic migration required | L1047-1058 |
| NFR-007 | Executable `.md` files (skills/commands/agents) are NOT exempt from compliance classification | compliance | STANDARD minimum tier | L778 |

---

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|-----------------------|
| DEP-001 | Phase 2 (Invocation Wiring) blocked on Phase 1 (Foundation) completion | internal | FR-007, FR-009, FR-010, FR-015 |
| DEP-002 | Phase 3 (Build System) MUST precede Phase 4 — enforcement before migration (Rule 7.5) | internal | FR-004, FR-005, FR-006 |
| DEP-003 | Phase 4 (Structural Validation) blocked on Phase 3 completion | internal | FR-024, FR-025, FR-026 |
| DEP-004 | All 5 skill directory renames must precede command file updates (Layer 1 before Layer 3) | internal | FR-002, FR-003, FR-020 |
| DEP-005 | `make lint-architecture` must pass before any Phase 4 work begins | internal | FR-004, FR-024 |
| DEP-006 | BUG-001 (`Skill` in `allowed-tools`) must be fixed before command refactoring is functional | internal | FR-009, FR-003 |
| DEP-007 | `src/` changes must precede `.claude/` dev copies via `make sync-dev` | internal | FR-002, FR-003, FR-005 |
| DEP-008 | Architecture policy document must exist before skill renames begin (Layer 0 before Layer 1) | internal | FR-001, FR-002 |
| DEP-009 | T01.01 probe result determines FALLBACK-ONLY variant, gating Wave 2 design decisions | internal | FR-016, FR-007, FR-015 |

**Maximum dependency chain depth**: 5 (DEP-008 → DEP-004 → DEP-005 → DEP-003 → Phase 4 tests)

---

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|------------|
| SC-001 | All 5 skill directories renamed with `-protocol` suffix and passing naming validation | FR-002 | Yes |
| SC-002 | All 5 paired commands have `## Activation` sections referencing correct `Skill sc:<name>-protocol` | FR-003, FR-010, FR-020 | Yes |
| SC-003 | All 5 paired commands have `Skill` in `allowed-tools` frontmatter | FR-009, FR-020 | Yes |
| SC-004 | `make lint-architecture` exits 0 on the final codebase state | FR-004 | Yes |
| SC-005 | `make sync-dev && make verify-sync` both pass with zero drift | FR-005, FR-006 | Yes |
| SC-006 | Wave 2 Step 3 passes 8-point structural audit | FR-015 | Yes |
| SC-007 | Return contract routing correctly handles Pass (≥0.6), Partial (≥0.5), Fail (<0.5) | FR-008, FR-024 | Yes |
| SC-008 | All BUG-001 through BUG-006 resolved with no regressions | FR-009 through FR-014 | Yes |
| SC-009 | Zero stale references to old skill directory names (`sc-adversarial/`, `sc-cleanup-audit/`, `sc-roadmap/`, `sc-task-unified/`, `sc-validate-tests/`) | FR-002 | Yes |
| SC-010 | `task-unified.md` reduced to ≤106 lines with functional parity | FR-019 | Yes |

---

## Risks

| ID | Description | Probability | Impact | Affected Requirements | Source |
|----|-------------|-------------|--------|----------------------|--------|
| RISK-001 | Partial application of changes breaks all invocation wiring (68-file incident repeat) | High | High | FR-002, FR-003, FR-009, NFR-004, NFR-006 | L1047-1058 |
| RISK-002 | Rogue agent untrusted staged changes on branch contaminate new work | Medium | High | FR-002 | L471 |
| RISK-003 | TOOL_NOT_AVAILABLE probe result may have changed in current environment | Low | Medium | FR-016, FR-007 | L572 |
| RISK-004 | Runtime scope control remains unsolved — agents can exceed planned file count (OUT OF SCOPE) | High | High | NFR-004 | L1078-1088 |
| RISK-005 | 4 unimplemented CI checks (checks 5, 7 need design) leave enforcement gaps | Medium | Medium | FR-004 | L681-683 |
| RISK-006 | Context compaction may drop `## Activation` directive silently | Medium | High | FR-003, FR-020 | L170 |
| RISK-007 | Zero test coverage for activation flow creates undetectable regression risk | High | Medium | FR-024, FR-025 | L1063-1068 |

---

## Domain Distribution

| Domain | Percentage | Requirement Count |
|--------|-----------|-------------------|
| Backend (framework internals) | 40% | 18 FRs |
| Infrastructure / DevOps | 25% | 3 FRs + 4 NFRs |
| Architecture | 20% | 2 FRs + design influence on all |
| Documentation | 10% | 4 FRs |
| Quality / Testing | 5% | 3 FRs (Phase 4) |

---

*Extraction generated by sc:roadmap from sprint-spec.md (1176 lines, chunked extraction)*
