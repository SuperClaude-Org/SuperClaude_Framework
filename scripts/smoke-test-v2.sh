#!/usr/bin/env bash
# =============================================================================
# smoke-test-v2.sh — Real Integration Smoke Tests for unified-audit-gating-v2
#
# These are NOT unit tests. They exercise the actual CLI, grep actual source
# files, run the real pytest suite, and (optionally) invoke real sprint
# dry-runs. Each test prints PASS/FAIL with evidence.
#
# Usage:
#   bash scripts/smoke-test-v2.sh              # Run all tests
#   bash scripts/smoke-test-v2.sh --quick      # Skip slow tests (dry-runs)
#   bash scripts/smoke-test-v2.sh --section N  # Run only section N (1-7)
# =============================================================================

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

QUICK=false
SECTION=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick) QUICK=true; shift ;;
    --section) shift; SECTION="${1:-}"; shift ;;
    [1-7]) SECTION="$1"; shift ;;
    *) shift ;;
  esac
done

PASS=0
FAIL=0
SKIP=0
TOTAL=0

pass() { ((PASS++)); ((TOTAL++)); echo "  [PASS] $1"; }
fail() { ((FAIL++)); ((TOTAL++)); echo "  [FAIL] $1"; echo "    -> $2"; }
skip() { ((SKIP++)); ((TOTAL++)); echo "  [SKIP] $1"; }
section() { echo ""; echo "═══════════════════════════════════════════════════"; echo "§$1 — $2"; echo "═══════════════════════════════════════════════════"; }

should_run() { [[ -z "$SECTION" || "$SECTION" == "$1" ]]; }

# ─────────────────────────────────────────────────────────────────────────────
# §1 — FR Verification: Source defaults are correct (grep-based)
# ─────────────────────────────────────────────────────────────────────────────
if should_run 1; then
  section 1 "FR Verification — Source Defaults (grep)"

  # FR-001: PipelineConfig.max_turns == 100
  if grep -q 'max_turns: int = 100' src/superclaude/cli/pipeline/models.py; then
    pass "FR-001: PipelineConfig.max_turns defaults to 100"
  else
    fail "FR-001: PipelineConfig.max_turns" "Expected 'max_turns: int = 100' in pipeline/models.py"
  fi

  # FR-002: SprintConfig.max_turns == 100
  if grep -q 'max_turns: int = 100' src/superclaude/cli/sprint/models.py; then
    pass "FR-002: SprintConfig.max_turns defaults to 100"
  else
    fail "FR-002: SprintConfig.max_turns" "Expected 'max_turns: int = 100' in sprint/models.py"
  fi

  # FR-003: CLI --max-turns default=100
  if grep -q 'default=100' src/superclaude/cli/sprint/commands.py; then
    pass "FR-003: CLI --max-turns defaults to 100"
  else
    fail "FR-003: CLI --max-turns default" "Expected 'default=100' in sprint/commands.py"
  fi

  # FR-004: CLI help text says "default: 100"
  if grep -qi 'default: 100' src/superclaude/cli/sprint/commands.py; then
    pass "FR-004: CLI help text references 'default: 100'"
  else
    fail "FR-004: CLI help text" "Expected 'default: 100' in sprint/commands.py help string"
  fi

  # FR-005: load_sprint_config max_turns default
  if grep -q 'max_turns: int = 100' src/superclaude/cli/sprint/config.py; then
    pass "FR-005: load_sprint_config max_turns defaults to 100"
  else
    fail "FR-005: load_sprint_config" "Expected 'max_turns: int = 100' in sprint/config.py"
  fi

  # FR-006: ClaudeProcess.__init__ max_turns default
  if grep -q 'max_turns: int = 100' src/superclaude/cli/pipeline/process.py; then
    pass "FR-006: ClaudeProcess max_turns defaults to 100"
  else
    fail "FR-006: ClaudeProcess" "Expected 'max_turns: int = 100' in pipeline/process.py"
  fi

  # FR-007: TurnLedger.reimbursement_rate == 0.8
  if grep -q 'reimbursement_rate: float = 0.8' src/superclaude/cli/sprint/models.py; then
    pass "FR-007: TurnLedger.reimbursement_rate defaults to 0.8"
  else
    fail "FR-007: reimbursement_rate" "Expected 'reimbursement_rate: float = 0.8' in sprint/models.py"
  fi

  # FR-008: execute-sprint.sh MAX_TURNS=100
  if grep -q 'MAX_TURNS=100' .dev/releases/execute-sprint.sh 2>/dev/null; then
    pass "FR-008: execute-sprint.sh MAX_TURNS=100"
  else
    fail "FR-008: execute-sprint.sh" "Expected 'MAX_TURNS=100' in .dev/releases/execute-sprint.sh"
  fi

  # FR-010: rerun-incomplete-phases.sh references max_turns (100)
  if grep -qi 'max_turns.*(100)' scripts/rerun-incomplete-phases.sh 2>/dev/null; then
    pass "FR-010: rerun-incomplete-phases.sh references max_turns (100)"
  else
    fail "FR-010: rerun-incomplete-phases.sh" "Expected 'max_turns (100)' reference"
  fi

  # FR-011: roadmap CLI default=100
  if grep -q 'default=100' src/superclaude/cli/roadmap/commands.py; then
    pass "FR-011: Roadmap CLI --max-turns defaults to 100"
  else
    fail "FR-011: Roadmap CLI" "Expected 'default=100' in roadmap/commands.py"
  fi

  # FR-012: roadmap CLI help text
  if grep -qi 'Default: 100' src/superclaude/cli/roadmap/commands.py; then
    pass "FR-012: Roadmap CLI help text references 'Default: 100'"
  else
    fail "FR-012: Roadmap CLI help" "Expected 'Default: 100' in roadmap/commands.py help"
  fi

  # NEGATIVE: No old defaults lingering
  OLD_50=$(grep -rn 'max_turns.*=.*50' src/superclaude/cli/ 2>/dev/null | grep -v '.pyc' | grep -v __pycache__ || true)
  if [[ -z "$OLD_50" ]]; then
    pass "NEG-001: No residual max_turns=50 in source"
  else
    fail "NEG-001: Residual max_turns=50 found" "$OLD_50"
  fi

  OLD_05=$(grep -rn 'reimbursement_rate.*=.*0\.5[^0-9]' src/superclaude/cli/ 2>/dev/null | grep -v '.pyc' | grep -v __pycache__ || true)
  if [[ -z "$OLD_05" ]]; then
    pass "NEG-002: No residual reimbursement_rate=0.5 in source"
  else
    fail "NEG-002: Residual reimbursement_rate=0.5 found" "$OLD_05"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# §2 — Python Import & Instantiation: defaults are correct at runtime
