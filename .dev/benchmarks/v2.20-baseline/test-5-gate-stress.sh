#!/usr/bin/env bash
# =============================================================================
# TEST 5: Gate False-Negative Stress Test
# =============================================================================
# Finding: F-001 — "Structural Validation Is Systematically Mistaken for
#                    Semantic Correctness"
# Gate weaknesses: _cross_refs_resolve() never fails, _has_actionable_content()
#                  accepts minimal bullets, _convergence_score_valid() only
#                  checks range
#
# WHAT THIS TESTS:
# This test directly exercises known gate weaknesses by validating REAL pipeline
# outputs, then corrupting copied artifacts and running real
# `superclaude roadmap validate` passes to see which corruptions are caught.
#
# CORRUPTIONS APPLIED (each designed to exploit a known gate weakness):
# 1. Cross-reference corruption: Add "See Section XYZ" referencing nonexistent heading
# 2. Actionability corruption: Replace bullet items with vague non-actionable text
# 3. Convergence corruption: Set convergence_score to 0.99 in a very short debate
# 4. Heading gap corruption: Skip H3 between H2 and H4
# 5. Duplicate heading corruption: Duplicate an H2
# 6. Frontmatter corruption: Add frontmatter with empty values
# 7. Semantic nonsense: Replace a milestone's content with Lorem Ipsum
#
# METHOD:
# 1. Validate a clean baseline copy of real pipeline outputs
# 2. For each corruption type:
#    a. Copy the clean baseline inputs
#    b. Apply one corruption deterministically
#    c. Run `superclaude roadmap validate` on the corrupted dir
#    d. Compare the result against the clean baseline and record detection
#
# EXPECTED BASELINE (pre-v2.20):
# - Corruptions 1, 2, 3, 7: MISSED (known gate weaknesses)
# - Corruptions 4, 5: CAUGHT (heading gaps and duplicates are enforced)
# - Corruption 6: CAUGHT only if STRICT tier (depends on which file)
#
# POST-v2.20 EXPECTED:
# - All corruptions caught by upgraded semantic gates
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

BENCHMARK_DIR="${REPO_ROOT}/.dev/benchmarks/v2.20-baseline"
RESULTS_DIR="${BENCHMARK_DIR}/results"
OUTPUT_DIR="${BENCHMARK_DIR}/outputs/test-5-gate-stress"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$RESULTS_DIR" "$OUTPUT_DIR"

SOURCE_DIR=""
for candidate in \
    "${BENCHMARK_DIR}/outputs/test-3-cascade" \
    "${BENCHMARK_DIR}/outputs/test-2-adversarial" \
    "${REPO_ROOT}/.dev/releases/complete/v2.19-roadmap-validate"
do
    if [ -f "${candidate}/roadmap.md" ] && \
       [ -f "${candidate}/extraction.md" ] && \
       [ -f "${candidate}/test-strategy.md" ]; then
        SOURCE_DIR="$candidate"
        break
    fi
done

if [ -z "$SOURCE_DIR" ]; then
    printf '%s\n' "ERROR: No completed pipeline output found with roadmap.md, extraction.md, and test-strategy.md." >&2
    printf '%s\n' "Run Test 3 first, or provide a completed release output." >&2
    exit 1
fi

copy_validation_inputs() {
    local src_dir="$1"
    local dest_dir="$2"

    rm -rf "$dest_dir"
    mkdir -p "$dest_dir"

    cp "${src_dir}/roadmap.md" "$dest_dir/"
    cp "${src_dir}/extraction.md" "$dest_dir/"
    cp "${src_dir}/test-strategy.md" "$dest_dir/"

    for optional in debate-transcript.md diff-analysis.md; do
        if [ -f "${src_dir}/${optional}" ]; then
            cp "${src_dir}/${optional}" "$dest_dir/"
        fi
    done
}

run_validate() {
    local target_dir="$1"
    local log_path="$2"

    set +e
    uv run superclaude roadmap validate "$target_dir" \
        --agents "opus:architect" \
        --debug >"$log_path" 2>&1
    local exit_code=$?
    set -e

    printf '%s' "$exit_code"
}

extract_counts() {
    local report_path="$1"

    uv run python - "$report_path" <<'PY'
from pathlib import Path
import re
import sys

report = Path(sys.argv[1])
if not report.exists():
    print("0|0|0")
    raise SystemExit(0)

text = report.read_text(encoding="utf-8")

def field(name: str) -> int:
    match = re.search(rf"{re.escape(name)}:\s*(\d+)", text)
    return int(match.group(1)) if match else 0

print(f"{field('blocking_issues_count')}|{field('warnings_count')}|{field('info_count')}")
PY
}

