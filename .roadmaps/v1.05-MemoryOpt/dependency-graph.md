# Dependency Graph: v1.05-MemoryOpt

**Generated**: 2026-02-13
**State**: Pre-compression baseline (checkpoint-pre-phase-1)

## File Inventory (22 framework files)

| # | File | Bytes | Category | @-Referenced by CLAUDE.md |
|---|------|-------|----------|---------------------------|
| 1 | CLAUDE.md | 1,925 | Entry Point | N/A (is entry point) |
| 2 | COMMANDS.md | 8,807 | Core | Yes |
| 3 | FLAGS.md | 4,832 | Core | Yes |
| 4 | PRINCIPLES.md | 2,573 | Core | Yes |
| 5 | RULES.md | 14,168 | Core | Yes |
| 6 | MCP.md | 14,831 | Core | Yes |
| 7 | PERSONAS.md | 20,671 | Core | Yes |
| 8 | ORCHESTRATOR.md | 25,930 | Core | Yes |
| 9 | MODES.md | 13,829 | Core | Yes |
| 10 | BUSINESS_PANEL_EXAMPLES.md | 8,253 | Specialist | Yes |
| 11 | BUSINESS_SYMBOLS.md | 7,653 | Specialist | Yes |
| 12 | RESEARCH_CONFIG.md | 9,607 | Specialist | Yes |
| 13 | MODE_Business_Panel.md | 11,761 | Specialist | Yes |
| 14 | MODE_Brainstorming.md | 2,132 | Satellite | Yes |
| 15 | MODE_DeepResearch.md | 1,599 | Satellite | Yes |
| 16 | MODE_Introspection.md | 1,862 | Satellite | Yes |
| 17 | MODE_Orchestration.md | 1,710 | Satellite | Yes |
| 18 | MODE_Task_Management.md | 3,574 | Satellite | Yes |
| 19 | MODE_Token_Efficiency.md | 3,029 | Satellite | Yes |
| 20 | MCP_Context7.md | 1,364 | Satellite | Yes |
| 21 | MCP_Sequential.md | 1,651 | Satellite | Yes |
| 22 | MCP_Serena.md | 1,563 | Satellite | Yes |

## @-Reference Topology (CLAUDE.md Entry Point)

```
CLAUDE.md (entry point, 1,925 bytes)
├── @COMMANDS.md          (8,807)  ─── Core
├── @FLAGS.md             (4,832)  ─── Core
├── @PRINCIPLES.md        (2,573)  ─── Core
├── @RULES.md             (14,168) ─── Core
├── @MCP.md               (14,831) ─── Core
├── @PERSONAS.md          (20,671) ─── Core
├── @ORCHESTRATOR.md      (25,930) ─── Core
├── @MODES.md             (13,829) ─── Core
├── @BUSINESS_PANEL_EXAMPLES.md  (8,253)  ─── Specialist (→ on-demand M3)
├── @BUSINESS_SYMBOLS.md         (7,653)  ─── Specialist (→ on-demand M3)
├── @RESEARCH_CONFIG.md          (9,607)  ─── Specialist (→ on-demand M3)
├── @MODE_Business_Panel.md      (11,761) ─── Specialist (→ on-demand M3)
├── @MODE_Brainstorming.md       (2,132)  ─── Satellite (→ merge M5)
├── @MODE_DeepResearch.md        (1,599)  ─── Satellite (→ merge M5)
├── @MODE_Introspection.md       (1,862)  ─── Satellite (→ merge M5)
├── @MODE_Orchestration.md       (1,710)  ─── Satellite (→ merge M5)
├── @MODE_Task_Management.md     (3,574)  ─── Satellite (→ merge M5)
├── @MODE_Token_Efficiency.md    (3,029)  ─── Satellite (→ merge M5)
├── @MCP_Context7.md             (1,364)  ─── Satellite (→ merge M5)
├── @MCP_Sequential.md           (1,651)  ─── Satellite (→ merge M5)
└── @MCP_Serena.md               (1,563)  ─── Satellite (→ merge M5)
```

**Total always-loaded**: All 22 files = 163,324 bytes (~40,831 tokens)

## Cross-File Reference Map

### Internal "See X.md" References (within framework files)

