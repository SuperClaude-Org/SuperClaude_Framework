---
spec_source: .dev/releases/current/v2.0-roadmap-v2/SC-ROADMAP-V2-SPEC.md
generated_by: sc:roadmap
generated_at: "2026-02-21"
depth: standard
complexity_score: 0.645
complexity_class: MEDIUM
primary_persona: architect
domain_distribution:
  backend: 53
  architecture: 29
  quality: 12
  frontend: 6
total_requirements: 20
total_deliverables: 37
---

# Extraction: SC-ROADMAP-V2-SPEC

## Functional Requirements

| ID | Requirement | Domain | Priority | Source Line(s) |
|----|-------------|--------|----------|----------------|
| FR-001 | Single-Spec Roadmap Generation: 5-wave pipeline producing roadmap.md, extraction.md, test-strategy.md with YAML frontmatter | backend | P0 | L87-L95 |
| FR-002 | Multi-Spec Consolidation: --specs flag invokes sc:adversarial --compare to produce unified spec | architecture | P1 | L96-L110 |
| FR-003 | Multi-Roadmap Generation: --multi-roadmap --agents invokes sc:adversarial --generate with 2-10 agent variants | architecture | P1 | L111-L130 |
| FR-004 | Agent Specification Format: model:persona:"instruction" parsing with model-only shorthand, orchestrator at ≥5 agents | backend | P1 | L131-L190 |
| FR-005 | Combined Mode: chains multi-spec consolidation + multi-roadmap generation sequentially | architecture | P2 | L191-L200 |
| FR-006 | YAML Frontmatter Contract: spec_source/spec_sources mutual exclusion, typed fields, versioned schema (additions only) | backend | P0 | L201-L280 |
| FR-007 | Continuous Parallel Validation: test-strategy.md with interleave ratios (LOW=1:3, MEDIUM=1:2, HIGH=1:1), stop-and-fix thresholds | quality | P1 | L281-L310 |
| FR-008 | Quality Gate Validation: Wave 4 PASS(≥85%)/REVISE(70-84%)/REJECT(<70%) scoring via quality-engineer + self-review agents | quality | P1 | L311-L340 |
| FR-009 | Depth Configuration: quick/standard/deep mapping to wave execution depth and adversarial depth | backend | P1 | L341-L370 |
| FR-010 | SKILL.md Split Pattern: lean ~400 line behavioral SKILL.md + refs/ directory with 5 reference files | architecture | P0 | L60-L86 |
| FR-011 | On-Demand Ref Loading: refs loaded per-wave (max 2-3 at any point), never pre-loaded | architecture | P0 | L76-L86 |
| FR-012 | Command File Definition: roadmap.md command file with flags, usage, examples, boundaries | backend | P1 | L371-L400 |
| FR-013 | Template Discovery: 4-tier search (local → user → plugin [future: v5.0] → inline generation) | backend | P1 | L886-L894 |
| FR-014 | Inline Template Generation: fallback when tiers 1-3 produce no match; generates template from domain analysis | backend | P2 | L891 |
| FR-015 | Progress Reporting: wave boundary emissions reporting current wave, elapsed time, next steps | backend | P1 | L957 |
| FR-016 | Chunked Extraction Protocol: >500 line activation, section indexing, chunk assembly, 4-pass completeness verification | backend | P1 | L862-L868 |
| FR-017 | Interactive Mode: --interactive flag for user prompts at decision points and adversarial convergence | frontend | P2 | L953 |

## Non-Functional Requirements

| ID | Requirement | Category | Constraint |
|----|-------------|----------|------------|
| NFR-001 | SKILL.md ≤500 lines with no YAML pseudocode | maintainability | Hard line limit enforced |
| NFR-002 | Ref files loaded on-demand, max 2-3 at any point | performance | Context window budget constraint |
| NFR-003 | YAML frontmatter parseable by standard YAML parsers | interoperability | Standard YAML 1.2 compliance |

## Domain Distribution

| Domain | Percentage | Key Indicators |
|--------|-----------|----------------|
| backend | 53% | Pipeline orchestration, flag parsing, agent specification, template discovery, progress reporting, chunked extraction |
| architecture | 29% | SKILL.md split, ref loading protocol, multi-spec consolidation, multi-roadmap generation, combined mode |
| quality | 12% | Continuous parallel validation, quality gate validation, REVISE loop, test-strategy authoring |
| frontend | 6% | Interactive mode, user prompts |

## Complexity Analysis