apply_corruption() {
    local corruption_name="$1"
    local corrupt_dir="$2"

    uv run python - "$corruption_name" "$corrupt_dir" <<'PY'
from pathlib import Path
import re
import sys

corruption = sys.argv[1]
corrupt_dir = Path(sys.argv[2])
roadmap = corrupt_dir / "roadmap.md"
debate = corrupt_dir / "debate-transcript.md"

if not roadmap.exists():
    raise SystemExit("roadmap.md missing in corruption target")

text = roadmap.read_text(encoding="utf-8")
original = text


def replace_first_n_bullets(source: str, replacements: list[str]) -> str:
    lines = source.splitlines()
    bullet_indexes = [i for i, line in enumerate(lines) if re.match(r"^\s*(?:[-*]|\d+\.)\s+", line)]
    if len(bullet_indexes) < len(replacements):
        raise SystemExit("not enough bullet items to corrupt actionability")
    for idx, replacement in zip(bullet_indexes[: len(replacements)], replacements):
        prefix_match = re.match(r"^(\s*)(?:[-*]|\d+\.)\s+", lines[idx])
        indent = prefix_match.group(1) if prefix_match else ""
        lines[idx] = f"{indent}- {replacement}"
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


if corruption == "cross-ref":
    heading_match = re.search(r"(?m)^## ", text)
    if not heading_match:
        raise SystemExit("no H2 heading found for cross-ref corruption")
    insert = (
        '> **Important**: See Section "Quantum Flux Integration" for critical dependency details. '
        'Also refer to "Risk Matrix Delta" in the appendix.\n'
    )
    text = text[: heading_match.start()] + insert + text[heading_match.start() :]
elif corruption == "actionability":
    text = replace_first_n_bullets(
        text,
        [
            "Things will be done appropriately",
            "Stuff will be handled as needed",
            "Various aspects will be considered",
            "Appropriate measures will be taken",
            "Items will be addressed in due course",
        ],
    )
elif corruption == "convergence":
    if not debate.exists():
        raise SystemExit("debate-transcript.md missing for convergence corruption")
    debate_text = debate.read_text(encoding="utf-8")
    if "convergence_score:" not in debate_text:
        raise SystemExit("convergence_score field missing in debate-transcript.md")
    debate_text, count = re.subn(
        r"(?m)^convergence_score:\s*.*$",
        "convergence_score: 0.99",
        debate_text,
        count=1,
    )
    if count != 1:
        raise SystemExit("failed to replace convergence_score")
    body_lines = debate_text.splitlines()
    frontmatter_end = None
    dash_count = 0
    for i, line in enumerate(body_lines):
        if line.strip() == "---":
            dash_count += 1
            if dash_count == 2:
                frontmatter_end = i
                break
    if frontmatter_end is None:
        raise SystemExit("debate-transcript frontmatter malformed")
    compact_body = [line for line in body_lines[frontmatter_end + 1 :] if line.strip()][:4]
    if not compact_body:
        compact_body = ["Round 1: A and B agree quickly."]
    debate.write_text(
        "\n".join(body_lines[: frontmatter_end + 1] + compact_body) + "\n",
        encoding="utf-8",
    )
    raise SystemExit(0)
elif corruption == "heading-gap":
    pattern = re.compile(r"(?ms)(^## .+?$\n)(.*?)(^### .+?$)")
    match = pattern.search(text)
    if not match:
        raise SystemExit("no H2/H3 boundary found for heading-gap corruption")
    replacement = match.group(1) + match.group(2) + match.group(3).replace("### ", "#### ", 1)
    text = text[: match.start()] + replacement + text[match.end() :]
elif corruption == "duplicate-heading":
    match = re.search(r"(?m)^(## .+)$", text)
    if not match:
        raise SystemExit("no H2 heading found for duplication")
    duplicate = match.group(1)
    insertion = f"{duplicate}\n"
    text = text[: match.end()] + "\n" + insertion + text[match.end() :]
elif corruption == "empty-frontmatter":
    required_fields = ["spec_source", "complexity_score"]
    for field in required_fields:
        if not re.search(rf"(?m)^{re.escape(field)}:\s*.+$", text):
            raise SystemExit(f"required frontmatter field missing: {field}")
        text = re.sub(rf"(?m)^{re.escape(field)}:\s*.+$", f"{field}: ", text, count=1)
elif corruption == "semantic-nonsense":
    pattern = re.compile(r"(?ms)(^### .+?$\n)(.*?)(?=^### |^## |\Z)")
    match = pattern.search(text)
    if not match:
        raise SystemExit("no H3 section found for semantic-nonsense corruption")
    lorem = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod\n"
        "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,\n"
        "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo\n"
        "consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse\n"
        "cillum dolore eu fugiat nulla pariatur.\n\n"
        "- Lorem ipsum bullet point one\n"
        "- Consectetur adipiscing elit item two\n"
        "- Sed do eiusmod tempor incididunt three\n"
    )
    text = text[: match.start(2)] + lorem + text[match.end(2) :]
