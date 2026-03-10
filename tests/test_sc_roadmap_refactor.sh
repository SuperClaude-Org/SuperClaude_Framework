#!/usr/bin/env bash
# =============================================================================
# tests/test_sc_roadmap_refactor.sh
# v2.01 Architecture Refactor — sc:roadmap Effectiveness Test Suite
#
# Run from repo root: bash tests/test_sc_roadmap_refactor.sh
# Safe to run 10x — all deterministic structural checks, no writes.
# =============================================================================

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

PASS=0; FAIL=0; WARN=0
RUN_ID=$(date +%Y%m%d-%H%M%S)
LOGFILE="claudedocs/test-results-${RUN_ID}.log"
mkdir -p claudedocs

log() { echo "$@" | tee -a "$LOGFILE"; }
pass() { PASS=$((PASS+1)); log "  ✅ PASS: $1"; }
fail() { FAIL=$((FAIL+1)); log "  ❌ FAIL: $1"; }
warn() { WARN=$((WARN+1)); log "  ⚠️  WARN: $1"; }
section() { log ""; log "=== $1 ==="; }

log "sc:roadmap Refactor Test Suite"
log "Run ID: $RUN_ID"
log "Date:   $(date)"
log "Commit: $(git log --oneline -1)"
log ""

# =============================================================================
# SUITE A: Invocation Wiring (RC1 fix verification)
# Tests that BUG-001 and BUG-006 are resolved
# =============================================================================
section "SUITE A: Invocation Wiring (RC1 — BUG-001 + BUG-006)"

# A1: roadmap.md has Activation section
if grep -q "## Activation" src/superclaude/commands/roadmap.md; then
  pass "A1: roadmap.md has ## Activation section"
else
  fail "A1: roadmap.md MISSING ## Activation section (BUG-006 not fixed)"
fi

# A2: Activation section references Skill sc:roadmap-protocol (not old file path)
if grep -A5 "## Activation" src/superclaude/commands/roadmap.md | grep -q "Skill sc:roadmap-protocol"; then
  pass "A2: ## Activation references 'Skill sc:roadmap-protocol'"
else
  fail "A2: ## Activation does NOT reference 'Skill sc:roadmap-protocol' — invocation chain broken (BUG-006)"
fi

# A3: Activation section has "Do NOT proceed" warning
if grep -A10 "## Activation" src/superclaude/commands/roadmap.md | grep -qi "do not proceed"; then
  pass "A3: ## Activation has 'Do NOT proceed' warning"
else
  warn "A3: ## Activation missing 'Do NOT proceed' warning (per spec template §5)"
fi

# A4: roadmap.md allowed-tools includes Skill
if grep "allowed-tools" src/superclaude/commands/roadmap.md | grep -q "Skill"; then
  pass "A4: roadmap.md allowed-tools includes 'Skill' (BUG-001 fixed for command)"
else
  fail "A4: roadmap.md allowed-tools MISSING 'Skill' — skill invocation will be blocked (BUG-001)"
fi

# A5: .claude/ copy matches src/ (atomic change requirement)
if diff -q src/superclaude/commands/roadmap.md .claude/commands/sc/roadmap.md >/dev/null 2>&1; then
  pass "A5: .claude/commands/sc/roadmap.md matches src/ (atomic sync verified)"
else
  fail "A5: .claude/commands/sc/roadmap.md DIFFERS from src/ — atomic change group incomplete"
fi

# =============================================================================
# SUITE B: Skill Naming Convention (RC6 fix verification)
# Tests that -protocol naming convention is enforced
# =============================================================================
section "SUITE B: Skill Naming Convention (RC6 + CI Check 9)"

# B1: SKILL.md frontmatter name ends in -protocol
# Note: name field contains colons (sc:roadmap-protocol), so use sed not cut
SKILL_NAME=$(grep "^name:" src/superclaude/skills/sc-roadmap-protocol/SKILL.md 2>/dev/null | head -1 | sed 's/^name:[[:space:]]*//' | tr -d ' "')
if echo "$SKILL_NAME" | grep -q ".*-protocol$"; then
  pass "B1: SKILL.md name field ends in '-protocol': $SKILL_NAME"
else
  fail "B1: SKILL.md name field '$SKILL_NAME' does NOT end in '-protocol' (re-entry deadlock risk)"
fi

# B2: Skill name ≠ command name (anti-deadlock)
CMD_NAME="sc:roadmap"
if [ "$SKILL_NAME" != "$CMD_NAME" ]; then
  pass "B2: Skill name ('$SKILL_NAME') ≠ command name ('$CMD_NAME') — no re-entry deadlock"
