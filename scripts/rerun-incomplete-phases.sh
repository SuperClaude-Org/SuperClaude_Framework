#!/usr/bin/env bash
# rerun-incomplete-phases.sh — Safely re-run incomplete sprint phases one at a time.
#
# Context: Sprint v2.11-roadmap-v4 hit max_turns (100) on all 4 phases,
# leaving 8 tasks incomplete. This script:
#   1. Backs up existing results and artifacts
#   2. Re-runs each phase individually with higher turn limit
#   3. Validates tests pass after each phase
#   4. Stops on first failure
#
# NOTE: The sprint runner has no task-level resume. Each phase re-run
# starts from task 1, redoing completed tasks before reaching incomplete
# ones. Completed artifacts WILL be overwritten (backup preserves originals).
# execution-log.md is overwritten per phase (snapshots saved to backup dir).
#
# Usage:
#   ./scripts/rerun-incomplete-phases.sh [--dry-run] [--max-turns N]
#
# Defaults: --max-turns 200

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASKLIST_DIR="$REPO_ROOT/.dev/releases/complete/v.2.11-roadmap-v4/tasklist"
INDEX_FILE="$TASKLIST_DIR/tasklist-index.md"
RESULTS_DIR="$TASKLIST_DIR/results"
ARTIFACTS_DIR="$TASKLIST_DIR/artifacts"
BACKUP_SUFFIX="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$TASKLIST_DIR/.backup-$BACKUP_SUFFIX"

MAX_TURNS=200
DRY_RUN=false
PHASES=(1 2 3 4)

# ── Argument parsing ─────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --max-turns)
            MAX_TURNS="$2"
            shift 2
            ;;
        --phases)
            IFS=',' read -ra PHASES <<< "$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [--max-turns N] [--phases 1,2,3,4]"
            echo ""
            echo "Options:"
            echo "  --dry-run        Show what would happen without executing"
            echo "  --max-turns N    Turns per phase (default: 200)"
            echo "  --phases 1,2,4   Comma-separated phases to re-run (default: 1,2,3,4)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# ── Preflight checks ────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════"
echo "  Sprint Re-run: v2.11-roadmap-v4 (incomplete phases)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Index:      $INDEX_FILE"
echo "  Max turns:  $MAX_TURNS per phase"
echo "  Phases:     ${PHASES[*]}"
echo "  Backup:     $BACKUP_DIR"
echo "  Dry run:    $DRY_RUN"
echo ""

if [[ ! -f "$INDEX_FILE" ]]; then
    echo "ERROR: Index file not found: $INDEX_FILE" >&2
    exit 1
fi

if ! command -v superclaude &>/dev/null; then
    echo "ERROR: 'superclaude' not found in PATH." >&2
    echo "  Run: make dev  (or: pipx install -e .)" >&2
    exit 1
fi

if ! command -v claude &>/dev/null; then
    echo "ERROR: 'claude' CLI not found in PATH." >&2
    exit 1
fi

# ── Run baseline tests ───────────────────────────────────────────────
echo "── Step 0: Baseline test validation ──────────────────────────"
echo "Running: uv run pytest tests/pipeline/ -q"
BASELINE_OUTPUT=$(uv run pytest tests/pipeline/ -q 2>&1) || {
    echo "$BASELINE_OUTPUT"
    echo ""
    echo "ERROR: Baseline tests failing. Fix before re-running sprint." >&2
    exit 1
}
echo "$BASELINE_OUTPUT" | tail -1
echo ""

# ── Create backup ────────────────────────────────────────────────────
echo "── Step 1: Backing up existing results and artifacts ─────────"

if $DRY_RUN; then
    echo "[DRY RUN] Would create: $BACKUP_DIR"
    echo "[DRY RUN] Would copy: results/, artifacts/, execution-log.*"
else
    mkdir -p "$BACKUP_DIR"

    # Back up results (phase output files)
    if [[ -d "$RESULTS_DIR" ]]; then
        cp -a "$RESULTS_DIR" "$BACKUP_DIR/results"
        echo "  Backed up: results/"
    fi

    # Back up artifacts (deliverable specs + evidence)
    if [[ -d "$ARTIFACTS_DIR" ]]; then
        cp -a "$ARTIFACTS_DIR" "$BACKUP_DIR/artifacts"
        echo "  Backed up: artifacts/"
    fi

    # Back up execution logs
    for logfile in "$TASKLIST_DIR"/execution-log.*; do
        if [[ -f "$logfile" ]]; then
            cp -a "$logfile" "$BACKUP_DIR/"
            echo "  Backed up: $(basename "$logfile")"
        fi
    done

    # Back up checkpoints
    if [[ -d "$TASKLIST_DIR/checkpoints" ]]; then
        cp -a "$TASKLIST_DIR/checkpoints" "$BACKUP_DIR/checkpoints"
        echo "  Backed up: checkpoints/"
    fi

    echo "  Backup complete: $BACKUP_DIR"
