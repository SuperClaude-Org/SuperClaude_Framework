#!/usr/bin/env bash
# =============================================================================
# COMPARE: Before/After Results Comparison
# =============================================================================
# Usage: bash compare-results.sh [baseline-label] [post-release-label]
# Example: bash compare-results.sh baseline post-v2.20
#
# Reads results from both runs and produces a delta report.
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

BENCHMARK_DIR=".dev/benchmarks/v2.20-baseline"
RESULTS_DIR="${BENCHMARK_DIR}/results"
LABEL_A="${1:-baseline}"
LABEL_B="${2:-post-release}"

echo "=================================================================="
echo "v2.20 BENCHMARK COMPARISON: ${LABEL_A} vs ${LABEL_B}"
echo "=================================================================="
echo ""

# Helper: extract JSON value (crude but works without jq)
json_val() {
    local file="$1"
    local key="$2"
    grep -oP "\"${key}\":\s*\K[^\",}]+" "$file" 2>/dev/null | head -1 || echo "N/A"
}

echo "TEST 1: Semantic Nonsense Gate Penetration"
echo "-------------------------------------------"
if [ -f "${RESULTS_DIR}/test-1-results.json" ]; then
    echo "  Files produced:            $(json_val "${RESULTS_DIR}/test-1-results.json" "files_produced") / 8"
    echo "  Nonsense in final roadmap: $(json_val "${RESULTS_DIR}/test-1-results.json" "nonsense_terms_in_final_roadmap") / $(json_val "${RESULTS_DIR}/test-1-results.json" "nonsense_terms_checked")"
    echo "  Propagation depth:         $(json_val "${RESULTS_DIR}/test-1-results.json" "nonsense_propagation_depth") / 8"
    echo "  Validation blocking:       $(json_val "${RESULTS_DIR}/test-1-results.json" "validation_blocking_count")"
else
    echo "  (not yet run)"
fi
echo ""

echo "TEST 2: Adversarial Conclusion Preservation"
echo "-------------------------------------------"
if [ -f "${RESULTS_DIR}/test-2-results.json" ]; then
    echo "  Preservation rate:         $(json_val "${RESULTS_DIR}/test-2-results.json" "preservation_rate_pct")%"
    echo "  Markers total:             $(json_val "${RESULTS_DIR}/test-2-results.json" "debate_content_markers_total")"
    echo "  Markers found in merged:   $(json_val "${RESULTS_DIR}/test-2-results.json" "debate_markers_in_merged")"
    echo "  Markers missing:           $(json_val "${RESULTS_DIR}/test-2-results.json" "debate_markers_missing")"
    echo "  Target: >=95% (SC-002)"
else
    echo "  (not yet run)"
fi
echo ""

echo "TEST 3: Cross-Boundary Information Cascade"
echo "-------------------------------------------"
if [ -f "${RESULTS_DIR}/test-3-results.json" ]; then
    echo "  (See full results in test-3-results.json for per-stage breakdown)"
    echo "  Pipeline exit:             $(json_val "${RESULTS_DIR}/test-3-results.json" "pipeline_exit_code")"
    echo "  Elapsed:                   $(json_val "${RESULTS_DIR}/test-3-results.json" "elapsed_seconds")s"
else
    echo "  (not yet run)"
fi
echo ""

echo "TEST 4: Multi-Agent Validation Depth"
echo "-------------------------------------------"
if [ -f "${RESULTS_DIR}/test-4-results.json" ]; then
    echo "  Single-agent blocking:     $(json_val "${RESULTS_DIR}/test-4-results.json" "blocking_issues" | head -1)"
    echo "  Multi-agent blocking:      $(json_val "${RESULTS_DIR}/test-4-results.json" "blocking_issues" | tail -1)"
    echo "  Blocking delta:            $(json_val "${RESULTS_DIR}/test-4-results.json" "blocking_delta")"
else
    echo "  (not yet run)"
fi
echo ""

echo "TEST 5: Gate False-Negative Stress Test"
echo "-------------------------------------------"
if [ -f "${RESULTS_DIR}/test-5-results.json" ]; then
    echo "  Detected:                  $(json_val "${RESULTS_DIR}/test-5-results.json" "detected") / 7"
    echo "  Missed:                    $(json_val "${RESULTS_DIR}/test-5-results.json" "missed")"
    echo "  Detection rate:            $(json_val "${RESULTS_DIR}/test-5-results.json" "detection_rate_pct")%"
    echo "  Target: 7/7 (100%)"
else
    echo "  (not yet run)"
fi
echo ""

echo "=================================================================="
echo "KEY METRICS FOR SPRINT COMPARISON"
echo "=================================================================="
echo ""
echo "| Metric                          | Baseline | Target  | Sprint Finding |"
echo "|---------------------------------|----------|---------|----------------|"
echo "| Nonsense gate penetration       | TBD      | 0/8     | F-001          |"
echo "| Adversarial preservation        | TBD      | >=95%   | F-003, SC-002  |"
echo "| Info cascade (req ID loss)      | TBD      | <10%    | F-006          |"
echo "| Validation semantic ratio       | TBD      | >50%    | F-001, F-002   |"
echo "| Gate corruption detection       | TBD      | 7/7     | F-001          |"
echo ""
echo "Fill in 'Baseline' after running all 5 tests pre-release."
echo "Fill in actual post-release values after implementing v2.20."
echo "=================================================================="
