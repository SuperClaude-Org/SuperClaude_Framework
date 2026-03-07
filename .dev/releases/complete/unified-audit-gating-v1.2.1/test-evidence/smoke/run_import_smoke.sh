#!/usr/bin/env bash
# run_import_smoke.sh -- Execute the unified-audit-gating-v1.2.1 import smoke tests.
#
# Usage:
#   bash run_import_smoke.sh
#
# Output is captured to import_smoke_results.txt alongside this script.
# Exits with the pytest exit code (0 = all pass).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
RESULTS_FILE="$SCRIPT_DIR/import_smoke_results.txt"

echo "=== unified-audit-gating-v1.2.1 Import Smoke Test ==="
echo "Project root: $PROJECT_ROOT"
echo "Test file:    $SCRIPT_DIR/test_import_smoke.py"
echo "Results file: $RESULTS_FILE"
echo ""

cd "$PROJECT_ROOT"

# Run pytest with verbose output, capturing to results file and stdout
uv run pytest "$SCRIPT_DIR/test_import_smoke.py" -v --tb=short 2>&1 | tee "$RESULTS_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=== Exit code: $EXIT_CODE ==="
echo "Results saved to: $RESULTS_FILE"

exit "$EXIT_CODE"
