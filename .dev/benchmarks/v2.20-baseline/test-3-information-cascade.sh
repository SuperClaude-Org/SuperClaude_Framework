#!/usr/bin/env bash
# =============================================================================
# TEST 3: Cross-Boundary Information Cascade Test
# =============================================================================
# Finding: F-006 — "Seam Failures Are a Primary Failure Habitat"
# Evidence Chain 2 — "Schema drift through passing gates"
# Evidence Chain 5 — "Spec-to-implementation drift without detection"
#
# WHAT THIS TESTS:
# The forensic diagnostic identified inter-stage boundaries where information
# degrades silently while gates keep reporting PASS. This test runs a complex
# spec through the full pipeline and measures information density at each stage.
#
# METHOD:
# 1. Run the real pipeline on a complex, requirement-dense spec
# 2. For each output artifact, measure:
#    - Requirement ID count (FR-xxx, NFR-xxx references)
#    - Constraint density (words like "must", "shall", "required")
#    - Unique technical terms
#    - Section/heading count
#    - Total word count
# 3. Compare adjacent stages to detect seam-level information loss
#
# EXPECTED BASELINE (pre-v2.20):
# - Steady information loss at each boundary
# - Requirement IDs progressively drop out
# - Final test-strategy has significantly fewer constraints than extraction
# - All gates still PASS despite information loss
#
# POST-v2.20 EXPECTED:
# - Seam gates detect information loss
# - Schema drift flagged when contract thins
# - Higher requirement preservation in merged output
#
# METRICS CAPTURED:
# - Per-stage: word_count, requirement_ids, constraint_words, unique_terms,
#              heading_count, bullet_count
# - Cross-stage: preservation_ratio at each boundary
# - Overall: end_to_end_information_loss
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
cd "$REPO_ROOT"

BENCHMARK_DIR="${REPO_ROOT}/.dev/benchmarks/v2.20-baseline"
RESULTS_DIR="${BENCHMARK_DIR}/results"
OUTPUT_DIR="${BENCHMARK_DIR}/outputs/test-3-cascade"
SPEC_FILE="${REPO_ROOT}/.dev/releases/complete/v2.0-roadmap-v2/SC-ROADMAP-V2-SPEC.md"
RESULTS_FILE="${RESULTS_DIR}/test-3-results.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

mkdir -p "$RESULTS_DIR" "$OUTPUT_DIR"

if [ ! -f "$SPEC_FILE" ]; then
    echo "ERROR: Spec file not found: $SPEC_FILE" >&2
    exit 1
fi

echo "=================================================================="
echo "TEST 3: Cross-Boundary Information Cascade Test"
echo "=================================================================="
echo "Spec: ${SPEC_FILE}"
echo "Output: ${OUTPUT_DIR}"
echo "Started: ${TIMESTAMP}"
echo ""
echo "This test measures information density at each pipeline stage to"
echo "detect silent schema drift and constraint degradation across seams."
echo ""

# Clean previous outputs but preserve benchmark root
rm -rf "${OUTPUT_DIR:?}"/*

# Run the full pipeline
# Keep the benchmark real-world: invoke the actual roadmap pipeline, not tests.
echo ">>> Running pipeline: superclaude roadmap run ..."
START_TIME=$(date +%s)

set +e
superclaude roadmap run "$SPEC_FILE" \
    --output "$OUTPUT_DIR" \
    --agents "opus:architect,haiku:analyst" \
    --depth standard \
    --debug 2>&1 | tee "${OUTPUT_DIR}/pipeline-stdout.log"
PIPELINE_EXIT=${PIPESTATUS[0]}
set -e

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo ">>> Pipeline completed with exit code: ${PIPELINE_EXIT}"
echo ">>> Elapsed time: ${ELAPSED}s"
echo ""

# ---- INFORMATION DENSITY ANALYSIS ----

echo ">>> Measuring information density at each stage..."

json_field() {
    local json="$1"
    local key="$2"
    local value

    value=$(printf '%s\n' "$json" | sed -nE "s/.*\"${key}\":[[:space:]]*\"?([^\",}]+)\"?.*/\1/p" | head -n 1)
    printf '%s' "${value:-}"
}

safe_ratio() {
    local numerator="$1"
    local denominator="$2"

    if [ "$denominator" -eq 0 ]; then
        if [ "$numerator" -eq 0 ]; then
            printf '1.0000'
        else
            printf '0.0000'
        fi
        return
    fi

    awk -v n="$numerator" -v d="$denominator" 'BEGIN { printf "%.4f", n / d }'
}

