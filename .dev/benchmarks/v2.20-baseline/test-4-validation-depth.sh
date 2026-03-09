#!/usr/bin/env bash
# =============================================================================
# TEST 4: Multi-Agent Validation Depth Test
# =============================================================================
# Finding: F-001 — "Structural Validation Is Systematically Mistaken for
#                    Semantic Correctness"
# Finding: F-002 — "Confidence Inflates Across Stages Through Proxy Stacking"
# Validate Pipeline — Tests the validation stage's actual detection capability
#
# WHAT THIS TESTS:
# The validation stage (roadmap validate) asks the LLM to perform deep semantic
# checks (schema, structure, traceability, cross-file consistency, parseability,
# interleave, decomposition). But the GATE on the validation report only checks
# that the REPORT is structurally valid — not that it found real issues.
#
# This test uses a COMPLETED pipeline run (from Test 3 or a previous release)
# and runs validation in BOTH modes:
#   a) Single-agent validation (default for standalone)
#   b) Multi-agent adversarial validation (2 agents)
# Then compares: do the two modes find the same issues? Different issues?
# Are the findings meaningful or just well-formatted?
#
# METHOD:
# 1. Use output from a completed pipeline run as validation input
# 2. Run single-agent validation
# 3. Run multi-agent validation (2 agents)
# 4. Compare findings between modes
# 5. Score finding quality (real vs. structural-only)
#
# EXPECTED BASELINE (pre-v2.20):
# - Both modes produce well-formatted reports
# - Finding counts may differ between modes
# - Most findings are structural, not semantic
# - REFLECT_GATE is STANDARD tier, so its semantic checks don't run
#
# POST-v2.20 EXPECTED:
# - Upgraded gates catch more real issues
# - Semantic findings increase
# - Multi-agent mode exposes issues single-agent misses
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
cd "$REPO_ROOT"

BENCHMARK_DIR="${REPO_ROOT}/.dev/benchmarks/v2.20-baseline"
RESULTS_DIR="${BENCHMARK_DIR}/results"
OUTPUT_DIR="${BENCHMARK_DIR}/outputs/test-4-validation"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REQUIRED_INPUTS=(roadmap.md test-strategy.md extraction.md)

log() {
    printf '%s\n' "$*"
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

have_required_inputs() {
    local dir="$1"
    local file

    for file in "${REQUIRED_INPUTS[@]}"; do
        if [ ! -f "${dir}/${file}" ]; then
            return 1
        fi
    done

    return 0
}

select_source_dir() {
    local candidate

    for candidate in \
        "${BENCHMARK_DIR}/outputs/test-3-cascade" \
        "${REPO_ROOT}/.dev/releases/complete/v2.19-roadmap-validate"
    do
        if have_required_inputs "$candidate"; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    return 1
}

prepare_input_dir() {
    local target_dir="$1"
    local file

    rm -rf "$target_dir"
    mkdir -p "$target_dir"

    for file in "${REQUIRED_INPUTS[@]}"; do
        cp "${SOURCE_DIR}/${file}" "${target_dir}/${file}"
    done
}

run_validation() {
    local target_dir="$1"
    local agents="$2"
    local log_file="$3"
    local exit_code=0

    set +e
    superclaude roadmap validate "$target_dir" \
        --agents "$agents" \
        --debug 2>&1 | tee "$log_file"
    exit_code=${PIPESTATUS[0]}
    set -e

    return "$exit_code"
}

frontmatter_number() {
    local file="$1"
    local key="$2"

    awk -F': *' -v key="$key" '
        BEGIN { in_frontmatter = 0 }
        NR == 1 && $0 == "---" { in_frontmatter = 1; next }
        in_frontmatter && $0 == "---" { exit }
        in_frontmatter && $1 == key {
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2)
            print $2
            exit
        }
    ' "$file"
}

frontmatter_value() {
    local file="$1"
    local key="$2"

    awk -F': *' -v key="$key" '
        BEGIN { in_frontmatter = 0 }
        NR == 1 && $0 == "---" { in_frontmatter = 1; next }
        in_frontmatter && $0 == "---" { exit }
        in_frontmatter && $1 == key {
            sub(/^[^:]*:[[:space:]]*/, "")
            gsub(/^[[:space:]]+|[[:space:]]+$/, "")
            gsub(/^"|"$/, "")
            gsub(/^'"'"'|'"'"'$/, "")
            print $0
            exit
        }
    ' "$file"
}

