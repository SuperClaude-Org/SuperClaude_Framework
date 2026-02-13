# Extraction: v1.05-MemoryOpt

## Source
- **Specification**: `.dev/.releases/backlog/v.1.05-MemoryOpt/SPEC.md`
- **Extracted**: 2026-02-13
- **Generator Version**: v2.1

## Extracted Items

| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| REQ-001 | FEATURE | ARCHITECTURE | Cross-file deduplication — establish single-source-of-truth for 6 concept clusters (wave system, persona activation, MCP roles, parallel-first, fallback/recovery, symbol system) across ORCHESTRATOR.md, PERSONAS.md, COMMANDS.md, MCP.md, RULES.md, RESEARCH_CONFIG.md. Target: ≥25KB saved. | None | P0-Critical |
| REQ-002 | FEATURE | ARCHITECTURE | Template abstraction for personas — replace repeated 7-heading structure across 11 personas in PERSONAS.md with shared template declaration + delta-only definitions. Target: ≥35% reduction of PERSONAS.md. | None | P0-Critical |
| IMP-001 | IMPROVEMENT | DOCS | Structure-over-prose conversion — convert verbose prose descriptions and multi-line YAML blocks into tables and concise lists in ORCHESTRATOR.md, RULES.md, MCP.md, COMMANDS.md. Preserve 100% factual content. | None | P1-High |
| REQ-003 | FEATURE | ARCHITECTURE | On-demand loading for specialist files — restructure CLAUDE.md @-references to exclude business panel files (27KB) and RESEARCH_CONFIG.md (9KB) from always-loaded context. Move to skill-activated loading. Target: ≥36KB removed from always-loaded. | REQ-001 | P1-High |
| IMP-002 | IMPROVEMENT | CONFIG | YAML/code block compression — compress RESEARCH_CONFIG.md (91% YAML, 9.6KB) by removing defaults, flattening nested YAML to tables. Target: ≥50% reduction. | None | P1-High |
| IMP-003 | IMPROVEMENT | CONFIG | Example trimming — reduce BUSINESS_PANEL_EXAMPLES.md (77% code, 8.2KB) from 14 examples to ≤5 representative cases. Target: ≥40% reduction. | None | P1-High |
| IMP-004 | IMPROVEMENT | ARCHITECTURE | Internal redundancy elimination — consolidate repeated content within files: ORCHESTRATOR.md wave info (4→1 location), RULES.md parallelism (4→1), MCP.md fallback (2→1), COMMANDS.md wave list (2→1). | REQ-001 | P1-High |
| REF-001 | REFACTOR | ARCHITECTURE | Small file merging — merge 6 MODE_*.md satellite files into MODES.md and 3 MCP_*.md files into MCP.md. Update CLAUDE.md @-references. Reduce file count from 22 to 13. | IMP-004 | P2-Medium |
| REF-002 | REFACTOR | CONFIG | CLAUDE.md @-reference update — restructure entry point file to reflect new file topology after on-demand loading (REQ-003) and file merging (REF-001). | REQ-003, REF-001 | P2-Medium |
| DOC-001 | DOC | DOCS | Compression changelog — document every content change with before/after byte counts, what was removed vs. relocated, and rationale for each decision. | REQ-001, REQ-002, IMP-001, IMP-004 | P2-Medium |
| IMP-005 | IMPROVEMENT | TESTING | A/B validation suite — create and execute 5-task validation suite (T-001 through T-005) testing persona activation, on-demand loading, research config, tier classification, MCP routing. | None | P0-Critical |
| IMP-006 | IMPROVEMENT | TESTING | Token counting validation — implement and run token measurement script after each phase. Verify actual savings within ±15% of estimates. | None | P1-High |
| IMP-007 | IMPROVEMENT | CONFIG | Git checkpoint protocol — create tagged git commits before each phase for rollback capability (<5 min revert). | None | P0-Critical |
| DOC-002 | DOC | DOCS | Dependency graph documentation — create and maintain file dependency graph showing which files reference which, updated after each phase. | REQ-001 | P2-Medium |
| IMP-008 | IMPROVEMENT | ARCHITECTURE | Business panel skill file update — add @-references to skill definition files (commands/business-panel.md, commands/research.md) so specialist context loads on skill invocation. | REQ-003 | P1-High |
| DOC-003 | DOC | DOCS | Post-compression CLAUDE.md verification — verify CLAUDE.md entry point correctly references all core files and no orphaned references remain. Final audit. | REF-001, REF-002 | P1-High |

## Summary Statistics

| Category | Count |
|----------|-------|
| FEATURE (REQ-) | 3 |
| IMPROVEMENT (IMP-) | 8 |
| REFACTOR (REF-) | 2 |
| DOC (DOC-) | 3 |
| **Total** | **16** |

## Domain Distribution

| Domain | Items | Percentage |
|--------|-------|------------|
| ARCHITECTURE | 7 | 44% |
| CONFIG | 3 | 19% |
| DOCS | 3 | 19% |
| TESTING | 2 | 12% |
| **Total** | **16** | **100%** (rounding) |
