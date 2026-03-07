#!/usr/bin/env bash
# Runner script for TurnLedger economics functional test.
# Executes the pytest suite with verbose output, captures results to a file,
# and exits with the pytest exit code.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_FILE="${SCRIPT_DIR}/turnledger_results.txt"
TEST_FILE="${SCRIPT_DIR}/test_turnledger_economics.py"

echo "=== TurnLedger Economics Functional Test ==="
echo "Test file : ${TEST_FILE}"
echo "Results   : ${RESULTS_FILE}"
echo ""

# Run pytest with verbose output, capturing stdout+stderr to results file
# while also displaying on terminal (tee).
cd /config/workspace/SuperClaude_Framework

uv run pytest "${TEST_FILE}" -v --tb=short 2>&1 | tee "${RESULTS_FILE}"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=== Test run complete (exit code: ${EXIT_CODE}) ==="
echo "Results saved to: ${RESULTS_FILE}"

exit "${EXIT_CODE}"