else:
    raise SystemExit(f"unknown corruption: {corruption}")

if text == original:
    raise SystemExit(f"corruption produced no change: {corruption}")

roadmap.write_text(text, encoding="utf-8")
PY
}

detect_corruption() {
    local corruption_name="$1"
    local baseline_blocking="$2"
    local baseline_warnings="$3"
    local current_blocking="$4"
    local current_warnings="$5"
    local report_path="$6"
    local log_path="$7"

    local regex=""
    case "$corruption_name" in
        cross-ref)
            regex='reference.*not found|missing.*section|unresolved.*reference|quantum flux|risk matrix delta'
            ;;
        actionability)
            regex='vague|non-actionable|insufficient detail|not actionable|generic|specific'
            ;;
        convergence)
            regex='convergence.*high|convergence.*suspicious|unrealistic.*convergence|0\.99|debate.*short|rounds_completed'
            ;;
        heading-gap)
            regex='heading.*gap|heading.*skip|hierarchy.*invalid|h2.*h4|level gap'
            ;;
        duplicate-heading)
            regex='duplicate.*heading|duplicate.*section|repeated.*heading'
            ;;
        empty-frontmatter)
            regex='empty.*value|missing.*value|frontmatter.*empty|blank.*field|required frontmatter'
            ;;
        semantic-nonsense)
            regex='lorem|nonsense|irrelevant|placeholder|not.*meaningful|content.*quality'
            ;;
    esac

    if [ -n "$regex" ] && grep -qiE "$regex" "$report_path" "$log_path" 2>/dev/null; then
        printf 'true'
        return
    fi

    if [ "$current_blocking" -gt "$baseline_blocking" ] || [ "$current_warnings" -gt "$baseline_warnings" ]; then
        printf 'true'
        return
    fi

    printf 'false'
}

RESULTS=()

BASELINE_DIR="${OUTPUT_DIR}/baseline-clean"
BASELINE_LOG="${OUTPUT_DIR}/baseline-validation.log"
copy_validation_inputs "$SOURCE_DIR" "$BASELINE_DIR"
BASELINE_EXIT="$(run_validate "$BASELINE_DIR" "$BASELINE_LOG")"
BASELINE_REPORT="${BASELINE_DIR}/validate/validation-report.md"
IFS='|' read -r BASELINE_BLOCKING BASELINE_WARNINGS BASELINE_INFO <<< "$(extract_counts "$BASELINE_REPORT")"

echo "=================================================================="
echo "TEST 5: Gate False-Negative Stress Test"
echo "=================================================================="
echo "Source: ${SOURCE_DIR}"
echo "Output: ${OUTPUT_DIR}"
echo "Started: ${TIMESTAMP}"
echo ""
echo "This test corrupts pipeline artifacts in 7 specific ways and tests"
echo "whether validation catches each corruption against a clean baseline."
echo ""
echo ">>> Clean baseline validation: exit=${BASELINE_EXIT}, blocking=${BASELINE_BLOCKING}, warnings=${BASELINE_WARNINGS}, info=${BASELINE_INFO}"
echo ""

declare -A CORRUPTIONS
CORRUPTIONS[cross-ref]="Add nonexistent cross-reference"
CORRUPTIONS[actionability]="Replace bullets with vague text"
CORRUPTIONS[convergence]="Inflate convergence to 0.99 in short debate"
CORRUPTIONS[heading-gap]="Introduce H2→H4 gap (skip H3)"
CORRUPTIONS[duplicate-heading]="Duplicate an H2 heading"
CORRUPTIONS[empty-frontmatter]="Empty frontmatter values"
CORRUPTIONS[semantic-nonsense]="Replace milestone content with Lorem Ipsum"

run_corruption_test() {
    local corruption_name="$1"
    local corruption_desc="$2"
    local corrupt_dir="${OUTPUT_DIR}/${corruption_name}"
    local validation_log="${corrupt_dir}/validation-stdout.log"
    local report="${corrupt_dir}/validate/validation-report.md"

    echo ">>> Testing corruption: ${corruption_name} — ${corruption_desc}"

    copy_validation_inputs "$SOURCE_DIR" "$corrupt_dir"
    apply_corruption "$corruption_name" "$corrupt_dir"

    local validation_exit
    validation_exit="$(run_validate "$corrupt_dir" "$validation_log")"

    local blocking warnings info detected
    IFS='|' read -r blocking warnings info <<< "$(extract_counts "$report")"
    detected="$(detect_corruption \
        "$corruption_name" \
        "$BASELINE_BLOCKING" \
        "$BASELINE_WARNINGS" \
        "$blocking" \
        "$warnings" \
        "$report" \
        "$validation_log")"

    echo "  Exit: ${validation_exit}, Blocking: ${blocking}, Warnings: ${warnings}, Info: ${info}, Detected: ${detected}"

    RESULTS+=("${corruption_name}|${validation_exit}|${blocking}|${warnings}|${info}|${detected}")
}