count_matches() {
    local pattern="$1"
    local file="$2"

    grep -cE "$pattern" "$file" 2>/dev/null || true
}

compute_ratio() {
    local numerator="$1"
    local denominator="$2"

    if [ "$denominator" -le 0 ]; then
        printf '0.00\n'
    else
        awk -v n="$numerator" -v d="$denominator" 'BEGIN { printf "%.2f\n", n / d }'
    fi
}

resolve_report_path() {
    local validate_dir="$1"

    if [ -f "${validate_dir}/merged-validation-report.md" ]; then
        printf '%s\n' "${validate_dir}/merged-validation-report.md"
    elif [ -f "${validate_dir}/validation-report.md" ]; then
        printf '%s\n' "${validate_dir}/validation-report.md"
    else
        printf '%s\n' "${validate_dir}/validation-report.md"
    fi
}

analyze_report() {
    local report="$1"

    if [ ! -f "$report" ]; then
        printf '0|0|0|0|0|0|0|false\n'
        return 0
    fi

    local blocking warnings info_count total_findings structural_findings semantic_findings word_count validation_complete

    blocking="$(frontmatter_number "$report" "blocking_issues_count")"
    warnings="$(frontmatter_number "$report" "warnings_count")"
    validation_complete="$(frontmatter_value "$report" "validation_complete")"

    blocking="${blocking:-0}"
    warnings="${warnings:-0}"
    validation_complete="${validation_complete:-true}"

    info_count=$(count_matches '^[[:space:]]*-[[:space:]]+\*\*\[INFO\]' "$report")
    total_findings=$(count_matches '^[[:space:]]*-[[:space:]]+\*\*\[(BLOCKING|WARNING|INFO)\]' "$report")
    structural_findings=$(count_matches '^[[:space:]]*-[[:space:]]+\*\*\[(BLOCKING|WARNING|INFO)\][[:space:]]+(Schema|Structure|Parseability):' "$report")
    semantic_findings=$(count_matches '^[[:space:]]*-[[:space:]]+\*\*\[(BLOCKING|WARNING|INFO)\][[:space:]]+(Traceability|Cross-file consistency|Consistency|Requirement|Semantic|Decomposition):' "$report")
    word_count=$(wc -w < "$report")

    printf '%s|%s|%s|%s|%s|%s|%s|%s\n' \
        "$blocking" \
        "$warnings" \
        "$info_count" \
        "$total_findings" \
        "$structural_findings" \
        "$semantic_findings" \
        "$word_count" \
        "$validation_complete"
}

count_agreement_category() {
    local report="$1"
    local category="$2"

    if [ ! -f "$report" ]; then
        printf '0\n'
        return 0
    fi

    grep -cE "\|[[:space:]]*${category}[[:space:]]*\|" "$report" 2>/dev/null || true
}

mkdir -p "$RESULTS_DIR"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

SOURCE_DIR="$(select_source_dir)" || die "No completed pipeline output found with roadmap.md, test-strategy.md, and extraction.md. Run Test 3 first or populate a complete source directory."

if [[ "$SOURCE_DIR" == *"test-3-cascade"* ]]; then
    log "Using Test 3 output as validation input"
else
    log "Using v2.19 completed release as validation input"
fi

log "=================================================================="
log "TEST 4: Multi-Agent Validation Depth Test"
log "=================================================================="
log "Source: ${SOURCE_DIR}"
log "Output: ${OUTPUT_DIR}"
log "Started: ${TIMESTAMP}"
log ""
log "This test runs both single-agent and multi-agent validation on the"
log "same pipeline output to measure actual semantic detection depth."
log ""

prepare_input_dir "${OUTPUT_DIR}/single-agent"
prepare_input_dir "${OUTPUT_DIR}/multi-agent"

log ">>> Running single-agent validation..."
SA_START=$(date +%s)
if run_validation "${OUTPUT_DIR}/single-agent" "opus:architect" "${OUTPUT_DIR}/single-agent-stdout.log"; then
    SA_EXIT=0
else
    SA_EXIT=$?
fi
SA_END=$(date +%s)
SA_ELAPSED=$((SA_END - SA_START))
log ">>> Single-agent validation completed: exit=${SA_EXIT}, ${SA_ELAPSED}s"

