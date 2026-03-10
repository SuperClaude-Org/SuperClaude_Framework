#!/usr/bin/env bash
# =============================================================================
# TEST 1: Semantic Nonsense Gate Penetration Test
# =============================================================================
# Finding: F-001 — "Structural Validation Is Systematically Mistaken for
#                    Semantic Correctness"
# Success Criteria: SC-007 — "Gate functions can fail on semantically invalid
#                              but structurally correct inputs"
#
# WHAT THIS TESTS:
# The forensic diagnostic found that gates check structure (file exists,
# non-empty, min lines, frontmatter keys, heading hierarchy) but NOT semantic
# validity. This test feeds a well-structured but completely nonsensical spec
# through the full pipeline and measures how far it gets.
#
# EXPECTED BASELINE BEHAVIOR (pre-v2.20):
# - Core pipeline stages complete on structurally valid nonsense
# - A merged roadmap is produced for impossible requirements
# - Validation may report issues, but too late to stop nonsense propagation
#
# POST-v2.20 EXPECTED BEHAVIOR:
# - Semantic gates should stop or materially degrade pipeline completion
# - Contract-based validation should flag blocking issues
# - Nonsensical content should not survive cleanly into roadmap.md
#
# METRICS CAPTURED:
# - gate_pass_signals: Pass-like strings observed in debug/stdout (signal only)
# - gate_fail_signals: Fail-like strings observed in debug/stdout (signal only)
# - files_produced: How many expected core pipeline artifacts were produced
# - validation_blocking_count: Blocking issues found by validation, if present
# - nonsense_propagation_depth: First missing core artifact stage (1-8, or 9=none)
# - output_contains_nonsense: Whether final roadmap contains absurd terms
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
BENCHMARK_DIR="${REPO_ROOT}/.dev/benchmarks/v2.20-baseline"
RESULTS_DIR="${BENCHMARK_DIR}/results"
OUTPUT_DIR="${BENCHMARK_DIR}/outputs/test-1-nonsense"
SPEC_FILE="${BENCHMARK_DIR}/fixtures/nonsense-spec.md"
RESULTS_FILE="${RESULTS_DIR}/test-1-results.json"
PIPELINE_LOG="${OUTPUT_DIR}/pipeline-stdout.log"
VALIDATION_REPORT="${OUTPUT_DIR}/validate/validation-report.md"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

EXPECTED_OUTPUTS=(
    "extraction.md"
    "roadmap-opus-architect.md"
    "roadmap-haiku-analyst.md"
    "diff-analysis.md"
    "debate-transcript.md"
    "base-selection.md"
    "roadmap.md"
    "test-strategy.md"
)

NONSENSE_TERMS=(
    "quantum banana"
    "telepathic"
    "parallel universe"
    "astral plane"
    "aura color"
    "interpretive dance"
    "Heisenberg coefficient"
    "cosmic validator"
)

mkdir -p "$RESULTS_DIR" "$OUTPUT_DIR"

if ! command -v superclaude >/dev/null 2>&1; then
    printf 'ERROR: superclaude command not found in PATH\n' >&2
    exit 1
fi

if [ ! -f "$SPEC_FILE" ]; then
    printf 'ERROR: benchmark fixture missing: %s\n' "$SPEC_FILE" >&2
    exit 1
fi

cd "$REPO_ROOT"

echo "=================================================================="
echo "TEST 1: Semantic Nonsense Gate Penetration Test"
echo "=================================================================="
echo "Spec: ${SPEC_FILE}"
echo "Output: ${OUTPUT_DIR}"
echo "Started: ${TIMESTAMP}"
echo ""
echo "This test feeds a structurally valid but semantically absurd spec"
echo "through the full roadmap pipeline. Pre-v2.20, we expect structure-only"
echo "gates to let nonsense propagate deep into the run."
echo ""

