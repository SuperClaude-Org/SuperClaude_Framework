#!/usr/bin/env bash
# Run the error_max_turns detection functional test and capture results.
#
# Usage:
#   bash run_error_max_turns_test.sh
#
# Exits with the pytest exit code (0 = all passed, nonzero = failure).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
RESULTS_FILE="$SCRIPT_DIR/error_max_turns_results.txt"

echo "=== error_max_turns Detection Functional Test ==="
echo "Project root: $PROJECT_ROOT"
echo "Test file:    $SCRIPT_DIR/test_error_max_turns_detection.py"
echo "Results file: $RESULTS_FILE"
echo ""

cd "$PROJECT_ROOT"

# Run the test with verbose output, capturing to results file.
# Use set +e so we can capture the exit code without the script aborting.
set +e
uv run pytest \
    "$SCRIPT_DIR/test_error_max_turns_detection.py" \
    -v \
    --tb=short \
    --no-header \
    2>&1 | tee "$RESULTS_FILE"
EXIT_CODE=${PIPESTATUS[0]}
set -e

echo ""
echo "=== Test run complete (exit code: $EXIT_CODE) ==="
echo "Results saved to: $RESULTS_FILE"

exit "$EXIT_CODE"