fi
echo ""

# ── Phase-by-phase re-run ───────────────────────────────────────────
FAILED_PHASE=0

for phase in "${PHASES[@]}"; do
    echo "══════════════════════════════════════════════════════════════"
    echo "  Phase $phase / ${#PHASES[@]}"
    echo "══════════════════════════════════════════════════════════════"

    if $DRY_RUN; then
        echo "[DRY RUN] Would run:"
        echo "  superclaude sprint run $INDEX_FILE \\"
        echo "    --start $phase --end $phase \\"
        echo "    --max-turns $MAX_TURNS --no-tmux"
        echo ""
        echo "[DRY RUN] Would then run: uv run pytest tests/pipeline/ -q"
        echo ""
        continue
    fi

    # Run single phase
    echo "Running phase $phase with $MAX_TURNS turns..."
    echo "Command: superclaude sprint run $INDEX_FILE --start $phase --end $phase --max-turns $MAX_TURNS --no-tmux"
    echo ""

    phase_start=$(date +%s)

    # Preserve per-phase execution log (write_header overwrites execution-log.md)
    if superclaude sprint run "$INDEX_FILE" \
        --start "$phase" --end "$phase" \
        --max-turns "$MAX_TURNS" \
        --no-tmux; then
        phase_end=$(date +%s)
        phase_dur=$((phase_end - phase_start))
        echo ""
        echo "  Phase $phase completed in ${phase_dur}s (exit 0)"
    else
        phase_exit=$?
        phase_end=$(date +%s)
        phase_dur=$((phase_end - phase_start))
        echo ""
        echo "WARNING: Phase $phase exited with code $phase_exit after ${phase_dur}s"

        # Sprint runner exits 1 on HALT (phase failure).
        # It exits 0 on max_turns (treated as pass_no_report).
        if [[ $phase_exit -eq 1 ]]; then
            echo "ERROR: Phase $phase HALTED. Stopping re-run." >&2
            FAILED_PHASE=$phase
            break
        fi
    fi

    # Save per-phase execution log snapshot (next phase overwrites execution-log.md)
    if [[ -f "$TASKLIST_DIR/execution-log.md" ]]; then
        cp "$TASKLIST_DIR/execution-log.md" "$BACKUP_DIR/execution-log-rerun-phase${phase}.md"
    fi

    # Post-phase test validation
    echo ""
    echo "── Post-phase $phase: Test validation ────────────────────────"
    POST_OUTPUT=$(uv run pytest tests/pipeline/ -q 2>&1) || {
        echo "$POST_OUTPUT"
        echo ""
        echo "ERROR: Tests failing after phase $phase!" >&2
        echo "  Backup available at: $BACKUP_DIR" >&2
        echo "  To restore artifacts:"
        echo "    cp -a $BACKUP_DIR/artifacts/* $ARTIFACTS_DIR/"
        FAILED_PHASE=$phase
        break
    }
    echo "  Post-phase $phase: $(echo "$POST_OUTPUT" | tail -1)"

    echo ""
done

# ── Summary ──────────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════"
echo "  Summary"
echo "═══════════════════════════════════════════════════════════════"

if $DRY_RUN; then
    echo "  Dry run complete. No changes made."
elif [[ $FAILED_PHASE -ne 0 ]]; then
    echo "  INCOMPLETE: Failed at phase $FAILED_PHASE"
    echo "  Backup: $BACKUP_DIR"
    echo ""
    echo "  To restore from backup:"
    echo "    cp -a $BACKUP_DIR/results/* $RESULTS_DIR/"
    echo "    cp -a $BACKUP_DIR/artifacts/* $ARTIFACTS_DIR/"
    exit 1
else
    echo "  All ${#PHASES[@]} phases re-run successfully."
    echo "  Backup preserved at: $BACKUP_DIR"
    echo ""

    # Final artifact check — report which deliverables are still missing
    echo "── Deliverable artifact check ────────────────────────────────"
    missing=0
    empty=0
    for d in $(seq 1 48); do
        did=$(printf "D-%04d" "$d")
        dir="$ARTIFACTS_DIR/$did"
        if [[ ! -d "$dir" ]]; then
            echo "  MISSING: $did (directory not created)"
            missing=$((missing + 1))
        elif [[ -z "$(ls -A "$dir" 2>/dev/null)" ]]; then
            echo "  EMPTY:   $did (directory exists but no files)"
            empty=$((empty + 1))
        fi
    done

    if [[ $missing -eq 0 && $empty -eq 0 ]]; then
        echo "  All 48 deliverables have artifacts."
    else
        echo ""
        echo "  Missing: $missing, Empty: $empty (of 48 total)"
    fi
fi

echo ""
echo "Done."
