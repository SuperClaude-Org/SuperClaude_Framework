# Token Measurements: v1.05-MemoryOpt

## Baseline (Pre-Phase-1)

**Measured**: 2026-02-13T19:52:30+00:00
**SPEC Estimate**: 163,324 bytes (~40,831 tokens)
**Actual**: 163,324 bytes (~40,831 tokens) — **MATCH**

### Core Always-Loaded Files (8 files)

| File | Bytes | ~Tokens |
|------|-------|---------|
| COMMANDS.md | 8,807 | 2,201 |
| FLAGS.md | 4,832 | 1,208 |
| PRINCIPLES.md | 2,573 | 643 |
| RULES.md | 14,168 | 3,542 |
| MCP.md | 14,831 | 3,707 |
| PERSONAS.md | 20,671 | 5,167 |
| ORCHESTRATOR.md | 25,930 | 6,482 |
| MODES.md | 13,829 | 3,457 |
| **Subtotal** | **105,641** | **26,410** |

### On-Demand Files (4 files — target for REQ-003)

| File | Bytes | ~Tokens |
|------|-------|---------|
| MODE_Business_Panel.md | 11,761 | 2,940 |
| BUSINESS_SYMBOLS.md | 7,653 | 1,913 |
| BUSINESS_PANEL_EXAMPLES.md | 8,253 | 2,063 |
| RESEARCH_CONFIG.md | 9,607 | 2,401 |
| **Subtotal** | **37,274** | **9,318** |

### Satellite Files (9 files — target for REF-001 merge)

| File | Bytes | ~Tokens |
|------|-------|---------|
| MODE_Brainstorming.md | 2,132 | 533 |
| MODE_DeepResearch.md | 1,599 | 399 |
| MODE_Introspection.md | 1,862 | 465 |
| MODE_Orchestration.md | 1,710 | 427 |
| MODE_Task_Management.md | 3,574 | 893 |
| MODE_Token_Efficiency.md | 3,029 | 757 |
| MCP_Context7.md | 1,364 | 341 |
| MCP_Sequential.md | 1,651 | 412 |
| MCP_Serena.md | 1,563 | 390 |
| **Subtotal** | **18,484** | **4,621** |

### Entry Point

| File | Bytes | ~Tokens |
|------|-------|---------|
| CLAUDE.md | 1,925 | 481 |

### Summary

| Category | Files | Bytes | ~Tokens | % of Total |
|----------|-------|-------|---------|------------|
| Core always-loaded | 8 | 105,641 | 26,410 | 64.7% |
| On-demand | 4 | 37,274 | 9,318 | 22.8% |
| Satellite | 9 | 18,484 | 4,621 | 11.3% |
| Entry point | 1 | 1,925 | 481 | 1.2% |
| **Grand Total** | **22** | **163,324** | **40,831** | **100%** |

---

## Post-M2 (High-Value Deduplication)

**Measured**: 2026-02-13
**Total**: 137,970 bytes (~34,492 tokens)
**Savings**: 25,354 bytes (~6,338 tokens) — **15.5% reduction**

### Changes Applied
| File | Before | After | Saved | Technique |
|------|--------|-------|-------|-----------|
| PERSONAS.md | 20,671 | 10,299 | 10,372 (50.2%) | Template abstraction: 3 anchor + 8 compact |
| ORCHESTRATOR.md | 25,930 | 18,113 | 7,817 (30.1%) | Cross-file dedup, YAML→tables, wave consolidation |
| MODES.md | 13,829 | 10,442 | 3,387 (24.5%) | Introspection tables, MCP cache dedup |
| MCP.md | 14,831 | 12,260 | 2,571 (17.3%) | Error/Circuit Breaker consolidation |
| COMMANDS.md | 8,807 | 7,600 | 1,207 (13.7%) | YAML→inline command format |

### Core Always-Loaded Files (8 files)

| File | Bytes | ~Tokens |
|------|-------|---------|
| COMMANDS.md | 7,600 | 1,900 |
| FLAGS.md | 4,832 | 1,208 |
| PRINCIPLES.md | 2,573 | 643 |
| RULES.md | 14,168 | 3,542 |
| MCP.md | 12,260 | 3,065 |
| PERSONAS.md | 10,299 | 2,574 |
| ORCHESTRATOR.md | 18,113 | 4,528 |
| MODES.md | 10,442 | 2,610 |
| **Subtotal** | **80,287** | **20,071** |

### Summary

| Category | Files | Bytes | ~Tokens | % of Total |
|----------|-------|-------|---------|------------|
| Core always-loaded | 8 | 80,287 | 20,071 | 58.2% |
| On-demand | 4 | 37,274 | 9,318 | 27.0% |
| Satellite | 9 | 18,484 | 4,621 | 13.4% |
| Entry point | 1 | 1,925 | 481 | 1.4% |
| **Grand Total** | **22** | **137,970** | **34,492** | **100%** |

## Post-M3 (On-Demand + YAML Compression)

**Measured**: 2026-02-13
**Total**: 131,296 bytes (~32,824 tokens)
**Cumulative savings**: 32,028 bytes (~8,007 tokens) — **19.6% reduction from baseline**
**M3 savings**: 6,674 bytes (~1,668 tokens)

### Changes Applied
| File | Before | After | Saved | Technique |
|------|--------|-------|-------|-----------|
| CLAUDE.md | 1,925 | 1,942 | -17 (grew) | On-demand: removed 4 specialist @-refs |
| RESEARCH_CONFIG.md | 9,607 | 4,559 | 5,048 (52.5%) | YAML→inline, verbose→tables, cross-refs |
| BUSINESS_PANEL_EXAMPLES.md | 8,253 | 6,610 | 1,643 (19.9%) | YAML→tables, workflow compression |

### On-Demand Files (4 files — no longer always-loaded via CLAUDE.md)

| File | Bytes | ~Tokens |
|------|-------|---------|
| MODE_Business_Panel.md | 11,761 | 2,940 |
| BUSINESS_SYMBOLS.md | 7,653 | 1,913 |
| BUSINESS_PANEL_EXAMPLES.md | 6,610 | 1,652 |
| RESEARCH_CONFIG.md | 4,559 | 1,139 |
| **Subtotal** | **30,583** | **7,645** |

### Summary

| Category | Files | Bytes | ~Tokens | % of Total |
|----------|-------|-------|---------|------------|
| Core always-loaded | 8 | 80,287 | 20,071 | 61.2% |
| On-demand | 4 | 30,583 | 7,645 | 23.3% |
| Satellite | 9 | 18,484 | 4,621 | 14.1% |
| Entry point | 1 | 1,942 | 485 | 1.5% |
| **Grand Total** | **22** | **131,296** | **32,824** | **100%** |

### Source File Updates (src/superclaude/core/)
| File | Updated | Matches Live |
|------|---------|-------------|
| RESEARCH_CONFIG.md | ✅ | 4,559 bytes |
| BUSINESS_PANEL_EXAMPLES.md | ✅ | 6,610 bytes |

## Post-M4 (Cross-File Consolidation)

_To be measured after M4 completion_

## Post-M5 (File Merging & Final)

_To be measured after M5 completion_