for corruption_name in cross-ref actionability convergence heading-gap duplicate-heading empty-frontmatter semantic-nonsense; do
    run_corruption_test "$corruption_name" "${CORRUPTIONS[$corruption_name]}"
    echo ""
done

RESULTS_JSON="["
DETECTED_COUNT=0
MISSED_COUNT=0
TOTAL_COUNT=${#RESULTS[@]}
for i in "${!RESULTS[@]}"; do
    IFS='|' read -r name validation_exit blocking warnings info detected <<< "${RESULTS[$i]}"
    [ "$i" -gt 0 ] && RESULTS_JSON+=","
    RESULTS_JSON+="{\"corruption\":\"${name}\",\"validate_exit\":${validation_exit},\"blocking\":${blocking},\"warnings\":${warnings},\"info\":${info},\"detected\":${detected}}"
    if [ "$detected" = "true" ]; then
        DETECTED_COUNT=$((DETECTED_COUNT + 1))
    else
        MISSED_COUNT=$((MISSED_COUNT + 1))
    fi
done
RESULTS_JSON+="]"

DETECTION_RATE_PCT="$(uv run python - "$DETECTED_COUNT" "$TOTAL_COUNT" <<'PY'
import sys

detected = int(sys.argv[1])
total = int(sys.argv[2])
print(round((detected * 100 / total) if total else 0, 1))
PY
)"

cat > "${RESULTS_DIR}/test-5-results.json" <<JSONEOF
{
    "test_id": "test-5-gate-stress",
    "test_version": "v2.20-baseline",
    "timestamp": "${TIMESTAMP}",
    "findings_targeted": ["F-001", "_cross_refs_resolve", "_has_actionable_content", "_convergence_score_valid"],
    "source_dir": "${SOURCE_DIR}",
    "baseline": {
        "validate_exit": ${BASELINE_EXIT},
        "blocking": ${BASELINE_BLOCKING},
        "warnings": ${BASELINE_WARNINGS},
        "info": ${BASELINE_INFO}
    },
    "corruption_results": ${RESULTS_JSON},
    "summary": {
        "total_corruptions": ${TOTAL_COUNT},
        "detected": ${DETECTED_COUNT},
        "missed": ${MISSED_COUNT},
        "detection_rate_pct": ${DETECTION_RATE_PCT}
    },
    "expected_baseline": {
        "cross-ref": "MISSED (never fails today)",
        "actionability": "MISSED (accepts any bullet)",
        "convergence": "MISSED (only checks range)",
        "heading-gap": "CAUGHT (enforced in merge gate)",
        "duplicate-heading": "CAUGHT (enforced in merge gate)",
        "empty-frontmatter": "DEPENDS (STRICT tier only)",
        "semantic-nonsense": "MISSED (no content validation)"
    },
    "interpretation": {
        "baseline_expectation": "~2-3 out of 7 detected (heading-gap, duplicate-heading, maybe empty-frontmatter)",
        "target": "7 out of 7 detected after v2.20 gate hardening"
    }
}
JSONEOF

echo "=================================================================="
echo "TEST 5 RESULTS — Gate False-Negative Stress Test"
echo "=================================================================="
echo ""
printf "%-20s %8s %10s %10s %10s %10s\n" "CORRUPTION" "EXIT" "BLOCKING" "WARNINGS" "INFO" "DETECTED"
printf "%-20s %8s %10s %10s %10s %10s\n" "==================" "======" "========" "========" "====" "========"

for r in "${RESULTS[@]}"; do
    IFS='|' read -r name validation_exit blocking warnings info detected <<< "$r"
    printf "%-20s %8s %10s %10s %10s %10s\n" "$name" "$validation_exit" "$blocking" "$warnings" "$info" "$detected"
done

echo ""
echo "SUMMARY: ${DETECTED_COUNT} / ${TOTAL_COUNT} corruptions detected"
echo "Baseline report counts: blocking=${BASELINE_BLOCKING}, warnings=${BASELINE_WARNINGS}, info=${BASELINE_INFO}"
echo ""
echo "INTERPRETATION:"
echo "  Pre-v2.20 baseline expects ~2-3 detections (structural checks only)."
echo "  Post-v2.20 target is ${TOTAL_COUNT}/${TOTAL_COUNT} after semantic gate hardening."
echo "  Any corruption marked 'MISSED' with expected 'CAUGHT' indicates a regression."
echo "  Any corruption marked 'CAUGHT' with expected 'MISSED' means validation logic or"
echo "  the validator itself surfaced the issue despite known gate weakness."
echo ""
echo "Results saved to: ${RESULTS_DIR}/test-5-results.json"
echo "=================================================================="