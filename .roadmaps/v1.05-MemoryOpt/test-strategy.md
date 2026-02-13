# Test Strategy: v1.05-MemoryOpt

## Test Environment
- **Location**: Tests are manual Claude Code session validations (no automated test directory)
- **Fixtures**: Pre-compression ~/.claude/ files preserved via git tags
- **Baseline**: `checkpoint-pre-phase-1` git tag captures unmodified state
- **Measurement Tool**: `wc -c` byte counting + token approximation (bytes ÷ 4)

## Test Approach

This release modifies static markdown instruction files, not executable code. Testing validates that Claude Code's **behavioral interpretation** of the compressed files matches the baseline. All tests are manual A/B comparisons executed in Claude Code sessions.

### A/B Testing Protocol
1. Capture baseline behavior on unmodified files (M1)
2. After each milestone, run relevant tests on compressed files
3. Compare: persona activation, MCP routing, command behavior, context completeness
4. Score: Pass (identical behavior) / Degraded (minor difference) / Fail (broken functionality)
5. Threshold: 0 Fails allowed. ≤1 Degraded allowed per milestone.

## Test Matrix

| Deliverable ID | Test ID | Test Description | Validates | Milestone Gate |
|----------------|---------|-----------------|-----------|----------------|
| REQ-001 | T-001 | `/sc:analyze @src/main.py --think --persona-security` — verify security persona activates, Sequential MCP used, analysis depth matches --think flag | Persona activation, MCP routing, flag processing | M2, M4, M5 |
| REQ-002 | T-001 | Same test — persona activation must work with template-abstracted definitions | Persona template parsing | M2 |
| REQ-003 | T-002 | `/sc:business-panel @strategy.md --mode debate` — verify full expert panel analysis with debate mode, all business symbols available | On-demand loading, business panel context | M3, M5 |
| REQ-003 | T-003 | `/sc:research "token optimization" --depth deep` — verify deep research with correct depth profile, source credibility tiers available | On-demand loading, research config | M3, M5 |
| IMP-001 | T-004 | `/sc:implement "add auth middleware" --compliance strict` — verify STRICT tier classification, persona-backend + persona-security activated | Tier classification, wave routing, persona combo | M2, M4, M5 |
| IMP-004 | T-005 | `/sc:build --feature --magic --react` — verify Magic MCP activated, frontend persona selected, wave eligibility assessed correctly | MCP selection, command routing, wave system | M2, M4, M5 |
| IMP-002 | T-006 | Verify RESEARCH_CONFIG.md retains: depth profiles (quick/standard/deep/exhaustive), source credibility tiers (T1-T4), extraction routing rules | YAML compression completeness | M3 |
| IMP-003 | T-007 | Verify BUSINESS_PANEL_EXAMPLES.md retains: ≥1 simple example, ≥1 advanced example, ≥1 workflow integration example | Example trimming completeness | M3 |
| REF-001 | T-008 | After file merging, verify MODES.md contains all 6 mode definitions (Brainstorming, Introspection, Orchestration, DeepResearch, Task Management, Token Efficiency) | File merging completeness | M5 |
| REF-001 | T-009 | After file merging, verify MCP.md contains all 3 server quick-reference sections (Context7, Sequential, Serena) | File merging completeness | M5 |
| REF-002 | T-010 | CLAUDE.md @-references resolve to existing files only. No orphaned references. | Reference integrity | M5 |
| DOC-003 | T-011 | Full orphan scan: grep for "See.*\.md" across all files, verify every target exists | Cross-reference integrity | M5 |

## Test Execution Order

### Per-Milestone Execution

**M1 (Foundation)**:
1. Verify feature branch exists
2. Run baseline T-001 through T-005 — capture expected behavior
3. Verify token measurement matches SPEC baseline (163,324 bytes ±5%)

**M2 (High-Value Dedup)**:
1. T-001: Persona activation with template-abstracted PERSONAS.md
2. T-004: Tier classification with deduped ORCHESTRATOR.md
3. T-005: MCP routing with deduped commands/MCP references
4. Token measurement: verify ≥18KB saved

**M3 (On-Demand + YAML)**:
1. T-002: Business panel with on-demand loading — **CRITICAL**
2. T-003: Research with on-demand config — **CRITICAL**
3. T-006: YAML content completeness check
4. T-007: Example content completeness check
5. Token measurement: verify always-loaded ≤96KB