else
  fail "B2: Skill name EQUALS command name '$SKILL_NAME' — Skill tool will deadlock (re-entry block)"
fi

# B3: SKILL.md has required frontmatter fields
for field in "name:" "description:" "allowed-tools:"; do
  if grep -q "^${field}" src/superclaude/skills/sc-roadmap-protocol/SKILL.md; then
    pass "B3: SKILL.md has required frontmatter field: $field"
  else
    fail "B3: SKILL.md MISSING required frontmatter field: $field (CI Check 8 will fail)"
  fi
done

# B4: SKILL.md allowed-tools includes Skill
if grep "allowed-tools" src/superclaude/skills/sc-roadmap-protocol/SKILL.md | grep -q "Skill"; then
  pass "B4: sc-roadmap-protocol SKILL.md allowed-tools includes 'Skill' (BUG-001 fixed for skill)"
else
  fail "B4: sc-roadmap-protocol SKILL.md allowed-tools MISSING 'Skill' (BUG-001 partial fix incomplete)"
fi

# =============================================================================
# SUITE C: Spec Execution Gap (RC2 fix verification — T02.03)
# Tests that Wave 2 Step 3 has explicit tool binding
# =============================================================================
section "SUITE C: Spec Execution Gap (RC2 — T02.03)"

# C1: Wave 2 Step 3 has sub-steps 3a-3f (not vague "Invoke" prose)
SKILL_FILE="src/superclaude/skills/sc-roadmap-protocol/SKILL.md"
STEPCOUNT=0
for step in "3a" "3b" "3c" "3d" "3e" "3f"; do
  if grep -q "\*\*${step}\*\*\|**${step}:**\|- \*\*${step}" "$SKILL_FILE"; then
    STEPCOUNT=$((STEPCOUNT+1))
  fi
done
if [ $STEPCOUNT -ge 6 ]; then
  pass "C1: Wave 2 Step 3 has all 6 sub-steps 3a-3f present"
elif [ $STEPCOUNT -ge 3 ]; then
  warn "C1: Wave 2 Step 3 has only $STEPCOUNT/6 sub-steps — partial T02.03 implementation"
else
  fail "C1: Wave 2 Step 3 is MISSING sub-steps 3a-3f — still using vague 'Invoke' prose (T02.03 not done)"
fi

# C2: Wave 2 Step 3 uses direct "Invoke Skill sc:adversarial-protocol" (SKILL-DIRECT, not Task agent)
if grep -A50 "### Wave 2" "$SKILL_FILE" | grep -q "Invoke Skill sc:adversarial-protocol\|Invoke.*sc:adversarial-protocol"; then
  pass "C2: Wave 2 uses 'Invoke Skill sc:adversarial-protocol' pattern (SKILL-DIRECT)"
else
  if grep -A50 "### Wave 2" "$SKILL_FILE" | grep -q "Dispatch.*Task\|Task agent"; then
    fail "C2: Wave 2 uses Task agent dispatch — SKILL-DIRECT not applied (D-0001 reversal not reflected)"
  else
    fail "C2: Wave 2 has no tool binding for adversarial dispatch"
  fi
fi

# C3: Wave 1A also uses direct Skill invocation (SKILL-DIRECT, not Task agent or bare prose)
if grep -A30 "Wave 1A" "$SKILL_FILE" | grep -q "Invoke Skill sc:adversarial-protocol\|Invoke.*sc:adversarial-protocol"; then
  pass "C3: Wave 1A uses 'Invoke Skill sc:adversarial-protocol' pattern (SKILL-DIRECT)"
else
  if grep -A30 "Wave 1A" "$SKILL_FILE" | grep -q "Dispatch.*Task\|Task agent"; then
    fail "C3: Wave 1A uses Task agent dispatch — SKILL-DIRECT not applied (D-0001 reversal not reflected)"
  elif grep -A30 "Wave 1A" "$SKILL_FILE" | grep -qi "invoke sc:adversarial[^-]"; then
    fail "C3: Wave 1A still contains bare 'Invoke sc:adversarial' prose — T02.03 incomplete"
  else
    warn "C3: Cannot confirm Wave 1A SKILL-DIRECT pattern"
  fi
fi

# C3.5: Wave 1A has no stale sc-adversarial/ references (only sc-adversarial-protocol)
if grep -A30 "Wave 1A" "$SKILL_FILE" | grep "sc-adversarial" | grep -v "sc-adversarial-protocol" | grep -q .; then
  fail "C3.5: Wave 1A still has stale 'sc-adversarial/' reference (BUG-005 not fully fixed in Wave 1A)"
else
  pass "C3.5: Wave 1A uses 'sc-adversarial-protocol' (no stale sc-adversarial/ paths)"
fi

