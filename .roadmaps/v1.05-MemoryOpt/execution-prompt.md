# Execution Instructions: v1.05-MemoryOpt - Memory Optimization

## Context Loading (READ THESE FIRST)
1. **Source specification**: `.dev/.releases/backlog/v.1.05-MemoryOpt/SPEC.md`
2. **This roadmap**: `.roadmaps/v1.05-MemoryOpt/roadmap.md`
3. **Extraction**: `.roadmaps/v1.05-MemoryOpt/extraction.md`
4. **Test strategy**: `.roadmaps/v1.05-MemoryOpt/test-strategy.md`
5. **Target files**: `~/.claude/` directory (22 markdown files, 163KB total)

## Key Constraints
- **CRITICAL**: This release modifies instruction files that control Claude Code behavior. Every change must be validated.
- **Architecture**: CLAUDE.md is the entry point using @-references. Changes cascade.
- **Quality**: ≥95% instruction-following parity with baseline required.
- **Guardrail**: Do NOT compress routing tables, decision trees, or tool selection matrices (Factory.ai research: "structure matters more than raw compression").
- **Rollback**: Git checkpoint before each milestone. Revert within 5 minutes if tests fail.

## Execution Rules
1. Work through milestones IN ORDER (M1 → M2 → M3 → M4 → M5)
2. Within milestones, respect dependency order (see roadmap.md §Dependency Graph)
3. Complete ALL deliverables before the milestone verification checkpoint
4. Run verification checkpoint before proceeding to next milestone
5. If any A/B validation test FAILS → STOP and evaluate rollback
6. If any A/B test is DEGRADED → document and proceed only if ≤1 degraded per milestone
7. Measure tokens after each milestone — record in `token-measurements.md`

## Task Execution Pattern (for each deliverable)

### 1. READ
- Read the deliverable's acceptance criteria from `roadmap.md`
- Read the target file(s) that will be modified
- Identify the specific content to change (line ranges, sections)

### 2. PLAN
- List specific changes: what content moves, what content is removed, what references are added
- For deduplication: identify canonical source and all duplicate locations
- For compression: prepare before/after comparison

### 3. IMPLEMENT
- Make changes to one file at a time
- Use Edit tool for precise modifications (not full file rewrites)
- For dedup: replace duplicate with "See [file].md §[Section]" reference
- For template abstraction: convert each persona to delta-only format
- For YAML compression: flatten to tables, remove defaults
- **Do NOT make unrelated changes** — scope strictly to the deliverable

### 4. VERIFY
- `wc -c` on modified file — confirm byte reduction
- Diff review: verify no information lost
- For dedup: verify canonical source still contains the full definition
- For on-demand: verify skill invocation loads correct context

### 5. DOCUMENT
- Record in `compression-changelog.md`:
  - File name
  - Before bytes → After bytes
  - What was changed (dedup / compress / restructure / merge)
  - Content relocated to: [destination]

### 6. CHECKPOINT
- After all milestone deliverables: run verification tests
- After tests pass: `git add` changed files + `git commit -m "v1.05 M[N]: [milestone name]"` + `git tag checkpoint-post-phase-[N]`

---

## Milestone-Specific Execution Details

### M1: Foundation & Validation Infrastructure

**Order**: IMP-007 → IMP-005 → IMP-006 → DOC-002

```
Step 1: Create feature branch
  $ git checkout -b feature/v1.05-memory-opt
  $ git tag checkpoint-pre-phase-1

Step 2: Define A/B validation suite (IMP-005)
  Create .roadmaps/v1.05-MemoryOpt/validation-baseline.md containing:
  - T-001 through T-005 task definitions with expected behaviors
  - Run each test task on current unmodified files
  - Record baseline behavior (persona activated, MCP used, output quality)

Step 3: Run token measurement (IMP-006)
  Run test-strategy.md §Token Measurement Script
  Record baseline in .roadmaps/v1.05-MemoryOpt/token-measurements.md
  Verify total matches ~163,324 bytes

Step 4: Create dependency graph (DOC-002)
  Document current @-reference topology from CLAUDE.md
  Map cross-file concept references (6 clusters from SPEC §3.2)

GATE: All infra artifacts exist. Proceed to M2.
```

### M2: High-Value Deduplication

**Order**: REQ-002 → REQ-001 → IMP-001 → IMP-004