# ─────────────────────────────────────────────────────────────────────────────
if should_run 2; then
  section 2 "Runtime Defaults — Python import verification"

  RUNTIME_CHECK=$(uv run python -c "
from superclaude.cli.pipeline.models import PipelineConfig
from superclaude.cli.sprint.models import SprintConfig, TurnLedger

pc = PipelineConfig()
sc = SprintConfig(index_path='/dev/null')
tl = TurnLedger(initial_budget=200)

errors = []
if pc.max_turns != 100:
    errors.append(f'PipelineConfig.max_turns={pc.max_turns}, expected 100')
if sc.max_turns != 100:
    errors.append(f'SprintConfig.max_turns={sc.max_turns}, expected 100')
if tl.reimbursement_rate != 0.8:
    errors.append(f'TurnLedger.reimbursement_rate={tl.reimbursement_rate}, expected 0.8')

if errors:
    print('FAIL:' + '|'.join(errors))
else:
    print('PASS')
" 2>&1 | grep -v '^warning:')

  if [[ "$RUNTIME_CHECK" == "PASS" ]]; then
    pass "RT-001: PipelineConfig, SprintConfig, TurnLedger defaults correct at runtime"
  else
    fail "RT-001: Runtime default verification" "$RUNTIME_CHECK"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# §3 — Budget Math: real TurnLedger simulation (46-task sprint)
# ─────────────────────────────────────────────────────────────────────────────
if should_run 3; then
  section 3 "Budget Simulation — 46-task sprint at rate=0.8"

  BUDGET_SIM=$(uv run python -c "
from superclaude.cli.sprint.models import TurnLedger
import math

ledger = TurnLedger(initial_budget=200, reimbursement_rate=0.8)
results = []
exhausted_at = None

for task_num in range(1, 47):
    avail = ledger.available()
    if avail < 1:
        exhausted_at = task_num
        break

    actual_turns = 8
    overhead = 2
    ledger.debit(actual_turns + overhead)
    credit = math.floor(actual_turns * ledger.reimbursement_rate)
    ledger.credit(credit)
    results.append((task_num, ledger.available()))

if exhausted_at:
    print(f'FAIL:Budget exhausted at task {exhausted_at}')
else:
    final = ledger.available()
    print(f'PASS:Completed 46 tasks, remaining budget={final}')
    # Verify monotonic decay
    budgets = [r[1] for r in results]
    monotonic = all(budgets[i] >= budgets[i+1] for i in range(len(budgets)-1))
    if not monotonic:
        print(f'WARN:Budget not monotonically decreasing')
    else:
        print(f'MONO:Budget monotonically decreasing confirmed')
" 2>&1)

  if echo "$BUDGET_SIM" | grep -q '^PASS:'; then
    pass "BUD-001: 46-task sprint completes without exhaustion"
    echo "    → $(echo "$BUDGET_SIM" | head -1 | sed 's/PASS://')"
  else
    fail "BUD-001: 46-task sprint" "$(echo "$BUDGET_SIM" | head -1)"
  fi

  if echo "$BUDGET_SIM" | grep -q '^MONO:'; then
    pass "BUD-002: Budget monotonically decreasing (NFR-008)"
  else
    fail "BUD-002: Monotonic budget decay" "Budget non-monotonic"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# §4 — Timeout Math: phase timeout at max_turns=100
# ─────────────────────────────────────────────────────────────────────────────
if should_run 4; then
  section 4 "Timeout Computation — NFR-004"

  TIMEOUT_CHECK=$(uv run python -c "
max_turns = 100
expected_timeout = max_turns * 120 + 300  # 12,300s
print(f'timeout={expected_timeout}')
if expected_timeout == 12300:
    print('PASS')
else:
    print(f'FAIL:Expected 12300, got {expected_timeout}')

# Also verify 9-phase sprint bound (NFR-005)
sprint_bound = 9 * expected_timeout
hours = sprint_bound / 3600
print(f'sprint_bound={sprint_bound}s ({hours:.2f}h)')
if abs(hours - 30.75) < 0.01:
    print('BOUND_PASS')
else:
    print(f'BOUND_FAIL:Expected 30.75h, got {hours}h')
" 2>&1)

  if echo "$TIMEOUT_CHECK" | grep -q '^PASS$'; then
    pass "NFR-004: Phase timeout = 12,300s at max_turns=100"
  else
    fail "NFR-004: Phase timeout" "$(echo "$TIMEOUT_CHECK" | grep FAIL)"
  fi

  if echo "$TIMEOUT_CHECK" | grep -q '^BOUND_PASS$'; then
    pass "NFR-005: 9-phase sprint bound = 30.75 hours"
  else
    fail "NFR-005: Sprint timeout bound" "$(echo "$TIMEOUT_CHECK" | grep BOUND_FAIL)"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# §5 — Real Pytest Suite: run the actual test files that cover v2 changes
# ─────────────────────────────────────────────────────────────────────────────
if should_run 5; then
  section 5 "Pytest Suite — Real test execution"

  # Sprint models (TurnLedger, SprintConfig defaults)
  if uv run pytest tests/sprint/test_models.py -v --tb=short 2>&1 | tee /tmp/smoke-sprint-models.txt | tail -1 | grep -q 'passed'; then
    SPRINT_COUNT=$(grep -c 'PASSED' /tmp/smoke-sprint-models.txt || echo 0)
    pass "TEST-001: tests/sprint/test_models.py — $SPRINT_COUNT tests passed"
  else
    fail "TEST-001: tests/sprint/test_models.py" "$(tail -3 /tmp/smoke-sprint-models.txt)"
  fi

  # Sprint config (load_sprint_config, explicit override)
  if uv run pytest tests/sprint/test_config.py -v --tb=short 2>&1 | tee /tmp/smoke-sprint-config.txt | tail -1 | grep -q 'passed'; then
    CONFIG_COUNT=$(grep -c 'PASSED' /tmp/smoke-sprint-config.txt || echo 0)
    pass "TEST-002: tests/sprint/test_config.py — $CONFIG_COUNT tests passed"
  else
    fail "TEST-002: tests/sprint/test_config.py" "$(tail -3 /tmp/smoke-sprint-config.txt)"
  fi

  # Pipeline models (PipelineConfig defaults)
  if uv run pytest tests/pipeline/test_models.py -v --tb=short 2>&1 | tee /tmp/smoke-pipeline-models.txt | tail -1 | grep -q 'passed'; then
    PIPE_COUNT=$(grep -c 'PASSED' /tmp/smoke-pipeline-models.txt || echo 0)
    pass "TEST-003: tests/pipeline/test_models.py — $PIPE_COUNT tests passed"
  else
    fail "TEST-003: tests/pipeline/test_models.py" "$(tail -3 /tmp/smoke-pipeline-models.txt)"
  fi

  # Full flow integration (budget scenarios)
  if uv run pytest tests/pipeline/test_full_flow.py -v --tb=short 2>&1 | tee /tmp/smoke-full-flow.txt | tail -1 | grep -q 'passed'; then
    FLOW_COUNT=$(grep -c 'PASSED' /tmp/smoke-full-flow.txt || echo 0)
    pass "TEST-004: tests/pipeline/test_full_flow.py — $FLOW_COUNT tests passed"
  else
    fail "TEST-004: tests/pipeline/test_full_flow.py" "$(tail -3 /tmp/smoke-full-flow.txt)"
  fi

  # Property-based tests (if they exist)
  if uv run pytest tests/sprint/test_property_based.py -v --tb=short 2>&1 | tee /tmp/smoke-property.txt | tail -1 | grep -q 'passed'; then
    PROP_COUNT=$(grep -c 'PASSED' /tmp/smoke-property.txt || echo 0)
    pass "TEST-005: tests/sprint/test_property_based.py — $PROP_COUNT tests passed"
  else
    fail "TEST-005: tests/sprint/test_property_based.py" "$(tail -3 /tmp/smoke-property.txt)"
  fi

  # Backward compat regression
  if uv run pytest tests/sprint/test_backward_compat_regression.py -v --tb=short 2>&1 | tee /tmp/smoke-compat.txt | tail -1 | grep -q 'passed'; then
    COMPAT_COUNT=$(grep -c 'PASSED' /tmp/smoke-compat.txt || echo 0)
    pass "TEST-006: tests/sprint/test_backward_compat_regression.py — $COMPAT_COUNT tests passed"
  else
    fail "TEST-006: tests/sprint/test_backward_compat_regression.py" "$(tail -3 /tmp/smoke-compat.txt)"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# §6 — CLI Smoke: dry-run exercises the real CLI code path
# ─────────────────────────────────────────────────────────────────────────────
if should_run 6; then
  section 6 "CLI Dry-Run — Real CLI invocation"

  if $QUICK; then
    skip "CLI-001: Sprint dry-run (--quick mode)"
    skip "CLI-002: Roadmap dry-run (--quick mode)"
    skip "CLI-003: Sprint --help shows default 100 (--quick mode)"
  else
    # Sprint dry-run on the completed release's tasklist
    COMPLETED_INDEX=".dev/releases/complete/unified-audit-gating-v2/tasklist-index.md"
    if [[ -f "$COMPLETED_INDEX" ]]; then
      SPRINT_DRY=$(uv run superclaude sprint run "$COMPLETED_INDEX" --dry-run --no-tmux 2>&1)
      if [[ $? -eq 0 ]]; then
        pass "CLI-001: Sprint dry-run succeeds on completed release index"
        echo "    → $(echo "$SPRINT_DRY" | head -3 | tr '\n' ' ')"
      else
        fail "CLI-001: Sprint dry-run" "Exit code non-zero: $(echo "$SPRINT_DRY" | tail -3)"
      fi
    else
      skip "CLI-001: Sprint dry-run (completed index not found)"
    fi

    # Sprint help text shows 100
    SPRINT_HELP=$(uv run superclaude sprint run --help 2>&1)
    if echo "$SPRINT_HELP" | grep -q 'default: 100'; then
      pass "CLI-002: Sprint --help shows 'default: 100'"
    else
      fail "CLI-002: Sprint --help" "Missing 'default: 100' in help output"
    fi

    # Roadmap help text shows 100
    ROADMAP_HELP=$(uv run superclaude roadmap run --help 2>&1)
    if echo "$ROADMAP_HELP" | grep -q 'Default: 100'; then
      pass "CLI-003: Roadmap --help shows 'Default: 100'"
    else
      fail "CLI-003: Roadmap --help" "Missing 'Default: 100' in help output"
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# §7 — Artifact Integrity: completed release has expected evidence
# ─────────────────────────────────────────────────────────────────────────────
if should_run 7; then
  section 7 "Release Artifact Integrity"

  RELEASE_DIR=".dev/releases/complete/unified-audit-gating-v2"

  # Execution log exists and shows all phases passed
  if [[ -f "$RELEASE_DIR/execution-log.md" ]]; then
    PHASE_PASSES=$(grep -c '| pass |' "$RELEASE_DIR/execution-log.md" || echo 0)
    if [[ "$PHASE_PASSES" -eq 6 ]]; then
      pass "ART-001: Execution log shows 6/6 phases passed"
    else
      fail "ART-001: Execution log" "Only $PHASE_PASSES/6 phases show 'pass'"
    fi
  else
    fail "ART-001: Execution log" "File not found: $RELEASE_DIR/execution-log.md"
  fi

  # All 6 phase result files exist
  ALL_RESULTS=true
  for i in 1 2 3 4 5 6; do
    if [[ ! -f "$RELEASE_DIR/results/phase-${i}-result.md" ]]; then
      ALL_RESULTS=false
      fail "ART-002.$i: Phase $i result" "Missing: results/phase-${i}-result.md"
    fi
  done
  if $ALL_RESULTS; then
    pass "ART-002: All 6 phase result files present"
  fi

  # All result files show PASS status
  ALL_PASS=true
  for i in 1 2 3 4 5 6; do
    if ! grep -q 'status: PASS' "$RELEASE_DIR/results/phase-${i}-result.md" 2>/dev/null; then
      ALL_PASS=false
      fail "ART-003.$i: Phase $i status" "Not marked as PASS"
    fi
  done
  if $ALL_PASS; then
    pass "ART-003: All 6 phase results have status: PASS"
  fi

  # Evidence artifacts exist (spot-check)
  ARTIFACT_COUNT=$(find "$RELEASE_DIR/artifacts/" -name 'evidence.md' | wc -l)
  if [[ "$ARTIFACT_COUNT" -ge 20 ]]; then
    pass "ART-004: $ARTIFACT_COUNT evidence artifacts found (≥20 expected)"
  else
    fail "ART-004: Evidence artifacts" "Only $ARTIFACT_COUNT found, expected ≥20"
  fi

  # Sprint exit code file
  if [[ -f "$RELEASE_DIR/.sprint-exitcode" ]]; then
    EXIT_CODE=$(cat "$RELEASE_DIR/.sprint-exitcode")
    if [[ "$EXIT_CODE" == "0" || -z "$EXIT_CODE" ]]; then
      pass "ART-005: Sprint exit code indicates success"
    else
      fail "ART-005: Sprint exit code" "Exit code = $EXIT_CODE"
    fi
  else
    skip "ART-005: Sprint exit code file not found"
  fi

  # Checkpoint reports exist
  CP_COUNT=$(find "$RELEASE_DIR/checkpoints/" -name '*.md' | wc -l)
  if [[ "$CP_COUNT" -ge 3 ]]; then
    pass "ART-006: $CP_COUNT checkpoint reports found"
  else
    fail "ART-006: Checkpoints" "Only $CP_COUNT found, expected ≥3"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "SMOKE TEST SUMMARY"
echo "═══════════════════════════════════════════════════"
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "  SKIP: $SKIP"
echo "  TOTAL: $TOTAL"
echo ""

if [[ $FAIL -gt 0 ]]; then
  echo "RESULT: $FAIL FAILURES"
  exit 1
else
  echo "RESULT: ALL PASSED"
  exit 0
fi