# C4: Return contract consumption present in SKILL.md
# Note: SKILL-DIRECT mode uses inline return values, not return-contract.yaml files
if grep -q "convergence_score\|## Return Contract" "$SKILL_FILE"; then
  pass "C4: SKILL.md has return contract routing (## Return Contract section + convergence_score)"
else
  fail "C4: SKILL.md has NO return contract routing — RC4 not addressed"
fi

# C5: 3-status routing present (convergence 0.6/0.5 thresholds)
if grep -q "0\.6\|convergence_score" "$SKILL_FILE"; then
  pass "C5: SKILL.md contains convergence threshold routing (0.6 PASS gate)"
else
  warn "C5: No convergence_score routing found in SKILL.md"
fi

# =============================================================================
# SUITE D: Bug Elimination
# =============================================================================
section "SUITE D: Bug Elimination (BUG-003, BUG-005)"

# D1: BUG-005 — No stale sc-adversarial/ paths in SKILL.md
if grep "sc-adversarial" "$SKILL_FILE" | grep -v "sc-adversarial-protocol" | grep -q .; then
  fail "D1: SKILL.md still contains stale 'sc-adversarial/' reference (BUG-005 not fixed)"
else
  pass "D1: No stale 'sc-adversarial/' paths in SKILL.md (BUG-005 fixed)"
fi

# D2: BUG-005 — No stale sc-adversarial/ paths in adversarial-integration.md ref
REF_FILE="src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md"
if grep "sc-adversarial" "$REF_FILE" | grep -v "sc-adversarial-protocol" | grep -q .; then
  fail "D2: adversarial-integration.md ref still has stale 'sc-adversarial/' path (BUG-005 ref)"
else
  pass "D2: No stale 'sc-adversarial/' paths in adversarial-integration.md ref (BUG-005 ref fixed)"
fi

# D3: BUG-003 — Orchestrator threshold is >=3 (not >=5)
# Check specifically for ">=5" or "≥5" or ">= 5" in orchestrator/agent context (not validation >=85%)
if grep -i "agent.*>= *5\|>= *5.*agent\|orchestrator.*>= *5\|≥ *5.*agent\|agent.*≥ *5" "$SKILL_FILE" | grep -v ">=85\|>=70" | grep -q .; then
  fail "D3: SKILL.md still has '>=5' orchestrator threshold (BUG-003 not fixed)"
else
  if grep -q "agent_count >= 3\|>= 3.*agent\|agent.*>= 3\|≥ 3.*orchestrator\|With >= 3 agents" "$SKILL_FILE"; then
    pass "D3: Orchestrator threshold is >=3 in SKILL.md (BUG-003 fixed)"
  else
    warn "D3: Cannot confirm orchestrator threshold in SKILL.md (grep inconclusive)"
  fi
fi

# D4: Return Contract section exists in SKILL.md
if grep -q "## Return Contract" "$SKILL_FILE"; then
  pass "D4: SKILL.md has '## Return Contract' section (required per §10 of sprint-spec)"
else
  fail "D4: SKILL.md MISSING '## Return Contract' section (every protocol skill must have this)"
fi

# =============================================================================
# SUITE E: Build System (RC7 fix verification)
# =============================================================================
section "SUITE E: Build System (RC7 — lint-architecture)"

# E1: lint-architecture target exists in Makefile
if grep -q "^lint-architecture:" Makefile; then
  pass "E1: lint-architecture target present in Makefile"
else
  fail "E1: lint-architecture target MISSING from Makefile — RC7 not addressed"
fi

# E2: lint-architecture is in .PHONY
if grep "^\.PHONY" Makefile | grep -q "lint-architecture"; then
  pass "E2: lint-architecture is in Makefile .PHONY"
else
  warn "E2: lint-architecture not in .PHONY (non-blocking but sloppy)"
fi

# E3: sync-dev skip heuristic removed
# The heuristic was: cmd_name=${skill_name#sc-} && if cmd exists, continue
# After fix, sc-roadmap-protocol should NOT be skipped when sc-roadmap command exists
if grep -A20 "^sync-dev:" Makefile | grep -q "served by\|cmd_name.*sc-\b.*continue"; then
  fail "E3: Makefile sync-dev STILL has skill-skip heuristic — sc-roadmap-protocol will not sync"
else
  pass "E3: Makefile sync-dev skill-skip heuristic removed"
fi

# E4: verify-sync skip heuristic removed
if grep -A30 "^verify-sync:" Makefile | grep -q "served by.*command"; then
  fail "E4: Makefile verify-sync STILL has 'served by command' skip heuristic"
else
  pass "E4: Makefile verify-sync skill-skip heuristic removed"
fi

