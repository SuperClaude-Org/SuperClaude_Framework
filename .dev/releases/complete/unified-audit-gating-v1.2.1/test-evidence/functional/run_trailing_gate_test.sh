#!/usr/bin/env bash
# Runner script for TrailingGateRunner async functional test.
# Executes the test with uv run pytest, captures output, exits with pytest code.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
RESULTS_FILE="$SCRIPT_DIR/trailing_gate_results.txt"

echo "=== TrailingGateRunner Async Functional Test ==="
echo "Project root: $PROJECT_ROOT"
echo "Test file:    $SCRIPT_DIR/test_trailing_gate_async.py"
echo "Results file: $RESULTS_FILE"
echo ""

cd "$PROJECT_ROOT"

uv run pytest \
    "$SCRIPT_DIR/test_trailing_gate_async.py" \
    -v \
    --tb=short \
    -x \
    2>&1 | tee "$RESULTS_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=== Test run complete. Exit code: $EXIT_CODE ==="
echo "Results saved to: $RESULTS_FILE"

exit "$EXIT_CODE"
