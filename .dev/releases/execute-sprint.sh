#!/usr/bin/env bash
# execute-sprint.sh — Sequential phase executor with fresh context per phase
#
# Reads a tasklist-index.md, discovers phase files (flexible naming),
# validates they exist, then executes each phase in a fresh Claude Code
# session using /sc:task-unified --compliance strict --strategy systematic.
#
# Usage:
#   ./execute-sprint.sh <tasklist-index-path> [options]
#
# Options:
#   --start N        Start from phase N (default: 1)
#   --end N          End at phase N (default: last discovered)
#   --max-turns N    Max agent turns per phase (default: 100)
#   --model MODEL    Claude model to use (default: from env or opus)
#   --dry-run        Show discovered phases without executing
#   --allow-hierarchical-permissions
#                    Use --allow-hierarchical-permissions instead of
#                    --dangerously-skip-permissions
#   --help           Show this help message
#
# Examples:
#   ./execute-sprint.sh .dev/releases/current/v2.02-Roadmap-v3/tasklist-index.md
#   ./execute-sprint.sh path/to/tasklist-index.md --start 3 --end 6
#   ./execute-sprint.sh path/to/tasklist-index.md --dry-run
#   ./execute-sprint.sh path/to/tasklist-index.md --model sonnet --max-turns 30

set -euo pipefail

# ── Color output helpers ────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

log_info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_phase() { echo -e "\n${BOLD}═══ $* ═══${NC}\n"; }

# ── Defaults ────────────────────────────────────────────────────────
START_PHASE=1
END_PHASE=0  # 0 = auto-detect from discovered phases
MAX_TURNS=100
MODEL="${CLAUDE_MODEL:-}"
DRY_RUN=false
PERM_FLAG="--dangerously-skip-permissions"
INDEX_PATH=""

# ── Argument parsing ────────────────────────────────────────────────
show_help() {
    sed -n '2,/^$/{ s/^# //; s/^#$//; p }' "$0"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --start)       START_PHASE="$2"; shift 2 ;;
        --end)         END_PHASE="$2"; shift 2 ;;
        --max-turns)   MAX_TURNS="$2"; shift 2 ;;
        --model)       MODEL="$2"; shift 2 ;;
        --dry-run)     DRY_RUN=true; shift ;;
        --allow-hierarchical-permissions)
                       PERM_FLAG="--allow-hierarchical-permissions"; shift ;;
        --help|-h)     show_help ;;
        -*)            log_error "Unknown option: $1"; show_help ;;
        *)
            if [[ -z "$INDEX_PATH" ]]; then
                INDEX_PATH="$1"
            else
                log_error "Unexpected argument: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$INDEX_PATH" ]]; then
    log_error "Missing required argument: <tasklist-index-path>"
    echo "Usage: $0 <tasklist-index-path> [options]"
    exit 1
fi

# ── Resolve paths ───────────────────────────────────────────────────
if [[ ! -f "$INDEX_PATH" ]]; then
    log_error "Index file not found: $INDEX_PATH"
    exit 1
fi

INDEX_DIR="$(cd "$(dirname "$INDEX_PATH")" && pwd)"
INDEX_FILE="$(basename "$INDEX_PATH")"
RELEASE_DIR="$INDEX_DIR"

log_info "Index file: ${INDEX_DIR}/${INDEX_FILE}"
log_info "Release dir: ${RELEASE_DIR}"