**M4 (Cross-File Consolidation)**:
1. T-001 through T-005: Full regression suite
2. T-011: Cross-reference integrity scan
3. Token measurement: verify always-loaded ≤84KB

**M5 (File Merging & Final)**:
1. T-008, T-009: File merging completeness
2. T-010: CLAUDE.md reference integrity
3. T-011: Full orphan scan
4. T-001 through T-005: Complete A/B regression
5. Final token measurement: verify ≤91KB always-loaded (moderate target)

## Coverage Targets

| Category | Target | Measurement |
|----------|--------|-------------|
| Persona activation | 100% of 11 personas testable | At minimum, 3 personas tested directly (security, frontend, backend) |
| MCP routing | 100% of 4 servers | Sequential, Context7, Magic, Playwright routing verified |
| On-demand loading | 100% of specialist clusters | Business panel (3 files) and research (1 file) verified |
| Cross-references | 100% of "See X.md §Y" references | Grep scan confirms all targets exist |
| Token budget | ±15% of SPEC estimates per phase | `wc -c` measurement script |
| File integrity | 0 orphaned files, 0 missing references | Post-merge audit |

## Token Measurement Script

```bash
#!/bin/bash
# Run after each milestone to measure progress
echo "=== Token Measurement: $(date -Iseconds) ==="
echo ""

# Always-loaded files (post FR-004, this list shrinks)
CORE_FILES=(
  COMMANDS.md FLAGS.md PRINCIPLES.md RULES.md
  MCP.md PERSONAS.md ORCHESTRATOR.md MODES.md
)

total=0
echo "| File | Bytes | ~Tokens |"
echo "|------|-------|---------|"
for f in "${CORE_FILES[@]}"; do
  if [ -f "$HOME/.claude/$f" ]; then
    bytes=$(wc -c < "$HOME/.claude/$f")
    tokens=$((bytes / 4))
    printf "| %-25s | %6d | %6d |\n" "$f" "$bytes" "$tokens"
    total=$((total + bytes))
  fi
done
echo ""
echo "Always-loaded total: $total bytes (~$((total/4)) tokens)"
echo ""

# On-demand files
echo "On-demand files (loaded by skills):"
ON_DEMAND=(
  MODE_Business_Panel.md BUSINESS_SYMBOLS.md
  BUSINESS_PANEL_EXAMPLES.md RESEARCH_CONFIG.md
)
od_total=0
for f in "${ON_DEMAND[@]}"; do
  if [ -f "$HOME/.claude/$f" ]; then
    bytes=$(wc -c < "$HOME/.claude/$f")
    printf "  %-35s %6d bytes\n" "$f" "$bytes"
    od_total=$((od_total + bytes))
  fi
done
echo "On-demand total: $od_total bytes (~$((od_total/4)) tokens)"
echo ""
echo "Grand total: $((total + od_total)) bytes (~$(((total + od_total)/4)) tokens)"
```

## Rollback Procedures

| Milestone | Rollback Command | Recovery Time |
|-----------|-----------------|---------------|
| M2 | `git checkout checkpoint-pre-phase-1 -- ~/.claude/PERSONAS.md ~/.claude/ORCHESTRATOR.md ~/.claude/COMMANDS.md` | <2 min |
| M3 | `git checkout checkpoint-post-phase-1 -- ~/.claude/CLAUDE.md ~/.claude/RESEARCH_CONFIG.md ~/.claude/BUSINESS_PANEL_EXAMPLES.md` | <2 min |
| M4 | `git checkout checkpoint-post-phase-2 -- ~/.claude/MCP.md ~/.claude/RULES.md ~/.claude/COMMANDS.md` | <2 min |
| M5 | `git checkout checkpoint-post-phase-3 -- ~/.claude/MODES.md ~/.claude/MCP.md ~/.claude/CLAUDE.md` + restore satellite files | <5 min |
| Full | `git checkout checkpoint-pre-phase-1 -- ~/.claude/` | <1 min |

## Quality Gate Summary

| Gate | Criteria | Blocking? |
|------|----------|-----------|
| M1 → M2 | Baseline captured, all infra ready | Yes |
| M2 → M3 | T-001, T-004, T-005 pass; ≥18KB saved | Yes |
| M3 → M4 | T-002, T-003 pass (CRITICAL); ≤96KB always-loaded | Yes |
| M4 → M5 | T-001—T-005 pass; cross-refs valid | Yes |
| M5 → Release | All tests pass; ≤91KB; 0 orphans; changelog complete | Yes |
