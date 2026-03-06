#!/usr/bin/env bash
# v2.13 CLIRunner Pipeline Targeted Fixes — Validation & Eval Script
# Runs all validation sections in parallel where possible, outputs structured log.
#
# Usage:
#   ./scripts/v2.13-validate.sh                  # Run all sections
#   ./scripts/v2.13-validate.sh --section 3      # Run only section 3
#   ./scripts/v2.13-validate.sh --section 1,3,6  # Run sections 1, 3, and 6
#   ./scripts/v2.13-validate.sh --log FILE        # Write log to FILE (default: stdout + v2.13-eval.log)
#   ./scripts/v2.13-validate.sh --no-color        # Disable color output
#   ./scripts/v2.13-validate.sh --help            # Show this help

set -uo pipefail

# ── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/v2.13-eval.log"
TMPDIR_BASE=$(mktemp -d "${TMPDIR:-/tmp}/v213-eval.XXXXXX")
RESULTS_DIR="$TMPDIR_BASE/results"
mkdir -p "$RESULTS_DIR"
SECTIONS_FILTER=""
USE_COLOR=1
START_TIME=$(date +%s)

# ── Argument Parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --section)  SECTIONS_FILTER="$2"; shift 2 ;;
        --log)      LOG_FILE="$2"; shift 2 ;;
        --no-color) USE_COLOR=0; shift ;;
        --help|-h)
            head -9 "$0" | tail -7
            exit 0
            ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# ── Color helpers ────────────────────────────────────────────────────────────