```
Step 1: Template-abstract PERSONAS.md (REQ-002)
  - Read PERSONAS.md fully
  - Create shared template header explaining the 7-field structure
  - Convert each of 11 personas to: single-line or compact delta format
  - KEEP 2-3 personas (architect, frontend, security) in slightly expanded format as anchors
  - Verify: all persona names, MCP prefs, trigger keywords preserved
  - Measure: wc -c → target ≤13,436 bytes

Step 2: Cross-file deduplication (REQ-001)
  Process each cluster in order:

  a) Wave System:
     Canonical: COMMANDS.md §Wave System Integration
     Remove from: ORCHESTRATOR.md (lines ~171-189), MODE_Business_Panel.md (lines ~310-321)
     Replace with: "**Wave System**: See COMMANDS.md §Wave System Integration"

  b) Persona Activation:
     Canonical: PERSONAS.md (per-persona triggers)
     Remove from: ORCHESTRATOR.md (lines ~402-463)
     Replace with: "**Persona Activation**: See PERSONAS.md §Auto-Activation Triggers"

  c) MCP Server Selection:
     Canonical: MCP.md §Server Selection Algorithm
     Remove from: ORCHESTRATOR.md (lines ~540-552), MODES.md §MCP caching
     Replace with: "**MCP Selection**: See MCP.md §Server Selection Algorithm"

  d) Parallel-First:
     Canonical: RULES.md §Planning Efficiency
     Remove from: RESEARCH_CONFIG.md redundant parallel blocks, ORCHESTRATOR.md §Operation Batching
     Replace with: single-line reference

  e) Fallback/Recovery:
     Canonical: MCP.md §Circuit Breaker Configuration
     Remove from: ORCHESTRATOR.md §Graceful Degradation (keep only the 3-level list, remove redundant fallback details)

  f) Symbol/Compression:
     Canonical: MODES.md §Token Efficiency Mode
     Remove from: BUSINESS_SYMBOLS.md §Token Efficiency Integration (generic parts only, keep business-specific)

  - Measure total bytes saved across all files

Step 3: Structure-over-prose (IMP-001) — ORCHESTRATOR.md only
  - Convert §Complexity Detection YAML to table (simple/moderate/complex)
  - Convert §Domain Identification YAML to table
  - Convert §Operation Type Classification YAML to table

Step 4: Internal consolidation (IMP-004) — ORCHESTRATOR.md only
  - Merge wave info from 4 locations into single §Wave Routing
  - Remove persona activation section (now references PERSONAS.md)

GATE: Run T-001, T-004, T-005. Measure tokens. Tag checkpoint-post-phase-1.
```

### M3: On-Demand Loading & YAML Compression

**Order**: REQ-003 → IMP-008 → IMP-002 → IMP-003

```
Step 1: Update CLAUDE.md (REQ-003)
  - Remove @-references to: MODE_Business_Panel.md, BUSINESS_SYMBOLS.md,
    BUSINESS_PANEL_EXAMPLES.md, RESEARCH_CONFIG.md
  - Keep @-references to: COMMANDS.md, FLAGS.md, PRINCIPLES.md, RULES.md,
    MCP.md, PERSONAS.md, ORCHESTRATOR.md, MODES.md

Step 2: Update skill files (IMP-008)
  - Locate business-panel skill definition file
  - Add @-references to the 3 business panel files at the skill file top
  - Locate research skill definition file
  - Add @-reference to RESEARCH_CONFIG.md
  - TEST IMMEDIATELY: invoke /sc:business-panel, verify context loaded

Step 3: Compress RESEARCH_CONFIG.md (IMP-002)
  - Remove parallel_first sections (canonical in RULES.md)
  - Remove obvious defaults (timeout: 60s, max_depth: 5, etc.)
  - Convert nested YAML (depth profiles, credibility tiers) to tables
  - Remove redundant parallelization sections
  - Target: ≤4,804 bytes

Step 4: Trim BUSINESS_PANEL_EXAMPLES.md (IMP-003)
  - Keep: 1 simple example, 1 advanced example, 1 workflow integration example,
    1 expert selection strategy, 1 output format example
  - Remove: 9 redundant/similar examples
  - Remove: workflow YAML blocks duplicated from MODE_Business_Panel.md
  - Target: ≤4,952 bytes

GATE: Run T-002, T-003 (CRITICAL). Run T-006, T-007. Measure tokens. Tag checkpoint-post-phase-2.
```