find_generated_variant() {
    local preferred="$1"
    local fallback_glob="$2"

    if [ -f "$preferred" ]; then
        printf '%s\n' "$preferred"
        return
    fi

    local fallback
    fallback=$(compgen -G "$fallback_glob" | head -n 1 || true)
    printf '%s\n' "${fallback:-}"
}

analyze_file() {
    local file="$1"
    local stage_name="$2"

    if [ -z "$file" ] || [ ! -f "$file" ]; then
        echo "{\"stage\": \"${stage_name}\", \"status\": \"missing\"}"
        return
    fi

    local word_count
    word_count=$(wc -w < "$file" 2>/dev/null || printf '0')

    local line_count
    line_count=$(wc -l < "$file" 2>/dev/null || printf '0')

    # Requirement IDs: support 1+ digits to avoid undercounting larger sets.
    local req_ids
    req_ids=$(grep -oiE '\b(FR|NFR|SC|AC|R|DEP|OQ)-[0-9]{1,}\b' "$file" 2>/dev/null | sort -u | wc -l | tr -d ' ')

    # Constraint words: count occurrences, not lines, for denser artifacts.
    local constraints
    constraints=$(grep -oiE '\b(must|shall|required|mandatory|critical|ensure|enforce|guarantee)\b' "$file" 2>/dev/null | wc -l | tr -d ' ')

    local headings
    headings=$(grep -cE '^#{1,6}[[:space:]]' "$file" 2>/dev/null || printf '0')

    local bullets
    bullets=$(grep -cE '^[[:space:]]*[-*][[:space:]]|^[[:space:]]*[0-9]+\.[[:space:]]' "$file" 2>/dev/null || printf '0')

    local unique_terms
    unique_terms=$(tr -cs '[:alnum:]_-' '\n' < "$file" 2>/dev/null | \
        grep -E '^[[:alnum:]_-]{4,}$' | \
        grep -viE '^(this|that|with|from|have|will|would|should|could|been|were|also|each|into|than|them|then|when|more|some|only|over|such|after|before|these|those|other|about|which|their|there|first|where|being|still|under|never|every|since|until|while|using|through|between|without|during|against|within|around)$' | \
        sort -u | wc -l | tr -d ' ')

    local fm_fields=0
    if grep -q '^---$' "$file" 2>/dev/null; then
        fm_fields=$(sed -n '/^---$/,/^---$/p' "$file" 2>/dev/null | grep -cE '^[A-Za-z0-9_-]+:' || printf '0')
    fi

    echo "{\"stage\": \"${stage_name}\", \"file\": \"${file}\", \"word_count\": ${word_count}, \"line_count\": ${line_count}, \"requirement_ids\": ${req_ids}, \"constraint_words\": ${constraints}, \"headings\": ${headings}, \"bullets\": ${bullets}, \"unique_terms\": ${unique_terms}, \"frontmatter_fields\": ${fm_fields}}"
}

build_boundary_metrics() {
    local from_json="$1"
    local to_json="$2"
    local boundary_name="$3"

    local from_stage to_stage from_status to_status
    from_stage=$(json_field "$from_json" "stage")
    to_stage=$(json_field "$to_json" "stage")
    from_status=$(json_field "$from_json" "status")
    to_status=$(json_field "$to_json" "status")

    if [ -n "$from_status" ] || [ -n "$to_status" ]; then
        echo "{\"boundary\": \"${boundary_name}\", \"from_stage\": \"${from_stage}\", \"to_stage\": \"${to_stage}\", \"status\": \"missing-stage\"}"
        return
    fi

    local from_words to_words from_reqs to_reqs from_constraints to_constraints from_terms to_terms
    from_words=$(json_field "$from_json" "word_count")
    to_words=$(json_field "$to_json" "word_count")
    from_reqs=$(json_field "$from_json" "requirement_ids")
    to_reqs=$(json_field "$to_json" "requirement_ids")
    from_constraints=$(json_field "$from_json" "constraint_words")
    to_constraints=$(json_field "$to_json" "constraint_words")
    from_terms=$(json_field "$from_json" "unique_terms")
    to_terms=$(json_field "$to_json" "unique_terms")

    local word_ratio req_ratio constraint_ratio term_ratio
    word_ratio=$(safe_ratio "$to_words" "$from_words")
    req_ratio=$(safe_ratio "$to_reqs" "$from_reqs")
    constraint_ratio=$(safe_ratio "$to_constraints" "$from_constraints")
    term_ratio=$(safe_ratio "$to_terms" "$from_terms")

    echo "{\"boundary\": \"${boundary_name}\", \"from_stage\": \"${from_stage}\", \"to_stage\": \"${to_stage}\", \"word_preservation_ratio\": ${word_ratio}, \"requirement_preservation_ratio\": ${req_ratio}, \"constraint_preservation_ratio\": ${constraint_ratio}, \"term_preservation_ratio\": ${term_ratio}}"
}

