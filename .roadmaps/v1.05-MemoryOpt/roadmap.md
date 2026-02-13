# Release Roadmap: v1.05-MemoryOpt - Memory Optimization

## Metadata
- **Source Specification**: `.dev/.releases/backlog/v.1.05-MemoryOpt/SPEC.md`
- **Generated**: 2026-02-13T19:45:00Z
- **Generator Version**: v2.1
- **Primary Persona**: Architect — 44% of items are ARCHITECTURE work
- **Consulting Personas**:
  - Refactorer for CONFIG items (19%)
  - Scribe for DOCS items (19%)
  - QA for TESTING items (12%)
- **Rationale**: Architecture-dominant release focusing on structural optimization of the ~/.claude/ file system. Refactorer and Scribe consult on content compression and documentation. QA validates quality preservation.
- **Codebase State**: Branch `Ironbelly/IBv1.4` (to create `feature/v1.05-memory-opt`)
- **Item Count**: 3 features, 8 improvements, 2 refactors, 3 docs

## Executive Summary

This release compresses the SuperClaude framework's ~/.claude/ instruction files from ~163KB (~41K tokens) to ~76-91KB (~19-23K tokens) through cross-file deduplication, on-demand loading, structural optimization, and file merging. The primary outcome is a 44-53% reduction in always-loaded context tokens per Claude Code session, freeing context window for actual user tasks while preserving ≥95% instruction-following quality.

## Milestones Overview

| Milestone | Name | Deliverables | Dependencies | Risk Level |
|-----------|------|--------------|--------------|------------|
| M1 | Foundation & Validation Infrastructure | 4 | None | Low |
| M2 | High-Value Deduplication | 4 | M1 | Low |
| M3 | On-Demand Loading & YAML Compression | 4 | M1, M2 (partial) | Medium |
| M4 | Cross-File Consolidation | 4 | M2 | Low |
| M5 | File Merging & Final Audit | 4 | M3, M4 | Low |

---

### Milestone 1: Foundation & Validation Infrastructure
**Objective**: Establish measurement baseline, validation suite, and rollback infrastructure before any content changes.
**Dependencies**: None
**Estimated Complexity**: Low

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| IMP-007 | IMPROVEMENT | Git checkpoint protocol — create feature branch, establish tagging convention for phase checkpoints | GIVEN the master branch WHEN feature branch is created THEN `feature/v1.05-memory-opt` exists AND tagging convention `checkpoint-phase-N` is documented | `.git/` |
| IMP-005 | IMPROVEMENT | A/B validation suite — define 5 test tasks (T-001..T-005) with expected behaviors for persona activation, on-demand loading, MCP routing, tier classification | GIVEN 5 test task definitions WHEN each task is executed against current (unmodified) files THEN baseline behavior is captured AND all 5 tasks produce expected results | `.roadmaps/v1.05-MemoryOpt/validation-baseline.md` |
| IMP-006 | IMPROVEMENT | Token counting validation — implement measurement script and capture baseline: total bytes, per-file bytes, always-loaded token count | GIVEN all 22 ~/.claude/ files WHEN measurement script runs THEN output matches SPEC §3.1 baseline (163,324 bytes, ~40,831 tokens) within ±5% | `.roadmaps/v1.05-MemoryOpt/token-measurements.md` |
| DOC-002 | DOC | Dependency graph documentation — create initial file dependency graph from SPEC §9B showing @-reference chains and cross-file concept references | GIVEN the current CLAUDE.md @-references WHEN dependency graph is created THEN all 22 files appear with their reference relationships AND graph matches SPEC §9B | `.roadmaps/v1.05-MemoryOpt/dependency-graph.md` |

#### Verification Checkpoint M1
- [ ] Feature branch `feature/v1.05-memory-opt` created from current branch
- [ ] All 5 A/B validation tasks defined with baseline captured
- [ ] Token measurement script produces accurate baseline
- [ ] Dependency graph complete and verified
- [ ] Git tag `checkpoint-pre-phase-1` created
- [ ] No file content modifications made yet

---

