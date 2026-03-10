#!/bin/bash
# ==============================================================================
# Full Suite Smoke Test — unified-audit-gating-v1.2.1
# ==============================================================================
# Runs the complete sprint and pipeline test suites to verify no regressions
# were introduced by the release. Captures all output, produces a summary
# report, and exits non-zero if either suite has failures.
#
# Usage:
#   bash .dev/releases/current/unified-audit-gating-v1.2.1/test-evidence/smoke/run_full_suite_smoke.sh
#
# Outputs (relative to project root):
#   .dev/releases/current/unified-audit-gating-v1.2.1/test-evidence/smoke/sprint_output.txt
#   .dev/releases/current/unified-audit-gating-v1.2.1/test-evidence/smoke/pipeline_output.txt
#   .dev/releases/current/unified-audit-gating-v1.2.1/test-evidence/smoke/full_suite_results.txt
# ==============================================================================

set -o pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT="/config/workspace/SuperClaude_Framework"
EVIDENCE_DIR="${PROJECT_ROOT}/.dev/releases/current/unified-audit-gating-v1.2.1/test-evidence/smoke"
SPRINT_OUTPUT="${EVIDENCE_DIR}/sprint_output.txt"
PIPELINE_OUTPUT="${EVIDENCE_DIR}/pipeline_output.txt"
SUMMARY_FILE="${EVIDENCE_DIR}/full_suite_results.txt"

RELEASE_TAG="unified-audit-gating-v1.2.1"
TIMESTAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
cd "${PROJECT_ROOT}" || { echo "FATAL: cannot cd to ${PROJECT_ROOT}"; exit 1; }
mkdir -p "${EVIDENCE_DIR}"

# Truncate / create output files so they always exist even on early failure.
: > "${SPRINT_OUTPUT}"
: > "${PIPELINE_OUTPUT}"
: > "${SUMMARY_FILE}"

# ---------------------------------------------------------------------------
# Helper: extract pytest summary line and counts
# ---------------------------------------------------------------------------
# Parses the short test summary line that pytest prints at the end, e.g.:
#   "===== 573 passed, 5 skipped in 12.34s ====="
# Returns: passed failed skipped errors total exit_code
parse_pytest_results() {
    local output_file="$1"
    local exit_code="$2"

    local passed=0 failed=0 skipped=0 errors=0

    # The summary line is the last "====..." line in the output.
    local summary_line
    summary_line="$(grep -E '^=+ .+ =+$' "${output_file}" | tail -1)"

    if [[ -n "${summary_line}" ]]; then
        # Extract individual counts via pattern matching.
        local p f s e
        p="$(echo "${summary_line}" | grep -oP '\d+(?= passed)')"
        f="$(echo "${summary_line}" | grep -oP '\d+(?= failed)')"
        s="$(echo "${summary_line}" | grep -oP '\d+(?= skipped)')"
        e="$(echo "${summary_line}" | grep -oP '\d+(?= error)')"
        [[ -n "$p" ]] && passed="$p"
        [[ -n "$f" ]] && failed="$f"
        [[ -n "$s" ]] && skipped="$s"
        [[ -n "$e" ]] && errors="$e"
    fi

    local total=$(( passed + failed + skipped + errors ))
    echo "${passed} ${failed} ${skipped} ${errors} ${total} ${exit_code}"
}

# ---------------------------------------------------------------------------
# Helper: extract failure details from pytest output
# ---------------------------------------------------------------------------
extract_failures() {
    local output_file="$1"
    # Capture the FAILURES section if present (between the two marker lines).
    sed -n '/^=\+ FAILURES =\+$/,/^=\+/p' "${output_file}" 2>/dev/null | head -200
}

# ---------------------------------------------------------------------------
# Run Sprint Suite
# ---------------------------------------------------------------------------
echo "[$(date -u '+%H:%M:%S')] Running sprint test suite..."

uv run pytest tests/sprint/ -v --tb=short 2>&1 | tee "${SPRINT_OUTPUT}"
SPRINT_EXIT=${PIPESTATUS[0]}

echo "[$(date -u '+%H:%M:%S')] Sprint suite finished (exit code: ${SPRINT_EXIT})"

# ---------------------------------------------------------------------------
# Run Pipeline Suite
# ---------------------------------------------------------------------------
echo "[$(date -u '+%H:%M:%S')] Running pipeline test suite..."

uv run pytest tests/pipeline/ -v --tb=short 2>&1 | tee "${PIPELINE_OUTPUT}"
PIPELINE_EXIT=${PIPESTATUS[0]}

echo "[$(date -u '+%H:%M:%S')] Pipeline suite finished (exit code: ${PIPELINE_EXIT})"

# ---------------------------------------------------------------------------
# Parse Results
# ---------------------------------------------------------------------------
read -r SP_PASS SP_FAIL SP_SKIP SP_ERR SP_TOTAL SP_EC <<< "$(parse_pytest_results "${SPRINT_OUTPUT}" "${SPRINT_EXIT}")"
read -r PL_PASS PL_FAIL PL_SKIP PL_ERR PL_TOTAL PL_EC <<< "$(parse_pytest_results "${PIPELINE_OUTPUT}" "${PIPELINE_EXIT}")"

