#!/usr/bin/env bash
# run_backward_compat_test.sh
# Runs the backward compatibility functional test for unified-audit-gating v1.2.1
# and captures output to test-evidence/functional/backward_compat_results.txt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
RESULTS_FILE="$SCRIPT_DIR/backward_compat_results.txt"

echo "=== Backward Compatibility Test: unified-audit-gating v1.2.1 ===" | tee "$RESULTS_FILE"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')" | tee -a "$RESULTS_FILE"
echo "Project root: $PROJECT_ROOT" | tee -a "$RESULTS_FILE"
echo "Test file: $SCRIPT_DIR/test_backward_compatibility.py" | tee -a "$RESULTS_FILE"
echo "---" | tee -a "$RESULTS_FILE"

cd "$PROJECT_ROOT"

uv run pytest \
    "$SCRIPT_DIR/test_backward_compatibility.py" \
    -v \
    --tb=long \
    --no-header \
    2>&1 | tee -a "$RESULTS_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "---" | tee -a "$RESULTS_FILE"
echo "Exit code: $EXIT_CODE" | tee -a "$RESULTS_FILE"
exit "$EXIT_CODE"