### Milestone 2: High-Value Deduplication
**Objective**: Apply cross-file deduplication and template abstraction to the two largest files (ORCHESTRATOR.md 25.9KB, PERSONAS.md 20.7KB) achieving ~18-22KB savings.
**Dependencies**: M1 (validation infrastructure must exist)
**Estimated Complexity**: Medium

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-002 | FEATURE | Template abstraction for personas — convert 11 personas from 7-heading repeated structure to shared template + delta-only cards | GIVEN PERSONAS.md at 20,671 bytes WHEN template abstraction applied THEN file size ≤13,436 bytes (35% reduction) AND all 11 personas individually identifiable AND each persona's MCP prefs, commands, triggers preserved | `~/.claude/PERSONAS.md` |
| REQ-001 | FEATURE | Cross-file deduplication — establish canonical sources for 6 concept clusters, replace duplicates with "See X.md §Y" references | GIVEN 6 identified clusters WHEN dedup applied THEN each cluster has exactly 1 canonical definition AND total bytes saved ≥25,000 across affected files AND no information lost (every concept accessible via reference) | `~/.claude/ORCHESTRATOR.md`, `~/.claude/COMMANDS.md`, `~/.claude/MCP.md`, `~/.claude/RULES.md`, `~/.claude/MODES.md`, `~/.claude/RESEARCH_CONFIG.md` |
| IMP-001 | IMPROVEMENT | Structure-over-prose conversion (Phase 1 targets) — convert ORCHESTRATOR.md complexity detection YAML to tables, convert routing prose to concise format | GIVEN verbose prose sections in ORCHESTRATOR.md WHEN structure conversion applied THEN replacement uses markdown tables or compact lists AND 100% factual content preserved AND fewer bytes than original | `~/.claude/ORCHESTRATOR.md` |
| IMP-004 | IMPROVEMENT | Internal redundancy elimination (ORCHESTRATOR) — consolidate wave info from 4 internal locations to 1, remove persona activation section (now canonical in PERSONAS.md) | GIVEN ORCHESTRATOR.md with wave info at 4 locations and persona activation duplicating PERSONAS.md WHEN internal consolidation applied THEN wave info appears in exactly 1 section AND persona activation section removed (reference to PERSONAS.md instead) | `~/.claude/ORCHESTRATOR.md` |

#### Verification Checkpoint M2
- [ ] PERSONAS.md byte count ≤13,436 (≥35% reduction)
- [ ] ORCHESTRATOR.md byte count reduced by ≥8,000 bytes
- [ ] Total bytes saved across all M2 files ≥18,000
- [ ] A/B validation: T-001 (persona activation) passes
- [ ] A/B validation: T-004 (tier classification) passes
- [ ] A/B validation: T-005 (MCP routing) passes
- [ ] No information lost (diff audit complete)
- [ ] Git tag `checkpoint-post-phase-1` created
- [ ] Token measurement updated

---

### Milestone 3: On-Demand Loading & YAML Compression
**Objective**: Remove specialist files from always-loaded context and compress YAML-heavy files, achieving ~14-17KB additional savings.
**Dependencies**: M1, M2 (REQ-001 must complete for business panel dedup)
**Estimated Complexity**: Medium (highest risk milestone — architectural change)

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REQ-003 | FEATURE | On-demand loading — remove 4 specialist @-references from CLAUDE.md (MODE_Business_Panel.md, BUSINESS_SYMBOLS.md, BUSINESS_PANEL_EXAMPLES.md, RESEARCH_CONFIG.md) | GIVEN CLAUDE.md with @-references to all 22 files WHEN specialist references removed THEN CLAUDE.md references only 8 core files AND always-loaded context decreases by ≥36,000 bytes | `~/.claude/CLAUDE.md` |
| IMP-008 | IMPROVEMENT | Skill file @-reference update — add specialist context @-references to skill definition files so context loads on skill invocation | GIVEN /sc:business-panel skill file WHEN updated with @-references THEN invoking /sc:business-panel loads MODE_Business_Panel.md, BUSINESS_SYMBOLS.md, BUSINESS_PANEL_EXAMPLES.md AND /sc:research loads RESEARCH_CONFIG.md | `commands/business-panel.md`, `commands/research.md` (or equivalent skill paths) |
| IMP-002 | IMPROVEMENT | YAML compression — flatten RESEARCH_CONFIG.md: remove default values, convert nested YAML to tables, remove parallel-first duplication (canonical in RULES.md) | GIVEN RESEARCH_CONFIG.md at 9,607 bytes (91% YAML) WHEN YAML compression applied THEN file size ≤4,804 bytes (≥50% reduction) AND all non-default config values preserved AND depth profiles and credibility tiers retained | `~/.claude/RESEARCH_CONFIG.md` |
| IMP-003 | IMPROVEMENT | Example trimming — reduce BUSINESS_PANEL_EXAMPLES.md from 14 examples to ≤5 representative cases (simple, advanced, workflow integration, multi-doc, learning) | GIVEN BUSINESS_PANEL_EXAMPLES.md at 8,253 bytes (14 examples) WHEN trimming applied THEN ≤5 examples remain AND file size ≤4,952 bytes (≥40% reduction) AND removed examples do not contain unique concepts | `~/.claude/BUSINESS_PANEL_EXAMPLES.md` |