# Clean previous outputs, including hidden state such as .roadmap-state.json
shopt -s nullglob dotglob
rm -rf "${OUTPUT_DIR:?}"/*
shopt -u nullglob dotglob

# Run the full pipeline and preserve the real exit code even with tee/pipefail
# roadmap run auto-invokes validation unless explicitly disabled.
echo ">>> Running pipeline: superclaude roadmap run ..."
START_TIME=$(date +%s)

set +e
superclaude roadmap run "$SPEC_FILE" \
    --output "$OUTPUT_DIR" \
    --agents "opus:architect,haiku:analyst" \
    --depth standard \
    --debug 2>&1 | tee "$PIPELINE_LOG"
PIPELINE_EXIT=${PIPESTATUS[0]}
set -e

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo ">>> Pipeline completed with exit code: ${PIPELINE_EXIT}"
echo ">>> Elapsed time: ${ELAPSED}s"
echo ""

# ---- METRIC COLLECTION ----

echo ">>> Collecting metrics..."

# Count pass/fail signals from stdout. These are heuristic signals, not authoritative gate counts.
GATE_PASS=$(grep -Eci '\bgate\b.*\bpass(ed|es)?\b|\bPASS\b' "$PIPELINE_LOG" 2>/dev/null || true)
GATE_FAIL=$(grep -Eci '\bgate\b.*\bfail(ed|s)?\b|\bFAIL\b|\bhalt(ed)?\b' "$PIPELINE_LOG" 2>/dev/null || true)
GATE_PASS=${GATE_PASS:-0}
GATE_FAIL=${GATE_FAIL:-0}

# Count expected core outputs. This is the primary completion metric for F-001 / SC-007.
FILES_PRODUCED=0
for output_name in "${EXPECTED_OUTPUTS[@]}"; do
    if [ -f "${OUTPUT_DIR}/${output_name}" ]; then
        FILES_PRODUCED=$((FILES_PRODUCED + 1))
    fi
done
EXPECTED_FILE_COUNT=${#EXPECTED_OUTPUTS[@]}

# Check validation results if auto-validation ran
BLOCKING_COUNT=0
WARNING_COUNT=0
VALIDATION_REPORT_PRESENT=false
if [ -f "$VALIDATION_REPORT" ]; then
    VALIDATION_REPORT_PRESENT=true
    BLOCKING_COUNT=$(grep -oP 'blocking_issues_count:\s*\K\d+' "$VALIDATION_REPORT" 2>/dev/null || true)
    WARNING_COUNT=$(grep -oP 'warnings_count:\s*\K\d+' "$VALIDATION_REPORT" 2>/dev/null || true)
    BLOCKING_COUNT=${BLOCKING_COUNT:-0}
    WARNING_COUNT=${WARNING_COUNT:-0}
fi

# Check for nonsense terms in final roadmap
NONSENSE_HITS=0
MERGED_ROADMAP="${OUTPUT_DIR}/roadmap.md"
if [ -f "$MERGED_ROADMAP" ]; then
    for term in "${NONSENSE_TERMS[@]}"; do
        if grep -Fqi "$term" "$MERGED_ROADMAP" 2>/dev/null; then
            NONSENSE_HITS=$((NONSENSE_HITS + 1))
        fi
    done
fi

# Determine propagation depth: first missing expected core artifact.
# 1-8 = first missing stage artifact, 9 = all expected artifacts exist.
PROPAGATION_DEPTH=$((EXPECTED_FILE_COUNT + 1))
for i in "${!EXPECTED_OUTPUTS[@]}"; do
    if [ ! -f "${OUTPUT_DIR}/${EXPECTED_OUTPUTS[$i]}" ]; then
        PROPAGATION_DEPTH=$((i + 1))
        break
    fi
done

# Derived rates kept numeric for easier comparison across runs.
FILE_COMPLETION_RATE_PCT=$((FILES_PRODUCED * 100 / EXPECTED_FILE_COUNT))
NONSENSE_SURVIVAL_RATE_PCT=$((NONSENSE_HITS * 100 / ${#NONSENSE_TERMS[@]}))

# ---- WRITE RESULTS ----

cat > "$RESULTS_FILE" <<JSONEOF
{
    "test_id": "test-1-nonsense-penetration",
    "test_version": "v2.20-baseline",
    "timestamp": "${TIMESTAMP}",
    "findings_targeted": ["F-001", "SC-007"],
    "spec_file": "${SPEC_FILE}",
    "pipeline_exit_code": ${PIPELINE_EXIT},
    "elapsed_seconds": ${ELAPSED},
    "metrics": {
        "gate_pass_signals": ${GATE_PASS},
        "gate_fail_signals": ${GATE_FAIL},
        "files_produced": ${FILES_PRODUCED},
        "expected_files": ${EXPECTED_FILE_COUNT},
        "file_completion_rate_pct": ${FILE_COMPLETION_RATE_PCT},
        "validation_report_present": ${VALIDATION_REPORT_PRESENT},
        "validation_blocking_count": ${BLOCKING_COUNT},
        "validation_warning_count": ${WARNING_COUNT},
        "nonsense_propagation_depth": ${PROPAGATION_DEPTH},
        "nonsense_terms_in_final_roadmap": ${NONSENSE_HITS},
        "nonsense_terms_checked": ${#NONSENSE_TERMS[@]},
        "nonsense_survival_rate_pct": ${NONSENSE_SURVIVAL_RATE_PCT}
    },
    "interpretation": {
        "primary_signal": "High files_produced plus nonsense in roadmap.md indicates semantic nonsense penetrated structure-only gates.",
        "secondary_signal": "validation_blocking_count > 0 with roadmap.md still produced means validation noticed issues after propagation, not before.",
        "propagation_scale": "1-8 = first missing expected core artifact, 9 = all expected core artifacts produced"
    }
}
JSONEOF

echo ""
echo "=================================================================="
echo "TEST 1 RESULTS"
echo "=================================================================="
echo "Pipeline exit code:          ${PIPELINE_EXIT}"
echo "Files produced:              ${FILES_PRODUCED} / ${EXPECTED_FILE_COUNT} expected"
echo "Core completion rate:        ${FILE_COMPLETION_RATE_PCT}%"
echo "Gate pass signals:           ${GATE_PASS}"
echo "Gate fail signals:           ${GATE_FAIL}"
echo "Validation report present:   ${VALIDATION_REPORT_PRESENT}"
echo "Validation blocking issues:  ${BLOCKING_COUNT}"
echo "Validation warnings:         ${WARNING_COUNT}"
echo "Nonsense propagation depth:  ${PROPAGATION_DEPTH}"
echo "Nonsense terms in final:     ${NONSENSE_HITS} / ${#NONSENSE_TERMS[@]} (${NONSENSE_SURVIVAL_RATE_PCT}%)"
echo ""
echo "INTERPRETATION:"
if [ "$FILES_PRODUCED" -eq "$EXPECTED_FILE_COUNT" ] && [ "$NONSENSE_HITS" -gt 0 ]; then
    echo "  >> BASELINE CONFIRMED: Structurally valid nonsense completed the core pipeline"
    echo "     and survived into roadmap.md. This supports F-001 and shows SC-007 is unmet."
    if [ "$BLOCKING_COUNT" -gt 0 ]; then
        echo "     Validation noticed issues, but only after nonsense had already propagated."
    fi
elif [ "$PROPAGATION_DEPTH" -le "$EXPECTED_FILE_COUNT" ]; then
    echo "  >> PIPELINE STOPPED EARLY: First missing expected artifact at stage ${PROPAGATION_DEPTH}."
    echo "     This may indicate stronger semantic resistance, or an unrelated execution failure."
    echo "     Review ${PIPELINE_LOG} and any *.err files in ${OUTPUT_DIR}."
else
    echo "  >> INCONCLUSIVE: No nonsense reached roadmap.md, but the pipeline did not clearly"
    echo "     demonstrate whether semantics were rejected or content was transformed away."
fi
echo ""
echo "Results saved to: ${RESULTS_FILE}"
echo "=================================================================="
