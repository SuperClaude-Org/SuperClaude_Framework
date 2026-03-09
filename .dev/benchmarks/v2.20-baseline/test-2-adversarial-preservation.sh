#!/usr/bin/env bash
# =============================================================================
# TEST 2: Adversarial Conclusion Preservation Test
# =============================================================================
# Finding: F-003 — "The Adversarial Stage Is Better at Design Critique Than
#                    Runtime Falsification"
# Finding: F-006 — "Seam Failures Are a Primary Failure Habitat"
# Success Criteria: SC-002 — "Adversarial conclusion incorporation rate ≥95%"
#
# WHAT THIS TESTS:
# The forensic diagnostic found that ~10-15% of adversarial conclusions are
# "simplified or dropped without systematic downstream tracking" at the
# adversarial→merge seam. This test runs the pipeline on a real, complex spec
# and measures the actual conclusion preservation rate.
#
# METHOD:
# 1. Run the full pipeline on a real spec (SC-ADVERSARIAL-SPEC.md)
# 2. Prefer incorporation directives from base-selection.md because they are the
#    explicit handoff from adversarial evaluation into the merge step
# 3. Fall back to debate-transcript.md conclusion markers if base-selection.md
#    does not provide explicit incorporation items
# 4. Check how many of those markers appear in the merged roadmap
# 5. Calculate preservation rate
#
# EXPECTED BASELINE (pre-v2.20):
# - 85-90% preservation rate (matching forensic estimate of 10-15% loss)
# - No tracking mechanism exists to audit what was lost
#
# POST-v2.20 EXPECTED:
# - ≥95% preservation rate (SC-002)
# - Tracking ledger showing disposition of every conclusion
#
# METRICS CAPTURED:
# - debate_conclusion_count: Total scored conclusions in debate transcript
# - incorporation_markers_total: Total markers tracked into merge
# - incorporation_markers_in_merged: How many appear in merged roadmap
# - incorporation_markers_missing: How many were lost
# - preservation_rate: incorporation_markers_in_merged / incorporation_markers_total
# - diff_point_count: Points declared by diff-analysis frontmatter
# - diff_topics_in_merged: How many debated topics survive in final roadmap
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"
cd "$REPO_ROOT"

BENCHMARK_DIR=".dev/benchmarks/v2.20-baseline"
RESULTS_DIR="${BENCHMARK_DIR}/results"
OUTPUT_DIR="${BENCHMARK_DIR}/outputs/test-2-adversarial"
SPEC_FILE=".dev/releases/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PIPELINE_LOG="${OUTPUT_DIR}/pipeline-stdout.log"

mkdir -p "$RESULTS_DIR" "$OUTPUT_DIR"

normalize_text_stream() {
    tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/ /g; s/[[:space:]]+/ /g; s/^ //; s/ $//'
}

normalize_line() {
    printf '%s\n' "$1" | normalize_text_stream
}

marker_word_count() {
    printf '%s\n' "$1" | wc -w | tr -d ' '
}

extract_base_selection_markers() {
    local source_file="$1"
    local output_file="$2"
    local tmp_raw
    tmp_raw="${OUTPUT_DIR}/base-selection-markers.raw"
    : > "$tmp_raw"

    awk '
        BEGIN { capture = 0 }
        /^### Strengths to Incorporate from Non-Base Variants/ { capture = 1; next }
        capture && /^### / { capture = 0 }
        capture && /^[[:space:]]*[0-9]+\.[[:space:]]/ {
            sub(/^[[:space:]]*[0-9]+\.[[:space:]]*/, "")
            print
        }
    ' "$source_file" > "$tmp_raw"

    : > "$output_file"
    while IFS= read -r line; do
        [ -n "$line" ] || continue
        local normalized
        normalized=$(normalize_line "$line")
        local word_count
        word_count=$(marker_word_count "$normalized")
        if [ "$word_count" -ge 4 ]; then
            printf '%s\n' "$normalized"
        fi
    done < "$tmp_raw" | sort -u > "$output_file"
}

extract_debate_markers() {
    local source_file="$1"
    local output_file="$2"
    local tmp_raw
    tmp_raw="${OUTPUT_DIR}/debate-markers.raw"
    : > "$tmp_raw"

    awk '
        /^## Scoring Matrix/ { scoring = 1; next }
        /^## Convergence Assessment/ { scoring = 0 }
        scoring && /^\| [A-Z]-[0-9]{3} / {
            n = split($0, parts, "|")
            if (n >= 6) {
                text = parts[5]
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", text)
                print text
            }
            next
        }
        /^## Round / { rounds = 1; next }
        rounds && /^## / { rounds = 0 }
        rounds && /^[[:space:]]*[0-9]+\.[[:space:]]/ {
            sub(/^[[:space:]]*[0-9]+\.[[:space:]]*/, "")
            print
        }
    ' "$source_file" > "$tmp_raw"

    : > "$output_file"
    while IFS= read -r line; do
        [ -n "$line" ] || continue
        local normalized
        normalized=$(normalize_line "$line")
        local word_count
        word_count=$(marker_word_count "$normalized")
        if [ "$word_count" -ge 4 ]; then
            printf '%s\n' "$normalized"
        fi
    done < "$tmp_raw" | sort -u > "$output_file"
}