# Analyze the input spec first
echo "  Analyzing input spec..."
SPEC_METRICS=$(analyze_file "$SPEC_FILE" "input-spec")

# Analyze each pipeline stage output
echo "  Analyzing pipeline outputs..."

VARIANT_A=$(find_generated_variant "${OUTPUT_DIR}/roadmap-opus.md" "${OUTPUT_DIR}/roadmap-opus*.md")
VARIANT_B=$(find_generated_variant "${OUTPUT_DIR}/roadmap-haiku.md" "${OUTPUT_DIR}/roadmap-haiku*.md")
VALIDATION_FILE="${OUTPUT_DIR}/validate/validation-report.md"

EXTRACT_METRICS=$(analyze_file "${OUTPUT_DIR}/extraction.md" "extract")
GENERATE_A_METRICS=$(analyze_file "$VARIANT_A" "generate-opus")
GENERATE_B_METRICS=$(analyze_file "$VARIANT_B" "generate-haiku")
DIFF_METRICS=$(analyze_file "${OUTPUT_DIR}/diff-analysis.md" "diff")
DEBATE_METRICS=$(analyze_file "${OUTPUT_DIR}/debate-transcript.md" "debate")
SCORE_METRICS=$(analyze_file "${OUTPUT_DIR}/base-selection.md" "score")
MERGE_METRICS=$(analyze_file "${OUTPUT_DIR}/roadmap.md" "merge")
TEST_STRAT_METRICS=$(analyze_file "${OUTPUT_DIR}/test-strategy.md" "test-strategy")

VALIDATE_METRICS='{"stage": "validate", "status": "not-run"}'
if [ -f "$VALIDATION_FILE" ]; then
    VALIDATE_METRICS=$(analyze_file "$VALIDATION_FILE" "validate")
fi

SPEC_TO_EXTRACT=$(build_boundary_metrics "$SPEC_METRICS" "$EXTRACT_METRICS" "spec-to-extract")
EXTRACT_TO_GENERATE_OPUS=$(build_boundary_metrics "$EXTRACT_METRICS" "$GENERATE_A_METRICS" "extract-to-generate-opus")
EXTRACT_TO_GENERATE_HAIKU=$(build_boundary_metrics "$EXTRACT_METRICS" "$GENERATE_B_METRICS" "extract-to-generate-haiku")
GENERATE_OPUS_TO_DIFF=$(build_boundary_metrics "$GENERATE_A_METRICS" "$DIFF_METRICS" "generate-opus-to-diff")
GENERATE_HAIKU_TO_DIFF=$(build_boundary_metrics "$GENERATE_B_METRICS" "$DIFF_METRICS" "generate-haiku-to-diff")
DIFF_TO_DEBATE=$(build_boundary_metrics "$DIFF_METRICS" "$DEBATE_METRICS" "diff-to-debate")
DEBATE_TO_SCORE=$(build_boundary_metrics "$DEBATE_METRICS" "$SCORE_METRICS" "debate-to-score")
SCORE_TO_MERGE=$(build_boundary_metrics "$SCORE_METRICS" "$MERGE_METRICS" "score-to-merge")
MERGE_TO_TEST_STRATEGY=$(build_boundary_metrics "$MERGE_METRICS" "$TEST_STRAT_METRICS" "merge-to-test-strategy")
END_TO_END=$(build_boundary_metrics "$SPEC_METRICS" "$TEST_STRAT_METRICS" "spec-to-test-strategy")

# ---- WRITE RESULTS ----