# ── Phase file discovery ────────────────────────────────────────────
# Flexible matching: phase-1-tasklist.md, p1-tasklist.md, phase1-tasklist.md,
# Phase_1_tasklist.md, etc. Extracts phase number from filename.
discover_phases() {
    local -a found_phases=()
    local -a found_files=()

    # Strategy 1: Grep the index file for phase file references
    # Look for lines referencing phase files (common patterns in tasklist indexes)
    local index_refs
    index_refs=$(grep -oiE '(phase|p)[-_]?[0-9]+[-_]tasklist[^[:space:]|)]*\.md' \
        "${INDEX_DIR}/${INDEX_FILE}" 2>/dev/null || true)

    if [[ -n "$index_refs" ]]; then
        while IFS= read -r ref; do
            # Extract phase number from the reference
            local num
            num=$(echo "$ref" | grep -oE '[0-9]+' | head -1)
            local full_path="${INDEX_DIR}/${ref}"
            if [[ -n "$num" && -f "$full_path" ]]; then
                found_phases+=("$num")
                found_files+=("$full_path")
            fi
        done <<< "$index_refs"
    fi

    # Strategy 2: If index grep found nothing, scan the directory
    if [[ ${#found_phases[@]} -eq 0 ]]; then
        log_warn "No phase files referenced in index. Scanning directory..."
        for f in "${INDEX_DIR}"/*tasklist*.md; do
            [[ -f "$f" ]] || continue
            # Skip the index file itself
            [[ "$(basename "$f")" == "$INDEX_FILE" ]] && continue
            local num
            num=$(basename "$f" | grep -oE '[0-9]+' | head -1)
            if [[ -n "$num" ]]; then
                found_phases+=("$num")
                found_files+=("$f")
            fi
        done
    fi

    # Deduplicate and sort by phase number
    local -A phase_map
    for i in "${!found_phases[@]}"; do
        local pnum="${found_phases[$i]}"
        # If duplicate phase number, keep the first match
        if [[ -z "${phase_map[$pnum]:-}" ]]; then
            phase_map["$pnum"]="${found_files[$i]}"
        fi
    done

    # Output sorted by phase number
    for pnum in $(echo "${!phase_map[@]}" | tr ' ' '\n' | sort -n); do
        echo "${pnum}|${phase_map[$pnum]}"
    done
}

# Run discovery
mapfile -t PHASE_ENTRIES < <(discover_phases)

if [[ ${#PHASE_ENTRIES[@]} -eq 0 ]]; then
    log_error "No phase tasklist files discovered from index or directory."
    log_error "Expected filenames like: phase-1-tasklist.md, p1-tasklist.md, phase1-tasklist.md"
    exit 1
fi

# Parse into parallel arrays
declare -a PHASE_NUMS=()
declare -a PHASE_FILES=()
for entry in "${PHASE_ENTRIES[@]}"; do
    PHASE_NUMS+=("${entry%%|*}")
    PHASE_FILES+=("${entry#*|}")
done

LAST_PHASE="${PHASE_NUMS[-1]}"
if [[ "$END_PHASE" -eq 0 ]]; then
    END_PHASE="$LAST_PHASE"
fi

# ── Display discovered phases ───────────────────────────────────────
log_phase "Phase Discovery"
log_info "Discovered ${#PHASE_NUMS[@]} phase file(s):"
for i in "${!PHASE_NUMS[@]}"; do
    local_status=""
    pn="${PHASE_NUMS[$i]}"
    pf="${PHASE_FILES[$i]}"
    if [[ "$pn" -lt "$START_PHASE" || "$pn" -gt "$END_PHASE" ]]; then
        local_status=" ${YELLOW}(skip — outside range ${START_PHASE}-${END_PHASE})${NC}"
    fi
    echo -e "  Phase ${BOLD}${pn}${NC}: $(basename "$pf")${local_status}"
done

# ── Validate all target phase files exist ───────────────────────────
log_info "Validating phase files in range ${START_PHASE}–${END_PHASE}..."
MISSING=0
for i in "${!PHASE_NUMS[@]}"; do
    pn="${PHASE_NUMS[$i]}"
    pf="${PHASE_FILES[$i]}"
    [[ "$pn" -lt "$START_PHASE" || "$pn" -gt "$END_PHASE" ]] && continue
    if [[ ! -f "$pf" ]]; then
        log_error "Phase ${pn} file missing: $pf"
        MISSING=$((MISSING + 1))
    fi
done

if [[ "$MISSING" -gt 0 ]]; then
    log_error "${MISSING} phase file(s) missing. Cannot proceed."
    exit 1
fi
log_ok "All phase files in range validated."

# ── Check for sequential gaps ───────────────────────────────────────
PREV=0
for i in "${!PHASE_NUMS[@]}"; do
    pn="${PHASE_NUMS[$i]}"
    [[ "$pn" -lt "$START_PHASE" || "$pn" -gt "$END_PHASE" ]] && continue
    if [[ "$PREV" -gt 0 && "$pn" -ne $((PREV + 1)) ]]; then
        log_warn "Gap in phase sequence: Phase ${PREV} → Phase ${pn} (Phase $((PREV + 1)) missing)"
    fi
    PREV="$pn"
done

# ── Dry run exit ────────────────────────────────────────────────────
if [[ "$DRY_RUN" == true ]]; then
    log_phase "Dry Run Complete"
    log_info "Would execute phases ${START_PHASE}–${END_PHASE} with:"
    log_info "  Max turns: ${MAX_TURNS}"
    log_info "  Model: ${MODEL:-<default>}"
    log_info "  Permissions: ${PERM_FLAG}"
    log_info "  Command: /sc:task-unified --compliance strict --strategy systematic"
    exit 0
fi

# ── Build common claude flags ───────────────────────────────────────
COMMON_FLAGS=(
    --print
    "$PERM_FLAG"
    --no-session-persistence
    --max-turns "$MAX_TURNS"
    --output-format text
)

if [[ -n "$MODEL" ]]; then
    COMMON_FLAGS+=(--model "$MODEL")
fi

# ── Execution log setup ────────────────────────────────────────────
EXEC_LOG="${RELEASE_DIR}/execution-log.md"
RESULTS_DIR="${RELEASE_DIR}/results"
mkdir -p "$RESULTS_DIR"

cat > "$EXEC_LOG" <<HEADER
# Sprint Execution Log

**Started**: $(date -Iseconds)
**Index**: ${INDEX_DIR}/${INDEX_FILE}
**Phases**: ${START_PHASE}–${END_PHASE}
**Max turns**: ${MAX_TURNS}
**Model**: ${MODEL:-default}
**Permissions**: ${PERM_FLAG}

| Phase | Status | Started | Completed | Duration | Exit |
|-------|--------|---------|-----------|----------|------|
HEADER

# ── Phase execution loop ───────────────────────────────────────────
SPRINT_START=$(date +%s)
HALT_PHASE=""

for i in "${!PHASE_NUMS[@]}"; do
    pn="${PHASE_NUMS[$i]}"
    pf="${PHASE_FILES[$i]}"

    [[ "$pn" -lt "$START_PHASE" || "$pn" -gt "$END_PHASE" ]] && continue

    PHASE_BASENAME="$(basename "$pf")"
    OUTPUT_FILE="${RESULTS_DIR}/phase-${pn}-output.txt"
    ERROR_FILE="${RESULTS_DIR}/phase-${pn}-errors.txt"
    RESULT_FILE="${RESULTS_DIR}/phase-${pn}-result.md"

    log_phase "Phase ${pn}: ${PHASE_BASENAME}"

    PHASE_START=$(date +%s)
    PHASE_START_ISO=$(date -Iseconds)

    # Build the prompt — sc:task-unified with strict compliance
    # The @file syntax loads the tasklist as context
    PROMPT="/sc:task-unified Execute all tasks in @${pf} --compliance strict --strategy systematic

## Execution Rules
- Execute tasks in order (T${pn}XX.01, T${pn}XX.02, etc.)
- For STRICT tier tasks: use Sequential MCP for analysis, run quality verification
- For STANDARD tier tasks: run direct test execution per acceptance criteria
- For LIGHT tier tasks: quick sanity check only
- For EXEMPT tier tasks: skip formal verification
- If a STRICT-tier task fails, STOP and report — do not continue to next task
- For all other tier failures, log the failure and continue

## Completion Protocol
When ALL tasks in this phase are complete (or halted on STRICT failure):
1. Write a phase completion report to ${RESULT_FILE} containing:
   - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL), tasks_total, tasks_passed, tasks_failed
   - Per-task status table: Task ID, Title, Tier, Status (pass/fail/skip), Evidence
   - Files modified (list all paths)
   - Blockers for next phase (if any)
   - The literal string EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT
2. If any task produced file changes, list them under ## Files Modified

## Important
- This is Phase ${pn} of a multi-phase sprint
- Previous phases have already been executed in separate sessions
- Do not re-execute work from prior phases
- Focus only on the tasks defined in the phase file"

    # Execute in a fresh Claude Code session
    # CLAUDECODE= prevents nested session detection
    log_info "Launching agent (max ${MAX_TURNS} turns)..."

    set +e  # Don't exit on agent failure
    CLAUDECODE= timeout $((MAX_TURNS * 120 + 300)) claude \
        "${COMMON_FLAGS[@]}" \
        -p "$PROMPT" \
        > "$OUTPUT_FILE" 2>"$ERROR_FILE"
    AGENT_EXIT=$?
    set -e

    PHASE_END=$(date +%s)
    PHASE_DURATION=$(( PHASE_END - PHASE_START ))
    PHASE_DURATION_FMT="$(( PHASE_DURATION / 60 ))m $(( PHASE_DURATION % 60 ))s"

    # Determine phase outcome
    PHASE_STATUS="UNKNOWN"

    if [[ $AGENT_EXIT -eq 124 ]]; then
        PHASE_STATUS="TIMEOUT"
        log_error "Phase ${pn} timed out after ${PHASE_DURATION_FMT}"
    elif [[ $AGENT_EXIT -ne 0 ]]; then
        PHASE_STATUS="ERROR"
        log_error "Phase ${pn} agent exited with code ${AGENT_EXIT}"
    elif [[ -f "$RESULT_FILE" ]]; then
        # Check the result file for CONTINUE/HALT recommendation
        if grep -q "EXIT_RECOMMENDATION: CONTINUE" "$RESULT_FILE" 2>/dev/null; then
            PHASE_STATUS="PASS"
        elif grep -q "EXIT_RECOMMENDATION: HALT" "$RESULT_FILE" 2>/dev/null; then
            PHASE_STATUS="HALT"
        elif grep -qi "status: PASS" "$RESULT_FILE" 2>/dev/null; then
            PHASE_STATUS="PASS"
        elif grep -qi "status: FAIL" "$RESULT_FILE" 2>/dev/null; then
            PHASE_STATUS="HALT"
        else
            PHASE_STATUS="PASS_NO_SIGNAL"
            log_warn "Phase ${pn} completed but no EXIT_RECOMMENDATION found. Assuming PASS."
        fi
    else
        # No result file written — check output for obvious success signals
        if [[ -s "$OUTPUT_FILE" ]]; then
            PHASE_STATUS="PASS_NO_REPORT"
            log_warn "Phase ${pn} produced output but no result file. Assuming PASS."
        else
            PHASE_STATUS="ERROR"
            log_error "Phase ${pn} produced no output and no result file."
        fi
    fi

    # Log to execution log
    echo "| Phase ${pn} | ${PHASE_STATUS} | ${PHASE_START_ISO} | $(date -Iseconds) | ${PHASE_DURATION_FMT} | ${AGENT_EXIT} |" >> "$EXEC_LOG"

    # Report
    case "$PHASE_STATUS" in
        PASS|PASS_NO_SIGNAL|PASS_NO_REPORT)
            log_ok "Phase ${pn}: ${PHASE_STATUS} (${PHASE_DURATION_FMT})"
            ;;
        HALT)
            log_error "Phase ${pn}: HALTED (${PHASE_DURATION_FMT})"
            log_error "A STRICT-tier task failed. Review: ${RESULT_FILE}"
            HALT_PHASE="$pn"
            break
            ;;
        TIMEOUT)
            log_error "Phase ${pn}: TIMEOUT (${PHASE_DURATION_FMT})"
            log_warn "Agent did not complete within time limit."
            HALT_PHASE="$pn"
            break
            ;;
        ERROR|*)
            log_error "Phase ${pn}: ERROR (exit code ${AGENT_EXIT}, ${PHASE_DURATION_FMT})"
            if [[ -s "$ERROR_FILE" ]]; then
                log_error "Stderr (last 5 lines):"
                tail -5 "$ERROR_FILE" | while read -r line; do
                    echo "  $line" >&2
                done
            fi
            HALT_PHASE="$pn"
            break
            ;;
    esac
done

# ── Sprint summary ──────────────────────────────────────────────────
SPRINT_END=$(date +%s)
SPRINT_DURATION=$(( SPRINT_END - SPRINT_START ))
SPRINT_DURATION_FMT="$(( SPRINT_DURATION / 60 ))m $(( SPRINT_DURATION % 60 ))s"

echo "" >> "$EXEC_LOG"

if [[ -n "$HALT_PHASE" ]]; then
    echo "**Halted**: Phase ${HALT_PHASE} — $(date -Iseconds)" >> "$EXEC_LOG"
    echo "**Total duration**: ${SPRINT_DURATION_FMT}" >> "$EXEC_LOG"
    echo "" >> "$EXEC_LOG"
    echo "**Resume command**: \`$0 ${INDEX_PATH} --start $((HALT_PHASE)) --end ${END_PHASE}\`" >> "$EXEC_LOG"

    log_phase "Sprint Halted at Phase ${HALT_PHASE}"
    log_info "Total duration: ${SPRINT_DURATION_FMT}"
    log_info "Review: ${RESULTS_DIR}/phase-${HALT_PHASE}-result.md"
    log_info "Output: ${RESULTS_DIR}/phase-${HALT_PHASE}-output.txt"
    log_info ""
    log_info "Resume after fixing:"
    echo -e "  ${BOLD}$0 ${INDEX_PATH} --start ${HALT_PHASE} --end ${END_PHASE}${NC}"
    exit 1
else
    echo "**Completed**: $(date -Iseconds)" >> "$EXEC_LOG"
    echo "**Total duration**: ${SPRINT_DURATION_FMT}" >> "$EXEC_LOG"

    log_phase "Sprint Complete"
    log_ok "All phases ${START_PHASE}–${END_PHASE} executed successfully."
    log_info "Total duration: ${SPRINT_DURATION_FMT}"
    log_info "Execution log: ${EXEC_LOG}"
    exit 0
fi