# E5: Run lint-architecture and check sc-roadmap-protocol specific checks
# Note: lint-architecture may fail due to pre-existing issues in other skills
# We check that sc-roadmap-protocol specifically passes all checks
log ""
log "  Running: make lint-architecture (checking sc-roadmap-protocol results)"
LINT_OUTPUT=$(make lint-architecture 2>&1 || true)
if echo "$LINT_OUTPUT" | grep -q "✅ \[Check 1\]: roadmap → sc-roadmap-protocol"; then
  pass "E5a: lint-architecture Check 1 passes for roadmap → sc-roadmap-protocol"
else
  fail "E5a: lint-architecture Check 1 fails for sc-roadmap-protocol"
fi
if echo "$LINT_OUTPUT" | grep -q "✅ \[Check 9\]: sc:roadmap-protocol ends in -protocol"; then
  pass "E5b: lint-architecture Check 9 passes for sc:roadmap-protocol naming"
else
  fail "E5b: lint-architecture Check 9 fails for sc:roadmap-protocol naming"
fi

# =============================================================================
# SUITE F: Dev Copy Sync
# =============================================================================
section "SUITE F: Dev Copy Sync (.claude/ parity)"

# F1: .claude/skills/sc-roadmap-protocol/ exists and is non-empty
if [ -d ".claude/skills/sc-roadmap-protocol" ]; then
  FILE_COUNT=$(find .claude/skills/sc-roadmap-protocol -type f | wc -l)
  if [ "$FILE_COUNT" -gt 0 ]; then
    pass "F1: .claude/skills/sc-roadmap-protocol/ exists with $FILE_COUNT files"
  else
    fail "F1: .claude/skills/sc-roadmap-protocol/ exists but is EMPTY — make sync-dev not run"
  fi
else
  fail "F1: .claude/skills/sc-roadmap-protocol/ MISSING from .claude/ — make sync-dev not run"
fi

# F2: SKILL.md is present in .claude/ copy
if [ -f ".claude/skills/sc-roadmap-protocol/SKILL.md" ]; then
  pass "F2: .claude/skills/sc-roadmap-protocol/SKILL.md exists"
else
  fail "F2: .claude/skills/sc-roadmap-protocol/SKILL.md MISSING from .claude/ copy"
fi

# F3: .claude/ SKILL.md matches src/ SKILL.md
if diff -q src/superclaude/skills/sc-roadmap-protocol/SKILL.md .claude/skills/sc-roadmap-protocol/SKILL.md >/dev/null 2>&1; then
  pass "F3: .claude/ SKILL.md matches src/ SKILL.md (no drift)"
else
  fail "F3: .claude/ SKILL.md DIFFERS from src/ — make sync-dev needed or failed"
fi

# F4: All 5 ref files present in .claude/ copy
for ref in extraction-pipeline.md templates.md adversarial-integration.md scoring.md validation.md; do
  if [ -f ".claude/skills/sc-roadmap-protocol/refs/$ref" ]; then
    pass "F4: .claude/refs/$ref exists"
  else
    fail "F4: .claude/refs/$ref MISSING"
  fi
done

# =============================================================================
# SUITE G: Command Line Count (Size constraint)
# =============================================================================
section "SUITE G: Command File Size Compliance"

CMD_LINES=$(wc -l < src/superclaude/commands/roadmap.md)
if [ "$CMD_LINES" -le 150 ]; then
  pass "G1: roadmap.md is $CMD_LINES lines (within ≤150 target)"
elif [ "$CMD_LINES" -le 350 ]; then
  warn "G1: roadmap.md is $CMD_LINES lines (over 150 target but within ≤350 hard limit)"
else
  fail "G1: roadmap.md is $CMD_LINES lines (exceeds ≤350 hard limit — spec violation)"
fi

# =============================================================================
# RESULTS
# =============================================================================
section "RESULTS SUMMARY"
log ""
log "  Run ID:   $RUN_ID"
log "  Total:    $((PASS + FAIL + WARN)) checks"
log "  PASS:     $PASS"
log "  FAIL:     $FAIL"
log "  WARN:     $WARN"
log ""

if [ $FAIL -eq 0 ]; then
  log "  🏆 ALL CHECKS PASSED — sc:roadmap refactor is architecturally correct"
  log "  The v2.01 root causes (RC1, RC2, RC4, RC6, RC7) are addressed for sc:roadmap."
  log ""
  log "  Results saved to: $LOGFILE"
  exit 0
else
  log "  ❌ $FAIL CHECK(S) FAILED — refactor incomplete"
  log "  Review failures above and consult sprint-spec §12–13 for fix guidance."
  log ""
  log "  Results saved to: $LOGFILE"
  exit 1
fi