if [[ "$USE_COLOR" -eq 1 ]] && [[ -t 1 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; DIM=''; RESET=''
fi

# ── Utilities ────────────────────────────────────────────────────────────────
log() { printf "${DIM}[%s]${RESET} %s\n" "$(date +%H:%M:%S)" "$*"; }
pass() { printf "${GREEN}  PASS${RESET} %s\n" "$*"; }
fail() { printf "${RED}  FAIL${RESET} %s\n" "$*"; }
warn() { printf "${YELLOW}  WARN${RESET} %s\n" "$*"; }
header() {
    printf "\n${BOLD}${CYAN}━━━ Section %s: %s ━━━${RESET}\n" "$1" "$2"
}

should_run() {
    local section="$1"
    if [[ -z "$SECTIONS_FILTER" ]]; then return 0; fi
    echo ",$SECTIONS_FILTER," | grep -q ",$section,"
}

# File-based result tracking (works across subshells)
mark_pass() { touch "$RESULTS_DIR/$1.pass"; }
mark_fail() { touch "$RESULTS_DIR/$1.fail"; }
mark_skip() { touch "$RESULTS_DIR/$1.skip"; }

# Run a pytest command, capture output, return pass/fail
run_pytest() {
    local label="$1"; shift
    local outfile="$1"; shift
    if uv run pytest "$@" > "$outfile" 2>&1; then
        local counts
        counts=$(tail -5 "$outfile" | grep -oE '[0-9]+ passed' | head -1 || echo "0 passed")
        pass "$label ($counts)"
        return 0
    else
        local err_line
        err_line=$(tail -5 "$outfile" | grep -E 'failed|error' | head -1 || echo "see log")
        fail "$label — $err_line"
        return 1
    fi
}

cleanup() { rm -rf "$TMPDIR_BASE"; }
trap cleanup EXIT

cd "$PROJECT_ROOT"

# Export functions and variables for subshells
export TMPDIR_BASE RESULTS_DIR USE_COLOR PROJECT_ROOT
export RED GREEN YELLOW CYAN BOLD DIM RESET

# ── Begin Log ────────────────────────────────────────────────────────────────
{
printf "${BOLD}v2.13 CLIRunner Pipeline Targeted Fixes — Validation Run${RESET}\n"
printf "Date:    %s\n" "$(date -Iseconds)"
printf "Branch:  %s\n" "$(git branch --show-current 2>/dev/null || echo 'detached')"
printf "Commit:  %s\n" "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
printf "Project: %s\n" "$PROJECT_ROOT"
printf "Log:     %s\n" "$LOG_FILE"

# ═════════════════════════════════════════════════════════════════════════════
# WAVE 1 — Fully Independent Checks (run in parallel)
# ═════════════════════════════════════════════════════════════════════════════

log "Wave 1: Independent checks (parallel)"

# ── Section 1: Smoke Tests ───────────────────────────────────────────────────
if should_run 1; then
    (
        header 1 "Smoke Tests"
        local_fail=0

        # 1a. Full suite
        run_pytest "Full suite (pipeline+sprint+roadmap)" "$TMPDIR_BASE/s1-full.txt" \
            tests/pipeline/ tests/sprint/ tests/roadmap/ -q --tb=line \
            || local_fail=1

        # 1b. Import checks
        for mod in \
            "superclaude.cli.pipeline.process:ClaudeProcess:pipeline" \
            "superclaude.cli.sprint.process:ClaudeProcess:sprint" \
            "superclaude.cli.roadmap.executor:execute_roadmap:roadmap"; do
            IFS=: read -r module symbol label <<< "$mod"
            if uv run python -c "from $module import $symbol" 2>/dev/null; then
                pass "Import $label OK"
            else
                fail "Import $label BROKEN"
                local_fail=1
            fi
        done

        if [[ $local_fail -eq 0 ]]; then mark_pass "1-Smoke"; else mark_fail "1-Smoke"; fi
    ) &
    PID_S1=$!
else
    mark_skip "1-Smoke"
fi

# ── Section 2: NFR-007 Compliance ────────────────────────────────────────────
if should_run 2; then
    (
        header 2 "NFR-007 — No Reverse Imports"
        local_fail=0

        # 2a. Grep for actual import statements only (exclude comments/docstrings)
        # Match lines that start with 'from' or 'import' (possibly indented)
        violations=$(grep -rn \
            -e "^from superclaude\.cli\.sprint" \
            -e "^from superclaude\.cli\.roadmap" \
            -e "^import superclaude\.cli\.sprint" \
            -e "^import superclaude\.cli\.roadmap" \
            -e "^[[:space:]]*from superclaude\.cli\.sprint" \
            -e "^[[:space:]]*from superclaude\.cli\.roadmap" \
            -e "^[[:space:]]*import superclaude\.cli\.sprint" \
            -e "^[[:space:]]*import superclaude\.cli\.roadmap" \
            --include="*.py" \
            src/superclaude/cli/pipeline/ 2>/dev/null | wc -l)
        if [[ "$violations" -eq 0 ]]; then
            pass "Zero reverse imports in pipeline/ (code-only check)"
        else
            fail "$violations reverse import(s) found in pipeline/"
            grep -rn \
                -e "^[[:space:]]*from superclaude\.cli\.sprint" \
                -e "^[[:space:]]*from superclaude\.cli\.roadmap" \
                -e "^[[:space:]]*import superclaude\.cli\.sprint" \
                -e "^[[:space:]]*import superclaude\.cli\.roadmap" \
                --include="*.py" \
                src/superclaude/cli/pipeline/ 2>/dev/null || true
            local_fail=1
        fi

        # 2b. NFR compliance tests
        run_pytest "NFR compliance tests" "$TMPDIR_BASE/s2-nfr.txt" \
            tests/roadmap/test_nfr_compliance.py -v --tb=short \
            || local_fail=1

        run_pytest "Path conventions" "$TMPDIR_BASE/s2-path.txt" \
            tests/sc-roadmap/compliance/test_path_conventions.py -v --tb=short \
            || local_fail=1

        if [[ $local_fail -eq 0 ]]; then mark_pass "2-NFR007"; else mark_fail "2-NFR007"; fi
    ) &
    PID_S2=$!
else
    mark_skip "2-NFR007"
fi

# ── Section 9: Manual Spot Checks ────────────────────────────────────────────
if should_run 9; then
    (
        header 9 "Spot Checks"
        local_fail=0

        # 9a. Dead code candidates are used
        refs_forbidden=$(grep -rn "_FORBIDDEN_FLAGS" src/superclaude/cli/roadmap/ 2>/dev/null | wc -l)
        refs_argv=$(grep -rn "_build_subprocess_argv" src/superclaude/cli/roadmap/ 2>/dev/null | wc -l)
        if [[ "$refs_forbidden" -gt 0 ]] && [[ "$refs_argv" -gt 0 ]]; then
            pass "_FORBIDDEN_FLAGS ($refs_forbidden refs) and _build_subprocess_argv ($refs_argv refs) in active use"
        else
            warn "Dead code symbols may be unused (FORBIDDEN=$refs_forbidden, ARGV=$refs_argv)"
        fi

        # 9b. Sprint process.py line count
        lines=$(wc -l < src/superclaude/cli/sprint/process.py)
        if [[ "$lines" -le 200 ]]; then
            pass "sprint/process.py: $lines lines (reduced from 201)"
        else
            warn "sprint/process.py: $lines lines (expected <= 200)"
        fi

        # 9c. Hook callbacks in pipeline base
        hook_refs=$(grep -c -E "on_spawn|on_exit|on_signal" src/superclaude/cli/pipeline/process.py || true)
        if [[ "$hook_refs" -gt 0 ]]; then
            pass "Pipeline base has $hook_refs hook references"
        else
            fail "No hook callbacks found in pipeline/process.py"
            local_fail=1
        fi

        # 9d. Method override check
        override_output=$(uv run python -c "
from superclaude.cli.sprint.process import ClaudeProcess as S
from superclaude.cli.pipeline.process import ClaudeProcess as P
overrides = [m for m in ['start','wait','terminate'] if getattr(S,m) is not getattr(P,m)]
if overrides:
    print('OVERRIDES: ' + ','.join(overrides))
else:
    print('NO_OVERRIDES')
" 2>/dev/null)
        if [[ "$override_output" == "NO_OVERRIDES" ]]; then
            pass "Sprint ClaudeProcess inherits start/wait/terminate (no overrides)"
        else
            fail "Sprint ClaudeProcess still overrides: $override_output"
            local_fail=1
        fi

        # 9e. No new dependencies
        dep_changes=$(git diff master -- pyproject.toml 2>/dev/null | grep -c "^\+.*dependencies" || true)
        if [[ "$dep_changes" -eq 0 ]]; then
            pass "No new package dependencies (NFR-004)"
        else
            warn "pyproject.toml dependency changes detected ($dep_changes lines)"
        fi

        if [[ $local_fail -eq 0 ]]; then mark_pass "9-SpotChecks"; else mark_fail "9-SpotChecks"; fi
    ) &
    PID_S9=$!
else
    mark_skip "9-SpotChecks"
fi

# Wait for Wave 1
for pid_var in PID_S1 PID_S2 PID_S9; do
    if [[ -n "${!pid_var:-}" ]]; then
        wait "${!pid_var}" 2>/dev/null || true
    fi
done
log "Wave 1 complete"

# ═════════════════════════════════════════════════════════════════════════════
# WAVE 2 — Per-Milestone Validation (run in parallel: M1, M2, M3 independent)
# ═════════════════════════════════════════════════════════════════════════════

log "Wave 2: Per-milestone validation (parallel)"

# ── Section 3: M1 — Characterization Tests ───────────────────────────────────
if should_run 3; then
    (
        header 3 "M1 — Sprint Executor Characterization Tests"
        local_fail=0

        run_pytest "Watchdog/stall detection" "$TMPDIR_BASE/s3-watchdog.txt" \
            tests/sprint/test_watchdog.py -v --tb=short \
            || local_fail=1

        run_pytest "Multi-phase sequencing" "$TMPDIR_BASE/s3-multi.txt" \
            tests/sprint/test_multi_phase.py -v --tb=short \
            || local_fail=1

        run_pytest "TUI/monitor integration" "$TMPDIR_BASE/s3-tui.txt" \
            tests/sprint/test_tui_monitor.py -v --tb=short \
            || local_fail=1

        run_pytest "Diagnostics" "$TMPDIR_BASE/s3-diag.txt" \
            tests/sprint/test_diagnostics.py -v --tb=short \
            || local_fail=1

        # Coverage check
        uv run pytest tests/sprint/test_executor.py \
            --cov=superclaude.cli.sprint.executor --cov-report=term-missing -q \
            > "$TMPDIR_BASE/s3-cov.txt" 2>&1 || true
        cov_pct=$(grep "TOTAL" "$TMPDIR_BASE/s3-cov.txt" | awk '{print $NF}' | tr -d '%' || echo "0")
        if [[ "${cov_pct:-0}" -ge 70 ]]; then
            pass "Sprint executor coverage: ${cov_pct}% (target: >= 70%)"
        else
            fail "Sprint executor coverage: ${cov_pct}% (target: >= 70%)"
            local_fail=1
        fi

        if [[ $local_fail -eq 0 ]]; then mark_pass "3-M1-CharTests"; else mark_fail "3-M1-CharTests"; fi
    ) &
    PID_S3=$!
else
    mark_skip "3-M1-CharTests"
fi

# ── Section 4: M2 — Process Hook Migration ──────────────────────────────────
if should_run 4; then
    (
        header 4 "M2 — Process Hook Migration"
        local_fail=0

        run_pytest "Pipeline hook tests" "$TMPDIR_BASE/s4-hooks.txt" \
            tests/pipeline/test_process_hooks.py -v --tb=short \
            || local_fail=1

        run_pytest "Sprint process tests" "$TMPDIR_BASE/s4-sprint.txt" \
            tests/sprint/test_process.py -v --tb=short \
            || local_fail=1

        run_pytest "Behavioral equivalence" "$TMPDIR_BASE/s4-behav.txt" \
            tests/pipeline/test_behavioral.py -v --tb=short \
            || local_fail=1

        if [[ $local_fail -eq 0 ]]; then mark_pass "4-M2-Hooks"; else mark_fail "4-M2-Hooks"; fi
    ) &
    PID_S4=$!
else
    mark_skip "4-M2-Hooks"
fi

# ── Section 5: M3 — Roadmap File-Passing Fix ────────────────────────────────
if should_run 5; then
    (
        header 5 "M3 — Roadmap File-Passing Fix"
        local_fail=0

        run_pytest "Embed inputs" "$TMPDIR_BASE/s5-embed.txt" \
            tests/roadmap/test_embed_inputs.py -v --tb=short \
            || local_fail=1

        run_pytest "File passing" "$TMPDIR_BASE/s5-file.txt" \
            tests/roadmap/test_file_passing.py -v --tb=short \
            || local_fail=1

        run_pytest "Roadmap executor" "$TMPDIR_BASE/s5-exec.txt" \
            tests/roadmap/test_executor.py -v --tb=short \
            || local_fail=1

        if [[ $local_fail -eq 0 ]]; then mark_pass "5-M3-FilePassing"; else mark_fail "5-M3-FilePassing"; fi
    ) &
    PID_S5=$!
else
    mark_skip "5-M3-FilePassing"
fi

# ── Section 6: Signal Handling Regression ────────────────────────────────────
if should_run 6; then
    (
        header 6 "Signal Handling Regression"
        local_fail=0

        run_pytest "Signal integration" "$TMPDIR_BASE/s6-signal.txt" \
            tests/sprint/test_integration_signal.py -v --tb=short \
            || local_fail=1

        run_pytest "Halt integration" "$TMPDIR_BASE/s6-halt.txt" \
            tests/sprint/test_integration_halt.py -v --tb=short \
            || local_fail=1

        run_pytest "E2E halt" "$TMPDIR_BASE/s6-e2ehalt.txt" \
            tests/sprint/test_e2e_halt.py -v --tb=short \
            || local_fail=1

        run_pytest "Lifecycle integration" "$TMPDIR_BASE/s6-lifecycle.txt" \
            tests/sprint/test_integration_lifecycle.py -v --tb=short \
            || local_fail=1

        run_pytest "E2E success" "$TMPDIR_BASE/s6-e2eok.txt" \
            tests/sprint/test_e2e_success.py -v --tb=short \
            || local_fail=1

        if [[ $local_fail -eq 0 ]]; then mark_pass "6-Signals"; else mark_fail "6-Signals"; fi
    ) &
    PID_S6=$!
else
    mark_skip "6-Signals"
fi

# ── Section 7: Pipeline Module Integrity ─────────────────────────────────────
if should_run 7; then
    (
        header 7 "Pipeline Module Integrity"
        local_fail=0

        run_pytest "All pipeline tests" "$TMPDIR_BASE/s7-pipe.txt" \
            tests/pipeline/ -v --tb=short \
            || local_fail=1

        # Coverage
        uv run pytest tests/pipeline/ \
            --cov=superclaude.cli.pipeline --cov-report=term-missing -q \
            > "$TMPDIR_BASE/s7-cov.txt" 2>&1 || true
        cov_line=$(grep "TOTAL" "$TMPDIR_BASE/s7-cov.txt" | head -1 || echo "TOTAL ? ? ? 0%")
        pass "Pipeline coverage: $(echo "$cov_line" | awk '{print $NF}')"

        if [[ $local_fail -eq 0 ]]; then mark_pass "7-Pipeline"; else mark_fail "7-Pipeline"; fi
    ) &
    PID_S7=$!
else
    mark_skip "7-Pipeline"
fi

# Wait for Wave 2
for pid_var in PID_S3 PID_S4 PID_S5 PID_S6 PID_S7; do
    if [[ -n "${!pid_var:-}" ]]; then
        wait "${!pid_var}" 2>/dev/null || true
    fi
done
log "Wave 2 complete"

# ═════════════════════════════════════════════════════════════════════════════
# WAVE 3 — Cross-Module Integration (depends on Waves 1+2 for confidence)
# ═════════════════════════════════════════════════════════════════════════════

if should_run 8; then
    log "Wave 3: Cross-module integration"
    header 8 "Cross-Module Integration"
    local_fail=0

    run_pytest "Sprint regression gaps" "$TMPDIR_BASE/s8-regress.txt" \
        tests/sprint/test_regression_gaps.py -v --tb=short \
        || local_fail=1

    run_pytest "Pipeline gates" "$TMPDIR_BASE/s8-gates.txt" \
        tests/pipeline/test_gates.py -v --tb=short \
        || local_fail=1

    run_pytest "Pipeline executor" "$TMPDIR_BASE/s8-pexec.txt" \
        tests/pipeline/test_executor.py -v --tb=short \
        || local_fail=1

    if [[ $local_fail -eq 0 ]]; then mark_pass "8-Integration"; else mark_fail "8-Integration"; fi
else
    mark_skip "8-Integration"
fi

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY — Read results from file markers
# ═════════════════════════════════════════════════════════════════════════════

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Ordered section names for display
ALL_SECTIONS=(
    "1-Smoke"
    "2-NFR007"
    "3-M1-CharTests"
    "4-M2-Hooks"
    "5-M3-FilePassing"
    "6-Signals"
    "7-Pipeline"
    "8-Integration"
    "9-SpotChecks"
)

printf "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
printf "${BOLD}               v2.13 VALIDATION SUMMARY${RESET}\n"
printf "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n\n"

printf "  Duration:  %dm %ds\n" $((DURATION / 60)) $((DURATION % 60))
printf "  Branch:    %s\n" "$(git branch --show-current 2>/dev/null || echo 'detached')"
printf "  Commit:    %s\n\n" "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"

printf "  %-25s %s\n" "Section" "Result"
printf "  %-25s %s\n" "-------------------------" "------"

total_pass=0
total_fail=0
total_skip=0

for s in "${ALL_SECTIONS[@]}"; do
    if [[ -f "$RESULTS_DIR/$s.pass" ]]; then
        printf "  %-25s ${GREEN}PASS${RESET}\n" "$s"
        total_pass=$((total_pass + 1))
    elif [[ -f "$RESULTS_DIR/$s.fail" ]]; then
        printf "  %-25s ${RED}FAIL${RESET}\n" "$s"
        total_fail=$((total_fail + 1))
    elif [[ -f "$RESULTS_DIR/$s.skip" ]]; then
        printf "  %-25s ${DIM}SKIP${RESET}\n" "$s"
        total_skip=$((total_skip + 1))
    fi
done

printf "\n"

if [[ $total_fail -eq 0 ]] && [[ $total_pass -gt 0 ]]; then
    printf "  ${GREEN}${BOLD}RESULT: ALL %d SECTIONS PASSED${RESET}" "$total_pass"
    [[ $total_skip -gt 0 ]] && printf " ${DIM}(%d skipped)${RESET}" "$total_skip"
    printf "\n"
    EXIT_CODE=0
elif [[ $total_fail -gt 0 ]]; then
    printf "  ${RED}${BOLD}RESULT: %d FAILED${RESET}, ${GREEN}%d passed${RESET}, ${DIM}%d skipped${RESET}\n" \
        "$total_fail" "$total_pass" "$total_skip"
    EXIT_CODE=1

    # Show failure details
    printf "\n  ${BOLD}Failure logs:${RESET}\n"
    for f in "$TMPDIR_BASE"/s*.txt; do
        if [[ -f "$f" ]] && grep -qE "FAILED|ERROR" "$f" 2>/dev/null; then
            printf "    %s\n" "$f"
        fi
    done
else
    printf "  ${YELLOW}${BOLD}RESULT: Nothing ran (check --section filter)${RESET}\n"
    EXIT_CODE=2
fi

printf "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"

} 2>&1 | tee "$LOG_FILE"

# Append raw test outputs to log file for analysis
{
    printf "\n\n=== RAW TEST OUTPUTS ===\n"
    for f in "$TMPDIR_BASE"/s*.txt; do
        if [[ -f "$f" ]]; then
            printf "\n--- %s ---\n" "$(basename "$f")"
            cat "$f"
        fi
    done
} >> "$LOG_FILE" 2>/dev/null

printf "\nFull log (with raw output): %s\n" "$LOG_FILE"
exit "${EXIT_CODE:-0}"