TOTAL_PASS=$(( SP_PASS + PL_PASS ))
TOTAL_FAIL=$(( SP_FAIL + PL_FAIL ))
TOTAL_SKIP=$(( SP_SKIP + PL_SKIP ))
TOTAL_ERR=$(( SP_ERR + PL_ERR ))
GRAND_TOTAL=$(( SP_TOTAL + PL_TOTAL ))

# Determine verdicts.
if [[ ${SPRINT_EXIT} -eq 0 ]]; then SPRINT_VERDICT="PASS"; else SPRINT_VERDICT="FAIL"; fi
if [[ ${PIPELINE_EXIT} -eq 0 ]]; then PIPELINE_VERDICT="PASS"; else PIPELINE_VERDICT="FAIL"; fi

if [[ ${SPRINT_EXIT} -eq 0 && ${PIPELINE_EXIT} -eq 0 ]]; then
    OVERALL_VERDICT="PASS"
    OVERALL_EXIT=0
else
    OVERALL_VERDICT="FAIL"
    OVERALL_EXIT=1
fi

# ---------------------------------------------------------------------------
# Generate Summary Report
# ---------------------------------------------------------------------------
cat > "${SUMMARY_FILE}" <<REPORT
================================================================================
  FULL SUITE SMOKE TEST RESULTS — ${RELEASE_TAG}
================================================================================
Timestamp : ${TIMESTAMP}
Project   : ${PROJECT_ROOT}
Branch    : $(git -C "${PROJECT_ROOT}" branch --show-current 2>/dev/null || echo "unknown")
Commit    : $(git -C "${PROJECT_ROOT}" rev-parse --short HEAD 2>/dev/null || echo "unknown")

--------------------------------------------------------------------------------
  SUITE RESULTS
--------------------------------------------------------------------------------

  Sprint Suite (tests/sprint/)
    Exit code : ${SPRINT_EXIT}
    Verdict   : ${SPRINT_VERDICT}
    Passed    : ${SP_PASS}
    Failed    : ${SP_FAIL}
    Skipped   : ${SP_SKIP}
    Errors    : ${SP_ERR}
    Total     : ${SP_TOTAL}

  Pipeline Suite (tests/pipeline/)
    Exit code : ${PIPELINE_EXIT}
    Verdict   : ${PIPELINE_VERDICT}
    Passed    : ${PL_PASS}
    Failed    : ${PL_FAIL}
    Skipped   : ${PL_SKIP}
    Errors    : ${PL_ERR}
    Total     : ${PL_TOTAL}

--------------------------------------------------------------------------------
  AGGREGATE
--------------------------------------------------------------------------------
    Total passed  : ${TOTAL_PASS}
    Total failed  : ${TOTAL_FAIL}
    Total skipped : ${TOTAL_SKIP}
    Total errors  : ${TOTAL_ERR}
    Grand total   : ${GRAND_TOTAL}

================================================================================
  OVERALL VERDICT: ${OVERALL_VERDICT}
================================================================================
REPORT

# Append failure details if any suite failed.
if [[ "${OVERALL_VERDICT}" == "FAIL" ]]; then
    {
        echo ""
        echo "================================================================================"
        echo "  FAILURE DETAILS"
        echo "================================================================================"

        if [[ "${SPRINT_VERDICT}" == "FAIL" ]]; then
            echo ""
            echo "--- Sprint Failures ---"
            SPRINT_FAILURES="$(extract_failures "${SPRINT_OUTPUT}")"
            if [[ -n "${SPRINT_FAILURES}" ]]; then
                echo "${SPRINT_FAILURES}"
            else
                echo "(no structured FAILURES section found; check sprint_output.txt)"
            fi
        fi

        if [[ "${PIPELINE_VERDICT}" == "FAIL" ]]; then
            echo ""
            echo "--- Pipeline Failures ---"
            PIPELINE_FAILURES="$(extract_failures "${PIPELINE_OUTPUT}")"
            if [[ -n "${PIPELINE_FAILURES}" ]]; then
                echo "${PIPELINE_FAILURES}"
            else
                echo "(no structured FAILURES section found; check pipeline_output.txt)"
            fi
        fi
    } >> "${SUMMARY_FILE}"
fi

# ---------------------------------------------------------------------------
# Print Summary to stdout
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
echo "  SMOKE TEST COMPLETE"
echo "========================================"
echo "  Sprint  : ${SPRINT_VERDICT} (${SP_PASS} passed, ${SP_FAIL} failed, ${SP_SKIP} skipped)"
echo "  Pipeline: ${PIPELINE_VERDICT} (${PL_PASS} passed, ${PL_FAIL} failed, ${PL_SKIP} skipped)"
echo "  Overall : ${OVERALL_VERDICT}"
echo "========================================"
echo ""
echo "Artifacts:"
echo "  ${SPRINT_OUTPUT}"
echo "  ${PIPELINE_OUTPUT}"
echo "  ${SUMMARY_FILE}"
echo ""

exit ${OVERALL_EXIT}