extract_diff_topics() {
    local source_file="$1"
    local output_file="$2"
    local tmp_raw
    tmp_raw="${OUTPUT_DIR}/diff-markers.raw"

    awk -F'|' '
        /^[|][[:space:]]*[SCXU]-[0-9]{3}[[:space:]]*[|]/ {
            topic = $3
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", topic)
            if (topic != "") {
                print topic
            }
        }
    ' "$source_file" > "$tmp_raw"

    : > "$output_file"
    while IFS= read -r line; do
        [ -n "$line" ] || continue
        local normalized
        normalized=$(normalize_line "$line")
        local word_count
        word_count=$(marker_word_count "$normalized")
        if [ "$word_count" -ge 2 ]; then
            printf '%s\n' "$normalized"
        fi
    done < "$tmp_raw" | sort -u > "$output_file"
}

count_markers_in_text() {
    local markers_file="$1"
    local haystack_file="$2"
    local found=0

    if [ ! -f "$markers_file" ] || [ ! -s "$markers_file" ] || [ ! -f "$haystack_file" ]; then
        printf '0\n'
        return
    fi

    while IFS= read -r marker; do
        [ -n "$marker" ] || continue
        if grep -Fqi -- "$marker" "$haystack_file"; then
            found=$((found + 1))
        fi
    done < "$markers_file"

    printf '%s\n' "$found"
}

write_missing_markers() {
    local markers_file="$1"
    local haystack_file="$2"
    local output_file="$3"

    : > "$output_file"
    if [ ! -f "$markers_file" ] || [ ! -s "$markers_file" ] || [ ! -f "$haystack_file" ]; then
        return
    fi

    while IFS= read -r marker; do
        [ -n "$marker" ] || continue
        if ! grep -Fqi -- "$marker" "$haystack_file"; then
            printf '%s\n' "$marker" >> "$output_file"
        fi
    done < "$markers_file"
}

parse_frontmatter_int() {
    local key="$1"
    local file_path="$2"

    if [ ! -f "$file_path" ]; then
        printf '0\n'
        return
    fi

    sed -n -E "s/^${key}:[[:space:]]*([0-9]+)[[:space:]]*$/\1/p" "$file_path" | head -n 1 | sed '/^$/d' || true
}

echo "=================================================================="
echo "TEST 2: Adversarial Conclusion Preservation Test"
echo "=================================================================="
echo "Spec: ${SPEC_FILE}"
echo "Output: ${OUTPUT_DIR}"
echo "Started: ${TIMESTAMP}"
echo ""
echo "This test runs a real complex spec through the full pipeline and"
echo "measures how many adversarial conclusions survive the merge seam."
echo ""

if ! command -v superclaude >/dev/null 2>&1; then
    echo "ERROR: superclaude command not found in PATH" >&2
    exit 127
fi

if ! command -v bc >/dev/null 2>&1; then
    echo "ERROR: bc command not found in PATH" >&2
    exit 127
fi

if [ ! -f "$SPEC_FILE" ]; then
    echo "ERROR: Spec file not found: ${SPEC_FILE}" >&2
    exit 1
fi