log ""
log ">>> Running multi-agent validation..."
MA_START=$(date +%s)
if run_validation "${OUTPUT_DIR}/multi-agent" "opus:architect,haiku:analyst" "${OUTPUT_DIR}/multi-agent-stdout.log"; then
    MA_EXIT=0
else
    MA_EXIT=$?
fi
MA_END=$(date +%s)
MA_ELAPSED=$((MA_END - MA_START))
log ">>> Multi-agent validation completed: exit=${MA_EXIT}, ${MA_ELAPSED}s"

log ""
log ">>> Analyzing validation reports..."

SA_VALIDATE_DIR="${OUTPUT_DIR}/single-agent/validate"
MA_VALIDATE_DIR="${OUTPUT_DIR}/multi-agent/validate"
SA_REPORT="$(resolve_report_path "$SA_VALIDATE_DIR")"
MA_REPORT="$(resolve_report_path "$MA_VALIDATE_DIR")"

IFS='|' read -r SA_BLOCKING SA_WARNINGS SA_INFO SA_TOTAL SA_STRUCTURAL SA_SEMANTIC SA_WORDS SA_COMPLETE <<< "$(analyze_report "$SA_REPORT")"
IFS='|' read -r MA_BLOCKING MA_WARNINGS MA_INFO MA_TOTAL MA_STRUCTURAL MA_SEMANTIC MA_WORDS MA_COMPLETE <<< "$(analyze_report "$MA_REPORT")"

SA_SEMANTIC_RATIO="$(compute_ratio "$SA_SEMANTIC" "$SA_TOTAL")"
MA_SEMANTIC_RATIO="$(compute_ratio "$MA_SEMANTIC" "$MA_TOTAL")"