### M4: Cross-File Consolidation

**Order**: IMP-004 (remaining) → IMP-001 (remaining) → REQ-001 (verify) → DOC-001

```
Step 1: Internal consolidation — remaining files (IMP-004)
  a) MCP.md: Remove §Error Handling and Recovery prose list (keep §Circuit Breaker YAML)
  b) RULES.md: Consolidate parallelism to §Planning Efficiency only; remove §Quick Reference
  c) COMMANDS.md: Remove bottom wave-enabled command list (keep top occurrence)

Step 2: Structure-over-prose — remaining files (IMP-001)
  a) RULES.md: Convert verbose decision trees to compact tables where applicable
  b) MCP.md: Convert long workflow process descriptions to concise numbered lists

Step 3: Cross-reference verification (REQ-001)
  Run: grep -r "See.*\.md" across all ~/.claude/*.md files
  Verify: every "See X.md §Y" reference points to a valid file and section
  Fix: any broken references

Step 4: Write interim compression changelog (DOC-001)
  Document all M2+M3+M4 changes per file

GATE: Run T-001—T-005 (full regression). Run T-011 (orphan scan). Measure tokens. Tag checkpoint-post-phase-3.
```

### M5: File Merging & Final Audit

**Order**: REF-001 → REF-002 → DOC-003 → DOC-001 (final)

```
Step 1: Merge satellite files (REF-001)
  a) Read each MODE_*.md file
  b) Append content as new ## section at end of MODES.md:
     ## Brainstorming Mode
     [content from MODE_Brainstorming.md]
     ## Introspection Mode
     [content from MODE_Introspection.md]
     ... etc.
  c) Read each MCP_*.md file
  d) Append content as new ## section at end of MCP.md:
     ## Context7 Quick Reference
     [content from MCP_Context7.md]
     ... etc.
  e) Delete the 9 satellite files

Step 2: Update CLAUDE.md references (REF-002)
  - Remove @-references to all 9 deleted satellite files
  - Verify remaining @-references point to existing files only
  - Verify MODE content accessible via MODES.md sections
  - Verify MCP content accessible via MCP.md sections

Step 3: Final audit (DOC-003)
  a) Run T-001—T-005: full A/B regression
  b) Run T-008, T-009: merge completeness
  c) Run T-010: CLAUDE.md reference integrity
  d) Run T-011: full orphan scan
  e) Final token measurement → record
  f) Verify: always-loaded ≤91KB (moderate target)
  g) Update dependency graph to reflect final topology

Step 4: Complete changelog (DOC-001)
  - Add M5 changes
  - Add final totals section:
    Before: 163,324 bytes, 22 files, ~41K tokens
    After: [measured] bytes, 13 files, ~[measured] tokens
    Savings: [calculated]% reduction
  - Add comparison to SPEC §7 estimates

RELEASE GATE:
- [ ] All tests pass (T-001 through T-011)
- [ ] Always-loaded ≤91KB
- [ ] File count = 13
- [ ] 0 orphaned references
- [ ] Changelog complete
- [ ] git tag v1.05.0-memory-opt
```

## Verification Checkpoints

After each milestone:
- [ ] All deliverables complete (verify IDs against roadmap.md)
- [ ] All designated tests passing
- [ ] Token measurement recorded in `token-measurements.md`
- [ ] Compression changelog updated
- [ ] Git commit + tag created

## Stop Conditions

HALT execution and report if:
- Any A/B validation test **FAILS** (not degraded — fails)
- On-demand loading produces empty context for /sc:business-panel or /sc:research
- Token measurement shows <10% savings after M2 (indicates technique not working as expected)
- Cross-reference scan finds >3 broken "See X.md" references
- Any file's byte count INCREASES after compression (indicates error)
- Security concern identified in file content during editing

## Rollback Procedure

If critical issue at any milestone:
1. Identify the failing milestone (M2/M3/M4/M5)
2. Run: `git checkout checkpoint-[pre-phase|post-phase-N] -- ~/.claude/`
3. Verify rollback: run A/B tests T-001—T-005
4. Document issue in `.roadmaps/v1.05-MemoryOpt/issues/[issue-name].md`
5. Analyze root cause before reattempting
6. Report to user with: what failed, why, proposed fix

Full rollback to original state:
```bash
git checkout checkpoint-pre-phase-1 -- ~/.claude/
```