#### Verification Checkpoint M3
- [ ] CLAUDE.md references exactly 8 core files (not 22)
- [ ] `/sc:business-panel` functions correctly with on-demand loaded context
- [ ] `/sc:research` functions correctly with on-demand loaded context
- [ ] A/B validation: T-002 (business panel) passes — CRITICAL
- [ ] A/B validation: T-003 (research config) passes — CRITICAL
- [ ] RESEARCH_CONFIG.md ≤4,804 bytes
- [ ] BUSINESS_PANEL_EXAMPLES.md ≤4,952 bytes
- [ ] Git tag `checkpoint-post-phase-2` created
- [ ] Token measurement updated — always-loaded should be ~96KB

---

### Milestone 4: Cross-File Consolidation
**Objective**: Apply remaining deduplication and internal redundancy elimination to medium-priority files, achieving ~9-12KB additional savings.
**Dependencies**: M2 (canonical sources must be established)
**Estimated Complexity**: Low

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| IMP-004 | IMPROVEMENT | Internal redundancy elimination (remaining files) — MCP.md: consolidate fallback prose+YAML→YAML only. RULES.md: consolidate parallelism 4→1, remove Quick Reference. COMMANDS.md: remove wave list duplication. | GIVEN MCP.md fallback in 2 forms, RULES.md parallelism in 4 sections, COMMANDS.md wave list in 2 locations WHEN consolidation applied THEN each concept appears exactly once per file AND canonical version is the most complete | `~/.claude/MCP.md`, `~/.claude/RULES.md`, `~/.claude/COMMANDS.md` |
| IMP-001 | IMPROVEMENT | Structure-over-prose conversion (Phase 3 targets) — RULES.md decision trees to tables, MCP.md workflow descriptions to concise format | GIVEN verbose prose in RULES.md and MCP.md WHEN conversion applied THEN tables/lists replace prose AND 100% content preserved AND fewer bytes | `~/.claude/RULES.md`, `~/.claude/MCP.md` |
| REQ-001 | FEATURE | Cross-file dedup verification — verify all 6 canonical sources correctly referenced, no orphaned "See X.md §Y" references pointing to removed content | GIVEN completed dedup from M2 WHEN verification run THEN all "See" references resolve to existing sections AND no concept cluster has >1 definition AND all cross-references in ORCHESTRATOR.md, COMMANDS.md, MODES.md are valid | All deduped files |
| DOC-001 | DOC | Compression changelog (interim) — document all M2+M3+M4 changes with before/after byte counts per file, content relocated vs. removed, rationale | GIVEN all changes in M2-M4 WHEN changelog written THEN every modified file has entry AND before/after bytes recorded AND relocated content tracked to new location | `.roadmaps/v1.05-MemoryOpt/compression-changelog.md` |

#### Verification Checkpoint M4
- [ ] MCP.md fallback content in single form (YAML circuit breaker only)
- [ ] RULES.md parallelism consolidated to §Planning Efficiency
- [ ] RULES.md §Quick Reference removed (no unique content)
- [ ] COMMANDS.md wave list appears once (bottom copy removed)
- [ ] All "See X.md §Y" references verified valid
- [ ] A/B validation: T-001 through T-005 all pass
- [ ] Git tag `checkpoint-post-phase-3` created
- [ ] Token measurement updated — always-loaded should be ~84KB

---

### Milestone 5: File Merging & Final Audit
**Objective**: Merge satellite files into parent documents, update all references, perform final validation. Reduce file count from 22 to 13.
**Dependencies**: M3 (MODES.md and MCP.md must be stable), M4
**Estimated Complexity**: Low

#### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| REF-001 | REFACTOR | Small file merging — merge 6 MODE_*.md as sections into MODES.md, merge 3 MCP_*.md as sections into MCP.md. Delete satellite files. | GIVEN 9 satellite files totaling ~19KB WHEN merged into parents THEN all satellite content appears as sections in parent AND satellite files deleted AND file count decreases from 22 to 13 | `~/.claude/MODES.md`, `~/.claude/MCP.md`, 9 satellite files |
| REF-002 | REFACTOR | CLAUDE.md @-reference update — remove all 9 satellite @-references, verify only core files referenced, update any path-based references elsewhere | GIVEN CLAUDE.md with satellite @-references WHEN references updated THEN CLAUDE.md lists exactly 8 core files (post on-demand) AND no orphaned references AND entry point loads correctly | `~/.claude/CLAUDE.md` |
| DOC-003 | DOC | Post-compression verification & final audit — verify CLAUDE.md entry point, run full A/B validation suite, verify token count targets, check for orphaned references, confirm all content traceable | GIVEN all phases complete WHEN final audit runs THEN 0 orphaned references AND all 5 A/B tests pass AND always-loaded tokens ≤23K (moderate target) AND dependency graph updated | All files |
| DOC-001 | DOC | Compression changelog (final) — complete changelog with final byte counts, total savings, quality assessment, lessons learned | GIVEN all phases complete WHEN final changelog written THEN every modified file documented AND total savings calculated AND comparison to SPEC estimates provided | `.roadmaps/v1.05-MemoryOpt/compression-changelog.md` |

#### Verification Checkpoint M5 (Release Gate)
- [ ] File count: 13 (from 22)
- [ ] Always-loaded context: ≤91KB (~23K tokens) — moderate target
- [ ] A/B validation: T-001 through T-005 all pass
- [ ] Token measurement: final count within ±15% of SPEC estimates
- [ ] No orphaned references in any file
- [ ] Compression changelog complete
- [ ] Dependency graph updated to reflect final topology
- [ ] Git tag `v1.05.0-memory-opt` created
- [ ] All checkpoint tags preserved for rollback reference

---

## Dependency Graph

```
IMP-007 (git checkpoints)
IMP-005 (validation suite)      ─── M1 foundation, no deps
IMP-006 (token counting)
DOC-002 (dependency graph)

REQ-002 (persona templates)     ─── M2, no deps
REQ-001 (cross-file dedup)      ─── M2, no deps
IMP-001 (structure-over-prose)  ─── M2 partial, M4 partial, no deps
IMP-004 (internal redundancy)   ─── M2 partial (depends REQ-001), M4 partial

REQ-003 (on-demand loading)     ─── M3, depends REQ-001
IMP-008 (skill file update)     ─── M3, depends REQ-003
IMP-002 (YAML compression)     ─── M3, no deps
IMP-003 (example trimming)     ─── M3, no deps

DOC-001 (changelog)             ─── M4 interim, M5 final, depends REQ-001/002, IMP-001/004

REF-001 (file merging)          ─── M5, depends IMP-004
REF-002 (CLAUDE.md update)      ─── M5, depends REQ-003, REF-001
DOC-003 (final audit)           ─── M5, depends REF-001, REF-002
```

**Critical Path**: IMP-007 → REQ-001 → REQ-003 → IMP-008 → REF-001 → REF-002 → DOC-003

## Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-001 | "See X.md §Y" cross-references not followed by Claude | Low | Medium | Use specific section anchors; test each reference in A/B suite |
| R-002 | On-demand skill files don't receive specialist context | Medium | High | Test /sc:business-panel and /sc:research after REQ-003; verify skill file @-references load correctly |
| R-003 | Template-abstracted personas harder for Claude to parse | Low | Medium | Keep 2-3 anchor personas in expanded format; test all persona keywords |
| R-004 | YAML compression removes non-obvious meaningful config | Low | Low | Diff every YAML change; these are instructional only, not executable |
| R-005 | Quick Reference removal in RULES.md loses navigability | Medium | Low | Rules themselves serve as reference; test multi-rule scenarios |
| R-006 | Merged parent files become too large for efficient parsing | Low | Low | MODES.md grows to ~28KB — smaller than current ORCHESTRATOR.md |
| R-007 | Cumulative small losses compound to >5% quality drop | Low | Medium | A/B test after each milestone (not just at end); canary approach |
