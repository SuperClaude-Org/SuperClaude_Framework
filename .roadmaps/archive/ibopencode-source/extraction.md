# Extraction: v3.0 Roadmap-Generator

> **Source**: `.dev/plans/v3.0_Roadmaps/v3.0_Roadmap-Generator-Specification.md`
> **Generated**: 2026-01-06
> **Generator Version**: v2.0

## Extracted Items

| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| REQ-001 | FEATURE | ARCHITECTURE | Command definition file `/rf:roadmap-gen` with full syntax, options parsing, and routing to orchestrator | None | P0-Critical |
| REQ-002 | FEATURE | ARCHITECTURE | Orchestrator agent skeleton with 9-phase pipeline structure (Phases 0-7.5) | REQ-001 | P0-Critical |
| REQ-003 | FEATURE | BACKEND | Preflight validation (Phase 0): Input file existence, actionable content check, output directory creation | REQ-002 | P1-High |
| REQ-004 | FEATURE | BACKEND | Input extraction (Phase 1): Parse specification, assign unique IDs (REQ/BUG/IMP/REF/DOC), normalize types, categorize domains, identify dependencies, extract priorities | REQ-003 | P1-High |
| REQ-005 | FEATURE | BACKEND | Persona selection (Phase 2): Calculate domain distribution, select primary persona (>40%), identify consulting personas (>15%), document rationale | REQ-004 | P1-High |
| REQ-006 | FEATURE | BACKEND | Template evaluation (Phase 2.5): Load templates from `.opencode/resources/templates/roadmaps/`, score against extraction+persona, select or create variant | REQ-005 | P1-High |
| REQ-007 | FEATURE | BACKEND | Template scorer agent with CoT-designed scoring algorithm (domain alignment, structure fit, complexity match) | REQ-006 | P1-High |
| DOC-001 | DOC | DOCS | Create feature-release.md starter template with Feature Breakdown, API Changes, Migration Notes, Deprecation Warnings sections | None | P1-High |
| DOC-002 | DOC | DOCS | Create quality-release.md starter template with Test Coverage Matrix, Performance Benchmarks, Security Checklist sections | None | P1-High |
| DOC-003 | DOC | DOCS | Create documentation-release.md starter template with Content Structure, Migration Guide, Cross-refs, Version History sections | None | P1-High |
| REQ-008 | FEATURE | BACKEND | Roadmap construction (Phase 3): Transform extracted items into dependency-ordered milestones with acceptance criteria and traceability using selected template | REQ-006, REQ-007 | P1-High |
| REQ-009 | FEATURE | BACKEND | Test strategy generation (Phase 4): Create test-strategy.md with unit/integration/regression/acceptance test matrix per deliverable | REQ-008 | P1-High |
| REQ-010 | FEATURE | BACKEND | Execution prompt generation (Phase 5): Create execution-prompt.md with context loading, execution rules, task patterns, verification checkpoints | REQ-009 | P1-High |
| REQ-011 | FEATURE | BACKEND | Self-validation (Phase 6): Verify artifact completeness, traceability, schema compliance, cross-reference integrity | REQ-010 | P1-High |
| REQ-012 | FEATURE | ARCHITECTURE | crossLLM integration (Phase 7): Implement Integration Protocol - invoke `/rf:crossLLM v2 file <chain>` for each upgradeable artifact | REQ-011 | P0-Critical |
| REQ-013 | FEATURE | ARCHITECTURE | Parallel upgrade execution: Run crossLLM upgrades for roadmap.md, test-strategy.md, execution-prompt.md concurrently | REQ-012 | P1-High |
| REQ-014 | FEATURE | BACKEND | Draft preservation: Copy artifact to .draft.md before upgrade, restore on failure | REQ-012 | P1-High |
| REQ-015 | FEATURE | BACKEND | Circuit breaker: Stop upgrades if ≥50% artifacts fail, preserve drafts for remaining | REQ-012 | P1-High |
| REQ-016 | FEATURE | BACKEND | Upgrade log generation: Create upgrade-log.md with configuration, per-artifact results, summary | REQ-012 | P1-High |
| REQ-017 | FEATURE | BACKEND | Cross-artifact consistency validation (Phase 7.5): Verify ID reference integrity, coverage completeness, structural alignment, naming consistency | REQ-013 | P1-High |
| REQ-018 | FEATURE | BACKEND | Consistency report generation: Create consistency-report.md documenting validation findings | REQ-017 | P2-Medium |
| REQ-019 | FEATURE | BACKEND | Multi-iteration upgrade support: Chain cycling (claude>gpt → gpt>gemini → gemini>claude) for --version N>2 | REQ-012 | P2-Medium |
| REQ-020 | FEATURE | BACKEND | Version folder management: Create v1/, v2/, v3/... folders for draft and each upgrade iteration | REQ-012 | P1-High |
| IMP-001 | IMPROVEMENT | BACKEND | --chain flag: Override first iteration chain (default: claude>gpt) | REQ-012 | P2-Medium |
| IMP-002 | IMPROVEMENT | BACKEND | --upgrade-threshold flag: Configurable minimum improvement percentage (default: 25%) | REQ-012 | P2-Medium |
| IMP-003 | IMPROVEMENT | BACKEND | --upgrade-only flag: Upgrade specific artifacts only (comma-separated list) | REQ-012 | P2-Medium |
| IMP-004 | IMPROVEMENT | BACKEND | --sequential-upgrades flag: Force sequential upgrade execution for debugging | REQ-013 | P2-Medium |
| IMP-005 | IMPROVEMENT | BACKEND | --output flag: Custom output directory name (default: derived from input spec filename) | REQ-002 | P2-Medium |
| DOC-004 | DOC | DOCS | User documentation: Usage guide for /rf:roadmap-gen command | REQ-001 | P1-High |
| DOC-005 | DOC | DOCS | Technical documentation: Architecture, agent specifications, integration protocol reference | REQ-002 | P1-High |
| REF-001 | REFACTOR | ARCHITECTURE | Extract Integration Protocol to standalone reusable document for future commands | REQ-012 | P2-Medium |

## Summary

| Type | Count | Percentage |
|------|-------|------------|
| FEATURE | 20 | 64.5% |
| DOC | 5 | 16.1% |
| IMPROVEMENT | 5 | 16.1% |
| REFACTOR | 1 | 3.2% |
| **Total** | **31** | **100%** |

## Domain Distribution

| Domain | Count | Percentage |
|--------|-------|------------|
| BACKEND | 17 | 54.8% |
| ARCHITECTURE | 5 | 16.1% |
| DOCS | 5 | 16.1% |
| *(None)* | 4 | 12.9% |

---

*Extraction complete. 31 items identified.*