| Factor | Raw Value | Normalized (0-1) | Weight | Weighted Score |
|--------|-----------|-------------------|--------|----------------|
| requirement_count | 20 | 0.70 | 0.25 | 0.175 |
| dependency_depth | 5-wave + sc:adversarial + refs | 0.65 | 0.25 | 0.163 |
| domain_spread | 4 domains | 0.60 | 0.20 | 0.120 |
| risk_severity | 9 risks, 3 High impact | 0.60 | 0.15 | 0.090 |
| scope_size | 7 new files + 1 update | 0.65 | 0.15 | 0.098 |
| **Total** | | | | **0.645** |

**Complexity Class**: MEDIUM

## Persona Assignment

| Role | Persona | Confidence | Rationale |
|------|---------|------------|-----------|
| Primary | architect | 0.82 | Pipeline orchestration, system design, ref architecture |
| Consulting | backend | 0.75 | Implementation details, flag parsing, extraction logic |
| Consulting | qa | 0.68 | Validation pipeline, test-strategy, quality gates |

## Dependencies

| ID | Dependency | Type | Affected Requirements |
|----|------------|------|----------------------|
| DEP-001 | sc:adversarial skill implemented and available | internal | FR-002, FR-003, FR-005 |
| DEP-002 | sc:save/sc:load skills for session persistence | internal | Section 7.3 |
| DEP-003 | Serena MCP server for cross-session memory | external | Section 7.3 |
| DEP-004 | Sequential MCP server for analysis reasoning | external | Waves 1-4 |
| DEP-005 | Context7 MCP server for template/pattern lookups | external | Waves 1-2 |
| DEP-006 | Existing roadmap.md command file at src/superclaude/commands/ | internal | FR-012 |

## Risks

| ID | Risk | Probability | Impact | Affected Requirements |
|----|------|-------------|--------|----------------------|
| RISK-001 | SKILL.md split causes Claude to miss ref files | Medium | High | FR-010, FR-011 |
| RISK-002 | sc:adversarial unavailable/not installed | Low | High | FR-002, FR-003, FR-005 |
| RISK-003 | Frontmatter schema breaks future tasklist generator | Medium | Medium | FR-006 |
| RISK-004 | Multi-spec mode produces incoherent unified spec | Medium | Medium | FR-002 |
| RISK-005 | Combined mode takes too long (two adversarial passes) | Medium | Low | FR-005 |
| RISK-006 | Adversarial partial status causes silent quality degradation | Medium | Medium | FR-002, FR-003 |
| RISK-007 | Large spec files overwhelm context window | Medium | High | FR-016 |
| RISK-008 | Interrupted session produces partial/stale artifacts | Low | Medium | Section 7.3 |
| RISK-009 | Unrecognized model in --agents causes late failure | Low | Medium | FR-004 |

## Success Criteria

| ID | Criterion | Derived From | Measurable |
|----|-----------|-------------|------------|
| SC-001 | Single-spec produces 3 artifacts with valid YAML frontmatter | FR-001, FR-006, NFR-003 | Yes |
| SC-002 | --specs invokes sc:adversarial and produces unified spec | FR-002, DEP-001 | Yes |
| SC-003 | --multi-roadmap --agents produces merged roadmap | FR-003, FR-004 | Yes |
| SC-004 | Combined mode chains both adversarial modes | FR-005 | Yes |
| SC-005 | Wave 4 produces PASS/REVISE/REJECT with score | FR-008 | Yes |
| SC-006 | REVISE loop re-runs Wave 3→4 up to 2 iterations | FR-008 | Yes |
| SC-007 | SKILL.md ≤500 lines with refs/ directory | FR-010, NFR-001 | Yes |
| SC-008 | Refs loaded on-demand, max 2-3 at any point | FR-011, NFR-002 | Yes |
| SC-009 | Output collision appends -N suffix | Section 5.1 | Yes |
| SC-010 | Chunked extraction activates for >500 line specs | FR-016 | Yes |
| SC-011 | sc:save triggered at each wave boundary | Section 7.3 | Yes |
| SC-012 | test-strategy.md encodes continuous parallel validation | FR-007 | Yes |
| SC-013 | Decision Summary section in roadmap.md | Section 8.1 | Yes |

## Warnings

- sc:adversarial dependency (DEP-001) is critical for multi-spec and multi-roadmap modes. If not yet implemented, those modes will be blocked. Single-spec mode is independent.
- The plugin tier in template discovery (FR-013, tier 3) is annotated as `[future: v5.0]` and should not be implemented now — only the placeholder/comment needs to exist.
- Chunked extraction protocol (FR-016) requires careful implementation to ensure the 4-pass completeness verification is robust. Anti-hallucination pass has zero tolerance.