MA_REFLECT_COUNT=0
if [ -d "$MA_VALIDATE_DIR" ]; then
    shopt -s nullglob
    reflect_reports=("${MA_VALIDATE_DIR}"/reflect-*.md)
    shopt -u nullglob
    MA_REFLECT_COUNT=${#reflect_reports[@]}
fi

HAS_AGREEMENT_TABLE=false
if [ -f "$MA_REPORT" ] && grep -q '^## Agreement Table' "$MA_REPORT" 2>/dev/null; then
    HAS_AGREEMENT_TABLE=true
fi

MA_BOTH_AGREE=$(count_agreement_category "$MA_REPORT" "BOTH_AGREE")
MA_ONLY_A=$(count_agreement_category "$MA_REPORT" "ONLY_A")
MA_ONLY_B=$(count_agreement_category "$MA_REPORT" "ONLY_B")
MA_CONFLICT=$(count_agreement_category "$MA_REPORT" "CONFLICT")

cat > "${RESULTS_DIR}/test-4-results.json" <<JSONEOF
{
    "test_id": "test-4-validation-depth",
    "test_version": "v2.20-baseline",
    "timestamp": "${TIMESTAMP}",
    "findings_targeted": ["F-001", "F-002", "validate-pipeline"],
    "source_dir": "${SOURCE_DIR}",
    "single_agent": {
        "exit_code": ${SA_EXIT},
        "elapsed_seconds": ${SA_ELAPSED},
        "report_path": "${SA_REPORT}",
        "validation_complete": ${SA_COMPLETE},
        "blocking_issues": ${SA_BLOCKING},
        "warnings": ${SA_WARNINGS},
        "info_items": ${SA_INFO},
        "total_findings": ${SA_TOTAL},
        "structural_findings": ${SA_STRUCTURAL},
        "semantic_findings": ${SA_SEMANTIC},
        "semantic_ratio": ${SA_SEMANTIC_RATIO},
        "word_count": ${SA_WORDS}
    },
    "multi_agent": {
        "exit_code": ${MA_EXIT},
        "elapsed_seconds": ${MA_ELAPSED},
        "report_path": "${MA_REPORT}",
        "validation_complete": ${MA_COMPLETE},
        "blocking_issues": ${MA_BLOCKING},
        "warnings": ${MA_WARNINGS},
        "info_items": ${MA_INFO},
        "total_findings": ${MA_TOTAL},
        "structural_findings": ${MA_STRUCTURAL},
        "semantic_findings": ${MA_SEMANTIC},
        "semantic_ratio": ${MA_SEMANTIC_RATIO},
        "reflect_reports": ${MA_REFLECT_COUNT},
        "has_agreement_table": ${HAS_AGREEMENT_TABLE},
        "both_agree": ${MA_BOTH_AGREE},
        "only_a": ${MA_ONLY_A},
        "only_b": ${MA_ONLY_B},
        "conflicts": ${MA_CONFLICT},
        "word_count": ${MA_WORDS}
    },
    "comparison": {
        "blocking_delta": $((MA_BLOCKING - SA_BLOCKING)),
        "warning_delta": $((MA_WARNINGS - SA_WARNINGS)),
        "info_delta": $((MA_INFO - SA_INFO)),
        "total_findings_delta": $((MA_TOTAL - SA_TOTAL)),
        "structural_delta": $((MA_STRUCTURAL - SA_STRUCTURAL)),
        "semantic_delta": $((MA_SEMANTIC - SA_SEMANTIC)),
        "semantic_ratio_single": ${SA_SEMANTIC_RATIO},
        "semantic_ratio_multi": ${MA_SEMANTIC_RATIO}
    },
    "interpretation": {
        "baseline_expectation": "Both modes may produce well-formed reports, but pre-v2.20 they are expected to skew structural. Multi-agent depth is only meaningful if the merged report completes successfully.",
        "target": "Higher semantic finding ratio, successful multi-agent merge, and evidence that multi-agent validation surfaces unique issues or conflicts that single-agent validation misses."
    }
}
JSONEOF

log ""
log "=================================================================="
log "TEST 4 RESULTS — Validation Depth Comparison"
log "=================================================================="
log ""
printf "%-25s %15s %15s\n" "METRIC" "SINGLE-AGENT" "MULTI-AGENT"
printf "%-25s %15s %15s\n" "========================" "==============" "=============="
printf "%-25s %15s %15s\n" "Exit code" "${SA_EXIT}" "${MA_EXIT}"
printf "%-25s %15s %15s\n" "Elapsed (s)" "${SA_ELAPSED}" "${MA_ELAPSED}"
printf "%-25s %15s %15s\n" "Report complete" "${SA_COMPLETE}" "${MA_COMPLETE}"
printf "%-25s %15s %15s\n" "Blocking issues" "${SA_BLOCKING}" "${MA_BLOCKING}"
printf "%-25s %15s %15s\n" "Warnings" "${SA_WARNINGS}" "${MA_WARNINGS}"
printf "%-25s %15s %15s\n" "Info items" "${SA_INFO}" "${MA_INFO}"
printf "%-25s %15s %15s\n" "Total findings" "${SA_TOTAL}" "${MA_TOTAL}"
printf "%-25s %15s %15s\n" "Structural findings" "${SA_STRUCTURAL}" "${MA_STRUCTURAL}"
printf "%-25s %15s %15s\n" "Semantic findings" "${SA_SEMANTIC}" "${MA_SEMANTIC}"
printf "%-25s %15s %15s\n" "Semantic ratio" "${SA_SEMANTIC_RATIO}" "${MA_SEMANTIC_RATIO}"
printf "%-25s %15s %15s\n" "Report word count" "${SA_WORDS}" "${MA_WORDS}"
printf "%-25s %15s %15s\n" "Reflect reports" "0" "${MA_REFLECT_COUNT}"
printf "%-25s %15s %15s\n" "Agreement table" "N/A" "${HAS_AGREEMENT_TABLE}"
printf "%-25s %15s %15s\n" "ONLY_A findings" "N/A" "${MA_ONLY_A}"
printf "%-25s %15s %15s\n" "ONLY_B findings" "N/A" "${MA_ONLY_B}"
printf "%-25s %15s %15s\n" "CONFLICT findings" "N/A" "${MA_CONFLICT}"
log ""
log "INTERPRETATION:"
log "  Compare semantic_ratio and semantic_delta first, but only trust the"
log "  multi-agent result if report_complete=true and the merged report exists."
log "  ONLY_A/ONLY_B/CONFLICT counts show whether multi-agent validation exposed"
log "  issue disagreement or additional depth instead of just longer prose."
log ""
log "Results saved to: ${RESULTS_DIR}/test-4-results.json"
log "=================================================================="