```
ORCHESTRATOR.md
├── "See MCP.md" (×2) — server capabilities, orchestration patterns
└── "See PERSONAS.md" (×1) — persona specifications

MODES.md
├── mentions PRINCIPLES.md — compliance checking
└── mentions RULES.md — compliance checking
```

**Note**: No `§` (section anchor) references found in current files. The dedup plan will introduce "See X.md §Section" references.

### Cross-File Concept Duplication Clusters

These are concepts that appear in multiple files without explicit cross-references:

#### Cluster 1: Wave System (3 locations)
```
COMMANDS.md §Wave System Integration    ← Canonical (M2)
ORCHESTRATOR.md §Wave Orchestration Engine   ← Duplicate detail
MODE_Business_Panel.md §Wave Mode Integration   ← Duplicate detail
```

#### Cluster 2: Persona Activation (3 locations)
```
PERSONAS.md §Auto-Activation Triggers    ← Canonical (M2)
ORCHESTRATOR.md §Persona Auto-Activation System   ← Duplicate detail
ORCHESTRATOR.md §Flag Auto-Activation Patterns   ← Duplicate detail
```

#### Cluster 3: MCP Server Selection (4 locations)
```
MCP.md §Server Selection Algorithm    ← Canonical (M2)
ORCHESTRATOR.md §MCP Server Selection Matrix   ← Summary reference
ORCHESTRATOR.md §Intelligent Server Coordination   ← Summary reference
MODES.md §MCP Optimization & Caching   ← Duplicate detail
```

#### Cluster 4: Parallel-First Doctrine (3 locations)
```
RULES.md §Planning Efficiency    ← Canonical (M2)
RESEARCH_CONFIG.md §parallel_execution_rules   ← Duplicate detail
ORCHESTRATOR.md §Operation Batching   ← Duplicate detail
```

#### Cluster 5: Fallback/Recovery (3 locations)
```
MCP.md §Circuit Breaker Configuration    ← Canonical (M2)
MCP.md §Error Handling and Recovery   ← Duplicate prose
ORCHESTRATOR.md §Graceful Degradation   ← Duplicate detail
```

#### Cluster 6: Symbol/Compression System (2 locations)
```
MODES.md §Token Efficiency Mode    ← Canonical (M2)
BUSINESS_SYMBOLS.md §Token Efficiency Integration   ← Business-specific extension
```

## Target Topology (Post-M5)

```
CLAUDE.md (entry point, reduced)
├── @COMMANDS.md          ─── Core (compressed)
├── @FLAGS.md             ─── Core (unchanged)
├── @PRINCIPLES.md        ─── Core (unchanged)
├── @RULES.md             ─── Core (compressed)
├── @MCP.md               ─── Core (compressed + 3 MCP_*.md merged in)
├── @PERSONAS.md          ─── Core (template-abstracted)
├── @ORCHESTRATOR.md      ─── Core (deduped + compressed)
└── @MODES.md             ─── Core (compressed + 6 MODE_*.md merged in)

On-demand (loaded via skill @-references):
├── MODE_Business_Panel.md    ─── via /sc:business-panel skill
├── BUSINESS_SYMBOLS.md       ─── via /sc:business-panel skill
├── BUSINESS_PANEL_EXAMPLES.md ─── via /sc:business-panel skill (trimmed)
└── RESEARCH_CONFIG.md        ─── via /sc:research skill (compressed)
```

**Target always-loaded**: 8 core files + CLAUDE.md = ≤91KB (~23K tokens)
**Target file count**: 13 (from 22)

## Transformation Plan Summary

| Phase | Action | Files Affected | Expected Savings |
|-------|--------|----------------|------------------|
| M2 | Dedup + template abstraction | PERSONAS.md, ORCHESTRATOR.md, COMMANDS.md, MCP.md, RULES.md, MODES.md | ~18-22KB |
| M3 | On-demand loading | CLAUDE.md (remove 4 @-refs), skill files (add @-refs) | ~37KB from always-loaded |
| M3 | YAML compression | RESEARCH_CONFIG.md, BUSINESS_PANEL_EXAMPLES.md | ~8KB |
| M4 | Internal consolidation | MCP.md, RULES.md, COMMANDS.md | ~9-12KB |
| M5 | File merging | 9 satellites → MODES.md + MCP.md | File count 22→13 |