cat > "$RESULTS_FILE" <<JSONEOF
{
  "test_id": "test-3-information-cascade",
  "test_version": "v2.20-baseline",
  "timestamp": "${TIMESTAMP}",
  "findings_targeted": ["F-006", "Evidence-Chain-2", "Evidence-Chain-5"],
  "spec_file": "${SPEC_FILE}",
  "pipeline_exit_code": ${PIPELINE_EXIT},
  "elapsed_seconds": ${ELAPSED},
  "stages": [
    ${SPEC_METRICS},
    ${EXTRACT_METRICS},
    ${GENERATE_A_METRICS},
    ${GENERATE_B_METRICS},
    ${DIFF_METRICS},
    ${DEBATE_METRICS},
    ${SCORE_METRICS},
    ${MERGE_METRICS},
    ${TEST_STRAT_METRICS},
    ${VALIDATE_METRICS}
  ],
  "boundaries": [
    ${SPEC_TO_EXTRACT},
    ${EXTRACT_TO_GENERATE_OPUS},
    ${EXTRACT_TO_GENERATE_HAIKU},
    ${GENERATE_OPUS_TO_DIFF},
    ${GENERATE_HAIKU_TO_DIFF},
    ${DIFF_TO_DEBATE},
    ${DEBATE_TO_SCORE},
    ${SCORE_TO_MERGE},
    ${MERGE_TO_TEST_STRATEGY},
    ${END_TO_END}
  ],
  "interpretation": {
    "what_to_look_for": [
      "Requirement IDs should survive across spec→extract→merge and not collapse in merge→test-strategy.",
      "Constraint preservation drops indicate seam-level contract thinning, especially extract→generate and merge→test-strategy.",
      "Diff/debate/score stages are expected to transform content shape, but severe requirement or constraint loss still signals seam failure.",
      "If merge has fewer requirement IDs than extract, schema drift through passing gates is present (Evidence Chain 2).",
      "If test-strategy loses substantial requirements or constraints relative to merge, spec-to-implementation drift is present (Evidence Chain 5)."
    ],
    "baseline_expectation": "Progressive information loss at multiple boundaries with all gates still passing.",
    "target": "Seam gates detect and flag significant information drops before drift reaches merged roadmap or test strategy."
  }
}
JSONEOF

# ---- DISPLAY RESULTS ----

echo ""
echo "=================================================================="
echo "TEST 3 RESULTS — Information Density Cascade"
echo "=================================================================="
echo "Pipeline exit code: ${PIPELINE_EXIT}"
echo "Elapsed time: ${ELAPSED}s"
echo ""
printf "%-20s %8s %8s %10s %8s %8s\n" "STAGE" "WORDS" "REQ_IDS" "CONSTR" "HEADS" "BULLETS"
printf "%-20s %8s %8s %10s %8s %8s\n" "====================" "======" "=======" "======" "=====" "======="

for metrics_var in SPEC_METRICS EXTRACT_METRICS GENERATE_A_METRICS GENERATE_B_METRICS DIFF_METRICS DEBATE_METRICS SCORE_METRICS MERGE_METRICS TEST_STRAT_METRICS VALIDATE_METRICS; do
    metrics="${!metrics_var}"
    stage=$(json_field "$metrics" "stage")
    status=$(json_field "$metrics" "status")

    if [ "$status" = "missing" ] || [ "$status" = "not-run" ]; then
        printf "%-20s %8s\n" "$stage" "($status)"
        continue
    fi

    words=$(json_field "$metrics" "word_count")
    reqs=$(json_field "$metrics" "requirement_ids")
    constr=$(json_field "$metrics" "constraint_words")
    heads=$(json_field "$metrics" "headings")
    bullets=$(json_field "$metrics" "bullets")

    printf "%-20s %8s %8s %10s %8s %8s\n" "$stage" "$words" "$reqs" "$constr" "$heads" "$bullets"
done

echo ""
echo "BOUNDARY PRESERVATION RATIOS:"
for boundary_var in SPEC_TO_EXTRACT EXTRACT_TO_GENERATE_OPUS EXTRACT_TO_GENERATE_HAIKU GENERATE_OPUS_TO_DIFF GENERATE_HAIKU_TO_DIFF DIFF_TO_DEBATE DEBATE_TO_SCORE SCORE_TO_MERGE MERGE_TO_TEST_STRATEGY END_TO_END; do
    boundary_json="${!boundary_var}"
    boundary_name=$(json_field "$boundary_json" "boundary")
    status=$(json_field "$boundary_json" "status")

    if [ "$status" = "missing-stage" ]; then
        printf "  %-28s %s\n" "$boundary_name" "missing-stage"
        continue
    fi

    req_ratio=$(json_field "$boundary_json" "requirement_preservation_ratio")
    constraint_ratio=$(json_field "$boundary_json" "constraint_preservation_ratio")
    term_ratio=$(json_field "$boundary_json" "term_preservation_ratio")
    printf "  %-28s req=%s constr=%s terms=%s\n" "$boundary_name" "$req_ratio" "$constraint_ratio" "$term_ratio"
done

echo ""
echo "INTERPRETATION:"
echo "  Look for large drops between adjacent stages, especially extract→generate, score→merge, and merge→test-strategy."
echo "  Pre-v2.20: expect steady decline with zero gate failures despite drift."
echo "  Post-v2.20: expect seam gates to flag drops above threshold."
echo ""
echo "Results saved to: ${RESULTS_FILE}"
echo "=================================================================="