rm -rf "${OUTPUT_DIR:?}"/*
mkdir -p "$OUTPUT_DIR"

echo ">>> Running pipeline: superclaude roadmap run ..."
START_TIME=$(date +%s)

set +e
superclaude roadmap run "$SPEC_FILE" \
    --output "$OUTPUT_DIR" \
    --agents "opus:architect,haiku:analyst" \
    --depth deep \
    --debug 2>&1 | tee "$PIPELINE_LOG"
PIPELINE_EXIT=${PIPESTATUS[0]}
set -e

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo ">>> Pipeline completed with exit code: ${PIPELINE_EXIT}"
echo ">>> Elapsed time: ${ELAPSED}s"
echo ""

echo ">>> Analyzing adversarial conclusion preservation..."

DEBATE="${OUTPUT_DIR}/debate-transcript.md"
if [ ! -f "$DEBATE" ] && [ -f "${OUTPUT_DIR}/adversarial/debate-transcript.md" ]; then
    DEBATE="${OUTPUT_DIR}/adversarial/debate-transcript.md"
fi

DIFF="${OUTPUT_DIR}/diff-analysis.md"
if [ ! -f "$DIFF" ] && [ -f "${OUTPUT_DIR}/adversarial/diff-analysis.md" ]; then
    DIFF="${OUTPUT_DIR}/adversarial/diff-analysis.md"
fi

BASE_SELECTION="${OUTPUT_DIR}/base-selection.md"
MERGED="${OUTPUT_DIR}/roadmap.md"
NORMALIZED_MERGED="${OUTPUT_DIR}/roadmap.normalized.txt"
PRESERVATION_MARKERS_FILE="${OUTPUT_DIR}/preservation-markers.txt"
MISSING_MARKERS_FILE="${OUTPUT_DIR}/missing-conclusions.txt"
DIFF_MARKERS_FILE="${OUTPUT_DIR}/diff-markers.txt"

if [ -f "$MERGED" ]; then
    normalize_text_stream < "$MERGED" > "$NORMALIZED_MERGED"
else
    : > "$NORMALIZED_MERGED"
fi

DEBATE_CONCLUSIONS=0
if [ -f "$DEBATE" ]; then
    DEBATE_CONCLUSIONS=$(awk '
        /^## Scoring Matrix/ { scoring = 1; next }
        /^## Convergence Assessment/ { scoring = 0 }
        scoring && /^\| [A-Z]-[0-9]{3} / { count++ }
        END { print count + 0 }
    ' "$DEBATE")
fi

PRESERVATION_SOURCE="none"
: > "$PRESERVATION_MARKERS_FILE"

if [ -f "$BASE_SELECTION" ]; then
    extract_base_selection_markers "$BASE_SELECTION" "$PRESERVATION_MARKERS_FILE"
    if [ -s "$PRESERVATION_MARKERS_FILE" ]; then
        PRESERVATION_SOURCE="base-selection-incorporations"
    fi
fi

if [ "$PRESERVATION_SOURCE" = "none" ] && [ -f "$DEBATE" ]; then
    extract_debate_markers "$DEBATE" "$PRESERVATION_MARKERS_FILE"
    if [ -s "$PRESERVATION_MARKERS_FILE" ]; then
        PRESERVATION_SOURCE="debate-fallback"
    fi
fi

MARKERS_TOTAL=0
if [ -f "$PRESERVATION_MARKERS_FILE" ] && [ -s "$PRESERVATION_MARKERS_FILE" ]; then
    MARKERS_TOTAL=$(wc -l < "$PRESERVATION_MARKERS_FILE" | tr -d ' ')
fi

MARKERS_FOUND=$(count_markers_in_text "$PRESERVATION_MARKERS_FILE" "$NORMALIZED_MERGED")
write_missing_markers "$PRESERVATION_MARKERS_FILE" "$NORMALIZED_MERGED" "$MISSING_MARKERS_FILE"

DIFF_POINTS_RAW=$(parse_frontmatter_int "total_diff_points" "$DIFF")
DIFF_POINTS=${DIFF_POINTS_RAW:-0}
if ! printf '%s\n' "$DIFF_POINTS" | grep -Eq '^[0-9]+$'; then
    DIFF_POINTS=0
fi

DIFF_TOPICS_TOTAL=0
DIFF_IN_MERGED=0
if [ -f "$DIFF" ]; then
    extract_diff_topics "$DIFF" "$DIFF_MARKERS_FILE"
    if [ -s "$DIFF_MARKERS_FILE" ]; then
        DIFF_TOPICS_TOTAL=$(wc -l < "$DIFF_MARKERS_FILE" | tr -d ' ')
        DIFF_IN_MERGED=$(count_markers_in_text "$DIFF_MARKERS_FILE" "$NORMALIZED_MERGED")
    fi
fi

if [ "$MARKERS_TOTAL" -gt 0 ]; then
    PRESERVATION_RATE=$(echo "scale=2; $MARKERS_FOUND * 100 / $MARKERS_TOTAL" | bc)
else
    PRESERVATION_RATE="N/A"
fi

DEBATE_WORDS=0
MERGED_WORDS=0
if [ -f "$DEBATE" ]; then
    DEBATE_WORDS=$(wc -w < "$DEBATE" | tr -d ' ')
fi
if [ -f "$MERGED" ]; then
    MERGED_WORDS=$(wc -w < "$MERGED" | tr -d ' ')
fi
if [ "$DEBATE_WORDS" -gt 0 ]; then
    COMPRESSION_RATIO=$(echo "scale=2; $MERGED_WORDS * 100 / $DEBATE_WORDS" | bc)
else
    COMPRESSION_RATIO="N/A"
fi

cat > "${RESULTS_DIR}/test-2-results.json" <<JSONEOF
{
    "test_id": "test-2-adversarial-preservation",
    "test_version": "v2.20-baseline",
    "timestamp": "${TIMESTAMP}",
    "findings_targeted": ["F-003", "F-006", "SC-002"],
    "spec_file": "${SPEC_FILE}",
    "pipeline_exit_code": ${PIPELINE_EXIT},
    "elapsed_seconds": ${ELAPSED},
    "artifacts": {
        "debate_transcript": "${DEBATE}",
        "diff_analysis": "${DIFF}",
        "base_selection": "${BASE_SELECTION}",
        "merged_roadmap": "${MERGED}"
    },
    "metrics": {
        "debate_conclusion_count": ${DEBATE_CONCLUSIONS},
        "incorporation_markers_total": ${MARKERS_TOTAL},
        "incorporation_markers_source": "${PRESERVATION_SOURCE}",
        "incorporation_markers_in_merged": ${MARKERS_FOUND},
        "incorporation_markers_missing": $((MARKERS_TOTAL - MARKERS_FOUND)),
        "preservation_rate_pct": "${PRESERVATION_RATE}",
        "diff_points_declared": ${DIFF_POINTS},
        "diff_topics_tracked": ${DIFF_TOPICS_TOTAL},
        "diff_topics_in_merged": ${DIFF_IN_MERGED},
        "debate_word_count": ${DEBATE_WORDS},
        "merged_word_count": ${MERGED_WORDS},
        "compression_ratio_pct": "${COMPRESSION_RATIO}"
    },
    "audit_artifacts": {
        "preservation_markers": "outputs/test-2-adversarial/preservation-markers.txt",
        "diff_markers": "outputs/test-2-adversarial/diff-markers.txt",
        "missing_conclusions": "outputs/test-2-adversarial/missing-conclusions.txt"
    },
    "interpretation": {
        "baseline_expectation": "85-90% preservation (10-15% loss per forensic finding F-003)",
        "target": ">=95% (SC-002)",
        "note": "Primary metric uses base-selection incorporation directives when available; otherwise falls back to normalized debate conclusions for approximate seam auditing"
    }
}
JSONEOF

echo ""
echo "=================================================================="
echo "TEST 2 RESULTS"
echo "=================================================================="
echo "Pipeline exit code:          ${PIPELINE_EXIT}"
echo "Elapsed time:                ${ELAPSED}s"
echo ""
echo "PRESERVATION ANALYSIS:"
echo "  Debate conclusions scored: ${DEBATE_CONCLUSIONS}"
echo "  Marker source:             ${PRESERVATION_SOURCE}"
echo "  Markers tracked:           ${MARKERS_TOTAL}"
echo "  Markers found in merged:   ${MARKERS_FOUND}"
echo "  Markers missing:           $((MARKERS_TOTAL - MARKERS_FOUND))"
echo "  Preservation rate:         ${PRESERVATION_RATE}%"
echo ""
echo "DIFF ANALYSIS:"
echo "  Declared diff points:      ${DIFF_POINTS}"
echo "  Diff topics tracked:       ${DIFF_TOPICS_TOTAL}"
echo "  Diff topics in merged:     ${DIFF_IN_MERGED}"
echo ""
echo "DENSITY:"
echo "  Debate word count:         ${DEBATE_WORDS}"
echo "  Merged word count:         ${MERGED_WORDS}"
echo "  Compression ratio:         ${COMPRESSION_RATIO}%"
echo ""
echo "INTERPRETATION:"
if [ "$PRESERVATION_RATE" != "N/A" ]; then
    RATE_INT=${PRESERVATION_RATE%.*}
    if [ "$RATE_INT" -lt 95 ]; then
        echo "  >> BASELINE CONFIRMED: Preservation rate ${PRESERVATION_RATE}% is below"
        echo "     SC-002 target of ≥95%. Consistent with F-003/F-006 seam loss."
    else
        echo "  >> BETTER THAN EXPECTED: Preservation rate exceeds target."
    fi
else
    echo "  >> INCONCLUSIVE: No usable preservation markers were extracted."
fi
if [ "$PIPELINE_EXIT" -ne 0 ]; then
    echo "  >> PIPELINE WARNING: roadmap run failed; metrics may reflect partial artifacts only."
fi
echo ""
echo "  Missing conclusions saved to: outputs/test-2-adversarial/missing-conclusions.txt"
echo "  Review manually for semantic paraphrases that normalized marker matching missed."
echo ""
echo "Results saved to: ${RESULTS_DIR}/test-2-results.json"
echo "=================================================================="

exit "$PIPELINE_EXIT"
