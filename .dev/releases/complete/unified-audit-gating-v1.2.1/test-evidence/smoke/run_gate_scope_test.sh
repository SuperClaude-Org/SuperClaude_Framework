#!/usr/bin/env bash
# Run the gate-scope safety smoke tests and capture output.
#
# Usage:
#   ./run_gate_scope_test.sh
#
# Outputs:
#   test-evidence/smoke/gate_scope_results.txt  -- full pytest output
#   Exit code matches pytest exit code (0 = all passed)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
RESULTS_FILE="$SCRIPT_DIR/gate_scope_results.txt"
TEST_FILE="$SCRIPT_DIR/test_gate_scope_safety.py"

echo "=== Gate Scope Safety Smoke Test ==="
echo "Repo root : $REPO_ROOT"
echo "Test file  : $TEST_FILE"
echo "Results    : $RESULTS_FILE"
echo ""

cd "$REPO_ROOT"

# Run pytest with verbose output, capturing to file and stdout
uv run pytest "$TEST_FILE" -v --tb=short 2>&1 | tee "$RESULTS_FILE"
EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=== Results written to: $RESULTS_FILE ==="
echo "=== Exit code: $EXIT_CODE ==="

exit "$EXIT_CODE"
